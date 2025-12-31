"""
Helicone 生產環境部署
=====================

本文件展示如何在生產環境中部署和運行 Helicone。
包含最佳實踐、監控、告警和故障恢復。

主要內容:
1. 生產環境配置
2. 負載均衡和高可用
3. 監控和告警系統
4. 日誌聚合
5. 性能優化
6. 安全加固
7. 災難恢復計劃

作者: Helicone Team
日期: 2025-12-31
"""

import os
import sys
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from dotenv import load_dotenv

try:
    import openai
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.tree import Tree
    from rich.progress import Progress, SpinnerColumn, TextColumn
    import pandas as pd
except ImportError as e:
    print(f"❌ 缺少必要的依賴: {e}")
    print("請運行: pip install openai rich pandas")
    sys.exit(1)


class DeploymentEnvironment(Enum):
    """部署環境"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class HealthStatus(Enum):
    """健康狀態"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ProductionConfig:
    """生產環境配置"""
    environment: str = "production"
    region: str = "us-east-1"

    # 高可用配置
    replicas: int = 3
    min_replicas: int = 2
    max_replicas: int = 10

    # 資源限制
    cpu_limit: str = "2000m"
    memory_limit: str = "4Gi"
    cpu_request: str = "500m"
    memory_request: str = "1Gi"

    # 性能配置
    max_connections: int = 1000
    connection_timeout: int = 30
    request_timeout: int = 300

    # 快取配置
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600

    # 速率限制
    rate_limit_enabled: bool = True
    requests_per_minute: int = 1000

    # 監控配置
    metrics_enabled: bool = True
    tracing_enabled: bool = True
    log_level: str = "info"

    # 安全配置
    ssl_enabled: bool = True
    cors_enabled: bool = True
    allowed_origins: List[str] = field(default_factory=lambda: ["https://app.example.com"])

    # 備份配置
    backup_enabled: bool = True
    backup_schedule: str = "0 2 * * *"  # 每天凌晨 2 點
    backup_retention_days: int = 30


