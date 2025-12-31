"""
Julep 並行執行示例

這個模塊展示了 Julep 平台的並行任務執行功能。
包括並發處理、線程池、異步執行、任務隊列和性能優化。

主要功能：
1. 並行任務執行
2. 線程池管理
3. 異步工作流
4. 任務隊列
5. 批量處理
6. 性能監控

作者：Julep 示例
日期：2025-12-31
"""

import time
import json
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed, Future
import threading
import queue
import uuid
import asyncio


class TaskStatus(Enum):
    """任務狀態"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """任務類"""
    id: str
    name: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: int = 0
    timeout: Optional[float] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def execute(self) -> Any:
        """執行任務"""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()

        try:
            result = self.func(*self.args, **self.kwargs)
            self.status = TaskStatus.COMPLETED
            self.result = result
            self.completed_at = datetime.now()
            return result
        except Exception as e:
            self.status = TaskStatus.FAILED
            self.error = str(e)
            self.completed_at = datetime.now()
            raise

    def get_duration(self) -> Optional[float]:
        """獲取執行時長"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def __lt__(self, other):
        """比較優先級（用於優先隊列）"""
        return self.priority > other.priority  # 高優先級在前


class ParallelExecutor:
    """並行執行器

    使用線程池並行執行多個任務。
    """

    def __init__(self, max_workers: int = 5):
        """初始化執行器

        Args:
            max_workers: 最大工作線程數
        """
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks: Dict[str, Task] = {}
        self.futures: Dict[str, Future] = {}

    def submit_task(
        self,
        name: str,
        func: Callable,
        *args,
        priority: int = 0,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Task:
        """提交任務

        Args:
            name: 任務名稱
            func: 執行函數
            *args: 位置參數
            priority: 優先級
            timeout: 超時時間
            **kwargs: 關鍵字參數

        Returns:
            任務對象
        """
        task_id = f"task_{uuid.uuid4().hex[:8]}"

        task = Task(
            id=task_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            timeout=timeout
        )

        # 提交到線程池
        future = self.executor.submit(task.execute)
        self.tasks[task_id] = task
        self.futures[task_id] = future

        print(f"[SUBMIT] 提交任務: {name} (ID: {task_id})")
        return task

    def wait_all(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """等待所有任務完成

        Args:
            timeout: 超時時間

        Returns:
            任務結果字典
        """
        print(f"\n[WAIT] 等待 {len(self.futures)} 個任務完成...")
        results = {}

        for task_id, future in self.futures.items():
            task = self.tasks[task_id]
            try:
                result = future.result(timeout=timeout)
                results[task_id] = {
                    "name": task.name,
                    "status": "completed",
                    "result": result,
                    "duration": task.get_duration()
                }
            except Exception as e:
                results[task_id] = {
                    "name": task.name,
                    "status": "failed",
                    "error": str(e)
                }

        return results

    def get_completed_count(self) -> int:
        """獲取已完成任務數"""
        return sum(1 for f in self.futures.values() if f.done())

    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
        running = sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING)

        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "running": running,
            "pending": total - completed - failed - running
        }

    def shutdown(self, wait: bool = True):
        """關閉執行器"""
        self.executor.shutdown(wait=wait)


