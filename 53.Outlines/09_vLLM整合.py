"""
Outlines vLLM 整合示例
======================

本示例展示如何使用 Outlines 與 vLLM 整合以提升性能。

主要內容:
1. vLLM 後端設置
2. 高吞吐量生成
3. 批量推理優化
4. GPU 加速
5. 性能基準測試

作者: Outlines 教學團隊
日期: 2025-01
"""

import outlines
from outlines import models, generate
import torch
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import json
import time
import sys
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import numpy as np

# ==================== 設置日誌 ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== 數據模型 ====================

class Document(BaseModel):
    """文檔模型"""
    title: str = Field(description="標題")
    content: str = Field(description="內容")
    category: str = Field(description="類別")
    tags: List[str] = Field(default_factory=list, description="標籤")
    author: str = Field(description="作者")


class Summary(BaseModel):
    """摘要模型"""
    main_points: List[str] = Field(description="要點")
    conclusion: str = Field(description="結論")
    keywords: List[str] = Field(description="關鍵詞")


class Classification(BaseModel):
    """分類模型"""
    category: str = Field(description="類別")
    confidence: float = Field(description="置信度", ge=0, le=1)
    subcategories: List[str] = Field(default_factory=list, description="子類別")


class EntityExtraction(BaseModel):
    """實體抽取模型"""
    persons: List[str] = Field(default_factory=list, description="人名")
    organizations: List[str] = Field(default_factory=list, description="組織")
    locations: List[str] = Field(default_factory=list, description="地點")
    dates: List[str] = Field(default_factory=list, description="日期")


class SentimentAnalysis(BaseModel):
    """情感分析模型"""
    sentiment: str = Field(description="情感")
    score: float = Field(description="分數", ge=-1, le=1)
    aspects: Dict[str, str] = Field(default_factory=dict, description="方面情感")


# ==================== 性能指標 ====================

@dataclass
class PerformanceMetrics:
    """性能指標"""
    backend: str
    total_items: int
    total_time: float
    throughput: float  # 項/秒
    avg_latency: float  # 秒/項
    p50_latency: float
    p95_latency: float
    p99_latency: float

    def __str__(self):
        return f"""
性能指標 ({self.backend}):
  總項目數: {self.total_items}
  總耗時: {self.total_time:.2f}秒
  吞吐量: {self.throughput:.2f} 項/秒
  平均延遲: {self.avg_latency:.4f}秒
  P50 延遲: {self.p50_latency:.4f}秒
  P95 延遲: {self.p95_latency:.4f}秒
  P99 延遲: {self.p99_latency:.4f}秒
        """


# ==================== vLLM 管理器 ====================

class VLLMManager:
    """
    vLLM 管理器

    管理 vLLM 後端的模型和生成
    """

    def __init__(
        self,
        model_name: str = "mistralai/Mistral-7B-v0.1",
        use_vllm: bool = True,
        tensor_parallel_size: int = 1,
        gpu_memory_utilization: float = 0.9
    ):
        """
        初始化 vLLM 管理器

        Args:
            model_name: 模型名稱
            use_vllm: 是否使用 vLLM
            tensor_parallel_size: 張量並行大小
            gpu_memory_utilization: GPU 內存使用率
        """
        self.model_name = model_name
        self.use_vllm = use_vllm
        self.tensor_parallel_size = tensor_parallel_size
        self.gpu_memory_utilization = gpu_memory_utilization
        self.model = None

        self.load_model()

        logger.info(f"vLLM 管理器初始化完成, 後端: {'vLLM' if use_vllm else 'Transformers'}")

    def load_model(self):
        """載入模型"""
        try:
            logger.info(f"載入模型: {self.model_name}")

            if self.use_vllm and torch.cuda.is_available():
                try:
                    # 嘗試使用 vLLM 後端
                    logger.info("使用 vLLM 後端")
                    self.model = models.vllm(
                        self.model_name,
                        tensor_parallel_size=self.tensor_parallel_size,
                        gpu_memory_utilization=self.gpu_memory_utilization
                    )
                    logger.info("vLLM 模型載入成功")

                except Exception as e:
                    logger.warning(f"vLLM 載入失敗,降級到 Transformers: {str(e)}")
                    self.use_vllm = False
                    self._load_transformers()
            else:
                self._load_transformers()

        except Exception as e:
            logger.error(f"模型載入失敗: {str(e)}")
            raise

    def _load_transformers(self):
        """載入 Transformers 模型"""
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"使用 Transformers 後端, 設備: {device}")

        self.model = models.transformers(
            self.model_name,
            device=device
        )

        logger.info("Transformers 模型載入成功")

    def generate_json(
        self,
        prompt: str,
        schema: type[BaseModel]
    ) -> BaseModel:
        """
        生成 JSON

        Args:
            prompt: 提示
            schema: Pydantic 模型

        Returns:
            模型實例
        """
        generator = generate.json(self.model, schema)
        return generator(prompt)

    def batch_generate_json(
        self,
        prompts: List[str],
        schema: type[BaseModel]
    ) -> List[BaseModel]:
        """
        批量生成 JSON

        Args:
            prompts: 提示列表
            schema: Pydantic 模型

        Returns:
            模型實例列表
        """
        generator = generate.json(self.model, schema)
        results = []

        for prompt in prompts:
            result = generator(prompt)
            results.append(result)

        return results


