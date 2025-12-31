"""
Mirascope 提示模板示例

本示例展示：
1. Jinja2 模板語法
2. 變量插值
3. 條件和循環
4. 模板繼承
5. 最佳實踐

運行方式：
    python 02_提示模板.py
"""

import os
from mirascope.openai import OpenAICall
from typing import List, Optional


# ==================== 基本變量插值 ====================

class BasicTemplate(OpenAICall):
    """基本模板"""
    prompt_template = """
    你好，{name}！
    今天是{date}，天氣{weather}。
    """

    name: str
    date: str
    weather: str


# ==================== 條件語句 ====================

class ConditionalTemplate(OpenAICall):
    """條件模板"""
    prompt_template = """
    為用戶推薦{product_type}。

    {% if budget %}
    預算限制：{budget}元以內
    {% endif %}

    {% if premium %}
    請推薦高端產品。
    {% else %}
    請推薦性價比高的產品。
    {% endif %}
    """

    product_type: str
    budget: Optional[int] = None
    premium: bool = False


# ==================== 循環語句 ====================

class LoopTemplate(OpenAICall):
    """循環模板"""
    prompt_template = """
    請分析以下項目：

    {% for item in items %}
    {{ loop.index }}. {{ item }}
    {% endfor %}

    總結它們的共同特點。
    """

    items: List[str]


# ==================== 複雜模板 ====================

class ComplexTemplate(OpenAICall):
    """複雜模板"""
    prompt_template = """
    # 任務：{{ task_name }}

    ## 描述
    {{ description }}

    ## 要求
    {% for requirement in requirements %}
    - {{ requirement }}
    {% endfor %}

    {% if examples %}
    ## 示例
    {% for example in examples %}
    **示例 {{ loop.index }}:**
    {{ example }}
    {% endfor %}
    {% endif %}

    {% if constraints %}
    ## 限制
    {% for constraint in constraints %}
    ⚠️ {{ constraint }}
    {% endfor %}
    {% endif %}

    請完成上述任務。
    """

    task_name: str
    description: str
    requirements: List[str]
    examples: Optional[List[str]] = None
    constraints: Optional[List[str]] = None


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("\\n" + "="*60)
    print("Mirascope 提示模板示例")
    print("="*60)

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 請設置 OPENAI_API_KEY 環境變量")
        return

    # 示例 1: 基本模板
    print("\\n示例 1: 基本變量插值")
    try:
        response = BasicTemplate(
            name="小明",
            date="2025年1月15日",
            weather="晴朗"
        ).call()
        print(f"結果: {response.content[:100]}...")
    except Exception as e:
        print(f"❌ 錯誤: {e}")

    # 示例 2: 條件模板
    print("\\n示例 2: 條件語句")
    try:
        response = ConditionalTemplate(
            product_type="筆記本電腦",
            budget=5000,
            premium=False
        ).call()
        print(f"結果: {response.content[:100]}...")
    except Exception as e:
        print(f"❌ 錯誤: {e}")

    # 示例 3: 循環模板
    print("\\n示例 3: 循環語句")
    try:
        response = LoopTemplate(
            items=["Python", "JavaScript", "Go", "Rust"]
        ).call()
        print(f"結果: {response.content[:100]}...")
    except Exception as e:
        print(f"❌ 錯誤: {e}")

    # 示例 4: 複雜模板
    print("\\n示例 4: 複雜模板")
    try:
        response = ComplexTemplate(
            task_name="代碼審查",
            description="審查 Python 代碼的質量和安全性",
            requirements=[
                "檢查代碼風格",
                "識別潛在bug",
                "評估性能"
            ],
            examples=["示例代碼1", "示例代碼2"],
            constraints=["不修改原代碼", "保持向後兼容"]
        ).call()
        print(f"結果: {response.content[:100]}...")
    except Exception as e:
        print(f"❌ 錯誤: {e}")

    print("\\n" + "="*60)
    print("✅ 所有示例運行完成！")
    print("="*60)


if __name__ == "__main__":
    main()
