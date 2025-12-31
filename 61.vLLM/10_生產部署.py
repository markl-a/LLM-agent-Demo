#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
vLLM 生產部署示例
=================

本示例展示如何將 vLLM 部署到生產環境，包括：
1. Docker 容器化部署
2. Kubernetes 集群部署
3. 負載均衡配置
4. 高可用架構
5. 監控和日誌
6. 安全性配置
7. CI/CD 流程
8. 故障恢復

目標：
- 高可用性
- 可擴展性
- 安全性
- 可維護性

適用場景：
- 生產環境部署
- 企業級應用
- 大規模服務
"""

import sys


def deployment_overview():
    """
    部署概覽

    介紹生產環境部署的整體架構
    """
    print("=" * 80)
    print("生產環境部署概覽")
    print("=" * 80)

    print("""
生產環境架構：
------------

                    ┌─────────────────┐
                    │  負載均衡器      │
                    │  (Nginx/HAProxy)│
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
     ┌──────▼──────┐  ┌─────▼──────┐  ┌─────▼──────┐
     │  vLLM 實例1  │  │ vLLM 實例2  │  │ vLLM 實例3  │
     │  (Pod/容器)  │  │ (Pod/容器)  │  │ (Pod/容器)  │
     └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
            │                │                │
     ┌──────▼──────────────┬▼────────────────▼──────┐
     │          GPU 資源池 (K8s 管理)                │
     └──────────────────────────────────────────────┘
            │
     ┌──────▼──────────────────────────────────────┐
     │  監控和日誌系統                               │
     │  (Prometheus + Grafana + ELK)                │
     └──────────────────────────────────────────────┘

核心組件：
---------

1. vLLM 服務
   - OpenAI 兼容 API 服務器
   - 支持多實例部署
   - 自動擴縮容

2. 負載均衡
   - Nginx/HAProxy/Envoy
   - 健康檢查
   - 請求路由

3. 容器編排
   - Kubernetes (推薦)
   - Docker Swarm
   - Nomad

4. 存儲
   - 模型文件存儲 (NFS/S3)
   - 持久化日誌
   - 配置管理

5. 監控
   - Prometheus (指標)
   - Grafana (可視化)
   - ELK Stack (日誌)
   - Jaeger (追蹤)

6. 安全
   - API 密鑰認證
   - HTTPS/TLS
   - 網絡隔離
   - 訪問控制

部署選項：
---------

選項 1: 單機部署
✓ 簡單
✓ 成本低
✗ 無高可用
✗ 難擴展
適合: 開發/測試環境

選項 2: 多實例 + 負載均衡
✓ 高可用
✓ 可擴展
✓ 易維護
推薦: 中小規模生產

選項 3: Kubernetes 集群
✓ 高可用
✓ 自動擴縮容
✓ 資源調度
✓ 故障自愈
推薦: 大規模生產
    """)


def docker_deployment():
    """
    Docker 容器化部署

    展示如何使用 Docker 部署 vLLM
    """
    print("\n" + "=" * 80)
    print("示例 1: Docker 容器化部署")
    print("=" * 80)

    print("""
Dockerfile：
-----------

```dockerfile
# Dockerfile
FROM nvidia/cuda:12.1.0-devel-ubuntu22.04

# 設置環境變量
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# 安裝基礎依賴
RUN apt-get update && apt-get install -y \\
    python3.10 \\
    python3-pip \\
    git \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# 安裝 vLLM
RUN pip3 install --no-cache-dir \\
    vllm>=0.4.0 \\
    torch>=2.0.0 \\
    transformers>=4.40.0

# 創建工作目錄
WORKDIR /app

# 複製配置文件
COPY config.yaml /app/config.yaml

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# 暴露端口
EXPOSE 8000

# 啟動命令
CMD ["python3", "-m", "vllm.entrypoints.openai.api_server", \\
     "--model", "meta-llama/Llama-2-7b-chat-hf", \\
     "--port", "8000", \\
     "--host", "0.0.0.0"]
```

構建鏡像：
---------

```bash
# 構建
docker build -t vllm-service:latest .

# 推送到私有倉庫
docker tag vllm-service:latest registry.example.com/vllm-service:latest
docker push registry.example.com/vllm-service:latest
```

docker-compose.yml：
-------------------

