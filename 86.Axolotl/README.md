# Axolotl - 簡化 LLM 微調的框架

## 簡介

Axolotl 是一個專為簡化大型語言模型（LLM）微調而設計的開源框架。它提供了一個統一的配置驅動介面，支持各種微調技術，包括 LoRA、QLoRA、全量微調等。Axolotl 讓研究人員和開發者能夠輕鬆地微調各種開源模型，而無需深入了解底層實現細節。

Axolotl 整合了 HuggingFace Transformers、PEFT、DeepSpeed 等主流框架，提供了開箱即用的訓練配置、數據處理管道和評估工具。它特別適合快速實驗不同的微調策略、在有限資源下訓練大模型，以及構建定制化的 AI 應用。

## 核心特點

### 1. 配置驅動的訓練
- **YAML 配置**: 使用簡單的 YAML 文件定義訓練參數
- **預設模板**: 提供多種預設配置模板
- **靈活擴展**: 輕鬆自定義配置項
- **版本控制**: 配置文件易於追蹤和管理

### 2. 多種微調技術
- **LoRA (Low-Rank Adaptation)**: 低秩適應，參數高效
- **QLoRA**: 量化 LoRA，進一步減少內存使用
- **全量微調**: 完整模型參數訓練
- **Adapter**: 輕量級適配器訓練
- **Prefix Tuning**: 前綴調優
- **P-Tuning**: 提示詞調優

### 3. 廣泛的模型支持
- **LLaMA/LLaMA-2/LLaMA-3**: Meta 的開源模型
- **Mistral/Mixtral**: Mistral AI 的模型
- **Falcon**: TII 的 Falcon 系列
- **MPT**: MosaicML 的 MPT 模型
- **GPT-NeoX**: EleutherAI 的模型
- **Phi**: Microsoft 的 Phi 系列
- **Qwen**: 阿里雲的通義千問
- **ChatGLM**: 智譜 AI 的模型

### 4. 數據處理
- **多種格式**: 支持 JSON、JSONL、CSV、Parquet
- **數據轉換**: 自動格式轉換和預處理
- **提示詞模板**: 內建多種對話模板
- **數據驗證**: 自動檢查數據格式
- **採樣策略**: 支持過採樣、欠採樣等

### 5. 高效訓練
- **混合精度**: FP16、BF16 訓練
- **梯度累積**: 模擬大批次訓練
- **梯度檢查點**: 減少內存使用
- **DeepSpeed**: 整合 DeepSpeed 加速
- **多 GPU**: 支持 DDP、FSDP
- **Flash Attention**: 加速注意力計算

### 6. 評估與監控
- **內建指標**: Perplexity、Accuracy 等
- **自定義評估**: 支持自定義評估函數
- **TensorBoard**: 訓練過程可視化
- **Weights & Biases**: 實驗追蹤整合
- **MLflow**: 模型版本管理

## 安裝

### 基本安裝

```bash
pip install axolotl
```

### 從源碼安裝（推薦）

```bash
git clone https://github.com/OpenAccess-AI-Collective/axolotl
cd axolotl
pip install -e .
```

### 使用 Docker

```bash
docker pull winglian/axolotl:main-latest
docker run --gpus all -v $(pwd):/workspace winglian/axolotl:main-latest
```

### 安裝依賴

```bash
pip install -r requirements.txt
```

## 系統要求

### 最小配置（LoRA 微調）
- **GPU**: NVIDIA GPU，至少 8GB VRAM（如 RTX 3060）
- **內存**: 16GB RAM
- **硬碟**: 50GB 可用空間
- **CUDA**: 11.8+
- **Python**: 3.9+

### 推薦配置（全量微調）
- **GPU**: NVIDIA A100 40GB/80GB 或 H100
- **內存**: 64GB+ RAM
- **硬碟**: SSD 存儲，至少 500GB
- **多 GPU**: 2-8 張 GPU
- **CUDA**: 12.1+

### 雲端選項
- **Google Colab**: 免費 GPU（受限）
- **Vast.ai**: 按小時付費 GPU
- **Lambda Labs**: 雲端 GPU 實例
- **RunPod**: 容器化 GPU 服務

## 核心概念

### 配置文件結構

Axolotl 使用 YAML 配置文件來定義訓練過程：

