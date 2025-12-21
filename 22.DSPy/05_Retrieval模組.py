"""
DSPy Retrieval 模組範例
======================

本範例展示如何在 DSPy 中整合檢索功能。

檢索方式：
1. ColBERT 檢索
2. Weaviate 向量數據庫
3. Pinecone 向量數據庫
4. 自定義檢索器

安裝依賴：
pip install dspy-ai colbert-ai weaviate-client pinecone-client
"""

import dspy
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

# ============================================================
# 配置
# ============================================================

turbo = dspy.OpenAI(model='gpt-3.5-turbo')
dspy.settings.configure(lm=turbo)


# ============================================================
# 1. ColBERT 檢索器
# ============================================================

COLBERT_EXAMPLE = '''
from dspy.retrieve.colbertv2 import ColBERTv2

# 初始化 ColBERT 檢索器
colbert = ColBERTv2(url="http://localhost:8893/api/search")

# 配置為默認檢索模型
dspy.settings.configure(rm=colbert)

# 使用 Retrieve 模組
class RAGModule(dspy.Module):
    def __init__(self, num_passages=3):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate = dspy.ChainOfThought("context, question -> answer")

    def forward(self, question):
        # 檢索相關段落
        context = self.retrieve(question).passages
        # 生成回答
        return self.generate(context=context, question=question)

# 使用
rag = RAGModule()
result = rag(question="什麼是深度學習？")
print(result.answer)
'''


# ============================================================
# 2. Weaviate 檢索器
# ============================================================

WEAVIATE_EXAMPLE = '''
from dspy.retrieve.weaviate_rm import WeaviateRM
import weaviate

# 連接 Weaviate
client = weaviate.Client("http://localhost:8080")

# 初始化 Weaviate 檢索器
weaviate_rm = WeaviateRM(
    weaviate_collection_name="Documents",
    weaviate_client=client,
    weaviate_collection_text_key="content"
)

# 配置
dspy.settings.configure(rm=weaviate_rm)

# 檢索示例
retriever = dspy.Retrieve(k=5)
results = retriever("機器學習的應用")

for passage in results.passages:
    print(passage[:200] + "...")
'''


# ============================================================
# 3. Pinecone 檢索器
# ============================================================

PINECONE_EXAMPLE = '''
from dspy.retrieve.pinecone_rm import PineconeRM
import pinecone

# 初始化 Pinecone
pinecone.init(
    api_key="your-api-key",
    environment="your-environment"
)

# 創建 Pinecone 檢索器
pinecone_rm = PineconeRM(
    pinecone_index_name="documents",
    pinecone_api_key="your-api-key",
    pinecone_env="your-environment",
    openai_api_key="your-openai-key"  # 用於生成嵌入
)

dspy.settings.configure(rm=pinecone_rm)

# 使用
retriever = dspy.Retrieve(k=3)
results = retriever("自然語言處理")
'''


# ============================================================
# 4. 自定義檢索器
# ============================================================

class SimpleRetriever(dspy.Retrieve):
    """簡單的基於關鍵詞的檢索器"""

    def __init__(self, documents: List[str], k: int = 3):
        super().__init__(k=k)
        self.documents = documents
        self.k = k

    def forward(self, query: str, k: Optional[int] = None) -> dspy.Prediction:
        """檢索相關文檔"""
        k = k or self.k
        query_terms = set(query.lower().split())

        # 計算每個文檔的相關性分數
        scored_docs = []
        for doc in self.documents:
            doc_terms = set(doc.lower().split())
            score = len(query_terms & doc_terms) / len(query_terms) if query_terms else 0
            scored_docs.append((score, doc))

        # 排序並返回 top-k
        scored_docs.sort(reverse=True, key=lambda x: x[0])
        passages = [doc for score, doc in scored_docs[:k]]

        return dspy.Prediction(passages=passages)


