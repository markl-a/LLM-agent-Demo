# CAMEL-AI 框架

## 簡介

CAMEL (Communicative Agents for "Mind" Exploration of Large Language Model Society) 是一個開創性的多 Agent 研究框架，專注於探索大型語言模型的自主協作能力。該框架通過角色扮演和任務導向的對話，研究多個 AI Agent 如何協同工作以解決複雜問題。

### 核心特性

- **角色扮演系統**：定義具有特定專業和個性的 Agent 角色
- **Multi-Agent 協作**：支援多個 Agent 之間的自主對話和協作
- **任務自動分解**：智能將複雜任務分解為可執行的子任務
- **社會模擬**：模擬 AI Agent 社會的互動和演化
- **工具整合**：支援外部工具和 API 調用
- **知識檢索**：整合 RAG (Retrieval-Augmented Generation) 能力

### 研究背景

CAMEL 框架源於對以下問題的探索：
- 多個 LLM Agent 如何自主協作？
- 角色扮演如何增強任務完成能力？
- AI Agent 社會如何演化和互動？
- 如何實現完全自主的任務執行？

## 架構設計

### 1. 角色扮演系統

CAMEL 的核心是其角色扮演機制：

```
┌─────────────────────────────────────┐
│        Role-Playing Framework       │
├─────────────────────────────────────┤
│  • AI User Agent (任務提出者)      │
│  • AI Assistant Agent (任務執行者) │
│  • Task Specifier (任務細化器)     │
│  • Critic Agent (評估者)           │
└─────────────────────────────────────┘
```

**角色類型**：
- **User Agent**：提出需求和問題
- **Assistant Agent**：提供解決方案
- **Task Specifier**：將模糊任務具體化
- **Critic**：評估輸出質量

### 2. Multi-Agent 對話流程

```
初始任務 → Task Specifier → 具體任務
                ↓
        User Agent ←→ Assistant Agent
                ↓
        Critic Agent (評估)
                ↓
            最終輸出
```

### 3. 任務分解與執行

CAMEL 自動將複雜任務分解為步驟：

1. **任務理解**：分析任務需求和約束
2. **任務分解**：生成執行步驟
3. **角色協作**：多 Agent 協同執行
4. **結果整合**：合併各 Agent 的輸出

## 主要組件

### RolePlaying 類

管理兩個 Agent 之間的對話：

```python
from camel.societies import RolePlaying

# 創建角色扮演場景
role_play = RolePlaying(
    assistant_role_name="Python 程式設計師",
    user_role_name="產品經理",
    task_prompt="開發一個任務管理系統"
)
```

### Agent 類型

1. **ChatAgent**：基礎對話 Agent
2. **TaskAgent**：任務導向 Agent
3. **CriticAgent**：評估和反饋 Agent
4. **EmbodiedAgent**：具身 Agent（可操作環境）

### Message 系統

```python
from camel.messages import BaseMessage

message = BaseMessage(
    role_name="助手",
    role_type=RoleType.ASSISTANT,
    meta_dict={"task": "編程"},
    content="我會幫你完成這個任務"
)
```

## 核心功能

### 1. 角色扮演對話

```python
# 定義角色
assistant_role = "資深軟體工程師"
user_role = "專案經理"

# 創建對話
session = RolePlaying(
    assistant_role_name=assistant_role,
    user_role_name=user_role,
    task_prompt="設計微服務架構"
)

# 執行對話
for msg in session.run():
    print(f"{msg.role_name}: {msg.content}")
```

### 2. 任務自動化

CAMEL 可以自動執行多步驟任務：

- **需求分析**：理解任務目標
- **方案設計**：制定執行計劃
- **分步實施**：逐步完成任務
- **質量檢查**：驗證結果

### 3. Multi-Agent 社會

模擬多個 Agent 的社會互動：

```python
from camel.societies import BabyAGI

society = BabyAGI(
    task="研發新產品",
    agents=[
        {"role": "CEO", "expertise": "戰略規劃"},
        {"role": "CTO", "expertise": "技術架構"},
        {"role": "設計師", "expertise": "UI/UX"}
    ]
)
```

### 4. 工具整合

支援外部工具調用：

