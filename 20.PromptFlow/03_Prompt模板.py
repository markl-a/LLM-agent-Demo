"""
PromptFlow Prompt 模板範例
=========================

本範例展示如何在 PromptFlow 中使用和管理 Prompt 模板。

Prompt 模板功能：
1. Jinja2 模板語法
2. 變數替換
3. 條件邏輯
4. 循環結構
5. 模板組合

安裝依賴：
pip install promptflow promptflow-tools jinja2
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from jinja2 import Template, Environment, BaseLoader

# ============================================================
# 配置
# ============================================================

# PromptFlow 使用 Jinja2 作為模板引擎
# 支持變數、條件、循環等高級功能


# ============================================================
# 基礎 Prompt 模板
# ============================================================

class PromptTemplate:
    """
    Prompt 模板類

    封裝 Jinja2 模板功能
    """

    def __init__(self, template_string: str):
        """
        初始化模板

        Args:
            template_string: Jinja2 模板字符串
        """
        self.template = Template(template_string)
        self.template_string = template_string

    def render(self, **kwargs) -> str:
        """
        渲染模板

        Args:
            **kwargs: 模板變數

        Returns:
            渲染後的字符串
        """
        return self.template.render(**kwargs)

    def get_variables(self) -> List[str]:
        """
        獲取模板中的變數名

        Returns:
            變數名列表
        """
        from jinja2 import meta
        env = Environment()
        ast = env.parse(self.template_string)
        return list(meta.find_undeclared_variables(ast))


# ============================================================
# Prompt 模板庫
# ============================================================

class PromptLibrary:
    """
    Prompt 模板庫

    管理和組織多個 Prompt 模板
    """

    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self._init_default_templates()

    def _init_default_templates(self):
        """初始化默認模板"""
        # 問答模板
        self.register("qa", """
你是一個專業的問答助手。請根據以下上下文回答問題。

上下文：
{{ context }}

問題：{{ question }}

請提供準確、簡潔的回答：
""")

        # 摘要模板
        self.register("summarize", """
請對以下文本進行摘要，保持主要信息，長度控制在 {{ max_words }} 字以內。

原文：
{{ text }}

摘要：
""")

        # 翻譯模板
        self.register("translate", """
請將以下 {{ source_lang }} 文本翻譯成 {{ target_lang }}：

原文：
{{ text }}

翻譯：
""")

        # 代碼生成模板
        self.register("code_generation", """
請根據以下需求生成 {{ language }} 代碼：

需求描述：
{{ requirement }}

{% if examples %}
參考示例：
{% for example in examples %}
- {{ example }}
{% endfor %}
{% endif %}

