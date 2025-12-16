"""
DSPy 評估系統範例
================

本範例展示如何評估 DSPy 模組的性能。

評估類型：
1. 內置指標
2. 自定義指標
3. 批量評估
4. A/B 測試

安裝依賴：
pip install dspy-ai pandas matplotlib
"""

import dspy
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass, field
import json

# ============================================================
# 配置
# ============================================================

turbo = dspy.OpenAI(model='gpt-3.5-turbo')
dspy.settings.configure(lm=turbo)


# ============================================================
# 1. 內置評估指標
# ============================================================

def exact_match(example, pred, trace=None):
    """精確匹配"""
    return example.answer.strip().lower() == pred.answer.strip().lower()


def answer_contains(example, pred, trace=None):
    """答案包含關鍵信息"""
    gold_keywords = example.answer.lower().split()[:5]
    pred_lower = pred.answer.lower()
    matches = sum(1 for kw in gold_keywords if kw in pred_lower)
    return matches / len(gold_keywords) if gold_keywords else 0


def answer_similarity(example, pred, trace=None):
    """答案相似度"""
    gold_words = set(example.answer.lower().split())
    pred_words = set(pred.answer.lower().split())

    if not gold_words:
        return 0.0

    intersection = gold_words & pred_words
    union = gold_words | pred_words

    return len(intersection) / len(union) if union else 0


# ============================================================
# 2. 高級評估指標
# ============================================================

class AdvancedMetrics:
    """高級評估指標"""

    @staticmethod
    def bleu_score(example, pred, trace=None):
        """簡化版 BLEU 分數"""
        from collections import Counter

        reference = example.answer.lower().split()
        hypothesis = pred.answer.lower().split()

        if not hypothesis:
            return 0.0

        # 1-gram 精確度
        ref_counts = Counter(reference)
        hyp_counts = Counter(hypothesis)

        matches = sum(min(ref_counts[w], hyp_counts[w]) for w in hyp_counts)
        precision = matches / len(hypothesis)

        # 長度懲罰
        brevity_penalty = min(1.0, len(hypothesis) / len(reference)) if reference else 0

        return brevity_penalty * precision

    @staticmethod
    def rouge_l(example, pred, trace=None):
        """簡化版 ROUGE-L 分數"""
        def lcs_length(s1: List[str], s2: List[str]) -> int:
            """計算最長公共子序列長度"""
            m, n = len(s1), len(s2)
            dp = [[0] * (n + 1) for _ in range(m + 1)]

            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    if s1[i-1] == s2[j-1]:
                        dp[i][j] = dp[i-1][j-1] + 1
                    else:
                        dp[i][j] = max(dp[i-1][j], dp[i][j-1])

            return dp[m][n]

        reference = example.answer.lower().split()
        hypothesis = pred.answer.lower().split()

        if not reference or not hypothesis:
            return 0.0

        lcs = lcs_length(reference, hypothesis)
        precision = lcs / len(hypothesis)
        recall = lcs / len(reference)

        if precision + recall == 0:
            return 0.0

        f1 = 2 * precision * recall / (precision + recall)
        return f1

    @staticmethod
    def semantic_coherence(example, pred, trace=None):
        """語義連貫性評估"""
        answer = pred.answer

        # 檢查基本結構
        has_period = '。' in answer or '.' in answer
        reasonable_length = 10 <= len(answer) <= 2000

        # 檢查重複
        words = answer.split()
        unique_ratio = len(set(words)) / len(words) if words else 0

        score = 0.0
        if has_period:
            score += 0.3
        if reasonable_length:
            score += 0.3
        score += 0.4 * unique_ratio

        return score


# ============================================================
# 3. 評估器類
# ============================================================

@dataclass
class EvaluationResult:
    """評估結果"""
    metric_name: str
    score: float
    num_examples: int
    details: List[Dict[str, Any]] = field(default_factory=list)


