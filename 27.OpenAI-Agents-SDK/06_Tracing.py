"""
OpenAI Agents SDK - Tracing（追蹤調試）範例

展示如何使用 Tracing 進行調試和性能監控
包含：基礎追蹤、性能分析、錯誤追蹤、可視化

這是 Agents SDK 相比 Swarm 的重要新功能！
"""

import os
import time
from openai_agents import Agent, tool, run, trace_run, Session, configure

# ============================================================================
# 1. 基礎 Tracing
# ============================================================================

def test_basic_tracing():
    """測試基礎追蹤功能"""
    print("\n" + "="*60)
    print("範例 1: 基礎 Tracing")
    print("="*60)

    agent = Agent(
        name="助手",
        model="gpt-4",
        instructions="你是助手，使用繁體中文。"
    )

    # 使用 trace_run 包裹執行
    with trace_run(name="簡單對話") as tracer:
        response = run(
            agent=agent,
            messages=[{"role": "user", "content": "你好，請介紹自己"}]
        )

    # 獲取追蹤數據
    print("\n追蹤數據：")
    print(f"  執行時間: {tracer.elapsed_time:.2f} 秒")
    print(f"  Token 使用:")
    print(f"    - Prompt: {tracer.prompt_tokens}")
    print(f"    - Completion: {tracer.completion_tokens}")
    print(f"    - Total: {tracer.total_tokens}")
    print(f"  成本估算: ${tracer.estimated_cost:.4f}")


# ============================================================================
# 2. 追蹤工具調用
# ============================================================================

@tool
def search_database(query: str) -> dict:
    """搜索數據庫（模擬）"""
    time.sleep(0.5)  # 模擬延遲
    return {"results": [f"結果 for {query}"]}


@tool
def process_data(data: str) -> dict:
    """處理數據（模擬）"""
    time.sleep(0.3)
    return {"processed": f"已處理: {data}"}


def test_tool_tracing():
    """測試工具調用追蹤"""
    print("\n" + "="*60)
    print("範例 2: 追蹤工具調用")
    print("="*60)

    agent = Agent(
        name="數據助手",
        model="gpt-4",
        instructions="使用工具處理數據。使用繁體中文。",
        tools=[search_database, process_data]
    )

    with trace_run(name="工具調用測試") as tracer:
        response = run(
            agent=agent,
            messages=[{"role": "user", "content": "搜索並處理 Python 相關數據"}]
        )

    # 分析工具調用
    print("\n工具調用分析：")
    tool_calls = tracer.get_tool_calls()

    for i, tc in enumerate(tool_calls, 1):
        print(f"\n  工具 {i}:")
        print(f"    名稱: {tc['name']}")
        print(f"    參數: {tc['arguments']}")
        print(f"    結果: {tc['result']}")
        print(f"    耗時: {tc['duration']:.3f} 秒")


# ============================================================================
# 3. 性能分析
# ============================================================================

def test_performance_analysis():
    """測試性能分析"""
    print("\n" + "="*60)
    print("範例 3: 性能分析")
    print("="*60)

    agent = Agent(
        name="助手",
        model="gpt-4",
        instructions="你是助手，使用繁體中文。",
        tools=[search_database]
    )

    # 運行多次，收集性能數據
    print("\n運行 3 次對話，收集性能數據：")

    results = []

    for i in range(3):
        with trace_run(name=f"測試 {i+1}") as tracer:
            response = run(
                agent=agent,
                messages=[{"role": "user", "content": f"第 {i+1} 個問題"}]
            )

        results.append({
            "run": i + 1,
            "time": tracer.elapsed_time,
            "tokens": tracer.total_tokens,
            "cost": tracer.estimated_cost
        })

    # 統計分析
    print("\n性能統計：")
    avg_time = sum(r["time"] for r in results) / len(results)
    avg_tokens = sum(r["tokens"] for r in results) / len(results)
    total_cost = sum(r["cost"] for r in results)

    print(f"  平均耗時: {avg_time:.2f} 秒")
    print(f"  平均 Token: {avg_tokens:.0f}")
    print(f"  總成本: ${total_cost:.4f}")

    # 詳細數據
    print("\n詳細數據：")
    for r in results:
        print(f"  第 {r['run']} 次: {r['time']:.2f}s, "
              f"{r['tokens']} tokens, ${r['cost']:.4f}")


# ============================================================================
# 4. 錯誤追蹤
# ============================================================================

@tool
def risky_operation(param: str) -> dict:
    """可能失敗的操作"""
    if "error" in param.lower():
        raise ValueError("模擬錯誤")
    return {"result": "成功"}


