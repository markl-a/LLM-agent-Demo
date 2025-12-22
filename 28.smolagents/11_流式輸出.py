"""
流式輸出 - 實時響應處理
======================

等待完整響應太慢？使用流式輸出！
實時顯示 Agent 的思考和執行過程。

本範例展示：
1. 啟用流式輸出
2. 處理流式響應
3. 實時進度顯示
4. 用戶體驗優化
5. 錯誤處理
"""

from smolagents import CodeAgent, HfApiModel, tool
import time
import sys


# ============================================================================
# 準備測試工具
# ============================================================================

@tool
def slow_computation(n: int) -> int:
    """
    模擬耗時計算

    Args:
        n: 計算參數

    Returns:
        計算結果
    """
    time.sleep(2)  # 模擬耗時操作
    return n * n


@tool
def multi_step_task(steps: int) -> list:
    """
    模擬多步驟任務

    Args:
        steps: 步驟數量

    Returns:
        每步的結果
    """
    results = []
    for i in range(steps):
        time.sleep(1)  # 每步耗時 1 秒
        results.append(f"步驟 {i+1} 完成")
    return results


# ============================================================================
# 範例 1: 為什麼需要流式輸出
# ============================================================================

def example_1_why_streaming():
    """為什麼需要流式輸出"""
    print("\n" + "="*70)
    print("範例 1: 為什麼需要流式輸出")
    print("="*70)

    print("\n非流式輸出的問題：")
    print("  ❌ 用戶需要等待完整響應")
    print("  ❌ 看不到進度")
    print("  ❌ 不知道 Agent 在做什麼")
    print("  ❌ 無法提前中止")
    print("  ❌ 糟糕的用戶體驗")

    print("\n流式輸出的優勢：")
    print("  ✓ 實時反饋")
    print("  ✓ 更好的用戶體驗")
    print("  ✓ 可以看到思考過程")
    print("  ✓ 提前發現問題")
    print("  ✓ 更專業的感覺")

    print("\n適用場景：")
    print("  - 長時間運行的任務")
    print("  - 多步驟推理")
    print("  - 用戶交互界面")
    print("  - 調試和開發")


# ============================================================================
# 範例 2: 基本流式輸出
# ============================================================================

def example_2_basic_streaming():
    """基本的流式輸出"""
    print("\n" + "="*70)
    print("範例 2: 基本流式輸出")
    print("="*70)

    print("\n啟用流式輸出很簡單：\n")

    print("```python")
    print("from smolagents import CodeAgent, HfApiModel")
    print("")
    print("model = HfApiModel()")
    print("agent = CodeAgent(tools=tools, model=model)")
    print("")
    print("# 使用 stream() 方法而不是 run()")
    print("for chunk in agent.stream(task):")
    print("    print(chunk, end='', flush=True)")
    print("```")

    print("\n實際示例（模擬）：")

    model = HfApiModel()
    agent = CodeAgent(
        tools=[slow_computation],
        model=model,
        max_steps=3
    )

    print("\nAgent 正在工作...")
    print("(實際使用中會看到實時輸出)\n")

    # 模擬流式輸出
    simulated_chunks = [
        "思考",
        "中",
        "...\n",
        "調用",
        " slow_computation",
        "...\n",
        "計算",
        "完成",
        "！\n"
    ]

    for chunk in simulated_chunks:
        print(chunk, end='', flush=True)
        time.sleep(0.2)


# ============================================================================
# 範例 3: 詳細的流式輸出
# ============================================================================

def example_3_verbose_streaming():
    """詳細的流式輸出"""
    print("\n" + "="*70)
    print("範例 3: 詳細的流式輸出")
    print("="*70)

    print("\n使用 verbose 參數查看更多細節：\n")

    print("```python")
    print("# verbose=0: 僅最終結果")
    print("agent.stream(task, verbose=0)")
    print("")
    print("# verbose=1: 中等詳細程度（推薦）")
    print("agent.stream(task, verbose=1)")
    print("")
    print("# verbose=2: 最詳細（調試用）")
    print("agent.stream(task, verbose=2)")
    print("```")

    print("\nverbose=1 輸出示例：")
    print("---")
    print("步驟 1: 思考...")
    print("步驟 2: 調用工具 slow_computation(5)")
    print("步驟 3: 工具返回: 25")
    print("步驟 4: 生成最終答案...")
    print("結果: 計算完成，答案是 25")
    print("---")

    print("\nverbose=2 輸出示例：")
    print("---")
    print("[DEBUG] 接收任務: 計算 5 的平方")
    print("[DEBUG] 生成代碼:")
    print("  result = slow_computation(5)")
    print("  print(f'結果: {result}')")
    print("[DEBUG] 執行代碼...")
    print("[DEBUG] 代碼輸出: 結果: 25")
    print("[DEBUG] 任務完成")
    print("---")


