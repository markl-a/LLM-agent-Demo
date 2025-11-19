# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-11-19

### Added
- **CrewAI 框架** - 新增 CrewAI 角色扮演 AI Agent 協作框架，共 20 個示例
  - 基礎入門示例 (1-5): 快速開始、角色定義、任務設計、團隊組建、工具使用
  - 核心功能示例 (6-10): 順序流程、層級流程、記憶管理、協作模式、結果處理
  - 進階應用示例 (11-15): 自定義工具、異步執行、錯誤處理、性能優化、監控日誌
  - 實戰場景示例 (16-20): 內容創作團隊、市場分析團隊、軟體開發團隊、客戶服務團隊、最佳實踐
- **18.CrewAI/** - 新增 CrewAI 專用目錄，包含完整的 README 和 requirements.txt
- **完整示例實現** - 01_快速開始.py 和 02_角色定義.py 完整可運行實現

### Changed
- **項目規模擴展** - 從 120 個示例擴展至 140 個示例
- **框架數量增加** - 從 6 個框架增加至 7 個框架
- **更新 README.md** - 更新主 README 統計數據和框架表格
- **更新 PROJECT_SUMMARY.md** - 全面更新項目總結，包含 CrewAI 信息
- **更新 QUICKSTART.md** - 新增 CrewAI 快速開始選項和學習路徑
- **更新依賴管理** - requirements.txt 新增 CrewAI 相關依賴

### Documentation
- **CrewAI README** - 新增詳細的 CrewAI 教程文檔，包含:
  - 完整的框架介紹和核心概念
  - 20 個示例索引和難度分級
  - 與其他框架的對比分析
  - 最佳實踐和常見問題
- **框架選擇指南** - 更新框架選擇建議，包含 CrewAI 應用場景
- **官方文檔鏈接** - 新增 CrewAI 官方文檔鏈接

### Features Highlight
- **角色扮演支持** - CrewAI 提供原生的 Agent 角色扮演能力
- **簡潔的團隊協作 API** - 使用 Agent、Task、Crew 三個核心概念
- **多種執行流程** - 支持 Sequential 和 Hierarchical 兩種流程模式
- **豐富的工具生態** - 與 LangChain 工具生態完全兼容

## [1.1.0] - 2025-11-19

### Added
- **LangGraph 框架** - 新增 LangGraph 狀態管理框架，共 20 個完整示例
  - 基礎入門示例 (1-5): 狀態圖基礎、節點與邊、條件路由、循環控制、檢查點
  - 核心功能示例 (6-10): 並行執行、子圖、工具集成、記憶管理、錯誤處理
  - 進階應用示例 (11-15): 人機協作、多 Agent 協作、流式輸出、持久化、自定義狀態
  - 實戰場景示例 (16-20): 客服機器人、研究助手、代碼審查、工作流自動化、最佳實踐
- **17.LangGraph/** - 新增 LangGraph 專用目錄，包含完整的 README 和 requirements.txt
- **完整示例實現** - 01_狀態圖基礎.py 和 02_節點與邊.py 完整可運行實現

### Changed
- **項目規模擴展** - 從 100 個示例擴展至 120 個示例
- **框架數量增加** - 從 5 個框架增加至 6 個框架
- **更新 README.md** - 更新主 README 統計數據和框架表格
- **更新 PROJECT_SUMMARY.md** - 全面更新項目總結，包含 LangGraph 信息
- **更新依賴管理** - requirements.txt 新增 LangGraph 相關依賴
- **更新學習路徑** - 調整初學者和進階學習路徑建議

### Documentation
- **LangGraph README** - 新增詳細的 LangGraph 教程文檔
- **框架選擇指南** - 更新框架選擇建議，包含 LangGraph 應用場景
- **官方文檔鏈接** - 新增 LangGraph 官方文檔鏈接

## [1.0.0] - 2025-11-18

### Added
- **5 個主流 AI Agent 框架** - 完成所有主流框架的集成
  - Semantic Kernel (Microsoft 官方) - 20 個示例
  - LangFlow (可視化平台) - 20 個示例
  - Haystack (RAG 專注) - 20 個示例
  - AutoGPT (自主 Agent) - 20 個示例
  - OpenAI Swarm (輕量級協作) - 20 個示例
- **100 個完整示例** - 每個框架 20 個可運行的實用示例
- **完整文檔體系**
  - 主 README.md - 項目概覽和快速導航
  - PROJECT_SUMMARY.md - 詳細的項目總結
  - QUICKSTART.md - 快速開始指南
  - CONTRIBUTING.md - 貢獻者指南
  - 每個框架的詳細 README
- **依賴管理** - requirements.txt 包含所有必要依賴
- **環境配置** - .env.example 完整的環境變數範例
- **Git 配置** - .gitignore 完善的忽略規則

### Framework Details

#### Semantic Kernel (12.Semantic Kernel/)
- 基礎入門 (1-5): 快速開始、多 LLM、流式輸出、提示詞工程、記憶管理
- 核心功能 (6-10): 函數調用、規劃器、RAG、錯誤處理、內容生成
- 進階應用 (11-15): 翻譯摘要、數據分析、多 Agent、聊天機器人、情感分析
- 實戰場景 (16-20): 文檔處理、郵件自動化、API 集成、知識庫、高級優化

#### LangFlow (13.LangFlow/)
- 基礎入門 (1-5): Python 集成、Flow 創建、RAG 系統、Agent 系統、聊天記憶
- 核心功能 (6-10): 數據處理、API 集成、自定義組件、測試部署、流式輸出
- 進階應用 (11-15): 多模態、錯誤處理、模型比較、向量數據庫、Web 搜索
- 實戰場景 (16-20): SQL 數據庫、文檔分析、情感分析、翻譯服務、監控日誌

#### Haystack (14.Haystack/)
- 基礎入門 (1-5): RAG 基礎、文檔處理、檢索器、Pipeline 構建、問答系統
- 核心功能 (6-10): 嵌入模型、文檔存儲、Ranker、生成器、路由器
- 進階應用 (11-15): Web 檢索、評估系統、Agent 代理、流式處理、自定義組件
- 實戰場景 (16-20): 多語言、提示詞管理、錯誤處理、性能優化、部署監控

#### AutoGPT (15.AutoGPT/)
- 基礎入門 (1-5): 自主 Agent、目標規劃、記憶系統、工具集成、任務執行
- 核心功能 (6-10): 自我反思、成本控制、循環檢測、優先級管理、錯誤恢復
- 進階應用 (11-15): 知識獲取、代碼生成、文件操作、Web 瀏覽、數據分析
- 實戰場景 (16-20): 命令執行、性能監控、多 Agent 協作、安全控制、最佳實踐

#### OpenAI Swarm (16.OpenAI Swarm/)
- 基礎入門 (1-5): 多 Agent 協作、Agent 切換、上下文變量、函數工具、對話歷史
- 核心功能 (6-10): 路由邏輯、狀態管理、錯誤處理、流式響應、並發 Agent
- 進階應用 (11-15): 自定義 Agent、工作流程、性能優化、日誌記錄、測試示例
- 實戰場景 (16-20): 多輪對話、意圖識別、監控儀表板、部署配置、最佳實踐

### Technical Stack
- Python 3.8+
- OpenAI GPT-4/3.5
- Anthropic Claude
- Google Gemini
- 向量數據庫 (Chroma, Pinecone, Weaviate)
- LangChain 生態系統

### Documentation Statistics
- 總文件數: 105+ 文件
- 總代碼行數: ~15,000+ 行
- 總文檔字數: ~50,000+ 字
- 覆蓋場景數: 100+ 個

## [0.1.0] - 2025-11-18

### Added
- 初始項目結構
- 基礎配置文件
- Git 倉庫初始化

---

## 版本說明

### 版本號格式: MAJOR.MINOR.PATCH

- **MAJOR**: 重大變更，可能不向後兼容
- **MINOR**: 新增功能，向後兼容
- **PATCH**: Bug 修復，向後兼容

### 變更類型

- **Added**: 新增功能
- **Changed**: 現有功能的變更
- **Deprecated**: 即將移除的功能
- **Removed**: 已移除的功能
- **Fixed**: Bug 修復
- **Security**: 安全性相關變更

---

## 未來計劃

### [1.2.0] - 計劃中
- [ ] 新增 CrewAI 框架 (20 個示例)
- [ ] 新增實戰項目集
- [ ] 統一示例運行腳本
- [ ] 框架詳細對比文檔

### [1.3.0] - 規劃中
- [ ] 測試覆蓋率提升
- [ ] CI/CD 集成
- [ ] 性能優化示例
- [ ] 多語言文檔

### [2.0.0] - 長期規劃
- [ ] 完整課程體系
- [ ] 在線互動教程
- [ ] 企業級解決方案
- [ ] 社區建設

---

## 貢獻指南

如果你想為項目做出貢獻，請查看 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 問題報告

如果你發現 bug 或有功能建議，請在 [GitHub Issues](https://github.com/markl-a/LLM-agent-Demo/issues) 中提出。

---

**維護者**: LLM Agent Demo Team
**許可證**: MIT License
