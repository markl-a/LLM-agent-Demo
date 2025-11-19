# CrewAI - 角色扮演 AI Agent 協作框架

<div align="center">

![CrewAI](https://img.shields.io/badge/CrewAI-v0.28+-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge)
![Examples](https://img.shields.io/badge/Examples-20-orange?style=for-the-badge)

**讓 AI Agents 像真實團隊一樣協作**

</div>

---

## 📖 目錄

- [什麼是 CrewAI？](#什麼是-crewai)
- [為什麼選擇 CrewAI？](#為什麼選擇-crewai)
- [核心概念](#核心概念)
- [快速開始](#快速開始)
- [示例索引](#示例索引)
- [實戰應用](#實戰應用)
- [最佳實踐](#最佳實踐)
- [常見問題](#常見問題)
- [參考資源](#參考資源)

---

## 什麼是 CrewAI？

CrewAI 是一個**革命性的 AI Agent 協作框架**，它讓你可以像組建真實團隊一樣組建 AI 團隊。

### 核心特點

🎭 **角色扮演**
- 每個 Agent 都有獨特的角色、目標和背景故事
- 就像真實的團隊成員一樣，每個 Agent 都有自己的專長

👥 **團隊協作**
- 多個 Agents 協同工作，完成複雜任務
- 支持任務委託、協商和共識機制

🔄 **靈活流程**
- Sequential Process: 順序執行，適合流水線式工作
- Hierarchical Process: 層級管理，經理-員工模式

🛠️ **豐富工具**
- 內建大量實用工具
- 輕鬆創建自定義工具
- 與 LangChain 工具生態完全兼容

📝 **記憶系統**
- 短期記憶：任務執行過程中的上下文
- 長期記憶：持久化的知識和經驗
- 實體記憶：關於特定實體的信息

---

## 為什麼選擇 CrewAI？

### CrewAI vs 其他框架

| 特性 | CrewAI | AutoGen | LangGraph |
|------|--------|---------|-----------|
| **角色扮演** | ✅ 原生支持 | ⚠️ 有限 | ❌ 需自己實現 |
| **團隊協作** | ✅ 內建 | ✅ 支持 | ⚠️ 需配置 |
| **易用性** | ✅ 非常簡單 | ⚠️ 中等 | ⚠️ 較複雜 |
| **流程控制** | ✅ 2種內建 | ✅ 靈活 | ✅ 非常靈活 |
| **工具集成** | ✅ 豐富 | ✅ 支持 | ✅ 支持 |
| **記憶管理** | ✅ 3種記憶 | ⚠️ 基礎 | ⚠️ 需自己實現 |

### 適用場景

✅ **內容創作** - 研究、寫作、編輯團隊協作
✅ **市場分析** - 數據收集、分析、報告生成
✅ **軟體開發** - 需求分析、編碼、測試
✅ **客戶服務** - 諮詢、支持、反饋處理
✅ **項目管理** - 規劃、執行、監控
✅ **研究助手** - 文獻調研、數據分析、報告撰寫

---

## 核心概念

### 1. Agent（智能體）

Agent 是團隊的核心成員，每個 Agent 都有：

```python
from crewai import Agent

researcher = Agent(
    role="高級研究員",  # 角色定位
    goal="發現並分析最新技術趨勢",  # 目標
    backstory="""你是一位經驗豐富的研究員，
    擅長從各種來源收集和分析信息...""",  # 背景故事
    verbose=True,  # 詳細輸出
    allow_delegation=False  # 是否允許委託任務
)
```

**關鍵屬性：**
- **role**: 定義 Agent 的專業身份
- **goal**: Agent 要達成的目標
- **backstory**: 影響 Agent 行為的背景故事
- **tools**: Agent 可以使用的工具列表
- **llm**: 使用的語言模型（可選）

### 2. Task（任務）

Task 定義了要完成的具體工作：

```python
from crewai import Task

research_task = Task(
    description="""對 {topic} 進行深入研究。
    你的研究應該包括:
    1. 定義和基本概念
    2. 當前的主要趨勢
    3. 實際應用場景""",

    expected_output="""一份結構化的研究報告，
    包含概述、主要發現和具體應用""",

    agent=researcher  # 負責的 Agent
)
```

**關鍵屬性：**
- **description**: 任務的詳細描述（可使用變量）
- **expected_output**: 明確的輸出要求
- **agent**: 執行任務的 Agent
- **context**: 依賴的其他任務（可選）

### 3. Crew（團隊）

Crew 將 Agents 和 Tasks 組織在一起：

```python
from crewai import Crew, Process

crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, write_task, edit_task],
    process=Process.sequential,  # 執行流程
    verbose=True
)

# 啟動團隊工作
result = crew.kickoff(inputs={"topic": "AI Agents"})
```

**執行流程：**
- **Sequential**: 任務按順序執行
- **Hierarchical**: 有經理 Agent 分配任務

---

## 快速開始

### 安裝

```bash
# 安裝 CrewAI
pip install crewai crewai-tools

# 安裝額外依賴
pip install openai python-dotenv
```

### 第一個示例

```python
from crewai import Agent, Task, Crew, Process
import os

# 設置 API Key
os.environ["OPENAI_API_KEY"] = "your-api-key"

# 1. 創建 Agent
researcher = Agent(
    role="研究員",
    goal="收集關於 {topic} 的信息",
    backstory="你是一位專業的研究員",
    verbose=True
)

# 2. 創建 Task
task = Task(
    description="研究 {topic} 的最新動態",
    expected_output="一份簡短的研究報告",
    agent=researcher
)

# 3. 組建 Crew
crew = Crew(
    agents=[researcher],
    tasks=[task],
    process=Process.sequential
)

# 4. 執行
result = crew.kickoff(inputs={"topic": "AI Agents"})
print(result)
```

### 5 分鐘教程

1. **查看示例**: `01_快速開始.py`
2. **理解角色**: `02_角色定義.py`
3. **設計任務**: `03_任務設計.py`
4. **組建團隊**: `04_團隊組建.py`
5. **使用工具**: `05_工具使用.py`

---

## 示例索引

### 📚 基礎入門 (1-5)

| 示例 | 說明 | 難度 | 重點概念 |
|-----|------|------|---------|
| [01_快速開始.py](01_快速開始.py) | 創建第一個 Agent 和 Task | ⭐ | Agent, Task, Crew |
| [02_角色定義.py](02_角色定義.py) | 設計豐富的 Agent 角色 | ⭐ | Role, Goal, Backstory |
| [03_任務設計.py](03_任務設計.py) | 設計複雜的多步驟任務 | ⭐⭐ | Task, Context, Output |
| [04_團隊組建.py](04_團隊組建.py) | 多 Agent 協作團隊 | ⭐⭐ | Crew, Process |
| [05_工具使用.py](05_工具使用.py) | 為 Agent 配置工具 | ⭐⭐ | Tools, Integration |

### 🔧 核心功能 (6-10)

| 示例 | 說明 | 難度 | 重點概念 |
|-----|------|------|---------|
| [06_順序流程.py](06_順序流程.py) | Sequential Process 任務流 | ⭐⭐ | Sequential |
| [07_層級流程.py](07_層級流程.py) | Hierarchical Process 管理模式 | ⭐⭐⭐ | Hierarchical, Manager |
| [08_記憶管理.py](08_記憶管理.py) | 短期、長期、實體記憶 | ⭐⭐⭐ | Memory Systems |
| [09_協作模式.py](09_協作模式.py) | Agent 間的協作策略 | ⭐⭐⭐ | Delegation, Collaboration |
| [10_結果處理.py](10_結果處理.py) | 格式化和驗證輸出 | ⭐⭐ | Output Formatting |

### 🚀 進階應用 (11-15)

| 示例 | 說明 | 難度 | 重點概念 |
|-----|------|------|---------|
| [11_自定義工具.py](11_自定義工具.py) | 創建專用工具 | ⭐⭐⭐ | Custom Tools |
| [12_異步執行.py](12_異步執行.py) | 並行任務處理 | ⭐⭐⭐⭐ | Async, Parallel |
| [13_錯誤處理.py](13_錯誤處理.py) | 異常處理和重試 | ⭐⭐⭐ | Error Handling |
| [14_性能優化.py](14_性能優化.py) | 提高執行效率 | ⭐⭐⭐⭐ | Optimization |
| [15_監控日誌.py](15_監控日誌.py) | 執行追蹤和調試 | ⭐⭐⭐ | Logging, Monitoring |

### 💼 實戰場景 (16-20)

| 示例 | 說明 | 難度 | 應用領域 |
|-----|------|------|---------|
| [16_內容創作團隊.py](16_內容創作團隊.py) | 研究-寫作-編輯流水線 | ⭐⭐⭐⭐ | 內容營銷 |
| [17_市場分析團隊.py](17_市場分析團隊.py) | 數據收集-分析-報告 | ⭐⭐⭐⭐ | 商業分析 |
| [18_軟體開發團隊.py](18_軟體開發團隊.py) | 需求-編碼-測試工作流 | ⭐⭐⭐⭐⭐ | 軟體工程 |
| [19_客戶服務團隊.py](19_客戶服務團隊.py) | 諮詢-支持-反饋系統 | ⭐⭐⭐⭐ | 客戶服務 |
| [20_最佳實踐.py](20_最佳實踐.py) | 生產級部署和優化 | ⭐⭐⭐⭐⭐ | 企業應用 |

---

## 實戰應用

### 內容創作團隊

```python
# 創建專業的內容創作團隊
researcher = Agent(role="研究員", goal="收集信息")
writer = Agent(role="作家", goal="創作內容")
editor = Agent(role="編輯", goal="審核潤色")

crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, write_task, edit_task],
    process=Process.sequential
)
```

**適用場景:**
- 博客文章生成
- 技術文檔撰寫
- 營銷內容創作
- 社交媒體內容

### 市場分析團隊

```python
# 創建市場分析團隊
data_collector = Agent(role="數據收集專家")
analyst = Agent(role="數據分析師")
reporter = Agent(role="報告撰寫專家")

crew = Crew(
    agents=[data_collector, analyst, reporter],
    tasks=[collect_task, analyze_task, report_task]
)
```

**適用場景:**
- 市場調研
- 競爭分析
- 趨勢預測
- 商業報告

---

## 最佳實踐

### 1. Agent 設計

✅ **DO（應該做）:**
- 給每個 Agent 明確的角色定位
- 撰寫詳細的背景故事
- 確保目標清晰可衡量
- 為專業任務分配專業 Agent

❌ **DON'T（不要做）:**
- 創建過於寬泛的 Agent
- 忽略背景故事的重要性
- 讓一個 Agent 承擔過多職責
- 使用模糊的角色描述

### 2. 任務設計

✅ **DO（應該做）:**
- 提供清晰的任務描述
- 明確期望的輸出格式
- 使用變量增加靈活性
- 設置合理的任務依賴

❌ **DON'T（不要做）:**
- 任務描述過於簡單
- 期望輸出模糊不清
- 創建循環依賴
- 忽略任務的順序關係

### 3. 團隊協作

✅ **DO（應該做）:**
- 選擇合適的執行流程
- 合理配置 Agent 權限
- 使用記憶增強協作
- 監控團隊執行過程

❌ **DON'T（不要做）:**
- 過度使用 delegation
- 忽略流程選擇
- 團隊規模過大
- 缺少監控和日誌

### 4. 性能優化

✅ **DO（應該做）:**
- 合理使用緩存
- 並行執行獨立任務
- 選擇合適的 LLM
- 控制輸出長度

❌ **DON'T（不要做）:**
- 過度依賴昂貴的模型
- 忽略並行優化機會
- 產生過長的輸出
- 缺少錯誤處理

---

## 常見問題

### Q: CrewAI 和 AutoGen 有什麼區別？

**A**: 主要區別：
- **CrewAI**: 專注於角色扮演和團隊協作，API 更簡潔
- **AutoGen**: 更注重對話和交互，配置更靈活
- 選擇建議：需要簡單易用選 CrewAI，需要高度定制選 AutoGen

### Q: 如何選擇 Sequential 還是 Hierarchical？

**A**: 選擇指南：
- **Sequential**: 任務順序明確，流水線式工作
- **Hierarchical**: 需要動態分配，有複雜決策邏輯
- 大多數情況下 Sequential 就足夠了

### Q: CrewAI 支持哪些 LLM？

**A**: CrewAI 通過 LangChain 支持：
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini)
- 本地模型 (通過 Ollama)
- 其他 LangChain 支持的模型

### Q: 如何降低 API 成本？

**A**: 成本優化建議：
1. 對簡單任務使用 GPT-3.5
2. 啟用緩存減少重複調用
3. 控制輸出長度
4. 使用本地模型處理非關鍵任務
5. 合理設置 max_iter 限制

### Q: CrewAI 適合生產環境嗎？

**A**: 是的，但需要注意：
- ✅ 框架穩定，有活躍社區
- ✅ 支持錯誤處理和重試
- ⚠️ 需要良好的監控和日誌
- ⚠️ 建議進行充分測試
- ⚠️ 控制成本和性能

---

## 參考資源

### 官方資源

- 📚 [官方文檔](https://docs.crewai.com/)
- 💻 [GitHub 倉庫](https://github.com/joaomdmoura/crewAI)
- 🎥 [視頻教程](https://www.youtube.com/c/crewai)
- 💬 [Discord 社區](https://discord.gg/crewai)

### 學習資源

- [CrewAI 快速入門指南](https://docs.crewai.com/getting-started)
- [Agent 設計最佳實踐](https://docs.crewai.com/best-practices)
- [工具使用文檔](https://docs.crewai.com/tools)
- [示例項目集合](https://github.com/joaomdmoura/crewAI-examples)

### 相關框架

- [LangChain](https://python.langchain.com/) - CrewAI 的基礎
- [AutoGen](https://github.com/microsoft/autogen) - 微軟的多 Agent 框架
- [LangGraph](https://github.com/langchain-ai/langgraph) - LangChain 的工作流框架

---

## 技術支持

### 遇到問題？

1. **查看文檔**: 大多數問題都能在官方文檔找到答案
2. **搜索 Issues**: GitHub Issues 中可能已有解決方案
3. **社區求助**: Discord 社區響應很快
4. **提交 Issue**: 如果是 bug，請在 GitHub 提交

### 貢獻

歡迎為本教程貢獻：
- 🐛 報告問題
- 💡 提出建議
- 📝 改進文檔
- 🌟 添加示例

---

<div align="center">

**🚀 開始你的 CrewAI 之旅！**

選擇一個示例開始學習 | [返回主項目](../README.md)

---

Made with ❤️ by LLM Agent Demo Team

</div>
