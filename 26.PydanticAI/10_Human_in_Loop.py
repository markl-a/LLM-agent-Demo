"""
Pydantic AI - Human-in-the-Loop 範例

本範例展示：
1. 人工審批流程
2. 用戶輸入整合
3. 決策點設計
4. 超時處理
5. 多級審批

Human-in-the-Loop 讓 AI 在關鍵決策點請求人工干預
"""

import asyncio
from typing import Optional, Literal
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext


# ============================================================================
# 範例 1: 基本人工確認
# ============================================================================

class ApprovalDecision(str, Enum):
    """審批決定"""
    APPROVED = "approved"
    REJECTED = "rejected"
    NEED_REVISION = "need_revision"


async def request_human_approval(
    prompt: str,
    timeout: float = 30.0
) -> ApprovalDecision:
    """
    請求人工審批（模擬）

    實際應用中，這裡會：
    - 發送通知給人工審批者
    - 等待審批決定
    - 處理超時情況
    """
    print(f"\n{'='*60}")
    print(f"🙋 請求人工審批")
    print(f"{'='*60}")
    print(f"{prompt}")
    print(f"{'='*60}")

    # 模擬人工輸入
    print("\n選項：")
    print("  1. 批准 (approved)")
    print("  2. 拒絕 (rejected)")
    print("  3. 需要修改 (need_revision)")

    # 自動批准（實際應用中會等待真實輸入）
    await asyncio.sleep(0.5)
    decision = ApprovalDecision.APPROVED

    print(f"\n決定：{decision.value}")
    return decision


async def example_1_basic_approval():
    """基本的人工審批流程"""
    print("\n" + "="*60)
    print("範例 1: 基本人工審批")
    print("="*60)

    agent = Agent('openai:gpt-4')

    # Agent 生成內容
    print("AI 生成內容...")
    result = await agent.run('寫一封感謝客戶的郵件')

    print(f"\nAI 生成的內容：")
    print(f"{result.data}\n")

    # 請求人工審批
    decision = await request_human_approval(
        f"請審批以下內容：\n{result.data[:200]}..."
    )

    if decision == ApprovalDecision.APPROVED:
        print("\n✓ 內容已批准，可以發送")
    elif decision == ApprovalDecision.REJECTED:
        print("\n✗ 內容被拒絕")
    else:
        print("\n⚠️  內容需要修改")


# ============================================================================
# 範例 2: 多步驟審批工作流
# ============================================================================

@dataclass
class ApprovalWorkflow:
    """審批工作流"""

    def __init__(self, agent: Agent):
        self.agent = agent
        self.approval_history = []

    async def generate_content(self, prompt: str) -> str:
        """生成內容"""
        print("\n→ 步驟 1: AI 生成內容")
        result = await self.agent.run(prompt)
        return result.data

    async def request_approval(
        self,
        content: str,
        approver: str
    ) -> ApprovalDecision:
        """請求審批"""
        print(f"\n→ 步驟 2: 請求 {approver} 審批")

        decision = await request_human_approval(
            f"{approver} 審批：\n{content[:150]}..."
        )

        self.approval_history.append({
            "approver": approver,
            "decision": decision,
            "timestamp": datetime.now().isoformat()
        })

        return decision

    async def revise_content(
        self,
        original: str,
        feedback: str
    ) -> str:
        """修改內容"""
        print("\n→ 步驟 3: AI 修改內容")

        result = await self.agent.run(
            f"請根據以下反饋修改內容：\n\n原內容：{original}\n\n反饋：{feedback}"
        )

        return result.data

    async def execute(
        self,
        prompt: str,
        max_revisions: int = 3
    ) -> dict:
        """執行完整的審批工作流"""
        content = await self.generate_content(prompt)

        for revision in range(max_revisions):
            # 請求審批
            decision = await self.request_approval(
                content,
                approver="管理員"
            )

            if decision == ApprovalDecision.APPROVED:
                print("\n✓ 內容獲得批准")
                break

            elif decision == ApprovalDecision.REJECTED:
                print("\n✗ 內容被拒絕")
                return {
                    "status": "rejected",
                    "content": content,
                    "approvals": self.approval_history
                }

            else:  # NEED_REVISION
                print(f"\n⚠️  需要修改（第 {revision + 1} 次）")
                content = await self.revise_content(
                    content,
                    "請使內容更專業和正式"
                )

        return {
            "status": "approved" if decision == ApprovalDecision.APPROVED else "max_revisions",
            "content": content,
            "approvals": self.approval_history,
            "revisions": len(self.approval_history) - 1
        }


async def example_2_approval_workflow():
    """多步驟審批工作流"""
    print("\n" + "="*60)
    print("範例 2: 多步驟審批工作流")
    print("="*60)

    agent = Agent('openai:gpt-4')
    workflow = ApprovalWorkflow(agent)

    result = await workflow.execute(
        "寫一份產品發布公告",
        max_revisions=2
    )

    print(f"\n工作流結果：")
    print(f"  狀態：{result['status']}")
    print(f"  審批次數：{len(result['approvals'])}")


