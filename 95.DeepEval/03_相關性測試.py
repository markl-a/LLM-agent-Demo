"""
DeepEval 相關性測試示例
深入探討答案相關性和上下文相關性評估
"""

from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric, ContextualRelevancyMetric


def test_high_relevancy():
    """測試高相關性答案"""
    print("\n測試高相關性答案...")

    test_case = LLMTestCase(
        input="如何在 Python 中讀取文件？",
        actual_output="在 Python 中，使用 open() 函數讀取文件：with open('file.txt', 'r') as f: content = f.read()"
    )

    metric = AnswerRelevancyMetric(
        threshold=0.7,
        model="gpt-3.5-turbo",
        include_reason=True
    )

    try:
        metric.measure(test_case)
        print(f"相關性得分: {metric.score:.4f}")
        print(f"評估理由: {metric.reason}")

        assert_test(test_case, [metric])
        print("✓ 測試通過")
    except Exception as e:
        print(f"✗ 測試失敗: {str(e)}")


def test_low_relevancy():
    """測試低相關性答案"""
    print("\n測試低相關性答案...")

    test_case = LLMTestCase(
        input="什麼是機器學習？",
        actual_output="Python 是一種編程語言，廣泛用於數據科學和 Web 開發。"  # 答非所問
    )

    metric = AnswerRelevancyMetric(
        threshold=0.7,
        include_reason=True
    )

    try:
        metric.measure(test_case)
        print(f"相關性得分: {metric.score:.4f}")
        print(f"評估理由: {metric.reason}")

        # 預期失敗
        try:
            assert_test(test_case, [metric])
            print("✗ 意外通過（應該失敗）")
        except AssertionError:
            print("✓ 正確檢測到低相關性")

    except Exception as e:
        print(f"評估失敗: {str(e)}")


def test_contextual_relevancy():
    """測試上下文相關性"""
    print("\n測試上下文相關性...")

    # 高質量上下文
    test_case_good = LLMTestCase(
        input="什麼是 Docker？",
        actual_output="Docker 是容器化平台，用於打包和運行應用。",
        retrieval_context=[
            "Docker 是一個開源的容器化平台。",
            "它使用容器技術來打包應用及其依賴。",
            "Docker 提供一致的運行環境。"
        ]
    )

    # 低質量上下文（包含無關信息）
    test_case_bad = LLMTestCase(
        input="什麼是 Docker？",
        actual_output="Docker 是容器化平台。",
        retrieval_context=[
            "Docker 是容器化平台。",  # 相關
            "Python 是編程語言。",  # 無關
            "Kubernetes 管理容器。",  # 相關但不直接
            "機器學習用於數據分析。"  # 完全無關
        ]
    )

    metric = ContextualRelevancyMetric(
        threshold=0.6,
        include_reason=True
    )

    # 測試高質量上下文
    print("\n高質量上下文:")
    try:
        metric.measure(test_case_good)
        print(f"  上下文相關性: {metric.score:.4f}")
        print(f"  理由: {metric.reason}")
    except Exception as e:
        print(f"  評估失敗: {str(e)}")

    # 測試低質量上下文
    print("\n低質量上下文:")
    try:
        metric.measure(test_case_bad)
        print(f"  上下文相關性: {metric.score:.4f}")
        print(f"  理由: {metric.reason}")
    except Exception as e:
        print(f"  評估失敗: {str(e)}")


def test_answer_length_impact():
    """測試答案長度對相關性的影響"""
    print("\n測試答案長度對相關性的影響...")

    question = "什麼是 Python？"

    test_cases = [
        ("簡短", "Python 是編程語言。"),
        ("適中", "Python 是一種高級編程語言，以簡潔的語法和強大的功能而聞名。"),
        ("詳細", "Python 是一種解釋型、面向對象的高級編程語言。它由 Guido van Rossum 於 1991 年首次發布。Python 以其清晰的語法和代碼可讀性而聞名，廣泛應用於 Web 開發、數據科學、機器學習等領域。")
    ]

    metric = AnswerRelevancyMetric(threshold=0.7)

    for length_type, answer in test_cases:
        test_case = LLMTestCase(
            input=question,
            actual_output=answer
        )

        try:
            metric.measure(test_case)
            print(f"{length_type}答案 ({len(answer)} 字符): {metric.score:.4f}")
        except Exception as e:
            print(f"{length_type}答案評估失敗: {str(e)}")


