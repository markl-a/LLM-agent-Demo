"""
Browser-Use 多標籤頁管理範例

這個範例展示了如何使用 Browser-Use 管理和操作多個瀏覽器標籤頁。
包括創建新標籤、切換標籤、並行處理、標籤頁間數據傳遞等。

主要功能：
1. 創建和關閉標籤頁
2. 在標籤頁之間切換
3. 並行處理多個標籤頁
4. 標籤頁間數據共享
5. 管理標籤頁生命週期
6. 處理彈出視窗
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

try:
    from browser_use import Agent, BrowserConfig
except ImportError:
    print("請先安裝 browser-use: pip install browser-use")
    exit(1)


async def basic_tab_management_example():
    """
    基礎標籤頁管理範例

    演示如何創建、切換和關閉標籤頁。
    """
    print("\n" + "="*60)
    print("範例 1: 基礎標籤頁管理")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行基礎標籤頁管理：
        1. 打開第一個標籤頁，訪問 https://www.google.com
        2. 打開第二個標籤頁，訪問 https://www.wikipedia.org
        3. 打開第三個標籤頁，訪問 https://www.github.com
        4. 列出所有打開的標籤頁及其 URL
        5. 切換回第一個標籤頁
        6. 告訴我當前標籤頁的標題
        7. 關閉第二個標籤頁
        8. 報告剩餘的標籤頁數量
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始標籤頁管理...")
        result = await agent.run()

        print(f"\n✓ 標籤頁管理完成！")
        print(f"\n執行結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 執行失敗: {str(e)}")


async def parallel_tab_processing_example():
    """
    並行標籤頁處理範例

    演示如何在多個標籤頁中並行執行任務。
    """
    print("\n" + "="*60)
    print("範例 2: 並行標籤頁處理")
    print("="*60)

    agent = Agent(
        task="""
        執行並行標籤頁處理：
        1. 打開 3 個標籤頁
        2. 第一個標籤頁：搜尋 'Python programming'
        3. 第二個標籤頁：搜尋 'JavaScript tutorials'
        4. 第三個標籤頁：搜尋 'Machine Learning basics'
        5. 在每個標籤頁中提取前 3 個搜尋結果的標題
        6. 將所有結果整合成一個報告
        7. 報告應該清楚標示每個搜尋詞的結果
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n開始並行處理...")
        print("這可能需要較長時間，請稍候...")

        start_time = datetime.now()
        result = await agent.run()
        duration = (datetime.now() - start_time).total_seconds()

        print(f"\n✓ 並行處理完成！耗時: {duration:.2f} 秒")
        print(f"\n處理結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 處理失敗: {str(e)}")


async def tab_data_sharing_example():
    """
    標籤頁間數據共享範例

    演示如何在不同標籤頁之間傳遞和共享數據。
    """
    print("\n" + "="*60)
    print("範例 3: 標籤頁間數據共享")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行標籤頁數據共享任務：
        1. 第一個標籤頁：訪問 https://news.ycombinator.com
        2. 提取第一篇文章的標題和 URL
        3. 第二個標籤頁：打開該文章的 URL
        4. 在第二個標籤頁中閱讀內容
        5. 返回第一個標籤頁
        6. 提取第二篇文章的標題和 URL
        7. 第三個標籤頁：打開該文章的 URL
        8. 整合所有訪問過的文章資訊
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始數據共享任務...")
        result = await agent.run()

        print(f"\n✓ 數據共享完成！")
        print(f"\n共享結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 執行失敗: {str(e)}")


