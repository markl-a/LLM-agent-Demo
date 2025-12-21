"""
Dify 數據處理範例
================

本範例展示如何使用 Dify 進行數據處理和轉換。

數據處理功能：
1. 批量數據處理
2. 數據轉換和清洗
3. 結構化數據提取
4. 數據導入導出

安裝依賴：
pip install requests pandas
"""

import os
import json
import requests
import csv
import io
from typing import Dict, Any, Optional, List, Generator
from dataclasses import dataclass
from datetime import datetime

# ============================================================
# 配置
# ============================================================

DIFY_API_KEY = os.getenv("DIFY_API_KEY", "app-xxxxxxxxxxxxxxxx")
DIFY_BASE_URL = os.getenv("DIFY_BASE_URL", "https://api.dify.ai/v1")


# ============================================================
# 數據處理客戶端
# ============================================================

class DifyDataProcessor:
    """
    Dify 數據處理器

    提供批量數據處理和轉換功能
    """

    def __init__(self, api_key: str, base_url: str = "https://api.dify.ai/v1"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def process_single(
        self,
        inputs: Dict[str, Any],
        user: str = "default-user"
    ) -> Dict[str, Any]:
        """
        處理單條數據

        Args:
            inputs: 輸入數據
            user: 用戶標識

        Returns:
            處理結果
        """
        url = f"{self.base_url}/completion-messages"

        payload = {
            "inputs": inputs,
            "user": user,
            "response_mode": "blocking"
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()

        return response.json()

    def process_batch(
        self,
        data_list: List[Dict[str, Any]],
        user: str = "default-user",
        batch_size: int = 10,
        on_progress: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        批量處理數據

        Args:
            data_list: 數據列表
            user: 用戶標識
            batch_size: 批次大小
            on_progress: 進度回調函數

        Returns:
            處理結果列表
        """
        results = []
        total = len(data_list)

        for i, data in enumerate(data_list):
            try:
                result = self.process_single(inputs=data, user=user)
                results.append({
                    "index": i,
                    "status": "success",
                    "input": data,
                    "output": result.get('answer', '')
                })
            except Exception as e:
                results.append({
                    "index": i,
                    "status": "error",
                    "input": data,
                    "error": str(e)
                })

            if on_progress:
                on_progress(i + 1, total)

        return results

    def extract_structured_data(
        self,
        text: str,
        schema: Dict[str, Any],
        user: str = "default-user"
    ) -> Dict[str, Any]:
        """
        從文本中提取結構化數據

        Args:
            text: 輸入文本
            schema: 數據結構定義
            user: 用戶標識

        Returns:
            結構化數據
        """
        prompt_inputs = {
            "text": text,
            "schema": json.dumps(schema, ensure_ascii=False)
        }

        result = self.process_single(inputs=prompt_inputs, user=user)

        # 嘗試解析 JSON 輸出
        answer = result.get('answer', '')
        try:
            # 提取 JSON 部分
            json_start = answer.find('{')
            json_end = answer.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(answer[json_start:json_end])
        except json.JSONDecodeError:
            pass

        return {"raw_output": answer}


# ============================================================
# 數據轉換工具
# ============================================================

class DataTransformer:
    """
    數據轉換器

    提供各種數據格式轉換功能
    """

    @staticmethod
    def csv_to_records(csv_content: str) -> List[Dict[str, str]]:
        """
        CSV 轉換為記錄列表

        Args:
            csv_content: CSV 內容

        Returns:
            記錄列表
        """
        reader = csv.DictReader(io.StringIO(csv_content))
        return list(reader)

    @staticmethod
    def records_to_csv(records: List[Dict[str, Any]]) -> str:
        """
        記錄列表轉換為 CSV

        Args:
            records: 記錄列表

        Returns:
            CSV 內容
        """
        if not records:
            return ""

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

        return output.getvalue()

    @staticmethod
    def flatten_nested_dict(
        nested_dict: Dict[str, Any],
        parent_key: str = "",
        separator: str = "_"
    ) -> Dict[str, Any]:
        """
        扁平化嵌套字典

        Args:
            nested_dict: 嵌套字典
            parent_key: 父鍵
            separator: 分隔符

        Returns:
            扁平化字典
        """
        items = []
        for key, value in nested_dict.items():
            new_key = f"{parent_key}{separator}{key}" if parent_key else key
            if isinstance(value, dict):
                items.extend(
                    DataTransformer.flatten_nested_dict(
                        value, new_key, separator
                    ).items()
                )
            else:
                items.append((new_key, value))
        return dict(items)

    @staticmethod
    def group_by(
        records: List[Dict[str, Any]],
        key: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        按鍵分組

        Args:
            records: 記錄列表
            key: 分組鍵

        Returns:
            分組結果
        """
        groups = {}
        for record in records:
            group_key = record.get(key, "unknown")
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(record)
        return groups


# ============================================================
# 批量處理任務
# ============================================================

@dataclass
class BatchJob:
    """批量處理任務"""
    id: str
    status: str  # pending, running, completed, failed
    total: int
    processed: int
    results: List[Dict[str, Any]]
    created_at: datetime
    completed_at: Optional[datetime] = None


class BatchProcessor:
    """
    批量處理器

    管理和執行批量數據處理任務
    """

    def __init__(self, client: DifyDataProcessor):
        self.client = client
        self.jobs: Dict[str, BatchJob] = {}
        self._job_counter = 0

    def create_job(
        self,
        data_list: List[Dict[str, Any]]
    ) -> str:
        """
        創建批量處理任務

        Args:
            data_list: 數據列表

        Returns:
            任務 ID
        """
        self._job_counter += 1
        job_id = f"batch_{self._job_counter}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        job = BatchJob(
            id=job_id,
            status="pending",
            total=len(data_list),
            processed=0,
            results=[],
            created_at=datetime.now()
        )

        self.jobs[job_id] = job
        return job_id

    def run_job(
        self,
        job_id: str,
        data_list: List[Dict[str, Any]],
        user: str = "default-user"
    ) -> BatchJob:
        """
        執行批量處理任務

        Args:
            job_id: 任務 ID
            data_list: 數據列表
            user: 用戶標識

        Returns:
            任務對象
        """
        if job_id not in self.jobs:
            raise ValueError(f"任務不存在: {job_id}")

        job = self.jobs[job_id]
        job.status = "running"

        def progress_callback(processed: int, total: int):
            job.processed = processed
            print(f"\r處理進度: {processed}/{total}", end="", flush=True)

        try:
            results = self.client.process_batch(
                data_list=data_list,
                user=user,
                on_progress=progress_callback
            )

            job.results = results
            job.status = "completed"
            job.completed_at = datetime.now()

        except Exception as e:
            job.status = "failed"
            job.results = [{"error": str(e)}]

        print()  # 換行
        return job

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """獲取任務狀態"""
        if job_id not in self.jobs:
            return {"error": "任務不存在"}

        job = self.jobs[job_id]
        return {
            "id": job.id,
            "status": job.status,
            "progress": f"{job.processed}/{job.total}",
            "created_at": job.created_at.isoformat(),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None
        }


# ============================================================
# 使用範例
# ============================================================

def example_single_processing():
    """
    範例 1: 單條數據處理

    展示處理單條數據
    """
    print("=" * 50)
    print("範例 1: 單條數據處理")
    print("=" * 50)

    processor = DifyDataProcessor(
        api_key=DIFY_API_KEY,
        base_url=DIFY_BASE_URL
    )

    try:
        # 假設有一個文本摘要應用
        result = processor.process_single(
            inputs={
                "text": """
                人工智能（AI）是計算機科學的一個分支，
                致力於創建能夠執行需要人類智能的任務的系統。
                這包括學習、推理、問題解決、感知和語言理解。
                近年來，深度學習技術的突破使得 AI 取得了顯著進展。
                """
            }
        )

        print(f"處理結果: {result.get('answer', '')}")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_batch_processing():
    """
    範例 2: 批量數據處理

    展示處理多條數據
    """
    print("\n" + "=" * 50)
    print("範例 2: 批量數據處理")
    print("=" * 50)

    processor = DifyDataProcessor(
        api_key=DIFY_API_KEY,
        base_url=DIFY_BASE_URL
    )

    # 準備批量數據
    data_list = [
        {"text": "這是第一條需要處理的文本"},
        {"text": "這是第二條需要處理的文本"},
        {"text": "這是第三條需要處理的文本"},
    ]

    try:
        results = processor.process_batch(
            data_list=data_list,
            on_progress=lambda p, t: print(f"\r進度: {p}/{t}", end="")
        )

        print("\n\n處理結果:")
        for r in results:
            status = "✓" if r['status'] == 'success' else "✗"
            print(f"  {status} 項目 {r['index']}: {r.get('output', r.get('error', ''))[:50]}...")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_structured_extraction():
    """
    範例 3: 結構化數據提取

    從文本中提取結構化信息
    """
    print("\n" + "=" * 50)
    print("範例 3: 結構化數據提取")
    print("=" * 50)

    processor = DifyDataProcessor(
        api_key=DIFY_API_KEY,
        base_url=DIFY_BASE_URL
    )

    # 待提取的文本
    text = """
    產品名稱：智能手表 Pro
    價格：NT$ 12,999
    顏色：黑色、銀色、金色
    特點：
    - 心率監測
    - GPS 定位
    - 防水 50 米
    - 電池續航 7 天
    """

    # 定義提取結構
    schema = {
        "product_name": "string",
        "price": "number",
        "colors": ["string"],
        "features": ["string"]
    }

    try:
        result = processor.extract_structured_data(
            text=text,
            schema=schema
        )

        print("提取結果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_csv_processing():
    """
    範例 4: CSV 數據處理

    處理 CSV 格式數據
    """
    print("\n" + "=" * 50)
    print("範例 4: CSV 數據處理")
    print("=" * 50)

    # 模擬 CSV 數據
    csv_data = """name,description,category
iPhone 15,蘋果最新款智能手機,電子產品
MacBook Pro,專業級筆記本電腦,電腦
AirPods Pro,主動降噪無線耳機,配件"""

    # 轉換為記錄
    records = DataTransformer.csv_to_records(csv_data)

    print("原始記錄:")
    for r in records:
        print(f"  {r}")

    # 按類別分組
    grouped = DataTransformer.group_by(records, "category")

    print("\n按類別分組:")
    for category, items in grouped.items():
        print(f"  {category}:")
        for item in items:
            print(f"    - {item['name']}")


def example_batch_job():
    """
    範例 5: 批量任務管理

    展示批量任務的創建和執行
    """
    print("\n" + "=" * 50)
    print("範例 5: 批量任務管理")
    print("=" * 50)

    processor = DifyDataProcessor(
        api_key=DIFY_API_KEY,
        base_url=DIFY_BASE_URL
    )

    batch = BatchProcessor(processor)

    # 準備數據
    data_list = [
        {"text": f"這是第 {i} 條測試數據"}
        for i in range(5)
    ]

    # 創建任務
    job_id = batch.create_job(data_list)
    print(f"創建任務: {job_id}")

    # 查看狀態
    status = batch.get_job_status(job_id)
    print(f"任務狀態: {status}")

    # 執行任務（模擬）
    print("\n執行任務...")

    # 注意：實際執行需要有效的 API Key
    # job = batch.run_job(job_id, data_list)
    # print(f"完成狀態: {batch.get_job_status(job_id)}")


def example_data_transformation():
    """
    範例 6: 數據轉換

    展示各種數據轉換操作
    """
    print("\n" + "=" * 50)
    print("範例 6: 數據轉換")
    print("=" * 50)

    # 嵌套數據
    nested_data = {
        "user": {
            "name": "John",
            "address": {
                "city": "Taipei",
                "country": "Taiwan"
            }
        },
        "orders": {
            "total": 3,
            "amount": 1500
        }
    }

    # 扁平化
    flat_data = DataTransformer.flatten_nested_dict(nested_data)

    print("嵌套數據:")
    print(json.dumps(nested_data, indent=2, ensure_ascii=False))

    print("\n扁平化後:")
    print(json.dumps(flat_data, indent=2, ensure_ascii=False))


def example_export_results():
    """
    範例 7: 導出處理結果

    展示如何導出處理結果
    """
    print("\n" + "=" * 50)
    print("範例 7: 導出處理結果")
    print("=" * 50)

    # 模擬處理結果
    results = [
        {"id": 1, "input": "文本1", "output": "處理結果1", "status": "success"},
        {"id": 2, "input": "文本2", "output": "處理結果2", "status": "success"},
        {"id": 3, "input": "文本3", "output": "處理結果3", "status": "success"},
    ]

    # 導出為 CSV
    csv_output = DataTransformer.records_to_csv(results)

    print("CSV 輸出:")
    print(csv_output)

    # 導出為 JSON
    json_output = json.dumps(results, indent=2, ensure_ascii=False)

    print("JSON 輸出:")
    print(json_output)


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    print("Dify 數據處理範例")
    print("請確保已設置 DIFY_API_KEY 環境變數")
    print()

    example_single_processing()
    example_batch_processing()
    example_structured_extraction()
    example_csv_processing()
    example_batch_job()
    example_data_transformation()
    example_export_results()
