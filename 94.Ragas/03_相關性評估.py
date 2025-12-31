"""
Ragas 答案相關性評估示例
展示如何評估答案與問題的相關性，確保答案切題
"""

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_relevancy
import pandas as pd


def create_relevancy_test_dataset():
    """
    創建用於相關性測試的數據集
    包含高相關性和低相關性的示例

    Returns:
        Dataset: 測試數據集
    """
    data = {
        'question': [
            # 示例 1: 高相關性
            '如何在 Python 中讀取 CSV 文件？',

            # 示例 2: 低相關性（答案雖然相關但不夠直接）
            '什麼是深度學習？',

            # 示例 3: 高相關性
            'React 和 Vue 的主要區別是什麼？',

            # 示例 4: 離題（答案沒有回答問題）
            'Docker 容器和虛擬機有什麼不同？',

            # 示例 5: 部分相關（答案包含額外無關信息）
            '如何優化 SQL 查詢性能？'
        ],
        'answer': [
            # 答案 1: 直接相關
            '在 Python 中可以使用 pandas 庫讀取 CSV 文件：import pandas as pd; df = pd.read_csv("file.csv")',

            # 答案 2: 過於寬泛，沒有直接回答
            '深度學習是機器學習的一個分支，涉及許多技術和應用。它在計算機視覺、自然語言處理等領域都有應用。要學習深度學習，需要了解神經網絡、反向傳播等基礎概念。',

            # 答案 3: 精確相關
            'React 和 Vue 的主要區別：1) React 使用 JSX，Vue 使用模板語法；2) React 更靈活但學習曲線較陡；3) Vue 更易上手且有更完整的官方生態。',

            # 答案 4: 完全離題
            '容器技術在現代軟件開發中越來越重要。許多公司都在使用 Kubernetes 來管理容器。雲原生應用的發展推動了容器技術的普及。',

            # 答案 5: 包含太多無關信息
            'SQL 查詢優化很重要。首先要了解數據庫的歷史和發展。SQL 語言在 1970 年代被發明。現在有很多數據庫系統如 MySQL、PostgreSQL。優化方法包括創建索引、避免 SELECT *、使用 EXPLAIN 分析查詢計劃。數據庫設計也很重要。'
        ],
        'contexts': [
            # 上下文 1
            ['Python 的 pandas 庫提供了讀取各種文件格式的功能。',
             'read_csv() 函數可以讀取 CSV 文件並返回 DataFrame 對象。'],

            # 上下文 2
            ['深度學習使用多層神經網絡來學習數據的層次化表示。',
             '它通過反向傳播算法來訓練網絡，調整權重以最小化損失函數。'],

            # 上下文 3
            ['React 是 Facebook 開發的 JavaScript 庫，使用虛擬 DOM 和 JSX 語法。',
             'Vue 是漸進式框架，使用模板語法，提供了更完整的官方工具鏈。'],

            # 上下文 4
            ['Docker 容器是進程級隔離，共享主機操作系統內核，啟動快、資源占用少。',
             '虛擬機是完整的操作系統隔離，包含完整的 Guest OS，資源占用大但隔離性更強。'],

            # 上下文 5
            ['SQL 查詢優化的關鍵方法包括：創建合適的索引、避免全表掃描、優化 JOIN 操作。',
             '使用 EXPLAIN 可以分析查詢執行計劃，識別性能瓶頸。']
        ]
    }

    return Dataset.from_dict(data)


def evaluate_answer_relevancy():
    """
    執行答案相關性評估
    """
    print("=" * 60)
    print("Ragas 答案相關性評估")
    print("=" * 60)

    # 1. 創建測試數據集
    print("\n1. 創建測試數據集...")
    dataset = create_relevancy_test_dataset()
    print(f"   數據集大小: {len(dataset)} 條")

    # 2. 執行相關性評估
    print("\n2. 執行相關性評估...")
    print("   評估中...")

    try:
        result = evaluate(
            dataset,
            metrics=[answer_relevancy]
        )

        # 3. 顯示結果
        print("\n3. 評估結果:")
        print("-" * 60)

        # 整體得分
        overall_score = result['answer_relevancy']
        print(f"\n整體相關性得分: {overall_score:.4f}")

        # 詳細結果
        df = result.to_pandas()
        print("\n詳細結果:")

        # 創建簡化視圖
        display_df = pd.DataFrame({
            '問題': df['question'].str[:40] + '...',
            '答案預覽': df['answer'].str[:50] + '...',
            '相關性得分': df['answer_relevancy'].round(4)
        })
        print(display_df.to_string(index=False))

        # 4. 分析結果
        print("\n4. 相關性分析:")
        analyze_relevancy_results(df)

        # 5. 識別離題答案
        print("\n5. 離題檢測:")
        detect_off_topic_answers(df)

    except Exception as e:
        print(f"\n評估失敗: {str(e)}")
        print("提示: 確保已設置 OPENAI_API_KEY 環境變量")


