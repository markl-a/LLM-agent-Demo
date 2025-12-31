"""
Ragas 持續監控示例
展示如何在生產環境中持續監控 RAG 系統性能
"""

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
import json
from datetime import datetime, timedelta
from typing import List, Dict
import random


class PerformanceMonitor:
    """RAG 系統性能監控器"""

    def __init__(self, alert_thresholds=None):
        """
        初始化監控器

        Args:
            alert_thresholds: 告警閾值字典
        """
        self.alert_thresholds = alert_thresholds or {
            'faithfulness': 0.7,
            'answer_relevancy': 0.7
        }
        self.history = []
        self.alerts = []

    def monitor_batch(self, dataset, batch_id=None):
        """
        監控一批數據

        Args:
            dataset: 待監控的數據集
            batch_id: 批次 ID

        Returns:
            監控結果
        """
        print(f"\n監控批次: {batch_id or 'unknown'}")
        print(f"  數據量: {len(dataset)}")

        # 執行評估
        try:
            result = evaluate(
                dataset,
                metrics=[faithfulness, answer_relevancy]
            )

            # 記錄結果
            monitor_result = {
                'timestamp': datetime.now().isoformat(),
                'batch_id': batch_id,
                'metrics': {
                    'faithfulness': float(result['faithfulness']),
                    'answer_relevancy': float(result['answer_relevancy'])
                },
                'sample_count': len(dataset)
            }

            self.history.append(monitor_result)

            # 檢查告警
            self._check_alerts(monitor_result)

            return monitor_result

        except Exception as e:
            print(f"  監控失敗: {str(e)}")
            return None

    def _check_alerts(self, result):
        """
        檢查是否需要告警

        Args:
            result: 監控結果
        """
        for metric, threshold in self.alert_thresholds.items():
            if metric in result['metrics']:
                score = result['metrics'][metric]

                if score < threshold:
                    alert = {
                        'timestamp': result['timestamp'],
                        'batch_id': result['batch_id'],
                        'metric': metric,
                        'score': score,
                        'threshold': threshold,
                        'severity': self._calculate_severity(score, threshold)
                    }
                    self.alerts.append(alert)
                    self._send_alert(alert)

    def _calculate_severity(self, score, threshold):
        """
        計算告警嚴重程度

        Args:
            score: 實際分數
            threshold: 閾值

        Returns:
            嚴重程度 (critical, warning, info)
        """
        gap = threshold - score

        if gap > 0.2:
            return 'critical'
        elif gap > 0.1:
            return 'warning'
        else:
            return 'info'

    def _send_alert(self, alert):
        """
        發送告警

        Args:
            alert: 告警信息
        """
        severity_icon = {
            'critical': '🚨',
            'warning': '⚠️',
            'info': 'ℹ️'
        }

        icon = severity_icon.get(alert['severity'], '•')

        print(f"\n{icon} 告警 [{alert['severity'].upper()}]")
        print(f"  時間: {alert['timestamp']}")
        print(f"  批次: {alert['batch_id']}")
        print(f"  指標: {alert['metric']}")
        print(f"  當前值: {alert['score']:.4f}")
        print(f"  閾值: {alert['threshold']:.4f}")

    def get_trend_analysis(self, window_size=5):
        """
        分析性能趨勢

        Args:
            window_size: 分析窗口大小

        Returns:
            趨勢分析結果
        """
        if len(self.history) < 2:
            return {
                'status': 'insufficient_data',
                'message': '數據不足，無法分析趨勢'
            }

        recent_history = self.history[-window_size:]

        # 計算每個指標的趨勢
        trends = {}

        for metric in self.alert_thresholds.keys():
            scores = [h['metrics'].get(metric, 0) for h in recent_history]

            # 簡單線性趨勢
            if len(scores) >= 2:
                trend = 'improving' if scores[-1] > scores[0] else 'declining' if scores[-1] < scores[0] else 'stable'
                avg_change = (scores[-1] - scores[0]) / len(scores)

                trends[metric] = {
                    'trend': trend,
                    'avg_change': avg_change,
                    'current': scores[-1],
                    'previous': scores[0]
                }

        return {
            'status': 'success',
            'trends': trends,
            'window_size': len(recent_history)
        }

    def generate_report(self):
        """
        生成監控報告

        Returns:
            監控報告
        """
        if not self.history:
            return {
                'status': 'no_data',
                'message': '沒有監控數據'
            }

        # 計算整體統計
        all_faithfulness = [h['metrics'].get('faithfulness', 0) for h in self.history]
        all_relevancy = [h['metrics'].get('answer_relevancy', 0) for h in self.history]

        report = {
            'timestamp': datetime.now().isoformat(),
            'monitoring_period': {
                'start': self.history[0]['timestamp'],
                'end': self.history[-1]['timestamp'],
                'batches_monitored': len(self.history)
            },
            'metrics_summary': {
                'faithfulness': {
                    'avg': sum(all_faithfulness) / len(all_faithfulness),
                    'min': min(all_faithfulness),
                    'max': max(all_faithfulness),
                    'current': all_faithfulness[-1]
                },
                'answer_relevancy': {
                    'avg': sum(all_relevancy) / len(all_relevancy),
                    'min': min(all_relevancy),
                    'max': max(all_relevancy),
                    'current': all_relevancy[-1]
                }
            },
            'alerts_summary': {
                'total_alerts': len(self.alerts),
                'by_severity': self._count_by_severity(),
                'recent_alerts': self.alerts[-5:]
            },
            'trend_analysis': self.get_trend_analysis()
        }

        return report

    def _count_by_severity(self):
        """
        按嚴重程度統計告警

        Returns:
            統計結果
        """
        counts = {'critical': 0, 'warning': 0, 'info': 0}

        for alert in self.alerts:
            severity = alert.get('severity', 'info')
            counts[severity] = counts.get(severity, 0) + 1

        return counts


