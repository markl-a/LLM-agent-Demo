"""
Browser-Use 快速開始範例

這個範例展示了如何使用 Browser-Use 框架進行基礎的瀏覽器控制操作。
我們將演示如何創建 Agent、執行簡單的網頁任務，並獲取結果。

主要功能：
1. 初始化 Browser-Use Agent
2. 執行簡單的搜尋任務
3. 提取網頁內容
4. 處理和顯示結果
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 檢查是否有安裝 browser-use
try:
    from browser_use import Agent, BrowserConfig
except ImportError:
    print("請先安裝 browser-use: pip install browser-use")
    exit(1)


async def basic_search_example():
    """
    基礎搜尋範例

    這個函數示範如何使用 Browser-Use 執行簡單的網頁搜尋任務。
    Agent 會自動：
    1. 打開瀏覽器
    2. 訪問搜尋引擎
    3. 輸入搜尋關鍵字
    4. 提取搜尋結果
    """
    print("\n" + "="*60)
    print("範例 1: 基礎 Google 搜尋")
    print("="*60)

    # 創建 Agent 實例
    agent = Agent(
        task="在 Google 上搜尋 'Python 教程'，並提取前三個搜尋結果的標題和連結",
        llm_model="gpt-4",  # 可以改為 claude-3-5-sonnet-20241022 或其他模型
    )

    try:
        # 執行任務
        print("\n正在執行搜尋任務...")
        start_time = datetime.now()

        result = await agent.run()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # 顯示結果
        print(f"\n✓ 任務完成！耗時: {duration:.2f} 秒")
        print(f"\n搜尋結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 執行失敗: {str(e)}")


async def website_visit_example():
    """
    網站訪問範例

    這個函數示範如何訪問特定網站並提取資訊。
    """
    print("\n" + "="*60)
    print("範例 2: 訪問特定網站並提取資訊")
    print("="*60)

    # 配置瀏覽器設定
    browser_config = BrowserConfig(
        headless=False,  # 設為 False 可以看到瀏覽器操作過程
        disable_security=False,
    )

    # 創建 Agent
    agent = Agent(
        task="訪問 https://example.com 並告訴我頁面的主要標題和內容",
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n正在訪問網站...")
        result = await agent.run()

        print(f"\n✓ 訪問成功！")
        print(f"\n頁面資訊：\n{result}")

    except Exception as e:
        print(f"\n✗ 執行失敗: {str(e)}")


async def extract_data_example():
    """
    數據提取範例

    這個函數示範如何從網頁中提取結構化數據。
    """
    print("\n" + "="*60)
    print("範例 3: 提取網頁結構化數據")
    print("="*60)

    # 創建 Agent，要求提取結構化數據
    agent = Agent(
        task="""
        訪問 https://www.python.org 並提取以下資訊：
        1. 最新的 Python 版本號
        2. 首頁的主要導航選單項目
        3. 最新的新聞標題（如果有的話）

        請以 JSON 格式返回結果
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n正在提取數據...")
        result = await agent.run()

        print(f"\n✓ 數據提取成功！")
        print(f"\n提取的數據：\n{result}")

    except Exception as e:
        print(f"\n✗ 執行失敗: {str(e)}")


