"""
智能客服機器人
使用 LangChain + LangGraph 構建的多功能客服系統

功能特點:
- 多輪對話管理
- 意圖識別和路由
- 知識庫檢索（FAQ）
- 工單創建和追蹤
- 情感分析
"""

import os
from typing import TypedDict, Annotated, Sequence
from datetime import datetime
import operator

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver


# ============ 狀態定義 ============
class AgentState(TypedDict):
    """客服機器人的狀態"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    intent: str  # 用戶意圖：query, complaint, create_ticket
    sentiment: str  # 情感：positive, neutral, negative
    ticket_id: str  # 工單ID（如果創建了工單）
    session_id: str  # 會話ID


# ============ 知識庫初始化 ============
def initialize_knowledge_base():
    """初始化 FAQ 知識庫"""

    # 模擬 FAQ 數據
    faq_data = [
        "問：如何重設密碼？\n答：請點擊登入頁面的「忘記密碼」連結，輸入您的電子郵件地址，我們會發送重設密碼的連結給您。",
        "問：訂單多久會送達？\n答：一般訂單會在 3-5 個工作天內送達。偏遠地區可能需要 5-7 個工作天。",
        "問：可以退貨嗎？\n答：我們提供 30 天無條件退貨服務。商品需保持全新未使用狀態，並附上原包裝。",
        "問：如何聯繫客服？\n答：您可以通過以下方式聯繫我們：\n1. 線上客服（工作日 9:00-18:00）\n2. 客服電話：0800-123-456\n3. 電子郵件：support@example.com",
        "問：支援哪些付款方式？\n答：我們支援信用卡、ATM 轉帳、超商代碼繳費、貨到付款等多種付款方式。",
        "問：會員有什麼優惠？\n答：會員享有：\n1. 首次購物 9 折優惠\n2. 生日當月額外 95 折\n3. 累積點數換購商品\n4. 專屬會員活動通知",
        "問：如何追蹤訂單？\n答：登入您的帳戶，進入「我的訂單」頁面，即可查看訂單狀態和物流資訊。",
        "問：商品有保固嗎？\n答：所有商品都享有原廠保固。電子產品通常為 1-2 年保固，詳細資訊請參考商品說明頁面。",
    ]

    # 文本分割
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=50
    )
    splits = text_splitter.create_documents(faq_data)

    # 創建向量存儲
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        collection_name="customer_service_faq"
    )

    return vectorstore


# ============ 工具函數 ============
def detect_intent(messages: Sequence[BaseMessage]) -> str:
    """檢測用戶意圖"""

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    intent_prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一個意圖分類器。分析用戶的最後一條消息，判斷其意圖：

        - query: 一般查詢、詢問問題
        - complaint: 投訴、不滿
        - create_ticket: 需要人工客服處理、複雜問題

        只回答意圖類別，不要其他說明。"""),
        MessagesPlaceholder(variable_name="messages"),
        ("human", "請判斷最後一條消息的意圖類別：")
    ])

    chain = intent_prompt | llm | StrOutputParser()
    intent = chain.invoke({"messages": messages}).strip().lower()

    # 確保返回有效的意圖
    valid_intents = ["query", "complaint", "create_ticket"]
    if intent not in valid_intents:
        intent = "query"

    return intent


def detect_sentiment(messages: Sequence[BaseMessage]) -> str:
    """檢測用戶情感"""

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    sentiment_prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一個情感分析器。分析用戶的情感狀態：

        - positive: 積極、滿意
        - neutral: 中性
        - negative: 消極、不滿

        只回答情感類別，不要其他說明。"""),
        MessagesPlaceholder(variable_name="messages"),
        ("human", "請判斷最後一條消息的情感：")
    ])

    chain = sentiment_prompt | llm | StrOutputParser()
    sentiment = chain.invoke({"messages": messages}).strip().lower()

    # 確保返回有效的情感
    valid_sentiments = ["positive", "neutral", "negative"]
    if sentiment not in valid_sentiments:
        sentiment = "neutral"

    return sentiment


def create_ticket(messages: Sequence[BaseMessage], session_id: str) -> str:
    """創建客服工單"""

    # 生成工單ID
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    ticket_id = f"TICKET-{timestamp}"

    # 提取問題描述
    last_message = messages[-1].content if messages else "未提供描述"

    # 在實際應用中，這裡會將工單保存到數據庫
    print(f"\n{'='*50}")
    print(f"📋 已創建工單: {ticket_id}")
    print(f"會話ID: {session_id}")
    print(f"問題描述: {last_message}")
    print(f"創建時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

    return ticket_id


# ============ 節點函數 ============
def classify_intent_node(state: AgentState) -> AgentState:
    """意圖分類節點"""

    messages = state["messages"]
    intent = detect_intent(messages)
    sentiment = detect_sentiment(messages)

    print(f"🎯 檢測到意圖: {intent}, 情感: {sentiment}")

    return {
        **state,
        "intent": intent,
        "sentiment": sentiment
    }


def knowledge_base_query_node(state: AgentState) -> AgentState:
    """知識庫查詢節點"""

    # 獲取知識庫
    vectorstore = initialize_knowledge_base()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

    # 獲取最後一條用戶消息
    last_message = state["messages"][-1].content

    # 檢索相關文檔
    docs = retriever.get_relevant_documents(last_message)
    context = "\n\n".join([doc.page_content for doc in docs])

    # 生成回答
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一個專業、友善的客服人員。

        請基於以下知識庫內容回答用戶問題：
        {context}

        注意事項：
        1. 態度要友善、專業
        2. 如果知識庫中有相關信息，請使用它
        3. 如果沒有相關信息，誠實告知並建議創建工單
        4. 保持簡潔明了
        """),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ])

    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({
        "context": context,
        "history": state["messages"][:-1],  # 歷史消息
        "question": last_message
    })

    return {
        **state,
        "messages": [AIMessage(content=response)]
    }


