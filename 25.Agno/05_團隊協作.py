"""
05_團隊協作.py - Agno 多 Agent 團隊協作

本範例展示如何使用 Agno 構建多 Agent 協作系統，包括：
- 多 Agent 系統架構
- Agent 角色分工
- 團隊協作模式（順序、並行、階層）
- 任務委派與執行
- 結果聚合與整合
- 團隊工作流設計

作者：LLM-agent-Demo Team
日期：2025-12
框架：Agno (原 Phidata)
"""

import os
from typing import List
from dotenv import load_dotenv

# Agno 核心導入
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.python import PythonTools
from agno.tools.calculator import CalculatorTools

# 載入環境變數
load_dotenv()


# ============================================================================
# 範例 1: 基礎團隊 - 研究與撰寫
# ============================================================================
def example_1_research_writing_team():
    """
    創建研究與撰寫團隊

    角色：
    - 研究員：搜索和收集信息
    - 撰寫員：撰寫文章
    """
    print("\n" + "="*80)
    print("範例 1: 研究與撰寫團隊")
    print("="*80)

    # 1. 創建研究員 Agent
    researcher = Agent(
        name="researcher",
        role="資深研究員",
        model=OpenAIChat(id="gpt-4"),

        tools=[DuckDuckGoTools()],

        instructions=[
            "使用網頁搜索收集準確、最新的信息",
            "從多個來源驗證信息",
            "整理研究發現並提供詳細報告",
            "引用可靠來源"
        ],

        show_tool_calls=True,
        markdown=True
    )

    # 2. 創建撰寫員 Agent
    writer = Agent(
        name="writer",
        role="專業技術作家",
        model=OpenAIChat(id="gpt-4"),

        instructions=[
            "基於研究資料撰寫高質量文章",
            "使用清晰、專業的語言",
            "結構化組織內容",
            "確保邏輯連貫性",
            "使用 Markdown 格式"
        ],

        markdown=True
    )

    # 任務：撰寫關於 AI 的文章
    topic = "Agno 框架的主要優勢"

    print(f"\n任務: 撰寫關於「{topic}」的文章\n")

    # 步驟 1: 研究員收集信息
    print("步驟 1: 研究員收集信息...")
    print("-" * 80)
    research = researcher.run(f"研究並收集關於{topic}的詳細信息")
    print(f"\n研究報告:\n{research.content}\n")

    # 步驟 2: 撰寫員撰寫文章
    print("步驟 2: 撰寫員撰寫文章...")
    print("-" * 80)
    article = writer.run(
        f"基於以下研究資料，撰寫一篇關於「{topic}」的文章：\n\n{research.content}"
    )
    print(f"\n最終文章:\n{article.content}\n")

    return {"research": research.content, "article": article.content}


# ============================================================================
# 範例 2: 並行處理團隊
# ============================================================================
def example_2_parallel_team():
    """
    並行處理：多個 Agent 同時執行不同任務

    應用場景：
    - 多角度分析
    - 並行研究
    - 獨立任務執行
    """
    print("\n" + "="*80)
    print("範例 2: 並行處理團隊")
    print("="*80)

    # 創建多個專業 Agent
    agents = {
        "technical": Agent(
            name="technical_analyst",
            role="技術分析專家",
            model=OpenAIChat(id="gpt-4"),
            instructions=["從技術角度分析", "關注技術實現和性能"]
        ),

        "business": Agent(
            name="business_analyst",
            role="商業分析專家",
            model=OpenAIChat(id="gpt-4"),
            instructions=["從商業角度分析", "關注市場價值和ROI"]
        ),

        "ux": Agent(
            name="ux_analyst",
            role="用戶體驗專家",
            model=OpenAIChat(id="gpt-4"),
            instructions=["從用戶體驗角度分析", "關注易用性和滿意度"]
        )
    }

    # 並行任務
    topic = "Agno 框架"

    print(f"\n任務: 從不同角度分析「{topic}」\n")

    results = {}

    # 並行執行（在實際應用中可以使用異步）
    for name, agent in agents.items():
        print(f"--- {name.upper()} 分析 ---")
        response = agent.run(f"分析{topic}的{agent.role}視角")
        results[name] = response.content
        print(f"{response.content}\n")

    # 綜合報告
    print("--- 綜合報告 ---")
    print("所有分析已完成，可以整合成完整報告\n")

    return results


