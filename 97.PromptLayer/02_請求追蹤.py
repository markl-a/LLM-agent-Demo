"""
PromptLayer 請求追蹤示例

本示例展示：
1. 追蹤不同類型的請求
2. 添加元數據和標籤
3. 查詢請求歷史
4. 請求分析
"""

import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

load_dotenv()
console = Console()


def track_basic_request():
    """追蹤基本請求"""
    console.print("\n[cyan]1. 基本請求追蹤[/cyan]\n")

    code = """import promptlayer

promptlayer.api_key = os.getenv("PROMPTLAYER_API_KEY")
OpenAI = promptlayer.openai.OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 基本追蹤
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "你好"}
    ],
    return_pl_id=True  # 返回 PromptLayer 請求 ID
)

print(f"響應: {response.choices[0].message.content}")
print(f"請求 ID: {response.pl_request_id}")

# 請求自動記錄到 PromptLayer
# 包含: 提示、響應、token 使用、延遲等
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def track_with_tags():
    """使用標籤追蹤"""
    console.print("[cyan]2. 使用標籤追蹤請求[/cyan]\n")

    code = """# 添加標籤便於分類和搜索
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "解釋量子計算"}
    ],
    # 添加多個標籤
    pl_tags=[
        "production",      # 環境
        "technical",       # 類別
        "v2.0",           # 版本
        "customer-123"    # 用戶
    ],
    return_pl_id=True
)

# 在 Web 界面可以按標籤過濾請求
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def track_with_metadata():
    """使用元數據追蹤"""
    console.print("[cyan]3. 添加元數據[/cyan]\n")

    code = """# 添加自定義元數據
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "你是客服助手"},
        {"role": "user", "content": "如何退款？"}
    ],
    # 自定義元數據
    metadata={
        "user_id": "user_12345",
        "session_id": "session_abc",
        "feature": "customer_service",
        "priority": "high",
        "region": "asia-pacific",
        "version": "2.1.0"
    },
    pl_tags=["customer-service", "production"],
    return_pl_id=True
)

# 元數據可用於:
# - 追蹤用戶行為
# - 性能分析
# - 成本歸因
# - 問題排查
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def track_different_models():
    """追蹤不同模型"""
    console.print("[cyan]4. 追蹤不同的 LLM 模型[/cyan]\n")

    code = """# GPT-4
gpt4_response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "寫一首詩"}],
    pl_tags=["gpt-4", "creative"],
    return_pl_id=True
)

# GPT-3.5-Turbo
gpt35_response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "寫一首詩"}],
    pl_tags=["gpt-3.5", "creative"],
    return_pl_id=True
)

# Embeddings
embeddings_response = client.embeddings.create(
    model="text-embedding-ada-002",
    input="機器學習",
    pl_tags=["embeddings", "search"],
    return_pl_id=True
)

# 在 PromptLayer 可以對比不同模型的:
# - 性能
# - 成本
# - 質量
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def track_streaming():
    """追蹤流式響應"""
    console.print("[cyan]5. 追蹤流式響應[/cyan]\n")

    code = """# 流式響應也會被追蹤
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "講一個故事"}
    ],
    stream=True,
    pl_tags=["streaming", "story"],
    return_pl_id=True
)

# 收集流式響應
full_response = ""
for chunk in stream:
    if chunk.choices[0].delta.content:
        content = chunk.choices[0].delta.content
        print(content, end="")
        full_response += content

print(f"\\n\\n請求 ID: {stream.pl_request_id}")

# 完整的流式響應會被記錄
# 包括總延遲和 token 使用
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def query_requests():
    """查詢請求歷史"""
    console.print("[cyan]6. 查詢請求歷史[/cyan]\n")

    code = """import promptlayer

# 使用 REST API 查詢請求
# (需要額外的 requests 庫)
import requests

def get_recent_requests(limit=10):
    \"\"\"獲取最近的請求\"\"\"
    url = "https://api.promptlayer.com/rest/get-requests"

    params = {
        "api_key": os.getenv("PROMPTLAYER_API_KEY"),
        "limit": limit
    }

    response = requests.get(url, params=params)
    return response.json()


