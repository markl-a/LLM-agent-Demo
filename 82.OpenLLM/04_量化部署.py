#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenLLM 量化部署示例
==================

本示例展示模型量化和部署，包括：
1. GPTQ 量化模型部署
2. AWQ 量化模型部署
3. bitsandbytes 量化
4. GGML/GGUF 格式
5. 量化效果對比
6. 性能優化建議

適用場景：
- 減少內存佔用
- 在有限資源上部署大模型
- 平衡性能和資源消耗
"""

import sys
from typing import Dict, List, Any


def gptq_quantization():
    """
    GPTQ 量化部署

    GPTQ 是一種後訓練量化方法，可將模型壓縮到 4-bit
    """
    print("=" * 80)
    print("示例 1: GPTQ 量化部署")
    print("=" * 80)

    print("\n📝 GPTQ 量化介紹：")
    print("-" * 80)
    print("✓ 4-bit 量化，內存減少約 75%")
    print("✓ 精度損失小於 1%")
    print("✓ 支持大部分主流模型")
    print("✓ 需要 GPU 推理")

    print("\n\nCLI 部署命令：")
    print("-" * 80)

    cli_commands = '''
# 啟動 GPTQ 量化的 Llama 2 模型
openllm start llama \\
  --model-id TheBloke/Llama-2-7B-Chat-GPTQ \\
  --quantization gptq

# 指定 GPTQ 配置
openllm start llama \\
  --model-id TheBloke/Llama-2-13B-Chat-GPTQ \\
  --quantization gptq \\
  --device cuda:0
'''

    print(cli_commands)

    print("\nPython API 使用：")
    print("-" * 80)

    python_code = '''
import openllm

# 加載 GPTQ 量化模型
llm = openllm.LLM(
    "llama",
    model_id="TheBloke/Llama-2-7B-Chat-GPTQ",
    quantization="gptq",
    device="cuda:0",
)

# 推理
prompt = "What is quantum computing?"
result = llm(prompt, max_new_tokens=200)
print(result)

# 也可以使用其他 GPTQ 模型
models = [
    "TheBloke/Mistral-7B-Instruct-v0.1-GPTQ",
    "TheBloke/CodeLlama-13B-Instruct-GPTQ",
    "TheBloke/Falcon-7B-Instruct-GPTQ",
]
'''

    print(python_code)

    print("\n常用 GPTQ 模型：")
    print("-" * 80)

    models = [
        "TheBloke/Llama-2-7B-Chat-GPTQ",
        "TheBloke/Llama-2-13B-Chat-GPTQ",
        "TheBloke/Mistral-7B-Instruct-v0.1-GPTQ",
        "TheBloke/CodeLlama-13B-Instruct-GPTQ",
    ]

    for model in models:
        print(f"  • {model}")


def awq_quantization():
    """
    AWQ 量化部署

    AWQ (Activation-aware Weight Quantization) 是另一種優秀的量化方法
    """
    print("\n" + "=" * 80)
    print("示例 2: AWQ 量化部署")
    print("=" * 80)

    print("\n📝 AWQ 量化介紹：")
    print("-" * 80)
    print("✓ 4-bit 量化，內存減少約 75%")
    print("✓ 保持更高的精度")
    print("✓ 推理速度更快")
    print("✓ 對激活值敏感的權重保護")

    print("\n\nCLI 部署：")
    print("-" * 80)

    cli_code = '''
# 啟動 AWQ 量化模型
openllm start llama \\
  --model-id TheBloke/Llama-2-7B-Chat-AWQ \\
  --quantization awq \\
  --backend vllm  # vLLM 對 AWQ 支持更好

# Mistral AWQ
openllm start mistral \\
  --model-id TheBloke/Mistral-7B-Instruct-v0.1-AWQ \\
  --quantization awq
'''

    print(cli_code)

    print("\nPython API：")
    print("-" * 80)

    python_code = '''
import openllm

# 加載 AWQ 量化模型
llm = openllm.LLM(
    "llama",
    model_id="TheBloke/Llama-2-7B-Chat-AWQ",
    quantization="awq",
    backend="vllm",  # 推薦使用 vLLM 後端
)

# 推理
result = llm(
    "Explain artificial intelligence",
    max_new_tokens=150,
    temperature=0.7,
)

print(result)
'''

    print(python_code)

    print("\n\nAWQ vs GPTQ 對比：")
    print("-" * 80)

    comparison = '''
特性          AWQ                GPTQ
────────────────────────────────────────
壓縮率        4-bit (75%)        4-bit (75%)
精度          優秀               良好
速度          更快               快
內存          相同               相同
易用性        簡單               簡單
模型支持      廣泛               廣泛
推薦場景      性能優先           通用場景
'''

    print(comparison)


def bitsandbytes_quantization():
    """
    bitsandbytes 量化

    使用 bitsandbytes 庫進行動態量化
    """
    print("\n" + "=" * 80)
    print("示例 3: bitsandbytes 量化")
    print("=" * 80)

    print("\n📝 bitsandbytes 量化類型：")
    print("-" * 80)
    print("• INT8 量化: 8-bit，內存減少 50%")
    print("• INT4 量化: 4-bit，內存減少 75%")
    print("• 支持任何 HuggingFace 模型")
    print("• 無需預量化模型")

    print("\n\n8-bit 量化示例：")
    print("-" * 80)

    int8_code = '''
import openllm

# 8-bit 量化
llm = openllm.LLM(
    "llama",
    model_id="meta-llama/Llama-2-7b-chat-hf",
    load_in_8bit=True,  # 啟用 8-bit 量化
    device_map="auto",  # 自動設備分配
)

# 推理
result = llm("Hello, how are you?", max_new_tokens=50)
print(result)
'''

    print(int8_code)

    print("\n4-bit 量化示例（NF4）：")
    print("-" * 80)

    int4_code = '''
import openllm

# 4-bit 量化（使用 NF4）
llm = openllm.LLM(
    "llama",
    model_id="meta-llama/Llama-2-7b-chat-hf",
    load_in_4bit=True,  # 啟用 4-bit 量化
    bnb_4bit_quant_type="nf4",  # NormalFloat4
    bnb_4bit_compute_dtype="float16",
    bnb_4bit_use_double_quant=True,  # 嵌套量化
)

result = llm("What is machine learning?", max_new_tokens=100)
print(result)
'''

    print(int4_code)

    print("\nCLI 使用：")
    print("-" * 80)

    cli_code = '''
# 8-bit 量化
openllm start llama \\
  --model-id meta-llama/Llama-2-7b-chat-hf \\
  --quantization int8

# 4-bit 量化
openllm start llama \\
  --model-id meta-llama/Llama-2-7b-chat-hf \\
  --quantization int4
'''

    print(cli_code)


def ggml_gguf_format():
    """
    GGML/GGUF 格式

    GGML 格式主要用於 CPU 推理
    """
    print("\n" + "=" * 80)
    print("示例 4: GGML/GGUF 格式")
    print("=" * 80)

    print("\n📝 GGML/GGUF 介紹：")
    print("-" * 80)
    print("✓ 為 CPU 推理優化")
    print("✓ 支持多種量化級別（Q2_K 到 Q8_0）")
    print("✓ 內存效率極高")
    print("✓ llama.cpp 原生格式")

    print("\n\n常見量化級別：")
    print("-" * 80)

    quant_levels = [
        ("Q2_K", "2-bit", "最小內存，精度較低"),
        ("Q3_K_M", "3-bit", "平衡"),
        ("Q4_K_M", "4-bit", "推薦日常使用"),
        ("Q5_K_M", "5-bit", "高質量"),
        ("Q6_K", "6-bit", "接近原始精度"),
        ("Q8_0", "8-bit", "最高精度"),
    ]

    for name, bits, desc in quant_levels:
        print(f"{name:10} {bits:8} - {desc}")

    print("\n\n使用示例：")
    print("-" * 80)

    usage_code = '''
# 使用 GGUF 格式需要 llama-cpp-python 或 ctransformers 後端
# 安裝: pip install openllm[ggml]

import openllm

# 加載 GGUF 模型
llm = openllm.LLM(
    "llama",
    model_id="TheBloke/Llama-2-7B-Chat-GGUF",
    backend="ctransformers",  # 或 "llama-cpp"
    model_file="llama-2-7b-chat.Q4_K_M.gguf",  # 指定具體文件
)

# CPU 推理
result = llm(
    "Explain the universe",
    max_new_tokens=100,
    temperature=0.7,
)

print(result)
'''

    print(usage_code)

    print("\nCLI 使用：")
    print("-" * 80)

    cli_code = '''
openllm start llama \\
  --model-id TheBloke/Llama-2-7B-Chat-GGUF \\
  --backend ctransformers \\
  --model-file llama-2-7b-chat.Q4_K_M.gguf
'''

    print(cli_code)


def quantization_comparison():
    """
    量化方法對比

    展示不同量化方法的性能和資源對比
    """
    print("\n" + "=" * 80)
    print("示例 5: 量化方法對比")
    print("=" * 80)

    print("\n📊 內存佔用對比（Llama-2-7B）：")
    print("-" * 80)

    comparison_data = [
        ("FP16 原始", "~14 GB", "100%", "基準"),
        ("GPTQ 4-bit", "~3.5 GB", "25%", "快"),
        ("AWQ 4-bit", "~3.5 GB", "25%", "更快"),
        ("INT8 (bnb)", "~7 GB", "50%", "中等"),
        ("INT4 (bnb)", "~3.5 GB", "25%", "快"),
        ("GGUF Q4_K_M", "~4 GB", "28%", "CPU 優化"),
    ]

    print(f"{'方法':<15} {'內存':<12} {'相對大小':<10} {'推理速度'}")
    print("-" * 60)
    for method, memory, relative, speed in comparison_data:
        print(f"{method:<15} {memory:<12} {relative:<10} {speed}")

    print("\n\n📊 精度對比：")
    print("-" * 80)

    accuracy_data = [
        ("FP16", "100%", "基準"),
        ("AWQ 4-bit", "99.5%", "最佳量化精度"),
        ("GPTQ 4-bit", "99.2%", "優秀"),
        ("INT8", "99.8%", "接近原始"),
        ("INT4 NF4", "99.0%", "良好"),
        ("GGUF Q4_K_M", "98.5%", "可接受"),
    ]

    print(f"{'方法':<15} {'相對精度':<12} {'說明'}")
    print("-" * 50)
    for method, accuracy, desc in accuracy_data:
        print(f"{method:<15} {accuracy:<12} {desc}")


def deployment_recommendations():
    """
    部署建議

    根據不同場景提供量化建議
    """
    print("\n" + "=" * 80)
    print("示例 6: 部署建議")
    print("=" * 80)

    print("\n📝 場景推薦：")
    print("-" * 80)

    scenarios = [
        {
            "scene": "生產環境 GPU 服務器",
            "recommendation": "AWQ 4-bit + vLLM 後端",
            "reason": "最佳性能和精度平衡"
        },
        {
            "scene": "有限 GPU 內存（<12GB）",
            "recommendation": "GPTQ 4-bit",
            "reason": "內存效率高，廣泛支持"
        },
        {
            "scene": "快速原型和測試",
            "recommendation": "INT8 bitsandbytes",
            "reason": "無需預量化，即插即用"
        },
        {
            "scene": "CPU 推理",
            "recommendation": "GGUF Q4_K_M",
            "reason": "CPU 優化，內存效率高"
        },
        {
            "scene": "邊緣設備",
            "recommendation": "GGUF Q2_K/Q3_K",
            "reason": "極小內存佔用"
        },
        {
            "scene": "精度優先",
            "recommendation": "INT8 或 AWQ",
            "reason": "精度損失最小"
        },
    ]

    for scenario in scenarios:
        print(f"\n場景: {scenario['scene']}")
        print(f"  推薦: {scenario['recommendation']}")
        print(f"  原因: {scenario['reason']}")

    print("\n\n💡 最佳實踐：")
    print("-" * 80)

    best_practices = [
        "先測試量化效果，選擇最適合的方法",
        "使用 vLLM 後端可獲得最佳性能",
        "監控精度損失，確保滿足業務需求",
        "考慮批處理大小和吞吐量需求",
        "定期更新到最新的量化模型",
    ]

    for i, practice in enumerate(best_practices, 1):
        print(f"{i}. {practice}")

    print("\n\n完整示例：")
    print("-" * 80)

    complete_example = '''
# 生產環境部署配置（推薦）
openllm start llama \\
  --model-id TheBloke/Llama-2-7B-Chat-AWQ \\
  --quantization awq \\
  --backend vllm \\
  --device cuda:0 \\
  --port 3000 \\
  --workers 1 \\
  --cors

# Python 配置
import openllm

llm = openllm.LLM(
    "llama",
    model_id="TheBloke/Llama-2-7B-Chat-AWQ",
    quantization="awq",
    backend="vllm",
    backend_config={
        "max_model_len": 4096,
        "gpu_memory_utilization": 0.9,
    }
)

# 啟動服務
llm.serve(host="0.0.0.0", port=3000)
'''

    print(complete_example)


def main():
    """
    主函數：運行所有示例
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "OpenLLM 量化部署示例" + " " * 20 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    try:
        # 示例 1: GPTQ 量化
        gptq_quantization()

        # 示例 2: AWQ 量化
        awq_quantization()

        # 示例 3: bitsandbytes
        bitsandbytes_quantization()

        # 示例 4: GGML/GGUF
        ggml_gguf_format()

        # 示例 5: 對比
        quantization_comparison()

        # 示例 6: 建議
        deployment_recommendations()

        print("\n" + "=" * 80)
        print("✓ 所有示例展示完成！")
        print("=" * 80)
        print("\n💡 關鍵要點：")
        print("   1. 量化可減少 50-75% 內存使用")
        print("   2. AWQ 提供最佳的性能和精度平衡")
        print("   3. 根據硬件和場景選擇合適的量化方法")
        print("   4. 配合 vLLM 後端獲得最佳性能")
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
