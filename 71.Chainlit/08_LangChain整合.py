"""
Chainlit LangChain 整合示例

本示例展示：
1. LangChain Callback 整合
2. Chain 執行可視化
3. Tool 調用追蹤
4. Agent 行為展示
5. 流式輸出整合

運行方式：
    chainlit run 08_LangChain整合.py -w

環境變量：
    需要設置 OPENAI_API_KEY
"""

import chainlit as cl
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage
from langchain.callbacks.base import BaseCallbackHandler
import os
from dotenv import load_dotenv
from typing import Any, Dict, List

# 載入環境變量
load_dotenv()


# ==================== 自定義 Chainlit Callback ====================

class ChainlitCallbackHandler(BaseCallbackHandler):
    """
    自定義 LangChain Callback Handler
    用於在 Chainlit 中可視化 LangChain 執行過程
    """

    def __init__(self):
        self.current_step = None

    async def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """LLM 開始時調用"""
        print("🤖 LLM 開始...")

    async def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        """LLM 結束時調用"""
        print("✅ LLM 完成")

    async def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Chain 開始時調用"""
        chain_name = serialized.get("name", "Chain")
        print(f"⛓️ {chain_name} 開始...")

    async def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Chain 結束時調用"""
        print("✅ Chain 完成")

    async def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        """Tool 開始時調用"""
        tool_name = serialized.get("name", "Tool")
        print(f"🔧 調用工具: {tool_name}")
        print(f"   輸入: {input_str}")

    async def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Tool 結束時調用"""
        print(f"✅ 工具完成")
        print(f"   輸出: {output[:100]}...")

    async def on_agent_action(self, action: Any, **kwargs: Any) -> None:
        """Agent 動作時調用"""
        print(f"🎯 Agent 行動: {action.tool}")


# ==================== 工具定義 ====================

def get_weather(location: str) -> str:
    """
    獲取天氣信息（模擬）

    Args:
        location: 地點名稱

    Returns:
        天氣信息
    """
    # 模擬天氣數據
    weather_data = {
        "台北": "多雲，溫度 25°C",
        "高雄": "晴天，溫度 28°C",
        "台中": "陰天，溫度 24°C",
    }

    return weather_data.get(location, f"{location} 天氣：晴天，溫度 22°C")


def calculate(expression: str) -> str:
    """
    計算數學表達式

    Args:
        expression: 數學表達式

    Returns:
        計算結果
    """
    try:
        result = eval(expression)
        return f"計算結果：{result}"
    except Exception as e:
        return f"計算錯誤：{str(e)}"


def search_database(query: str) -> str:
    """
    搜索數據庫（模擬）

    Args:
        query: 搜索查詢

    Returns:
        搜索結果
    """
    # 模擬數據庫搜索
    results = {
        "用戶": "找到 150 個用戶記錄",
        "訂單": "找到 320 筆訂單",
        "產品": "找到 45 個產品",
    }

    for key in results:
        if key in query:
            return results[key]

    return f"搜索 '{query}' 找到 10 筆相關記錄"


# 創建 LangChain 工具
tools = [
    Tool(
        name="get_weather",
        func=get_weather,
        description="獲取指定地點的天氣信息。輸入應該是地點名稱，例如：台北、高雄"
    ),
    Tool(
        name="calculator",
        func=calculate,
        description="計算數學表達式。輸入應該是有效的數學表達式，例如：2+2、10*5"
    ),
    Tool(
        name="search_database",
        func=search_database,
        description="搜索數據庫。輸入應該是搜索關鍵詞，例如：用戶、訂單、產品"
    ),
]


# ==================== 會話初始化 ====================

@cl.on_chat_start
async def on_chat_start():
    """初始化聊天會話"""
    try:
        # 檢查 API Key
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            await cl.Message(
                content="""
⚠️ **警告**: 未設置 OPENAI_API_KEY

本示例需要 OpenAI API Key 才能運行。

請設置環境變量：
```bash
export OPENAI_API_KEY="your-key-here"
```

或在 .env 文件中設置。
                """,
                author="系統"
            ).send()
            return

        # 初始化 LLM
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            streaming=True
        )

        # 創建 Agent Prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一個友善的助手，可以使用工具來幫助用戶。

可用工具：
- get_weather: 獲取天氣信息
- calculator: 計算數學表達式
- search_database: 搜索數據庫

請用繁體中文回答。"""),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # 創建 Agent
        agent = create_openai_tools_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=3,
            handle_parsing_errors=True
        )

        # 保存到會話
        cl.user_session.set("agent", agent_executor)
        cl.user_session.set("chat_history", [])

        # 發送歡迎消息
        welcome = """
# 🔗 LangChain 整合示例

歡迎！這個示例展示了 Chainlit 與 LangChain 的深度整合。

## ✨ 功能特點

- 🤖 **LangChain Agent** - 智能工具調用
- 🔧 **工具可視化** - 展示工具調用過程
- 📊 **執行追蹤** - 可視化 Chain 執行
- 💬 **流式輸出** - 實時響應

## 🎯 可用工具

1. **天氣查詢** - 查詢城市天氣
2. **計算器** - 執行數學運算
3. **數據庫搜索** - 搜索模擬數據

## 💡 試試這些

- "台北的天氣如何？"
- "計算 123 * 456"
- "搜索用戶資料"
- "台中天氣怎樣，順便算一下 100+200"

**開始提問吧！** Agent 會自動選擇合適的工具 🚀
        """

        await cl.Message(content=welcome, author="系統").send()

        print("✅ LangChain Agent 已初始化")

    except Exception as e:
        error_msg = f"❌ 初始化失敗: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()


