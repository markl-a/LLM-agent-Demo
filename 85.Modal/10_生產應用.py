"""
Modal 生產應用示例

本示例展示：
1. 完整的生產級應用架構
2. 錯誤處理和重試
3. 監控和日誌
4. 最佳實踐集成
"""

import modal
from rich.console import Console
from rich.panel import Panel
import logging
from datetime import datetime

console = Console()

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============= 應用配置 =============

app = modal.App("production-app")

# 生產環境鏡像
production_image = modal.Image.debian_slim().pip_install(
    "fastapi",
    "pydantic",
    "torch",
    "transformers",
    "prometheus-client",
    "sentry-sdk"
)

# 持久化存儲
model_volume = modal.Volume.from_name("production-models", create_if_missing=True)
cache_dict = modal.Dict.from_name("production-cache", create_if_missing=True)

# Secrets（實際生產中從 Modal Dashboard 創建）
app_secrets = [
    modal.Secret.from_dict({
        "SENTRY_DSN": "https://xxx@sentry.io/xxx",
        "API_KEY": "production-api-key",
        "DATABASE_URL": "postgresql://..."
    })
]


# ============= 生產級模型服務 =============

@app.cls(
    gpu="T4",
    image=production_image,
    volumes={"/models": model_volume},
    secrets=app_secrets,
    container_idle_timeout=300,  # 5 分鐘空閒後停止
    retries=3,  # 失敗重試 3 次
    timeout=60  # 60 秒超時
)
class ProductionModel:
    """生產級模型服務"""

    def __enter__(self):
        """容器啟動時初始化"""
        import os
        import sentry_sdk

        # 初始化錯誤追蹤
        sentry_dsn = os.getenv("SENTRY_DSN")
        if sentry_dsn and sentry_dsn != "https://xxx@sentry.io/xxx":
            sentry_sdk.init(sentry_dsn)
            logger.info("Sentry initialized")

        # 加載模型
        logger.info("Loading production model...")

        try:
            from transformers import pipeline

            self.model = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=0
            )

            logger.info("Model loaded successfully")
            self.model_loaded = True

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model_loaded = False
            raise

        # 初始化指標
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0
        }

    @modal.method()
    def predict(self, text: str, request_id: str = None) -> dict:
        """
        執行預測（帶完整的錯誤處理和日誌）

        Args:
            text: 輸入文本
            request_id: 請求 ID（用於追蹤）

        Returns:
            預測結果
        """
        import time

        # 生成請求 ID
        if not request_id:
            request_id = f"{datetime.now().timestamp()}-{hash(text) % 10000}"

        # 記錄請求
        logger.info(f"[{request_id}] Processing request")
        self.metrics["total_requests"] += 1

        # 檢查模型是否已加載
        if not self.model_loaded:
            logger.error(f"[{request_id}] Model not loaded")
            self.metrics["failed_requests"] += 1
            return {
                "request_id": request_id,
                "error": "Model not loaded",
                "status": "error"
            }

        # 驗證輸入
        if not text or len(text) == 0:
            logger.warning(f"[{request_id}] Empty input")
            self.metrics["failed_requests"] += 1
            return {
                "request_id": request_id,
                "error": "Empty input",
                "status": "error"
            }

        if len(text) > 512:
            logger.warning(f"[{request_id}] Input too long: {len(text)} chars")
            return {
                "request_id": request_id,
                "error": "Input exceeds 512 characters",
                "status": "error"
            }

        # 檢查緩存
        cache_key = f"pred:{hash(text)}"
        try:
            cached_result = cache_dict.get(cache_key)
            if cached_result:
                logger.info(f"[{request_id}] Cache hit")
                self.metrics["successful_requests"] += 1
                return {
                    **cached_result,
                    "request_id": request_id,
                    "cached": True
                }
        except:
            pass

        # 執行預測
        try:
            start_time = time.time()

            result = self.model(text)[0]

            elapsed = time.time() - start_time

            # 構建響應
            response = {
                "request_id": request_id,
                "text": text,
                "label": result["label"],
                "confidence": float(result["score"]),
                "latency_ms": round(elapsed * 1000, 2),
                "cached": False,
                "status": "success"
            }

            # 緩存結果
            try:
                cache_dict[cache_key] = {
                    "label": result["label"],
                    "confidence": float(result["score"])
                }
            except:
                logger.warning(f"[{request_id}] Failed to cache result")

            # 記錄成功
            logger.info(
                f"[{request_id}] Prediction: {result['label']} "
                f"({result['score']:.4f}) in {elapsed*1000:.2f}ms"
            )
            self.metrics["successful_requests"] += 1

            return response

        except Exception as e:
            # 錯誤處理
            logger.error(f"[{request_id}] Prediction failed: {e}", exc_info=True)
            self.metrics["failed_requests"] += 1

            return {
                "request_id": request_id,
                "error": str(e),
                "status": "error"
            }

    @modal.method()
    def batch_predict(self, texts: list) -> list:
        """批量預測"""
        logger.info(f"Batch prediction: {len(texts)} texts")

        results = []
        for i, text in enumerate(texts):
            request_id = f"batch-{datetime.now().timestamp()}-{i}"
            result = self.predict(text, request_id)
            results.append(result)

        return results

    @modal.method()
    def health_check(self) -> dict:
        """健康檢查"""
        return {
            "status": "healthy" if self.model_loaded else "unhealthy",
            "model_loaded": self.model_loaded,
            "metrics": self.metrics,
            "timestamp": datetime.now().isoformat()
        }


