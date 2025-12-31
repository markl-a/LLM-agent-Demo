"""
Agent S 螢幕操作指南
====================

本範例演示 Agent S 的螢幕捕獲和 UI 元素識別功能。
這是構建電腦使用 Agent 的基礎能力。

主要內容：
1. 螢幕截圖捕獲
2. UI 元素檢測
3. 元素定位和識別
4. 視覺理解和分析
"""

import os
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


# =============================================================================
# 1. UI 元素類型定義
# =============================================================================

class ElementType(Enum):
    """UI 元素類型枚舉"""
    BUTTON = "button"
    TEXT_FIELD = "text_field"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    DROPDOWN = "dropdown"
    MENU = "menu"
    MENU_ITEM = "menu_item"
    ICON = "icon"
    LINK = "link"
    IMAGE = "image"
    WINDOW = "window"
    TAB = "tab"
    SCROLL_BAR = "scroll_bar"
    UNKNOWN = "unknown"


@dataclass
class BoundingBox:
    """元素邊界框"""
    x: int
    y: int
    width: int
    height: int

    @property
    def center(self) -> Tuple[int, int]:
        """獲取中心點坐標"""
        return (self.x + self.width // 2, self.y + self.height // 2)

    @property
    def area(self) -> int:
        """獲取面積"""
        return self.width * self.height

    def contains(self, x: int, y: int) -> bool:
        """檢查點是否在邊界框內"""
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)


@dataclass
class UIElement:
    """UI 元素數據類"""
    id: str
    type: ElementType
    text: str
    bbox: BoundingBox
    confidence: float = 1.0
    interactable: bool = True
    visible: bool = True
    enabled: bool = True
    attributes: Dict = field(default_factory=dict)

    def __str__(self):
        return f"UIElement({self.type.value}, '{self.text}', pos=({self.bbox.x}, {self.bbox.y}))"


@dataclass
class Screenshot:
    """螢幕截圖數據類"""
    width: int
    height: int
    format: str
    timestamp: str
    data: Optional[bytes] = None
    elements: List[UIElement] = field(default_factory=list)


# =============================================================================
# 2. 螢幕捕獲類
# =============================================================================

