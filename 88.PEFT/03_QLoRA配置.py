"""
QLoRA 量化微調配置

這個文件介紹 QLoRA (Quantized LoRA) 的使用，包括：
1. QLoRA 原理和優勢
2. 4-bit 和 8-bit 量化配置
3. 顯存優化策略
4. 在消費級 GPU 上訓練大模型
5. 性能與精度平衡

QLoRA 結合了量化和 LoRA，可以在單個 24GB GPU 上微調 65B 參數的模型！
"""

import os
import torch
from typing import Dict, Optional
import warnings

warnings.filterwarnings('ignore')


def explain_qlora():
    """
    解釋 QLoRA 的原理
    """
    print("=" * 70)
    print("QLoRA 原理詳解")
    print("=" * 70)

    print("""
QLoRA (Quantized Low-Rank Adaptation) 的創新點：

1. 核心技術組合：
   • 4-bit NormalFloat (NF4) 量化
   • 雙重量化 (Double Quantization)
   • 分頁優化器 (Paged Optimizers)
   • LoRA 低秩適配

2. NF4 量化：
   • 專為正態分佈權重設計的 4-bit 數據類型
   • 相比傳統 INT4，更適合神經網絡權重
   • 理論上信息損失最小化

3. 雙重量化：
   • 對量化常數本身也進行量化
   • 進一步節省顯存
   • 每 64 個參數共享一個量化常數

4. 分頁優化器：
   • 使用 NVIDIA 統一內存
   • 自動在 CPU 和 GPU 間轉移數據
   • 避免 OOM（內存不足）錯誤

5. 顯存節省：
   • 4-bit 量化: 相比 FP32 節省 87.5% 顯存
   • 結合 LoRA: 額外節省訓練參數顯存
   • 總計可節省 90% 以上顯存

6. 實例對比（LLaMA-7B）：
   ┌─────────────────┬───────────┬──────────────┐
   │ 方法            │ 顯存需求  │ 可訓練參數   │
   ├─────────────────┼───────────┼──────────────┤
   │ 全量微調 (FP32) │ ~28 GB    │ 7B (100%)    │
   │ 全量微調 (FP16) │ ~14 GB    │ 7B (100%)    │
   │ LoRA (FP16)     │ ~12 GB    │ ~30M (0.4%)  │
   │ QLoRA (8-bit)   │ ~9 GB     │ ~30M (0.4%)  │
   │ QLoRA (4-bit)   │ ~5 GB     │ ~30M (0.4%)  │
   └─────────────────┴───────────┴──────────────┘

結論：QLoRA 讓你能在單個消費級 GPU 上微調大型模型！
    """)


def create_quantization_configs() -> Dict:
    """
    創建不同的量化配置

    Returns:
        Dict: 量化配置字典
    """
    print("\n" + "=" * 70)
    print("量化配置方案")
    print("=" * 70)

    from transformers import BitsAndBytesConfig

    configs = {
        "4-bit NF4 (推薦)": BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16
        ),
        "4-bit FP4": BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="fp4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16
        ),
        "8-bit": BitsAndBytesConfig(
            load_in_8bit=True,
            llm_int8_threshold=6.0
        ),
        "4-bit NF4 (float16計算)": BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.float16
        ),
    }

    print("\n各配置詳情：\n")
    for name, config in configs.items():
        print(f"【{name}】")

        if hasattr(config, 'load_in_4bit') and config.load_in_4bit:
            print(f"  量化位數: 4-bit")
            print(f"  量化類型: {config.bnb_4bit_quant_type}")
            print(f"  雙重量化: {config.bnb_4bit_use_double_quant}")
            print(f"  計算精度: {config.bnb_4bit_compute_dtype}")
            print(f"  顯存節省: ~75%")
            print(f"  適用: 顯存受限，追求最大節省")

        elif hasattr(config, 'load_in_8bit') and config.load_in_8bit:
            print(f"  量化位數: 8-bit")
            print(f"  INT8 閾值: {config.llm_int8_threshold}")
            print(f"  顯存節省: ~50%")
            print(f"  適用: 平衡性能和顯存")

        print()

    return configs


