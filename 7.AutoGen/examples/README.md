# AutoGen 示例代碼

這個目錄包含了各種 AutoGen 使用示例，從簡單到複雜，幫助你快速上手。

## 📁 示例列表

### 1. `simple_chat.py` - 簡單對話
**難度**: ⭐
**描述**: 最基礎的 AutoGen 對話示例
**學習內容**:
- 創建 AssistantAgent
- 創建 UserProxyAgent
- 發起對話

**運行**:
```bash
python simple_chat.py
```

---

### 2. `code_execution.py` - 代碼執行
**難度**: ⭐⭐
**描述**: 展示如何讓 Agent 生成並執行代碼
**學習內容**:
- 配置代碼執行環境
- 生成 Python 代碼
- 執行並查看結果
- 處理多個任務

**運行**:
```bash
python code_execution.py
```

**注意**: 會在 `coding/` 目錄下生成文件

---

### 3. `group_chat.py` - 群組對話
**難度**: ⭐⭐⭐
**描述**: 多個 Agent 協作完成任務
**學習內容**:
- 創建多個專業 Agent
- GroupChat 配置
- GroupChatManager 使用
- 協作流程管理

**運行**:
```bash
python group_chat.py
```

---

### 4. `function_calling.py` - 函數調用
**難度**: ⭐⭐⭐
**描述**: Agent 調用外部函數和工具
**學習內容**:
- 定義工具函數
- 配置函數調用
- function_map 使用
- 多工具協作

**運行**:
```bash
python function_calling.py
```

---

## 🚀 快速開始

### 1. 環境準備

```bash
# 安裝依賴
pip install pyautogen python-dotenv

# 配置環境變量
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### 2. 運行示例

```bash
# 進入 examples 目錄
cd examples

# 運行任一示例
python simple_chat.py
```

## 📚 學習路徑

### 初學者
1. 先運行 `simple_chat.py` 理解基本概念
2. 嘗試 `code_execution.py` 學習代碼執行
3. 閱讀代碼註釋，理解每個參數的作用

### 進階者
1. 學習 `group_chat.py` 的多 Agent 協作
2. 研究 `function_calling.py` 的工具調用
3. 嘗試修改示例，添加新功能

### 高級用戶
1. 結合多個示例的特性
2. 構建自己的 Agent 系統
3. 參考 [實戰項目案例](../7.實戰項目案例.md) 構建完整項目

## 💡 使用技巧

### 修改 LLM 模型

```python
# 使用 GPT-3.5 (更便宜)
config_list = [
    {
        "model": "gpt-3.5-turbo",
        "api_key": os.getenv("OPENAI_API_KEY")
    }
]

# 使用本地模型 (零成本)
config_list = [
    {
        "model": "llama2",
        "api_base": "http://localhost:11434/v1",
        "api_key": "ollama"
    }
]
```

### 啟用 Docker 隔離

```python
code_execution_config={
    "work_dir": "coding",
    "use_docker": True,  # 啟用 Docker
    "docker_image": "python:3.11-slim"
}
```

### 調試模式

```python
import logging

logging.basicConfig(level=logging.INFO)
```

## ⚠️ 常見問題

### Q: API 密鑰錯誤
**A**: 檢查 `.env` 文件中的 API 密鑰是否正確

### Q: 代碼執行失敗
**A**: 確保工作目錄有寫入權限，或啟用 Docker

### Q: 對話無法結束
**A**: 檢查 `is_termination_msg` 和 `max_consecutive_auto_reply` 設置

### Q: 成本過高
**A**:
- 使用 `gpt-3.5-turbo` 而非 `gpt-4`
- 設置 `max_tokens` 限制
- 使用本地模型

## 🔗 相關資源

- [基礎對話教程](../0.基礎對話.ipynb)
- [進階協作模式](../1.進階Agent協作模式.md)
- [實戰項目案例](../7.實戰項目案例.md)
- [故障排除指南](../6.故障排除與最佳實踐.md)

## 🤝 貢獻

歡迎貢獻新的示例！請確保：
- 代碼清晰、有註釋
- 包含使用說明
- 測試通過

## 📄 許可證

MIT License - 自由使用和修改
