"""
Unsloth 推理測試示例

本示例展示：
1. 載入訓練好的模型
2. 文本生成
3. 推理優化
4. 批量推理
"""

from rich.console import Console
from rich.panel import Panel

console = Console()


def show_basic_inference():
    """基本推理"""
    console.print("\n[cyan]基本推理示例:[/cyan]\n")

    console.print("""
from unsloth import FastLanguageModel

# 載入訓練好的模型
model, tokenizer = FastLanguageModel.from_pretrained(
    "lora_model",                               # 你的模型路徑
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True,
)

# 設為推理模式（啟用 Unsloth 優化）
FastLanguageModel.for_inference(model)

# 準備輸入
prompt = "解釋什麼是機器學習"
inputs = tokenizer([prompt], return_tensors="pt").to("cuda")

# 生成
outputs = model.generate(
    **inputs,
    max_new_tokens=200,
    temperature=0.7,
    top_p=0.9,
    do_sample=True,
)

# 解碼輸出
text = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
print(text)
    """)


def show_inference_optimization():
    """推理優化"""
    console.print("[cyan]推理優化:[/cyan]\n")

    console.print("""
# 1. 啟用 Unsloth 推理優化
FastLanguageModel.for_inference(model)          # 必須調用！

# 2. 使用最佳生成參數
outputs = model.generate(
    **inputs,
    max_new_tokens=200,
    use_cache=True,                             # 啟用 KV cache
    do_sample=True,
    temperature=0.7,
    top_p=0.9,
    top_k=50,
)

# 3. 批量推理（更高效）
prompts = [
    "解釋機器學習",
    "什麼是深度學習",
    "介紹神經網絡"
]

inputs = tokenizer(prompts, return_tensors="pt", padding=True).to("cuda")
outputs = model.generate(**inputs, max_new_tokens=200)
texts = tokenizer.batch_decode(outputs, skip_special_tokens=True)
    """)


def show_streaming_inference():
    """流式推理"""
    console.print("[cyan]流式生成（實時輸出）:[/cyan]\n")

    console.print("""
from transformers import TextStreamer

# 創建 streamer
streamer = TextStreamer(tokenizer, skip_prompt=True)

# 流式生成
outputs = model.generate(
    **inputs,
    max_new_tokens=200,
    streamer=streamer,                          # 實時輸出
)
    """)


def show_chatbot_example():
    """聊天機器人示例"""
    console.print("[cyan]聊天機器人示例:[/cyan]\n")

    console.print("""
# 簡單的聊天循環
while True:
    user_input = input("User: ")
    if user_input.lower() == 'exit':
        break

    prompt = f"User: {user_input}\\nAssistant: "
    inputs = tokenizer([prompt], return_tensors="pt").to("cuda")

    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        temperature=0.7,
        top_p=0.9,
        do_sample=True,
    )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    response = response.split("Assistant: ")[-1]
    print(f"Assistant: {response}")
    """)


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Unsloth 推理測試示例[/bold cyan]",
        border_style="cyan"
    ))

    show_basic_inference()
    show_inference_optimization()
    show_streaming_inference()
    show_chatbot_example()

    console.print("="*60)
    console.print("[bold green]✓ 推理測試示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點:[/cyan]")
    console.print("  必須調用 FastLanguageModel.for_inference(model)")
    console.print("  這會啟用 Unsloth 的推理優化，大幅提升速度")


if __name__ == "__main__":
    main()
