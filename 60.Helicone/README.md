# Helicone - AI 網關與可觀測性平台

## 框架簡介

Helicone 是一個強大的 AI 網關(AI Gateway)和可觀測性平台,專為管理和監控大型語言模型(LLM)應用程序而設計。它提供了一個統一的接口來處理多個 AI 模型提供商,同時提供路由、故障轉移、速率限制、快取和全面的可觀測性功能。

### 什麼是 AI 網關?

AI 網關是位於您的應用程序和 AI 模型提供商之間的中間層,它可以:
- 統一管理多個 AI 模型提供商
- 提供智能路由和負載均衡
- 實現成本優化和快取策略
- 監控和追蹤所有 API 請求
- 提供安全性和合規性控制

### 為什麼選擇 Helicone?

- **簡單易用**: 只需一行代碼即可集成
- **多模型支持**: 支援 100+ 個 AI 模型
- **全面監控**: 完整的請求追蹤和分析
- **成本優化**: 智能快取和成本分析
- **高可用性**: 自動故障轉移和負載均衡
- **靈活部署**: 雲端或自託管選項

## 核心功能

### 1. 路由管理 (Routing)
- **智能路由**: 根據模型可用性、成本、延遲自動選擇最佳端點
- **負載均衡**: 在多個端點之間分配請求
- **故障轉移**: 自動切換到備用模型或端點
- **A/B 測試**: 輕鬆比較不同模型的性能

### 2. 快取系統 (Caching)
- **語義快取**: 基於語義相似性的智能快取
- **精確快取**: 完全匹配的快取策略
- **成本節省**: 減少 API 調用次數,降低成本高達 90%
- **自定義 TTL**: 靈活的快取過期時間設置

### 3. 限流控制 (Rate Limiting)
- **用戶級限流**: 為不同用戶設置不同的速率限制
- **端點限流**: 保護您的 API 端點不被濫用
- **成本控制**: 設置預算上限,防止意外高額費用
- **配額管理**: 靈活的配額分配和追蹤

### 4. 可觀測性 (Observability)
- **請求追蹤**: 詳細記錄每個 API 請求和響應
- **性能監控**: 追蹤延遲、吞吐量、錯誤率
- **成本分析**: 實時成本追蹤和預測
- **自定義儀表板**: 可視化您的 AI 使用情況

### 5. 100+ 模型支持
- **OpenAI**: GPT-4, GPT-3.5, GPT-4 Turbo, o1
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku
- **Google**: Gemini Pro, Gemini Ultra, PaLM 2
- **Meta**: Llama 2, Llama 3, Code Llama
- **Cohere**: Command, Generate, Embed
- **Mistral AI**: Mistral Large, Mistral Medium
- **開源模型**: 通過 vLLM, Ollama, Together AI 等

## 安裝指南

### 前置要求

- Python 3.8+
- API 密鑰(來自您選擇的 AI 模型提供商)
- Helicone API 密鑰(免費註冊於 https://helicone.ai)

### 基本安裝

```bash
# 安裝 Helicone 和相關依賴
pip install helicone openai anthropic

# 或使用 requirements.txt
pip install -r requirements.txt
```

### 環境變量設置

```bash
# 設置 Helicone API 密鑰
export HELICONE_API_KEY="your-helicone-api-key"

# 設置模型提供商 API 密鑰
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

## 快速開始

### 方法 1: 一行代碼集成 (推薦)

```python
from helicone import openai_proxy
import openai

# 只需將 base_url 指向 Helicone 代理
client = openai.OpenAI(
    api_key="your-openai-api-key",
    base_url="https://oai.helicone.ai/v1",
    default_headers={
        "Helicone-Auth": f"Bearer {HELICONE_API_KEY}"
    }
)

# 正常使用,所有請求都會被 Helicone 追蹤
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### 方法 2: 使用 Helicone SDK

```python
from helicone import Helicone
import openai

# 初始化 Helicone
helicone = Helicone(api_key="your-helicone-api-key")

# 包裝您的 OpenAI 客戶端
client = helicone.openai()

# 使用
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### 方法 3: 自託管部署

```bash
# 使用 Docker Compose 啟動 Helicone
git clone https://github.com/Helicone/helicone
cd helicone
docker-compose up -d
```

## 使用案例

### 1. 成本優化

使用 Helicone 的快取功能,可以大幅降低 API 調用成本:

```python
# 啟用快取
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "什麼是機器學習?"}],
    extra_headers={
        "Helicone-Cache-Enabled": "true",
        "Helicone-Cache-Bucket-Max-Size": "100"
    }
)

# 第二次相同請求會從快取返回,節省成本
```

**實際效果**:
- 減少 API 調用次數 50-90%
- 降低響應延遲 80-95%
- 每月節省數千美元

### 2. 生產環境監控

監控您的 AI 應用程序性能和使用情況:

```python
# 添加自定義屬性以便追蹤
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "分析這段代碼"}],
    extra_headers={
        "Helicone-User-Id": "user-123",
        "Helicone-Session-Id": "session-456",
        "Helicone-Property-Environment": "production",
        "Helicone-Property-Feature": "code-analysis"
    }
)
```

**監控指標**:
- 請求延遲和成功率
- 每個用戶/功能的使用情況
- 成本歸屬和預測
- 錯誤追蹤和告警

### 3. A/B 測試

比較不同模型的性能:

```python
import random

