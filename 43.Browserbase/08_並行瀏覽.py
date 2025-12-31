"""
Browserbase 並行瀏覽示例
========================

本模塊展示了如何使用 Browserbase 進行並行瀏覽器操作。
包括多 Session 並發、任務隊列、資源管理、性能優化等。

主要內容:
1. 並發 Session 管理
2. 任務隊列處理
3. 線程池和進程池
4. 資源限制和控制
5. 錯誤處理和重試
6. 性能監控和優化

作者: Browserbase 示例團隊
日期: 2025-12-31
"""

import os
import time
import asyncio
import threading
import queue
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from collections import defaultdict
from dotenv import load_dotenv


# 加載環境變量
load_dotenv()


class TaskStatus(Enum):
    """任務狀態"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BrowserTask:
    """瀏覽器任務"""
    id: str
    url: str
    action: Callable
    priority: int = 0
    retry_count: int = 0
    max_retries: int = 3
    timeout: float = 30.0
    metadata: Dict = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def get_duration(self) -> Optional[float]:
        """獲取執行時長"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


class ParallelBrowserManager:
    """
    並行瀏覽器管理器

    管理多個並發的瀏覽器 Session。
    """

    def __init__(
        self,
        max_workers: int = 5,
        max_sessions: int = 10
    ):
        """
        初始化並行管理器

        Args:
            max_workers: 最大工作線程數
            max_sessions: 最大 Session 數
        """
        self.max_workers = max_workers
        self.max_sessions = max_sessions
        self.active_sessions = {}
        self.session_lock = threading.Lock()
        self.stats = defaultdict(int)

        print(f"[ParallelBrowserManager] 初始化完成")
        print(f"  - 最大工作線程: {max_workers}")
        print(f"  - 最大 Session: {max_sessions}")

    def create_session(self, session_id: str) -> Dict:
        """
        創建 Session

        Args:
            session_id: Session ID

        Returns:
            Session 信息
        """
        with self.session_lock:
            if len(self.active_sessions) >= self.max_sessions:
                raise RuntimeError("Session 數量已達上限")

            session = {
                "id": session_id,
                "created_at": datetime.now(),
                "task_count": 0
            }

            self.active_sessions[session_id] = session
            self.stats['total_sessions_created'] += 1

            print(f"[ParallelBrowserManager] 創建 Session: {session_id}")
            return session

    def get_or_create_session(self, task_id: str) -> Dict:
        """獲取或創建 Session"""
        session_id = f"session_{task_id}"

        if session_id not in self.active_sessions:
            return self.create_session(session_id)

        return self.active_sessions[session_id]

    def release_session(self, session_id: str):
        """釋放 Session"""
        with self.session_lock:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                print(f"[ParallelBrowserManager] 釋放 Session: {session_id}")

    def execute_task(self, task: BrowserTask) -> BrowserTask:
        """
        執行單個任務

        Args:
            task: 瀏覽器任務

        Returns:
            完成的任務
        """
        task.start_time = datetime.now()
        task.status = TaskStatus.RUNNING

        print(f"\n[執行任務] {task.id}")
        print(f"  URL: {task.url}")
        print(f"  優先級: {task.priority}")

        try:
            # 獲取 Session
            session = self.get_or_create_session(task.id)
            session['task_count'] += 1

            # 執行任務
            result = task.action(task.url, task.metadata)

            # 標記完成
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.end_time = datetime.now()

            self.stats['tasks_completed'] += 1

            duration = task.get_duration()
            print(f"  ✓ 完成 (耗時: {duration:.2f}秒)")

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.end_time = datetime.now()

            self.stats['tasks_failed'] += 1

            print(f"  ✗ 失敗: {str(e)}")

            # 重試邏輯
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                print(f"  準備重試 ({task.retry_count}/{task.max_retries})")

        finally:
            # 清理
            session_id = f"session_{task.id}"
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                if session['task_count'] <= 1:
                    self.release_session(session_id)

        return task

    def execute_parallel(
        self,
        tasks: List[BrowserTask],
        use_threads: bool = True
    ) -> List[BrowserTask]:
        """
        並行執行多個任務

        Args:
            tasks: 任務列表
            use_threads: 使用線程池（True）或進程池（False）

        Returns:
            完成的任務列表
        """
        print(f"\n[ParallelBrowserManager] 並行執行 {len(tasks)} 個任務")
        print(f"  使用: {'線程池' if use_threads else '進程池'}")
        print("=" * 60)

        # 選擇執行器
        ExecutorClass = ThreadPoolExecutor if use_threads else ProcessPoolExecutor

        results = []

        with ExecutorClass(max_workers=self.max_workers) as executor:
            # 提交所有任務
            future_to_task = {
                executor.submit(self.execute_task, task): task
                for task in tasks
            }

            # 收集結果
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    completed_task = future.result()
                    results.append(completed_task)
                except Exception as e:
                    print(f"[錯誤] 任務 {task.id} 異常: {str(e)}")
                    task.status = TaskStatus.FAILED
                    task.error = str(e)
                    results.append(task)

        print("\n" + "=" * 60)
        print(f"並行執行完成:")

        # 統計
        completed = sum(1 for t in results if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in results if t.status == TaskStatus.FAILED)

        print(f"  - 成功: {completed}")
        print(f"  - 失敗: {failed}")
        print(f"  - 總計: {len(results)}")
        print("=" * 60 + "\n")

        return results


