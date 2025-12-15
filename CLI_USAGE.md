# LLM Agent Demo CLI 使用指南

## 概述

`llm-agent` 是一個強大的命令行工具，用於管理和監控 LLM Agent 專案的配置、成本和 API 金鑰。

## 安裝

### 從源碼安裝

```bash
# 克隆專案
git clone https://github.com/markl-a/LLM-agent-Demo.git
cd LLM-agent-Demo

# 安裝專案（開發模式）
pip install -e .
```

### 驗證安裝

```bash
llm-agent --version
llm-agent --help
```

## 核心命令

### 1. config - 查看配置

查看當前專案的配置信息，包括 LLM 提供商設定、RAG 參數和向量數據庫配置。

#### 基本用法

```bash
# 查看所有配置
llm-agent config

# 查看特定提供商的配置
llm-agent config -p openai
llm-agent config -p anthropic
llm-agent config -p google
llm-agent config -p groq

# 顯示完整的 API 金鑰（默認會遮蔽）
llm-agent config --show-keys

# 以 JSON 格式輸出（適合腳本使用）
llm-agent config -f json

# 重新載入配置（清除快取）
llm-agent config --reload
```

#### 輸出示例

```
╭────────────────────────────╮
│ 📋 LLM Agent Demo 配置信息 │
╰────────────────────────────╯

               應用程式設定
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ 設定項               ┃ 值          ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ 環境                 │ development │
│ 除錯模式             │ ✗ 禁用      │
│ 日誌級別             │ INFO        │
│ 最大重試次數         │ 3           │
│ 請求超時             │ 30 秒       │
│ 成本追蹤             │ ✓ 啟用      │
└──────────────────────┴─────────────┘

              OPENAI 配置
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ 設定項        ┃ 值                  ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ API 金鑰      │ ✓ sk-a***           │
│ 預設模型      │ gpt-4o-mini         │
│ API Base      │ https://...         │
└───────────────┴─────────────────────┘
```

#### JSON 輸出示例

```bash
llm-agent config -p openai -f json
```

```json
{
  "app": {
    "environment": "development",
    "debug": false,
    "log_level": "INFO"
  },
  "llm_providers": {
    "openai": {
      "api_key": "sk-a***",
      "model": "gpt-4o-mini",
      "configured": true
    }
  },
  "rag": {
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "top_k": 5,
    "embedding_model": "text-embedding-3-small"
  }
}
```

---

### 2. cost - 查看成本統計

查看 LLM API 的使用成本統計，包括 token 使用量和費用計算。

#### 基本用法

```bash
# 顯示價格表
llm-agent cost --pricing

# 從文件載入成本記錄
llm-agent cost -f ./cost_usage.json

# 只顯示特定模型的統計
llm-agent cost -f ./cost_usage.json -m gpt-4o

# 以 JSON 格式輸出
llm-agent cost -f ./cost_usage.json --format json
```

#### 價格表示例

```bash
llm-agent cost --pricing
```

```
╭───────────────────────────────────╮
│ 💰 LLM API 價格表 (USD/1K tokens) │
╰───────────────────────────────────╯

                  OpenAI
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ 模型            ┃  輸入價格 ┃  輸出價格 ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━┩
│ gpt-4o-mini     │ $0.000150 │ $0.000600 │
│ gpt-4o          │ $0.002500 │ $0.010000 │
│ gpt-4-turbo     │ $0.010000 │ $0.030000 │
└─────────────────┴───────────┴───────────┘
```

#### 成本統計示例

```
╭──────────────╮
│ 💰 API 成本統計 │
╰──────────────╯

┏━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ 項目         ┃   數值  ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ 總請求次數   │     125 │
│ 總 Token 數  │  45,230 │
│   └─ 輸入    │  32,100 │
│   └─ 輸出    │  13,130 │
│ 總成本       │ $0.0523 │
└──────────────┴─────────┘

           按模型統計
┏━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┓
┃ 模型        ┃ 請求次數 ┃ Token 數 ┃   成本  ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━┩
│ gpt-4o      │      50 │  25,000 │ $0.0350 │
│ gpt-4o-mini │      75 │  20,230 │ $0.0173 │
└─────────────┴─────────┴─────────┴─────────┘
```

---

### 3. validate - 驗證 API 金鑰

驗證 API 金鑰是否正確配置並符合格式要求。

#### 基本用法

```bash
# 驗證所有提供商的 API 金鑰
llm-agent validate

# 只驗證特定提供商
llm-agent validate -p openai
llm-agent validate -p anthropic

# 嘗試自動修復常見問題（如移除空格）
llm-agent validate --fix
```

