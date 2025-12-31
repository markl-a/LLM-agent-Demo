# Agent S - 電腦使用 Agent 框架

## 框架簡介

Agent S 是由 Simular AI 開發的開源 Agentic 框架，專門用於構建能夠像人類一樣使用電腦的自主 Agent。該框架在 ICLR 2025 被接受，並在 OSWorld 基準測試中達到了 **72.60%** 的成功率，**超越人類水平** (72.36%)。

### 核心特點

#### 1. Agent-Computer Interface (ACI)
- 統一的電腦操作接口
- 支持滑鼠點擊、鍵盤輸入、螢幕截圖
- 跨平台支持（Windows、macOS、Linux）

#### 2. 經驗增強的階層式規劃
- **外部知識搜索**：從網路和文檔檢索相關信息
- **內部經驗檢索**：從過往成功案例學習
- **多層次規劃**：高層任務分解 + 低層操作執行

#### 3. 三代演進
| 版本 | OSWorld 分數 | 主要改進 |
|------|-------------|---------|
| Agent S | 20.6% | 基礎版本 |
| Agent S2 | 34.5% | 模組化設計 |
| Agent S3 | 72.6% | 原生代碼 Agent + bBoN |

#### 4. 支持的模型
- Azure OpenAI (GPT-4V)
- Anthropic (Claude 3)
- Google Gemini
- Open Router
- vLLM (本地部署)
- UI-TARS-1.5-7B (推薦)

### 適用場景

- **桌面自動化**：自動完成重複性電腦任務
- **軟體測試**：自動化 UI 測試和驗證
- **數據輸入**：批量處理表單和文檔
- **工作流自動化**：跨應用程序的複雜工作流
- **研究助手**：網頁瀏覽和信息收集

## 安裝方式

### 方法一：使用 pip 安裝

```bash
# 基礎安裝
pip install agent-s

# 完整安裝（包含所有依賴）
pip install "agent-s[all]"
```

### 方法二：從源碼安裝

```bash
# 克隆倉庫
git clone https://github.com/simular-ai/Agent-S.git
cd Agent-S

# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴
pip install -e .
```

### 方法三：使用 Docker

```bash
# 使用官方 Docker 鏡像
docker pull simularai/agent-s:latest
docker run -it simularai/agent-s:latest
```

## 環境配置

### 1. API Keys 設置

創建 `.env` 文件：

```bash
# OpenAI / Azure OpenAI
OPENAI_API_KEY=your_openai_key
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
AZURE_OPENAI_API_KEY=your_azure_key

# Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_key

# Google Gemini
GOOGLE_API_KEY=your_google_key

# Open Router
OPENROUTER_API_KEY=your_openrouter_key
```

### 2. 螢幕和輸入權限

```bash
# macOS: 需要授予輔助功能權限
# 系統偏好設置 > 安全性與隱私 > 隱私 > 輔助功能

# Linux: 需要 X11 或 Wayland 權限
# Ubuntu/Debian
sudo apt-get install python3-xlib

# Windows: 通常不需要額外配置
```

## 範例檔案說明

本目錄包含 12 個完整的 Python 範例：

| 檔案 | 說明 | 難度 |
|------|------|------|
| `01_快速開始.py` | Agent S 基礎使用 | ⭐ |
| `02_螢幕操作.py` | 螢幕截圖和元素識別 | ⭐⭐ |
| `03_滑鼠鍵盤.py` | 滑鼠點擊和鍵盤輸入 | ⭐⭐ |
| `04_任務規劃.py` | 階層式任務規劃 | ⭐⭐⭐ |
| `05_經驗學習.py` | 從經驗中學習和改進 | ⭐⭐⭐ |
| `06_Web瀏覽.py` | 網頁瀏覽和操作 | ⭐⭐⭐ |
| `07_文件操作.py` | 文件管理和編輯 | ⭐⭐⭐ |
| `08_應用控制.py` | 控制桌面應用程序 | ⭐⭐⭐ |
| `09_多步任務.py` | 複雜多步驟任務 | ⭐⭐⭐⭐ |
| `10_錯誤恢復.py` | 錯誤處理和恢復 | ⭐⭐⭐⭐ |
| `11_自定義模型.py` | 使用自定義模型 | ⭐⭐⭐⭐ |
| `12_生產部署.py` | 生產環境部署 | ⭐⭐⭐⭐⭐ |

