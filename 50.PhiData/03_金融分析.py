"""
PhiData 金融分析 Agent 示例

這個腳本展示了如何使用 PhiData 創建金融分析 Agent，包括：
1. 股票數據獲取
2. 財務指標分析
3. 市場趨勢分析
4. 投資組合評估
5. 風險評估
6. 技術分析
7. 基本面分析
8. 多股票比較
9. 財報解讀
10. 投資建議生成

作者: PhiData Team
日期: 2025
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import yfinance as yf
import pandas as pd

# PhiData 核心導入
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.yfinance import YFinanceTools
from phi.utils.log import logger

# 環境變量管理
from dotenv import load_dotenv

# 載入環境變量
load_dotenv()


class FinancialAnalysisAgent:
    """
    金融分析 Agent 類

    提供全面的金融分析功能，包括股票分析、市場研究、投資建議等。
    整合 YFinance 工具獲取實時金融數據。
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化金融分析 Agent

        參數:
            api_key: OpenAI API 密鑰
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("未找到 OPENAI_API_KEY")

        logger.info("初始化金融分析 Agent")

        # 分析歷史
        self.analysis_history: List[Dict[str, Any]] = []

    def create_stock_analyst_agent(self) -> Agent:
        """
        創建股票分析師 Agent

        專注於股票分析和評估。

        返回:
            股票分析師 Agent
        """
        logger.info("創建股票分析師 Agent")

        agent = Agent(
            name="股票分析師",
            model=OpenAIChat(
                id="gpt-4",
                api_key=self.api_key,
                temperature=0.3,  # 較低溫度，專注於數據分析
            ),
            tools=[YFinanceTools()],
            description="專業的股票分析師，提供深入的股票分析和投資建議",
            instructions=[
                "使用 YFinance 工具獲取最新的股票數據",
                "分析股票的基本面和技術面",
                "提供客觀、基於數據的分析",
                "說明投資風險",
                "使用繁體中文回應",
            ],
            show_tool_calls=True,
            markdown=True,
        )

        return agent

    def create_portfolio_manager_agent(self) -> Agent:
        """
        創建投資組合管理 Agent

        專注於投資組合構建和管理。

        返回:
            投資組合管理 Agent
        """
        logger.info("創建投資組合管理 Agent")

        agent = Agent(
            name="投資組合經理",
            model=OpenAIChat(
                id="gpt-4",
                api_key=self.api_key,
                temperature=0.2,
            ),
            tools=[YFinanceTools()],
            description="專業的投資組合經理，擅長資產配置和風險管理",
            instructions=[
                "分析多個資產的表現",
                "提供多元化投資建議",
                "評估投資組合風險",
                "考慮風險收益比",
                "基於現代投資組合理論",
                "使用繁體中文回應",
            ],
            show_tool_calls=True,
            markdown=True,
        )

        return agent

    def create_market_analyst_agent(self) -> Agent:
        """
        創建市場分析 Agent

        專注於市場整體趨勢分析。

        返回:
            市場分析 Agent
        """
        logger.info("創建市場分析 Agent")

        agent = Agent(
            name="市場分析師",
            model=OpenAIChat(
                id="gpt-4",
                api_key=self.api_key,
            ),
            tools=[YFinanceTools()],
            description="市場趨勢專家，分析整體市場動態",
            instructions=[
                "分析市場整體趨勢",
                "識別市場機會和風險",
                "關注宏觀經濟因素",
                "提供前瞻性見解",
                "使用繁體中文回應",
            ],
            show_tool_calls=True,
            markdown=True,
        )

        return agent

    def analyze_stock(
        self,
        agent: Agent,
        symbol: str,
        analysis_type: str = "comprehensive"
    ) -> str:
        """
        分析單一股票

        參數:
            agent: Agent 實例
            symbol: 股票代碼
            analysis_type: 分析類型（comprehensive/technical/fundamental）

        返回:
            分析報告
        """
        logger.info(f"分析股票: {symbol} (類型: {analysis_type})")

        print(f"\n{'='*60}")
        print(f"股票分析: {symbol}")
        print(f"分析類型: {analysis_type}")
        print(f"{'='*60}\n")

        # 根據分析類型構建查詢
        if analysis_type == "comprehensive":
            query = f"""
            請對股票 {symbol} 進行全面分析，包括：

            1. 基本資料（公司名稱、產業、市值等）
            2. 當前股價和歷史表現
            3. 財務指標（PE、PB、股息率等）
            4. 技術指標分析
            5. 近期新聞和事件
            6. 投資建議和風險評估

            請提供詳細、客觀的分析報告。
            """
        elif analysis_type == "technical":
            query = f"""
            請對股票 {symbol} 進行技術分析：

            1. 價格趨勢（短期、中期、長期）
            2. 支撐位和壓力位
            3. 技術指標（RSI、MACD、均線等）
            4. 成交量分析
            5. 圖表形態
            6. 交易建議
            """
        else:  # fundamental
            query = f"""
            請對股票 {symbol} 進行基本面分析：

            1. 公司業務和競爭優勢
            2. 財務健康狀況
            3. 盈利能力分析
            4. 成長性評估
            5. 估值分析
            6. 長期投資價值
            """

        response = agent.run(query)
        result = response.content if hasattr(response, 'content') else str(response)

        # 記錄分析
        self.analysis_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "stock_analysis",
            "symbol": symbol,
            "analysis_type": analysis_type,
            "result": result,
        })

        return result

    def compare_stocks(
        self,
        agent: Agent,
        symbols: List[str]
    ) -> str:
        """
        比較多個股票

        參數:
            agent: Agent 實例
            symbols: 股票代碼列表

        返回:
            比較分析報告
        """
        logger.info(f"比較股票: {', '.join(symbols)}")

        print(f"\n{'='*60}")
        print(f"股票比較分析")
        print(f"股票: {', '.join(symbols)}")
        print(f"{'='*60}\n")

        query = f"""
        請比較以下股票：{', '.join(symbols)}

        比較維度：
        1. 基本資料和市值
        2. 股價表現（YTD、1年、5年）
        3. 財務指標比較
        4. 估值比較
        5. 風險收益特徵
        6. 投資建議

        請以表格形式展示關鍵指標，並提供詳細的比較分析。
        """

        response = agent.run(query)
        result = response.content if hasattr(response, 'content') else str(response)

        self.analysis_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "stock_comparison",
            "symbols": symbols,
            "result": result,
        })

        return result

    def analyze_portfolio(
        self,
        agent: Agent,
        holdings: Dict[str, float]
    ) -> str:
        """
        分析投資組合

        參數:
            agent: Agent 實例
            holdings: 持股字典 {股票代碼: 權重/數量}

        返回:
            投資組合分析報告
        """
        logger.info(f"分析投資組合，共 {len(holdings)} 個持股")

        print(f"\n{'='*60}")
        print(f"投資組合分析")
        print(f"持股數量: {len(holdings)}")
        print(f"{'='*60}\n")

        holdings_str = "\n".join([
            f"- {symbol}: {weight}" for symbol, weight in holdings.items()
        ])

        query = f"""
        請分析以下投資組合：

        {holdings_str}

        分析內容：
        1. 組合整體表現
        2. 資產配置評估
        3. 風險分散情況
        4. 各持股貢獻度
        5. 相關性分析
        6. 再平衡建議
        7. 風險評估
        8. 優化建議

        請提供詳細的投資組合分析報告。
        """

        response = agent.run(query)
        result = response.content if hasattr(response, 'content') else str(response)

        self.analysis_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "portfolio_analysis",
            "holdings": holdings,
            "result": result,
        })

        return result

    def market_overview(self, agent: Agent) -> str:
        """
        市場概況分析

        參數:
            agent: Agent 實例

        返回:
            市場概況報告
        """
        logger.info("分析市場概況")

        print(f"\n{'='*60}")
        print(f"市場概況分析")
        print(f"{'='*60}\n")

        query = """
        請提供當前市場概況分析：

        1. 主要指數表現（S&P 500, NASDAQ, Dow Jones）
        2. 市場情緒和趨勢
        3. 熱門板塊和個股
        4. 市場風險因素
        5. 近期重要經濟數據
        6. 投資機會和建議

        請提供全面的市場分析報告。
        """

        response = agent.run(query)
        result = response.content if hasattr(response, 'content') else str(response)

        self.analysis_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "market_overview",
            "result": result,
        })

        return result

    def sector_analysis(self, agent: Agent, sector: str) -> str:
        """
        行業分析

        參數:
            agent: Agent 實例
            sector: 行業名稱

        返回:
            行業分析報告
        """
        logger.info(f"分析行業: {sector}")

        print(f"\n{'='*60}")
        print(f"行業分析: {sector}")
        print(f"{'='*60}\n")

        query = f"""
        請對{sector}行業進行深入分析：

        1. 行業概況和規模
        2. 主要公司和市場份額
        3. 行業趨勢和驅動因素
        4. 增長前景
        5. 風險和挑戰
        6. 投資機會
        7. 推薦股票

        請提供專業的行業分析報告。
        """

        response = agent.run(query)
        result = response.content if hasattr(response, 'content') else str(response)

        self.analysis_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "sector_analysis",
            "sector": sector,
            "result": result,
        })

        return result

    def risk_assessment(
        self,
        agent: Agent,
        symbol: str
    ) -> str:
        """
        風險評估

        參數:
            agent: Agent 實例
            symbol: 股票代碼

        返回:
            風險評估報告
        """
        logger.info(f"風險評估: {symbol}")

        print(f"\n{'='*60}")
        print(f"風險評估: {symbol}")
        print(f"{'='*60}\n")

        query = f"""
        請對股票 {symbol} 進行全面的風險評估：

        1. 市場風險（Beta、波動率）
        2. 業務風險（商業模式、競爭）
        3. 財務風險（負債、流動性）
        4. 管理風險
        5. 監管和法律風險
        6. 宏觀經濟風險
        7. 整體風險評級
        8. 風險緩解建議

        請提供詳細的風險分析報告。
        """

        response = agent.run(query)
        result = response.content if hasattr(response, 'content') else str(response)

        self.analysis_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "risk_assessment",
            "symbol": symbol,
            "result": result,
        })

        return result

    def earnings_analysis(
        self,
        agent: Agent,
        symbol: str
    ) -> str:
        """
        財報分析

        參數:
            agent: Agent 實例
            symbol: 股票代碼

        返回:
            財報分析報告
        """
        logger.info(f"財報分析: {symbol}")

        print(f"\n{'='*60}")
        print(f"財報分析: {symbol}")
        print(f"{'='*60}\n")

        query = f"""
        請分析股票 {symbol} 的最新財報：

        1. 營收和盈利表現
        2. 同比和環比變化
        3. 毛利率和淨利率
        4. EPS 和市場預期比較
        5. 資產負債表分析
        6. 現金流分析
        7. 關鍵業務指標
        8. 管理層指引
        9. 財報後股價反應
        10. 投資建議

        請提供深入的財報解讀。
        """

        response = agent.run(query)
        result = response.content if hasattr(response, 'content') else str(response)

        self.analysis_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "earnings_analysis",
            "symbol": symbol,
            "result": result,
        })

        return result

    def investment_strategy(
        self,
        agent: Agent,
        profile: Dict[str, Any]
    ) -> str:
        """
        投資策略建議

        參數:
            agent: Agent 實例
            profile: 投資者檔案

        返回:
            投資策略建議
        """
        logger.info("生成投資策略建議")

        print(f"\n{'='*60}")
        print(f"投資策略建議")
        print(f"{'='*60}\n")

        profile_str = json.dumps(profile, ensure_ascii=False, indent=2)

        query = f"""
        基於以下投資者檔案，請提供個性化的投資策略建議：

        {profile_str}

        建議內容：
        1. 適合的投資風格
        2. 資產配置建議
        3. 推薦的投資產品
        4. 具體股票建議
        5. 風險管理策略
        6. 再平衡頻率
        7. 稅務優化建議
        8. 長期規劃

        請提供專業、個性化的投資建議。
        """

        response = agent.run(query)
        result = response.content if hasattr(response, 'content') else str(response)

        self.analysis_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "investment_strategy",
            "profile": profile,
            "result": result,
        })

        return result

    def generate_analysis_report(self, filepath: str) -> None:
        """
        生成分析報告

        參數:
            filepath: 報告保存路徑
        """
        logger.info(f"生成分析報告: {filepath}")

        report = "# 金融分析報告\n\n"
        report += f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += f"總分析次數: {len(self.analysis_history)}\n\n"
        report += "---\n\n"

        for i, analysis in enumerate(self.analysis_history, 1):
            report += f"## 分析 {i}: {analysis['type']}\n\n"
            report += f"**時間**: {analysis['timestamp']}\n\n"

            # 添加特定字段
            for key, value in analysis.items():
                if key not in ['timestamp', 'type', 'result']:
                    report += f"**{key}**: {value}\n\n"

            report += f"**分析結果**:\n\n{analysis['result']}\n\n"
            report += "---\n\n"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n分析報告已生成: {filepath}")


