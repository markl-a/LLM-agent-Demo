"""
SuperAGI 快速開始示例

這個示例展示了如何:
1. 安裝和配置 SuperAGI
2. 創建第一個 Agent
3. 設置基本目標
4. 運行 Agent
5. 查看執行結果

SuperAGI 是一個生產就緒的開源 AI Agent 框架，提供圖形界面和豐富的工具生態系統。
"""

import os
from typing import List, Dict
from datetime import datetime


# ==================== 配置管理 ====================

class SuperAGIConfig:
    """SuperAGI 配置管理"""

    def __init__(self):
        """初始化配置"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "your-api-key")
        self.database_url = os.getenv("DATABASE_URL", "postgresql://localhost/superagi")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

        # Agent 默認配置
        self.default_model = "gpt-4"
        self.default_max_iterations = 25
        self.default_budget = 10.0
        self.default_timeout = 1800  # 30 分鐘

    def validate(self) -> bool:
        """驗證配置"""
        if not self.openai_api_key or self.openai_api_key == "your-api-key":
            print("❌ 請設置 OPENAI_API_KEY 環境變量")
            return False

        print("✅ 配置驗證通過")
        return True

    def display(self):
        """顯示配置"""
        print("\n=== SuperAGI 配置 ===")
        print(f"模型: {self.default_model}")
        print(f"最大迭代: {self.default_max_iterations}")
        print(f"預算: ${self.default_budget}")
        print(f"超時: {self.default_timeout}s")
        print("=" * 50)


# ==================== Agent 配置 ====================

class AgentConfig:
    """Agent 配置類"""

    def __init__(
        self,
        name: str,
        description: str,
        goals: List[str],
        tools: List[str] = None,
        model: str = "gpt-4",
        max_iterations: int = 25,
        budget: float = 10.0
    ):
        """
        初始化 Agent 配置

        參數:
            name: Agent 名稱
            description: Agent 描述
            goals: 目標列表
            tools: 工具列表
            model: 使用的 LLM 模型
            max_iterations: 最大迭代次數
            budget: 預算限制
        """
        self.name = name
        self.description = description
        self.goals = goals
        self.tools = tools or ["GoogleSearchTool", "FileWriteTool"]
        self.model = model
        self.max_iterations = max_iterations
        self.budget = budget
        self.created_at = datetime.now()

    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            "name": self.name,
            "description": self.description,
            "goals": self.goals,
            "tools": self.tools,
            "model": self.model,
            "max_iterations": self.max_iterations,
            "budget": self.budget,
            "created_at": self.created_at.isoformat()
        }

    def display(self):
        """顯示配置"""
        print(f"\n=== Agent 配置: {self.name} ===")
        print(f"描述: {self.description}")
        print(f"\n目標 ({len(self.goals)} 個):")
        for i, goal in enumerate(self.goals, 1):
            print(f"  {i}. {goal}")
        print(f"\n工具 ({len(self.tools)} 個):")
        for tool in self.tools:
            print(f"  - {tool}")
        print(f"\n資源限制:")
        print(f"  模型: {self.model}")
        print(f"  最大迭代: {self.max_iterations}")
        print(f"  預算: ${self.budget}")
        print("=" * 50)


# ==================== 簡化的 Agent 實現 ====================

class SimpleAgent:
    """
    簡化的 SuperAGI Agent 實現
    (實際的 SuperAGI 會更複雜，這裡是教學示例)
    """

    def __init__(self, config: AgentConfig):
        """
        初始化 Agent

        參數:
            config: Agent 配置
        """
        self.config = config
        self.iteration = 0
        self.used_budget = 0.0
        self.execution_log = []
        self.status = "initialized"

    def run(self) -> Dict:
        """
        運行 Agent

        返回:
            執行結果
        """
        print(f"\n🚀 啟動 Agent: {self.config.name}")
        print("=" * 50)

        self.status = "running"
        results = []

        try:
            # 執行每個目標
            for i, goal in enumerate(self.config.goals, 1):
                print(f"\n📌 執行目標 {i}/{len(self.config.goals)}: {goal}")

                # 模擬執行
                result = self._execute_goal(goal)
                results.append(result)

                # 檢查預算和迭代
                if self.used_budget >= self.config.budget:
                    print("\n⚠️  達到預算限制，停止執行")
                    break

                if self.iteration >= self.config.max_iterations:
                    print("\n⚠️  達到最大迭代次數，停止執行")
                    break

            self.status = "completed"
            print("\n✅ Agent 執行完成")

        except Exception as e:
            self.status = "failed"
            print(f"\n❌ Agent 執行失敗: {e}")
            raise

        # 返回結果
        return {
            "status": self.status,
            "results": results,
            "iterations": self.iteration,
            "budget_used": self.used_budget,
            "execution_log": self.execution_log
        }

    def _execute_goal(self, goal: str) -> Dict:
        """
        執行單個目標

        參數:
            goal: 目標描述

        返回:
            執行結果
        """
        self.iteration += 1

        # 模擬思考過程
        print(f"\n  💭 思考: 分析目標...")
        thought = f"需要使用搜索工具找到相關信息，然後保存結果"

        # 模擬選擇工具
        print(f"  🔧 選擇工具: GoogleSearchTool")
        tool = "GoogleSearchTool"

        # 模擬執行工具
        print(f"  ⚙️  執行工具...")
        tool_result = f"找到了關於 '{goal}' 的 5 個相關結果"

        # 模擬評估
        print(f"  ✓ 評估: 目標部分完成")
        evaluation = "部分完成"

        # 更新成本
        cost = 0.05  # 模擬成本
        self.used_budget += cost

        # 記錄日誌
        log_entry = {
            "iteration": self.iteration,
            "goal": goal,
            "thought": thought,
            "tool": tool,
            "result": tool_result,
            "evaluation": evaluation,
            "cost": cost
        }
        self.execution_log.append(log_entry)

        return {
            "goal": goal,
            "status": "completed",
            "result": tool_result,
            "cost": cost
        }

    def get_summary(self) -> str:
        """
        獲取執行摘要

        返回:
            摘要文本
        """
        summary = f"""
