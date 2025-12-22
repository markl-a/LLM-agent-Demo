"""
Rasa 部署上線 - 生產環境部署

本文件涵蓋：
1. Docker 部署
2. Kubernetes 部署
3. 通道整合（Slack, Telegram, Web）
4. 性能優化
5. 監控和日誌
"""

import os
import yaml


# ==================== 1. Docker 部署 ====================

def docker_deployment():
    """
    Docker 部署配置
    """
    print("=" * 60)
    print("Docker 部署")
    print("=" * 60)

    # Dockerfile for Rasa
    dockerfile_rasa = """
# Dockerfile
FROM rasa/rasa:3.6.0-full

# 切換工作目錄
WORKDIR /app

# 複製項目文件
COPY . /app

# 安裝中文支持
RUN pip install jieba

# 訓練模型
RUN rasa train

# 設置端口
EXPOSE 5005

# 啟動 Rasa server
CMD ["run", "--enable-api", "--cors", "*"]
"""

    print("\nDockerfile (Rasa Server):")
    print(dockerfile_rasa)

    # Dockerfile for Action Server
    dockerfile_actions = """
# Dockerfile.actions
FROM rasa/rasa-sdk:3.6.0

# 切換工作目錄
WORKDIR /app

# 複製 actions 文件
COPY ./actions /app/actions

# 安裝額外依賴
COPY requirements-actions.txt /app/
RUN pip install -r requirements-actions.txt

# 設置端口
EXPOSE 5055

# 啟動 Action Server
CMD ["start", "--actions", "actions"]
"""

    print("\nDockerfile.actions (Action Server):")
    print(dockerfile_actions)

    # docker-compose.yml
    docker_compose = """
# docker-compose.yml
version: '3.8'

services:
  # Rasa Server
  rasa:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "5005:5005"
    volumes:
      - ./models:/app/models
      - ./data:/app/data
    networks:
      - rasa-network
    environment:
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_USER=rasa
      - DB_PASSWORD=rasa
      - DB_DATABASE=rasa
    depends_on:
      - postgres
      - actions

  # Action Server
  actions:
    build:
      context: .
      dockerfile: Dockerfile.actions
    ports:
      - "5055:5055"
    networks:
      - rasa-network
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}

  # PostgreSQL (用於 Tracker Store)
  postgres:
    image: postgres:13
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=rasa
      - POSTGRES_PASSWORD=rasa
      - POSTGRES_DB=rasa
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - rasa-network

  # Redis (用於 Lock Store)
  redis:
    image: redis:6
    ports:
      - "6379:6379"
    networks:
      - rasa-network

  # Nginx (反向代理)
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    networks:
      - rasa-network
    depends_on:
      - rasa

volumes:
  postgres-data:

networks:
  rasa-network:
    driver: bridge
"""

    print("\ndocker-compose.yml:")
    print(docker_compose)

    # 部署命令
    print("\n部署命令:")
    print("""
# 構建並啟動所有服務
docker-compose up -d

# 查看日誌
docker-compose logs -f rasa

# 重新訓練模型
docker-compose exec rasa rasa train

# 停止服務
docker-compose down

# 清理並重啟
docker-compose down -v
docker-compose up -d --build
""")


# ==================== 2. Kubernetes 部署 ====================

