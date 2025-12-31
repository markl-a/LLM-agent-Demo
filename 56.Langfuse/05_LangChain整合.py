"""
Langfuse LangChain 整合示例

這個示例展示如何將 Langfuse 與 LangChain 整合，包括：
- LangChain 回調處理器
- 鏈路追蹤
- Agent 監控
- RAG 系統追蹤
- 工具調用追蹤
- 記憶體管理

主要內容：
1. LangChain 回調基礎
2. 簡單鏈追蹤
3. 複雜鏈路監控
4. Agent 系統整合
5. RAG 流程追蹤
6. 工具使用監控
7. 性能優化

作者: Langfuse Team
日期: 2025-01-01
"""

import os
import time
from typing import Dict, List, Any, Optional
from langfuse import Langfuse
from langfuse.callback import CallbackHandler

# LangChain 導入
try:
    from langchain.chat_models import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate, PromptTemplate
    from langchain.schema import HumanMessage, SystemMessage, AIMessage
    from langchain.chains import LLMChain, SequentialChain
    from langchain.agents import AgentType, initialize_agent, Tool
    from langchain.memory import ConversationBufferMemory
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️  LangChain 未安裝，部分功能將被模擬")


# ============================================================================
# 第一部分：LangChain 回調基礎
# ============================================================================

class LangChainBasicIntegration:
    """
    LangChain 基礎整合

    展示如何設置 Langfuse 回調處理器。
    """

    def __init__(self):
        """初始化整合配置"""
        # 初始化 Langfuse 回調處理器
        self.callback_handler = CallbackHandler(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY", "pk-demo"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY", "sk-demo"),
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        )

        print("✅ Langfuse 回調處理器初始化成功")

    def simple_chat_example(self):
        """
        簡單聊天示例

        展示最基本的 LangChain + Langfuse 整合。
        """
        print("\n" + "="*60)
        print("簡單聊天示例")
        print("="*60)

        if not LANGCHAIN_AVAILABLE:
            print("⚠️  模擬模式：LangChain 未安裝")
            return

        # 初始化 ChatOpenAI
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            callbacks=[self.callback_handler]  # 添加 Langfuse 回調
        )

        print("🤖 初始化 LangChain ChatOpenAI")

        # 創建消息
        messages = [
            SystemMessage(content="你是一個友善的 AI 助手。"),
            HumanMessage(content="請介紹一下 Langfuse。")
        ]

        print("💬 發送消息...")

        try:
            # 調用 LLM（自動追蹤到 Langfuse）
            response = llm.invoke(messages)

            print(f"✅ 回應: {response.content[:100]}...")
            print("📊 追蹤已自動記錄到 Langfuse")

        except Exception as e:
            print(f"❌ 錯誤: {e}")

    def prompt_template_example(self):
        """
        提示模板示例

        展示如何追蹤使用提示模板的調用。
        """
        print("\n" + "="*60)
        print("提示模板示例")
        print("="*60)

        if not LANGCHAIN_AVAILABLE:
            print("⚠️  模擬模式：LangChain 未安裝")
            return

        # 創建提示模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一位{role}專家。"),
            ("human", "{question}")
        ])

        print("📝 創建提示模板")

        # 初始化 LLM
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            callbacks=[self.callback_handler]
        )

        # 創建鏈
        chain = prompt | llm

        print("🔗 創建 LangChain 鏈")

        try:
            # 執行鏈
            result = chain.invoke({
                "role": "資料科學",
                "question": "什麼是交叉驗證？"
            })

            print(f"✅ 結果: {result.content[:100]}...")
            print("📊 完整鏈路已追蹤到 Langfuse")

        except Exception as e:
            print(f"❌ 錯誤: {e}")


# ============================================================================
# 第二部分：複雜鏈路監控
# ============================================================================

