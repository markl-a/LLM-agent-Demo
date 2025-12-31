# SWE-Agent - 軟體工程 AI Agent 框架

## 框架簡介

SWE-Agent 是由 Princeton NLP 開發的軟體工程 AI Agent 框架，專門用於自動解決 GitHub Issues 和執行程式碼修復任務。該框架在 SWE-bench 基準測試中達到了業界領先的效果，能夠自主分析問題、搜索相關程式碼、生成修復補丁並驗證修復效果。

SWE-Agent 結合了大型語言模型（LLM）的理解能力與專門設計的工具集，使 AI Agent 能夠像人類軟體工程師一樣工作：閱讀程式碼、理解需求、定位問題、提出解決方案並進行測試驗證。

### 核心特點

- **自動 Issue 解決**: 直接從 GitHub Issue 描述自動生成完整的修復方案
- **智能程式碼搜索**: 高效的程式碼導航和相關檔案定位能力
- **補丁生成與應用**: 自動生成修復補丁並應用到程式碼庫
- **測試驅動修復**: 整合測試框架，確保修復不破壞現有功能
- **多語言支援**: 支援 Python、JavaScript、Java、Go 等多種程式語言
- **沙箱執行環境**: Docker 容器隔離，保證安全執行
- **SWE-bench 評測**: 內建評測工具，追蹤性能指標
- **可擴展架構**: 支援自定義工具和命令擴展

### 技術架構

```
SWE-Agent 架構
├── Agent 控制器 (Agent Controller)
│   ├── LLM 整合 (OpenAI/Anthropic)
│   ├── 決策引擎 (Decision Engine)
│   └── 記憶管理 (Memory Manager)
├── 工具系統 (Tool System)
│   ├── 檔案操作工具
│   ├── 程式碼搜索工具
│   ├── Git 操作工具
│   └── 測試執行工具
├── 執行環境 (Execution Environment)
│   ├── Docker 容器管理
│   ├── 環境配置
│   └── 依賴安裝
└── 評估系統 (Evaluation System)
    ├── SWE-bench 測試集
    ├── 指標計算
    └── 結果報告
```

## 主要功能

### 1. GitHub Issue 解決

SWE-Agent 能夠自動從 GitHub Issue 中提取問題描述，分析問題類型，定位相關程式碼，並生成修復方案：

- 自動拉取 Issue 內容
- 理解問題描述和重現步驟
- 定位相關程式碼檔案
- 生成修復補丁
- 運行測試驗證
- 提交修復結果

### 2. 程式碼修復

針對各種程式碼問題提供自動修復能力：

- Bug 修復
- 功能增強
- 性能優化
- 程式碼重構
- 文檔補充

### 3. SWE-bench 評測

SWE-bench 是業界標準的軟體工程 AI 評測基準，包含真實的開源專案 Issue：

- 完整的測試數據集
- 標準化評測流程
- 性能指標追蹤
- 結果可視化

## 安裝指南

### 系統要求

- Python 3.8 或更高版本
- Docker 20.10 或更高版本
- Git 2.0 或更高版本
- 8GB+ RAM 建議
- Linux/macOS (Windows 需 WSL2)

### 基礎安裝

```bash
# 克隆儲存庫
git clone https://github.com/princeton-nlp/SWE-agent.git
cd SWE-agent

# 安裝依賴
pip install -r requirements.txt

# 或使用 pip 直接安裝
pip install sweagent
```

### Docker 設置

```bash
# 確保 Docker 正在運行
docker --version

# 拉取基礎映像
docker pull sweagent/swe-agent:latest
```

### API 金鑰配置

```bash
# 設置 OpenAI API 金鑰
export OPENAI_API_KEY="your-api-key-here"

# 或設置 Anthropic API 金鑰
export ANTHROPIC_API_KEY="your-api-key-here"

# GitHub Token (用於訪問私有儲存庫)
export GITHUB_TOKEN="your-github-token"
```

## 快速開始

### 基本使用範例

```python
from sweagent import SWEAgent
from sweagent.environment import DockerEnvironment

# 初始化 Agent
agent = SWEAgent(
    model="gpt-4",
    api_key="your-api-key"
)

# 創建執行環境
env = DockerEnvironment(
    image="python:3.9",
    repo_path="/path/to/repo"
)

# 解決 GitHub Issue
result = agent.solve_issue(
    repo="owner/repo",
    issue_number=123,
    environment=env
)

print(f"修復結果: {result.status}")
print(f"生成的補丁: {result.patch}")
```

### 從 Issue URL 解決問題

```python
from sweagent import SWEAgent

agent = SWEAgent(model="claude-3-5-sonnet-20241022")

# 直接從 Issue URL 解決
result = agent.solve_from_url(
    "https://github.com/django/django/issues/12345"
)

if result.success:
    print(f"成功修復! 補丁已保存到: {result.patch_path}")
    print(f"通過測試數: {result.tests_passed}/{result.tests_total}")
```

### 本地程式碼修復

```python
from sweagent import SWEAgent
from sweagent.task import Task

agent = SWEAgent(model="gpt-4-turbo")

# 定義修復任務
task = Task(
    description="修復 user_service.py 中的記憶體洩漏問題",
    repo_path="/path/to/project",
    test_command="pytest tests/test_user_service.py"
)

# 執行修復
result = agent.run_task(task)
```

## 使用案例

### 案例 1: 開源專案維護

**場景**: 你維護一個開源專案，收到大量 Issue 報告

