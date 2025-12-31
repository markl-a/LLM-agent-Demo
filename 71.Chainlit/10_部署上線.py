"""
Chainlit 部署上線示例

本示例展示：
1. 生產環境配置
2. Docker 容器化
3. 環境變量管理
4. 性能優化
5. 部署最佳實踐

運行方式：
    chainlit run 10_部署上線.py -w

生產部署：
    見本文件中的說明和配置示例
"""

import chainlit as cl
import os
import sys
from datetime import datetime
from typing import Dict, Any


# ==================== 環境配置 ====================

def get_environment() -> str:
    """獲取當前環境"""
    return os.getenv("ENVIRONMENT", "development")


def is_production() -> bool:
    """檢查是否為生產環境"""
    return get_environment() == "production"


# ==================== 配置管理 ====================

class Config:
    """應用配置類"""

    def __init__(self):
        self.environment = get_environment()

        # 基礎配置
        self.app_name = os.getenv("APP_NAME", "Chainlit App")
        self.app_version = os.getenv("APP_VERSION", "1.0.0")

        # 服務器配置
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))

        # OpenAI 配置
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")

        # 數據庫配置（如果需要）
        self.database_url = os.getenv("DATABASE_URL", "")

        # 認證配置
        self.auth_enabled = os.getenv("AUTH_ENABLED", "false").lower() == "true"
        self.jwt_secret = os.getenv("JWT_SECRET", "your-secret-key")

        # 日誌配置
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

        # 性能配置
        self.max_concurrent_requests = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
        self.request_timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))

    def validate(self) -> bool:
        """驗證配置"""
        if is_production():
            if not self.openai_api_key:
                print("❌ 生產環境必須設置 OPENAI_API_KEY")
                return False

            if self.auth_enabled and self.jwt_secret == "your-secret-key":
                print("❌ 生產環境必須設置安全的 JWT_SECRET")
                return False

        return True

    def display(self):
        """顯示配置（不顯示敏感信息）"""
        print(f"""
╔══════════════════════════════════════════╗
║         應用配置                         ║
╚══════════════════════════════════════════╝

環境: {self.environment}
應用名稱: {self.app_name}
版本: {self.app_version}

服務器:
- Host: {self.host}
- Port: {self.port}

功能:
- OpenAI: {'✓' if self.openai_api_key else '✗'}
- 認證: {'啟用' if self.auth_enabled else '禁用'}
- 數據庫: {'已配置' if self.database_url else '未配置'}

性能:
- 最大並發: {self.max_concurrent_requests}
- 超時時間: {self.request_timeout}s
- 日誌級別: {self.log_level}
        """)


# 創建全局配置實例
config = Config()


# ==================== 健康檢查 ====================

@cl.on_chat_start
async def on_chat_start():
    """初始化聊天會話"""
    try:
        # 檢查配置
        if not config.validate():
            await cl.Message(
                content="⚠️ 配置驗證失敗，請檢查環境變量。"
            ).send()
            return

        # 歡迎消息
        welcome = f"""
# 🚀 {config.app_name}

版本：{config.app_version}
環境：{config.environment.upper()}

## 📚 部署指南

這個示例展示了如何將 Chainlit 應用部署到生產環境。

### 🎯 部署選項

1. **Chainlit Cloud** - 官方託管平台（推薦）
2. **Docker** - 容器化部署
3. **傳統服務器** - VPS/雲服務器
4. **無服務器** - AWS Lambda, Cloud Functions

### 💡 生產環境檢查清單

- {'✅' if config.openai_api_key else '❌'} OpenAI API Key
- {'✅' if config.auth_enabled else '⚠️'} 用戶認證
- {'✅' if config.database_url else '⚠️'} 數據持久化
- {'✅' if is_production() else '⚠️'} 環境設置

輸入命令查看更多信息：
- `docker` - Docker 部署指南
- `cloud` - 雲端部署指南
- `config` - 配置說明
- `security` - 安全建議
- `performance` - 性能優化
        """

        await cl.Message(content=welcome, author="系統").send()

    except Exception as e:
        await cl.Message(content=f"❌ 初始化失敗: {str(e)}").send()


# ==================== 消息處理 ====================

@cl.on_message
async def on_message(message: cl.Message):
    """處理用戶消息"""
    try:
        user_message = message.content.strip().lower()

        if "docker" in user_message:
            await show_docker_guide()
        elif "cloud" in user_message:
            await show_cloud_guide()
        elif "config" in user_message:
            await show_config_guide()
        elif "security" in user_message:
            await show_security_guide()
        elif "performance" in user_message:
            await show_performance_guide()
        else:
            await show_help()

    except Exception as e:
        await cl.Message(content=f"❌ 處理失敗: {str(e)}").send()


