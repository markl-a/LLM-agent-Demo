"""
Temporal 版本控制 - 工作流版本管理

這個示例展示了：
1. 工作流版本控制策略
2. 向後兼容的代碼更新
3. Patching API 使用
4. 版本遷移模式
5. 活動簽名變更處理
6. 安全的代碼部署
7. 版本查詢和管理
8. 生產環境最佳實踐
"""

import asyncio
from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.workflow import Workflow


# ============================================================
# 數據模型
# ============================================================

@dataclass
class OrderV1:
    """訂單數據 - 版本 1"""
    order_id: str
    user_id: str
    amount: float


@dataclass
class OrderV2:
    """訂單數據 - 版本 2（新增字段）"""
    order_id: str
    user_id: str
    amount: float
    currency: str = "USD"  # 新增字段
    discount: float = 0.0  # 新增字段


@dataclass
class OrderV3:
    """訂單數據 - 版本 3（重構字段）"""
    order_id: str
    user_id: str
    pricing: dict  # 重構：將 amount, currency, discount 整合


# ============================================================
# Activity 定義（多版本）
# ============================================================

# 版本 1：原始版本
@activity.defn(name="process_payment")
async def process_payment_v1(order_id: str, amount: float) -> dict:
    """處理支付 - V1"""
    print(f"💳 [V1] 處理支付: 訂單 {order_id}, ${amount}")
    await asyncio.sleep(0.5)

    return {
        "version": "v1",
        "order_id": order_id,
        "amount": amount,
        "status": "completed"
    }


# 版本 2：新增貨幣參數
@activity.defn(name="process_payment_v2")
async def process_payment_v2(order_id: str, amount: float, currency: str = "USD") -> dict:
    """處理支付 - V2（新增貨幣）"""
    print(f"💳 [V2] 處理支付: 訂單 {order_id}, {amount} {currency}")
    await asyncio.sleep(0.5)

    return {
        "version": "v2",
        "order_id": order_id,
        "amount": amount,
        "currency": currency,
        "status": "completed"
    }


@activity.defn
async def send_notification_v1(user_id: str, message: str) -> bool:
    """發送通知 - V1"""
    print(f"📧 [V1] 發送通知: {user_id} - {message}")
    await asyncio.sleep(0.3)
    return True


@activity.defn(name="send_notification_v2")
async def send_notification_v2(user_id: str, message: str, channel: str = "email") -> bool:
    """發送通知 - V2（新增渠道）"""
    print(f"📧 [V2] 發送通知 [{channel}]: {user_id} - {message}")
    await asyncio.sleep(0.3)
    return True


@activity.defn
async def validate_order(order_id: str) -> bool:
    """驗證訂單"""
    print(f"✅ 驗證訂單: {order_id}")
    await asyncio.sleep(0.3)
    return True


# ============================================================
# 工作流版本 1：原始版本
# ============================================================

@workflow.defn
class OrderWorkflowV1:
    """
    訂單處理工作流 - 版本 1（原始版本）

    簡單的訂單處理流程
    """

    @workflow.run
    async def run(self, order: OrderV1) -> dict:
        """執行訂單處理 - V1"""

        print(f"\n📦 [V1] 訂單處理開始: {order.order_id}")

        # 步驟 1: 處理支付
        payment_result = await workflow.execute_activity(
            process_payment_v1,
            order.order_id,
            order.amount,
            start_to_close_timeout=timedelta(seconds=30),
        )

        # 步驟 2: 發送通知
        await workflow.execute_activity(
            send_notification_v1,
            order.user_id,
            f"訂單 {order.order_id} 已完成",
            start_to_close_timeout=timedelta(seconds=30),
        )

        return {
            "version": "v1",
            "order_id": order.order_id,
            "payment": payment_result
        }


# ============================================================
# 工作流版本 2：使用 Patching 進行安全升級
# ============================================================

