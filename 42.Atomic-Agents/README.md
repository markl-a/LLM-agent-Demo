# Atomic Agents 框架

## 框架介紹

Atomic Agents 是一個輕量級、模組化的 AI Agent 框架，專注於構建具有清晰輸入輸出模式的 AI 代理和管道。該框架強調可預測性和可測試性，讓開發者能夠輕鬆構建、測試和部署生產級的 AI 應用。

Atomic Agents 的核心理念是將複雜的 AI 工作流分解為可組合的"原子"組件，每個組件都有明確定義的輸入和輸出模式。這種設計使得代碼更容易理解、測試和維護。

## 核心特性

### 模組化設計
- **原子組件**：將 Agent 功能分解為小型、可重用的組件
- **清晰界面**：每個組件都有明確定義的輸入和輸出
- **可組合性**：輕鬆組合多個組件構建複雜工作流
- **解耦架構**：組件之間低耦合，易於替換和擴展

### Schema 驅動
- **類型安全**：使用 Pydantic 模型確保類型安全
- **自動驗證**：輸入輸出自動驗證，減少運行時錯誤
- **文檔生成**：從 Schema 自動生成文檔
- **IDE 支持**：完整的類型提示和自動完成

### 可測試性
- **單元測試**：每個原子組件都可獨立測試
- **Mock 支持**：輕鬆模擬外部依賴
- **確定性**：清晰的輸入輸出使測試更加可靠
- **測試覆蓋**：易於達到高測試覆蓋率

### 輕量級
- **最小依賴**：只依賴必要的核心庫
- **快速啟動**：低開銷，快速初始化
- **靈活部署**：適用於各種部署環境
- **易於學習**：簡潔的 API，快速上手

## 安裝指南

### 基本安裝

```bash
# 使用 pip 安裝
pip install atomic-agents

# 或從源碼安裝
git clone https://github.com/BrainBlend-AI/atomic-agents.git
cd atomic-agents
pip install -e .
```

### 安裝完整依賴

```bash
# 安裝所有依賴（包括可選依賴）
pip install -r requirements.txt
```

### 驗證安裝

```python
import atomic_agents
print(f"Atomic Agents 版本: {atomic_agents.__version__}")
```

## 快速開始

### 創建第一個 Agent

```python
from atomic_agents.agents.base_agent import BaseAgent
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from pydantic import BaseModel, Field
from typing import Optional

# 定義輸入模式
class UserQuery(BaseModel):
    """用戶查詢輸入模式"""
    question: str = Field(..., description="用戶的問題")
    context: Optional[str] = Field(None, description="可選的上下文信息")

# 定義輸出模式
class AgentResponse(BaseModel):
    """Agent 響應輸出模式"""
    answer: str = Field(..., description="Agent 的回答")
    confidence: float = Field(..., description="回答的信心分數 (0-1)")

# 創建 Agent
class SimpleAgent(BaseAgent):
    """簡單的問答 Agent"""

    def __init__(self):
        # 配置系統提示
        system_prompt = SystemPromptGenerator(
            background=[
                "你是一個專業的 AI 助手。",
                "你的任務是回答用戶的問題並提供信心分數。"
            ],
            steps=[
                "仔細理解用戶的問題",
                "基於你的知識提供準確的回答",
                "評估你對答案的信心程度"
            ],
            output_instructions=[
                "提供清晰、簡潔的回答",
                "信心分數應在 0 到 1 之間"
            ]
        )

        super().__init__(
            input_schema=UserQuery,
            output_schema=AgentResponse,
            system_prompt_generator=system_prompt
        )

# 使用 Agent
agent = SimpleAgent()
query = UserQuery(question="什麼是 Atomic Agents？")
response = agent.run(query)

print(f"回答: {response.answer}")
print(f"信心分數: {response.confidence}")
```

### 構建 Agent 管道

