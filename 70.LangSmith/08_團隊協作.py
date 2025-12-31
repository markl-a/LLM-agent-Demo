"""
LangSmith 團隊協作 - Team Collaboration

這個示例展示如何：
1. 設置團隊工作區
2. 管理成員和權限
3. 共享項目和數據集
4. 協作調試和評估
5. 建立團隊工作流
6. 最佳協作實踐

團隊協作功能讓多人高效協同工作。
"""

import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from langsmith import Client
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

console = Console()


def setup_environment():
    """配置環境"""
    load_dotenv()
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    if not os.getenv("LANGCHAIN_PROJECT"):
        os.environ["LANGCHAIN_PROJECT"] = "team-collaboration-demo"
    console.print("[green]✓ 環境配置完成[/green]")


def workspace_management():
    """示例 1：工作區管理"""
    console.print(Panel("[bold cyan]示例 1：工作區管理[/bold cyan]"))

    guide = """
[bold green]LangSmith 工作區概念：[/bold green]

[cyan]1. 個人工作區[/cyan]
   - 每個用戶有默認的個人工作區
   - 完全私有
   - 適合個人實驗和開發

[cyan]2. 團隊工作區[/cyan]
   - 支持多人協作
   - 共享資源（項目、數據集、提示詞）
   - 細粒度權限控制
   - 適合團隊開發和生產環境

[bold yellow]創建團隊工作區（在 UI 中）：[/bold yellow]

1. 登入 LangSmith (https://smith.langchain.com/)
2. 點擊右上角的工作區選擇器
3. 選擇 "Create Organization"
4. 填寫組織信息：
   - 組織名稱
   - 組織 ID（URL 標識符）
   - 計費信息（如需付費功能）
5. 點擊創建

[bold yellow]切換工作區：[/bold yellow]

```python
from langsmith import Client

# 默認使用個人工作區
client = Client()

# 使用特定組織工作區
# 設置環境變量或在代碼中指定
os.environ["LANGCHAIN_ORG_ID"] = "your-org-id"
client = Client()

# 或在初始化時指定
client = Client(
    api_key=os.getenv("LANGCHAIN_API_KEY"),
    api_url="https://api.smith.langchain.com",
    # 如果 SDK 支持組織 ID
)
```

[cyan]3. 工作區資源[/cyan]
   - 項目（Projects）
   - 數據集（Datasets）
   - 提示詞（Prompts）
   - 評估結果（Experiments）
   - 追蹤數據（Runs）
    """

    console.print(guide)


def member_management():
    """示例 2：成員和權限管理"""
    console.print(Panel("[bold cyan]示例 2：成員和權限管理[/bold cyan]"))

    # 創建權限表格
    table = Table(title="LangSmith 權限級別", show_header=True, header_style="bold magenta")
    table.add_column("角色", style="cyan", width=15)
    table.add_column("權限", style="white", width=50)
    table.add_column("適用場景", style="green", width=30)

    roles = [
        (
            "Owner",
            "完全控制：管理成員、計費、刪除組織",
            "創建者、管理員"
        ),
        (
            "Admin",
            "管理成員、項目、數據集，無法管理計費",
            "技術主管、團隊負責人"
        ),
        (
            "Member",
            "創建和管理自己的資源，查看團隊資源",
            "開發人員"
        ),
        (
            "Viewer",
            "只讀訪問，可查看追蹤和評估結果",
            "產品經理、QA"
        )
    ]

    for role, permissions, use_case in roles:
        table.add_row(role, permissions, use_case)

    console.print(table)

    management_guide = """
[bold yellow]在 UI 中管理成員：[/bold yellow]

1. 進入組織設置
2. 選擇 "Members" 標籤
3. 點擊 "Invite Member"
4. 輸入郵箱地址
5. 選擇角色
6. 發送邀請

[bold yellow]邀請流程：[/bold yellow]

發送邀請 → 成員收到郵件 → 接受邀請 → 加入組織

[bold yellow]權限最佳實踐：[/bold yellow]

✓ 遵循最小權限原則
✓ 定期審查成員列表
✓ 為不同環境設置不同權限
✓ 使用 Viewer 角色給非技術人員
✗ 給所有人 Admin 權限
✗ 不移除離職成員
    """

    console.print(Panel(management_guide, border_style="blue"))


