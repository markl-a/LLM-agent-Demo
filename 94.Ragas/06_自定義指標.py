"""
Ragas 自定義指標示例
展示如何創建自定義評估指標以滿足特定需求
"""

from datasets import Dataset
from ragas.metrics.base import MetricWithLLM, MetricWithEmbeddings
from ragas import evaluate
import numpy as np


class CustomAnswerLengthMetric:
    """
    自定義指標：評估答案長度是否適當
    """

    def __init__(self, min_length=50, max_length=500):
        """
        初始化

        Args:
            min_length: 最小期望長度
            max_length: 最大期望長度
        """
        self.min_length = min_length
        self.max_length = max_length
        self.name = "answer_length_score"

    def score(self, answer: str) -> float:
        """
        計算答案長度分數

        Args:
            answer: 待評估的答案

        Returns:
            分數 (0-1)
        """
        length = len(answer)

        if length < self.min_length:
            # 過短：按比例給分
            return length / self.min_length
        elif length > self.max_length:
            # 過長：超出部分扣分
            excess = length - self.max_length
            penalty = min(excess / self.max_length, 0.5)
            return 1.0 - penalty
        else:
            # 理想長度：滿分
            return 1.0


class CustomKeywordCoverageMetric:
    """
    自定義指標：評估答案是否包含關鍵詞
    """

    def __init__(self, required_keywords):
        """
        初始化

        Args:
            required_keywords: 必需關鍵詞列表
        """
        self.required_keywords = required_keywords
        self.name = "keyword_coverage"

    def score(self, answer: str) -> float:
        """
        計算關鍵詞覆蓋率

        Args:
            answer: 待評估的答案

        Returns:
            覆蓋率 (0-1)
        """
        answer_lower = answer.lower()
        covered = sum(
            1 for keyword in self.required_keywords
            if keyword.lower() in answer_lower
        )
        return covered / len(self.required_keywords) if self.required_keywords else 0


class CustomCitationMetric:
    """
    自定義指標：評估答案是否包含引用
    """

    def __init__(self):
        self.name = "has_citation"

    def score(self, answer: str) -> float:
        """
        檢查答案是否包含引用標記

        Args:
            answer: 待評估的答案

        Returns:
            1.0 如果有引用，0.0 如果沒有
        """
        # 檢測常見的引用格式
        citation_patterns = ['[', '【', '(來源:', '(ref:', 'source:', '參考:']

        for pattern in citation_patterns:
            if pattern in answer:
                return 1.0

        return 0.0


class CustomCompletenessMetric:
    """
    自定義指標：評估答案的完整性
    基於是否回答了問題的所有子問題
    """

    def __init__(self):
        self.name = "answer_completeness"

    def score(self, question: str, answer: str) -> float:
        """
        評估答案完整性

        Args:
            question: 問題
            answer: 答案

        Returns:
            完整性分數 (0-1)
        """
        # 檢測問題中的子問題數量
        sub_questions = self._count_sub_questions(question)

        if sub_questions == 0:
            return 1.0  # 單一問題，只要有答案即可

        # 檢測答案中的要點數量
        answer_points = self._count_answer_points(answer)

        # 計算覆蓋率
        coverage = min(answer_points / sub_questions, 1.0)
        return coverage

    def _count_sub_questions(self, question: str) -> int:
        """計算子問題數量"""
        # 檢測 '和'、'以及'、編號等
        indicators = ['和', '以及', '與', '、']
        count = 1  # 至少有一個問題

        for indicator in indicators:
            count += question.count(indicator)

        # 檢測編號
        for i in range(1, 10):
            if f'{i}.' in question or f'{i})' in question:
                count = max(count, i)

        return min(count, 5)  # 最多認為有5個子問題

    def _count_answer_points(self, answer: str) -> int:
        """計算答案要點數量"""
        # 檢測列表標記
        points = 0
        lines = answer.split('\n')

        for line in lines:
            if any(line.strip().startswith(marker)
                   for marker in ['•', '-', '*', '1.', '2.', '3.', '4.', '5.']):
                points += 1

        # 如果沒有明顯的列表，檢測分號和句號
        if points == 0:
            points = answer.count('。') + answer.count(';')

        return max(points, 1)  # 至少算1個要點


