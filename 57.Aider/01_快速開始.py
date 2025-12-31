"""
Aider 快速開始指南
===================

本範例展示如何開始使用 Aider 進行 AI 輔助編程。
包括基本設定、初始化會話、基本命令操作等。

作者：AI Agent Demo
日期：2025-12-31
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Optional, Dict
import json
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AiderConfig:
    """
    Aider 配置類

    用於管理 Aider 的基本配置選項，包括模型選擇、API 金鑰、
    工作目錄等設定。
    """
    model: str = "gpt-4-turbo"
    api_key: Optional[str] = None
    work_dir: str = "."
    auto_commits: bool = False
    dark_mode: bool = True
    voice_language: Optional[str] = None

    def __post_init__(self):
        """初始化後驗證配置"""
        if not self.api_key:
            # 嘗試從環境變數中獲取 API 金鑰
            if "gpt" in self.model.lower():
                self.api_key = os.getenv("OPENAI_API_KEY")
            elif "claude" in self.model.lower():
                self.api_key = os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            print("警告：未設定 API 金鑰，請設定環境變數")


class AiderQuickStart:
    """
    Aider 快速開始類

    提供一系列方法來幫助用戶快速上手 Aider，包括環境檢查、
    基本配置、示例項目創建等功能。
    """

    def __init__(self, config: Optional[AiderConfig] = None):
        """
        初始化 AiderQuickStart

        Args:
            config: Aider 配置對象，如果不提供則使用默認配置
        """
        self.config = config or AiderConfig()
        self.work_dir = Path(self.config.work_dir)
        self.history: List[Dict] = []

    def check_environment(self) -> bool:
        """
        檢查運行環境是否滿足 Aider 的要求

        檢查項目包括：
        1. Python 版本（>= 3.8）
        2. Git 是否安裝
        3. Aider 是否安裝
        4. API 金鑰是否設定

        Returns:
            bool: 環境檢查是否通過
        """
        print("=" * 60)
        print("檢查 Aider 運行環境...")
        print("=" * 60)

        checks = {
            "Python 版本": self._check_python_version(),
            "Git 安裝": self._check_git_installed(),
            "Aider 安裝": self._check_aider_installed(),
            "API 金鑰": self._check_api_key()
        }

        for check_name, passed in checks.items():
            status = "✓ 通過" if passed else "✗ 失敗"
            print(f"{check_name}: {status}")

        all_passed = all(checks.values())
        print("=" * 60)

        if all_passed:
            print("環境檢查全部通過！可以開始使用 Aider")
        else:
            print("環境檢查未通過，請解決上述問題")

        return all_passed

    def _check_python_version(self) -> bool:
        """檢查 Python 版本是否 >= 3.8"""
        version = sys.version_info
        return version.major >= 3 and version.minor >= 8

    def _check_git_installed(self) -> bool:
        """檢查 Git 是否安裝"""
        try:
            subprocess.run(
                ["git", "--version"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _check_aider_installed(self) -> bool:
        """檢查 Aider 是否安裝"""
        try:
            subprocess.run(
                ["aider", "--version"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _check_api_key(self) -> bool:
        """檢查 API 金鑰是否設定"""
        return self.config.api_key is not None

    def install_aider(self) -> bool:
        """
        安裝 Aider

        使用 pip 安裝最新版本的 Aider。
        如果需要語音功能，會提示用戶是否安裝額外依賴。

        Returns:
            bool: 安裝是否成功
        """
        print("\n開始安裝 Aider...")

        try:
            # 基本安裝
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "aider-chat"],
                check=True
            )

            print("✓ Aider 基本安裝完成")

            # 詢問是否安裝語音功能
            install_voice = input("\n是否安裝語音功能？(y/n): ").lower() == 'y'

            if install_voice:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "aider-chat[voice]"],
                    check=True
                )
                print("✓ Aider 語音功能安裝完成")

            return True

        except subprocess.CalledProcessError as e:
            print(f"✗ 安裝失敗: {e}")
            return False

    def setup_api_keys(self) -> None:
        """
        設定 API 金鑰

        引導用戶設定所需的 API 金鑰，支援：
        - OpenAI API Key
        - Anthropic API Key
        - Google API Key

        金鑰會被保存到環境變數配置文件中。
        """
        print("\n" + "=" * 60)
        print("API 金鑰設定")
        print("=" * 60)

        print("\nAider 支援多種 AI 模型提供商：")
        print("1. OpenAI (GPT-4, GPT-3.5)")
        print("2. Anthropic (Claude)")
        print("3. Google (PaLM)")
        print("4. 本地模型 (Ollama)")

        provider = input("\n請選擇您要使用的提供商 (1-4): ")

        env_vars = {}

        if provider == "1":
            api_key = input("請輸入您的 OpenAI API Key: ")
            env_vars["OPENAI_API_KEY"] = api_key
            self.config.model = "gpt-4-turbo"

        elif provider == "2":
            api_key = input("請輸入您的 Anthropic API Key: ")
            env_vars["ANTHROPIC_API_KEY"] = api_key
            self.config.model = "claude-3-5-sonnet-20241022"

        elif provider == "3":
            api_key = input("請輸入您的 Google API Key: ")
            env_vars["GOOGLE_API_KEY"] = api_key
            self.config.model = "gemini-pro"

        elif provider == "4":
            print("\n使用本地模型，無需 API 金鑰")
            self.config.model = "ollama/codellama"

        # 保存到 .env 文件
        if env_vars:
            self._save_to_env_file(env_vars)
            print(f"\n✓ API 金鑰已保存到 .env 文件")
            print(f"✓ 已設定使用模型: {self.config.model}")

    def _save_to_env_file(self, env_vars: Dict[str, str]) -> None:
        """
        將環境變數保存到 .env 文件

        Args:
            env_vars: 要保存的環境變數字典
        """
        env_file = self.work_dir / ".env"

        # 讀取現有內容
        existing_vars = {}
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        existing_vars[key] = value

        # 更新變數
        existing_vars.update(env_vars)

        # 寫回文件
        with open(env_file, 'w') as f:
            for key, value in existing_vars.items():
                f.write(f"{key}={value}\n")

    def create_sample_project(self) -> Path:
        """
        創建示例項目

        創建一個簡單的 Python 項目，用於演示 Aider 的功能。
        項目包括：
        - 一個簡單的 Python 模組
        - README 文件
        - Git 儲存庫初始化

        Returns:
            Path: 創建的項目路徑
        """
        print("\n創建示例項目...")

        # 創建項目目錄
        project_dir = self.work_dir / "aider_demo_project"
        project_dir.mkdir(exist_ok=True)

        # 創建示例 Python 文件
        main_py = project_dir / "main.py"
        main_py.write_text('''"""