def demonstration_stock_analysis():
    """
    演示股票分析
    """
    print("\n" + "="*60)
    print("演示 1: 股票分析")
    print("="*60)

    fin_agent = FinancialAnalysisAgent()
    agent = fin_agent.create_stock_analyst_agent()

    # 分析蘋果公司股票
    result = fin_agent.analyze_stock(
        agent,
        "AAPL",
        analysis_type="comprehensive"
    )
    print(f"\n{result}")


def demonstration_stock_comparison():
    """
    演示股票比較
    """
    print("\n" + "="*60)
    print("演示 2: 股票比較")
    print("="*60)

    fin_agent = FinancialAnalysisAgent()
    agent = fin_agent.create_stock_analyst_agent()

    # 比較科技股
    result = fin_agent.compare_stocks(
        agent,
        ["AAPL", "MSFT", "GOOGL"]
    )
    print(f"\n{result}")


def demonstration_portfolio_analysis():
    """
    演示投資組合分析
    """
    print("\n" + "="*60)
    print("演示 3: 投資組合分析")
    print("="*60)

    fin_agent = FinancialAnalysisAgent()
    agent = fin_agent.create_portfolio_manager_agent()

    # 分析投資組合
    portfolio = {
        "AAPL": 0.3,
        "MSFT": 0.25,
        "GOOGL": 0.2,
        "AMZN": 0.15,
        "NVDA": 0.1,
    }

    result = fin_agent.analyze_portfolio(agent, portfolio)
    print(f"\n{result}")


