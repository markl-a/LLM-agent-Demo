"""
Ragas 忠實度評估示例
展示如何評估 RAG 系統答案的忠實度，檢測幻覺問題
"""

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness
import pandas as pd


def create_faithfulness_test_dataset():
    """
    創建用於忠實度測試的數據集
    包含高忠實度和低忠實度的示例

    Returns:
        Dataset: 測試數據集
    """
    data = {
        'question': [
            # 示例 1: 高忠實度
            'GPT-3 有多少個參數？',

            # 示例 2: 低忠實度（答案包含上下文中沒有的信息）
            'BERT 模型是什麼時候發布的？',

            # 示例 3: 高忠實度
            'Transformer 架構的主要組件是什麼？',

            # 示例 4: 幻覺示例（答案完全編造）
            'ResNet 模型的創新點是什麼？',

            # 示例 5: 部分忠實（混合了正確和錯誤信息）
            '什麼是遷移學習？'
        ],
        'answer': [
            # 答案 1: 忠實於上下文
            'GPT-3 有 1750 億個參數，是當時最大的語言模型之一。',

            # 答案 2: 包含額外信息（上下文中沒有具體日期）
            'BERT 是 Google 在 2018 年 10 月發布的預訓練語言模型，revolutionized NLP 領域。',

            # 答案 3: 忠實於上下文
            'Transformer 的主要組件包括自注意力機制和位置編碼，這些組件使其能夠並行處理序列數據。',

            # 答案 4: 完全編造（上下文中沒有提到跳躍連接）
            'ResNet 的創新在於引入了跳躍連接，允許梯度直接流過網絡，解決了深層網絡的梯度消失問題，並且使用了批量歸一化技術。',

            # 答案 5: 部分正確
            '遷移學習是將在一個任務上訓練的模型應用到另一個相關任務的技術，可以顯著減少訓練時間和數據需求，是深度學習中最重要的技術之一。'
        ],
        'contexts': [
            # 上下文 1
            ['GPT-3（Generative Pre-trained Transformer 3）是 OpenAI 開發的大型語言模型。',
             '它擁有 1750 億個參數，在各種 NLP 任務上表現出色。'],

            # 上下文 2（沒有具體日期）
            ['BERT（Bidirectional Encoder Representations from Transformers）是 Google 開發的預訓練模型。',
             'BERT 使用雙向 Transformer 編碼器來理解文本上下文。'],

            # 上下文 3
            ['Transformer 架構由 Vaswani 等人在 2017 年提出。',
             '其核心是自注意力機制和位置編碼，使模型能夠並行處理輸入序列。'],

            # 上下文 4（沒有提到批量歸一化）
            ['ResNet（Residual Network）是一種深度卷積神經網絡架構。',
             '它通過跳躍連接解決了深層網絡的退化問題。'],

            # 上下文 5（沒有提到是最重要的技術）
            ['遷移學習允許模型將從一個任務學到的知識應用到新任務。',
             '這種方法在數據稀缺的情況下特別有用。']
        ],
        'ground_truth': [
            'GPT-3 有 1750 億個參數。',
            'BERT 是 Google 開發的預訓練模型。',
            'Transformer 使用自注意力機制和位置編碼。',
            'ResNet 使用跳躍連接解決深層網絡問題。',
            '遷移學習將已學知識應用到新任務。'
        ]
    }

    return Dataset.from_dict(data)


def evaluate_faithfulness():
    """
    執行忠實度評估
    """
    print("=" * 60)
    print("Ragas 忠實度評估")
    print("=" * 60)

    # 1. 創建測試數據集
    print("\n1. 創建測試數據集...")
    dataset = create_faithfulness_test_dataset()
    print(f"   數據集大小: {len(dataset)} 條")

    # 2. 執行忠實度評估
    print("\n2. 執行忠實度評估...")
    print("   評估中...")

    try:
        result = evaluate(
            dataset,
            metrics=[faithfulness]
        )

        # 3. 顯示結果
        print("\n3. 評估結果:")
        print("-" * 60)

        # 整體得分
        overall_score = result['faithfulness']
        print(f"\n整體忠實度得分: {overall_score:.4f}")

        # 詳細結果
        df = result.to_pandas()
        print("\n詳細結果:")
        print(df[['question', 'answer', 'faithfulness']].to_string())

        # 4. 分析結果
        print("\n4. 忠實度分析:")
        analyze_faithfulness_results(df)

        # 5. 識別幻覺
        print("\n5. 幻覺檢測:")
        detect_hallucinations(df)

    except Exception as e:
        print(f"\n評估失敗: {str(e)}")
        print("提示: 確保已設置 OPENAI_API_KEY 環境變量")


