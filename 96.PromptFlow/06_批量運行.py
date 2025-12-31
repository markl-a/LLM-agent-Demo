"""
PromptFlow 批量運行示例

本示例展示：
1. 批量測試數據準備
2. 批量運行配置
3. 結果分析和統計
4. 性能優化技巧
"""

import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def create_test_dataset():
    """創建測試數據集"""
    console.print("\n[cyan]1. 創建測試數據集[/cyan]\n")

    console.print("[yellow]數據格式:[/yellow] JSONL (每行一個 JSON 對象)\n")

    # 示例數據
    test_data = [
        {
            "question": "什麼是機器學習？",
            "context": "機器學習是人工智能的一個分支...",
            "expected_keywords": ["AI", "算法", "數據"]
        },
        {
            "question": "Python 的主要特點是什麼？",
            "context": "Python 是一種高級程式語言...",
            "expected_keywords": ["簡單", "易讀", "庫"]
        },
        {
            "question": "如何優化數據庫查詢？",
            "context": "數據庫優化涉及多個方面...",
            "expected_keywords": ["索引", "查詢計劃", "緩存"]
        },
        {
            "question": "什麼是 RESTful API？",
            "context": "REST 是一種軟件架構風格...",
            "expected_keywords": ["HTTP", "無狀態", "資源"]
        },
        {
            "question": "Docker 的優勢是什麼？",
            "context": "Docker 是一個容器化平台...",
            "expected_keywords": ["容器", "隔離", "移植性"]
        },
    ]

    # 顯示數據示例
    table = Table(title="測試數據集示例")
    table.add_column("ID", style="cyan", width=5)
    table.add_column("問題", style="yellow", width=30)
    table.add_column("關鍵詞", style="green", width=25)

    for i, item in enumerate(test_data, 1):
        table.add_row(
            str(i),
            item["question"],
            ", ".join(item["expected_keywords"])
        )

    console.print(table)
    console.print()

    # 保存為 JSONL
    output_file = Path("test_data.jsonl")
    with open(output_file, "w", encoding="utf-8") as f:
        for item in test_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    console.print(f"[green]✓ 測試數據已保存到: {output_file}[/green]\n")

    # 顯示 JSONL 格式
    console.print("[dim]JSONL 格式示例:[/dim]")
    console.print('[dim]{"question": "問題1", "context": "上下文1"}[/dim]')
    console.print('[dim]{"question": "問題2", "context": "上下文2"}[/dim]')
    console.print()

    return test_data


def show_batch_run_cli():
    """顯示批量運行 CLI 命令"""
    console.print("[cyan]2. 批量運行 CLI 命令[/cyan]\n")

    commands = [
        ("基本批量運行", "pf run create --flow ./my_flow --data ./test_data.jsonl --name my_run"),
        ("流式輸出", "pf run create --flow ./my_flow --data ./test_data.jsonl --stream"),
        ("指定列映射", "pf run create --flow ./my_flow --data ./test_data.jsonl --column-mapping question='${data.question}'"),
        ("查看運行狀態", "pf run show --name my_run"),
        ("查看運行列表", "pf run list"),
        ("查看運行詳情", "pf run show-details --name my_run"),
        ("查看運行指標", "pf run show-metrics --name my_run"),
        ("導出運行結果", "pf run export --name my_run --output ./results.json"),
    ]

    table = Table(title="批量運行命令")
    table.add_column("用途", style="cyan", width=20)
    table.add_column("命令", style="yellow")

    for purpose, command in commands:
        table.add_row(purpose, command)

    console.print(table)
    console.print()


def show_column_mapping():
    """列映射配置"""
    console.print("[cyan]3. 列映射（Column Mapping）[/cyan]\n")

    console.print("[yellow]用途:[/yellow] 將數據集中的列映射到 Flow 的輸入參數\n")

    # 數據集結構
    console.print("[dim]數據集列:[/dim]")
    console.print("  • question")
    console.print("  • context")
    console.print("  • expected_keywords\n")

    # Flow 輸入
    console.print("[dim]Flow 輸入參數:[/dim]")
    console.print("  • user_query")
    console.print("  • reference_text\n")

    # 映射配置
    mapping = """# 方式 1: CLI 參數
pf run create \\
  --flow ./my_flow \\
  --data ./test_data.jsonl \\
  --column-mapping \\
    user_query='${data.question}' \\
    reference_text='${data.context}'

# 方式 2: 配置文件 (run.yaml)
$schema: https://azuremlschemas.azureedge.net/promptflow/latest/Run.schema.json
flow: ./my_flow
data: ./test_data.jsonl
column_mapping:
  user_query: ${data.question}
  reference_text: ${data.context}

# 運行配置文件
pf run create --file run.yaml"""

    from rich.syntax import Syntax
    syntax = Syntax(mapping, "yaml", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def simulate_batch_run():
    """模擬批量運行過程"""
    console.print("[cyan]4. 模擬批量運行過程[/cyan]\n")

    test_data = [
        {"id": 1, "question": "問題 1"},
        {"id": 2, "question": "問題 2"},
        {"id": 3, "question": "問題 3"},
        {"id": 4, "question": "問題 4"},
        {"id": 5, "question": "問題 5"},
    ]

    results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]運行 Flow...", total=len(test_data))

        for item in test_data:
            # 模擬處理
            import time
            time.sleep(0.3)

            result = {
                "id": item["id"],
                "input": item["question"],
                "output": f"回答 {item['id']}",
                "latency": 0.85 + (item["id"] * 0.1),
                "tokens": 150 + (item["id"] * 10)
            }
            results.append(result)

            progress.update(task, advance=1)

    console.print()

    # 顯示結果
    table = Table(title="批量運行結果")
    table.add_column("ID", style="cyan")
    table.add_column("輸入", style="yellow")
    table.add_column("輸出", style="green")
    table.add_column("延遲(s)", style="magenta")
    table.add_column("Tokens", style="blue")

    for result in results:
        table.add_row(
            str(result["id"]),
            result["input"],
            result["output"],
            f"{result['latency']:.2f}",
            str(result["tokens"])
        )

    console.print(table)
    console.print()

    return results


