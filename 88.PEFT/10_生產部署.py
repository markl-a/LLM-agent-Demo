"""
PEFT 生產部署指南

這個文件介紹 PEFT 模型的生產部署，包括：
1. 部署架構設計
2. 模型服務化
3. 性能優化和監控
4. 錯誤處理和容錯
5. 擴展和負載均衡
6. 最佳實踐和安全考慮

完整的生產級部署方案。
"""

import warnings
warnings.filterwarnings('ignore')


def deployment_architecture():
    """
    部署架構設計
    """
    print("=" * 70)
    print("PEFT 生產部署架構")
    print("=" * 70)

    print("""
1. 單模型部署架構：

```
┌─────────────────────────────────────────────┐
│              負載均衡器 (Nginx/ALB)        │
└────────────┬────────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼────┐      ┌────▼───┐
│ 推理服務 1│    │ 推理服務 2│
│ (GPU 0)  │    │ (GPU 1)  │
└─────────┘      └─────────┘

每個推理服務包含：
• 合併後的 PEFT 模型
• FastAPI/Flask REST API
• 批處理隊列
• 監控和日誌
```

2. 多適配器部署架構：

```
┌─────────────────────────────────────────────┐
│         API Gateway + 路由                  │
└────┬──────────┬──────────┬─────────────────┘
     │          │          │
     ▼          ▼          ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│ 適配器 A │ │ 適配器 B │ │ 適配器 C │
│ (任務1)  │ │ (任務2)  │ │ (任務3)  │
└─────────┘ └─────────┘ └─────────┘
     │          │          │
     └──────┬───┴──────────┘
            ▼
    ┌───────────────┐
    │ 共享基礎模型  │
    │ (內存中)      │
    └───────────────┘

優勢：
• 共享基礎模型，節省內存
• 動態加載適配器
• 靈活的任務路由
```
    """)


def create_rest_api():
    """
    創建 REST API 服務
    """
    print("\n" + "=" * 70)
    print("REST API 服務實現")
    print("=" * 70)

    print("""
使用 FastAPI 創建生產級服務：

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import List, Optional
import asyncio
from collections import deque
import time

app = FastAPI(title="PEFT Model API", version="1.0.0")

# 請求模型
class GenerateRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 50
    temperature: float = 0.7
    top_p: float = 0.9
    adapter_name: Optional[str] = None

class GenerateResponse(BaseModel):
    generated_text: str
    tokens_generated: int
    latency_ms: float

# 模型管理器
class ModelManager:
    def __init__(self, model_path: str, device: str = "cuda"):
        # 加載模型
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model.eval()

        # 適配器緩存
        self.adapters = {}

        # 批處理隊列
        self.request_queue = deque()
        self.batch_size = 8
        self.batch_timeout = 0.01  # 10ms

    async def generate(self, request: GenerateRequest) -> GenerateResponse:
        start_time = time.time()

        # 編碼輸入
        inputs = self.tokenizer(
            request.prompt,
            return_tensors="pt"
        ).to(self.model.device)

        # 生成
        with torch.inference_mode():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=request.max_new_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                do_sample=True if request.temperature > 0 else False,
                pad_token_id=self.tokenizer.pad_token_id,
            )

        # 解碼
        generated_text = self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )

        latency = (time.time() - start_time) * 1000  # ms
        tokens_generated = len(outputs[0]) - len(inputs.input_ids[0])

        return GenerateResponse(
            generated_text=generated_text,
            tokens_generated=tokens_generated,
            latency_ms=latency
        )

# 全局模型管理器
model_manager = None

@app.on_event("startup")
async def startup_event():
    global model_manager
    print("加載模型...")
    model_manager = ModelManager("./merged_model")
    print("模型加載完成")

@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    '''生成文本 API'''
    try:
        response = await model_manager.generate(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    '''健康檢查'''
    return {
        "status": "healthy",
        "gpu_available": torch.cuda.is_available(),
        "gpu_memory_allocated": torch.cuda.memory_allocated() / 1e9 if torch.cuda.is_available() else 0
    }

@app.get("/metrics")
async def metrics():
    '''性能指標'''
    return {
        "model_loaded": model_manager is not None,
        "adapters_cached": len(model_manager.adapters) if model_manager else 0,
    }

# 運行: uvicorn main:app --host 0.0.0.0 --port 8000
```

使用示例：

```bash
# 測試 API
curl -X POST "http://localhost:8000/generate" \\
  -H "Content-Type: application/json" \\
  -d '{
    "prompt": "What is AI?",
    "max_new_tokens": 50,
    "temperature": 0.7
  }'

# 健康檢查
curl "http://localhost:8000/health"
```
    """)


