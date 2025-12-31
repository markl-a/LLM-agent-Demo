"""
LiteLLM 生產部署範例

這個檔案展示如何將 LiteLLM 部署到生產環境：
1. Docker 容器化部署
2. Kubernetes 部署配置
3. 環境變數管理
4. 健康檢查和探針
5. 日誌和監控
6. 自動擴展配置
7. 備份和災難恢復
8. 安全最佳實踐
9. 效能優化
10. CI/CD 整合

生產環境部署需要考慮可靠性、安全性、可擴展性等多個面向。
"""

import os
import yaml
import json
from typing import Dict, List, Any, Optional
from pathlib import Path


# ============================================================================
# 第一部分：Docker 部署
# ============================================================================

def generate_dockerfile():
    """
    生成 Dockerfile

    建立一個生產級別的 Docker 映像檔配置。
    """
    print("=" * 80)
    print("生成 Dockerfile")
    print("=" * 80)

    dockerfile_content = """# LiteLLM 生產環境 Dockerfile
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY . .

# 建立非 root 使用者
RUN useradd -m -u 1000 litellm && \\
    chown -R litellm:litellm /app

USER litellm

# 暴露埠號
EXPOSE 4000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:4000/health')"

# 啟動命令
CMD ["litellm", "--config", "/app/config/production.yaml", "--port", "4000", "--num_workers", "4"]
"""

    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)

    print("✓ Dockerfile 已建立")
    print("\n內容預覽：")
    print(dockerfile_content)


def generate_docker_compose():
    """
    生成 docker-compose.yml

    包含 LiteLLM、Redis、PostgreSQL 等服務。
    """
    print("\n" + "=" * 80)
    print("生成 docker-compose.yml")
    print("=" * 80)

    docker_compose = {
        "version": "3.8",
        "services": {
            "litellm": {
                "build": ".",
                "ports": ["4000:4000"],
                "environment": {
                    "OPENAI_API_KEY": "${OPENAI_API_KEY}",
                    "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",
                    "DATABASE_URL": "postgresql://litellm:password@postgres:5432/litellm",
                    "REDIS_HOST": "redis",
                    "REDIS_PORT": "6379"
                },
                "volumes": [
                    "./config:/app/config:ro",
                    "./logs:/app/logs"
                ],
                "depends_on": [
                    "postgres",
                    "redis"
                ],
                "restart": "unless-stopped",
                "healthcheck": {
                    "test": ["CMD", "curl", "-f", "http://localhost:4000/health"],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3,
                    "start_period": "40s"
                }
            },

            "postgres": {
                "image": "postgres:15-alpine",
                "environment": {
                    "POSTGRES_DB": "litellm",
                    "POSTGRES_USER": "litellm",
                    "POSTGRES_PASSWORD": "password"
                },
                "volumes": [
                    "postgres_data:/var/lib/postgresql/data"
                ],
                "restart": "unless-stopped",
                "healthcheck": {
                    "test": ["CMD-SHELL", "pg_isready -U litellm"],
                    "interval": "10s",
                    "timeout": "5s",
                    "retries": 5
                }
            },

            "redis": {
                "image": "redis:7-alpine",
                "command": "redis-server --appendonly yes",
                "volumes": [
                    "redis_data:/data"
                ],
                "restart": "unless-stopped",
                "healthcheck": {
                    "test": ["CMD", "redis-cli", "ping"],
                    "interval": "10s",
                    "timeout": "5s",
                    "retries": 5
                }
            },

            "prometheus": {
                "image": "prom/prometheus:latest",
                "ports": ["9090:9090"],
                "volumes": [
                    "./prometheus.yml:/etc/prometheus/prometheus.yml:ro"
                ],
                "command": [
                    "--config.file=/etc/prometheus/prometheus.yml",
                    "--storage.tsdb.path=/prometheus"
                ],
                "restart": "unless-stopped"
            },

            "grafana": {
                "image": "grafana/grafana:latest",
                "ports": ["3000:3000"],
                "environment": {
                    "GF_SECURITY_ADMIN_PASSWORD": "admin"
                },
                "volumes": [
                    "grafana_data:/var/lib/grafana"
                ],
                "depends_on": ["prometheus"],
                "restart": "unless-stopped"
            }
        },

        "volumes": {
            "postgres_data": {},
            "redis_data": {},
            "grafana_data": {}
        }
    }

    with open("docker-compose.yml", "w") as f:
        yaml.dump(docker_compose, f, default_flow_style=False)

    print("✓ docker-compose.yml 已建立")
    print("\n服務列表：")
    for service in docker_compose["services"].keys():
        print(f"  • {service}")


