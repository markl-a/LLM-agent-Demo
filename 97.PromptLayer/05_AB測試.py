"""
PromptLayer A/B 測試示例

本示例展示：
1. 設置 A/B 測試
2. 收集測試數據
3. 分析測試結果
4. 決策最佳版本
"""

import os
import random
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

console = Console()


def ab_test_concept():
    """A/B 測試概念"""
    console.print("\n[cyan]A/B 測試概念[/cyan]\n")

    concept = """A/B 測試用於對比不同提示版本的效果

流程：
1. 創建兩個版本（A 和 B）
2. 隨機分配流量
3. 收集性能數據
4. 統計分析對比
5. 選擇最佳版本

評估指標：
• 響應質量（評分）
• 響應速度（延遲）
• Token 使用（成本）
• 用戶滿意度
• 任務完成率"""

    console.print(Panel(concept, border_style="cyan"))
    console.print()


def setup_ab_test():
    """設置 A/B 測試"""
    console.print("[cyan]1. 設置 A/B 測試[/cyan]\n")

    code = """import promptlayer
import random

class ABTest:
    \"\"\"A/B 測試管理器\"\"\"

    def __init__(self, template_name, version_a, version_b, split_ratio=0.5):
        self.template_name = template_name
        self.version_a = version_a
        self.version_b = version_b
        self.split_ratio = split_ratio  # A 版本的流量比例

    def get_version(self, user_id=None):
        \"\"\"根據策略選擇版本\"\"\"

        # 策略 1: 隨機分配
        if random.random() < self.split_ratio:
            return 'A', self.version_a
        else:
            return 'B', self.version_b

        # 策略 2: 基於用戶 ID（一致性分配）
        # if user_id:
        #     hash_value = hash(user_id) % 100
        #     if hash_value < self.split_ratio * 100:
        #         return 'A', self.version_a
        #     else:
        #         return 'B', self.version_b

    def run_test(self, input_variables, user_id=None):
        \"\"\"運行 A/B 測試\"\"\"

        # 選擇版本
        variant, version = self.get_version(user_id)

        # 運行對應版本
        response = promptlayer.run(
            prompt_name=self.template_name,
            prompt_version=version,
            input_variables=input_variables,
            tags=[f"ab_test", f"variant_{variant}"],
            metadata={
                "ab_test_variant": variant,
                "user_id": user_id
            },
            return_metadata=True
        )

        # 記錄測試數據
        return {
            "variant": variant,
            "version": version,
            "response": response['response'],
            "request_id": response['request_id']
        }


# 使用示例
ab_test = ABTest(
    template_name="customer_service",
    version_a=1,  # 原始版本
    version_b=2,  # 新版本
    split_ratio=0.5  # 50/50 分配
)

# 運行測試
result = ab_test.run_test(
    input_variables={"question": "如何退款？"},
    user_id="user_123"
)

print(f"使用版本: {result['variant']}")
print(f"響應: {result['response']}")
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def collect_test_data():
    """收集測試數據"""
    console.print("[cyan]2. 收集和追蹤測試數據[/cyan]\n")

    code = """import requests
import pandas as pd
from datetime import datetime, timedelta

def collect_ab_test_data(template_name, days=7):
    \"\"\"收集 A/B 測試數據\"\"\"

    # 獲取測試期間的所有請求
    url = "https://api.promptlayer.com/rest/search-requests"

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    params = {
        "api_key": os.getenv("PROMPTLAYER_API_KEY"),
        "template_name": template_name,
        "tags": ["ab_test"],
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }

    response = requests.post(url, json=params)
    requests_data = response.json()

    # 轉換為 DataFrame
    df = pd.DataFrame(requests_data)

    # 提取變體信息
    df['variant'] = df['metadata'].apply(lambda x: x.get('ab_test_variant', 'unknown'))

    return df


def add_user_feedback(request_id, rating, feedback=None):
    \"\"\"添加用戶反饋\"\"\"

    # 評分（0-100）
    promptlayer.track.score(
        request_id=request_id,
        score=rating,
        metadata={
            "feedback_type": "user_rating",
            "feedback_text": feedback
        }
    )


