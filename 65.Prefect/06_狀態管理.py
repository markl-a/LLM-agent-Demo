#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prefect 狀態管理
=================

這個示例展示了 Prefect 的狀態管理系統，包括：
1. 任務和工作流狀態
2. 狀態轉換
3. 自定義狀態處理
4. 狀態鉤子（Hooks）
5. 失敗處理
6. 狀態持久化
"""

from prefect import task, flow, get_run_logger
from prefect.states import (
    State,
    Completed,
    Failed,
    Pending,
    Running,
    Cancelled,
    Crashed,
    Paused
)
from prefect.exceptions import PrefectException
import time
import random
from datetime import datetime
from typing import Optional


# ============================================================================
# 基本狀態理解
# ============================================================================

@task
def basic_task(name: str) -> str:
    """
    基本任務，用於理解狀態

    Args:
        name: 任務名稱

    Returns:
        結果
    """
    logger = get_run_logger()
    logger.info(f"執行任務：{name}")

    # 任務執行時的狀態：Running
    # 任務完成後的狀態：Completed
    return f"任務 {name} 完成"


@flow(name="基本狀態示例")
def basic_state_flow():
    """
    演示基本的狀態轉換

    狀態轉換流程：
    Pending -> Running -> Completed (成功)
    Pending -> Running -> Failed (失敗)
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("基本狀態流程")
    logger.info("=" * 60)

    # 初始狀態：Pending
    logger.info("工作流狀態：Pending -> Running")

    # 執行任務
    result = basic_task("示例任務")

    # 完成狀態：Completed
    logger.info(f"工作流狀態：Running -> Completed")
    logger.info(f"結果：{result}")

    return result


# ============================================================================
# 失敗狀態處理
# ============================================================================

@task(retries=2)
def task_that_fails(should_fail: bool = True) -> str:
    """
    會失敗的任務

    Args:
        should_fail: 是否應該失敗

    Returns:
        結果

    Raises:
        ValueError: 當 should_fail 為 True 時
    """
    logger = get_run_logger()

    if should_fail:
        logger.error("任務失敗")
        raise ValueError("這是一個測試錯誤")

    logger.info("任務成功")
    return "成功"


@flow(name="失敗狀態處理")
def failure_handling_flow():
    """
    演示失敗狀態的處理

    狀態：Running -> Failed
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("失敗狀態處理")
    logger.info("=" * 60)

    try:
        # 這個任務會失敗並重試
        result = task_that_fails(should_fail=True)
        logger.info(f"結果：{result}")
    except Exception as e:
        logger.error(f"任務失敗：{e}")
        logger.info("工作流狀態：Running -> Failed")
        # 即使任務失敗，工作流可以繼續執行
        logger.info("工作流繼續執行其他邏輯...")

    return "工作流完成（部分失敗）"


# ============================================================================
# 狀態鉤子（Hooks）
# ============================================================================

def on_completion_hook(task, task_run, state):
    """
    任務完成時的鉤子函數

    Args:
        task: 任務對象
        task_run: 任務運行對象
        state: 狀態對象
    """
    logger = get_run_logger()
    logger.info(f"🎉 任務完成鉤子觸發：{task.name}")
    logger.info(f"   狀態：{state.type}")
    logger.info(f"   時間：{datetime.now()}")


def on_failure_hook(task, task_run, state):
    """
    任務失敗時的鉤子函數

    Args:
        task: 任務對象
        task_run: 任務運行對象
        state: 狀態對象
    """
    logger = get_run_logger()
    logger.error(f"❌ 任務失敗鉤子觸發：{task.name}")
    logger.error(f"   狀態：{state.type}")
    logger.error(f"   錯誤：{state.message}")
    logger.info("   發送告警郵件...")  # 實際應用中可以發送通知


@task(
    on_completion=[on_completion_hook],
    on_failure=[on_failure_hook]
)
def task_with_hooks(success: bool = True) -> str:
    """
    帶鉤子的任務

    Args:
        success: 是否成功

    Returns:
        結果

    Raises:
        RuntimeError: 當 success 為 False 時
    """
    logger = get_run_logger()
    logger.info("執行帶鉤子的任務")

    if not success:
        raise RuntimeError("任務失敗")

    return "任務成功"


@flow(name="狀態鉤子示例")
def state_hooks_flow():
    """
    演示狀態鉤子的使用
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("狀態鉤子示例")
    logger.info("=" * 60)

    # 成功的任務（觸發 on_completion）
    logger.info("\n--- 成功的任務 ---")
    try:
        result1 = task_with_hooks(success=True)
        logger.info(f"結果：{result1}")
    except Exception as e:
        logger.error(f"錯誤：{e}")

    # 失敗的任務（觸發 on_failure）
    logger.info("\n--- 失敗的任務 ---")
    try:
        result2 = task_with_hooks(success=False)
        logger.info(f"結果：{result2}")
    except Exception as e:
        logger.error(f"錯誤：{e}")


# ============================================================================
# 條件狀態轉換
# ============================================================================

