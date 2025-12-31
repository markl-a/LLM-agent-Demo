"""
Ragas 上下文精度評估示例
展示如何評估檢索上下文的精確度，確保檢索質量
"""

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import context_precision
import pandas as pd


def create_context_precision_dataset():
    """
    創建用於上下文精度測試的數據集

    Returns:
        Dataset: 測試數據集
    """
    data = {
        'question': [
            # 示例 1: 高精度（所有上下文都相關）
            'Python 中如何定義函數？',

            # 示例 2: 中等精度（部分上下文無關）
            '什麼是 Docker？',

            # 示例 3: 低精度（大部分上下文無關）
            '如何使用 Git 創建分支？',

            # 示例 4: 高精度
            'React Hooks 是什麼？',

            # 示例 5: 低精度（檢索到很多噪音）
            'SQL JOIN 有哪些類型？'
        ],
        'contexts': [
            # 上下文 1: 所有片段都高度相關
            [
                'Python 使用 def 關鍵字定義函數。',
                '函數定義的基本語法是: def function_name(parameters): 函數體',
                '函數可以有返回值，使用 return 語句返回。'
            ],

            # 上下文 2: 混合相關和無關內容
            [
                'Docker 是一個容器化平台，用於打包和運行應用程序。',
                'Kubernetes 是容器編排系統。',  # 相關但不是問題焦點
                'Docker 使用鏡像和容器的概念。',
                '雲計算技術包括很多工具。'  # 無關
            ],

            # 上下文 3: 大量無關內容
            [
                'Git 是版本控制系統。',  # 相關但太寬泛
                'GitHub 是代碼托管平台。',  # 無關
                'Python 是流行的編程語言。',  # 完全無關
                '使用 git branch <branch-name> 創建新分支。',  # 相關且精確
                'JavaScript 用於 Web 開發。'  # 完全無關
            ],

            # 上下文 4: 高精度
            [
                'React Hooks 是 React 16.8 引入的新特性。',
                'Hooks 允許在函數組件中使用狀態和其他 React 特性。',
                '常用的 Hooks 包括 useState、useEffect 等。'
            ],

            # 上下文 5: 低精度，噪音多
            [
                '數據庫是存儲數據的系統。',  # 太寬泛
                'SQL 是結構化查詢語言。',  # 相關但不精確
                'NoSQL 數據庫越來越流行。',  # 無關
                'SQL JOIN 用於連接多個表，包括 INNER JOIN、LEFT JOIN、RIGHT JOIN、FULL JOIN。',  # 精確相關
                'Python 可以連接數據庫。',  # 無關
                '索引可以提高查詢性能。'  # 無關
            ]
        ],
        'ground_truth': [
            '使用 def 關鍵字定義函數',
            'Docker 是容器化平台',
            '使用 git branch 命令創建分支',
            'Hooks 允許函數組件使用狀態',
            'SQL JOIN 包括 INNER、LEFT、RIGHT、FULL JOIN'
        ]
    }

    return Dataset.from_dict(data)


def evaluate_context_precision():
    """
    執行上下文精度評估
    """
    print("=" * 60)
    print("Ragas 上下文精度評估")
    print("=" * 60)

    # 1. 創建測試數據集
    print("\n1. 創建測試數據集...")
    dataset = create_context_precision_dataset()
    print(f"   數據集大小: {len(dataset)} 條")

    # 2. 執行精度評估
    print("\n2. 執行上下文精度評估...")
    print("   評估中...")

    try:
        result = evaluate(
            dataset,
            metrics=[context_precision]
        )

        # 3. 顯示結果
        print("\n3. 評估結果:")
        print("-" * 60)

        # 整體得分
        overall_score = result['context_precision']
        print(f"\n整體上下文精度得分: {overall_score:.4f}")

        # 詳細結果
        df = result.to_pandas()
        print("\n詳細結果:")
        for idx, row in df.iterrows():
            print(f"\n問題 {idx + 1}: {row['question']}")
            print(f"精度得分: {row['context_precision']:.4f}")
            print(f"上下文數量: {len(row['contexts'])}")

        # 4. 分析結果
        print("\n4. 上下文精度分析:")
        analyze_context_precision(df)

        # 5. 識別問題
        print("\n5. 檢索問題診斷:")
        diagnose_retrieval_issues(df)

    except Exception as e:
        print(f"\n評估失敗: {str(e)}")
        print("提示: 確保已設置 OPENAI_API_KEY 環境變量")


