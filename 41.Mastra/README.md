# Mastra - TypeScript-First AI Agent 框架

## 🌟 簡介

Mastra 是一個現代化的 TypeScript-first AI Agent 框架，專為構建生產級 AI 應用而設計。它於 2025 年推出，致力於提供強大的工作流引擎、豐富的工具整合能力和優雅的多 Agent 協作機制。

### 核心特點

- **🎯 TypeScript 原生支持**：完整的類型安全和 IntelliSense 支持
- **⚙️ 強大的工作流引擎**：可視化定義和執行複雜的 AI 工作流
- **🔌 豐富的整合生態**：支持 100+ 第三方服務和工具
- **🤝 多 Agent 協作**：輕鬆構建協同工作的 Agent 系統
- **💾 智能記憶管理**：持久化對話歷史和上下文
- **📊 可觀測性**：內建監控、日誌和追蹤功能
- **🚀 生產就緒**：企業級的錯誤處理和可靠性

## 🏗️ 設計理念

### 1. TypeScript First

Mastra 從零開始就為 TypeScript 設計，而不是將 JavaScript 框架改造為 TypeScript。這意味著：

- 完整的類型定義和類型推斷
- IDE 友好的自動完成
- 編譯時錯誤檢測
- 更好的代碼維護性

### 2. 工作流驅動

Mastra 將 AI 應用視為工作流的組合：

```typescript
const workflow = mastra.workflow('customer-service')
  .step('classify', async (ctx) => {
    return await classifyIntent(ctx.input);
  })
  .step('route', async (ctx) => {
    return await routeToAgent(ctx.results.classify);
  })
  .step('respond', async (ctx) => {
    return await generateResponse(ctx.results.route);
  });
```

### 3. 工具優先

所有功能都以工具（Tools）的形式組織：

- 標準化的工具接口
- 可組合的工具鏈
- 豐富的預建工具庫
- 自定義工具開發簡單

### 4. 可觀測性內建

從一開始就考慮生產環境的需求：

- 自動追蹤每個步驟
- 結構化日誌輸出
- 性能指標收集
- 錯誤追蹤和報警

## 📦 核心組件

### 1. Agent 系統

```typescript
import { Agent } from '@mastra/core';

const agent = new Agent({
  name: 'customer-service-agent',
  description: '客服助手',
  model: {
    provider: 'openai',
    name: 'gpt-4',
  },
  tools: [searchKB, createTicket, sendEmail],
  instructions: '你是一個專業的客服助手...',
});
```

### 2. 工作流引擎

Mastra 的工作流引擎支持：

- **順序執行**：按步驟依次執行
- **並行執行**：同時執行多個步驟
- **條件分支**：根據結果選擇路徑
- **循環迭代**：重複執行直到滿足條件
- **錯誤處理**：自動重試和降級策略

### 3. 工具和整合

預建整合包括：

| 類別 | 整合服務 |
|------|---------|
| **通訊** | Slack, Discord, Telegram, WhatsApp |
| **CRM** | Salesforce, HubSpot, Zoho |
| **數據庫** | PostgreSQL, MongoDB, Redis |
| **搜索** | Algolia, Elasticsearch, Pinecone |
| **郵件** | Gmail, SendGrid, Mailgun |
| **文檔** | Google Docs, Notion, Confluence |
| **開發** | GitHub, GitLab, Jira, Linear |
| **分析** | Google Analytics, Mixpanel, Amplitude |

### 4. 記憶管理

Mastra 提供多層次的記憶系統：

- **短期記憶**：當前對話的上下文
- **工作記憶**：跨對話的臨時信息
- **長期記憶**：持久化的知識庫
- **向量記憶**：語義搜索和檢索

### 5. RAG 支持

內建的 RAG（檢索增強生成）功能：

```typescript
import { RAG } from '@mastra/rag';

const rag = new RAG({
  embeddings: {
    provider: 'openai',
    model: 'text-embedding-3-large',
  },
  vectorStore: {
    provider: 'pinecone',
    index: 'knowledge-base',
  },
  chunking: {
    size: 1000,
    overlap: 200,
  },
});
```

## 🚀 安装和配置

### TypeScript/Node.js 安裝

```bash
# 使用 npm
npm install @mastra/core

# 使用 yarn
yarn add @mastra/core

# 使用 pnpm
pnpm add @mastra/core
```

### Python 集成

雖然 Mastra 是 TypeScript-first 框架，但可以通過 HTTP API 從 Python 調用：

```bash
pip install -r requirements.txt
```

### 環境配置

創建 `.env` 文件：

```env
# OpenAI 配置
OPENAI_API_KEY=your-api-key

# Mastra 配置
MASTRA_API_URL=http://localhost:3000
MASTRA_API_KEY=your-mastra-api-key

# 向量數據庫
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=us-west1-gcp

# 其他服務
SLACK_BOT_TOKEN=xoxb-...
GITHUB_TOKEN=ghp_...
```

## 🎯 快速開始

### TypeScript 範例

```typescript
import { Mastra } from '@mastra/core';
import { OpenAI } from '@mastra/llm-openai';

// 初始化 Mastra
const mastra = new Mastra({
  llm: new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
    model: 'gpt-4',
  }),
});

// 創建 Agent
const agent = mastra.agent({
  name: 'assistant',
  instructions: '你是一個有幫助的助手',
  tools: [],
});

// 執行對話
const response = await agent.chat('你好，介紹一下自己');
console.log(response.message);
```