def load_quantized_model(
    model_name: str = "gpt2",
    quantization_config = None
):
    """
    加載量化模型

    Args:
        model_name: 模型名稱
        quantization_config: 量化配置

    Returns:
        tuple: (model, tokenizer)
    """
    print("\n" + "=" * 70)
    print(f"加載量化模型: {model_name}")
    print("=" * 70)

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer

        # 加載分詞器
        print("\n1. 加載分詞器...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        # 加載量化模型
        print("2. 加載量化模型...")
        if quantization_config:
            print("   使用量化配置:")
            if hasattr(quantization_config, 'load_in_4bit'):
                print(f"   - 4-bit 量化: {quantization_config.load_in_4bit}")
                if quantization_config.load_in_4bit:
                    print(f"   - 量化類型: {quantization_config.bnb_4bit_quant_type}")
                    print(f"   - 雙重量化: {quantization_config.bnb_4bit_use_double_quant}")
            if hasattr(quantization_config, 'load_in_8bit'):
                print(f"   - 8-bit 量化: {quantization_config.load_in_8bit}")

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=quantization_config,
            device_map="auto",  # 自動分配設備
            trust_remote_code=True
        )

        print("\n✓ 模型加載成功")

        # 顯示模型信息
        print(f"\n模型信息:")
        print(f"  參數量: {model.num_parameters() / 1e6:.2f}M")

        # 顯示設備映射
        if hasattr(model, 'hf_device_map'):
            print(f"  設備映射: {model.hf_device_map}")

        # 估計顯存使用
        if torch.cuda.is_available():
            memory_allocated = torch.cuda.memory_allocated() / 1e9
            print(f"  當前顯存使用: {memory_allocated:.2f} GB")

        return model, tokenizer

    except Exception as e:
        print(f"✗ 加載失敗: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def prepare_model_for_training(model):
    """
    準備量化模型進行訓練

    Args:
        model: 量化後的模型

    Returns:
        準備好的模型
    """
    print("\n" + "=" * 70)
    print("準備模型進行訓練")
    print("=" * 70)

    try:
        from peft import prepare_model_for_kbit_training

        print("\n1. 準備 k-bit 訓練...")
        model = prepare_model_for_kbit_training(model)

        print("2. 啟用梯度檢查點...")
        model.gradient_checkpointing_enable()

        print("\n✓ 模型準備完成")

        return model

    except Exception as e:
        print(f"✗ 準備失敗: {e}")
        import traceback
        traceback.print_exc()
        return None


def apply_qlora(model, target_modules: list = None):
    """
    應用 QLoRA 配置

    Args:
        model: 量化後的模型
        target_modules: 目標模塊

    Returns:
        PEFT 模型
    """
    print("\n" + "=" * 70)
    print("應用 QLoRA")
    print("=" * 70)

    try:
        from peft import LoraConfig, get_peft_model, TaskType

        # 默認目標模塊（適用於大多數 Transformer 模型）
        if target_modules is None:
            target_modules = ["q_proj", "k_proj", "v_proj", "o_proj"]

        # QLoRA 配置
        qlora_config = LoraConfig(
            r=64,  # QLoRA 論文推薦使用較大的秩
            lora_alpha=16,
            target_modules=target_modules,
            lora_dropout=0.05,
            bias="none",
            task_type=TaskType.CAUSAL_LM
        )

        print("\nQLoRA 配置:")
        print(f"  秩 (r): {qlora_config.r}")
        print(f"  Alpha: {qlora_config.lora_alpha}")
        print(f"  目標模塊: {qlora_config.target_modules}")
        print(f"  Dropout: {qlora_config.lora_dropout}")

        # 應用 LoRA
        print("\n應用 LoRA 到量化模型...")
        peft_model = get_peft_model(model, qlora_config)

        # 顯示參數統計
        print("\n參數統計:")
        peft_model.print_trainable_parameters()

        return peft_model

    except Exception as e:
        print(f"✗ 應用 QLoRA 失敗: {e}")
        import traceback
        traceback.print_exc()
        return None


def qlora_training_example(
    model,
    tokenizer,
    dataset,
    output_dir: str = "./output/qlora_model"
):
    """
    QLoRA 訓練完整示例

    Args:
        model: QLoRA 模型
        tokenizer: 分詞器
        dataset: 訓練數據集
        output_dir: 輸出目錄
    """
    print("\n" + "=" * 70)
    print("QLoRA 訓練")
    print("=" * 70)

    try:
        from transformers import Trainer, TrainingArguments, DataCollatorForLanguageModeling

        os.makedirs(output_dir, exist_ok=True)

        # 訓練參數 - QLoRA 特定優化
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=1,  # QLoRA 通常使用較小的 batch size
            gradient_accumulation_steps=16,  # 通過梯度累積增加有效 batch size
            learning_rate=2e-4,
            weight_decay=0.01,
            logging_steps=10,
            save_strategy="epoch",
            save_total_limit=2,
            bf16=True,  # QLoRA 推薦使用 bfloat16
            gradient_checkpointing=True,  # 啟用梯度檢查點節省顯存
            optim="paged_adamw_8bit",  # 使用分頁優化器
            report_to="none",
        )

        print("\n訓練配置:")
        print(f"  Batch Size: {training_args.per_device_train_batch_size}")
        print(f"  梯度累積: {training_args.gradient_accumulation_steps}")
        print(f"  有效 Batch Size: {training_args.per_device_train_batch_size * training_args.gradient_accumulation_steps}")
        print(f"  學習率: {training_args.learning_rate}")
        print(f"  優化器: {training_args.optim}")
        print(f"  精度: bf16")

        # 數據整理器
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False
        )

        # 預處理數據
        def tokenize_function(examples):
            return tokenizer(examples["text"], truncation=True, max_length=512, padding="max_length")

        tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=dataset.column_names)

        # 創建訓練器
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=data_collator,
        )

        # 訓練
        print("\n開始訓練...")
        print("=" * 70)
        trainer.train()

        # 保存
        print("\n保存模型...")
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)

        print("\n✓ 訓練完成！")

        return trainer

    except Exception as e:
        print(f"✗ 訓練失敗: {e}")
        import traceback
        traceback.print_exc()
        return None


