# 最小化示例集合

這個目錄包含一系列最簡化的 AI Agent 入門示例，適合新手驗證開發環境和理解基本概念。

## 特點

- **極簡代碼**：每個示例都控制在 20-60 行代碼
- **完整註釋**：所有代碼都有詳細的中文註釋
- **快速驗證**：無需複雜配置，設置好 API key 即可運行
- **清晰輸出**：每個示例都有明確的運行結果展示

## 示例列表

| 文件 | 說明 | 代碼行數 |
|------|------|----------|
| `01_openai_hello.py` | OpenAI API 基礎調用 | ~20行 |
| `02_anthropic_hello.py` | Claude API 基礎調用 | ~20行 |
| `03_ollama_hello.py` | 本地 Ollama 模型調用 | ~20行 |
| `04_streaming.py` | 流式輸出實現 | ~30行 |
| `05_simple_agent.py` | 單一 Agent 實現 | ~40行 |
| `06_simple_rag.py` | RAG 檢索增強生成 | ~50行 |
| `07_multi_agent.py` | 多 Agent 協作 | ~60行 |

## 環境準備

### 1. 安裝依賴

```bash
pip install openai anthropic ollama
```

### 2. 設置 API Keys

```bash
# OpenAI
export OPENAI_API_KEY="your-openai-api-key"

# Anthropic (Claude)
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# Ollama 需要本地安裝並運行
# 安裝：https://ollama.ai/
# 運行：ollama serve
```

### 3. 驗證 Ollama（本地模型）

```bash
# 下載模型
ollama pull llama2

# 驗證運行
ollama run llama2 "Hello"
```

## 運行示例

```bash
cd examples/minimal

# 運行任意示例
python 01_openai_hello.py
python 02_anthropic_hello.py
python 03_ollama_hello.py
# ...
```

## 學習路徑

建議按照文件編號順序學習：

1. **基礎調用** (01-03)：理解不同 LLM 的基本調用方式
2. **流式輸出** (04)：學習如何實現打字機效果
3. **Agent 概念** (05)：理解 Agent 的基本結構
4. **RAG 模式** (06)：掌握檢索增強生成的核心思想
5. **多 Agent** (07)：了解 Agent 之間如何協作

## 注意事項

- 這些示例專注於**概念展示**，不包含生產級的錯誤處理
- API 調用會產生費用，建議使用測試 API key
- 本地模型（Ollama）無需 API key，適合離線學習
- 如遇到問題，請檢查 API key 配置和網絡連接

## 下一步

掌握這些基礎示例後，可以探索：

- `/examples` 目錄中的更多高級示例
- `/frameworks` 目錄中各種 Agent 框架的完整實現
- 項目根目錄的 README.md 了解完整項目結構

## 反饋與貢獻

如果您有任何問題或建議，歡迎提交 Issue 或 Pull Request。
