"""
Flowise 嵌入模型範例
==================

本範例展示如何在 Flowise 中配置嵌入模型。

支持的嵌入模型：
1. OpenAI Embeddings
2. Azure OpenAI Embeddings
3. HuggingFace Embeddings
4. Cohere Embeddings
5. 本地嵌入模型

安裝依賴：
pip install requests sentence-transformers
"""

import os
import json
from typing import Dict, Any, List

# ============================================================
# 配置
# ============================================================

FLOWISE_API_URL = os.getenv("FLOWISE_API_URL", "http://localhost:3000")


# ============================================================
# 嵌入模型配置
# ============================================================

OPENAI_EMBEDDINGS = '''
{
    "nodes": [
        {
            "id": "openAIEmbeddings_0",
            "type": "OpenAIEmbeddings",
            "data": {
                "label": "OpenAI Embeddings",
                "inputs": {
                    "modelName": "text-embedding-ada-002",
                    "stripNewLines": true,
                    "batchSize": 512
                },
                "credential": {
                    "openAIApiKey": "{{OPENAI_API_KEY}}"
                }
            }
        }
    ]
}
'''

AZURE_EMBEDDINGS = '''
{
    "nodes": [
        {
            "id": "azureOpenAIEmbeddings_0",
            "type": "AzureOpenAIEmbeddings",
            "data": {
                "label": "Azure OpenAI Embeddings",
                "inputs": {
                    "azureOpenAIApiDeploymentName": "text-embedding-ada-002"
                },
                "credential": {
                    "azureOpenAIApiKey": "{{AZURE_OPENAI_API_KEY}}",
                    "azureOpenAIApiInstanceName": "{{AZURE_INSTANCE}}",
                    "azureOpenAIApiVersion": "2024-02-15-preview"
                }
            }
        }
    ]
}
'''

HUGGINGFACE_EMBEDDINGS = '''
{
    "nodes": [
        {
            "id": "huggingFaceEmbeddings_0",
            "type": "HuggingFaceEmbeddings",
            "data": {
                "label": "HuggingFace Embeddings",
                "inputs": {
                    "modelName": "sentence-transformers/all-MiniLM-L6-v2"
                }
            }
        }
    ]
}
'''

COHERE_EMBEDDINGS = '''
{
    "nodes": [
        {
            "id": "cohereEmbeddings_0",
            "type": "CohereEmbeddings",
            "data": {
                "label": "Cohere Embeddings",
                "inputs": {
                    "modelName": "embed-multilingual-v3.0"
                },
                "credential": {
                    "cohereApiKey": "{{COHERE_API_KEY}}"
                }
            }
        }
    ]
}
'''

LOCAL_EMBEDDINGS = '''
{
    "nodes": [
        {
            "id": "localAIEmbeddings_0",
            "type": "LocalAIEmbeddings",
            "data": {
                "label": "Local Embeddings",
                "inputs": {
                    "basePath": "http://localhost:8080",
                    "modelName": "text-embedding-ada-002"
                }
            }
        }
    ]
}
'''


# ============================================================
# 使用範例
# ============================================================

def example_openai():
    """範例 1: OpenAI Embeddings"""
    print("=" * 50)
    print("範例 1: OpenAI Embeddings")
    print("=" * 50)
    print(OPENAI_EMBEDDINGS)
    print("\n特點: 高質量、1536 維度、支持批量處理")


def example_azure():
    """範例 2: Azure OpenAI Embeddings"""
    print("\n" + "=" * 50)
    print("範例 2: Azure OpenAI Embeddings")
    print("=" * 50)
    print(AZURE_EMBEDDINGS)
    print("\n特點: 企業級、合規性強")


def example_huggingface():
    """範例 3: HuggingFace Embeddings"""
    print("\n" + "=" * 50)
    print("範例 3: HuggingFace Embeddings")
    print("=" * 50)
    print(HUGGINGFACE_EMBEDDINGS)
    print("\n特點: 免費、可本地運行、多語言支持")


def example_cohere():
    """範例 4: Cohere Embeddings"""
    print("\n" + "=" * 50)
    print("範例 4: Cohere Embeddings")
    print("=" * 50)
    print(COHERE_EMBEDDINGS)
    print("\n特點: 多語言優秀、語義搜索優化")


def example_local():
    """範例 5: 本地 Embeddings"""
    print("\n" + "=" * 50)
    print("範例 5: 本地 Embeddings")
    print("=" * 50)
    print(LOCAL_EMBEDDINGS)
    print("\n特點: 隱私安全、無 API 費用")


def example_comparison():
    """範例 6: 模型比較"""
    print("\n" + "=" * 50)
    print("範例 6: 嵌入模型比較")
    print("=" * 50)
    print("""
| 模型                          | 維度   | 特點           | 適用場景      |
|------------------------------|--------|----------------|--------------|
| text-embedding-ada-002       | 1536   | 高質量         | 通用         |
| all-MiniLM-L6-v2            | 384    | 快速、輕量     | 實時應用     |
| embed-multilingual-v3.0      | 1024   | 多語言優秀     | 國際化應用   |
| text-embedding-3-large       | 3072   | 最高精度       | 高精度需求   |
""")


def example_custom_dimensions():
    """範例 7: 自定義維度"""
    print("\n" + "=" * 50)
    print("範例 7: 自定義嵌入維度")
    print("=" * 50)
    print('''
{
    "nodes": [
        {
            "id": "openAIEmbeddings_0",
            "type": "OpenAIEmbeddings",
            "data": {
                "inputs": {
                    "modelName": "text-embedding-3-small",
                    "dimensions": 512
                }
            }
        }
    ]
}

# OpenAI text-embedding-3 系列支持自定義維度
# 較小維度: 更快、更省存儲
# 較大維度: 更精確
''')


if __name__ == "__main__":
    print("Flowise 嵌入模型範例\\n")
    example_openai()
    example_azure()
    example_huggingface()
    example_cohere()
    example_local()
    example_comparison()
    example_custom_dimensions()