# ==================== 消息處理 ====================

@cl.on_message
async def on_message(message: cl.Message):
    """處理用戶消息"""
    try:
        # 獲取 Agent
        agent_executor = cl.user_session.get("agent")

        if not agent_executor:
            await cl.Message(
                content="❌ Agent 未初始化，請重新啟動。"
            ).send()
            return

        # 獲取對話歷史
        chat_history = cl.user_session.get("chat_history", [])

        # 創建流式響應消息
        msg = cl.Message(content="", author="AI Agent")
        await msg.send()

        # 使用 Step 展示 Agent 執行過程
        async with cl.Step(name="🤖 Agent 執行") as step:
            step.input = message.content

            try:
                # 執行 Agent（帶回調）
                response = await agent_executor.ainvoke(
                    {
                        "input": message.content,
                        "chat_history": chat_history
                    }
                )

                # 獲取輸出
                output = response.get("output", "抱歉，我無法處理這個請求。")

                # 流式顯示響應
                for char in output:
                    await msg.stream_token(char)

                await msg.update()

                step.output = output

                # 更新對話歷史
                chat_history.append(HumanMessage(content=message.content))
                chat_history.append(AIMessage(content=output))
                cl.user_session.set("chat_history", chat_history)

                # 如果有中間步驟，展示出來
                if "intermediate_steps" in response and response["intermediate_steps"]:
                    await show_intermediate_steps(response["intermediate_steps"])

                print(f"✅ Agent 執行完成")

            except Exception as e:
                error_msg = f"執行錯誤：{str(e)}"
                await msg.stream_token(f"\n\n❌ {error_msg}")
                await msg.update()
                step.output = error_msg
                print(f"❌ Agent 錯誤: {str(e)}")

    except Exception as e:
        error_msg = f"❌ 處理失敗: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()


# ==================== 輔助函數 ====================

async def show_intermediate_steps(steps: List):
    """
    展示 Agent 的中間執行步驟

    Args:
        steps: 中間步驟列表
    """
    try:
        if not steps:
            return

        steps_msg = "## 🔍 執行步驟\n\n"

        for i, (action, observation) in enumerate(steps, 1):
            tool_name = action.tool
            tool_input = action.tool_input

            steps_msg += f"""
### 步驟 {i}: 使用工具 `{tool_name}`

**輸入**:
```
{tool_input}
```

**輸出**:
```
{observation}
```

---
            """

        await cl.Message(content=steps_msg, author="執行追蹤").send()

    except Exception as e:
        print(f"❌ 展示步驟失敗: {str(e)}")


# ==================== LangChain Chain 示例 ====================

async def demo_simple_chain():
    """演示簡單的 LangChain Chain"""
    try:
        from langchain.chains import LLMChain

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一個詩人，擅長寫短詩。"),
            ("human", "寫一首關於{topic}的短詩"),
        ])

        chain = LLMChain(llm=llm, prompt=prompt)

        # 使用 Step 展示執行過程
        async with cl.Step(name="📝 生成詩歌") as step:
            step.input = "春天"

            result = await chain.ainvoke({"topic": "春天"})

            step.output = result["text"]

        await cl.Message(
            content=f"## 🎭 生成的詩歌\n\n{result['text']}"
        ).send()

    except Exception as e:
        await cl.Message(content=f"❌ Chain 執行失敗: {str(e)}").send()


# ==================== RAG Chain 示例 ====================

async def demo_rag_chain():
    """演示 RAG (檢索增強生成) Chain"""
    try:
        from langchain.text_splitter import CharacterTextSplitter
        from langchain.vectorstores import Chroma
        from langchain.embeddings import OpenAIEmbeddings
        from langchain.chains import RetrievalQA

        # 模擬文檔
        documents = [
            "Chainlit 是一個用於構建 LLM 應用的 Python 框架。",
            "LangChain 是一個用於開發由語言模型驅動的應用程序的框架。",
            "OpenAI 提供 GPT-4 和 GPT-3.5 等先進的語言模型。",
            "向量數據庫用於存儲和檢索文檔嵌入。",
        ]

        # 分割文檔
        text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
        texts = text_splitter.create_documents(documents)

        # 創建向量存儲
        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma.from_documents(texts, embeddings)

        # 創建 QA Chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(model="gpt-4o-mini"),
            chain_type="stuff",
            retriever=vectorstore.as_retriever()
        )

        # 執行查詢
        async with cl.Step(name="🔍 RAG 檢索") as step:
            query = "什麼是 Chainlit？"
            step.input = query

            result = await qa_chain.ainvoke({"query": query})

            step.output = result["result"]

        await cl.Message(
            content=f"## 📚 RAG 回答\n\n{result['result']}"
        ).send()

    except Exception as e:
        await cl.Message(content=f"❌ RAG 執行失敗: {str(e)}").send()


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║   Chainlit LangChain 整合示例            ║
╚══════════════════════════════════════════╝

運行命令：
    chainlit run 08_LangChain整合.py -w

環境變量：
    export OPENAI_API_KEY="your-key-here"

功能特點：
✅ LangChain Agent 整合
✅ 工具調用可視化
✅ 執行步驟追蹤
✅ 流式輸出
✅ 對話歷史管理
✅ 自定義 Callback Handler

可用工具：
🌤️ 天氣查詢
🔢 計算器
🔍 數據庫搜索

試試這些：
- "台北的天氣如何？"
- "計算 123 * 456"
- "搜索用戶資料"

訪問 http://localhost:8000 體驗 LangChain 整合！
    """)


if __name__ == "__main__":
    main()
