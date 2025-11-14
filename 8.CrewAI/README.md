# CrewAI 學習教程

## 📚 簡介

CrewAI 是一個角色扮演型多 Agent 協作框架，通過定義不同角色的 Agent 來協作完成複雜任務。

### 核心概念

- **Agent（代理）**: 具有特定角色、目標和能力的 AI 實體
- **Task（任務）**: Agent 需要完成的具體工作
- **Crew（團隊）**: 多個 Agent 組成的協作團隊
- **Process（流程）**: 任務執行的順序和方式

## 🎯 教程內容

### 0. 快速開始 (0.快速開始.ipynb)
- CrewAI 安裝和基礎配置
- 創建第一個 Agent
- 定義簡單任務
- 組建團隊並執行

### 1. 角色和任務 (1.角色和任務.ipynb)
- 深入理解 Agent 角色定義
- 設計任務和目標
- 使用工具（Tools）
- 任務依賴和流程

### 2. 實際案例 (2.實際案例.ipynb)
- 內容創作團隊
- 市場研究團隊
- 軟體開發團隊
- 客戶服務團隊

## 🚀 快速示例

```python
from crewai import Agent, Task, Crew, Process

# 定義研究員 Agent
researcher = Agent(
    role='研究員',
    goal='進行深入的市場研究',
    backstory='你是一位經驗豐富的市場研究專家',
    verbose=True
)

# 定義寫作 Agent
writer = Agent(
    role='內容作家',
    goal='撰寫引人入勝的文章',
    backstory='你是一位專業的內容創作者',
    verbose=True
)

# 定義任務
research_task = Task(
    description='研究 AI Agent 的最新趨勢',
    agent=researcher
)

write_task = Task(
    description='基於研究結果撰寫一篇文章',
    agent=writer
)

# 組建團隊
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential
)

# 執行
result = crew.kickoff()
```

## 💡 最佳實踐

1. **清晰的角色定義**: 給每個 Agent 明確的角色和職責
2. **具體的任務描述**: 任務描述要詳細和可執行
3. **合理的工具配置**: 為 Agent 提供必要的工具
4. **流程設計**: 根據任務特點選擇合適的執行流程

## 📖 學習資源

- [CrewAI 官方文檔](https://docs.crewai.com/)
- [GitHub 倉庫](https://github.com/joaomdmoura/crewAI)
