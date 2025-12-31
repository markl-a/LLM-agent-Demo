"""
Browser-Use 表單填寫範例

這個範例展示了如何使用 Browser-Use 自動填寫各種類型的網頁表單。
包括文字輸入、下拉選單、單選框、複選框、文件上傳等。

主要功能：
1. 文字輸入框填寫
2. 下拉選單選擇
3. 單選框和複選框操作
4. 日期選擇器
5. 文件上傳
6. 表單驗證
7. 表單提交
"""

import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, List
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

try:
    from browser_use import Agent, BrowserConfig
except ImportError:
    print("請先安裝 browser-use: pip install browser-use")
    exit(1)


async def simple_text_input_example():
    """
    簡單文字輸入範例

    演示如何填寫基本的文字輸入框。
    """
    print("\n" + "="*60)
    print("範例 1: 簡單文字輸入")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行以下表單填寫任務：
        1. 訪問 https://httpbin.org/forms/post
        2. 在 'custname' 欄位填寫：張三
        3. 在 'custtel' 欄位填寫：0912345678
        4. 在 'custemail' 欄位填寫：zhangsan@example.com
        5. 在 'comments' 欄位填寫：這是測試留言
        6. 不要提交表單，只是填寫
        7. 告訴我已填寫的內容
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始填寫表單...")
        result = await agent.run()

        print(f"\n✓ 表單填寫完成！")
        print(f"\n填寫結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 填寫失敗: {str(e)}")


