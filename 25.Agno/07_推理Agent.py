"""
07_推理Agent.py - Agno 高級推理 Agent

本範例展示 Agno 的高級推理能力，包括：
- Chain of Thought (CoT) 思維鏈推理
- ReAct (Reasoning + Acting) 模式
- 思維樹（Tree of Thoughts）
- 自我反思（Self-Reflection）
- 計劃與執行（Plan-and-Execute）
- 多步驟推理

作者：LLM-agent-Demo Team
日期：2025-12
框架：Agno (原 Phidata)
"""

import os
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
# 範例 1: Chain of Thought (CoT) 推理
# ============================================================================
def example_1_chain_of_thought():
    """
    Chain of Thought：逐步推理解決問題

    特點：
    - 顯式展示推理過程
    - 提高複雜問題的準確率
    - 可解釋性強
    """
    print("\n" + "="*80)
    print("範例 1: Chain of Thought (CoT) 推理")
    print("="*80)

    # 創建 CoT 推理 Agent
    cot_agent = Agent(
        name="cot_reasoner",
        role="邏輯推理專家",
        model=OpenAIChat(id="gpt-4"),

        instructions=[
            "使用 Chain of Thought 方法解決問題",
            "逐步展示你的推理過程",
            "明確標註每一步的思考",
            "最後給出明確的答案",
            "格式：思考 → 推理 → 結論"
        ],

        markdown=True
    )

    # 測試問題
    problems = [
        """
        問題：如果一個班級有 30 名學生，其中 60% 是女生。
        在女生中，40% 戴眼鏡。請問這個班級有多少名戴眼鏡的女生？
        """,
        """
        問題：Alice 比 Bob 大 5 歲，Bob 比 Charlie 小 3 歲。
        如果 Charlie 25 歲，那麼 Alice 多少歲？
        """,
        """
        問題：一個數字乘以 3，再加 12，結果等於 45。這個數字是多少？
        """
    ]

    for i, problem in enumerate(problems, 1):
        print(f"\n問題 {i}:")
        print(problem.strip())
        print("-" * 80)

        response = cot_agent.run(problem)
        print(f"\n推理過程:\n{response.content}\n")


# ============================================================================
# 範例 2: ReAct 模式 (Reasoning + Acting)
# ============================================================================
def example_2_react_pattern():
    """
    ReAct 模式：推理與行動交替

    流程：
    Thought → Action → Observation →
    Thought → Action → Observation →
    ... → Answer
    """
    print("\n" + "="*80)
    print("範例 2: ReAct 模式")
    print("="*80)

    # 創建 ReAct Agent
    react_agent = Agent(
        name="react_agent",
        role="ReAct 推理專家",
        model=OpenAIChat(id="gpt-4"),

        # 添加工具以支持 Action
        tools=[
            DuckDuckGoTools(),
            CalculatorTools()
        ],

        instructions=[
            "使用 ReAct 模式解決問題",
            "按照：思考（Thought）→ 行動（Action）→ 觀察（Observation）的循環",
            "每一步都明確說明你的思考和行動",
            "根據觀察結果決定下一步",
            "持續迭代直到找到答案"
        ],

        show_tool_calls=True,
        markdown=True
    )

    # 複雜查詢任務
    task = """
    任務：找出 2024 年諾貝爾物理學獎得主，並計算如果他們每人獲得 100 萬美元，
    總共需要多少獎金（假設有多位得主平分）。
    """

    print(f"\n任務:\n{task}")
    print("-" * 80)

    response = react_agent.run(task)
    print(f"\nReAct 推理過程:\n{response.content}\n")