def kubernetes_deployment():
    """
    Kubernetes 部署配置
    """
    print("\n" + "=" * 60)
    print("Kubernetes 部署")
    print("=" * 60)

    # Deployment for Rasa
    k8s_deployment = """
# k8s/rasa-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rasa-deployment
  labels:
    app: rasa
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rasa
  template:
    metadata:
      labels:
        app: rasa
    spec:
      containers:
      - name: rasa
        image: your-registry/rasa:latest
        ports:
        - containerPort: 5005
        env:
        - name: DB_HOST
          value: "postgres-service"
        - name: DB_PORT
          value: "5432"
        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: rasa-secrets
              key: db-user
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: rasa-secrets
              key: db-password
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /
            port: 5005
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 5005
          initialDelaySeconds: 10
          periodSeconds: 5

---
# Service for Rasa
apiVersion: v1
kind: Service
metadata:
  name: rasa-service
spec:
  selector:
    app: rasa
  ports:
  - protocol: TCP
    port: 5005
    targetPort: 5005
  type: LoadBalancer
"""

    print("\nKubernetes Deployment:")
    print(k8s_deployment)

    # Action Server Deployment
    k8s_actions = """
# k8s/actions-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: actions-deployment
  labels:
    app: actions
spec:
  replicas: 2
  selector:
    matchLabels:
      app: actions
  template:
    metadata:
      labels:
        app: actions
    spec:
      containers:
      - name: actions
        image: your-registry/rasa-actions:latest
        ports:
        - containerPort: 5055
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: rasa-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "1000m"

---
apiVersion: v1
kind: Service
metadata:
  name: actions-service
spec:
  selector:
    app: actions
  ports:
  - protocol: TCP
    port: 5055
    targetPort: 5055
"""

    print("\nActions Deployment:")
    print(k8s_actions)

    # 部署命令
    print("\n部署命令:")
    print("""
# 應用配置
kubectl apply -f k8s/

# 查看狀態
kubectl get pods
kubectl get services

# 查看日誌
kubectl logs -f deployment/rasa-deployment

# 擴展副本
kubectl scale deployment rasa-deployment --replicas=5

# 滾動更新
kubectl set image deployment/rasa-deployment rasa=your-registry/rasa:v2

# 刪除部署
kubectl delete -f k8s/
""")


# ==================== 3. 通道整合 ====================

def channel_integration():
    """
    通道整合配置
    """
    print("\n" + "=" * 60)
    print("通道整合")
    print("=" * 60)

    # credentials.yml
    credentials = """
# credentials.yml

# Web Widget
socketio:
  user_message_evt: user_uttered
  bot_message_evt: bot_uttered
  session_persistence: true

# REST API
rest:

# Slack
slack:
  slack_token: "xoxb-your-bot-token"
  slack_channel: "your-channel-id"
  slack_signing_secret: "your-signing-secret"

# Telegram
telegram:
  access_token: "your-telegram-bot-token"
  verify: "your-verify-token"
  webhook_url: "https://your-domain.com/webhooks/telegram/webhook"

# Facebook Messenger
facebook:
  verify: "your-verify-token"
  secret: "your-app-secret"
  page-access-token: "your-page-access-token"

# Line
line:
  channel_secret: "your-channel-secret"
  channel_access_token: "your-channel-access-token"

# Microsoft Bot Framework
botframework:
  app_id: "your-app-id"
  app_password: "your-app-password"
"""

    print("\ncredentials.yml:")
    print(credentials)

    # Web Chat Widget
    web_widget = """
<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Rasa Chatbot</title>
</head>
<body>
    <h1>客服機器人</h1>

    <!-- Rasa Webchat Widget -->
    <div id="rasa-chat-widget"></div>

    <script src="https://unpkg.com/@rasahq/rasa-chat"></script>
    <script>
        RasaChat.default.init({
            selector: "#rasa-chat-widget",
            initPayload: "/greet",
            customData: {"language": "zh"},
            socketUrl: "http://localhost:5005",
            title: "客服助手",
            subtitle: "有什麼可以幫您？",
            inputTextFieldHint: "輸入訊息...",
            connectingText: "連接中...",
            hideWhenNotConnected: false,
            fullScreenMode: false,
            showFullScreenButton: false,
            profileAvatar: "https://your-domain.com/avatar.png",
            openLauncherImage: "https://your-domain.com/launcher.png",
            params: {
                storage: "session"
            }
        });
    </script>
</body>
</html>
"""

    print("\nWeb Chat Widget:")
    print(web_widget)


# ==================== 4. 配置文件 ====================

