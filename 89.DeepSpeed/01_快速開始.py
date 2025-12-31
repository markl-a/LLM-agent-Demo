"""
DeepSpeed 快速開始示例

這個文件演示了 DeepSpeed 的基礎使用，包括：
1. 環境檢查和配置
2. 基礎模型訓練
3. ZeRO優化入門
4. 混合精度訓練
5. 檢查點保存和加載
"""

import os
import torch
import warnings

warnings.filterwarnings('ignore')


def check_deepspeed():
    """檢查 DeepSpeed 安裝"""
    print("=" * 70)
    print("檢查 DeepSpeed 環境")
    print("=" * 70)

    try:
        import deepspeed
        print(f"✓ DeepSpeed 版本: {deepspeed.__version__}")

        # 檢查 GPU
        if torch.cuda.is_available():
            print(f"✓ GPU 可用: {torch.cuda.get_device_name(0)}")
            print(f"  GPU 數量: {torch.cuda.device_count()}")
            print(f"  CUDA 版本: {torch.version.cuda}")
        else:
            print("✗ 未檢測到 GPU")

        # 運行環境報告
        print("\n運行 DeepSpeed 環境報告...")
        os.system("ds_report")

        return True
    except ImportError:
        print("✗ DeepSpeed 未安裝")
        print("請運行: pip install deepspeed")
        return False


def basic_deepspeed_config():
    """創建基礎 DeepSpeed 配置"""
    print("\n" + "=" * 70)
    print("基礎 DeepSpeed 配置")
    print("=" * 70)

    config = {
        "train_batch_size": 16,
        "gradient_accumulation_steps": 1,
        "optimizer": {
            "type": "AdamW",
            "params": {
                "lr": 3e-5,
                "betas": [0.9, 0.999],
                "eps": 1e-8,
                "weight_decay": 0.01
            }
        },
        "fp16": {
            "enabled": True,
            "loss_scale": 0,
            "initial_scale_power": 16
        },
        "zero_optimization": {
            "stage": 2,
            "allgather_partitions": True,
            "reduce_scatter": True,
            "overlap_comm": True,
            "contiguous_gradients": True
        }
    }

    print("\n配置詳情:")
    print(f"  批次大小: {config['train_batch_size']}")
    print(f"  梯度累積步數: {config['gradient_accumulation_steps']}")
    print(f"  混合精度: FP16")
    print(f"  ZeRO 階段: Stage {config['zero_optimization']['stage']}")
    print(f"  優化器: {config['optimizer']['type']}")
    print(f"  學習率: {config['optimizer']['params']['lr']}")

    return config


def training_example():
    """完整的訓練示例"""
    print("\n" + "=" * 70)
    print("DeepSpeed 訓練示例")
    print("=" * 70)

    print("""
完整的訓練代碼:

```python
import torch
import deepspeed
from transformers import AutoModelForCausalLM, AutoTokenizer, get_linear_schedule_with_warmup
from torch.utils.data import DataLoader, Dataset

# 1. 準備模型和數據
model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token

class TextDataset(Dataset):
    def __init__(self, texts):
        self.encodings = tokenizer(texts, truncation=True, padding=True, max_length=128)

    def __len__(self):
        return len(self.encodings.input_ids)

    def __getitem__(self, idx):
        return {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}

dataset = TextDataset(["示例文本 " + str(i) for i in range(100)])
dataloader = DataLoader(dataset, batch_size=4)

# 2. DeepSpeed 配置
ds_config = {
    "train_batch_size": 16,
    "gradient_accumulation_steps": 4,
    "fp16": {"enabled": True},
    "zero_optimization": {"stage": 2}
}

# 3. 初始化 DeepSpeed
model_engine, optimizer, _, lr_scheduler = deepspeed.initialize(
    model=model,
    config=ds_config
)

# 4. 訓練循環
model_engine.train()
for epoch in range(3):
    for batch in dataloader:
        batch = {k: v.to(model_engine.device) for k, v in batch.items()}

        outputs = model_engine(**batch, labels=batch['input_ids'])
        loss = outputs.loss

        model_engine.backward(loss)
        model_engine.step()

        print(f"Loss: {loss.item():.4f}")

# 5. 保存模型
model_engine.save_checkpoint('./checkpoints')
```
    """)


def main():
    """主函數"""
    print("=" * 70)
    print("DeepSpeed 快速開始")
    print("=" * 70)

    # 1. 環境檢查
    if not check_deepspeed():
        return

    # 2. 配置示例
    config = basic_deepspeed_config()

    # 3. 訓練示例
    training_example()

    # 4. 總結
    print("\n" * "=" * 70)
    print("總結")
    print("=" * 70)
    print("""
DeepSpeed 關鍵要點:

1. 核心優勢:
   ✓ ZeRO 優化 - 大幅降低顯存需求
   ✓ 混合精度 - 加速訓練
   ✓ 分佈式訓練 - 多 GPU/多節點
   ✓ 易於集成 - 支持 HuggingFace

2. 基本使用:
   ✓ 創建配置文件
   ✓ 使用 deepspeed.initialize()
   ✓ 替換 backward() 和 step()
   ✓ 保存檢查點

3. 下一步:
   • 查看 02_ZeRO優化.py - 深入 ZeRO
   • 查看 03_混合精度.py - 精度優化
   • 查看其他示例文件
    """)


if __name__ == "__main__":
    main()
