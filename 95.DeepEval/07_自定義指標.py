"""
DeepEval 自定義指標示例
展示如何創建自定義評估指標
"""

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase
from deepeval import assert_test
from typing import Optional
import re


class LengthMetric(BaseMetric):
    """
    自定義指標：評估答案長度是否適當
    """

    def __init__(
        self,
        min_length: int = 50,
        max_length: int = 500,
        threshold: float = 0.7
    ):
        self.min_length = min_length
        self.max_length = max_length
        self.threshold = threshold

    def measure(self, test_case: LLMTestCase) -> float:
        """
        測量指標

        Args:
            test_case: 測試用例

        Returns:
            分數 (0-1)
        """
        output = test_case.actual_output
        length = len(output)

        if length < self.min_length:
            # 過短
            self.score = length / self.min_length
            self.reason = f"答案過短（{length} < {self.min_length}）"
        elif length > self.max_length:
            # 過長
            excess = length - self.max_length
            penalty = min(excess / self.max_length, 0.5)
            self.score = 1.0 - penalty
            self.reason = f"答案過長（{length} > {self.max_length}）"
        else:
            # 理想長度
            self.score = 1.0
            self.reason = f"答案長度適當（{length}）"

        self.success = self.score >= self.threshold
        return self.score

    @property
    def __name__(self):
        return "Length Appropriateness"


class KeywordCoverageMetric(BaseMetric):
    """
    自定義指標：檢查關鍵詞覆蓋率
    """

    def __init__(
        self,
        required_keywords: list,
        threshold: float = 0.7
    ):
        self.required_keywords = required_keywords
        self.threshold = threshold

    def measure(self, test_case: LLMTestCase) -> float:
        """測量關鍵詞覆蓋率"""
        output = test_case.actual_output.lower()

        covered = []
        missing = []

        for keyword in self.required_keywords:
            if keyword.lower() in output:
                covered.append(keyword)
            else:
                missing.append(keyword)

        self.score = len(covered) / len(self.required_keywords)
        self.success = self.score >= self.threshold

        if missing:
            self.reason = f"缺少關鍵詞: {', '.join(missing)}"
        else:
            self.reason = "包含所有關鍵詞"

        return self.score

    @property
    def __name__(self):
        return "Keyword Coverage"


class FormatMetric(BaseMetric):
    """
    自定義指標：檢查答案格式
    """

    def __init__(
        self,
        required_format: str = "markdown",  # markdown, code, list, plain
        threshold: float = 0.8
    ):
        self.required_format = required_format
        self.threshold = threshold

    def measure(self, test_case: LLMTestCase) -> float:
        """檢查格式是否符合要求"""
        output = test_case.actual_output

        format_checks = {
            "markdown": self._check_markdown,
            "code": self._check_code,
            "list": self._check_list,
            "plain": self._check_plain
        }

        check_func = format_checks.get(self.required_format, self._check_plain)
        self.score, self.reason = check_func(output)
        self.success = self.score >= self.threshold

        return self.score

    def _check_markdown(self, text: str) -> tuple:
        """檢查是否包含 Markdown 元素"""
        score = 0.0
        reasons = []

        # 檢查標題
        if re.search(r'^#{1,6}\s', text, re.MULTILINE):
            score += 0.3
            reasons.append("包含標題")

        # 檢查列表
        if re.search(r'^[\-\*]\s', text, re.MULTILINE):
            score += 0.3
            reasons.append("包含列表")

        # 檢查代碼塊
        if '```' in text or '`' in text:
            score += 0.2
            reasons.append("包含代碼")

        # 檢查粗體/斜體
        if re.search(r'\*\*.*\*\*|\*.*\*', text):
            score += 0.2
            reasons.append("包含強調")

        reason = "; ".join(reasons) if reasons else "缺少 Markdown 格式"
        return min(score, 1.0), reason

    def _check_code(self, text: str) -> tuple:
        """檢查是否包含代碼"""
        has_code_block = '```' in text
        has_inline_code = '`' in text and '```' not in text

        if has_code_block:
            return 1.0, "包含代碼塊"
        elif has_inline_code:
            return 0.7, "包含內聯代碼"
        else:
            return 0.0, "缺少代碼"

    def _check_list(self, text: str) -> tuple:
        """檢查是否為列表格式"""
        list_pattern = r'^[\d\.\-\*]\s'
        matches = re.findall(list_pattern, text, re.MULTILINE)

        if len(matches) >= 3:
            return 1.0, f"包含 {len(matches)} 個列表項"
        elif len(matches) > 0:
            return 0.5, f"只有 {len(matches)} 個列表項"
        else:
            return 0.0, "不是列表格式"

    def _check_plain(self, text: str) -> tuple:
        """檢查是否為純文本"""
        # 純文本不應包含特殊格式
        has_markdown = bool(re.search(r'[#\*`]', text))

        if not has_markdown:
            return 1.0, "符合純文本格式"
        else:
            return 0.5, "包含格式標記"

    @property
    def __name__(self):
        return "Format Compliance"