**解決方案**:
```python
from sweagent import SWEAgent, IssueManager

agent = SWEAgent(model="gpt-4")
manager = IssueManager(repo="your-org/your-repo")

# 自動處理新 Issue
for issue in manager.get_new_issues():
    if issue.is_bug_report():
        result = agent.solve_issue(
            repo="your-org/your-repo",
            issue_number=issue.number
        )

        if result.success:
            manager.create_pull_request(
                issue=issue,
                patch=result.patch,
                title=f"Fix #{issue.number}: {issue.title}"
            )
```

### 案例 2: CI/CD 整合

**場景**: 在 CI 流程中自動修復常見問題

**解決方案**:
```python
from sweagent import SWEAgent
from sweagent.triggers import TestFailureTrigger

agent = SWEAgent(model="claude-3-5-sonnet-20241022")

# 監聽測試失敗
trigger = TestFailureTrigger(
    test_command="pytest",
    on_failure=lambda failures: agent.fix_tests(failures)
)

trigger.run()
```

### 案例 3: 程式碼審查輔助

**場景**: 在 PR 審查過程中自動發現並修復問題

**解決方案**:
```python
from sweagent import SWEAgent, CodeReviewer

agent = SWEAgent(model="gpt-4")
reviewer = CodeReviewer(agent=agent)

# 審查 Pull Request
issues = reviewer.review_pr(
    repo="org/repo",
    pr_number=456
)

# 自動修復發現的問題
for issue in issues:
    if issue.auto_fixable:
        agent.fix_issue(issue)
```

### 案例 4: 技術債務清理

**場景**: 系統性地解決專案中的技術債務

**解決方案**:
```python
from sweagent import SWEAgent
from sweagent.debt import TechnicalDebtAnalyzer

agent = SWEAgent(model="gpt-4-turbo")
analyzer = TechnicalDebtAnalyzer(repo_path="/path/to/repo")

# 分析技術債務
debts = analyzer.analyze(
    categories=["deprecated_api", "code_smell", "security"]
)

# 批次修復
for debt in debts:
    result = agent.fix_technical_debt(debt)
    print(f"修復 {debt.type}: {result.status}")
```

### 案例 5: SWE-bench 評測

**場景**: 評估和改進 Agent 性能

**解決方案**:
```python
from sweagent import SWEAgent
from sweagent.evaluation import SWEBenchEvaluator

agent = SWEAgent(model="gpt-4")
evaluator = SWEBenchEvaluator()

# 在測試集上評估
results = evaluator.evaluate(
    agent=agent,
    dataset="swe-bench-lite",
    num_instances=100
)

print(f"解決率: {results.solve_rate}%")
print(f"平均成本: ${results.avg_cost}")
print(f"平均時間: {results.avg_time}秒")
```

## 配置選項

### Agent 配置

```python
agent = SWEAgent(
    model="gpt-4",                    # LLM 模型
    api_key="your-key",               # API 金鑰
    temperature=0.2,                  # 生成溫度
    max_iterations=30,                # 最大迭代次數
    timeout=1800,                     # 超時時間（秒）
    tools=["search", "edit", "test"], # 啟用的工具
    memory_size=10000,                # 記憶體大小
    verbose=True                      # 詳細輸出
)
```

### 環境配置

```python
env = DockerEnvironment(
    image="python:3.9",
    repo_path="/path/to/repo",
    install_commands=[
        "pip install -r requirements.txt",
        "pip install -e ."
    ],
    resource_limits={
        "memory": "4g",
        "cpus": 2
    }
)
```

## 性能指標

根據 SWE-bench 官方評測結果：

| 模型配置 | 解決率 | 平均時間 | 平均成本 |
|---------|--------|----------|----------|
| GPT-4 | 12.5% | 3.2分鐘 | $1.50 |
| GPT-4 Turbo | 13.8% | 2.8分鐘 | $0.80 |
| Claude 3.5 Sonnet | 14.2% | 2.5分鐘 | $0.75 |
| GPT-4o | 15.1% | 2.3分鐘 | $0.60 |

## 注意事項

1. **API 成本**: 每個 Issue 解決可能消耗大量 tokens，建議設置預算限制
2. **執行時間**: 複雜問題可能需要 10-30 分鐘
3. **Docker 資源**: 確保有足夠的 Docker 資源
4. **安全性**: 在沙箱環境中執行不受信任的程式碼
5. **測試覆蓋**: 確保專案有良好的測試覆蓋率

## 進階功能

### 自定義工具

```python
from sweagent.tools import Tool

class CustomSearchTool(Tool):
    def execute(self, query):
        # 自定義搜索邏輯
        return results

agent.register_tool(CustomSearchTool())
```

### 多 Agent 協作

```python
from sweagent import SWEAgent, AgentTeam

team = AgentTeam([
    SWEAgent(model="gpt-4", role="debugger"),
    SWEAgent(model="claude-3-5-sonnet", role="tester"),
    SWEAgent(model="gpt-4-turbo", role="reviewer")
])

result = team.solve_issue(repo="org/repo", issue_number=123)
```

## 相關資源

- [官方文檔](https://princeton-nlp.github.io/SWE-agent/)
- [GitHub 儲存庫](https://github.com/princeton-nlp/SWE-agent)
- [SWE-bench 基準測試](https://www.swebench.com/)
- [論文](https://arxiv.org/abs/2405.15793)
- [Discord 社群](https://discord.gg/swe-agent)

## 授權

MIT License

## 貢獻

歡迎提交 Issue 和 Pull Request！

---

**更新日期**: 2025-12-31
**版本**: 0.6.0
