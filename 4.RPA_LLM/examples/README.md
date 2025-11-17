# 程式碼範例

本目錄包含完整的可執行範例，幫助你快速上手 RPA + LLM 開發。

## 範例列表

### 1. 基礎 RPA 範例
- `01_hello_rpa.py` - Hello World 範例
- `02_web_scraping.py` - 網頁數據採集
- `03_excel_automation.py` - Excel 自動化

### 2. LLM 整合範例
- `11_llm_basic.py` - LLM 基礎使用
- `12_data_extraction.py` - 智能數據提取
- `13_prompt_engineering.py` - Prompt 工程技巧

### 3. 完整專案範例
- `21_invoice_processor/` - 發票處理系統
- `22_email_automation/` - 郵件自動化
- `23_customer_service_bot/` - 客服機器人

## 使用說明

1. 安裝依賴：
```bash
pip install -r ../requirements.txt
```

2. 配置環境變數：
```bash
cp .env.example .env
# 編輯 .env 填入你的 API 金鑰
```

3. 運行範例：
```bash
python 01_hello_rpa.py
```

## 學習路徑

建議按以下順序學習：

1. **第一週**：基礎 RPA (01-03)
2. **第二週**：LLM 整合 (11-13)
3. **第三週**：完整專案 (21-23)

每個範例都包含詳細註釋，建議邊看邊實踐。

## 常見問題

**Q: 範例無法運行？**
A: 檢查是否正確安裝依賴和配置環境變數

**Q: API 調用失敗？**
A: 確認 API 金鑰有效，檢查網路連接

**Q: 如何修改範例？**
A: 所有範例都可以自由修改，建議先複製一份再修改

## 貢獻

歡迎提交新的範例或改進現有範例！

## 授權

本目錄下所有範例代碼採用 MIT 授權，可自由使用。
