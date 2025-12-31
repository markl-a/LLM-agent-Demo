#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenLLM 與 BentoML 整合示例
=========================

本示例展示如何將 OpenLLM 與 BentoML 整合，包括：
1. 創建 BentoML 服務
2. 構建 Bento
3. 服務部署
4. API 定義
5. 生產環境配置

適用場景：
- 生產環境部署
- 服務封裝和版本管理
- 複雜的服務編排
"""

import sys
from typing import Dict, Any


def create_bentoml_service():
    """
    創建 BentoML 服務

    展示如何創建完整的 BentoML 服務
    """
    print("=" * 80)
    print("示例 1: 創建 BentoML 服務")
    print("=" * 80)

    print("\n📝 基本服務定義（service.py）：")
    print("-" * 80)

    service_code = '''
# service.py
import bentoml
import openllm
from bentoml.io import JSON, Text

# 加載模型
llm = openllm.LLM("llama", model_id="meta-llama/Llama-2-7b-chat-hf")

# 創建 Runner
llm_runner = bentoml.Runner(llm, name="llm_runner")

# 定義服務
svc = bentoml.Service(
    name="openllm-service",
    runners=[llm_runner],
)

# 定義 API 端點
@svc.api(
    input=Text(),
    output=Text(),
    route="/generate",
)
async def generate(text: str) -> str:
    """文本生成 API"""
    result = await llm_runner.generate.async_run(
        text,
        max_new_tokens=200,
        temperature=0.7,
    )
    return result

@svc.api(
    input=JSON(),
    output=JSON(),
    route="/chat",
)
async def chat(input_data: dict) -> dict:
    """聊天 API"""
    messages = input_data.get("messages", [])

    # 構建提示詞
    prompt = construct_prompt(messages)

    # 生成回覆
    response = await llm_runner.generate.async_run(
        prompt,
        max_new_tokens=input_data.get("max_tokens", 256),
    )

    return {
        "message": {
            "role": "assistant",
            "content": response,
        }
    }

def construct_prompt(messages):
    """構建聊天提示詞"""
    prompt = ""
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content")
        if role == "user":
            prompt += f"[INST] {content} [/INST]\\n"
        elif role == "assistant":
            prompt += f"{content}\\n"
    return prompt
'''

    print(service_code)

    print("\n啟動服務：")
    print("-" * 80)
    print("bentoml serve service:svc --host 0.0.0.0 --port 3000")


def build_bento():
    """
    構建 Bento

    展示如何將服務打包成 Bento
    """
    print("\n" + "=" * 80)
    print("示例 2: 構建 Bento")
    print("=" * 80)

    print("\n📝 Bento 配置文件（bentofile.yaml）：")
    print("-" * 80)

    bentofile = '''
service: "service:svc"
name: "openllm-service"
version: "1.0.0"

description: |
  OpenLLM 生產服務
  基於 Llama 2 模型的文本生成服務

labels:
  owner: ml-team
  project: llm-deployment
  environment: production

include:
  - "service.py"
  - "*.py"
  - "config/"

exclude:
  - "tests/"
  - "*.pyc"
  - "__pycache__"

python:
  requirements_txt: "./requirements.txt"
  packages:
    - openllm>=0.4.0
    - bentoml>=1.2.0
    - torch>=2.0.0
    - transformers>=4.40.0
  lock_packages: true
  index_url: "https://pypi.org/simple"

docker:
  distro: debian
  python_version: "3.10"
  cuda_version: "11.8"
  system_packages:
    - git
    - build-essential
  env:
    TRANSFORMERS_CACHE: "/models/cache"
  setup_script: "./setup.sh"

resources:
  gpu: 1
  gpu_type: nvidia-tesla-t4
  memory: "16Gi"
  cpu: "4"
'''

    print(bentofile)

    print("\n構建命令：")
    print("-" * 80)

    build_commands = '''
# 1. 構建 Bento
bentoml build

# 2. 查看構建的 Bento
bentoml list

# 3. 查看特定 Bento 的信息
bentoml get openllm-service:latest

# 4. 導出 Bento
bentoml export openllm-service:latest openllm-service.bento

# 5. 導入 Bento
bentoml import openllm-service.bento
'''

    print(build_commands)


def containerize_bento():
    """
    容器化 Bento

    展示如何將 Bento 打包成 Docker 鏡像
    """
    print("\n" + "=" * 80)
    print("示例 3: 容器化部署")
    print("=" * 80)

    print("\n📝 生成 Docker 鏡像：")
    print("-" * 80)

    docker_commands = '''
# 1. 構建 Docker 鏡像
bentoml containerize openllm-service:latest \\
  --image-tag openllm-service:v1.0.0

# 2. 查看生成的鏡像
docker images | grep openllm-service

# 3. 運行容器
docker run --rm \\
  --gpus all \\
  -p 3000:3000 \\
  -v ~/.cache/huggingface:/models/cache \\
  openllm-service:v1.0.0 \\
  serve --production

# 4. 推送到 Docker Registry
docker tag openllm-service:v1.0.0 your-registry/openllm-service:v1.0.0
docker push your-registry/openllm-service:v1.0.0
'''

    print(docker_commands)

    print("\nDocker Compose 配置：")
    print("-" * 80)

    compose_config = '''
# docker-compose.yml
version: '3.8'

services:
  openllm:
    image: openllm-service:v1.0.0
    ports:
      - "3000:3000"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - BENTOML_PORT=3000
      - TRANSFORMERS_CACHE=/models/cache
    volumes:
      - model-cache:/models/cache
    command: serve --production --workers 1

volumes:
  model-cache:
'''

    print(compose_config)


def kubernetes_deployment():
    """
    Kubernetes 部署

    展示如何在 K8s 上部署 Bento
    """
    print("\n" + "=" * 80)
    print("示例 4: Kubernetes 部署")
    print("=" * 80)

    print("\n📝 生成 K8s 配置：")
    print("-" * 80)

    print("bentoml containerize openllm-service:latest --generate-kubernetes-manifest")

    print("\n\nKubernetes Deployment：")
    print("-" * 80)

    k8s_deployment = '''
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openllm-service
  labels:
    app: openllm-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: openllm-service
  template:
    metadata:
      labels:
        app: openllm-service
    spec:
      containers:
      - name: openllm
        image: your-registry/openllm-service:v1.0.0
        ports:
        - containerPort: 3000
        resources:
          requests:
            memory: "16Gi"
            cpu: "4"
            nvidia.com/gpu: "1"
          limits:
            memory: "16Gi"
            cpu: "4"
            nvidia.com/gpu: "1"
        env:
        - name: BENTOML_PORT
          value: "3000"
        volumeMounts:
        - name: model-cache
          mountPath: /models/cache
      volumes:
      - name: model-cache
        persistentVolumeClaim:
          claimName: model-cache-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: openllm-service
spec:
  selector:
    app: openllm-service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: openllm-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: openllm-service
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
'''

    print(k8s_deployment)

    print("\n部署命令：")
    print("-" * 80)

    deploy_commands = '''
# 應用配置
kubectl apply -f deployment.yaml

# 查看部署狀態
kubectl get deployments
kubectl get pods
kubectl get services

# 查看日誌
kubectl logs -f deployment/openllm-service

# 擴展服務
kubectl scale deployment openllm-service --replicas=3
'''

    print(deploy_commands)


def bentocloud_deployment():
    """
    BentoCloud 部署

    展示如何部署到 BentoCloud
    """
    print("\n" + "=" * 80)
    print("示例 5: BentoCloud 部署")
    print("=" * 80)

    print("\n📝 部署到 BentoCloud：")
    print("-" * 80)

    bentocloud_commands = '''
# 1. 登錄 BentoCloud
bentoml cloud login

# 2. 構建並推送 Bento
bentoml build
bentoml push openllm-service:latest

# 3. 創建部署
bentoml deployment create \\
  --name openllm-production \\
  --bento openllm-service:latest \\
  --instance-type gpu.t4.medium \\
  --scaling-min 1 \\
  --scaling-max 5 \\
  --envs TRANSFORMERS_CACHE=/models/cache

# 4. 查看部署狀態
bentoml deployment list
bentoml deployment get openllm-production

# 5. 查看日誌
bentoml deployment logs openllm-production

# 6. 更新部署
bentoml deployment update openllm-production \\
  --bento openllm-service:v2.0.0

# 7. 刪除部署
bentoml deployment delete openllm-production
'''

    print(bentocloud_commands)

    print("\n部署配置（YAML）：")
    print("-" * 80)

    deployment_config = '''
# deployment_config.yaml
name: openllm-production
bento: openllm-service:latest

instance_type: gpu.t4.medium

scaling:
  min_replicas: 1
  max_replicas: 5
  policy:
    - metric: cpu
      target: 70
    - metric: latency_p99
      target: 500  # ms

resources:
  gpu: 1
  memory: "16Gi"
  cpu: "4"

envs:
  TRANSFORMERS_CACHE: "/models/cache"
  BENTOML_WORKER_TIMEOUT: "300"

health_check:
  path: "/health"
  interval: 30
  timeout: 10

monitoring:
  enabled: true
  prometheus: true
'''

    print(deployment_config)

    print("\n使用配置文件部署：")
    print("bentoml deployment apply -f deployment_config.yaml")


def advanced_features():
    """
    高級功能

    展示 BentoML 的高級功能
    """
    print("\n" + "=" * 80)
    print("示例 6: 高級功能")
    print("=" * 80)

    print("\n📝 多模型服務：")
    print("-" * 80)

    multi_model_code = '''
# service.py - 多模型服務
import bentoml
import openllm

# 加載多個模型
llm_7b = openllm.LLM("llama", model_id="meta-llama/Llama-2-7b-chat-hf")
llm_13b = openllm.LLM("llama", model_id="meta-llama/Llama-2-13b-chat-hf")

# 創建多個 Runner
runner_7b = bentoml.Runner(llm_7b, name="llm_7b")
runner_13b = bentoml.Runner(llm_13b, name="llm_13b")

svc = bentoml.Service(
    name="multi-llm-service",
    runners=[runner_7b, runner_13b],
)

@svc.api(input=JSON(), output=JSON())
async def generate(input_data: dict) -> dict:
    """根據需求選擇不同大小的模型"""
    prompt = input_data.get("prompt")
    model_size = input_data.get("model_size", "7b")

    if model_size == "13b":
        result = await runner_13b.generate.async_run(prompt)
    else:
        result = await runner_7b.generate.async_run(prompt)

    return {"result": result, "model": model_size}
'''

    print(multi_model_code)

    print("\n中間件和鉤子：")
    print("-" * 80)

    middleware_code = '''
import bentoml
from bentoml.io import JSON
import time

svc = bentoml.Service("openllm-service")

@svc.on_startup
async def startup():
    """服務啟動時執行"""
    print("服務啟動中...")
    # 預熱模型
    # 加載緩存
    pass

@svc.on_shutdown
async def shutdown():
    """服務關閉時執行"""
    print("服務關閉中...")
    # 清理資源
    pass

@svc.middleware
async def log_middleware(request, call_next):
    """請求日誌中間件"""
    start = time.time()

    # 處理請求
    response = await call_next(request)

    # 記錄日誌
    duration = time.time() - start
    print(f"Request: {request.url} - Duration: {duration:.2f}s")

    return response
'''

    print(middleware_code)


def main():
    """
    主函數：運行所有示例
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 18 + "OpenLLM BentoML 整合示例" + " " * 18 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    try:
        # 示例 1: 創建服務
        create_bentoml_service()

        # 示例 2: 構建 Bento
        build_bento()

        # 示例 3: 容器化
        containerize_bento()

        # 示例 4: K8s 部署
        kubernetes_deployment()

        # 示例 5: BentoCloud
        bentocloud_deployment()

        # 示例 6: 高級功能
        advanced_features()

        print("\n" + "=" * 80)
        print("✓ 所有示例展示完成！")
        print("=" * 80)
        print("\n💡 關鍵要點：")
        print("   1. BentoML 提供完整的服務封裝")
        print("   2. 支持多種部署方式")
        print("   3. 內置監控和擴展功能")
        print("   4. 生產環境就緒")
        print()

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
