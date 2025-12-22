# Microsoft Magentic-One 多 Agent 系統

## 概述

Magentic-One 是 Microsoft 開發的先進多 Agent 系統，基於 AutoGen 框架構建。它專為解決複雜的實際任務而設計，通過多個專門化的 Agent 協同工作來完成網頁瀏覽、文件操作、代碼生成等多樣化任務。

## 核心特點

### 1. 模組化 Agent 架構
- **Orchestrator（協調者）**: 任務規劃、分解和協調
- **WebSurfer（網頁瀏覽器）**: 網頁搜索和信息提取
- **FileSurfer（文件瀏覽器）**: 文件系統操作和文檔處理
- **Coder（編碼者）**: 代碼生成、調試和執行
- **ComputerTerminal（終端）**: 系統命令執行

### 2. 智能任務協調
- 自動任務分解
- 動態 Agent 分配
- 結果整合與驗證
- 錯誤恢復機制

### 3. 人機協作
- 人工監督和介入
- 決策確認機制
- 交互式問題解決

### 4. 安全與控制
- 權限管理
- 沙盒執行環境
- 操作審計日誌

## 安裝

### 基礎安裝

```bash
# 安裝 AutoGen（包含 Magentic-One）
pip install pyautogen

# 或使用完整版本
pip install "pyautogen[magentic-one]"
```

### 額外依賴

```bash
# 網頁瀏覽功能
pip install playwright
playwright install

# 文件處理
pip install python-docx PyPDF2 pandas openpyxl

# 圖像處理
pip install pillow
```

### Docker 環境（推薦）

```bash
# 使用官方 Docker 鏡像
docker pull mcr.microsoft.com/autogen/magentic-one:latest

# 運行容器
docker run -it --rm \
  -v $(pwd):/workspace \
  -e OPENAI_API_KEY=your_key \
  mcr.microsoft.com/autogen/magentic-one:latest
```

## 環境配置

### API 密鑰設置

```python
import os

# OpenAI API
os.environ["OPENAI_API_KEY"] = "your_openai_key"

# Azure OpenAI
os.environ["AZURE_OPENAI_API_KEY"] = "your_azure_key"
os.environ["AZURE_OPENAI_ENDPOINT"] = "your_endpoint"
```

### 配置文件範例

創建 `config.json`:

```json
{
  "llm_config": {
    "model": "gpt-4",
    "api_key": "your_api_key",
    "temperature": 0.7,
    "max_tokens": 2000
  },
  "orchestrator": {
    "max_rounds": 30,
    "timeout": 600
  },
  "web_surfer": {
    "headless": true,
    "viewport": {"width": 1280, "height": 720}
  },
  "coder": {
    "work_dir": "./workspace",
    "use_docker": true
  },
  "safety": {
    "require_approval": ["delete", "execute", "write"],
    "blocked_commands": ["rm -rf", "format"]
  }
}
```

## 快速開始

### 基礎範例

```python
from autogen.agentchat.contrib.magentic_one import MagenticOne

# 創建 Magentic-One 系統
magentic_one = MagenticOne(
    llm_config={"model": "gpt-4", "api_key": "your_key"}
)

# 執行任務
result = magentic_one.run(
    task="搜索最新的 Python 3.12 新特性，並創建一個總結文檔"
)

print(result)
```

### 複雜任務範例

```python
# 多步驟任務
task = """
1. 訪問 Python 官網獲取 3.12 版本的發布說明
2. 提取主要新特性列表
3. 為每個特性創建代碼範例
4. 生成 Markdown 格式的完整報告
5. 保存到 python_312_features.md
"""

result = magentic_one.run(task=task)
```

## 核心 Agent 詳解

### 1. Orchestrator（協調者）

**職責**:
- 理解和分解任務
- 規劃執行策略
- 分配子任務給專門 Agent
- 監控執行進度
- 整合最終結果

**工作流程**:
```
用戶任務 → 任務分析 → 制定計劃 → 分配任務 → 監控執行 → 結果整合
```

**特點**:
- 使用高級 LLM（如 GPT-4）進行決策
- 維護任務狀態和上下文
- 處理異常和重試邏輯

### 2. WebSurfer（網頁瀏覽器）

**職責**:
- 網頁導航和搜索
- 信息提取
- 表單填寫和交互
- 截圖和內容保存

**能力**:
- 使用 Playwright 進行瀏覽器控制
- 智能等待和元素定位
- JavaScript 執行
- Cookie 和會話管理

**典型應用**:
- 信息收集和研究
- 價格比較
- 表單自動填寫
- 網頁監控