# ============================================================================
# 範例 3: 計劃與執行 (Plan-and-Execute)
# ============================================================================
def example_3_plan_and_execute():
    """
    計劃與執行：先制定計劃，再逐步執行

    優勢：
    - 結構化解決複雜問題
    - 可追蹤執行進度
    - 易於調整和優化
    """
    print("\n" + "="*80)
    print("範例 3: 計劃與執行")
    print("="*80)

    # 計劃 Agent
    planner = Agent(
        name="planner",
        role="任務規劃專家",
        model=OpenAIChat(id="gpt-4"),

        instructions=[
            "分析任務並制定詳細計劃",
            "將複雜任務分解為具體步驟",
            "為每個步驟分配優先級",
            "考慮步驟之間的依賴關係",
            "輸出結構化的執行計劃"
        ],

        markdown=True
    )

    # 執行 Agent
    executor = Agent(
        name="executor",
        role="任務執行專員",
        model=OpenAIChat(id="gpt-4"),

        tools=[
            DuckDuckGoTools(),
            PythonTools(),
            CalculatorTools()
        ],

        instructions=[
            "按照計劃逐步執行任務",
            "完成每個步驟並報告結果",
            "使用可用工具完成任務",
            "記錄執行過程和結果"
        ],

        show_tool_calls=True,
        markdown=True
    )

    # 複雜任務
    complex_task = """
    撰寫一份關於「AI Agent 框架對比」的簡報，包括：
    1. 市場上主要的 AI Agent 框架
    2. 它們的性能對比
    3. 各自的優缺點
    4. 使用建議
    """

    print(f"\n任務:\n{complex_task}")
    print("\n" + "="*80)

    # 步驟 1: 制定計劃
    print("\n步驟 1: 制定執行計劃")
    print("-" * 80)
    plan = planner.run(f"請為以下任務制定詳細的執行計劃：\n{complex_task}")
    print(f"\n執行計劃:\n{plan.content}\n")

    # 步驟 2: 執行計劃
    print("步驟 2: 執行計劃")
    print("-" * 80)
    result = executor.run(
        f"請根據以下計劃完成任務：\n\n計劃：\n{plan.content}\n\n原始任務：\n{complex_task}"
    )
    print(f"\n執行結果:\n{result.content}\n")


# ============================================================================
# 範例 4: 自我反思 (Self-Reflection)
# ============================================================================
def example_4_self_reflection():
    """
    自我反思：Agent 評估和改進自己的輸出

    流程：
    Generate → Reflect → Improve → Validate
    """
    print("\n" + "="*80)
    print("範例 4: 自我反思")
    print("="*80)

    # 創作 Agent
    creator = Agent(
        name="creator",
        role="內容創作者",
        model=OpenAIChat(id="gpt-4"),
        instructions=["創作高質量內容"],
        markdown=True
    )

    # 反思 Agent
    reflector = Agent(
        name="reflector",
        role="自我反思評論家",
        model=OpenAIChat(id="gpt-4"),

        instructions=[
            "批判性地評估內容",
            "識別問題和改進空間",
            "提供具體的改進建議",
            "評分並說明理由（1-10 分）"
        ],

        markdown=True
    )

    # 改進 Agent
    improver = Agent(
        name="improver",
        role="內容改進專家",
        model=OpenAIChat(id="gpt-4"),

        instructions=[
            "基於反思意見改進內容",
            "保持核心思想不變",
            "提升質量和清晰度"
        ],

        markdown=True
    )

    # 任務
    topic = "解釋什麼是 Agno 框架"

    print(f"\n任務: {topic}\n")

    # 迭代改進（最多 2 輪）
    current_content = None

    for iteration in range(1, 3):
        print(f"\n--- 第 {iteration} 輪 ---\n")

        # 創作/改進
        if iteration == 1:
            print("步驟 1: 初始創作")
            print("-" * 80)
            response = creator.run(topic)
            current_content = response.content
        else:
            print("步驟 1: 內容改進")
            print("-" * 80)
            response = improver.run(
                f"根據以下反思意見改進內容：\n\n原內容：\n{current_content}\n\n反思意見：\n{reflection}"
            )
            current_content = response.content

        print(f"\n內容:\n{current_content}\n")

        # 反思
        print("步驟 2: 自我反思")
        print("-" * 80)
        reflection_response = reflector.run(
            f"評估以下內容並提供改進建議：\n\n{current_content}"
        )
        reflection = reflection_response.content
        print(f"\n反思:\n{reflection}\n")

    print("最終內容已生成並優化\n")