請生成完整、可運行的代碼：
```{{ language }}
""")

        # 分類模板
        self.register("classification", """
請將以下文本分類到給定的類別中。

文本：{{ text }}

可選類別：
{% for category in categories %}
- {{ category }}
{% endfor %}

請只回答類別名稱：
""")

    def register(self, name: str, template_string: str):
        """註冊模板"""
        self.templates[name] = PromptTemplate(template_string)

    def get(self, name: str) -> Optional[PromptTemplate]:
        """獲取模板"""
        return self.templates.get(name)

    def render(self, name: str, **kwargs) -> str:
        """渲染模板"""
        template = self.get(name)
        if not template:
            raise ValueError(f"模板不存在: {name}")
        return template.render(**kwargs)

    def list_templates(self) -> List[str]:
        """列出所有模板"""
        return list(self.templates.keys())


# ============================================================
# 高級模板功能
# ============================================================

class AdvancedPromptBuilder:
    """
    高級 Prompt 構建器

    支持複雜的 Prompt 構建邏輯
    """

    def __init__(self):
        self.env = Environment(loader=BaseLoader())
        self._register_filters()

    def _register_filters(self):
        """註冊自定義過濾器"""
        # 截斷過濾器
        self.env.filters['truncate_words'] = lambda s, n: ' '.join(s.split()[:n])

        # 列表格式化
        self.env.filters['as_bullets'] = lambda items: '\n'.join(f"• {item}" for item in items)

        # JSON 格式化
        import json
        self.env.filters['to_json'] = lambda obj: json.dumps(obj, ensure_ascii=False, indent=2)

    def build_prompt(
        self,
        template_string: str,
        **kwargs
    ) -> str:
        """構建 Prompt"""
        template = self.env.from_string(template_string)
        return template.render(**kwargs)

    def build_chat_prompt(
        self,
        system_message: str,
        user_message: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """
        構建聊天 Prompt

        Args:
            system_message: 系統消息
            user_message: 用戶消息
            history: 對話歷史

        Returns:
            消息列表
        """
        messages = [{"role": "system", "content": system_message}]

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": user_message})

        return messages


# ============================================================
# PromptFlow 專用模板
# ============================================================

# PromptFlow 使用 .jinja2 文件存儲模板
# 以下是模板文件的示例內容

CHAT_TEMPLATE = """
system:
你是一個有幫助的 AI 助手。請提供準確、有用的回答。

{% if persona %}
你的角色是：{{ persona }}
{% endif %}

user:
{{ user_input }}
"""

RAG_TEMPLATE = """
system:
你是一個知識問答助手。請根據提供的上下文回答問題。
如果上下文中沒有相關信息，請誠實地說「根據現有資料無法回答」。

user:
# 上下文
{% for doc in documents %}
---
來源：{{ doc.source }}
內容：{{ doc.content }}
{% endfor %}

# 問題
{{ question }}

請基於上下文回答：
"""

CHAIN_OF_THOUGHT_TEMPLATE = """
system:
你是一個擅長邏輯推理的助手。請一步一步思考問題。

user:
問題：{{ question }}

請按以下步驟回答：
1. 首先，分析問題的關鍵點
2. 然後，列出解決步驟
3. 接著，逐步推理
4. 最後，給出結論

開始思考：
"""

FEW_SHOT_TEMPLATE = """
system:
請根據示例完成任務。

{% for example in examples %}
輸入：{{ example.input }}
輸出：{{ example.output }}

{% endfor %}

user:
輸入：{{ input }}
輸出：
"""


# ============================================================
# 使用範例
# ============================================================

def example_basic_template():
    """
    範例 1: 基礎模板使用

    展示簡單的模板渲染
    """
    print("=" * 50)
    print("範例 1: 基礎模板使用")
    print("=" * 50)

    template = PromptTemplate("""
你好 {{ name }}！

今天是 {{ date }}，天氣 {{ weather }}。
有什麼我可以幫助你的嗎？
""")

    result = template.render(
        name="小明",
        date="2024年1月15日",
        weather="晴朗"
    )

    print("渲染結果:")
    print(result)

    # 獲取變數
    variables = template.get_variables()
    print(f"\n模板變數: {variables}")


def example_conditional_template():
    """
    範例 2: 條件模板

    展示帶條件邏輯的模板
    """
    print("\n" + "=" * 50)
    print("範例 2: 條件模板")
    print("=" * 50)

    template = PromptTemplate("""
{% if is_premium %}
尊貴的 VIP 用戶 {{ username }}，歡迎回來！
您可以享受以下特權：
- 無限制查詢
- 優先響應
- 專屬客服
{% else %}
親愛的用戶 {{ username }}，歡迎使用！
升級為 VIP 可享受更多特權。
{% endif %}
""")

    # VIP 用戶
    print("VIP 用戶:")
    print(template.render(username="張三", is_premium=True))

    # 普通用戶
    print("\n普通用戶:")
    print(template.render(username="李四", is_premium=False))


def example_loop_template():
    """
    範例 3: 循環模板

    展示帶循環的模板
    """
    print("\n" + "=" * 50)
    print("範例 3: 循環模板")
    print("=" * 50)

    template = PromptTemplate("""
請分析以下產品列表：

{% for product in products %}
{{ loop.index }}. {{ product.name }}
   - 價格：${{ product.price }}
   - 類別：{{ product.category }}
{% endfor %}

請提供：
1. 總價值
2. 按類別分組
3. 最貴和最便宜的產品
""")

    products = [
        {"name": "筆記本電腦", "price": 1200, "category": "電子"},
        {"name": "無線滑鼠", "price": 30, "category": "配件"},
        {"name": "顯示器", "price": 350, "category": "電子"},
        {"name": "鍵盤", "price": 80, "category": "配件"},
    ]

    result = template.render(products=products)
    print("渲染結果:")
    print(result)


def example_prompt_library():
    """
    範例 4: 使用 Prompt 庫

    展示如何使用預定義的模板庫
    """
    print("\n" + "=" * 50)
    print("範例 4: 使用 Prompt 庫")
    print("=" * 50)

    library = PromptLibrary()

    print("可用模板:", library.list_templates())

    # 使用問答模板
    qa_prompt = library.render(
        "qa",
        context="Python 是一種高級編程語言，由 Guido van Rossum 於 1991 年創建。",
        question="Python 是誰創建的？"
    )
    print("\n問答模板:")
    print(qa_prompt)

    # 使用翻譯模板
    translate_prompt = library.render(
        "translate",
        source_lang="中文",
        target_lang="英文",
        text="人工智能正在改變世界"
    )
    print("\n翻譯模板:")
    print(translate_prompt)


def example_advanced_builder():
    """
    範例 5: 高級構建器

    展示高級 Prompt 構建功能
    """
    print("\n" + "=" * 50)
    print("範例 5: 高級構建器")
    print("=" * 50)

    builder = AdvancedPromptBuilder()

    # 使用自定義過濾器
    template = """
任務列表：
{{ tasks | as_bullets }}

前 3 個任務：
{{ description | truncate_words(10) }}...

配置：
{{ config | to_json }}
"""

    result = builder.build_prompt(
        template,
        tasks=["完成報告", "發送郵件", "開會討論"],
        description="這是一個很長的描述，包含了很多細節信息，需要被截斷",
        config={"model": "gpt-4", "temperature": 0.7}
    )

    print("渲染結果:")
    print(result)


def example_chat_prompt():
    """
    範例 6: 聊天 Prompt

    展示如何構建聊天格式的 Prompt
    """
    print("\n" + "=" * 50)
    print("範例 6: 聊天 Prompt")
    print("=" * 50)

    builder = AdvancedPromptBuilder()

    history = [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好！有什麼可以幫助你的嗎？"},
    ]

    messages = builder.build_chat_prompt(
        system_message="你是一個專業的客服助手",
        user_message="我想了解你們的退款政策",
        history=history
    )

    print("聊天消息:")
    for msg in messages:
        print(f"  [{msg['role']}]: {msg['content']}")


def example_few_shot():
    """
    範例 7: Few-Shot 模板

    展示 Few-Shot 學習的模板
    """
    print("\n" + "=" * 50)
    print("範例 7: Few-Shot 模板")
    print("=" * 50)

    template = PromptTemplate(FEW_SHOT_TEMPLATE)

    examples = [
        {"input": "我今天很開心", "output": "正面"},
        {"input": "這個產品太差了", "output": "負面"},
        {"input": "天氣還可以", "output": "中性"},
    ]

    result = template.render(
        examples=examples,
        input="這部電影真的太棒了！"
    )

    print("Few-Shot Prompt:")
    print(result)


# ============================================================
# PromptFlow 文件模板示例
# ============================================================

def example_promptflow_templates():
    """
    範例 8: PromptFlow 文件模板

    展示 PromptFlow 中的模板文件格式
    """
    print("\n" + "=" * 50)
    print("範例 8: PromptFlow 文件模板")
    print("=" * 50)

    print("PromptFlow 使用 .jinja2 文件存儲模板")
    print("\n示例模板文件內容:\n")

    print("=== chat.jinja2 ===")
    print(CHAT_TEMPLATE)

    print("\n=== rag.jinja2 ===")
    print(RAG_TEMPLATE[:300] + "...")


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    print("PromptFlow Prompt 模板範例")
    print()

    example_basic_template()
    example_conditional_template()
    example_loop_template()
    example_prompt_library()
    example_advanced_builder()
    example_chat_prompt()
    example_few_shot()
    example_promptflow_templates()
