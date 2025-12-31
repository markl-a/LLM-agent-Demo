# Chainlit 框架完整範例

## 框架簡介

Chainlit 是一個專為 LLM 應用設計的現代化 UI 框架，讓開發者能夠快速構建美觀、互動性強的聊天界面和 AI 應用。與 Gradio、Streamlit 不同，Chainlit 專注於對話式 AI 應用，提供原生的聊天界面、流式響應和豐富的互動元素。

### 核心特點

#### 1. 專為 LLM 應用設計 💬
- 原生聊天界面，無需額外配置
- 自動處理對話歷史
- 完美支持流式響應
- 多輪對話管理

```python
import chainlit as cl

@cl.on_message
async def main(message: cl.Message):
    # 自動處理消息和響應
    await cl.Message(content=f"收到: {message.content}").send()
```

#### 2. 美觀的現代化界面 🎨
- 精心設計的 UI 組件
- 響應式布局
- 深色/淺色主題
- 可自定義品牌元素
- 專業的用戶體驗

#### 3. 豐富的互動元素 🎯
- 文件上傳（支持多種格式）
- 圖片展示
- 代碼高亮
- 表格渲染
- 音頻/視頻播放
- 自定義元素

```python
# 圖片展示
image = cl.Image(path="./chart.png", name="分析結果")
await cl.Message(content="這是分析圖表", elements=[image]).send()

# 文件上傳
@cl.on_file_upload
async def handle_file(file):
    # 處理上傳的文件
    pass
```

#### 4. 流式響應支持 ⚡
- 即時顯示 LLM 輸出
- 更好的用戶體驗
- 減少等待時間
- 支持 Token 級別流式傳輸

```python
msg = cl.Message(content="")
await msg.send()

# 流式更新
for token in stream:
    await msg.stream_token(token)
```

#### 5. 多步驟流程展示 📊
- 可視化執行步驟
- 進度追蹤
- 嵌套步驟支持
- 執行時間統計

```python
async with cl.Step(name="數據處理") as step:
    step.output = "處理完成"
```

#### 6. 用戶認證系統 🔐
- 內建認證機制
- OAuth 整合
- 自定義認證邏輯
- 用戶會話管理

#### 7. LangChain 原生整合 🔗
- 無縫整合 LangChain
- 自動展示 Chain 執行過程
- Tool 調用可視化
- Agent 行為追蹤

```python
from langchain.chains import LLMChain
from chainlit.langchain import LangchainCallbackHandler

chain = LLMChain(...)
await chain.arun(
    query,
    callbacks=[LangchainCallbackHandler()]
)
```

#### 8. 部署簡單 🚀
- 一鍵部署到 Chainlit Cloud
- 支持 Docker 容器化
- 可部署到主流雲平台
- WebSocket 支持

## 安裝指南

### 基礎安裝
```bash
pip install chainlit
```

### 完整安裝（包含 LangChain）
```bash
pip install chainlit langchain openai
```

### 開發環境設置
```bash
# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安裝依賴
pip install -r requirements.txt

# 設置環境變量
export OPENAI_API_KEY='your-key-here'
```

## 快速開始

### 第一個 Chainlit 應用

創建 `app.py`：

```python
import chainlit as cl

@cl.on_chat_start
async def start():
    await cl.Message(content="歡迎使用 Chainlit！").send()

@cl.on_message
async def main(message: cl.Message):
    await cl.Message(content=f"你說: {message.content}").send()
```

運行應用：
```bash
chainlit run app.py -w
```

訪問 http://localhost:8000 查看應用。

### 與 OpenAI 整合

```python
import chainlit as cl
from openai import AsyncOpenAI

client = AsyncOpenAI()

@cl.on_message
async def main(message: cl.Message):
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": message.content}]
    )

    await cl.Message(content=response.choices[0].message.content).send()
```

### 流式響應

