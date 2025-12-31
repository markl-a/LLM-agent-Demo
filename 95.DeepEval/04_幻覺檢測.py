"""
DeepEval 幻覺檢測示例
展示如何檢測和評估 LLM 的幻覺問題
"""

from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import HallucinationMetric, FaithfulnessMetric


def test_no_hallucination():
    """測試無幻覺的答案"""
    print("\n測試無幻覺的答案...")

    test_case = LLMTestCase(
        input="Docker 是什麼？",
        actual_output="Docker 是一個容器化平台，用於打包和運行應用程序。",
        context=[
            "Docker 是開源的容器化平台。",
            "Docker 用於打包應用及其依賴。"
        ]
    )

    metric = HallucinationMetric(threshold=0.3)  # 幻覺分數越低越好

    try:
        metric.measure(test_case)
        print(f"幻覺得分: {metric.score:.4f} (越低越好)")
        print(f"狀態: {'✓ 無幻覺' if metric.score < 0.3 else '✗ 可能有幻覺'}")
    except Exception as e:
        print(f"評估失敗: {str(e)}")


def test_with_hallucination():
    """測試包含幻覺的答案"""
    print("\n測試包含幻覺的答案...")

    test_case = LLMTestCase(
        input="Python 的創建者是誰？",
        actual_output="Python 由 Guido van Rossum 於 1989 年創建，並在 2000 年獲得圖靈獎。",  # 圖靈獎是編造的
        context=[
            "Python 由 Guido van Rossum 創建。",
            "Python 於 1991 年首次發布。"
        ]
    )

    metric = HallucinationMetric(threshold=0.3)

    try:
        metric.measure(test_case)
        print(f"幻覺得分: {metric.score:.4f}")

        if metric.score > 0.3:
            print("✗ 檢測到幻覺：答案包含上下文中沒有的信息")
    except Exception as e:
        print(f"評估失敗: {str(e)}")


def test_hallucination_types():
    """測試不同類型的幻覺"""
    print("\n" + "=" * 60)
    print("常見幻覺類型測試")
    print("=" * 60)

    hallucination_examples = [
        {
            "type": "事實幻覺",
            "input": "GPT-3 有多少參數？",
            "output": "GPT-3 有 2000 億個參數。",  # 實際是 1750 億
            "context": ["GPT-3 擁有 1750 億個參數。"]
        },
        {
            "type": "日期幻覺",
            "input": "BERT 何時發布？",
            "output": "BERT 於 2017 年 10 月發布。",  # 實際是 2018 年
            "context": ["BERT 是 Google 在 2018 年發布的模型。"]
        },
        {
            "type": "過度推斷",
            "input": "Docker 的優勢是什麼？",
            "output": "Docker 是最好的容器化工具，沒有任何缺點，所有公司都應該使用。",
            "context": ["Docker 提供輕量級容器化，啟動快速。"]
        },
        {
            "type": "添加細節",
            "input": "什麼是機器學習？",
            "output": "機器學習由 Arthur Samuel 在 1959 年正式命名，最初用於下棋程序。",
            "context": ["機器學習是 AI 的一個分支，讓計算機從數據中學習。"]
        }
    ]

    metric = HallucinationMetric(threshold=0.3)

    for example in hallucination_examples:
        print(f"\n{example['type']}:")
        print(f"  問題: {example['input']}")
        print(f"  答案: {example['output']}")

        test_case = LLMTestCase(
            input=example['input'],
            actual_output=example['output'],
            context=example['context']
        )

        try:
            metric.measure(test_case)
            print(f"  幻覺得分: {metric.score:.4f}")
        except Exception as e:
            print(f"  評估失敗: {str(e)}")


def test_faithfulness_vs_hallucination():
    """對比忠實度和幻覺檢測"""
    print("\n" + "=" * 60)
    print("忠實度 vs 幻覺檢測")
    print("=" * 60)

    test_case = LLMTestCase(
        input="解釋 Transformer 架構",
        actual_output="Transformer 由 Vaswani 等人在 2017 年提出，使用自注意力機制處理序列數據。它由編碼器和解碼器組成，每個包含多個層。",
        context=[
            "Transformer 在 2017 年的論文中提出。",
            "它使用自注意力機制和位置編碼。"
        ]
    )

    # 忠實度指標
    faithfulness = FaithfulnessMetric(threshold=0.7)
    # 幻覺指標
    hallucination = HallucinationMetric(threshold=0.3)

    print("\n評估結果:")
    try:
        faithfulness.measure(test_case)
        print(f"  忠實度: {faithfulness.score:.4f} (越高越好，閾值 0.7)")

        hallucination.measure(test_case)
        print(f"  幻覺度: {hallucination.score:.4f} (越低越好，閾值 0.3)")

        print("\n解釋:")
        print("  • 忠實度衡量答案是否基於上下文")
        print("  • 幻覺度衡量答案是否包含虛構信息")
        print("  • 兩者互補，建議同時使用")

    except Exception as e:
        print(f"評估失敗: {str(e)}")