class ChainMonitoring:
    """
    鏈路監控

    追蹤複雜的 LangChain 鏈路。
    """

    def __init__(self, callback_handler: CallbackHandler):
        self.callback_handler = callback_handler

    def sequential_chain_example(self):
        """
        順序鏈示例

        追蹤多步驟的順序處理鏈。
        """
        print("\n" + "="*60)
        print("順序鏈追蹤示例")
        print("="*60)

        if not LANGCHAIN_AVAILABLE:
            print("⚠️  模擬順序鏈執行...")
            print("   步驟 1: 翻譯文本")
            print("   步驟 2: 總結內容")
            print("   步驟 3: 提取關鍵詞")
            print("✅ 模擬完成（實際需要安裝 LangChain）")
            return

        print("🔗 構建順序處理鏈...")

        # LLM
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            callbacks=[self.callback_handler]
        )

        # 第一個鏈：翻譯
        translation_prompt = PromptTemplate(
            input_variables=["text"],
            template="將以下文本翻譯成英文：\n{text}"
        )
        translation_chain = LLMChain(
            llm=llm,
            prompt=translation_prompt,
            output_key="translated_text",
            callbacks=[self.callback_handler]
        )

        # 第二個鏈：總結
        summary_prompt = PromptTemplate(
            input_variables=["translated_text"],
            template="用一句話總結：\n{translated_text}"
        )
        summary_chain = LLMChain(
            llm=llm,
            prompt=summary_prompt,
            output_key="summary",
            callbacks=[self.callback_handler]
        )

        # 第三個鏈：關鍵詞提取
        keywords_prompt = PromptTemplate(
            input_variables=["summary"],
            template="提取 3 個關鍵詞：\n{summary}"
        )
        keywords_chain = LLMChain(
            llm=llm,
            prompt=keywords_prompt,
            output_key="keywords",
            callbacks=[self.callback_handler]
        )

        # 組合成順序鏈
        overall_chain = SequentialChain(
            chains=[translation_chain, summary_chain, keywords_chain],
            input_variables=["text"],
            output_variables=["translated_text", "summary", "keywords"],
            callbacks=[self.callback_handler]
        )

        print("✅ 順序鏈構建完成")

        # 執行鏈
        input_text = "人工智慧正在改變我們的生活方式，從智能助手到自動駕駛，AI 技術無處不在。"

        print(f"\n📥 輸入: {input_text}")
        print("⏳ 執行順序鏈...")

        try:
            result = overall_chain.invoke({"text": input_text})

            print(f"\n📤 輸出:")
            print(f"   翻譯: {result['translated_text'][:80]}...")
            print(f"   總結: {result['summary']}")
            print(f"   關鍵詞: {result['keywords']}")

            print("\n✅ 順序鏈執行完成")
            print("📊 所有步驟已追蹤到 Langfuse")

        except Exception as e:
            print(f"❌ 執行失敗: {e}")

    def parallel_processing_example(self):
        """
        並行處理示例

        模擬並行執行多個鏈。
        """
        print("\n" + "="*60)
        print("並行處理追蹤示例")
        print("="*60)

        if not LANGCHAIN_AVAILABLE:
            print("⚠️  模擬並行處理...")
            tasks = ["情感分析", "實體識別", "主題分類"]
            for task in tasks:
                print(f"   • {task}: 完成")
            print("✅ 模擬完成")
            return

        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            callbacks=[self.callback_handler]
        )

        input_text = "Langfuse 是一個優秀的開源 LLM 可觀測性平台。"

        # 定義多個並行任務
        tasks = [
            {
                "name": "情感分析",
                "prompt": f"分析情感：{input_text}"
            },
            {
                "name": "實體識別",
                "prompt": f"識別實體：{input_text}"
            },
            {
                "name": "主題分類",
                "prompt": f"分類主題：{input_text}"
            }
        ]

        print(f"🚀 並行執行 {len(tasks)} 個任務...")

        results = []

        for task in tasks:
            try:
                result = llm.invoke([HumanMessage(content=task["prompt"])])
                results.append({
                    "task": task["name"],
                    "result": result.content[:50] + "..."
                })
                print(f"   ✓ {task['name']}: 完成")

            except Exception as e:
                print(f"   ✗ {task['name']}: 失敗 - {e}")

        print(f"\n✅ 並行處理完成")
        print("📊 所有任務已追蹤到 Langfuse")


