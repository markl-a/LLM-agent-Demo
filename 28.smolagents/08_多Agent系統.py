"""
多 Agent 系統 - Agent 協作
=========================

單個 Agent 很強大，多個 Agent 協作更強大！

本範例展示：
1. 多 Agent 協作模式
2. 專業化 Agent
3. Manager-Worker 模式
4. 協作工作流
5. Agent 通信
"""

from smolagents import CodeAgent, ToolCallingAgent, HfApiModel, tool
from typing import List, Dict


# ============================================================================
# 準備專業化工具
# ============================================================================

# 研究 Agent 的工具
@tool
def search_web(query: str) -> str:
    """
    搜索網頁（模擬）

    Args:
        query: 搜索查詢

    Returns:
        搜索結果摘要
    """
    return f"關於 '{query}' 的搜索結果：找到了相關的最新信息和研究資料。"


@tool
def read_paper(title: str) -> str:
    """
    閱讀學術論文（模擬）

    Args:
        title: 論文標題

    Returns:
        論文摘要
    """
    return f"論文《{title}》的主要發現：提出了新的方法並取得了顯著成果。"


# 寫作 Agent 的工具
@tool
def write_section(title: str, content: str) -> str:
    """
    撰寫文章段落

    Args:
        title: 段落標題
        content: 段落內容

    Returns:
        格式化的段落
    """
    return f"## {title}\n\n{content}\n"


@tool
def format_document(sections: List[str]) -> str:
    """
    格式化完整文檔

    Args:
        sections: 段落列表

    Returns:
        完整文檔
    """
    return "\n".join(sections)


# 審核 Agent 的工具
@tool
def check_grammar(text: str) -> Dict[str, any]:
    """
    檢查語法（模擬）

    Args:
        text: 要檢查的文本

    Returns:
        檢查結果
    """
    return {
        "errors": 2,
        "warnings": 3,
        "suggestions": ["建議使用更正式的用詞", "段落結構可以優化"]
    }


@tool
def check_facts(text: str) -> Dict[str, any]:
    """
    事實核查（模擬）

    Args:
        text: 要檢查的文本

    Returns:
        核查結果
    """
    return {
        "verified": True,
        "confidence": 0.95,
        "notes": "所有引用的數據和事實都已驗證"
    }


# ============================================================================
# 範例 1: 專業化 Agent
# ============================================================================

def example_1_specialized_agents():
    """創建專業化的 Agent"""
    print("\n" + "="*70)
    print("範例 1: 專業化 Agent")
    print("="*70)

    model = HfApiModel()

    # 研究 Agent
    researcher = CodeAgent(
        tools=[search_web, read_paper],
        model=model,
        max_steps=5
    )

    # 寫作 Agent
    writer = CodeAgent(
        tools=[write_section, format_document],
        model=model,
        max_steps=5
    )

    # 審核 Agent
    reviewer = CodeAgent(
        tools=[check_grammar, check_facts],
        model=model,
        max_steps=5
    )

    print("\n創建了三個專業化 Agent：")
    print("  1. 研究 Agent - 搜索和閱讀資料")
    print("  2. 寫作 Agent - 撰寫和格式化")
    print("  3. 審核 Agent - 檢查和驗證\n")

    # 模擬工作流
    print("工作流程：")
    print("  研究 Agent → 收集信息")
    research_result = researcher.run("研究 AI Agent 的最新發展")
    print(f"  研究結果: {research_result[:100]}...")

    print("\n  寫作 Agent → 撰寫文章")
    article = writer.run(f"根據這些研究撰寫一篇文章：{research_result}")
    print(f"  文章: {article[:100]}...")

    print("\n  審核 Agent → 檢查質量")
    review = reviewer.run(f"審核這篇文章：{article}")
    print(f"  審核結果: {review[:100]}...")


# ============================================================================
# 範例 2: Manager-Worker 模式
# ============================================================================

