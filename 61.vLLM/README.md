# vLLM - 高性能 LLM 推理框架

## 簡介

vLLM 是一個快速且易於使用的大型語言模型（LLM）推理和服務框架。它由加州大學伯克利分校的研究團隊開發，專為生產環境中的高吞吐量和低延遲推理而設計。vLLM 通過創新的 PagedAttention 算法和連續批處理技術，能夠顯著提升 LLM 的推理性能。

vLLM 的目標是讓大型語言模型的部署變得簡單、快速且經濟高效，為開發者提供與 OpenAI API 兼容的接口，同時保持對模型和硬件的完全控制。

## 核心特點

### 1. 極致性能
- **PagedAttention 算法**：受操作系統虛擬內存分頁機制啟發，有效管理 attention 的 KV cache，減少內存浪費
- **高吞吐量**：相比傳統推理方法，吞吐量提升高達 24 倍
- **連續批處理**：動態批處理請求，最大化 GPU 利用率
- **優化的 CUDA 內核**：針對 Transformer 模型的自定義 CUDA 內核

### 2. 易於使用
- **OpenAI 兼容 API**：可無縫替換 OpenAI API，降低遷移成本
- **簡單的 Python 接口**：幾行代碼即可完成模型推理
- **支持主流模型**：兼容 HuggingFace 上的大部分主流 LLM 模型
- **即插即用**：無需複雜配置，開箱即用

### 3. 靈活部署
- **多 GPU 支持**：支持張量並行和管道並行
- **量化支持**：支持 AWQ、GPTQ 等量化方法，降低內存需求
- **LoRA 適配**：支持動態加載多個 LoRA 適配器
- **流式輸出**：支持 Server-Sent Events（SSE）流式響應

### 4. 生產就緒
- **高可用性**：穩定的服務端架構
- **監控指標**：內置 Prometheus 監控
- **水平擴展**：支持多節點部署
- **容器化部署**：提供官方 Docker 鏡像

## 安裝

### 基礎安裝

```bash
# 安裝 vLLM（需要 CUDA 11.8+）
pip install vllm

# 或從源碼安裝
pip install git+https://github.com/vllm-project/vllm.git
```

### 完整安裝（包含所有依賴）

```bash
# 克隆項目
git clone https://github.com/vllm-project/vllm.git
cd vllm

# 安裝依賴
pip install -r requirements.txt

# 安裝 vLLM
pip install -e .
```

### Docker 安裝

```bash
# 拉取官方鏡像
docker pull vllm/vllm-openai:latest

# 運行容器
docker run --runtime nvidia --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    -p 8000:8000 \
    --ipc=host \
    vllm/vllm-openai:latest \
    --model meta-llama/Llama-2-7b-chat-hf
```

## 使用案例

### 1. 快速開始

```python
from vllm import LLM, SamplingParams

# 初始化模型
llm = LLM(model="facebook/opt-125m")

# 設置生成參數
sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

# 生成文本
prompts = ["Hello, my name is", "The future of AI is"]
outputs = llm.generate(prompts, sampling_params)

# 打印結果
for output in outputs:
    print(f"Prompt: {output.prompt}")
    print(f"Generated: {output.outputs[0].text}")
```

### 2. OpenAI 兼容 API 服務

```bash
# 啟動 API 服務器
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-2-7b-chat-hf \
    --port 8000

# 使用 OpenAI 客戶端調用
from openai import OpenAI
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="token-abc123"
)

response = client.chat.completions.create(
    model="meta-llama/Llama-2-7b-chat-hf",
    messages=[
        {"role": "user", "content": "你好，請介紹一下 vLLM"}
    ]
)
print(response.choices[0].message.content)
```

### 3. 批量推理

```python
from vllm import LLM, SamplingParams

llm = LLM(model="meta-llama/Llama-2-7b-hf")
sampling_params = SamplingParams(temperature=0.8, max_tokens=100)

# 批量處理大量請求
prompts = [f"Question {i}: What is AI?" for i in range(100)]
outputs = llm.generate(prompts, sampling_params)

# vLLM 會自動優化批處理，最大化吞吐量
for i, output in enumerate(outputs):
    print(f"Response {i}: {output.outputs[0].text}")
```

### 4. 多 GPU 部署

```python
from vllm import LLM, SamplingParams

# 張量並行：跨 4 個 GPU 部署
llm = LLM(
    model="meta-llama/Llama-2-70b-hf",
    tensor_parallel_size=4,  # 使用 4 個 GPU
    dtype="float16"
)

sampling_params = SamplingParams(temperature=0.7, max_tokens=256)
outputs = llm.generate(["Explain quantum computing"], sampling_params)
```

