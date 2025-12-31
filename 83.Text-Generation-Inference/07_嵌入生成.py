#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TGI 嵌入生成示例"""
import sys

def embeddings():
    print("=" * 80)
    print("嵌入向量生成示例")
    print("=" * 80)
    code = '''
# TGI 主要用於文本生成，嵌入功能有限
# 對於嵌入，建議使用專門的模型服務

# 但可以通過 token logits 獲取一些表示信息
from text_generation import Client

client = Client("http://localhost:8080")

response = client.generate(
    "This is a test sentence",
    max_new_tokens=1,  # 只生成一個 token
)

# 訪問 token 的詳細信息
for token in response.details.tokens:
    print(f"Token: {token.text}")
    print(f"ID: {token.id}")
    print(f"LogProb: {token.logprob}")
'''
    print(code)

if __name__ == "__main__":
    print("\n" + "="*80)
    print("TGI 嵌入生成示例")
    print("="*80 + "\n")
    embeddings()
    print("\n✓ 完成\n")
