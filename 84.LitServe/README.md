# LitServe - Lightning AI 推理服務框架

## 簡介

LitServe 是 Lightning AI 推出的高性能 AI 模型推理服務框架，專為將機器學習模型快速部署為生產級 API 服務而設計。它提供了簡潔的 API、高性能的推理引擎、內置的批量處理和流式響應功能，讓開發者能夠輕鬆將任何 PyTorch、TensorFlow、scikit-learn 等模型部署為可擴展的 REST API 服務。

LitServe 由 Lightning AI 團隊開發（PyTorch Lightning 的創建者），專注於簡化模型部署流程，同時提供企業級的性能和可靠性。它特別適合需要快速迭代、高併發處理和靈活部署的 AI 應用場景。

## 核心特點

### 1. 簡潔的 API
- **最小化代碼**: 只需幾行代碼即可部署模型
- **統一接口**: 支持任何機器學習框架
- **類型安全**: 使用 Pydantic 進行數據驗證
- **自動文檔**: 自動生成 OpenAPI 文檔

### 2. 高性能推理
- **自動批量處理**: 智能批處理提升吞吐量
- **GPU 加速**: 原生支持 CUDA 和多 GPU
- **異步處理**: 基於 FastAPI 的異步架構
- **連接池**: 高效的連接管理

### 3. 靈活的部署
- **本地開發**: 快速本地測試
- **容器化**: 內置 Docker 支持
- **雲部署**: 輕鬆部署到 AWS、GCP、Azure
- **Lightning Cloud**: 一鍵部署到 Lightning AI 雲平台

### 4. 生產就緒
- **監控指標**: 內置 Prometheus 指標
- **健康檢查**: 自動健康檢查端點
- **負載均衡**: 支持水平擴展
- **錯誤處理**: 完善的錯誤處理機制

### 5. 流式響應
- **實時流式**: 支持 Server-Sent Events (SSE)
- **WebSocket**: 雙向通信支持
- **漸進式輸出**: 適合生成式 AI 模型
- **低延遲**: 最小化首字節時間

### 6. 安全性
- **身份驗證**: 內置 API key 和 JWT 支持
- **速率限制**: 防止濫用
- **CORS 配置**: 靈活的跨域設置
- **輸入驗證**: 自動驗證請求數據

## 安裝

### 基礎安裝

```bash
pip install litserve
```

### 完整安裝（包含所有依賴）

```bash
pip install "litserve[full]"
```

### 從源碼安裝

```bash
git clone https://github.com/Lightning-AI/litserve
cd litserve
pip install -e .
```

### 安裝本示例依賴

```bash
pip install -r requirements.txt
```

## 系統要求

### 最小配置
- **Python**: 3.8+
- **CPU**: 2 核心
- **內存**: 4GB RAM
- **硬碟**: 10GB 可用空間

### 推薦配置（GPU 加速）
- **Python**: 3.10+
- **CPU**: 8+ 核心
- **內存**: 16GB+ RAM
- **GPU**: NVIDIA GPU (CUDA 11.0+)
- **硬碟**: SSD 存儲,50GB+ 可用空間

## 核心概念

### LitAPI 基類
LitServe 的核心是 `LitAPI` 類，你需要繼承它並實現以下方法：

```python
from litserve import LitAPI

class MyAPI(LitAPI):
    def setup(self, device):
        """初始化模型（在服務啟動時調用一次）"""
        self.model = load_model()
        self.model.to(device)

    def decode_request(self, request):
        """解析請求數據"""
        return request["input"]

    def predict(self, x):
        """執行推理"""
        return self.model(x)

    def encode_response(self, output):
        """格式化響應"""
        return {"output": output}
```

### 批量處理
自動批處理可以顯著提升吞吐量：

```python
from litserve import LitAPI

class BatchAPI(LitAPI):
    def setup(self, device):
        self.model = load_model()

    def decode_request(self, request):
        return request["input"]

    def batch(self, inputs):
        """將多個請求批量處理"""
        return torch.stack(inputs)

    def predict(self, x_batch):
        """批量推理"""
        return self.model(x_batch)

    def unbatch(self, output):
        """拆分批量結果"""
        return list(output)

    def encode_response(self, output):
        return {"output": output.tolist()}
```

