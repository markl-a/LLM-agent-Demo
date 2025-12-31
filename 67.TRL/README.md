# TRL (Transformer Reinforcement Learning) 框架

## 簡介

TRL 是 HuggingFace 開發的 Transformer 強化學習框架，專門用於訓練語言模型使用人類反饋進行強化學習（RLHF）。該框架提供了完整的工具鏈，從監督微調（SFT）到強化學習訓練（PPO、DPO、ORPO 等），使得訓練更符合人類偏好的語言模型變得簡單高效。

TRL 是構建類似 ChatGPT 等對話模型的核心技術，支持多種 RLHF 算法和訓練策略。

## 核心特點

### 1. 完整的 RLHF 訓練流程
- **監督微調（SFT）**：使用高質量對話數據進行初始訓練
- **獎勵模型訓練**：學習人類偏好，為生成結果打分
- **強化學習訓練**：使用 PPO、DPO、ORPO 等算法優化模型

### 2. 多種強化學習算法
- **PPO (Proximal Policy Optimization)**：經典的強化學習算法
- **DPO (Direct Preference Optimization)**：直接優化偏好，無需獎勵模型
- **ORPO (Odds Ratio Preference Optimization)**：結合 SFT 和偏好優化
- **ReAct**：推理行動框架
- **RLOO (Reinforcement Learning with Likelihood-free Optimization)**：新型優化方法

### 3. 參數高效訓練
- 完整支持 **LoRA** 和 **QLoRA**
- 支持 **8-bit** 和 **4-bit** 量化訓練
- 大幅降低顯存需求，支持在消費級 GPU 上訓練大模型

### 4. 靈活的配置系統
- 豐富的訓練配置選項
- 支持分布式訓練
- 自動混合精度訓練
- 梯度累積和檢查點

### 5. 與 HuggingFace 生態整合
- 無縫整合 Transformers
- 支持 PEFT（參數高效微調）
- 兼容 Datasets 和 Accelerate

## RLHF 原理

### 訓練流程

```
1. 監督微調（SFT）
   ↓
   使用高質量對話數據訓練基礎模型

2. 獎勵模型訓練（Reward Modeling）
   ↓
   訓練模型學習人類偏好

3. 強化學習訓練（RL Training）
   ↓
   使用 PPO/DPO 等算法優化策略

4. 模型評估與迭代
   ↓
   評估模型表現，持續改進
```

### 核心概念

1. **監督微調（SFT）**
   - 使用標註數據訓練模型基礎能力
   - 學習任務格式和基本回答方式

2. **獎勵模型（Reward Model）**
   - 訓練一個模型來預測人類偏好
   - 為生成的回答打分

3. **強化學習（RL）**
   - PPO：通過獎勵信號優化生成策略
   - DPO：直接從偏好數據學習，無需獎勵模型
   - ORPO：同時進行 SFT 和偏好優化

## 安裝

```bash
# 基礎安裝
pip install trl

# 完整安裝（包含所有依賴）
pip install -r requirements.txt

# 從源碼安裝最新版
pip install git+https://github.com/huggingface/trl.git
```

## 快速開始

### 1. 監督微調（SFT）

```python
from trl import SFTTrainer
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset

# 加載模型和數據
model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")
dataset = load_dataset("timdettmers/openassistant-guanaco")

# 訓練
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset["train"],
    dataset_text_field="text",
    max_seq_length=512,
)
trainer.train()
```

### 2. DPO 訓練

```python
from trl import DPOTrainer, DPOConfig

config = DPOConfig(
    output_dir="dpo_model",
    per_device_train_batch_size=4,
    learning_rate=5e-5,
)

trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,
    config=config,
    train_dataset=dataset,
    tokenizer=tokenizer,
)
trainer.train()
```

### 3. PPO 訓練

```python
from trl import PPOTrainer, PPOConfig, AutoModelForCausalLMWithValueHead

config = PPOConfig(
    model_name="gpt2",
    learning_rate=1.41e-5,
    batch_size=128,
)

model = AutoModelForCausalLMWithValueHead.from_pretrained(config.model_name)
trainer = PPOTrainer(config=config, model=model, tokenizer=tokenizer)
```