class TaskQueue:
    """任務隊列

    管理任務的優先級隊列和批量處理。
    """

    def __init__(self, workers: int = 3):
        """初始化任務隊列

        Args:
            workers: 工作線程數
        """
        self.task_queue: queue.PriorityQueue = queue.PriorityQueue()
        self.workers = workers
        self.running = False
        self.threads: List[threading.Thread] = []
        self.completed_tasks: List[Task] = []
        self.lock = threading.Lock()

    def add_task(self, task: Task):
        """添加任務到隊列

        Args:
            task: 任務對象
        """
        self.task_queue.put(task)
        print(f"[QUEUE] 添加任務: {task.name} (優先級: {task.priority})")

    def worker(self):
        """工作線程函數"""
        while self.running:
            try:
                # 從隊列獲取任務（超時1秒）
                task = self.task_queue.get(timeout=1)

                print(f"\n[WORKER] 開始執行: {task.name}")
                task.execute()

                with self.lock:
                    self.completed_tasks.append(task)

                duration = task.get_duration()
                print(f"[WORKER] 完成: {task.name} (耗時: {duration:.2f}s)")

                self.task_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                print(f"[ERROR] 任務執行失敗: {e}")

    def start(self):
        """啟動工作線程"""
        self.running = True

        for i in range(self.workers):
            thread = threading.Thread(target=self.worker, name=f"Worker-{i+1}")
            thread.daemon = True
            thread.start()
            self.threads.append(thread)

        print(f"[INFO] 啟動了 {self.workers} 個工作線程")

    def stop(self):
        """停止工作線程"""
        self.running = False
        for thread in self.threads:
            thread.join()
        print("[INFO] 所有工作線程已停止")

    def wait_completion(self):
        """等待所有任務完成"""
        self.task_queue.join()
        print("[INFO] 所有任務已完成")

    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        with self.lock:
            completed = len(self.completed_tasks)
            pending = self.task_queue.qsize()

        return {
            "completed": completed,
            "pending": pending,
            "workers": self.workers
        }


class BatchProcessor:
    """批量處理器

    高效處理大量數據項。
    """

    def __init__(self, batch_size: int = 10, max_workers: int = 4):
        """初始化批量處理器

        Args:
            batch_size: 批次大小
            max_workers: 最大工作線程數
        """
        self.batch_size = batch_size
        self.max_workers = max_workers

    def process_batch(
        self,
        items: List[Any],
        process_func: Callable,
        show_progress: bool = True
    ) -> List[Any]:
        """處理批次

        Args:
            items: 數據項列表
            process_func: 處理函數
            show_progress: 顯示進度

        Returns:
            處理結果列表
        """
        total_items = len(items)
        results = []

        print(f"\n[BATCH] 開始批量處理 {total_items} 個項目")
        print(f"[BATCH] 批次大小: {self.batch_size}, 工作線程: {self.max_workers}")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 分批提交
            futures = []
            for i in range(0, total_items, self.batch_size):
                batch = items[i:i + self.batch_size]
                future = executor.submit(self._process_batch_items, batch, process_func)
                futures.append(future)

            # 收集結果
            completed = 0
            for future in as_completed(futures):
                batch_results = future.result()
                results.extend(batch_results)
                completed += len(batch_results)

                if show_progress:
                    progress = (completed / total_items) * 100
                    print(f"[PROGRESS] {completed}/{total_items} ({progress:.1f}%)")

        print(f"[BATCH] 處理完成，共 {len(results)} 個結果")
        return results

    def _process_batch_items(
        self,
        batch: List[Any],
        process_func: Callable
    ) -> List[Any]:
        """處理單個批次的項目

        Args:
            batch: 批次數據
            process_func: 處理函數

        Returns:
            批次結果
        """
        return [process_func(item) for item in batch]


