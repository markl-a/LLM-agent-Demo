# DeepSpeed - 分佈式訓練框架

## 簡介

DeepSpeed 是微軟開發的深度學習優化庫，專門用於大規模分佈式訓練。它通過 ZeRO (Zero Redundancy Optimizer) 等創新技術，能夠訓練擁有數千億參數的超大型模型，同時大幅降低訓練成本和時間。

DeepSpeed 是目前訓練大型語言模型（如 GPT、BLOOM、Megatron）的主流框架之一。

## 核心特點

### 1. ZeRO 優化技術

DeepSpeed 的核心創新 - 零冗餘優化器（Zero Redundancy Optimizer）：

- **ZeRO Stage 1**：優化器狀態分片，減少 4x 顯存
- **ZeRO Stage 2**：+ 梯度分片，減少 8x 顯存
- **ZeRO Stage 3**：+ 參數分片，減少 Nd 顯存（N 是 GPU 數量）
- **ZeRO-Infinity**：利用 NVMe/CPU 訓練無限大模型
- **ZeRO-Offload**：卸載到 CPU，單 GPU 訓練大模型

### 2. 混合精度訓練

- 自動混合精度（FP16、BF16）
- 動態損失縮放
- 梯度累積
- 最高 3x 訓練加速

### 3. 模型並行

- **流水線並行（Pipeline Parallelism）**：層間並行
- **張量並行（Tensor Parallelism）**：層內並行
- **數據並行（Data Parallelism）**：批次並行
- **3D 並行**：結合所有並行策略

### 4. 高效通信

- 1-bit Adam：通信壓縮
- 梯度壓縮
- 通信-計算重疊
- NCCL 優化

### 5. 推理優化

- DeepSpeed Inference
- Kernel 融合
- 量化支持
- 多 GPU 推理加速

## ZeRO 原理

### ZeRO 的創新

傳統數據並行訓練中，每個 GPU 都保存：
- 模型參數
- 梯度
- 優化器狀態

這導致大量**冗餘**，ZeRO 通過分片消除冗餘：

```
傳統數據並行（4 GPU，7.5B 模型）：
┌──────────┬──────────┬──────────┬──────────┐
│ GPU 0    │ GPU 1    │ GPU 2    │ GPU 3    │
│ 參數 7.5B│ 參數 7.5B│ 參數 7.5B│ 參數 7.5B│  30B 參數
│ 梯度 7.5B│ 梯度 7.5B│ 梯度 7.5B│ 梯度 7.5B│  30B 梯度
│ 優化器15B│ 優化器15B│ 優化器15B│ 優化器15B│  60B 優化器
│ 總: 120GB 顯存                            │
└──────────┴──────────┴──────────┴──────────┘

ZeRO Stage 3（4 GPU，7.5B 模型）：
┌──────────┬──────────┬──────────┬──────────┐
│ GPU 0    │ GPU 1    │ GPU 2    │ GPU 3    │
│ 參數 1.9B│ 參數 1.9B│ 參數 1.9B│ 參數 1.9B│  7.5B 參數（分片）
│ 梯度 1.9B│ 梯度 1.9B│ 梯度 1.9B│ 梯度 1.9B│  7.5B 梯度（分片）
│ 優化器3.8B│優化器3.8B│優化器3.8B│優化器3.8B│  15B 優化器（分片）
│ 總: 30GB 顯存（4x 減少）                  │
└──────────┴──────────┴──────────┴──────────┘
```

### ZeRO 各階段對比

| Stage | 優化內容 | 顯存節省 | 通信開銷 | 適用場景 |
|-------|----------|----------|----------|----------|
| Stage 1 | 優化器狀態分片 | 4x | 低 | 中小型模型 |
| Stage 2 | + 梯度分片 | 8x | 中 | 大型模型 |
| Stage 3 | + 參數分片 | Nd (N=GPU數) | 高 | 超大模型 |
| ZeRO-Offload | + CPU卸載 | 10x+ | 高 | 單GPU大模型 |
| ZeRO-Infinity | + NVMe | 無限 | 很高 | 極大模型 |

## 安裝

```bash
# 基礎安裝
pip install deepspeed

# 完整安裝（包含所有依賴）
pip install -r requirements.txt

# 從源碼安裝最新版
git clone https://github.com/microsoft/DeepSpeed.git
cd DeepSpeed
pip install .

# 驗證安裝
ds_report
```

## 快速開始

### 1. 基礎使用

```python
import torch
import deepspeed
from transformers import AutoModelForCausalLM, AutoTokenizer

# 加載模型
model = AutoModelForCausalLM.from_pretrained("gpt2")

# DeepSpeed 配置
ds_config = {
    "train_batch_size": 16,
    "gradient_accumulation_steps": 1,
    "fp16": {
        "enabled": True
    },
    "zero_optimization": {
        "stage": 2
    }
}

# 初始化 DeepSpeed
model_engine, optimizer, _, _ = deepspeed.initialize(
    model=model,
    config=ds_config
)

# 訓練
for batch in dataloader:
    outputs = model_engine(batch)
    loss = outputs.loss
    model_engine.backward(loss)
    model_engine.step()
```

### 2. ZeRO Stage 3 訓練

```python
ds_config = {
    "train_batch_size": 32,
    "fp16": {"enabled": True},
    "zero_optimization": {
        "stage": 3,
        "offload_param": {
            "device": "cpu",
            "pin_memory": True
        },
        "offload_optimizer": {
            "device": "cpu",
            "pin_memory": True
        }
    }
}

# 可以訓練更大的模型
model_engine, _, _, _ = deepspeed.initialize(
    model=large_model,
    config=ds_config
)
```

