#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prefect 部署配置
=================

這個示例展示了 Prefect 的部署功能，包括：
1. 創建部署（Deployment）
2. Work Pool 配置
3. 調度設置
4. 參數配置
5. 基礎設施配置
6. 部署管理
"""

from prefect import task, flow, get_run_logger
from prefect.server.schemas.schedules import CronSchedule, IntervalSchedule
from datetime import timedelta, datetime
import time
from typing import Dict, List, Optional


# ============================================================================
# 可部署的工作流
# ============================================================================

@task
def fetch_data_task(source: str, limit: int = 100) -> List[dict]:
    """
    獲取數據任務

    Args:
        source: 數據源
        limit: 記錄限制

    Returns:
        數據列表
    """
    logger = get_run_logger()
    logger.info(f"從 {source} 獲取數據（限制：{limit}）")

    time.sleep(1)

    data = [
        {"id": i, "value": i * 10}
        for i in range(1, min(limit + 1, 101))
    ]

    logger.info(f"獲取了 {len(data)} 條記錄")
    return data


@task
def process_data_task(data: List[dict]) -> Dict:
    """
    處理數據任務

    Args:
        data: 數據列表

    Returns:
        處理結果
    """
    logger = get_run_logger()
    logger.info(f"處理 {len(data)} 條記錄")

    time.sleep(1)

    result = {
        "processed_count": len(data),
        "total_value": sum(item["value"] for item in data),
        "timestamp": datetime.now().isoformat()
    }

    logger.info(f"處理完成：{result}")
    return result


@task
def save_result_task(result: Dict, target: str) -> str:
    """
    保存結果任務

    Args:
        result: 結果數據
        target: 目標位置

    Returns:
        狀態消息
    """
    logger = get_run_logger()
    logger.info(f"保存結果到 {target}")

    time.sleep(0.5)

    message = f"✓ 已保存到 {target}"
    logger.info(message)
    return message


@flow(name="生產環境工作流")
def production_workflow(
    source: str = "database",
    target: str = "warehouse",
    limit: int = 100,
    environment: str = "production"
):
    """
    生產環境數據處理工作流

    Args:
        source: 數據源
        target: 目標位置
        limit: 記錄限制
        environment: 環境名稱
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info(f"生產環境工作流 - {environment}")
    logger.info("=" * 60)

    # 獲取數據
    data = fetch_data_task(source, limit)

    # 處理數據
    result = process_data_task(data)

    # 保存結果
    status = save_result_task(result, target)

    logger.info(f"工作流完成：{status}")
    return result


# ============================================================================
# 部署配置示例
# ============================================================================

def show_basic_deployment_example():
    """
    顯示基本部署配置示例
    """
    print("\n" + "=" * 70)
    print("基本部署配置")
    print("=" * 70)

    example = '''
# 方法 1: 使用 Python API 創建部署
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule

# 創建部署
deployment = Deployment.build_from_flow(
    flow=production_workflow,
    name="production-daily-job",
    work_pool_name="default-agent-pool",
    schedule=CronSchedule(
        cron="0 2 * * *",  # 每天凌晨 2 點
        timezone="Asia/Taipei"
    ),
    parameters={
        "source": "production-db",
        "target": "data-warehouse",
        "limit": 1000,
        "environment": "production"
    },
    tags=["production", "daily", "etl"]
)

# 應用部署
deployment.apply()

# 方法 2: 使用 Flow.deploy() 方法（更簡單）
production_workflow.deploy(
    name="production-daily-job",
    work_pool_name="default-agent-pool",
    schedule=CronSchedule(cron="0 2 * * *", timezone="Asia/Taipei"),
    parameters={
        "source": "production-db",
        "target": "data-warehouse",
        "limit": 1000
    },
    tags=["production", "daily"]
)
    '''

    print(example)