### 5. 量化部署

```python
from vllm import LLM, SamplingParams

# 使用 AWQ 量化模型
llm = LLM(
    model="TheBloke/Llama-2-7B-Chat-AWQ",
    quantization="awq",
    dtype="float16"
)

# 相比 FP16 模型，內存佔用減少約 4 倍
sampling_params = SamplingParams(temperature=0.8)
outputs = llm.generate(["你好"], sampling_params)
```

## 與其他框架對比

### vLLM vs HuggingFace Transformers

| 特性 | vLLM | HuggingFace Transformers |
|------|------|--------------------------|
| **推理速度** | 極快（24x 提升） | 標準 |
| **內存效率** | 高（PagedAttention） | 中等 |
| **批處理** | 動態連續批處理 | 靜態批處理 |
| **易用性** | 簡單 | 簡單 |
| **模型支持** | 主流 LLM | 所有模型 |
| **生產環境** | 優秀 | 良好 |

### vLLM vs TGI (Text Generation Inference)

| 特性 | vLLM | TGI |
|------|------|-----|
| **性能** | 更快 | 快 |
| **內存管理** | PagedAttention | 動態批處理 |
| **API 兼容** | OpenAI 兼容 | 自定義 API |
| **部署靈活性** | 高 | 中 |
| **社區支持** | 活躍 | 活躍（HuggingFace） |

### vLLM vs TensorRT-LLM

| 特性 | vLLM | TensorRT-LLM |
|------|------|--------------|
| **性能** | 極快 | 最快 |
| **易用性** | 簡單 | 複雜（需編譯） |
| **靈活性** | 高 | 低 |
| **模型支持** | 即插即用 | 需要轉換 |
| **開發速度** | 快 | 慢 |

### vLLM vs llama.cpp

| 特性 | vLLM | llama.cpp |
|------|------|-----------|
| **硬件要求** | GPU（NVIDIA） | CPU/GPU（通用） |
| **性能** | GPU 上極快 | CPU 上優秀 |
| **內存需求** | 中（GPU 內存） | 低（系統內存） |
| **量化支持** | AWQ、GPTQ | GGUF 格式 |
| **適用場景** | 生產環境、高吞吐 | 邊緣設備、低資源 |

## 性能基準

根據官方測試（Meta Llama-2-7B 模型）：

```
環境：NVIDIA A100 GPU (40GB)
輸入：1000 個請求，平均 input length 256，output length 128

框架                吞吐量(tokens/s)    延遲(P50)    內存使用
vLLM               2,200              0.8s        18GB
HF Transformers    93                 22s         28GB
TGI                1,800              1.2s        22GB
```

## 最佳實踐

### 1. 選擇合適的批大小
- 根據 GPU 內存調整 `max_num_batched_tokens` 和 `max_num_seqs`
- 監控 GPU 內存使用率，保持在 80-90% 最佳

### 2. 使用量化降低成本
- 對於 70B 模型，推薦使用 AWQ 或 GPTQ 量化
- 可將內存需求降低 3-4 倍，性能損失小於 1%

### 3. 多 GPU 策略
- 13B 以下模型：單卡部署
- 13B-70B 模型：張量並行（2-4 卡）
- 70B+ 模型：張量並行 + 管道並行

### 4. 生產環境部署
- 使用 Docker 容器化部署
- 配置健康檢查和自動重啟
- 啟用 Prometheus 監控
- 使用負載均衡器分發請求

## 支持的模型

vLLM 支持以下架構的模型：

- **GPT 系列**：GPT-2, GPT-J, GPT-NeoX
- **LLaMA 系列**：LLaMA, LLaMA-2, Vicuna, Alpaca
- **OPT 系列**：OPT, OPT-IML
- **BLOOM 系列**：BLOOM, BLOOMZ
- **Falcon**：Falcon-7B, Falcon-40B
- **MPT**：MPT-7B, MPT-30B
- **Mistral**：Mistral-7B, Mixtral
- **Qwen**：Qwen, Qwen-1.5, Qwen-2

完整列表請參考：https://docs.vllm.ai/en/latest/models/supported_models.html

## 資源連結

- **官方網站**：https://vllm.ai/
- **GitHub**：https://github.com/vllm-project/vllm
- **文檔**：https://docs.vllm.ai/
- **論文**：https://arxiv.org/abs/2309.06180
- **Discord 社群**：https://discord.gg/vllm

## 授權

vLLM 採用 Apache 2.0 授權協議開源。

---

**更新日期**：2025-12-31
**版本**：v0.4.0+
