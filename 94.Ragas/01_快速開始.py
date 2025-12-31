"""
Ragas 快速開始示例
展示如何使用 Ragas 進行基礎的 RAG 評估
"""

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)

def create_sample_dataset():
    """
    創建示例評估數據集

    Returns:
        Dataset: 包含問題、答案、上下文和真實答案的數據集
    """
    # 示例數據
    data = {
        'question': [
            '什麼是機器學習？',
            'Python 的主要特點是什麼？',
            '深度學習與機器學習有什麼區別？'
        ],
        'answer': [
            '機器學習是人工智慧的一個分支，它使計算機能夠從數據中學習並改進性能，而無需明確編程。',
            'Python 是一種高級編程語言，具有簡潔易讀的語法、豐富的庫支持和跨平台特性。',
            '深度學習是機器學習的一個子集，它使用多層神經網絡來學習數據的複雜模式。'
        ],
        'contexts': [
            ['機器學習（ML）是人工智慧的一個子領域，專注於開發能夠從數據中學習的算法。',
             '通過機器學習，計算機可以自動識別模式並做出決策。'],
            ['Python 是一種解釋型、面向對象的高級編程語言。',
             '它以簡潔的語法和強大的標準庫而聞名。'],
            ['深度學習使用人工神經網絡，特別是深度神經網絡來處理數據。',
             '它是機器學習的一個專門領域，特別適合處理圖像和語音等複雜數據。']
        ],
        'ground_truth': [
            '機器學習是人工智慧的分支，通過算法讓計算機從數據中學習。',
            'Python 是簡潔易用的高級編程語言，擁有豐富的庫。',
            '深度學習是機器學習的子集，使用深度神經網絡處理複雜數據。'
        ]
    }

    return Dataset.from_dict(data)


def run_basic_evaluation():
    """
    運行基礎 RAG 評估
    """
    print("=" * 60)
    print("Ragas 快速開始示例")
    print("=" * 60)

    # 1. 創建數據集
    print("\n1. 創建評估數據集...")
    dataset = create_sample_dataset()
    print(f"   數據集大小: {len(dataset)} 條")

    # 2. 選擇評估指標
    print("\n2. 選擇評估指標...")
    metrics = [
        faithfulness,        # 忠實度
        answer_relevancy,    # 答案相關性
        context_precision,   # 上下文精度
        context_recall       # 上下文召回
    ]
    print(f"   選擇的指標: {[m.name for m in metrics]}")

    # 3. 執行評估
    print("\n3. 執行評估...")
    print("   (這可能需要幾分鐘，因為需要調用 LLM...)")

    try:
        # 注意：需要設置 OPENAI_API_KEY 環境變量
        result = evaluate(
            dataset,
            metrics=metrics
        )

        # 4. 顯示結果
        print("\n4. 評估結果:")
        print("-" * 60)

        # 整體指標
        print("\n整體指標:")
        for metric_name, score in result.items():
            if not metric_name.startswith('_'):
                print(f"   {metric_name}: {score:.4f}")

        # 詳細結果
        print("\n詳細結果:")
        df = result.to_pandas()
        print(df.to_string())

        # 5. 結果分析
        print("\n5. 結果分析:")
        analyze_results(result)

    except Exception as e:
        print(f"\n評估失敗: {str(e)}")
        print("\n提示:")
        print("   1. 確保已設置 OPENAI_API_KEY 環境變量")
        print("   2. 確保已安裝所有依賴: pip install ragas langchain-openai")
        print("   3. 檢查網絡連接")


def analyze_results(result):
    """
    分析評估結果並提供建議

    Args:
        result: Ragas 評估結果
    """
    # 提取指標分數
    faithfulness_score = result.get('faithfulness', 0)
    relevancy_score = result.get('answer_relevancy', 0)
    precision_score = result.get('context_precision', 0)
    recall_score = result.get('context_recall', 0)

    print("\n指標解讀:")

    # 忠實度分析
    if faithfulness_score < 0.7:
        print(f"   ⚠️  忠實度較低 ({faithfulness_score:.2f}): 答案可能包含幻覺內容")
    else:
        print(f"   ✓  忠實度良好 ({faithfulness_score:.2f}): 答案基於提供的上下文")

    # 相關性分析
    if relevancy_score < 0.7:
        print(f"   ⚠️  相關性較低 ({relevancy_score:.2f}): 答案可能偏離問題")
    else:
        print(f"   ✓  相關性良好 ({relevancy_score:.2f}): 答案切合問題")

    # 精度分析
    if precision_score < 0.7:
        print(f"   ⚠️  上下文精度較低 ({precision_score:.2f}): 檢索到太多無關信息")
    else:
        print(f"   ✓  上下文精度良好 ({precision_score:.2f}): 檢索信息精確")

    # 召回分析
    if recall_score < 0.7:
        print(f"   ⚠️  上下文召回較低 ({recall_score:.2f}): 可能遺漏重要信息")
    else:
        print(f"   ✓  上下文召回良好 ({recall_score:.2f}): 檢索到所有相關信息")

    # 綜合建議
    print("\n改進建議:")
    suggestions = []

    if faithfulness_score < 0.7:
        suggestions.append("   • 優化提示詞，強調基於上下文回答")
    if relevancy_score < 0.7:
        suggestions.append("   • 改進問題理解模塊")
    if precision_score < 0.7:
        suggestions.append("   • 優化檢索算法，提高相關性過濾")
    if recall_score < 0.7:
        suggestions.append("   • 增加檢索數量或調整檢索策略")

    if suggestions:
        for suggestion in suggestions:
            print(suggestion)
    else:
        print("   ✓ 整體表現良好，繼續保持！")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Ragas 快速開始教程")
    print("=" * 60)

    print("\n本示例展示:")
    print("  1. 如何創建評估數據集")
    print("  2. 如何選擇評估指標")
    print("  3. 如何執行評估")
    print("  4. 如何解讀評估結果")
    print("  5. 如何分析和改進 RAG 系統")

    print("\n注意事項:")
    print("  • 需要設置 OPENAI_API_KEY 環境變量")
    print("  • 評估過程會調用 OpenAI API，產生一定費用")
    print("  • 首次運行可能需要下載模型")

    input("\n按 Enter 繼續...")

    # 運行評估
    run_basic_evaluation()

    print("\n" + "=" * 60)
    print("評估完成！")
    print("=" * 60)

    print("\n下一步:")
    print("  • 查看其他示例了解更多評估指標")
    print("  • 使用自己的 RAG 系統進行評估")
    print("  • 根據評估結果優化系統")


if __name__ == "__main__":
    main()
