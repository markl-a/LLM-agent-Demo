"""事件系統模組 - 提供事件發布/訂閱功能

這個模組提供了完整的事件系統解決方案，包括：
- 事件發布/訂閱模式 (EventEmitter)
- 事件過濾和優先級
- 同步和異步事件處理
- 內建事件類型
- 事件歷史記錄
- 條件訂閱和一次性訂閱

使用示例：
    >>> from llm_agent_demo.utils.events import EventEmitter, Event, EventType
    >>>
    >>> # 創建事件發射器
    >>> emitter = EventEmitter()
    >>>
    >>> # 訂閱事件
    >>> def on_api_call(event: Event):
    ...     print(f"API 調用: {event.data}")
    >>>
    >>> emitter.on(EventType.API_CALL, on_api_call)
    >>>
    >>> # 發射事件
    >>> emitter.emit(EventType.API_CALL, {"model": "gpt-4", "tokens": 100})
    >>>
    >>> # 異步事件處理
    >>> async def async_handler(event: Event):
    ...     await some_async_operation(event.data)
    >>>
    >>> emitter.on_async(EventType.API_CALL, async_handler)
    >>> await emitter.emit_async(EventType.API_CALL, {"model": "gpt-4"})
"""

import asyncio
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable, Coroutine, Deque, Dict, List, Optional, Set, Union
from uuid import uuid4

from .logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# 事件類型定義
# ============================================================================


class EventType(str, Enum):
    """內建事件類型枚舉"""

    # API 相關事件
    API_CALL = "api_call"
    API_SUCCESS = "api_success"
    API_ERROR = "api_error"
    API_RETRY = "api_retry"

    # 成本追蹤事件
    COST_TRACKED = "cost_tracked"
    COST_LIMIT_WARNING = "cost_limit_warning"
    COST_LIMIT_EXCEEDED = "cost_limit_exceeded"

    # 錯誤事件
    ERROR = "error"
    WARNING = "warning"
    CRITICAL = "critical"

    # Agent 相關事件
    AGENT_START = "agent_start"
    AGENT_STEP = "agent_step"
    AGENT_COMPLETE = "agent_complete"
    AGENT_ERROR = "agent_error"

    # 工具執行事件
    TOOL_START = "tool_start"
    TOOL_COMPLETE = "tool_complete"
    TOOL_ERROR = "tool_error"

    # 數據事件
    DATA_LOADED = "data_loaded"
    DATA_SAVED = "data_saved"
    DATA_ERROR = "data_error"

    # 自定義事件
    CUSTOM = "custom"


class EventPriority(int, Enum):
    """事件優先級"""

    LOWEST = 0
    LOW = 1
    NORMAL = 2
    HIGH = 3
    HIGHEST = 4


# ============================================================================
# 事件數據結構
# ============================================================================


@dataclass
class Event:
    """事件對象"""

    type: Union[EventType, str]
    data: Any = None
    timestamp: datetime = field(default_factory=datetime.now)
    event_id: str = field(default_factory=lambda: str(uuid4()))
    source: Optional[str] = None
    priority: EventPriority = EventPriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "type": str(self.type),
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "event_id": self.event_id,
            "source": self.source,
            "priority": self.priority.value,
            "metadata": self.metadata,
        }

    def __str__(self) -> str:
        return f"Event({self.type}, id={self.event_id[:8]}, priority={self.priority.name})"


@dataclass
class EventListener:
    """事件監聽器"""

    callback: Union[Callable[[Event], None], Callable[[Event], Coroutine]]
    priority: EventPriority = EventPriority.NORMAL
    once: bool = False  # 是否只執行一次
    filter_func: Optional[Callable[[Event], bool]] = None  # 事件過濾函數
    listener_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    is_async: bool = False

    def should_handle(self, event: Event) -> bool:
        """判斷是否應該處理此事件"""
        if self.filter_func:
            return self.filter_func(event)
        return True

    def __str__(self) -> str:
        return f"EventListener(id={self.listener_id[:8]}, priority={self.priority.name}, once={self.once})"


# ============================================================================
# 事件統計
# ============================================================================


