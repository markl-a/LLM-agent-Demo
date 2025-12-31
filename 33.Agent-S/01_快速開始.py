"""
Agent S 快速開始指南
====================

本範例演示如何使用 Agent S 框架構建一個基本的電腦使用 Agent。
Agent S 是一個能夠像人類一樣操作電腦的 AI Agent 框架。

依賴安裝：
    pip install agent-s

環境要求：
    - Python 3.9+
    - 螢幕輔助功能權限（macOS/Linux）
    - OpenAI API Key 或其他支持的模型
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


# =============================================================================
# 1. 基礎配置
# =============================================================================

@dataclass
class AgentConfig:
    """Agent 配置類"""
    model_name: str = "gpt-4-vision-preview"
    api_key: Optional[str] = None
    enable_screen: bool = True
    enable_input: bool = True
    max_steps: int = 50
    timeout: int = 300  # 秒

    def __post_init__(self):
        if self.api_key is None:
            self.api_key = os.getenv("OPENAI_API_KEY")


# =============================================================================
# 2. Agent S 模擬實現（用於演示）
# =============================================================================

class MockScreenCapture:
    """模擬螢幕捕獲（實際使用時會調用系統 API）"""

    def capture(self) -> dict:
        """捕獲當前螢幕"""
        return {
            "width": 1920,
            "height": 1080,
            "format": "png",
            "timestamp": "2025-12-31T10:00:00",
            "elements": [
                {"type": "button", "text": "Start", "x": 10, "y": 1050, "width": 100, "height": 30},
                {"type": "icon", "text": "Chrome", "x": 50, "y": 500, "width": 64, "height": 64},
                {"type": "window", "text": "File Explorer", "x": 100, "y": 100, "width": 800, "height": 600}
            ]
        }

    def detect_elements(self, screenshot: dict) -> list:
        """檢測 UI 元素"""
        return screenshot.get("elements", [])


class MockInputController:
    """模擬輸入控制器"""

    def __init__(self):
        self.action_log = []

    def click(self, x: int, y: int, button: str = "left"):
        """模擬滑鼠點擊"""
        action = f"Click {button} at ({x}, {y})"
        self.action_log.append(action)
        print(f"[輸入] {action}")
        return True

    def double_click(self, x: int, y: int):
        """模擬雙擊"""
        action = f"Double-click at ({x}, {y})"
        self.action_log.append(action)
        print(f"[輸入] {action}")
        return True

    def type_text(self, text: str):
        """模擬鍵盤輸入"""
        action = f"Type: '{text}'"
        self.action_log.append(action)
        print(f"[輸入] {action}")
        return True

    def press_key(self, key: str):
        """模擬按鍵"""
        action = f"Press key: {key}"
        self.action_log.append(action)
        print(f"[輸入] {action}")
        return True

    def hotkey(self, *keys):
        """模擬組合鍵"""
        action = f"Hotkey: {'+'.join(keys)}"
        self.action_log.append(action)
        print(f"[輸入] {action}")
        return True


class MockLLM:
    """模擬 LLM（實際使用時會調用 OpenAI/Claude 等）"""

    def __init__(self, model_name: str):
        self.model_name = model_name

    def analyze_screen(self, screenshot: dict, task: str) -> dict:
        """分析螢幕並決定下一步動作"""
        print(f"[LLM] 分析螢幕，任務: {task}")

        # 模擬 LLM 分析結果
        return {
            "reasoning": f"為了完成任務 '{task}'，需要先找到相關的 UI 元素",
            "action": {
                "type": "click",
                "target": "Chrome icon",
                "x": 50,
                "y": 500
            },
            "confidence": 0.95
        }

    def plan_task(self, task: str) -> list:
        """規劃任務步驟"""
        print(f"[LLM] 規劃任務: {task}")

        # 模擬任務規劃
        return [
            {"step": 1, "action": "打開 Chrome 瀏覽器", "details": "雙擊 Chrome 圖標"},
            {"step": 2, "action": "等待瀏覽器載入", "details": "等待 2 秒"},
            {"step": 3, "action": "輸入網址", "details": "在地址欄輸入目標網址"},
            {"step": 4, "action": "按下 Enter", "details": "確認導航"},
            {"step": 5, "action": "等待頁面載入", "details": "等待頁面完全載入"}
        ]


# =============================================================================
# 3. Agent S 核心類
# =============================================================================

class AgentS:
    """
    Agent S 主類

    實現像人類一樣使用電腦的自主 Agent。

    主要功能：
    - 螢幕理解和 UI 元素識別
    - 滑鼠和鍵盤控制
    - 階層式任務規劃
    - 從經驗中學習
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """
        初始化 Agent S

        Args:
            config: Agent 配置，如果為 None 則使用默認配置
        """
        self.config = config or AgentConfig()
        self.screen = MockScreenCapture()
        self.input = MockInputController()
        self.llm = MockLLM(self.config.model_name)
        self.step_count = 0
        self.task_history = []

        print(f"[Agent S] 初始化完成")
        print(f"  - 模型: {self.config.model_name}")
        print(f"  - 螢幕捕獲: {'啟用' if self.config.enable_screen else '禁用'}")
        print(f"  - 輸入控制: {'啟用' if self.config.enable_input else '禁用'}")

    def run(self, task: str, max_steps: Optional[int] = None) -> dict:
        """
        執行任務

        Args:
            task: 任務描述（自然語言）
            max_steps: 最大步數，默認使用配置值

        Returns:
            執行結果字典
        """
        max_steps = max_steps or self.config.max_steps
        print(f"\n{'='*60}")
        print(f"[Agent S] 開始執行任務: {task}")
        print(f"{'='*60}")

        # 1. 規劃任務
        plan = self.llm.plan_task(task)
        print(f"\n[規劃] 任務分解為 {len(plan)} 個步驟:")
        for step in plan:
            print(f"  {step['step']}. {step['action']}")

        # 2. 執行步驟
        results = []
        for step in plan:
            if self.step_count >= max_steps:
                print(f"\n[警告] 達到最大步數限制 ({max_steps})")
                break

            result = self._execute_step(step)
            results.append(result)
            self.step_count += 1

        # 3. 總結結果
        success = all(r.get("success", False) for r in results)
        summary = {
            "task": task,
            "success": success,
            "steps_executed": len(results),
            "total_actions": len(self.input.action_log),
            "results": results
        }

        print(f"\n{'='*60}")
        print(f"[Agent S] 任務完成: {'成功' if success else '失敗'}")
        print(f"  - 執行步驟: {len(results)}")
        print(f"  - 總操作數: {len(self.input.action_log)}")
        print(f"{'='*60}")

        self.task_history.append(summary)
        return summary

    def _execute_step(self, step: dict) -> dict:
        """執行單個步驟"""
        print(f"\n[步驟 {step['step']}] {step['action']}")

        # 捕獲螢幕
        screenshot = self.screen.capture()

        # 分析並決定動作
        analysis = self.llm.analyze_screen(screenshot, step['action'])

        # 執行動作
        action = analysis['action']
        if action['type'] == 'click':
            self.input.click(action['x'], action['y'])
        elif action['type'] == 'double_click':
            self.input.double_click(action['x'], action['y'])
        elif action['type'] == 'type':
            self.input.type_text(action.get('text', ''))
        elif action['type'] == 'key':
            self.input.press_key(action.get('key', ''))

        return {
            "step": step['step'],
            "action": step['action'],
            "success": True,
            "reasoning": analysis['reasoning']
        }

    def get_history(self) -> list:
        """獲取任務執行歷史"""
        return self.task_history

    def reset(self):
        """重置 Agent 狀態"""
        self.step_count = 0
        self.input.action_log = []
        print("[Agent S] 狀態已重置")


