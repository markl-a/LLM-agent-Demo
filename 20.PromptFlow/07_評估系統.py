"""
PromptFlow 評估系統範例
======================

本範例展示如何在 PromptFlow 中評估 Flow 的性能。

評估功能：
1. 內建評估指標
2. 自定義評估器
3. 批量評估
4. 評估報告

安裝依賴：
pip install promptflow promptflow-tools promptflow-evals
"""

import os
import json
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import statistics

# ============================================================
# 評估指標
# ============================================================

@dataclass
class EvaluationMetric:
    """評估指標"""
    name: str
    value: float
    description: str = ""


@dataclass
class EvaluationResult:
    """單條評估結果"""
    id: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    ground_truth: Optional[Dict[str, Any]] = None
    metrics: List[EvaluationMetric] = field(default_factory=list)
    passed: bool = True


@dataclass
class EvaluationReport:
    """評估報告"""
    name: str
    flow_name: str
    timestamp: datetime
    total_samples: int
    results: List[EvaluationResult]
    aggregate_metrics: Dict[str, float] = field(default_factory=dict)


# ============================================================
# 基礎評估器
# ============================================================

class BaseEvaluator:
    """
    基礎評估器

    所有評估器的基類
    """

    def __init__(self, name: str):
        self.name = name

    def evaluate(
        self,
        output: Dict[str, Any],
        ground_truth: Optional[Dict[str, Any]] = None,
        input_data: Optional[Dict[str, Any]] = None
    ) -> EvaluationMetric:
        """
        評估單個輸出

        Args:
            output: 模型輸出
            ground_truth: 真實標籤
            input_data: 輸入數據

        Returns:
            評估指標
        """
        raise NotImplementedError


# ============================================================
# 內建評估器
# ============================================================

class ExactMatchEvaluator(BaseEvaluator):
    """
    精確匹配評估器

    檢查輸出是否與真實標籤完全匹配
    """

    def __init__(self, output_field: str = "answer", truth_field: str = "answer"):
        super().__init__("exact_match")
        self.output_field = output_field
        self.truth_field = truth_field

    def evaluate(
        self,
        output: Dict[str, Any],
        ground_truth: Optional[Dict[str, Any]] = None,
        input_data: Optional[Dict[str, Any]] = None
    ) -> EvaluationMetric:
        if not ground_truth:
            return EvaluationMetric(name=self.name, value=0, description="無真實標籤")

        output_value = str(output.get(self.output_field, "")).strip().lower()
        truth_value = str(ground_truth.get(self.truth_field, "")).strip().lower()

        match = 1.0 if output_value == truth_value else 0.0

        return EvaluationMetric(
            name=self.name,
            value=match,
            description="精確匹配" if match else "不匹配"
        )


class ContainsEvaluator(BaseEvaluator):
    """
    包含評估器

    檢查輸出是否包含關鍵詞
    """

    def __init__(self, output_field: str = "answer", keywords_field: str = "keywords"):
        super().__init__("contains")
        self.output_field = output_field
        self.keywords_field = keywords_field

    def evaluate(
        self,
        output: Dict[str, Any],
        ground_truth: Optional[Dict[str, Any]] = None,
        input_data: Optional[Dict[str, Any]] = None
    ) -> EvaluationMetric:
        if not ground_truth:
            return EvaluationMetric(name=self.name, value=0, description="無真實標籤")

        output_text = str(output.get(self.output_field, "")).lower()
        keywords = ground_truth.get(self.keywords_field, [])

        if not keywords:
            return EvaluationMetric(name=self.name, value=1.0, description="無關鍵詞要求")

        contained = sum(1 for kw in keywords if kw.lower() in output_text)
        score = contained / len(keywords)

        return EvaluationMetric(
            name=self.name,
            value=score,
            description=f"包含 {contained}/{len(keywords)} 個關鍵詞"
        )


class LengthEvaluator(BaseEvaluator):
    """
    長度評估器

    評估輸出長度是否在合理範圍
    """

    def __init__(
        self,
        output_field: str = "answer",
        min_length: int = 10,
        max_length: int = 1000
    ):
        super().__init__("length")
        self.output_field = output_field
        self.min_length = min_length
        self.max_length = max_length

    def evaluate(
        self,
        output: Dict[str, Any],
        ground_truth: Optional[Dict[str, Any]] = None,
        input_data: Optional[Dict[str, Any]] = None
    ) -> EvaluationMetric:
        text = str(output.get(self.output_field, ""))
        length = len(text)

        if length < self.min_length:
            score = 0.0
            desc = f"太短 ({length} < {self.min_length})"
        elif length > self.max_length:
            score = 0.5
            desc = f"太長 ({length} > {self.max_length})"
        else:
            score = 1.0
            desc = f"長度合適 ({length})"

        return EvaluationMetric(name=self.name, value=score, description=desc)


