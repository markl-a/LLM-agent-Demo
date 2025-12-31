"""
Outlines 語法生成示例
====================

本示例展示如何使用 Outlines 的上下文無關語法(CFG)進行代碼生成。

主要內容:
1. SQL 查詢生成
2. Python 代碼生成
3. JSON 生成
4. 自定義語法
5. 語法驗證

作者: Outlines 教學團隊
日期: 2025-01
"""

import outlines
from outlines import models, generate
import torch
from typing import List, Dict, Optional, Any
import logging
import sys
import re
from dataclasses import dataclass

# ==================== 設置日誌 ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== 語法定義 ====================

class GrammarDefinitions:
    """
    語法定義庫

    包含各種常用的上下文無關語法
    """

    # SQL SELECT 語法
    SQL_SELECT = """
    ?start: select_statement

    select_statement: "SELECT" columns "FROM" table where_clause? order_clause? limit_clause?

    columns: "*" | column_list
    column_list: column ("," column)*
    column: CNAME | aggregate_func

    aggregate_func: ("COUNT" | "SUM" | "AVG" | "MAX" | "MIN") "(" (column | "*") ")"

    table: CNAME

    where_clause: "WHERE" condition
    condition: column operator value
    operator: "=" | "!=" | ">" | "<" | ">=" | "<="
    value: STRING | NUMBER

    order_clause: "ORDER BY" column ("ASC" | "DESC")?
    limit_clause: "LIMIT" NUMBER

    %import common.CNAME
    %import common.STRING
    %import common.NUMBER
    %import common.WS
    %ignore WS
    """

    # SQL INSERT 語法
    SQL_INSERT = """
    ?start: insert_statement

    insert_statement: "INSERT INTO" table "(" column_list ")" "VALUES" "(" value_list ")"

    table: CNAME
    column_list: CNAME ("," CNAME)*
    value_list: value ("," value)*
    value: STRING | NUMBER | "NULL"

    %import common.CNAME
    %import common.STRING
    %import common.NUMBER
    %import common.WS
    %ignore WS
    """

    # SQL UPDATE 語法
    SQL_UPDATE = """
    ?start: update_statement

    update_statement: "UPDATE" table "SET" assignments where_clause?

    table: CNAME
    assignments: assignment ("," assignment)*
    assignment: CNAME "=" value
    value: STRING | NUMBER | "NULL"

    where_clause: "WHERE" condition
    condition: CNAME operator value
    operator: "=" | "!=" | ">" | "<" | ">=" | "<="

    %import common.CNAME
    %import common.STRING
    %import common.NUMBER
    %import common.WS
    %ignore WS
    """

    # Python 函數定義語法
    PYTHON_FUNCTION = """
    ?start: function_def

    function_def: "def" CNAME "(" params? ")" ":" suite

    params: param ("," param)*
    param: CNAME

    suite: simple_stmt | NEWLINE INDENT stmt+ DEDENT
    simple_stmt: "return" expr NEWLINE | "pass" NEWLINE
    stmt: simple_stmt | if_stmt | for_stmt

    if_stmt: "if" expr ":" suite ("else" ":" suite)?
    for_stmt: "for" CNAME "in" expr ":" suite

    expr: CNAME | NUMBER | STRING | binary_op | func_call
    binary_op: expr ("+" | "-" | "*" | "/" | "==" | "!=" | "<" | ">") expr
    func_call: CNAME "(" (expr ("," expr)*)? ")"

    %import common.CNAME
    %import common.NUMBER
    %import common.STRING
    %import common.NEWLINE
    %import common.INDENT
    %import common.DEDENT
    %import common.WS
    %ignore WS
    """

    # JSON 語法
    JSON_GRAMMAR = """
    ?start: value

    value: object
         | array
         | STRING
         | NUMBER
         | "true"
         | "false"
         | "null"

    object: "{" [pair ("," pair)*] "}"
    pair: STRING ":" value

    array: "[" [value ("," value)*] "]"

    %import common.STRING
    %import common.NUMBER
    %import common.WS
    %ignore WS
    """

    # 算術表達式語法
    ARITHMETIC = """
    ?start: expr

    expr: term
        | expr "+" term
        | expr "-" term

    term: factor
        | term "*" factor
        | term "/" factor

    factor: NUMBER
          | "(" expr ")"
          | CNAME

    %import common.CNAME
    %import common.NUMBER
    %import common.WS
    %ignore WS
    """

    # 配置文件語法
    CONFIG = """
    ?start: config

    config: section+

    section: "[" CNAME "]" NEWLINE assignment+

    assignment: CNAME "=" value NEWLINE

    value: STRING | NUMBER | CNAME

    %import common.CNAME
    %import common.STRING
    %import common.NUMBER
    %import common.NEWLINE
    %import common.WS
    %ignore WS
    """


