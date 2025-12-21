"""
Outlines 基礎範例
================

本範例展示 Outlines 庫的基本使用方法。

Outlines 特點：
1. 結構化文本生成
2. 正則表達式約束
3. JSON Schema 約束
4. 類型安全輸出

安裝依賴：
pip install outlines
"""

import outlines
from outlines import models, generate
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json

# ============================================================
# 1. 模型加載
# ============================================================

LOAD_MODEL_EXAMPLE = '''
import outlines

# 加載 OpenAI 模型
model = outlines.models.openai("gpt-3.5-turbo")

# 加載本地模型 (Transformers)
model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")

# 加載量化模型
model = outlines.models.transformers(
    "mistralai/Mistral-7B-v0.1",
    device="cuda",
    model_kwargs={"load_in_4bit": True}
)

# 加載 vLLM 模型（高性能）
model = outlines.models.vllm("mistralai/Mistral-7B-v0.1")
'''


# ============================================================
# 2. 基本文本生成
# ============================================================

def basic_generation_example():
    """基本文本生成"""
    print("基本文本生成範例:")
    print('''
import outlines

model = outlines.models.openai("gpt-3.5-turbo")

# 簡單生成
generator = outlines.generate.text(model)
result = generator("寫一個關於 AI 的句子：")
print(result)
''')


# ============================================================
# 3. 選擇生成（Choice）
# ============================================================

def choice_generation_example():
    """選擇生成範例"""
    print("\n選擇生成範例:")
    print('''
import outlines

model = outlines.models.openai("gpt-3.5-turbo")

# 從固定選項中選擇
choices = ["正面", "負面", "中性"]
generator = outlines.generate.choice(model, choices)

result = generator("這個產品很棒！")
print(result)  # 輸出: 正面

# 使用 Enum
from enum import Enum

class Sentiment(Enum):
    POSITIVE = "正面"
    NEGATIVE = "負面"
    NEUTRAL = "中性"

generator = outlines.generate.choice(model, Sentiment)
result = generator("這個服務太差了")
print(result)  # 輸出: Sentiment.NEGATIVE
''')


# ============================================================
# 4. 整數生成
# ============================================================

def integer_generation_example():
    """整數生成範例"""
    print("\n整數生成範例:")
    print('''
import outlines

model = outlines.models.openai("gpt-3.5-turbo")

# 生成整數
generator = outlines.generate.format(model, int)

result = generator("1 + 1 = ")
print(result)  # 輸出: 2
print(type(result))  # <class 'int'>

# 生成浮點數
generator = outlines.generate.format(model, float)
result = generator("圓周率約等於：")
print(result)  # 輸出: 3.14159
''')


# ============================================================
# 5. JSON 生成
# ============================================================

JSON_GENERATION_EXAMPLE = '''
import outlines
from pydantic import BaseModel
from typing import List, Optional

model = outlines.models.openai("gpt-3.5-turbo")

# 定義輸出結構
class Person(BaseModel):
    name: str
    age: int
    city: str
    hobbies: List[str]

# 創建 JSON 生成器
generator = outlines.generate.json(model, Person)

# 生成
prompt = "生成一個住在台北的年輕人的資料："
result = generator(prompt)

print(type(result))  # <class 'Person'>
print(result.name)
print(result.age)
print(result.hobbies)
'''


# ============================================================
# 6. 正則表達式生成
# ============================================================

REGEX_GENERATION_EXAMPLE = '''
import outlines

model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")

# 電話號碼格式
phone_regex = r"\\d{3}-\\d{4}-\\d{4}"
generator = outlines.generate.regex(model, phone_regex)

result = generator("客服電話：")
print(result)  # 例如: 02-1234-5678

# 電子郵件格式
email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"
generator = outlines.generate.regex(model, email_regex)

result = generator("聯繫郵箱：")
print(result)  # 例如: support@example.com

# 日期格式
date_regex = r"\\d{4}-\\d{2}-\\d{2}"
generator = outlines.generate.regex(model, date_regex)

result = generator("今天日期：")
print(result)  # 例如: 2024-03-15
'''


# ============================================================
# 7. 提示模板
# ============================================================

def prompt_template_example():
    """提示模板範例"""
    print("\n提示模板範例:")
    print('''
import outlines

# 使用裝飾器定義模板
@outlines.prompt
def sentiment_prompt(text):
    """分析以下文本的情感：

    文本: {{ text }}

    情感（正面/負面/中性）："""

# 生成提示
prompt = sentiment_prompt("這個產品真的很好用！")
print(prompt)

# 帶多個變量的模板
@outlines.prompt
def qa_prompt(context, question):
    """根據以下背景回答問題。

    背景: {{ context }}

    問題: {{ question }}

    回答："""

prompt = qa_prompt(
    context="Python 是一種程式語言",
    question="Python 是什麼？"
)
''')