class LatencyEvaluator(BaseEvaluator):
    """
    延遲評估器

    評估響應延遲
    """

    def __init__(self, threshold_ms: float = 1000):
        super().__init__("latency")
        self.threshold_ms = threshold_ms

    def evaluate(
        self,
        output: Dict[str, Any],
        ground_truth: Optional[Dict[str, Any]] = None,
        input_data: Optional[Dict[str, Any]] = None
    ) -> EvaluationMetric:
        latency = output.get("_latency_ms", 0)

        if latency <= self.threshold_ms:
            score = 1.0
            desc = f"延遲正常 ({latency:.0f}ms)"
        else:
            score = max(0, 1 - (latency - self.threshold_ms) / self.threshold_ms)
            desc = f"延遲較高 ({latency:.0f}ms > {self.threshold_ms}ms)"

        return EvaluationMetric(name=self.name, value=score, description=desc)


# ============================================================
# LLM 評估器（使用 AI 評估）
# ============================================================

class RelevanceEvaluator(BaseEvaluator):
    """
    相關性評估器

    使用 LLM 評估回答與問題的相關性
    """

    def __init__(self):
        super().__init__("relevance")

    def evaluate(
        self,
        output: Dict[str, Any],
        ground_truth: Optional[Dict[str, Any]] = None,
        input_data: Optional[Dict[str, Any]] = None
    ) -> EvaluationMetric:
        # 模擬 LLM 評估
        # 實際使用時應調用 LLM API
        question = input_data.get("question", "") if input_data else ""
        answer = output.get("answer", "")

        # 簡單的相關性評估（模擬）
        if not question or not answer:
            score = 0.0
        elif len(answer) > 10:
            score = 0.8
        else:
            score = 0.5

        return EvaluationMetric(
            name=self.name,
            value=score,
            description="模擬相關性評估"
        )


class CoherenceEvaluator(BaseEvaluator):
    """
    連貫性評估器

    評估回答的連貫性和邏輯性
    """

    def __init__(self):
        super().__init__("coherence")

    def evaluate(
        self,
        output: Dict[str, Any],
        ground_truth: Optional[Dict[str, Any]] = None,
        input_data: Optional[Dict[str, Any]] = None
    ) -> EvaluationMetric:
        answer = output.get("answer", "")

        # 簡單的連貫性評估（模擬）
        # 檢查是否有完整的句子結構
        if not answer:
            score = 0.0
        elif "。" in answer or "." in answer:
            score = 0.9
        else:
            score = 0.6

        return EvaluationMetric(
            name=self.name,
            value=score,
            description="模擬連貫性評估"
        )


# ============================================================
# 評估管理器
# ============================================================

class EvaluationManager:
    """
    評估管理器

    管理和執行評估任務
    """

    def __init__(self):
        self.evaluators: List[BaseEvaluator] = []

    def add_evaluator(self, evaluator: BaseEvaluator):
        """添加評估器"""
        self.evaluators.append(evaluator)

    def evaluate_single(
        self,
        output: Dict[str, Any],
        ground_truth: Optional[Dict[str, Any]] = None,
        input_data: Optional[Dict[str, Any]] = None
    ) -> List[EvaluationMetric]:
        """評估單個輸出"""
        metrics = []
        for evaluator in self.evaluators:
            metric = evaluator.evaluate(output, ground_truth, input_data)
            metrics.append(metric)
        return metrics

    def evaluate_batch(
        self,
        outputs: List[Dict[str, Any]],
        ground_truths: Optional[List[Dict[str, Any]]] = None,
        inputs: Optional[List[Dict[str, Any]]] = None
    ) -> EvaluationReport:
        """批量評估"""
        results = []

        for i, output in enumerate(outputs):
            gt = ground_truths[i] if ground_truths and i < len(ground_truths) else None
            inp = inputs[i] if inputs and i < len(inputs) else None

            metrics = self.evaluate_single(output, gt, inp)

            result = EvaluationResult(
                id=str(i),
                input_data=inp or {},
                output_data=output,
                ground_truth=gt,
                metrics=metrics,
                passed=all(m.value >= 0.5 for m in metrics)
            )
            results.append(result)

        # 計算聚合指標
        aggregate = self._compute_aggregate(results)

        return EvaluationReport(
            name="batch_evaluation",
            flow_name="unknown",
            timestamp=datetime.now(),
            total_samples=len(outputs),
            results=results,
            aggregate_metrics=aggregate
        )

    def _compute_aggregate(
        self,
        results: List[EvaluationResult]
    ) -> Dict[str, float]:
        """計算聚合指標"""
        aggregate = {}

        for evaluator in self.evaluators:
            values = [
                m.value for r in results
                for m in r.metrics
                if m.name == evaluator.name
            ]
            if values:
                aggregate[f"{evaluator.name}_mean"] = statistics.mean(values)
                aggregate[f"{evaluator.name}_std"] = statistics.stdev(values) if len(values) > 1 else 0

        # 總體通過率
        aggregate["pass_rate"] = sum(1 for r in results if r.passed) / len(results)

        return aggregate