# ============================================================================
# 範例 3: 交互式對話
# ============================================================================

class InteractiveAgent:
    """交互式 Agent"""

    def __init__(self, agent: Agent):
        self.agent = agent
        self.conversation_history = []

    async def ask_user(self, question: str) -> str:
        """詢問用戶"""
        print(f"\n🤖 Agent: {question}")
        print("👤 您: ", end='', flush=True)

        # 模擬用戶輸入
        await asyncio.sleep(0.3)
        user_input = "藍色"  # 實際應用中從標準輸入讀取

        print(user_input)
        return user_input

    async def interactive_run(self, initial_prompt: str) -> str:
        """交互式運行"""
        current_prompt = initial_prompt

        # 最多 3 輪交互
        for round_num in range(3):
            # Agent 處理
            result = await self.agent.run(current_prompt)

            print(f"\n🤖 Agent: {result.data}")

            # 檢查是否需要用戶輸入
            if "你喜歡什麼顏色" in result.data or round_num == 0:
                user_response = await self.ask_user("請告訴我您的偏好")

                # 將用戶輸入加入下一輪
                current_prompt = f"用戶回答：{user_response}。請根據這個回答繼續對話。"
            else:
                # 對話完成
                break

        return result.data


async def example_3_interactive_conversation():
    """交互式對話"""
    print("\n" + "="*60)
    print("範例 3: 交互式對話")
    print("="*60)

    agent = Agent('openai:gpt-4')
    interactive = InteractiveAgent(agent)

    await interactive.interactive_run(
        "問用戶喜歡什麼顏色，然後推薦相應的產品"
    )


# ============================================================================
# 範例 4: 敏感操作確認
# ============================================================================

class SensitiveOperation(str, Enum):
    """敏感操作類型"""
    DELETE_DATA = "delete_data"
    SEND_EMAIL = "send_email"
    MAKE_PAYMENT = "make_payment"
    GRANT_ACCESS = "grant_access"


@dataclass
class OperationRequest:
    """操作請求"""
    operation: SensitiveOperation
    description: str
    parameters: dict
    requires_confirmation: bool = True


async def confirm_sensitive_operation(
    request: OperationRequest
) -> bool:
    """確認敏感操作"""
    print(f"\n⚠️  敏感操作確認")
    print(f"{'='*60}")
    print(f"操作類型：{request.operation.value}")
    print(f"描述：{request.description}")
    print(f"參數：{request.parameters}")
    print(f"{'='*60}")

    # 模擬確認
    await asyncio.sleep(0.5)
    confirmed = True  # 實際應用中等待真實確認

    print(f"確認：{'是' if confirmed else '否'}")
    return confirmed


async def execute_with_confirmation(
    request: OperationRequest
) -> dict:
    """執行需要確認的操作"""
    if request.requires_confirmation:
        confirmed = await confirm_sensitive_operation(request)

        if not confirmed:
            return {
                "status": "cancelled",
                "message": "操作已取消"
            }

    # 執行操作
    print(f"\n✓ 執行操作：{request.operation.value}")

    return {
        "status": "success",
        "operation": request.operation.value,
        "executed_at": datetime.now().isoformat()
    }


async def example_4_sensitive_operations():
    """敏感操作確認"""
    print("\n" + "="*60)
    print("範例 4: 敏感操作確認")
    print("="*60)

    # 創建刪除請求
    delete_request = OperationRequest(
        operation=SensitiveOperation.DELETE_DATA,
        description="刪除舊的日誌文件",
        parameters={"file_pattern": "*.log", "older_than": "30 days"}
    )

    result = await execute_with_confirmation(delete_request)

    print(f"\n結果：{result['status']}")


# ============================================================================
# 範例 5: 分級審批系統
# ============================================================================

class ApprovalLevel(str, Enum):
    """審批級別"""
    TEAM_LEAD = "team_lead"
    MANAGER = "manager"
    DIRECTOR = "director"


@dataclass
class HierarchicalApproval:
    """分級審批系統"""

    def __init__(self, amount: float):
        self.amount = amount
        self.approvals = []

    def required_levels(self) -> list[ApprovalLevel]:
        """根據金額確定需要的審批級別"""
        levels = []

        if self.amount > 1000:
            levels.append(ApprovalLevel.TEAM_LEAD)

        if self.amount > 10000:
            levels.append(ApprovalLevel.MANAGER)

        if self.amount > 100000:
            levels.append(ApprovalLevel.DIRECTOR)

        return levels

    async def request_level_approval(
        self,
        level: ApprovalLevel
    ) -> bool:
        """請求特定級別的審批"""
        print(f"\n→ 請求 {level.value} 審批（金額：${self.amount:,.0f}）")

        # 模擬審批
        await asyncio.sleep(0.3)
        approved = True  # 實際應用中由真實審批者決定

        self.approvals.append({
            "level": level,
            "approved": approved,
            "timestamp": datetime.now().isoformat()
        })

        print(f"  {level.value}: {'✓ 批准' if approved else '✗ 拒絕'}")

        return approved

    async def execute(self) -> dict:
        """執行分級審批"""
        levels = self.required_levels()

        if not levels:
            print("✓ 金額較小，無需審批")
            return {"status": "auto_approved", "amount": self.amount}

        print(f"需要 {len(levels)} 級審批")

        # 依次請求各級審批
        for level in levels:
            approved = await self.request_level_approval(level)

            if not approved:
                return {
                    "status": "rejected",
                    "rejected_at": level.value,
                    "approvals": self.approvals
                }

        return {
            "status": "approved",
            "amount": self.amount,
            "approvals": self.approvals
        }