# ============================================================
# 8. 類型定義
# ============================================================

# Pydantic 模型
from pydantic import BaseModel, Field
from typing import List, Optional


class Address(BaseModel):
    """地址模型"""
    street: str = Field(description="街道地址")
    city: str = Field(description="城市")
    country: str = Field(description="國家")
    postal_code: Optional[str] = Field(None, description="郵遞區號")


class PersonInfo(BaseModel):
    """人員信息模型"""
    name: str = Field(description="姓名")
    age: int = Field(ge=0, le=150, description="年齡")
    email: str = Field(description="電子郵件")
    address: Address = Field(description="地址")
    skills: List[str] = Field(default_factory=list, description="技能列表")


class ClassificationResult(BaseModel):
    """分類結果模型"""
    category: str = Field(description="分類類別")
    confidence: float = Field(ge=0, le=1, description="置信度")
    reasoning: str = Field(description="分類理由")


# ============================================================
# 9. 批量生成
# ============================================================

BATCH_GENERATION_EXAMPLE = '''
import outlines
from pydantic import BaseModel

model = outlines.models.openai("gpt-3.5-turbo")

class Sentiment(BaseModel):
    text: str
    sentiment: str
    confidence: float

generator = outlines.generate.json(model, Sentiment)

# 批量處理
texts = [
    "這個產品很棒！",
    "服務太差了",
    "還可以吧"
]

results = []
for text in texts:
    prompt = f"分析情感: {text}"
    result = generator(prompt)
    results.append(result)

for r in results:
    print(f"{r.text}: {r.sentiment} ({r.confidence})")
'''


# ============================================================
# 10. 生成配置
# ============================================================

GENERATION_CONFIG_EXAMPLE = '''
import outlines

model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")

# 配置生成參數
generator = outlines.generate.text(model)

result = generator(
    "寫一個故事開頭：",
    max_tokens=100,        # 最大 token 數
    temperature=0.8,       # 溫度（創造性）
    top_p=0.9,            # nucleus sampling
    top_k=50,             # top-k sampling
    stop=["。", "\\n"],    # 停止標記
)

print(result)
'''


# ============================================================
# 使用範例展示
# ============================================================

def example_load_model():
    """範例 1: 模型加載"""
    print("=" * 50)
    print("範例 1: 模型加載")
    print("=" * 50)
    print(LOAD_MODEL_EXAMPLE)


def example_basic_generation():
    """範例 2: 基本生成"""
    print("\n" + "=" * 50)
    print("範例 2: 基本文本生成")
    print("=" * 50)
    basic_generation_example()


def example_choice():
    """範例 3: 選擇生成"""
    print("\n" + "=" * 50)
    print("範例 3: 選擇生成")
    print("=" * 50)
    choice_generation_example()


def example_integer():
    """範例 4: 整數生成"""
    print("\n" + "=" * 50)
    print("範例 4: 整數生成")
    print("=" * 50)
    integer_generation_example()


def example_json():
    """範例 5: JSON 生成"""
    print("\n" + "=" * 50)
    print("範例 5: JSON 生成")
    print("=" * 50)
    print(JSON_GENERATION_EXAMPLE)


def example_regex():
    """範例 6: 正則表達式生成"""
    print("\n" + "=" * 50)
    print("範例 6: 正則表達式生成")
    print("=" * 50)
    print(REGEX_GENERATION_EXAMPLE)


def example_prompt_template():
    """範例 7: 提示模板"""
    print("\n" + "=" * 50)
    print("範例 7: 提示模板")
    print("=" * 50)
    prompt_template_example()


def example_types():
    """範例 8: 類型定義"""
    print("\n" + "=" * 50)
    print("範例 8: Pydantic 類型定義")
    print("=" * 50)

    print("\n定義的類型:")
    print(f"  PersonInfo: {PersonInfo.model_json_schema()}")


def example_batch():
    """範例 9: 批量生成"""
    print("\n" + "=" * 50)
    print("範例 9: 批量生成")
    print("=" * 50)
    print(BATCH_GENERATION_EXAMPLE)


def example_config():
    """範例 10: 生成配置"""
    print("\n" + "=" * 50)
    print("範例 10: 生成配置")
    print("=" * 50)
    print(GENERATION_CONFIG_EXAMPLE)


if __name__ == "__main__":
    print("Outlines 基礎範例\n")
    example_load_model()
    example_basic_generation()
    example_choice()
    example_integer()
    example_json()
    example_regex()
    example_prompt_template()
    example_types()
    example_batch()
    example_config()
