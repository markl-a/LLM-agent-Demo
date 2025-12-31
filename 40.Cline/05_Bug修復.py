"""
Cline Bug 修復示例

展示如何使用 Cline 自動修復 Bug：
1. 識別常見錯誤
2. 修復邏輯錯誤
3. 修復語法錯誤
4. 修復運行時錯誤
5. 添加錯誤處理
6. 修復安全漏洞

自動化 Bug 修復可以大大提高開發效率。
"""

import os
from typing import Dict, List, Any, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class ClineBugFixer:
    """Cline Bug 修復工具"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化 Bug 修復工具"""
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

    def fix_syntax_error(self, code: str, error_message: str) -> str:
        """
        修復語法錯誤

        Args:
            code: 有錯誤的代碼
            error_message: 錯誤信息

        Returns:
            修復後的代碼
        """
        prompt = f"""
        以下代碼有語法錯誤：

        錯誤信息:
        {error_message}

        代碼:
        ```
        {code}
        ```

        請修復語法錯誤，並解釋修復內容。
        """

        system = "你是一個專業的調試專家，擅長快速識別和修復代碼錯誤。"

        return self._call_claude(prompt, system)

    def fix_logic_error(self, code: str, expected_behavior: str, actual_behavior: str) -> str:
        """
        修復邏輯錯誤

        Args:
            code: 有錯誤的代碼
            expected_behavior: 期望行為
            actual_behavior: 實際行為

        Returns:
            修復後的代碼
        """
        prompt = f"""
        以下代碼有邏輯錯誤：

        期望行為:
        {expected_behavior}

        實際行為:
        {actual_behavior}

        代碼:
        ```
        {code}
        ```

        請:
        1. 找出邏輯錯誤
        2. 修復錯誤
        3. 解釋錯誤原因
        4. 添加測試用例確保修復正確
        """

        return self._call_claude(prompt)

    def fix_runtime_error(self, code: str, traceback: str) -> str:
        """
        修復運行時錯誤

        Args:
            code: 有錯誤的代碼
            traceback: 錯誤堆棧信息

        Returns:
            修復後的代碼
        """
        prompt = f"""
        以下代碼在運行時出錯：

        錯誤堆棧:
        {traceback}

        代碼:
        ```
        {code}
        ```

        請:
        1. 分析錯誤原因
        2. 修復錯誤
        3. 添加適當的錯誤處理
        4. 防止類似錯誤再次發生
        """

        return self._call_claude(prompt)

    def add_error_handling(self, code: str) -> str:
        """
        添加錯誤處理

        Args:
            code: 原始代碼

        Returns:
            添加錯誤處理後的代碼
        """
        prompt = f"""
        請為以下代碼添加適當的錯誤處理：

        ```
        {code}
        ```

        要求:
        1. 識別可能的錯誤點
        2. 添加 try-except 塊
        3. 提供有意義的錯誤信息
        4. 處理邊界情況
        5. 使用日誌記錄錯誤
        """

        return self._call_claude(prompt)

    def fix_security_vulnerability(self, code: str, vulnerability_type: str = None) -> str:
        """
        修復安全漏洞

        Args:
            code: 有漏洞的代碼
            vulnerability_type: 漏洞類型（可選）

        Returns:
            修復後的代碼
        """
        vuln_info = f"\n已知漏洞類型: {vulnerability_type}" if vulnerability_type else ""

        prompt = f"""
        請分析並修復以下代碼中的安全漏洞：
        {vuln_info}

        代碼:
        ```
        {code}
        ```

        請檢查:
        1. SQL 注入
        2. XSS 攻擊
        3. 命令注入
        4. 路徑遍歷
        5. 不安全的反序列化
        6. 硬編碼憑證

        請修復發現的漏洞，並解釋修復方案。
        """

        return self._call_claude(prompt)

    def fix_performance_bug(self, code: str, performance_issue: str) -> str:
        """
        修復性能問題

        Args:
            code: 有性能問題的代碼
            performance_issue: 性能問題描述

        Returns:
            修復後的代碼
        """
        prompt = f"""
        以下代碼有性能問題：

        問題描述:
        {performance_issue}

        代碼:
        ```
        {code}
        ```

        請:
        1. 識別性能瓶頸
        2. 優化算法或數據結構
        3. 減少不必要的操作
        4. 保持功能完整性
        """

        return self._call_claude(prompt)

    def fix_memory_leak(self, code: str) -> str:
        """
        修復內存洩漏

        Args:
            code: 可能有內存洩漏的代碼

        Returns:
            修復後的代碼
        """
        prompt = f"""
        請檢查並修復以下代碼中的內存洩漏問題：

        ```
        {code}
        ```

        請檢查:
        1. 未釋放的資源
        2. 循環引用
        3. 事件監聽器未移除
        4. 緩存無限增長

        請修復發現的問題。
        """

        return self._call_claude(prompt)

    def fix_concurrency_bug(self, code: str, issue_description: str) -> str:
        """
        修復並發問題

        Args:
            code: 有並發問題的代碼
            issue_description: 問題描述

        Returns:
            修復後的代碼
        """
        prompt = f"""
        以下代碼有並發問題：

        問題描述:
        {issue_description}

        代碼:
        ```
        {code}
        ```

        請:
        1. 識別競態條件
        2. 添加適當的同步機制
        3. 避免死鎖
        4. 使用線程安全的數據結構
        """

        return self._call_claude(prompt)


