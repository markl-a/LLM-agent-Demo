"""
Browser-Use 登錄操作範例

這個範例展示了如何使用 Browser-Use 自動化各種登錄流程。
包括表單登錄、OAuth 登錄、雙因素認證、Cookie 管理等。

主要功能：
1. 基本用戶名密碼登錄
2. 處理記住我選項
3. Cookie 和會話管理
4. 登出操作
5. 自動重新登錄
6. 安全憑證管理

注意：本範例使用測試網站進行演示，不建議在生產環境中存儲真實憑證。
"""

import asyncio
import os
import json
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

try:
    from browser_use import Agent, BrowserConfig
except ImportError:
    print("請先安裝 browser-use: pip install browser-use")
    exit(1)


async def basic_login_example():
    """
    基本登錄範例

    演示基本的用戶名和密碼登錄流程。
    """
    print("\n" + "="*60)
    print("範例 1: 基本登錄操作")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行基本登錄操作：
        1. 訪問 https://practicetestautomation.com/practice-test-login/
        2. 在用戶名欄位輸入：student
        3. 在密碼欄位輸入：Password123
        4. 點擊登錄按鈕
        5. 等待登錄完成
        6. 確認是否成功登錄（檢查是否有成功訊息或跳轉）
        7. 報告登錄結果
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始登錄流程...")
        start_time = datetime.now()

        result = await agent.run()

        duration = (datetime.now() - start_time).total_seconds()
        print(f"\n✓ 登錄流程完成！耗時: {duration:.2f} 秒")
        print(f"\n登錄結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 登錄失敗: {str(e)}")


async def login_with_validation_example():
    """
    帶驗證的登錄範例

    演示如何處理登錄驗證和錯誤提示。
    """
    print("\n" + "="*60)
    print("範例 2: 帶驗證的登錄")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行帶驗證的登錄流程：

        第一次嘗試（錯誤憑證）：
        1. 訪問 https://practicetestautomation.com/practice-test-login/
        2. 輸入錯誤的用戶名和密碼
        3. 點擊登錄
        4. 觀察並記錄錯誤訊息

        第二次嘗試（正確憑證）：
        5. 清空表單
        6. 輸入正確的用戶名：student
        7. 輸入正確的密碼：Password123
        8. 點擊登錄
        9. 確認登錄成功

        報告：
        10. 報告兩次嘗試的結果和錯誤訊息
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始驗證登錄流程...")
        result = await agent.run()

        print(f"\n✓ 驗證登錄完成！")
        print(f"\n驗證結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 驗證失敗: {str(e)}")


async def remember_me_example():
    """
    記住我功能範例

    演示如何處理「記住我」選項。
    """
    print("\n" + "="*60)
    print("範例 3: 記住我功能")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        測試「記住我」功能：
        1. 訪問登錄頁面
        2. 填寫用戶名和密碼
        3. 勾選「記住我」複選框（如果有的話）
        4. 登錄
        5. 檢查是否設置了持久性 Cookie
        6. 登出
        7. 重新訪問網站
        8. 檢查是否自動登錄或保留用戶名
        9. 報告「記住我」功能的行為
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n測試記住我功能...")
        result = await agent.run()

        print(f"\n✓ 記住我測試完成！")
        print(f"\n測試結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 測試失敗: {str(e)}")


async def session_management_example():
    """
    會話管理範例

    演示如何管理登錄會話和 Cookie。
    """
    print("\n" + "="*60)
    print("範例 4: 會話管理")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行會話管理任務：
        1. 登錄到網站
        2. 檢查並記錄設置的 Cookie
        3. 執行一些需要登錄的操作
        4. 檢查會話是否仍然有效
        5. 如果會話過期，重新登錄
        6. 報告會話狀態和 Cookie 資訊
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始會話管理...")
        result = await agent.run()

        print(f"\n✓ 會話管理完成！")
        print(f"\n管理結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 管理失敗: {str(e)}")


