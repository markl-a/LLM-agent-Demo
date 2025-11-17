#!/usr/bin/env python3
"""
批量處理示例
============

這個示例展示如何高效地處理大量潛在客戶：
- 並行處理
- 錯誤處理和重試
- 進度追蹤
- 性能優化

運行方式：
    python examples/batch_processing.py
"""

import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

# 加載環境變數
load_dotenv()


# ===== 數據類 =====

@dataclass
class Lead:
    """潛在客戶數據類"""
    id: str
    name: str
    email: str
    company: str
    position: str = ""
    status: str = "pending"


@dataclass
class ProcessResult:
    """處理結果"""
    lead_id: str
    success: bool
    error_message: Optional[str] = None
    processing_time: float = 0.0
    retry_count: int = 0


# ===== 批量處理器 =====

class BatchProcessor:
    """批量處理器"""

    def __init__(self, max_workers: int = 5, max_retries: int = 3):
        """
        初始化批量處理器

        Args:
            max_workers: 最大並行工作數
            max_retries: 最大重試次數
        """
        self.max_workers = max_workers
        self.max_retries = max_retries

        self.results: List[ProcessResult] = []
        self.start_time: Optional[float] = None

    def process_single_lead(self, lead: Lead, retry_count: int = 0) -> ProcessResult:
        """
        處理單個潛在客戶

        Args:
            lead: 客戶數據
            retry_count: 當前重試次數

        Returns:
            ProcessResult: 處理結果
        """
        start_time = time.time()

        try:
            # 模擬處理過程
            self._simulate_processing(lead)

            # 成功
            return ProcessResult(
                lead_id=lead.id,
                success=True,
                processing_time=time.time() - start_time,
                retry_count=retry_count
            )

        except Exception as e:
            # 失敗 - 檢查是否需要重試
            if retry_count < self.max_retries:
                print(f"⚠️  {lead.name} 處理失敗，重試 ({retry_count + 1}/{self.max_retries})")
                time.sleep(2 ** retry_count)  # 指數退避
                return self.process_single_lead(lead, retry_count + 1)
            else:
                return ProcessResult(
                    lead_id=lead.id,
                    success=False,
                    error_message=str(e),
                    processing_time=time.time() - start_time,
                    retry_count=retry_count
                )

    def _simulate_processing(self, lead: Lead):
        """
        模擬處理流程

        實際應用中，這裡會：
        1. 研究客戶
        2. 生成郵件
        3. 發送郵件
        4. 更新 CRM
        """
        # 模擬耗時操作
        time.sleep(0.5)

        # 模擬 10% 的失敗率
        import random
        if random.random() < 0.1:
            raise Exception("模擬的隨機錯誤")

        print(f"✅ {lead.name} ({lead.company}) - 處理完成")

    def process_batch(self, leads: List[Lead]) -> List[ProcessResult]:
        """
        批量處理潛在客戶（並行）

        Args:
            leads: 客戶列表

        Returns:
            List[ProcessResult]: 處理結果列表
        """
        print(f"\n🚀 開始批量處理 {len(leads)} 個客戶")
        print(f"   並行工作數: {self.max_workers}")
        print(f"   最大重試次數: {self.max_retries}\n")

        self.start_time = time.time()
        self.results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任務
            future_to_lead = {
                executor.submit(self.process_single_lead, lead): lead
                for lead in leads
            }

            # 收集結果（帶進度顯示）
            completed = 0
            total = len(leads)

            for future in as_completed(future_to_lead):
                lead = future_to_lead[future]

                try:
                    result = future.result()
                    self.results.append(result)

                    completed += 1
                    self._print_progress(completed, total)

                except Exception as e:
                    print(f"❌ {lead.name} 發生未預期錯誤: {e}")
                    self.results.append(ProcessResult(
                        lead_id=lead.id,
                        success=False,
                        error_message=f"未預期錯誤: {str(e)}"
                    ))

        return self.results

    def _print_progress(self, completed: int, total: int):
        """打印進度"""
        percentage = (completed / total) * 100
        bar_length = 40
        filled_length = int(bar_length * completed // total)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)

        elapsed_time = time.time() - self.start_time
        avg_time = elapsed_time / completed
        eta = avg_time * (total - completed)

        print(f"\r進度: |{bar}| {completed}/{total} ({percentage:.1f}%) "
              f"ETA: {eta:.1f}s", end='', flush=True)

        if completed == total:
            print()  # 換行

    def generate_report(self) -> Dict:
        """
        生成處理報告

        Returns:
            Dict: 包含統計信息的報告
        """
        if not self.results:
            return {}

        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]

        total_time = time.time() - self.start_time if self.start_time else 0
        avg_time = sum(r.processing_time for r in self.results) / len(self.results)

        report = {
            'total': len(self.results),
            'successful': len(successful),
            'failed': len(failed),
            'success_rate': len(successful) / len(self.results) * 100,
            'total_time': total_time,
            'average_time_per_lead': avg_time,
            'throughput': len(self.results) / total_time if total_time > 0 else 0,
        }

        return report

    def print_report(self):
        """打印報告"""
        report = self.generate_report()

        if not report:
            print("沒有處理結果")
            return

        print("\n" + "=" * 70)
        print("處理報告")
        print("=" * 70)
        print(f"總計:           {report['total']} 個客戶")
        print(f"成功:           {report['successful']} ({report['success_rate']:.1f}%)")
        print(f"失敗:           {report['failed']}")
        print(f"總耗時:         {report['total_time']:.2f} 秒")
        print(f"平均耗時:       {report['average_time_per_lead']:.2f} 秒/客戶")
        print(f"吞吐量:         {report['throughput']:.2f} 客戶/秒")
        print("=" * 70 + "\n")

        # 顯示失敗的客戶
        failed_results = [r for r in self.results if not r.success]
        if failed_results:
            print("失敗的客戶:")
            for result in failed_results:
                print(f"  - ID: {result.lead_id}")
                print(f"    錯誤: {result.error_message}")
                print(f"    重試次數: {result.retry_count}\n")


