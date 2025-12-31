"""
Unsloth 數據格式示例

本示例展示：
1. Alpaca 格式
2. ShareGPT 格式
3. Chat 格式
4. 自定義格式化函數
"""

import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()


def show_alpaca_format():
    """Alpaca 格式示例"""
    console.print("\n[cyan]1. Alpaca 格式（最常用）:[/cyan]\n")

    alpaca_template = '''Below is an instruction. Write a response.

### Instruction:
{}

### Input:
{}

### Response:
{}'''

    console.print("[yellow]數據格式:[/yellow]")
    console.print("""
{
  "instruction": "解釋什麼是機器學習",
  "input": "",
  "output": "機器學習是..."
}
    """)

    console.print("[yellow]格式化函數:[/yellow]")
    console.print("""
def formatting_prompts_func(examples):
    instructions = examples["instruction"]
    inputs = examples.get("input", [""] * len(instructions))
    outputs = examples["output"]
    texts = []

    for instruction, input_text, output in zip(instructions, inputs, outputs):
        text = alpaca_template.format(instruction, input_text, output)
        texts.append(text)

    return {"text": texts}

dataset = dataset.map(formatting_prompts_func, batched=True)
    """)


def show_sharegpt_format():
    """ShareGPT 格式示例"""
    console.print("\n[cyan]2. ShareGPT 格式（對話）:[/cyan]\n")

    console.print("[yellow]數據格式:[/yellow]")
    console.print("""
{
  "conversations": [
    {"from": "human", "value": "你好"},
    {"from": "gpt", "value": "你好！有什麼可以幫助你的？"},
    {"from": "human", "value": "解釋深度學習"},
    {"from": "gpt", "value": "深度學習是..."}
  ]
}
    """)

    console.print("[yellow]格式化函數:[/yellow]")
    console.print("""
def format_sharegpt(examples):
    texts = []
    for convs in examples["conversations"]:
        text = ""
        for turn in convs:
            if turn["from"] == "human":
                text += f"User: {turn['value']}\\n"
            else:
                text += f"Assistant: {turn['value']}\\n"
        texts.append(text)
    return {"text": texts}
    """)


def show_chat_format():
    """Chat 格式示例"""
    console.print("\n[cyan]3. Chat 格式（標準對話）:[/cyan]\n")

    console.print("[yellow]數據格式:[/yellow]")
    console.print("""
{
  "messages": [
    {"role": "system", "content": "你是一個有幫助的助手"},
    {"role": "user", "content": "什麼是 AI？"},
    {"role": "assistant", "content": "AI 是..."}
  ]
}
    """)

    console.print("[yellow]使用 apply_chat_template:[/yellow]")
    console.print("""
# 使用 tokenizer 的 chat template
def format_chat(examples):
    texts = []
    for messages in examples["messages"]:
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False
        )
        texts.append(text)
    return {"text": texts}
    """)


def show_complete_example():
    """完整示例"""
    console.print("\n[cyan]完整訓練示例:[/cyan]\n")

    console.print("""
from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments

# 1. 載入模型
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-2-7b-bnb-4bit",
    max_seq_length=2048,
)

# 2. 配置 LoRA
model = FastLanguageModel.get_peft_model(
    model, r=16, lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    use_gradient_checkpointing="unsloth",
)

# 3. 載入數據（Alpaca 格式）
dataset = load_dataset("yahma/alpaca-cleaned", split="train")

# 4. 格式化
alpaca_prompt = '''Below is an instruction.

### Instruction:
{}

### Response:
{}'''

def formatting_func(examples):
    texts = []
    for inst, out in zip(examples["instruction"], examples["output"]):
        texts.append(alpaca_prompt.format(inst, out))
    return {"text": texts}

dataset = dataset.map(formatting_func, batched=True)

# 5. 訓練
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=2048,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        max_steps=100,
        learning_rate=2e-4,
        output_dir="outputs",
        optim="adamw_8bit",
    ),
)

trainer.train()
    """)


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Unsloth 數據格式示例[/bold cyan]",
        border_style="cyan"
    ))

    show_alpaca_format()
    show_sharegpt_format()
    show_chat_format()
    show_complete_example()

    console.print("="*60)
    console.print("[bold green]✓ 數據格式示例完成！[/bold green]")


if __name__ == "__main__":
    main()