# ============================================================================
# 第二部分：Kubernetes 部署
# ============================================================================

def generate_k8s_deployment():
    """
    生成 Kubernetes Deployment 配置
    """
    print("\n" + "=" * 80)
    print("生成 Kubernetes Deployment")
    print("=" * 80)

    deployment = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": "litellm",
            "labels": {
                "app": "litellm"
            }
        },
        "spec": {
            "replicas": 3,
            "selector": {
                "matchLabels": {
                    "app": "litellm"
                }
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app": "litellm"
                    }
                },
                "spec": {
                    "containers": [{
                        "name": "litellm",
                        "image": "litellm:latest",
                        "ports": [{
                            "containerPort": 4000
                        }],
                        "env": [
                            {
                                "name": "OPENAI_API_KEY",
                                "valueFrom": {
                                    "secretKeyRef": {
                                        "name": "litellm-secrets",
                                        "key": "openai-api-key"
                                    }
                                }
                            },
                            {
                                "name": "DATABASE_URL",
                                "valueFrom": {
                                    "secretKeyRef": {
                                        "name": "litellm-secrets",
                                        "key": "database-url"
                                    }
                                }
                            }
                        ],
                        "resources": {
                            "requests": {
                                "memory": "512Mi",
                                "cpu": "250m"
                            },
                            "limits": {
                                "memory": "1Gi",
                                "cpu": "500m"
                            }
                        },
                        "livenessProbe": {
                            "httpGet": {
                                "path": "/health",
                                "port": 4000
                            },
                            "initialDelaySeconds": 30,
                            "periodSeconds": 10
                        },
                        "readinessProbe": {
                            "httpGet": {
                                "path": "/health/ready",
                                "port": 4000
                            },
                            "initialDelaySeconds": 5,
                            "periodSeconds": 5
                        }
                    }]
                }
            }
        }
    }

    with open("k8s-deployment.yaml", "w") as f:
        yaml.dump(deployment, f, default_flow_style=False)

    print("✓ k8s-deployment.yaml 已建立")


def generate_k8s_service():
    """生成 Kubernetes Service 配置"""
    print("\n" + "=" * 80)
    print("生成 Kubernetes Service")
    print("=" * 80)

    service = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": "litellm-service",
            "labels": {
                "app": "litellm"
            }
        },
        "spec": {
            "type": "LoadBalancer",
            "selector": {
                "app": "litellm"
            },
            "ports": [{
                "protocol": "TCP",
                "port": 80,
                "targetPort": 4000
            }]
        }
    }

    with open("k8s-service.yaml", "w") as f:
        yaml.dump(service, f, default_flow_style=False)

    print("✓ k8s-service.yaml 已建立")


