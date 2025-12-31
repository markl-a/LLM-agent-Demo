"""
Browser-Use 網頁導航範例

這個範例展示了如何使用 Browser-Use 進行複雜的網頁導航操作。
包括頁面跳轉、元素點擊、前進後退、滾動等操作。

主要功能：
1. 多頁面導航
2. 元素查找和點擊
3. 頁面滾動操作
4. 前進和後退
5. 等待頁面載入
6. URL 導航
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


async def basic_navigation_example():
    """
    基礎導航範例

    演示如何在網頁之間導航，包括：
    - 訪問 URL
    - 點擊連結
    - 頁面前進/後退
    """
    print("\n" + "="*60)
    print("範例 1: 基礎網頁導航")
    print("="*60)

    # 配置瀏覽器
    browser_config = BrowserConfig(
        headless=False,  # 顯示瀏覽器以便觀察
        disable_security=False,
    )

    # 創建導航任務
    agent = Agent(
        task="""
        執行以下導航任務：
        1. 訪問 https://www.wikipedia.org
        2. 點擊 'English' 連結進入英文維基百科
        3. 在搜尋框中搜尋 'Artificial Intelligence'
        4. 告訴我文章的第一段內容（摘要）
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始導航任務...")
        start_time = datetime.now()

        result = await agent.run()

        duration = (datetime.now() - start_time).total_seconds()
        print(f"\n✓ 導航完成！耗時: {duration:.2f} 秒")
        print(f"\n結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 導航失敗: {str(e)}")


