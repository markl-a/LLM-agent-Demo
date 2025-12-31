"""
SuperAGI 生產部署示例

這個示例展示了如何:
1. Docker 容器化部署
2. Kubernetes 集群部署
3. 監控和告警配置
4. 日誌管理
5. 高可用性配置
6. 性能優化
7. 安全加固
8. 備份和恢復

將 SuperAGI 部署到生產環境的完整指南。
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass


# ==================== Docker 配置 ====================

class DockerConfig:
    """Docker 配置生成器"""

    @staticmethod
    def generate_dockerfile() -> str:
        """生成 Dockerfile"""
        dockerfile = """# SuperAGI Production Dockerfile
FROM python:3.10-slim

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \\
    build-essential \\
    git \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# 複製依賴文件
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY . .

# 創建非 root 用戶
RUN useradd -m -u 1000 superagi && \\
    chown -R superagi:superagi /app

USER superagi

# 暴露端口
EXPOSE 8000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# 啟動命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        return dockerfile

    @staticmethod
    def generate_docker_compose() -> str:
        """生成 docker-compose.yml"""
        compose = """version: '3.8'

services:
  superagi:
    build: .
    container_name: superagi-app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/superagi
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ENV=production
    depends_on:
      - db
      - redis
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - superagi-network

  db:
    image: postgres:14
    container_name: superagi-db
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=superagi
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - superagi-network

  redis:
    image: redis:7-alpine
    container_name: superagi-redis
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - superagi-network

  nginx:
    image: nginx:alpine
    container_name: superagi-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - superagi
    restart: unless-stopped
    networks:
      - superagi-network

volumes:
  postgres_data:
  redis_data:

networks:
  superagi-network:
    driver: bridge
"""
        return compose

    @staticmethod
    def generate_nginx_config() -> str:
        """生成 Nginx 配置"""
        config = """upstream superagi {
    server superagi:8000;
}

server {
    listen 80;
    server_name yourdomain.com;

    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL 配置
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # 安全頭
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # 日誌
    access_log /var/log/nginx/superagi-access.log;
    error_log /var/log/nginx/superagi-error.log;

    # 代理設置
    location / {
        proxy_pass http://superagi;
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
    location /static {
        alias /app/static;
        expires 30d;
    }
}
"""
        return config


# ==================== Kubernetes 配置 ====================

class KubernetesConfig:
    """Kubernetes 配置生成器"""

    @staticmethod
    def generate_deployment() -> str:
        """生成 Deployment 配置"""
        deployment = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: superagi
  labels:
    app: superagi
spec:
  replicas: 3
  selector:
    matchLabels:
      app: superagi
  template:
    metadata:
      labels:
        app: superagi
    spec:
      containers:
      - name: superagi
        image: superagi:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: superagi-secrets
              key: database-url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: superagi-secrets
              key: openai-key
        - name: REDIS_URL
          value: "redis://redis:6379"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        volumeMounts:
        - name: data
          mountPath: /app/data
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: superagi-data-pvc
      - name: logs
        persistentVolumeClaim:
          claimName: superagi-logs-pvc
"""
        return deployment

    @staticmethod
    def generate_service() -> str:
        """生成 Service 配置"""
        service = """apiVersion: v1
kind: Service
metadata:
  name: superagi-service
spec:
  selector:
    app: superagi
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
"""
        return service

    @staticmethod
    def generate_hpa() -> str:
        """生成 HorizontalPodAutoscaler 配置"""
        hpa = """apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: superagi-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: superagi
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
"""
        return hpa

    @staticmethod
    def generate_ingress() -> str:
        """生成 Ingress 配置"""
        ingress = """apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: superagi-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - superagi.yourdomain.com
    secretName: superagi-tls
  rules:
  - host: superagi.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: superagi-service
            port:
              number: 80