def test_error_tracing():
    """測試錯誤追蹤"""
    print("\n" + "="*60)
    print("範例 4: 錯誤追蹤")
    print("="*60)

    agent = Agent(
        name="測試助手",
        model="gpt-4",
        instructions="使用工具。使用繁體中文。",
        tools=[risky_operation]
    )

    # 測試正常情況
    print("\n測試 1: 正常操作")
    try:
        with trace_run(name="正常操作") as tracer:
            response = run(
                agent=agent,
                messages=[{"role": "user", "content": "執行正常操作"}]
            )
        print(f"  ✓ 成功")
        print(f"  執行時間: {tracer.elapsed_time:.2f}s")
    except Exception as e:
        print(f"  ✗ 失敗: {e}")

    # 測試錯誤情況
    print("\n測試 2: 觸發錯誤")
    try:
        with trace_run(name="錯誤操作") as tracer:
            response = run(
                agent=agent,
                messages=[{"role": "user", "content": "執行 error 操作"}]
            )
        print(f"  ✓ 成功")
    except Exception as e:
        print(f"  ✗ 捕獲錯誤: {type(e).__name__}")

        # 獲取錯誤追蹤
        error_trace = tracer.get_error_trace()
        print(f"\n  錯誤追蹤:")
        print(f"    類型: {error_trace['type']}")
        print(f"    消息: {error_trace['message']}")
        print(f"    位置: {error_trace['location']}")


# ============================================================================
# 5. 時間線追蹤
# ============================================================================

def test_timeline_tracing():
    """測試執行時間線"""
    print("\n" + "="*60)
    print("範例 5: 執行時間線")
    print("="*60)

    agent = Agent(
        name="助手",
        model="gpt-4",
        instructions="使用工具。使用繁體中文。",
        tools=[search_database, process_data]
    )

    with trace_run(name="時間線測試") as tracer:
        tracer.log_event("開始執行")

        response = run(
            agent=agent,
            messages=[{"role": "user", "content": "搜索並處理數據"}]
        )

        tracer.log_event("執行完成")

    # 獲取時間線
    print("\n執行時間線：")
    timeline = tracer.get_timeline()

    for event in timeline:
        timestamp = event['timestamp']
        name = event['name']
        duration = event.get('duration', 'N/A')

        print(f"  [{timestamp:.3f}s] {name}")
        if duration != 'N/A':
            print(f"    耗時: {duration:.3f}s")


# ============================================================================
# 6. 自定義指標
# ============================================================================

def test_custom_metrics():
    """測試自定義指標"""
    print("\n" + "="*60)
    print("範例 6: 自定義指標")
    print("="*60)

    agent = Agent(
        name="助手",
        model="gpt-4",
        instructions="你是助手，使用繁體中文。"
    )

    with trace_run(name="自定義指標") as tracer:
        # 添加自定義元數據
        tracer.add_metadata({
            "user_id": "U12345",
            "session_id": "S67890",
            "environment": "production"
        })

        # 記錄自定義指標
        tracer.log_metric("user_satisfaction", 4.5)
        tracer.log_metric("response_relevance", 0.92)

        response = run(
            agent=agent,
            messages=[{"role": "user", "content": "你好"}]
        )

        # 更多指標
        tracer.log_metric("message_length", len(response.messages[-1]['content']))

    # 獲取所有指標
    print("\n自定義指標：")
    metrics = tracer.get_metrics()

    for key, value in metrics.items():
        print(f"  {key}: {value}")


# ============================================================================
# 7. Session 與 Tracing 整合
# ============================================================================

def test_session_tracing():
    """測試 Session 與 Tracing 整合"""
    print("\n" + "="*60)
    print("範例 7: Session + Tracing")
    print("="*60)

    agent = Agent(
        name="助手",
        model="gpt-4",
        instructions="你是助手，記住對話歷史。使用繁體中文。"
    )

    session = Session(
        agent=agent,
        session_id="trace_test"
    )

    # 追蹤整個 Session 的多輪對話
    with trace_run(name="多輪對話") as tracer:
        tracer.log_event("Session 開始")

        for i in range(3):
            tracer.log_event(f"第 {i+1} 輪開始")
            response = session.run(f"第 {i+1} 個問題")
            tracer.log_event(f"第 {i+1} 輪結束")

        tracer.log_event("Session 結束")

    # 分析結果
    print("\n追蹤結果：")
    print(f"  總耗時: {tracer.elapsed_time:.2f}s")
    print(f"  總 Token: {tracer.total_tokens}")
    print(f"  總成本: ${tracer.estimated_cost:.4f}")

    print(f"\n  平均每輪:")
    print(f"    耗時: {tracer.elapsed_time / 3:.2f}s")
    print(f"    Token: {tracer.total_tokens // 3}")


# ============================================================================
# 8. 追蹤數據導出
# ============================================================================

