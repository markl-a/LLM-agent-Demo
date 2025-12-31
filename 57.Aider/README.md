# Aider - 終端 AI 編程助手

## 框架介紹

Aider 是一個強大的終端基礎 AI 編程助手，專為開發者設計，能夠直接在命令行中與 AI 協作編寫代碼。它不僅僅是一個簡單的代碼生成工具，而是一個完整的 AI 配對編程解決方案，支援多文件編輯、版本控制整合、語音編程等高級功能。

### 核心特色

Aider 將 AI 助手無縫整合到開發工作流程中，讓開發者可以：
- 使用自然語言描述需求，AI 自動生成和修改代碼
- 在多個文件之間進行協調的修改
- 自動管理 Git 提交歷史
- 支援語音輸入進行免手動編程
- 與多種大型語言模型（LLM）後端協作

### 技術架構

Aider 採用模組化架構，核心組件包括：
- **命令行介面（CLI）**：提供直觀的終端交互體驗
- **多模型支援**：支援 OpenAI、Anthropic、Google 等多種 LLM 提供商
- **Git 整合層**：自動化版本控制操作
- **上下文管理器**：智能管理代碼上下文，優化 Token 使用
- **語音識別模組**：支援語音輸入和輸出

## 主要功能

### 1. 多文件編輯

Aider 能夠同時處理多個文件的修改，保持代碼一致性：
- 自動識別相關文件
- 跨文件重構支援
- 智能依賴追蹤
- 批量修改操作

### 2. Git 整合

深度整合 Git 版本控制系統：
- 自動創建有意義的提交訊息
- 支援分支操作
- 變更歷史追蹤
- 衝突解決輔助
- 回滾和撤銷操作

### 3. 語音編程

支援語音輸入，提升編程效率：
- 語音轉文字
- 語音命令執行
- 多語言語音支援
- 文字轉語音回饋

### 4. 智能上下文管理

優化大型代碼庫的處理：
- 自動選擇相關代碼片段
- Token 使用優化
- 增量上下文更新
- Repository map 生成

### 5. 多模型支援

靈活切換不同的 AI 模型：
- OpenAI GPT-4, GPT-3.5
- Anthropic Claude 3.5 Sonnet, Opus
- Google PaLM
- 本地模型支援（通過 Ollama）
- 自定義 API 端點

## 安裝指南

### 系統要求

- Python 3.8 或更高版本
- Git 2.0 或更高版本
- 穩定的網路連接（用於 API 調用）
- API 金鑰（OpenAI、Anthropic 等）

### 基本安裝

使用 pip 安裝 Aider：

```bash
pip install aider-chat
```

### 從源碼安裝

```bash
git clone https://github.com/paul-gauthier/aider.git
cd aider
pip install -e .
```

### 安裝額外依賴

如果需要語音功能：

```bash
pip install aider-chat[voice]
```

### 配置 API 金鑰

設定環境變數：

```bash
# OpenAI
export OPENAI_API_KEY="your-api-key-here"

# Anthropic Claude
export ANTHROPIC_API_KEY="your-api-key-here"
```

或在專案目錄創建 `.env` 文件：

```
OPENAI_API_KEY=your-api-key-here
ANTHROPIC_API_KEY=your-api-key-here
```

## 快速開始

### 基本使用

1. **啟動 Aider**

在專案目錄中執行：

```bash
aider
```

2. **添加文件到會話**

```bash
aider main.py utils.py
```

3. **開始編程對話**

```
> 請在 main.py 中添加一個計算斐波那契數列的函數
```

Aider 會自動修改文件並顯示變更。

4. **審查和應用變更**

```
> /diff  # 查看變更
> /commit  # 提交到 Git
```

### 互動式會話範例

```bash
# 啟動 Aider 並添加文件
$ aider src/app.py src/utils.py

Aider v0.65.0
Model: gpt-4-turbo
Git repo: /path/to/project
Added src/app.py src/utils.py to the chat

> 請幫我重構 app.py 中的 process_data 函數，使用更清晰的變數命名

# Aider 會分析代碼並提出修改建議
# 顯示 diff 並詢問是否應用

> 看起來不錯，請同時更新 utils.py 中的相關函數

# Aider 會協調修改兩個文件

> /commit 重構 process_data 函數以提升可讀性

# 自動創建 Git 提交
```

### 命令列選項

```bash
# 指定模型
aider --model gpt-4-turbo

# 使用 Claude
aider --model claude-3-5-sonnet-20241022

# 啟用語音模式
aider --voice-language zh-TW

# 自動提交
aider --auto-commits

# 只讀模式（不修改文件）
aider --read

# 指定 repository map
aider --map-tokens 1024
```

## 使用案例

### 案例 1：新功能開發

**場景**：為 Web 應用添加用戶認證功能

```bash
$ aider src/auth.py src/models.py src/routes.py

> 請實現一個完整的用戶認證系統，包括：
> 1. User 模型（使用 SQLAlchemy）
> 2. 註冊和登入路由
> 3. JWT token 生成和驗證
> 4. 密碼加密（使用 bcrypt）
```

Aider 會：
- 在 `models.py` 中創建 User 模型
- 在 `auth.py` 中實現認證邏輯
- 在 `routes.py` 中添加 API 端點
- 自動處理依賴和導入

### 案例 2：Bug 修復

**場景**：修復生產環境中的錯誤

```bash
$ aider src/payment.py tests/test_payment.py

> 用戶報告說在處理退款時會出現 KeyError。
> 請檢查 payment.py 中的 process_refund 函數並修復這個問題。
> 同時添加測試確保問題不會再次出現。
```