def get_request_by_id(request_id):
    \"\"\"根據 ID 獲取請求詳情\"\"\"
    url = f"https://api.promptlayer.com/rest/get-request/{request_id}"

    params = {
        "api_key": os.getenv("PROMPTLAYER_API_KEY")
    }

    response = requests.get(url, params=params)
    return response.json()


def search_requests(tags=None, start_date=None, end_date=None):
    \"\"\"搜索請求\"\"\"
    url = "https://api.promptlayer.com/rest/search-requests"

    params = {
        "api_key": os.getenv("PROMPTLAYER_API_KEY"),
        "tags": tags,
        "start_date": start_date,
        "end_date": end_date
    }

    response = requests.post(url, json=params)
    return response.json()


# 使用示例
recent = get_recent_requests(limit=5)
for req in recent:
    print(f"ID: {req['id']}, Model: {req['model']}, Tokens: {req['tokens']}")
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def analyze_requests():
    """分析請求"""
    console.print("[cyan]7. 請求分析示例[/cyan]\n")

    code = """import pandas as pd
from datetime import datetime, timedelta

def analyze_request_patterns():
    \"\"\"分析請求模式\"\"\"

    # 獲取過去 7 天的請求
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    requests_data = search_requests(
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )

    # 轉換為 DataFrame
    df = pd.DataFrame(requests_data)

    # 分析統計
    print("=== 請求統計 ===")
    print(f"總請求數: {len(df)}")
    print(f"\\n按模型分組:")
    print(df.groupby('model').size())

    print(f"\\n總 Token 使用:")
    print(f"輸入: {df['prompt_tokens'].sum()}")
    print(f"輸出: {df['completion_tokens'].sum()}")
    print(f"總計: {df['total_tokens'].sum()}")

    print(f"\\n平均延遲: {df['latency'].mean():.2f}秒")

    print(f"\\n按標籤分組:")
    # 展開標籤並計數
    all_tags = []
    for tags in df['tags']:
        all_tags.extend(tags)
    tag_counts = pd.Series(all_tags).value_counts()
    print(tag_counts)

    return df


# 執行分析
df = analyze_request_patterns()

# 可視化（需要 matplotlib）
import matplotlib.pyplot as plt

# Token 使用趨勢
df['date'] = pd.to_datetime(df['timestamp']).dt.date
daily_tokens = df.groupby('date')['total_tokens'].sum()
daily_tokens.plot(kind='line', title='每日 Token 使用量')
plt.show()
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_best_practices():
    """最佳實踐"""
    console.print("[cyan]請求追蹤最佳實踐[/cyan]\n")

    practices = """1. 標籤策略
   - 使用一致的命名規範
   - 包含環境標籤（dev/staging/prod）
   - 添加版本標籤便於追蹤
   - 使用功能標籤分類

2. 元數據管理
   - 包含用戶 ID 追蹤用戶行為
   - 添加會話 ID 追蹤對話
   - 記錄功能模塊便於分析
   - 包含版本信息便於調試

3. 請求組織
   - 定期審查請求日誌
   - 清理舊的測試請求
   - 為重要請求添加註釋
   - 建立命名規範

4. 性能監控
   - 監控平均延遲
   - 追蹤 token 使用趨勢
   - 識別異常請求
   - 設置告警閾值

5. 成本控制
   - 定期檢查成本報告
   - 識別高成本請求
   - 優化頻繁調用
   - 設置預算限制"""

    console.print(Panel(practices, border_style="cyan"))
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]PromptLayer 請求追蹤示例[/bold cyan]\n"
        "[dim]學習如何追蹤和分析 LLM 請求[/dim]",
        border_style="cyan"
    ))

    # 1. 基本追蹤
    track_basic_request()

    # 2. 標籤追蹤
    track_with_tags()

    # 3. 元數據
    track_with_metadata()

    # 4. 不同模型
    track_different_models()

    # 5. 流式響應
    track_streaming()

    # 6. 查詢請求
    query_requests()

    # 7. 分析請求
    analyze_requests()

    # 8. 最佳實踐
    show_best_practices()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 請求追蹤示例完成！[/bold green]\n")
    console.print("[cyan]下一步:[/cyan]")
    console.print("  1. 查看 03_提示模板.py - 學習模板管理")
    console.print("  2. 查看 06_評分系統.py - 學習請求評分")
    console.print("  3. 實踐: 在項目中添加標籤和元數據")


if __name__ == "__main__":
    main()