class ManagerWorkerSystem:
    """Manager-Worker 多 Agent 系統"""

    def __init__(self):
        self.model = HfApiModel()

        # Manager Agent - 協調整體任務
        self.manager = CodeAgent(
            tools=[],
            model=self.model,
            max_steps=10
        )

        # Worker Agents - 執行具體任務
        self.workers = {
            "researcher": CodeAgent(
                tools=[search_web, read_paper],
                model=self.model,
                max_steps=5
            ),
            "writer": CodeAgent(
                tools=[write_section],
                model=self.model,
                max_steps=5
            ),
            "reviewer": CodeAgent(
                tools=[check_grammar, check_facts],
                model=self.model,
                max_steps=5
            ),
        }

    def execute_task(self, task: str) -> str:
        """
        執行複雜任務

        Args:
            task: 任務描述

        Returns:
            執行結果
        """
        print(f"\nManager: 分析任務 '{task}'")

        # Manager 分解任務
        subtasks = [
            ("researcher", "收集相關資料"),
            ("writer", "撰寫初稿"),
            ("reviewer", "審核並改進"),
        ]

        results = []
        for worker_name, subtask in subtasks:
            print(f"\n  → 分配給 {worker_name}: {subtask}")
            worker = self.workers[worker_name]
            result = worker.run(subtask)
            results.append(result)
            print(f"  ← {worker_name} 完成")

        # Manager 整合結果
        final_result = "\n\n".join(results)
        return final_result


def example_2_manager_worker():
    """Manager-Worker 模式"""
    print("\n" + "="*70)
    print("範例 2: Manager-Worker 模式")
    print("="*70)

    print("\nManager-Worker 模式特點：")
    print("  - Manager 負責任務分解和協調")
    print("  - Worker 負責執行具體子任務")
    print("  - 清晰的責任劃分")
    print("  - 可擴展性強\n")

    system = ManagerWorkerSystem()
    result = system.execute_task("創建一篇關於 AI 的技術文章")

    print(f"\n最終結果:\n{result[:200]}...")


# ============================================================================
# 範例 3: 流水線協作
# ============================================================================

class AgentPipeline:
    """Agent 流水線"""

    def __init__(self):
        self.model = HfApiModel()

        self.stages = [
            CodeAgent(tools=[search_web], model=self.model, max_steps=3),
            CodeAgent(tools=[write_section], model=self.model, max_steps=3),
            CodeAgent(tools=[check_grammar], model=self.model, max_steps=3),
        ]

    def run(self, initial_input: str) -> str:
        """
        運行流水線

        Args:
            initial_input: 初始輸入

        Returns:
            最終輸出
        """
        current_output = initial_input

        for i, agent in enumerate(self.stages, 1):
            print(f"\n階段 {i}: 處理中...")
            current_output = agent.run(current_output)
            print(f"階段 {i}: 完成")

        return current_output


def example_3_pipeline():
    """流水線協作"""
    print("\n" + "="*70)
    print("範例 3: 流水線協作")
    print("="*70)

    print("\n流水線模式：")
    print("  輸入 → Agent1 → Agent2 → Agent3 → 輸出")
    print("  每個 Agent 處理上一個 Agent 的輸出\n")

    pipeline = AgentPipeline()
    result = pipeline.run("研究量子計算的應用")

    print(f"\n最終輸出: {result[:200]}...")


# ============================================================================
# 範例 4: 並行協作
# ============================================================================

def example_4_parallel_agents():
    """並行 Agent 協作"""
    print("\n" + "="*70)
    print("範例 4: 並行協作")
    print("="*70)

    print("\n並行模式：")
    print("  輸入 → [Agent1, Agent2, Agent3] → 聚合 → 輸出")
    print("  多個 Agent 同時處理同一任務的不同方面\n")

    model = HfApiModel()

    # 創建多個 Agent 處理不同方面
    agents = {
        "技術": CodeAgent(tools=[search_web], model=model, max_steps=3),
        "應用": CodeAgent(tools=[search_web], model=model, max_steps=3),
        "趨勢": CodeAgent(tools=[search_web], model=model, max_steps=3),
    }

    task = "分析 AI Agent 技術"
    results = {}

    print("並行執行中...")
    for aspect, agent in agents.items():
        print(f"  {aspect} Agent 處理中...")
        results[aspect] = agent.run(f"從{aspect}角度分析：{task}")
        print(f"  {aspect} Agent 完成")

    # 聚合結果
    print("\n聚合結果:")
    for aspect, result in results.items():
        print(f"\n{aspect}方面:")
        print(f"  {result[:100]}...")