def show_multiple_deployment_example():
    """
    顯示多環境部署示例
    """
    print("\n" + "=" * 70)
    print("多環境部署配置")
    print("=" * 70)

    example = '''
# 同一個工作流，不同環境的部署

# 開發環境部署
production_workflow.deploy(
    name="dev-hourly-job",
    work_pool_name="dev-pool",
    schedule=IntervalSchedule(interval=timedelta(hours=1)),
    parameters={
        "source": "dev-db",
        "target": "dev-warehouse",
        "limit": 10,
        "environment": "development"
    },
    tags=["development", "hourly"]
)

# 測試環境部署
production_workflow.deploy(
    name="staging-daily-job",
    work_pool_name="staging-pool",
    schedule=CronSchedule(cron="0 8 * * *"),
    parameters={
        "source": "staging-db",
        "target": "staging-warehouse",
        "limit": 100,
        "environment": "staging"
    },
    tags=["staging", "daily"]
)

# 生產環境部署
production_workflow.deploy(
    name="production-daily-job",
    work_pool_name="production-pool",
    schedule=CronSchedule(cron="0 2 * * *"),
    parameters={
        "source": "production-db",
        "target": "production-warehouse",
        "limit": 10000,
        "environment": "production"
    },
    tags=["production", "daily", "critical"]
)

# 手動觸發部署（無調度）
production_workflow.deploy(
    name="manual-job",
    work_pool_name="production-pool",
    parameters={
        "source": "production-db",
        "target": "adhoc-results",
        "limit": 1000,
        "environment": "production"
    },
    tags=["manual", "adhoc"]
    # 注意：沒有 schedule 參數，需要手動觸發
)
    '''

    print(example)


def show_work_pool_configuration():
    """
    顯示 Work Pool 配置
    """
    print("\n" + "=" * 70)
    print("Work Pool 配置")
    print("=" * 70)

    example = '''
# Work Pool 是執行部署的基礎設施

# 1. 創建 Process Work Pool（本地進程）
prefect work-pool create "local-pool" --type process

# 2. 創建 Docker Work Pool（Docker 容器）
prefect work-pool create "docker-pool" --type docker

# 3. 創建 Kubernetes Work Pool（K8s 集群）
prefect work-pool create "k8s-pool" --type kubernetes

# 4. 查看所有 Work Pool
prefect work-pool ls

# 5. 查看 Work Pool 詳情
prefect work-pool inspect "local-pool"

# 6. 啟動 Worker（執行任務）
prefect worker start --pool "local-pool"

# 7. 在後台啟動 Worker
nohup prefect worker start --pool "local-pool" > worker.log 2>&1 &

# Work Pool 配置示例（Python）
from prefect.deployments import Deployment

deployment = Deployment.build_from_flow(
    flow=production_workflow,
    name="my-deployment",
    work_pool_name="docker-pool",
    infrastructure_overrides={
        "image": "my-app:latest",
        "env": {
            "DATABASE_URL": "postgresql://...",
            "API_KEY": "secret"
        },
        "resources": {
            "limits": {
                "memory": "2Gi",
                "cpu": "1000m"
            }
        }
    }
)
    '''

    print(example)


def show_deployment_yaml_example():
    """
    顯示 YAML 部署配置示例
    """
    print("\n" + "=" * 70)
    print("YAML 部署配置")
    print("=" * 70)

    example = '''
# deployment.yaml

# 基本信息
name: production-daily-job
description: 生產環境每日數據處理任務
version: 1.0.0

# 工作流配置
flow_name: production_workflow
entrypoint: 09_部署配置.py:production_workflow

# Work Pool
work_pool:
  name: production-pool
  work_queue_name: default

# 調度配置
schedule:
  cron: "0 2 * * *"
  timezone: "Asia/Taipei"

# 參數
parameters:
  source: production-db
  target: data-warehouse
  limit: 10000
  environment: production

# 標籤
tags:
  - production
  - daily
  - etl

# 基礎設施配置（Docker 示例）
infrastructure:
  type: docker-container
  image: my-prefect-app:latest
  env:
    DATABASE_URL: ${DATABASE_URL}
    API_KEY: ${API_KEY}
  labels:
    team: data-engineering
    project: etl-pipeline

# 應用 YAML 配置
# prefect deployment apply deployment.yaml
    '''

    print(example)