@dataclass
class EventStats:
    """事件統計信息"""

    total_emitted: int = 0
    total_handled: int = 0
    total_errors: int = 0
    events_by_type: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    handlers_by_type: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    last_event_time: Optional[datetime] = None
    average_handler_time: float = 0.0
    _handler_times: List[float] = field(default_factory=list, repr=False)

    def record_event(self, event_type: str) -> None:
        """記錄事件發射"""
        self.total_emitted += 1
        self.events_by_type[event_type] += 1
        self.last_event_time = datetime.now()

    def record_handle(self, event_type: str, duration: float) -> None:
        """記錄事件處理"""
        self.total_handled += 1
        self._handler_times.append(duration)
        # 保持最近 1000 次的平均值
        if len(self._handler_times) > 1000:
            self._handler_times.pop(0)
        self.average_handler_time = sum(self._handler_times) / len(self._handler_times)

    def record_error(self) -> None:
        """記錄錯誤"""
        self.total_errors += 1

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "total_emitted": self.total_emitted,
            "total_handled": self.total_handled,
            "total_errors": self.total_errors,
            "events_by_type": dict(self.events_by_type),
            "handlers_by_type": dict(self.handlers_by_type),
            "last_event_time": self.last_event_time.isoformat()
            if self.last_event_time
            else None,
            "average_handler_time": self.average_handler_time,
        }


# ============================================================================
# 事件發射器
# ============================================================================