### Python 調用範例

```python
import requests
import os

# Mastra API 配置
MASTRA_API_URL = os.getenv('MASTRA_API_URL')
MASTRA_API_KEY = os.getenv('MASTRA_API_KEY')

# 調用 Agent
response = requests.post(
    f'{MASTRA_API_URL}/api/agents/assistant/chat',
    headers={'Authorization': f'Bearer {MASTRA_API_KEY}'},
    json={'message': '你好，介紹一下自己'}
)

print(response.json()['message'])
```

## 🔧 核心概念

### 1. Agents（代理）

Agent 是 Mastra 中的基本執行單元，每個 Agent 都有：

- **身份**：名稱和描述
- **能力**：可用的工具集
- **知識**：指令和上下文
- **記憶**：對話歷史

### 2. Tools（工具）

工具是 Agent 可以執行的操作：

```typescript
const searchTool = {
  name: 'search',
  description: '搜索知識庫',
  parameters: {
    query: { type: 'string', description: '搜索查詢' },
  },
  execute: async ({ query }) => {
    // 執行搜索邏輯
    return results;
  },
};
```

### 3. Workflows（工作流）

工作流編排多個步驟的執行：

```typescript
const workflow = mastra.workflow('onboarding')
  .step('create-account', createAccount)
  .step('send-welcome-email', sendWelcomeEmail)
  .step('assign-to-team', assignToTeam);
```

### 4. Integrations（整合）

整合連接外部服務：

```typescript
import { SlackIntegration } from '@mastra/integrations-slack';

const slack = new SlackIntegration({
  token: process.env.SLACK_BOT_TOKEN,
});

await slack.postMessage({
  channel: '#general',
  text: 'Hello from Mastra!',
});
```

## 📊 監控和可觀測性

### 內建追蹤

Mastra 自動追蹤：

- 每個 Agent 調用
- 工作流執行步驟
- 工具使用情況
- LLM API 調用
- 錯誤和異常

### 日誌系統

結構化日誌輸出：

```typescript
mastra.logger.info('Processing request', {
  userId: '123',
  action: 'chat',
  metadata: { ... },
});
```

### 性能指標

自動收集：

- 響應時間
- Token 使用量
- 成功/失敗率
- 工具執行次數

## 🔒 安全性

### API 密鑰管理

- 環境變量存儲
- 加密傳輸
- 定期輪換

### 權限控制

- 基於角色的訪問控制（RBAC）
- Agent 級別的權限
- 工具使用限制

### 數據隱私

- 敏感信息過濾
- PII 檢測和脫敏
- 合規性支持（GDPR, CCPA）

## 🌍 多 Agent 協作

Mastra 支持多種協作模式：

### 1. 主從模式

```typescript
const supervisor = mastra.agent({
  name: 'supervisor',
  tools: [delegateToResearcher, delegateToWriter],
});
```

### 2. 對等協作

```typescript
const team = mastra.team({
  agents: [researcher, writer, reviewer],
  strategy: 'collaborative',
});
```

### 3. 工作流編排

```typescript
const workflow = mastra.workflow('content-creation')
  .step('research', researcher)
  .step('write', writer)
  .step('review', reviewer);
```

## 📚 學習資源

- **官方網站**: https://mastra.ai
- **文檔**: https://docs.mastra.ai
- **GitHub**: https://github.com/mastra-ai/mastra
- **Discord 社群**: https://discord.gg/mastra
- **範例項目**: https://github.com/mastra-ai/examples

## 🆚 與其他框架對比

| 特性 | Mastra | LangChain | AutoGen | CrewAI |
|------|--------|-----------|---------|--------|
| TypeScript 支持 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| 工作流引擎 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 工具整合 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 多 Agent | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 可觀測性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| 生產就緒 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

## 🎓 學習路徑

### 初學者

1. ✅ 閱讀快速開始指南
2. ✅ 運行基礎範例
3. ✅ 創建第一個 Agent
4. ✅ 嘗試內建工具

### 進階用戶

1. ✅ 設計複雜工作流
2. ✅ 開發自定義工具
3. ✅ 整合外部服務
4. ✅ 實現 RAG 系統

### 專家級

1. ✅ 多 Agent 協作系統
2. ✅ 生產環境部署
3. ✅ 性能優化和監控
4. ✅ 安全性和合規性

## 🤝 社群和支持

- **問題反饋**: GitHub Issues
- **功能請求**: GitHub Discussions
- **即時幫助**: Discord 社群
- **商業支持**: enterprise@mastra.ai

## 📝 授權

Mastra 採用 MIT 授權，可免費用於商業和個人項目。

## 🎯 使用案例

### 客戶服務
- 智能客服機器人
- 工單自動分類和路由
- 客戶情緒分析

### 內容創作
- 文章自動生成
- SEO 優化建議
- 多語言翻譯

### 數據分析
- 自然語言查詢
- 報告自動生成
- 異常檢測和告警

### 開發助手
- 代碼審查
- 文檔生成
- Bug 分析和修復建議

## 🔮 未來規劃

- 🎨 可視化工作流設計器
- 🧪 A/B 測試框架
- 🌐 多語言 SDK（Python, Go, Rust）
- 🔄 實時協作編輯
- 📱 移動端 SDK

---

**立即開始使用 Mastra，構建下一代 AI 應用！**