def project_sharing():
    """示例 3：共享項目和資源"""
    console.print(Panel("[bold cyan]示例 3：共享項目和資源[/bold cyan]"))

    example_code = '''
from langsmith import Client

client = Client()

# 1. 在團隊工作區中創建共享項目
# 項目會自動對團隊成員可見

# 設置項目名稱包含團隊/功能信息
shared_project = "team-chatbot-dev"
os.environ["LANGCHAIN_PROJECT"] = shared_project

# 團隊成員可以看到這個項目的所有追蹤

# 2. 創建共享數據集
dataset = client.create_dataset(
    dataset_name="team-qa-dataset",
    description="團隊共享的問答測試集"
)

# 添加示例
client.create_example(
    dataset_id=dataset.id,
    inputs={"question": "測試問題"},
    outputs={"answer": "測試答案"}
)

# 團隊成員都可以使用這個數據集進行評估

# 3. 從 Hub 拉取團隊提示詞
from langchain import hub

# 假設團隊已經推送了提示詞
team_prompt = hub.pull("team-org/standard-qa-prompt")

# 4. 運行評估並共享結果
from langsmith import evaluate

results = evaluate(
    predict_function,
    data="team-qa-dataset",
    experiment_prefix="alice-experiment",  # 個人實驗標識
    description="Alice 的優化嘗試"
)

# 團隊成員可以在 Experiments 頁面看到並比較所有人的實驗
    '''

    syntax = Syntax(example_code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)

    sharing_guide = """
[bold green]資源共享最佳實踐：[/bold green]

[cyan]1. 項目命名規範[/cyan]
   - team-{功能}-{環境}
   - 例如：team-chatbot-dev, team-chatbot-prod
   - 清晰表明用途和環境

[cyan]2. 數據集組織[/cyan]
   - 團隊共享數據集：team-*
   - 個人實驗數據集：{name}-*
   - 明確數據集用途和所有者

[cyan]3. 實驗命名[/cyan]
   - {姓名}-{目的}-{日期}
   - 例如：alice-prompt-opt-20240115
   - 方便識別和追蹤

[cyan]4. 提示詞管理[/cyan]
   - 組織級提示詞：org-name/*
   - 團隊提示詞：team-name/*
   - 個人提示詞：user-name/*

[cyan]5. 文檔化[/cyan]
   ✓ 為項目添加清晰描述
   ✓ 記錄數據集來源和用途
   ✓ 實驗結果添加註釋
   ✓ 維護團隊 Wiki
    """

    console.print(Panel(sharing_guide, border_style="green"))


def collaborative_debugging():
    """示例 4：協作調試"""
    console.print(Panel("[bold cyan]示例 4：協作調試[/bold cyan]"))

    workflow = """
[bold green]協作調試工作流：[/bold green]

[cyan]場景：團隊成員發現問題[/cyan]

1. [yellow]發現問題[/yellow]
   Alice 在生產環境發現一個失敗的 run

2. [yellow]標記和分享[/yellow]
   - 在 LangSmith UI 中找到該 run
   - 添加標籤：bug, needs-review
   - 添加註釋說明問題
   - 複製 run URL 分享給團隊

3. [yellow]團隊分析[/yellow]
   Bob 查看該 run：
   - 檢查輸入輸出
   - 查看完整追蹤鏈
   - 分析錯誤堆棧
   - 查看相關的其他 runs

4. [yellow]重現問題[/yellow]
   - 從該 run 創建測試案例
   - 添加到數據集
   - 本地重現和調試

5. [yellow]修復驗證[/yellow]
   - 修改代碼/提示詞
   - 對測試數據集運行評估
   - 確認問題已修復

6. [yellow]更新和關閉[/yellow]
   - 在原 run 添加註釋說明已修復
   - 更新相關文檔
   - 移除 needs-review 標籤

[bold yellow]使用 SDK 進行協作：[/bold yellow]

```python
from langsmith import Client

client = Client()

# 查詢帶特定標籤的 runs
runs = client.list_runs(
    project_name="team-chatbot-prod",
    filter='tags("bug")'  # 查找標記為 bug 的 runs
)

for run in runs:
    print(f"Run ID: {run.id}")
    print(f"Tags: {run.tags}")
    print(f"Status: {run.status}")
    print("---")

# 從問題 run 創建測試案例
problem_run_id = "run-id-with-issue"

client.create_example_from_run(
    run_id=problem_run_id,
    dataset_id="bug-reproduction-dataset"
)

# 添加註釋（在 UI 中操作更方便）
# SDK 可能需要特定方法
```

[bold green]UI 功能：[/bold green]

- ✓ Run 詳情頁面查看完整信息
- ✓ 添加註釋和標籤
- ✓ 分享 run URL
- ✓ 比較多個 runs
- ✓ 從 run 創建數據集示例
    """

    console.print(workflow)


