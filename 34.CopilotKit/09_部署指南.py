"""
CopilotKit 生產環境部署指南

這個文檔提供完整的生產環境部署指南，包括：
1. 環境配置
2. Docker 容器化
3. CI/CD 流程
4. 監控和日誌
5. 性能優化
6. 安全加固
7. 擴展策略
8. 故障恢復

注意：這是一個綜合性的部署指南，包含配置文件和腳本
"""

# ============================================================================
# 第一部分：生產環境配置
# ============================================================================

PRODUCTION_ENV = """
# .env.production - 生產環境配置

# 應用配置
APP_NAME=copilotkit-app
APP_ENV=production
DEBUG=false
LOG_LEVEL=info

# 服務器配置
HOST=0.0.0.0
PORT=8000
WORKERS=4  # 根據 CPU 核心數調整

# CORS 配置
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
ALLOWED_METHODS=GET,POST,PUT,DELETE
ALLOWED_HEADERS=*

# API Keys（使用環境變量或密鑰管理服務）
OPENAI_API_KEY=${OPENAI_API_KEY}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}

# 數據庫配置
DATABASE_URL=postgresql://user:password@postgres:5432/copilotkit
REDIS_URL=redis://redis:6379/0

# 會話和安全
SECRET_KEY=${SECRET_KEY}  # 使用強隨機密鑰
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=strict

# 速率限制
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# 監控
SENTRY_DSN=${SENTRY_DSN}
PROMETHEUS_ENABLED=true

# 日誌
LOG_FORMAT=json
LOG_FILE=/var/log/copilotkit/app.log
"""


# ============================================================================
# 第二部分：Docker 配置
# ============================================================================

DOCKERFILE = """
# Dockerfile - 多階段構建

# ========== 前端構建階段 ==========
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# 複製前端依賴文件
COPY frontend/package*.json ./

# 安裝依賴
RUN npm ci --only=production

# 複製前端源代碼
COPY frontend/ ./

# 構建前端
RUN npm run build


# ========== 後端構建階段 ==========
FROM python:3.11-slim AS backend-builder

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# 複製後端依賴文件
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir -r requirements.txt


# ========== 生產階段 ==========
FROM python:3.11-slim

WORKDIR /app

# 創建非 root 用戶
RUN useradd -m -u 1000 appuser && \\
    mkdir -p /var/log/copilotkit && \\
    chown -R appuser:appuser /var/log/copilotkit

# 從構建階段複製依賴
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# 複製應用代碼
COPY --chown=appuser:appuser . .

# 從前端構建階段複製靜態文件
COPY --from=frontend-builder --chown=appuser:appuser /app/frontend/build ./static

# 切換到非 root 用戶
USER appuser

# 暴露端口
EXPOSE 8000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# 啟動命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
"""


DOCKER_COMPOSE = """
# docker-compose.yml - 完整服務編排

version: '3.8'

services:
  # CopilotKit 應用
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: copilotkit-app
    restart: unless-stopped
    ports:
      - "8000:8000"
    env_file:
      - .env.production
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/copilotkit
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./logs:/var/log/copilotkit
    networks:
      - copilotkit-network
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.copilotkit.rule=Host(`api.yourdomain.com`)"
      - "traefik.http.routers.copilotkit.tls=true"

  # PostgreSQL 數據庫
  postgres:
    image: postgres:15-alpine
    container_name: copilotkit-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=copilotkit
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password  # 使用強密碼！
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - copilotkit-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis 緩存
  redis:
    image: redis:7-alpine
    container_name: copilotkit-redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    networks:
      - copilotkit-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Nginx 反向代理
  nginx:
    image: nginx:alpine
    container_name: copilotkit-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - ./static:/usr/share/nginx/html:ro
    depends_on:
      - app
    networks:
      - copilotkit-network

  # Prometheus 監控
  prometheus:
    image: prom/prometheus:latest
    container_name: copilotkit-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    networks:
      - copilotkit-network

  # Grafana 可視化
  grafana:
    image: grafana/grafana:latest
    container_name: copilotkit-grafana
    restart: unless-stopped
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin  # 修改默認密碼！
    volumes:
      - grafana-data:/var/lib/grafana
    networks:
      - copilotkit-network

volumes:
  postgres-data:
  redis-data:
  prometheus-data:
  grafana-data:

networks:
  copilotkit-network:
    driver: bridge
"""


# ============================================================================
# 第三部分：Nginx 配置
# ============================================================================

NGINX_CONFIG = """
# nginx.conf

events {
    worker_connections 1024;
}

http {
    upstream copilotkit_backend {
        server app:8000;
    }

    # 速率限制
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    server {
        listen 80;
        server_name api.yourdomain.com;

        # 重定向到 HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name api.yourdomain.com;

        # SSL 配置
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # 安全頭
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # 壓縮
        gzip on;
        gzip_types text/plain text/css application/json application/javascript;

        # API 代理
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;

            proxy_pass http://copilotkit_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # WebSocket 支持
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";

            # 超時設置
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # 靜態文件
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # 健康檢查
        location /health {
            proxy_pass http://copilotkit_backend/health;
            access_log off;
        }
    }
}
"""


# ============================================================================
# 第四部分：CI/CD 配置 (GitHub Actions)
# ============================================================================

GITHUB_ACTIONS = """
# .github/workflows/deploy.yml

name: Deploy to Production

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: pytest --cov=. --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: yourusername/copilotkit:latest
          cache-from: type=registry,ref=yourusername/copilotkit:buildcache
          cache-to: type=registry,ref=yourusername/copilotkit:buildcache,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /opt/copilotkit
            docker-compose pull
            docker-compose up -d
            docker-compose exec app alembic upgrade head
"""