def simulate_production_data(num_batches=5, batch_size=10):
    """
    模擬生產環境數據

    Args:
        num_batches: 批次數量
        batch_size: 每批數據量

    Yields:
        (batch_id, dataset) 元組
    """
    questions_pool = [
        '什麼是機器學習？',
        'Python 和 Java 的區別？',
        '如何優化數據庫？',
        '解釋深度學習',
        'Docker 的用途是什麼？',
        '什麼是 REST API？',
        'Git 如何使用？',
        '微服務架構的優勢？',
        'React 和 Vue 的對比',
        'SQL JOIN 類型有哪些？'
    ]

    for batch_idx in range(num_batches):
        # 隨機選擇問題
        selected_questions = random.sample(questions_pool, min(batch_size, len(questions_pool)))

        # 模擬答案（實際應該是系統真實輸出）
        data = {
            'question': selected_questions,
            'answer': [
                f'這是關於「{q}」的回答。' + '詳細內容...' * random.randint(1, 3)
                for q in selected_questions
            ],
            'contexts': [
                [f'上下文 {i+1}' for i in range(2)]
                for _ in selected_questions
            ]
        }

        dataset = Dataset.from_dict(data)
        batch_id = f'batch_{datetime.now().strftime("%Y%m%d")}_{batch_idx:03d}'

        yield batch_id, dataset


def print_monitoring_report(report):
    """
    打印監控報告

    Args:
        report: 監控報告
    """
    print("\n" + "=" * 80)
    print("監控報告")
    print("=" * 80)

    if report['status'] == 'no_data':
        print(f"\n{report['message']}")
        return

    # 監控期間
    period = report['monitoring_period']
    print(f"\n監控期間:")
    print(f"  開始時間: {period['start']}")
    print(f"  結束時間: {period['end']}")
    print(f"  監控批次: {period['batches_monitored']}")

    # 指標摘要
    print(f"\n指標摘要:")
    for metric, stats in report['metrics_summary'].items():
        print(f"\n  {metric}:")
        print(f"    當前值: {stats['current']:.4f}")
        print(f"    平均值: {stats['avg']:.4f}")
        print(f"    最小值: {stats['min']:.4f}")
        print(f"    最大值: {stats['max']:.4f}")

    # 告警摘要
    alerts = report['alerts_summary']
    print(f"\n告警摘要:")
    print(f"  總告警數: {alerts['total_alerts']}")

    if alerts['total_alerts'] > 0:
        by_severity = alerts['by_severity']
        print(f"  嚴重: {by_severity.get('critical', 0)}")
        print(f"  警告: {by_severity.get('warning', 0)}")
        print(f"  信息: {by_severity.get('info', 0)}")

        if alerts['recent_alerts']:
            print(f"\n  最近告警:")
            for alert in alerts['recent_alerts'][-3:]:
                print(f"    • {alert['metric']}: {alert['score']:.4f} "
                      f"(閾值: {alert['threshold']:.4f}) [{alert['severity']}]")

    # 趨勢分析
    trend = report['trend_analysis']
    if trend['status'] == 'success':
        print(f"\n趨勢分析:")
        for metric, trend_data in trend['trends'].items():
            trend_icon = {
                'improving': '📈',
                'declining': '📉',
                'stable': '➡️'
            }.get(trend_data['trend'], '•')

            print(f"  {metric}: {trend_icon} {trend_data['trend']}")
            print(f"    變化: {trend_data['avg_change']:+.4f}")


