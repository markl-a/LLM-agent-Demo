"""
Outlines 生產部署示例
====================

本示例展示如何將 Outlines 部署到生產環境。

主要內容:
1. FastAPI 服務搭建
2. 模型緩存和預熱
3. 負載均衡
4. 監控和日誌
5. 錯誤處理和重試

作者: Outlines 教學團隊
日期: 2025-01
"""

import outlines
from outlines import models, generate
import torch
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
import json
import time
import sys
import asyncio
from functools import lru_cache
from collections import defaultdict
import threading
from queue import Queue, Empty
from enum import Enum

# ==================== 設置日誌 ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('production.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


# ==================== 請求和響應模型 ====================

class GenerationRequest(BaseModel):
    """生成請求模型"""
    prompt: str = Field(description="提示文本", min_length=1)
    schema_type: str = Field(description="Schema 類型")
    parameters: Optional[Dict[str, Any]] = Field(None, description="額外參數")


class GenerationResponse(BaseModel):
    """生成響應模型"""
    request_id: str = Field(description="請求ID")
    result: Dict[str, Any] = Field(description="生成結果")
    generation_time: float = Field(description="生成耗時(秒)")
    timestamp: str = Field(description="時間戳")


class HealthResponse(BaseModel):
    """健康檢查響應"""
    status: str = Field(description="狀態")
    model_loaded: bool = Field(description="模型是否已載入")
    gpu_available: bool = Field(description="GPU 是否可用")
    uptime_seconds: float = Field(description="運行時間(秒)")
    total_requests: int = Field(description="總請求數")
    avg_response_time: float = Field(description="平均響應時間(秒)")


class MetricsResponse(BaseModel):
    """指標響應"""
    total_requests: int = Field(description="總請求數")
    successful_requests: int = Field(description="成功請求數")
    failed_requests: int = Field(description="失敗請求數")
    avg_response_time: float = Field(description="平均響應時間")
    requests_per_minute: float = Field(description="每分鐘請求數")
    cache_hit_rate: float = Field(description="緩存命中率")


# ==================== 業務模型 ====================

class UserProfile(BaseModel):
    """用戶資料"""
    name: str = Field(description="姓名")
    email: str = Field(description="郵箱")
    age: int = Field(description="年齡", ge=0, le=120)
    interests: List[str] = Field(description="興趣")


class ProductInfo(BaseModel):
    """產品信息"""
    name: str = Field(description="產品名稱")
    description: str = Field(description="產品描述")
    price: float = Field(description="價格", gt=0)
    category: str = Field(description="類別")
    tags: List[str] = Field(description="標籤")


class ArticleSummary(BaseModel):
    """文章摘要"""
    title: str = Field(description="標題")
    summary: str = Field(description="摘要")
    key_points: List[str] = Field(description="要點")
    sentiment: str = Field(description="情感")


class CustomerIntent(BaseModel):
    """客戶意圖"""
    intent_type: str = Field(description="意圖類型")
    confidence: float = Field(description="置信度", ge=0, le=1)
    entities: Dict[str, str] = Field(description="實體")
    suggested_action: str = Field(description="建議操作")


# ==================== 模型管理器 ====================

