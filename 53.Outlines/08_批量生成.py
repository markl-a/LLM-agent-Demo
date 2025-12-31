"""
Outlines 批量生成示例
====================

本示例展示如何使用 Outlines 高效地進行批量結構化生成。

主要內容:
1. 批量數據生成
2. 並行處理
3. 性能優化
4. 結果聚合
5. 錯誤處理

作者: Outlines 教學團隊
日期: 2025-01
"""

import outlines
from outlines import models, generate
import torch
from typing import List, Dict, Optional, Any, Callable
from pydantic import BaseModel, Field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import json
import time
import sys
from dataclasses import dataclass
from collections import defaultdict

# ==================== 設置日誌 ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== 數據模型 ====================

class TestUser(BaseModel):
    """測試用戶模型"""
    id: int = Field(description="用戶ID", ge=1)
    username: str = Field(description="用戶名", min_length=3, max_length=20)
    email: str = Field(description="郵箱")
    age: int = Field(description="年齡", ge=18, le=100)
    city: str = Field(description="城市")
    is_active: bool = Field(default=True, description="是否活躍")


class TestProduct(BaseModel):
    """測試產品模型"""
    id: int = Field(description="產品ID", ge=1)
    name: str = Field(description="產品名稱")
    price: float = Field(description="價格", gt=0)
    category: str = Field(description="類別")
    stock: int = Field(description="庫存", ge=0)
    rating: float = Field(description="評分", ge=0, le=5)


class TestOrder(BaseModel):
    """測試訂單模型"""
    order_id: str = Field(description="訂單號")
    user_id: int = Field(description="用戶ID")
    product_ids: List[int] = Field(description="產品ID列表")
    total_amount: float = Field(description="總金額", gt=0)
    status: str = Field(description="狀態")


class LogEntry(BaseModel):
    """日誌條目模型"""
    timestamp: str = Field(description="時間戳")
    level: str = Field(description="日誌級別")
    message: str = Field(description="消息")
    source: str = Field(description="來源")


class SyntheticReview(BaseModel):
    """合成評論模型"""
    product_name: str = Field(description="產品名稱")
    rating: int = Field(description="評分", ge=1, le=5)
    title: str = Field(description="評論標題")
    content: str = Field(description="評論內容")
    helpful_count: int = Field(default=0, description="有用計數", ge=0)


# ==================== 性能統計 ====================

@dataclass
class GenerationStats:
    """生成統計"""
    total_count: int
    success_count: int
    failure_count: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float

    def __str__(self):
        return f"""
生成統計:
  總數: {self.total_count}
  成功: {self.success_count}
  失敗: {self.failure_count}
  總耗時: {self.total_time:.2f}秒
  平均耗時: {self.avg_time:.2f}秒
  最小耗時: {self.min_time:.2f}秒
  最大耗時: {self.max_time:.2f}秒
  速率: {self.total_count / self.total_time:.2f} 項/秒
        """


# ==================== 批量生成管理器 ====================

