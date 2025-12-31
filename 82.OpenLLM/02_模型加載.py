#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenLLM 模型加載示例
===================

本示例展示不同的模型加載方法，包括：
1. 從 HuggingFace Hub 加載模型
2. 從本地路徑加載模型
3. 加載不同類型的模型
4. 配置模型參數
5. 處理模型下載和緩存

適用場景：
- 了解各種模型加載方式
- 配置模型加載參數
- 管理本地模型緩存
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any


def load_from_huggingface():
    """
    從 HuggingFace Hub 加載模型

    展示如何從 HuggingFace Model Hub 加載各種預訓練模型
    """
    print("=" * 80)
    print("示例 1: 從 HuggingFace Hub 加載模型")
    print("=" * 80)

    try:
        import openllm

        # 不同模型的加載示例
        model_configs = [
            {
                "name": "Llama 2 7B Chat",
                "model_type": "llama",
                "model_id": "meta-llama/Llama-2-7b-chat-hf",
                "description": "Meta 的對話模型"
            },
            {
                "name": "Mistral 7B Instruct",
                "model_type": "mistral",
                "model_id": "mistralai/Mistral-7B-Instruct-v0.1",
                "description": "Mistral AI 的指令微調模型"
            },
            {
                "name": "Falcon 7B Instruct",
                "model_type": "falcon",
                "model_id": "tiiuae/falcon-7b-instruct",
                "description": "TII 的開源模型"
            },
            {
                "name": "OPT 125M",
                "model_type": "opt",
                "model_id": "facebook/opt-125m",
                "description": "小型測試模型"
            },
        ]

        print("\n支持的模型列表：")
        print("-" * 80)
        for i, config in enumerate(model_configs, 1):
            print(f"\n{i}. {config['name']}")
            print(f"   模型類型: {config['model_type']}")
            print(f"   模型 ID: {config['model_id']}")
            print(f"   說明: {config['description']}")

        # 實際加載一個小模型進行演示
        print("\n" + "-" * 80)
        print("演示加載: facebook/opt-125m")
        print("-" * 80)

        llm = openllm.LLM(
            model_name="opt",
            model_id="facebook/opt-125m",
            trust_remote_code=True,  # 信任遠程代碼
        )

        print("✓ 模型加載成功！")

        # 測試生成
        result = llm("Hello, I am", max_new_tokens=20)
        print(f"\n測試生成: {result}")

    except ImportError:
        print("✗ 錯誤: 需要安裝 openllm")
        print("運行: pip install openllm")
    except Exception as e:
        print(f"✗ 加載失敗: {str(e)}")
        print("\n💡 提示: 某些模型需要:")
        print("   1. HuggingFace 賬號授權")
        print("   2. 足夠的 GPU 內存")
        print("   3. 接受模型使用條款")


def load_from_local_path():
    """
    從本地路徑加載模型

    展示如何加載已下載到本地的模型
    """
    print("\n" + "=" * 80)
    print("示例 2: 從本地路徑加載模型")
    print("=" * 80)

    print("\n📝 從本地加載模型的步驟：")
    print("-" * 80)

    print("""
1. 下載模型到本地：

   from huggingface_hub import snapshot_download

   model_path = snapshot_download(
       repo_id="meta-llama/Llama-2-7b-chat-hf",
       cache_dir="./models"
   )

2. 加載本地模型：

   import openllm

   llm = openllm.LLM(
       model_name="llama",
       model_id="/path/to/local/model",  # 本地路徑
   )

3. 使用模型：

   result = llm("Your prompt here")
   print(result)
""")

    # 檢查常見的緩存位置
    print("\n檢查 HuggingFace 緩存位置：")
    print("-" * 80)

    cache_dirs = [
        Path.home() / ".cache" / "huggingface" / "hub",
        Path.home() / ".cache" / "huggingface" / "transformers",
        Path("./models"),
    ]

    for cache_dir in cache_dirs:
        exists = cache_dir.exists()
        print(f"{'✓' if exists else '✗'} {cache_dir}: {'存在' if exists else '不存在'}")

        if exists and cache_dir.is_dir():
            models = list(cache_dir.glob("models--*"))
            if models:
                print(f"   找到 {len(models)} 個緩存模型")
                for model in models[:3]:  # 只顯示前3個
                    print(f"   - {model.name}")