```python
@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="")
    await msg.send()

    stream = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": message.content}],
        stream=True
    )

    async for chunk in stream:
        if chunk.choices[0].delta.content:
            await msg.stream_token(chunk.choices[0].delta.content)

    await msg.update()
```

## 與其他框架對比

### Chainlit vs Gradio

| 特性 | Chainlit | Gradio |
|------|----------|--------|
| **主要用途** | 聊天式 AI 應用 | 通用機器學習 Demo |
| **界面風格** | 專業聊天界面 | 表單式界面 |
| **流式響應** | 原生支持 | 需要額外配置 |
| **對話歷史** | 自動管理 | 需手動處理 |
| **LangChain 整合** | 深度整合 | 基礎支持 |
| **學習曲線** | 低 | 非常低 |
| **適用場景** | ChatGPT 類應用 | ML 模型展示 |

**Gradio 優勢：**
- 更簡單的表單式界面
- 快速原型開發
- 更多輸入/輸出組件
- HuggingFace Spaces 整合

**Chainlit 優勢：**
- 專業的聊天體驗
- 更好的對話管理
- 豐富的消息元素
- Agent 行為可視化

### Chainlit vs Streamlit

| 特性 | Chainlit | Streamlit |
|------|----------|-----------|
| **應用類型** | 對話式 AI | 數據儀表板 |
| **運行模式** | 異步 | 同步 |
| **狀態管理** | 會話自動管理 | 需 session_state |
| **實時更新** | WebSocket | 重新運行腳本 |
| **聊天界面** | 原生支持 | 需 st.chat_message |
| **部署** | Chainlit Cloud | Streamlit Cloud |
| **性能** | 高（異步） | 中（同步） |

**Streamlit 優勢：**
- 強大的數據可視化
- 豐富的組件生態
- 更適合數據應用
- 更大的社區

**Chainlit 優勢：**
- 專為 LLM 設計
- 更好的異步支持
- 原生聊天體驗
- 更好的流式處理

### 選擇建議

**選擇 Chainlit：**
- 構建 ChatGPT 類應用
- 需要專業聊天界面
- Agent/Chain 可視化需求
- 多輪對話應用
- 客服機器人
- AI 助手應用

**選擇 Gradio：**
- 快速 ML 模型 Demo
- 簡單的輸入輸出應用
- 需要 HuggingFace 整合
- 非對話式應用

**選擇 Streamlit：**
- 數據分析儀表板
- 內部工具開發
- 需要複雜的數據可視化
- BI 報表應用

## 範例文件導覽

### 基礎篇

#### 01_快速開始.py
- Chainlit 基本結構
- 生命週期鉤子
- 消息發送和接收
- Hello World 示例

#### 02_對話界面.py
- 聊天界面配置
- 對話歷史管理
- 用戶會話處理
- 消息類型

#### 03_流式響應.py
- Token 級別流式傳輸
- OpenAI 流式整合
- 進度展示
- 錯誤處理

#### 04_文件上傳.py
- 文件上傳處理
- 支持的文件類型
- 文件解析
- 圖片/PDF 處理

### 進階篇

#### 05_多步驟.py
- Step 組件使用
- 嵌套步驟
- 進度追蹤
- 執行時間統計

#### 06_自定義元素.py
- 圖片元素
- 文件元素
- 代碼塊
- 表格展示
- 自定義組件

#### 07_用戶認證.py
- 認證系統配置
- OAuth 整合
- 自定義認證邏輯
- 用戶權限管理

#### 08_LangChain整合.py
- LangChain Callback
- Chain 執行可視化
- Tool 調用追蹤
- Agent 行為展示

### 高級篇

#### 09_Agent界面.py
- Agent 對話界面
- 工具調用展示
- 思考過程可視化
- 多 Agent 協作

#### 10_部署上線.py
- Chainlit Cloud 部署
- Docker 容器化
- 環境配置
- 生產環境最佳實踐

## 核心概念

### 生命週期鉤子

Chainlit 提供多個鉤子函數控制應用流程：

