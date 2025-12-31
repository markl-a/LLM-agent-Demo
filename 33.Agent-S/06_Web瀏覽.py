"""
Agent-S Web 瀏覽模組

此模組展示 Agent-S 的網頁瀏覽和操作能力：
1. 網頁導航 - 打開瀏覽器並訪問網站
2. 元素定位 - 通過視覺和語義定位網頁元素
3. 交互操作 - 點擊、輸入、滾動等操作
4. 信息提取 - 從網頁提取結構化信息

Agent-S 使用計算機視覺和 DOM 分析來理解和操作網頁。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
import time
from datetime import datetime


class BrowserType(Enum):
    """瀏覽器類型"""
    CHROME = "Chrome"
    FIREFOX = "Firefox"
    SAFARI = "Safari"
    EDGE = "Edge"


class ElementType(Enum):
    """網頁元素類型"""
    BUTTON = "按鈕"
    INPUT = "輸入框"
    LINK = "鏈接"
    IMAGE = "圖片"
    TEXT = "文本"
    DROPDOWN = "下拉菜單"
    CHECKBOX = "複選框"
    RADIO = "單選框"


@dataclass
class WebElement:
    """網頁元素"""
    element_id: str
    element_type: ElementType
    text: Optional[str] = None
    tag: Optional[str] = None
    attributes: Dict[str, str] = field(default_factory=dict)
    position: Tuple[int, int] = (0, 0)  # (x, y)
    size: Tuple[int, int] = (0, 0)  # (width, height)
    visible: bool = True

    def __str__(self):
        return f"{self.element_type.value} '{self.text or self.element_id}' at {self.position}"


@dataclass
class WebPage:
    """網頁信息"""
    url: str
    title: str
    elements: List[WebElement] = field(default_factory=list)
    loaded_at: datetime = field(default_factory=datetime.now)
    scroll_position: int = 0
    viewport_size: Tuple[int, int] = (1920, 1080)

    def find_element_by_text(self, text: str) -> Optional[WebElement]:
        """通過文本查找元素"""
        for element in self.elements:
            if element.text and text.lower() in element.text.lower():
                return element
        return None

    def find_elements_by_type(self, element_type: ElementType) -> List[WebElement]:
        """通過類型查找元素"""
        return [e for e in self.elements if e.element_type == element_type]


class Browser:
    """
    瀏覽器控制器

    模擬瀏覽器操作
    """

    def __init__(self, browser_type: BrowserType = BrowserType.CHROME):
        self.browser_type = browser_type
        self.current_page: Optional[WebPage] = None
        self.history: List[str] = []
        self.is_open = False

    def launch(self) -> bool:
        """啟動瀏覽器"""
        print(f"\n啟動 {self.browser_type.value} 瀏覽器...")
        time.sleep(0.5)  # 模擬啟動時間
        self.is_open = True
        print("瀏覽器已啟動 ✓")
        return True

    def navigate(self, url: str) -> WebPage:
        """導航到 URL"""
        if not self.is_open:
            self.launch()

        print(f"\n導航到: {url}")
        time.sleep(0.3)  # 模擬加載時間

        # 模擬頁面加載
        page = self._load_page(url)
        self.current_page = page
        self.history.append(url)

        print(f"頁面加載完成: {page.title}")
        print(f"發現 {len(page.elements)} 個元素")

        return page

    def _load_page(self, url: str) -> WebPage:
        """模擬加載頁面"""
        # 根據 URL 生成模擬頁面
        if "search" in url or "google" in url:
            return self._create_search_page(url)
        elif "shop" in url or "store" in url:
            return self._create_shop_page(url)
        elif "news" in url:
            return self._create_news_page(url)
        else:
            return self._create_generic_page(url)

    def _create_search_page(self, url: str) -> WebPage:
        """創建搜索頁面"""
        return WebPage(
            url=url,
            title="搜索引擎",
            elements=[
                WebElement("search_box", ElementType.INPUT, "搜索", "input",
                          {"placeholder": "輸入搜索關鍵詞"}, (500, 300), (400, 50)),
                WebElement("search_btn", ElementType.BUTTON, "搜索", "button",
                          {}, (910, 300), (80, 50)),
                WebElement("result_1", ElementType.LINK, "第一個搜索結果", "a",
                          {"href": "/result1"}, (300, 400), (600, 30)),
                WebElement("result_2", ElementType.LINK, "第二個搜索結果", "a",
                          {"href": "/result2"}, (300, 450), (600, 30)),
            ]
        )

    def _create_shop_page(self, url: str) -> WebPage:
        """創建購物頁面"""
        return WebPage(
            url=url,
            title="在線商店",
            elements=[
                WebElement("search", ElementType.INPUT, "商品搜索", "input",
                          {}, (100, 50), (300, 40)),
                WebElement("product_1", ElementType.IMAGE, "商品圖片1", "img",
                          {"alt": "筆記本電腦"}, (100, 150), (200, 200)),
                WebElement("product_1_name", ElementType.TEXT, "高性能筆記本電腦", "div",
                          {}, (100, 360), (200, 30)),
                WebElement("add_to_cart_1", ElementType.BUTTON, "加入購物車", "button",
                          {}, (100, 400), (200, 40)),
                WebElement("product_2", ElementType.IMAGE, "商品圖片2", "img",
                          {"alt": "無線滑鼠"}, (350, 150), (200, 200)),
                WebElement("cart_icon", ElementType.BUTTON, "購物車 (0)", "button",
                          {}, (1700, 50), (150, 40)),
            ]
        )

    def _create_news_page(self, url: str) -> WebPage:
        """創建新聞頁面"""
        return WebPage(
            url=url,
            title="新聞網站",
            elements=[
                WebElement("headline", ElementType.LINK, "今日頭條新聞", "a",
                          {}, (200, 100), (1000, 60)),
                WebElement("article_1", ElementType.LINK, "科技新聞：AI 新突破", "a",
                          {}, (200, 200), (600, 40)),
                WebElement("article_2", ElementType.LINK, "經濟新聞：市場分析", "a",
                          {}, (200, 260), (600, 40)),
                WebElement("article_3", ElementType.LINK, "體育新聞：比賽結果", "a",
                          {}, (200, 320), (600, 40)),
            ]
        )

    def _create_generic_page(self, url: str) -> WebPage:
        """創建通用頁面"""
        return WebPage(
            url=url,
            title="網頁",
            elements=[
                WebElement("link_1", ElementType.LINK, "首頁", "a", {}, (100, 50), (100, 30)),
                WebElement("link_2", ElementType.LINK, "關於", "a", {}, (220, 50), (100, 30)),
                WebElement("content", ElementType.TEXT, "頁面內容", "div", {}, (100, 150), (800, 400)),
            ]
        )

    def close(self):
        """關閉瀏覽器"""
        print(f"\n關閉 {self.browser_type.value} 瀏覽器")
        self.is_open = False
        self.current_page = None


class WebNavigator:
    """
    網頁導航器

    提供高級網頁導航和操作功能
    """

    def __init__(self):
        self.browser = Browser()

    def click(self, element: WebElement) -> bool:
        """點擊元素"""
        print(f"\n點擊: {element}")
        time.sleep(0.2)

        # 模擬點擊效果
        if element.element_type == ElementType.LINK:
            print(f"  跳轉到: {element.attributes.get('href', '#')}")
        elif element.element_type == ElementType.BUTTON:
            print(f"  按鈕已激活")

        return True

    def input_text(self, element: WebElement, text: str) -> bool:
        """在輸入框中輸入文本"""
        if element.element_type != ElementType.INPUT:
            print(f"錯誤: {element} 不是輸入框")
            return False

        print(f"\n在 {element} 中輸入: '{text}'")
        time.sleep(0.1)
        return True

    def scroll(self, direction: str = "down", amount: int = 500) -> bool:
        """滾動頁面"""
        if not self.browser.current_page:
            return False

        print(f"\n向{direction}滾動 {amount}px")

        if direction == "down":
            self.browser.current_page.scroll_position += amount
        else:
            self.browser.current_page.scroll_position = max(0,
                self.browser.current_page.scroll_position - amount)

        print(f"當前滾動位置: {self.browser.current_page.scroll_position}px")
        return True

    def find_and_click(self, text: str) -> bool:
        """通過文本查找並點擊元素"""
        if not self.browser.current_page:
            print("錯誤: 沒有加載頁面")
            return False

        element = self.browser.current_page.find_element_by_text(text)

        if not element:
            print(f"未找到包含文本 '{text}' 的元素")
            return False

        return self.click(element)

    def extract_links(self) -> List[str]:
        """提取頁面中的所有鏈接"""
        if not self.browser.current_page:
            return []

        links = self.browser.current_page.find_elements_by_type(ElementType.LINK)
        link_texts = [link.text for link in links if link.text]

        print(f"\n提取到 {len(link_texts)} 個鏈接:")
        for i, text in enumerate(link_texts, 1):
            print(f"  {i}. {text}")

        return link_texts

    def extract_text(self) -> str:
        """提取頁面文本內容"""
        if not self.browser.current_page:
            return ""

        texts = []
        for element in self.browser.current_page.elements:
            if element.text and element.visible:
                texts.append(element.text)

        content = "\n".join(texts)
        print(f"\n提取到 {len(content)} 個字符的文本")

        return content


class WebAutomation:
    """
    Web 自動化任務執行器

    執行複雜的 Web 自動化任務
    """

    def __init__(self):
        self.navigator = WebNavigator()

    def search_web(self, query: str, search_engine: str = "https://google.com") -> List[str]:
        """執行 Web 搜索"""
        print("\n" + "="*60)
        print(f"執行搜索: {query}")
        print("="*60)

        # 打開搜索引擎
        self.navigator.browser.launch()
        page = self.navigator.browser.navigate(search_engine)

        # 找到搜索框並輸入
        search_box = page.find_elements_by_type(ElementType.INPUT)[0]
        self.navigator.input_text(search_box, query)

        # 點擊搜索按鈕
        search_btn = page.find_element_by_text("搜索")
        if search_btn:
            self.navigator.click(search_btn)

        # 等待結果加載（模擬）
        time.sleep(0.5)

        # 提取搜索結果
        results = self.navigator.extract_links()

        return results

    def online_shopping(self, product_name: str, store_url: str = "https://example-store.com") -> bool:
        """自動化在線購物流程"""
        print("\n" + "="*60)
        print(f"在線購物: {product_name}")
        print("="*60)

        try:
            # 訪問商店
            self.navigator.browser.launch()
            page = self.navigator.browser.navigate(store_url)

            # 搜索商品
            search_box = page.find_elements_by_type(ElementType.INPUT)[0]
            self.navigator.input_text(search_box, product_name)

            # 找到並點擊商品
            product = page.find_element_by_text(product_name)
            if not product:
                print(f"未找到商品: {product_name}")
                return False

            self.navigator.click(product)

            # 加入購物車
            add_to_cart = page.find_element_by_text("加入購物車")
            if add_to_cart:
                self.navigator.click(add_to_cart)
                print("\n✓ 商品已加入購物車")
                return True

        except Exception as e:
            print(f"購物過程出錯: {e}")
            return False

        return False

    def read_news(self, news_site: str = "https://news.example.com", count: int = 3) -> List[str]:
        """自動閱讀新聞"""
        print("\n" + "="*60)
        print(f"閱讀新聞 (前 {count} 篇)")
        print("="*60)

        articles = []

        # 訪問新聞網站
        self.navigator.browser.launch()
        page = self.navigator.browser.navigate(news_site)

        # 找到所有文章鏈接
        article_links = page.find_elements_by_type(ElementType.LINK)

        # 閱讀前幾篇
        for i, article in enumerate(article_links[:count], 1):
            print(f"\n閱讀第 {i} 篇: {article.text}")
            self.navigator.click(article)

            # 提取文章內容（模擬）
            time.sleep(0.3)
            content = f"{article.text} 的詳細內容..."
            articles.append(content)

            # 返回列表頁（模擬）
            self.navigator.browser.navigate(news_site)

        return articles

    def fill_form(self, form_url: str, form_data: Dict[str, str]) -> bool:
        """自動填寫表單"""
        print("\n" + "="*60)
        print("自動填寫表單")
        print("="*60)

        # 訪問表單頁面
        self.navigator.browser.launch()
        page = self.navigator.browser.navigate(form_url)

        # 模擬表單元素
        form_fields = [
            WebElement("name", ElementType.INPUT, "姓名", "input", {"name": "name"}),
            WebElement("email", ElementType.INPUT, "郵箱", "input", {"name": "email"}),
            WebElement("message", ElementType.INPUT, "留言", "textarea", {"name": "message"}),
        ]

        # 填寫每個字段
        for field in form_fields:
            field_name = field.attributes.get("name", "")
            if field_name in form_data:
                value = form_data[field_name]
                self.navigator.input_text(field, value)

        # 提交表單
        submit_btn = WebElement("submit", ElementType.BUTTON, "提交", "button")
        self.navigator.click(submit_btn)

        print("\n✓ 表單已提交")
        return True


def 示例1_基本瀏覽():
    """示例：基本網頁瀏覽"""
    print("\n" + "="*60)
    print("示例 1: 基本網頁瀏覽")
    print("="*60)

    navigator = WebNavigator()

    # 啟動瀏覽器
    navigator.browser.launch()

    # 訪問網站
    page = navigator.browser.navigate("https://example.com")

    # 查找並點擊鏈接
    navigator.find_and_click("首頁")

    # 提取內容
    text = navigator.extract_text()

    # 關閉瀏覽器
    navigator.browser.close()

    return page


def 示例2_搜索引擎():
    """示例：使用搜索引擎"""
    print("\n" + "="*60)
    print("示例 2: 使用搜索引擎")
    print("="*60)

    automation = WebAutomation()

    # 搜索
    results = automation.search_web("Agent-S 框架", "https://google.com/search")

    print(f"\n找到 {len(results)} 個結果")

    # 關閉
    automation.navigator.browser.close()

    return results


def 示例3_在線購物():
    """示例：自動化在線購物"""
    print("\n" + "="*60)
    print("示例 3: 自動化在線購物")
    print("="*60)

    automation = WebAutomation()

    # 購物
    success = automation.online_shopping(
        product_name="筆記本電腦",
        store_url="https://shop.example.com"
    )

    if success:
        print("\n購物流程完成！")
    else:
        print("\n購物失敗")

    # 關閉
    automation.navigator.browser.close()

    return success


def 示例4_閱讀新聞():
    """示例：自動閱讀新聞"""
    print("\n" + "="*60)
    print("示例 4: 自動閱讀新聞")
    print("="*60)

    automation = WebAutomation()

    # 閱讀新聞
    articles = automation.read_news("https://news.example.com", count=3)

    print(f"\n共閱讀 {len(articles)} 篇文章")

    # 關閉
    automation.navigator.browser.close()

    return articles


def 示例5_表單填寫():
    """示例：自動填寫表單"""
    print("\n" + "="*60)
    print("示例 5: 自動填寫表單")
    print("="*60)

    automation = WebAutomation()

    # 表單數據
    form_data = {
        "name": "張三",
        "email": "zhangsan@example.com",
        "message": "這是一條測試留言"
    }

    # 填寫表單
    success = automation.fill_form("https://example.com/contact", form_data)

    # 關閉
    automation.navigator.browser.close()

    return success


if __name__ == "__main__":
    print("Agent-S Web 瀏覽演示\n")

    示例1_基本瀏覽()
    示例2_搜索引擎()
    示例3_在線購物()
    示例4_閱讀新聞()
    示例5_表單填寫()

    print("\n所有示例執行完成！")
