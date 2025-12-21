"""事件系統模組的單元測試"""

import asyncio
import pytest
import time
from unittest.mock import MagicMock, patch
from datetime import datetime

# 檢查是否安裝了核心模組
try:
    from src.llm_agent_demo.utils.events import (
        EventEmitter,
        EventType,
        EventPriority,
        Event,
        EventListener,
        EventStats,
        get_global_emitter,
        set_global_emitter,
        event_handler,
        emit_event,
        emit,
        emit_async,
        on,
        on_async,
        off,
    )

    CORE_MODULE_AVAILABLE = True
except ImportError:
    CORE_MODULE_AVAILABLE = False
    pytest.skip("核心模組未安裝", allow_module_level=True)


@pytest.fixture
def event_emitter():
    """創建事件發射器的 fixture"""
    return EventEmitter(max_history=10, enable_stats=True, log_events=False)


@pytest.fixture
def sample_event():
    """創建測試事件的 fixture"""
    return Event(
        type=EventType.API_CALL,
        data={"model": "gpt-4", "tokens": 100},
        source="test",
        priority=EventPriority.NORMAL,
    )


@pytest.fixture
def clean_global_emitter():
    """清理全局事件發射器的 fixture"""
    import src.llm_agent_demo.utils.events as events_module

    # 保存原始的全局發射器
    original_emitter = events_module._global_emitter

    # 重置全局發射器
    events_module._global_emitter = None

    yield

    # 測試後恢復
    events_module._global_emitter = original_emitter


# ============================================================================
# EventType 測試
# ============================================================================


@pytest.mark.unit
class TestEventType:
    """測試 EventType 枚舉"""

    def test_event_type_values(self):
        """測試事件類型的值"""
        assert EventType.API_CALL == "api_call"
        assert EventType.API_SUCCESS == "api_success"
        assert EventType.API_ERROR == "api_error"
        assert EventType.COST_TRACKED == "cost_tracked"

    def test_event_type_string_comparison(self):
        """測試事件類型與字串的比較"""
        assert str(EventType.API_CALL) == "api_call"
        assert EventType.ERROR.value == "error"


# ============================================================================
# EventPriority 測試
# ============================================================================


@pytest.mark.unit
class TestEventPriority:
    """測試 EventPriority 枚舉"""

    def test_priority_values(self):
        """測試優先級的值"""
        assert EventPriority.LOWEST.value == 0
        assert EventPriority.LOW.value == 1
        assert EventPriority.NORMAL.value == 2
        assert EventPriority.HIGH.value == 3
        assert EventPriority.HIGHEST.value == 4

    def test_priority_ordering(self):
        """測試優先級排序"""
        assert EventPriority.LOWEST < EventPriority.NORMAL
        assert EventPriority.HIGH > EventPriority.LOW
        assert EventPriority.HIGHEST > EventPriority.LOWEST


# ============================================================================
# Event 測試
# ============================================================================


@pytest.mark.unit
class TestEvent:
    """測試 Event 數據類"""

    def test_event_creation(self, sample_event):
        """測試事件創建"""
        assert sample_event.type == EventType.API_CALL
        assert sample_event.data == {"model": "gpt-4", "tokens": 100}
        assert sample_event.source == "test"
        assert sample_event.priority == EventPriority.NORMAL

    def test_event_default_values(self):
        """測試事件的默認值"""
        event = Event(type=EventType.ERROR)
        assert event.data is None
        assert event.source is None
        assert event.priority == EventPriority.NORMAL
        assert isinstance(event.timestamp, datetime)
        assert isinstance(event.event_id, str)
        assert isinstance(event.metadata, dict)

    def test_event_to_dict(self, sample_event):
        """測試事件轉換為字典"""
        event_dict = sample_event.to_dict()

        assert event_dict["type"] == "api_call"
        assert event_dict["data"] == {"model": "gpt-4", "tokens": 100}
        assert event_dict["source"] == "test"
        assert event_dict["priority"] == 2
        assert "timestamp" in event_dict
        assert "event_id" in event_dict

    def test_event_str_representation(self, sample_event):
        """測試事件的字串表示"""
        event_str = str(sample_event)
        assert "Event" in event_str
        assert "api_call" in event_str
        assert "NORMAL" in event_str

    def test_event_with_metadata(self):
        """測試帶有元數據的事件"""
        event = Event(
            type=EventType.API_CALL,
            data={"test": "data"},
            metadata={"user_id": "123", "session_id": "abc"},
        )
        assert event.metadata["user_id"] == "123"
        assert event.metadata["session_id"] == "abc"


