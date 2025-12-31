# CopilotKit - React AI Agent UI 基礎設施框架

![GitHub Stars](https://img.shields.io/badge/GitHub-26.8K%20stars-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 框架簡介

CopilotKit 是一個開源的 React UI 基礎設施框架，專為將 AI Agent 無縫嵌入到 Web 應用中而設計。它提供了完整的前後端整合方案，讓開發者可以快速構建具有 AI 能力的互動式應用。

### 主要特點

- **React 原生支持**：深度整合 React 生態系統，提供開箱即用的 UI 組件
- **CoAgent 架構**：支援多 Agent 協作，實現複雜的 AI 互動場景
- **前後端整合**：無縫連接前端 UI 和後端 AI 邏輯
- **流式輸出**：實時串流 AI 響應，提供流暢的用戶體驗
- **狀態管理**：智能管理前端狀態，與 AI Agent 雙向同步
- **可自定義 UI**：靈活的組件系統，支援完全自定義界面
- **生產就緒**：內建最佳實踐，適合生產環境部署
- **TypeScript 支持**：完整的類型定義，提供優秀的開發體驗

## 核心概念

### 1. CopilotKit

CopilotKit 是框架的核心提供者，負責管理 AI 上下文、配置和全局狀態。

```typescript
import { CopilotKit } from "@copilotkit/react-core";

<CopilotKit runtimeUrl="/api/copilotkit">
  <YourApp />
</CopilotKit>
```

**關鍵功能**：
- 管理 AI 運行時配置
- 提供全局上下文
- 處理與後端的通信
- 管理 Agent 生命週期

### 2. CoAgent

CoAgent 是 CopilotKit 的智能代理單元，可以獨立執行任務或與其他 Agent 協作。

**特性**：
- **自主執行**：可獨立完成複雜任務
- **協作能力**：多個 Agent 之間可以協調工作
- **狀態感知**：理解並操作應用狀態
- **工具調用**：可以調用定義的 Actions 和工具

### 3. Actions

Actions 是 Agent 可以執行的操作，連接 AI 推理和實際功能。

```typescript
useCopilotAction({
  name: "updateData",
  description: "更新應用數據",
  parameters: [
    { name: "value", type: "string", description: "新的值" }
  ],
  handler: async ({ value }) => {
    // 執行操作
  }
});
```

**類型**：
- **前端 Actions**：直接在瀏覽器執行
- **後端 Actions**：在服務器端處理
- **混合 Actions**：結合前後端能力

### 4. Copilot Chat

內建的聊天界面組件，提供即插即用的 AI 對話功能。

```typescript
import { CopilotChat } from "@copilotkit/react-ui";

<CopilotChat
  labels={{
    title: "AI 助手",
    initial: "有什麼可以幫你的？"
  }}
/>
```

### 5. 可讀狀態 (Readable State)

使應用狀態對 AI Agent 可見，讓 Agent 理解當前上下文。

```typescript
useCopilotReadable({
  description: "當前用戶信息",
  value: userData
});
```

### 6. LangGraph 整合

支援與 LangGraph 深度整合，構建複雜的 AI 工作流。

## 安裝和配置

### 前端安裝

```bash
# 核心包
npm install @copilotkit/react-core @copilotkit/react-ui

# 可選：LangGraph 整合
npm install @copilotkit/react-textarea
```

### 後端安裝

```bash
# Python 後端
pip install copilotkit

# 或者使用 Node.js
npm install @copilotkit/runtime
```

### 基本配置

#### 1. 前端設置

```typescript
// app.tsx
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotPopup } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";

function App() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit">
      <YourApp />
      <CopilotPopup
        instructions="你是一個友好的 AI 助手"
        defaultOpen={true}
        labels={{
          title: "AI 助手",
          initial: "有什麼可以幫你的？"
        }}
      />
    </CopilotKit>
  );
}
```

#### 2. 後端設置（Python FastAPI）

```python
from fastapi import FastAPI
from copilotkit import CopilotKitSDK, LangGraphAgent
from copilotkit.integrations.fastapi import add_fastapi_endpoint

app = FastAPI()
sdk = CopilotKitSDK()

# 添加 CopilotKit 端點
add_fastapi_endpoint(app, sdk, "/copilotkit")

# 定義 Agent
agent = LangGraphAgent(
    name="assistant",
    description="通用助手"
)

sdk.add_agent(agent)
```

#### 3. 後端設置（Node.js）

```typescript
import { CopilotRuntime, OpenAIAdapter } from "@copilotkit/runtime";
import OpenAI from "openai";

const openai = new OpenAI();
const serviceAdapter = new OpenAIAdapter();

app.post("/api/copilotkit", async (req, res) => {
  const runtime = new CopilotRuntime();
  const { handleRequest } = runtime.streamHttpServerResponse(
    req,
    res,
    serviceAdapter
  );

  await handleRequest();
});
```

## 範例索引

本目錄包含以下範例，從基礎到進階循序漸進：

### 基礎範例

1. **[01_快速開始.py](./01_快速開始.py)**
   - CopilotKit 基本設置
   - 簡單的聊天界面
   - 第一個 Action 定義

2. **[02_React整合.py](./02_React整合.py)**
   - React 組件整合
   - Hooks 使用方法
   - UI 組件配置

3. **[03_CoAgent.py](./03_CoAgent.py)**
   - CoAgent 基本概念
   - Agent 定義和配置
   - Agent 間通信

### 進階功能

4. **[04_前端狀態.py](./04_前端狀態.py)**
   - 可讀狀態管理
   - 可寫狀態同步
   - 狀態變更監聽

5. **[05_後端Action.py](./05_後端Action.py)**
   - 後端 Action 定義
   - 參數驗證
   - 錯誤處理

6. **[06_流式輸出.py](./06_流式輸出.py)**
   - 實時串流響應
   - 進度更新
   - 中斷處理

### 高級應用

7. **[07_自定義UI.py](./07_自定義UI.py)**
   - 自定義聊天界面
   - 主題定制
   - 組件擴展

8. **[08_多Agent.py](./08_多Agent.py)**
   - 多 Agent 協作
   - Agent 編排
   - 任務分配

### 生產實踐

9. **[09_部署指南.py](./09_部署指南.py)**
   - 生產環境配置
   - 性能優化
   - 監控和日誌

10. **[10_最佳實踐.py](./10_最佳實踐.py)**
    - 設計模式
    - 安全考慮
    - 性能調優

## 與其他框架對比

### CopilotKit vs LangChain

| 特性 | CopilotKit | LangChain |
|------|-----------|-----------|
| **主要用途** | React UI + AI Agent | 通用 AI 應用開發 |
| **前端整合** | ⭐⭐⭐⭐⭐ 原生 React | ⭐⭐ 需要自行整合 |
| **UI 組件** | ⭐⭐⭐⭐⭐ 內建完整 UI | ⭐ 無內建 UI |
| **狀態管理** | ⭐⭐⭐⭐⭐ 雙向同步 | ⭐⭐ 需要自行實現 |
| **流式輸出** | ⭐⭐⭐⭐⭐ 原生支持 | ⭐⭐⭐⭐ 支持但需配置 |
| **學習曲線** | ⭐⭐⭐ 中等（需了解 React） | ⭐⭐⭐⭐ 較陡 |
| **適用場景** | Web 應用 AI 功能 | 各類 AI 應用 |

### CopilotKit vs AutoGen

| 特性 | CopilotKit | AutoGen |
|------|-----------|----------|
| **架構重點** | UI 優先 | Multi-Agent 對話 |
| **Agent 協作** | ⭐⭐⭐⭐ CoAgent 機制 | ⭐⭐⭐⭐⭐ 核心功能 |
| **Web 整合** | ⭐⭐⭐⭐⭐ 專為 Web 設計 | ⭐⭐ 需要額外工作 |
| **即時互動** | ⭐⭐⭐⭐⭐ 優秀 | ⭐⭐⭐ 一般 |
| **複雜工作流** | ⭐⭐⭐ 基本支持 | ⭐⭐⭐⭐⭐ 強大 |
| **適用場景** | 互動式 Web 應用 | 複雜 Agent 系統 |

### CopilotKit vs CrewAI

| 特性 | CopilotKit | CrewAI |
|------|-----------|--------|
| **Agent 組織** | CoAgent 協作 | Crew 團隊模型 |
| **前端體驗** | ⭐⭐⭐⭐⭐ 一流 | ⭐ 無前端 |
| **任務編排** | ⭐⭐⭐ 基本 | ⭐⭐⭐⭐⭐ 豐富 |
| **角色定義** | ⭐⭐⭐ 靈活 | ⭐⭐⭐⭐ 結構化 |
| **即時反饋** | ⭐⭐⭐⭐⭐ 實時 | ⭐⭐ 批處理為主 |
| **適用場景** | 用戶互動應用 | 自動化工作流 |

### CopilotKit vs LangGraph

| 特性 | CopilotKit | LangGraph |
|------|-----------|-----------|
| **工作流定義** | ⭐⭐⭐ 簡單流程 | ⭐⭐⭐⭐⭐ 複雜圖結構 |
| **React 整合** | ⭐⭐⭐⭐⭐ 原生支持 | ⭐⭐⭐ 可整合 |
| **狀態機** | ⭐⭐⭐ 基本 | ⭐⭐⭐⭐⭐ 強大 |
| **UI 層** | ⭐⭐⭐⭐⭐ 完整 | ⭐ 無 |
| **互操作性** | ⭐⭐⭐⭐ 支持 LangGraph | ⭐⭐⭐⭐ 可被整合 |
| **適用場景** | UI 驅動應用 | 複雜工作流引擎 |

## 核心優勢

### 1. 極致的前端體驗
CopilotKit 將 AI 能力完美整合到 React 應用中，提供：
- 即插即用的 UI 組件
- 流暢的實時互動
- 優雅的狀態管理
- TypeScript 完整支持

### 2. 靈活的架構設計
- **前後端分離**：清晰的職責劃分
- **可擴展性**：易於添加新功能
- **模塊化**：組件可獨立使用
- **框架無關後端**：支持多種後端技術

### 3. 開發者友好
- **文檔完善**：詳細的官方文檔和範例
- **活躍社區**：GitHub 26.8K stars
- **最佳實踐**：內建常見場景解決方案
- **快速迭代**：持續更新和改進

## 適用場景

### 理想場景
- ✅ 需要 AI 功能的 React Web 應用
- ✅ 互動式聊天界面
- ✅ AI 輔助的數據處理應用
- ✅ 智能表單和工作流
- ✅ 協作編輯工具
- ✅ 客戶服務系統

### 不太適合
- ❌ 純後端 AI 服務
- ❌ 非 React 框架（Vue、Angular 等）
- ❌ 極其複雜的 Multi-Agent 系統
- ❌ 批處理 AI 任務
- ❌ 移動原生應用（僅限 Web）

## 技術架構

```
┌─────────────────────────────────────────┐
│           React Application             │
│  ┌────────────────────────────────────┐ │
│  │        CopilotKit Provider         │ │
│  │  ┌──────────┐      ┌────────────┐ │ │
│  │  │ UI Layer │      │ Hooks API  │ │ │
│  │  │  - Chat  │      │ - Actions  │ │ │
│  │  │  - Popup │      │ - Readable │ │ │
│  │  └────┬─────┘      └─────┬──────┘ │ │
│  │       │                  │        │ │
│  │       └────────┬─────────┘        │ │
│  │                │                  │ │
│  │         ┌──────▼────────┐         │ │
│  │         │  Runtime API  │         │ │
│  │         └───────┬───────┘         │ │
│  └─────────────────┼─────────────────┘ │
└────────────────────┼───────────────────┘
                     │ HTTP/WebSocket
         ┌───────────▼───────────┐
         │   Backend Runtime     │
         │  ┌─────────────────┐  │
         │  │   CoAgents      │  │
         │  ├─────────────────┤  │
         │  │   Actions       │  │
         │  ├─────────────────┤  │
         │  │   LLM Service   │  │
         │  │ (OpenAI/Anthropic)│
         │  └─────────────────┘  │
         └───────────────────────┘
```

## 快速開始

### 5 分鐘快速開始

1. **安裝依賴**
```bash
npm install @copilotkit/react-core @copilotkit/react-ui
pip install copilotkit fastapi uvicorn
```

2. **設置環境變量**
```bash
export OPENAI_API_KEY=your_api_key
```

3. **創建後端** (api.py)
```python
from fastapi import FastAPI
from copilotkit import CopilotKitSDK
from copilotkit.integrations.fastapi import add_fastapi_endpoint

app = FastAPI()
sdk = CopilotKitSDK()
add_fastapi_endpoint(app, sdk, "/copilotkit")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

4. **創建前端** (App.tsx)
```typescript
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotPopup } from "@copilotkit/react-ui";

