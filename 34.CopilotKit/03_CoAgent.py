"""
CopilotKit CoAgent 協作範例

CoAgent 是 CopilotKit 的核心功能，允許創建具有特定能力的 AI Agent，
並讓它們協作完成複雜任務。

這個範例展示：
1. 定義和配置 CoAgent
2. Agent 之間的協作
3. LangGraph 整合
4. 工具和狀態管理
5. 多 Agent 工作流

官方文檔：https://docs.copilotkit.ai/coagents
"""

import os
from typing import Any, Dict, List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from copilotkit import CopilotKitSDK, LangGraphAgent
from copilotkit.integrations.fastapi import add_fastapi_endpoint

# LangGraph 相關導入
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict

import uvicorn


# ============================================================================
# 第一部分：定義 Agent 狀態
# ============================================================================

class AgentState(TypedDict):
    """Agent 工作流狀態"""
    messages: List[Any]
    current_task: str
    results: Dict[str, Any]
    next_agent: Optional[str]


# ============================================================================
# 第二部分：創建專門化的 Agents
# ============================================================================

class ResearchAgent:
    """研究型 Agent - 負責信息搜集和分析"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.name = "研究員"

    async def execute(self, state: AgentState) -> AgentState:
        """執行研究任務"""
        task = state["current_task"]

        # 使用 LLM 進行研究
        messages = [
            SystemMessage(content=f"你是一個專業的研究員，負責深入分析：{task}"),
            HumanMessage(content=f"請研究這個主題並提供詳細分析：{task}")
        ]

        response = await self.llm.ainvoke(messages)

        # 更新狀態
        state["messages"].append(AIMessage(content=response.content, name=self.name))
        state["results"]["research"] = response.content

        return state


class WriterAgent:
    """寫作型 Agent - 負責內容創作"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.name = "作家"

    async def execute(self, state: AgentState) -> AgentState:
        """執行寫作任務"""
        research_data = state["results"].get("research", "")

        messages = [
            SystemMessage(content="你是一個專業的內容作家"),
            HumanMessage(content=f"基於以下研究內容，撰寫一篇文章：\\n\\n{research_data}")
        ]

        response = await self.llm.ainvoke(messages)

        state["messages"].append(AIMessage(content=response.content, name=self.name))
        state["results"]["article"] = response.content

        return state


