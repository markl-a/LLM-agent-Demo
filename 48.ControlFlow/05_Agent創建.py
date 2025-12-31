"""
ControlFlow Agent 創建詳解
==========================

本文件深入探討 ControlFlow 中 Agent 的創建和配置,包括:
1. 基本 Agent 配置
2. Agent 角色和專長
3. Agent 指令優化
4. 多 Agent 協作
5. Agent 工具綁定
6. Agent 記憶和上下文
7. 高級 Agent 模式

作者: ControlFlow 示例團隊
日期: 2025
"""

import os
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
import controlflow as cf
from controlflow import Agent, Task, Flow
from pydantic import BaseModel, Field
from dotenv import load_dotenv


# ========== 配置 ==========

load_dotenv()


# ========== 數據模型 ==========

class AgentCapability(BaseModel):
    """Agent 能力模型"""
    name: str = Field(description="能力名稱")
    description: str = Field(description="能力描述")
    proficiency: float = Field(ge=0, le=1, description="熟練度")


class AgentProfile(BaseModel):
    """Agent 配置檔案"""
    name: str
    role: str
    expertise: List[str]
    capabilities: List[AgentCapability]
    model: str = "gpt-4"
    temperature: float = 0.7


# ========== 基本 Agent 配置 ==========

class BasicAgentSetup:
    """
    基本 Agent 配置示例

    演示如何創建和配置基本的 Agent
    """

    @staticmethod
    def create_simple_agent() -> Agent:
        """
        創建最簡單的 Agent

        Returns:
            Agent: 基本 Agent 實例
        """
        print("🤖 創建簡單 Agent...")

        agent = Agent(
            name="通用助手",
            model="gpt-4"
        )

        print(f"   名稱: {agent.name}")
        print(f"   模型: {agent.model}")
        print()

        return agent

    @staticmethod
    def create_configured_agent() -> Agent:
        """
        創建配置完整的 Agent

        Returns:
            Agent: 完整配置的 Agent 實例
        """
        print("🤖 創建配置完整的 Agent...")

        agent = Agent(
            name="專業顧問",
            description="一個專業的商業顧問 AI",
            instructions="""
            你是一位經驗豐富的商業顧問。
            你的職責是:
            1. 分析商業問題和機會
            2. 提供戰略建議
            3. 協助決策制定
            4. 評估風險和收益

            請始終保持專業、客觀,並提供可行的建議。
            """,
            model="gpt-4",
            temperature=0.7
        )

        print(f"   名稱: {agent.name}")
        print(f"   描述: {agent.description}")
        print(f"   模型: {agent.model}")
        print(f"   溫度: {agent.temperature}")
        print()

        return agent

    @staticmethod
    def create_specialized_agent(
        role: str,
        expertise: List[str],
        personality: str = "professional"
    ) -> Agent:
        """
        創建專業化的 Agent

        Args:
            role: Agent 角色
            expertise: 專長領域列表
            personality: 個性風格

        Returns:
            Agent: 專業化的 Agent
        """
        print(f"🤖 創建專業 Agent: {role}...")

        # 構建指令
        instructions = f"""
        你是一位{role},專長領域包括: {', '.join(expertise)}。

        你的個性風格是{personality}。
        """

        if personality == "friendly":
            instructions += "\n請用友好、親切的語氣與用戶交流。"
        elif personality == "professional":
            instructions += "\n請保持專業、正式的溝通風格。"
        elif personality == "concise":
            instructions += "\n請保持簡潔,直接給出要點。"

        agent = Agent(
            name=role,
            description=f"專注於 {', '.join(expertise)} 的專業助手",
            instructions=instructions,
            model="gpt-4"
        )

        print(f"   角色: {agent.name}")
        print(f"   專長: {', '.join(expertise)}")
        print(f"   風格: {personality}")
        print()

        return agent


# ========== Agent 角色設計 ==========