# ==================== 語法生成管理器 ====================

class GrammarGenerationManager:
    """
    語法生成管理器

    管理基於上下文無關語法的生成
    """

    def __init__(self, model_name: str = "mistralai/Mistral-7B-v0.1"):
        """
        初始化管理器

        Args:
            model_name: 模型名稱
        """
        self.model_name = model_name
        self.model = None
        self.grammars = GrammarDefinitions()
        self.load_model()

        logger.info(f"語法生成管理器初始化完成")

    def load_model(self):
        """載入模型"""
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = models.transformers(self.model_name, device=device)
            logger.info("模型載入完成")
        except Exception as e:
            logger.error(f"模型載入失敗: {str(e)}")
            raise

    def generate_with_grammar(
        self,
        prompt: str,
        grammar: str
    ) -> str:
        """
        使用語法生成

        Args:
            prompt: 提示
            grammar: 語法定義

        Returns:
            生成的文本
        """
        try:
            logger.info(f"使用語法生成")

            # 創建語法生成器
            generator = generate.cfg(self.model, grammar)

            # 生成結果
            result = generator(prompt)

            logger.info(f"生成成功: {result[:100]}...")
            return result

        except Exception as e:
            logger.error(f"語法生成失敗: {str(e)}")
            raise


# ==================== SQL 生成器 ====================

class SQLGenerator:
    """
    SQL 生成器

    生成各種 SQL 語句
    """

    def __init__(self, manager: GrammarGenerationManager):
        """
        初始化 SQL 生成器

        Args:
            manager: 語法生成管理器
        """
        self.manager = manager
        logger.info("SQL 生成器初始化完成")

    def generate_select(
        self,
        description: str
    ) -> str:
        """
        生成 SELECT 語句

        Args:
            description: 查詢描述

        Returns:
            SQL SELECT 語句
        """
        prompt = f"生成 SQL 查詢: {description}"
        sql = self.manager.generate_with_grammar(
            prompt,
            self.manager.grammars.SQL_SELECT
        )

        logger.info(f"生成 SELECT: {sql}")
        return sql

    def generate_insert(
        self,
        table: str,
        description: str
    ) -> str:
        """
        生成 INSERT 語句

        Args:
            table: 表名
            description: 插入描述

        Returns:
            SQL INSERT 語句
        """
        prompt = f"生成插入 {table} 表的 SQL: {description}"
        sql = self.manager.generate_with_grammar(
            prompt,
            self.manager.grammars.SQL_INSERT
        )

        logger.info(f"生成 INSERT: {sql}")
        return sql

    def generate_update(
        self,
        table: str,
        description: str
    ) -> str:
        """
        生成 UPDATE 語句

        Args:
            table: 表名
            description: 更新描述

        Returns:
            SQL UPDATE 語句
        """
        prompt = f"生成更新 {table} 表的 SQL: {description}"
        sql = self.manager.generate_with_grammar(
            prompt,
            self.manager.grammars.SQL_UPDATE
        )

        logger.info(f"生成 UPDATE: {sql}")
        return sql

    def generate_query_for_analytics(
        self,
        metric: str,
        table: str
    ) -> str:
        """
        生成分析查詢

        Args:
            metric: 指標名稱
            table: 表名

        Returns:
            SQL 查詢語句
        """
        prompt = f"生成計算 {table} 表中 {metric} 的 SQL 查詢"
        sql = self.manager.generate_with_grammar(
            prompt,
            self.manager.grammars.SQL_SELECT
        )

        return sql