async def click_and_navigate_example():
    """
    點擊和導航範例

    這個函數示範如何進行頁面導航和元素點擊操作。
    """
    print("\n" + "="*60)
    print("範例 4: 頁面導航和元素點擊")
    print("="*60)

    # 創建 Agent
    agent = Agent(
        task="""
        1. 訪問 https://www.wikipedia.org
        2. 找到並點擊 '中文' 或 'English' 語言選項
        3. 告訴我進入後頁面的標題
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n正在執行導航任務...")
        result = await agent.run()

        print(f"\n✓ 導航成功！")
        print(f"\n執行結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 執行失敗: {str(e)}")


async def custom_config_example():
    """
    自定義配置範例

    這個函數示範如何使用自定義的瀏覽器配置。
    """
    print("\n" + "="*60)
    print("範例 5: 使用自定義瀏覽器配置")
    print("="*60)

    # 自定義瀏覽器配置
    browser_config = BrowserConfig(
        headless=True,  # 無頭模式，不顯示瀏覽器視窗
        disable_security=False,
        window_width=1920,  # 視窗寬度
        window_height=1080,  # 視窗高度
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    )

    # 創建 Agent
    agent = Agent(
        task="訪問 https://httpbin.org/user-agent 並告訴我檢測到的 User-Agent",
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n正在執行任務...")
        result = await agent.run()

        print(f"\n✓ 任務完成！")
        print(f"\n結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 執行失敗: {str(e)}")


async def error_handling_example():
    """
    錯誤處理範例

    這個函數示範如何處理可能發生的錯誤。
    """
    print("\n" + "="*60)
    print("範例 6: 錯誤處理機制")
    print("="*60)

    # 創建一個可能失敗的任務
    agent = Agent(
        task="訪問 https://this-website-does-not-exist-12345.com 並提取內容",
        llm_model="gpt-4",
    )

    try:
        print("\n嘗試訪問不存在的網站...")
        result = await agent.run()
        print(f"\n結果：\n{result}")

    except Exception as e:
        print(f"\n✓ 成功捕獲錯誤：{type(e).__name__}")
        print(f"錯誤訊息：{str(e)}")
        print("\n這是預期的行為，Agent 會嘗試處理錯誤情況")


def check_environment():
    """
    檢查環境配置

    在執行範例前，檢查必要的環境變數是否已設置。
    """
    print("\n檢查環境配置...")

    required_vars = {
        "OPENAI_API_KEY": "OpenAI API 金鑰",
        # 如果要使用其他模型，取消下面的註解
        # "ANTHROPIC_API_KEY": "Anthropic API 金鑰",
        # "GOOGLE_API_KEY": "Google API 金鑰",
    }

    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"  - {var} ({description})")

    if missing_vars:
        print("\n⚠ 警告：以下環境變數未設置：")
        for var in missing_vars:
            print(var)
        print("\n請在 .env 文件中設置這些變數，或使用 export 命令：")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return False

    print("✓ 環境配置正確！")
    return True


async def main():
    """
    主函數

    運行所有範例。
    """
    print("\n" + "="*60)
    print("Browser-Use 快速開始範例集")
    print("="*60)

    # 檢查環境
    if not check_environment():
        print("\n請先配置環境變數後再運行範例。")
        return

    # 運行各個範例
    examples = [
        ("基礎搜尋", basic_search_example),
        ("網站訪問", website_visit_example),
        ("數據提取", extract_data_example),
        ("頁面導航", click_and_navigate_example),
        ("自定義配置", custom_config_example),
        ("錯誤處理", error_handling_example),
    ]

    print("\n本範例包含以下示範：")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")

    print("\n" + "-"*60)
    user_input = input("\n請選擇要運行的範例編號（1-6），或按 Enter 運行全部：")

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
        # 運行所有範例
        for name, func in examples:
            await func()
            await asyncio.sleep(2)  # 範例之間稍作等待

    print("\n" + "="*60)
    print("所有範例執行完畢！")
    print("="*60)
    print("\n下一步：")
    print("- 查看其他範例文件學習更多功能")
    print("- 修改這些範例以適應您的需求")
    print("- 閱讀 README.md 了解更多詳情")
    print("="*60 + "\n")


if __name__ == "__main__":
    """
    程式進入點

    使用方式：
    1. 確保已安裝所有依賴：pip install -r requirements.txt
    2. 設置 API 金鑰：export OPENAI_API_KEY='your-key'
    3. 運行程式：python 01_快速開始.py
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n程式已被用戶中斷。")
    except Exception as e:
        print(f"\n發生錯誤：{str(e)}")
        import traceback
        traceback.print_exc()
