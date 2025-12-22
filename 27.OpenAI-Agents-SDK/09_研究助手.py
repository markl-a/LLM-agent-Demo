"""
OpenAI Agents SDK - 研究助手範例

構建一個多步驟研究系統
包含：文獻搜索、數據收集、分析整合、報告生成
"""

import os
from datetime import datetime
from typing import Dict, List
from openai_agents import (
    Agent, tool, handoff_to, Session,
    trace_run, configure
)

# ============================================================================
# 1. 研究工具函數
# ============================================================================

@tool
def搜索學術論文(keywords: str, limit: int = 5) -> List[Dict]:
    """搜索學術論文（模擬）

    Args:
        keywords: 搜索關鍵詞
        limit: 返回結果數量

    Returns:
        論文列表
    """
    # 模擬論文數據
    papers = [
        {
            "title": f"{keywords} 相關研究 1",
            "authors": ["張三", "李四"],
            "year": 2024,
            "abstract": f"這是關於 {keywords} 的重要研究...",
            "citations": 150,
            "url": "https://example.com/paper1"
        },
        {
            "title": f"{keywords} 最新進展",
            "authors": ["王五"],
            "year": 2023,
            "abstract": f"{keywords} 領域的最新突破...",
            "citations": 200,
            "url": "https://example.com/paper2"
        }
    ]

    return papers[:limit]


@tool
def搜索網絡資源(query: str) -> List[Dict]:
    """搜索網絡資源（模擬）

    Args:
        query: 搜索查詢

    Returns:
        資源列表
    """
    resources = [
        {
            "title": f"{query} - 官方文檔",
            "url": "https://docs.example.com",
            "snippet": "官方技術文檔...",
            "relevance": 0.95
        },
        {
            "title": f"{query} 教學",
            "url": "https://tutorial.example.com",
            "snippet": "詳細教學指南...",
            "relevance": 0.87
        }
    ]

    return resources


@tool
def提取關鍵信息(text: str) -> Dict:
    """從文本提取關鍵信息（模擬）

    Args:
        text: 輸入文本

    Returns:
        提取的關鍵信息
    """
    return {
        "keywords": ["AI", "機器學習", "深度學習"],
        "main_points": [
            "神經網絡架構創新",
            "訓練效率提升",
            "應用場景擴展"
        ],
        "statistics": {
            "accuracy": "95%",
            "performance_gain": "30%"
        }
    }


@tool
def數據分析(data: List[Dict]) -> Dict:
    """分析數據集（模擬）

    Args:
        data: 數據列表

    Returns:
        分析結果
    """
    return {
        "total_items": len(data),
        "summary": "數據分析顯示明顯的上升趨勢",
        "key_findings": [
            "發現 1: 研究興趣持續增長",
            "發現 2: 應用範圍不斷擴大",
            "發現 3: 技術成熟度提高"
        ],
        "trends": "整體向好"
    }


@tool
def生成圖表(data_type: str, title: str) -> Dict:
    """生成數據圖表（模擬）

    Args:
        data_type: 圖表類型
        title: 圖表標題

    Returns:
        圖表信息
    """
    return {
        "chart_type": data_type,
        "title": title,
        "file_path": f"/tmp/{title.replace(' ', '_')}.png",
        "status": "已生成"
    }


