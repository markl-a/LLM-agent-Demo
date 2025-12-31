"""
Modal Web 端點示例

本示例展示：
1. 創建 HTTP API 端點
2. 處理不同的 HTTP 方法
3. 請求和響應處理
4. CORS 配置
"""

import modal
from rich.console import Console
from rich.panel import Panel

console = Console()

# 創建應用
app = modal.App("web-endpoints")

# 定義鏡像
web_image = modal.Image.debian_slim().pip_install(
    "fastapi",
    "pydantic"
)


# 示例 1: 簡單的 GET 端點
@app.function(image=web_image)
@modal.web_endpoint(method="GET")
def hello_world():
    """最簡單的 GET 端點"""
    return {"message": "Hello from Modal!", "status": "success"}


# 示例 2: POST 端點接收 JSON
@app.function(image=web_image)
@modal.web_endpoint(method="POST")
def process_data(data: dict):
    """
    處理 POST 請求的 JSON 數據

    curl -X POST https://your-url/process_data \\
      -H "Content-Type: application/json" \\
      -d '{"text": "hello", "count": 5}'
    """
    print(f"收到數據: {data}")

    text = data.get("text", "")
    count = data.get("count", 1)

    # 處理數據
    result = {
        "original": text,
        "uppercase": text.upper(),
        "repeated": text * count,
        "length": len(text)
    }

    return result


# 示例 3: 使用 FastAPI 的完整端點
@app.function(image=web_image)
@modal.web_endpoint(method="POST")
def analyze_text(request: dict):
    """
    文本分析 API

    Body:
    {
        "text": "要分析的文本",
        "analysis_type": "basic|detailed"
    }
    """
    text = request.get("text", "")
    analysis_type = request.get("analysis_type", "basic")

    if not text:
        return {"error": "text is required"}, 400

    # 基本分析
    analysis = {
        "char_count": len(text),
        "word_count": len(text.split()),
        "line_count": len(text.splitlines())
    }

    # 詳細分析
    if analysis_type == "detailed":
        analysis.update({
            "unique_words": len(set(text.lower().split())),
            "avg_word_length": sum(len(word) for word in text.split()) / len(text.split()) if text.split() else 0,
            "has_digits": any(c.isdigit() for c in text),
            "has_uppercase": any(c.isupper() for c in text)
        })

    return {
        "text": text[:100] + "..." if len(text) > 100 else text,
        "analysis": analysis
    }


# 示例 4: 返回不同狀態碼
@app.function(image=web_image)
@modal.web_endpoint(method="GET")
def status_code_demo(code: int = 200):
    """
    演示返回不同的 HTTP 狀態碼

    ?code=200  - 成功
    ?code=400  - 客戶端錯誤
    ?code=500  - 服務器錯誤
    """
    messages = {
        200: "Success",
        400: "Bad Request",
        404: "Not Found",
        500: "Internal Server Error"
    }

    message = messages.get(code, "Unknown Status")

    # 返回元組: (response_body, status_code)
    return {"message": message, "code": code}, code


# 示例 5: 文件上傳處理
@app.function(image=web_image)
@modal.web_endpoint(method="POST")
def upload_file(request: dict):
    """
    處理文件上傳

    curl -X POST https://your-url/upload_file \\
      -F "file=@image.jpg" \\
      -F "description=my image"
    """
    # 在實際應用中，這裡會處理文件數據
    file_info = {
        "status": "received",
        "message": "File upload endpoint (實際文件處理需要額外配置)"
    }

    return file_info


# 示例 6: 使用查詢參數
@app.function(image=web_image)
@modal.web_endpoint(method="GET")
def search(query: str = "", limit: int = 10, offset: int = 0):
    """
    搜索 API（使用查詢參數）

    ?query=python&limit=20&offset=0
    """
    print(f"搜索: query={query}, limit={limit}, offset={offset}")

    # 模擬搜索結果
    results = [
        {"id": i + offset, "title": f"Result {i + offset}", "score": 100 - i}
        for i in range(limit)
    ]

    return {
        "query": query,
        "total": 1000,  # 模擬總數
        "limit": limit,
        "offset": offset,
        "results": results
    }


