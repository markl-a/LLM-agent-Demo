"""
ControlFlow 快速開始示例
======================

本文件演示 ControlFlow 框架的基本使用方法,包括:
1. 基本設置和配置
2. 創建第一個 Agent
3. 定義和執行簡單任務
4. 創建基本工作流
5. 處理輸入和輸出
6. 使用上下文和變量

作者: ControlFlow 示例團隊
日期: 2025
"""

import os
from typing import Optional, List, Dict, Any
import controlflow as cf
from controlflow import Agent, Task, Flow
from dotenv import load_dotenv


# ========== 環境配置 ==========

def setup_environment():
    """
    設置 ControlFlow 運行環境

    這個函數負責:
    1. 載入環境變量
    2. 配置 API 密鑰
    3. 設置日誌級別
    4. 驗證配置是否正確
    """
    # 載入 .env 文件中的環境變量
    load_dotenv()

    # 檢查必要的環境變量
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ 警告: 未找到 OPENAI_API_KEY 環境變量")
        print("請在 .env 文件中設置: OPENAI_API_KEY=your_key_here")
    else:
        print("✅ 環境配置成功!")
        print(f"   API Key: {api_key[:8]}...{api_key[-4:]}")

    # 設置默認配置
    cf.settings.log_level = os.getenv("CONTROLFLOW_LOG_LEVEL", "INFO")
    cf.settings.default_model = os.getenv("CONTROLFLOW_DEFAULT_MODEL", "gpt-4")

    print(f"   日誌級別: {cf.settings.log_level}")
    print(f"   默認模型: {cf.settings.default_model}")
    print()


# ========== 基本 Agent 創建 ==========

class SimpleAgentExample:
    """
    簡單 Agent 示例類

    演示如何創建和配置基本的 AI Agent
    """

    def __init__(self):
        """初始化示例"""
        self.agent = None

    def create_basic_agent(self) -> Agent:
        """
        創建一個基本的 Agent

        Returns:
            Agent: 配置好的 Agent 實例
        """
        print("📌 創建基本 Agent...")

        # 創建一個簡單的 Agent
        agent = Agent(
            name="小助手",
            description="一個友好的 AI 助手,能夠回答問題和提供幫助",
            model="gpt-4"
        )

        print(f"   Agent 名稱: {agent.name}")
        print(f"   Agent 描述: {agent.description}")
        print(f"   使用模型: {agent.model}")
        print()

        self.agent = agent
        return agent

    def create_specialized_agent(self, role: str, expertise: str) -> Agent:
        """
        創建一個專業化的 Agent

        Args:
            role: Agent 的角色
            expertise: Agent 的專長領域

        Returns:
            Agent: 專業化的 Agent 實例
        """
        print(f"📌 創建專業 Agent: {role}...")

        agent = Agent(
            name=role,
            description=f"專注於{expertise}的專業助手",
            instructions=f"""
            你是一個{role},專門負責{expertise}相關的任務。
            請始終保持專業、準確,並提供有價值的見解。
            在回答時,請考慮最佳實踐和行業標準。
            """,
            model="gpt-4"
        )

        print(f"   角色: {agent.name}")
        print(f"   專長: {expertise}")
        print()

        return agent


# ========== 基本任務定義 ==========

