"""
DeepEval 快速開始示例
展示 DeepEval 的基本使用方法
"""

from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from typing import List


def create_simple_test_case():
    """
    創建簡單的測試用例

    Returns:
        LLMTestCase: 測試用例
    """
    test_case = LLMTestCase(
        input="什麼是機器學習？",
        actual_output="機器學習是人工智慧的一個分支，它使計算機能夠從數據中學習並改進性能，而無需明確編程。",
        expected_output="機器學習是讓計算機從數據中學習的技術。",
        retrieval_context=[
            "機器學習是 AI 的子領域，專注於從數據中學習的算法。",
            "通過機器學習，計算機可以自動識別模式並做出預測。"
        ]
    )

    return test_case


def basic_evaluation():
    """
    基礎評估示例
    """
    print("=" * 60)
    print("DeepEval 基礎評估")
    print("=" * 60)

    # 1. 創建測試用例
    print("\n1. 創建測試用例...")
    test_case = create_simple_test_case()

    print(f"   輸入: {test_case.input}")
    print(f"   輸出: {test_case.actual_output[:60]}...")
    print(f"   上下文數量: {len(test_case.retrieval_context)}")

    # 2. 創建評估指標
    print("\n2. 創建評估指標...")

    # 答案相關性指標
    relevancy_metric = AnswerRelevancyMetric(
        threshold=0.7,  # 相關性閾值
        model="gpt-3.5-turbo",  # 使用的評估模型
        include_reason=True  # 包含評估理由
    )

    # 忠實度指標
    faithfulness_metric = FaithfulnessMetric(
        threshold=0.7,
        model="gpt-3.5-turbo",
        include_reason=True
    )

    metrics = [relevancy_metric, faithfulness_metric]
    print(f"   已創建 {len(metrics)} 個指標")

    # 3. 執行評估
    print("\n3. 執行評估...")
    print("   (這可能需要幾秒鐘...)")

    try:
        # 測量指標
        for metric in metrics:
            metric.measure(test_case)

        # 4. 顯示結果
        print("\n4. 評估結果:")
        print("-" * 60)

        for metric in metrics:
            print(f"\n{metric.__class__.__name__}:")
            print(f"  得分: {metric.score:.4f}")
            print(f"  閾值: {metric.threshold}")
            print(f"  通過: {'✓' if metric.score >= metric.threshold else '✗'}")

            if hasattr(metric, 'reason') and metric.reason:
                print(f"  理由: {metric.reason}")

        # 5. 使用 assert_test 進行斷言
        print("\n5. 執行測試斷言...")

        try:
            assert_test(test_case, metrics)
            print("   ✓ 所有測試通過！")
        except AssertionError as e:
            print(f"   ✗ 測試失敗: {str(e)}")

    except Exception as e:
        print(f"\n評估失敗: {str(e)}")
        print("\n提示:")
        print("  1. 確保已設置 OPENAI_API_KEY 環境變量")
        print("  2. 確保已安裝 deepeval: pip install deepeval")
        print("  3. 檢查網絡連接")


def batch_evaluation():
    """
    批量評估示例
    """
    print("\n" + "=" * 60)
    print("批量評估示例")
    print("=" * 60)

    # 創建多個測試用例
    test_cases = [
        LLMTestCase(
            input="什麼是 Python？",
            actual_output="Python 是一種高級編程語言，以其簡潔的語法和強大的功能而聞名。",
            retrieval_context=["Python 是解釋型、面向對象的編程語言。"]
        ),
        LLMTestCase(
            input="深度學習和機器學習有什麼區別？",
            actual_output="深度學習是機器學習的一個子集，使用多層神經網絡來學習複雜模式。",
            retrieval_context=["深度學習使用深度神經網絡，是機器學習的專門領域。"]
        ),
        LLMTestCase(
            input="如何學習 AI？",
            actual_output="學習 AI 需要掌握數學基礎、編程技能和機器學習算法。",
            retrieval_context=["AI 學習路徑包括數學、編程和算法。"]
        )
    ]

    print(f"\n創建了 {len(test_cases)} 個測試用例")

    # 創建指標
    metric = AnswerRelevancyMetric(threshold=0.7)

    # 批量評估
    print("\n執行批量評估...")

    try:
        results = []
        for i, test_case in enumerate(test_cases, 1):
            metric.measure(test_case)
            results.append({
                'case_id': i,
                'input': test_case.input,
                'score': metric.score,
                'passed': metric.score >= metric.threshold
            })

        # 顯示結果
        print("\n批量評估結果:")
        print("-" * 60)

        for result in results:
            status = "✓" if result['passed'] else "✗"
            print(f"{status} 案例 {result['case_id']}: {result['input'][:40]}...")
            print(f"   得分: {result['score']:.4f}")

        # 統計
        passed = sum(1 for r in results if r['passed'])
        total = len(results)
        print(f"\n總計: {passed}/{total} 通過 ({passed/total*100:.1f}%)")

    except Exception as e:
        print(f"批量評估失敗: {str(e)}")


