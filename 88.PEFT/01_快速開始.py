"""
PEFT 快速開始示例

這個文件演示了 PEFT 框架的基礎使用，包括：
1. 環境設置與依賴檢查
2. 模型和分詞器加載
3. LoRA 配置和應用
4. 查看可訓練參數
5. 簡單的訓練示例

PEFT (Parameter-Efficient Fine-Tuning) 是 HuggingFace 的參數高效微調庫，
可以以極低的成本微調大型模型。
"""

import os
import sys
from typing import Dict, Optional
import warnings

warnings.filterwarnings('ignore')


def check_dependencies() -> Dict[str, bool]:
    """
    檢查必要的依賴包是否已安裝

    Returns:
        Dict[str, bool]: 各依賴包的安裝狀態
    """
    print("=" * 60)
    print("檢查依賴包...")
    print("=" * 60)

    dependencies = {
        'torch': False,
        'transformers': False,
        'peft': False,
        'accelerate': False,
        'datasets': False
    }

    for package in dependencies.keys():
        try:
            __import__(package)
            dependencies[package] = True
            print(f"✓ {package:15s} - 已安裝")
        except ImportError:
            dependencies[package] = False
            print(f"✗ {package:15s} - 未安裝")

    print("=" * 60)

    all_installed = all(dependencies.values())
    if not all_installed:
        print("\n⚠️  部分依賴未安裝，請運行：pip install -r requirements.txt")
    else:
        print("\n✓ 所有依賴已安裝完成！")

    return dependencies