def example_fix_syntax_error():
    """示例 1: 修復語法錯誤"""
    print("=" * 60)
    print("示例 1: 修復語法錯誤")
    print("=" * 60)

    fixer = ClineBugFixer()

    # 有語法錯誤的代碼
    buggy_code = """
def calculate_total(items):
    total = 0
    for item in items
        total += item['price'] * item['quantity']
    return total

result = calculate_total([
    {'price': 10, 'quantity': 2},
    {'price': 15, 'quantity': 1}
)
    """

    error_msg = "SyntaxError: invalid syntax (line 3)"

    print("\n有錯誤的代碼:")
    print(buggy_code)
    print(f"\n錯誤信息: {error_msg}")

    fixed_code = fixer.fix_syntax_error(buggy_code, error_msg)

    print("\n修復後的代碼:")
    print(fixed_code)


def example_fix_logic_error():
    """示例 2: 修復邏輯錯誤"""
    print("\n" + "=" * 60)
    print("示例 2: 修復邏輯錯誤")
    print("=" * 60)

    fixer = ClineBugFixer()

    # 有邏輯錯誤的代碼
    buggy_code = """
def is_palindrome(text):
    '''檢查字符串是否為回文'''
    text = text.lower().replace(' ', '')
    for i in range(len(text)):
        if text[i] != text[len(text) - i]:
            return False
    return True

# 測試
print(is_palindrome("A man a plan a canal Panama"))  # 應該返回 True
    """

    expected = "對於回文字符串 'A man a plan a canal Panama'，應該返回 True"
    actual = "返回 False 或出錯"

    print("\n有錯誤的代碼:")
    print(buggy_code)
    print(f"\n期望: {expected}")
    print(f"實際: {actual}")

    fixed_code = fixer.fix_logic_error(buggy_code, expected, actual)

    print("\n修復後的代碼:")
    print(fixed_code)


def example_fix_runtime_error():
    """示例 3: 修復運行時錯誤"""
    print("\n" + "=" * 60)
    print("示例 3: 修復運行時錯誤")
    print("=" * 60)

    fixer = ClineBugFixer()

    # 會產生運行時錯誤的代碼
    buggy_code = """
def get_average(numbers):
    total = sum(numbers)
    average = total / len(numbers)
    return average

def process_data(data):
    results = []
    for item in data:
        avg = get_average(item['values'])
        results.append({
            'name': item['name'],
            'average': avg
        })
    return results

# 測試
data = [
    {'name': 'A', 'values': [1, 2, 3]},
    {'name': 'B', 'values': []},  # 這會導致除零錯誤
    {'name': 'C', 'values': [4, 5, 6]}
]
print(process_data(data))
    """

    traceback_msg = """
Traceback (most recent call last):
  File "test.py", line 20, in <module>
    print(process_data(data))
  File "test.py", line 11, in process_data
    avg = get_average(item['values'])
  File "test.py", line 3, in get_average
    average = total / len(numbers)
ZeroDivisionError: division by zero
    """

    print("\n有錯誤的代碼:")
    print(buggy_code)
    print("\n錯誤堆棧:")
    print(traceback_msg)

    fixed_code = fixer.fix_runtime_error(buggy_code, traceback_msg)

    print("\n修復後的代碼:")
    print(fixed_code)


def example_add_error_handling():
    """示例 4: 添加錯誤處理"""
    print("\n" + "=" * 60)
    print("示例 4: 添加錯誤處理")
    print("=" * 60)

    fixer = ClineBugFixer()

    # 缺少錯誤處理的代碼
    code = """
import json
import requests

def fetch_user_data(user_id):
    response = requests.get(f'https://api.example.com/users/{user_id}')
    data = response.json()
    return data

def save_to_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)

def process_user(user_id):
    user_data = fetch_user_data(user_id)
    save_to_file(user_data, f'user_{user_id}.json')
    print(f"User {user_id} processed successfully")
    """

    print("\n原始代碼（缺少錯誤處理）:")
    print(code)

    enhanced_code = fixer.add_error_handling(code)

    print("\n添加錯誤處理後的代碼:")
    print(enhanced_code)