```yaml
# 基礎模型配置
base_model: meta-llama/Llama-2-7b-hf
model_type: LlamaForCausalLM
tokenizer_type: LlamaTokenizer

# LoRA 配置
adapter: lora
lora_r: 8
lora_alpha: 16
lora_dropout: 0.05
lora_target_modules:
  - q_proj
  - v_proj

# 數據配置
datasets:
  - path: data/train.jsonl
    type: alpaca

# 訓練配置
sequence_len: 2048
batch_size: 4
micro_batch_size: 1
num_epochs: 3
learning_rate: 0.0002
```

### 數據格式

**Alpaca 格式:**
```json
{
  "instruction": "寫一首關於春天的詩",
  "input": "",
  "output": "春風拂面暖，花開滿山園..."
}
```

**Chat 格式:**
```json
{
  "conversations": [
    {"from": "human", "value": "你好"},
    {"from": "gpt", "value": "你好！有什麼我可以幫助你的嗎？"}
  ]
}
```

### 微調技術對比

| 技術 | 參數量 | 內存使用 | 訓練速度 | 效果 |
|-----|--------|----------|----------|------|
| 全量微調 | 100% | 極高 | 慢 | 最佳 |
| LoRA | 0.1-1% | 低 | 快 | 優秀 |
| QLoRA | 0.1-1% | 極低 | 中等 | 良好 |
| Adapter | 2-4% | 低 | 快 | 良好 |
| Prefix Tuning | <0.1% | 極低 | 極快 | 中等 |

## 使用案例

### 1. 指令微調
- **任務**: 訓練模型遵循特定指令
- **數據**: Alpaca、Dolly、FLAN 等指令數據集
- **應用**: 通用助手、任務執行

### 2. 對話微調
- **任務**: 訓練對話模型
- **數據**: ShareGPT、Guanaco、OASST 等對話數據
- **應用**: 聊天機器人、客服系統

### 3. 領域適應
- **任務**: 適應特定領域（法律、醫療、金融）
- **數據**: 領域專業文本和問答
- **應用**: 專業諮詢、知識問答

### 4. 代碼生成
- **任務**: 訓練代碼生成能力
- **數據**: Code Alpaca、CodeSearchNet
- **應用**: 編程助手、代碼補全

### 5. 多語言訓練
- **任務**: 增強多語言能力
- **數據**: 多語言對照數據
- **應用**: 翻譯、跨語言問答

### 6. RLHF 微調
- **任務**: 基於人類反饋的強化學習
- **數據**: 偏好數據集
- **應用**: 對齊人類價值觀

## 示例文件說明

本目錄包含 10 個完整的示例文件，涵蓋 Axolotl 的各個方面：

1. **01_快速開始.py** - 安裝配置、基本訓練流程
2. **02_數據準備.py** - 數據格式轉換、預處理、驗證
3. **03_LoRA微調.py** - LoRA 配置、訓練、保存
4. **04_QLoRA訓練.py** - QLoRA 4-bit 量化訓練
5. **05_全量微調.py** - 完整參數微調配置
6. **06_多GPU訓練.py** - DDP、FSDP、DeepSpeed 配置
7. **07_評估測試.py** - 模型評估、性能測試
8. **08_模型合併.py** - LoRA 權重合併到基礎模型
9. **09_推理部署.py** - 模型載入、推理優化
10. **10_最佳實踐.py** - 超參數調優、訓練技巧

## 最佳實踐

### 1. 數據準備
- **質量優於數量**: 1000 條高質量數據勝過 10000 條低質量數據
- **數據清洗**: 移除重複、格式化統一
- **數據平衡**: 確保不同類別的平衡
- **驗證集**: 預留 10-20% 作為驗證集

### 2. 超參數選擇

**LoRA 參數:**
- `lora_r`: 8-64（越大效果越好但內存越多）
- `lora_alpha`: r 的 2 倍（16-128）
- `lora_dropout`: 0.05-0.1

**訓練參數:**
- `learning_rate`: 1e-4 到 5e-4（LoRA）
- `batch_size`: 根據 GPU 內存調整
- `num_epochs`: 2-5（避免過擬合）
- `warmup_steps`: 總步數的 5-10%

### 3. 內存優化
- 使用梯度檢查點（gradient_checkpointing）
- 啟用混合精度訓練（bf16 或 fp16）
- 減小批次大小，增加梯度累積
- 使用 QLoRA 4-bit 量化
- 凍結部分層（如 embedding）

### 4. 訓練監控
- 觀察訓練/驗證損失曲線
- 監控梯度範數
- 定期評估生成質量
- 使用 early stopping 避免過擬合

