# Docker 部署指南

本文檔介紹如何使用 Docker 和 Docker Compose 部署 LLM Agent Demo 專案。

## 目錄

- [快速開始](#快速開始)
- [配置說明](#配置說明)
- [服務架構](#服務架構)
- [使用方式](#使用方式)
- [常見問題](#常見問題)

---

## 快速開始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 8GB RAM（推薦 16GB）
- （可選）NVIDIA GPU + nvidia-docker（用於 Ollama GPU 加速）

### 1. 準備環境變數

```bash
# 複製環境變數範例文件
cp .env.example .env

# 編輯 .env 文件，填入你的 API Keys
nano .env
```

至少需要配置一個 LLM 提供商的 API Key：
- `OPENAI_API_KEY`
- `GOOGLE_API_KEY`
- `ANTHROPIC_API_KEY`
- `GROQ_API_KEY`

### 2. 啟動服務

**生產環境：**
```bash
docker-compose up -d
```

**開發環境：**
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### 3. 訪問服務

- **Jupyter Lab**: http://localhost:8888
- **ChromaDB**: http://localhost:8000
- **Ollama API**: http://localhost:11434

開發環境額外服務：
- **Adminer（數據庫管理）**: http://localhost:8081
- **Portainer（容器管理）**: http://localhost:9000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

---

## 配置說明

### 文件結構

```
.
├── Dockerfile                      # 多階段構建的 Docker 鏡像
├── .dockerignore                   # Docker 構建忽略文件
├── docker-compose.yml              # 生產環境配置
├── docker-compose.dev.yml          # 開發環境配置
└── docker/
    ├── entrypoint.sh              # 容器啟動腳本
    └── healthcheck.py             # 健康檢查腳本
```

### Dockerfile 說明

使用多階段構建優化鏡像大小：

1. **base**: 基礎環境設置
2. **dependencies**: 安裝依賴
3. **runtime**: 運行時環境（生產）
4. **development**: 開發環境

### 環境變數

#### 必需變數

```env
# 至少配置一個 LLM 提供商
OPENAI_API_KEY=sk-xxx
```

#### 可選變數

```env
# 端口配置
APP_PORT=8888
CHROMADB_PORT=8000
OLLAMA_PORT=11434

# 應用配置
LOG_LEVEL=INFO
DEFAULT_LLM_MODEL=gpt-4

# LangSmith 追蹤
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=xxx
```

---

## 服務架構

### 生產環境服務

1. **app**: 主應用容器
   - 運行 Jupyter Lab
   - 提供 API 服務
   - 自動健康檢查

2. **ollama**: 本地 LLM 服務
   - 支持多種開源模型
   - GPU 加速支持
   - 持久化存儲

3. **chromadb**: 向量數據庫
   - 用於 RAG 應用
   - 數據持久化
   - REST API 訪問

### 開發環境額外服務

4. **postgres**: PostgreSQL 數據庫
5. **redis**: Redis 緩存
6. **adminer**: 數據庫管理界面
7. **portainer**: Docker 容器管理界面

### 網絡和存儲

- **網絡**: `llm-network` (bridge, 172.28.0.0/16)
- **數據卷**:
  - `chroma-data`: ChromaDB 數據
  - `ollama-data`: Ollama 模型和配置
  - `postgres-data`: PostgreSQL 數據（開發）
  - `redis-data`: Redis 數據（開發）

---

## 使用方式

### 基本命令

```bash
# 啟動所有服務
docker-compose up -d

# 查看日誌
docker-compose logs -f

# 查看特定服務的日誌
docker-compose logs -f app

# 停止所有服務
docker-compose down

# 停止並刪除所有數據
docker-compose down -v

# 重新構建鏡像
docker-compose build --no-cache

# 進入容器
docker-compose exec app bash
```

### Ollama 模型管理

```bash
# 拉取模型
docker-compose exec ollama ollama pull llama2

# 列出已安裝的模型
docker-compose exec ollama ollama list

# 運行模型
docker-compose exec ollama ollama run llama2

# 刪除模型
docker-compose exec ollama ollama rm llama2
```

### 開發環境

```bash
# 啟動開發環境（包含額外的開發工具）
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# 查看所有服務
docker-compose -f docker-compose.yml -f docker-compose.dev.yml ps

# 停止開發環境
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
```

### 健康檢查

```bash
# 手動運行健康檢查
docker-compose exec app python /healthcheck.py

# 查看健康狀態
docker-compose ps
```

### 數據備份

```bash
# 備份 ChromaDB 數據
docker run --rm -v llm-agent-demo_chroma-data:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/chromadb-backup.tar.gz /data

# 備份 Ollama 模型
docker run --rm -v llm-agent-demo_ollama-data:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/ollama-backup.tar.gz /data

# 恢復數據
docker run --rm -v llm-agent-demo_chroma-data:/data -v $(pwd):/backup \
  ubuntu tar xzf /backup/chromadb-backup.tar.gz -C /
```

---

## GPU 支持

### 啟用 NVIDIA GPU

1. 安裝 [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

2. 確認 GPU 可用：
```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

3. GPU 配置已在 `docker-compose.yml` 的 ollama 服務中設置

### 無 GPU 環境

如果沒有 GPU，需要修改 `docker-compose.yml`：

```yaml
# 註釋掉 ollama 服務的 deploy 部分
ollama:
  # ... 其他配置
  # deploy:
  #   resources:
  #     limits:
  #       memory: 8G
  #     reservations:
  #       devices:
  #         - driver: nvidia
  #           count: all
  #           capabilities: [gpu]
```

---

## 常見問題

### 1. 端口衝突

**問題**: 端口已被佔用
```
Error: bind: address already in use
```

**解決方案**: 修改 `.env` 文件中的端口配置
```env
APP_PORT=8889
CHROMADB_PORT=8001
OLLAMA_PORT=11435
```

### 2. 記憶體不足

**問題**: 容器啟動失敗或運行緩慢

**解決方案**:
- 增加 Docker 的記憶體限制（Docker Desktop 設置）
- 減少 ollama 服務的記憶體限制
- 一次只運行需要的服務

### 3. Ollama 無法連接

**問題**: 應用無法連接到 Ollama

**解決方案**:
```bash
# 檢查 Ollama 服務狀態
docker-compose logs ollama

# 重啟 Ollama 服務
docker-compose restart ollama

# 測試連接
curl http://localhost:11434/api/tags
```

### 4. ChromaDB 數據丟失

**問題**: 重啟後數據消失

**解決方案**:
- 確保使用命名卷而不是匿名卷
- 不要使用 `docker-compose down -v`（會刪除卷）
- 使用 `docker-compose down` 而不是 `docker-compose rm`

### 5. 權限問題

**問題**: Permission denied 錯誤

**解決方案**:
```bash
# 修復數據目錄權限
sudo chown -R 1000:1000 ./data ./outputs ./logs

# 或在 docker-compose.yml 中設置用戶
user: "1000:1000"
```

### 6. 構建失敗

**問題**: Docker 構建過程中出錯

**解決方案**:
```bash
# 清理構建緩存
docker builder prune -a

# 重新構建
docker-compose build --no-cache

# 如果是網絡問題，使用代理
docker-compose build --build-arg http_proxy=http://proxy:port
```

---

## 性能優化

### 1. 使用 BuildKit

```bash
# 啟用 BuildKit（更快的構建）
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

docker-compose build
```

### 2. 多階段構建緩存

Dockerfile 已經使用多階段構建優化：
- 分離依賴安裝和應用代碼
- 利用 Docker 層緩存
- 減小最終鏡像大小

### 3. 資源限制

根據需要調整資源限制：

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G
    reservations:
      memory: 2G
```

---

## 安全建議

1. **不要將 .env 文件提交到 Git**
   ```bash
   # 確認 .env 在 .gitignore 中
   echo ".env" >> .gitignore
   ```

2. **使用非 root 用戶運行容器**
   - Dockerfile 已配置 `appuser`

3. **限制容器權限**
   ```yaml
   security_opt:
     - no-new-privileges:true
   cap_drop:
     - ALL
   ```

4. **使用私有鏡像倉庫**
   ```bash
   docker tag llm-agent-demo:latest your-registry.com/llm-agent-demo:latest
   docker push your-registry.com/llm-agent-demo:latest
   ```

5. **定期更新鏡像**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

---

## 監控和日誌

### 查看日誌

```bash
# 實時查看所有服務日誌
docker-compose logs -f

# 查看最近 100 行日誌
docker-compose logs --tail=100

# 只看錯誤日誌
docker-compose logs | grep ERROR
```

### 資源監控

```bash
# 查看資源使用情況
docker stats

# 查看特定容器
docker stats llm-agent-demo-app
```

### 使用 Portainer（開發環境）

訪問 http://localhost:9000 使用圖形界面管理容器。

---

## 維護

### 清理

```bash
# 清理未使用的容器
docker container prune

# 清理未使用的鏡像
docker image prune

# 清理所有未使用的資源
docker system prune -a

# 清理未使用的卷（小心！）
docker volume prune
```

### 更新

```bash
# 拉取最新代碼
git pull

# 重新構建和啟動
docker-compose up -d --build
```

---

## 參考資源

- [Docker 官方文檔](https://docs.docker.com/)
- [Docker Compose 文檔](https://docs.docker.com/compose/)
- [Ollama 文檔](https://github.com/ollama/ollama)
- [ChromaDB 文檔](https://docs.trychroma.com/)

---

## 支援

如有問題，請：
1. 查看本文檔的常見問題部分
2. 查看專案 Issues: https://github.com/markl-a/LLM-agent-Demo/issues
3. 創建新的 Issue 描述問題
