# Modal - 無服務器 GPU 運算平台

## 簡介

Modal 是一個現代化的無服務器雲端運算平台，專為 Python 開發者設計，讓你能夠輕鬆地將本地代碼部署到雲端 GPU 上運行。Modal 提供了簡潔的 Python API、按需付費的 GPU 資源、自動擴展能力和完整的容器化環境，特別適合機器學習模型推理、數據處理、定時任務等場景。

Modal 由 Erik Bernhardsson（Spotify 推薦系統負責人）創立，旨在簡化雲端計算的複雜性，讓開發者能夠專注於代碼本身，而不是基礎設施管理。它特別適合需要 GPU 資源但不想管理服務器的 AI/ML 工程師。

## 核心特點

### 1. 無服務器架構
- **零運維**: 無需管理服務器、容器或 Kubernetes
- **按需付費**: 只為實際使用的計算時間付費
- **自動擴展**: 根據負載自動增減資源
- **冷啟動優化**: 毫秒級的函數啟動時間

### 2. GPU 加速
- **多種 GPU**: T4、A10G、A100、H100 等
- **靈活配置**: 按需選擇 GPU 型號和數量
- **成本優化**: GPU 使用時才計費
- **批量處理**: 高效的 GPU 利用率

### 3. Python 優先
- **原生 Python**: 使用熟悉的 Python 語法
- **裝飾器風格**: 簡潔的函數裝飾器
- **本地開發**: 本地測試，一鍵部署
- **類型安全**: 完整的類型提示支持

### 4. 容器化環境
- **自動構建**: 自動創建和管理容器
- **依賴管理**: 聲明式的依賴定義
- **快速啟動**: 智能緩存加速部署
- **環境隔離**: 每個函數獨立環境

### 5. Web 端點
- **HTTP API**: 自動生成 REST API
- **WebSocket**: 實時雙向通信
- **流式響應**: 支持 Server-Sent Events
- **自定義域名**: 綁定自己的域名

### 6. 數據持久化
- **Volumes**: 持久化文件存儲
- **Secrets**: 安全的密鑰管理
- **Dicts**: 鍵值存儲
- **Queues**: 消息隊列

## 安裝

### 安裝 Modal 客戶端

```bash
pip install modal
```

### 設置 Modal 帳號

```bash
# 創建帳號並獲取 token
modal token new

# 這會打開瀏覽器進行認證
# 認證成功後 token 會自動保存
```

### 驗證安裝

```bash
modal --help
```

### 安裝本示例依賴

```bash
pip install -r requirements.txt
```

## 系統要求

### 本地環境
- **Python**: 3.8+
- **網絡**: 穩定的網絡連接
- **操作系統**: Linux、macOS、Windows

### Modal 雲端資源
- **CPU**: 0.25-32 核心
- **內存**: 128MB-256GB
- **GPU**: T4、A10G、A100、H100 等
- **存儲**: 無限制（按使用計費）

## 核心概念

### 函數裝飾器
使用 `@app.function()` 將本地函數轉換為雲端函數：

```python
import modal

app = modal.App("my-app")

@app.function()
def my_function(x: int) -> int:
    return x * 2

# 本地調用（在雲端執行）
with app.run():
    result = my_function.remote(5)
    print(result)  # 10
```

### GPU 加速
輕鬆使用 GPU 資源：

```python
@app.function(gpu="A100")
def gpu_task():
    import torch
    print(f"CUDA available: {torch.cuda.is_available()}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
```

### Web 端點
創建 HTTP API：

```python
@app.function()
@modal.web_endpoint(method="POST")
def api_endpoint(data: dict):
    return {"result": process(data)}

# 自動生成 URL:
# https://your-username--my-app-api-endpoint.modal.run
```

### 定時任務
設置定時執行：

```python
@app.function(schedule=modal.Period(hours=1))
def hourly_task():
    print("This runs every hour")
```

### 容器鏡像
自定義運行環境：

```python
image = modal.Image.debian_slim().pip_install(
    "torch",
    "transformers",
    "numpy"
)

@app.function(image=image)
def ml_task():
    import torch
    # Your ML code here
```

### 持久化存儲
使用 Volumes 存儲數據：

```python
volume = modal.Volume.from_name("my-data")

@app.function(volumes={"/data": volume})
def save_data():
    with open("/data/file.txt", "w") as f:
        f.write("Hello Modal!")
```

## 使用案例

### 1. AI 模型推理
- **LLM 服務**: 部署 GPT、LLaMA 等大語言模型
- **圖像生成**: Stable Diffusion、DALL-E API
- **語音處理**: Whisper 語音識別服務
- **批量推理**: 大規模數據批處理