def create_test_dataset():
    """
    創建測試數據集
    """
    data = {
        'question': [
            'Python 有哪些主要特點？',
            'Docker 和虛擬機的區別是什麼？有哪些優缺點？',
            '什麼是機器學習？',
            '解釋深度學習的工作原理。',
            'React 的主要優勢是什麼？'
        ],
        'answer': [
            # 答案 1: 長度適中，包含關鍵詞，有列表
            'Python 的主要特點包括：1) 簡潔易讀的語法；2) 豐富的標準庫；3) 跨平台支持；4) 動態類型系統。',

            # 答案 2: 較長，完整回答了多個子問題
            'Docker 容器和虛擬機的主要區別在於隔離級別。Docker 共享主機內核，啟動快、資源占用少，適合微服務架構。虛擬機則提供完整的 OS 隔離，安全性更高但資源消耗大。優點：Docker 更輕量、部署快；虛擬機隔離性強。缺點：Docker 安全性相對較弱；虛擬機啟動慢、資源占用大。',

            # 答案 3: 過短
            '機器學習是 AI 的一種。',

            # 答案 4: 過長且冗餘
            '深度學習是一個非常複雜的主題，涉及很多方面。首先我們要了解神經網絡的歷史，它起源於 20 世紀 40 年代。然後是反向傳播算法的發明，這是一個重要的突破。現在深度學習在很多領域都有應用，比如計算機視覺、自然語言處理等。深度學習使用多層神經網絡，每一層都會學習不同級別的特徵。訓練過程需要大量數據和計算資源。優化算法如 SGD、Adam 等也很重要。還有各種架構如 CNN、RNN、Transformer 等。總之，深度學習是當今 AI 領域最重要的技術之一，未來還會繼續發展。',

            # 答案 5: 包含引用
            'React 的主要優勢包括虛擬 DOM 提升性能、組件化開發提高復用性、豐富的生態系統。[來源: React 官方文檔]'
        ],
        'contexts': [
            ['Python 是高級編程語言，以簡潔著稱。'],
            ['Docker 使用容器技術，虛擬機使用硬件虛擬化。'],
            ['機器學習讓計算機從數據中學習。'],
            ['深度學習使用深層神經網絡處理數據。'],
            ['React 是流行的前端 JavaScript 庫。']
        ]
    }

    return Dataset.from_dict(data)


def evaluate_with_custom_metrics():
    """
    使用自定義指標進行評估
    """
    print("=" * 60)
    print("Ragas 自定義指標評估")
    print("=" * 60)

    # 1. 創建數據集
    print("\n1. 創建測試數據集...")
    dataset = create_test_dataset()
    print(f"   數據集大小: {len(dataset)} 條")

    # 2. 創建自定義指標
    print("\n2. 創建自定義指標...")

    length_metric = CustomAnswerLengthMetric(min_length=30, max_length=300)
    keyword_metric = CustomKeywordCoverageMetric(['優勢', '特點', '區別', '原理', '主要'])
    citation_metric = CustomCitationMetric()
    completeness_metric = CustomCompletenessMetric()

    print("   已創建指標:")
    print(f"   • {length_metric.name}")
    print(f"   • {keyword_metric.name}")
    print(f"   • {citation_metric.name}")
    print(f"   • {completeness_metric.name}")

    # 3. 手動評估（因為自定義指標不一定與 Ragas 兼容）
    print("\n3. 執行自定義評估...")

    results = []
    for idx, item in enumerate(dataset):
        question = item['question']
        answer = item['answer']

        # 計算各項指標
        length_score = length_metric.score(answer)
        keyword_score = keyword_metric.score(answer)
        citation_score = citation_metric.score(answer)
        completeness_score = completeness_metric.score(question, answer)

        results.append({
            'question': question,
            'answer': answer,
            'length_score': length_score,
            'keyword_coverage': keyword_score,
            'has_citation': citation_score,
            'completeness': completeness_score,
            'overall': np.mean([length_score, keyword_score, citation_score, completeness_score])
        })

    # 4. 顯示結果
    print("\n4. 評估結果:")
    print("-" * 80)

    for idx, result in enumerate(results, 1):
        print(f"\n問題 {idx}: {result['question']}")
        print(f"答案長度: {len(result['answer'])} 字符")
        print(f"指標得分:")
        print(f"  • 長度適當性: {result['length_score']:.3f}")
        print(f"  • 關鍵詞覆蓋: {result['keyword_coverage']:.3f}")
        print(f"  • 包含引用: {result['has_citation']:.3f}")
        print(f"  • 答案完整性: {result['completeness']:.3f}")
        print(f"  • 綜合得分: {result['overall']:.3f}")

    # 5. 統計分析
    print("\n5. 統計分析:")
    analyze_custom_metrics(results)


def analyze_custom_metrics(results):
    """
    分析自定義指標結果

    Args:
        results: 評估結果列表
    """
    # 計算平均分
    avg_length = np.mean([r['length_score'] for r in results])
    avg_keyword = np.mean([r['keyword_coverage'] for r in results])
    avg_citation = np.mean([r['has_citation'] for r in results])
    avg_completeness = np.mean([r['completeness'] for r in results])
    avg_overall = np.mean([r['overall'] for r in results])

    print(f"\n平均指標得分:")
    print(f"  • 長度適當性: {avg_length:.3f}")
    print(f"  • 關鍵詞覆蓋: {avg_keyword:.3f}")
    print(f"  • 引用率: {avg_citation:.3f}")
    print(f"  • 完整性: {avg_completeness:.3f}")
    print(f"  • 綜合得分: {avg_overall:.3f}")

    # 識別問題
    print(f"\n問題識別:")
    issues = []

    for idx, result in enumerate(results, 1):
        if result['length_score'] < 0.7:
            issues.append(f"  • 問題 {idx}: 答案長度不適當")
        if result['keyword_coverage'] < 0.3:
            issues.append(f"  • 問題 {idx}: 關鍵詞覆蓋不足")
        if result['completeness'] < 0.7:
            issues.append(f"  • 問題 {idx}: 答案不夠完整")

    if issues:
        for issue in issues:
            print(issue)
    else:
        print("  ✓ 未發現明顯問題")