```yaml
version: '3.8'

services:
  vllm:
    image: vllm-service:latest
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - CUDA_VISIBLE_DEVICES=0
    ports:
      - "8000:8000"
    volumes:
      - /path/to/models:/models:ro
      - ./logs:/app/logs
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  # Nginx 負載均衡
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - vllm
    restart: unless-stopped

  # Prometheus 監控
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    restart: unless-stopped

  # Grafana 可視化
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
```

啟動服務：
---------

```bash
# 啟動所有服務
docker-compose up -d

# 查看日誌
docker-compose logs -f vllm

# 擴展實例
docker-compose up -d --scale vllm=3

# 停止服務
docker-compose down
```

多 GPU 配置：
------------

```yaml
# docker-compose.gpu.yml
services:
  vllm-gpu0:
    image: vllm-service:latest
    runtime: nvidia
    environment:
      - CUDA_VISIBLE_DEVICES=0
    ports:
      - "8001:8000"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['0']
              capabilities: [gpu]

  vllm-gpu1:
    image: vllm-service:latest
    runtime: nvidia
    environment:
      - CUDA_VISIBLE_DEVICES=1
    ports:
      - "8002:8000"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['1']
              capabilities: [gpu]
```
    """)


def kubernetes_deployment():
    """
    Kubernetes 集群部署

    展示如何在 K8s 集群上部署 vLLM
    """
    print("\n" + "=" * 80)
    print("示例 2: Kubernetes 集群部署")
    print("=" * 80)

    print("""
Deployment YAML：
----------------

```yaml
# vllm-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-deployment
  namespace: llm-serving
  labels:
    app: vllm
spec:
  replicas: 3
  selector:
    matchLabels:
      app: vllm
  template:
    metadata:
      labels:
        app: vllm
    spec:
      containers:
      - name: vllm
        image: registry.example.com/vllm-service:latest
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: MODEL_NAME
          value: "meta-llama/Llama-2-7b-chat-hf"
        - name: TENSOR_PARALLEL_SIZE
          value: "1"
        resources:
          requests:
            nvidia.com/gpu: 1
            memory: "16Gi"
            cpu: "4"
          limits:
            nvidia.com/gpu: 1
            memory: "32Gi"
            cpu: "8"
        volumeMounts:
        - name: model-cache
          mountPath: /root/.cache/huggingface
          readOnly: true
        - name: logs
          mountPath: /app/logs
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
      volumes:
      - name: model-cache
        persistentVolumeClaim:
          claimName: model-cache-pvc
      - name: logs
        emptyDir: {}
      nodeSelector:
        gpu: "true"
      tolerations:
      - key: nvidia.com/gpu
        operator: Exists
        effect: NoSchedule
---
apiVersion: v1
kind: Service
metadata:
  name: vllm-service
  namespace: llm-serving
spec:
  selector:
    app: vllm
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
    name: http
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: model-cache-pvc
  namespace: llm-serving
spec:
  accessModes:
  - ReadWriteMany
  storageClassName: nfs-client
  resources:
    requests:
      storage: 100Gi
```

Ingress 配置：
-------------

```yaml
# vllm-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vllm-ingress
  namespace: llm-serving
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - llm.example.com
    secretName: vllm-tls
  rules:
  - host: llm.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: vllm-service
            port:
              number: 8000
```

HPA 自動擴縮容：
--------------

```yaml
# vllm-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: vllm-hpa
  namespace: llm-serving
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: vllm-deployment
  minReplicas: 2
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
  - type: Pods
    pods:
      metric:
        name: requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 2
        periodSeconds: 30
```

部署命令：
---------

```bash
# 創建命名空間
kubectl create namespace llm-serving

# 部署應用
kubectl apply -f vllm-deployment.yaml
kubectl apply -f vllm-ingress.yaml
kubectl apply -f vllm-hpa.yaml

# 查看狀態
kubectl get pods -n llm-serving
kubectl get svc -n llm-serving
kubectl get hpa -n llm-serving

# 查看日誌
kubectl logs -f deployment/vllm-deployment -n llm-serving

# 擴縮容
kubectl scale deployment vllm-deployment --replicas=5 -n llm-serving

# 滾動更新
kubectl set image deployment/vllm-deployment \\
    vllm=registry.example.com/vllm-service:v2 \\
    -n llm-serving

# 回滾
kubectl rollout undo deployment/vllm-deployment -n llm-serving
```

GPU 調度配置：
-------------