class Evaluator:
    """DSPy 模組評估器"""

    def __init__(self, metrics: Dict[str, Callable] = None):
        self.metrics = metrics or {
            "exact_match": exact_match,
            "contains": answer_contains,
            "similarity": answer_similarity
        }
        self.results_history = []

    def evaluate(
        self,
        module: dspy.Module,
        dataset: List[dspy.Example],
        metrics: List[str] = None
    ) -> Dict[str, EvaluationResult]:
        """評估模組"""
        metrics = metrics or list(self.metrics.keys())
        results = {}

        for metric_name in metrics:
            if metric_name not in self.metrics:
                continue

            metric_fn = self.metrics[metric_name]
            scores = []
            details = []

            for example in dataset:
                try:
                    # 運行模組
                    pred = module(**example.inputs())

                    # 計算分數
                    score = metric_fn(example, pred)
                    scores.append(score)

                    details.append({
                        "input": example.inputs(),
                        "expected": example.answer if hasattr(example, 'answer') else None,
                        "predicted": pred.answer if hasattr(pred, 'answer') else str(pred),
                        "score": score
                    })
                except Exception as e:
                    scores.append(0.0)
                    details.append({
                        "input": example.inputs(),
                        "error": str(e),
                        "score": 0.0
                    })

            avg_score = sum(scores) / len(scores) if scores else 0.0
            results[metric_name] = EvaluationResult(
                metric_name=metric_name,
                score=avg_score,
                num_examples=len(dataset),
                details=details
            )

        self.results_history.append(results)
        return results

    def compare_modules(
        self,
        modules: Dict[str, dspy.Module],
        dataset: List[dspy.Example],
        metrics: List[str] = None
    ) -> Dict[str, Dict[str, EvaluationResult]]:
        """比較多個模組"""
        comparison = {}

        for name, module in modules.items():
            comparison[name] = self.evaluate(module, dataset, metrics)

        return comparison

    def generate_report(
        self,
        results: Dict[str, EvaluationResult]
    ) -> str:
        """生成評估報告"""
        report = []
        report.append("=" * 50)
        report.append("評估報告")
        report.append("=" * 50)

        for metric_name, result in results.items():
            report.append(f"\n指標: {metric_name}")
            report.append(f"  平均分數: {result.score:.4f}")
            report.append(f"  樣本數量: {result.num_examples}")

            # 最佳和最差案例
            if result.details:
                sorted_details = sorted(result.details, key=lambda x: x['score'], reverse=True)

                report.append(f"\n  最佳案例 (分數: {sorted_details[0]['score']:.4f}):")
                report.append(f"    輸入: {sorted_details[0].get('input', 'N/A')}")

                report.append(f"\n  最差案例 (分數: {sorted_details[-1]['score']:.4f}):")
                report.append(f"    輸入: {sorted_details[-1].get('input', 'N/A')}")

        return "\n".join(report)


# ============================================================
# 4. 批量評估
# ============================================================

class BatchEvaluator:
    """批量評估器"""

    def __init__(self, num_threads: int = 4):
        self.num_threads = num_threads

    def evaluate_batch(
        self,
        module: dspy.Module,
        dataset: List[dspy.Example],
        metric: Callable,
        batch_size: int = 10
    ) -> List[float]:
        """批量評估"""
        scores = []

        for i in range(0, len(dataset), batch_size):
            batch = dataset[i:i + batch_size]
            batch_scores = []

            for example in batch:
                try:
                    pred = module(**example.inputs())
                    score = metric(example, pred)
                    batch_scores.append(score)
                except Exception:
                    batch_scores.append(0.0)

            scores.extend(batch_scores)
            print(f"已評估 {min(i + batch_size, len(dataset))}/{len(dataset)} 個樣本")

        return scores


# ============================================================
# 5. A/B 測試
# ============================================================

@dataclass
class ABTestResult:
    """A/B 測試結果"""
    module_a_name: str
    module_b_name: str
    module_a_score: float
    module_b_score: float
    winner: str
    improvement: float
    statistical_significance: bool


class ABTester:
    """A/B 測試器"""

    def __init__(self, metric: Callable):
        self.metric = metric

    def run_test(
        self,
        module_a: dspy.Module,
        module_b: dspy.Module,
        dataset: List[dspy.Example],
        module_a_name: str = "Module A",
        module_b_name: str = "Module B"
    ) -> ABTestResult:
        """運行 A/B 測試"""
        scores_a = []
        scores_b = []

        for example in dataset:
            try:
                pred_a = module_a(**example.inputs())
                score_a = self.metric(example, pred_a)
                scores_a.append(score_a)
            except Exception:
                scores_a.append(0.0)

            try:
                pred_b = module_b(**example.inputs())
                score_b = self.metric(example, pred_b)
                scores_b.append(score_b)
            except Exception:
                scores_b.append(0.0)

        avg_a = sum(scores_a) / len(scores_a) if scores_a else 0
        avg_b = sum(scores_b) / len(scores_b) if scores_b else 0

        # 簡單的顯著性檢驗
        diff = abs(avg_a - avg_b)
        significant = diff > 0.05  # 簡化：差異大於 5% 認為顯著

        winner = module_a_name if avg_a > avg_b else module_b_name
        improvement = abs(avg_a - avg_b) / max(avg_a, avg_b) if max(avg_a, avg_b) > 0 else 0

        return ABTestResult(
            module_a_name=module_a_name,
            module_b_name=module_b_name,
            module_a_score=avg_a,
            module_b_score=avg_b,
            winner=winner,
            improvement=improvement,
            statistical_significance=significant
        )


# ============================================================
# 6. 評估數據集管理
# ============================================================