# ==================== Python 代碼生成器 ====================

class PythonCodeGenerator:
    """
    Python 代碼生成器

    生成 Python 代碼片段
    """

    def __init__(self, manager: GrammarGenerationManager):
        """
        初始化 Python 代碼生成器

        Args:
            manager: 語法生成管理器
        """
        self.manager = manager
        logger.info("Python 代碼生成器初始化完成")

    def generate_function(
        self,
        description: str
    ) -> str:
        """
        生成函數定義

        Args:
            description: 函數描述

        Returns:
            Python 函數代碼
        """
        prompt = f"生成 Python 函數: {description}"
        code = self.manager.generate_with_grammar(
            prompt,
            self.manager.grammars.PYTHON_FUNCTION
        )

        logger.info(f"生成函數: {code[:100]}...")
        return code

    def generate_utility_function(
        self,
        function_name: str,
        purpose: str
    ) -> str:
        """
        生成工具函數

        Args:
            function_name: 函數名稱
            purpose: 函數用途

        Returns:
            Python 函數代碼
        """
        prompt = f"生成名為 {function_name} 的函數,用於 {purpose}"
        code = self.manager.generate_with_grammar(
            prompt,
            self.manager.grammars.PYTHON_FUNCTION
        )

        return code

    def generate_data_processing_function(
        self,
        input_type: str,
        output_type: str
    ) -> str:
        """
        生成數據處理函數

        Args:
            input_type: 輸入類型
            output_type: 輸出類型

        Returns:
            Python 函數代碼
        """
        prompt = f"生成處理 {input_type} 並返回 {output_type} 的函數"
        code = self.manager.generate_with_grammar(
            prompt,
            self.manager.grammars.PYTHON_FUNCTION
        )

        return code


# ==================== 算術表達式生成器 ====================

class ArithmeticGenerator:
    """
    算術表達式生成器

    生成數學表達式
    """

    def __init__(self, manager: GrammarGenerationManager):
        """
        初始化算術表達式生成器

        Args:
            manager: 語法生成管理器
        """
        self.manager = manager
        logger.info("算術表達式生成器初始化完成")

    def generate_expression(
        self,
        description: str
    ) -> str:
        """
        生成算術表達式

        Args:
            description: 表達式描述

        Returns:
            算術表達式
        """
        prompt = f"生成算術表達式: {description}"
        expr = self.manager.generate_with_grammar(
            prompt,
            self.manager.grammars.ARITHMETIC
        )

        logger.info(f"生成表達式: {expr}")
        return expr

    def generate_formula(
        self,
        variables: List[str],
        operation: str
    ) -> str:
        """
        生成公式

        Args:
            variables: 變量列表
            operation: 操作描述

        Returns:
            算術公式
        """
        vars_str = ", ".join(variables)
        prompt = f"使用變量 {vars_str} 生成 {operation} 的公式"
        formula = self.manager.generate_with_grammar(
            prompt,
            self.manager.grammars.ARITHMETIC
        )

        return formula


# ==================== 自定義語法生成器 ====================

