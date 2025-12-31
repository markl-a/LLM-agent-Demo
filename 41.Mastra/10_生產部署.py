"""
Mastra 生產部署指南

本示例展示如何將 Mastra 應用部署到生產環境。

功能：
1. 部署架構設計
2. 容器化和編排
3. 擴展策略
4. 安全配置
5. CI/CD 流程
"""

import os
import json
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()


def example_1_deployment_architecture():
    """示例 1：部署架構"""
    print("=" * 60)
    print("示例 1：生產部署架構")
    print("=" * 60)

    architecture = {
        'components': {
            'load_balancer': {
                'type': 'AWS ALB / NGINX',
                'purpose': '流量分發和 SSL 終止',
                'config': {
                    'ssl': True,
                    'health_check': '/health',
                    'algorithm': 'least_connections'
                }
            },
            'api_servers': {
                'type': 'Node.js / TypeScript',
                'replicas': 3,
                'resources': {
                    'cpu': '2 cores',
                    'memory': '4 GB',
                    'storage': '20 GB'
                },
                'auto_scaling': {
                    'min': 3,
                    'max': 10,
                    'target_cpu': '70%'
                }
            },
            'database': {
                'primary': {
                    'type': 'PostgreSQL 15',
                    'size': 'db.r5.xlarge',
                    'storage': '100 GB SSD',
                    'backups': 'daily'
                },
                'replica': {
                    'count': 2,
                    'lag': '< 1s'
                }
            },
            'cache': {
                'type': 'Redis Cluster',
                'nodes': 3,
                'memory': '16 GB per node',
                'persistence': 'AOF + RDB'
            },
            'vector_database': {
                'type': 'Pinecone / Weaviate',
                'index_size': '1M vectors',
                'dimensions': 1536,
                'replicas': 2
            },
            'message_queue': {
                'type': 'RabbitMQ / AWS SQS',
                'purpose': '異步任務處理',
                'queues': ['llm-requests', 'notifications', 'analytics']
            },
            'storage': {
                'type': 'S3 / MinIO',
                'purpose': '文件和備份存儲',
                'lifecycle': {
                    'hot': '30d',
                    'cold': '90d',
                    'archive': '365d'
                }
            }
        },
        'network': {
            'vpc': {
                'cidr': '10.0.0.0/16',
                'subnets': {
                    'public': ['10.0.1.0/24', '10.0.2.0/24'],
                    'private': ['10.0.10.0/24', '10.0.11.0/24'],
                    'database': ['10.0.20.0/24', '10.0.21.0/24']
                }
            },
            'security_groups': {
                'alb': {
                    'inbound': ['80/tcp:0.0.0.0/0', '443/tcp:0.0.0.0/0'],
                    'outbound': ['all']
                },
                'api': {
                    'inbound': ['3000/tcp:alb-sg'],
                    'outbound': ['all']
                },
                'database': {
                    'inbound': ['5432/tcp:api-sg'],
                    'outbound': ['none']
                }
            }
        }
    }

    print(f"\n架構配置: {json.dumps(architecture, indent=2, ensure_ascii=False)}")

    print("\n架構圖:")
    print("""
    ┌─────────────────────────────────────────────────┐
    │                   Internet                       │
    └────────────────────┬────────────────────────────┘
                         │
                         ▼
    ┌─────────────────────────────────────────────────┐
    │              Load Balancer (ALB)                 │
    │         SSL Termination, Health Checks           │
    └─────────┬──────────┬──────────┬──────────────────┘
              │          │          │
              ▼          ▼          ▼
    ┌─────────────┬─────────────┬─────────────┐
    │  API Server │  API Server │  API Server │
    │  (Node.js)  │  (Node.js)  │  (Node.js)  │
    └─────┬───────┴──────┬──────┴──────┬──────┘
          │              │             │
          └──────┬───────┴─────┬───────┘
                 │             │
        ┌────────▼──────┐ ┌───▼─────────┐
        │   PostgreSQL  │ │    Redis    │
        │   (Primary)   │ │   Cluster   │
        │               │ │             │
        │   ┌─────────┐ │ └─────────────┘
        │   │ Replica │ │
        │   │ Replica │ │
        │   └─────────┘ │
        └───────────────┘
                 │
        ┌────────▼──────────┐
        │  Vector Database  │
        │   (Pinecone)      │
        └───────────────────┘
    """)