class TaskQueue:
    """
    任務隊列

    管理待執行的瀏覽器任務。
    """

    def __init__(self, max_size: int = 100):
        """
        初始化任務隊列

        Args:
            max_size: 最大隊列大小
        """
        self.queue = queue.PriorityQueue(maxsize=max_size)
        self.completed_tasks = []
        self.task_count = 0
        print(f"[TaskQueue] 初始化完成 (最大大小: {max_size})")

    def add_task(self, task: BrowserTask):
        """
        添加任務到隊列

        Args:
            task: 瀏覽器任務
        """
        # 優先隊列使用負數使高優先級排在前面
        self.queue.put((-task.priority, self.task_count, task))
        self.task_count += 1
        print(f"[TaskQueue] 添加任務: {task.id} (優先級: {task.priority})")

    def add_tasks(self, tasks: List[BrowserTask]):
        """批量添加任務"""
        for task in tasks:
            self.add_task(task)

    def get_task(self, timeout: Optional[float] = None) -> Optional[BrowserTask]:
        """
        獲取下一個任務

        Args:
            timeout: 超時時間

        Returns:
            任務對象
        """
        try:
            _, _, task = self.queue.get(timeout=timeout)
            return task
        except queue.Empty:
            return None

    def size(self) -> int:
        """獲取隊列大小"""
        return self.queue.qsize()

    def is_empty(self) -> bool:
        """檢查隊列是否為空"""
        return self.queue.empty()


class TaskWorker:
    """
    任務工作器

    從隊列中取任務並執行。
    """

    def __init__(
        self,
        worker_id: int,
        task_queue: TaskQueue,
        manager: ParallelBrowserManager
    ):
        """
        初始化工作器

        Args:
            worker_id: 工作器 ID
            task_queue: 任務隊列
            manager: 瀏覽器管理器
        """
        self.worker_id = worker_id
        self.task_queue = task_queue
        self.manager = manager
        self.is_running = False
        self.tasks_processed = 0
        print(f"[Worker-{worker_id}] 初始化完成")

    def start(self):
        """啟動工作器"""
        self.is_running = True
        print(f"[Worker-{self.worker_id}] 啟動")

        while self.is_running:
            # 從隊列獲取任務
            task = self.task_queue.get_task(timeout=1.0)

            if task is None:
                if self.task_queue.is_empty():
                    print(f"[Worker-{self.worker_id}] 隊列為空，等待...")
                continue

            # 執行任務
            print(f"[Worker-{self.worker_id}] 處理任務: {task.id}")
            completed_task = self.manager.execute_task(task)

            self.task_queue.completed_tasks.append(completed_task)
            self.tasks_processed += 1

        print(f"[Worker-{self.worker_id}] 停止 (已處理 {self.tasks_processed} 個任務)")

    def stop(self):
        """停止工作器"""
        self.is_running = False


