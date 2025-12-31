# Cline - VS Code 自主編程助手

## 簡介

Cline 是一個開源的 VS Code 擴展，為開發者提供強大的自主編程助手功能。它不僅僅是一個代碼補全工具，而是一個能夠理解整個項目、規劃任務並自動執行的 AI 編程夥伴。

### 核心能力

1. **項目理解**
   - 讀取和分析整個代碼庫
   - 理解項目結構和依賴關係
   - 追蹤文件之間的關聯

2. **智能搜索**
   - 快速搜索文件內容
   - 語義化代碼搜索
   - 跨文件引用查找

3. **終端集成**
   - 執行終端命令
   - 運行測試和構建
   - 監控命令輸出

4. **自動編輯**
   - 自動修改代碼文件
   - 跨文件重構
   - 批量代碼更新

5. **任務規劃**
   - 將複雜任務分解為步驟
   - 制定執行計劃
   - 追蹤進度

## Plan 與 Act 雙模式

### Plan 模式（規劃模式）

在 Plan 模式下，Cline 會：
- 分析用戶的需求
- 制定詳細的執行計劃
- 列出需要修改的文件
- 說明每個步驟的目的
- **等待用戶確認後再執行**

適用場景：
- 複雜的重構任務
- 涉及多個文件的修改
- 需要謹慎處理的變更
- 學習和理解 AI 的思考過程

### Act 模式（執行模式）

在 Act 模式下，Cline 會：
- 直接執行任務
- 自動做出決策
- 快速完成簡單任務
- 在遇到問題時才詢問

適用場景：
- 簡單的代碼生成
- 常規的 Bug 修復
- 文檔編寫
- 測試用例生成

### 模式切換

```
/plan    # 切換到 Plan 模式
/act     # 切換到 Act 模式
```

## 支持的 LLM 提供商

Cline 支持多種 LLM 提供商，讓您可以選擇最適合的模型：

### 1. Anthropic Claude
- Claude 3.5 Sonnet（推薦）
- Claude 3 Opus
- Claude 3 Sonnet
- Claude 3 Haiku

**優勢**：
- 出色的代碼理解能力
- 長上下文窗口（200k tokens）
- 精確的代碼生成
- 更好的安全性

### 2. OpenAI
- GPT-4 Turbo
- GPT-4
- GPT-3.5 Turbo

**優勢**：
- 廣泛的知識庫
- 快速響應
- 成本相對較低（3.5 Turbo）

### 3. Google Gemini
- Gemini 1.5 Pro
- Gemini 1.5 Flash

**優勢**：
- 超長上下文（1M+ tokens）
- 多模態支持
- 免費額度

### 4. 開源模型
- Ollama（本地運行）
- LM Studio
- OpenRouter

**優勢**：
- 完全私密
- 無成本限制
- 可定制化

### 5. Azure OpenAI
- 企業級服務
- 數據隱私保證
- SLA 保障

## 與其他編程助手對比

| 功能 | Cline | GitHub Copilot | Cursor | Tabnine |
|------|-------|----------------|--------|---------|
| **代碼補全** | ✅ | ✅ | ✅ | ✅ |
| **項目理解** | ✅✅✅ | ✅ | ✅✅ | ✅ |
| **終端控制** | ✅✅✅ | ❌ | ✅✅ | ❌ |
| **文件編輯** | ✅✅✅ | ✅ | ✅✅ | ✅ |
| **任務規劃** | ✅✅✅ | ❌ | ✅ | ❌ |
| **多文件重構** | ✅✅✅ | ✅ | ✅✅ | ✅ |
| **開源** | ✅ | ❌ | ❌ | 部分 |
| **多 LLM 選擇** | ✅✅✅ | ❌ | ✅ | ✅ |
| **本地模型** | ✅ | ❌ | ❌ | ✅ |
| **價格** | 免費 | $10/月 | $20/月 | 免費/$12/月 |

### Cline 的獨特優勢

1. **完全開源**
   - 透明的代碼邏輯
   - 社區驅動開發
   - 可自定義和擴展

2. **自主決策能力**
   - 不只是補全，而是完整的任務執行
   - 可以讀取、搜索、修改文件
   - 可以運行命令和測試

3. **靈活的 LLM 選擇**
   - 不綁定特定提供商
   - 可以使用本地模型
   - 成本可控

4. **Plan 模式的透明度**
   - 清晰的執行計劃
   - 用戶完全控制
   - 學習 AI 的思考方式

## 安裝和配置

### 安裝步驟

1. **安裝 VS Code**
   ```bash
   # 確保已安裝 VS Code 1.84.0 或更高版本
   code --version
   ```

2. **安裝 Cline 擴展**
   - 打開 VS Code
   - 進入擴展市場（Ctrl+Shift+X）
   - 搜索 "Cline"
   - 點擊安裝

   或通過命令行：
   ```bash
   code --install-extension saoudrizwan.claude-dev
   ```

