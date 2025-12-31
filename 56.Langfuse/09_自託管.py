"""
Langfuse 自託管設置示例

這個示例展示如何自託管 Langfuse，包括：
- Docker 部署配置
- 環境變量設置
- 數據庫配置
- 反向代理設置
- 備份和恢復
- 監控和維護

主要內容：
1. Docker Compose 部署
2. 環境配置管理
3. 數據庫設置和遷移
4. 安全配置
5. 備份策略
6. 性能優化
7. 故障排除

作者: Langfuse Team
日期: 2025-01-01
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional


# ============================================================================
# 第一部分：Docker Compose 部署
# ============================================================================

class DockerDeployment:
    """
    Docker 部署配置

    提供 Docker Compose 部署的完整配置。
    """

    @staticmethod
    def generate_docker_compose():
        """
        生成 Docker Compose 配置文件

        這個方法展示完整的 docker-compose.yml 配置。
        """
        print("\n" + "="*60)
        print("Docker Compose 配置生成")
        print("="*60)

        docker_compose = """version: '3.8'

services:
  # PostgreSQL 數據庫
  db:
    image: postgres:15-alpine
    container_name: langfuse-db
    restart: always
    environment:
      POSTGRES_DB: langfuse
      POSTGRES_USER: langfuse
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - langfuse-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U langfuse"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis (可選，用於緩存和會話)
  redis:
    image: redis:7-alpine
    container_name: langfuse-redis
    restart: always
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - langfuse-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Langfuse 應用
  langfuse:
    image: langfuse/langfuse:latest
    container_name: langfuse-app
    restart: always
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      # 數據庫配置
      DATABASE_URL: postgresql://langfuse:${DB_PASSWORD:-changeme}@db:5432/langfuse

      # Redis 配置 (可選)
      REDIS_URL: redis://redis:6379

      # 應用配置
      NEXTAUTH_URL: ${NEXTAUTH_URL:-http://localhost:3000}
      NEXTAUTH_SECRET: ${NEXTAUTH_SECRET:-generate-a-random-secret-here}

      # 認證配置
      SALT: ${SALT:-generate-a-random-salt-here}

      # Telemetry (可選，設為 false 禁用)
      TELEMETRY_ENABLED: ${TELEMETRY_ENABLED:-true}

      # 日誌級別
      LOG_LEVEL: ${LOG_LEVEL:-info}

      # 其他配置
      NODE_ENV: production
    ports:
      - "${PORT:-3000}:3000"
    networks:
      - langfuse-network
    volumes:
      - langfuse_data:/app/data
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Nginx 反向代理 (可選)
  nginx:
    image: nginx:alpine
    container_name: langfuse-nginx
    restart: always
    depends_on:
      - langfuse
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - nginx_logs:/var/log/nginx
    networks:
      - langfuse-network

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  langfuse_data:
    driver: local
  nginx_logs:
    driver: local

networks:
  langfuse-network:
    driver: bridge
"""

        print("📝 Docker Compose 配置:")
        print("-" * 60)
        print(docker_compose)
        print("-" * 60)

        print("\n✅ Docker Compose 配置生成完成")

        return docker_compose

    @staticmethod
    def generate_env_file():
        """
        生成環境變量文件

        創建 .env 文件配置。
        """
        print("\n" + "="*60)
        print("環境變量配置生成")
        print("="*60)

        env_config = """# Langfuse 自託管環境變量配置
# 生成時間: {timestamp}

# ==============================================
# 數據庫配置
# ==============================================
DB_PASSWORD=your-secure-db-password-here

# ==============================================
# 應用配置
# ==============================================
# 應用訪問 URL
NEXTAUTH_URL=https://langfuse.yourdomain.com

# NextAuth Secret (使用 openssl rand -base64 32 生成)
NEXTAUTH_SECRET=your-nextauth-secret-here

# Salt (使用 openssl rand -base64 32 生成)
SALT=your-salt-here

# ==============================================
# 服務端口
# ==============================================
PORT=3000

# ==============================================
# 可選配置
# ==============================================
# Redis URL (如果使用 Redis)
# REDIS_URL=redis://redis:6379

# 日誌級別 (error, warn, info, debug)
LOG_LEVEL=info

# 是否啟用 Telemetry
TELEMETRY_ENABLED=false

# ==============================================
# 郵件配置 (用於通知)
# ==============================================
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=your-email@gmail.com
# SMTP_PASSWORD=your-app-password
# EMAIL_FROM=langfuse@yourdomain.com

# ==============================================
# S3 存儲配置 (可選，用於大文件存儲)
# ==============================================
# S3_ENDPOINT=https://s3.amazonaws.com
# S3_ACCESS_KEY_ID=your-access-key
# S3_SECRET_ACCESS_KEY=your-secret-key
# S3_BUCKET_NAME=langfuse-data
# S3_REGION=us-east-1

# ==============================================
# 認證提供商 (可選)
# ==============================================
# Google OAuth
# GOOGLE_CLIENT_ID=your-google-client-id
# GOOGLE_CLIENT_SECRET=your-google-client-secret

# GitHub OAuth
# GITHUB_CLIENT_ID=your-github-client-id
# GITHUB_CLIENT_SECRET=your-github-client-secret

# ==============================================
# 性能優化
# ==============================================
# Node.js 內存限制 (MB)
# NODE_OPTIONS=--max-old-space-size=4096

# 工作進程數
# WEB_CONCURRENCY=2
""".format(timestamp=datetime.now().isoformat())

        print("📝 環境變量配置:")
        print("-" * 60)
        print(env_config)
        print("-" * 60)

        print("\n⚠️  重要提示:")
        print("   1. 務必更改所有密碼和密鑰")
        print("   2. 使用強隨機字符串作為 SECRET 和 SALT")
        print("   3. 不要將 .env 文件提交到版本控制")
        print("   4. 定期輪換密鑰以提高安全性")

        print("\n✅ 環境變量配置生成完成")

        return env_config

    @staticmethod
    def generate_nginx_config():
        """
        生成 Nginx 配置

        創建反向代理和 SSL 配置。
        """
        print("\n" + "="*60)
        print("Nginx 配置生成")
        print("="*60)

        nginx_config = """# Langfuse Nginx 配置

upstream langfuse_backend {
    server langfuse:3000;
    keepalive 32;
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name langfuse.yourdomain.com;

    # Let's Encrypt 驗證路徑
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # 其他請求重定向到 HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS 配置
server {
    listen 443 ssl http2;
    server_name langfuse.yourdomain.com;

    # SSL 證書
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    # SSL 配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 安全標頭
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # 客戶端最大請求體大小
    client_max_body_size 100M;

    # 超時設置
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    # 代理到 Langfuse
    location / {
        proxy_pass http://langfuse_backend;

        # 代理標頭
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 緩存設置
        proxy_cache_bypass $http_upgrade;
        proxy_no_cache $http_pragma $http_authorization;
    }

    # 靜態文件緩存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff|woff2)$ {
        proxy_pass http://langfuse_backend;
        proxy_set_header Host $host;

        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # 健康檢查端點
    location /api/health {
        proxy_pass http://langfuse_backend;
        access_log off;
    }

    # 訪問日誌
    access_log /var/log/nginx/langfuse-access.log;
    error_log /var/log/nginx/langfuse-error.log;
}
"""

        print("📝 Nginx 配置:")
        print("-" * 60)
        print(nginx_config)
        print("-" * 60)

        print("\n✅ Nginx 配置生成完成")

        return nginx_config


# ============================================================================
# 第二部分：部署和管理腳本
# ============================================================================

class DeploymentScripts:
    """
    部署和管理腳本

    提供常用的部署和管理命令。
    """

    @staticmethod
    def generate_deployment_guide():
        """
        生成部署指南

        提供完整的部署步驟。
        """
        print("\n" + "="*60)
        print("自託管部署指南")
        print("="*60)

        guide = """
╔══════════════════════════════════════════════════════════════╗
║           Langfuse 自託管部署完整指南                        ║
╚══════════════════════════════════════════════════════════════╝

📋 前置要求
─────────────────────────────────────────────────────
• Docker Engine 20.10+
• Docker Compose 2.0+
• 至少 2GB RAM
• 至少 10GB 磁盤空間
• (可選) 域名和 SSL 證書


🔧 第一步：準備環境
─────────────────────────────────────────────────────
1. 創建項目目錄:
   mkdir langfuse-selfhosted
   cd langfuse-selfhosted

2. 創建必要的配置文件:
   touch docker-compose.yml
   touch .env
   touch nginx.conf

3. 生成密鑰 (保存這些值到 .env):
   # NEXTAUTH_SECRET
   openssl rand -base64 32

   # SALT
   openssl rand -base64 32


📝 第二步：配置文件
─────────────────────────────────────────────────────
1. 編輯 .env 文件，設置必要的環境變量
2. 修改 docker-compose.yml 中的配置
3. (如使用 Nginx) 配置 nginx.conf


🚀 第三步：啟動服務
─────────────────────────────────────────────────────
1. 首次啟動 (會下載鏡像):
   docker-compose up -d

2. 查看日誌:
   docker-compose logs -f langfuse

3. 檢查服務狀態:
   docker-compose ps


🔐 第四步：初始化設置
─────────────────────────────────────────────────────
1. 訪問 http://localhost:3000 (或您的域名)
2. 創建管理員賬戶
3. 配置組織設置
4. 生成 API 密鑰


✅ 第五步：驗證部署
─────────────────────────────────────────────────────
1. 測試 Web UI 訪問
2. 測試 API 端點:
   curl http://localhost:3000/api/health

3. 測試追蹤記錄:
   # 使用生成的 API 密鑰測試


🔄 第六步：配置備份
─────────────────────────────────────────────────────
1. 設置定期數據庫備份
2. 配置備份存儲位置
3. 測試恢復流程


📊 第七步：監控設置
─────────────────────────────────────────────────────
1. 配置日誌收集
2. 設置性能監控
3. 配置告警規則


🔧 常用管理命令
─────────────────────────────────────────────────────
# 啟動服務
docker-compose up -d

# 停止服務
docker-compose down

# 重啟服務
docker-compose restart

# 查看日誌
docker-compose logs -f [service_name]

# 更新到最新版本
docker-compose pull
docker-compose up -d

# 備份數據庫
docker-compose exec db pg_dump -U langfuse langfuse > backup.sql

# 恢復數據庫
docker-compose exec -T db psql -U langfuse langfuse < backup.sql

# 清理未使用的資源
docker system prune -a


⚠️  重要注意事項
─────────────────────────────────────────────────────
1. 定期更新到最新版本
2. 保持數據庫定期備份
3. 監控磁盤空間使用
4. 定期檢查安全更新
5. 使用 HTTPS (生產環境必須)
6. 限制數據庫和 Redis 的網絡訪問
7. 定期審查訪問日誌


🔒 安全建議
─────────────────────────────────────────────────────
1. 使用強密碼和密鑰
2. 啟用防火牆規則
3. 配置 SSL/TLS
4. 定期更新系統和依賴
5. 實施訪問控制
6. 啟用審計日誌
7. 定期進行安全掃描


📚 更多資源
─────────────────────────────────────────────────────
• 官方文檔: https://langfuse.com/docs/deployment/self-host
• GitHub: https://github.com/langfuse/langfuse
• Discord 社區: https://discord.gg/langfuse
"""

        print(guide)
        print("\n✅ 部署指南生成完成")

        return guide

    @staticmethod
    def generate_management_scripts():
        """
        生成管理腳本

        創建常用的管理和維護腳本。
        """
        print("\n" + "="*60)
        print("管理腳本生成")
        print("="*60)

        # 備份腳本
        backup_script = """#!/bin/bash
# Langfuse 備份腳本

set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="langfuse_backup_${TIMESTAMP}.tar.gz"

echo "開始備份 Langfuse..."

# 創建備份目錄
mkdir -p $BACKUP_DIR

# 備份數據庫
echo "備份數據庫..."
docker-compose exec -T db pg_dump -U langfuse langfuse | gzip > $BACKUP_DIR/db_${TIMESTAMP}.sql.gz

# 備份 volumes
echo "備份數據卷..."
docker run --rm \\
    -v langfuse-selfhosted_postgres_data:/data \\
    -v $(pwd)/$BACKUP_DIR:/backup \\
    alpine tar czf /backup/postgres_${TIMESTAMP}.tar.gz -C /data .

# 備份配置文件
echo "備份配置文件..."
tar czf $BACKUP_DIR/config_${TIMESTAMP}.tar.gz \\
    docker-compose.yml \\
    .env \\
    nginx.conf 2>/dev/null || true

echo "備份完成: $BACKUP_DIR"
echo "清理 30 天前的備份..."
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "✅ 備份成功完成"
"""

        # 恢復腳本
        restore_script = """#!/bin/bash
# Langfuse 恢復腳本

set -e

if [ -z "$1" ]; then
    echo "用法: ./restore.sh <backup_timestamp>"
    echo "例如: ./restore.sh 20250101_120000"
    exit 1
fi

TIMESTAMP=$1
BACKUP_DIR="./backups"

echo "開始恢復 Langfuse (時間戳: $TIMESTAMP)..."

# 停止服務
echo "停止服務..."
docker-compose down

# 恢復數據庫
if [ -f "$BACKUP_DIR/db_${TIMESTAMP}.sql.gz" ]; then
    echo "恢復數據庫..."
    docker-compose up -d db
    sleep 10
    gunzip < $BACKUP_DIR/db_${TIMESTAMP}.sql.gz | docker-compose exec -T db psql -U langfuse langfuse
else
    echo "⚠️  找不到數據庫備份文件"
fi

# 恢復配置
if [ -f "$BACKUP_DIR/config_${TIMESTAMP}.tar.gz" ]; then
    echo "恢復配置文件..."
    tar xzf $BACKUP_DIR/config_${TIMESTAMP}.tar.gz
else
    echo "⚠️  找不到配置備份文件"
fi

# 啟動所有服務
echo "啟動服務..."
docker-compose up -d

echo "✅ 恢復完成"
"""

        # 更新腳本
        update_script = """#!/bin/bash
# Langfuse 更新腳本

set -e

echo "開始更新 Langfuse..."

# 備份
echo "執行備份..."
./backup.sh

# 拉取最新鏡像
echo "拉取最新鏡像..."
docker-compose pull

# 重啟服務
echo "重啟服務..."
docker-compose down
docker-compose up -d

# 等待服務啟動
echo "等待服務啟動..."
sleep 20

# 檢查健康狀態
echo "檢查健康狀態..."
curl -f http://localhost:3000/api/health || echo "⚠️  健康檢查失敗"

echo "✅ 更新完成"
docker-compose ps
"""

        # 監控腳本
        monitor_script = """#!/bin/bash
# Langfuse 監控腳本

echo "Langfuse 系統狀態"
echo "=================="

# 服務狀態
echo "
📊 服務狀態:"
docker-compose ps

# 資源使用
echo "
💾 資源使用:"
docker stats --no-stream --format "table {{.Name}}\\t{{.CPUPerc}}\\t{{.MemUsage}}" langfuse-app langfuse-db langfuse-redis

# 磁盤使用
echo "
💿 磁盤使用:"
docker system df

# 最近日誌
echo "
📝 最近日誌 (最後 20 行):"
docker-compose logs --tail=20 langfuse

# 數據庫大小
echo "
🗄️  數據庫大小:"
docker-compose exec db psql -U langfuse -d langfuse -c "
SELECT pg_size_pretty(pg_database_size('langfuse')) as db_size;
"

echo "
✅ 監控完成"
"""

        print("\n📝 生成的管理腳本:\n")
        print("1. backup.sh - 備份腳本")
        print("2. restore.sh - 恢復腳本")
        print("3. update.sh - 更新腳本")
        print("4. monitor.sh - 監控腳本")

        print("\n💡 使用方法:")
        print("   chmod +x *.sh")
        print("   ./backup.sh")
        print("   ./monitor.sh")

        print("\n✅ 管理腳本生成完成")

        return {
            "backup": backup_script,
            "restore": restore_script,
            "update": update_script,
            "monitor": monitor_script
        }


# ============================================================================
# 第三部分：故障排除
# ============================================================================

class Troubleshooting:
    """
    故障排除指南

    提供常見問題的解決方案。
    """

    @staticmethod
    def generate_troubleshooting_guide():
        """
        生成故障排除指南

        列出常見問題和解決方案。
        """
        print("\n" + "="*60)
        print("故障排除指南")
        print("="*60)

        guide = """
╔══════════════════════════════════════════════════════════════╗
║                 Langfuse 故障排除指南                        ║
╚══════════════════════════════════════════════════════════════╝

❌ 問題 1: 服務無法啟動
─────────────────────────────────────────────────────
症狀: docker-compose up 失敗或服務立即退出

解決方案:
1. 檢查日誌:
   docker-compose logs langfuse

2. 驗證環境變量:
   docker-compose config

3. 檢查端口衝突:
   netstat -tuln | grep 3000

4. 確保數據庫健康:
   docker-compose exec db pg_isready -U langfuse


❌ 問題 2: 無法連接數據庫
─────────────────────────────────────────────────────
症狀: "ECONNREFUSED" 或 "connection refused"

解決方案:
1. 檢查數據庫狀態:
   docker-compose ps db

2. 驗證連接字符串:
   echo $DATABASE_URL

3. 重啟數據庫:
   docker-compose restart db

4. 檢查網絡:
   docker network ls
   docker network inspect langfuse-selfhosted_langfuse-network


❌ 問題 3: 內存不足
─────────────────────────────────────────────────────
症狀: 服務緩慢或 OOM killed

解決方案:
1. 增加內存限制:
   # 在 docker-compose.yml 中添加:
   deploy:
     resources:
       limits:
         memory: 2G

2. 優化 Node.js 內存:
   NODE_OPTIONS=--max-old-space-size=2048

3. 清理未使用資源:
   docker system prune -a


❌ 問題 4: SSL/HTTPS 問題
─────────────────────────────────────────────────────
症狀: 證書錯誤或 HTTPS 無法訪問

解決方案:
1. 驗證證書文件:
   ls -la /path/to/ssl/

2. 檢查 Nginx 配置:
   docker-compose exec nginx nginx -t

3. 使用 Let's Encrypt:
   certbot certonly --webroot -w /var/www/certbot \\
     -d langfuse.yourdomain.com

4. 重新加載 Nginx:
   docker-compose restart nginx


❌ 問題 5: 性能問題
─────────────────────────────────────────────────────
症狀: 響應緩慢或超時

解決方案:
1. 檢查資源使用:
   docker stats

2. 優化數據庫:
   docker-compose exec db psql -U langfuse -d langfuse -c "VACUUM ANALYZE;"

3. 增加工作進程:
   WEB_CONCURRENCY=4

4. 啟用 Redis 緩存

5. 添加數據庫連接池


❌ 問題 6: 數據丟失或損壞
─────────────────────────────────────────────────────
症狀: 數據無法訪問或不完整

解決方案:
1. 從備份恢復:
   ./restore.sh <timestamp>

2. 檢查數據庫完整性:
   docker-compose exec db pg_dump -U langfuse langfuse > test.sql

3. 修復數據庫:
   docker-compose exec db psql -U langfuse -d langfuse -c "REINDEX DATABASE langfuse;"


❌ 問題 7: 更新失敗
─────────────────────────────────────────────────────
症狀: 更新後服務無法啟動

解決方案:
1. 回滾到舊版本:
   docker-compose down
   # 修改 docker-compose.yml 使用舊版本
   docker-compose up -d

2. 檢查遷移日誌:
   docker-compose logs langfuse | grep migration

3. 手動運行遷移:
   docker-compose exec langfuse npm run db:migrate


🔍 調試技巧
─────────────────────────────────────────────────────
1. 啟用調試日誌:
   LOG_LEVEL=debug

2. 進入容器調試:
   docker-compose exec langfuse sh

3. 檢查網絡連通性:
   docker-compose exec langfuse ping db

4. 查看完整環境變量:
   docker-compose exec langfuse env


📞 獲取幫助
─────────────────────────────────────────────────────
• GitHub Issues: https://github.com/langfuse/langfuse/issues
• Discord: https://discord.gg/langfuse
• 文檔: https://langfuse.com/docs
"""

        print(guide)
        print("\n✅ 故障排除指南生成完成")

        return guide


# ============================================================================
# 主程序
# ============================================================================

def main():
    """
    主函數：生成所有自託管配置和文檔
    """
    print("\n" + "="*70)
    print("Langfuse 自託管設置示例")
    print("="*70)

    print("\n本示例將生成完整的自託管部署配置和文檔")

    try:
        # 1. Docker 部署配置
        print("\n第一部分：Docker 部署配置")
        print("="*70)
        docker = DockerDeployment()
        docker.generate_docker_compose()
        docker.generate_env_file()
        docker.generate_nginx_config()

        # 2. 部署和管理
        print("\n第二部分：部署和管理")
        print("="*70)
        scripts = DeploymentScripts()
        scripts.generate_deployment_guide()
        scripts.generate_management_scripts()

        # 3. 故障排除
        print("\n第三部分：故障排除")
        print("="*70)
        troubleshooting = Troubleshooting()
        troubleshooting.generate_troubleshooting_guide()

        print("\n" + "="*70)
        print("✅ 所有自託管配置和文檔生成完成！")
        print("="*70)

        print("\n📋 生成的配置清單:")
        print("   ✓ docker-compose.yml - Docker Compose 配置")
        print("   ✓ .env - 環境變量配置")
        print("   ✓ nginx.conf - Nginx 反向代理配置")
        print("   ✓ 部署指南 - 完整的部署步驟")
        print("   ✓ 管理腳本 - 備份、恢復、更新、監控")
        print("   ✓ 故障排除指南 - 常見問題解決方案")

        print("\n💡 下一步:")
        print("   1. 將生成的配置保存到文件")
        print("   2. 根據您的環境調整配置")
        print("   3. 生成安全的密鑰和密碼")
        print("   4. 按照部署指南執行部署")
        print("   5. 配置備份和監控")

        print("\n⚠️  重要提醒:")
        print("   • 務必使用強密碼和密鑰")
        print("   • 生產環境必須使用 HTTPS")
        print("   • 定期備份數據")
        print("   • 保持系統更新")
        print("   • 監控資源使用")

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
