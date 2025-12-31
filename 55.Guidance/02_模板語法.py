#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Guidance 模板語法示例
====================================================

本模塊深入探討 Guidance 的模板語法系統，包括:
1. 基本模板結構
2. 變量插值和格式化
3. 條件邏輯控制
4. 循環和迭代
5. 函數式模板組合
6. 角色系統 (system, user, assistant)
7. 模板繼承和復用

Guidance 的模板語法讓你能夠以聲明式的方式構建複雜的
提示工程流程，同時保持代碼的可讀性和可維護性。

作者: Guidance 示例團隊
日期: 2025-01-01
"""

import os
import sys
from typing import List, Dict, Any, Optional, Callable
import json
from datetime import datetime
from functools import wraps

# Guidance 核心導入
try:
    from guidance import models, gen, select, user, assistant, system
    from guidance import block, each, one_or_more, optional, zero_or_more
    import guidance
except ImportError:
    print("錯誤: 請先安裝 guidance 庫")
    print("運行: pip install guidance>=0.2.0")
    sys.exit(1)


class TemplateEngine:
    """
    Guidance 模板引擎演示類

    展示 Guidance 模板語法的各種特性和最佳實踐。

    Attributes:
        model_name: 使用的模型名稱
        api_key: API 密鑰
        lm: 模型實例
        templates: 已註冊的模板字典
    """

    def __init__(self, model_name: str = "gpt-4", api_key: Optional[str] = None):
        """
        初始化模板引擎

        Args:
            model_name: 模型名稱
            api_key: API 密鑰
        """
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.lm = None
        self.templates: Dict[str, Callable] = {}

        if not self.api_key:
            print("警告: 未找到 API 密鑰")

    def initialize(self) -> None:
        """初始化模型實例"""
        print(f"\n{'='*60}")
        print("初始化 Guidance 模板引擎")
        print(f"{'='*60}\n")

        self.lm = models.OpenAI(
            model=self.model_name,
            api_key=self.api_key
        )
        print(f"✓ 模型已初始化: {self.model_name}")

    def example_basic_template(self) -> None:
        """
        示例 1: 基本模板語法

        演示最基本的模板結構，包括靜態文本和動態生成的組合。
        """
        print(f"\n{'='*60}")
        print("示例 1: 基本模板語法")
        print(f"{'='*60}\n")

        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        # 方法 1: 使用 += 操作符逐步構建
        print("方法 1: 逐步構建模板")
        lm += "問題: 什麼是機器學習?\n"
        lm += "答案: "
        lm += gen(name="answer", max_tokens=100)

        print(f"生成的答案:\n{lm['answer']}\n")

        # 方法 2: 使用 f-string 進行變量插值
        print("方法 2: 使用 f-string 插值")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        topic = "深度學習"
        lm += f"請用一句話解釋「{topic}」: "
        lm += gen(name="explanation", max_tokens=80)

        print(f"解釋:\n{lm['explanation']}\n")

        # 方法 3: 多行模板
        print("方法 3: 多行模板字符串")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        template = """請分析以下技術:

技術名稱: Python
類型: 程式語言

