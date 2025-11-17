# 專門用於 RPA 的開源 LLM 專案

## 簡介

近年來，大型語言模型（LLM）在自然語言處理領域取得了顯著的進展，並開始被應用於各個領域，包括機器人流程自動化（RPA）。LLM 可以幫助 RPA 系統更好地理解人類語言、處理非結構化數據，並自動生成工作流程，從而提高 RPA 的效率和靈活性。

LLM 的整合也標誌著 RPA 發展的重大轉變，從傳統的基於規則的 RPA 轉變為更智能、更具適應性的代理流程自動化（APA）。APA 利用 LLM 的能力，使機器人能夠理解自然語言指令、從非結構化數據中提取資訊，並根據情況變化調整工作流程。

本文將介紹一些專門用於 RPA 的開源 LLM 專案，並探討 LLM 如何賦能 RPA。

## LLM 如何賦能 RPA？

傳統的 RPA 系統通常依賴於預先定義的規則和工作流程，難以處理複雜或非結構化的數據。而 LLM 的出現為 RPA 帶來了新的可能性：

- **智能數據提取**: LLM 可以從非結構化數據（如文檔、郵件、網頁）中提取關鍵信息，並將其轉換為結構化數據，供 RPA 系統使用。例如，LLM 可以用於從發票中提取關鍵數據，例如發票號碼、日期和總金額。

- **自然語言理解**: LLM 可以理解人類語言，並將其轉換為 RPA 系統可以理解的指令，從而實現更自然的交互方式。例如，LLM 可以用於理解客戶服務查詢，並生成相應的回覆。

- **自動工作流程生成**: LLM 可以根據人類的指令自動生成 RPA 工作流程，從而減少人工編程的工作量。

- **動態決策**: LLM 可以根據實時情況做出決策，並調整 RPA 工作流程，從而提高 RPA 系統的靈活性。

- **持續學習和適應**: LLM 可以不斷學習新的數據和知識，並根據新的情況調整 RPA 工作流程，從而提高 RPA 系統的效率和準確性。

## RPA 和 LLM 社群和論壇

如果您對 LLM 在 RPA 中的應用感興趣，可以參考以下社群和論壇：

- **Reddit 的 r/rpa**: 這是 Reddit 上一個專門討論 RPA 的子版塊，其中也包含關於 LLM 和 RPA 結合的討論。
- **UiPath 社區論壇**: UiPath 作為領先的 RPA 平台，其社區論壇也提供了關於 LLM 和 RPA 結合的討論和資源。
- **Stack Overflow**: Stack Overflow 是一個程式設計師常用的問答網站，其中也包含關於 RPA 和 LLM 的問題和解答。

## 專門用於 RPA 的開源 LLM 專案

### 綜合比較表

| 專案名稱 | 星標數 | 是否使用 LLM | 主要語言 | 適用場景 | 學習曲線 |
|---------|-------|-------------|---------|---------|---------|
| Skyvern-AI/skyvern | ⭐ 高 | ✅ 是 | Python | 複雜網頁自動化 | 中等 |
| OpenAdaptAI/OpenAdapt | ⭐ 中 | ✅ 是 | Python | 通用桌面自動化 | 中等 |
| AmitXShukla/RPA | ⭐ 中 | ✅ 是 | Python/Julia | 業務流程自動化 | 低 |
| tebelorg/RPA-Python | ⭐ 高 | ⚠️ 部分 | Python | 快速原型開發 | 低 |
| ProAgent | ⭐ 中 | ✅ 是 | Python | Agent 流程自動化 | 高 |
| AutoGPT-RPA | ⭐ 低 | ✅ 是 | Python | 自主任務執行 | 高 |

### 詳細專案介紹

#### 1. Skyvern-AI/skyvern 🌟 推薦