def memory_comparison():
    """
    顯存使用對比
    """
    print("\n" + "=" * 70)
    print("顯存使用對比（LLaMA 模型系列）")
    print("=" * 70)

    comparisons = [
        {
            "模型": "LLaMA-7B",
            "全量FP32": "28 GB",
            "全量FP16": "14 GB",
            "LoRA": "12 GB",
            "QLoRA-8bit": "9 GB",
            "QLoRA-4bit": "5 GB",
            "推薦GPU": "RTX 3090/4090 (24GB)"
        },
        {
            "模型": "LLaMA-13B",
            "全量FP32": "52 GB",
            "全量FP16": "26 GB",
            "LoRA": "20 GB",
            "QLoRA-8bit": "16 GB",
            "QLoRA-4bit": "9 GB",
            "推薦GPU": "A100 40GB 或 RTX 4090"
        },
        {
            "模型": "LLaMA-33B",
            "全量FP32": "132 GB",
            "全量FP16": "66 GB",
            "LoRA": "50 GB",
            "QLoRA-8bit": "40 GB",
            "QLoRA-4bit": "24 GB",
            "推薦GPU": "A100 40GB (需多卡) 或 H100"
        },
        {
            "模型": "LLaMA-65B",
            "全量FP32": "260 GB",
            "全量FP16": "130 GB",
            "LoRA": "95 GB",
            "QLoRA-8bit": "80 GB",
            "QLoRA-4bit": "48 GB",
            "推薦GPU": "A100 80GB 或 H100 80GB"
        },
    ]

    for comp in comparisons:
        print(f"\n【{comp['模型']}】")
        print(f"  全量微調 (FP32): {comp['全量FP32']}")
        print(f"  全量微調 (FP16): {comp['全量FP16']}")
        print(f"  LoRA (FP16):     {comp['LoRA']}")
        print(f"  QLoRA (8-bit):   {comp['QLoRA-8bit']}")
        print(f"  QLoRA (4-bit):   {comp['QLoRA-4bit']}")
        print(f"  推薦 GPU:        {comp['推薦GPU']}")

    print("\n" + "=" * 70)
    print("關鍵結論:")
    print("  • QLoRA-4bit 可以在單個 24GB GPU 上訓練 33B 模型")
    print("  • QLoRA-4bit 可以在單個 48GB GPU 上訓練 65B 模型")
    print("  • 顯存節省 75-85%，同時保持性能")
    print("=" * 70)


