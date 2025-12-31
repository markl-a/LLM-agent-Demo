#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SWE-Agent 生產部署範例
======================

這個範例展示如何將 SWE-Agent 部署到生產環境：
1. 配置管理
2. 監控和日誌
3. 錯誤處理和恢復
4. 擴展性設計
5. 安全性考慮
6. CI/CD 集成

生產部署需要考慮可靠性、安全性、可觀測性等多個方面。

作者: SWE-Agent 團隊
日期: 2025-12-31
"""

import os
import sys
import json
import yaml
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import signal
import atexit

# Web 框架
try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("請安裝: pip install fastapi uvicorn pydantic")

# 監控和日誌
from loguru import logger
try:
    import prometheus_client
    from prometheus_client import Counter, Histogram, Gauge
except ImportError:
    print("請安裝: pip install prometheus-client")

# 消息隊列
try:
    from celery import Celery
    import redis
except ImportError:
    print("請安裝: pip install celery redis")

# SWE-Agent
from sweagent import SWEAgent

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class Environment(Enum):
    """部署環境"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DeploymentConfig:
    """
    部署配置
    """
    # 環境
    environment: Environment = Environment.PRODUCTION

    # Agent 配置
    agent_model: str = "gpt-4"
    agent_temperature: float = 0.2
    agent_max_iterations: int = 30

    # API 配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4

    # 數據庫配置
    database_url: str = "postgresql://localhost/sweagent"
    redis_url: str = "redis://localhost:6379/0"

    # 安全配置
    api_key_required: bool = True
    allowed_origins: List[str] = field(default_factory=list)
    rate_limit: int = 100  # 每小時請求數

    # 監控配置
    enable_metrics: bool = True
    enable_tracing: bool = True
    log_level: str = "INFO"

    # 資源限制
    max_concurrent_tasks: int = 10
    task_timeout: int = 3600  # 1 小時

    # 存儲配置
    storage_path: Path = Path("/var/lib/sweagent")
    logs_path: Path = Path("/var/log/sweagent")

    @classmethod
    def from_file(cls, config_file: Path) -> 'DeploymentConfig':
        """
        從配置文件加載

        Args:
            config_file: 配置文件路徑

        Returns:
            配置對象
        """
        with open(config_file, 'r') as f:
            if config_file.suffix == '.json':
                data = json.load(f)
            elif config_file.suffix in ['.yml', '.yaml']:
                data = yaml.safe_load(f)
            else:
                raise ValueError(f"不支持的配置文件格式: {config_file.suffix}")

        return cls(**data)

    def save(self, config_file: Path):
        """保存配置到文件"""
        data = asdict(self)

        with open(config_file, 'w') as f:
            if config_file.suffix == '.json':
                json.dump(data, f, indent=2)
            elif config_file.suffix in ['.yml', '.yaml']:
                yaml.dump(data, f, default_flow_style=False)


class MetricsCollector:
    """
    指標收集器

    使用 Prometheus 收集和導出指標
    """

    def __init__(self):
        """初始化指標收集器"""
        # 計數器
        self.requests_total = Counter(
            'sweagent_requests_total',
            'Total number of requests',
            ['endpoint', 'status']
        )

        self.tasks_total = Counter(
            'sweagent_tasks_total',
            'Total number of tasks',
            ['status']
        )

        # 直方圖
        self.task_duration = Histogram(
            'sweagent_task_duration_seconds',
            'Task duration in seconds'
        )

        self.api_latency = Histogram(
            'sweagent_api_latency_seconds',
            'API request latency in seconds',
            ['endpoint']
        )

        # 儀表
        self.active_tasks = Gauge(
            'sweagent_active_tasks',
            'Number of currently active tasks'
        )

        self.agent_cost = Counter(
            'sweagent_cost_total',
            'Total cost in USD'
        )

        logger.info("指標收集器初始化完成")

    def record_request(self, endpoint: str, status: str):
        """記錄請求"""
        self.requests_total.labels(endpoint=endpoint, status=status).inc()

    def record_task(self, status: str, duration: float, cost: float):
        """記錄任務"""
        self.tasks_total.labels(status=status).inc()
        self.task_duration.observe(duration)
        self.agent_cost.inc(cost)