### 5. 模型評估
- **自動指標**: Perplexity、BLEU、ROUGE
- **人工評估**: 生成質量、事實準確性
- **A/B 測試**: 對比不同版本
- **領域測試**: 特定任務的基準測試

## 性能指標

### 訓練速度（7B 模型）

| 配置 | GPU | 批次大小 | 速度 (tokens/s) | 內存使用 |
|-----|-----|----------|----------------|----------|
| LoRA | RTX 3090 24GB | 4 | ~5000 | ~16GB |
| LoRA | A100 40GB | 8 | ~10000 | ~32GB |
| QLoRA | RTX 3090 24GB | 8 | ~3000 | ~12GB |
| 全量微調 | A100 80GB | 2 | ~2000 | ~75GB |

### 常見模型內存需求

| 模型 | 參數量 | LoRA (8bit) | QLoRA (4bit) | 全量微調 (bf16) |
|-----|--------|-------------|--------------|----------------|
| LLaMA-7B | 7B | ~12GB | ~6GB | ~28GB |
| LLaMA-13B | 13B | ~18GB | ~10GB | ~52GB |
| LLaMA-30B | 30B | ~40GB | ~20GB | ~120GB |
| LLaMA-65B | 65B | ~80GB | ~40GB | ~260GB |

## 常見問題

### Q1: Out of Memory (OOM) 錯誤？
- 減小批次大小（batch_size、micro_batch_size）
- 啟用梯度檢查點
- 使用 QLoRA 代替 LoRA
- 減小序列長度（sequence_len）
- 使用多 GPU

### Q2: 訓練損失不下降？
- 檢查學習率（可能太小或太大）
- 確認數據格式正確
- 增加訓練數據量
- 調整 LoRA rank 和 alpha
- 檢查是否需要更多 epochs

### Q3: 生成質量不佳？
- 增加訓練數據質量和數量
- 調整溫度（temperature）參數
- 嘗試不同的採樣策略
- 增加 LoRA rank
- 延長訓練時間

### Q4: 如何選擇微調方法？
- **有限 GPU (<16GB)**: QLoRA
- **中等 GPU (16-24GB)**: LoRA
- **充足資源 (>40GB)**: 全量微調或 LoRA
- **快速實驗**: LoRA（r=8）
- **最佳效果**: 全量微調

## 工作流程

```
┌─────────────────────────────────────────────────┐
│              1. 準備階段                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ 選擇模型 │  │ 準備數據 │  │ 編寫配置 │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│              2. 訓練階段                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ 數據載入 │→ │ 模型訓練 │→ │ 檢查點   │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│              3. 評估階段                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ 模型評估 │  │ 質量測試 │  │ 性能分析 │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│              4. 部署階段                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ 合併權重 │  │ 模型量化 │  │ 推理部署 │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────┘
```

## 相關資源

- **GitHub**: https://github.com/OpenAccess-AI-Collective/axolotl
- **文檔**: https://github.com/OpenAccess-AI-Collective/axolotl/tree/main/docs
- **Discord 社群**: https://discord.gg/HhrNrHJPRb
- **示例配置**: https://github.com/OpenAccess-AI-Collective/axolotl/tree/main/examples
- **HuggingFace**: https://huggingface.co/models?other=axolotl
- **教學影片**: https://www.youtube.com/@AxolotlAI

## 技術棧

- **基礎框架**: PyTorch
- **Transformers**: HuggingFace Transformers
- **PEFT**: Parameter-Efficient Fine-Tuning
- **DeepSpeed**: 分散式訓練加速
- **Flash Attention**: 注意力計算優化
- **BitsAndBytes**: 量化訓練
- **Accelerate**: 多 GPU 訓練抽象
- **Wandb/TensorBoard**: 實驗追蹤

## 版本信息

- **Axolotl**: 0.4+
- **PyTorch**: 2.0+
- **Transformers**: 4.35+
- **PEFT**: 0.7+
- **Python**: 3.9+
- **CUDA**: 11.8+ (推薦 12.1+)

## 授權

Axolotl 採用 Apache License 2.0 授權。本示例代碼僅供學習參考使用。

---

**注意**: Axolotl 是一個活躍開發的項目，功能和 API 可能會有變化。建議定期檢查官方文檔和 GitHub 倉庫以獲取最新信息。對於生產環境，建議充分測試並選擇穩定版本。
