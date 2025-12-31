"""
ControlFlow 生產部署詳解
========================

本文件深入探討 ControlFlow 在生產環境的部署和最佳實踐,包括:
1. 環境配置
2. 日誌和監控
3. 性能優化
4. 安全配置
5. 擴展性設計
6. 容器化部署
7. CI/CD 整合

作者: ControlFlow 示例團隊
日期: 2025
"""

import os
import sys
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path
from enum import Enum
import controlflow as cf
from controlflow import Agent, Task, Flow
from pydantic import BaseModel, Field, SecretStr
from dotenv import load_dotenv


# ========== 配置管理 ==========

class Environment(str, Enum):
    """環境類型"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class DatabaseConfig(BaseModel):
    """數據庫配置"""
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    database: str
    username: str
    password: SecretStr
    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)


class RedisConfig(BaseModel):
    """Redis 配置"""
    host: str = Field(default="localhost")
    port: int = Field(default=6379)
    password: Optional[SecretStr] = None
    db: int = Field(default=0)
    max_connections: int = Field(default=50)


class MonitoringConfig(BaseModel):
    """監控配置"""
    enabled: bool = Field(default=True)
    metrics_port: int = Field(default=9090)
    health_check_interval: int = Field(default=30)
    log_level: str = Field(default="INFO")


class ProductionConfig(BaseModel):
    """生產環境配置"""
    environment: Environment
    app_name: str = Field(default="controlflow-app")
    version: str = Field(default="1.0.0")

    # API 配置
    openai_api_key: SecretStr
    openai_api_base: str = Field(default="https://api.openai.com/v1")
    openai_timeout: int = Field(default=60)
    max_retries: int = Field(default=3)

    # 數據庫配置
    database: Optional[DatabaseConfig] = None

    # 緩存配置
    redis: Optional[RedisConfig] = None

    # 監控配置
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)

    # 性能配置
    max_concurrent_tasks: int = Field(default=10)
    task_timeout: int = Field(default=300)
    rate_limit_per_minute: int = Field(default=60)

    # 安全配置
    enable_tls: bool = Field(default=True)
    allowed_origins: List[str] = Field(default_factory=list)


class ConfigurationManager:
    """
    配置管理器

    管理不同環境的配置
    """

    def __init__(self, env: Environment = Environment.DEVELOPMENT):
        """
        初始化配置管理器

        Args:
            env: 運行環境
        """
        self.env = env
        self.config: Optional[ProductionConfig] = None

    def load_config(self, config_file: Optional[str] = None) -> ProductionConfig:
        """
        加載配置

        Args:
            config_file: 配置文件路徑

        Returns:
            ProductionConfig: 配置對象
        """
        print(f"🔧 加載 {self.env.value} 環境配置...")

        # 加載環境變量
        load_dotenv()

        if config_file and Path(config_file).exists():
            # 從文件加載
            with open(config_file, 'r') as f:
                config_data = json.load(f)

            self.config = ProductionConfig(**config_data)

        else:
            # 從環境變量加載
            self.config = ProductionConfig(
                environment=self.env,
                openai_api_key=os.getenv("OPENAI_API_KEY", ""),
                openai_api_base=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
                database=DatabaseConfig(
                    host=os.getenv("DB_HOST", "localhost"),
                    port=int(os.getenv("DB_PORT", "5432")),
                    database=os.getenv("DB_NAME", "controlflow"),
                    username=os.getenv("DB_USER", "user"),
                    password=os.getenv("DB_PASSWORD", "password")
                ) if os.getenv("DB_HOST") else None,
                redis=RedisConfig(
                    host=os.getenv("REDIS_HOST", "localhost"),
                    port=int(os.getenv("REDIS_PORT", "6379"))
                ) if os.getenv("REDIS_HOST") else None
            )

        print(f"   ✅ 配置加載完成")
        print(f"   環境: {self.config.environment.value}")
        print(f"   應用: {self.config.app_name} v{self.config.version}")

        return self.config

    def validate_config(self) -> bool:
        """
        驗證配置

        Returns:
            bool: 配置是否有效
        """
        print("\n🔍 驗證配置...")

        if not self.config:
            print("   ❌ 配置未加載")
            return False

        # 檢查必需配置
        if not self.config.openai_api_key:
            print("   ❌ 缺少 OpenAI API Key")
            return False

        # 生產環境額外檢查
        if self.config.environment == Environment.PRODUCTION:
            if not self.config.enable_tls:
                print("   ⚠️ 生產環境建議啟用 TLS")

            if not self.config.database:
                print("   ⚠️ 生產環境建議配置數據庫")

            if not self.config.redis:
                print("   ⚠️ 生產環境建議配置 Redis")

        print("   ✅ 配置驗證通過")
        return True

    def save_config(self, output_file: str):
        """
        保存配置到文件

        Args:
            output_file: 輸出文件路徑
        """
        if not self.config:
            print("❌ 無配置可保存")
            return

        print(f"💾 保存配置到: {output_file}")

        # 轉換為字典(排除敏感信息)
        config_dict = self.config.dict()

        # 移除密碼等敏感信息
        if config_dict.get("database"):
            config_dict["database"]["password"] = "***REDACTED***"

        if config_dict.get("redis") and config_dict["redis"].get("password"):
            config_dict["redis"]["password"] = "***REDACTED***"

        config_dict["openai_api_key"] = "***REDACTED***"

        with open(output_file, 'w') as f:
            json.dump(config_dict, f, indent=2)

        print("   ✅ 配置已保存")


# ========== 日誌和監控 ==========

class LoggingSetup:
    """
    日誌配置

    配置生產級日誌
    """

    @staticmethod
    def setup_logging(
        log_level: str = "INFO",
        log_file: Optional[str] = None,
        json_format: bool = False
    ):
        """
        設置日誌

        Args:
            log_level: 日誌級別
            log_file: 日誌文件路徑
            json_format: 是否使用 JSON 格式
        """
        print(f"📝 設置日誌系統...")
        print(f"   級別: {log_level}")
        print(f"   文件: {log_file or '控制台'}")

        # 創建日誌格式
        if json_format:
            # JSON 格式(適合日誌收集系統)
            formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
                '"logger": "%(name)s", "message": "%(message)s"}'
            )
        else:
            # 標準格式
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

        # 配置根日誌記錄器
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))

        # 清除現有處理器
        root_logger.handlers.clear()

        # 控制台處理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # 文件處理器
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        print("   ✅ 日誌系統已配置")

    @staticmethod
    def create_structured_logger(name: str) -> logging.Logger:
        """
        創建結構化日誌記錄器

        Args:
            name: 日誌記錄器名稱

        Returns:
            logging.Logger: 日誌記錄器
        """
        logger = logging.getLogger(name)

        # 添加自定義方法
        def log_with_context(level, message, **context):
            """帶上下文的日誌"""
            extra_info = " | ".join(f"{k}={v}" for k, v in context.items())
            full_message = f"{message} | {extra_info}" if context else message
            logger.log(level, full_message)

        logger.log_with_context = log_with_context

        return logger


class MonitoringSetup:
    """
    監控配置

    配置性能監控和健康檢查
    """

    def __init__(self):
        """初始化監控"""
        self.metrics: Dict[str, Any] = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_failed": 0,
            "avg_response_time": 0.0,
            "tasks_completed": 0,
            "tasks_failed": 0
        }

        self.logger = logging.getLogger(__name__)

    def record_request(self, success: bool, response_time: float):
        """
        記錄請求指標

        Args:
            success: 是否成功
            response_time: 響應時間
        """
        self.metrics["requests_total"] += 1

        if success:
            self.metrics["requests_success"] += 1
        else:
            self.metrics["requests_failed"] += 1

        # 更新平均響應時間
        total = self.metrics["requests_total"]
        current_avg = self.metrics["avg_response_time"]
        self.metrics["avg_response_time"] = (
            (current_avg * (total - 1) + response_time) / total
        )

    def record_task(self, success: bool):
        """
        記錄任務指標

        Args:
            success: 是否成功
        """
        if success:
            self.metrics["tasks_completed"] += 1
        else:
            self.metrics["tasks_failed"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """
        獲取指標

        Returns:
            Dict[str, Any]: 指標數據
        """
        return self.metrics.copy()

    def health_check(self) -> Dict[str, Any]:
        """
        健康檢查

        Returns:
            Dict[str, Any]: 健康狀態
        """
        # 計算成功率
        total_requests = self.metrics["requests_total"]
        success_rate = (
            self.metrics["requests_success"] / total_requests
            if total_requests > 0 else 1.0
        )

        # 計算任務成功率
        total_tasks = (
            self.metrics["tasks_completed"] + self.metrics["tasks_failed"]
        )
        task_success_rate = (
            self.metrics["tasks_completed"] / total_tasks
            if total_tasks > 0 else 1.0
        )

        # 判斷健康狀態
        is_healthy = (
            success_rate >= 0.95 and
            task_success_rate >= 0.90 and
            self.metrics["avg_response_time"] < 5.0
        )

        return {
            "status": "healthy" if is_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "success_rate": success_rate,
            "task_success_rate": task_success_rate,
            "avg_response_time": self.metrics["avg_response_time"],
            "metrics": self.metrics
        }


# ========== 性能優化 ==========

class PerformanceOptimization:
    """
    性能優化

    實現各種性能優化策略
    """

    def __init__(self):
        """初始化性能優化"""
        self.cache: Dict[str, Any] = {}
        self.cache_hits = 0
        self.cache_misses = 0

    def cached_execution(
        self,
        cache_key: str,
        operation: callable,
        ttl: int = 300
    ) -> Any:
        """
        帶緩存的執行

        Args:
            cache_key: 緩存鍵
            operation: 操作函數
            ttl: 緩存生存時間(秒)

        Returns:
            Any: 執行結果
        """
        # 檢查緩存
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            cache_time = cached_data["timestamp"]

            # 檢查是否過期
            age = (datetime.now() - cache_time).total_seconds()

            if age < ttl:
                self.cache_hits += 1
                print(f"   ✅ 緩存命中: {cache_key}")
                return cached_data["value"]

        # 執行操作
        self.cache_misses += 1
        print(f"   ⚠️ 緩存未命中: {cache_key}")

        result = operation()

        # 存入緩存
        self.cache[cache_key] = {
            "value": result,
            "timestamp": datetime.now()
        }

        return result

    def batch_processing(
        self,
        items: List[Any],
        process_fn: callable,
        batch_size: int = 10
    ) -> List[Any]:
        """
        批量處理

        Args:
            items: 項目列表
            process_fn: 處理函數
            batch_size: 批次大小

        Returns:
            List[Any]: 處理結果
        """
        print(f"⚡ 批量處理 {len(items)} 個項目 (批次: {batch_size})")

        results = []

        for i in range(0, len(items), batch_size):
            batch = items[i:i+batch_size]
            print(f"   處理批次 {i//batch_size + 1}...")

            batch_results = [process_fn(item) for item in batch]
            results.extend(batch_results)

        return results

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        獲取緩存統計

        Returns:
            Dict[str, Any]: 緩存統計信息
        """
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (
            self.cache_hits / total_requests
            if total_requests > 0 else 0
        )

        return {
            "cache_size": len(self.cache),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": hit_rate
        }