# ============================================================================
# 第五部分：監控配置
# ============================================================================

PROMETHEUS_CONFIG = """
# prometheus.yml

global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'copilotkit'
    static_configs:
      - targets: ['app:8000']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:9121']
"""


# ============================================================================
# 第六部分：部署腳本
# ============================================================================

DEPLOY_SCRIPT = """#!/bin/bash
# deploy.sh - 自動化部署腳本

set -e

echo "🚀 開始部署 CopilotKit..."

# 檢查環境
if [ ! -f .env.production ]; then
    echo "❌ 錯誤：未找到 .env.production 文件"
    exit 1
fi

# 備份數據庫
echo "📦 備份數據庫..."
docker-compose exec postgres pg_dump -U postgres copilotkit > backup_$(date +%Y%m%d_%H%M%S).sql

# 拉取最新代碼
echo "📥 拉取最新代碼..."
git pull origin main

# 構建鏡像
echo "🔨 構建 Docker 鏡像..."
docker-compose build --no-cache

# 停止舊容器
echo "⏸️  停止舊容器..."
docker-compose down

# 啟動新容器
echo "▶️  啟動新容器..."
docker-compose up -d

# 數據庫遷移
echo "🗄️  執行數據庫遷移..."
docker-compose exec app alembic upgrade head

# 健康檢查
echo "🏥 執行健康檢查..."
sleep 10
if curl -f http://localhost:8000/health; then
    echo "✅ 部署成功！"
else
    echo "❌ 健康檢查失敗，回滾..."
    docker-compose down
    docker-compose up -d
    exit 1
fi

# 清理舊鏡像
echo "🧹 清理舊鏡像..."
docker image prune -f

echo "🎉 部署完成！"
"""


# ============================================================================
# 運行說明
# ============================================================================

if __name__ == "__main__":
    print("\\n" + "="*70)
    print("CopilotKit 生產環境部署指南")
    print("="*70)
    print("\\n包含的配置文件：")
    print("  • .env.production - 環境變量")
    print("  • Dockerfile - Docker 鏡像")
    print("  • docker-compose.yml - 服務編排")
    print("  • nginx.conf - 反向代理")
    print("  • .github/workflows/deploy.yml - CI/CD")
    print("  • prometheus.yml - 監控")
    print("  • deploy.sh - 部署腳本")
    print("\\n部署步驟：")
    print("  1. 配置環境變量")
    print("  2. 設置 SSL 證書")
    print("  3. 配置數據庫")
    print("  4. 運行 docker-compose up -d")
    print("  5. 設置監控和日誌")
    print("  6. 配置 CI/CD 流程")
    print("="*70 + "\\n")

    # 創建部署配置文件
    import os

    # 創建必要的目錄
    os.makedirs("deployment", exist_ok=True)

    # 寫入配置文件
    with open("deployment/.env.production.example", "w") as f:
        f.write(PRODUCTION_ENV)

    with open("deployment/Dockerfile", "w") as f:
        f.write(DOCKERFILE)

    with open("deployment/docker-compose.yml", "w") as f:
        f.write(DOCKER_COMPOSE)

    with open("deployment/nginx.conf", "w") as f:
        f.write(NGINX_CONFIG)

    with open("deployment/deploy.sh", "w") as f:
        f.write(DEPLOY_SCRIPT)

    # 設置執行權限
    os.chmod("deployment/deploy.sh", 0o755)

    print("✅ 部署配置文件已創建在 deployment/ 目錄")


"""
生產環境部署檢查清單：

前期準備：
□ 註冊域名
□ 獲取 SSL 證書
□ 設置 DNS 記錄
□ 準備服務器（雲服務器或 VPS）
□ 配置防火牆

環境配置：
□ 安裝 Docker 和 Docker Compose
□ 配置環境變量
□ 設置數據庫
□ 配置 Redis
□ 設置日誌目錄

安全加固：
□ 使用強密碼
□ 啟用 HTTPS
□ 配置防火牆規則
□ 設置速率限制
□ 啟用安全頭
□ 定期更新依賴

監控和日誌：
□ 配置 Prometheus
□ 設置 Grafana 儀表板
□ 配置日誌聚合
□ 設置告警規則
□ 配置錯誤追蹤（Sentry）

備份策略：
□ 定期數據庫備份
□ 配置文件備份
□ 設置自動備份
□ 測試恢復流程

性能優化：
□ 啟用緩存
□ 配置 CDN
□ 優化數據庫查詢
□ 啟用 Gzip 壓縮
□ 設置合理的工作進程數

CI/CD：
□ 配置自動測試
□ 設置自動部署
□ 配置回滾機制
□ 設置部署通知

上線後：
□ 監控應用性能
□ 檢查錯誤日誌
□ 測試所有功能
□ 監控資源使用
□ 收集用戶反饋

常見問題：

Q: 如何擴展應用？
A: 1. 水平擴展：增加應用實例
   2. 垂直擴展：增加服務器資源
   3. 數據庫讀寫分離
   4. 使用負載均衡器

Q: 如何處理零停機部署？
A: 1. 使用藍綠部署
   2. 滾動更新
   3. 健康檢查
   4. 優雅關閉

Q: 如何監控應用健康？
A: 1. Prometheus + Grafana
   2. 健康檢查端點
   3. 日誌監控
   4. APM 工具

下一步：
- 查看 10_最佳實踐.py 了解最佳實踐
- 閱讀官方文檔的部署指南
- 根據實際需求調整配置
"""