def get_device() -> str:
    """
    獲取可用的計算設備（GPU 或 CPU）

    Returns:
        str: 設備名稱
    """
    try:
        import torch
        if torch.cuda.is_available():
            device = "cuda"
            print(f"\n使用 GPU: {torch.cuda.get_device_name(0)}")
            print(f"顯存: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        else:
            device = "cpu"
            print("\n使用 CPU (建議使用 GPU 進行訓練)")
        return device
    except Exception as e:
        print(f"獲取設備信息時出錯: {e}")
        return "cpu"


def load_base_model(model_name: str = "gpt2"):
    """
    加載基礎模型和分詞器

    Args:
        model_name: 模型名稱，默認使用 GPT-2

    Returns:
        tuple: (model, tokenizer)
    """
    print("\n" + "=" * 60)
    print(f"加載基礎模型: {model_name}")
    print("=" * 60)

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer

        print("加載分詞器...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)

        # 設置 pad_token（GPT-2 默認沒有）
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            print("設置 pad_token = eos_token")

        print("加載模型...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True
        )

        print(f"✓ 模型加載成功")
        print(f"  模型參數量: {model.num_parameters() / 1e6:.2f}M")

        return model, tokenizer

    except Exception as e:
        print(f"✗ 加載模型失敗: {e}")
        return None, None


def apply_lora(model):
    """
    應用 LoRA 到模型

    Args:
        model: 基礎模型

    Returns:
        PEFT 模型
    """
    print("\n" + "=" * 60)
    print("應用 LoRA 配置")
    print("=" * 60)

    try:
        from peft import LoraConfig, get_peft_model, TaskType

        # 配置 LoRA 參數
        lora_config = LoraConfig(
            r=16,                          # LoRA 秩
            lora_alpha=32,                 # LoRA alpha 參數
            target_modules=["c_attn"],     # 目標模塊（GPT-2 的注意力層）
            lora_dropout=0.1,              # Dropout 率
            bias="none",                   # 偏置設置
            task_type=TaskType.CAUSAL_LM   # 任務類型
        )

        print("\nLoRA 配置:")
        print(f"  秩 (r): {lora_config.r}")
        print(f"  Alpha: {lora_config.lora_alpha}")
        print(f"  目標模塊: {lora_config.target_modules}")
        print(f"  Dropout: {lora_config.lora_dropout}")

        # 應用 LoRA
        print("\n應用 LoRA 到模型...")
        peft_model = get_peft_model(model, lora_config)

        print("✓ LoRA 應用成功")

        # 顯示可訓練參數統計
        peft_model.print_trainable_parameters()

        return peft_model

    except Exception as e:
        print(f"✗ 應用 LoRA 失敗: {e}")
        import traceback
        traceback.print_exc()
        return None


def analyze_model_structure(model):
    """
    分析模型結構，顯示可以應用 LoRA 的層

    Args:
        model: 模型
    """
    print("\n" + "=" * 60)
    print("模型結構分析")
    print("=" * 60)

    try:
        print("\n主要模塊:")
        for name, module in model.named_modules():
            # 只顯示主要層，跳過子模塊
            if '.' not in name and name:
                module_type = type(module).__name__
                print(f"  • {name:20s} - {module_type}")

        print("\n線性層（可應用 LoRA）:")
        linear_layers = []
        for name, module in model.named_modules():
            if isinstance(module, type(model).__bases__[0].__bases__[0]):  # Linear layer
                continue
            module_type = type(module).__name__
            if 'Linear' in module_type or 'Attention' in module_type:
                linear_layers.append((name, module_type))

        for name, module_type in linear_layers[:10]:  # 只顯示前 10 個
            print(f"  • {name:30s} - {module_type}")

        if len(linear_layers) > 10:
            print(f"  ... 還有 {len(linear_layers) - 10} 個線性層")

    except Exception as e:
        print(f"分析模型結構時出錯: {e}")


def create_sample_dataset():
    """
    創建示例訓練數據集

    Returns:
        Dataset: HuggingFace 數據集對象
    """
    print("\n" + "=" * 60)
    print("創建示例數據集")
    print("=" * 60)

    try:
        from datasets import Dataset

        # 創建簡單的文本數據
        data = {
            "text": [
                "PEFT 是一個參數高效的微調庫。",
                "LoRA 通過低秩矩陣分解減少可訓練參數。",
                "使用 PEFT 可以在消費級 GPU 上訓練大模型。",
                "QLoRA 結合了量化和 LoRA 技術。",
                "Prefix Tuning 通過添加可訓練前綴進行微調。",
                "PEFT 支持多種高效微調方法。",
                "適配器可以輕鬆保存和加載。",
                "一個基礎模型可以使用多個適配器。",
            ]
        }

        dataset = Dataset.from_dict(data)
        print(f"✓ 創建數據集成功，包含 {len(dataset)} 個樣本")
        print(f"\n示例數據：")
        print(f"  {dataset[0]['text']}")

        return dataset

    except Exception as e:
        print(f"✗ 創建數據集失敗: {e}")
        return None


def simple_training_demo(model, tokenizer, dataset, output_dir: str = "./output/peft_quick_start"):
    """
    簡單的訓練演示

    Args:
        model: PEFT 模型
        tokenizer: 分詞器
        dataset: 訓練數據集
        output_dir: 輸出目錄
    """
    print("\n" + "=" * 60)
    print("訓練演示")
    print("=" * 60)

    try:
        from transformers import Trainer, TrainingArguments, DataCollatorForLanguageModeling

        # 創建輸出目錄
        os.makedirs(output_dir, exist_ok=True)

        # 配置訓練參數
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=1,
            per_device_train_batch_size=2,
            learning_rate=3e-4,  # LoRA 通常使用較高的學習率
            logging_steps=1,
            save_strategy="epoch",
            report_to="none",
        )

        print("\n訓練配置:")
        print(f"  Epochs: {training_args.num_train_epochs}")
        print(f"  Batch Size: {training_args.per_device_train_batch_size}")
        print(f"  Learning Rate: {training_args.learning_rate}")

        # 數據整理器
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False
        )

        # 預處理數據集
        def tokenize_function(examples):
            return tokenizer(examples["text"], truncation=True, max_length=128)

        tokenized_dataset = dataset.map(tokenize_function, batched=True)

        # 創建訓練器
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=data_collator,
        )

        print("\n開始訓練...")
        trainer.train()

        print("\n✓ 訓練完成！")

        # 保存適配器（只保存 LoRA 參數，非常小）
        print(f"\n保存 LoRA 適配器到: {output_dir}")
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)

        # 檢查適配器大小
        adapter_file = os.path.join(output_dir, "adapter_model.safetensors")
        if os.path.exists(adapter_file):
            size_mb = os.path.getsize(adapter_file) / (1024 * 1024)
            print(f"✓ 適配器文件大小: {size_mb:.2f} MB")
            print(f"  相比完整模型（~500MB），適配器非常小！")

        return trainer

    except Exception as e:
        print(f"✗ 訓練失敗: {e}")
        import traceback
        traceback.print_exc()
        return None


