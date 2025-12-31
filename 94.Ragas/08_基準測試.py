"""
Ragas 基準測試示例
展示如何建立性能基準並進行對比測試
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
import json
from datetime import datetime
from typing import Dict, List


def create_golden_dataset():
    """
    創建黃金標準測試集
    這是一個精心設計的測試集，用於基準測試

    Returns:
        Dataset: 黃金測試集
    """
    data = {
        'question': [
            # 技術定義類
            '什麼是 Docker？',
            '解釋什麼是 REST API',

            # 比較類
            'Git 和 SVN 有什麼區別？',
            'Python 列表和元組的差異是什麼？',

            # 方法類
            '如何優化 SQL 查詢？',
            '如何在 Python 中處理異常？',

            # 概念理解類
            '什麼是微服務架構？',
            '解釋深度學習的工作原理',

            # 實踐類
            'React Hooks 如何使用？',
            '如何設置 Docker 容器？'
        ],
        'answer': [
            'Docker 是一個開源的容器化平台，用於打包、分發和運行應用程序。',
            'REST API 是一種基於 HTTP 協議的 Web 服務架構風格，使用標準 HTTP 方法進行資源操作。',
            'Git 是分布式版本控制系統，每個開發者都有完整倉庫；SVN 是集中式的，依賴中央服務器。',
            'Python 列表是可變的，可以修改；元組是不可變的，創建後不能改變。列表用 []，元組用 ()。',
            'SQL 優化包括：創建適當的索引、避免 SELECT *、使用 JOIN 代替子查詢、分析執行計劃。',
            'Python 使用 try-except 塊處理異常。將可能出錯的代碼放在 try 中，在 except 中處理異常。',
            '微服務架構將應用拆分為多個獨立的小型服務，每個服務專注於特定業務功能，可以獨立部署和擴展。',
            '深度學習使用多層神經網絡學習數據的層次化表示。通過前向傳播計算輸出，反向傳播調整權重。',
            'React Hooks 如 useState 管理狀態，useEffect 處理副作用。在函數組件中調用：const [state, setState] = useState(initialValue)。',
            '使用 docker run 命令啟動容器，或創建 Dockerfile 定義鏡像，然後 docker build 構建並 docker run 運行。'
        ],
        'contexts': [
            ['Docker 提供容器化技術。', '容器包含應用及其依賴，確保一致性。'],
            ['REST 使用 HTTP 方法如 GET、POST。', '它是無狀態的架構風格。'],
            ['Git 支持分布式開發。', 'SVN 使用中央服務器存儲代碼。'],
            ['列表是可變序列。', '元組是不可變序列。'],
            ['索引可以加速查詢。', 'EXPLAIN 分析執行計劃。'],
            ['try-except 捕獲和處理異常。', 'finally 塊總是執行。'],
            ['微服務獨立部署。', '每個服務有自己的數據庫。'],
            ['深度學習使用多層網絡。', '反向傳播優化權重。'],
            ['useState 管理組件狀態。', 'useEffect 處理副作用。'],
            ['Dockerfile 定義鏡像。', 'docker run 啟動容器。']
        ],
        'ground_truth': [
            'Docker 是容器化平台。',
            'REST API 是基於 HTTP 的 Web 服務架構。',
            'Git 分布式，SVN 集中式。',
            '列表可變，元組不可變。',
            '通過索引和優化 SQL 提升性能。',
            '使用 try-except 捕獲異常。',
            '微服務是獨立部署的小型服務。',
            '深度學習通過多層網絡學習特徵。',
            'useState 管理狀態，useEffect 處理副作用。',
            '使用 Dockerfile 和 docker run。'
        ]
    }

    return Dataset.from_dict(data)


def run_benchmark(dataset, config_name='baseline'):
    """
    運行基準測試

    Args:
        dataset: 測試數據集
        config_name: 配置名稱

    Returns:
        評估結果
    """
    print(f"\n運行基準測試: {config_name}")
    print(f"  數據集大小: {len(dataset)}")

    # 評估指標
    metrics = [
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall
    ]

    try:
        # 執行評估
        result = evaluate(dataset, metrics=metrics)

        # 添加元數據
        benchmark_data = {
            'config_name': config_name,
            'timestamp': datetime.now().isoformat(),
            'dataset_size': len(dataset),
            'metrics': {
                metric: float(score) for metric, score in result.items()
                if not metric.startswith('_')
            }
        }

        return benchmark_data

    except Exception as e:
        print(f"  評估失敗: {str(e)}")
        return None


def compare_benchmarks(benchmarks: List[Dict]):
    """
    對比多個基準測試結果

    Args:
        benchmarks: 基準測試結果列表
    """
    print("\n" + "=" * 80)
    print("基準測試對比")
    print("=" * 80)

    if not benchmarks:
        print("沒有可對比的基準測試結果")
        return

    # 創建對比表
    print("\n指標對比:")
    print("-" * 80)

    # 獲取所有指標名稱
    all_metrics = set()
    for benchmark in benchmarks:
        all_metrics.update(benchmark['metrics'].keys())

    # 打印表頭
    header = f"{'指標':<25}"
    for benchmark in benchmarks:
        header += f"{benchmark['config_name']:<15}"
    print(header)
    print("-" * 80)

    # 打印每個指標的對比
    for metric in sorted(all_metrics):
        row = f"{metric:<25}"
        for benchmark in benchmarks:
            score = benchmark['metrics'].get(metric, 0)
            row += f"{score:<15.4f}"
        print(row)

    # 計算整體性能
    print("\n整體性能對比:")
    print("-" * 80)

    for benchmark in benchmarks:
        avg_score = sum(benchmark['metrics'].values()) / len(benchmark['metrics'])
        print(f"{benchmark['config_name']:<25}{avg_score:<15.4f}")

    # 找出最佳配置
    best_benchmark = max(benchmarks, key=lambda x: sum(x['metrics'].values()))
    print(f"\n最佳配置: {best_benchmark['config_name']}")


def analyze_improvement(baseline, current):
    """
    分析性能改進

    Args:
        baseline: 基準測試結果
        current: 當前測試結果
    """
    print("\n" + "=" * 80)
    print("性能改進分析")
    print("=" * 80)

    print(f"\n對比: {baseline['config_name']} vs {current['config_name']}")
    print("-" * 80)

    improvements = {}

    for metric in baseline['metrics']:
        if metric in current['metrics']:
            baseline_score = baseline['metrics'][metric]
            current_score = current['metrics'][metric]
            improvement = current_score - baseline_score
            improvement_pct = (improvement / baseline_score * 100) if baseline_score > 0 else 0

            improvements[metric] = {
                'baseline': baseline_score,
                'current': current_score,
                'improvement': improvement,
                'improvement_pct': improvement_pct
            }

            # 打印結果
            status = "✓" if improvement > 0 else "✗" if improvement < 0 else "="
            print(f"{metric:<25}{baseline_score:<10.4f}{current_score:<10.4f}"
                  f"{improvement:>10.4f} ({improvement_pct:>6.2f}%) {status}")

    # 整體改進
    baseline_avg = sum(baseline['metrics'].values()) / len(baseline['metrics'])
    current_avg = sum(current['metrics'].values()) / len(current['metrics'])
    overall_improvement = current_avg - baseline_avg
    overall_improvement_pct = (overall_improvement / baseline_avg * 100) if baseline_avg > 0 else 0

    print("-" * 80)
    print(f"{'整體性能':<25}{baseline_avg:<10.4f}{current_avg:<10.4f}"
          f"{overall_improvement:>10.4f} ({overall_improvement_pct:>6.2f}%)")

    # 總結
    print("\n總結:")
    if overall_improvement > 0.05:
        print("  ✓ 顯著改進！性能提升明顯。")
    elif overall_improvement > 0:
        print("  ✓ 輕微改進。繼續優化。")
    elif overall_improvement == 0:
        print("  = 性能持平。")
    else:
        print("  ✗ 性能下降。需要檢查配置。")


def save_benchmark(benchmark, filename='benchmarks.json'):
    """
    保存基準測試結果

    Args:
        benchmark: 基準測試結果
        filename: 文件名
    """
    # 讀取現有基準測試
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            benchmarks = json.load(f)
    except FileNotFoundError:
        benchmarks = []

    # 添加新結果
    benchmarks.append(benchmark)

    # 保存
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(benchmarks, f, ensure_ascii=False, indent=2)

    print(f"\n基準測試結果已保存到 {filename}")


def load_benchmarks(filename='benchmarks.json'):
    """
    加載歷史基準測試結果

    Args:
        filename: 文件名

    Returns:
        基準測試結果列表
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def benchmark_best_practices():
    """
    基準測試最佳實踐
    """
    print("\n" + "=" * 80)
    print("基準測試最佳實踐")
    print("=" * 80)

    practices = [
        {
            "實踐": "建立黃金標準測試集",
            "要點": [
                "精心選擇代表性問題",
                "覆蓋不同難度和類型",
                "確保測試集質量",
                "定期更新測試集"
            ]
        },
        {
            "實踐": "設定明確的基準線",
            "要點": [
                "記錄初始性能",
                "建立可接受的最低標準",
                "設定改進目標",
                "追蹤長期趨勢"
            ]
        },
        {
            "實踐": "系統化測試流程",
            "要點": [
                "每次更改後運行基準測試",
                "使用相同的測試集",
                "保持評估條件一致",
                "記錄所有變更"
            ]
        },
        {
            "實踐": "對比分析",
            "要點": [
                "與歷史數據對比",
                "與競品對比",
                "識別性能趨勢",
                "找出退化原因"
            ]
        },
        {
            "實踐": "持續改進",
            "要點": [
                "根據結果優化系統",
                "實施 A/B 測試",
                "迭代改進",
                "設定新的基準"
            ]
        }
    ]

    for i, practice in enumerate(practices, 1):
        print(f"\n{i}. {practice['實踐']}")
        for point in practice['要點']:
            print(f"   • {point}")


