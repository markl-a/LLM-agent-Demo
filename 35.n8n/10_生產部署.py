"""
n8n 生產部署
============

本範例展示如何在生產環境部署 n8n，包括：
- Docker 部署配置
- 數據庫設置
- 環境變量配置
- 監控和日誌
- 備份和恢復

安裝依賴:
pip install requests python-dotenv docker

作者: n8n Demo
日期: 2025-12-31
"""

import os
import requests
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 加載環境變量
load_dotenv()


class N8NProductionDeployment:
    """
    n8n 生產部署工具

    提供生產環境部署的配置和管理功能
    """

    def __init__(self, base_url: str = "http://localhost:5678", api_key: Optional[str] = None):
        """初始化部署工具"""
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv("N8N_API_KEY")

        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                "X-N8N-API-KEY": self.api_key,
                "Content-Type": "application/json"
            })

        print(f"✓ n8n 生產部署工具已初始化")

    def generate_docker_compose(self) -> str:
        """
        示例 1: 生成生產環境 Docker Compose 配置

        返回:
            Docker Compose YAML 內容
        """
        print("\n" + "="*60)
        print("示例 1: 生成生產環境 Docker Compose 配置")
        print("="*60)

        docker_compose = """version: '3.8'

services:
  # n8n 主服務
  n8n:
    image: n8nio/n8n:latest
    restart: always
    ports:
      - "5678:5678"
    environment:
      # 基本配置
      - N8N_HOST=${N8N_HOST:-localhost}
      - N8N_PORT=5678
      - N8N_PROTOCOL=${N8N_PROTOCOL:-https}
      - NODE_ENV=production

      # Webhook 配置
      - WEBHOOK_URL=${WEBHOOK_URL:-https://n8n.yourdomain.com/}

      # 認證配置
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_AUTH_USER:-admin}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_AUTH_PASSWORD}

      # 數據庫配置（PostgreSQL）
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=${POSTGRES_DB:-n8n}
      - DB_POSTGRESDB_USER=${POSTGRES_USER:-n8n}
      - DB_POSTGRESDB_PASSWORD=${POSTGRES_PASSWORD}

      # 執行配置
      - EXECUTIONS_PROCESS=main
      - EXECUTIONS_DATA_SAVE_ON_ERROR=all
      - EXECUTIONS_DATA_SAVE_ON_SUCCESS=all
      - EXECUTIONS_DATA_SAVE_MANUAL_EXECUTIONS=true
      - EXECUTIONS_DATA_MAX_AGE=336  # 14 天

      # 性能配置
      - N8N_PAYLOAD_SIZE_MAX=16
      - N8N_METRICS=true

      # 日誌配置
      - N8N_LOG_LEVEL=info
      - N8N_LOG_OUTPUT=console,file
      - N8N_LOG_FILE_LOCATION=/home/node/.n8n/logs/

      # AI 服務 API Keys
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}

      # 向量數據庫
      - PINECONE_API_KEY=${PINECONE_API_KEY}
      - QDRANT_API_KEY=${QDRANT_API_KEY}

      # 加密密鑰（重要！）
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}

    volumes:
      - n8n_data:/home/node/.n8n
      - ./logs:/home/node/.n8n/logs
    networks:
      - n8n-network
    depends_on:
      - postgres
      - redis
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:5678/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3

  # PostgreSQL 數據庫
  postgres:
    image: postgres:15-alpine
    restart: always
    environment:
      - POSTGRES_DB=${POSTGRES_DB:-n8n}
      - POSTGRES_USER=${POSTGRES_USER:-n8n}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - PGDATA=/var/lib/postgresql/data/pgdata
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - n8n-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-n8n}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis（緩存和隊列）
  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - n8n-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Nginx 反向代理（可選）
  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    networks:
      - n8n-network
    depends_on:
      - n8n

volumes:
  n8n_data:
    driver: local
  postgres_data:
    driver: local
  redis_data:
    driver: local

networks:
  n8n-network:
    driver: bridge
"""

        # 保存到文件
        filename = "docker-compose.production.yml"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(docker_compose)

        print(f"\n✓ Docker Compose 配置已生成")
        print(f"  文件: {filename}")
        print(f"\n  使用方法:")
        print(f"  1. 創建 .env 文件並設置必要的環境變量")
        print(f"  2. 運行: docker-compose -f {filename} up -d")

        return docker_compose

    def generate_env_template(self) -> str:
        """
        示例 2: 生成環境變量模板

        返回:
            .env 文件內容
        """
        print("\n" + "="*60)
        print("示例 2: 生成環境變量模板")
        print("="*60)

        env_template = """# n8n 生產環境配置

# ========================================
# 基本配置
# ========================================
N8N_HOST=n8n.yourdomain.com
N8N_PROTOCOL=https
WEBHOOK_URL=https://n8n.yourdomain.com/

# ========================================
# 認證配置
# ========================================
N8N_AUTH_USER=admin
N8N_AUTH_PASSWORD=change-this-strong-password

# ========================================
# 數據庫配置
# ========================================
POSTGRES_DB=n8n
POSTGRES_USER=n8n
POSTGRES_PASSWORD=change-this-db-password

# ========================================
# 加密密鑰（重要！不要洩露）
# ========================================
# 生成方法: openssl rand -base64 32
N8N_ENCRYPTION_KEY=your-encryption-key-here

# ========================================
# AI 服務 API Keys
# ========================================
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# ========================================
# 向量數據庫
# ========================================
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=...
QDRANT_API_KEY=...
QDRANT_URL=...

# ========================================
# 郵件服務（用於通知）
# ========================================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# ========================================
# 監控和日誌
# ========================================
N8N_METRICS=true
N8N_LOG_LEVEL=info

# ========================================
# 性能調優
# ========================================
N8N_PAYLOAD_SIZE_MAX=16
EXECUTIONS_DATA_MAX_AGE=336

# ========================================
# 其他配置
# ========================================
TIMEZONE=Asia/Taipei
"""

        filename = ".env.example"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(env_template)

        print(f"\n✓ 環境變量模板已生成")
        print(f"  文件: {filename}")
        print(f"\n  使用方法:")
        print(f"  1. 複製: cp {filename} .env")
        print(f"  2. 編輯 .env 並設置實際的值")
        print(f"  3. 確保 .env 文件不被提交到版本控制")

        return env_template

    def generate_nginx_config(self) -> str:
        """
        示例 3: 生成 Nginx 配置

        返回:
            Nginx 配置內容
        """
        print("\n" + "="*60)
        print("示例 3: 生成 Nginx 配置")
        print("="*60)

        nginx_config = """# n8n Nginx 配置

# HTTP -> HTTPS 重定向
server {
    listen 80;
    server_name n8n.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS 配置
server {
    listen 443 ssl http2;
    server_name n8n.yourdomain.com;

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
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # 日誌
    access_log /var/log/nginx/n8n_access.log;
    error_log /var/log/nginx/n8n_error.log;

    # 客戶端配置
    client_max_body_size 50M;

    # 代理到 n8n
    location / {
        proxy_pass http://n8n:5678;
        proxy_http_version 1.1;

        # WebSocket 支持
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';

        # 標準代理頭
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超時設置
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;

        # 緩存控制
        proxy_cache_bypass $http_upgrade;
    }

    # 健康檢查端點
    location /healthz {
        proxy_pass http://n8n:5678/healthz;
        access_log off;
    }
}
"""

        filename = "nginx.conf"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(nginx_config)

        print(f"\n✓ Nginx 配置已生成")
        print(f"  文件: {filename}")
        print(f"\n  使用前:")
        print(f"  1. 修改 server_name 為你的域名")
        print(f"  2. 配置 SSL 證書（Let's Encrypt 推薦）")
        print(f"  3. 測試配置: nginx -t")

        return nginx_config

    def generate_backup_script(self) -> str:
        """
        示例 4: 生成備份腳本

        返回:
            備份腳本內容
        """
        print("\n" + "="*60)
        print("示例 4: 生成備份腳本")
        print("="*60)

        backup_script = """#!/bin/bash
# n8n 備份腳本

set -e

# 配置
BACKUP_DIR="/backup/n8n"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# 創建備份目錄
mkdir -p $BACKUP_DIR

echo "開始備份 n8n..."

# 1. 備份 PostgreSQL 數據庫
echo "備份數據庫..."
docker exec n8n-postgres pg_dump -U n8n n8n | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# 2. 備份 n8n 數據目錄
echo "備份數據文件..."
docker run --rm -v n8n_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/data_$DATE.tar.gz -C /data .

# 3. 備份工作流（通過 API）
echo "備份工作流..."
curl -X GET http://localhost:5678/api/v1/workflows \\
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \\
  | gzip > $BACKUP_DIR/workflows_$DATE.json.gz

# 4. 創建備份清單
echo "創建備份清單..."
cat > $BACKUP_DIR/backup_$DATE.txt <<EOF
備份時間: $(date)
數據庫備份: db_$DATE.sql.gz
數據文件備份: data_$DATE.tar.gz
工作流備份: workflows_$DATE.json.gz
EOF

# 5. 清理舊備份
echo "清理舊備份..."
find $BACKUP_DIR -name "*.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.txt" -mtime +$RETENTION_DAYS -delete

echo "備份完成！"
echo "備份位置: $BACKUP_DIR"

# 6. 上傳到遠程存儲（可選）
# aws s3 sync $BACKUP_DIR s3://your-backup-bucket/n8n/
# rclone sync $BACKUP_DIR remote:n8n-backups

# 7. 發送通知（可選）
# curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL \\
#   -d "{\\"text\\": \\"n8n 備份成功: $DATE\\"}"
"""

        filename = "backup.sh"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(backup_script)

        # 設置執行權限
        os.chmod(filename, 0o755)

        print(f"\n✓ 備份腳本已生成")
        print(f"  文件: {filename}")
        print(f"\n  使用方法:")
        print(f"  1. 設置環境變量 N8N_API_KEY")
        print(f"  2. 手動運行: ./{filename}")
        print(f"  3. 設置 Cron 定時任務:")
        print(f"     0 2 * * * /path/to/{filename}")

        return backup_script

    def generate_monitoring_config(self) -> str:
        """
        示例 5: 生成監控配置

        返回:
            監控配置內容
        """
        print("\n" + "="*60)
        print("示例 5: 生成監控配置")
        print("="*60)

        monitoring_script = """#!/usr/bin/env python3
\"\"\"
n8n 監控腳本
\"\"\"

import requests
import time
import os
from datetime import datetime

class N8NMonitor:
    def __init__(self):
        self.base_url = os.getenv('N8N_URL', 'http://localhost:5678')
        self.api_key = os.getenv('N8N_API_KEY')
        self.webhook_url = os.getenv('ALERT_WEBHOOK_URL')  # Slack/Discord

    def check_health(self):
        \"\"\"檢查 n8n 健康狀態\"\"\"
        try:
            response = requests.get(f'{self.base_url}/healthz', timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"健康檢查失敗: {e}")
            return False

    def get_failed_executions(self):
        \"\"\"獲取失敗的執行\"\"\"
        try:
            headers = {'X-N8N-API-KEY': self.api_key}
            response = requests.get(
                f'{self.base_url}/api/v1/executions',
                headers=headers,
                params={'status': 'error', 'limit': 10}
            )
            return response.json()
        except Exception as e:
            print(f"獲取執行失敗: {e}")
            return []

    def send_alert(self, message):
        \"\"\"發送告警\"\"\"
        if not self.webhook_url:
            print(f"告警: {message}")
            return

        try:
            requests.post(self.webhook_url, json={
                'text': f'🚨 n8n 告警\\n{message}',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"發送告警失敗: {e}")

    def monitor(self):
        \"\"\"執行監控\"\"\"
        print(f"[{datetime.now()}] 開始監控...")

        # 1. 健康檢查
        if not self.check_health():
            self.send_alert('n8n 服務不可用！')
            return

        # 2. 檢查失敗的執行
        failed = self.get_failed_executions()
        if failed and len(failed) > 5:
            self.send_alert(f'發現 {len(failed)} 個失敗的執行')

        print("監控完成")

if __name__ == '__main__':
    monitor = N8NMonitor()

    # 持續監控
    while True:
        monitor.monitor()
        time.sleep(300)  # 每 5 分鐘檢查一次
"""

        filename = "monitor.py"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(monitoring_script)

        os.chmod(filename, 0o755)

        print(f"\n✓ 監控腳本已生成")
        print(f"  文件: {filename}")
        print(f"\n  使用方法:")
        print(f"  1. 設置環境變量:")
        print(f"     export N8N_URL=http://localhost:5678")
        print(f"     export N8N_API_KEY=your-api-key")
        print(f"     export ALERT_WEBHOOK_URL=your-webhook")
        print(f"  2. 運行: python3 {filename}")

        return monitoring_script


