"""
Microsoft Agent Framework - 人機協作

這個檔案展示如何實現人機協作 (Human-in-the-Loop)。
在某些情況下,Agent 需要人工介入來做出決策或提供指導。

主要內容:
1. Human-in-the-Loop 概念
2. 審批工作流
3. 人工介入點設計
4. 決策升級機制
5. 反饋收集
6. 主動學習
7. 安全性和合規
8. 實際應用案例

作者: Microsoft Agent Framework Team
日期: 2025-12-31
版本: 1.0.0
"""

import os
import time
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from queue import Queue
from dotenv import load_dotenv

# Agent Framework
from agent_framework import Agent, AgentThread
from agent_framework.models import OpenAIModel

# ============================================================================
# 1. Human-in-the-Loop 概念
# ============================================================================

def explain_human_in_the_loop():
    """
    解釋 Human-in-the-Loop 的概念和應用

    HITL 是一種設計模式,將人類專家整合到 AI 系統的決策流程中
    """
    print("="*70)
    print("Human-in-the-Loop (HITL) 介紹")
    print("="*70)

    print("\n📚 HITL 核心概念:")

    concepts = [
        ("1. 人工監督", "人類監督 AI 的決策過程,確保品質和安全性"),
        ("2. 決策審批", "重要決策需要人工審批才能執行"),
        ("3. 主動學習", "從人類反饋中學習,改進 AI 性能"),
        ("4. 異常處理", "遇到不確定情況時,升級給人類處理"),
        ("5. 合規保證", "確保符合法規和倫理要求"),
    ]

    for title, description in concepts:
        print(f"\n   {title}")
        print(f"      {description}")

    print("\n🎯 HITL 的應用場景:")

    scenarios = [
        "金融交易審批 (高價值交易需要人工確認)",
        "醫療診斷建議 (AI 輔助,醫生最終決策)",
        "內容審核 (敏感內容需要人工審查)",
        "客戶服務升級 (複雜問題轉人工處理)",
        "合約審核 (法律文件需要專家審查)",
    ]

    for scenario in scenarios:
        print(f"   - {scenario}")


# ============================================================================
# 2. 介入點類型
# ============================================================================

class InterventionType(str, Enum):
    """人工介入類型"""
    APPROVAL = "approval"              # 審批
    FEEDBACK = "feedback"              # 反饋
    CORRECTION = "correction"          # 修正
    ESCALATION = "escalation"          # 升級
    GUIDANCE = "guidance"              # 指導


class InterventionStatus(str, Enum):
    """介入狀態"""
    PENDING = "pending"                # 等待中
    APPROVED = "approved"              # 已批准
    REJECTED = "rejected"              # 已拒絕
    COMPLETED = "completed"            # 已完成
    TIMEOUT = "timeout"                # 超時


# ============================================================================
# 3. 介入請求資料結構
# ============================================================================

@dataclass
class InterventionRequest:
    """
    人工介入請求

    封裝需要人工處理的請求資訊
    """
    request_id: str
    intervention_type: InterventionType
    agent_name: str
    thread_id: str
    context: Dict[str, Any]
    question: str
    options: List[Dict[str, Any]]
    timeout_seconds: Optional[int] = None
    created_at: datetime = None
    status: InterventionStatus = InterventionStatus.PENDING
    response: Optional[Dict[str, Any]] = None
    responded_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "request_id": self.request_id,
            "intervention_type": self.intervention_type.value,
            "agent_name": self.agent_name,
            "thread_id": self.thread_id,
            "context": self.context,
            "question": self.question,
            "options": self.options,
            "timeout_seconds": self.timeout_seconds,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "response": self.response,
            "responded_at": self.responded_at.isoformat() if self.responded_at else None,
        }


# ============================================================================
# 4. 人工介入管理器
# ============================================================================

