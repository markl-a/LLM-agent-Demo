"""
Microsoft Agent Framework - 多 Agent 編排

這個檔案展示如何編排多個 Agent 協同工作,實現複雜的業務流程。
這是 Agent Framework 融合 AutoGen 多 Agent 能力的核心特性。

主要內容:
1. Agent 團隊概念
2. 協作模式 (Sequential, Parallel, Dynamic)
3. Agent 間通信
4. 任務分配和結果聚合
5. 複雜工作流編排
6. 錯誤處理和重試機制
7. 實際應用案例

作者: Microsoft Agent Framework Team
日期: 2025-12-31
版本: 1.0.0
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from dotenv import load_dotenv

# Agent Framework 核心模組
from agent_framework import Agent, AgentThread, AgentTeam
from agent_framework.models import OpenAIModel
from agent_framework.patterns import (
    SequentialPattern,
    ParallelPattern,
    RouterPattern,
    HierarchicalPattern,
)
from agent_framework.messaging import Message, MessageRole

# ============================================================================
# 1. 協作模式定義
# ============================================================================

class CollaborationMode(str, Enum):
    """Agent 協作模式"""
    SEQUENTIAL = "sequential"      # 順序執行
    PARALLEL = "parallel"          # 並行執行
    DYNAMIC_ROUTING = "routing"    # 動態路由
    HIERARCHICAL = "hierarchical"  # 階層式


# ============================================================================
# 2. 專門 Agent 定義
# ============================================================================

def create_researcher_agent(model: OpenAIModel) -> Agent:
    """
    創建研究員 Agent

    負責收集和分析資訊
    """
    def search_web(query: str, max_results: int = 5) -> str:
        """搜尋網路資訊 (模擬)"""
        results = [
            f"搜尋結果 {i+1}: 關於 '{query}' 的資訊..."
            for i in range(min(max_results, 3))
        ]
        return "\n".join(results)

    def analyze_data(data: str) -> Dict[str, Any]:
        """分析資料"""
        return {
            "summary": f"分析了 {len(data)} 個字符的資料",
            "key_points": [
                "要點 1: 資料包含豐富資訊",
                "要點 2: 發現多個重要模式",
                "要點 3: 建議進一步研究"
            ],
            "confidence": 0.85
        }

    agent = Agent(
        name="researcher",
        model=model,
        instructions="""
        你是一位專業的研究員,負責收集和分析資訊。

        你的職責:
        1. 根據主題收集相關資訊
        2. 分析資料並提取關鍵見解
        3. 識別重要模式和趨勢
        4. 提供可靠的參考來源

        工作原則:
        - 資訊要準確可靠
        - 分析要客觀深入
        - 結論要有根據
        - 使用繁體中文

        輸出格式:
        - 研究摘要
        - 關鍵發現
        - 資料來源
        """,
        tools=[search_web, analyze_data]
    )

    return agent


def create_writer_agent(model: OpenAIModel) -> Agent:
    """
    創建寫作 Agent

    負責撰寫和編輯內容
    """
    def format_text(text: str, style: str = "professional") -> str:
        """格式化文字"""
        styles = {
            "professional": "專業風格",
            "casual": "輕鬆風格",
            "technical": "技術風格"
        }
        return f"[{styles.get(style, '一般')}格式]\n{text}"

    def check_grammar(text: str) -> Dict[str, Any]:
        """檢查語法 (模擬)"""
        return {
            "total_words": len(text.split()),
            "issues_found": 0,
            "suggestions": [],
            "grade": "優秀"
        }

    agent = Agent(
        name="writer",
        model=model,
        instructions="""
        你是一位專業作家,負責撰寫高品質的內容。

        你的職責:
        1. 根據研究資料撰寫文章
        2. 確保內容結構清晰
        3. 使用適當的語言風格
        4. 保持內容的可讀性

        寫作原則:
        - 結構清晰,邏輯連貫
        - 語言流暢,用詞精準
        - 觀點明確,論述充分
        - 使用繁體中文

        輸出格式:
        - 標題
        - 前言
        - 主要內容 (分段)
        - 結論
        """,
        tools=[format_text, check_grammar]
    )

    return agent


def create_reviewer_agent(model: OpenAIModel) -> Agent:
    """
    創建審核 Agent

    負責審核和改進內容
    """
    def quality_check(content: str) -> Dict[str, Any]:
        """品質檢查"""
        return {
            "completeness": 0.9,
            "clarity": 0.85,
            "accuracy": 0.95,
            "overall_score": 0.9,
            "feedback": [
                "內容完整性良好",
                "建議加強某些論點的支持",
                "整體品質優秀"
            ]
        }

    agent = Agent(
        name="reviewer",
        model=model,
        instructions="""
        你是一位資深審核員,負責審核內容品質。

        審核標準:
        1. 內容完整性和準確性
        2. 邏輯性和連貫性
        3. 語言品質和可讀性
        4. 格式規範性

        審核流程:
        - 仔細閱讀全文
        - 檢查事實準確性
        - 評估邏輯性
        - 提出改進建議

        回應格式:
        - 總體評價
        - 優點列舉
        - 改進建議
        - 最終評分
        """,
        tools=[quality_check]
    )

    return agent


def create_coordinator_agent(model: OpenAIModel) -> Agent:
    """
    創建協調 Agent

    負責協調其他 Agent 的工作
    """
    agent = Agent(
        name="coordinator",
        model=model,
        instructions="""
        你是專案協調員,負責協調團隊成員的工作。

        你的職責:
        1. 理解整體任務目標
        2. 分配任務給適當的團隊成員
        3. 監控進度和品質
        4. 整合各方成果
        5. 確保按時完成

        協調原則:
        - 清晰的任務分配
        - 有效的溝通
        - 靈活的調整
        - 品質優先

        使用繁體中文溝通。
        """,
        tools=[]
    )

    return agent


# ============================================================================
# 3. 順序協作模式
# ============================================================================

def demonstrate_sequential_pattern():
    """
    示範順序協作模式

    Agent 按照固定順序依次執行,前一個的輸出作為後一個的輸入。
    適用於有明確步驟順序的任務,如研究 -> 撰寫 -> 審核。
    """
    print("\n" + "="*70)
    print("🎯 範例 1: 順序協作模式 (Sequential Pattern)")
    print("="*70)

    load_dotenv()
    model = OpenAIModel(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # 創建 Agent 團隊
    researcher = create_researcher_agent(model)
    writer = create_writer_agent(model)
    reviewer = create_reviewer_agent(model)

    # 創建順序執行的團隊
    team = AgentTeam(
        name="research_team",
        agents=[researcher, writer, reviewer],
        pattern=SequentialPattern(),
        description="按順序執行研究、寫作、審核"
    )

    print(f"\n✅ 創建團隊: {team.name}")
    print(f"   成員: {', '.join([a.name for a in team.agents])}")
    print(f"   模式: 順序執行")

    # 執行任務
    task = "研究 AI Agent 的最新發展趨勢,並撰寫一份報告"

    print(f"\n📋 任務: {task}")
    print("\n執行流程:")
    print("   1. researcher: 收集和分析資訊")
    print("   2. writer: 撰寫報告")
    print("   3. reviewer: 審核報告品質")

    try:
        result = team.run(task=task)

        print("\n✅ 任務完成!")
        print(f"\n最終結果:\n{result}")

    except Exception as e:
        print(f"\n❌ 執行失敗: {str(e)}")


# ============================================================================
# 4. 並行協作模式
# ============================================================================

def demonstrate_parallel_pattern():
    """
    示範並行協作模式

    多個 Agent 同時執行不同的子任務,然後聚合結果。
    適用於可以並行處理的獨立任務。
    """
    print("\n" + "="*70)
    print("🎯 範例 2: 並行協作模式 (Parallel Pattern)")
    print("="*70)

    load_dotenv()
    model = OpenAIModel(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # 創建專門負責不同主題的研究員
    tech_researcher = Agent(
        name="tech_researcher",
        model=model,
        instructions="你是技術研究員,專門研究技術相關主題",
        tools=[]
    )

    market_researcher = Agent(
        name="market_researcher",
        model=model,
        instructions="你是市場研究員,專門研究市場和商業趨勢",
        tools=[]
    )

    user_researcher = Agent(
        name="user_researcher",
        model=model,
        instructions="你是使用者研究員,專門研究用戶需求和體驗",
        tools=[]
    )

    # 創建並行執行的團隊
    team = AgentTeam(
        name="parallel_research_team",
        agents=[tech_researcher, market_researcher, user_researcher],
        pattern=ParallelPattern(aggregator="coordinator"),
        description="並行研究不同面向"
    )

    print(f"\n✅ 創建團隊: {team.name}")
    print(f"   成員: {', '.join([a.name for a in team.agents])}")
    print(f"   模式: 並行執行")

    # 執行任務
    task = "全面分析 AI Agent 市場,包含技術、市場和用戶三個面向"

    print(f"\n📋 任務: {task}")
    print("\n執行流程:")
    print("   - tech_researcher: 技術分析 (並行)")
    print("   - market_researcher: 市場分析 (並行)")
    print("   - user_researcher: 用戶分析 (並行)")
    print("   - 聚合所有結果")

    try:
        # 在實際環境中會真正並行執行
        print("\n⚡ 並行執行中...")
        results = {
            "tech_researcher": "技術分析: AI Agent 框架日益成熟...",
            "market_researcher": "市場分析: 市場規模持續成長...",
            "user_researcher": "用戶分析: 用戶對自動化需求增加..."
        }

        print("\n✅ 所有 Agent 完成!")
        for agent_name, result in results.items():
            print(f"\n{agent_name} 結果:")
            print(f"   {result}")

    except Exception as e:
        print(f"\n❌ 執行失敗: {str(e)}")


# ============================================================================
# 5. 動態路由模式
# ============================================================================

def demonstrate_router_pattern():
    """
    示範動態路由模式

    根據任務內容動態選擇最適合的 Agent 執行。
    適用於處理多樣化任務的場景。
    """
    print("\n" + "="*70)
    print("🎯 範例 3: 動態路由模式 (Router Pattern)")
    print("="*70)

    load_dotenv()
    model = OpenAIModel(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # 創建不同專長的 Agent
    technical_support = Agent(
        name="technical_support",
        model=model,
        instructions="你是技術支援專員,處理技術問題",
        tools=[]
    )

    sales_agent = Agent(
        name="sales_agent",
        model=model,
        instructions="你是業務專員,處理產品諮詢和銷售",
        tools=[]
    )

    customer_service = Agent(
        name="customer_service",
        model=model,
        instructions="你是客服專員,處理一般客戶問題",
        tools=[]
    )

    # 創建路由器 Agent
    router = Agent(
        name="router",
        model=model,
        instructions="""
        你是客服路由器,負責將客戶問題分配給適當的專員。

        分類規則:
        - 技術問題 (bug, 錯誤, 安裝等) -> technical_support
        - 產品諮詢 (功能, 價格, 購買等) -> sales_agent
        - 一般問題 (帳號, 使用方法等) -> customer_service

        請根據問題內容選擇最適合的專員。
        """,
        tools=[]
    )

    # 創建帶路由的團隊
    team = AgentTeam(
        name="customer_service_team",
        agents=[technical_support, sales_agent, customer_service],
        pattern=RouterPattern(router=router),
        description="根據問題類型路由到適當的專員"
    )

    print(f"\n✅ 創建團隊: {team.name}")
    print(f"   路由器: {router.name}")
    print(f"   專員: {', '.join([a.name for a in team.agents])}")

    # 測試不同類型的問題
    test_cases = [
        ("我的程式出現錯誤訊息,無法啟動", "技術問題"),
        ("請問你們的企業版有哪些功能?", "銷售問題"),
        ("我忘記密碼了,如何重設?", "客服問題"),
    ]

    for question, category in test_cases:
        print(f"\n👤 客戶問題 ({category}): {question}")
        print(f"   🔀 路由中...")

        # 模擬路由決策
        if "錯誤" in question or "bug" in question.lower():
            assigned_agent = "technical_support"
        elif "功能" in question or "價格" in question:
            assigned_agent = "sales_agent"
        else:
            assigned_agent = "customer_service"

        print(f"   ✅ 路由至: {assigned_agent}")
        print(f"   🤖 {assigned_agent}: 我來處理這個問題...")


# ============================================================================
# 6. 階層式協作模式
# ============================================================================

def demonstrate_hierarchical_pattern():
    """
    示範階層式協作模式

    具有管理層級的 Agent 架構,上層 Agent 協調下層 Agent。
    適用於複雜的組織化任務。
    """
    print("\n" + "="*70)
    print("🎯 範例 4: 階層式協作模式 (Hierarchical Pattern)")
    print("="*70)

    load_dotenv()
    model = OpenAIModel(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # 底層工作 Agent
    data_collector = Agent(
        name="data_collector",
        model=model,
        instructions="收集原始資料",
        tools=[]
    )

    data_processor = Agent(
        name="data_processor",
        model=model,
        instructions="處理和清理資料",
        tools=[]
    )

    # 中層管理 Agent
    data_manager = Agent(
        name="data_manager",
        model=model,
        instructions="管理資料收集和處理團隊",
        tools=[]
    )

    analyst = Agent(
        name="analyst",
        model=model,
        instructions="分析處理後的資料",
        tools=[]
    )

    visualizer = Agent(
        name="visualizer",
        model=model,
        instructions="視覺化分析結果",
        tools=[]
    )

    # 中層管理 Agent
    analysis_manager = Agent(
        name="analysis_manager",
        model=model,
        instructions="管理分析和視覺化團隊",
        tools=[]
    )

    # 頂層協調 Agent
    project_coordinator = create_coordinator_agent(model)

    print("\n✅ 創建階層式團隊結構:")
    print("\n   頂層:")
    print(f"      {project_coordinator.name} (專案協調員)")
    print("\n   中層:")
    print(f"      {data_manager.name} (資料管理)")
    print(f"      {analysis_manager.name} (分析管理)")
    print("\n   底層:")
    print(f"      {data_collector.name}, {data_processor.name}")
    print(f"      {analyst.name}, {visualizer.name}")

    # 模擬階層式任務執行
    task = "執行完整的資料分析專案"

    print(f"\n📋 任務: {task}")
    print("\n執行流程:")
    print("   1. project_coordinator 分解任務")
    print("   2. data_manager 協調資料收集和處理")
    print("      - data_collector 收集資料")
    print("      - data_processor 處理資料")
    print("   3. analysis_manager 協調分析和視覺化")
    print("      - analyst 分析資料")
    print("      - visualizer 製作圖表")
    print("   4. project_coordinator 整合所有結果")

    print("\n✅ 階層式執行完成!")


# ============================================================================
# 7. 實際應用案例: 內容創作流程
# ============================================================================

def demonstrate_content_creation_workflow():
    """
    完整的內容創作工作流程

    展示如何組合多種模式實現複雜的實際應用
    """
    print("\n" + "="*70)
    print("🎯 實際案例: 自動化內容創作平台")
    print("="*70)

    load_dotenv()
    model = OpenAIModel(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # 創建完整的內容創作團隊
    topic_researcher = create_researcher_agent(model)
    content_writer = create_writer_agent(model)
    editor = create_reviewer_agent(model)
    seo_specialist = Agent(
        name="seo_specialist",
        model=model,
        instructions="優化內容以提高搜尋引擎排名",
        tools=[]
    )

    print("\n✅ 內容創作團隊:")
    print(f"   - {topic_researcher.name}: 主題研究")
    print(f"   - {content_writer.name}: 內容撰寫")
    print(f"   - {editor.name}: 內容審核")
    print(f"   - {seo_specialist.name}: SEO 優化")

    # 完整工作流程
    task = "創作一篇關於 'AI Agent 在企業中的應用' 的文章"

    print(f"\n📋 任務: {task}")
    print("\n🔄 執行完整工作流程:")

    steps = [
        ("1. 主題研究", topic_researcher.name, "收集 AI Agent 企業應用資訊"),
        ("2. 內容撰寫", content_writer.name, "撰寫文章初稿"),
        ("3. 內容審核", editor.name, "審核並提供修改建議"),
        ("4. 修訂內容", content_writer.name, "根據建議修訂"),
        ("5. SEO 優化", seo_specialist.name, "優化關鍵字和結構"),
        ("6. 最終審核", editor.name, "確認最終版本"),
    ]

    for step, agent, description in steps:
        print(f"\n   {step}")
        print(f"      執行者: {agent}")
        print(f"      任務: {description}")
        print(f"      狀態: ✅ 完成")

    print("\n✅ 內容創作流程完成!")
    print("\n📊 產出:")
    print("   - 文章標題: AI Agent 在企業中的應用")
    print("   - 字數: 約 2000 字")
    print("   - 品質評分: 9.0/10")
    print("   - SEO 分數: 85/100")


# ============================================================================
# 8. 錯誤處理和重試機制
# ============================================================================

def demonstrate_error_handling():
    """
    示範多 Agent 協作中的錯誤處理
    """
    print("\n" + "="*70)
    print("🎯 錯誤處理和重試機制")
    print("="*70)

    print("\n💡 多 Agent 系統的錯誤處理策略:")
    print("\n   1. Agent 層級錯誤:")
    print("      - 捕獲單個 Agent 的執行錯誤")
    print("      - 提供降級方案")
    print("      - 記錄錯誤日誌")

    print("\n   2. 團隊層級錯誤:")
    print("      - 重試失敗的步驟")
    print("      - 跳過非關鍵步驟")
    print("      - 通知協調 Agent")

    print("\n   3. 通信錯誤:")
    print("      - 檢測超時")
    print("      - 重新建立連接")
    print("      - 保存中間狀態")

    print("\n   4. 資源錯誤:")
    print("      - 監控 API 配額")
    print("      - 實施速率限制")
    print("      - 使用備用資源")


# ============================================================================
# 9. 主程式
# ============================================================================

def main():
    """主程式"""
    print("="*70)
    print("Microsoft Agent Framework - 多 Agent 編排")
    print("="*70)

    # 執行各種協作模式示範
    demonstrate_sequential_pattern()
    demonstrate_parallel_pattern()
    demonstrate_router_pattern()
    demonstrate_hierarchical_pattern()

    # 實際應用案例
    demonstrate_content_creation_workflow()

    # 錯誤處理
    demonstrate_error_handling()

    print("\n" + "="*70)
    print("✅ 多 Agent 編排示範完成!")
    print("="*70)

    print("\n💡 關鍵要點:")
    print("   1. Sequential: 適合有順序依賴的任務")
    print("   2. Parallel: 適合可獨立執行的子任務")
    print("   3. Router: 適合多樣化的任務類型")
    print("   4. Hierarchical: 適合複雜的組織化任務")
    print("   5. 可以組合多種模式實現複雜工作流")

    print("\n📚 下一步:")
    print("   查看 04_線程管理.py 學習對話狀態管理")


if __name__ == "__main__":
    main()
