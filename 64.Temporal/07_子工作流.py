"""
Temporal 子工作流 - 子流程調用

這個示例展示了：
1. 子工作流的定義和調用
2. 父子工作流通信
3. 工作流組合模式
4. 子工作流錯誤處理
5. 並行執行多個子工作流
6. 子工作流的獨立性
7. 子工作流 ID 管理
8. 複雜業務流程分解
"""

import asyncio
from dataclasses import dataclass
from datetime import timedelta
from typing import List, Optional

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError, ChildWorkflowError
from temporalio.worker import Worker


# ============================================================
# 數據模型
# ============================================================

@dataclass
class User:
    """用戶數據"""
    user_id: str
    name: str
    email: str


@dataclass
class Product:
    """產品數據"""
    product_id: str
    name: str
    price: float
    quantity: int


@dataclass
class Order:
    """訂單數據"""
    order_id: str
    user: User
    products: List[Product]
    total_amount: float


@dataclass
class Payment:
    """支付數據"""
    payment_id: str
    order_id: str
    amount: float
    status: str


# ============================================================
# Activity 定義
# ============================================================

@activity.defn
async def validate_user(user: User) -> bool:
    """驗證用戶"""
    print(f"👤 驗證用戶: {user.name}")
    await asyncio.sleep(0.3)
    return True


@activity.defn
async def check_product_stock(product: Product) -> bool:
    """檢查產品庫存"""
    print(f"📦 檢查庫存: {product.name} x {product.quantity}")
    await asyncio.sleep(0.3)
    # 模擬庫存檢查
    return product.quantity <= 10


@activity.defn
async def reserve_product(product: Product) -> str:
    """預留產品"""
    print(f"🔒 預留產品: {product.name} x {product.quantity}")
    await asyncio.sleep(0.3)
    return f"RESERVE-{product.product_id}"


@activity.defn
async def process_payment_activity(order_id: str, amount: float) -> Payment:
    """處理支付"""
    print(f"💳 處理支付: 訂單 {order_id}, 金額 ${amount}")
    await asyncio.sleep(1)

    return Payment(
        payment_id=f"PAY-{order_id}",
        order_id=order_id,
        amount=amount,
        status="completed"
    )


@activity.defn
async def ship_products(order_id: str, products: List[Product]) -> str:
    """發貨"""
    print(f"🚚 發貨: 訂單 {order_id}, {len(products)} 個商品")
    await asyncio.sleep(1)
    return f"TRACK-{order_id}"


@activity.defn
async def send_email(to: str, subject: str, body: str) -> bool:
    """發送郵件"""
    print(f"📧 發送郵件給 {to}: {subject}")
    await asyncio.sleep(0.3)
    return True


@activity.defn
async def generate_invoice(order: Order) -> str:
    """生成發票"""
    print(f"📄 生成發票: 訂單 {order.order_id}")
    await asyncio.sleep(0.5)
    return f"INVOICE-{order.order_id}"


# ============================================================
# 子工作流定義
# ============================================================

@workflow.defn
class UserValidationWorkflow:
    """
    用戶驗證子工作流

    專門負責用戶驗證邏輯
    """

    @workflow.run
    async def run(self, user: User) -> dict:
        """執行用戶驗證"""
        print(f"\n  [子工作流] 用戶驗證: {user.user_id}")

        # 驗證用戶
        is_valid = await workflow.execute_activity(
            validate_user,
            user,
            start_to_close_timeout=timedelta(seconds=10),
        )

        if not is_valid:
            raise ApplicationError("用戶驗證失敗")

        return {
            "user_id": user.user_id,
            "validated": True,
            "workflow_id": workflow.info().workflow_id
        }


@workflow.defn
class InventoryWorkflow:
    """
    庫存管理子工作流

    處理單個產品的庫存檢查和預留
    """

    @workflow.run
    async def run(self, product: Product) -> dict:
        """執行庫存處理"""
        print(f"\n  [子工作流] 庫存處理: {product.product_id}")

        # 檢查庫存
        stock_available = await workflow.execute_activity(
            check_product_stock,
            product,
            start_to_close_timeout=timedelta(seconds=10),
        )

        if not stock_available:
            raise ApplicationError(f"庫存不足: {product.name}")

        # 預留庫存
        reservation_id = await workflow.execute_activity(
            reserve_product,
            product,
            start_to_close_timeout=timedelta(seconds=10),
        )

        return {
            "product_id": product.product_id,
            "reservation_id": reservation_id,
            "quantity": product.quantity
        }