class HumanInterventionManager:
    """
    人工介入管理器

    管理所有的人工介入請求
    """

    def __init__(self):
        """初始化管理器"""
        self.pending_requests: Dict[str, InterventionRequest] = {}
        self.completed_requests: List[InterventionRequest] = []
        self.request_counter = 0

    def create_request(
        self,
        intervention_type: InterventionType,
        agent_name: str,
        thread_id: str,
        context: Dict[str, Any],
        question: str,
        options: List[Dict[str, Any]],
        timeout_seconds: Optional[int] = None
    ) -> InterventionRequest:
        """
        創建人工介入請求

        Args:
            intervention_type: 介入類型
            agent_name: Agent 名稱
            thread_id: Thread ID
            context: 上下文資訊
            question: 需要回答的問題
            options: 可選的選項
            timeout_seconds: 超時時間

        Returns:
            介入請求
        """
        self.request_counter += 1
        request_id = f"req_{self.request_counter:06d}"

        request = InterventionRequest(
            request_id=request_id,
            intervention_type=intervention_type,
            agent_name=agent_name,
            thread_id=thread_id,
            context=context,
            question=question,
            options=options,
            timeout_seconds=timeout_seconds,
        )

        self.pending_requests[request_id] = request

        print(f"\n🙋 創建人工介入請求: {request_id}")
        print(f"   類型: {intervention_type.value}")
        print(f"   問題: {question}")

        return request

    def respond_to_request(
        self,
        request_id: str,
        response: Dict[str, Any]
    ):
        """
        回應介入請求

        Args:
            request_id: 請求 ID
            response: 人工回應
        """
        if request_id not in self.pending_requests:
            raise ValueError(f"請求不存在: {request_id}")

        request = self.pending_requests[request_id]
        request.response = response
        request.responded_at = datetime.now()
        request.status = InterventionStatus.COMPLETED

        # 移到已完成列表
        self.completed_requests.append(request)
        del self.pending_requests[request_id]

        print(f"\n✅ 人工回應已提交: {request_id}")

    def get_pending_requests(
        self,
        agent_name: Optional[str] = None
    ) -> List[InterventionRequest]:
        """
        獲取待處理的請求

        Args:
            agent_name: 篩選 Agent 名稱

        Returns:
            待處理請求列表
        """
        requests = list(self.pending_requests.values())

        if agent_name:
            requests = [r for r in requests if r.agent_name == agent_name]

        return requests

    def check_timeout(self):
        """檢查並處理超時請求"""
        now = datetime.now()

        for request_id, request in list(self.pending_requests.items()):
            if request.timeout_seconds:
                elapsed = (now - request.created_at).total_seconds()
                if elapsed > request.timeout_seconds:
                    request.status = InterventionStatus.TIMEOUT
                    self.completed_requests.append(request)
                    del self.pending_requests[request_id]

                    print(f"\n⏰ 請求超時: {request_id}")


# ============================================================================
# 5. 支援 HITL 的 Agent
# ============================================================================

class HITLAgent:
    """
    支援 Human-in-the-Loop 的 Agent

    在需要時請求人工介入
    """

    def __init__(
        self,
        agent: Agent,
        intervention_manager: HumanInterventionManager,
        confidence_threshold: float = 0.7
    ):
        """
        初始化 HITL Agent

        Args:
            agent: 基礎 Agent
            intervention_manager: 介入管理器
            confidence_threshold: 信心閾值,低於此值會請求人工介入
        """
        self.agent = agent
        self.intervention_manager = intervention_manager
        self.confidence_threshold = confidence_threshold

    def run_with_human_oversight(
        self,
        thread: AgentThread,
        message: str,
        require_approval: bool = False
    ) -> Dict[str, Any]:
        """
        執行帶人工監督的任務

        Args:
            thread: 對話線程
            message: 用戶訊息
            require_approval: 是否需要審批

        Returns:
            執行結果
        """
        print(f"\n🤖 Agent 處理中: {message[:50]}...")

        # Agent 生成回應
        # 在實際實作中,這裡會調用 agent.run()
        agent_response = {
            "content": "這是 Agent 的建議回應...",
            "confidence": 0.6,  # 模擬信心分數
        }

        # 檢查是否需要人工介入
        needs_intervention = (
            require_approval or
            agent_response["confidence"] < self.confidence_threshold
        )

        if needs_intervention:
            print(f"\n⚠️  信心分數過低 ({agent_response['confidence']:.2f}),請求人工審核")

            # 創建介入請求
            request = self.intervention_manager.create_request(
                intervention_type=InterventionType.APPROVAL,
                agent_name=self.agent.name,
                thread_id=thread.id,
                context={
                    "user_message": message,
                    "agent_response": agent_response["content"],
                    "confidence": agent_response["confidence"],
                },
                question="請審核 Agent 的回應是否適當",
                options=[
                    {"value": "approve", "label": "批准"},
                    {"value": "reject", "label": "拒絕"},
                    {"value": "modify", "label": "修改"},
                ],
                timeout_seconds=300
            )

            # 等待人工回應 (模擬)
            print("\n⏳ 等待人工審核...")

            # 在實際應用中,這裡會等待真實的人工回應
            # 這裡模擬人工批准
            self.intervention_manager.respond_to_request(
                request.request_id,
                {
                    "decision": "approve",
                    "comment": "回應適當,批准發送"
                }
            )

            return {
                "response": agent_response["content"],
                "approved": True,
                "approver": "human_supervisor"
            }

        else:
            print(f"\n✅ 信心分數足夠 ({agent_response['confidence']:.2f}),直接回應")
            return {
                "response": agent_response["content"],
                "approved": True,
                "approver": "auto"
            }


