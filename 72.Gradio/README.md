# Gradio 框架完整範例

## 框架簡介

Gradio 是一個快速構建機器學習和 AI 模型演示界面的 Python 框架，讓開發者能夠在幾分鐘內將 ML 模型轉換為美觀、互動的 Web 應用。Gradio 專注於簡單性和快速原型開發，是展示 AI 能力的理想選擇。

### 核心特點

#### 1. 極速上手 🚀
- 3 行代碼即可創建界面
- 無需 HTML/CSS/JavaScript 知識
- 自動生成美觀的 UI
- 快速迭代和測試

```python
import gradio as gr

def greet(name):
    return f"你好，{name}！"

gr.Interface(fn=greet, inputs="text", outputs="text").launch()
```

#### 2. 豐富的組件庫 🎨
- **輸入組件**：文本框、圖片、音頻、視頻、文件上傳
- **輸出組件**：文本、圖片、圖表、JSON、HTML
- **互動組件**：滑塊、下拉選單、多選框、按鈕
- **數據組件**：DataFrame、Gallery、JSON

```python
# 多輸入輸出示例
gr.Interface(
    fn=analyze_image,
    inputs=[
        gr.Image(type="pil"),
        gr.Slider(0, 100, value=50)
    ],
    outputs=[
        gr.Label(),
        gr.Image()
    ]
).launch()
```

#### 3. 多模態支持 📸
- 圖片處理（PIL、NumPy、文件路徑）
- 音頻處理（WAV、MP3）
- 視頻處理
- 文本分析
- 文件上傳與處理

```python
# 圖片到圖片的轉換
def process_image(img):
    return transform(img)

gr.Interface(
    fn=process_image,
    inputs=gr.Image(type="pil"),
    outputs=gr.Image()
).launch()
```

#### 4. 實時預覽 ⚡
- 自動刷新功能
- 即時參數調整
- 實時結果展示
- 流式輸出支持

```python
# 實時更新
gr.Interface(
    fn=predict,
    inputs="text",
    outputs="text",
    live=True  # 實時更新
).launch()
```

#### 5. HuggingFace 整合 🤗
- 一鍵部署到 Spaces
- 無縫整合 Transformers
- 共享公開連結
- 免費託管

```python
from transformers import pipeline

# 載入預訓練模型
classifier = pipeline("sentiment-analysis")

gr.Interface.from_pipeline(classifier).launch()
```

#### 6. 分享功能 🌐
- 生成公開分享連結
- 無需部署服務器
- 72 小時有效期
- 支持密碼保護

```python
# 生成分享連結
interface.launch(share=True)
# 輸出：Running on public URL: https://xxxxx.gradio.app
```

#### 7. 自定義布局 📐
- Blocks API 靈活布局
- 行列組織
- 標籤頁
- 手風琴折疊
- 自定義 CSS

```python
with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            input_text = gr.Textbox(label="輸入")
        with gr.Column():
            output_text = gr.Textbox(label="輸出")

    btn = gr.Button("提交")
    btn.click(fn=process, inputs=input_text, outputs=output_text)

demo.launch()
```

#### 8. API 端點 🔌
- 自動生成 REST API
- 支持程序化調用
- JSON 格式交互
- 易於整合

```python
# API 端點自動可用
# POST http://localhost:7860/api/predict
```

## 安裝指南

### 基礎安裝
```bash
pip install gradio
```

### 完整安裝（包含 AI 工具）
```bash
pip install gradio openai transformers torch
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

### 第一個 Gradio 應用

創建 `app.py`：

```python
import gradio as gr

def greet(name):
    return f"你好，{name}！"

demo = gr.Interface(
    fn=greet,
    inputs=gr.Textbox(label="你的名字"),
    outputs=gr.Textbox(label="問候")
)

demo.launch()
```

運行應用：
```bash
python app.py
```

訪問 http://localhost:7860 查看應用。

### 圖片處理應用

```python
import gradio as gr
from PIL import Image, ImageFilter