class StructureMetric(BaseMetric):
    """
    自定義指標：評估答案結構
    """

    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold

    def measure(self, test_case: LLMTestCase) -> float:
        """評估答案結構"""
        output = test_case.actual_output

        score_components = []

        # 檢查是否有開頭
        if len(output) > 0:
            score_components.append(0.2)

        # 檢查段落
        paragraphs = output.split('\n\n')
        if len(paragraphs) >= 2:
            score_components.append(0.3)

        # 檢查句子數量
        sentences = re.split(r'[。！？.!?]', output)
        if 3 <= len(sentences) <= 10:
            score_components.append(0.3)

        # 檢查邏輯連接詞
        connectors = ['因此', '所以', '但是', '然而', '首先', '其次', '最後']
        has_connectors = any(conn in output for conn in connectors)
        if has_connectors:
            score_components.append(0.2)

        self.score = sum(score_components)
        self.success = self.score >= self.threshold

        self.reason = f"結構得分: {self.score:.2f} (段落: {len(paragraphs)}, 句子: {len(sentences)})"

        return self.score

    @property
    def __name__(self):
        return "Answer Structure"


def test_custom_metrics():
    """測試自定義指標"""
    print("\n" + "=" * 60)
    print("測試自定義指標")
    print("=" * 60)

    # 測試用例
    test_case = LLMTestCase(
        input="解釋什麼是機器學習",
        actual_output="""機器學習是人工智慧的一個重要分支。

它使計算機能夠從數據中學習，而無需明確編程。主要包括監督學習、非監督學習和強化學習三種類型。

因此，機器學習在現代 AI 應用中扮演著關鍵角色。"""
    )

    # 創建自定義指標
    metrics = [
        LengthMetric(min_length=30, max_length=500),
        KeywordCoverageMetric(required_keywords=['機器學習', '數據', '學習']),
        FormatMetric(required_format="plain"),
        StructureMetric()
    ]

    # 測試每個指標
    for metric in metrics:
        print(f"\n{metric.__name__}:")
        metric.measure(test_case)
        print(f"  得分: {metric.score:.3f}")
        print(f"  通過: {metric.success}")
        print(f"  理由: {metric.reason}")


def test_combined_metrics():
    """測試組合使用多個自定義指標"""
    print("\n" + "=" * 60)
    print("組合使用自定義指標")
    print("=" * 60)

    test_case = LLMTestCase(
        input="如何使用 Python 讀取文件？",
        actual_output="""使用 Python 讀取文件很簡單：

```python
with open('file.txt', 'r') as f:
    content = f.read()
```

這個方法會自動關閉文件，是最推薦的做法。"""
    )

    metrics = [
        LengthMetric(min_length=50, max_length=300),
        FormatMetric(required_format="code"),
        KeywordCoverageMetric(required_keywords=['Python', '文件', 'open'])
    ]

    try:
        assert_test(test_case, metrics)
        print("✓ 所有自定義指標測試通過")
    except AssertionError as e:
        print(f"✗ 測試失敗: {str(e)}")


def best_practices():
    """自定義指標最佳實踐"""
    print("\n" + "=" * 60)
    print("自定義指標最佳實踐")
    print("=" * 60)

    practices = [
        {
            "實踐": "明確目標",
            "說明": "清楚定義指標要評估什麼",
            "示例": "評估答案長度、格式、關鍵詞等具體方面"
        },
        {
            "實踐": "合理閾值",
            "說明": "設定符合實際的通過標準",
            "示例": "根據業務需求和測試結果調整閾值"
        },
        {
            "實踐": "提供理由",
            "說明": "說明評分的依據",
            "示例": "在 reason 屬性中詳細說明"
        },
        {
            "實踐": "可組合性",
            "說明": "設計可以與其他指標組合使用的指標",
            "示例": "遵循 BaseMetric 接口"
        }
    ]

    for i, practice in enumerate(practices, 1):
        print(f"\n{i}. {practice['實踐']}")
        print(f"   說明: {practice['說明']}")
        print(f"   示例: {practice['示例']}")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("DeepEval 自定義指標教程")
    print("=" * 60)

    print("\n為什麼需要自定義指標？")
    print("  • 評估特定領域的需求")
    print("  • 實施業務規則")
    print("  • 補充內置指標")
    print("  • 實現精細化控制")

    print("\n自定義指標示例:")
    print("  • LengthMetric - 答案長度")
    print("  • KeywordCoverageMetric - 關鍵詞覆蓋")
    print("  • FormatMetric - 格式檢查")
    print("  • StructureMetric - 結構評估")

    input("\n按 Enter 開始測試...")

    test_custom_metrics()
    test_combined_metrics()
    best_practices()

    print("\n" + "=" * 60)
    print("自定義指標測試完成！")
    print("=" * 60)

    print("\n關鍵要點:")
    print("  • 自定義指標提供靈活的評估能力")
    print("  • 繼承 BaseMetric 類實現自定義邏輯")
    print("  • 可以與內置指標組合使用")
    print("  • 適合特定領域和業務需求")


if __name__ == "__main__":
    main()
