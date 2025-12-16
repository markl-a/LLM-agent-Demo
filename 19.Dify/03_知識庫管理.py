"""
Dify 知識庫管理範例
==================

本範例展示如何使用 Dify 的知識庫（Dataset）功能。

知識庫功能包括：
1. 創建和管理數據集
2. 上傳和處理文檔
3. 文檔分段配置
4. 知識檢索

安裝依賴：
pip install requests
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List, BinaryIO
from dataclasses import dataclass
from enum import Enum

# ============================================================
# 配置
# ============================================================

# 注意：知識庫 API 使用 Dataset API Key，不是應用 API Key
DIFY_DATASET_API_KEY = os.getenv("DIFY_DATASET_API_KEY", "dataset-xxxxxxxxxxxxxxxx")
DIFY_BASE_URL = os.getenv("DIFY_BASE_URL", "https://api.dify.ai/v1")


# ============================================================
# 枚舉類型
# ============================================================

class IndexingTechnique(Enum):
    """索引技術"""
    HIGH_QUALITY = "high_quality"  # 高質量模式（使用 embedding）
    ECONOMY = "economy"  # 經濟模式（使用關鍵詞）


class DocType(Enum):
    """文檔類型"""
    TXT = "txt"
    MARKDOWN = "markdown"
    PDF = "pdf"
    HTML = "html"
    XLSX = "xlsx"
    DOCX = "docx"
    CSV = "csv"


class DocForm(Enum):
    """文檔形式"""
    TEXT_MODEL = "text_model"  # 文本模式
    QA_MODEL = "qa_model"  # 問答對模式


# ============================================================
# 知識庫客戶端
# ============================================================

class DifyDatasetClient:
    """
    Dify 知識庫 API 客戶端

    提供知識庫的完整管理功能
    """

    def __init__(self, api_key: str, base_url: str = "https://api.dify.ai/v1"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    # --------------------------------------------------------
    # 數據集管理
    # --------------------------------------------------------

    def create_dataset(
        self,
        name: str,
        description: str = "",
        indexing_technique: IndexingTechnique = IndexingTechnique.HIGH_QUALITY,
        permission: str = "only_me"
    ) -> Dict[str, Any]:
        """
        創建數據集

        Args:
            name: 數據集名稱
            description: 描述
            indexing_technique: 索引技術
            permission: 權限設置

        Returns:
            創建的數據集信息
        """
        url = f"{self.base_url}/datasets"

        payload = {
            "name": name,
            "description": description,
            "indexing_technique": indexing_technique.value,
            "permission": permission
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()

        return response.json()

    def list_datasets(
        self,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        獲取數據集列表

        Args:
            page: 頁碼
            limit: 每頁數量

        Returns:
            數據集列表
        """
        url = f"{self.base_url}/datasets"

        params = {
            "page": page,
            "limit": limit
        }

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        return response.json()

    def delete_dataset(self, dataset_id: str) -> bool:
        """
        刪除數據集

        Args:
            dataset_id: 數據集 ID

        Returns:
            是否成功
        """
        url = f"{self.base_url}/datasets/{dataset_id}"

        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()

        return True

    # --------------------------------------------------------
    # 文檔管理
    # --------------------------------------------------------

    def create_document_by_text(
        self,
        dataset_id: str,
        name: str,
        text: str,
        indexing_technique: IndexingTechnique = IndexingTechnique.HIGH_QUALITY,
        doc_form: DocForm = DocForm.TEXT_MODEL,
        process_rule: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        通過文本創建文檔

        Args:
            dataset_id: 數據集 ID
            name: 文檔名稱
            text: 文檔內容
            indexing_technique: 索引技術
            doc_form: 文檔形式
            process_rule: 處理規則

        Returns:
            創建的文檔信息
        """
        url = f"{self.base_url}/datasets/{dataset_id}/document/create_by_text"

        # 默認處理規則
        if process_rule is None:
            process_rule = {
                "mode": "automatic"
            }

        payload = {
            "name": name,
            "text": text,
            "indexing_technique": indexing_technique.value,
            "doc_form": doc_form.value,
            "process_rule": process_rule
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()

        return response.json()

    def create_document_by_file(
        self,
        dataset_id: str,
        file_path: str,
        indexing_technique: IndexingTechnique = IndexingTechnique.HIGH_QUALITY,
        doc_form: DocForm = DocForm.TEXT_MODEL,
        process_rule: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        通過文件創建文檔

        Args:
            dataset_id: 數據集 ID
            file_path: 文件路徑
            indexing_technique: 索引技術
            doc_form: 文檔形式
            process_rule: 處理規則

        Returns:
            創建的文檔信息
        """
        url = f"{self.base_url}/datasets/{dataset_id}/document/create_by_file"

        # 默認處理規則
        if process_rule is None:
            process_rule = {
                "mode": "automatic"
            }

        # 準備表單數據
        data = {
            "indexing_technique": indexing_technique.value,
            "doc_form": doc_form.value,
            "process_rule": json.dumps(process_rule)
        }

        # 準備文件
        with open(file_path, 'rb') as f:
            files = {'file': f}

            # 移除 Content-Type header（讓 requests 自動設置）
            headers = {"Authorization": f"Bearer {self.api_key}"}

            response = requests.post(url, headers=headers, data=data, files=files)
            response.raise_for_status()

        return response.json()

    def list_documents(
        self,
        dataset_id: str,
        page: int = 1,
        limit: int = 20,
        keyword: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        獲取文檔列表

        Args:
            dataset_id: 數據集 ID
            page: 頁碼
            limit: 每頁數量
            keyword: 搜索關鍵詞

        Returns:
            文檔列表
        """
        url = f"{self.base_url}/datasets/{dataset_id}/documents"

        params = {
            "page": page,
            "limit": limit
        }

        if keyword:
            params["keyword"] = keyword

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        return response.json()

    def delete_document(
        self,
        dataset_id: str,
        document_id: str
    ) -> bool:
        """
        刪除文檔

        Args:
            dataset_id: 數據集 ID
            document_id: 文檔 ID

        Returns:
            是否成功
        """
        url = f"{self.base_url}/datasets/{dataset_id}/documents/{document_id}"

        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()

        return True

    def get_document_indexing_status(
        self,
        dataset_id: str,
        batch: str
    ) -> Dict[str, Any]:
        """
        獲取文檔索引狀態

        Args:
            dataset_id: 數據集 ID
            batch: 批次 ID

        Returns:
            索引狀態
        """
        url = f"{self.base_url}/datasets/{dataset_id}/documents/{batch}/indexing-status"

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        return response.json()

    # --------------------------------------------------------
    # 分段管理
    # --------------------------------------------------------

    def list_segments(
        self,
        dataset_id: str,
        document_id: str,
        keyword: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        獲取文檔分段列表

        Args:
            dataset_id: 數據集 ID
            document_id: 文檔 ID
            keyword: 搜索關鍵詞
            status: 狀態過濾

        Returns:
            分段列表
        """
        url = f"{self.base_url}/datasets/{dataset_id}/documents/{document_id}/segments"

        params = {}
        if keyword:
            params["keyword"] = keyword
        if status:
            params["status"] = status

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        return response.json()

    def add_segment(
        self,
        dataset_id: str,
        document_id: str,
        content: str,
        answer: Optional[str] = None,
        keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        添加分段

        Args:
            dataset_id: 數據集 ID
            document_id: 文檔 ID
            content: 分段內容
            answer: 答案（QA 模式）
            keywords: 關鍵詞

        Returns:
            添加的分段信息
        """
        url = f"{self.base_url}/datasets/{dataset_id}/documents/{document_id}/segments"

        segment = {
            "content": content
        }

        if answer:
            segment["answer"] = answer
        if keywords:
            segment["keywords"] = keywords

        payload = {
            "segments": [segment]
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()

        return response.json()

    def update_segment(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str,
        content: str,
        answer: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        enabled: bool = True
    ) -> Dict[str, Any]:
        """
        更新分段

        Args:
            dataset_id: 數據集 ID
            document_id: 文檔 ID
            segment_id: 分段 ID
            content: 分段內容
            answer: 答案
            keywords: 關鍵詞
            enabled: 是否啟用

        Returns:
            更新後的分段信息
        """
        url = f"{self.base_url}/datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}"

        segment = {
            "content": content,
            "enabled": enabled
        }

        if answer:
            segment["answer"] = answer
        if keywords:
            segment["keywords"] = keywords

        payload = {"segment": segment}

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()

        return response.json()

    def delete_segment(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str
    ) -> bool:
        """
        刪除分段

        Args:
            dataset_id: 數據集 ID
            document_id: 文檔 ID
            segment_id: 分段 ID

        Returns:
            是否成功
        """
        url = f"{self.base_url}/datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}"

        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()

        return True

    # --------------------------------------------------------
    # 檢索
    # --------------------------------------------------------

    def retrieve(
        self,
        dataset_id: str,
        query: str,
        top_k: int = 3,
        score_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        檢索知識庫

        Args:
            dataset_id: 數據集 ID
            query: 查詢文本
            top_k: 返回結果數量
            score_threshold: 分數閾值

        Returns:
            檢索結果
        """
        url = f"{self.base_url}/datasets/{dataset_id}/retrieve"

        payload = {
            "query": query,
            "retrieval_model": {
                "top_k": top_k,
                "score_threshold": score_threshold
            }
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()

        return response.json()


# ============================================================
# 使用範例
# ============================================================

def example_create_dataset():
    """
    範例 1: 創建數據集

    展示如何創建和管理數據集
    """
    print("=" * 50)
    print("範例 1: 創建數據集")
    print("=" * 50)

    client = DifyDatasetClient(
        api_key=DIFY_DATASET_API_KEY,
        base_url=DIFY_BASE_URL
    )

    try:
        # 創建數據集
        dataset = client.create_dataset(
            name="產品知識庫",
            description="包含產品文檔和常見問題",
            indexing_technique=IndexingTechnique.HIGH_QUALITY
        )

        print(f"數據集 ID: {dataset.get('id')}")
        print(f"數據集名稱: {dataset.get('name')}")

        # 列出所有數據集
        datasets = client.list_datasets()
        print(f"\n共有 {datasets.get('total', 0)} 個數據集")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_add_document_text():
    """
    範例 2: 通過文本添加文檔

    展示如何直接通過文本內容創建文檔
    """
    print("\n" + "=" * 50)
    print("範例 2: 通過文本添加文檔")
    print("=" * 50)

    client = DifyDatasetClient(
        api_key=DIFY_DATASET_API_KEY,
        base_url=DIFY_BASE_URL
    )

    # 假設我們有一個數據集 ID
    dataset_id = "your-dataset-id"

    # 準備文檔內容
    document_content = """
    # 產品介紹

    我們的產品是一款智能助手應用，具有以下特點：

    ## 核心功能
    1. 自然語言理解
    2. 多輪對話支持
    3. 知識庫檢索

    ## 使用場景
    - 客服自動化
    - 文檔問答
    - 內部知識管理

    ## 技術優勢
    - 高準確率
    - 低延遲響應
    - 易於集成
    """

    try:
        # 創建文檔
        doc = client.create_document_by_text(
            dataset_id=dataset_id,
            name="產品介紹文檔",
            text=document_content,
            doc_form=DocForm.TEXT_MODEL,
            process_rule={
                "mode": "custom",
                "rules": {
                    "pre_processing_rules": [
                        {"id": "remove_extra_spaces", "enabled": True},
                        {"id": "remove_urls_emails", "enabled": False}
                    ],
                    "segmentation": {
                        "separator": "\n\n",
                        "max_tokens": 500
                    }
                }
            }
        )

        print(f"文檔 ID: {doc.get('document', {}).get('id')}")
        print(f"批次 ID: {doc.get('batch')}")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_add_document_file():
    """
    範例 3: 通過文件添加文檔

    展示如何上傳文件創建文檔
    """
    print("\n" + "=" * 50)
    print("範例 3: 通過文件添加文檔")
    print("=" * 50)

    client = DifyDatasetClient(
        api_key=DIFY_DATASET_API_KEY,
        base_url=DIFY_BASE_URL
    )

    dataset_id = "your-dataset-id"
    file_path = "path/to/your/document.pdf"

    try:
        # 上傳文件
        doc = client.create_document_by_file(
            dataset_id=dataset_id,
            file_path=file_path,
            indexing_technique=IndexingTechnique.HIGH_QUALITY
        )

        print(f"文檔 ID: {doc.get('document', {}).get('id')}")

        # 檢查索引狀態
        batch = doc.get('batch')
        status = client.get_document_indexing_status(dataset_id, batch)
        print(f"索引狀態: {status}")

    except FileNotFoundError:
        print(f"文件不存在: {file_path}")
    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_qa_document():
    """
    範例 4: 創建 QA 模式文檔

    展示如何創建問答對形式的文檔
    """
    print("\n" + "=" * 50)
    print("範例 4: 創建 QA 模式文檔")
    print("=" * 50)

    client = DifyDatasetClient(
        api_key=DIFY_DATASET_API_KEY,
        base_url=DIFY_BASE_URL
    )

    dataset_id = "your-dataset-id"

    # QA 格式的內容
    qa_content = """
    Q: 如何重置密碼？
    A: 請訪問登錄頁面，點擊「忘記密碼」鏈接，輸入您的註冊郵箱，系統將發送重置鏈接。

    Q: 支持哪些支付方式？
    A: 我們支持信用卡、PayPal、銀行轉賬等多種支付方式。

    Q: 如何聯繫客服？
    A: 您可以通過在線聊天、郵件 support@example.com 或電話 400-xxx-xxxx 聯繫我們。
    """

    try:
        doc = client.create_document_by_text(
            dataset_id=dataset_id,
            name="常見問題 FAQ",
            text=qa_content,
            doc_form=DocForm.QA_MODEL  # QA 模式
        )

        print(f"QA 文檔創建成功: {doc.get('document', {}).get('id')}")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_manage_segments():
    """
    範例 5: 管理文檔分段

    展示如何查看和編輯文檔分段
    """
    print("\n" + "=" * 50)
    print("範例 5: 管理文檔分段")
    print("=" * 50)

    client = DifyDatasetClient(
        api_key=DIFY_DATASET_API_KEY,
        base_url=DIFY_BASE_URL
    )

    dataset_id = "your-dataset-id"
    document_id = "your-document-id"

    try:
        # 列出分段
        segments = client.list_segments(dataset_id, document_id)

        print(f"共有 {len(segments.get('data', []))} 個分段")

        for seg in segments.get('data', [])[:3]:  # 顯示前 3 個
            print(f"  - ID: {seg.get('id')}")
            print(f"    內容: {seg.get('content')[:50]}...")
            print(f"    狀態: {seg.get('status')}")

        # 添加新分段
        new_seg = client.add_segment(
            dataset_id=dataset_id,
            document_id=document_id,
            content="這是手動添加的新分段內容",
            keywords=["手動", "分段"]
        )

        print(f"\n新分段已添加: {new_seg}")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_retrieve():
    """
    範例 6: 知識庫檢索

    展示如何從知識庫中檢索相關內容
    """
    print("\n" + "=" * 50)
    print("範例 6: 知識庫檢索")
    print("=" * 50)

    client = DifyDatasetClient(
        api_key=DIFY_DATASET_API_KEY,
        base_url=DIFY_BASE_URL
    )

    dataset_id = "your-dataset-id"

    try:
        # 執行檢索
        results = client.retrieve(
            dataset_id=dataset_id,
            query="如何使用產品的核心功能？",
            top_k=5,
            score_threshold=0.3
        )

        print("檢索結果:")
        for i, record in enumerate(results.get('records', []), 1):
            print(f"\n結果 {i}:")
            print(f"  分數: {record.get('score', 0):.4f}")
            print(f"  內容: {record.get('segment', {}).get('content', '')[:100]}...")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_batch_import():
    """
    範例 7: 批量導入文檔

    展示如何批量導入多個文檔
    """
    print("\n" + "=" * 50)
    print("範例 7: 批量導入文檔")
    print("=" * 50)

    client = DifyDatasetClient(
        api_key=DIFY_DATASET_API_KEY,
        base_url=DIFY_BASE_URL
    )

    dataset_id = "your-dataset-id"

    # 準備多個文檔
    documents = [
        {"name": "產品手冊", "content": "這是產品手冊的內容..."},
        {"name": "API 文檔", "content": "這是 API 文檔的內容..."},
        {"name": "用戶指南", "content": "這是用戶指南的內容..."},
    ]

    try:
        results = []

        for doc in documents:
            result = client.create_document_by_text(
                dataset_id=dataset_id,
                name=doc["name"],
                text=doc["content"]
            )
            results.append(result)
            print(f"已導入: {doc['name']}")

        print(f"\n成功導入 {len(results)} 個文檔")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    print("Dify 知識庫管理範例")
    print("請確保已設置 DIFY_DATASET_API_KEY 環境變數")
    print()

    example_create_dataset()
    example_add_document_text()
    example_add_document_file()
    example_qa_document()
    example_manage_segments()
    example_retrieve()
    example_batch_import()
