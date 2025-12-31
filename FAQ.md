# ❓ 常見問題解答 (FAQ)

> 收集了用戶最常遇到的問題和解決方案

---

## 📦 環境配置

### Q1: 沒有 GPU 可以運行嗎？

**答：** 可以！大多數示例使用 API 調用（OpenAI、Anthropic 等），不需要本地 GPU。

需要 GPU 的場景：
- 本地運行大模型（如 Llama、Mistral）
- 使用 vLLM 或 Ollama 部署
- 訓練或微調模型

### Q2: Python 版本要求是什麼？

**答：** 推薦 Python 3.9+，最佳體驗使用 Python 3.11。

```bash
# 檢查版本
python --version

# 推薦版本
Python 3.11.x
```

### Q3: 需要安裝所有依賴嗎？

**答：** 不需要！每個框架目錄都有獨立的 `requirements.txt`。

```bash
# 只安裝特定框架的依賴
cd 16.OpenAI\ Swarm
pip install -r requirements.txt
```

### Q4: 遇到 ImportError 怎麼辦？

**答：** 這通常表示缺少依賴：

```bash
# 1. 確保在正確的虛擬環境中
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# 2. 安裝缺失的包
pip install <package_name>

# 3. 或安裝框架的所有依賴
pip install -r requirements.txt
```

---

## 🔑 API 配置

### Q5: API Key 不工作怎麼辦？

**答：** 檢查以下幾點：

1. **確認 .env 文件存在**
   ```bash
   ls -la .env
   ```

2. **確認格式正確**
   ```
   OPENAI_API_KEY=sk-xxx...
   # 注意：不要有引號！
   ```

3. **確認 API Key 有效**
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

4. **確認餘額充足**
   - OpenAI: https://platform.openai.com/account/billing
   - Anthropic: https://console.anthropic.com/settings/billing

### Q6: API 調用成本高嗎？

**答：** 取決於使用量，但示例通常很便宜：

| 模型 | 預估成本/次 |
|------|------------|
| GPT-3.5-Turbo | $0.001-0.005 |
| GPT-4 | $0.01-0.05 |
| Claude 3 Haiku | $0.001-0.003 |
| Claude 3.5 Sonnet | $0.01-0.03 |

**省錢技巧：**
- 開發時使用 GPT-3.5 或 Haiku
- 設置 `max_tokens` 限制
- 使用本地模型（Ollama）

### Q7: 支持哪些 LLM 提供商？

**答：** 項目支持主流提供商：

| 提供商 | 環境變量 | 說明 |
|--------|----------|------|
| OpenAI | `OPENAI_API_KEY` | GPT-4, GPT-3.5 |
| Anthropic | `ANTHROPIC_API_KEY` | Claude 3.x |
| Google | `GOOGLE_API_KEY` | Gemini |
| Groq | `GROQ_API_KEY` | 快速推理 |
| Azure OpenAI | `AZURE_OPENAI_*` | 企業版 |

---

## 🛠️ 運行問題

### Q8: 示例運行報錯怎麼辦？

**答：** 常見排查步驟：

1. **檢查錯誤類型**
   - `ImportError` → 安裝依賴
   - `AuthenticationError` → 檢查 API Key
   - `RateLimitError` → 等待或降低頻率
   - `TimeoutError` → 網絡問題

2. **查看完整錯誤信息**
   ```bash
   python example.py 2>&1 | tee error.log
   ```

3. **嘗試最小示例**
   ```python
   from openai import OpenAI
   client = OpenAI()
   response = client.chat.completions.create(
       model="gpt-3.5-turbo",
       messages=[{"role": "user", "content": "Hello!"}]
   )
   print(response.choices[0].message.content)
   ```

### Q9: 網絡連接超時怎麼辦？

**答：**
1. 檢查網絡連接
2. 嘗試使用代理：
   ```bash
   export HTTPS_PROXY=http://127.0.0.1:7890
   ```
3. 增加超時時間（在代碼中設置）

### Q10: 在中國大陸無法訪問 API？

**答：** 可以考慮：
1. 使用代理服務
2. 使用 Azure OpenAI（有中國區域）
3. 使用國產 LLM（通義千問、文心一言、智譜）
4. 使用本地模型（Ollama + Llama）

---

## 🎯 框架選擇

### Q11: 初學者應該從哪個框架開始？

**答：** 推薦順序：

1. **OpenAI Swarm**（最簡單）
   - 代碼量少，概念清晰
   - 適合理解 Agent 基礎

2. **CrewAI**（中等難度）
   - 角色扮演模式直觀
   - 文檔完善

3. **LangChain**（功能全面）
   - 生態豐富
   - 學習資源多

### Q12: 企業項目應該用什麼框架？

**答：** 取決於需求：

| 需求 | 推薦框架 |
|------|----------|
| Microsoft 生態 | Semantic Kernel |
| RAG 系統 | Haystack, LlamaIndex |
| 低代碼 | Dify, LangFlow |
| 多 Agent | AutoGen, Magentic-One |

### Q13: 各框架的學習曲線如何？

**答：**

```
簡單 ─────────────────────────────────── 困難

OpenAI Swarm → CrewAI → LangChain → LangGraph → AutoGen → Haystack
     ⭐           ⭐⭐       ⭐⭐⭐        ⭐⭐⭐⭐      ⭐⭐⭐⭐      ⭐⭐⭐⭐⭐
```

---

## 📈 性能優化

### Q14: 如何降低 API 調用延遲？

**答：**
1. 使用 streaming 模式
2. 減少 token 數量
3. 使用更快的模型（GPT-3.5, Haiku）
4. 使用 Groq（快速推理）
5. 本地部署（vLLM + GPU）

### Q15: 如何處理大量請求？

**答：**
1. 實現重試機制（指數退避）
2. 使用批量處理
3. 設置速率限制
4. 使用多個 API Key 輪換

---

## 🔧 開發問題

### Q16: 如何調試 Agent？

**答：**
1. 啟用詳細日誌
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. 使用 LangSmith 或 Langfuse 追蹤

3. 打印中間狀態
   ```python
   print(f"State: {agent.state}")
   ```

### Q17: 如何貢獻代碼？

**答：** 參考 [CONTRIBUTING.md](CONTRIBUTING.md)

1. Fork 項目
2. 創建分支
3. 提交 PR
4. 等待審核

---

## 🆘 獲取幫助

### 還有問題？

1. **搜索現有 Issue**
   - [GitHub Issues](https://github.com/your-repo/issues)

2. **查看官方文檔**
   - [LangChain Docs](https://python.langchain.com/)
   - [OpenAI Docs](https://platform.openai.com/docs)
   - [Anthropic Docs](https://docs.anthropic.com/)

3. **社區支持**
   - Discord 社群
   - Stack Overflow

4. **提交新 Issue**
   - 描述問題
   - 附上錯誤信息
   - 提供復現步驟

---

*最後更新：2025-12-31*