```yaml
# gpu-node-pool.yaml
apiVersion: v1
kind: Node
metadata:
  name: gpu-node-1
  labels:
    gpu: "true"
    gpu-type: "a100"
    gpu-count: "8"
spec:
  taints:
  - key: nvidia.com/gpu
    value: "true"
    effect: NoSchedule
```

多模型部署：
-----------

```yaml
# multi-model-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-llama-7b
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: vllm
        env:
        - name: MODEL_NAME
          value: "meta-llama/Llama-2-7b-chat-hf"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-mistral-7b
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: vllm
        env:
        - name: MODEL_NAME
          value: "mistralai/Mistral-7B-Instruct-v0.1"
```
    """)


def load_balancing():
    """
    負載均衡配置

    展示負載均衡器的配置
    """
    print("\n" + "=" * 80)
    print("示例 3: 負載均衡配置")
    print("=" * 80)

    print("""
Nginx 配置：
-----------

```nginx
# nginx.conf
upstream vllm_backend {
    least_conn;  # 最少連接算法

    # vLLM 實例
    server vllm-1:8000 max_fails=3 fail_timeout=30s;
    server vllm-2:8000 max_fails=3 fail_timeout=30s;
    server vllm-3:8000 max_fails=3 fail_timeout=30s;

    # 健康檢查
    keepalive 32;
}

server {
    listen 80;
    server_name llm.example.com;

    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name llm.example.com;

    # SSL 配置
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # 安全頭
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # 日誌
    access_log /var/log/nginx/vllm_access.log;
    error_log /var/log/nginx/vllm_error.log;

    # 限流
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;
    limit_req zone=api_limit burst=20 nodelay;

    # 代理配置
    location / {
        proxy_pass http://vllm_backend;
        proxy_http_version 1.1;

        # 超時設置
        proxy_connect_timeout 60s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;

        # 頭部設置
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支持（用於流式）
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 緩衝設置
        proxy_buffering off;
        proxy_request_buffering off;
    }

    # 健康檢查端點
    location /health {
        proxy_pass http://vllm_backend/health;
        access_log off;
    }

    # 監控端點（僅內部訪問）
    location /metrics {
        allow 10.0.0.0/8;
        deny all;
        proxy_pass http://vllm_backend/metrics;
    }
}
```

HAProxy 配置：
-------------

```haproxy
# haproxy.cfg
global
    log /dev/log local0
    maxconn 4096
    stats socket /run/haproxy/admin.sock mode 660 level admin
    stats timeout 30s

defaults
    log global
    mode http
    option httplog
    option dontlognull
    timeout connect 10s
    timeout client 600s
    timeout server 600s

frontend vllm_frontend
    bind *:80
    bind *:443 ssl crt /etc/haproxy/certs/cert.pem

    # HTTPS 重定向
    redirect scheme https code 301 if !{ ssl_fc }

    # 訪問控制列表
    acl is_health path_beg /health
    acl is_api path_beg /v1

    # 路由規則
    use_backend vllm_health if is_health
    use_backend vllm_api if is_api
    default_backend vllm_api

backend vllm_health
    option httpchk GET /health
    http-check expect status 200

    server vllm-1 vllm-1:8000 check inter 10s
    server vllm-2 vllm-2:8000 check inter 10s
    server vllm-3 vllm-3:8000 check inter 10s

backend vllm_api
    balance leastconn
    option httpchk GET /health
    http-check expect status 200

    # 會話粘性（如果需要）
    # stick-table type ip size 200k expire 30m
    # stick on src

    server vllm-1 vllm-1:8000 check inter 30s fall 3 rise 2
    server vllm-2 vllm-2:8000 check inter 30s fall 3 rise 2
    server vllm-3 vllm-3:8000 check inter 30s fall 3 rise 2

# 監控頁面
listen stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 30s
    stats auth admin:password
```

基於路由的負載均衡：
------------------

```nginx
# 根據模型路由到不同後端
map $request_uri $backend_name {
    ~*/v1/chat/llama    vllm_llama_backend;
    ~*/v1/chat/mistral  vllm_mistral_backend;
    default             vllm_default_backend;
}

upstream vllm_llama_backend {
    server vllm-llama-1:8000;
    server vllm-llama-2:8000;
}

upstream vllm_mistral_backend {
    server vllm-mistral-1:8000;
    server vllm-mistral-2:8000;
}

server {
    location / {
        proxy_pass http://$backend_name;
    }
}
```
    """)


def monitoring_and_logging():
    """
    監控和日誌配置

    展示監控和日誌系統的配置
    """
    print("\n" + "=" * 80)
    print("示例 4: 監控和日誌")
    print("=" * 80)

    print("""
