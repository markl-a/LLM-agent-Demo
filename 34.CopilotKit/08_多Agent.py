"""
CopilotKit 多 Agent 協作範例

這個範例展示複雜的多 Agent 協作場景，包括：
1. 多個專門化 Agent 定義
2. Agent 之間的通信和協調
3. 任務分配和路由
4. 並行 vs 順序執行
5. Agent 編排模式
6. 實際應用場景（客戶服務、開發助手等）

這是 CopilotKit 最強大的功能之一
"""

import os
import asyncio
from typing import Any, Dict, List, Optional
from enum import Enum
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from copilotkit import CopilotKitSDK, LangGraphAgent, Action
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
import uvicorn


# ============================================================================
# 第一部分：定義 Agent 類型和狀態
# ============================================================================

class AgentType(str, Enum):
    """Agent 類型枚舉"""
    COORDINATOR = "coordinator"  # 協調者
    RESEARCHER = "researcher"    # 研究員
    ANALYST = "analyst"         # 分析師
    WRITER = "writer"           # 寫作者
    REVIEWER = "reviewer"       # 審核者
    CUSTOMER_SERVICE = "customer_service"  # 客服


class MultiAgentState(TypedDict):
    """多 Agent 工作流狀態"""
    messages: List[Any]
    task: str
    current_agent: Optional[str]
    results: Dict[str, Any]
    metadata: Dict[str, Any]
    next_agent: Optional[str]


# ============================================================================
# 第二部分：定義專門化的 Agents
# ============================================================================

class CoordinatorAgent:
    """
    協調者 Agent
    負責：任務分解、Agent 調度、結果整合
    """

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.name = "協調者"

    async def execute(self, state: MultiAgentState) -> MultiAgentState:
        """執行協調任務"""
        task = state["task"]

        messages = [
            SystemMessage(content=f"""
你是一個智能協調者。分析任務並決定需要哪些 Agent 協作。

可用的 Agents：
- researcher: 研究和信息搜集
- analyst: 數據分析和洞察
- writer: 內容創作
- reviewer: 質量審核
- customer_service: 客戶服務

任務: {task}

請決定執行順序和需要的 Agents。
            """),
            HumanMessage(content=f"請分析這個任務：{task}")
        ]

        response = await self.llm.ainvoke(messages)

        state["messages"].append(AIMessage(
            content=response.content,
            name=self.name
        ))
        state["results"]["coordination"] = response.content

        # 決定下一個 Agent（這裡簡化處理）
        if "研究" in task or "調查" in task:
            state["next_agent"] = "researcher"
        elif "分析" in task:
            state["next_agent"] = "analyst"
        elif "寫" in task or "創作" in task:
            state["next_agent"] = "writer"
        else:
            state["next_agent"] = "customer_service"

        return state


class ResearcherAgent:
    """研究員 Agent - 專注於信息搜集"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.name = "研究員"

    async def execute(self, state: MultiAgentState) -> MultiAgentState:
        task = state["task"]
        context = state["results"].get("coordination", "")

        messages = [
            SystemMessage(content="你是一個專業研究員，負責深入調查和信息搜集"),
            HumanMessage(content=f"基於協調者的建議：{context}\\n\\n請研究：{task}")
        ]

        response = await self.llm.ainvoke(messages)

        state["messages"].append(AIMessage(
            content=response.content,
            name=self.name
        ))
        state["results"]["research"] = response.content
        state["next_agent"] = "analyst"  # 研究完成後交給分析師

        return state


class AnalystAgent:
    """分析師 Agent - 專注於數據分析"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.name = "分析師"

    async def execute(self, state: MultiAgentState) -> MultiAgentState:
        research_data = state["results"].get("research", "")

        messages = [
            SystemMessage(content="你是一個專業數據分析師"),
            HumanMessage(content=f"基於研究結果：{research_data}\\n\\n請進行深入分析")
        ]

        response = await self.llm.ainvoke(messages)

        state["messages"].append(AIMessage(
            content=response.content,
            name=self.name
        ))
        state["results"]["analysis"] = response.content
        state["next_agent"] = "writer"  # 分析完成後交給寫作者

        return state


class WriterAgent:
    """寫作者 Agent - 專注於內容創作"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.name = "寫作者"

    async def execute(self, state: MultiAgentState) -> MultiAgentState:
        analysis = state["results"].get("analysis", "")
        research = state["results"].get("research", "")

        messages = [
            SystemMessage(content="你是一個專業內容作家"),
            HumanMessage(content=f"""
基於以下內容創作文章：

研究結果：{research}

