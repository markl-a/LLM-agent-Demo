"""
Temporal 錯誤處理 - 重試和補償

這個示例展示了：
1. 自動重試策略
2. 超時控制（多種類型）
3. 錯誤類型處理
4. 自定義重試策略
5. 補償邏輯（Saga）
6. 錯誤傳播
7. 非重試錯誤
8. 死信隊列模式
"""

import asyncio
import random
from dataclasses import dataclass
from datetime import timedelta
from typing import List, Optional

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.exceptions import (
    ActivityError,
    ApplicationError,
    TimeoutError,
)
from temporalio.worker import Worker


# ============================================================
# 數據模型
# ============================================================

@dataclass
class Transaction:
    """交易數據"""
    transaction_id: str
    amount: float
    account_from: str
    account_to: str


@dataclass
class CompensationLog:
    """補償日誌"""
    step: str
    data: dict
    compensated: bool = False


# ============================================================
# Activity 定義 - 各種錯誤場景
# ============================================================

@activity.defn
async def flaky_network_call(url: str, fail_rate: float = 0.5) -> dict:
    """
    不穩定的網絡調用

    模擬網絡請求，可能失敗
    這種情況適合使用自動重試
    """
    info = activity.info()
    attempt = info.attempt

    print(f"🌐 網絡調用 {url} (嘗試 #{attempt})")

    # 模擬網絡不穩定
    if random.random() < fail_rate and attempt < 3:
        print(f"  ✗ 網絡錯誤（嘗試 #{attempt}）")
        # 可重試錯誤
        raise ApplicationError(
            f"網絡連接失敗",
            non_retryable=False  # 允許重試
        )

    print(f"  ✓ 成功（嘗試 #{attempt}）")
    return {"status": "success", "url": url, "attempt": attempt}


@activity.defn
async def validate_input(data: dict) -> bool:
    """
    驗證輸入

    驗證失敗不應該重試（業務邏輯錯誤）
    """
    print(f"✅ 驗證輸入: {data}")

    # 檢查必需字段
    if "user_id" not in data:
        # 不可重試錯誤
        raise ApplicationError(
            "缺少必需字段: user_id",
            non_retryable=True  # 不重試
        )

    if "amount" in data and data["amount"] <= 0:
        raise ApplicationError(
            "金額必須大於 0",
            non_retryable=True
        )

    return True


@activity.defn
async def slow_operation(duration: int) -> str:
    """
    慢操作

    用於測試超時
    """
    print(f"🐌 慢操作開始（需要 {duration} 秒）")

    for i in range(duration):
        await asyncio.sleep(1)
        # 發送心跳，防止心跳超時
        activity.heartbeat(f"進度: {i + 1}/{duration}")
        print(f"  進度: {i + 1}/{duration}")

    print("  ✓ 完成")
    return f"Completed after {duration} seconds"


@activity.defn
async def database_transaction(transaction: Transaction) -> str:
    """
    數據庫事務

    模擬數據庫操作，可能因為死鎖、連接池耗盡等失敗
    """
    info = activity.info()
    attempt = info.attempt

    print(f"💾 數據庫事務: {transaction.transaction_id} (嘗試 #{attempt})")

    # 模擬瞬時數據庫錯誤（連接池、死鎖等）
    if random.random() < 0.3 and attempt < 3:
        print(f"  ✗ 數據庫瞬時錯誤（嘗試 #{attempt}）")
        raise ApplicationError("數據庫連接失敗", non_retryable=False)

    # 模擬業務錯誤（餘額不足等）
    if random.random() < 0.1:
        print(f"  ✗ 餘額不足")
        raise ApplicationError("餘額不足", non_retryable=True)

    await asyncio.sleep(0.5)
    print(f"  ✓ 事務成功")
    return f"TX-{transaction.transaction_id}"


@activity.defn
async def external_api_call(endpoint: str) -> dict:
    """
    外部 API 調用

    可能因為限流、服務不可用等失敗
    """
    info = activity.info()
    attempt = info.attempt

    print(f"🔌 API 調用: {endpoint} (嘗試 #{attempt})")

    # 模擬限流錯誤（應該使用較長的重試間隔）
    if random.random() < 0.4 and attempt == 1:
        print(f"  ✗ API 限流")
        raise ApplicationError("Rate limit exceeded", non_retryable=False)

    # 模擬服務不可用
    if random.random() < 0.2 and attempt < 2:
        print(f"  ✗ 服務不可用")
        raise ApplicationError("Service unavailable", non_retryable=False)

    await asyncio.sleep(0.3)
    print(f"  ✓ API 成功")
    return {"endpoint": endpoint, "data": "API response"}