def example_2_containerization():
    """示例 2：容器化配置"""
    print("\n" + "=" * 60)
    print("示例 2：Docker 容器化")
    print("=" * 60)

    # Dockerfile 示例
    dockerfile = '''
# Multi-stage build for Mastra application

# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# Install dependencies
RUN npm ci --only=production && \\
    npm cache clean --force

# Copy source code
COPY src ./src

# Build TypeScript
RUN npm run build

# Stage 2: Production
FROM node:20-alpine

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \\
    adduser -S nodejs -u 1001

WORKDIR /app

# Copy built artifacts from builder
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/package*.json ./

# Switch to non-root user
USER nodejs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD node healthcheck.js

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Start application
CMD ["node", "dist/main.js"]
'''

    # docker-compose.yml 示例
    docker_compose = '''
version: '3.8'

services:
  mastra-api:
    image: mastra/api:latest
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://user:pass@postgres:5432/mastra
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=mastra
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=mastra
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - mastra-api
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
'''

    print("Dockerfile:")
    print(dockerfile)
    print("\ndocker-compose.yml:")
    print(docker_compose)


def example_3_kubernetes_deployment():
    """示例 3：Kubernetes 部署"""
    print("\n" + "=" * 60)
    print("示例 3：Kubernetes 配置")
    print("=" * 60)

    # Kubernetes Deployment
    k8s_deployment = '''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mastra-api
  namespace: production
  labels:
    app: mastra-api
    version: v1.0.0
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: mastra-api
  template:
    metadata:
      labels:
        app: mastra-api
        version: v1.0.0
    spec:
      serviceAccountName: mastra-api
      containers:
      - name: mastra-api
        image: your-registry/mastra-api:1.0.0
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 3000
          name: http
        env:
        - name: NODE_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: mastra-secrets
              key: database-url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: mastra-secrets
              key: openai-api-key
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
          failureThreshold: 2
---
apiVersion: v1
kind: Service
metadata:
  name: mastra-api
  namespace: production
spec:
  type: ClusterIP
  selector:
    app: mastra-api
  ports:
  - port: 80
    targetPort: 3000
    protocol: TCP
    name: http
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: mastra-api-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: mastra-api
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
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Pods
        value: 1
        periodSeconds: 60
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mastra-api
  namespace: production
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - api.mastra.example.com
    secretName: mastra-tls
  rules:
  - host: api.mastra.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: mastra-api
            port:
              number: 80
'''

    print("Kubernetes 配置:")
    print(k8s_deployment)


def example_4_cicd_pipeline():
    """示例 4：CI/CD 流程"""
    print("\n" + "=" * 60)
    print("示例 4：CI/CD 流程")
    print("=" * 60)

    # GitHub Actions workflow
    github_actions = '''
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint

      - name: Run type check
        run: npm run type-check

      - name: Run tests
        run: npm test -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment:
      name: staging
      url: https://staging.mastra.example.com
    steps:
      - name: Deploy to staging
        run: |
          # 部署到 staging 環境
          kubectl set image deployment/mastra-api \\
            mastra-api=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \\
            -n staging

      - name: Wait for rollout
        run: |
          kubectl rollout status deployment/mastra-api -n staging

      - name: Run smoke tests
        run: |
          npm run test:smoke -- --env staging

  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://api.mastra.example.com
    steps:
      - name: Deploy to production
        run: |
          kubectl set image deployment/mastra-api \\
            mastra-api=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \\
            -n production

      - name: Wait for rollout
        run: |
          kubectl rollout status deployment/mastra-api -n production

      - name: Run smoke tests
        run: |
          npm run test:smoke -- --env production

      - name: Notify team
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Production deployment: ${{ job.status }}'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
'''

    print("GitHub Actions Workflow:")
    print(github_actions)

    print("\n\n部署流程:")
    print("""
    1. 代碼提交
       ↓
    2. 自動化測試
       ├─ 單元測試
       ├─ 集成測試
       ├─ Linting
       └─ 類型檢查
       ↓
    3. 構建 Docker 鏡像
       ├─ 多階段構建
       ├─ 安全掃描
       └─ 推送到 Registry
       ↓
    4. 部署到 Staging
       ├─ 滾動更新
       ├─ 煙霧測試
       └─ 性能測試
       ↓
    5. 人工審核（可選）
       ↓
    6. 部署到 Production
       ├─ 藍綠部署
       ├─ 金絲雀發布
       └─ 監控和驗證
       ↓
    7. 完成
       └─ 團隊通知
    """)


