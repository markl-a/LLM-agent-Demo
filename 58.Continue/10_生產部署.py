"""
Continue AI 編程助手 - 生產部署

這個文件展示了如何將 Continue 部署到生產環境。
包括服務器部署、Docker 容器化、監控、安全配置等。

主要內容:
1. 部署架構設計
2. Docker 容器化
3. 配置管理
4. 安全加固
5. 性能優化
6. 監控和日誌
7. 備份和恢復
8. 負載均衡

Author: Continue Team
Date: 2025
"""

import os
import json
import yaml
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import hashlib
import secrets


# =====================================================
# 第一部分: 部署配置定義
# =====================================================

@dataclass
class DeploymentConfig:
    """
    部署配置
    """
    environment: str  # 環境(development/staging/production)
    host: str  # 主機地址
    port: int  # 端口
    workers: int  # 工作進程數
    enable_ssl: bool = True  # 是否啟用 SSL
    ssl_cert_path: Optional[str] = None  # SSL 證書路徑
    ssl_key_path: Optional[str] = None  # SSL 密鑰路徑
    log_level: str = "INFO"  # 日誌級別
    max_request_size: int = 10 * 1024 * 1024  # 最大請求大小(10MB)
    timeout: int = 300  # 超時時間(秒)
    cors_origins: List[str] = field(default_factory=list)  # CORS 允許的源

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "environment": self.environment,
            "host": self.host,
            "port": self.port,
            "workers": self.workers,
            "enable_ssl": self.enable_ssl,
            "ssl_cert_path": self.ssl_cert_path,
            "ssl_key_path": self.ssl_key_path,
            "log_level": self.log_level,
            "max_request_size": self.max_request_size,
            "timeout": self.timeout,
            "cors_origins": self.cors_origins
        }


@dataclass
class SecurityConfig:
    """
    安全配置
    """
    api_key_enabled: bool = True  # 是否啟用 API 密鑰
    api_keys: List[str] = field(default_factory=list)  # API 密鑰列表
    rate_limit_enabled: bool = True  # 是否啟用速率限制
    rate_limit_requests: int = 100  # 每分鐘最大請求數
    ip_whitelist: List[str] = field(default_factory=list)  # IP 白名單
    encryption_key: Optional[str] = None  # 加密密鑰

    def generate_api_key(self) -> str:
        """
        生成 API 密鑰

        Returns:
            API 密鑰
        """
        api_key = secrets.token_urlsafe(32)
        self.api_keys.append(api_key)
        return api_key

    def validate_api_key(self, api_key: str) -> bool:
        """
        驗證 API 密鑰

        Args:
            api_key: API 密鑰

        Returns:
            是否有效
        """
        return api_key in self.api_keys


# =====================================================
# 第二部分: Docker 配置生成
# =====================================================

