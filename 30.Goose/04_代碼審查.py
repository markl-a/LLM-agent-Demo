#!/usr/bin/env python3
"""
Goose 代碼審查示例

展示如何使用 Goose 進行代碼審查:
1. 自動代碼審查
2. 安全性檢查
3. 性能分析
4. 代碼風格檢查
5. 最佳實踐建議

作者: AI Agent
日期: 2024
"""

from typing import List, Dict
from dataclasses import dataclass


@dataclass
class ReviewIssue:
    """審查發現的問題"""
    severity: str  # critical, high, medium, low
    category: str  # security, performance, style, best_practice
    file: str
    line: int
    message: str
    suggestion: str


class CodeReviewDemo:
    """代碼審查演示"""

    def __init__(self):
        """初始化"""
        self.issues = []

    def security_review(self):
        """
        安全性審查示例
        檢查常見的安全漏洞
        """
        print("\n" + "="*70)
        print("安全性審查")
        print("="*70)

        # 有安全問題的代碼示例
        vulnerable_code = '''
# 1. SQL 注入風險
def get_user(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)

# 2. 硬編碼密鑰
API_KEY = "sk-1234567890abcdef"
SECRET_KEY = "my-secret-key-123"

# 3. 不安全的密碼哈希
import hashlib
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# 4. 使用 eval（代碼注入風險）
def calculate(expression):
    return eval(expression)

# 5. 不驗證文件路徑
def read_file(filename):
    with open(f"/data/{filename}", 'r') as f:
        return f.read()
'''

        print("\n❌ 有安全問題的代碼:")
        print("-"*70)
        print(vulnerable_code)

        # Goose 審查建議
        security_issues = [
            {
                "issue": "SQL 注入風險",
                "line": "2-3",
                "severity": "critical",
                "description": "直接拼接用戶輸入到 SQL 查詢",
                "fix": '''
# ✅ 使用參數化查詢
def get_user(username):
    query = "SELECT * FROM users WHERE username = ?"
    return db.execute(query, (username,))

# 或使用 ORM
def get_user_orm(username):
    return User.query.filter_by(username=username).first()
'''
            },
            {
                "issue": "硬編碼密鑰",
                "line": "6-7",
                "severity": "critical",
                "description": "敏感信息不應硬編碼在源碼中",
                "fix": '''
# ✅ 使用環境變量
import os
API_KEY = os.getenv('API_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')

# 或使用配置文件（不提交到版本控制）
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv('API_KEY')
'''
            },
            {
                "issue": "不安全的哈希算法",
                "line": "10-12",
                "severity": "high",
                "description": "MD5 已被破解，不適合密碼哈希",
                "fix": '''
# ✅ 使用專門的密碼哈希庫
import bcrypt

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

# 或使用 argon2
from argon2 import PasswordHasher
ph = PasswordHasher()
hashed = ph.hash(password)
'''
            },
            {
                "issue": "代碼注入風險",
                "line": "15-16",
                "severity": "critical",
                "description": "eval() 可以執行任意代碼",
                "fix": '''
# ✅ 使用安全的替代方案
import ast
import operator

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

def safe_eval(expression):
    """安全地計算數學表達式"""
    tree = ast.parse(expression, mode='eval')
    # 只允許數學運算
    return _eval_node(tree.body)
'''
            },
            {
                "issue": "路徑遍歷漏洞",
                "line": "19-21",
                "severity": "high",
                "description": "未驗證文件路徑可能導致訪問任意文件",
                "fix": '''
# ✅ 驗證和規範化路徑
from pathlib import Path

def read_file(filename):
    # 規範化路徑
    safe_path = Path("/data").resolve()
    file_path = (safe_path / filename).resolve()

    # 確保文件在允許的目錄內
    if not str(file_path).startswith(str(safe_path)):
        raise ValueError("非法文件路徑")

    with open(file_path, 'r') as f:
        return f.read()
'''
            }
        ]

        for issue in security_issues:
            print(f"\n🔒 {issue['issue']}")
            print(f"   行數: {issue['line']}")
            print(f"   嚴重性: {issue['severity']}")
            print(f"   問題: {issue['description']}")
            print(f"\n   修復方案:")
            print(issue['fix'])
            print("-"*70)

    def performance_review(self):
        """
        性能分析示例
        識別性能瓶頸
        """
        print("\n" + "="*70)
        print("性能分析")
        print("="*70)

        # 性能不佳的代碼
        slow_code = '''
# 1. N+1 查詢問題
def get_user_posts(user_ids):
    posts = []
    for user_id in user_ids:
        user_posts = db.query(f"SELECT * FROM posts WHERE user_id={user_id}")
        posts.extend(user_posts)
    return posts

# 2. 不必要的重複計算
def process_items(items):
    results = []
    for item in items:
        if expensive_calculation(item) > 100:
            value = expensive_calculation(item) * 2
            results.append(value)
    return results

# 3. 大數據載入到記憶體
def analyze_log_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()  # 載入整個文件
    return [line for line in lines if 'ERROR' in line]

# 4. 字符串拼接
def build_html(items):
    html = ""
    for item in items:
        html += f"<li>{item}</li>"
    return html
'''

        print("\n⚠️ 性能不佳的代碼:")
        print("-"*70)
        print(slow_code)

        performance_issues = [
            {
                "issue": "N+1 查詢問題",
                "impact": "高",
                "description": "每個用戶執行一次查詢，1000 個用戶 = 1000 次查詢",
                "fix": '''
# ✅ 使用批量查詢
def get_user_posts(user_ids):
    # 一次查詢獲取所有數據
    query = "SELECT * FROM posts WHERE user_id IN (?)"
    placeholders = ','.join('?' * len(user_ids))
    return db.query(query.replace('?', placeholders), user_ids)

# 使用 ORM
def get_user_posts_orm(user_ids):
    return Post.query.filter(Post.user_id.in_(user_ids)).all()
'''
            },
            {
                "issue": "重複計算",
                "impact": "中",
                "description": "同一個值計算了兩次",
                "fix": '''
# ✅ 緩存計算結果
def process_items(items):
    results = []
    for item in items:
        calc_result = expensive_calculation(item)  # 只計算一次
        if calc_result > 100:
            results.append(calc_result * 2)
    return results

# 使用列表推導式
def process_items_v2(items):
    return [
        calc * 2
        for item in items
        if (calc := expensive_calculation(item)) > 100
    ]
'''
            },
            {
                "issue": "記憶體過度使用",
                "impact": "高",
                "description": "大文件會耗盡記憶體",
                "fix": '''
# ✅ 流式處理
def analyze_log_file(filename):
    errors = []
    with open(filename, 'r') as f:
        for line in f:  # 逐行讀取
            if 'ERROR' in line:
                errors.append(line.strip())
    return errors

# 使用生成器（更節省記憶體）
def analyze_log_file_gen(filename):
    with open(filename, 'r') as f:
        for line in f:
            if 'ERROR' in line:
                yield line.strip()
'''
            },
            {
                "issue": "低效的字符串拼接",
                "impact": "中",
                "description": "字符串拼接會創建多個臨時對象",
                "fix": '''
# ✅ 使用 join
def build_html(items):
    return ''.join(f"<li>{item}</li>" for item in items)

# 或使用列表
def build_html_v2(items):
    parts = [f"<li>{item}</li>" for item in items]
    return ''.join(parts)
'''
            }
        ]

        for issue in performance_issues:
            print(f"\n⚡ {issue['issue']}")
            print(f"   影響: {issue['impact']}")
            print(f"   問題: {issue['description']}")
            print(f"\n   優化方案:")
            print(issue['fix'])
            print("-"*70)

    def code_style_review(self):
        """
        代碼風格檢查
        符合 PEP 8 和最佳實踐
        """
        print("\n" + "="*70)
        print("代碼風格檢查")
        print("="*70)

        # 風格不佳的代碼
        bad_style = '''
# 命名不規範
def GetUserData(UserID):
    user_data=db.get(UserID)
    return user_data

# 過長的行
def process_data(data, option1, option2, option3, option4, option5, option6, option7, option8):
    return some_function(data, option1, option2, option3, option4, option5, option6, option7, option8)

# 缺少類型提示
def calculate(x, y):
    return x + y

# 魔術數字
def calculate_price(quantity):
    if quantity > 100:
        return quantity * 9.99 * 0.9
    return quantity * 9.99
'''

        print("\n❌ 風格不佳的代碼:")
        print("-"*70)
        print(bad_style)

        style_improvements = [
            {
                "issue": "命名規範",
                "pep8": "函數名使用 snake_case，參數名小寫",
                "fix": '''
# ✅ 正確的命名
def get_user_data(user_id: int) -> dict:
    """獲取用戶數據"""
    user_data = db.get(user_id)
    return user_data
'''
            },
            {
                "issue": "行長度",
                "pep8": "每行不超過 79 字符",
                "fix": '''
# ✅ 適當換行
def process_data(
    data: dict,
    option1: str,
    option2: str,
    option3: str,
    option4: str,
    option5: str,
) -> dict:
    return some_function(
        data,
        option1, option2,
        option3, option4,
        option5
    )
'''
            },
            {
                "issue": "類型提示",
                "pep8": "使用類型提示提高可讀性",
                "fix": '''
# ✅ 添加類型提示
from typing import Union

def calculate(x: Union[int, float], y: Union[int, float]) -> float:
    """計算兩數之和"""
    return x + y
'''
            },
            {
                "issue": "魔術數字",
                "pep8": "使用常量替代魔術數字",
                "fix": '''
# ✅ 使用命名常量
UNIT_PRICE = 9.99
BULK_DISCOUNT = 0.9
BULK_THRESHOLD = 100

def calculate_price(quantity: int) -> float:
    """計算總價"""
    total = quantity * UNIT_PRICE

    if quantity > BULK_THRESHOLD:
        total *= BULK_DISCOUNT

    return total
'''
            }
        ]

        for improvement in style_improvements:
            print(f"\n📝 {improvement['issue']}")
            print(f"   PEP 8: {improvement['pep8']}")
            print(f"\n   改進:")
            print(improvement['fix'])
            print("-"*70)

    def best_practices_review(self):
        """
        最佳實踐建議
        """
        print("\n" + "="*70)
        print("最佳實踐建議")
        print("="*70)

        practices = [
            {
                "category": "錯誤處理",
                "bad": '''
def get_config():
    with open('config.json') as f:
        return json.load(f)
''',
                "good": '''
def get_config() -> dict:
    """載入配置文件"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("配置文件不存在")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"配置文件格式錯誤: {e}")
        return {}
'''
            },
            {
                "category": "資源管理",
                "bad": '''
def write_log(message):
    f = open('log.txt', 'a')
    f.write(message)
    f.close()
''',
                "good": '''
from pathlib import Path
from contextlib import contextmanager

def write_log(message: str) -> None:
    """寫入日誌"""
    log_file = Path('log.txt')
    with log_file.open('a', encoding='utf-8') as f:
        f.write(f"{message}\\n")

# 或使用 logging 模塊
import logging
logger = logging.getLogger(__name__)
logger.info(message)
'''
            },
            {
                "category": "默認參數",
                "bad": '''
def add_item(item, items=[]):
    items.append(item)
    return items
''',
                "good": '''
def add_item(item: str, items: list = None) -> list:
    """添加項目到列表"""
    if items is None:
        items = []
    items.append(item)
    return items

# 或使用不可變默認值
from typing import List, Optional

def add_item_v2(item: str, items: Optional[List[str]] = None) -> List[str]:
    """添加項目到列表"""
    items = items or []
    return [*items, item]  # 返回新列表
'''
            },
            {
                "category": "文檔字符串",
                "bad": '''
def process(data, mode):
    # 處理數據
    return result
''',
                "good": '''
def process(data: dict, mode: str = 'default') -> dict:
    """處理數據

    根據指定模式處理輸入數據。

    Args:
        data: 要處理的數據字典
        mode: 處理模式，可選值: 'default', 'strict', 'lenient'

    Returns:
        處理後的數據字典

    Raises:
        ValueError: 如果模式無效
        KeyError: 如果數據缺少必要的鍵

    Example:
        >>> process({'name': 'test'}, mode='strict')
        {'name': 'TEST', 'processed': True}
    """
    # 實現邏輯
    return result
'''
            }
        ]

        for practice in practices:
            print(f"\n💡 {practice['category']}")
            print("\n   ❌ 不好的做法:")
            print(practice['bad'])
            print("\n   ✅ 推薦做法:")
            print(practice['good'])
            print("-"*70)

    def goose_review_workflow(self):
        """
        使用 Goose 進行代碼審查的工作流
        """
        print("\n" + "="*70)
        print("Goose 代碼審查工作流")
        print("="*70)

        workflow = [
            {
                "step": "1. 審查單個文件",
                "command": 'goose "審查 src/auth.py，關注安全性和性能"',
                "output": "檢查 SQL 注入、XSS、性能瓶頸等"
            },
            {
                "step": "2. 審查整個目錄",
                "command": 'goose "審查 src/ 目錄下所有 Python 文件"',
                "output": "批量檢查代碼質量"
            },
            {
                "step": "3. 檢查特定問題",
                "command": 'goose "檢查項目中的硬編碼密鑰和密碼"',
                "output": "掃描敏感信息洩露"
            },
            {
                "step": "4. 風格檢查",
                "command": 'goose "檢查代碼是否符合 PEP 8"',
                "output": "代碼風格規範性檢查"
            },
            {
                "step": "5. 最佳實踐",
                "command": 'goose "檢查是否遵循 Python 最佳實踐"',
                "output": "設計模式、慣用法檢查"
            },
            {
                "step": "6. 生成審查報告",
                "command": 'goose "生成完整的代碼審查報告，包括所有發現的問題"',
                "output": "Markdown 格式的詳細報告"
            }
        ]

        for item in workflow:
            print(f"\n{item['step']}")
            print(f"   命令: {item['command']}")
            print(f"   輸出: {item['output']}")

    def review_checklist(self):
        """代碼審查檢查清單"""
        print("\n" + "="*70)
        print("代碼審查檢查清單")
        print("="*70)

        checklist = {
            "安全性": [
                "無 SQL 注入風險",
                "無 XSS 漏洞",
                "無硬編碼密鑰",
                "使用安全的密碼哈希",
                "輸入驗證完整",
                "輸出編碼正確",
                "文件路徑驗證"
            ],
            "性能": [
                "無 N+1 查詢",
                "適當使用緩存",
                "避免不必要的計算",
                "使用生成器處理大數據",
                "數據庫查詢優化",
                "並發處理得當"
            ],
            "代碼質量": [
                "符合 PEP 8",
                "有類型提示",
                "有文檔字符串",
                "命名清晰",
                "函數職責單一",
                "避免魔術數字",
                "適當的註釋"
            ],
            "錯誤處理": [
                "適當的異常處理",
                "錯誤信息清晰",
                "資源正確釋放",
                "日誌記錄完整"
            ],
            "測試": [
                "有單元測試",
                "測試覆蓋率足夠",
                "測試案例完整",
                "邊界條件測試"
            ]
        }

        for category, items in checklist.items():
            print(f"\n📋 {category}:")
            for item in items:
                print(f"   □ {item}")


def main():
    """主函數"""
    print("="*70)
    print("Goose 代碼審查教程")
    print("="*70)

    demo = CodeReviewDemo()

    sections = [
        ("安全性審查", demo.security_review),
        ("性能分析", demo.performance_review),
        ("代碼風格", demo.code_style_review),
        ("最佳實踐", demo.best_practices_review),
        ("審查工作流", demo.goose_review_workflow),
        ("審查清單", demo.review_checklist),
    ]

    print("\n執行所有示例...\n")

    for name, func in sections:
        func()

    print("\n" + "="*70)
    print("教程完成！")
    print("="*70)

    print("\n關鍵要點:")
    print("1. 使用 Goose 自動檢測安全漏洞")
    print("2. 識別性能瓶頸並優化")
    print("3. 確保代碼符合風格規範")
    print("4. 遵循最佳實踐")
    print("5. 定期進行代碼審查")

    print("\n下一步: 閱讀 05_自定義工具.py")


if __name__ == "__main__":
    main()
