"""
Atomic Agents 快速開始指南
=========================

本文件展示如何使用 Atomic Agents 創建第一個 Agent。
Atomic Agents 是一個輕量級、模組化的框架，強調清晰的輸入輸出模式。

主要內容：
1. 基礎 Agent 設置
2. 輸入輸出模式定義
3. 系統提示配置
4. Agent 運行示例
5. 錯誤處理基礎

作者：Atomic Agents 團隊
日期：2025-12-31
"""

import os
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from dataclasses import dataclass
from datetime import datetime

# 模擬 Atomic Agents 核心組件（實際使用時從 atomic_agents 導入）
try:
    from atomic_agents.agents.base_agent import BaseAgent
    from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
except ImportError:
    print("注意：atomic_agents 未安裝，使用模擬實現")


# ============================================================================
# 第一部分：定義輸入輸出模式
# ============================================================================

class UserQuery(BaseModel):
    """
    用戶查詢輸入模式

    這個類定義了 Agent 接收的輸入格式。
    使用 Pydantic 確保類型安全和自動驗證。
    """
    question: str = Field(
        ...,
        description="用戶的問題",
        min_length=1,
        max_length=1000
    )
    context: Optional[str] = Field(
        None,
        description="可選的上下文信息，幫助 Agent 更好地理解問題"
    )
    language: str = Field(
        default="zh-TW",
        description="回答的語言偏好"
    )
    max_tokens: int = Field(
        default=500,
        description="回答的最大長度（tokens）",
        ge=50,
        le=2000
    )

    @validator('question')
    def question_not_empty(cls, v):
        """驗證問題不為空"""
        if not v.strip():
            raise ValueError('問題不能為空')
        return v.strip()


class AgentResponse(BaseModel):
    """
    Agent 響應輸出模式

    定義 Agent 輸出的結構化格式。
    """
    answer: str = Field(
        ...,
        description="Agent 的回答"
    )
    confidence: float = Field(
        ...,
        description="回答的信心分數 (0-1)",
        ge=0.0,
        le=1.0
    )
    sources: Optional[List[str]] = Field(
        default=None,
        description="回答的來源或參考"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="響應生成時間"
    )
    model_used: str = Field(
        default="gpt-4",
        description="使用的模型名稱"
    )


# ============================================================================
# 第二部分：創建簡單的 Agent
# ============================================================================

@dataclass
class SystemPromptConfig:
    """系統提示配置"""
    background: List[str]
    steps: List[str]
    output_instructions: List[str]


