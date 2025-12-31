#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TGI 停止序列示例"""
import sys

def stop_sequences():
    print("=" * 80)
    print("停止序列示例")
    print("=" * 80)
    code = '''
from text_generation import Client

client = Client("http://localhost:8080")

# 使用停止序列控制輸出格式
response = client.generate(
    "Write a JSON object with name and age:",
    max_new_tokens=100,
    stop_sequences=["}"],  # 在 } 處停止
)

# 多個停止序列
response = client.generate(
    "List items:\\n- ",
    max_new_tokens=200,
    stop_sequences=["\\n\\n", "---", "END"],
)
'''
    print(code)

if __name__ == "__main__":
    print("\n" + "="*80)
    print("TGI 停止序列示例")
    print("="*80 + "\n")
    stop_sequences()
    print("\n✓ 完成\n")
