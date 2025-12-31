"""
Temporal 工作流編排 - 複雜工作流模式

這個示例展示了：
1. 串行執行（Sequential）
2. 並行執行（Parallel）
3. 條件分支（Conditional）
4. 循環處理（Loop）
5. 動態工作流（Dynamic）
6. Saga 模式（補償事務）
7. 扇出/扇入模式（Fan-out/Fan-in）
8. 管道模式（Pipeline）
"""

import asyncio
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from typing import List, Optional

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError
from temporalio.worker import Worker


# ============================================================
# 數據模型
# ============================================================

class OrderStatus(str, Enum):
    """訂單狀態"""
    CREATED = "created"
    INVENTORY_CHECKED = "inventory_checked"
    PAYMENT_PROCESSED = "payment_processed"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATED = "compensated"


@dataclass
class OrderData:
    """訂單數據"""
    order_id: str
    user_id: str
    items: List[str]
    total_amount: float
    status: OrderStatus = OrderStatus.CREATED


@dataclass
class PaymentInfo:
    """支付信息"""
    payment_id: str
    amount: float
    method: str


# ============================================================
# Activity 定義
# ============================================================

@activity.defn
async def check_inventory(order: OrderData) -> bool:
    """檢查庫存"""
    print(f"📦 檢查庫存: 訂單 {order.order_id}")
    await asyncio.sleep(0.5)

    # 模擬庫存檢查
    available = len(order.items) <= 5  # 簡單邏輯
    print(f"  庫存{'充足' if available else '不足'}")
    return available


@activity.defn
async def reserve_inventory(order: OrderData) -> bool:
    """預留庫存"""
    print(f"🔒 預留庫存: 訂單 {order.order_id}")
    await asyncio.sleep(0.5)
    return True


@activity.defn
async def release_inventory(order: OrderData) -> bool:
    """釋放庫存（補償操作）"""
    print(f"🔓 釋放庫存: 訂單 {order.order_id}")
    await asyncio.sleep(0.3)
    return True


@activity.defn
async def process_payment(order: OrderData) -> PaymentInfo:
    """處理支付"""
    print(f"💳 處理支付: 訂單 {order.order_id}, 金額 ${order.total_amount}")
    await asyncio.sleep(1)

    payment_info = PaymentInfo(
        payment_id=f"PAY-{order.order_id}",
        amount=order.total_amount,
        method="credit_card"
    )
    print(f"  支付成功: {payment_info.payment_id}")
    return payment_info


@activity.defn
async def refund_payment(payment_info: PaymentInfo) -> bool:
    """退款（補償操作）"""
    print(f"💰 退款: {payment_info.payment_id}, 金額 ${payment_info.amount}")
    await asyncio.sleep(0.5)
    return True


@activity.defn
async def ship_order(order: OrderData) -> str:
    """發貨"""
    print(f"🚚 發貨: 訂單 {order.order_id}")
    await asyncio.sleep(1)

    tracking_number = f"TRACK-{order.order_id}"
    print(f"  物流單號: {tracking_number}")
    return tracking_number


@activity.defn
async def send_notification(user_id: str, message: str) -> bool:
    """發送通知"""
    print(f"📧 發送通知給用戶 {user_id}: {message}")
    await asyncio.sleep(0.3)
    return True


@activity.defn
async def update_order_status(order_id: str, status: OrderStatus) -> bool:
    """更新訂單狀態"""
    print(f"📝 更新訂單狀態: {order_id} -> {status.value}")
    await asyncio.sleep(0.2)
    return True


# 數據處理相關 Activities

@activity.defn
async def fetch_data(source: str) -> dict:
    """獲取數據"""
    print(f"🔽 從 {source} 獲取數據")
    await asyncio.sleep(0.5)
    return {"source": source, "data": f"data_from_{source}"}


@activity.defn
async def transform_data(data: dict) -> dict:
    """轉換數據"""
    print(f"🔄 轉換數據: {data['source']}")
    await asyncio.sleep(0.3)
    return {"source": data["source"], "transformed": data["data"].upper()}


@activity.defn
async def load_data(data: dict) -> bool:
    """加載數據"""
    print(f"🔼 加載數據: {data['source']}")
    await asyncio.sleep(0.4)
    return True


# ============================================================
# 模式 1: 串行執行工作流
# ============================================================

