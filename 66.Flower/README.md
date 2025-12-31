# Flower - 聯邦學習框架

## 簡介

Flower (flwr) 是一個友好的聯邦學習框架，用於構建、訓練和部署分佈式機器學習系統。它專注於隱私保護的 AI 訓練，允許多個客戶端在不共享原始數據的情況下協同訓練模型。

Flower 支持任何機器學習框架（PyTorch、TensorFlow、JAX 等），可在異構設備上運行，並提供強大的隱私保護機制。

## 核心特點

### 1. **框架無關性**
- 支持 PyTorch、TensorFlow、scikit-learn 等
- 靈活的客戶端-服務器架構
- 易於集成現有 ML 管道

### 2. **隱私保護**
- **差分隱私 (Differential Privacy)**：在模型更新中添加噪聲
- **安全聚合 (Secure Aggregation)**：加密的模型參數聚合
- **本地數據保留**：數據永不離開客戶端設備

### 3. **異構支持**
- 處理不同計算能力的設備
- 支持非 IID 數據分佈
- 動態客戶端選擇

### 4. **可擴展性**
- 支持數百萬客戶端
- 自定義聚合策略
- 靈活的通信協議

### 5. **生產就緒**
- Docker 支持
- Kubernetes 部署
- 監控和日誌記錄

## 安裝

```bash
# 基本安裝
pip install flwr

# 使用 PyTorch
pip install flwr[pytorch]

# 使用 TensorFlow
pip install flwr[tensorflow]

# 完整安裝（包含所有依賴）
pip install flwr[all]
```

或使用本項目的 requirements.txt：

```bash
pip install -r requirements.txt
```

## 快速開始

### 基本聯邦學習流程

```python
import flwr as fl

# 1. 定義客戶端
class FlowerClient(fl.client.NumPyClient):
    def get_parameters(self, config):
        return get_model_parameters()

    def fit(self, parameters, config):
        set_model_parameters(parameters)
        train()
        return get_model_parameters(), num_examples, {}

    def evaluate(self, parameters, config):
        set_model_parameters(parameters)
        loss, accuracy = test()
        return loss, num_examples, {"accuracy": accuracy}

# 2. 啟動客戶端
fl.client.start_numpy_client(server_address="localhost:8080", client=FlowerClient())

# 3. 啟動服務器
fl.server.start_server(
    server_address="0.0.0.0:8080",
    config=fl.server.ServerConfig(num_rounds=3),
)
```

## 使用案例

### 1. 醫療健康
```python
# 醫院聯邦學習示例
# 多家醫院協同訓練疾病診斷模型，無需共享患者數據

strategy = fl.server.strategy.FedAvg(
    min_available_clients=5,  # 至少 5 家醫院
    min_fit_clients=3,        # 每輪至少 3 家參與訓練
)

fl.server.start_server(
    config=fl.server.ServerConfig(num_rounds=10),
    strategy=strategy,
)
```

### 2. 金融風控
```python
# 銀行聯邦學習示例
# 多家銀行協同訓練反欺詐模型

from flwr.server.strategy import FedProx

# FedProx 適合處理異構數據
strategy = FedProx(
    proximal_mu=0.1,  # 正則化參數
    min_available_clients=10,
)
```

### 3. 移動設備
```python
# 手機聯邦學習示例
# 訓練鍵盤預測模型，保護用戶隱私

# 支持設備異構性和間歇性連接
strategy = fl.server.strategy.FedAvg(
    min_available_clients=100,
    fraction_fit=0.1,  # 每輪隨機選擇 10% 設備
    fraction_evaluate=0.05,
)
```

### 4. 物聯網 (IoT)
```python
# IoT 設備聯邦學習
# 智能家居設備協同學習用戶習慣

strategy = fl.server.strategy.FedAvg(
    min_available_clients=50,
    on_fit_config_fn=lambda rnd: {"batch_size": 16, "local_epochs": 1}
)
```

## 隱私保護場景

### 1. 差分隱私保護

```python
from flwr.server.strategy import DifferentialPrivacyClientSideFixedClipping

# 客戶端差分隱私
strategy = DifferentialPrivacyClientSideFixedClipping(
    noise_multiplier=0.5,      # 噪聲倍數
    clipping_norm=1.0,         # 梯度裁剪範數
    num_sampled_clients=10,    # 採樣客戶端數量
)
```

### 2. 安全聚合

```python
# 使用安全聚合保護模型更新
# 服務器無法看到單個客戶端的模型更新

strategy = fl.server.strategy.FedAvg(
    # 啟用安全聚合協議
    fit_metrics_aggregation_fn=weighted_average,
)
```