- **搜尋引擎**：Google、Bing 搜尋
- **代碼執行**：Python、Shell 命令
- **API 調用**：REST API、數據庫
- **文件操作**：讀寫、解析文件

### 5. 知識檢索 (RAG)

整合向量數據庫進行知識檢索：

```python
from camel.retrievers import VectorRetriever

retriever = VectorRetriever(
    embedding_model="text-embedding-ada-002",
    vector_store="chromadb"
)

# 檢索相關知識
context = retriever.retrieve(query="如何設計 API")
```

## 應用場景

### 學術研究

- **AI 協作研究**：研究多 Agent 協作機制
- **對話系統**：研發更自然的對話模型
- **認知科學**：理解 AI 的"思維"過程
- **社會模擬**：模擬 AI 社會演化

### 商業應用

1. **軟體開發**
   - 需求分析到代碼實現
   - 自動化測試和除錯
   - 代碼審查和優化

2. **內容創作**
   - 協作寫作（多角色）
   - 創意腦力激盪
   - 內容審核和改進

3. **客戶服務**
   - 多層級問題解決
   - 知識庫查詢
   - 個性化回應

4. **研發創新**
   - 產品設計協作
   - 技術方案評估
   - 專利檢索分析

### 教育應用

- **程式教學**：學生與 AI 導師對話
- **語言學習**：角色扮演練習
- **問題解決**：蘇格拉底式提問

## 安裝與配置

### 安裝

```bash
# 使用 pip 安裝
pip install camel-ai

# 或從源碼安裝
git clone https://github.com/camel-ai/camel.git
cd camel
pip install -e .
```

### 依賴套件

```
camel-ai>=0.1.0
openai>=1.0.0
anthropic>=0.3.0
langchain>=0.1.0
chromadb>=0.4.0
numpy>=1.24.0
tiktoken>=0.5.0
```

### 環境配置

創建 `.env` 文件：

```bash
# OpenAI API
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1

# Anthropic API (可選)
ANTHROPIC_API_KEY=your_anthropic_key

# 其他配置
CAMEL_LOG_LEVEL=INFO
CAMEL_MAX_RETRIES=3
```

### 基本配置

```python
from camel.configs import ChatGPTConfig

config = ChatGPTConfig(
    temperature=0.7,
    max_tokens=2000,
    model="gpt-4",
    presence_penalty=0.0,
    frequency_penalty=0.0
)
```

## 快速開始

### 1. 簡單對話

```python
from camel.agents import ChatAgent
from camel.messages import BaseMessage

# 創建 Agent
agent = ChatAgent(system_message="你是一位友善的助手")

# 發送消息
user_msg = BaseMessage.make_user_message(
    role_name="用戶",
    content="你好，介紹一下 CAMEL"
)

response = agent.step(user_msg)
print(response.msg.content)
```

### 2. 角色扮演

```python
from camel.societies import RolePlaying

# 創建角色扮演場景
role_play = RolePlaying(
    assistant_role_name="資深 Python 開發者",
    user_role_name="初學者",
    task_prompt="學習 Python 裝飾器"
)

# 執行對話（最多 10 輪）
for i, msg in enumerate(role_play.run(max_iters=10)):
    print(f"輪次 {i}: {msg.content[:100]}...")
```

### 3. 任務分解

```python
from camel.tasks import TaskPlanner

planner = TaskPlanner()
task = "開發一個電商網站"

# 分解任務
subtasks = planner.decompose(task)
for i, subtask in enumerate(subtasks, 1):
    print(f"{i}. {subtask}")
```

## 進階特性

### 1. 自定義 Agent

```python
from camel.agents import ChatAgent
from camel.typing import RoleType

class ExpertAgent(ChatAgent):
    def __init__(self, expertise):
        system_msg = f"你是一位 {expertise} 專家"
        super().__init__(
            system_message=system_msg,
            role_type=RoleType.ASSISTANT
        )

    def analyze(self, problem):
        """專家分析問題"""
        msg = BaseMessage.make_user_message(
            role_name="用戶",
            content=f"請分析：{problem}"
        )
        return self.step(msg)
```

### 2. Memory 機制

CAMEL 支援不同的記憶機制：