分析:
"""
        lm += template
        lm += gen(name="analysis", max_tokens=150)

        print(f"分析結果:\n{lm['analysis']}\n")

    def example_role_system(self) -> None:
        """
        示例 2: 角色系統

        演示 Guidance 的角色系統 (system, user, assistant)
        這對於構建結構化的對話非常有用。
        """
        print(f"\n{'='*60}")
        print("示例 2: 角色系統 (system, user, assistant)")
        print(f"{'='*60}\n")

        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        # 使用 system 角色設置模型行為
        with system():
            lm += "你是一位專業的 Python 程式設計教師，擅長用簡單的語言解釋複雜的概念。"

        # 使用 user 角色表示用戶輸入
        with user():
            lm += "什麼是裝飾器 (decorator)?"

        # 使用 assistant 角色表示助手回應
        with assistant():
            lm += gen(name="response", max_tokens=200)

        print(f"助手回應:\n{lm['response']}\n")

        # 多輪對話
        print("多輪對話示例:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        with system():
            lm += "你是一位耐心的數學老師。"

        # 第一輪
        with user():
            lm += "什麼是質數?"

        with assistant():
            lm += gen(name="answer1", max_tokens=100)

        print(f"Q1: 什麼是質數?")
        print(f"A1: {lm['answer1']}\n")

        # 第二輪
        with user():
            lm += "請舉三個例子"

        with assistant():
            lm += gen(name="answer2", max_tokens=80)

        print(f"Q2: 請舉三個例子")
        print(f"A2: {lm['answer2']}\n")

    def example_variable_interpolation(self) -> None:
        """
        示例 3: 變量插值

        演示如何在模板中使用變量，包括簡單插值和複雜表達式。
        """
        print(f"\n{'='*60}")
        print("示例 3: 變量插值")
        print(f"{'='*60}\n")

        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        # 簡單變量插值
        name = "Alice"
        age = 25
        profession = "數據科學家"

        lm += f"姓名: {name}\n"
        lm += f"年齡: {age}\n"
        lm += f"職業: {profession}\n\n"
        lm += f"請為 {name}（{age} 歲的{profession}）推薦三本技術書籍:\n"

        for i in range(3):
            lm += f"{i+1}. "
            lm += gen(name=f"book_{i}", max_tokens=30, stop="\n")
            lm += "\n"

        print("推薦書籍:")
        for i in range(3):
            print(f"  {i+1}. {lm[f'book_{i}']}")

        # 字典變量插值
        print("\n使用字典變量:")
        user_info = {
            "name": "Bob",
            "skills": ["Python", "Machine Learning", "Docker"],
            "experience": 5
        }

        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += f"候選人: {user_info['name']}\n"
        lm += f"技能: {', '.join(user_info['skills'])}\n"
        lm += f"經驗: {user_info['experience']} 年\n\n"
        lm += "職位推薦: "
        lm += gen(name="job_recommendation", max_tokens=50)

        print(f"推薦職位: {lm['job_recommendation']}\n")

    def example_conditional_logic(self) -> None:
        """
        示例 4: 條件邏輯

        演示如何在模板中使用條件語句來控制生成流程。
        """
        print(f"\n{'='*60}")
        print("示例 4: 條件邏輯")
        print(f"{'='*60}\n")

        # 根據條件選擇不同的提示
        difficulty_levels = ["初級", "中級", "高級"]

        for level in difficulty_levels:
            print(f"\n--- {level} 難度 ---")
            lm = models.OpenAI(self.model_name, api_key=self.api_key)

            lm += "請出一道 Python 程式題目。\n\n"

            # 根據難度調整要求
            if level == "初級":
                lm += "要求: 適合初學者，涉及基本語法\n"
                max_tokens = 80
            elif level == "中級":
                lm += "要求: 涉及數據結構和算法\n"
                max_tokens = 120
            else:  # 高級
                lm += "要求: 涉及設計模式或優化\n"
                max_tokens = 150

            lm += "題目: "
            lm += gen(name="question", max_tokens=max_tokens)

            print(f"{lm['question']}")

        # 條件選擇
        print("\n\n--- 條件選擇示例 ---")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "這個代碼有 bug 嗎? "
        lm += select(["有", "沒有"], name="has_bug")

        print(f"是否有 bug: {lm['has_bug']}")

        # 根據選擇執行不同的後續操作
        if lm["has_bug"] == "有":
            lm += "\n\n請描述 bug: "
            lm += gen(name="bug_description", max_tokens=100)
            print(f"Bug 描述: {lm['bug_description']}")
        else:
            lm += "\n\n請評價代碼質量: "
            lm += select(["優秀", "良好", "一般"], name="quality")
            print(f"代碼質量: {lm['quality']}")

    def example_loops_and_iteration(self) -> None:
        """
        示例 5: 循環和迭代

        演示如何在模板中使用循環來重複生成內容。
        """
        print(f"\n{'='*60}")
        print("示例 5: 循環和迭代")
        print(f"{'='*60}\n")

        # 簡單循環
        print("生成待辦事項列表:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "今天的待辦事項:\n\n"

        num_tasks = 5
        for i in range(num_tasks):
            lm += f"{i+1}. "
            lm += gen(name=f"task_{i}", max_tokens=30, stop="\n")
            lm += "\n"

        print("待辦事項:")
        for i in range(num_tasks):
            print(f"  {i+1}. {lm[f'task_{i}']}")

        # 迭代列表
        print("\n\n為每個主題生成摘要:")
        topics = ["區塊鏈", "量子計算", "邊緣計算"]

        for topic in topics:
            lm = models.OpenAI(self.model_name, api_key=self.api_key)
            lm += f"用一句話介紹「{topic}」: "
            lm += gen(name="summary", max_tokens=60)
            print(f"  {topic}: {lm['summary']}")

        # 嵌套循環
        print("\n\n生成課程大綱:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        chapters = ["基礎概念", "進階應用", "實戰項目"]
        lm += "Python 機器學習課程大綱:\n\n"

        for i, chapter in enumerate(chapters):
            lm += f"第 {i+1} 章: {chapter}\n"

            # 為每章生成 3 個小節
            for j in range(3):
                lm += f"  {i+1}.{j+1} "
                lm += gen(name=f"section_{i}_{j}", max_tokens=20, stop="\n")
                lm += "\n"

        print("課程大綱:")
        for i, chapter in enumerate(chapters):
            print(f"\n第 {i+1} 章: {chapter}")
            for j in range(3):
                print(f"  {i+1}.{j+1} {lm[f'section_{i}_{j}']}")

    def example_template_functions(self) -> None:
        """
        示例 6: 模板函數

        演示如何創建可復用的模板函數。
        """
        print(f"\n{'='*60}")
        print("示例 6: 模板函數")
        print(f"{'='*60}\n")

        # 定義模板函數
        def create_qa_template(question: str, max_answer_length: int = 100):
            """創建問答模板"""
            lm = models.OpenAI(self.model_name, api_key=self.api_key)
            lm += f"問題: {question}\n"
            lm += "答案: "
            lm += gen(name="answer", max_tokens=max_answer_length)
            return lm

        # 使用模板函數
        questions = [
            "什麼是 REST API?",
            "解釋 Docker 的優勢",
            "什麼是微服務架構?"
        ]

        print("使用 QA 模板函數:")
        for q in questions:
            lm = create_qa_template(q, max_answer_length=80)
            print(f"\nQ: {q}")
            print(f"A: {lm['answer']}")

        # 帶有角色的模板函數
        def create_expert_template(domain: str, question: str):
            """創建專家諮詢模板"""
            lm = models.OpenAI(self.model_name, api_key=self.api_key)

            with system():
                lm += f"你是一位{domain}領域的專家。"

            with user():
                lm += question

            with assistant():
                lm += gen(name="expert_answer", max_tokens=150)

            return lm

        # 使用專家模板
        print("\n\n使用專家模板:")
        lm = create_expert_template("網絡安全", "如何防止 SQL 注入攻擊?")
        print(f"專家回答:\n{lm['expert_answer']}")

    def example_template_composition(self) -> None:
        """
        示例 7: 模板組合

        演示如何組合多個模板來構建複雜的生成流程。
        """
        print(f"\n{'='*60}")
        print("示例 7: 模板組合")
        print(f"{'='*60}\n")

        # 定義基礎模板組件
        def add_header(lm, title: str):
            """添加標題"""
            lm += f"\n{'='*50}\n"
            lm += f"{title}\n"
            lm += f"{'='*50}\n\n"
            return lm

        def add_section(lm, section_name: str, content_name: str, max_tokens: int = 100):
            """添加章節"""
            lm += f"## {section_name}\n\n"
            lm += gen(name=content_name, max_tokens=max_tokens)
            lm += "\n\n"
            return lm

        def add_footer(lm):
            """添加頁腳"""
            lm += f"\n生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            return lm

        # 組合模板
        print("生成技術報告:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        # 組合各個組件
        lm = add_header(lm, "人工智能技術報告")

        lm += "請撰寫一份關於人工智能的技術報告:\n\n"

        lm = add_section(lm, "引言", "introduction", 80)
        lm = add_section(lm, "當前趨勢", "trends", 100)
        lm = add_section(lm, "未來展望", "future", 80)
        lm = add_footer(lm)

        # 輸出完整報告
        print(str(lm))

    def example_dynamic_templates(self) -> None:
        """
        示例 8: 動態模板

        演示如何根據運行時數據動態構建模板。
        """
        print(f"\n{'='*60}")
        print("示例 8: 動態模板")
        print(f"{'='*60}\n")

        # 動態表單生成
        form_fields = [
            {"name": "姓名", "type": "text", "required": True},
            {"name": "年齡", "type": "number", "required": True},
            {"name": "城市", "type": "select", "options": ["台北", "台中", "高雄"], "required": False},
            {"name": "職業", "type": "text", "required": True}
        ]

        print("動態表單填寫:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "請填寫以下表單:\n\n"

        for field in form_fields:
            field_name = field["name"]
            field_type = field["type"]

            lm += f"{field_name}: "

            if field_type == "select":
                lm += select(field["options"], name=field_name.lower())
            elif field_type == "number":
                lm += gen(name=field_name.lower(), regex=r"\d+")
            else:
                lm += gen(name=field_name.lower(), max_tokens=20, stop="\n")

            lm += "\n"

        print("填寫結果:")
        for field in form_fields:
            field_name = field["name"]
            value = lm[field_name.lower()]
            print(f"  {field_name}: {value}")

        # 動態問卷生成
        print("\n\n動態問卷調查:")
        questions_config = [
            {"q": "你最常用的程式語言是?", "type": "select", "options": ["Python", "JavaScript", "Java", "C++"]},
            {"q": "你有多少年的開發經驗?", "type": "select", "options": ["1年以下", "1-3年", "3-5年", "5年以上"]},
            {"q": "你最感興趣的技術領域是?", "type": "text"}
        ]

        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "問卷調查:\n\n"

        for i, q_config in enumerate(questions_config):
            lm += f"Q{i+1}: {q_config['q']}\n"
            lm += "A: "

            if q_config["type"] == "select":
                lm += select(q_config["options"], name=f"answer_{i}")
            else:
                lm += gen(name=f"answer_{i}", max_tokens=30, stop="\n")

            lm += "\n\n"

        print("問卷結果:")
        for i, q_config in enumerate(questions_config):
            print(f"Q{i+1}: {q_config['q']}")
            print(f"A{i+1}: {lm[f'answer_{i}']}\n")

    def example_template_inheritance(self) -> None:
        """
        示例 9: 模板繼承

        演示如何創建基礎模板並通過繼承來擴展功能。
        """
        print(f"\n{'='*60}")
        print("示例 9: 模板繼承")
        print(f"{'='*60}\n")

        # 基礎模板類
        class BaseTemplate:
            def __init__(self, model_name: str, api_key: str):
                self.model_name = model_name
                self.api_key = api_key

            def create_model(self):
                return models.OpenAI(self.model_name, api_key=self.api_key)

            def add_prompt(self, lm, prompt: str):
                lm += prompt
                return lm

            def generate(self, lm, name: str, max_tokens: int = 100):
                lm += gen(name=name, max_tokens=max_tokens)
                return lm

        # 文章模板 (繼承基礎模板)
        class ArticleTemplate(BaseTemplate):
            def create_article(self, title: str, sections: List[str]):
                lm = self.create_model()
                lm += f"文章標題: {title}\n\n"

                for i, section in enumerate(sections):
                    lm += f"## {section}\n\n"
                    lm = self.generate(lm, f"section_{i}", max_tokens=100)
                    lm += "\n\n"

                return lm

        # 代碼模板 (繼承基礎模板)
        class CodeTemplate(BaseTemplate):
            def create_function(self, function_name: str, description: str):
                lm = self.create_model()
                lm += f"請實現以下 Python 函數:\n\n"
                lm += f"函數名: {function_name}\n"
                lm += f"功能: {description}\n\n"
                lm += "代碼:\n"
                lm = self.generate(lm, "code", max_tokens=200)
                return lm

        # 使用文章模板
        print("使用文章模板:")
        article_template = ArticleTemplate(self.model_name, self.api_key)
        lm = article_template.create_article(
            "深度學習入門",
            ["什麼是深度學習", "常用框架介紹", "學習路線建議"]
        )

        for i in range(3):
            print(f"\n章節 {i+1}:")
            print(lm[f"section_{i}"])

        # 使用代碼模板
        print("\n\n使用代碼模板:")
        code_template = CodeTemplate(self.model_name, self.api_key)
        lm = code_template.create_function(
            "calculate_average",
            "計算列表中所有數字的平均值"
        )

        print(f"生成的代碼:\n{lm['code']}")

    def example_advanced_formatting(self) -> None:
        """
        示例 10: 高級格式化

        演示複雜的格式化技巧和最佳實踐。
        """
        print(f"\n{'='*60}")
        print("示例 10: 高級格式化")
        print(f"{'='*60}\n")

        # Markdown 格式化
        print("生成 Markdown 格式文檔:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "# API 文檔\n\n"
        lm += "## GET /users\n\n"
        lm += "**描述**: "
        lm += gen(name="description", max_tokens=50, stop="\n")
        lm += "\n\n"

        lm += "**參數**:\n"
        for i, param in enumerate(["page", "limit", "sort"]):
            lm += f"- `{param}`: "
            lm += gen(name=f"param_{param}", max_tokens=30, stop="\n")
            lm += "\n"

        lm += "\n**返回值**: "
        lm += gen(name="return_value", max_tokens=50)

        print(str(lm))

        # JSON 格式化
        print("\n\n生成結構化數據:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "生成一個用戶配置:\n\n"
        lm += "姓名: "
        lm += gen(name="name", max_tokens=10, stop="\n")
        lm += "\n級別: "
        lm += select(["初級", "中級", "高級"], name="level")
        lm += "\n語言: "
        lm += select(["Python", "JavaScript", "Java"], name="language")

        # 組裝成 JSON
        user_config = {
            "name": lm["name"],
            "level": lm["level"],
            "language": lm["language"],
            "created_at": datetime.now().isoformat()
        }

        print("\n用戶配置 (JSON):")
        print(json.dumps(user_config, indent=2, ensure_ascii=False))

    def run_all_examples(self) -> None:
        """運行所有示例"""
        self.initialize()

        self.example_basic_template()
        self.example_role_system()
        self.example_variable_interpolation()
        self.example_conditional_logic()
        self.example_loops_and_iteration()
        self.example_template_functions()
        self.example_template_composition()
        self.example_dynamic_templates()
        self.example_template_inheritance()
        self.example_advanced_formatting()

        print(f"\n{'='*60}")
        print("✓ 所有模板示例執行完成!")
        print(f"{'='*60}")


def main():
    """主函數"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║         Guidance 框架 - 模板語法示例                       ║
    ║                                                            ║
    ║  展示 Guidance 豐富的模板語法特性                          ║
    ║  包括變量插值、條件邏輯、循環迭代等                        ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        return

    engine = TemplateEngine(
        model_name="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    try:
        engine.run_all_examples()
    except KeyboardInterrupt:
        print("\n\n⚠️  用戶中斷執行")
    except Exception as e:
        print(f"\n✗ 執行出錯: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
