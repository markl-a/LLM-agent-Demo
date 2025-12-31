"""
Browserbase 快速開始示例
======================

本模塊展示了如何快速開始使用 Browserbase 進行瀏覽器自動化。
包括基礎連接、簡單操作和常見配置。

主要內容:
1. Browserbase 客戶端初始化
2. 創建和管理瀏覽器 Session
3. 使用 Playwright 連接遠程瀏覽器
4. 基本的頁面操作（導航、點擊、輸入）
5. 錯誤處理和資源清理

作者: Browserbase 示例團隊
日期: 2025-12-31
"""

import os
import sys
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv

try:
    from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext
except ImportError:
    print("請先安裝 playwright: pip install playwright")
    print("然後運行: playwright install chromium")
    sys.exit(1)


# 加載環境變量
load_dotenv()


@dataclass
class BrowserbaseConfig:
    """Browserbase 配置類"""
    api_key: str
    project_id: str
    base_url: str = "https://api.browserbase.com"
    timeout: int = 30000  # 30秒超時
    headless: bool = True
    stealth: bool = True


class BrowserbaseClient:
    """
    Browserbase 客戶端類

    提供了與 Browserbase API 交互的高級接口，
    簡化了 Session 創建、管理和清理流程。
    """

    def __init__(self, config: BrowserbaseConfig):
        """
        初始化 Browserbase 客戶端

        Args:
            config: Browserbase 配置對象
        """
        self.config = config
        self.active_sessions = []
        print(f"[{self._timestamp()}] Browserbase 客戶端初始化成功")

    def _timestamp(self) -> str:
        """獲取當前時間戳"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def create_session(
        self,
        stealth: Optional[bool] = None,
        proxy: bool = False,
        keep_alive: bool = False
    ) -> Dict[str, Any]:
        """
        創建新的瀏覽器 Session

        Args:
            stealth: 是否啟用隱身模式（默認使用配置值）
            proxy: 是否使用代理
            keep_alive: Session 是否持久化

        Returns:
            Session 信息字典
        """
        print(f"[{self._timestamp()}] 正在創建瀏覽器 Session...")

        # 模擬 API 調用（實際使用時需要真實的 API 集成）
        session_data = {
            "id": f"session_{int(time.time())}",
            "project_id": self.config.project_id,
            "status": "running",
            "stealth": stealth if stealth is not None else self.config.stealth,
            "proxy": proxy,
            "keep_alive": keep_alive,
            "connect_url": "ws://localhost:9222/devtools/browser/mock",
            "created_at": self._timestamp()
        }

        self.active_sessions.append(session_data)
        print(f"[{self._timestamp()}] Session 創建成功: {session_data['id']}")

        return session_data

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        獲取 Session 信息

        Args:
            session_id: Session ID

        Returns:
            Session 信息字典，如果不存在則返回 None
        """
        for session in self.active_sessions:
            if session["id"] == session_id:
                return session
        return None

    def delete_session(self, session_id: str) -> bool:
        """
        刪除 Session

        Args:
            session_id: Session ID

        Returns:
            是否成功刪除
        """
        print(f"[{self._timestamp()}] 正在刪除 Session: {session_id}")

        for i, session in enumerate(self.active_sessions):
            if session["id"] == session_id:
                self.active_sessions.pop(i)
                print(f"[{self._timestamp()}] Session 已刪除")
                return True

        print(f"[{self._timestamp()}] Session 不存在")
        return False

    def cleanup_all_sessions(self):
        """清理所有活躍的 Session"""
        print(f"[{self._timestamp()}] 正在清理所有 Session...")
        count = len(self.active_sessions)
        self.active_sessions.clear()
        print(f"[{self._timestamp()}] 已清理 {count} 個 Session")