## 快速開始

```python
from agent_s import Agent, Task
from agent_s.models import OpenAIModel

# 初始化 Agent
agent = Agent(
    model=OpenAIModel("gpt-4-vision-preview"),
    enable_screen_capture=True,
    enable_mouse_keyboard=True
)

# 定義任務
task = Task(
    description="打開瀏覽器，搜索 'Agent S framework'，並保存第一個結果的標題"
)

# 執行任務
result = agent.run(task)
print(f"任務結果: {result}")
```

## 核心概念

### 1. Agent-Computer Interface (ACI)

```python
from agent_s.aci import ACI

# 創建 ACI 實例
aci = ACI()

# 螢幕操作
screenshot = aci.capture_screen()
elements = aci.detect_ui_elements(screenshot)

# 滑鼠操作
aci.click(x=100, y=200)
aci.double_click(x=100, y=200)
aci.right_click(x=100, y=200)
aci.drag(start=(100, 200), end=(300, 400))

# 鍵盤操作
aci.type_text("Hello World")
aci.press_key("enter")
aci.hotkey("ctrl", "c")
```

### 2. 階層式規劃

```python
from agent_s.planning import HierarchicalPlanner

planner = HierarchicalPlanner(
    high_level_model="gpt-4",
    low_level_model="gpt-4-vision-preview"
)

# 高層規劃：分解任務
high_level_plan = planner.plan_high_level(
    task="創建一個 PowerPoint 簡報，包含 5 張幻燈片"
)

# 低層執行：具體操作
for subtask in high_level_plan.subtasks:
    actions = planner.plan_low_level(subtask)
    for action in actions:
        result = aci.execute(action)
```

### 3. 經驗學習

```python
from agent_s.memory import ExperienceMemory

memory = ExperienceMemory()

# 記錄成功經驗
memory.add_experience(
    task="打開 Excel 並創建新工作表",
    actions=[...],
    success=True
)

# 檢索相似經驗
similar_experiences = memory.retrieve_similar(
    query="打開 Word 並創建新文檔",
    top_k=3
)
```

## 最佳實踐

### 1. 任務描述

```python
# ✅ 好的任務描述
task = Task(
    description="打開 Chrome 瀏覽器，訪問 gmail.com，登錄帳號 user@gmail.com",
    constraints=["不要關閉其他視窗", "使用英文界面"],
    timeout=120
)

# ❌ 避免的任務描述
task = Task(description="發郵件")  # 太模糊
```

### 2. 錯誤處理

```python
from agent_s.exceptions import AgentError, TimeoutError

try:
    result = agent.run(task, max_retries=3)
except TimeoutError:
    print("任務超時，嘗試簡化任務")
except AgentError as e:
    print(f"Agent 錯誤: {e}")
    agent.recover()
```

### 3. 安全考量

```python
agent = Agent(
    model=model,
    # 安全配置
    allowed_applications=["chrome", "word", "excel"],
    blocked_actions=["delete_files", "format_disk"],
    require_confirmation=True,  # 危險操作需要確認
    sandbox_mode=True  # 在沙盒環境中運行
)
```

## 性能基準

### OSWorld 測試結果

| 模型配置 | 準確率 | 平均步數 |
|---------|--------|---------|
| Agent S3 + GPT-4V | 72.60% | 8.3 |
| Agent S3 + Claude 3 | 68.5% | 9.1 |
| Agent S3 + UI-TARS | 69.2% | 7.8 |
| 人類基準 | 72.36% | 12.4 |

## 社群與資源

- **GitHub**: https://github.com/simular-ai/Agent-S
- **論文**: https://arxiv.org/abs/2410.08164
- **官網**: https://www.simular.ai
- **Discord**: Simular AI 社群

## 授權

Agent S 採用 Apache 2.0 開源授權。

---

**最後更新**: 2025-12
**框架版本**: Agent S3
**維護狀態**: 積極維護中 ✅