class ScreenCapture:
    """
    螢幕捕獲和分析類

    提供螢幕截圖、UI 元素檢測和視覺分析功能。
    """

    def __init__(self, use_gpu: bool = False):
        """
        初始化螢幕捕獲

        Args:
            use_gpu: 是否使用 GPU 加速元素檢測
        """
        self.use_gpu = use_gpu
        self.last_screenshot: Optional[Screenshot] = None
        print(f"[螢幕捕獲] 初始化完成 (GPU: {'啟用' if use_gpu else '禁用'})")

    def capture(self, region: Optional[Tuple[int, int, int, int]] = None) -> Screenshot:
        """
        捕獲螢幕截圖

        Args:
            region: 可選的區域 (x, y, width, height)，None 表示全螢幕

        Returns:
            Screenshot 對象
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # 模擬螢幕捕獲（實際實現會使用系統 API）
        screenshot = Screenshot(
            width=1920,
            height=1080,
            format="png",
            timestamp=timestamp,
            elements=self._mock_detect_elements()
        )

        self.last_screenshot = screenshot
        print(f"[螢幕捕獲] 截圖完成: {screenshot.width}x{screenshot.height}")
        print(f"  - 檢測到 {len(screenshot.elements)} 個 UI 元素")

        return screenshot

    def _mock_detect_elements(self) -> List[UIElement]:
        """模擬 UI 元素檢測"""
        elements = [
            UIElement(
                id="btn_start",
                type=ElementType.BUTTON,
                text="Start",
                bbox=BoundingBox(10, 1050, 100, 30),
                confidence=0.98
            ),
            UIElement(
                id="icon_chrome",
                type=ElementType.ICON,
                text="Chrome",
                bbox=BoundingBox(50, 500, 64, 64),
                confidence=0.95
            ),
            UIElement(
                id="icon_vscode",
                type=ElementType.ICON,
                text="VS Code",
                bbox=BoundingBox(50, 580, 64, 64),
                confidence=0.93
            ),
            UIElement(
                id="window_explorer",
                type=ElementType.WINDOW,
                text="File Explorer",
                bbox=BoundingBox(100, 100, 800, 600),
                confidence=0.99
            ),
            UIElement(
                id="txt_search",
                type=ElementType.TEXT_FIELD,
                text="Search...",
                bbox=BoundingBox(150, 120, 300, 30),
                confidence=0.92
            ),
            UIElement(
                id="btn_close",
                type=ElementType.BUTTON,
                text="X",
                bbox=BoundingBox(880, 100, 20, 20),
                confidence=0.97
            ),
            UIElement(
                id="menu_file",
                type=ElementType.MENU,
                text="File",
                bbox=BoundingBox(110, 100, 40, 20),
                confidence=0.96
            ),
            UIElement(
                id="menu_edit",
                type=ElementType.MENU,
                text="Edit",
                bbox=BoundingBox(160, 100, 40, 20),
                confidence=0.95
            ),
        ]
        return elements

    def detect_elements(
        self,
        screenshot: Optional[Screenshot] = None,
        filter_type: Optional[ElementType] = None,
        min_confidence: float = 0.5
    ) -> List[UIElement]:
        """
        檢測 UI 元素

        Args:
            screenshot: 螢幕截圖，None 表示使用最後一次截圖
            filter_type: 過濾特定類型的元素
            min_confidence: 最小置信度閾值

        Returns:
            符合條件的 UI 元素列表
        """
        if screenshot is None:
            screenshot = self.last_screenshot or self.capture()

        elements = screenshot.elements

        # 過濾類型
        if filter_type:
            elements = [e for e in elements if e.type == filter_type]

        # 過濾置信度
        elements = [e for e in elements if e.confidence >= min_confidence]

        return elements

    def find_element_by_text(
        self,
        text: str,
        exact_match: bool = False,
        screenshot: Optional[Screenshot] = None
    ) -> Optional[UIElement]:
        """
        根據文字查找元素

        Args:
            text: 要查找的文字
            exact_match: 是否精確匹配
            screenshot: 螢幕截圖

        Returns:
            找到的元素，或 None
        """
        elements = self.detect_elements(screenshot)

        for element in elements:
            if exact_match:
                if element.text == text:
                    return element
            else:
                if text.lower() in element.text.lower():
                    return element

        return None

    def find_element_at_position(
        self,
        x: int,
        y: int,
        screenshot: Optional[Screenshot] = None
    ) -> Optional[UIElement]:
        """
        根據位置查找元素

        Args:
            x: X 坐標
            y: Y 坐標
            screenshot: 螢幕截圖

        Returns:
            該位置的元素，或 None
        """
        elements = self.detect_elements(screenshot)

        # 找到包含該點且面積最小的元素
        candidates = [e for e in elements if e.bbox.contains(x, y)]

        if not candidates:
            return None

        return min(candidates, key=lambda e: e.bbox.area)

    def get_clickable_elements(
        self,
        screenshot: Optional[Screenshot] = None
    ) -> List[UIElement]:
        """
        獲取所有可點擊的元素

        Returns:
            可點擊元素列表
        """
        elements = self.detect_elements(screenshot)

        clickable_types = {
            ElementType.BUTTON,
            ElementType.LINK,
            ElementType.ICON,
            ElementType.MENU,
            ElementType.MENU_ITEM,
            ElementType.TAB,
            ElementType.CHECKBOX,
            ElementType.RADIO
        }

        return [e for e in elements
                if e.type in clickable_types and e.interactable and e.enabled]


# =============================================================================
# 3. 視覺分析類
# =============================================================================

class VisualAnalyzer:
    """
    視覺分析類

    使用 LLM 進行螢幕理解和分析。
    """

    def __init__(self, model_name: str = "gpt-4-vision-preview"):
        """
        初始化視覺分析器

        Args:
            model_name: 使用的模型名稱
        """
        self.model_name = model_name
        print(f"[視覺分析] 初始化完成 (模型: {model_name})")

    def analyze_screen(
        self,
        screenshot: Screenshot,
        question: str
    ) -> Dict:
        """
        分析螢幕內容

        Args:
            screenshot: 螢幕截圖
            question: 關於螢幕的問題

        Returns:
            分析結果
        """
        print(f"[視覺分析] 問題: {question}")

        # 模擬 LLM 分析
        result = {
            "question": question,
            "answer": f"根據螢幕截圖分析，{question}的答案是...",
            "elements_mentioned": [e.text for e in screenshot.elements[:3]],
            "confidence": 0.85
        }

        return result

    def describe_screen(self, screenshot: Screenshot) -> str:
        """
        描述螢幕內容

        Args:
            screenshot: 螢幕截圖

        Returns:
            螢幕描述文字
        """
        elements = screenshot.elements
        element_types = {}

        for e in elements:
            type_name = e.type.value
            element_types[type_name] = element_types.get(type_name, 0) + 1

        description = f"螢幕尺寸: {screenshot.width}x{screenshot.height}\n"
        description += f"檢測到的元素:\n"

        for type_name, count in element_types.items():
            description += f"  - {type_name}: {count} 個\n"

        description += "\n主要元素:\n"
        for e in elements[:5]:
            description += f"  - {e.type.value}: '{e.text}' at ({e.bbox.x}, {e.bbox.y})\n"

        return description

    def find_target_element(
        self,
        screenshot: Screenshot,
        target_description: str
    ) -> Optional[UIElement]:
        """
        根據描述查找目標元素

        Args:
            screenshot: 螢幕截圖
            target_description: 目標元素的自然語言描述

        Returns:
            最匹配的元素
        """
        print(f"[視覺分析] 查找目標: {target_description}")

        # 模擬 LLM 匹配
        elements = screenshot.elements

        # 簡單的關鍵字匹配
        for element in elements:
            if any(word.lower() in element.text.lower()
                   for word in target_description.split()):
                print(f"  -> 找到匹配: {element}")
                return element

        print("  -> 未找到匹配元素")
        return None


# =============================================================================
# 4. 使用示例
# =============================================================================

def example_basic_capture():
    """基礎螢幕捕獲示例"""
    print("\n" + "="*60)
    print("範例 1: 基礎螢幕捕獲")
    print("="*60)

    capture = ScreenCapture()

    # 捕獲全螢幕
    screenshot = capture.capture()

    # 列出所有元素
    print("\n檢測到的元素:")
    for element in screenshot.elements:
        print(f"  {element}")


def example_find_elements():
    """查找元素示例"""
    print("\n" + "="*60)
    print("範例 2: 查找元素")
    print("="*60)

    capture = ScreenCapture()
    screenshot = capture.capture()

    # 根據文字查找
    chrome = capture.find_element_by_text("Chrome")
    if chrome:
        print(f"\n找到 Chrome: {chrome}")
        print(f"  中心位置: {chrome.bbox.center}")

    # 根據類型過濾
    buttons = capture.detect_elements(filter_type=ElementType.BUTTON)
    print(f"\n找到 {len(buttons)} 個按鈕:")
    for btn in buttons:
        print(f"  - {btn.text} at {btn.bbox.center}")

    # 獲取可點擊元素
    clickable = capture.get_clickable_elements()
    print(f"\n可點擊元素 ({len(clickable)} 個):")
    for elem in clickable:
        print(f"  - [{elem.type.value}] {elem.text}")


def example_visual_analysis():
    """視覺分析示例"""
    print("\n" + "="*60)
    print("範例 3: 視覺分析")
    print("="*60)

    capture = ScreenCapture()
    analyzer = VisualAnalyzer()

    screenshot = capture.capture()

    # 描述螢幕
    description = analyzer.describe_screen(screenshot)
    print("\n螢幕描述:")
    print(description)

    # 分析問題
    result = analyzer.analyze_screen(
        screenshot,
        "目前有哪些應用程序圖標可見？"
    )
    print("\n分析結果:")
    print(f"  問題: {result['question']}")
    print(f"  相關元素: {result['elements_mentioned']}")

    # 查找目標
    target = analyzer.find_target_element(
        screenshot,
        "瀏覽器圖標"
    )
    if target:
        print(f"\n找到瀏覽器圖標: {target}")


def example_element_interaction():
    """元素交互準備示例"""
    print("\n" + "="*60)
    print("範例 4: 元素交互準備")
    print("="*60)

    capture = ScreenCapture()
    screenshot = capture.capture()

    # 模擬準備點擊操作
    target = capture.find_element_by_text("Chrome")

    if target:
        center = target.bbox.center
        print(f"\n準備點擊 '{target.text}'")
        print(f"  目標位置: ({center[0]}, {center[1]})")
        print(f"  元素類型: {target.type.value}")
        print(f"  可交互: {target.interactable}")
        print(f"  置信度: {target.confidence:.2%}")


# =============================================================================
# 5. 主程序
# =============================================================================

if __name__ == "__main__":
    print("Agent S 螢幕操作指南")
    print("=" * 60)

    example_basic_capture()
    example_find_elements()
    example_visual_analysis()
    example_element_interaction()

    print("\n" + "="*60)
    print("螢幕操作指南完成！")
    print("下一步：查看 03_滑鼠鍵盤.py 學習輸入控制")
    print("="*60)
