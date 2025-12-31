#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenLLM Docker 部署示例
=====================

本示例展示 Docker 容器化部署，包括：
1. 使用官方 Docker 鏡像
2. 自定義 Dockerfile
3. Docker Compose 編排
4. 多階段構建
5. 生產環境配置

適用場景：
- 容器化部署
- 環境隔離
- 快速部署和擴展
"""

import sys


def official_docker_image():
    """
    使用官方 Docker 鏡像

    展示如何使用 OpenLLM 官方鏡像
    """
    print("=" * 80)
    print("示例 1: 使用官方 Docker 鏡像")
    print("=" * 80)

    print("\n📝 基本 Docker 命令：")
    print("-" * 80)

    basic_commands = '''
# 1. 拉取官方鏡像
docker pull ghcr.io/bentoml/openllm:latest

# 2. 運行容器（CPU）
docker run -it --rm \\
  -p 3000:3000 \\
  ghcr.io/bentoml/openllm \\
  start llama --model-id meta-llama/Llama-2-7b-chat-hf

# 3. 運行容器（GPU）
docker run -it --rm \\
  --gpus all \\
  -p 3000:3000 \\
  ghcr.io/bentoml/openllm \\
  start llama --model-id meta-llama/Llama-2-7b-chat-hf

# 4. 掛載模型緩存目錄
docker run -it --rm \\
  --gpus all \\
  -p 3000:3000 \\
  -v ~/.cache/huggingface:/root/.cache/huggingface \\
  ghcr.io/bentoml/openllm \\
  start llama --model-id meta-llama/Llama-2-7b-chat-hf

# 5. 使用環境變量
docker run -it --rm \\
  --gpus all \\
  -p 3000:3000 \\
  -e HF_TOKEN=your_token \\
  -e OPENLLM_BACKEND=vllm \\
  -v ~/.cache/huggingface:/root/.cache/huggingface \\
  ghcr.io/bentoml/openllm \\
  start llama --model-id meta-llama/Llama-2-7b-chat-hf
'''

    print(basic_commands)

    print("\n常用選項說明：")
    print("-" * 80)
    print("--gpus all          # 使用所有 GPU")
    print("--gpus device=0     # 使用特定 GPU")
    print("-p 3000:3000        # 端口映射")
    print("-v <host>:<container>  # 卷掛載")
    print("--ipc=host          # 共享內存（推薦）")
    print("--shm-size=8g       # 設置共享內存大小")


def custom_dockerfile():
    """
    自定義 Dockerfile

    展示如何創建自定義 Docker 鏡像
    """
    print("\n" + "=" * 80)
    print("示例 2: 自定義 Dockerfile")
    print("=" * 80)

    print("\n📝 基礎 Dockerfile：")
    print("-" * 80)

    basic_dockerfile = '''
# Dockerfile
FROM ghcr.io/bentoml/openllm:latest

# 設置工作目錄
WORKDIR /app

# 複製配置文件
COPY config.yaml /app/config.yaml
COPY requirements.txt /app/requirements.txt

# 安裝額外依賴
RUN pip install --no-cache-dir -r requirements.txt

# 預下載模型（可選）
RUN python -c "from transformers import AutoModel; \\
    AutoModel.from_pretrained('meta-llama/Llama-2-7b-chat-hf')"

# 設置環境變量
ENV OPENLLM_BACKEND=vllm
ENV TRANSFORMERS_CACHE=/models/cache

# 暴露端口
EXPOSE 3000

# 啟動命令
CMD ["openllm", "start", "llama", \\
     "--model-id", "meta-llama/Llama-2-7b-chat-hf", \\
     "--config", "/app/config.yaml"]
'''

    print(basic_dockerfile)

    print("\n多階段構建 Dockerfile：")
    print("-" * 80)

    multistage_dockerfile = '''
# Dockerfile.multistage
# 階段 1: 構建環境
FROM python:3.10-slim as builder

WORKDIR /build

# 安裝構建依賴
RUN apt-get update && apt-get install -y \\
    build-essential \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# 安裝 Python 依賴
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 階段 2: 運行環境
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# 安裝 Python
RUN apt-get update && apt-get install -y \\
    python3.10 \\
    python3-pip \\
    && rm -rf /var/lib/apt/lists/*

# 從構建階段複製依賴
COPY --from=builder /root/.local /root/.local

# 設置 PATH
ENV PATH=/root/.local/bin:$PATH

WORKDIR /app

# 複製應用代碼
COPY . /app

EXPOSE 3000

CMD ["openllm", "start", "llama", \\
     "--model-id", "meta-llama/Llama-2-7b-chat-hf"]
'''

    print(multistage_dockerfile)

    print("\n構建和運行：")
    print("-" * 80)

    build_commands = '''
# 構建鏡像
docker build -t my-openllm:latest -f Dockerfile .

# 多階段構建
docker build -t my-openllm:slim -f Dockerfile.multistage .

# 運行自定義鏡像
docker run -it --rm --gpus all -p 3000:3000 my-openllm:latest
'''

    print(build_commands)


def docker_compose():
    """
    Docker Compose 編排

    展示如何使用 Docker Compose 管理服務
    """
    print("\n" + "=" * 80)
    print("示例 3: Docker Compose 編排")
    print("=" * 80)

    print("\n📝 基本 docker-compose.yml：")
    print("-" * 80)

    basic_compose = '''
# docker-compose.yml
version: '3.8'

services:
  openllm:
    image: ghcr.io/bentoml/openllm:latest
    command: >
      start llama
      --model-id meta-llama/Llama-2-7b-chat-hf
      --backend vllm
      --port 3000
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
      - TRANSFORMERS_CACHE=/models/cache
      - HF_HOME=/models/cache
    volumes:
      - model-cache:/models/cache
      - ./config.yaml:/app/config.yaml
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

volumes:
  model-cache:
    driver: local
'''

    print(basic_compose)

    print("\n完整生產環境配置：")
    print("-" * 80)

    production_compose = '''
# docker-compose.prod.yml
version: '3.8'

services:
  # OpenLLM 服務
  openllm:
    image: ghcr.io/bentoml/openllm:latest
    command: >
      start llama
      --model-id meta-llama/Llama-2-7b-chat-hf
      --backend vllm
      --port 3000
      --workers 1
    ports:
      - "3000:3000"
    deploy:
      replicas: 2
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
        limits:
          memory: 16G
    environment:
      - TRANSFORMERS_CACHE=/models/cache
      - OPENLLM_BACKEND=vllm
    volumes:
      - model-cache:/models/cache
    networks:
      - openllm-network
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Nginx 反向代理
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - openllm
    networks:
      - openllm-network
    restart: unless-stopped

  # Prometheus 監控
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - openllm-network
    restart: unless-stopped

  # Grafana 可視化
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - prometheus
    networks:
      - openllm-network
    restart: unless-stopped

volumes:
  model-cache:
  prometheus-data:
  grafana-data:

networks:
  openllm-network:
    driver: bridge
'''

    print(production_compose)

    print("\nDocker Compose 命令：")
    print("-" * 80)

    compose_commands = '''
# 啟動所有服務
docker-compose up -d

# 查看日誌
docker-compose logs -f openllm

# 停止服務
docker-compose down

# 重啟服務
docker-compose restart openllm

# 擴展服務
docker-compose up -d --scale openllm=3

# 使用生產配置
docker-compose -f docker-compose.prod.yml up -d
'''

    print(compose_commands)


def production_optimization():
    """
    生產環境優化

    展示生產環境的優化配置
    """
    print("\n" + "=" * 80)
    print("示例 4: 生產環境優化")
    print("=" * 80)

    print("\n📝 優化的 Dockerfile：")
    print("-" * 80)

    optimized_dockerfile = '''
# Dockerfile.optimized
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# 設置非交互式安裝
ENV DEBIAN_FRONTEND=noninteractive

# 安裝系統依賴
RUN apt-get update && apt-get install -y \\
    python3.10 \\
    python3-pip \\
    git \\
    curl \\
    && rm -rf /var/lib/apt/lists/* \\
    && apt-get clean

# 升級 pip
RUN pip3 install --no-cache-dir --upgrade pip

# 安裝 OpenLLM 和依賴
RUN pip3 install --no-cache-dir \\
    openllm[vllm]>=0.4.0 \\
    bentoml>=1.2.0

# 創建非 root 用戶
RUN useradd -m -u 1000 openllm && \\
    mkdir -p /models/cache && \\
    chown -R openllm:openllm /models

USER openllm
WORKDIR /home/openllm

# 設置環境變量
ENV PATH=/home/openllm/.local/bin:$PATH
ENV TRANSFORMERS_CACHE=/models/cache
ENV HF_HOME=/models/cache

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \\
  CMD curl -f http://localhost:3000/health || exit 1

EXPOSE 3000

# 使用 exec 格式避免 shell
ENTRYPOINT ["openllm"]
CMD ["start", "llama", "--model-id", "meta-llama/Llama-2-7b-chat-hf"]
'''

    print(optimized_dockerfile)

    print("\n.dockerignore 文件：")
    print("-" * 80)

    dockerignore = '''
# .dockerignore
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info
dist
build
.git
.gitignore
.DS_Store
*.md
tests
docs
.pytest_cache
.coverage
htmlcov
'''

    print(dockerignore)

    print("\n性能調優參數：")
    print("-" * 80)

    tuning_params = '''
# 運行時性能優化
docker run -it --rm \\
  --gpus all \\
  --ipc=host \\                    # 共享內存，提高性能
  --shm-size=8g \\                 # 增加共享內存
  --ulimit memlock=-1 \\           # 解除內存鎖定限制
  --ulimit stack=67108864 \\       # 增加棧大小
  -p 3000:3000 \\
  -v ~/.cache/huggingface:/models/cache \\
  -e OMP_NUM_THREADS=4 \\          # OpenMP 線程數
  -e CUDA_VISIBLE_DEVICES=0 \\     # 指定 GPU
  my-openllm:latest
'''

    print(tuning_params)


def monitoring_and_logging():
    """
    監控和日誌

    展示 Docker 環境的監控和日誌配置
    """
    print("\n" + "=" * 80)
    print("示例 5: 監控和日誌")
    print("=" * 80)

    print("\n📝 日誌配置：")
    print("-" * 80)

    logging_config = '''
# docker-compose.yml 日誌配置
services:
  openllm:
    image: ghcr.io/bentoml/openllm:latest
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "production"
        tag: "{{.Name}}/{{.ID}}"
'''

    print(logging_config)

    print("\n查看日誌：")
    print("-" * 80)

    log_commands = '''
# 查看容器日誌
docker logs openllm-container

# 實時跟蹤日誌
docker logs -f openllm-container

# 查看最近 100 行
docker logs --tail 100 openllm-container

# 查看特定時間段
docker logs --since 2024-01-01T00:00:00 openllm-container
'''

    print(log_commands)

    print("\nPrometheus 配置：")
    print("-" * 80)

    prometheus_config = '''
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'openllm'
    static_configs:
      - targets: ['openllm:3000']
    metrics_path: '/metrics'
'''

    print(prometheus_config)


def main():
    """
    主函數：運行所有示例
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "OpenLLM Docker 部署示例" + " " * 20 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    try:
        # 示例 1: 官方鏡像
        official_docker_image()

        # 示例 2: 自定義 Dockerfile
        custom_dockerfile()

        # 示例 3: Docker Compose
        docker_compose()

        # 示例 4: 生產優化
        production_optimization()

        # 示例 5: 監控日誌
        monitoring_and_logging()

        print("\n" + "=" * 80)
        print("✓ 所有示例展示完成！")
        print("=" * 80)
        print("\n💡 關鍵要點：")
        print("   1. Docker 提供環境隔離和一致性")
        print("   2. Docker Compose 簡化多服務編排")
        print("   3. 生產環境需要適當的優化配置")
        print("   4. 完善的監控和日誌系統")
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
