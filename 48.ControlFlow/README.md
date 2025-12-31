# ControlFlow - Agentic AI 工作流框架

## 框架介紹

ControlFlow 是一個強大的 Python 框架,專門用於構建 Agentic AI 工作流。它提供了一種結構化的方法來編排 AI Agent,具有清晰的控制流模式,使複雜的 AI 工作流程變得簡單易管理。

ControlFlow 建立在 Prefect 之上,結合了現代工作流編排的最佳實踐,專為 AI Agent 應用而設計。它允許開發者定義任務、管理狀態、處理錯誤,並創建複雜的條件邏輯,同時保持代碼的可讀性和可維護性。

## 核心特性

### 🔄 工作流編排
- **聲明式定義**: 使用簡潔的 Python 語法定義工作流
- **視覺化流程**: 自動生成工作流程圖
- **並行執行**: 支持任務並行處理以提高效率
- **依賴管理**: 自動處理任務之間的依賴關係

### 📋 任務管理
- **靈活的任務定義**: 支持多種任務類型和配置
- **任務優先級**: 設定任務執行優先順序
- **重試機制**: 自動重試失敗的任務
- **超時控制**: 為任務設定執行時間限制

### 🎮 流程控制
- **順序執行**: 按順序執行任務鏈
- **並行處理**: 同時執行多個獨立任務
- **條件路由**: 根據條件選擇不同的執行路徑
- **循環迭代**: 支持循環和迭代模式

### 🌲 條件分支
- **動態決策**: 基於運行時數據做出決策
- **多路分支**: 支持複雜的分支邏輯
- **智能路由**: AI Agent 自主選擇執行路徑
- **狀態驅動**: 根據工作流狀態調整行為

### 🤖 Agent 整合
- **多 Agent 支持**: 在同一工作流中使用多個 Agent
- **Agent 通信**: Agent 之間的數據傳遞和協作
- **工具綁定**: 為 Agent 配置專屬工具
- **上下文管理**: 維護 Agent 的對話上下文

### 🛡️ 可靠性保障
- **錯誤恢復**: 自動處理和恢復錯誤
- **狀態持久化**: 保存工作流狀態以便恢復
- **監控告警**: 實時監控工作流執行狀態
- **日誌記錄**: 詳細的執行日誌

## 安裝指南

### 基本安裝

```bash
pip install controlflow
```

### 完整安裝(包含所有依賴)

```bash
pip install -r requirements.txt
```

### 從源碼安裝

```bash
git clone https://github.com/PrefectHQ/ControlFlow.git
cd ControlFlow
pip install -e .
```

## 環境配置

創建 `.env` 文件並配置必要的環境變量:

```bash
# OpenAI API 配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1

# Prefect 配置(可選)
PREFECT_API_URL=http://localhost:4200/api
PREFECT_LOGGING_LEVEL=INFO

# ControlFlow 配置
CONTROLFLOW_LOG_LEVEL=DEBUG
CONTROLFLOW_DEFAULT_MODEL=gpt-4
```

## 快速開始

### 基本示例

```python
import controlflow as cf
from controlflow import Agent, Task, Flow

# 創建 Agent
agent = Agent(
    name="助手",
    description="一個能幫助用戶解決問題的 AI 助手",
    model="gpt-4"
)

# 定義任務
task = Task(
    objective="分析用戶輸入並提供建議",
    instructions="理解用戶需求,提供專業的建議和解決方案",
    agent=agent
)

# 創建工作流
@cf.flow
def my_workflow(user_input: str):
    result = task.run(context={"input": user_input})
    return result

# 執行工作流
if __name__ == "__main__":
    result = my_workflow("如何提高工作效率?")
    print(result)
```

### 多任務工作流

```python
import controlflow as cf

@cf.flow
def research_workflow(topic: str):
    # 任務 1: 收集資料
    research_task = cf.Task(
        objective=f"研究主題: {topic}",
        instructions="收集相關資料和信息"
    )

    # 任務 2: 分析資料
    analysis_task = cf.Task(
        objective="分析研究結果",
        instructions="整理和分析收集的資料",
        depends_on=[research_task]
    )

    # 任務 3: 生成報告
    report_task = cf.Task(
        objective="生成研究報告",
        instructions="基於分析結果生成完整報告",
        depends_on=[analysis_task]
    )

    # 執行工作流
    result = report_task.run()
    return result

# 運行工作流
report = research_workflow("人工智能在醫療領域的應用")
```

### 條件分支工作流