# 隨機選擇模型進行測試
model = random.choice(["gpt-4", "gpt-3.5-turbo"])

response = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "寫一個產品描述"}],
    extra_headers={
        "Helicone-Property-Experiment": "model-comparison",
        "Helicone-Property-Variant": model
    }
)
```

### 4. 多租戶應用

為不同客戶提供獨立的使用追蹤和限流:

```python
# 為每個租戶設置配額
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "生成報告"}],
    extra_headers={
        "Helicone-User-Id": f"tenant-{tenant_id}",
        "Helicone-Rate-Limit-Policy": "tier-premium",
        "Helicone-Property-Organization": org_name
    }
)
```

### 5. 故障轉移和高可用性

自動切換到備用模型:

```python
# 配置故障轉移
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "處理請求"}],
    extra_headers={
        "Helicone-Fallback-Model": "gpt-3.5-turbo",
        "Helicone-Retry-Enabled": "true",
        "Helicone-Retry-Count": "3"
    }
)
```

## 核心概念

### 請求追蹤

每個通過 Helicone 的請求都會被完整記錄:
- 請求時間和持續時間
- 輸入和輸出 token 數量
- 成本計算
- 模型和參數
- 自定義屬性和元數據

### 會話管理

將相關請求組織在一起:
- 使用 `Helicone-Session-Id` 追蹤對話
- 分析整個會話的成本和性能
- 調試多輪對話問題

### 用戶歸屬

追蹤每個用戶的使用情況:
- 使用 `Helicone-User-Id` 標識用戶
- 按用戶分析成本和使用模式
- 實施用戶級別的速率限制

## 進階功能

### 1. 自定義提示版本控制

```python
# 追蹤不同版本的提示詞
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "優化的提示詞 v2"}],
    extra_headers={
        "Helicone-Prompt-Id": "customer-support-v2",
        "Helicone-Property-Version": "2.0"
    }
)
```

### 2. 成本告警

設置預算限制和告警:
- 每日/每月預算上限
- 異常使用檢測
- 實時成本通知
- 自動降級策略

### 3. 數據導出

導出您的數據進行分析:
- CSV/JSON 格式導出
- 與 BI 工具集成
- 自定義報告生成
- API 訪問歷史數據

### 4. 團隊協作

- 多用戶訪問控制
- 角色和權限管理
- 審計日誌
- 共享儀表板

## 架構設計

### 雲端架構

```
您的應用 → Helicone 雲端網關 → AI 模型提供商
             ↓
         可觀測性平台
```

### 自託管架構

```
您的應用 → Helicone Docker → AI 模型提供商
             ↓
         本地數據庫
```

## 性能指標

- **延遲開銷**: < 10ms (雲端), < 1ms (自託管)
- **可用性**: 99.9% SLA
- **吞吐量**: 每秒處理 10,000+ 請求
- **數據保留**: 90 天(免費版), 無限制(企業版)

## 定價

- **開發者版**: 免費
  - 100,000 請求/月
  - 基本可觀測性
  - 社區支持

- **專業版**: $50/月
  - 1,000,000 請求/月
  - 高級分析
  - 優先支持

- **企業版**: 聯繫銷售
  - 無限請求
  - 自託管選項
  - 專屬支持
  - SLA 保證

## 最佳實踐

1. **總是使用會話 ID**: 便於追蹤和調試多輪對話
2. **設置用戶 ID**: 實現精確的成本歸屬
3. **啟用快取**: 對於重複查詢可節省大量成本
4. **監控成本**: 設置預算告警,避免意外費用
5. **使用自定義屬性**: 便於分類和分析請求
6. **定期審查**: 查看儀表板,優化使用模式

## 常見問題

**Q: Helicone 會增加多少延遲?**
A: 雲端版本通常增加 < 10ms,自託管版本 < 1ms。

**Q: 我的數據安全嗎?**
A: Helicone 支持端到端加密,且可以選擇自託管以完全控制數據。

**Q: 可以在不修改代碼的情況下使用嗎?**
A: 可以,只需修改 base_url 即可。

**Q: 支持哪些編程語言?**
A: 官方支持 Python, JavaScript/TypeScript, Go。其他語言可通過 REST API 使用。

## 資源鏈接

- 官方網站: https://helicone.ai
- 文檔: https://docs.helicone.ai
- GitHub: https://github.com/Helicone/helicone
- Discord 社區: https://discord.gg/helicone
- API 參考: https://docs.helicone.ai/api-reference

## 範例文件說明

本目錄包含 10 個詳細的 Python 範例:

1. **01_快速開始.py** - 基本設置和一行集成
2. **02_請求追蹤.py** - 請求追蹤和日誌記錄
3. **03_快取策略.py** - 快取配置和成本節省
4. **04_路由管理.py** - 路由和故障轉移
5. **05_限流控制.py** - 速率限制和配額管理
6. **06_成本分析.py** - 成本分析和優化
7. **07_用戶追蹤.py** - 用戶追蹤和會話管理
8. **08_自定義屬性.py** - 自定義屬性和元數據
9. **09_自託管.py** - Docker 自託管部署
10. **10_生產部署.py** - 生產環境部署

每個文件都包含詳細的中文註釋和實用範例。

## 貢獻

歡迎提交問題和拉取請求!

## 許可證

本範例代碼採用 MIT 許可證。