def handle_complaint_node(state: AgentState) -> AgentState:
    """處理投訴節點"""

    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一個經驗豐富的客訴處理專員。

        處理原則：
        1. 首先表達同理心和歉意
        2. 了解問題的具體細節
        3. 提供解決方案或後續處理步驟
        4. 告知用戶已創建優先處理的工單
        5. 語氣要誠懇、專業
        """),
        MessagesPlaceholder(variable_name="messages"),
    ])

    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"messages": state["messages"]})

    # 自動創建優先工單
    ticket_id = create_ticket(state["messages"], state["session_id"])

    enhanced_response = f"{response}\n\n📋 我已為您創建優先處理工單（編號：{ticket_id}），我們的專員會在 24 小時內與您聯繫。"

    return {
        **state,
        "messages": [AIMessage(content=enhanced_response)],
        "ticket_id": ticket_id
    }


def create_ticket_node(state: AgentState) -> AgentState:
    """創建工單節點"""

    ticket_id = create_ticket(state["messages"], state["session_id"])

    response = f"""我理解您的需求。由於這個問題需要更詳細的處理，我已為您創建工單。

📋 工單編號：{ticket_id}
⏰ 預計響應時間：2 個工作小時內
📧 您將收到電子郵件通知

我們的專業客服團隊會盡快與您聯繫。您還有其他問題嗎？"""

    return {
        **state,
        "messages": [AIMessage(content=response)],
        "ticket_id": ticket_id
    }


# ============ 路由函數 ============
def route_by_intent(state: AgentState) -> str:
    """根據意圖路由到不同節點"""

    intent = state.get("intent", "query")

    routing_map = {
        "query": "knowledge_base",
        "complaint": "complaint_handler",
        "create_ticket": "ticket_creator"
    }

    return routing_map.get(intent, "knowledge_base")


# ============ 構建圖 ============
def create_customer_service_graph():
    """創建客服機器人工作流圖"""

    # 創建狀態圖
    workflow = StateGraph(AgentState)

    # 添加節點
    workflow.add_node("classifier", classify_intent_node)
    workflow.add_node("knowledge_base", knowledge_base_query_node)
    workflow.add_node("complaint_handler", handle_complaint_node)
    workflow.add_node("ticket_creator", create_ticket_node)

    # 設置入口
    workflow.set_entry_point("classifier")

    # 添加條件邊：根據意圖路由
    workflow.add_conditional_edges(
        "classifier",
        route_by_intent,
        {
            "knowledge_base": "knowledge_base",
            "complaint_handler": "complaint_handler",
            "ticket_creator": "ticket_creator"
        }
    )

    # 所有處理節點都指向 END
    workflow.add_edge("knowledge_base", END)
    workflow.add_edge("complaint_handler", END)
    workflow.add_edge("ticket_creator", END)

    # 添加記憶體檢查點
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)


# ============ 主程序 ============
def run_customer_service_bot():
    """運行客服機器人"""

    print("🤖 智能客服機器人已啟動")
    print("=" * 60)
    print("輸入 'quit' 或 'exit' 結束對話\n")

    # 創建圖
    app = create_customer_service_graph()

    # 生成會話ID
    session_id = f"SESSION-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # 配置
    config = {
        "configurable": {
            "thread_id": session_id
        }
    }

    # 初始狀態
    state = {
        "messages": [
            SystemMessage(content="你好！我是智能客服助手，很高興為您服務。請問有什麼可以幫助您的？")
        ],
        "intent": "",
        "sentiment": "",
        "ticket_id": "",
        "session_id": session_id
    }

    print(f"🤖 助手: {state['messages'][0].content}\n")

    while True:
        # 獲取用戶輸入
        user_input = input("👤 您: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ['quit', 'exit', '退出']:
            print("\n感謝您的使用，再見！👋")
            break

        # 添加用戶消息
        state["messages"].append(HumanMessage(content=user_input))

        try:
            # 運行圖
            result = app.invoke(state, config)

            # 獲取最新的 AI 回復
            ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
            if ai_messages:
                latest_response = ai_messages[-1].content
                print(f"\n🤖 助手: {latest_response}\n")

                # 更新狀態
                state = result

        except Exception as e:
            print(f"\n❌ 發生錯誤: {str(e)}\n")
            print("請稍後再試，或輸入其他問題。\n")


if __name__ == "__main__":
    # 檢查環境變數
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 錯誤: 請設置 OPENAI_API_KEY 環境變數")
        print("   export OPENAI_API_KEY='your-api-key'")
        exit(1)

    run_customer_service_bot()
