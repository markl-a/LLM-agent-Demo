#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenLLM 批量處理示例
==================

本示例展示批量推理處理，包括：
1. 批量文本生成
2. 並發處理優化
3. 批處理配置
4. 性能監控
5. 大規模數據處理

適用場景：
- 批量數據標註
- 離線內容生成
- 數據集處理
"""

import sys
import time
import asyncio
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed


def basic_batch_processing():
    """
    基本批量處理

    展示如何批量處理多個提示詞
    """
    print("=" * 80)
    print("示例 1: 基本批量處理")
    print("=" * 80)

    code_example = '''
import openllm

# 加載模型
llm = openllm.LLM("opt", model_id="facebook/opt-125m")

# 準備批量提示詞
prompts = [
    "The future of AI is",
    "Machine learning helps us",
    "Python programming is",
    "Deep learning enables",
    "Natural language processing allows",
]

# 批量生成
print("批量處理中...")
results = []

for i, prompt in enumerate(prompts):
    print(f"處理 {i+1}/{len(prompts)}: {prompt}")
    result = llm(prompt, max_new_tokens=50)
    results.append({
        "prompt": prompt,
        "result": result,
    })

# 顯示結果
for i, item in enumerate(results, 1):
    print(f"\\n[{i}] {item['prompt']}")
    print(f"    {item['result']}")
'''

    print(code_example)

    print("\n實際演示：")
    print("-" * 80)

    try:
        import openllm

        llm = openllm.LLM("opt", model_id="facebook/opt-125m")

        prompts = [
            "AI is",
            "Technology enables",
            "The future will",
        ]

        print(f"批量處理 {len(prompts)} 個提示詞...\n")
        results = []

        for i, prompt in enumerate(prompts):
            start = time.time()
            result = llm(prompt, max_new_tokens=30)
            elapsed = time.time() - start

            results.append(result)
            print(f"[{i+1}] {prompt}: {result} ({elapsed:.2f}s)")

        print(f"\n✓ 批量處理完成，共 {len(results)} 個結果")

    except Exception as e:
        print(f"ℹ️  演示跳過: {str(e)}")


def concurrent_batch_processing():
    """
    並發批量處理

    使用多線程/異步提高批處理效率
    """
    print("\n" + "=" * 80)
    print("示例 2: 並發批量處理")
    print("=" * 80)

    print("\n📝 多線程並發：")
    print("-" * 80)

    threading_code = '''
from concurrent.futures import ThreadPoolExecutor, as_completed
import openllm

llm = openllm.LLM("llama", model_id="meta-llama/Llama-2-7b-chat-hf")

prompts = [f"Question {i}: What is AI?" for i in range(10)]

def process_prompt(prompt):
    """處理單個提示詞"""
    result = llm(prompt, max_new_tokens=100)
    return {"prompt": prompt, "result": result}

# 使用線程池並發處理
with ThreadPoolExecutor(max_workers=4) as executor:
    # 提交所有任務
    futures = [executor.submit(process_prompt, p) for p in prompts]

    # 收集結果
    results = []
    for future in as_completed(futures):
        try:
            result = future.result()
            results.append(result)
            print(f"✓ 完成: {result['prompt'][:30]}...")
        except Exception as e:
            print(f"✗ 錯誤: {e}")

print(f"\\n完成 {len(results)} 個任務")
'''

    print(threading_code)

    print("\n異步並發：")
    print("-" * 80)

    async_code = '''
import asyncio
import openllm

async def process_batch_async(llm, prompts):
    """異步批量處理"""
    async def process_one(prompt):
        # 使用 run_in_executor 讓同步調用變成異步
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            llm,
            prompt,
        )
        return {"prompt": prompt, "result": result}

    # 並發執行所有任務
    tasks = [process_one(p) for p in prompts]
    results = await asyncio.gather(*tasks)

    return results

# 使用
llm = openllm.LLM("llama", model_id="meta-llama/Llama-2-7b-chat-hf")
prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]

results = asyncio.run(process_batch_async(llm, prompts))
'''

    print(async_code)


def batch_api_usage():
    """
    批量 API 使用

    展示如何通過 API 進行批量處理
    """
    print("\n" + "=" * 80)
    print("示例 3: 批量 API 使用")
    print("=" * 80)

    print("\n📝 HTTP API 批量請求：")
    print("-" * 80)

    api_code = '''
import requests
from concurrent.futures import ThreadPoolExecutor

API_URL = "http://localhost:3000/v1/generate"

def generate_one(prompt):
    """單個 API 請求"""
    response = requests.post(
        API_URL,
        json={
            "prompt": prompt,
            "max_new_tokens": 100,
            "temperature": 0.7,
        },
        timeout=30,
    )
    return response.json()

# 批量提示詞
prompts = [
    "What is machine learning?",
    "Explain quantum computing",
    "Describe artificial intelligence",
]

# 並發請求
with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(generate_one, prompts))

# 處理結果
for prompt, result in zip(prompts, results):
    print(f"Prompt: {prompt}")
    print(f"Result: {result.get('text', '')[:100]}...")
    print()
'''

    print(api_code)

    print("\n使用 OpenAI 客戶端批量：")
    print("-" * 80)

    openai_code = '''
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor

client = OpenAI(
    base_url="http://localhost:3000/v1",
    api_key="not-needed",
)

def chat_completion(message):
    """單個聊天完成請求"""
    response = client.chat.completions.create(
        model="llama",
        messages=[{"role": "user", "content": message}],
        max_tokens=100,
    )
    return response.choices[0].message.content

# 批量消息
messages = [
    "What is AI?",
    "Explain ML",
    "Describe NLP",
]

# 並發處理
with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(chat_completion, messages))

for msg, result in zip(messages, results):
    print(f"Q: {msg}")
    print(f"A: {result}\\n")
'''

    print(openai_code)


def batch_configuration():
    """
    批處理配置

    展示如何配置批處理參數以優化性能
    """
    print("\n" + "=" * 80)
    print("示例 4: 批處理配置")
    print("=" * 80)

    print("\n📝 vLLM 後端批處理配置：")
    print("-" * 80)

    vllm_config = '''
import openllm

# 使用 vLLM 後端並配置批處理
llm = openllm.LLM(
    "llama",
    model_id="meta-llama/Llama-2-7b-chat-hf",
    backend="vllm",
    backend_config={
        # 批處理配置
        "max_num_seqs": 256,              # 最大並發序列數
        "max_num_batched_tokens": 4096,   # 批處理最大 token 數

        # 性能配置
        "gpu_memory_utilization": 0.9,
        "max_model_len": 4096,

        # 調度配置
        "swap_space": 4,  # GB
    }
)

# 批量處理
prompts = [f"Prompt {i}" for i in range(100)]
results = [llm(p, max_new_tokens=100) for p in prompts]
'''

    print(vllm_config)

    print("\nCLI 批處理配置：")
    print("-" * 80)

    cli_config = '''
# 啟動服務時配置批處理參數
openllm start llama \\
  --model-id meta-llama/Llama-2-7b-chat-hf \\
  --backend vllm \\
  --max-num-seqs 256 \\
  --max-num-batched-tokens 4096 \\
  --gpu-memory-utilization 0.9
'''

    print(cli_config)

    print("\n配置文件（YAML）：")
    print("-" * 80)

    yaml_config = '''
# config.yaml
model_name: llama
model_id: meta-llama/Llama-2-7b-chat-hf

backend: vllm
backend_config:
  # 批處理配置
  max_num_seqs: 256
  max_num_batched_tokens: 4096

  # 調度策略
  scheduling_policy: "fcfs"  # First Come First Serve

  # 性能
  gpu_memory_utilization: 0.9
  max_model_len: 4096
'''

    print(yaml_config)


def performance_monitoring():
    """
    性能監控

    監控批處理性能和資源使用
    """
    print("\n" + "=" * 80)
    print("示例 5: 性能監控")
    print("=" * 80)

    print("\n📝 基本性能統計：")
    print("-" * 80)

    monitoring_code = '''
import time
import openllm
from statistics import mean, stdev

llm = openllm.LLM("opt", model_id="facebook/opt-125m")

# 準備測試數據
prompts = [f"Test prompt {i}" for i in range(20)]

# 性能統計
latencies = []
throughputs = []

print("開始性能測試...")

for i, prompt in enumerate(prompts):
    start = time.time()

    result = llm(prompt, max_new_tokens=50)

    # 計算延遲
    latency = time.time() - start
    latencies.append(latency)

    # 計算吞吐量（tokens/s）
    # 假設平均生成 50 個 token
    throughput = 50 / latency
    throughputs.append(throughput)

    if (i + 1) % 5 == 0:
        print(f"處理 {i+1}/{len(prompts)} 個請求...")

# 統計結果
print(f"\\n性能統計:")
print(f"  總請求數: {len(prompts)}")
print(f"  平均延遲: {mean(latencies):.2f}s")
print(f"  延遲標準差: {stdev(latencies):.2f}s")
print(f"  最小延遲: {min(latencies):.2f}s")
print(f"  最大延遲: {max(latencies):.2f}s")
print(f"  平均吞吐量: {mean(throughputs):.2f} tokens/s")
'''

    print(monitoring_code)

    print("\nGPU 使用監控：")
    print("-" * 80)

    gpu_monitoring = '''
import torch
import openllm

def monitor_gpu_usage():
    """監控 GPU 使用情況"""
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            print(f"GPU {i}:")
            print(f"  名稱: {torch.cuda.get_device_name(i)}")
            print(f"  已用內存: {torch.cuda.memory_allocated(i) / 1e9:.2f} GB")
            print(f"  緩存內存: {torch.cuda.memory_reserved(i) / 1e9:.2f} GB")
            print(f"  總內存: {torch.cuda.get_device_properties(i).total_memory / 1e9:.2f} GB")

# 在批處理前後監控
llm = openllm.LLM("llama", model_id="meta-llama/Llama-2-7b-chat-hf")

print("批處理前:")
monitor_gpu_usage()

# 批處理
prompts = [f"Prompt {i}" for i in range(10)]
results = [llm(p, max_new_tokens=100) for p in prompts]

print("\\n批處理後:")
monitor_gpu_usage()
'''

    print(gpu_monitoring)


def large_scale_processing():
    """
    大規模數據處理

    處理大量數據的最佳實踐
    """
    print("\n" + "=" * 80)
    print("示例 6: 大規模數據處理")
    print("=" * 80)

    print("\n📝 分批處理大數據集：")
    print("-" * 80)

    chunking_code = '''
import openllm
from tqdm import tqdm

def process_large_dataset(llm, prompts, batch_size=32):
    """分批處理大數據集"""
    results = []

    # 分批
    for i in tqdm(range(0, len(prompts), batch_size)):
        batch = prompts[i:i + batch_size]

        # 處理當前批次
        batch_results = []
        for prompt in batch:
            result = llm(prompt, max_new_tokens=100)
            batch_results.append(result)

        results.extend(batch_results)

        # 可選：保存中間結果
        if (i + batch_size) % 100 == 0:
            save_checkpoint(results, f"checkpoint_{i}.json")

    return results

# 使用
llm = openllm.LLM("llama", model_id="meta-llama/Llama-2-7b-chat-hf")
large_prompts = [f"Prompt {i}" for i in range(1000)]

results = process_large_dataset(llm, large_prompts, batch_size=32)
'''

    print(chunking_code)

    print("\n使用生成器節省內存：")
    print("-" * 80)

    generator_code = '''
def process_with_generator(llm, prompts):
    """使用生成器逐個生成結果"""
    for prompt in prompts:
        result = llm(prompt, max_new_tokens=100)
        yield {
            "prompt": prompt,
            "result": result,
        }

# 使用生成器處理大量數據
llm = openllm.LLM("llama", model_id="meta-llama/Llama-2-7b-chat-hf")
prompts = [f"Prompt {i}" for i in range(10000)]

# 逐個處理並保存，不需要一次性加載所有結果到內存
with open("results.jsonl", "w") as f:
    for result in process_with_generator(llm, prompts):
        f.write(json.dumps(result) + "\\n")
'''

    print(generator_code)

    print("\n\n💡 大規模處理最佳實踐：")
    print("-" * 80)

    best_practices = [
        "使用合適的批大小（通常 16-64）",
        "實現檢查點機制，定期保存中間結果",
        "使用生成器處理超大數據集",
        "監控資源使用，避免 OOM",
        "實現錯誤處理和重試機制",
        "考慮使用任務隊列（Celery、RQ）",
        "記錄處理進度和統計信息",
    ]

    for i, practice in enumerate(best_practices, 1):
        print(f"{i}. {practice}")


def main():
    """
    主函數：運行所有示例
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "OpenLLM 批量處理示例" + " " * 20 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    try:
        # 示例 1: 基本批量處理
        basic_batch_processing()

        # 示例 2: 並發處理
        concurrent_batch_processing()

        # 示例 3: 批量 API
        batch_api_usage()

        # 示例 4: 批處理配置
        batch_configuration()

        # 示例 5: 性能監控
        performance_monitoring()

        # 示例 6: 大規模處理
        large_scale_processing()

        print("\n" + "=" * 80)
        print("✓ 所有示例展示完成！")
        print("=" * 80)
        print("\n💡 關鍵要點：")
        print("   1. 並發處理提高批量效率")
        print("   2. 合理配置批大小和並發數")
        print("   3. 監控性能和資源使用")
        print("   4. 大規模處理需要分批和檢查點")
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