```python
@cl.on_chat_start
async def start():
    """用戶開始新會話時調用"""
    await cl.Message(content="歡迎！").send()

@cl.on_message
async def main(message: cl.Message):
    """接收到用戶消息時調用"""
    await cl.Message(content="收到").send()

@cl.on_chat_end
async def end():
    """會話結束時調用"""
    print("會話結束")

@cl.on_stop
async def stop():
    """用戶停止執行時調用"""
    print("執行已停止")
```

### 消息系統

```python
# 簡單消息
await cl.Message(content="Hello").send()

# 帶元素的消息
image = cl.Image(path="image.png", name="圖片")
await cl.Message(
    content="查看圖片",
    elements=[image]
).send()

# 流式消息
msg = cl.Message(content="")
await msg.send()
await msg.stream_token("token")
await msg.update()
```

### 步驟系統

```python
async with cl.Step(name="步驟 1") as step:
    step.input = "輸入數據"
    # 執行邏輯
    step.output = "輸出結果"

    # 嵌套步驟
    async with cl.Step(name="子步驟") as substep:
        substep.output = "子結果"
```

### 用戶會話

```python
@cl.on_chat_start
async def start():
    # 存儲會話數據
    cl.user_session.set("key", "value")

@cl.on_message
async def main(message: cl.Message):
    # 獲取會話數據
    value = cl.user_session.get("key")
```

### 自定義配置

創建 `.chainlit/config.toml`：

```toml
[project]
name = "My AI App"
enable_telemetry = false

[UI]
name = "My Assistant"
default_collapse_content = true
default_expand_messages = false

[features]
spontaneous_file_upload = {
    enabled = true,
    accept = ["image/*", "application/pdf"]
}
```

## 最佳實踐

### 1. 錯誤處理

```python
@cl.on_message
async def main(message: cl.Message):
    try:
        # 處理邏輯
        result = await process(message.content)
        await cl.Message(content=result).send()
    except Exception as e:
        await cl.Message(
            content=f"❌ 錯誤: {str(e)}"
        ).send()
```

### 2. 超時控制

```python
import asyncio

@cl.on_message
async def main(message: cl.Message):
    try:
        result = await asyncio.wait_for(
            long_running_task(message.content),
            timeout=30.0
        )
        await cl.Message(content=result).send()
    except asyncio.TimeoutError:
        await cl.Message(content="操作超時").send()
```

### 3. 進度反饋

```python
@cl.on_message
async def main(message: cl.Message):
    async with cl.Step(name="處理中") as step:
        step.output = "步驟 1: 載入數據..."
        await asyncio.sleep(1)

        step.output = "步驟 2: 分析..."
        await asyncio.sleep(1)

        step.output = "完成！"
```

### 4. 會話數據管理

```python
@cl.on_chat_start
async def start():
    # 初始化會話
    cl.user_session.set("messages", [])
    cl.user_session.set("user_name", "User")

@cl.on_message
async def main(message: cl.Message):
    # 管理對話歷史
    messages = cl.user_session.get("messages")
    messages.append({
        "role": "user",
        "content": message.content
    })
    cl.user_session.set("messages", messages)
```

### 5. 性能優化

- 使用異步操作
- 合理使用流式響應
- 避免阻塞主線程
- 適當的緩存策略

```python
# 好的做法：異步
@cl.on_message
async def main(message: cl.Message):
    result = await async_llm_call(message.content)
    await cl.Message(content=result).send()

# 避免：同步阻塞
@cl.on_message
async def main(message: cl.Message):
    result = sync_blocking_call(message.content)  # 不推薦
    await cl.Message(content=result).send()
```

## 常見問題

### Q: Chainlit 與 FastAPI 可以一起使用嗎？

**A:** 可以，Chainlit 基於 FastAPI 構建，可以輕鬆整合：

