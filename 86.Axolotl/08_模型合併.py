"""
Axolotl 模型合併示例

本示例展示：
1. LoRA 權重合併到基礎模型
2. 合併後的模型保存
3. 量化和優化
4. 部署準備
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def explain_model_merging():
    """解釋模型合併"""
    console.print("\n[cyan]什麼是模型合併？[/cyan]\n")
    console.print("將 LoRA 適配器權重合併回基礎模型：\n")
    console.print("  [yellow]為什麼需要合併？[/yellow]")
    console.print("    - 簡化部署（只需一個模型文件）")
    console.print("    - 提升推理速度（無需額外計算）")
    console.print("    - 便於量化和優化")
    console.print("    - 兼容更多推理框架\n")
    console.print("  [yellow]注意事項：[/yellow]")
    console.print("    - 合併後無法再調整 LoRA 權重")
    console.print("    - 模型大小會變為完整大小")
    console.print("    - QLoRA 需要先反量化\n")


def show_merging_code():
    """顯示合併代碼"""
    console.print("[cyan]模型合併代碼:[/cyan]\n")

    console.print("[yellow]1. 基本合併（LoRA）:[/yellow]")
    console.print("""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# 載入基礎模型
base_model_name = "meta-llama/Llama-2-7b-hf"
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    torch_dtype=torch.float16,
    device_map="auto",
)

# 載入 LoRA 適配器
lora_model = PeftModel.from_pretrained(
    base_model,
    "./lora_output/checkpoint-100"
)

# 合併權重
merged_model = lora_model.merge_and_unload()

# 保存合併後的模型
output_dir = "./merged_model"
merged_model.save_pretrained(output_dir)

# 保存 tokenizer
tokenizer = AutoTokenizer.from_pretrained(base_model_name)
tokenizer.save_pretrained(output_dir)

print(f"模型已合併並保存到: {output_dir}")
    """)

    console.print("\n[yellow]2. QLoRA 合併（需要先反量化）:[/yellow]")
    console.print("""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

# 載入量化的基礎模型
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

base_model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=bnb_config,
    device_map="auto",
)

# 載入 QLoRA 適配器
model = PeftModel.from_pretrained(base_model, "./qlora_output/checkpoint-200")

# 合併（會自動反量化）
merged_model = model.merge_and_unload()

# 轉換為 float16 以減小大小
merged_model = merged_model.to(torch.float16)

# 保存
merged_model.save_pretrained("./merged_qlora_model")
    """)

    console.print("\n[yellow]3. 分片保存（大模型）:[/yellow]")
    console.print("""
# 對於大模型，使用分片保存
merged_model.save_pretrained(
    "./merged_model",
    max_shard_size="5GB",  # 每個分片最大 5GB
    safe_serialization=True,  # 使用 safetensors 格式
)
    """)


def show_quantization_after_merge():
    """顯示合併後量化"""
    console.print("[cyan]合併後量化優化:[/cyan]\n")

    console.print("[yellow]1. GPTQ 量化（4-bit）:[/yellow]")
    console.print("""
from transformers import AutoModelForCausalLM, GPTQConfig

# GPTQ 量化配置
gptq_config = GPTQConfig(
    bits=4,
    dataset="c4",
    tokenizer=tokenizer,
)

# 載入並量化
quantized_model = AutoModelForCausalLM.from_pretrained(
    "./merged_model",
    device_map="auto",
    quantization_config=gptq_config,
)

# 保存量化模型
quantized_model.save_pretrained("./merged_model_gptq")
    """)

    console.print("\n[yellow]2. AWQ 量化:[/yellow]")
    console.print("""
# 需要 autoawq 庫
from awq import AutoAWQForCausalLM

# 量化配置
quant_config = {
    "zero_point": True,
    "q_group_size": 128,
    "w_bit": 4,
}

# 載入模型
model = AutoAWQForCausalLM.from_pretrained("./merged_model")

# 執行量化
model.quantize(tokenizer, quant_config=quant_config)

# 保存
model.save_quantized("./merged_model_awq")
    """)

    console.print("\n[yellow]3. GGUF 格式（llama.cpp）:[/yellow]")
    console.print("""
# 使用 llama.cpp 的轉換腳本
# 先轉換為 GGUF 格式
python llama.cpp/convert.py ./merged_model \\
    --outtype f16 \\
    --outfile ./merged_model.gguf