# ============================================================================
# 範例 5: 思維樹 (Tree of Thoughts)
# ============================================================================
def example_5_tree_of_thoughts():
    """
    思維樹：探索多條推理路徑

    流程：
    1. 生成多個可能的解決方案
    2. 評估每個方案
    3. 選擇最佳方案或組合方案
    """
    print("\n" + "="*80)
    print("範例 5: 思維樹 (Tree of Thoughts)")
    print("="*80)

    # 創意生成 Agent
    ideator = Agent(
        name="ideator",
        role="創意生成專家",
        model=OpenAIChat(id="gpt-4"),
        instructions=["生成多個創新的解決方案"],
        markdown=True
    )

    # 評估 Agent
    evaluator = Agent(
        name="evaluator",
        role="方案評估專家",
        model=OpenAIChat(id="gpt-4"),

        instructions=[
            "評估每個方案的可行性",
            "考慮優缺點",
            "給出評分和理由"
        ],

        markdown=True
    )

    # 綜合 Agent
    synthesizer = Agent(
        name="synthesizer",
        role="方案綜合專家",
        model=OpenAIChat(id="gpt-4"),

        instructions=[
            "綜合所有方案",
            "選擇最佳方案或組合多個方案",
            "提供最終建議"
        ],

        markdown=True
    )

    # 問題
    problem = "如何提高 AI Agent 的推理能力？"

    print(f"\n問題: {problem}\n")

    # 步驟 1: 生成多個方案
    print("步驟 1: 生成創意方案")
    print("-" * 80)
    ideas = ideator.run(f"針對問題「{problem}」，生成 3 個不同的解決方案")
    print(f"\n方案:\n{ideas.content}\n")

    # 步驟 2: 評估方案
    print("步驟 2: 評估各個方案")
    print("-" * 80)
    evaluation = evaluator.run(f"評估以下方案：\n\n{ideas.content}")
    print(f"\n評估:\n{evaluation.content}\n")

    # 步驟 3: 綜合最佳方案
    print("步驟 3: 綜合最佳方案")
    print("-" * 80)
    final = synthesizer.run(
        f"基於以下評估，提供最終建議：\n\n{evaluation.content}"
    )
    print(f"\n最終建議:\n{final.content}\n")


# ============================================================================
# 主函數：運行所有範例
# ============================================================================
def main():
    """運行所有推理範例"""

    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║            Agno 高級推理 Agent 完整示範                        ║
    ║                                                                ║
    ║  展示 CoT、ReAct、思維樹等高級推理技術                         ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

    # 檢查環境變數
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 錯誤: 請設置 OPENAI_API_KEY 環境變數")
        return

    try:
        # 運行各個範例
        example_1_chain_of_thought()
        example_2_react_pattern()
        example_3_plan_and_execute()
        example_4_self_reflection()
        example_5_tree_of_thoughts()

        print("\n" + "="*80)
        print("✅ 所有範例執行完成！")
        print("="*80)

        print("\n📚 下一步學習：")
        print("- 08_結構化輸出.py - 使用 Pydantic 模型")
        print("- 09_AgentOS部署.py - 生產環境部署")
        print("- 10_MCP整合.py - Model Context Protocol")

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
📚 Agno 高級推理學習要點：

1. **Chain of Thought (CoT)**
   ```
   問題 → 思考步驟1 → 思考步驟2 → ... → 結論
   ```
   - 顯式推理過程
   - 提高準確率
   - 可解釋性強

2. **ReAct 模式**
   ```
   循環：Thought → Action → Observation
   ```
   - 推理與行動交替
   - 動態調整策略
   - 適合複雜任務

3. **Plan-and-Execute**
   ```
   Planning → Execution → Monitoring → Completion
   ```
   - 結構化問題解決
   - 可追蹤進度
   - 易於調試

4. **Self-Reflection**
   ```
   Generate → Reflect → Improve → Validate
   ```
   - 自我評估
   - 持續改進
   - 提升質量

5. **Tree of Thoughts**
   ```
   Generate Multiple Paths → Evaluate → Select Best
   ```
   - 探索多條路徑
   - 並行評估
   - 選擇最優方案

6. **推理提示詞設計**
   ```python
   agent = Agent(
       instructions=[
           "逐步分析問題",
           "展示推理過程",
           "驗證每一步的正確性",
           "給出明確結論"
       ]
   )
   ```

7. **多 Agent 推理**
   - Planner：制定計劃
   - Executor：執行任務
   - Reflector：評估反思
   - Synthesizer：綜合結果

8. **推理優化技巧**
   - 明確推理步驟
   - 使用結構化格式
   - 中間結果驗證
   - 錯誤檢測和修正
   - 多輪迭代改進

💡 最佳實踐：
- 選擇適合的推理模式
- 明確展示推理過程
- 實施質量驗證
- 組合多種推理技術
- 記錄推理軌跡

🔗 相關資源：
- CoT 論文: https://arxiv.org/abs/2201.11903
- ReAct 論文: https://arxiv.org/abs/2210.03629
- Tree of Thoughts: https://arxiv.org/abs/2305.10601

⚡ 推理能力優勢：
- 處理複雜問題
- 提高準確率
- 增強可解釋性
- 支持多步驟任務
"""
