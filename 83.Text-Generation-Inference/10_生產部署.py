#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TGI 生產部署示例"""
import sys

def production_deployment():
    print("=" * 80)
    print("生產部署示例")
    print("=" * 80)

    print("\n📝 Kubernetes 部署：\n")
    k8s = '''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tgi-production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tgi
  template:
    metadata:
      labels:
        app: tgi
    spec:
      containers:
      - name: tgi
        image: ghcr.io/huggingface/text-generation-inference:latest
        args:
          - --model-id
          - meta-llama/Llama-2-7b-chat-hf
          - --num-shard
          - "1"
        ports:
        - containerPort: 80
        resources:
          limits:
            nvidia.com/gpu: 1
            memory: 16Gi
          requests:
            nvidia.com/gpu: 1
            memory: 16Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 120
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 60
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: tgi-service
spec:
  selector:
    app: tgi
  ports:
  - port: 80
    targetPort: 80
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: tgi-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: tgi-production
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
'''
    print(k8s)

    print("\n監控配置：\n")
    monitoring = '''
# Prometheus 監控
scrape_configs:
  - job_name: 'tgi'
    static_configs:
      - targets: ['tgi-service:80']
    metrics_path: '/metrics'

# 查看關鍵指標
# - tgi_request_duration_seconds
# - tgi_queue_size
# - tgi_batch_inference_duration_seconds
'''
    print(monitoring)

if __name__ == "__main__":
    print("\n" + "="*80)
    print("TGI 生產部署示例")
    print("="*80 + "\n")
    production_deployment()
    print("\n✓ 完成\n")