# ============================================================================
# 第三部分：Agent 系統整合
# ============================================================================

class AgentIntegration:
    """
    Agent 系統整合

    追蹤 LangChain Agent 的執行。
    """

    def __init__(self, callback_handler: CallbackHandler):
        self.callback_handler = callback_handler

    def simple_agent_example(self):
        """
        簡單 Agent 示例

        展示如何追蹤 Agent 的工具調用。
        """
        print("\n" + "="*60)
        print("Agent 追蹤示例")
        print("="*60)

        if not LANGCHAIN_AVAILABLE:
            print("⚠️  模擬 Agent 執行...")
            print("   🤖 Agent 思考中...")
            print("   🔧 使用工具: 計算器")
            print("   📊 工具結果: 150")
            print("   💭 Agent 總結: 計算完成")
            print("✅ 模擬完成")
            return

        # 定義工具
        def calculator(expression: str) -> str:
            """簡單的計算器工具"""
            try:
                result = eval(expression)
                return str(result)
            except Exception as e:
                return f"計算錯誤: {e}"

        def text_length(text: str) -> str:
            """計算文本長度"""
            return str(len(text))

        tools = [
            Tool(
                name="計算器",
                func=calculator,
                description="用於數學計算。輸入數學表達式，例如：'100 + 50'"
            ),
            Tool(
                name="文本長度",
                func=text_length,
                description="計算文本長度。輸入任何文本。"
            )
        ]

        # 初始化 LLM
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            callbacks=[self.callback_handler]
        )

        # 初始化 Agent
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            callbacks=[self.callback_handler]
        )

        print("🤖 Agent 初始化完成")

        # 執行 Agent
        query = "100 加 50 等於多少？"
        print(f"\n❓ 查詢: {query}")
        print("⏳ Agent 執行中...")

        try:
            result = agent.invoke({"input": query})

            print(f"\n✅ Agent 回答: {result['output']}")
            print("📊 Agent 執行過程已追蹤到 Langfuse")

        except Exception as e:
            print(f"❌ Agent 執行失敗: {e}")

    def multi_step_agent_example(self):
        """
        多步驟 Agent 示例

        追蹤需要多次工具調用的複雜任務。
        """
        print("\n" + "="*60)
        print("多步驟 Agent 追蹤示例")
        print("="*60)

        if not LANGCHAIN_AVAILABLE:
            print("⚠️  模擬多步驟 Agent...")
            print("   步驟 1: 查詢天氣")
            print("   步驟 2: 查詢匯率")
            print("   步驟 3: 綜合回答")
            print("✅ 模擬完成")
            return

        # 模擬工具函數
        def get_weather(location: str) -> str:
            """獲取天氣信息（模擬）"""
            return f"{location}今天天氣晴朗，氣溫 25°C"

        def get_exchange_rate(currency: str) -> str:
            """獲取匯率（模擬）"""
            rates = {"USD": "30.5", "EUR": "33.2", "JPY": "0.22"}
            return rates.get(currency, "未知貨幣")

        tools = [
            Tool(
                name="天氣查詢",
                func=get_weather,
                description="查詢指定地點的天氣。輸入地點名稱。"
            ),
            Tool(
                name="匯率查詢",
                func=get_exchange_rate,
                description="查詢貨幣匯率。輸入貨幣代碼（如 USD, EUR）。"
            )
        ]

        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            callbacks=[self.callback_handler]
        )

        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            callbacks=[self.callback_handler]
        )

        query = "台北天氣如何？美元匯率是多少？"
        print(f"❓ 複雜查詢: {query}")

        try:
            result = agent.invoke({"input": query})
            print(f"\n✅ 完整回答: {result['output']}")
            print("📊 多步驟執行已追蹤")

        except Exception as e:
            print(f"❌ 失敗: {e}")