╔══════════════════════════════════════════════════╗
║           Agent 執行摘要                          ║
╠══════════════════════════════════════════════════╣
║ Agent: {self.config.name:40} ║
║ 狀態: {self.status:41} ║
║ 總迭代: {self.iteration:38} ║
║ 使用預算: ${self.used_budget:.2f} / ${self.config.budget:.2f}              ║
║ 完成目標: {len([r for r in self.execution_log if r['status'] == 'completed'])}/{len(self.config.goals):34} ║
╚══════════════════════════════════════════════════╝
        """
        return summary


# ==================== 示例場景 ====================

def example_1_basic_agent():
    """示例 1: 創建基本的 Agent"""
    print("\n" + "=" * 60)
    print("示例 1: 創建基本的 SuperAGI Agent")
    print("=" * 60)

    # 創建配置
    config = AgentConfig(
        name="ResearchAgent",
        description="研究助手，幫助收集和整理信息",
        goals=[
            "搜索關於 AI Agent 的最新資訊",
            "總結主要發展趨勢",
            "生成研究報告"
        ],
        tools=["GoogleSearchTool", "FileWriteTool"],
        max_iterations=10,
        budget=5.0
    )

    # 顯示配置
    config.display()

    # 創建並運行 Agent
    agent = SimpleAgent(config)
    result = agent.run()

    # 顯示摘要
    print(agent.get_summary())


def example_2_data_analysis():
    """示例 2: 數據分析 Agent"""
    print("\n" + "=" * 60)
    print("示例 2: 數據分析 Agent")
    print("=" * 60)

    config = AgentConfig(
        name="DataAnalyzer",
        description="數據分析專家，處理和分析數據",
        goals=[
            "讀取 data.csv 文件",
            "執行統計分析",
            "生成可視化圖表",
            "撰寫分析報告"
        ],
        tools=[
            "FileReadTool",
            "DataAnalysisTool",
            "PlotTool",
            "FileWriteTool"
        ],
        model="gpt-4",
        max_iterations=15,
        budget=8.0
    )

    config.display()

    agent = SimpleAgent(config)
    result = agent.run()

    print(agent.get_summary())


def example_3_code_assistant():
    """示例 3: 代碼助手 Agent"""
    print("\n" + "=" * 60)
    print("示例 3: 代碼助手 Agent")
    print("=" * 60)

    config = AgentConfig(
        name="CodeAssistant",
        description="編程助手，幫助開發和優化代碼",
        goals=[
            "分析現有代碼結構",
            "識別性能瓶頸",
            "提供優化建議",
            "生成改進代碼"
        ],
        tools=[
            "FileReadTool",
            "CodeAnalysisTool",
            "CodeGenerationTool",
            "TestRunnerTool"
        ],
        max_iterations=20,
        budget=10.0
    )

    config.display()

    agent = SimpleAgent(config)
    result = agent.run()

    print(agent.get_summary())


def example_4_with_validation():
    """示例 4: 帶配置驗證的 Agent"""
    print("\n" + "=" * 60)
    print("示例 4: 帶配置驗證的 Agent")
    print("=" * 60)

    # 初始化並驗證系統配置
    sys_config = SuperAGIConfig()
    sys_config.display()

    # 注意: 在實際使用中，如果驗證失敗應該停止
    # if not sys_config.validate():
    #     return

    # 創建 Agent 配置
    config = AgentConfig(
        name="ValidatedAgent",
        description="帶完整驗證的 Agent",
        goals=[
            "執行任務 A",
            "執行任務 B"
        ]
    )

    config.display()

    # 創建並運行
    agent = SimpleAgent(config)
    result = agent.run()

    print(agent.get_summary())


# ==================== 最佳實踐 ====================

def best_practices():
    """最佳實踐示例"""
    print("\n" + "=" * 60)
    print("SuperAGI 最佳實踐")
    print("=" * 60)

    print("""
    1. 明確的目標設置
       ✅ 好: "從 data.csv 讀取數據並計算平均值"
       ❌ 差: "分析數據"

    2. 合理的資源限制
       - 設置適當的 max_iterations (10-25)
       - 設置預算上限防止超支
       - 設置超時時間

    3. 選擇合適的工具
       - 只添加必要的工具
       - 理解每個工具的功能
       - 考慮工具的成本

    4. 監控執行過程
       - 查看執行日誌
       - 跟蹤預算使用
       - 關注錯誤和警告

    5. 漸進式開發
       - 從簡單目標開始
       - 逐步增加複雜度
       - 測試每個階段

    6. 錯誤處理
       - 設置合理的超時
       - 處理工具失敗
       - 提供降級方案

    7. 安全考慮
       - 限制文件訪問
       - 禁止危險操作
       - 審核 Agent 輸出
    """)


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("\n" + "🤖 " * 20)
    print("SuperAGI 快速開始教程")
    print("🤖 " * 20)

    # 運行示例
    try:
        # 示例 1: 基本 Agent
        example_1_basic_agent()

        # 示例 2: 數據分析
        example_2_data_analysis()

        # 示例 3: 代碼助手
        example_3_code_assistant()

        # 示例 4: 配置驗證
        example_4_with_validation()

        # 最佳實踐
        best_practices()

        print("\n" + "=" * 60)
        print("✅ 所有示例執行完成！")
        print("=" * 60)

        print("""
        下一步:
        1. 閱讀 02_工具使用.py 學習工具系統
        2. 訪問 http://localhost:8000 使用 Web 界面
        3. 查看文檔了解更多功能
        4. 嘗試創建自己的 Agent
        """)

    except Exception as e:
        print(f"\n❌ 執行出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


# ==================== 補充說明 ====================

"""
SuperAGI 與其他框架的對比:

1. AutoGPT:
   - SuperAGI 有圖形界面，AutoGPT 是命令行
   - SuperAGI 更適合企業部署
   - SuperAGI 有更豐富的工具生態

2. LangChain:
   - LangChain 更偏向於開發框架
   - SuperAGI 提供開箱即用的解決方案
   - SuperAGI 有內建的 Agent 管理

3. CrewAI:
   - CrewAI 專注於多 Agent 協作
   - SuperAGI 功能更全面
   - SuperAGI 有生產級的監控和管理

實際使用 SuperAGI:

1. 安裝:
   git clone https://github.com/TransformerOptimus/SuperAGI.git
   cd SuperAGI
   pip install -r requirements.txt

2. 配置:
   cp .env.example .env
   # 編輯 .env 設置 API key

3. 啟動:
   python run.py

4. 訪問:
   打開瀏覽器訪問 http://localhost:8000

5. 創建 Agent:
   - 使用 Web 界面創建
   - 或使用 API 創建
   - 或使用 Python SDK 創建

常見問題:

Q: SuperAGI 需要什麼配置？
A: 至少需要 OpenAI API Key，推薦配置向量數據庫

Q: 如何限制 Agent 的行為？
A: 通過資源限制、工具選擇和安全策略

Q: 支持哪些 LLM？
A: OpenAI GPT-4/3.5, Anthropic Claude, 本地模型等

Q: 如何部署到生產環境？
A: 參考 10_生產部署.py 的詳細說明
"""