def main():
    """
    主函數：生成所有部署配置
    """
    print("\n" + "="*60)
    print("n8n 生產部署配置生成")
    print("="*60)

    deployer = N8NProductionDeployment()

    # 生成所有配置文件
    deployer.generate_docker_compose()
    deployer.generate_env_template()
    deployer.generate_nginx_config()
    deployer.generate_backup_script()
    deployer.generate_monitoring_config()

    print("\n" + "="*60)
    print("所有部署配置已生成！")
    print("="*60)

    print("\n部署步驟:")
    print("1. 檢查並修改生成的配置文件")
    print("2. 創建 .env 文件並設置環境變量")
    print("3. 配置 SSL 證書（Let's Encrypt）")
    print("4. 運行: docker-compose -f docker-compose.production.yml up -d")
    print("5. 設置備份定時任務")
    print("6. 配置監控和告警")
    print("7. 測試工作流")


if __name__ == "__main__":
    main()

    print("\n" + "-"*60)
    print("生產部署最佳實踐:")
    print("-"*60)
    print("""
    1. 安全性
       - 使用 HTTPS
       - 啟用認證
       - 強密碼
       - 定期更新
       - 防火牆配置

    2. 高可用性
       - 負載均衡
       - 數據庫主從
       - 自動重啟
       - 健康檢查
       - 故障轉移

    3. 性能優化
       - 使用 PostgreSQL
       - Redis 緩存
       - 增加資源
       - 調優參數
       - CDN 加速

    4. 備份策略
       - 每日自動備份
       - 異地備份
       - 定期測試恢復
       - 版本控制
       - 保留策略

    5. 監控告警
       - 系統監控
       - 應用監控
       - 日誌聚合
       - 告警通知
       - 性能分析

    6. 維護計劃
       - 定期更新
       - 性能審計
       - 安全掃描
       - 容量規劃
       - 災難恢復演練

    推薦工具:
    - 容器編排: Docker Compose, Kubernetes
    - 反向代理: Nginx, Traefik
    - SSL 證書: Let's Encrypt, Certbot
    - 監控: Prometheus, Grafana
    - 日誌: ELK Stack, Loki
    - 備份: Restic, Duplicati
    """)