"""
        return ingress


# ==================== 監控配置 ====================

class MonitoringConfig:
    """監控配置生成器"""

    @staticmethod
    def generate_prometheus_config() -> str:
        """生成 Prometheus 配置"""
        config = """global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'superagi'
    static_configs:
      - targets: ['superagi:8000']
    metrics_path: /metrics

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - /etc/prometheus/rules/*.yml
"""
        return config

    @staticmethod
    def generate_alert_rules() -> str:
        """生成告警規則"""
        rules = """groups:
  - name: superagi_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} for {{ $labels.instance }}"

      - alert: HighMemoryUsage
        expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value }}% for {{ $labels.container }}"

      - alert: HighCPUUsage
        expr: rate(container_cpu_usage_seconds_total[5m]) > 0.8
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is {{ $value }}% for {{ $labels.container }}"

      - alert: DatabaseConnectionPoolExhausted
        expr: pg_stat_database_numbackends / pg_settings_max_connections > 0.9
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Database connection pool nearly exhausted"

      - alert: APIRateLimitApproaching
        expr: rate(api_requests_total[1m]) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "API rate limit approaching"
"""
        return rules

    @staticmethod
    def generate_grafana_dashboard() -> Dict:
        """生成 Grafana 儀表板配置"""
        dashboard = {
            "dashboard": {
                "title": "SuperAGI Monitoring",
                "panels": [
                    {
                        "title": "Request Rate",
                        "targets": [
                            {
                                "expr": "rate(http_requests_total[5m])"
                            }
                        ]
                    },
                    {
                        "title": "Error Rate",
                        "targets": [
                            {
                                "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
                            }
                        ]
                    },
                    {
                        "title": "Response Time",
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
                            }
                        ]
                    },
                    {
                        "title": "Active Agents",
                        "targets": [
                            {
                                "expr": "agent_active_total"
                            }
                        ]
                    }
                ]
            }
        }
        return dashboard


# ==================== 日誌配置 ====================

class LoggingConfig:
    """日誌配置生成器"""

    @staticmethod
    def generate_logging_config() -> Dict:
        """生成日誌配置"""
        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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
                    "level": "DEBUG",
                    "formatter": "json",
                    "filename": "/app/logs/superagi.log",
                    "maxBytes": 10485760,
                    "backupCount": 10
                },
                "error_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "ERROR",
                    "formatter": "json",
                    "filename": "/app/logs/error.log",
                    "maxBytes": 10485760,
                    "backupCount": 10
                }
            },
            "loggers": {
                "superagi": {
                    "level": "DEBUG",
                    "handlers": ["console", "file", "error_file"],
                    "propagate": False
                }
            },
            "root": {
                "level": "INFO",
                "handlers": ["console", "file"]
            }
        }
        return config

    @staticmethod
    def generate_fluentd_config() -> str:
        """生成 Fluentd 配置"""
        config = """<source>
  @type tail
  path /app/logs/*.log
  pos_file /var/log/fluentd/superagi.pos
  tag superagi.*
  <parse>
    @type json
    time_key timestamp
    time_format %Y-%m-%dT%H:%M:%S.%L%z
  </parse>
</source>

<filter superagi.**>
  @type record_transformer
  <record>
    hostname "#{Socket.gethostname}"
    service "superagi"
  </record>
</filter>

<match superagi.**>
  @type elasticsearch
  host elasticsearch
  port 9200
  logstash_format true
  logstash_prefix superagi
  <buffer>
    @type file
    path /var/log/fluentd/buffer
    flush_interval 10s
  </buffer>
</match>
"""
        return config


# ==================== 安全配置 ====================

class SecurityConfig:
    """安全配置生成器"""

    @staticmethod
    def generate_security_checklist() -> List[str]:
        """生成安全檢查清單"""
        checklist = [
            "✓ 使用 HTTPS/TLS 加密通信",
            "✓ 實施 API Key 認證",
            "✓ 配置防火牆規則",
            "✓ 啟用速率限制",
            "✓ 實施 CORS 策略",
            "✓ 使用環境變量存儲敏感信息",
            "✓ 定期更新依賴包",
            "✓ 實施輸入驗證",
            "✓ 啟用審計日誌",
            "✓ 配置備份策略",
            "✓ 實施最小權限原則",
            "✓ 啟用數據加密",
            "✓ 配置入侵檢測",
            "✓ 實施災難恢復計劃"
        ]
        return checklist

    @staticmethod
    def generate_env_template() -> str:
        """生成環境變量模板"""
        template = """# SuperAGI 生產環境配置

# 應用設置
ENV=production
DEBUG=false
SECRET_KEY=change-this-to-random-secret-key

# 數據庫
DATABASE_URL=postgresql://user:password@localhost:5432/superagi
REDIS_URL=redis://localhost:6379

# API Keys
OPENAI_API_KEY=sk-your-openai-key
PINECONE_API_KEY=your-pinecone-key

# 安全設置
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ORIGINS=https://yourdomain.com

# 資源限制
MAX_AGENTS_PER_USER=10
API_RATE_LIMIT=100
DEFAULT_BUDGET=10.0

# 監控
SENTRY_DSN=your-sentry-dsn
PROMETHEUS_ENABLED=true

# 日誌
LOG_LEVEL=INFO
LOG_FORMAT=json
"""
        return template


# ==================== 部署腳本 ====================

class DeploymentScripts:
    """部署腳本生成器"""

    @staticmethod
    def generate_deploy_script() -> str:
        """生成部署腳本"""
        script = """#!/bin/bash
set -e

echo "🚀 開始部署 SuperAGI..."

# 1. 檢查環境
echo "1. 檢查環境..."
if [ ! -f .env ]; then
    echo "❌ .env 文件不存在"
    exit 1
fi

# 2. 構建 Docker 鏡像
echo "2. 構建 Docker 鏡像..."
docker build -t superagi:latest .

# 3. 運行測試
echo "3. 運行測試..."
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# 4. 備份數據庫
echo "4. 備份數據庫..."
./scripts/backup_db.sh

# 5. 停止舊容器
echo "5. 停止舊容器..."
docker-compose down

# 6. 啟動新容器
echo "6. 啟動新容器..."
docker-compose up -d

# 7. 運行數據庫遷移
echo "7. 運行數據庫遷移..."
docker-compose exec superagi alembic upgrade head

# 8. 健康檢查
echo "8. 健康檢查..."
sleep 10
curl -f http://localhost:8000/health || exit 1

echo "✅ 部署完成！"
"""
        return script

    @staticmethod
    def generate_rollback_script() -> str:
        """生成回滾腳本"""
        script = """#!/bin/bash
set -e

echo "🔙 開始回滾 SuperAGI..."

# 1. 停止當前容器
echo "1. 停止當前容器..."
docker-compose down

# 2. 恢復數據庫備份
echo "2. 恢復數據庫備份..."
./scripts/restore_db.sh

# 3. 使用上一個版本的鏡像
echo "3. 使用上一個版本..."
docker-compose up -d

# 4. 健康檢查
echo "4. 健康檢查..."
sleep 10
curl -f http://localhost:8000/health || exit 1

echo "✅ 回滾完成！"
"""
        return script


# ==================== 示例場景 ====================

def example_1_docker_setup():
    """示例 1: Docker 部署設置"""
    print("\n" + "=" * 60)
    print("示例 1: Docker 部署配置")
    print("=" * 60)

    docker_config = DockerConfig()

    print("\n生成 Dockerfile:")
    print(docker_config.generate_dockerfile())

    print("\n生成 docker-compose.yml:")
    print(docker_config.generate_docker_compose()[:500] + "...")


def example_2_kubernetes_setup():
    """示例 2: Kubernetes 部署設置"""
    print("\n" + "=" * 60)
    print("示例 2: Kubernetes 部署配置")
    print("=" * 60)

    k8s_config = KubernetesConfig()

    print("\n生成 Deployment:")
    print(k8s_config.generate_deployment()[:500] + "...")

    print("\n生成 Service:")
    print(k8s_config.generate_service())


def example_3_monitoring_setup():
    """示例 3: 監控設置"""
    print("\n" + "=" * 60)
    print("示例 3: 監控配置")
    print("=" * 60)

    monitoring = MonitoringConfig()

    print("\n生成 Prometheus 配置:")
    print(monitoring.generate_prometheus_config())

    print("\n生成告警規則:")
    print(monitoring.generate_alert_rules()[:500] + "...")


def example_4_logging_setup():
    """示例 4: 日誌設置"""
    print("\n" + "=" * 60)
    print("示例 4: 日誌配置")
    print("=" * 60)

    logging_config = LoggingConfig()

    print("\n生成日誌配置:")
    config = logging_config.generate_logging_config()
    print(json.dumps(config, indent=2))


def example_5_security_setup():
    """示例 5: 安全設置"""
    print("\n" + "=" * 60)
    print("示例 5: 安全配置")
    print("=" * 60)

    security = SecurityConfig()

    print("\n安全檢查清單:")
    for item in security.generate_security_checklist():
        print(f"  {item}")

    print("\n環境變量模板:")
    print(security.generate_env_template())


def example_6_deployment_scripts():
    """示例 6: 部署腳本"""
    print("\n" + "=" * 60)
    print("示例 6: 部署和回滾腳本")
    print("=" * 60)

    scripts = DeploymentScripts()

    print("\n部署腳本:")
    print(scripts.generate_deploy_script())


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("\n" + "🚀 " * 20)
    print("SuperAGI 生產部署教程")
    print("🚀 " * 20)

    try:
        # 示例 1: Docker 設置
        example_1_docker_setup()

        # 示例 2: Kubernetes 設置
        example_2_kubernetes_setup()

        # 示例 3: 監控設置
        example_3_monitoring_setup()

        # 示例 4: 日誌設置
        example_4_logging_setup()

        # 示例 5: 安全設置
        example_5_security_setup()

        # 示例 6: 部署腳本
        example_6_deployment_scripts()

        print("\n" + "=" * 60)
        print("✅ 所有生產部署示例執行完成！")
        print("=" * 60)

        print("""
        生產部署檢查清單:

        部署前:
        1. ✓ 完成所有測試
        2. ✓ 審查安全配置
        3. ✓ 備份數據
        4. ✓ 準備回滾計劃
        5. ✓ 配置監控和告警

        部署階段:
        1. ✓ 構建和測試鏡像
        2. ✓ 執行數據庫遷移
        3. ✓ 逐步發布（金絲雀/藍綠）
        4. ✓ 監控系統指標
        5. ✓ 驗證功能正常

        部署後:
        1. ✓ 監控錯誤日誌
        2. ✓ 檢查性能指標
        3. ✓ 驗證所有功能
        4. ✓ 更新文檔
        5. ✓ 通知團隊

        運維最佳實踐:
        - 實施自動化部署流程
        - 定期備份和測試恢復
        - 監控系統健康狀態
        - 保持依賴更新
        - 定期審查安全配置
        - 維護災難恢復計劃
        """)

    except Exception as e:
        print(f"\n❌ 執行出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