class ProductionLogger:
    """
    生產環境日誌器

    配置結構化日誌輸出
    """

    def __init__(self, config: DeploymentConfig):
        """
        初始化日誌器

        Args:
            config: 部署配置
        """
        self.config = config

        # 移除默認處理器
        logger.remove()

        # 添加控制台處理器
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=config.log_level,
            colorize=True
        )

        # 添加文件處理器
        log_file = config.logs_path / "sweagent_{time}.log"
        logger.add(
            log_file,
            rotation="1 day",
            retention="30 days",
            compression="gz",
            level=config.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
        )

        # 添加錯誤日誌
        error_log = config.logs_path / "error_{time}.log"
        logger.add(
            error_log,
            rotation="1 day",
            retention="90 days",
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
        )

        logger.info(f"日誌系統初始化完成，級別: {config.log_level}")


# API 請求模型
class TaskRequest(BaseModel):
    """任務請求"""
    repo: str
    issue_number: int
    api_key: Optional[str] = None


class TaskResponse(BaseModel):
    """任務響應"""
    task_id: str
    status: str
    message: str


class ProductionAPI:
    """
    生產環境 API 服務

    提供 REST API 接口
    """

    def __init__(self, config: DeploymentConfig):
        """
        初始化 API 服務

        Args:
            config: 部署配置
        """
        self.config = config
        self.app = FastAPI(
            title="SWE-Agent API",
            description="AI-powered software engineering agent",
            version="1.0.0"
        )

        self.metrics = MetricsCollector()
        self.agent = SWEAgent(model=config.agent_model)

        # 任務隊列
        self.tasks = {}

        self._setup_routes()
        self._setup_middleware()

        logger.info("API 服務初始化完成")

    def _setup_routes(self):
        """設置路由"""

        @self.app.get("/")
        async def root():
            """健康檢查端點"""
            return {"status": "healthy", "version": "1.0.0"}

        @self.app.get("/health")
        async def health():
            """詳細健康檢查"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "environment": self.config.environment.value,
                "active_tasks": len(self.tasks)
            }

        @self.app.post("/tasks", response_model=TaskResponse)
        async def create_task(
            request: TaskRequest,
            background_tasks: BackgroundTasks
        ):
            """創建新任務"""

            # 驗證 API 密鑰
            if self.config.api_key_required:
                if not request.api_key or not self._verify_api_key(request.api_key):
                    raise HTTPException(status_code=401, detail="Invalid API key")

            # 創建任務 ID
            task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # 添加到後台任務
            background_tasks.add_task(
                self._execute_task,
                task_id,
                request.repo,
                request.issue_number
            )

            self.tasks[task_id] = {
                "status": "pending",
                "created_at": datetime.now().isoformat()
            }

            logger.info(f"任務已創建: {task_id}")

            return TaskResponse(
                task_id=task_id,
                status="pending",
                message="Task created successfully"
            )

        @self.app.get("/tasks/{task_id}")
        async def get_task_status(task_id: str):
            """獲取任務狀態"""

            if task_id not in self.tasks:
                raise HTTPException(status_code=404, detail="Task not found")

            return self.tasks[task_id]

        @self.app.get("/metrics")
        async def metrics():
            """Prometheus 指標端點"""
            from prometheus_client import generate_latest
            return generate_latest()

    def _setup_middleware(self):
        """設置中間件"""

        @self.app.middleware("http")
        async def add_process_time_header(request, call_next):
            """添加處理時間頭"""
            import time

            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time

            response.headers["X-Process-Time"] = str(process_time)

            # 記錄指標
            self.metrics.api_latency.labels(
                endpoint=request.url.path
            ).observe(process_time)

            return response

    def _verify_api_key(self, api_key: str) -> bool:
        """驗證 API 密鑰"""
        # 實際應該從數據庫或環境變量檢查
        valid_key = os.getenv("SWEAGENT_API_KEY")
        return api_key == valid_key

    async def _execute_task(self, task_id: str, repo: str, issue_number: int):
        """
        執行任務

        Args:
            task_id: 任務 ID
            repo: 儲存庫
            issue_number: Issue 編號
        """
        start_time = datetime.now()

        try:
            # 更新狀態
            self.tasks[task_id]["status"] = "running"
            self.metrics.active_tasks.inc()

            # 執行 Agent
            result = self.agent.solve_issue(
                repo=repo,
                issue_number=issue_number
            )

            # 計算時長
            duration = (datetime.now() - start_time).total_seconds()

            # 更新結果
            self.tasks[task_id].update({
                "status": "completed" if result.success else "failed",
                "completed_at": datetime.now().isoformat(),
                "duration": duration,
                "result": {
                    "success": result.success,
                    "patch": result.patch,
                    "tests_passed": result.tests_passed,
                    "cost": result.cost
                }
            })

            # 記錄指標
            self.metrics.record_task(
                status="success" if result.success else "failed",
                duration=duration,
                cost=result.cost
            )

            logger.info(f"任務完成: {task_id}, 成功: {result.success}")

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()

            self.tasks[task_id].update({
                "status": "error",
                "completed_at": datetime.now().isoformat(),
                "duration": duration,
                "error": str(e)
            })

            self.metrics.record_task(
                status="error",
                duration=duration,
                cost=0
            )

            logger.error(f"任務失敗: {task_id}, 錯誤: {e}")

        finally:
            self.metrics.active_tasks.dec()

    def run(self):
        """運行 API 服務"""
        uvicorn.run(
            self.app,
            host=self.config.api_host,
            port=self.config.api_port,
            workers=self.config.api_workers,
            log_level=self.config.log_level.lower()
        )


class CeleryWorker:
    """
    Celery 工作器

    使用 Celery 處理異步任務
    """

    def __init__(self, config: DeploymentConfig):
        """
        初始化工作器

        Args:
            config: 部署配置
        """
        self.config = config

        # 創建 Celery 應用
        self.celery = Celery(
            'sweagent',
            broker=config.redis_url,
            backend=config.redis_url
        )

        # 配置 Celery
        self.celery.conf.update(
            task_serializer='json',
            accept_content=['json'],
            result_serializer='json',
            timezone='UTC',
            enable_utc=True,
            task_time_limit=config.task_timeout,
            worker_max_tasks_per_child=100
        )

        self._register_tasks()

        logger.info("Celery 工作器初始化完成")

    def _register_tasks(self):
        """註冊任務"""

        @self.celery.task(name='sweagent.solve_issue')
        def solve_issue_task(repo: str, issue_number: int) -> Dict:
            """解決 Issue 任務"""
            agent = SWEAgent(model=self.config.agent_model)

            result = agent.solve_issue(
                repo=repo,
                issue_number=issue_number
            )

            return {
                "success": result.success,
                "patch": result.patch,
                "cost": result.cost
            }

    def start(self):
        """啟動工作器"""
        self.celery.worker_main([
            'worker',
            '--loglevel=info',
            f'--concurrency={self.config.max_concurrent_tasks}'
        ])


class DeploymentManager:
    """
    部署管理器

    管理整個部署生命周期
    """

    def __init__(self, config: DeploymentConfig):
        """
        初始化部署管理器

        Args:
            config: 部署配置
        """
        self.config = config
        self.console = Console()

        # 初始化組件
        self.logger = ProductionLogger(config)
        self.api = ProductionAPI(config)

        # 註冊清理函數
        atexit.register(self.cleanup)
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        logger.info(f"部署管理器初始化完成，環境: {config.environment.value}")

    def _signal_handler(self, signum, frame):
        """信號處理器"""
        logger.info(f"收到信號: {signum}")
        self.cleanup()
        sys.exit(0)

    def pre_flight_check(self) -> bool:
        """
        啟動前檢查

        Returns:
            是否通過檢查
        """
        self.console.print("\n[bold]啟動前檢查...[/bold]")

        checks = {
            "配置文件": self._check_config(),
            "存儲目錄": self._check_storage(),
            "API 密鑰": self._check_api_keys(),
            "網路連接": self._check_network(),
            "依賴服務": self._check_dependencies()
        }

        table = Table(title="檢查結果")
        table.add_column("項目", style="cyan")
        table.add_column("狀態", style="magenta")

        all_passed = True

        for check_name, passed in checks.items():
            status = "✓ 通過" if passed else "✗ 失敗"
            style = "green" if passed else "red"

            table.add_row(check_name, f"[{style}]{status}[/{style}]")

            if not passed:
                all_passed = False

        self.console.print(table)

        return all_passed

    def _check_config(self) -> bool:
        """檢查配置"""
        try:
            assert self.config.agent_model
            assert self.config.api_port > 0
            return True
        except:
            return False

    def _check_storage(self) -> bool:
        """檢查存儲"""
        try:
            self.config.storage_path.mkdir(parents=True, exist_ok=True)
            self.config.logs_path.mkdir(parents=True, exist_ok=True)
            return True
        except:
            return False

    def _check_api_keys(self) -> bool:
        """檢查 API 密鑰"""
        return bool(
            os.getenv("OPENAI_API_KEY") or
            os.getenv("ANTHROPIC_API_KEY")
        )

    def _check_network(self) -> bool:
        """檢查網路"""
        try:
            import requests
            requests.get("https://api.openai.com", timeout=5)
            return True
        except:
            return False

    def _check_dependencies(self) -> bool:
        """檢查依賴服務"""
        # 檢查 Redis
        try:
            import redis
            r = redis.from_url(self.config.redis_url)
            r.ping()
            return True
        except:
            return False

    def start(self):
        """啟動服務"""
        self.console.print(Panel(
            "[bold]SWE-Agent 生產部署[/bold]\n\n"
            f"環境: {self.config.environment.value}\n"
            f"端口: {self.config.api_port}",
            border_style="green"
        ))

        # 啟動前檢查
        if not self.pre_flight_check():
            self.console.print("[red]啟動前檢查失敗[/red]")
            return

        # 啟動 API 服務
        logger.info("啟動 API 服務...")
        self.api.run()

    def cleanup(self):
        """清理資源"""
        logger.info("清理資源...")

        # 保存配置
        config_file = self.config.storage_path / "config.yaml"
        self.config.save(config_file)

        logger.info("清理完成")


def create_systemd_service(config: DeploymentConfig) -> str:
    """
    創建 systemd 服務文件

    Args:
        config: 部署配置

    Returns:
        服務文件內容
    """
    service_content = f"""[Unit]
