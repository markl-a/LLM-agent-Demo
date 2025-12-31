"""
Browser-Use 購物流程自動化範例

這個範例展示了如何使用 Browser-Use 自動化完整的電商購物流程。
包括商品搜尋、瀏覽、加入購物車、結帳等操作。

主要功能：
1. 商品搜尋和篩選
2. 商品詳情查看
3. 加入購物車
4. 購物車管理
5. 結帳流程
6. 訂單追蹤

注意：本範例使用演示網站，不會進行真實交易。
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


async def product_search_example():
    """
    商品搜尋範例

    演示如何在電商網站搜尋商品。
    """
    print("\n" + "="*60)
    print("範例 1: 商品搜尋")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行商品搜尋任務：
        1. 訪問電商演示網站（如 https://www.saucedemo.com）
        2. 如果需要登錄，使用測試帳號登錄
           用戶名：standard_user
           密碼：secret_sauce
        3. 找到搜尋框或商品列表
        4. 瀏覽所有可用的商品
        5. 記錄商品的名稱和價格
        6. 按價格從低到高排序（如果有排序選項）
        7. 返回前 5 個最便宜的商品資訊
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始商品搜尋...")
        start_time = datetime.now()

        result = await agent.run()

        duration = (datetime.now() - start_time).total_seconds()
        print(f"\n✓ 商品搜尋完成！耗時: {duration:.2f} 秒")
        print(f"\n搜尋結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 搜尋失敗: {str(e)}")


async def product_filtering_example():
    """
    商品篩選範例

    演示如何使用篩選器縮小商品範圍。
    """
    print("\n" + "="*60)
    print("範例 2: 商品篩選")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行商品篩選任務：
        1. 訪問電商網站並登錄
        2. 查看商品列表
        3. 使用排序功能：
           - 嘗試「價格從低到高」排序
           - 記錄排序後的前 3 個商品
        4. 如果有篩選選項：
           - 嘗試按類別篩選
           - 記錄篩選結果
        5. 返回篩選和排序的完整結果
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始商品篩選...")
        result = await agent.run()

        print(f"\n✓ 商品篩選完成！")
        print(f"\n篩選結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 篩選失敗: {str(e)}")


async def product_details_example():
    """
    商品詳情查看範例

    演示如何查看商品的詳細資訊。
    """
    print("\n" + "="*60)
    print("範例 3: 查看商品詳情")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行商品詳情查看：
        1. 訪問電商網站並登錄
        2. 選擇第一個商品
        3. 點擊進入商品詳情頁
        4. 提取以下資訊：
           - 商品名稱
           - 商品價格
           - 商品描述
           - 商品圖片 URL
           - 庫存狀態
        5. 返回商品列表
        6. 選擇另一個商品重複步驟 3-4
        7. 比較兩個商品的資訊
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始查看商品詳情...")
        result = await agent.run()

        print(f"\n✓ 商品詳情查看完成！")
        print(f"\n商品資訊：\n{result}")

    except Exception as e:
        print(f"\n✗ 查看失敗: {str(e)}")


async def add_to_cart_example():
    """
    加入購物車範例

    演示如何將商品加入購物車。
    """
    print("\n" + "="*60)
    print("範例 4: 加入購物車")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行加入購物車操作：
        1. 訪問電商網站並登錄
        2. 選擇第一個商品並點擊「加入購物車」按鈕
        3. 確認購物車圖標更新（顯示數量）
        4. 選擇第二個商品並加入購物車
        5. 選擇第三個商品並加入購物車
        6. 點擊購物車圖標查看購物車
        7. 確認所有 3 個商品都在購物車中
        8. 記錄每個商品的名稱、價格和數量
        9. 計算購物車總金額
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始加入購物車...")
        result = await agent.run()

        print(f"\n✓ 加入購物車完成！")
        print(f"\n購物車內容：\n{result}")

    except Exception as e:
        print(f"\n✗ 操作失敗: {str(e)}")


async def cart_management_example():
    """
    購物車管理範例

    演示如何管理購物車中的商品。
    """
    print("\n" + "="*60)
    print("範例 5: 購物車管理")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行購物車管理：
        1. 訪問電商網站並登錄
        2. 加入 3-4 個商品到購物車
        3. 打開購物車頁面
        4. 記錄初始的購物車內容和總價
        5. 移除其中一個商品
        6. 確認商品已被移除，總價已更新
        7. 如果可以修改數量：
           - 將某個商品的數量改為 2
           - 確認總價更新
        8. 清空購物車（移除所有商品）
        9. 確認購物車為空
        10. 報告整個管理過程
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始購物車管理...")
        result = await agent.run()

        print(f"\n✓ 購物車管理完成！")
        print(f"\n管理報告：\n{result}")

    except Exception as e:
        print(f"\n✗ 管理失敗: {str(e)}")


async def checkout_flow_example():
    """
    結帳流程範例

    演示完整的結帳流程。
    """
    print("\n" + "="*60)
    print("範例 6: 結帳流程")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行結帳流程：
        1. 訪問電商網站並登錄
        2. 加入至少 2 個商品到購物車
        3. 進入購物車頁面
        4. 點擊「結帳」或「Checkout」按鈕
        5. 填寫配送資訊：
           - 姓名：Test User
           - 郵遞區號：12345
        6. 點擊繼續
        7. 查看訂單摘要
        8. 記錄訂單詳情（商品、價格、總計）
        9. 不要完成最終支付，停在確認頁面
        10. 報告結帳流程的每個步驟
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始結帳流程...")
        result = await agent.run()

        print(f"\n✓ 結帳流程完成！")
        print(f"\n流程報告：\n{result}")

    except Exception as e:
        print(f"\n✗ 結帳失敗: {str(e)}")


async def price_comparison_example():
    """
    價格比較範例

    演示如何比較不同商品的價格。
    """
    print("\n" + "="*60)
    print("範例 7: 價格比較")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行價格比較任務：
        1. 訪問電商網站並登錄
        2. 收集所有商品的價格資訊
        3. 建立價格列表
        4. 找出：
           - 最便宜的商品
           - 最貴的商品
           - 平均價格
        5. 按價格排序所有商品
        6. 找出性價比最高的商品（如果有評分的話）
        7. 生成價格分析報告
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始價格比較...")
        result = await agent.run()

        print(f"\n✓ 價格比較完成！")
        print(f"\n分析報告：\n{result}")

    except Exception as e:
        print(f"\n✗ 比較失敗: {str(e)}")


async def wishlist_management_example():
    """
    願望清單管理範例

    演示如何管理商品願望清單。
    """
    print("\n" + "="*60)
    print("範例 8: 願望清單管理")
    print("="*60)

    agent = Agent(
        task="""
        執行願望清單管理：
        1. 訪問電商網站並登錄
        2. 查找「加入願望清單」或「收藏」功能
        3. 將 3 個商品加入願望清單
        4. 訪問願望清單頁面
        5. 確認所有商品都在願望清單中
        6. 從願望清單中移除一個商品
        7. 從願望清單直接加入購物車（如果支援）
        8. 報告願望清單功能的完整操作
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n開始願望清單管理...")
        result = await agent.run()

        print(f"\n✓ 願望清單管理完成！")
        print(f"\n管理報告：\n{result}")

    except Exception as e:
        print(f"\n✗ 管理失敗: {str(e)}")


