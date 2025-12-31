"""
DeepEval 單元測試示例
展示如何使用 pytest 進行 LLM 單元測試
"""

import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualRelevancyMetric
)


# ============================================================================
# 基礎單元測試
# ============================================================================

def test_simple_answer_relevancy():
    """
    測試簡單的答案相關性

    這是最基本的測試形式
    """
    # Arrange - 準備測試數據
    test_case = LLMTestCase(
        input="什麼是 Python？",
        actual_output="Python 是一種高級編程語言，以簡潔的語法和強大的功能而聞名。"
    )

    # Act - 執行評估
    metric = AnswerRelevancyMetric(threshold=0.7)

    # Assert - 斷言測試通過
    assert_test(test_case, [metric])


def test_faithfulness_with_context():
    """
    測試帶上下文的忠實度

    忠實度指標需要提供 retrieval_context
    """
    test_case = LLMTestCase(
        input="Docker 的主要用途是什麼？",
        actual_output="Docker 主要用於容器化應用程序，提供一致的運行環境，簡化部署和擴展。",
        retrieval_context=[
            "Docker 是一個容器化平台，用於打包和運行應用。",
            "它提供一致的環境，避免'在我機器上可以運行'的問題。"
        ]
    )

    metric = FaithfulnessMetric(threshold=0.7)
    assert_test(test_case, [metric])


# ============================================================================
# 參數化測試
# ============================================================================

@pytest.mark.parametrize(
    "input_text,output_text",
    [
        ("什麼是機器學習？", "機器學習是 AI 的一個分支，讓計算機從數據中學習。"),
        ("解釋深度學習", "深度學習使用多層神經網絡學習複雜模式。"),
        ("什麼是 NLP？", "NLP 是自然語言處理，讓計算機理解人類語言。"),
    ]
)
def test_multiple_qa_pairs(input_text, output_text):
    """
    參數化測試 - 測試多組問答對

    使用 pytest.mark.parametrize 可以用相同的測試邏輯測試多組數據
    """
    test_case = LLMTestCase(
        input=input_text,
        actual_output=output_text
    )

    metric = AnswerRelevancyMetric(threshold=0.7)
    assert_test(test_case, [metric])


@pytest.mark.parametrize(
    "question,answer,context,expected_pass",
    [
        # 應該通過的案例
        (
            "什麼是 Git？",
            "Git 是分布式版本控制系統。",
            ["Git 用於追蹤代碼變更。"],
            True
        ),
        # 應該失敗的案例（答案不忠實）
        (
            "Python 有幾個版本？",
            "Python 有 5 個主要版本。",  # 這是錯誤的
            ["Python 有 Python 2 和 Python 3 兩個主要版本。"],
            False
        ),
    ]
)
def test_expected_outcomes(question, answer, context, expected_pass):
    """
    測試預期結果 - 包括通過和失敗的案例

    這樣可以測試負面情況，確保系統能正確識別問題
    """
    test_case = LLMTestCase(
        input=question,
        actual_output=answer,
        retrieval_context=context
    )

    metric = FaithfulnessMetric(threshold=0.7)

    if expected_pass:
        # 預期通過
        assert_test(test_case, [metric])
    else:
        # 預期失敗
        with pytest.raises(AssertionError):
            assert_test(test_case, [metric])


# ============================================================================
# 多指標測試
# ============================================================================

def test_multiple_metrics():
    """
    同時測試多個指標

    實際應用中通常需要評估多個維度
    """
    test_case = LLMTestCase(
        input="解釋 REST API 的工作原理",
        actual_output="REST API 是基於 HTTP 協議的 Web 服務架構，使用 GET、POST 等標準方法進行資源操作。",
        retrieval_context=[
            "REST 使用 HTTP 協議。",
            "REST API 通過 URL 標識資源，使用 HTTP 方法操作資源。"
        ]
    )

    # 創建多個指標
    metrics = [
        AnswerRelevancyMetric(threshold=0.7),
        FaithfulnessMetric(threshold=0.7),
    ]

    # 同時測試所有指標
    assert_test(test_case, metrics)


# ============================================================================
# Fixture 使用
# ============================================================================

@pytest.fixture
def rag_system_mock():
    """
    模擬 RAG 系統的 fixture

    在實際應用中，這裡會是真實的 RAG 系統
    """
    class MockRAGSystem:
        def query(self, question):
            # 模擬查詢邏輯
            responses = {
                "什麼是 Docker？": {
                    "answer": "Docker 是容器化平台。",
                    "context": ["Docker 用於容器化應用。"]
                },
                "什麼是 Kubernetes？": {
                    "answer": "Kubernetes 是容器編排平台。",
                    "context": ["Kubernetes 管理容器集群。"]
                }
            }
            return responses.get(question, {
                "answer": "我不知道。",
                "context": []
            })

    return MockRAGSystem()


def test_with_fixture(rag_system_mock):
    """
    使用 fixture 測試 RAG 系統

    這展示了如何測試實際的系統輸出
    """
    # 使用 RAG 系統
    question = "什麼是 Docker？"
    result = rag_system_mock.query(question)

    # 創建測試用例
    test_case = LLMTestCase(
        input=question,
        actual_output=result["answer"],
        retrieval_context=result["context"]
    )

    # 評估
    metric = AnswerRelevancyMetric(threshold=0.7)
    assert_test(test_case, [metric])