class DockerConfigGenerator:
    """
    Docker 配置生成器

    生成 Dockerfile 和 docker-compose.yml
    """

    @staticmethod
    def generate_dockerfile(
        python_version: str = "3.11",
        base_image: str = "python"
    ) -> str:
        """
        生成 Dockerfile

        Args:
            python_version: Python 版本
            base_image: 基礎鏡像

        Returns:
            Dockerfile 內容
        """
        dockerfile = f"""# Continue AI 助手 - 生產環境 Dockerfile
FROM {base_image}:{python_version}-slim

# 設置工作目錄
WORKDIR /app

# 設置環境變量
ENV PYTHONUNBUFFERED=1 \\
    PYTHONDONTWRITEBYTECODE=1 \\
    PIP_NO_CACHE_DIR=1 \\
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安裝系統依賴
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    git \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# 複製依賴文件
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --upgrade pip && \\
    pip install -r requirements.txt

# 複製應用代碼
COPY . .

# 創建非 root 用戶
RUN useradd -m -u 1000 continue && \\
    chown -R continue:continue /app

# 切換到非 root 用戶
USER continue

# 暴露端口
EXPOSE 8000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# 啟動命令
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
"""
        return dockerfile

    @staticmethod
    def generate_docker_compose(
        service_name: str = "continue-ai",
        port: int = 8000
    ) -> str:
        """
        生成 docker-compose.yml

        Args:
            service_name: 服務名稱
            port: 端口

        Returns:
            docker-compose.yml 內容
        """
        compose = f"""version: '3.8'

services:
  {service_name}:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: {service_name}
    ports:
      - "{port}:{port}"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      - OPENAI_API_KEY=${{OPENAI_API_KEY}}
      - ANTHROPIC_API_KEY=${{ANTHROPIC_API_KEY}}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config:ro
    restart: unless-stopped
    networks:
      - continue-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:{port}/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Redis 緩存(可選)
  redis:
    image: redis:7-alpine
    container_name: {service_name}-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped
    networks:
      - continue-network

  # Nginx 反向代理(可選)
  nginx:
    image: nginx:alpine
    container_name: {service_name}-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - {service_name}
    restart: unless-stopped
    networks:
      - continue-network

networks:
  continue-network:
    driver: bridge

volumes:
  redis-data:
"""
        return compose

    @staticmethod
    def generate_dockerignore() -> str:
        """
        生成 .dockerignore

        Returns:
            .dockerignore 內容
        """
        return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Git
.git/
.gitignore

# Docker
Dockerfile
docker-compose.yml
.dockerignore

# Logs
logs/
*.log

# Environment
.env
.env.local
.env.production

# Data
data/
tmp/
"""


# =====================================================
# 第三部分: Nginx 配置生成
# =====================================================

class NginxConfigGenerator:
    """
    Nginx 配置生成器
    """

    @staticmethod
    def generate_nginx_config(
        server_name: str = "continue.example.com",
        backend_port: int = 8000
    ) -> str:
        """
        生成 Nginx 配置

        Args:
            server_name: 服務器域名
            backend_port: 後端端口

        Returns:
            Nginx 配置內容
        """
        config = f"""# Continue AI 助手 - Nginx 配置

# 上游服務器
upstream continue_backend {{
    least_conn;
    server continue-ai:{backend_port} max_fails=3 fail_timeout=30s;
}}

# HTTP 重定向到 HTTPS
server {{
    listen 80;
    server_name {server_name};

    location / {{
        return 301 https://$server_name$request_uri;
    }}
}}

# HTTPS 服務器
server {{
    listen 443 ssl http2;
    server_name {server_name};

    # SSL 證書
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # SSL 配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 安全頭
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # 日誌
    access_log /var/log/nginx/continue_access.log;
    error_log /var/log/nginx/continue_error.log;

    # 客戶端請求大小限制
    client_max_body_size 10M;

    # 反向代理配置
    location / {{
        proxy_pass http://continue_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超時設置
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }}

    # 健康檢查端點
    location /health {{
        proxy_pass http://continue_backend/health;
        access_log off;
    }}

    # 靜態文件
    location /static {{
        alias /app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }}
}}
"""
        return config


# =====================================================
# 第四部分: 監控配置
# =====================================================

@dataclass
class MonitoringConfig:
    """
    監控配置
    """
    enable_prometheus: bool = True  # 啟用 Prometheus
    prometheus_port: int = 9090  # Prometheus 端口
    enable_grafana: bool = True  # 啟用 Grafana
    grafana_port: int = 3000  # Grafana 端口
    alert_email: Optional[str] = None  # 告警郵箱
    alert_webhook: Optional[str] = None  # 告警 Webhook


class PrometheusConfigGenerator:
    """
    Prometheus 配置生成器
    """

    @staticmethod
    def generate_prometheus_config() -> str:
        """
        生成 Prometheus 配置

        Returns:
            prometheus.yml 內容
        """
        config = """# Prometheus 配置
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'continue-ai'
    replica: 'main'

# 告警規則
rule_files:
  - 'alerts.yml'

