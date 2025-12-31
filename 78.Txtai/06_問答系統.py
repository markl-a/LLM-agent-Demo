"""
Txtai - 問答系統範例

本範例展示：
1. 基於上下文的問答
2. 多文檔問答
3. 答案提取
4. 置信度評估
5. RAG 模式問答

安裝：pip install txtai sentence-transformers transformers
"""

from txtai import Embeddings, Extractor


# ============================================================================
# 範例 1: 基本問答系統
# ============================================================================

def example_1_basic_qa():
    """創建基本的問答系統"""
    print("\n" + "="*60)
    print("範例 1: 基本問答系統")
    print("="*60)

    # 創建嵌入索引
    embeddings = Embeddings({"content": True})

    # 知識庫
    context = [
        "Paris is the capital city of France.",
        "The Eiffel Tower is located in Paris.",
        "France is a country in Western Europe.",
        "French is the official language of France.",
    ]

    # 索引知識庫
    embeddings.index([(i, text, None) for i, text in enumerate(context)])

    # 問答
    questions = [
        "What is the capital of France?",
        "Where is the Eiffel Tower?",
        "What language do they speak in France?",
    ]

    print("問答示例:\n")
    for question in questions:
        # 搜索最相關的答案
        results = embeddings.search(question, limit=1)
        if results:
            print(f"Q: {question}")
            print(f"A: {results[0]['text']}")
            print(f"   (置信度: {results[0]['score']:.4f})\n")


# ============================================================================
# 範例 2: 使用 Extractor 進行答案提取
# ============================================================================

def example_2_answer_extraction():
    """使用 Extractor 提取精確答案"""
    print("\n" + "="*60)
    print("範例 2: 答案提取")
    print("="*60)

    try:
        # 創建嵌入和提取器
        embeddings = Embeddings({"content": True, "path": "sentence-transformers/nli-mpnet-base-v2"})

        # 使用問答模型
        extractor = Extractor(embeddings, "distilbert-base-cased-distilled-squad")

        # 知識庫
        data = [
            "Python was created by Guido van Rossum and first released in 1991.",
            "Python is known for its simple and readable syntax.",
            "Python is widely used in data science, web development, and automation.",
        ]

        # 索引
        embeddings.index([(i, text, None) for i, text in enumerate(data)])

        # 問題
        questions = [
            "Who created Python?",
            "When was Python first released?",
            "What is Python used for?",
        ]

        print("答案提取:\n")
        for question in questions:
            # 提取答案
            answer = extractor([(question, data)])
            print(f"Q: {question}")
            print(f"A: {answer}\n")

    except Exception as e:
        print(f"注意: Extractor 需要額外的模型下載")
        print(f"錯誤: {str(e)}")


# ============================================================================
# 範例 3: 多文檔問答
# ============================================================================

def example_3_multi_document_qa():
    """從多個文檔中回答問題"""
    print("\n" + "="*60)
    print("範例 3: 多文檔問答")
    print("="*60)

    embeddings = Embeddings({"content": True})

    # 多主題知識庫
    documents = [
        # 關於科技
        "Artificial Intelligence is transforming industries worldwide.",
        "Machine learning algorithms can learn from data without explicit programming.",
        # 關於地理
        "Mount Everest is the tallest mountain in the world at 8,848 meters.",
        "The Pacific Ocean is the largest ocean on Earth.",
        # 關於歷史
        "The Roman Empire was one of the most powerful civilizations in history.",
        "The Great Wall of China was built over many centuries.",
    ]

    embeddings.index([(i, doc, None) for i, doc in enumerate(documents)])

    questions = [
        "What is AI doing to industries?",
        "How tall is Mount Everest?",
        "Tell me about the Roman Empire.",
    ]

    print("多文檔問答:\n")
    for question in questions:
        results = embeddings.search(question, limit=1)
        if results:
            print(f"Q: {question}")
            print(f"A: {results[0]['text']}\n")


# ============================================================================
# 範例 4: 帶元數據的問答
# ============================================================================

def example_4_metadata_qa():
    """使用元數據增強問答"""
    print("\n" + "="*60)
    print("範例 4: 帶元數據的問答")
    print("="*60)

    embeddings = Embeddings({"content": True})

    documents = [
        (0, "Python 3.11 was released in October 2022.", {
            "topic": "Python", "type": "release", "year": 2022
        }),
        (1, "Python is used by millions of developers worldwide.", {
            "topic": "Python", "type": "statistics"
        }),
        (2, "JavaScript is the most popular language for web development.", {
            "topic": "JavaScript", "type": "statistics"
        }),
    ]

    embeddings.index(documents)

    # 帶過濾的問答
    question = "When was Python 3.11 released?"
    sql = f"SELECT text, score FROM txtai WHERE similar('{question}') AND topic = 'Python' LIMIT 1"

    results = embeddings.search(sql)

    print(f"Q: {question}")
    if results:
        print(f"A: {results[0]['text']}")
        print(f"   主題: Python, 評分: {results[0]['score']:.4f}")


# ============================================================================
# 範例 5: 對話式問答
# ============================================================================