@workflow.defn
class OrderWorkflowV2:
    """
    訂單處理工作流 - 版本 2（使用 Patching）

    新增功能：
    1. 支持多貨幣
    2. 支持折扣
    3. 新增訂單驗證步驟

    使用 Patching 確保向後兼容
    """

    @workflow.run
    async def run(self, order_data: dict) -> dict:
        """
        執行訂單處理 - V2

        使用 dict 參數以支持不同版本的數據結構
        """

        # 兼容性處理：支持 V1 和 V2 數據格式
        if "currency" not in order_data:
            order = OrderV1(**order_data)
            currency = "USD"
            discount = 0.0
        else:
            order = OrderV2(**order_data)
            currency = order.currency
            discount = order.discount

        print(f"\n📦 [V2] 訂單處理開始: {order.order_id}")
        print(f"   貨幣: {currency}, 折扣: {discount}")

        # Patch: 新增訂單驗證（新工作流執行，舊工作流跳過）
        if workflow.patched("add-order-validation"):
            print(f"   [PATCH] 執行訂單驗證（新版本）")
            await workflow.execute_activity(
                validate_order,
                order.order_id,
                start_to_close_timeout=timedelta(seconds=30),
            )
        else:
            print(f"   [PATCH] 跳過訂單驗證（舊版本兼容）")

        # 計算最終金額（考慮折扣）
        final_amount = order.amount - discount

        # Patch: 使用新的支付 API（支持貨幣）
        if workflow.patched("payment-api-v2"):
            print(f"   [PATCH] 使用新支付 API (V2)")
            payment_result = await workflow.execute_activity(
                process_payment_v2,
                order.order_id,
                final_amount,
                currency,
                start_to_close_timeout=timedelta(seconds=30),
            )
        else:
            print(f"   [PATCH] 使用舊支付 API (V1)")
            payment_result = await workflow.execute_activity(
                process_payment_v1,
                order.order_id,
                final_amount,
                start_to_close_timeout=timedelta(seconds=30),
            )

        # Patch: 使用新的通知 API（支持多渠道）
        if workflow.patched("notification-api-v2"):
            print(f"   [PATCH] 使用新通知 API (V2)")
            await workflow.execute_activity(
                send_notification_v2,
                order.user_id,
                f"訂單 {order.order_id} 已完成，金額：{final_amount} {currency}",
                "email",
                start_to_close_timeout=timedelta(seconds=30),
            )
        else:
            print(f"   [PATCH] 使用舊通知 API (V1)")
            await workflow.execute_activity(
                send_notification_v1,
                order.user_id,
                f"訂單 {order.order_id} 已完成",
                start_to_close_timeout=timedelta(seconds=30),
            )

        return {
            "version": "v2",
            "order_id": order.order_id,
            "amount": final_amount,
            "currency": currency,
            "discount": discount,
            "payment": payment_result
        }


# ============================================================
# 工作流版本 3：完全重寫（新工作流）
# ============================================================

@workflow.defn
class OrderWorkflowV3:
    """
    訂單處理工作流 - 版本 3（完全重寫）

    策略：創建新的工作流類型，而不是修改現有的
    優點：
    - 舊工作流實例繼續使用舊代碼
    - 新工作流實例使用新代碼
    - 清晰的版本隔離
    """

    @workflow.run
    async def run(self, order: OrderV3) -> dict:
        """執行訂單處理 - V3（重構版）"""

        print(f"\n📦 [V3] 訂單處理開始: {order.order_id}")
        print(f"   定價信息: {order.pricing}")

        # 步驟 1: 驗證訂單
        await workflow.execute_activity(
            validate_order,
            order.order_id,
            start_to_close_timeout=timedelta(seconds=30),
        )

        # 步驟 2: 處理支付（使用新的定價結構）
        payment_result = await workflow.execute_activity(
            process_payment_v2,
            order.order_id,
            order.pricing["final_amount"],
            order.pricing["currency"],
            start_to_close_timeout=timedelta(seconds=30),
        )

        # 步驟 3: 多渠道通知
        notification_channels = ["email", "sms", "push"]
        for channel in notification_channels:
            await workflow.execute_activity(
                send_notification_v2,
                order.user_id,
                f"訂單 {order.order_id} 已完成",
                channel,
                start_to_close_timeout=timedelta(seconds=30),
            )

        return {
            "version": "v3",
            "order_id": order.order_id,
            "pricing": order.pricing,
            "payment": payment_result,
            "notifications_sent": len(notification_channels)
        }