# ============================================================
# 使用範例
# ============================================================

def example_basic_evaluation():
    """
    範例 1: 基礎評估

    展示簡單的評估流程
    """
    print("=" * 50)
    print("範例 1: 基礎評估")
    print("=" * 50)

    # 創建評估器
    evaluator = ExactMatchEvaluator()

    # 模擬輸出和真實標籤
    output = {"answer": "Python"}
    ground_truth = {"answer": "Python"}

    metric = evaluator.evaluate(output, ground_truth)

    print(f"評估器: {evaluator.name}")
    print(f"得分: {metric.value}")
    print(f"描述: {metric.description}")


def example_multiple_evaluators():
    """
    範例 2: 多評估器

    展示使用多個評估器
    """
    print("\n" + "=" * 50)
    print("範例 2: 多評估器")
    print("=" * 50)

    manager = EvaluationManager()
    manager.add_evaluator(ExactMatchEvaluator())
    manager.add_evaluator(ContainsEvaluator())
    manager.add_evaluator(LengthEvaluator(min_length=5, max_length=200))

    output = {
        "answer": "Python 是一種高級編程語言，由 Guido van Rossum 創建。"
    }
    ground_truth = {
        "answer": "Python 是一種編程語言",
        "keywords": ["Python", "編程", "語言"]
    }

    metrics = manager.evaluate_single(output, ground_truth)

    print("評估結果:")
    for m in metrics:
        print(f"  {m.name}: {m.value:.2f} - {m.description}")


def example_batch_evaluation():
    """
    範例 3: 批量評估

    展示批量評估多個樣本
    """
    print("\n" + "=" * 50)
    print("範例 3: 批量評估")
    print("=" * 50)

    manager = EvaluationManager()
    manager.add_evaluator(ExactMatchEvaluator())
    manager.add_evaluator(RelevanceEvaluator())
    manager.add_evaluator(CoherenceEvaluator())

    # 模擬數據
    outputs = [
        {"answer": "Python 是編程語言。"},
        {"answer": "機器學習是 AI 的一個分支。"},
        {"answer": ""},  # 空回答
    ]

    ground_truths = [
        {"answer": "Python 是一種編程語言"},
        {"answer": "機器學習是人工智能的分支"},
        {"answer": "這是一個測試"},
    ]

    inputs = [
        {"question": "什麼是 Python？"},
        {"question": "什麼是機器學習？"},
        {"question": "測試問題"},
    ]

    report = manager.evaluate_batch(outputs, ground_truths, inputs)

    print(f"總樣本數: {report.total_samples}")
    print(f"\n聚合指標:")
    for name, value in report.aggregate_metrics.items():
        print(f"  {name}: {value:.3f}")


