"""
Axolotl 推理部署示例

本示例展示：
1. 不同推理框架
2. API 服務部署
3. 推理優化技術
4. 生產環境配置
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def compare_inference_frameworks():
    """比較推理框架"""
    console.print("\n[cyan]推理框架對比:[/cyan]\n")

    frameworks = [
        ("vLLM", "最快", "高", "優秀", "PagedAttention, 批處理"),
        ("TGI", "快", "高", "優秀", "Rust 實現，高性能"),
        ("llama.cpp", "快", "低", "良好", "CPU 友好，跨平台"),
        ("Ollama", "中等", "低", "良好", "易用，本地部署"),
        ("Transformers", "中等", "中", "優秀", "靈活性最高"),
    ]

    table = Table(title="推理框架對比")
    table.add_column("框架", style="cyan")
    table.add_column("速度", style="yellow")
    table.add_column("資源需求", style="green")
    table.add_column("功能性", style="magenta")
    table.add_column("特點", style="dim")

    for framework in frameworks:
        table.add_row(*framework)

    console.print(table)
    console.print()


def show_vllm_deployment():
    """顯示 vLLM 部署"""
    console.print("[cyan]vLLM 部署（推薦用於生產）:[/cyan]\n")

    console.print("[yellow]1. 安裝:[/yellow]")
    console.print("  pip install vllm\n")

    console.print("[yellow]2. Python API:[/yellow]")
    console.print("""
from vllm import LLM, SamplingParams

# 載入模型
llm = LLM(
    model="./merged_model",
    tensor_parallel_size=1,  # GPU 數量
    max_model_len=2048,
    gpu_memory_utilization=0.9,
)

# 推理參數
sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=512,
)

# 批量推理
prompts = [
    "解釋什麼是機器學習",
    "寫一個 Python 函數",
    "總結人工智能的發展",
]

outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    print(f"Prompt: {output.prompt}")
    print(f"Output: {output.outputs[0].text}")
    print("-" * 50)
    """)

    console.print("\n[yellow]3. OpenAI 兼容 API 服務:[/yellow]")
    console.print("""
# 啟動 API 服務器
python -m vllm.entrypoints.openai.api_server \\
    --model ./merged_model \\
    --host 0.0.0.0 \\
    --port 8000 \\
    --tensor-parallel-size 1

# 客戶端調用
import openai

openai.api_key = "EMPTY"
openai.api_base = "http://localhost:8000/v1"

response = openai.Completion.create(
    model="./merged_model",
    prompt="解釋深度學習",
    max_tokens=200,
    temperature=0.7,
)

print(response.choices[0].text)
    """)


def show_tgi_deployment():
    """顯示 TGI 部署"""
    console.print("[cyan]Text Generation Inference (TGI) 部署:[/cyan]\n")

    console.print("[yellow]使用 Docker:[/yellow]")
    console.print("""
docker run --gpus all --shm-size 1g -p 8080:80 \\
    -v $(pwd)/merged_model:/data \\
    ghcr.io/huggingface/text-generation-inference:latest \\
    --model-id /data \\
    --max-input-length 2048 \\
    --max-total-tokens 4096 \\
    --max-batch-prefill-tokens 4096
    """)

    console.print("\n[yellow]客戶端調用:[/yellow]")
    console.print("""
import requests

API_URL = "http://localhost:8080"

def generate(prompt):
    response = requests.post(
        f"{API_URL}/generate",
        json={
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.7,
                "top_p": 0.9,
            }
        }
    )
    return response.json()["generated_text"]

result = generate("解釋什麼是 Transformer")
print(result)
    """)


def show_llamacpp_deployment():
    """顯示 llama.cpp 部署"""
    console.print("[cyan]llama.cpp 部署（CPU 友好）:[/cyan]\n")

    console.print("[yellow]1. 轉換模型為 GGUF:[/yellow]")
    console.print("""
# 克隆 llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp

# 編譯
make

# 轉換模型
python convert.py ../merged_model \\
    --outtype f16 \\
    --outfile ../merged_model.gguf

# 量化
./quantize ../merged_model.gguf \\
    ../merged_model_q4_k_m.gguf q4_k_m
    """)

    console.print("\n[yellow]2. 運行推理:[/yellow]")
    console.print("""
# 命令行推理
./main -m ../merged_model_q4_k_m.gguf \\
    -n 200 \\
    -p "解釋什麼是機器學習"

# 服務器模式
./server -m ../merged_model_q4_k_m.gguf \\
    --host 0.0.0.0 \\
    --port 8080
    """)

    console.print("\n[yellow]3. Python 綁定:[/yellow]")
    console.print("""
from llama_cpp import Llama

llm = Llama(
    model_path="../merged_model_q4_k_m.gguf",
    n_ctx=2048,
    n_threads=8,
)

output = llm(
    "解釋什麼是深度學習",
    max_tokens=200,
    temperature=0.7,
)

print(output["choices"][0]["text"])
    """)


def show_fastapi_deployment():
    """顯示 FastAPI 部署"""
    console.print("[cyan]FastAPI 自定義服務:[/cyan]\n")

    console.print("[yellow]服務器代碼 (server.py):[/yellow]")
    console.print("""
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = FastAPI()