# ==================== 基準測試器 ====================

class BenchmarkRunner:
    """
    基準測試運行器

    比較不同後端的性能
    """

    def __init__(self):
        """初始化基準測試運行器"""
        logger.info("基準測試運行器初始化完成")

    def run_benchmark(
        self,
        manager: VLLMManager,
        schema: type[BaseModel],
        prompts: List[str]
    ) -> PerformanceMetrics:
        """
        運行基準測試

        Args:
            manager: vLLM 管理器
            schema: Pydantic 模型
            prompts: 提示列表

        Returns:
            性能指標
        """
        logger.info(f"開始基準測試, 項目數: {len(prompts)}")

        latencies = []
        start_time = time.time()

        for prompt in prompts:
            item_start = time.time()
            _ = manager.generate_json(prompt, schema)
            latency = time.time() - item_start
            latencies.append(latency)

        total_time = time.time() - start_time

        # 計算指標
        latencies_sorted = sorted(latencies)
        metrics = PerformanceMetrics(
            backend="vLLM" if manager.use_vllm else "Transformers",
            total_items=len(prompts),
            total_time=total_time,
            throughput=len(prompts) / total_time,
            avg_latency=np.mean(latencies),
            p50_latency=np.percentile(latencies, 50),
            p95_latency=np.percentile(latencies, 95),
            p99_latency=np.percentile(latencies, 99)
        )

        logger.info("基準測試完成")
        return metrics

    def compare_backends(
        self,
        model_name: str,
        schema: type[BaseModel],
        prompts: List[str]
    ) -> Dict[str, PerformanceMetrics]:
        """
        比較不同後端

        Args:
            model_name: 模型名稱
            schema: Pydantic 模型
            prompts: 提示列表

        Returns:
            性能指標字典
        """
        results = {}

        # 測試 Transformers 後端
        print("\n測試 Transformers 後端...")
        manager_tf = VLLMManager(model_name, use_vllm=False)
        metrics_tf = self.run_benchmark(manager_tf, schema, prompts)
        results["Transformers"] = metrics_tf

        # 測試 vLLM 後端
        if torch.cuda.is_available():
            print("\n測試 vLLM 後端...")
            try:
                manager_vllm = VLLMManager(model_name, use_vllm=True)
                metrics_vllm = self.run_benchmark(manager_vllm, schema, prompts)
                results["vLLM"] = metrics_vllm
            except Exception as e:
                logger.warning(f"vLLM 測試失敗: {str(e)}")

        return results


# ==================== 高級應用 ====================