def analyze_faithfulness_results(df):
    """
    分析忠實度評估結果

    Args:
        df: 包含評估結果的 DataFrame
    """
    # 統計不同忠實度級別的數量
    high_faith = len(df[df['faithfulness'] >= 0.8])
    medium_faith = len(df[(df['faithfulness'] >= 0.6) & (df['faithfulness'] < 0.8)])
    low_faith = len(df[df['faithfulness'] < 0.6])

    print(f"\n忠實度分佈:")
    print(f"   高忠實度 (≥0.8): {high_faith} 條")
    print(f"   中等忠實度 (0.6-0.8): {medium_faith} 條")
    print(f"   低忠實度 (<0.6): {low_faith} 條")

    # 計算平均忠實度
    avg_faith = df['faithfulness'].mean()
    print(f"\n平均忠實度: {avg_faith:.4f}")

    # 評估系統健康度
    print("\n系統健康度評估:")
    if avg_faith >= 0.8:
        print("   ✓ 優秀: 系統基本無幻覺問題")
    elif avg_faith >= 0.6:
        print("   ⚠️  良好: 存在輕微幻覺，建議優化")
    else:
        print("   ✗ 需要改進: 幻覺問題較嚴重")


def detect_hallucinations(df, threshold=0.6):
    """
    檢測幻覺問題

    Args:
        df: 評估結果 DataFrame
        threshold: 忠實度閾值
    """
    # 找出低忠實度的示例
    hallucination_cases = df[df['faithfulness'] < threshold]

    if len(hallucination_cases) == 0:
        print("   ✓ 未檢測到明顯的幻覺問題")
        return

    print(f"   檢測到 {len(hallucination_cases)} 個潛在幻覺案例:")
    print()

    for idx, row in hallucination_cases.iterrows():
        print(f"   案例 {idx + 1}:")
        print(f"   問題: {row['question']}")
        print(f"   答案: {row['answer'][:100]}...")
        print(f"   忠實度: {row['faithfulness']:.4f}")
        print(f"   分析: 答案可能包含上下文中沒有的信息")
        print()


def improve_faithfulness():
    """
    提供改進忠實度的建議
    """
    print("\n" + "=" * 60)
    print("改進忠實度的建議")
    print("=" * 60)

    suggestions = [
        {
            "問題": "答案包含上下文中沒有的信息",
            "解決方案": [
                "優化提示詞，明確要求只基於提供的上下文回答",
                "示例: '請僅根據以下上下文回答問題，不要添加額外信息'",
                "使用更嚴格的生成參數（降低 temperature）"
            ]
        },
        {
            "問題": "答案過度推斷或猜測",
            "解決方案": [
                "訓練模型識別知識邊界",
                "當上下文不足時，明確表示'根據提供的信息無法確定'",
                "添加置信度評估"
            ]
        },
        {
            "問題": "上下文質量不佳",
            "解決方案": [
                "改進檢索算法，提高上下文相關性",
                "增加上下文數量和多樣性",
                "使用重排序模型優化上下文順序"
            ]
        },
        {
            "問題": "模型傾向於過度概括",
            "解決方案": [
                "使用少樣本學習提供具體示例",
                "調整模型參數減少創造性",
                "實施答案驗證機制"
            ]
        }
    ]

    for i, suggestion in enumerate(suggestions, 1):
        print(f"\n{i}. {suggestion['問題']}")
        print("   解決方案:")
        for sol in suggestion['解決方案']:
            print(f"   • {sol}")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Ragas 忠實度評估教程")
    print("=" * 60)

    print("\n什麼是忠實度？")
    print("  忠實度（Faithfulness）衡量生成的答案是否忠實於提供的上下文。")
    print("  高忠實度意味著答案完全基於上下文，沒有編造或添加信息。")

    print("\n為什麼忠實度重要？")
    print("  • 防止 AI 幻覺（生成虛假信息）")
    print("  • 確保答案的可靠性和可信度")
    print("  • 提高 RAG 系統的實用價值")
    print("  • 避免誤導用戶")

    print("\n本示例包含:")
    print("  1. 高忠實度和低忠實度的對比示例")
    print("  2. 幻覺檢測方法")
    print("  3. 忠實度分析和報告")
    print("  4. 改進建議")

    input("\n按 Enter 開始評估...")

    # 執行評估
    evaluate_faithfulness()

    # 提供改進建議
    improve_faithfulness()

    print("\n" + "=" * 60)
    print("評估完成！")
    print("=" * 60)

    print("\n關鍵要點:")
    print("  • 忠實度是 RAG 系統最重要的指標之一")
    print("  • 定期監控忠實度可以及早發現問題")
    print("  • 通過優化提示詞和檢索策略可以提高忠實度")
    print("  • 低忠實度通常是幻覺的信號")


if __name__ == "__main__":
    main()