class EventEmitter:
    """事件發射器 - 實現發布/訂閱模式

    特性：
    - 支持同步和異步事件處理
    - 事件優先級
    - 事件過濾
    - 一次性訂閱
    - 事件歷史記錄
    - 統計信息
    - 線程安全
    """

    def __init__(
        self,
        max_history: int = 100,
        enable_stats: bool = True,
        log_events: bool = False,
    ):
        """初始化事件發射器

        Args:
            max_history: 保存的最大事件歷史數量
            enable_stats: 是否啟用統計功能
            log_events: 是否記錄事件日誌
        """
        self._listeners: Dict[str, List[EventListener]] = defaultdict(list)
        self._history: Deque[Event] = deque(maxlen=max_history)
        self._stats = EventStats() if enable_stats else None
        self._log_events = log_events
        self._lock = threading.RLock()
        self._wildcard_listeners: List[EventListener] = []
        self._enabled = True

        if self._log_events:
            logger.info("事件發射器已初始化", extra={"max_history": max_history})

    # ========================================================================
    # 訂閱方法
    # ========================================================================

    def on(
        self,
        event_type: Union[EventType, str],
        callback: Callable[[Event], None],
        priority: EventPriority = EventPriority.NORMAL,
        filter_func: Optional[Callable[[Event], bool]] = None,
    ) -> str:
        """訂閱事件（同步）

        Args:
            event_type: 事件類型
            callback: 回調函數
            priority: 優先級
            filter_func: 事件過濾函數

        Returns:
            監聽器 ID
        """
        return self._add_listener(
            event_type=str(event_type),
            callback=callback,
            priority=priority,
            filter_func=filter_func,
            is_async=False,
        )

    def on_async(
        self,
        event_type: Union[EventType, str],
        callback: Callable[[Event], Coroutine],
        priority: EventPriority = EventPriority.NORMAL,
        filter_func: Optional[Callable[[Event], bool]] = None,
    ) -> str:
        """訂閱事件（異步）

        Args:
            event_type: 事件類型
            callback: 異步回調函數
            priority: 優先級
            filter_func: 事件過濾函數

        Returns:
            監聽器 ID
        """
        return self._add_listener(
            event_type=str(event_type),
            callback=callback,
            priority=priority,
            filter_func=filter_func,
            is_async=True,
        )

    def once(
        self,
        event_type: Union[EventType, str],
        callback: Callable[[Event], None],
        priority: EventPriority = EventPriority.NORMAL,
        filter_func: Optional[Callable[[Event], bool]] = None,
    ) -> str:
        """訂閱事件（只執行一次）

        Args:
            event_type: 事件類型
            callback: 回調函數
            priority: 優先級
            filter_func: 事件過濾函數

        Returns:
            監聽器 ID
        """
        return self._add_listener(
            event_type=str(event_type),
            callback=callback,
            priority=priority,
            filter_func=filter_func,
            once=True,
            is_async=False,
        )

    def once_async(
        self,
        event_type: Union[EventType, str],
        callback: Callable[[Event], Coroutine],
        priority: EventPriority = EventPriority.NORMAL,
        filter_func: Optional[Callable[[Event], bool]] = None,
    ) -> str:
        """訂閱事件（異步，只執行一次）

        Args:
            event_type: 事件類型
            callback: 異步回調函數
            priority: 優先級
            filter_func: 事件過濾函數

        Returns:
            監聽器 ID
        """
        return self._add_listener(
            event_type=str(event_type),
            callback=callback,
            priority=priority,
            filter_func=filter_func,
            once=True,
            is_async=True,
        )

    def on_any(
        self,
        callback: Callable[[Event], None],
        priority: EventPriority = EventPriority.NORMAL,
        filter_func: Optional[Callable[[Event], bool]] = None,
    ) -> str:
        """訂閱所有事件（通配符訂閱）

        Args:
            callback: 回調函數
            priority: 優先級
            filter_func: 事件過濾函數

        Returns:
            監聽器 ID
        """
        listener = EventListener(
            callback=callback,
            priority=priority,
            filter_func=filter_func,
            is_async=False,
        )

        with self._lock:
            self._wildcard_listeners.append(listener)
            self._wildcard_listeners.sort(key=lambda x: x.priority.value, reverse=True)

        if self._log_events:
            logger.debug(f"添加通配符監聽器: {listener}")

        return listener.listener_id

    def _add_listener(
        self,
        event_type: str,
        callback: Union[Callable[[Event], None], Callable[[Event], Coroutine]],
        priority: EventPriority,
        filter_func: Optional[Callable[[Event], bool]],
        once: bool = False,
        is_async: bool = False,
    ) -> str:
        """添加監聽器（內部方法）"""
        listener = EventListener(
            callback=callback,
            priority=priority,
            once=once,
            filter_func=filter_func,
            is_async=is_async,
        )

        with self._lock:
            self._listeners[event_type].append(listener)
            # 按優先級排序（高優先級在前）
            self._listeners[event_type].sort(
                key=lambda x: x.priority.value, reverse=True
            )

            if self._stats:
                self._stats.handlers_by_type[event_type] += 1

        if self._log_events:
            logger.debug(
                f"添加監聽器: type={event_type}, {listener}, async={is_async}"
            )

        return listener.listener_id

    # ========================================================================
    # 取消訂閱方法
    # ========================================================================

    def off(
        self,
        event_type: Union[EventType, str],
        listener_id: Optional[str] = None,
        callback: Optional[Callable] = None,
    ) -> bool:
        """取消訂閱

        Args:
            event_type: 事件類型
            listener_id: 監聽器 ID（可選）
            callback: 回調函數（可選）

        Returns:
            是否成功取消訂閱
        """
        event_type_str = str(event_type)

        with self._lock:
            if event_type_str not in self._listeners:
                return False

            original_count = len(self._listeners[event_type_str])

            if listener_id:
                # 根據 ID 移除
                self._listeners[event_type_str] = [
                    listener
                    for listener in self._listeners[event_type_str]
                    if listener.listener_id != listener_id
                ]
            elif callback:
                # 根據回調函數移除
                self._listeners[event_type_str] = [
                    listener
                    for listener in self._listeners[event_type_str]
                    if listener.callback != callback
                ]
            else:
                # 移除所有該類型的監聽器
                self._listeners[event_type_str] = []

            removed_count = original_count - len(self._listeners[event_type_str])

            if self._stats and removed_count > 0:
                self._stats.handlers_by_type[event_type_str] -= removed_count

            if self._log_events and removed_count > 0:
                logger.debug(f"移除了 {removed_count} 個監聽器: type={event_type_str}")

            return removed_count > 0

    def off_all(self, event_type: Optional[Union[EventType, str]] = None) -> int:
        """移除所有監聽器

        Args:
            event_type: 事件類型（可選，如果不指定則移除所有類型）

        Returns:
            移除的監聽器數量
        """
        with self._lock:
            if event_type:
                event_type_str = str(event_type)
                count = len(self._listeners.get(event_type_str, []))
                self._listeners[event_type_str] = []
                if self._stats:
                    self._stats.handlers_by_type[event_type_str] = 0
            else:
                count = sum(len(listeners) for listeners in self._listeners.values())
                self._listeners.clear()
                self._wildcard_listeners.clear()
                if self._stats:
                    self._stats.handlers_by_type.clear()

            if self._log_events:
                logger.debug(f"移除了所有監聽器: count={count}")

            return count

    # ========================================================================
    # 發射事件方法
    # ========================================================================

    def emit(
        self,
        event_type: Union[EventType, str],
        data: Any = None,
        source: Optional[str] = None,
        priority: EventPriority = EventPriority.NORMAL,
        **metadata,
    ) -> Event:
        """發射同步事件

        Args:
            event_type: 事件類型
            data: 事件數據
            source: 事件來源
            priority: 事件優先級
            **metadata: 額外的元數據

        Returns:
            Event 對象
        """
        if not self._enabled:
            return Event(type=event_type, data=data, priority=priority)

        event = Event(
            type=event_type,
            data=data,
            source=source,
            priority=priority,
            metadata=metadata,
        )

        with self._lock:
            # 添加到歷史記錄
            self._history.append(event)

            # 記錄統計
            if self._stats:
                self._stats.record_event(str(event_type))

            if self._log_events:
                logger.debug(f"發射事件: {event}")

        # 處理事件
        self._handle_event_sync(event)

        return event

    async def emit_async(
        self,
        event_type: Union[EventType, str],
        data: Any = None,
        source: Optional[str] = None,
        priority: EventPriority = EventPriority.NORMAL,
        **metadata,
    ) -> Event:
        """發射異步事件

        Args:
            event_type: 事件類型
            data: 事件數據
            source: 事件來源
            priority: 事件優先級
            **metadata: 額外的元數據

        Returns:
            Event 對象
        """
        if not self._enabled:
            return Event(type=event_type, data=data, priority=priority)

        event = Event(
            type=event_type,
            data=data,
            source=source,
            priority=priority,
            metadata=metadata,
        )

        with self._lock:
            # 添加到歷史記錄
            self._history.append(event)

            # 記錄統計
            if self._stats:
                self._stats.record_event(str(event_type))

            if self._log_events:
                logger.debug(f"發射異步事件: {event}")

        # 處理事件
        await self._handle_event_async(event)

        return event

    def _handle_event_sync(self, event: Event) -> None:
        """處理同步事件（內部方法）"""
        event_type_str = str(event.type)
        listeners_to_remove = []

        # 獲取監聽器列表（複製以避免在迭代時修改）
        with self._lock:
            listeners = list(self._listeners.get(event_type_str, []))
            wildcard_listeners = list(self._wildcard_listeners)

        # 合併並按優先級排序
        all_listeners = listeners + wildcard_listeners
        all_listeners.sort(key=lambda x: x.priority.value, reverse=True)

        # 執行回調
        for listener in all_listeners:
            if not listener.should_handle(event):
                continue

            try:
                start_time = time.time()

                if listener.is_async:
                    # 異步回調需要在事件循環中執行
                    logger.warning(
                        f"同步事件中有異步監聽器，將被跳過: {listener}"
                    )
                    continue

                listener.callback(event)

                duration = time.time() - start_time

                if self._stats:
                    self._stats.record_handle(event_type_str, duration)

                # 如果是一次性監聽器，標記為移除
                if listener.once:
                    listeners_to_remove.append((event_type_str, listener.listener_id))

            except Exception as e:
                if self._stats:
                    self._stats.record_error()
                logger.error(f"事件處理器錯誤: {e}", exc_info=True)

        # 移除一次性監聽器
        for event_type_str, listener_id in listeners_to_remove:
            self.off(event_type_str, listener_id=listener_id)

    async def _handle_event_async(self, event: Event) -> None:
        """處理異步事件（內部方法）"""
        event_type_str = str(event.type)
        listeners_to_remove = []

        # 獲取監聽器列表（複製以避免在迭代時修改）
        with self._lock:
            listeners = list(self._listeners.get(event_type_str, []))
            wildcard_listeners = list(self._wildcard_listeners)

        # 合併並按優先級排序
        all_listeners = listeners + wildcard_listeners
        all_listeners.sort(key=lambda x: x.priority.value, reverse=True)

        # 收集所有任務
        tasks = []
        for listener in all_listeners:
            if not listener.should_handle(event):
                continue

            async def handle_listener(lst: EventListener):
                try:
                    start_time = time.time()

                    if lst.is_async:
                        await lst.callback(event)
                    else:
                        # 在執行器中運行同步回調
                        await asyncio.get_event_loop().run_in_executor(
                            None, lst.callback, event
                        )

                    duration = time.time() - start_time

                    if self._stats:
                        self._stats.record_handle(event_type_str, duration)

                    # 如果是一次性監聽器，標記為移除
                    if lst.once:
                        listeners_to_remove.append((event_type_str, lst.listener_id))

                except Exception as e:
                    if self._stats:
                        self._stats.record_error()
                    logger.error(f"異步事件處理器錯誤: {e}", exc_info=True)

            tasks.append(handle_listener(listener))

        # 並發執行所有處理器
        if tasks:
            await asyncio.gather(*tasks)

        # 移除一次性監聽器
        for event_type_str, listener_id in listeners_to_remove:
            self.off(event_type_str, listener_id=listener_id)

    # ========================================================================
    # 工具方法
    # ========================================================================

    def enable(self) -> None:
        """啟用事件發射器"""
        self._enabled = True
        if self._log_events:
            logger.info("事件發射器已啟用")

    def disable(self) -> None:
        """禁用事件發射器"""
        self._enabled = False
        if self._log_events:
            logger.info("事件發射器已禁用")

    def is_enabled(self) -> bool:
        """檢查是否啟用"""
        return self._enabled

    def listener_count(
        self, event_type: Optional[Union[EventType, str]] = None
    ) -> int:
        """獲取監聽器數量

        Args:
            event_type: 事件類型（可選）

        Returns:
            監聽器數量
        """
        with self._lock:
            if event_type:
                return len(self._listeners.get(str(event_type), []))
            else:
                return sum(len(listeners) for listeners in self._listeners.values())

    def event_types(self) -> Set[str]:
        """獲取所有已訂閱的事件類型"""
        with self._lock:
            return set(self._listeners.keys())

    def get_history(
        self,
        event_type: Optional[Union[EventType, str]] = None,
        limit: Optional[int] = None,
    ) -> List[Event]:
        """獲取事件歷史

        Args:
            event_type: 事件類型（可選）
            limit: 限制數量（可選）

        Returns:
            事件列表
        """
        with self._lock:
            events = list(self._history)

        if event_type:
            events = [e for e in events if str(e.type) == str(event_type)]

        if limit:
            events = events[-limit:]

        return events

    def clear_history(self) -> None:
        """清空事件歷史"""
        with self._lock:
            self._history.clear()

        if self._log_events:
            logger.debug("事件歷史已清空")

    def get_stats(self) -> Optional[EventStats]:
        """獲取統計信息"""
        return self._stats

    def reset_stats(self) -> None:
        """重置統計信息"""
        if self._stats:
            self._stats = EventStats()
            if self._log_events:
                logger.debug("統計信息已重置")

    def wait_for(
        self,
        event_type: Union[EventType, str],
        timeout: Optional[float] = None,
        filter_func: Optional[Callable[[Event], bool]] = None,
    ) -> Optional[Event]:
        """等待特定事件（同步，使用線程事件）

        Args:
            event_type: 事件類型
            timeout: 超時時間（秒）
            filter_func: 事件過濾函數

        Returns:
            Event 對象或 None（超時）
        """
        result = {"event": None}
        event_flag = threading.Event()

        def handler(event: Event):
            result["event"] = event
            event_flag.set()

        listener_id = self.once(
            event_type=event_type,
            callback=handler,
            priority=EventPriority.HIGHEST,
            filter_func=filter_func,
        )

        # 等待事件
        event_flag.wait(timeout)

        # 如果超時，移除監聽器
        if not event_flag.is_set():
            self.off(event_type, listener_id=listener_id)

        return result["event"]

    async def wait_for_async(
        self,
        event_type: Union[EventType, str],
        timeout: Optional[float] = None,
        filter_func: Optional[Callable[[Event], bool]] = None,
    ) -> Optional[Event]:
        """等待特定事件（異步）

        Args:
            event_type: 事件類型
            timeout: 超時時間（秒）
            filter_func: 事件過濾函數

        Returns:
            Event 對象或 None（超時）
        """
        future = asyncio.Future()

        async def handler(event: Event):
            if not future.done():
                future.set_result(event)

        listener_id = self.once_async(
            event_type=event_type,
            callback=handler,
            priority=EventPriority.HIGHEST,
            filter_func=filter_func,
        )

        try:
            if timeout:
                result = await asyncio.wait_for(future, timeout=timeout)
            else:
                result = await future
            return result
        except asyncio.TimeoutError:
            self.off(event_type, listener_id=listener_id)
            return None