@workflow.defn
class SequentialWorkflow:
    """
    串行執行工作流

    步驟按順序一個接一個執行
    適用於：有依賴關係的步驟
    """

    @workflow.run
    async def run(self, order: OrderData) -> dict:
        """執行訂單處理流程（串行）"""

        print(f"\n🔄 開始處理訂單: {order.order_id}")

        # 步驟 1: 檢查庫存
        inventory_ok = await workflow.execute_activity(
            check_inventory,
            order,
            start_to_close_timeout=timedelta(seconds=10),
        )

        if not inventory_ok:
            return {"success": False, "reason": "庫存不足"}

        # 步驟 2: 預留庫存
        await workflow.execute_activity(
            reserve_inventory,
            order,
            start_to_close_timeout=timedelta(seconds=10),
        )

        # 步驟 3: 處理支付
        payment_info = await workflow.execute_activity(
            process_payment,
            order,
            start_to_close_timeout=timedelta(seconds=30),
        )

        # 步驟 4: 發貨
        tracking = await workflow.execute_activity(
            ship_order,
            order,
            start_to_close_timeout=timedelta(seconds=30),
        )

        # 步驟 5: 發送通知
        await workflow.execute_activity(
            send_notification,
            order.user_id,
            f"訂單 {order.order_id} 已發貨，物流單號：{tracking}",
            start_to_close_timeout=timedelta(seconds=10),
        )

        return {
            "success": True,
            "order_id": order.order_id,
            "payment_id": payment_info.payment_id,
            "tracking_number": tracking
        }


# ============================================================
# 模式 2: 並行執行工作流
# ============================================================

@workflow.defn
class ParallelWorkflow:
    """
    並行執行工作流

    多個獨立任務同時執行
    適用於：沒有依賴關係的步驟
    """

    @workflow.run
    async def run(self, user_id: str) -> dict:
        """並行執行多個獨立任務"""

        print(f"\n⚡ 並行處理用戶任務: {user_id}")

        # 創建多個並行任務
        tasks = [
            workflow.execute_activity(
                send_notification,
                user_id,
                "歡迎郵件",
                start_to_close_timeout=timedelta(seconds=10),
            ),
            workflow.execute_activity(
                send_notification,
                user_id,
                "SMS 驗證碼",
                start_to_close_timeout=timedelta(seconds=10),
            ),
            workflow.execute_activity(
                send_notification,
                user_id,
                "APP 推送",
                start_to_close_timeout=timedelta(seconds=10),
            ),
        ]

        # 並行執行所有任務
        results = await asyncio.gather(*tasks)

        return {
            "user_id": user_id,
            "notifications_sent": len(results),
            "all_successful": all(results)
        }


# ============================================================
# 模式 3: 條件分支工作流
# ============================================================

@workflow.defn
class ConditionalWorkflow:
    """
    條件分支工作流

    根據條件選擇不同的執行路徑
    """

    @workflow.run
    async def run(self, order: OrderData, is_premium_user: bool) -> dict:
        """根據用戶類型執行不同的處理流程"""

        print(f"\n🔀 條件處理: 訂單 {order.order_id}")

        # 檢查庫存
        inventory_ok = await workflow.execute_activity(
            check_inventory,
            order,
            start_to_close_timeout=timedelta(seconds=10),
        )

        if not inventory_ok:
            # 庫存不足的處理
            if is_premium_user:
                # VIP 用戶：發送缺貨通知，稍後處理
                await workflow.execute_activity(
                    send_notification,
                    order.user_id,
                    "商品暫時缺貨，我們將優先為您安排",
                    start_to_close_timeout=timedelta(seconds=10),
                )
                return {"success": False, "vip_queued": True}
            else:
                # 普通用戶：直接取消
                await workflow.execute_activity(
                    send_notification,
                    order.user_id,
                    "抱歉，商品已售罄",
                    start_to_close_timeout=timedelta(seconds=10),
                )
                return {"success": False, "cancelled": True}

        # 庫存充足，繼續處理
        payment_info = await workflow.execute_activity(
            process_payment,
            order,
            start_to_close_timeout=timedelta(seconds=30),
        )

        # VIP 用戶使用快速物流
        if is_premium_user:
            tracking = await workflow.execute_activity(
                ship_order,
                order,
                start_to_close_timeout=timedelta(seconds=30),
            )
            message = f"VIP訂單已使用極速物流發貨：{tracking}"
        else:
            tracking = await workflow.execute_activity(
                ship_order,
                order,
                start_to_close_timeout=timedelta(seconds=30),
            )
            message = f"訂單已發貨：{tracking}"

        await workflow.execute_activity(
            send_notification,
            order.user_id,
            message,
            start_to_close_timeout=timedelta(seconds=10),
        )

        return {
            "success": True,
            "is_premium": is_premium_user,
            "tracking": tracking
        }