# ============================================================================
# 範例 4: 進度條和狀態顯示
# ============================================================================

def example_4_progress_display():
    """進度條和狀態顯示"""
    print("\n" + "="*70)
    print("範例 4: 進度條和狀態顯示")
    print("="*70)

    print("\n結合流式輸出實現進度顯示：\n")

    print("```python")
    print("from tqdm import tqdm")
    print("import sys")
    print("")
    print("# 創建進度條")
    print("pbar = tqdm(total=100, desc='Agent 工作中')")
    print("")
    print("current_progress = 0")
    print("for chunk in agent.stream(task):")
    print("    # 更新進度（根據輸出估算）")
    print("    if '步驟' in chunk:")
    print("        progress = min(current_progress + 20, 100)")
    print("        pbar.update(progress - current_progress)")
    print("        current_progress = progress")
    print("    ")
    print("    # 顯示輸出")
    print("    sys.stdout.write(chunk)")
    print("    sys.stdout.flush()")
    print("")
    print("pbar.close()")
    print("```")

    print("\n實際效果（模擬）：")
    print("")

    # 模擬進度條
    steps = ["初始化", "分析任務", "執行計算", "生成結果", "完成"]
    for i, step in enumerate(steps):
        progress = int((i + 1) / len(steps) * 100)
        bar = "█" * (progress // 5) + "░" * (20 - progress // 5)
        print(f"\r[{bar}] {progress}% - {step}", end='', flush=True)
        time.sleep(0.5)

    print("\n")


# ============================================================================
# 範例 5: 實時日誌記錄
# ============================================================================

def example_5_logging():
    """實時日誌記錄"""
    print("\n" + "="*70)
    print("範例 5: 實時日誌記錄")
    print("="*70)

    print("\n記錄 Agent 的執行過程：\n")

    print("```python")
    print("import logging")
    print("from datetime import datetime")
    print("")
    print("# 配置日誌")
    print("logging.basicConfig(")
    print("    filename='agent.log',")
    print("    level=logging.INFO,")
    print("    format='%(asctime)s - %(message)s'")
    print(")")
    print("")
    print("# 流式執行並記錄")
    print("log_buffer = []")
    print("for chunk in agent.stream(task, verbose=1):")
    print("    # 顯示給用戶")
    print("    print(chunk, end='', flush=True)")
    print("    ")
    print("    # 記錄到日誌")
    print("    log_buffer.append(chunk)")
    print("    if len(log_buffer) > 10 or '\\n' in chunk:")
    print("        logging.info(''.join(log_buffer))")
    print("        log_buffer = []")
    print("```")

    print("\n日誌文件示例：")
    print("---")
    print("2024-01-15 10:30:15 - 開始任務: 分析數據")
    print("2024-01-15 10:30:16 - 步驟 1: 載入數據")
    print("2024-01-15 10:30:18 - 步驟 2: 數據清洗")
    print("2024-01-15 10:30:20 - 步驟 3: 分析完成")
    print("---")


# ============================================================================
# 範例 6: 用戶交互
# ============================================================================

def example_6_user_interaction():
    """流式輸出中的用戶交互"""
    print("\n" + "="*70)
    print("範例 6: 用戶交互")
    print("="*70)

    print("\n允許用戶在執行過程中交互：\n")

    print("```python")
    print("import sys")
    print("import select")
    print("")
    print("print('Agent 正在工作... (按 Ctrl+C 中止)')\\n')")
    print("")
    print("try:")
    print("    for chunk in agent.stream(task):")
    print("        print(chunk, end='', flush=True)")
    print("        ")
    print("        # 檢查用戶輸入（非阻塞）")
    print("        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:")
    print("            user_input = sys.stdin.readline().strip()")
    print("            if user_input.lower() == 'skip':")
    print("                print('\\n用戶跳過當前步驟')")
    print("                break")
    print("")
    print("except KeyboardInterrupt:")
    print("    print('\\n\\n用戶中止執行')")
    print("```")

    print("\n用戶體驗優化：")
    print("  - 顯示可用命令")
    print("  - 提供進度估算")
    print("  - 允許暫停/繼續")
    print("  - 優雅處理中斷")


# ============================================================================
# 範例 7: 錯誤處理
# ============================================================================

def example_7_error_handling():
    """流式輸出中的錯誤處理"""
    print("\n" + "="*70)
    print("範例 7: 錯誤處理")
    print("="*70)

    print("\n處理流式執行中的錯誤：\n")

    print("```python")
    print("collected_output = []")
    print("error_occurred = False")
    print("")
    print("try:")
    print("    for chunk in agent.stream(task, verbose=1):")
    print("        # 收集輸出")
    print("        collected_output.append(chunk)")
    print("        print(chunk, end='', flush=True)")
    print("        ")
    print("        # 檢查錯誤標誌")
    print("        if 'ERROR' in chunk or 'FAILED' in chunk:")
    print("            error_occurred = True")
    print("")
    print("except Exception as e:")
    print("    print(f'\\n\\n錯誤: {e}')")
    print("    error_occurred = True")
    print("")
    print("finally:")
    print("    # 保存輸出供調試")
    print("    if error_occurred:")
    print("        with open('error_log.txt', 'w') as f:")
    print("            f.write(''.join(collected_output))")
    print("        print('錯誤日誌已保存到 error_log.txt')")
    print("```")

    print("\n最佳實踐：")
    print("  - 始終使用 try-except")
    print("  - 保存部分輸出")
    print("  - 提供有用的錯誤消息")
    print("  - 允許重試")


# ============================================================================
# 範例 8: 性能考慮
# ============================================================================

def example_8_performance():
    """流式輸出的性能考慮"""
    print("\n" + "="*70)
    print("範例 8: 性能考慮")
    print("="*70)

    print("\n流式輸出的性能特點：\n")

    print("優勢：")
    print("  ✓ 更早開始顯示結果")
    print("  ✓ 更好的用戶感知速度")
    print("  ✓ 內存效率（不需要緩存完整響應）")

    print("\n注意事項：")
    print("  - 每個 chunk 都有 I/O 開銷")
    print("  - 過於頻繁的更新可能影響性能")
    print("  - 建議批量處理 chunk")

    print("\n優化建議：")
    print("```python")
    print("buffer = []")
    print("buffer_size = 100  # 字符")
    print("")
    print("for chunk in agent.stream(task):")
    print("    buffer.append(chunk)")
    print("    ")
    print("    # 達到緩衝大小或遇到換行")
    print("    if len(''.join(buffer)) >= buffer_size or '\\n' in chunk:")
    print("        print(''.join(buffer), end='', flush=True)")
    print("        buffer = []")
    print("")
    print("# 輸出剩餘內容")
    print("if buffer:")
    print("    print(''.join(buffer), end='', flush=True)")
    print("```")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*70)
    print("流式輸出 - 實時響應處理")
    print("="*70)

    examples = [
        ("範例 1: 為什麼需要流式輸出", example_1_why_streaming),
        ("範例 2: 基本流式輸出", example_2_basic_streaming),
        ("範例 3: 詳細輸出", example_3_verbose_streaming),
        ("範例 4: 進度顯示", example_4_progress_display),
        ("範例 5: 日誌記錄", example_5_logging),
        ("範例 6: 用戶交互", example_6_user_interaction),
        ("範例 7: 錯誤處理", example_7_error_handling),
        ("範例 8: 性能考慮", example_8_performance),
    ]

    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n{name} 執行失敗: {e}")

    print("\n" + "="*70)
    print("流式輸出完成！")
    print("="*70)

    print("\n關鍵要點：")
    print("  - 使用 stream() 方法啟用流式輸出")
    print("  - verbose 參數控制詳細程度")
    print("  - 實時反饋提升用戶體驗")
    print("  - 結合進度條更專業")
    print("  - 良好的錯誤處理很重要")

    print("\n恭喜！您已完成所有 smolagents 範例")
    print("現在可以開始構建自己的 Agent 應用了！")


if __name__ == "__main__":
    main()
