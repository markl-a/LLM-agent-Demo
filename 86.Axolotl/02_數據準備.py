"""
Axolotl 數據準備示例

本示例展示：
1. 支持的數據格式
2. 數據格式轉換
3. 數據驗證
4. 提示詞模板
"""

import json
from pathlib import Path
from typing import List, Dict
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def show_supported_formats():
    """展示支持的數據格式"""
    console.print("\n[cyan]Axolotl 支持的數據格式:[/cyan]\n")

    formats = {
        "Alpaca": {
            "instruction": "用戶指令",
            "input": "可選的輸入",
            "output": "期望的輸出"
        },
        "ShareGPT": {
            "conversations": [
                {"from": "human", "value": "用戶消息"},
                {"from": "gpt", "value": "助手回覆"}
            ]
        },
        "Completion": {
            "text": "完整的訓練文本"
        },
        "Chat": {
            "messages": [
                {"role": "user", "content": "用戶消息"},
                {"role": "assistant", "content": "助手回覆"}
            ]
        }
    }

    for name, example in formats.items():
        console.print(f"[yellow]{name} 格式:[/yellow]")
        console.print(json.dumps(example, ensure_ascii=False, indent=2))
        console.print()


def create_alpaca_dataset():
    """創建 Alpaca 格式數據集"""
    console.print("[cyan]創建 Alpaca 格式數據集...[/cyan]")

    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    alpaca_data = [
        {
            "instruction": "總結以下文章的主要內容",
            "input": "人工智能正在改變我們的生活方式。從智能手機到自動駕駛汽車，AI 技術無處不在。",
            "output": "文章主要討論人工智能如何通過各種應用（如智能手機和自動駕駛汽車）改變我們的日常生活。"
        },
        {
            "instruction": "將以下數字相加",
            "input": "123 + 456 + 789",
            "output": "123 + 456 + 789 = 1368"
        },
        {
            "instruction": "解釋什麼是遞歸",
            "input": "",
            "output": "遞歸是一種編程技術，函數在執行過程中調用自身。它通常包含基礎情況（停止條件）和遞歸情況（繼續調用自身）。"
        },
        {
            "instruction": "將以下句子改寫得更正式",
            "input": "這個東西真的超棒的！",
            "output": "此項產品的品質確實令人滿意。"
        },
        {
            "instruction": "列出健康生活的五個建議",
            "input": "",
            "output": "1. 保持規律運動\n2. 均衡飲食\n3. 充足睡眠\n4. 減少壓力\n5. 定期體檢"
        },
    ]

    output_path = data_dir / "alpaca_format.jsonl"
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in alpaca_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    console.print(f"[green]✓ Alpaca 數據集已創建: {output_path}[/green]")
    console.print(f"[dim]數據條數: {len(alpaca_data)}[/dim]\n")

    return output_path


def create_sharegpt_dataset():
    """創建 ShareGPT 格式數據集"""
    console.print("[cyan]創建 ShareGPT 格式數據集...[/cyan]")

    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    sharegpt_data = [
        {
            "conversations": [
                {"from": "human", "value": "你好！"},
                {"from": "gpt", "value": "你好！很高興為你服務。有什麼我可以幫助你的嗎？"},
                {"from": "human", "value": "我想學習 Python 編程"},
                {"from": "gpt", "value": "太棒了！Python 是一門很適合初學者的語言。建議你從基礎語法開始，然後逐步學習數據結構、函數和面向對象編程。"}
            ]
        },
        {
            "conversations": [
                {"from": "human", "value": "什麼是機器學習？"},
                {"from": "gpt", "value": "機器學習是人工智能的一個分支，它讓計算機能夠從數據中學習並改進性能，而不需要明確編程。"},
                {"from": "human", "value": "有哪些常見的機器學習算法？"},
                {"from": "gpt", "value": "常見的機器學習算法包括：\n1. 線性回歸\n2. 決策樹\n3. 隨機森林\n4. 支持向量機(SVM)\n5. 神經網絡\n6. K-means 聚類"}
            ]
        },
    ]

    output_path = data_dir / "sharegpt_format.jsonl"
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in sharegpt_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    console.print(f"[green]✓ ShareGPT 數據集已創建: {output_path}[/green]")
    console.print(f"[dim]數據條數: {len(sharegpt_data)}[/dim]\n")

    return output_path


def create_chat_dataset():
    """創建 Chat 格式數據集"""
    console.print("[cyan]創建 Chat 格式數據集...[/cyan]")

    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    chat_data = [
        {
            "messages": [
                {"role": "system", "content": "你是一個有幫助的助手。"},
                {"role": "user", "content": "什麼是深度學習？"},
                {"role": "assistant", "content": "深度學習是機器學習的一個子領域，使用多層神經網絡來學習數據的複雜表示。"}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": "你是一個編程助手。"},
                {"role": "user", "content": "如何在 Python 中讀取文件？"},
                {"role": "assistant", "content": "在 Python 中讀取文件可以使用 open() 函數：\n```python\nwith open('file.txt', 'r') as f:\n    content = f.read()\n```"}
            ]
        },
    ]

    output_path = data_dir / "chat_format.jsonl"
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in chat_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    console.print(f"[green]✓ Chat 數據集已創建: {output_path}[/green]")
    console.print(f"[dim]數據條數: {len(chat_data)}[/dim]\n")

    return output_path