class AgentRoles:
    """
    常見 Agent 角色設計

    提供預定義的 Agent 角色模板
    """

    @staticmethod
    def create_researcher() -> Agent:
        """
        創建研究員 Agent

        Returns:
            Agent: 研究員 Agent
        """
        print("🔬 創建研究員 Agent...")

        agent = Agent(
            name="研究員",
            description="專業的研究分析專家",
            instructions="""
            你是一位專業的研究員,擅長:
            - 信息收集和整理
            - 文獻綜述
            - 數據分析
            - 趨勢研究
            - 報告撰寫

            研究方法:
            1. 明確研究問題
            2. 系統收集資料
            3. 批判性分析
            4. 綜合結論
            5. 提出建議

            請確保研究的全面性和準確性。
            """,
            model="gpt-4"
        )

        print(f"   ✅ 研究員 Agent 創建完成")
        print()

        return agent

    @staticmethod
    def create_writer() -> Agent:
        """
        創建寫作 Agent

        Returns:
            Agent: 寫作 Agent
        """
        print("✍️ 創建寫作 Agent...")

        agent = Agent(
            name="寫作專家",
            description="專業的內容創作者",
            instructions="""
            你是一位優秀的寫作專家,擅長:
            - 文章撰寫
            - 內容編輯
            - 文案創作
            - 風格調整
            - 語言潤飾

            寫作原則:
            1. 清晰表達
            2. 邏輯連貫
            3. 讀者導向
            4. 適當修辭
            5. 精煉語言

            請根據目標受眾調整寫作風格。
            """,
            model="gpt-4",
            temperature=0.8  # 較高溫度以增加創造性
        )

        print(f"   ✅ 寫作 Agent 創建完成")
        print()

        return agent

    @staticmethod
    def create_reviewer() -> Agent:
        """
        創建審查員 Agent

        Returns:
            Agent: 審查員 Agent
        """
        print("👁️ 創建審查員 Agent...")

        agent = Agent(
            name="審查員",
            description="嚴格的質量審查專家",
            instructions="""
            你是一位嚴謹的審查員,負責:
            - 內容審核
            - 質量檢查
            - 錯誤識別
            - 改進建議
            - 標準驗證

            審查標準:
            1. 準確性檢查
            2. 完整性評估
            3. 一致性驗證
            4. 規範性審核
            5. 質量評分

            請保持客觀、嚴格,提供建設性反饋。
            """,
            model="gpt-4",
            temperature=0.3  # 較低溫度以保持客觀
        )

        print(f"   ✅ 審查員 Agent 創建完成")
        print()

        return agent

    @staticmethod
    def create_analyst() -> Agent:
        """
        創建分析師 Agent

        Returns:
            Agent: 分析師 Agent
        """
        print("📊 創建分析師 Agent...")

        agent = Agent(
            name="數據分析師",
            description="專業的數據分析專家",
            instructions="""
            你是一位資深數據分析師,專長:
            - 數據解讀
            - 統計分析
            - 趨勢預測
            - 可視化建議
            - 洞察提取

            分析流程:
            1. 理解數據背景
            2. 探索性分析
            3. 深度挖掘
            4. 模式識別
            5. 結論和建議

            請用數據說話,提供可操作的洞察。
            """,
            model="gpt-4"
        )

        print(f"   ✅ 分析師 Agent 創建完成")
        print()

        return agent

    @staticmethod
    def create_coordinator() -> Agent:
        """
        創建協調員 Agent

        Returns:
            Agent: 協調員 Agent
        """
        print("🎯 創建協調員 Agent...")

        agent = Agent(
            name="項目協調員",
            description="高效的項目協調專家",
            instructions="""
            你是一位專業的項目協調員,負責:
            - 任務分配
            - 進度跟蹤
            - 資源協調
            - 溝通管理
            - 問題解決

            協調原則:
            1. 清晰溝通
            2. 合理分工
            3. 及時跟進
            4. 靈活調整
            5. 目標導向

            請確保團隊高效協作,按時交付成果。
            """,
            model="gpt-4"
        )

        print(f"   ✅ 協調員 Agent 創建完成")
        print()

        return agent


# ========== 多 Agent 協作 ==========