def example_fix_security_vulnerability():
    """示例 5: 修復安全漏洞"""
    print("\n" + "=" * 60)
    print("示例 5: 修復安全漏洞")
    print("=" * 60)

    fixer = ClineBugFixer()

    # 有安全漏洞的代碼
    vulnerable_code = """
import sqlite3
from flask import Flask, request

app = Flask(__name__)

@app.route('/user')
def get_user():
    user_id = request.args.get('id')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # SQL 注入漏洞
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)

    result = cursor.fetchone()
    conn.close()
    return str(result)

@app.route('/search')
def search():
    keyword = request.args.get('q')
    # XSS 漏洞
    return f"<h1>Search results for: {keyword}</h1>"

# 硬編碼憑證
DATABASE_PASSWORD = "admin123"
API_KEY = "sk-1234567890abcdef"
    """

    print("\n有安全漏洞的代碼:")
    print(vulnerable_code)

    fixed_code = fixer.fix_security_vulnerability(vulnerable_code)

    print("\n修復後的代碼:")
    print(fixed_code)


def example_fix_performance_bug():
    """示例 6: 修復性能問題"""
    print("\n" + "=" * 60)
    print("示例 6: 修復性能問題")
    print("=" * 60)

    fixer = ClineBugFixer()

    # 有性能問題的代碼
    slow_code = """
def find_duplicates(numbers):
    duplicates = []
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            if numbers[i] == numbers[j]:
                if numbers[i] not in duplicates:
                    duplicates.append(numbers[i])
    return duplicates

def process_large_dataset(data):
    results = []
    for item in data:
        # 每次都重新計算
        if item['value'] > sum(data) / len(data):
            results.append(item)
    return results
    """

    performance_issue = "處理大數據集時非常慢，O(n²) 複雜度"

    print("\n有性能問題的代碼:")
    print(slow_code)
    print(f"\n性能問題: {performance_issue}")

    optimized_code = fixer.fix_performance_bug(slow_code, performance_issue)

    print("\n優化後的代碼:")
    print(optimized_code)


def example_fix_concurrency_bug():
    """示例 7: 修復並發問題"""
    print("\n" + "=" * 60)
    print("示例 7: 修復並發問題")
    print("=" * 60)

    fixer = ClineBugFixer()

    # 有並發問題的代碼
    concurrent_bug = """
import threading

class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        # 競態條件：讀取-修改-寫入不是原子操作
        current = self.count
        self.count = current + 1

    def get_count(self):
        return self.count

# 使用示例
counter = Counter()
threads = []

for i in range(10):
    t = threading.Thread(target=lambda: [counter.increment() for _ in range(1000)])
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# 期望: 10000, 實際: 可能小於 10000
print(f"Count: {counter.get_count()}")
    """

    issue_desc = "多線程環境下，counter.increment() 存在競態條件，導致計數不準確"

    print("\n有並發問題的代碼:")
    print(concurrent_bug)
    print(f"\n問題描述: {issue_desc}")

    fixed_code = fixer.fix_concurrency_bug(concurrent_bug, issue_desc)

    print("\n修復後的代碼:")
    print(fixed_code)


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Cline Bug 修復示例")
    print("=" * 60)

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠️  警告: 未設置 ANTHROPIC_API_KEY")
        return

    try:
        # 運行示例（注釋以節省 API 調用）
        # example_fix_syntax_error()
        # example_fix_logic_error()
        # example_fix_runtime_error()
        # example_add_error_handling()
        # example_fix_security_vulnerability()
        # example_fix_performance_bug()
        # example_fix_concurrency_bug()

        print("\n✅ Bug 修復示例已準備就緒")
        print("\n💡 提示:")
        print("1. 使用 fix_syntax_error() 快速修復語法錯誤")
        print("2. 使用 fix_logic_error() 修復邏輯問題")
        print("3. 使用 add_error_handling() 增強代碼健壯性")
        print("4. 使用 fix_security_vulnerability() 提高安全性")
        print("5. 使用 fix_performance_bug() 優化性能")

        print("\n⚠️  重要提示:")
        print("- AI 修復的代碼應該經過人工審查")
        print("- 運行測試確保修復正確")
        print("- 理解錯誤原因，避免重複犯錯")

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