# ============================================================================
# 範例 3: 階層式團隊 - 經理與專員
# ============================================================================
def example_3_hierarchical_team():
    """
    階層式團隊：經理協調多個專員

    架構：
    - Team Lead（團隊領導）
    - Specialist Agents（專業 Agent）
    """
    print("\n" + "="*80)
    print("範例 3: 階層式團隊")
    print("="*80)

    # 創建專員 Agent
    data_analyst = Agent(
        name="data_analyst",
        role="數據分析專員",
        model=OpenAIChat(id="gpt-4"),
        tools=[PythonTools(), CalculatorTools()],
        instructions=["執行數據分析任務", "使用Python和計算器工具"]
    )

    researcher = Agent(
        name="researcher",
        role="研究專員",
        model=OpenAIChat(id="gpt-4"),
        tools=[DuckDuckGoTools()],
        instructions=["執行研究任務", "收集最新信息"]
    )

    # 創建團隊領導 Agent
    team_lead = Agent(
        name="team_lead",
        role="團隊領導",
        model=OpenAIChat(id="gpt-4"),

        instructions=[
            "協調團隊成員完成任務",
            "分析任務需求並分配給合適的專員",
            "整合團隊成員的工作成果",
            "確保任務高質量完成"
        ],

        markdown=True
    )

    # 複雜任務
    task = "分析 AI 框架市場現狀，包括使用數據和趨勢"

    print(f"\n任務: {task}\n")
    print("團隊領導分析任務...")
    print("-" * 80)

    # 團隊領導的決策
    print("""
    團隊領導決策：
    1. 研究專員 - 搜索 AI 框架市場信息
    2. 數據分析專員 - 分析使用數據和趨勢
    3. 整合所有結果生成報告
    """)

    # 執行子任務（模擬）
    print("\n研究專員執行中...")
    research_result = researcher.run("搜索當前主流 AI 框架的信息")

    print("\n數據分析專員執行中...")
    analysis_result = data_analyst.run("分析AI框架使用趨勢，列出關鍵數據")

    # 團隊領導整合結果
    print("\n團隊領導整合結果...")
    final_report = team_lead.run(
        f"""
        請整合以下團隊成員的工作成果，生成完整報告：

        研究結果：
        {research_result.content}

        數據分析：
        {analysis_result.content}
        """
    )

    print(f"\n最終報告:\n{final_report.content}\n")


# ============================================================================
# 範例 4: 專家小組 - 集體決策
# ============================================================================
def example_4_expert_panel():
    """
    專家小組：多個專家討論並達成共識

    應用場景：
    - 技術評審
    - 決策制定
    - 問題診斷
    """
    print("\n" + "="*80)
    print("範例 4: 專家小組")
    print("="*80)

    # 創建專家小組
    experts = {
        "architect": Agent(
            name="system_architect",
            role="系統架構師",
            model=OpenAIChat(id="gpt-4"),
            instructions=["從架構角度評估", "關注可擴展性和維護性"]
        ),

        "security": Agent(
            name="security_expert",
            role="安全專家",
            model=OpenAIChat(id="gpt-4"),
            instructions=["從安全角度評估", "識別潛在風險"]
        ),

        "performance": Agent(
            name="performance_expert",
            role="性能優化專家",
            model=OpenAIChat(id="gpt-4"),
            instructions=["從性能角度評估", "關注效率和資源使用"]
        )
    }

    # 評審任務
    proposal = "使用 Agno 框架構建企業級 AI 客服系統"

    print(f"\n提案: {proposal}\n")
    print("專家小組評審中...\n")

    opinions = {}

    # 每位專家提供意見
    for name, expert in experts.items():
        print(f"--- {expert.role} 的評估 ---")
        opinion = expert.run(f"評估以下提案：{proposal}")
        opinions[name] = opinion.content
        print(f"{opinion.content}\n")

    # 綜合意見
    print("--- 綜合評審結果 ---")
    print("所有專家意見已收集，可以制定最終決策\n")


