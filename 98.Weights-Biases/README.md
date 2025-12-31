# Weights & Biases - ML 實驗追蹤和可視化平台

## 框架簡介

Weights & Biases (W&B) 是業界領先的機器學習實驗追蹤、模型版本管理和可視化平台。它為 ML 團隊提供了一套完整的工具，用於追蹤實驗、可視化結果、協作開發和部署模型。

### 核心特點

- **📊 實驗追蹤**: 自動記錄模型訓練過程中的所有指標、超參數和系統資源
- **📈 實時可視化**: 即時查看訓練曲線、系統性能和自定義圖表
- **🔍 超參數掃描**: 智能化超參數優化，支持網格搜索、隨機搜索和貝葉斯優化
- **📦 模型版本管理**: 追蹤模型版本、血統關係和性能指標
- **🤖 LLM 監控**: 專門為大型語言模型設計的追蹤和評估工具
- **👥 團隊協作**: 共享實驗結果、報告和模型，促進團隊協作
- **📝 報告生成**: 自動生成包含圖表和分析的專業報告
- **🔄 CI/CD 整合**: 與持續集成和部署流程無縫整合

### 主要功能

#### 1. 實驗追蹤 (Experiment Tracking)
- 自動記錄訓練指標
- 超參數配置管理
- 系統資源監控（GPU、CPU、內存）
- 代碼版本和環境追蹤
- 自定義圖表和可視化

#### 2. 超參數掃描 (Sweeps)
- 多種搜索策略（網格、隨機、貝葉斯）
- 早停機制
- 並行實驗執行
- 自動化最佳配置選擇
- 可視化參數重要性

#### 3. 模型註冊表 (Model Registry)
- 集中管理模型版本
- 模型血統追蹤
- 性能對比和基準測試
- 模型部署狀態管理
- 自動化模型評估

#### 4. LLM 專用功能
- Prompt 追蹤和版本管理
- LLM 調用鏈可視化
- Token 使用統計和成本追蹤
- 輸入輸出樣本記錄
- 模型性能評估

#### 5. 報告和協作
- 交互式報告創建
- 嵌入式圖表和表格
- Markdown 支援
- 團隊共享和權限管理
- 評論和討論功能

## 安裝指南

### 基本安裝

```bash
# 使用 pip 安裝
pip install wandb

# 安裝完整依賴（包括深度學習框架）
pip install -r requirements.txt
```

### 環境配置

```bash
# 登錄到 W&B（首次使用需要）
wandb login

# 或通過環境變量設置 API Key
export WANDB_API_KEY="your-api-key-here"

# 設置項目和實體（可選）
export WANDB_PROJECT="my-project"
export WANDB_ENTITY="my-team"
```

### 離線模式

```bash
# 設置離線模式（無需網絡連接）
export WANDB_MODE=offline

# 或在代碼中設置
wandb.init(mode="offline")
```

## 快速開始

### 基本使用示例

```python
import wandb

# 初始化 W&B 運行
wandb.init(
    project="my-first-project",
    config={
        "learning_rate": 0.001,
        "epochs": 10,
        "batch_size": 32
    }
)

# 訓練循環
for epoch in range(wandb.config.epochs):
    # 訓練代碼...
    train_loss = 0.5  # 示例值

    # 記錄指標
    wandb.log({
        "epoch": epoch,
        "train_loss": train_loss
    })

# 完成運行
wandb.finish()
```

### PyTorch 整合

```python
import torch
import torch.nn as nn
import wandb

# 初始化
wandb.init(project="pytorch-demo")

# 訓練模型
model = nn.Linear(10, 1)
wandb.watch(model)  # 自動追蹤模型

# 訓練循環
for epoch in range(10):
    loss = train_step(model)
    wandb.log({"loss": loss})

# 保存模型
torch.save(model.state_dict(), "model.pth")
wandb.save("model.pth")
```

### TensorFlow/Keras 整合

```python
import tensorflow as tf
import wandb
from wandb.keras import WandbCallback

# 初始化
wandb.init(project="keras-demo")

# 構建模型
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(10, activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# 訓練（自動追蹤）
model.fit(
    x_train, y_train,
    validation_data=(x_val, y_val),
    epochs=10,
    callbacks=[WandbCallback()]
)
```

### Hugging Face Transformers 整合

```python
from transformers import Trainer, TrainingArguments
import wandb

# 初始化
wandb.init(project="transformers-demo")

# 訓練配置
training_args = TrainingArguments(
    output_dir="./results",
    report_to="wandb",  # 啟用 W&B 追蹤
    logging_steps=10,
)

# 訓練
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)

trainer.train()
```

## 使用場景

### 1. 深度學習實驗管理
- 追蹤不同架構的性能
- 對比不同訓練配置
- 記錄和可視化訓練過程
- 分析模型行為和異常

### 2. 超參數優化
- 自動化超參數搜索
- 多實驗並行運行
- 識別最佳配置
- 參數重要性分析

### 3. LLM 開發和監控
- Prompt 工程和版本管理
- LLM 調用追蹤
- 成本和性能監控
- 輸出質量評估

### 4. 模型生命週期管理
- 版本控制和血統追蹤
- 性能基準測試
- A/B 測試支援
- 部署狀態管理