class ModelManager:
    """
    模型管理器

    單例模式管理模型實例
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.model = None
        self.model_name = "mistralai/Mistral-7B-v0.1"
        self.generators: Dict[str, Any] = {}
        self.schema_registry: Dict[str, type[BaseModel]] = {
            "user_profile": UserProfile,
            "product_info": ProductInfo,
            "article_summary": ArticleSummary,
            "customer_intent": CustomerIntent
        }

        self._initialized = True
        logger.info("模型管理器初始化完成")

    def load_model(self):
        """載入模型"""
        if self.model is not None:
            logger.info("模型已載入,跳過")
            return

        try:
            logger.info(f"載入模型: {self.model_name}")
            start_time = time.time()

            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = models.transformers(self.model_name, device=device)

            # 預熱生成器
            self._warmup_generators()

            load_time = time.time() - start_time
            logger.info(f"模型載入完成,耗時: {load_time:.2f}秒")

        except Exception as e:
            logger.error(f"模型載入失敗: {str(e)}")
            raise

    def _warmup_generators(self):
        """預熱生成器"""
        logger.info("預熱生成器...")

        for schema_name, schema in self.schema_registry.items():
            self.generators[schema_name] = generate.json(self.model, schema)

        logger.info("生成器預熱完成")

    def get_generator(self, schema_type: str) -> Any:
        """
        獲取生成器

        Args:
            schema_type: Schema 類型

        Returns:
            生成器

        Raises:
            ValueError: 未知的 Schema 類型
        """
        if schema_type not in self.generators:
            raise ValueError(f"未知的 Schema 類型: {schema_type}")

        return self.generators[schema_type]

    def is_loaded(self) -> bool:
        """檢查模型是否已載入"""
        return self.model is not None


# ==================== 緩存管理器 ====================

class CacheManager:
    """
    緩存管理器

    管理生成結果緩存
    """

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        初始化緩存管理器

        Args:
            max_size: 最大緩存條目數
            ttl_seconds: 緩存有效期(秒)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, tuple[Any, datetime]] = {}
        self.hits = 0
        self.misses = 0
        self._lock = threading.Lock()

        logger.info(f"緩存管理器初始化完成, 大小: {max_size}, TTL: {ttl_seconds}秒")

    def get(self, key: str) -> Optional[Any]:
        """
        獲取緩存

        Args:
            key: 緩存鍵

        Returns:
            緩存值或 None
        """
        with self._lock:
            if key in self.cache:
                value, timestamp = self.cache[key]

                # 檢查是否過期
                if datetime.now() - timestamp < timedelta(seconds=self.ttl_seconds):
                    self.hits += 1
                    logger.debug(f"緩存命中: {key}")
                    return value
                else:
                    # 刪除過期條目
                    del self.cache[key]

            self.misses += 1
            logger.debug(f"緩存未命中: {key}")
            return None

    def set(self, key: str, value: Any):
        """
        設置緩存

        Args:
            key: 緩存鍵
            value: 緩存值
        """
        with self._lock:
            # 如果緩存已滿,刪除最舊的條目
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
                del self.cache[oldest_key]

            self.cache[key] = (value, datetime.now())
            logger.debug(f"緩存已設置: {key}")

    def get_hit_rate(self) -> float:
        """
        獲取緩存命中率

        Returns:
            命中率(0-1)
        """
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def clear(self):
        """清空緩存"""
        with self._lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0
            logger.info("緩存已清空")


# ==================== 指標收集器 ====================

class MetricsCollector:
    """
    指標收集器

    收集和統計服務指標
    """

    def __init__(self):
        """初始化指標收集器"""
        self.start_time = datetime.now()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.response_times: List[float] = []
        self.request_timestamps: List[datetime] = []
        self._lock = threading.Lock()

        logger.info("指標收集器初始化完成")

    def record_request(self, success: bool, response_time: float):
        """
        記錄請求

        Args:
            success: 是否成功
            response_time: 響應時間(秒)
        """
        with self._lock:
            self.total_requests += 1

            if success:
                self.successful_requests += 1
            else:
                self.failed_requests += 1

            self.response_times.append(response_time)
            self.request_timestamps.append(datetime.now())

            # 保留最近 1000 條記錄
            if len(self.response_times) > 1000:
                self.response_times = self.response_times[-1000:]
                self.request_timestamps = self.request_timestamps[-1000:]

    def get_metrics(self) -> MetricsResponse:
        """
        獲取指標

        Returns:
            指標響應
        """
        with self._lock:
            # 計算每分鐘請求數
            now = datetime.now()
            recent_requests = [
                ts for ts in self.request_timestamps
                if now - ts < timedelta(minutes=1)
            ]
            requests_per_minute = len(recent_requests)

            # 計算平均響應時間
            avg_response_time = (
                sum(self.response_times) / len(self.response_times)
                if self.response_times else 0.0
            )

            return MetricsResponse(
                total_requests=self.total_requests,
                successful_requests=self.successful_requests,
                failed_requests=self.failed_requests,
                avg_response_time=avg_response_time,
                requests_per_minute=requests_per_minute,
                cache_hit_rate=0.0  # 將由應用層填充
            )

    def get_uptime(self) -> float:
        """
        獲取運行時間

        Returns:
            運行時間(秒)
        """
        return (datetime.now() - self.start_time).total_seconds()


# ==================== FastAPI 應用 ====================

app = FastAPI(
    title="Outlines 生產服務",
    description="基於 Outlines 的結構化生成 API 服務",
    version="1.0.0"
)

# 添加 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局實例
model_manager = ModelManager()
cache_manager = CacheManager()
metrics_collector = MetricsCollector()


# ==================== 依賴項 ====================

def get_model_manager() -> ModelManager:
    """獲取模型管理器"""
    return model_manager


def get_cache_manager() -> CacheManager:
    """獲取緩存管理器"""
    return cache_manager


def get_metrics_collector() -> MetricsCollector:
    """獲取指標收集器"""
    return metrics_collector


# ==================== 啟動事件 ====================

@app.on_event("startup")
async def startup_event():
    """啟動事件"""
    logger.info("服務啟動中...")

    # 載入模型
    try:
        model_manager.load_model()
        logger.info("服務啟動完成")
    except Exception as e:
        logger.error(f"服務啟動失敗: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """關閉事件"""
    logger.info("服務關閉中...")
    cache_manager.clear()
    logger.info("服務已關閉")


# ==================== API 端點 ====================

@app.get("/", response_model=dict)
async def root():
    """根端點"""
    return {
        "service": "Outlines 生產服務",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check(
    manager: ModelManager = Depends(get_model_manager),
    metrics: MetricsCollector = Depends(get_metrics_collector)
):
    """健康檢查"""
    m = metrics.get_metrics()

    return HealthResponse(
        status="healthy" if manager.is_loaded() else "unhealthy",
        model_loaded=manager.is_loaded(),
        gpu_available=torch.cuda.is_available(),
        uptime_seconds=metrics.get_uptime(),
        total_requests=m.total_requests,
        avg_response_time=m.avg_response_time
    )


@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics(
    cache: CacheManager = Depends(get_cache_manager),
    metrics: MetricsCollector = Depends(get_metrics_collector)
):
    """獲取服務指標"""
    m = metrics.get_metrics()

    return MetricsResponse(
        total_requests=m.total_requests,
        successful_requests=m.successful_requests,
        failed_requests=m.failed_requests,
        avg_response_time=m.avg_response_time,
        requests_per_minute=m.requests_per_minute,
        cache_hit_rate=cache.get_hit_rate()
    )


@app.post("/generate", response_model=GenerationResponse)
async def generate(
    request: GenerationRequest,
    manager: ModelManager = Depends(get_model_manager),
    cache: CacheManager = Depends(get_cache_manager),
    metrics: MetricsCollector = Depends(get_metrics_collector)
):
    """
    生成結構化輸出

    Args:
        request: 生成請求

    Returns:
        生成響應
    """
    request_id = f"{int(time.time() * 1000)}"
    start_time = time.time()

    try:
        # 檢查模型是否已載入
        if not manager.is_loaded():
            raise HTTPException(status_code=503, detail="模型未載入")

        # 生成緩存鍵
        cache_key = f"{request.schema_type}:{hash(request.prompt)}"

        # 檢查緩存
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.info(f"使用緩存結果: {request_id}")

            response_time = time.time() - start_time
            metrics.record_request(True, response_time)

            return GenerationResponse(
                request_id=request_id,
                result=cached_result,
                generation_time=response_time,
                timestamp=datetime.now().isoformat()
            )

        # 獲取生成器
        generator = manager.get_generator(request.schema_type)

        # 生成結果
        result = generator(request.prompt)
        result_dict = result.dict()

        # 緩存結果
        cache.set(cache_key, result_dict)

        # 記錄指標
        response_time = time.time() - start_time
        metrics.record_request(True, response_time)

        logger.info(f"請求完成: {request_id}, 耗時: {response_time:.2f}秒")

        return GenerationResponse(
            request_id=request_id,
            result=result_dict,
            generation_time=response_time,
            timestamp=datetime.now().isoformat()
        )

    except ValueError as e:
        response_time = time.time() - start_time
        metrics.record_request(False, response_time)
        logger.error(f"請求失敗: {request_id}, 錯誤: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        response_time = time.time() - start_time
        metrics.record_request(False, response_time)
        logger.error(f"請求失敗: {request_id}, 錯誤: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="內部服務器錯誤")


@app.post("/batch_generate")
async def batch_generate(
    requests: List[GenerationRequest],
    manager: ModelManager = Depends(get_model_manager),
    cache: CacheManager = Depends(get_cache_manager),
    metrics: MetricsCollector = Depends(get_metrics_collector)
):
    """
    批量生成

    Args:
        requests: 請求列表

    Returns:
        響應列表
    """
    if len(requests) > 100:
        raise HTTPException(status_code=400, detail="批量大小不能超過 100")

    results = []

    for req in requests:
        try:
            response = await generate(req, manager, cache, metrics)
            results.append(response)
        except HTTPException as e:
            results.append({
                "error": e.detail,
                "status_code": e.status_code
            })

    return {"results": results, "total": len(requests)}


@app.delete("/cache")
async def clear_cache(
    cache: CacheManager = Depends(get_cache_manager)
):
    """清空緩存"""
    cache.clear()
    return {"message": "緩存已清空"}


# ==================== 主程序 ====================

def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    workers: int = 1
):
    """
    運行服務器

    Args:
        host: 主機地址
        port: 端口號
        workers: Worker 數量
    """
    logger.info(f"啟動服務器: {host}:{port}, workers: {workers}")

    uvicorn.run(
        app,
        host=host,
        port=port,
        workers=workers,
        log_level="info"
    )


def main():
    """主函數"""
    print("\n" + "="*60)
    print("Outlines 生產部署示例")
    print("="*60)

    print("\n啟動選項:")
    print("1. 啟動服務器")
    print("2. 查看使用文檔")
    print("3. 運行測試")

    choice = input("\n請選擇 (1-3): ")

    if choice == "1":
        run_server()

    elif choice == "2":
        print("\n使用文檔:")
        print("\nAPI 端點:")
        print("  GET  /          - 服務信息")
        print("  GET  /health    - 健康檢查")
        print("  GET  /metrics   - 服務指標")
        print("  POST /generate  - 生成結構化輸出")
        print("  POST /batch_generate - 批量生成")
        print("  DELETE /cache   - 清空緩存")

        print("\n示例請求:")
        print("""
curl -X POST "http://localhost:8000/generate" \\
  -H "Content-Type: application/json" \\
  -d '{
    "prompt": "生成一個用戶資料",
    "schema_type": "user_profile"
  }'
        """)

    elif choice == "3":
        print("\n運行測試...")
        print("請先啟動服務器,然後運行:")
        print("  pytest tests/")

    else:
        print("無效的選擇")


if __name__ == "__main__":
    main()