### 3. FileSurfer（文件瀏覽器）

**職責**:
- 文件系統導航
- 文件讀取和寫入
- 文檔格式轉換
- 目錄結構分析

**支持格式**:
- 文本：TXT, MD, JSON, XML
- 文檔：PDF, DOCX, XLSX
- 代碼：PY, JS, JAVA 等
- 圖像：PNG, JPG（基礎信息）

**操作類型**:
- 搜索和過濾
- 內容提取
- 批量處理
- 元數據管理

### 4. Coder（編碼者）

**職責**:
- 代碼生成
- 代碼執行和調試
- 測試用例創建
- 代碼審查和優化

**支持語言**:
- Python
- JavaScript/TypeScript
- Shell/Bash
- SQL

**執行環境**:
- 本地執行
- Docker 容器（推薦）
- 虛擬環境

**安全特性**:
- 代碼沙盒
- 資源限制
- 執行超時
- 輸出過濾

### 5. ComputerTerminal（終端）

**職責**:
- 系統命令執行
- 腳本運行
- 進程管理
- 環境操作

**能力**:
- 跨平台命令支持
- 管道和重定向
- 環境變量管理
- 輸出解析

**安全限制**:
- 命令白名單
- 權限檢查
- 危險操作確認
- 審計日誌

## 協作模式

### 1. 順序協作

```
Orchestrator → WebSurfer → FileSurfer → Coder → 完成
```

任務按順序在 Agent 之間流轉。

### 2. 並行協作

```
        ┌─ WebSurfer (搜索信息)
        │
Orchestrator ─┼─ FileSurfer (讀取本地文件)
        │
        └─ Coder (生成代碼框架)

        ↓ 結果整合
```

多個 Agent 同時執行不同子任務。

### 3. 迭代協作

```
Coder → Terminal (執行) → 錯誤 → Coder (修復) → Terminal → 成功
```

Agent 之間反覆交互直到完成。

### 4. 人機協作

```
Orchestrator → WebSurfer → [人工確認] → Coder → [人工審查] → 完成
```

關鍵步驟需要人工介入。

## 應用場景

### 1. 研究和數據收集

```python
task = """
調查 2024 年前 10 大 AI 模型：
1. 從相關網站收集信息
2. 提取模型參數、性能指標
3. 創建比較表格
4. 生成分析報告
"""
```

### 2. 軟件開發輔助

```python
task = """
創建一個 FastAPI Web 應用：
1. 生成項目結構
2. 實現 CRUD API
3. 添加數據庫集成
4. 創建測試用例
5. 生成文檔
"""
```

### 3. 文檔處理和分析

```python
task = """
分析季度銷售報告：
1. 讀取 Excel 文件
2. 計算關鍵指標
3. 生成可視化圖表
4. 創建 PowerPoint 總結
"""
```

### 4. 系統管理和自動化

```python
task = """
系統健康檢查：
1. 檢查磁盤空間
2. 監控服務狀態
3. 分析日誌錯誤
4. 生成健康報告
"""
```

## 高級功能

### 1. 自定義 Agent

```python
from autogen import ConversableAgent

class CustomAgent(ConversableAgent):
    def __init__(self, name, llm_config, **kwargs):
        super().__init__(name, llm_config=llm_config, **kwargs)

    def process_task(self, task):
        # 自定義任務處理邏輯
        pass
```

### 2. 工作流定制

```python
from autogen.agentchat.contrib.magentic_one import Orchestrator

orchestrator = Orchestrator(
    llm_config=llm_config,
    max_rounds=50,
    planning_strategy="hierarchical"  # 或 "sequential", "parallel"
)
```

### 3. 記憶和上下文管理

```python
magentic_one = MagenticOne(
    llm_config=llm_config,
    memory_config={
        "type": "vector",
        "storage": "chromadb",
        "collection": "tasks"
    }
)
```

### 4. 錯誤處理和重試

```python
result = magentic_one.run(
    task=task,
    max_retries=3,
    retry_strategy="exponential_backoff",
    error_handler=custom_error_handler
)
```

## 性能優化

### 1. 並行執行

啟用並行處理以加速獨立任務：

```python
orchestrator.config.update({
    "parallel_execution": True,
    "max_parallel_agents": 3
})
```

### 2. 緩存機制

減少重複的 LLM 調用：

```python
llm_config = {
    "model": "gpt-4",
    "cache_seed": 42  # 啟用緩存
}
```

### 3. 資源管理

設置資源限制：