def validate_dataset(file_path: Path, format_type: str):
    """驗證數據集格式"""
    console.print(f"[cyan]驗證數據集: {file_path}[/cyan]")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        valid_count = 0
        invalid_count = 0
        errors = []

        for i, line in enumerate(lines, 1):
            try:
                data = json.loads(line)

                # 根據格式類型驗證
                if format_type == "alpaca":
                    if all(key in data for key in ["instruction", "output"]):
                        valid_count += 1
                    else:
                        invalid_count += 1
                        errors.append(f"行 {i}: 缺少必需字段")

                elif format_type == "sharegpt":
                    if "conversations" in data:
                        valid_count += 1
                    else:
                        invalid_count += 1
                        errors.append(f"行 {i}: 缺少 conversations 字段")

                elif format_type == "chat":
                    if "messages" in data:
                        valid_count += 1
                    else:
                        invalid_count += 1
                        errors.append(f"行 {i}: 缺少 messages 字段")

            except json.JSONDecodeError:
                invalid_count += 1
                errors.append(f"行 {i}: JSON 格式錯誤")

        # 顯示驗證結果
        table = Table(title="數據驗證結果")
        table.add_column("指標", style="cyan")
        table.add_column("值", style="green")

        table.add_row("總行數", str(len(lines)))
        table.add_row("有效行數", str(valid_count))
        table.add_row("無效行數", str(invalid_count))
        table.add_row("驗證狀態", "✓ 通過" if invalid_count == 0 else "✗ 失敗")

        console.print(table)

        if errors:
            console.print("\n[yellow]錯誤列表:[/yellow]")
            for error in errors[:5]:  # 只顯示前 5 個錯誤
                console.print(f"  - {error}")

        console.print()

        return invalid_count == 0

    except Exception as e:
        console.print(f"[red]✗ 驗證失敗: {e}[/red]\n")
        return False


def show_prompt_templates():
    """展示常用的提示詞模板"""
    console.print("[cyan]常用提示詞模板:[/cyan]\n")

    templates = {
        "Alpaca": "Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction:\n{instruction}\n\n### Response:\n{output}",

        "Alpaca with Input": "Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.\n\n### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:\n{output}",

        "ChatML": "<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n{instruction}<|im_end|>\n<|im_start|>assistant\n{output}<|im_end|>",

        "Vicuna": "A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions.\n\nUSER: {instruction}\nASSISTANT: {output}",
    }

    for name, template in templates.items():
        console.print(f"[yellow]{name}:[/yellow]")
        console.print(f"[dim]{template}[/dim]")
        console.print()


def convert_format(input_path: Path, output_format: str):
    """轉換數據格式"""
    console.print(f"[cyan]轉換數據格式到 {output_format}...[/cyan]")

    # 這是一個簡化的示例
    # 實際應用中需要根據源格式和目標格式進行轉換
    console.print("[yellow]格式轉換需要根據具體格式編寫轉換邏輯[/yellow]")
    console.print("[dim]示例：Alpaca -> ShareGPT, Chat -> Alpaca 等[/dim]\n")


def show_data_best_practices():
    """展示數據準備最佳實踐"""
    console.print("[cyan]數據準備最佳實踐:[/cyan]\n")

    practices = [
        "1. 數據質量 > 數量：高質量的少量數據勝過低質量的大量數據",
        "2. 數據清洗：移除重複、格式化統一、修正錯誤",
        "3. 數據平衡：確保不同類別或任務類型的平衡",
        "4. 驗證集：預留 10-20% 作為驗證集",
        "5. 提示詞一致性：保持提示詞格式的一致性",
        "6. 長度控制：根據模型的 context length 控制序列長度",
        "7. 特殊字符：確保正確處理特殊字符和編碼",
        "8. 版本控制：對數據集進行版本管理",
    ]

    for practice in practices:
        console.print(f"  {practice}")
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Axolotl 數據準備示例[/bold cyan]",
        border_style="cyan"
    ))

    # 1. 展示支持的格式
    show_supported_formats()

    # 2. 創建不同格式的數據集
    alpaca_path = create_alpaca_dataset()
    sharegpt_path = create_sharegpt_dataset()
    chat_path = create_chat_dataset()

    # 3. 驗證數據集
    validate_dataset(alpaca_path, "alpaca")
    validate_dataset(sharegpt_path, "sharegpt")
    validate_dataset(chat_path, "chat")

    # 4. 展示提示詞模板
    show_prompt_templates()

    # 5. 展示最佳實踐
    show_data_best_practices()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 數據準備示例完成！[/bold green]")
    console.print("\n[cyan]配置文件中的數據設置:[/cyan]")
    console.print("""
datasets:
  - path: data/alpaca_format.jsonl
    type: alpaca
  - path: data/sharegpt_format.jsonl
    type: sharegpt
  - path: data/chat_format.jsonl
    type: chat
    """)


if __name__ == "__main__":
    main()