@tool
def保存研究筆記(topic: str, content: str) -> Dict:
    """保存研究筆記

    Args:
        topic: 主題
        content: 內容

    Returns:
        保存結果
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"research_{topic}_{timestamp}.md"

    return {
        "status": "已保存",
        "filename": filename,
        "path": f"/tmp/{filename}",
        "size": len(content)
    }


# ============================================================================
# 2. 研究 Agents
# ============================================================================

def create_research_system():
    """創建研究助手系統"""

    # 報告生成器
    report_generator = Agent(
        name="報告生成器",
        model="gpt-4",
        instructions="""你是報告生成器，負責：
        1. 整合所有研究發現
        2. 生成結構化報告
        3. 包含引用和參考文獻
        4. 提供結論和建議

        使用繁體中文，格式要專業規範。""",
        tools=[保存研究筆記, 生成圖表]
    )

    # 數據分析師
    def to_reporter():
        return handoff_to(report_generator)

    data_analyst = Agent(
        name="數據分析師",
        model="gpt-4",
        instructions="""你是數據分析師，負責：
        1. 分析收集的數據
        2. 提取關鍵發現
        3. 生成數據可視化
        4. 完成後轉給報告生成器

        使用繁體中文，分析要深入專業。""",
        tools=[數據分析, 提取關鍵信息, 生成圖表, to_reporter]
    )

    # 文獻收集器
    def to_analyst():
        return handoff_to(data_analyst)

    literature_collector = Agent(
        name="文獻收集器",
        model="gpt-4",
        instructions="""你是文獻收集器，負責：
        1. 搜索相關學術論文
        2. 收集網絡資源
        3. 評估資源質量
        4. 完成後轉給數據分析師

        使用繁體中文，搜索要全面準確。""",
        tools=[搜索學術論文, 搜索網絡資源, to_analyst]
    )

    # 研究協調器
    def start_research():
        return handoff_to(literature_collector)

    research_coordinator = Agent(
        name="研究協調器",
        model="gpt-4",
        instructions="""你是研究協調器，負責：
        1. 理解研究主題和目標
        2. 規劃研究步驟
        3. 啟動文獻收集流程

        使用繁體中文，規劃要系統全面。""",
        tools=[start_research]
    )

    return research_coordinator


# ============================================================================
# 3. 研究會話管理
# ============================================================================

class ResearchSession:
    """研究會話管理器"""

    def __init__(self, topic: str):
        self.topic = topic
        self.agent = create_research_system()
        self.session = Session(
            agent=self.agent,
            session_id=f"research_{topic}_{int(datetime.now().timestamp())}",
            metadata={
                "topic": topic,
                "started_at": datetime.now().isoformat(),
                "type": "research"
            }
        )

    def conduct_research(self, query: str) -> str:
        """執行研究"""
        with trace_run(name=f"研究_{self.topic}") as tracer:
            tracer.add_metadata({
                "topic": self.topic,
                "query": query
            })

            tracer.log_event("研究開始")

            response = self.session.run(query)

            tracer.log_event("研究完成")

            # 記錄指標
            tracer.log_metric("total_time", tracer.elapsed_time)
            tracer.log_metric("tokens_used", tracer.total_tokens)

            return response.messages[-1]['content']

    def get_progress(self) -> Dict:
        """獲取研究進度"""
        history = self.session.get_history()

        # 分析已執行的步驟
        tool_calls = []
        for msg in history:
            if msg.get("tool_calls"):
                for tc in msg["tool_calls"]:
                    tool_calls.append(tc["function"]["name"])

        return {
            "total_messages": len(history),
            "tools_used": len(tool_calls),
            "steps_completed": tool_calls
        }


# ============================================================================
# 4. 測試場景
# ============================================================================

def test_simple_research():
    """測試簡單研究"""
    print("\n" + "="*60)
    print("場景 1: 簡單主題研究")
    print("="*60)

    session = ResearchSession(topic="深度學習")

    print("\n研究主題: 深度學習最新進展")

    with trace_run(name="簡單研究") as tracer:
        result = session.conduct_research(
            "研究深度學習在 2024 年的最新進展，生成綜合報告"
        )

    print(f"\n研究結果:")
    print(f"{result[:300]}...")

    print(f"\n性能指標:")
    print(f"  耗時: {tracer.elapsed_time:.2f}s")
    print(f"  Token: {tracer.total_tokens}")

    # 顯示進度
    progress = session.get_progress()
    print(f"\n研究進度:")
    print(f"  總消息數: {progress['total_messages']}")
    print(f"  使用工具數: {progress['tools_used']}")


def test_multi_step_research():
    """測試多步驟研究"""
    print("\n" + "="*60)
    print("場景 2: 多步驟深度研究")
    print("="*60)

    session = ResearchSession(topic="量子計算")

    queries = [
        "第1步：收集量子計算的基礎文獻",
        "第2步：分析當前技術瓶頸",
        "第3步：總結未來發展方向並生成報告"
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{query}")
        result = session.conduct_research(query)
        print(f"結果: {result[:150]}...")

    # 最終進度
    progress = session.get_progress()
    print(f"\n最終進度:")
    print(f"  完成步驟: {progress['steps_completed']}")


def test_comparative_research():
    """測試對比研究"""
    print("\n" + "="*60)
    print("場景 3: 對比研究")
    print("="*60)

    session = ResearchSession(topic="AI框架對比")

    query = """
    對比研究以下 AI 框架：
    1. TensorFlow
    2. PyTorch
    3. JAX

    分析各自的優勢、劣勢和適用場景，生成對比報告。
    """

    print("\n執行對比研究...")
    result = session.conduct_research(query)
    print(f"\n研究結果:")
    print(f"{result[:400]}...")


def test_literature_review():
    """測試文獻綜述"""
    print("\n" + "="*60)
    print("場景 4: 文獻綜述")
    print("="*60)

    session = ResearchSession(topic="自然語言處理")

    query = """
    進行NLP領域的文獻綜述：
    1. 搜索最近3年的重要論文
    2. 分析研究趨勢
    3. 總結關鍵技術進展
    4. 生成文獻綜述報告
    """

    print("\n執行文獻綜述...")

    with trace_run(name="文獻綜述") as tracer:
        result = session.conduct_research(query)

    print(f"\n文獻綜述結果:")
    print(f"{result[:400]}...")

    # 分析工具使用
    timeline = tracer.get_timeline()
    print(f"\n執行時間線: 共 {len(timeline)} 個事件")


def test_data_driven_research():
    """測試數據驅動研究"""
    print("\n" + "="*60)
    print("場景 5: 數據驅動研究")
    print("="*60)

    session = ResearchSession(topic="AI市場趨勢")

    query = """
    基於數據分析AI市場趨勢：
    1. 收集市場數據
    2. 分析增長趨勢
    3. 生成可視化圖表
    4. 預測未來發展
    5. 生成研究報告
    """

    print("\n執行數據驅動研究...")
    result = session.conduct_research(query)

    print(f"\n研究結果:")
    print(f"{result[:400]}...")

    progress = session.get_progress()
    print(f"\n使用的工具:")
    for tool in set(progress['steps_completed']):
        print(f"  - {tool}")


def test_iterative_refinement():
    """測試迭代優化研究"""
    print("\n" + "="*60)
    print("場景 6: 迭代優化")
    print("="*60)

    session = ResearchSession(topic="機器學習優化")

    # 第一輪：初步研究
    print("\n第1輪: 初步研究")
    result1 = session.conduct_research(
        "對機器學習優化算法進行初步研究"
    )
    print(f"結果: {result1[:150]}...")

    # 第二輪：深入分析
    print("\n第2輪: 深入分析")
    result2 = session.conduct_research(
        "基於初步研究，深入分析 Adam 優化器"
    )
    print(f"結果: {result2[:150]}...")

    # 第三輪：生成報告
    print("\n第3輪: 生成最終報告")
    result3 = session.conduct_research(
        "整合前面的研究，生成完整的技術報告"
    )
    print(f"結果: {result3[:150]}...")

    print(f"\n✓ 完成 3 輪迭代研究")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """運行所有測試場景"""
    print("="*60)
    print("OpenAI Agents SDK - 研究助手系統")
    print("="*60)

    configure(
        api_key=os.getenv("OPENAI_API_KEY"),
        timeout=120  # 研究任務可能需要更長時間
    )
    print("✓ 環境配置完成")

    try:
        test_simple_research()
        test_multi_step_research()
        test_comparative_research()
        test_literature_review()
        test_data_driven_research()
        test_iterative_refinement()
    except Exception as e:
        print(f"\n錯誤: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)
    print("所有場景測試完成！")
    print("="*60)

    print("\n研究助手系統特點：")
    print("  ✓ 多階段工作流（收集→分析→報告）")
    print("  ✓ 文獻搜索和資源收集")
    print("  ✓ 數據分析和可視化")
    print("  ✓ 自動生成研究報告")
    print("  ✓ 支持迭代優化")
    print("  ✓ 完整的進度追蹤")

    print("\n應用場景：")
    print("  • 學術研究輔助")
    print("  • 市場分析報告")
    print("  • 技術調研")
    print("  • 競品分析")
    print("  • 文獻綜述")


if __name__ == "__main__":
    main()
