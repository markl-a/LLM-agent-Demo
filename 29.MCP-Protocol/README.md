# Model Context Protocol (MCP) 完整教程

> AI 時代的「USB-C 接口」- 標準化 LLM 與工具、數據源的連接方式

## 目錄

- [專案概述](#專案概述)
- [MCP 簡介](#mcp-簡介)
- [核心優勢](#核心優勢)
- [架構設計](#架構設計)
- [教程結構](#教程結構)
- [快速開始](#快速開始)
- [生態系統](#生態系統)
- [最佳實踐](#最佳實踐)
- [常見問題](#常見問題)
- [參考資源](#參考資源)

---

## 專案概述

本目錄提供 **Model Context Protocol (MCP)** 的完整教學，從基礎概念到生產部署，幫助開發者快速掌握這個革命性的 AI 互操作性標準。

### 學習目標

- 理解 MCP 協議的設計理念和架構
- 掌握 MCP 服務器和客戶端的開發
- 學習與主流 LLM 提供商的整合
- 了解安全性和生產部署最佳實踐
- 實現 Code Execution 優化，減少 Token 使用

### 目標受眾

- AI 應用開發者
- LLM 工具整合工程師
- 企業級 AI 系統架構師
- 開源工具開發者

---

## MCP 簡介

### 什麼是 MCP？

**Model Context Protocol (MCP)** 是由 Anthropic 開發並於 2025 年 12 月捐贈給 Linux 基金會 Agentic AI Foundation 的**開放標準協議**。

MCP 的核心使命是**標準化大型語言模型（LLM）與外部工具、數據源之間的連接方式**，就像 USB-C 標準化了設備充電接口一樣。

### 為什麼需要 MCP？

在 MCP 出現之前，每個 LLM 提供商、每個 AI 應用都需要：

- ❌ 為每個數據源編寫自定義連接器
- ❌ 實現不同的工具調用格式
- ❌ 處理各種不同的認證機制
- ❌ 維護大量重複的整合代碼

**MCP 解決的問題：**

✅ **標準化通信**：統一的協議規範
✅ **互操作性**：一次編寫，多處使用
✅ **可組合性**：輕鬆組合多個工具和數據源
✅ **安全性**：內建安全機制和權限控制
✅ **效率提升**：Code Execution 模式減少 98.7% Token 使用

### 重要里程碑

- **2024 年 11 月**：Anthropic 發布 MCP 1.0
- **2024 年 12 月**：OpenAI、Google、Microsoft、AWS 宣布支持
- **2025 年 12 月**：捐贈給 Linux 基金會 Agentic AI Foundation
- **2025 年 12 月**：月下載量突破 97M+

---

## 核心優勢

### 1. 標準化接口

```
傳統方式：
LLM A → 自定義適配器 → 工具 X
LLM B → 另一個適配器 → 工具 X
LLM A → 又一個適配器 → 工具 Y

MCP 方式：
LLM A ──┐
LLM B ──┼── MCP 協議 ── MCP Server ──┬── 工具 X
LLM C ──┘                              ├── 工具 Y
                                       └── 工具 Z
```

### 2. 產業支持

主要支持者包括：

- **Anthropic** (Claude)
- **OpenAI** (ChatGPT, GPT-4)
- **Google** (Gemini)
- **Microsoft** (Azure OpenAI)
- **Amazon** (AWS Bedrock)
- **Sourcegraph** (Cody)
- **Zed**、**Replit** 等開發工具

### 3. 驚人的效率提升

使用 **Code Execution with MCP** 模式：

- 📉 **減少 98.7% Token 使用**
- ⚡ **降低成本和延遲**
- 🎯 **更精確的工具執行**

### 4. 豐富的生態系統

目前已有超過 **100+ 官方和社區 MCP 服務器**：

- 文件系統操作
- 數據庫查詢（PostgreSQL, MySQL, SQLite）
- API 整合（GitHub, Slack, Google Drive）
- 瀏覽器自動化（Puppeteer）
- 開發工具（Git, Docker）

---

## 架構設計

### 核心組件

```
┌─────────────────────────────────────────────────────────┐
│                     MCP 架構                              │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐         ┌──────────────┐              │
│  │  MCP Client  │ ◄─────► │  MCP Server  │              │
│  │   (主機)     │   MCP   │   (工具端)   │              │
│  │              │  Protocol│              │              │
│  └──────────────┘         └──────────────┘              │
│         │                         │                      │
│         ▼                         ▼                      │
│  ┌──────────────┐         ┌──────────────┐              │
│  │    Claude    │         │   Tools      │              │
│  │    GPT-4     │         │   Resources  │              │
│  │    Gemini    │         │   Prompts    │              │
│  └──────────────┘         └──────────────┘              │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### 三大核心功能

#### 1. Tools（工具）

MCP 服務器可以向客戶端公開可調用的工具：

```python
# 工具定義示例
{
    "name": "read_file",
    "description": "讀取指定路徑的文件內容",
    "inputSchema": {
        "type": "object",
        "properties": {
            "path": {"type": "string"}
        }
    }
}
```

#### 2. Resources（資源）

服務器可以提供結構化數據資源：

```python
# 資源示例
{
    "uri": "file:///project/README.md",
    "name": "專案說明",
    "mimeType": "text/markdown"
}
```

#### 3. Prompts（提示模板）

預定義的提示模板：

```python
# 提示模板示例
{
    "name": "code_review",
    "description": "代碼審查提示",
    "arguments": [
        {"name": "language", "required": true}
    ]
}
```

### 通信機制

MCP 使用 **JSON-RPC 2.0** 協議進行通信：

- **傳輸層**：stdio、HTTP/SSE、WebSocket
- **消息格式**：JSON
- **通信模式**：請求-響應、通知、流式傳輸

---

## 教程結構

### 📚 基礎篇

| 文件 | 內容 | 難度 |
|------|------|------|
| `01_MCP概述.py` | MCP 協議概念、架構、核心組件 | ⭐ |
| `02_安裝配置.py` | Python/TypeScript SDK 安裝和環境配置 | ⭐ |

### 🔧 開發篇

| 文件 | 內容 | 難度 |
|------|------|------|
| `03_創建MCP服務器.py` | 從零構建自定義 MCP 服務器 | ⭐⭐ |
| `04_創建MCP客戶端.py` | 開發 MCP 客戶端連接服務器 | ⭐⭐ |
| `05_工具定義.py` | 定義和實現 MCP 工具 | ⭐⭐ |
| `06_資源管理.py` | 實現資源提供和訪問 | ⭐⭐ |
| `07_提示模板.py` | 創建和使用提示模板 | ⭐⭐ |

### 🚀 整合篇

| 文件 | 內容 | 難度 |
|------|------|------|
| `08_Claude整合.py` | 與 Claude Desktop 整合 | ⭐⭐⭐ |
| `09_OpenAI整合.py` | 與 OpenAI API 整合 | ⭐⭐⭐ |
| `10_代碼執行優化.py` | Code Execution 模式實現 | ⭐⭐⭐⭐ |

### 🔒 進階篇

| 文件 | 內容 | 難度 |
|------|------|------|
| `11_安全最佳實踐.py` | 認證、授權、沙箱隔離 | ⭐⭐⭐⭐ |
| `12_生產部署.py` | 監控、日誌、擴展、容錯 | ⭐⭐⭐⭐⭐ |

---

## 快速開始

### 前置需求

- Python 3.10+ 或 Node.js 18+
- 基本的 async/await 概念
- 了解 JSON 和 REST API

### 5 分鐘快速上手

#### 1. 安裝 MCP SDK

```bash
# Python
pip install mcp

# TypeScript
npm install @modelcontextprotocol/sdk
```

#### 2. 創建簡單的 MCP 服務器

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server

# 創建服務器實例
app = Server("my-first-server")

# 定義工具
@app.tool()
async def hello(name: str) -> str:
    """向用戶問好"""
    return f"你好，{name}！"

# 運行服務器
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

#### 3. 配置 Claude Desktop

編輯 `~/Library/Application Support/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "my-first-server": {
      "command": "python",
      "args": ["/path/to/your/server.py"]
    }
  }
}
```

#### 4. 測試

重啟 Claude Desktop，輸入：

```
使用 hello 工具向 "世界" 問好
```

應該會看到：`你好，世界！`

---

## 生態系統

### 官方 MCP 服務器（部分）

#### 開發工具

- **@modelcontextprotocol/server-filesystem** - 文件系統操作
- **@modelcontextprotocol/server-git** - Git 倉庫管理
- **@modelcontextprotocol/server-github** - GitHub API 整合

#### 數據庫

- **@modelcontextprotocol/server-postgres** - PostgreSQL 查詢
- **@modelcontextprotocol/server-sqlite** - SQLite 操作

#### 生產力工具

- **@modelcontextprotocol/server-google-drive** - Google Drive 文件
- **@modelcontextprotocol/server-slack** - Slack 整合

#### 瀏覽器自動化

- **@modelcontextprotocol/server-puppeteer** - 網頁抓取和自動化

### 社區貢獻

查看完整列表：https://github.com/modelcontextprotocol/servers

---

## 最佳實踐

### 1. 設計原則

✅ **單一職責**：每個 MCP 服務器專注於一個領域
✅ **清晰命名**：工具名稱要描述性強
✅ **完整文檔**：詳細的 description 和參數說明
✅ **錯誤處理**：提供有幫助的錯誤消息

### 2. 安全考慮

🔒 **最小權限**：只請求必要的權限
🔒 **輸入驗證**：嚴格驗證所有用戶輸入
🔒 **沙箱隔離**：在受限環境中執行不受信任的代碼
🔒 **審計日誌**：記錄所有敏感操作

### 3. 性能優化

⚡ **異步處理**：使用 async/await 避免阻塞
⚡ **連接池**：重用數據庫和 API 連接
⚡ **緩存策略**：緩存頻繁訪問的資源
⚡ **批量操作**：合併多個小請求

### 4. 可觀測性

📊 **結構化日誌**：使用 JSON 格式日誌
📊 **指標收集**：追蹤請求量、延遲、錯誤率
📊 **分佈式追蹤**：使用 OpenTelemetry
📊 **健康檢查**：實現 health check 端點

---

## 常見問題

### Q1: MCP 和 OpenAI Function Calling 有什麼區別？

**A**:

- **OpenAI Function Calling** 是 OpenAI 特定的功能，只能在 OpenAI 的模型中使用
- **MCP** 是一個**開放標準**，支持多個 LLM 提供商（Claude、GPT、Gemini 等）
- MCP 提供了更豐富的功能（Tools + Resources + Prompts）

### Q2: MCP 支持哪些編程語言？

**A**: 官方 SDK 支持：

- **Python** (mcp)
- **TypeScript/JavaScript** (@modelcontextprotocol/sdk)

社區維護的 SDK：
- Rust
- Go
- Java

### Q3: 如何處理 MCP 服務器的認證？

**A**: MCP 支持多種認證方式：

- 環境變數
- OAuth 2.0
- API 密鑰
- mTLS (雙向 TLS)

詳見 `11_安全最佳實踐.py`

### Q4: MCP 服務器可以部署到雲端嗎？

**A**: 可以！支持多種部署方式：

- **本地運行**：stdio 傳輸
- **HTTP 服務器**：使用 SSE (Server-Sent Events)
- **容器化**：Docker/Kubernetes
- **Serverless**：AWS Lambda、Google Cloud Functions

詳見 `12_生產部署.py`

### Q5: Code Execution 如何減少 98.7% Token？

**A**: 傳統方式：

1. LLM 生成代碼（消耗 Token）
2. 返回代碼給客戶端（消耗 Token）
3. 客戶端執行代碼
4. 返回結果（消耗 Token）

Code Execution 方式：

1. LLM 調用 MCP 工具（少量 Token）
2. **MCP 服務器直接執行代碼**
3. 只返回執行結果（少量 Token）

詳見 `10_代碼執行優化.py`

### Q6: 如何除錯 MCP 服務器？

**A**: 推薦工具：

```bash
# 使用官方 Inspector
npx @modelcontextprotocol/inspector python server.py

# 查看日誌
tail -f mcp-server.log

# 使用 MCP CLI
mcp dev server.py
```

### Q7: MCP 的未來發展方向？

**A**: 根據 Linux 基金會的規劃：

- 🌐 更多語言 SDK
- 🔄 協議版本演進（MCP 2.0）
- 🏢 企業級功能（治理、合規）
- 📱 移動端支持
- 🔗 與其他標準整合（OpenTelemetry、gRPC）

---

## 參考資源

### 官方文檔

- 📘 [MCP 官方網站](https://modelcontextprotocol.io)
- 📗 [MCP 規範](https://spec.modelcontextprotocol.io)
- 📙 [Python SDK 文檔](https://github.com/modelcontextprotocol/python-sdk)
- 📕 [TypeScript SDK 文檔](https://github.com/modelcontextprotocol/typescript-sdk)

### 社區資源

- 💬 [Discord 社群](https://discord.gg/modelcontextprotocol)
- 🐙 [GitHub 討論區](https://github.com/modelcontextprotocol/discussions)
- 📺 [YouTube 教程頻道](https://youtube.com/@modelcontextprotocol)

### 相關工具

- 🔍 [MCP Inspector](https://github.com/modelcontextprotocol/inspector) - 除錯工具
- 📦 [MCP Registry](https://mcp.so) - 服務器註冊表
- 🛠️ [MCP CLI](https://github.com/modelcontextprotocol/cli) - 命令行工具

### 學習資源

- 📚 [Awesome MCP](https://github.com/modelcontextprotocol/awesome-mcp) - 精選資源列表
- 🎓 [MCP 教程合集](https://modelcontextprotocol.io/tutorials)
- 📝 [部落格文章](https://www.anthropic.com/news/model-context-protocol)

---

## 貢獻指南

發現問題或有改進建議？歡迎：

1. 提交 Issue
2. 發起 Pull Request
3. 在社區分享您的 MCP 服務器

---

## 授權

本教程採用 MIT 授權。MCP 協議本身是開放標準，歡迎所有人使用和實現。

---

## 致謝

感謝以下組織和個人對 MCP 的貢獻：

- **Anthropic** - 協議設計和初始實現
- **Linux Foundation Agentic AI Foundation** - 協議治理
- **OpenAI, Google, Microsoft, AWS** - 生態系統支持
- **開源社區** - 數百個 MCP 服務器和工具

---

**開始您的 MCP 之旅吧！從 `01_MCP概述.py` 開始。**

---

*最後更新：2025-12-22*
*MCP 協議版本：1.0*
*教程版本：1.0.0*