async def auto_relogin_example():
    """
    自動重新登錄範例

    演示如何檢測會話過期並自動重新登錄。
    """
    print("\n" + "="*60)
    print("範例 5: 自動重新登錄")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    # 從環境變數讀取憑證（如果有的話）
    test_username = os.getenv("TEST_USERNAME", "student")
    test_password = os.getenv("TEST_PASSWORD", "Password123")

    agent = Agent(
        task=f"""
        實施自動重新登錄機制：
        1. 訪問登錄頁面
        2. 使用憑證登錄（用戶名：{test_username}）
        3. 執行需要登錄的操作
        4. 模擬或等待會話過期
        5. 檢測到未登錄狀態時
        6. 自動使用相同憑證重新登錄
        7. 繼續執行之前的操作
        8. 報告重新登錄過程
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n測試自動重新登錄...")
        result = await agent.run()

        print(f"\n✓ 自動重新登錄測試完成！")
        print(f"\n測試結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 測試失敗: {str(e)}")


async def multi_account_login_example():
    """
    多帳號登錄範例

    演示如何管理和切換多個帳號。
    """
    print("\n" + "="*60)
    print("範例 6: 多帳號登錄管理")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行多帳號管理：
        1. 使用第一個帳號登錄
        2. 執行該帳號的操作
        3. 記錄操作結果
        4. 登出
        5. 使用第二個帳號登錄
        6. 執行該帳號的操作
        7. 記錄操作結果
        8. 比較兩個帳號的數據差異
        9. 生成多帳號管理報告
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始多帳號管理...")
        result = await agent.run()

        print(f"\n✓ 多帳號管理完成！")
        print(f"\n管理報告：\n{result}")

    except Exception as e:
        print(f"\n✗ 管理失敗: {str(e)}")


async def social_login_simulation():
    """
    社交登錄模擬範例

    演示社交媒體登錄流程（模擬）。
    """
    print("\n" + "="*60)
    print("範例 7: 社交登錄流程")
    print("="*60)

    agent = Agent(
        task="""
        模擬社交登錄流程：
        1. 訪問有社交登錄選項的網站
        2. 識別社交登錄按鈕（Google、Facebook、GitHub 等）
        3. 記錄可用的社交登錄選項
        4. 點擊其中一個社交登錄按鈕
        5. 觀察跳轉行為
        6. 記錄跳轉的 URL 和參數
        7. 報告社交登錄流程

        注意：不要實際完成社交登錄，只是觀察流程
        """,
        llm_model="gpt-4",
    )

    try:
        print("\n開始社交登錄模擬...")
        result = await agent.run()

        print(f"\n✓ 社交登錄模擬完成！")
        print(f"\n模擬結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 模擬失敗: {str(e)}")


async def logout_verification_example():
    """
    登出驗證範例

    演示如何正確登出並驗證登出狀態。
    """
    print("\n" + "="*60)
    print("範例 8: 登出驗證")
    print("="*60)

    browser_config = BrowserConfig(
        headless=False,
        disable_security=False,
    )

    agent = Agent(
        task="""
        執行登出驗證流程：
        1. 先登錄到網站
        2. 確認登錄成功
        3. 找到登出按鈕或選項
        4. 執行登出操作
        5. 確認跳轉到登出後的頁面
        6. 檢查 Cookie 是否被清除
        7. 嘗試訪問需要登錄的頁面
        8. 確認是否被重定向到登錄頁面
        9. 報告完整的登出驗證結果
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n開始登出驗證...")
        result = await agent.run()

        print(f"\n✓ 登出驗證完成！")
        print(f"\n驗證結果：\n{result}")

    except Exception as e:
        print(f"\n✗ 驗證失敗: {str(e)}")


async def secure_login_best_practices():
    """
    安全登錄最佳實踐範例

    演示安全的登錄操作實踐。
    """
    print("\n" + "="*60)
    print("範例 9: 安全登錄最佳實踐")
    print("="*60)

    # 從環境變數讀取憑證
    username = os.getenv("DEMO_USERNAME", "demo_user")
    password = os.getenv("DEMO_PASSWORD", "demo_password")

    print("\n安全提示：")
    print("- 憑證已從環境變數讀取")
    print("- 不在代碼中硬編碼敏感資訊")
    print("- 使用加密連接（HTTPS）")
    print("- 避免在日誌中記錄密碼")

    browser_config = BrowserConfig(
        headless=True,  # 使用無頭模式提高安全性
        disable_security=False,
    )

    agent = Agent(
        task=f"""
        執行安全登錄流程：
        1. 確認使用 HTTPS 連接
        2. 檢查登錄頁面的安全性（SSL 證書）
        3. 使用環境變數中的憑證登錄
        4. 不在頁面上顯示密碼
        5. 檢查是否有安全警告
        6. 驗證登錄後的會話安全性
        7. 生成安全性檢查報告

        注意：這是演示用憑證，僅用於測試
        """,
        llm_model="gpt-4",
        browser_config=browser_config,
    )

    try:
        print("\n執行安全登錄檢查...")
        result = await agent.run()

        print(f"\n✓ 安全檢查完成！")
        print(f"\n檢查報告：\n{result}")

    except Exception as e:
        print(f"\n✗ 檢查失敗: {str(e)}")


def print_login_security_tips():
    """
    打印登錄安全提示和最佳實踐
    """
    print("\n" + "="*60)
    print("登錄操作安全最佳實踐")
    print("="*60)

    tips = [
        "1. 憑證管理：",
        "   - 使用環境變數存儲憑證",
        "   - 不在代碼中硬編碼密碼",
        "   - 使用密鑰管理服務（如 AWS Secrets Manager）",
        "   - 定期輪換憑證",
        "",
        "2. 連接安全：",
        "   - 始終使用 HTTPS",
        "   - 驗證 SSL 證書",
        "   - 避免在不安全的網路上登錄",
        "   - 使用 VPN 保護連接",
        "",
        "3. 會話管理：",
        "   - 設置適當的會話超時",
        "   - 使用安全的 Cookie 設置",
        "   - 實施 CSRF 防護",
        "   - 在登出時清除所有會話數據",
        "",
        "4. 日誌記錄：",
        "   - 不在日誌中記錄密碼",
        "   - 記錄登錄嘗試（成功和失敗）",
        "   - 監控異常登錄活動",
        "   - 實施審計追蹤",
        "",
        "5. 錯誤處理：",
        "   - 不洩露具體的錯誤原因",
        "   - 使用通用錯誤訊息",
        "   - 實施登錄嘗試限制",
        "   - 防止暴力破解攻擊",
        "",
        "6. 多因素認證：",
        "   - 啟用 2FA/MFA",
        "   - 使用時間基礎的一次性密碼（TOTP）",
        "   - 支援生物識別認證",
        "   - 提供備份驗證方式",
        "",
        "7. 法律和合規：",
        "   - 遵守網站的服務條款",
        "   - 不進行未授權的訪問",
        "   - 遵守數據保護法規（GDPR、CCPA 等）",
        "   - 獲得適當的授權",
        "",
        "8. 測試環境：",
        "   - 使用測試帳號進行開發",
        "   - 不在生產環境測試",
        "   - 隔離開發和生產憑證",
        "   - 定期清理測試數據",
    ]

    for tip in tips:
        print(tip)

    print("="*60)


async def main():
    """
    主函數 - 運行所有登錄操作範例
    """
    print("\n" + "="*60)
    print("Browser-Use 登錄操作範例集")
    print("="*60)

    # 檢查 API 金鑰
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠ 請設置 OPENAI_API_KEY 環境變數")
        return

    examples = [
        ("基本登錄操作", basic_login_example),
        ("帶驗證的登錄", login_with_validation_example),
        ("記住我功能", remember_me_example),
        ("會話管理", session_management_example),
        ("自動重新登錄", auto_relogin_example),
        ("多帳號登錄管理", multi_account_login_example),
        ("社交登錄流程", social_login_simulation),
        ("登出驗證", logout_verification_example),
        ("安全登錄最佳實踐", secure_login_best_practices),
    ]

    print("\n可用的登錄操作範例：")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i:2d}. {name}")

    print("\n" + "-"*60)
    user_input = input("\n請選擇要運行的範例編號（1-9），或按 Enter 查看安全提示：")

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
        print_login_security_tips()

    print("\n" + "="*60)
    print("登錄操作範例演示完成！")
    print("="*60)
    print("\n重要提醒：")
    print("- 不要在代碼中硬編碼真實憑證")
    print("- 使用環境變數管理敏感資訊")
    print("- 遵守網站的服務條款")
    print("- 實施適當的安全措施")
    print("="*60 + "\n")


if __name__ == "__main__":
    """
    運行登錄操作範例

    使用方式：
    1. 設置環境變數：
       export OPENAI_API_KEY='your-key'
       export DEMO_USERNAME='your-username'  # 可選
       export DEMO_PASSWORD='your-password'  # 可選

    2. 運行程式：
       python 06_登錄操作.py
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n程式已被用戶中斷。")
    except Exception as e:
        print(f"\n發生錯誤：{str(e)}")
        import traceback
        traceback.print_exc()