# ============================================================================
# 6. 審批工作流
# ============================================================================

class ApprovalWorkflow:
    """
    審批工作流

    實現多級審批流程
    """

    def __init__(self, intervention_manager: HumanInterventionManager):
        """初始化工作流"""
        self.intervention_manager = intervention_manager

    def request_approval(
        self,
        title: str,
        description: str,
        data: Dict[str, Any],
        approver_level: int = 1
    ) -> bool:
        """
        請求審批

        Args:
            title: 審批標題
            description: 描述
            data: 相關資料
            approver_level: 審批級別 (1: 一般, 2: 高級, 3: 最高)

        Returns:
            是否批准
        """
        print(f"\n📋 提交審批請求: {title}")
        print(f"   級別: {approver_level}")

        request = self.intervention_manager.create_request(
            intervention_type=InterventionType.APPROVAL,
            agent_name="approval_workflow",
            thread_id="workflow",
            context=data,
            question=f"{description}\n\n是否批准?",
            options=[
                {"value": "approve", "label": "批准"},
                {"value": "reject", "label": "拒絕"},
                {"value": "request_more_info", "label": "需要更多資訊"},
            ],
            timeout_seconds=600
        )

        # 模擬審批過程
        print("   ⏳ 等待審批...")

        # 模擬批准
        self.intervention_manager.respond_to_request(
            request.request_id,
            {
                "decision": "approve",
                "comment": "審批通過",
                "approver_id": f"approver_level_{approver_level}"
            }
        )

        return True


# ============================================================================
# 7. 實際應用案例
# ============================================================================

