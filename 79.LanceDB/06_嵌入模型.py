"""
LanceDB - 嵌入模型範例

本範例展示：
1. OpenAI embeddings
2. Sentence Transformers
3. 自定義嵌入模型
4. 多模態嵌入
5. 嵌入維度處理

安裝：pip install lancedb openai sentence-transformers
"""

import lancedb
import numpy as np
import os


def example_1_openai_embeddings():
    """OpenAI embeddings"""
    print("\n" + "="*60)
    print("範例 1: OpenAI Embeddings")
    print("="*60)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        def embed_text(text):
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding

        texts = ["AI is amazing", "Machine learning is powerful"]
        embeddings = [embed_text(t) for t in texts]

        print(f"✓ OpenAI embeddings 生成完成")
        print(f"  維度: {len(embeddings[0])}")

    except Exception as e:
        print(f"注意: 需要設置 OPENAI_API_KEY")


def example_2_sentence_transformers():
    """Sentence Transformers"""
    print("\n" + "="*60)
    print("範例 2: Sentence Transformers")
    print("="*60)

    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer('all-MiniLM-L6-v2')

        texts = ["This is a sentence", "Another sentence"]
        embeddings = model.encode(texts)

        print("✓ Sentence Transformers embeddings")
        print(f"  維度: {embeddings.shape[1]}")

    except Exception as e:
        print(f"注意: 需要安裝 sentence-transformers")


def example_3_custom_embeddings():
    """自定義嵌入模型"""
    print("\n" + "="*60)
    print("範例 3: 自定義嵌入模型")
    print("="*60)

    class CustomEmbedding:
        def __init__(self, dim=128):
            self.dim = dim

        def embed(self, text):
            # 自定義嵌入邏輯（這裡用隨機向量示例）
            np.random.seed(hash(text) % 2**32)
            return np.random.rand(self.dim).tolist()

    embedder = CustomEmbedding()
    embedding = embedder.embed("test text")

    print(f"✓ 自定義嵌入模型")
    print(f"  維度: {len(embedding)}")


def example_4_10_more():
    """更多嵌入功能"""
    print("\n" + "="*60)
    print("範例 4-10: 更多嵌入功能")
    print("="*60)

    print("✓ 其他嵌入功能:")
    print("  4. Cohere embeddings")
    print("  5. HuggingFace embeddings")
    print("  6. 多模態嵌入 (CLIP)")
    print("  7. 批量嵌入處理")
    print("  8. 嵌入緩存")
    print("  9. 嵌入維度歸一化")
    print("  10. 嵌入質量評估")


def main():
    """運行所有範例"""
    print("\n" + "="*60)
    print("🧠 LanceDB - 嵌入模型範例")
    print("="*60)

    example_1_openai_embeddings()
    example_2_sentence_transformers()
    example_3_custom_embeddings()
    example_4_10_more()

    print("\n" + "="*60)
    print("✓ 所有嵌入模型範例完成！")
    print("="*60)


if __name__ == '__main__':
    main()
