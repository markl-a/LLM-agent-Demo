"""
PromptLayer 評分系統示例

本示例展示：
1. 請求評分
2. 評分分析
3. 質量追蹤
4. 反饋收集
"""

import os
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


def score_requests():
    """評分請求"""
    console.print("\n[cyan]1. 請求評分[/cyan]\n")

    code = """import promptlayer

# 運行請求並獲取 ID
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "你好"}],
    return_pl_id=True
)

request_id = response.pl_request_id

# 評分（0-100）
promptlayer.track.score(
    request_id=request_id,
    score=85,  # 質量分數
    metadata={
        "evaluated_by": "human",
        "criteria": "relevance, accuracy",
        "notes": "回答準確但可以更詳細"
    }
)

print(f"已評分: {request_id} - 85/100")
"""

    from rich.syntax import Syntax
    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print("\n[green]✓ 評分已記錄到 PromptLayer[/green]\n")


def batch_scoring():
    """批量評分"""
    console.print("[cyan]2. 批量評分[/cyan]\n")

    code = """def batch_score_requests(request_scores):
    \"\"\"批量評分多個請求\"\"\"
    for request_id, score, metadata in request_scores:
        promptlayer.track.score(
            request_id=request_id,
            score=score,
            metadata=metadata
        )
        print(f"已評分: {request_id} - {score}/100")

# 使用示例
scores = [
    ("req_123", 90, {"evaluator": "張三"}),
    ("req_124", 75, {"evaluator": "李四"}),
    ("req_125", 88, {"evaluator": "王五"})
]

batch_score_requests(scores)
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def analyze_scores():
    """分析評分"""
    console.print("[cyan]3. 評分分析和統計[/cyan]\n")

    code = """import pandas as pd

def analyze_request_scores(template_name=None):
    \"\"\"分析請求評分\"\"\"
    # 獲取帶評分的請求
    requests_data = get_requests_with_scores(template_name)
    
    df = pd.DataFrame(requests_data)
    scored = df[df['score'].notna()]
    
    print("=== 評分統計 ===")
    print(f"總請求數: {len(df)}")
    print(f"已評分: {len(scored)} ({len(scored)/len(df)*100:.1f}%)")
    print(f"\\n評分分布:")
    print(f"平均分: {scored['score'].mean():.1f}")
    print(f"中位數: {scored['score'].median():.1f}")
    print(f"標準差: {scored['score'].std():.1f}")
    print(f"最高分: {scored['score'].max():.0f}")
    print(f"最低分: {scored['score'].min():.0f}")
    
    # 分數段分布
    print(f"\\n分數段分布:")
    print(f"優秀 (90-100): {len(scored[scored['score'] >= 90])}")
    print(f"良好 (75-89): {len(scored[(scored['score'] >= 75) & (scored['score'] < 90)])}")
    print(f"及格 (60-74): {len(scored[(scored['score'] >= 60) & (scored['score'] < 75)])}")
    print(f"不及格 (<60): {len(scored[scored['score'] < 60])}")

analyze_request_scores("customer_service")
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]PromptLayer 評分系統示例[/bold cyan]\n"
        "[dim]學習如何評分和追蹤質量[/dim]",
        border_style="cyan"
    ))

    score_requests()
    batch_scoring()
    analyze_scores()

    console.print("="*60)
    console.print("[bold green]✓ 評分系統示例完成！[/bold green]\n")


if __name__ == "__main__":
    main()
