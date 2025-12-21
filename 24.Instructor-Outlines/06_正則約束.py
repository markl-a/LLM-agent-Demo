"""
Outlines 正則約束範例
====================

本範例展示如何使用正則表達式約束 LLM 輸出。

正則約束類型：
1. 簡單模式匹配
2. 複雜格式驗證
3. 自定義語法
4. 組合約束

安裝依賴：
pip install outlines
"""

import outlines
from typing import List, Dict, Any, Optional
import re

# ============================================================
# 1. 基本正則模式
# ============================================================

# 常用正則模式
PATTERNS = {
    # 數字格式
    "integer": r"-?\d+",
    "float": r"-?\d+\.?\d*",
    "positive_int": r"[1-9]\d*",

    # 日期時間
    "date_iso": r"\d{4}-\d{2}-\d{2}",
    "date_tw": r"\d{4}/\d{2}/\d{2}",
    "time_24h": r"[0-2]\d:[0-5]\d",
    "datetime": r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",

    # 聯繫方式
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "phone_tw": r"09\d{8}",
    "phone_intl": r"\+\d{1,3}-\d{1,14}",

    # 網絡
    "url": r"https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}[/\w.-]*",
    "ip_v4": r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",

    # 識別碼
    "uuid": r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    "hex_color": r"#[0-9a-fA-F]{6}",
}


BASIC_REGEX_EXAMPLE = '''
import outlines

model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")

# 電子郵件
email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
email_generator = outlines.generate.regex(model, email_pattern)

email = email_generator("公司聯繫郵箱是：")
print(f"郵箱: {email}")

# 日期
date_pattern = r"\d{4}-\d{2}-\d{2}"
date_generator = outlines.generate.regex(model, date_pattern)

date = date_generator("會議日期：")
print(f"日期: {date}")

# 電話
phone_pattern = r"09\d{8}"
phone_generator = outlines.generate.regex(model, phone_pattern)

phone = phone_generator("手機號碼：")
print(f"電話: {phone}")
'''


# ============================================================
# 2. 複雜格式約束
# ============================================================

COMPLEX_REGEX_EXAMPLE = '''
import outlines

model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")

# 信用卡號碼（簡化版）
card_pattern = r"\d{4}-\d{4}-\d{4}-\d{4}"
card_generator = outlines.generate.regex(model, card_pattern)

# 台灣身分證字號格式
id_pattern = r"[A-Z][12]\d{8}"
id_generator = outlines.generate.regex(model, id_pattern)

# 車牌號碼
plate_pattern = r"[A-Z]{2,3}-\d{4}"
plate_generator = outlines.generate.regex(model, plate_pattern)

# MAC 地址
mac_pattern = r"([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}"
mac_generator = outlines.generate.regex(model, mac_pattern)
'''


# ============================================================
# 3. 數值範圍約束
# ============================================================

class NumericConstraints:
    """數值約束生成器"""

    @staticmethod
    def integer_range(min_val: int, max_val: int) -> str:
        """生成指定範圍的整數正則"""
        # 簡化版本，實際應用可能需要更複雜的處理
        if min_val >= 0 and max_val <= 9:
            return f"[{min_val}-{max_val}]"
        elif min_val >= 0 and max_val <= 99:
            return f"[1-9]?\\d|{max_val}"
        else:
            # 簡單處理：允許所有數字，後續驗證
            return r"-?\d+"

    @staticmethod
    def decimal(precision: int = 2) -> str:
        """生成指定精度的小數正則"""
        return rf"-?\d+\.\d{{{precision}}}"

    @staticmethod
    def percentage() -> str:
        """百分比（0-100）"""
        return r"(?:100|[1-9]?\d)%"


NUMERIC_EXAMPLE = '''
import outlines

model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")

# 分數（0-100）
score_pattern = r"(?:100|[1-9]?\d)"
score_generator = outlines.generate.regex(model, score_pattern)

score = score_generator("學生的考試成績是：")
print(f"分數: {score}")

# 價格
price_pattern = r"\d+\.\d{2}"
price_generator = outlines.generate.regex(model, price_pattern)

price = price_generator("商品價格：$")
print(f"價格: ${price}")

# 概率
prob_pattern = r"0\.\d{1,4}|1\.0{1,4}"
prob_generator = outlines.generate.regex(model, prob_pattern)

prob = prob_generator("成功概率：")
print(f"概率: {prob}")
'''


# ============================================================
# 4. 結構化文本約束
# ============================================================

STRUCTURED_TEXT_EXAMPLE = '''
import outlines

model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")

# JSON 對象（簡化）
json_pattern = r'\{"name": "[^"]+", "age": \d+\}'
json_generator = outlines.generate.regex(model, json_pattern)

result = json_generator("生成用戶資料：")
print(f"JSON: {result}")

# 列表格式
list_pattern = r'\[("[^"]+"(?:, "[^"]+")*)\]'
list_generator = outlines.generate.regex(model, list_pattern)

result = list_generator("列出三種水果：")
print(f"列表: {result}")

# 鍵值對
kv_pattern = r"[a-zA-Z]+: [a-zA-Z0-9]+"
kv_generator = outlines.generate.regex(model, kv_pattern)

result = kv_generator("狀態：")
print(f"鍵值對: {result}")
'''


# ============================================================
# 5. 自定義語法
# ============================================================

class GrammarBuilder:
    """語法構建器"""

    def __init__(self):
        self.rules = {}

    def add_rule(self, name: str, pattern: str):
        """添加規則"""
        self.rules[name] = pattern
        return self

    def build_pattern(self, start_rule: str) -> str:
        """構建最終模式"""
        pattern = self.rules.get(start_rule, "")

        # 替換引用的規則
        for name, rule in self.rules.items():
            pattern = pattern.replace(f"<{name}>", f"({rule})")

        return pattern


