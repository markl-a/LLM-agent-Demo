"""
Gradio API 端點示例

本示例展示：
1. API 端點使用
2. 程序化調用
3. cURL 示例
4. Python 客戶端

運行方式：
    python 07_API端點.py
"""

import gradio as gr
import requests
import json
from typing import Dict, Any


# ==================== API 處理函數 ====================

def text_processor(text: str) -> Dict[str, Any]:
    """
    文本處理器（用於 API 調用）

    Args:
        text: 輸入文本

    Returns:
        處理結果字典
    """
    result = {
        "input": text,
        "length": len(text),
        "word_count": len(text.split()),
        "uppercase": text.upper(),
        "lowercase": text.lower(),
        "reversed": text[::-1],
        "status": "success"
    }

    return result


def image_info(image) -> Dict[str, Any]:
    """
    圖像信息提取器

    Args:
        image: 輸入圖像

    Returns:
        圖像信息字典
    """
    if image is None:
        return {"error": "No image provided"}

    from PIL import Image
    if isinstance(image, str):
        img = Image.open(image)
    else:
        img = image

    return {
        "width": img.width,
        "height": img.height,
        "mode": img.mode,
        "format": img.format if hasattr(img, 'format') else "Unknown",
        "size_bytes": img.width * img.height * len(img.getbands()),
        "status": "success"
    }


def calculator_api(num1: float, num2: float, operation: str) -> Dict[str, Any]:
    """
    計算器 API

    Args:
        num1: 第一個數字
        num2: 第二個數字
        operation: 運算符

    Returns:
        計算結果
    """
    operations = {
        "add": num1 + num2,
        "subtract": num1 - num2,
        "multiply": num1 * num2,
        "divide": num1 / num2 if num2 != 0 else "Error: Division by zero"
    }

    result = operations.get(operation, "Invalid operation")

    return {
        "num1": num1,
        "num2": num2,
        "operation": operation,
        "result": result,
        "status": "success"
    }


def generate_api_examples(base_url: str) -> str:
    """
    生成 API 調用示例

    Args:
        base_url: 基礎 URL

    Returns:
        示例代碼
    """
    examples = f"""
# ==================== API 調用示例 ====================

## 1. cURL 示例

### 文本處理 API
```bash
curl -X POST {base_url}/api/predict \\
  -H "Content-Type: application/json" \\
  -d '{{"data": ["Hello Gradio API"]}}'
```

### 計算器 API
```bash
curl -X POST {base_url}/api/predict \\
  -H "Content-Type: application/json" \\
  -d '{{"data": [10, 5, "add"]}}'
```

## 2. Python requests 示例

```python
import requests
import json

# 設置 API 端點
api_url = "{base_url}/api/predict"

# 調用文本處理 API
response = requests.post(
    api_url,
    json={{"data": ["Hello Gradio API"]}}
)

result = response.json()
print(result)

# 調用計算器 API
response = requests.post(
    api_url,
    json={{"data": [10, 5, "add"]}}
)

result = response.json()
print(result)
```

## 3. JavaScript fetch 示例

```javascript
// 文本處理 API
fetch('{base_url}/api/predict', {{
    method: 'POST',
    headers: {{
        'Content-Type': 'application/json'
    }},
    body: JSON.stringify({{
        data: ['Hello Gradio API']
    }})
}})
.then(response => response.json())
.then(data => console.log(data));
```

## 4. Python gradio_client 示例

```python
from gradio_client import Client

# 連接到 Gradio 應用
client = Client("{base_url}")

# 調用 API
result = client.predict(
    "Hello Gradio API",
    api_name="/predict"
)

print(result)
```

## 5. 獲取 API 信息

```bash
# 獲取 API 端點列表
curl {base_url}/api/

# 獲取具體端點信息
curl {base_url}/api/predict/
```

## 6. 批量請求示例

```python
import requests
import concurrent.futures

def call_api(text):
    response = requests.post(
        "{base_url}/api/predict",
        json={{"data": [text]}}
    )
    return response.json()

# 批量處理
texts = ["Text 1", "Text 2", "Text 3"]

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(call_api, texts))

for result in results:
    print(result)
```
    """

    return examples