# ============================================================================
# EventListener 測試
# ============================================================================


@pytest.mark.unit
class TestEventListener:
    """測試 EventListener 數據類"""

    def test_listener_creation(self):
        """測試監聽器創建"""

        def callback(event):
            pass

        listener = EventListener(
            callback=callback, priority=EventPriority.HIGH, once=True
        )

        assert listener.callback == callback
        assert listener.priority == EventPriority.HIGH
        assert listener.once is True
        assert isinstance(listener.listener_id, str)

    def test_listener_should_handle_without_filter(self, sample_event):
        """測試沒有過濾器時的處理判斷"""

        def callback(event):
            pass

        listener = EventListener(callback=callback)
        assert listener.should_handle(sample_event) is True

    def test_listener_should_handle_with_filter(self, sample_event):
        """測試帶過濾器的處理判斷"""

        def callback(event):
            pass

        def filter_func(event):
            return event.data.get("tokens", 0) > 50

        listener = EventListener(callback=callback, filter_func=filter_func)
        assert listener.should_handle(sample_event) is True

        # 測試過濾失敗的情況
        event = Event(type=EventType.API_CALL, data={"tokens": 10})
        assert listener.should_handle(event) is False

    def test_listener_str_representation(self):
        """測試監聽器的字串表示"""

        def callback(event):
            pass

        listener = EventListener(callback=callback, priority=EventPriority.HIGH)
        listener_str = str(listener)

        assert "EventListener" in listener_str
        assert "HIGH" in listener_str


# ============================================================================
# EventStats 測試
# ============================================================================


@pytest.mark.unit
class TestEventStats:
    """測試 EventStats 數據類"""

    def test_stats_initialization(self):
        """測試統計信息初始化"""
        stats = EventStats()
        assert stats.total_emitted == 0
        assert stats.total_handled == 0
        assert stats.total_errors == 0
        assert stats.last_event_time is None

    def test_record_event(self):
        """測試記錄事件"""
        stats = EventStats()
        stats.record_event("api_call")

        assert stats.total_emitted == 1
        assert stats.events_by_type["api_call"] == 1
        assert stats.last_event_time is not None

    def test_record_handle(self):
        """測試記錄處理"""
        stats = EventStats()
        stats.record_handle("api_call", 0.5)

        assert stats.total_handled == 1
        assert stats.average_handler_time == 0.5

    def test_record_handle_average(self):
        """測試處理時間平均值計算"""
        stats = EventStats()
        stats.record_handle("api_call", 0.5)
        stats.record_handle("api_call", 1.5)

        assert stats.total_handled == 2
        assert stats.average_handler_time == 1.0

    def test_record_error(self):
        """測試記錄錯誤"""
        stats = EventStats()
        stats.record_error()
        stats.record_error()

        assert stats.total_errors == 2

    def test_stats_to_dict(self):
        """測試統計信息轉換為字典"""
        stats = EventStats()
        stats.record_event("api_call")
        stats.record_handle("api_call", 0.5)

        stats_dict = stats.to_dict()

        assert stats_dict["total_emitted"] == 1
        assert stats_dict["total_handled"] == 1
        assert stats_dict["events_by_type"]["api_call"] == 1


# ============================================================================
# EventEmitter 測試
# ============================================================================