class SimpleQAAgent:
    """
    簡單問答 Agent

    這是一個基礎的問答 Agent，展示 Atomic Agents 的核心概念。
    實際使用時應該繼承 BaseAgent。
    """

    def __init__(self, model: str = "gpt-4"):
        """
        初始化 Agent

        Args:
            model: 使用的 LLM 模型名稱
        """
        self.model = model
        self.system_prompt = self._create_system_prompt()

    def _create_system_prompt(self) -> str:
        """創建系統提示"""
        config = SystemPromptConfig(
            background=[
                "你是一個專業的 AI 助手，使用 Atomic Agents 框架。",
                "你的任務是回答用戶的問題並提供信心分數。",
                "你應該基於事實和知識提供準確、有用的回答。"
            ],
            steps=[
                "1. 仔細閱讀並理解用戶的問題",
                "2. 如果提供了上下文，將其納入考慮",
                "3. 基於你的知識庫提供準確的回答",
                "4. 評估你對答案的信心程度（0-1 分數）",
                "5. 如果可能，提供相關的來源或參考"
            ],
            output_instructions=[
                "提供清晰、簡潔但完整的回答",
                "信心分數應該真實反映你對答案的確定性",
                "如果不確定，坦率承認並提供最佳猜測",
                "使用用戶指定的語言回答"
            ]
        )

        # 組合系統提示
        prompt = "## 背景\n"
        prompt += "\n".join(config.background)
        prompt += "\n\n## 步驟\n"
        prompt += "\n".join(config.steps)
        prompt += "\n\n## 輸出要求\n"
        prompt += "\n".join(config.output_instructions)

        return prompt

    def run(self, user_input: UserQuery) -> AgentResponse:
        """
        運行 Agent

        Args:
            user_input: 用戶輸入

        Returns:
            Agent 響應
        """
        print(f"\n{'='*60}")
        print(f"處理問題: {user_input.question}")
        print(f"{'='*60}\n")

        # 在實際應用中，這裡會調用 LLM API
        # 這裡我們使用模擬響應
        answer = self._generate_answer(user_input)
        confidence = self._calculate_confidence(user_input)

        response = AgentResponse(
            answer=answer,
            confidence=confidence,
            sources=["Atomic Agents 文檔", "內部知識庫"],
            model_used=self.model
        )

        return response

    def _generate_answer(self, user_input: UserQuery) -> str:
        """生成回答（模擬）"""
        # 實際使用時，這裡會調用 LLM
        base_answer = f"關於「{user_input.question}」，這是一個很好的問題。"

        if "atomic agents" in user_input.question.lower():
            base_answer += (
                "Atomic Agents 是一個輕量級、模組化的 AI Agent 框架，"
                "專注於構建具有清晰輸入輸出模式的 AI 代理和管道。"
                "它的核心優勢包括模組化設計、Schema 驅動、高可測試性和輕量級特性。"
            )
        else:
            base_answer += "基於提供的信息，我會盡力為您提供準確的回答。"

        if user_input.context:
            base_answer += f"\n\n考慮到上下文：{user_input.context}"

        return base_answer

    def _calculate_confidence(self, user_input: UserQuery) -> float:
        """計算信心分數（模擬）"""
        # 簡單的啟發式計算
        confidence = 0.7  # 基礎信心

        # 如果有上下文，信心提高
        if user_input.context:
            confidence += 0.15

        # 如果問題包含已知關鍵詞，信心提高
        if "atomic agents" in user_input.question.lower():
            confidence += 0.1

        return min(confidence, 1.0)


# ============================================================================
# 第三部分：高級 Agent 示例
# ============================================================================

class ResearchQuery(BaseModel):
    """研究查詢輸入"""
    topic: str = Field(..., description="研究主題")
    depth: str = Field(
        default="medium",
        description="研究深度：shallow, medium, deep"
    )
    focus_areas: Optional[List[str]] = Field(
        default=None,
        description="重點關注的領域"
    )


class ResearchReport(BaseModel):
    """研究報告輸出"""
    summary: str = Field(..., description="研究摘要")
    key_findings: List[str] = Field(..., description="關鍵發現")
    recommendations: List[str] = Field(..., description="建議")
    confidence: float = Field(..., description="整體信心分數")
    research_depth: str = Field(..., description="實際研究深度")


class ResearchAgent:
    """
    研究 Agent

    展示更複雜的 Agent 使用場景。
    """

    def __init__(self):
        self.model = "gpt-4"

    def run(self, query: ResearchQuery) -> ResearchReport:
        """執行研究任務"""
        print(f"\n開始研究主題: {query.topic}")
        print(f"研究深度: {query.depth}")

        # 模擬研究過程
        findings = self._conduct_research(query)
        recommendations = self._generate_recommendations(findings)

        report = ResearchReport(
            summary=f"關於「{query.topic}」的研究報告",
            key_findings=findings,
            recommendations=recommendations,
            confidence=0.85,
            research_depth=query.depth
        )

        return report

    def _conduct_research(self, query: ResearchQuery) -> List[str]:
        """進行研究（模擬）"""
        findings = [
            f"{query.topic} 是一個重要且活躍的研究領域",
            "近年來有顯著的技術進展",
            "存在多種實現方法和最佳實踐"
        ]

        if query.focus_areas:
            findings.append(f"在 {', '.join(query.focus_areas)} 方面有特別的應用")

        return findings

    def _generate_recommendations(self, findings: List[str]) -> List[str]:
        """生成建議"""
        return [
            "建議進行更深入的技術調研",
            "可以考慮實施試點項目",
            "建議與相關專家交流"
        ]


# ============================================================================
# 第四部分：實用工具函數
# ============================================================================