分析結果：{analysis}
            """)
        ]

        response = await self.llm.ainvoke(messages)

        state["messages"].append(AIMessage(
            content=response.content,
            name=self.name
        ))
        state["results"]["article"] = response.content
        state["next_agent"] = "reviewer"  # 寫作完成後交給審核者

        return state


class ReviewerAgent:
    """審核者 Agent - 專注於質量控制"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.name = "審核者"

    async def execute(self, state: MultiAgentState) -> MultiAgentState:
        article = state["results"].get("article", "")

        messages = [
            SystemMessage(content="你是一個專業內容審核員"),
            HumanMessage(content=f"請審核以下文章並提供改進建議：\\n\\n{article}")
        ]

        response = await self.llm.ainvoke(messages)

        state["messages"].append(AIMessage(
            content=response.content,
            name=self.name
        ))
        state["results"]["review"] = response.content
        state["next_agent"] = None  # 審核完成，工作流結束

        return state


class CustomerServiceAgent:
    """客服 Agent - 處理客戶查詢"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.name = "客服專員"

    async def execute(self, state: MultiAgentState) -> MultiAgentState:
        task = state["task"]

        messages = [
            SystemMessage(content="你是一個友好專業的客服人員"),
            HumanMessage(content=f"客戶問題：{task}")
        ]

        response = await self.llm.ainvoke(messages)

        state["messages"].append(AIMessage(
            content=response.content,
            name=self.name
        ))
        state["results"]["customer_response"] = response.content
        state["next_agent"] = None

        return state


# ============================================================================
# 第三部分：構建多 Agent 工作流
# ============================================================================

def create_content_production_workflow():
    """
    創建完整的內容生產工作流
    流程：協調 → 研究 → 分析 → 寫作 → 審核
    """
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)

    # 創建所有 Agents
    coordinator = CoordinatorAgent(llm)
    researcher = ResearcherAgent(llm)
    analyst = AnalystAgent(llm)
    writer = WriterAgent(llm)
    reviewer = ReviewerAgent(llm)

    # 創建狀態圖
    workflow = StateGraph(MultiAgentState)

    # 添加節點
    workflow.add_node("coordinator", coordinator.execute)
    workflow.add_node("researcher", researcher.execute)
    workflow.add_node("analyst", analyst.execute)
    workflow.add_node("writer", writer.execute)
    workflow.add_node("reviewer", reviewer.execute)

    # 定義流程
    workflow.set_entry_point("coordinator")

    # 條件路由：根據協調者的決定選擇下一個 Agent
    def route_from_coordinator(state: MultiAgentState) -> str:
        next_agent = state.get("next_agent")
        return next_agent if next_agent else END

    workflow.add_conditional_edges(
        "coordinator",
        route_from_coordinator,
        {
            "researcher": "researcher",
            "analyst": "analyst",
            "writer": "writer",
            "customer_service": END,
            END: END
        }
    )

    # 順序執行
    workflow.add_edge("researcher", "analyst")
    workflow.add_edge("analyst", "writer")
    workflow.add_edge("writer", "reviewer")
    workflow.add_edge("reviewer", END)

    return workflow.compile()


def create_customer_service_workflow():
    """
    創建客戶服務工作流
    包含：分類 → 專門處理 → 響應
    """
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)

    coordinator = CoordinatorAgent(llm)
    customer_service = CustomerServiceAgent(llm)

    workflow = StateGraph(MultiAgentState)

    workflow.add_node("coordinator", coordinator.execute)
    workflow.add_node("customer_service", customer_service.execute)

    workflow.set_entry_point("coordinator")
    workflow.add_edge("coordinator", "customer_service")
    workflow.add_edge("customer_service", END)

    return workflow.compile()


# ============================================================================
# 第四部分：並行 Agent 執行示例
# ============================================================================

async def execute_agents_in_parallel(
    agents: List[Any],
    state: MultiAgentState
) -> Dict[str, Any]:
    """並行執行多個 Agents"""
    tasks = [agent.execute(state.copy()) for agent in agents]
    results = await asyncio.gather(*tasks)

    # 合併結果
    combined_results = {}
    for result in results:
        combined_results.update(result.get("results", {}))

    return combined_results


# ============================================================================
# 第五部分：FastAPI 應用設置
# ============================================================================

app = FastAPI(title="CopilotKit 多 Agent 協作範例")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.environ.setdefault("OPENAI_API_KEY", "your-openai-api-key")


# ============================================================================
# 第六部分：註冊 LangGraph Agents
# ============================================================================

sdk = CopilotKitSDK()

# 註冊內容生產工作流
sdk.add_agent(LangGraphAgent(
    name="content_production",
    description="完整的內容生產流程：研究 → 分析 → 寫作 → 審核",
    graph=create_content_production_workflow()
))

# 註冊客戶服務工作流
sdk.add_agent(LangGraphAgent(
    name="customer_service",
    description="智能客戶服務系統",
    graph=create_customer_service_workflow()
))


# 添加輔助 Actions
def list_available_agents() -> Dict[str, Any]:
    """列出所有可用的 Agents"""
    return {
        "success": True,
        "agents": [
            {
                "name": "content_production",
                "type": "workflow",
                "agents": ["coordinator", "researcher", "analyst", "writer", "reviewer"],
                "description": "完整內容生產流程"
            },
            {
                "name": "customer_service",
                "type": "workflow",
                "agents": ["coordinator", "customer_service"],
                "description": "客戶服務系統"
            }
        ]
    }


sdk.add_action(Action(
    name="list_agents",
    description="列出所有可用的 Agents 和工作流",
    parameters=[],
    handler=list_available_agents
))

add_fastapi_endpoint(app, sdk, "/copilotkit")


# ============================================================================
# 第七部分：REST API 端點
# ============================================================================

@app.get("/")
async def root():
    return {
        "message": "CopilotKit 多 Agent 協作範例",
        "workflows": [
            "content_production - 內容生產流程",
            "customer_service - 客戶服務"
        ]
    }


@app.get("/agents")
async def list_agents_endpoint():
    return list_available_agents()


# ============================================================================
# 第八部分：運行說明
# ============================================================================

if __name__ == "__main__":
    print("\\n" + "="*70)
    print("CopilotKit 多 Agent 協作範例")
    print("="*70)
    print("\\n可用的工作流：")
    print("\\n1. 內容生產流程 (content_production)")
    print("   協調者 → 研究員 → 分析師 → 寫作者 → 審核者")
    print("\\n2. 客戶服務 (customer_service)")
    print("   協調者 → 客服專員")
    print("\\n特點：")
    print("  • 動態任務路由")
    print("  • Agent 間狀態共享")
    print("  • 順序和並行執行")
    print("  • 條件分支")
    print("="*70 + "\\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)


"""
多 Agent 協作最佳實踐：