def team_workflow():
    """示例 5：團隊工作流建議"""
    console.print(Panel("[bold cyan]示例 5：團隊工作流[/bold cyan]"))

    workflow = """
[bold green]推薦的團隊開發流程：[/bold green]

[cyan]階段 1：規劃[/cyan]
1. 創建團隊項目
2. 定義評估指標
3. 準備基準數據集
4. 建立命名規範

[cyan]階段 2：開發[/cyan]
每個成員：
1. 在個人分支開發
2. 使用 {name}-{feature} 項目名
3. 頻繁追蹤和評估
4. 記錄實驗結果

[cyan]階段 3：評審[/cyan]
1. 在團隊會議上分享結果
2. 在 LangSmith UI 中並排比較實驗
3. 討論不同方法的優劣
4. 選擇最佳方案

[cyan]階段 4：集成[/cyan]
1. 將最佳方案合併到主分支
2. 在團隊數據集上驗證
3. 更新團隊提示詞
4. 記錄到文檔

[cyan]階段 5：部署[/cyan]
1. 在 staging 環境測試
2. 使用 team-{app}-staging 項目
3. 監控關鍵指標
4. 團隊確認後部署到生產

[cyan]階段 6：監控[/cyan]
1. 使用 team-{app}-prod 項目
2. 設置告警
3. 定期審查
4. 收集失敗案例

[cyan]階段 7：迭代[/cyan]
1. 從生產問題創建新測試
2. 添加到數據集
3. 開始新一輪優化

[bold yellow]會議和溝通：[/bold yellow]

[green]每日站會：[/green]
- 分享昨天的實驗結果
- 討論遇到的問題
- 計劃今天的工作

[green]每週評審：[/green]
- 在 LangSmith 中回顧所有實驗
- 分析性能趨勢
- 決定下週重點

[green]月度回顧：[/green]
- 評估整體性能
- 更新基準數據集
- 優化工作流程
    """

    console.print(workflow)


def collaboration_best_practices():
    """協作最佳實踐"""
    console.print(Panel("[bold cyan]協作最佳實踐[/bold cyan]"))

    practices = """
[bold green]團隊協作最佳實踐：[/bold green]

1. [cyan]命名規範[/cyan]
   ✓ 統一的命名模式
   ✓ 包含上下文信息
   ✓ 易於搜索和過濾
   ✗ 隨意命名

2. [cyan]文檔化[/cyan]
   ✓ 為項目添加描述
   ✓ 記錄實驗假設
   ✓ 說明數據集用途
   ✓ 維護團隊知識庫
   ✗ 沒有文檔

3. [cyan]代碼審查[/cyan]
   ✓ 重要變更需要審查
   ✓ 共享評估結果
   ✓ 討論決策依據
   ✗ 各自為政

4. [cyan]數據管理[/cyan]
   ✓ 區分個人/團隊數據集
   ✓ 定期清理過期數據
   ✓ 數據集版本控制
   ✗ 數據混亂

5. [cyan]權限管理[/cyan]
   ✓ 最小權限原則
   ✓ 定期審查權限
   ✓ 區分開發/生產環境
   ✗ 權限過大

6. [cyan]溝通協作[/cyan]
   ✓ 及時分享發現
   ✓ 使用標籤和註釋
   ✓ 定期團隊會議
   ✗ 信息孤島

7. [cyan]質量控制[/cyan]
   ✓ 使用標準評估流程
   ✓ 所有變更都要評估
   ✓ 追蹤性能趨勢
   ✗ 沒有質量標準

8. [cyan]知識共享[/cyan]
   ✓ 分享最佳提示詞
   ✓ 記錄失敗教訓
   ✓ 培訓新成員
   ✗ 知識不流通

[bold yellow]避免的陷阱：[/bold yellow]

✗ 所有人都是 Admin
✗ 沒有命名規範
✗ 不寫描述和註釋
✗ 刪除他人的資源
✗ 不分享實驗結果
✗ 生產和開發混用
✗ 不審查就部署
✗ 忽視成本控制
    """

    console.print(practices)


