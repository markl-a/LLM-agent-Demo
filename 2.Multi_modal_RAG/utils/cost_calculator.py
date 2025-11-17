"""
成本計算器

功能：
1. 計算 RAG 系統各項成本
2. 估算月度成本
3. 成本優化建議
4. 導出成本報告
"""

import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from enum import Enum
import argparse


class ModelType(Enum):
    """模型類型"""
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_35_TURBO = "gpt-3.5-turbo"
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"


# API 定價表（美元）- 2024年11月價格
PRICING = {
    # GPT-4o
    ModelType.GPT_4O: {
        "input": 0.0025 / 1000,      # $2.50 per 1M tokens
        "output": 0.01 / 1000,        # $10.00 per 1M tokens
        "image": 0.00765,             # per 1024x1024 image
    },
    # GPT-4o mini
    ModelType.GPT_4O_MINI: {
        "input": 0.00015 / 1000,     # $0.150 per 1M tokens
        "output": 0.0006 / 1000,      # $0.600 per 1M tokens
        "image": 0.002833,            # per 1024x1024 image
    },
    # GPT-4 Turbo
    ModelType.GPT_4_TURBO: {
        "input": 0.01 / 1000,         # $10 per 1M tokens
        "output": 0.03 / 1000,        # $30 per 1M tokens
    },
    # GPT-3.5 Turbo
    ModelType.GPT_35_TURBO: {
        "input": 0.0005 / 1000,       # $0.50 per 1M tokens
        "output": 0.0015 / 1000,      # $1.50 per 1M tokens
    },
    # 嵌入模型
    ModelType.TEXT_EMBEDDING_3_SMALL: {
        "input": 0.00002 / 1000,      # $0.02 per 1M tokens
    },
    ModelType.TEXT_EMBEDDING_3_LARGE: {
        "input": 0.00013 / 1000,      # $0.13 per 1M tokens
    },
}


@dataclass
class QueryCost:
    """單次查詢成本"""
    embedding: float = 0.0          # 嵌入成本
    retrieval: float = 0.0          # 檢索成本（向量庫）
    image_processing: float = 0.0   # 圖像處理成本
    text_summary: float = 0.0       # 文本摘要成本
    generation: float = 0.0         # 答案生成成本
    total: float = 0.0              # 總成本

    def calculate_total(self):
        """計算總成本"""
        self.total = (
            self.embedding +
            self.retrieval +
            self.image_processing +
            self.text_summary +
            self.generation
        )
        return self.total


@dataclass
class DocumentProcessingCost:
    """文檔處理成本"""
    parsing: float = 0.0           # 解析成本
    image_summary: float = 0.0     # 圖像摘要
    text_summary: float = 0.0      # 文本摘要
    table_summary: float = 0.0     # 表格摘要
    embedding: float = 0.0         # 嵌入
    storage: float = 0.0           # 存儲（月度）
    total: float = 0.0

    def calculate_total(self):
        """計算總成本"""
        self.total = (
            self.parsing +
            self.image_summary +
            self.text_summary +
            self.table_summary +
            self.embedding +
            self.storage
        )
        return self.total