# ============================================================
# 版本檢測和查詢工作流
# ============================================================

@workflow.defn
class VersionedWorkflow:
    """
    帶版本檢測的工作流

    演示如何在工作流中處理版本信息
    """

    @workflow.run
    async def run(self, data: dict, version: str = "auto") -> dict:
        """
        根據版本執行不同的邏輯
        """

        # 自動檢測版本
        if version == "auto":
            if "pricing" in data:
                version = "v3"
            elif "currency" in data:
                version = "v2"
            else:
                version = "v1"

        print(f"\n🔖 檢測到版本: {version}")

        workflow_version = workflow.info().workflow_type
        workflow_id = workflow.info().workflow_id

        return {
            "detected_version": version,
            "workflow_type": workflow_version,
            "workflow_id": workflow_id,
            "data": data
        }

    @workflow.query
    def get_version(self) -> str:
        """查詢工作流版本"""
        return workflow.info().workflow_type


# ============================================================
# Worker 和 Client
# ============================================================

async def run_worker():
    """
    啟動 Worker

    注意：Worker 需要註冊所有版本的工作流和活動
    這樣才能處理新舊工作流實例
    """
    client = await Client.connect("localhost:7233")

    print("=" * 60)
    print("🚀 版本控制 Worker 啟動中...")
    print("=" * 60)
    print("註冊的工作流版本:")
    print("  - OrderWorkflowV1 (原始版本)")
    print("  - OrderWorkflowV2 (Patching 升級)")
    print("  - OrderWorkflowV3 (完全重寫)")
    print("  - VersionedWorkflow (版本檢測)")
    print("=" * 60)

    worker = Worker(
        client,
        task_queue="versioning-queue",
        workflows=[
            OrderWorkflowV1,
            OrderWorkflowV2,
            OrderWorkflowV3,
            VersionedWorkflow,
        ],
        activities=[
            process_payment_v1,
            process_payment_v2,
            send_notification_v1,
            send_notification_v2,
            validate_order,
        ],
    )

    print("Worker 已就緒，可以處理所有版本的工作流\n")
    await worker.run()