function App() {
  return (
    <CopilotKit runtimeUrl="http://localhost:8000/copilotkit">
      <YourApp />
      <CopilotPopup />
    </CopilotKit>
  );
}
```

5. **運行**
```bash
# 終端 1：啟動後端
python api.py

# 終端 2：啟動前端
npm start
```

## 學習路徑

```
入門階段（1-2 天）
  ↓
01_快速開始.py → 了解基本概念
  ↓
02_React整合.py → 掌握組件使用
  ↓
基礎階段（3-5 天）
  ↓
03_CoAgent.py → 理解 Agent 機制
  ↓
04_前端狀態.py → 學習狀態管理
  ↓
05_後端Action.py → 實現業務邏輯
  ↓
進階階段（1-2 週）
  ↓
06_流式輸出.py → 優化用戶體驗
  ↓
07_自定義UI.py → 定制界面
  ↓
08_多Agent.py → 複雜協作場景
  ↓
生產階段（持續）
  ↓
09_部署指南.py → 部署到生產
  ↓
10_最佳實踐.py → 持續優化
```

## 常見問題

### Q: CopilotKit 支持哪些 LLM？
A: 支持 OpenAI、Anthropic Claude、Google Gemini、本地模型等，任何兼容 OpenAI API 的服務都可以使用。

### Q: 可以在非 React 項目中使用嗎？
A: CopilotKit 主要為 React 設計，但後端部分可以獨立使用。對於其他前端框架，建議使用 LangChain 或其他通用框架。

### Q: 如何處理敏感數據？
A: 使用後端 Actions 處理敏感操作，避免在前端暴露敏感信息。參見 [05_後端Action.py](./05_後端Action.py)。

### Q: 性能如何優化？
A: 使用流式輸出、合理的狀態管理、Action 緩存等。詳見 [10_最佳實踐.py](./10_最佳實踐.py)。

### Q: 支持多語言嗎？
A: 完全支持，UI 標籤可自定義，AI 響應語言由提示詞控制。

## 相關資源

- **官方網站**: https://www.copilotkit.ai/
- **GitHub**: https://github.com/CopilotKit/CopilotKit
- **文檔**: https://docs.copilotkit.ai/
- **Discord 社區**: https://discord.gg/copilotkit
- **示範應用**: https://demo.copilotkit.ai/

## 授權

CopilotKit 採用 MIT 授權，可自由用於商業和開源項目。

## 總結

CopilotKit 是構建 AI 增強 Web 應用的最佳選擇之一，特別適合：
- React 開發者快速添加 AI 功能
- 需要優秀用戶體驗的 AI 應用
- 前後端分離的現代 Web 架構
- 追求開發效率和代碼質量的團隊

從 [01_快速開始.py](./01_快速開始.py) 開始，探索 CopilotKit 的強大功能！
