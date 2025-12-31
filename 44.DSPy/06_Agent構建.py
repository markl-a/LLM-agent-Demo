"""
DSPy Agent 構建教學

本模組展示如何使用 DSPy 構建智能代理（Agent）：
1. Agent 基礎概念和架構
2. 工具定義和集成
3. ReAct 模式實現
4. 多步驟任務規劃
5. 自主決策 Agent
6. 多 Agent 協作
7. Agent 錯誤處理和恢復

作者：DSPy 教學團隊
日期：2025-01
"""

import dspy
from typing import List, Dict, Optional, Callable, Any
import json
import math
import random
from datetime import datetime


# ==================== Agent 基礎概念 ====================

def explain_agent_concept():
    """
    解釋 Agent 的核心概念

    Agent = 能夠自主行動的智能系統
    """
    print("\n" + "="*60)
    print("Agent 核心概念")
    print("="*60)

    print("""
    什麼是 Agent？
    - 能夠感知環境
    - 能夠自主決策
    - 能夠執行行動
    - 能夠學習和適應

    Agent 的關鍵組件：
    1. 感知（Perception）：理解輸入和環境
    2. 推理（Reasoning）：決定做什麼
    3. 行動（Action）：執行工具和操作
    4. 記憶（Memory）：存儲和檢索資訊

    DSPy Agent 的優勢：
    - 自動優化決策策略
    - 模組化工具集成
    - 可追蹤的推理過程
    - 可評估和改進

    常見 Agent 模式：
    - ReAct：推理-行動循環
    - Plan-and-Execute：先規劃後執行
    - Reflection：反思和自我糾正
    - Multi-Agent：多個 Agent 協作
    """)


# ==================== 工具定義 ====================

class Tool:
    """工具基類"""

    def __init__(self, name: str, description: str, function: Callable):
        """
        初始化工具

        Args:
            name: 工具名稱
            description: 工具描述
            function: 執行函數
        """
        self.name = name
        self.description = description
        self.function = function

    def __call__(self, *args, **kwargs):
        """執行工具"""
        return self.function(*args, **kwargs)

    def __str__(self):
        return f"{self.name}: {self.description}"


# 定義具體工具

def calculator_tool(expression: str) -> str:
    """
    計算器工具

    Args:
        expression: 數學表達式

    Returns:
        計算結果
    """
    try:
        # 安全評估數學表達式
        allowed_names = {
            'abs': abs, 'round': round,
            'min': min, 'max': max,
            'sum': sum, 'pow': pow,
            'sqrt': math.sqrt,
            'sin': math.sin, 'cos': math.cos,
            'pi': math.pi, 'e': math.e
        }
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"計算結果：{result}"
    except Exception as e:
        return f"計算錯誤：{str(e)}"


def search_tool(query: str) -> str:
    """
    搜索工具（模擬）

    Args:
        query: 搜索查詢

    Returns:
        搜索結果
    """
    # 模擬搜索結果
    mock_results = {
        "天氣": "今天天氣晴朗，溫度 25°C，適合戶外活動。",
        "新聞": "最新科技新聞：AI 技術持續發展，多個新模型發布。",
        "股票": "股市今日上漲 1.5%，科技股表現強勁。",
    }

    for key in mock_results:
        if key in query:
            return mock_results[key]

    return f"搜索 '{query}' 的結果：找到 3 條相關資訊..."


