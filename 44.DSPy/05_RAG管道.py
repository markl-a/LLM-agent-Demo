"""
DSPy RAG 管道構建教學

本模組展示如何使用 DSPy 構建檢索增強生成（RAG）系統：
1. RAG 基礎概念和架構
2. 向量數據庫集成（ChromaDB）
3. 檢索器配置和優化
4. RAG 模組設計
5. 多跳推理 RAG
6. 自適應檢索策略
7. RAG 系統評估和優化

作者：DSPy 教學團隊
日期：2025-01
"""

import dspy
from typing import List, Dict, Optional
import chromadb
from chromadb.utils import embedding_functions


# ==================== RAG 基礎概念 ====================

def explain_rag_concept():
    """
    解釋 RAG 的核心概念

    RAG = Retrieval-Augmented Generation
    檢索增強生成
    """
    print("\n" + "="*60)
    print("RAG 核心概念")
    print("="*60)

    print("""
    RAG 的工作流程：
    1. 用戶提出問題
    2. 從知識庫檢索相關文檔
    3. 將文檔和問題一起送給 LLM
    4. LLM 基於檢索到的上下文生成答案

    RAG 的優勢：
    - 提供最新的資訊（知識庫可更新）
    - 減少幻覺（基於實際文檔）
    - 可追溯來源（知道答案來自哪裡）
    - 降低成本（不需要訓練大模型）

    DSPy RAG 的特點：
    - 自動優化檢索策略
    - 優化檢索-生成的協同
    - 模組化設計，易於擴展
    """)


# ==================== 向量數據庫設置 ====================

