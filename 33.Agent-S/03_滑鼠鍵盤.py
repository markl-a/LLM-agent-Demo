"""
Agent S 滑鼠鍵盤控制指南
========================

本範例演示 Agent S 的滑鼠和鍵盤控制功能。
這是 Agent 與電腦交互的核心能力。

主要內容：
1. 滑鼠移動和點擊
2. 鍵盤輸入和快捷鍵
3. 拖放操作
4. 組合操作
"""

import time
from dataclasses import dataclass
from typing import List, Tuple, Optional
from enum import Enum


# =============================================================================
# 1. 輸入類型定義
# =============================================================================

class MouseButton(Enum):
    """滑鼠按鈕枚舉"""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


class KeyModifier(Enum):
    """鍵盤修飾鍵枚舉"""
    CTRL = "ctrl"
    ALT = "alt"
    SHIFT = "shift"
    META = "meta"  # Windows 鍵 / Command 鍵


@dataclass
class MouseAction:
    """滑鼠動作記錄"""
    action_type: str
    x: int
    y: int
    button: MouseButton = MouseButton.LEFT
    timestamp: float = 0

    def __post_init__(self):
        if self.timestamp == 0:
            self.timestamp = time.time()


@dataclass
class KeyboardAction:
    """鍵盤動作記錄"""
    action_type: str
    key: str
    modifiers: List[KeyModifier] = None
    timestamp: float = 0

    def __post_init__(self):
        if self.modifiers is None:
            self.modifiers = []
        if self.timestamp == 0:
            self.timestamp = time.time()


# =============================================================================
# 2. 滑鼠控制類
# =============================================================================

class MouseController:
    """
    滑鼠控制類

    提供滑鼠移動、點擊、拖放等操作。
    """

    def __init__(self, smooth_move: bool = True, move_duration: float = 0.5):
        """
        初始化滑鼠控制器

        Args:
            smooth_move: 是否使用平滑移動
            move_duration: 移動動畫持續時間（秒）
        """
        self.smooth_move = smooth_move
        self.move_duration = move_duration
        self.current_position = (0, 0)
        self.action_history: List[MouseAction] = []

        print(f"[滑鼠控制] 初始化完成")
        print(f"  - 平滑移動: {'啟用' if smooth_move else '禁用'}")

    def move_to(self, x: int, y: int, duration: Optional[float] = None) -> bool:
        """
        移動滑鼠到指定位置

        Args:
            x: 目標 X 坐標
            y: 目標 Y 坐標
            duration: 移動持續時間

        Returns:
            是否成功
        """
        duration = duration or self.move_duration

        print(f"[滑鼠] 移動到 ({x}, {y})")

        if self.smooth_move and duration > 0:
            # 模擬平滑移動
            steps = int(duration * 60)  # 60fps
            start_x, start_y = self.current_position

            for i in range(steps):
                progress = (i + 1) / steps
                current_x = int(start_x + (x - start_x) * progress)
                current_y = int(start_y + (y - start_y) * progress)
                # 實際實現會調用系統 API 移動滑鼠

        self.current_position = (x, y)
        self.action_history.append(MouseAction("move", x, y))
        return True

    def click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        button: MouseButton = MouseButton.LEFT,
        clicks: int = 1
    ) -> bool:
        """
        點擊滑鼠

        Args:
            x: X 坐標（None 表示當前位置）
            y: Y 坐標（None 表示當前位置）
            button: 滑鼠按鈕
            clicks: 點擊次數

        Returns:
            是否成功
        """
        if x is not None and y is not None:
            self.move_to(x, y)

        click_type = "click" if clicks == 1 else f"click x{clicks}"
        print(f"[滑鼠] {click_type} ({button.value}) at {self.current_position}")

        self.action_history.append(MouseAction(
            f"click_{clicks}",
            self.current_position[0],
            self.current_position[1],
            button
        ))

        return True

    def double_click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None
    ) -> bool:
        """雙擊滑鼠"""
        return self.click(x, y, clicks=2)

    def right_click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None
    ) -> bool:
        """右鍵點擊"""
        return self.click(x, y, button=MouseButton.RIGHT)

    def drag(
        self,
        start: Tuple[int, int],
        end: Tuple[int, int],
        button: MouseButton = MouseButton.LEFT,
        duration: float = 0.5
    ) -> bool:
        """
        拖放操作

        Args:
            start: 起始位置
            end: 結束位置
            button: 使用的滑鼠按鈕
            duration: 拖動持續時間

        Returns:
            是否成功
        """
        print(f"[滑鼠] 拖放 {start} -> {end}")

        # 移動到起始位置
        self.move_to(start[0], start[1], duration=0.1)

        # 按下按鈕
        print(f"  - 按下 {button.value}")
        self.action_history.append(MouseAction("mouse_down", start[0], start[1], button))

        # 移動到結束位置
        self.move_to(end[0], end[1], duration=duration)

        # 釋放按鈕
        print(f"  - 釋放 {button.value}")
        self.action_history.append(MouseAction("mouse_up", end[0], end[1], button))

        return True

    def scroll(
        self,
        direction: str = "down",
        amount: int = 3,
        x: Optional[int] = None,
        y: Optional[int] = None
    ) -> bool:
        """
        滾動滑鼠滾輪

        Args:
            direction: 方向 ("up", "down", "left", "right")
            amount: 滾動量
            x: X 坐標
            y: Y 坐標

        Returns:
            是否成功
        """
        if x is not None and y is not None:
            self.move_to(x, y, duration=0.1)

        print(f"[滑鼠] 滾動 {direction} x{amount}")
        self.action_history.append(MouseAction(
            f"scroll_{direction}",
            self.current_position[0],
            self.current_position[1]
        ))

        return True


