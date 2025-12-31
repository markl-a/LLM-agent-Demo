#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Guidance 語法控制示例
====================================================

本模塊展示 Guidance 的上下文無關文法(CFG)控制功能:
1. 基本 CFG 語法定義
2. 語法規則組合
3. 代碼生成語法
4. 自然語言語法
5. 結構化文檔生成
6. SQL 語法控制
7. 配置文件語法
8. 自定義 DSL

CFG (Context-Free Grammar) 是 Guidance 最強大的功能之一，
可以定義複雜的結構約束，確保輸出符合特定語法規則。

作者: Guidance 示例團隊
日期: 2025-01-01
"""

import os
import sys
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

try:
    from guidance import models, gen, select
    import guidance
except ImportError:
    print("錯誤: 請先安裝 guidance 庫")
    sys.exit(1)


class GrammarController:
    """
    語法控制演示類

    展示如何使用 CFG 定義和控制複雜的語法結構。
    """

    def __init__(self, model_name: str = "gpt-4", api_key: Optional[str] = None):
        """初始化語法控制器"""
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.grammars: Dict[str, Any] = {}

    def example_basic_grammar(self) -> None:
        """
        示例 1: 基本語法定義

        演示如何定義和使用基本的 CFG 規則。
        """
        print(f"\n{'='*60}")
        print("示例 1: 基本語法定義")
        print(f"{'='*60}\n")

        # 簡單的算術表達式語法
        print("生成算術表達式:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        # number operator number
        lm += gen(name="num1", regex=r"\d+")
        lm += " "
        lm += select(["+", "-", "*", "/"], name="operator")
        lm += " "
        lm += gen(name="num2", regex=r"\d+")

        expression = f"{lm['num1']} {lm['operator']} {lm['num2']}"
        print(f"表達式: {expression}")

        # 計算結果
        try:
            result = eval(expression)
            print(f"結果: {result}\n")
        except:
            print(f"無法計算\n")

        # 變量賦值語法
        print("生成變量賦值語句:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += gen(name="var_name", regex=r"[a-z][a-z0-9_]*")
        lm += " = "
        lm += gen(name="value", regex=r"\d+")
        lm += ";"

        statement = f"{lm['var_name']} = {lm['value']};"
        print(f"語句: {statement}\n")

        # if-else 語句結構
        print("生成條件語句結構:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "if ("
        lm += gen(name="condition", max_tokens=20, stop=")")
        lm += ") {\n"
        lm += "    "
        lm += gen(name="true_branch", max_tokens=30, stop="\n")
        lm += "\n"
        lm += "} else {\n"
        lm += "    "
        lm += gen(name="false_branch", max_tokens=30, stop="\n")
        lm += "\n"
        lm += "}"

        print(f"條件語句:")
        print(f"if ({lm['condition']}) {{")
        print(f"    {lm['true_branch']}")
        print(f"}} else {{")
        print(f"    {lm['false_branch']}")
        print(f"}}\n")

    def example_code_grammar(self) -> None:
        """
        示例 2: 代碼生成語法

        演示如何定義編程語言的語法規則。
        """
        print(f"\n{'='*60}")
        print("示例 2: 代碼生成語法")
        print(f"{'='*60}\n")

        # Python 函數定義
        print("生成 Python 函數:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "def "
        lm += gen(name="func_name", regex=r"[a-z_][a-z0-9_]*")
        lm += "("

        # 參數列表
        param_count = 2
        params = []
        for i in range(param_count):
            lm += gen(name=f"param_{i}", regex=r"[a-z_][a-z0-9_]*")
            params.append(lm[f"param_{i}"])
            if i < param_count - 1:
                lm += ", "

        lm += "):\n"
        lm += "    \"\"\""
        lm += gen(name="docstring", max_tokens=50, stop='"""')
        lm += "\"\"\"\n"
        lm += "    return "
        lm += gen(name="return_expr", max_tokens=30, stop="\n")

        print(f"def {lm['func_name']}({', '.join(params)}):")
        print(f'    """{lm["docstring"]}"""')
        print(f"    return {lm['return_expr']}\n")

        # JavaScript 類定義
        print("生成 JavaScript 類:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "class "
        lm += gen(name="class_name", regex=r"[A-Z][a-zA-Z0-9]*")
        lm += " {\n"
        lm += "    constructor("
        lm += gen(name="constructor_param", regex=r"[a-z][a-zA-Z0-9]*")
        lm += ") {\n"
        lm += "        this."
        lm += gen(name="property", regex=r"[a-z][a-zA-Z0-9]*")
        lm += " = "
        lm += gen(name="init_value", max_tokens=10, stop=";")
        lm += ";\n"
        lm += "    }\n"
        lm += "}"

        print(f"class {lm['class_name']} {{")
        print(f"    constructor({lm['constructor_param']}) {{")
        print(f"        this.{lm['property']} = {lm['init_value']};")
        print(f"    }}")
        print(f"}}\n")

        # SQL 查詢語法
        print("生成 SQL 查詢:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "SELECT "

        # 列名
        col_count = 3
        columns = []
        for i in range(col_count):
            lm += gen(name=f"col_{i}", regex=r"[a-z_][a-z0-9_]*")
            columns.append(lm[f"col_{i}"])
            if i < col_count - 1:
                lm += ", "

        lm += " FROM "
        lm += gen(name="table", regex=r"[a-z_][a-z0-9_]*")
        lm += " WHERE "
        lm += gen(name="condition_col", regex=r"[a-z_][a-z0-9_]*")
        lm += " "
        lm += select(["=", ">", "<", ">=", "<=", "!="], name="operator")
        lm += " "
        lm += gen(name="condition_val", regex=r"['\"]?[a-zA-Z0-9]+['\"]?")
        lm += ";"

        print(f"SELECT {', '.join(columns)}")
        print(f"FROM {lm['table']}")
        print(f"WHERE {lm['condition_col']} {lm['operator']} {lm['condition_val']};\n")

    def example_structured_documents(self) -> None:
        """
        示例 3: 結構化文檔生成

        演示如何生成符合特定格式的文檔。
        """
        print(f"\n{'='*60}")
        print("示例 3: 結構化文檔生成")
        print(f"{'='*60}\n")

        # Markdown 文檔
        print("生成 Markdown 文檔:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        # 標題
        lm += "# "
        lm += gen(name="title", max_tokens=20, stop="\n")
        lm += "\n\n"

        # 簡介
        lm += "## 簡介\n\n"
        lm += gen(name="intro", max_tokens=80, stop="\n\n")
        lm += "\n\n"

        # 功能列表
        lm += "## 功能\n\n"
        for i in range(3):
            lm += f"- "
            lm += gen(name=f"feature_{i}", max_tokens=30, stop="\n")
            lm += "\n"

        lm += "\n"

        # 代碼示例
        lm += "## 示例\n\n"
        lm += "```python\n"
        lm += gen(name="code_example", max_tokens=60, stop="```")
        lm += "\n```\n"

        print(f"# {lm['title']}\n")
        print(f"## 簡介\n{lm['intro']}\n")
        print(f"## 功能")
        for i in range(3):
            print(f"- {lm[f'feature_{i}']}")
        print(f"\n## 示例")
        print(f"```python\n{lm['code_example']}\n```\n")

        # HTML 文檔
        print("\n生成 HTML 文檔:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "<!DOCTYPE html>\n"
        lm += "<html>\n"
        lm += "<head>\n"
        lm += "    <title>"
        lm += gen(name="page_title", max_tokens=20, stop="<")
        lm += "</title>\n"
        lm += "</head>\n"
        lm += "<body>\n"
        lm += "    <h1>"
        lm += gen(name="heading", max_tokens=20, stop="<")
        lm += "</h1>\n"
        lm += "    <p>"
        lm += gen(name="paragraph", max_tokens=50, stop="<")
        lm += "</p>\n"
        lm += "</body>\n"
        lm += "</html>"

        print(f"<!DOCTYPE html>")
        print(f"<html>")
        print(f"<head>")
        print(f"    <title>{lm['page_title']}</title>")
        print(f"</head>")
        print(f"<body>")
        print(f"    <h1>{lm['heading']}</h1>")
        print(f"    <p>{lm['paragraph']}</p>")
        print(f"</body>")
        print(f"</html>\n")

    def example_natural_language_grammar(self) -> None:
        """
        示例 4: 自然語言語法

        演示如何定義自然語言的語法規則。
        """
        print(f"\n{'='*60}")
        print("示例 4: 自然語言語法")
        print(f"{'='*60}\n")

        # 簡單句子結構: 主語 + 動詞 + 賓語
        print("生成簡單句子 (主謂賓):")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        subjects = ["我", "他", "她", "我們", "他們"]
        verbs = ["喜歡", "學習", "創建", "使用", "開發"]
        objects = ["Python", "機器學習", "網站", "應用程序", "系統"]

        lm += select(subjects, name="subject")
        lm += select(verbs, name="verb")
        lm += select(objects, name="object")
        lm += "。"

        sentence = f"{lm['subject']}{lm['verb']}{lm['object']}。"
        print(f"句子: {sentence}\n")

        # 複雜句子: 時間 + 地點 + 主語 + 動詞 + 賓語
        print("生成複雜句子:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        times = ["今天", "昨天", "明天", "上週", "下個月"]
        places = ["在家", "在公司", "在學校", "在圖書館"]

        lm += select(times, name="time")
        lm += select(places, name="place")
        lm += "，"
        lm += select(subjects, name="subject")
        lm += select(verbs, name="verb")
        lm += "了"
        lm += select(objects, name="object")
        lm += "。"

        complex_sentence = f"{lm['time']}{lm['place']}，{lm['subject']}{lm['verb']}了{lm['object']}。"
        print(f"句子: {complex_sentence}\n")

        # 疑問句結構
        print("生成疑問句:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        question_words = ["什麼", "為什麼", "如何", "哪裡"]
        lm += select(question_words, name="question_word")
        lm += "是"
        lm += gen(name="question_content", max_tokens=20, stop="？")
        lm += "？"

        question = f"{lm['question_word']}是{lm['question_content']}？"
        print(f"疑問句: {question}\n")

    def example_config_grammar(self) -> None:
        """
        示例 5: 配置文件語法

        演示如何生成符合特定格式的配置文件。
        """
        print(f"\n{'='*60}")
        print("示例 5: 配置文件語法")
        print(f"{'='*60}\n")

        # INI 格式配置
        print("生成 INI 配置文件:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        sections = ["database", "server", "logging"]

        for section in sections:
            lm += f"[{section}]\n"

            # 生成 3 個配置項
            for i in range(3):
                lm += gen(name=f"{section}_key_{i}", regex=r"[a-z_]+")
                lm += " = "
                lm += gen(name=f"{section}_value_{i}", max_tokens=15, stop="\n")
                lm += "\n"

            lm += "\n"

        print("配置文件:")
        for section in sections:
            print(f"[{section}]")
            for i in range(3):
                key = lm[f"{section}_key_{i}"]
                value = lm[f"{section}_value_{i}"]
                print(f"{key} = {value}")
            print()

        # YAML 格式配置
        print("\n生成 YAML 配置文件:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "app:\n"
        lm += "  name: "
        lm += gen(name="app_name", max_tokens=10, stop="\n")
        lm += "\n"
        lm += "  version: "
        lm += gen(name="version", regex=r"\d+\.\d+\.\d+")
        lm += "\n"
        lm += "  port: "
        lm += gen(name="port", regex=r"\d{4,5}")
        lm += "\n"
        lm += "database:\n"
        lm += "  host: "
        lm += gen(name="db_host", regex=r"[a-z0-9.-]+")
        lm += "\n"
        lm += "  user: "
        lm += gen(name="db_user", regex=r"[a-z_][a-z0-9_]*")
        lm += "\n"

        print("YAML 配置:")
        print(f"app:")
        print(f"  name: {lm['app_name']}")
        print(f"  version: {lm['version']}")
        print(f"  port: {lm['port']}")
        print(f"database:")
        print(f"  host: {lm['db_host']}")
        print(f"  user: {lm['db_user']}\n")

    def example_api_grammar(self) -> None:
        """
        示例 6: API 定義語法

        演示如何生成 API 端點定義。
        """
        print(f"\n{'='*60}")
        print("示例 6: API 定義語法")
        print(f"{'='*60}\n")

        # REST API 端點
        print("生成 REST API 端點:")

        methods = ["GET", "POST", "PUT", "DELETE"]

        for i in range(3):
            lm = models.OpenAI(self.model_name, api_key=self.api_key)

            lm += select(methods, name="method")
            lm += " /"
            lm += gen(name="resource", regex=r"[a-z]+")

            # 如果是 GET 或 DELETE，可能有 ID
            if lm["method"] in ["GET", "DELETE"]:
                lm += "/:"
                lm += gen(name="param", regex=r"[a-z]+")

            endpoint = f"{lm['method']} /{lm['resource']}"
            if "param" in dir(lm):
                endpoint += f"/:{lm['param']}"

            print(f"端點 {i+1}: {endpoint}")

        print()

        # OpenAPI 風格定義
        print("\n生成 OpenAPI 風格定義:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "paths:\n"
        lm += "  /"
        lm += gen(name="path", regex=r"[a-z]+")
        lm += ":\n"
        lm += "    get:\n"
        lm += "      summary: "
        lm += gen(name="summary", max_tokens=30, stop="\n")
        lm += "\n"
        lm += "      responses:\n"
        lm += "        200:\n"
        lm += "          description: "
        lm += gen(name="description", max_tokens=30, stop="\n")
        lm += "\n"

        print(f"paths:")
        print(f"  /{lm['path']}:")
        print(f"    get:")
        print(f"      summary: {lm['summary']}")
        print(f"      responses:")
        print(f"        200:")
        print(f"          description: {lm['description']}\n")

    def example_template_language(self) -> None:
        """
        示例 7: 模板語言語法

        演示如何生成模板語言代碼。
        """
        print(f"\n{'='*60}")
        print("示例 7: 模板語言語法")
        print(f"{'='*60}\n")

        # Jinja2 模板
        print("生成 Jinja2 模板:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "<h1>{{ "
        lm += gen(name="title_var", regex=r"[a-z_][a-z0-9_]*")
        lm += " }}</h1>\n"
        lm += "{% for "
        lm += gen(name="loop_var", regex=r"[a-z_][a-z0-9_]*")
        lm += " in "
        lm += gen(name="collection", regex=r"[a-z_][a-z0-9_]*")
        lm += " %}\n"
        lm += "  <li>{{ "
        lm += gen(name="item_prop", regex=r"[a-z_][a-z0-9_]*\.[a-z_][a-z0-9_]*")
        lm += " }}</li>\n"
        lm += "{% endfor %}"

        print(f"<h1>{{{{ {lm['title_var']} }}}}</h1>")
        print(f"{{% for {lm['loop_var']} in {lm['collection']} %}}")
        print(f"  <li>{{{{ {lm['item_prop']} }}}}</li>")
        print(f"{{% endfor %}}\n")

        # Handlebars 模板
        print("\n生成 Handlebars 模板:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "{{#each "
        lm += gen(name="items", regex=r"[a-z][a-zA-Z0-9]*")
        lm += "}}\n"
        lm += "  <div class=\""
        lm += gen(name="class_name", regex=r"[a-z-]+")
        lm += "\">\n"
        lm += "    {{"
        lm += gen(name="property", regex=r"[a-z][a-zA-Z0-9]*")
        lm += "}}\n"
        lm += "  </div>\n"
        lm += "{{/each}}"

        print(f"{{{{#each {lm['items']}}}}}")
        print(f'  <div class="{lm["class_name"]}">')
        print(f"    {{{{{lm['property']}}}}}")
        print(f"  </div>")
        print(f"{{{{/each}}}}\n")

    def example_dsl_grammar(self) -> None:
        """
        示例 8: 自定義 DSL 語法

        演示如何定義領域特定語言(DSL)。
        """
        print(f"\n{'='*60}")
        print("示例 8: 自定義 DSL 語法")
        print(f"{'='*60}\n")

        # 簡單的任務描述 DSL
        print("生成任務描述 DSL:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "TASK "
        lm += gen(name="task_name", regex=r"[A-Z][a-z]+")
        lm += "\n"
        lm += "  PRIORITY "
        lm += select(["HIGH", "MEDIUM", "LOW"], name="priority")
        lm += "\n"
        lm += "  ASSIGNED_TO "
        lm += gen(name="assignee", regex=r"[A-Z][a-z]+")
        lm += "\n"
        lm += "  DUE_DATE "
        lm += gen(name="due_date", regex=r"\d{4}-\d{2}-\d{2}")
        lm += "\n"
        lm += "END"

        print(f"TASK {lm['task_name']}")
        print(f"  PRIORITY {lm['priority']}")
        print(f"  ASSIGNED_TO {lm['assignee']}")
        print(f"  DUE_DATE {lm['due_date']}")
        print(f"END\n")

        # 規則引擎 DSL
        print("\n生成規則引擎 DSL:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "RULE "
        lm += gen(name="rule_name", max_tokens=15, stop="\n")
        lm += "\n"
        lm += "  WHEN "
        lm += gen(name="condition_field", regex=r"[a-z_]+")
        lm += " "
        lm += select([">", "<", "==", "!="], name="condition_op")
        lm += " "
        lm += gen(name="condition_value", regex=r"\d+")
        lm += "\n"
        lm += "  THEN "
        lm += gen(name="action", max_tokens=20, stop="\n")
        lm += "\n"
        lm += "END_RULE"

        print(f"RULE {lm['rule_name']}")
        print(f"  WHEN {lm['condition_field']} {lm['condition_op']} {lm['condition_value']}")
        print(f"  THEN {lm['action']}")
        print(f"END_RULE\n")

    def example_grammar_composition(self) -> None:
        """
        示例 9: 語法組合

        演示如何組合多個語法規則創建複雜結構。
        """
        print(f"\n{'='*60}")
        print("示例 9: 語法組合")
        print(f"{'='*60}\n")

        # 組合多個語法規則生成完整程序
        print("生成完整的 Python 模組:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        # 導入語句
        lm += "import "
        lm += gen(name="import1", regex=r"[a-z_][a-z0-9_]*")
        lm += "\n"
        lm += "from "
        lm += gen(name="module", regex=r"[a-z_][a-z0-9_]*")
        lm += " import "
        lm += gen(name="import2", regex=r"[a-z_][a-z0-9_]*")
        lm += "\n\n"

        # 常量定義
        lm += gen(name="constant", regex=r"[A-Z_]+")
        lm += " = "
        lm += gen(name="const_value", regex=r"\d+")
        lm += "\n\n"

        # 類定義
        lm += "class "
        lm += gen(name="class_name", regex=r"[A-Z][a-zA-Z0-9]*")
        lm += ":\n"
        lm += "    def __init__(self, "
        lm += gen(name="param", regex=r"[a-z_][a-z0-9_]*")
        lm += "):\n"
        lm += "        self."
        lm += gen(name="attr", regex=r"[a-z_][a-z0-9_]*")
        lm += " = "
        lm += lm["param"]
        lm += "\n"

        print(f"import {lm['import1']}")
        print(f"from {lm['module']} import {lm['import2']}\n")
        print(f"{lm['constant']} = {lm['const_value']}\n")
        print(f"class {lm['class_name']}:")
        print(f"    def __init__(self, {lm['param']}):")
        print(f"        self.{lm['attr']} = {lm['param']}\n")

    def example_validation(self) -> None:
        """
        示例 10: 語法驗證

        演示如何驗證生成的代碼是否符合語法規則。
        """
        print(f"\n{'='*60}")
        print("示例 10: 語法驗證")
        print(f"{'='*60}\n")

        # 生成 Python 代碼並驗證語法
        print("生成並驗證 Python 代碼:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "def "
        lm += gen(name="func_name", regex=r"[a-z_][a-z0-9_]*")
        lm += "():\n"
        lm += "    return "
        lm += gen(name="return_val", regex=r"\d+")

        code = f"def {lm['func_name']}():\n    return {lm['return_val']}"

        print(f"生成的代碼:")
        print(code)
        print()

        # 驗證語法
        try:
            compile(code, '<string>', 'exec')
            print("✓ Python 語法驗證通過\n")
        except SyntaxError as e:
            print(f"✗ 語法錯誤: {e}\n")

        # 生成 JSON 並驗證
        print("生成並驗證 JSON:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += '{"'
        lm += gen(name="key", regex=r"[a-z]+")
        lm += '": "'
        lm += gen(name="value", max_tokens=10, stop='"')
        lm += '"}'

        json_str = f'{{"{lm["key"]}": "{lm["value"]}"}}'

        print(f"生成的 JSON:")
        print(json_str)
        print()

        try:
            json.loads(json_str)
            print("✓ JSON 語法驗證通過\n")
        except json.JSONDecodeError as e:
            print(f"✗ JSON 錯誤: {e}\n")

    def run_all_examples(self) -> None:
        """運行所有示例"""
        print(f"\n{'='*60}")
        print("Guidance 語法控制 - 完整示例")
        print(f"{'='*60}")

        self.example_basic_grammar()
        self.example_code_grammar()
        self.example_structured_documents()
        self.example_natural_language_grammar()
        self.example_config_grammar()
        self.example_api_grammar()
        self.example_template_language()
        self.example_dsl_grammar()
        self.example_grammar_composition()
        self.example_validation()

        print(f"\n{'='*60}")
        print("執行摘要")
        print(f"{'='*60}")
        print(f"✓ 所有語法控制示例執行完成!")


def main():
    """主函數"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║         Guidance 框架 - 語法控制示例                       ║
    ║                                                            ║
    ║  使用 CFG 定義複雜的語法規則                               ║
    ║  適用於代碼生成、DSL、結構化文檔等場景                     ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        return

    controller = GrammarController(
        model_name="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    try:
        controller.run_all_examples()
    except KeyboardInterrupt:
        print("\n\n⚠️  用戶中斷執行")
    except Exception as e:
        print(f"\n✗ 執行出錯: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
