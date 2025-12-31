"""
Browser-Use 數據提取範例

這個範例展示了如何使用 Browser-Use 從網頁中提取各種類型的數據。
包括文字內容、表格數據、列表數據、圖片連結、結構化數據等。

主要功能：
1. 提取網頁文字內容
2. 提取表格數據
3. 提取列表數據
4. 提取連結和圖片
5. 提取結構化數據（JSON-LD、Microdata）
6. 提取動態載入的內容
7. 數據清理和格式化
"""

import asyncio
import os
import json
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


async def extract_text_content_example():
    """
    提取文字內容範例

    演示如何從網頁中提取純文字內容。
    """
    print("\n" + "="*60)
    print("範例 1: 提取網頁文字內容")
    print("="*60)

    agent = Agent(
        task="""
        執行以下文字提取任務：
        1. 訪問 https://en.wikipedia.org/wiki/Artificial_intelligence
        2. 提取文章的第一段（摘要）
        3. 提取 'History' 章節的前兩段
        4. 提取頁面標題
        5. 以結構化格式返回所有提取的文字
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n開始提取文字內容...")
        start_time = datetime.now()

        result = await agent.run()

        duration = (datetime.now() - start_time).total_seconds()
        print(f"\n✓ 文字提取完成！耗時: {duration:.2f} 秒")
        print(f"\n提取的內容：\n{result}")

    except Exception as e:
        print(f"\n✗ 提取失敗: {str(e)}")


async def extract_table_data_example():
    """
    提取表格數據範例

    演示如何從網頁中提取表格數據。
    """
    print("\n" + "="*60)
    print("範例 2: 提取表格數據")
    print("="*60)

    agent = Agent(
        task="""
        執行以下表格數據提取：
        1. 訪問 https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)
        2. 找到主要的人口統計表格
        3. 提取前 10 個國家的數據
        4. 提取的欄位包括：國家名稱、人口數、百分比
        5. 以 JSON 格式返回數據，每個國家一個物件
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n開始提取表格數據...")
        result = await agent.run()

        print(f"\n✓ 表格數據提取完成！")
        print(f"\n提取的數據：\n{result}")

        # 嘗試解析為 JSON
        try:
            # 如果返回的是 JSON 字符串，嘗試美化輸出
            if isinstance(result, str) and result.strip().startswith('['):
                data = json.loads(result)
                print(f"\n格式化的 JSON：\n{json.dumps(data, indent=2, ensure_ascii=False)}")
        except:
            pass

    except Exception as e:
        print(f"\n✗ 提取失敗: {str(e)}")