Description=SWE-Agent API Service
After=network.target

[Service]
Type=simple
User=sweagent
WorkingDirectory=/opt/sweagent
Environment="PATH=/opt/sweagent/venv/bin"
Environment="SWEAGENT_ENV={config.environment.value}"
ExecStart=/opt/sweagent/venv/bin/python -m sweagent.deploy
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

    return service_content


def create_docker_compose() -> str:
    """
    創建 Docker Compose 配置

    Returns:
        docker-compose.yml 內容
    """
    compose_content = """version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SWEAGENT_ENV=production
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    restart: always

  worker:
    build: .
    command: celery -A sweagent worker -l info
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    restart: always

  redis:
    image: redis:7-alpine
    restart: always

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    restart: always
"""

    return compose_content


def main():
    """主函數"""
    console = Console()

    console.print(Panel(
        "[bold]SWE-Agent 生產部署範例[/bold]\n\n"
        "展示如何將 Agent 部署到生產環境",
        border_style="green"
    ))

    # 1. 加載配置
    console.print("\n[bold cyan]1. 加載配置[/bold cyan]")

    config = DeploymentConfig(
        environment=Environment.PRODUCTION,
        api_port=8000,
        log_level="INFO"
    )

    # 保存配置示例
    config_file = Path("config.yaml")
    config.save(config_file)
    console.print(f"配置已保存: {config_file}")

    # 2. 創建部署文件
    console.print("\n[bold cyan]2. 創建部署文件[/bold cyan]")

    # systemd 服務
    systemd_service = create_systemd_service(config)
    with open("sweagent.service", 'w') as f:
        f.write(systemd_service)
    console.print("已創建: sweagent.service")

    # docker-compose
    docker_compose = create_docker_compose()
    with open("docker-compose.yml", 'w') as f:
        f.write(docker_compose)
    console.print("已創建: docker-compose.yml")

    # 3. 啟動服務（示例）
    console.print("\n[bold cyan]3. 部署管理器[/bold cyan]")

    manager = DeploymentManager(config)

    # 只執行檢查，不實際啟動
    manager.pre_flight_check()

    console.print("\n[bold green]部署配置完成！[/bold green]")
    console.print("\n下一步:")
    console.print("  1. 配置環境變量")
    console.print("  2. 安裝 systemd 服務: sudo cp sweagent.service /etc/systemd/system/")
    console.print("  3. 啟動服務: sudo systemctl start sweagent")
    console.print("  4. 或使用 Docker: docker-compose up -d")


if __name__ == "__main__":
    main()
