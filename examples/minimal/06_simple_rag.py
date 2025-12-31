"""
最簡單的 RAG（檢索增強生成）實現
演示如何結合知識庫回答問題
"""

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 模擬知識庫（實際應用中可能是向量數據庫）
KNOWLEDGE_BASE = {
    "Python": "Python 是一種高級編程語言，由 Guido van Rossum 於 1991 年創建。它以簡潔的語法和強大的功能著稱。",
    "JavaScript": "JavaScript 是網頁開發的核心語言，由 Brendan Eich 於 1995 年創建。它可以在瀏覽器和服務器端運行。",
    "Rust": "Rust 是一種系統級編程語言，由 Mozilla 於 2010 年發布。它注重安全性、並發性和性能。"
}

def retrieve(query):
    """檢索：從知識庫中找到相關信息"""
    print(f"\n[檢索] 搜索關鍵詞：{query}")

    # 簡單的關鍵詞匹配（實際應用中使用向量相似度）
    results = []
    for key, value in KNOWLEDGE_BASE.items():
        if key.lower() in query.lower():
            results.append(value)
            print(f"[檢索] 找到相關內容：{key}")

    return results

def augment(query, retrieved_docs):
    """增強：將檢索到的信息整合到提示詞中"""
    if not retrieved_docs:
        context = "沒有找到相關信息"
    else:
        context = "\n".join(retrieved_docs)

    # 構建增強後的提示詞
    augmented_prompt = f"""基於以下背景信息回答問題：

背景信息：
{context}

問題：{query}

請基於背景信息進行回答。如果背景信息不足，請說明。"""

    return augmented_prompt

def generate(prompt):
    """生成：使用 LLM 生成回答"""
    print(f"\n[生成] 正在生成回答...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def rag_pipeline(query):
    """完整的 RAG 流程：檢索 -> 增強 -> 生成"""
    # 1. 檢索相關文檔
    docs = retrieve(query)

    # 2. 增強提示詞
    augmented_prompt = augment(query, docs)

    # 3. 生成回答
    answer = generate(augmented_prompt)

    return answer

def main():
    print("=" * 50)
    print("簡單 RAG 示例")
    print("=" * 50)

    # 測試問題
    question = "請介紹一下 Python 的創建者"

    print(f"\n用戶問題：{question}")
    answer = rag_pipeline(question)

    print(f"\n最終回答：{answer}\n")
    print("=" * 50)

if __name__ == "__main__":
    main()