# ============================================================================
# 範例 5: Agent 間通信
# ============================================================================

class CommunicatingAgent:
    """可以通信的 Agent"""

    def __init__(self, name: str, tools: list):
        self.name = name
        self.model = HfApiModel()
        self.agent = CodeAgent(tools=tools, model=self.model, max_steps=5)
        self.inbox = []

    def send_message(self, recipient: 'CommunicatingAgent', message: str):
        """發送消息給另一個 Agent"""
        print(f"\n📨 {self.name} → {recipient.name}: {message[:50]}...")
        recipient.inbox.append({
            "from": self.name,
            "message": message
        })

    def receive_messages(self) -> List[Dict]:
        """接收消息"""
        messages = self.inbox.copy()
        self.inbox.clear()
        return messages

    def run(self, task: str) -> str:
        """執行任務"""
        return self.agent.run(task)


def example_5_agent_communication():
    """Agent 間通信"""
    print("\n" + "="*70)
    print("範例 5: Agent 間通信")
    print("="*70)

    # 創建可通信的 Agent
    alice = CommunicatingAgent("Alice", [search_web])
    bob = CommunicatingAgent("Bob", [write_section])

    print("\nAgent 通信流程：")

    # Alice 完成研究並通知 Bob
    research = alice.run("研究 AI 安全")
    alice.send_message(bob, f"研究完成：{research}")

    # Bob 接收消息並開始寫作
    messages = bob.receive_messages()
    for msg in messages:
        print(f"\n📬 {bob.name} 收到來自 {msg['from']} 的消息")
        article = bob.run(f"基於以下研究寫文章：{msg['message']}")
        print(f"\n{bob.name} 完成寫作: {article[:100]}...")


# ============================================================================
# 範例 6: 多 Agent 最佳實踐
# ============================================================================

def example_6_best_practices():
    """多 Agent 系統最佳實踐"""
    print("\n" + "="*70)
    print("範例 6: 多 Agent 最佳實踐")
    print("="*70)

    print("\n1. 清晰的職責劃分")
    print("   - 每個 Agent 專注於特定任務")
    print("   - 避免職責重疊")
    print("   - 定義清晰的接口")

    print("\n2. 有效的協調機制")
    print("   - Manager Agent 協調整體")
    print("   - 定義工作流程")
    print("   - 處理衝突和依賴")

    print("\n3. 錯誤處理和容錯")
    print("   - Agent 失敗時有備份方案")
    print("   - 超時保護")
    print("   - 優雅降級")

    print("\n4. 性能優化")
    print("   - 並行執行獨立任務")
    print("   - 緩存中間結果")
    print("   - 避免重複工作")

    print("\n5. 監控和調試")
    print("   - 記錄 Agent 間通信")
    print("   - 追蹤任務流程")
    print("   - 性能指標收集")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*70)
    print("多 Agent 系統 - Agent 協作")
    print("="*70)

    examples = [
        ("範例 1: 專業化 Agent", example_1_specialized_agents),
        ("範例 2: Manager-Worker 模式", example_2_manager_worker),
        ("範例 3: 流水線協作", example_3_pipeline),
        ("範例 4: 並行協作", example_4_parallel_agents),
        ("範例 5: Agent 通信", example_5_agent_communication),
        ("範例 6: 最佳實踐", example_6_best_practices),
    ]

    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n{name} 執行失敗: {e}")

    print("\n" + "="*70)
    print("多 Agent 系統完成！")
    print("="*70)

    print("\n關鍵要點：")
    print("  - 多 Agent 可以處理更複雜的任務")
    print("  - 專業化提高效率")
    print("  - Manager-Worker 模式易於擴展")
    print("  - 並行執行提升性能")
    print("  - 良好的協調機制很重要")

    print("\n下一步: 查看 09_LangChain工具.py 學習與 LangChain 集成")


if __name__ == "__main__":
    main()
