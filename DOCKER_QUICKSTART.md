# Docker 快速啟動指南

這是 LLM Agent Demo 專案的 Docker 快速啟動指南。詳細文檔請參閱 [DOCKER.md](DOCKER.md)。

## 5 分鐘快速開始

### 1️⃣ 前置要求

- [Docker](https://docs.docker.com/get-docker/) 20.10+
- [Docker Compose](https://docs.docker.com/compose/install/) 2.0+
- 至少 8GB RAM

### 2️⃣ 配置環境變數

```bash
# 複製環境變數範例
cp .env.example .env

# 編輯並填入你的 API Keys（至少配置一個）
nano .env
```

**必需配置（至少一個）：**
- `OPENAI_API_KEY` - OpenAI API Key
- `GOOGLE_API_KEY` - Google Gemini API Key
- `ANTHROPIC_API_KEY` - Anthropic Claude API Key
- `GROQ_API_KEY` - Groq API Key

### 3️⃣ 啟動服務

**方式一：使用快速啟動腳本（推薦）**

```bash
./docker-start.sh
```

腳本會引導你完成：
- 系統檢查
- 環境配置
- 模式選擇
- 服務啟動

**方式二：使用 Docker Compose**

```bash
# 生產模式（精簡）
docker-compose up -d

# 開發模式（完整，包含調試工具）
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

**方式三：使用 Makefile**

```bash
# 生產模式
make docker-up

# 開發模式
make docker-dev
```

### 4️⃣ 訪問服務

服務啟動後（約 1-2 分鐘），訪問：

- **Jupyter Lab**: http://localhost:8888
- **ChromaDB**: http://localhost:8000
- **Ollama API**: http://localhost:11434

開發模式額外服務：
- **Adminer**: http://localhost:8081
- **Portainer**: http://localhost:9000

### 5️⃣ 驗證安裝

```bash
# 查看服務狀態
docker-compose ps

# 運行健康檢查
docker-compose exec app python /healthcheck.py

# 查看日誌
docker-compose logs -f app
```

---

## 常用命令速查

### 服務管理

```bash
# 啟動服務
docker-compose up -d

# 停止服務
docker-compose down

# 重啟服務
docker-compose restart

# 查看狀態
docker-compose ps

# 查看日誌
docker-compose logs -f
```

### Makefile 快捷命令

```bash
make docker-up          # 啟動服務（生產）
make docker-dev         # 啟動服務（開發）
make docker-down        # 停止服務
make docker-restart     # 重啟服務
make docker-logs        # 查看日誌
make docker-shell       # 進入容器
make docker-status      # 查看狀態
make docker-health      # 健康檢查
make docker-backup      # 備份數據
```

### Ollama 模型管理

```bash
# 拉取模型
docker-compose exec ollama ollama pull llama2

# 列出模型
docker-compose exec ollama ollama list

# 運行模型
docker-compose exec ollama ollama run llama2

# 快捷方式（使用 Makefile）
make docker-ollama-pull
make docker-ollama-list
```

### 調試和維護

```bash
# 進入應用容器
docker-compose exec app bash

# 進入 Ollama 容器
docker-compose exec ollama bash

# 查看實時資源使用
docker stats

# 清理未使用的資源
docker system prune -a
```

---

## 服務架構

```
┌─────────────────────────────────────────────────┐
│                LLM Agent Demo                    │
│                                                  │
│  ┌─────────┐  ┌──────────┐  ┌───────────┐      │
│  │   App   │  │ ChromaDB │  │  Ollama   │      │
│  │ :8888   │  │  :8000   │  │  :11434   │      │
│  └─────────┘  └──────────┘  └───────────┘      │
│       │             │              │            │
│       └─────────────┴──────────────┘            │
│                llm-network                       │
└─────────────────────────────────────────────────┘
```

**核心服務：**
- **App**: Jupyter Lab 主應用（Python 3.11）
- **ChromaDB**: 向量數據庫（用於 RAG）
- **Ollama**: 本地 LLM 服務（支持多種開源模型）

**開發環境額外服務：**
- **PostgreSQL**: 關系型數據庫
- **Redis**: 緩存服務
- **Adminer**: 數據庫管理界面
- **Portainer**: 容器管理界面

---

## 數據持久化

數據存儲在 Docker 卷中，重啟容器不會丟失：

- `chroma-data`: ChromaDB 向量數據
- `ollama-data`: Ollama 模型和配置
- `postgres-data`: PostgreSQL 數據（開發模式）
- `redis-data`: Redis 數據（開發模式）

**備份數據：**

```bash
# 自動備份（推薦）
make docker-backup

# 手動備份
docker run --rm -v llm-agent-demo_chroma-data:/data \
  -v $(pwd):/backup ubuntu \
  tar czf /backup/chromadb-backup.tar.gz /data
```

---

## 故障排除

### ❌ 端口已被佔用

**錯誤**: `Error: bind: address already in use`

**解決方案**: 編輯 `.env` 文件修改端口

```env
APP_PORT=8889
CHROMADB_PORT=8001
OLLAMA_PORT=11435
```

### ❌ 記憶體不足

**症狀**: 容器啟動失敗或運行緩慢

**解決方案**:
1. 增加 Docker Desktop 的記憶體限制
2. 只啟動需要的服務：
   ```bash
   docker-compose up -d app chromadb
   ```

### ❌ Ollama 無法連接

**解決方案**:

```bash
# 檢查 Ollama 日誌
docker-compose logs ollama

# 重啟 Ollama
docker-compose restart ollama

# 測試連接
curl http://localhost:11434/api/tags
```

### ❌ GPU 不可用

**檢查 GPU**:
```bash
nvidia-smi
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

**如果沒有 GPU**: 編輯 `docker-compose.yml`，註釋掉 ollama 服務的 `deploy` 部分

### 🔍 查看詳細日誌

```bash
# 所有服務
docker-compose logs -f

# 特定服務
docker-compose logs -f app
docker-compose logs -f ollama

# 最近 100 行
docker-compose logs --tail=100
```

---

## 環境切換

### 從開發環境切換到生產環境

```bash
# 停止開發環境
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

# 啟動生產環境
docker-compose up -d
```

### 從生產環境切換到開發環境

```bash
# 停止生產環境
docker-compose down

# 啟動開發環境
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

---

## 性能優化建議

### 1. 使用 BuildKit 加速構建

```bash
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
docker-compose build
```

### 2. 啟用 GPU 加速（Ollama）

確保安裝了 [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

### 3. 調整資源限制

編輯 `docker-compose.yml`：

```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 8G
```

---

## 下一步

- 📖 閱讀完整文檔: [DOCKER.md](DOCKER.md)
- 🚀 查看專案說明: [README.md](README.md)
- 💻 開始使用 Jupyter Lab: http://localhost:8888
- 📚 探索示例代碼: `/examples` 目錄

---

## 獲取幫助

- 查看常見問題: [DOCKER.md#常見問題](DOCKER.md#常見問題)
- 提交 Issue: https://github.com/markl-a/LLM-agent-Demo/issues
- 查看完整文檔: [DOCKER.md](DOCKER.md)

---

**祝使用愉快！** 🎉
