"""
Gradio 部署和分享示例

本示例展示：
1. HuggingFace Spaces 部署
2. Docker 容器化
3. 公開分享
4. 生產環境配置

運行方式：
    python 10_部署分享.py
"""

import gradio as gr
import os


# ==================== 示例應用 ====================

def demo_function(text: str, number: float, choice: str) -> str:
    """
    演示函數

    Args:
        text: 文本輸入
        number: 數字輸入
        choice: 選擇輸入

    Returns:
        處理結果
    """
    result = f"""
📊 **處理結果**

• 文本：{text}
• 數字：{number}
• 選擇：{choice}

✅ 處理完成！

這個應用已準備好部署！
    """

    return result


# ==================== Gradio 界面 ====================

def create_demo():
    """創建 Gradio 應用"""

    with gr.Blocks(
        theme=gr.themes.Soft(),
        title="🚀 Gradio 部署示例",
        analytics_enabled=False  # 生產環境可啟用
    ) as demo:

        gr.Markdown("# 🚀 Gradio 部署和分享指南")

        with gr.Tabs():

            # Tab 1: 示例應用
            with gr.TabItem("📱 示例應用"):
                gr.Markdown("### 準備部署的應用")

                with gr.Row():
                    with gr.Column():
                        text_input = gr.Textbox(
                            label="文本輸入",
                            placeholder="輸入一些文字..."
                        )
                        number_input = gr.Slider(
                            minimum=0,
                            maximum=100,
                            value=50,
                            label="數字輸入"
                        )
                        choice_input = gr.Radio(
                            choices=["選項 A", "選項 B", "選項 C"],
                            label="選擇",
                            value="選項 A"
                        )
                        submit_btn = gr.Button("🚀 提交", variant="primary")

                    with gr.Column():
                        output = gr.Textbox(
                            label="輸出",
                            lines=10
                        )

                submit_btn.click(
                    fn=demo_function,
                    inputs=[text_input, number_input, choice_input],
                    outputs=output
                )

            # Tab 2: 本地分享
            with gr.TabItem("🌐 本地分享"):
                gr.Markdown("""
### 使用 share 參數創建公開連結

#### 快速分享

```python
import gradio as gr

demo = gr.Interface(...)
demo.launch(share=True)  # 創建公開連結
```

運行後會生成一個公開 URL：
```
Running on public URL: https://xxxxx.gradio.live
```

#### 特點

✅ **優點：**
- 無需部署即可分享
- 72 小時有效期
- 免費使用
- 適合快速演示

❌ **限制：**
- 臨時連結（72小時）
- 性能限制
- 不適合生產環境
- 需要本地服務器運行

#### 使用場景

- 快速演示原型
- 臨時分享給團隊
- 測試和反饋收集
- 教學演示

#### 注意事項

⚠️ **安全提示：**
- 不要分享敏感數據
- 可以添加密碼保護
- 注意 API 密鑰安全

```python
# 添加密碼保護
demo.launch(
    share=True,
    auth=("username", "password")
)
```
                """)

            # Tab 3: HuggingFace Spaces
            with gr.TabItem("🤗 HuggingFace Spaces"):
                gr.Markdown("""
### 部署到 HuggingFace Spaces

#### 步驟 1: 創建 Space

1. 訪問 [huggingface.co/spaces](https://huggingface.co/spaces)
2. 點擊「Create new Space」
3. 選擇 Gradio SDK
4. 設置 Space 名稱和可見性

#### 步驟 2: 準備文件

創建以下文件結構：
```
my-gradio-app/
├── app.py              # 主應用文件
├── requirements.txt    # Python 依賴
└── README.md          # 說明文檔
```

**app.py 示例：**
```python
import gradio as gr

def greet(name):
    return f"Hello {name}!"

demo = gr.Interface(
    fn=greet,
    inputs="text",
    outputs="text"
)

if __name__ == "__main__":
    demo.launch()
```

**requirements.txt：**
```
gradio>=4.0.0
openai>=1.0.0
pillow>=10.0.0
```

#### 步驟 3: 上傳代碼

**方式 1: Web 界面**
- 直接在 Space 頁面上傳文件

**方式 2: Git**
```bash
# 克隆 Space 倉庫
git clone https://huggingface.co/spaces/username/space-name
cd space-name

# 添加文件
git add .
git commit -m "Initial commit"
git push
```

#### 步驟 4: 配置 Secrets

如果需要 API 密鑰：
1. 進入 Space 設置
2. 添加 Secret
3. 名稱：`OPENAI_API_KEY`
4. 值：你的 API 密鑰

在代碼中使用：
```python
import os
api_key = os.environ.get("OPENAI_API_KEY")
```

#### 高級配置

**README.md 配置：**
```yaml
---
title: My Gradio App
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
---

# My Gradio Application

Description of your app...
```

**自定義硬件：**
- 免費版：CPU 基礎
- 升級版：GPU、更多內存

#### 特點

✅ **優點：**
- 完全託管
- 免費使用（CPU）
- 自動 HTTPS
- 版本控制
- 社區展示

❌ **限制：**
- 免費版性能限制
- 冷啟動時間
- 存儲空間限制

#### 示例 Spaces

- [Stable Diffusion](https://huggingface.co/spaces/stabilityai/stable-diffusion)
- [ChatGPT Clone](https://huggingface.co/spaces/yuntian-deng/ChatGPT)
                """)

            # Tab 4: Docker 部署
            with gr.TabItem("🐳 Docker 部署"):
                gr.Markdown("""
### 使用 Docker 容器化部署

#### Dockerfile

```dockerfile
FROM python:3.10-slim

# 設置工作目錄
WORKDIR /app

# 複製依賴文件
COPY requirements.txt .

# 安裝依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用文件
COPY . .

# 暴露端口
EXPOSE 7860

# 設置環境變量
ENV GRADIO_SERVER_NAME="0.0.0.0"
ENV GRADIO_SERVER_PORT="7860"

# 運行應用
CMD ["python", "app.py"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  gradio-app:
    build: .
    ports:
      - "7860:7860"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

#### 構建和運行

```bash
# 構建鏡像
docker build -t my-gradio-app .

# 運行容器
docker run -p 7860:7860 \
  -e OPENAI_API_KEY=your-key \
  my-gradio-app

# 或使用 docker-compose
docker-compose up -d
```

#### 推送到 Docker Hub

```bash
# 標記鏡像
docker tag my-gradio-app username/my-gradio-app:latest

# 推送
docker push username/my-gradio-app:latest

# 在其他機器上運行
docker pull username/my-gradio-app:latest
docker run -p 7860:7860 username/my-gradio-app:latest
```

#### 多階段構建優化

```dockerfile
# 構建階段
FROM python:3.10-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 運行階段
FROM python:3.10-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH

EXPOSE 7860
CMD ["python", "app.py"]
```
                """)

            # Tab 5: 雲平台部署
            with gr.TabItem("☁️ 雲平台部署"):
                gr.Markdown("""
### 部署到主流雲平台

#### 1. Railway

```bash
# 安裝 Railway CLI
npm install -g @railway/cli

# 登錄
railway login

# 初始化項目
railway init

# 部署
railway up
```

**配置文件（railway.json）：**
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python app.py",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

#### 2. Render

1. 連接 GitHub 倉庫
2. 選擇 Web Service
3. 設置構建命令：`pip install -r requirements.txt`
4. 設置啟動命令：`python app.py`
5. 環境變量中添加 API 密鑰

#### 3. AWS (EC2)

```bash
# 連接到 EC2 實例
ssh -i key.pem ubuntu@ec2-instance

# 安裝 Docker
sudo apt update
sudo apt install docker.io -y

# 拉取並運行
docker pull username/my-gradio-app
docker run -d -p 80:7860 username/my-gradio-app
```

#### 4. Google Cloud Run

```bash
# 構建鏡像
gcloud builds submit --tag gcr.io/project-id/gradio-app

# 部署
gcloud run deploy gradio-app \
  --image gcr.io/project-id/gradio-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### 5. Azure App Service

```bash
# 使用 Azure CLI
az login
az webapp up \
  --name my-gradio-app \
  --runtime PYTHON:3.10
```

#### 成本對比

| 平台 | 免費額度 | 付費價格 |
|------|---------|---------|
| **HuggingFace** | CPU 免費 | $0.60/GPU 小時 |
| **Railway** | $5 免費額度 | $0.000231/GB秒 |
| **Render** | 750小時/月 | $7/月起 |
| **AWS** | 12個月免費 | 按需計費 |
| **GCP** | $300 免費額度 | 按需計費 |
                """)

            # Tab 6: 生產配置
            with gr.TabItem("⚙️ 生產配置"):
                gr.Markdown("""
### 生產環境最佳配置

#### 完整的啟動配置

```python
import gradio as gr

demo = gr.Interface(...)

if __name__ == "__main__":
    demo.launch(
        # 服務器配置
        server_name="0.0.0.0",  # 監聽所有接口
        server_port=7860,        # 端口
        share=False,             # 不創建公開連結

        # 安全配置
        auth=authenticate,       # 認證函數
        auth_message="請登錄",   # 認證提示

        # 性能配置
        max_threads=40,          # 最大線程數
        show_error=False,        # 隱藏詳細錯誤

        # 功能配置
        show_api=True,          # 顯示 API 文檔
        analytics_enabled=True,  # 啟用分析

        # SSL 配置（如果需要）
        ssl_keyfile="key.pem",
        ssl_certfile="cert.pem",
        ssl_verify=True,

        # 其他配置
        favicon_path="./favicon.ico",
        root_path="/app"  # 如果在子路徑下
    )
```

#### 環境變量管理

**.env 文件：**
```env
OPENAI_API_KEY=sk-...
GRADIO_SERVER_NAME=0.0.0.0
GRADIO_SERVER_PORT=7860
MAX_THREADS=40
```

**加載環境變量：**
```python
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
```

#### 日誌配置

```python
import logging

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gradio.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def my_function(input):
    logger.info(f"Processing: {input}")
    try:
        result = process(input)
        logger.info("Success")
        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
```

#### 性能監控

```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper

@monitor_performance
def expensive_function(input):
    # 處理邏輯
    return result
```

#### 錯誤處理

```python
def safe_function(input):
    try:
        result = process(input)
        return result
    except ValueError as e:
        return f"輸入錯誤：{e}"
    except Exception as e:
        # 記錄錯誤但不暴露細節
        logger.error(f"Error: {e}")
        return "處理失敗，請稍後重試"
```

#### 隊列配置

```python
# 啟用隊列處理並發請求
demo.queue(
    max_size=20,              # 最大隊列長度
    default_concurrency_limit=5  # 並發限制
)

demo.launch()
```

#### 緩存配置

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_function(input):
    # 耗時操作
    return expensive_computation(input)
```

#### Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### 健康檢查

```python
from fastapi import FastAPI
import gradio as gr

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# 掛載 Gradio
demo = gr.Interface(...)
app = gr.mount_gradio_app(app, demo, path="/")
```

#### 監控和告警

- 使用 Prometheus + Grafana
- 設置 Sentry 錯誤追蹤
- 配置 CloudWatch/Stackdriver
- 實施日誌聚合（ELK Stack）
                """)

        gr.Markdown("""
---
### 📋 部署檢查清單

部署前確認：

- [ ] 代碼已測試
- [ ] 依賴已鎖定（requirements.txt）
- [ ] 環境變量已配置
- [ ] 錯誤處理已實現
- [ ] 日誌記錄已配置
- [ ] 性能已優化
- [ ] 安全措施已實施
- [ ] 備份策略已制定
- [ ] 監控已設置
- [ ] 文檔已完善

### 🔗 有用資源

- [Gradio 部署文檔](https://gradio.app/guides/deploying-gradio-apps/)
- [HuggingFace Spaces 文檔](https://huggingface.co/docs/hub/spaces)
- [Docker 最佳實踐](https://docs.docker.com/develop/dev-best-practices/)
- [AWS 部署指南](https://aws.amazon.com/getting-started/)

祝部署順利！🚀
        """)

    return demo


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║      Gradio 部署和分享示例               ║
╚══════════════════════════════════════════╝

涵蓋內容：
✅ 本地分享（share=True）
✅ HuggingFace Spaces 部署
✅ Docker 容器化
✅ 雲平台部署（AWS, GCP, Azure 等）
✅ 生產環境配置
✅ 性能優化

啟動示例應用...
    """)

    demo = create_demo()

    # 開發模式
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # 設為 True 可創建公開連結
        show_api=True
    )

    # 生產模式示例（註釋掉）
    # demo.queue(max_size=20)
    # demo.launch(
    #     server_name="0.0.0.0",
    #     server_port=7860,
    #     share=False,
    #     auth=authenticate_function,
    #     max_threads=40,
    #     show_error=False
    # )


if __name__ == "__main__":
    main()