**GitHub**: [Skyvern-AI/skyvern](https://github.com/Skyvern-AI/skyvern)

**核心特色**：
- 使用 LLM 和計算機視覺自動化瀏覽器任務
- 無需預先定義的選擇器（selectors），適應性強
- 支援複雜的多步驟工作流程

**主要功能**：
- 🌐 智能網頁導航與互動
- 📊 結構化數據提取
- 🔄 循環操作與條件邏輯
- 📄 文件上傳與解析
- 📧 自動化郵件處理
- 🔐 表單自動填充

**技術架構**：
```
用戶指令 → LLM 理解 → 視覺識別 → 動作執行 → 結果驗證
```

**適用場景**：
- 電商數據採集
- 競品監控
- 表單批量提交
- 跨平台數據整合

**安裝與使用**：
```bash
pip install skyvern
# 詳細使用請參考 tutorial-part2-llm-integration.md
```

---

#### 2. OpenAdaptAI/OpenAdapt 🔥 新興專案

**GitHub**: [OpenAdaptAI/OpenAdapt](https://github.com/OpenAdaptAI/OpenAdapt)

**核心特色**：
- 記錄並重放人類操作行為
- 使用 LLM 理解操作意圖
- 支援桌面應用程式自動化

**主要功能**：
- 🎥 操作錄製與重放
- 🧠 智能化操作理解
- 🖥️ 跨平台桌面自動化
- 🔍 視覺元素識別
- 📝 自然語言驅動的自動化

**技術架構**：
```
錄製階段: 用戶操作 → 截圖 + 事件 → 存儲
重放階段: LLM 分析 → 識別元素 → 執行操作
```

**適用場景**：
- 重複性桌面操作
- 跨應用程式工作流
- 操作文檔化
- 自動化培訓

**安裝與使用**：
```bash
pip install openadapt
# 詳細使用請參考 tutorial-part1-basic-rpa.md
```

---

#### 3. AmitXShukla/RPA 🎯 實用工具集

**GitHub**: [AmitXShukla/RPA](https://github.com/AmitXShukla/RPA)

**核心特色**：
- Python 和 Julia 雙語言支援
- 整合 ChatGPT 等 LLM
- 豐富的實用工具集

**主要功能**：
- 📁 文件批量處理（分割、合併、轉換）
- 📸 網頁截圖自動化
- 🔤 OCR 文字識別
- 🎫 QR Code 生成與讀取
- 🧪 測試數據生成
- 🤖 推薦系統構建
- ⏱️ ETA 預測

**技術架構**：
- 模組化設計，可按需使用
- LLM 用於智能決策與數據分析
- 支援與現有系統整合

**適用場景**：
- 文檔管理自動化
- 業務數據處理
- 測試環境搭建
- 智能推薦系統

---

#### 4. tebelorg/RPA-Python 📦 經典框架

**GitHub**: [tebelorg/RPA-Python](https://github.com/tebelorg/RPA-Python)

**核心特色**：
- 簡單易用的 Python RPA 框架
- 支援多種自動化類型
- 活躍的社群支援

**主要功能**：
- 🌐 網頁自動化（支援 Chrome、Firefox）
- 👁️ 視覺自動化（圖像識別）
- 📖 OCR 文字識別
- ⌨️ 鍵盤模擬
- 🖱️ 滑鼠控制
- 📋 剪貼簿操作

**技術架構**：
```python
# 簡潔的 API 設計
rpa.init()
rpa.url('https://example.com')
rpa.type('//*[@id="search"]', 'RPA')
rpa.click('Search')
rpa.close()
```

**適用場景**：
- 快速原型開發
- 簡單重複任務
- 網頁數據抓取
- UI 測試自動化

---

#### 5. OpenBMB/ProAgent 🚀 進階 Agent 系統

**GitHub**: [OpenBMB/ProAgent](https://github.com/OpenBMB/ProAgent)

**核心特色**：
- 基於 LLM 的智能 Agent 系統
- 支援複雜的多步驟工作流
- 自主規劃與執行能力

**主要功能**：
- 🎯 任務自動分解
- 🔄 動態工作流生成
- 🧩 多工具協同
- 📊 執行監控與調試
- 🔧 可擴展的 Plugin 系統

**技術架構**：
```
任務輸入 → LLM 規劃 → 工具選擇 → 執行引擎 → 結果整合
```

**適用場景**：
- 複雜業務流程自動化
- 需要推理決策的任務
- 多系統整合場景
- 研究與實驗

---

#### 6. 其他值得關注的專案

**AutoGen (Microsoft)** - 多 Agent 協作框架
- 適合建構複雜的 Agent 系統
- 支援 Agent 之間的對話與協作

**LangChain** - LLM 應用開發框架
- 不是專門的 RPA 工具，但可用於構建 LLM 驅動的自動化
- 豐富的工具鏈與整合

**n8n** - 工作流程自動化平台
- 視覺化的工作流編輯器
- 支援整合 LLM API

### 如何選擇合適的工具？

根據你的需求選擇：

| 需求 | 推薦工具 | 原因 |
|------|---------|------|
| 網頁自動化 | Skyvern、RPA-Python | 成熟穩定，社群支援好 |
| 桌面自動化 | OpenAdapt、RPA-Python | 支援跨平台，易於使用 |
| 智能化程度高 | Skyvern、ProAgent | LLM 深度整合 |
| 快速開發 | RPA-Python、AmitXShukla/RPA | API 簡單，上手快 |
| 學習研究 | ProAgent、OpenAdapt | 架構先進，文檔完善 |
| 生產環境 | Skyvern、RPA-Python | 穩定性好，有商業支援 |

詳細對比請參考 [tools-comparison.md](./tools-comparison.md)

## 總結

LLM 的出現為 RPA 帶來了新的發展機遇，可以提高 RPA 系統的效率、靈活性，和智能化程度。相信隨著 LLM 技術的發展和應用，LLM 與 RPA 的結合將會更加緊密，並為各個行業帶來更大的價值。

我們可以更加的探索開源項目和了解更多關於 LLM 在 RPA 中的應用。同時，也需要關注 LLM 在自動化中應用的相關議題，包括：

- **倫理考量**：例如演算法偏差、隱私保護、資料安全等
- **社會影響**：包括就業市場變遷、工作轉型需求等
- **技術挑戰**：如模型解釋性、可靠性和穩定性等
- **實施策略**：需要制定完善的治理框架和最佳實踐指南

建議組織在導入 LLM 強化 RPA 時，應採取循序漸進的方式，並建立完整的評估和監控機制，以確保技術應用既能發揮效益，又能妥善管理相關風險。

## 引用的著作

1. OpenBMB/ProAgent: An LLM-based Agent for the New ... - GitHub, 檢索日期：2月 13, 2025， https://github.com/OpenBMB/ProAgent
2. From Robotic Process Automation to Agentic Process Automation - UiPath Community Forum, 檢索日期：2月 13, 2025， https://forum.uipath.com/t/from-robotic-process-automation-to-agentic-process-automation/779088
3. RPA vs AI agents vs Agentic Process Automation. Whats the future? : r/AI_Agents - Reddit, 檢索日期：2月 13, 2025， https://www.reddit.com/r/AI_Agents/comments/1iftryd/rpa_vs_ai_agents_vs_agentic_process_automation/
4. UiPath® DocPath - Document Understanding, 檢索日期：2月 13, 2025， https://docs.uipath.com/document-understanding/automation-cloud/latest/user-guide/uipath-docpath
5. LLM Powered Robotic Process Automation: Unleashing the Industry Transformation Revolution | Tangentia, 檢索日期：2月 13, 2025， https://www.tangentia.com/llm-powered-robotic-process-automation-unleashing-the-industry-transformation-revolution/
6. Workflow Generation - Enhans, 檢索日期：2月 13, 2025， https://www.enhans.ai/newsroom/workflow-generation
7. Large Language Model (LLM) and RPA to Solve Complex Use Cases - Rannsolve, 檢索日期：2月 13, 2025， https://rannsolve.com/blog/large-language-model-llm-and-rpa-to-solve-complex-use-cases/
8. r/rpa - Reddit, 檢索日期：2月 13, 2025， https://www.reddit.com/r/rpa/
9. Retrieval-augmented generation – Stack Overflow's Industry Guide to AI, 檢索日期：2月 13, 2025， https://stackoverflow.co/teams/resources/ai-industry-guide/key-tools-technologies-terms/rag/
10. Latest Articles on RPA News and Automation Insights | UiPath Blog, 檢索日期：2月 13, 2025， https://www.uipath.com/blog
11. Paper page - FlowMind: Automatic Workflow Generation with LLMs - Hugging Face, 檢索日期：2月 13, 2025， https://huggingface.co/papers/2404.13050
12. AmitXShukla/RPA: AI Bots - Robotic Processing automation ... - GitHub, 檢索日期：2月 13, 2025， https://github.com/AmitXShukla/RPA
13. tebelorg/RPA-Python: Python package for doing RPA - GitHub, 檢索日期：2月 13, 2025， https://github.com/tebelorg/RPA-Python
14. Skyvern-AI/skyvern: Automate browser-based workflows ... - GitHub, 檢索日期：2月 13, 2025， https://github.com/Skyvern-AI/skyvern
15. OpenAdaptAI/OpenAdapt: Open Source Generative ... - GitHub, 檢索日期：2月 13, 2025， https://github.com/OpenAdaptAI/OpenAdapt
16. New Generative AI features in UiPath Document Understanding - cxai.au, 檢索日期：2月 13, 2025， https://cxai.au/new-generative-ai-features-in-uipath-document-understanding/
17. Communications Mining - CommPath LLM vs. Preview LLM - UiPath Documentation, 檢索日期：2月 13, 2025， https://docs.uipath.com/communications-mining/automation-cloud/latest/user-guide/comm-path-llm-vs-review-llm
18. LangGraph and UiPath: streamlining enterprise LLMs | Community blog, 檢索日期：2月 13, 2025， https://www.uipath.com/community-blog/tutorials/langgraph-meets-uipath-simplifying-enterprise-llm
19. AI Agent Studio - Automation Anywhere, 檢索日期：2月 13, 2025， https://www.automationanywhere.com/products/ai-agent-studio
20. Put generative AI to work - Automation Anywhere, 檢索日期：2月 13, 2025， https://www.automationanywhere.com/products/generative-ai-process-models
21. Communications Mining - Prompt-based learning with Transformers - UiPath Documentation, 檢索日期：2月 13, 2025， https://docs.uipath.com/communications-mining/automation-cloud/latest/developer-guide/prompt-based-learning-with-transformers
22. EleutherAI/gpt-neo: An implementation of model parallel GPT-2 and GPT-3-style models using the mesh-tensorflow library. - GitHub, 檢索日期：2月 13, 2025， https://github.com/EleutherAI/gpt-neo
23. Automate Tasks with GPT using RPA Webinar - YouTube, 檢索日期：2月 13, 2025， https://www.youtube.com/watch?v=W0Z3L4Foryo
24. Smartflow: AI-Driven RPA, 檢索日期：2月 13, 2025， https://smartflow-4c5a0a.webflow.io/
25. Paper Review: FlowMind: Automatic Workflow Generation with LLMs - Medium, 檢索日期：2月 13, 2025， https://medium.com/llms-research/paper-review-flowmind-automatic-workflow-generation-with-llms-2cbd5d5c380d
26. The Next Generation of Productivity: Generative Process Automation | by Nick Giometti | Geodesic Capital | Medium, 檢索日期：2月 13, 2025， https://medium.com/geodesic-capital/the-next-generation-of-productivity-generative-process-automation-cbce68870c10
27. How Has RPA Evolved Since AI, LLMs & Agents Went Mainstream? : r/sysadmin - Reddit, 檢索日期：2月 13, 2025， https://www.reddit.com/r/sysadmin/comments/1ilzav3/how_has_rpa_evolved_since_ai_llms_agents_went/
28. Can LLM Replace Stack Overflow? A Study on Robustness and Reliability of Large Language Model Code Generation | Proceedings of the AAAI Conference on Artificial Intelligence, 檢索日期：2月 13, 2025， https://ojs.aaai.org/index.php/AAAI/article/view/30185
29. Going Beyond RPA with LLMs - IKANGAI, 檢索日期：2月 13, 2025， https://www.ikangai.com/going-beyond-rpa-with-llms/