# ============= Web API 端點 =============

@app.function(
    image=production_image,
    secrets=app_secrets,
    retries=2
)
@modal.web_endpoint(method="POST")
def predict_api(request: dict):
    """
    生產級預測 API

    POST /predict_api
    {
        "text": "要分析的文本"
    }
    """
    # 驗證請求
    if "text" not in request:
        logger.warning("Missing text field")
        return {"error": "Missing 'text' field"}, 400

    text = request["text"]

    # 調用模型
    model = ProductionModel()
    result = model.predict.remote(text)

    # 返回結果
    if result["status"] == "error":
        return result, 500
    else:
        return result, 200


@app.function(
    image=production_image,
    secrets=app_secrets
)
@modal.web_endpoint(method="POST")
def batch_predict_api(request: dict):
    """
    批量預測 API

    POST /batch_predict_api
    {
        "texts": ["text1", "text2", ...]
    }
    """
    # 驗證請求
    if "texts" not in request:
        return {"error": "Missing 'texts' field"}, 400

    texts = request["texts"]

    if not isinstance(texts, list):
        return {"error": "'texts' must be a list"}, 400

    if len(texts) > 100:
        return {"error": "Maximum 100 texts per request"}, 400

    # 批量預測
    model = ProductionModel()
    results = model.batch_predict.remote(texts)

    return {
        "count": len(results),
        "results": results
    }, 200


@app.function(image=production_image)
@modal.web_endpoint(method="GET")
def health():
    """健康檢查端點"""
    model = ProductionModel()
    health_status = model.health_check.remote()

    status_code = 200 if health_status["status"] == "healthy" else 503

    return health_status, status_code


# ============= 定時任務 =============

@app.function(
    schedule=modal.Period(hours=1),
    image=production_image,
    secrets=app_secrets
)
def cleanup_cache():
    """每小時清理過期緩存"""
    logger.info("Running cache cleanup...")

    # 清理邏輯（這裡只是示例）
    cleaned = 0

    try:
        # 實際應用中會檢查時間戳並刪除過期項
        logger.info(f"Cleaned {cleaned} cache entries")

        return {
            "cleaned": cleaned,
            "status": "success"
        }

    except Exception as e:
        logger.error(f"Cache cleanup failed: {e}")
        return {
            "error": str(e),
            "status": "error"
        }