# ============================================================
# 補償相關 Activities
# ============================================================

@activity.defn
async def deduct_balance(account: str, amount: float) -> str:
    """扣款"""
    print(f"💸 從賬戶 {account} 扣款 ${amount}")
    await asyncio.sleep(0.3)
    return f"DEDUCT-{account}"


@activity.defn
async def credit_balance(account: str, amount: float) -> str:
    """補償：退款"""
    print(f"💰 向賬戶 {account} 退款 ${amount}")
    await asyncio.sleep(0.3)
    return f"CREDIT-{account}"


@activity.defn
async def send_money(to_account: str, amount: float) -> str:
    """轉賬"""
    print(f"💳 向賬戶 {to_account} 轉賬 ${amount}")
    await asyncio.sleep(0.3)

    # 模擬轉賬可能失敗
    if random.random() < 0.3:
        raise ApplicationError("轉賬失敗", non_retryable=False)

    return f"SEND-{to_account}"


@activity.defn
async def reverse_transfer(to_account: str, amount: float) -> str:
    """補償：撤銷轉賬"""
    print(f"🔙 撤銷向賬戶 {to_account} 的轉賬 ${amount}")
    await asyncio.sleep(0.3)
    return f"REVERSE-{to_account}"


@activity.defn
async def notify_transaction(account: str, message: str) -> bool:
    """發送交易通知"""
    print(f"📧 通知 {account}: {message}")
    await asyncio.sleep(0.2)
    return True


# ============================================================
# 工作流 1: 自定義重試策略
# ============================================================

@workflow.defn
class RetryPolicyWorkflow:
    """
    演示不同的重試策略
    """

    @workflow.run
    async def run(self, scenario: str) -> dict:
        """
        測試不同的重試策略

        Args:
            scenario: 測試場景
                - 'default': 默認重試策略
                - 'aggressive': 激進重試（快速、多次）
                - 'conservative': 保守重試（慢速、少次）
                - 'exponential': 指數退避
        """

        print(f"\n🔄 重試策略測試: {scenario}")

        if scenario == "default":
            # Temporal 默認重試策略
            retry_policy = None

        elif scenario == "aggressive":
            # 激進重試：快速重試，適合瞬時錯誤
            retry_policy = RetryPolicy(
                initial_interval=timedelta(milliseconds=100),  # 100ms 開始
                maximum_interval=timedelta(seconds=1),  # 最多 1s
                maximum_attempts=10,  # 最多 10 次
                backoff_coefficient=1.5,  # 退避係數
            )

        elif scenario == "conservative":
            # 保守重試：慢速重試，適合外部服務
            retry_policy = RetryPolicy(
                initial_interval=timedelta(seconds=5),  # 5s 開始
                maximum_interval=timedelta(seconds=60),  # 最多 60s
                maximum_attempts=3,  # 最多 3 次
                backoff_coefficient=2.0,
            )

        elif scenario == "exponential":
            # 指數退避：適合 API 限流
            retry_policy = RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(minutes=5),
                maximum_attempts=5,
                backoff_coefficient=3.0,  # 快速增長
            )

        else:
            retry_policy = None

        try:
            result = await workflow.execute_activity(
                flaky_network_call,
                "https://api.example.com/data",
                0.6,  # 60% 失敗率
                start_to_close_timeout=timedelta(seconds=60),
                retry_policy=retry_policy,
            )
            return {"success": True, "result": result}

        except Exception as e:
            return {"success": False, "error": str(e)}


# ============================================================
# 工作流 2: 超時控制
# ============================================================

@workflow.defn
class TimeoutWorkflow:
    """
    演示不同類型的超時
    """

    @workflow.run
    async def run(self, timeout_type: str) -> dict:
        """
        測試不同的超時類型

        Temporal 支持的超時類型：
        - start_to_close_timeout: 從開始到完成的總時間
        - schedule_to_close_timeout: 從調度到完成的總時間
        - schedule_to_start_timeout: 從調度到開始的最大等待時間
        - heartbeat_timeout: 心跳超時
        """

        print(f"\n⏰ 超時測試: {timeout_type}")

        try:
            if timeout_type == "start_to_close":
                # 執行超時：Activity 總執行時間
                await workflow.execute_activity(
                    slow_operation,
                    10,  # 需要 10 秒
                    start_to_close_timeout=timedelta(seconds=5),  # 但只允許 5 秒
                )

            elif timeout_type == "heartbeat":
                # 心跳超時：Activity 必須定期發送心跳
                await workflow.execute_activity(
                    slow_operation,
                    10,
                    start_to_close_timeout=timedelta(seconds=30),
                    heartbeat_timeout=timedelta(seconds=2),  # 2 秒內必須有心跳
                )

            return {"success": True}

        except TimeoutError as e:
            return {"success": False, "error": "超時", "type": timeout_type}
        except Exception as e:
            return {"success": False, "error": str(e)}