# ============================================================================
# 測試類組織
# ============================================================================

class TestRAGSystem:
    """
    使用測試類組織相關測試

    這有助於組織大量測試
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """每個測試前的設置"""
        self.default_threshold = 0.7
        print("\n設置測試...")

    def test_answer_quality(self):
        """測試答案質量"""
        test_case = LLMTestCase(
            input="什麼是 AI？",
            actual_output="AI 是人工智慧，模擬人類智能的計算機系統。"
        )

        metric = AnswerRelevancyMetric(threshold=self.default_threshold)
        assert_test(test_case, [metric])

    def test_context_relevancy(self):
        """測試上下文相關性"""
        test_case = LLMTestCase(
            input="什麼是機器學習？",
            actual_output="機器學習讓計算機從數據中學習。",
            retrieval_context=[
                "機器學習是 AI 的子領域。",
                "它使用算法從數據中學習模式。"
            ]
        )

        metric = ContextualRelevancyMetric(threshold=self.default_threshold)
        assert_test(test_case, [metric])


# ============================================================================
# 標記和跳過
# ============================================================================

@pytest.mark.slow
def test_comprehensive_evaluation():
    """
    全面評估（標記為慢速測試）

    使用 pytest -m "not slow" 可以跳過慢速測試
    """
    test_case = LLMTestCase(
        input="詳細解釋深度學習的工作原理",
        actual_output="深度學習使用多層人工神經網絡...",  # 長文本輸出
        retrieval_context=["深度學習的相關知識..."]
    )

    # 多個指標的全面評估
    metrics = [
        AnswerRelevancyMetric(threshold=0.7),
        FaithfulnessMetric(threshold=0.7),
        ContextualRelevancyMetric(threshold=0.6),
    ]

    assert_test(test_case, metrics)


@pytest.mark.skip(reason="需要特殊配置")
def test_with_special_model():
    """
    需要特殊配置的測試

    暫時跳過此測試
    """
    pass


@pytest.mark.skipif(
    not pytest.config.getoption("--run-expensive"),
    reason="需要 --run-expensive 選項"
)
def test_expensive_evaluation():
    """
    昂貴的評估（需要特殊標誌）

    運行: pytest --run-expensive
    """
    pass


# ============================================================================
# 輔助函數示例
# ============================================================================

def create_test_case(question, answer, context=None):
    """
    創建測試用例的輔助函數

    減少重複代碼
    """
    return LLMTestCase(
        input=question,
        actual_output=answer,
        retrieval_context=context or []
    )


def evaluate_with_defaults(test_case):
    """
    使用默認配置評估的輔助函數
    """
    metrics = [
        AnswerRelevancyMetric(threshold=0.7),
        FaithfulnessMetric(threshold=0.7)
    ]
    assert_test(test_case, metrics)


def test_using_helpers():
    """
    使用輔助函數的測試

    提高代碼復用性
    """
    test_case = create_test_case(
        question="什麼是 Docker？",
        answer="Docker 是容器化平台。",
        context=["Docker 用於應用容器化。"]
    )

    evaluate_with_defaults(test_case)


# ============================================================================
# 主函數 - 運行說明
# ============================================================================

def main():
    """
    運行測試的說明

    注意：這個文件應該使用 pytest 運行，而不是直接執行
    """
    print("=" * 60)
    print("DeepEval 單元測試示例")
    print("=" * 60)

    print("\n如何運行這些測試:")
    print("\n1. 運行所有測試:")
    print("   pytest 02_單元測試.py")

    print("\n2. 運行特定測試:")
    print("   pytest 02_單元測試.py::test_simple_answer_relevancy")

    print("\n3. 運行測試類:")
    print("   pytest 02_單元測試.py::TestRAGSystem")

    print("\n4. 詳細輸出:")
    print("   pytest 02_單元測試.py -v")

    print("\n5. 跳過慢速測試:")
    print("   pytest 02_單元測試.py -m 'not slow'")

    print("\n6. 顯示打印輸出:")
    print("   pytest 02_單元測試.py -s")

    print("\n7. 並行運行（需要 pytest-xdist）:")
    print("   pytest 02_單元測試.py -n auto")

    print("\n測試組織結構:")
    print("  • 基礎單元測試 - 簡單的測試用例")
    print("  • 參數化測試 - 測試多組數據")
    print("  • 多指標測試 - 綜合評估")
    print("  • Fixture 使用 - 測試真實系統")
    print("  • 測試類 - 組織相關測試")
    print("  • 標記和跳過 - 靈活控制測試")

    print("\n最佳實踐:")
    print("  • 使用描述性的測試名稱")
    print("  • 每個測試只測試一個概念")
    print("  • 使用 fixture 共享設置")
    print("  • 參數化測試減少重複")
    print("  • 合理使用標記組織測試")

    print("\n注意:")
    print("  • 確保已設置 OPENAI_API_KEY")
    print("  • 測試會產生 API 調用費用")
    print("  • 可以使用 mock 減少實際調用")


if __name__ == "__main__":
    main()


# ============================================================================
# pytest.ini 配置示例
# ============================================================================

"""
創建 pytest.ini 文件進行配置:

[pytest]
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests

testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

addopts =
    -v
    --strict-markers
    --tb=short
"""