# ============================================================
# 模式 4: 循環處理工作流
# ============================================================

@workflow.defn
class LoopWorkflow:
    """
    循環處理工作流

    處理批量數據
    """

    @workflow.run
    async def run(self, user_ids: List[str]) -> dict:
        """批量處理用戶"""

        print(f"\n🔁 批量處理 {len(user_ids)} 個用戶")

        successful = []
        failed = []

        # 循環處理每個用戶
        for user_id in user_ids:
            try:
                result = await workflow.execute_activity(
                    send_notification,
                    user_id,
                    "系統通知",
                    start_to_close_timeout=timedelta(seconds=10),
                    retry_policy=RetryPolicy(maximum_attempts=2),
                )

                if result:
                    successful.append(user_id)
                else:
                    failed.append(user_id)

            except Exception as e:
                print(f"處理用戶 {user_id} 失敗: {e}")
                failed.append(user_id)

        return {
            "total": len(user_ids),
            "successful": len(successful),
            "failed": len(failed),
            "failed_users": failed
        }


# ============================================================
# 模式 5: Saga 模式（補償事務）
# ============================================================

@workflow.defn
class SagaWorkflow:
    """
    Saga 模式工作流

    分佈式事務，支持補償
    當後續步驟失敗時，回滾之前的操作
    """

    @workflow.run
    async def run(self, order: OrderData, should_fail_payment: bool = False) -> dict:
        """
        訂單處理 Saga

        如果任何步驟失敗，執行補償操作
        """

        print(f"\n🔄 Saga: 處理訂單 {order.order_id}")

        compensations = []  # 補償操作列表

        try:
            # 步驟 1: 預留庫存
            await workflow.execute_activity(
                reserve_inventory,
                order,
                start_to_close_timeout=timedelta(seconds=10),
            )
            # 記錄補償操作
            compensations.append(("release_inventory", order))

            # 步驟 2: 處理支付
            if should_fail_payment:
                raise ApplicationError("模擬支付失敗")

            payment_info = await workflow.execute_activity(
                process_payment,
                order,
                start_to_close_timeout=timedelta(seconds=30),
            )
            # 記錄補償操作
            compensations.append(("refund_payment", payment_info))

            # 步驟 3: 發貨
            tracking = await workflow.execute_activity(
                ship_order,
                order,
                start_to_close_timeout=timedelta(seconds=30),
            )

            return {
                "success": True,
                "order_id": order.order_id,
                "tracking": tracking
            }

        except Exception as e:
            print(f"\n❌ 發生錯誤: {e}")
            print("🔙 執行補償操作...")

            # 逆序執行補償操作
            for compensation_name, compensation_arg in reversed(compensations):
                try:
                    if compensation_name == "release_inventory":
                        await workflow.execute_activity(
                            release_inventory,
                            compensation_arg,
                            start_to_close_timeout=timedelta(seconds=10),
                        )
                    elif compensation_name == "refund_payment":
                        await workflow.execute_activity(
                            refund_payment,
                            compensation_arg,
                            start_to_close_timeout=timedelta(seconds=10),
                        )
                except Exception as comp_error:
                    print(f"  補償操作失敗: {comp_error}")

            return {
                "success": False,
                "error": str(e),
                "compensated": True
            }


# ============================================================
# 模式 6: 扇出/扇入模式（Fan-out/Fan-in）
# ============================================================

@workflow.defn
class FanOutFanInWorkflow:
    """
    扇出/扇入模式

    將任務分發到多個並行執行的 Activity，然後聚合結果
    """

    @workflow.run
    async def run(self, sources: List[str]) -> dict:
        """
        從多個數據源並行獲取數據，然後聚合
        """

        print(f"\n🌟 扇出/扇入: 處理 {len(sources)} 個數據源")

        # 扇出：並行獲取所有數據源
        fetch_tasks = [
            workflow.execute_activity(
                fetch_data,
                source,
                start_to_close_timeout=timedelta(seconds=10),
            )
            for source in sources
        ]

        # 等待所有獲取任務完成
        fetched_data = await asyncio.gather(*fetch_tasks)

        # 扇入：聚合結果
        all_data = {
            "sources": sources,
            "data_count": len(fetched_data),
            "data": fetched_data
        }

        return all_data


# ============================================================
# 模式 7: 管道模式（Pipeline）
# ============================================================

