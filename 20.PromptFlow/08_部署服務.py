"""
PromptFlow 部署服務範例
======================

本範例展示如何將 PromptFlow 部署為服務。

部署選項：
1. 本地部署
2. Docker 部署
3. Azure ML 部署
4. Kubernetes 部署

安裝依賴：
pip install promptflow promptflow-tools flask fastapi uvicorn
"""

import os
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

# ============================================================
# 本地服務部署
# ============================================================

# Flask 服務示例
FLASK_SERVER_CODE = '''
"""
Flask 服務器
"""
from flask import Flask, request, jsonify
from promptflow import load_flow

app = Flask(__name__)

# 加載 Flow
flow = load_flow("./my_flow")

@app.route("/health", methods=["GET"])
def health():
    """健康檢查"""
    return jsonify({"status": "healthy"})

@app.route("/predict", methods=["POST"])
def predict():
    """預測接口"""
    try:
        data = request.json
        result = flow(**data)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
'''

# FastAPI 服務示例
FASTAPI_SERVER_CODE = '''
"""
FastAPI 服務器
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from promptflow import load_flow

app = FastAPI(title="PromptFlow Service")

# 加載 Flow
flow = load_flow("./my_flow")

class PredictRequest(BaseModel):
    question: str
    context: Optional[str] = None

class PredictResponse(BaseModel):
    answer: str
    confidence: float

@app.get("/health")
async def health():
    """健康檢查"""
    return {"status": "healthy"}

@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """預測接口"""
    try:
        result = flow(
            question=request.question,
            context=request.context
        )
        return PredictResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 運行: uvicorn server:app --host 0.0.0.0 --port 8080
'''


# ============================================================
# Docker 部署配置
# ============================================================

DOCKERFILE = '''
# Dockerfile for PromptFlow

FROM python:3.10-slim

WORKDIR /app

# 安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY . .

# 設置環境變數
ENV PROMPTFLOW_FLOW_PATH=/app/flow

# 暴露端口
EXPOSE 8080

# 啟動命令
CMD ["pf", "flow", "serve", "--source", "/app/flow", "--port", "8080", "--host", "0.0.0.0"]
'''

DOCKER_COMPOSE = '''
version: '3.8'

services:
  promptflow-service:
    build: .
    ports:
      - "8080:8080"
    environment:
      - AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
    volumes:
      - ./flow:/app/flow
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
'''


# ============================================================
# 部署管理類
# ============================================================

@dataclass
class DeploymentConfig:
    """部署配置"""
    name: str
    flow_path: str
    port: int = 8080
    host: str = "0.0.0.0"
    workers: int = 4
    timeout: int = 60
    environment: Dict[str, str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "flow_path": self.flow_path,
            "port": self.port,
            "host": self.host,
            "workers": self.workers,
            "timeout": self.timeout,
            "environment": self.environment or {}
        }


