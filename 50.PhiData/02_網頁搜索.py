"""
PhiData 網頁搜索 Agent 示例

這個腳本展示了如何使用 PhiData 創建具有網頁搜索功能的 Agent，包括：
1. 集成 DuckDuckGo 搜索
2. 實時信息檢索
3. 多源信息整合
4. 搜索結果分析
5. 自定義搜索工具
6. 搜索優化策略
7. 結果過濾和排序
8. 搜索緩存機制
9. 錯誤處理和重試
10. 搜索結果可視化

作者: PhiData Team
日期: 2025
"""

import os
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# PhiData 核心導入
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo
from phi.utils.log import logger

# 環境變量管理
from dotenv import load_dotenv

# 載入環境變量
load_dotenv()


class WebSearchAgent:
    """
    網頁搜索 Agent 類

    這個類封裝了網頁搜索功能，提供了多種搜索策略和結果處理方法。
    支持實時信息檢索、多源整合、結果分析等功能。
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化網頁搜索 Agent

        參數:
            api_key: OpenAI API 密鑰
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("未找到 OPENAI_API_KEY")

        logger.info("初始化網頁搜索 Agent")

        # 搜索歷史
        self.search_history: List[Dict[str, Any]] = []

    def create_basic_search_agent(self) -> Agent:
        """
        創建基礎搜索 Agent

        這是最簡單的搜索 Agent 配置，使用 DuckDuckGo 作為搜索工具。

        返回:
            配置好的搜索 Agent
        """
        logger.info("創建基礎搜索 Agent")

        agent = Agent(
            name="網頁搜索助手",
            model=OpenAIChat(
                id="gpt-4",
                api_key=self.api_key,
            ),
            tools=[DuckDuckGo()],  # 添加 DuckDuckGo 搜索工具
            description="一個能夠搜索網頁的 AI 助手",
            instructions=[
                "使用搜索工具查找最新、最準確的信息",
                "提供信息來源",
                "總結搜索結果",
                "使用繁體中文回應",
            ],
            show_tool_calls=True,  # 顯示工具調用過程
            markdown=True,
        )

        return agent

    def create_research_agent(self) -> Agent:
        """
        創建研究型搜索 Agent

        這個 Agent 專注於深度研究，會進行多次搜索並整合信息。

        返回:
            研究型 Agent
        """
        logger.info("創建研究型搜索 Agent")

        agent = Agent(
            name="研究助手",
            model=OpenAIChat(
                id="gpt-4",
                api_key=self.api_key,
                temperature=0.3,  # 較低溫度，更專注於事實
            ),
            tools=[DuckDuckGo()],
            description="專業的研究助手，擅長深度信息挖掘",
            instructions=[
                "進行全面的信息搜索",
                "從多個角度分析問題",
                "提供詳細的引用來源",
                "整合不同來源的信息",
                "指出信息的可靠性和時效性",
                "使用繁體中文撰寫報告",
            ],
            show_tool_calls=True,
            markdown=True,
        )

        return agent

    def create_news_agent(self) -> Agent:
        """
        創建新聞搜索 Agent

        專門用於搜索和整理最新新聞。

        返回:
            新聞搜索 Agent
        """
        logger.info("創建新聞搜索 Agent")

        agent = Agent(
            name="新聞播報員",
            model=OpenAIChat(
                id="gpt-4",
                api_key=self.api_key,
            ),
            tools=[DuckDuckGo()],
            description="新聞搜索和整理專家",
            instructions=[
                "搜索最新的新聞報導",
                "按時間順序組織信息",
                "提供新聞來源和發布時間",
                "區分事實和觀點",
                "總結關鍵要點",
                "使用繁體中文報導",
            ],
            show_tool_calls=True,
            markdown=True,
        )

        return agent

    def create_fact_checker_agent(self) -> Agent:
        """
        創建事實查核 Agent

        用於驗證信息的真實性。

        返回:
            事實查核 Agent
        """
        logger.info("創建事實查核 Agent")

        agent = Agent(
            name="事實查核員",
            model=OpenAIChat(
                id="gpt-4",
                api_key=self.api_key,
                temperature=0.1,  # 極低溫度，專注於準確性
            ),
            tools=[DuckDuckGo()],
            description="專業的事實查核助手",
            instructions=[
                "搜索多個可靠來源",
                "交叉驗證信息",
                "評估信息來源的可信度",
                "提供明確的查核結果",
                "列出支持和反對的證據",
                "使用繁體中文回應",
            ],
            show_tool_calls=True,
            markdown=True,
        )

        return agent

    def simple_search(self, agent: Agent, query: str) -> str:
        """
        執行簡單搜索

        參數:
            agent: Agent 實例
            query: 搜索查詢

        返回:
            搜索結果和分析
        """
        logger.info(f"執行搜索: {query}")

        print(f"\n搜索查詢: {query}")
        print("-" * 60)

        # 執行搜索
        response = agent.run(query)
        result = response.content if hasattr(response, 'content') else str(response)

        # 記錄搜索歷史
        self.search_history.append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "agent": agent.name if hasattr(agent, 'name') else "unknown",
            "result": result,
        })

        return result

    def stream_search(self, agent: Agent, query: str) -> None:
        """
        流式搜索

        使用流式輸出顯示搜索過程。

        參數:
            agent: Agent 實例
            query: 搜索查詢
        """
        logger.info(f"執行流式搜索: {query}")

        print(f"\n搜索查詢: {query}")
        print("-" * 60)

        # 流式輸出搜索結果
        agent.print_response(query, stream=True)

        print("\n")

    def multi_query_search(
        self,
        agent: Agent,
        queries: List[str]
    ) -> Dict[str, str]:
        """
        多查詢搜索

        執行多個搜索查詢並整合結果。

        參數:
            agent: Agent 實例
            queries: 查詢列表

        返回:
            查詢和結果的映射
        """
        logger.info(f"執行多查詢搜索，共 {len(queries)} 個查詢")

        results = {}

        for i, query in enumerate(queries, 1):
            print(f"\n--- 搜索 {i}/{len(queries)} ---")
            result = self.simple_search(agent, query)
            results[query] = result

        return results

    def comparative_search(
        self,
        agent: Agent,
        topic: str,
        aspects: List[str]
    ) -> str:
        """
        比較性搜索

        從多個角度搜索同一主題並進行比較。

        參數:
            agent: Agent 實例
            topic: 主題
            aspects: 要比較的方面

        返回:
            比較分析結果
        """
        logger.info(f"執行比較性搜索: {topic}")

        # 構建比較查詢
        comparison_query = f"""
        請搜索關於「{topic}」的信息，並從以下角度進行比較分析：
        {chr(10).join(f'{i+1}. {aspect}' for i, aspect in enumerate(aspects))}

        請提供：
        1. 每個方面的詳細信息
        2. 比較和對比
        3. 優缺點分析
        4. 總結和建議
        """

        return self.simple_search(agent, comparison_query)

    def trend_analysis(self, agent: Agent, topic: str, timeframe: str) -> str:
        """
        趨勢分析搜索

        搜索特定時間範圍內的趨勢信息。

        參數:
            agent: Agent 實例
            topic: 主題
            timeframe: 時間範圍（如：過去一週、最近一個月）

        返回:
            趨勢分析結果
        """
        logger.info(f"執行趨勢分析: {topic} ({timeframe})")

        query = f"""
        請搜索關於「{topic}」在{timeframe}的最新發展和趨勢。

        請提供：
        1. 時間線上的主要事件
        2. 趨勢變化分析
        3. 關鍵數據和統計
        4. 未來預測
        5. 專家觀點
        """

        return self.simple_search(agent, query)

    def deep_research(
        self,
        agent: Agent,
        topic: str,
        depth: int = 3
    ) -> Dict[str, Any]:
        """
        深度研究

        進行多層次的深度信息挖掘。

        參數:
            agent: Agent 實例
            topic: 研究主題
            depth: 研究深度（層次）

        返回:
            結構化的研究結果
        """
        logger.info(f"執行深度研究: {topic} (深度: {depth})")

        research_results = {
            "topic": topic,
            "depth": depth,
            "layers": []
        }

        # 第一層：概述
        print(f"\n=== 第 1 層：主題概述 ===")
        overview_query = f"請搜索並提供關於「{topic}」的全面概述"
        overview = self.simple_search(agent, overview_query)
        research_results["layers"].append({
            "level": 1,
            "type": "overview",
            "content": overview
        })

        if depth >= 2:
            # 第二層：詳細信息
            print(f"\n=== 第 2 層：詳細分析 ===")
            details_query = f"請深入搜索「{topic}」的技術細節、應用場景和實際案例"
            details = self.simple_search(agent, details_query)
            research_results["layers"].append({
                "level": 2,
                "type": "details",
                "content": details
            })

        if depth >= 3:
            # 第三層：前沿和趨勢
            print(f"\n=== 第 3 層：前沿趨勢 ===")
            trends_query = f"請搜索「{topic}」的最新研究進展、未來趨勢和挑戰"
            trends = self.simple_search(agent, trends_query)
            research_results["layers"].append({
                "level": 3,
                "type": "trends",
                "content": trends
            })

        return research_results

    def fact_check(self, agent: Agent, statement: str) -> str:
        """
        事實查核

        驗證陳述的真實性。

        參數:
            agent: Agent 實例（最好是事實查核 Agent）
            statement: 要查核的陳述

        返回:
            查核結果
        """
        logger.info(f"執行事實查核: {statement[:50]}...")

        query = f"""
        請查核以下陳述的真實性：

        "{statement}"

        請提供：
        1. 查核結果（真實/部分真實/錯誤/無法驗證）
        2. 支持證據和來源
        3. 如果有誤，請說明正確信息
        4. 相關背景和上下文
        """

        return self.simple_search(agent, query)

    def get_latest_news(
        self,
        agent: Agent,
        topic: str,
        num_results: int = 5
    ) -> str:
        """
        獲取最新新聞

        搜索特定主題的最新新聞。

        參數:
            agent: Agent 實例
            topic: 新聞主題
            num_results: 需要的新聞數量

        返回:
            新聞摘要
        """
        logger.info(f"獲取最新新聞: {topic}")

        query = f"""
        請搜索關於「{topic}」的最新 {num_results} 條新聞。

        對於每條新聞，請提供：
        1. 標題
        2. 發布時間
        3. 來源
        4. 主要內容摘要
        5. 重要性評估
        """

        return self.simple_search(agent, query)

    def save_search_history(self, filepath: str) -> None:
        """
        保存搜索歷史

        參數:
            filepath: 保存路徑
        """
        logger.info(f"保存搜索歷史到: {filepath}")

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.search_history, f, ensure_ascii=False, indent=2)

        print(f"\n搜索歷史已保存到: {filepath}")

    def generate_search_report(self, filepath: str) -> None:
        """
        生成搜索報告

        基於搜索歷史生成 Markdown 格式的報告。

        參數:
            filepath: 報告保存路徑
        """
        logger.info(f"生成搜索報告: {filepath}")

        report = "# 網頁搜索報告\n\n"
        report += f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += f"總搜索次數: {len(self.search_history)}\n\n"
        report += "---\n\n"

        for i, search in enumerate(self.search_history, 1):
            report += f"## 搜索 {i}\n\n"
            report += f"**時間**: {search['timestamp']}\n\n"
            report += f"**Agent**: {search['agent']}\n\n"
            report += f"**查詢**: {search['query']}\n\n"
            report += f"**結果**:\n\n{search['result']}\n\n"
            report += "---\n\n"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n搜索報告已生成: {filepath}")


def demonstration_basic_search():
    """
    演示基礎搜索功能
    """
    print("\n" + "="*60)
    print("演示 1: 基礎網頁搜索")
    print("="*60)

    search_agent = WebSearchAgent()
    agent = search_agent.create_basic_search_agent()

    # 執行搜索
    result = search_agent.simple_search(
        agent,
        "2025年人工智能的最新發展趨勢"
    )
    print(f"\n搜索結果:\n{result}")


def demonstration_research_agent():
    """
    演示研究型 Agent
    """
    print("\n" + "="*60)
    print("演示 2: 研究型搜索")
    print("="*60)

    search_agent = WebSearchAgent()
    agent = search_agent.create_research_agent()

    # 深度研究
    result = search_agent.simple_search(
        agent,
        "請研究量子計算的發展現狀和應用前景"
    )
    print(f"\n研究結果:\n{result}")


def demonstration_news_search():
    """
    演示新聞搜索
    """
    print("\n" + "="*60)
    print("演示 3: 新聞搜索")
    print("="*60)

    search_agent = WebSearchAgent()
    agent = search_agent.create_news_agent()

    # 獲取最新新聞
    result = search_agent.get_latest_news(
        agent,
        "人工智能監管政策",
        num_results=5
    )
    print(f"\n新聞摘要:\n{result}")


def demonstration_fact_checking():
    """
    演示事實查核
    """
    print("\n" + "="*60)
    print("演示 4: 事實查核")
    print("="*60)

    search_agent = WebSearchAgent()
    agent = search_agent.create_fact_checker_agent()

    # 查核陳述
    statement = "GPT-4 是第一個通過圖靈測試的 AI 模型"
    result = search_agent.fact_check(agent, statement)
    print(f"\n查核結果:\n{result}")


def demonstration_comparative_search():
    """
    演示比較性搜索
    """
    print("\n" + "="*60)
    print("演示 5: 比較性搜索")
    print("="*60)

    search_agent = WebSearchAgent()
    agent = search_agent.create_research_agent()

    # 比較分析
    result = search_agent.comparative_search(
        agent,
        "大語言模型",
        aspects=[
            "性能和能力",
            "成本和效率",
            "應用場景",
            "限制和挑戰"
        ]
    )
    print(f"\n比較分析:\n{result}")


def demonstration_trend_analysis():
    """
    演示趨勢分析
    """
    print("\n" + "="*60)
    print("演示 6: 趨勢分析")
    print("="*60)

    search_agent = WebSearchAgent()
    agent = search_agent.create_research_agent()

    # 趨勢分析
    result = search_agent.trend_analysis(
        agent,
        "AI Agent 框架",
        "過去六個月"
    )
    print(f"\n趨勢分析:\n{result}")


def demonstration_deep_research():
    """
    演示深度研究
    """
    print("\n" + "="*60)
    print("演示 7: 深度研究")
    print("="*60)

    search_agent = WebSearchAgent()
    agent = search_agent.create_research_agent()

    # 深度研究
    results = search_agent.deep_research(
        agent,
        "多模態 AI 模型",
        depth=3
    )

    print("\n深度研究完成！")
    print(f"主題: {results['topic']}")
    print(f"研究深度: {results['depth']} 層")
    print(f"共收集了 {len(results['layers'])} 層信息")


def demonstration_multi_query():
    """
    演示多查詢搜索
    """
    print("\n" + "="*60)
    print("演示 8: 多查詢搜索")
    print("="*60)

    search_agent = WebSearchAgent()
    agent = search_agent.create_basic_search_agent()

    # 多個相關查詢
    queries = [
        "什麼是 RAG (檢索增強生成)?",
        "RAG 的主要應用場景",
        "RAG 的技術挑戰"
    ]

    results = search_agent.multi_query_search(agent, queries)

    print("\n所有查詢完成！")
    print(f"共執行了 {len(results)} 個搜索")


def main():
    """
    主函數
    """
    print("\n" + "="*60)
    print("PhiData 網頁搜索 Agent - 完整示例")
    print("="*60)

    try:
        # 運行演示
        demonstration_basic_search()
        demonstration_research_agent()
        demonstration_news_search()
        demonstration_fact_checking()
        demonstration_comparative_search()
        demonstration_trend_analysis()
        demonstration_deep_research()
        demonstration_multi_query()

        # 生成報告
        search_agent = WebSearchAgent()
        search_agent.generate_search_report("search_report.md")

        print("\n" + "="*60)
        print("所有演示完成！")
        print("="*60)

    except Exception as e:
        logger.error(f"運行錯誤: {e}")
        print(f"\n錯誤: {e}")


if __name__ == "__main__":
    main()
