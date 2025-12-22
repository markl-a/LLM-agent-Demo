#!/usr/bin/env python3
"""
Goose 自定義工具示例

展示如何擴展 Goose 的功能:
1. 創建自定義工具
2. 集成外部 API
3. 包裝現有工具
4. 創建工具插件
5. 工具鏈組合

作者: AI Agent
日期: 2024
"""

from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
import json
import subprocess
from pathlib import Path


@dataclass
class ToolMetadata:
    """工具元數據"""
    name: str
    description: str
    parameters: Dict
    returns: str
    examples: List[str]


class CustomToolsDemo:
    """自定義工具演示"""

    def __init__(self):
        """初始化"""
        self.tools = []

    def basic_tool_example(self):
        """
        基本工具範例
        展示如何創建簡單的自定義工具
        """
        print("\n" + "="*70)
        print("基本自定義工具")
        print("="*70)

        # 工具定義範例
        tool_example = '''
# goose_tools/my_tools.py

from goose.toolkit import Tool, tool

@tool
def greet(name: str, language: str = "en") -> str:
    """
    問候工具

    Args:
        name: 要問候的名字
        language: 語言代碼 (en, zh, es, fr)

    Returns:
        問候語

    Example:
        >>> greet("Alice", "en")
        "Hello, Alice!"
    """
    greetings = {
        "en": f"Hello, {name}!",
        "zh": f"你好，{name}！",
        "es": f"¡Hola, {name}!",
        "fr": f"Bonjour, {name}!"
    }
    return greetings.get(language, greetings["en"])


@tool
def calculate_hash(text: str, algorithm: str = "sha256") -> str:
    """
    計算文本哈希值

    Args:
        text: 要哈希的文本
        algorithm: 哈希算法 (md5, sha1, sha256)

    Returns:
        十六進制哈希值
    """
    import hashlib

    algorithms = {
        "md5": hashlib.md5,
        "sha1": hashlib.sha1,
        "sha256": hashlib.sha256,
    }

    if algorithm not in algorithms:
        return f"不支持的算法: {algorithm}"

    hasher = algorithms[algorithm]()
    hasher.update(text.encode('utf-8'))
    return hasher.hexdigest()


@tool
def list_directory(path: str = ".", pattern: str = "*") -> List[str]:
    """
    列出目錄內容

    Args:
        path: 目錄路徑
        pattern: 文件匹配模式

    Returns:
        文件列表
    """
    from pathlib import Path

    directory = Path(path)
    if not directory.exists():
        return [f"目錄不存在: {path}"]

    files = list(directory.glob(pattern))
    return [str(f.relative_to(directory)) for f in files]
'''

        print("\n📝 自定義工具代碼:")
        print("-"*70)
        print(tool_example)

        # 註冊工具
        registration = '''
# 註冊工具到 Goose
# ~/.config/goose/config.yaml

tools:
  custom:
    - module: goose_tools.my_tools
      tools:
        - greet
        - calculate_hash
        - list_directory
'''

        print("\n📋 工具註冊:")
        print("-"*70)
        print(registration)

        # 使用示例
        usage = '''
# 在 Goose 中使用自定義工具

# 問候
> 用中文問候 Alice
Goose 將調用: greet("Alice", "zh")
輸出: 你好，Alice！

# 計算哈希
> 計算 "hello world" 的 SHA256 哈希
Goose 將調用: calculate_hash("hello world", "sha256")

# 列出文件
> 列出當前目錄的所有 Python 文件
Goose 將調用: list_directory(".", "*.py")
'''

        print("\n💡 使用示例:")
        print("-"*70)
        print(usage)

    def api_integration_example(self):
        """
        API 集成示例
        展示如何將外部 API 包裝為工具
        """
        print("\n" + "="*70)
        print("API 集成工具")
        print("="*70)

        # 天氣 API 工具
        weather_tool = '''
# goose_tools/weather.py

import requests
from typing import Dict, Optional
from goose.toolkit import tool

@tool
def get_weather(city: str, units: str = "metric") -> Dict:
    """
    獲取城市天氣

    Args:
        city: 城市名稱
        units: 單位系統 (metric, imperial)

    Returns:
        天氣信息字典
    """
    import os

    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return {"error": "未設置 API Key"}

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": units
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"]
        }

    except requests.RequestException as e:
        return {"error": str(e)}


@tool
def search_github(query: str, max_results: int = 5) -> List[Dict]:
    """
    搜索 GitHub 倉庫

    Args:
        query: 搜索關鍵詞
        max_results: 最大結果數

    Returns:
        倉庫列表
    """
    url = "https://api.github.com/search/repositories"
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": max_results
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        return [
            {
                "name": repo["full_name"],
                "description": repo["description"],
                "stars": repo["stargazers_count"],
                "url": repo["html_url"]
            }
            for repo in data["items"]
        ]

    except requests.RequestException as e:
        return [{"error": str(e)}]


@tool
def translate_text(text: str, target_lang: str = "en") -> str:
    """
    翻譯文本（使用 DeepL API）

    Args:
        text: 要翻譯的文本
        target_lang: 目標語言代碼

    Returns:
        翻譯後的文本
    """
    import os

    api_key = os.getenv("DEEPL_API_KEY")
    url = "https://api-free.deepl.com/v2/translate"

    data = {
        "auth_key": api_key,
        "text": text,
        "target_lang": target_lang.upper()
    }

    response = requests.post(url, data=data)
    result = response.json()

    return result["translations"][0]["text"]
'''

        print("\n🌐 API 集成工具:")
        print("-"*70)
        print(weather_tool)

    def database_tool_example(self):
        """
        數據庫工具示例
        展示如何創建數據庫操作工具
        """
        print("\n" + "="*70)
        print("數據庫操作工具")
        print("="*70)

        db_tools = '''
# goose_tools/database.py

from typing import List, Dict, Optional
from goose.toolkit import tool
import sqlite3
import pandas as pd

@tool
def query_database(
    query: str,
    database: str = "default.db",
    params: Optional[tuple] = None
) -> List[Dict]:
    """
    執行 SQL 查詢

    Args:
        query: SQL 查詢語句
        database: 數據庫文件路徑
        params: 查詢參數（防止 SQL 注入）

    Returns:
        查詢結果列表
    """
    try:
        conn = sqlite3.connect(database)
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return results

    except sqlite3.Error as e:
        return [{"error": str(e)}]


@tool
def export_to_csv(
    query: str,
    output_file: str,
    database: str = "default.db"
) -> str:
    """
    將查詢結果導出為 CSV

    Args:
        query: SQL 查詢
        output_file: 輸出文件路徑
        database: 數據庫文件

    Returns:
        狀態消息
    """
    try:
        conn = sqlite3.connect(database)
        df = pd.read_sql_query(query, conn)
        df.to_csv(output_file, index=False)
        conn.close()

        return f"已導出 {len(df)} 行數據到 {output_file}"

    except Exception as e:
        return f"導出失敗: {str(e)}"


@tool
def analyze_table(table_name: str, database: str = "default.db") -> Dict:
    """
    分析數據表統計信息

    Args:
        table_name: 表名
        database: 數據庫文件

    Returns:
        統計信息字典
    """
    conn = sqlite3.connect(database)

    # 獲取行數
    count_query = f"SELECT COUNT(*) FROM {table_name}"
    row_count = conn.execute(count_query).fetchone()[0]

    # 獲取列信息
    columns_query = f"PRAGMA table_info({table_name})"
    columns = conn.execute(columns_query).fetchall()

    conn.close()

    return {
        "table": table_name,
        "row_count": row_count,
        "columns": [
            {"name": col[1], "type": col[2]}
            for col in columns
        ]
    }
'''

        print("\n🗄️ 數據庫工具:")
        print("-"*70)
        print(db_tools)

    def advanced_tool_example(self):
        """
        進階工具示例
        展示複雜的工具實現
        """
        print("\n" + "="*70)
        print("進階工具")
        print("="*70)

        advanced_tools = '''
# goose_tools/advanced.py

from goose.toolkit import tool
from typing import List, Dict
import ast
import subprocess
from pathlib import Path

@tool
def analyze_code_complexity(file_path: str) -> Dict:
    """
    分析代碼複雜度

    Args:
        file_path: Python 文件路徑

    Returns:
        複雜度分析結果
    """
    try:
        with open(file_path, 'r') as f:
            code = f.read()

        tree = ast.parse(code)

        # 統計函數數量
        functions = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        ]

        # 統計類數量
        classes = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
        ]

        # 計算代碼行數
        lines = len(code.splitlines())
        code_lines = len([
            line for line in code.splitlines()
            if line.strip() and not line.strip().startswith('#')
        ])

        return {
            "file": file_path,
            "total_lines": lines,
            "code_lines": code_lines,
            "functions": len(functions),
            "classes": len(classes),
            "avg_function_length": code_lines // len(functions) if functions else 0
        }

    except Exception as e:
        return {"error": str(e)}


@tool
def run_code_quality_check(directory: str = ".") -> Dict:
    """
    運行代碼質量檢查

    使用 pylint, black, mypy 等工具

    Args:
        directory: 要檢查的目錄

    Returns:
        質量檢查結果
    """
    results = {}

    # 運行 pylint
    try:
        pylint_output = subprocess.run(
            ["pylint", directory],
            capture_output=True,
            text=True,
            timeout=30
        )
        results["pylint"] = pylint_output.stdout

    except subprocess.TimeoutExpired:
        results["pylint"] = "超時"
    except FileNotFoundError:
        results["pylint"] = "未安裝 pylint"

    # 運行 black（檢查格式）
    try:
        black_output = subprocess.run(
            ["black", "--check", directory],
            capture_output=True,
            text=True,
            timeout=30
        )
        results["black"] = "格式正確" if black_output.returncode == 0 else "需要格式化"

    except FileNotFoundError:
        results["black"] = "未安裝 black"

    # 運行 mypy（類型檢查）
    try:
        mypy_output = subprocess.run(
            ["mypy", directory],
            capture_output=True,
            text=True,
            timeout=30
        )
        results["mypy"] = mypy_output.stdout

    except FileNotFoundError:
        results["mypy"] = "未安裝 mypy"

    return results


@tool
def generate_project_structure(root_dir: str = ".") -> str:
    """
    生成項目結構樹

    Args:
        root_dir: 項目根目錄

    Returns:
        ASCII 樹形結構
    """
    from pathlib import Path

    def build_tree(directory: Path, prefix: str = "", is_last: bool = True):
        """遞歸構建目錄樹"""
        contents = list(directory.iterdir())

        # 過濾掉不需要的目錄
        contents = [
            item for item in contents
            if not item.name.startswith('.')
            and item.name not in ['__pycache__', 'node_modules', 'venv']
        ]

        tree = []
        for i, path in enumerate(contents):
            is_last_item = i == len(contents) - 1
            connector = "└── " if is_last_item else "├── "

            tree.append(f"{prefix}{connector}{path.name}")

            if path.is_dir():
                extension = "    " if is_last_item else "│   "
                tree.extend(build_tree(path, prefix + extension, is_last_item))

        return tree

    root = Path(root_dir)
    tree = [str(root)]
    tree.extend(build_tree(root))

    return "\\n".join(tree)
'''

        print("\n🔧 進階工具:")
        print("-"*70)
        print(advanced_tools)

    def tool_composition_example(self):
        """
        工具組合示例
        展示如何組合多個工具創建工作流
        """
        print("\n" + "="*70)
        print("工具組合與工作流")
        print("="*70)

        composition = '''
# goose_tools/workflows.py

from goose.toolkit import tool, ToolChain
from typing import Dict

@tool
def code_review_workflow(file_path: str) -> Dict:
    """
    完整代碼審查工作流

    組合多個工具進行全面審查

    Args:
        file_path: 要審查的文件

    Returns:
        審查報告
    """
    results = {}

    # 1. 分析複雜度
    results["complexity"] = analyze_code_complexity(file_path)

    # 2. 運行靜態分析
    results["linting"] = run_pylint(file_path)

    # 3. 檢查格式
    results["formatting"] = check_formatting(file_path)

    # 4. 類型檢查
    results["type_check"] = run_mypy(file_path)

    # 5. 安全檢查
    results["security"] = security_scan(file_path)

    # 6. 生成建議
    results["suggestions"] = generate_suggestions(results)

    return results


@tool
def deploy_workflow(
    environment: str = "staging",
    run_tests: bool = True
) -> Dict:
    """
    部署工作流

    Args:
        environment: 部署環境
        run_tests: 是否運行測試

    Returns:
        部署結果
    """
    steps = []

    # 1. 運行測試（可選）
    if run_tests:
        test_result = run_all_tests()
        steps.append({"step": "tests", "result": test_result})

        if not test_result["passed"]:
            return {"status": "failed", "reason": "tests_failed", "steps": steps}

    # 2. 構建
    build_result = build_project()
    steps.append({"step": "build", "result": build_result})

    # 3. 部署
    deploy_result = deploy_to_environment(environment)
    steps.append({"step": "deploy", "result": deploy_result})

    # 4. 驗證
    verify_result = verify_deployment(environment)
    steps.append({"step": "verify", "result": verify_result})

    return {
        "status": "success",
        "environment": environment,
        "steps": steps
    }
'''

        print("\n⚙️ 工作流工具:")
        print("-"*70)
        print(composition)

    def plugin_system_example(self):
        """
        插件系統示例
        展示如何創建 Goose 插件
        """
        print("\n" + "="*70)
        print("插件系統")
        print("="*70)

        plugin_example = '''
# my_goose_plugin/plugin.py

from goose.plugin import Plugin
from goose.toolkit import tool

class MyPlugin(Plugin):
    """自定義 Goose 插件"""

    # 插件元數據
    name = "my_plugin"
    version = "1.0.0"
    description = "我的自定義 Goose 插件"
    author = "Your Name"

    def __init__(self, config: dict = None):
        """初始化插件"""
        super().__init__()
        self.config = config or {}
        self.tools = []

    def load(self):
        """加載插件時調用"""
        print(f"加載插件: {self.name}")

        # 註冊工具
        self.register_tool("my_tool", self.my_tool)
        self.register_tool("another_tool", self.another_tool)

        # 註冊事件處理器
        self.on("before_execute", self.before_execute_handler)
        self.on("after_execute", self.after_execute_handler)

    def unload(self):
        """卸載插件時調用"""
        print(f"卸載插件: {self.name}")

    @tool
    def my_tool(self, arg: str) -> str:
        """插件提供的工具"""
        return f"處理: {arg}"

    @tool
    def another_tool(self, data: dict) -> dict:
        """另一個工具"""
        # 工具邏輯
        return {"processed": True, "data": data}

    def before_execute_handler(self, event):
        """執行前的事件處理器"""
        print("工具執行前...")

    def after_execute_handler(self, event):
        """執行後的事件處理器"""
        print("工具執行後...")


# setup.py（用於安裝插件）

from setuptools import setup, find_packages

setup(
    name="my-goose-plugin",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "goose-ai>=0.1.0",
    ],
    entry_points={
        "goose.plugins": [
            "my_plugin=my_goose_plugin.plugin:MyPlugin",
        ],
    },
)
'''

        print("\n🔌 插件示例:")
        print("-"*70)
        print(plugin_example)

        # 安裝和使用
        usage = '''
# 安裝插件
$ pip install my-goose-plugin

# 或從本地安裝
$ pip install -e ./my-goose-plugin

# 啟用插件
# ~/.config/goose/config.yaml
plugins:
  enabled:
    - my_plugin

  my_plugin:
    setting1: value1
    setting2: value2

# 使用插件提供的工具
$ goose
> 使用 my_tool 處理數據
'''

        print("\n💡 安裝和使用:")
        print("-"*70)
        print(usage)


def main():
    """主函數"""
    print("="*70)
    print("Goose 自定義工具教程")
    print("="*70)

    demo = CustomToolsDemo()

    sections = [
        ("基本工具", demo.basic_tool_example),
        ("API 集成", demo.api_integration_example),
        ("數據庫工具", demo.database_tool_example),
        ("進階工具", demo.advanced_tool_example),
        ("工具組合", demo.tool_composition_example),
        ("插件系統", demo.plugin_system_example),
    ]

    print("\n執行所有示例...\n")

    for name, func in sections:
        func()

    print("\n" + "="*70)
    print("教程完成！")
    print("="*70)

    print("\n關鍵要點:")
    print("1. 使用 @tool 裝飾器創建工具")
    print("2. 提供清晰的文檔字符串和類型提示")
    print("3. 集成外部 API 擴展功能")
    print("4. 組合工具創建工作流")
    print("5. 使用插件系統打包和分發工具")

    print("\n下一步: 閱讀 06_配置文件.py")


if __name__ == "__main__":
    main()