# 載入模型（啟動時）
model = None
tokenizer = None

@app.on_event("startup")
async def load_model():
    global model, tokenizer
    model = AutoModelForCausalLM.from_pretrained(
        "./merged_model",
        device_map="auto",
        torch_dtype=torch.float16,
    )
    tokenizer = AutoTokenizer.from_pretrained("./merged_model")

class GenerateRequest(BaseModel):
    prompt: str
    max_length: int = 200
    temperature: float = 0.7
    top_p: float = 0.9

@app.post("/generate")
async def generate(request: GenerateRequest):
    inputs = tokenizer(request.prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=request.max_length,
            temperature=request.temperature,
            top_p=request.top_p,
            do_sample=True,
        )

    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"generated_text": text}

@app.get("/health")
async def health():
    return {"status": "healthy"}
    """)

    console.print("\n[yellow]啟動服務:[/yellow]")
    console.print("  uvicorn server:app --host 0.0.0.0 --port 8000\n")

    console.print("[yellow]客戶端調用:[/yellow]")
    console.print("""
import requests

response = requests.post(
    "http://localhost:8000/generate",
    json={
        "prompt": "解釋什麼是機器學習",
        "max_length": 200,
        "temperature": 0.7,
    }
)

print(response.json()["generated_text"])
    """)


def show_optimization_techniques():
    """顯示優化技術"""
    console.print("[cyan]推理優化技術:[/cyan]\n")

    techniques = {
        "Flash Attention": "加速注意力計算，減少內存",
        "PagedAttention": "高效管理 KV cache（vLLM）",
        "Continuous Batching": "動態批處理，提高吞吐量",
        "Quantization": "4-bit/8-bit 量化減少內存",
        "Speculative Decoding": "使用小模型加速大模型",
        "KV Cache 優化": "壓縮或共享 KV cache",
        "Tensor Parallelism": "多 GPU 並行推理",
        "Prefix Caching": "緩存常見前綴",
    }

    for technique, desc in techniques.items():
        console.print(f"  [yellow]{technique}:[/yellow] {desc}")
    console.print()


def show_production_config():
    """顯示生產環境配置"""
    console.print("[cyan]生產環境配置建議:[/cyan]\n")

    configs = [
        "1. 資源配置：",
        "   - GPU: 根據模型大小選擇（7B 建議 A100 40GB）",
        "   - CPU: 16+ 核心",
        "   - 內存: 64GB+",
        "   - 存儲: SSD 100GB+",
        "",
        "2. 並發配置：",
        "   - max_batch_size: 根據 VRAM 調整（建議 8-32）",
        "   - max_concurrent_requests: 2-4x GPU 數量",
        "   - request_timeout: 60-120 秒",
        "",
        "3. 監控指標：",
        "   - 請求延遲（P50, P95, P99）",
        "   - 吞吐量（requests/s, tokens/s）",
        "   - GPU 利用率和內存",
        "   - 錯誤率",
        "",
        "4. 安全配置：",
        "   - 輸入長度限制",
        "   - 輸出長度限制",
        "   - 速率限制（rate limiting）",
        "   - 內容過濾",
        "",
        "5. 高可用：",
        "   - 負載均衡",
        "   - 健康檢查",
        "   - 自動重啟",
        "   - 多副本部署",
    ]

    for config in configs:
        console.print(f"  {config}")
    console.print()


def show_docker_deployment():
    """顯示 Docker 部署"""
    console.print("[cyan]Docker 部署示例:[/cyan]\n")

    console.print("[yellow]Dockerfile:[/yellow]")
    console.print("""
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# 安裝 Python
RUN apt-get update && apt-get install -y python3 python3-pip

# 安裝依賴
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# 複製模型和代碼
COPY merged_model /app/model
COPY server.py /app/

WORKDIR /app

# 暴露端口
EXPOSE 8000

# 啟動命令
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
    """)

    console.print("\n[yellow]docker-compose.yml:[/yellow]")
    console.print("""
version: '3.8'

services:
  llm-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      - CUDA_VISIBLE_DEVICES=0
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    """)


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Axolotl 推理部署示例[/bold cyan]",
        border_style="cyan"
    ))

    # 1. 框架對比
    compare_inference_frameworks()

    # 2. vLLM 部署
    show_vllm_deployment()

    # 3. TGI 部署
    show_tgi_deployment()

    # 4. llama.cpp 部署
    show_llamacpp_deployment()

    # 5. FastAPI 部署
    show_fastapi_deployment()

    # 6. 優化技術
    show_optimization_techniques()

    # 7. 生產配置
    show_production_config()

    # 8. Docker 部署
    show_docker_deployment()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 推理部署示例完成！[/bold green]")
    console.print("\n[cyan]選擇建議:[/cyan]")
    console.print("  - 高吞吐量需求: vLLM")
    console.print("  - 生產級穩定性: TGI")
    console.print("  - CPU 部署: llama.cpp")
    console.print("  - 自定義需求: FastAPI + Transformers")


if __name__ == "__main__":
    main()
