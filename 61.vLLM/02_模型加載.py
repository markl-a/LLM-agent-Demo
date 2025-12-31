#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
vLLM 模型加載示例
=================

本示例展示如何使用 vLLM 加載不同類型的模型，包括：
1. 從 HuggingFace Hub 加載模型
2. 從本地路徑加載模型
3. 加載不同架構的模型（GPT、LLaMA、Mistral 等）
4. 配置模型加載參數
5. 處理模型加載錯誤

適用場景：
- 使用各種預訓練模型
- 本地模型部署
- 自定義模型配置
"""

import os
import sys
from pathlib import Path
from typing import Optional
from vllm import LLM, SamplingParams


def load_from_huggingface():
    """
    從 HuggingFace Hub 加載模型

    展示如何直接從 HuggingFace 加載各種熱門模型
    """
    print("=" * 80)
    print("示例 1: 從 HuggingFace Hub 加載模型")
    print("=" * 80)

    try:
        # 加載小型 OPT 模型
        print("\n[1] 加載 facebook/opt-125m 模型...")
        llm = LLM(
            model="facebook/opt-125m",
            download_dir="/tmp/vllm_models",  # 指定下載目錄
            trust_remote_code=True,
        )
        print("✓ OPT-125M 模型加載成功！")

        # 測試推理
        sampling_params = SamplingParams(temperature=0.8, max_tokens=30)
        outputs = llm.generate(["Hello, I am"], sampling_params)
        print(f"生成結果: {outputs[0].outputs[0].text}")

        # 釋放資源
        del llm

        # 其他常見模型示例（註釋掉以節省資源）
        print("\n其他可加載的 HuggingFace 模型：")
        model_examples = [
            "facebook/opt-350m",           # OPT 系列
            "facebook/opt-1.3b",
            "EleutherAI/gpt-j-6b",         # GPT-J
            "EleutherAI/gpt-neox-20b",     # GPT-NeoX
            "meta-llama/Llama-2-7b-hf",    # LLaMA 2
            "meta-llama/Llama-2-13b-hf",
            "mistralai/Mistral-7B-v0.1",   # Mistral
            "mistralai/Mixtral-8x7B-v0.1", # Mixtral MoE
            "tiiuae/falcon-7b",            # Falcon
            "bigscience/bloom-560m",       # BLOOM
        ]

        for model_name in model_examples:
            print(f"  - {model_name}")

    except Exception as e:
        print(f"✗ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


def load_from_local_path():
    """
    從本地路徑加載模型

    展示如何加載本地存儲的模型文件
    """
    print("\n" + "=" * 80)
    print("示例 2: 從本地路徑加載模型")
    print("=" * 80)

    try:
        # 假設模型已經下載到本地
        # 實際使用時，需要先下載模型到本地目錄

        local_model_path = "/path/to/local/model"  # 替換為實際路徑

        # 檢查路徑是否存在
        if not os.path.exists(local_model_path):
            print(f"\n⚠ 本地模型路徑不存在: {local_model_path}")
            print("請先下載模型到本地，或使用以下命令：")
            print("  from transformers import AutoModel")
            print("  model = AutoModel.from_pretrained('model_name')")
            print("  model.save_pretrained('/path/to/local/model')")
            return

        print(f"\n正在從本地加載模型: {local_model_path}")
        llm = LLM(
            model=local_model_path,
            trust_remote_code=True,
        )
        print("✓ 本地模型加載成功！")

        # 測試推理
        sampling_params = SamplingParams(temperature=0.8, max_tokens=50)
        outputs = llm.generate(["Once upon a time"], sampling_params)
        print(f"\n生成結果: {outputs[0].outputs[0].text}")

    except Exception as e:
        print(f"✗ 錯誤: {str(e)}")


def load_with_custom_config():
    """
    使用自定義配置加載模型

    展示各種模型加載配置選項
    """
    print("\n" + "=" * 80)
    print("示例 3: 自定義配置加載模型")
    print("=" * 80)

    try:
        print("\n正在加載模型（自定義配置）...")

        llm = LLM(
            model="facebook/opt-125m",

            # 張量並行配置
            tensor_parallel_size=1,  # 使用的 GPU 數量

            # 數據類型
            dtype="auto",  # 可選: "auto", "float16", "bfloat16", "float32"

            # KV Cache 配置
            max_model_len=None,  # 最大序列長度（None 表示使用模型默認值）

            # 內存管理
            gpu_memory_utilization=0.9,  # GPU 內存使用率（0.0-1.0）
            swap_space=4,  # CPU swap 空間（GB）

            # 信任遠程代碼
            trust_remote_code=True,

            # 下載配置
            download_dir="/tmp/vllm_models",
            revision="main",  # 模型版本/分支

            # 量化（如果支持）
            # quantization="awq",  # 可選: "awq", "gptq"

            # 執行配置
            enforce_eager=False,  # 是否使用 eager 模式（調試用）
        )

        print("✓ 模型加載成功！")
        print("\n模型配置信息：")
        print(f"  - 張量並行大小: 1")
        print(f"  - GPU 內存利用率: 90%")
        print(f"  - Swap 空間: 4GB")

        # 測試推理
        sampling_params = SamplingParams(temperature=0.7, max_tokens=40)
        outputs = llm.generate(["The meaning of life is"], sampling_params)
        print(f"\n生成結果: {outputs[0].outputs[0].text}")

    except Exception as e:
        print(f"✗ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


def load_different_architectures():
    """
    加載不同架構的模型

    展示 vLLM 支持的各種模型架構
    """
    print("\n" + "=" * 80)
    print("示例 4: 加載不同架構的模型")
    print("=" * 80)

    # 定義不同架構的模型（選擇較小的模型進行演示）
    models_to_test = [
        {
            "name": "OPT (Meta)",
            "model_id": "facebook/opt-125m",
            "description": "Meta 的開源預訓練 Transformer 模型"
        },
        # 以下模型較大，註釋掉以節省資源
        # {
        #     "name": "GPT-2",
        #     "model_id": "gpt2",
        #     "description": "OpenAI 的經典生成式模型"
        # },
        # {
        #     "name": "BLOOM",
        #     "model_id": "bigscience/bloom-560m",
        #     "description": "多語言大型語言模型"
        # },
    ]

    for model_info in models_to_test:
        print(f"\n{'-' * 80}")
        print(f"模型: {model_info['name']}")
        print(f"ID: {model_info['model_id']}")
        print(f"描述: {model_info['description']}")
        print(f"{'-' * 80}")

        try:
            print(f"正在加載 {model_info['name']}...")

            llm = LLM(
                model=model_info['model_id'],
                trust_remote_code=True,
                download_dir="/tmp/vllm_models",
            )

            print(f"✓ {model_info['name']} 加載成功！")

            # 測試推理
            sampling_params = SamplingParams(
                temperature=0.8,
                max_tokens=30,
            )

            prompt = "Artificial Intelligence will"
            outputs = llm.generate([prompt], sampling_params)

            print(f"提示詞: {prompt}")
            print(f"生成: {outputs[0].outputs[0].text}")

            # 清理資源
            del llm

        except Exception as e:
            print(f"✗ 加載 {model_info['name']} 失敗: {str(e)}")


def load_with_tokenizer_config():
    """
    自定義 Tokenizer 配置

    展示如何配置 tokenizer 相關選項
    """
    print("\n" + "=" * 80)
    print("示例 5: 自定義 Tokenizer 配置")
    print("=" * 80)

    try:
        print("\n正在加載模型...")

        llm = LLM(
            model="facebook/opt-125m",
            tokenizer="facebook/opt-125m",  # 可以使用不同的 tokenizer
            trust_remote_code=True,

            # Tokenizer 配置
            tokenizer_mode="auto",  # 可選: "auto", "slow"
            # skip_tokenizer_init=False,  # 是否跳過 tokenizer 初始化
        )

        print("✓ 模型和 Tokenizer 加載成功！")

        # 測試不同的提示詞
        prompts = [
            "Hello, world!",
            "你好，世界！",  # 中文
            "Bonjour le monde!",  # 法文
        ]

        sampling_params = SamplingParams(temperature=0.8, max_tokens=20)

        print("\n測試多語言輸入：")
        for i, prompt in enumerate(prompts):
            outputs = llm.generate([prompt], sampling_params)
            print(f"\n[{i+1}] 輸入: {prompt}")
            print(f"    輸出: {outputs[0].outputs[0].text}")

    except Exception as e:
        print(f"✗ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


def handle_loading_errors():
    """
    處理模型加載錯誤

    展示常見的加載錯誤及處理方法
    """
    print("\n" + "=" * 80)
    print("示例 6: 錯誤處理")
    print("=" * 80)

    # 錯誤 1: 模型不存在
    print("\n[1] 測試加載不存在的模型...")
    try:
        llm = LLM(model="nonexistent/model-123")
    except Exception as e:
        print(f"✓ 捕獲預期錯誤: {type(e).__name__}")
        print(f"   錯誤信息: {str(e)[:100]}...")

    # 錯誤 2: GPU 內存不足
    print("\n[2] GPU 內存不足的處理建議：")
    print("   - 減少 gpu_memory_utilization 參數（如 0.8 或 0.7）")
    print("   - 使用量化模型（AWQ, GPTQ）")
    print("   - 增加 tensor_parallel_size（使用多 GPU）")
    print("   - 減少 max_model_len")

    # 錯誤 3: 不支持的模型架構
    print("\n[3] 檢查模型是否支持：")
    print("   訪問 https://docs.vllm.ai/en/latest/models/supported_models.html")
    print("   查看 vLLM 支持的模型列表")

    # 正確的錯誤處理示例
    print("\n[4] 推薦的加載模式（帶錯誤處理）：")
    print("-" * 80)

    def safe_load_model(model_name: str, **kwargs) -> Optional[LLM]:
        """安全地加載模型"""
        try:
            print(f"正在加載模型: {model_name}")
            llm = LLM(model=model_name, **kwargs)
            print(f"✓ 模型加載成功")
            return llm
        except FileNotFoundError as e:
            print(f"✗ 模型文件未找到: {e}")
            return None
        except RuntimeError as e:
            print(f"✗ 運行時錯誤（可能是內存不足）: {e}")
            return None
        except Exception as e:
            print(f"✗ 未知錯誤: {type(e).__name__}: {e}")
            return None

    # 使用安全加載
    llm = safe_load_model(
        "facebook/opt-125m",
        trust_remote_code=True,
        gpu_memory_utilization=0.8,
    )

    if llm is not None:
        print("\n測試模型推理...")
        sampling_params = SamplingParams(temperature=0.8, max_tokens=20)
        outputs = llm.generate(["Test prompt"], sampling_params)
        print(f"生成結果: {outputs[0].outputs[0].text}")


def check_system_requirements():
    """
    檢查系統要求

    驗證系統是否滿足運行 vLLM 的要求
    """
    print("\n" + "=" * 80)
    print("系統要求檢查")
    print("=" * 80)

    try:
        import torch
        import vllm

        print(f"\n✓ vLLM 版本: {vllm.__version__}")
        print(f"✓ PyTorch 版本: {torch.__version__}")

        # 檢查 CUDA
        if torch.cuda.is_available():
            print(f"✓ CUDA 可用")
            print(f"  - CUDA 版本: {torch.version.cuda}")
            print(f"  - GPU 數量: {torch.cuda.device_count()}")

            for i in range(torch.cuda.device_count()):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1e9
                print(f"  - GPU {i}: {gpu_name} ({gpu_memory:.2f} GB)")

            # 檢查計算能力
            compute_capability = torch.cuda.get_device_capability(0)
            print(f"  - 計算能力: {compute_capability[0]}.{compute_capability[1]}")

            if compute_capability[0] < 7:
                print("  ⚠ 警告: GPU 計算能力較低，建議使用 7.0 或更高")
        else:
            print("✗ CUDA 不可用")
            print("  vLLM 需要 NVIDIA GPU 支持")

    except ImportError as e:
        print(f"✗ 缺少必要的依賴: {e}")


def main():
    """
    主函數：運行所有示例
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 25 + "vLLM 模型加載示例" + " " * 25 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    # 首先檢查系統要求
    check_system_requirements()

    print("\n")

    try:
        # 示例 1: 從 HuggingFace 加載
        load_from_huggingface()

        # 示例 2: 從本地路徑加載
        # load_from_local_path()  # 需要本地模型文件

        # 示例 3: 自定義配置
        load_with_custom_config()

        # 示例 4: 不同架構
        load_different_architectures()

        # 示例 5: Tokenizer 配置
        load_with_tokenizer_config()

        # 示例 6: 錯誤處理
        handle_loading_errors()

        print("\n" + "=" * 80)
        print("✓ 所有示例運行完成！")
        print("=" * 80)

        # 使用建議
        print("\n使用建議：")
        print("  1. 首次使用建議從小模型開始（如 OPT-125M）")
        print("  2. 根據 GPU 內存選擇合適的模型大小")
        print("  3. 使用量化模型可以減少內存佔用")
        print("  4. 生產環境建議設置 download_dir 避免重複下載")
        print("  5. 使用 trust_remote_code=True 時注意安全性")

    except KeyboardInterrupt:
        print("\n\n程序被用戶中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ 運行出錯: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
