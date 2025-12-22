#!/usr/bin/env python3
"""
Goose 開發任務輔助示例

展示如何使用 Goose 輔助日常軟件開發任務:
1. 代碼生成
2. 重構現有代碼
3. Bug 調試
4. 測試編寫
5. 文檔生成

作者: AI Agent
日期: 2024
"""

from typing import List, Dict, Optional
import subprocess
import os
from pathlib import Path


class DevelopmentTasksDemo:
    """開發任務示例"""

    def __init__(self):
        """初始化"""
        self.examples_dir = Path("goose_examples")
        self.examples_dir.mkdir(exist_ok=True)

    def code_generation_examples(self):
        """
        代碼生成示例
        展示如何使用 Goose 生成各種代碼
        """
        print("\n" + "="*70)
        print("代碼生成")
        print("="*70)

        examples = [
            {
                "task": "創建 RESTful API",
                "prompt": """
創建一個 FastAPI 應用，包含以下功能:
- 用戶 CRUD 操作（創建、讀取、更新、刪除）
- 使用 Pydantic 模型進行數據驗證
- SQLAlchemy ORM 連接 PostgreSQL
- JWT 認證
- 異常處理和日誌記錄
                """,
                "expected_files": [
                    "main.py",
                    "models.py",
                    "schemas.py",
                    "database.py",
                    "auth.py",
                    "requirements.txt"
                ]
            },
            {
                "task": "創建數據處理管道",
                "prompt": """
創建一個 Python 數據處理管道:
- 從 CSV 文件讀取數據
- 清理和驗證數據
- 執行統計分析
- 生成可視化圖表
- 導出結果到 Excel
使用 pandas, matplotlib, openpyxl
                """,
                "expected_files": [
                    "pipeline.py",
                    "data_cleaner.py",
                    "analyzer.py",
                    "visualizer.py"
                ]
            },
            {
                "task": "創建 CLI 工具",
                "prompt": """
創建一個命令行工具:
- 使用 Click 框架
- 支持多個子命令（init, process, export）
- 彩色輸出
- 進度條顯示
- 配置文件支持
- 詳細的幫助信息
                """,
                "expected_files": [
                    "cli.py",
                    "commands/__init__.py",
                    "commands/init.py",
                    "commands/process.py"
                ]
            }
        ]

        for example in examples:
            print(f"\n📝 任務: {example['task']}")
            print(f"\n提示詞:")
            print(example['prompt'])
            print(f"\n預期生成的文件:")
            for file in example['expected_files']:
                print(f"  - {file}")
            print(f"\n使用命令:")
            print(f'  goose "{example["task"]}"')
            print("\n" + "-"*70)

    def refactoring_examples(self):
        """
        重構示例
        展示如何使用 Goose 重構代碼
        """
        print("\n" + "="*70)
        print("代碼重構")
        print("="*70)

        # 原始代碼示例（需要重構）
        original_code = '''
def process_data(data):
    result = []
    for item in data:
        if item['status'] == 'active':
            if item['age'] >= 18:
                if item['verified'] == True:
                    result.append(item)
    return result

def calculate_total(items):
    total = 0
    for item in items:
        total = total + item['price']
    return total

def send_notification(user, message):
    # 發送郵件
    import smtplib
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('user@example.com', 'password')
    msg = f"To: {user['email']}\\nSubject: Notification\\n\\n{message}"
    server.sendmail('user@example.com', user['email'], msg)
    server.quit()
'''

        print("\n原始代碼（需要重構）:")
        print("-"*70)
        print(original_code)

        refactoring_tasks = [
            {
                "type": "簡化條件邏輯",
                "prompt": "重構 process_data 函數，減少嵌套的 if 語句",
                "improved": '''
def process_data(data):
    """篩選符合條件的數據"""
    return [
        item for item in data
        if item.get('status') == 'active'
        and item.get('age', 0) >= 18
        and item.get('verified', False)
    ]
'''
            },
            {
                "type": "使用內建函數",
                "prompt": "重構 calculate_total，使用 Python 內建函數",
                "improved": '''
def calculate_total(items):
    """計算總價"""
    return sum(item['price'] for item in items)
'''
            },
            {
                "type": "提取配置和異常處理",
                "prompt": "重構 send_notification，提取配置並添加異常處理",
                "improved": '''
import smtplib
from email.message import EmailMessage
from dataclasses import dataclass
import logging

@dataclass
class EmailConfig:
    smtp_server: str = 'smtp.gmail.com'
    smtp_port: int = 587
    username: str = ''
    password: str = ''

def send_notification(user: dict, message: str, config: EmailConfig):
    """發送郵件通知"""
    try:
        msg = EmailMessage()
        msg['To'] = user['email']
        msg['From'] = config.username
        msg['Subject'] = 'Notification'
        msg.set_content(message)

        with smtplib.SMTP(config.smtp_server, config.smtp_port) as server:
            server.starttls()
            server.login(config.username, config.password)
            server.send_message(msg)

        logging.info(f"郵件已發送到 {user['email']}")
        return True

    except smtplib.SMTPException as e:
        logging.error(f"發送郵件失敗: {e}")
        return False
'''
            }
        ]

        for task in refactoring_tasks:
            print(f"\n🔧 重構類型: {task['type']}")
            print(f"\n提示詞:")
            print(f"  {task['prompt']}")
            print(f"\n改進後的代碼:")
            print(task['improved'])
            print("-"*70)

    def debugging_examples(self):
        """
        調試輔助示例
        展示如何使用 Goose 幫助調試
        """
        print("\n" + "="*70)
        print("Bug 調試")
        print("="*70)

        # 有問題的代碼
        buggy_code = '''
def calculate_average(numbers):
    total = sum(numbers)
    return total / len(numbers)

def get_user_by_id(user_id):
    users = fetch_users_from_db()
    return users[user_id]

def process_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data['results']
'''

        print("\n有 Bug 的代碼:")
        print("-"*70)
        print(buggy_code)

        debugging_tasks = [
            {
                "issue": "空列表導致除以零",
                "prompt": "修復 calculate_average，處理空列表情況",
                "fix": '''
def calculate_average(numbers: list) -> float:
    """計算平均值，處理空列表"""
    if not numbers:
        raise ValueError("不能計算空列表的平均值")
    return sum(numbers) / len(numbers)

# 或使用默認值
def calculate_average_safe(numbers: list, default: float = 0.0) -> float:
    """安全計算平均值"""
    return sum(numbers) / len(numbers) if numbers else default
'''
            },
            {
                "issue": "KeyError 異常",
                "prompt": "修復 get_user_by_id，處理用戶不存在的情況",
                "fix": '''
def get_user_by_id(user_id: str) -> Optional[dict]:
    """通過 ID 獲取用戶"""
    users = fetch_users_from_db()
    return users.get(user_id)  # 使用 get 方法

# 或拋出自定義異常
class UserNotFoundError(Exception):
    pass

def get_user_by_id_strict(user_id: str) -> dict:
    """通過 ID 獲取用戶（嚴格模式）"""
    users = fetch_users_from_db()
    if user_id not in users:
        raise UserNotFoundError(f"用戶 {user_id} 不存在")
    return users[user_id]
'''
            },
            {
                "issue": "文件和 JSON 錯誤處理",
                "prompt": "修復 process_file，添加完整的錯誤處理",
                "fix": '''
import json
import logging
from pathlib import Path

def process_file(filename: str) -> Optional[list]:
    """處理 JSON 文件"""
    file_path = Path(filename)

    # 檢查文件存在
    if not file_path.exists():
        logging.error(f"文件不存在: {filename}")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 檢查必要的鍵
        if 'results' not in data:
            logging.warning(f"文件 {filename} 缺少 'results' 鍵")
            return None

        return data['results']

    except json.JSONDecodeError as e:
        logging.error(f"JSON 解析錯誤: {e}")
        return None
    except Exception as e:
        logging.error(f"處理文件時發生錯誤: {e}")
        return None
'''
            }
        ]

        for task in debugging_tasks:
            print(f"\n🐛 問題: {task['issue']}")
            print(f"\n提示詞:")
            print(f"  {task['prompt']}")
            print(f"\n修復後的代碼:")
            print(task['fix'])
            print("-"*70)

    def test_generation_examples(self):
        """
        測試生成示例
        展示如何使用 Goose 生成測試
        """
        print("\n" + "="*70)
        print("測試生成")
        print("="*70)

        # 要測試的代碼
        code_to_test = '''
class Calculator:
    """簡單計算器"""

    def add(self, a: float, b: float) -> float:
        """加法"""
        return a + b

    def subtract(self, a: float, b: float) -> float:
        """減法"""
        return a - b

    def multiply(self, a: float, b: float) -> float:
        """乘法"""
        return a * b

    def divide(self, a: float, b: float) -> float:
        """除法"""
        if b == 0:
            raise ValueError("不能除以零")
        return a / b

    def power(self, base: float, exponent: float) -> float:
        """冪運算"""
        return base ** exponent
'''

        print("\n要測試的代碼:")
        print("-"*70)
        print(code_to_test)

        test_examples = [
            {
                "framework": "pytest",
                "prompt": "為 Calculator 類生成 pytest 測試，包括正常情況和邊界情況",
                "test_code": '''
import pytest
from calculator import Calculator

class TestCalculator:
    """Calculator 測試套件"""

    def setup_method(self):
        """測試前設置"""
        self.calc = Calculator()

    def test_add(self):
        """測試加法"""
        assert self.calc.add(2, 3) == 5
        assert self.calc.add(-1, 1) == 0
        assert self.calc.add(0, 0) == 0

    def test_subtract(self):
        """測試減法"""
        assert self.calc.subtract(5, 3) == 2
        assert self.calc.subtract(0, 5) == -5

    def test_multiply(self):
        """測試乘法"""
        assert self.calc.multiply(3, 4) == 12
        assert self.calc.multiply(-2, 3) == -6
        assert self.calc.multiply(0, 100) == 0

    def test_divide(self):
        """測試除法"""
        assert self.calc.divide(10, 2) == 5
        assert self.calc.divide(7, 2) == 3.5

    def test_divide_by_zero(self):
        """測試除以零異常"""
        with pytest.raises(ValueError, match="不能除以零"):
            self.calc.divide(10, 0)

    def test_power(self):
        """測試冪運算"""
        assert self.calc.power(2, 3) == 8
        assert self.calc.power(5, 0) == 1
        assert self.calc.power(4, 0.5) == 2

    @pytest.mark.parametrize("a,b,expected", [
        (1, 1, 2),
        (0, 0, 0),
        (-1, 1, 0),
        (100, 200, 300),
    ])
    def test_add_parametrized(self, a, b, expected):
        """參數化測試加法"""
        assert self.calc.add(a, b) == expected
'''
            },
            {
                "framework": "unittest",
                "prompt": "使用 unittest 框架生成測試",
                "test_code": '''
import unittest
from calculator import Calculator

class TestCalculator(unittest.TestCase):
    """Calculator 單元測試"""

    def setUp(self):
        """測試前設置"""
        self.calc = Calculator()

    def test_add(self):
        """測試加法"""
        self.assertEqual(self.calc.add(2, 3), 5)
        self.assertEqual(self.calc.add(-1, 1), 0)

    def test_divide_by_zero(self):
        """測試除以零"""
        with self.assertRaises(ValueError):
            self.calc.divide(10, 0)

if __name__ == '__main__':
    unittest.main()
'''
            }
        ]

        for example in test_examples:
            print(f"\n🧪 測試框架: {example['framework']}")
            print(f"\n提示詞:")
            print(f"  {example['prompt']}")
            print(f"\n生成的測試代碼:")
            print(example['test_code'])
            print("-"*70)

    def documentation_examples(self):
        """
        文檔生成示例
        展示如何使用 Goose 生成文檔
        """
        print("\n" + "="*70)
        print("文檔生成")
        print("="*70)

        code_without_docs = '''
class UserManager:
    def __init__(self, db_connection):
        self.db = db_connection

    def create_user(self, username, email, password):
        hashed_pw = self._hash_password(password)
        user_id = self.db.insert({
            'username': username,
            'email': email,
            'password': hashed_pw
        })
        return user_id

    def get_user(self, user_id):
        return self.db.get(user_id)

    def update_user(self, user_id, **kwargs):
        return self.db.update(user_id, kwargs)

    def delete_user(self, user_id):
        return self.db.delete(user_id)

    def _hash_password(self, password):
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
'''

        print("\n原始代碼（無文檔）:")
        print("-"*70)
        print(code_without_docs)

        doc_examples = [
            {
                "style": "Google Style",
                "prompt": "為 UserManager 添加 Google 風格的 docstring",
                "documented": '''
class UserManager:
    """用戶管理器，處理用戶的 CRUD 操作

    負責用戶的創建、讀取、更新和刪除操作，
    自動處理密碼哈希。

    Attributes:
        db: 數據庫連接對象
    """

    def __init__(self, db_connection):
        """初始化用戶管理器

        Args:
            db_connection: 數據庫連接對象
        """
        self.db = db_connection

    def create_user(self, username: str, email: str, password: str) -> int:
        """創建新用戶

        Args:
            username: 用戶名
            email: 電子郵件地址
            password: 明文密碼（將被哈希處理）

        Returns:
            int: 新創建用戶的 ID

        Raises:
            ValueError: 如果用戶名或郵箱已存在
            DatabaseError: 如果數據庫操作失敗
        """
        hashed_pw = self._hash_password(password)
        user_id = self.db.insert({
            'username': username,
            'email': email,
            'password': hashed_pw
        })
        return user_id

    def _hash_password(self, password: str) -> str:
        """哈希密碼

        使用 SHA-256 算法哈希密碼

        Args:
            password: 明文密碼

        Returns:
            str: 哈希後的密碼
        """
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
'''
            }
        ]

        for example in doc_examples:
            print(f"\n📚 文檔風格: {example['style']}")
            print(f"\n提示詞:")
            print(f"  {example['prompt']}")
            print(f"\n添加文檔後:")
            print(example['documented'])
            print("-"*70)

        # README 生成
        print("\n📝 README 生成:")
        print("-"*70)
        print("""
提示詞: 為這個項目生成詳細的 README.md

生成內容包括:
- 項目概述
- 功能特性
- 安裝說明
- 使用示例
- API 文檔
- 配置選項
- 貢獻指南
- 許可證信息
        """)

    def practical_workflow(self):
        """實際工作流示例"""
        print("\n" + "="*70)
        print("實際開發工作流")
        print("="*70)

        workflow = [
            {
                "step": 1,
                "task": "創建項目結構",
                "command": 'goose "創建 FastAPI 項目結構，包含 models, routes, services"'
            },
            {
                "step": 2,
                "task": "實現核心功能",
                "command": 'goose "實現用戶註冊和登錄功能"'
            },
            {
                "step": 3,
                "task": "添加測試",
                "command": 'goose "為 auth.py 生成完整的測試套件"'
            },
            {
                "step": 4,
                "task": "運行測試",
                "command": 'goose "運行所有測試並顯示覆蓋率"'
            },
            {
                "step": 5,
                "task": "修復失敗的測試",
                "command": 'goose "分析測試失敗原因並修復"'
            },
            {
                "step": 6,
                "task": "代碼審查",
                "command": 'goose "審查代碼，檢查安全性和最佳實踐"'
            },
            {
                "step": 7,
                "task": "優化性能",
                "command": 'goose "分析性能瓶頸並優化"'
            },
            {
                "step": 8,
                "task": "生成文檔",
                "command": 'goose "生成 API 文檔和 README"'
            },
            {
                "step": 9,
                "task": "準備部署",
                "command": 'goose "創建 Dockerfile 和 docker-compose.yml"'
            }
        ]

        print("\n完整開發流程:")
        for step in workflow:
            print(f"\n步驟 {step['step']}: {step['task']}")
            print(f"  命令: {step['command']}")


def main():
    """主函數"""
    print("="*70)
    print("Goose 開發任務輔助")
    print("="*70)

    demo = DevelopmentTasksDemo()

    sections = [
        ("代碼生成", demo.code_generation_examples),
        ("代碼重構", demo.refactoring_examples),
        ("Bug 調試", demo.debugging_examples),
        ("測試生成", demo.test_generation_examples),
        ("文檔生成", demo.documentation_examples),
        ("實際工作流", demo.practical_workflow),
    ]

    print("\n本教程展示 Goose 在開發任務中的應用\n")

    for i, (name, func) in enumerate(sections, 1):
        print(f"{i}. {name}")

    print("\n執行所有示例...")

    for name, func in sections:
        func()
        print("\n" + "="*70)

    print("\n教程完成！")
    print("\n關鍵要點:")
    print("1. Goose 可以生成各種類型的代碼")
    print("2. 使用 Goose 重構可以提高代碼質量")
    print("3. Goose 能幫助快速定位和修復 Bug")
    print("4. 自動生成測試可以節省大量時間")
    print("5. 文檔生成確保代碼可維護性")
    print("\n下一步: 閱讀 04_代碼審查.py")


if __name__ == "__main__":
    main()
