"""
Langfuse 數據集管理示例

這個示例展示如何使用 Langfuse 管理測試數據集，包括：
- 數據集創建和管理
- 測試用例組織
- 批量測試執行
- 結果追蹤和比較
- 回歸測試
- 基準測試

主要內容：
1. 數據集基礎操作
2. 測試用例管理
3. 批量評估執行
4. 結果分析和對比
5. 回歸測試流程
6. 性能基準測試
7. 數據集版本管理

作者: Langfuse Team
日期: 2025-01-01
"""

import os
import time
import json
import random
from datetime import datetime
from typing import Dict, List, Any, Optional
from langfuse import Langfuse
from openai import OpenAI


# ============================================================================
# 第一部分：數據集基礎操作
# ============================================================================

class DatasetManagement:
    """
    數據集管理

    提供數據集的創建、更新和組織功能。
    """

    def __init__(self, langfuse: Langfuse):
        """
        初始化數據集管理器

        Args:
            langfuse: Langfuse 客戶端實例
        """
        self.langfuse = langfuse
        self.openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "sk-demo")
        )

    def create_dataset_example(self):
        """
        創建數據集示例

        展示如何創建和組織測試數據集。
        """
        print("\n" + "="*60)
        print("創建數據集示例")
        print("="*60)

        # 定義數據集
        dataset_config = {
            "name": "qa-evaluation-dataset",
            "description": "問答系統評估數據集",
            "version": "v1.0",
            "created_at": datetime.now().isoformat(),
            "metadata": {
                "domain": "general-knowledge",
                "language": "zh-TW",
                "size": 20
            }
        }

        print(f"📚 創建數據集:")
        print(f"   名稱: {dataset_config['name']}")
        print(f"   描述: {dataset_config['description']}")
        print(f"   版本: {dataset_config['version']}")

        # 創建測試用例
        test_cases = [
            {
                "id": "tc-001",
                "input": "什麼是機器學習？",
                "expected_output": "機器學習是人工智慧的一個分支，讓計算機能夠從數據中學習並改進其性能，而無需明確編程。",
                "category": "基礎概念",
                "difficulty": "easy",
                "tags": ["AI", "基礎", "定義"]
            },
            {
                "id": "tc-002",
                "input": "解釋深度學習和機器學習的區別",
                "expected_output": "深度學習是機器學習的子集，使用多層神經網絡。機器學習包含更廣泛的算法，而深度學習專注於神經網絡方法。",
                "category": "概念比較",
                "difficulty": "medium",
                "tags": ["AI", "深度學習", "比較"]
            },
            {
                "id": "tc-003",
                "input": "什麼是過擬合？如何避免？",
                "expected_output": "過擬合是模型在訓練數據上表現很好但在新數據上表現不佳。可通過正則化、交叉驗證、增加數據等方法避免。",
                "category": "進階概念",
                "difficulty": "hard",
                "tags": ["機器學習", "問題", "解決方案"]
            },
            {
                "id": "tc-004",
                "input": "常見的機器學習算法有哪些？",
                "expected_output": "常見算法包括：線性回歸、邏輯回歸、決策樹、隨機森林、支持向量機、K近鄰、神經網絡等。",
                "category": "技術細節",
                "difficulty": "medium",
                "tags": ["算法", "分類"]
            },
            {
                "id": "tc-005",
                "input": "什麼是自然語言處理？",
                "expected_output": "自然語言處理（NLP）是人工智慧的一個領域，專注於使計算機能夠理解、解釋和生成人類語言。",
                "category": "基礎概念",
                "difficulty": "easy",
                "tags": ["NLP", "AI", "定義"]
            }
        ]

        print(f"\n📝 測試用例:")
        for tc in test_cases:
            print(f"   [{tc['id']}] {tc['input'][:50]}...")
            print(f"            難度: {tc['difficulty']}, 分類: {tc['category']}")

        # 將數據集保存到元數據中（實際應用中可能使用 Langfuse Dataset API）
        dataset_trace = self.langfuse.trace(
            name="dataset-creation",
            metadata={
                "dataset_config": dataset_config,
                "test_cases": test_cases,
                "operation": "create_dataset"
            },
            tags=["dataset", "qa-evaluation"]
        )

        print(f"\n✅ 數據集創建完成")
        print(f"   包含 {len(test_cases)} 個測試用例")

        return test_cases

    def organize_test_cases(self):
        """
        組織測試用例示例

        按不同維度組織和分類測試用例。
        """
        print("\n" + "="*60)
        print("測試用例組織示例")
        print("="*60)

        # 創建多個數據集分類
        datasets = {
            "basic_concepts": {
                "name": "基礎概念測試集",
                "count": 10,
                "difficulty": "easy"
            },
            "advanced_concepts": {
                "name": "進階概念測試集",
                "count": 15,
                "difficulty": "hard"
            },
            "edge_cases": {
                "name": "邊界案例測試集",
                "count": 8,
                "difficulty": "hard"
            },
            "multilingual": {
                "name": "多語言測試集",
                "count": 12,
                "difficulty": "medium"
            }
        }

        print("📂 數據集組織結構:\n")

        for ds_id, ds_info in datasets.items():
            print(f"   📊 {ds_info['name']}")
            print(f"      • ID: {ds_id}")
            print(f"      • 用例數: {ds_info['count']}")
            print(f"      • 難度: {ds_info['difficulty']}")

            # 記錄數據集元數據
            trace = self.langfuse.trace(
                name=f"dataset-{ds_id}",
                metadata={
                    "dataset_id": ds_id,
                    "dataset_info": ds_info,
                    "organization": "by_difficulty_and_domain"
                },
                tags=["dataset", ds_id, ds_info['difficulty']]
            )

        print(f"\n✅ 測試用例組織完成")
        print(f"   總數據集數: {len(datasets)}")
        print(f"   總測試用例: {sum(ds['count'] for ds in datasets.values())}")


