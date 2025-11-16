# 智能客服機器人

基於 LangChain + LangGraph 構建的智能客服系統，具備多輪對話、意圖識別、知識庫檢索和工單管理等功能。

## 功能特點

### 1. 智能意圖識別
- 自動識別用戶意圖（查詢、投訴、工單）
- 情感分析（積極、中性、消極）
- 動態路由到對應處理流程

### 2. 知識庫檢索
- 基於 RAG 的 FAQ 問答
- 向量語義搜索
- 自動匹配最相關答案

### 3. 投訴處理
- 專業的客訴處理話術
- 自動創建優先工單
- 同理心回應

### 4. 工單管理
- 自動生成工單編號
- 記錄完整對話歷史
- 預計響應時間通知

### 5. 多輪對話
- 保持對話上下文
- 會話狀態管理
- 自然的交互體驗

## 架構設計

```
┌─────────────┐
│  用戶輸入    │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  意圖分類器      │
│  - 意圖識別      │
│  - 情感分析      │
└────────┬────────┘
         │
    ┌────┴────┐
    │ 路由器   │
    └────┬────┘
         │
    ┌────┴────────────────┐
    │                     │
    ▼                     ▼
┌────────┐         ┌─────────┐
│知識庫  │         │投訴處理  │
│查詢    │         │         │
└────┬───┘         └────┬────┘
     │                  │
     ▼                  ▼
┌─────────────┐   ┌──────────┐
│  生成回答    │   │創建工單   │
└─────────────┘   └──────────┘
```

## 快速開始

### 1. 安裝依賴

```bash
# 安裝所需套件
pip install -r requirements.txt
```

### 2. 配置環境變數

```bash
# 創建 .env 文件
cp .env.example .env

# 編輯 .env，添加你的 API Key
export OPENAI_API_KEY='your-openai-api-key'
```

### 3. 運行程序

```bash
# 運行客服機器人
python main.py
```

## 使用範例

### 範例 1：一般查詢

```
👤 您: 如何重設密碼？

🤖 助手: 重設密碼很簡單！請按照以下步驟操作：

1. 前往登入頁面
2. 點擊「忘記密碼」連結
3. 輸入您註冊時使用的電子郵件地址
4. 查收郵件並點擊重設密碼連結
5. 設定新密碼

如果沒有收到郵件，請檢查垃圾郵件資料夾，或聯繫我們進一步協助。
```

### 範例 2：投訴處理

```
👤 您: 我收到的商品有損壞，非常不滿意！

🎯 檢測到意圖: complaint, 情感: negative

🤖 助手: 非常抱歉給您帶來不便！我完全理解您的不滿。

我們會立即處理這個問題：

1. 我已為您創建優先處理工單
2. 請提供損壞商品的照片（如有）
3. 我們將安排：
   - 免費退貨/換貨服務
   - 運費由我們承擔
   - 如需補償，將由專員評估

📋 我已為您創建優先處理工單（編號：TICKET-20250116123456），
我們的專員會在 24 小時內與您聯繫。
```

### 範例 3：複雜問題

```
👤 您: 我想客製化大量訂單，需要特殊包裝和物流安排

🎯 檢測到意圖: create_ticket, 情感: neutral

🤖 助手: 我理解您的需求。由於這個問題需要更詳細的處理，
我已為您創建工單。

📋 工單編號：TICKET-20250116123457
⏰ 預計響應時間：2 個工作小時內
📧 您將收到電子郵件通知

我們的專業客服團隊會盡快與您聯繫。您還有其他問題嗎？
```

## 配置說明

### 修改 FAQ 知識庫

在 `main.py` 的 `initialize_knowledge_base()` 函數中修改 `faq_data` 列表：

```python
faq_data = [
    "問：你的問題？\n答：相應的答案",
    # 添加更多 FAQ...
]
```

### 調整模型參數