def benchmark_scenarios():
    """
    基準測試應用場景
    """
    print("\n" + "=" * 80)
    print("基準測試應用場景")
    print("=" * 80)

    scenarios = [
        {
            "場景": "模型升級評估",
            "描述": "評估新模型是否比舊模型更好",
            "步驟": [
                "使用相同測試集評估兩個模型",
                "對比關鍵指標",
                "分析改進點和退步點",
                "決定是否升級"
            ]
        },
        {
            "場景": "提示詞優化",
            "描述": "測試不同提示詞的效果",
            "步驟": [
                "準備多個提示詞變體",
                "在基準測試集上評估",
                "對比性能差異",
                "選擇最佳提示詞"
            ]
        },
        {
            "場景": "檢索策略優化",
            "描述": "評估不同檢索配置的效果",
            "步驟": [
                "測試不同的 top_k 值",
                "對比不同的嵌入模型",
                "評估重排序效果",
                "選擇最優配置"
            ]
        },
        {
            "場景": "回歸測試",
            "描述": "確保更新不會降低性能",
            "步驟": [
                "更新前運行基準測試",
                "更新後再次測試",
                "對比結果",
                "確保無退化"
            ]
        }
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['場景']}")
        print(f"   描述: {scenario['描述']}")
        print(f"   步驟:")
        for step in scenario['步驟']:
            print(f"   • {step}")


