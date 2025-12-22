# Goose - 開發者優先的 AI Agent

<div align="center">

![Goose Logo](https://img.shields.io/badge/Block-Goose-0066cc?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-Apache--2.0-green?style=for-the-badge)

**由 Block 開發的開發者優先 AI Agent**

[官方倉庫](https://github.com/block/goose) | [文檔](https://block.github.io/goose/) | [示例代碼](./02_基礎使用.py)

</div>

---

## 📚 目錄

- [簡介](#-簡介)
- [核心特點](#-核心特點)
- [安裝方式](#-安裝方式)
- [快速開始](#-快速開始)
- [核心概念](#-核心概念)
- [詳細教程](#-詳細教程)
- [實際應用場景](#-實際應用場景)
- [框架對比](#-框架對比)
- [最佳實踐](#-最佳實踐)
- [常見問題](#-常見問題)
- [參考資源](#-參考資源)

---

## 🎯 簡介

### 什麼是 Goose？

**Goose** 是由 **Block**（原 Square）開發的開發者優先 AI Agent，也是 **Agentic AI Foundation (AAIF)** 的創始項目之一。Goose 專注於幫助開發者完成軟件開發任務，從代碼編寫到調試，從代碼審查到文檔生成。

### 為什麼選擇 Goose？

與傳統的 AI 編程助手不同，Goose 是一個**完整的 AI Agent**，而非僅僅是代碼補全工具：

- **開發者優先**：專為軟件開發工作流設計
- **Agent 架構**：自主決策和執行能力
- **工具集成**：與開發工具無縫整合
- **多模型支持**：支持多種 LLM 提供商
- **可擴展性**：豐富的工具系統和插件機制
- **命令行友好**：高效的 CLI 界面

### Goose 的核心理念

1. **AI 助手應該理解開發者的工作流**
2. **AI 應該能夠自主執行任務，而非僅提供建議**
3. **開發者體驗至上**
4. **開源和社區驅動**

### 適用場景

✅ **適合**：
- 日常軟件開發任務
- 代碼審查和重構
- Bug 調試和修復
- 文檔生成和維護
- 項目架構設計
- 學習新技術和框架

❌ **不適合**：
- 需要 100% 準確性的關鍵任務
- 完全替代人類開發者
- 不需要開發工具的場景

---

## ⭐ 核心特點

### 1. 智能任務理解

```bash
# Goose 理解自然語言指令
$ goose "幫我重構這個函數，使其更易讀"
$ goose "找出為什麼測試失敗了"
$ goose "為這個 API 生成文檔"
```

### 2. 自主執行能力

Goose 不只是建議，而是**真正執行**：

- 讀取和修改文件
- 運行測試和構建
- 執行 shell 命令
- 與 git 互動
- 調用開發工具

### 3. 上下文感知

```python
# Goose 理解項目上下文
- 項目結構和依賴
- 代碼風格和慣例
- 現有架構模式
- 團隊編碼規範
```

### 4. 多模型支持

支持多種 LLM 提供商：

- **OpenAI**: GPT-4, GPT-4 Turbo
- **Anthropic**: Claude 3 系列
- **Google**: Gemini Pro
- **本地模型**: Ollama, LM Studio
- **Azure OpenAI**
- **其他**: 可通過插件擴展

### 5. 豐富的工具系統

內建工具：
- 文件操作（讀、寫、搜索）
- Shell 命令執行
- Git 操作
- Web 搜索
- 代碼分析
- 測試運行

自定義工具：
- Python 函數轉工具
- Shell 腳本集成
- API 調用封裝

### 6. 會話管理

```bash
# 保存和恢復會話
$ goose session save my-refactor
$ goose session load my-refactor
$ goose session list
```

---

## 🚀 安裝方式

### 方法 1: pipx（推薦）

```bash
# 安裝 pipx（如果尚未安裝）
python -m pip install --user pipx
python -m pipx ensurepath

# 安裝 Goose
pipx install goose-ai

# 驗證安裝
goose --version
```

### 方法 2: Homebrew（macOS/Linux）

```bash
# 添加 Block tap
brew tap block/tap

# 安裝 Goose
brew install goose

# 驗證安裝
goose --version
```

### 方法 3: pip

```bash
# 創建虛擬環境（推薦）
python -m venv goose-env
source goose-env/bin/activate  # Windows: goose-env\Scripts\activate

# 安裝
pip install goose-ai

# 驗證
goose --version
```

### 方法 4: 從源碼安裝

```bash
# 克隆倉庫
git clone https://github.com/block/goose.git
cd goose

# 安裝
pip install -e .

# 驗證
goose --version
```

---

## 🏃 快速開始

### 1. 初始化配置

```bash
# 初始化 Goose 配置
goose init

# 這會創建 ~/.config/goose/config.yaml
```

### 2. 配置 API Key

```bash
# 設置 OpenAI API Key
export OPENAI_API_KEY='your-api-key-here'

# 或使用 Anthropic Claude
export ANTHROPIC_API_KEY='your-api-key-here'

# 永久設置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.bashrc
```

### 3. 第一次使用

```bash
# 啟動 Goose
goose

# 在交互式界面中輸入任務
> 你好，請介紹一下你自己

# 退出
> exit
```

### 4. 直接執行任務

```bash
# 命令行模式
goose "創建一個 Python 腳本，計算斐波那契數列"

# 在特定目錄中執行
cd /path/to/project
goose "分析這個項目的結構"
```

### 5. 使用會話

```bash
# 開始新會話
goose session new code-review

# 恢復會話
goose session resume code-review

# 查看會話列表
goose session list
```

---

## 🧩 核心概念

### 1. Agent 架構

Goose 採用 Agent 架構，包含三個核心組件：

```
┌─────────────────────────────────────┐
│          Goose Agent                │
│                                     │
│  ┌──────────┐  ┌──────────┐       │
│  │   LLM    │  │  Tools   │       │
│  │  Engine  │←→│  System  │       │
│  └──────────┘  └──────────┘       │
│       ↑              ↑             │
│       └──────┬───────┘             │
│              │                     │
│      ┌───────▼────────┐            │
│      │   Controller   │            │
│      └────────────────┘            │
└─────────────────────────────────────┘
```

**組件說明**：
- **LLM Engine**: 語言模型推理引擎
- **Tools System**: 工具調用和執行系統
- **Controller**: 協調和控制邏輯

### 2. 工具（Tools）

工具是 Goose 與環境互動的方式：

```python
# 工具定義範例
class FileTool:
    def read_file(self, path: str) -> str:
        """讀取文件內容"""
        with open(path, 'r') as f:
            return f.read()

    def write_file(self, path: str, content: str) -> str:
        """寫入文件"""
        with open(path, 'w') as f:
            f.write(content)
        return f"已寫入 {path}"
```

**內建工具類別**：
- **文件工具**: 讀寫、搜索、修改文件
- **Shell 工具**: 執行命令、運行腳本
- **Git 工具**: 提交、分支、合併
- **分析工具**: 代碼分析、依賴檢查
- **Web 工具**: 搜索、獲取文檔

### 3. 會話（Sessions）

會話保存了對話歷史和上下文：

```bash
# 會話結構
~/.config/goose/sessions/
├── my-project-20240115/
│   ├── messages.json      # 消息歷史
│   ├── context.json       # 上下文信息
│   └── metadata.json      # 會話元數據
```

**會話特性**：
- 持久化對話歷史
- 保存項目上下文
- 支持暫停和恢復
- 多會話並存

### 4. 提供商（Providers）

支持多種 LLM 提供商：

```yaml
# config.yaml
provider:
  type: openai
  model: gpt-4-turbo-preview
  api_key: ${OPENAI_API_KEY}

# 或使用 Anthropic
provider:
  type: anthropic
  model: claude-3-opus-20240229
  api_key: ${ANTHROPIC_API_KEY}
```

### 5. 插件系統

擴展 Goose 功能：

```python
# 自定義插件範例
from goose.plugin import Plugin

class MyPlugin(Plugin):
    name = "my_plugin"

    def load(self):
        """加載插件"""
        self.register_tool("my_tool", self.my_tool)

    def my_tool(self, arg: str) -> str:
        """自定義工具"""
        return f"處理: {arg}"
```

---

## 📖 詳細教程

本目錄包含完整的教程和示例：

### 安裝和配置
1. **[安裝配置](01_安裝配置.md)** - 詳細安裝指南、環境配置、故障排除

### 基礎使用 (2-4)
2. **[基礎使用](02_基礎使用.py)** - CLI 命令、交互模式、基本操作
3. **[開發任務](03_開發任務.py)** - 代碼生成、重構、調試輔助
4. **[代碼審查](04_代碼審查.py)** - 自動審查、問題檢測、改進建議

### 進階功能 (5-7)
5. **[自定義工具](05_自定義工具.py)** - 創建工具、集成 API、擴展能力
6. **[配置文件](06_配置文件.py)** - 配置詳解、個性化設置、團隊配置
7. **[多模型支持](07_多模型支持.py)** - 切換模型、比較性能、混合使用

### 實戰應用 (8-9)
8. **[工作流自動化](08_工作流自動化.py)** - 自動化任務、CI/CD 集成、腳本化
9. **[與 IDE 整合](09_與IDE整合.py)** - VS Code 插件、JetBrains 集成、編輯器配置

---

## 🎨 實際應用場景

### 場景 1：快速原型開發

```bash
# 創建一個完整的 Web API
$ goose "創建一個 FastAPI 項目，包含用戶認證和 CRUD 操作"

# Goose 會：
# 1. 創建項目結構
# 2. 生成 API 代碼
# 3. 添加測試
# 4. 生成文檔
# 5. 設置依賴
```

### 場景 2：代碼審查助手

```bash
# 審查最新的提交
$ goose "審查最新的 commit，檢查潛在問題"

# 審查特定文件
$ goose "審查 src/auth.py，關注安全問題"

# 審查 PR
$ goose "審查 PR #123，提供改進建議"
```

### 場景 3：Bug 調試

```bash
# 診斷測試失敗
$ goose "運行測試並找出失敗原因"

# 分析錯誤日誌
$ goose "分析 error.log，找出根本原因"

# 修復 Bug
$ goose "修復 issue #456 中描述的 bug"
```

### 場景 4：重構代碼

```bash
# 重構函數
$ goose "重構 utils.py 中的 process_data 函數"

# 提取共用邏輯
$ goose "找出重複代碼並提取到共用模塊"

# 應用設計模式
$ goose "將這個類重構為策略模式"
```

### 場景 5：文檔生成

```bash
# 生成 API 文檔
$ goose "為所有 API 端點生成 OpenAPI 文檔"

# 添加函數文檔
$ goose "為 src/ 目錄下所有函數添加 docstring"

# 生成 README
$ goose "為這個項目生成詳細的 README.md"
```

### 場景 6：學習新技術

```bash
# 學習框架
$ goose "教我如何使用 React Hooks，並創建示例"

# 理解代碼庫
$ goose "解釋這個項目的架構，並創建架構圖"

# 最佳實踐
$ goose "審查代碼並建議符合 Python PEP 8 的改進"
```

---

## 🔄 框架對比

### Goose vs GitHub Copilot vs Cursor

| 特性 | Goose | GitHub Copilot | Cursor |
|------|-------|----------------|--------|
| **類型** | AI Agent | 代碼補全 | AI IDE |
| **自主執行** | ✅ 完全自主 | ❌ 僅建議 | ⚠️ 部分自主 |
| **工具調用** | ✅ 豐富工具集 | ❌ 無 | ⚠️ 有限 |
| **CLI 界面** | ✅ 優秀 | ❌ 無 | ❌ 無 |
| **多模型** | ✅ 支持 | ❌ 固定 | ✅ 支持 |
| **開源** | ✅ 是 | ❌ 否 | ❌ 否 |
| **定價** | 免費（需 API） | 訂閱制 | 訂閱制 |
| **適用場景** | 任務執行 | 代碼編寫 | 編輯器內開發 |

### Goose vs AutoGPT vs MetaGPT

| 特性 | Goose | AutoGPT | MetaGPT |
|------|-------|---------|---------|
| **專注領域** | 軟件開發 | 通用任務 | 軟件工程 |
| **開發者體驗** | ✅ 優秀 | ⚠️ 一般 | ⚠️ 一般 |
| **易用性** | ✅ 簡單 | ⚠️ 複雜 | ⚠️ 複雜 |
| **工具集成** | ✅ 深度集成 | ⚠️ 基礎 | ✅ 豐富 |
| **會話管理** | ✅ 優秀 | ⚠️ 基礎 | ⚠️ 基礎 |
| **生產就緒** | ✅ 是 | ❌ 實驗性 | ⚠️ 發展中 |

### 選擇建議

**選擇 Goose 當**：
- 主要工作是軟件開發
- 需要 AI Agent 自主執行任務
- 偏好命令行界面
- 想要開源和可定制的解決方案

**選擇 Copilot 當**：
- 主要需要代碼補全
- 在 IDE 中工作
- 不需要自主執行能力

**選擇 Cursor 當**：
- 需要 AI 增強的 IDE
- 喜歡編輯器內的體驗
- 願意付費訂閱

---

## 💡 最佳實踐

### 1. 清晰的任務描述

```bash
# ✅ 好的描述
$ goose "重構 src/auth.py 的 login 函數，提高可讀性並添加錯誤處理"

# ❌ 模糊的描述
$ goose "改進代碼"
```

### 2. 提供上下文

```bash
# ✅ 提供足夠上下文
$ goose "這是一個 Django 項目，幫我添加用戶認證功能，使用 JWT token"

# ❌ 缺乏上下文
$ goose "添加認證"
```

### 3. 分步驟執行

```bash
# ✅ 分解任務
$ goose "第一步：創建用戶模型"
$ goose "第二步：創建註冊 API"
$ goose "第三步：添加測試"

# ❌ 一次性大任務
$ goose "創建完整的用戶系統"
```

### 4. 審查 AI 輸出

```python
# 總是審查 AI 生成的代碼
# 特別注意：
- 安全性問題
- 邊界情況處理
- 錯誤處理
- 性能影響
```

### 5. 使用會話

```bash
# 長期項目使用會話
$ goose session new my-feature
> 開始開發新功能

# 稍後繼續
$ goose session resume my-feature
> 繼續之前的工作
```

### 6. 配置項目特定設置

```yaml
# .goose/config.yaml（項目根目錄）
project:
  name: my-app
  language: python
  framework: django

preferences:
  code_style: pep8
  test_framework: pytest
  documentation: google_style
```

### 7. 版本控制

```bash
# 在使用 Goose 前提交變更
$ git add .
$ git commit -m "保存當前狀態"

# 使用 Goose
$ goose "重構代碼"

# 審查變更
$ git diff

# 如果滿意，提交
$ git commit -m "AI 輔助重構"
```

---

## ❓ 常見問題

### Q1: Goose 需要聯網嗎？

**A**: 取決於使用的模型：
- **雲端模型**（OpenAI, Anthropic）：需要聯網
- **本地模型**（Ollama）：可以完全離線使用

### Q2: Goose 會修改我的代碼嗎？

**A**: Goose 只在你授權時才會修改代碼。建議：
- 使用 git 版本控制
- 審查所有變更
- 使用會話功能暫停和恢復

### Q3: 如何切換不同的 LLM？

**A**:
```bash
# 臨時切換
$ goose --model gpt-4 "執行任務"

# 永久切換（修改配置文件）
$ goose config set provider.model claude-3-opus-20240229
```

### Q4: Goose 支持哪些編程語言？

**A**: Goose 支持所有主流編程語言，包括：
- Python, JavaScript/TypeScript
- Java, C++, Go, Rust
- Ruby, PHP, Swift, Kotlin
- 以及更多...

### Q5: 如何限制 Goose 的權限？

**A**:
```yaml
# config.yaml
permissions:
  allow_file_write: true
  allow_shell_exec: false  # 禁止執行 shell 命令
  allowed_directories:
    - /path/to/project
  blocked_files:
    - "*.env"
    - "secrets.*"
```

### Q6: Goose 的成本如何？

**A**: Goose 本身免費開源，但需要 LLM API：
- **OpenAI**: 按 token 計費
- **Anthropic**: 按 token 計費
- **本地模型**: 免費（需要計算資源）

### Q7: 如何提高 Goose 的響應速度？

**A**:
```yaml
# 使用更快的模型
provider:
  model: gpt-3.5-turbo  # 而非 gpt-4

# 限制上下文長度
context:
  max_tokens: 4000

# 啟用緩存
cache:
  enabled: true
```

### Q8: Goose 可以訪問互聯網嗎？

**A**: 可以，通過 Web 搜索工具：
```bash
$ goose "搜索 Python 3.12 的新特性並總結"
```

---

## 📚 參考資源

### 官方資源

- [Goose GitHub](https://github.com/block/goose)
- [官方文檔](https://block.github.io/goose/)
- [AAIF 官網](https://agenticaifoundation.org/)
- [Block 技術博客](https://developer.block.xyz/)

### 相關項目

- [Aider](https://github.com/paul-gauthier/aider) - AI 結對編程
- [GPT Engineer](https://github.com/AntonOsika/gpt-engineer)
- [Sweep](https://github.com/sweepai/sweep) - AI 代碼審查

### 社區

- [Discord 社區](https://discord.gg/goose-ai)
- [GitHub Discussions](https://github.com/block/goose/discussions)
- [Stack Overflow Tag](https://stackoverflow.com/questions/tagged/goose-ai)

### 學習資源

- [AI Agent 設計模式](https://www.deeplearning.ai/)
- [LLM 應用開發](https://www.coursera.org/)
- [提示工程指南](https://www.promptingguide.ai/)

---

## 🎓 總結

### 核心要點

1. **Goose 是開發者的 AI 助手**：專為軟件開發設計
2. **Agent 架構**：自主決策和執行能力
3. **開源和可擴展**：完全控制和定制
4. **多模型支持**：靈活選擇 LLM

### 何時使用 Goose

- ✅ 日常開發任務自動化
- ✅ 代碼審查和重構
- ✅ 學習新技術和框架
- ✅ 快速原型開發
- ✅ Bug 調試和修復

### 下一步

1. **安裝 Goose**：參考[安裝配置](01_安裝配置.md)
2. **運行示例**：`python 02_基礎使用.py`
3. **探索功能**：嘗試不同的開發任務
4. **自定義配置**：根據需求調整設置

---

## 📝 許可證

本教程基於 MIT 許可證開源。

Goose 採用 Apache 2.0 許可證。

---

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

---

<div align="center">

**Happy Coding with Goose!** 🪿

Made with ❤️ by AI Enthusiasts

</div>