def example_5_conversational_qa():
    """構建對話式問答系統"""
    print("\n" + "="*60)
    print("範例 5: 對話式問答")
    print("="*60)

    embeddings = Embeddings({"content": True})

    # 關於某個主題的詳細信息
    knowledge = [
        "Docker is a containerization platform.",
        "Docker containers are lightweight and portable.",
        "Docker uses images to create containers.",
        "Docker Compose helps manage multi-container applications.",
    ]

    embeddings.index([(i, text, None) for i, text in enumerate(knowledge)])

    # 對話序列
    conversation = [
        "What is Docker?",
        "How are Docker containers different?",
        "What is Docker Compose used for?",
    ]

    print("對話式問答:\n")
    for i, question in enumerate(conversation, 1):
        results = embeddings.search(question, limit=1)
        if results:
            print(f"輪次 {i}:")
            print(f"  User: {question}")
            print(f"  Bot:  {results[0]['text']}\n")


# ============================================================================
# 範例 6-10: 更多問答應用
# ============================================================================

def example_6_faq_system():
    """常見問題解答系統"""
    print("\n" + "="*60)
    print("範例 6: FAQ 系統")
    print("="*60)

    embeddings = Embeddings({"content": True})

    faqs = [
        "Q: How do I reset my password? A: Click 'Forgot Password' on the login page.",
        "Q: What payment methods do you accept? A: We accept credit cards, PayPal, and bank transfers.",
        "Q: How long does shipping take? A: Standard shipping takes 5-7 business days.",
        "Q: What is your return policy? A: Items can be returned within 30 days of purchase.",
    ]

    embeddings.index([(i, faq, None) for i, faq in enumerate(faqs)])

    user_questions = [
        "I forgot my password",
        "Do you accept PayPal?",
        "How fast is delivery?",
    ]

    print("FAQ 匹配:\n")
    for question in user_questions:
        results = embeddings.search(question, limit=1)
        if results:
            print(f"用戶: {question}")
            print(f"答案: {results[0]['text']}\n")


def example_7_technical_qa():
    """技術文檔問答"""
    print("\n" + "="*60)
    print("範例 7: 技術文檔問答")
    print("="*60)

    embeddings = Embeddings({"content": True})

    docs = [
        "To install the package, run: pip install txtai",
        "Create an embeddings index with: embeddings = Embeddings()",
        "Index documents using: embeddings.index(data)",
        "Search with: embeddings.search(query, limit=10)",
    ]

    embeddings.index([(i, doc, None) for i, doc in enumerate(docs)])

    questions = [
        "How do I install txtai?",
        "How to create an index?",
        "How do I search?",
    ]

    print("技術問答:\n")
    for q in questions:
        results = embeddings.search(q, limit=1)
        if results:
            print(f"Q: {q}")
            print(f"A: {results[0]['text']}\n")


def example_8_educational_qa():
    """教育問答系統"""
    print("\n" + "="*60)
    print("範例 8: 教育問答")
    print("="*60)

    embeddings = Embeddings({"content": True})

    lessons = [
        "Photosynthesis is the process plants use to convert light into energy.",
        "The water cycle includes evaporation, condensation, and precipitation.",
        "Mitosis is cell division that results in two identical daughter cells.",
    ]

    embeddings.index([(i, lesson, None) for i, lesson in enumerate(lessons)])

    student_questions = [
        "What is photosynthesis?",
        "Explain the water cycle",
    ]

    print("學生問答:\n")
    for q in student_questions:
        results = embeddings.search(q, limit=1)
        if results:
            print(f"學生: {q}")
            print(f"老師: {results[0]['text']}\n")


def example_9_product_qa():
    """產品信息問答"""
    print("\n" + "="*60)
    print("範例 9: 產品信息問答")
    print("="*60)

    embeddings = Embeddings({"content": True})

    products = [
        "The XPhone Pro has a 6.5-inch OLED display and 128GB storage.",
        "The XPhone Pro battery lasts up to 24 hours on a single charge.",
        "The XPhone Pro features a triple camera system with 48MP main sensor.",
    ]

    embeddings.index([(i, prod, None) for i, prod in enumerate(products)])

    customer_questions = [
        "What's the screen size?",
        "How long does the battery last?",
        "Tell me about the camera",
    ]

    print("客戶咨詢:\n")
    for q in customer_questions:
        results = embeddings.search(q, limit=1)
        if results:
            print(f"客戶: {q}")
            print(f"客服: {results[0]['text']}\n")


def example_10_confidence_scoring():
    """置信度評估"""
    print("\n" + "="*60)
    print("範例 10: 置信度評估")
    print("="*60)

    embeddings = Embeddings({"content": True})

    knowledge = [
        "Machine learning is a subset of artificial intelligence.",
        "Neural networks are inspired by the human brain.",
        "Deep learning uses multiple layers of neural networks.",
    ]

    embeddings.index([(i, text, None) for i, text in enumerate(knowledge)])

    questions = [
        ("What is machine learning?", "高相關"),
        ("How do computers work?", "低相關"),
    ]

    print("置信度評估:\n")
    for question, expected in questions:
        results = embeddings.search(question, limit=1)
        if results:
            score = results[0]['score']
            confidence = "高" if score > 0.5 else "中" if score > 0.3 else "低"

            print(f"問題: {question}")
            print(f"答案: {results[0]['text']}")
            print(f"置信度: {confidence} (評分: {score:.4f})")
            print(f"預期: {expected}\n")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*60)
    print("❓ Txtai - 問答系統範例")
    print("="*60)

    example_1_basic_qa()
    example_2_answer_extraction()
    example_3_multi_document_qa()
    example_4_metadata_qa()
    example_5_conversational_qa()
    example_6_faq_system()
    example_7_technical_qa()
    example_8_educational_qa()
    example_9_product_qa()
    example_10_confidence_scoring()

    print("\n" + "="*60)
    print("✓ 所有問答系統範例完成！")
    print("="*60)


if __name__ == '__main__':
    main()