1. Agent 設計原則
   ✓ 單一職責：每個 Agent 專注一個領域
   ✓ 清晰接口：定義明確的輸入輸出
   ✓ 無狀態：避免 Agent 內部狀態
   ✓ 可組合：易於組合成複雜工作流

2. 任務分配策略
   ✓ 基於能力：根據 Agent 專長分配
   ✓ 負載均衡：避免單個 Agent 過載
   ✓ 優先級：重要任務優先處理
   ✓ 動態路由：根據上下文選擇 Agent

3. 通信模式
   ✓ 共享狀態：通過 StateGraph 共享
   ✓ 消息傳遞：使用 messages 列表
   ✓ 結果累積：在 results 字典中累積
   ✓ 元數據：使用 metadata 傳遞控制信息

4. 執行模式
   ✓ 順序執行：一個接一個（用於依賴任務）
   ✓ 並行執行：同時執行（用於獨立任務）
   ✓ 條件執行：根據條件選擇路徑
   ✓ 循環執行：迭代改進

5. 錯誤處理
   ✓ 優雅降級：Agent 失敗時降級處理
   ✓ 重試機制：自動重試失敗的 Agent
   ✓ 回退策略：準備備用 Agent
   ✓ 錯誤隔離：防止錯誤傳播

Agent 編排模式：

1. 管道模式（Pipeline）
   A → B → C → D
   適用：順序處理流程

2. 扇出模式（Fan-out）
   A → [B, C, D] (並行)
   適用：獨立並行任務

3. 扇入模式（Fan-in）
   [A, B, C] → D (聚合)
   適用：結果聚合

4. 分支模式（Branch）
   A → {B or C or D}
   適用：條件路由

5. 迭代模式（Iteration）
   A ⇄ B (循環)
   適用：迭代改進

實際應用場景：

1. 內容生產系統
   研究 → 大綱 → 寫作 → 編輯 → 發布

2. 客戶服務系統
   分類 → 路由 → 處理 → 跟進

3. 數據分析平台
   採集 → 清洗 → 分析 → 可視化 → 報告

4. 軟件開發助手
   需求 → 設計 → 編碼 → 測試 → 部署

5. 研究助手
   搜索 → 篩選 → 總結 → 引用 → 報告

性能優化：

1. 並行化
   - 識別可並行的 Agents
   - 使用 asyncio.gather
   - 注意資源限制

2. 緩存
   - 緩存 Agent 結果
   - 避免重複計算
   - 設置合理的過期時間

3. 超時控制
   - 為每個 Agent 設置超時
   - 長任務異步處理
   - 提供進度反饋

下一步：
- 查看 09_部署指南.py 了解生產部署
- 查看 10_最佳實踐.py 學習最佳實踐
- 研究 LangGraph 文檔深入學習
"""