class EmbeddingRetriever(dspy.Retrieve):
    """基於嵌入的檢索器"""

    def __init__(self, documents: List[str], embeddings: List[List[float]], k: int = 3):
        super().__init__(k=k)
        self.documents = documents
        self.embeddings = embeddings
        self.k = k

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """計算餘弦相似度"""
        import math
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        return dot_product / (norm_a * norm_b) if norm_a and norm_b else 0

    def _get_embedding(self, text: str) -> List[float]:
        """獲取文本嵌入（簡化版本）"""
        # 實際應用中使用 OpenAI 或其他嵌入模型
        words = text.lower().split()
        # 簡化：使用詞頻作為特徵
        vocab = list(set(" ".join(self.documents).lower().split()))
        embedding = [words.count(w) for w in vocab[:100]]
        return embedding

    def forward(self, query: str, k: Optional[int] = None) -> dspy.Prediction:
        """基於嵌入檢索"""
        k = k or self.k
        query_embedding = self._get_embedding(query)

        # 計算相似度
        similarities = [
            (self._cosine_similarity(query_embedding, emb), doc)
            for emb, doc in zip(self.embeddings, self.documents)
        ]

        # 排序並返回
        similarities.sort(reverse=True, key=lambda x: x[0])
        passages = [doc for _, doc in similarities[:k]]

        return dspy.Prediction(passages=passages)


# ============================================================
# 5. RAG 模組
# ============================================================

class BasicRAG(dspy.Module):
    """基本 RAG 模組"""

    def __init__(self, num_passages: int = 3):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate = dspy.ChainOfThought("context, question -> answer")

    def forward(self, question: str):
        context = self.retrieve(question).passages
        context_str = "\n\n".join(context)
        return self.generate(context=context_str, question=question)


class MultiHopRAG(dspy.Module):
    """多跳 RAG 模組"""

    def __init__(self, num_passages: int = 3, num_hops: int = 2):
        super().__init__()
        self.num_hops = num_hops
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate_query = dspy.ChainOfThought("context, question -> search_query")
        self.generate_answer = dspy.ChainOfThought("context, question -> answer")

    def forward(self, question: str):
        context = []

        # 多次檢索
        current_query = question
        for hop in range(self.num_hops):
            # 檢索
            passages = self.retrieve(current_query).passages
            context.extend(passages)

            # 生成下一個查詢
            if hop < self.num_hops - 1:
                context_str = "\n\n".join(context)
                next_query = self.generate_query(
                    context=context_str,
                    question=question
                )
                current_query = next_query.search_query

        # 生成最終回答
        context_str = "\n\n".join(context)
        return self.generate_answer(context=context_str, question=question)


class ReRankRAG(dspy.Module):
    """帶重排序的 RAG 模組"""

    def __init__(self, num_passages: int = 10, top_k: int = 3):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.top_k = top_k
        self.rerank = dspy.ChainOfThought(
            "passages, question -> ranked_indices: list[int]"
        )
        self.generate = dspy.ChainOfThought("context, question -> answer")

    def forward(self, question: str):
        # 初步檢索
        passages = self.retrieve(question).passages

        # 重排序（簡化版本）
        # 實際應用中可以使用專門的重排序模型
        scored = []
        for i, p in enumerate(passages):
            # 簡單的相關性評分
            query_words = set(question.lower().split())
            passage_words = set(p.lower().split())
            score = len(query_words & passage_words)
            scored.append((score, i, p))

        # 取 top-k
        scored.sort(reverse=True, key=lambda x: x[0])
        top_passages = [p for _, _, p in scored[:self.top_k]]

        # 生成回答
        context_str = "\n\n".join(top_passages)
        return self.generate(context=context_str, question=question)


# ============================================================
# 6. 文檔處理
# ============================================================

@dataclass
class Document:
    """文檔類"""
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: Optional[str] = None