class CostCalculator:
    """成本計算器"""

    def __init__(
        self,
        embedding_model: ModelType = ModelType.TEXT_EMBEDDING_3_SMALL,
        llm_model: ModelType = ModelType.GPT_4O,
        vision_model: ModelType = ModelType.GPT_4O,
    ):
        """
        初始化成本計算器

        Args:
            embedding_model: 嵌入模型
            llm_model: LLM 模型
            vision_model: 視覺模型
        """
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.vision_model = vision_model

    def calculate_query_cost(
        self,
        query_tokens: int,
        retrieved_docs: int = 5,
        retrieved_images: int = 2,
        input_tokens: int = 2000,
        output_tokens: int = 300
    ) -> QueryCost:
        """
        計算單次查詢成本

        Args:
            query_tokens: 查詢的 token 數
            retrieved_docs: 檢索的文檔數
            retrieved_images: 檢索的圖像數
            input_tokens: LLM 輸入 token 數
            output_tokens: LLM 輸出 token 數

        Returns:
            QueryCost: 查詢成本
        """
        cost = QueryCost()

        # 1. 嵌入成本
        cost.embedding = query_tokens * PRICING[self.embedding_model]["input"]

        # 2. 檢索成本（Pinecone: ~$0.0001 per query）
        cost.retrieval = 0.0001

        # 3. 圖像處理成本
        if retrieved_images > 0:
            cost.image_processing = (
                retrieved_images * PRICING[self.vision_model].get("image", 0)
            )

        # 4. LLM 成本
        cost.generation = (
            input_tokens * PRICING[self.llm_model]["input"] +
            output_tokens * PRICING[self.llm_model]["output"]
        )

        cost.calculate_total()
        return cost

    def calculate_document_processing_cost(
        self,
        num_texts: int,
        num_images: int,
        num_tables: int,
        avg_text_tokens: int = 1000,
        avg_table_tokens: int = 500,
    ) -> DocumentProcessingCost:
        """
        計算文檔處理成本

        Args:
            num_texts: 文本塊數量
            num_images: 圖像數量
            num_tables: 表格數量
            avg_text_tokens: 平均文本 token 數
            avg_table_tokens: 平均表格 token 數

        Returns:
            DocumentProcessingCost: 文檔處理成本
        """
        cost = DocumentProcessingCost()

        # 1. 圖像摘要成本
        cost.image_summary = num_images * PRICING[self.vision_model].get("image", 0)

        # 2. 文本摘要成本
        if num_texts > 0:
            total_text_tokens = num_texts * avg_text_tokens
            # 輸入成本
            cost.text_summary += total_text_tokens * PRICING[self.llm_model]["input"]
            # 輸出成本（假設壓縮到 30%）
            cost.text_summary += (
                total_text_tokens * 0.3 * PRICING[self.llm_model]["output"]
            )

        # 3. 表格摘要成本
        if num_tables > 0:
            total_table_tokens = num_tables * avg_table_tokens
            cost.table_summary += total_table_tokens * PRICING[self.llm_model]["input"]
            cost.table_summary += (
                total_table_tokens * 0.3 * PRICING[self.llm_model]["output"]
            )

        # 4. 嵌入成本
        total_summary_tokens = (
            num_texts * avg_text_tokens * 0.3 +  # 文本摘要
            num_images * 50 +                     # 圖像摘要（估計 50 tokens）
            num_tables * avg_table_tokens * 0.3   # 表格摘要
        )
        cost.embedding = total_summary_tokens * PRICING[self.embedding_model]["input"]

        # 5. 存儲成本（S3: $0.023/GB/month）
        # 假設每個文本塊 1KB，每張圖像 100KB
        storage_mb = (num_texts * 1 / 1024 + num_images * 100 / 1024)
        cost.storage = storage_mb * 0.023 / 1024

        cost.calculate_total()
        return cost

    def estimate_monthly_cost(
        self,
        daily_queries: int,
        avg_query_cost: Optional[QueryCost] = None,
        new_documents_per_month: int = 0,
        avg_doc_cost: Optional[DocumentProcessingCost] = None,
    ) -> Dict:
        """
        估算月度成本

        Args:
            daily_queries: 每日查詢數
            avg_query_cost: 平均查詢成本
            new_documents_per_month: 每月新增文檔數
            avg_doc_cost: 平均文檔處理成本

        Returns:
            Dict: 月度成本估算
        """
        # 默認查詢成本
        if avg_query_cost is None:
            avg_query_cost = self.calculate_query_cost(
                query_tokens=50,
                retrieved_images=1,
                input_tokens=1500,
                output_tokens=300
            )

        # 默認文檔處理成本
        if avg_doc_cost is None:
            avg_doc_cost = self.calculate_document_processing_cost(
                num_texts=20,
                num_images=5,
                num_tables=3
            )

        # 計算月度成本
        monthly_query_cost = avg_query_cost.total * daily_queries * 30
        monthly_doc_cost = avg_doc_cost.total * new_documents_per_month

        # 向量庫成本（Pinecone Starter: $70/month）
        monthly_vector_db = 70.0

        # 服務器成本（估算）
        monthly_infrastructure = 100.0

        total_monthly = (
            monthly_query_cost +
            monthly_doc_cost +
            monthly_vector_db +
            monthly_infrastructure
        )

        return {
            "breakdown": {
                "query_processing": monthly_query_cost,
                "document_processing": monthly_doc_cost,
                "vector_database": monthly_vector_db,
                "infrastructure": monthly_infrastructure,
            },
            "total": total_monthly,
            "per_query": avg_query_cost.total,
            "metrics": {
                "daily_queries": daily_queries,
                "monthly_queries": daily_queries * 30,
                "new_documents_per_month": new_documents_per_month,
            }
        }

    def optimize_cost(
        self,
        current_config: Dict,
        target_reduction: float = 0.3
    ) -> Dict:
        """
        成本優化建議

        Args:
            current_config: 當前配置
            target_reduction: 目標降低比例（例如 0.3 = 30%）

        Returns:
            Dict: 優化建議
        """
        suggestions = []

        # 建議 1：使用更便宜的模型
        if self.llm_model == ModelType.GPT_4O:
            savings_mini = self._estimate_model_savings(
                ModelType.GPT_4O,
                ModelType.GPT_4O_MINI,
                current_config.get("monthly_queries", 1000)
            )
            suggestions.append({
                "action": "使用 GPT-4o-mini 替代 GPT-4o 處理簡單查詢",
                "estimated_savings": savings_mini,
                "trade_off": "性能略微下降（約 5-10%）",
                "priority": "high"
            })

        # 建議 2：智能圖像處理
        avg_images = current_config.get("avg_retrieved_images", 2)
        if avg_images > 1:
            potential_savings = (
                avg_images * 0.5 *  # 假設減少 50% 圖像處理
                PRICING[self.vision_model].get("image", 0) *
                current_config.get("monthly_queries", 1000)
            )
            suggestions.append({
                "action": "實現智能圖像處理（只在需要時處理圖像）",
                "estimated_savings": potential_savings,
                "trade_off": "需要額外的查詢意圖分析邏輯",
                "priority": "high"
            })

        # 建議 3：調整檢索數量
        avg_docs = current_config.get("avg_retrieved_docs", 5)
        if avg_docs > 3:
            suggestions.append({
                "action": "減少檢索文檔數量（5 → 3）",
                "estimated_savings": "10-20% 的生成成本",
                "trade_off": "可能遺漏部分相關資訊",
                "priority": "medium"
            })

        # 建議 4：實現快取
        cache_hit_rate = current_config.get("cache_hit_rate", 0)
        if cache_hit_rate < 0.2:
            potential_savings = (
                current_config.get("monthly_query_cost", 100) * 0.3  # 假設 30% 快取命中
            )
            suggestions.append({
                "action": "實現查詢快取（Redis）",
                "estimated_savings": potential_savings,
                "trade_off": "需要快取管理和更新邏輯",
                "priority": "medium"
            })

        # 建議 5：批量處理
        suggestions.append({
            "action": "使用批量 API 處理文檔摘要",
            "estimated_savings": "10-15% 的文檔處理成本",
            "trade_off": "略微增加處理延遲",
            "priority": "low"
        })

        return {
            "target_reduction": f"{target_reduction * 100:.0f}%",
            "suggestions": suggestions,
            "total_potential_savings": sum(
                s.get("estimated_savings", 0)
                for s in suggestions
                if isinstance(s.get("estimated_savings"), (int, float))
            )
        }

    def _estimate_model_savings(
        self,
        current_model: ModelType,
        new_model: ModelType,
        monthly_queries: int
    ) -> float:
        """估算模型切換的成本節省"""
        # 假設平均使用量
        avg_input = 1500
        avg_output = 300

        current_cost = (
            avg_input * PRICING[current_model]["input"] +
            avg_output * PRICING[current_model]["output"]
        )

        new_cost = (
            avg_input * PRICING[new_model]["input"] +
            avg_output * PRICING[new_model]["output"]
        )

        monthly_savings = (current_cost - new_cost) * monthly_queries

        return monthly_savings

    def generate_report(
        self,
        daily_queries: int,
        new_documents_per_month: int = 0,
        output_file: Optional[str] = None
    ) -> Dict:
        """
        生成成本報告

        Args:
            daily_queries: 每日查詢數
            new_documents_per_month: 每月新增文檔數
            output_file: 輸出文件路徑（可選）

        Returns:
            Dict: 成本報告
        """
        # 計算成本
        monthly_cost = self.estimate_monthly_cost(
            daily_queries=daily_queries,
            new_documents_per_month=new_documents_per_month
        )

        # 優化建議
        optimization = self.optimize_cost(
            current_config={
                "monthly_queries": daily_queries * 30,
                "monthly_query_cost": monthly_cost["breakdown"]["query_processing"],
                "avg_retrieved_images": 2,
                "avg_retrieved_docs": 5,
                "cache_hit_rate": 0.1
            }
        )

        # 構建報告
        report = {
            "configuration": {
                "embedding_model": self.embedding_model.value,
                "llm_model": self.llm_model.value,
                "vision_model": self.vision_model.value,
            },
            "monthly_cost": monthly_cost,
            "optimization": optimization,
            "summary": {
                "current_monthly_cost": monthly_cost["total"],
                "cost_per_query": monthly_cost["per_query"],
                "cost_per_1000_queries": monthly_cost["per_query"] * 1000,
                "potential_savings": optimization["total_potential_savings"],
            }
        }

        # 保存報告
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"報告已保存到：{output_file}")

        return report