@pytest.mark.unit
class TestEventEmitter:
    """測試 EventEmitter 類"""

    def test_emitter_initialization(self):
        """測試發射器初始化"""
        emitter = EventEmitter(max_history=50, enable_stats=True, log_events=False)
        assert emitter is not None
        assert emitter.is_enabled()

    def test_subscribe_and_emit(self, event_emitter):
        """測試訂閱和發射事件"""
        received_events = []

        def handler(event):
            received_events.append(event)

        event_emitter.on(EventType.API_CALL, handler)
        event_emitter.emit(EventType.API_CALL, {"model": "gpt-4"})

        assert len(received_events) == 1
        assert received_events[0].data["model"] == "gpt-4"

    def test_multiple_listeners(self, event_emitter):
        """測試多個監聽器"""
        received_1 = []
        received_2 = []

        def handler1(event):
            received_1.append(event)

        def handler2(event):
            received_2.append(event)

        event_emitter.on(EventType.API_CALL, handler1)
        event_emitter.on(EventType.API_CALL, handler2)
        event_emitter.emit(EventType.API_CALL, {"test": "data"})

        assert len(received_1) == 1
        assert len(received_2) == 1

    def test_priority_ordering(self, event_emitter):
        """測試優先級排序"""
        call_order = []

        def low_priority(event):
            call_order.append("low")

        def high_priority(event):
            call_order.append("high")

        event_emitter.on(EventType.API_CALL, low_priority, priority=EventPriority.LOW)
        event_emitter.on(EventType.API_CALL, high_priority, priority=EventPriority.HIGH)
        event_emitter.emit(EventType.API_CALL)

        # 高優先級應該先執行
        assert call_order == ["high", "low"]

    def test_once_listener(self, event_emitter):
        """測試一次性監聽器"""
        received_events = []

        def handler(event):
            received_events.append(event)

        event_emitter.once(EventType.API_CALL, handler)
        event_emitter.emit(EventType.API_CALL)
        event_emitter.emit(EventType.API_CALL)

        # 只應該收到一次事件
        assert len(received_events) == 1

    def test_filter_function(self, event_emitter):
        """測試過濾函數"""
        received_events = []

        def handler(event):
            received_events.append(event)

        def filter_high_tokens(event):
            return event.data.get("tokens", 0) > 50

        event_emitter.on(EventType.API_CALL, handler, filter_func=filter_high_tokens)

        event_emitter.emit(EventType.API_CALL, {"tokens": 100})
        event_emitter.emit(EventType.API_CALL, {"tokens": 10})

        # 只有高於 50 tokens 的事件被處理
        assert len(received_events) == 1
        assert received_events[0].data["tokens"] == 100

    def test_unsubscribe_by_listener_id(self, event_emitter):
        """測試通過監聽器 ID 取消訂閱"""
        received_events = []

        def handler(event):
            received_events.append(event)

        listener_id = event_emitter.on(EventType.API_CALL, handler)
        event_emitter.emit(EventType.API_CALL)
        event_emitter.off(EventType.API_CALL, listener_id=listener_id)
        event_emitter.emit(EventType.API_CALL)

        # 取消訂閱後不再收到事件
        assert len(received_events) == 1

    def test_unsubscribe_by_callback(self, event_emitter):
        """測試通過回調函數取消訂閱"""
        received_events = []

        def handler(event):
            received_events.append(event)

        event_emitter.on(EventType.API_CALL, handler)
        event_emitter.emit(EventType.API_CALL)
        event_emitter.off(EventType.API_CALL, callback=handler)
        event_emitter.emit(EventType.API_CALL)

        assert len(received_events) == 1

    def test_off_all(self, event_emitter):
        """測試移除所有監聽器"""

        def handler(event):
            pass

        event_emitter.on(EventType.API_CALL, handler)
        event_emitter.on(EventType.API_SUCCESS, handler)

        count = event_emitter.off_all()
        assert count == 2
        assert event_emitter.listener_count() == 0

    def test_listener_count(self, event_emitter):
        """測試監聽器計數"""

        def handler(event):
            pass

        event_emitter.on(EventType.API_CALL, handler)
        event_emitter.on(EventType.API_CALL, handler)
        event_emitter.on(EventType.API_SUCCESS, handler)

        assert event_emitter.listener_count() == 3
        assert event_emitter.listener_count(EventType.API_CALL) == 2

    def test_event_types(self, event_emitter):
        """測試獲取事件類型"""

        def handler(event):
            pass

        event_emitter.on(EventType.API_CALL, handler)
        event_emitter.on(EventType.API_SUCCESS, handler)

        event_types = event_emitter.event_types()
        assert "api_call" in event_types
        assert "api_success" in event_types

    def test_event_history(self, event_emitter):
        """測試事件歷史記錄"""
        event_emitter.emit(EventType.API_CALL, {"model": "gpt-4"})
        event_emitter.emit(EventType.API_SUCCESS, {"status": "ok"})

        history = event_emitter.get_history()
        assert len(history) == 2

    def test_event_history_filter_by_type(self, event_emitter):
        """測試按類型過濾歷史"""
        event_emitter.emit(EventType.API_CALL, {"model": "gpt-4"})
        event_emitter.emit(EventType.API_SUCCESS, {"status": "ok"})

        history = event_emitter.get_history(event_type=EventType.API_CALL)
        assert len(history) == 1
        assert history[0].type == EventType.API_CALL

    def test_clear_history(self, event_emitter):
        """測試清空歷史記錄"""
        event_emitter.emit(EventType.API_CALL)
        event_emitter.clear_history()

        history = event_emitter.get_history()
        assert len(history) == 0

    def test_enable_disable(self, event_emitter):
        """測試啟用/禁用發射器"""
        received_events = []

        def handler(event):
            received_events.append(event)

        event_emitter.on(EventType.API_CALL, handler)
        event_emitter.disable()
        event_emitter.emit(EventType.API_CALL)

        # 禁用時不應收到事件
        assert len(received_events) == 0

        event_emitter.enable()
        event_emitter.emit(EventType.API_CALL)

        # 重新啟用後收到事件
        assert len(received_events) == 1

    def test_statistics(self, event_emitter):
        """測試統計信息"""

        def handler(event):
            pass

        event_emitter.on(EventType.API_CALL, handler)
        event_emitter.emit(EventType.API_CALL)
        event_emitter.emit(EventType.API_SUCCESS)

        stats = event_emitter.get_stats()
        assert stats.total_emitted == 2
        assert stats.total_handled == 1

    def test_reset_stats(self, event_emitter):
        """測試重置統計信息"""
        event_emitter.emit(EventType.API_CALL)
        event_emitter.reset_stats()

        stats = event_emitter.get_stats()
        assert stats.total_emitted == 0

    def test_wildcard_listener(self, event_emitter):
        """測試通配符監聽器"""
        received_events = []

        def handler(event):
            received_events.append(event)

        event_emitter.on_any(handler)
        event_emitter.emit(EventType.API_CALL)
        event_emitter.emit(EventType.API_SUCCESS)

        # 應該收到所有類型的事件
        assert len(received_events) == 2

    def test_error_handling_in_listener(self, event_emitter):
        """測試監聽器中的錯誤處理"""

        def failing_handler(event):
            raise ValueError("Test error")

        def working_handler(event):
            pass

        event_emitter.on(EventType.API_CALL, failing_handler)
        event_emitter.on(EventType.API_CALL, working_handler)

        # 即使一個處理器失敗，其他的也應該執行
        event_emitter.emit(EventType.API_CALL)

        stats = event_emitter.get_stats()
        assert stats.total_errors == 1


