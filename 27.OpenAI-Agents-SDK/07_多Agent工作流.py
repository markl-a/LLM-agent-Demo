"""
OpenAI Agents SDK - 多 Agent 工作流範例

展示複雜的多 Agent 協作場景
包含：流水線工作流、並行處理、層級結構、決策樹
"""

import os
from openai_agents import Agent, tool, handoff_to, run, Session, trace_run, configure

# ============================================================================
# 1. 流水線工作流（Pipeline）
# ============================================================================

def create_pipeline_workflow():
    """創建流水線工作流：數據收集 → 分析 → 報告"""

    # 階段 3：報告生成器
    reporter = Agent(
        name="報告生成器",
        model="gpt-4",
        instructions="""你是報告生成器，負責：
        1. 整理分析結果
        2. 生成專業報告
        3. 使用繁體中文
        """
    )

    # 階段 2：數據分析師
    def to_reporter():
        return handoff_to(reporter)

    analyst = Agent(
        name="數據分析師",
        model="gpt-4",
        instructions="""你是數據分析師，負責：
        1. 分析收集的數據
        2. 提取關鍵洞察
        3. 完成後轉給報告生成器
        使用繁體中文。""",
        tools=[to_reporter]
    )

    # 階段 1：數據收集器
    def to_analyst():
        return handoff_to(analyst)

    collector = Agent(
        name="數據收集器",
        model="gpt-4",
        instructions="""你是數據收集器，負責：
        1. 收集相關數據
        2. 整理數據格式
        3. 完成後轉給分析師
        使用繁體中文。""",
        tools=[to_analyst]
    )

    return collector


def test_pipeline():
    """測試流水線工作流"""
    print("\n" + "="*60)
    print("範例 1: 流水線工作流")
    print("="*60)

    pipeline = create_pipeline_workflow()

    with trace_run(name="流水線執行") as tracer:
        response = run(
            agent=pipeline,
            messages=[{"role": "user", "content": "分析 2024 年 Q1 銷售數據並生成報告"}]
        )

    print(f"\n最終處理者: {response.agent.name}")
    print(f"執行時間: {tracer.elapsed_time:.2f}s")
    print(f"Token 使用: {tracer.total_tokens}")


# ============================================================================
# 2. 並行處理工作流
# ============================================================================

@tool
def analyze_text(text: str) -> dict:
    """分析文本"""
    return {"analysis": f"已分析: {text}", "sentiment": "positive"}


@tool
def translate_text(text: str, target: str = "en") -> dict:
    """翻譯文本"""
    return {"translated": f"Translated: {text}", "language": target}


@tool
def summarize_text(text: str) -> dict:
    """摘要文本"""
    return {"summary": f"摘要: {text}"}


def create_parallel_workflow():
    """創建並行處理工作流"""

    # 匯總 Agent
    aggregator = Agent(
        name="結果匯總",
        model="gpt-4",
        instructions="整合所有處理結果，生成綜合報告。使用繁體中文。"
    )

    # 並行處理 Agents
    text_analyzer = Agent(
        name="文本分析",
        model="gpt-4",
        instructions="執行文本分析。使用繁體中文。",
        tools=[analyze_text]
    )

    translator = Agent(
        name="翻譯服務",
        model="gpt-4",
        instructions="執行文本翻譯。使用繁體中文。",
        tools=[translate_text]
    )

    summarizer = Agent(
        name="摘要生成",
        model="gpt-4",
        instructions="生成文本摘要。使用繁體中文。",
        tools=[summarize_text]
    )

    # 路由 Agent
    def to_analyzer():
        return handoff_to(text_analyzer)

    def to_translator():
        return handoff_to(translator)

    def to_summarizer():
        return handoff_to(summarizer)

    router = Agent(
        name="任務路由",
        model="gpt-4",
        instructions="""分析用戶需求，分配給合適的處理器：
        - 分析任務 → 文本分析
        - 翻譯任務 → 翻譯服務
        - 摘要任務 → 摘要生成
        使用繁體中文。""",
        tools=[to_analyzer, to_translator, to_summarizer]
    )

    return router


