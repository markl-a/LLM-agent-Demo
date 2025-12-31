# PEFT (Parameter-Efficient Fine-Tuning) 框架

## 簡介

PEFT 是 HuggingFace 開發的參數高效微調庫，讓你能夠以極低的計算成本微調大型預訓練模型。PEFT 只訓練少量的額外參數，同時保持預訓練模型的大部分參數凍結，大幅降低訓練成本和存儲需求。

使用 PEFT，你可以在消費級 GPU 上微調數十億參數的大型模型，而無需昂貴的硬件設備。

## 核心特點

### 1. 多種高效微調方法

- **LoRA (Low-Rank Adaptation)**：在注意力層添加低秩矩陣，只訓練這些小矩陣
- **QLoRA**：結合 4-bit 量化的 LoRA，進一步降低顯存需求
- **Prefix Tuning**：在輸入序列前添加可訓練的前綴向量
- **P-Tuning**：使用可訓練的提示編碼器
- **Prompt Tuning**：只訓練軟提示（soft prompts）
- **IA3 (Infused Adapter by Inhibiting and Amplifying Inner Activations)**：通過縮放激活值進行微調
- **AdaLoRA**：自適應分配 LoRA 的秩

### 2. 極低的訓練成本

- **參數量**：通常只訓練 < 1% 的模型參數
- **顯存需求**：相比全量微調降低 50-90%
- **訓練速度**：更快的訓練和收斂
- **存儲空間**：適配器文件通常只有幾 MB

### 3. 易於使用

```python
from peft import LoraConfig, get_peft_model

# 配置 LoRA
config = LoraConfig(r=16, lora_alpha=32)

# 應用到模型
model = get_peft_model(model, config)

# 只訓練 0.1% 的參數！
model.print_trainable_parameters()
```

### 4. 靈活的模型管理

- **多適配器**：一個基礎模型可以加載不同的適配器
- **適配器切換**：輕鬆在不同任務間切換
- **適配器合併**：將適配器合併回基礎模型
- **適配器共享**：輕鬆分享和部署適配器

### 5. 與 HuggingFace 生態無縫整合

- 支持所有 Transformers 模型
- 兼容 Trainer 和 Pipeline
- 可上傳到 HuggingFace Hub
- 支持量化（8-bit、4-bit）

## LoRA 原理

LoRA (Low-Rank Adaptation) 是最流行的 PEFT 方法之一。

### 核心思想

在預訓練模型的權重矩陣旁邊，添加兩個小的低秩矩陣 A 和 B：

```
W' = W + BA

其中：
- W: 原始預訓練權重（凍結）
- B: 下投影矩陣（可訓練）
- A: 上投影矩陣（可訓練）
- r: 秩（遠小於原始維度）
```

### 優勢

1. **參數量極小**：如果 W 是 1024×1024，r=8，則只需訓練 1024×8 + 8×1024 = 16,384 個參數，相比原來的 1,048,576 個參數，減少了 98%
2. **推理無額外開銷**：可以將 BA 合併到 W 中，推理速度與原模型相同
3. **易於切換**：可以輕鬆加載不同的適配器

### QLoRA

QLoRA 結合了 LoRA 和量化技術：

1. 將基礎模型量化到 4-bit（NF4 格式）
2. 使用 LoRA 進行訓練
3. 訓練時使用 16-bit 計算以保持精度

**效果**：可以在單個 24GB GPU 上微調 65B 參數的模型！

## 安裝

```bash
# 基礎安裝
pip install peft

# 完整安裝（包含所有依賴）
pip install -r requirements.txt

# 從源碼安裝最新版
pip install git+https://github.com/huggingface/peft.git
```

## 快速開始

### 1. LoRA 基礎使用

```python
from transformers import AutoModelForCausalLM
from peft import LoraConfig, get_peft_model

# 加載基礎模型
model = AutoModelForCausalLM.from_pretrained("gpt2")

# 配置 LoRA
config = LoraConfig(
    r=16,                 # 秩
    lora_alpha=32,        # 縮放因子
    target_modules=["c_attn"],  # 要應用 LoRA 的模塊
    lora_dropout=0.1,     # dropout
    bias="none",
    task_type="CAUSAL_LM"
)

# 獲取 PEFT 模型
model = get_peft_model(model, config)

# 查看可訓練參數
model.print_trainable_parameters()
# 輸出: trainable params: 294,912 || all params: 124,734,720 || trainable%: 0.24%
```

### 2. 訓練和保存

```python
from transformers import Trainer, TrainingArguments

# 訓練參數
training_args = TrainingArguments(
    output_dir="./lora_model",
    num_train_epochs=3,
    per_device_train_batch_size=4,
)

# 訓練
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
)
trainer.train()

# 只保存適配器（幾 MB）
model.save_pretrained("./lora_adapter")
```

### 3. 加載和推理

```python
from peft import PeftModel

# 加載基礎模型
base_model = AutoModelForCausalLM.from_pretrained("gpt2")

# 加載適配器
model = PeftModel.from_pretrained(base_model, "./lora_adapter")

# 推理
outputs = model.generate(**inputs)
```

### 4. QLoRA 量化微調

```python
from transformers import BitsAndBytesConfig

# 4-bit 量化配置
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16
)

# 加載量化模型
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=bnb_config,
    device_map="auto"
)

# 應用 LoRA
model = get_peft_model(model, lora_config)
```