class ResourceMonitor:
    """
    資源監控器

    監控並行執行的資源使用情況。
    """

    def __init__(self):
        """初始化監控器"""
        self.metrics = defaultdict(list)
        self.start_time = None
        print("[ResourceMonitor] 初始化完成")

    def start_monitoring(self):
        """開始監控"""
        self.start_time = time.time()
        print("[ResourceMonitor] 開始監控")

    def record_metric(self, name: str, value: float):
        """
        記錄指標

        Args:
            name: 指標名稱
            value: 指標值
        """
        timestamp = time.time() - (self.start_time or 0)
        self.metrics[name].append((timestamp, value))

    def get_statistics(self) -> Dict:
        """獲取統計信息"""
        stats = {}

        for name, values in self.metrics.items():
            if values:
                metric_values = [v for _, v in values]
                stats[name] = {
                    "count": len(metric_values),
                    "min": min(metric_values),
                    "max": max(metric_values),
                    "avg": sum(metric_values) / len(metric_values),
                    "total": sum(metric_values)
                }

        return stats

    def print_statistics(self):
        """打印統計信息"""
        print("\n[ResourceMonitor] 性能統計:")
        print("=" * 60)

        stats = self.get_statistics()

        for name, metric_stats in stats.items():
            print(f"\n{name}:")
            for key, value in metric_stats.items():
                if isinstance(value, float):
                    print(f"  - {key}: {value:.2f}")
                else:
                    print(f"  - {key}: {value}")

        print("=" * 60 + "\n")


class RateLimiter:
    """
    速率限制器

    控制任務執行速率。
    """

    def __init__(self, max_requests_per_second: int = 10):
        """
        初始化速率限制器

        Args:
            max_requests_per_second: 每秒最大請求數
        """
        self.max_requests = max_requests_per_second
        self.min_interval = 1.0 / max_requests_per_second
        self.last_request_time = 0
        self.lock = threading.Lock()
        print(f"[RateLimiter] 初始化 (最大速率: {max_requests_per_second} req/s)")

    def acquire(self):
        """獲取執行許可"""
        with self.lock:
            now = time.time()
            elapsed = now - self.last_request_time

            if elapsed < self.min_interval:
                sleep_time = self.min_interval - elapsed
                time.sleep(sleep_time)

            self.last_request_time = time.time()

    def wait(self):
        """等待（別名）"""
        self.acquire()


# 示例任務函數

def scrape_page(url: str, metadata: Dict) -> Dict:
    """爬取頁面"""
    time.sleep(0.5)  # 模擬網絡請求
    return {
        "url": url,
        "title": f"頁面標題 - {url}",
        "content_length": len(url) * 100,
        "timestamp": datetime.now().isoformat()
    }


def check_page_status(url: str, metadata: Dict) -> Dict:
    """檢查頁面狀態"""
    time.sleep(0.2)  # 模擬請求
    return {
        "url": url,
        "status_code": 200,
        "response_time": 0.2
    }


def example_parallel_execution():
    """示例1: 並行執行任務"""
    print("\n" + "=" * 60)
    print("示例1: 並行執行任務")
    print("=" * 60 + "\n")

    manager = ParallelBrowserManager(max_workers=3, max_sessions=5)

    # 創建任務
    tasks = []
    for i in range(10):
        task = BrowserTask(
            id=f"task_{i + 1}",
            url=f"https://example.com/page/{i + 1}",
            action=scrape_page,
            priority=i % 3  # 不同優先級
        )
        tasks.append(task)

    # 並行執行
    results = manager.execute_parallel(tasks)

    # 顯示結果
    print("\n執行結果:")
    for task in results:
        status_icon = "✓" if task.status == TaskStatus.COMPLETED else "✗"
        duration = task.get_duration() or 0
        print(f"  {status_icon} {task.id}: {task.status.value} ({duration:.2f}s)")