### 5. 團隊協作和知識分享
- 實驗結果共享
- 最佳實踐文檔化
- 交互式報告
- 跨團隊學習

### 6. 生產監控
- 模型性能追蹤
- 數據漂移檢測
- 系統資源監控
- 告警和通知

## 核心概念

### 1. Run (運行)
單次實驗或訓練會話，包含配置、指標和輸出。

### 2. Project (項目)
組織相關實驗的容器，例如"圖像分類"或"語言模型"。

### 3. Config (配置)
實驗的超參數和設置，自動記錄和可視化。

### 4. Metrics (指標)
訓練過程中記錄的數值（損失、準確率等）。

### 5. Artifacts (工件)
模型檢查點、數據集、預測結果等文件。

### 6. Sweep (掃描)
自動化超參數優化實驗。

### 7. Table (表格)
結構化數據的記錄和可視化。

## 架構組件

### 1. 客戶端 SDK
- Python SDK（主要）
- JavaScript SDK
- Go SDK
- 命令行工具

### 2. 後端服務
- 數據存儲和管理
- 實時同步服務
- 可視化引擎
- 搜索和查詢 API

### 3. Web 應用
- 實驗儀表板
- 圖表可視化
- 報告編輯器
- 模型註冊表 UI

### 4. 整合生態
- PyTorch、TensorFlow、Keras
- Hugging Face Transformers
- Scikit-learn
- XGBoost、LightGBM
- Ray Tune、Optuna

## 定價方案

### 免費方案（Academic/Personal）
- 無限實驗
- 100 GB 存儲
- 個人使用
- 基本支援

### 團隊方案
- 從 $50/用戶/月起
- 無限存儲
- 團隊協作功能
- 優先支援

### 企業方案
- 自訂定價
- 私有部署選項
- 高級安全功能
- 專屬支援
- SLA 保證

### 學術方案
- 完全免費
- 為教育和研究機構
- 所有專業功能
- 社區支援

## 最佳實踐

### 1. 組織實驗
```python
# 使用有意義的項目和運行名稱
wandb.init(
    project="image-classification",
    name="resnet50-augmented-lr0.001",
    tags=["resnet", "augmentation", "baseline"]
)
```

### 2. 記錄豐富的元數據
```python
# 記錄配置、環境信息
wandb.config.update({
    "architecture": "ResNet50",
    "dataset": "ImageNet",
    "optimizer": "Adam",
    "git_commit": git_hash,
})
```

### 3. 使用表格記錄樣本
```python
# 記錄預測樣本
wandb.log({
    "predictions": wandb.Table(
        columns=["image", "prediction", "truth"],
        data=[[wandb.Image(img), pred, truth]]
    )
})
```

### 4. 模型檢查點管理
```python
# 保存和追蹤模型
artifact = wandb.Artifact("model", type="model")
artifact.add_file("model.pth")
wandb.log_artifact(artifact)
```

### 5. 早停和最佳模型選擇
```python
# 使用 W&B 回調實現早停
from wandb.keras import WandbCallback

callback = WandbCallback(
    save_model=True,
    monitor="val_loss",
    mode="min"
)
```

## 技術規格

- **語言**: Python 3.7+, JavaScript, Go
- **支援框架**: PyTorch, TensorFlow, Keras, JAX, Scikit-learn
- **許可證**: 專有軟件（提供免費方案）
- **GitHub**: https://github.com/wandb/wandb
- **文檔**: https://docs.wandb.ai
- **官網**: https://wandb.ai

## 社區與支援

- **Discord**: 活躍的開發者社區
- **論壇**: 社區討論和問答
- **YouTube**: 教程和最佳實踐視頻
- **博客**: 技術文章和案例研究
- **GitHub**: 開源示例和整合

## 與其他工具比較

| 功能 | W&B | MLflow | TensorBoard |
|------|-----|--------|-------------|
| 實驗追蹤 | ✅ 優秀 | ✅ 良好 | ✅ 基本 |
| 超參數掃描 | ✅ 內建 | ⚠️ 有限 | ❌ 無 |
| 模型註冊 | ✅ | ✅ | ❌ |
| LLM 支援 | ✅ 專門 | ✅ 基本 | ❌ |
| 團隊協作 | ✅ 優秀 | ⚠️ 有限 | ❌ |
| 報告生成 | ✅ 強大 | ❌ | ❌ |
| 雲端託管 | ✅ 官方 | ⚠️ 自建 | ⚠️ 自建 |
| 免費額度 | ✅ 慷慨 | ✅ 開源 | ✅ 開源 |

## 總結

Weights & Biases 是一個功能豐富、易於使用的 ML 實驗追蹤平台，特別適合：

- 需要強大可視化的 ML 團隊
- 進行大量超參數實驗的項目
- LLM 應用開發和監控
- 需要團隊協作的組織
- 重視實驗可重現性的研究

通過本目錄中的示例，你可以學習如何：
- 追蹤和可視化 ML 實驗
- 進行自動化超參數優化
- 管理模型版本和部署
- 監控 LLM 應用
- 創建專業的實驗報告
- 整合到現有工作流

開始探索示例文件，提升你的 ML 實驗效率！
