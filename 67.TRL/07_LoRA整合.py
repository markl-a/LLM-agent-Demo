"""
LoRA (Low-Rank Adaptation) 整合訓練

這個文件演示了在 TRL 訓練中整合 LoRA，包括：
1. LoRA 原理和優勢
2. LoRA 配置
3. 與 TRL 訓練器整合
4. QLoRA（量化 LoRA）
5. 記憶體優化技巧

LoRA 是參數高效微調技術，可以在消費級 GPU 上訓練大模型，
大幅降低訓練成本和記憶體需求。
"""

import os
import sys
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
import warnings

warnings.filterwarnings('ignore')


@dataclass
class LoRATrainingConfig:
    """LoRA 訓練配置"""

    # 模型配置
    model_name: str = "gpt2"

    # LoRA 配置
    lora_r: int = 16  # LoRA 秩
    lora_alpha: int = 32  # LoRA alpha
    lora_dropout: float = 0.05  # LoRA dropout
    lora_target_modules: Optional[List[str]] = None  # 目標模組
    lora_bias: str = "none"  # "none", "all", "lora_only"

    # 量化配置（QLoRA）
    use_4bit: bool = False  # 使用 4-bit 量化
    use_8bit: bool = False  # 使用 8-bit 量化
    bnb_4bit_compute_dtype: str = "float16"  # 計算精度
    bnb_4bit_quant_type: str = "nf4"  # 量化類型

    # 訓練配置
    training_type: str = "sft"  # "sft", "dpo", "orpo"
    output_dir: str = "./output/lora_training"
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    max_seq_length: int = 512

    # 其他
    seed: int = 42


def explain_lora():
    """
    解釋 LoRA 原理
    """
    print("\n" + "=" * 60)
    print("LoRA 原理與優勢")
    print("=" * 60)

    explanation = """
LoRA (Low-Rank Adaptation) 是一種參數高效微調技術，
由 Microsoft 在 2021 年提出，徹底改變了大模型微調方式。

核心思想:
不直接更新預訓練模型的權重矩陣 W，而是添加低秩分解：
W' = W + BA
其中:
- W: 原始權重（凍結）
- B, A: 可訓練的低秩矩陣
- B ∈ R^(d×r), A ∈ R^(r×k)
- r << min(d,k)  # r 是秩，通常很小（如 8, 16）

數學原理:
假設 W ∈ R^(d×k)，參數量 = d×k
使用 LoRA: 參數量 = r×(d+k)
當 r << min(d,k) 時，大幅減少可訓練參數

示例計算:
假設 W 是 4096×4096 的矩陣:
- 全量微調: 16,777,216 參數
- LoRA (r=8): 65,536 參數
- 減少 99.6% 參數量！

關鍵優勢:
1. 參數效率
   • 只訓練 0.1-1% 的參數
   • 大幅降低記憶體需求
   • 加快訓練速度

2. 無性能損失
   • 在多個任務上與全量微調相當
   • 甚至某些情況下更好（正則化效果）

3. 便於部署
   • LoRA 權重可以獨立保存（幾 MB）
   • 基礎模型可以共享
   • 快速切換不同任務

4. 可組合性
   • 多個 LoRA 可以疊加
   • 支持多任務學習

5. 易於實現
   • 無需修改模型架構
   • 與現有訓練流程兼容

QLoRA (Quantized LoRA):
• 結合量化和 LoRA
• 使用 4-bit 量化基礎模型
• 在 16-bit 精度下訓練 LoRA
• 在單個 24GB GPU 上微調 65B 模型

記憶體對比（以 7B 模型為例）:
┌──────────────┬─────────┬─────────┐
│   方法       │  記憶體 │ 訓練參數│
├──────────────┼─────────┼─────────┤
│ 全量微調     │  ~28GB  │  100%   │
│ LoRA         │  ~14GB  │  ~0.5%  │
│ QLoRA (8bit) │  ~10GB  │  ~0.5%  │
│ QLoRA (4bit) │   ~6GB  │  ~0.5%  │
└──────────────┴─────────┴─────────┘

應用場景:
✓ 消費級 GPU 訓練大模型
✓ 多任務微調
✓ 快速實驗迭代
✓ 個性化模型部署
✓ 資源受限環境

LoRA 超參數:
• r (秩): 通常 4-64，越大越接近全量微調
• alpha: 縮放因子，通常設為 2×r
• dropout: 防止過擬合，通常 0.05-0.1
• target_modules: 選擇要應用 LoRA 的層
"""

    print(explanation)


