"""
Ragas 批量評估示例
展示如何高效地對大規模數據集進行評估
"""

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)
import pandas as pd
from typing import List, Dict
import json
from datetime import datetime


def load_test_dataset(size='small'):
    """
    加載測試數據集

    Args:
        size: 數據集大小 ('small', 'medium', 'large')

    Returns:
        Dataset: 測試數據集
    """
    # 基礎數據
    base_data = {
        'question': [
            '什麼是人工智慧？',
            'Python 和 Java 的主要區別？',
            '如何優化數據庫查詢？',
            '什麼是微服務架構？',
            '解釋 REST API 的原理',
            'Docker 的主要用途是什麼？',
            'Git 和 SVN 有什麼不同？',
            '什麼是機器學習？',
            'React 和 Vue 哪個更好？',
            'CSS Flexbox 如何使用？'
        ],
        'answer': [
            '人工智慧是計算機科學的一個分支，致力於創建能夠模擬人類智能的系統。',
            'Python 是解釋型動態語言，語法簡潔；Java 是編譯型靜態語言，性能更高。',
            '優化數據庫查詢可以通過創建索引、優化 SQL 語句、使用緩存等方法。',
            '微服務架構將應用拆分為獨立的小型服務，每個服務專注於特定功能。',
            'REST API 是基於 HTTP 協議的 Web 服務接口，使用標準 HTTP 方法進行資源操作。',
            'Docker 用於容器化應用，提供一致的運行環境，簡化部署和擴展。',
            'Git 是分布式版本控制系統，SVN 是集中式的；Git 更靈活但學習曲線較陡。',
            '機器學習是讓計算機從數據中學習模式的技術，無需明確編程。',
            'React 和 Vue 各有優勢，React 生態更大，Vue 更易學習，選擇取決於項目需求。',
            'Flexbox 是 CSS 佈局模塊，通過 display: flex 創建彈性容器，靈活排列子元素。'
        ],
        'contexts': [
            ['人工智慧（AI）旨在創建智能機器。', '它包括機器學習、深度學習等子領域。'],
            ['Python 語法簡潔，適合快速開發。', 'Java 性能優秀，廣泛用於企業應用。'],
            ['數據庫優化包括索引優化、查詢優化等。', '合適的索引可以大幅提升查詢速度。'],
            ['微服務將單體應用拆分為多個服務。', '每個服務可以獨立部署和擴展。'],
            ['REST 使用 HTTP 方法如 GET、POST 等。', '它是無狀態的架構風格。'],
            ['Docker 提供輕量級容器化。', '容器包含應用及其所有依賴。'],
            ['Git 支持分支和合併。', 'SVN 使用集中式服務器。'],
            ['機器學習從數據中發現模式。', '它包括監督學習和非監督學習。'],
            ['React 由 Facebook 開發。', 'Vue 是漸進式框架。'],
            ['Flexbox 簡化響應式佈局。', '它提供多種對齊和分佈選項。']
        ],
        'ground_truth': [
            'AI 是模擬人類智能的計算機系統。',
            'Python 動態簡潔，Java 靜態高效。',
            '通過索引和優化 SQL 提升查詢性能。',
            '微服務是獨立部署的小型服務架構。',
            'REST 是基於 HTTP 的無狀態 Web 服務。',
            'Docker 容器化應用提供一致環境。',
            'Git 分布式，SVN 集中式。',
            '機器學習讓計算機從數據學習。',
            '兩者各有優勢，按需選擇。',
            'Flexbox 是靈活的 CSS 佈局系統。'
        ]
    }

    # 根據大小調整數據集
    if size == 'small':
        # 小數據集：前 5 條
        data = {k: v[:5] for k, v in base_data.items()}
    elif size == 'medium':
        # 中等數據集：所有 10 條
        data = base_data
    else:  # large
        # 大數據集：複製數據以模擬大規模
        multiplier = 10
        data = {
            k: v * multiplier for k, v in base_data.items()
        }

    return Dataset.from_dict(data)


def batch_evaluate(dataset, metrics, batch_size=10):
    """
    批量評估數據集

    Args:
        dataset: 待評估的數據集
        metrics: 評估指標列表
        batch_size: 批次大小

    Returns:
        評估結果
    """
    print(f"\n開始批量評估...")
    print(f"  數據集大小: {len(dataset)}")
    print(f"  批次大小: {batch_size}")
    print(f"  評估指標: {[m.name for m in metrics]}")

    # 執行評估
    result = evaluate(
        dataset,
        metrics=metrics
    )

    return result


