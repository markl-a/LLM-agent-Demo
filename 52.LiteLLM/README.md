# LiteLLM - 統一 LLM API 網關

## 框架簡介

LiteLLM 是一個功能強大的 Python SDK 和 AI 網關（代理伺服器），為開發者提供統一的介面來呼叫 100+ 種大型語言模型 API。無論您使用 OpenAI、Anthropic、Google、AWS Bedrock 還是其他任何 LLM 提供商，LiteLLM 都能讓您用相同的程式碼格式進行呼叫。

### 核心價值

- **統一介面**：使用 OpenAI 格式呼叫所有 LLM，大幅降低學習成本
- **靈活切換**：輕鬆在不同模型供應商之間切換，無需重寫程式碼
- **企業級功能**：成本追蹤、負載均衡、快取、護欄等生產環境必備功能
- **高效能**：P95 延遲僅 8ms，適合大規模部署

## 主要特性

### 1. 100+ 模型支援

LiteLLM 支援所有主流 LLM 提供商：

- **OpenAI**：GPT-4、GPT-3.5、GPT-4 Turbo、GPT-4o
- **Anthropic**：Claude 3.5 Sonnet、Claude 3 Opus/Sonnet/Haiku
- **Google**：Gemini Pro、PaLM 2
- **AWS Bedrock**：Claude、Llama、Titan
- **Azure OpenAI**：所有 Azure 託管的模型
- **Cohere**：Command、Embed
- **Hugging Face**：開源模型
- **Replicate**：社群模型
- **本地模型**：Ollama、LM Studio

### 2. 成本追蹤與管理

- **即時成本計算**：自動追蹤每次 API 呼叫的成本
- **預算控制**：設定使用者、團隊或專案級別的預算上限
- **成本分析**：詳細的成本分析報告和趨勢圖表
- **多幣別支援**：支援多種貨幣單位顯示

### 3. 負載均衡與容錯

- **智慧路由**：根據延遲、成本、可用性自動選擇最佳模型
- **故障轉移**：自動切換到備用模型，確保服務可用性
- **速率限制管理**：智慧處理 API 速率限制
- **重試機制**：可配置的重試策略

### 4. 效能優化

- **回應快取**：相同請求直接返回快取結果
- **批次處理**：支援批次 API 呼叫
- **8ms P95 延遲**：極低的額外延遲
- **串流支援**：完整支援串流式回應

### 5. 安全與護欄

- **內容過濾**：自動檢測和過濾不當內容
- **提示注入防護**：防止惡意提示注入攻擊
- **PII 檢測**：識別和保護個人敏感資訊
- **存取控制**：基於角色的存取控制（RBAC）

### 6. 可觀測性

- **詳細日誌**：完整的請求/回應日誌記錄
- **效能監控**：延遲、成功率等關鍵指標
- **整合支援**：Prometheus、Grafana、DataDog 等
- **告警系統**：自訂告警規則

## 安裝指南

### 基礎安裝

```bash
# 安裝 LiteLLM SDK
pip install litellm

# 安裝完整版本（包含所有供應商的 SDK）
pip install 'litellm[extra]'

# 安裝代理伺服器
pip install 'litellm[proxy]'
```

### Docker 部署

```bash
# 拉取映像檔
docker pull ghcr.io/berriai/litellm:main-latest

# 執行代理伺服器
docker run -p 4000:4000 ghcr.io/berriai/litellm:main-latest
```

### 環境變數設定

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# AWS Bedrock
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION_NAME="us-east-1"

# Azure OpenAI
export AZURE_API_KEY="..."
export AZURE_API_BASE="https://..."
export AZURE_API_VERSION="2024-02-01"
```

## 快速開始

### SDK 基本使用

```python
from litellm import completion
import os

# 設定 API 金鑰
os.environ["OPENAI_API_KEY"] = "your-api-key"

# 呼叫 OpenAI
response = completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "你好，請介紹一下 LiteLLM"}]
)
print(response.choices[0].message.content)

# 切換到 Anthropic Claude，只需修改模型名稱
response = completion(
    model="claude-3-5-sonnet-20241022",
    messages=[{"role": "user", "content": "你好，請介紹一下 LiteLLM"}]
)
print(response.choices[0].message.content)
```

### 代理伺服器模式

```bash
# 建立設定檔 config.yaml
cat > config.yaml << EOF
model_list:
  - model_name: gpt-4
    litellm_params:
      model: gpt-4
      api_key: os.environ/OPENAI_API_KEY

  - model_name: claude-3-5-sonnet
    litellm_params:
      model: claude-3-5-sonnet-20241022
      api_key: os.environ/ANTHROPIC_API_KEY