class ChromaDBSetup:
    """ChromaDB 設置和管理"""

    def __init__(self, collection_name="dspy_docs", persist_directory="./chroma_db"):
        """
        初始化 ChromaDB

        Args:
            collection_name: 集合名稱
            persist_directory: 持久化目錄
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory

        # 創建客戶端
        self.client = chromadb.PersistentClient(path=persist_directory)

        # 創建或獲取集合
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        print(f"✓ ChromaDB 集合 '{collection_name}' 已準備就緒")
        print(f"  文檔數量：{self.collection.count()}")

    def add_documents(self, documents: List[str], metadatas: Optional[List[Dict]] = None):
        """
        添加文檔到向量數據庫

        Args:
            documents: 文檔列表
            metadatas: 元數據列表（可選）
        """
        if not documents:
            return

        # 生成 ID
        ids = [f"doc_{i}" for i in range(len(documents))]

        # 添加文檔
        self.collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas if metadatas else None
        )

        print(f"✓ 已添加 {len(documents)} 個文檔")

    def clear(self):
        """清空集合"""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        print("✓ 集合已清空")


def create_sample_knowledge_base():
    """
    創建範例知識庫

    返回一組關於機器學習的文檔
    """
    documents = [
        # 機器學習基礎
        "機器學習是人工智能的一個分支，它使計算機系統能夠從數據中學習和改進，而無需明確編程。主要方法包括監督學習、非監督學習和強化學習。",

        "監督學習使用標註數據來訓練模型，常見任務包括分類和回歸。例如，圖像分類、垃圾郵件檢測和房價預測都是監督學習的應用。",

        "非監督學習處理未標註的數據，旨在發現數據中的隱藏模式。聚類和降維是兩種主要的非監督學習任務。K-means 和 PCA 是常用的算法。",

        "強化學習通過與環境互動並根據獎勵信號調整行為來學習最優策略。AlphaGo 和自動駕駛都使用了強化學習技術。",

        # 深度學習
        "深度學習是機器學習的一個子集，使用多層神經網絡來學習數據的複雜模式。它在圖像識別、自然語言處理和語音識別等領域取得了突破性進展。",

        "卷積神經網絡（CNN）專門用於處理網格狀數據，如圖像。它通過卷積層、池化層和全連接層來提取和學習特徵。ResNet 和 VGG 是著名的 CNN 架構。",

        "循環神經網絡（RNN）用於處理序列數據，如文本和時間序列。LSTM 和 GRU 是改進的 RNN 變體，能夠更好地處理長期依賴。",

        "Transformer 架構徹底改變了自然語言處理領域。它使用自注意力機制，能夠並行處理序列數據。BERT、GPT 和 T5 都基於 Transformer。",

        # 模型訓練
        "過擬合是指模型在訓練數據上表現很好，但在新數據上表現不佳。常用的解決方法包括正則化、數據增強和早停。",

        "正則化技術包括 L1 和 L2 正則化、Dropout 和批量歸一化。這些技術幫助模型學習更通用的特徵，提高泛化能力。",

        "梯度下降是訓練神經網絡的核心優化算法。變體包括隨機梯度下降（SGD）、Adam 和 RMSprop。學習率是最重要的超參數之一。",

        "遷移學習利用在大型數據集上預訓練的模型，通過微調來解決特定任務。這可以顯著減少訓練時間和數據需求。",

        # 模型評估
        "評估指標的選擇取決於具體任務。分類任務常用準確率、精確率、召回率和 F1 分數。回歸任務常用 MSE、RMSE 和 R²。",

        "交叉驗證是評估模型性能的重要技術。K 折交叉驗證將數據分成 K 個子集，輪流使用一個子集作為驗證集，其餘作為訓練集。",

        "混淆矩陣提供了分類模型性能的詳細視圖，顯示真陽性、假陽性、真陰性和假陰性的數量。ROC 曲線和 AUC 是評估二分類器的有用工具。",

        # NLP 和 LLM
        "自然語言處理（NLP）使計算機能夠理解、解釋和生成人類語言。應用包括機器翻譯、情感分析、問答系統和聊天機器人。",

        "詞嵌入將詞語映射到連續向量空間，使語義相似的詞語在空間中更接近。Word2Vec、GloVe 和 FastText 是常用的詞嵌入方法。",

        "大型語言模型（LLM）如 GPT-4、Claude 和 PaLM 通過在海量文本數據上訓練，展現出驚人的語言理解和生成能力。它們可以執行多種任務而無需特定訓練。",

        "提示工程是與 LLM 互動的藝術和科學。精心設計的提示可以顯著提高模型輸出的質量。思維鏈提示和少樣本學習是有效的技術。",

        # RAG 和檢索
        "檢索增強生成（RAG）結合了資訊檢索和文本生成。它先從知識庫檢索相關文檔，然後基於這些文檔生成答案，從而提供更準確和最新的資訊。",

        "向量數據庫如 Pinecone、Weaviate 和 ChromaDB 專門用於存儲和檢索向量嵌入。它們支持高效的相似性搜索，是 RAG 系統的關鍵組件。",
    ]

    metadatas = [
        {"topic": "ml_basics", "subtopic": "intro"},
        {"topic": "ml_basics", "subtopic": "supervised"},
        {"topic": "ml_basics", "subtopic": "unsupervised"},
        {"topic": "ml_basics", "subtopic": "reinforcement"},
        {"topic": "deep_learning", "subtopic": "intro"},
        {"topic": "deep_learning", "subtopic": "cnn"},
        {"topic": "deep_learning", "subtopic": "rnn"},
        {"topic": "deep_learning", "subtopic": "transformer"},
        {"topic": "training", "subtopic": "overfitting"},
        {"topic": "training", "subtopic": "regularization"},
        {"topic": "training", "subtopic": "optimization"},
        {"topic": "training", "subtopic": "transfer_learning"},
        {"topic": "evaluation", "subtopic": "metrics"},
        {"topic": "evaluation", "subtopic": "cross_validation"},
        {"topic": "evaluation", "subtopic": "confusion_matrix"},
        {"topic": "nlp", "subtopic": "intro"},
        {"topic": "nlp", "subtopic": "embeddings"},
        {"topic": "nlp", "subtopic": "llm"},
        {"topic": "nlp", "subtopic": "prompting"},
        {"topic": "rag", "subtopic": "intro"},
        {"topic": "rag", "subtopic": "vector_db"},
    ]

    return documents, metadatas


# ==================== 基礎 RAG 模組 ====================

class SimpleRAG(dspy.Module):
    """
    簡單的 RAG 模組

    基本流程：檢索 -> 生成
    """

    def __init__(self, num_passages=3):
        """
        初始化 RAG 模組

        Args:
            num_passages: 檢索的文檔數量
        """
        super().__init__()

        # 定義生成簽名
        class GenerateAnswer(dspy.Signature):
            """基於上下文回答問題"""
            context = dspy.InputField(desc="檢索到的相關文檔")
            question = dspy.InputField(desc="用戶問題")
            answer = dspy.OutputField(desc="基於上下文的答案")

        # 創建檢索和生成模組
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate_answer = dspy.ChainOfThought(GenerateAnswer)

    def forward(self, question):
        """
        執行 RAG 流程

        Args:
            question: 用戶問題

        Returns:
            包含答案和上下文的預測結果
        """
        # 檢索相關文檔
        context = self.retrieve(question).passages

        # 生成答案
        prediction = self.generate_answer(context=context, question=question)

        # 返回結果（包含上下文以便檢查）
        return dspy.Prediction(
            answer=prediction.answer,
            context=context
        )


class RAGWithSourceCitation(dspy.Module):
    """
    帶來源引用的 RAG 模組

    不僅生成答案，還標註來源
    """

    def __init__(self, num_passages=3):
        super().__init__()

        class GenerateAnswerWithCitation(dspy.Signature):
            """基於上下文回答問題並引用來源"""
            context = dspy.InputField(desc="編號的相關文檔")
            question = dspy.InputField(desc="用戶問題")
            answer = dspy.OutputField(desc="基於上下文的答案")
            citations = dspy.OutputField(desc="使用的文檔編號（如 [1][2]）")

        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate_answer = dspy.ChainOfThought(GenerateAnswerWithCitation)

    def forward(self, question):
        """執行帶引用的 RAG"""
        # 檢索
        passages = self.retrieve(question).passages

        # 格式化上下文（添加編號）
        numbered_context = "\n\n".join([
            f"[{i+1}] {passage}"
            for i, passage in enumerate(passages)
        ])

        # 生成答案
        prediction = self.generate_answer(
            context=numbered_context,
            question=question
        )

        return dspy.Prediction(
            answer=prediction.answer,
            citations=prediction.citations,
            context=passages
        )


# ==================== 多跳推理 RAG ====================

class MultiHopRAG(dspy.Module):
    """
    多跳推理 RAG 模組

    對於複雜問題，可能需要多次檢索
    """

    def __init__(self, num_passages=3, max_hops=2):
        super().__init__()
        self.max_hops = max_hops

        # 生成搜索查詢
        class GenerateSearchQuery(dspy.Signature):
            """基於問題和已知資訊生成搜索查詢"""
            question = dspy.InputField()
            context = dspy.InputField(desc="已知資訊")
            search_query = dspy.OutputField(desc="搜索查詢")

        # 生成答案
        class GenerateAnswer(dspy.Signature):
            """基於多個上下文回答問題"""
            question = dspy.InputField()
            contexts = dspy.InputField(desc="檢索到的所有上下文")
            answer = dspy.OutputField()

        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate_query = dspy.ChainOfThought(GenerateSearchQuery)
        self.generate_answer = dspy.ChainOfThought(GenerateAnswer)

    def forward(self, question):
        """執行多跳推理"""
        all_contexts = []
        current_context = ""

        # 多次檢索
        for hop in range(self.max_hops):
            if hop == 0:
                # 第一跳：直接使用問題
                query = question
            else:
                # 後續跳：生成新的搜索查詢
                query_result = self.generate_query(
                    question=question,
                    context=current_context
                )
                query = query_result.search_query

            # 檢索
            passages = self.retrieve(query).passages
            all_contexts.extend(passages)
            current_context = "\n\n".join(passages)

        # 基於所有上下文生成答案
        all_contexts_text = "\n\n".join([
            f"Context {i+1}: {ctx}"
            for i, ctx in enumerate(all_contexts)
        ])

        prediction = self.generate_answer(
            question=question,
            contexts=all_contexts_text
        )

        return dspy.Prediction(
            answer=prediction.answer,
            all_contexts=all_contexts
        )


# ==================== 自適應 RAG ====================

class AdaptiveRAG(dspy.Module):
    """
    自適應 RAG 模組

    根據問題複雜度決定是否需要檢索
    """

    def __init__(self, num_passages=3):
        super().__init__()

        # 判斷是否需要檢索
        class NeedRetrieval(dspy.Signature):
            """判斷問題是否需要外部知識"""
            question = dspy.InputField()
            needs_retrieval = dspy.OutputField(desc="yes 或 no")
            reasoning = dspy.OutputField(desc="判斷理由")

        # 不帶檢索的答案
        class DirectAnswer(dspy.Signature):
            """直接回答常識性問題"""
            question = dspy.InputField()
            answer = dspy.OutputField()

        # 帶檢索的答案
        class RAGAnswer(dspy.Signature):
            """基於檢索回答問題"""
            context = dspy.InputField()
            question = dspy.InputField()
            answer = dspy.OutputField()

        self.need_retrieval = dspy.Predict(NeedRetrieval)
        self.direct_answer = dspy.ChainOfThought(DirectAnswer)
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.rag_answer = dspy.ChainOfThought(RAGAnswer)

    def forward(self, question):
        """自適應回答"""
        # 判斷是否需要檢索
        decision = self.need_retrieval(question=question)

        if "yes" in decision.needs_retrieval.lower():
            # 需要檢索
            context = self.retrieve(question).passages
            prediction = self.rag_answer(
                context=context,
                question=question
            )
            used_retrieval = True
        else:
            # 不需要檢索
            prediction = self.direct_answer(question=question)
            context = []
            used_retrieval = False

        return dspy.Prediction(
            answer=prediction.answer,
            used_retrieval=used_retrieval,
            decision_reasoning=decision.reasoning,
            context=context if used_retrieval else []
        )


# ==================== RAG 優化 ====================

class OptimizedRAG(dspy.Module):
    """
    優化的 RAG 模組

    包含檢索質量評估和答案驗證
    """

    def __init__(self, num_passages=5):
        super().__init__()

        # 評估檢索質量
        class AssessRelevance(dspy.Signature):
            """評估檢索文檔的相關性"""
            question = dspy.InputField()
            passage = dspy.InputField()
            is_relevant = dspy.OutputField(desc="yes 或 no")

        # 生成答案
        class GenerateAnswer(dspy.Signature):
            """生成答案"""
            context = dspy.InputField()
            question = dspy.InputField()
            answer = dspy.OutputField()
            confidence = dspy.OutputField(desc="置信度（0-100）")

        self.retrieve = dspy.Retrieve(k=num_passages)
        self.assess_relevance = dspy.Predict(AssessRelevance)
        self.generate_answer = dspy.ChainOfThought(GenerateAnswer)

    def forward(self, question):
        """執行優化的 RAG"""
        # 檢索
        passages = self.retrieve(question).passages

        # 過濾相關文檔
        relevant_passages = []
        for passage in passages:
            assessment = self.assess_relevance(
                question=question,
                passage=passage
            )
            if "yes" in assessment.is_relevant.lower():
                relevant_passages.append(passage)

        # 如果沒有相關文檔，使用原始文檔
        if not relevant_passages:
            relevant_passages = passages[:2]

        # 生成答案
        context = "\n\n".join(relevant_passages)
        prediction = self.generate_answer(
            context=context,
            question=question
        )

        return dspy.Prediction(
            answer=prediction.answer,
            confidence=prediction.confidence,
            num_passages_retrieved=len(passages),
            num_relevant_passages=len(relevant_passages),
            relevant_context=relevant_passages
        )


# ==================== 實用函數 ====================

def demo_simple_rag(rag_module, questions):
    """演示簡單 RAG"""
    print("\n" + "="*60)
    print("簡單 RAG 演示")
    print("="*60)

    for question in questions:
        print(f"\n問題：{question}")
        result = rag_module(question=question)
        print(f"答案：{result.answer}")
        print(f"\n檢索到的上下文（前 100 字）：")
        for i, ctx in enumerate(result.context[:2], 1):
            print(f"  [{i}] {ctx[:100]}...")


def demo_rag_with_citation(rag_module, questions):
    """演示帶引用的 RAG"""
    print("\n" + "="*60)
    print("帶引用 RAG 演示")
    print("="*60)

    for question in questions:
        print(f"\n問題：{question}")
        result = rag_module(question=question)
        print(f"答案：{result.answer}")
        print(f"引用：{result.citations}")


def demo_adaptive_rag(rag_module, questions):
    """演示自適應 RAG"""
    print("\n" + "="*60)
    print("自適應 RAG 演示")
    print("="*60)

    for question in questions:
        print(f"\n問題：{question}")
        result = rag_module(question=question)
        print(f"使用檢索：{result.used_retrieval}")
        print(f"決策理由：{result.decision_reasoning}")
        print(f"答案：{result.answer}")


# ==================== 主程序 ====================

def main():
    """主函數：演示所有 RAG 功能"""

    print("="*60)
    print("DSPy RAG 管道構建教學")
    print("="*60)

    # 1. 概念說明
    explain_rag_concept()

    # 2. 配置 DSPy
    print("\n" + "="*60)
    print("配置 DSPy")
    print("="*60)
    try:
        lm = dspy.OpenAI(model="gpt-4", max_tokens=600)
        dspy.settings.configure(lm=lm)
        print("✓ LLM 配置完成")
    except Exception as e:
        print(f"配置失敗：{e}")
        return

    # 3. 設置向量數據庫
    print("\n" + "="*60)
    print("設置向量數據庫")
    print("="*60)
    try:
        db = ChromaDBSetup()

        # 創建知識庫
        documents, metadatas = create_sample_knowledge_base()
        db.clear()
        db.add_documents(documents, metadatas)

        # 配置 DSPy 檢索器
        # 注意：這裡需要配置 ChromaDB 檢索器
        # 實際實現可能需要自定義檢索模組
        print("✓ 知識庫準備完成")
    except Exception as e:
        print(f"數據庫設置失敗：{e}")
        print("繼續使用模擬檢索器...")

    # 4. 測試問題
    questions = [
        "什麼是深度學習？",
        "如何解決過擬合問題？",
        "Transformer 架構有什麼優勢？",
        "什麼是 RAG？"
    ]

    # 5. 簡單 RAG 演示
    try:
        print("\n" + "="*60)
        print("演示 1：簡單 RAG")
        print("="*60)
        simple_rag = SimpleRAG(num_passages=3)
        # demo_simple_rag(simple_rag, questions[:2])
        print("需要配置檢索器才能運行實際演示")
    except Exception as e:
        print(f"錯誤：{e}")

    # 6. 帶引用 RAG 演示
    try:
        print("\n" + "="*60)
        print("演示 2：帶引用 RAG")
        print("="*60)
        citation_rag = RAGWithSourceCitation(num_passages=3)
        print("需要配置檢索器才能運行實際演示")
    except Exception as e:
        print(f"錯誤：{e}")

    # 7. 自適應 RAG 演示
    try:
        print("\n" + "="*60)
        print("演示 3：自適應 RAG")
        print("="*60)
        adaptive_questions = [
            "2+2等於多少？",  # 不需要檢索
            "什麼是量子機器學習？",  # 需要檢索
        ]
        adaptive_rag = AdaptiveRAG(num_passages=3)
        # demo_adaptive_rag(adaptive_rag, adaptive_questions)
        print("需要配置檢索器才能運行實際演示")
    except Exception as e:
        print(f"錯誤：{e}")

    # 總結
    print("\n" + "="*60)
    print("教學完成！")
    print("="*60)
    print("""
    你已經學會了：
    1. ✓ RAG 的核心概念和優勢
    2. ✓ 向量數據庫（ChromaDB）設置
    3. ✓ 基礎 RAG 模組構建
    4. ✓ 帶來源引用的 RAG
    5. ✓ 多跳推理 RAG
    6. ✓ 自適應 RAG
    7. ✓ RAG 優化技術

    RAG 系統設計要點：
    - 選擇合適的向量數據庫
    - 優化文檔分塊策略
    - 調整檢索數量（k 值）
    - 設計好的提示模板
    - 評估和優化檢索質量

    進階技巧：
    - 混合檢索（向量 + 關鍵詞）
    - 重排序（Reranking）
    - 查詢擴展
    - 上下文壓縮
    - 多模態 RAG

    下一步：
    - 學習 Agent 構建（06_Agent構建.py）
    - 學習評估指標（07_評估指標.py）
    - 將 RAG 應用到實際項目
    """)


if __name__ == "__main__":
    main()
