# LLM Agent Demo - Dockerfile
# 基於 Python 3.11 的官方映像
FROM python:3.14-slim AS base

# 設置工作目錄
WORKDIR /app

# 設置環境變數
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# ==================== 依賴層 ====================
FROM base AS dependencies

# 安裝系統依賴
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 升級 pip
RUN pip install --upgrade pip setuptools wheel

# 複製 requirements.txt（利用 Docker 分層緩存）
COPY requirements.txt requirements-prod.txt ./

# 安裝 Python 核心依賴
RUN pip install --no-cache-dir -r requirements-prod.txt

# ==================== 運行時層 ====================
FROM base AS runtime

# 從依賴層複製已安裝的包
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# 安裝運行時必需的系統工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 創建應用用戶（安全最佳實踐）
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data /app/outputs /app/logs && \
    chown -R appuser:appuser /app

# 複製項目文件
COPY --chown=appuser:appuser . .

# 複製 Docker 腳本
COPY --chown=appuser:appuser docker/entrypoint.sh /entrypoint.sh
COPY --chown=appuser:appuser docker/healthcheck.py /healthcheck.py
RUN chmod +x /entrypoint.sh /healthcheck.py

# 切換到應用用戶
USER appuser

# 設置環境變數
ENV JUPYTER_ENABLE_LAB=yes \
    JUPYTER_TOKEN="" \
    JUPYTER_PASSWORD="" \
    PATH="/home/appuser/.local/bin:${PATH}"

# 暴露端口
EXPOSE 8888 8000 8080

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python /healthcheck.py

# 入口點
ENTRYPOINT ["/entrypoint.sh"]

# 默認命令：啟動 Jupyter Lab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]

# ==================== 開發層 ====================
FROM runtime AS development

USER root

# 安裝開發依賴
COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# 安裝額外的開發工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    vim \
    nano \
    htop \
    procps \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Playwright 瀏覽器（用於 Web 爬蟲）
RUN playwright install chromium --with-deps || true

USER appuser

# 開發環境默認命令
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--autoreload"]