async def example_5_hierarchical_approval():
    """分級審批系統"""
    print("\n" + "="*60)
    print("範例 5: 分級審批系統")
    print("="*60)

    # 測試不同金額
    amounts = [500, 5000, 50000, 500000]

    for amount in amounts:
        print(f"\n測試金額：${amount:,.0f}")
        approval = HierarchicalApproval(amount)
        result = await approval.execute()
        print(f"結果：{result['status']}")


# ============================================================================
# 範例 6: 超時處理
# ============================================================================

async def request_approval_with_timeout(
    prompt: str,
    timeout_seconds: float = 5.0
) -> Optional[ApprovalDecision]:
    """帶超時的審批請求"""
    print(f"\n⏱️  請求審批（{timeout_seconds} 秒超時）")
    print(f"{prompt}")

    try:
        # 模擬等待審批
        await asyncio.wait_for(
            asyncio.sleep(1),  # 實際應用中等待真實輸入
            timeout=timeout_seconds
        )

        decision = ApprovalDecision.APPROVED
        print(f"✓ 在時限內收到決定：{decision.value}")
        return decision

    except asyncio.TimeoutError:
        print(f"⏱️  超時！使用默認決定")
        return None


async def example_6_timeout_handling():
    """超時處理"""
    print("\n" + "="*60)
    print("範例 6: 審批超時處理")
    print("="*60)

    decision = await request_approval_with_timeout(
        "請審批這個操作",
        timeout_seconds=3.0
    )

    if decision is None:
        print("\n使用默認策略：自動拒絕")
    else:
        print(f"\n收到決定：{decision.value}")


# ============================================================================
# 範例 7: 批量審批
# ============================================================================

@dataclass
class BatchApproval:
    """批量審批"""

    def __init__(self, items: list[str]):
        self.items = items
        self.approved_items = []
        self.rejected_items = []

    async def review_batch(self) -> dict:
        """審批批量項目"""
        print(f"\n📋 批量審批：{len(self.items)} 個項目")

        print("\n項目列表：")
        for i, item in enumerate(self.items, 1):
            print(f"  {i}. {item}")

        # 模擬批量審批決定
        await asyncio.sleep(0.5)

        # 簡單規則：包含 "urgent" 的批准
        for item in self.items:
            if "urgent" in item.lower():
                self.approved_items.append(item)
            else:
                self.rejected_items.append(item)

        print(f"\n結果：")
        print(f"  ✓ 批准：{len(self.approved_items)} 個")
        print(f"  ✗ 拒絕：{len(self.rejected_items)} 個")

        return {
            "approved": self.approved_items,
            "rejected": self.rejected_items,
            "approval_rate": len(self.approved_items) / len(self.items)
        }


async def example_7_batch_approval():
    """批量審批"""
    print("\n" + "="*60)
    print("範例 7: 批量審批")
    print("="*60)

    items = [
        "Urgent: Fix security bug",
        "Update documentation",
        "Urgent: Deploy hotfix",
        "Refactor code",
        "Urgent: Respond to customer"
    ]

    batch = BatchApproval(items)
    result = await batch.review_batch()

    print(f"\n批准率：{result['approval_rate']*100:.0f}%")


# ============================================================================
# 主程式
# ============================================================================

async def main():
    """運行所有範例"""
    print("\n" + "👥 " + "="*58)
    print("Pydantic AI - Human-in-the-Loop 範例")
    print("="*60)

    await example_1_basic_approval()
    await example_2_approval_workflow()
    await example_3_interactive_conversation()
    await example_4_sensitive_operations()
    await example_5_hierarchical_approval()
    await example_6_timeout_handling()
    await example_7_batch_approval()

    print("\n" + "="*60)
    print("✓ Human-in-the-Loop 範例完成！")
    print("💡 人機協作最佳實踐：")
    print("   1. 明確需要人工干預的場景")
    print("   2. 提供清晰的上下文信息")
    print("   3. 設置合理的超時機制")
    print("   4. 記錄所有審批決定")
    print("="*60)


if __name__ == '__main__':
    import os
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  請設置 OPENAI_API_KEY 環境變量")
    else:
        asyncio.run(main())
