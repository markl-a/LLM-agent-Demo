"""
Agent-S 應用控制模組

此模組展示 Agent-S 控制桌面應用程序的能力：
1. 應用啟動 - 啟動和關閉應用程序
2. 窗口管理 - 管理應用窗口（最小化、最大化、移動）
3. UI 交互 - 與應用 UI 元素交互
4. 跨應用協作 - 在多個應用間協調操作

Agent-S 使用操作系統 API 和計算機視覺來控制應用程序。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
import time


class AppType(Enum):
    """應用類型"""
    BROWSER = "瀏覽器"
    EDITOR = "編輯器"
    TERMINAL = "終端"
    FILE_MANAGER = "文件管理器"
    EMAIL = "郵件客戶端"
    OFFICE = "辦公軟件"
    MEDIA_PLAYER = "媒體播放器"
    COMMUNICATION = "通訊軟件"


class WindowState(Enum):
    """窗口狀態"""
    NORMAL = "正常"
    MINIMIZED = "最小化"
    MAXIMIZED = "最大化"
    FULLSCREEN = "全屏"
    CLOSED = "已關閉"


@dataclass
class WindowInfo:
    """窗口信息"""
    window_id: str
    title: str
    app_name: str
    state: WindowState = WindowState.NORMAL
    position: Tuple[int, int] = (0, 0)  # (x, y)
    size: Tuple[int, int] = (800, 600)  # (width, height)
    is_focused: bool = False

    def __str__(self):
        return f"{self.app_name}: {self.title} [{self.state.value}]"


@dataclass
class UIElement:
    """UI 元素"""
    element_id: str
    element_type: str  # button, menu, input, etc.
    label: str
    position: Tuple[int, int]
    size: Tuple[int, int]
    enabled: bool = True
    visible: bool = True

    def __str__(self):
        return f"{self.element_type}: {self.label}"


@dataclass
class Application:
    """應用程序"""
    app_id: str
    name: str
    app_type: AppType
    executable: str
    is_running: bool = False
    main_window: Optional[WindowInfo] = None
    ui_elements: List[UIElement] = field(default_factory=list)

    def __str__(self):
        status = "運行中" if self.is_running else "未運行"
        return f"{self.name} ({self.app_type.value}) - {status}"


class ApplicationController:
    """
    應用程序控制器

    管理應用程序的生命週期和基本操作
    """

    def __init__(self):
        self.applications: Dict[str, Application] = {}
        self.running_apps: Dict[str, Application] = {}
        self._register_common_apps()

    def _register_common_apps(self):
        """註冊常用應用程序"""
        apps = [
            Application("chrome", "Google Chrome", AppType.BROWSER, "chrome.exe"),
            Application("vscode", "VS Code", AppType.EDITOR, "code.exe"),
            Application("terminal", "終端", AppType.TERMINAL, "terminal.exe"),
            Application("explorer", "文件管理器", AppType.FILE_MANAGER, "explorer.exe"),
            Application("outlook", "Outlook", AppType.EMAIL, "outlook.exe"),
            Application("word", "Microsoft Word", AppType.OFFICE, "winword.exe"),
            Application("excel", "Microsoft Excel", AppType.OFFICE, "excel.exe"),
            Application("slack", "Slack", AppType.COMMUNICATION, "slack.exe"),
        ]

        for app in apps:
            self.applications[app.app_id] = app

    def launch(self, app_id: str, args: Optional[List[str]] = None) -> bool:
        """啟動應用程序"""
        if app_id not in self.applications:
            print(f"錯誤: 未知應用程序 '{app_id}'")
            return False

        app = self.applications[app_id]

        if app.is_running:
            print(f"{app.name} 已在運行中")
            return True

        print(f"\n啟動應用程序: {app.name}")
        print(f"可執行文件: {app.executable}")

        if args:
            print(f"參數: {args}")

        # 模擬啟動
        time.sleep(0.5)

        # 創建主窗口
        app.main_window = WindowInfo(
            window_id=f"win_{app.app_id}",
            title=app.name,
            app_name=app.name,
            state=WindowState.NORMAL,
            is_focused=True
        )

        # 創建 UI 元素
        app.ui_elements = self._create_ui_elements(app)

        app.is_running = True
        self.running_apps[app_id] = app

        print(f"✓ {app.name} 已啟動")
        return True

    def _create_ui_elements(self, app: Application) -> List[UIElement]:
        """創建應用 UI 元素（模擬）"""
        if app.app_type == AppType.BROWSER:
            return [
                UIElement("url_bar", "input", "地址欄", (100, 50), (600, 30)),
                UIElement("back_btn", "button", "後退", (10, 50), (30, 30)),
                UIElement("forward_btn", "button", "前進", (50, 50), (30, 30)),
                UIElement("refresh_btn", "button", "刷新", (710, 50), (30, 30)),
            ]
        elif app.app_type == AppType.EDITOR:
            return [
                UIElement("menu_file", "menu", "文件", (10, 10), (50, 20)),
                UIElement("menu_edit", "menu", "編輯", (70, 10), (50, 20)),
                UIElement("editor_area", "textarea", "編輯區", (0, 50), (800, 550)),
            ]
        elif app.app_type == AppType.EMAIL:
            return [
                UIElement("new_email_btn", "button", "新建郵件", (10, 50), (100, 30)),
                UIElement("inbox", "list", "收件箱", (10, 100), (200, 400)),
                UIElement("email_content", "panel", "郵件內容", (220, 100), (580, 400)),
            ]
        else:
            return [
                UIElement("main_area", "panel", "主區域", (0, 0), (800, 600)),
            ]

    def close(self, app_id: str) -> bool:
        """關閉應用程序"""
        if app_id not in self.running_apps:
            print(f"{app_id} 未運行")
            return False

        app = self.running_apps[app_id]

        print(f"\n關閉應用程序: {app.name}")

        # 模擬關閉
        time.sleep(0.2)

        app.is_running = False
        app.main_window.state = WindowState.CLOSED if app.main_window else None
        del self.running_apps[app_id]

        print(f"✓ {app.name} 已關閉")
        return True

    def get_running_apps(self) -> List[Application]:
        """獲取所有運行中的應用"""
        return list(self.running_apps.values())

    def focus(self, app_id: str) -> bool:
        """將應用程序設為焦點"""
        if app_id not in self.running_apps:
            return False

        app = self.running_apps[app_id]

        # 取消其他應用的焦點
        for other_app in self.running_apps.values():
            if other_app.main_window:
                other_app.main_window.is_focused = False

        # 設置焦點
        if app.main_window:
            app.main_window.is_focused = True

        print(f"\n切換到: {app.name}")
        return True


class WindowManager:
    """
    窗口管理器

    管理應用窗口的狀態和位置
    """

    def __init__(self, controller: ApplicationController):
        self.controller = controller

    def minimize(self, app_id: str) -> bool:
        """最小化窗口"""
        if app_id not in self.controller.running_apps:
            return False

        app = self.controller.running_apps[app_id]
        if app.main_window:
            app.main_window.state = WindowState.MINIMIZED
            print(f"\n{app.name} 已最小化")
            return True

        return False

    def maximize(self, app_id: str) -> bool:
        """最大化窗口"""
        if app_id not in self.controller.running_apps:
            return False

        app = self.controller.running_apps[app_id]
        if app.main_window:
            app.main_window.state = WindowState.MAXIMIZED
            print(f"\n{app.name} 已最大化")
            return True

        return False

    def restore(self, app_id: str) -> bool:
        """恢復窗口"""
        if app_id not in self.controller.running_apps:
            return False

        app = self.controller.running_apps[app_id]
        if app.main_window:
            app.main_window.state = WindowState.NORMAL
            print(f"\n{app.name} 已恢復")
            return True

        return False

    def move(self, app_id: str, x: int, y: int) -> bool:
        """移動窗口"""
        if app_id not in self.controller.running_apps:
            return False

        app = self.controller.running_apps[app_id]
        if app.main_window:
            app.main_window.position = (x, y)
            print(f"\n{app.name} 已移動到 ({x}, {y})")
            return True

        return False

    def resize(self, app_id: str, width: int, height: int) -> bool:
        """調整窗口大小"""
        if app_id not in self.controller.running_apps:
            return False

        app = self.controller.running_apps[app_id]
        if app.main_window:
            app.main_window.size = (width, height)
            print(f"\n{app.name} 已調整為 {width}x{height}")
            return True

        return False

    def tile_windows(self, app_ids: List[str]) -> bool:
        """平鋪窗口"""
        running_apps = [
            self.controller.running_apps[aid]
            for aid in app_ids
            if aid in self.controller.running_apps
        ]

        if not running_apps:
            return False

        print(f"\n平鋪 {len(running_apps)} 個窗口")

        # 簡單的水平平鋪
        screen_width = 1920
        screen_height = 1080
        window_width = screen_width // len(running_apps)

        for i, app in enumerate(running_apps):
            if app.main_window:
                x = i * window_width
                app.main_window.position = (x, 0)
                app.main_window.size = (window_width, screen_height)
                print(f"  {app.name}: ({x}, 0) {window_width}x{screen_height}")

        return True


class UIAutomation:
    """
    UI 自動化

    與應用程序的 UI 元素交互
    """

    def __init__(self, controller: ApplicationController):
        self.controller = controller

    def click(self, app_id: str, element_id: str) -> bool:
        """點擊 UI 元素"""
        if app_id not in self.controller.running_apps:
            print(f"應用 {app_id} 未運行")
            return False

        app = self.controller.running_apps[app_id]

        # 查找元素
        element = self._find_element(app, element_id)
        if not element:
            print(f"未找到元素: {element_id}")
            return False

        if not element.enabled or not element.visible:
            print(f"元素不可用: {element}")
            return False

        print(f"\n點擊 {app.name} 的 {element}")
        time.sleep(0.1)

        return True

    def input_text(self, app_id: str, element_id: str, text: str) -> bool:
        """在輸入框中輸入文本"""
        if app_id not in self.controller.running_apps:
            return False

        app = self.controller.running_apps[app_id]
        element = self._find_element(app, element_id)

        if not element or element.element_type not in ["input", "textarea"]:
            print(f"元素不是輸入框: {element_id}")
            return False

        print(f"\n在 {app.name} 的 {element} 中輸入: '{text}'")
        time.sleep(0.1)

        return True

    def select_menu(self, app_id: str, menu_path: List[str]) -> bool:
        """選擇菜單項"""
        if app_id not in self.controller.running_apps:
            return False

        app = self.controller.running_apps[app_id]

        print(f"\n在 {app.name} 中選擇菜單: {' > '.join(menu_path)}")

        for menu_item in menu_path:
            time.sleep(0.1)
            print(f"  點擊: {menu_item}")

        return True

    def _find_element(self, app: Application, element_id: str) -> Optional[UIElement]:
        """查找 UI 元素"""
        for element in app.ui_elements:
            if element.element_id == element_id:
                return element
        return None


class WorkflowAutomator:
    """
    工作流自動化器

    協調多個應用完成複雜任務
    """

    def __init__(self):
        self.controller = ApplicationController()
        self.window_manager = WindowManager(self.controller)
        self.ui_automation = UIAutomation(self.controller)

    def send_email_with_attachment(self, to: str, subject: str, body: str, file_path: str) -> bool:
        """發送帶附件的郵件"""
        print("\n" + "="*60)
        print("自動化任務: 發送帶附件的郵件")
        print("="*60)

        # 1. 打開文件管理器，找到文件
        print("\n步驟 1: 準備附件")
        self.controller.launch("explorer")
        time.sleep(0.3)

        # 2. 打開郵件客戶端
        print("\n步驟 2: 打開郵件客戶端")
        self.controller.launch("outlook")
        time.sleep(0.3)

        # 3. 創建新郵件
        print("\n步驟 3: 創建新郵件")
        self.ui_automation.click("outlook", "new_email_btn")

        # 4. 填寫郵件
        print("\n步驟 4: 填寫郵件內容")
        print(f"  收件人: {to}")
        print(f"  主題: {subject}")
        print(f"  正文: {body}")
        print(f"  附件: {file_path}")

        # 5. 發送
        print("\n步驟 5: 發送郵件")
        time.sleep(0.2)

        print("\n✓ 郵件發送完成")
        return True

    def create_presentation_from_data(self, data_file: str, output_file: str) -> bool:
        """從數據文件創建演示文稿"""
        print("\n" + "="*60)
        print("自動化任務: 創建演示文稿")
        print("="*60)

        # 1. 打開 Excel 讀取數據
        print("\n步驟 1: 讀取數據")
        self.controller.launch("excel", [data_file])
        time.sleep(0.3)

        # 模擬讀取數據
        print("  讀取數據...")

        # 2. 打開 PowerPoint
        print("\n步驟 2: 創建演示文稿")
        # 這裡應該啟動 PowerPoint，但為了簡化使用 Word
        self.controller.launch("word")
        time.sleep(0.3)

        # 3. 創建幻燈片
        print("\n步驟 3: 插入數據和圖表")
        time.sleep(0.5)

        # 4. 保存
        print(f"\n步驟 4: 保存為 {output_file}")
        self.ui_automation.select_menu("word", ["文件", "另存為"])

        print("\n✓ 演示文稿創建完成")
        return True

    def multi_app_research(self, topic: str) -> Dict[str, Any]:
        """使用多個應用進行研究"""
        print("\n" + "="*60)
        print(f"自動化研究任務: {topic}")
        print("="*60)

        results = {
            "topic": topic,
            "web_results": [],
            "notes": "",
            "sources": []
        }

        # 1. 打開瀏覽器搜索
        print("\n步驟 1: 在線搜索")
        self.controller.launch("chrome")
        time.sleep(0.3)

        self.ui_automation.input_text("chrome", "url_bar", f"https://google.com/search?q={topic}")
        results["web_results"] = ["結果1", "結果2", "結果3"]

        # 2. 打開編輯器做筆記
        print("\n步驟 2: 記錄筆記")
        self.controller.launch("vscode")
        time.sleep(0.3)

        # 平鋪窗口以便同時查看
        self.window_manager.tile_windows(["chrome", "vscode"])

        # 3. 在編輯器中寫筆記
        self.ui_automation.input_text("vscode", "editor_area", f"研究主題: {topic}\n\n")
        results["notes"] = f"關於 {topic} 的研究筆記..."

        print("\n✓ 研究任務完成")
        return results

    def cleanup(self):
        """清理：關閉所有應用"""
        print("\n清理環境...")
        for app_id in list(self.controller.running_apps.keys()):
            self.controller.close(app_id)


def 示例1_應用啟動和關閉():
    """示例：啟動和關閉應用"""
    print("\n" + "="*60)
    print("示例 1: 應用啟動和關閉")
    print("="*60)

    controller = ApplicationController()

    # 啟動多個應用
    controller.launch("chrome")
    controller.launch("vscode")
    controller.launch("terminal")

    # 查看運行中的應用
    print("\n運行中的應用:")
    for app in controller.get_running_apps():
        print(f"  - {app}")

    # 關閉應用
    controller.close("terminal")

    return controller


def 示例2_窗口管理():
    """示例：管理窗口"""
    print("\n" + "="*60)
    print("示例 2: 窗口管理")
    print("="*60)

    controller = ApplicationController()
    window_mgr = WindowManager(controller)

    # 啟動應用
    controller.launch("chrome")
    controller.launch("vscode")

    # 窗口操作
    window_mgr.maximize("chrome")
    time.sleep(0.2)

    window_mgr.minimize("vscode")
    time.sleep(0.2)

    # 平鋪窗口
    window_mgr.restore("vscode")
    window_mgr.restore("chrome")
    window_mgr.tile_windows(["chrome", "vscode"])

    return window_mgr


def 示例3_UI交互():
    """示例：UI 元素交互"""
    print("\n" + "="*60)
    print("示例 3: UI 元素交互")
    print("="*60)

    controller = ApplicationController()
    ui_auto = UIAutomation(controller)

    # 啟動瀏覽器
    controller.launch("chrome")

    # 交互操作
    ui_auto.input_text("chrome", "url_bar", "https://github.com")
    ui_auto.click("chrome", "back_btn")
    ui_auto.click("chrome", "forward_btn")
    ui_auto.click("chrome", "refresh_btn")

    return ui_auto


def 示例4_發送郵件():
    """示例：自動發送郵件"""
    print("\n" + "="*60)
    print("示例 4: 自動發送郵件")
    print("="*60)

    automator = WorkflowAutomator()

    # 發送郵件
    automator.send_email_with_attachment(
        to="colleague@example.com",
        subject="項目進度報告",
        body="請查看附件中的項目進度報告。",
        file_path="/Documents/報告.pdf"
    )

    # 清理
    automator.cleanup()

    return automator


def 示例5_多應用協作():
    """示例：多應用協作研究"""
    print("\n" + "="*60)
    print("示例 5: 多應用協作研究")
    print("="*60)

    automator = WorkflowAutomator()

    # 執行研究任務
    results = automator.multi_app_research("人工智能最新進展")

    print("\n研究結果:")
    print(f"  搜索結果: {len(results['web_results'])} 條")
    print(f"  筆記: {results['notes']}")

    # 清理
    automator.cleanup()

    return results


if __name__ == "__main__":
    print("Agent-S 應用控制演示\n")

    示例1_應用啟動和關閉()
    示例2_窗口管理()
    示例3_UI交互()
    示例4_發送郵件()
    示例5_多應用協作()

    print("\n所有示例執行完成！")