def create_lora_config(config: LoRATrainingConfig):
    """
    創建 LoRA 配置

    Args:
        config: LoRA 訓練配置

    Returns:
        LoraConfig 對象
    """
    print("\n" + "=" * 60)
    print("創建 LoRA 配置")
    print("=" * 60)

    try:
        from peft import LoraConfig, TaskType

        # 如果沒有指定目標模組，使用默認值
        if config.lora_target_modules is None:
            # GPT-2 的注意力層
            target_modules = ["c_attn", "c_proj", "c_fc"]
            print("使用默認目標模組（GPT-2）: c_attn, c_proj, c_fc")
        else:
            target_modules = config.lora_target_modules

        # 創建 LoRA 配置
        lora_config = LoraConfig(
            r=config.lora_r,
            lora_alpha=config.lora_alpha,
            lora_dropout=config.lora_dropout,
            target_modules=target_modules,
            bias=config.lora_bias,
            task_type=TaskType.CAUSAL_LM,
        )

        print(f"\nLoRA 配置:")
        print(f"  秩 (r): {config.lora_r}")
        print(f"  Alpha: {config.lora_alpha}")
        print(f"  Dropout: {config.lora_dropout}")
        print(f"  目標模組: {target_modules}")
        print(f"  Bias: {config.lora_bias}")

        # 計算參數減少比例
        print(f"\n預計參數減少: ~99% (只訓練 LoRA 權重)")

        return lora_config

    except Exception as e:
        print(f"✗ 創建 LoRA 配置失敗: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_quantization_config(config: LoRATrainingConfig):
    """
    創建量化配置（用於 QLoRA）

    Args:
        config: LoRA 訓練配置

    Returns:
        BitsAndBytesConfig 對象或 None
    """
    if not config.use_4bit and not config.use_8bit:
        return None

    print("\n" + "=" * 60)
    print("創建量化配置（QLoRA）")
    print("=" * 60)

    try:
        from transformers import BitsAndBytesConfig
        import torch

        if config.use_4bit:
            print("使用 4-bit 量化")
            quant_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16 if config.bnb_4bit_compute_dtype == "float16" else torch.bfloat16,
                bnb_4bit_quant_type=config.bnb_4bit_quant_type,
                bnb_4bit_use_double_quant=True,  # 雙重量化
            )
            print(f"  量化類型: {config.bnb_4bit_quant_type}")
            print(f"  計算精度: {config.bnb_4bit_compute_dtype}")
            print(f"  記憶體節省: ~75%")

        elif config.use_8bit:
            print("使用 8-bit 量化")
            quant_config = BitsAndBytesConfig(
                load_in_8bit=True,
            )
            print(f"  記憶體節省: ~50%")

        return quant_config

    except Exception as e:
        print(f"✗ 創建量化配置失敗: {e}")
        print("請安裝: pip install bitsandbytes")
        import traceback
        traceback.print_exc()
        return None