### 2. 數據處理
- **ETL 管道**: 數據提取、轉換、加載
- **視頻處理**: 視頻轉碼、幀提取
- **圖像處理**: 批量圖像調整、濾鏡
- **數據分析**: 大規模數據聚合

### 3. Web 應用
- **API 服務**: RESTful API 後端
- **Webhook 處理**: GitHub、Stripe webhook
- **表單處理**: 文件上傳、數據驗證
- **實時應用**: WebSocket 聊天室

### 4. 定時任務
- **數據同步**: 定期同步外部數據
- **報告生成**: 每日/每週報告
- **健康檢查**: 監控和告警
- **備份任務**: 自動備份

### 5. 機器學習訓練
- **模型訓練**: 雲端 GPU 訓練
- **超參數搜索**: 並行實驗
- **模型評估**: 批量評估
- **數據增強**: 大規模數據增強

### 6. DevOps 工具
- **CI/CD**: 自動化測試和部署
- **代碼掃描**: 安全和質量掃描
- **性能測試**: 負載測試
- **日誌處理**: 日誌聚合和分析

## 示例文件說明

本目錄包含 10 個完整的示例文件,涵蓋 Modal 的各個方面:

1. **01_快速開始.py** - Modal 基礎和第一個雲端函數
2. **02_函數部署.py** - 部署和調用遠程函數
3. **03_GPU運算.py** - 使用 GPU 加速計算
4. **04_定時任務.py** - 設置定時執行的任務
5. **05_Web端點.py** - 創建 HTTP API 端點
6. **06_模型推理.py** - 部署機器學習模型推理服務
7. **07_數據處理.py** - 大規模數據處理管道
8. **08_並行計算.py** - 並行執行和 Map/Reduce
9. **09_持久化存儲.py** - 使用 Volumes、Secrets 和 Dicts
10. **10_生產應用.py** - 完整的生產級應用示例

## 最佳實踐

### 1. 成本優化
- 使用合適的 GPU 型號（不要過度配置）
- 啟用批量處理提升 GPU 利用率
- 使用 spot instances（如可用）
- 設置合理的超時時間
- 監控和分析使用情況

### 2. 性能優化
- 使用容器鏡像緩存
- 預加載大文件和模型
- 批量處理請求
- 合理設置並發數
- 使用持久化存儲減少重複下載

### 3. 開發流程
- 先在本地測試函數邏輯
- 使用 `modal run` 測試雲端執行
- 使用 `modal deploy` 部署生產
- 實施版本控制
- 編寫測試用例

### 4. 安全性
- 使用 Secrets 管理敏感信息
- 不要硬編碼 API 密鑰
- 實施輸入驗證
- 使用 HTTPS 端點
- 定期輪換密鑰

### 5. 監控和日誌
- 使用 `print()` 輸出日誌
- 在 Modal Dashboard 查看日誌
- 設置錯誤告警
- 監控成本和使用量
- 分析性能指標

### 6. 錯誤處理
- 使用 try-except 捕獲異常
- 返回有意義的錯誤消息
- 實施重試機制
- 設置合理的超時
- 記錄錯誤詳情

## 價格模型

### 計算資源（按秒計費）
- **CPU**: $0.000031/秒/核心
- **內存**: $0.0000041/秒/GB
- **T4 GPU**: $0.00055/秒
- **A10G GPU**: $0.0012/秒
- **A100 GPU**: $0.0040/秒
- **H100 GPU**: $0.0120/秒

### 存儲和網絡
- **Volumes**: $0.15/GB/月
- **網絡出口**: $0.12/GB（超過 10GB）
- **請求**: 前 200 萬免費

### 免費額度
- **每月免費**: $30 信用額度
- **足夠運行**: 約 25 小時 T4 GPU

## 與其他平台對比

### Modal vs 其他無服務器平台

| 特性 | Modal | AWS Lambda | Google Cloud Run | Replicate |
|-----|-------|------------|------------------|-----------|
| GPU 支持 | ✅ 多種 | ❌ | ❌ | ✅ |
| Python 優先 | ✅ | 部分 | 部分 | ✅ |
| 冷啟動 | < 1秒 | 1-5秒 | 1-3秒 | 5-30秒 |
| 最大執行時間 | 無限制 | 15分鐘 | 60分鐘 | 無限制 |
| 價格 | 競爭力強 | 便宜 | 中等 | 較貴 |
| 易用性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 本地開發 | ✅ | 模擬 | 模擬 | ❌ |
| 自動擴展 | ✅ | ✅ | ✅ | ✅ |

