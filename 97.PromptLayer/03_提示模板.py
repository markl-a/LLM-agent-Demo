"""
PromptLayer 提示模板示例

本示例展示：
1. 創建提示模板
2. 使用模板變量
3. 模板版本管理
4. 模板性能分析
"""

import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

load_dotenv()
console = Console()


def create_template_via_web():
    """通過 Web 界面創建模板"""
    console.print("\n[cyan]1. 通過 Web 界面創建模板[/cyan]\n")

    steps = """步驟：
1. 訪問 https://www.promptlayer.com
2. 登錄賬號
3. 點擊左側 "Templates"
4. 點擊 "Create Template"
5. 填寫模板信息：
   - Name: customer_service_greeting
   - Prompt: 你好 {{customer_name}}，我是客服助手。你的問題是：{{question}}
   - Variables: customer_name, question
6. 保存模板"""

    console.print(Panel(steps, border_style="cyan"))
    console.print()


def use_template():
    """使用模板"""
    console.print("[cyan]2. 使用提示模板[/cyan]\n")

    code = """import promptlayer

promptlayer.api_key = os.getenv("PROMPTLAYER_API_KEY")

# 運行模板
response = promptlayer.run(
    prompt_name="customer_service_greeting",
    input_variables={
        "customer_name": "張三",
        "question": "如何退款？"
    },
    # 可選參數
    prompt_version=1,  # 指定版本
    tags=["customer-service", "production"],
    return_metadata=True
)

print(f"生成的提示: {response['prompt']}")
print(f"LLM 響應: {response['response']}")
print(f"使用的版本: {response['version']}")
print(f"請求 ID: {response['request_id']}")
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def template_with_system_prompt():
    """帶系統提示的模板"""
    console.print("[cyan]3. 帶系統提示的模板[/cyan]\n")

    example = """模板名稱: translation_template

系統提示:
你是一個專業的翻譯助手。請將用戶的文本翻譯成 {{target_language}}。

用戶提示:
請翻譯以下文本：
{{text}}

變量:
- target_language: 目標語言
- text: 要翻譯的文本
"""

    console.print(Panel(example, title="模板示例", border_style="cyan"))
    console.print()

    code = """# 使用翻譯模板
response = promptlayer.run(
    prompt_name="translation_template",
    input_variables={
        "target_language": "英文",
        "text": "這是一個測試"
    }
)

print(response['response'])
# 輸出: "This is a test"
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def template_with_examples():
    """帶示例的模板"""
    console.print("[cyan]4. 帶示例的 Few-Shot 模板[/cyan]\n")

    template_example = """模板名稱: sentiment_analysis

提示:
分析以下文本的情感傾向，返回"正面"、"負面"或"中性"。

示例:
輸入: 這個產品太棒了！
輸出: 正面

輸入: 服務很差，不推薦。
輸出: 負面

輸入: 還可以吧。
輸出: 中性

現在請分析:
輸入: {{text}}
輸出:
"""

    console.print(Panel(template_example, title="Few-Shot 模板", border_style="cyan"))
    console.print()


def manage_template_versions():
    """管理模板版本"""
    console.print("[cyan]5. 模板版本管理[/cyan]\n")

    code = """# 使用特定版本
response_v1 = promptlayer.run(
    prompt_name="greeting_template",
    prompt_version=1,  # 使用版本 1
    input_variables={"name": "用戶"}
)

# 使用最新版本（默認）
response_latest = promptlayer.run(
    prompt_name="greeting_template",
    # 不指定版本，使用最新版
    input_variables={"name": "用戶"}
)

# 獲取模板的所有版本
import requests

def get_template_versions(template_name):
    url = "https://api.promptlayer.com/rest/get-template-versions"
    params = {
        "api_key": os.getenv("PROMPTLAYER_API_KEY"),
        "template_name": template_name
    }
    response = requests.get(url, params=params)
    return response.json()

versions = get_template_versions("greeting_template")
for version in versions:
    print(f"版本 {version['version']}: {version['created_at']}")
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def programmatic_template_creation():
    """程序化創建模板"""
    console.print("[cyan]6. 程序化創建和更新模板[/cyan]\n")

    code = """import requests

def create_template(name, prompt_template, variables):
    \"\"\"創建新模板\"\"\"
    url = "https://api.promptlayer.com/rest/create-template"

    data = {
        "api_key": os.getenv("PROMPTLAYER_API_KEY"),
        "template_name": name,
        "prompt_template": prompt_template,
        "variables": variables
    }

    response = requests.post(url, json=data)
    return response.json()


