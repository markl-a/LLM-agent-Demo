"""
Cline 終端命令示例

展示如何使用 Cline 執行終端命令：
1. 執行 Git 命令
2. 運行測試
3. 構建和部署
4. 包管理
5. 數據庫操作
6. 系統管理

Cline 可以自動執行終端命令，實現完全自動化的工作流程。
"""

import os
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class ClineTerminal:
    """Cline 終端命令執行器"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化終端執行器"""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("需要提供 ANTHROPIC_API_KEY")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"

    def _call_claude(self, prompt: str, system: str = None) -> str:
        """調用 Claude API"""
        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": messages
        }

        if system:
            kwargs["system"] = system

        response = self.client.messages.create(**kwargs)
        return response.content[0].text

    def execute_command(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout: int = 30
    ) -> Tuple[int, str, str]:
        """
        執行終端命令

        Args:
            command: 要執行的命令
            cwd: 工作目錄
            timeout: 超時時間（秒）

        Returns:
            (返回碼, 標準輸出, 錯誤輸出)
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                timeout=timeout,
                capture_output=True,
                text=True
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return -1, "", str(e)

    def suggest_commands(self, task_description: str) -> List[str]:
        """
        建議執行的命令

        Args:
            task_description: 任務描述

        Returns:
            建議的命令列表
        """
        prompt = f"""
        對於以下任務，請建議需要執行的終端命令：

        任務: {task_description}

        要求:
        1. 提供完整的命令序列
        2. 包含必要的錯誤檢查
        3. 添加命令說明
        4. 考慮跨平台兼容性
        5. 包含安全性檢查

        請以列表形式返回命令，每行一個命令，格式如下：
        # 說明
        命令內容
        """

        response = self._call_claude(prompt)

        # 解析命令
        commands = []
        for line in response.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                commands.append(line)

        return commands

    def plan_git_workflow(self, goal: str) -> List[str]:
        """
        規劃 Git 工作流程

        Args:
            goal: Git 操作目標

        Returns:
            Git 命令序列
        """
        prompt = f"""
        請為以下 Git 操作規劃命令序列：

        目標: {goal}

        要求:
        1. 遵循 Git 最佳實踐
        2. 包含必要的檢查步驟
        3. 添加安全確認
        4. 處理可能的錯誤

        請返回 Git 命令序列。
        """

        response = self._call_claude(prompt)

        # 提取 Git 命令
        commands = []
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('git '):
                commands.append(line)

        return commands

    def plan_testing_workflow(self, project_type: str) -> Dict[str, List[str]]:
        """
        規劃測試工作流程

        Args:
            project_type: 項目類型

        Returns:
            測試命令字典（按測試類型分組）
        """
        prompt = f"""
        請為 {project_type} 項目規劃完整的測試工作流程：

        要求:
        1. 包含單元測試
        2. 包含集成測試
        3. 包含代碼質量檢查
        4. 包含覆蓋率報告
        5. 按順序組織

        請返回按測試類型分組的命令。
        """

        response = self._call_claude(prompt)
        return {"all_tests": response.split('\n')}

    def plan_deployment(
        self,
        environment: str,
        platform: str
    ) -> List[str]:
        """
        規劃部署流程

        Args:
            environment: 環境（dev, staging, production）
            platform: 平台（docker, kubernetes, heroku 等）

        Returns:
            部署命令序列
        """
        prompt = f"""
        請規劃部署到 {environment} 環境的命令序列：

        平台: {platform}
        環境: {environment}

        要求:
        1. 包含構建步驟
        2. 包含測試驗證
        3. 包含部署命令
        4. 包含健康檢查
        5. 包含回滾方案

        請返回完整的部署命令序列。
        """

        response = self._call_claude(prompt)

        commands = []
        for line in response.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                commands.append(line)

        return commands

    def troubleshoot_error(self, error_output: str) -> str:
        """
        診斷錯誤並建議解決方案

        Args:
            error_output: 錯誤輸出

        Returns:
            診斷和建議
        """
        prompt = f"""
        以下是執行命令時的錯誤輸出：

        {error_output}

        請:
        1. 分析錯誤原因
        2. 提供解決方案
        3. 建議修復命令
        4. 提供預防措施

        請給出詳細的診斷和建議。
        """

        return self._call_claude(prompt)


def example_execute_commands():
    """示例 1: 執行基本命令"""
    print("=" * 60)
    print("示例 1: 執行基本終端命令")
    print("=" * 60)

    terminal = ClineTerminal()

    # 執行一些基本命令
    commands = [
        ("查看當前目錄", "pwd"),
        ("列出文件", "ls -la"),
        ("檢查 Python 版本", "python --version"),
        ("檢查 Git 版本", "git --version")
    ]

    for description, command in commands:
        print(f"\n{description}:")
        print(f"命令: {command}")

        returncode, stdout, stderr = terminal.execute_command(command)

        if returncode == 0:
            print(f"✅ 成功")
            print(f"輸出: {stdout.strip()}")
        else:
            print(f"❌ 失敗 (返回碼: {returncode})")
            print(f"錯誤: {stderr.strip()}")


def example_suggest_commands():
    """示例 2: 建議命令"""
    print("\n" + "=" * 60)
    print("示例 2: 為任務建議命令")
    print("=" * 60)

    terminal = ClineTerminal()

    # 任務描述
    tasks = [
        "創建一個 Python 虛擬環境並安裝依賴",
        "初始化一個新的 Git 倉庫並創建第一個提交",
        "構建 Docker 鏡像並運行容器"
    ]

    for task in tasks:
        print(f"\n任務: {task}")
        print("建議的命令:")

        commands = terminal.suggest_commands(task)

        for i, cmd in enumerate(commands, 1):
            print(f"{i}. {cmd}")


def example_git_workflow():
    """示例 3: Git 工作流程"""
    print("\n" + "=" * 60)
    print("示例 3: 規劃 Git 工作流程")
    print("=" * 60)

    terminal = ClineTerminal()

    # Git 操作目標
    goals = [
        "創建新分支並推送到遠程",
        "合併功能分支到主分支",
        "回滾最後一次提交",
        "解決合併衝突"
    ]

    for goal in goals:
        print(f"\n目標: {goal}")
        print("Git 命令序列:")

        commands = terminal.plan_git_workflow(goal)

        for i, cmd in enumerate(commands, 1):
            print(f"{i}. {cmd}")


def example_testing_workflow():
    """示例 4: 測試工作流程"""
    print("\n" + "=" * 60)
    print("示例 4: 規劃測試工作流程")
    print("=" * 60)

    terminal = ClineTerminal()

    project_types = [
        "Python FastAPI 項目",
        "React TypeScript 項目",
        "Node.js Express 項目"
    ]

    for project_type in project_types:
        print(f"\n項目類型: {project_type}")
        print("測試命令:")

        workflow = terminal.plan_testing_workflow(project_type)

        for test_type, commands in workflow.items():
            print(f"\n{test_type}:")
            for cmd in commands[:5]:  # 只顯示前 5 個
                if cmd.strip():
                    print(f"  - {cmd.strip()}")


def example_deployment_workflow():
    """示例 5: 部署工作流程"""
    print("\n" + "=" * 60)
    print("示例 5: 規劃部署流程")
    print("=" * 60)

    terminal = ClineTerminal()

    scenarios = [
        ("staging", "docker"),
        ("production", "kubernetes"),
        ("dev", "heroku")
    ]

    for environment, platform in scenarios:
        print(f"\n環境: {environment}, 平台: {platform}")
        print("部署命令:")

        commands = terminal.plan_deployment(environment, platform)

        for i, cmd in enumerate(commands[:10], 1):  # 只顯示前 10 個
            print(f"{i}. {cmd}")


def example_troubleshoot_error():
    """示例 6: 錯誤診斷"""
    print("\n" + "=" * 60)
    print("示例 6: 診斷終端錯誤")
    print("=" * 60)

    terminal = ClineTerminal()

    # 模擬錯誤
    error_scenarios = [
        """
        npm ERR! code ENOENT
        npm ERR! syscall open
        npm ERR! path /path/to/package.json
        npm ERR! errno -2
        npm ERR! enoent ENOENT: no such file or directory
        """,
        """
        fatal: not a git repository (or any of the parent directories): .git
        """,
        """
        ModuleNotFoundError: No module named 'requests'
        """
    ]

    for error in error_scenarios:
        print(f"\n錯誤輸出:")
        print(error.strip())

        diagnosis = terminal.troubleshoot_error(error)

        print("\n診斷和建議:")
        print(diagnosis)
        print("-" * 60)


def example_automated_workflow():
    """示例 7: 自動化工作流程"""
    print("\n" + "=" * 60)
    print("示例 7: 完整自動化工作流程")
    print("=" * 60)

    terminal = ClineTerminal()

    print("\n場景: 創建新功能並部署")
    print("\n步驟:")

    workflow = [
        ("1. 創建功能分支", "git checkout -b feature/new-feature"),
        ("2. 查看狀態", "git status"),
        ("3. 運行測試", "pytest tests/"),
        ("4. 檢查代碼質量", "ruff check ."),
        ("5. 格式化代碼", "black ."),
    ]

    for step, command in workflow:
        print(f"\n{step}")
        print(f"命令: {command}")

        # 模擬執行（不實際執行以避免錯誤）
        print("狀態: ⏭️  跳過（示例模式）")


def example_complex_task():
    """示例 8: 複雜任務自動化"""
    print("\n" + "=" * 60)
    print("示例 8: 複雜任務自動化")
    print("=" * 60)

    terminal = ClineTerminal()

    complex_task = """
    設置一個新的 Python FastAPI 項目，包括：
    - 創建虛擬環境
    - 安裝依賴
    - 初始化 Git
    - 創建項目結構
    - 運行初始測試
    - 創建 Docker 容器
    """

    print(f"\n複雜任務:\n{complex_task}")
    print("\n建議的命令序列:")

    commands = terminal.suggest_commands(complex_task)

    for i, cmd in enumerate(commands, 1):
        print(f"{i}. {cmd}")

    print("\n執行計劃:")
    print("✓ 檢查前提條件")
    print("✓ 按順序執行命令")
    print("✓ 驗證每步結果")
    print("✓ 錯誤時回滾")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Cline 終端命令示例")
    print("=" * 60)

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠️  警告: 未設置 ANTHROPIC_API_KEY")
        return

    try:
        # 運行示例
        example_execute_commands()
        # example_suggest_commands()
        # example_git_workflow()
        # example_testing_workflow()
        # example_deployment_workflow()
        # example_troubleshoot_error()
        # example_automated_workflow()
        # example_complex_task()

        print("\n✅ 終端命令示例演示完成")
        print("\n💡 提示:")
        print("1. 使用 execute_command() 執行單個命令")
        print("2. 使用 suggest_commands() 獲取任務建議")
        print("3. 使用 plan_git_workflow() 規劃 Git 操作")
        print("4. 使用 troubleshoot_error() 診斷錯誤")
        print("5. 將多個命令組合成自動化工作流程")

        print("\n⚠️  安全提示:")
        print("- 在執行命令前檢查其安全性")
        print("- 避免執行不可信的命令")
        print("- 對破壞性操作要特別小心")
        print("- 在生產環境中添加額外確認")

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