Aider 會：
- 分析 `process_refund` 函數
- 識別潛在的 KeyError 來源
- 添加適當的錯誤處理
- 在測試文件中添加覆蓋此場景的測試

### 案例 3：代碼重構

**場景**：改善代碼品質和架構

```bash
$ aider src/*.py

> 請重構這個專案以遵循 SOLID 原則：
> 1. 將大型類拆分為更小的、單一職責的類
> 2. 使用依賴注入代替硬編碼依賴
> 3. 添加抽象層以提高可測試性
```

Aider 會：
- 分析整個代碼庫
- 識別重構機會
- 系統性地重組代碼
- 保持功能完整性

### 案例 4：測試生成

**場景**：為現有代碼添加測試覆蓋

```bash
$ aider src/calculator.py tests/test_calculator.py

> 請為 calculator.py 中的所有函數創建全面的單元測試，
> 包括邊界條件和錯誤處理測試。
```

Aider 會：
- 分析 calculator.py 中的所有函數
- 生成對應的測試案例
- 包括正常情況和異常情況
- 確保測試覆蓋率

### 案例 5：文件轉換

**場景**：將專案從 JavaScript 遷移到 TypeScript

```bash
$ aider src/*.js

> 請將這些 JavaScript 文件轉換為 TypeScript，
> 添加適當的類型註解和介面定義。
```

Aider 會：
- 逐個轉換 .js 文件為 .ts
- 添加類型定義
- 創建必要的介面和類型
- 處理類型相關的錯誤

### 案例 6：API 整合

**場景**：整合第三方 API 服務

```bash
$ aider src/services/stripe.py src/models/payment.py

> 請整合 Stripe 支付 API，實現：
> 1. 創建支付意圖
> 2. 處理 webhook 事件
> 3. 訂閱管理
> 4. 錯誤處理和重試邏輯
```

### 案例 7：性能優化

**場景**：優化慢速查詢和演算法

```bash
$ aider src/database.py src/queries.py

> 這個查詢在大型數據集上很慢。
> 請優化 get_user_statistics 函數，
> 使用更有效的 SQL 查詢和適當的索引建議。
```

### 案例 8：文檔生成

**場景**：為代碼添加文檔

```bash
$ aider src/api.py

> 請為所有函數添加詳細的 docstring，
> 包括參數說明、返回值、異常和使用範例。
> 使用 Google 風格的 docstring 格式。
```

## 進階功能

### Repository Map

Aider 自動生成代碼庫地圖，幫助 AI 理解專案結構：

```bash
# 調整 map tokens 大小
aider --map-tokens 2048
```

### 架構師模式

使用架構師模式進行大規模重構：

```bash
aider --architect
```

### 批處理模式

使用腳本自動化多個任務：

```bash
aider --yes --message "實現用戶認證" src/*.py
```

### 自定義提示詞

創建 `.aider.conf.yml` 配置文件：

```yaml
model: gpt-4-turbo
auto-commits: true
dirty-commits: false
attribute-author: true
attribute-committer: true
attribute-commit-message-author: true
attribute-commit-message-committer: true
```

## 最佳實踐

### 1. 明確的指令

提供清晰、具體的需求描述：

```
✅ 好的指令：
"請在 User 類中添加一個 email_verified 布林欄位，
並創建一個 send_verification_email 方法"

❌ 不好的指令：
"添加郵件驗證"
```

### 2. 增量開發

將大型任務分解為小步驟：

```
1. 首先創建基本的資料模型
2. 然後添加驗證邏輯
3. 接著實現 API 端點
4. 最後添加測試
```

### 3. 及時審查

定期檢查 Aider 的修改：

```bash
> /diff  # 查看變更
> /undo  # 如果需要撤銷
```

### 4. 使用 Git

充分利用 Git 整合：

```bash
> /commit 描述性的提交訊息
> /diff  # 查看未提交的變更
```

### 5. 上下文管理

只添加相關文件到會話：

```bash
# 好的做法
aider src/auth.py src/models.py

# 避免
aider src/**/*.py  # 太多文件會浪費 tokens
```

## 常見問題

### Q: Aider 支援哪些編程語言？

A: Aider 支援所有主流編程語言，包括 Python、JavaScript、TypeScript、Java、C++、Go、Rust 等。

### Q: 如何處理大型代碼庫？

A: 使用 repository map 功能和選擇性添加文件。只將需要修改的文件添加到會話中。

### Q: Aider 會覆蓋我的代碼嗎？

A: Aider 在修改前會顯示 diff，你可以選擇接受或拒絕變更。建議始終使用 Git 以便回滾。

### Q: 可以離線使用嗎？

A: 可以使用本地模型（通過 Ollama），但功能可能受限。

### Q: 如何控制成本？

A: 使用較小的模型（如 GPT-3.5）、限制上下文大小、使用 `--map-tokens` 參數。

## 資源連結

- **官方網站**：https://aider.chat
- **GitHub 儲存庫**：https://github.com/paul-gauthier/aider
- **文檔**：https://aider.chat/docs/
- **Discord 社群**：https://discord.gg/Tv2uQnR4jq
- **示例影片**：https://aider.chat/examples/

## 授權

Aider 採用 Apache 2.0 授權。

## 貢獻

歡迎貢獻！請查看 [CONTRIBUTING.md](https://github.com/paul-gauthier/aider/blob/main/CONTRIBUTING.md) 了解詳情。

---

**更新日期**：2025-12-31
**版本**：0.65.0