# ============================================================
# 工作流 3: Saga 補償模式
# ============================================================

@workflow.defn
class SagaCompensationWorkflow:
    """
    Saga 補償模式

    實現分佈式事務：
    - 正向操作序列
    - 失敗時執行補償操作序列
    """

    @workflow.run
    async def run(self, transaction: Transaction) -> dict:
        """
        執行轉賬事務，失敗時自動補償
        """

        print(f"\n💰 Saga 轉賬: {transaction.transaction_id}")

        # 補償日誌
        compensations: List[CompensationLog] = []

        try:
            # ===== 步驟 1: 扣款 =====
            deduct_id = await workflow.execute_activity(
                deduct_balance,
                transaction.account_from,
                transaction.amount,
                start_to_close_timeout=timedelta(seconds=10),
            )
            compensations.append(CompensationLog(
                step="deduct",
                data={
                    "account": transaction.account_from,
                    "amount": transaction.amount
                }
            ))
            print(f"  ✓ 步驟 1: 扣款成功 ({deduct_id})")

            # ===== 步驟 2: 轉賬 =====
            send_id = await workflow.execute_activity(
                send_money,
                transaction.account_to,
                transaction.amount,
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(
                    maximum_attempts=3,
                    initial_interval=timedelta(seconds=1),
                ),
            )
            compensations.append(CompensationLog(
                step="send",
                data={
                    "account": transaction.account_to,
                    "amount": transaction.amount
                }
            ))
            print(f"  ✓ 步驟 2: 轉賬成功 ({send_id})")

            # ===== 步驟 3: 通知 =====
            await workflow.execute_activity(
                notify_transaction,
                transaction.account_from,
                f"成功轉賬 ${transaction.amount} 到 {transaction.account_to}",
                start_to_close_timeout=timedelta(seconds=10),
            )
            print(f"  ✓ 步驟 3: 通知已發送")

            return {
                "success": True,
                "transaction_id": transaction.transaction_id,
                "steps_completed": 3
            }

        except Exception as e:
            print(f"\n  ❌ 錯誤: {e}")
            print(f"  🔙 開始補償操作...")

            # 執行補償（逆序）
            compensation_results = []
            for comp_log in reversed(compensations):
                try:
                    if comp_log.step == "deduct":
                        # 補償：退款
                        await workflow.execute_activity(
                            credit_balance,
                            comp_log.data["account"],
                            comp_log.data["amount"],
                            start_to_close_timeout=timedelta(seconds=10),
                        )
                        comp_log.compensated = True
                        print(f"    ✓ 補償: 已退款到 {comp_log.data['account']}")

                    elif comp_log.step == "send":
                        # 補償：撤銷轉賬
                        await workflow.execute_activity(
                            reverse_transfer,
                            comp_log.data["account"],
                            comp_log.data["amount"],
                            start_to_close_timeout=timedelta(seconds=10),
                        )
                        comp_log.compensated = True
                        print(f"    ✓ 補償: 已撤銷轉賬")

                    compensation_results.append({
                        "step": comp_log.step,
                        "compensated": True
                    })

                except Exception as comp_error:
                    print(f"    ✗ 補償失敗: {comp_error}")
                    compensation_results.append({
                        "step": comp_log.step,
                        "compensated": False,
                        "error": str(comp_error)
                    })

            return {
                "success": False,
                "error": str(e),
                "compensations": compensation_results,
                "fully_compensated": all(c.compensated for c in compensations)
            }


# ============================================================
# 工作流 4: 錯誤類型處理
# ============================================================