class MultiAgentCollaboration:
    """
    多 Agent 協作示例

    演示多個 Agent 如何協同工作
    """

    def __init__(self):
        """初始化協作團隊"""
        self.researcher = AgentRoles.create_researcher()
        self.writer = AgentRoles.create_writer()
        self.reviewer = AgentRoles.create_reviewer()

    @cf.flow
    def content_creation_pipeline(self, topic: str):
        """
        內容創作管道

        多個 Agent 協作完成內容創作

        Args:
            topic: 內容主題
        """
        print(f"🔄 啟動內容創作管道: {topic}")
        print()

        # 階段 1: 研究(研究員)
        print("📍 階段 1: 研究階段")
        research_task = Task(
            objective=f"研究主題: {topic}",
            instructions="收集相關資料,整理關鍵信息",
            agent=self.researcher,
            context={"topic": topic}
        )
        research_result = research_task.run()
        print(f"✅ 研究完成\n")

        # 階段 2: 撰寫(寫作專家)
        print("📍 階段 2: 撰寫階段")
        writing_task = Task(
            objective="撰寫文章",
            instructions="基於研究結果撰寫高質量文章",
            agent=self.writer,
            context={
                "topic": topic,
                "research": research_result
            }
        )
        draft = writing_task.run()
        print(f"✅ 撰寫完成\n")

        # 階段 3: 審查(審查員)
        print("📍 階段 3: 審查階段")
        review_task = Task(
            objective="審查文章質量",
            instructions="檢查文章質量,提供改進建議",
            agent=self.reviewer,
            context={
                "draft": draft,
                "research": research_result
            }
        )
        review_result = review_task.run()
        print(f"✅ 審查完成\n")

        # 階段 4: 修訂(寫作專家)
        print("📍 階段 4: 修訂階段")
        revision_task = Task(
            objective="根據反饋修訂文章",
            instructions="應用審查建議,完善文章",
            agent=self.writer,
            context={
                "draft": draft,
                "review": review_result
            }
        )
        final_article = revision_task.run()
        print(f"✅ 修訂完成\n")

        print("🎉 內容創作管道完成!")
        return final_article

    @cf.flow
    def problem_solving_team(self, problem: str):
        """
        問題解決團隊

        多個 Agent 從不同角度分析問題

        Args:
            problem: 要解決的問題
        """
        print(f"🔄 啟動問題解決團隊")
        print(f"   問題: {problem}\n")

        # 創建專業團隊
        analyst = AgentRoles.create_analyst()
        researcher = AgentRoles.create_researcher()
        coordinator = AgentRoles.create_coordinator()

        # 並行分析
        print("📍 並行分析階段")

        # 數據分析視角
        analysis_task = Task(
            objective="從數據角度分析問題",
            agent=analyst,
            context={"problem": problem}
        )

        # 研究視角
        research_task = Task(
            objective="研究類似問題的解決方案",
            agent=researcher,
            context={"problem": problem}
        )

        # 協調和整合
        print("📍 整合階段")
        coordination_task = Task(
            objective="整合分析和研究結果,提出解決方案",
            agent=coordinator,
            depends_on=[analysis_task, research_task],
            context={"problem": problem}
        )

        solution = coordination_task.run()

        print("✅ 問題解決完成!")
        return solution


# ========== Agent 工具綁定 ==========