# 示例 7: 完整的 CRUD API
@app.function(image=web_image)
@modal.web_endpoint(method="POST")
def create_item(item: dict):
    """創建項目（CREATE）"""
    return {"id": "123", "item": item, "status": "created"}


@app.function(image=web_image)
@modal.web_endpoint(method="GET")
def get_item(id: str):
    """獲取項目（READ）"""
    return {"id": id, "name": f"Item {id}", "status": "active"}


@app.function(image=web_image)
@modal.web_endpoint(method="PUT")
def update_item(id: str, item: dict):
    """更新項目（UPDATE）"""
    return {"id": id, "item": item, "status": "updated"}


@app.function(image=web_image)
@modal.web_endpoint(method="DELETE")
def delete_item(id: str):
    """刪除項目（DELETE）"""
    return {"id": id, "status": "deleted"}


# 示例 8: 健康檢查端點
@app.function(image=web_image)
@modal.web_endpoint(method="GET")
def health():
    """健康檢查端點"""
    import time

    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "modal-web-api"
    }


@app.local_entrypoint()
def main():
    """本地入口（用於測試）"""
    console.print(Panel.fit(
        "[bold cyan]Modal Web 端點示例[/bold cyan]\n"
        "[dim]創建 HTTP API 服務[/dim]",
        border_style="cyan"
    ))

    console.print("\n[green]Web 端點已配置完成！[/green]")
    console.print("\n[yellow]部署步驟:[/yellow]")
    console.print("  1. modal deploy 05_Web端點.py")
    console.print("  2. 查看生成的 URL")
    console.print("  3. 使用 curl 或瀏覽器測試")


def print_endpoint_guide():
    """打印端點使用指南"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]Web 端點配置指南:[/bold cyan]")
    console.print("""
[green]1. 基本配置:[/green]

@app.function(image=web_image)
@modal.web_endpoint(method="GET")  # GET, POST, PUT, DELETE
def my_endpoint():
    return {"message": "Hello"}

[green]2. 接收參數:[/green]

# 查詢參數（GET）
@modal.web_endpoint(method="GET")
def search(query: str, limit: int = 10):
    return {...}
# 調用: ?query=test&limit=20

# JSON Body（POST）
@modal.web_endpoint(method="POST")
def create(data: dict):
    return {...}
# 調用: -d '{"key": "value"}'

[green]3. 返回值:[/green]

# 返回 JSON
return {"data": "value"}

# 返回 JSON + 狀態碼
return {"error": "..."}, 400

# 返回 JSON + 狀態碼 + Headers
return {"data": "..."}, 200, {"X-Custom": "header"}

[green]4. 測試示例:[/green]

# GET 請求
curl https://your-app--hello-world.modal.run

# POST 請求
curl -X POST https://your-app--process-data.modal.run \\
  -H "Content-Type: application/json" \\
  -d '{"text": "hello"}'

# 帶參數的 GET
curl "https://your-app--search.modal.run?query=test&limit=5"

[yellow]部署和訪問:[/yellow]

# 部署
modal deploy script.py

# 生成的 URL 格式:
https://{username}--{app-name}-{function-name}.modal.run

[yellow]最佳實踐:[/yellow]

✓ 使用合適的 HTTP 方法（GET/POST/PUT/DELETE）
✓ 驗證輸入數據
✓ 返回有意義的錯誤消息
✓ 設置合理的超時
✓ 實施速率限制
✓ 添加監控和日誌
✓ 使用 HTTPS（Modal 自動提供）
    """)
    console.print("="*60 + "\n")


if __name__ == "__main__":
    print_endpoint_guide()
    console.print("[yellow]部署 Web API:[/yellow]")
    console.print("  modal deploy 05_Web端點.py\n")