@task
def check_data_quality(data: list) -> bool:
    """
    檢查數據質量

    Args:
        data: 要檢查的數據

    Returns:
        數據是否合格
    """
    logger = get_run_logger()
    logger.info(f"檢查數據質量：{len(data)} 項")

    # 簡單的質量檢查
    is_valid = len(data) > 0 and all(isinstance(x, (int, float)) for x in data)

    if is_valid:
        logger.info("✓ 數據質量合格")
    else:
        logger.warning("✗ 數據質量不合格")

    return is_valid


@task
def process_valid_data(data: list) -> dict:
    """
    處理合格的數據

    Args:
        data: 數據

    Returns:
        處理結果
    """
    logger = get_run_logger()
    logger.info("處理合格數據")

    result = {
        "status": "processed",
        "count": len(data),
        "sum": sum(data)
    }

    return result


@task
def handle_invalid_data(data: list) -> dict:
    """
    處理不合格的數據

    Args:
        data: 數據

    Returns:
        處理結果
    """
    logger = get_run_logger()
    logger.warning("處理不合格數據")

    result = {
        "status": "rejected",
        "reason": "質量檢查失敗",
        "data": data
    }

    return result


@flow(name="條件狀態轉換")
def conditional_state_flow(data: list):
    """
    根據條件選擇不同的狀態路徑

    Args:
        data: 輸入數據
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("條件狀態轉換")
    logger.info("=" * 60)

    # 檢查數據質量
    is_valid = check_data_quality(data)

    # 根據檢查結果選擇不同的處理路徑
    if is_valid:
        logger.info("→ 數據合格，執行正常處理流程")
        result = process_valid_data(data)
    else:
        logger.info("→ 數據不合格，執行異常處理流程")
        result = handle_invalid_data(data)

    logger.info(f"最終結果：{result}")
    return result


# ============================================================================
# 重試狀態管理
# ============================================================================

# 用於追蹤重試次數的全局變量
retry_attempts = {}


@task(retries=3, retry_delay_seconds=1)
def task_with_retries(task_id: str, fail_count: int = 2) -> str:
    """
    帶重試的任務

    Args:
        task_id: 任務 ID
        fail_count: 前幾次會失敗

    Returns:
        結果

    Raises:
        RuntimeError: 當重試次數未達到要求時
    """
    logger = get_run_logger()

    # 初始化或增加重試計數
    if task_id not in retry_attempts:
        retry_attempts[task_id] = 0
    retry_attempts[task_id] += 1

    attempt = retry_attempts[task_id]
    logger.info(f"任務 {task_id} 第 {attempt} 次嘗試")

    if attempt <= fail_count:
        logger.warning(f"任務 {task_id} 失敗（{attempt}/{fail_count}）")
        raise RuntimeError(f"任務暫時失敗（嘗試 {attempt}）")

    logger.info(f"任務 {task_id} 成功")
    retry_attempts[task_id] = 0  # 重置計數
    return f"任務 {task_id} 在第 {attempt} 次嘗試後成功"


@flow(name="重試狀態管理")
def retry_state_flow():
    """
    演示重試狀態的管理

    狀態轉換：
    Running -> Failed -> Pending (重試) -> Running -> ...
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("重試狀態管理")
    logger.info("=" * 60)

    try:
        result = task_with_retries("task-1", fail_count=2)
        logger.info(f"結果：{result}")
    except Exception as e:
        logger.error(f"任務最終失敗：{e}")

    return "重試演示完成"


# ============================================================================
# 狀態持久化和查詢
# ============================================================================

@task
def long_running_task(duration: int = 3) -> dict:
    """
    長時間運行的任務

    Args:
        duration: 運行時長（秒）

    Returns:
        結果
    """
    logger = get_run_logger()
    logger.info(f"開始長時間任務（{duration} 秒）")

    start_time = time.time()

    # 模擬長時間運行
    for i in range(duration):
        time.sleep(1)
        progress = (i + 1) / duration * 100
        logger.info(f"進度：{progress:.0f}%")

    elapsed = time.time() - start_time

    result = {
        "duration": duration,
        "elapsed": elapsed,
        "status": "completed"
    }

    logger.info(f"任務完成：{result}")
    return result


@flow(name="狀態持久化示例")
def state_persistence_flow():
    """
    演示狀態持久化

    Prefect 會自動持久化所有狀態信息，包括：
    - 任務開始時間
    - 任務結束時間
    - 執行日誌
    - 結果數據
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("狀態持久化示例")
    logger.info("=" * 60)

    # 執行任務
    result = long_running_task(duration=3)

    logger.info("""
    狀態信息已自動持久化到 Prefect 服務器。
    你可以通過以下方式查詢：
    1. Prefect UI: http://localhost:4200
    2. CLI 命令: prefect flow-run ls
    3. API 查詢
    """)

    return result


# ============================================================================
# 自定義狀態邏輯
# ============================================================================

@task
def task_with_custom_state() -> str:
    """
    使用自定義狀態邏輯的任務

    Returns:
        結果
    """
    logger = get_run_logger()
    logger.info("執行自定義狀態任務")

    # 模擬檢查某個條件
    condition = random.choice([True, False])

    if not condition:
        logger.warning("條件不滿足，返回自定義狀態")
        # 在實際應用中，可以返回自定義狀態
        # return Paused(message="等待外部條件滿足")

    logger.info("任務正常完成")
    return "完成"


@flow(name="自定義狀態示例")
def custom_state_flow():
    """
    演示自定義狀態的使用
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("自定義狀態示例")
    logger.info("=" * 60)

    result = task_with_custom_state()
    logger.info(f"結果：{result}")

    logger.info("""
    自定義狀態可以用於：
    - 實現審批流程（Paused 狀態）
    - 條件等待
    - 複雜的狀態機邏輯
    """)