def generate_k8s_hpa():
    """生成 Horizontal Pod Autoscaler 配置"""
    print("\n" + "=" * 80)
    print("生成 Horizontal Pod Autoscaler")
    print("=" * 80)

    hpa = {
        "apiVersion": "autoscaling/v2",
        "kind": "HorizontalPodAutoscaler",
        "metadata": {
            "name": "litellm-hpa"
        },
        "spec": {
            "scaleTargetRef": {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "name": "litellm"
            },
            "minReplicas": 2,
            "maxReplicas": 10,
            "metrics": [
                {
                    "type": "Resource",
                    "resource": {
                        "name": "cpu",
                        "target": {
                            "type": "Utilization",
                            "averageUtilization": 70
                        }
                    }
                },
                {
                    "type": "Resource",
                    "resource": {
                        "name": "memory",
                        "target": {
                            "type": "Utilization",
                            "averageUtilization": 80
                        }
                    }
                }
            ]
        }
    }

    with open("k8s-hpa.yaml", "w") as f:
        yaml.dump(hpa, f, default_flow_style=False)

    print("✓ k8s-hpa.yaml 已建立")
    print("\n自動擴展配置：")
    print(f"  最小副本數：{hpa['spec']['minReplicas']}")
    print(f"  最大副本數：{hpa['spec']['maxReplicas']}")
    print(f"  CPU 目標：70%")
    print(f"  記憶體目標：80%")


# ============================================================================
# 第三部分：生產環境配置
# ============================================================================

def generate_production_config():
    """
    生成生產環境配置檔案
    """
    print("\n" + "=" * 80)
    print("生成生產環境配置")
    print("=" * 80)

    config = {
        # 模型列表
        "model_list": [
            {
                "model_name": "gpt-4",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "os.environ/OPENAI_API_KEY",
                    "rpm": 500,
                    "tpm": 100000
                },
                "model_info": {
                    "max_budget": 1000.0,
                    "budget_duration": "30d"
                }
            },
            {
                "model_name": "gpt-3.5",
                "litellm_params": {
                    "model": "gpt-3.5-turbo",
                    "api_key": "os.environ/OPENAI_API_KEY",
                    "rpm": 1000,
                    "tpm": 200000
                },
                "model_info": {
                    "max_budget": 500.0,
                    "budget_duration": "30d"
                }
            }
        ],

        # LiteLLM 設定
        "litellm_settings": {
            # 快取
            "cache": True,
            "cache_params": {
                "type": "redis",
                "host": "os.environ/REDIS_HOST",
                "port": "os.environ/REDIS_PORT",
                "ttl": 3600
            },

            # 回調
            "success_callback": ["langfuse", "prometheus"],
            "failure_callback": ["sentry", "slack"],

            # 超時和重試
            "request_timeout": 600,
            "num_retries": 3,
            "retry_delay": 2,

            # 日誌
            "set_verbose": True,
            "json_logs": True,

            # 速率限制
            "global_max_parallel_requests": 1000
        },

        # 一般設定
        "general_settings": {
            # 認證
            "master_key": "os.environ/LITELLM_MASTER_KEY",

            # 資料庫
            "database_url": "os.environ/DATABASE_URL",
            "store_model_in_db": True,

            # 虛擬金鑰
            "use_virtual_keys": True,

            # 安全
            "allowed_ips": [],
            "enable_cors": True,
            "cors_origins": ["*"]
        },

        # 路由器設定
        "router_settings": {
            "routing_strategy": "least-busy",
            "allowed_fails": 3,
            "cooldown_time": 60,
            "num_retries": 2
        }
    }

    # 建立配置目錄
    os.makedirs("config", exist_ok=True)

    with open("config/production.yaml", "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    print("✓ config/production.yaml 已建立")
    print("\n主要功能：")
    print("  • Redis 快取")
    print("  • Prometheus 監控")
    print("  • Sentry 錯誤追蹤")
    print("  • 速率限制和預算控制")
    print("  • 虛擬金鑰支援")


# ============================================================================
# 第四部分：監控配置
# ============================================================================

def generate_prometheus_config():
    """生成 Prometheus 配置"""
    print("\n" + "=" * 80)
    print("生成 Prometheus 配置")
    print("=" * 80)

    config = {
        "global": {
            "scrape_interval": "15s",
            "evaluation_interval": "15s"
        },
        "scrape_configs": [
            {
                "job_name": "litellm",
                "static_configs": [
                    {
                        "targets": ["litellm:4000"]
                    }
                ],
                "metrics_path": "/metrics"
            }
        ]
    }

    with open("prometheus.yml", "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    print("✓ prometheus.yml 已建立")


def generate_grafana_dashboard():
    """生成 Grafana 儀表板配置"""
    print("\n" + "=" * 80)
    print("生成 Grafana 儀表板")
    print("=" * 80)

    dashboard = {
        "dashboard": {
            "title": "LiteLLM Monitoring",
            "panels": [
                {
                    "title": "Requests per Second",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "rate(litellm_requests_total[5m])"
                        }
                    ]
                },
                {
                    "title": "Average Latency",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "rate(litellm_request_duration_seconds_sum[5m]) / rate(litellm_request_duration_seconds_count[5m])"
                        }
                    ]
                },
                {
                    "title": "Error Rate",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "rate(litellm_errors_total[5m])"
                        }
                    ]
                },
                {
                    "title": "Token Usage",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "rate(litellm_tokens_total[5m])"
                        }
                    ]
                }
            ]
        }
    }

    os.makedirs("grafana", exist_ok=True)

    with open("grafana/dashboard.json", "w") as f:
        json.dump(dashboard, f, indent=2)

    print("✓ grafana/dashboard.json 已建立")
    print("\n儀表板包含：")
    print("  • 每秒請求數")
    print("  • 平均延遲")
    print("  • 錯誤率")
    print("  • Token 使用量")