def blur_image(img, blur_amount):
    return img.filter(ImageFilter.GaussianBlur(blur_amount))

gr.Interface(
    fn=blur_image,
    inputs=[
        gr.Image(type="pil", label="上傳圖片"),
        gr.Slider(0, 20, value=5, label="模糊程度")
    ],
    outputs=gr.Image(label="處理結果")
).launch()
```

### 與 OpenAI 整合

```python
import gradio as gr
from openai import OpenAI

client = OpenAI()

def chat(message, history):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": message}]
    )
    return response.choices[0].message.content

gr.ChatInterface(fn=chat).launch()
```

## 與其他框架對比

### Gradio vs Streamlit

| 特性 | Gradio | Streamlit |
|------|--------|-----------|
| **主要用途** | ML 模型演示 | 數據應用 |
| **學習曲線** | 非常低 | 低 |
| **代碼量** | 極少 | 少 |
| **布局靈活性** | 中等 | 高 |
| **HuggingFace 整合** | 深度整合 | 基礎支持 |
| **分享功能** | 內建 | 需第三方 |
| **適用場景** | AI Demo | 數據儀表板 |

**Streamlit 優勢：**
- 更靈活的布局控制
- 更豐富的數據可視化
- 更適合複雜應用
- 更大的社區

**Gradio 優勢：**
- 更快的原型開發
- 更簡單的 API
- HuggingFace 原生支持
- 內建分享功能

### Gradio vs Chainlit

| 特性 | Gradio | Chainlit |
|------|--------|----------|
| **應用類型** | 通用 ML Demo | 對話式 AI |
| **界面風格** | 表單式 | 聊天式 |
| **開發速度** | 極快 | 快 |
| **聊天界面** | ChatInterface 組件 | 原生支持 |
| **流式響應** | 支持 | 原生優化 |
| **適用場景** | 各類 ML 模型 | ChatGPT 類應用 |

**Chainlit 優勢：**
- 專業的聊天體驗
- 更好的對話管理
- LangChain 深度整合
- Agent 可視化

**Gradio 優勢：**
- 更通用的組件
- 更快的開發速度
- 更簡單的 API
- 更廣泛的應用場景

### 選擇建議

**選擇 Gradio：**
- 快速展示 ML 模型
- 需要各種輸入/輸出類型
- HuggingFace 模型部署
- 簡單的 AI 應用原型
- 教學和演示
- 內部工具快速開發

**選擇 Streamlit：**
- 複雜的數據應用
- 需要豐富的可視化
- 多頁面應用
- 數據分析工具

**選擇 Chainlit：**
- 專業的聊天機器人
- Agent 系統界面
- 對話式 AI 應用
- 需要 LangChain 整合

## 範例文件導覽

### 基礎篇

#### 01_快速開始.py
- Gradio 基本結構
- Interface API 使用
- 簡單的輸入輸出
- Hello World 示例

#### 02_文本界面.py
- 文本處理應用
- Textbox 組件
- 多輸入輸出
- 文本分析示例

#### 03_圖像處理.py
- 圖片上傳和處理
- Image 組件
- PIL 圖像操作
- 圖像濾鏡應用

#### 04_聊天界面.py
- ChatInterface 組件
- 對話歷史管理
- 流式響應
- LLM 整合

### 進階篇

#### 05_多模態.py
- 多種輸入類型組合
- 圖片、音頻、視頻處理
- 文件上傳
- 複雜輸出展示

#### 06_自定義組件.py
- Blocks API 使用
- 自定義布局
- 事件處理
- 狀態管理

#### 07_API端點.py
- API 端點使用
- 程序化調用
- cURL 示例
- Python 客戶端

#### 08_認證系統.py
- 用戶認證
- 密碼保護
- 多用戶管理
- 權限控制

### 高級篇

#### 09_LLM整合.py
- OpenAI 整合
- HuggingFace 模型
- 流式生成
- 提示工程

#### 10_部署分享.py
- HuggingFace Spaces 部署
- Docker 容器化
- 公開分享
- 生產環境配置

## 核心概念

### Interface API

最簡單的 Gradio 應用方式：

```python
gr.Interface(
    fn=function,           # 處理函數
    inputs=input_type,     # 輸入組件
    outputs=output_type,   # 輸出組件
    title="標題",
    description="描述",
    examples=[...]         # 示例輸入
).launch()
```

### Blocks API

更靈活的布局控制：

```python
with gr.Blocks() as demo:
    # 使用行列組織組件
    with gr.Row():
        input1 = gr.Textbox(label="輸入1")
        input2 = gr.Textbox(label="輸入2")

    output = gr.Textbox(label="輸出")
    btn = gr.Button("處理")

    # 綁定事件
    btn.click(fn=process, inputs=[input1, input2], outputs=output)