# ============================================================================
# 第二部分：批量評估執行
# ============================================================================

class BatchEvaluation:
    """
    批量評估

    執行數據集上的批量測試。
    """

    def __init__(self, langfuse: Langfuse):
        self.langfuse = langfuse
        self.openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "sk-demo")
        )

    def run_batch_evaluation(self, test_cases: List[Dict]):
        """
        運行批量評估

        對測試用例集執行批量評估。

        Args:
            test_cases: 測試用例列表
        """
        print("\n" + "="*60)
        print("批量評估執行示例")
        print("="*60)

        print(f"🧪 開始批量評估...")
        print(f"   測試用例數: {len(test_cases)}")

        # 創建批次追蹤
        batch_trace = self.langfuse.trace(
            name="batch-evaluation-run",
            metadata={
                "batch_size": len(test_cases),
                "start_time": datetime.now().isoformat(),
                "model": "gpt-3.5-turbo"
            },
            tags=["batch-evaluation", "qa-test"]
        )

        results = []
        passed = 0
        failed = 0

        print(f"\n執行進度:")

        for idx, tc in enumerate(test_cases, 1):
            print(f"   [{idx}/{len(test_cases)}] {tc['id']}...", end=" ")

            # 創建單個測試的追蹤
            test_trace = self.langfuse.trace(
                name=f"test-{tc['id']}",
                input={"question": tc['input']},
                metadata={
                    "test_case_id": tc['id'],
                    "batch_id": batch_trace.id,
                    "expected_output": tc.get('expected_output'),
                    "category": tc.get('category'),
                    "difficulty": tc.get('difficulty')
                },
                tags=["test-case"] + tc.get('tags', [])
            )

            try:
                # 執行測試（這裡模擬，實際應調用 LLM）
                # 模擬成功率約 80%
                is_correct = random.random() < 0.8

                # 模擬響應
                if is_correct:
                    output = tc.get('expected_output', "正確答案")
                    score = random.uniform(0.85, 1.0)
                else:
                    output = "不完全正確的答案"
                    score = random.uniform(0.4, 0.7)

                # 記錄結果
                generation = test_trace.generation(
                    name="model-response",
                    model="gpt-3.5-turbo",
                    input=[{"role": "user", "content": tc['input']}],
                    output=output
                )

                generation.end(
                    usage={
                        "prompt_tokens": len(tc['input']) // 4,
                        "completion_tokens": len(output) // 4,
                        "total_tokens": (len(tc['input']) + len(output)) // 4
                    }
                )

                # 添加評分
                test_trace.score(
                    name="correctness",
                    value=score,
                    comment="正確" if is_correct else "需改進"
                )

                # 更新統計
                if is_correct:
                    passed += 1
                    status = "✅"
                else:
                    failed += 1
                    status = "❌"

                results.append({
                    "test_case_id": tc['id'],
                    "passed": is_correct,
                    "score": score,
                    "difficulty": tc.get('difficulty')
                })

                print(f"{status}")

            except Exception as e:
                print(f"❌ 失敗: {e}")
                failed += 1

            time.sleep(0.05)  # 避免過快

        # 更新批次追蹤
        pass_rate = passed / len(test_cases) if len(test_cases) > 0 else 0

        batch_trace.update(
            output={
                "total_tests": len(test_cases),
                "passed": passed,
                "failed": failed,
                "pass_rate": pass_rate
            },
            metadata={
                "end_time": datetime.now().isoformat(),
                "results": results
            }
        )

        # 顯示結果
        print(f"\n" + "="*60)
        print(f"批量評估結果:")
        print(f"   總測試數: {len(test_cases)}")
        print(f"   通過: {passed} ✅")
        print(f"   失敗: {failed} ❌")
        print(f"   通過率: {pass_rate:.1%}")

        # 按難度分析
        print(f"\n按難度分析:")
        difficulties = {}
        for result in results:
            diff = result.get('difficulty', 'unknown')
            if diff not in difficulties:
                difficulties[diff] = {"passed": 0, "total": 0}

            difficulties[diff]["total"] += 1
            if result["passed"]:
                difficulties[diff]["passed"] += 1

        for diff, stats in difficulties.items():
            rate = stats["passed"] / stats["total"] if stats["total"] > 0 else 0
            print(f"   {diff:10s}: {stats['passed']}/{stats['total']} ({rate:.1%})")

        print(f"\n✅ 批量評估完成")

        return results


