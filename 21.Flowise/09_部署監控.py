"""
Flowise 部署與監控範例
====================

本範例展示如何部署和監控 Flowise。

部署選項：
1. Docker 部署
2. 雲端部署
3. 監控設置
4. 日誌管理

安裝依賴：
pip install requests prometheus-client
"""

import os
import json
from typing import Dict, Any

# ============================================================
# Docker 部署配置
# ============================================================

DOCKER_COMPOSE = '''
version: '3.8'

services:
  flowise:
    image: flowiseai/flowise:latest
    restart: always
    environment:
      - PORT=3000
      - FLOWISE_USERNAME=${FLOWISE_USERNAME}
      - FLOWISE_PASSWORD=${FLOWISE_PASSWORD}
      - DATABASE_TYPE=postgres
      - DATABASE_HOST=postgres
      - DATABASE_PORT=5432
      - DATABASE_USER=${POSTGRES_USER}
      - DATABASE_PASSWORD=${POSTGRES_PASSWORD}
      - DATABASE_NAME=flowise
      - SECRETKEY_PATH=/root/.flowise
    ports:
      - "3000:3000"
    volumes:
      - flowise_data:/root/.flowise
    depends_on:
      - postgres
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15
    restart: always
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=flowise
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  flowise_data:
  postgres_data:
'''

DOCKERFILE = '''
FROM flowiseai/flowise:latest

# 安裝額外依賴
RUN npm install -g pm2

# 設置環境變數
ENV NODE_ENV=production
ENV PORT=3000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \\
    CMD curl -f http://localhost:3000/api/v1/health || exit 1

EXPOSE 3000

CMD ["npx", "flowise", "start"]
'''


# ============================================================
# Kubernetes 部署
# ============================================================

K8S_DEPLOYMENT = '''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flowise
spec:
  replicas: 3
  selector:
    matchLabels:
      app: flowise
  template:
    metadata:
      labels:
        app: flowise
    spec:
      containers:
      - name: flowise
        image: flowiseai/flowise:latest
        ports:
        - containerPort: 3000
        env:
        - name: DATABASE_TYPE
          value: "postgres"
        - name: DATABASE_HOST
          valueFrom:
            secretKeyRef:
              name: flowise-secrets
              key: db-host
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: flowise-service
spec:
  selector:
    app: flowise
  ports:
  - port: 80
    targetPort: 3000
  type: LoadBalancer
'''


# ============================================================
# 監控配置
# ============================================================

PROMETHEUS_CONFIG = '''
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'flowise'
    static_configs:
      - targets: ['flowise:3000']
    metrics_path: /api/v1/metrics
'''

GRAFANA_DASHBOARD = '''
{
  "dashboard": {
    "title": "Flowise Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "rate(flowise_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(flowise_response_time_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "singlestat",
        "targets": [
          {
            "expr": "sum(rate(flowise_errors_total[5m]))"
          }
        ]
      }
    ]
  }
}
'''


# ============================================================
# 使用範例
# ============================================================

def example_docker():
    """範例 1: Docker 部署"""
    print("=" * 50)
    print("範例 1: Docker 部署")
    print("=" * 50)
    print(DOCKER_COMPOSE)


def example_k8s():
    """範例 2: Kubernetes 部署"""
    print("\n" + "=" * 50)
    print("範例 2: Kubernetes 部署")
    print("=" * 50)
    print(K8S_DEPLOYMENT[:1000] + "...")


def example_monitoring():
    """範例 3: 監控配置"""
    print("\n" + "=" * 50)
    print("範例 3: Prometheus 監控")
    print("=" * 50)
    print(PROMETHEUS_CONFIG)


def example_health_check():
    """範例 4: 健康檢查"""
    print("\n" + "=" * 50)
    print("範例 4: 健康檢查 API")
    print("=" * 50)
    print("""
# 健康檢查端點
GET /api/v1/health

# 響應示例
{
    "status": "OK",
    "uptime": 123456,
    "version": "1.0.0"
}

# 使用 Python 檢查
import requests

def check_health(base_url):
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=5)
        return response.status_code == 200
    except:
        return False
""")


def example_logging():
    """範例 5: 日誌配置"""
    print("\n" + "=" * 50)
    print("範例 5: 日誌配置")
    print("=" * 50)
    print("""
# 環境變數配置
LOG_LEVEL=info
LOG_PATH=/var/log/flowise

# Docker 日誌收集
services:
  flowise:
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "5"
""")


def example_backup():
    """範例 6: 備份策略"""
    print("\n" + "=" * 50)
    print("範例 6: 備份策略")
    print("=" * 50)
    print("""
# 備份數據庫
pg_dump -h localhost -U flowise flowise > backup.sql

# 備份 Chatflows
curl -X GET http://localhost:3000/api/v1/chatflows \\
    -H "Authorization: Bearer $API_KEY" \\
    > chatflows_backup.json

# 定時備份腳本
#!/bin/bash
DATE=$(date +%Y%m%d)
pg_dump flowise > /backups/flowise_$DATE.sql
""")


def example_scaling():
    """範例 7: 擴展配置"""
    print("\n" + "=" * 50)
    print("範例 7: 自動擴展")
    print("=" * 50)
    print("""
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: flowise-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: flowise
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
""")


if __name__ == "__main__":
    print("Flowise 部署與監控範例\\n")
    example_docker()
    example_k8s()
    example_monitoring()
    example_health_check()
    example_logging()
    example_backup()
    example_scaling()