# ===== 智能批次處理器 =====

class SmartBatchProcessor(BatchProcessor):
    """
    智能批次處理器

    根據系統性能動態調整批次大小
    """

    def __init__(self, initial_batch_size: int = 10, **kwargs):
        """
        初始化智能批次處理器

        Args:
            initial_batch_size: 初始批次大小
            **kwargs: 傳遞給父類的參數
        """
        super().__init__(**kwargs)
        self.batch_size = initial_batch_size

    def process_in_smart_batches(self, leads: List[Lead]) -> List[ProcessResult]:
        """
        智能批次處理

        根據處理速度動態調整批次大小
        """
        print(f"\n🧠 智能批次處理模式")
        print(f"   初始批次大小: {self.batch_size}\n")

        all_results = []
        processed = 0
        total = len(leads)

        while processed < total:
            # 獲取當前批次
            batch = leads[processed:processed + self.batch_size]

            print(f"\n批次 {processed // self.batch_size + 1}: "
                  f"{len(batch)} 個客戶（批次大小: {self.batch_size}）")

            # 處理批次
            batch_start = time.time()
            batch_results = self.process_batch(batch)
            batch_time = time.time() - batch_start

            all_results.extend(batch_results)
            processed += len(batch)

            # 動態調整批次大小
            self._adjust_batch_size(batch_time, len(batch))

        self.results = all_results
        return all_results

    def _adjust_batch_size(self, batch_time: float, batch_size: int):
        """
        根據處理時間調整批次大小

        Args:
            batch_time: 批次處理時間
            batch_size: 當前批次大小
        """
        target_time = 10.0  # 目標處理時間（秒）
        min_batch_size = 5
        max_batch_size = 50

        # 如果太快，增加批次大小
        if batch_time < target_time * 0.5:
            new_size = min(int(batch_size * 1.5), max_batch_size)
            print(f"   ⚡ 處理速度快，增加批次大小: {batch_size} → {new_size}")
            self.batch_size = new_size

        # 如果太慢，減少批次大小
        elif batch_time > target_time * 1.5:
            new_size = max(int(batch_size * 0.7), min_batch_size)
            print(f"   🐌 處理速度慢，減少批次大小: {batch_size} → {new_size}")
            self.batch_size = new_size
        else:
            print(f"   👍 批次大小合適，保持: {batch_size}")


# ===== 主函數 =====

def generate_mock_leads(count: int = 50) -> List[Lead]:
    """
    生成模擬的潛在客戶數據

    Args:
        count: 生成的客戶數量

    Returns:
        List[Lead]: 客戶列表
    """
    companies = ['TechCorp', 'DataInc', 'CloudSolutions', 'AIStartup', 'DevTools']
    positions = ['CEO', 'CTO', 'VP Engineering', 'Director', 'Manager']

    leads = []
    for i in range(count):
        import random
        leads.append(Lead(
            id=str(i + 1),
            name=f"Lead {i + 1}",
            email=f"lead{i + 1}@example.com",
            company=random.choice(companies),
            position=random.choice(positions)
        ))

    return leads


def main():
    """主函數"""

    print("\n" + "=" * 70)
    print("批量處理示例")
    print("=" * 70)

    # 生成測試數據
    num_leads = 50
    print(f"\n📋 生成 {num_leads} 個測試客戶...")
    leads = generate_mock_leads(num_leads)
    print(f"✅ 測試數據已生成\n")

    # 選擇處理模式
    print("選擇處理模式:")
    print("1. 標準並行處理")
    print("2. 智能批次處理")

    # 這裡簡化為直接使用智能批次處理
    mode = 2

    if mode == 1:
        # 標準並行處理
        processor = BatchProcessor(max_workers=5, max_retries=2)
        processor.process_batch(leads)
    else:
        # 智能批次處理
        processor = SmartBatchProcessor(
            initial_batch_size=10,
            max_workers=5,
            max_retries=2
        )
        processor.process_in_smart_batches(leads)

    # 打印報告
    processor.print_report()

    # 保存結果到文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"batch_report_{timestamp}.txt"

    with open(report_file, 'w', encoding='utf-8') as f:
        report = processor.generate_report()
        f.write("批量處理報告\n")
        f.write("=" * 50 + "\n")
        f.write(f"生成時間: {datetime.now()}\n\n")

        for key, value in report.items():
            f.write(f"{key}: {value}\n")

    print(f"📄 報告已保存到: {report_file}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  程式被用戶中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