## 使用案例

### 案例 1：指令微調

在有限的計算資源下微調大型語言模型：

1. 使用 QLoRA 量化到 4-bit
2. 應用 LoRA 進行微調
3. 在單個消費級 GPU 上訓練 7B/13B 模型

### 案例 2：多任務適配器

為一個基礎模型創建多個任務特定的適配器：

1. 訓練翻譯適配器
2. 訓練摘要適配器
3. 訓練問答適配器
4. 根據任務動態切換適配器

### 案例 3：領域適應

快速將通用模型適應到特定領域：

1. 使用領域數據訓練 LoRA 適配器
2. 保持基礎模型的通用能力
3. 獲得領域特定的性能提升

### 案例 4：高效實驗

在研究中快速測試不同的假設：

1. 固定基礎模型
2. 訓練不同配置的適配器
3. 快速比較結果
4. 節省計算和存儲資源

## 主要組件

### PEFT 配置

- **LoraConfig**：LoRA 配置
- **PrefixTuningConfig**：前綴調優配置
- **PromptTuningConfig**：提示調優配置
- **PromptEncoderConfig**：P-Tuning 配置
- **IA3Config**：IA3 方法配置
- **AdaLoraConfig**：自適應 LoRA 配置

### PEFT 模型

- **PeftModel**：PEFT 模型包裝器
- **PeftModelForCausalLM**：因果語言模型的 PEFT
- **PeftModelForSeq2SeqLM**：序列到序列模型的 PEFT
- **PeftModelForSequenceClassification**：分類模型的 PEFT
- **PeftModelForTokenClassification**：標記分類的 PEFT

### 工具函數

- **get_peft_model()**：將 PEFT 應用到模型
- **prepare_model_for_kbit_training()**：準備量化模型進行訓練
- **set_peft_model_state_dict()**：設置 PEFT 模型狀態

## LoRA 超參數選擇

### r (秩)

- **較小 (4-8)**：參數更少，訓練更快，但表達能力有限
- **中等 (16-32)**：平衡性能和效率，推薦用於大多數任務
- **較大 (64-128)**：更強的表達能力，但參數量增加

### lora_alpha

- 通常設為 r 的 2 倍（如 r=16, alpha=32）
- 控制 LoRA 更新的縮放程度

### target_modules

- **注意力層**：通常針對 q_proj, k_proj, v_proj, o_proj
- **全連接層**：可以包含 FFN 層
- **all-linear**：應用到所有線性層（更多參數，更好性能）

### lora_dropout

- 通常設為 0.05-0.1
- 防止過擬合

## 性能優化

### 1. 使用量化

```python
# 4-bit 量化
load_in_4bit=True

# 8-bit 量化
load_in_8bit=True
```

### 2. 梯度檢查點

```python
model.gradient_checkpointing_enable()
```

### 3. 混合精度訓練

```python
training_args = TrainingArguments(
    fp16=True,  # 或 bf16=True
)
```

### 4. 選擇合適的 target_modules

```python
# 只訓練注意力層（更快）
target_modules=["q_proj", "v_proj"]

# 訓練所有線性層（更好性能）
target_modules="all-linear"
```

## 最佳實踐

1. **從小開始**：先用較小的 r 值測試，確認效果後再增加
2. **量化優先**：對於大模型，優先考慮 QLoRA
3. **目標模塊選擇**：從注意力層開始，如需要再擴展到 FFN
4. **學習率**：通常比全量微調高 1-2 倍（如 3e-4）
5. **監控訓練**：使用 print_trainable_parameters() 確認參數量
6. **適配器管理**：為不同版本的適配器使用清晰的命名
7. **合併推理**：推理時將適配器合併到基礎模型以提升速度

## 顯存需求對比

以 LLaMA-7B 為例：

| 方法 | 顯存需求 | 可訓練參數 |
|------|----------|------------|
| 全量微調 | ~28 GB | 7B (100%) |
| LoRA | ~14 GB | ~30M (0.4%) |
| QLoRA (8-bit) | ~9 GB | ~30M (0.4%) |
| QLoRA (4-bit) | ~5 GB | ~30M (0.4%) |

**結論**：QLoRA 可以在單個 24GB GPU 上訓練 65B 模型，在單個 8GB GPU 上訓練 7B 模型！

## 資源鏈接

- **官方文檔**：https://huggingface.co/docs/peft/
- **GitHub**：https://github.com/huggingface/peft
- **LoRA 論文**：https://arxiv.org/abs/2106.09685
- **QLoRA 論文**：https://arxiv.org/abs/2305.14314
- **示例代碼**：https://github.com/huggingface/peft/tree/main/examples

## 示例文件說明

本目錄包含 10 個完整的示例文件：

1. **01_快速開始.py** - PEFT 基礎入門
2. **02_LoRA基礎.py** - LoRA 完整使用指南
3. **03_QLoRA配置.py** - QLoRA 量化微調
4. **04_Prefix_Tuning.py** - 前綴調優方法
5. **05_P_Tuning.py** - P-Tuning 實現
6. **06_IA3方法.py** - IA3 微調技術
7. **07_多任務學習.py** - 多適配器管理
8. **08_模型合併.py** - 適配器合併技術
9. **09_推理優化.py** - 推理性能優化
10. **10_生產部署.py** - 生產環境最佳實踐

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 許可證

Apache License 2.0
