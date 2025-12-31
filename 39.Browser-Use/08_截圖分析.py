"""
Browser-Use 截圖分析範例

這個範例展示了如何使用 Browser-Use 的視覺分析功能。
包括頁面截圖、元素截圖、視覺驗證、OCR 文字識別等。

主要功能：
1. 全頁面截圖
2. 元素截圖
3. 視覺內容分析
4. OCR 文字識別
5. 視覺驗證
6. 截圖比較
7. 視覺回歸測試
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

try:
    from browser_use import Agent, BrowserConfig
except ImportError:
    print("請先安裝 browser-use: pip install browser-use")
    exit(1)


# 創建截圖保存目錄
SCREENSHOT_DIR = Path("/tmp/browser_use_screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)


async def full_page_screenshot_example():
    """
    全頁面截圖範例

    演示如何截取完整頁面的截圖。
    """
    print("\n" + "="*60)
    print("範例 1: 全頁面截圖")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = SCREENSHOT_DIR / f"fullpage_{timestamp}.png"

    agent = Agent(
        task=f"""
        執行全頁面截圖：
        1. 訪問 https://www.python.org
        2. 等待頁面完全載入
        3. 截取完整頁面的截圖
        4. 保存截圖到：{screenshot_path}
        5. 分析截圖內容：
           - 識別頁面的主要元素
           - 檢測頁面顏色方案
           - 識別主要文字內容
        6. 報告截圖資訊和分析結果
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始全頁面截圖...")
        start_time = datetime.now()

        result = await agent.run()

        duration = (datetime.now() - start_time).total_seconds()
        print(f"\n✓ 全頁面截圖完成！耗時: {duration:.2f} 秒")
        print(f"\n截圖已保存到: {screenshot_path}")
        print(f"\n分析結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 截圖失敗: {str(e)}")


async def element_screenshot_example():
    """
    元素截圖範例

    演示如何截取特定元素的截圖。
    """
    print("\n" + "="*60)
    print("範例 2: 元素截圖")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行元素截圖：
        1. 訪問 https://www.github.com
        2. 找到主要的搜尋框元素
        3. 截取搜尋框的截圖
        4. 找到導航選單
        5. 截取導航選單的截圖
        6. 找到主要內容區域
        7. 截取主要內容的截圖
        8. 分析每個元素的視覺特徵
        9. 報告所有元素截圖的資訊
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始元素截圖...")
        result = await agent.run()

        print(f"\n✓ 元素截圖完成！")
        print(f"\n分析結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 截圖失敗: {str(e)}")


async def visual_content_analysis_example():
    """
    視覺內容分析範例

    演示如何分析頁面的視覺內容。
    """
    print("\n" + "="*60)
    print("範例 3: 視覺內容分析")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行視覺內容分析：
        1. 訪問 https://www.wikipedia.org
        2. 截取首頁截圖
        3. 分析視覺元素：
           - 識別 Logo 和品牌元素
           - 檢測主要顏色和配色方案
           - 識別按鈕和互動元素
           - 分析頁面佈局結構
        4. 識別所有語言選項
        5. 分析頁面的視覺層次
        6. 生成詳細的視覺分析報告
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始視覺內容分析...")
        result = await agent.run()

        print(f"\n✓ 視覺分析完成！")
        print(f"\n分析報告：\n{result}")

    except Exception as e:
        print(f"\n✗ 分析失敗: {str(e)}")


async def ocr_text_recognition_example():
    """
    OCR 文字識別範例

    演示如何使用 OCR 從圖片中識別文字。
    """
    print("\n" + "="*60)
    print("範例 4: OCR 文字識別")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行 OCR 文字識別：
        1. 訪問包含圖片文字的網頁
        2. 找到包含文字的圖片元素
        3. 截取這些圖片
        4. 使用 OCR 識別圖片中的文字
        5. 提取並整理識別出的文字
        6. 與頁面上的實際文字比較（如果有的話）
        7. 報告 OCR 識別結果和準確度
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始 OCR 文字識別...")
        result = await agent.run()

        print(f"\n✓ OCR 識別完成！")
        print(f"\n識別結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 識別失敗: {str(e)}")