### 3. 命令行啟動

```bash
# 單機多 GPU
deepspeed --num_gpus=4 train.py --deepspeed ds_config.json

# 多機訓練
deepspeed --num_nodes=2 --num_gpus=8 train.py --deepspeed ds_config.json

# 使用 hostfile
deepspeed --hostfile=hostfile train.py --deepspeed ds_config.json
```

## 顯存節省對比

以 GPT-3 175B 為例：

| 方法 | 顯存需求 | GPU 數量 | 訓練時間 |
|------|----------|----------|----------|
| 傳統訓練 | 不可行 | - | - |
| 數據並行 | ~700GB | ~90 GPU | 基準 |
| ZeRO-2 | ~350GB | ~45 GPU | 0.9x |
| ZeRO-3 | ~175GB | ~23 GPU | 0.85x |
| ZeRO-3 + CPU Offload | ~88GB | ~12 GPU | 0.7x |

## 使用案例

### 案例 1：大型語言模型預訓練

訓練 GPT 類模型：

```python
# 使用 ZeRO Stage 3 + Offload
ds_config = {
    "zero_optimization": {
        "stage": 3,
        "offload_optimizer": {"device": "cpu"},
        "offload_param": {"device": "cpu"},
    },
    "fp16": {"enabled": True},
    "train_batch_size": 128,
    "gradient_accumulation_steps": 8,
}

# 可以在有限 GPU 上訓練數十億參數模型
```

### 案例 2：微調大型模型

結合 HuggingFace Transformers：

```python
from transformers import Trainer, TrainingArguments

training_args = TrainingArguments(
    output_dir="./output",
    deepspeed="./ds_config.json",  # DeepSpeed 配置
    fp16=True,
    per_device_train_batch_size=4,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
)

trainer.train()
```

### 案例 3：推理加速

使用 DeepSpeed Inference：

```python
import deepspeed

# 優化推理
model = deepspeed.init_inference(
    model,
    mp_size=4,  # 模型並行
    dtype=torch.half,
    replace_with_kernel_inject=True  # Kernel 融合
)

# 推理速度提升 2-10x
outputs = model.generate(**inputs)
```

## 主要配置選項

### ZeRO 配置

```json
{
  "zero_optimization": {
    "stage": 3,
    "reduce_bucket_size": 5e8,
    "allgather_bucket_size": 5e8,
    "overlap_comm": true,
    "contiguous_gradients": true,
    "offload_optimizer": {
      "device": "cpu",
      "pin_memory": true
    },
    "offload_param": {
      "device": "cpu",
      "pin_memory": true
    }
  }
}
```

### 混合精度配置

```json
{
  "fp16": {
    "enabled": true,
    "loss_scale": 0,
    "initial_scale_power": 16,
    "loss_scale_window": 1000
  }
}
```

### 優化器配置

```json
{
  "optimizer": {
    "type": "AdamW",
    "params": {
      "lr": 3e-5,
      "betas": [0.9, 0.999],
      "eps": 1e-8,
      "weight_decay": 0.01
    }
  }
}
```

## 性能優化

### 1. 通信優化

- 使用 `overlap_comm` 重疊通信和計算
- 調整 `reduce_bucket_size` 和 `allgather_bucket_size`
- 啟用 `contiguous_gradients`

### 2. 內存優化

- 啟用 gradient checkpointing
- 使用 CPU/NVMe offload
- 調整 batch size 和 accumulation steps

### 3. 計算優化

- 使用混合精度訓練
- 啟用 kernel 融合
- 優化數據加載

## 最佳實踐

1. **選擇合適的 ZeRO Stage**：
   - Stage 1: 顯存充足，追求速度
   - Stage 2: 平衡顯存和速度
   - Stage 3: 顯存受限，大模型

2. **批次大小調優**：
   - 使用盡可能大的 batch size
   - 通過 gradient accumulation 增大有效 batch size

3. **Offload 策略**：
   - 優先 offload 優化器（影響較小）
   - 再考慮 offload 參數
   - 使用 NVMe 處理超大模型

4. **監控和調試**：
   - 使用 `--profile` 分析性能
   - 監控 GPU 利用率
   - 檢查通信開銷

5. **多機訓練**：
   - 使用高速網絡（InfiniBand）
   - 優化網絡拓撲
   - 調整通信參數

## 資源鏈接

- **官方文檔**：https://www.deepspeed.ai/
- **GitHub**：https://github.com/microsoft/DeepSpeed
- **教程**：https://www.deepspeed.ai/tutorials/
- **論文**：
  - ZeRO: https://arxiv.org/abs/1910.02054
  - ZeRO-Offload: https://arxiv.org/abs/2101.06840
  - ZeRO-Infinity: https://arxiv.org/abs/2104.07857

## 示例文件說明

本目錄包含 10 個完整的示例文件：

1. **01_快速開始.py** - DeepSpeed 基礎入門
2. **02_ZeRO優化.py** - ZeRO 各階段使用
3. **03_混合精度.py** - FP16/BF16 訓練
4. **04_梯度累積.py** - 大批次訓練技巧
5. **05_模型並行.py** - 模型並行策略
6. **06_流水線並行.py** - Pipeline 並行
7. **07_推理優化.py** - DeepSpeed Inference
8. **08_DeepSpeed_Chat.py** - RLHF 訓練
9. **09_配置優化.py** - 配置調優指南
10. **10_多節點訓練.py** - 分佈式訓練實踐

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 許可證

Apache License 2.0