demo.launch()
```

### 常用組件

**輸入組件：**
- `gr.Textbox()` - 文本輸入
- `gr.Image()` - 圖片上傳
- `gr.Audio()` - 音頻輸入
- `gr.Video()` - 視頻上傳
- `gr.File()` - 文件上傳
- `gr.Slider()` - 滑塊
- `gr.Dropdown()` - 下拉選單
- `gr.Radio()` - 單選按鈕
- `gr.Checkbox()` - 多選框

**輸出組件：**
- `gr.Textbox()` - 文本輸出
- `gr.Image()` - 圖片展示
- `gr.Label()` - 分類標籤
- `gr.JSON()` - JSON 數據
- `gr.HTML()` - HTML 內容
- `gr.DataFrame()` - 表格數據
- `gr.Gallery()` - 圖片畫廊
- `gr.Plot()` - 圖表

### 事件處理

```python
# 按鈕點擊事件
button.click(fn=function, inputs=input_comp, outputs=output_comp)

# 輸入改變事件
textbox.change(fn=function, inputs=textbox, outputs=output)

# 提交事件
textbox.submit(fn=function, inputs=textbox, outputs=output)

# 實時更新
textbox.change(fn=function, inputs=textbox, outputs=output,
               every=1)  # 每秒更新
```

### 狀態管理

```python
with gr.Blocks() as demo:
    # 創建狀態變量
    state = gr.State(value=0)

    def increment(count):
        return count + 1

    btn = gr.Button("增加")
    output = gr.Number(label="計數")

    btn.click(increment, inputs=state, outputs=[state, output])
```

## 最佳實踐

### 1. 錯誤處理

```python
def safe_process(input_text):
    try:
        result = process(input_text)
        return result
    except Exception as e:
        return f"錯誤：{str(e)}"

gr.Interface(fn=safe_process, ...).launch()
```

### 2. 進度追蹤

```python
def long_task(input_data, progress=gr.Progress()):
    progress(0, desc="開始處理...")
    for i in range(100):
        time.sleep(0.1)
        progress((i+1)/100, desc=f"處理中... {i+1}%")
    return "完成！"

gr.Interface(fn=long_task, ...).launch()
```

### 3. 緩存優化

```python
@gr.cache  # 緩存結果
def expensive_computation(input_value):
    # 耗時操作
    return result

gr.Interface(fn=expensive_computation, ...).launch()
```

### 4. 示例數據

```python
gr.Interface(
    fn=process,
    inputs="text",
    outputs="text",
    examples=[
        ["示例輸入 1"],
        ["示例輸入 2"],
        ["示例輸入 3"]
    ]
).launch()
```

### 5. 性能優化

- 使用 `queue()` 處理高並發
- 啟用緩存減少重複計算
- 優化模型加載時間
- 使用異步處理長任務

```python
# 啟用隊列處理
demo.queue(max_size=20)
demo.launch()
```

## 常見問題

### Q: Gradio 應用如何部署到生產環境？

**A:** 有多種部署方式：

1. **HuggingFace Spaces**（推薦新手）：
```bash
# 在 HuggingFace 創建 Space
# 上傳代碼和 requirements.txt
# 自動部署
```

2. **Docker**：
```dockerfile
FROM python:3.10
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

