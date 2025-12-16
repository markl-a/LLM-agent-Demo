# LiteLLM - 統一的 LLM API 代理層

## 概述

LiteLLM 是一個開源的 Python 函式庫，提供統一的介面來呼叫 100+ 種不同的大型語言模型 API。它就像是 LLM API 的萬用翻譯器，讓您只需要學習一個介面，就能連接到所有主流的 AI 服務提供商。

## 主要特點

### 🌐 統一的 API 介面
- 使用 OpenAI 格式的統一介面存取任何模型
- 支援超過 100 種 LLM 提供商（OpenAI、Azure、Anthropic、Cohere、HuggingFace、VertexAI 等）
- 一次編寫代碼，可在任何提供商上運行

### ⚡ 高性能
- 極低延遲：在 1k RPS 下 P95 延遲僅 8ms
- 可處理 1500+ 請求/秒的負載測試

### 🔄 智能路由與負載均衡
- 多種路由策略：simple-shuffle、least-busy、usage-based、latency-based
- 自動故障轉移和回退機制
- 支援多個部署之間的負載均衡
- Redis 支援分散式狀態管理

### 💰 成本追蹤
- 自動追蹤所有已知模型的費用
- 支援串流和非串流響應的成本計算
- 提供詳細的每日使用數據（按模型、提供商、API 金鑰）
- 整合觀測工具（Langfuse、MLflow 等）

### 🛡️ 可靠性功能
- 自動重試（固定和指數退避）
- 超時控制
- 熔斷器模式（Cooldown）
- 請求限速（RPM/TPM）

### 🔧 雙重架構
1. **Python SDK** - 直接在代碼中使用
2. **Proxy Server** - 作為團隊和企業的中央 AI 閘道

### 📊 其他功能
- 串流響應支援
- Function Calling（工具調用）
- 緩存策略
- 安全防護（Guardrails）
- 管理儀表板
- 日誌記錄

## 安裝方式

### 基礎安裝

```bash
pip install litellm
```

### 需求
- Python >= 3.9 且 < 4.0
- MIT 授權

### 安裝 Proxy Server（可選）

```bash
pip install 'litellm[proxy]'
```

### 從源碼安裝

```bash
git clone https://github.com/BerriAI/litellm.git
cd litellm
pip install -e .
```

## 快速開始

### 使用 Python SDK

```python
from litellm import completion
import os

# 設定 API 金鑰
os.environ["OPENAI_API_KEY"] = "your-api-key"

# 呼叫模型
response = completion(
    model="gpt-4",
    messages=[{"content": "Hello, how are you?", "role": "user"}]
)

print(response.choices[0].message.content)
```

### 使用 Proxy Server

1. 啟動代理伺服器：

```bash
litellm --model gpt-3.5-turbo

# 或使用配置檔案
litellm --config config.yaml
```

2. 通過代理調用：

```python
import openai

client = openai.OpenAI(
    api_key="anything",
    base_url="http://0.0.0.0:4000"
)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## 支援的提供商

- **OpenAI** - GPT-3.5, GPT-4, GPT-4o 等
- **Anthropic** - Claude 3.5 Sonnet, Claude 3 Opus 等
- **Azure OpenAI** - Azure 託管的模型
- **Google** - VertexAI, Gemini
- **AWS** - Bedrock, Sagemaker
- **Cohere** - Command, Embed
- **HuggingFace** - 各種開源模型
- **本地部署** - Ollama, vLLM, LM Studio
- **其他** - Anthropic, Replicate, Together AI 等 100+ 種

## 架構組件

### Python SDK
```
應用程式 → litellm.completion() → LLM 提供商
```

### Proxy Server
```
應用程式 → LiteLLM Proxy → Router → 負載均衡 → 多個 LLM 部署
                          ↓
                    成本追蹤、日誌、限速
```

## 配置檔案範例

```yaml
model_list:
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: os.environ/OPENAI_API_KEY

  - model_name: claude-3
    litellm_params:
      model: anthropic/claude-3-sonnet-20240229
      api_key: os.environ/ANTHROPIC_API_KEY