# ========== 安全配置 ==========

class SecuritySetup:
    """
    安全配置

    實現安全最佳實踐
    """

    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """
        驗證 API 密鑰

        Args:
            api_key: API 密鑰

        Returns:
            bool: 是否有效
        """
        # 基本驗證
        if not api_key or len(api_key) < 20:
            return False

        # 檢查格式(OpenAI 密鑰格式)
        if not api_key.startswith("sk-"):
            return False

        return True

    @staticmethod
    def sanitize_input(user_input: str) -> str:
        """
        清理用戶輸入

        Args:
            user_input: 用戶輸入

        Returns:
            str: 清理後的輸入
        """
        # 移除潛在危險字符
        dangerous_chars = ["<", ">", "&", "'", '"', ";"]

        sanitized = user_input

        for char in dangerous_chars:
            sanitized = sanitized.replace(char, "")

        return sanitized.strip()

    @staticmethod
    def rate_limit_check(
        user_id: str,
        requests: Dict[str, List[datetime]],
        max_per_minute: int = 60
    ) -> bool:
        """
        速率限制檢查

        Args:
            user_id: 用戶 ID
            requests: 請求歷史
            max_per_minute: 每分鐘最大請求數

        Returns:
            bool: 是否允許請求
        """
        now = datetime.now()
        one_minute_ago = now.timestamp() - 60

        # 獲取用戶的請求歷史
        user_requests = requests.get(user_id, [])

        # 清理過期記錄
        user_requests = [
            req for req in user_requests
            if req.timestamp() > one_minute_ago
        ]

        # 更新請求歷史
        requests[user_id] = user_requests

        # 檢查是否超過限制
        if len(user_requests) >= max_per_minute:
            return False

        # 添加新請求
        user_requests.append(now)

        return True