def test_trace_export():
    """測試追蹤數據導出"""
    print("\n" + "="*60)
    print("範例 8: 追蹤數據導出")
    print("="*60)

    agent = Agent(
        name="助手",
        model="gpt-4",
        instructions="你是助手，使用繁體中文。",
        tools=[search_database]
    )

    with trace_run(name="導出測試") as tracer:
        tracer.add_metadata({"test": "export"})

        response = run(
            agent=agent,
            messages=[{"role": "user", "content": "搜索數據"}]
        )

    # 導出為 JSON
    print("\n導出格式：")

    trace_data = tracer.to_dict()
    print(f"  1. JSON 格式: {len(str(trace_data))} 字符")

    # 導出摘要
    summary = tracer.get_summary()
    print(f"\n  2. 摘要:")
    for key, value in summary.items():
        print(f"     {key}: {value}")

    # 可以保存到文件
    import json
    trace_file = "/tmp/trace_export.json"
    with open(trace_file, 'w', encoding='utf-8') as f:
        json.dump(trace_data, f, indent=2, ensure_ascii=False)

    print(f"\n  ✓ 追蹤數據已保存到: {trace_file}")


# ============================================================================
# 9. 最佳實踐
# ============================================================================

def demonstrate_best_practices():
    """展示 Tracing 最佳實踐"""
    print("\n" + "="*60)
    print("範例 9: Tracing 最佳實踐")
    print("="*60)

    print("""
最佳實踐：

1. 何時使用 Tracing
   ✓ 開發階段：調試和優化
   ✓ 生產環境：性能監控
   ✓ 問題排查：錯誤追蹤
   ✓ 成本分析：Token 使用統計

2. 命名規範
   ✓ 使用有意義的 trace 名稱
   ✓ 包含業務上下文
   ✓ 便於後續分析

   好: trace_run(name="訂單處理_用戶12345")
   差: trace_run(name="test")

3. 元數據管理
   ✓ 記錄關鍵業務信息
   ✓ 用戶 ID、會話 ID
   ✓ 環境標記（dev/prod）
   ✓ 功能標記

4. 性能考慮
   - Tracing 有輕微性能開銷
   - 生產環境考慮採樣（不是每次都追蹤）
   - 定期清理歷史追蹤數據

5. 與監控系統整合
   ✓ 導出到 Prometheus
   ✓ 發送到 ELK Stack
   ✓ 整合 APM 工具（如 Datadog）

示例代碼：
    """)

    print("""
    class TracingManager:
        def __init__(self, enable_sampling=True, sample_rate=0.1):
            self.enable_sampling = enable_sampling
            self.sample_rate = sample_rate

        def should_trace(self):
            if not self.enable_sampling:
                return True
            import random
            return random.random() < self.sample_rate

        def trace_request(self, name, metadata):
            if not self.should_trace():
                # 不追蹤，直接執行
                return nullcontext()

            return trace_run(
                name=name,
                metadata={
                    **metadata,
                    "sampled": True
                }
            )
    """)


# ============================================================================
# 10. 與 Swarm 對比
# ============================================================================

def swarm_vs_agents_tracing():
    """Tracing 是 Agents SDK 獨有功能"""
    print("\n" + "="*60)
    print("範例 10: Tracing - Agents SDK 獨有功能")
    print("="*60)

    print("\n【Swarm】")
    print("  ✗ 沒有內建 Tracing")
    print("  - 需要手動添加日誌")
    print("  - 無法自動追蹤 Token 使用")
    print("  - 難以分析性能瓶頸")

    print("\n【Agents SDK】")
    print("  ✓ 完整的 Tracing 系統")
    print("  - 自動追蹤執行時間")
    print("  - 自動統計 Token 使用")
    print("  - 追蹤工具調用")
    print("  - 錯誤堆棧追蹤")
    print("  - 支持自定義指標")
    print("  - 可導出分析數據")

    print("\n實際價值：")
    print("  • 性能優化：識別慢查詢")
    print("  • 成本控制：追蹤 Token 使用")
    print("  • 問題排查：完整的執行軌跡")
    print("  • 質量保證：監控 Agent 表現")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """運行所有範例"""
    print("="*60)
    print("OpenAI Agents SDK - Tracing 範例")
    print("="*60)

    # 配置環境
    configure(
        api_key=os.getenv("OPENAI_API_KEY"),
        timeout=60
    )
    print("✓ 環境配置完成")

    # 運行各個範例
    try:
        test_basic_tracing()
        test_tool_tracing()
        test_performance_analysis()
        test_error_tracing()
        test_timeline_tracing()
        test_custom_metrics()
        test_session_tracing()
        test_trace_export()
        demonstrate_best_practices()
        swarm_vs_agents_tracing()
    except Exception as e:
        print(f"\n錯誤: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)
    print("所有範例運行完成！")
    print("="*60)


if __name__ == "__main__":
    main()
