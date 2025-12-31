"""
Ragas 報告生成示例
展示如何生成全面的評估報告，包括可視化和洞察
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


def create_comprehensive_dataset():
    """
    創建全面的測試數據集用於報告生成

    Returns:
        Dataset: 測試數據集
    """
    data = {
        'question': [
            '什麼是人工智慧？',
            'Python 和 Java 有什麼區別？',
            '如何優化 SQL 查詢性能？',
            '解釋微服務架構的優勢',
            'Docker 容器和虛擬機的區別？',
            '什麼是 REST API？',
            'React Hooks 如何使用？',
            'Git 的主要功能是什麼？',
            '深度學習的工作原理？',
            'Kubernetes 的用途是什麼？'
        ],
        'answer': [
            '人工智慧是計算機科學的一個分支，旨在創建能夠執行通常需要人類智能的任務的系統。',
            'Python 是動態類型的解釋型語言，語法簡潔；Java 是靜態類型的編譯型語言，性能更高。',
            'SQL 優化包括創建適當的索引、避免 SELECT *、優化 JOIN 操作、使用 EXPLAIN 分析查詢計劃。',
            '微服務架構的優勢包括：獨立部署、技術棧靈活、易於擴展、故障隔離。',
            'Docker 容器共享主機操作系統內核，啟動快、資源占用少；虛擬機包含完整 OS，隔離性更強但資源消耗大。',
            'REST API 是基於 HTTP 協議的 Web 服務架構風格，使用標準 HTTP 方法進行資源操作。',
            'React Hooks 如 useState 用於狀態管理，useEffect 用於副作用處理，在函數組件中使用。',
            'Git 是分布式版本控制系統，主要功能包括版本管理、分支合併、協作開發、歷史追蹤。',
            '深度學習使用多層神經網絡，通過前向傳播計算輸出，反向傳播調整權重，學習數據的層次化特徵。',
            'Kubernetes 是容器編排平台，用於自動化容器的部署、擴展和管理。'
        ],
        'contexts': [
            ['AI 模擬人類智能。', '包括機器學習、深度學習等技術。'],
            ['Python 語法簡潔易讀。', 'Java 性能優秀適合大型應用。'],
            ['索引加速查詢。', 'EXPLAIN 分析執行計劃。'],
            ['微服務獨立部署。', '每個服務專注特定功能。'],
            ['Docker 容器輕量級。', '虛擬機完全隔離。'],
            ['REST 使用 HTTP 方法。', '是無狀態架構。'],
            ['useState 管理狀態。', 'useEffect 處理副作用。'],
            ['Git 版本控制。', '支持分布式協作。'],
            ['深度學習使用神經網絡。', '多層學習特徵。'],
            ['Kubernetes 編排容器。', '自動化部署管理。']
        ],
        'ground_truth': [
            'AI 是模擬人類智能的計算機系統。',
            'Python 動態簡潔，Java 靜態高效。',
            '通過索引和優化 SQL 提升性能。',
            '微服務獨立部署、靈活擴展。',
            'Docker 輕量快速，虛擬機隔離性強。',
            'REST 是基於 HTTP 的 Web 服務架構。',
            'useState 和 useEffect 是常用 Hooks。',
            'Git 是分布式版本控制系統。',
            '深度學習通過多層網絡學習特徵。',
            'Kubernetes 自動化容器管理。'
        ]
    }

    return Dataset.from_dict(data)


class EvaluationReportGenerator:
    """評估報告生成器"""

    def __init__(self, evaluation_result):
        """
        初始化報告生成器

        Args:
            evaluation_result: Ragas 評估結果
        """
        self.result = evaluation_result
        self.df = evaluation_result.to_pandas()
        self.timestamp = datetime.now()

    def generate_executive_summary(self):
        """
        生成執行摘要

        Returns:
            執行摘要字典
        """
        # 提取指標
        metrics = {k: v for k, v in self.result.items() if not k.startswith('_')}

        # 計算整體得分
        overall_score = sum(metrics.values()) / len(metrics) if metrics else 0

        # 判斷等級
        if overall_score >= 0.85:
            grade = 'A - 優秀'
            recommendation = '系統表現出色，可以投入生產使用。'
        elif overall_score >= 0.75:
            grade = 'B - 良好'
            recommendation = '系統表現良好，建議進行小幅優化。'
        elif overall_score >= 0.65:
            grade = 'C - 中等'
            recommendation = '系統基本可用，需要重點優化。'
        else:
            grade = 'D - 需改進'
            recommendation = '系統需要大幅改進才能投入使用。'

        return {
            'overall_score': overall_score,
            'grade': grade,
            'total_samples': len(self.df),
            'metrics_evaluated': list(metrics.keys()),
            'recommendation': recommendation,
            'timestamp': self.timestamp.isoformat()
        }

    def generate_metrics_analysis(self):
        """
        生成詳細的指標分析

        Returns:
            指標分析字典
        """
        analysis = {}

        metric_columns = [col for col in self.df.columns
                         if col not in ['question', 'answer', 'contexts', 'ground_truth']]

        for metric in metric_columns:
            if metric in self.df.columns:
                scores = self.df[metric]

                analysis[metric] = {
                    'mean': float(scores.mean()),
                    'median': float(scores.median()),
                    'std': float(scores.std()),
                    'min': float(scores.min()),
                    'max': float(scores.max()),
                    'distribution': {
                        'excellent (≥0.9)': int((scores >= 0.9).sum()),
                        'good (0.8-0.9)': int(((scores >= 0.8) & (scores < 0.9)).sum()),
                        'fair (0.7-0.8)': int(((scores >= 0.7) & (scores < 0.8)).sum()),
                        'poor (<0.7)': int((scores < 0.7).sum())
                    }
                }

        return analysis

    def identify_issues(self, threshold=0.7):
        """
        識別問題案例

        Args:
            threshold: 問題閾值

        Returns:
            問題案例列表
        """
        issues = []

        metric_columns = [col for col in self.df.columns
                         if col not in ['question', 'answer', 'contexts', 'ground_truth']]

        for idx, row in self.df.iterrows():
            row_issues = []

            for metric in metric_columns:
                if metric in row and row[metric] < threshold:
                    row_issues.append({
                        'metric': metric,
                        'score': float(row[metric]),
                        'threshold': threshold
                    })

            if row_issues:
                issues.append({
                    'index': int(idx),
                    'question': row['question'],
                    'answer': row['answer'][:100] + '...' if len(row['answer']) > 100 else row['answer'],
                    'issues': row_issues
                })

        return issues

    def generate_recommendations(self):
        """
        生成改進建議

        Returns:
            建議列表
        """
        recommendations = []

        # 分析每個指標
        metrics_analysis = self.generate_metrics_analysis()

        for metric, stats in metrics_analysis.items():
            if stats['mean'] < 0.7:
                if metric == 'faithfulness':
                    recommendations.append({
                        'priority': 'high',
                        'metric': metric,
                        'issue': f'忠實度較低 ({stats["mean"]:.2f})',
                        'suggestions': [
                            '優化提示詞，強調基於上下文回答',
                            '降低生成溫度參數',
                            '實施答案驗證機制'
                        ]
                    })
                elif metric == 'answer_relevancy':
                    recommendations.append({
                        'priority': 'high',
                        'metric': metric,
                        'issue': f'答案相關性較低 ({stats["mean"]:.2f})',
                        'suggestions': [
                            '改進問題理解模塊',
                            '優化提示詞設計',
                            '控制答案長度'
                        ]
                    })
                elif metric == 'context_precision':
                    recommendations.append({
                        'priority': 'medium',
                        'metric': metric,
                        'issue': f'上下文精度較低 ({stats["mean"]:.2f})',
                        'suggestions': [
                            '提高檢索相似度閾值',
                            '實施重排序',
                            '優化查詢重寫'
                        ]
                    })
                elif metric == 'context_recall':
                    recommendations.append({
                        'priority': 'medium',
                        'metric': metric,
                        'issue': f'上下文召回較低 ({stats["mean"]:.2f})',
                        'suggestions': [
                            '增加檢索數量',
                            '使用查詢擴展',
                            '改進文檔分塊策略'
                        ]
                    })

        return recommendations

    def generate_html_report(self, output_file='evaluation_report.html'):
        """
        生成 HTML 格式的報告

        Args:
            output_file: 輸出文件路徑
        """
        summary = self.generate_executive_summary()
        metrics = self.generate_metrics_analysis()
        issues = self.identify_issues()
        recommendations = self.generate_recommendations()

        html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAG 系統評估報告</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .section {{
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric-card {{
            display: inline-block;
            width: 48%;
            margin: 1%;
            padding: 15px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 4px;
        }}
        .grade {{
            font-size: 48px;
            font-weight: bold;
            color: #667eea;
        }}
        .score {{
            font-size: 24px;
            color: #764ba2;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #667eea;
            color: white;
        }}
        .issue {{
            background: #fff3cd;
            padding: 10px;
            margin: 10px 0;
            border-left: 4px solid #ffc107;
            border-radius: 4px;
        }}
        .recommendation {{
            background: #d1ecf1;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #17a2b8;
            border-radius: 4px;
        }}
        .priority-high {{
            color: #dc3545;
            font-weight: bold;
        }}
        .priority-medium {{
            color: #ffc107;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>RAG 系統評估報告</h1>
        <p>生成時間: {summary['timestamp']}</p>
        <p>評估樣本: {summary['total_samples']} 條</p>
    </div>

    <div class="section">
        <h2>執行摘要</h2>
        <div style="text-align: center;">
            <div class="grade">{summary['grade']}</div>
            <div class="score">整體得分: {summary['overall_score']:.2%}</div>
            <p style="margin-top: 20px; font-size: 18px;">{summary['recommendation']}</p>
        </div>
    </div>

    <div class="section">
        <h2>指標詳情</h2>
"""

        # 添加指標卡片
        for metric, stats in metrics.items():
            html_content += f"""
        <div class="metric-card">
            <h3>{metric}</h3>
            <p><strong>平均值:</strong> {stats['mean']:.3f}</p>
            <p><strong>範圍:</strong> {stats['min']:.3f} - {stats['max']:.3f}</p>
            <p><strong>標準差:</strong> {stats['std']:.3f}</p>
        </div>
"""

        html_content += """
    </div>

    <div class="section">
        <h2>分數分佈</h2>
        <table>
            <tr>
                <th>指標</th>
                <th>優秀 (≥0.9)</th>
                <th>良好 (0.8-0.9)</th>
                <th>一般 (0.7-0.8)</th>
                <th>較差 (<0.7)</th>
            </tr>
"""

        for metric, stats in metrics.items():
            dist = stats['distribution']
            html_content += f"""
            <tr>
                <td>{metric}</td>
                <td>{dist['excellent (≥0.9)']}</td>
                <td>{dist['good (0.8-0.9)']}</td>
                <td>{dist['fair (0.7-0.8)']}</td>
                <td>{dist['poor (<0.7)']}</td>
            </tr>
"""

        html_content += """
        </table>
    </div>
"""

        # 添加問題案例
        if issues:
            html_content += """
    <div class="section">
        <h2>問題案例</h2>
"""
            for issue in issues[:5]:  # 只顯示前 5 個
                html_content += f"""
        <div class="issue">
            <h4>案例 {issue['index'] + 1}</h4>
            <p><strong>問題:</strong> {issue['question']}</p>
            <p><strong>答案:</strong> {issue['answer']}</p>
            <p><strong>問題指標:</strong></p>
            <ul>
"""
                for i in issue['issues']:
                    html_content += f"<li>{i['metric']}: {i['score']:.3f}</li>"

                html_content += """
            </ul>
        </div>
"""
            html_content += """
    </div>
"""

        # 添加建議
        if recommendations:
            html_content += """
    <div class="section">
        <h2>改進建議</h2>
"""
            for rec in recommendations:
                priority_class = f"priority-{rec['priority']}"
                html_content += f"""
        <div class="recommendation">
            <h4 class="{priority_class}">優先級: {rec['priority'].upper()}</h4>
            <p><strong>指標:</strong> {rec['metric']}</p>
            <p><strong>問題:</strong> {rec['issue']}</p>
            <p><strong>建議:</strong></p>
            <ul>
"""
                for suggestion in rec['suggestions']:
                    html_content += f"<li>{suggestion}</li>"

                html_content += """
            </ul>
        </div>
"""
            html_content += """
    </div>
"""

        html_content += """
</body>
</html>
"""

        # 保存文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"\n✓ HTML 報告已生成: {output_file}")

    def generate_json_report(self, output_file='evaluation_report.json'):
        """
        生成 JSON 格式的報告

        Args:
            output_file: 輸出文件路徑
        """
        report = {
            'executive_summary': self.generate_executive_summary(),
            'metrics_analysis': self.generate_metrics_analysis(),
            'issues': self.identify_issues(),
            'recommendations': self.generate_recommendations()
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"✓ JSON 報告已生成: {output_file}")

    def print_text_report(self):
        """
        打印文本格式的報告到控制台
        """
        summary = self.generate_executive_summary()
        metrics = self.generate_metrics_analysis()
        recommendations = self.generate_recommendations()

        print("\n" + "=" * 80)
        print("RAG 系統評估報告")
        print("=" * 80)

        print(f"\n執行摘要:")
        print(f"  整體得分: {summary['overall_score']:.2%}")
        print(f"  等級: {summary['grade']}")
        print(f"  評估樣本: {summary['total_samples']} 條")
        print(f"  建議: {summary['recommendation']}")

        print(f"\n指標分析:")
        for metric, stats in metrics.items():
            print(f"\n  {metric}:")
            print(f"    平均值: {stats['mean']:.3f}")
            print(f"    範圍: {stats['min']:.3f} - {stats['max']:.3f}")

        if recommendations:
            print(f"\n改進建議:")
            for i, rec in enumerate(recommendations, 1):
                print(f"\n  {i}. [{rec['priority'].upper()}] {rec['metric']}")
                print(f"     問題: {rec['issue']}")
                print(f"     建議:")
                for suggestion in rec['suggestions']:
                    print(f"     • {suggestion}")