# ============================================================================
# 全局事件發射器實例
# ============================================================================

# 默認的全局事件發射器
_global_emitter: Optional[EventEmitter] = None
_global_emitter_lock = threading.Lock()


def get_global_emitter() -> EventEmitter:
    """獲取全局事件發射器實例（單例模式）"""
    global _global_emitter

    if _global_emitter is None:
        with _global_emitter_lock:
            if _global_emitter is None:
                _global_emitter = EventEmitter(
                    max_history=1000, enable_stats=True, log_events=False
                )
                logger.info("全局事件發射器已創建")

    return _global_emitter


def set_global_emitter(emitter: EventEmitter) -> None:
    """設置全局事件發射器

    Args:
        emitter: EventEmitter 實例
    """
    global _global_emitter
    with _global_emitter_lock:
        _global_emitter = emitter
        logger.info("全局事件發射器已更新")


# ============================================================================
# 裝飾器
# ============================================================================


def event_handler(
    event_type: Union[EventType, str],
    emitter: Optional[EventEmitter] = None,
    priority: EventPriority = EventPriority.NORMAL,
) -> Callable:
    """事件處理器裝飾器

    使用示例：
        >>> @event_handler(EventType.API_CALL)
        ... def handle_api_call(event: Event):
        ...     print(f"API 調用: {event.data}")
    """

    def decorator(func: Callable) -> Callable:
        target_emitter = emitter or get_global_emitter()

        if asyncio.iscoroutinefunction(func):
            target_emitter.on_async(event_type, func, priority=priority)
        else:
            target_emitter.on(event_type, func, priority=priority)

        return func

    return decorator