class CustomGrammarGenerator:
    """
    自定義語法生成器

    支持用戶定義的語法
    """

    def __init__(self, manager: GrammarGenerationManager):
        """
        初始化自定義語法生成器

        Args:
            manager: 語法生成管理器
        """
        self.manager = manager
        self.custom_grammars: Dict[str, str] = {}
        logger.info("自定義語法生成器初始化完成")

    def register_grammar(
        self,
        name: str,
        grammar: str
    ):
        """
        註冊自定義語法

        Args:
            name: 語法名稱
            grammar: 語法定義
        """
        self.custom_grammars[name] = grammar
        logger.info(f"註冊語法: {name}")

    def generate(
        self,
        grammar_name: str,
        prompt: str
    ) -> str:
        """
        使用自定義語法生成

        Args:
            grammar_name: 語法名稱
            prompt: 提示

        Returns:
            生成的文本
        """
        if grammar_name not in self.custom_grammars:
            raise ValueError(f"未找到語法: {grammar_name}")

        grammar = self.custom_grammars[grammar_name]
        result = self.manager.generate_with_grammar(prompt, grammar)

        return result

    def generate_email_template(self) -> str:
        """
        生成郵件模板

        Returns:
            郵件模板
        """
        # 定義郵件模板語法
        email_grammar = """
        ?start: email

        email: header NEWLINE NEWLINE body NEWLINE NEWLINE signature

        header: "To:" STRING NEWLINE "Subject:" STRING

        body: paragraph+
        paragraph: sentence+ NEWLINE

        sentence: WORD+
        WORD: /[a-zA-Z]+/

        signature: "Best regards," NEWLINE CNAME

        %import common.CNAME
        %import common.STRING
        %import common.NEWLINE
        %import common.WS
        %ignore WS
        """

        self.register_grammar("email", email_grammar)
        result = self.generate("email", "生成一封專業的郵件")

        return result

    def generate_log_entry(self) -> str:
        """
        生成日誌條目

        Returns:
            日誌條目
        """
        # 定義日誌語法
        log_grammar = """
        ?start: log_entry

        log_entry: timestamp level source message

        timestamp: "[" DATE TIME "]"
        DATE: /\\d{4}-\\d{2}-\\d{2}/
        TIME: /\\d{2}:\\d{2}:\\d{2}/

        level: "[" ("INFO" | "WARNING" | "ERROR" | "DEBUG") "]"

        source: CNAME ":"

        message: STRING

        %import common.CNAME
        %import common.STRING
        %import common.WS
        %ignore WS
        """

        self.register_grammar("log", log_grammar)
        result = self.generate("log", "生成一條錯誤日誌")

        return result


# ==================== 語法驗證器 ====================

@dataclass
class ValidationResult:
    """驗證結果"""
    is_valid: bool
    error_message: Optional[str] = None
    parsed_tree: Optional[Any] = None


class GrammarValidator:
    """
    語法驗證器

    驗證生成的代碼是否符合語法
    """

    @staticmethod
    def validate_sql(sql: str) -> ValidationResult:
        """
        驗證 SQL 語句

        Args:
            sql: SQL 語句

        Returns:
            驗證結果
        """
        # 簡單的 SQL 驗證
        sql = sql.strip().upper()

        valid_starts = ['SELECT', 'INSERT', 'UPDATE', 'DELETE']
        if not any(sql.startswith(cmd) for cmd in valid_starts):
            return ValidationResult(
                is_valid=False,
                error_message="SQL 語句必須以有效的命令開頭"
            )

        return ValidationResult(is_valid=True)

    @staticmethod
    def validate_python(code: str) -> ValidationResult:
        """
        驗證 Python 代碼

        Args:
            code: Python 代碼

        Returns:
            驗證結果
        """
        try:
            compile(code, '<string>', 'exec')
            return ValidationResult(is_valid=True)
        except SyntaxError as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"語法錯誤: {str(e)}"
            )

    @staticmethod
    def validate_arithmetic(expr: str) -> ValidationResult:
        """
        驗證算術表達式

        Args:
            expr: 算術表達式

        Returns:
            驗證結果
        """
        # 檢查是否包含有效字符
        valid_chars = set('0123456789+-*/() ')
        if not all(c in valid_chars or c.isalpha() for c in expr):
            return ValidationResult(
                is_valid=False,
                error_message="包含無效字符"
            )

        return ValidationResult(is_valid=True)