def load_model_with_lora(config: LoRATrainingConfig, lora_config, quant_config=None):
    """
    加載帶 LoRA 的模型

    Args:
        config: LoRA 訓練配置
        lora_config: LoRA 配置
        quant_config: 量化配置（可選）

    Returns:
        tuple: (model, tokenizer)
    """
    print("\n" + "=" * 60)
    print("加載帶 LoRA 的模型")
    print("=" * 60)

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import get_peft_model
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"使用設備: {device}")

        # 加載分詞器
        print("\n1. 加載分詞器...")
        tokenizer = AutoTokenizer.from_pretrained(config.model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        print("   ✓ 分詞器加載成功")

        # 加載基礎模型
        print("2. 加載基礎模型...")

        load_kwargs = {
            "trust_remote_code": True,
        }

        # 添加量化配置
        if quant_config is not None:
            load_kwargs["quantization_config"] = quant_config
            load_kwargs["device_map"] = "auto"
        else:
            load_kwargs["torch_dtype"] = torch.float32

        model = AutoModelForCausalLM.from_pretrained(
            config.model_name,
            **load_kwargs
        )

        print(f"   ✓ 基礎模型參數: {model.num_parameters() / 1e6:.2f}M")

        # 應用 LoRA
        print("3. 應用 LoRA...")
        model = get_peft_model(model, lora_config)

        # 顯示可訓練參數
        trainable_params, all_params = model.get_nb_trainable_parameters()
        print(f"\n參數統計:")
        print(f"  總參數: {all_params:,}")
        print(f"  可訓練參數: {trainable_params:,}")
        print(f"  可訓練比例: {100 * trainable_params / all_params:.2f}%")

        # 顯示模型結構
        print(f"\nLoRA 已應用到以下層:")
        model.print_trainable_parameters()

        return model, tokenizer

    except Exception as e:
        print(f"✗ 加載模型失敗: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def train_with_lora_sft(model, tokenizer, config: LoRATrainingConfig):
    """
    使用 LoRA 進行 SFT 訓練

    Args:
        model: LoRA 模型
        tokenizer: 分詞器
        config: 訓練配置
    """
    print("\n" + "=" * 60)
    print("使用 LoRA 進行 SFT 訓練")
    print("=" * 60)

    try:
        from trl import SFTTrainer, SFTConfig
        from datasets import Dataset

        # 創建示例數據
        data = {
            "text": [
                "### Human: 什麼是 LoRA？\n### Assistant: LoRA 是低秩適應技術，通過添加小型可訓練矩陣來微調大模型，大幅減少參數量和記憶體需求。",
                "### Human: LoRA 的優勢？\n### Assistant: LoRA 的主要優勢包括參數效率高、訓練快速、記憶體需求低、便於部署，可在消費級 GPU 上訓練大模型。",
                "### Human: 什麼是 QLoRA？\n### Assistant: QLoRA 結合了量化和 LoRA，使用 4-bit 量化基礎模型，進一步降低記憶體需求，可在單個 GPU 上訓練超大模型。",
            ] * 3  # 重複以增加樣本數
        }
        dataset = Dataset.from_dict(data)

        print(f"訓練數據: {len(dataset)} 個樣本")

        # 創建輸出目錄
        os.makedirs(config.output_dir, exist_ok=True)

        # 訓練配置
        training_args = SFTConfig(
            output_dir=config.output_dir,
            num_train_epochs=config.num_train_epochs,
            per_device_train_batch_size=config.per_device_train_batch_size,
            gradient_accumulation_steps=config.gradient_accumulation_steps,
            learning_rate=config.learning_rate,
            logging_steps=1,
            save_strategy="epoch",
            max_seq_length=config.max_seq_length,
            report_to="none",
            seed=config.seed,
        )

        print(f"\n訓練配置:")
        print(f"  Epochs: {config.num_train_epochs}")
        print(f"  Batch Size: {config.per_device_train_batch_size}")
        print(f"  Learning Rate: {config.learning_rate}")

        # 創建訓練器
        trainer = SFTTrainer(
            model=model,
            args=training_args,
            train_dataset=dataset,
            dataset_text_field="text",
            tokenizer=tokenizer,
        )

        print("\n開始訓練...")
        trainer.train()

        print("\n✓ 訓練完成")

        # 保存 LoRA 權重
        lora_path = os.path.join(config.output_dir, "lora_weights")
        model.save_pretrained(lora_path)
        tokenizer.save_pretrained(lora_path)

        print(f"\n✓ LoRA 權重保存到: {lora_path}")

        # 檢查文件大小
        import glob
        lora_files = glob.glob(os.path.join(lora_path, "*.bin")) + glob.glob(os.path.join(lora_path, "*.safetensors"))
        if lora_files:
            total_size = sum(os.path.getsize(f) for f in lora_files)
            print(f"✓ LoRA 權重大小: {total_size / 1e6:.2f} MB")
            print(f"  (相比完整模型，節省大量空間！)")

        return trainer

    except Exception as e:
        print(f"✗ 訓練失敗: {e}")
        import traceback
        traceback.print_exc()
        return None


def load_and_merge_lora(base_model_name: str, lora_path: str):
    """
    加載並合併 LoRA 權重

    Args:
        base_model_name: 基礎模型名稱
        lora_path: LoRA 權重路徑
    """
    print("\n" + "=" * 60)
    print("加載並合併 LoRA 權重")
    print("=" * 60)

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel

        # 加載基礎模型
        print(f"1. 加載基礎模型: {base_model_name}")
        base_model = AutoModelForCausalLM.from_pretrained(base_model_name)
        tokenizer = AutoTokenizer.from_pretrained(base_model_name)

        # 加載 LoRA 權重
        print(f"2. 加載 LoRA 權重: {lora_path}")
        model = PeftModel.from_pretrained(base_model, lora_path)

        print("3. 可選操作:")
        print("   • model.merge_and_unload() - 合併 LoRA 到基礎模型")
        print("   • 然後可以保存為標準模型格式")

        # 示例：合併並保存
        # merged_model = model.merge_and_unload()
        # merged_model.save_pretrained("merged_model")

        print("\n✓ LoRA 權重加載成功")

        return model, tokenizer

    except Exception as e:
        print(f"✗ 加載失敗: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def demonstrate_lora_advantages():
    """
    演示 LoRA 的實際優勢
    """
    print("\n" + "=" * 60)
    print("LoRA 實際應用優勢")
    print("=" * 60)

    advantages = """
1. 多任務部署:

   基礎模型（固定）
        ├── LoRA-任務A (10MB)
        ├── LoRA-任務B (10MB)
        ├── LoRA-任務C (10MB)
        └── LoRA-任務D (10MB)

   只需一個基礎模型 + 多個小型 LoRA 適配器
   快速切換任務，無需重新加載大模型

2. 記憶體節省示例:

   7B 模型全量微調:
   • 模型參數: 14GB (FP16)
   • 梯度: 14GB
   • 優化器狀態: 28GB
   • 總計: ~56GB
   └─> 需要 A100 80GB

   7B 模型 + LoRA:
   • 模型參數: 14GB (凍結)
   • LoRA 參數: 70MB
   • 梯度: 70MB
   • 優化器狀態: 140MB
   • 總計: ~15GB
   └─> 可用 RTX 3090 24GB

   7B 模型 + QLoRA (4-bit):
   • 模型參數: 3.5GB (量化)
   • LoRA 參數: 70MB
   • 梯度: 70MB
   • 優化器狀態: 140MB
   • 總計: ~5GB
   └─> 可用 RTX 3060 12GB！

3. 訓練速度:

   全量微調: 100% (基準)
   LoRA: ~150% (更快！因為參數少)
   QLoRA: ~80% (稍慢，但可訓練更大模型)

4. 存儲效率:

   全量微調模型:
   • 每個任務: ~14GB
   • 10 個任務: ~140GB

   LoRA:
   • 基礎模型: 14GB (共享)
   • 每個 LoRA: ~10MB
   • 10 個任務: ~14.1GB
   └─> 節省 90% 存儲空間

5. 實驗迭代:

   全量微調:
   • 保存檢查點: 14GB × N 個
   • 切換模型: 重新加載 14GB

   LoRA:
   • 保存檢查點: 10MB × N 個
   • 切換模型: 只加載 10MB
   └─> 快速實驗迭代

6. 生產部署:

   場景: 個性化聊天機器人
   • 基礎模型: 統一的語言能力
   • 用戶 LoRA: 個性化風格/知識
   • 動態加載: 根據用戶切換 LoRA
   • 成本: 每個用戶只需 10MB

7. 組合能力:

   可以疊加多個 LoRA:
   LoRA-語言風格 + LoRA-專業知識 + LoRA-個性化
   = 定制化模型

8. 最佳實踐:

   選擇 r (秩):
   • r=4-8: 簡單任務
   • r=16: 通用推薦
   • r=32-64: 複雜任務
   • r 越大越接近全量微調

   選擇目標層:
   • 注意力層: 通常最重要
   • MLP 層: 可選添加
   • 全部層: 最大靈活性（但更慢）

   學習率:
   • LoRA 通常需要更高學習率
   • 推薦: 1e-4 到 3e-4
   • 是全量微調的 10-100 倍

9. 常見問題:

   Q: LoRA 會降低性能嗎？
   A: 通常不會。r 足夠大時性能與全量微調相當。

   Q: 所有模型都適用嗎？
   A: 是的。Transformer 架構都可以。

   Q: 可以訓練哪些層？
   A: 任何線性層。通常選擇注意力層。

   Q: LoRA 和量化能一起用嗎？
   A: 可以！這就是 QLoRA。
"""

    print(advantages)


def main():
    """
    主函數：演示 LoRA 整合訓練
    """
    print("=" * 60)
    print("LoRA 整合訓練")
    print("=" * 60)

    # 1. 解釋 LoRA
    explain_lora()

    # 2. 創建配置
    config = LoRATrainingConfig(
        model_name="gpt2",
        lora_r=8,
        lora_alpha=16,
        num_train_epochs=1,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=2,
        learning_rate=2e-4,
        output_dir="./output/lora_training",
        use_4bit=False,  # 設為 True 啟用 QLoRA
    )

    # 3. 創建 LoRA 配置
    lora_config = create_lora_config(config)
    if lora_config is None:
        print("LoRA 配置創建失敗，退出程序")
        return

    # 4. 創建量化配置（可選）
    quant_config = create_quantization_config(config)

    # 5. 加載模型
    model, tokenizer = load_model_with_lora(config, lora_config, quant_config)
    if model is None:
        print("模型加載失敗，退出程序")
        return

    # 6. 訓練
    trainer = train_with_lora_sft(model, tokenizer, config)

    # 7. 演示 LoRA 優勢
    demonstrate_lora_advantages()

    # 8. 示例：加載 LoRA（如果訓練成功）
    if trainer is not None:
        lora_path = os.path.join(config.output_dir, "lora_weights")
        if os.path.exists(lora_path):
            print("\n演示：加載保存的 LoRA 權重")
            # load_and_merge_lora(config.model_name, lora_path)

    # 9. 總結
    print("\n" + "=" * 60)
    print("LoRA 訓練演示完成！")
    print("=" * 60)

    print("\nLoRA 的革命性意義:")
    print("  ✓ 使大模型微調民主化")
    print("  ✓ 降低 99% 參數量")
    print("  ✓ 節省 70% 以上記憶體")
    print("  ✓ 加快訓練和部署")
    print("  ✓ 支持多任務和個性化")

    print("\n建議:")
    print("  • 優先使用 LoRA 進行實驗")
    print("  • 記憶體受限時使用 QLoRA")
    print("  • 生產環境可考慮合併權重")
    print("  • 多任務場景保持分離")

    print("\n進一步學習:")
    print("  • LoRA 論文: https://arxiv.org/abs/2106.09685")
    print("  • QLoRA 論文: https://arxiv.org/abs/2305.14314")
    print("  • PEFT 文檔: https://huggingface.co/docs/peft/")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用戶中斷")
    except Exception as e:
        print(f"\n程序執行出錯: {e}")
        import traceback
        traceback.print_exc()