def analyze_context_precision(df):
    """
    分析上下文精度評估結果

    Args:
        df: 包含評估結果的 DataFrame
    """
    # 統計不同精度級別的數量
    high_prec = len(df[df['context_precision'] >= 0.8])
    medium_prec = len(df[(df['context_precision'] >= 0.6) & (df['context_precision'] < 0.8)])
    low_prec = len(df[df['context_precision'] < 0.6])

    print(f"\n精度分佈:")
    print(f"   高精度 (≥0.8): {high_prec} 條")
    print(f"   中等精度 (0.6-0.8): {medium_prec} 條")
    print(f"   低精度 (<0.6): {low_prec} 條")

    # 計算平均精度
    avg_prec = df['context_precision'].mean()
    print(f"\n平均精度: {avg_prec:.4f}")

    # 分析上下文數量影響
    print(f"\n上下文數量分析:")
    for idx, row in df.iterrows():
        num_contexts = len(row['contexts'])
        precision = row['context_precision']
        print(f"   問題 {idx + 1}: {num_contexts} 個上下文, 精度 {precision:.4f}")

    # 評估檢索系統健康度
    print("\n檢索系統健康度評估:")
    if avg_prec >= 0.8:
        print("   ✓ 優秀: 檢索高度精確，噪音少")
    elif avg_prec >= 0.6:
        print("   ⚠️  良好: 檢索基本準確，存在一些無關內容")
    else:
        print("   ✗ 需要改進: 檢索噪音較多，精確度不足")


def diagnose_retrieval_issues(df, threshold=0.6):
    """
    診斷檢索問題

    Args:
        df: 評估結果 DataFrame
        threshold: 精度閾值
    """
    # 找出低精度的示例
    low_precision_cases = df[df['context_precision'] < threshold]

    if len(low_precision_cases) == 0:
        print("   ✓ 未檢測到明顯的檢索問題")
        return

    print(f"   檢測到 {len(low_precision_cases)} 個檢索精度問題:")
    print()

    for idx, row in low_precision_cases.iterrows():
        print(f"   案例 {idx + 1}:")
        print(f"   問題: {row['question']}")
        print(f"   精度: {row['context_precision']:.4f}")
        print(f"   檢索到 {len(row['contexts'])} 個上下文")

        # 分析可能的問題
        analyze_context_quality(row)
        print()


def analyze_context_quality(row):
    """
    分析上下文質量

    Args:
        row: 單條評估結果
    """
    contexts = row['contexts']
    question = row['question'].lower()

    print(f"   上下文分析:")

    # 檢查每個上下文片段
    relevant_count = 0
    for i, ctx in enumerate(contexts, 1):
        # 簡單的相關性檢查（實際應用中應該更複雜）
        question_words = set(question.split())
        context_words = set(ctx.lower().split())
        overlap = len(question_words & context_words)

        if overlap >= 2:
            relevant_count += 1
            print(f"   • 上下文 {i}: 可能相關 ✓")
        else:
            print(f"   • 上下文 {i}: 可能無關 ✗")

    relevance_ratio = relevant_count / len(contexts) if contexts else 0
    print(f"\n   相關上下文比例: {relevance_ratio:.2%}")

    # 診斷
    if relevance_ratio < 0.5:
        print(f"   診斷: 檢索到太多無關內容")
        print(f"   建議: 提高檢索相似度閾值，優化查詢重寫")
    elif len(contexts) > 5:
        print(f"   診斷: 檢索數量過多")
        print(f"   建議: 減少檢索數量或使用重排序")


