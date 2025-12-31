"""
Helicone 自託管部署
==================

本文件展示如何使用 Docker 自託管 Helicone。
自託管給您完全的控制權和數據隱私。

主要內容:
1. Docker 部署配置
2. Docker Compose 設置
3. 數據庫配置
4. 環境變量管理
5. 備份和恢復
6. 監控和日誌
7. 擴展和優化

作者: Helicone Team
日期: 2025-12-31
"""

import os
import sys
import subprocess
import time
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from dotenv import load_dotenv

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.progress import Progress, SpinnerColumn, TextColumn
    import yaml
except ImportError as e:
    print(f"❌ 缺少必要的依賴: {e}")
    print("請運行: pip install rich pyyaml")
    sys.exit(1)


class HeliconeSelfHosted:
    """
    Helicone 自託管管理器

    管理 Helicone 的自託管部署。
    """

    def __init__(self, base_dir: str = "./helicone-self-hosted"):
        """初始化自託管管理器"""
        self.console = Console()
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

        self.console.print("✅ [green]自託管管理器已初始化[/green]")
        self.console.print(f"📁 基礎目錄: {self.base_dir.absolute()}")

    def generate_docker_compose(self) -> str:
        """
        生成 Docker Compose 配置

        這個配置包括:
        - Helicone Web 服務
        - Helicone Worker
        - PostgreSQL 數據庫
        - Redis 緩存
        - ClickHouse (分析數據庫)
        """
        docker_compose = """
version: '3.8'

services:
  # PostgreSQL 數據庫 - 主要數據存儲
  postgres:
    image: postgres:15-alpine
    container_name: helicone-postgres
    environment:
      POSTGRES_DB: helicone
      POSTGRES_USER: helicone
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-helicone_password}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    networks:
      - helicone-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U helicone"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Redis - 緩存和會話存儲
  redis:
    image: redis:7-alpine
    container_name: helicone-redis
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-redis_password}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - helicone-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # ClickHouse - 分析數據庫
  clickhouse:
    image: clickhouse/clickhouse-server:latest
    container_name: helicone-clickhouse
    environment:
      CLICKHOUSE_DB: helicone_analytics
      CLICKHOUSE_USER: helicone
      CLICKHOUSE_PASSWORD: ${CLICKHOUSE_PASSWORD:-clickhouse_password}
    volumes:
      - clickhouse_data:/var/lib/clickhouse
    ports:
      - "8123:8123"  # HTTP 接口
      - "9000:9000"  # Native 接口
    networks:
      - helicone-network
    ulimits:
      nofile:
        soft: 262144
        hard: 262144
    restart: unless-stopped

  # Helicone Web - 主應用程序
  helicone-web:
    image: helicone/helicone:latest
    container_name: helicone-web
    environment:
      # 數據庫配置
      DATABASE_URL: postgresql://helicone:${POSTGRES_PASSWORD:-helicone_password}@postgres:5432/helicone

      # Redis 配置
      REDIS_URL: redis://:${REDIS_PASSWORD:-redis_password}@redis:6379

      # ClickHouse 配置
      CLICKHOUSE_HOST: clickhouse
      CLICKHOUSE_PORT: 8123
      CLICKHOUSE_USER: helicone
      CLICKHOUSE_PASSWORD: ${CLICKHOUSE_PASSWORD:-clickhouse_password}
      CLICKHOUSE_DATABASE: helicone_analytics

      # 應用配置
      NODE_ENV: production
      PORT: 3000

      # 認證
      JWT_SECRET: ${JWT_SECRET:-your-super-secret-jwt-key-change-this}

      # API Keys
      HELICONE_API_KEY: ${HELICONE_API_KEY:-your-api-key}

      # 可選: OpenAI Proxy
      OPENAI_API_KEY: ${OPENAI_API_KEY}

      # 日誌級別
      LOG_LEVEL: ${LOG_LEVEL:-info}

      # 特性開關
      ENABLE_CACHING: ${ENABLE_CACHING:-true}
      ENABLE_RATE_LIMITING: ${ENABLE_RATE_LIMITING:-true}
      ENABLE_ANALYTICS: ${ENABLE_ANALYTICS:-true}
    ports:
      - "3000:3000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - helicone-network
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  # Helicone Worker - 後台任務處理
  helicone-worker:
    image: helicone/helicone-worker:latest
    container_name: helicone-worker
    environment:
      # 繼承與 web 相同的環境變量
      DATABASE_URL: postgresql://helicone:${POSTGRES_PASSWORD:-helicone_password}@postgres:5432/helicone
      REDIS_URL: redis://:${REDIS_PASSWORD:-redis_password}@redis:6379
      CLICKHOUSE_HOST: clickhouse
      CLICKHOUSE_PORT: 8123
      CLICKHOUSE_USER: helicone
      CLICKHOUSE_PASSWORD: ${CLICKHOUSE_PASSWORD:-clickhouse_password}
      CLICKHOUSE_DATABASE: helicone_analytics
      NODE_ENV: production
      LOG_LEVEL: ${LOG_LEVEL:-info}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - helicone-network
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  # Nginx - 反向代理和負載均衡
  nginx:
    image: nginx:alpine
    container_name: helicone-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - helicone-web
    networks:
      - helicone-network
    restart: unless-stopped

networks:
  helicone-network:
    driver: bridge

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  clickhouse_data:
    driver: local
"""
        return docker_compose.strip()

    def generate_env_template(self) -> str:
        """生成環境變量模板"""
        env_template = """
# Helicone 自託管環境配置
# 複製此文件為 .env 並填入實際值

# ============================================
# 數據庫密碼
# ============================================
POSTGRES_PASSWORD=your_secure_postgres_password_here
REDIS_PASSWORD=your_secure_redis_password_here
CLICKHOUSE_PASSWORD=your_secure_clickhouse_password_here

# ============================================
# JWT 密鑰 (用於認證)
# ============================================
JWT_SECRET=your_super_secret_jwt_key_change_this_to_random_string

# ============================================
# Helicone API 密鑰
# ============================================
HELICONE_API_KEY=your_helicone_api_key_here

# ============================================
# OpenAI API 密鑰 (如果需要代理)
# ============================================
OPENAI_API_KEY=your_openai_api_key_here

# ============================================
# 應用配置
# ============================================
LOG_LEVEL=info
ENABLE_CACHING=true
ENABLE_RATE_LIMITING=true
ENABLE_ANALYTICS=true

# ============================================
# 可選: 郵件配置 (用於告警)
# ============================================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_email_password
SMTP_FROM=noreply@helicone.local

# ============================================
# 可選: Slack 集成
# ============================================
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# ============================================
# 可選: 監控配置
# ============================================
ENABLE_METRICS=true
METRICS_PORT=9090
"""
        return env_template.strip()

    def generate_nginx_config(self) -> str:
        """生成 Nginx 配置"""
        nginx_config = """
events {
    worker_connections 1024;
}

http {
    upstream helicone_backend {
        server helicone-web:3000;
    }

    # HTTP 服務器 - 重定向到 HTTPS
    server {
        listen 80;
        server_name _;

        # 健康檢查端點
        location /health {
            access_log off;
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }

        # 重定向所有其他請求到 HTTPS
        location / {
            return 301 https://$host$request_uri;
        }
    }

    # HTTPS 服務器
    server {
        listen 443 ssl http2;
        server_name _;

        # SSL 證書配置
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # SSL 安全配置
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # 日誌
        access_log /var/log/nginx/helicone_access.log;
        error_log /var/log/nginx/helicone_error.log;

        # 請求大小限制
        client_max_body_size 10M;

        # 代理設置
        location / {
            proxy_pass http://helicone_backend;
            proxy_http_version 1.1;

            # Headers
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # 超時設置
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # API 路由 - 更長的超時時間
        location /api/ {
            proxy_pass http://helicone_backend;
            proxy_http_version 1.1;

            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # 更長的超時時間用於 AI API
            proxy_connect_timeout 300s;
            proxy_send_timeout 300s;
            proxy_read_timeout 300s;
        }
    }
}
"""
        return nginx_config.strip()

    def generate_init_sql(self) -> str:
        """生成數據庫初始化 SQL"""
        init_sql = """
-- Helicone 數據庫初始化腳本

-- 創建擴展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 用戶表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tier VARCHAR(50) DEFAULT 'free',
    is_active BOOLEAN DEFAULT true
);

-- 請求記錄表
CREATE TABLE IF NOT EXISTS requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    request_id VARCHAR(255) UNIQUE NOT NULL,
    session_id VARCHAR(255),
    model VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL,
    cost_usd DECIMAL(10, 6) NOT NULL,
    latency_ms INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'success',
    error_message TEXT,

    -- 索引
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_created_at (created_at),
    INDEX idx_model (model)
);

-- 自定義屬性表
CREATE TABLE IF NOT EXISTS request_properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id UUID REFERENCES requests(id) ON DELETE CASCADE,
    property_key VARCHAR(100) NOT NULL,
    property_value TEXT NOT NULL,

    INDEX idx_request_id (request_id),
    INDEX idx_property_key (property_key)
);

-- 配額表
CREATE TABLE IF NOT EXISTS quotas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    quota_type VARCHAR(50) NOT NULL,
    limit_value INTEGER NOT NULL,
    used_value INTEGER DEFAULT 0,
    reset_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, quota_type)
);

-- 創建視圖: 每日成本匯總
CREATE OR REPLACE VIEW daily_costs AS
SELECT
    user_id,
    DATE(created_at) as date,
    COUNT(*) as request_count,
    SUM(total_tokens) as total_tokens,
    SUM(cost_usd) as total_cost_usd,
    AVG(latency_ms) as avg_latency_ms
FROM requests
WHERE status = 'success'
GROUP BY user_id, DATE(created_at);

-- 創建視圖: 模型使用統計
CREATE OR REPLACE VIEW model_usage_stats AS
SELECT
    model,
    COUNT(*) as request_count,
    SUM(total_tokens) as total_tokens,
    SUM(cost_usd) as total_cost_usd,
    AVG(latency_ms) as avg_latency_ms
FROM requests
WHERE status = 'success'
GROUP BY model;

-- 創建示例用戶
INSERT INTO users (email, username, api_key, tier)
VALUES ('admin@helicone.local', 'admin', 'sk-' || md5(random()::text), 'enterprise')
ON CONFLICT (email) DO NOTHING;

COMMIT;
"""
        return init_sql.strip()

    def setup_project(self):
        """
        設置完整的項目結構

        創建所有必要的配置文件和目錄。
        """
        self.console.print("\n[bold cyan]🚀 設置 Helicone 自託管項目[/bold cyan]")
        self.console.print("=" * 80)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            # 任務 1: 創建目錄結構
            task = progress.add_task("創建目錄結構...", total=None)

            directories = [
                "logs",
                "ssl",
                "init-scripts",
                "backups"
            ]

            for dir_name in directories:
                dir_path = self.base_dir / dir_name
                dir_path.mkdir(exist_ok=True)

            progress.update(task, completed=True)

            # 任務 2: 生成 docker-compose.yml
            task = progress.add_task("生成 docker-compose.yml...", total=None)

            compose_file = self.base_dir / "docker-compose.yml"
            compose_file.write_text(self.generate_docker_compose())

            progress.update(task, completed=True)

            # 任務 3: 生成 .env 模板
            task = progress.add_task("生成 .env.template...", total=None)

            env_template_file = self.base_dir / ".env.template"
            env_template_file.write_text(self.generate_env_template())

            progress.update(task, completed=True)

            # 任務 4: 生成 nginx.conf
            task = progress.add_task("生成 nginx.conf...", total=None)

            nginx_file = self.base_dir / "nginx.conf"
            nginx_file.write_text(self.generate_nginx_config())

            progress.update(task, completed=True)

            # 任務 5: 生成初始化 SQL
            task = progress.add_task("生成數據庫初始化腳本...", total=None)

            init_sql_file = self.base_dir / "init-scripts" / "01_init.sql"
            init_sql_file.write_text(self.generate_init_sql())

            progress.update(task, completed=True)

            # 任務 6: 創建 README
            task = progress.add_task("生成 README.md...", total=None)

            readme_content = self.generate_readme()
            readme_file = self.base_dir / "README.md"
            readme_file.write_text(readme_content)

            progress.update(task, completed=True)

        self.console.print("\n✅ [green]項目設置完成![/green]")
        self.display_project_structure()
        self.display_next_steps()

    def generate_readme(self) -> str:
        """生成 README 文檔"""
        readme = """
# Helicone 自託管部署

這是 Helicone 的自託管部署配置。

## 目錄結構

```
helicone-self-hosted/
├── docker-compose.yml      # Docker Compose 配置
├── .env                    # 環境變量 (需要創建)
├── .env.template          # 環境變量模板
├── nginx.conf             # Nginx 配置
├── init-scripts/          # 數據庫初始化腳本
│   └── 01_init.sql
├── logs/                  # 應用日誌
├── ssl/                   # SSL 證書
│   ├── cert.pem          # (需要創建)
│   └── key.pem           # (需要創建)
└── backups/              # 數據庫備份
```

## 快速開始

### 1. 配置環境變量

```bash
cp .env.template .env
# 編輯 .env 文件,填入實際的密碼和 API 密鑰
vi .env
```

### 2. 生成 SSL 證書 (自簽名,僅用於測試)

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \\
  -keyout ssl/key.pem -out ssl/cert.pem \\
  -subj "/C=TW/ST=Taiwan/L=Taipei/O=Helicone/CN=localhost"
```

### 3. 啟動服務

```bash
docker-compose up -d
```

### 4. 檢查服務狀態

```bash
docker-compose ps
```

### 5. 查看日誌

```bash
# 查看所有服務日誌
docker-compose logs -f

# 查看特定服務日誌
docker-compose logs -f helicone-web
```

### 6. 訪問服務

- Web 界面: https://localhost
- API 端點: https://localhost/api
- 健康檢查: http://localhost/health

## 管理命令

### 停止服務

```bash
docker-compose stop
```

### 重啟服務

```bash
docker-compose restart
```

### 完全刪除 (包括數據)

```bash
docker-compose down -v
```

### 數據庫備份

```bash
docker-compose exec postgres pg_dump -U helicone helicone > backups/backup_$(date +%Y%m%d_%H%M%S).sql
```

### 數據庫恢復

```bash
docker-compose exec -T postgres psql -U helicone helicone < backups/your_backup.sql
```

## 監控

### 查看資源使用

```bash
docker stats
```

### 查看 PostgreSQL 連接

```bash
docker-compose exec postgres psql -U helicone -c "SELECT count(*) FROM pg_stat_activity;"
```

### 查看 Redis 信息

```bash
docker-compose exec redis redis-cli -a redis_password INFO
```

## 擴展

### 水平擴展 Web 服務

```bash
docker-compose up -d --scale helicone-web=3
```

### 水平擴展 Worker 服務

```bash
docker-compose up -d --scale helicone-worker=5
```

## 故障排除

### 重置數據庫

```bash
docker-compose down
docker volume rm helicone-self-hosted_postgres_data
docker-compose up -d
```

### 查看容器日誌

```bash
docker-compose logs --tail=100 helicone-web
```

### 進入容器調試

```bash
docker-compose exec helicone-web sh
```

## 安全建議

1. **修改所有默認密碼** - 在 .env 文件中設置強密碼
2. **使用正式 SSL 證書** - 生產環境使用 Let's Encrypt 或其他 CA
3. **限制端口暴露** - 只暴露必要的端口
4. **啟用防火牆** - 配置 ufw 或 iptables
5. **定期備份** - 設置自動備份計劃
6. **更新鏡像** - 定期更新 Docker 鏡像

## 性能優化

1. **數據庫優化** - 調整 PostgreSQL 配置
2. **Redis 持久化** - 根據需求調整 RDB/AOF
3. **Nginx 緩存** - 啟用靜態資源緩存
4. **資源限制** - 在 docker-compose.yml 中設置資源限制

## 支持

如有問題,請查閱:
- 官方文檔: https://docs.helicone.ai
- GitHub: https://github.com/Helicone/helicone
- Discord: https://discord.gg/helicone
"""
        return readme.strip()

    def display_project_structure(self):
        """顯示項目結構"""
        self.console.print("\n[bold cyan]📂 項目結構[/bold cyan]")

        tree = Tree(
            f"[bold blue]{self.base_dir.name}/[/bold blue]",
            guide_style="cyan"
        )

        # 文件
        tree.add("[green]docker-compose.yml[/green] - Docker Compose 配置")
        tree.add("[yellow].env.template[/yellow] - 環境變量模板")
        tree.add("[green]nginx.conf[/green] - Nginx 配置")
        tree.add("[cyan]README.md[/cyan] - 部署文檔")

        # 目錄
        init_scripts = tree.add("[bold blue]init-scripts/[/bold blue] - 初始化腳本")
        init_scripts.add("[green]01_init.sql[/green]")

        tree.add("[bold blue]logs/[/bold blue] - 應用日誌")
        tree.add("[bold blue]ssl/[/bold blue] - SSL 證書")
        tree.add("[bold blue]backups/[/bold blue] - 數據庫備份")

        self.console.print(tree)

    def display_next_steps(self):
        """顯示後續步驟"""
        next_steps = """
[bold cyan]📋 後續步驟:[/bold cyan]

1️⃣  複製環境變量模板
   [green]cd {base_dir}[/green]
   [green]cp .env.template .env[/green]

2️⃣  編輯 .env 文件,設置密碼和 API 密鑰
   [green]vi .env[/green]

3️⃣  生成 SSL 證書 (測試用,自簽名)
   [green]openssl req -x509 -nodes -days 365 -newkey rsa:2048 \\[/green]
   [green]  -keyout ssl/key.pem -out ssl/cert.pem \\[/green]
   [green]  -subj "/C=TW/ST=Taiwan/L=Taipei/O=Helicone/CN=localhost"[/green]

4️⃣  啟動服務
   [green]docker-compose up -d[/green]

5️⃣  檢查服務狀態
   [green]docker-compose ps[/green]

6️⃣  訪問服務
   [cyan]https://localhost[/cyan]

[yellow]⚠️  注意事項:[/yellow]
- 生產環境請使用正式的 SSL 證書
- 確保修改所有默認密碼
- 定期備份數據庫
        """.format(base_dir=self.base_dir.absolute())

        panel = Panel(
            next_steps.strip(),
            title="🚀 開始部署",
            border_style="green"
        )

        self.console.print(panel)

    def generate_backup_script(self) -> str:
        """生成備份腳本"""
        script = """#!/bin/bash
# Helicone 自動備份腳本

# 配置
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# 創建備份目錄
mkdir -p $BACKUP_DIR

# 備份 PostgreSQL
echo "備份 PostgreSQL..."
docker-compose exec -T postgres pg_dump -U helicone helicone > "$BACKUP_DIR/postgres_$TIMESTAMP.sql"
gzip "$BACKUP_DIR/postgres_$TIMESTAMP.sql"

# 備份 Redis
echo "備份 Redis..."
docker-compose exec redis redis-cli -a $(grep REDIS_PASSWORD .env | cut -d= -f2) SAVE
docker cp helicone-redis:/data/dump.rdb "$BACKUP_DIR/redis_$TIMESTAMP.rdb"
gzip "$BACKUP_DIR/redis_$TIMESTAMP.rdb"

# 刪除舊備份
echo "清理舊備份..."
find $BACKUP_DIR -name "*.gz" -mtime +$RETENTION_DAYS -delete

echo "備份完成: $TIMESTAMP"
"""
        return script.strip()


def main():
    """主函數"""
    console = Console()
    console.print("[bold green]🎯 Helicone 自託管部署工具[/bold green]\n")

    try:
        # 創建自託管管理器
        manager = HeliconeSelfHosted()

        # 設置項目
        manager.setup_project()

        # 生成備份腳本
        backup_script_path = manager.base_dir / "backup.sh"
        backup_script_path.write_text(manager.generate_backup_script())
        backup_script_path.chmod(0o755)

        console.print(f"\n✅ [green]備份腳本已創建: {backup_script_path}[/green]")

        console.print("\n✨ [bold green]部署配置已完成![/bold green]")
        console.print("📖 請查閱 README.md 了解詳細的部署步驟")

    except Exception as e:
        console.print(f"\n❌ [red]錯誤: {str(e)}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