def load_with_custom_config():
    """
    使用自定義配置加載模型

    展示如何配置模型加載參數
    """
    print("\n" + "=" * 80)
    print("示例 3: 自定義配置加載")
    print("=" * 80)

    print("\n📝 配置選項說明：")
    print("-" * 80)

    config_example = '''
import openllm

# 完整配置示例
llm = openllm.LLM(
    # 基本配置
    model_name="llama",
    model_id="meta-llama/Llama-2-7b-chat-hf",

    # 設備配置
    device="cuda:0",              # 指定 GPU
    device_map="auto",            # 自動設備分配

    # 精度配置
    torch_dtype="float16",        # 使用 FP16
    load_in_8bit=False,           # 8-bit 量化
    load_in_4bit=False,           # 4-bit 量化

    # 內存優化
    low_cpu_mem_usage=True,       # 減少 CPU 內存使用
    max_memory=None,              # 最大內存限制

    # 安全選項
    trust_remote_code=True,       # 是否信任遠程代碼

    # 後端選擇
    backend="pt",                 # pytorch 後端
    # backend="vllm",             # vLLM 後端（更快）

    # 其他選項
    revision="main",              # 模型版本/分支
    cache_dir=None,               # 緩存目錄
)
'''

    print(config_example)

    try:
        import openllm

        print("\n實際演示 - 使用自定義配置：")
        print("-" * 80)

        # 使用較小的模型和基本配置
        llm = openllm.LLM(
            model_name="opt",
            model_id="facebook/opt-125m",
            trust_remote_code=True,
            low_cpu_mem_usage=True,
        )

        print("✓ 模型加載成功（使用自定義配置）")

        # 測試
        result = llm("AI is", max_new_tokens=25)
        print(f"\n生成結果: {result}")

    except Exception as e:
        print(f"✗ 錯誤: {str(e)}")


def load_quantized_models():
    """
    加載量化模型

    展示如何加載和使用量化模型以減少內存使用
    """
    print("\n" + "=" * 80)
    print("示例 4: 加載量化模型")
    print("=" * 80)

    print("\n📝 量化模型類型：")
    print("-" * 80)

    quantization_types = [
        {
            "type": "GPTQ (4-bit)",
            "example": "TheBloke/Llama-2-7B-Chat-GPTQ",
            "config": "quantization='gptq'",
            "memory_reduction": "~75%",
        },
        {
            "type": "AWQ (4-bit)",
            "example": "TheBloke/Llama-2-7B-Chat-AWQ",
            "config": "quantization='awq'",
            "memory_reduction": "~75%",
        },
        {
            "type": "GGML/GGUF",
            "example": "TheBloke/Llama-2-7B-Chat-GGML",
            "config": "backend='ggml'",
            "memory_reduction": "可變",
        },
        {
            "type": "bitsandbytes (8-bit)",
            "example": "meta-llama/Llama-2-7b-chat-hf",
            "config": "load_in_8bit=True",
            "memory_reduction": "~50%",
        },
    ]

    for i, quant in enumerate(quantization_types, 1):
        print(f"\n{i}. {quant['type']}")
        print(f"   示例模型: {quant['example']}")
        print(f"   配置: {quant['config']}")
        print(f"   內存減少: {quant['memory_reduction']}")

    print("\n\n代碼示例：")
    print("-" * 80)

    code_examples = '''
# 1. GPTQ 量化模型
llm = openllm.LLM(
    "llama",
    model_id="TheBloke/Llama-2-7B-Chat-GPTQ",
    quantization="gptq",
)

# 2. AWQ 量化模型
llm = openllm.LLM(
    "llama",
    model_id="TheBloke/Llama-2-7B-Chat-AWQ",
    quantization="awq",
)

# 3. 8-bit 量化（使用 bitsandbytes）
llm = openllm.LLM(
    "llama",
    model_id="meta-llama/Llama-2-7b-chat-hf",
    load_in_8bit=True,
)

# 4. 4-bit 量化（使用 bitsandbytes）
llm = openllm.LLM(
    "llama",
    model_id="meta-llama/Llama-2-7b-chat-hf",
    load_in_4bit=True,
)
'''

    print(code_examples)