class BatchGenerationManager:
    """
    批量生成管理器

    管理大規模批量生成任務
    """

    def __init__(self, model_name: str = "mistralai/Mistral-7B-v0.1"):
        """
        初始化批量生成管理器

        Args:
            model_name: 模型名稱
        """
        self.model_name = model_name
        self.model = None
        self.load_model()

        logger.info(f"批量生成管理器初始化完成")

    def load_model(self):
        """載入模型"""
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = models.transformers(self.model_name, device=device)
            logger.info("模型載入完成")
        except Exception as e:
            logger.error(f"模型載入失敗: {str(e)}")
            raise

    def batch_generate(
        self,
        schema: type[BaseModel],
        count: int,
        prompt_template: str,
        show_progress: bool = True
    ) -> tuple[List[BaseModel], GenerationStats]:
        """
        批量生成數據

        Args:
            schema: Pydantic 模型
            count: 生成數量
            prompt_template: 提示模板
            show_progress: 是否顯示進度

        Returns:
            (生成結果列表, 統計信息)
        """
        logger.info(f"開始批量生成 {count} 個 {schema.__name__}")

        results = []
        times = []
        success_count = 0
        failure_count = 0

        # 創建生成器
        generator = generate.json(self.model, schema)

        start_time = time.time()

        for i in range(count):
            try:
                item_start = time.time()

                # 格式化提示
                prompt = prompt_template.format(index=i+1)

                # 生成
                result = generator(prompt)
                results.append(result)

                item_time = time.time() - item_start
                times.append(item_time)
                success_count += 1

                if show_progress and (i + 1) % 10 == 0:
                    logger.info(f"進度: {i+1}/{count}")

            except Exception as e:
                logger.error(f"生成第 {i+1} 項失敗: {str(e)}")
                failure_count += 1

        total_time = time.time() - start_time

        # 計算統計
        stats = GenerationStats(
            total_count=count,
            success_count=success_count,
            failure_count=failure_count,
            total_time=total_time,
            avg_time=sum(times) / len(times) if times else 0,
            min_time=min(times) if times else 0,
            max_time=max(times) if times else 0
        )

        logger.info(f"批量生成完成: {success_count}/{count} 成功")

        return results, stats

    def parallel_batch_generate(
        self,
        schema: type[BaseModel],
        count: int,
        prompt_template: str,
        max_workers: int = 4
    ) -> tuple[List[BaseModel], GenerationStats]:
        """
        並行批量生成

        Args:
            schema: Pydantic 模型
            count: 生成數量
            prompt_template: 提示模板
            max_workers: 最大並行數

        Returns:
            (生成結果列表, 統計信息)
        """
        logger.info(f"開始並行批量生成 {count} 個 {schema.__name__}, 並行數: {max_workers}")

        results = []
        times = []
        success_count = 0
        failure_count = 0

        # 創建生成器
        generator = generate.json(self.model, schema)

        def generate_item(index: int):
            """生成單個項目"""
            try:
                start = time.time()
                prompt = prompt_template.format(index=index+1)
                result = generator(prompt)
                elapsed = time.time() - start
                return index, result, elapsed, None
            except Exception as e:
                return index, None, 0, str(e)

        start_time = time.time()

        # 並行執行
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(generate_item, i) for i in range(count)]

            for future in as_completed(futures):
                index, result, elapsed, error = future.result()

                if error:
                    logger.error(f"項目 {index+1} 生成失敗: {error}")
                    failure_count += 1
                else:
                    results.append((index, result))
                    times.append(elapsed)
                    success_count += 1

        total_time = time.time() - start_time

        # 按索引排序
        results.sort(key=lambda x: x[0])
        results = [r for _, r in results]

        # 計算統計
        stats = GenerationStats(
            total_count=count,
            success_count=success_count,
            failure_count=failure_count,
            total_time=total_time,
            avg_time=sum(times) / len(times) if times else 0,
            min_time=min(times) if times else 0,
            max_time=max(times) if times else 0
        )

        logger.info(f"並行生成完成: {success_count}/{count} 成功")

        return results, stats


# ==================== 數據生成器 ====================

class SyntheticDataGenerator:
    """
    合成數據生成器

    生成各種測試和訓練數據
    """

    def __init__(self, manager: BatchGenerationManager):
        """
        初始化合成數據生成器

        Args:
            manager: 批量生成管理器
        """
        self.manager = manager
        logger.info("合成數據生成器初始化完成")

    def generate_users(
        self,
        count: int,
        parallel: bool = False
    ) -> tuple[List[TestUser], GenerationStats]:
        """
        生成用戶數據

        Args:
            count: 生成數量
            parallel: 是否並行

        Returns:
            (用戶列表, 統計信息)
        """
        prompt_template = "生成第 {index} 個測試用戶的信息"

        if parallel:
            return self.manager.parallel_batch_generate(
                TestUser,
                count,
                prompt_template
            )
        else:
            return self.manager.batch_generate(
                TestUser,
                count,
                prompt_template
            )

    def generate_products(
        self,
        count: int,
        category: Optional[str] = None
    ) -> tuple[List[TestProduct], GenerationStats]:
        """
        生成產品數據

        Args:
            count: 生成數量
            category: 產品類別

        Returns:
            (產品列表, 統計信息)
        """
        if category:
            prompt_template = f"生成第 {{index}} 個 {category} 類別的產品"
        else:
            prompt_template = "生成第 {index} 個產品的信息"

        return self.manager.batch_generate(
            TestProduct,
            count,
            prompt_template
        )

    def generate_orders(
        self,
        count: int
    ) -> tuple[List[TestOrder], GenerationStats]:
        """
        生成訂單數據

        Args:
            count: 生成數量

        Returns:
            (訂單列表, 統計信息)
        """
        prompt_template = "生成第 {index} 個測試訂單"

        return self.manager.batch_generate(
            TestOrder,
            count,
            prompt_template
        )

    def generate_reviews(
        self,
        count: int,
        product_type: str = "電子產品"
    ) -> tuple[List[SyntheticReview], GenerationStats]:
        """
        生成產品評論

        Args:
            count: 生成數量
            product_type: 產品類型

        Returns:
            (評論列表, 統計信息)
        """
        prompt_template = f"為 {product_type} 生成第 {{index}} 條評論"

        return self.manager.batch_generate(
            SyntheticReview,
            count,
            prompt_template
        )

    def generate_logs(
        self,
        count: int,
        log_level: str = "INFO"
    ) -> tuple[List[LogEntry], GenerationStats]:
        """
        生成日誌條目

        Args:
            count: 生成數量
            log_level: 日誌級別

        Returns:
            (日誌列表, 統計信息)
        """
        prompt_template = f"生成第 {{index}} 條 {log_level} 級別的日誌"

        return self.manager.batch_generate(
            LogEntry,
            count,
            prompt_template
        )