router_settings:
  routing_strategy: simple-shuffle
  num_retries: 3
  timeout: 30

litellm_settings:
  success_callback: ["langfuse"]
  cache: true
```

## 主要使用場景

1. **多模型測試** - 輕鬆測試不同提供商的模型性能
2. **故障轉移** - 當主要提供商故障時自動切換
3. **成本優化** - 根據成本和性能選擇最佳模型
4. **企業 AI 閘道** - 集中管理團隊的所有 LLM 存取
5. **開發與生產環境隔離** - 開發用 GPT-3.5，生產用 GPT-4

## 範例檔案說明

本資料夾包含 10 個詳細的 Python 範例：

1. **01_快速開始.py** - LiteLLM 基礎使用和多提供商調用
2. **02_多模型調用.py** - 同時使用多個提供商和模型
3. **03_流式輸出.py** - 串流響應處理
4. **04_函數調用.py** - Function Calling 和工具使用
5. **05_負載均衡.py** - 路由策略和負載均衡配置
6. **06_成本追蹤.py** - 費用監控和預算管理
7. **07_錯誤處理.py** - 重試、回退和錯誤處理
8. **08_代理服務.py** - Proxy Server 配置和使用
9. **09_緩存策略.py** - 緩存配置以節省成本
10. **10_進階技巧.py** - 高級功能和最佳實踐

## 環境變數設定

在運行範例之前，請設定相關的 API 金鑰：

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Azure
export AZURE_API_KEY="..."
export AZURE_API_BASE="https://..."
export AZURE_API_VERSION="2024-02-15-preview"

# Cohere
export COHERE_API_KEY="..."

# Google VertexAI
export VERTEX_PROJECT="..."
export VERTEX_LOCATION="..."
```

## 效能指標

- **延遲**: 8ms (P95 @ 1k RPS)
- **吞吐量**: 1500+ 請求/秒
- **可用性**: 支援多區域容錯
- **可擴展性**: 支援 Kubernetes 和多實例部署

## 最佳實踐

1. **使用環境變數** - 不要硬編碼 API 金鑰
2. **設定超時** - 避免長時間等待
3. **啟用重試** - 提高可靠性
4. **監控成本** - 使用成本追蹤功能
5. **配置緩存** - 減少重複請求的成本
6. **使用 Proxy** - 團隊協作時使用代理伺服器
7. **日誌記錄** - 啟用詳細日誌以便除錯

## 常見問題

### Q: LiteLLM 和直接使用提供商 SDK 的區別？
A: LiteLLM 提供統一介面，讓您可以輕鬆切換提供商，並獲得額外的功能如負載均衡、成本追蹤等。

### Q: 是否支援本地模型？
A: 是的，支援 Ollama、vLLM、LM Studio 等本地部署方案。

### Q: 如何處理 API 金鑰安全？
A: 使用環境變數或 Proxy Server 的金鑰管理功能，永遠不要在代碼中硬編碼。

### Q: 成本追蹤準確嗎？
A: LiteLLM 使用官方定價數據，並定期從 GitHub 同步更新，確保準確性。

## 資源連結

- **官方文檔**: https://docs.litellm.ai/
- **GitHub**: https://github.com/BerriAI/litellm
- **PyPI**: https://pypi.org/project/litellm/
- **負載均衡文檔**: https://docs.litellm.ai/docs/proxy/load_balancing
- **路由文檔**: https://docs.litellm.ai/docs/routing
- **成本追蹤文檔**: https://docs.litellm.ai/docs/proxy/cost_tracking
- **串流文檔**: https://docs.litellm.ai/docs/completion/stream

## 授權

MIT License

## 貢獻

歡迎貢獻！請訪問 [GitHub 倉庫](https://github.com/BerriAI/litellm) 提交 Issue 或 Pull Request。

---

**最後更新**: 2025-12-15
**LiteLLM 版本**: 最新穩定版