# ========== 部署腳本 ==========

class DeploymentScripts:
    """
    部署腳本

    生成部署相關的腳本和配置
    """

    @staticmethod
    def generate_dockerfile() -> str:
        """
        生成 Dockerfile

        Returns:
            str: Dockerfile 內容
        """
        return """
# ControlFlow Production Dockerfile

FROM python:3.11-slim

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# 複製依賴文件
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY . .

# 創建非 root 用戶
RUN useradd -m -u 1000 appuser && \\
    chown -R appuser:appuser /app

USER appuser

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# 暴露端口
EXPOSE 8000

# 啟動命令
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

    @staticmethod
    def generate_docker_compose() -> str:
        """
        生成 docker-compose.yml

        Returns:
            str: docker-compose 內容
        """
        return """
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DB_HOST=postgres
      - REDIS_HOST=redis
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=controlflow
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped

volumes:
  postgres_data:
"""

    @staticmethod
    def generate_kubernetes_deployment() -> str:
        """
        生成 Kubernetes 部署配置

        Returns:
            str: K8s 部署配置
        """
        return """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: controlflow-app
  labels:
    app: controlflow
spec:
  replicas: 3
  selector:
    matchLabels:
      app: controlflow
  template:
    metadata:
      labels:
        app: controlflow
    spec:
      containers:
      - name: controlflow
        image: controlflow:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: controlflow-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: controlflow-service