# ============================================================================
# 範例 5: 審核與改進流程
# ============================================================================
def example_5_review_improve_flow():
    """
    審核與改進：創作 → 審核 → 改進循環

    流程：
    1. 創作者生成內容
    2. 審核者檢查質量
    3. 編輯者改進內容
    """
    print("\n" + "="*80)
    print("範例 5: 審核與改進流程")
    print("="*80)

    # 創建者
    creator = Agent(
        name="content_creator",
        role="內容創作者",
        model=OpenAIChat(id="gpt-4"),
        instructions=["創作高質量內容", "注重創意和吸引力"]
    )

    # 審核者
    reviewer = Agent(
        name="content_reviewer",
        role="內容審核員",
        model=OpenAIChat(id="gpt-4"),
        instructions=[
            "檢查內容質量",
            "識別錯誤和改進點",
            "提供具體的修改建議"
        ]
    )

    # 編輯者
    editor = Agent(
        name="content_editor",
        role="內容編輯",
        model=OpenAIChat(id="gpt-4"),
        instructions=[
            "基於審核意見改進內容",
            "保持原始創意",
            "提升整體質量"
        ]
    )

    # 內容主題
    topic = "Agno 快速入門指南"

    print(f"\n任務: 創作「{topic}」\n")

    # 第一輪：創作
    print("第一輪：內容創作")
    print("-" * 80)
    draft = creator.run(f"撰寫{topic}")
    print(f"初稿:\n{draft.content}\n")

    # 第二輪：審核
    print("第二輪：內容審核")
    print("-" * 80)
    review = reviewer.run(f"審核以下內容並提供改進建議：\n{draft.content}")
    print(f"審核意見:\n{review.content}\n")

    # 第三輪：改進
    print("第三輪：內容改進")
    print("-" * 80)
    final = editor.run(
        f"基於以下審核意見改進內容：\n\n原文：\n{draft.content}\n\n審核意見：\n{review.content}"
    )
    print(f"最終版本:\n{final.content}\n")


# ============================================================================
# 主函數：運行所有範例
# ============================================================================
def main():
    """運行所有團隊協作範例"""

    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║            Agno 多 Agent 團隊協作完整示範                      ║
    ║                                                                ║
    ║  展示如何構建和管理多 Agent 協作系統                           ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

    # 檢查環境變數
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 錯誤: 請設置 OPENAI_API_KEY 環境變數")
        return

    try:
        # 運行各個範例
        example_1_research_writing_team()
        example_2_parallel_team()
        example_3_hierarchical_team()
        example_4_expert_panel()
        example_5_review_improve_flow()

        print("\n" + "="*80)
        print("✅ 所有範例執行完成！")
        print("="*80)

        print("\n📚 下一步學習：")
        print("- 06_記憶和知識.py - 實現 Agent 記憶系統")
        print("- 07_推理Agent.py - 高級推理能力")
        print("- 08_結構化輸出.py - 使用 Pydantic 模型")

    except Exception as e:
        print(f"\n❌ 執行過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


# ============================================================================
# 學習要點總結
# ============================================================================
"""
📚 Agno 多 Agent 團隊協作學習要點：

1. **團隊協作模式**

   順序執行（Sequential）：
   - Agent A → Agent B → Agent C
   - 適合有依賴關係的任務
   - 例：研究 → 分析 → 撰寫

   並行執行（Parallel）：
   - Agent A、B、C 同時執行
   - 適合獨立任務
   - 例：多角度分析

   階層式（Hierarchical）：
   - Manager → Worker Agents
   - 適合複雜項目
   - 例：項目經理 + 專業團隊

2. **Agent 角色設計**
   ```python
   agent = Agent(
       name="agent_name",      # 唯一標識
       role="agent_role",      # 角色定位
       instructions=[...],     # 具體指導
       tools=[...]            # 專業工具
   )
   ```

3. **任務分配策略**
   - 根據 Agent 專長分配任務
   - 明確輸入和輸出格式
   - 設置任務依賴關係
   - 處理任務失敗和重試

4. **結果整合**
   - 收集所有 Agent 的輸出
   - 使用協調 Agent 整合結果
   - 解決衝突和不一致
   - 生成綜合報告

5. **溝通協議**
   - 標準化輸入/輸出格式
   - 使用 Markdown 或 JSON
   - 明確職責邊界
   - 實施錯誤處理

6. **性能優化**
   - 並行執行獨立任務
   - 緩存中間結果
   - 合理分配資源
   - 監控執行時間

7. **常見團隊模式**

   研究團隊：
   - Researcher + Analyst + Writer

   開發團隊：
   - Architect + Developer + Tester

   創意團隊：
   - Creator + Reviewer + Editor

   決策團隊：
   - Multiple Experts + Coordinator

8. **最佳實踐**
   - 清晰的角色定義
   - 明確的工作流程
   - 完善的錯誤處理
   - 詳細的日誌記錄
   - 結果驗證機制

💡 團隊設計原則：
- 單一職責：每個 Agent 專注一個領域
- 明確接口：標準化輸入輸出
- 鬆散耦合：減少 Agent 間依賴
- 可擴展性：易於添加新 Agent
- 容錯性：處理 Agent 失敗

🔗 相關資源：
- Agno 團隊文檔: https://docs.agno.com/teams
- 工作流設計: https://docs.agno.com/workflows
- 最佳實踐: https://docs.agno.com/teams/best-practices

⚡ 多 Agent 優勢：
- 專業分工提高質量
- 並行處理提升效率
- 互相審核減少錯誤
- 模擬真實團隊協作
"""
