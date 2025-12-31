#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TGI 多模型部署示例"""
import sys

def multi_model_deployment():
    print("=" * 80)
    print("多模型部署示例")
    print("=" * 80)
    print("\n📝 Docker Compose 配置：\n")
    compose = '''
version: '3.8'
services:
  tgi-7b:
    image: ghcr.io/huggingface/text-generation-inference:latest
    command: --model-id meta-llama/Llama-2-7b-chat-hf
    ports:
      - "8080:80"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  tgi-13b:
    image: ghcr.io/huggingface/text-generation-inference:latest
    command: --model-id meta-llama/Llama-2-13b-chat-hf
    ports:
      - "8081:80"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
'''
    print(compose)

    print("\n使用不同模型：\n")
    code = '''
from text_generation import Client

# 7B 模型（快速）
client_7b = Client("http://localhost:8080")
result_7b = client_7b.generate("Quick question", max_new_tokens=50)

# 13B 模型（更好質量）
client_13b = Client("http://localhost:8081")
result_13b = client_13b.generate("Complex question", max_new_tokens=200)
'''
    print(code)

if __name__ == "__main__":
    print("\n" + "="*80)
    print("TGI 多模型部署示例")
    print("="*80 + "\n")
    multi_model_deployment()
    print("\n✓ 完成\n")