## 使用案例

### 案例 1：對話模型微調

使用 TRL 訓練一個類似 ChatGPT 的對話模型：

1. **SFT 階段**：使用 OpenAssistant、Dolly 等對話數據集
2. **獎勵模型**：使用人類偏好數據訓練獎勵模型
3. **PPO 訓練**：使用獎勵模型優化對話質量

### 案例 2：代碼生成模型

訓練專門的代碼生成助手：

1. 使用 CodeAlpaca 數據進行 SFT
2. 使用代碼質量評分作為獎勵
3. DPO 訓練優化代碼質量

### 案例 3：摘要生成

優化文本摘要模型：

1. SFT：學習基本摘要能力
2. 獎勵模型：評估摘要質量（ROUGE、相關性等）
3. RL 訓練：優化摘要品質

### 案例 4：參數高效微調

在消費級 GPU 上訓練大模型：

1. 使用 QLoRA 進行 4-bit 量化
2. 只訓練 LoRA 參數（<1% 參數量）
3. 大幅降低顯存需求

## 主要組件

### 訓練器（Trainers）

- **SFTTrainer**：監督微調訓練器
- **RewardTrainer**：獎勵模型訓練器
- **PPOTrainer**：PPO 算法訓練器
- **DPOTrainer**：DPO 算法訓練器
- **ORPOTrainer**：ORPO 算法訓練器

### 配置（Configs）

- **SFTConfig**：SFT 訓練配置
- **RewardConfig**：獎勵模型配置
- **PPOConfig**：PPO 訓練配置
- **DPOConfig**：DPO 訓練配置
- **ORPOConfig**：ORPO 訓練配置

### 模型包裝器

- **AutoModelForCausalLMWithValueHead**：帶價值頭的因果語言模型
- **AutoModelForSeq2SeqLMWithValueHead**：帶價值頭的序列到序列模型

## 性能優化

### 1. 使用 LoRA/QLoRA

```python
from peft import LoraConfig

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)
```

### 2. 梯度累積

```python
training_args = TrainingArguments(
    gradient_accumulation_steps=4,
    per_device_train_batch_size=2,
)
```

### 3. 混合精度訓練

```python
training_args = TrainingArguments(
    fp16=True,  # 或 bf16=True
)
```

### 4. 梯度檢查點

```python
training_args = TrainingArguments(
    gradient_checkpointing=True,
)
```

## 最佳實踐

1. **數據質量**：高質量的訓練數據是成功的關鍵
2. **循序漸進**：按照 SFT → RM → RL 的順序訓練
3. **超參數調優**：learning_rate、batch_size 對結果影響很大
4. **定期評估**：使用多種指標評估模型表現
5. **顯存管理**：合理使用 LoRA、量化等技術
6. **分布式訓練**：大規模訓練使用多 GPU/多節點

## 資源鏈接

- **官方文檔**：https://huggingface.co/docs/trl/
- **GitHub**：https://github.com/huggingface/trl
- **示例代碼**：https://github.com/huggingface/trl/tree/main/examples
- **論文**：
  - PPO: https://arxiv.org/abs/1707.06347
  - InstructGPT: https://arxiv.org/abs/2203.02155
  - DPO: https://arxiv.org/abs/2305.18290

## 示例文件說明

本目錄包含 10 個完整的示例文件：

1. **01_快速開始.py** - TRL 基礎入門
2. **02_SFT訓練.py** - 監督微調完整流程
3. **03_獎勵模型.py** - 獎勵模型訓練
4. **04_PPO訓練.py** - PPO 算法實現
5. **05_DPO訓練.py** - DPO 直接偏好優化
6. **06_ORPO訓練.py** - ORPO 方法
7. **07_LoRA整合.py** - 參數高效訓練
8. **08_數據處理.py** - 數據準備與處理
9. **09_評估指標.py** - 模型評估方法
10. **10_最佳實踐.py** - 生產環境建議

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 許可證

Apache License 2.0