def improve_context_precision():
    """
    提供改進上下文精度的建議
    """
    print("\n" + "=" * 60)
    print("改進上下文精度的策略")
    print("=" * 60)

    strategies = [
        {
            "策略": "優化檢索算法",
            "方法": [
                "使用更好的嵌入模型（如 OpenAI ada-002）",
                "調整相似度閾值，過濾低相關度結果",
                "使用混合檢索（向量 + 關鍵詞）",
                "實施查詢擴展技術"
            ]
        },
        {
            "策略": "實施重排序",
            "方法": [
                "使用交叉編碼器對檢索結果重新排序",
                "基於相關性分數過濾",
                "考慮多樣性，避免重複內容",
                "使用 Cohere Rerank 等專業工具"
            ]
        },
        {
            "策略": "優化查詢處理",
            "方法": [
                "提取查詢中的關鍵實體和概念",
                "查詢重寫和擴展",
                "處理同義詞和變體",
                "使用 HyDE（假設文檔嵌入）技術"
            ]
        },
        {
            "策略": "改進文檔分塊",
            "方法": [
                "使用合適的分塊大小（通常 200-500 tokens）",
                "保持語義完整性",
                "添加上下文元數據",
                "使用重疊分塊策略"
            ]
        },
        {
            "策略": "控制檢索數量",
            "方法": [
                "根據問題複雜度動態調整 top_k",
                "簡單問題檢索 3-5 個結果",
                "複雜問題可以檢索更多",
                "設置相似度閾值自動截斷"
            ]
        },
        {
            "策略": "評估和監控",
            "方法": [
                "定期評估檢索精度",
                "收集錯誤案例",
                "A/B 測試不同配置",
                "建立精度基準"
            ]
        }
    ]

    for i, strategy in enumerate(strategies, 1):
        print(f"\n{i}. {strategy['策略']}")
        print("   具體方法:")
        for method in strategy['方法']:
            print(f"   • {method}")

    # 提供代碼示例
    print("\n" + "=" * 60)
    print("代碼示例: 實施相似度閾值過濾")
    print("=" * 60)

    print("""
def filter_contexts_by_threshold(contexts, similarities, threshold=0.7):
    '''
    根據相似度閾值過濾上下文

    Args:
        contexts: 檢索到的上下文列表
        similarities: 對應的相似度分數
        threshold: 相似度閾值

    Returns:
        過濾後的高質量上下文
    '''
    filtered = [
        ctx for ctx, sim in zip(contexts, similarities)
        if sim >= threshold
    ]
    return filtered[:5]  # 最多保留5個

# 使用示例
contexts = vector_db.similarity_search_with_score(query, k=10)
high_quality_contexts = filter_contexts_by_threshold(
    [ctx.page_content for ctx, _ in contexts],
    [score for _, score in contexts],
    threshold=0.75
)
    """)


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Ragas 上下文精度評估教程")
    print("=" * 60)

    print("\n什麼是上下文精度？")
    print("  上下文精度（Context Precision）衡量檢索到的上下文與問題的相關程度。")
    print("  高精度意味著檢索到的大部分內容都與回答問題直接相關。")

    print("\n為什麼上下文精度重要？")
    print("  • 減少噪音，提高答案質量")
    print("  • 降低 token 消耗和成本")
    print("  • 減少模型被無關信息干擾的可能")
    print("  • 提升系統效率")

    print("\n常見的精度問題:")
    print("  • 檢索到太多無關內容")
    print("  • 檢索結果過於寬泛")
    print("  • 檢索數量過多")
    print("  • 相似度閾值設置不當")

    print("\n本示例包含:")
    print("  1. 不同精度級別的對比")
    print("  2. 檢索問題診斷")
    print("  3. 精度優化策略")
    print("  4. 實用代碼示例")

    input("\n按 Enter 開始評估...")

    # 執行評估
    evaluate_context_precision()

    # 提供改進建議
    improve_context_precision()

    print("\n" + "=" * 60)
    print("評估完成！")
    print("=" * 60)

    print("\n關鍵要點:")
    print("  • 上下文精度直接影響 RAG 系統效率")
    print("  • 通過優化檢索和重排序可以顯著提高精度")
    print("  • 精度和召回需要平衡")
    print("  • 定期評估有助於維持檢索質量")


if __name__ == "__main__":
    main()
