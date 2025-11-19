# LangGraph - 狀態管理與工作流編排框架

<div align="center">

![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![LangChain](https://img.shields.io/badge/LangChain-Official-orange?style=for-the-badge)

**LangChain 官方的狀態管理和複雜工作流編排框架**

[官方文檔](https://langchain-ai.github.io/langgraph/) | [GitHub](https://github.com/langchain-ai/langgraph) | [示例](./01_狀態圖基礎.py)

</div>

---

## 📚 目錄

- [簡介](#-簡介)
- [核心特點](#-核心特點)
- [核心概念](#-核心概念)
- [快速開始](#-快速開始)
- [完整示例](#-完整示例代碼-20-個)
- [實際應用](#-實際應用場景)
- [最佳實踐](#-最佳實踐)
- [常見問題](#-常見問題)

---

## 🎯 簡介

### 什麼是 LangGraph？

**LangGraph** 是 LangChain 官方開發的狀態管理框架，專門用於構建複雜的、有狀態的 LLM 應用和 Agent 系統。

### 為什麼需要 LangGraph？

傳統的 LangChain Chain 適合線性流程，但對於複雜的 Agent 應用有以下限制：
- ❌ 難以處理循環邏輯
- ❌ 缺乏複雜的條件分支
- ❌ 狀態管理不夠靈活
- ❌ 難以實現人機協作

LangGraph 解決了這些問題：
- ✅ 基於圖的工作流編排
- ✅ 靈活的狀態管理
- ✅ 支持循環和條件邏輯
- ✅ 內建檢查點和持久化
- ✅ 人機協作支持

---

## ⭐ 核心特點

### 1. 狀態圖 (State Graph)

```python
from langgraph.graph import StateGraph

# 定義狀態
class State(TypedDict):
    messages: list
    data: dict

# 創建狀態圖
workflow = StateGraph(State)
```

### 2. 靈活的節點與邊

```python
# 添加節點
workflow.add_node("process", process_function)

# 添加普通邊
workflow.add_edge("start", "process")

# 添加條件邊
workflow.add_conditional_edges(
    "process",
    routing_function,
    {"path1": "node1", "path2": "node2"}
)
```

### 3. 循環與遞歸

```python
# 自循環
workflow.add_edge("node", "node")

# 條件循環
workflow.add_conditional_edges(
    "loop_node",
    should_continue,
    {"continue": "loop_node", "end": END}
)
```

### 4. 檢查點 (Checkpoints)

```python
from langgraph.checkpoint import MemorySaver

# 添加檢查點
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)

# 恢復狀態
app.invoke(state, config={"thread_id": "123"})
```

---

## 🧩 核心概念

### 1. 狀態 (State)

狀態是在節點之間傳遞的數據結構：

```python
from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    # 累積型狀態（使用 operator.add）
    messages: Annotated[list, operator.add]
    
    # 覆蓋型狀態
    current_step: str
    counter: int
```

**狀態類型**:
- **累積型**: 使用 `Annotated[list, operator.add]`，新值會添加到列表
- **覆蓋型**: 直接類型，新值會覆蓋舊值

### 2. 節點 (Nodes)

節點是執行特定操作的函數：

```python
def my_node(state: AgentState) -> AgentState:
    """節點函數"""
    # 處理邏輯
    state["counter"] += 1
    state["messages"].append("New message")
    return state

# 添加到圖
workflow.add_node("my_node", my_node)
```

**節點特點**:
- 接收當前狀態
- 返回更新後的狀態
- 可以是同步或異步函數

### 3. 邊 (Edges)

邊定義節點之間的連接：

**普通邊**:
```python
workflow.add_edge("source", "target")
```

**條件邊**:
```python
def route_function(state):
    if state["condition"]:
        return "path_a"
    return "path_b"

workflow.add_conditional_edges(
    "source",
    route_function,
    {"path_a": "node_a", "path_b": "node_b"}
)
```

### 4. 入口與出口

```python
# 設置入口點
workflow.set_entry_point("start_node")

# 設置出口（結束）
workflow.add_edge("end_node", END)
```

---

## 🚀 快速開始

### 1. 安裝

```bash
pip install langgraph langchain langchain-openai
```

### 2. 配置 API Key

```bash
export OPENAI_API_KEY='your-api-key'
```

### 3. 第一個示例

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END

# 定義狀態
class State(TypedDict):
    count: int

# 定義節點
def increment(state):
    return {"count": state["count"] + 1}

# 創建圖
workflow = StateGraph(State)
workflow.add_node("increment", increment)
workflow.set_entry_point("increment")
workflow.add_edge("increment", END)

# 編譯並運行
app = workflow.compile()
result = app.invoke({"count": 0})
print(result)  # {"count": 1}
```

### 4. 運行示例

```bash
cd "17.LangGraph"
python 01_狀態圖基礎.py
```

---

## 🔥 完整示例代碼 (20 個)

### 基礎入門 (1-5)
1. **[狀態圖基礎](01_狀態圖基礎.py)** - 狀態定義、節點創建、基本工作流
2. **[節點與邊](02_節點與邊.py)** - 普通邊、條件邊、動態路由
3. **[條件路由](03_條件路由.py)** - if-else 邏輯、多條件判斷、動態分支
4. **[循環控制](04_循環控制.py)** - 循環邏輯、退出條件、遞歸處理
5. **[檢查點](05_檢查點.py)** - 狀態保存、斷點續傳、持久化

### 核心功能 (6-10)
6. **[並行執行](06_並行執行.py)** - 並行節點、並發處理、結果合併
7. **[子圖](07_子圖.py)** - 子圖嵌套、模塊化、復用
8. **[工具集成](08_工具集成.py)** - 外部工具、API 調用、工具鏈
9. **[記憶管理](09_記憶管理.py)** - 會話記憶、上下文保持、歷史追蹤
10. **[錯誤處理](10_錯誤處理.py)** - 異常捕獲、重試機制、降級策略

### 進階應用 (11-15)
11. **[人機協作](11_人機協作.py)** - 人工介入、批准流程、交互式決策
12. **[多Agent協作](12_多Agent協作.py)** - Agent 團隊、角色分工、協作模式
13. **[流式輸出](13_流式輸出.py)** - 實時響應、流式處理、增量輸出
14. **[持久化](14_持久化.py)** - 數據庫存儲、狀態恢復、長期運行
15. **[自定義狀態](15_自定義狀態.py)** - 複雜狀態、Reducer、狀態合併

### 實戰場景 (16-20)
16. **[客服機器人](16_客服機器人.py)** - 完整案例、意圖識別、工單系統
17. **[研究助手](17_研究助手.py)** - 文獻搜索、信息提取、報告生成
18. **[代碼審查](18_代碼審查.py)** - 代碼分析、問題檢測、建議生成
19. **[工作流自動化](19_工作流自動化.py)** - 業務流程、審批系統、通知機制
20. **[最佳實踐](20_最佳實踐.py)** - 設計模式、優化技巧、生產部署

> 💡 **提示**: 所有示例都包含完整代碼、詳細註釋和最佳實踐，展示 LangGraph 的強大功能。

---

## 🎨 實際應用場景

### 場景 1: 客服機器人

```python
# 多輪對話 + 意圖識別 + 工具調用
workflow = StateGraph(State)

workflow.add_node("greet", greet_user)
workflow.add_node("identify_intent", identify_intent)
workflow.add_node("handle_query", handle_query)
workflow.add_node("escalate", escalate_to_human)

workflow.add_conditional_edges(
    "identify_intent",
    route_intent,
    {
        "simple": "handle_query",
        "complex": "escalate"
    }
)
```

### 場景 2: 研究助手

```python
# 文獻搜索 + 總結 + 報告生成
workflow.add_node("search", search_papers)
workflow.add_node("filter", filter_relevant)
workflow.add_node("summarize", summarize_papers)
workflow.add_node("generate_report", generate_report)

# 循環過濾直到找到足夠的文獻
workflow.add_conditional_edges(
    "filter",
    check_enough_papers,
    {"continue": "search", "done": "summarize"}
)
```

### 場景 3: 工作流自動化

```python
# 審批流程自動化
workflow.add_node("submit", submit_request)
workflow.add_node("review", auto_review)
workflow.add_node("human_approval", wait_for_approval)
workflow.add_node("execute", execute_action)

workflow.add_conditional_edges(
    "review",
    needs_human_approval,
    {"yes": "human_approval", "no": "execute"}
)
```

---

## 💡 最佳實踐

### 1. 狀態設計

**✅ 好的設計**:
```python
class State(TypedDict):
    # 明確的類型註解
    messages: Annotated[list, operator.add]
    current_user: str
    iteration: int
```

**❌ 避免**:
```python
class State(TypedDict):
    # 太多字段，難以維護
    data1: str
    data2: str
    # ... 20 more fields
```

### 2. 節點職責單一

**✅ 好的設計**:
```python
def analyze_sentiment(state):
    """只負責情感分析"""
    ...

def generate_response(state):
    """只負責生成回應"""
    ...
```

**❌ 避免**:
```python
def do_everything(state):
    """做太多事情"""
    analyze()
    process()
    respond()
    log()
    ...
```

### 3. 合理使用檢查點

```python
# 長時間運行的任務
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)

# 可以隨時恢復
result = app.invoke(
    state,
    config={"thread_id": "session_123"}
)
```

### 4. 錯誤處理

```python
def robust_node(state):
    try:
        result = risky_operation()
        state["result"] = result
    except Exception as e:
        state["error"] = str(e)
        state["status"] = "failed"
    return state
```

---

## ❓ 常見問題

### Q1: LangGraph vs LangChain Chain 的區別？

**A**:
- **Chain**: 線性流程，適合簡單應用
- **LangGraph**: 圖結構，支持循環、條件、並行

### Q2: 何時使用 LangGraph？

**A**: 當你需要：
- 複雜的條件邏輯
- 循環和遞歸
- 狀態持久化
- 人機協作
- 多 Agent 協作

### Q3: 如何調試 LangGraph？

**A**:
```python
# 使用 verbose 模式
app = workflow.compile(debug=True)

# 或使用 LangSmith
from langsmith import traceable

@traceable
def my_node(state):
    ...
```

### Q4: 性能如何優化？

**A**:
1. 使用並行節點處理獨立任務
2. 合理設計狀態，避免過大
3. 使用緩存減少重複計算
4. 考慮使用異步節點

---

## 📚 參考資源

### 官方資源
- [LangGraph 文檔](https://langchain-ai.github.io/langgraph/)
- [GitHub 倉庫](https://github.com/langchain-ai/langgraph)
- [LangChain 文檔](https://python.langchain.com/)

### 學習資源
- [LangGraph 教程](https://python.langchain.com/docs/langgraph)
- [示例集合](https://github.com/langchain-ai/langgraph/tree/main/examples)

### 社區
- [Discord](https://discord.gg/langchain)
- [GitHub Discussions](https://github.com/langchain-ai/langgraph/discussions)

---

## 📄 許可證

LangGraph 採用 MIT 許可證。

**最後更新**: 2025-11-19  
**LangGraph 版本**: 0.2.50+

---

<div align="center">

**開始使用 LangGraph 構建複雜的 AI 應用！** 🚀

[查看示例](./01_狀態圖基礎.py) | [返回主頁](../README.md)

</div>