def prevention_strategies():
    """幻覺預防策略"""
    print("\n" + "=" * 60)
    print("幻覺預防策略")
    print("=" * 60)

    strategies = [
        {
            "策略": "優化提示詞",
            "方法": [
                "明確要求只基於提供的信息回答",
                "示例：'請僅根據以下內容回答，不要添加其他信息'",
                "要求引用來源",
                "當信息不足時，明確表示'無法確定'"
            ]
        },
        {
            "策略": "調整模型參數",
            "方法": [
                "降低 temperature（如 0.3-0.5）",
                "減少 top_p 值",
                "使用更保守的生成策略",
                "限制輸出長度避免過度發揮"
            ]
        },
        {
            "策略": "改進上下文質量",
            "方法": [
                "提供更完整、準確的上下文",
                "確保上下文來源可靠",
                "包含必要的細節信息",
                "移除可能誤導的內容"
            ]
        },
        {
            "策略": "後處理驗證",
            "方法": [
                "事實檢查機制",
                "交叉驗證關鍵信息",
                "標記不確定的陳述",
                "人工審核關鍵輸出"
            ]
        },
        {
            "策略": "訓練和微調",
            "方法": [
                "使用高質量數據微調",
                "強化基於事實的回答",
                "懲罰虛構信息",
                "持續評估和改進"
            ]
        }
    ]

    for i, strategy in enumerate(strategies, 1):
        print(f"\n{i}. {strategy['策略']}")
        for method in strategy['方法']:
            print(f"   • {method}")


def detection_tools():
    """幻覺檢測工具"""
    print("\n" + "=" * 60)
    print("幻覺檢測工具和方法")
    print("=" * 60)

    tools = [
        {
            "工具": "DeepEval HallucinationMetric",
            "特點": "專門的幻覺檢測指標",
            "用法": "metric = HallucinationMetric(threshold=0.3)"
        },
        {
            "工具": "FaithfulnessMetric",
            "特點": "評估答案對上下文的忠實度",
            "用法": "metric = FaithfulnessMetric(threshold=0.7)"
        },
        {
            "工具": "人工審核",
            "特點": "專家評估關鍵輸出",
            "用法": "定期抽樣審核系統輸出"
        },
        {
            "工具": "事實檢查 API",
            "特點": "自動驗證事實陳述",
            "用法": "集成第三方事實檢查服務"
        }
    ]

    for tool in tools:
        print(f"\n{tool['工具']}:")
        print(f"  特點: {tool['特點']}")
        print(f"  用法: {tool['用法']}")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("DeepEval 幻覺檢測教程")
    print("=" * 60)

    print("\n什麼是 AI 幻覺？")
    print("  AI 幻覺是指語言模型生成的看似合理但實際上")
    print("  不準確或虛構的信息。這是 LLM 的固有問題。")

    print("\n幻覺的危害:")
    print("  • 提供錯誤信息誤導用戶")
    print("  • 損害系統可信度")
    print("  • 可能導致嚴重後果（醫療、法律等領域）")
    print("  • 降低用戶滿意度")

    print("\n本示例包含:")
    print("  1. 無幻覺和有幻覺的對比測試")
    print("  2. 常見幻覺類型")
    print("  3. 忠實度與幻覺的關係")
    print("  4. 預防策略")
    print("  5. 檢測工具")

    input("\n按 Enter 開始測試...")

    # 執行測試
    test_no_hallucination()
    test_with_hallucination()
    test_hallucination_types()
    test_faithfulness_vs_hallucination()

    # 策略和工具
    prevention_strategies()
    detection_tools()

    print("\n" + "=" * 60)
    print("幻覺檢測測試完成！")
    print("=" * 60)

    print("\n關鍵要點:")
    print("  • 幻覺是 LLM 的常見問題，需要重點關注")
    print("  • 使用多種指標和方法檢測幻覺")
    print("  • 通過優化提示詞和參數減少幻覺")
    print("  • 在關鍵應用中必須進行幻覺檢測")


if __name__ == "__main__":
    main()