async def extract_list_data_example():
    """
    提取列表數據範例

    演示如何提取網頁中的列表數據。
    """
    print("\n" + "="*60)
    print("範例 3: 提取列表數據")
    print("="*60)

    agent = Agent(
        task="""
        執行以下列表數據提取：
        1. 訪問 https://news.ycombinator.com
        2. 提取首頁前 15 個新聞項目
        3. 每個項目包括：
           - 標題
           - 連結 URL
           - 分數（如果有）
           - 評論數（如果有）
        4. 以結構化列表返回數據
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n開始提取列表數據...")
        result = await agent.run()

        print(f"\n✓ 列表數據提取完成！")
        print(f"\n提取的數據：\n{result}")

    except Exception as e:
        print(f"\n✗ 提取失敗: {str(e)}")


async def extract_links_images_example():
    """
    提取連結和圖片範例

    演示如何提取頁面中的所有連結和圖片。
    """
    print("\n" + "="*60)
    print("範例 4: 提取連結和圖片")
    print("="*60)

    agent = Agent(
        task="""
        執行以下資源提取：
        1. 訪問 https://www.python.org
        2. 提取頁面中所有的外部連結（href）
        3. 提取前 10 個圖片的 URL（src）
        4. 分別統計連結和圖片的數量
        5. 返回結構化數據，包括：
           - 總連結數
           - 總圖片數
           - 前 10 個連結的 URL 和文字
           - 前 10 個圖片的 URL 和 alt 文字
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n開始提取連結和圖片...")
        result = await agent.run()

        print(f"\n✓ 連結和圖片提取完成！")
        print(f"\n提取的數據：\n{result}")

    except Exception as e:
        print(f"\n✗ 提取失敗: {str(e)}")


async def extract_metadata_example():
    """
    提取元數據範例

    演示如何提取頁面的元數據（meta tags、Open Graph 等）。
    """
    print("\n" + "="*60)
    print("範例 5: 提取頁面元數據")
    print("="*60)

    agent = Agent(
        task="""
        執行以下元數據提取：
        1. 訪問 https://github.com
        2. 提取以下元數據：
           - 頁面標題（title）
           - meta description
           - meta keywords（如果有）
           - Open Graph 數據（og:title, og:description, og:image）
           - Twitter Card 數據（如果有）
        3. 以結構化格式返回所有元數據
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n開始提取元數據...")
        result = await agent.run()

        print(f"\n✓ 元數據提取完成！")
        print(f"\n提取的元數據：\n{result}")

    except Exception as e:
        print(f"\n✗ 提取失敗: {str(e)}")


async def extract_dynamic_content_example():
    """
    提取動態內容範例

    演示如何提取通過 JavaScript 動態載入的內容。
    """
    print("\n" + "="*60)
    print("範例 6: 提取動態載入的內容")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行動態內容提取：
        1. 訪問一個使用無限滾動的網站（如 Twitter 或 Reddit）
        2. 向下滾動 3 次，每次等待新內容載入
        3. 提取滾動過程中載入的所有內容項目
        4. 統計總共載入了多少個項目
        5. 返回前 20 個項目的標題或摘要
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始提取動態內容...")
        print("這可能需要較長時間，請稍候...")
        result = await agent.run()

        print(f"\n✓ 動態內容提取完成！")
        print(f"\n提取的內容：\n{result}")

    except Exception as e:
        print(f"\n✗ 提取失敗: {str(e)}")


async def extract_structured_data_example():
    """
    提取結構化數據範例

    演示如何提取頁面中的結構化數據（JSON-LD、Microdata）。
    """
    print("\n" + "="*60)
    print("範例 7: 提取結構化數據")
    print("="*60)

    agent = Agent(
        task="""
        執行結構化數據提取：
        1. 訪問一個包含結構化數據的網站（如產品頁面或文章頁面）
        2. 查找 JSON-LD 腳本標籤
        3. 提取並解析 JSON-LD 數據
        4. 查找 Microdata 或 RDFa 標記
        5. 返回所有找到的結構化數據
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n開始提取結構化數據...")
        result = await agent.run()

        print(f"\n✓ 結構化數據提取完成！")
        print(f"\n提取的數據：\n{result}")

    except Exception as e:
        print(f"\n✗ 提取失敗: {str(e)}")


async def extract_social_media_data():
    """
    提取社交媒體數據範例

    演示如何從社交媒體頁面提取數據。
    """
    print("\n" + "="*60)
    print("範例 8: 提取社交媒體數據")
    print("="*60)

    agent = Agent(
        task="""
        執行社交媒體數據提取：
        1. 訪問一個 GitHub 專案頁面（如 https://github.com/microsoft/vscode）
        2. 提取以下資訊：
           - 專案名稱
           - 星標數（Stars）
           - Fork 數
           - 觀察者數（Watchers）
           - 主要程式語言
           - 最後更新時間
           - README 的前三段
        3. 以結構化格式返回所有數據
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n開始提取社交媒體數據...")
        result = await agent.run()

        print(f"\n✓ 社交媒體數據提取完成！")
        print(f"\n提取的數據：\n{result}")

    except Exception as e:
        print(f"\n✗ 提取失敗: {str(e)}")


async def extract_ecommerce_data():
    """
    提取電商數據範例

    演示如何從電商網站提取產品資訊。
    """
    print("\n" + "="*60)
    print("範例 9: 提取電商產品數據")
    print("="*60)

    agent = Agent(
        task="""
        執行電商數據提取：
        1. 訪問一個電商產品頁面
        2. 提取以下產品資訊：
           - 產品名稱
           - 價格（當前價格、原價、折扣）
           - 產品評分和評論數
           - 產品描述
           - 產品圖片 URL
           - 產品規格（顏色、尺寸等選項）
           - 庫存狀態
        3. 以 JSON 格式返回完整的產品資訊
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n開始提取電商數據...")
        result = await agent.run()

        print(f"\n✓ 電商數據提取完成！")
        print(f"\n提取的數據：\n{result}")

    except Exception as e:
        print(f"\n✗ 提取失敗: {str(e)}")


async def comprehensive_data_extraction():
    """
    綜合數據提取範例

    演示一個完整的數據提取工作流。
    """
    print("\n" + "="*60)
    print("範例 10: 綜合數據提取工作流")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行綜合數據提取任務：

        階段 1 - 新聞網站數據：
        1. 訪問 https://news.ycombinator.com
        2. 提取前 5 個熱門新聞的標題、連結、分數

        階段 2 - 技術文檔數據：
        3. 訪問 https://docs.python.org
        4. 提取主要文檔章節的標題和連結

        階段 3 - 開源專案數據：
        5. 訪問 https://github.com/trending
        6. 提取前 3 個趨勢專案的名稱、描述、星標數

        階段 4 - 數據整合：
        7. 將所有提取的數據整合成一個結構化報告
        8. 包括數據來源、提取時間、數據統計

        最終輸出：
        - 以 JSON 格式返回完整的數據集
        - 包括元數據（提取時間、來源 URL、項目數量）
        - 每個數據源的詳細內容
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始綜合數據提取...")
        print("這是一個複雜的多階段任務，可能需要幾分鐘...\n")

        start_time = datetime.now()
        result = await agent.run()
        duration = (datetime.now() - start_time).total_seconds()

        print(f"\n✓ 綜合數據提取完成！總耗時: {duration:.2f} 秒")
        print(f"\n提取的完整數據：\n{result}")

        # 保存數據到文件
        output_file = f"/tmp/extracted_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"數據提取報告\n")
            f.write(f"提取時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"總耗時: {duration:.2f} 秒\n")
            f.write(f"\n{'='*60}\n\n")
            f.write(str(result))

        print(f"\n數據已保存到: {output_file}")

    except Exception as e:
        print(f"\n✗ 提取失敗: {str(e)}")


def print_data_extraction_tips():
    """
    打印數據提取技巧和最佳實踐
    """
    print("\n" + "="*60)
    print("數據提取最佳實踐")
    print("="*60)

    tips = [
        "1. 數據定位策略：",
        "   - 使用 CSS 選擇器精確定位",
        "   - 利用語義化 HTML 標籤",
        "   - 查找 data-* 屬性",
        "   - 使用 XPath 處理複雜結構",
        "",
        "2. 數據清理：",
        "   - 去除多餘的空白字符",
        "   - 標準化數據格式",
        "   - 處理缺失值",
        "   - 驗證數據完整性",
        "",
        "3. 處理動態內容：",
        "   - 等待 AJAX 請求完成",
        "   - 處理無限滾動",
        "   - 監聽 DOM 變化",
        "   - 使用適當的等待策略",
        "",
        "4. 結構化數據：",
        "   - 提取 JSON-LD 數據",
        "   - 解析 Microdata",
        "   - 處理 Open Graph 標籤",
        "   - 使用結構化輸出格式",
        "",
        "5. 性能優化：",
        "   - 批量提取數據",
        "   - 避免重複請求",
        "   - 使用緩存機制",
        "   - 並行處理多個頁面",
        "",
        "6. 錯誤處理：",
        "   - 處理元素不存在的情況",
        "   - 設置合理的超時時間",
        "   - 記錄失敗的提取",
        "   - 實現重試邏輯",
        "",
        "7. 道德和法律：",
        "   - 遵守 robots.txt",
        "   - 尊重網站的使用條款",
        "   - 設置合理的請求頻率",
        "   - 不提取私人或敏感資訊",
        "",
        "8. 數據存儲：",
        "   - 選擇合適的數據格式（JSON、CSV、Database）",
        "   - 記錄數據來源和時間戳",
        "   - 實現數據版本控制",
        "   - 定期備份重要數據",
    ]

    for tip in tips:
        print(tip)

    print("="*60)


async def main():
    """
    主函數 - 運行所有數據提取範例
    """
    print("\n" + "="*60)
    print("Browser-Use 數據提取範例集")
    print("="*60)

    # 檢查 API 金鑰
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠ 請設置 OPENAI_API_KEY 環境變數")
        return

    examples = [
        ("提取文字內容", extract_text_content_example),
        ("提取表格數據", extract_table_data_example),
        ("提取列表數據", extract_list_data_example),
        ("提取連結和圖片", extract_links_images_example),
        ("提取頁面元數據", extract_metadata_example),
        ("提取動態內容", extract_dynamic_content_example),
        ("提取結構化數據", extract_structured_data_example),
        ("提取社交媒體數據", extract_social_media_data),
        ("提取電商數據", extract_ecommerce_data),
        ("綜合數據提取", comprehensive_data_extraction),
    ]

    print("\n可用的數據提取範例：")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i:2d}. {name}")

    print("\n" + "-"*60)
    user_input = input("\n請選擇要運行的範例編號（1-10），或按 Enter 查看提取技巧：")

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
        print_data_extraction_tips()

    print("\n" + "="*60)
    print("數據提取範例演示完成！")
    print("="*60)
    print("\n重要提醒：")
    print("- 提取數據時請遵守網站的使用條款")
    print("- 設置合理的請求頻率，避免對網站造成負擔")
    print("- 不要提取和使用私人或敏感資訊")
    print("- 定期檢查和更新提取邏輯，因為網站結構可能變化")
    print("="*60 + "\n")


if __name__ == "__main__":
    """
    運行數據提取範例

    使用方式：
    python 04_數據提取.py
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n程式已被用戶中斷。")
    except Exception as e:
        print(f"\n發生錯誤：{str(e)}")
        import traceback
        traceback.print_exc()
