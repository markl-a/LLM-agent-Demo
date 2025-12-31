#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prefect 緩存機制
=================

這個示例展示了 Prefect 的緩存功能，包括：
1. 基於輸入的緩存
2. 基於任務的緩存
3. 緩存過期設置
4. 自定義緩存鍵
5. 緩存策略
6. 緩存失效
"""

from prefect import task, flow, get_run_logger
from prefect.tasks import task_input_hash
from prefect.cache_policies import CachePolicy, INPUTS, TASK_SOURCE
from datetime import timedelta, datetime
import time
import hashlib
import json
from typing import Any, Optional


# ============================================================================
# 基本緩存示例
# ============================================================================

@task(
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(minutes=5)
)
def expensive_computation(x: int, y: int) -> int:
    """
    昂貴的計算任務（帶緩存）

    相同的輸入在 5 分鐘內會使用緩存結果。

    Args:
        x: 第一個數字
        y: 第二個數字

    Returns:
        計算結果
    """
    logger = get_run_logger()
    logger.info(f"執行昂貴的計算：{x} + {y}")
    logger.info("這是一個耗時的操作...")

    # 模擬耗時計算
    time.sleep(2)

    result = x + y
    logger.info(f"計算完成：{result}")

    return result


@flow(name="基本緩存示例")
def basic_cache_demo():
    """
    演示基本的緩存功能
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("基本緩存示例")
    logger.info("=" * 60)

    # 第一次調用 - 會執行計算
    logger.info("\n--- 第一次調用（會執行計算）---")
    start1 = time.time()
    result1 = expensive_computation(10, 20)
    time1 = time.time() - start1
    logger.info(f"結果：{result1}，耗時：{time1:.2f}s")

    # 第二次調用相同參數 - 使用緩存
    logger.info("\n--- 第二次調用相同參數（使用緩存）---")
    start2 = time.time()
    result2 = expensive_computation(10, 20)
    time2 = time.time() - start2
    logger.info(f"結果：{result2}，耗時：{time2:.2f}s")

    # 不同參數 - 會重新計算
    logger.info("\n--- 不同參數（重新計算）---")
    start3 = time.time()
    result3 = expensive_computation(15, 25)
    time3 = time.time() - start3
    logger.info(f"結果：{result3}，耗時：{time3:.2f}s")

    logger.info(f"\n性能對比：")
    logger.info(f"  第一次：{time1:.2f}s（實際計算）")
    logger.info(f"  第二次：{time2:.2f}s（緩存，快 {time1/time2:.1f}x）")
    logger.info(f"  第三次：{time3:.2f}s（實際計算）")


# ============================================================================
# 不同緩存過期時間
# ============================================================================

@task(
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(seconds=10)
)
def short_cache_task(value: int) -> str:
    """
    短期緩存任務（10 秒）

    Args:
        value: 輸入值

    Returns:
        結果
    """
    logger = get_run_logger()
    logger.info(f"執行短期緩存任務：{value}")

    time.sleep(1)

    result = f"值：{value}，時間：{datetime.now().strftime('%H:%M:%S')}"
    logger.info(f"結果：{result}")

    return result


@task(
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=1)
)
def long_cache_task(value: int) -> str:
    """
    長期緩存任務（1 小時）

    Args:
        value: 輸入值

    Returns:
        結果
    """
    logger = get_run_logger()
    logger.info(f"執行長期緩存任務：{value}")

    time.sleep(1)

    result = f"值：{value}，時間：{datetime.now().strftime('%H:%M:%S')}"
    logger.info(f"結果：{result}")

    return result


