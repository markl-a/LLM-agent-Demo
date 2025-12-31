"""
PhiData 多 Agent 團隊協作示例

這個腳本展示了如何使用 PhiData 構建多 Agent 協作系統，包括：
1. 團隊 Agent 架構
2. 角色分工和職責
3. Agent 間通信
4. 任務協調和分配
5. 工作流編排
6. 並行和串行執行
7. 結果整合
8. 錯誤處理和容錯
9. 性能優化
10. 複雜任務分解

作者: PhiData Team
日期: 2025
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# PhiData 核心導入
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.yfinance import YFinanceTools
from phi.utils.log import logger

# 環境變量管理
from dotenv import load_dotenv

# 載入環境變量
load_dotenv()


class MultiAgentTeam:
    """
    多 Agent 團隊類

    管理和協調多個 Agent 協同工作，實現複雜任務的分工合作。
    支持不同的協作模式和工作流。
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化多 Agent 團隊

        參數:
            api_key: OpenAI API 密鑰
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("未找到 OPENAI_API_KEY")

        logger.info("初始化多 Agent 團隊")

        # 團隊成員
        self.agents: Dict[str, Agent] = {}

        # 任務歷史
        self.task_history: List[Dict[str, Any]] = []

    def create_researcher_agent(self) -> Agent:
        """
        創建研究員 Agent

        負責信息收集和研究。

        返回:
            研究員 Agent
        """
        logger.info("創建研究員 Agent")

        agent = Agent(
            name="研究員",
            role="負責收集和研究相關信息",
            model=OpenAIChat(
                id="gpt-4",
                api_key=self.api_key,
            ),
            tools=[DuckDuckGo()],
            description="專業的研究人員，擅長信息收集和分析",
            instructions=[
                "搜索最新、最相關的信息",
                "提供詳細的背景資料",
                "引用可靠來源",
                "組織信息清晰易讀",
                "使用繁體中文",
            ],
            show_tool_calls=True,
            markdown=True,
        )

        return agent

    def create_analyst_agent(self) -> Agent:
        """
        創建分析師 Agent

        負責數據分析和洞察提取。

        返回:
            分析師 Agent
        """
        logger.info("創建分析師 Agent")

        agent = Agent(
            name="分析師",
            role="負責分析數據並提供洞察",
            model=OpenAIChat(
                id="gpt-4",
                api_key=self.api_key,
                temperature=0.3,
            ),
            tools=[YFinanceTools()],
            description="專業的數據分析師",
            instructions=[
                "深入分析數據",
                "識別趨勢和模式",
                "提供有價值的洞察",
                "使用數據支持結論",
                "使用繁體中文",
            ],
            show_tool_calls=True,
            markdown=True,
        )

        return agent

    def create_writer_agent(self) -> Agent:
        """
        創建寫作 Agent

        負責內容創作和報告撰寫。

        返回:
            寫作 Agent
        """
        logger.info("創建寫作 Agent")

        agent = Agent(
            name="作家",
            role="負責撰寫報告和文檔",
            model=OpenAIChat(
                id="gpt-4",
                api_key=self.api_key,
                temperature=0.7,
            ),
            description="專業的內容創作者",
            instructions=[
                "撰寫清晰、專業的內容",
                "組織信息邏輯清晰",
                "使用恰當的語言風格",
                "確保內容完整準確",
                "使用繁體中文",
            ],
            markdown=True,
        )

        return agent

    def create_reviewer_agent(self) -> Agent:
        """
        創建審核 Agent

        負責質量審核和改進建議。

        返回:
            審核 Agent
        """
        logger.info("創建審核 Agent")

        agent = Agent(
            name="審核員",
            role="負責質量審核和改進",
            model=OpenAIChat(
                id="gpt-4",
                api_key=self.api_key,
                temperature=0.2,
            ),
            description="專業的質量審核員",
            instructions=[
                "仔細審核內容質量",
                "識別錯誤和不足",
                "提供改進建議",
                "確保專業水準",
                "使用繁體中文",
            ],
            markdown=True,
        )

        return agent

    def create_coordinator_agent(self) -> Agent:
        """
        創建協調員 Agent

        負責任務協調和團隊管理。

        返回:
            協調員 Agent
        """
        logger.info("創建協調員 Agent")

        agent = Agent(
            name="協調員",
            role="負責協調團隊工作",
            model=OpenAIChat(
                id="gpt-4",
                api_key=self.api_key,
            ),
            description="團隊協調者和項目經理",
            instructions=[
                "協調各個 Agent 的工作",
                "確保任務順利完成",
                "整合團隊成果",
                "管理工作流程",
                "使用繁體中文",
            ],
            markdown=True,
        )

        return agent

    def create_team_leader(
        self,
        team_members: List[Agent]
    ) -> Agent:
        """
        創建團隊領導 Agent

        領導整個團隊完成任務。

        參數:
            team_members: 團隊成員列表

        返回:
            團隊領導 Agent
        """
        logger.info(f"創建團隊領導，團隊成員數: {len(team_members)}")

        agent = Agent(
            name="團隊領導",
            role="領導團隊完成複雜任務",
            model=OpenAIChat(
                id="gpt-4",
                api_key=self.api_key,
            ),
            team=team_members,  # 指定團隊成員
            description="經驗豐富的團隊領導",
            instructions=[
                "分解複雜任務",
                "分配任務給合適的團隊成員",
                "協調團隊協作",
                "整合團隊成果",
                "確保高質量交付",
                "使用繁體中文",
            ],
            show_tool_calls=True,
            markdown=True,
        )

        return agent

    def sequential_workflow(
        self,
        agents: List[Agent],
        task: str
    ) -> List[str]:
        """
        串行工作流

        Agent 按順序執行任務，每個 Agent 的輸出作為下一個的輸入。

        參數:
            agents: Agent 列表（按執行順序）
            task: 初始任務

        返回:
            每個 Agent 的輸出列表
        """
        logger.info(f"執行串行工作流，共 {len(agents)} 個 Agent")

        print(f"\n{'='*60}")
        print(f"串行工作流")
        print(f"Agent 數量: {len(agents)}")
        print(f"{'='*60}\n")

        results = []
        current_input = task

        for i, agent in enumerate(agents, 1):
            print(f"\n--- 階段 {i}: {agent.name} ---")
            print(f"輸入: {current_input[:100]}...\n")

            response = agent.run(current_input)
            output = response.content if hasattr(response, 'content') else str(response)

            print(f"輸出: {output[:200]}...\n")

            results.append(output)
            current_input = output  # 下一個 Agent 的輸入

        # 記錄任務
        self.task_history.append({
            "timestamp": datetime.now().isoformat(),
            "workflow_type": "sequential",
            "task": task,
            "agents": [agent.name for agent in agents],
            "results": results,
        })

        return results

    def parallel_workflow(
        self,
        agents: List[Agent],
        tasks: List[str]
    ) -> Dict[str, str]:
        """
        並行工作流

        多個 Agent 同時執行不同的任務。

        參數:
            agents: Agent 列表
            tasks: 任務列表（與 agents 對應）

        返回:
            Agent 名稱到輸出的映射
        """
        logger.info(f"執行並行工作流，共 {len(agents)} 個 Agent")

        print(f"\n{'='*60}")
        print(f"並行工作流")
        print(f"並行任務數: {len(tasks)}")
        print(f"{'='*60}\n")

        results = {}

        # 使用線程池並行執行
        with ThreadPoolExecutor(max_workers=len(agents)) as executor:
            # 提交所有任務
            future_to_agent = {
                executor.submit(self._run_agent, agent, task): (agent, task)
                for agent, task in zip(agents, tasks)
            }

            # 收集結果
            for future in as_completed(future_to_agent):
                agent, task = future_to_agent[future]
                try:
                    result = future.result()
                    results[agent.name] = result
                    print(f"✓ {agent.name} 完成")
                except Exception as e:
                    logger.error(f"{agent.name} 執行失敗: {e}")
                    results[agent.name] = f"錯誤: {e}"

        # 記錄任務
        self.task_history.append({
            "timestamp": datetime.now().isoformat(),
            "workflow_type": "parallel",
            "tasks": tasks,
            "agents": [agent.name for agent in agents],
            "results": results,
        })

        return results

    def _run_agent(self, agent: Agent, task: str) -> str:
        """
        運行單個 Agent（內部方法）

        參數:
            agent: Agent 實例
            task: 任務

        返回:
            Agent 輸出
        """
        response = agent.run(task)
        return response.content if hasattr(response, 'content') else str(response)

    def hierarchical_workflow(
        self,
        leader: Agent,
        task: str
    ) -> str:
        """
        分層工作流

        由領導 Agent 協調團隊成員完成任務。

        參數:
            leader: 領導 Agent（包含團隊成員）
            task: 任務

        返回:
            最終結果
        """
        logger.info("執行分層工作流")

        print(f"\n{'='*60}")
        print(f"分層工作流")
        print(f"領導: {leader.name}")
        print(f"{'='*60}\n")

        print(f"任務: {task}\n")

        response = leader.run(task)
        result = response.content if hasattr(response, 'content') else str(response)

        print(f"\n最終結果:\n{result}\n")

        # 記錄任務
        self.task_history.append({
            "timestamp": datetime.now().isoformat(),
            "workflow_type": "hierarchical",
            "task": task,
            "leader": leader.name,
            "result": result,
        })

        return result

    def collaborative_workflow(
        self,
        agents: List[Agent],
        task: str,
        iterations: int = 2
    ) -> List[str]:
        """
        協作工作流

        Agent 們協作完成任務，互相審核和改進。

        參數:
            agents: Agent 列表
            task: 任務
            iterations: 迭代次數

        返回:
            每次迭代的結果
        """
        logger.info(f"執行協作工作流，迭代 {iterations} 次")

        print(f"\n{'='*60}")
        print(f"協作工作流")
        print(f"迭代次數: {iterations}")
        print(f"{'='*60}\n")

        results = []
        current_work = task

        for i in range(iterations):
            print(f"\n=== 迭代 {i + 1} ===\n")

            iteration_results = []

            for agent in agents:
                print(f"--- {agent.name} ---")
                response = agent.run(f"任務: {current_work}\n\n之前的工作成果:\n{iteration_results[-1] if iteration_results else '無'}")
                output = response.content if hasattr(response, 'content') else str(response)
                iteration_results.append(output)
                print(f"{output[:200]}...\n")

            # 使用最後一個 Agent 的輸出作為下一次迭代的輸入
            current_work = iteration_results[-1]
            results.append(current_work)

        # 記錄任務
        self.task_history.append({
            "timestamp": datetime.now().isoformat(),
            "workflow_type": "collaborative",
            "task": task,
            "iterations": iterations,
            "agents": [agent.name for agent in agents],
            "results": results,
        })

        return results

    def research_and_report_workflow(
        self,
        topic: str
    ) -> str:
        """
        研究和報告工作流

        完整的研究到報告生成流程。

        參數:
            topic: 研究主題

        返回:
            最終報告
        """
        logger.info(f"執行研究和報告工作流: {topic}")

        print(f"\n{'='*60}")
        print(f"研究和報告工作流")
        print(f"主題: {topic}")
        print(f"{'='*60}\n")

        # 創建團隊
        researcher = self.create_researcher_agent()
        analyst = self.create_analyst_agent()
        writer = self.create_writer_agent()
        reviewer = self.create_reviewer_agent()

        # 階段 1: 研究
        print("\n--- 階段 1: 信息研究 ---")
        research_task = f"請研究「{topic}」的相關信息，包括最新發展、關鍵數據和重要事件。"
        research_result = self._run_agent(researcher, research_task)
        print(f"研究完成\n")

        # 階段 2: 分析
        print("\n--- 階段 2: 數據分析 ---")
        analysis_task = f"基於以下研究結果，進行深入分析：\n\n{research_result}\n\n請提供洞察和結論。"
        analysis_result = self._run_agent(analyst, analysis_task)
        print(f"分析完成\n")

        # 階段 3: 撰寫
        print("\n--- 階段 3: 報告撰寫 ---")
        writing_task = f"基於以下研究和分析，撰寫一份專業報告：\n\n研究結果:\n{research_result}\n\n分析結果:\n{analysis_result}"
        report_draft = self._run_agent(writer, writing_task)
        print(f"報告撰寫完成\n")

        # 階段 4: 審核
        print("\n--- 階段 4: 質量審核 ---")
        review_task = f"請審核以下報告，提供改進建議：\n\n{report_draft}"
        review_result = self._run_agent(reviewer, review_task)
        print(f"審核完成\n")

        # 階段 5: 最終修訂
        print("\n--- 階段 5: 最終修訂 ---")
        final_task = f"根據審核意見修訂報告：\n\n原報告:\n{report_draft}\n\n審核意見:\n{review_result}"
        final_report = self._run_agent(writer, final_task)
        print(f"最終報告完成\n")

        # 記錄任務
        self.task_history.append({
            "timestamp": datetime.now().isoformat(),
            "workflow_type": "research_and_report",
            "topic": topic,
            "stages": [
                "研究", "分析", "撰寫", "審核", "修訂"
            ],
            "final_report": final_report,
        })

        return final_report

    def save_task_history(self, filepath: str) -> None:
        """
        保存任務歷史

        參數:
            filepath: 保存路徑
        """
        logger.info(f"保存任務歷史: {filepath}")

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.task_history, f, ensure_ascii=False, indent=2)

        print(f"\n任務歷史已保存到: {filepath}")


