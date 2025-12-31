# OpenLLM - 開源 LLM 部署框架

## 簡介

OpenLLM 是由 BentoML 團隊開發的開源大型語言模型（LLM）部署和服務框架。它為開發者提供了一個簡單、高效的方式來部署、管理和服務各種開源 LLM 模型。OpenLLM 建立在 BentoML 之上，繼承了其強大的模型服務能力，同時針對 LLM 的特性進行了專門優化。

OpenLLM 的設計理念是讓 LLM 的部署變得像使用 API 一樣簡單，開發者無需深入了解底層技術細節，就能快速將模型部署到生產環境。它支持多種主流開源模型，提供統一的接口和工具鏈，大大降低了 LLM 應用的開發和運維成本。

## 核心特點

### 1. 廣泛的模型支持
- **主流開源模型**：支持 Llama、Mistral、Falcon、MPT、StarCoder 等熱門模型
- **多種架構**：支持自回歸、編碼器-解碼器等不同架構
- **模型庫整合**：與 HuggingFace Hub 無縫整合
- **自定義模型**：支持添加自定義模型定義

### 2. 靈活的部署方式
- **本地部署**：支持在本地環境快速啟動服務
- **容器化部署**：一鍵生成 Docker 鏡像
- **Kubernetes 部署**：原生支持 K8s 部署和擴展
- **雲端部署**：支持主流雲平台（AWS、GCP、Azure）

### 3. 生產級性能
- **批處理優化**：自動批處理請求以提高吞吐量
- **量化支持**：支持 INT8、INT4 量化降低內存需求
- **GPU 加速**：充分利用 GPU 資源
- **流式輸出**：支持流式生成，提升用戶體驗

### 4. 開發者友好
- **簡單的 CLI**：命令行工具一鍵啟動服務
- **RESTful API**：標準的 HTTP API 接口
- **OpenAI 兼容**：提供 OpenAI API 兼容層
- **豐富的文檔**：完整的使用指南和最佳實踐

### 5. BentoML 生態系統
- **模型管理**：統一的模型版本管理
- **服務編排**：支持複雜的服務編排
- **監控告警**：內置監控和日誌系統
- **A/B 測試**：支持多版本模型並行測試

## 安裝

### 基礎安裝

```bash
# 使用 pip 安裝（推薦）
pip install openllm

# 或使用 conda 安裝
conda install -c conda-forge openllm
```

### 完整安裝（包含所有後端）

```bash
# 安裝 OpenLLM 及所有運行時依賴
pip install "openllm[all]"

# 只安裝特定後端
pip install "openllm[vllm]"      # vLLM 後端
pip install "openllm[ctransformers]"  # CTransformers 後端
pip install "openllm[ggml]"      # GGML 後端
```

### 從源碼安裝

```bash
# 克隆倉庫
git clone https://github.com/bentoml/OpenLLM.git
cd OpenLLM

# 安裝開發版本
pip install -e .
```

### Docker 安裝

```bash
# 拉取官方鏡像
docker pull ghcr.io/bentoml/openllm

# 運行容器
docker run -it --rm \
  --gpus all \
  -p 3000:3000 \
  ghcr.io/bentoml/openllm \
  start llama --model-id meta-llama/Llama-2-7b-chat-hf
```

## 快速開始

### 命令行使用

```bash
# 啟動 Llama 2 模型服務
openllm start llama --model-id meta-llama/Llama-2-7b-chat-hf

# 啟動 Mistral 模型
openllm start mistral --model-id mistralai/Mistral-7B-Instruct-v0.1

# 使用量化模型
openllm start llama --model-id TheBloke/Llama-2-7B-Chat-GPTQ --quantize gptq

# 指定 GPU
openllm start llama --model-id meta-llama/Llama-2-7b-chat-hf --device cuda:0
```

### Python API

```python
import openllm

# 方式 1: 使用客戶端連接到服務
client = openllm.client.HTTPClient("http://localhost:3000")
response = client.query("What is machine learning?")
print(response)

# 方式 2: 直接在 Python 中使用模型
llm = openllm.LLM("llama", model_id="meta-llama/Llama-2-7b-chat-hf")
result = llm("Explain quantum computing in simple terms")
print(result)

# 流式生成
for token in llm.generate_iter("Tell me a story"):
    print(token, end="", flush=True)
```

### 使用 BentoML 構建服務

```python
# service.py
import bentoml
import openllm

# 獲取模型
model = openllm.LLM("llama", model_id="meta-llama/Llama-2-7b-chat-hf")

# 創建 BentoML runner
llm_runner = bentoml.Runner(model)

# 定義服務
svc = bentoml.Service("llm-service", runners=[llm_runner])

@svc.api(input=bentoml.io.Text(), output=bentoml.io.Text())
async def generate(input_text: str) -> str:
    result = await llm_runner.generate.async_run(input_text)
    return result
```

## 支持的模型

OpenLLM 支持以下主流開源模型：

### Llama 系列
- Meta Llama 2 (7B, 13B, 70B)
- Meta Llama 3 (8B, 70B)
- Vicuna
- Alpaca
- CodeLlama

### Mistral 系列
- Mistral 7B
- Mixtral 8x7B
- Zephyr

### 其他模型
- Falcon (7B, 40B, 180B)
- MPT (7B, 30B)
- StarCoder / StarCoderBase
- Dolly V2
- Flan-T5
- StableLM
- ChatGLM
- Baichuan
- Qwen

完整支持列表：https://github.com/bentoml/OpenLLM#-supported-models

## 高級功能

### 1. 量化部署