# ============================================================================
# 第三部分：結果分析和對比
# ============================================================================

class ResultAnalysis:
    """
    結果分析

    分析和對比評估結果。
    """

    def __init__(self, langfuse: Langfuse):
        self.langfuse = langfuse

    def compare_model_performance(self):
        """
        模型性能對比示例

        對比不同模型在相同數據集上的表現。
        """
        print("\n" + "="*60)
        print("模型性能對比示例")
        print("="*60)

        # 模擬兩個模型的評估結果
        models = {
            "gpt-3.5-turbo": {
                "total_tests": 50,
                "passed": 38,
                "avg_score": 0.82,
                "avg_latency": 1.2,
                "cost_per_test": 0.002
            },
            "gpt-4": {
                "total_tests": 50,
                "passed": 45,
                "avg_score": 0.91,
                "avg_latency": 2.5,
                "cost_per_test": 0.015
            }
        }

        print(f"\n📊 模型性能對比:")
        print(f"{'指標':<20} {'GPT-3.5-Turbo':<20} {'GPT-4':<20} {'差異':<15}")
        print("-" * 80)

        # 通過率
        for model_name, stats in models.items():
            pass_rate = stats["passed"] / stats["total_tests"]
            models[model_name]["pass_rate"] = pass_rate

        print(f"{'通過率':<20} "
              f"{models['gpt-3.5-turbo']['pass_rate']:<20.1%} "
              f"{models['gpt-4']['pass_rate']:<20.1%} "
              f"{models['gpt-4']['pass_rate'] - models['gpt-3.5-turbo']['pass_rate']:<14.1%}")

        # 平均分數
        print(f"{'平均分數':<20} "
              f"{models['gpt-3.5-turbo']['avg_score']:<20.2f} "
              f"{models['gpt-4']['avg_score']:<20.2f} "
              f"{models['gpt-4']['avg_score'] - models['gpt-3.5-turbo']['avg_score']:<14.2f}")

        # 平均延遲
        print(f"{'平均延遲 (s)':<20} "
              f"{models['gpt-3.5-turbo']['avg_latency']:<20.2f} "
              f"{models['gpt-4']['avg_latency']:<20.2f} "
              f"{models['gpt-4']['avg_latency'] - models['gpt-3.5-turbo']['avg_latency']:<14.2f}")

        # 每次測試成本
        print(f"{'成本/測試 ($)':<20} "
              f"{models['gpt-3.5-turbo']['cost_per_test']:<20.4f} "
              f"{models['gpt-4']['cost_per_test']:<20.4f} "
              f"{models['gpt-4']['cost_per_test'] - models['gpt-3.5-turbo']['cost_per_test']:<14.4f}")

        # 總成本
        total_cost_35 = models['gpt-3.5-turbo']['cost_per_test'] * models['gpt-3.5-turbo']['total_tests']
        total_cost_4 = models['gpt-4']['cost_per_test'] * models['gpt-4']['total_tests']

        print(f"{'總成本 ($)':<20} "
              f"{total_cost_35:<20.4f} "
              f"{total_cost_4:<20.4f} "
              f"{total_cost_4 - total_cost_35:<14.4f}")

        # 綜合評估
        print(f"\n💡 綜合評估:")
        print(f"   GPT-4:")
        print(f"      ✅ 準確率更高 (+{(models['gpt-4']['pass_rate'] - models['gpt-3.5-turbo']['pass_rate']):.1%})")
        print(f"      ✅ 質量分數更高 (+{models['gpt-4']['avg_score'] - models['gpt-3.5-turbo']['avg_score']:.2f})")
        print(f"      ❌ 成本更高 ({models['gpt-4']['cost_per_test'] / models['gpt-3.5-turbo']['cost_per_test']:.1f}x)")
        print(f"      ❌ 延遲更高 ({models['gpt-4']['avg_latency'] / models['gpt-3.5-turbo']['avg_latency']:.1f}x)")

        print(f"\n   建議:")
        print(f"      • 對準確性要求高的任務使用 GPT-4")
        print(f"      • 對成本敏感的大批量任務使用 GPT-3.5-Turbo")

        # 記錄對比結果
        comparison_trace = self.langfuse.trace(
            name="model-performance-comparison",
            metadata={
                "models_compared": list(models.keys()),
                "results": models,
                "comparison_date": datetime.now().isoformat()
            },
            tags=["comparison", "performance-analysis"]
        )

        print(f"\n✅ 模型對比完成")

    def version_comparison_example(self):
        """
        版本對比示例

        對比同一系統不同版本的表現。
        """
        print("\n" + "="*60)
        print("版本對比示例")
        print("="*60)

        # 模擬三個版本的結果
        versions = {
            "v1.0": {
                "date": "2024-01-01",
                "pass_rate": 0.72,
                "avg_score": 0.75,
                "avg_latency": 1.8
            },
            "v1.5": {
                "date": "2024-03-01",
                "pass_rate": 0.80,
                "avg_score": 0.82,
                "avg_latency": 1.5
            },
            "v2.0": {
                "date": "2024-06-01",
                "pass_rate": 0.88,
                "avg_score": 0.89,
                "avg_latency": 1.2
            }
        }

        print(f"\n📈 版本演進分析:")
        print(f"{'版本':<10} {'發布日期':<15} {'通過率':<12} {'平均分':<12} {'延遲(s)':<12}")
        print("-" * 70)

        for version, stats in versions.items():
            print(f"{version:<10} {stats['date']:<15} "
                  f"{stats['pass_rate']:<12.1%} "
                  f"{stats['avg_score']:<12.2f} "
                  f"{stats['avg_latency']:<12.2f}")

        # 計算改進
        v1_stats = versions["v1.0"]
        v2_stats = versions["v2.0"]

        print(f"\n📊 v1.0 → v2.0 改進:")
        print(f"   通過率: {v1_stats['pass_rate']:.1%} → {v2_stats['pass_rate']:.1%} "
              f"(+{(v2_stats['pass_rate'] - v1_stats['pass_rate']):.1%})")
        print(f"   平均分: {v1_stats['avg_score']:.2f} → {v2_stats['avg_score']:.2f} "
              f"(+{(v2_stats['avg_score'] - v1_stats['avg_score']):.2f})")
        print(f"   延遲: {v1_stats['avg_latency']:.2f}s → {v2_stats['avg_latency']:.2f}s "
              f"(-{(v1_stats['avg_latency'] - v2_stats['avg_latency']):.2f}s, {((v1_stats['avg_latency'] - v2_stats['avg_latency']) / v1_stats['avg_latency']):.1%} 改善)")

        print(f"\n✅ 版本對比完成")


