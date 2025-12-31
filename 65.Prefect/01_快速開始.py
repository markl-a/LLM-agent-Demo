#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prefect 快速開始示例
====================

這個示例展示了 Prefect 的基本使用方法，包括：
1. 定義 Task（任務）
2. 定義 Flow（流程）
3. 執行工作流
4. 查看執行結果

Prefect 的核心理念是將普通的 Python 函數轉換為可觀測、可重試的工作流。
"""

from prefect import task, flow, get_run_logger
from typing import List
import time
from datetime import datetime


# ============================================================================
# Task 定義
# ============================================================================

@task(name="問候任務")
def say_hello(name: str) -> str:
    """
    最簡單的 Task 示例

    使用 @task 裝飾器將普通函數轉換為 Prefect 任務。
    任務會自動獲得日誌、重試、超時等功能。

    Args:
        name: 要問候的名字

    Returns:
        問候語
    """
    logger = get_run_logger()
    logger.info(f"正在問候 {name}")

    greeting = f"你好，{name}！歡迎使用 Prefect！"
    return greeting


@task(name="獲取當前時間")
def get_current_time() -> str:
    """
    獲取當前時間的任務

    Returns:
        格式化的當前時間
    """
    logger = get_run_logger()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"當前時間：{current_time}")
    return current_time


@task(name="處理數據")
def process_data(data: List[int]) -> dict:
    """
    數據處理任務

    Args:
        data: 要處理的數字列表

    Returns:
        包含統計信息的字典
    """
    logger = get_run_logger()
    logger.info(f"正在處理 {len(data)} 個數據點")

    # 模擬數據處理
    time.sleep(1)

    result = {
        "count": len(data),
        "sum": sum(data),
        "average": sum(data) / len(data) if data else 0,
        "max": max(data) if data else None,
        "min": min(data) if data else None
    }

    logger.info(f"處理完成：{result}")
    return result


@task(name="保存結果")
def save_result(data: dict, filename: str = "result.txt") -> str:
    """
    保存結果任務（模擬）

    Args:
        data: 要保存的數據
        filename: 文件名

    Returns:
        保存狀態消息
    """
    logger = get_run_logger()
    logger.info(f"正在保存結果到 {filename}")

    # 實際應用中，這裡會保存到文件或數據庫
    # 這裡只是模擬
    message = f"✓ 結果已保存到 {filename}"
    logger.info(message)

    return message


# ============================================================================
# Flow 定義
# ============================================================================

@flow(name="簡單工作流", description="最基本的 Prefect 工作流示例")
def simple_flow(name: str = "世界") -> str:
    """
    簡單的工作流示例

    這個工作流演示了如何組合多個任務。

    Args:
        name: 要問候的名字

    Returns:
        問候語
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("開始執行簡單工作流")
    logger.info("=" * 60)

    # 執行任務
    greeting = say_hello(name)
    current_time = get_current_time()

    logger.info("工作流執行完成！")
    return greeting


@flow(name="數據處理工作流", description="包含多個步驟的數據處理流程")
def data_processing_flow(numbers: List[int] = None) -> dict:
    """
    數據處理工作流

    演示了任務之間的數據傳遞和依賴關係。

    Args:
        numbers: 要處理的數字列表

    Returns:
        處理結果
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("開始執行數據處理工作流")
    logger.info("=" * 60)

    # 默認數據
    if numbers is None:
        numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # 步驟 1: 獲取時間戳
    timestamp = get_current_time()

    # 步驟 2: 處理數據
    result = process_data(numbers)

    # 步驟 3: 保存結果
    save_status = save_result(result, f"result_{timestamp}.txt")

    logger.info("數據處理工作流執行完成！")
    return result


@flow(name="嵌套工作流示例")
def nested_flow_example():
    """
    嵌套工作流示例

    Prefect 支持在一個 Flow 中調用另一個 Flow（子流程）。
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("開始執行嵌套工作流")
    logger.info("=" * 60)

    # 調用第一個子流程
    logger.info("\n--- 執行子流程 1 ---")
    simple_flow("Alice")

    # 調用第二個子流程
    logger.info("\n--- 執行子流程 2 ---")
    data_processing_flow([10, 20, 30, 40, 50])

    logger.info("\n嵌套工作流執行完成！")


# ============================================================================
# 錯誤處理示例
# ============================================================================

@task(name="可能失敗的任務", retries=2, retry_delay_seconds=1)
def might_fail_task(should_fail: bool = False) -> str:
    """
    演示錯誤處理的任務

    Args:
        should_fail: 是否應該失敗

    Returns:
        成功消息

    Raises:
        ValueError: 當 should_fail 為 True 時
    """
    logger = get_run_logger()

    if should_fail:
        logger.warning("任務將失敗（演示重試機制）")
        raise ValueError("這是一個演示錯誤！")

    logger.info("任務執行成功")
    return "成功！"


@flow(name="錯誤處理示例")
def error_handling_flow():
    """
    演示錯誤處理的工作流
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("開始執行錯誤處理示例")
    logger.info("=" * 60)

    try:
        # 這個會成功
        logger.info("\n--- 執行正常任務 ---")
        might_fail_task(should_fail=False)

        # 這個會失敗並重試
        logger.info("\n--- 執行會失敗的任務（將會重試） ---")
        might_fail_task(should_fail=True)

    except Exception as e:
        logger.error(f"捕獲到錯誤：{e}")
        logger.info("工作流繼續執行...")

    logger.info("\n錯誤處理示例完成！")


# ============================================================================
# 運行示例
# ============================================================================

def main():
    """
    主函數 - 運行所有示例
    """
    print("\n" + "=" * 70)
    print("Prefect 快速開始示例")
    print("=" * 70)

    # 示例 1: 簡單工作流
    print("\n【示例 1】簡單工作流")
    print("-" * 70)
    result1 = simple_flow("Prefect 用戶")
    print(f"\n結果：{result1}")

    # 示例 2: 數據處理工作流
    print("\n【示例 2】數據處理工作流")
    print("-" * 70)
    result2 = data_processing_flow([5, 10, 15, 20, 25])
    print(f"\n結果：{result2}")

    # 示例 3: 嵌套工作流
    print("\n【示例 3】嵌套工作流")
    print("-" * 70)
    nested_flow_example()

    # 示例 4: 錯誤處理
    print("\n【示例 4】錯誤處理")
    print("-" * 70)
    error_handling_flow()

    # 使用說明
    print("\n" + "=" * 70)
    print("使用說明")
    print("=" * 70)
    print("""
1. 基本概念：
   - @task: 將函數轉換為可重試、可監控的任務
   - @flow: 將函數轉換為工作流，可以包含多個任務

2. 查看執行結果：
   - 啟動 Prefect UI: prefect server start
   - 訪問: http://localhost:4200
   - 在 UI 中可以看到所有執行的工作流和詳細日誌

3. 關鍵特性：
   - 自動日誌記錄
   - 任務依賴管理
   - 錯誤重試
   - 執行狀態追蹤

4. 下一步：
   - 查看 02_任務定義.py 了解更多 Task 配置選項
   - 查看 03_參數傳遞.py 了解參數處理
   - 查看其他示例文件學習更多功能
    """)

    print("=" * 70)
    print("提示：運行 'prefect server start' 啟動 UI 界面查看詳細信息")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