# ==================== 數據分析器 ====================

class DataAnalyzer:
    """
    數據分析器

    分析批量生成的數據
    """

    @staticmethod
    def analyze_users(users: List[TestUser]) -> Dict[str, Any]:
        """
        分析用戶數據

        Args:
            users: 用戶列表

        Returns:
            分析結果
        """
        if not users:
            return {}

        ages = [u.age for u in users]
        cities = [u.city for u in users]
        active_count = sum(1 for u in users if u.is_active)

        city_distribution = defaultdict(int)
        for city in cities:
            city_distribution[city] += 1

        return {
            "total_users": len(users),
            "avg_age": sum(ages) / len(ages),
            "min_age": min(ages),
            "max_age": max(ages),
            "active_users": active_count,
            "active_rate": active_count / len(users) * 100,
            "unique_cities": len(set(cities)),
            "top_cities": sorted(
                city_distribution.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }

    @staticmethod
    def analyze_products(products: List[TestProduct]) -> Dict[str, Any]:
        """
        分析產品數據

        Args:
            products: 產品列表

        Returns:
            分析結果
        """
        if not products:
            return {}

        prices = [p.price for p in products]
        ratings = [p.rating for p in products]
        stocks = [p.stock for p in products]

        category_distribution = defaultdict(int)
        for product in products:
            category_distribution[product.category] += 1

        return {
            "total_products": len(products),
            "avg_price": sum(prices) / len(prices),
            "min_price": min(prices),
            "max_price": max(prices),
            "avg_rating": sum(ratings) / len(ratings),
            "total_stock": sum(stocks),
            "out_of_stock": sum(1 for s in stocks if s == 0),
            "unique_categories": len(set(category_distribution.keys())),
            "category_distribution": dict(category_distribution)
        }

    @staticmethod
    def analyze_reviews(reviews: List[SyntheticReview]) -> Dict[str, Any]:
        """
        分析評論數據

        Args:
            reviews: 評論列表

        Returns:
            分析結果
        """
        if not reviews:
            return {}

        ratings = [r.rating for r in reviews]
        helpful_counts = [r.helpful_count for r in reviews]

        rating_distribution = defaultdict(int)
        for rating in ratings:
            rating_distribution[rating] += 1

        return {
            "total_reviews": len(reviews),
            "avg_rating": sum(ratings) / len(ratings),
            "rating_distribution": dict(rating_distribution),
            "avg_helpful_count": sum(helpful_counts) / len(helpful_counts),
            "positive_reviews": sum(1 for r in ratings if r >= 4),
            "negative_reviews": sum(1 for r in ratings if r <= 2)
        }

    @staticmethod
    def print_analysis(analysis: Dict[str, Any], title: str):
        """
        打印分析結果

        Args:
            analysis: 分析結果
            title: 標題
        """
        print("\n" + "="*60)
        print(f"{title}")
        print("="*60)

        for key, value in analysis.items():
            if isinstance(value, float):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")

        print("="*60)


# ==================== 數據導出器 ====================

class DataExporter:
    """
    數據導出器

    導出生成的數據
    """

    @staticmethod
    def export_to_json(
        data: List[BaseModel],
        filename: str
    ):
        """
        導出為 JSON

        Args:
            data: 數據列表
            filename: 文件名
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json_data = [item.dict() for item in data]
                json.dump(json_data, f, ensure_ascii=False, indent=2)

            logger.info(f"數據已導出到 {filename}")

        except Exception as e:
            logger.error(f"導出失敗: {str(e)}")

    @staticmethod
    def export_to_csv(
        data: List[BaseModel],
        filename: str
    ):
        """
        導出為 CSV

        Args:
            data: 數據列表
            filename: 文件名
        """
        try:
            import csv

            if not data:
                return

            # 獲取字段名
            fieldnames = data[0].dict().keys()

            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for item in data:
                    writer.writerow(item.dict())

            logger.info(f"數據已導出到 {filename}")

        except Exception as e:
            logger.error(f"導出失敗: {str(e)}")


# ==================== 示例運行器 ====================

def run_user_generation_example():
    """運行用戶生成示例"""
    print("\n" + "="*60)
    print("示例 1: 批量生成用戶數據")
    print("="*60)

    manager = BatchGenerationManager()
    generator = SyntheticDataGenerator(manager)

    # 生成用戶
    print("\n生成 50 個測試用戶...")
    users, stats = generator.generate_users(50)

    print(stats)

    # 分析數據
    analysis = DataAnalyzer.analyze_users(users)
    DataAnalyzer.print_analysis(analysis, "用戶數據分析")

    # 顯示樣本
    print("\n用戶樣本 (前 3 個):")
    for user in users[:3]:
        print(f"  - {user.username} ({user.email}), {user.age}歲, {user.city}")


def run_product_generation_example():
    """運行產品生成示例"""
    print("\n" + "="*60)
    print("示例 2: 批量生成產品數據")
    print("="*60)

    manager = BatchGenerationManager()
    generator = SyntheticDataGenerator(manager)

    # 生成產品
    print("\n生成 30 個電子產品...")
    products, stats = generator.generate_products(30, "電子產品")

    print(stats)

    # 分析數據
    analysis = DataAnalyzer.analyze_products(products)
    DataAnalyzer.print_analysis(analysis, "產品數據分析")

    # 顯示樣本
    print("\n產品樣本 (前 3 個):")
    for product in products[:3]:
        print(f"  - {product.name}: ${product.price:.2f}, 評分: {product.rating}/5")


def run_review_generation_example():
    """運行評論生成示例"""
    print("\n" + "="*60)
    print("示例 3: 批量生成產品評論")
    print("="*60)

    manager = BatchGenerationManager()
    generator = SyntheticDataGenerator(manager)

    # 生成評論
    print("\n生成 20 條產品評論...")
    reviews, stats = generator.generate_reviews(20)

    print(stats)

    # 分析數據
    analysis = DataAnalyzer.analyze_reviews(reviews)
    DataAnalyzer.print_analysis(analysis, "評論數據分析")

    # 顯示樣本
    print("\n評論樣本 (前 2 條):")
    for review in reviews[:2]:
        print(f"\n  產品: {review.product_name}")
        print(f"  評分: {review.rating}/5")
        print(f"  標題: {review.title}")
        print(f"  內容: {review.content[:100]}...")


def run_parallel_generation_example():
    """運行並行生成示例"""
    print("\n" + "="*60)
    print("示例 4: 並行批量生成")
    print("="*60)

    manager = BatchGenerationManager()
    generator = SyntheticDataGenerator(manager)

    # 順序生成
    print("\n順序生成 20 個用戶...")
    users_seq, stats_seq = generator.generate_users(20, parallel=False)
    print("順序生成統計:")
    print(stats_seq)

    # 並行生成
    print("\n並行生成 20 個用戶...")
    users_par, stats_par = generator.generate_users(20, parallel=True)
    print("並行生成統計:")
    print(stats_par)

    # 性能對比
    speedup = stats_seq.total_time / stats_par.total_time
    print(f"\n加速比: {speedup:.2f}x")


def main():
    """主函數"""
    try:
        print("\n開始運行批量生成示例...")

        run_user_generation_example()
        run_product_generation_example()
        run_review_generation_example()
        run_parallel_generation_example()

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