# ============================================================================
# 第四部分：回歸測試
# ============================================================================

class RegressionTesting:
    """
    回歸測試

    確保新變更不會破壞現有功能。
    """

    def __init__(self, langfuse: Langfuse):
        self.langfuse = langfuse

    def run_regression_test(self):
        """
        運行回歸測試示例

        執行回歸測試並對比結果。
        """
        print("\n" + "="*60)
        print("回歸測試示例")
        print("="*60)

        print(f"🔄 運行回歸測試...\n")

        # 基準測試結果（上一次穩定版本）
        baseline = {
            "version": "v1.5-stable",
            "test_results": {
                "tc-001": {"passed": True, "score": 0.92},
                "tc-002": {"passed": True, "score": 0.88},
                "tc-003": {"passed": True, "score": 0.85},
                "tc-004": {"passed": True, "score": 0.90},
                "tc-005": {"passed": False, "score": 0.65}
            }
        }

        # 當前測試結果
        current = {
            "version": "v2.0-beta",
            "test_results": {
                "tc-001": {"passed": True, "score": 0.93},
                "tc-002": {"passed": True, "score": 0.89},
                "tc-003": {"passed": False, "score": 0.72},  # 回歸！
                "tc-004": {"passed": True, "score": 0.92},
                "tc-005": {"passed": True, "score": 0.88}   # 改進！
            }
        }

        print(f"基準版本: {baseline['version']}")
        print(f"當前版本: {current['version']}\n")

        # 對比結果
        regressions = []
        improvements = []
        unchanged = []

        print(f"{'測試用例':<12} {'基準':<15} {'當前':<15} {'狀態':<15}")
        print("-" * 70)

        for tc_id in baseline["test_results"].keys():
            baseline_result = baseline["test_results"][tc_id]
            current_result = current["test_results"][tc_id]

            baseline_str = f"{'✅' if baseline_result['passed'] else '❌'} {baseline_result['score']:.2f}"
            current_str = f"{'✅' if current_result['passed'] else '❌'} {current_result['score']:.2f}"

            # 判斷狀態
            if baseline_result["passed"] and not current_result["passed"]:
                status = "🔴 回歸"
                regressions.append(tc_id)
            elif not baseline_result["passed"] and current_result["passed"]:
                status = "✅ 改進"
                improvements.append(tc_id)
            elif current_result["score"] > baseline_result["score"] + 0.05:
                status = "⬆️  提升"
                improvements.append(tc_id)
            elif current_result["score"] < baseline_result["score"] - 0.05:
                status = "⬇️  下降"
                regressions.append(tc_id)
            else:
                status = "➡️  持平"
                unchanged.append(tc_id)

            print(f"{tc_id:<12} {baseline_str:<15} {current_str:<15} {status:<15}")

        # 記錄回歸測試結果
        regression_trace = self.langfuse.trace(
            name="regression-test-run",
            metadata={
                "baseline_version": baseline["version"],
                "current_version": current["version"],
                "regressions_found": len(regressions),
                "improvements_found": len(improvements),
                "test_date": datetime.now().isoformat()
            },
            tags=["regression-test", "qa"]
        )

        # 總結
        print(f"\n" + "="*60)
        print(f"回歸測試總結:")
        print(f"   總測試數: {len(baseline['test_results'])}")
        print(f"   回歸問題: {len(regressions)} {'🚨' if regressions else '✅'}")
        print(f"   改進項目: {len(improvements)}")
        print(f"   持平項目: {len(unchanged)}")

        if regressions:
            print(f"\n⚠️  發現回歸問題:")
            for tc_id in regressions:
                print(f"      • {tc_id}")
            print(f"\n   建議: 修復回歸問題後再發布")
        else:
            print(f"\n✅ 沒有發現回歸問題，可以繼續發布流程")

        if improvements:
            print(f"\n🎉 改進項目:")
            for tc_id in improvements:
                print(f"      • {tc_id}")

        print(f"\n✅ 回歸測試完成")