def example_5_security_configuration():
    """示例 5：安全配置"""
    print("\n" + "=" * 60)
    print("示例 5：安全配置和最佳實踐")
    print("=" * 60)

    security_config = {
        'authentication': {
            'jwt': {
                'algorithm': 'RS256',
                'expiration': '1h',
                'refresh_token_expiration': '7d',
                'issuer': 'mastra-api',
                'audience': 'mastra-clients'
            },
            'api_keys': {
                'format': 'mastra_live_xxxxxxxxxxxxxxxx',
                'rotation_policy': '90d',
                'rate_limit': '1000/hour'
            },
            'oauth2': {
                'providers': ['google', 'github'],
                'scopes': ['openid', 'profile', 'email']
            }
        },
        'authorization': {
            'rbac': {
                'roles': [
                    {
                        'name': 'admin',
                        'permissions': ['*']
                    },
                    {
                        'name': 'developer',
                        'permissions': [
                            'agents:read',
                            'agents:write',
                            'workflows:read',
                            'workflows:write'
                        ]
                    },
                    {
                        'name': 'viewer',
                        'permissions': [
                            'agents:read',
                            'workflows:read',
                            'logs:read'
                        ]
                    }
                ]
            }
        },
        'encryption': {
            'data_at_rest': {
                'database': 'AES-256-GCM',
                'storage': 'S3 SSE-KMS'
            },
            'data_in_transit': {
                'tls_version': '1.3',
                'cipher_suites': [
                    'TLS_AES_256_GCM_SHA384',
                    'TLS_CHACHA20_POLY1305_SHA256'
                ]
            },
            'secrets': {
                'provider': 'AWS Secrets Manager',
                'rotation': 'automatic',
                'access_audit': True
            }
        },
        'network_security': {
            'firewall': {
                'default_policy': 'deny',
                'allowed_ips': ['cloudflare', 'office-network'],
                'rate_limiting': {
                    'requests_per_minute': 100,
                    'burst': 200
                }
            },
            'waf': {
                'enabled': True,
                'rules': [
                    'SQL injection protection',
                    'XSS protection',
                    'CSRF protection',
                    'Rate limiting'
                ]
            },
            'ddos_protection': {
                'provider': 'Cloudflare',
                'mode': 'always_on'
            }
        },
        'input_validation': {
            'sanitization': True,
            'content_filter': {
                'enabled': True,
                'block_malicious_content': True,
                'pii_detection': True
            },
            'max_request_size': '10MB',
            'timeout': '30s'
        },
        'audit_logging': {
            'enabled': True,
            'events': [
                'authentication',
                'authorization',
                'data_access',
                'configuration_changes'
            ],
            'retention': '7y',
            'immutable': True
        },
        'security_headers': {
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'X-Frame-Options': 'DENY',
            'X-Content-Type-Options': 'nosniff',
            'X-XSS-Protection': '1; mode=block',
            'Content-Security-Policy': "default-src 'self'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
    }

    print(f"\n安全配置: {json.dumps(security_config, indent=2, ensure_ascii=False)}")


def example_6_backup_disaster_recovery():
    """示例 6：備份和災難恢復"""
    print("\n" + "=" * 60)
    print("示例 6：備份和災難恢復")
    print("=" * 60)

    dr_plan = {
        'backup_strategy': {
            'database': {
                'full_backup': {
                    'frequency': 'daily',
                    'time': '02:00 UTC',
                    'retention': '30 days'
                },
                'incremental_backup': {
                    'frequency': 'every 6 hours',
                    'retention': '7 days'
                },
                'point_in_time_recovery': {
                    'enabled': True,
                    'retention': '7 days'
                }
            },
            'vector_database': {
                'snapshot': {
                    'frequency': 'daily',
                    'retention': '14 days'
                },
                'replication': {
                    'enabled': True,
                    'regions': ['us-east-1', 'eu-west-1']
                }
            },
            'configuration': {
                'version_control': 'git',
                'backup_frequency': 'on_change',
                'retention': 'unlimited'
            }
        },
        'disaster_recovery': {
            'rto': '4 hours',  # Recovery Time Objective
            'rpo': '1 hour',   # Recovery Point Objective
            'multi_region': {
                'primary': 'us-east-1',
                'secondary': 'eu-west-1',
                'failover': 'automatic'
            },
            'recovery_procedures': [
                {
                    'step': 1,
                    'action': '檢測故障',
                    'automation': 'health checks + monitoring'
                },
                {
                    'step': 2,
                    'action': '切換到備用區域',
                    'automation': 'DNS failover + load balancer'
                },
                {
                    'step': 3,
                    'action': '恢復數據庫',
                    'automation': 'automated restore from backup'
                },
                {
                    'step': 4,
                    'action': '驗證服務',
                    'automation': 'smoke tests'
                },
                {
                    'step': 5,
                    'action': '通知團隊',
                    'automation': 'PagerDuty + Slack'
                }
            ]
        },
        'testing': {
            'frequency': 'quarterly',
            'scenarios': [
                'database failure',
                'region outage',
                'data corruption',
                'security breach'
            ],
            'documentation': 'runbooks updated after each test'
        }
    }

    print(f"\n災難恢復計劃: {json.dumps(dr_plan, indent=2, ensure_ascii=False)}")


def example_7_performance_optimization():
    """示例 7：性能優化"""
    print("\n" + "=" * 60)
    print("示例 7：生產環境性能優化")
    print("=" * 60)

    performance_tips = '''
    🚀 性能優化策略

    1. 緩存策略
       ✅ LLM 響應緩存（基於 prompt hash）
       ✅ 向量搜索結果緩存
       ✅ API 響應緩存（HTTP Cache-Control）
       ✅ CDN 靜態資源緩存

       實現:
       - Redis 作為主緩存
       - TTL: 1小時到7天
       - 緩存失效策略: LRU
       - 緩存預熱（常見查詢）

    2. 數據庫優化
       ✅ 索引優化（查詢分析）
       ✅ 連接池（pg: 20-50 連接）
       ✅ 查詢優化（避免 N+1）
       ✅ 讀寫分離（主從複製）
       ✅ 分區和分片（大表）

    3. API 優化
       ✅ 響應壓縮（gzip/brotli）
       ✅ 批量 API（減少往返）
       ✅ GraphQL/字段選擇
       ✅ 分頁和游標
       ✅ 限流和配額

    4. LLM 調用優化
       ✅ 批量處理請求
       ✅ 流式響應（SSE）
       ✅ prompt 優化（減少 tokens）
       ✅ 模型選擇（根據任務複雜度）
       ✅ 並行調用（獨立任務）

    5. 向量搜索優化
       ✅ 使用 HNSW 索引
       ✅ 量化（降低內存）
       ✅ 預過濾（元數據）
       ✅ 批量嵌入生成

    6. 代碼優化
       ✅ 異步處理（Promise.all）
       ✅ 避免阻塞操作
       ✅ 使用 worker threads
       ✅ 內存優化（避免泄漏）
       ✅ 代碼分割和懶加載

    7. 網絡優化
       ✅ HTTP/2 或 HTTP/3
       ✅ Keep-Alive 連接
       ✅ DNS 預解析
       ✅ 負載均衡

    8. 監控和持續優化
       ✅ APM 工具（識別瓶頸）
       ✅ 定期性能測試
       ✅ A/B 測試優化
       ✅ 用戶體驗監控

    性能目標:
    • P50 延遲: < 500ms
    • P95 延遲: < 2s
    • P99 延遲: < 5s
    • 吞吐量: > 1000 req/s
    • 可用性: 99.9%
    '''

    print(performance_tips)


def example_8_scaling_strategy():
    """示例 8：擴展策略"""
    print("\n" + "=" * 60)
    print("示例 8：水平和垂直擴展")
    print("=" * 60)

    scaling_strategy = {
        'horizontal_scaling': {
            'description': '添加更多實例',
            'when_to_use': [
                'CPU 使用率持續 > 70%',
                '請求隊列積壓',
                '響應時間增加'
            ],
            'implementation': {
                'auto_scaling': {
                    'enabled': True,
                    'min_instances': 3,
                    'max_instances': 20,
                    'metrics': [
                        {
                            'type': 'cpu',
                            'target': 70,
                            'scale_up_threshold': 75,
                            'scale_down_threshold': 30
                        },
                        {
                            'type': 'memory',
                            'target': 80
                        },
                        {
                            'type': 'request_count',
                            'target': 1000,
                            'per': 'instance'
                        }
                    ],
                    'cooldown': {
                        'scale_up': '60s',
                        'scale_down': '300s'
                    }
                },
                'load_balancing': {
                    'algorithm': 'least_connections',
                    'health_check': {
                        'interval': '30s',
                        'timeout': '5s',
                        'unhealthy_threshold': 3
                    }
                }
            },
            'considerations': [
                '無狀態服務設計',
                '共享緩存（Redis）',
                '會話親和性（如需要）',
                '一致性處理'
            ]
        },
        'vertical_scaling': {
            'description': '增加實例資源',
            'when_to_use': [
                '內存密集型操作',
                '單個請求需要更多資源',
                '數據庫連接限制'
            ],
            'tiers': [
                {
                    'name': 'small',
                    'cpu': '1 core',
                    'memory': '2 GB',
                    'use_case': '開發/測試'
                },
                {
                    'name': 'medium',
                    'cpu': '2 cores',
                    'memory': '4 GB',
                    'use_case': '小型生產'
                },
                {
                    'name': 'large',
                    'cpu': '4 cores',
                    'memory': '8 GB',
                    'use_case': '中型生產'
                },
                {
                    'name': 'xlarge',
                    'cpu': '8 cores',
                    'memory': '16 GB',
                    'use_case': '大型生產'
                }
            ],
            'considerations': [
                '停機時間（通常需要重啟）',
                '成本增加',
                '單點故障風險',
                '擴展上限'
            ]
        },
        'database_scaling': {
            'read_replicas': {
                'count': 2,
                'purpose': '分散讀取負載',
                'lag_tolerance': '< 1s'
            },
            'connection_pooling': {
                'enabled': True,
                'pool_size': 20,
                'max_overflow': 10
            },
            'sharding': {
                'strategy': 'by_tenant_id',
                'shards': 4,
                'when': 'DB size > 500GB'
            }
        },
        'caching_layer': {
            'redis_cluster': {
                'nodes': 3,
                'memory_per_node': '16 GB',
                'eviction_policy': 'allkeys-lru'
            },
            'cdn': {
                'provider': 'Cloudflare',
                'cache_everything': False,
                'edge_caching': True
            }
        }
    }

    print(f"\n擴展策略: {json.dumps(scaling_strategy, indent=2, ensure_ascii=False)}")


def example_9_cost_optimization():
    """示例 9：成本優化"""
    print("\n" + "=" * 60)
    print("示例 9：生產成本優化")
    print("=" * 60)

    cost_optimization = '''
    💰 成本優化策略

    1. LLM 成本優化
       ✅ 智能模型選擇
          - 簡單任務: gpt-3.5-turbo ($0.001/1K tokens)
          - 複雜任務: gpt-4 ($0.03/1K tokens)
       ✅ Prompt 工程
          - 減少不必要的 tokens
          - 使用更短的指令
          - 避免重複上下文
       ✅ 緩存策略
          - 緩存常見查詢結果
          - 相似查詢去重
          - TTL 設置合理
       ✅ 批量處理
          - 合併相似請求
          - 批量 embeddings 生成

       估算:
       • 10K 請求/天
       • 平均 500 tokens/請求
       • gpt-4: $150/天 → gpt-3.5: $7.5/天
       • 節省: 95%

    2. 基礎設施成本
       ✅ 自動伸縮
          - 根據流量自動調整
          - 夜間縮減實例
       ✅ Spot/Preemptible 實例
          - 非關鍵工作負載
          - 節省 60-90%
       ✅ 保留實例/承諾使用
          - 長期穩定負載
          - 節省 30-50%
       ✅ 多區域優化
          - 選擇成本較低的區域
          - 網絡流量優化

    3. 數據存儲成本
       ✅ 生命週期管理
          - 熱數據: SSD (30天)
          - 溫數據: Standard (90天)
          - 冷數據: Archive (1年+)
       ✅ 壓縮
          - 日誌壓縮
          - 備份壓縮
       ✅ 去重
          - 向量去重
          - 數據去重

    4. 網絡成本
       ✅ CDN 使用
          - 靜態資源
          - API 響應（可緩存）
       ✅ 區域間流量最小化
          - 數據本地化
          - 智能路由

    5. 監控成本
       ✅ 採樣
          - 日誌採樣（10%）
          - Trace 採樣（5%）
       ✅ 保留策略
          - 短期: 詳細日誌（7天）
          - 長期: 聚合指標（1年）

    成本監控儀表板:
    ┌─────────────────────────────────────┐
    │ 月度成本預估: $5,234                 │
    ├─────────────────────────────────────┤
    │ LLM API:        $3,200 (61%)        │
    │ 計算:           $1,200 (23%)        │
    │ 數據庫:           $450 (9%)         │
    │ 存儲:             $234 (4%)         │
    │ 網絡:             $100 (2%)         │
    │ 其他:              $50 (1%)         │
    └─────────────────────────────────────┘

    優化建議:
    • 使用 gpt-3.5-turbo 可節省 $1,500/月
    • 實現緩存可減少 30% LLM 調用
    • Spot 實例可節省 $400/月
    '''

    print(cost_optimization)


def example_10_deployment_checklist():
    """示例 10：部署檢查清單"""
    print("\n" + "=" * 60)
    print("示例 10：生產部署檢查清單")
    print("=" * 60)

    checklist = '''
    ✅ 生產部署檢查清單

    📋 部署前檢查

    代碼質量:
    □ 所有測試通過（單元、集成、E2E）
    □ 代碼審查完成
    □ 測試覆蓋率 > 80%
    □ 無已知的高/中危安全漏洞
    □ 性能測試通過
    □ 文檔已更新

    環境配置:
    □ 環境變量已設置
    □ 密鑰已輪換並安全存儲
    □ 資源配額已設置
    □ 速率限制已配置
    □ 備份策略已啟用

    基礎設施:
    □ 負載均衡器配置正確
    □ 自動伸縮規則已設置
    □ 健康檢查已配置
    □ SSL 證書有效
    □ DNS 記錄正確
    □ 防火牆規則已審查

    監控和告警:
    □ 日誌收集已啟用
    □ 指標收集已配置
    □ 追蹤已啟用
    □ 告警規則已設置
    □ On-call 輪值已安排
    □ Runbooks 已準備

    安全:
    □ 身份驗證已啟用
    □ 授權策略已實施
    □ 數據加密（傳輸和靜態）
    □ 安全頭已設置
    □ WAF 已配置
    □ DDoS 防護已啟用
    □ 審計日誌已啟用

    數據:
    □ 數據庫遷移已測試
    □ 備份已驗證
    □ 恢復流程已測試
    □ 數據一致性已檢查

    📋 部署期間

    □ 通知團隊部署開始
    □ 執行部署前備份
    □ 滾動部署（零停機）
    □ 監控部署進度
    □ 檢查健康狀態
    □ 運行煙霧測試
    □ 驗證關鍵功能

    📋 部署後檢查

    立即檢查（0-15 分鐘）:
    □ 所有服務健康
    □ 無錯誤日誌
    □ 響應時間正常
    □ 核心功能工作
    □ 集成正常
    □ 監控數據流入

    短期檢查（1-24 小時）:
    □ 錯誤率在正常範圍
    □ 性能指標穩定
    □ 無內存泄漏
    □ 資源使用正常
    □ 用戶反饋正面
    □ 成本在預算內

    長期檢查（1-7 天）:
    □ 系統穩定性
    □ 擴展性驗證
    □ 備份成功
    □ 無安全事件
    □ 成本趨勢正常

    📋 回滾計劃

    觸發條件:
    □ 錯誤率 > 5%
    □ P95 延遲 > 5s
    □ 關鍵功能失敗
    □ 安全漏洞發現
    □ 數據完整性問題

    回滾步驟:
    1. 暫停新部署
    2. 通知團隊
    3. 執行回滾腳本
    4. 驗證舊版本
    5. 調查根本原因
    6. 修復並重新部署

    📋 溝通

    部署前:
    □ 通知利益相關者
    □ 更新狀態頁面
    □ 準備公告

    部署期間:
    □ 實時更新狀態
    □ 團隊在線待命

    部署後:
    □ 宣布成功/問題
    □ 更新變更日誌
    □ 收集反饋

    📋 文檔

    □ 部署筆記已記錄
    □ 問題已記錄
    □ 學習點已總結
    □ Runbooks 已更新
    □ 架構文檔已更新
    '''

    print(checklist)


def main():
    """主函數"""
    print("\n🚀 Mastra 生產部署指南\n")

    try:
        example_1_deployment_architecture()
        example_2_containerization()
        example_3_kubernetes_deployment()
        example_4_cicd_pipeline()
        example_5_security_configuration()
        example_6_backup_disaster_recovery()
        example_7_performance_optimization()
        example_8_scaling_strategy()
        example_9_cost_optimization()
        example_10_deployment_checklist()

        print("\n" + "=" * 60)
        print("✅ 所有示例運行完成！")
        print("=" * 60)
        print("\n📚 相關資源:")
        print("  • Mastra 官方文檔: https://docs.mastra.ai")
        print("  • GitHub: https://github.com/mastra-ai/mastra")
        print("  • 社群: https://discord.gg/mastra")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")


if __name__ == "__main__":
    main()