@flow(name="緩存過期示例")
def cache_expiration_demo():
    """
    演示不同的緩存過期時間
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("緩存過期示例")
    logger.info("=" * 60)

    # 短期緩存
    logger.info("\n--- 短期緩存（10 秒）---")
    result1 = short_cache_task(100)
    logger.info(f"第一次：{result1}")

    result2 = short_cache_task(100)
    logger.info(f"第二次（緩存）：{result2}")

    # 長期緩存
    logger.info("\n--- 長期緩存（1 小時）---")
    result3 = long_cache_task(200)
    logger.info(f"第一次：{result3}")

    result4 = long_cache_task(200)
    logger.info(f"第二次（緩存）：{result4}")


# ============================================================================
# 自定義緩存鍵函數
# ============================================================================

def custom_cache_key_fn(context, parameters):
    """
    自定義緩存鍵函數

    只基於特定參數生成緩存鍵，忽略其他參數。

    Args:
        context: 任務上下文
        parameters: 任務參數

    Returns:
        緩存鍵
    """
    # 只使用 'id' 參數作為緩存鍵，忽略 'timestamp'
    cache_key_data = {
        "id": parameters.get("id"),
        "task_name": context.task.name
    }

    # 生成 hash
    cache_key = hashlib.md5(
        json.dumps(cache_key_data, sort_keys=True).encode()
    ).hexdigest()

    return cache_key


@task(
    cache_key_fn=custom_cache_key_fn,
    cache_expiration=timedelta(minutes=10)
)
def task_with_custom_cache(id: int, timestamp: str = None) -> dict:
    """
    使用自定義緩存鍵的任務

    只基於 id 緩存，忽略 timestamp 參數。

    Args:
        id: ID（用於緩存）
        timestamp: 時間戳（不用於緩存）

    Returns:
        結果
    """
    logger = get_run_logger()
    logger.info(f"執行任務：id={id}, timestamp={timestamp}")

    time.sleep(1)

    result = {
        "id": id,
        "timestamp": timestamp or datetime.now().isoformat(),
        "computed_at": datetime.now().isoformat()
    }

    logger.info(f"結果：{result}")
    return result


@flow(name="自定義緩存鍵示例")
def custom_cache_key_demo():
    """
    演示自定義緩存鍵
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("自定義緩存鍵示例")
    logger.info("=" * 60)

    # 相同 id，不同 timestamp - 會使用緩存
    logger.info("\n--- 相同 ID，不同 timestamp ---")
    result1 = task_with_custom_cache(1, "2024-01-01")
    logger.info(f"第一次：{result1}")

    result2 = task_with_custom_cache(1, "2024-01-02")
    logger.info(f"第二次（緩存，注意 computed_at 相同）：{result2}")

    # 不同 id - 不使用緩存
    logger.info("\n--- 不同 ID ---")
    result3 = task_with_custom_cache(2, "2024-01-01")
    logger.info(f"第三次（重新計算）：{result3}")


# ============================================================================
# 無緩存 vs 有緩存性能對比
# ============================================================================

@task
def no_cache_task(x: int) -> int:
    """
    無緩存的任務

    Args:
        x: 輸入值

    Returns:
        結果
    """
    logger = get_run_logger()
    logger.info(f"執行無緩存任務：{x}")

    time.sleep(0.5)  # 模擬計算

    return x * x


@task(
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(minutes=10)
)
def with_cache_task(x: int) -> int:
    """
    有緩存的任務

    Args:
        x: 輸入值

    Returns:
        結果
    """
    logger = get_run_logger()
    logger.info(f"執行有緩存任務：{x}")

    time.sleep(0.5)  # 模擬計算

    return x * x