# ============================================================================
# 第四部分：RAG 系統追蹤
# ============================================================================

class RAGIntegration:
    """
    RAG 系統整合

    追蹤檢索增強生成流程。
    """

    def __init__(self, callback_handler: CallbackHandler):
        self.callback_handler = callback_handler

    def simple_rag_example(self):
        """
        簡單 RAG 示例

        展示如何追蹤 RAG 流程的各個階段。
        """
        print("\n" + "="*60)
        print("RAG 系統追蹤示例")
        print("="*60)

        print("📚 模擬 RAG 流程...")

        # 模擬文檔檢索
        query = "什麼是 Langfuse？"
        print(f"\n🔍 查詢: {query}")

        # 階段 1: 向量化查詢
        print("   步驟 1: 查詢向量化...")
        time.sleep(0.1)
        print("   ✓ 向量化完成")

        # 階段 2: 檢索相關文檔
        print("   步驟 2: 檢索相關文檔...")
        time.sleep(0.2)

        retrieved_docs = [
            "Langfuse 是開源的 LLM 可觀測性平台",
            "提供追蹤、提示管理和評估功能",
            "支持 LangChain 整合"
        ]

        print(f"   ✓ 檢索到 {len(retrieved_docs)} 個相關文檔")

        # 階段 3: 生成回答
        print("   步驟 3: 生成回答...")

        if LANGCHAIN_AVAILABLE:
            llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                callbacks=[self.callback_handler]
            )

            context = "\n".join(retrieved_docs)
            prompt = f"""基於以下信息回答問題：

{context}

問題：{query}

回答："""

            try:
                result = llm.invoke([HumanMessage(content=prompt)])
                print(f"   ✓ 生成完成")
                print(f"\n💬 回答: {result.content[:100]}...")

            except Exception as e:
                print(f"   ✗ 生成失敗: {e}")
        else:
            print("   ✓ 生成完成（模擬）")

        print("\n✅ RAG 流程完成")
        print("📊 完整流程已追蹤到 Langfuse")


# ============================================================================
# 第五部分：記憶體管理
# ============================================================================

class MemoryManagement:
    """
    記憶體管理

    追蹤帶記憶的對話。
    """

    def __init__(self, callback_handler: CallbackHandler):
        self.callback_handler = callback_handler

    def conversation_memory_example(self):
        """
        對話記憶示例

        追蹤帶有上下文記憶的對話。
        """
        print("\n" + "="*60)
        print("對話記憶追蹤示例")
        print("="*60)

        if not LANGCHAIN_AVAILABLE:
            print("⚠️  模擬對話記憶...")
            conversations = [
                ("你好", "你好！有什麼可以幫助你的嗎？"),
                ("我叫小明", "很高興認識你，小明！"),
                ("我叫什麼名字？", "你叫小明。")
            ]
            for user, ai in conversations:
                print(f"   用戶: {user}")
                print(f"   AI: {ai}")
            print("✅ 模擬完成")
            return

        # 初始化記憶
        memory = ConversationBufferMemory()

        # 初始化 LLM
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            callbacks=[self.callback_handler]
        )

        print("🧠 對話記憶已初始化")

        # 模擬多輪對話
        conversations = [
            "你好！",
            "我的名字是小明",
            "請記住我的名字",
        ]

        print("\n💬 開始對話:")

        for idx, user_input in enumerate(conversations, 1):
            print(f"\n   輪次 {idx}")
            print(f"   用戶: {user_input}")

            # 獲取歷史
            history = memory.load_memory_variables({})

            # 構建提示
            messages = []
            if history.get("history"):
                messages.append(SystemMessage(content=f"對話歷史：\n{history['history']}"))
            messages.append(HumanMessage(content=user_input))

            try:
                response = llm.invoke(messages)
                print(f"   AI: {response.content}")

                # 保存到記憶
                memory.save_context(
                    {"input": user_input},
                    {"output": response.content}
                )

            except Exception as e:
                print(f"   錯誤: {e}")

        print("\n✅ 對話完成")
        print("📊 所有輪次已追蹤到 Langfuse")