def analyze_batch_results(result):
    """
    分析批量評估結果

    Args:
        result: 評估結果
    """
    print("\n" + "=" * 60)
    print("批量評估結果分析")
    print("=" * 60)

    # 1. 整體統計
    print("\n1. 整體指標得分:")
    for metric_name, score in result.items():
        if not metric_name.startswith('_'):
            print(f"   {metric_name}: {score:.4f}")

    # 2. 轉換為 DataFrame 進行詳細分析
    df = result.to_pandas()

    # 3. 統計分佈
    print("\n2. 分數分佈統計:")
    metric_columns = [col for col in df.columns if col not in ['question', 'answer', 'contexts', 'ground_truth']]

    for col in metric_columns:
        if col in df.columns:
            print(f"\n   {col}:")
            print(f"     最小值: {df[col].min():.4f}")
            print(f"     最大值: {df[col].max():.4f}")
            print(f"     平均值: {df[col].mean():.4f}")
            print(f"     中位數: {df[col].median():.4f}")
            print(f"     標準差: {df[col].std():.4f}")

    # 4. 識別異常值
    print("\n3. 異常值檢測:")
    identify_outliers(df)

    # 5. 性能分析
    print("\n4. 性能分析:")
    analyze_performance(df)


def identify_outliers(df, threshold=0.5):
    """
    識別異常低分的數據

    Args:
        df: 評估結果 DataFrame
        threshold: 異常值閾值
    """
    metric_columns = [col for col in df.columns if col not in ['question', 'answer', 'contexts', 'ground_truth']]

    outliers_found = False

    for col in metric_columns:
        if col in df.columns:
            low_scores = df[df[col] < threshold]

            if len(low_scores) > 0:
                outliers_found = True
                print(f"\n   {col} 低於 {threshold} 的數據:")
                for idx, row in low_scores.iterrows():
                    print(f"     • 問題 {idx + 1}: {row['question'][:50]}... (得分: {row[col]:.3f})")

    if not outliers_found:
        print(f"   ✓ 未發現得分低於 {threshold} 的異常值")


def analyze_performance(df):
    """
    分析不同問題類型的性能

    Args:
        df: 評估結果 DataFrame
    """
    # 簡單分類問題類型
    df['question_type'] = df['question'].apply(classify_question)

    # 按類型統計
    print("\n   按問題類型統計:")
    for q_type in df['question_type'].unique():
        type_data = df[df['question_type'] == q_type]
        print(f"\n   {q_type} ({len(type_data)} 條):")

        metric_columns = [col for col in df.columns if col not in ['question', 'answer', 'contexts', 'ground_truth', 'question_type']]
        for col in metric_columns:
            if col in type_data.columns:
                avg_score = type_data[col].mean()
                print(f"     {col}: {avg_score:.4f}")


def classify_question(question):
    """
    簡單分類問題類型

    Args:
        question: 問題文本

    Returns:
        問題類型
    """
    question_lower = question.lower()

    if '什麼是' in question or 'what is' in question_lower:
        return '定義型'
    elif '區別' in question or '不同' in question or 'difference' in question_lower:
        return '比較型'
    elif '如何' in question or 'how to' in question_lower:
        return '方法型'
    else:
        return '其他'


def save_results(result, output_file='evaluation_results.json'):
    """
    保存評估結果到文件

    Args:
        result: 評估結果
        output_file: 輸出文件路徑
    """
    print(f"\n保存結果到 {output_file}...")

    # 轉換為可序列化的格式
    df = result.to_pandas()

    output_data = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            metric: float(score) for metric, score in result.items()
            if not metric.startswith('_')
        },
        'details': df.to_dict('records')
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"   ✓ 結果已保存")