class ReviewerAgent:
    """審核型 Agent - 負責質量檢查"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.name = "審核員"

    async def execute(self, state: AgentState) -> AgentState:
        """執行審核任務"""
        article = state["results"].get("article", "")

        messages = [
            SystemMessage(content="你是一個專業的內容審核員"),
            HumanMessage(content=f"請審核以下文章並提供改進建議：\\n\\n{article}")
        ]

        response = await self.llm.ainvoke(messages)

        state["messages"].append(AIMessage(content=response.content, name=self.name))
        state["results"]["review"] = response.content

        return state


# ============================================================================
# 第三部分：構建 LangGraph 工作流
# ============================================================================

def create_content_workflow():
    """創建內容生產工作流"""

    # 初始化 LLM
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)

    # 創建 Agents
    researcher = ResearchAgent(llm)
    writer = WriterAgent(llm)
    reviewer = ReviewerAgent(llm)

    # 創建狀態圖
    workflow = StateGraph(AgentState)

    # 定義節點（Agents）
    workflow.add_node("research", researcher.execute)
    workflow.add_node("write", writer.execute)
    workflow.add_node("review", reviewer.execute)

    # 定義邊（Agent 之間的流程）
    workflow.set_entry_point("research")
    workflow.add_edge("research", "write")
    workflow.add_edge("write", "review")
    workflow.add_edge("review", END)

    return workflow.compile()


# ============================================================================
# 第四部分：定義 LangGraph CoAgents
# ============================================================================

def create_research_agent():
    """創建研究 Agent"""

    def research_graph():
        llm = ChatOpenAI(model="gpt-4")
        researcher = ResearchAgent(llm)

        workflow = StateGraph(AgentState)
        workflow.add_node("research", researcher.execute)
        workflow.set_entry_point("research")
        workflow.add_edge("research", END)

        return workflow.compile()

    return LangGraphAgent(
        name="researcher",
        description="專業研究員，負責深入調查和分析主題",
        graph=research_graph(),
    )


def create_writer_agent():
    """創建寫作 Agent"""

    def writer_graph():
        llm = ChatOpenAI(model="gpt-4")
        writer = WriterAgent(llm)

        workflow = StateGraph(AgentState)
        workflow.add_node("write", writer.execute)
        workflow.set_entry_point("write")
        workflow.add_edge("write", END)

        return workflow.compile()

    return LangGraphAgent(
        name="writer",
        description="專業作家，負責創作高質量內容",
        graph=writer_graph(),
    )


def create_content_pipeline_agent():
    """創建完整的內容生產流水線 Agent"""

    return LangGraphAgent(
        name="content_pipeline",
        description="完整的內容生產流程：研究 → 寫作 → 審核",
        graph=create_content_workflow(),
    )


# ============================================================================
# 第五部分：FastAPI 應用設置
# ============================================================================

app = FastAPI(
    title="CopilotKit CoAgent 範例",
    description="展示 CoAgent 協作功能",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# 第六部分：初始化 CopilotKit SDK
# ============================================================================

# 設置環境變量
os.environ.setdefault("OPENAI_API_KEY", "your-openai-api-key")

# 創建 SDK 實例
sdk = CopilotKitSDK()

# 註冊 CoAgents
sdk.add_agent(create_research_agent())
sdk.add_agent(create_writer_agent())
sdk.add_agent(create_content_pipeline_agent())


# 添加傳統的 Actions（與 CoAgents 協作）
from copilotkit import Action


def get_topic_suggestions(category: str) -> Dict[str, Any]:
    """獲取主題建議"""
    suggestions = {
        "技術": ["AI 發展趨勢", "雲端運算", "區塊鏈應用"],
        "商業": ["創業指南", "市場分析", "品牌策略"],
        "生活": ["健康飲食", "時間管理", "理財規劃"],
    }
    return {
        "success": True,
        "category": category,
        "suggestions": suggestions.get(category, ["通用主題"])
    }


sdk.add_action(
    Action(
        name="get_topic_suggestions",
        description="獲取特定類別的主題建議",
        parameters=[{
            "name": "category",
            "type": "string",
            "description": "主題類別（技術、商業、生活）",
            "required": True
        }],
        handler=get_topic_suggestions
    )
)


# 添加 CopilotKit 端點
add_fastapi_endpoint(app, sdk, "/copilotkit")


# ============================================================================
# 第七部分：REST API 端點
# ============================================================================

@app.get("/")
async def root():
    return {
        "message": "CopilotKit CoAgent 協作範例",
        "agents": [
            {
                "name": "researcher",
                "description": "研究員 Agent",
                "capabilities": ["信息搜集", "數據分析", "趨勢研究"]
            },
            {
                "name": "writer",
                "description": "作家 Agent",
                "capabilities": ["內容創作", "文章撰寫", "SEO 優化"]
            },
            {
                "name": "content_pipeline",
                "description": "完整內容流水線",
                "capabilities": ["端到端內容生產", "質量保證", "協作編排"]
            }
        ]
    }


@app.get("/agents")
async def list_agents():
    """列出所有可用的 Agents"""
    return {
        "agents": [
            {
                "name": "researcher",
                "type": "LangGraphAgent",
                "description": "專業研究員，負責深入調查和分析主題"
            },
            {
                "name": "writer",
                "type": "LangGraphAgent",
                "description": "專業作家，負責創作高質量內容"
            },
            {
                "name": "content_pipeline",
                "type": "LangGraphAgent",
                "description": "完整的內容生產流程"
            }
        ]
    }


# ============================================================================
# 第八部分：前端整合範例（React + TypeScript）
# ============================================================================

REACT_CODE = """
// ===== App.tsx =====
import React, { useState } from 'react';
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";
import { useCopilotAction, useCopilotReadable } from "@copilotkit/react-core";
import "@copilotkit/react-ui/styles.css";

function ContentStudio() {
  const [currentProject, setCurrentProject] = useState({
    topic: "",
    research: "",
    article: "",
    review: "",
  });

  // 讓 AI 知道當前項目狀態
  useCopilotReadable({
    description: "當前內容項目的狀態",
    value: currentProject,
  });

  // 定義與 CoAgents 交互的 Actions
  useCopilotAction({
    name: "startResearch",
    description: "啟動研究 Agent 調查主題",
    parameters: [
      {
        name: "topic",
        type: "string",
        description: "要研究的主題",
        required: true,
      },
    ],
    handler: async ({ topic }) => {
      setCurrentProject(prev => ({ ...prev, topic }));
      // CoAgent 會自動處理研究任務
      return `已啟動研究：${topic}`;
    },
  });

  useCopilotAction({
    name: "generateArticle",
    description: "讓寫作 Agent 基於研究生成文章",
    parameters: [],
    handler: async () => {
      // CoAgent 會基於當前狀態生成文章
      return "寫作 Agent 正在工作...";
    },
  });

  return (
    <div className="content-studio">
      <h1>AI 內容工作室</h1>

      {/* 項目狀態展示 */}
      <div className="project-status">
        <div className="status-card">
          <h3>📚 研究</h3>
          <p>{currentProject.research || "等待中..."}</p>
        </div>
        <div className="status-card">
          <h3>✍️ 文章</h3>
          <p>{currentProject.article || "等待中..."}</p>
        </div>
        <div className="status-card">
          <h3>✅ 審核</h3>
          <p>{currentProject.review || "等待中..."}</p>
        </div>
      </div>

      {/* AI 協作提示 */}
      <div className="ai-hints">
        <h3>💡 試試對 AI 說：</h3>
        <ul>
          <li>"研究 AI 在醫療領域的應用"</li>
          <li>"基於研究寫一篇文章"</li>
          <li>"啟動完整的內容生產流程"</li>
          <li>"給我一些技術類主題建議"</li>
        </ul>
      </div>
    </div>
  );
}