def batching_service():
    """
    批處理服務實現
    """
    print("\n" + "=" * 70)
    print("動態批處理服務")
    print("=" * 70)

    print("""
實現動態批處理以提升吞吐量：

```python
import asyncio
from collections import deque
from dataclasses import dataclass
import time

@dataclass
class PendingRequest:
    prompt: str
    max_new_tokens: int
    temperature: float
    future: asyncio.Future
    timestamp: float

class BatchingModelService:
    def __init__(self, model, tokenizer, batch_size=8, batch_timeout=0.05):
        self.model = model
        self.tokenizer = tokenizer
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout  # 50ms

        self.pending_requests = deque()
        self.processing = False

        # 啟動批處理循環
        asyncio.create_task(self.process_batches())

    async def generate(self, prompt: str, max_new_tokens: int = 50,
                      temperature: float = 0.7) -> str:
        '''異步生成'''
        # 創建 future
        future = asyncio.Future()

        # 添加到隊列
        request = PendingRequest(
            prompt=prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            future=future,
            timestamp=time.time()
        )
        self.pending_requests.append(request)

        # 等待結果
        return await future

    async def process_batches(self):
        '''批處理循環'''
        while True:
            # 等待請求或超時
            await asyncio.sleep(0.001)  # 1ms 檢查間隔

            if not self.pending_requests:
                continue

            # 檢查是否應該處理批次
            should_process = (
                len(self.pending_requests) >= self.batch_size or
                (time.time() - self.pending_requests[0].timestamp) > self.batch_timeout
            )

            if should_process:
                await self._process_batch()

    async def _process_batch(self):
        '''處理一個批次'''
        # 收集批次
        batch_requests = []
        while self.pending_requests and len(batch_requests) < self.batch_size:
            batch_requests.append(self.pending_requests.popleft())

        if not batch_requests:
            return

        try:
            # 準備批次輸入
            prompts = [req.prompt for req in batch_requests]

            # 批量編碼
            inputs = self.tokenizer(
                prompts,
                padding=True,
                return_tensors="pt"
            ).to(self.model.device)

            # 批量生成
            with torch.inference_mode():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=batch_requests[0].max_new_tokens,
                    temperature=batch_requests[0].temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                )

            # 解碼並返回結果
            for i, request in enumerate(batch_requests):
                generated_text = self.tokenizer.decode(
                    outputs[i],
                    skip_special_tokens=True
                )
                request.future.set_result(generated_text)

        except Exception as e:
            # 處理錯誤
            for request in batch_requests:
                request.future.set_exception(e)

# 使用
service = BatchingModelService(model, tokenizer)

# 並發請求會自動批處理
results = await asyncio.gather(*[
    service.generate(f"Prompt {i}") for i in range(100)
])
```
    """)


