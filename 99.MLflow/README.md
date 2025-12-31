# MLflow - 開源 ML 生命週期管理平台

## 框架簡介

MLflow 是一個開源的機器學習生命週期管理平台，由 Databricks 開發。它為 ML 工程師和數據科學家提供了一套完整的工具，用於管理 ML 項目的整個生命週期，從實驗追蹤到模型部署。

### 核心特點

- **🔬 實驗追蹤 (Tracking)**: 記錄和查詢實驗參數、代碼版本、指標和輸出
- **📦 項目 (Projects)**: 可重現的 ML 代碼打包格式
- **🗂️ 模型註冊表 (Model Registry)**: 集中管理模型版本、狀態和部署
- **🚀 模型部署 (Models)**: 多種部署格式，支持各種推理平台
- **🤖 LLM 支援**: 專門為大型語言模型設計的追蹤和評估功能
- **🔄 開源自由**: Apache 2.0 許可證，完全免費使用
- **🌐 多語言支援**: Python, R, Java, REST API
- **📊 豐富的 UI**: 直觀的網頁界面查看實驗和模型

### 四大核心組件

#### 1. MLflow Tracking
- 記錄實驗參數和指標
- 追蹤代碼版本和依賴
- 存儲和可視化輸出文件
- 比較多次運行
- 本地或遠程追蹤服務器

#### 2. MLflow Projects
- 可重現的運行格式
- 標準化項目結構
- 環境管理（Conda/Docker）
- 參數化執行
- 與追蹤自動整合

#### 3. MLflow Models
- 統一的模型打包格式
- 多種"flavors"（PyTorch、TensorFlow、Scikit-learn等）
- 自動生成推理API
- 部署到多個平台（Kubernetes、AWS SageMaker等）
- 模型簽名和輸入驗證

#### 4. MLflow Model Registry
- 集中存儲模型版本
- 模型生命週期管理
- 版本轉換（Staging → Production）
- 註釋和標籤
- 協作和審批工作流

## 安裝指南

### 基本安裝

```bash
# 使用 pip 安裝
pip install mlflow

# 安裝完整依賴（包括深度學習框架）
pip install -r requirements.txt
```

### 啟動 MLflow UI

```bash
# 啟動追蹤服務器
mlflow ui

# 訪問 http://localhost:5000

# 指定端口和後端存儲
mlflow server \
    --backend-store-uri sqlite:///mlflow.db \
    --default-artifact-root ./mlruns \
    --host 0.0.0.0 \
    --port 5000
```

### Docker 部署

```bash
# 使用 Docker Compose
docker-compose up -d

# 或使用官方鏡像
docker run -p 5000:5000 \
    -v $(pwd)/mlruns:/mlruns \
    ghcr.io/mlflow/mlflow:latest \
    mlflow server --host 0.0.0.0
```

## 快速開始

### 基本實驗追蹤

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

# 開始運行
with mlflow.start_run():
    # 記錄參數
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 5)

    # 訓練模型
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    clf = RandomForestClassifier(n_estimators=100, max_depth=5)
    clf.fit(X_train, y_train)

    # 記錄指標
    accuracy = clf.score(X_test, y_test)
    mlflow.log_metric("accuracy", accuracy)

    # 記錄模型
    mlflow.sklearn.log_model(clf, "model")

    print(f"模型準確率: {accuracy:.2%}")
```

### PyTorch 整合

```python
import mlflow.pytorch
import torch
import torch.nn as nn

# 定義模型
model = nn.Sequential(
    nn.Linear(10, 50),
    nn.ReLU(),
    nn.Linear(50, 1)
)

# 自動記錄
mlflow.pytorch.autolog()

# 訓練循環
with mlflow.start_run():
    optimizer = torch.optim.Adam(model.parameters())
    criterion = nn.MSELoss()

    for epoch in range(100):
        # 訓練代碼...
        pass

    # MLflow 自動記錄參數、指標和模型
```

### 模型註冊和部署

```python
import mlflow

# 註冊模型
with mlflow.start_run():
    # 訓練和記錄模型
    mlflow.sklearn.log_model(
        clf,
        "model",
        registered_model_name="iris-classifier"
    )

# 載入模型
model_uri = "models:/iris-classifier/Production"
model = mlflow.pyfunc.load_model(model_uri)

# 推理
predictions = model.predict(X_test)
```

### LLM 追蹤

```python
import mlflow
from transformers import pipeline

# 啟用 LLM 追蹤
mlflow.llm.autolog()

# 使用 LLM
generator = pipeline('text-generation', model='gpt2')

with mlflow.start_run():
    prompt = "機器學習是"
    output = generator(prompt, max_length=50)

    # MLflow 自動記錄 prompt、輸出、token 使用等
    mlflow.log_param("prompt", prompt)
    mlflow.log_param("max_length", 50)
