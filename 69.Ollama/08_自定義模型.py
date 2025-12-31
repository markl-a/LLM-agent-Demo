"""
Ollama 自定義模型示例

本示例展示：
1. Modelfile 基礎
2. 自定義系統提示詞
3. 參數調整
4. 創建專用模型
5. 模型繼承和修改
"""

import ollama
import subprocess
import tempfile
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown

console = Console()


def create_basic_modelfile():
    """創建基礎 Modelfile"""
    try:
        console.print("\n[bold cyan]基礎 Modelfile 示例[/bold cyan]")

        # 基礎 Modelfile 內容
        modelfile_content = """FROM llama3.2

# 設置溫度參數
PARAMETER temperature 0.7

# 設置系統提示詞
SYSTEM \"\"\"
你是一個友好、樂於助人的 AI 助手。
請用簡潔、清晰的語言回答問題。
\"\"\"
"""

        console.print("\n[bold]Modelfile 內容:[/bold]")
        console.print(Panel(
            Syntax(modelfile_content, "dockerfile", theme="monokai"),
            title="[bold yellow]Modelfile[/bold yellow]",
            border_style="yellow"
        ))

        console.print("\n[bold]Modelfile 組成:[/bold]")
        console.print("  • FROM: 基礎模型")
        console.print("  • PARAMETER: 模型參數")
        console.print("  • SYSTEM: 系統提示詞")
        console.print("  • TEMPLATE: 提示詞模板（可選）")
        console.print("  • LICENSE: 授權信息（可選）")

        return modelfile_content

    except Exception as e:
        console.print(f"[red]創建 Modelfile 失敗: {e}[/red]")
        return None


def create_specialized_model(base_model='llama3.2'):
    """創建專用模型"""
    try:
        console.print("\n[bold cyan]創建專用模型示例[/bold cyan]")

        # Python 導師模型
        python_tutor_modelfile = f"""FROM {base_model}

# 設置參數
PARAMETER temperature 0.8
PARAMETER top_p 0.9
PARAMETER top_k 40

# 系統提示詞
SYSTEM \"\"\"
你是一位資深的 Python 編程導師。你的特點：

1. 教學風格：
   - 用簡單的語言解釋複雜概念
   - 總是提供實際的代碼示例
   - 鼓勵最佳實踐和 Pythonic 寫法

2. 回答格式：
   - 先解釋概念
   - 然後提供代碼示例
   - 最後給出實用建議

3. 態度：
   - 友好且有耐心
   - 鼓勵學習者提問
   - 從不批評，只提建設性意見

請始終保持這個角色和風格。
\"\"\"
"""

        console.print("\n[bold yellow]Python 導師模型 Modelfile:[/bold yellow]")
        console.print(Panel(
            Syntax(python_tutor_modelfile, "dockerfile", theme="monokai"),
            border_style="yellow"
        ))

        # 創建模型的命令
        console.print("\n[bold]創建命令:[/bold]")
        console.print("  1. 將 Modelfile 保存到文件")
        console.print("  2. 運行: ollama create python-tutor -f Modelfile")

        console.print("\n[bold]使用示例:[/bold]")
        usage = """import ollama

response = ollama.chat(
    model='python-tutor',
    messages=[{
        'role': 'user',
        'content': '什麼是裝飾器？'
    }]
)
"""
        console.print(Panel(
            Syntax(usage, "python", theme="monokai"),
            border_style="blue"
        ))

        return python_tutor_modelfile

    except Exception as e:
        console.print(f"[red]創建專用模型失敗: {e}[/red]")
        return None