# ==================== 部署指南 ====================

async def show_docker_guide():
    """顯示 Docker 部署指南"""
    guide = """
## 🐳 Docker 部署指南

### 1. 創建 Dockerfile

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# 複製依賴文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY . .

# 暴露端口
EXPOSE 8000

# 運行命令
CMD ["chainlit", "run", "app.py", "-h", "0.0.0.0", "-p", "8000"]
```

### 2. 創建 docker-compose.yml

```yaml
version: '3.8'

services:
  chainlit-app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ENVIRONMENT=production
      - AUTH_ENABLED=true
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

### 3. 創建 .env 文件

```bash
OPENAI_API_KEY=your-key-here
JWT_SECRET=your-secret-key
DATABASE_URL=postgresql://user:pass@db:5432/dbname
```

### 4. 構建和運行

```bash
# 構建鏡像
docker build -t chainlit-app .

# 運行容器
docker run -p 8000:8000 --env-file .env chainlit-app

# 或使用 docker-compose
docker-compose up -d
```

### 5. 查看日誌

```bash
docker logs -f chainlit-app
```

### 📝 注意事項

- ⚠️ 不要將 .env 文件提交到 Git
- ✅ 使用 .dockerignore 排除不必要的文件
- ✅ 定期更新基礎鏡像
- ✅ 使用多階段構建優化鏡像大小
    """

    await cl.Message(content=guide, author="Docker 部署").send()


async def show_cloud_guide():
    """顯示雲端部署指南"""
    guide = """
## ☁️ 雲端部署指南

### 1. Chainlit Cloud（推薦）

```bash
# 安裝 CLI
pip install chainlit

# 登入
chainlit login

# 部署
chainlit deploy

# 查看部署
chainlit deployments
```

**優點：**
- ✅ 零配置部署
- ✅ 自動擴展
- ✅ 內建認證
- ✅ SSL 證書
- ✅ 全球 CDN

### 2. AWS (Elastic Beanstalk)

```bash
# 安裝 EB CLI
pip install awsebcli

# 初始化
eb init -p python-3.10 chainlit-app

# 創建環境
eb create chainlit-env

# 部署
eb deploy
```

**配置 .ebextensions/chainlit.config：**

```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: "/var/app/current:$PYTHONPATH"
  aws:elasticbeanstalk:container:python:
    WSGIPath: app:app
```

### 3. Google Cloud Platform (Cloud Run)

```bash
# 構建並推送鏡像
gcloud builds submit --tag gcr.io/PROJECT-ID/chainlit-app

# 部署
gcloud run deploy chainlit-app \\
  --image gcr.io/PROJECT-ID/chainlit-app \\
  --platform managed \\
  --region us-central1 \\
  --allow-unauthenticated
```

### 4. Azure (App Service)

```bash
# 創建資源組
az group create --name chainlit-rg --location eastus

# 創建 App Service 計劃
az appservice plan create \\
  --name chainlit-plan \\
  --resource-group chainlit-rg \\
  --sku B1 --is-linux

# 創建 Web App
az webapp create \\
  --resource-group chainlit-rg \\
  --plan chainlit-plan \\
  --name chainlit-app \\
  --runtime "PYTHON:3.10"

# 部署代碼
az webapp up --name chainlit-app
```

### 5. Heroku

```bash
# 創建應用
heroku create chainlit-app

# 設置環境變量
heroku config:set OPENAI_API_KEY=your-key

# 部署
git push heroku main
```

**Procfile：**
```
web: chainlit run app.py -h 0.0.0.0 -p $PORT
```

### 📊 成本比較

| 平台 | 免費額度 | 基礎費用/月 | 擴展性 |
|------|----------|-------------|--------|
| Chainlit Cloud | 有 | $29 | 自動 |
| AWS EB | 750h | ~$10 | 手動 |
| GCP Cloud Run | 180萬請求 | ~$5 | 自動 |
| Azure | $200信用 | ~$13 | 手動 |
| Heroku | 550h | $7 | 手動 |
    """

    await cl.Message(content=guide, author="雲端部署").send()