def show_deployment_cli_commands():
    """
    顯示部署管理命令
    """
    print("\n" + "=" * 70)
    print("部署管理命令")
    print("=" * 70)

    commands = '''
# 1. 查看所有部署
prefect deployment ls

# 2. 查看特定流程的部署
prefect deployment ls --flow-name "production_workflow"

# 3. 查看部署詳情
prefect deployment inspect "production_workflow/production-daily-job"

# 4. 手動運行部署
prefect deployment run "production_workflow/production-daily-job"

# 5. 帶自定義參數運行
prefect deployment run "production_workflow/production-daily-job" \\
    --param source=custom-db \\
    --param limit=500

# 6. 暫停部署（停止調度）
prefect deployment pause "production_workflow/production-daily-job"

# 7. 恢復部署
prefect deployment resume "production_workflow/production-daily-job"

# 8. 刪除部署
prefect deployment delete "production_workflow/production-daily-job"

# 9. 更新部署調度
prefect deployment set-schedule \\
    "production_workflow/production-daily-job" \\
    --cron "0 3 * * *"

# 10. 查看部署的運行歷史
prefect flow-run ls --deployment-name "production-daily-job"

# 11. 導出部署配置
prefect deployment export "production_workflow/production-daily-job" \\
    > deployment-backup.yaml

# 12. 從文件應用部署
prefect deployment apply deployment.yaml

# 13. 構建部署（生成配置但不應用）
prefect deployment build \\
    09_部署配置.py:production_workflow \\
    -n "my-deployment" \\
    -o deployment.yaml
    '''

    print(commands)


# ============================================================================
# 部署最佳實踐
# ============================================================================

def show_deployment_best_practices():
    """
    顯示部署最佳實踐
    """
    print("\n" + "=" * 70)
    print("部署最佳實踐")
    print("=" * 70)

    practices = '''
1. 環境分離：
   - 為不同環境創建不同的部署
   - 使用不同的 Work Pool
   - 參數化配置（數據庫、API 端點等）

2. 命名規範：
   - {environment}-{frequency}-{purpose}
   - 例如：production-daily-etl, dev-hourly-sync

3. 標籤使用：
   - 環境標籤：production, staging, development
   - 頻率標籤：daily, hourly, weekly
   - 類型標籤：etl, ml, reporting
   - 優先級標籤：critical, high, normal, low

4. 參數管理：
   - 使用環境變量
   - 使用 Prefect Blocks 存儲敏感信息
   - 為每個環境設置不同的默認參數

5. 調度策略：
   - 避免所有任務同時運行
   - 考慮系統負載高峰期
   - 設置合理的超時時間
   - 為不同優先級任務分配不同時段

6. 監控和告警：
   - 為關鍵任務設置失敗告警
   - 監控執行時間和資源使用
   - 定期檢查部署狀態

7. 版本控制：
   - 將部署配置納入 Git
   - 使用語義化版本號
   - 記錄變更歷史

8. 基礎設施：
   - 使用容器化（Docker）
   - 配置資源限制
   - 實現高可用性

9. 測試流程：
   - 先在開發環境測試
   - 使用 staging 環境驗證
   - 藍綠部署或金絲雀發布

10. 文檔：
    - 記錄部署配置
    - 說明參數含義
    - 提供故障排除指南
    '''

    print(practices)


# ============================================================================
# Docker 部署示例
# ============================================================================