# ============================================================================
# 第六部分：性能優化
# ============================================================================

class PerformanceOptimization:
    """
    性能優化

    追蹤和優化 LangChain 性能。
    """

    def __init__(self, callback_handler: CallbackHandler):
        self.callback_handler = callback_handler

    def batch_processing_example(self):
        """
        批量處理示例

        展示批量處理的追蹤。
        """
        print("\n" + "="*60)
        print("批量處理追蹤示例")
        print("="*60)

        if not LANGCHAIN_AVAILABLE:
            print("⚠️  模擬批量處理...")
            for i in range(5):
                print(f"   • 處理項目 {i+1}/5: 完成")
            print("✅ 模擬完成")
            return

        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            callbacks=[self.callback_handler]
        )

        # 準備批量輸入
        inputs = [
            "總結：AI 正在改變世界",
            "總結：量子計算很有前景",
            "總結：區塊鏈技術日益成熟",
            "總結：元宇宙引領未來",
            "總結：綠色能源勢在必行"
        ]

        print(f"📦 批量處理 {len(inputs)} 個項目...")

        results = []

        for idx, text in enumerate(inputs, 1):
            try:
                result = llm.invoke([HumanMessage(content=text)])
                results.append(result.content[:30] + "...")
                print(f"   ✓ 項目 {idx}/{len(inputs)}: 完成")

            except Exception as e:
                print(f"   ✗ 項目 {idx}/{len(inputs)}: 失敗")

        print(f"\n✅ 批量處理完成")
        print(f"   成功: {len(results)}/{len(inputs)}")
        print("📊 所有處理已追蹤到 Langfuse")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """
    主函數：運行所有 LangChain 整合示例
    """
    print("\n" + "="*70)
    print("Langfuse LangChain 整合示例")
    print("="*70)

    if not LANGCHAIN_AVAILABLE:
        print("\n⚠️  警告: LangChain 未安裝")
        print("   部分功能將以模擬模式運行")
        print("   安裝命令: pip install langchain\n")

    try:
        # 1. 基礎整合
        print("\n第一部分：LangChain 基礎整合")
        print("="*70)
        basic = LangChainBasicIntegration()
        basic.simple_chat_example()
        basic.prompt_template_example()

        # 2. 鏈路監控
        print("\n第二部分：複雜鏈路監控")
        print("="*70)
        chain_monitor = ChainMonitoring(basic.callback_handler)
        chain_monitor.sequential_chain_example()
        chain_monitor.parallel_processing_example()

        # 3. Agent 整合
        print("\n第三部分：Agent 系統整合")
        print("="*70)
        agent_integration = AgentIntegration(basic.callback_handler)
        agent_integration.simple_agent_example()
        agent_integration.multi_step_agent_example()

        # 4. RAG 整合
        print("\n第四部分：RAG 系統追蹤")
        print("="*70)
        rag = RAGIntegration(basic.callback_handler)
        rag.simple_rag_example()

        # 5. 記憶體管理
        print("\n第五部分：記憶體管理")
        print("="*70)
        memory = MemoryManagement(basic.callback_handler)
        memory.conversation_memory_example()

        # 6. 性能優化
        print("\n第六部分：性能優化")
        print("="*70)
        perf = PerformanceOptimization(basic.callback_handler)
        perf.batch_processing_example()

        print("\n" + "="*70)
        print("✅ 所有 LangChain 整合示例運行完成！")
        print("="*70)

        print("\n💡 整合最佳實踐:")
        print("   1. 始終添加 Langfuse 回調到 LLM 初始化")
        print("   2. 為複雜鏈路提供清晰的命名")
        print("   3. 追蹤 Agent 的工具調用和決策過程")
        print("   4. 監控 RAG 各階段的性能")
        print("   5. 記錄對話記憶的使用情況")

        # 刷新數據
        basic.callback_handler.flush()

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