class SimpleBrowser:
    """
    簡單的瀏覽器操作封裝類

    提供了常見的瀏覽器操作方法，簡化 Playwright API 的使用。
    """

    def __init__(self, page: Page):
        """
        初始化簡單瀏覽器

        Args:
            page: Playwright Page 對象
        """
        self.page = page

    def navigate(self, url: str, wait_until: str = "load") -> None:
        """
        導航到指定 URL

        Args:
            url: 目標 URL
            wait_until: 等待條件 (load, domcontentloaded, networkidle)
        """
        print(f"正在訪問: {url}")
        self.page.goto(url, wait_until=wait_until)
        print(f"頁面加載完成: {self.page.title()}")

    def click_element(self, selector: str, timeout: int = 5000) -> None:
        """
        點擊元素

        Args:
            selector: CSS 選擇器
            timeout: 超時時間（毫秒）
        """
        print(f"點擊元素: {selector}")
        self.page.click(selector, timeout=timeout)

    def type_text(self, selector: str, text: str, delay: int = 50) -> None:
        """
        在輸入框中輸入文本

        Args:
            selector: CSS 選擇器
            text: 要輸入的文本
            delay: 每個字符的延遲（毫秒）
        """
        print(f"在 {selector} 中輸入: {text}")
        self.page.type(selector, text, delay=delay)

    def get_text(self, selector: str) -> str:
        """
        獲取元素文本

        Args:
            selector: CSS 選擇器

        Returns:
            元素的文本內容
        """
        return self.page.inner_text(selector)

    def wait_for_element(self, selector: str, timeout: int = 5000) -> None:
        """
        等待元素出現

        Args:
            selector: CSS 選擇器
            timeout: 超時時間（毫秒）
        """
        print(f"等待元素: {selector}")
        self.page.wait_for_selector(selector, timeout=timeout)

    def screenshot(self, path: str, full_page: bool = False) -> None:
        """
        截取頁面截圖

        Args:
            path: 保存路徑
            full_page: 是否截取整個頁面
        """
        print(f"截圖保存至: {path}")
        self.page.screenshot(path=path, full_page=full_page)


def example_basic_usage():
    """示例1: 基礎使用流程"""
    print("\n" + "=" * 60)
    print("示例1: 基礎使用流程")
    print("=" * 60 + "\n")

    # 1. 配置 Browserbase
    config = BrowserbaseConfig(
        api_key=os.getenv("BROWSERBASE_API_KEY", "demo_api_key"),
        project_id=os.getenv("BROWSERBASE_PROJECT_ID", "demo_project"),
        stealth=True
    )

    # 2. 創建客戶端
    client = BrowserbaseClient(config)

    # 3. 創建 Session
    session = client.create_session()

    print(f"Session ID: {session['id']}")
    print(f"隱身模式: {session['stealth']}")
    print(f"創建時間: {session['created_at']}")

    # 4. 清理 Session
    client.delete_session(session["id"])


def example_playwright_integration():
    """示例2: Playwright 集成"""
    print("\n" + "=" * 60)
    print("示例2: Playwright 集成")
    print("=" * 60 + "\n")

    config = BrowserbaseConfig(
        api_key=os.getenv("BROWSERBASE_API_KEY", "demo_api_key"),
        project_id=os.getenv("BROWSERBASE_PROJECT_ID", "demo_project")
    )

    client = BrowserbaseClient(config)
    session = client.create_session()

    # 注意: 這是演示代碼，實際使用時需要真實的連接 URL
    print("演示 Playwright 集成流程:")
    print("1. 使用 sync_playwright() 創建 playwright 實例")
    print("2. 使用 chromium.connect_over_cdp() 連接遠程瀏覽器")
    print("3. 創建新頁面並執行操作")
    print("4. 關閉瀏覽器和清理資源")

    # 實際代碼示例（需要真實環境）:
    # with sync_playwright() as p:
    #     browser = p.chromium.connect_over_cdp(session['connect_url'])
    #     page = browser.new_page()
    #     page.goto('https://example.com')
    #     print(f"頁面標題: {page.title()}")
    #     browser.close()

    client.delete_session(session["id"])


def example_simple_browser_wrapper():
    """示例3: 使用簡單瀏覽器封裝"""
    print("\n" + "=" * 60)
    print("示例3: 使用簡單瀏覽器封裝")
    print("=" * 60 + "\n")

    print("SimpleBrowser 類提供了以下便捷方法:")
    print("- navigate(url): 導航到 URL")
    print("- click_element(selector): 點擊元素")
    print("- type_text(selector, text): 輸入文本")
    print("- get_text(selector): 獲取文本")
    print("- wait_for_element(selector): 等待元素")
    print("- screenshot(path): 截圖")

    # 實際使用示例（需要真實 Page 對象）:
    # simple_browser = SimpleBrowser(page)
    # simple_browser.navigate('https://example.com')
    # simple_browser.click_element('#button')
    # simple_browser.screenshot('screenshot.png')