async def show_config_guide():
    """顯示配置說明"""
    guide = f"""
## ⚙️ 配置說明

### 環境變量

#### 必需變量

```bash
# OpenAI API Key
export OPENAI_API_KEY="sk-..."

# 環境標識
export ENVIRONMENT="production"  # development, staging, production
```

#### 可選變量

```bash
# 應用配置
export APP_NAME="My Chainlit App"
export APP_VERSION="1.0.0"

# 服務器配置
export HOST="0.0.0.0"
export PORT="8000"

# 認證配置
export AUTH_ENABLED="true"
export JWT_SECRET="your-secret-key-here"

# 數據庫配置
export DATABASE_URL="postgresql://user:pass@host:5432/db"

# 性能配置
export MAX_CONCURRENT_REQUESTS="10"
export REQUEST_TIMEOUT="30"

# 日誌配置
export LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR
```

### Chainlit 配置文件

創建 `.chainlit/config.toml`：

```toml
[project]
# 是否啟用遙測
enable_telemetry = false

[features]
# 自發文件上傳
spontaneous_file_upload = {{
    enabled = true,
    accept = ["image/png", "image/jpeg"],
    max_size_mb = 10
}}

# Latex 支持
latex = true

[UI]
# 應用名稱
name = "{config.app_name}"

# 默認折疊內容
default_collapse_content = true

# 默認展開消息
default_expand_messages = false

# 隱藏來源
hide_cot = false

[theme]
# 主題顏色
primary = "#007bff"
background = "#ffffff"

[auth]
# 認證配置（如果需要）
secret = "your-jwt-secret"
```

### 當前配置狀態

{_format_current_config()}
    """

    await cl.Message(content=guide, author="配置管理").send()


async def show_security_guide():
    """顯示安全建議"""
    guide = """
## 🔐 安全建議

### 1. API Key 管理

```python
# ❌ 不要硬編碼
client = OpenAI(api_key="sk-...")

# ✅ 使用環境變量
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ 使用密鑰管理服務
# - AWS Secrets Manager
# - Google Secret Manager
# - Azure Key Vault
```

### 2. 用戶認證

```python
import chainlit as cl

@cl.password_auth_callback
async def auth_callback(username: str, password: str):
    # ✅ 使用安全的密碼哈希
    import hashlib
    hashed = hashlib.sha256(password.encode()).hexdigest()

    # ✅ 從安全的數據庫獲取用戶
    user = await get_user_from_db(username)

    if user and user.password_hash == hashed:
        return cl.User(identifier=username)

    return None
```

### 3. HTTPS/SSL

```nginx
# Nginx 配置
server {{
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {{
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}
}}
```

### 4. 速率限制

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@limiter.limit("10/minute")
async def on_message(message):
    # 處理消息
    pass
```

### 5. 輸入驗證

```python
@cl.on_message
async def on_message(message: cl.Message):
    # ✅ 驗證輸入長度
    if len(message.content) > 1000:
        await cl.Message("消息太長").send()
        return

    # ✅ 過濾危險內容
    if contains_dangerous_content(message.content):
        await cl.Message("檢測到危險內容").send()
        return

    # 處理消息...
```

### 6. CORS 設置

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # ❌ 不要用 "*"
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### 7. 環境隔離

```bash
# 開發環境
ENVIRONMENT=development
DEBUG=true

# 生產環境
ENVIRONMENT=production
DEBUG=false
SECURE_COOKIES=true
HTTPS_ONLY=true
```

### 8. 日誌管理

```python
import logging

# ✅ 不要記錄敏感信息
logger.info(f"User {{user_id}} logged in")

# ❌ 避免記錄密碼、API Key
# logger.info(f"Password: {{password}}")  # 不要這樣做！
```

### 🎯 安全檢查清單

- [ ] 使用環境變量存儲敏感信息
- [ ] 啟用 HTTPS
- [ ] 實施用戶認證
- [ ] 設置速率限制
- [ ] 驗證用戶輸入
- [ ] 配置 CORS
- [ ] 定期更新依賴
- [ ] 監控異常活動
- [ ] 備份重要數據
- [ ] 制定應急響應計劃
    """

    await cl.Message(content=guide, author="安全建議").send()