def production_configuration():
    """
    生產環境配置
    """
    print("\n" + "=" * 60)
    print("生產環境配置")
    print("=" * 60)

    # endpoints.yml
    endpoints = """
# endpoints.yml

# Action Server
action_endpoint:
  url: "http://actions:5055/webhook"

# Tracker Store (PostgreSQL)
tracker_store:
  type: SQL
  dialect: postgresql
  host: postgres
  port: 5432
  db: rasa
  username: rasa
  password: rasa
  login_db: rasa

# Event Broker (Redis)
event_broker:
  type: redis
  url: redis
  port: 6379
  db: 0
  password: null

# Lock Store (Redis)
lock_store:
  type: redis
  url: redis
  port: 6379
  db: 1
  password: null

# Model Server (可選)
# model_endpoint:
#   url: "http://model-server:5000"
#   wait_time_between_pulls: 10
"""

    print("\nendpoints.yml:")
    print(endpoints)

    # Nginx 配置
    nginx_config = """
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream rasa {
        least_conn;
        server rasa:5005;
    }

    server {
        listen 80;
        server_name your-domain.com;

        # 重定向到 HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL 證書
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # SSL 配置
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # 限流
        limit_req_zone $binary_remote_addr zone=rasa:10m rate=10r/s;
        limit_req zone=rasa burst=20;

        # WebSocket 支持
        location /socket.io/ {
            proxy_pass http://rasa;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }

        # API 端點
        location /webhooks/ {
            proxy_pass http://rasa;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # 靜態文件
        location / {
            root /var/www/html;
            try_files $uri $uri/ /index.html;
        }
    }
}
"""

    print("\nnginx.conf:")
    print(nginx_config)


# ==================== 5. 性能優化 ====================

def performance_optimization():
    """
    性能優化建議
    """
    print("\n" + "=" * 60)
    print("性能優化")
    print("=" * 60)

    print("""
    【模型優化】
    1. 減少 epochs
       - 開發環境：50-100
       - 生產環境：100-200（根據性能測試）

    2. 使用較小的模型
       - DIETClassifier 而非多個分類器
       - 移除不必要的 Pipeline 組件

    3. 模型緩存
       - 避免重複加載模型
       - 使用持久化存儲

    【服務器配置】
    1. Worker 數量
       - CPU 密集型：CPU 核心數 + 1
       - IO 密集型：2 * CPU 核心數

    2. 內存配置
       - 最小：2 GB
       - 推薦：4-8 GB
       - 大模型：16+ GB

    3. 連接池
       - 數據庫連接池
       - Redis 連接池

    【緩存策略】
    1. NLU 結果緩存
       - 相同輸入緩存解析結果
       - TTL: 1 小時

    2. 響應緩存
       - 常見問題響應緩存
       - TTL: 24 小時

    3. 會話緩存
       - Redis 存儲活躍會話
       - TTL: 30 分鐘

    【數據庫優化】
    1. 索引
       - sender_id 索引
       - timestamp 索引

    2. 分區
       - 按時間分區對話歷史

    3. 定期清理
       - 清理過期會話
       - 歸檔歷史數據

    【負載均衡】
    1. 多個 Rasa 實例
    2. Sticky sessions（會話親和性）
    3. 健康檢查
    4. 自動擴展（K8s HPA）
    """)


# ==================== 6. 監控和日誌 ====================

