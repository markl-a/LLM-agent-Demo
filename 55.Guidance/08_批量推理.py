#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Guidance 批量推理示例
====================================================

本模塊展示如何使用 Guidance 進行高效的批量推理:
1. 基本批量處理
2. 並行推理優化
3. 批次大小調整
4. 進度跟蹤和監控
5. 錯誤處理和重試
6. 結果聚合
7. 緩存策略
8. 性能優化技巧

批量推理是生產環境中的常見需求，Guidance 提供了
多種優化策略來提高吞吐量和降低延遲。

作者: Guidance 示例團隊
日期: 2025-01-01
"""

import os
import sys
from typing import List, Dict, Any, Optional, Callable
import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import hashlib

try:
    from guidance import models, gen, select
    import guidance
except ImportError:
    print("錯誤: 請先安裝 guidance 庫")
    sys.exit(1)


class BatchInference:
    """
    批量推理演示類

    展示如何高效地處理大規模推理任務。
    """

    def __init__(self, model_name: str = "gpt-4", api_key: Optional[str] = None):
        """初始化批量推理器"""
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.cache: Dict[str, Any] = {}
        self.stats = {
            "total_processed": 0,
            "cache_hits": 0,
            "errors": 0,
            "total_time": 0.0
        }

    def example_basic_batch(self) -> None:
        """
        示例 1: 基本批量處理

        演示如何處理一批輸入。
        """
        print(f"\n{'='*60}")
        print("示例 1: 基本批量處理")
        print(f"{'='*60}\n")

        if not self.api_key:
            print("⚠️  未設置 API 密鑰，跳過此示例")
            return

        # 準備批量輸入
        inputs = [
            "解釋機器學習",
            "什麼是深度學習",
            "介紹神經網絡",
            "說明自然語言處理",
            "描述計算機視覺"
        ]

        print(f"處理 {len(inputs)} 個輸入...\n")

        results = []
        start_time = time.time()

        for i, prompt in enumerate(inputs, 1):
            print(f"處理 {i}/{len(inputs)}: {prompt}")

            lm = models.OpenAI(
                model=self.model_name,
                api_key=self.api_key
            )

            lm += prompt + ": "
            lm += gen(name="answer", max_tokens=80)

            result = {
                "prompt": prompt,
                "answer": lm["answer"],
                "timestamp": datetime.now().isoformat()
            }

            results.append(result)
            print(f"  回答: {lm['answer'][:60]}...\n")

        elapsed = time.time() - start_time

        print(f"批量處理完成:")
        print(f"  總數: {len(results)}")
        print(f"  耗時: {elapsed:.2f}s")
        print(f"  平均: {elapsed/len(results):.2f}s/項\n")

    def example_parallel_processing(self) -> None:
        """
        示例 2: 並行處理

        演示如何使用多線程並行處理批量任務。
        """
        print(f"\n{'='*60}")
        print("示例 2: 並行處理")
        print(f"{'='*60}\n")

        if not self.api_key:
            print("⚠️  未設置 API 密鑰，跳過此示例")
            return

        inputs = [
            "Python 的優勢",
            "JavaScript 的特點",
            "Java 的應用",
            "Go 的性能",
            "Rust 的安全性",
            "C++ 的複雜性",
            "TypeScript 的類型",
            "Kotlin 的簡潔性"
        ]

        def process_single(prompt: str) -> Dict[str, Any]:
            """處理單個輸入"""
            try:
                lm = models.OpenAI(
                    model=self.model_name,
                    api_key=self.api_key
                )

                lm += prompt + ": "
                lm += gen(name="answer", max_tokens=60)

                return {
                    "prompt": prompt,
                    "answer": lm["answer"],
                    "status": "success"
                }

            except Exception as e:
                return {
                    "prompt": prompt,
                    "error": str(e),
                    "status": "error"
                }

        print(f"並行處理 {len(inputs)} 個輸入 (最多 4 個並發)...\n")

        start_time = time.time()
        results = []

        # 使用線程池並行處理
        with ThreadPoolExecutor(max_workers=4) as executor:
            # 提交所有任務
            future_to_prompt = {
                executor.submit(process_single, prompt): prompt
                for prompt in inputs
            }

            # 收集結果
            for future in as_completed(future_to_prompt):
                prompt = future_to_prompt[future]
                try:
                    result = future.result()
                    results.append(result)
                    print(f"✓ 完成: {prompt}")
                except Exception as e:
                    print(f"✗ 失敗: {prompt} - {str(e)}")

        elapsed = time.time() - start_time

        # 統計
        success_count = sum(1 for r in results if r["status"] == "success")
        error_count = len(results) - success_count

        print(f"\n並行處理完成:")
        print(f"  成功: {success_count}")
        print(f"  失敗: {error_count}")
        print(f"  耗時: {elapsed:.2f}s")
        print(f"  平均: {elapsed/len(results):.2f}s/項\n")

    def example_batch_with_progress(self) -> None:
        """
        示例 3: 進度跟蹤

        演示如何在批量處理時顯示進度。
        """
        print(f"\n{'='*60}")
        print("示例 3: 進度跟蹤")
        print(f"{'='*60}\n")

        if not self.api_key:
            print("⚠️  未設置 API 密鑰，跳過此示例")
            return

        inputs = [f"主題 {i}" for i in range(1, 11)]

        print(f"處理 {len(inputs)} 個輸入 (帶進度顯示)...\n")

        results = []
        start_time = time.time()

        for i, prompt in enumerate(inputs, 1):
            # 進度條
            progress = i / len(inputs)
            bar_length = 40
            filled = int(bar_length * progress)
            bar = '█' * filled + '-' * (bar_length - filled)

            print(f"\r進度: [{bar}] {i}/{len(inputs)} ({progress*100:.1f}%)", end='', flush=True)

            # 處理
            try:
                lm = models.OpenAI(
                    model=self.model_name,
                    api_key=self.api_key,
                    max_tokens=50
                )

                lm += f"簡要介紹{prompt}: "
                lm += gen(name="answer", max_tokens=50)

                results.append({
                    "prompt": prompt,
                    "answer": lm["answer"],
                    "status": "success"
                })

            except Exception as e:
                results.append({
                    "prompt": prompt,
                    "error": str(e),
                    "status": "error"
                })

        print()  # 換行

        elapsed = time.time() - start_time

        print(f"\n處理完成:")
        print(f"  總數: {len(results)}")
        print(f"  成功: {sum(1 for r in results if r['status'] == 'success')}")
        print(f"  耗時: {elapsed:.2f}s\n")

    def example_batch_with_retry(self) -> None:
        """
        示例 4: 錯誤重試

        演示如何為失敗的任務實現重試機制。
        """
        print(f"\n{'='*60}")
        print("示例 4: 錯誤重試")
        print(f"{'='*60}\n")

        if not self.api_key:
            print("⚠️  未設置 API 密鑰，跳過此示例")
            return

        def process_with_retry(prompt: str, max_retries: int = 3) -> Dict[str, Any]:
            """帶重試的處理函數"""
            for attempt in range(max_retries):
                try:
                    lm = models.OpenAI(
                        model=self.model_name,
                        api_key=self.api_key,
                        max_tokens=60
                    )

                    lm += prompt + ": "
                    lm += gen(name="answer", max_tokens=60)

                    return {
                        "prompt": prompt,
                        "answer": lm["answer"],
                        "attempts": attempt + 1,
                        "status": "success"
                    }

                except Exception as e:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # 指數退避
                        print(f"  重試 {attempt + 1}/{max_retries} (等待 {wait_time}s): {prompt}")
                        time.sleep(wait_time)
                    else:
                        return {
                            "prompt": prompt,
                            "error": str(e),
                            "attempts": max_retries,
                            "status": "error"
                        }

        inputs = [
            "量子計算原理",
            "區塊鏈技術",
            "邊緣計算應用"
        ]

        print(f"處理 {len(inputs)} 個輸入 (最多重試 3 次)...\n")

        results = []
        for prompt in inputs:
            print(f"處理: {prompt}")
            result = process_with_retry(prompt, max_retries=3)
            results.append(result)
            print(f"  狀態: {result['status']} (嘗試 {result['attempts']} 次)\n")

        # 統計
        success_count = sum(1 for r in results if r["status"] == "success")
        total_attempts = sum(r["attempts"] for r in results)
        avg_attempts = total_attempts / len(results)

        print(f"重試統計:")
        print(f"  成功率: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
        print(f"  平均嘗試次數: {avg_attempts:.1f}\n")

    def example_batch_caching(self) -> None:
        """
        示例 5: 批量處理緩存

        演示如何使用緩存加速重複查詢。
        """
        print(f"\n{'='*60}")
        print("示例 5: 批量處理緩存")
        print(f"{'='*60}\n")

        if not self.api_key:
            print("⚠️  未設置 API 密鑰，跳過此示例")
            return

        def get_cache_key(prompt: str) -> str:
            """生成緩存鍵"""
            return hashlib.md5(prompt.encode()).hexdigest()

        def process_with_cache(prompt: str) -> Dict[str, Any]:
            """帶緩存的處理函數"""
            cache_key = get_cache_key(prompt)

            # 檢查緩存
            if cache_key in self.cache:
                self.stats["cache_hits"] += 1
                return {
                    "prompt": prompt,
                    "answer": self.cache[cache_key],
                    "cached": True,
                    "status": "success"
                }

            # 未命中緩存，實際處理
            try:
                lm = models.OpenAI(
                    model=self.model_name,
                    api_key=self.api_key,
                    max_tokens=60
                )

                lm += prompt + ": "
                lm += gen(name="answer", max_tokens=60)

                # 存入緩存
                self.cache[cache_key] = lm["answer"]

                return {
                    "prompt": prompt,
                    "answer": lm["answer"],
                    "cached": False,
                    "status": "success"
                }

            except Exception as e:
                return {
                    "prompt": prompt,
                    "error": str(e),
                    "cached": False,
                    "status": "error"
                }

        # 包含重複的輸入
        inputs = [
            "什麼是 AI",
            "什麼是機器學習",
            "什麼是 AI",  # 重複
            "什麼是深度學習",
            "什麼是機器學習",  # 重複
            "什麼是 AI"  # 重複
        ]

        print(f"處理 {len(inputs)} 個輸入 (包含重複)...\n")

        results = []
        start_time = time.time()

        for i, prompt in enumerate(inputs, 1):
            result = process_with_cache(prompt)
            results.append(result)

            cache_status = "✓ 緩存命中" if result.get("cached") else "✗ 緩存未命中"
            print(f"{i}. {prompt}: {cache_status}")

        elapsed = time.time() - start_time

        # 統計
        cache_hits = sum(1 for r in results if r.get("cached", False))
        cache_misses = len(results) - cache_hits

        print(f"\n緩存統計:")
        print(f"  總請求: {len(results)}")
        print(f"  緩存命中: {cache_hits}")
        print(f"  緩存未命中: {cache_misses}")
        print(f"  命中率: {cache_hits/len(results)*100:.1f}%")
        print(f"  耗時: {elapsed:.2f}s\n")

    def example_batch_size_optimization(self) -> None:
        """
        示例 6: 批次大小優化

        演示如何調整批次大小以優化性能。
        """
        print(f"\n{'='*60}")
        print("示例 6: 批次大小優化")
        print(f"{'='*60}\n")

        if not self.api_key:
            print("⚠️  未設置 API 密鑰，跳過此示例")
            return

        # 生成測試數據
        inputs = [f"測試輸入 {i}" for i in range(1, 21)]

        batch_sizes = [1, 2, 5, 10]

        print(f"測試不同批次大小的性能...\n")

        for batch_size in batch_sizes:
            print(f"批次大小: {batch_size}")

            start_time = time.time()
            processed = 0

            # 分批處理
            for i in range(0, len(inputs), batch_size):
                batch = inputs[i:i+batch_size]

                # 模擬批次處理
                for prompt in batch:
                    try:
                        lm = models.OpenAI(
                            model=self.model_name,
                            api_key=self.api_key,
                            max_tokens=20
                        )

                        lm += f"{prompt}: "
                        lm += gen(name="answer", max_tokens=20)

                        processed += 1

                    except Exception as e:
                        print(f"  錯誤: {str(e)}")

            elapsed = time.time() - start_time

            print(f"  處理: {processed}/{len(inputs)}")
            print(f"  耗時: {elapsed:.2f}s")
            print(f"  吞吐量: {processed/elapsed:.2f} 項/秒\n")

    def example_result_aggregation(self) -> None:
        """
        示例 7: 結果聚合

        演示如何聚合和分析批量處理結果。
        """
        print(f"\n{'='*60}")
        print("示例 7: 結果聚合")
        print(f"{'='*60}\n")

        if not self.api_key:
            print("⚠️  未設置 API 密鑰，跳過此示例")
            return

        # 分類任務
        texts = [
            "這個產品很棒!",
            "質量太差了",
            "還可以",
            "非常滿意",
            "不推薦購買",
            "物有所值",
            "浪費錢",
            "超出預期"
        ]

        print(f"批量情感分析 ({len(texts)} 條評論)...\n")

        results = []

        for text in texts:
            lm = models.OpenAI(
                model=self.model_name,
                api_key=self.api_key
            )

            lm += f"評論: {text}\n情感: "
            lm += select(["正面", "負面", "中性"], name="sentiment")

            results.append({
                "text": text,
                "sentiment": lm["sentiment"]
            })

            print(f"  {text} -> {lm['sentiment']}")

        # 聚合統計
        sentiment_counts = defaultdict(int)
        for r in results:
            sentiment_counts[r["sentiment"]] += 1

        print(f"\n情感分布:")
        for sentiment, count in sentiment_counts.items():
            percentage = count / len(results) * 100
            print(f"  {sentiment}: {count} ({percentage:.1f}%)")

        # 可視化
        print(f"\n可視化:")
        max_count = max(sentiment_counts.values())
        for sentiment, count in sentiment_counts.items():
            bar = '█' * int(count / max_count * 30)
            print(f"  {sentiment:6s} {bar} {count}")

        print()

    def example_streaming_batch(self) -> None:
        """
        示例 8: 流式批量處理

        演示如何處理流式輸入的批量任務。
        """
        print(f"\n{'='*60}")
        print("示例 8: 流式批量處理")
        print(f"{'='*60}\n")

        if not self.api_key:
            print("⚠️  未設置 API 密鑰，跳過此示例")
            return

        def input_generator():
            """模擬流式輸入"""
            topics = ["AI", "ML", "DL", "NLP", "CV"]
            for topic in topics:
                yield f"介紹{topic}"
                time.sleep(0.5)  # 模擬數據到達間隔

        print("流式批量處理 (數據逐步到達)...\n")

        results = []
        start_time = time.time()

        for i, prompt in enumerate(input_generator(), 1):
            print(f"[{i}] 收到輸入: {prompt}")

            try:
                lm = models.OpenAI(
                    model=self.model_name,
                    api_key=self.api_key,
                    max_tokens=40
                )

                lm += prompt + ": "
                lm += gen(name="answer", max_tokens=40)

                result = {
                    "prompt": prompt,
                    "answer": lm["answer"][:50] + "...",
                    "timestamp": time.time() - start_time
                }

                results.append(result)
                print(f"    完成: {result['answer']}")
                print(f"    耗時: {result['timestamp']:.2f}s\n")

            except Exception as e:
                print(f"    錯誤: {str(e)}\n")

        total_time = time.time() - start_time

        print(f"流式處理完成:")
        print(f"  總數: {len(results)}")
        print(f"  總耗時: {total_time:.2f}s\n")

    def example_batch_monitoring(self) -> None:
        """
        示例 9: 批量處理監控

        演示如何監控批量處理的性能指標。
        """
        print(f"\n{'='*60}")
        print("示例 9: 批量處理監控")
        print(f"{'='*60}\n")

        if not self.api_key:
            print("⚠️  未設置 API 密鑰，跳過此示例")
            return

        inputs = [f"查詢 {i}" for i in range(1, 11)]

        metrics = {
            "total": 0,
            "success": 0,
            "error": 0,
            "latencies": [],
            "token_counts": []
        }

        print(f"監控批量處理性能...\n")

        for i, prompt in enumerate(inputs, 1):
            start = time.time()
            metrics["total"] += 1

            try:
                lm = models.OpenAI(
                    model=self.model_name,
                    api_key=self.api_key,
                    max_tokens=50
                )

                lm += f"{prompt}: "
                lm += gen(name="answer", max_tokens=50)

                latency = time.time() - start
                token_count = len(lm["answer"])

                metrics["success"] += 1
                metrics["latencies"].append(latency)
                metrics["token_counts"].append(token_count)

                print(f"[{i}] {prompt}")
                print(f"    延遲: {latency:.3f}s")
                print(f"    Token: {token_count}\n")

            except Exception as e:
                metrics["error"] += 1
                print(f"[{i}] {prompt}")
                print(f"    錯誤: {str(e)}\n")

        # 計算統計指標
        if metrics["latencies"]:
            avg_latency = sum(metrics["latencies"]) / len(metrics["latencies"])
            min_latency = min(metrics["latencies"])
            max_latency = max(metrics["latencies"])
            avg_tokens = sum(metrics["token_counts"]) / len(metrics["token_counts"])

            print(f"性能指標:")
            print(f"  總請求: {metrics['total']}")
            print(f"  成功: {metrics['success']}")
            print(f"  失敗: {metrics['error']}")
            print(f"  成功率: {metrics['success']/metrics['total']*100:.1f}%")
            print(f"\n延遲統計:")
            print(f"  平均: {avg_latency:.3f}s")
            print(f"  最小: {min_latency:.3f}s")
            print(f"  最大: {max_latency:.3f}s")
            print(f"\nToken 統計:")
            print(f"  平均: {avg_tokens:.0f} tokens\n")

    def example_production_batch(self) -> None:
        """
        示例 10: 生產級批量處理

        演示一個完整的生產級批量處理實現。
        """
        print(f"\n{'='*60}")
        print("示例 10: 生產級批量處理")
        print(f"{'='*60}\n")

        if not self.api_key:
            print("⚠️  未設置 API 密鑰，跳過此示例")
            return

        print("生產級批量處理系統特性:")

        features = [
            "✓ 並行處理 (多線程)",
            "✓ 錯誤重試 (指數退避)",
            "✓ 結果緩存",
            "✓ 進度跟蹤",
            "✓ 性能監控",
            "✓ 日誌記錄",
            "✓ 優雅降級",
            "✓ 資源限制"
        ]

        for feature in features:
            print(f"  {feature}")

        print("\n示例配置:")

        config = {
            "batch_size": 10,
            "max_workers": 4,
            "max_retries": 3,
            "timeout": 30,
            "cache_enabled": True,
            "monitoring_enabled": True,
            "log_level": "INFO"
        }

        print(json.dumps(config, indent=2))

        print("\n完整實現請參考生產部署示例 (10_生產部署.py)\n")

    def run_all_examples(self) -> None:
        """運行所有示例"""
        print(f"\n{'='*60}")
        print("Guidance 批量推理 - 完整示例")
        print(f"{'='*60}")

        self.example_basic_batch()
        self.example_parallel_processing()
        self.example_batch_with_progress()
        self.example_batch_with_retry()
        self.example_batch_caching()
        self.example_batch_size_optimization()
        self.example_result_aggregation()
        self.example_streaming_batch()
        self.example_batch_monitoring()
        self.example_production_batch()

        print(f"\n{'='*60}")
        print("執行摘要")
        print(f"{'='*60}")
        print(f"✓ 所有批量推理示例執行完成!")
        print(f"\n統計數據:")
        print(json.dumps(self.stats, indent=2))


def main():
    """主函數"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║         Guidance 框架 - 批量推理示例                       ║
    ║                                                            ║
    ║  高效處理大規模推理任務                                    ║
    ║  包括並行處理、緩存、重試等優化策略                        ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        return

    batch = BatchInference(
        model_name="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    try:
        batch.run_all_examples()
    except KeyboardInterrupt:
        print("\n\n⚠️  用戶中斷執行")
    except Exception as e:
        print(f"\n✗ 執行出錯: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