示例項目主文件
"""

def greet(name: str) -> str:
    """
    問候函數

    Args:
        name: 要問候的名字

    Returns:
        問候訊息
    """
    return f"Hello, {name}!"


def main():
    """主函數"""
    print(greet("World"))


if __name__ == "__main__":
    main()
''')

        # 創建 README
        readme = project_dir / "README.md"
        readme.write_text('''# Aider Demo Project

這是一個用於演示 Aider 功能的示例項目。

## 使用方法

```bash
python main.py
```
''')

        # 初始化 Git 儲存庫
        subprocess.run(
            ["git", "init"],
            cwd=project_dir,
            capture_output=True
        )

        subprocess.run(
            ["git", "add", "."],
            cwd=project_dir,
            capture_output=True
        )

        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=project_dir,
            capture_output=True
        )

        print(f"✓ 示例項目已創建於: {project_dir}")
        return project_dir

    def run_basic_tutorial(self) -> None:
        """
        運行基本教學

        引導用戶進行一系列基本操作，學習 Aider 的核心功能：
        1. 啟動 Aider
        2. 添加文件到會話
        3. 發送簡單的編程請求
        4. 查看和應用變更
        5. 提交到 Git
        """
        print("\n" + "=" * 60)
        print("Aider 基本教學")
        print("=" * 60)

        # 步驟 1: 創建示例項目
        print("\n步驟 1: 創建示例項目")
        project_dir = self.create_sample_project()

        # 步驟 2: 顯示如何啟動 Aider
        print("\n步驟 2: 啟動 Aider")
        print("\n要啟動 Aider，請在項目目錄中執行：")
        print(f"\n  cd {project_dir}")
        print(f"  aider --model {self.config.model}\n")

        # 步驟 3: 基本命令
        print("步驟 3: 基本命令")
        print("\n在 Aider 會話中，您可以使用以下命令：")

        basic_commands = [
            ("/add <file>", "添加文件到會話"),
            ("/drop <file>", "從會話中移除文件"),
            ("/ls", "列出會話中的文件"),
            ("/diff", "查看未提交的變更"),
            ("/commit <msg>", "提交變更到 Git"),
            ("/undo", "撤銷最後一次變更"),
            ("/help", "顯示幫助訊息"),
            ("/exit", "退出 Aider"),
        ]

        for command, description in basic_commands:
            print(f"  {command:20} - {description}")

        # 步驟 4: 示例對話
        print("\n步驟 4: 示例對話")
        print("\n以下是一個典型的 Aider 使用流程：")

        example_dialogue = """
> aider main.py

Aider v0.65.0
Model: gpt-4-turbo
Added main.py to the chat

> 請在 main.py 中添加一個計算兩個數字之和的函數