def example_task_queue():
    """示例2: 任務隊列處理"""
    print("\n" + "=" * 60)
    print("示例2: 任務隊列處理")
    print("=" * 60 + "\n")

    # 創建組件
    task_queue = TaskQueue(max_size=50)
    manager = ParallelBrowserManager(max_workers=2)

    # 添加任務
    for i in range(8):
        task = BrowserTask(
            id=f"queue_task_{i + 1}",
            url=f"https://example.com/item/{i + 1}",
            action=scrape_page,
            priority=3 - (i % 3)  # 高優先級的先執行
        )
        task_queue.add_task(task)

    print(f"\n隊列大小: {task_queue.size()}")

    # 創建工作器
    workers = []
    for i in range(2):
        worker = TaskWorker(i + 1, task_queue, manager)
        workers.append(worker)

    # 在線程中啟動工作器
    threads = []
    for worker in workers:
        thread = threading.Thread(target=worker.start)
        thread.start()
        threads.append(thread)

    # 等待隊列清空
    print("\n等待任務完成...")
    time.sleep(5)

    # 停止工作器
    for worker in workers:
        worker.stop()

    for thread in threads:
        thread.join(timeout=1)

    print(f"\n已完成任務: {len(task_queue.completed_tasks)}")


def example_rate_limiting():
    """示例3: 速率限制"""
    print("\n" + "=" * 60)
    print("示例3: 速率限制")
    print("=" * 60 + "\n")

    limiter = RateLimiter(max_requests_per_second=5)

    print("執行10個請求（限制 5 req/s）:")

    start_time = time.time()

    for i in range(10):
        limiter.acquire()
        print(f"  請求 {i + 1} - {time.time() - start_time:.2f}s")

    total_time = time.time() - start_time
    actual_rate = 10 / total_time

    print(f"\n總耗時: {total_time:.2f}秒")
    print(f"實際速率: {actual_rate:.2f} req/s")


def example_resource_monitoring():
    """示例4: 資源監控"""
    print("\n" + "=" * 60)
    print("示例4: 資源監控")
    print("=" * 60 + "\n")

    monitor = ResourceMonitor()
    monitor.start_monitoring()

    manager = ParallelBrowserManager(max_workers=3)

    # 創建任務
    tasks = []
    for i in range(6):
        task = BrowserTask(
            id=f"monitor_task_{i + 1}",
            url=f"https://example.com/page/{i + 1}",
            action=scrape_page
        )
        tasks.append(task)

    # 執行並監控
    results = manager.execute_parallel(tasks)

    # 記錄指標
    for task in results:
        if task.status == TaskStatus.COMPLETED:
            duration = task.get_duration()
            if duration:
                monitor.record_metric("task_duration", duration)

    monitor.record_metric("tasks_completed", len([t for t in results if t.status == TaskStatus.COMPLETED]))
    monitor.record_metric("tasks_failed", len([t for t in results if t.status == TaskStatus.FAILED]))

    # 顯示統計
    monitor.print_statistics()


def example_error_handling():
    """示例5: 錯誤處理和重試"""
    print("\n" + "=" * 60)
    print("示例5: 錯誤處理和重試")
    print("=" * 60 + "\n")

    def failing_action(url: str, metadata: Dict) -> Dict:
        """會失敗的動作"""
        import random
        if random.random() < 0.5:  # 50% 失敗率
            raise Exception("隨機錯誤")
        return {"url": url, "success": True}

    manager = ParallelBrowserManager(max_workers=2)

    # 創建任務（帶重試）
    tasks = []
    for i in range(5):
        task = BrowserTask(
            id=f"retry_task_{i + 1}",
            url=f"https://example.com/page/{i + 1}",
            action=failing_action,
            max_retries=2
        )
        tasks.append(task)

    # 執行
    results = manager.execute_parallel(tasks)

    # 統計
    print("\n結果統計:")
    completed = sum(1 for t in results if t.status == TaskStatus.COMPLETED)
    failed = sum(1 for t in results if t.status == TaskStatus.FAILED)
    total_retries = sum(t.retry_count for t in results)

    print(f"  - 成功: {completed}")
    print(f"  - 失敗: {failed}")
    print(f"  - 總重試次數: {total_retries}")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Browserbase 並行瀏覽示例")
    print("=" * 60)

    # 運行所有示例
    example_parallel_execution()
    example_task_queue()
    example_rate_limiting()
    example_resource_monitoring()
    example_error_handling()

    print("\n" + "=" * 60)
    print("所有示例完成！")
    print("=" * 60 + "\n")

    print("最佳實踐:")
    print("- 合理設置並發數量，避免資源耗盡")
    print("- 使用任務隊列管理大量任務")
    print("- 實施速率限制避免被封禁")
    print("- 監控資源使用情況")
    print("- 實現錯誤處理和重試機制")


if __name__ == "__main__":
    main()