def setup_environment():
    """設置環境"""
    # 設置 API 密鑰（實際使用時從環境變量讀取）
    os.environ.setdefault('OPENAI_API_KEY', 'your-api-key-here')
    os.environ.setdefault('ANTHROPIC_API_KEY', 'your-api-key-here')
    print("環境設置完成")


def validate_response(response: AgentResponse) -> bool:
    """
    驗證響應的有效性

    Args:
        response: Agent 響應

    Returns:
        是否有效
    """
    if not response.answer or len(response.answer.strip()) == 0:
        print("錯誤：回答為空")
        return False

    if response.confidence < 0 or response.confidence > 1:
        print("錯誤：信心分數超出範圍")
        return False

    print("響應驗證通過")
    return True


def print_response(response: AgentResponse):
    """美化輸出響應"""
    print("\n" + "="*60)
    print("Agent 響應")
    print("="*60)
    print(f"\n回答：\n{response.answer}\n")
    print(f"信心分數: {response.confidence:.2f}")
    print(f"模型: {response.model_used}")
    print(f"時間: {response.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    if response.sources:
        print(f"來源: {', '.join(response.sources)}")
    print("="*60 + "\n")


# ============================================================================
# 第五部分：使用示例
# ============================================================================

def example_basic_qa():
    """基礎問答示例"""
    print("\n" + "="*60)
    print("示例 1: 基礎問答")
    print("="*60)

    # 創建 Agent
    agent = SimpleQAAgent(model="gpt-4")

    # 創建查詢
    query = UserQuery(
        question="什麼是 Atomic Agents？",
        context="我想了解這個框架的核心特性",
        language="zh-TW"
    )

    # 運行 Agent
    response = agent.run(query)

    # 驗證並輸出
    if validate_response(response):
        print_response(response)


def example_with_context():
    """帶上下文的示例"""
    print("\n" + "="*60)
    print("示例 2: 帶上下文的查詢")
    print("="*60)

    agent = SimpleQAAgent()

    query = UserQuery(
        question="如何開始使用？",
        context="我是一個 Python 開發者，熟悉 FastAPI 和 Pydantic",
        language="zh-TW",
        max_tokens=300
    )

    response = agent.run(query)
    print_response(response)


def example_research_agent():
    """研究 Agent 示例"""
    print("\n" + "="*60)
    print("示例 3: 研究 Agent")
    print("="*60)

    agent = ResearchAgent()

    query = ResearchQuery(
        topic="AI Agent 框架比較",
        depth="deep",
        focus_areas=["性能", "易用性", "可擴展性"]
    )

    report = agent.run(query)

    print("\n研究報告:")
    print(f"摘要: {report.summary}")
    print(f"\n關鍵發現:")
    for i, finding in enumerate(report.key_findings, 1):
        print(f"  {i}. {finding}")
    print(f"\n建議:")
    for i, rec in enumerate(report.recommendations, 1):
        print(f"  {i}. {rec}")
    print(f"\n信心分數: {report.confidence:.2f}")


def example_error_handling():
    """錯誤處理示例"""
    print("\n" + "="*60)
    print("示例 4: 錯誤處理")
    print("="*60)

    agent = SimpleQAAgent()

    # 測試無效輸入
    try:
        query = UserQuery(
            question="",  # 空問題
            language="zh-TW"
        )
    except Exception as e:
        print(f"捕獲到驗證錯誤: {e}")

    # 測試超長問題
    try:
        query = UserQuery(
            question="問題" * 1000,  # 超過最大長度
            language="zh-TW"
        )
    except Exception as e:
        print(f"捕獲到驗證錯誤: {e}")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主函數"""
    print("\n" + "="*60)
    print("Atomic Agents 快速開始指南")
    print("="*60)

    # 設置環境
    setup_environment()

    # 運行示例
    example_basic_qa()
    example_with_context()
    example_research_agent()
    example_error_handling()

    print("\n" + "="*60)
    print("所有示例運行完成！")
    print("="*60)
    print("\n下一步:")
    print("1. 查看 02_輸入輸出模式.py 學習更多 Schema 設計")
    print("2. 探索 03_原子工具.py 了解如何創建工具")
    print("3. 閱讀 04_鏈式管道.py 構建複雜工作流")


if __name__ == "__main__":
    main()
