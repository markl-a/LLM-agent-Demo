"""
Google ADK - 部署上線範例

這個範例展示生產環境部署：
- Docker 容器化
- Kubernetes 部署
- Cloud Run 部署
- 監控和日誌
- CI/CD 流程
"""

import os
from typing import Optional, Dict, Any
import yaml
import json
from google_adk import Agent
from google_adk.models import GeminiPro
from google_adk.deployment import (
    DockerBuilder,
    KubernetesDeployer,
    CloudRunDeployer
)


class DeploymentExample:
    """部署上線範例類"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化部署範例"""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

    def example_1_dockerfile(self):
        """範例 1: 創建 Dockerfile"""
        print("\n" + "="*60)
        print("範例 1: 創建 Dockerfile")
        print("="*60)

        dockerfile_content = """# Google ADK Agent Dockerfile
FROM python:3.11-slim

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# 複製依賴文件
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY . .

# 設置環境變量
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# 健康檢查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:${PORT}/health || exit 1

# 暴露端口
EXPOSE ${PORT}

# 運行應用
CMD ["python", "app.py"]
"""

        print("Dockerfile 內容:")
        print(dockerfile_content)

        # Docker 構建命令
        build_commands = """
# 構建 Docker 映像
docker build -t google-adk-agent:latest .

# 標記版本
docker tag google-adk-agent:latest gcr.io/${PROJECT_ID}/google-adk-agent:v1.0.0

# 推送到 Google Container Registry
docker push gcr.io/${PROJECT_ID}/google-adk-agent:v1.0.0

# 本地測試
docker run -p 8080:8080 \\
  -e GOOGLE_API_KEY=${GOOGLE_API_KEY} \\
  google-adk-agent:latest
"""

        print("\nDocker 構建命令:")
        print(build_commands)

    def example_2_docker_compose(self):
        """範例 2: Docker Compose 配置"""
        print("\n" + "="*60)
        print("範例 2: Docker Compose 配置")
        print("="*60)

        docker_compose = {
            "version": "3.8",
            "services": {
                "agent": {
                    "build": ".",
                    "ports": ["8080:8080"],
                    "environment": [
                        "GOOGLE_API_KEY=${GOOGLE_API_KEY}",
                        "GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}",
                        "REDIS_HOST=redis",
                        "REDIS_PORT=6379"
                    ],
                    "depends_on": ["redis"],
                    "restart": "always",
                    "healthcheck": {
                        "test": ["CMD", "curl", "-f", "http://localhost:8080/health"],
                        "interval": "30s",
                        "timeout": "3s",
                        "retries": 3
                    }
                },
                "redis": {
                    "image": "redis:7-alpine",
                    "ports": ["6379:6379"],
                    "volumes": ["redis-data:/data"],
                    "restart": "always"
                },
                "nginx": {
                    "image": "nginx:alpine",
                    "ports": ["80:80", "443:443"],
                    "volumes": [
                        "./nginx.conf:/etc/nginx/nginx.conf",
                        "./ssl:/etc/nginx/ssl"
                    ],
                    "depends_on": ["agent"],
                    "restart": "always"
                }
            },
            "volumes": {
                "redis-data": {}
            }
        }

        print("docker-compose.yml:")
        print(yaml.dump(docker_compose, default_flow_style=False))

        print("\nDocker Compose 命令:")
        print("  啟動: docker-compose up -d")
        print("  停止: docker-compose down")
        print("  查看日誌: docker-compose logs -f")
        print("  重啟: docker-compose restart")

    def example_3_kubernetes_deployment(self):
        """範例 3: Kubernetes 部署配置"""
        print("\n" + "="*60)
        print("範例 3: Kubernetes 部署配置")
        print("="*60)

        # Deployment 配置
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "google-adk-agent",
                "labels": {
                    "app": "google-adk-agent"
                }
            },
            "spec": {
                "replicas": 3,
                "selector": {
                    "matchLabels": {
                        "app": "google-adk-agent"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "google-adk-agent"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "agent",
                            "image": "gcr.io/PROJECT_ID/google-adk-agent:v1.0.0",
                            "ports": [{
                                "containerPort": 8080
                            }],
                            "env": [{
                                "name": "GOOGLE_API_KEY",
                                "valueFrom": {
                                    "secretKeyRef": {
                                        "name": "google-adk-secrets",
                                        "key": "api-key"
                                    }
                                }
                            }],
                            "resources": {
                                "requests": {
                                    "cpu": "500m",
                                    "memory": "512Mi"
                                },
                                "limits": {
                                    "cpu": "1000m",
                                    "memory": "1Gi"
                                }
                            },
                            "livenessProbe": {
                                "httpGet": {
                                    "path": "/health",
                                    "port": 8080
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {
                                    "path": "/ready",
                                    "port": 8080
                                },
                                "initialDelaySeconds": 5,
                                "periodSeconds": 5
                            }
                        }]
                    }
                }
            }
        }

        # Service 配置
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "google-adk-agent-service"
            },
            "spec": {
                "type": "LoadBalancer",
                "selector": {
                    "app": "google-adk-agent"
                },
                "ports": [{
                    "protocol": "TCP",
                    "port": 80,
                    "targetPort": 8080
                }]
            }
        }

        print("Kubernetes Deployment:")
        print(yaml.dump(deployment, default_flow_style=False)[:500] + "...")

        print("\nKubernetes Service:")
        print(yaml.dump(service, default_flow_style=False))

        print("\n部署命令:")
        print("  kubectl apply -f deployment.yaml")
        print("  kubectl apply -f service.yaml")
        print("  kubectl get pods")
        print("  kubectl get services")

    def example_4_cloud_run_deployment(self):
        """範例 4: Cloud Run 部署"""
        print("\n" + "="*60)
        print("範例 4: Cloud Run 部署")
        print("="*60)

        # Cloud Run 服務配置
        cloud_run_config = {
            "apiVersion": "serving.knative.dev/v1",
            "kind": "Service",
            "metadata": {
                "name": "google-adk-agent"
            },
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "autoscaling.knative.dev/minScale": "1",
                            "autoscaling.knative.dev/maxScale": "10"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "image": "gcr.io/PROJECT_ID/google-adk-agent:v1.0.0",
                            "ports": [{
                                "containerPort": 8080
                            }],
                            "env": [{
                                "name": "GOOGLE_API_KEY",
                                "valueFrom": {
                                    "secretKeyRef": {
                                        "name": "google-adk-secrets",
                                        "key": "api-key"
                                    }
                                }
                            }],
                            "resources": {
                                "limits": {
                                    "cpu": "2",
                                    "memory": "2Gi"
                                }
                            }
                        }]
                    }
                }
            }
        }

        print("Cloud Run 配置:")
        print(yaml.dump(cloud_run_config, default_flow_style=False))

        print("\nCloud Run 部署命令:")
        deploy_commands = """
# 使用 gcloud 部署
gcloud run deploy google-adk-agent \\
  --image gcr.io/${PROJECT_ID}/google-adk-agent:v1.0.0 \\
  --platform managed \\
  --region us-central1 \\
  --allow-unauthenticated \\
  --min-instances 1 \\
  --max-instances 10 \\
  --memory 2Gi \\
  --cpu 2 \\
  --set-env-vars GOOGLE_API_KEY=${GOOGLE_API_KEY}

# 查看服務
gcloud run services describe google-adk-agent --region us-central1

# 查看日誌
gcloud run services logs read google-adk-agent --region us-central1
"""
        print(deploy_commands)

    def example_5_cicd_pipeline(self):
        """範例 5: CI/CD 流程配置"""
        print("\n" + "="*60)
        print("範例 5: CI/CD 流程配置")
        print("="*60)

        # GitHub Actions 配置
        github_actions = """
name: Deploy Google ADK Agent

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  SERVICE_NAME: google-adk-agent
  REGION: us-central1

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: pytest tests/ --cov=app

      - name: Lint
        run: |
          pip install flake8
          flake8 app/

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ env.PROJECT_ID }}

      - name: Configure Docker
        run: gcloud auth configure-docker

      - name: Build Docker image
        run: |
          docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:$GITHUB_SHA .
          docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:latest .

      - name: Push Docker image
        run: |
          docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:$GITHUB_SHA
          docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ env.PROJECT_ID }}

      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy $SERVICE_NAME \\
            --image gcr.io/$PROJECT_ID/$SERVICE_NAME:$GITHUB_SHA \\
            --platform managed \\
            --region $REGION \\
            --allow-unauthenticated

      - name: Verify deployment
        run: |
          SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \\
            --region $REGION --format 'value(status.url)')
          curl -f $SERVICE_URL/health
"""

        print("GitHub Actions 工作流:")
        print(github_actions)

    def example_6_monitoring_setup(self):
        """範例 6: 監控配置"""
        print("\n" + "="*60)
        print("範例 6: 監控配置")
        print("="*60)

        # Prometheus 配置
        prometheus_config = """
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'google-adk-agent'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/metrics'

  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: google-adk-agent
"""

        print("Prometheus 配置 (prometheus.yml):")
        print(prometheus_config)

        # Grafana Dashboard 配置
        grafana_dashboard = {
            "dashboard": {
                "title": "Google ADK Agent Monitoring",
                "panels": [
                    {
                        "title": "Request Rate",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(http_requests_total[5m])"
                        }]
                    },
                    {
                        "title": "Response Time",
                        "type": "graph",
                        "targets": [{
                            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
                        }]
                    },
                    {
                        "title": "Error Rate",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
                        }]
                    }
                ]
            }
        }

        print("\nGrafana Dashboard 配置:")
        print(json.dumps(grafana_dashboard, indent=2))

    def example_7_logging_setup(self):
        """範例 7: 日誌配置"""
        print("\n" + "="*60)
        print("範例 7: 日誌配置")
        print("="*60)

        # 結構化日誌配置
        logging_config = """
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # 控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(JsonFormatter())
        self.logger.addHandler(console_handler)

    def log(self, level, message, **kwargs):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message,
            'service': 'google-adk-agent',
            **kwargs
        }
        getattr(self.logger, level)(json.dumps(log_data))

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        return json.dumps(log_data)

# 使用範例
logger = StructuredLogger('google-adk-agent')
logger.log('info', 'Agent started', version='1.0.0')
logger.log('error', 'Request failed', error_code='500', user_id='user-123')
"""

        print("結構化日誌配置:")
        print(logging_config)

        print("\nCloud Logging 查詢範例:")
        queries = """
# 查看錯誤日誌
resource.type="cloud_run_revision"
resource.labels.service_name="google-adk-agent"
severity="ERROR"

# 查看特定用戶的請求
resource.type="cloud_run_revision"
jsonPayload.user_id="user-123"

# 查看慢請求
resource.type="cloud_run_revision"
jsonPayload.latency>1000
"""
        print(queries)

    def example_8_scaling_config(self):
        """範例 8: 自動擴展配置"""
        print("\n" + "="*60)
        print("範例 8: 自動擴展配置")
        print("="*60)

        # Kubernetes HPA 配置
        hpa_config = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": "google-adk-agent-hpa"
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": "google-adk-agent"
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
                ],
                "behavior": {
                    "scaleDown": {
                        "stabilizationWindowSeconds": 300,
                        "policies": [{
                            "type": "Percent",
                            "value": 50,
                            "periodSeconds": 60
                        }]
                    },
                    "scaleUp": {
                        "stabilizationWindowSeconds": 60,
                        "policies": [{
                            "type": "Percent",
                            "value": 100,
                            "periodSeconds": 60
                        }]
                    }
                }
            }
        }

        print("Horizontal Pod Autoscaler 配置:")
        print(yaml.dump(hpa_config, default_flow_style=False))

    def example_9_disaster_recovery(self):
        """範例 9: 災難恢復計劃"""
        print("\n" + "="*60)
        print("範例 9: 災難恢復計劃")
        print("="*60)

        dr_plan = {
            "備份策略": {
                "數據備份": "每日自動備份到 Cloud Storage",
                "配置備份": "版本控制在 Git 倉庫",
                "保留期限": "30 天",
                "備份驗證": "每週進行恢復測試"
            },
            "故障轉移": {
                "主區域": "us-central1",
                "備用區域": "us-east1",
                "RTO": "< 1 小時",  # Recovery Time Objective
                "RPO": "< 5 分鐘"   # Recovery Point Objective
            },
            "恢復步驟": [
                "1. 評估故障範圍和影響",
                "2. 通知相關人員",
                "3. 切換到備用區域",
                "4. 從最近備份恢復數據",
                "5. 驗證服務功能",
                "6. 更新 DNS 記錄",
                "7. 監控服務狀態",
                "8. 記錄事件報告"
            ]
        }

        print("災難恢復計劃:")
        for section, content in dr_plan.items():
            print(f"\n{section}:")
            if isinstance(content, dict):
                for key, value in content.items():
                    print(f"  {key}: {value}")
            elif isinstance(content, list):
                for item in content:
                    print(f"  {item}")

        # 備份腳本
        backup_script = """
#!/bin/bash
# 自動備份腳本

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="gs://my-backup-bucket/google-adk-agent"

# 備份數據
echo "開始備份..."

# 備份 Redis 數據
kubectl exec redis-pod -- redis-cli BGSAVE
kubectl cp redis-pod:/data/dump.rdb ./dump_${TIMESTAMP}.rdb
gsutil cp ./dump_${TIMESTAMP}.rdb ${BACKUP_DIR}/redis/

# 備份配置
kubectl get all -n google-adk-agent -o yaml > config_${TIMESTAMP}.yaml
gsutil cp config_${TIMESTAMP}.yaml ${BACKUP_DIR}/config/

# 清理舊備份（保留 30 天）
gsutil -m rm -r ${BACKUP_DIR}/**/$(date -d '30 days ago' +%Y%m%d)*

echo "備份完成"
"""

        print("\n自動備份腳本:")
        print(backup_script)

    def example_10_production_checklist(self):
        """範例 10: 生產環境檢查清單"""
        print("\n" + "="*60)
        print("範例 10: 生產環境檢查清單")
        print("="*60)

        checklist = {
            "安全性": [
                "[ ] API 密鑰安全存儲在 Secret Manager",
                "[ ] 啟用 HTTPS/TLS",
                "[ ] 配置防火牆規則",
                "[ ] 實施速率限制",
                "[ ] 啟用審計日誌",
                "[ ] 完成安全掃描"
            ],
            "可靠性": [
                "[ ] 配置健康檢查",
                "[ ] 設置自動擴展",
                "[ ] 實施重試機制",
                "[ ] 配置備份策略",
                "[ ] 測試故障轉移",
                "[ ] 設置 SLA 監控"
            ],
            "性能": [
                "[ ] 完成負載測試",
                "[ ] 優化響應時間",
                "[ ] 配置緩存策略",
                "[ ] 啟用 CDN（如適用）",
                "[ ] 資源限制設置合理",
                "[ ] 數據庫連接池優化"
            ],
            "監控": [
                "[ ] 配置指標收集",
                "[ ] 設置告警規則",
                "[ ] 集成日誌系統",
                "[ ] 配置追蹤系統",
                "[ ] 設置儀表板",
                "[ ] 準備事件響應流程"
            ],
            "文檔": [
                "[ ] API 文檔完整",
                "[ ] 運維手冊準備",
                "[ ] 故障排除指南",
                "[ ] 架構圖更新",
                "[ ] 變更日誌維護",
                "[ ] 聯繫人信息更新"
            ],
            "合規性": [
                "[ ] 數據隱私政策",
                "[ ] 用戶協議準備",
                "[ ] 合規性審查完成",
                "[ ] 許可證檢查",
                "[ ] 數據處理協議",
                "[ ] GDPR/CCPA 合規"
            ]
        }

        print("生產環境部署檢查清單:\n")
        for category, items in checklist.items():
            print(f"{category}:")
            for item in items:
                print(f"  {item}")
            print()

        # 部署後驗證
        print("部署後驗證步驟:")
        verification_steps = [
            "1. 驗證服務可訪問性",
            "2. 測試主要功能",
            "3. 檢查日誌無錯誤",
            "4. 驗證監控指標",
            "5. 確認告警正常",
            "6. 檢查性能指標",
            "7. 驗證備份功能",
            "8. 測試故障恢復",
            "9. 更新運維文檔",
            "10. 通知相關團隊"
        ]

        for step in verification_steps:
            print(f"  {step}")


def main():
    """主函數"""
    print("="*60)
    print("Google ADK - 部署上線範例")
    print("="*60)

    # 創建範例實例
    example = DeploymentExample()

    try:
        # 運行所有範例
        example.example_1_dockerfile()
        example.example_2_docker_compose()
        example.example_3_kubernetes_deployment()
        example.example_4_cloud_run_deployment()
        example.example_5_cicd_pipeline()
        example.example_6_monitoring_setup()
        example.example_7_logging_setup()
        example.example_8_scaling_config()
        example.example_9_disaster_recovery()
        example.example_10_production_checklist()

        print("\n" + "="*60)
        print("所有部署上線範例執行完成！")
        print("="*60)

        print("\n下一步:")
        print("  1. 根據範例配置您的部署環境")
        print("  2. 完成生產環境檢查清單")
        print("  3. 執行測試和驗證")
        print("  4. 設置監控和告警")
        print("  5. 準備運維文檔")
        print("  6. 進行生產部署")

    except Exception as e:
        print(f"\n❌ 執行錯誤: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