def main():
    """主函數"""
    print("\n" + "=" * 80)
    print("Ragas 基準測試教程")
    print("=" * 80)

    print("\n什麼是基準測試？")
    print("  基準測試是使用標準化測試集評估系統性能的過程。")
    print("  它提供了客觀的性能指標，用於對比和追蹤改進。")

    print("\n為什麼需要基準測試？")
    print("  • 建立性能基準線")
    print("  • 評估改進效果")
    print("  • 防止性能退化")
    print("  • 支持數據驅動決策")

    print("\n本示例包含:")
    print("  1. 黃金標準測試集創建")
    print("  2. 基準測試執行")
    print("  3. 對比分析")
    print("  4. 最佳實踐")

    input("\n按 Enter 開始基準測試...")

    # 1. 創建黃金測試集
    print("\n1. 創建黃金標準測試集...")
    dataset = create_golden_dataset()
    print(f"   ✓ 已創建 {len(dataset)} 條測試數據")

    # 2. 運行基線測試
    print("\n2. 運行基線測試...")
    try:
        baseline = run_benchmark(dataset, 'baseline')

        if baseline:
            print("\n基線測試完成:")
            for metric, score in baseline['metrics'].items():
                print(f"   {metric}: {score:.4f}")

            # 保存基準測試
            save_benchmark(baseline)

            # 加載歷史基準測試
            all_benchmarks = load_benchmarks()

            if len(all_benchmarks) > 1:
                # 對比最近的測試
                print("\n3. 與歷史基準對比...")
                compare_benchmarks(all_benchmarks[-2:])

                # 分析改進
                analyze_improvement(all_benchmarks[-2], all_benchmarks[-1])

    except Exception as e:
        print(f"\n基準測試失敗: {str(e)}")
        print("提示: 確保已設置 OPENAI_API_KEY 環境變量")

    # 最佳實踐
    benchmark_best_practices()

    # 應用場景
    benchmark_scenarios()

    print("\n" + "=" * 80)
    print("基準測試完成！")
    print("=" * 80)

    print("\n關鍵要點:")
    print("  • 基準測試是性能評估的基礎")
    print("  • 需要高質量的測試集")
    print("  • 定期運行確保質量")
    print("  • 用數據指導優化決策")


if __name__ == "__main__":
    main()