def parameter_configurations():
    """參數配置說明"""
    try:
        console.print("\n[bold cyan]Modelfile 參數配置[/bold cyan]")

        parameters = [
            {
                'name': 'temperature',
                'range': '0.0 - 2.0',
                'default': '0.8',
                'desc': '控制創造性。0=確定性，2=非常創造性'
            },
            {
                'name': 'top_p',
                'range': '0.0 - 1.0',
                'default': '0.9',
                'desc': '核採樣參數。較小值=更專注'
            },
            {
                'name': 'top_k',
                'range': '1 - 100',
                'default': '40',
                'desc': '候選詞數量。較小值=更保守'
            },
            {
                'name': 'num_predict',
                'range': '1 - ∞',
                'default': '-1',
                'desc': '最大生成 token 數。-1=無限制'
            },
            {
                'name': 'num_ctx',
                'range': '1 - 128k',
                'default': '2048',
                'desc': '上下文窗口大小'
            },
            {
                'name': 'repeat_penalty',
                'range': '0.0 - 2.0',
                'default': '1.1',
                'desc': '重複懲罰。>1 減少重複'
            },
            {
                'name': 'seed',
                'range': '0 - ∞',
                'default': '0',
                'desc': '隨機種子。固定值=可重現'
            }
        ]

        from rich.table import Table

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("參數", style="cyan", width=15)
        table.add_column("範圍", style="yellow", width=12)
        table.add_column("默認值", style="green", width=10)
        table.add_column("說明", style="blue", width=35)

        for param in parameters:
            table.add_row(
                param['name'],
                param['range'],
                param['default'],
                param['desc']
            )

        console.print(table)

        # 示例配置
        console.print("\n[bold]示例配置:[/bold]")

        example_configs = {
            "創造性寫作": """PARAMETER temperature 1.2
PARAMETER top_p 0.95
PARAMETER top_k 50""",
            "技術文檔": """PARAMETER temperature 0.3
PARAMETER top_p 0.8
PARAMETER top_k 20""",
            "代碼生成": """PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.2"""
        }

        for use_case, config in example_configs.items():
            console.print(f"\n[yellow]{use_case}:[/yellow]")
            console.print(Panel(config, border_style="blue"))

    except Exception as e:
        console.print(f"[red]參數配置說明失敗: {e}[/red]")


def create_role_based_models():
    """創建不同角色的模型"""
    try:
        console.print("\n[bold cyan]角色模型示例[/bold cyan]")

        roles = {
            "translator": {
                "name": "中英翻譯助手",
                "system": """你是專業的中英雙語翻譯。

規則：
1. 中文翻譯成英文，英文翻譯成中文
2. 保持原文的語氣和風格
3. 只返回翻譯結果，不要解釋
4. 確保翻譯自然流暢""",
                "params": "temperature 0.3"
            },
            "code-reviewer": {
                "name": "代碼審查員",
                "system": """你是經驗豐富的代碼審查員。

審查標準：
1. 代碼質量和可讀性
2. 性能和效率
3. 安全性問題
4. 最佳實踐

格式：
- 優點：列出做得好的地方
- 問題：指出需要改進的地方
- 建議：提供具體改進方案""",
                "params": "temperature 0.5"
            },
            "storyteller": {
                "name": "故事創作者",
                "system": """你是富有想像力的故事創作者。

風格：
1. 生動有趣的描述
2. 引人入勝的情節
3. 鮮明的人物性格
4. 適當的懸念和節奏

要求：
- 使用豐富的修辭手法
- 創造沉浸式體驗
- 保持故事連貫性""",
                "params": "temperature 1.0"
            }
        }

        for role_id, role_info in roles.items():
            console.print(f"\n[bold yellow]{role_info['name']} ({role_id}):[/bold yellow]")

            modelfile = f"""FROM llama3.2

PARAMETER {role_info['params']}

SYSTEM \"\"\"
{role_info['system']}
\"\"\"
"""

            console.print(Panel(
                Syntax(modelfile, "dockerfile", theme="monokai"),
                border_style="yellow"
            ))

            console.print(f"[dim]創建命令: ollama create {role_id} -f Modelfile[/dim]")

    except Exception as e:
        console.print(f"[red]創建角色模型失敗: {e}[/red]")


def create_and_test_model():
    """實際創建並測試自定義模型"""
    try:
        console.print("\n[bold cyan]創建並測試自定義模型[/bold cyan]")

        # 創建簡單的自定義模型
        modelfile_content = """FROM llama3.2

PARAMETER temperature 0.7
PARAMETER top_p 0.9

SYSTEM \"\"\"
你是一個簡潔的助手。
每次回答控制在 2-3 句話以內。
用最簡單的語言解釋概念。
\"\"\"
"""

        console.print("\n[bold]Modelfile:[/bold]")
        console.print(Panel(
            Syntax(modelfile_content, "dockerfile", theme="monokai"),
            border_style="yellow"
        ))

        # 保存到臨時文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='', delete=False) as f:
            f.write(modelfile_content)
            modelfile_path = f.name

        model_name = "demo-concise-assistant"

        console.print(f"\n[dim]臨時 Modelfile: {modelfile_path}[/dim]")
        console.print(f"[dim]模型名稱: {model_name}[/dim]")

        # 創建模型（實際執行）
        console.print("\n[yellow]注意: 以下命令會實際創建模型[/yellow]")
        console.print(f"[dim]命令: ollama create {model_name} -f {modelfile_path}[/dim]")

        console.print("\n[bold]創建步驟:[/bold]")
        console.print("  1. 保存 Modelfile 到文件")
        console.print(f"  2. 運行: ollama create {model_name} -f Modelfile")
        console.print(f"  3. 使用: ollama run {model_name}")

        # 清理臨時文件
        os.unlink(modelfile_path)

        console.print("\n[bold]測試自定義模型:[/bold]")
        test_code = f"""import ollama

# 測試自定義模型
response = ollama.chat(
    model='{model_name}',
    messages=[{{
        'role': 'user',
        'content': '什麼是機器學習？'
    }}]
)

print(response['message']['content'])
"""
        console.print(Panel(
            Syntax(test_code, "python", theme="monokai"),
            border_style="blue"
        ))

    except Exception as e:
        console.print(f"[red]創建測試模型失敗: {e}[/red]")