# Aider 會修改文件並顯示 diff

> /diff

# 查看具體的變更內容

> /commit 添加 add_numbers 函數

# 提交到 Git

> 請為 add_numbers 函數添加單元測試

# Aider 會創建或修改測試文件

> /exit

# 結束會話
        """

        print(example_dialogue)

        # 步驟 5: 提示和技巧
        print("\n步驟 5: 提示和技巧")
        print("\n使用 Aider 的最佳實踐：")

        tips = [
            "明確描述您的需求，提供足夠的上下文",
            "一次處理一個功能，保持變更的專注性",
            "經常查看 diff 以確保變更符合預期",
            "使用有意義的提交訊息",
            "遇到問題時可以使用 /undo 撤銷",
            "利用 Git 分支進行實驗性變更",
        ]

        for i, tip in enumerate(tips, 1):
            print(f"  {i}. {tip}")

    def generate_config_file(self) -> None:
        """
        生成 Aider 配置文件

        創建 .aider.conf.yml 文件，包含常用的配置選項。
        用戶可以根據需要修改這些配置。
        """
        config_content = f"""# Aider 配置文件
# 更多選項請參考: https://aider.chat/docs/config.html

# 默認使用的模型
model: {self.config.model}

# 自動提交變更
auto-commits: {str(self.config.auto_commits).lower()}

# 不允許在有未提交變更時進行修改
dirty-commits: false

# 在 Git 提交中標註作者
attribute-author: true
attribute-committer: true

# 顏色主題 (light/dark)
dark-mode: {str(self.config.dark_mode).lower()}

# Repository map 的 token 數量
map-tokens: 1024

# 自動添加相關文件到會話
auto-lint: true

# 顯示 diff 時使用的格式
pretty: true

# 語音語言設定
# voice-language: zh-TW
"""

        config_file = self.work_dir / ".aider.conf.yml"
        config_file.write_text(config_content)

        print(f"\n✓ 配置文件已創建: {config_file}")

    def show_common_workflows(self) -> None:
        """
        展示常見工作流程

        提供幾個實際的使用場景和對應的 Aider 命令。
        """
        print("\n" + "=" * 60)
        print("常見工作流程")
        print("=" * 60)

        workflows = {
            "新功能開發": """
1. 創建新分支
   $ git checkout -b feature/new-feature

2. 啟動 Aider 並添加相關文件
   $ aider src/module.py tests/test_module.py

3. 描述需求
   > 請實現一個新功能...

4. 審查和測試
   > /diff
   > /test

5. 提交變更
   > /commit 實現新功能 XYZ
            """,

            "Bug 修復": """
1. 重現問題
   $ python -m pytest tests/test_bug.py -v

2. 啟動 Aider
   $ aider src/buggy_module.py

3. 描述問題
   > 這個函數在處理空值時會崩潰，請修復

4. 驗證修復
   > /test

5. 提交
   > /commit 修復空值處理問題
            """,

            "代碼重構": """
1. 確保有測試覆蓋
   $ python -m pytest

2. 啟動 Aider 包含所有相關文件
   $ aider src/*.py

3. 描述重構目標
   > 請重構這些類以遵循單一職責原則

4. 確保測試仍然通過
   > /test

5. 提交
   > /commit 重構以改善代碼結構
            """,
        }

        for title, workflow in workflows.items():
            print(f"\n### {title}")
            print(workflow)


def main():
    """
    主函數

    演示 Aider 快速開始的完整流程。
    """
    print("=" * 60)
    print("歡迎使用 Aider - AI 編程助手")
    print("=" * 60)

    # 創建配置
    config = AiderConfig(
        model="gpt-4-turbo",
        auto_commits=False,
        dark_mode=True
    )

    # 創建快速開始實例
    quick_start = AiderQuickStart(config)

    # 檢查環境
    env_ok = quick_start.check_environment()

    if not env_ok:
        print("\n需要先解決環境問題")
        install = input("是否現在安裝 Aider? (y/n): ").lower() == 'y'

        if install:
            quick_start.install_aider()
            quick_start.setup_api_keys()

    # 生成配置文件
    quick_start.generate_config_file()

    # 運行教學
    tutorial = input("\n是否運行基本教學? (y/n): ").lower() == 'y'
    if tutorial:
        quick_start.run_basic_tutorial()

    # 顯示常見工作流程
    workflows = input("\n是否查看常見工作流程? (y/n): ").lower() == 'y'
    if workflows:
        quick_start.show_common_workflows()

    print("\n" + "=" * 60)
    print("快速開始完成！")
    print("現在您可以開始使用 Aider 了")
    print("執行 'aider --help' 查看所有可用選項")
    print("=" * 60)


if __name__ == "__main__":
    main()