```python
import controlflow as cf

@cf.flow
def conditional_workflow(task_type: str):
    # 決策任務
    decision_task = cf.Task(
        objective="判斷任務類型",
        result_type=str
    )

    decision = decision_task.run(context={"type": task_type})

    # 根據決策執行不同任務
    if decision == "urgent":
        urgent_task = cf.Task(objective="處理緊急任務")
        return urgent_task.run()
    else:
        normal_task = cf.Task(objective="處理普通任務")
        return normal_task.run()

result = conditional_workflow("urgent")
```

## 使用場景

### 1. 複雜工作流編排

ControlFlow 特別適合需要多個步驟、多個 Agent 協作的複雜業務流程:

- **客戶服務自動化**: 多輪對話、問題分類、自動回覆
- **內容生成管道**: 研究 → 撰寫 → 審核 → 發布
- **數據處理流程**: 收集 → 清洗 → 分析 → 可視化

### 2. 自動化流程

將重複性工作自動化,提高效率:

- **報告生成**: 自動收集數據、分析並生成報告
- **代碼審查**: 自動檢查代碼質量、提出改進建議
- **郵件處理**: 分類、摘要、自動回覆

### 3. Agent 編排

協調多個專業 Agent 完成複雜任務:

- **研究助手**: 協調搜索、分析、總結等多個 Agent
- **創意工作室**: 協調撰寫、設計、審核等 Agent
- **技術支持**: 協調診斷、解決、文檔等 Agent

### 4. 決策支持系統

構建智能決策輔助系統:

- **投資分析**: 多維度分析、風險評估、建議生成
- **招聘流程**: 簡歷篩選、面試安排、評估報告
- **項目管理**: 任務分配、進度跟蹤、風險預警

## 核心概念

### Flow (工作流)

Flow 是工作流的容器,定義了整個執行過程:

```python
@cf.flow
def my_flow():
    # 工作流邏輯
    pass
```

### Task (任務)

Task 是工作流中的基本執行單元:

```python
task = cf.Task(
    objective="任務目標",
    instructions="執行指令",
    agent=my_agent
)
```

### Agent (代理)

Agent 是執行任務的 AI 實體:

```python
agent = cf.Agent(
    name="專家",
    model="gpt-4",
    instructions="你是一個專業的助手"
)
```

### Tools (工具)

Tools 為 Agent 提供額外能力:

```python
@cf.tool
def search_web(query: str) -> str:
    # 工具實現
    return result
```

## 示例文件說明

本目錄包含 10 個詳細的示例文件,涵蓋 ControlFlow 的各個方面:

1. **01_快速開始.py** - 基本設置和簡單示例
2. **02_任務定義.py** - 任務定義和配置
3. **03_流程控制.py** - 順序和並行執行模式
4. **04_條件分支.py** - 條件邏輯和路由
5. **05_Agent創建.py** - Agent 配置和使用
6. **06_工具整合.py** - 工具開發和整合
7. **07_狀態管理.py** - 工作流狀態管理
8. **08_錯誤處理.py** - 錯誤處理和恢復
9. **09_子流程.py** - 子流程和組合模式
10. **10_生產部署.py** - 生產環境部署

## 最佳實踐

### 1. 任務設計
- 保持任務單一職責
- 明確定義任務目標和輸出
- 合理設置任務依賴關係

### 2. Agent 配置
- 為不同任務使用專門的 Agent
- 提供清晰的 Agent 指令
- 合理選擇模型(GPT-4 vs GPT-3.5)

### 3. 錯誤處理
- 為關鍵任務添加重試邏輯
- 實現優雅的錯誤降級
- 記錄詳細的錯誤信息

### 4. 性能優化
- 使用並行執行提高效率
- 緩存重複計算結果
- 合理設置超時時間

## 資源鏈接

- **官方文檔**: https://controlflow.ai/docs
- **GitHub 倉庫**: https://github.com/PrefectHQ/ControlFlow
- **示例集合**: https://controlflow.ai/examples
- **社區論壇**: https://discourse.prefect.io/c/controlflow
- **API 參考**: https://controlflow.ai/api-reference

## 貢獻指南

歡迎貢獻代碼、文檔或示例!請查看 CONTRIBUTING.md 了解詳情。

## 授權協議

本示例代碼採用 MIT 協議,ControlFlow 框架遵循其原項目協議。

## 技術支持

如有問題或建議,請:
- 提交 GitHub Issue
- 加入社區討論
- 查看官方文檔

---

**開始使用 ControlFlow,構建強大的 Agentic AI 工作流!**