# 再進行 k-quant 量化
./llama.cpp/quantize ./merged_model.gguf \\
    ./merged_model_q4_k_m.gguf q4_k_m
    """)


def compare_formats():
    """比較不同格式"""
    console.print("[cyan]模型格式對比:[/cyan]\n")

    formats = [
        ("原始 (FP16)", "14 GB", "快", "最高", "PyTorch, Transformers"),
        ("GPTQ (4-bit)", "3.5 GB", "快", "優秀", "Transformers, vLLM"),
        ("AWQ (4-bit)", "3.5 GB", "最快", "優秀", "vLLM, TGI"),
        ("GGUF Q4_K_M", "4 GB", "中等", "良好", "llama.cpp, Ollama"),
        ("GGUF Q5_K_M", "5 GB", "中等", "優秀", "llama.cpp, Ollama"),
    ]

    table = Table(title="模型格式對比（7B 模型）")
    table.add_column("格式", style="cyan")
    table.add_column("大小", style="yellow")
    table.add_column("速度", style="green")
    table.add_column("質量", style="magenta")
    table.add_column("兼容性", style="dim")

    for fmt in formats:
        table.add_row(*fmt)

    console.print(table)
    console.print()


def show_push_to_hub():
    """顯示上傳到 HuggingFace Hub"""
    console.print("[cyan]上傳到 HuggingFace Hub:[/cyan]\n")

    console.print("[yellow]1. 登錄 HuggingFace:[/yellow]")
    console.print("""
from huggingface_hub import login
login()  # 輸入 token
    """)

    console.print("\n[yellow]2. 上傳模型:[/yellow]")
    console.print("""
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("./merged_model")
tokenizer = AutoTokenizer.from_pretrained("./merged_model")

# 上傳到 Hub
repo_name = "your-username/llama2-7b-finetuned"
model.push_to_hub(repo_name)
tokenizer.push_to_hub(repo_name)
    """)

    console.print("\n[yellow]3. 添加模型卡片:[/yellow]")
    console.print("""
# 創建 README.md
readme_content = '''
---
language: zh
license: llama2
tags:
- llama2
- fine-tuned
datasets:
- your-dataset
---

# LLaMA-2-7B Fine-tuned Model

這是基於 LLaMA-2-7B 使用 LoRA 微調的模型。

## 訓練細節
- 基礎模型: meta-llama/Llama-2-7b-hf
- 微調方法: LoRA (r=16, alpha=32)
- 訓練數據: 10,000 樣本
- 訓練時長: 3 epochs

## 使用方法
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("your-username/llama2-7b-finetuned")
tokenizer = AutoTokenizer.from_pretrained("your-username/llama2-7b-finetuned")
```
'''

with open("./merged_model/README.md", "w") as f:
    f.write(readme_content)
    """)


def show_verification():
    """顯示驗證合併結果"""
    console.print("[cyan]驗證合併結果:[/cyan]\n")

    console.print("[yellow]1. 載入測試:[/yellow]")
    console.print("""
# 載入合併後的模型
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "./merged_model",
    device_map="auto",
)
tokenizer = AutoTokenizer.from_pretrained("./merged_model")

print("✓ 模型載入成功")
    """)

    console.print("\n[yellow]2. 生成測試:[/yellow]")
    console.print("""
# 測試生成
prompt = "解釋什麼是機器學習"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_length=200)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)

print(f"Prompt: {prompt}")
print(f"Response: {response}")
    """)

    console.print("\n[yellow]3. 對比測試:[/yellow]")
    console.print("""
# 對比 LoRA 模型和合併模型的輸出
# 應該完全一致

from peft import PeftModel

# LoRA 模型
base = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
lora_model = PeftModel.from_pretrained(base, "./lora_output/checkpoint-100")

# 合併模型
merged = AutoModelForCausalLM.from_pretrained("./merged_model")

# 測試
prompt = "測試提示詞"
inputs = tokenizer(prompt, return_tensors="pt")

lora_output = lora_model.generate(**inputs, max_length=100)
merged_output = merged.generate(**inputs, max_length=100)

# 應該相同
assert torch.equal(lora_output, merged_output)
print("✓ 輸出一致性驗證通過")
    """)


def show_workflow():
    """顯示完整工作流程"""
    console.print("[cyan]完整工作流程:[/cyan]\n")

    steps = [
        "1. 訓練 LoRA/QLoRA 模型",
        "2. 選擇最佳檢查點",
        "3. 合併權重到基礎模型",
        "4. 驗證合併結果",
        "5. （可選）量化優化",
        "6. 保存為目標格式",
        "7. 測試推理性能",
        "8. 上傳到 HuggingFace Hub 或私有倉庫",
        "9. 部署到生產環境",
    ]

    for step in steps:
        console.print(f"  {step}")
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Axolotl 模型合併示例[/bold cyan]",
        border_style="cyan"
    ))

    # 1. 解釋模型合併
    explain_model_merging()

    # 2. 合併代碼
    show_merging_code()

    # 3. 量化優化
    show_quantization_after_merge()

    # 4. 格式對比
    compare_formats()

    # 5. 上傳到 Hub
    show_push_to_hub()

    # 6. 驗證
    show_verification()

    # 7. 工作流程
    show_workflow()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 模型合併示例完成！[/bold green]")
    console.print("\n[cyan]下一步:[/cyan]")
    console.print("  1. 查看 09_推理部署.py 學習部署方法")
    console.print("  2. 查看 10_最佳實踐.py 學習完整工作流程")


if __name__ == "__main__":
    main()