def show_peft_info():
    """
    顯示 PEFT 框架信息
    """
    print("\n" + "=" * 60)
    print("PEFT 框架信息")
    print("=" * 60)

    try:
        import peft
        print(f"PEFT 版本: {peft.__version__}")

        print("\n支持的 PEFT 方法:")
        methods = [
            "LoRA (Low-Rank Adaptation) - 低秩適配",
            "Prefix Tuning - 前綴調優",
            "P-Tuning - 提示調優",
            "Prompt Tuning - 軟提示調優",
            "IA3 (Infused Adapter) - 注入式適配器",
            "AdaLoRA - 自適應 LoRA",
        ]
        for method in methods:
            print(f"  • {method}")

        print("\n核心優勢:")
        advantages = [
            "極低的參數量（< 1%）",
            "大幅降低顯存需求",
            "更快的訓練速度",
            "適配器文件很小（幾 MB）",
            "支持多適配器管理",
        ]
        for adv in advantages:
            print(f"  • {adv}")

    except Exception as e:
        print(f"獲取 PEFT 信息失敗: {e}")


def main():
    """
    主函數：執行完整的快速開始流程
    """
    print("=" * 60)
    print("PEFT 框架快速開始")
    print("=" * 60)

    # 1. 檢查依賴
    dependencies = check_dependencies()
    if not all(dependencies.values()):
        print("\n請先安裝所有必要的依賴包")
        return

    # 2. 顯示 PEFT 信息
    show_peft_info()

    # 3. 檢查設備
    device = get_device()

    # 4. 加載基礎模型
    print("\n提示: 首次運行會下載模型，可能需要幾分鐘...")
    model, tokenizer = load_base_model("gpt2")

    if model is None or tokenizer is None:
        print("模型加載失敗，退出程序")
        return

    # 5. 分析模型結構
    analyze_model_structure(model)

    # 6. 應用 LoRA
    peft_model = apply_lora(model)

    if peft_model is None:
        print("LoRA 應用失敗，退出程序")
        return

    # 將模型移到設備
    import torch
    peft_model = peft_model.to(device)

    # 7. 創建數據集
    dataset = create_sample_dataset()

    if dataset is None:
        print("數據集創建失敗，退出程序")
        return

    # 8. 訓練演示
    print("\n" + "=" * 60)
    print("注意: 這是一個快速演示，實際訓練需要更多數據")
    print("=" * 60)

    trainer = simple_training_demo(peft_model, tokenizer, dataset)

    # 9. 總結
    print("\n" + "=" * 60)
    print("快速開始完成！")
    print("=" * 60)
    print("\n主要收獲:")
    print("  ✓ 了解了 PEFT 的基本概念")
    print("  ✓ 學會了如何應用 LoRA")
    print("  ✓ 看到了可訓練參數的大幅減少")
    print("  ✓ 完成了一個簡單的訓練示例")

    print("\n接下來可以:")
    print("  1. 查看 02_LoRA基礎.py - 深入學習 LoRA 配置")
    print("  2. 查看 03_QLoRA配置.py - 學習量化微調")
    print("  3. 查看 04_Prefix_Tuning.py - 了解其他 PEFT 方法")
    print("  4. 查看其他示例文件，探索更多功能")

    print("\n資源:")
    print("  • 官方文檔: https://huggingface.co/docs/peft/")
    print("  • GitHub: https://github.com/huggingface/peft")
    print("  • LoRA 論文: https://arxiv.org/abs/2106.09685")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用戶中斷")
    except Exception as e:
        print(f"\n程序執行出錯: {e}")
        import traceback
        traceback.print_exc()