# ============================================================================
# 異步測試
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
class TestEventEmitterAsync:
    """測試 EventEmitter 的異步功能"""

    async def test_async_emit(self, event_emitter):
        """測試異步發射事件"""
        received_events = []

        async def async_handler(event):
            received_events.append(event)

        event_emitter.on_async(EventType.API_CALL, async_handler)
        await event_emitter.emit_async(EventType.API_CALL, {"model": "gpt-4"})

        assert len(received_events) == 1

    async def test_async_once(self, event_emitter):
        """測試異步一次性監聽器"""
        received_events = []

        async def async_handler(event):
            received_events.append(event)

        event_emitter.once_async(EventType.API_CALL, async_handler)
        await event_emitter.emit_async(EventType.API_CALL)
        await event_emitter.emit_async(EventType.API_CALL)

        assert len(received_events) == 1

    async def test_wait_for_async(self, event_emitter):
        """測試異步等待事件"""

        async def emit_later():
            await asyncio.sleep(0.1)
            await event_emitter.emit_async(EventType.API_CALL, {"test": "data"})

        asyncio.create_task(emit_later())
        event = await event_emitter.wait_for_async(EventType.API_CALL, timeout=1.0)

        assert event is not None
        assert event.data["test"] == "data"

    async def test_wait_for_async_timeout(self, event_emitter):
        """測試異步等待超時"""
        event = await event_emitter.wait_for_async(EventType.API_CALL, timeout=0.1)
        assert event is None


