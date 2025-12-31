"""
最簡單的 Ollama 本地模型調用示例
演示如何使用本地運行的開源 LLM
"""

import ollama

def main():
    print("=" * 50)
    print("Ollama 本地模型調用示例")
    print("=" * 50)

    # 確保已安裝並運行 Ollama
    # 1. 安裝：https://ollama.ai/
    # 2. 下載模型：ollama pull llama2
    # 3. 啟動服務：ollama serve

    print("\n正在調用本地模型（llama2）...")

    # 發送簡單的對話請求
    response = ollama.chat(
        model='llama2',  # 使用本地的 Llama2 模型
        messages=[
            {'role': 'user', 'content': '用一句話介紹什麼是深度學習'}
        ]
    )

    # 提取並打印回復
    answer = response['message']['content']
    print(f"\n問題：用一句話介紹什麼是深度學習")
    print(f"回答：{answer}\n")
    print("=" * 50)

if __name__ == "__main__":
    main()