class DocumentProcessor:
    """文檔處理器"""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        """分割文本"""
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # 嘗試在句號處分割
            if end < len(text):
                # 向後找句號
                for i in range(min(50, end - start)):
                    if end - i < len(text) and text[end - i] in '.。！？!?':
                        end = end - i + 1
                        break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - self.chunk_overlap

        return chunks

    def process_documents(self, documents: List[Document]) -> List[str]:
        """處理多個文檔"""
        all_chunks = []

        for doc in documents:
            chunks = self.split_text(doc.content)
            all_chunks.extend(chunks)

        return all_chunks


# ============================================================
# 使用範例
# ============================================================

def example_colbert():
    """範例 1: ColBERT 檢索"""
    print("=" * 50)
    print("範例 1: ColBERT 檢索器")
    print("=" * 50)
    print(COLBERT_EXAMPLE)


def example_weaviate():
    """範例 2: Weaviate 檢索"""
    print("\n" + "=" * 50)
    print("範例 2: Weaviate 檢索器")
    print("=" * 50)
    print(WEAVIATE_EXAMPLE)


def example_pinecone():
    """範例 3: Pinecone 檢索"""
    print("\n" + "=" * 50)
    print("範例 3: Pinecone 檢索器")
    print("=" * 50)
    print(PINECONE_EXAMPLE)


def example_custom_retriever():
    """範例 4: 自定義檢索器"""
    print("\n" + "=" * 50)
    print("範例 4: 自定義檢索器")
    print("=" * 50)

    # 示例文檔
    documents = [
        "機器學習是人工智能的一個分支，專注於讓計算機從數據中學習。",
        "深度學習是機器學習的子領域，使用多層神經網絡。",
        "自然語言處理讓計算機理解和生成人類語言。",
        "計算機視覺專注於讓計算機理解圖像和視頻。",
        "強化學習通過獎勵和懲罰來訓練代理做決策。"
    ]

    # 創建檢索器
    retriever = SimpleRetriever(documents, k=2)

    # 測試檢索
    query = "什麼是深度學習和神經網絡？"
    results = retriever(query)

    print(f"查詢: {query}")
    print(f"\n檢索結果:")
    for i, passage in enumerate(results.passages):
        print(f"  {i+1}. {passage}")


def example_rag_modules():
    """範例 5: RAG 模組"""
    print("\n" + "=" * 50)
    print("範例 5: RAG 模組類型")
    print("=" * 50)

    print("""
1. BasicRAG - 基本檢索增強生成
   - 單次檢索
   - 直接生成回答

2. MultiHopRAG - 多跳推理
   - 多次檢索
   - 迭代式問題分解

3. ReRankRAG - 重排序 RAG
   - 初步檢索大量文檔
   - 重排序選擇最相關的
   - 基於精選文檔生成回答
""")


def example_document_processing():
    """範例 6: 文檔處理"""
    print("\n" + "=" * 50)
    print("範例 6: 文檔處理")
    print("=" * 50)

    processor = DocumentProcessor(chunk_size=100, chunk_overlap=20)

    long_text = """
    人工智能（AI）是計算機科學的一個分支，致力於創造能夠執行通常需要人類智能的任務的機器。
    這些任務包括視覺感知、語音識別、決策制定和語言翻譯。
    機器學習是 AI 的一個子集，它使計算機能夠在沒有明確編程的情況下從經驗中學習。
    深度學習是機器學習的一種類型，它使用多層人工神經網絡來學習數據的複雜模式。
    """

    chunks = processor.split_text(long_text)

    print(f"原始文本長度: {len(long_text)} 字符")
    print(f"分割成 {len(chunks)} 個塊:")
    for i, chunk in enumerate(chunks):
        print(f"\n塊 {i+1} ({len(chunk)} 字符):")
        print(f"  {chunk[:80]}...")


if __name__ == "__main__":
    print("DSPy Retrieval 模組範例\n")
    example_colbert()
    example_weaviate()
    example_pinecone()
    example_custom_retriever()
    example_rag_modules()
    example_document_processing()