def best_practices():
    """
    QLoRA 最佳實踐
    """
    print("\n" + "=" * 70)
    print("QLoRA 最佳實踐")
    print("=" * 70)

    practices = {
        "1. 量化類型選擇": [
            "優先使用 NF4 量化（專為神經網絡設計）",
            "啟用雙重量化以進一步節省顯存",
            "計算精度使用 bfloat16（如果硬件支持）"
        ],
        "2. LoRA 配置": [
            "使用較大的秩 (r=64) - QLoRA 論文推薦",
            "目標模塊包含所有注意力層",
            "考慮添加 FFN 層以提升性能"
        ],
        "3. 訓練配置": [
            "使用 paged_adamw_8bit 優化器",
            "啟用梯度檢查點",
            "較小的 batch size + 梯度累積",
            "學習率可以稍高 (2e-4 到 3e-4)"
        ],
        "4. 顯存優化": [
            "設置 device_map='auto' 自動分配",
            "使用 gradient_checkpointing",
            "限制序列長度",
            "減少 batch size，增加梯度累積步數"
        ],
        "5. 性能保持": [
            "4-bit 量化幾乎不損失性能",
            "關鍵是使用 NF4 和雙重量化",
            "訓練時計算仍使用 16-bit",
            "適當增加訓練步數"
        ],
        "6. 常見問題": [
            "OOM 錯誤: 減小 batch size 或序列長度",
            "訓練慢: 檢查是否啟用了梯度檢查點",
            "精度下降: 嘗試增加 LoRA 秩或使用 8-bit",
            "保存失敗: 確保只保存適配器，不保存整個模型"
        ]
    }

    for title, items in practices.items():
        print(f"\n{title}:")
        for item in items:
            print(f"  • {item}")


def main():
    """
    主函數：QLoRA 完整教程
    """
    print("=" * 70)
    print("QLoRA 量化微調完整指南")
    print("=" * 70)

    # 1. 原理講解
    explain_qlora()

    # 2. 配置方案
    configs = create_quantization_configs()

    # 3. 顯存對比
    memory_comparison()

    # 4. 最佳實踐
    best_practices()

    # 5. 實際使用示例
    print("\n" + "=" * 70)
    print("實際使用示例（已註釋）")
    print("=" * 70)
    print("""
取消以下代碼的註釋以運行 QLoRA 訓練：

# from transformers import BitsAndBytesConfig
# from datasets import Dataset
#
# # 1. 創建量化配置
# bnb_config = BitsAndBytesConfig(
#     load_in_4bit=True,
#     bnb_4bit_quant_type="nf4",
#     bnb_4bit_use_double_quant=True,
#     bnb_4bit_compute_dtype=torch.bfloat16
# )
#
# # 2. 加載量化模型
# model, tokenizer = load_quantized_model("gpt2", bnb_config)
#
# # 3. 準備訓練
# model = prepare_model_for_training(model)
#
# # 4. 應用 QLoRA
# peft_model = apply_qlora(model)
#
# # 5. 創建數據集
# dataset = Dataset.from_dict({
#     "text": ["示例文本 " + str(i) for i in range(100)]
# })
#
# # 6. 訓練
# trainer = qlora_training_example(peft_model, tokenizer, dataset)
    """)

    print("\n" + "=" * 70)
    print("總結")
    print("=" * 70)
    print("""
QLoRA 的革命性突破：
  ✓ 在消費級 GPU 上訓練大型模型
  ✓ 顯存節省 75-85%
  ✓ 性能幾乎無損失
  ✓ 訓練速度可接受
  ✓ 降低了 AI 研究的門檻

關鍵技術：
  • NF4 量化: 為神經網絡優化的 4-bit 格式
  • 雙重量化: 連量化常數也量化
  • 分頁優化器: 智能管理顯存
  • LoRA: 只訓練少量參數

實際效果：
  • 單個 24GB GPU → 訓練 33B 模型
  • 單個 48GB GPU → 訓練 65B 模型
  • 消費級硬件 → 企業級能力
    """)

    print("\n資源:")
    print("  • QLoRA 論文: https://arxiv.org/abs/2305.14314")
    print("  • PEFT 文檔: https://huggingface.co/docs/peft/")
    print("  • bitsandbytes: https://github.com/TimDettmers/bitsandbytes")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用戶中斷")
    except Exception as e:
        print(f"\n程序執行出錯: {e}")
        import traceback
        traceback.print_exc()