class SimpleTaskExample:
    """
    簡單任務示例類

    演示如何定義和執行基本任務
    """

    def __init__(self, agent: Optional[Agent] = None):
        """
        初始化任務示例

        Args:
            agent: 可選的 Agent 實例,如果不提供則使用默認 Agent
        """
        self.agent = agent

    def create_simple_task(self, objective: str) -> Task:
        """
        創建一個簡單任務

        Args:
            objective: 任務目標

        Returns:
            Task: 創建的任務實例
        """
        print(f"📋 創建任務: {objective}...")

        task = Task(
            objective=objective,
            agent=self.agent
        )

        print(f"   任務 ID: {task.id}")
        print(f"   任務目標: {task.objective}")
        print()

        return task

    def create_detailed_task(
        self,
        objective: str,
        instructions: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Task:
        """
        創建一個詳細配置的任務

        Args:
            objective: 任務目標
            instructions: 詳細指令
            context: 任務上下文

        Returns:
            Task: 配置完整的任務實例
        """
        print(f"📋 創建詳細任務: {objective}...")

        task = Task(
            objective=objective,
            instructions=instructions,
            context=context or {},
            agent=self.agent
        )

        print(f"   任務目標: {task.objective}")
        print(f"   指令長度: {len(instructions)} 字符")
        if context:
            print(f"   上下文鍵: {', '.join(context.keys())}")
        print()

        return task

    def execute_task(self, task: Task) -> Any:
        """
        執行任務並返回結果

        Args:
            task: 要執行的任務

        Returns:
            Any: 任務執行結果
        """
        print(f"▶️ 執行任務: {task.objective}...")

        try:
            result = task.run()
            print(f"✅ 任務完成!")
            print(f"   結果: {result}")
            print()
            return result
        except Exception as e:
            print(f"❌ 任務執行失敗: {str(e)}")
            print()
            raise


# ========== 基本工作流 ==========

class SimpleFlowExample:
    """
    簡單工作流示例類

    演示如何創建和執行基本工作流
    """

    @staticmethod
    @cf.flow
    def hello_world_flow() -> str:
        """
        最簡單的 Hello World 工作流

        Returns:
            str: 問候消息
        """
        print("🌊 執行 Hello World 工作流...")

        # 創建一個簡單任務
        task = Task(
            objective="生成一個友好的問候消息",
            instructions="創建一個溫暖、專業的問候語"
        )

        # 執行任務
        result = task.run()

        print(f"✅ 工作流完成!")
        return result

    @staticmethod
    @cf.flow
    def question_answer_flow(question: str) -> str:
        """
        問答工作流

        接收用戶問題並返回答案

        Args:
            question: 用戶的問題

        Returns:
            str: AI 的回答
        """
        print(f"🌊 執行問答工作流...")
        print(f"   問題: {question}")

        # 創建問答任務
        task = Task(
            objective="回答用戶的問題",
            instructions="""
            請仔細理解用戶的問題,提供準確、有幫助的答案。
            答案應該清晰、簡潔,必要時提供例子或進一步的解釋。
            """,
            context={"question": question}
        )

        # 執行任務
        answer = task.run()

        print(f"✅ 已生成答案!")
        return answer

    @staticmethod
    @cf.flow
    def multi_step_flow(topic: str) -> Dict[str, Any]:
        """
        多步驟工作流

        演示如何將一個複雜任務分解為多個步驟

        Args:
            topic: 要處理的主題

        Returns:
            Dict[str, Any]: 包含各步驟結果的字典
        """
        print(f"🌊 執行多步驟工作流: {topic}...")

        results = {}

        # 步驟 1: 研究主題
        print("\n📍 步驟 1: 研究主題...")
        research_task = Task(
            objective=f"研究主題: {topic}",
            instructions="收集關於該主題的基本信息和關鍵要點"
        )
        results["research"] = research_task.run()

        # 步驟 2: 分析信息
        print("\n📍 步驟 2: 分析信息...")
        analysis_task = Task(
            objective="分析研究結果",
            instructions="整理和分析收集到的信息,提煉關鍵見解",
            context={"research_data": results["research"]}
        )
        results["analysis"] = analysis_task.run()

        # 步驟 3: 生成總結
        print("\n📍 步驟 3: 生成總結...")
        summary_task = Task(
            objective="生成總結報告",
            instructions="基於研究和分析,生成一個清晰的總結",
            context={
                "research": results["research"],
                "analysis": results["analysis"]
            }
        )
        results["summary"] = summary_task.run()

        print(f"\n✅ 多步驟工作流完成!")
        return results


# ========== 上下文和變量處理 ==========

class ContextExample:
    """
    上下文和變量處理示例類

    演示如何在任務和工作流中使用上下文和變量
    """

    @staticmethod
    @cf.flow
    def context_sharing_flow(user_data: Dict[str, Any]) -> str:
        """
        演示上下文共享的工作流

        Args:
            user_data: 用戶數據字典

        Returns:
            str: 個性化的輸出
        """
        print("🌊 執行上下文共享工作流...")
        print(f"   用戶數據: {user_data}")

        # 任務 1: 分析用戶數據
        analyze_task = Task(
            objective="分析用戶數據",
            instructions="理解用戶的偏好和需求",
            context=user_data
        )
        analysis = analyze_task.run()

        # 任務 2: 生成個性化建議(使用前一任務的結果)
        recommend_task = Task(
            objective="生成個性化建議",
            instructions="基於用戶分析,提供定制化的建議",
            context={
                "user_data": user_data,
                "analysis": analysis
            }
        )
        recommendation = recommend_task.run()

        return recommendation

    @staticmethod
    def demonstrate_variable_passing():
        """
        演示變量在任務間傳遞
        """
        print("🔄 演示變量傳遞...")

        # 初始數據
        data = {"count": 0, "messages": []}

        # 任務 1: 處理數據
        task1 = Task(
            objective="處理初始數據",
            context=data
        )
        result1 = task1.run()

        # 將結果傳遞給下一個任務
        task2 = Task(
            objective="進一步處理",
            context={"previous_result": result1}
        )
        result2 = task2.run()

        print(f"✅ 變量傳遞完成!")
        return result2


# ========== 實用工具函數 ==========

def print_section(title: str):
    """
    打印分節標題

    Args:
        title: 標題文本
    """
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demonstrate_basic_usage():
    """
    演示 ControlFlow 的基本使用方法

    這個函數展示了從設置到執行的完整流程
    """
    print_section("ControlFlow 快速開始示例")

    # 1. 環境設置
    print_section("1. 環境設置")
    setup_environment()

    # 2. 創建 Agent
    print_section("2. 創建 Agent")
    agent_example = SimpleAgentExample()
    basic_agent = agent_example.create_basic_agent()

    # 創建專業 Agent
    expert_agent = agent_example.create_specialized_agent(
        role="數據分析師",
        expertise="數據分析和可視化"
    )

    # 3. 定義和執行任務
    print_section("3. 定義和執行任務")
    task_example = SimpleTaskExample(agent=basic_agent)

    # 簡單任務
    simple_task = task_example.create_simple_task(
        objective="介紹 ControlFlow 框架的主要特點"
    )
    task_example.execute_task(simple_task)

    # 詳細任務
    detailed_task = task_example.create_detailed_task(
        objective="分析 Python 在 AI 領域的應用",
        instructions="""
        請從以下幾個方面分析:
        1. Python 的優勢
        2. 主要的 AI 庫和框架
        3. 實際應用案例
        4. 未來發展趨勢
        """,
        context={"focus": "實用性", "depth": "中等"}
    )
    task_example.execute_task(detailed_task)

    # 4. 執行工作流
    print_section("4. 執行簡單工作流")
    flow_example = SimpleFlowExample()

    # Hello World 工作流
    greeting = flow_example.hello_world_flow()
    print(f"問候: {greeting}\n")

    # 問答工作流
    answer = flow_example.question_answer_flow(
        "什麼是 Agentic AI?"
    )
    print(f"答案: {answer}\n")

    # 5. 多步驟工作流
    print_section("5. 執行多步驟工作流")
    results = flow_example.multi_step_flow("機器學習基礎")

    print("\n📊 工作流結果:")
    for step, result in results.items():
        print(f"\n{step.upper()}:")
        print(f"{result[:200]}..." if len(str(result)) > 200 else result)

    # 6. 上下文處理
    print_section("6. 上下文和變量處理")
    context_example = ContextExample()

    user_data = {
        "name": "張三",
        "interests": ["AI", "機器學習", "數據分析"],
        "level": "中級"
    }

    recommendation = context_example.context_sharing_flow(user_data)
    print(f"\n個性化建議: {recommendation}")


# ========== 主程序 ==========

def main():
    """
    主程序入口

    運行所有示例演示
    """
    try:
        # 執行基本使用演示
        demonstrate_basic_usage()

        print_section("演示完成")
        print("✅ 所有示例已成功執行!")
        print("\n💡 下一步:")
        print("   - 查看 02_任務定義.py 學習更多任務配置")
        print("   - 查看 03_流程控制.py 學習流程控制模式")
        print("   - 查看 05_Agent創建.py 學習高級 Agent 配置")
        print()

    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