async def popup_window_handling_example():
    """
    彈出視窗處理範例

    演示如何處理彈出視窗和新窗口。
    """
    print("\n" + "="*60)
    print("範例 4: 彈出視窗處理")
    print("="*60)

    agent = Agent(
        task="""
        執行彈出視窗處理：
        1. 訪問一個可能有彈出視窗的網站
        2. 檢測是否有新的彈出視窗出現
        3. 如果有彈出視窗：
           - 切換到彈出視窗
           - 記錄彈出視窗的內容
           - 關閉彈出視窗
        4. 返回主視窗
        5. 繼續主視窗的操作
        6. 報告處理過程
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n開始處理彈出視窗...")
        result = await agent.run()

        print(f"\n✓ 彈出視窗處理完成！")
        print(f"\n處理結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 處理失敗: {str(e)}")


async def sequential_tab_workflow_example():
    """
    順序標籤頁工作流範例

    演示一個需要順序處理多個標籤頁的複雜工作流。
    """
    print("\n" + "="*60)
    print("範例 5: 順序標籤頁工作流")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行順序標籤頁工作流：

        階段 1 - 資訊收集：
        1. 標籤頁 1：訪問 https://www.python.org
        2. 提取最新的 Python 版本號
        3. 記錄下載連結

        階段 2 - 文檔查找：
        4. 標籤頁 2：訪問 Python 文檔頁面
        5. 搜尋 "asyncio" 相關文檔
        6. 記錄文檔 URL

        階段 3 - 社群資源：
        7. 標籤頁 3：訪問 https://github.com
        8. 搜尋 "python asyncio examples"
        9. 記錄前 3 個相關專案

        階段 4 - 整合報告：
        10. 整合所有收集的資訊
        11. 生成結構化報告
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始順序工作流...")
        print("這是一個多階段任務，請稍候...\n")

        start_time = datetime.now()
        result = await agent.run()
        duration = (datetime.now() - start_time).total_seconds()

        print(f"\n✓ 順序工作流完成！總耗時: {duration:.2f} 秒")
        print(f"\n整合報告：\n{result}")

    except Exception as e:
        print(f"\n✗ 執行失敗: {str(e)}")


async def tab_state_management_example():
    """
    標籤頁狀態管理範例

    演示如何管理標籤頁的狀態和生命週期。
    """
    print("\n" + "="*60)
    print("範例 6: 標籤頁狀態管理")
    print("="*60)

    agent = Agent(
        task="""
        執行標籤頁狀態管理：
        1. 創建 5 個標籤頁
        2. 在每個標籤頁中載入不同的網站
        3. 記錄每個標籤頁的：
           - 標題
           - URL
           - 載入狀態
        4. 找出載入最慢的標籤頁
        5. 關閉載入失敗或超時的標籤頁
        6. 報告最終的標籤頁狀態
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n開始狀態管理...")
        result = await agent.run()

        print(f"\n✓ 狀態管理完成！")
        print(f"\n狀態報告：\n{result}")

    except Exception as e:
        print(f"\n✗ 執行失敗: {str(e)}")


async def cross_tab_comparison_example():
    """
    跨標籤頁比較範例

    演示如何在多個標籤頁中比較相同類型的數據。
    """
    print("\n" + "="*60)
    print("範例 7: 跨標籤頁數據比較")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行跨標籤頁數據比較：
        1. 標籤頁 1：訪問 Hacker News
        2. 標籤頁 2：訪問 Reddit r/programming
        3. 標籤頁 3：訪問 Dev.to
        4. 在每個標籤頁提取前 5 個熱門話題
        5. 比較三個網站的話題
        6. 找出共同討論的主題
        7. 生成比較報告
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始跨標籤頁比較...")
        result = await agent.run()

        print(f"\n✓ 比較完成！")
        print(f"\n比較報告：\n{result}")

    except Exception as e:
        print(f"\n✗ 比較失敗: {str(e)}")


async def tab_resource_optimization():
    """
    標籤頁資源優化範例

    演示如何優化多標籤頁的資源使用。
    """
    print("\n" + "="*60)
    print("範例 8: 標籤頁資源優化")
    print("="*60)

    agent = Agent(
        task="""
        執行資源優化管理：
        1. 創建 10 個標籤頁
        2. 在每個標籤頁執行輕量任務
        3. 完成任務後立即關閉標籤頁
        4. 監控記憶體使用情況
        5. 實施標籤頁複用策略
        6. 報告資源使用效率
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n開始資源優化...")
        result = await agent.run()

        print(f"\n✓ 資源優化完成！")
        print(f"\n優化報告：\n{result}")

    except Exception as e:
        print(f"\n✗ 優化失敗: {str(e)}")


async def complex_multi_tab_workflow():
    """
    複雜多標籤頁工作流範例

    演示一個涉及多個標籤頁的完整業務流程。
    """
    print("\n" + "="*60)
    print("範例 9: 複雜多標籤頁工作流")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行複雜的多標籤頁工作流：

        準備階段：
        1. 打開主控標籤頁用於協調

        執行階段：
        2. 標籤頁 A：收集 GitHub 上的趨勢專案
        3. 標籤頁 B：同時收集 Hacker News 的熱門討論
        4. 標籤頁 C：同時檢查 Stack Overflow 的熱門問題

        分析階段：
        5. 在主控標籤頁整合所有數據
        6. 找出跨平台的共同主題
        7. 識別最熱門的技術趨勢

        深入研究階段：
        8. 對識別出的熱門主題開啟新標籤頁
        9. 深入研究每個主題
        10. 收集詳細資訊

        報告階段：
        11. 生成完整的技術趨勢報告
        12. 包括數據來源、趨勢分析、詳細資訊
        13. 清理並關閉所有輔助標籤頁
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始複雜工作流...")
        print("這是一個大型任務，可能需要數分鐘...\n")

        start_time = datetime.now()
        result = await agent.run()
        duration = (datetime.now() - start_time).total_seconds()

        print(f"\n✓ 複雜工作流完成！總耗時: {duration:.2f} 秒")
        print(f"\n完整報告：\n{result}")

    except Exception as e:
        print(f"\n✗ 執行失敗: {str(e)}")


def print_multi_tab_tips():
    """
    打印多標籤頁管理技巧和最佳實踐
    """
    print("\n" + "="*60)
    print("多標籤頁管理最佳實踐")
    print("="*60)

    tips = [
        "1. 標籤頁生命週期管理：",
        "   - 及時關閉不需要的標籤頁",
        "   - 避免同時開啟過多標籤頁",
        "   - 實施標籤頁複用策略",
        "   - 監控標籤頁狀態",
        "",
        "2. 並行處理策略：",
        "   - 識別可並行執行的任務",
        "   - 合理分配資源",
        "   - 實施任務優先級",
        "   - 處理並行競爭條件",
        "",
        "3. 數據同步：",
        "   - 使用共享數據結構",
        "   - 實施數據鎖定機制",
        "   - 避免數據競爭",
        "   - 確保數據一致性",
        "",
        "4. 錯誤處理：",
        "   - 隔離標籤頁錯誤",
        "   - 實施重試機制",
        "   - 記錄失敗的標籤頁",
        "   - 優雅降級",
        "",
        "5. 性能優化：",
        "   - 限制並行標籤頁數量",
        "   - 使用無頭模式",
        "   - 禁用不必要的資源載入",
        "   - 實施標籤頁池",
        "",
        "6. 記憶體管理：",
        "   - 監控記憶體使用",
        "   - 定期清理標籤頁",
        "   - 避免記憶體洩漏",
        "   - 設置資源限制",
        "",
        "7. 任務協調：",
        "   - 使用主控標籤頁協調",
        "   - 實施任務隊列",
        "   - 管理任務依賴",
        "   - 追蹤任務進度",
    ]

    for tip in tips:
        print(tip)

    print("="*60)


async def main():
    """
    主函數 - 運行所有多標籤頁範例
    """
    print("\n" + "="*60)
    print("Browser-Use 多標籤頁管理範例集")
    print("="*60)

    # 檢查 API 金鑰
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠ 請設置 OPENAI_API_KEY 環境變數")
        return

    examples = [
        ("基礎標籤頁管理", basic_tab_management_example),
        ("並行標籤頁處理", parallel_tab_processing_example),
        ("標籤頁數據共享", tab_data_sharing_example),
        ("彈出視窗處理", popup_window_handling_example),
        ("順序標籤頁工作流", sequential_tab_workflow_example),
        ("標籤頁狀態管理", tab_state_management_example),
        ("跨標籤頁數據比較", cross_tab_comparison_example),
        ("標籤頁資源優化", tab_resource_optimization),
        ("複雜多標籤頁工作流", complex_multi_tab_workflow),
    ]

    print("\n可用的多標籤頁範例：")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i:2d}. {name}")

    print("\n" + "-"*60)
    user_input = input("\n請選擇要運行的範例編號（1-9），或按 Enter 查看管理技巧：")

    if user_input.strip():
        try:
            index = int(user_input) - 1
            if 0 <= index < len(examples):
                name, func = examples[index]
                await func()
            else:
                print("無效的選擇！")
        except ValueError:
            print("請輸入有效的數字！")
    else:
        print_multi_tab_tips()

    print("\n" + "="*60)
    print("多標籤頁管理範例演示完成！")
    print("="*60)
    print("\n提示：")
    print("- 多標籤頁管理是提升效率的關鍵")
    print("- 注意資源使用，避免過度消耗")
    print("- 實施良好的錯誤隔離機制")
    print("="*60 + "\n")


if __name__ == "__main__":
    """
    運行多標籤頁管理範例

    使用方式：
    python 05_多標籤頁.py
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n程式已被用戶中斷。")
    except Exception as e:
        print(f"\n發生錯誤：{str(e)}")
        import traceback
        traceback.print_exc()