class AsyncWorkflow:
    """異步工作流

    使用 asyncio 處理異步任務。
    """

    def __init__(self):
        """初始化異步工作流"""
        self.tasks: List[asyncio.Task] = []

    async def execute_async_task(
        self,
        name: str,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """執行異步任務

        Args:
            name: 任務名稱
            func: 異步函數
            *args: 參數
            **kwargs: 關鍵字參數

        Returns:
            執行結果
        """
        print(f"[ASYNC] 開始: {name}")
        start_time = time.time()

        result = await func(*args, **kwargs)

        duration = time.time() - start_time
        print(f"[ASYNC] 完成: {name} (耗時: {duration:.2f}s)")

        return result

    async def run_parallel(
        self,
        tasks: List[tuple]
    ) -> List[Any]:
        """並行運行多個異步任務

        Args:
            tasks: (名稱, 函數, 參數) 元組列表

        Returns:
            結果列表
        """
        print(f"\n[ASYNC] 並行執行 {len(tasks)} 個異步任務")

        coroutines = [
            self.execute_async_task(name, func, *args)
            for name, func, args in tasks
        ]

        results = await asyncio.gather(*coroutines)

        print(f"[ASYNC] 所有任務完成")
        return results


# 示例任務函數

def simulate_api_call(endpoint: str, delay: float = 0.5) -> Dict:
    """模擬 API 調用"""
    print(f"  -> 調用 API: {endpoint}")
    time.sleep(delay)
    return {"endpoint": endpoint, "status": "success", "data": f"Data from {endpoint}"}


def process_data_item(item: Dict) -> Dict:
    """處理數據項"""
    time.sleep(0.1)  # 模擬處理時間
    return {
        "id": item.get("id"),
        "processed": True,
        "value": item.get("value", 0) * 2
    }


def compute_heavy_task(n: int) -> int:
    """計算密集型任務"""
    print(f"  -> 計算任務: n={n}")
    time.sleep(0.3)
    result = sum(i * i for i in range(n))
    return result


async def async_fetch_data(source: str) -> Dict:
    """異步獲取數據"""
    await asyncio.sleep(0.5)  # 模擬異步 I/O
    return {"source": source, "data": f"Data from {source}"}


def demo_parallel_executor():
    """並行執行器示例"""
    print("\n" + "="*60)
    print("示例 1: 並行執行器")
    print("="*60)

    executor = ParallelExecutor(max_workers=3)

    # 提交多個任務
    endpoints = [
        "/api/users",
        "/api/products",
        "/api/orders",
        "/api/analytics",
        "/api/reports"
    ]

    for endpoint in endpoints:
        executor.submit_task(
            name=f"API 調用: {endpoint}",
            func=simulate_api_call,
            endpoint=endpoint,
            delay=0.5
        )

    # 等待完成
    results = executor.wait_all(timeout=10)

    # 顯示結果
    print(f"\n執行結果:")
    for task_id, result in results.items():
        print(f"  {result['name']}: {result['status']}")
        if result['status'] == 'completed':
            print(f"    耗時: {result['duration']:.2f}s")

    # 統計
    stats = executor.get_stats()
    print(f"\n統計: {stats}")

    executor.shutdown()


def demo_task_queue():
    """任務隊列示例"""
    print("\n" + "="*60)
    print("示例 2: 優先級任務隊列")
    print("="*60)

    task_queue = TaskQueue(workers=2)
    task_queue.start()

    # 添加不同優先級的任務
    tasks_data = [
        ("低優先級任務 1", 1, 0.3),
        ("高優先級任務 1", 5, 0.3),
        ("中優先級任務 1", 3, 0.3),
        ("高優先級任務 2", 5, 0.3),
        ("低優先級任務 2", 1, 0.3),
        ("中優先級任務 2", 3, 0.3),
    ]

    for name, priority, delay in tasks_data:
        task = Task(
            id=f"task_{uuid.uuid4().hex[:8]}",
            name=name,
            func=lambda d=delay: time.sleep(d),
            priority=priority
        )
        task_queue.add_task(task)

    # 等待完成
    time.sleep(0.5)  # 讓任務開始執行
    task_queue.wait_completion()

    # 統計
    stats = task_queue.get_stats()
    print(f"\n統計: {stats}")

    task_queue.stop()


def demo_batch_processing():
    """批量處理示例"""
    print("\n" + "="*60)
    print("示例 3: 批量處理")
    print("="*60)

    # 創建測試數據
    items = [{"id": i, "value": i * 10} for i in range(50)]

    # 批量處理
    processor = BatchProcessor(batch_size=10, max_workers=4)
    results = processor.process_batch(
        items=items,
        process_func=process_data_item,
        show_progress=True
    )

    # 顯示部分結果
    print(f"\n前 5 個結果:")
    for result in results[:5]:
        print(f"  {result}")


def demo_async_workflow():
    """異步工作流示例"""
    print("\n" + "="*60)
    print("示例 4: 異步工作流")
    print("="*60)

    async def run_async_demo():
        workflow = AsyncWorkflow()

        # 定義異步任務
        tasks = [
            ("獲取用戶數據", async_fetch_data, ("users",)),
            ("獲取產品數據", async_fetch_data, ("products",)),
            ("獲取訂單數據", async_fetch_data, ("orders",)),
        ]

        # 並行執行
        results = await workflow.run_parallel(tasks)

        # 顯示結果
        print(f"\n結果:")
        for i, result in enumerate(results, 1):
            print(f"  任務 {i}: {result}")

    # 運行異步代碼
    asyncio.run(run_async_demo())


def demo_performance_comparison():
    """性能對比示例"""
    print("\n" + "="*60)
    print("示例 5: 性能對比（順序 vs 並行）")
    print("="*60)

    tasks_count = 10
    task_duration = 0.2

    # 順序執行
    print("\n順序執行:")
    start_time = time.time()
    for i in range(tasks_count):
        simulate_api_call(f"/api/task{i}", delay=task_duration)
    sequential_time = time.time() - start_time
    print(f"總耗時: {sequential_time:.2f}s")

    # 並行執行
    print("\n並行執行:")
    start_time = time.time()
    executor = ParallelExecutor(max_workers=5)
    for i in range(tasks_count):
        executor.submit_task(
            name=f"並行任務 {i}",
            func=simulate_api_call,
            endpoint=f"/api/task{i}",
            delay=task_duration
        )
    executor.wait_all()
    parallel_time = time.time() - start_time
    executor.shutdown()
    print(f"總耗時: {parallel_time:.2f}s")

    # 對比
    speedup = sequential_time / parallel_time
    print(f"\n性能對比:")
    print(f"  順序執行: {sequential_time:.2f}s")
    print(f"  並行執行: {parallel_time:.2f}s")
    print(f"  加速比: {speedup:.2f}x")


def demo_mixed_workload():
    """混合工作負載示例"""
    print("\n" + "="*60)
    print("示例 6: 混合工作負載")
    print("="*60)

    executor = ParallelExecutor(max_workers=4)

    # 提交不同類型的任務
    print("\n提交混合任務...")

    # API 調用任務
    for i in range(3):
        executor.submit_task(
            name=f"API 調用 {i+1}",
            func=simulate_api_call,
            endpoint=f"/api/endpoint{i+1}",
            priority=3
        )

    # 計算任務
    for i in range(3):
        executor.submit_task(
            name=f"計算任務 {i+1}",
            func=compute_heavy_task,
            n=1000 * (i+1),
            priority=2
        )

    # 數據處理任務
    for i in range(4):
        executor.submit_task(
            name=f"數據處理 {i+1}",
            func=process_data_item,
            item={"id": i, "value": i * 100},
            priority=1
        )

    # 等待並顯示進度
    print("\n執行中...")
    time.sleep(0.5)

    while executor.get_completed_count() < len(executor.tasks):
        stats = executor.get_stats()
        print(f"  進度: {stats['completed']}/{stats['total']} 完成")
        time.sleep(0.5)

    results = executor.wait_all()

    print(f"\n最終統計:")
    stats = executor.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    executor.shutdown()


def main():
    """主函數"""
    print("="*60)
    print("Julep 並行執行示例")
    print("="*60)

    try:
        demo_parallel_executor()
        demo_task_queue()
        demo_batch_processing()
        demo_async_workflow()
        demo_performance_comparison()
        demo_mixed_workload()

        print("\n" + "="*60)
        print("所有示例執行完成！")
        print("="*60)

    except Exception as e:
        print(f"\n[ERROR] 執行出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
