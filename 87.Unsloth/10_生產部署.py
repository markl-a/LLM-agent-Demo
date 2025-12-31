"""
Unsloth 生產部署示例

本示例展示：
1. 部署準備
2. API 服務
3. 性能優化
4. 最佳實踐
"""

from rich.console import Console
from rich.panel import Panel

console = Console()


def show_deployment_prep():
    """部署準備"""
    console.print("\n[cyan]部署前準備:[/cyan]\n")

    console.print("""
# 1. 合併並保存為 16-bit
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained("lora_model")
model.save_pretrained_merged(
    "production_model",
    tokenizer,
    save_method="merged_16bit",
)

# 2. 或導出為 GGUF（用於 llama.cpp/Ollama）
model.save_pretrained_gguf(
    "production_model_gguf",
    tokenizer,
    quantization_method="q4_k_m",
)

# 3. 測試模型質量
# 運行評估腳本，確保質量滿足要求
    """)


def show_vllm_deployment():
    """vLLM 部署"""
    console.print("[cyan]使用 vLLM 部署（推薦）:[/cyan]\n")

    console.print("""
# 安裝 vLLM
pip install vllm

# Python API
from vllm import LLM, SamplingParams

llm = LLM(
    model="production_model",
    tensor_parallel_size=1,
    max_model_len=2048,
)

sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=200,
)

outputs = llm.generate(["解釋機器學習"], sampling_params)
print(outputs[0].outputs[0].text)

# OpenAI 兼容服務器
python -m vllm.entrypoints.openai.api_server \\
    --model production_model \\
    --port 8000
    """)


def show_fastapi_deployment():
    """FastAPI 部署"""
    console.print("[cyan]FastAPI 自定義服務:[/cyan]\n")

    console.print("""
from fastapi import FastAPI
from pydantic import BaseModel
from unsloth import FastLanguageModel
import torch

app = FastAPI()
model, tokenizer = None, None

@app.on_event("startup")
async def load_model():
    global model, tokenizer
    model, tokenizer = FastLanguageModel.from_pretrained(
        "production_model",
        max_seq_length=2048,
        dtype=None,
        load_in_4bit=True,
    )
    FastLanguageModel.for_inference(model)

class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 200

@app.post("/generate")
async def generate(request: GenerateRequest):
    inputs = tokenizer([request.prompt], return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=request.max_tokens)
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"generated_text": text}

# 運行：uvicorn server:app --host 0.0.0.0 --port 8000
    """)


def show_docker_deployment():
    """Docker 部署"""
    console.print("[cyan]Docker 容器化部署:[/cyan]\n")

    console.print("""
# Dockerfile
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install unsloth fastapi uvicorn

COPY production_model /app/model
COPY server.py /app/

WORKDIR /app
EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]

# 構建和運行
docker build -t llm-service .
docker run --gpus all -p 8000:8000 llm-service
    """)


def show_best_practices():
    """最佳實踐"""
    console.print("[cyan]生產環境最佳實踐:[/cyan]\n")

    practices = [
        "1. 模型準備：",
        "   - 充分測試模型質量",
        "   - 保存多個檢查點備用",
        "   - 記錄訓練配置和數據",
        "",
        "2. 性能優化：",
        "   - 使用 vLLM 或 TGI 提升吞吐量",
        "   - 啟用批處理",
        "   - 調整 batch size 和並發數",
        "",
        "3. 監控和日誌：",
        "   - 記錄所有請求和響應",
        "   - 監控延遲和吞吐量",
        "   - 設置告警",
        "",
        "4. 安全性：",
        "   - 輸入驗證和清理",
        "   - 輸出過濾",
        "   - 速率限制",
        "   - API 認證",
        "",
        "5. 可擴展性：",
        "   - 負載均衡",
        "   - 多副本部署",
        "   - 自動擴展",
    ]

    for practice in practices:
        console.print(f"  {practice}")
    console.print()


def show_complete_workflow():
    """完整工作流程"""
    console.print("[cyan]完整部署工作流程:[/cyan]\n")

    steps = [
        "1. 訓練和評估模型",
        "2. 選擇最佳檢查點",
        "3. 合併 LoRA 權重",
        "4. 導出為部署格式（16-bit 或 GGUF）",
        "5. 本地測試推理",
        "6. 選擇部署方案（vLLM/FastAPI/llama.cpp）",
        "7. 容器化（Docker）",
        "8. 部署到生產環境",
        "9. 負載測試",
        "10. 監控和維護",
    ]

    for step in steps:
        console.print(f"  {step}")
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Unsloth 生產部署示例[/bold cyan]",
        border_style="cyan"
    ))

    show_deployment_prep()
    show_vllm_deployment()
    show_fastapi_deployment()
    show_docker_deployment()
    show_best_practices()
    show_complete_workflow()

    console.print("="*60)
    console.print("[bold green]✓ 所有 Unsloth 示例完成！[/bold green]")
    console.print("\n[cyan]Unsloth 總結:[/cyan]")
    console.print("  - 2-5x 訓練加速")
    console.print("  - 80% 內存節省")
    console.print("  - 完美的 HuggingFace 兼容性")
    console.print("  - 簡單易用的 API")
    console.print("\n  非常適合快速原型開發和資源受限環境！")


if __name__ == "__main__":
    main()