# =============================================================================
# 4. 使用示例
# =============================================================================

def example_basic_usage():
    """基礎使用示例"""
    print("\n" + "="*60)
    print("範例 1: 基礎使用")
    print("="*60)

    # 創建 Agent
    agent = AgentS()

    # 執行簡單任務
    result = agent.run("打開 Chrome 瀏覽器並訪問 google.com")

    return result


def example_with_config():
    """自定義配置示例"""
    print("\n" + "="*60)
    print("範例 2: 自定義配置")
    print("="*60)

    # 自定義配置
    config = AgentConfig(
        model_name="gpt-4-vision-preview",
        max_steps=20,
        timeout=120
    )

    # 創建 Agent
    agent = AgentS(config)

    # 執行任務
    result = agent.run("創建一個新的文字文檔並輸入 'Hello World'")

    return result


def example_multi_task():
    """多任務執行示例"""
    print("\n" + "="*60)
    print("範例 3: 多任務執行")
    print("="*60)

    agent = AgentS()

    tasks = [
        "打開計算機應用",
        "計算 123 + 456",
        "複製計算結果"
    ]

    results = []
    for task in tasks:
        result = agent.run(task, max_steps=10)
        results.append(result)
        agent.reset()  # 重置狀態

    print(f"\n[總結] 完成 {len(results)} 個任務")
    for i, r in enumerate(results, 1):
        status = "✓" if r['success'] else "✗"
        print(f"  {status} 任務 {i}: {r['task']}")

    return results


# =============================================================================
# 5. 主程序
# =============================================================================

if __name__ == "__main__":
    print("Agent S 快速開始指南")
    print("=" * 60)
    print("注意：這是一個模擬演示，實際使用需要安裝 agent-s 套件")
    print("並配置相應的 API Key 和系統權限。")
    print("=" * 60)

    # 執行示例
    example_basic_usage()
    example_with_config()
    example_multi_task()

    print("\n" + "="*60)
    print("快速開始指南完成！")
    print("下一步：")
    print("  1. 安裝 agent-s: pip install agent-s")
    print("  2. 配置 API Key")
    print("  3. 授予系統權限")
    print("  4. 查看更多範例：02_螢幕操作.py")
    print("="*60)