def main():
    """主函數"""
    print("\n" + "=" * 80)
    print("Ragas 報告生成教程")
    print("=" * 80)

    print("\n報告的重要性:")
    print("  • 可視化評估結果")
    print("  • 識別問題和機會")
    print("  • 提供可操作的建議")
    print("  • 支持決策制定")

    print("\n報告類型:")
    print("  1. 文本報告 - 控制台輸出")
    print("  2. JSON 報告 - 機器可讀")
    print("  3. HTML 報告 - 可視化展示")

    input("\n按 Enter 開始生成報告...")

    # 1. 創建數據集並評估
    print("\n1. 準備數據並執行評估...")
    dataset = create_comprehensive_dataset()

    try:
        result = evaluate(
            dataset,
            metrics=[faithfulness, answer_relevancy, context_precision, context_recall]
        )

        print("   ✓ 評估完成")

        # 2. 創建報告生成器
        print("\n2. 創建報告生成器...")
        report_gen = EvaluationReportGenerator(result)

        # 3. 生成各種格式的報告
        print("\n3. 生成報告...")

        # 文本報告
        print("\n生成文本報告:")
        report_gen.print_text_report()

        # JSON 報告
        print("\n生成 JSON 報告...")
        report_gen.generate_json_report()

        # HTML 報告
        print("\n生成 HTML 報告...")
        report_gen.generate_html_report()

        print("\n" + "=" * 80)
        print("所有報告已生成！")
        print("=" * 80)

        print("\n生成的文件:")
        print("  • evaluation_report.json - 機器可讀的評估數據")
        print("  • evaluation_report.html - 可視化報告（在瀏覽器中打開查看）")

    except Exception as e:
        print(f"\n評估失敗: {str(e)}")
        print("提示: 確保已設置 OPENAI_API_KEY 環境變量")

    print("\n" + "=" * 80)
    print("報告生成完成！")
    print("=" * 80)

    print("\n關鍵要點:")
    print("  • 報告使評估結果更易理解")
    print("  • 不同格式適用於不同場景")
    print("  • 可操作的建議至關重要")
    print("  • 定期生成報告追蹤進展")


if __name__ == "__main__":
    main()