def print_report(report: Dict):
    """打印美化的報告"""
    print("\n" + "=" * 60)
    print("RAG 系統成本報告")
    print("=" * 60)

    # 配置
    print("\n配置：")
    for key, value in report["configuration"].items():
        print(f"  {key}: {value}")

    # 月度成本
    print("\n月度成本分解：")
    for key, value in report["monthly_cost"]["breakdown"].items():
        print(f"  {key}: ${value:.2f}")

    print(f"\n總成本：${report['monthly_cost']['total']:.2f}/月")
    print(f"每次查詢成本：${report['summary']['cost_per_query']:.4f}")
    print(f"每 1000 次查詢成本：${report['summary']['cost_per_1000_queries']:.2f}")

    # 優化建議
    print("\n成本優化建議：")
    for i, suggestion in enumerate(report["optimization"]["suggestions"], 1):
        print(f"\n  {i}. {suggestion['action']}")
        print(f"     預估節省：{suggestion['estimated_savings']}")
        print(f"     權衡：{suggestion['trade_off']}")
        print(f"     優先級：{suggestion['priority']}")

    print(f"\n總潛在節省：${report['summary']['potential_savings']:.2f}/月")

    print("\n" + "=" * 60)


def main():
    """命令行工具"""
    parser = argparse.ArgumentParser(description="RAG 系統成本計算器")
    parser.add_argument(
        "--daily-queries",
        type=int,
        required=True,
        help="每日查詢數"
    )
    parser.add_argument(
        "--new-docs",
        type=int,
        default=0,
        help="每月新增文檔數"
    )
    parser.add_argument(
        "--llm-model",
        choices=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
        default="gpt-4o",
        help="LLM 模型"
    )
    parser.add_argument(
        "--output",
        help="輸出報告文件路徑"
    )

    args = parser.parse_args()

    # 創建計算器
    model_map = {
        "gpt-4o": ModelType.GPT_4O,
        "gpt-4o-mini": ModelType.GPT_4O_MINI,
        "gpt-4-turbo": ModelType.GPT_4_TURBO,
    }

    calculator = CostCalculator(
        llm_model=model_map[args.llm_model],
        vision_model=model_map[args.llm_model]
    )

    # 生成報告
    report = calculator.generate_report(
        daily_queries=args.daily_queries,
        new_documents_per_month=args.new_docs,
        output_file=args.output
    )

    # 打印報告
    print_report(report)


if __name__ == "__main__":
    main()