spec:
  selector:
    app: controlflow
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
"""


# ========== 主程序 ==========

def main():
    """
    主程序入口

    演示生產部署配置
    """
    print("=" * 70)
    print("  ControlFlow 生產部署示例")
    print("=" * 70)
    print()

    try:
        # 1. 配置管理
        print("\n" + "=" * 70)
        print("1. 配置管理")
        print("=" * 70 + "\n")

        config_mgr = ConfigurationManager(Environment.DEVELOPMENT)
        config = config_mgr.load_config()
        config_mgr.validate_config()

        print()

        # 2. 日誌設置
        print("\n" + "=" * 70)
        print("2. 日誌配置")
        print("=" * 70 + "\n")

        LoggingSetup.setup_logging(
            log_level="INFO",
            log_file="./logs/controlflow.log",
            json_format=False
        )

        logger = LoggingSetup.create_structured_logger("controlflow.app")
        logger.info("日誌系統已啟動")

        print()

        # 3. 監控設置
        print("\n" + "=" * 70)
        print("3. 監控配置")
        print("=" * 70 + "\n")

        monitoring = MonitoringSetup()

        # 模擬一些請求
        monitoring.record_request(success=True, response_time=0.5)
        monitoring.record_request(success=True, response_time=0.7)
        monitoring.record_request(success=False, response_time=1.2)
        monitoring.record_task(success=True)
        monitoring.record_task(success=True)

        health_status = monitoring.health_check()
        print(f"健康狀態: {health_status['status']}")
        print(f"成功率: {health_status['success_rate']:.2%}")
        print(f"平均響應時間: {health_status['avg_response_time']:.3f}s")

        print()

        # 4. 性能優化
        print("\n" + "=" * 70)
        print("4. 性能優化")
        print("=" * 70 + "\n")

        perf = PerformanceOptimization()

        def expensive_operation():
            print("   執行昂貴操作...")
            return "計算結果"

        # 第一次調用(緩存未命中)
        result1 = perf.cached_execution("key1", expensive_operation, ttl=60)

        # 第二次調用(緩存命中)
        result2 = perf.cached_execution("key1", expensive_operation, ttl=60)

        stats = perf.get_cache_stats()
        print(f"\n緩存統計:")
        print(f"   緩存大小: {stats['cache_size']}")
        print(f"   命中率: {stats['hit_rate']:.2%}")

        print()

        # 5. 部署配置
        print("\n" + "=" * 70)
        print("5. 生成部署配置")
        print("=" * 70 + "\n")

        print("生成 Dockerfile...")
        dockerfile = DeploymentScripts.generate_dockerfile()
        print(f"   ✅ Dockerfile 已生成 ({len(dockerfile)} 字符)")

        print("\n生成 docker-compose.yml...")
        compose = DeploymentScripts.generate_docker_compose()
        print(f"   ✅ docker-compose.yml 已生成 ({len(compose)} 字符)")

        print("\n生成 Kubernetes 配置...")
        k8s = DeploymentScripts.generate_kubernetes_deployment()
        print(f"   ✅ K8s 配置已生成 ({len(k8s)} 字符)")

        print()

        print("\n" + "=" * 70)
        print("演示完成")
        print("=" * 70)
        print("\n✅ 所有生產部署示例已成功展示!")
        print("\n💡 生產部署要點:")
        print("   - 配置管理: 使用環境變量和配置文件")
        print("   - 日誌監控: 結構化日誌和性能監控")
        print("   - 性能優化: 緩存、批處理、連接池")
        print("   - 安全配置: API 密鑰保護、輸入驗證、速率限制")
        print("   - 容器化: Docker、Kubernetes 部署")
        print("\n💡 生產檢查清單:")
        print("   ✓ 環境變量配置完整")
        print("   ✓ 日誌級別設置正確")
        print("   ✓ 監控和告警配置")
        print("   ✓ 安全措施到位")
        print("   ✓ 備份和恢復策略")
        print("   ✓ 擴展性設計")
        print("\n🎉 恭喜!您已完成所有 ControlFlow 示例學習!")
        print()

    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