def custom_metric_examples():
    """
    展示更多自定義指標的例子
    """
    print("\n" + "=" * 60)
    print("更多自定義指標示例")
    print("=" * 60)

    examples = [
        {
            "指標名稱": "Tone Appropriateness（語氣適當性）",
            "用途": "評估答案語氣是否符合場景",
            "實現思路": [
                "檢測正式/非正式用語",
                "分析情感傾向",
                "評估禮貌程度"
            ]
        },
        {
            "指標名稱": "Technical Accuracy（技術準確性）",
            "用途": "評估技術細節的準確性",
            "實現思路": [
                "檢查代碼語法",
                "驗證術語使用",
                "對比技術文檔"
            ]
        },
        {
            "指標名稱": "Readability（可讀性）",
            "用途": "評估答案易讀程度",
            "實現思路": [
                "計算句子長度",
                "分析詞彙難度",
                "評估結構清晰度"
            ]
        },
        {
            "指標名稱": "Actionability（可操作性）",
            "用途": "評估答案是否提供可執行的建議",
            "實現思路": [
                "檢測行動動詞",
                "識別具體步驟",
                "評估指導性"
            ]
        },
        {
            "指標名稱": "Source Diversity（來源多樣性）",
            "用途": "評估引用來源的多樣性",
            "實現思路": [
                "統計引用數量",
                "分析來源類型",
                "評估觀點平衡性"
            ]
        }
    ]

    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['指標名稱']}")
        print(f"   用途: {example['用途']}")
        print(f"   實現思路:")
        for thought in example['實現思路']:
            print(f"   • {thought}")


def integration_guide():
    """
    自定義指標整合指南
    """
    print("\n" + "=" * 60)
    print("整合自定義指標到 Ragas")
    print("=" * 60)

    print("""
要將自定義指標整合到 Ragas 評估流程，需要繼承 Ragas 的基類：

```python
from ragas.metrics.base import Metric

class MyCustomMetric(Metric):
    def __init__(self):
        self.name = "my_custom_metric"

    def score(self, row):
        # 從 row 中提取需要的字段
        question = row['question']
        answer = row['answer']
        context = row['contexts']

        # 實現評分邏輯
        score = self._calculate_score(question, answer, context)

        return score

    def _calculate_score(self, question, answer, context):
        # 具體的評分邏輯
        pass
```

使用自定義指標：

```python
from ragas import evaluate

# 創建自定義指標實例
custom_metric = MyCustomMetric()

# 與內置指標一起使用
result = evaluate(
    dataset,
    metrics=[faithfulness, custom_metric]
)
```

進階：使用 LLM 的自定義指標：

```python
from ragas.metrics.base import MetricWithLLM

class LLMBasedCustomMetric(MetricWithLLM):
    def __init__(self):
        super().__init__()
        self.name = "llm_custom_metric"

    async def _ascore(self, row):
        # 使用 self.llm 調用語言模型
        prompt = self._create_prompt(row)
        response = await self.llm.generate(prompt)
        score = self._parse_response(response)
        return score
```
    """)


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Ragas 自定義指標教程")
    print("=" * 60)

    print("\n為什麼需要自定義指標？")
    print("  • 內置指標無法滿足特定需求")
    print("  • 不同領域有不同的評估標準")
    print("  • 需要評估特定的業務指標")
    print("  • 實現更細粒度的質量控制")

    print("\n自定義指標的類型:")
    print("  1. 規則基礎指標 - 基於明確規則")
    print("  2. 統計指標 - 基於統計特徵")
    print("  3. LLM 輔助指標 - 使用 LLM 評估")
    print("  4. 混合指標 - 結合多種方法")

    print("\n本示例包含:")
    print("  1. 4 個實用的自定義指標實現")
    print("  2. 完整的評估流程")
    print("  3. 更多指標創意")
    print("  4. 整合指南")

    input("\n按 Enter 開始評估...")

    # 執行評估
    evaluate_with_custom_metrics()

    # 更多示例
    custom_metric_examples()

    # 整合指南
    integration_guide()

    print("\n" + "=" * 60)
    print("評估完成！")
    print("=" * 60)

    print("\n關鍵要點:")
    print("  • 自定義指標讓評估更靈活")
    print("  • 根據業務需求設計指標")
    print("  • 可以與內置指標結合使用")
    print("  • 持續迭代優化指標設計")


if __name__ == "__main__":
    main()