def team_tools_and_features():
    """團隊工具和功能"""
    console.print(Panel("[bold cyan]團隊工具和功能[/bold cyan]"))

    # 創建功能表格
    table = Table(title="LangSmith 團隊功能", show_header=True, header_style="bold magenta")
    table.add_column("功能", style="cyan", width=25)
    table.add_column("說明", style="white", width=40)
    table.add_column("用途", style="green", width=30)

    features = [
        (
            "共享工作區",
            "團隊成員共享項目和資源",
            "協作開發"
        ),
        (
            "權限管理",
            "細粒度的角色和權限控制",
            "安全和合規"
        ),
        (
            "實驗比較",
            "並排比較多個實驗結果",
            "A/B 測試、方案選擇"
        ),
        (
            "註釋和標籤",
            "為 runs 添加註釋和標籤",
            "問題追蹤、知識分享"
        ),
        (
            "Prompt Hub",
            "共享和版本控制提示詞",
            "提示詞管理"
        ),
        (
            "共享數據集",
            "團隊共享測試數據集",
            "統一評估標準"
        ),
        (
            "活動日誌",
            "查看團隊成員活動",
            "審計和監控"
        ),
        (
            "通知",
            "重要事件通知（如果支持）",
            "及時響應問題"
        )
    ]

    for feature, desc, use_case in features:
        table.add_row(feature, desc, use_case)

    console.print(table)

    integration = """
[bold yellow]與其他工具集成：[/bold yellow]

[cyan]1. Git[/cyan]
   - 在 commit 中引用 experiment ID
   - 關聯代碼變更和性能變化

[cyan]2. CI/CD[/cyan]
   - 在 CI 中運行評估
   - 性能下降則失敗
   - 自動化測試流程

[cyan]3. 溝通工具[/cyan]
   - Slack：分享 run URLs
   - 通知重要事件
   - 討論結果

[cyan]4. 項目管理[/cyan]
   - Jira/Linear：關聯問題
   - 追蹤優化任務
   - 記錄決策

示例 CI 集成：

```yaml
# .github/workflows/evaluate.yml
name: LangSmith Evaluation

on: [pull_request]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run evaluation
        env:
          LANGCHAIN_API_KEY: ${{ secrets.LANGCHAIN_API_KEY }}
          LANGCHAIN_PROJECT: ci-evaluation
        run: python evaluate.py

      - name: Check results
        run: python check_results.py
```
    """

    console.print(Panel(integration, border_style="blue"))


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]LangSmith 團隊協作[/bold green]",
        border_style="green"
    ))

    # 設置環境
    setup_environment()

    console.print("\n" + "="*60 + "\n")

    # 展示內容
    workspace_management()
    console.print("\n" + "="*60 + "\n")

    member_management()
    console.print("\n" + "="*60 + "\n")

    project_sharing()
    console.print("\n" + "="*60 + "\n")

    collaborative_debugging()
    console.print("\n" + "="*60 + "\n")

    team_workflow()
    console.print("\n" + "="*60 + "\n")

    collaboration_best_practices()
    console.print("\n" + "="*60 + "\n")

    team_tools_and_features()

    # 總結
    console.print(Panel("""
[bold green]團隊協作總結[/bold green]

核心概念：
1. 工作區：個人 vs 團隊
2. 權限：Owner > Admin > Member > Viewer
3. 共享：項目、數據集、提示詞、實驗
4. 協作：調試、評審、決策

團隊工作流：
規劃 → 開發 → 評審 → 集成 → 部署 → 監控 → 迭代

關鍵工具：
✓ 共享工作區
✓ 權限管理
✓ 實驗比較
✓ 註釋標籤
✓ Prompt Hub
✓ 活動日誌

最佳實踐：
✓ 統一命名規範
✓ 充分文檔化
✓ 定期代碼審查
✓ 知識共享
✓ 權限最小化
✓ 質量控制
✓ 持續溝通

下一步：
- 創建團隊工作區
- 邀請團隊成員
- 建立工作流程
- 制定團隊規範
- 查看 09_成本分析.py 了解成本管理
- 查看 10_生產監控.py 學習監控

提示：
- LangSmith 團隊功能需要付費計劃
- 建議先試用個人版熟悉功能
- 制定清晰的團隊規範很重要
- 定期審查和優化工作流程
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()