#### 輸出示例

```
╭─────────────────╮
│ 🔑 API 金鑰驗證 │
╰─────────────────╯

┏━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 提供商    ┃ 狀態    ┃ 詳情                      ┃
┡━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ OPENAI    │ ✓ 通過  │ 金鑰長度: 51 字符         │
│           │         │ 金鑰前綴: sk-proj-... │
├───────────┼─────────┼───────────────────────────┤
│ ANTHROPIC │ ✗ 失敗  │ 請設定環境變數 ANTHROPIC_API_KEY │
├───────────┼─────────┼───────────────────────────┤
│ GOOGLE    │ ✓ 通過  │ 金鑰長度: 39 字符         │
│           │         │ 金鑰前綴: AIzaSy...       │
├───────────┼─────────┼───────────────────────────┤
│ GROQ      │ ✗ 失敗  │ 請設定環境變數 GROQ_API_KEY │
└───────────┴─────────┴───────────────────────────┘
```

---

## 配置環境變數

CLI 工具會從以下來源讀取配置：

1. 環境變數
2. `.env` 文件（專案根目錄）

### 創建 .env 文件

在專案根目錄創建 `.env` 文件：

```bash
# .env

# OpenAI
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_BASE=https://api.openai.com/v1

# Anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Google Gemini
GOOGLE_API_KEY=your-google-api-key
GOOGLE_MODEL=gemini-2.0-flash-exp

# Groq
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama-3.3-70b-versatile

# 應用程式設定
APP_ENV=development
DEBUG=false
LOG_LEVEL=INFO
MAX_RETRIES=3
TIMEOUT=30
ENABLE_COST_TRACKING=true

# RAG 設定
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K=5
EMBEDDING_MODEL=text-embedding-3-small
MAX_TOKENS=4000
TEMPERATURE=0.7

# 向量數據庫
CHROMA_PERSIST_DIRECTORY=./chroma_db
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=your-environment
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your-qdrant-key
```

---

## 在 Python 腳本中使用

CLI 工具也可以在 Python 腳本中程式化使用：

```python
from llm_agent_demo.utils.config import get_settings
from llm_agent_demo.utils.cost_tracker import CostTracker
from llm_agent_demo.utils.validators import validate_openai_api_key

# 獲取配置
settings = get_settings()
print(f"OpenAI 模型: {settings.openai_model}")

# 驗證 API 金鑰
try:
    validate_openai_api_key(settings.openai_api_key)
    print("✓ OpenAI API 金鑰有效")
except Exception as e:
    print(f"✗ 驗證失敗: {e}")

# 使用成本追蹤器
tracker = CostTracker(save_path="./usage.json")
tracker.track_usage(
    prompt_tokens=1000,
    completion_tokens=500,
    model="gpt-4o-mini",
    provider="openai"
)
tracker.print_summary()
```

---

## 進階用法

### 與 CI/CD 整合

```yaml
# .github/workflows/validate.yml
name: Validate API Keys

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -e .
      - name: Validate API keys
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          llm-agent validate -p openai
```

### 自動化成本監控

```bash
#!/bin/bash
# monitor_costs.sh

# 每小時檢查成本
while true; do
    llm-agent cost -f ./usage.json -f json > cost_report.json

    # 檢查是否超過預算
    total_cost=$(jq '.total_cost' cost_report.json)
    if (( $(echo "$total_cost > 10.0" | bc -l) )); then
        echo "警告: 成本超過 $10！"
        # 發送通知...
    fi

    sleep 3600  # 等待 1 小時
done
```

---

## 故障排除

### 問題 1: 找不到命令 `llm-agent`

**解決方案:**
```bash
# 確保已安裝專案
pip install -e .

# 或使用模組方式運行
python -m llm_agent_demo.cli --help
```

### 問題 2: API 金鑰驗證失敗

**解決方案:**
1. 檢查 `.env` 文件是否存在
2. 確認 API 金鑰格式正確（無多餘空格）
3. 使用 `--fix` 選項自動修復常見問題

```bash
llm-agent validate --fix
```

### 問題 3: 無法載入成本記錄

**解決方案:**
確保指定的文件路徑正確：

```bash
llm-agent cost -f ./cost_usage.json
```

---

## 貢獻

歡迎貢獻！請查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解更多信息。

## 許可證

MIT License - 查看 [LICENSE](LICENSE) 文件了解詳情。