# ============================================================================
# 第五部分：CI/CD 配置
# ============================================================================

def generate_github_actions():
    """生成 GitHub Actions 工作流程"""
    print("\n" + "=" * 80)
    print("生成 GitHub Actions 工作流程")
    print("=" * 80)

    workflow = {
        "name": "Deploy LiteLLM",
        "on": {
            "push": {
                "branches": ["main", "production"]
            }
        },
        "jobs": {
            "test": {
                "runs-on": "ubuntu-latest",
                "steps": [
                    {
                        "name": "Checkout code",
                        "uses": "actions/checkout@v3"
                    },
                    {
                        "name": "Set up Python",
                        "uses": "actions/setup-python@v4",
                        "with": {
                            "python-version": "3.11"
                        }
                    },
                    {
                        "name": "Install dependencies",
                        "run": "pip install -r requirements.txt"
                    },
                    {
                        "name": "Run tests",
                        "run": "pytest tests/"
                    }
                ]
            },
            "build": {
                "needs": "test",
                "runs-on": "ubuntu-latest",
                "steps": [
                    {
                        "name": "Build Docker image",
                        "run": "docker build -t litellm:${{ github.sha }} ."
                    },
                    {
                        "name": "Push to registry",
                        "run": """
                            echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
                            docker tag litellm:${{ github.sha }} ${{ secrets.DOCKER_REGISTRY }}/litellm:latest
                            docker push ${{ secrets.DOCKER_REGISTRY }}/litellm:latest
                        """
                    }
                ]
            },
            "deploy": {
                "needs": "build",
                "runs-on": "ubuntu-latest",
                "if": "github.ref == 'refs/heads/production'",
                "steps": [
                    {
                        "name": "Deploy to Kubernetes",
                        "run": "kubectl apply -f k8s/"
                    }
                ]
            }
        }
    }

    os.makedirs(".github/workflows", exist_ok=True)

    with open(".github/workflows/deploy.yml", "w") as f:
        yaml.dump(workflow, f, default_flow_style=False)

    print("✓ .github/workflows/deploy.yml 已建立")
    print("\n工作流程：")
    print("  1. 測試")
    print("  2. 建立 Docker 映像")
    print("  3. 部署到 Kubernetes（僅 production 分支）")


# ============================================================================
# 第六部分：環境變數範本
# ============================================================================

