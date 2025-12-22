"""
WebSurfer - 網頁瀏覽 Agent
===================================

WebSurfer 是 Magentic-One 的網頁瀏覽專家，負責：
1. 網頁導航和搜索
2. 信息提取和解析
3. 表單填寫和交互
4. 頁面截圖和內容保存
5. 動態內容處理

技術特點：
- 基於 Playwright 的瀏覽器控制
- 支持 JavaScript 渲染
- 智能等待和元素定位
- 多標籤頁管理
- Cookie 和會話管理
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re


class WebSurferAgent:
    """
    網頁瀏覽 Agent

    使用瀏覽器自動化技術完成網頁相關任務
    """

    def __init__(
        self,
        llm_config: Dict[str, Any],
        headless: bool = True,
        viewport: Dict[str, int] = None,
        timeout: int = 30000
    ):
        """
        初始化 WebSurfer

        Args:
            llm_config: LLM 配置
            headless: 是否無頭模式
            viewport: 視窗大小
            timeout: 超時時間（毫秒）
        """
        self.llm_config = llm_config
        self.headless = headless
        self.viewport = viewport or {"width": 1280, "height": 720}
        self.timeout = timeout

        # 瀏覽器狀態
        self.browser = None
        self.current_page = None
        self.tabs: List[Any] = []

        # 歷史記錄
        self.navigation_history: List[Dict] = []
        self.extracted_data: List[Dict] = []

        # 統計
        self.stats = {
            'pages_visited': 0,
            'forms_submitted': 0,
            'screenshots_taken': 0,
            'data_extracted': 0
        }

    def navigate(self, url: str, wait_for: str = "load") -> Dict[str, Any]:
        """
        導航到指定 URL

        Args:
            url: 目標 URL
            wait_for: 等待條件 (load/domcontentloaded/networkidle)

        Returns:
            導航結果
        """
        print(f"\n🌐 導航到: {url}")

        try:
            # 模擬導航（實際應使用 Playwright）
            navigation_info = {
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'wait_for': wait_for,
                'status': 'success'
            }

            self.navigation_history.append(navigation_info)
            self.stats['pages_visited'] += 1

            # 模擬頁面加載
            page_content = self._load_page(url)

            print(f"✓ 頁面加載成功")
            print(f"  標題: {page_content['title']}")
            print(f"  URL: {page_content['url']}")

            return {
                'success': True,
                'page': page_content,
                'navigation_info': navigation_info
            }

        except Exception as e:
            print(f"✗ 導航失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def search(self, query: str, engine: str = "google") -> Dict[str, Any]:
        """
        執行網頁搜索

        Args:
            query: 搜索查詢
            engine: 搜索引擎 (google/bing/duckduckgo)

        Returns:
            搜索結果
        """
        print(f"\n🔍 搜索: '{query}' (引擎: {engine})")

        # 構建搜索 URL
        search_urls = {
            'google': f'https://www.google.com/search?q={query}',
            'bing': f'https://www.bing.com/search?q={query}',
            'duckduckgo': f'https://duckduckgo.com/?q={query}'
        }

        url = search_urls.get(engine, search_urls['google'])

        # 導航到搜索頁面
        nav_result = self.navigate(url)

        if not nav_result['success']:
            return nav_result

        # 提取搜索結果
        results = self._extract_search_results(nav_result['page'])

        print(f"✓ 找到 {len(results)} 個結果")

        return {
            'success': True,
            'query': query,
            'engine': engine,
            'results': results,
            'total_results': len(results)
        }

    def extract_content(
        self,
        selectors: Dict[str, str],
        extract_links: bool = False
    ) -> Dict[str, Any]:
        """
        提取頁面內容

        Args:
            selectors: CSS 選擇器字典 {key: selector}
            extract_links: 是否提取連結

        Returns:
            提取的內容
        """
        print(f"\n📄 提取頁面內容")

        if not self.current_page:
            return {'success': False, 'error': '沒有打開的頁面'}

        extracted = {}

        # 使用選擇器提取內容
        for key, selector in selectors.items():
            print(f"  提取 '{key}' (選擇器: {selector})")
            content = self._extract_by_selector(selector)
            extracted[key] = content

        # 提取連結
        if extract_links:
            links = self._extract_links()
            extracted['links'] = links
            print(f"  提取了 {len(links)} 個連結")

        self.extracted_data.append({
            'timestamp': datetime.now().isoformat(),
            'data': extracted
        })
        self.stats['data_extracted'] += 1

        return {
            'success': True,
            'data': extracted
        }

    def fill_form(self, form_data: Dict[str, str], submit: bool = True) -> Dict[str, Any]:
        """
        填寫表單

        Args:
            form_data: 表單數據 {field_name: value}
            submit: 是否提交

        Returns:
            操作結果
        """
        print(f"\n📝 填寫表單")

        try:
            # 填寫每個欄位
            for field, value in form_data.items():
                print(f"  填寫 '{field}': {value}")
                self._fill_field(field, value)

            # 提交表單
            if submit:
                print(f"  提交表單...")
                self._submit_form()
                self.stats['forms_submitted'] += 1

            return {
                'success': True,
                'fields_filled': len(form_data),
                'submitted': submit
            }

        except Exception as e:
            print(f"✗ 表單填寫失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def take_screenshot(self, filename: str, full_page: bool = False) -> Dict[str, Any]:
        """
        截取頁面截圖

        Args:
            filename: 保存文件名
            full_page: 是否截取整頁

        Returns:
            操作結果
        """
        print(f"\n📸 截取截圖: {filename}")

        try:
            # 模擬截圖
            screenshot_info = {
                'filename': filename,
                'full_page': full_page,
                'timestamp': datetime.now().isoformat(),
                'viewport': self.viewport
            }

            self.stats['screenshots_taken'] += 1

            print(f"✓ 截圖已保存")

            return {
                'success': True,
                'screenshot': screenshot_info
            }

        except Exception as e:
            print(f"✗ 截圖失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def click_element(self, selector: str, wait_navigation: bool = False) -> Dict[str, Any]:
        """
        點擊元素

        Args:
            selector: 元素選擇器
            wait_navigation: 是否等待導航

        Returns:
            操作結果
        """
        print(f"\n👆 點擊元素: {selector}")

        try:
            # 模擬點擊
            click_info = {
                'selector': selector,
                'wait_navigation': wait_navigation,
                'timestamp': datetime.now().isoformat()
            }

            print(f"✓ 元素已點擊")

            return {
                'success': True,
                'click_info': click_info
            }

        except Exception as e:
            print(f"✗ 點擊失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def scroll_page(self, direction: str = "down", distance: int = 500) -> Dict[str, Any]:
        """
        滾動頁面

        Args:
            direction: 方向 (up/down/left/right)
            distance: 距離（像素）

        Returns:
            操作結果
        """
        print(f"\n⬇️ 滾動頁面: {direction} {distance}px")

        scroll_commands = {
            'down': f'window.scrollBy(0, {distance})',
            'up': f'window.scrollBy(0, -{distance})',
            'right': f'window.scrollBy({distance}, 0)',
            'left': f'window.scrollBy(-{distance}, 0)'
        }

        command = scroll_commands.get(direction)

        return {
            'success': True,
            'direction': direction,
            'distance': distance
        }

    def wait_for_element(self, selector: str, timeout: int = None) -> Dict[str, Any]:
        """
        等待元素出現

        Args:
            selector: 元素選擇器
            timeout: 超時時間（毫秒）

        Returns:
            等待結果
        """
        timeout = timeout or self.timeout
        print(f"\n⏳ 等待元素: {selector} (超時: {timeout}ms)")

        try:
            # 模擬等待
            print(f"✓ 元素已出現")

            return {
                'success': True,
                'selector': selector,
                'found': True
            }

        except Exception as e:
            print(f"✗ 等待超時: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def execute_javascript(self, script: str) -> Dict[str, Any]:
        """
        執行 JavaScript 代碼

        Args:
            script: JavaScript 代碼

        Returns:
            執行結果
        """
        print(f"\n💻 執行 JavaScript")
        print(f"  代碼: {script[:100]}...")

        try:
            # 模擬執行
            result = "執行成功"

            return {
                'success': True,
                'result': result
            }

        except Exception as e:
            print(f"✗ 執行失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_cookies(self) -> List[Dict]:
        """獲取 Cookies"""
        print("\n🍪 獲取 Cookies")

        cookies = [
            {'name': 'session_id', 'value': 'abc123', 'domain': '.example.com'},
            {'name': 'user_pref', 'value': 'dark_mode', 'domain': '.example.com'}
        ]

        print(f"✓ 獲取了 {len(cookies)} 個 Cookie")

        return cookies

    def set_cookies(self, cookies: List[Dict]) -> Dict[str, Any]:
        """設置 Cookies"""
        print(f"\n🍪 設置 {len(cookies)} 個 Cookie")

        return {
            'success': True,
            'cookies_set': len(cookies)
        }

    # 內部輔助方法

    def _load_page(self, url: str) -> Dict[str, Any]:
        """模擬加載頁面"""
        return {
            'url': url,
            'title': f'頁面: {url}',
            'content': f'這是 {url} 的內容',
            'status': 200
        }

    def _extract_search_results(self, page: Dict) -> List[Dict]:
        """提取搜索結果"""
        # 模擬搜索結果
        return [
            {
                'title': '結果 1',
                'url': 'https://example.com/1',
                'snippet': '這是第一個搜索結果的摘要'
            },
            {
                'title': '結果 2',
                'url': 'https://example.com/2',
                'snippet': '這是第二個搜索結果的摘要'
            },
            {
                'title': '結果 3',
                'url': 'https://example.com/3',
                'snippet': '這是第三個搜索結果的摘要'
            }
        ]

    def _extract_by_selector(self, selector: str) -> str:
        """根據選擇器提取內容"""
        return f"通過選擇器 '{selector}' 提取的內容"

    def _extract_links(self) -> List[Dict]:
        """提取頁面連結"""
        return [
            {'text': '連結 1', 'href': 'https://example.com/link1'},
            {'text': '連結 2', 'href': 'https://example.com/link2'}
        ]

    def _fill_field(self, field: str, value: str):
        """填寫表單欄位"""
        pass

    def _submit_form(self):
        """提交表單"""
        pass

    def get_statistics(self) -> Dict[str, Any]:
        """獲取統計數據"""
        return {
            'pages_visited': self.stats['pages_visited'],
            'forms_submitted': self.stats['forms_submitted'],
            'screenshots_taken': self.stats['screenshots_taken'],
            'data_extracted': self.stats['data_extracted'],
            'navigation_history_length': len(self.navigation_history)
        }


def demo_web_navigation():
    """網頁導航示範"""
    print("=" * 60)
    print("範例 1: 網頁導航")
    print("=" * 60)

    web_surfer = WebSurferAgent(
        llm_config={"model": "gpt-4"},
        headless=True
    )

    # 訪問網頁
    result = web_surfer.navigate("https://www.python.org")

    print("\n導航結果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


def demo_web_search():
    """網頁搜索示範"""
    print("\n" + "=" * 60)
    print("範例 2: 網頁搜索")
    print("=" * 60)

    web_surfer = WebSurferAgent(llm_config={"model": "gpt-4"})

    # 執行搜索
    result = web_surfer.search("Python 最佳實踐", engine="google")

    print("\n搜索結果:")
    for i, item in enumerate(result['results'], 1):
        print(f"\n{i}. {item['title']}")
        print(f"   URL: {item['url']}")
        print(f"   摘要: {item['snippet']}")


def demo_content_extraction():
    """內容提取示範"""
    print("\n" + "=" * 60)
    print("範例 3: 內容提取")
    print("=" * 60)

    web_surfer = WebSurferAgent(llm_config={"model": "gpt-4"})

    # 導航到頁面
    web_surfer.navigate("https://example.com")

    # 提取內容
    selectors = {
        'title': 'h1',
        'description': '.description',
        'main_content': '#content'
    }

    result = web_surfer.extract_content(selectors, extract_links=True)

    print("\n提取的內容:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


def demo_form_interaction():
    """表單交互示範"""
    print("\n" + "=" * 60)
    print("範例 4: 表單填寫")
    print("=" * 60)

    web_surfer = WebSurferAgent(llm_config={"model": "gpt-4"})

    # 導航到表單頁面
    web_surfer.navigate("https://example.com/contact")

    # 填寫表單
    form_data = {
        'name': '張三',
        'email': 'zhangsan@example.com',
        'message': '這是一個測試消息'
    }

    result = web_surfer.fill_form(form_data, submit=True)

    print("\n表單提交結果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


def demo_advanced_interactions():
    """高級交互示範"""
    print("\n" + "=" * 60)
    print("範例 5: 高級網頁交互")
    print("=" * 60)

    web_surfer = WebSurferAgent(llm_config={"model": "gpt-4"})

    # 導航
    web_surfer.navigate("https://example.com")

    # 點擊元素
    web_surfer.click_element("#menu-button")

    # 等待元素
    web_surfer.wait_for_element(".dropdown-menu")

    # 滾動頁面
    web_surfer.scroll_page("down", 1000)

    # 執行 JavaScript
    web_surfer.execute_javascript("document.querySelector('h1').style.color = 'red'")

    # 截圖
    web_surfer.take_screenshot("example_screenshot.png", full_page=True)

    # 獲取統計
    stats = web_surfer.get_statistics()

    print("\n統計數據:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))


def demo_cookie_management():
    """Cookie 管理示範"""
    print("\n" + "=" * 60)
    print("範例 6: Cookie 管理")
    print("=" * 60)

    web_surfer = WebSurferAgent(llm_config={"model": "gpt-4"})

    # 導航到頁面
    web_surfer.navigate("https://example.com")

    # 獲取 Cookies
    cookies = web_surfer.get_cookies()
    print(f"\n當前 Cookies:")
    for cookie in cookies:
        print(f"  {cookie['name']}: {cookie['value']}")

    # 設置新的 Cookies
    new_cookies = [
        {'name': 'custom_cookie', 'value': 'custom_value', 'domain': '.example.com'}
    ]
    web_surfer.set_cookies(new_cookies)


if __name__ == "__main__":
    demo_web_navigation()
    demo_web_search()
    demo_content_extraction()
    demo_form_interaction()
    demo_advanced_interactions()
    demo_cookie_management()

    print("\n" + "=" * 60)
    print("WebSurfer 示範完成！")
    print("=" * 60)
