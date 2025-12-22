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

注意：此模組已重構為多個子模組，但保持完全向後兼容。
"""

# 從新模塊重新導出所有內容以保持向後兼容性
from .event_emitter import (
    EventEmitter,
    emit,
    emit_async,
    emit_event,
    event_handler,
    get_global_emitter,
    off,
    on,
    on_async,
    set_global_emitter,
)
from .event_model import Event, EventListener
from .event_stats import EventStats
from .event_types import EventPriority, EventType

# 導入 event_emitter 模塊以訪問私有變量（用於測試）
from . import event_emitter as _event_emitter_module


# 提供對私有變量的訪問（向後兼容，用於測試）
def __getattr__(name):
    """動態屬性訪問，用於訪問內部變量"""
    if name == "_global_emitter":
        return _event_emitter_module._global_emitter
    elif name == "_global_emitter_lock":
        return _event_emitter_module._global_emitter_lock
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

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