# 模擬用戶反饋收集
def simulate_user_feedback(result):
    \"\"\"模擬收集用戶反饋\"\"\"

    # 顯示響應給用戶
    print("AI 響應:", result['response'])

    # 用戶評分 (實際應該從 UI 收集)
    user_rating = random.randint(60, 100)

    # 記錄反饋
    add_user_feedback(
        request_id=result['request_id'],
        rating=user_rating,
        feedback="測試反饋"
    )

    print(f"用戶評分: {user_rating}")

# 收集數據
df = collect_ab_test_data("customer_service", days=7)
print(f"收集了 {len(df)} 條測試數據")
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def analyze_results():
    """分析測試結果"""
    console.print("[cyan]3. 分析 A/B 測試結果[/cyan]\n")

    code = """import numpy as np
from scipy import stats

def analyze_ab_test(df):
    \"\"\"分析 A/B 測試結果\"\"\"

    # 分組統計
    variant_a = df[df['variant'] == 'A']
    variant_b = df[df['variant'] == 'B']

    print("=== A/B 測試分析 ===\\n")

    # 樣本量
    print(f"樣本量:")
    print(f"  版本 A: {len(variant_a)}")
    print(f"  版本 B: {len(variant_b)}")
    print()

    # 評分對比
    scores_a = variant_a['score'].dropna()
    scores_b = variant_b['score'].dropna()

    print(f"平均評分:")
    print(f"  版本 A: {scores_a.mean():.2f} (±{scores_a.std():.2f})")
    print(f"  版本 B: {scores_b.mean():.2f} (±{scores_b.std():.2f})")
    print()

    # 統計顯著性測試（t-test）
    if len(scores_a) > 0 and len(scores_b) > 0:
        t_stat, p_value = stats.ttest_ind(scores_a, scores_b)
        print(f"統計檢驗:")
        print(f"  t 統計量: {t_stat:.4f}")
        print(f"  p 值: {p_value:.4f}")
        print(f"  結論: {'顯著差異' if p_value < 0.05 else '無顯著差異'}")
        print()

    # 延遲對比
    print(f"平均延遲 (秒):")
    print(f"  版本 A: {variant_a['latency'].mean():.3f}")
    print(f"  版本 B: {variant_b['latency'].mean():.3f}")
    print()

    # Token 使用對比
    print(f"平均 Token 使用:")
    print(f"  版本 A: {variant_a['total_tokens'].mean():.1f}")
    print(f"  版本 B: {variant_b['total_tokens'].mean():.1f}")
    print()

    # 成本對比 (假設 $0.00002/token)
    cost_per_token = 0.00002
    print(f"平均成本 ($):")
    print(f"  版本 A: ${variant_a['total_tokens'].mean() * cost_per_token:.6f}")
    print(f"  版本 B: ${variant_b['total_tokens'].mean() * cost_per_token:.6f}")
    print()

    # 綜合評估
    print("=== 綜合評估 ===")

    def calculate_score(variant_df):
        # 綜合分數 = 質量分數 * 0.6 - 成本懲罰 * 0.2 - 延遲懲罰 * 0.2
        quality = variant_df['score'].mean() / 100
        cost_penalty = variant_df['total_tokens'].mean() / 1000
        latency_penalty = variant_df['latency'].mean()

        return quality * 0.6 - cost_penalty * 0.2 - latency_penalty * 0.2

    score_a = calculate_score(variant_a)
    score_b = calculate_score(variant_b)

    print(f"綜合分數:")
    print(f"  版本 A: {score_a:.4f}")
    print(f"  版本 B: {score_b:.4f}")
    print()
    print(f"推薦版本: {'A' if score_a > score_b else 'B'}")


# 執行分析
df = collect_ab_test_data("customer_service")
analyze_ab_test(df)
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def visualize_results():
    """可視化結果"""
    console.print("[cyan]4. 可視化 A/B 測試結果[/cyan]\n")

    code = """import matplotlib.pyplot as plt
import seaborn as sns