function App() {
  return (
    <CopilotKit
      runtimeUrl="http://localhost:8000/copilotkit"
      agent="content_pipeline"  // 指定默認 Agent
    >
      <CopilotSidebar
        instructions={`
          你是一個內容工作室的協調者。你可以調用三個專業 Agent：
          1. researcher - 研究員，負責調查和分析
          2. writer - 作家，負責內容創作
          3. content_pipeline - 完整流程，自動協調所有步驟

          根據用戶需求選擇合適的 Agent 或 Action。
        `}
        labels={{
          title: "內容工作室 AI",
          initial: "我可以幫你研究、寫作和審核內容！",
        }}
        defaultOpen={true}
      >
        <ContentStudio />
      </CopilotSidebar>
    </CopilotKit>
  );
}

export default App;

// ===== 高級：手動調用特定 Agent =====
import { useCopilotContext } from "@copilotkit/react-core";

function ManualAgentControl() {
  const { runAgent } = useCopilotContext();

  const handleResearch = async () => {
    const result = await runAgent("researcher", {
      messages: [
        { role: "user", content: "研究 AI 倫理問題" }
      ]
    });
    console.log("研究結果:", result);
  };

  return (
    <button onClick={handleResearch}>
      啟動研究 Agent
    </button>
  );
}
"""


# ============================================================================
# 第九部分：運行說明
# ============================================================================

if __name__ == "__main__":
    print("\\n" + "="*70)
    print("CopilotKit CoAgent 協作範例")
    print("="*70)
    print("\\n已註冊的 CoAgents:")
    print("  1. researcher - 研究員 Agent（單一功能）")
    print("  2. writer - 作家 Agent（單一功能）")
    print("  3. content_pipeline - 完整流水線（多 Agent 協作）")
    print("\\nCoAgent 特點：")
    print("  • 使用 LangGraph 構建複雜工作流")
    print("  • 多個 Agent 可以協作完成任務")
    print("  • 每個 Agent 有專門的職責和能力")
    print("  • 支持狀態管理和流程控制")
    print("\\n啟動服務器...")
    print("="*70 + "\\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)


"""
CoAgent 核心概念：

1. Agent 定義
   - 每個 Agent 是一個獨立的智能單元
   - 有明確的職責和能力範圍
   - 使用 LangGraph 定義行為邏輯

2. Agent 協作
   - 通過共享狀態交換信息
   - 工作流編排控制執行順序
   - 支持條件分支和循環

3. LangGraph 整合
   - StateGraph：定義狀態機
   - Nodes：Agent 的執行節點
   - Edges：Agent 之間的連接

4. 與前端交互
   - 前端通過 Actions 觸發 Agent
   - Agent 執行結果返回給前端
   - 實時更新應用狀態

CoAgent vs 傳統 Action：

| 特性 | CoAgent | Action |
|------|---------|--------|
| 複雜度 | 高（複雜工作流） | 低（單一操作） |
| 自主性 | 強（自主決策） | 弱（被動調用） |
| 協作 | 支持多 Agent | 單獨執行 |
| 狀態 | 有狀態 | 無狀態 |
| 適用場景 | 複雜任務 | 簡單操作 |

使用場景：

1. 內容生產流水線
   - 研究 → 寫作 → 審核 → 發布

2. 客戶服務系統
   - 接待 → 分類 → 處理 → 跟進

3. 數據分析工作流
   - 採集 → 清洗 → 分析 → 報告

4. 軟件開發輔助
   - 需求分析 → 設計 → 編碼 → 測試

最佳實踐：

1. Agent 設計
   - 單一職責原則
   - 清晰的輸入輸出
   - 良好的錯誤處理

2. 工作流設計
   - 明確的流程步驟
   - 合理的狀態管理
   - 支持回退和重試

3. 性能優化
   - 並行執行獨立任務
   - 緩存中間結果
   - 異步處理長任務

下一步：
- 查看 04_前端狀態.py 學習狀態管理
- 查看 08_多Agent.py 學習更複雜的協作
- 查看 10_最佳實踐.py 了解生產級實現
"""