@flow(name="緩存性能對比")
def cache_performance_demo():
    """
    對比有無緩存的性能差異
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("緩存性能對比")
    logger.info("=" * 60)

    # 無緩存
    logger.info("\n--- 無緩存任務（重複調用 5 次）---")
    start1 = time.time()
    for i in range(5):
        result = no_cache_task(10)
    time1 = time.time() - start1
    logger.info(f"總耗時：{time1:.2f}s")

    # 有緩存
    logger.info("\n--- 有緩存任務（重複調用 5 次）---")
    start2 = time.time()
    for i in range(5):
        result = with_cache_task(10)
    time2 = time.time() - start2
    logger.info(f"總耗時：{time2:.2f}s")

    logger.info(f"\n性能提升：{time1/time2:.1f}x")


# ============================================================================
# 緩存策略示例
# ============================================================================

@task(
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(minutes=30)
)
def fetch_api_data(api_endpoint: str) -> dict:
    """
    獲取 API 數據（帶緩存）

    避免頻繁調用外部 API。

    Args:
        api_endpoint: API 端點

    Returns:
        API 響應
    """
    logger = get_run_logger()
    logger.info(f"調用 API：{api_endpoint}")
    logger.info("這會產生 API 費用...")

    # 模擬 API 調用
    time.sleep(1)

    response = {
        "endpoint": api_endpoint,
        "status": 200,
        "data": {"key": "value"},
        "fetched_at": datetime.now().isoformat()
    }

    logger.info(f"API 響應：{response}")
    return response


@task(
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=24)
)
def process_large_dataset(dataset_id: str) -> dict:
    """
    處理大型數據集（帶緩存）

    對於不常變化的數據集，使用長期緩存。

    Args:
        dataset_id: 數據集 ID

    Returns:
        處理結果
    """
    logger = get_run_logger()
    logger.info(f"處理大型數據集：{dataset_id}")
    logger.info("這是一個非常耗時的操作...")

    # 模擬數據處理
    time.sleep(2)

    result = {
        "dataset_id": dataset_id,
        "rows_processed": 1000000,
        "processing_time": 2.0,
        "processed_at": datetime.now().isoformat()
    }

    logger.info(f"處理完成：{result}")
    return result


@flow(name="緩存策略示例")
def cache_strategy_demo():
    """
    演示不同場景的緩存策略
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("緩存策略示例")
    logger.info("=" * 60)

    # API 調用緩存（避免重複調用）
    logger.info("\n--- API 調用緩存 ---")
    api_result1 = fetch_api_data("/users")
    logger.info(f"第一次調用：{api_result1['fetched_at']}")

    api_result2 = fetch_api_data("/users")
    logger.info(f"第二次調用（緩存）：{api_result2['fetched_at']}")

    # 大數據處理緩存（避免重複處理）
    logger.info("\n--- 大數據處理緩存 ---")
    data_result1 = process_large_dataset("dataset-2024")
    logger.info(f"第一次處理：{data_result1['processed_at']}")

    data_result2 = process_large_dataset("dataset-2024")
    logger.info(f"第二次處理（緩存）：{data_result2['processed_at']}")


# ============================================================================
# 條件緩存
# ============================================================================

def conditional_cache_key_fn(context, parameters):
    """
    條件緩存鍵函數

    根據參數決定是否使用緩存。

    Args:
        context: 任務上下文
        parameters: 任務參數

    Returns:
        緩存鍵或 None（不緩存）
    """
    use_cache = parameters.get("use_cache", True)

    if not use_cache:
        # 返回 None 表示不使用緩存
        return None

    # 使用正常的緩存鍵
    return task_input_hash(context, parameters)


@task(
    cache_key_fn=conditional_cache_key_fn,
    cache_expiration=timedelta(minutes=10)
)
def conditional_cache_task(value: int, use_cache: bool = True) -> dict:
    """
    條件緩存任務

    Args:
        value: 值
        use_cache: 是否使用緩存

    Returns:
        結果
    """
    logger = get_run_logger()
    logger.info(f"執行任務：value={value}, use_cache={use_cache}")

    time.sleep(1)

    result = {
        "value": value,
        "use_cache": use_cache,
        "computed_at": datetime.now().isoformat()
    }

    return result


@flow(name="條件緩存示例")
def conditional_cache_demo():
    """
    演示條件緩存
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("條件緩存示例")
    logger.info("=" * 60)

    # 使用緩存
    logger.info("\n--- 使用緩存 ---")
    result1 = conditional_cache_task(100, use_cache=True)
    logger.info(f"第一次：{result1}")

    result2 = conditional_cache_task(100, use_cache=True)
    logger.info(f"第二次（緩存）：{result2}")

    # 不使用緩存
    logger.info("\n--- 不使用緩存 ---")
    result3 = conditional_cache_task(100, use_cache=False)
    logger.info(f"第三次（強制重新計算）：{result3}")


# ============================================================================
# 實際應用：數據管道緩存
# ============================================================================

@task(
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=6)
)
def extract_data(source: str) -> list:
    """
    提取數據（帶緩存）

    Args:
        source: 數據源

    Returns:
        數據列表
    """
    logger = get_run_logger()
    logger.info(f"從 {source} 提取數據")

    time.sleep(1)  # 模擬數據提取

    data = [{"id": i, "value": i * 10} for i in range(1, 11)]
    logger.info(f"提取了 {len(data)} 條記錄")

    return data


@task(
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=1)
)
def transform_data(data: list) -> list:
    """
    轉換數據（帶緩存）

    Args:
        data: 原始數據

    Returns:
        轉換後的數據
    """
    logger = get_run_logger()
    logger.info(f"轉換 {len(data)} 條記錄")

    time.sleep(1)  # 模擬數據轉換

    transformed = [
        {**item, "transformed": True, "doubled_value": item["value"] * 2}
        for item in data
    ]

    logger.info("轉換完成")
    return transformed


@task
def load_data(data: list, target: str) -> str:
    """
    加載數據（不緩存）

    加載操作通常不應該緩存。

    Args:
        data: 數據
        target: 目標

    Returns:
        狀態
    """
    logger = get_run_logger()
    logger.info(f"加載 {len(data)} 條記錄到 {target}")

    time.sleep(0.5)  # 模擬數據加載

    return f"✓ 已加載 {len(data)} 條記錄到 {target}"


@flow(name="數據管道緩存")
def cached_etl_pipeline(source: str = "database", target: str = "warehouse"):
    """
    使用緩存的 ETL 管道

    Args:
        source: 數據源
        target: 目標
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("帶緩存的 ETL 管道")
    logger.info("=" * 60)

    # 提取（會緩存）
    logger.info("\n--- 提取階段 ---")
    data = extract_data(source)

    # 轉換（會緩存）
    logger.info("\n--- 轉換階段 ---")
    transformed_data = transform_data(data)

    # 加載（不緩存）
    logger.info("\n--- 加載階段 ---")
    status = load_data(transformed_data, target)

    logger.info(f"\n{status}")
    return status


