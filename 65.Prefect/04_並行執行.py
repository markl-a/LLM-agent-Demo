#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prefect 並行執行示例
====================

這個示例展示了 Prefect 中的並發執行功能，包括：
1. 使用 submit() 並行執行任務
2. map() 函數批量並行處理
3. 不同的 TaskRunner 配置
4. 並發控制和限制
5. 等待任務完成
6. 並行任務的錯誤處理
"""

from prefect import task, flow, get_run_logger
from prefect.task_runners import ConcurrentTaskRunner, SequentialTaskRunner
from prefect.futures import wait
from typing import List
import time
import random
from datetime import datetime


# ============================================================================
# 基本並行任務
# ============================================================================

@task
def slow_task(task_id: int, duration: float = 1.0) -> dict:
    """
    模擬耗時任務

    Args:
        task_id: 任務 ID
        duration: 執行時長（秒）

    Returns:
        任務結果
    """
    logger = get_run_logger()
    start_time = time.time()

    logger.info(f"任務 {task_id} 開始執行（預計 {duration} 秒）")
    time.sleep(duration)

    end_time = time.time()
    elapsed = end_time - start_time

    result = {
        "task_id": task_id,
        "duration": duration,
        "actual_time": elapsed,
        "timestamp": datetime.now().isoformat()
    }

    logger.info(f"任務 {task_id} 完成（實際用時 {elapsed:.2f} 秒）")
    return result


# ============================================================================
# 順序執行 vs 並行執行
# ============================================================================

@flow(name="順序執行示例", task_runner=SequentialTaskRunner())
def sequential_flow(task_count: int = 5):
    """
    順序執行任務

    Args:
        task_count: 任務數量
    """
    logger = get_run_logger()
    logger.info(f"順序執行 {task_count} 個任務")

    start_time = time.time()
    results = []

    for i in range(task_count):
        result = slow_task(i, duration=1.0)
        results.append(result)

    total_time = time.time() - start_time
    logger.info(f"順序執行完成，總耗時：{total_time:.2f} 秒")

    return results


@flow(name="並行執行示例", task_runner=ConcurrentTaskRunner())
def parallel_flow(task_count: int = 5):
    """
    並行執行任務

    Args:
        task_count: 任務數量
    """
    logger = get_run_logger()
    logger.info(f"並行執行 {task_count} 個任務")

    start_time = time.time()

    # 使用 submit() 提交任務以並行執行
    futures = []
    for i in range(task_count):
        future = slow_task.submit(i, duration=1.0)
        futures.append(future)

    # 等待所有任務完成並獲取結果
    results = [future.result() for future in futures]

    total_time = time.time() - start_time
    logger.info(f"並行執行完成，總耗時：{total_time:.2f} 秒")

    return results


# ============================================================================
# 使用 map() 進行並行處理
# ============================================================================

@task
def process_item(item: int) -> dict:
    """
    處理單個項目

    Args:
        item: 要處理的項目

    Returns:
        處理結果
    """
    logger = get_run_logger()
    logger.info(f"處理項目 {item}")

    # 模擬處理時間
    processing_time = random.uniform(0.5, 2.0)
    time.sleep(processing_time)

    result = {
        "item": item,
        "result": item ** 2,
        "processing_time": processing_time
    }

    logger.info(f"項目 {item} 處理完成")
    return result


@flow(name="Map 並行處理", task_runner=ConcurrentTaskRunner())
def map_parallel_flow(items: List[int]):
    """
    使用 map() 並行處理多個項目

    Args:
        items: 要處理的項目列表
    """
    logger = get_run_logger()
    logger.info(f"使用 map() 並行處理 {len(items)} 個項目")

    start_time = time.time()

    # map() 會自動並行處理所有項目
    results = process_item.map(items)

    total_time = time.time() - start_time
    logger.info(f"Map 處理完成，總耗時：{total_time:.2f} 秒")

    return results


# ============================================================================
# 動態並行任務生成
# ============================================================================

@task
def fetch_urls(url: str) -> dict:
    """
    模擬獲取 URL 內容

    Args:
        url: URL 地址

    Returns:
        獲取結果
    """
    logger = get_run_logger()
    logger.info(f"獲取 URL: {url}")

    # 模擬網絡請求
    time.sleep(random.uniform(0.5, 1.5))

    result = {
        "url": url,
        "status": 200,
        "content_length": random.randint(1000, 5000),
        "timestamp": datetime.now().isoformat()
    }

    logger.info(f"URL 獲取成功: {url} ({result['content_length']} bytes)")
    return result


@flow(name="動態並行任務", task_runner=ConcurrentTaskRunner())
def dynamic_parallel_flow(urls: List[str]):
    """
    動態生成並行任務

    Args:
        urls: URL 列表
    """
    logger = get_run_logger()
    logger.info(f"並行獲取 {len(urls)} 個 URL")

    start_time = time.time()

    # 動態提交任務
    futures = [fetch_urls.submit(url) for url in urls]

    # 等待所有任務完成
    logger.info("等待所有任務完成...")
    results = [future.result() for future in futures]

    total_time = time.time() - start_time
    logger.info(f"所有 URL 獲取完成，總耗時：{total_time:.2f} 秒")

    # 統計
    total_size = sum(r['content_length'] for r in results)
    logger.info(f"總共獲取 {total_size} bytes 數據")

    return results


# ============================================================================
# 並發控制
# ============================================================================

@task
def rate_limited_task(task_id: int) -> str:
    """
    需要速率限制的任務

    Args:
        task_id: 任務 ID

    Returns:
        結果
    """
    logger = get_run_logger()
    logger.info(f"執行速率限制任務 {task_id}")

    # 模擬 API 調用
    time.sleep(0.5)

    return f"任務 {task_id} 完成"


@flow(name="並發控制示例", task_runner=ConcurrentTaskRunner())
def concurrency_control_flow(task_count: int = 20):
    """
    演示並發控制

    Args:
        task_count: 任務總數
    """
    logger = get_run_logger()
    logger.info(f"執行 {task_count} 個任務（並發控制）")

    start_time = time.time()

    # 提交所有任務
    futures = [rate_limited_task.submit(i) for i in range(task_count)]

    # 等待所有任務完成
    results = [future.result() for future in futures]

    total_time = time.time() - start_time
    logger.info(f"所有任務完成，總耗時：{total_time:.2f} 秒")

    return results


# ============================================================================
# 等待部分任務完成
# ============================================================================

@task
def variable_duration_task(task_id: int, duration: float) -> dict:
    """
    可變時長的任務

    Args:
        task_id: 任務 ID
        duration: 執行時長

    Returns:
        結果
    """
    logger = get_run_logger()
    logger.info(f"任務 {task_id} 開始（{duration:.1f}s）")

    time.sleep(duration)

    logger.info(f"任務 {task_id} 完成")
    return {"task_id": task_id, "duration": duration}


@flow(name="部分等待示例", task_runner=ConcurrentTaskRunner())
def partial_wait_flow():
    """
    演示等待部分任務完成
    """
    logger = get_run_logger()
    logger.info("提交不同時長的任務")

    # 提交不同執行時長的任務
    durations = [0.5, 1.0, 1.5, 2.0, 2.5]
    futures = [
        variable_duration_task.submit(i, duration)
        for i, duration in enumerate(durations)
    ]

    # 等待最快的任務完成
    logger.info("\n--- 等待第一個任務完成 ---")
    completed_futures, pending_futures = wait(futures, return_when="FIRST_COMPLETED")
    logger.info(f"已完成: {len(completed_futures)}, 待完成: {len(pending_futures)}")

    # 等待所有任務完成
    logger.info("\n--- 等待所有任務完成 ---")
    results = [future.result() for future in futures]
    logger.info(f"所有 {len(results)} 個任務已完成")

    return results


# ============================================================================
# 錯誤處理
# ============================================================================

@task
def unreliable_task(task_id: int, fail_probability: float = 0.3) -> str:
    """
    可能失敗的任務

    Args:
        task_id: 任務 ID
        fail_probability: 失敗概率

    Returns:
        結果

    Raises:
        RuntimeError: 隨機失敗
    """
    logger = get_run_logger()
    logger.info(f"執行不穩定任務 {task_id}")

    time.sleep(0.5)

    if random.random() < fail_probability:
        logger.error(f"任務 {task_id} 失敗")
        raise RuntimeError(f"任務 {task_id} 執行失敗")

    logger.info(f"任務 {task_id} 成功")
    return f"任務 {task_id} 完成"


@flow(name="並行錯誤處理", task_runner=ConcurrentTaskRunner())
def parallel_error_handling_flow(task_count: int = 10):
    """
    演示並行執行中的錯誤處理

    Args:
        task_count: 任務數量
    """
    logger = get_run_logger()
    logger.info(f"執行 {task_count} 個可能失敗的任務")

    # 提交所有任務
    futures = [unreliable_task.submit(i, fail_probability=0.3) for i in range(task_count)]

    # 收集結果，處理錯誤
    results = []
    errors = []

    for i, future in enumerate(futures):
        try:
            result = future.result()
            results.append(result)
        except Exception as e:
            logger.error(f"任務 {i} 失敗：{e}")
            errors.append({"task_id": i, "error": str(e)})

    logger.info(f"\n成功: {len(results)}, 失敗: {len(errors)}")
    return {"results": results, "errors": errors}


# ============================================================================
# 實際應用：批量數據處理
# ============================================================================

@task
def process_batch(batch_id: int, data_batch: List[int]) -> dict:
    """
    處理數據批次

    Args:
        batch_id: 批次 ID
        data_batch: 數據批次

    Returns:
        處理結果
    """
    logger = get_run_logger()
    logger.info(f"處理批次 {batch_id}（{len(data_batch)} 項）")

    # 模擬批量處理
    time.sleep(random.uniform(0.5, 1.5))

    result = {
        "batch_id": batch_id,
        "count": len(data_batch),
        "sum": sum(data_batch),
        "avg": sum(data_batch) / len(data_batch) if data_batch else 0
    }

    logger.info(f"批次 {batch_id} 處理完成")
    return result


@flow(name="批量數據處理", task_runner=ConcurrentTaskRunner())
def batch_processing_flow(data: List[int], batch_size: int = 10):
    """
    並行批量處理數據

    Args:
        data: 要處理的數據
        batch_size: 批次大小
    """
    logger = get_run_logger()
    logger.info(f"處理 {len(data)} 個數據項，批次大小 {batch_size}")

    start_time = time.time()

    # 分批
    batches = [
        data[i:i + batch_size]
        for i in range(0, len(data), batch_size)
    ]
    logger.info(f"分為 {len(batches)} 個批次")

    # 並行處理所有批次
    futures = [
        process_batch.submit(i, batch)
        for i, batch in enumerate(batches)
    ]

    # 等待所有批次完成
    results = [future.result() for future in futures]

    total_time = time.time() - start_time

    # 統計
    total_count = sum(r['count'] for r in results)
    total_sum = sum(r['sum'] for r in results)
    overall_avg = total_sum / total_count if total_count > 0 else 0

    logger.info(f"\n批量處理完成：")
    logger.info(f"  - 總數據量: {total_count}")
    logger.info(f"  - 總和: {total_sum}")
    logger.info(f"  - 平均值: {overall_avg:.2f}")
    logger.info(f"  - 總耗時: {total_time:.2f} 秒")

    return results


# ============================================================================
# 運行示例
# ============================================================================

def main():
    """
    主函數 - 運行所有示例
    """
    print("\n" + "=" * 70)
    print("Prefect 並行執行示例")
    print("=" * 70)

    # 示例 1: 順序 vs 並行
    print("\n【示例 1】順序執行 vs 並行執行")
    print("-" * 70)
    print("\n順序執行:")
    sequential_flow(task_count=5)

    print("\n並行執行:")
    parallel_flow(task_count=5)

    # 示例 2: Map 並行處理
    print("\n【示例 2】Map 並行處理")
    print("-" * 70)
    items = list(range(1, 11))
    map_parallel_flow(items)

    # 示例 3: 動態並行任務
    print("\n【示例 3】動態並行任務")
    print("-" * 70)
    urls = [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3",
        "https://example.com/page4",
        "https://example.com/page5"
    ]
    dynamic_parallel_flow(urls)

    # 示例 4: 並發控制
    print("\n【示例 4】並發控制")
    print("-" * 70)
    concurrency_control_flow(task_count=10)

    # 示例 5: 部分等待
    print("\n【示例 5】部分等待示例")
    print("-" * 70)
    partial_wait_flow()

    # 示例 6: 錯誤處理
    print("\n【示例 6】並行錯誤處理")
    print("-" * 70)
    error_results = parallel_error_handling_flow(task_count=10)
    print(f"成功: {len(error_results['results'])}, 失敗: {len(error_results['errors'])}")

    # 示例 7: 批量數據處理
    print("\n【示例 7】批量數據處理")
    print("-" * 70)
    data = list(range(1, 101))
    batch_processing_flow(data, batch_size=20)

    # 使用說明
    print("\n" + "=" * 70)
    print("並行執行總結")
    print("=" * 70)
    print("""
1. 並行執行方法：
   - submit(): 提交單個任務並行執行
   - map(): 批量並行處理
   - 返回 Future 對象，調用 .result() 獲取結果

2. TaskRunner 類型：
   - SequentialTaskRunner: 順序執行（默認）
   - ConcurrentTaskRunner: 並發執行（多線程）
   - DaskTaskRunner: 分布式執行（需安裝 dask）

3. 使用場景：
   - I/O 密集型任務：網絡請求、文件讀寫
   - 獨立任務：任務間無依賴關係
   - 批量處理：大量相似的任務

4. 性能對比：
   - 順序執行 5 個任務（每個 1 秒）：~5 秒
   - 並行執行 5 個任務（每個 1 秒）：~1 秒

5. 最佳實踐：
   - 使用 submit() 處理獨立任務
   - 使用 map() 處理列表數據
   - 適當控制並發數量
   - 處理並行任務中的異常

6. 注意事項：
   - CPU 密集型任務可能不適合多線程
   - 注意外部服務的速率限制
   - 處理共享資源時要小心

7. 下一步：
   - 查看 05_調度器.py 了解任務調度
   - 查看 06_狀態管理.py 了解狀態處理
    """)

    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