@app.function(
    schedule=modal.Cron("0 0 * * *"),  # 每天午夜
    image=production_image,
    secrets=app_secrets
)
def daily_metrics_report():
    """每日指標報告"""
    logger.info("Generating daily metrics report...")

    # 收集指標
    model = ProductionModel()
    metrics = model.health_check.remote()

    # 發送報告（實際應用中會發送郵件或推送到監控系統）
    logger.info(f"Daily metrics: {metrics}")

    return metrics


# ============= 本地測試 =============

@app.local_entrypoint()
def main():
    """本地測試入口"""
    console.print(Panel.fit(
        "[bold cyan]Modal 生產應用示例[/bold cyan]\n"
        "[dim]完整的生產級架構[/dim]",
        border_style="cyan"
    ))

    # 測試模型
    console.print("\n[cyan]1. 測試模型預測[/cyan]")
    model = ProductionModel()

    # 單個預測
    result = model.predict.remote("This is an amazing product!")
    console.print(f"[green]結果: {result}[/green]")

    # 批量預測
    console.print("\n[cyan]2. 測試批量預測[/cyan]")
    texts = [
        "I love this!",
        "This is terrible.",
        "It's okay."
    ]
    results = model.batch_predict.remote(texts)
    for r in results:
        console.print(f"[green]  {r}[/green]")

    # 健康檢查
    console.print("\n[cyan]3. 健康檢查[/cyan]")
    health_status = model.health_check.remote()
    console.print(f"[green]{health_status}[/green]")

    console.print("\n" + "="*60)
    console.print("[bold green]✓ 生產應用測試完成！[/bold green]")


def print_production_guide():
    """打印生產部署指南"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]生產部署指南:[/bold cyan]")
    console.print("""
[green]1. 環境配置:[/green]

# 創建 Secrets
modal secret create prod-secrets \\
  SENTRY_DSN=xxx \\
  API_KEY=yyy \\
  DATABASE_URL=zzz

# 創建 Volume
modal volume create production-models

[green]2. 部署:[/green]

# 部署到生產環境
modal deploy 10_生產應用.py

# 查看部署狀態
modal app list

# 查看日誌
modal app logs production-app

[green]3. 監控:[/green]

# 健康檢查
curl https://your-app--health.modal.run

# 查看指標
modal app logs production-app --tail

[green]4. 測試 API:[/green]

# 單個預測
curl -X POST https://your-app--predict-api.modal.run \\
  -H "Content-Type: application/json" \\
  -d '{"text": "I love this product!"}'

# 批量預測
curl -X POST https://your-app--batch-predict-api.modal.run \\
  -H "Content-Type: application/json" \\
  -d '{"texts": ["text1", "text2"]}'

[yellow]生產最佳實踐:[/yellow]

✓ 完整的錯誤處理和日誌
✓ 使用 Sentry 等錯誤追蹤服務
✓ 實施請求 ID 追蹤
✓ 緩存常見請求
✓ 設置合理的超時和重試
✓ 實施速率限制
✓ 監控指標和告警
✓ 定期備份數據
✓ 藍綠部署策略
✓ 負載測試

[yellow]安全性:[/yellow]

✓ 使用 Secrets 管理敏感信息
✓ API 密鑰認證
✓ 輸入驗證和過濾
✓ 速率限制
✓ HTTPS（Modal 默認）
✓ 定期更新依賴

[yellow]成本優化:[/yellow]

✓ 設置 container_idle_timeout
✓ 使用緩存減少計算
✓ 批量處理提升效率
✓ 選擇合適的 GPU 型號
✓ 監控使用量
✓ 設置預算告警
    """)
    console.print("="*60 + "\n")


if __name__ == "__main__":
    print_production_guide()

    console.print("[yellow]本地測試:[/yellow]")
    console.print("  modal run 10_生產應用.py\n")

    console.print("[yellow]部署到生產:[/yellow]")
    console.print("  modal deploy 10_生產應用.py\n")

    console.print("[bold red]重要提示:[/bold red]")
    console.print("  1. 先在 Modal Dashboard 創建真實的 Secrets")
    console.print("  2. 配置 Sentry 或其他監控服務")
    console.print("  3. 進行充分的測試")
    console.print("  4. 設置預算告警\n")