3. **配置 API 密鑰**

   打開 Cline 設置（Ctrl+Shift+P -> "Cline: Open Settings"）

   #### Anthropic Claude
   ```json
   {
     "cline.apiProvider": "anthropic",
     "cline.apiKey": "sk-ant-api03-...",
     "cline.model": "claude-3-5-sonnet-20241022"
   }
   ```

   #### OpenAI
   ```json
   {
     "cline.apiProvider": "openai",
     "cline.apiKey": "sk-...",
     "cline.model": "gpt-4-turbo-preview"
   }
   ```

   #### Ollama（本地）
   ```json
   {
     "cline.apiProvider": "ollama",
     "cline.ollamaBaseUrl": "http://localhost:11434",
     "cline.model": "codellama"
   }
   ```

### 基本使用

1. **打開 Cline 面板**
   - 點擊側邊欄的 Cline 圖標
   - 或使用快捷鍵：Ctrl+Shift+P -> "Cline: Open"

2. **開始對話**
   ```
   請幫我創建一個 Python 的 FastAPI 項目
   ```

3. **選擇模式**
   ```
   /plan    # 查看執行計劃
   /act     # 直接執行
   ```

4. **審查和確認**
   - Plan 模式：查看計劃後點擊 "Approve"
   - Act 模式：自動執行，可隨時中斷

### 高級配置

#### 自定義提示詞

創建 `.clinerules` 文件在項目根目錄：

```
# 項目特定規則
- 使用 TypeScript 嚴格模式
- 遵循 Airbnb 代碼風格
- 為所有公共 API 編寫 JSDoc
- 單元測試使用 Jest
- 提交信息遵循 Conventional Commits
```

#### 忽略文件

創建 `.clineignore` 文件：

```
node_modules/
.git/
dist/
build/
*.log
.env
```

#### 自定義快捷命令

在 VS Code `settings.json` 中：

```json
{
  "cline.customCommands": {
    "test": "npm test",
    "build": "npm run build",
    "lint": "npm run lint"
  }
}
```

## 最佳實踐

### 1. 明確的任務描述

❌ 不好的例子：
```
改進這個函數
```

✅ 好的例子：
```
重構 src/utils/parser.ts 中的 parseConfig 函數：
1. 添加錯誤處理
2. 提取重複邏輯到輔助函數
3. 添加 TypeScript 類型
4. 編寫單元測試
```

### 2. 使用 Plan 模式進行複雜任務

對於涉及多個文件或重大變更的任務，先使用 Plan 模式：

```
/plan
重構整個認證系統，從 JWT 遷移到 OAuth 2.0
```

### 3. 增量式開發

將大任務分解為小步驟：

```
步驟 1: 創建 OAuth 配置文件
步驟 2: 實現 OAuth 中間件
步驟 3: 更新登錄端點
步驟 4: 遷移現有用戶
步驟 5: 移除舊的 JWT 代碼
```

### 4. 利用項目上下文

在任務描述中引用項目文件：

```
參考 docs/architecture.md 中的設計，
在 src/services/ 中實現新的支付服務
```

### 5. 驗證和測試

每次變更後要求運行測試：

```
實現功能後，請運行 npm test 確保所有測試通過
```

## 常見問題

### Q: Cline 會收集我的代碼嗎？
A: 不會。Cline 是開源的，代碼只發送到您選擇的 LLM 提供商。您可以使用 Ollama 在本地運行，完全離線。

### Q: 如何限制 Cline 的權限？
A: 使用 `.clineignore` 文件排除敏感目錄，並在 Plan 模式下審查每個操作。

### Q: 支持哪些編程語言？
A: Cline 支持所有主流編程語言，依賴於底層 LLM 的能力。

### Q: 如何提高響應速度？
A: 使用更快的模型（如 Claude 3 Haiku 或 GPT-3.5 Turbo），或在本地運行 Ollama。

### Q: 可以在團隊中共享配置嗎？
A: 可以。將 `.clinerules` 和項目特定配置提交到版本控制，API 密鑰使用環境變量。

## 資源鏈接

- **GitHub**: https://github.com/cline/cline
- **VS Code 市場**: https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev
- **文檔**: https://github.com/cline/cline/wiki
- **Discord 社區**: https://discord.gg/cline
- **示例項目**: https://github.com/cline/examples

## 許可證

MIT License

## 貢獻

歡迎貢獻！請查看 [CONTRIBUTING.md](https://github.com/cline/cline/blob/main/CONTRIBUTING.md)

## 致謝

感謝所有為 Cline 做出貢獻的開發者和社區成員。

---

**注意**: 本目錄包含 Cline 的 Python SDK 使用示例，用於程序化地與 Cline 交互或構建自定義工具。
