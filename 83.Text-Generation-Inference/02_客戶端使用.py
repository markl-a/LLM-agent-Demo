#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TGI 客戶端使用示例
==================

本示例展示 Python 客戶端的詳細使用，包括：
1. 客戶端初始化
2. 同步和異步調用
3. 參數配置
4. 錯誤處理
"""

import sys


def sync_client_usage():
    """同步客戶端使用"""
    print("=" * 80)
    print("示例 1: 同步客戶端")
    print("=" * 80)

    code = '''
from text_generation import Client

# 創建客戶端
client = Client("http://localhost:8080")

# 基本生成
response = client.generate("Hello, how are you?", max_new_tokens=50)
print(response.generated_text)

# 帶詳細參數
response = client.generate(
    "Explain AI",
    max_new_tokens=200,
    temperature=0.8,
    top_p=0.95,
    repetition_penalty=1.1,
    do_sample=True,
)

# 查看詳情
print(f"生成 tokens: {len(response.details.tokens)}")
for token in response.details.tokens:
    print(f"{token.text} (logprob: {token.logprob:.4f})")
'''
    print(code)


def async_client_usage():
    """異步客戶端使用"""
    print("\n" + "=" * 80)
    print("示例 2: 異步客戶端")
    print("=" * 80)

    code = '''
import asyncio
from text_generation import AsyncClient

async def main():
    client = AsyncClient("http://localhost:8080")

    # 異步生成
    response = await client.generate(
        "What is machine learning?",
        max_new_tokens=100,
    )
    print(response.generated_text)

    # 並發請求
    tasks = [
        client.generate(f"Question {i}", max_new_tokens=50)
        for i in range(5)
    ]

    responses = await asyncio.gather(*tasks)
    for i, resp in enumerate(responses):
        print(f"[{i+1}] {resp.generated_text}")

asyncio.run(main())
'''
    print(code)


def main():
    """主函數"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "TGI 客戶端使用示例" + " " * 20 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    sync_client_usage()
    async_client_usage()

    print("\n" + "=" * 80)
    print("✓ 示例完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