def monitoring_and_logging():
    """
    監控和日誌
    """
    print("\n" + "=" * 70)
    print("監控和日誌")
    print("=" * 70)

    print("""
1. Prometheus 指標：

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response
import time

# 定義指標
request_count = Counter(
    'inference_requests_total',
    'Total inference requests'
)

request_latency = Histogram(
    'inference_latency_seconds',
    'Inference request latency',
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

gpu_memory = Gauge(
    'gpu_memory_allocated_bytes',
    'GPU memory allocated'
)

active_requests = Gauge(
    'active_requests',
    'Number of active requests'
)

@app.post("/generate")
async def generate(request: GenerateRequest):
    request_count.inc()
    active_requests.inc()

    start = time.time()
    try:
        response = await model_manager.generate(request)
        return response
    finally:
        request_latency.observe(time.time() - start)
        active_requests.dec()
        gpu_memory.set(torch.cuda.memory_allocated())

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

2. 結構化日誌：

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

# 配置日誌
logger = logging.getLogger("inference")
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# 使用
@app.post("/generate")
async def generate(request: GenerateRequest):
    logger.info("Inference request received", extra={
        "prompt_length": len(request.prompt),
        "max_new_tokens": request.max_new_tokens
    })

    try:
        response = await model_manager.generate(request)
        logger.info("Inference completed", extra={
            "latency_ms": response.latency_ms,
            "tokens_generated": response.tokens_generated
        })
        return response
    except Exception as e:
        logger.error(f"Inference failed: {str(e)}", exc_info=True)
        raise
```

3. 性能追蹤：

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

# 設置追蹤
provider = TracerProvider()
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

@app.post("/generate")
async def generate(request: GenerateRequest):
    with tracer.start_as_current_span("inference_request") as span:
        span.set_attribute("prompt_length", len(request.prompt))
        span.set_attribute("max_new_tokens", request.max_new_tokens)

        response = await model_manager.generate(request)

        span.set_attribute("tokens_generated", response.tokens_generated)
        span.set_attribute("latency_ms", response.latency_ms)

        return response
```
    """)


def deployment_best_practices():
    """
    部署最佳實踐
    """
    print("\n" + "=" * 70)
    print("部署最佳實踐")
    print("=" * 70)

    practices = {
        "1. 模型優化": [
            "合併所有適配器（merge_and_unload）",
            "使用 BF16/FP16 混合精度",
            "考慮量化（INT8/INT4）用於推理",
            "啟用 torch.compile（PyTorch 2.0+）",
        ],
        "2. 服務配置": [
            "使用異步框架（FastAPI, aiohttp）",
            "實現動態批處理",
            "設置合理的超時時間",
            "配置連接池和重試策略",
        ],
        "3. 資源管理": [
            "限制並發請求數",
            "監控 GPU 顯存使用",
            "實現優雅關閉",
            "使用健康檢查和自動重啟",
        ],
        "4. 安全性": [
            "實現速率限制",
            "添加身份驗證（API key, JWT）",
            "輸入驗證和清理",
            "日誌脫敏",
        ],
        "5. 可觀測性": [
            "集成 Prometheus 指標",
            "結構化日誌（JSON）",
            "分布式追蹤（OpenTelemetry）",
            "告警配置",
        ],
        "6. 擴展性": [
            "使用負載均衡器",
            "支持水平擴展",
            "實現緩存機制",
            "考慮模型分片（大模型）",
        ],
        "7. 容錯": [
            "實現重試邏輯",
            "熔斷器模式",
            "降級策略",
            "備份模型服務",
        ],
    }

    for title, items in practices.items():
        print(f"\n{title}:")
        for item in items:
            print(f"  • {item}")


def docker_deployment():
    """
    Docker 部署
    """
    print("\n" + "=" * 70)
    print("Docker 部署")
    print("=" * 70)

    print("""
1. Dockerfile：

```dockerfile
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# 安裝 Python
RUN apt-get update && apt-get install -y python3.10 python3-pip

# 設置工作目錄
WORKDIR /app

# 複製需求文件
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY . .

# 下載模型（或從volume掛載）
# RUN python3 download_model.py

# 暴露端口
EXPOSE 8000

# 啟動命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. docker-compose.yml：

```yaml
version: '3.8'

services:
  inference:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
    environment:
      - CUDA_VISIBLE_DEVICES=0
      - MODEL_PATH=/app/models/merged_model
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

3. 構建和運行：

```bash
# 構建
docker build -t peft-inference .

# 運行
docker run --gpus all -p 8000:8000 peft-inference

# 使用 docker-compose
docker-compose up -d
```
    """)


