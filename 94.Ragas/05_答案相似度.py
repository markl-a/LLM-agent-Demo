"""
Ragas 答案相似度評估示例
展示如何評估生成答案與參考答案的相似度
"""

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_similarity
import pandas as pd


def create_similarity_test_dataset():
    """
    創建用於答案相似度測試的數據集

    Returns:
        Dataset: 測試數據集
    """
    data = {
        'question': [
            '什麼是深度學習？',
            'Python 列表和元組的區別是什麼？',
            '如何反轉 Python 字符串？',
            '什麼是 REST API？',
            '解釋什麼是虛擬環境？'
        ],
        'answer': [
            # 答案 1: 與參考答案語義相似但表述不同
            '深度學習是機器學習的一個分支，它使用多層神經網絡來學習數據的複雜表示。',

            # 答案 2: 相似但包含更多細節
            'Python 中，列表是可變的，可以修改元素；而元組是不可變的，創建後不能改變。列表用方括號 []，元組用圓括號 ()。',

            # 答案 3: 簡潔準確
            '使用切片 [::-1] 或 reversed() 函數可以反轉字符串。',

            # 答案 4: 較詳細的解釋
            'REST API 是一種基於 HTTP 協議的 Web 服務架構風格，使用標準的 HTTP 方法（GET、POST、PUT、DELETE）進行資源操作，具有無狀態、可緩存等特性。',

            # 答案 5: 簡化版本
            '虛擬環境是 Python 的獨立運行環境，用於隔離不同項目的依賴。'
        ],
        'contexts': [
            ['深度學習使用深度神經網絡，通過多層處理來提取特徵。',
             '它是機器學習的子領域，在圖像、語音等任務上表現優異。'],

            ['列表（list）是可變序列，可以添加、刪除、修改元素。',
             '元組（tuple）是不可變序列，一旦創建就不能改變。'],

            ['Python 提供多種方法反轉字符串。',
             '常用的方法包括切片操作和內置函數。'],

            ['REST（Representational State Transfer）是一種架構風格。',
             '它定義了一組約束條件，用於創建 Web 服務。'],

            ['虛擬環境允許為每個項目創建獨立的 Python 環境。',
             '這樣可以避免不同項目之間的依賴衝突。']
        ],
        'ground_truth': [
            # 參考答案 1
            '深度學習是機器學習的子領域，使用深層神經網絡學習數據表示。',

            # 參考答案 2
            '列表是可變的，元組是不可變的。',

            # 參考答案 3
            '可以使用 [::-1] 切片語法反轉字符串。',

            # 參考答案 4
            'REST API 是基於 HTTP 的 Web 服務架構，使用標準 HTTP 方法操作資源。',

            # 參考答案 5
            '虛擬環境是隔離的 Python 環境，用於管理項目依賴。'
        ]
    }

    return Dataset.from_dict(data)


def evaluate_answer_similarity():
    """
    執行答案相似度評估
    """
    print("=" * 60)
    print("Ragas 答案相似度評估")
    print("=" * 60)

    # 1. 創建測試數據集
    print("\n1. 創建測試數據集...")
    dataset = create_similarity_test_dataset()
    print(f"   數據集大小: {len(dataset)} 條")

    # 2. 執行相似度評估
    print("\n2. 執行答案相似度評估...")
    print("   評估中...")

    try:
        result = evaluate(
            dataset,
            metrics=[answer_similarity]
        )

        # 3. 顯示結果
        print("\n3. 評估結果:")
        print("-" * 60)

        # 整體得分
        overall_score = result['answer_similarity']
        print(f"\n整體相似度得分: {overall_score:.4f}")

        # 詳細結果
        df = result.to_pandas()
        print("\n詳細結果:")
        display_similarity_results(df)

        # 4. 分析結果
        print("\n4. 相似度分析:")
        analyze_similarity_results(df)

        # 5. 對比分析
        print("\n5. 答案對比分析:")
        compare_answers(df)

    except Exception as e:
        print(f"\n評估失敗: {str(e)}")
        print("提示: 確保已設置 OPENAI_API_KEY 環境變量")