def update_template(name, prompt_template, variables):
    \"\"\"更新模板（創建新版本）\"\"\"
    url = "https://api.promptlayer.com/rest/update-template"

    data = {
        "api_key": os.getenv("PROMPTLAYER_API_KEY"),
        "template_name": name,
        "prompt_template": prompt_template,
        "variables": variables
    }

    response = requests.post(url, json=data)
    return response.json()


# 創建模板
result = create_template(
    name="code_review",
    prompt_template=\"\"\"請審查以下代碼：

語言：{{language}}
代碼：
{{code}}

請指出潛在問題和改進建議。\"\"\",
    variables=["language", "code"]
)

print(f"模板已創建: {result}")

# 更新模板（新版本）
update_result = update_template(
    name="code_review",
    prompt_template=\"\"\"請審查以下 {{language}} 代碼：

```{{language}}
{{code}}
```

請從以下角度審查：
1. 代碼質量
2. 潛在 bug
3. 性能問題
4. 安全隱患
5. 改進建議
\"\"\",
    variables=["language", "code"]
)

print(f"模板已更新到版本: {update_result['version']}")
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def template_analytics():
    """模板分析"""
    console.print("[cyan]7. 模板性能分析[/cyan]\n")

    code = """def analyze_template_usage(template_name):
    \"\"\"分析模板使用情況\"\"\"

    # 獲取使用此模板的所有請求
    url = "https://api.promptlayer.com/rest/search-requests"
    params = {
        "api_key": os.getenv("PROMPTLAYER_API_KEY"),
        "template_name": template_name
    }

    response = requests.post(url, json=params)
    requests_data = response.json()

    # 統計分析
    total_requests = len(requests_data)
    avg_latency = sum(r['latency'] for r in requests_data) / total_requests
    total_tokens = sum(r['total_tokens'] for r in requests_data)
    avg_score = sum(r.get('score', 0) for r in requests_data if r.get('score')) / total_requests

    print(f"=== 模板分析: {template_name} ===")
    print(f"總使用次數: {total_requests}")
    print(f"平均延遲: {avg_latency:.2f}秒")
    print(f"總 Token 使用: {total_tokens}")
    print(f"平均評分: {avg_score:.1f}/100")

    # 按版本分組
    from collections import defaultdict
    version_stats = defaultdict(int)
    for req in requests_data:
        version = req.get('template_version', 'unknown')
        version_stats[version] += 1

    print("\\n按版本使用統計:")
    for version, count in version_stats.items():
        print(f"  版本 {version}: {count} 次")


# 分析模板
analyze_template_usage("customer_service_greeting")
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_best_practices():
    """模板管理最佳實踐"""
    console.print("[cyan]模板管理最佳實踐[/cyan]\n")

    practices = """1. 命名規範
   - 使用描述性名稱
   - 包含功能和用途
   - 遵循團隊命名約定
   - 避免特殊字符

2. 變量設計
   - 變量名清晰明確
   - 提供默認值（如適用）
   - 文檔說明變量用途
   - 驗證輸入數據

3. 版本控制
   - 重大更改創建新版本
   - 記錄變更說明
   - 測試後再更新生產版本
   - 保留關鍵版本歷史

4. 質量保證
   - 測試不同的變量組合
   - 收集用戶反饋
   - 定期審查和優化
   - A/B 測試新版本

5. 文檔化
   - 註明模板用途
   - 說明變量含義
   - 提供使用示例
   - 記錄最佳實踐

6. 性能監控
   - 追蹤使用頻率
   - 監控平均評分
   - 分析 token 使用
   - 識別優化機會"""

    console.print(Panel(practices, border_style="cyan"))
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]PromptLayer 提示模板示例[/bold cyan]\n"
        "[dim]學習如何管理和使用提示模板[/dim]",
        border_style="cyan"
    ))

    # 1. Web 創建
    create_template_via_web()

    # 2. 使用模板
    use_template()

    # 3. 系統提示模板
    template_with_system_prompt()

    # 4. Few-Shot 模板
    template_with_examples()

    # 5. 版本管理
    manage_template_versions()

    # 6. 程序化創建
    programmatic_template_creation()

    # 7. 模板分析
    template_analytics()

    # 8. 最佳實踐
    show_best_practices()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 提示模板示例完成！[/bold green]\n")
    console.print("[cyan]下一步:[/cyan]")
    console.print("  1. 查看 04_版本管理.py - 深入版本控制")
    console.print("  2. 查看 05_AB測試.py - 進行模板 A/B 測試")
    console.print("  3. 實踐: 創建和管理自己的模板庫")


if __name__ == "__main__":
    main()