class AgentWithTools:
    """
    Agent 工具綁定示例

    演示如何為 Agent 配置工具
    """

    @staticmethod
    @cf.tool
    def search_database(query: str) -> str:
        """
        搜索數據庫工具

        Args:
            query: 搜索查詢

        Returns:
            str: 搜索結果
        """
        print(f"   🔍 搜索數據庫: {query}")
        # 模擬數據庫搜索
        return f"數據庫搜索結果: {query}"

    @staticmethod
    @cf.tool
    def calculate(expression: str) -> float:
        """
        計算工具

        Args:
            expression: 數學表達式

        Returns:
            float: 計算結果
        """
        print(f"   🧮 計算: {expression}")
        try:
            # 安全的計算(實際應用中需要更嚴格的驗證)
            result = eval(expression)
            return float(result)
        except:
            return 0.0

    @staticmethod
    @cf.tool
    def fetch_data(source: str) -> Dict[str, Any]:
        """
        數據獲取工具

        Args:
            source: 數據源

        Returns:
            Dict[str, Any]: 獲取的數據
        """
        print(f"   📥 獲取數據: {source}")
        # 模擬數據獲取
        return {
            "source": source,
            "data": "示例數據",
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def create_agent_with_tools() -> Agent:
        """
        創建帶工具的 Agent

        Returns:
            Agent: 配置了工具的 Agent
        """
        print("🔧 創建帶工具的 Agent...")

        # 創建 Agent 並綁定工具
        agent = Agent(
            name="工具專家",
            description="能夠使用多種工具的 Agent",
            instructions="""
            你可以使用以下工具:
            - search_database: 搜索數據庫
            - calculate: 執行數學計算
            - fetch_data: 獲取外部數據

            根據任務需求選擇合適的工具。
            """,
            tools=[
                AgentWithTools.search_database,
                AgentWithTools.calculate,
                AgentWithTools.fetch_data
            ],
            model="gpt-4"
        )

        print(f"   ✅ Agent 創建完成,已綁定 3 個工具")
        print()

        return agent


# ========== Agent 記憶和上下文 ==========

class AgentMemory:
    """
    Agent 記憶和上下文管理

    演示如何管理 Agent 的記憶和上下文
    """

    def __init__(self):
        """初始化帶記憶的 Agent"""
        self.conversation_history = []

        self.agent = Agent(
            name="記憶助手",
            instructions="""
            你是一個能記住對話歷史的助手。
            請參考之前的對話內容,提供連貫的回應。
            """,
            model="gpt-4"
        )

    def chat(self, user_message: str) -> str:
        """
        與 Agent 對話

        Args:
            user_message: 用戶消息

        Returns:
            str: Agent 回應
        """
        print(f"👤 用戶: {user_message}")

        # 添加到歷史
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now()
        })

        # 創建任務,包含對話歷史
        task = Task(
            objective="回應用戶消息",
            instructions="根據對話歷史,給出恰當的回應",
            agent=self.agent,
            context={
                "message": user_message,
                "history": self.conversation_history[-5:]  # 最近5條
            }
        )

        response = task.run()

        # 添加 Agent 回應到歷史
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now()
        })

        print(f"🤖 Agent: {response}\n")

        return response

    def get_conversation_summary(self) -> str:
        """
        獲取對話摘要

        Returns:
            str: 對話摘要
        """
        print("📝 生成對話摘要...")

        task = Task(
            objective="總結對話內容",
            instructions="回顧對話歷史,生成簡潔的摘要",
            agent=self.agent,
            context={"history": self.conversation_history}
        )

        summary = task.run()
        print(f"摘要: {summary}\n")

        return summary


# ========== Agent 配置最佳實踐 ==========

class AgentBestPractices:
    """
    Agent 配置最佳實踐

    提供 Agent 設計和配置的最佳實踐
    """

    @staticmethod
    def create_task_specific_agent(task_description: str) -> Agent:
        """
        為特定任務創建優化的 Agent

        Args:
            task_description: 任務描述

        Returns:
            Agent: 優化的 Agent
        """
        print(f"🎯 為特定任務創建 Agent...")
        print(f"   任務: {task_description}\n")

        # 根據任務特徵選擇配置
        if "創意" in task_description or "設計" in task_description:
            temperature = 0.9
            model = "gpt-4"
            style = "創造性和開放性思維"

        elif "分析" in task_description or "計算" in task_description:
            temperature = 0.3
            model = "gpt-4"
            style = "邏輯性和精確性"

        elif "總結" in task_description or "摘要" in task_description:
            temperature = 0.5
            model = "gpt-4"
            style = "簡潔性和準確性"

        else:
            temperature = 0.7
            model = "gpt-4"
            style = "平衡性"

        agent = Agent(
            name="任務專家",
            description=f"針對 '{task_description}' 優化的 Agent",
            instructions=f"""
            你的任務是: {task_description}

            請以{style}的方式完成任務。
            確保輸出質量高、相關性強。
            """,
            model=model,
            temperature=temperature
        )

        print(f"   ✅ Agent 創建完成")
        print(f"   模型: {model}")
        print(f"   溫度: {temperature}")
        print(f"   風格: {style}\n")

        return agent

    @staticmethod
    def demonstrate_agent_comparison():
        """
        演示不同 Agent 配置的效果
        """
        print("📊 Agent 配置對比...\n")

        # 高溫度 Agent (創造性)
        creative_agent = Agent(
            name="創意大師",
            temperature=0.9,
            model="gpt-4"
        )

        # 低溫度 Agent (精確性)
        precise_agent = Agent(
            name="精確專家",
            temperature=0.2,
            model="gpt-4"
        )

        # 中等溫度 Agent (平衡)
        balanced_agent = Agent(
            name="平衡助手",
            temperature=0.5,
            model="gpt-4"
        )

        print("   ✅ 創建了 3 個不同配置的 Agent:")
        print(f"      - 創意大師 (溫度: 0.9) - 適合創意任務")
        print(f"      - 精確專家 (溫度: 0.2) - 適合分析任務")
        print(f"      - 平衡助手 (溫度: 0.5) - 適合通用任務")
        print()