# ==================== 示例運行器 ====================

def run_sql_generation_example():
    """運行 SQL 生成示例"""
    print("\n" + "="*60)
    print("示例 1: SQL 語句生成")
    print("="*60)

    manager = GrammarGenerationManager()
    generator = SQLGenerator(manager)

    # 生成 SELECT 語句
    print("\n生成 SELECT 語句:")
    queries = [
        "查詢所有用戶",
        "查詢年齡大於18的用戶",
        "查詢銷售總額"
    ]

    for query_desc in queries:
        try:
            sql = generator.generate_select(query_desc)
            print(f"  描述: {query_desc}")
            print(f"  SQL: {sql}\n")

            # 驗證
            result = GrammarValidator.validate_sql(sql)
            if result.is_valid:
                print("  ✓ 驗證通過\n")
            else:
                print(f"  ✗ 驗證失敗: {result.error_message}\n")
        except Exception as e:
            print(f"  生成失敗: {str(e)}\n")


def run_python_generation_example():
    """運行 Python 代碼生成示例"""
    print("\n" + "="*60)
    print("示例 2: Python 代碼生成")
    print("="*60)

    manager = GrammarGenerationManager()
    generator = PythonCodeGenerator(manager)

    # 生成函數
    print("\n生成 Python 函數:")
    functions = [
        "計算兩個數的和",
        "檢查數字是否為偶數",
        "查找列表中的最大值"
    ]

    for func_desc in functions:
        try:
            code = generator.generate_function(func_desc)
            print(f"  描述: {func_desc}")
            print(f"  代碼:\n{code}\n")

            # 驗證
            result = GrammarValidator.validate_python(code)
            if result.is_valid:
                print("  ✓ 語法有效\n")
            else:
                print(f"  ✗ 語法錯誤: {result.error_message}\n")
        except Exception as e:
            print(f"  生成失敗: {str(e)}\n")


def run_arithmetic_generation_example():
    """運行算術表達式生成示例"""
    print("\n" + "="*60)
    print("示例 3: 算術表達式生成")
    print("="*60)

    manager = GrammarGenerationManager()
    generator = ArithmeticGenerator(manager)

    # 生成表達式
    print("\n生成算術表達式:")
    expressions = [
        "兩個數的和",
        "圓的面積公式",
        "複合利息計算"
    ]

    for expr_desc in expressions:
        try:
            expr = generator.generate_expression(expr_desc)
            print(f"  描述: {expr_desc}")
            print(f"  表達式: {expr}")

            # 驗證
            result = GrammarValidator.validate_arithmetic(expr)
            if result.is_valid:
                print("  ✓ 驗證通過\n")
            else:
                print(f"  ✗ 驗證失敗: {result.error_message}\n")
        except Exception as e:
            print(f"  生成失敗: {str(e)}\n")


def run_custom_grammar_example():
    """運行自定義語法示例"""
    print("\n" + "="*60)
    print("示例 4: 自定義語法生成")
    print("="*60)

    manager = GrammarGenerationManager()
    generator = CustomGrammarGenerator(manager)

    # 生成郵件模板
    print("\n生成郵件模板:")
    try:
        email = generator.generate_email_template()
        print(email)
    except Exception as e:
        print(f"生成失敗: {str(e)}")

    # 生成日誌條目
    print("\n生成日誌條目:")
    try:
        log = generator.generate_log_entry()
        print(log)
    except Exception as e:
        print(f"生成失敗: {str(e)}")


def main():
    """主函數"""
    try:
        print("\n開始運行語法生成示例...")

        run_sql_generation_example()
        run_python_generation_example()
        run_arithmetic_generation_example()
        run_custom_grammar_example()

        print("\n" + "="*60)
        print("所有示例運行完成!")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\n用戶中斷執行")
    except Exception as e:
        print(f"\n錯誤: {str(e)}")
        logger.error(f"主程序錯誤: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