def custom_test_case():
    """
    自定義測試用例示例
    """
    print("\n" + "=" * 60)
    print("自定義測試用例")
    print("=" * 60)

    # 可以添加額外的元數據
    test_case = LLMTestCase(
        input="Docker 的主要用途是什麼？",
        actual_output="Docker 主要用於容器化應用，提供一致的運行環境。",
        retrieval_context=["Docker 是容器化平台，用於打包和運行應用。"],
        context=["這是額外的上下文信息"],  # 額外上下文
        expected_output="Docker 用於容器化應用。"  # 期望輸出（可選）
    )

    print(f"\n測試用例屬性:")
    print(f"  輸入: {test_case.input}")
    print(f"  實際輸出: {test_case.actual_output}")
    print(f"  期望輸出: {test_case.expected_output}")
    print(f"  檢索上下文: {len(test_case.retrieval_context)} 條")

    # 評估
    metric = AnswerRelevancyMetric(threshold=0.7)

    try:
        metric.measure(test_case)
        print(f"\n評估得分: {metric.score:.4f}")
    except Exception as e:
        print(f"評估失敗: {str(e)}")


def understanding_metrics():
    """
    理解不同的評估指標
    """
    print("\n" + "=" * 60)
    print("DeepEval 核心指標")
    print("=" * 60)

    metrics_info = [
        {
            "name": "AnswerRelevancyMetric",
            "description": "答案相關性",
            "purpose": "評估答案是否切合問題",
            "threshold": "通常 0.7-0.8"
        },
        {
            "name": "FaithfulnessMetric",
            "description": "忠實度",
            "purpose": "評估答案是否忠實於上下文",
            "threshold": "通常 0.7-0.8"
        },
        {
            "name": "ContextualRelevancyMetric",
            "description": "上下文相關性",
            "purpose": "評估檢索上下文的質量",
            "threshold": "通常 0.6-0.7"
        },
        {
            "name": "HallucinationMetric",
            "description": "幻覺檢測",
            "purpose": "檢測模型是否產生幻覺",
            "threshold": "越低越好，< 0.3"
        }
    ]

    for i, metric in enumerate(metrics_info, 1):
        print(f"\n{i}. {metric['name']}")
        print(f"   描述: {metric['description']}")
        print(f"   用途: {metric['purpose']}")
        print(f"   推薦閾值: {metric['threshold']}")


def best_practices():
    """
    DeepEval 最佳實踐
    """
    print("\n" + "=" * 60)
    print("DeepEval 最佳實踐")
    print("=" * 60)

    practices = [
        {
            "practice": "選擇合適的指標",
            "tips": [
                "根據應用場景選擇指標",
                "通常組合使用多個指標",
                "RAG 應用重點關注相關性和忠實度",
                "安全應用加入毒性和偏見檢測"
            ]
        },
        {
            "practice": "設定合理的閾值",
            "tips": [
                "從較低閾值開始（如 0.7）",
                "根據實際表現調整",
                "不同指標可以有不同閾值",
                "記錄閾值選擇的理由"
            ]
        },
        {
            "practice": "編寫全面的測試用例",
            "tips": [
                "覆蓋正常和邊界情況",
                "包含預期失敗的案例",
                "測試不同長度和複雜度的輸入",
                "定期更新測試集"
            ]
        },
        {
            "practice": "整合到開發流程",
            "tips": [
                "在 CI/CD 中自動運行測試",
                "本地開發時快速驗證",
                "追蹤性能趨勢",
                "設置告警機制"
            ]
        }
    ]

    for i, practice in enumerate(practices, 1):
        print(f"\n{i}. {practice['practice']}")
        for tip in practice['tips']:
            print(f"   • {tip}")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("DeepEval 快速開始教程")
    print("=" * 60)

    print("\n什麼是 DeepEval？")
    print("  DeepEval 是一個用於評估 LLM 應用的開源框架。")
    print("  它提供了豐富的評估指標和與 pytest 的無縫整合。")

    print("\n核心概念:")
    print("  • LLMTestCase: 測試用例，包含輸入、輸出和上下文")
    print("  • Metrics: 評估指標，如相關性、忠實度等")
    print("  • assert_test: 執行測試斷言")

    print("\n本示例包含:")
    print("  1. 基礎評估")
    print("  2. 批量評估")
    print("  3. 自定義測試用例")
    print("  4. 指標介紹")
    print("  5. 最佳實踐")

    input("\n按 Enter 開始演示...")

    # 執行示例
    basic_evaluation()
    batch_evaluation()
    custom_test_case()
    understanding_metrics()
    best_practices()

    print("\n" + "=" * 60)
    print("快速開始演示完成！")
    print("=" * 60)

    print("\n下一步:")
    print("  • 查看 02_單元測試.py 了解 pytest 整合")
    print("  • 探索其他示例了解更多指標")
    print("  • 在自己的項目中應用 DeepEval")

    print("\n重要提示:")
    print("  • 需要設置 OPENAI_API_KEY 環境變量")
    print("  • 評估會產生 API 調用費用")
    print("  • 可以使用本地模型降低成本")


if __name__ == "__main__":
    main()