class LocalDeployment:
    """
    本地部署管理

    管理本地服務的部署
    """

    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.process = None

    def start(self):
        """啟動服務"""
        import subprocess

        cmd = [
            "pf", "flow", "serve",
            "--source", self.config.flow_path,
            "--port", str(self.config.port),
            "--host", self.config.host
        ]

        self.process = subprocess.Popen(cmd)
        print(f"服務已啟動: http://{self.config.host}:{self.config.port}")

    def stop(self):
        """停止服務"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            print("服務已停止")

    def health_check(self) -> bool:
        """健康檢查"""
        import requests
        try:
            response = requests.get(
                f"http://{self.config.host}:{self.config.port}/health",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False


class DockerDeployment:
    """
    Docker 部署管理

    管理 Docker 容器部署
    """

    def __init__(self, config: DeploymentConfig):
        self.config = config

    def generate_dockerfile(self) -> str:
        """生成 Dockerfile"""
        return DOCKERFILE

    def generate_compose(self) -> str:
        """生成 docker-compose.yml"""
        return DOCKER_COMPOSE

    def build_image(self, tag: str = "promptflow-service:latest"):
        """構建鏡像"""
        import subprocess
        cmd = ["docker", "build", "-t", tag, "."]
        subprocess.run(cmd, check=True)
        print(f"鏡像已構建: {tag}")

    def run_container(self, tag: str = "promptflow-service:latest"):
        """運行容器"""
        import subprocess

        env_args = []
        for key, value in (self.config.environment or {}).items():
            env_args.extend(["-e", f"{key}={value}"])

        cmd = [
            "docker", "run", "-d",
            "-p", f"{self.config.port}:8080",
            "--name", self.config.name,
            *env_args,
            tag
        ]

        subprocess.run(cmd, check=True)
        print(f"容器已啟動: {self.config.name}")

    def stop_container(self):
        """停止容器"""
        import subprocess
        subprocess.run(["docker", "stop", self.config.name])
        subprocess.run(["docker", "rm", self.config.name])
        print(f"容器已停止: {self.config.name}")


# ============================================================
# Azure ML 部署
# ============================================================

AZURE_DEPLOYMENT_CONFIG = '''
# azure_deployment.yaml

$schema: https://azuremlschemas.azureedge.net/latest/managedOnlineDeployment.schema.json
name: promptflow-deployment
endpoint_name: promptflow-endpoint

# 模型配置
model:
  path: ./flow
  type: custom_model

# 環境配置
environment:
  name: promptflow-env
  image: mcr.microsoft.com/azureml/promptflow/promptflow-runtime:latest
  conda_file: conda.yaml

# 實例配置
instance_type: Standard_DS3_v2
instance_count: 1

# 請求設置
request_settings:
  request_timeout_ms: 60000
  max_concurrent_requests_per_instance: 10

# 探測設置
liveness_probe:
  initial_delay: 30
  period: 10
  failure_threshold: 3

readiness_probe:
  initial_delay: 30
  period: 10
  failure_threshold: 3
'''


# ============================================================
# Kubernetes 部署
# ============================================================

K8S_DEPLOYMENT = '''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: promptflow-service
  labels:
    app: promptflow
spec:
  replicas: 3
  selector:
    matchLabels:
      app: promptflow
  template:
    metadata:
      labels:
        app: promptflow
    spec:
      containers:
      - name: promptflow
        image: promptflow-service:latest
        ports:
        - containerPort: 8080
        env:
        - name: AZURE_OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: promptflow-secrets
              key: azure-openai-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: promptflow-service
spec:
  selector:
    app: promptflow
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
'''


# ============================================================
# 使用範例
# ============================================================

def example_local_deployment():
    """
    範例 1: 本地部署

    展示如何在本地部署服務
    """
    print("=" * 50)
    print("範例 1: 本地部署")
    print("=" * 50)

    config = DeploymentConfig(
        name="my-service",
        flow_path="./my_flow",
        port=8080
    )

    print("部署配置:")
    print(json.dumps(config.to_dict(), indent=2, ensure_ascii=False))

    print("\n啟動命令:")
    print(f"pf flow serve --source {config.flow_path} --port {config.port}")


def example_flask_server():
    """
    範例 2: Flask 服務

    展示 Flask 服務器代碼
    """
    print("\n" + "=" * 50)
    print("範例 2: Flask 服務")
    print("=" * 50)

    print("Flask 服務器代碼:")
    print(FLASK_SERVER_CODE)


def example_fastapi_server():
    """
    範例 3: FastAPI 服務

    展示 FastAPI 服務器代碼
    """
    print("\n" + "=" * 50)
    print("範例 3: FastAPI 服務")
    print("=" * 50)

    print("FastAPI 服務器代碼:")
    print(FASTAPI_SERVER_CODE)


def example_docker_deployment():
    """
    範例 4: Docker 部署

    展示 Docker 部署配置
    """
    print("\n" + "=" * 50)
    print("範例 4: Docker 部署")
    print("=" * 50)

    print("Dockerfile:")
    print(DOCKERFILE)

    print("\ndocker-compose.yml:")
    print(DOCKER_COMPOSE)


def example_azure_deployment():
    """
    範例 5: Azure ML 部署

    展示 Azure ML 部署配置
    """
    print("\n" + "=" * 50)
    print("範例 5: Azure ML 部署")
    print("=" * 50)

    print("Azure 部署配置:")
    print(AZURE_DEPLOYMENT_CONFIG)

    print("\n部署命令:")
    print("""
# 創建端點
az ml online-endpoint create --file endpoint.yaml

# 創建部署
az ml online-deployment create --file deployment.yaml

# 測試部署
az ml online-endpoint invoke --name promptflow-endpoint --request-file request.json
""")


def example_k8s_deployment():
    """
    範例 6: Kubernetes 部署

    展示 Kubernetes 部署配置
    """
    print("\n" + "=" * 50)
    print("範例 6: Kubernetes 部署")
    print("=" * 50)

    print("Kubernetes 部署配置:")
    print(K8S_DEPLOYMENT)


def example_cli_commands():
    """
    範例 7: CLI 部署命令

    展示 PromptFlow CLI 部署命令
    """
    print("\n" + "=" * 50)
    print("範例 7: CLI 部署命令")
    print("=" * 50)

    commands = """
# PromptFlow 部署 CLI 命令

# 本地服務
pf flow serve --source ./my_flow --port 8080

# 構建為 Docker
pf flow build --source ./my_flow --output ./docker --format docker

# 構建為可執行文件
pf flow build --source ./my_flow --output ./dist --format executable

# 測試本地服務
curl -X POST http://localhost:8080/predict \\
    -H "Content-Type: application/json" \\
    -d '{"question": "Hello"}'

# Azure ML 部署
pf flow deploy --source ./my_flow \\
    --endpoint-name my-endpoint \\
    --deployment-name my-deployment \\
    --subscription <subscription_id> \\
    --resource-group <resource_group> \\
    --workspace <workspace>
"""

    print(commands)


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    print("PromptFlow 部署服務範例")
    print()

    example_local_deployment()
    example_flask_server()
    example_fastapi_server()
    example_docker_deployment()
    example_azure_deployment()
    example_k8s_deployment()
    example_cli_commands()