def modelfile_best_practices():
    """Modelfile 最佳實踐"""
    try:
        console.print("\n[bold cyan]Modelfile 最佳實踐[/bold cyan]")

        best_practices = [
            {
                'title': '1. 清晰的系統提示詞',
                'desc': '明確定義角色、行為和輸出格式',
                'example': """SYSTEM \"\"\"
你是專業的技術寫作助手。

職責：
- 將技術概念轉換為易懂的文檔
- 保持專業但友好的語氣
- 提供結構化的輸出

格式：
1. 簡介
2. 詳細說明
3. 示例
4. 注意事項
\"\"\""""
            },
            {
                'title': '2. 合適的參數設置',
                'desc': '根據用途調整參數',
                'example': """# 代碼生成 - 低溫度，高確定性
PARAMETER temperature 0.2
PARAMETER top_p 0.8

# 創意寫作 - 高溫度，高創造性
PARAMETER temperature 1.0
PARAMETER top_p 0.95"""
            },
            {
                'title': '3. 版本控制',
                'desc': '在 Modelfile 中記錄版本和變更',
                'example': """# Version: 1.0.0
# Created: 2025-01-01
# Purpose: Customer service chatbot
# Changes:
#   - Initial version
#   - Added polite greeting instructions

FROM llama3.2"""
            },
            {
                'title': '4. 模板定制（高級）',
                'desc': '自定義提示詞模板格式',
                'example': """TEMPLATE \"\"\"
{{ if .System }}System: {{ .System }}

{{ end }}{{ if .Prompt }}User: {{ .Prompt }}

{{ end }}Assistant:
\"\"\""""
            }
        ]

        for practice in best_practices:
            console.print(f"\n[bold yellow]{practice['title']}[/bold yellow]")
            console.print(f"[dim]{practice['desc']}[/dim]")
            console.print(Panel(
                practice['example'],
                border_style="blue"
            ))

        console.print("\n[bold]額外建議:[/bold]")
        console.print("  • 使用描述性的模型名稱")
        console.print("  • 文檔化模型的用途和限制")
        console.print("  • 定期測試和調整參數")
        console.print("  • 保存 Modelfile 到版本控制")

    except Exception as e:
        console.print(f"[red]最佳實踐說明失敗: {e}[/red]")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Ollama 自定義模型示例[/bold cyan]",
        border_style="cyan"
    ))

    console.print("\n[dim]Modelfile 允許你創建專用的自定義模型[/dim]")

    # 1. 基礎 Modelfile
    console.print("\n[bold]示例 1: 基礎 Modelfile[/bold]")
    create_basic_modelfile()

    # 2. 參數配置
    console.print("\n[bold]示例 2: 參數配置說明[/bold]")
    parameter_configurations()

    # 3. 專用模型
    console.print("\n[bold]示例 3: 創建專用模型[/bold]")
    create_specialized_model()

    # 4. 角色模型
    console.print("\n[bold]示例 4: 角色模型[/bold]")
    create_role_based_models()

    # 5. 實際創建測試
    console.print("\n[bold]示例 5: 創建並測試模型[/bold]")
    create_and_test_model()

    # 6. 最佳實踐
    console.print("\n[bold]示例 6: Modelfile 最佳實踐[/bold]")
    modelfile_best_practices()

    # 完成
    console.print("\n" + "="*60)
    console.print("[bold green]✓ 自定義模型示例完成！[/bold green]")

    console.print("\n[cyan]快速參考:[/cyan]")
    console.print("  創建模型: ollama create <name> -f Modelfile")
    console.print("  查看模型: ollama show <name>")
    console.print("  刪除模型: ollama rm <name>")
    console.print("  運行模型: ollama run <name>")

    console.print("\n[cyan]關鍵要點:[/cyan]")
    console.print("  1. Modelfile 類似 Dockerfile，定義模型配置")
    console.print("  2. 可以自定義系統提示詞和參數")
    console.print("  3. 基於已有模型創建專用版本")
    console.print("  4. 適合創建特定用途的模型")


if __name__ == "__main__":
    main()