```python
# 使用不同的模型
llm = ChatOpenAI(
    model="gpt-4",  # 或 "gpt-3.5-turbo"
    temperature=0.7  # 調整創造性 (0-1)
)
```

### 自定義意圖類別

在 `detect_intent()` 函數中修改意圖類別：

```python
valid_intents = ["query", "complaint", "create_ticket", "your_custom_intent"]
```

並在圖中添加對應的處理節點。

## 進階功能

### 1. 整合真實數據庫

替換 `create_ticket()` 函數中的模擬實現：

```python
def create_ticket(messages, session_id):
    # 連接到你的數據庫
    import sqlite3
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()

    # 插入工單記錄
    cursor.execute("""
        INSERT INTO tickets (ticket_id, session_id, description, created_at)
        VALUES (?, ?, ?, ?)
    """, (ticket_id, session_id, description, datetime.now()))

    conn.commit()
    conn.close()

    return ticket_id
```

### 2. 添加更多向量數據庫選項

```python
# 使用 Pinecone
from langchain_community.vectorstores import Pinecone

vectorstore = Pinecone.from_documents(
    documents=splits,
    embedding=embeddings,
    index_name="customer-service"
)

# 使用 FAISS
from langchain_community.vectorstores import FAISS

vectorstore = FAISS.from_documents(
    documents=splits,
    embedding=embeddings
)
```

### 3. 整合 Web 界面

使用 Streamlit 或 FastAPI 創建 Web 界面：

```python
# 使用 Streamlit
import streamlit as st

st.title("智能客服機器人")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 顯示對話歷史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 用戶輸入
if prompt := st.chat_input("請輸入您的問題"):
    # 處理並顯示回應
    ...
```

### 4. 添加多語言支持

```python
def detect_language(text):
    from langdetect import detect
    return detect(text)

def translate_if_needed(text, target_lang="zh-TW"):
    # 使用翻譯 API
    ...
```

## 性能優化

### 1. 緩存向量存儲

```python
import pickle

# 保存向量存儲
vectorstore.persist()

# 加載已有的向量存儲
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)
```

### 2. 批量處理

對於高並發場景，使用異步處理：

```python
import asyncio
from langchain.callbacks.manager import AsyncCallbackManager

async def ahandle_request(user_input):
    # 異步處理請求
    ...
```

### 3. 使用更便宜的模型

```python
# 意圖分類使用較小模型
intent_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 回答生成使用較大模型
response_llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
```

## 測試

運行測試用例：

```bash
python test_customer_service.py
```

## 部署

### Docker 部署

```bash
# 構建鏡像
docker build -t customer-service-bot .

# 運行容器
docker run -d \
  -e OPENAI_API_KEY=your_key \
  -p 8000:8000 \
  customer-service-bot
```

### 生產環境建議

1. **使用專業向量數據庫**: Pinecone、Weaviate
2. **添加日誌系統**: ELK Stack、CloudWatch
3. **設置監控**: Prometheus、Grafana
4. **實現負載均衡**: Nginx、AWS ALB
5. **數據備份**: 定期備份對話記錄和工單

## 常見問題

### Q1: 如何提高回答準確性？

1. 增加 FAQ 數據量
2. 優化文本分塊策略
3. 調整檢索參數 `k` 值
4. 使用更好的 embedding 模型

### Q2: 如何處理超長對話？

使用對話摘要：

```python
from langchain.chains.summarize import load_summarize_chain

# 當對話超過一定長度時，生成摘要
if len(messages) > 10:
    summary = summarize_chain.run(messages)
```

### Q3: 如何評估系統性能？

```python
# 記錄關鍵指標
metrics = {
    "response_time": response_time,
    "intent_accuracy": intent_accuracy,
    "user_satisfaction": user_rating,
    "ticket_rate": tickets_created / total_sessions
}
```

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 授權

MIT License

## 聯絡

如有問題，請聯繫：support@example.com