async def dropdown_selection_example():
    """
    下拉選單選擇範例

    演示如何操作下拉選單。
    """
    print("\n" + "="*60)
    print("範例 2: 下拉選單選擇")
    print("="*60)

    agent = Agent(
        task="""
        執行以下下拉選單操作：
        1. 訪問一個包含下拉選單的表單頁面
        2. 找到所有下拉選單
        3. 選擇第一個下拉選單中的第二個選項
        4. 記錄選擇的值
        5. 告訴我下拉選單的所有可用選項和已選擇的選項
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n開始操作下拉選單...")
        result = await agent.run()

        print(f"\n✓ 下拉選單操作完成！")
        print(f"\n操作結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 操作失敗: {str(e)}")


async def checkbox_radio_example():
    """
    複選框和單選框範例

    演示如何操作複選框和單選框。
    """
    print("\n" + "="*60)
    print("範例 3: 複選框和單選框")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行以下操作：
        1. 訪問 https://httpbin.org/forms/post
        2. 找到所有的單選框（radio buttons）
        3. 選擇 'Medium' 大小（size）
        4. 找到所有的複選框（checkboxes）
        5. 勾選 'Bacon' 選項
        6. 告訴我已選擇的選項
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始操作選擇框...")
        result = await agent.run()

        print(f"\n✓ 選擇框操作完成！")
        print(f"\n操作結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 操作失敗: {str(e)}")


async def complete_form_example():
    """
    完整表單填寫範例

    演示如何填寫一個完整的表單並提交。
    """
    print("\n" + "="*60)
    print("範例 4: 完整表單填寫")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行完整的表單填寫流程：
        1. 訪問 https://httpbin.org/forms/post
        2. 填寫所有必填欄位：
           - Customer name: 李四
           - Telephone: 0923456789
           - Email: lisi@example.com
           - Size: Large (單選框)
           - Topping: Cheese (複選框)
           - Delivery time: 盡快
           - Comments: 請盡快送達
        3. 檢查所有欄位是否正確填寫
        4. 提交表單
        5. 告訴我提交後的響應內容
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始填寫完整表單...")
        result = await agent.run()

        print(f"\n✓ 表單提交成功！")
        print(f"\n提交結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 提交失敗: {str(e)}")


async def multi_step_form_example():
    """
    多步驟表單範例

    演示如何填寫多頁的表單（如註冊流程）。
    """
    print("\n" + "="*60)
    print("範例 5: 多步驟表單")
    print("="*60)

    agent = Agent(
        task="""
        執行多步驟表單填寫：
        1. 訪問一個多步驟註冊表單網站
        2. 第一步：填寫基本資訊（姓名、郵箱）
        3. 點擊「下一步」
        4. 第二步：填寫聯絡資訊（電話、地址）
        5. 點擊「下一步」
        6. 第三步：填寫偏好設定
        7. 點擊「完成」
        8. 記錄每一步的進度
        9. 告訴我完整的註冊流程和結果
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n開始填寫多步驟表單...")
        result = await agent.run()

        print(f"\n✓ 多步驟表單完成！")
        print(f"\n結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 執行失敗: {str(e)}")


async def form_validation_example():
    """
    表單驗證範例

    演示如何處理表單驗證錯誤。
    """
    print("\n" + "="*60)
    print("範例 6: 表單驗證處理")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        測試表單驗證：
        1. 訪問一個有驗證規則的表單
        2. 故意填寫錯誤的郵箱格式（如 'invalid-email'）
        3. 嘗試提交
        4. 觀察並記錄驗證錯誤訊息
        5. 更正郵箱為正確格式（如 'user@example.com'）
        6. 再次提交
        7. 告訴我驗證過程和結果
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始測試表單驗證...")
        result = await agent.run()

        print(f"\n✓ 驗證測試完成！")
        print(f"\n測試結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 測試失敗: {str(e)}")


async def dynamic_form_example():
    """
    動態表單範例

    演示如何處理根據選擇動態變化的表單。
    """
    print("\n" + "="*60)
    print("範例 7: 動態表單填寫")
    print("="*60)

    agent = Agent(
        task="""
        處理動態表單：
        1. 訪問一個包含動態欄位的表單
        2. 在「國家」下拉選單選擇「美國」
        3. 觀察「州」下拉選單是否出現
        4. 在「州」下拉選單選擇「加州」
        5. 觀察是否有更多欄位出現
        6. 填寫所有動態出現的欄位
        7. 記錄表單的變化過程
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n開始處理動態表單...")
        result = await agent.run()

        print(f"\n✓ 動態表單處理完成！")
        print(f"\n結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 處理失敗: {str(e)}")


async def autocomplete_example():
    """
    自動完成輸入範例

    演示如何處理帶有自動完成功能的輸入框。
    """
    print("\n" + "="*60)
    print("範例 8: 自動完成輸入")
    print("="*60)

    agent = Agent(
        task="""
        處理自動完成輸入：
        1. 訪問 Google 首頁
        2. 在搜尋框中輸入 'Python'
        3. 等待自動完成建議出現
        4. 記錄所有建議選項
        5. 點擊第二個建議
        6. 告訴我建議列表和最終選擇的項目
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n開始處理自動完成...")
        result = await agent.run()

        print(f"\n✓ 自動完成處理完成！")
        print(f"\n結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 處理失敗: {str(e)}")


async def file_upload_simulation():
    """
    文件上傳模擬範例

    演示如何處理文件上傳（注意：實際上傳需要真實文件）。
    """
    print("\n" + "="*60)
    print("範例 9: 文件上傳處理")
    print("="*60)

    agent = Agent(
        task="""
        處理文件上傳欄位：
        1. 訪問一個包含文件上傳的表單
        2. 找到文件上傳按鈕
        3. 觀察按鈕的屬性和要求（如接受的文件類型）
        4. 記錄文件大小限制和格式要求
        5. 告訴我上傳欄位的所有限制和要求
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n開始處理文件上傳...")
        result = await agent.run()

        print(f"\n✓ 文件上傳處理完成！")
        print(f"\n結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 處理失敗: {str(e)}")


async def complex_registration_form():
    """
    複雜註冊表單範例

    演示一個完整的用戶註冊流程。
    """
    print("\n" + "="*60)
    print("範例 10: 複雜註冊表單")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    # 生成隨機用戶資訊
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    user_data = {
        "username": f"testuser_{timestamp}",
        "email": f"testuser_{timestamp}@example.com",
        "password": "SecurePass123!",
        "first_name": "測試",
        "last_name": "用戶",
        "phone": "0912345678",
    }

    agent = Agent(
        task=f"""
        執行完整的用戶註冊流程：

        第一階段 - 訪問註冊頁面：
        1. 訪問註冊頁面
        2. 確認頁面已完全載入

        第二階段 - 填寫基本資訊：
        3. 填寫用戶名：{user_data['username']}
        4. 填寫郵箱：{user_data['email']}
        5. 填寫密碼：{user_data['password']}
        6. 確認密碼：{user_data['password']}

        第三階段 - 填寫個人資訊：
        7. 填寫姓氏：{user_data['last_name']}
        8. 填寫名字：{user_data['first_name']}
        9. 填寫電話：{user_data['phone']}

        第四階段 - 隱私和條款：
        10. 勾選「我已閱讀並同意服務條款」
        11. 勾選「我已閱讀並同意隱私政策」

        第五階段 - 驗證和提交：
        12. 檢查所有欄位是否正確填寫
        13. 處理任何驗證錯誤
        14. 提交表單
        15. 記錄註冊結果（成功訊息或錯誤訊息）

        請提供完整的註冊過程報告。
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始執行註冊流程...")
        print(f"使用的測試帳號：{user_data['username']}")

        start_time = datetime.now()
        result = await agent.run()
        duration = (datetime.now() - start_time).total_seconds()

        print(f"\n✓ 註冊流程完成！耗時: {duration:.2f} 秒")
        print(f"\n註冊結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 註冊失敗: {str(e)}")


def print_form_filling_tips():
    """
    打印表單填寫技巧和最佳實踐
    """
    print("\n" + "="*60)
    print("表單填寫最佳實踐")
    print("="*60)

    tips = [
        "1. 元素識別策略：",
        "   - 使用 label 文字來識別輸入框",
        "   - 檢查 placeholder 提示文字",
        "   - 利用 name 和 id 屬性",
        "   - 考慮使用 ARIA 標籤",
        "",
        "2. 輸入驗證：",
        "   - 填寫前檢查欄位要求",
        "   - 注意必填欄位標記",
        "   - 遵守格式限制（郵箱、電話等）",
        "   - 處理即時驗證反饋",
        "",
        "3. 動態內容處理：",
        "   - 等待下拉選單載入完成",
        "   - 處理條件顯示的欄位",
        "   - 應對自動完成建議",
        "   - 處理 AJAX 表單提交",
        "",
        "4. 錯誤處理：",
        "   - 捕獲驗證錯誤訊息",
        "   - 重試失敗的操作",
        "   - 記錄錯誤詳情",
        "   - 提供友好的錯誤報告",
        "",
        "5. 安全考量：",
        "   - 不在代碼中硬編碼敏感資訊",
        "   - 使用環境變數存儲憑證",
        "   - 注意 CAPTCHA 和反機器人檢測",
        "   - 遵守網站的使用條款",
        "",
        "6. 性能優化：",
        "   - 批量填寫多個欄位",
        "   - 減少不必要的等待時間",
        "   - 複用表單驗證結果",
        "   - 優化表單提交流程",
    ]

    for tip in tips:
        print(tip)

    print("="*60)


async def main():
    """
    主函數 - 運行所有表單填寫範例
    """
    print("\n" + "="*60)
    print("Browser-Use 表單填寫範例集")
    print("="*60)

    # 檢查 API 金鑰
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠ 請設置 OPENAI_API_KEY 環境變數")
        return

    examples = [
        ("簡單文字輸入", simple_text_input_example),
        ("下拉選單選擇", dropdown_selection_example),
        ("複選框和單選框", checkbox_radio_example),
        ("完整表單填寫", complete_form_example),
        ("多步驟表單", multi_step_form_example),
        ("表單驗證處理", form_validation_example),
        ("動態表單填寫", dynamic_form_example),
        ("自動完成輸入", autocomplete_example),
        ("文件上傳處理", file_upload_simulation),
        ("複雜註冊表單", complex_registration_form),
    ]

    print("\n可用的表單填寫範例：")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i:2d}. {name}")

    print("\n" + "-"*60)
    user_input = input("\n請選擇要運行的範例編號（1-10），或按 Enter 查看填寫技巧：")

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
        print_form_filling_tips()

    print("\n" + "="*60)
    print("表單填寫範例演示完成！")
    print("="*60)
    print("\n提示：")
    print("- 表單填寫是 Web 自動化的核心功能")
    print("- 處理好驗證和錯誤情況很重要")
    print("- 記得遵守網站的使用條款和 robots.txt")
    print("="*60 + "\n")


if __name__ == "__main__":
    """
    運行表單填寫範例

    使用方式：
    python 03_表單填寫.py
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n程式已被用戶中斷。")
    except Exception as e:
        print(f"\n發生錯誤：{str(e)}")
        import traceback
        traceback.print_exc()