async def run_client():
    """演示版本控制"""
    client = await Client.connect("localhost:7233")

    print("\n" + "=" * 60)
    print("📋 工作流版本控制示例")
    print("=" * 60)

    # ========================================
    # 示例 1: 運行 V1 工作流
    # ========================================
    print("\n【示例 1】運行 V1 工作流（原始版本）")
    print("-" * 60)

    order_v1 = OrderV1(
        order_id="ORDER-V1-001",
        user_id="user123",
        amount=100.0
    )

    result = await client.execute_workflow(
        OrderWorkflowV1.run,
        order_v1,
        id=f"order-v1-{order_v1.order_id}",
        task_queue="versioning-queue",
    )

    print(f"✓ V1 結果: {result}\n")

    # ========================================
    # 示例 2: 運行 V2 工作流（使用 V1 數據格式）
    # ========================================
    print("【示例 2】運行 V2 工作流（V1 數據格式 - 向後兼容）")
    print("-" * 60)

    order_v1_data = {
        "order_id": "ORDER-V2-001",
        "user_id": "user123",
        "amount": 100.0
    }

    result = await client.execute_workflow(
        OrderWorkflowV2.run,
        order_v1_data,
        id=f"order-v2-compat-{order_v1_data['order_id']}",
        task_queue="versioning-queue",
    )

    print(f"✓ V2 結果（V1 數據）: {result}\n")

    # ========================================
    # 示例 3: 運行 V2 工作流（使用 V2 數據格式）
    # ========================================
    print("【示例 3】運行 V2 工作流（V2 數據格式 - 新功能）")
    print("-" * 60)

    order_v2_data = {
        "order_id": "ORDER-V2-002",
        "user_id": "user456",
        "amount": 200.0,
        "currency": "EUR",
        "discount": 20.0
    }

    result = await client.execute_workflow(
        OrderWorkflowV2.run,
        order_v2_data,
        id=f"order-v2-new-{order_v2_data['order_id']}",
        task_queue="versioning-queue",
    )

    print(f"✓ V2 結果（V2 數據）: {result}\n")

    # ========================================
    # 示例 4: 運行 V3 工作流（完全重寫）
    # ========================================
    print("【示例 4】運行 V3 工作流（完全重寫版本）")
    print("-" * 60)

    order_v3 = OrderV3(
        order_id="ORDER-V3-001",
        user_id="user789",
        pricing={
            "original_amount": 300.0,
            "discount": 30.0,
            "final_amount": 270.0,
            "currency": "GBP"
        }
    )

    result = await client.execute_workflow(
        OrderWorkflowV3.run,
        order_v3,
        id=f"order-v3-{order_v3.order_id}",
        task_queue="versioning-queue",
    )

    print(f"✓ V3 結果: {result}\n")

    # ========================================
    # 示例 5: 版本檢測
    # ========================================
    print("【示例 5】自動版本檢測")
    print("-" * 60)

    test_data_sets = [
        {"order_id": "TEST-1", "user_id": "user1", "amount": 100.0},
        {"order_id": "TEST-2", "user_id": "user2", "amount": 100.0, "currency": "USD"},
        {"order_id": "TEST-3", "user_id": "user3", "pricing": {"final_amount": 100.0}},
    ]

    for i, test_data in enumerate(test_data_sets):
        result = await client.execute_workflow(
            VersionedWorkflow.run,
            test_data,
            "auto",
            id=f"version-detect-{i}",
            task_queue="versioning-queue",
        )
        print(f"  數據集 {i + 1}: 檢測版本 = {result['detected_version']}")

    print("\n" + "=" * 60)
    print("版本控制最佳實踐：")
    print("-" * 60)
    print("1. 使用 Patching 進行小幅改動")
    print("2. 創建新工作流類型進行大幅重構")
    print("3. 保持向後兼容（支持舊數據格式）")
    print("4. Worker 註冊所有版本")
    print("5. 逐步遷移，不要強制停止舊工作流")
    print("6. 使用版本標記和文檔")
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
║              Temporal 工作流版本控制                           ║
╚══════════════════════════════════════════════════════════════╝

版本控制策略：
------------

1. Patching API（小幅改動）
   ✓ 使用 workflow.patched() 標記新代碼
   ✓ 新工作流執行新代碼
   ✓ 舊工作流跳過新代碼
   ✓ 保持向後兼容

2. 新工作流類型（大幅重構）
   ✓ 創建新的工作流類（如 V2, V3）
   ✓ 舊工作流繼續使用舊代碼
   ✓ 新工作流使用新代碼
   ✓ 版本隔離清晰

3. 數據格式兼容
   ✓ 使用可選參數
   ✓ 提供默認值
   ✓ 兼容性檢查
   ✓ 優雅降級

關鍵概念：
---------
- Determinism（確定性）：相同輸入產生相同輸出
- Patching：安全地添加新代碼
- Versioning：管理多個工作流版本
- Migration：逐步遷移到新版本

部署策略：
---------
1. 部署新 Worker（支持新舊版本）
2. 逐步啟動新工作流
3. 等待舊工作流完成
4. 移除舊代碼（可選）

注意事項：
---------
⚠️ 不要在運行中的工作流中刪除代碼
⚠️ 始終保持向後兼容
⚠️ 使用 Patching 而不是條件分支
⚠️ 測試所有版本的工作流

使用方法：
---------
1. 啟動 Worker: python 09_版本控制.py
2. 執行示例: python 09_版本控制.py client
    """)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 程序已停止")