Prometheus 配置：
----------------

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # vLLM 服務監控
  - job_name: 'vllm'
    static_configs:
      - targets:
          - 'vllm-1:8000'
          - 'vllm-2:8000'
          - 'vllm-3:8000'
    metrics_path: '/metrics'

  # Node Exporter（系統指標）
  - job_name: 'node'
    static_configs:
      - targets:
          - 'node-exporter:9100'

  # GPU Exporter
  - job_name: 'gpu'
    static_configs:
      - targets:
          - 'gpu-exporter:9101'

  # Kubernetes 監控
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true

# 告警規則
rule_files:
  - '/etc/prometheus/rules/*.yml'
```

告警規則：
---------

```yaml
# alerts.yml
groups:
  - name: vllm_alerts
    interval: 30s
    rules:
      # 高延遲告警
      - alert: HighLatency
        expr: histogram_quantile(0.99, rate(vllm_request_latency_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "vLLM 高延遲"
          description: "P99 延遲超過 1 秒"

      # GPU 內存告警
      - alert: HighGPUMemory
        expr: (nvidia_gpu_memory_used_bytes / nvidia_gpu_memory_total_bytes) > 0.95
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "GPU 內存使用過高"
          description: "GPU 內存使用率超過 95%"

      # 服務不可用
      - alert: ServiceDown
        expr: up{job="vllm"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "vLLM 服務不可用"
          description: "{{ $labels.instance }} 已下線"

      # 錯誤率過高
      - alert: HighErrorRate
        expr: rate(vllm_requests_failed_total[5m]) / rate(vllm_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "錯誤率過高"
          description: "錯誤率超過 5%"
```

Grafana 儀表板：
---------------

關鍵面板:

1. 請求概覽
   - QPS (Queries Per Second)
   - 總請求數
   - 錯誤率

2. 延遲分布
   - P50/P90/P95/P99 延遲
   - 延遲熱力圖

3. 資源使用
   - GPU 利用率
   - GPU 內存使用
   - CPU 使用率
   - 系統內存

4. 吞吐量
   - Tokens/秒
   - 每請求 tokens 數

5. 模型性能
   - 首 token 延遲 (TTFT)
   - 每 token 延遲 (TPOT)

日誌配置：
---------

```yaml
# filebeat.yml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/vllm/*.log
    fields:
      service: vllm
      environment: production

  - type: docker
    containers.ids: '*'
    processors:
      - add_docker_metadata: ~

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "vllm-logs-%{+yyyy.MM.dd}"

setup.kibana:
  host: "kibana:5601"

setup.ilm:
  enabled: true
  rollover_alias: "vllm-logs"
  pattern: "{now/d}-000001"
  policy_name: "vllm-logs-policy"
```

應用日誌格式：
------------

```python
# logging_config.py
import logging
import json
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record['service'] = 'vllm'
        log_record['environment'] = 'production'
        log_record['timestamp'] = record.created

# 配置
logHandler = logging.StreamHandler()
formatter = CustomJsonFormatter(
    '%(timestamp)s %(level)s %(name)s %(message)s'
)
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# 使用
logger.info('Request processed', extra={
    'request_id': 'abc123',
    'latency_ms': 145,
    'tokens': 234,
    'model': 'llama-2-7b'
})
```

鏈路追蹤（Jaeger）：
------------------

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# 配置 Jaeger
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)

provider = TracerProvider()
processor = BatchSpanProcessor(jaeger_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

# 使用
with tracer.start_as_current_span("vllm_generate"):
    with tracer.start_as_current_span("model_forward"):
        output = llm.generate(prompt)
```
    """)


def security_and_best_practices():
    """
    安全性和最佳實踐

    展示安全配置和部署最佳實踐
    """
    print("\n" + "=" * 80)
    print("示例 5: 安全性和最佳實踐")
    print("=" * 80)

    print("""
安全配置：
---------

1. API 密鑰認證
```python
# auth_middleware.py
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

API_KEY = "your-secret-api-key"
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key
```

2. 速率限制
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/v1/chat/completions")
@limiter.limit("100/minute")
async def chat_completion(request: Request):
    pass
```

3. 輸入驗證
```python
from pydantic import BaseModel, validator

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    max_tokens: int = 100

    @validator('max_tokens')
    def check_max_tokens(cls, v):
        if v > 4096:
            raise ValueError('max_tokens 不能超過 4096')
        return v

    @validator('messages')
    def check_messages(cls, v):
        if len(v) > 100:
            raise ValueError('消息數量不能超過 100')
        return v
```

4. HTTPS/TLS
```bash
# 使用 Let's Encrypt
certbot --nginx -d llm.example.com

# 或使用自簽證書
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \\
    -keyout /etc/ssl/private/nginx-selfsigned.key \\
    -out /etc/ssl/certs/nginx-selfsigned.crt
```

5. 網絡隔離
```yaml
# Kubernetes NetworkPolicy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: vllm-network-policy
spec:
  podSelector:
    matchLabels:
      app: vllm
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: llm-serving
      ports:
        - protocol: TCP
          port: 8000
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              name: kube-system
```

部署最佳實踐：
------------

1. 資源限制
✓ 設置 CPU/內存 limits
✓ 設置 GPU 請求和限制
✓ 使用資源配額

2. 高可用
✓ 至少 3 個副本
✓ 跨可用區部署
✓ 健康檢查和自動重啟

3. 配置管理
✓ 使用 ConfigMap/Secret
✓ 環境變量隔離
✓ 版本控制

4. 備份和恢復
✓ 定期備份模型文件
✓ 配置備份
✓ 災難恢復計劃

5. CI/CD
```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - deploy

build:
  stage: build
  script:
    - docker build -t vllm-service:$CI_COMMIT_SHA .
    - docker push vllm-service:$CI_COMMIT_SHA

test:
  stage: test
  script:
    - pytest tests/
    - python benchmark.py

deploy-staging:
  stage: deploy
  script:
    - kubectl set image deployment/vllm-deployment \\
        vllm=vllm-service:$CI_COMMIT_SHA \\
        -n staging
  only:
    - develop

deploy-production:
  stage: deploy
  script:
    - kubectl set image deployment/vllm-deployment \\
        vllm=vllm-service:$CI_COMMIT_SHA \\
        -n production
  when: manual
  only:
    - main
```

6. 成本優化
✓ 使用 Spot/Preemptible 實例
✓ 自動擴縮容
✓ 量化模型
✓ 資源池共享

7. 文檔和培訓
✓ API 文檔
✓ 運維手冊
✓ 故障排查指南
✓ 團隊培訓

生產環境檢查清單：
----------------

部署前:
□ 性能基準測試完成
□ 安全審計通過
□ 負載測試通過
□ 備份策略就緒
□ 監控告警配置
□ 文檔完善

部署中:
□ 藍綠部署或金絲雀發布
□ 健康檢查驗證
□ 監控指標正常
□ 日誌收集正常

部署後:
□ 性能監控
□ 錯誤率監控
□ 用戶反饋收集
□ 定期回顧和優化
    """)


def main():
    """
    主函數：運行所有示例
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 25 + "vLLM 生產部署示例" + " " * 25 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    try:
        # 概覽
        deployment_overview()

        # 示例 1: Docker 部署
        docker_deployment()

        # 示例 2: Kubernetes 部署
        kubernetes_deployment()

        # 示例 3: 負載均衡
        load_balancing()

        # 示例 4: 監控日誌
        monitoring_and_logging()

        # 示例 5: 安全最佳實踐
        security_and_best_practices()

        print("\n" + "=" * 80)
        print("✓ 所有示例展示完成！")
        print("=" * 80)

        print("\n關鍵要點：")
        print("  1. 使用容器化部署提高可移植性")
        print("  2. Kubernetes 提供自動化運維能力")
        print("  3. 完善的監控是生產環境必備")
        print("  4. 安全性配置不可忽視")
        print("  5. 遵循最佳實踐確保穩定性")

        print("\n下一步：")
        print("  - 根據實際需求調整配置")
        print("  - 進行充分的測試")
        print("  - 制定詳細的運維計劃")
        print("  - 準備應急預案")
        print("  - 持續優化和改進")

    except KeyboardInterrupt:
        print("\n\n程序被用戶中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ 運行出錯: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