def test_partial_relevancy():
    """測試部分相關的答案"""
    print("\n測試部分相關的答案...")

    test_case = LLMTestCase(
        input="Python 和 Java 有什麼區別？",
        actual_output="Python 是一種解釋型語言，語法簡潔。它廣泛用於數據科學和機器學習。"  # 只回答了 Python，沒有對比
    )

    metric = AnswerRelevancyMetric(
        threshold=0.7,
        include_reason=True
    )

    try:
        metric.measure(test_case)
        print(f"相關性得分: {metric.score:.4f}")
        print(f"評估理由: {metric.reason}")

        if metric.score < 0.8:
            print("分析: 答案只涵蓋了問題的一部分，未進行完整對比")

    except Exception as e:
        print(f"評估失敗: {str(e)}")


def analyze_relevancy_factors():
    """分析影響相關性的因素"""
    print("\n" + "=" * 60)
    print("影響相關性的因素分析")
    print("=" * 60)

    factors = [
        {
            "因素": "直接性",
            "說明": "答案是否直接回答問題",
            "示例": {
                "好": "Q: 什麼是 AI？ A: AI 是人工智慧...",
                "差": "Q: 什麼是 AI？ A: 技術發展很快..."
            }
        },
        {
            "因素": "完整性",
            "說明": "答案是否涵蓋問題的所有方面",
            "示例": {
                "好": "Q: A 和 B 的區別？ A: A 的特點...，B 的特點...",
                "差": "Q: A 和 B 的區別？ A: A 的特點..."
            }
        },
        {
            "因素": "具體性",
            "說明": "答案是否提供具體信息",
            "示例": {
                "好": "使用 open() 函數讀取文件",
                "差": "可以用 Python 處理文件"
            }
        },
        {
            "因素": "冗餘度",
            "說明": "答案是否包含過多無關信息",
            "示例": {
                "好": "Docker 是容器化平台",
                "差": "首先要了解歷史...Docker 是容器化平台..."
            }
        }
    ]

    for i, factor in enumerate(factors, 1):
        print(f"\n{i}. {factor['因素']}")
        print(f"   說明: {factor['說明']}")
        print(f"   良好示例: {factor['示例']['好']}")
        print(f"   不佳示例: {factor['示例']['差']}")


def optimization_tips():
    """相關性優化建議"""
    print("\n" + "=" * 60)
    print("提高答案相關性的建議")
    print("=" * 60)

    tips = [
        {
            "建議": "優化提示詞",
            "方法": [
                "明確要求直接回答問題",
                "指定答案的結構和長度",
                "提供良好的示例",
                "強調關鍵信息"
            ]
        },
        {
            "建議": "改進問題理解",
            "方法": [
                "提取問題關鍵詞",
                "識別問題類型（定義、對比、方法等）",
                "理解隱含的信息需求",
                "處理多部分問題"
            ]
        },
        {
            "建議": "控制答案生成",
            "方法": [
                "調整 temperature 參數",
                "使用 max_tokens 控制長度",
                "實施答案驗證",
                "過濾無關內容"
            ]
        },
        {
            "建議": "優化上下文",
            "方法": [
                "提高檢索精度",
                "使用重排序",
                "過濾無關上下文",
                "保持上下文相關性"
            ]
        }
    ]

    for i, tip in enumerate(tips, 1):
        print(f"\n{i}. {tip['建議']}")
        for method in tip['方法']:
            print(f"   • {method}")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("DeepEval 相關性測試教程")
    print("=" * 60)

    print("\n相關性的重要性:")
    print("  • 確保答案切合問題")
    print("  • 提高用戶滿意度")
    print("  • 避免資源浪費")
    print("  • 改善系統實用性")

    print("\n兩種相關性:")
    print("  1. 答案相關性 - 答案與問題的相關程度")
    print("  2. 上下文相關性 - 檢索上下文的相關程度")

    input("\n按 Enter 開始測試...")

    # 執行測試
    test_high_relevancy()
    test_low_relevancy()
    test_contextual_relevancy()
    test_answer_length_impact()
    test_partial_relevancy()

    # 分析和建議
    analyze_relevancy_factors()
    optimization_tips()

    print("\n" + "=" * 60)
    print("相關性測試完成！")
    print("=" * 60)

    print("\n關鍵要點:")
    print("  • 相關性是 LLM 應用的基本要求")
    print("  • 需要同時關注答案和上下文相關性")
    print("  • 通過優化提示詞和檢索可以提高相關性")
    print("  • 定期評估確保質量")


if __name__ == "__main__":
    main()
