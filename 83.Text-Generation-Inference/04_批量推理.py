#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TGI 批量推理示例"""
import sys

def batch_processing():
    print("=" * 80)
    print("批量處理示例")
    print("=" * 80)
    code = '''
from text_generation import Client
from concurrent.futures import ThreadPoolExecutor

client = Client("http://localhost:8080")

prompts = [f"Question {i}: What is AI?" for i in range(10)]

def process_one(prompt):
    return client.generate(prompt, max_new_tokens=100)

# 並發處理
with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(process_one, prompts))

for i, result in enumerate(results):
    print(f"[{i+1}] {result.generated_text[:50]}...")
'''
    print(code)

if __name__ == "__main__":
    print("\n" + "="*80)
    print("TGI 批量推理示例")
    print("="*80 + "\n")
    batch_processing()
    print("\n✓ 完成\n")