def load_with_vllm_backend():
    """
    使用 vLLM 後端加載

    展示如何使用高性能的 vLLM 後端
    """
    print("\n" + "=" * 80)
    print("示例 5: 使用 vLLM 後端")
    print("=" * 80)

    print("\n📝 vLLM 後端優勢：")
    print("-" * 80)
    print("✓ 更快的推理速度（PagedAttention）")
    print("✓ 更高的吞吐量（連續批處理）")
    print("✓ 更好的內存管理")
    print("✓ 更低的延遲")

    print("\n使用方式：")
    print("-" * 80)

    vllm_example = '''
import openllm

# 方式 1: 在 LLM 初始化時指定後端
llm = openllm.LLM(
    "llama",
    model_id="meta-llama/Llama-2-7b-chat-hf",
    backend="vllm",  # 使用 vLLM 後端
)

# 方式 2: 通過環境變量指定
import os
os.environ["OPENLLM_BACKEND"] = "vllm"

llm = openllm.LLM(
    "llama",
    model_id="meta-llama/Llama-2-7b-chat-hf",
)

# vLLM 特定配置
llm = openllm.LLM(
    "llama",
    model_id="meta-llama/Llama-2-7b-chat-hf",
    backend="vllm",
    backend_config={
        "max_model_len": 4096,           # 最大序列長度
        "gpu_memory_utilization": 0.9,   # GPU 內存利用率
        "tensor_parallel_size": 1,       # 張量並行大小
    }
)
'''

    print(vllm_example)

    print("\n💡 注意：")
    print("   - 需要先安裝 vLLM: pip install vllm")
    print("   - vLLM 只支持 NVIDIA GPU")
    print("   - 某些模型可能不被 vLLM 支持")


def manage_model_cache():
    """
    管理模型緩存

    展示如何管理 HuggingFace 模型緩存
    """
    print("\n" + "=" * 80)
    print("示例 6: 管理模型緩存")
    print("=" * 80)

    try:
        from huggingface_hub import scan_cache_dir
        import humanize

        print("\n掃描 HuggingFace 緩存...")
        print("-" * 80)

        cache_info = scan_cache_dir()

        print(f"\n緩存位置: {cache_info.cache_dir}")
        print(f"倉庫數量: {len(cache_info.repos)}")

        total_size = sum(repo.size_on_disk for repo in cache_info.repos)
        print(f"總大小: {humanize.naturalsize(total_size)}")

        # 列出緩存的模型
        if cache_info.repos:
            print("\n緩存的模型:")
            for repo in list(cache_info.repos)[:5]:  # 只顯示前5個
                size = humanize.naturalsize(repo.size_on_disk)
                print(f"  - {repo.repo_id}: {size}")

        print("\n\n管理緩存的方法：")
        print("-" * 80)

        management_code = '''
# 1. 清理未使用的緩存
from huggingface_hub import scan_cache_dir

cache_info = scan_cache_dir()
strategy = cache_info.delete_revisions(
    # 刪除超過30天未使用的版本
    # lambda repo, revision: revision.last_modified < datetime.now() - timedelta(days=30)
)
print(f"將釋放: {strategy.expected_freed_size_str}")
# strategy.execute()  # 執行刪除

# 2. 手動刪除特定模型
import shutil
model_path = "/path/to/.cache/huggingface/hub/models--xxx"
shutil.rmtree(model_path)

# 3. 設置自定義緩存目錄
import os
os.environ["HF_HOME"] = "/custom/cache/dir"

# 或在代碼中指定
llm = openllm.LLM(
    "llama",
    model_id="meta-llama/Llama-2-7b-chat-hf",
    cache_dir="/custom/cache/dir"
)
'''

        print(management_code)

    except ImportError:
        print("✗ 需要安裝: pip install huggingface-hub humanize")
    except Exception as e:
        print(f"ℹ️  {str(e)}")


def main():
    """
    主函數：運行所有示例
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "OpenLLM 模型加載示例" + " " * 20 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    try:
        # 示例 1: 從 HuggingFace Hub 加載
        load_from_huggingface()

        # 示例 2: 從本地路徑加載
        load_from_local_path()

        # 示例 3: 自定義配置
        load_with_custom_config()

        # 示例 4: 量化模型
        load_quantized_models()

        # 示例 5: vLLM 後端
        load_with_vllm_backend()

        # 示例 6: 緩存管理
        manage_model_cache()

        print("\n" + "=" * 80)
        print("✓ 所有示例展示完成！")
        print("=" * 80)
        print("\n💡 關鍵要點：")
        print("   1. OpenLLM 支持多種模型加載方式")
        print("   2. 量化可以顯著減少內存使用")
        print("   3. vLLM 後端提供更好的性能")
        print("   4. 定期清理緩存可以節省磁盤空間")
        print()

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