def example_custom_evaluator():
    """
    範例 4: 自定義評估器

    展示如何創建自定義評估器
    """
    print("\n" + "=" * 50)
    print("範例 4: 自定義評估器")
    print("=" * 50)

    class SentimentEvaluator(BaseEvaluator):
        """情感一致性評估器"""

        def __init__(self):
            super().__init__("sentiment_consistency")

        def evaluate(
            self,
            output: Dict[str, Any],
            ground_truth: Optional[Dict[str, Any]] = None,
            input_data: Optional[Dict[str, Any]] = None
        ) -> EvaluationMetric:
            answer = output.get("answer", "")
            expected_sentiment = ground_truth.get("sentiment", "neutral") if ground_truth else "neutral"

            # 簡單的情感檢測
            positive_words = ["好", "棒", "喜歡", "優秀"]
            negative_words = ["差", "糟", "討厭", "失望"]

            pos_count = sum(1 for w in positive_words if w in answer)
            neg_count = sum(1 for w in negative_words if w in answer)

            if pos_count > neg_count:
                detected = "positive"
            elif neg_count > pos_count:
                detected = "negative"
            else:
                detected = "neutral"

            score = 1.0 if detected == expected_sentiment else 0.0

            return EvaluationMetric(
                name=self.name,
                value=score,
                description=f"預期: {expected_sentiment}, 檢測: {detected}"
            )

    evaluator = SentimentEvaluator()

    output = {"answer": "這個產品非常好用，我很喜歡！"}
    ground_truth = {"sentiment": "positive"}

    metric = evaluator.evaluate(output, ground_truth)
    print(f"自定義評估器: {evaluator.name}")
    print(f"得分: {metric.value}")
    print(f"描述: {metric.description}")


def example_evaluation_report():
    """
    範例 5: 評估報告

    展示如何生成評估報告
    """
    print("\n" + "=" * 50)
    print("範例 5: 評估報告")
    print("=" * 50)

    manager = EvaluationManager()
    manager.add_evaluator(ExactMatchEvaluator())
    manager.add_evaluator(LengthEvaluator())
    manager.add_evaluator(RelevanceEvaluator())

    # 模擬評估數據
    outputs = [{"answer": f"回答 {i}"} for i in range(5)]
    ground_truths = [{"answer": f"回答 {i}"} for i in range(5)]
    inputs = [{"question": f"問題 {i}"} for i in range(5)]

    report = manager.evaluate_batch(outputs, ground_truths, inputs)

    # 生成報告
    print("=" * 30)
    print("       評估報告")
    print("=" * 30)
    print(f"評估名稱: {report.name}")
    print(f"評估時間: {report.timestamp}")
    print(f"樣本數量: {report.total_samples}")
    print()
    print("聚合指標:")
    for name, value in report.aggregate_metrics.items():
        print(f"  {name}: {value:.3f}")
    print()
    print(f"通過率: {report.aggregate_metrics['pass_rate']:.1%}")


def example_cli_evaluation():
    """
    範例 6: CLI 評估命令

    展示 PromptFlow 評估的 CLI 命令
    """
    print("\n" + "=" * 50)
    print("範例 6: CLI 評估命令")
    print("=" * 50)

    cli_commands = """
# PromptFlow 評估 CLI 命令

# 創建評估運行
pf run create --flow ./eval_flow \\
    --data ./test_data.jsonl \\
    --run <flow_run_name> \\
    --column-mapping groundtruth='${data.answer}'

# 使用內建評估器
pf eval create --name my_eval \\
    --flow ./my_flow \\
    --data ./test_data.jsonl \\
    --evaluators relevance coherence groundedness

# 查看評估結果
pf eval show --name my_eval

# 比較多次評估
pf eval compare --evals eval1 eval2 eval3

# 導出評估報告
pf eval export --name my_eval --format html --output report.html
"""

    print(cli_commands)


def example_eval_config():
    """
    範例 7: 評估配置

    展示評估的 YAML 配置
    """
    print("\n" + "=" * 50)
    print("範例 7: 評估配置")
    print("=" * 50)

    yaml_config = """
# evaluation.yaml - 評估配置

name: qa_evaluation
description: 問答系統評估

# 評估數據
data:
  path: ./test_data.jsonl
  format: jsonl

# 評估器配置
evaluators:
  - name: relevance
    type: llm
    model: gpt-4
    prompt: |
      評估回答與問題的相關性（1-5分）
      問題：{{question}}
      回答：{{answer}}

  - name: accuracy
    type: exact_match
    field: answer

  - name: groundedness
    type: llm
    model: gpt-4
    prompt: |
      評估回答是否有根據（1-5分）
      上下文：{{context}}
      回答：{{answer}}

# 閾值設置
thresholds:
  relevance: 3.5
  accuracy: 0.8
  groundedness: 3.0

# 輸出配置
output:
  format: json
  path: ./eval_results.json
  include_details: true
"""

    print("評估配置示例:")
    print(yaml_config)


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    print("PromptFlow 評估系統範例")
    print()

    example_basic_evaluation()
    example_multiple_evaluators()
    example_batch_evaluation()
    example_custom_evaluator()
    example_evaluation_report()
    example_cli_evaluation()
    example_eval_config()