@workflow.defn
class PipelineWorkflow:
    """
    管道模式

    數據流經多個處理階段
    ETL (Extract, Transform, Load) 典型模式
    """

    @workflow.run
    async def run(self, sources: List[str]) -> dict:
        """
        ETL 管道處理
        """

        print(f"\n📊 管道處理: {len(sources)} 個數據源")

        results = []

        for source in sources:
            # 階段 1: Extract（提取）
            raw_data = await workflow.execute_activity(
                fetch_data,
                source,
                start_to_close_timeout=timedelta(seconds=10),
            )

            # 階段 2: Transform（轉換）
            transformed = await workflow.execute_activity(
                transform_data,
                raw_data,
                start_to_close_timeout=timedelta(seconds=10),
            )

            # 階段 3: Load（加載）
            loaded = await workflow.execute_activity(
                load_data,
                transformed,
                start_to_close_timeout=timedelta(seconds=10),
            )

            results.append({
                "source": source,
                "loaded": loaded
            })

        return {
            "total_sources": len(sources),
            "results": results,
            "all_successful": all(r["loaded"] for r in results)
        }


# ============================================================
# Worker 和 Client
# ============================================================

async def run_worker():
    """啟動 Worker"""
    client = await Client.connect("localhost:7233")

    print("=" * 60)
    print("🚀 工作流編排 Worker 啟動中...")
    print("=" * 60)

    worker = Worker(
        client,
        task_queue="orchestration-queue",
        workflows=[
            SequentialWorkflow,
            ParallelWorkflow,
            ConditionalWorkflow,
            LoopWorkflow,
            SagaWorkflow,
            FanOutFanInWorkflow,
            PipelineWorkflow,
        ],
        activities=[
            check_inventory,
            reserve_inventory,
            release_inventory,
            process_payment,
            refund_payment,
            ship_order,
            send_notification,
            update_order_status,
            fetch_data,
            transform_data,
            load_data,
        ],
    )

    await worker.run()


async def run_client():
    """執行示例工作流"""
    client = await Client.connect("localhost:7233")

    print("\n" + "=" * 60)
    print("📋 工作流編排模式演示")
    print("=" * 60)

    # 示例 1: 串行執行
    print("\n【示例 1】串行執行 - 訂單處理")
    print("-" * 60)
    order = OrderData(
        order_id="ORDER-001",
        user_id="user123",
        items=["item1", "item2"],
        total_amount=99.99
    )
    result = await client.execute_workflow(
        SequentialWorkflow.run,
        order,
        id="sequential-1",
        task_queue="orchestration-queue",
    )
    print(f"✓ 結果: {result}\n")

    # 示例 2: 並行執行
    print("【示例 2】並行執行 - 多渠道通知")
    print("-" * 60)
    result = await client.execute_workflow(
        ParallelWorkflow.run,
        "user456",
        id="parallel-1",
        task_queue="orchestration-queue",
    )
    print(f"✓ 結果: {result}\n")

    # 示例 3: Saga 模式（成功）
    print("【示例 3】Saga 模式 - 成功場景")
    print("-" * 60)
    result = await client.execute_workflow(
        SagaWorkflow.run,
        order,
        False,  # 不失敗
        id="saga-success-1",
        task_queue="orchestration-queue",
    )
    print(f"✓ 結果: {result}\n")

    # 示例 4: Saga 模式（失敗+補償）
    print("【示例 4】Saga 模式 - 失敗+補償")
    print("-" * 60)
    result = await client.execute_workflow(
        SagaWorkflow.run,
        order,
        True,  # 模擬支付失敗
        id="saga-fail-1",
        task_queue="orchestration-queue",
    )
    print(f"✓ 結果: {result}\n")

    # 示例 5: 扇出/扇入
    print("【示例 5】扇出/扇入 - 並行數據獲取")
    print("-" * 60)
    result = await client.execute_workflow(
        FanOutFanInWorkflow.run,
        ["source1", "source2", "source3"],
        id="fanout-1",
        task_queue="orchestration-queue",
    )
    print(f"✓ 獲取了 {result['data_count']} 個數據源\n")

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
║              Temporal 工作流編排模式                           ║
╚══════════════════════════════════════════════════════════════╝

支持的編排模式：
--------------
1. 串行執行 (Sequential) - 步驟依次執行
2. 並行執行 (Parallel) - 多任務同時執行
3. 條件分支 (Conditional) - 根據條件選擇路徑
4. 循環處理 (Loop) - 批量數據處理
5. Saga 模式 - 分佈式事務+補償
6. 扇出/扇入 (Fan-out/Fan-in) - 並行聚合
7. 管道模式 (Pipeline) - ETL 數據流

使用方法：
---------
1. 啟動 Worker: python 03_工作流編排.py
2. 執行示例: python 03_工作流編排.py client
    """)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 程序已停止")
