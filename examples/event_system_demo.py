"""事件系統演示範例

展示如何使用事件系統的各種功能：
- 基本事件發布/訂閱
- 事件優先級
- 事件過濾
- 同步和異步處理
- 裝飾器使用
- 一次性訂閱
- 全局事件發射器
"""

import asyncio
import time
from llm_agent_demo.utils.events import (
    EventEmitter,
    EventType,
    EventPriority,
    Event,
    event_handler,
    emit_event,
    get_global_emitter,
)


# ============================================================================
# 1. 基本事件發布/訂閱
# ============================================================================


def demo_basic_events():
    """演示基本事件發布/訂閱"""
    print("\n=== 1. 基本事件發布/訂閱 ===")

    emitter = EventEmitter(log_events=True)

    # 訂閱 API 調用事件
    def on_api_call(event: Event):
        print(f"  處理 API 調用: {event.data}")

    emitter.on(EventType.API_CALL, on_api_call)

    # 發射事件
    emitter.emit(EventType.API_CALL, {"model": "gpt-4", "tokens": 100})
    emitter.emit(EventType.API_CALL, {"model": "claude-3", "tokens": 200})

    print(f"  監聽器數量: {emitter.listener_count(EventType.API_CALL)}")


# ============================================================================
# 2. 事件優先級
# ============================================================================


def demo_event_priority():
    """演示事件優先級"""
    print("\n=== 2. 事件優先級 ===")

    emitter = EventEmitter()

    # 添加不同優先級的監聽器
    emitter.on(
        EventType.ERROR,
        lambda e: print(f"  [NORMAL] 錯誤: {e.data}"),
        priority=EventPriority.NORMAL,
    )
    emitter.on(
        EventType.ERROR,
        lambda e: print(f"  [HIGHEST] 緊急處理: {e.data}"),
        priority=EventPriority.HIGHEST,
    )
    emitter.on(
        EventType.ERROR,
        lambda e: print(f"  [LOW] 日誌記錄: {e.data}"),
        priority=EventPriority.LOW,
    )

    # 發射錯誤事件（應該按優先級順序處理）
    emitter.emit(EventType.ERROR, {"message": "資料庫連接失敗"})


# ============================================================================
# 3. 事件過濾
# ============================================================================


def demo_event_filtering():
    """演示事件過濾"""
    print("\n=== 3. 事件過濾 ===")

    emitter = EventEmitter()

    # 只處理成本超過 $1 的事件
    def cost_filter(event: Event) -> bool:
        return event.data.get("cost", 0) > 1.0

    emitter.on(
        EventType.COST_TRACKED,
        lambda e: print(f"  高成本警告: ${e.data['cost']:.2f}"),
        filter_func=cost_filter,
    )

    # 發射多個成本追蹤事件
    emitter.emit(EventType.COST_TRACKED, {"cost": 0.5, "model": "gpt-3.5"})
    emitter.emit(EventType.COST_TRACKED, {"cost": 1.5, "model": "gpt-4"})
    emitter.emit(EventType.COST_TRACKED, {"cost": 0.8, "model": "gpt-3.5"})
    emitter.emit(EventType.COST_TRACKED, {"cost": 2.3, "model": "claude-opus"})


# ============================================================================
# 4. 異步事件處理
# ============================================================================


async def demo_async_events():
    """演示異步事件處理"""
    print("\n=== 4. 異步事件處理 ===")

    emitter = EventEmitter()

    # 異步事件處理器
    async def async_api_handler(event: Event):
        print(f"  開始異步處理: {event.data['model']}")
        await asyncio.sleep(0.5)  # 模擬異步操作
        print(f"  完成異步處理: {event.data['model']}")

    # 同步事件處理器
    def sync_logger(event: Event):
        print(f"  同步日誌: {event.data['model']}")

    # 訂閱異步和同步處理器
    emitter.on_async(EventType.API_SUCCESS, async_api_handler)
    emitter.on(EventType.API_SUCCESS, sync_logger)

    # 發射異步事件
    await emitter.emit_async(EventType.API_SUCCESS, {"model": "gpt-4"})
    await emitter.emit_async(EventType.API_SUCCESS, {"model": "claude-3"})


# ============================================================================
# 5. 一次性訂閱
# ============================================================================


def demo_once_subscription():
    """演示一次性訂閱"""
    print("\n=== 5. 一次性訂閱 ===")

    emitter = EventEmitter()

    # 一次性訂閱
    emitter.once(
        EventType.AGENT_START, lambda e: print(f"  Agent 首次啟動: {e.data}")
    )

    # 普通訂閱
    emitter.on(
        EventType.AGENT_START, lambda e: print(f"  Agent 啟動記錄: {e.data}")
    )

    # 發射多次事件
    emitter.emit(EventType.AGENT_START, {"name": "研究助手"})
    emitter.emit(EventType.AGENT_START, {"name": "代碼助手"})
    emitter.emit(EventType.AGENT_START, {"name": "寫作助手"})