def test_parallel():
    """測試並行工作流"""
    print("\n" + "="*60)
    print("範例 2: 並行處理工作流")
    print("="*60)

    router = create_parallel_workflow()

    tasks = [
        "分析這段文字的情感",
        "將這段話翻譯成英文",
        "生成這篇文章的摘要"
    ]

    for task in tasks:
        print(f"\n任務: {task}")
        response = run(agent=router, messages=[{"role": "user", "content": task}])
        print(f"處理者: {response.agent.name}")


# ============================================================================
# 3. 層級結構工作流
# ============================================================================

def create_hierarchical_workflow():
    """創建層級結構：經理 → 主管 → 員工"""

    # 員工層
    junior_dev = Agent(
        name="初級工程師",
        model="gpt-4",
        instructions="處理簡單的開發任務。使用繁體中文。"
    )

    senior_dev = Agent(
        name="高級工程師",
        model="gpt-4",
        instructions="處理複雜的技術問題。使用繁體中文。"
    )

    # 主管層
    def to_junior():
        return handoff_to(junior_dev)

    def to_senior():
        return handoff_to(senior_dev)

    tech_lead = Agent(
        name="技術主管",
        model="gpt-4",
        instructions="""分配技術任務：
        - 簡單任務 → 初級工程師
        - 複雜任務 → 高級工程師
        使用繁體中文。""",
        tools=[to_junior, to_senior]
    )

    # 經理層
    def to_tech_lead():
        return handoff_to(tech_lead)

    manager = Agent(
        name="項目經理",
        model="gpt-4",
        instructions="""處理項目管理和任務分配。
        技術任務轉給技術主管。
        使用繁體中文。""",
        tools=[to_tech_lead]
    )

    return manager


def test_hierarchical():
    """測試層級工作流"""
    print("\n" + "="*60)
    print("範例 3: 層級結構工作流")
    print("="*60)

    manager = create_hierarchical_workflow()

    requests = [
        "修復一個簡單的 UI bug",
        "設計一個高性能的分布式系統"
    ]

    for req in requests:
        print(f"\n需求: {req}")
        response = run(agent=manager, messages=[{"role": "user", "content": req}])
        print(f"最終處理者: {response.agent.name}")


# ============================================================================
# 4. 決策樹工作流
# ============================================================================

def create_decision_tree():
    """創建決策樹工作流"""

    # 葉子節點 Agents
    refund_agent = Agent(
        name="退款處理",
        model="gpt-4",
        instructions="處理退款請求。使用繁體中文。"
    )

    exchange_agent = Agent(
        name="換貨處理",
        model="gpt-4",
        instructions="處理換貨請求。使用繁體中文。"
    )

    repair_agent = Agent(
        name="維修服務",
        model="gpt-4",
        instructions="處理維修請求。使用繁體中文。"
    )

    complaint_agent = Agent(
        name="投訴處理",
        model="gpt-4",
        instructions="處理客戶投訴。使用繁體中文。"
    )

    # 決策函數
    def route_by_issue_type(issue_type: str):
        """根據問題類型路由"""
        routes = {
            "退款": refund_agent,
            "換貨": exchange_agent,
            "維修": repair_agent,
            "投訴": complaint_agent
        }

        for key, agent in routes.items():
            if key in issue_type:
                print(f"  → 路由到: {agent.name}")
                return handoff_to(agent)

        return handoff_to(complaint_agent)  # 默認

    # 決策路由器
    decision_router = Agent(
        name="智能路由",
        model="gpt-4",
        instructions="""分析客戶問題，識別類型（退款/換貨/維修/投訴），
        然後路由到合適的處理部門。使用繁體中文。""",
        tools=[route_by_issue_type]
    )

    return decision_router


def test_decision_tree():
    """測試決策樹"""
    print("\n" + "="*60)
    print("範例 4: 決策樹工作流")
    print("="*60)

    router = create_decision_tree()

    cases = [
        "我要退款",
        "商品壞了需要換貨",
        "手機需要維修",
        "對服務不滿意，要投訴"
    ]

    for case in cases:
        print(f"\n客戶: {case}")
        response = run(agent=router, messages=[{"role": "user", "content": case}])
        print(f"處理部門: {response.agent.name}")


# ============================================================================
# 5. 循環工作流（迭代優化）
# ============================================================================

