#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prefect 任務定義詳解
====================

這個示例深入探討 Task 裝飾器的各種配置選項，包括：
1. 重試機制
2. 超時設置
3. 標籤和描述
4. 任務優先級
5. 結果持久化
6. 自定義任務配置
"""

from prefect import task, flow, get_run_logger
from prefect.tasks import task_input_hash
from datetime import timedelta
import time
import random


# ============================================================================
# 基本任務配置
# ============================================================================

@task(
    name="基本任務",
    description="這是一個基本任務示例",
    tags=["示例", "基礎"]
)
def basic_task(message: str) -> str:
    """
    最基本的任務配置

    Args:
        message: 要處理的消息

    Returns:
        處理後的消息
    """
    logger = get_run_logger()
    logger.info(f"處理消息：{message}")
    return f"已處理：{message}"


# ============================================================================
# 重試機制
# ============================================================================

@task(
    name="有重試的任務",
    retries=3,  # 最多重試 3 次
    retry_delay_seconds=2  # 每次重試間隔 2 秒
)
def task_with_retries(fail_count: int = 0) -> str:
    """
    演示重試機制的任務

    Args:
        fail_count: 前幾次調用會失敗

    Returns:
        成功消息
    """
    logger = get_run_logger()

    # 模擬不穩定的操作
    if not hasattr(task_with_retries, 'attempt'):
        task_with_retries.attempt = 0

    task_with_retries.attempt += 1
    logger.info(f"第 {task_with_retries.attempt} 次嘗試")

    if task_with_retries.attempt <= fail_count:
        logger.warning(f"模擬失敗（{task_with_retries.attempt}/{fail_count}）")
        raise ValueError("臨時錯誤，稍後會成功")

    logger.info("任務成功執行！")
    task_with_retries.attempt = 0  # 重置計數器
    return "成功！"


@task(
    name="指數退避重試",
    retries=3,
    retry_delay_seconds=[1, 2, 4]  # 指數退避：1秒、2秒、4秒
)
def task_with_exponential_backoff() -> str:
    """
    使用指數退避策略的任務

    重試延遲會逐漸增加，適合處理外部服務臨時不可用的情況。
    """
    logger = get_run_logger()

    # 模擬隨機失敗
    if random.random() < 0.7:  # 70% 概率失敗
        logger.warning("服務暫時不可用，將會重試")
        raise ConnectionError("無法連接到服務")

    logger.info("成功連接到服務")
    return "數據已獲取"


# ============================================================================
# 超時設置
# ============================================================================

@task(
    name="有超時限制的任務",
    timeout_seconds=5  # 5 秒超時
)
def task_with_timeout(sleep_time: float = 2) -> str:
    """
    演示超時設置的任務

    Args:
        sleep_time: 睡眠時間（秒）

    Returns:
        完成消息
    """
    logger = get_run_logger()
    logger.info(f"任務將運行 {sleep_time} 秒")

    time.sleep(sleep_time)

    logger.info("任務完成")
    return f"運行了 {sleep_time} 秒"


# ============================================================================
# 緩存配置
# ============================================================================

@task(
    name="有緩存的任務",
    cache_key_fn=task_input_hash,  # 基於輸入參數的緩存
    cache_expiration=timedelta(minutes=5)  # 緩存 5 分鐘
)
def cached_task(x: int, y: int) -> int:
    """
    使用緩存的任務

    相同的輸入在緩存期內會直接返回緩存結果，不會重新執行。

    Args:
        x: 第一個數字
        y: 第二個數字

    Returns:
        計算結果
    """
    logger = get_run_logger()
    logger.info(f"執行昂貴的計算：{x} + {y}")

    # 模擬耗時的計算
    time.sleep(2)

    result = x + y
    logger.info(f"計算完成：{result}")
    return result


# ============================================================================
# 持久化結果
# ============================================================================

@task(
    name="持久化結果的任務",
    persist_result=True  # 持久化結果到存儲
)
def task_with_persisted_result(data: list) -> dict:
    """
    結果會被持久化存儲的任務

    當任務完成後，結果會被保存。如果工作流失敗，
    已完成的任務結果可以被重用，無需重新執行。

    Args:
        data: 要處理的數據

    Returns:
        處理結果
    """
    logger = get_run_logger()
    logger.info(f"處理 {len(data)} 個數據項")

    # 模擬耗時的數據處理
    time.sleep(1)

    result = {
        "count": len(data),
        "sum": sum(data),
        "mean": sum(data) / len(data) if data else 0
    }

    logger.info(f"處理完成：{result}")
    return result


# ============================================================================
# 自定義標籤和元數據
# ============================================================================

@task(
    name="數據提取任務",
    description="從數據源提取數據",
    tags=["ETL", "提取", "數據庫"],
    version="1.0.0"
)
def extract_data(source: str) -> list:
    """
    帶有豐富元數據的任務

    標籤可以用於：
    - 任務分類和搜索
    - 觸發特定的處理邏輯
    - 生成報告和統計

    Args:
        source: 數據源名稱

    Returns:
        提取的數據
    """
    logger = get_run_logger()
    logger.info(f"從 {source} 提取數據")

    # 模擬數據提取
    data = [1, 2, 3, 4, 5]
    logger.info(f"成功提取 {len(data)} 條記錄")

    return data


@task(
    name="數據轉換任務",
    description="轉換數據格式",
    tags=["ETL", "轉換"],
    version="1.0.0"
)
def transform_data(data: list) -> list:
    """
    數據轉換任務

    Args:
        data: 原始數據

    Returns:
        轉換後的數據
    """
    logger = get_run_logger()
    logger.info(f"轉換 {len(data)} 條記錄")

    # 模擬數據轉換
    transformed = [x * 2 for x in data]
    logger.info("轉換完成")

    return transformed


@task(
    name="數據加載任務",
    description="將數據加載到目標系統",
    tags=["ETL", "加載", "數據庫"],
    version="1.0.0"
)
def load_data(data: list, target: str) -> str:
    """
    數據加載任務

    Args:
        data: 要加載的數據
        target: 目標系統名稱

    Returns:
        加載狀態
    """
    logger = get_run_logger()
    logger.info(f"將 {len(data)} 條記錄加載到 {target}")

    # 模擬數據加載
    time.sleep(1)
    logger.info("數據加載成功")

    return f"✓ {len(data)} 條記錄已加載到 {target}"


# ============================================================================
# 工作流示例
# ============================================================================

@flow(name="任務配置演示")
def task_configuration_demo():
    """
    演示各種任務配置的工作流
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("任務配置演示")
    logger.info("=" * 60)

    # 1. 基本任務
    logger.info("\n--- 基本任務 ---")
    basic_task("Hello Prefect")

    # 2. 重試機制
    logger.info("\n--- 重試機制 ---")
    try:
        task_with_retries(fail_count=2)
    except Exception as e:
        logger.error(f"任務失敗：{e}")

    # 3. 超時設置
    logger.info("\n--- 超時設置 ---")
    try:
        task_with_timeout(sleep_time=2)  # 應該成功
        # task_with_timeout(sleep_time=10)  # 會超時
    except Exception as e:
        logger.error(f"任務超時：{e}")

    logger.info("\n演示完成！")