- **短期記憶**：對話歷史
- **長期記憶**：向量數據庫
- **工作記憶**：任務上下文

```python
from camel.memory import MemoryRecord

memory = MemoryRecord()
memory.add_message(role="user", content="任務需求")
memory.add_message(role="assistant", content="解決方案")

# 檢索相關記憶
relevant = memory.retrieve(query="之前的需求", top_k=3)
```

### 3. 工具使用

```python
from camel.toolkits import FunctionTool

def calculate_sum(a: int, b: int) -> int:
    """計算兩數之和"""
    return a + b

tool = FunctionTool(calculate_sum)
result = tool.run(a=5, b=3)
```

### 4. 多模態支援

```python
from camel.agents import MultiModalAgent

agent = MultiModalAgent(
    model="gpt-4-vision-preview"
)

# 處理圖像和文本
response = agent.process(
    text="描述這張圖片",
    image_url="https://example.com/image.jpg"
)
```

## 性能優化

### 1. 並行處理

```python
import asyncio
from camel.agents import ChatAgent

async def parallel_agents():
    agents = [ChatAgent() for _ in range(5)]
    tasks = [agent.step_async(msg) for agent in agents]
    results = await asyncio.gather(*tasks)
    return results
```

### 2. 緩存策略

```python
from camel.caching import ResponseCache

cache = ResponseCache(ttl=3600)  # 1小時過期

# 使用緩存
if cache.has(query):
    response = cache.get(query)
else:
    response = agent.step(query)
    cache.set(query, response)
```

### 3. Token 優化

```python
from camel.utils import TokenCounter

counter = TokenCounter(model="gpt-4")
tokens = counter.count(text)

# 控制 token 數量
if tokens > 3000:
    text = summarize(text)
```

## 最佳實踐

### 1. 角色設計

- 明確定義角色的專業領域
- 設置清晰的角色目標
- 避免角色職責重疊

### 2. 任務設計

- 任務描述要具體明確
- 設置合理的完成標準
- 提供必要的上下文信息

### 3. 對話控制

- 設置最大輪次限制
- 實施終止條件檢查
- 監控對話質量

### 4. 錯誤處理

```python
from camel.exceptions import CAMELError

try:
    result = agent.step(message)
except CAMELError as e:
    print(f"CAMEL 錯誤: {e}")
    # 實施回退策略
```

## 示例項目結構

```
camel-project/
├── agents/              # 自定義 Agent
│   ├── expert_agent.py
│   └── task_agent.py
├── societies/           # 社會模擬
│   ├── dev_team.py
│   └── research_lab.py
├── tools/              # 工具集
│   ├── search.py
│   └── code_exec.py
├── configs/            # 配置文件
│   └── settings.py
├── data/               # 數據和知識庫
│   ├── documents/
│   └── embeddings/
├── logs/               # 日誌
└── main.py            # 主程序
```

## 研究方向

CAMEL 框架支援以下研究方向：

1. **Multi-Agent 協作機制**
   - 通信協議設計
   - 任務分配策略
   - 衝突解決機制

2. **涌現行為研究**
   - Agent 社會演化
   - 協作模式識別
   - 集體智能

3. **角色扮演優化**
   - 角色一致性
   - 專業知識注入
   - 個性化建模

4. **自主性增強**
   - 自主任務規劃
   - 自我評估和改進
   - 目標導向行為

## 社群與資源

- **官方網站**：https://www.camel-ai.org/
- **GitHub**：https://github.com/camel-ai/camel
- **論文**：[CAMEL: Communicative Agents for "Mind" Exploration](https://arxiv.org/abs/2303.17760)
- **文檔**：https://docs.camel-ai.org/
- **Discord**：CAMEL-AI 社群

## 貢獻指南

歡迎為 CAMEL 做出貢獻：

1. Fork 專案
2. 創建功能分支
3. 提交更改
4. 推送到分支
5. 創建 Pull Request

## 許可證

CAMEL 使用 Apache 2.0 許可證。

## 致謝

CAMEL 由研究社群開發，感謝所有貢獻者的努力。

---

**注意**：本框架主要用於研究目的，生產環境使用請謹慎評估。