def display_similarity_results(df):
    """
    顯示相似度評估結果

    Args:
        df: 包含評估結果的 DataFrame
    """
    for idx, row in df.iterrows():
        print(f"\n問題 {idx + 1}: {row['question']}")
        print(f"生成答案: {row['answer'][:80]}...")
        print(f"參考答案: {row['ground_truth'][:80]}...")
        print(f"相似度得分: {row['answer_similarity']:.4f}")


def analyze_similarity_results(df):
    """
    分析相似度評估結果

    Args:
        df: 包含評估結果的 DataFrame
    """
    # 統計不同相似度級別的數量
    high_sim = len(df[df['answer_similarity'] >= 0.8])
    medium_sim = len(df[(df['answer_similarity'] >= 0.6) & (df['answer_similarity'] < 0.8)])
    low_sim = len(df[df['answer_similarity'] < 0.6])

    print(f"\n相似度分佈:")
    print(f"   高相似度 (≥0.8): {high_sim} 條")
    print(f"   中等相似度 (0.6-0.8): {medium_sim} 條")
    print(f"   低相似度 (<0.6): {low_sim} 條")

    # 計算平均相似度
    avg_sim = df['answer_similarity'].mean()
    print(f"\n平均相似度: {avg_sim:.4f}")

    # 找出最高和最低相似度的示例
    max_idx = df['answer_similarity'].idxmax()
    min_idx = df['answer_similarity'].idxmin()

    print(f"\n最高相似度示例:")
    print(f"   問題: {df.loc[max_idx, 'question']}")
    print(f"   得分: {df.loc[max_idx, 'answer_similarity']:.4f}")

    print(f"\n最低相似度示例:")
    print(f"   問題: {df.loc[min_idx, 'question']}")
    print(f"   得分: {df.loc[min_idx, 'answer_similarity']:.4f}")


def compare_answers(df):
    """
    對比生成答案和參考答案

    Args:
        df: 評估結果 DataFrame
    """
    print("\n逐條對比分析:")

    for idx, row in df.iterrows():
        print(f"\n{'=' * 50}")
        print(f"問題 {idx + 1}: {row['question']}")
        print(f"{'=' * 50}")

        print(f"\n生成答案:")
        print(f"  {row['answer']}")

        print(f"\n參考答案:")
        print(f"  {row['ground_truth']}")

        print(f"\n相似度: {row['answer_similarity']:.4f}")

        # 分析差異
        analyze_answer_difference(
            row['answer'],
            row['ground_truth'],
            row['answer_similarity']
        )


def analyze_answer_difference(generated, reference, similarity):
    """
    分析生成答案和參考答案的差異

    Args:
        generated: 生成的答案
        reference: 參考答案
        similarity: 相似度分數
    """
    print(f"\n差異分析:")

    # 長度對比
    gen_len = len(generated)
    ref_len = len(reference)
    length_diff = abs(gen_len - ref_len) / max(gen_len, ref_len)

    if length_diff > 0.5:
        print(f"  • 長度差異較大 ({gen_len} vs {ref_len} 字符)")
    else:
        print(f"  • 長度相近 ({gen_len} vs {ref_len} 字符)")

    # 語義分析
    if similarity >= 0.8:
        print(f"  • 語義高度一致 ✓")
    elif similarity >= 0.6:
        print(f"  • 語義基本一致，有些表述差異")
    else:
        print(f"  • 語義差異較大，可能遺漏關鍵信息")

    # 詳細程度
    if gen_len > ref_len * 1.5:
        print(f"  • 生成答案更詳細")
    elif gen_len < ref_len * 0.5:
        print(f"  • 生成答案較簡潔")
    else:
        print(f"  • 詳細程度適中")