```bash
# GPTQ 量化
openllm start llama \
  --model-id TheBloke/Llama-2-7B-Chat-GPTQ \
  --quantize gptq

# AWQ 量化
openllm start llama \
  --model-id TheBloke/Llama-2-7B-Chat-AWQ \
  --quantize awq

# bitsandbytes 量化
openllm start llama \
  --model-id meta-llama/Llama-2-7b-chat-hf \
  --quantize int8
```

### 2. 多 GPU 部署

```bash
# 張量並行（跨多個 GPU）
openllm start llama \
  --model-id meta-llama/Llama-2-70b-chat-hf \
  --tensor-parallel-size 4

# 指定特定 GPU
openllm start llama \
  --model-id meta-llama/Llama-2-7b-chat-hf \
  --device "cuda:0,cuda:1"
```

### 3. 配置文件

```yaml
# config.yaml
model_name: llama
model_id: meta-llama/Llama-2-7b-chat-hf
backend: vllm

llm_config:
  max_model_len: 4096
  gpu_memory_utilization: 0.9
  quantization: awq

server_config:
  host: 0.0.0.0
  port: 3000
  workers: 1
```

```bash
# 使用配置文件啟動
openllm start --config config.yaml
```

### 4. Fine-tuned 模型

```python
import openllm

# 加載 fine-tuned 模型
llm = openllm.LLM(
    "llama",
    model_id="your-username/fine-tuned-llama-2-7b",
    trust_remote_code=True
)

# 使用模型
result = llm("Your prompt here")
```

## 與 BentoML 整合

### 構建 Bento

```python
# bentofile.yaml
service: "service:svc"
labels:
  owner: ml-team
  project: llm-service
include:
  - "*.py"
python:
  packages:
    - openllm
    - torch
    - transformers
```

```bash
# 構建 Bento
bentoml build

# 查看 Bento
bentoml list

# 容器化
bentoml containerize llm-service:latest

# 部署到 BentoCloud
bentoml deploy llm-service:latest
```

## 生產部署

### Kubernetes 部署

```bash
# 生成 Kubernetes 配置
openllm build llama --model-id meta-llama/Llama-2-7b-chat-hf

# 部署到 K8s
bentoml containerize llm-service:latest
kubectl apply -f deployment.yaml
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  openllm:
    image: ghcr.io/bentoml/openllm:latest
    command: start llama --model-id meta-llama/Llama-2-7b-chat-hf
    ports:
      - "3000:3000"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    volumes:
      - model-cache:/root/.cache/huggingface
```

### 負載均衡

```nginx
# nginx.conf
upstream openllm_backend {
    server openllm-1:3000;
    server openllm-2:3000;
    server openllm-3:3000;
}

server {
    listen 80;
    location / {
        proxy_pass http://openllm_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 監控和日誌

### Prometheus 監控

```python
# 啟用 Prometheus 指標
openllm start llama \
  --model-id meta-llama/Llama-2-7b-chat-hf \
  --enable-metrics

# 訪問指標端點
# http://localhost:3000/metrics
```

### 日誌配置

```python
import logging
import openllm

# 配置日誌級別
openllm.utils.set_debug_mode(True)
openllm.utils.configure_logging(level=logging.DEBUG)
```

## 最佳實踐

### 1. 模型選擇
- **7B 模型**：適合大多數應用場景，平衡性能和資源
- **13B 模型**：需要更好的理解能力時使用
- **70B+ 模型**：複雜任務，需要多 GPU 部署

### 2. 量化策略
- **GPTQ/AWQ**：4-bit 量化，內存減少 75%，精度損失小
- **INT8**：適度量化，更好的精度保持
- **無量化**：性能優先，GPU 內存充足時

### 3. 批處理優化
- 設置合適的 `max_batch_size` 和 `max_waiting_time`
- 監控 GPU 利用率，調整批大小
- 使用動態批處理提高吞吐量

### 4. 緩存策略
- 使用 HuggingFace 本地緩存避免重複下載
- 部署環境使用持久化存儲保存模型
- 預熱模型緩存提升啟動速度

## 與其他框架對比

### OpenLLM vs vLLM

| 特性 | OpenLLM | vLLM |
|------|---------|------|
| **易用性** | 極簡（CLI 一鍵啟動） | 簡單 |
| **模型支持** | 精選主流模型 | 更廣泛 |
| **性能** | 優秀 | 極致 |
| **部署方式** | BentoML 生態 | 獨立服務 |
| **生產工具** | 完整（監控、版本管理） | 基礎 |
| **學習曲線** | 低 | 中 |

### OpenLLM vs TGI

| 特性 | OpenLLM | Text-Generation-Inference |
|------|---------|--------------------------|
| **生態系統** | BentoML | HuggingFace |
| **API 風格** | RESTful + OpenAI | gRPC + HTTP |
| **模型管理** | 內置版本控制 | 基礎 |
| **部署靈活性** | 高（多種方式） | 中 |
| **社區支持** | 活躍 | 非常活躍 |

## 常見問題

### 1. 如何減少內存佔用？
- 使用量化模型（GPTQ、AWQ）
- 減小 `max_model_len`
- 降低 `gpu_memory_utilization`

### 2. 如何提高吞吐量？
- 增加批大小
- 使用更強大的 GPU
- 啟用張量並行

### 3. 如何處理長文本？
- 設置更大的 `max_model_len`
- 使用支持長上下文的模型
- 考慮文本分塊處理

## 資源連結

- **官方網站**：https://github.com/bentoml/OpenLLM
- **文檔**：https://github.com/bentoml/OpenLLM/tree/main/docs
- **BentoML 文檔**：https://docs.bentoml.org/
- **Discord 社群**：https://l.bentoml.com/join-openllm-discord
- **示例項目**：https://github.com/bentoml/OpenLLM/tree/main/examples

## 授權

OpenLLM 採用 Apache 2.0 授權協議開源。

---

**更新日期**：2025-12-31
**版本**：v0.4.0+