GRAMMAR_EXAMPLE = '''
# 自定義語法示例

# 定義 SQL SELECT 語句語法
sql_select_pattern = r"SELECT [a-zA-Z_]+(, [a-zA-Z_]+)* FROM [a-zA-Z_]+"

# 定義函數調用語法
func_call_pattern = r"[a-zA-Z_]+\([^)]*\)"

# 定義表達式語法
expr_pattern = r"\d+(\s*[+\-*/]\s*\d+)*"

# 使用
import outlines

model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")

sql_generator = outlines.generate.regex(model, sql_select_pattern)
result = sql_generator("查詢用戶表：")
print(f"SQL: {result}")
'''


# ============================================================
# 6. 組合約束
# ============================================================

class CombinedConstraint:
    """組合約束"""

    @staticmethod
    def union(*patterns: str) -> str:
        """聯合多個模式（OR）"""
        return "(" + "|".join(f"({p})" for p in patterns) + ")"

    @staticmethod
    def sequence(*patterns: str, separator: str = "") -> str:
        """序列模式"""
        return separator.join(f"({p})" for p in patterns)

    @staticmethod
    def repeat(pattern: str, min_count: int = 1, max_count: int = None) -> str:
        """重複模式"""
        if max_count is None:
            if min_count == 0:
                return f"({pattern})*"
            elif min_count == 1:
                return f"({pattern})+"
            else:
                return f"({pattern}){{{min_count},}}"
        else:
            return f"({pattern}){{{min_count},{max_count}}}"

    @staticmethod
    def optional(pattern: str) -> str:
        """可選模式"""
        return f"({pattern})?"


COMBINED_EXAMPLE = '''
import outlines

model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")

# 組合：地址格式
# 格式：城市, 區域, 街道 號碼
address_pattern = r"[\\u4e00-\\u9fff]+市, [\\u4e00-\\u9fff]+區, [\\u4e00-\\u9fff]+路 \\d+號"

# 組合：完整日期時間
datetime_pattern = r"\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}"

# 組合：帶單位的數值
value_with_unit = r"\\d+(\\.\\d+)? (kg|g|lb|oz|m|cm|km)"

# 使用
generator = outlines.generate.regex(model, value_with_unit)
result = generator("產品重量：")
print(f"重量: {result}")
'''


# ============================================================
# 7. 驗證和測試
# ============================================================

class PatternValidator:
    """模式驗證器"""

    def __init__(self, pattern: str):
        self.pattern = pattern
        self.regex = re.compile(f"^{pattern}$")

    def validate(self, text: str) -> bool:
        """驗證文本是否匹配模式"""
        return bool(self.regex.match(text))

    def extract(self, text: str) -> List[str]:
        """從文本中提取所有匹配"""
        return re.findall(self.pattern, text)

    def test_samples(self, samples: List[str]) -> Dict[str, bool]:
        """測試多個樣本"""
        return {s: self.validate(s) for s in samples}


def example_validation():
    """模式驗證範例"""
    # 電子郵件驗證
    email_validator = PatternValidator(PATTERNS["email"])

    test_emails = [
        "user@example.com",
        "test.user@domain.org",
        "invalid-email",
        "no@domain"
    ]

    print("電子郵件驗證:")
    for email in test_emails:
        valid = email_validator.validate(email)
        print(f"  {email}: {'✓' if valid else '✗'}")


# ============================================================
# 使用範例
# ============================================================

def example_basic():
    """範例 1: 基本正則"""
    print("=" * 50)
    print("範例 1: 基本正則模式")
    print("=" * 50)
    print(BASIC_REGEX_EXAMPLE)


def example_complex():
    """範例 2: 複雜格式"""
    print("\n" + "=" * 50)
    print("範例 2: 複雜格式約束")
    print("=" * 50)
    print(COMPLEX_REGEX_EXAMPLE)


def example_numeric():
    """範例 3: 數值約束"""
    print("\n" + "=" * 50)
    print("範例 3: 數值範圍約束")
    print("=" * 50)
    print(NUMERIC_EXAMPLE)


def example_structured():
    """範例 4: 結構化文本"""
    print("\n" + "=" * 50)
    print("範例 4: 結構化文本約束")
    print("=" * 50)
    print(STRUCTURED_TEXT_EXAMPLE)


def example_grammar():
    """範例 5: 自定義語法"""
    print("\n" + "=" * 50)
    print("範例 5: 自定義語法")
    print("=" * 50)
    print(GRAMMAR_EXAMPLE)


def example_combined():
    """範例 6: 組合約束"""
    print("\n" + "=" * 50)
    print("範例 6: 組合約束")
    print("=" * 50)
    print(COMBINED_EXAMPLE)


def example_validator():
    """範例 7: 驗證測試"""
    print("\n" + "=" * 50)
    print("範例 7: 模式驗證")
    print("=" * 50)
    example_validation()


def example_patterns():
    """範例 8: 常用模式庫"""
    print("\n" + "=" * 50)
    print("範例 8: 常用正則模式")
    print("=" * 50)

    print("\n預定義模式:")
    for name, pattern in PATTERNS.items():
        print(f"  {name}: {pattern}")


if __name__ == "__main__":
    print("Outlines 正則約束範例\n")
    example_basic()
    example_complex()
    example_numeric()
    example_structured()
    example_grammar()
    example_combined()
    example_validator()
    example_patterns()