def example_error_handling():
    """示例4: 錯誤處理"""
    print("\n" + "=" * 60)
    print("示例4: 錯誤處理")
    print("=" * 60 + "\n")

    config = BrowserbaseConfig(
        api_key=os.getenv("BROWSERBASE_API_KEY", "demo_api_key"),
        project_id=os.getenv("BROWSERBASE_PROJECT_ID", "demo_project")
    )

    client = BrowserbaseClient(config)

    try:
        # 創建 Session
        session = client.create_session()

        # 模擬操作
        print("執行瀏覽器操作...")

        # 模擬可能的錯誤
        if False:  # 這裡設為 False 以避免真實錯誤
            raise Exception("模擬錯誤")

        print("操作完成")

    except Exception as e:
        print(f"發生錯誤: {str(e)}")
        print("正在進行錯誤處理...")

    finally:
        # 確保清理資源
        print("清理資源...")
        client.cleanup_all_sessions()


def example_multiple_sessions():
    """示例5: 管理多個 Session"""
    print("\n" + "=" * 60)
    print("示例5: 管理多個 Session")
    print("=" * 60 + "\n")

    config = BrowserbaseConfig(
        api_key=os.getenv("BROWSERBASE_API_KEY", "demo_api_key"),
        project_id=os.getenv("BROWSERBASE_PROJECT_ID", "demo_project")
    )

    client = BrowserbaseClient(config)

    # 創建多個 Session
    sessions = []
    for i in range(3):
        session = client.create_session()
        sessions.append(session)
        print(f"Session {i + 1}: {session['id']}")

    print(f"\n當前活躍 Session 數量: {len(client.active_sessions)}")

    # 查詢特定 Session
    session_info = client.get_session(sessions[0]["id"])
    if session_info:
        print(f"\n查詢到 Session: {session_info['id']}")
        print(f"狀態: {session_info['status']}")

    # 清理所有 Session
    client.cleanup_all_sessions()
    print(f"清理後活躍 Session 數量: {len(client.active_sessions)}")


def example_configuration_options():
    """示例6: 配置選項"""
    print("\n" + "=" * 60)
    print("示例6: 配置選項")
    print("=" * 60 + "\n")

    # 基礎配置
    basic_config = BrowserbaseConfig(
        api_key="demo_api_key",
        project_id="demo_project"
    )
    print("基礎配置:")
    print(f"  - API Key: {basic_config.api_key}")
    print(f"  - Project ID: {basic_config.project_id}")
    print(f"  - 隱身模式: {basic_config.stealth}")
    print(f"  - 超時: {basic_config.timeout}ms")

    # 自定義配置
    custom_config = BrowserbaseConfig(
        api_key="demo_api_key",
        project_id="demo_project",
        timeout=60000,  # 60秒
        stealth=False,
        headless=False
    )
    print("\n自定義配置:")
    print(f"  - 超時: {custom_config.timeout}ms")
    print(f"  - 隱身模式: {custom_config.stealth}")
    print(f"  - 無頭模式: {custom_config.headless}")


def main():
    """主函數：運行所有示例"""
    print("\n" + "=" * 60)
    print("Browserbase 快速開始示例")
    print("=" * 60)

    # 檢查環境變量
    if not os.getenv("BROWSERBASE_API_KEY"):
        print("\n⚠️  警告: 未設置 BROWSERBASE_API_KEY 環境變量")
        print("請在 .env 文件中設置或使用以下命令:")
        print("export BROWSERBASE_API_KEY='your_api_key'")

    # 運行所有示例
    example_basic_usage()
    example_playwright_integration()
    example_simple_browser_wrapper()
    example_error_handling()
    example_multiple_sessions()
    example_configuration_options()

    print("\n" + "=" * 60)
    print("所有示例運行完成！")
    print("=" * 60 + "\n")

    print("下一步:")
    print("1. 查看 02_Session管理.py 學習 Session 高級管理")
    print("2. 查看 03_隱身瀏覽.py 學習反檢測技術")
    print("3. 訪問 https://docs.browserbase.com 查看完整文檔")


if __name__ == "__main__":
    main()