@workflow.defn
class PaymentWorkflow:
    """
    支付處理子工作流

    專門處理支付邏輯
    """

    @workflow.run
    async def run(self, order_id: str, amount: float) -> Payment:
        """執行支付處理"""
        print(f"\n  [子工作流] 支付處理: {order_id}")

        # 處理支付
        payment = await workflow.execute_activity(
            process_payment_activity,
            order_id,
            amount,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=1),
            ),
        )

        if payment.status != "completed":
            raise ApplicationError("支付失敗")

        return payment


@workflow.defn
class ShippingWorkflow:
    """
    發貨子工作流

    處理商品發貨
    """

    @workflow.run
    async def run(self, order_id: str, products: List[Product]) -> dict:
        """執行發貨處理"""
        print(f"\n  [子工作流] 發貨處理: {order_id}")

        # 發貨
        tracking_number = await workflow.execute_activity(
            ship_products,
            order_id,
            products,
            start_to_close_timeout=timedelta(minutes=10),
        )

        return {
            "order_id": order_id,
            "tracking_number": tracking_number,
            "product_count": len(products)
        }


@workflow.defn
class NotificationWorkflow:
    """
    通知子工作流

    發送各種通知
    """

    @workflow.run
    async def run(self, user_email: str, notification_type: str, data: dict) -> bool:
        """發送通知"""
        print(f"\n  [子工作流] 通知: {notification_type}")

        # 根據類型構造郵件內容
        if notification_type == "order_confirmation":
            subject = f"訂單確認 - {data['order_id']}"
            body = f"您的訂單已確認，金額：${data['amount']}"

        elif notification_type == "payment_success":
            subject = f"支付成功 - {data['payment_id']}"
            body = f"支付已完成，金額：${data['amount']}"

        elif notification_type == "shipping":
            subject = f"商品已發貨"
            body = f"物流單號：{data['tracking_number']}"

        else:
            subject = "通知"
            body = str(data)

        # 發送郵件
        sent = await workflow.execute_activity(
            send_email,
            user_email,
            subject,
            body,
            start_to_close_timeout=timedelta(seconds=30),
        )

        return sent


# ============================================================
# 父工作流：訂單處理
# ============================================================

