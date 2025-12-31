#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TGI 流式輸出示例"""
import sys

def streaming_generation():
    print("=" * 80)
    print("流式生成示例")
    print("=" * 80)
    code = '''
from text_generation import Client

client = Client("http://localhost:8080")

# 流式生成
print("生成: ", end="", flush=True)
for response in client.generate_stream(
    "Tell me a story about AI",
    max_new_tokens=200,
):
    if not response.token.special:
        print(response.token.text, end="", flush=True)
print()
'''
    print(code)

if __name__ == "__main__":
    print("\n" + "="*80)
    print("TGI 流式輸出示例")
    print("="*80 + "\n")
    streaming_generation()
    print("\n✓ 完成\n")
