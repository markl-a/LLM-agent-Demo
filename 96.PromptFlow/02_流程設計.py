"""
PromptFlow 流程設計示例

本示例展示：
1. Flow 配置文件結構
2. DAG（有向無環圖）設計
3. 輸入輸出定義
4. 節點連接和依賴
"""

import os
import yaml
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich.syntax import Syntax

console = Console()


def explain_flow_structure():
    """解釋 Flow 結構"""
    console.print("\n[cyan]Flow 配置文件結構[/cyan]\n")

    # 顯示基本結構
    structure = """
Flow 配置文件 (flow.dag.yaml) 包含以下部分：

1. inputs:  定義 Flow 的輸入參數
2. outputs: 定義 Flow 的輸出結果
3. nodes:   定義處理節點及其連接關係

每個節點包含：
- name:   節點名稱（唯一標識）
- type:   節點類型（python/llm/prompt等）
- source: 節點代碼來源
- inputs: 節點輸入（可引用其他節點）
"""

    console.print(Panel(structure, title="Flow 結構說明", border_style="cyan"))
    console.print()


def create_simple_flow():
    """創建簡單的 Flow"""
    console.print("[cyan]示例 1: 簡單的問答 Flow[/cyan]\n")

    flow_config = {
        "$schema": "https://azuremlschemas.azureedge.net/promptflow/latest/Flow.schema.json",
        "inputs": {
            "question": {
                "type": "string",
                "description": "用戶問題"
            }
        },
        "outputs": {
            "answer": {
                "type": "string",
                "reference": "${answer_node.output}"
            }
        },
        "nodes": [
            {
                "name": "answer_node",
                "type": "python",
                "source": {
                    "type": "code",
                    "path": "answer.py"
                },
                "inputs": {
                    "question": "${inputs.question}"
                }
            }
        ]
    }

    # 顯示配置
    yaml_str = yaml.dump(flow_config, allow_unicode=True, sort_keys=False)
    syntax = Syntax(yaml_str, "yaml", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()

    return flow_config


def create_multi_node_flow():
    """創建多節點 Flow"""
    console.print("[cyan]示例 2: 多節點處理 Flow[/cyan]\n")

    flow_config = {
        "$schema": "https://azuremlschemas.azureedge.net/promptflow/latest/Flow.schema.json",
        "inputs": {
            "user_input": {
                "type": "string"
            }
        },
        "outputs": {
            "final_result": {
                "type": "string",
                "reference": "${format_output.output}"
            }
        },
        "nodes": [
            # 節點 1: 預處理
            {
                "name": "preprocess",
                "type": "python",
                "source": {
                    "type": "code",
                    "path": "preprocess.py"
                },
                "inputs": {
                    "text": "${inputs.user_input}"
                }
            },
            # 節點 2: 核心處理
            {
                "name": "process",
                "type": "python",
                "source": {
                    "type": "code",
                    "path": "process.py"
                },
                "inputs": {
                    "processed_text": "${preprocess.output}"
                }
            },
            # 節點 3: 格式化輸出
            {
                "name": "format_output",
                "type": "python",
                "source": {
                    "type": "code",
                    "path": "format.py"
                },
                "inputs": {
                    "data": "${process.output}"
                }
            }
        ]
    }

    yaml_str = yaml.dump(flow_config, allow_unicode=True, sort_keys=False)
    syntax = Syntax(yaml_str, "yaml", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()

    # 顯示節點依賴關係
    console.print("[cyan]節點依賴關係:[/cyan]")
    tree = Tree("🔄 Flow 執行順序")
    tree.add("📥 inputs.user_input")
    node1 = tree.add("🔧 preprocess")
    node2 = node1.add("⚙️  process")
    node3 = node2.add("📝 format_output")
    node3.add("📤 outputs.final_result")
    console.print(tree)
    console.print()

    return flow_config


def create_parallel_flow():
    """創建並行處理 Flow"""
    console.print("[cyan]示例 3: 並行處理 Flow[/cyan]\n")

    flow_config = {
        "$schema": "https://azuremlschemas.azureedge.net/promptflow/latest/Flow.schema.json",
        "inputs": {
            "text": {
                "type": "string"
            }
        },
        "outputs": {
            "combined_result": {
                "type": "object",
                "reference": "${combine.output}"
            }
        },
        "nodes": [
            # 並行節點 1: 情感分析
            {
                "name": "sentiment_analysis",
                "type": "python",
                "source": {
                    "type": "code",
                    "path": "sentiment.py"
                },
                "inputs": {
                    "text": "${inputs.text}"
                }
            },
            # 並行節點 2: 關鍵詞提取
            {
                "name": "keyword_extraction",
                "type": "python",
                "source": {
                    "type": "code",
                    "path": "keywords.py"
                },
                "inputs": {
                    "text": "${inputs.text}"
                }
            },
            # 並行節點 3: 主題分類
            {
                "name": "topic_classification",
                "type": "python",
                "source": {
                    "type": "code",
                    "path": "topics.py"
                },
                "inputs": {
                    "text": "${inputs.text}"
                }
            },
            # 合併節點
            {
                "name": "combine",
                "type": "python",
                "source": {
                    "type": "code",
                    "path": "combine.py"
                },
                "inputs": {
                    "sentiment": "${sentiment_analysis.output}",
                    "keywords": "${keyword_extraction.output}",
                    "topics": "${topic_classification.output}"
                }
            }
        ]
    }

    yaml_str = yaml.dump(flow_config, allow_unicode=True, sort_keys=False)
    syntax = Syntax(yaml_str, "yaml", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()

    # 顯示並行結構
    console.print("[cyan]並行執行結構:[/cyan]")
    tree = Tree("🔄 Flow 執行結構")
    input_node = tree.add("📥 inputs.text")
    parallel = input_node.add("⚡ 並行執行")
    parallel.add("😊 sentiment_analysis")
    parallel.add("🔑 keyword_extraction")
    parallel.add("📂 topic_classification")
    combine_node = tree.add("🔗 combine")
    combine_node.add("📤 outputs.combined_result")
    console.print(tree)
    console.print()

    return flow_config


def create_llm_flow():
    """創建 LLM 節點 Flow"""
    console.print("[cyan]示例 4: 使用 LLM 節點的 Flow[/cyan]\n")

    flow_config = {
        "$schema": "https://azuremlschemas.azureedge.net/promptflow/latest/Flow.schema.json",
        "inputs": {
            "question": {
                "type": "string"
            },
            "context": {
                "type": "string",
                "default": ""
            }
        },
        "outputs": {
            "answer": {
                "type": "string",
                "reference": "${llm_node.output}"
            }
        },
        "nodes": [
            # LLM 節點
            {
                "name": "llm_node",
                "type": "llm",
                "source": {
                    "type": "code",
                    "path": "prompt.jinja2"
                },
                "inputs": {
                    "question": "${inputs.question}",
                    "context": "${inputs.context}"
                },
                "connection": "azure_openai_connection",
                "api": "chat",
                "deployment_name": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 500
            }
        ]
    }

    yaml_str = yaml.dump(flow_config, allow_unicode=True, sort_keys=False)
    syntax = Syntax(yaml_str, "yaml", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()

    # 顯示對應的 Jinja2 模板
    console.print("[cyan]對應的 Prompt 模板 (prompt.jinja2):[/cyan]\n")

    prompt_template = """system:
你是一個有幫助的 AI 助手。

{% if context %}
參考上下文:
{{ context }}
{% endif %}

user:
{{ question }}
"""

    syntax = Syntax(prompt_template, "jinja2", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()

    return flow_config


def show_flow_best_practices():
    """顯示 Flow 設計最佳實踐"""
    console.print("[cyan]Flow 設計最佳實踐[/cyan]\n")

    practices = [
        ("1. 明確的輸入輸出", "定義清晰的類型和描述"),
        ("2. 有意義的節點名稱", "使用描述性的名稱，便於理解"),
        ("3. 合理的節點粒度", "每個節點職責單一，便於測試"),
        ("4. 避免循環依賴", "保持 DAG 結構，避免死循環"),
        ("5. 並行優化", "獨立節點可以並行執行"),
        ("6. 錯誤處理", "在關鍵節點添加錯誤處理"),
        ("7. 版本控制", "使用 Git 管理 Flow 配置"),
        ("8. 文檔註釋", "添加必要的說明和註釋"),
    ]

    from rich.table import Table
    table = Table(title="最佳實踐指南")
    table.add_column("實踐", style="cyan")
    table.add_column("說明", style="yellow")

    for practice, description in practices:
        table.add_row(practice, description)

    console.print(table)
    console.print()


def show_variable_reference():
    """顯示變量引用語法"""
    console.print("[cyan]變量引用語法[/cyan]\n")

    references = [
        ("${inputs.param_name}", "引用 Flow 輸入參數"),
        ("${node_name.output}", "引用節點的輸出"),
        ("${node_name.output.field}", "引用輸出的特定字段"),
        ("${variants.variant_id.output}", "引用變體輸出"),
    ]

    from rich.table import Table
    table = Table(title="變量引用語法")
    table.add_column("語法", style="cyan", no_wrap=True)
    table.add_column("說明", style="yellow")

    for syntax_str, description in references:
        table.add_row(syntax_str, description)

    console.print(table)
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]PromptFlow 流程設計示例[/bold cyan]\n"
        "[dim]學習如何設計和組織 Flow[/dim]",
        border_style="cyan"
    ))

    # 1. 解釋結構
    explain_flow_structure()

    # 2. 簡單 Flow
    create_simple_flow()

    # 3. 多節點 Flow
    create_multi_node_flow()

    # 4. 並行 Flow
    create_parallel_flow()

    # 5. LLM Flow
    create_llm_flow()

    # 6. 變量引用
    show_variable_reference()

    # 7. 最佳實踐
    show_flow_best_practices()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 流程設計示例完成！[/bold green]\n")
    console.print("[cyan]下一步:[/cyan]")
    console.print("  1. 查看 03_節點類型.py - 學習各種節點類型")
    console.print("  2. 查看 04_變量傳遞.py - 深入理解數據流")
    console.print("  3. 查看 05_條件分支.py - 學習條件邏輯")


if __name__ == "__main__":
    main()