class ProductionDeployment:
    """
    生產環境部署管理器

    管理 Helicone 在生產環境的部署和運維。
    """

    def __init__(self):
        """初始化部署管理器"""
        load_dotenv()

        self.console = Console()

        # API 配置
        self.helicone_api_key = os.getenv("HELICONE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.helicone_base_url = "https://oai.helicone.ai/v1"

        # 生產配置
        self.config = ProductionConfig()

        # 健康檢查歷史
        self.health_checks: List[Dict] = []

        # 告警歷史
        self.alerts: List[Dict] = []

        self.console.print("✅ [green]生產部署管理器已初始化[/green]")

    def generate_kubernetes_deployment(self) -> str:
        """
        生成 Kubernetes 部署配置

        包含完整的生產級 K8s 配置。
        """
        k8s_config = f"""
---
# Namespace
apiVersion: v1
kind: Namespace
metadata:
  name: helicone-production

---
# ConfigMap - 應用配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: helicone-config
  namespace: helicone-production
data:
  NODE_ENV: "production"
  LOG_LEVEL: "{self.config.log_level}"
  ENABLE_CACHING: "{str(self.config.cache_enabled).lower()}"
  ENABLE_RATE_LIMITING: "{str(self.config.rate_limit_enabled).lower()}"
  ENABLE_METRICS: "{str(self.config.metrics_enabled).lower()}"
  CACHE_TTL_SECONDS: "{self.config.cache_ttl_seconds}"
  MAX_CONNECTIONS: "{self.config.max_connections}"
  REQUEST_TIMEOUT: "{self.config.request_timeout}"

---
# Secret - 敏感信息
apiVersion: v1
kind: Secret
metadata:
  name: helicone-secrets
  namespace: helicone-production
type: Opaque
stringData:
  DATABASE_URL: "postgresql://user:password@postgres:5432/helicone"
  REDIS_URL: "redis://:password@redis:6379"
  JWT_SECRET: "your-super-secret-jwt-key"
  HELICONE_API_KEY: "your-helicone-api-key"

---
# Deployment - Web 服務
apiVersion: apps/v1
kind: Deployment
metadata:
  name: helicone-web
  namespace: helicone-production
  labels:
    app: helicone
    component: web
spec:
  replicas: {self.config.replicas}
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: helicone
      component: web
  template:
    metadata:
      labels:
        app: helicone
        component: web
    spec:
      # 安全上下文
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000

      # 容器配置
      containers:
      - name: helicone-web
        image: helicone/helicone:latest
        imagePullPolicy: Always

        # 資源限制
        resources:
          requests:
            cpu: {self.config.cpu_request}
            memory: {self.config.memory_request}
          limits:
            cpu: {self.config.cpu_limit}
            memory: {self.config.memory_limit}

        # 端口
        ports:
        - name: http
          containerPort: 3000
          protocol: TCP
        - name: metrics
          containerPort: 9090
          protocol: TCP

        # 環境變量
        envFrom:
        - configMapRef:
            name: helicone-config
        - secretRef:
            name: helicone-secrets

        # 健康檢查
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3

        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3

        # 啟動探針
        startupProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 0
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 30

        # 卷掛載
        volumeMounts:
        - name: logs
          mountPath: /app/logs

      # 卷定義
      volumes:
      - name: logs
        emptyDir: {{}}

      # 親和性配置 - 分散到不同節點
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - helicone
              topologyKey: kubernetes.io/hostname

---
# Service - 內部服務
apiVersion: v1
kind: Service
metadata:
  name: helicone-web
  namespace: helicone-production
  labels:
    app: helicone
    component: web
spec:
  type: ClusterIP
  ports:
  - name: http
    port: 80
    targetPort: 3000
    protocol: TCP
  - name: metrics
    port: 9090
    targetPort: 9090
    protocol: TCP
  selector:
    app: helicone
    component: web

---
# HorizontalPodAutoscaler - 自動擴展
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: helicone-web-hpa
  namespace: helicone-production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: helicone-web
  minReplicas: {self.config.min_replicas}
  maxReplicas: {self.config.max_replicas}
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

---
# Ingress - 外部訪問
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: helicone-ingress
  namespace: helicone-production
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
spec:
  tls:
  - hosts:
    - helicone.example.com
    secretName: helicone-tls
  rules:
  - host: helicone.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: helicone-web
            port:
              number: 80

---
# PodDisruptionBudget - 確保高可用
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: helicone-web-pdb
  namespace: helicone-production
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: helicone
      component: web

---
# ServiceMonitor - Prometheus 監控
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: helicone-web
  namespace: helicone-production
  labels:
    app: helicone
spec:
  selector:
    matchLabels:
      app: helicone
      component: web
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
"""
        return k8s_config.strip()

    def generate_monitoring_config(self) -> str:
        """生成 Prometheus 監控配置"""
        prometheus_config = """
# Prometheus 配置

global:
  scrape_interval: 30s
  evaluation_interval: 30s

# 告警規則
rule_files:
  - 'alerts.yml'

# 告警管理器
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

# 抓取配置
scrape_configs:
  # Helicone 應用指標
  - job_name: 'helicone'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - helicone-production
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: helicone
      - source_labels: [__meta_kubernetes_pod_container_port_name]
        action: keep
        regex: metrics

  # Node Exporter - 節點指標
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  # PostgreSQL Exporter
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  # Redis Exporter
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
"""
        return prometheus_config.strip()

    def generate_alert_rules(self) -> str:
        """生成告警規則"""
        alert_rules = """
# Prometheus 告警規則

groups:
  - name: helicone_alerts
    interval: 30s
    rules:
      # 高錯誤率告警
      - alert: HighErrorRate
        expr: |
          (
            sum(rate(http_requests_total{status=~"5.."}[5m]))
            /
            sum(rate(http_requests_total[5m]))
          ) > 0.05
        for: 5m
        labels:
          severity: critical
          component: helicone-web
        annotations:
          summary: "高錯誤率: {{ $value | humanizePercentage }}"
          description: "Helicone 的錯誤率超過 5%"

      # 高延遲告警
      - alert: HighLatency
        expr: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
          ) > 2
        for: 5m
        labels:
          severity: warning
          component: helicone-web
        annotations:
          summary: "高延遲: {{ $value }}s"
          description: "95% 請求延遲超過 2 秒"

      # 容器重啟告警
      - alert: PodRestart
        expr: |
          rate(kube_pod_container_status_restarts_total{namespace="helicone-production"}[15m]) > 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Pod 正在重啟"
          description: "{{ $labels.pod }} 在過去 15 分鐘內重啟了 {{ $value }} 次"

      # CPU 使用率告警
      - alert: HighCPUUsage
        expr: |
          (
            sum(rate(container_cpu_usage_seconds_total{namespace="helicone-production"}[5m]))
            /
            sum(kube_pod_container_resource_limits{namespace="helicone-production",resource="cpu"})
          ) > 0.8
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "CPU 使用率過高: {{ $value | humanizePercentage }}"
          description: "CPU 使用率超過 80%"

      # 內存使用率告警
      - alert: HighMemoryUsage
        expr: |
          (
            sum(container_memory_usage_bytes{namespace="helicone-production"})
            /
            sum(kube_pod_container_resource_limits{namespace="helicone-production",resource="memory"})
          ) > 0.85
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "內存使用率過高: {{ $value | humanizePercentage }}"
          description: "內存使用率超過 85%"

      # 數據庫連接池告警
      - alert: DatabaseConnectionPoolExhaustion
        expr: |
          pg_stat_database_numbackends / pg_settings_max_connections > 0.8
        for: 5m
        labels:
          severity: critical
          component: database
        annotations:
          summary: "數據庫連接池接近耗盡"
          description: "PostgreSQL 連接使用率: {{ $value | humanizePercentage }}"

      # Redis 內存使用告警
      - alert: RedisHighMemoryUsage
        expr: |
          redis_memory_used_bytes / redis_memory_max_bytes > 0.9
        for: 5m
        labels:
          severity: warning
          component: redis
        annotations:
          summary: "Redis 內存使用率過高"
          description: "Redis 內存使用率: {{ $value | humanizePercentage }}"

      # 磁盤空間告警
      - alert: DiskSpaceLow
        expr: |
          (
            node_filesystem_avail_bytes{mountpoint="/data"}
            /
            node_filesystem_size_bytes{mountpoint="/data"}
          ) < 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "磁盤空間不足"
          description: "可用磁盤空間少於 10%"
"""
        return alert_rules.strip()

    def generate_deployment_checklist(self) -> List[Dict[str, str]]:
        """生成部署檢查清單"""
        checklist = [
            {
                "category": "環境準備",
                "items": [
                    "✓ Kubernetes 集群已就緒 (版本 >= 1.24)",
                    "✓ kubectl 已配置並可訪問集群",
                    "✓ Helm 已安裝 (如果使用)",
                    "✓ 域名 DNS 記錄已配置",
                    "✓ SSL 證書已準備 (Let's Encrypt 或其他)",
                ]
            },
            {
                "category": "依賴服務",
                "items": [
                    "✓ PostgreSQL 已部署並可訪問",
                    "✓ Redis 已部署並可訪問",
                    "✓ ClickHouse 已部署 (可選)",
                    "✓ 對象存儲已配置 (S3/MinIO)",
                    "✓ 密鑰管理服務已配置",
                ]
            },
            {
                "category": "監控和日誌",
                "items": [
                    "✓ Prometheus 已部署",
                    "✓ Grafana 已部署並配置儀表板",
                    "✓ AlertManager 已配置",
                    "✓ 日誌聚合系統已就緒 (ELK/Loki)",
                    "✓ 告警通道已配置 (Email/Slack/PagerDuty)",
                ]
            },
            {
                "category": "安全配置",
                "items": [
                    "✓ 所有密碼已更改為強密碼",
                    "✓ API 密鑰已輪換",
                    "✓ RBAC 權限已配置",
                    "✓ 網絡策略已啟用",
                    "✓ Pod 安全策略已配置",
                    "✓ 鏡像簽名驗證已啟用",
                ]
            },
            {
                "category": "備份和恢復",
                "items": [
                    "✓ 數據庫自動備份已配置",
                    "✓ 備份恢復流程已測試",
                    "✓ 災難恢復計劃已文檔化",
                    "✓ RTO/RPO 目標已定義",
                ]
            },
            {
                "category": "性能和擴展",
                "items": [
                    "✓ HPA (自動擴展) 已配置",
                    "✓ 資源限制已設置",
                    "✓ PDB (中斷預算) 已配置",
                    "✓ 負載測試已完成",
                    "✓ 性能基準已建立",
                ]
            },
            {
                "category": "上線前檢查",
                "items": [
                    "✓ 健康檢查端點正常",
                    "✓ 所有服務通信正常",
                    "✓ 監控告警正常工作",
                    "✓ 日誌正確收集",
                    "✓ 備份計劃運行正常",
                    "✓ 文檔已更新",
                    "✓ 團隊已培訓",
                    "✓ 回滾計劃已準備",
                ]
            }
        ]
        return checklist

    def display_deployment_checklist(self):
        """顯示部署檢查清單"""
        self.console.print("\n[bold cyan]📋 生產部署檢查清單[/bold cyan]")
        self.console.print("=" * 80)

        checklist = self.generate_deployment_checklist()

        for section in checklist:
            self.console.print(f"\n[bold yellow]{section['category']}[/bold yellow]")

            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column("項目", style="green")

            for item in section["items"]:
                table.add_row(item)

            self.console.print(table)

    def generate_runbook(self) -> str:
        """生成運維手冊"""
        runbook = """
# Helicone 生產環境運維手冊

## 常見問題和解決方案

### 1. 服務無響應

**症狀**: 服務不響應請求,返回 502/503 錯誤

**診斷步驟**:
```bash
# 檢查 Pod 狀態
kubectl get pods -n helicone-production

# 查看 Pod 日誌
kubectl logs -n helicone-production deployment/helicone-web --tail=100

# 檢查資源使用
kubectl top pods -n helicone-production

# 檢查事件
kubectl get events -n helicone-production --sort-by='.lastTimestamp'
```

**解決方案**:
1. 如果是 OOM (內存不足):
   ```bash
   kubectl scale deployment/helicone-web -n helicone-production --replicas=0
   kubectl scale deployment/helicone-web -n helicone-production --replicas=3
   ```

2. 如果是 CPU 限制:
   - 增加資源限制或觸發自動擴展

3. 如果是應用崩潰:
   - 查看日誌找出根因
   - 回滾到上一個穩定版本

### 2. 數據庫連接問題

**症狀**: 日誌中出現 "too many connections" 錯誤

**診斷步驟**:
```bash
# 檢查數據庫連接數
kubectl exec -n helicone-production postgres-0 -- \
  psql -U helicone -c "SELECT count(*) FROM pg_stat_activity;"

# 查看連接詳情
kubectl exec -n helicone-production postgres-0 -- \
  psql -U helicone -c "SELECT * FROM pg_stat_activity;"
```

**解決方案**:
1. 終止空閒連接:
   ```sql
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle'
   AND state_change < current_timestamp - INTERVAL '30 minutes';
   ```

2. 增加 max_connections:
   - 編輯 PostgreSQL 配置
   - 重啟數據庫

### 3. 高延遲

**症狀**: API 響應時間過長

**診斷步驟**:
```bash
# 檢查應用性能指標
kubectl port-forward -n helicone-production svc/helicone-web 9090:9090
# 訪問 http://localhost:9090/metrics

# 檢查數據庫性能
kubectl exec -n helicone-production postgres-0 -- \
  psql -U helicone -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

**解決方案**:
1. 啟用或優化快取
2. 優化慢查詢
3. 增加副本數量
4. 檢查網絡延遲

### 4. 磁盤空間不足

**症狀**: 磁盤使用率 > 90%

**診斷步驟**:
```bash
# 檢查磁盤使用
kubectl exec -n helicone-production postgres-0 -- df -h

# 查找大文件
kubectl exec -n helicone-production postgres-0 -- \
  du -h /var/lib/postgresql/data | sort -rh | head -20
```

**解決方案**:
1. 清理舊日誌:
   ```bash
   kubectl exec -n helicone-production postgres-0 -- \
     find /var/lib/postgresql/data/pg_log -mtime +7 -delete
   ```

2. 清理舊備份
3. 擴展 PVC 容量:
   ```bash
   kubectl edit pvc postgres-data -n helicone-production
   # 增加 spec.resources.requests.storage
   ```

### 5. 部署回滾

**症狀**: 新部署導致問題

**回滾步驟**:
```bash
# 查看部署歷史
kubectl rollout history deployment/helicone-web -n helicone-production

# 回滾到上一個版本
kubectl rollout undo deployment/helicone-web -n helicone-production

# 回滾到特定版本
kubectl rollout undo deployment/helicone-web -n helicone-production --to-revision=2

# 檢查回滾狀態
kubectl rollout status deployment/helicone-web -n helicone-production
```

### 6. 擴容/縮容

**手動擴展**:
```bash
# 擴展到 5 個副本
kubectl scale deployment/helicone-web -n helicone-production --replicas=5

# 檢查擴展狀態
kubectl get pods -n helicone-production -l app=helicone
```

**調整自動擴展**:
```bash
# 編輯 HPA
kubectl edit hpa helicone-web-hpa -n helicone-production

# 查看 HPA 狀態
kubectl get hpa -n helicone-production
```

### 7. 數據庫備份和恢復

**手動備份**:
```bash
# 創建備份
kubectl exec -n helicone-production postgres-0 -- \
  pg_dump -U helicone helicone | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

**恢復備份**:
```bash
# 恢復數據
gunzip -c backup_20231225_120000.sql.gz | \
  kubectl exec -i -n helicone-production postgres-0 -- \
  psql -U helicone helicone
```

## 日常維護任務

### 每日任務
- [ ] 檢查監控儀表板
- [ ] 查看告警
- [ ] 檢查錯誤日誌
- [ ] 驗證備份成功

### 每週任務
- [ ] 審查資源使用趨勢
- [ ] 檢查磁盤空間
- [ ] 更新依賴包
- [ ] 審查安全掃描結果

### 每月任務
- [ ] 測試災難恢復流程
- [ ] 審查訪問權限
- [ ] 輪換密鑰和密碼
- [ ] 性能優化審查
- [ ] 容量規劃

## 聯繫方式

- **緊急問題**: ops-oncall@example.com
- **一般支持**: support@example.com
- **Slack**: #helicone-ops
- **PagerDuty**: https://example.pagerduty.com
"""
        return runbook.strip()

    def display_production_architecture(self):
        """顯示生產架構"""
        self.console.print("\n[bold cyan]🏗️  生產環境架構[/bold cyan]")
        self.console.print("=" * 80)

        architecture = """
┌─────────────────────────────────────────────────────────────────┐
│                        外部用戶/API 客戶端                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  DNS / CDN    │
                    └───────┬───────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │  Load Balancer  │  ◄── SSL Termination
                   │   (Ingress)     │
                   └────────┬────────┘
                            │
            ┌───────────────┴───────────────┐
            │                               │
            ▼                               ▼
    ┌──────────────┐              ┌──────────────┐
    │ Helicone Web │              │ Helicone Web │  ◄── Auto-scaling
    │   Pod 1      │              │   Pod 2-N    │
    └──────┬───────┘              └──────┬───────┘
           │                             │
           └──────────┬──────────────────┘
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
    ┌──────────┐           ┌──────────┐
    │PostgreSQL│           │  Redis   │  ◄── Session & Cache
    │ Primary  │◄─────────►│ Cluster  │
    └────┬─────┘           └──────────┘
         │
         ▼
    ┌──────────┐
    │PostgreSQL│  ◄── Read Replica
    │ Replica  │
    └──────────┘

監控層:
    ┌──────────┐     ┌──────────┐     ┌──────────┐
    │Prometheus│────►│ Grafana  │────►│AlertMgr  │
    └──────────┘     └──────────┘     └──────────┘

日誌層:
    ┌──────────┐     ┌──────────┐
    │  Loki    │────►│ Grafana  │
    └──────────┘     └──────────┘
"""

        self.console.print(architecture)

    def display_deployment_summary(self):
        """顯示部署摘要"""
        summary = f"""
[bold cyan]部署配置摘要[/bold cyan]

[yellow]環境:[/yellow] {self.config.environment.upper()}
[yellow]區域:[/yellow] {self.config.region}

[yellow]高可用配置:[/yellow]
  副本數: {self.config.replicas} (最小: {self.config.min_replicas}, 最大: {self.config.max_replicas})

[yellow]資源配置:[/yellow]
  CPU: {self.config.cpu_request} ~ {self.config.cpu_limit}
  內存: {self.config.memory_request} ~ {self.config.memory_limit}

[yellow]性能配置:[/yellow]
  最大連接數: {self.config.max_connections}
  請求超時: {self.config.request_timeout}s

[yellow]功能開關:[/yellow]
  快取: {'✓' if self.config.cache_enabled else '✗'}
  速率限制: {'✓' if self.config.rate_limit_enabled else '✗'}
  監控: {'✓' if self.config.metrics_enabled else '✗'}
  SSL: {'✓' if self.config.ssl_enabled else '✗'}
  備份: {'✓' if self.config.backup_enabled else '✗'}
"""

        panel = Panel(
            summary.strip(),
            title="📊 配置概覽",
            border_style="cyan"
        )

        self.console.print(panel)


def main():
    """主函數"""
    console = Console()
    console.print("[bold green]🎯 Helicone 生產環境部署指南[/bold green]\n")

    try:
        # 初始化部署管理器
        deployment = ProductionDeployment()

        # 顯示部署摘要
        deployment.display_deployment_summary()

        # 顯示架構
        deployment.display_production_architecture()

        # 顯示檢查清單
        deployment.display_deployment_checklist()

        # 生成 Kubernetes 配置
        console.print("\n[bold cyan]📝 生成 Kubernetes 配置文件...[/bold cyan]")
        k8s_config = deployment.generate_kubernetes_deployment()
        with open("helicone-production-k8s.yaml", "w") as f:
            f.write(k8s_config)
        console.print("✅ [green]已保存: helicone-production-k8s.yaml[/green]")

        # 生成監控配置
        console.print("\n[bold cyan]📝 生成監控配置...[/bold cyan]")
        prometheus_config = deployment.generate_monitoring_config()
        with open("prometheus.yml", "w") as f:
            f.write(prometheus_config)
        console.print("✅ [green]已保存: prometheus.yml[/green]")

        # 生成告警規則
        alert_rules = deployment.generate_alert_rules()
        with open("alerts.yml", "w") as f:
            f.write(alert_rules)
        console.print("✅ [green]已保存: alerts.yml[/green]")

        # 生成運維手冊
        console.print("\n[bold cyan]📝 生成運維手冊...[/bold cyan]")
        runbook = deployment.generate_runbook()
        with open("RUNBOOK.md", "w") as f:
            f.write(runbook)
        console.print("✅ [green]已保存: RUNBOOK.md[/green]")

        # 最終提示
        console.print("\n" + "=" * 80)
        console.print("[bold green]✨ 生產部署配置已完成![/bold green]\n")

        next_steps = """
[bold cyan]後續步驟:[/bold cyan]

1. 審查生成的配置文件
2. 根據實際環境調整配置
3. 完成部署檢查清單中的所有項目
4. 在測試環境驗證配置
5. 執行部署:
   [green]kubectl apply -f helicone-production-k8s.yaml[/green]
6. 驗證部署:
   [green]kubectl get pods -n helicone-production[/green]
7. 配置監控和告警
8. 執行冒煙測試
9. 監控指標並優化

[yellow]⚠️  重要提醒:[/yellow]
- 確保所有密鑰已正確配置
- 在生產環境使用正式 SSL 證書
- 設置適當的資源限制
- 配置自動備份
- 建立災難恢復計劃
- 培訓運維團隊
"""

        panel = Panel(
            next_steps.strip(),
            title="🚀 準備就緒",
            border_style="green"
        )

        console.print(panel)

    except Exception as e:
        console.print(f"\n❌ [red]錯誤: {str(e)}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