async def complete_shopping_workflow():
    """
    完整購物工作流範例

    演示一個端到端的完整購物流程。
    """
    print("\n" + "="*60)
    print("範例 9: 完整購物工作流")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行完整的購物工作流：

        第一階段 - 登錄和瀏覽：
        1. 訪問 https://www.saucedemo.com
        2. 使用測試帳號登錄
           用戶名：standard_user
           密碼：secret_sauce
        3. 瀏覽所有可用商品

        第二階段 - 商品選擇：
        4. 按價格排序（從低到高）
        5. 選擇 3 個價格最低的商品
        6. 查看每個商品的詳細資訊
        7. 將這 3 個商品加入購物車

        第三階段 - 購物車確認：
        8. 打開購物車
        9. 確認所有商品都已加入
        10. 檢查總金額
        11. 如果總金額過高，移除最貴的商品

        第四階段 - 結帳流程：
        12. 開始結帳流程
        13. 填寫配送資訊
        14. 查看訂單摘要
        15. 記錄最終訂單詳情

        第五階段 - 報告生成：
        16. 生成完整的購物報告，包括：
            - 選擇的商品清單
            - 每個商品的價格
            - 總金額
            - 配送資訊
            - 整個流程的時間線
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始完整購物工作流...")
        print("這是一個複雜的多階段流程，可能需要幾分鐘...\n")

        start_time = datetime.now()
        result = await agent.run()
        duration = (datetime.now() - start_time).total_seconds()

        print(f"\n✓ 完整購物工作流完成！總耗時: {duration:.2f} 秒")
        print(f"\n購物報告：\n{result}")

        # 保存報告
        report_file = f"/tmp/shopping_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"購物流程報告\n")
            f.write(f"完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"總耗時: {duration:.2f} 秒\n")
            f.write(f"\n{'='*60}\n\n")
            f.write(str(result))

        print(f"\n報告已保存到: {report_file}")

    except Exception as e:
        print(f"\n✗ 工作流失敗: {str(e)}")


def print_shopping_automation_tips():
    """
    打印購物自動化技巧和最佳實踐
    """
    print("\n" + "="*60)
    print("電商購物自動化最佳實踐")
    print("="*60)

    tips = [
        "1. 商品選擇策略：",
        "   - 使用篩選器縮小範圍",
        "   - 比較多個商品",
        "   - 檢查庫存狀態",
        "   - 閱讀商品評價",
        "",
        "2. 購物車管理：",
        "   - 定期檢查購物車內容",
        "   - 移除不需要的商品",
        "   - 注意商品數量限制",
        "   - 檢查價格變動",
        "",
        "3. 結帳流程：",
        "   - 驗證配送資訊",
        "   - 確認訂單總額",
        "   - 選擇適當的配送方式",
        "   - 保存訂單確認",
        "",
        "4. 錯誤處理：",
        "   - 處理商品缺貨情況",
        "   - 處理價格變動",
        "   - 處理結帳錯誤",
        "   - 實施重試機制",
        "",
        "5. 性能優化：",
        "   - 複用瀏覽器會話",
        "   - 批量處理商品",
        "   - 使用快取減少請求",
        "   - 並行處理獨立任務",
        "",
        "6. 安全考量：",
        "   - 使用測試環境",
        "   - 不進行真實交易",
        "   - 保護支付資訊",
        "   - 遵守網站規則",
        "",
        "7. 數據記錄：",
        "   - 記錄商品資訊",
        "   - 追蹤價格歷史",
        "   - 保存訂單詳情",
        "   - 生成購物報告",
        "",
        "8. 合規性：",
        "   - 遵守服務條款",
        "   - 尊重爬蟲協議",
        "   - 避免過度請求",
        "   - 不進行價格操縱",
    ]

    for tip in tips:
        print(tip)

    print("="*60)


async def main():
    """
    主函數 - 運行所有購物流程範例
    """
    print("\n" + "="*60)
    print("Browser-Use 購物流程自動化範例集")
    print("="*60)

    # 檢查 API 金鑰
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠ 請設置 OPENAI_API_KEY 環境變數")
        return

    examples = [
        ("商品搜尋", product_search_example),
        ("商品篩選", product_filtering_example),
        ("查看商品詳情", product_details_example),
        ("加入購物車", add_to_cart_example),
        ("購物車管理", cart_management_example),
        ("結帳流程", checkout_flow_example),
        ("價格比較", price_comparison_example),
        ("願望清單管理", wishlist_management_example),
        ("完整購物工作流", complete_shopping_workflow),
    ]

    print("\n可用的購物流程範例：")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i:2d}. {name}")

    print("\n測試網站資訊：")
    print("URL: https://www.saucedemo.com")
    print("測試帳號: standard_user")
    print("密碼: secret_sauce")

    print("\n" + "-"*60)
    user_input = input("\n請選擇要運行的範例編號（1-9），或按 Enter 查看自動化技巧：")

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
        print_shopping_automation_tips()

    print("\n" + "="*60)
    print("購物流程範例演示完成！")
    print("="*60)
    print("\n重要提醒：")
    print("- 本範例僅用於學習和測試")
    print("- 不要在真實電商網站進行自動化操作")
    print("- 遵守網站的服務條款和使用規則")
    print("- 不要進行未經授權的交易")
    print("="*60 + "\n")


if __name__ == "__main__":
    """
    運行購物流程範例

    使用方式：
    python 07_購物流程.py
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n程式已被用戶中斷。")
    except Exception as e:
        print(f"\n發生錯誤：{str(e)}")
        import traceback
        traceback.print_exc()