# ============================================================================
# 第五部分：性能基準測試
# ============================================================================

class BenchmarkTesting:
    """
    性能基準測試

    測試和追蹤性能指標。
    """

    def __init__(self, langfuse: Langfuse):
        self.langfuse = langfuse

    def run_performance_benchmark(self):
        """
        運行性能基準測試

        測試系統在不同負載下的性能。
        """
        print("\n" + "="*60)
        print("性能基準測試示例")
        print("="*60)

        print(f"⚡ 運行性能基準測試...\n")

        # 不同並發級別的測試
        concurrency_levels = [1, 5, 10, 20, 50]
        benchmark_results = []

        for concurrency in concurrency_levels:
            print(f"測試並發級別: {concurrency}")

            # 模擬性能測試
            requests = concurrency * 10
            avg_latency = 1.0 + (concurrency * 0.05)  # 延遲隨並發增加
            success_rate = max(0.95 - (concurrency * 0.01), 0.75)  # 成功率隨並發下降
            throughput = requests / (avg_latency * concurrency / 1000)  # 請求/秒

            result = {
                "concurrency": concurrency,
                "total_requests": requests,
                "avg_latency": avg_latency,
                "p95_latency": avg_latency * 1.5,
                "p99_latency": avg_latency * 2.0,
                "success_rate": success_rate,
                "throughput": throughput
            }

            benchmark_results.append(result)

            # 記錄基準測試
            benchmark_trace = self.langfuse.trace(
                name=f"benchmark-concurrency-{concurrency}",
                metadata={
                    "benchmark_type": "concurrency",
                    "concurrency_level": concurrency,
                    "results": result
                },
                tags=["benchmark", "performance"]
            )

            print(f"   平均延遲: {avg_latency:.2f}s")
            print(f"   成功率: {success_rate:.1%}")
            print(f"   吞吐量: {throughput:.2f} req/s\n")

        # 性能報告
        print("="*70)
        print("                    性能基準測試報告")
        print("="*70)

        print(f"\n{'並發':<10} {'請求數':<12} {'平均延遲':<12} {'P95':<10} {'成功率':<12} {'吞吐量':<15}")
        print("-" * 80)

        for result in benchmark_results:
            print(f"{result['concurrency']:<10} "
                  f"{result['total_requests']:<12} "
                  f"{result['avg_latency']:<12.2f} "
                  f"{result['p95_latency']:<10.2f} "
                  f"{result['success_rate']:<12.1%} "
                  f"{result['throughput']:<15.2f}")

        # 性能分析
        print(f"\n📊 性能分析:")
        print(f"   最佳並發級別: {min(benchmark_results, key=lambda x: x['avg_latency'])['concurrency']} (最低延遲)")
        print(f"   最高吞吐量: {max(benchmark_results, key=lambda x: x['throughput'])['throughput']:.2f} req/s")
        print(f"   推薦並發級別: 10-20 (平衡性能和穩定性)")

        print(f"\n✅ 性能基準測試完成")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """
    主函數：運行所有數據集管理示例
    """
    print("\n" + "="*70)
    print("Langfuse 數據集管理示例")
    print("="*70)

    # 初始化 Langfuse
    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY", "pk-demo"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY", "sk-demo"),
        debug=True
    )

    try:
        # 1. 數據集基礎操作
        print("\n第一部分：數據集基礎操作")
        print("="*70)
        dataset_mgmt = DatasetManagement(langfuse)
        test_cases = dataset_mgmt.create_dataset_example()
        dataset_mgmt.organize_test_cases()

        # 2. 批量評估執行
        print("\n第二部分：批量評估執行")
        print("="*70)
        batch_eval = BatchEvaluation(langfuse)
        results = batch_eval.run_batch_evaluation(test_cases)

        # 3. 結果分析和對比
        print("\n第三部分：結果分析和對比")
        print("="*70)
        analysis = ResultAnalysis(langfuse)
        analysis.compare_model_performance()
        analysis.version_comparison_example()

        # 4. 回歸測試
        print("\n第四部分：回歸測試")
        print("="*70)
        regression = RegressionTesting(langfuse)
        regression.run_regression_test()

        # 5. 性能基準測試
        print("\n第五部分：性能基準測試")
        print("="*70)
        benchmark = BenchmarkTesting(langfuse)
        benchmark.run_performance_benchmark()

        print("\n" + "="*70)
        print("✅ 所有數據集管理示例運行完成！")
        print("="*70)

        print("\n💡 數據集管理最佳實踐:")
        print("   1. 建立全面的測試數據集覆蓋各種場景")
        print("   2. 按難度和類型組織測試用例")
        print("   3. 定期運行批量評估追蹤質量")
        print("   4. 對比不同模型和版本的表現")
        print("   5. 實施回歸測試防止質量下降")
        print("   6. 進行性能基準測試確保系統穩定")
        print("   7. 持續更新數據集保持相關性")

        # 刷新數據
        langfuse.flush()

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