@workflow.defn
class OrderProcessingWorkflow:
    """
    訂單處理主工作流

    編排多個子工作流完成完整的訂單流程
    """

    @workflow.run
    async def run(self, order: Order) -> dict:
        """
        執行完整的訂單處理流程

        流程：
        1. 用戶驗證
        2. 庫存檢查（並行處理多個產品）
        3. 支付處理
        4. 發貨
        5. 發送通知
        """
        print(f"\n🛒 訂單處理主工作流: {order.order_id}")
        results = {}

        # ===== 步驟 1: 用戶驗證子工作流 =====
        print(f"\n📋 步驟 1: 用戶驗證")
        user_validation_result = await workflow.execute_child_workflow(
            UserValidationWorkflow.run,
            order.user,
            id=f"{order.order_id}-user-validation",
            task_queue="child-workflow-queue",
        )
        results["user_validation"] = user_validation_result
        print(f"  ✓ 用戶驗證完成")

        # ===== 步驟 2: 庫存處理（並行執行多個子工作流）=====
        print(f"\n📋 步驟 2: 庫存處理（並行）")
        inventory_tasks = []
        for i, product in enumerate(order.products):
            task = workflow.execute_child_workflow(
                InventoryWorkflow.run,
                product,
                id=f"{order.order_id}-inventory-{i}",
                task_queue="child-workflow-queue",
            )
            inventory_tasks.append(task)

        try:
            inventory_results = await asyncio.gather(*inventory_tasks)
            results["inventory"] = inventory_results
            print(f"  ✓ 所有產品庫存處理完成")
        except ChildWorkflowError as e:
            print(f"  ✗ 庫存處理失敗: {e}")
            raise ApplicationError("庫存不足，訂單取消")

        # ===== 步驟 3: 支付處理子工作流 =====
        print(f"\n📋 步驟 3: 支付處理")
        payment_result = await workflow.execute_child_workflow(
            PaymentWorkflow.run,
            order.order_id,
            order.total_amount,
            id=f"{order.order_id}-payment",
            task_queue="child-workflow-queue",
        )
        results["payment"] = {
            "payment_id": payment_result.payment_id,
            "amount": payment_result.amount,
            "status": payment_result.status
        }
        print(f"  ✓ 支付完成: {payment_result.payment_id}")

        # ===== 步驟 4: 發貨子工作流 =====
        print(f"\n📋 步驟 4: 發貨處理")
        shipping_result = await workflow.execute_child_workflow(
            ShippingWorkflow.run,
            order.order_id,
            order.products,
            id=f"{order.order_id}-shipping",
            task_queue="child-workflow-queue",
        )
        results["shipping"] = shipping_result
        print(f"  ✓ 發貨完成: {shipping_result['tracking_number']}")

        # ===== 步驟 5: 發送通知（並行發送多個通知）=====
        print(f"\n📋 步驟 5: 發送通知（並行）")
        notification_tasks = [
            # 訂單確認通知
            workflow.execute_child_workflow(
                NotificationWorkflow.run,
                order.user.email,
                "order_confirmation",
                {"order_id": order.order_id, "amount": order.total_amount},
                id=f"{order.order_id}-notif-order",
                task_queue="child-workflow-queue",
            ),
            # 支付成功通知
            workflow.execute_child_workflow(
                NotificationWorkflow.run,
                order.user.email,
                "payment_success",
                {"payment_id": payment_result.payment_id, "amount": order.total_amount},
                id=f"{order.order_id}-notif-payment",
                task_queue="child-workflow-queue",
            ),
            # 發貨通知
            workflow.execute_child_workflow(
                NotificationWorkflow.run,
                order.user.email,
                "shipping",
                {"tracking_number": shipping_result['tracking_number']},
                id=f"{order.order_id}-notif-shipping",
                task_queue="child-workflow-queue",
            ),
        ]

        notification_results = await asyncio.gather(*notification_tasks)
        results["notifications_sent"] = all(notification_results)
        print(f"  ✓ 所有通知已發送")

        # ===== 生成發票 =====
        invoice_id = await workflow.execute_activity(
            generate_invoice,
            order,
            start_to_close_timeout=timedelta(seconds=30),
        )
        results["invoice_id"] = invoice_id

        print(f"\n✅ 訂單處理完成: {order.order_id}")

        return {
            "order_id": order.order_id,
            "status": "completed",
            "results": results,
            "total_amount": order.total_amount
        }


# ============================================================
# 批量訂單處理工作流
# ============================================================

@workflow.defn
class BatchOrderWorkflow:
    """
    批量訂單處理工作流

    演示如何並行執行多個子工作流
    """

    @workflow.run
    async def run(self, orders: List[Order]) -> dict:
        """
        並行處理多個訂單

        每個訂單都作為獨立的子工作流執行
        """
        print(f"\n📦 批量訂單處理: {len(orders)} 個訂單")

        # 為每個訂單創建子工作流
        order_tasks = []
        for i, order in enumerate(orders):
            task = workflow.execute_child_workflow(
                OrderProcessingWorkflow.run,
                order,
                id=f"batch-order-{i}-{order.order_id}",
                task_queue="child-workflow-queue",
            )
            order_tasks.append((order.order_id, task))

        # 並行執行所有訂單
        results = []
        failed = []

        for order_id, task in order_tasks:
            try:
                result = await task
                results.append(result)
            except Exception as e:
                print(f"  ✗ 訂單 {order_id} 失敗: {e}")
                failed.append({"order_id": order_id, "error": str(e)})

        return {
            "total_orders": len(orders),
            "successful": len(results),
            "failed": len(failed),
            "results": results,
            "failures": failed
        }