def get_current_time_tool() -> str:
    """
    獲取當前時間工具

    Returns:
        當前時間字符串
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def python_executor_tool(code: str) -> str:
    """
    Python 程式碼執行器（受限）

    Args:
        code: Python 程式碼

    Returns:
        執行結果
    """
    try:
        # 非常受限的執行環境
        allowed_globals = {
            'abs': abs, 'len': len, 'max': max, 'min': min,
            'sum': sum, 'sorted': sorted, 'range': range,
            'list': list, 'dict': dict, 'str': str, 'int': int,
        }
        local_vars = {}
        exec(code, allowed_globals, local_vars)

        # 返回所有變量
        return f"執行成功。變量：{local_vars}"
    except Exception as e:
        return f"執行錯誤：{str(e)}"


def weather_tool(city: str) -> str:
    """
    天氣查詢工具（模擬）

    Args:
        city: 城市名稱

    Returns:
        天氣資訊
    """
    weather_data = {
        "台北": "晴天，溫度 26°C，濕度 65%",
        "高雄": "多雲，溫度 28°C，濕度 70%",
        "台中": "陰天，溫度 24°C，濕度 75%",
    }

    return weather_data.get(city, f"{city}：晴天，溫度 25°C")


# 創建工具集合

TOOLS = [
    Tool("calculator", "執行數學計算，輸入數學表達式", calculator_tool),
    Tool("search", "搜索資訊，輸入搜索查詢", search_tool),
    Tool("get_time", "獲取當前時間，無需輸入", get_current_time_tool),
    Tool("python", "執行簡單的 Python 程式碼", python_executor_tool),
    Tool("weather", "查詢城市天氣，輸入城市名稱", weather_tool),
]


def get_tools_description() -> str:
    """獲取所有工具的描述"""
    return "\n".join([
        f"- {tool.name}: {tool.description}"
        for tool in TOOLS
    ])


def execute_tool(tool_name: str, tool_input: str) -> str:
    """
    執行工具

    Args:
        tool_name: 工具名稱
        tool_input: 工具輸入

    Returns:
        執行結果
    """
    for tool in TOOLS:
        if tool.name == tool_name:
            try:
                if tool_name == "get_time":
                    return tool()
                else:
                    return tool(tool_input)
            except Exception as e:
                return f"工具執行錯誤：{str(e)}"

    return f"未找到工具：{tool_name}"


# ==================== ReAct Agent ====================

class ReActAgent(dspy.Module):
    """
    ReAct Agent

    ReAct = Reasoning + Acting
    交替進行推理和行動
    """

    def __init__(self, max_steps=5):
        super().__init__()
        self.max_steps = max_steps

        # 推理步驟
        class Reason(dspy.Signature):
            """分析當前情況並決定下一步行動"""
            question = dspy.InputField(desc="原始問題")
            previous_steps = dspy.InputField(desc="之前的步驟和觀察")
            available_tools = dspy.InputField(desc="可用工具列表")

            thought = dspy.OutputField(desc="當前的思考")
            action = dspy.OutputField(desc="要執行的工具名稱，或 'finish' 表示完成")
            action_input = dspy.OutputField(desc="工具的輸入參數")

        # 生成最終答案
        class GenerateFinalAnswer(dspy.Signature):
            """基於所有步驟生成最終答案"""
            question = dspy.InputField()
            steps_and_observations = dspy.InputField()
            final_answer = dspy.OutputField()

        self.reason = dspy.ChainOfThought(Reason)
        self.generate_answer = dspy.Predict(GenerateFinalAnswer)

    def forward(self, question):
        """執行 ReAct 循環"""
        steps = []
        previous_steps_text = "無"

        for step in range(self.max_steps):
            # 推理
            reasoning = self.reason(
                question=question,
                previous_steps=previous_steps_text,
                available_tools=get_tools_description()
            )

            thought = reasoning.thought
            action = reasoning.action.strip().lower()
            action_input = reasoning.action_input

            steps.append({
                "step": step + 1,
                "thought": thought,
                "action": action,
                "action_input": action_input
            })

            # 如果決定完成
            if action == "finish":
                break

            # 執行工具
            observation = execute_tool(action, action_input)
            steps[-1]["observation"] = observation

            # 更新歷史
            previous_steps_text = "\n\n".join([
                f"步驟 {s['step']}:\n"
                f"思考: {s['thought']}\n"
                f"行動: {s['action']}({s.get('action_input', '')})\n"
                f"觀察: {s.get('observation', 'N/A')}"
                for s in steps
            ])

        # 生成最終答案
        final = self.generate_answer(
            question=question,
            steps_and_observations=previous_steps_text
        )

        return dspy.Prediction(
            answer=final.final_answer,
            steps=steps,
            num_steps=len(steps)
        )


# ==================== Plan-and-Execute Agent ====================

class PlanAndExecuteAgent(dspy.Module):
    """
    Plan-and-Execute Agent

    先制定完整計劃，然後逐步執行
    """

    def __init__(self):
        super().__init__()

        # 制定計劃
        class CreatePlan(dspy.Signature):
            """制定解決問題的步驟計劃"""
            question = dspy.InputField()
            available_tools = dspy.InputField()
            plan = dspy.OutputField(desc="步驟列表，每行一個步驟")

        # 執行單個步驟
        class ExecuteStep(dspy.Signature):
            """執行計劃中的一個步驟"""
            question = dspy.InputField()
            plan = dspy.InputField()
            current_step = dspy.InputField()
            previous_results = dspy.InputField()
            available_tools = dspy.InputField()

            tool_to_use = dspy.OutputField(desc="要使用的工具名稱")
            tool_input = dspy.OutputField(desc="工具輸入")

        # 綜合結果
        class SynthesizeResults(dspy.Signature):
            """綜合所有步驟的結果"""
            question = dspy.InputField()
            plan = dspy.InputField()
            results = dspy.InputField()
            final_answer = dspy.OutputField()

        self.create_plan = dspy.ChainOfThought(CreatePlan)
        self.execute_step = dspy.Predict(ExecuteStep)
        self.synthesize = dspy.Predict(SynthesizeResults)

    def forward(self, question):
        """執行計劃和執行流程"""
        # 制定計劃
        plan_result = self.create_plan(
            question=question,
            available_tools=get_tools_description()
        )

        plan_steps = [
            step.strip()
            for step in plan_result.plan.split("\n")
            if step.strip()
        ]

        # 執行每個步驟
        results = []
        previous_results_text = "無"

        for i, step in enumerate(plan_steps):
            # 執行步驟
            execution = self.execute_step(
                question=question,
                plan=plan_result.plan,
                current_step=step,
                previous_results=previous_results_text,
                available_tools=get_tools_description()
            )

            # 執行工具
            observation = execute_tool(
                execution.tool_to_use,
                execution.tool_input
            )

            results.append({
                "step": i + 1,
                "plan_step": step,
                "tool": execution.tool_to_use,
                "tool_input": execution.tool_input,
                "observation": observation
            })

            # 更新歷史
            previous_results_text = "\n".join([
                f"{r['step']}. {r['plan_step']} -> {r['observation']}"
                for r in results
            ])

        # 綜合結果
        results_text = "\n\n".join([
            f"步驟 {r['step']}: {r['plan_step']}\n"
            f"工具: {r['tool']}\n"
            f"結果: {r['observation']}"
            for r in results
        ])

        synthesis = self.synthesize(
            question=question,
            plan=plan_result.plan,
            results=results_text
        )

        return dspy.Prediction(
            answer=synthesis.final_answer,
            plan=plan_steps,
            execution_results=results
        )


# ==================== Self-Reflective Agent ====================

class ReflectiveAgent(dspy.Module):
    """
    自我反思 Agent

    能夠評估自己的輸出並進行改進
    """

    def __init__(self, max_iterations=2):
        super().__init__()
        self.max_iterations = max_iterations

        # 生成初始答案
        class GenerateAnswer(dspy.Signature):
            """生成問題的答案"""
            question = dspy.InputField()
            previous_attempt = dspy.InputField(desc="之前的嘗試（如果有）")
            feedback = dspy.InputField(desc="反饋（如果有）")
            answer = dspy.OutputField()

        # 自我評估
        class SelfEvaluate(dspy.Signature):
            """評估答案的質量"""
            question = dspy.InputField()
            answer = dspy.InputField()
            is_satisfactory = dspy.OutputField(desc="yes 或 no")
            issues = dspy.OutputField(desc="發現的問題")
            suggestions = dspy.OutputField(desc="改進建議")

        self.generate = dspy.ChainOfThought(GenerateAnswer)
        self.evaluate = dspy.Predict(SelfEvaluate)

    def forward(self, question):
        """執行反思循環"""
        iterations = []
        current_answer = ""
        feedback = "無"

        for i in range(self.max_iterations):
            # 生成答案
            result = self.generate(
                question=question,
                previous_attempt=current_answer if current_answer else "無",
                feedback=feedback
            )
            current_answer = result.answer

            # 自我評估
            evaluation = self.evaluate(
                question=question,
                answer=current_answer
            )

            iterations.append({
                "iteration": i + 1,
                "answer": current_answer,
                "is_satisfactory": evaluation.is_satisfactory,
                "issues": evaluation.issues,
                "suggestions": evaluation.suggestions
            })

            # 如果滿意，提前退出
            if "yes" in evaluation.is_satisfactory.lower():
                break

            # 準備下一次的反饋
            feedback = f"問題：{evaluation.issues}\n建議：{evaluation.suggestions}"

        return dspy.Prediction(
            final_answer=current_answer,
            iterations=iterations,
            num_iterations=len(iterations)
        )


# ==================== Multi-Agent System ====================

class MultiAgentSystem(dspy.Module):
    """
    多 Agent 系統

    多個專業 Agent 協作解決問題
    """

    def __init__(self):
        super().__init__()

        # 任務分配器
        class TaskRouter(dspy.Signature):
            """決定哪個專業 Agent 處理任務"""
            question = dspy.InputField()
            agent_type = dspy.OutputField(
                desc="research（研究）, analysis（分析）, "
                     "creative（創意）, technical（技術）"
            )
            reasoning = dspy.OutputField(desc="選擇理由")

        # 研究 Agent
        class ResearchAgent(dspy.Signature):
            """專注於資訊收集和研究"""
            question = dspy.InputField()
            research_findings = dspy.OutputField()

        # 分析 Agent
        class AnalysisAgent(dspy.Signature):
            """專注於數據分析和推理"""
            question = dspy.InputField()
            analysis_result = dspy.OutputField()

        # 創意 Agent
        class CreativeAgent(dspy.Signature):
            """專注於創意性任務"""
            question = dspy.InputField()
            creative_output = dspy.OutputField()

        # 技術 Agent
        class TechnicalAgent(dspy.Signature):
            """專注於技術性問題"""
            question = dspy.InputField()
            technical_solution = dspy.OutputField()

        self.router = dspy.Predict(TaskRouter)
        self.research_agent = dspy.ChainOfThought(ResearchAgent)
        self.analysis_agent = dspy.ChainOfThought(AnalysisAgent)
        self.creative_agent = dspy.ChainOfThought(CreativeAgent)
        self.technical_agent = dspy.ChainOfThought(TechnicalAgent)

    def forward(self, question):
        """路由到適當的 Agent"""
        # 決定使用哪個 Agent
        routing = self.router(question=question)
        agent_type = routing.agent_type.lower()

        # 執行對應的 Agent
        if "research" in agent_type:
            result = self.research_agent(question=question)
            answer = result.research_findings
        elif "analysis" in agent_type:
            result = self.analysis_agent(question=question)
            answer = result.analysis_result
        elif "creative" in agent_type:
            result = self.creative_agent(question=question)
            answer = result.creative_output
        else:  # technical
            result = self.technical_agent(question=question)
            answer = result.technical_solution

        return dspy.Prediction(
            answer=answer,
            agent_used=agent_type,
            routing_reasoning=routing.reasoning
        )


# ==================== 演示函數 ====================

def demo_react_agent():
    """演示 ReAct Agent"""
    print("\n" + "="*60)
    print("ReAct Agent 演示")
    print("="*60)

    agent = ReActAgent(max_steps=5)

    questions = [
        "計算 25 的平方根再乘以 10",
        "現在是什麼時間？台北的天氣如何？",
    ]

    for question in questions:
        print(f"\n問題：{question}")
        result = agent(question=question)
        print(f"答案：{result.answer}")
        print(f"執行步驟數：{result.num_steps}")
        print("\n步驟詳情：")
        for step in result.steps:
            print(f"  步驟 {step['step']}: {step['thought'][:50]}...")


def demo_plan_execute_agent():
    """演示 Plan-and-Execute Agent"""
    print("\n" + "="*60)
    print("Plan-and-Execute Agent 演示")
    print("="*60)

    agent = PlanAndExecuteAgent()
    question = "查詢台北天氣，並計算如果溫度是 26 度，轉換成華氏是多少"

    print(f"\n問題：{question}")
    result = agent(question=question)
    print(f"\n計劃：")
    for i, step in enumerate(result.plan, 1):
        print(f"  {i}. {step}")
    print(f"\n最終答案：{result.answer}")


def demo_reflective_agent():
    """演示 Reflective Agent"""
    print("\n" + "="*60)
    print("Reflective Agent 演示")
    print("="*60)

    agent = ReflectiveAgent(max_iterations=2)
    question = "解釋量子糾纏的概念"

    print(f"\n問題：{question}")
    result = agent(question=question)
    print(f"\n迭代次數：{result.num_iterations}")
    print(f"最終答案：{result.final_answer}")


# ==================== 主程序 ====================

def main():
    """主函數：演示所有 Agent 類型"""

    print("="*60)
    print("DSPy Agent 構建教學")
    print("="*60)

    # 1. 概念說明
    explain_agent_concept()

    # 2. 配置
    print("\n" + "="*60)
    print("配置 DSPy")
    print("="*60)
    try:
        lm = dspy.OpenAI(model="gpt-4", max_tokens=800)
        dspy.settings.configure(lm=lm)
        print("✓ 配置完成")
    except Exception as e:
        print(f"配置失敗：{e}")
        return

    # 3. 工具展示
    print("\n" + "="*60)
    print("可用工具")
    print("="*60)
    print(get_tools_description())

    # 4. ReAct Agent 演示
    try:
        demo_react_agent()
    except Exception as e:
        print(f"ReAct Agent 錯誤：{e}")

    # 5. Plan-and-Execute Agent 演示
    try:
        demo_plan_execute_agent()
    except Exception as e:
        print(f"Plan-and-Execute Agent 錯誤：{e}")

    # 6. Reflective Agent 演示
    try:
        demo_reflective_agent()
    except Exception as e:
        print(f"Reflective Agent 錯誤：{e}")

    # 7. Multi-Agent 演示
    try:
        print("\n" + "="*60)
        print("Multi-Agent System 演示")
        print("="*60)
        multi_agent = MultiAgentSystem()
        questions = [
            "研究區塊鏈技術的最新發展",  # research
            "分析電動車市場的增長趨勢",  # analysis
        ]
        for q in questions:
            result = multi_agent(question=q)
            print(f"\n問題：{q}")
            print(f"使用的 Agent：{result.agent_used}")
            print(f"答案：{result.answer[:100]}...")
    except Exception as e:
        print(f"Multi-Agent 錯誤：{e}")

    # 總結
    print("\n" + "="*60)
    print("教學完成！")
    print("="*60)
    print("""
    你已經學會了：
    1. ✓ Agent 的核心概念
    2. ✓ 工具定義和集成
    3. ✓ ReAct Agent 實現
    4. ✓ Plan-and-Execute Agent
    5. ✓ Self-Reflective Agent
    6. ✓ Multi-Agent 協作

    Agent 設計原則：
    - 清晰的工具定義
    - 合理的推理步驟限制
    - 完善的錯誤處理
    - 可追蹤的執行過程

    進階技巧：
    - 工具鏈組合
    - 動態工具選擇
    - 記憶和上下文管理
    - Agent 學習和適應

    下一步：
    - 學習評估指標（07_評估指標.py）
    - 學習多模型支援（08_多模型支援.py）
    - 構建實際應用 Agent
    """)


if __name__ == "__main__":
    main()