# 抓取配置
scrape_configs:
  # Continue AI 服務
  - job_name: 'continue-ai'
    static_configs:
      - targets: ['continue-ai:8000']
    metrics_path: '/metrics'

  # Node Exporter
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']

  # Redis
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
"""
        return config

    @staticmethod
    def generate_alert_rules() -> str:
        """
        生成告警規則

        Returns:
            alerts.yml 內容
        """
        rules = """groups:
  - name: continue_alerts
    interval: 30s
    rules:
      # 服務可用性告警
      - alert: ServiceDown
        expr: up{job="continue-ai"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Continue AI 服務不可用"
          description: "服務已停止超過 1 分鐘"

      # 高錯誤率告警
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "錯誤率過高"
          description: "5xx 錯誤率超過 5%"

      # 高響應時間告警
      - alert: HighResponseTime
        expr: http_request_duration_seconds{quantile="0.95"} > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "響應時間過長"
          description: "95% 響應時間超過 2 秒"

      # 高內存使用告警
      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes / 1024 / 1024 / 1024 > 4
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "內存使用過高"
          description: "內存使用超過 4GB"

      # CPU 使用率告警
      - alert: HighCPUUsage
        expr: rate(process_cpu_seconds_total[5m]) > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "CPU 使用率過高"
          description: "CPU 使用率超過 80%"
"""
        return rules


# =====================================================
# 第五部分: 日誌配置
# =====================================================

class LoggingConfig:
    """
    日誌配置
    """

    @staticmethod
    def generate_logging_config() -> Dict[str, Any]:
        """
        生成日誌配置

        Returns:
            日誌配置字典
        """
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                },
                "json": {
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "INFO",
                    "formatter": "default",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "INFO",
                    "formatter": "json",
                    "filename": "/app/logs/app.log",
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5
                },
                "error_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "ERROR",
                    "formatter": "json",
                    "filename": "/app/logs/error.log",
                    "maxBytes": 10485760,
                    "backupCount": 5
                }
            },
            "root": {
                "level": "INFO",
                "handlers": ["console", "file", "error_file"]
            }
        }


# =====================================================
# 第六部分: 部署管理器
# =====================================================

class DeploymentManager:
    """
    部署管理器

    管理整個部署過程
    """

    def __init__(self, output_dir: str = "./deployment"):
        """
        初始化

        Args:
            output_dir: 輸出目錄
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all_configs(
        self,
        environment: str = "production",
        server_name: str = "continue.example.com"
    ):
        """
        生成所有配置文件

        Args:
            environment: 環境
            server_name: 服務器域名
        """
        print("=" * 60)
        print("生成部署配置文件")
        print("=" * 60)

        # 創建目錄結構
        (self.output_dir / "docker").mkdir(exist_ok=True)
        (self.output_dir / "nginx").mkdir(exist_ok=True)
        (self.output_dir / "monitoring").mkdir(exist_ok=True)
        (self.output_dir / "config").mkdir(exist_ok=True)

        # 生成 Docker 配置
        print("\n生成 Docker 配置...")
        self._save_file(
            "Dockerfile",
            DockerConfigGenerator.generate_dockerfile()
        )
        self._save_file(
            "docker-compose.yml",
            DockerConfigGenerator.generate_docker_compose()
        )
        self._save_file(
            ".dockerignore",
            DockerConfigGenerator.generate_dockerignore()
        )

        # 生成 Nginx 配置
        print("生成 Nginx 配置...")
        self._save_file(
            "nginx/nginx.conf",
            NginxConfigGenerator.generate_nginx_config(server_name)
        )

        # 生成監控配置
        print("生成監控配置...")
        self._save_file(
            "monitoring/prometheus.yml",
            PrometheusConfigGenerator.generate_prometheus_config()
        )
        self._save_file(
            "monitoring/alerts.yml",
            PrometheusConfigGenerator.generate_alert_rules()
        )

        # 生成日誌配置
        print("生成日誌配置...")
        self._save_file(
            "config/logging.json",
            json.dumps(LoggingConfig.generate_logging_config(), indent=2)
        )

        # 生成部署配置
        print("生成部署配置...")
        deploy_config = DeploymentConfig(
            environment=environment,
            host="0.0.0.0",
            port=8000,
            workers=4
        )
        self._save_file(
            "config/deployment.json",
            json.dumps(deploy_config.to_dict(), indent=2)
        )

        # 生成安全配置模板
        print("生成安全配置...")
        security_config = SecurityConfig()
        api_key = security_config.generate_api_key()
        self._save_file(
            "config/security.json",
            json.dumps({
                "api_key_enabled": True,
                "rate_limit_enabled": True,
                "rate_limit_requests": 100,
                "sample_api_key": api_key
            }, indent=2)
        )

        # 生成環境變量模板
        print("生成環境變量模板...")
        env_template = """# Continue AI 環境變量配置

# 環境
ENVIRONMENT=production

# API 密鑰
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# 服務配置
HOST=0.0.0.0
PORT=8000
WORKERS=4

# 安全
API_KEY={api_key}
ENCRYPTION_KEY=your-encryption-key

# 日誌
LOG_LEVEL=INFO

# Redis(可選)
REDIS_URL=redis://redis:6379/0

# 監控
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
""".format(api_key=api_key)

        self._save_file(".env.example", env_template)

        # 生成部署腳本
        print("生成部署腳本...")
        self._generate_deploy_script()

        print("\n" + "=" * 60)
        print("配置文件生成完成!")
        print(f"輸出目錄: {self.output_dir.absolute()}")
        print("=" * 60)

    def _save_file(self, filename: str, content: str):
        """
        保存文件

        Args:
            filename: 文件名
            content: 內容
        """
        filepath = self.output_dir / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  ✓ {filename}")

    def _generate_deploy_script(self):
        """生成部署腳本"""
        script = """#!/bin/bash
# Continue AI 部署腳本

set -e

echo "================================"
echo "Continue AI 部署腳本"
echo "================================"

# 檢查 Docker
if ! command -v docker &> /dev/null; then
    echo "錯誤: 未安裝 Docker"
    exit 1
fi

# 檢查 docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "錯誤: 未安裝 docker-compose"
    exit 1
fi

# 拉取最新代碼(可選)
# git pull origin main

# 構建鏡像
echo "構建 Docker 鏡像..."
docker-compose build

# 停止舊容器
echo "停止舊容器..."
docker-compose down

# 啟動新容器
echo "啟動新容器..."
docker-compose up -d

# 等待服務啟動
echo "等待服務啟動..."
sleep 10

# 健康檢查
echo "執行健康檢查..."
if curl -f http://localhost:8000/health; then
    echo "✓ 服務啟動成功!"
else
    echo "✗ 服務啟動失敗!"
    docker-compose logs
    exit 1
fi

echo "================================"
echo "部署完成!"
echo "================================"
"""
        self._save_file("deploy.sh", script)

        # 添加執行權限
        deploy_file = self.output_dir / "deploy.sh"
        deploy_file.chmod(0o755)


# =====================================================
# 第七部分: 使用示例
# =====================================================

def deployment_example():
    """
    部署示例
    """
    print("Continue AI - 生產部署配置生成\n")

    # 創建部署管理器
    manager = DeploymentManager(output_dir="./deployment_output")

    # 生成所有配置
    manager.generate_all_configs(
        environment="production",
        server_name="continue.example.com"
    )

    print("\n下一步:")
    print("1. 檢查生成的配置文件")
    print("2. 修改 .env.example 並重命名為 .env")
    print("3. 配置 SSL 證書")
    print("4. 運行 ./deploy.sh 開始部署")
    print("5. 設置監控和告警")


def main():
    """
    主函數
    """
    deployment_example()


if __name__ == "__main__":
    main()
