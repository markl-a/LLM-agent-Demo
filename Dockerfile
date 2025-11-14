# LLM Agent Demo - Dockerfile
# 基於 Python 3.11 的官方映像
FROM python:3.11-slim

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案文件
COPY . .

# 設置環境變數
ENV PYTHONUNBUFFERED=1
ENV JUPYTER_ENABLE_LAB=yes

# 暴露 Jupyter Lab 端口
EXPOSE 8888

# 創建數據目錄
RUN mkdir -p /app/data /app/outputs

# 啟動 Jupyter Lab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