# ============================================================================
# 6. 使用裝飾器
# ============================================================================


def demo_decorators():
    """演示裝飾器使用"""
    print("\n=== 6. 使用裝飾器 ===")

    emitter = EventEmitter()

    # 使用事件處理器裝飾器
    @event_handler(EventType.TOOL_START, emitter=emitter)
    def handle_tool_start(event: Event):
        print(f"  工具開始執行: {event.data}")

    # 使用自動發射事件裝飾器
    @emit_event(EventType.TOOL_COMPLETE, emitter=emitter, include_args=True)
    def execute_tool(tool_name: str, params: dict):
        print(f"  執行工具: {tool_name}")
        return {"status": "success", "result": f"已執行 {tool_name}"}

    # 觸發事件
    emitter.emit(EventType.TOOL_START, {"tool": "搜索引擎", "query": "Python"})
    result = execute_tool("搜索引擎", {"query": "Python"})


# ============================================================================
# 7. 全局事件發射器
# ============================================================================


def demo_global_emitter():
    """演示全局事件發射器"""
    print("\n=== 7. 全局事件發射器 ===")

    # 獲取全局發射器
    emitter = get_global_emitter()

    # 使用全局裝飾器
    @event_handler(EventType.CUSTOM)
    def global_handler(event: Event):
        print(f"  全局處理器: {event.data}")

    # 從任何地方發射事件
    from llm_agent_demo.utils.events import emit

    emit(EventType.CUSTOM, {"message": "這是全局事件"})


# ============================================================================
# 8. 事件歷史和統計
# ============================================================================


def demo_history_and_stats():
    """演示事件歷史和統計"""
    print("\n=== 8. 事件歷史和統計 ===")

    emitter = EventEmitter(max_history=50, enable_stats=True)

    # 添加監聽器
    emitter.on(EventType.API_CALL, lambda e: None)
    emitter.on(EventType.API_SUCCESS, lambda e: None)
    emitter.on(EventType.API_ERROR, lambda e: time.sleep(0.01))  # 模擬處理時間

    # 發射多個事件
    for i in range(10):
        emitter.emit(EventType.API_CALL, {"request_id": i})
        emitter.emit(EventType.API_SUCCESS, {"request_id": i})

    emitter.emit(EventType.API_ERROR, {"error": "超時"})

    # 顯示統計信息
    stats = emitter.get_stats()
    if stats:
        print(f"  總發射事件: {stats.total_emitted}")
        print(f"  總處理事件: {stats.total_handled}")
        print(f"  總錯誤: {stats.total_errors}")
        print(f"  平均處理時間: {stats.average_handler_time*1000:.2f}ms")

    # 顯示歷史記錄
    history = emitter.get_history(limit=5)
    print(f"\n  最近 5 個事件:")
    for event in history:
        print(f"    - {event.type}: {event.data}")


# ============================================================================
# 9. 等待事件
# ============================================================================


async def demo_wait_for_event():
    """演示等待特定事件"""
    print("\n=== 9. 等待事件 ===")

    emitter = EventEmitter()

    # 異步等待任務
    async def wait_task():
        print("  等待 Agent 完成...")
        event = await emitter.wait_for_async(EventType.AGENT_COMPLETE, timeout=2.0)
        if event:
            print(f"  Agent 已完成: {event.data}")
        else:
            print("  等待超時")

    # 模擬 Agent 執行
    async def agent_task():
        await asyncio.sleep(1.0)
        await emitter.emit_async(EventType.AGENT_COMPLETE, {"result": "任務完成"})

    # 並發執行
    await asyncio.gather(wait_task(), agent_task())


# ============================================================================
# 10. 通配符訂閱
# ============================================================================


def demo_wildcard_subscription():
    """演示通配符訂閱（訂閱所有事件）"""
    print("\n=== 10. 通配符訂閱 ===")

    emitter = EventEmitter()

    # 訂閱所有事件
    emitter.on_any(lambda e: print(f"  [ALL] {e.type}: {e.data}"))

    # 發射不同類型的事件
    emitter.emit(EventType.API_CALL, {"model": "gpt-4"})
    emitter.emit(EventType.COST_TRACKED, {"cost": 0.5})
    emitter.emit(EventType.AGENT_START, {"name": "助手"})


# ============================================================================
# 主函數
# ============================================================================


def main():
    """運行所有演示"""
    print("=" * 70)
    print("事件系統演示")
    print("=" * 70)

    # 同步演示
    demo_basic_events()
    demo_event_priority()
    demo_event_filtering()
    demo_once_subscription()
    demo_decorators()
    demo_global_emitter()
    demo_history_and_stats()
    demo_wildcard_subscription()

    # 異步演示
    print("\n" + "=" * 70)
    print("異步演示")
    print("=" * 70)
    asyncio.run(demo_async_events())
    asyncio.run(demo_wait_for_event())

    print("\n" + "=" * 70)
    print("演示完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
