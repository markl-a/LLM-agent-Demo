# MetaGPT 學習教程

<div align="center">

**一個革命性的多 Agent 協作框架**

*將軟體公司的整個開發流程自動化*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![MetaGPT](https://img.shields.io/badge/MetaGPT-Latest-green.svg)](https://github.com/geekan/MetaGPT)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

## 📚 簡介

MetaGPT 是一個創新的多 Agent 元編程框架，它將軟體公司的組織架構和工作流程完整地編碼為 AI Agents，實現從需求分析到代碼實現的全流程自動化。

### 🎯 核心理念

**軟體公司 = LLM + SOP（標準作業流程）**

MetaGPT 模擬真實軟體公司的運作方式：

```
用戶需求 → 產品經理（PRD） → 架構師（設計） → 工程師（代碼） → 測試（QA） → 完成
```

### ✨ 主要特性

- 🔄 **標準化流程**: 基於軟體工程最佳實踐的 SOP
- 👥 **角色專業化**: 每個 Agent 扮演特定角色，各司其職
- 📝 **文檔驅動**: 通過結構化文檔傳遞信息，確保質量
- 🚀 **完整開發流程**: 從需求到代碼的全流程自動化
- 🔧 **高度可擴展**: 支持自定義角色和行為
- 🎨 **靈活配置**: 根據項目需求自由組合角色

## 📖 教程目錄

### 基礎教程

| 教程 | 內容 | 難度 | 預計時間 |
|------|------|------|----------|
| [0.基礎概念](./0.基礎概念.ipynb) | MetaGPT 架構、安裝配置、核心概念 | ⭐ 入門 | 30 分鐘 |
| [1.軟體開發流程](./1.軟體開發流程.ipynb) | 完整開發流程、各角色職責、實戰演練 | ⭐⭐ 進階 | 45 分鐘 |
| [2.角色定制與擴展](./2.角色定制與擴展.ipynb) | 自定義角色、自定義行為、工具集成 | ⭐⭐⭐ 高級 | 60 分鐘 |

### 教程內容詳解

#### 📘 0. 基礎概念

**學習內容:**
- MetaGPT 架構理解與核心組件
- 完整的安裝和配置指南
- 角色系統深度解析（ProductManager、Architect、Engineer、QA）
- 消息傳遞機制
- 工作區和文件管理
- 成本控制策略
- 常見問題解決

**適合對象:** MetaGPT 初學者，想要了解基礎概念和使用方法

**實踐項目:**
- 創建第一個 MetaGPT 項目
- 單獨使用各個角色
- 配置和優化

#### 📗 1. 軟體開發流程

**學習內容:**
- 需求分析階段（ProductManager）
  - PRD 文檔撰寫
  - 用戶故事定義
  - 功能需求分析

- 系統設計階段（Architect）
  - 架構設計
  - 數據模型設計
  - API 接口設計

- 代碼實現階段（Engineer）
  - 模組化代碼實現
  - 遵循設計文檔
  - 代碼質量保證

- 測試驗證階段（QA Engineer）
  - 測試用例編寫
  - 測試執行
  - Bug 報告

**適合對象:** 已掌握基礎概念，想要深入了解完整開發流程

**實踐項目:**
- 任務管理系統
- 筆記應用
- 自定義開發流程

#### 📙 2. 角色定制與擴展

**學習內容:**
- 理解角色系統架構
- 創建自定義 Action（行為）
- 創建自定義 Role（角色）
- 配置角色協作
- 集成外部工具
- 動態行為選擇
- 複雜團隊配置

**適合對象:** 有一定經驗，想要定制化開發流程

**實踐項目:**
- 代碼審查員角色
- 技術文檔員角色
- DevOps 工程師角色
- 數據科學團隊

## 🚀 快速開始

### 1. 安裝 MetaGPT

```bash
# 使用 pip 安裝
pip install metagpt

# 或從源碼安裝（推薦）
git clone https://github.com/geekan/MetaGPT.git
cd MetaGPT
pip install -e .
```

### 2. 配置環境

創建 `.env` 文件並配置 API 密鑰：

```bash
# OpenAI API 配置
OPENAI_API_KEY=your-api-key-here

# 或使用其他 LLM
# ANTHROPIC_API_KEY=your-claude-api-key
# ZHIPUAI_API_KEY=your-zhipu-api-key
```

### 3. 運行第一個示例

```python
from metagpt.team import Team

# 創建團隊
team = Team()

# 定義需求
requirement = "創建一個待辦事項管理應用"

# 設置預算
team.invest(investment=3.0)

# 運行項目
team.run_project(requirement)
await team.run(n_round=5)
```

## 💡 實際應用案例

### ✅ 適合使用 MetaGPT 的場景

| 場景 | 說明 | 預期成本 | 預期時間 |
|------|------|----------|----------|
| 🎨 **快速原型開發** | 驗證產品想法，生成 MVP | 1-3 美元 | 5-10 分鐘 |
| 🛠️ **CLI 工具開發** | 命令行工具、自動化腳本 | 1-2 美元 | 5-8 分鐘 |
| 📱 **小型應用** | 簡單的 Web/移動應用 | 3-8 美元 | 10-20 分鐘 |
| 📚 **文檔生成** | API 文檔、技術規範 | 1-2 美元 | 3-5 分鐘 |
| 🎓 **學習項目** | 理解軟體開發流程 | 2-5 美元 | 10-15 分鐘 |

### ⚠️ 不適合的場景

- ❌ 大型企業級應用（複雜度過高）
- ❌ 需要精細控制的項目
- ❌ 實時性要求高的應用
- ❌ 預算非常有限的項目（<1 美元）

## 📦 實戰範例

### 範例 1: 簡單任務管理器

```bash
python examples/simple_task_manager.py
```

**功能:**
- 創建、編輯、刪除任務
- 任務狀態管理
- 數據持久化

**成本:** 約 1-2 美元
**時間:** 5-8 分鐘

### 範例 2: 自定義角色演示

```bash
python examples/custom_role_demo.py
```

**展示:**
- 創建代碼審查員角色
- 創建技術文檔員角色
- 角色協作

**成本:** 約 2-3 美元
**時間:** 8-12 分鐘

## 🎯 最佳實踐

### 💰 成本控制

1. **使用便宜的模型測試**: 開發時使用 GPT-3.5-turbo，生產使用 GPT-4
2. **設置預算限制**: 使用 `team.invest(investment=3.0)` 設置上限
3. **限制運行輪數**: 使用 `n_round` 參數控制迭代次數
4. **簡化角色配置**: 簡單項目只用必要角色（如 PM + Engineer）
5. **分階段開發**: 先實現核心功能，再迭代完善

### 📝 需求描述

1. **清晰具體**: 使用明確的語言描述功能
2. **包含示例**: 提供輸入輸出示例
3. **說明約束**: 明確技術棧、性能要求
4. **分解功能**: 將複雜需求分解為小功能
5. **優先級明確**: 標註核心功能和可選功能

### ✅ 質量保證

1. **人工審核**: 仔細檢查生成的代碼和文檔
2. **測試驗證**: 運行測試，確保功能正常
3. **安全檢查**: 審查潛在的安全漏洞
4. **代碼優化**: 改進性能和可維護性
5. **錯誤處理**: 添加完善的異常處理

## 📐 系統架構

```
MetaGPT 架構
│
├── Role (角色層)
│   ├── ProductManager    - 產品經理
│   ├── Architect        - 架構師
│   ├── Engineer         - 工程師
│   └── QA Engineer      - 測試工程師
│
├── Action (行為層)
│   ├── WritePRD         - 撰寫 PRD
│   ├── WriteDesign      - 設計架構
│   ├── WriteCode        - 編寫代碼
│   └── WriteTest        - 編寫測試
│
├── Memory (記憶層)
│   └── MessageHistory   - 消息歷史
│
└── Environment (環境層)
    ├── Workspace        - 工作區
    └── Config          - 配置管理
```

## 🔑 核心概念

### Role（角色）

每個角色代表軟體團隊中的一個職位：

- **ProductManager**: 分析需求，撰寫 PRD
- **Architect**: 設計架構，定義接口
- **Engineer**: 實現代碼，遵循設計
- **QA Engineer**: 編寫測試，保證質量

### Action（行為）

角色執行的具體動作：

- **WritePRD**: 生成產品需求文檔
- **WriteDesign**: 生成系統設計文檔
- **WriteCode**: 生成代碼實現
- **WriteTest**: 生成測試用例

### Message（消息）

角色間通過結構化消息傳遞信息，確保信息完整性。

## 🛠️ 配置選項

### 模型配置

```yaml
llm:
  api_type: "openai"
  model: "gpt-4"              # 或 gpt-3.5-turbo
  temperature: 0.7
  max_tokens: 4096
```

### 工作區配置

```yaml
workspace:
  path: "./workspace"
  use_git: true
```

### 角色配置

```yaml
roles:
  product_manager: true
  architect: true
  engineer: true
  qa_engineer: false          # 節省成本可禁用
```

## 📊 成本估算

| 項目類型 | 使用模型 | 預估成本 | 預估時間 |
|---------|---------|---------|---------|
| 簡單 CLI 工具 | GPT-3.5-turbo | $1-2 | 5-8 分鐘 |
| 中型 Web 應用 | GPT-4 | $5-10 | 10-20 分鐘 |
| 複雜系統 | GPT-4 + 多輪 | $15-30 | 20-40 分鐘 |

> 💡 **成本優化提示**:
> - 開發測試階段使用 GPT-3.5-turbo
> - 只在需要高質量輸出時使用 GPT-4
> - 限制最大輪數避免無限循環

## ⚠️ 注意事項

### 使用前必讀

1. **API 成本**: MetaGPT 會進行多次 LLM 調用，請注意控制成本
2. **輸出質量**: 生成的代碼需要人工審核和測試
3. **適用範圍**: 主要適合中小型項目和原型開發
4. **模型選擇**: GPT-4 效果更好，但成本更高
5. **網絡要求**: 需要穩定的網絡連接

### 常見問題

<details>
<summary><b>Q: 如何降低使用成本？</b></summary>

A:
- 使用 GPT-3.5-turbo 而非 GPT-4
- 設置預算上限 `team.invest()`
- 限制運行輪數 `n_round=3`
- 減少使用的角色數量
- 簡化項目需求
</details>

<details>
<summary><b>Q: 生成的代碼質量如何？</b></summary>

A:
- 使用 GPT-4 質量較好
- 需求描述越詳細，質量越高
- 建議人工審核和優化
- 適合作為起點，不是最終產品
</details>

<details>
<summary><b>Q: 支持哪些編程語言？</b></summary>

A:
- 主要支持 Python
- 也支持其他主流語言（JavaScript、Go、Java 等）
- 效果依賴於所用 LLM 的訓練數據
</details>

<details>
<summary><b>Q: 如何處理生成失敗？</b></summary>

A:
- 檢查 API 密鑰配置
- 確認網絡連接正常
- 簡化需求重試
- 查看日誌了解錯誤原因
- 增加預算或輪數限制
</details>

## 🔗 學習資源

### 官方資源

- 📚 [MetaGPT GitHub](https://github.com/geekan/MetaGPT) - 官方倉庫
- 📖 [官方文檔](https://docs.deepwisdom.ai/) - 完整文檔
- 📄 [研究論文](https://arxiv.org/abs/2308.00352) - 理論基礎
- 💬 [討論區](https://github.com/geekan/MetaGPT/discussions) - 社群討論

### 推薦閱讀

- [Multi-Agent 系統設計](https://github.com/geekan/MetaGPT/blob/main/docs/ROADMAP.md)
- [最佳實踐指南](https://github.com/geekan/MetaGPT/blob/main/docs/tutorial/)
- [示例項目集合](https://github.com/geekan/MetaGPT/tree/main/examples)

## 🤝 貢獻

歡迎貢獻新的教程、範例和改進建議！

## 📄 許可證

本教程基於 MIT 許可證開源。

---

<div align="center">

**開始你的 MetaGPT 學習之旅！** 🚀

從 [0.基礎概念](./0.基礎概念.ipynb) 開始學習

</div>
