#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenLLM Kubernetes 部署示例
=========================

本示例展示在 Kubernetes 上部署 OpenLLM，包括：
1. 基本 Deployment 配置
2. Service 和 Ingress
3. 水平擴展（HPA）
4. 資源管理和配額
5. 生產環境最佳實踐

適用場景：
- 大規模生產環境
- 自動擴展需求
- 高可用性部署
"""

import sys


def basic_deployment():
    """
    基本 Deployment 配置

    展示最基礎的 K8s 部署配置
    """
    print("=" * 80)
    print("示例 1: 基本 Deployment 配置")
    print("=" * 80)

    print("\n📝 Deployment YAML：")
    print("-" * 80)

    deployment_yaml = '''
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openllm
  labels:
    app: openllm
    version: v1
spec:
  replicas: 2
  selector:
    matchLabels:
      app: openllm
  template:
    metadata:
      labels:
        app: openllm
        version: v1
    spec:
      containers:
      - name: openllm
        image: ghcr.io/bentoml/openllm:latest
        command:
          - "openllm"
          - "start"
          - "llama"
          - "--model-id"
          - "meta-llama/Llama-2-7b-chat-hf"
          - "--backend"
          - "vllm"
        ports:
        - containerPort: 3000
          name: http
          protocol: TCP
        env:
        - name: TRANSFORMERS_CACHE
          value: "/models/cache"
        - name: OPENLLM_BACKEND
          value: "vllm"
        resources:
          requests:
            memory: "16Gi"
            cpu: "4"
            nvidia.com/gpu: "1"
          limits:
            memory: "16Gi"
            cpu: "4"
            nvidia.com/gpu: "1"
        volumeMounts:
        - name: model-cache
          mountPath: /models/cache
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 120
          periodSeconds: 30
          timeoutSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 60
          periodSeconds: 10
      volumes:
      - name: model-cache
        persistentVolumeClaim:
          claimName: model-cache-pvc
      # GPU 節點選擇
      nodeSelector:
        accelerator: nvidia-tesla-t4
      tolerations:
      - key: nvidia.com/gpu
        operator: Exists
        effect: NoSchedule
'''

    print(deployment_yaml)

    print("\nPersistentVolumeClaim：")
    print("-" * 80)

    pvc_yaml = '''
# pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: model-cache-pvc
spec:
  accessModes:
    - ReadWriteMany  # 多個 Pod 共享
  resources:
    requests:
      storage: 100Gi
  storageClassName: fast-ssd
'''

    print(pvc_yaml)


def service_and_ingress():
    """
    Service 和 Ingress 配置

    展示如何暴露服務
    """
    print("\n" + "=" * 80)
    print("示例 2: Service 和 Ingress")
    print("=" * 80)

    print("\n📝 Service 配置：")
    print("-" * 80)

    service_yaml = '''
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: openllm-service
  labels:
    app: openllm
spec:
  type: LoadBalancer  # 或 ClusterIP, NodePort
  selector:
    app: openllm
  ports:
  - name: http
    protocol: TCP
    port: 80
    targetPort: 3000
  sessionAffinity: ClientIP  # 會話親和性
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800
'''

    print(service_yaml)

    print("\nIngress 配置：")
    print("-" * 80)

    ingress_yaml = '''
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: openllm-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/proxy-body-size: "0"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "600"
spec:
  tls:
  - hosts:
    - openllm.example.com
    secretName: openllm-tls
  rules:
  - host: openllm.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: openllm-service
            port:
              number: 80
'''

    print(ingress_yaml)


def horizontal_pod_autoscaler():
    """
    水平自動擴展

    展示如何配置 HPA
    """
    print("\n" + "=" * 80)
    print("示例 3: 水平自動擴展（HPA）")
    print("=" * 80)

    print("\n📝 HPA 配置：")
    print("-" * 80)

    hpa_yaml = '''
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: openllm-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: openllm
  minReplicas: 1
  maxReplicas: 10
  metrics:
  # CPU 使用率
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  # 內存使用率
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  # 自定義指標：請求速率
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
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
      selectPolicy: Max
'''

    print(hpa_yaml)

    print("\n查看 HPA 狀態：")
    print("-" * 80)

    hpa_commands = '''
# 查看 HPA
kubectl get hpa openllm-hpa

# 查看詳細信息
kubectl describe hpa openllm-hpa

# 查看擴展歷史
kubectl get hpa openllm-hpa --watch
'''

    print(hpa_commands)


def resource_management():
    """
    資源管理和配額

    展示資源管理最佳實踐
    """
    print("\n" + "=" * 80)
    print("示例 4: 資源管理和配額")
    print("=" * 80)

    print("\n📝 ResourceQuota：")
    print("-" * 80)

    quota_yaml = '''
# resourcequota.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: openllm-quota
  namespace: ml-services
spec:
  hard:
    requests.cpu: "20"
    requests.memory: "64Gi"
    requests.nvidia.com/gpu: "4"
    limits.cpu: "40"
    limits.memory: "128Gi"
    limits.nvidia.com/gpu: "8"
    persistentvolumeclaims: "5"
    pods: "10"
'''

    print(quota_yaml)

    print("\nLimitRange：")
    print("-" * 80)

    limitrange_yaml = '''
# limitrange.yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: openllm-limits
  namespace: ml-services
spec:
  limits:
  - max:
      cpu: "8"
      memory: "32Gi"
      nvidia.com/gpu: "2"
    min:
      cpu: "1"
      memory: "4Gi"
      nvidia.com/gpu: "1"
    default:
      cpu: "4"
      memory: "16Gi"
    defaultRequest:
      cpu: "2"
      memory: "8Gi"
    type: Container
'''

    print(limitrange_yaml)

    print("\nPriorityClass：")
    print("-" * 80)

    priority_yaml = '''
# priorityclass.yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority-llm
value: 1000000
globalDefault: false
description: "高優先級 LLM 服務"
'''

    print(priority_yaml)


def production_best_practices():
    """
    生產環境最佳實踐

    展示完整的生產環境配置
    """
    print("\n" + "=" * 80)
    print("示例 5: 生產環境最佳實踐")
    print("=" * 80)

    print("\n📝 完整生產配置：")
    print("-" * 80)

    production_yaml = '''
# production-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openllm-production
  namespace: ml-services
  labels:
    app: openllm
    environment: production
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: openllm
      environment: production
  template:
    metadata:
      labels:
        app: openllm
        environment: production
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "3000"
        prometheus.io/path: "/metrics"
    spec:
      # 高優先級
      priorityClassName: high-priority-llm

      # 服務賬號
      serviceAccountName: openllm-sa

      # 安全上下文
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000

      containers:
      - name: openllm
        image: ghcr.io/bentoml/openllm:0.4.0
        imagePullPolicy: IfNotPresent

        command:
          - "openllm"
          - "start"
          - "llama"
          - "--model-id"
          - "meta-llama/Llama-2-7b-chat-hf"
          - "--backend"
          - "vllm"
          - "--config"
          - "/config/model-config.yaml"

        ports:
        - containerPort: 3000
          name: http
          protocol: TCP
        - containerPort: 9090
          name: metrics
          protocol: TCP

        env:
        - name: TRANSFORMERS_CACHE
          value: "/models/cache"
        - name: OPENLLM_BACKEND
          value: "vllm"
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: POD_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace

        resources:
          requests:
            memory: "16Gi"
            cpu: "4"
            nvidia.com/gpu: "1"
          limits:
            memory: "16Gi"
            cpu: "4"
            nvidia.com/gpu: "1"

        volumeMounts:
        - name: model-cache
          mountPath: /models/cache
        - name: config
          mountPath: /config
        - name: tmp
          mountPath: /tmp

        # 健康檢查
        livenessProbe:
          httpGet:
            path: /livez
            port: 3000
          initialDelaySeconds: 120
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3

        readinessProbe:
          httpGet:
            path: /readyz
            port: 3000
          initialDelaySeconds: 60
          periodSeconds: 10
          timeoutSeconds: 5
          successThreshold: 1
          failureThreshold: 3

        # 優雅關閉
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 15"]

      volumes:
      - name: model-cache
        persistentVolumeClaim:
          claimName: model-cache-pvc
      - name: config
        configMap:
          name: openllm-config
      - name: tmp
        emptyDir: {}

      # 節點親和性
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: accelerator
                operator: In
                values:
                - nvidia-tesla-t4
                - nvidia-tesla-v100
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - openllm
              topologyKey: kubernetes.io/hostname

      tolerations:
      - key: nvidia.com/gpu
        operator: Exists
        effect: NoSchedule
'''

    print(production_yaml)

    print("\nConfigMap 配置：")
    print("-" * 80)

    configmap_yaml = '''
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: openllm-config
  namespace: ml-services
data:
  model-config.yaml: |
    backend: vllm
    backend_config:
      max_model_len: 4096
      gpu_memory_utilization: 0.9
      tensor_parallel_size: 1

    generation_config:
      max_new_tokens: 256
      temperature: 0.7
      top_p: 0.95
'''

    print(configmap_yaml)


def monitoring_setup():
    """
    監控設置

    展示如何設置監控和告警
    """
    print("\n" + "=" * 80)
    print("示例 6: 監控和告警")
    print("=" * 80)

    print("\n📝 ServiceMonitor (Prometheus Operator)：")
    print("-" * 80)

    servicemonitor_yaml = '''
# servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: openllm-monitor
  namespace: ml-services
spec:
  selector:
    matchLabels:
      app: openllm
  endpoints:
  - port: http
    interval: 30s
    path: /metrics
'''

    print(servicemonitor_yaml)

    print("\n部署命令：")
    print("-" * 80)

    deploy_commands = '''
# 創建命名空間
kubectl create namespace ml-services

# 應用所有配置
kubectl apply -f pvc.yaml
kubectl apply -f configmap.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml
kubectl apply -f hpa.yaml

# 查看部署狀態
kubectl get all -n ml-services
kubectl get pods -n ml-services -w

# 查看日誌
kubectl logs -f deployment/openllm -n ml-services

# 擴展部署
kubectl scale deployment openllm --replicas=5 -n ml-services

# 滾動更新
kubectl set image deployment/openllm \\
  openllm=ghcr.io/bentoml/openllm:0.5.0 \\
  -n ml-services

# 回滾
kubectl rollout undo deployment/openllm -n ml-services
'''

    print(deploy_commands)


def main():
    """
    主函數：運行所有示例
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 17 + "OpenLLM Kubernetes 部署示例" + " " * 18 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    try:
        # 示例 1: 基本部署
        basic_deployment()

        # 示例 2: Service 和 Ingress
        service_and_ingress()

        # 示例 3: HPA
        horizontal_pod_autoscaler()

        # 示例 4: 資源管理
        resource_management()

        # 示例 5: 生產最佳實踐
        production_best_practices()

        # 示例 6: 監控設置
        monitoring_setup()

        print("\n" + "=" * 80)
        print("✓ 所有示例展示完成！")
        print("=" * 80)
        print("\n💡 關鍵要點：")
        print("   1. K8s 提供自動擴展和高可用性")
        print("   2. 合理配置資源請求和限制")
        print("   3. 實施完善的健康檢查")
        print("   4. 使用 HPA 實現自動擴展")
        print("   5. 配置監控和告警系統")
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
