"""
LangSmith 成本分析 - Cost Tracking

這個示例展示如何：
1. 追蹤 LLM API 成本
2. 分析 token 使用情況
3. 識別高成本操作
4. 優化成本
5. 設置預算告警
6. 成本歸因分析

成本控制是生產環境的關鍵考慮。
"""

import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.callbacks import get_openai_callback
from langsmith import Client
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress
import time

console = Console()


def setup_environment():
    """配置環境"""
    load_dotenv()
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    if not os.getenv("LANGCHAIN_PROJECT"):
        os.environ["LANGCHAIN_PROJECT"] = "cost-tracking-demo"
    console.print("[green]✓ 環境配置完成[/green]")


def track_basic_cost():
    """示例 1：基本成本追蹤"""
    console.print(Panel("[bold cyan]示例 1：基本成本追蹤[/bold cyan]"))

    try:
        # 使用 OpenAI callback 追蹤成本
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

        console.print("\n[cyan]執行單次調用...[/cyan]\n")

        with get_openai_callback() as cb:
            response = llm.invoke("用三句話介紹人工智慧")

            console.print(f"[green]回應：[/green]{response.content}\n")

            # 顯示成本信息
            table = Table(title="成本統計", show_header=True, header_style="bold magenta")
            table.add_column("指標", style="cyan", width=25)
            table.add_column("值", style="green", width=20)

            table.add_row("總 Tokens", str(cb.total_tokens))
            table.add_row("提示 Tokens", str(cb.prompt_tokens))
            table.add_row("完成 Tokens", str(cb.completion_tokens))
            table.add_row("總成本", f"${cb.total_cost:.6f}")

            console.print(table)

        console.print("\n[yellow]提示：LangSmith 會自動追蹤所有調用的成本[/yellow]")

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")


def track_batch_cost():
    """示例 2：批量操作成本追蹤"""
    console.print(Panel("[bold cyan]示例 2：批量操作成本[/bold cyan]"))

    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        prompt = ChatPromptTemplate.from_template("用一句話描述：{topic}")
        chain = prompt | llm | StrOutputParser()

        topics = [
            "機器學習",
            "深度學習",
            "自然語言處理",
            "計算機視覺",
            "強化學習"
        ]

        console.print(f"\n[cyan]處理 {len(topics)} 個主題...[/cyan]\n")

        with get_openai_callback() as cb:
            with Progress() as progress:
                task = progress.add_task("[cyan]處理中...", total=len(topics))

                for topic in topics:
                    result = chain.invoke({"topic": topic})
                    console.print(f"{topic}: {result}")
                    progress.update(task, advance=1)
                    time.sleep(0.1)  # 避免速率限制

            # 計算平均成本
            avg_cost = cb.total_cost / len(topics) if topics else 0

            console.print("\n[bold green]批量處理成本統計：[/bold green]\n")

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("指標", style="cyan")
            table.add_column("值", style="green")

            table.add_row("處理數量", str(len(topics)))
            table.add_row("總 Tokens", str(cb.total_tokens))
            table.add_row("總成本", f"${cb.total_cost:.6f}")
            table.add_row("平均成本", f"${avg_cost:.6f}")
            table.add_row("每 Token 成本", f"${cb.total_cost/cb.total_tokens:.8f}" if cb.total_tokens > 0 else "N/A")

            console.print(table)

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")