```python
magentic_one = MagenticOne(
    llm_config=llm_config,
    resource_limits={
        "max_memory_mb": 4096,
        "max_execution_time": 300,
        "max_file_size_mb": 100
    }
)
```

## 安全最佳實踐

### 1. 最小權限原則

```python
agent_permissions = {
    "web_surfer": ["read_web"],
    "file_surfer": ["read_file", "write_file"],
    "coder": ["execute_code"],
    "terminal": []  # 默認禁用
}
```

### 2. 操作審核

```python
def approval_handler(operation, details):
    print(f"請求批准：{operation}")
    print(f"詳情：{details}")
    return input("批准？(y/n): ").lower() == 'y'

magentic_one.set_approval_handler(approval_handler)
```

### 3. 沙盒執行

```python
coder_config = {
    "use_docker": True,
    "docker_image": "python:3.11-slim",
    "network": "none",  # 禁用網絡
    "readonly_paths": ["/etc", "/usr"]
}
```

## 監控和調試

### 1. 日誌配置

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('magentic_one.log'),
        logging.StreamHandler()
    ]
)
```

### 2. 執行追蹤

```python
magentic_one.enable_trace(
    output_file="execution_trace.json",
    include_messages=True,
    include_state=True
)
```

### 3. 性能指標

```python
metrics = magentic_one.get_metrics()
print(f"任務完成時間: {metrics['duration']}")
print(f"LLM 調用次數: {metrics['llm_calls']}")
print(f"總 Token 使用: {metrics['total_tokens']}")
```

## 與 AutoGen 的區別

| 特性 | AutoGen | Magentic-One |
|------|---------|--------------|
| 定位 | 通用多 Agent 框架 | 任務導向系統 |
| Agent 類型 | 需自行定義 | 預定義專門 Agent |
| 協調機制 | 需手動配置 | 內置 Orchestrator |
| 任務處理 | 對話驅動 | 目標驅動 |
| 複雜度 | 靈活但複雜 | 開箱即用 |
| 適用場景 | 研究和定制 | 實際應用 |

## 故障排除

### 常見問題

**1. Agent 無法啟動**
- 檢查 API 密鑰是否正確
- 確認依賴包已安裝
- 查看錯誤日誌

**2. 任務執行超時**
- 增加超時時間限制
- 簡化任務複雜度
- 檢查網絡連接

**3. 代碼執行失敗**
- 啟用 Docker 沙盒
- 檢查依賴是否安裝
- 查看執行日誌

**4. 網頁瀏覽錯誤**
- 確認 Playwright 已安裝
- 檢查目標網站是否可訪問
- 嘗試非無頭模式調試

## 資源鏈接

- [官方文檔](https://microsoft.github.io/autogen/docs/topics/magentic-one/)
- [GitHub 倉庫](https://github.com/microsoft/autogen)
- [論文](https://arxiv.org/abs/2411.04468)
- [示例集合](https://github.com/microsoft/autogen/tree/main/samples/magentic-one)
- [社區論壇](https://github.com/microsoft/autogen/discussions)

## 學習路徑

1. **入門** (1-2 天)
   - 安裝和配置
   - 運行基礎範例
   - 理解核心概念

2. **進階** (1 週)
   - 學習各個 Agent 的能力
   - 嘗試不同協作模式
   - 自定義配置

3. **高級** (2-4 週)
   - 創建自定義 Agent
   - 設計複雜工作流
   - 優化性能和安全

4. **專家** (持續)
   - 貢獻開源項目
   - 研究新應用場景
   - 分享最佳實踐

## 範例文件說明

- `01_架構概述.py` - Magentic-One 整體架構和組件
- `02_Orchestrator.py` - 任務協調和規劃
- `03_WebSurfer.py` - 網頁瀏覽和信息提取
- `04_FileSurfer.py` - 文件操作和處理
- `05_Coder.py` - 代碼生成和執行
- `06_ComputerTerminal.py` - 系統命令執行
- `07_團隊協作.py` - 多 Agent 協同工作
- `08_複雜任務.py` - 端到端複雜任務處理
- `09_自定義Agent.py` - 擴展自定義 Agent
- `10_安全配置.py` - 安全機制和權限管理
- `11_與AutoGen對比.py` - 與基礎 AutoGen 的對比

## 貢獻指南

歡迎貢獻新範例和改進！請遵循以下步驟：

1. Fork 倉庫
2. 創建功能分支
3. 添加範例和文檔
4. 提交 Pull Request

## 授權

本專案採用 MIT 授權條款。

---

**注意**: Magentic-One 仍在積極開發中，API 可能會有變化。請參考官方文檔獲取最新信息。