def emit_event(
    event_type: Union[EventType, str],
    emitter: Optional[EventEmitter] = None,
    data_key: str = "result",
    include_args: bool = False,
) -> Callable:
    """自動發射事件的裝飾器

    使用示例：
        >>> @emit_event(EventType.API_CALL)
        ... def api_call(model: str, prompt: str):
        ...     return {"response": "..."}
        ...
        ... # 調用函數時會自動發射事件
    """

    def decorator(func: Callable) -> Callable:
        target_emitter = emitter or get_global_emitter()

        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    result = await func(*args, **kwargs)
                    event_data = {data_key: result}
                    if include_args:
                        event_data["args"] = args
                        event_data["kwargs"] = kwargs
                    await target_emitter.emit_async(
                        event_type, data=event_data, source=func.__name__
                    )
                    return result
                except Exception as e:
                    await target_emitter.emit_async(
                        EventType.ERROR,
                        data={"error": str(e), "function": func.__name__},
                        source=func.__name__,
                    )
                    raise

            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    result = func(*args, **kwargs)
                    event_data = {data_key: result}
                    if include_args:
                        event_data["args"] = args
                        event_data["kwargs"] = kwargs
                    target_emitter.emit(
                        event_type, data=event_data, source=func.__name__
                    )
                    return result
                except Exception as e:
                    target_emitter.emit(
                        EventType.ERROR,
                        data={"error": str(e), "function": func.__name__},
                        source=func.__name__,
                    )
                    raise

            return sync_wrapper

    return decorator