def demonstration_market_overview():
    """
    演示市場概況
    """
    print("\n" + "="*60)
    print("演示 4: 市場概況")
    print("="*60)

    fin_agent = FinancialAnalysisAgent()
    agent = fin_agent.create_market_analyst_agent()

    result = fin_agent.market_overview(agent)
    print(f"\n{result}")


def demonstration_sector_analysis():
    """
    演示行業分析
    """
    print("\n" + "="*60)
    print("演示 5: 行業分析")
    print("="*60)

    fin_agent = FinancialAnalysisAgent()
    agent = fin_agent.create_market_analyst_agent()

    result = fin_agent.sector_analysis(agent, "人工智能與半導體")
    print(f"\n{result}")


def demonstration_risk_assessment():
    """
    演示風險評估
    """
    print("\n" + "="*60)
    print("演示 6: 風險評估")
    print("="*60)

    fin_agent = FinancialAnalysisAgent()
    agent = fin_agent.create_stock_analyst_agent()

    result = fin_agent.risk_assessment(agent, "TSLA")
    print(f"\n{result}")


def demonstration_investment_strategy():
    """
    演示投資策略
    """
    print("\n" + "="*60)
    print("演示 7: 投資策略建議")
    print("="*60)

    fin_agent = FinancialAnalysisAgent()
    agent = fin_agent.create_portfolio_manager_agent()

    investor_profile = {
        "年齡": 35,
        "風險承受度": "中等",
        "投資期限": "長期（10年以上）",
        "投資目標": "退休儲蓄",
        "初始資金": 100000,
        "月度投入": 5000,
        "投資經驗": "中級",
        "偏好行業": ["科技", "醫療健康"],
    }

    result = fin_agent.investment_strategy(agent, investor_profile)
    print(f"\n{result}")


def main():
    """
    主函數
    """
    print("\n" + "="*60)
    print("PhiData 金融分析 Agent - 完整示例")
    print("="*60)

    try:
        # 運行演示
        demonstration_stock_analysis()
        demonstration_stock_comparison()
        demonstration_portfolio_analysis()
        demonstration_market_overview()
        demonstration_sector_analysis()
        demonstration_risk_assessment()
        demonstration_investment_strategy()

        # 生成報告
        fin_agent = FinancialAnalysisAgent()
        fin_agent.generate_analysis_report("financial_analysis_report.md")

        print("\n" + "="*60)
        print("所有演示完成！")
        print("="*60)

        print("\n免責聲明：")
        print("本示例僅供教育目的，不構成投資建議。")
        print("投資有風險，請謹慎決策。")

    except Exception as e:
        logger.error(f"運行錯誤: {e}")
        print(f"\n錯誤: {e}")


if __name__ == "__main__":
    main()