def demonstration_sequential_workflow():
    """
    演示串行工作流
    """
    print("\n" + "="*60)
    print("演示 1: 串行工作流")
    print("="*60)

    team = MultiAgentTeam()

    # 創建工作流: 研究 -> 分析 -> 撰寫
    researcher = team.create_researcher_agent()
    analyst = team.create_analyst_agent()
    writer = team.create_writer_agent()

    agents = [researcher, analyst, writer]
    task = "請研究人工智能在醫療領域的應用"

    results = team.sequential_workflow(agents, task)

    print(f"\n最終結果:\n{results[-1]}")


def demonstration_parallel_workflow():
    """
    演示並行工作流
    """
    print("\n" + "="*60)
    print("演示 2: 並行工作流")
    print("="*60)

    team = MultiAgentTeam()

    # 創建多個研究員，同時研究不同主題
    agents = [
        team.create_researcher_agent(),
        team.create_researcher_agent(),
        team.create_researcher_agent(),
    ]

    tasks = [
        "研究 GPT-4 的特點",
        "研究 Claude 的特點",
        "研究 Gemini 的特點",
    ]

    results = team.parallel_workflow(agents, tasks)

    print(f"\n所有研究完成！")
    for agent_name, result in results.items():
        print(f"\n{agent_name}:\n{result[:200]}...")