def similarity_use_cases():
    """
    展示答案相似度的使用場景
    """
    print("\n" + "=" * 60)
    print("答案相似度的應用場景")
    print("=" * 60)

    use_cases = [
        {
            "場景": "模型評估",
            "說明": "評估不同模型生成答案的質量",
            "示例": [
                "對比 GPT-4 和 Claude 的答案質量",
                "評估微調模型是否改進",
                "選擇最佳模型配置"
            ]
        },
        {
            "場景": "提示詞優化",
            "說明": "評估不同提示詞的效果",
            "示例": [
                "測試不同的提示詞模板",
                "優化 few-shot 示例",
                "調整生成參數"
            ]
        },
        {
            "場景": "回歸測試",
            "說明": "確保系統更新不會降低質量",
            "示例": [
                "部署前的質量檢查",
                "監控性能退化",
                "版本對比測試"
            ]
        },
        {
            "場景": "教育評估",
            "說明": "評估學生答案的準確性",
            "示例": [
                "自動評分系統",
                "學習效果評估",
                "提供改進建議"
            ]
        }
    ]

    for i, use_case in enumerate(use_cases, 1):
        print(f"\n{i}. {use_case['場景']}")
        print(f"   {use_case['說明']}")
        print(f"   應用示例:")
        for example in use_case['示例']:
            print(f"   • {example}")


def best_practices():
    """
    答案相似度評估的最佳實踐
    """
    print("\n" + "=" * 60)
    print("最佳實踐")
    print("=" * 60)

    practices = [
        {
            "實踐": "準備高質量參考答案",
            "要點": [
                "參考答案應該準確、完整",
                "覆蓋關鍵信息點",
                "保持一致的格式和風格",
                "定期更新和完善"
            ]
        },
        {
            "實踐": "設定合理的閾值",
            "要點": [
                "不要期望完全一致（1.0 分）",
                "語義相似即可，不要求字面相同",
                "根據應用場景調整標準",
                "參考行業基準"
            ]
        },
        {
            "實踐": "結合其他指標",
            "要點": [
                "單一指標不夠全面",
                "同時考慮相關性、忠實度等",
                "建立綜合評估體系",
                "平衡多個維度"
            ]
        },
        {
            "實踐": "處理邊界情況",
            "要點": [
                "考慮多個正確答案的情況",
                "處理答案長度差異",
                "識別等價的不同表述",
                "允許合理的擴展說明"
            ]
        }
    ]

    for i, practice in enumerate(practices, 1):
        print(f"\n{i}. {practice['實踐']}")
        for point in practice['要點']:
            print(f"   • {point}")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Ragas 答案相似度評估教程")
    print("=" * 60)

    print("\n什麼是答案相似度？")
    print("  答案相似度（Answer Similarity）衡量生成的答案與參考答案的語義相似程度。")
    print("  它使用語義嵌入來比較答案，而不是簡單的字符串匹配。")

    print("\n為什麼需要答案相似度？")
    print("  • 評估答案質量的客觀標準")
    print("  • 自動化測試和評估")
    print("  • 模型性能基準測試")
    print("  • 質量保證和監控")

    print("\n與傳統指標的區別:")
    print("  • BLEU/ROUGE: 基於 n-gram 重疊，字面匹配")
    print("  • 答案相似度: 基於語義嵌入，理解含義")
    print("  • 更適合評估生成式任務")

    print("\n本示例包含:")
    print("  1. 不同相似度級別的示例")
    print("  2. 詳細的對比分析")
    print("  3. 應用場景介紹")
    print("  4. 最佳實踐指南")

    input("\n按 Enter 開始評估...")

    # 執行評估
    evaluate_answer_similarity()

    # 應用場景
    similarity_use_cases()

    # 最佳實踐
    best_practices()

    print("\n" + "=" * 60)
    print("評估完成！")
    print("=" * 60)

    print("\n關鍵要點:")
    print("  • 答案相似度是評估答案質量的重要指標")
    print("  • 語義相似比字面匹配更有意義")
    print("  • 應該與其他指標結合使用")
    print("  • 需要高質量的參考答案")


if __name__ == "__main__":
    main()
