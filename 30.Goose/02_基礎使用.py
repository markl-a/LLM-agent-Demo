#!/usr/bin/env python3
"""
Goose 基礎使用示例

本範例展示 Goose 的基本命令和交互模式，包括：
1. CLI 命令使用
2. 交互式會話
3. 基本任務執行
4. 文件操作
5. Shell 命令集成

作者: AI Agent
日期: 2024
"""

import subprocess
import os
from pathlib import Path
from typing import List, Dict
import json


class GooseBasicUsage:
    """Goose 基礎使用示例"""

    def __init__(self):
        """初始化"""
        self.config_dir = Path.home() / ".config" / "goose"
        self.session_dir = self.config_dir / "sessions"

    def check_installation(self) -> bool:
        """
        檢查 Goose 是否已安裝

        Returns:
            bool: 安裝狀態
        """
        try:
            result = subprocess.run(
                ["goose", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                print(f"✓ Goose 已安裝: {result.stdout.strip()}")
                return True
            else:
                print("✗ Goose 未正確安裝")
                return False

        except FileNotFoundError:
            print("✗ 找不到 goose 命令")
            print("請先安裝: pipx install goose-ai")
            return False
        except Exception as e:
            print(f"✗ 檢查時發生錯誤: {e}")
            return False

    def show_help(self):
        """顯示 Goose 幫助信息"""
        print("\n" + "="*60)
        print("Goose 幫助信息")
        print("="*60)

        subprocess.run(["goose", "--help"])

    def basic_commands(self):
        """展示基本命令"""
        print("\n" + "="*60)
        print("基本命令示例")
        print("="*60)

        commands = [
            ("goose --version", "查看版本"),
            ("goose --help", "查看幫助"),
            ("goose info", "查看系統信息"),
            ("goose config list", "列出配置"),
            ("goose models list", "列出可用模型"),
        ]

        for cmd, desc in commands:
            print(f"\n📌 {desc}")
            print(f"   命令: {cmd}")
            print(f"   示例輸出:")
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True
            )
            if result.stdout:
                print(f"   {result.stdout[:200]}...")  # 只顯示前 200 字符

    def single_command_mode(self):
        """
        單命令模式
        在命令行直接執行任務，不進入交互模式
        """
        print("\n" + "="*60)
        print("單命令模式")
        print("="*60)

        # 示例任務列表
        tasks = [
            "列出當前目錄的文件",
            "顯示系統時間",
            "計算 123 + 456",
            "將 'Hello, Goose!' 寫入 test.txt",
            "讀取 test.txt 的內容"
        ]

        print("\n單命令模式適合快速執行簡單任務\n")

        for i, task in enumerate(tasks, 1):
            print(f"{i}. 任務: {task}")
            print(f"   命令: goose \"{task}\"")
            print()

        # 實際執行示例（註釋掉以避免真實執行）
        # subprocess.run(["goose", tasks[0]])

    def interactive_mode(self):
        """
        交互式模式
        進入持續對話模式
        """
        print("\n" + "="*60)
        print("交互式模式")
        print("="*60)

        print("""
交互式模式使用方法:

1. 啟動交互模式:
   $ goose

2. 在提示符下輸入任務:
   > 創建一個 Python 腳本，打印斐波那契數列

3. 多輪對話:
   > 現在添加命令行參數來指定數量
   > 添加單元測試
   > 生成 README 文檔

4. 特殊命令:
   > /help       - 查看幫助
   > /clear      - 清除螢幕
   > /save       - 保存當前會話
   > /exit       - 退出

5. 快捷鍵:
   Ctrl+C      - 中斷當前任務
   Ctrl+D      - 退出
        """)

        # 模擬交互過程
        print("\n示例交互過程:")
        print("-" * 60)

        conversation = [
            ("用戶", "創建一個計算器程序"),
            ("Goose", "好的！我會創建一個簡單的計算器。讓我來實現..."),
            ("Goose", "✓ 已創建 calculator.py"),
            ("用戶", "添加除法功能並處理除以零的錯誤"),
            ("Goose", "我會添加安全的除法功能..."),
            ("Goose", "✓ 已更新 calculator.py，添加了錯誤處理"),
        ]

        for role, message in conversation:
            if role == "用戶":
                print(f"\n> {message}")
            else:
                print(f"{message}")

    def session_management(self):
        """會話管理"""
        print("\n" + "="*60)
        print("會話管理")
        print("="*60)

        print("""
會話允許你保存和恢復對話歷史

1. 創建新會話:
   $ goose session new my-project

2. 列出所有會話:
   $ goose session list

3. 恢復會話:
   $ goose session resume my-project

4. 刪除會話:
   $ goose session delete my-project

5. 查看會話詳情:
   $ goose session info my-project
        """)

        # 列出現有會話（如果有的話）
        if self.session_dir.exists():
            sessions = list(self.session_dir.iterdir())
            if sessions:
                print(f"\n當前系統中的會話:")
                for session in sessions:
                    print(f"  - {session.name}")

    def file_operations_demo(self):
        """文件操作演示"""
        print("\n" + "="*60)
        print("文件操作")
        print("="*60)

        print("""
Goose 可以執行各種文件操作:

1. 讀取文件:
   > 讀取 src/main.py 的內容

2. 寫入文件:
   > 創建一個 config.json 文件，包含數據庫設置

3. 修改文件:
   > 在 app.py 中添加錯誤處理

4. 搜索文件:
   > 在項目中搜索所有包含 "TODO" 的文件

5. 重命名/移動:
   > 將 old_name.py 重命名為 new_name.py

6. 刪除文件:
   > 刪除臨時文件 temp.txt
        """)

        # 文件操作示例代碼
        examples = {
            "讀取": """
# Goose 會執行類似操作
with open('file.txt', 'r') as f:
    content = f.read()
            """,
            "寫入": """
# Goose 會執行類似操作
with open('file.txt', 'w') as f:
    f.write('內容')
            """,
            "搜索": """
# Goose 使用工具搜索
import glob
for file in glob.glob('**/*.py', recursive=True):
    # 搜索邏輯
            """
        }

        for op, code in examples.items():
            print(f"\n{op}操作示例:")
            print(code)

    def shell_integration(self):
        """Shell 命令集成"""
        print("\n" + "="*60)
        print("Shell 命令集成")
        print("="*60)

        print("""
Goose 可以執行 shell 命令來完成任務:

1. Git 操作:
   > 提交當前更改，消息為 "添加新功能"
   > 創建新分支 feature/user-auth
   > 查看最近 5 次提交

2. 包管理:
   > 安裝 requests 包
   > 更新所有依賴
   > 列出已安裝的包

3. 測試運行:
   > 運行所有測試
   > 運行 tests/test_auth.py
   > 運行測試並生成覆蓋率報告

4. 構建和部署:
   > 構建 Docker 鏡像
   > 運行 npm build
   > 啟動開發服務器
        """)

        # 常用命令示例
        common_commands = {
            "Git": [
                "git status",
                "git add .",
                "git commit -m 'message'",
                "git push origin main"
            ],
            "Python": [
                "pip install package",
                "python script.py",
                "pytest tests/",
                "black ."
            ],
            "Node.js": [
                "npm install",
                "npm test",
                "npm run build",
                "npm start"
            ]
        }

        print("\n常用命令參考:")
        for category, cmds in common_commands.items():
            print(f"\n{category}:")
            for cmd in cmds:
                print(f"  - {cmd}")

    def context_awareness(self):
        """上下文感知演示"""
        print("\n" + "="*60)
        print("上下文感知")
        print("="*60)

        print("""
Goose 理解項目上下文並做出智能決策:

1. 項目類型檢測:
   - 檢測 package.json → Node.js 項目
   - 檢測 requirements.txt → Python 項目
   - 檢測 pom.xml → Java Maven 項目

2. 框架識別:
   - Django: manage.py, settings.py
   - Flask: app.py, Flask imports
   - React: package.json with react
   - FastAPI: FastAPI imports

3. 代碼風格適應:
   - 檢測現有縮進（2 或 4 空格）
   - 引號風格（單引號或雙引號）
   - 命名慣例（camelCase 或 snake_case）

4. 依賴管理:
   - 自動安裝缺失的包
   - 更新 requirements.txt
   - 處理版本衝突
        """)

        # 項目檢測示例
        project_markers = {
            "Python": ["requirements.txt", "setup.py", "pyproject.toml"],
            "Node.js": ["package.json", "package-lock.json"],
            "Go": ["go.mod", "go.sum"],
            "Rust": ["Cargo.toml", "Cargo.lock"],
            "Java": ["pom.xml", "build.gradle"]
        }

        print("\n項目類型標識文件:")
        for lang, markers in project_markers.items():
            print(f"\n{lang}:")
            for marker in markers:
                print(f"  - {marker}")

    def advanced_features(self):
        """進階功能預覽"""
        print("\n" + "="*60)
        print("進階功能")
        print("="*60)

        features = [
            {
                "name": "代碼生成",
                "description": "從自然語言生成完整代碼",
                "example": 'goose "創建一個 REST API，包含用戶 CRUD 操作"'
            },
            {
                "name": "代碼審查",
                "description": "自動審查代碼並提供建議",
                "example": 'goose "審查 src/auth.py 的安全性"'
            },
            {
                "name": "Bug 修復",
                "description": "診斷和修復 Bug",
                "example": 'goose "修復測試失敗的問題"'
            },
            {
                "name": "重構",
                "description": "改進代碼結構和質量",
                "example": 'goose "重構 utils.py，提高可讀性"'
            },
            {
                "name": "文檔生成",
                "description": "自動生成文檔",
                "example": 'goose "為所有函數添加 docstring"'
            },
            {
                "name": "測試生成",
                "description": "創建單元測試",
                "example": 'goose "為 calculator.py 生成測試"'
            }
        ]

        for feature in features:
            print(f"\n📌 {feature['name']}")
            print(f"   {feature['description']}")
            print(f"   示例: {feature['example']}")

    def best_practices(self):
        """最佳實踐"""
        print("\n" + "="*60)
        print("最佳實踐")
        print("="*60)

        practices = [
            "1. 清晰的任務描述",
            "   ✓ '重構 auth.py 的 login 函數，添加錯誤處理'",
            "   ✗ '改進代碼'",
            "",
            "2. 提供足夠上下文",
            "   ✓ '這是 Django 項目，添加用戶認證，使用 JWT'",
            "   ✗ '添加認證'",
            "",
            "3. 分步驟執行",
            "   ✓ 先創建模型，再創建 API，最後添加測試",
            "   ✗ 一次要求完成所有功能",
            "",
            "4. 使用版本控制",
            "   - 在使用 Goose 前提交變更",
            "   - 審查 AI 生成的代碼",
            "   - 測試後再提交",
            "",
            "5. 審查輸出",
            "   - 檢查安全性",
            "   - 驗證邏輯正確性",
            "   - 運行測試",
            "",
            "6. 善用會話",
            "   - 長期項目使用命名會話",
            "   - 定期保存進度",
            "   - 為不同任務創建不同會話"
        ]

        for practice in practices:
            print(practice)


def main():
    """主函數"""
    print("="*60)
    print("Goose 基礎使用教程")
    print("="*60)

    goose = GooseBasicUsage()

    # 檢查安裝
    if not goose.check_installation():
        print("\n請先安裝 Goose，參考 01_安裝配置.md")
        return

    # 展示各種功能
    demos = [
        ("幫助信息", goose.show_help),
        ("基本命令", goose.basic_commands),
        ("單命令模式", goose.single_command_mode),
        ("交互式模式", goose.interactive_mode),
        ("會話管理", goose.session_management),
        ("文件操作", goose.file_operations_demo),
        ("Shell 集成", goose.shell_integration),
        ("上下文感知", goose.context_awareness),
        ("進階功能", goose.advanced_features),
        ("最佳實踐", goose.best_practices),
    ]

    print("\n選擇要查看的示例:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"{i}. {name}")
    print("0. 全部執行")

    try:
        choice = input("\n請輸入選項 (0-{}): ".format(len(demos)))
        choice = int(choice)

        if choice == 0:
            # 執行所有示例
            for name, func in demos:
                func()
                input("\n按 Enter 繼續...")
        elif 1 <= choice <= len(demos):
            # 執行選定的示例
            _, func = demos[choice - 1]
            func()
        else:
            print("無效的選項")

    except KeyboardInterrupt:
        print("\n\n中斷執行")
    except ValueError:
        print("請輸入數字")

    print("\n" + "="*60)
    print("教程結束")
    print("="*60)
    print("\n下一步:")
    print("- 閱讀 03_開發任務.py 學習開發任務")
    print("- 閱讀 04_代碼審查.py 學習代碼審查")
    print("- 訪問 https://block.github.io/goose/ 查看完整文檔")


if __name__ == "__main__":
    main()