def parallel_evaluation_example():
    """
    並行評估示例（概念展示）
    """
    print("\n" + "=" * 60)
    print("並行評估策略")
    print("=" * 60)

    print("""
對於大規模數據集，可以使用並行評估提升效率：

方法 1: 數據分片並行
-----------------
from concurrent.futures import ThreadPoolExecutor

def evaluate_chunk(chunk):
    return evaluate(chunk, metrics=metrics)

# 將數據集分成多個塊
chunks = split_dataset(dataset, num_chunks=4)

# 並行評估
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(evaluate_chunk, chunks))

# 合併結果
final_result = merge_results(results)


方法 2: 異步評估
-------------
import asyncio

async def async_evaluate(dataset, metrics):
    tasks = [evaluate_async(item, metrics) for item in dataset]
    return await asyncio.gather(*tasks)

# 運行異步評估
results = asyncio.run(async_evaluate(dataset, metrics))


方法 3: 分布式評估
--------------
# 使用 Ray 進行分布式評估
import ray

@ray.remote
def evaluate_remote(dataset_chunk):
    return evaluate(dataset_chunk, metrics=metrics)

# 分布式執行
ray.init()
chunks = split_dataset(dataset, num_chunks=10)
futures = [evaluate_remote.remote(chunk) for chunk in chunks]
results = ray.get(futures)
    """)


def optimization_tips():
    """
    批量評估優化建議
    """
    print("\n" + "=" * 60)
    print("批量評估優化建議")
    print("=" * 60)

    tips = [
        {
            "建議": "使用批處理",
            "說明": "將大數據集分成小批次處理，避免內存溢出",
            "代碼": "for batch in create_batches(dataset, batch_size=100):\n    result = evaluate(batch, metrics)"
        },
        {
            "建議": "緩存結果",
            "說明": "對已評估的數據進行緩存，避免重複計算",
            "代碼": "cache = {}\nif cache_key in cache:\n    return cache[cache_key]"
        },
        {
            "建議": "選擇性評估",
            "說明": "只評估關鍵指標，減少計算量",
            "代碼": "metrics = [faithfulness, answer_relevancy]  # 只選擇重要指標"
        },
        {
            "建議": "採樣評估",
            "說明": "對大數據集進行採樣評估以快速驗證",
            "代碼": "sample = dataset.shuffle().select(range(100))  # 隨機採樣 100 條"
        },
        {
            "建議": "進度監控",
            "說明": "添加進度條顯示評估進度",
            "代碼": "from tqdm import tqdm\nfor item in tqdm(dataset):\n    evaluate(item)"
        }
    ]

    for i, tip in enumerate(tips, 1):
        print(f"\n{i}. {tip['建議']}")
        print(f"   說明: {tip['說明']}")
        print(f"   示例代碼:")
        for line in tip['代碼'].split('\n'):
            print(f"     {line}")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Ragas 批量評估教程")
    print("=" * 60)

    print("\n批量評估的重要性:")
    print("  • 評估系統整體性能")
    print("  • 發現系統性問題")
    print("  • 建立性能基準")
    print("  • 支持 A/B 測試")

    print("\n批量評估的挑戰:")
    print("  • 計算成本高")
    print("  • 耗時長")
    print("  • 內存占用大")
    print("  • 需要優化策略")

    print("\n選擇數據集大小:")
    print("  1. Small (5 條) - 快速測試")
    print("  2. Medium (10 條) - 標準評估")
    print("  3. Large (100 條) - 大規模評估")

    choice = input("\n請選擇 (1/2/3，默認 1): ").strip() or '1'

    size_map = {'1': 'small', '2': 'medium', '3': 'large'}
    size = size_map.get(choice, 'small')

    # 1. 加載數據集
    print(f"\n1. 加載 {size} 數據集...")
    dataset = load_test_dataset(size)
    print(f"   ✓ 已加載 {len(dataset)} 條數據")

    # 2. 選擇指標
    print("\n2. 選擇評估指標...")
    metrics = [
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall
    ]
    print(f"   ✓ 已選擇 {len(metrics)} 個指標")

    # 3. 執行評估
    print("\n3. 執行批量評估...")
    print("   (這可能需要一些時間...)")

    try:
        result = batch_evaluate(dataset, metrics)

        # 4. 分析結果
        analyze_batch_results(result)

        # 5. 保存結果
        save_results(result)

    except Exception as e:
        print(f"\n評估失敗: {str(e)}")
        print("提示: 確保已設置 OPENAI_API_KEY 環境變量")

    # 展示優化策略
    parallel_evaluation_example()
    optimization_tips()

    print("\n" + "=" * 60)
    print("批量評估完成！")
    print("=" * 60)

    print("\n關鍵要點:")
    print("  • 批量評估是系統評估的基礎")
    print("  • 需要平衡評估全面性和效率")
    print("  • 使用優化策略降低成本")
    print("  • 定期進行批量評估確保質量")


if __name__ == "__main__":
    main()