### 3. 本地差分隱私

```python
import torch

class PrivateClient(fl.client.NumPyClient):
    def fit(self, parameters, config):
        # 訓練模型
        model = train(parameters)

        # 添加本地差分隱私噪聲
        for param in model.parameters():
            noise = torch.normal(0, 0.1, size=param.shape)
            param.data.add_(noise)

        return get_parameters(model), len(trainloader.dataset), {}
```

### 4. 聯邦遷移學習

```python
# 使用預訓練模型，只共享部分層的更新
class TransferLearningClient(fl.client.NumPyClient):
    def get_parameters(self, config):
        # 只返回最後幾層的參數
        return model.fc.state_dict()

    def fit(self, parameters, config):
        # 只更新最後幾層
        model.fc.load_state_dict(parameters)
        # 凍結其他層
        for param in model.features.parameters():
            param.requires_grad = False
        train()
        return model.fc.state_dict(), num_examples, {}
```

### 5. 多方安全計算

```python
# 結合多方安全計算協議
from flwr.server.strategy import SecAgg

strategy = SecAgg(
    fraction_fit=0.5,
    min_available_clients=3,
    # 安全聚合需要至少 3 個客戶端
)
```

## 核心概念

### 聯邦學習流程

1. **初始化**：服務器初始化全局模型
2. **分發**：服務器將模型發送給選定的客戶端
3. **本地訓練**：客戶端使用本地數據訓練模型
4. **上傳**：客戶端將模型更新發送回服務器
5. **聚合**：服務器聚合所有客戶端的更新
6. **迭代**：重複步驟 2-5，直到收斂

### 關鍵組件

- **Client（客戶端）**：持有數據並執行本地訓練
- **Server（服務器）**：協調訓練過程並聚合更新
- **Strategy（策略）**：定義聚合算法（FedAvg、FedProx 等）
- **Config（配置）**：控制訓練超參數

## 示例文件說明

- `01_快速開始.py` - Flower 基本概念和簡單示例
- `02_客戶端定義.py` - 如何實現自定義客戶端
- `03_服務端配置.py` - 服務器配置和策略選擇
- `04_模型訓練.py` - 分佈式模型訓練流程
- `05_聚合策略.py` - FedAvg、FedProx 等聚合策略
- `06_差分隱私.py` - 差分隱私保護機制
- `07_安全聚合.py` - 安全聚合協議
- `08_異構設備.py` - 處理不同計算能力的設備
- `09_模型評估.py` - 聯邦學習中的模型評估
- `10_生產部署.py` - 生產環境部署配置

## 進階主題

### 自定義聚合策略

```python
from flwr.server.strategy import Strategy

class CustomStrategy(Strategy):
    def aggregate_fit(self, rnd, results, failures):
        # 自定義聚合邏輯
        pass
```

### 異步聯邦學習

```python
# 支持客戶端異步更新
strategy = fl.server.strategy.FedAsync(
    tau=10,  # 聚合窗口
)
```

### 個性化聯邦學習

```python
# 每個客戶端保留個性化層
class PersonalizedClient(fl.client.NumPyClient):
    def __init__(self):
        self.personal_layers = PersonalModel()

    def fit(self, parameters, config):
        # 更新全局層 + 個性化層
        pass
```

## 最佳實踐

1. **數據隱私**：始終在客戶端保留原始數據
2. **通信效率**：使用模型壓縮和量化減少傳輸
3. **魯棒性**：處理客戶端掉線和惡意更新
4. **公平性**：確保所有客戶端公平參與
5. **監控**：記錄訓練指標和系統性能

## 相關資源

- [官方文檔](https://flower.dev/docs/)
- [GitHub 倉庫](https://github.com/adap/flower)
- [論文集合](https://flower.dev/conf/flower-summit-2023)
- [教程和示例](https://flower.dev/docs/examples/)

## 與其他框架對比

| 特性 | Flower | TensorFlow Federated | PySyft |
|------|--------|---------------------|---------|
| 框架支持 | 全部 | TensorFlow | PyTorch 主導 |
| 易用性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 生產就緒 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 社區活躍度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 隱私保護 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 許可證

本示例代碼遵循 MIT 許可證。Flower 框架本身遵循 Apache 2.0 許可證。

## 貢獻

歡迎提交 Issue 和 Pull Request！

---

**注意**：這些示例僅供學習使用。在生產環境中部署聯邦學習系統時，請仔細評估隱私和安全需求。