# ============================================================================
# 狀態監控
# ============================================================================

@task
def monitored_task(task_id: int) -> dict:
    """
    被監控的任務

    Args:
        task_id: 任務 ID

    Returns:
        結果
    """
    logger = get_run_logger()
    logger.info(f"執行任務 {task_id}")

    start_time = time.time()

    # 模擬工作
    time.sleep(random.uniform(0.5, 2.0))

    elapsed = time.time() - start_time

    result = {
        "task_id": task_id,
        "elapsed": elapsed,
        "status": "completed"
    }

    return result


@flow(name="狀態監控示例")
def state_monitoring_flow(task_count: int = 5):
    """
    演示狀態監控

    Args:
        task_count: 任務數量
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("狀態監控示例")
    logger.info("=" * 60)

    logger.info(f"執行 {task_count} 個任務並監控狀態")

    results = []
    for i in range(task_count):
        result = monitored_task(i)
        results.append(result)
        logger.info(f"任務 {i} 完成：{result['elapsed']:.2f}s")

    # 統計
    total_time = sum(r['elapsed'] for r in results)
    avg_time = total_time / len(results)

    logger.info(f"\n統計信息：")
    logger.info(f"  - 總任務數：{len(results)}")
    logger.info(f"  - 總耗時：{total_time:.2f}s")
    logger.info(f"  - 平均耗時：{avg_time:.2f}s")

    return results


# ============================================================================
# 運行示例
# ============================================================================

def main():
    """
    主函數 - 運行所有示例
    """
    print("\n" + "=" * 70)
    print("Prefect 狀態管理")
    print("=" * 70)

    # 示例 1: 基本狀態
    print("\n【示例 1】基本狀態流程")
    print("-" * 70)
    basic_state_flow()

    # 示例 2: 失敗處理
    print("\n【示例 2】失敗狀態處理")
    print("-" * 70)
    failure_handling_flow()

    # 示例 3: 狀態鉤子
    print("\n【示例 3】狀態鉤子")
    print("-" * 70)
    state_hooks_flow()

    # 示例 4: 條件狀態
    print("\n【示例 4】條件狀態轉換（合格數據）")
    print("-" * 70)
    conditional_state_flow([1, 2, 3, 4, 5])

    print("\n【示例 5】條件狀態轉換（不合格數據）")
    print("-" * 70)
    conditional_state_flow([])

    # 示例 5: 重試狀態
    print("\n【示例 6】重試狀態管理")
    print("-" * 70)
    retry_state_flow()

    # 示例 6: 狀態持久化
    print("\n【示例 7】狀態持久化")
    print("-" * 70)
    state_persistence_flow()

    # 示例 7: 自定義狀態
    print("\n【示例 8】自定義狀態")
    print("-" * 70)
    custom_state_flow()

    # 示例 8: 狀態監控
    print("\n【示例 9】狀態監控")
    print("-" * 70)
    state_monitoring_flow(task_count=5)

    # 使用說明
    print("\n" + "=" * 70)
    print("狀態管理總結")
    print("=" * 70)
    print("""
1. Prefect 狀態類型：
   - Pending: 等待執行
   - Running: 正在執行
   - Completed: 成功完成
   - Failed: 執行失敗
   - Cancelled: 已取消
   - Crashed: 意外崩潰
   - Paused: 已暫停

2. 狀態轉換：
   Pending -> Running -> Completed (正常流程)
   Pending -> Running -> Failed (失敗)
   Running -> Paused (暫停，等待恢復)

3. 狀態鉤子：
   - on_completion: 任務完成時觸發
   - on_failure: 任務失敗時觸發
   - 可用於通知、清理、日誌等

4. 重試機制：
   - 自動重試失敗的任務
   - 可配置重試次數和延遲
   - 支持指數退避

5. 狀態持久化：
   - Prefect 自動持久化所有狀態
   - 可通過 UI 或 API 查詢
   - 包含完整的執行歷史

6. 最佳實踐：
   - 使用鉤子函數處理特殊事件
   - 為關鍵任務設置重試
   - 監控任務狀態和性能
   - 使用條件邏輯處理不同場景

7. 查看狀態：
   - Prefect UI: http://localhost:4200
   - CLI: prefect flow-run ls
   - API 查詢

8. 下一步：
   - 查看 07_緩存機制.py 了解結果緩存
   - 查看 08_通知告警.py 了解通知配置
    """)

    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