def visualize_ab_test(df):
    \"\"\"可視化 A/B 測試結果\"\"\"

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # 1. 評分分布
    sns.boxplot(data=df, x='variant', y='score', ax=axes[0, 0])
    axes[0, 0].set_title('評分分布對比')
    axes[0, 0].set_ylabel('評分')

    # 2. 延遲分布
    sns.violinplot(data=df, x='variant', y='latency', ax=axes[0, 1])
    axes[0, 1].set_title('延遲分布對比')
    axes[0, 1].set_ylabel('延遲 (秒)')

    # 3. Token 使用
    df.groupby('variant')['total_tokens'].mean().plot(kind='bar', ax=axes[1, 0])
    axes[1, 0].set_title('平均 Token 使用')
    axes[1, 0].set_ylabel('Tokens')
    axes[1, 0].set_xlabel('版本')

    # 4. 成本對比
    cost_data = df.groupby('variant')['total_tokens'].sum() * 0.00002
    cost_data.plot(kind='bar', ax=axes[1, 1])
    axes[1, 1].set_title('總成本對比')
    axes[1, 1].set_ylabel('成本 ($)')
    axes[1, 1].set_xlabel('版本')

    plt.tight_layout()
    plt.savefig('ab_test_results.png')
    plt.show()

# 生成可視化
visualize_ab_test(df)
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def make_decision():
    """做出決策"""
    console.print("[cyan]5. 基於數據做決策[/cyan]\n")

    decision_process = """決策流程：

1. 檢查樣本量
   - 每個版本至少 100 個樣本
   - 樣本量越大，結論越可靠

2. 評估統計顯著性
   - p 值 < 0.05: 有顯著差異
   - p 值 >= 0.05: 無顯著差異

3. 考慮業務指標
   - 用戶評分
   - 任務完成率
   - 用戶留存

4. 權衡成本與質量
   - 質量提升是否值得成本增加
   - 長期 ROI 分析

5. 風險評估
   - 新版本的風險
   - 回滾計劃

決策示例：

if p_value < 0.05 and score_b > score_a:
    if cost_increase < 20%:  # 成本增加在可接受範圍
        decision = "採用版本 B"
    else:
        decision = "需要進一步優化版本 B"
else:
    decision = "保持版本 A"

實施計劃：
1. 逐步推廣（10% → 50% → 100%）
2. 持續監控關鍵指標
3. 準備回滾方案
4. 收集用戶反饋"""

    console.print(Panel(decision_process, border_style="cyan"))
    console.print()


def show_best_practices():
    """最佳實踐"""
    console.print("[cyan]A/B 測試最佳實踐[/cyan]\n")

    practices = """1. 測試設計
   - 每次只測試一個變量
   - 確保足夠的樣本量
   - 設定合理的測試時長
   - 考慮季節性因素

2. 流量分配
   - 50/50 分配（標準）
   - 90/10 分配（風險較大的變更）
   - 基於用戶 ID 保持一致性
   - 避免污染

3. 數據收集
   - 定義明確的成功指標
   - 收集多維度數據
   - 記錄用戶反饋
   - 追蹤邊界情況

4. 分析評估
   - 使用統計檢驗
   - 考慮實際業務影響
   - 平衡多個指標
   - 避免過早結論

5. 實施推廣
   - 灰度發布
   - 監控關鍵指標
   - 準備回滾
   - 文檔記錄

6. 持續優化
   - 定期進行 A/B 測試
   - 迭代改進
   - 積累最佳實踐
   - 分享學習"""

    console.print(Panel(practices, border_style="cyan"))
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]PromptLayer A/B 測試示例[/bold cyan]\n"
        "[dim]學習如何進行科學的 A/B 測試[/dim]",
        border_style="cyan"
    ))

    # 1. A/B 測試概念
    ab_test_concept()

    # 2. 設置測試
    setup_ab_test()

    # 3. 收集數據
    collect_test_data()

    # 4. 分析結果
    analyze_results()

    # 5. 可視化
    visualize_results()

    # 6. 決策
    make_decision()

    # 7. 最佳實踐
    show_best_practices()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ A/B 測試示例完成！[/bold green]\n")
    console.print("[cyan]下一步:[/cyan]")
    console.print("  1. 查看 06_評分系統.py - 學習評分機制")
    console.print("  2. 查看 07_成本分析.py - 分析成本")
    console.print("  3. 實踐: 為自己的模板進行 A/B 測試")


if __name__ == "__main__":
    main()