def analyze_results(results):
    """分析批量運行結果"""
    console.print("[cyan]5. 結果分析和統計[/cyan]\n")

    # 計算統計數據
    total_runs = len(results)
    total_tokens = sum(r["tokens"] for r in results)
    avg_latency = sum(r["latency"] for r in results) / total_runs
    min_latency = min(r["latency"] for r in results)
    max_latency = max(r["latency"] for r in results)

    # 顯示統計表
    table = Table(title="性能統計")
    table.add_column("指標", style="cyan")
    table.add_column("值", style="yellow")

    table.add_row("總運行次數", str(total_runs))
    table.add_row("總 Token 數", str(total_tokens))
    table.add_row("平均延遲", f"{avg_latency:.2f}s")
    table.add_row("最小延遲", f"{min_latency:.2f}s")
    table.add_row("最大延遲", f"{max_latency:.2f}s")
    table.add_row("預估成本", f"${total_tokens * 0.00002:.4f}")

    console.print(table)
    console.print()


def show_parallel_execution():
    """並行執行配置"""
    console.print("[cyan]6. 並行執行優化[/cyan]\n")

    config = """# 設置並行執行數
# 方式 1: CLI 參數
pf run create \\
  --flow ./my_flow \\
  --data ./test_data.jsonl \\
  --worker-count 4  # 使用 4 個並行工作進程

# 方式 2: 配置文件
$schema: https://azuremlschemas.azureedge.net/promptflow/latest/Run.schema.json
flow: ./my_flow
data: ./test_data.jsonl
run:
  worker_count: 4
  batch_size: 10

# 注意事項
# 1. worker_count 不應超過 CPU 核心數
# 2. LLM 調用可能有速率限制
# 3. 過多並行可能導致 API 限流"""

    from rich.syntax import Syntax
    syntax = Syntax(config, "yaml", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_comparison_run():
    """對比運行"""
    console.print("[cyan]7. 對比多個運行結果[/cyan]\n")

    # 模擬兩個運行的對比
    runs = [
        {
            "name": "baseline_v1",
            "avg_latency": 1.2,
            "avg_tokens": 180,
            "success_rate": 0.95
        },
        {
            "name": "optimized_v2",
            "avg_latency": 0.8,
            "avg_tokens": 150,
            "success_rate": 0.97
        },
    ]

    table = Table(title="運行對比")
    table.add_column("運行名稱", style="cyan")
    table.add_column("平均延遲", style="yellow")
    table.add_column("平均 Tokens", style="green")
    table.add_column("成功率", style="magenta")
    table.add_column("改進", style="blue")

    baseline = runs[0]
    for run in runs:
        if run == baseline:
            improvement = "-"
        else:
            latency_imp = (baseline["avg_latency"] - run["avg_latency"]) / baseline["avg_latency"] * 100
            improvement = f"{latency_imp:+.1f}%"

        table.add_row(
            run["name"],
            f"{run['avg_latency']:.2f}s",
            str(run["avg_tokens"]),
            f"{run['success_rate']:.1%}",
            improvement
        )

    console.print(table)
    console.print()

    # CLI 命令
    console.print("[dim]對比命令:[/dim]")
    console.print("[dim]pf run list[/dim]")
    console.print("[dim]pf run compare --runs baseline_v1 optimized_v2[/dim]")
    console.print()


def show_best_practices():
    """最佳實踐"""
    console.print("[cyan]批量運行最佳實踐[/cyan]\n")

    practices = """1. 數據準備
   - 使用代表性的測試數據
   - 包含各種邊界情況
   - 定期更新測試集

2. 運行配置
   - 合理設置並行數
   - 注意 API 速率限制
   - 配置超時時間

3. 結果分析
   - 記錄關鍵指標
   - 對比不同版本
   - 識別異常情況

4. 成本控制
   - 預估 token 使用量
   - 使用較小的測試集進行初步驗證
   - 監控實際成本

5. 自動化
   - 整合到 CI/CD 流程
   - 自動觸發測試
   - 自動生成報告

6. 版本管理
   - 保存運行配置
   - 記錄測試數據版本
   - 追蹤性能變化"""

    console.print(Panel(practices, border_style="cyan"))
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]PromptFlow 批量運行示例[/bold cyan]\n"
        "[dim]學習如何批量測試和評估 Flow[/dim]",
        border_style="cyan"
    ))

    # 1. 創建測試數據
    test_data = create_test_dataset()

    # 2. CLI 命令
    show_batch_run_cli()

    # 3. 列映射
    show_column_mapping()

    # 4. 模擬運行
    results = simulate_batch_run()

    # 5. 結果分析
    analyze_results(results)

    # 6. 並行執行
    show_parallel_execution()

    # 7. 對比運行
    show_comparison_run()

    # 8. 最佳實踐
    show_best_practices()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 批量運行示例完成！[/bold green]\n")
    console.print("[cyan]下一步:[/cyan]")
    console.print("  1. 查看 07_評估流程.py - 學習 Flow 評估")
    console.print("  2. 查看 08_部署服務.py - 學習部署")
    console.print("  3. 實踐: 創建自己的測試數據集並批量運行")


if __name__ == "__main__":
    main()