litellm_settings:
  success_callback: ["langfuse"]
  failure_callback: ["sentry"]
EOF

# 啟動代理伺服器
litellm --config config.yaml --port 4000
```

### 使用代理伺服器

```python
import openai

# 設定代理伺服器
client = openai.OpenAI(
    api_key="sk-1234",  # 代理伺服器的 API 金鑰
    base_url="http://localhost:4000"
)

# 使用標準 OpenAI SDK 呼叫
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "你好"}]
)
print(response.choices[0].message.content)
```

## 主要使用場景

### 1. 多模型整合

當您需要在應用中整合多個 LLM 供應商時，LiteLLM 提供統一的介面：

```python
from litellm import completion

def call_llm(provider, prompt):
    """統一的 LLM 呼叫函數"""
    model_map = {
        "openai": "gpt-4o",
        "anthropic": "claude-3-5-sonnet-20241022",
        "google": "gemini-pro",
        "aws": "bedrock/anthropic.claude-3-sonnet-20240229-v1:0"
    }

    return completion(
        model=model_map[provider],
        messages=[{"role": "user", "content": prompt}]
    )
```

### 2. 成本優化

透過成本追蹤和負載均衡，優化 LLM 使用成本：

```python
from litellm import completion, cost_per_token

# 自動選擇成本最低的模型
models = ["gpt-3.5-turbo", "claude-3-haiku-20240307"]
prompt = "分析這段文字的情感傾向"

costs = []
for model in models:
    cost = cost_per_token(model=model, prompt_tokens=100, completion_tokens=50)
    costs.append((model, cost))

# 使用成本最低的模型
best_model = min(costs, key=lambda x: x[1])[0]
response = completion(model=best_model, messages=[{"role": "user", "content": prompt}])
```

### 3. 高可用性系統

使用負載均衡和故障轉移確保系統可用性：

```python
from litellm import completion

# 設定主要模型和備用模型
response = completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "重要的業務查詢"}],
    fallbacks=["gpt-4-turbo", "claude-3-5-sonnet-20241022"]
)
```

### 4. 企業級部署

代理伺服器模式提供企業級功能：

- **集中式管理**：統一管理所有 API 金鑰和模型設定
- **使用者認證**：支援多種認證方式（API Key、JWT、OAuth）
- **配額管理**：團隊和使用者級別的配額控制
- **審計日誌**：完整的使用記錄和合規支援

### 5. 成本控制與預算

```python
# 在代理伺服器設定檔中設定預算
model_list:
  - model_name: gpt-4
    litellm_params:
      model: gpt-4
    model_info:
      max_budget: 100.0  # 每月最多 100 美元
      budget_duration: 30d
```

### 6. A/B 測試

輕鬆進行不同模型的 A/B 測試：

```python
import random
from litellm import completion

def ab_test_llm(prompt):
    """50/50 流量分配"""
    model = random.choice(["gpt-4o", "claude-3-5-sonnet-20241022"])
    response = completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        metadata={"experiment": "model_comparison", "variant": model}
    )
    return response
```

## 進階功能

### 串流回應

```python
from litellm import completion

response = completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "寫一首關於 AI 的詩"}],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### 嵌入向量

```python
from litellm import embedding

# OpenAI 嵌入
response = embedding(
    model="text-embedding-3-small",
    input=["LiteLLM 是一個很棒的工具"]
)
print(response.data[0].embedding)

# 切換到其他供應商
response = embedding(
    model="cohere/embed-english-v3.0",
    input=["LiteLLM is a great tool"]
)
```

### 函數呼叫

```python
from litellm import completion

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "取得指定城市的天氣",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名稱"}
                },
                "required": ["city"]
            }
        }
    }
]

response = completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "台北現在天氣如何？"}],
    tools=tools,
    tool_choice="auto"
)
```

## 效能指標

- **延遲**：P95 延遲 8ms（相比直接呼叫 API）
- **吞吐量**：支援每秒數千次請求
- **可用性**：99.9% SLA（使用容錯配置）
- **擴展性**：支援水平擴展到數百個節點

## 社群與支援

- **GitHub**：https://github.com/BerriAI/litellm
- **文件**：https://docs.litellm.ai
- **Discord**：https://discord.com/invite/wuPM9dRgDw
- **電子郵件**：support@berri.ai

## 授權

MIT License

## 總結

LiteLLM 是現代 AI 應用開發的理想選擇，特別適合：

- 需要整合多個 LLM 供應商的應用
- 注重成本控制和優化的企業
- 需要高可用性和效能的生產系統
- 希望簡化 LLM 整合複雜度的開發團隊

透過 LiteLLM，您可以專注於構建優秀的 AI 應用，而不必擔心底層 API 的複雜性和差異。