@workflow.defn
class ErrorTypeWorkflow:
    """
    演示如何處理不同類型的錯誤
    """

    @workflow.run
    async def run(self, error_scenario: str) -> dict:
        """
        測試不同的錯誤場景

        Args:
            error_scenario:
                - 'retryable': 可重試錯誤
                - 'non_retryable': 不可重試錯誤（業務錯誤）
                - 'timeout': 超時錯誤
        """

        print(f"\n🚨 錯誤處理測試: {error_scenario}")

        try:
            if error_scenario == "retryable":
                # 可重試錯誤：網絡問題
                result = await workflow.execute_activity(
                    flaky_network_call,
                    "https://api.example.com/endpoint",
                    0.7,  # 70% 失敗率
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=RetryPolicy(maximum_attempts=5),
                )
                return {"success": True, "result": result}

            elif error_scenario == "non_retryable":
                # 不可重試錯誤：業務邏輯錯誤
                await workflow.execute_activity(
                    validate_input,
                    {"amount": -100},  # 無效輸入
                    start_to_close_timeout=timedelta(seconds=10),
                )
                return {"success": True}

            elif error_scenario == "timeout":
                # 超時錯誤
                await workflow.execute_activity(
                    slow_operation,
                    20,  # 需要 20 秒
                    start_to_close_timeout=timedelta(seconds=5),  # 只允許 5 秒
                )
                return {"success": True}

        except ApplicationError as e:
            # 業務錯誤
            return {
                "success": False,
                "error_type": "ApplicationError",
                "message": str(e),
                "retryable": not e.non_retryable
            }

        except TimeoutError as e:
            # 超時錯誤
            return {
                "success": False,
                "error_type": "TimeoutError",
                "message": "Activity 超時"
            }

        except ActivityError as e:
            # Activity 執行錯誤
            return {
                "success": False,
                "error_type": "ActivityError",
                "message": str(e)
            }

        except Exception as e:
            # 其他錯誤
            return {
                "success": False,
                "error_type": type(e).__name__,
                "message": str(e)
            }


# ============================================================
# Worker 和 Client
# ============================================================

async def run_worker():
    """啟動 Worker"""
    client = await Client.connect("localhost:7233")

    print("=" * 60)
    print("🚀 錯誤處理 Worker 啟動中...")
    print("=" * 60)

    worker = Worker(
        client,
        task_queue="error-handling-queue",
        workflows=[
            RetryPolicyWorkflow,
            TimeoutWorkflow,
            SagaCompensationWorkflow,
            ErrorTypeWorkflow,
        ],
        activities=[
            flaky_network_call,
            validate_input,
            slow_operation,
            database_transaction,
            external_api_call,
            deduct_balance,
            credit_balance,
            send_money,
            reverse_transfer,
            notify_transaction,
        ],
    )

    await worker.run()


async def run_client():
    """執行示例工作流"""
    client = await Client.connect("localhost:7233")

    print("\n" + "=" * 60)
    print("📋 錯誤處理示例演示")
    print("=" * 60)

    # 示例 1: 激進重試策略
    print("\n【示例 1】激進重試策略")
    print("-" * 60)
    result = await client.execute_workflow(
        RetryPolicyWorkflow.run,
        "aggressive",
        id="retry-aggressive-1",
        task_queue="error-handling-queue",
    )
    print(f"結果: {result}\n")

    # 示例 2: Saga 補償（失敗）
    print("【示例 2】Saga 補償模式")
    print("-" * 60)
    transaction = Transaction(
        transaction_id="TX-001",
        amount=100.0,
        account_from="ACC-123",
        account_to="ACC-456"
    )
    result = await client.execute_workflow(
        SagaCompensationWorkflow.run,
        transaction,
        id="saga-comp-1",
        task_queue="error-handling-queue",
    )
    print(f"結果: {result}\n")

    # 示例 3: 不可重試錯誤
    print("【示例 3】不可重試錯誤（業務錯誤）")
    print("-" * 60)
    result = await client.execute_workflow(
        ErrorTypeWorkflow.run,
        "non_retryable",
        id="error-type-1",
        task_queue="error-handling-queue",
    )
    print(f"結果: {result}\n")

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
║              Temporal 錯誤處理與重試機制                       ║
╚══════════════════════════════════════════════════════════════╝

錯誤處理策略：
------------
1. 自動重試 - 網絡錯誤、瞬時故障
2. 超時控制 - 防止無限等待
3. Saga 補償 - 分佈式事務回滾
4. 錯誤分類 - 可重試 vs 不可重試

使用方法：
---------
1. 啟動 Worker: python 04_錯誤處理.py
2. 執行示例: python 04_錯誤處理.py client
    """)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 程序已停止")