# =============================================================================
# 3. 鍵盤控制類
# =============================================================================

class KeyboardController:
    """
    鍵盤控制類

    提供鍵盤輸入、快捷鍵等操作。
    """

    # 常用按鍵映射
    SPECIAL_KEYS = {
        "enter": "Return",
        "tab": "Tab",
        "escape": "Escape",
        "backspace": "BackSpace",
        "delete": "Delete",
        "up": "Up",
        "down": "Down",
        "left": "Left",
        "right": "Right",
        "home": "Home",
        "end": "End",
        "pageup": "Page_Up",
        "pagedown": "Page_Down",
        "space": "space",
        "f1": "F1", "f2": "F2", "f3": "F3", "f4": "F4",
        "f5": "F5", "f6": "F6", "f7": "F7", "f8": "F8",
        "f9": "F9", "f10": "F10", "f11": "F11", "f12": "F12",
    }

    def __init__(self, typing_speed: float = 0.05):
        """
        初始化鍵盤控制器

        Args:
            typing_speed: 打字速度（每個字符的間隔秒數）
        """
        self.typing_speed = typing_speed
        self.action_history: List[KeyboardAction] = []
        print(f"[鍵盤控制] 初始化完成 (打字速度: {1/typing_speed:.1f} 字/秒)")

    def type_text(self, text: str, interval: Optional[float] = None) -> bool:
        """
        輸入文字

        Args:
            text: 要輸入的文字
            interval: 字符間隔時間

        Returns:
            是否成功
        """
        interval = interval or self.typing_speed
        print(f"[鍵盤] 輸入: '{text}'")

        for char in text:
            # 實際實現會調用系統 API
            self.action_history.append(KeyboardAction("type", char))
            time.sleep(0.001)  # 模擬延遲

        return True

    def press_key(self, key: str) -> bool:
        """
        按下單個按鍵

        Args:
            key: 按鍵名稱

        Returns:
            是否成功
        """
        key_name = self.SPECIAL_KEYS.get(key.lower(), key)
        print(f"[鍵盤] 按鍵: {key_name}")

        self.action_history.append(KeyboardAction("press", key_name))
        return True

    def hotkey(self, *keys: str) -> bool:
        """
        按下組合鍵

        Args:
            keys: 按鍵序列（修飾鍵在前）

        Returns:
            是否成功
        """
        key_names = [self.SPECIAL_KEYS.get(k.lower(), k) for k in keys]
        combo = "+".join(key_names)
        print(f"[鍵盤] 組合鍵: {combo}")

        # 解析修飾鍵
        modifiers = []
        for key in keys[:-1]:
            try:
                mod = KeyModifier(key.lower())
                modifiers.append(mod)
            except ValueError:
                pass

        self.action_history.append(KeyboardAction(
            "hotkey",
            keys[-1],
            modifiers
        ))

        return True

    def copy(self) -> bool:
        """複製 (Ctrl+C)"""
        return self.hotkey("ctrl", "c")

    def paste(self) -> bool:
        """粘貼 (Ctrl+V)"""
        return self.hotkey("ctrl", "v")

    def cut(self) -> bool:
        """剪切 (Ctrl+X)"""
        return self.hotkey("ctrl", "x")

    def select_all(self) -> bool:
        """全選 (Ctrl+A)"""
        return self.hotkey("ctrl", "a")

    def undo(self) -> bool:
        """撤銷 (Ctrl+Z)"""
        return self.hotkey("ctrl", "z")

    def redo(self) -> bool:
        """重做 (Ctrl+Y)"""
        return self.hotkey("ctrl", "y")

    def save(self) -> bool:
        """保存 (Ctrl+S)"""
        return self.hotkey("ctrl", "s")


# =============================================================================
# 4. 綜合輸入控制類
# =============================================================================