async def visual_verification_example():
    """
    視覺驗證範例

    演示如何驗證頁面的視覺元素。
    """
    print("\n" + "="*60)
    print("範例 5: 視覺驗證")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行視覺驗證：
        1. 訪問 https://www.saucedemo.com
        2. 截取登錄頁面截圖
        3. 驗證以下視覺元素：
           - Logo 是否顯示
           - 用戶名輸入框是否可見
           - 密碼輸入框是否可見
           - 登錄按鈕是否可見
           - 頁面佈局是否正確
        4. 登錄後截取主頁截圖
        5. 驗證登錄後的視覺元素：
           - 商品列表是否顯示
           - 購物車圖標是否顯示
           - 導航選單是否顯示
        6. 生成視覺驗證報告
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始視覺驗證...")
        result = await agent.run()

        print(f"\n✓ 視覺驗證完成！")
        print(f"\n驗證報告：\n{result}")

    except Exception as e:
        print(f"\n✗ 驗證失敗: {str(e)}")


async def screenshot_comparison_example():
    """
    截圖比較範例

    演示如何比較不同狀態的頁面截圖。
    """
    print("\n" + "="*60)
    print("範例 6: 截圖比較")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    agent = Agent(
        task=f"""
        執行截圖比較：
        1. 訪問 https://www.python.org
        2. 截取初始狀態的截圖（保存為 before_{timestamp}.png）
        3. 執行某些操作（如點擊選單、搜尋等）
        4. 截取操作後的截圖（保存為 after_{timestamp}.png）
        5. 比較兩張截圖：
           - 識別視覺差異
           - 檢測新增或移除的元素
           - 分析佈局變化
        6. 生成詳細的比較報告
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始截圖比較...")
        result = await agent.run()

        print(f"\n✓ 截圖比較完成！")
        print(f"\n比較報告：\n{result}")

    except Exception as e:
        print(f"\n✗ 比較失敗: {str(e)}")


async def responsive_design_testing():
    """
    響應式設計測試範例

    演示如何測試不同螢幕尺寸下的頁面顯示。
    """
    print("\n" + "="*60)
    print("範例 7: 響應式設計測試")
    print("="*60)

    # 測試不同的視窗尺寸
    viewports = [
        ("桌面", 1920, 1080),
        ("平板", 768, 1024),
        ("手機", 375, 667),
    ]

    results = []

    for name, width, height in viewports:
        print(f"\n測試 {name} 視窗 ({width}x{height})...")

        browser_config = BrowserConfig(
            headless=False,
            disable_security=False,
            window_width=width,
            window_height=height,
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = SCREENSHOT_DIR / f"responsive_{name}_{timestamp}.png"

        agent = Agent(
            task=f"""
            在 {width}x{height} 視窗尺寸下測試頁面：
            1. 訪問 https://www.wikipedia.org
            2. 等待頁面完全載入
            3. 截取全頁面截圖，保存到 {screenshot_path}
            4. 分析頁面佈局：
               - 元素排列是否合理
               - 文字是否可讀
               - 圖片是否正確縮放
               - 導航選單是否正確顯示
            5. 報告在此尺寸下的顯示狀況
            """,
            llm_model="gpt-4",
            browser_config=browser_config,
        )

        try:
            result = await agent.run()
            results.append({
                "viewport": name,
                "size": f"{width}x{height}",
                "screenshot": str(screenshot_path),
                "analysis": result
            })
            print(f"✓ {name} 測試完成")

        except Exception as e:
            print(f"✗ {name} 測試失敗: {str(e)}")
            results.append({
                "viewport": name,
                "size": f"{width}x{height}",
                "error": str(e)
            })

    print("\n" + "="*60)
    print("響應式設計測試報告")
    print("="*60)
    for result in results:
        print(f"\n{result['viewport']} ({result['size']}):")
        if 'error' in result:
            print(f"  錯誤: {result['error']}")
        else:
            print(f"  截圖: {result['screenshot']}")
            print(f"  分析: {result['analysis'][:200]}...")


async def visual_regression_testing():
    """
    視覺回歸測試範例

    演示如何進行視覺回歸測試。
    """
    print("\n" + "="*60)
    print("範例 8: 視覺回歸測試")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行視覺回歸測試：
        1. 訪問測試頁面
        2. 截取基準截圖（baseline）
        3. 執行一些操作（如主題切換、語言切換）
        4. 返回初始狀態
        5. 截取當前截圖
        6. 比較基準截圖和當前截圖：
           - 檢測視覺差異
           - 計算相似度
           - 識別不一致的區域
        7. 判斷是否存在視覺回歸
        8. 生成回歸測試報告
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始視覺回歸測試...")
        result = await agent.run()

        print(f"\n✓ 視覺回歸測試完成！")
        print(f"\n測試報告：\n{result}")

    except Exception as e:
        print(f"\n✗ 測試失敗: {str(e)}")


async def accessibility_visual_check():
    """
    無障礙性視覺檢查範例

    演示如何進行視覺無障礙性檢查。
    """
    print("\n" + "="*60)
    print("範例 9: 無障礙性視覺檢查")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行無障礙性視覺檢查：
        1. 訪問網頁
        2. 截取頁面截圖
        3. 檢查視覺無障礙性：
           - 檢測顏色對比度
           - 識別文字大小是否合適
           - 檢查互動元素是否足夠大
           - 驗證重要資訊是否清晰可見
        4. 檢查鍵盤導航可見性：
           - 焦點指示器是否明顯
           - 選中狀態是否清晰
        5. 檢查替代文字：
           - 圖片是否有 alt 文字
           - 按鈕是否有清晰標籤
        6. 生成無障礙性檢查報告
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始無障礙性檢查...")
        result = await agent.run()

        print(f"\n✓ 無障礙性檢查完成！")
        print(f"\n檢查報告：\n{result}")

    except Exception as e:
        print(f"\n✗ 檢查失敗: {str(e)}")


def print_visual_testing_tips():
    """
    打印視覺測試技巧和最佳實踐
    """
    print("\n" + "="*60)
    print("視覺測試最佳實踐")
    print("="*60)

    tips = [
        "1. 截圖策略：",
        "   - 等待頁面完全載入後再截圖",
        "   - 使用一致的視窗尺寸",
        "   - 處理動態內容（如動畫）",
        "   - 考慮截圖時機",
        "",
        "2. 圖片質量：",
        "   - 使用適當的圖片格式（PNG、JPEG）",
        "   - 設置合適的解析度",
        "   - 壓縮大型截圖以節省空間",
        "   - 保持截圖清晰度",
        "",
        "3. 視覺比較：",
        "   - 設定合理的相似度閾值",
        "   - 忽略可接受的差異（如時間戳）",
        "   - 使用結構化比較方法",
        "   - 記錄所有差異",
        "",
        "4. OCR 優化：",
        "   - 提高圖片質量",
        "   - 使用適當的預處理",
        "   - 選擇正確的 OCR 引擎",
        "   - 驗證識別結果",
        "",
        "5. 存儲管理：",
        "   - 組織截圖文件結構",
        "   - 定期清理舊截圖",
        "   - 使用有意義的文件名",
        "   - 實施版本控制",
        "",
        "6. 性能考量：",
        "   - 限制截圖數量",
        "   - 使用異步處理",
        "   - 壓縮和優化圖片",
        "   - 並行處理多個截圖",
        "",
        "7. 測試自動化：",
        "   - 建立基準截圖庫",
        "   - 自動化比較流程",
        "   - 集成到 CI/CD 管道",
        "   - 生成視覺測試報告",
        "",
        "8. 無障礙性：",
        "   - 檢查顏色對比度",
        "   - 驗證文字可讀性",
        "   - 測試不同視窗尺寸",
        "   - 考慮色盲友好設計",
    ]

    for tip in tips:
        print(tip)

    print("="*60)


async def main():
    """
    主函數 - 運行所有截圖分析範例
    """
    print("\n" + "="*60)
    print("Browser-Use 截圖分析範例集")
    print("="*60)

    # 檢查 API 金鑰
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠ 請設置 OPENAI_API_KEY 環境變數")
        return

    print(f"\n截圖保存目錄: {SCREENSHOT_DIR}")

    examples = [
        ("全頁面截圖", full_page_screenshot_example),
        ("元素截圖", element_screenshot_example),
        ("視覺內容分析", visual_content_analysis_example),
        ("OCR 文字識別", ocr_text_recognition_example),
        ("視覺驗證", visual_verification_example),
        ("截圖比較", screenshot_comparison_example),
        ("響應式設計測試", responsive_design_testing),
        ("視覺回歸測試", visual_regression_testing),
        ("無障礙性視覺檢查", accessibility_visual_check),
    ]

    print("\n可用的截圖分析範例：")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i:2d}. {name}")

    print("\n" + "-"*60)
    user_input = input("\n請選擇要運行的範例編號（1-9），或按 Enter 查看視覺測試技巧：")

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
        print_visual_testing_tips()

    print("\n" + "="*60)
    print("截圖分析範例演示完成！")
    print("="*60)
    print("\n提示：")
    print("- 視覺分析是確保 UI 質量的重要方法")
    print("- 定期進行視覺回歸測試")
    print("- 關注無障礙性和響應式設計")
    print(f"- 檢查保存的截圖: {SCREENSHOT_DIR}")
    print("="*60 + "\n")


if __name__ == "__main__":
    """
    運行截圖分析範例

    使用方式：
    python 08_截圖分析.py
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n程式已被用戶中斷。")
    except Exception as e:
        print(f"\n發生錯誤：{str(e)}")
        import traceback
        traceback.print_exc()