def demonstrate_customer_service_escalation():
    """
    示範客服場景的人工升級

    當 Agent 無法處理時,升級給人工客服
    """
    print("\n" + "="*70)
    print("🎯 案例 1: 客服升級場景")
    print("="*70)

    load_dotenv()
    model = OpenAIModel(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # 創建客服 Agent
    agent = Agent(
        name="customer_service",
        model=model,
        instructions="你是客服 Agent,處理客戶問題",
    )

    intervention_manager = HumanInterventionManager()
    hitl_agent = HITLAgent(agent, intervention_manager, confidence_threshold=0.8)

    # 模擬客戶問題
    thread = AgentThread()
    customer_questions = [
        ("一般問題", "如何重設密碼?", False),
        ("複雜問題", "我的帳號被莫名扣款,要求立即退款!", True),
    ]

    for category, question, require_approval in customer_questions:
        print(f"\n--- {category} ---")
        print(f"👤 客戶: {question}")

        result = hitl_agent.run_with_human_oversight(
            thread=thread,
            message=question,
            require_approval=require_approval
        )

        print(f"\n🤖 最終回應: {result['response'][:80]}...")
        print(f"   審批者: {result['approver']}")


def demonstrate_financial_approval():
    """
    示範金融交易審批

    高價值交易需要多級審批
    """
    print("\n" + "="*70)
    print("🎯 案例 2: 金融交易審批")
    print("="*70)

    intervention_manager = HumanInterventionManager()
    workflow = ApprovalWorkflow(intervention_manager)

    # 模擬不同金額的交易
    transactions = [
        {"amount": 1000, "level": 1, "desc": "小額交易"},
        {"amount": 50000, "level": 2, "desc": "中額交易"},
        {"amount": 500000, "level": 3, "desc": "大額交易"},
    ]

    for tx in transactions:
        print(f"\n--- {tx['desc']} ---")

        approved = workflow.request_approval(
            title=f"交易審批 - ${tx['amount']:,}",
            description=f"請審批金額為 ${tx['amount']:,} 的交易",
            data={
                "amount": tx["amount"],
                "currency": "USD",
                "type": "wire_transfer"
            },
            approver_level=tx["level"]
        )

        if approved:
            print(f"   ✅ 交易已批准,可以執行")
        else:
            print(f"   ❌ 交易被拒絕")


def demonstrate_content_moderation():
    """
    示範內容審核

    敏感內容需要人工審查
    """
    print("\n" + "="*70)
    print("🎯 案例 3: 內容審核")
    print("="*70)

    intervention_manager = HumanInterventionManager()

    # 模擬內容審核
    contents = [
        {
            "text": "這是一般的評論內容",
            "ai_flag": False,
            "reason": None
        },
        {
            "text": "這段內容可能包含敏感資訊...",
            "ai_flag": True,
            "reason": "包含敏感關鍵字"
        },
    ]

    for i, content in enumerate(contents, 1):
        print(f"\n--- 內容 {i} ---")
        print(f"內容: {content['text']}")

        if content["ai_flag"]:
            print(f"⚠️  AI 標記: {content['reason']}")

            # 請求人工審核
            request = intervention_manager.create_request(
                intervention_type=InterventionType.APPROVAL,
                agent_name="content_moderator",
                thread_id=f"content_{i}",
                context={"content": content["text"]},
                question="請審核此內容是否適當發布",
                options=[
                    {"value": "approve", "label": "通過"},
                    {"value": "reject", "label": "拒絕"},
                    {"value": "require_edit", "label": "需要修改"},
                ],
            )

            print("   ⏳ 提交人工審核...")

            # 模擬審核結果
            intervention_manager.respond_to_request(
                request.request_id,
                {
                    "decision": "approve",
                    "comment": "內容適當,允許發布"
                }
            )

            print("   ✅ 人工審核通過")
        else:
            print("   ✅ AI 自動通過")


def demonstrate_feedback_collection():
    """
    示範反饋收集

    收集人類反饋用於改進 AI
    """
    print("\n" + "="*70)
    print("🎯 案例 4: 反饋收集")
    print("="*70)

    intervention_manager = HumanInterventionManager()

    print("\n收集用戶對 AI 回應的反饋:")

    # 模擬 AI 回應
    ai_responses = [
        "這是 AI 的第一個回應...",
        "這是 AI 的第二個回應...",
    ]

    for i, response in enumerate(ai_responses, 1):
        print(f"\n回應 {i}: {response}")

        # 請求反饋
        request = intervention_manager.create_request(
            intervention_type=InterventionType.FEEDBACK,
            agent_name="feedback_collector",
            thread_id=f"feedback_{i}",
            context={"ai_response": response},
            question="請評價此回應的品質",
            options=[
                {"value": "excellent", "label": "優秀"},
                {"value": "good", "label": "良好"},
                {"value": "fair", "label": "普通"},
                {"value": "poor", "label": "差"},
            ],
        )

        # 模擬用戶反饋
        intervention_manager.respond_to_request(
            request.request_id,
            {
                "rating": "good",
                "comment": "回應準確但可以更詳細"
            }
        )

        print("   ✅ 反饋已收集")

    print(f"\n📊 總共收集了 {len(intervention_manager.completed_requests)} 條反饋")


# ============================================================================
# 8. 最佳實踐
# ============================================================================

def print_hitl_best_practices():
    """輸出 HITL 最佳實踐"""
    print("\n" + "="*70)
    print("💡 Human-in-the-Loop 最佳實踐")
    print("="*70)

    practices = [
        ("1. 明確介入點", [
            "清楚定義何時需要人工介入",
            "基於風險和信心分數自動判斷",
            "避免過度或過少的人工介入"
        ]),
        ("2. 用戶體驗", [
            "提供清晰的等待提示",
            "設定合理的超時時間",
            "支援非同步處理"
        ]),
        ("3. 審批流程", [
            "實施適當的權限控制",
            "記錄所有審批決策",
            "支援審批歷史追蹤"
        ]),
        ("4. 反饋循環", [
            "系統化收集人類反饋",
            "使用反饋改進 AI 模型",
            "追蹤改進效果"
        ]),
        ("5. 性能優化", [
            "減少不必要的人工介入",
            "提高 AI 信心分數",
            "優化審批流程效率"
        ]),
    ]

    for title, points in practices:
        print(f"\n   {title}")
        for point in points:
            print(f"      - {point}")


# ============================================================================
# 9. 主程式
# ============================================================================

def main():
    """主程式"""
    print("="*70)
    print("Microsoft Agent Framework - 人機協作")
    print("="*70)

    # HITL 概念介紹
    explain_human_in_the_loop()

    # 實際應用案例
    demonstrate_customer_service_escalation()
    demonstrate_financial_approval()
    demonstrate_content_moderation()
    demonstrate_feedback_collection()

    # 最佳實踐
    print_hitl_best_practices()

    print("\n" + "="*70)
    print("✅ 人機協作示範完成!")
    print("="*70)

    print("\n💡 關鍵要點:")
    print("   1. HITL 確保 AI 系統的可靠性和安全性")
    print("   2. 支援多種介入類型 (審批、反饋、升級)")
    print("   3. 適合高風險和合規要求的場景")
    print("   4. 收集人類反饋改進 AI 性能")
    print("   5. 平衡自動化和人工控制")

    print("\n📚 下一步:")
    print("   查看 10_生產部署.py 學習生產環境最佳實踐")


if __name__ == "__main__":
    main()
