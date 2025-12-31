"""
DeepEval 儀表板示例
展示如何可視化評估結果和生成報告
"""

import json
from datetime import datetime
from typing import List, Dict


def generate_html_dashboard(test_results: List[Dict]) -> str:
    """
    生成 HTML 儀表板

    Args:
        test_results: 測試結果列表

    Returns:
        HTML 內容
    """
    # 計算統計數據
    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results if r.get('passed', False))
    failed_tests = total_tests - passed_tests
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    # 計算平均分數
    avg_scores = {}
    for result in test_results:
        for metric, score in result.get('scores', {}).items():
            if metric not in avg_scores:
                avg_scores[metric] = []
            avg_scores[metric].append(score)

    for metric in avg_scores:
        avg_scores[metric] = sum(avg_scores[metric]) / len(avg_scores[metric])

    html = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DeepEval 評估儀表板</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            color: #667eea;
            margin-bottom: 10px;
        }}

        .header p {{
            color: #666;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}

        .stat-card {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
        }}

        .stat-card h3 {{
            color: #666;
            font-size: 14px;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}

        .stat-value {{
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
        }}

        .stat-label {{
            color: #999;
            font-size: 12px;
            margin-top: 5px;
        }}

        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}

        .chart-card {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .chart-card h3 {{
            color: #333;
            margin-bottom: 20px;
        }}

        .test-results {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}

        th {{
            background: #f8f9fa;
            color: #333;
            font-weight: 600;
        }}

        .status-badge {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}

        .status-pass {{
            background: #d4edda;
            color: #155724;
        }}

        .status-fail {{
            background: #f8d7da;
            color: #721c24;
        }}

        .score {{
            font-weight: 600;
            color: #667eea;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DeepEval 評估儀表板</h1>
            <p>生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>總測試數</h3>
                <div class="stat-value">{total_tests}</div>
                <div class="stat-label">個測試用例</div>
            </div>

            <div class="stat-card">
                <h3>通過率</h3>
                <div class="stat-value">{pass_rate:.1f}%</div>
                <div class="stat-label">{passed_tests} 通過 / {failed_tests} 失敗</div>
            </div>

            <div class="stat-card">
                <h3>平均相關性</h3>
                <div class="stat-value">{avg_scores.get('relevancy', 0):.2f}</div>
                <div class="stat-label">答案相關性得分</div>
            </div>

            <div class="stat-card">
                <h3>平均忠實度</h3>
                <div class="stat-value">{avg_scores.get('faithfulness', 0):.2f}</div>
                <div class="stat-label">忠實度得分</div>
            </div>
        </div>

        <div class="charts-grid">
            <div class="chart-card">
                <h3>測試結果分佈</h3>
                <canvas id="passFailChart"></canvas>
            </div>

            <div class="chart-card">
                <h3>評估指標得分</h3>
                <canvas id="metricsChart"></canvas>
            </div>
        </div>

        <div class="test-results">
            <h3 style="margin-bottom: 20px;">詳細測試結果</h3>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>測試用例</th>
                        <th>狀態</th>
                        <th>相關性</th>
                        <th>忠實度</th>
                    </tr>
                </thead>
                <tbody>
"""

    # 添加測試結果行
    for i, result in enumerate(test_results, 1):
        status_class = 'status-pass' if result.get('passed') else 'status-fail'
        status_text = '通過' if result.get('passed') else '失敗'

        scores = result.get('scores', {})
        relevancy = scores.get('relevancy', 0)
        faithfulness = scores.get('faithfulness', 0)

        html += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{result.get('name', f'測試 {i}')}</td>
                        <td><span class="status-badge {status_class}">{status_text}</span></td>
                        <td class="score">{relevancy:.3f}</td>
                        <td class="score">{faithfulness:.3f}</td>
                    </tr>
"""

    html += f"""
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // 通過/失敗餅圖
        const passFailCtx = document.getElementById('passFailChart').getContext('2d');
        new Chart(passFailCtx, {{
            type: 'pie',
            data: {{
                labels: ['通過', '失敗'],
                datasets: [{{
                    data: [{passed_tests}, {failed_tests}],
                    backgroundColor: ['#28a745', '#dc3545']
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false
            }}
        }});

        // 指標得分柱狀圖
        const metricsCtx = document.getElementById('metricsChart').getContext('2d');
        new Chart(metricsCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(list(avg_scores.keys()))},
                datasets: [{{
                    label: '平均得分',
                    data: {json.dumps(list(avg_scores.values()))},
                    backgroundColor: '#667eea'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 1
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
    """

    return html


def create_sample_results() -> List[Dict]:
    """創建示例測試結果"""
    import random

    results = []
    test_names = [
        "什麼是 Python？",
        "Docker 的用途",
        "解釋機器學習",
        "REST API 原理",
        "Git 和 SVN 區別"
    ]

    for i, name in enumerate(test_names):
        relevancy = random.uniform(0.6, 0.95)
        faithfulness = random.uniform(0.65, 0.92)

        results.append({
            'name': name,
            'passed': relevancy >= 0.7 and faithfulness >= 0.7,
            'scores': {
                'relevancy': relevancy,
                'faithfulness': faithfulness
            }
        })

    return results


def generate_json_report(test_results: List[Dict]) -> str:
    """生成 JSON 格式報告"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_tests': len(test_results),
            'passed': sum(1 for r in test_results if r.get('passed')),
            'failed': sum(1 for r in test_results if not r.get('passed')),
            'pass_rate': sum(1 for r in test_results if r.get('passed')) / len(test_results) if test_results else 0
        },
        'results': test_results
    }

    return json.dumps(report, indent=2, ensure_ascii=False)


def generate_markdown_report(test_results: List[Dict]) -> str:
    """生成 Markdown 格式報告"""
    total = len(test_results)
    passed = sum(1 for r in test_results if r.get('passed'))
    failed = total - passed

    md = f"""# DeepEval 評估報告

**生成時間:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 摘要

- **總測試數:** {total}
- **通過:** {passed} ✓
- **失敗:** {failed} ✗
- **通過率:** {passed/total*100:.1f}%

## 詳細結果

| # | 測試用例 | 狀態 | 相關性 | 忠實度 |
|---|---------|------|--------|--------|
"""

    for i, result in enumerate(test_results, 1):
        status = '✓ 通過' if result.get('passed') else '✗ 失敗'
        scores = result.get('scores', {})
        relevancy = scores.get('relevancy', 0)
        faithfulness = scores.get('faithfulness', 0)

        md += f"| {i} | {result.get('name', f'測試 {i}')} | {status} | {relevancy:.3f} | {faithfulness:.3f} |\n"

    md += "\n## 建議\n\n"

    if passed / total < 0.8:
        md += "- ⚠️ 通過率較低，建議檢查失敗的測試用例\n"
        md += "- 優化提示詞和系統配置\n"
    else:
        md += "- ✓ 測試表現良好\n"
        md += "- 繼續保持質量標準\n"

    return md


def dashboard_features():
    """儀表板功能介紹"""
    print("\n" + "=" * 60)
    print("儀表板功能")
    print("=" * 60)

    features = [
        {
            "功能": "概覽統計",
            "描述": "快速查看關鍵指標",
            "包含": [
                "總測試數",
                "通過率",
                "平均得分",
                "趨勢指標"
            ]
        },
        {
            "功能": "可視化圖表",
            "描述": "直觀展示評估結果",
            "包含": [
                "通過/失敗分佈",
                "指標得分對比",
                "時間趨勢圖",
                "分數分佈直方圖"
            ]
        },
        {
            "功能": "詳細列表",
            "描述": "查看每個測試的詳情",
            "包含": [
                "測試用例名稱",
                "各項指標得分",
                "通過/失敗狀態",
                "失敗原因"
            ]
        },
        {
            "功能": "導出功能",
            "描述": "以多種格式導出報告",
            "包含": [
                "HTML 報告",
                "JSON 數據",
                "Markdown 文檔",
                "PDF 報告（可選）"
            ]
        }
    ]

    for i, feature in enumerate(features, 1):
        print(f"\n{i}. {feature['功能']}")
        print(f"   描述: {feature['描述']}")
        print(f"   包含:")
        for item in feature['包含']:
            print(f"   • {item}")


def integration_examples():
    """整合示例"""
    print("\n" + "=" * 60)
    print("儀表板整合示例")
    print("=" * 60)

    print("\n1. 與 CI/CD 整合:")
    print("""
# 在 CI 腳本中生成儀表板

pytest tests/ --html=report.html --self-contained-html

# 或使用自定義腳本
python generate_dashboard.py --input test-results.json --output dashboard.html
    """)

    print("\n2. 定期生成報告:")
    print("""
# 定時任務（cron）
0 0 * * * cd /path/to/project && python generate_dashboard.py

# 或使用 GitHub Actions
on:
  schedule:
    - cron: '0 0 * * *'
    """)

    print("\n3. 發布到網站:")
    print("""
# 部署到 GitHub Pages
- name: Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./reports
    """)


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("DeepEval 儀表板教程")
    print("=" * 60)

    print("\n為什麼需要儀表板？")
    print("  • 可視化評估結果")
    print("  • 追蹤性能趨勢")
    print("  • 快速識別問題")
    print("  • 與團隊共享結果")

    print("\n支持的格式:")
    print("  • HTML - 交互式網頁")
    print("  • JSON - 機器可讀")
    print("  • Markdown - 文檔格式")
    print("  • PDF - 打印友好（可選）")

    input("\n按 Enter 生成示例儀表板...")

    # 創建示例結果
    print("\n1. 創建示例測試結果...")
    results = create_sample_results()
    print(f"   ✓ 創建了 {len(results)} 個測試結果")

    # 生成 HTML 儀表板
    print("\n2. 生成 HTML 儀表板...")
    html = generate_html_dashboard(results)
    with open('dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("   ✓ 已生成 dashboard.html")

    # 生成 JSON 報告
    print("\n3. 生成 JSON 報告...")
    json_report = generate_json_report(results)
    with open('report.json', 'w', encoding='utf-8') as f:
        f.write(json_report)
    print("   ✓ 已生成 report.json")

    # 生成 Markdown 報告
    print("\n4. 生成 Markdown 報告...")
    md_report = generate_markdown_report(results)
    with open('report.md', 'w', encoding='utf-8') as f:
        f.write(md_report)
    print("   ✓ 已生成 report.md")

    # 功能介紹
    dashboard_features()
    integration_examples()

    print("\n" + "=" * 60)
    print("儀表板生成完成！")
    print("=" * 60)

    print("\n生成的文件:")
    print("  • dashboard.html - 在瀏覽器中打開查看")
    print("  • report.json - JSON 格式報告")
    print("  • report.md - Markdown 格式報告")

    print("\n關鍵要點:")
    print("  • 儀表板使結果更易理解")
    print("  • 支持多種導出格式")
    print("  • 可整合到 CI/CD 流程")
    print("  • 便於團隊協作和決策")


if __name__ == "__main__":
    main()