@flow(name="緩存演示")
def caching_demo():
    """
    演示緩存機制的工作流
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("緩存機制演示")
    logger.info("=" * 60)

    # 第一次調用 - 會執行計算
    logger.info("\n--- 第一次調用（會執行計算）---")
    result1 = cached_task(10, 20)
    logger.info(f"結果：{result1}")

    # 第二次調用相同參數 - 使用緩存
    logger.info("\n--- 第二次調用（使用緩存）---")
    result2 = cached_task(10, 20)
    logger.info(f"結果：{result2}")

    # 不同參數 - 會重新計算
    logger.info("\n--- 不同參數（重新計算）---")
    result3 = cached_task(15, 25)
    logger.info(f"結果：{result3}")

    logger.info("\n緩存演示完成！")


@flow(name="ETL 管道")
def etl_pipeline():
    """
    使用標籤組織的 ETL 工作流
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("ETL 管道")
    logger.info("=" * 60)

    # 提取
    logger.info("\n--- 提取階段 ---")
    raw_data = extract_data("PostgreSQL")

    # 轉換
    logger.info("\n--- 轉換階段 ---")
    transformed_data = transform_data(raw_data)

    # 加載
    logger.info("\n--- 加載階段 ---")
    status = load_data(transformed_data, "Data Warehouse")

    logger.info(f"\n{status}")
    logger.info("ETL 管道完成！")