async def show_performance_guide():
    """顯示性能優化建議"""
    guide = """
## ⚡ 性能優化

### 1. 異步操作

```python
# ✅ 使用異步
@cl.on_message
async def on_message(message: cl.Message):
    result = await async_llm_call(message.content)
    await cl.Message(content=result).send()

# ❌ 避免同步阻塞
def sync_operation():
    time.sleep(5)  # 會阻塞整個應用
```

### 2. 連接池

```python
from openai import AsyncOpenAI

# ✅ 重用客戶端
client = AsyncOpenAI()

@cl.on_message
async def on_message(message):
    response = await client.chat.completions.create(...)
```

### 3. 緩存策略

```python
from functools import lru_cache
import redis

# 內存緩存
@lru_cache(maxsize=128)
def get_static_data(key):
    return expensive_operation(key)

# Redis 緩存
redis_client = redis.Redis()

async def get_with_cache(key):
    cached = redis_client.get(key)
    if cached:
        return cached

    result = await expensive_operation(key)
    redis_client.setex(key, 3600, result)
    return result
```

### 4. 流式響應

```python
# ✅ 使用流式輸出
@cl.on_message
async def on_message(message: cl.Message):
    msg = cl.Message(content="")
    await msg.send()

    stream = await client.chat.completions.create(
        model="gpt-4",
        messages=[...],
        stream=True
    )

    async for chunk in stream:
        await msg.stream_token(chunk.choices[0].delta.content)
```

### 5. 數據庫優化

```sql
-- ✅ 添加索引
CREATE INDEX idx_user_id ON messages(user_id);
CREATE INDEX idx_created_at ON messages(created_at);

-- ✅ 使用連接池
-- Python: SQLAlchemy, asyncpg
```

### 6. 負載均衡

```nginx
upstream chainlit_backend {{
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}}

server {{
    location / {{
        proxy_pass http://chainlit_backend;
    }}
}}
```

### 7. CDN 靜態資源

```html
<!-- ✅ 使用 CDN -->
<link href="https://cdn.example.com/style.css">

<!-- ❌ 避免服務器直接提供 -->
<link href="/static/style.css">
```

### 8. 監控和分析

```python
import time

@cl.on_message
async def on_message(message: cl.Message):
    start = time.time()

    # 處理消息
    result = await process(message)

    duration = time.time() - start
    print(f"處理時間: {{duration:.2f}}s")

    # 記錄到監控系統
    monitor.record_metric("response_time", duration)
```

### 📊 性能指標

目標：
- 🎯 平均響應時間 < 2s
- 🎯 P95 響應時間 < 5s
- 🎯 並發用戶 > 100
- 🎯 錯誤率 < 0.1%

當前配置：
- 最大並發: {config.max_concurrent_requests}
- 超時時間: {config.request_timeout}s
    """

    await cl.Message(content=guide, author="性能優化").send()


async def show_help():
    """顯示幫助信息"""
    help_msg = """
## 📚 部署指南

輸入以下命令查看具體指南：

- `docker` - Docker 容器化部署
- `cloud` - 雲端平台部署
- `config` - 環境配置說明
- `security` - 安全最佳實踐
- `performance` - 性能優化建議

### 🎯 快速開始

1. **本地開發**: `chainlit run app.py -w`
2. **Docker 部署**: 見 `docker` 指南
3. **雲端部署**: 見 `cloud` 指南

選擇一個命令開始探索！
    """

    await cl.Message(content=help_msg, author="幫助").send()


# ==================== 輔助函數 ====================

def _format_current_config() -> str:
    """格式化當前配置"""
    return f"""
**當前配置：**

- 環境: `{config.environment}`
- 應用: {config.app_name} v{config.app_version}
- 服務器: {config.host}:{config.port}
- OpenAI: {'已配置' if config.openai_api_key else '未配置'}
- 認證: {'啟用' if config.auth_enabled else '禁用'}
- 日誌級別: {config.log_level}
    """


# ==================== 主函數 ====================

def main():
    """主函數"""
    # 顯示配置
    config.display()

    # 驗證配置
    if not config.validate():
        print("\n❌ 配置驗證失敗，請檢查環境變量")
        sys.exit(1)

    print(f"""
╔══════════════════════════════════════════╗
║   Chainlit 部署上線示例                  ║
╚══════════════════════════════════════════╝

運行命令：
    chainlit run 10_部署上線.py -w

生產部署：
    chainlit run 10_部署上線.py -h 0.0.0.0 -p 8000

功能特點：
✅ 完整的部署指南
✅ Docker 容器化
✅ 多雲平台支持
✅ 安全最佳實踐
✅ 性能優化建議
✅ 配置管理
✅ 健康檢查

部署選項：
🐳 Docker
☁️ Chainlit Cloud
🌐 AWS / GCP / Azure
🚀 Heroku / Vercel

訪問 http://localhost:8000 查看完整指南！
    """)


if __name__ == "__main__":
    main()