# ========== 主程序 ==========

def main():
    """
    主程序入口

    演示各種 Agent 創建和配置方法
    """
    print("=" * 70)
    print("  ControlFlow Agent 創建示例")
    print("=" * 70)
    print()

    try:
        # 1. 基本 Agent 配置
        print("\n" + "=" * 70)
        print("1. 基本 Agent 配置")
        print("=" * 70 + "\n")

        basic = BasicAgentSetup()
        basic.create_simple_agent()
        basic.create_configured_agent()
        basic.create_specialized_agent(
            "數據科學家",
            ["機器學習", "統計分析", "數據可視化"],
            "professional"
        )

        # 2. Agent 角色
        print("\n" + "=" * 70)
        print("2. 常見 Agent 角色")
        print("=" * 70 + "\n")

        roles = AgentRoles()
        roles.create_researcher()
        roles.create_writer()
        roles.create_reviewer()
        roles.create_analyst()
        roles.create_coordinator()

        # 3. 多 Agent 協作
        print("\n" + "=" * 70)
        print("3. 多 Agent 協作")
        print("=" * 70 + "\n")

        # collaboration = MultiAgentCollaboration()
        # collaboration.content_creation_pipeline("人工智能的未來")
        print("✅ 多 Agent 協作示例已定義\n")

        # 4. Agent 工具
        print("\n" + "=" * 70)
        print("4. Agent 工具綁定")
        print("=" * 70 + "\n")

        tools = AgentWithTools()
        tools.create_agent_with_tools()

        # 5. Agent 記憶
        print("\n" + "=" * 70)
        print("5. Agent 記憶和上下文")
        print("=" * 70 + "\n")

        # memory_agent = AgentMemory()
        # memory_agent.chat("你好!")
        # memory_agent.chat("我對 AI 很感興趣")
        # memory_agent.get_conversation_summary()
        print("✅ Agent 記憶示例已定義\n")

        # 6. 最佳實踐
        print("\n" + "=" * 70)
        print("6. Agent 配置最佳實踐")
        print("=" * 70 + "\n")

        best_practices = AgentBestPractices()
        best_practices.create_task_specific_agent("創意文案撰寫")
        best_practices.demonstrate_agent_comparison()

        print("\n" + "=" * 70)
        print("演示完成")
        print("=" * 70)
        print("\n✅ 所有 Agent 創建示例已成功展示!")
        print("\n💡 Agent 設計要點:")
        print("   - 明確角色: 清晰定義 Agent 的職責")
        print("   - 優化指令: 提供詳細、結構化的指令")
        print("   - 溫度調節: 根據任務特性調整創造性")
        print("   - 工具配置: 為 Agent 提供必要的工具")
        print("   - 協作設計: 多 Agent 協作完成複雜任務")
        print("\n💡 下一步:")
        print("   - 查看 06_工具整合.py 學習工具開發")
        print("   - 查看 07_狀態管理.py 學習狀態管理")
        print()

    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
