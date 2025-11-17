# 📚 代碼示例

本目錄包含各種使用場景的代碼示例，幫助你快速上手銷售外展自動化系統。

## 示例列表

### 1. basic_usage.py
基礎使用示例，展示如何：
- 初始化系統
- 從 CRM 讀取潛在客戶
- 生成並發送郵件
- 更新 CRM 狀態

**適合**：首次使用者、快速原型

### 2. custom_agent.py
自定義 Agent 示例，展示如何：
- 創建自定義的 Agent
- 整合到 LangGraph 工作流
- 添加自定義邏輯

**適合**：需要擴展功能的開發者

### 3. batch_processing.py
批量處理示例，展示如何：
- 並行處理大量客戶
- 優化性能
- 處理錯誤和重試

**適合**：處理大規模客戶列表

## 運行示例

### 前置條件

確保已完成以下步驟：

1. 安裝依賴
```bash
cd ../sales-outreach-automation-langgraph
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. 配置環境變數
```bash
# 編輯 .env 文件
cp .env.example .env
# 填入你的 API 金鑰
```

3. 設置 Google 憑證
```bash
# 下載 credentials.json 並放到專案根目錄
```

### 運行示例

```bash
# 基礎使用
python examples/basic_usage.py

# 自定義 Agent
python examples/custom_agent.py

# 批量處理
python examples/batch_processing.py
```

## 注意事項

⚠️ **重要**：
- 這些示例僅供學習和測試
- 在生產環境使用前，請仔細測試
- 確保遵守相關法律法規和郵件發送最佳實踐

## 獲取幫助

- 查看 [troubleshooting.md](../docs/troubleshooting.md) 解決問題
- 查看 [best-practices.md](../docs/best-practices.md) 了解最佳實踐
- 查看 [architecture.md](../docs/architecture.md) 了解系統設計