def analyze_relevancy_results(df):
    """
    分析相關性評估結果

    Args:
        df: 包含評估結果的 DataFrame
    """
    # 統計不同相關性級別的數量
    high_rel = len(df[df['answer_relevancy'] >= 0.8])
    medium_rel = len(df[(df['answer_relevancy'] >= 0.6) & (df['answer_relevancy'] < 0.8)])
    low_rel = len(df[df['answer_relevancy'] < 0.6])

    print(f"\n相關性分佈:")
    print(f"   高相關性 (≥0.8): {high_rel} 條")
    print(f"   中等相關性 (0.6-0.8): {medium_rel} 條")
    print(f"   低相關性 (<0.6): {low_rel} 條")

    # 計算平均相關性
    avg_rel = df['answer_relevancy'].mean()
    print(f"\n平均相關性: {avg_rel:.4f}")

    # 找出最高和最低相關性的示例
    max_idx = df['answer_relevancy'].idxmax()
    min_idx = df['answer_relevancy'].idxmin()

    print(f"\n最高相關性示例:")
    print(f"   問題: {df.loc[max_idx, 'question']}")
    print(f"   得分: {df.loc[max_idx, 'answer_relevancy']:.4f}")

    print(f"\n最低相關性示例:")
    print(f"   問題: {df.loc[min_idx, 'question']}")
    print(f"   得分: {df.loc[min_idx, 'answer_relevancy']:.4f}")

    # 評估系統健康度
    print("\n系統健康度評估:")
    if avg_rel >= 0.8:
        print("   ✓ 優秀: 答案高度相關")
    elif avg_rel >= 0.6:
        print("   ⚠️  良好: 大部分答案相關，有改進空間")
    else:
        print("   ✗ 需要改進: 答案相關性較差")


def detect_off_topic_answers(df, threshold=0.6):
    """
    檢測離題答案

    Args:
        df: 評估結果 DataFrame
        threshold: 相關性閾值
    """
    # 找出低相關性的示例
    off_topic_cases = df[df['answer_relevancy'] < threshold]

    if len(off_topic_cases) == 0:
        print("   ✓ 未檢測到明顯的離題答案")
        return

    print(f"   檢測到 {len(off_topic_cases)} 個可能離題的答案:")
    print()

    for idx, row in off_topic_cases.iterrows():
        print(f"   案例 {idx + 1}:")
        print(f"   問題: {row['question']}")
        print(f"   答案: {row['answer'][:80]}...")
        print(f"   相關性: {row['answer_relevancy']:.4f}")

        # 診斷可能的原因
        diagnose_low_relevancy(row)
        print()


def diagnose_low_relevancy(row):
    """
    診斷低相關性的可能原因

    Args:
        row: 單條評估結果
    """
    question = row['question'].lower()
    answer = row['answer'].lower()

    # 檢查答案是否包含問題關鍵詞
    question_words = set(question.split())
    answer_words = set(answer.split())
    common_words = question_words & answer_words

    if len(common_words) < 2:
        print(f"   可能原因: 答案沒有包含問題的關鍵詞")

    # 檢查答案長度
    if len(answer) < 20:
        print(f"   可能原因: 答案過短，信息不足")
    elif len(answer) > 500:
        print(f"   可能原因: 答案過長，可能包含太多無關信息")

    # 檢查是否直接回答
    if not any(word in answer for word in ['是', '可以', '使用', '方法', '區別']):
        print(f"   可能原因: 答案沒有直接回答問題")


def improve_relevancy():
    """
    提供改進相關性的建議
    """
    print("\n" + "=" * 60)
    print("改進答案相關性的建議")
    print("=" * 60)

    strategies = [
        {
            "策略": "優化提示詞設計",
            "方法": [
                "明確要求直接回答問題",
                "示例: '請簡潔直接地回答以下問題，不要包含無關信息'",
                "使用少樣本學習提供好的示例"
            ]
        },
        {
            "策略": "改進問題理解",
            "方法": [
                "提取問題中的關鍵詞和意圖",
                "識別問題類型（what、how、why 等）",
                "根據問題類型調整答案結構"
            ]
        },
        {
            "策略": "控制答案長度",
            "方法": [
                "根據問題複雜度調整答案長度",
                "簡單問題給出簡潔答案",
                "複雜問題可以分點詳細說明",
                "使用 max_tokens 參數控制輸出長度"
            ]
        },
        {
            "策略": "後處理優化",
            "方法": [
                "移除答案中的無關句子",
                "突出與問題最相關的信息",
                "使用摘要技術壓縮冗長答案"
            ]
        },
        {
            "策略": "評估和迭代",
            "方法": [
                "定期評估答案相關性",
                "收集用戶反饋",
                "持續優化提示詞和生成策略"
            ]
        }
    ]

    for i, strategy in enumerate(strategies, 1):
        print(f"\n{i}. {strategy['策略']}")
        print("   具體方法:")
        for method in strategy['方法']:
            print(f"   • {method}")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Ragas 答案相關性評估教程")
    print("=" * 60)

    print("\n什麼是答案相關性？")
    print("  答案相關性（Answer Relevancy）衡量生成的答案與提出的問題的匹配程度。")
    print("  高相關性意味著答案直接、準確地回答了問題，沒有偏離主題。")

    print("\n為什麼相關性重要？")
    print("  • 確保用戶得到所需的信息")
    print("  • 提高用戶體驗和滿意度")
    print("  • 避免浪費用戶時間")
    print("  • 提升系統的實用性")

    print("\n常見的相關性問題:")
    print("  • 答案過於寬泛，沒有針對性")
    print("  • 答案包含太多無關信息")
    print("  • 答案完全離題")
    print("  • 答案過短，信息不足")

    print("\n本示例包含:")
    print("  1. 不同相關性級別的示例")
    print("  2. 離題檢測方法")
    print("  3. 相關性分析和診斷")
    print("  4. 改進策略")

    input("\n按 Enter 開始評估...")

    # 執行評估
    evaluate_answer_relevancy()

    # 提供改進建議
    improve_relevancy()

    print("\n" + "=" * 60)
    print("評估完成！")
    print("=" * 60)

    print("\n關鍵要點:")
    print("  • 答案相關性直接影響用戶體驗")
    print("  • 通過優化提示詞可以顯著提高相關性")
    print("  • 定期評估有助於維持高質量輸出")
    print("  • 相關性和忠實度需要平衡考慮")


if __name__ == "__main__":
    main()