def generate_env_template():
    """生成環境變數範本"""
    print("\n" + "=" * 80)
    print("生成環境變數範本")
    print("=" * 80)

    env_content = """# LiteLLM 生產環境變數範本

# API 金鑰
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
COHERE_API_KEY=...

# AWS 憑證（用於 Bedrock）
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION_NAME=us-east-1

# Azure OpenAI
AZURE_API_KEY=...
AZURE_API_BASE=https://...
AZURE_API_VERSION=2024-02-01

# LiteLLM 設定
LITELLM_MASTER_KEY=sk-master-...

# 資料庫
DATABASE_URL=postgresql://litellm:password@localhost:5432/litellm

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# 監控
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
SENTRY_DSN=...
SLACK_WEBHOOK_URL=...

# 其他
LOG_LEVEL=INFO
ENVIRONMENT=production
"""

    with open(".env.example", "w") as f:
        f.write(env_content)

    print("✓ .env.example 已建立")
    print("\n注意：")
    print("  1. 複製 .env.example 到 .env")
    print("  2. 填入實際的 API 金鑰和憑證")
    print("  3. 不要將 .env 提交到版本控制")


# ============================================================================
# 第七部分：部署腳本
# ============================================================================

def generate_deployment_scripts():
    """生成部署腳本"""
    print("\n" + "=" * 80)
    print("生成部署腳本")
    print("=" * 80)

    # Docker 部署腳本
    docker_deploy = """#!/bin/bash
# Docker 部署腳本

set -e

echo "🚀 開始部署 LiteLLM..."

# 檢查環境變數
if [ ! -f .env ]; then
    echo "❌ 錯誤：.env 檔案不存在"
    echo "請複製 .env.example 到 .env 並填入設定"
    exit 1
fi

# 拉取最新程式碼
echo "📥 拉取最新程式碼..."
git pull origin main

# 建立 Docker 映像
echo "🔨 建立 Docker 映像..."
docker-compose build

# 停止舊容器
echo "🛑 停止舊容器..."
docker-compose down

# 啟動新容器
echo "▶️  啟動新容器..."
docker-compose up -d

# 等待服務就緒
echo "⏳ 等待服務就緒..."
sleep 10

# 健康檢查
echo "🏥 執行健康檢查..."
if curl -f http://localhost:4000/health; then
    echo "✅ 部署成功！"
else
    echo "❌ 健康檢查失敗"
    docker-compose logs litellm
    exit 1
fi

echo "🎉 部署完成！"
"""

    with open("deploy-docker.sh", "w") as f:
        f.write(docker_deploy)
    os.chmod("deploy-docker.sh", 0o755)

    # Kubernetes 部署腳本
    k8s_deploy = """#!/bin/bash
# Kubernetes 部署腳本

set -e

echo "🚀 開始部署到 Kubernetes..."

# 檢查 kubectl 可用性
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl 未安裝"
    exit 1
fi

# 應用配置
echo "📝 應用配置..."
kubectl apply -f k8s-deployment.yaml
kubectl apply -f k8s-service.yaml
kubectl apply -f k8s-hpa.yaml

# 等待部署完成
echo "⏳ 等待部署完成..."
kubectl rollout status deployment/litellm

# 取得服務狀態
echo "📊 服務狀態："
kubectl get pods -l app=litellm
kubectl get svc litellm-service

echo "✅ 部署完成！"
"""

    with open("deploy-k8s.sh", "w") as f:
        f.write(k8s_deploy)
    os.chmod("deploy-k8s.sh", 0o755)

    print("✓ 部署腳本已建立：")
    print("  • deploy-docker.sh")
    print("  • deploy-k8s.sh")


# ============================================================================
# 第八部分：安全檢查清單
# ============================================================================