def monitoring_best_practices():
    """
    監控最佳實踐
    """
    print("\n" + "=" * 80)
    print("持續監控最佳實踐")
    print("=" * 80)

    practices = [
        {
            "實踐": "實時監控",
            "要點": [
                "監控生產環境的實際查詢",
                "設置合理的採樣率（如 1-5%）",
                "避免監控影響性能",
                "使用異步評估"
            ]
        },
        {
            "實踐": "設置告警",
            "要點": [
                "定義關鍵指標閾值",
                "分級告警（critical, warning, info）",
                "配置告警通道（郵件、Slack 等）",
                "避免告警疲勞"
            ]
        },
        {
            "實踐": "趨勢分析",
            "要點": [
                "追蹤長期性能趨勢",
                "識別性能退化",
                "關聯業務指標",
                "預測潛在問題"
            ]
        },
        {
            "實踐": "自動化響應",
            "要點": [
                "自動重試失敗查詢",
                "動態調整參數",
                "自動回滾問題版本",
                "觸發人工審查"
            ]
        },
        {
            "實踐": "定期報告",
            "要點": [
                "生成每日/每週報告",
                "可視化趨勢圖表",
                "分享給相關團隊",
                "記錄改進行動"
            ]
        }
    ]

    for i, practice in enumerate(practices, 1):
        print(f"\n{i}. {practice['實踐']}")
        for point in practice['要點']:
            print(f"   • {point}")


def integration_example():
    """
    整合示例
    """
    print("\n" + "=" * 80)
    print("生產環境整合示例")
    print("=" * 80)

    print("""
將監控整合到 RAG 系統:

```python
from ragas_monitor import PerformanceMonitor

# 初始化監控器
monitor = PerformanceMonitor(
    alert_thresholds={
        'faithfulness': 0.7,
        'answer_relevancy': 0.7
    }
)

# 在 RAG 查詢處理中
def process_query(query):
    # 生成答案
    answer, contexts = rag_system.query(query)

    # 採樣監控（1% 的查詢）
    if random.random() < 0.01:
        # 異步評估，不阻塞主流程
        monitor_dataset = create_dataset(query, answer, contexts)
        asyncio.create_task(
            monitor.monitor_batch(monitor_dataset, batch_id=generate_id())
        )

    return answer

# 定期生成報告
@scheduled(cron="0 0 * * *")  # 每天午夜
def daily_report():
    report = monitor.generate_report()
    send_to_dashboard(report)
    if report['alerts_summary']['total_alerts'] > 0:
        notify_team(report)
```

告警通知示例:

```python
def setup_alerts(monitor):
    # Slack 通知
    def send_slack_alert(alert):
        slack_client.chat_postMessage(
            channel='#rag-alerts',
            text=f"RAG 系統告警: {alert['metric']} "
                 f"低於閾值 {alert['threshold']}"
        )

    # 郵件通知
    def send_email_alert(alert):
        if alert['severity'] == 'critical':
            send_email(
                to='team@example.com',
                subject='RAG 系統嚴重告警',
                body=format_alert(alert)
            )

    monitor.on_alert = lambda alert: (
        send_slack_alert(alert),
        send_email_alert(alert) if alert['severity'] == 'critical' else None
    )
```
    """)


def main():
    """主函數"""
    print("\n" + "=" * 80)
    print("Ragas 持續監控教程")
    print("=" * 80)

    print("\n為什麼需要持續監控？")
    print("  • 及時發現性能問題")
    print("  • 確保生產環境質量")
    print("  • 追蹤長期趨勢")
    print("  • 支持快速響應")

    print("\n監控內容:")
    print("  • 核心質量指標（忠實度、相關性等）")
    print("  • 性能趨勢")
    print("  • 異常檢測")
    print("  • 用戶反饋")

    print("\n本示例包含:")
    print("  1. 性能監控器實現")
    print("  2. 告警機制")
    print("  3. 趨勢分析")
    print("  4. 監控報告")
    print("  5. 最佳實踐")

    input("\n按 Enter 開始模擬監控...")

    # 創建監控器
    print("\n1. 初始化監控器...")
    monitor = PerformanceMonitor(
        alert_thresholds={
            'faithfulness': 0.7,
            'answer_relevancy': 0.7
        }
    )
    print("   ✓ 監控器已初始化")

    # 模擬監控
    print("\n2. 模擬生產環境監控...")
    print("   (為演示目的，使用模擬數據)")

    try:
        for batch_id, dataset in simulate_production_data(num_batches=3, batch_size=3):
            result = monitor.monitor_batch(dataset, batch_id)

            if result:
                print(f"   ✓ 批次 {batch_id} 監控完成")
                print(f"     忠實度: {result['metrics']['faithfulness']:.4f}")
                print(f"     相關性: {result['metrics']['answer_relevancy']:.4f}")

        # 生成報告
        print("\n3. 生成監控報告...")
        report = monitor.generate_report()
        print_monitoring_report(report)

    except Exception as e:
        print(f"\n監控失敗: {str(e)}")
        print("提示: 在生產環境中需要設置 OPENAI_API_KEY")

    # 最佳實踐
    monitoring_best_practices()

    # 整合示例
    integration_example()

    print("\n" + "=" * 80)
    print("監控演示完成！")
    print("=" * 80)

    print("\n關鍵要點:")
    print("  • 持續監控是生產系統的必備")
    print("  • 設置合理的告警閾值")
    print("  • 關注趨勢而非單點")
    print("  • 自動化監控和響應")


if __name__ == "__main__":
    main()