def create_iterative_workflow():
    """創建迭代優化工作流：生成 → 審查 → 改進"""

    iteration_count = {"count": 0}

    # 生成器
    generator = Agent(
        name="內容生成器",
        model="gpt-4",
        instructions="生成內容初稿。使用繁體中文。"
    )

    # 改進器
    def back_to_generator():
        iteration_count["count"] += 1
        if iteration_count["count"] < 3:  # 最多 3 次迭代
            print(f"  ↻ 第 {iteration_count['count']} 次迭代")
            return handoff_to(generator)
        else:
            print("  ✓ 達到最大迭代次數")
            return None

    improver = Agent(
        name="內容改進",
        model="gpt-4",
        instructions="改進內容質量。如需要可返回生成器。使用繁體中文。",
        tools=[back_to_generator]
    )

    # 審查器
    def to_improver():
        return handoff_to(improver)

    def approve():
        print("  ✓ 內容已批准")
        return None

    reviewer = Agent(
        name="內容審查",
        model="gpt-4",
        instructions="""審查內容質量。
        如果需要改進，轉給改進器。
        否則批准。使用繁體中文。""",
        tools=[to_improver, approve]
    )

    # 將審查器連接到生成器
    def to_reviewer():
        return handoff_to(reviewer)

    generator.tools = [to_reviewer]

    return generator


def test_iterative():
    """測試迭代工作流"""
    print("\n" + "="*60)
    print("範例 5: 迭代優化工作流")
    print("="*60)

    workflow = create_iterative_workflow()

    response = run(
        agent=workflow,
        messages=[{"role": "user", "content": "寫一篇關於 AI 的文章"}]
    )

    print(f"\n最終狀態: {response.agent.name}")


# ============================================================================
# 6. 完整企業工作流
# ============================================================================

def create_enterprise_workflow():
    """創建完整的企業級工作流"""

    # 專業團隊
    sales = Agent(name="銷售", model="gpt-4", instructions="處理銷售。使用繁體中文。")
    tech = Agent(name="技術支持", model="gpt-4", instructions="技術支持。使用繁體中文。")
    billing = Agent(name="財務", model="gpt-4", instructions="處理帳務。使用繁體中文。")
    legal = Agent(name="法務", model="gpt-4", instructions="法律諮詢。使用繁體中文。")

    # 路由工具
    def to_sales():
        return handoff_to(sales)

    def to_tech():
        return handoff_to(tech)

    def to_billing():
        return handoff_to(billing)

    def to_legal():
        return handoff_to(legal)

    # 總機
    receptionist = Agent(
        name="智能總機",
        model="gpt-4",
        instructions="""根據客戶需求路由：
        - 產品購買、報價 → 銷售
        - 技術問題、故障 → 技術支持
        - 帳單、付款 → 財務
        - 合約、法律 → 法務
        使用繁體中文。""",
        tools=[to_sales, to_tech, to_billing, to_legal]
    )

    return receptionist


def test_enterprise():
    """測試企業工作流"""
    print("\n" + "="*60)
    print("範例 6: 企業級工作流")
    print("="*60)

    system = create_enterprise_workflow()

    session = Session(agent=system, session_id="enterprise_demo")

    scenarios = [
        "我想購買你們的企業版產品",
        "系統無法登錄，需要技術支持",
        "帳單有誤，需要核對",
        "合約條款需要法律意見"
    ]

    for scenario in scenarios:
        print(f"\n場景: {scenario}")
        response = session.run(scenario)
        print(f"處理部門: {response.agent.name}")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """運行所有範例"""
    print("="*60)
    print("OpenAI Agents SDK - 多 Agent 工作流範例")
    print("="*60)

    configure(
        api_key=os.getenv("OPENAI_API_KEY"),
        timeout=60
    )
    print("✓ 環境配置完成")

    try:
        test_pipeline()
        test_parallel()
        test_hierarchical()
        test_decision_tree()
        test_iterative()
        test_enterprise()
    except Exception as e:
        print(f"\n錯誤: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)
    print("所有範例運行完成！")
    print("="*60)

    print("\n工作流設計模式：")
    print("  1. 流水線：順序處理，層層推進")
    print("  2. 並行：同時處理，提高效率")
    print("  3. 層級：分級管理，職責明確")
    print("  4. 決策樹：智能路由，精準分配")
    print("  5. 迭代：循環優化，持續改進")
    print("  6. 企業級：綜合應用，完整閉環")


if __name__ == "__main__":
    main()