def generate_security_checklist():
    """生成安全檢查清單"""
    print("\n" + "=" * 80)
    print("生成安全檢查清單")
    print("=" * 80)

    checklist = """# LiteLLM 生產環境安全檢查清單

## API 金鑰管理
- [ ] 所有 API 金鑰都儲存在環境變數或密鑰管理服務中
- [ ] 沒有將 API 金鑰提交到版本控制
- [ ] 定期輪換 API 金鑰
- [ ] 使用最小權限原則

## 網路安全
- [ ] 啟用 HTTPS/TLS
- [ ] 配置防火牆規則
- [ ] 使用 VPC 或私有網路
- [ ] 限制來源 IP（如適用）

## 認證和授權
- [ ] 啟用虛擬金鑰系統
- [ ] 實施速率限制
- [ ] 設定預算上限
- [ ] 使用強密碼

## 資料保護
- [ ] 加密傳輸中的資料（TLS）
- [ ] 加密靜態資料
- [ ] 實施資料備份策略
- [ ] 定期測試災難恢復

## 監控和日誌
- [ ] 設定日誌收集
- [ ] 啟用錯誤追蹤（Sentry）
- [ ] 配置告警規則
- [ ] 定期審查日誌

## 合規性
- [ ] 遵守 GDPR/隱私法規
- [ ] 實施 PII 檢測和保護
- [ ] 記錄資料處理活動
- [ ] 定期進行安全審計

## 容器安全
- [ ] 使用最小化基礎映像
- [ ] 定期更新依賴
- [ ] 掃描容器漏洞
- [ ] 使用非 root 使用者執行

## Kubernetes 安全
- [ ] 設定 Pod 安全策略
- [ ] 使用 Network Policies
- [ ] 啟用 RBAC
- [ ] 定期更新集群

## 應用安全
- [ ] 實施輸入驗證
- [ ] 防止提示注入
- [ ] 過濾輸出內容
- [ ] 設定請求超時

## 運維安全
- [ ] 建立事件回應計劃
- [ ] 定期備份配置
- [ ] 文件化部署流程
- [ ] 進行滲透測試
"""

    with open("SECURITY_CHECKLIST.md", "w") as f:
        f.write(checklist)

    print("✓ SECURITY_CHECKLIST.md 已建立")


# ============================================================================
# 第九部分：部署文件
# ============================================================================