```

## 使用場景

### 1. 實驗管理
- 追蹤超參數調優實驗
- 比較不同模型架構
- 記錄訓練曲線和指標
- 管理實驗數據和工件

### 2. 模型版本控制
- 集中管理模型版本
- 追蹤模型血統
- 管理模型生命週期
- 模型性能對比

### 3. 可重現性
- 標準化項目結構
- 環境和依賴管理
- 代碼版本追蹤
- 參數化運行

### 4. 模型部署
- 統一的部署接口
- 多平台支援
- A/B 測試支援
- 模型服務監控

### 5. 團隊協作
- 共享實驗結果
- 模型審批流程
- 註釋和文檔
- 角色和權限管理

### 6. LLM 開發
- Prompt 追蹤
- Token 使用監控
- 生成質量評估
- 微調實驗管理

## 核心概念

### 實驗 (Experiment)
組織相關運行的容器，例如"圖像分類"或"價格預測"。

### 運行 (Run)
單次執行，包含參數、指標、標籤和工件。

### 參數 (Parameters)
鍵值對，記錄運行的輸入（超參數、配置等）。

### 指標 (Metrics)
數值，隨時間變化，如損失、準確率。

### 工件 (Artifacts)
輸出文件，如模型、圖像、數據文件。

### 標籤 (Tags)
鍵值對元數據，用於組織和搜索運行。

### 模型 (Model)
打包的 ML 模型，包含推理代碼和依賴。

## 架構組件

### 1. 追蹤服務器
- REST API 服務
- 後端存儲（FileStore、SQLAlchemy）
- 工件存儲（本地、S3、Azure Blob等）
- Web UI

### 2. 客戶端庫
- Python SDK（主要）
- R API
- Java API
- REST API

### 3. 模型註冊表
- 模型版本管理
- 生命週期狀態
- 註釋和標籤
- Webhooks

### 4. 部署工具
- MLflow Models CLI
- Docker 容器生成
- 雲平台部署（AWS、Azure、GCP）
- Kubernetes 整合

## 存儲後端選項

### 後端存儲（元數據）
- **FileStore**: 本地文件系統（默認）
- **SQLAlchemy**: PostgreSQL、MySQL、SQLite
- **REST**: 遠程追蹤服務器

### 工件存儲
- **本地文件系統**
- **Amazon S3**
- **Azure Blob Storage**
- **Google Cloud Storage**
- **HDFS**
- **SFTP**

## 與其他工具比較

| 功能 | MLflow | W&B | TensorBoard |
|------|--------|-----|-------------|
| 開源 | ✅ Apache 2.0 | ⚠️ 部分開源 | ✅ Apache 2.0 |
| 實驗追蹤 | ✅ 優秀 | ✅ 優秀 | ✅ 基本 |
| 模型註冊表 | ✅ 完整 | ✅ | ❌ |
| 模型部署 | ✅ 多平台 | ⚠️ 有限 | ❌ |
| 項目打包 | ✅ | ❌ | ❌ |
| LLM 支援 | ✅ | ✅ | ❌ |
| 自託管 | ✅ 簡單 | ⚠️ 複雜 | ✅ |
| 雲託管 | ⚠️ Databricks | ✅ 官方 | ❌ |
| 超參數掃描 | ⚠️ 基本 | ✅ 強大 | ❌ |

## 最佳實踐

### 1. 組織實驗
```python
# 使用有意義的實驗名稱
mlflow.set_experiment("image-classification-resnet")

# 使用標籤組織運行
with mlflow.start_run():
    mlflow.set_tag("model_type", "resnet50")
    mlflow.set_tag("dataset", "imagenet")
    mlflow.set_tag("environment", "production")
```

### 2. 記錄完整信息
```python
with mlflow.start_run():
    # 記錄所有超參數
    mlflow.log_params({
        "learning_rate": 0.001,
        "batch_size": 32,
        "optimizer": "adam",
        "epochs": 50
    })

    # 記錄環境信息
    mlflow.log_param("python_version", "3.10")
    mlflow.log_param("cuda_version", "11.8")

    # 記錄指標歷史
    for epoch in range(50):
        mlflow.log_metric("train_loss", loss, step=epoch)
```

### 3. 使用自動記錄
```python
# PyTorch 自動記錄
import mlflow.pytorch
mlflow.pytorch.autolog()

# Scikit-learn 自動記錄
import mlflow.sklearn
mlflow.sklearn.autolog()

# Transformers 自動記錄
import mlflow.transformers
mlflow.transformers.autolog()
```

### 4. 模型簽名
```python
from mlflow.models.signature import infer_signature

# 推斷模型簽名
signature = infer_signature(X_train, model.predict(X_train))

# 記錄帶簽名的模型
mlflow.sklearn.log_model(
    model,
    "model",
    signature=signature
)
```

### 5. 使用模型註冊表
```python
# 註冊模型
mlflow.register_model(
    "runs:/abc123/model",
    "production-model"
)

# 轉換模型階段
client = mlflow.tracking.MlflowClient()
client.transition_model_version_stage(
    name="production-model",
    version=1,
    stage="Production"
)
```

## 技術規格

- **語言**: Python 3.8+, R 3.6+, Java
- **許可證**: Apache License 2.0
- **GitHub**: https://github.com/mlflow/mlflow
- **文檔**: https://mlflow.org/docs/latest/index.html
- **官網**: https://mlflow.org

## 社區與支援

- **Slack**: 活躍的開發者社區
- **GitHub Issues**: 問題追蹤和功能請求
- **Stack Overflow**: 標籤 `mlflow`
- **郵件列表**: dev@mlflow.apache.org
- **會議**: MLflow 社區會議

## 生態系統整合

### ML 框架
- Scikit-learn
- PyTorch
- TensorFlow / Keras
- XGBoost / LightGBM
- Hugging Face Transformers

### 雲平台
- AWS SageMaker
- Azure ML
- Google Cloud AI Platform
- Databricks

### 部署平台
- Kubernetes
- Docker
- AWS Lambda
- Azure Functions

### 其他工具
- Apache Spark
- Airflow
- Kubeflow
- DVC

## 總結

MLflow 是一個強大而靈活的 ML 生命週期管理平台，特別適合：

- 需要端到端 ML 工作流管理的團隊
- 重視開源和可移植性的組織
- 需要統一模型部署接口的項目
- 進行大量實驗的數據科學團隊
- 需要嚴格模型治理的企業

通過本目錄中的示例，你可以學習如何：
- 追蹤和管理 ML 實驗
- 註冊和部署模型
- 構建可重現的 ML 流水線
- 追蹤 LLM 應用
- 整合到生產環境

開始探索示例文件，掌握 MLflow 的強大功能！
