# Letta (MemGPT) 框架

## 框架介紹

Letta（前身為 MemGPT）是一個革命性的有狀態 AI Agent 框架，專為需要持久記憶和長期上下文管理的應用而設計。它使開發者能夠構建真正記得過去對話的 AI Agent，就像人類一樣擁有長期記憶。

### 核心概念

Letta 實現了類似操作系統的記憶管理架構，將記憶分為：
- **核心記憶（Core Memory）**: 類似 CPU 緩存，存儲當前對話的關鍵信息
- **歸檔記憶（Archival Memory）**: 類似硬碟，存儲所有歷史信息
- **回憶記憶（Recall Memory）**: 存儲完整的對話歷史

## 主要特性

### 1. 持久記憶系統
- **多層記憶架構**: 核心記憶、歸檔記憶、回憶記憶三層結構
- **智能記憶管理**: 自動決定何時存儲、檢索和遺忘信息
- **長期上下文**: 支持無限長度的對話歷史

### 2. MemGPT 架構
- **自我編輯記憶**: Agent 可以主動管理自己的記憶
- **上下文窗口管理**: 智能管理有限的 LLM 上下文窗口
- **記憶分頁**: 類似操作系統的內存分頁機制

### 3. 狀態管理
- **持久化狀態**: 所有對話狀態都可以保存和恢復
- **多會話支持**: 支持並行管理多個獨立對話
- **狀態序列化**: 完整的狀態導出和導入功能

### 4. 長期記憶能力
- **向量數據庫集成**: 使用 ChromaDB 等進行語義搜索
- **SQL 存儲**: 使用 SQLAlchemy 進行結構化數據存儲
- **混合檢索**: 結合關鍵詞和語義搜索

## 安裝指南

### 基本安裝

```bash
# 使用 pip 安裝
pip install letta

# 或從源碼安裝
git clone https://github.com/letta-ai/letta.git
cd letta
pip install -e .
```

### 依賴安裝

```bash
# 安裝所有依賴
pip install -r requirements.txt

# 核心依賴
pip install letta>=0.5.0
pip install openai>=1.50.0
pip install anthropic>=0.37.0
pip install chromadb>=0.5.0
pip install sqlalchemy>=2.0.0
```

### 環境配置

```bash
# 設置 API 密鑰
export OPENAI_API_KEY="your-api-key"
export ANTHROPIC_API_KEY="your-api-key"

# 或使用 .env 文件
echo "OPENAI_API_KEY=your-api-key" > .env
echo "ANTHROPIC_API_KEY=your-api-key" >> .env
```

## 快速開始

### 基本使用示例

```python
from letta import create_client

# 創建 Letta 客戶端
client = create_client()

# 創建一個新的 Agent
agent_state = client.create_agent(
    name="我的助手",
    persona="你是一個友善且樂於助人的 AI 助手，能記住所有對話內容。",
    human="用戶是一個需要長期支持的客戶。"
)

# 與 Agent 對話
response = client.send_message(
    agent_id=agent_state.id,
    message="你好！我叫小明，我喜歡編程。"
)
print(response)

# 在另一個會話中，Agent 仍然記得
response = client.send_message(
    agent_id=agent_state.id,
    message="你還記得我的名字嗎？"
)
print(response)  # Agent 會回答："當然，你是小明！"
```

### 記憶管理示例

```python
# 查看核心記憶
core_memory = client.get_core_memory(agent_id=agent_state.id)
print(f"核心記憶: {core_memory}")

# 修改核心記憶
client.update_core_memory(
    agent_id=agent_state.id,
    section="human",
    content="用戶小明是一個熱愛 Python 編程的開發者"
)

# 搜索歸檔記憶
results = client.search_archival_memory(
    agent_id=agent_state.id,
    query="編程相關的對話",
    limit=5
)
```

### 工具集成示例

```python
from letta import Tool

# 定義自定義工具
def search_web(query: str) -> str:
    """搜索網絡上的信息"""
    # 實現搜索邏輯
    return f"搜索結果: {query}"

# 註冊工具
tool = Tool(
    name="search_web",
    func=search_web,
    description="在網絡上搜索信息"
)

# 創建帶工具的 Agent
agent_state = client.create_agent(
    name="搜索助手",
    tools=[tool]
)
```

## 核心功能詳解

### 1. 三層記憶架構

**核心記憶（Core Memory）**
- 大小受限（通常 2-4K tokens）
- 每次交互都會加載
- 存儲最重要的信息

**歸檔記憶（Archival Memory）**
- 無限容量
- 通過向量搜索訪問
- 存儲所有歷史信息

**回憶記憶（Recall Memory）**
- 存儲完整對話歷史
- 按時間順序組織
- 可以分頁檢索

### 2. 自我編輯能力

