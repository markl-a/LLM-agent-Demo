"""
Temporal 信號通信 - Signal 和 Query

這個示例展示了：
1. Signal - 向運行中的工作流發送信號
2. Query - 查詢工作流當前狀態
3. 人機交互流程（審批）
4. 動態更新工作流狀態
5. 工作流控制（暫停/繼續/取消）
6. 等待信號
7. 多信號處理
8. 信號與業務邏輯結合
"""

import asyncio
from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum
from typing import List, Optional

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker


# ============================================================
# 數據模型
# ============================================================

class ApprovalStatus(str, Enum):
    """審批狀態"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class OrderStatus(str, Enum):
    """訂單狀態"""
    CREATED = "created"
    PROCESSING = "processing"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class ApprovalRequest:
    """審批請求"""
    request_id: str
    title: str
    description: str
    amount: float
    requester: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    approver: Optional[str] = None
    approved_at: Optional[str] = None
    comment: Optional[str] = None


@dataclass
class OrderInfo:
    """訂單信息"""
    order_id: str
    items: List[str]
    total: float
    status: OrderStatus = OrderStatus.CREATED
    status_history: List[dict] = field(default_factory=list)


# ============================================================
# Activity 定義
# ============================================================

@activity.defn
async def send_approval_notification(request: ApprovalRequest, approver: str) -> bool:
    """發送審批通知"""
    print(f"📧 發送審批通知給 {approver}")
    print(f"   請求: {request.title}")
    print(f"   金額: ${request.amount}")
    await asyncio.sleep(0.5)
    return True


@activity.defn
async def process_approved_request(request: ApprovalRequest) -> dict:
    """處理已批准的請求"""
    print(f"✅ 處理已批准的請求: {request.request_id}")
    await asyncio.sleep(1)

    return {
        "request_id": request.request_id,
        "processed": True,
        "result": "資金已發放"
    }


@activity.defn
async def process_order(order_id: str) -> dict:
    """處理訂單"""
    print(f"📦 處理訂單: {order_id}")
    await asyncio.sleep(1.5)

    return {
        "order_id": order_id,
        "shipped": True,
        "tracking_number": f"TRACK-{order_id}"
    }


@activity.defn
async def send_notification(user: str, message: str) -> bool:
    """發送通知"""
    print(f"📬 通知 {user}: {message}")
    await asyncio.sleep(0.3)
    return True


# ============================================================
# 工作流 1: 審批工作流（Signal 示例）
# ============================================================

@workflow.defn
class ApprovalWorkflow:
    """
    審批工作流

    演示如何使用 Signal 實現人機交互
    工作流會等待外部審批決策
    """

    def __init__(self):
        self.request: Optional[ApprovalRequest] = None
        self.approval_received = False
        self.approval_decision: Optional[str] = None
        self.approval_comment: Optional[str] = None

    @workflow.run
    async def run(self, request: ApprovalRequest, approver: str, timeout_minutes: int = 60) -> dict:
        """
        執行審批流程

        Args:
            request: 審批請求
            approver: 審批人
            timeout_minutes: 超時時間（分鐘）
        """
        self.request = request

        print(f"\n📝 審批工作流開始")
        print(f"   請求 ID: {request.request_id}")
        print(f"   審批人: {approver}")

        # 發送審批通知
        await workflow.execute_activity(
            send_approval_notification,
            request,
            approver,
            start_to_close_timeout=timedelta(seconds=30),
        )

        print(f"   等待審批決策（超時: {timeout_minutes} 分鐘）...")

        # 等待審批信號（帶超時）
        try:
            await workflow.wait_condition(
                lambda: self.approval_received,
                timeout=timedelta(minutes=timeout_minutes)
            )

            print(f"   ✓ 收到審批決策: {self.approval_decision}")

            # 根據審批結果處理
            if self.approval_decision == "approved":
                self.request.status = ApprovalStatus.APPROVED
                self.request.approver = approver
                self.request.approved_at = workflow.now().isoformat()
                self.request.comment = self.approval_comment

                # 處理批准的請求
                result = await workflow.execute_activity(
                    process_approved_request,
                    self.request,
                    start_to_close_timeout=timedelta(minutes=5),
                )

                return {
                    "status": "approved",
                    "request_id": request.request_id,
                    "result": result,
                    "comment": self.approval_comment
                }

            else:  # rejected
                self.request.status = ApprovalStatus.REJECTED
                self.request.comment = self.approval_comment

                return {
                    "status": "rejected",
                    "request_id": request.request_id,
                    "comment": self.approval_comment
                }

        except asyncio.TimeoutError:
            print(f"   ✗ 審批超時")
            self.request.status = ApprovalStatus.CANCELLED

            return {
                "status": "timeout",
                "request_id": request.request_id,
                "message": f"審批超時（{timeout_minutes} 分鐘內未響應）"
            }

    @workflow.signal
    async def approve(self, comment: str = ""):
        """
        批准信號

        外部調用此方法來批准請求
        """
        print(f"   📥 收到批准信號")
        self.approval_decision = "approved"
        self.approval_comment = comment
        self.approval_received = True

    @workflow.signal
    async def reject(self, comment: str = ""):
        """
        拒絕信號

        外部調用此方法來拒絕請求
        """
        print(f"   📥 收到拒絕信號")
        self.approval_decision = "rejected"
        self.approval_comment = comment
        self.approval_received = True

    @workflow.query
    def get_status(self) -> dict:
        """
        查詢當前狀態

        外部可以隨時查詢工作流狀態
        """
        return {
            "request_id": self.request.request_id if self.request else None,
            "status": self.request.status.value if self.request else "not_started",
            "approval_received": self.approval_received,
            "decision": self.approval_decision
        }


# ============================================================
# 工作流 2: 可控制的訂單處理工作流
# ============================================================

@workflow.defn
class ControllableOrderWorkflow:
    """
    可控制的訂單處理工作流

    演示如何使用 Signal 控制工作流執行（暫停/繼續/取消）
    """

    def __init__(self):
        self.order: Optional[OrderInfo] = None
        self.is_paused = False
        self.is_cancelled = False
        self.priority = 0  # 優先級

    @workflow.run
    async def run(self, order: OrderInfo) -> dict:
        """
        執行訂單處理

        可以通過 Signal 暫停、繼續或取消
        """
        self.order = order
        self._update_status(OrderStatus.PROCESSING)

        print(f"\n📦 訂單處理開始: {order.order_id}")

        # 步驟 1: 驗證庫存
        print(f"   [1/3] 驗證庫存...")
        await self._check_pause_or_cancel()
        await asyncio.sleep(1)

        if self.is_cancelled:
            return self._get_cancelled_result()

        # 步驟 2: 處理支付
        print(f"   [2/3] 處理支付...")
        await self._check_pause_or_cancel()
        await asyncio.sleep(1)

        if self.is_cancelled:
            return self._get_cancelled_result()

        # 步驟 3: 安排發貨
        print(f"   [3/3] 安排發貨...")
        await self._check_pause_or_cancel()

        result = await workflow.execute_activity(
            process_order,
            order.order_id,
            start_to_close_timeout=timedelta(minutes=5),
        )

        if self.is_cancelled:
            return self._get_cancelled_result()

        self._update_status(OrderStatus.COMPLETED)

        return {
            "status": "completed",
            "order_id": order.order_id,
            "result": result,
            "priority": self.priority,
            "status_history": self.order.status_history
        }

    async def _check_pause_or_cancel(self):
        """檢查是否需要暫停或取消"""
        # 如果被暫停，等待繼續信號
        while self.is_paused and not self.is_cancelled:
            print(f"   ⏸️  工作流已暫停，等待繼續...")
            await asyncio.sleep(1)

    def _update_status(self, new_status: OrderStatus):
        """更新狀態"""
        if self.order:
            self.order.status = new_status
            self.order.status_history.append({
                "status": new_status.value,
                "timestamp": workflow.now().isoformat()
            })

    def _get_cancelled_result(self) -> dict:
        """獲取取消結果"""
        self._update_status(OrderStatus.CANCELLED)
        return {
            "status": "cancelled",
            "order_id": self.order.order_id,
            "message": "訂單已取消"
        }

    @workflow.signal
    async def pause(self):
        """暫停工作流"""
        print(f"   📥 收到暫停信號")
        self.is_paused = True
        self._update_status(OrderStatus.PAUSED)

    @workflow.signal
    async def resume(self):
        """繼續工作流"""
        print(f"   📥 收到繼續信號")
        self.is_paused = False
        self._update_status(OrderStatus.PROCESSING)

    @workflow.signal
    async def cancel(self):
        """取消工作流"""
        print(f"   📥 收到取消信號")
        self.is_cancelled = True
        self.is_paused = False  # 確保不會卡在暫停狀態

    @workflow.signal
    async def update_priority(self, new_priority: int):
        """更新優先級"""
        print(f"   📥 更新優先級: {self.priority} -> {new_priority}")
        self.priority = new_priority

    @workflow.query
    def get_status(self) -> dict:
        """查詢當前狀態"""
        return {
            "order_id": self.order.order_id if self.order else None,
            "status": self.order.status.value if self.order else "not_started",
            "is_paused": self.is_paused,
            "is_cancelled": self.is_cancelled,
            "priority": self.priority,
            "status_history": self.order.status_history if self.order else []
        }

    @workflow.query
    def get_order_info(self) -> dict:
        """查詢訂單詳細信息"""
        if not self.order:
            return {}

        return {
            "order_id": self.order.order_id,
            "items": self.order.items,
            "total": self.order.total,
            "status": self.order.status.value
        }


# ============================================================
# 工作流 3: 多信號協調工作流
# ============================================================

@workflow.defn
class MultiSignalWorkflow:
    """
    多信號協調工作流

    演示處理多個不同的信號
    """

    def __init__(self):
        self.messages: List[str] = []
        self.config: dict = {"max_items": 10}
        self.should_stop = False

    @workflow.run
    async def run(self, duration_minutes: int = 5) -> dict:
        """
        運行指定時間，接收各種信號
        """
        print(f"\n🎯 多信號工作流開始（運行 {duration_minutes} 分鐘）")

        start_time = workflow.now()
        end_time = start_time + timedelta(minutes=duration_minutes)

        iteration = 0

        while workflow.now() < end_time and not self.should_stop:
            iteration += 1
            print(f"   迭代 {iteration}: {len(self.messages)} 條消息")

            await asyncio.sleep(5)  # 每 5 秒一次迭代

        print(f"   工作流結束")

        return {
            "iterations": iteration,
            "messages_received": len(self.messages),
            "messages": self.messages,
            "config": self.config,
            "stopped_early": self.should_stop
        }

    @workflow.signal
    async def add_message(self, message: str):
        """添加消息信號"""
        print(f"   📥 收到消息: {message}")
        self.messages.append(message)

    @workflow.signal
    async def update_config(self, key: str, value: any):
        """更新配置信號"""
        print(f"   📥 更新配置: {key} = {value}")
        self.config[key] = value

    @workflow.signal
    async def clear_messages(self):
        """清空消息信號"""
        print(f"   📥 清空消息")
        self.messages.clear()

    @workflow.signal
    async def stop(self):
        """停止工作流信號"""
        print(f"   📥 收到停止信號")
        self.should_stop = True

    @workflow.query
    def get_message_count(self) -> int:
        """查詢消息數量"""
        return len(self.messages)

    @workflow.query
    def get_messages(self) -> List[str]:
        """查詢所有消息"""
        return self.messages

    @workflow.query
    def get_config(self) -> dict:
        """查詢配置"""
        return self.config


# ============================================================
# Worker 和 Client
# ============================================================

async def run_worker():
    """啟動 Worker"""
    client = await Client.connect("localhost:7233")

    print("=" * 60)
    print("🚀 Signal/Query Worker 啟動中...")
    print("=" * 60)

    worker = Worker(
        client,
        task_queue="signal-query-queue",
        workflows=[
            ApprovalWorkflow,
            ControllableOrderWorkflow,
            MultiSignalWorkflow,
        ],
        activities=[
            send_approval_notification,
            process_approved_request,
            process_order,
            send_notification,
        ],
    )

    await worker.run()


async def run_client():
    """演示 Signal 和 Query 的使用"""
    client = await Client.connect("localhost:7233")

    print("\n" + "=" * 60)
    print("📋 Signal 和 Query 示例")
    print("=" * 60)

    # ========================================
    # 示例 1: 審批工作流
    # ========================================
    print("\n【示例 1】審批工作流 - Signal 交互")
    print("-" * 60)

    request = ApprovalRequest(
        request_id="REQ-001",
        title="採購設備",
        description="購買開發服務器",
        amount=5000.0,
        requester="alice@example.com"
    )

    # 啟動審批工作流（不等待完成）
    handle = await client.start_workflow(
        ApprovalWorkflow.run,
        request,
        "manager@example.com",
        2,  # 2 分鐘超時
        id="approval-workflow-1",
        task_queue="signal-query-queue",
    )

    print(f"✓ 審批工作流已啟動: {handle.id}")

    # 等待 2 秒
    await asyncio.sleep(2)

    # 查詢狀態
    status = await handle.query(ApprovalWorkflow.get_status)
    print(f"📊 當前狀態: {status}")

    # 等待 1 秒
    await asyncio.sleep(1)

    # 發送批准信號
    print(f"✅ 發送批准信號...")
    await handle.signal(ApprovalWorkflow.approve, "預算充足，批准採購")

    # 等待工作流完成
    result = await handle.result()
    print(f"✓ 審批完成: {result['status']}")
    print(f"   備註: {result.get('comment', 'N/A')}\n")

    # ========================================
    # 示例 2: 可控制的訂單工作流
    # ========================================
    print("【示例 2】可控制的訂單工作流 - 暫停/繼續")
    print("-" * 60)

    order = OrderInfo(
        order_id="ORDER-001",
        items=["商品A", "商品B"],
        total=299.99
    )

    # 啟動訂單工作流
    handle = await client.start_workflow(
        ControllableOrderWorkflow.run,
        order,
        id="order-workflow-1",
        task_queue="signal-query-queue",
    )

    print(f"✓ 訂單工作流已啟動: {handle.id}")

    # 等待 1.5 秒
    await asyncio.sleep(1.5)

    # 暫停工作流
    print(f"⏸️  暫停工作流...")
    await handle.signal(ControllableOrderWorkflow.pause)

    # 查詢狀態
    await asyncio.sleep(0.5)
    status = await handle.query(ControllableOrderWorkflow.get_status)
    print(f"📊 狀態: {status['status']}, 暫停: {status['is_paused']}")

    # 更新優先級
    print(f"⬆️  更新優先級為 5...")
    await handle.signal(ControllableOrderWorkflow.update_priority, 5)

    # 等待 2 秒
    await asyncio.sleep(2)

    # 繼續工作流
    print(f"▶️  繼續工作流...")
    await handle.signal(ControllableOrderWorkflow.resume)

    # 等待完成
    result = await handle.result()
    print(f"✓ 訂單完成: {result['status']}")
    print(f"   優先級: {result['priority']}\n")

    # ========================================
    # 示例 3: 多信號工作流
    # ========================================
    print("【示例 3】多信號協調 - 動態交互")
    print("-" * 60)

    # 啟動工作流（運行 1 分鐘）
    handle = await client.start_workflow(
        MultiSignalWorkflow.run,
        1,  # 1 分鐘
        id="multi-signal-1",
        task_queue="signal-query-queue",
    )

    print(f"✓ 多信號工作流已啟動: {handle.id}")

    # 發送多個消息
    messages = [
        "第一條消息",
        "第二條消息",
        "重要通知",
    ]

    for msg in messages:
        await handle.signal(MultiSignalWorkflow.add_message, msg)
        await asyncio.sleep(0.5)

    # 查詢消息數量
    count = await handle.query(MultiSignalWorkflow.get_message_count)
    print(f"📊 消息數量: {count}")

    # 更新配置
    await handle.signal(MultiSignalWorkflow.update_config, "max_items", 20)

    # 查詢配置
    config = await handle.query(MultiSignalWorkflow.get_config)
    print(f"⚙️  配置: {config}")

    # 發送停止信號（提前結束）
    print(f"🛑 發送停止信號...")
    await handle.signal(MultiSignalWorkflow.stop)

    # 等待完成
    result = await handle.result()
    print(f"✓ 工作流完成:")
    print(f"   迭代次數: {result['iterations']}")
    print(f"   消息數: {result['messages_received']}")
    print(f"   提前停止: {result['stopped_early']}\n")

    print("=" * 60)


async def main():
    """主函數"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "client":
        await run_client()
    else:
        await run_worker()


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║              Temporal Signal 和 Query                        ║
╚══════════════════════════════════════════════════════════════╝

Signal（信號）：
--------------
- 向運行中的工作流發送數據
- 可以改變工作流狀態
- 支持多個不同的信號
- 實現人機交互、工作流控制

Query（查詢）：
-------------
- 查詢工作流當前狀態
- 只讀操作，不改變狀態
- 可以隨時查詢
- 獲取實時信息

使用場景：
---------
1. 審批流程 - 等待人工決策
2. 工作流控制 - 暫停/繼續/取消
3. 動態配置 - 運行時更新參數
4. 進度查詢 - 查看執行狀態

使用方法：
---------
1. 啟動 Worker: python 06_信號通信.py
2. 執行示例: python 06_信號通信.py client
    """)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 程序已停止")