def monitoring_and_logging():
    """
    監控和日誌配置
    """
    print("\n" + "=" * 60)
    print("監控和日誌")
    print("=" * 60)

    # Prometheus 配置
    prometheus_config = """
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'rasa'
    static_configs:
      - targets: ['rasa:5005']
    metrics_path: '/metrics'
"""

    print("\nPrometheus 配置:")
    print(prometheus_config)

    # 日誌配置
    logging_config = """
# logging.yml
version: 1
disable_existing_loggers: false

formatters:
  simple:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  detailed:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: simple
    stream: ext://sys.stdout

  file:
    class: logging.handlers.RotatingFileHandler
    level: DEBUG
    formatter: detailed
    filename: logs/rasa.log
    maxBytes: 10485760  # 10MB
    backupCount: 10

  error_file:
    class: logging.handlers.RotatingFileHandler
    level: ERROR
    formatter: detailed
    filename: logs/error.log
    maxBytes: 10485760
    backupCount: 5

root:
  level: INFO
  handlers: [console, file, error_file]

loggers:
  rasa:
    level: DEBUG
  actions:
    level: DEBUG
"""

    print("\n日誌配置:")
    print(logging_config)

    # 監控指標
    print("\n重要監控指標:")
    print("""
    【性能指標】
    - 響應時間（p50, p95, p99）
    - 吞吐量（requests/second）
    - 錯誤率
    - 可用性（uptime）

    【業務指標】
    - 對話數量
    - 意圖分布
    - 置信度分布
    - Fallback 率
    - 用戶滿意度

    【系統指標】
    - CPU 使用率
    - 內存使用率
    - 磁盤 I/O
    - 網絡流量
    - 數據庫連接數

    【告警設置】
    - 錯誤率 > 5%
    - 響應時間 > 2s
    - 可用性 < 99%
    - CPU > 80%
    - 內存 > 85%
    """)


# ==================== 7. CI/CD ====================

def cicd_pipeline():
    """
    CI/CD 流程
    """
    print("\n" + "=" * 60)
    print("CI/CD 流程")
    print("=" * 60)

    # GitHub Actions
    github_actions = """
# .github/workflows/deploy.yml
name: Deploy Rasa

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8

    - name: Install dependencies
      run: |
        pip install rasa
        pip install -r requirements.txt

    - name: Validate data
      run: rasa data validate

    - name: Train model
      run: rasa train

    - name: Test NLU
      run: rasa test nlu --nlu data/test/nlu.yml

    - name: Test Core
      run: rasa test core --stories data/test/stories.yml

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2

    - name: Build Docker image
      run: |
        docker build -t your-registry/rasa:${{ github.sha }} .
        docker build -t your-registry/rasa-actions:${{ github.sha }} -f Dockerfile.actions .

    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push your-registry/rasa:${{ github.sha }}
        docker push your-registry/rasa-actions:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/rasa-deployment rasa=your-registry/rasa:${{ github.sha }}
        kubectl set image deployment/actions-deployment actions=your-registry/rasa-actions:${{ github.sha }}
        kubectl rollout status deployment/rasa-deployment
"""

    print("\nGitHub Actions:")
    print(github_actions)


# ==================== 主程序 ====================

def main():
    """
    主程序
    """
    print("\n" + "=" * 70)
    print("Rasa 部署上線 - 完整指南")
    print("=" * 70)

    # 1. Docker
    docker_deployment()

    # 2. Kubernetes
    kubernetes_deployment()

    # 3. 通道整合
    channel_integration()

    # 4. 配置
    production_configuration()

    # 5. 性能優化
    performance_optimization()

    # 6. 監控
    monitoring_and_logging()

    # 7. CI/CD
    cicd_pipeline()

    # 總結
    print("\n" + "=" * 70)
    print("部署檢查清單")
    print("=" * 70)
    print("""
    □ 1. 數據驗證：rasa data validate
    □ 2. 模型訓練：rasa train
    □ 3. 模型測試：rasa test
    □ 4. Docker 構建：docker build
    □ 5. 環境變量：配置所有密鑰
    □ 6. 數據庫：PostgreSQL 設置
    □ 7. 緩存：Redis 設置
    □ 8. SSL 證書：HTTPS 配置
    □ 9. 負載均衡：Nginx/K8s
    □ 10. 監控：Prometheus + Grafana
    □ 11. 日誌：集中式日誌管理
    □ 12. 備份：定期備份模型和數據
    □ 13. 文檔：部署文檔和運維手冊
    □ 14. 測試：壓力測試和容錯測試

    【下一步】
    學習 09_客服機器人.py - 完整的客服系統實現
    """)


if __name__ == "__main__":
    main()
