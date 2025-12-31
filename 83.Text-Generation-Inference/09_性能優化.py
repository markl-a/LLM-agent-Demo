#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TGI 性能優化示例"""
import sys

def performance_optimization():
    print("=" * 80)
    print("性能優化示例")
    print("=" * 80)

    print("\n📝 啟動參數優化：\n")
    cmd = '''
text-generation-launcher \\
  --model-id meta-llama/Llama-2-7b-chat-hf \\
  --num-shard 2 \\                     # 張量並行
  --max-concurrent-requests 256 \\     # 最大並發
  --max-batch-prefill-tokens 4096 \\  # 批預填充
  --max-batch-total-tokens 8192 \\    # 批總 tokens
  --max-waiting-tokens 20 \\          # 最大等待
  --dtype float16 \\                   # 使用 FP16
  --quantize gptq                      # 量化
'''
    print(cmd)

    print("\n客戶端優化：\n")
    code = '''
from text_generation import Client
import time

client = Client("http://localhost:8080", timeout=60)

# 性能測試
prompts = [f"Test {i}" for i in range(100)]
start = time.time()

for prompt in prompts:
    client.generate(prompt, max_new_tokens=50)

elapsed = time.time() - start
print(f"吞吐量: {100/elapsed:.2f} req/s")
'''
    print(code)

if __name__ == "__main__":
    print("\n" + "="*80)
    print("TGI 性能優化示例")
    print("="*80 + "\n")
    performance_optimization()
    print("\n✓ 完成\n")