# ============================================================================
# 便捷函數
# ============================================================================


def emit(
    event_type: Union[EventType, str],
    data: Any = None,
    **kwargs,
) -> Event:
    """使用全局發射器發射事件（同步）"""
    return get_global_emitter().emit(event_type, data, **kwargs)


async def emit_async(
    event_type: Union[EventType, str],
    data: Any = None,
    **kwargs,
) -> Event:
    """使用全局發射器發射事件（異步）"""
    return await get_global_emitter().emit_async(event_type, data, **kwargs)


def on(
    event_type: Union[EventType, str],
    callback: Callable[[Event], None],
    **kwargs,
) -> str:
    """使用全局發射器訂閱事件（同步）"""
    return get_global_emitter().on(event_type, callback, **kwargs)


def on_async(
    event_type: Union[EventType, str],
    callback: Callable[[Event], Coroutine],
    **kwargs,
) -> str:
    """使用全局發射器訂閱事件（異步）"""
    return get_global_emitter().on_async(event_type, callback, **kwargs)


def off(
    event_type: Union[EventType, str],
    **kwargs,
) -> bool:
    """使用全局發射器取消訂閱"""
    return get_global_emitter().off(event_type, **kwargs)


__all__ = [
    # 核心類
    "EventEmitter",
    "Event",
    "EventListener",
    "EventStats",
    # 枚舉
    "EventType",
    "EventPriority",
    # 全局實例
    "get_global_emitter",
    "set_global_emitter",
    # 裝飾器
    "event_handler",
    "emit_event",
    # 便捷函數
    "emit",
    "emit_async",
    "on",
    "on_async",
    "off",
]