### 流式響應
支持實時流式輸出：

```python
from litserve import LitAPI

class StreamAPI(LitAPI):
    def setup(self, device):
        self.model = load_model()

    def predict(self, x):
        """生成流式輸出"""
        for token in self.model.generate_stream(x):
            yield token

    def encode_response(self, output_stream):
        """流式編碼響應"""
        for token in output_stream:
            yield {"token": token}
```

## 使用案例

### 1. 文本生成 API
- **LLM 服務**: 部署 GPT、BERT 等語言模型
- **聊天機器人**: 實時對話服務
- **內容生成**: 文章、代碼生成

### 2. 圖像處理
- **圖像分類**: ResNet、ViT 等模型服務
- **目標檢測**: YOLO、Faster R-CNN API
- **圖像生成**: Stable Diffusion、DALL-E

### 3. 語音處理
- **語音識別**: Whisper、Wav2Vec2 API
- **語音合成**: TTS 模型服務
- **語音轉換**: 聲音克隆服務

### 4. 推薦系統
- **個性化推薦**: 實時推薦 API
- **內容過濾**: 智能過濾服務
- **排序優化**: 排序模型服務

### 5. 時序預測
- **股票預測**: 金融時序模型
- **需求預測**: 銷售預測服務
- **異常檢測**: 實時監控 API

### 6. 多模態應用
- **圖文理解**: CLIP、BLIP 等模型
- **視頻分析**: 視頻理解服務
- **跨模態檢索**: 多模態搜索 API

## 示例文件說明

本目錄包含 10 個完整的示例文件,涵蓋 LitServe 的各個方面:

1. **01_快速開始.py** - 最簡單的模型服務示例
2. **02_簡單服務.py** - 完整的 REST API 服務
3. **03_批量處理.py** - 自動批處理優化吞吐量
4. **04_流式響應.py** - 實時流式輸出
5. **05_GPU加速.py** - GPU 推理加速
6. **06_多模型.py** - 同時服務多個模型
7. **07_身份驗證.py** - API 安全和身份驗證
8. **08_監控指標.py** - Prometheus 監控集成
9. **09_負載均衡.py** - 水平擴展和負載均衡
10. **10_生產部署.py** - 完整的生產部署配置

## 最佳實踐

### 1. 性能優化
- 啟用批量處理以提升吞吐量
- 使用 GPU 加速計算密集型任務
- 適當配置 worker 數量
- 使用連接池管理資源

### 2. 資源管理
- 在 `setup()` 中加載模型（避免重複加載）
- 使用適當的批大小
- 監控內存使用
- 實施請求超時

### 3. 錯誤處理
- 驗證輸入數據
- 捕獲並記錄異常
- 返回有意義的錯誤消息
- 實施重試機制

### 4. 監控與日誌
- 記錄請求和響應
- 監控延遲和吞吐量
- 設置告警閾值
- 定期檢查健康狀態

### 5. 安全性
- 使用 API 密鑰認證
- 實施速率限制
- 驗證所有輸入
- 定期更新依賴

### 6. 部署策略
- 使用容器化部署
- 實施藍綠部署
- 配置自動擴展
- 設置監控告警

## 性能指標

### 吞吐量（批量處理）
- **小模型**: 1000+ 請求/秒
- **中等模型**: 100-500 請求/秒
- **大模型**: 10-50 請求/秒

### 延遲
- **CPU 推理**: 10-100ms
- **GPU 推理**: 1-10ms
- **批處理延遲**: +10-50ms（換取更高吞吐量）

### 資源使用
- **內存開銷**: 模型大小 + 100-500MB
- **CPU 使用**: 根據並發數線性增長
- **GPU 使用**: 批處理可達 90%+ 利用率

## 與其他框架對比

### LitServe vs 其他推理服務