def test_api_call(api_url: str, input_data: str) -> str:
    """
    測試 API 調用

    Args:
        api_url: API URL
        input_data: 輸入數據

    Returns:
        調用結果
    """
    try:
        response = requests.post(
            api_url,
            json={"data": [input_data]},
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            return f"""
✅ **API 調用成功**

**響應狀態：** {response.status_code}

**響應數據：**
```json
{json.dumps(result, indent=2, ensure_ascii=False)}
```

**響應頭：**
{json.dumps(dict(response.headers), indent=2)}
            """
        else:
            return f"""
❌ **API 調用失敗**

**狀態碼：** {response.status_code}
**錯誤信息：** {response.text}
            """

    except Exception as e:
        return f"❌ **錯誤：** {str(e)}"


# ==================== Gradio 界面 ====================

def create_demo():
    """創建 Gradio 應用"""

    with gr.Blocks(theme=gr.themes.Soft(), title="🔌 Gradio API 端點") as demo:

        gr.Markdown("# 🔌 Gradio API 端點示例")
        gr.Markdown("展示如何使用 Gradio 的 API 功能")

        with gr.Tabs():

            # Tab 1: 文本處理 API
            with gr.TabItem("📝 文本處理 API"):
                gr.Markdown("### 文本處理端點")

                with gr.Row():
                    with gr.Column():
                        text_input = gr.Textbox(
                            label="輸入文本",
                            placeholder="輸入要處理的文本...",
                            value="Hello Gradio API"
                        )
                        text_btn = gr.Button("🚀 處理文本", variant="primary")

                    with gr.Column():
                        text_output = gr.JSON(label="API 響應")

                text_btn.click(
                    fn=text_processor,
                    inputs=text_input,
                    outputs=text_output,
                    api_name="text_process"  # 設置 API 端點名稱
                )

                gr.Markdown("""
**API 端點：** `/api/text_process`

**調用示例：**
```bash
curl -X POST http://localhost:7860/api/text_process \\
  -H "Content-Type: application/json" \\
  -d '{"data": ["Hello Gradio"]}'
```
                """)

            # Tab 2: 計算器 API
            with gr.TabItem("🔢 計算器 API"):
                gr.Markdown("### 計算器端點")

                with gr.Row():
                    with gr.Column():
                        calc_num1 = gr.Number(label="數字 1", value=10)
                        calc_num2 = gr.Number(label="數字 2", value=5)
                        calc_op = gr.Dropdown(
                            choices=["add", "subtract", "multiply", "divide"],
                            label="運算",
                            value="add"
                        )
                        calc_btn = gr.Button("🔢 計算", variant="primary")

                    with gr.Column():
                        calc_output = gr.JSON(label="API 響應")

                calc_btn.click(
                    fn=calculator_api,
                    inputs=[calc_num1, calc_num2, calc_op],
                    outputs=calc_output,
                    api_name="calculator"
                )

                gr.Markdown("""
**API 端點：** `/api/calculator`

**調用示例：**
```bash
curl -X POST http://localhost:7860/api/calculator \\
  -H "Content-Type: application/json" \\
  -d '{"data": [10, 5, "add"]}'
```
                """)

            # Tab 3: 圖像 API
            with gr.TabItem("🖼️ 圖像 API"):
                gr.Markdown("### 圖像信息提取端點")

                with gr.Row():
                    with gr.Column():
                        image_input = gr.Image(type="pil", label="上傳圖像")
                        image_btn = gr.Button("📊 獲取信息", variant="primary")

                    with gr.Column():
                        image_output = gr.JSON(label="圖像信息")

                image_btn.click(
                    fn=image_info,
                    inputs=image_input,
                    outputs=image_output,
                    api_name="image_info"
                )

                gr.Markdown("""
**API 端點：** `/api/image_info`

**注意：** 圖像需要以 base64 編碼傳輸
                """)

            # Tab 4: API 文檔
            with gr.TabItem("📚 API 文檔"):
                gr.Markdown("### 自動生成的 API 調用示例")

                api_examples = gr.Textbox(
                    label="API 調用示例",
                    value=generate_api_examples("http://localhost:7860"),
                    lines=30
                )

                gr.Button("🔄 刷新示例").click(
                    fn=lambda: generate_api_examples("http://localhost:7860"),
                    outputs=api_examples
                )

            # Tab 5: API 測試
            with gr.TabItem("🧪 API 測試"):
                gr.Markdown("### 測試 API 端點")

                with gr.Row():
                    with gr.Column():
                        test_url = gr.Textbox(
                            label="API URL",
                            value="http://localhost:7860/api/text_process",
                            placeholder="輸入 API 端點 URL..."
                        )
                        test_data = gr.Textbox(
                            label="測試數據",
                            value="Test API Call",
                            placeholder="輸入測試數據..."
                        )
                        test_btn = gr.Button("🧪 測試 API", variant="primary")

                    with gr.Column():
                        test_output = gr.Textbox(
                            label="測試結果",
                            lines=20
                        )

                test_btn.click(
                    fn=test_api_call,
                    inputs=[test_url, test_data],
                    outputs=test_output
                )

            # Tab 6: Python 客戶端
            with gr.TabItem("🐍 Python 客戶端"):
                gr.Markdown("### 使用 gradio_client")

                gr.Markdown("""
## 安裝客戶端

```bash
pip install gradio_client
```

## 基礎用法

```python
from gradio_client import Client

# 連接到 Gradio 應用
client = Client("http://localhost:7860")

# 方式 1: 使用 predict
result = client.predict(
    "Hello Gradio",
    api_name="/text_process"
)
print(result)

# 方式 2: 直接調用
result = client.text_process("Hello Gradio")
print(result)
```

## 查看可用 API

```python
# 查看所有 API 端點
print(client.view_api())

# 查看具體端點信息
print(client.view_api(api_name="/text_process"))
```

## 異步調用

```python
import asyncio
from gradio_client import Client

async def async_call():
    client = Client("http://localhost:7860")

    # 異步調用
    result = await client.predict(
        "Hello Async",
        api_name="/text_process"
    )
    print(result)

# 運行異步函數
asyncio.run(async_call())
```

## 批量處理

```python
from gradio_client import Client
import concurrent.futures

client = Client("http://localhost:7860")

def process_text(text):
    return client.predict(text, api_name="/text_process")

# 批量處理
texts = ["Text 1", "Text 2", "Text 3"]

with concurrent.futures.ThreadPoolExecutor() as executor:
    results = list(executor.map(process_text, texts))

for result in results:
    print(result)
```

## 處理文件

```python
# 上傳圖像
result = client.predict(
    "path/to/image.jpg",
    api_name="/image_info"
)
```
                """)

        gr.Markdown("""
---
### 💡 API 使用指南

**特點：**
- 自動生成 RESTful API
- 支持 JSON 格式交互
- 可通過任何 HTTP 客戶端調用
- 提供 Python 客戶端庫

**API 端點格式：**
- 基礎 URL：`http://localhost:7860`
- API 端點：`/api/{api_name}`
- 查看所有端點：`/api/`

**請求格式：**
```json
{
  "data": [參數1, 參數2, ...]
}
```

**響應格式：**
```json
{
  "data": [結果],
  "duration": 處理時間,
  "average_duration": 平均時間
}
```

**相關資源：**
- [Gradio API 文檔](https://gradio.app/docs/#api)
- [gradio_client 文檔](https://gradio.app/docs/#python-client)
        """)

    return demo


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║      Gradio API 端點示例                 ║
╚══════════════════════════════════════════╝

功能特點：
✅ 自動生成 RESTful API
✅ 文本處理 API
✅ 計算器 API
✅ 圖像處理 API
✅ API 調用示例
✅ Python 客戶端使用

API 端點：
• /api/text_process - 文本處理
• /api/calculator - 計算器
• /api/image_info - 圖像信息

啟動應用...
    """)

    demo = create_demo()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_api=True  # 顯示 API 文檔
    )

    print("""
✅ 應用已啟動！

📱 界面地址：http://localhost:7860
📚 API 文檔：http://localhost:7860/docs
🔌 查看端點：http://localhost:7860/api/
    """)


if __name__ == "__main__":
    main()