## 架構設計

```
┌─────────────────────────────────────────────┐
│           本地開發環境                        │
│  ┌────────────────────────────────┐         │
│  │     Python 代碼                │         │
│  │  @app.function(gpu="A100")     │         │
│  │  def my_function():            │         │
│  │      ...                       │         │
│  └────────────┬───────────────────┘         │
└───────────────┼─────────────────────────────┘
                │ modal run / modal deploy
                ▼
┌─────────────────────────────────────────────┐
│           Modal 雲端平台                     │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │        控制平面                       │  │
│  │  • 函數調度                           │  │
│  │  • 資源分配                           │  │
│  │  • 自動擴展                           │  │
│  └──────────────┬───────────────────────┘  │
│                 │                           │
│  ┌──────────────▼───────────────────────┐  │
│  │        執行環境                       │  │
│  │  ┌──────┐  ┌──────┐  ┌──────┐       │  │
│  │  │Container│Container│Container│      │  │
│  │  │ GPU 1 │ │ GPU 2 │ │ GPU 3 │       │  │
│  │  └──────┘  └──────┘  └──────┘       │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │        存儲層                         │  │
│  │  • Volumes (持久化)                   │  │
│  │  • Secrets (密鑰)                     │  │
│  │  • Dicts (KV 存儲)                    │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────┐
│           外部服務                           │
│  • HTTP/HTTPS 端點                          │
│  • Webhook                                  │
│  • API 客戶端                               │
└─────────────────────────────────────────────┘
```

## 快速開始

### 最簡單的示例

```python
import modal

# 創建 Modal 應用
app = modal.App("hello-modal")

# 定義雲端函數
@app.function()
def hello(name: str) -> str:
    return f"Hello, {name}!"

# 本地入口
@app.local_entrypoint()
def main():
    # 調用遠程函數
    result = hello.remote("World")
    print(result)  # Hello, World!
```

### 運行方式

```bash
# 方式 1: 直接運行
modal run hello.py

# 方式 2: 部署為服務
modal deploy hello.py

# 方式 3: 作為 Web API
modal serve hello.py
```

## 常用命令

```bash
# 認證和設置
modal token new              # 創建新 token
modal token set --token-id xxx --token-secret yyy

# 運行和部署
modal run script.py          # 運行腳本
modal deploy script.py       # 部署為服務
modal serve script.py        # 本地開發服務器

# 管理
modal app list               # 列出所有應用
modal app stop app-name      # 停止應用
modal app logs app-name      # 查看日誌

# Volumes
modal volume list            # 列出 volumes
modal volume create vol-name # 創建 volume
modal volume delete vol-name # 刪除 volume

# Secrets
modal secret list            # 列出 secrets
modal secret create name     # 創建 secret
```

## 相關資源

- **官方網站**: https://modal.com
- **官方文檔**: https://modal.com/docs
- **GitHub**: https://github.com/modal-labs/modal-client
- **Discord 社群**: https://discord.gg/modal
- **Blog**: https://modal.com/blog
- **示例庫**: https://modal.com/docs/examples
- **定價**: https://modal.com/pricing
- **Dashboard**: https://modal.com/apps

## 環境變量

```bash
# Modal 配置
MODAL_TOKEN_ID=xxx
MODAL_TOKEN_SECRET=yyy
MODAL_ENVIRONMENT=main

# 應用配置
MODAL_PROFILE=default
MODAL_LOGLEVEL=INFO
```

## 故障排除

### 常見問題

**Q: 函數執行失敗**
- 檢查依賴是否正確安裝
- 查看日誌輸出
- 確認 GPU 資源是否可用

**Q: 冷啟動時間長**
- 使用容器鏡像緩存
- 減少依賴數量
- 使用預構建鏡像

**Q: 成本過高**
- 檢查函數超時設置
- 優化批處理大小
- 選擇合適的 GPU

**Q: 無法連接**
- 確認網絡連接
- 檢查 token 是否有效
- 查看 Modal 狀態頁面

## 版本信息

- **Modal**: 0.57+
- **Python**: 3.8+
- **支持的 GPU**: T4, A10G, A100, H100
- **支持的操作系統**: Linux, macOS, Windows

## 授權

Modal 是商業服務，但提供免費額度。本示例代碼採用 MIT 授權，僅供學習參考使用。

---

**注意**: Modal 是付費服務，雖然提供每月 $30 的免費額度，但請注意監控使用量，避免意外費用。建議設置預算告警。