async def multi_page_navigation_example():
    """
    多頁面導航範例

    演示如何在多個頁面之間進行複雜的導航。
    """
    print("\n" + "="*60)
    print("範例 2: 多頁面導航")
    print("="*60)

    agent = Agent(
        task="""
        執行以下多頁面導航任務：
        1. 訪問 https://news.ycombinator.com (Hacker News)
        2. 找到第一篇文章並點擊進入
        3. 記錄文章標題
        4. 返回首頁
        5. 找到第二篇文章並點擊進入
        6. 記錄文章標題
        7. 返回首頁
        8. 以列表形式返回這兩篇文章的標題
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n執行多頁面導航...")
        result = await agent.run()

        print(f"\n✓ 多頁面導航完成！")
        print(f"\n訪問的文章：\n{result}")

    except Exception as e:
        print(f"\n✗ 執行失敗: {str(e)}")


async def scroll_navigation_example():
    """
    滾動導航範例

    演示如何在頁面中進行滾動操作以查看更多內容。
    """
    print("\n" + "="*60)
    print("範例 3: 頁面滾動導航")
    print("="*60)

    agent = Agent(
        task="""
        執行以下滾動任務：
        1. 訪問 https://www.reddit.com
        2. 向下滾動頁面三次
        3. 每次滾動後等待內容載入
        4. 收集前 10 個貼文的標題
        5. 返回這些標題的列表
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n執行滾動導航...")
        result = await agent.run()

        print(f"\n✓ 滾動完成！")
        print(f"\n收集到的貼文：\n{result}")

    except Exception as e:
        print(f"\n✗ 執行失敗: {str(e)}")


async def menu_navigation_example():
    """
    選單導航範例

    演示如何與網站的導航選單互動。
    """
    print("\n" + "="*60)
    print("範例 4: 選單導航")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行以下選單導航任務：
        1. 訪問 https://www.python.org
        2. 找到頂部導航選單
        3. 點擊 'Downloads' 選項
        4. 找到最新的 Python 版本資訊
        5. 返回首頁
        6. 點擊 'Documentation' 選項
        7. 告訴我文檔首頁的主要章節
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n執行選單導航...")
        result = await agent.run()

        print(f"\n✓ 選單導航完成！")
        print(f"\n導航結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 執行失敗: {str(e)}")


async def breadcrumb_navigation_example():
    """
    麵包屑導航範例

    演示如何使用網站的麵包屑導航。
    """
    print("\n" + "="*60)
    print("範例 5: 麵包屑導航")
    print("="*60)

    agent = Agent(
        task="""
        執行以下麵包屑導航任務：
        1. 訪問 https://docs.python.org
        2. 進入任意一個深層次的文檔頁面
        3. 找到麵包屑導航（breadcrumb）
        4. 記錄導航路徑
        5. 使用麵包屑返回上一層
        6. 告訴我導航路徑和返回後的頁面標題
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n執行麵包屑導航...")
        result = await agent.run()

        print(f"\n✓ 麵包屑導航完成！")
        print(f"\n結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 執行失敗: {str(e)}")


async def search_and_navigate_example():
    """
    搜尋和導航範例

    演示如何使用網站的搜尋功能並導航到結果。
    """
    print("\n" + "="*60)
    print("範例 6: 搜尋導航")
    print("="*60)

    agent = Agent(
        task="""
        執行以下搜尋導航任務：
        1. 訪問 https://github.com
        2. 使用頂部搜尋框搜尋 'browser automation'
        3. 點擊第一個搜尋結果
        4. 記錄專案的名稱、星標數和描述
        5. 點擊 'Issues' 標籤
        6. 記錄前三個 issue 的標題
        7. 返回所有收集到的資訊
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n執行搜尋導航...")
        result = await agent.run()

        print(f"\n✓ 搜尋導航完成！")
        print(f"\n收集到的資訊：\n{result}")

    except Exception as e:
        print(f"\n✗ 執行失敗: {str(e)}")


async def dynamic_content_navigation_example():
    """
    動態內容導航範例

    演示如何處理動態載入的內容（如無限滾動、延遲載入等）。
    """
    print("\n" + "="*60)
    print("範例 7: 動態內容導航")
    print("="*60)

    agent = Agent(
        task="""
        執行以下動態內容導航任務：
        1. 訪問一個有無限滾動的網站（如 Twitter/X 或 Instagram）
        2. 向下滾動並等待新內容載入
        3. 重複滾動 3 次
        4. 記錄每次滾動後載入的新內容數量
        5. 返回總共看到的內容數量
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n執行動態內容導航...")
        result = await agent.run()

        print(f"\n✓ 動態內容導航完成！")
        print(f"\n結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 執行失敗: {str(e)}")


async def tab_navigation_example():
    """
    標籤頁導航範例

    演示如何在同一網站的不同標籤頁之間導航。
    """
    print("\n" + "="*60)
    print("範例 8: 標籤頁導航")
    print("="*60)

    agent = Agent(
        task="""
        執行以下標籤頁導航任務：
        1. 訪問 https://stackoverflow.com
        2. 點擊 'Questions' 標籤
        3. 記錄顯示的內容
        4. 點擊 'Tags' 標籤
        5. 記錄顯示的內容
        6. 點擊 'Users' 標籤
        7. 記錄顯示的內容
        8. 返回所有標籤頁的內容摘要
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n執行標籤頁導航...")
        result = await agent.run()

        print(f"\n✓ 標籤頁導航完成！")
        print(f"\n各標籤內容：\n{result}")

    except Exception as e:
        print(f"\n✗ 執行失敗: {str(e)}")


async def wait_and_navigate_example():
    """
    等待和導航範例

    演示如何智能地等待頁面元素載入後再進行導航。
    """
    print("\n" + "="*60)
    print("範例 9: 智能等待導航")
    print("="*60)

    agent = Agent(
        task="""
        執行以下智能等待導航任務：
        1. 訪問一個載入較慢的網站
        2. 等待頁面完全載入（包括圖片和動態內容）
        3. 確認關鍵元素已經出現
        4. 點擊一個需要等待的互動元素（如下拉選單）
        5. 等待下拉選單完全展開
        6. 選擇一個選項
        7. 等待頁面響應
        8. 返回操作結果
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n執行智能等待導航...")
        result = await agent.run()

        print(f"\n✓ 智能等待導航完成！")
        print(f"\n結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 執行失敗: {str(e)}")


async def complex_navigation_workflow():
    """
    複雜導航工作流範例

    演示一個完整的複雜導航場景。
    """
    print("\n" + "="*60)
    print("範例 10: 複雜導航工作流")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行以下複雜的導航工作流：

        第一階段 - 資訊收集：
        1. 訪問 https://news.ycombinator.com
        2. 收集前 5 個熱門文章的標題和連結

        第二階段 - 深度探索：
        3. 點擊第一篇文章的評論區
        4. 記錄評論數量和前 3 條評論
        5. 返回首頁

        第三階段 - 交叉驗證：
        6. 訪問 https://www.reddit.com/r/programming
        7. 查看是否有相同的主題討論
        8. 如果有，記錄相關討論

        第四階段 - 結果整理：
        9. 返回所有收集到的資訊
        10. 提供一個簡短的摘要
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n執行複雜導航工作流...")
        print("這可能需要較長時間，請耐心等待...\n")

        start_time = datetime.now()
        result = await agent.run()
        duration = (datetime.now() - start_time).total_seconds()

        print(f"\n✓ 複雜工作流完成！總耗時: {duration:.2f} 秒")
        print(f"\n完整結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 執行失敗: {str(e)}")


def print_navigation_tips():
    """
    打印導航技巧和最佳實踐
    """
    print("\n" + "="*60)
    print("網頁導航最佳實踐")
    print("="*60)

    tips = [
        "1. 等待策略：",
        "   - 使用智能等待而非固定延遲",
        "   - 等待特定元素出現而非固定時間",
        "   - 處理動態載入的內容",
        "",
        "2. 元素定位：",
        "   - 優先使用語義化選擇器",
        "   - 提供清晰的元素描述給 AI",
        "   - 考慮頁面結構可能的變化",
        "",
        "3. 錯誤處理：",
        "   - 處理頁面載入失敗",
        "   - 處理元素找不到的情況",
        "   - 實現重試機制",
        "",
        "4. 性能優化：",
        "   - 避免不必要的頁面跳轉",
        "   - 複用已打開的頁面",
        "   - 合理設置超時時間",
        "",
        "5. 任務設計：",
        "   - 將複雜任務分解為小步驟",
        "   - 提供明確的成功標準",
        "   - 記錄中間結果以便調試",
    ]

    for tip in tips:
        print(tip)

    print("="*60)


async def main():
    """
    主函數 - 運行所有導航範例
    """
    print("\n" + "="*60)
    print("Browser-Use 網頁導航範例集")
    print("="*60)

    # 檢查 API 金鑰
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠ 請設置 OPENAI_API_KEY 環境變數")
        return

    examples = [
        ("基礎網頁導航", basic_navigation_example),
        ("多頁面導航", multi_page_navigation_example),
        ("頁面滾動導航", scroll_navigation_example),
        ("選單導航", menu_navigation_example),
        ("麵包屑導航", breadcrumb_navigation_example),
        ("搜尋導航", search_and_navigate_example),
        ("動態內容導航", dynamic_content_navigation_example),
        ("標籤頁導航", tab_navigation_example),
        ("智能等待導航", wait_and_navigate_example),
        ("複雜導航工作流", complex_navigation_workflow),
    ]

    print("\n可用的導航範例：")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i:2d}. {name}")

    print("\n" + "-"*60)
    user_input = input("\n請選擇要運行的範例編號（1-10），或按 Enter 查看導航技巧：")

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
        print_navigation_tips()

    print("\n" + "="*60)
    print("網頁導航範例演示完成！")
    print("="*60 + "\n")


if __name__ == "__main__":
    """
    運行導航範例

    使用方式：
    python 02_網頁導航.py
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n程式已被用戶中斷。")
    except Exception as e:
        print(f"\n發生錯誤：{str(e)}")
        import traceback
        traceback.print_exc()