# ============================================================================
# 運行示例
# ============================================================================

def main():
    """
    主函數 - 運行所有示例
    """
    print("\n" + "=" * 70)
    print("Prefect 緩存機制")
    print("=" * 70)

    # 示例 1: 基本緩存
    print("\n【示例 1】基本緩存")
    print("-" * 70)
    basic_cache_demo()

    # 示例 2: 緩存過期
    print("\n【示例 2】緩存過期時間")
    print("-" * 70)
    cache_expiration_demo()

    # 示例 3: 自定義緩存鍵
    print("\n【示例 3】自定義緩存鍵")
    print("-" * 70)
    custom_cache_key_demo()

    # 示例 4: 性能對比
    print("\n【示例 4】緩存性能對比")
    print("-" * 70)
    cache_performance_demo()

    # 示例 5: 緩存策略
    print("\n【示例 5】緩存策略")
    print("-" * 70)
    cache_strategy_demo()

    # 示例 6: 條件緩存
    print("\n【示例 6】條件緩存")
    print("-" * 70)
    conditional_cache_demo()

    # 示例 7: ETL 管道
    print("\n【示例 7】ETL 管道緩存")
    print("-" * 70)
    cached_etl_pipeline()

    # 第二次運行 ETL（會使用緩存）
    print("\n【示例 8】ETL 管道第二次運行（使用緩存）")
    print("-" * 70)
    cached_etl_pipeline()

    # 使用說明
    print("\n" + "=" * 70)
    print("緩存機制總結")
    print("=" * 70)
    print("""
1. 緩存配置：
   @task(
       cache_key_fn=task_input_hash,  # 緩存鍵函數
       cache_expiration=timedelta(hours=1)  # 過期時間
   )

2. 內建緩存鍵函數：
   - task_input_hash: 基於輸入參數（最常用）
   - 自定義函數: 自定義緩存邏輯

3. 緩存過期時間：
   - 短期: timedelta(minutes=5-30)
   - 中期: timedelta(hours=1-6)
   - 長期: timedelta(days=1-7)

4. 使用場景：
   - API 調用: 避免重複請求
   - 數據提取: 減少數據庫查詢
   - 計算密集: 避免重複計算
   - 數據處理: 緩存中間結果

5. 緩存策略：
   - 頻繁變化的數據: 短期緩存或不緩存
   - 穩定的數據: 長期緩存
   - API 調用: 根據速率限制設置
   - 昂貴操作: 盡可能使用緩存

6. 注意事項：
   - 緩存會佔用存儲空間
   - 確保緩存鍵的唯一性
   - 考慮數據新鮮度要求
   - 寫操作通常不應緩存

7. 性能提升：
   - 可以提升 10x - 100x 性能
   - 減少外部服務調用
   - 降低計算成本
   - 提高響應速度

8. 下一步：
   - 查看 08_通知告警.py 了解通知配置
   - 查看 09_部署配置.py 了解部署選項
    """)

    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