Agent 可以使用內建函數管理記憶：
- `core_memory_append()`: 添加信息到核心記憶
- `core_memory_replace()`: 替換核心記憶內容
- `archival_memory_insert()`: 插入到歸檔記憶
- `archival_memory_search()`: 搜索歸檔記憶

### 3. 持久化機制

所有數據自動保存到本地數據庫：
- SQLite 用於結構化數據
- ChromaDB 用於向量存儲
- 支持自定義存儲後端

## 應用場景

### 1. 長對話應用
- **客戶服務**: 記住客戶的歷史問題和偏好
- **教育輔導**: 追蹤學生的學習進度和困難點
- **健康諮詢**: 記錄患者的症狀和治療歷史

### 2. 個人助理
- **日程管理**: 記住用戶的習慣和偏好
- **任務追蹤**: 長期追蹤項目進度
- **知識助手**: 積累專業領域知識

### 3. 知識管理
- **文檔問答**: 基於大量文檔的智能問答
- **研究助手**: 管理和檢索研究資料
- **企業知識庫**: 公司內部知識管理系統

### 4. 遊戲和娛樂
- **遊戲 NPC**: 記住玩家行為的遊戲角色
- **故事生成**: 連貫的長篇故事創作
- **虛擬夥伴**: 有記憶的虛擬朋友

## 項目結構

```
45.Letta/
├── README.md                 # 本文件
├── requirements.txt          # 項目依賴
├── 01_快速開始.py           # 基本設置和使用
├── 02_記憶管理.py           # 記憶系統詳解
├── 03_對話持久化.py         # 持久化對話
├── 04_工具整合.py           # 工具和函數調用
├── 05_知識庫.py             # 知識庫構建
├── 06_多Agent.py            # 多 Agent 系統
├── 07_自定義Persona.py      # 自定義人格
├── 08_記憶檢索.py           # 高級檢索策略
├── 09_狀態序列化.py         # 狀態保存和恢復
└── 10_生產部署.py           # 生產環境部署
```

## 學習路徑

### 初學者
1. 從 `01_快速開始.py` 了解基本概念
2. 學習 `02_記憶管理.py` 理解記憶系統
3. 實踐 `03_對話持久化.py` 掌握持久化

### 中級開發者
4. 探索 `04_工具整合.py` 擴展 Agent 能力
5. 學習 `05_知識庫.py` 構建知識系統
6. 研究 `06_多Agent.py` 設計複雜系統

### 高級開發者
7. 掌握 `07_自定義Persona.py` 打造獨特 Agent
8. 優化 `08_記憶檢索.py` 提升性能
9. 實現 `09_狀態序列化.py` 高級功能
10. 部署 `10_生產部署.py` 到生產環境

## 最佳實踐

### 記憶管理
- **核心記憶**: 只存儲最關鍵的信息（姓名、偏好、當前任務）
- **定期清理**: 使用 Agent 的自我編輯能力更新過時信息
- **結構化存儲**: 在核心記憶中使用清晰的格式

### 性能優化
- **批量處理**: 合併相似的記憶操作
- **索引優化**: 為常用查詢建立索引
- **緩存策略**: 緩存頻繁訪問的記憶

### 安全性
- **數據加密**: 敏感信息加密存儲
- **訪問控制**: 實施適當的權限管理
- **審計日誌**: 記錄所有記憶訪問

## 常見問題

### Q: Letta 和普通 LLM 有什麼區別？
A: Letta 提供持久記憶，能在多次對話間保持上下文，而普通 LLM 每次對話都是獨立的。

### Q: 記憶容量有限制嗎？
A: 核心記憶有限（2-4K tokens），但歸檔記憶和回憶記憶理論上無限。

### Q: 支持哪些 LLM 後端？
A: 支持 OpenAI、Anthropic、本地模型（通過 LiteLLM）等多種後端。

### Q: 如何遷移數據？
A: 使用狀態序列化功能，可以導出和導入完整的 Agent 狀態。

### Q: 性能如何？
A: 記憶檢索通常在毫秒級別，具體取決於數據量和硬件配置。

## 相關資源

- **官方網站**: https://www.letta.com/
- **GitHub**: https://github.com/letta-ai/letta
- **文檔**: https://docs.letta.com/
- **Discord 社區**: https://discord.gg/letta
- **論文**: MemGPT - Towards LLMs as Operating Systems

## 技術支持

如遇問題，請通過以下方式獲取幫助：
- 查看官方文檔
- 在 GitHub 提交 Issue
- 加入 Discord 社區討論
- 查看示例代碼

## 版本信息

- **當前版本**: 0.5.0+
- **Python 要求**: 3.10+
- **最後更新**: 2025年

## 授權協議

Letta 使用 Apache 2.0 授權協議，可自由用於商業和非商業項目。