```python
from fastapi import FastAPI
import chainlit as cl

app = FastAPI()

@app.get("/api/status")
async def status():
    return {"status": "ok"}

# Chainlit 邏輯
@cl.on_message
async def main(message: cl.Message):
    await cl.Message(content="Hello").send()
```

### Q: 如何處理大文件上傳？

**A:** 配置文件大小限制和處理邏輯：

```python
# config.toml
[features]
spontaneous_file_upload = {
    enabled = true,
    max_size_mb = 100
}

# app.py
@cl.on_file_upload
async def handle_file(file):
    # 分塊處理大文件
    pass
```

### Q: 如何部署到生產環境？

**A:**

1. **Chainlit Cloud**（推薦）：
```bash
chainlit deploy
```

2. **Docker**：
```dockerfile
FROM python:3.10
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["chainlit", "run", "app.py", "-h", "0.0.0.0"]
```

3. **傳統服務器**：
```bash
chainlit run app.py -h 0.0.0.0 -p 8000
```

### Q: 支持多語言嗎？

**A:** 支持，可在配置中設置：

```toml
[UI]
default_locale = "zh-TW"
```

## 進階主題

### 自定義主題

創建 `.chainlit/theme.py`：

```python
import chainlit as cl

theme = {
    "primary_color": "#2196F3",
    "background_color": "#FFFFFF",
    "text_color": "#000000",
    "font_family": "Inter, sans-serif"
}

cl.config.ui.theme = theme
```

### WebSocket 事件

```python
@cl.on_connect
async def on_connect():
    print("客戶端連接")

@cl.on_disconnect
async def on_disconnect():
    print("客戶端斷開")
```

### 多模態支持

```python
# 音頻
audio = cl.Audio(path="audio.mp3", name="語音")
await cl.Message(elements=[audio]).send()

# 視頻
video = cl.Video(path="video.mp4", name="演示")
await cl.Message(elements=[video]).send()

# PDF
pdf = cl.Pdf(path="doc.pdf", name="文檔")
await cl.Message(elements=[pdf]).send()
```

### 與向量數據庫整合

```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

@cl.on_chat_start
async def start():
    # 初始化向量數據庫
    vectorstore = Chroma(
        embedding_function=OpenAIEmbeddings()
    )
    cl.user_session.set("vectorstore", vectorstore)

@cl.on_message
async def main(message: cl.Message):
    vectorstore = cl.user_session.get("vectorstore")
    docs = vectorstore.similarity_search(message.content)
    # 使用檢索的文檔
```

## 參考資源

### 官方文檔
- [Chainlit 官方文檔](https://docs.chainlit.io/)
- [API 參考](https://docs.chainlit.io/api-reference)
- [GitHub 倉庫](https://github.com/Chainlit/chainlit)

### 社區資源
- [Discord 社區](https://discord.gg/chainlit)
- [示例項目](https://github.com/Chainlit/chainlit/tree/main/examples)
- [視頻教程](https://www.youtube.com/c/chainlit)

### 相關工具
- [LangChain](https://python.langchain.com/) - LLM 框架
- [OpenAI](https://openai.com/) - LLM 提供商
- [FastAPI](https://fastapi.tiangolo.com/) - Web 框架

## 生態系統

### 插件和擴展
- chainlit-auth: 增強認證功能
- chainlit-analytics: 使用分析
- chainlit-themes: 主題市場

### 整合案例
- 客服機器人
- 知識庫問答
- 代碼助手
- 教育輔導
- 內容生成工具

## 貢獻指南

歡迎貢獻新的範例或改進現有代碼！

1. Fork 本倉庫
2. 創建功能分支
3. 編寫清晰的註釋
4. 測試代碼
5. 提交 Pull Request

## 授權

本範例集採用 MIT 授權，可自由使用和修改。

## 更新日誌

- **2024-12**: 創建初始範例集
- 包含 10 個完整範例
- 涵蓋所有核心功能
- 繁體中文註釋

---

**開始探索** → 從 `01_快速開始.py` 開始你的 Chainlit 之旅！