def show_docker_deployment_example():
    """
    顯示 Docker 部署示例
    """
    print("\n" + "=" * 70)
    print("Docker 部署示例")
    print("=" * 70)

    example = '''
# 1. Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製代碼
COPY . .

# 設置環境變量
ENV PREFECT_API_URL=http://prefect-server:4200/api

# 啟動命令會由 Prefect 覆蓋
CMD ["python", "flow.py"]

# 2. 構建鏡像
docker build -t my-prefect-app:latest .

# 3. 推送到倉庫
docker push my-prefect-app:latest

# 4. 創建部署（使用 Docker）
from prefect.deployments import Deployment
from prefect.infrastructure.docker import DockerContainer

docker_container = DockerContainer(
    image="my-prefect-app:latest",
    env={
        "DATABASE_URL": "postgresql://...",
        "API_KEY": "secret"
    },
    networks=["prefect"],
    volumes=["/data:/app/data"]
)

deployment = Deployment.build_from_flow(
    flow=production_workflow,
    name="docker-deployment",
    infrastructure=docker_container,
    work_pool_name="docker-pool"
)

deployment.apply()

# 5. docker-compose.yml（完整環境）
version: '3.8'

services:
  prefect-server:
    image: prefecthq/prefect:2-python3.11
    command: prefect server start
    ports:
      - "4200:4200"
    environment:
      - PREFECT_UI_URL=http://localhost:4200
    volumes:
      - prefect-data:/root/.prefect

  prefect-worker:
    image: my-prefect-app:latest
    command: prefect worker start --pool docker-pool
    depends_on:
      - prefect-server
    environment:
      - PREFECT_API_URL=http://prefect-server:4200/api
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock

volumes:
  prefect-data:
    '''

    print(example)


# ============================================================================
# 運行示例
# ============================================================================

def main():
    """
    主函數 - 顯示所有示例和文檔
    """
    print("\n" + "=" * 70)
    print("Prefect 部署配置")
    print("=" * 70)

    # 運行工作流示例
    print("\n【示例】運行生產環境工作流")
    print("-" * 70)
    result = production_workflow(
        source="example-db",
        target="example-warehouse",
        limit=10,
        environment="demo"
    )
    print(f"結果：{result}")

    # 顯示配置示例
    show_basic_deployment_example()
    show_multiple_deployment_example()
    show_work_pool_configuration()
    show_deployment_yaml_example()
    show_deployment_cli_commands()
    show_docker_deployment_example()
    show_deployment_best_practices()

    # 使用說明
    print("\n" + "=" * 70)
    print("部署配置總結")
    print("=" * 70)
    print("""
1. 部署流程：
   a. 開發工作流
   b. 測試工作流
   c. 創建部署配置
   d. 應用部署
   e. 啟動 Worker
   f. 監控執行

2. 創建部署的方法：
   - Python API: flow.deploy()
   - Deployment.build_from_flow()
   - YAML 配置文件
   - CLI 命令: prefect deployment build

3. Work Pool 類型：
   - Process: 本地進程
   - Docker: Docker 容器
   - Kubernetes: K8s 集群
   - Cloud Run: Google Cloud Run
   - ECS: AWS ECS

4. 調度選項：
   - CronSchedule: Cron 表達式
   - IntervalSchedule: 時間間隔
   - RRuleSchedule: 複雜規則
   - 無調度: 手動觸發

5. 關鍵配置：
   - name: 部署名稱
   - work_pool_name: Work Pool
   - schedule: 調度配置
   - parameters: 默認參數
   - tags: 標籤

6. 環境管理：
   - 使用不同的 Work Pool
   - 參數化配置
   - 環境變量
   - Prefect Blocks

7. 部署管理：
   prefect deployment ls          # 列出部署
   prefect deployment run         # 運行部署
   prefect deployment pause       # 暫停部署
   prefect deployment resume      # 恢復部署
   prefect deployment delete      # 刪除部署

8. Worker 管理：
   prefect worker start --pool "pool-name"
   prefect work-pool create "pool-name" --type process
   prefect work-pool ls

9. 監控：
   - Prefect UI: http://localhost:4200
   - 查看部署狀態
   - 監控運行歷史
   - 檢查 Worker 狀態

10. 下一步：
    - 查看 10_監控面板.py 了解監控功能
    - 啟動 Prefect 服務器並實際部署
    - 配置生產環境
    """)

    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