def kubernetes_deployment():
    """
    Kubernetes 部署
    """
    print("\n" + "=" * 70)
    print("Kubernetes 部署")
    print("=" * 70)

    print("""
1. Deployment 配置：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: peft-inference
spec:
  replicas: 3
  selector:
    matchLabels:
      app: peft-inference
  template:
    metadata:
      labels:
        app: peft-inference
    spec:
      containers:
      - name: inference
        image: your-registry/peft-inference:latest
        ports:
        - containerPort: 8000
        resources:
          limits:
            nvidia.com/gpu: 1
            memory: "16Gi"
            cpu: "4"
          requests:
            nvidia.com/gpu: 1
            memory: "8Gi"
            cpu: "2"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        env:
        - name: MODEL_PATH
          value: "/models/merged_model"
        volumeMounts:
        - name: model-storage
          mountPath: /models
      volumes:
      - name: model-storage
        persistentVolumeClaim:
          claimName: model-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: peft-inference-service
spec:
  selector:
    app: peft-inference
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: peft-inference-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: peft-inference
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

2. 部署：

```bash
# 應用配置
kubectl apply -f deployment.yaml

# 檢查狀態
kubectl get pods
kubectl get svc

# 查看日誌
kubectl logs -f deployment/peft-inference

# 擴展
kubectl scale deployment peft-inference --replicas=5
```
    """)


def main():
    """
    主函數：生產部署完整指南
    """
    print("=" * 70)
    print("PEFT 生產部署完整指南")
    print("=" * 70)

    # 1. 架構設計
    deployment_architecture()

    # 2. REST API
    create_rest_api()

    # 3. 批處理服務
    batching_service()

    # 4. 監控日誌
    monitoring_and_logging()

    # 5. 最佳實踐
    deployment_best_practices()

    # 6. Docker 部署
    docker_deployment()

    # 7. Kubernetes 部署
    kubernetes_deployment()

    # 8. 總結
    print("\n" + "=" * 70)
    print("總結")
    print("=" * 70)
    print("""
PEFT 生產部署關鍵要點：

1. 部署前準備：
   ✓ 合併適配器
   ✓ 優化模型（BF16, 量化）
   ✓ 性能基準測試
   ✓ 負載測試

2. 服務設計：
   ✓ 異步 API（FastAPI）
   ✓ 動態批處理
   ✓ 健康檢查
   ✓ 優雅關閉

3. 性能優化：
   ✓ 批處理（5-10x 吞吐量提升）
   ✓ 混合精度（2x 加速）
   ✓ KV 緩存
   ✓ torch.compile

4. 可觀測性：
   ✓ Prometheus 指標
   ✓ 結構化日誌
   ✓ 分布式追蹤
   ✓ 告警配置

5. 容器化：
   ✓ Docker 鏡像
   ✓ GPU 支持
   ✓ 健康檢查
   ✓ 資源限制

6. 編排：
   ✓ Kubernetes deployment
   ✓ 自動擴展（HPA）
   ✓ 負載均衡
   ✓ 滾動更新

7. 安全性：
   ✓ 身份驗證
   ✓ 速率限制
   ✓ 輸入驗證
   ✓ 日誌脫敏

生產檢查清單：
□ 模型已優化和測試
□ API 已實現並測試
□ 監控和日誌已配置
□ 錯誤處理和重試已實現
□ 資源限制已設置
□ 健康檢查已配置
□ 文檔已完善
□ 負載測試已通過
□ 安全審查已完成
□ 備份和恢復計劃已制定
    """)

    print("\n資源:")
    print("  • FastAPI 文檔: https://fastapi.tiangolo.com/")
    print("  • Kubernetes 文檔: https://kubernetes.io/docs/")
    print("  • Prometheus: https://prometheus.io/")
    print("  • NVIDIA Triton: https://github.com/triton-inference-server")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用戶中斷")
    except Exception as e:
        print(f"\n程序執行出錯: {e}")
        import traceback
        traceback.print_exc()