@flow(name="持久化演示")
def persistence_demo():
    """
    演示結果持久化
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("結果持久化演示")
    logger.info("=" * 60)

    data = [10, 20, 30, 40, 50]
    result = task_with_persisted_result(data)

    logger.info(f"結果：{result}")
    logger.info("結果已持久化到存儲")


# ============================================================================
# 高級任務模式
# ============================================================================

@task
def conditional_task(condition: bool) -> str:
    """
    根據條件返回不同結果的任務

    Args:
        condition: 條件

    Returns:
        結果消息
    """
    logger = get_run_logger()

    if condition:
        logger.info("條件為真，執行路徑 A")
        return "路徑 A 的結果"
    else:
        logger.info("條件為假，執行路徑 B")
        return "路徑 B 的結果"


@flow(name="條件執行示例")
def conditional_execution_demo():
    """
    演示條件執行
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("條件執行示例")
    logger.info("=" * 60)

    # 測試兩種情況
    result1 = conditional_task(True)
    logger.info(f"條件=True 的結果：{result1}")

    result2 = conditional_task(False)
    logger.info(f"條件=False 的結果：{result2}")


# ============================================================================
# 運行示例
# ============================================================================

def main():
    """
    主函數 - 運行所有示例
    """
    print("\n" + "=" * 70)
    print("Prefect 任務定義詳解")
    print("=" * 70)

    # 示例 1: 任務配置
    print("\n【示例 1】任務配置演示")
    print("-" * 70)
    task_configuration_demo()

    # 示例 2: 緩存機制
    print("\n【示例 2】緩存機制演示")
    print("-" * 70)
    caching_demo()

    # 示例 3: ETL 管道
    print("\n【示例 3】ETL 管道（帶標籤）")
    print("-" * 70)
    etl_pipeline()

    # 示例 4: 持久化
    print("\n【示例 4】結果持久化")
    print("-" * 70)
    persistence_demo()

    # 示例 5: 條件執行
    print("\n【示例 5】條件執行")
    print("-" * 70)
    conditional_execution_demo()

    # 任務配置總結
    print("\n" + "=" * 70)
    print("任務配置選項總結")
    print("=" * 70)
    print("""
1. 基本配置：
   - name: 任務名稱
   - description: 任務描述
   - tags: 標籤列表，用於分類和搜索
   - version: 版本號

2. 重試配置：
   - retries: 重試次數（默認 0）
   - retry_delay_seconds: 重試延遲，可以是單個數字或列表

3. 超時配置：
   - timeout_seconds: 任務超時時間

4. 緩存配置：
   - cache_key_fn: 緩存鍵函數（如 task_input_hash）
   - cache_expiration: 緩存過期時間

5. 持久化配置：
   - persist_result: 是否持久化結果

6. 最佳實踐：
   - 為任務添加清晰的名稱和描述
   - 為相關任務添加標籤，方便管理
   - 為不穩定的操作設置重試
   - 為長時間運行的任務設置超時
   - 為昂貴的計算啟用緩存

7. 下一步：
   - 查看 03_參數傳遞.py 了解參數處理
   - 查看 04_並行執行.py 了解任務並發
   - 查看 07_緩存機制.py 深入了解緩存策略
    """)

    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