3. **雲服務器**：
```bash
# 使用 systemd 或 supervisor 管理進程
python app.py --server-name 0.0.0.0 --server-port 7860
```

### Q: 如何處理大文件上傳？

**A:** 配置文件大小限制和處理策略：

```python
gr.Interface(
    fn=process_file,
    inputs=gr.File(file_count="multiple", file_types=[".pdf", ".txt"]),
    outputs="text"
).launch(max_file_size="100mb")
```

### Q: Gradio 支持實時流式輸出嗎？

**A:** 支持，使用生成器函數：

```python
def streaming_response(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.1)

gr.Interface(fn=streaming_response, inputs="text", outputs="text").launch()
```

### Q: 如何自定義 CSS 樣式？

**A:** 使用 Blocks 的 CSS 參數：

```python
css = """
.gradio-container {
    font-family: 'Arial', sans-serif;
}
.my-button {
    background-color: #4CAF50 !important;
}
"""

with gr.Blocks(css=css) as demo:
    # 組件定義
    pass
```

### Q: Gradio 和 FastAPI 可以一起使用嗎？

**A:** 可以，將 Gradio 掛載到 FastAPI：

```python
from fastapi import FastAPI
import gradio as gr

app = FastAPI()

@app.get("/api/health")
def health():
    return {"status": "ok"}

# 掛載 Gradio
io = gr.Interface(lambda x: x, "textbox", "textbox")
app = gr.mount_gradio_app(app, io, path="/gradio")
```

## 進階主題

### 自定義主題

```python
theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="gray",
    neutral_hue="slate",
)

with gr.Blocks(theme=theme) as demo:
    # 組件定義
    pass
```

### 多頁面應用

```python
with gr.Blocks() as demo:
    with gr.Tabs():
        with gr.TabItem("頁面 1"):
            # 第一個頁面的組件
            pass

        with gr.TabItem("頁面 2"):
            # 第二個頁面的組件
            pass
```

### 數據持久化

```python
import json

def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f)
    return "已保存"

def load_data():
    with open("data.json", "r") as f:
        return json.load(f)

# 在界面中使用
```

### WebSocket 支持

```python
# Gradio 自動處理 WebSocket 連接
# 用於實時更新和雙向通信
demo.launch(show_api=False)
```

## 參考資源

### 官方文檔
- [Gradio 官方文檔](https://gradio.app/docs/)
- [Gradio Guides](https://gradio.app/guides/)
- [GitHub 倉庫](https://github.com/gradio-app/gradio)

### 社區資源
- [HuggingFace Spaces](https://huggingface.co/spaces)
- [Gradio Discord](https://discord.gg/gradio)
- [示例畫廊](https://gradio.app/demos/)

### 相關工具
- [HuggingFace Transformers](https://huggingface.co/transformers/)
- [OpenAI API](https://openai.com/api/)
- [Stable Diffusion](https://stability.ai/)

## 生態系統

### 熱門應用案例
- 圖像生成（Stable Diffusion WebUI）
- 文本生成（ChatGPT 界面）
- 圖像分類（ResNet、ViT）
- 語音識別（Whisper）
- 翻譯工具
- 代碼生成

### HuggingFace 整合

```python
# 直接從 HuggingFace 載入模型
from transformers import pipeline

pipe = pipeline("text-generation", model="gpt2")
gr.Interface.from_pipeline(pipe).launch()
```

### 插件和擴展
- gradio-client: Python/JavaScript 客戶端
- gradio-tools: LangChain 工具整合
- gr-themes: 主題市場

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

**開始探索** → 從 `01_快速開始.py` 開始你的 Gradio 之旅！