# ============================================================================
# 全局發射器測試
# ============================================================================


@pytest.mark.unit
class TestGlobalEmitter:
    """測試全局事件發射器"""

    def test_get_global_emitter(self, clean_global_emitter):
        """測試獲取全局發射器"""
        emitter = get_global_emitter()
        assert emitter is not None
        assert isinstance(emitter, EventEmitter)

    def test_global_emitter_singleton(self, clean_global_emitter):
        """測試全局發射器是單例"""
        emitter1 = get_global_emitter()
        emitter2 = get_global_emitter()
        assert emitter1 is emitter2

    def test_set_global_emitter(self, clean_global_emitter):
        """測試設置全局發射器"""
        new_emitter = EventEmitter()
        set_global_emitter(new_emitter)

        emitter = get_global_emitter()
        assert emitter is new_emitter

    def test_convenience_functions(self, clean_global_emitter):
        """測試便捷函數"""
        received_events = []

        def handler(event):
            received_events.append(event)

        # 使用便捷函數訂閱和發射
        on(EventType.API_CALL, handler)
        emit(EventType.API_CALL, {"test": "data"})

        assert len(received_events) == 1


# ============================================================================
# 裝飾器測試
# ============================================================================


@pytest.mark.unit
class TestDecorators:
    """測試裝飾器"""

    def test_event_handler_decorator(self, clean_global_emitter):
        """測試事件處理器裝飾器"""
        received_events = []

        @event_handler(EventType.API_CALL)
        def handler(event):
            received_events.append(event)

        emit(EventType.API_CALL, {"test": "data"})

        assert len(received_events) == 1

    def test_emit_event_decorator(self, clean_global_emitter):
        """測試自動發射事件裝飾器"""
        received_events = []

        @event_handler(EventType.API_CALL)
        def handler(event):
            received_events.append(event)

        @emit_event(EventType.API_CALL)
        def api_function(model: str):
            return {"response": "success"}

        api_function("gpt-4")

        assert len(received_events) == 1
        assert received_events[0].data["result"]["response"] == "success"


# ============================================================================
# 邊界情況和錯誤處理測試
# ============================================================================


@pytest.mark.unit
class TestEdgeCases:
    """測試邊界情況和錯誤處理"""

    def test_emit_without_listeners(self, event_emitter):
        """測試沒有監聽器時發射事件"""
        # 不應該拋出異常
        event = event_emitter.emit(EventType.API_CALL)
        assert event is not None

    def test_off_nonexistent_listener(self, event_emitter):
        """測試移除不存在的監聽器"""
        result = event_emitter.off(EventType.API_CALL, listener_id="nonexistent")
        assert result is False

    def test_max_history_limit(self):
        """測試歷史記錄上限"""
        emitter = EventEmitter(max_history=5)

        for i in range(10):
            emitter.emit(EventType.API_CALL, {"index": i})

        history = emitter.get_history()
        # 只保留最近的 5 條
        assert len(history) == 5

    def test_event_with_none_data(self, event_emitter):
        """測試數據為 None 的事件"""
        received_events = []

        def handler(event):
            received_events.append(event)

        event_emitter.on(EventType.API_CALL, handler)
        event_emitter.emit(EventType.API_CALL, None)

        assert len(received_events) == 1
        assert received_events[0].data is None

    def test_custom_event_type(self, event_emitter):
        """測試自定義事件類型"""
        received_events = []

        def handler(event):
            received_events.append(event)

        custom_type = "my_custom_event"
        event_emitter.on(custom_type, handler)
        event_emitter.emit(custom_type, {"custom": "data"})

        assert len(received_events) == 1
        assert received_events[0].type == custom_type