# ============================================================
# Worker 和 Client
# ============================================================

async def run_worker():
    """啟動 Worker"""
    client = await Client.connect("localhost:7233")

    print("=" * 60)
    print("🚀 子工作流 Worker 啟動中...")
    print("=" * 60)

    worker = Worker(
        client,
        task_queue="child-workflow-queue",
        workflows=[
            # 父工作流
            OrderProcessingWorkflow,
            BatchOrderWorkflow,
            # 子工作流
            UserValidationWorkflow,
            InventoryWorkflow,
            PaymentWorkflow,
            ShippingWorkflow,
            NotificationWorkflow,
        ],
        activities=[
            validate_user,
            check_product_stock,
            reserve_product,
            process_payment_activity,
            ship_products,
            send_email,
            generate_invoice,
        ],
    )

    print("等待任務中...\n")
    await worker.run()


async def run_client():
    """執行示例"""
    client = await Client.connect("localhost:7233")

    print("\n" + "=" * 60)
    print("📋 子工作流示例演示")
    print("=" * 60)

    # ========================================
    # 示例 1: 單個訂單處理
    # ========================================
    print("\n【示例 1】單個訂單處理 - 子工作流編排")
    print("-" * 60)

    user = User(
        user_id="user123",
        name="Alice Wang",
        email="alice@example.com"
    )

    products = [
        Product("prod1", "筆記本電腦", 1200.0, 1),
        Product("prod2", "無線鼠標", 50.0, 2),
        Product("prod3", "機械鍵盤", 150.0, 1),
    ]

    order = Order(
        order_id="ORDER-001",
        user=user,
        products=products,
        total_amount=1450.0
    )

    result = await client.execute_workflow(
        OrderProcessingWorkflow.run,
        order,
        id="order-processing-1",
        task_queue="child-workflow-queue",
    )

    print(f"\n✓ 訂單處理結果:")
    print(f"   訂單 ID: {result['order_id']}")
    print(f"   狀態: {result['status']}")
    print(f"   總金額: ${result['total_amount']}")
    print(f"   發票: {result['results']['invoice_id']}")
    print()

    # ========================================
    # 示例 2: 批量訂單處理
    # ========================================
    print("【示例 2】批量訂單處理 - 並行子工作流")
    print("-" * 60)

    orders = [
        Order(
            order_id=f"ORDER-00{i}",
            user=User(f"user{i}", f"User {i}", f"user{i}@example.com"),
            products=[Product(f"prod{i}", f"Product {i}", 100.0 * i, 1)],
            total_amount=100.0 * i
        )
        for i in range(2, 5)
    ]

    result = await client.execute_workflow(
        BatchOrderWorkflow.run,
        orders,
        id="batch-order-1",
        task_queue="child-workflow-queue",
    )

    print(f"\n✓ 批量處理結果:")
    print(f"   總訂單數: {result['total_orders']}")
    print(f"   成功: {result['successful']}")
    print(f"   失敗: {result['failed']}")
    print()

    print("=" * 60)
    print("提示：訪問 http://localhost:8080 查看工作流層次結構")
    print("=" * 60 + "\n")


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
║              Temporal 子工作流與流程組合                       ║
╚══════════════════════════════════════════════════════════════╝

子工作流優勢：
------------
1. 模塊化 - 將複雜流程分解為獨立單元
2. 可重用 - 子工作流可被多個父工作流調用
3. 獨立性 - 每個子工作流有獨立的歷史和狀態
4. 並行化 - 多個子工作流可並行執行
5. 清晰性 - 提高代碼可讀性和維護性

子工作流特點：
------------
- 有獨立的 Workflow ID
- 可以獨立查詢和監控
- 失敗不會直接影響父工作流（可捕獲異常）
- 可以有自己的重試策略

使用場景：
---------
- 複雜業務流程分解
- 可重用的業務邏輯
- 需要並行執行的獨立任務
- 長時間運行的子任務

使用方法：
---------
1. 啟動 Worker: python 07_子工作流.py
2. 執行示例: python 07_子工作流.py client
    """)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 程序已停止")