def compare_model_costs():
    """示例 3：比較不同模型的成本"""
    console.print(Panel("[bold cyan]示例 3：模型成本比較[/bold cyan]"))

    try:
        # 定義要比較的模型
        models = [
            {"name": "GPT-4o-mini", "model": "gpt-4o-mini"},
            {"name": "GPT-3.5-turbo", "model": "gpt-3.5-turbo"},
        ]

        prompt_text = "請詳細解釋量子計算的基本原理，包括量子比特、量子疊加和量子糾纏的概念。"

        results = []

        for model_config in models:
            console.print(f"\n[cyan]測試模型：{model_config['name']}[/cyan]")

            llm = ChatOpenAI(model=model_config["model"], temperature=0.7)

            with get_openai_callback() as cb:
                response = llm.invoke(prompt_text)

                results.append({
                    "model": model_config["name"],
                    "tokens": cb.total_tokens,
                    "cost": cb.total_cost,
                    "response_length": len(response.content)
                })

                console.print(f"Token 使用：{cb.total_tokens}")
                console.print(f"成本：${cb.total_cost:.6f}")

        # 創建比較表格
        console.print("\n[bold green]模型成本比較：[/bold green]\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("模型", style="cyan", width=20)
        table.add_column("Tokens", style="yellow", width=15)
        table.add_column("成本", style="green", width=15)
        table.add_column("回應長度", style="blue", width=15)
        table.add_column("成本效益", style="magenta", width=15)

        for result in results:
            cost_efficiency = result["response_length"] / result["cost"] if result["cost"] > 0 else 0

            table.add_row(
                result["model"],
                str(result["tokens"]),
                f"${result['cost']:.6f}",
                str(result["response_length"]),
                f"{cost_efficiency:.0f} 字/$"
            )

        console.print(table)

        # 找出最經濟的選擇
        cheapest = min(results, key=lambda x: x["cost"])
        console.print(f"\n[green]最經濟的模型：{cheapest['model']} (${cheapest['cost']:.6f})[/green]")

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")


def analyze_langsmith_costs():
    """示例 4：分析 LangSmith 中的成本數據"""
    console.print(Panel("[bold cyan]示例 4：LangSmith 成本分析[/bold cyan]"))

    guide = """
[bold green]在 LangSmith UI 中查看成本：[/bold green]

[cyan]1. 項目級別成本[/cyan]
   - 進入 Projects 頁面
   - 選擇特定項目
   - 查看 "Usage" 標籤
   - 顯示：
     * 總 token 使用
     * 預估成本
     * 時間趨勢圖
     * 模型分布

[cyan]2. Run 級別成本[/cyan]
   - 點擊任一 run
   - 查看詳情頁面
   - 成本信息包括：
     * 提示 tokens
     * 完成 tokens
     * 總成本
     * 模型信息

[cyan]3. 篩選高成本 Runs[/cyan]
   - 使用篩選器
   - 按成本排序
   - 識別異常高成本調用
   - 分析原因

[cyan]4. 導出成本數據[/cyan]
   - 導出 CSV
   - 自定義分析
   - 生成報告

[bold yellow]使用 SDK 查詢成本：[/bold yellow]

```python
from langsmith import Client
from datetime import datetime, timedelta

client = Client()

# 獲取最近的 runs
end_time = datetime.now()
start_time = end_time - timedelta(days=7)

runs = client.list_runs(
    project_name="your-project",
    start_time=start_time,
    end_time=end_time
)

# 計算總成本
total_cost = 0
total_tokens = 0

for run in runs:
    # 如果 run 包含成本信息
    if hasattr(run, 'total_tokens'):
        total_tokens += run.total_tokens or 0

    # 成本信息可能在 extra 字段中
    # 具體結構取決於 LangSmith 版本

print(f"7 天總 Tokens: {total_tokens}")
print(f"預估成本: ${total_cost:.2f}")
```

[cyan]5. 按標籤分析成本[/cyan]
   - 為不同功能添加標籤
   - 按標籤分組查看成本
   - 識別高成本功能
   - 優化優先級
    """

    console.print(guide)


def cost_optimization_strategies():
    """示例 5：成本優化策略"""
    console.print(Panel("[bold cyan]示例 5：成本優化策略[/bold cyan]"))

    strategies = """
[bold green]成本優化策略：[/bold green]

[cyan]1. 選擇合適的模型[/cyan]
   ✓ 簡單任務使用較小的模型
   ✓ GPT-4o-mini vs GPT-4（成本差 10-30 倍）
   ✓ 評估質量 vs 成本權衡
   ✗ 所有任務都用最大模型

   示例：
   - 分類/提取 → GPT-4o-mini
   - 創意寫作 → GPT-4
   - 簡單問答 → GPT-3.5-turbo

[cyan]2. 優化提示詞長度[/cyan]
   ✓ 簡潔明確的指令
   ✓ 避免重複信息
   ✓ 使用示例但不過多
   ✗ 冗長的提示詞

   優化前：
   ```
   你是一個非常專業的助手，擁有豐富的經驗...（200 字）
   請幫我...
   ```

   優化後：
   ```
   作為專家，請簡潔回答：{question}
   ```

[cyan]3. 控制輸出長度[/cyan]
   ✓ 使用 max_tokens 限制
   ✓ 在提示詞中指定長度
   ✓ "用一句話回答" vs "詳細解釋"
   ✗ 不限制輸出

   ```python
   llm = ChatOpenAI(
       model="gpt-4o-mini",
       max_tokens=100  # 限制輸出長度
   )
   ```

[cyan]4. 使用緩存[/cyan]
   ✓ 緩存常見查詢
   ✓ 避免重複調用
   ✓ 使用 Redis/數據庫
   ✗ 每次都調用 API

   ```python
   import hashlib
   from functools import lru_cache

   @lru_cache(maxsize=1000)
   def get_response(prompt_hash):
       return llm.invoke(prompt)

   # 使用時
   prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
   response = get_response(prompt_hash)
   ```

[cyan]5. 批量處理[/cyan]
   ✓ 合並多個小請求
   ✓ 使用批量 API
   ✓ 減少往返次數
   ✗ 逐個處理

[cyan]6. 採樣和漸進式處理[/cyan]
   ✓ 開發時使用小樣本
   ✓ 先處理部分數據驗證
   ✓ 確認後再全量處理
   ✗ 直接全量處理

[cyan]7. 設置預算限制[/cyan]
   ✓ 監控每日/每月支出
   ✓ 設置告警閾值
   ✓ 超預算時降級服務
   ✗ 不設預算控制

[cyan]8. 錯誤處理和重試[/cyan]
   ✓ 智能重試策略
   ✓ 避免無意義的重試
   ✓ 記錄失敗原因
   ✗ 無限重試

[cyan]9. 使用流式輸出[/cyan]
   ✓ 改善用戶體驗
   ✓ 提前終止不需要的輸出
   ✓ 降低感知延遲
   但不會降低成本（token 相同）

[cyan]10. 定期審查[/cyan]
   ✓ 每週查看成本報告
   ✓ 識別異常高成本
   ✓ 分析成本趨勢
   ✓ 持續優化
    """

    console.print(strategies)


def cost_monitoring_setup():
    """示例 6：設置成本監控"""
    console.print(Panel("[bold cyan]示例 6：成本監控設置[/bold cyan]"))

    example_code = '''
import os
from datetime import datetime
from langsmith import Client
from langchain.callbacks import get_openai_callback

class CostMonitor:
    """成本監控類"""

    def __init__(self, daily_limit=10.0):
        self.daily_limit = daily_limit
        self.daily_cost = 0.0
        self.client = Client()
        self.reset_date = datetime.now().date()

    def check_and_update(self, cost):
        """檢查並更新成本"""
        # 檢查是否需要重置
        today = datetime.now().date()
        if today != self.reset_date:
            self.daily_cost = 0.0
            self.reset_date = today

        # 更新成本
        self.daily_cost += cost

        # 檢查是否超限
        if self.daily_cost >= self.daily_limit:
            raise Exception(f"超出每日成本限制：${self.daily_limit}")

        # 警告
        if self.daily_cost >= self.daily_limit * 0.8:
            print(f"⚠️  警告：已使用 {self.daily_cost/self.daily_limit*100:.0f}% 的每日預算")

        return True

    def get_stats(self):
        """獲取統計信息"""
        remaining = self.daily_limit - self.daily_cost
        percentage = (self.daily_cost / self.daily_limit) * 100

        return {
            "daily_limit": self.daily_limit,
            "daily_cost": self.daily_cost,
            "remaining": remaining,
            "percentage": percentage
        }


# 使用示例
monitor = CostMonitor(daily_limit=10.0)

llm = ChatOpenAI(model="gpt-4o-mini")

try:
    with get_openai_callback() as cb:
        response = llm.invoke("你好")

        # 更新監控
        monitor.check_and_update(cb.total_cost)

        stats = monitor.get_stats()
        print(f"今日已用：${stats['daily_cost']:.4f}")
        print(f"剩餘預算：${stats['remaining']:.4f}")
        print(f"使用比例：{stats['percentage']:.1f}%")

except Exception as e:
    print(f"錯誤：{e}")
    # 降級處理或停止服務
    '''

    from rich.syntax import Syntax
    syntax = Syntax(example_code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)


def pricing_reference():
    """定價參考"""
    console.print(Panel("[bold cyan]LLM 定價參考（僅供參考，請查看官網最新價格）[/bold cyan]"))

    # 創建定價表格
    table = Table(title="OpenAI 定價（2024 年參考）", show_header=True, header_style="bold magenta")
    table.add_column("模型", style="cyan", width=20)
    table.add_column("輸入價格", style="green", width=20)
    table.add_column("輸出價格", style="yellow", width=20)
    table.add_column("上下文長度", style="blue", width=15)

    pricing = [
        ("GPT-4", "$30 / 1M tokens", "$60 / 1M tokens", "8K"),
        ("GPT-4 Turbo", "$10 / 1M tokens", "$30 / 1M tokens", "128K"),
        ("GPT-4o", "$5 / 1M tokens", "$15 / 1M tokens", "128K"),
        ("GPT-4o-mini", "$0.15 / 1M tokens", "$0.6 / 1M tokens", "128K"),
        ("GPT-3.5-turbo", "$0.5 / 1M tokens", "$1.5 / 1M tokens", "16K"),
    ]

    for model, input_price, output_price, context in pricing:
        table.add_row(model, input_price, output_price, context)

    console.print(table)

    calculations = """
[bold yellow]成本計算示例：[/bold yellow]

假設使用 GPT-4o-mini：
- 輸入：$0.15 / 1M tokens
- 輸出：$0.6 / 1M tokens

[cyan]場景 1：簡單問答[/cyan]
- 輸入：50 tokens
- 輸出：100 tokens
- 成本：(50 * 0.15 + 100 * 0.6) / 1,000,000 = $0.0000675

[cyan]場景 2：文檔總結[/cyan]
- 輸入：2000 tokens（長文檔）
- 輸出：200 tokens（總結）
- 成本：(2000 * 0.15 + 200 * 0.6) / 1,000,000 = $0.00042

[cyan]場景 3：每月 10 萬次簡單查詢[/cyan]
- 每次：50 輸入 + 100 輸出 tokens
- 總計：150 tokens * 100,000 = 15M tokens
- 月成本：約 $6.75

[bold green]省錢技巧：[/bold green]
✓ GPT-4o-mini 比 GPT-4 便宜 200+ 倍
✓ 優化提示詞可減少 30-50% token
✓ 緩存可減少 50-80% 重複調用
✓ 批量處理可提高效率
    """

    console.print(Panel(calculations, border_style="green"))


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]LangSmith 成本分析[/bold green]",
        border_style="green"
    ))

    # 設置環境
    setup_environment()

    console.print("\n" + "="*60 + "\n")

    # 運行示例
    track_basic_cost()
    console.print("\n" + "="*60 + "\n")

    track_batch_cost()
    console.print("\n" + "="*60 + "\n")

    compare_model_costs()
    console.print("\n" + "="*60 + "\n")

    analyze_langsmith_costs()
    console.print("\n" + "="*60 + "\n")

    cost_optimization_strategies()
    console.print("\n" + "="*60 + "\n")

    cost_monitoring_setup()
    console.print("\n" + "="*60 + "\n")

    pricing_reference()

    # 總結
    console.print(Panel("""
[bold green]成本分析總結[/bold green]

追蹤方法：
1. OpenAI Callback（本地追蹤）
2. LangSmith UI（全局追蹤）
3. 自定義監控系統

關鍵指標：
- Token 使用量
- API 調用成本
- 平均每次成本
- 成本趨勢

優化策略：
✓ 選擇合適的模型
✓ 優化提示詞長度
✓ 限制輸出長度
✓ 使用緩存
✓ 批量處理
✓ 設置預算限制

監控建議：
✓ 每日檢查成本
✓ 設置告警閾值
✓ 分析高成本操作
✓ 定期優化

成本控制目標：
- 開發環境：< $10/天
- 測試環境：< $50/天
- 生產環境：根據業務設定

下一步：
- 查看 10_生產監控.py 學習生產環境監控
- 在 LangSmith UI 中分析成本趨勢
- 設置預算告警
- 持續優化成本

重要提示：
- 成本優化是持續過程
- 平衡質量和成本
- 監控異常高成本調用
- 定期審查和調整策略
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()