class DocumentProcessor:
    """
    文檔處理器

    使用 vLLM 處理大量文檔
    """

    def __init__(self, manager: VLLMManager):
        """
        初始化文檔處理器

        Args:
            manager: vLLM 管理器
        """
        self.manager = manager
        logger.info("文檔處理器初始化完成")

    def summarize_documents(
        self,
        documents: List[str]
    ) -> List[Summary]:
        """
        批量摘要文檔

        Args:
            documents: 文檔列表

        Returns:
            摘要列表
        """
        logger.info(f"摘要 {len(documents)} 個文檔")

        prompts = [
            f"為以下文檔生成摘要:\n{doc}"
            for doc in documents
        ]

        summaries = self.manager.batch_generate_json(prompts, Summary)

        return summaries

    def classify_documents(
        self,
        documents: List[str]
    ) -> List[Classification]:
        """
        批量分類文檔

        Args:
            documents: 文檔列表

        Returns:
            分類列表
        """
        logger.info(f"分類 {len(documents)} 個文檔")

        prompts = [
            f"分類以下文檔:\n{doc}"
            for doc in documents
        ]

        classifications = self.manager.batch_generate_json(prompts, Classification)

        return classifications

    def extract_entities(
        self,
        documents: List[str]
    ) -> List[EntityExtraction]:
        """
        批量抽取實體

        Args:
            documents: 文檔列表

        Returns:
            實體抽取結果列表
        """
        logger.info(f"從 {len(documents)} 個文檔中抽取實體")

        prompts = [
            f"從以下文檔中抽取實體:\n{doc}"
            for doc in documents
        ]

        entities = self.manager.batch_generate_json(prompts, EntityExtraction)

        return entities

    def analyze_sentiment(
        self,
        texts: List[str]
    ) -> List[SentimentAnalysis]:
        """
        批量情感分析

        Args:
            texts: 文本列表

        Returns:
            情感分析結果列表
        """
        logger.info(f"分析 {len(texts)} 個文本的情感")

        prompts = [
            f"分析以下文本的情感:\n{text}"
            for text in texts
        ]

        sentiments = self.manager.batch_generate_json(prompts, SentimentAnalysis)

        return sentiments


# ==================== 優化器 ====================

class VLLMOptimizer:
    """
    vLLM 優化器

    提供各種性能優化建議和工具
    """

    @staticmethod
    def get_optimal_batch_size(
        model_name: str,
        available_memory_gb: float
    ) -> int:
        """
        獲取最優批量大小

        Args:
            model_name: 模型名稱
            available_memory_gb: 可用內存(GB)

        Returns:
            建議的批量大小
        """
        # 簡化的批量大小計算
        if "7B" in model_name:
            base_memory = 14  # GB
        elif "13B" in model_name:
            base_memory = 26  # GB
        else:
            base_memory = 8  # GB

        if available_memory_gb < base_memory:
            logger.warning("可用內存不足,建議使用較小批量")
            return 1

        batch_size = int((available_memory_gb - base_memory) / 2)
        batch_size = max(1, min(batch_size, 32))

        return batch_size

    @staticmethod
    def get_gpu_config() -> Dict[str, Any]:
        """
        獲取 GPU 配置信息

        Returns:
            GPU 配置字典
        """
        if not torch.cuda.is_available():
            return {
                "available": False,
                "message": "CUDA 不可用"
            }

        config = {
            "available": True,
            "device_count": torch.cuda.device_count(),
            "current_device": torch.cuda.current_device(),
            "device_name": torch.cuda.get_device_name(),
            "total_memory_gb": torch.cuda.get_device_properties(0).total_memory / 1e9,
            "allocated_memory_gb": torch.cuda.memory_allocated() / 1e9,
            "cached_memory_gb": torch.cuda.memory_reserved() / 1e9
        }

        return config

    @staticmethod
    def suggest_optimizations(
        model_name: str,
        task_type: str
    ) -> List[str]:
        """
        建議優化方案

        Args:
            model_name: 模型名稱
            task_type: 任務類型

        Returns:
            優化建議列表
        """
        suggestions = []

        # 基於模型大小的建議
        if "7B" in model_name or "13B" in model_name:
            suggestions.append("使用 vLLM 可獲得 2-3x 性能提升")
            suggestions.append("考慮使用 tensor_parallel_size=2 或更大值")

        # 基於任務類型的建議
        if task_type == "batch":
            suggestions.append("增加批量大小以提高吞吐量")
            suggestions.append("使用 GPU 內存利用率 0.9 以獲得最佳性能")

        elif task_type == "realtime":
            suggestions.append("減小批量大小以降低延遲")
            suggestions.append("考慮使用模型量化")

        # GPU 相關建議
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            if gpu_count > 1:
                suggestions.append(f"檢測到 {gpu_count} 個 GPU,考慮使用張量並行")

        return suggestions