class EvaluationDataset:
    """評估數據集"""

    def __init__(self, examples: List[dspy.Example] = None):
        self.examples = examples or []

    def add_example(self, **kwargs):
        """添加示例"""
        example = dspy.Example(**kwargs)
        self.examples.append(example)

    def load_from_json(self, path: str):
        """從 JSON 加載"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            self.examples.append(dspy.Example(**item))

    def save_to_json(self, path: str):
        """保存到 JSON"""
        data = [dict(ex) for ex in self.examples]
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def split(self, train_ratio: float = 0.8):
        """分割數據集"""
        import random
        shuffled = self.examples.copy()
        random.shuffle(shuffled)

        split_idx = int(len(shuffled) * train_ratio)
        return shuffled[:split_idx], shuffled[split_idx:]

    def __len__(self):
        return len(self.examples)

    def __iter__(self):
        return iter(self.examples)


# ============================================================
# 使用範例
# ============================================================

def example_basic_metrics():
    """範例 1: 基本評估指標"""
    print("=" * 50)
    print("範例 1: 基本評估指標")
    print("=" * 50)

    # 模擬數據
    @dataclass
    class MockExample:
        answer: str

    gold = MockExample(answer="機器學習是讓計算機從數據中自動學習的技術")
    pred = MockExample(answer="機器學習是計算機從數據自動學習的方法")

    print(f"標準答案: {gold.answer}")
    print(f"預測答案: {pred.answer}")
    print(f"\n精確匹配: {exact_match(gold, pred)}")
    print(f"包含匹配: {answer_contains(gold, pred):.4f}")
    print(f"相似度: {answer_similarity(gold, pred):.4f}")


def example_advanced_metrics():
    """範例 2: 高級評估指標"""
    print("\n" + "=" * 50)
    print("範例 2: 高級評估指標")
    print("=" * 50)

    @dataclass
    class MockExample:
        answer: str

    gold = MockExample(answer="深度學習使用多層神經網絡來處理複雜的模式識別任務")
    pred = MockExample(answer="深度學習利用多層神經網絡進行複雜模式的識別")

    print(f"標準答案: {gold.answer}")
    print(f"預測答案: {pred.answer}")
    print(f"\nBLEU 分數: {AdvancedMetrics.bleu_score(gold, pred):.4f}")
    print(f"ROUGE-L: {AdvancedMetrics.rouge_l(gold, pred):.4f}")
    print(f"語義連貫性: {AdvancedMetrics.semantic_coherence(gold, pred):.4f}")


def example_evaluator():
    """範例 3: 評估器使用"""
    print("\n" + "=" * 50)
    print("範例 3: 評估器")
    print("=" * 50)

    evaluator = Evaluator({
        "exact": exact_match,
        "similarity": answer_similarity,
        "bleu": AdvancedMetrics.bleu_score
    })

    print("評估器配置:")
    print(f"  可用指標: {list(evaluator.metrics.keys())}")

    print("""
使用示例:
    # 創建測試數據
    dataset = [
        dspy.Example(question="什麼是 AI?", answer="人工智能").with_inputs("question"),
        dspy.Example(question="什麼是 ML?", answer="機器學習").with_inputs("question"),
    ]

    # 評估模組
    results = evaluator.evaluate(my_module, dataset)

    # 生成報告
    report = evaluator.generate_report(results)
    print(report)
""")


def example_ab_testing():
    """範例 4: A/B 測試"""
    print("\n" + "=" * 50)
    print("範例 4: A/B 測試")
    print("=" * 50)

    print("""
A/B 測試流程:
    1. 準備兩個模組版本
    2. 準備測試數據集
    3. 運行比較測試
    4. 分析結果

代碼示例:
    tester = ABTester(metric=answer_similarity)

    result = tester.run_test(
        module_a=original_module,
        module_b=optimized_module,
        dataset=test_dataset,
        module_a_name="原始版本",
        module_b_name="優化版本"
    )

    print(f"勝者: {result.winner}")
    print(f"提升: {result.improvement:.2%}")
    print(f"統計顯著: {result.statistical_significance}")
""")


def example_dataset_management():
    """範例 5: 數據集管理"""
    print("\n" + "=" * 50)
    print("範例 5: 數據集管理")
    print("=" * 50)

    dataset = EvaluationDataset()

    # 添加示例
    dataset.add_example(
        question="什麼是機器學習？",
        answer="機器學習是人工智能的一個分支"
    )
    dataset.add_example(
        question="什麼是深度學習？",
        answer="深度學習是使用多層神經網絡的機器學習"
    )

    print(f"數據集大小: {len(dataset)}")

    # 分割
    train, test = dataset.split(0.8)
    print(f"訓練集: {len(train)}, 測試集: {len(test)}")


if __name__ == "__main__":
    print("DSPy 評估系統範例\n")
    example_basic_metrics()
    example_advanced_metrics()
    example_evaluator()
    example_ab_testing()
    example_dataset_management()