class InputController:
    """
    綜合輸入控制類

    整合滑鼠和鍵盤控制，提供高級操作。
    """

    def __init__(self):
        """初始化輸入控制器"""
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        print("[輸入控制] 初始化完成")

    def click_and_type(
        self,
        x: int,
        y: int,
        text: str,
        clear_first: bool = False
    ) -> bool:
        """
        點擊並輸入文字

        Args:
            x: X 坐標
            y: Y 坐標
            text: 要輸入的文字
            clear_first: 是否先清空輸入框

        Returns:
            是否成功
        """
        print(f"[操作] 點擊 ({x}, {y}) 並輸入 '{text}'")

        # 點擊
        self.mouse.click(x, y)

        # 清空（可選）
        if clear_first:
            self.keyboard.select_all()
            self.keyboard.press_key("delete")

        # 輸入
        self.keyboard.type_text(text)

        return True

    def drag_and_drop(
        self,
        source: Tuple[int, int],
        target: Tuple[int, int]
    ) -> bool:
        """
        拖放操作

        Args:
            source: 源位置
            target: 目標位置

        Returns:
            是否成功
        """
        print(f"[操作] 拖放 {source} -> {target}")
        return self.mouse.drag(source, target)

    def right_click_menu(
        self,
        x: int,
        y: int,
        menu_item: str
    ) -> bool:
        """
        右鍵選單操作

        Args:
            x: X 坐標
            y: Y 坐標
            menu_item: 選單項文字

        Returns:
            是否成功
        """
        print(f"[操作] 右鍵選單 -> {menu_item}")

        # 右鍵點擊
        self.mouse.right_click(x, y)

        # 模擬等待選單出現
        time.sleep(0.1)

        # 輸入選單項（模擬）
        # 實際實現會識別選單並點擊
        self.keyboard.type_text(menu_item)
        self.keyboard.press_key("enter")

        return True


# =============================================================================
# 5. 使用示例
# =============================================================================

def example_mouse_operations():
    """滑鼠操作示例"""
    print("\n" + "="*60)
    print("範例 1: 滑鼠操作")
    print("="*60)

    mouse = MouseController()

    # 移動和點擊
    mouse.move_to(100, 200)
    mouse.click()

    # 雙擊
    mouse.double_click(300, 400)

    # 右鍵
    mouse.right_click(500, 300)

    # 拖放
    mouse.drag((100, 100), (500, 500))

    # 滾動
    mouse.scroll("down", 5)

    print(f"\n總共執行 {len(mouse.action_history)} 個滑鼠操作")


def example_keyboard_operations():
    """鍵盤操作示例"""
    print("\n" + "="*60)
    print("範例 2: 鍵盤操作")
    print("="*60)

    keyboard = KeyboardController()

    # 輸入文字
    keyboard.type_text("Hello, Agent S!")

    # 按鍵
    keyboard.press_key("enter")

    # 組合鍵
    keyboard.hotkey("ctrl", "a")
    keyboard.hotkey("ctrl", "c")

    # 快捷操作
    keyboard.save()

    print(f"\n總共執行 {len(keyboard.action_history)} 個鍵盤操作")


def example_combined_operations():
    """組合操作示例"""
    print("\n" + "="*60)
    print("範例 3: 組合操作")
    print("="*60)

    controller = InputController()

    # 點擊並輸入
    controller.click_and_type(400, 300, "Hello World", clear_first=True)

    # 拖放
    controller.drag_and_drop((100, 100), (500, 500))

    # 右鍵選單
    controller.right_click_menu(600, 400, "Copy")


def example_workflow():
    """工作流示例"""
    print("\n" + "="*60)
    print("範例 4: 完整工作流 - 創建並保存文檔")
    print("="*60)

    controller = InputController()

    workflow = [
        ("雙擊打開記事本", lambda: controller.mouse.double_click(50, 500)),
        ("等待應用啟動", lambda: time.sleep(0.5)),
        ("輸入標題", lambda: controller.keyboard.type_text("Agent S Demo\n")),
        ("輸入內容", lambda: controller.keyboard.type_text("這是一個使用 Agent S 創建的文檔。\n")),
        ("輸入更多內容", lambda: controller.keyboard.type_text("Agent S 可以自動操作電腦。")),
        ("保存文檔", lambda: controller.keyboard.save()),
    ]

    for step_name, action in workflow:
        print(f"\n[步驟] {step_name}")
        action()

    print("\n工作流完成！")


# =============================================================================
# 6. 主程序
# =============================================================================

if __name__ == "__main__":
    print("Agent S 滑鼠鍵盤控制指南")
    print("=" * 60)

    example_mouse_operations()
    example_keyboard_operations()
    example_combined_operations()
    example_workflow()

    print("\n" + "="*60)
    print("滑鼠鍵盤控制指南完成！")
    print("下一步：查看 04_任務規劃.py 學習階層式任務規劃")
    print("="*60)