```python
from atomic_agents.agents.base_agent import BaseAgent

# 創建多個 Agent
classifier = ClassifierAgent()
analyzer = AnalyzerAgent()
responder = ResponderAgent()

# 構建管道
def process_query(user_input: str) -> str:
    # 步驟 1: 分類
    classification = classifier.run(user_input)

    # 步驟 2: 分析
    analysis = analyzer.run(classification)

    # 步驟 3: 生成響應
    response = responder.run(analysis)

    return response.text

# 執行管道
result = process_query("如何使用 Atomic Agents？")
print(result)
```

## 使用場景

### 1. 對話系統
構建智能客服、虛擬助手等對話式 AI 應用：
- 意圖識別
- 上下文管理
- 多輪對話
- 個性化回應

### 2. 數據處理管道
創建端到端的數據處理工作流：
- 數據提取
- 內容分析
- 信息轉換
- 結果聚合

### 3. 內容生成
自動化內容創作和優化：
- 文章生成
- 內容摘要
- 風格轉換
- 多語言翻譯

### 4. 自動化工作流
構建企業級自動化解決方案：
- 文檔處理
- 報告生成
- 郵件分類
- 智能路由

### 5. 研究與實驗
快速原型設計和實驗：
- A/B 測試
- 模型比較
- 提示工程
- 性能優化

## 項目結構

```
42.Atomic-Agents/
├── README.md                 # 項目說明文檔
├── requirements.txt          # 依賴列表
├── 01_快速開始.py           # 基礎 Agent 設置
├── 02_輸入輸出模式.py       # Schema 定義
├── 03_原子工具.py           # 工具創建
├── 04_鏈式管道.py           # 管道構建
├── 05_上下文管理.py         # 上下文和記憶
├── 06_錯誤處理.py           # 錯誤處理
├── 07_多模型支援.py         # 多 LLM 支持
├── 08_測試策略.py           # 測試方法
├── 09_流式輸出.py           # 流式響應
└── 10_生產部署.py           # 部署模式
```

## 學習路徑

1. **入門階段**
   - 閱讀 `01_快速開始.py` 了解基本概念
   - 學習 `02_輸入輸出模式.py` 掌握 Schema 設計
   - 實踐 `03_原子工具.py` 創建自定義工具

2. **進階階段**
   - 探索 `04_鏈式管道.py` 構建複雜工作流
   - 研究 `05_上下文管理.py` 處理狀態
   - 掌握 `06_錯誤處理.py` 提高穩定性

3. **生產階段**
   - 學習 `07_多模型支援.py` 實現模型切換
   - 實施 `08_測試策略.py` 確保質量
   - 應用 `09_流式輸出.py` 優化用戶體驗
   - 參考 `10_生產部署.py` 部署到生產環境

## 最佳實踐

### Schema 設計
- 使用描述性的字段名稱
- 為每個字段添加清晰的描述
- 使用適當的類型約束和驗證
- 提供合理的默認值

### Agent 組織
- 保持 Agent 職責單一
- 使用組合而非繼承
- 明確定義 Agent 邊界
- 避免循環依賴

### 錯誤處理
- 實現優雅的降級策略
- 提供有意義的錯誤消息
- 記錄關鍵操作日誌
- 使用重試機制處理臨時故障

### 測試
- 為每個 Agent 編寫單元測試
- 使用 Mock 隔離外部依賴
- 測試邊界情況和錯誤路徑
- 保持高測試覆蓋率

## 相關資源

- **官方文檔**: https://atomic-agents.readthedocs.io/
- **GitHub 倉庫**: https://github.com/BrainBlend-AI/atomic-agents
- **示例項目**: https://github.com/BrainBlend-AI/atomic-agents-examples
- **社區論壇**: https://github.com/BrainBlend-AI/atomic-agents/discussions

## 技術支持

如有問題或建議，歡迎通過以下方式聯繫：
- 提交 GitHub Issue
- 參與社區討論
- 查閱官方文檔

## 許可證

Atomic Agents 採用 MIT 許可證，可自由用於商業和個人項目。

## 貢獻

歡迎貢獻代碼、文檔或示例！請查看貢獻指南了解詳情。