# ==================== 示例運行器 ====================

def run_vllm_basic_example():
    """運行 vLLM 基本示例"""
    print("\n" + "="*60)
    print("示例 1: vLLM 基本使用")
    print("="*60)

    # 創建管理器
    manager = VLLMManager(use_vllm=True)

    # 生成文檔
    print("\n生成文檔:")
    doc = manager.generate_json(
        "生成一篇關於人工智能的技術文檔",
        Document
    )

    print(f"標題: {doc.title}")
    print(f"類別: {doc.category}")
    print(f"作者: {doc.author}")
    print(f"標籤: {', '.join(doc.tags)}")
    print(f"內容: {doc.content[:200]}...")


def run_batch_processing_example():
    """運行批量處理示例"""
    print("\n" + "="*60)
    print("示例 2: 批量文檔處理")
    print("="*60)

    manager = VLLMManager(use_vllm=True)
    processor = DocumentProcessor(manager)

    # 測試文檔
    documents = [
        "人工智能正在改變世界...",
        "機器學習是AI的一個分支...",
        "深度學習使用神經網絡..."
    ]

    # 批量摘要
    print("\n批量生成摘要:")
    summaries = processor.summarize_documents(documents)

    for i, summary in enumerate(summaries, 1):
        print(f"\n文檔 {i}:")
        print(f"  要點: {summary.main_points}")
        print(f"  結論: {summary.conclusion}")

    # 批量分類
    print("\n批量分類文檔:")
    classifications = processor.classify_documents(documents)

    for i, cls in enumerate(classifications, 1):
        print(f"\n文檔 {i}:")
        print(f"  類別: {cls.category}")
        print(f"  置信度: {cls.confidence:.2f}")


def run_performance_benchmark():
    """運行性能基準測試"""
    print("\n" + "="*60)
    print("示例 3: 性能基準測試")
    print("="*60)

    # 準備測試數據
    prompts = [
        f"生成第 {i+1} 個測試文檔"
        for i in range(10)
    ]

    # 運行基準測試
    benchmark = BenchmarkRunner()
    results = benchmark.compare_backends(
        "mistralai/Mistral-7B-v0.1",
        Document,
        prompts
    )

    # 顯示結果
    for backend, metrics in results.items():
        print(metrics)

    # 計算加速比
    if len(results) == 2:
        tf_time = results["Transformers"].total_time
        vllm_time = results["vLLM"].total_time
        speedup = tf_time / vllm_time
        print(f"\nvLLM 加速比: {speedup:.2f}x")


def run_optimization_example():
    """運行優化示例"""
    print("\n" + "="*60)
    print("示例 4: 性能優化建議")
    print("="*60)

    # 獲取 GPU 配置
    print("\nGPU 配置:")
    gpu_config = VLLMOptimizer.get_gpu_config()

    for key, value in gpu_config.items():
        print(f"  {key}: {value}")

    # 獲取優化建議
    print("\n優化建議:")
    suggestions = VLLMOptimizer.suggest_optimizations(
        "mistralai/Mistral-7B-v0.1",
        "batch"
    )

    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")

    # 獲取最優批量大小
    if gpu_config.get("available"):
        optimal_batch = VLLMOptimizer.get_optimal_batch_size(
            "mistralai/Mistral-7B-v0.1",
            gpu_config["total_memory_gb"]
        )
        print(f"\n建議批量大小: {optimal_batch}")


def main():
    """主函數"""
    try:
        print("\n開始運行 vLLM 整合示例...")

        run_vllm_basic_example()
        run_batch_processing_example()
        run_performance_benchmark()
        run_optimization_example()

        print("\n" + "="*60)
        print("所有示例運行完成!")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\n用戶中斷執行")
    except Exception as e:
        print(f"\n錯誤: {str(e)}")
        logger.error(f"主程序錯誤: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
