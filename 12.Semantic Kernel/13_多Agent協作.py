#!/usr/bin/env python3
"""
Semantic Kernel - 多 Agent 協作示例

本示例展示：
1. 多 Agent 系統
2. Agent 間通信
3. 任務分配與協作
4. Agent 協調
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

try:
    import semantic_kernel as sk
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
    from semantic_kernel.agents import ChatCompletionAgent
    from semantic_kernel.contents import ChatHistory
except ImportError:
    print("❌ 請安裝 Semantic Kernel:")
    print("   pip install semantic-kernel")
    exit(1)


async def example_basic_multi_agent():
    """示例 1: 基本多 Agent 系統"""
    print("\n" + "=" * 60)
    print("示例 1: 基本多 Agent 系統")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    # 創建多個專業 Agent
    researcher = ChatCompletionAgent(
        service_id="chat-gpt",
        kernel=kernel,
        name="Researcher",
        instructions="""你是一個研究專家，負責收集和分析信息。
        你的回答要基於事實，引用可靠來源。""",
    )

    writer = ChatCompletionAgent(
        service_id="chat-gpt",
        kernel=kernel,
        name="Writer",
        instructions="""你是一個專業作家，負責將信息組織成結構清晰的文章。
        你的寫作要簡潔、易懂、有邏輯。""",
    )

    reviewer = ChatCompletionAgent(
        service_id="chat-gpt",
        kernel=kernel,
        name="Reviewer",
        instructions="""你是一個審核專家，負責檢查內容的準確性和質量。
        你要指出錯誤、提出改進建議。""",
    )

    print("✅ 創建了 3 個專業 Agent:")
    print("   - Researcher (研究專家)")
    print("   - Writer (專業作家)")
    print("   - Reviewer (審核專家)\n")

    topic = "量子計算的基本概念"
    print(f"📝 主題: {topic}\n")

    # 研究階段
    print("🔬 階段 1: 研究")
    research_history = ChatHistory()
    research_history.add_user_message(f"請研究並總結: {topic}")

    research_result = await researcher.invoke(research_history)
    research_content = research_result.messages[-1].content

    print(f"Researcher: {research_content}\n")

    # 寫作階段
    print("✍️  階段 2: 寫作")
    write_history = ChatHistory()
    write_history.add_user_message(
        f"基於以下研究，寫一篇文章:\n\n{research_content}"
    )

    write_result = await writer.invoke(write_history)
    write_content = write_result.messages[-1].content

    print(f"Writer: {write_content}\n")

    # 審核階段
    print("🔍 階段 3: 審核")
    review_history = ChatHistory()
    review_history.add_user_message(f"請審核以下文章:\n\n{write_content}")

    review_result = await reviewer.invoke(review_history)
    review_content = review_result.messages[-1].content

    print(f"Reviewer: {review_content}")


async def example_collaborative_problem_solving():
    """示例 2: 協作解決問題"""
    print("\n" + "=" * 60)
    print("示例 2: 協作解決問題")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    # 創建問題解決團隊
    analyst = ChatCompletionAgent(
        service_id="chat-gpt",
        kernel=kernel,
        name="Analyst",
        instructions="你是數據分析專家，擅長發現模式和洞察。",
    )

    strategist = ChatCompletionAgent(
        service_id="chat-gpt",
        kernel=kernel,
        name="Strategist",
        instructions="你是戰略規劃專家，擅長制定解決方案。",
    )

    implementer = ChatCompletionAgent(
        service_id="chat-gpt",
        kernel=kernel,
        name="Implementer",
        instructions="你是執行專家，擅長將計劃轉化為具體行動。",
    )

    problem = "公司的客戶流失率在過去三個月增加了 20%"
    print(f"❓ 問題: {problem}\n")

    # 分析
    print("📊 Analyst 分析問題:")
    analyst_history = ChatHistory()
    analyst_history.add_user_message(f"分析這個問題: {problem}")

    analyst_result = await analyst.invoke(analyst_history)
    analysis = analyst_result.messages[-1].content
    print(f"{analysis}\n")

    # 制定策略
    print("📋 Strategist 制定策略:")
    strategist_history = ChatHistory()
    strategist_history.add_user_message(
        f"基於以下分析制定解決策略:\n\n{analysis}"
    )

    strategist_result = await strategist.invoke(strategist_history)
    strategy = strategist_result.messages[-1].content
    print(f"{strategy}\n")

    # 執行計劃
    print("🎯 Implementer 制定執行計劃:")
    implementer_history = ChatHistory()
    implementer_history.add_user_message(
        f"將以下策略轉化為具體行動計劃:\n\n{strategy}"
    )

    implementer_result = await implementer.invoke(implementer_history)
    action_plan = implementer_result.messages[-1].content
    print(f"{action_plan}")


async def example_agent_debate():
    """示例 3: Agent 辯論"""
    print("\n" + "=" * 60)
    print("示例 3: Agent 辯論")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    # 創建正反方 Agent
    pro_agent = ChatCompletionAgent(
        service_id="chat-gpt",
        kernel=kernel,
        name="Pro",
        instructions="""你是正方辯手，支持該論點。
        請提供有力的論據和例證。""",
    )

    con_agent = ChatCompletionAgent(
        service_id="chat-gpt",
        kernel=kernel,
        name="Con",
        instructions="""你是反方辯手，反對該論點。
        請指出問題並提供反駁。""",
    )

    moderator = ChatCompletionAgent(
        service_id="chat-gpt",
        kernel=kernel,
        name="Moderator",
        instructions="""你是主持人，總結雙方觀點並給出平衡的結論。""",
    )

    topic = "遠程工作是否應該成為常態？"
    print(f"💬 辯論主題: {topic}\n")

    # 正方論述
    print("✅ 正方論述:")
    pro_history = ChatHistory()
    pro_history.add_user_message(f"請論述為什麼支持: {topic}")

    pro_result = await pro_agent.invoke(pro_history)
    pro_argument = pro_result.messages[-1].content
    print(f"{pro_argument}\n")

    # 反方論述
    print("❌ 反方論述:")
    con_history = ChatHistory()
    con_history.add_user_message(
        f"請反駁正方的觀點:\n\n正方論點: {pro_argument}"
    )

    con_result = await con_agent.invoke(con_history)
    con_argument = con_result.messages[-1].content
    print(f"{con_argument}\n")

    # 主持人總結
    print("⚖️  主持人總結:")
    moderator_history = ChatHistory()
    moderator_history.add_user_message(
        f"""總結雙方觀點並給出平衡的結論:

正方: {pro_argument}

反方: {con_argument}"""
    )

    moderator_result = await moderator.invoke(moderator_history)
    conclusion = moderator_result.messages[-1].content
    print(f"{conclusion}")


async def example_specialized_team():
    """示例 4: 專業團隊協作"""
    print("\n" + "=" * 60)
    print("示例 4: 專業團隊協作")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    # 創建產品開發團隊
    pm = ChatCompletionAgent(
        service_id="chat-gpt",
        kernel=kernel,
        name="ProductManager",
        instructions="你是產品經理，負責定義產品需求和優先級。",
    )

    designer = ChatCompletionAgent(
        service_id="chat-gpt",
        kernel=kernel,
        name="Designer",
        instructions="你是 UI/UX 設計師，負責設計用戶界面和體驗。",
    )

    developer = ChatCompletionAgent(
        service_id="chat-gpt",
        kernel=kernel,
        name="Developer",
        instructions="你是開發工程師，負責技術實現和架構設計。",
    )

    project = "開發一個 AI 驅動的任務管理應用"
    print(f"🚀 項目: {project}\n")

    # PM 定義需求
    print("📋 Product Manager 定義需求:")
    pm_history = ChatHistory()
    pm_history.add_user_message(f"為以下項目定義核心需求: {project}")

    pm_result = await pm.invoke(pm_history)
    requirements = pm_result.messages[-1].content
    print(f"{requirements}\n")

    # Designer 設計方案
    print("🎨 Designer 設計方案:")
    designer_history = ChatHistory()
    designer_history.add_user_message(
        f"基於以下需求設計 UI/UX 方案:\n\n{requirements}"
    )

    designer_result = await designer.invoke(designer_history)
    design = designer_result.messages[-1].content
    print(f"{design}\n")

    # Developer 技術方案
    print("💻 Developer 技術方案:")
    developer_history = ChatHistory()
    developer_history.add_user_message(
        f"基於以下需求和設計，提出技術實現方案:\n\n需求: {requirements}\n\n設計: {design}"
    )

    developer_result = await developer.invoke(developer_history)
    tech_plan = developer_result.messages[-1].content
    print(f"{tech_plan}")


async def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🚀 Semantic Kernel - 多 Agent 協作示例")
    print("=" * 60)

    try:
        await example_basic_multi_agent()
        await example_collaborative_problem_solving()
        await example_agent_debate()
        await example_specialized_team()

    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ 所有示例運行完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