def demonstration_hierarchical_workflow():
    """
    演示分層工作流
    """
    print("\n" + "="*60)
    print("演示 3: 分層工作流（團隊協作）")
    print("="*60)

    team = MultiAgentTeam()

    # 創建團隊
    team_members = [
        team.create_researcher_agent(),
        team.create_analyst_agent(),
        team.create_writer_agent(),
    ]

    # 創建領導
    leader = team.create_team_leader(team_members)

    # 執行任務
    task = "分析並撰寫關於量子計算發展現狀的專業報告"
    result = team.hierarchical_workflow(leader, task)

    print(f"\n團隊協作完成！")


def demonstration_research_workflow():
    """
    演示完整的研究和報告工作流
    """
    print("\n" + "="*60)
    print("演示 4: 研究和報告工作流")
    print("="*60)

    team = MultiAgentTeam()

    # 執行完整工作流
    report = team.research_and_report_workflow("區塊鏈技術在金融領域的應用")

    print(f"\n最終報告:\n{report}")


def main():
    """
    主函數
    """
    print("\n" + "="*60)
    print("PhiData 多 Agent 團隊協作 - 完整示例")
    print("="*60)

    try:
        # 運行演示
        demonstration_sequential_workflow()
        demonstration_parallel_workflow()
        demonstration_hierarchical_workflow()
        demonstration_research_workflow()

        # 保存歷史
        team = MultiAgentTeam()
        team.save_task_history("multi_agent_history.json")

        print("\n" + "="*60)
        print("所有演示完成！")
        print("="*60)

        print("\n多 Agent 協作優勢：")
        print("1. 分工明確，提高效率")
        print("2. 並行處理，節省時間")
        print("3. 專業分工，提升質量")
        print("4. 協作互補，完善結果")

    except Exception as e:
        logger.error(f"運行錯誤: {e}")
        print(f"\n錯誤: {e}")


if __name__ == "__main__":
    main()