| 特性 | LitServe | TorchServe | TensorFlow Serving | BentoML |
|-----|----------|------------|-------------------|---------|
| 易用性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| 性能 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 框架支持 | 全部 | PyTorch | TensorFlow | 全部 |
| 流式響應 | ✅ | ❌ | ❌ | ✅ |
| 批處理 | 自動 | 手動 | 自動 | 手動 |
| GPU 支持 | ✅ | ✅ | ✅ | ✅ |
| 監控 | Prometheus | Prometheus | Prometheus | Prometheus |
| 雲集成 | Lightning Cloud | AWS | GCP | 多雲 |

## 架構設計

```
┌─────────────────────────────────────────────┐
│           客戶端應用                          │
│  Web App │ Mobile App │ Backend Service    │
└──────────────┬──────────────────────────────┘
               │ HTTP/WebSocket
┌──────────────▼──────────────────────────────┐
│          負載均衡器                           │
│         (Nginx/Traefik)                     │
└──────────────┬──────────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
┌───────▼───────┐ ┌──▼────────────┐
│  LitServe #1  │ │  LitServe #2  │
│               │ │               │
│  ┌─────────┐  │ │  ┌─────────┐  │
│  │ FastAPI │  │ │  │ FastAPI │  │
│  └────┬────┘  │ │  └────┬────┘  │
│       │       │ │       │       │
│  ┌────▼────┐  │ │  ┌────▼────┐  │
│  │  LitAPI │  │ │  │  LitAPI │  │
│  │ (Model) │  │ │  │ (Model) │  │
│  └─────────┘  │ │  └─────────┘  │
└───────┬───────┘ └───┬───────────┘
        │             │
        │  GPU #1     │  GPU #2
        └─────────────┘
               │
┌──────────────▼──────────────────────────────┐
│          監控和日誌                           │
│  Prometheus │ Grafana │ CloudWatch         │
└─────────────────────────────────────────────┘
```

## 部署選項

### 1. 本地開發
```bash
python your_api.py
```

### 2. Docker 容器
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "your_api.py"]
```

### 3. Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: litserve-app
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: your-litserve-image:latest
        ports:
        - containerPort: 8000
```

### 4. Lightning Cloud
```bash
lightning run app your_api.py --cloud
```

## 相關資源

- **官方網站**: https://lightning.ai/lightning-docs/litserve
- **GitHub**: https://github.com/Lightning-AI/litserve
- **官方文檔**: https://lightning.ai/docs/litserve
- **Lightning AI**: https://lightning.ai
- **PyTorch Lightning**: https://lightning.ai/docs/pytorch
- **社群論壇**: https://lightning.ai/forums
- **Discord**: https://discord.gg/lightning-ai
- **教學影片**: https://www.youtube.com/@LightningAI

## 快速開始

### 最簡單的示例

```python
from litserve import LitAPI, LitServer

# 1. 定義 API
class SimpleAPI(LitAPI):
    def setup(self, device):
        # 加載模型
        self.model = lambda x: x.upper()

    def decode_request(self, request):
        # 解析請求
        return request["text"]

    def predict(self, x):
        # 執行推理
        return self.model(x)

    def encode_response(self, output):
        # 返回響應
        return {"result": output}

# 2. 創建服務器
server = LitServer(SimpleAPI(), accelerator="auto")

# 3. 啟動服務
server.run(port=8000)
```

### 測試 API

```bash
# 使用 curl 測試
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "hello world"}'

# 響應
# {"result": "HELLO WORLD"}
```

## 版本信息

- **LitServe**: 0.2+
- **Python**: 3.8+
- **FastAPI**: 0.100+
- **Uvicorn**: 0.20+
- **支持的框架**: PyTorch, TensorFlow, JAX, scikit-learn, XGBoost 等

## 授權

LitServe 採用 Apache License 2.0 授權。本示例代碼僅供學習參考使用。

---

**注意**: LitServe 仍在積極開發中，API 可能會有變化。建議查看官方文檔獲取最新信息。對於生產環境，建議進行充分測試並實施適當的監控和錯誤處理機制。
