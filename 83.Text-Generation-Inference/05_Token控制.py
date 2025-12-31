#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TGI Token 控制示例"""
import sys

def token_control():
    print("=" * 80)
    print("Token 控制示例")
    print("=" * 80)
    code = '''
from text_generation import Client

client = Client("http://localhost:8080")

# 精確控制 token 數量
response = client.generate(
    "Explain quantum physics",
    max_new_tokens=150,
    min_new_tokens=50,  # 最小生成數量
)

# 使用停止序列
response = client.generate(
    "List three benefits of AI:\\n1.",
    max_new_tokens=200,
    stop_sequences=["\\n\\n", "4."],  # 遇到這些就停止
)

# Token 詳情
for token in response.details.tokens:
    print(f"{token.text} [ID: {token.id}, LogProb: {token.logprob:.3f}]")
'''
    print(code)

if __name__ == "__main__":
    print("\n" + "="*80)
    print("TGI Token 控制示例")
    print("="*80 + "\n")
    token_control()
    print("\n✓ 完成\n")