def generate_deployment_guide():
    """生成部署指南"""
    print("\n" + "=" * 80)
    print("生成部署指南")
    print("=" * 80)

    guide = """# LiteLLM 生產環境部署指南

## 前置需求

### 軟體需求
- Docker 20.10+
- Docker Compose 2.0+
- Kubernetes 1.24+（如使用 K8s）
- kubectl（如使用 K8s）

### API 金鑰
- OpenAI API Key
- Anthropic API Key（可選）
- 其他所需的 LLM 供應商金鑰

## 快速開始

### 1. 克隆倉庫
```bash
git clone https://github.com/your-org/litellm-deployment.git
cd litellm-deployment
```

### 2. 配置環境變數
```bash
cp .env.example .env
# 編輯 .env 並填入實際的 API 金鑰
```

### 3. 選擇部署方式

#### 選項 A：Docker Compose（推薦用於開發和小型部署）
```bash
./deploy-docker.sh
```

#### 選項 B：Kubernetes（推薦用於生產環境）
```bash
# 建立 secrets
kubectl create secret generic litellm-secrets \\
    --from-literal=openai-api-key=$OPENAI_API_KEY \\
    --from-literal=database-url=$DATABASE_URL

# 部署
./deploy-k8s.sh
```

## 驗證部署

### 健康檢查
```bash
curl http://localhost:4000/health
```

### 測試 API
```bash
curl -X POST http://localhost:4000/chat/completions \\
    -H "Authorization: Bearer your-api-key" \\
    -H "Content-Type: application/json" \\
    -d '{
        "model": "gpt-3.5",
        "messages": [{"role": "user", "content": "Hello"}]
    }'
```

## 監控

### Prometheus
訪問 http://localhost:9090 查看指標

### Grafana
訪問 http://localhost:3000 查看儀表板
- 預設使用者名稱：admin
- 預設密碼：admin

## 擴展

### 水平擴展（Docker Compose）
```bash
docker-compose up -d --scale litellm=3
```

### 水平擴展（Kubernetes）
```bash
kubectl scale deployment litellm --replicas=5
```

## 備份

### 資料庫備份
```bash
docker-compose exec postgres pg_dump -U litellm litellm > backup.sql
```

### 配置備份
```bash
tar -czf config-backup.tar.gz config/ .env
```

## 故障排除

### 查看日誌
```bash
# Docker
docker-compose logs -f litellm

# Kubernetes
kubectl logs -f deployment/litellm
```

### 常見問題

#### 1. 服務無法啟動
- 檢查環境變數是否正確設定
- 查看日誌中的錯誤訊息
- 確認所有依賴服務（PostgreSQL、Redis）正常運行

#### 2. API 請求失敗
- 驗證 API 金鑰是否有效
- 檢查網路連接
- 查看速率限制設定

#### 3. 效能問題
- 增加副本數量
- 調整資源限制
- 啟用快取

## 維護

### 更新部署
```bash
git pull origin main
./deploy-docker.sh  # 或 ./deploy-k8s.sh
```

### 查看資源使用
```bash
# Kubernetes
kubectl top pods
kubectl top nodes
```

## 安全

請參考 SECURITY_CHECKLIST.md 確保所有安全措施都已實施。

## 支援

如有問題，請：
1. 查看文件
2. 搜尋 GitHub Issues
3. 聯絡支援團隊
"""

    with open("DEPLOYMENT_GUIDE.md", "w") as f:
        f.write(guide)

    print("✓ DEPLOYMENT_GUIDE.md 已建立")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """主程式"""
    print("\n")
    print("=" * 80)
    print("LiteLLM 生產部署配置生成器")
    print("=" * 80)
    print()

    # 生成所有配置檔案
    print("開始生成生產環境配置檔案...\n")

    # Docker 相關
    generate_dockerfile()
    generate_docker_compose()

    # Kubernetes 相關
    generate_k8s_deployment()
    generate_k8s_service()
    generate_k8s_hpa()

    # 配置檔案
    generate_production_config()

    # 監控
    generate_prometheus_config()
    generate_grafana_dashboard()

    # CI/CD
    generate_github_actions()

    # 環境變數
    generate_env_template()

    # 部署腳本
    generate_deployment_scripts()

    # 安全和文件
    generate_security_checklist()
    generate_deployment_guide()

    print("\n" + "=" * 80)
    print("配置生成完成！")
    print("=" * 80)
    print("\n已生成的檔案：")
    print("  Docker:")
    print("    • Dockerfile")
    print("    • docker-compose.yml")
    print("  Kubernetes:")
    print("    • k8s-deployment.yaml")
    print("    • k8s-service.yaml")
    print("    • k8s-hpa.yaml")
    print("  配置:")
    print("    • config/production.yaml")
    print("  監控:")
    print("    • prometheus.yml")
    print("    • grafana/dashboard.json")
    print("  CI/CD:")
    print("    • .github/workflows/deploy.yml")
    print("  其他:")
    print("    • .env.example")
    print("    • deploy-docker.sh")
    print("    • deploy-k8s.sh")
    print("    • SECURITY_CHECKLIST.md")
    print("    • DEPLOYMENT_GUIDE.md")
    print("\n下一步：")
    print("  1. 閱讀 DEPLOYMENT_GUIDE.md")
    print("  2. 複製 .env.example 到 .env 並填入設定")
    print("  3. 執行部署腳本")
    print("  4. 查看 SECURITY_CHECKLIST.md 確保安全")
    print()


if __name__ == "__main__":
    main()
