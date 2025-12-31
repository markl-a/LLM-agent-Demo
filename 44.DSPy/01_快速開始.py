"""
DSPy 快速開始範例

本模組展示 DSPy 的基礎用法，包括：
1. 環境配置和初始化
2. 基本簽名定義
3. Predict 模組使用
4. ChainOfThought 模組使用
5. 簡單的資料處理流程

作者：DSPy 教學團隊
日期：2025-01
"""

import os
import dspy
from typing import List, Optional
from dataclasses import dataclass


# ==================== 配置部分 ====================

def setup_dspy_openai():
    """
    配置 DSPy 使用 OpenAI 作為語言模型

    這是最常用的配置方式，需要設置 OPENAI_API_KEY 環境變數
    """
    # 從環境變數獲取 API 金鑰
    api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")

    # 創建 OpenAI 語言模型實例
    # model: 選擇的模型，如 gpt-4, gpt-3.5-turbo
    # max_tokens: 最大生成的 token 數量
    # temperature: 控制輸出的隨機性 (0-2)
    lm = dspy.OpenAI(
        model="gpt-4",
        max_tokens=500,
        temperature=0.7
    )

    # 配置 DSPy 全局設置
    dspy.settings.configure(lm=lm)
    print("✓ DSPy 已配置完成，使用 OpenAI GPT-4")
    return lm


def setup_dspy_anthropic():
    """
    配置 DSPy 使用 Anthropic Claude 作為語言模型

    Claude 在長文本處理和推理任務上表現優異
    """
    api_key = os.getenv("ANTHROPIC_API_KEY", "your-api-key-here")

    # 創建 Anthropic 語言模型實例
    lm = dspy.Claude(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        api_key=api_key
    )

    dspy.settings.configure(lm=lm)
    print("✓ DSPy 已配置完成，使用 Claude 3.5 Sonnet")
    return lm


# ==================== 簽名定義 ====================

class BasicQA(dspy.Signature):
    """
    最基本的問答簽名

    簽名定義了模組的輸入和輸出結構
    DSPy 會根據這個簽名自動生成適當的提示
    """
    # 輸入欄位
    question = dspy.InputField(desc="用戶的問題")

    # 輸出欄位
    answer = dspy.OutputField(desc="簡潔準確的答案")


class SentimentAnalysis(dspy.Signature):
    """分析文本的情感傾向"""
    text = dspy.InputField(desc="要分析的文本內容")
    sentiment = dspy.OutputField(desc="情感分類：positive（正面）、negative（負面）或 neutral（中性）")
    confidence = dspy.OutputField(desc="置信度分數（0-100）")


class TextSummarization(dspy.Signature):
    """文本摘要生成"""
    text = dspy.InputField(desc="需要摘要的長文本")
    max_words = dspy.InputField(desc="摘要的最大字數")
    summary = dspy.OutputField(desc="簡潔的摘要")


class LanguageTranslation(dspy.Signature):
    """語言翻譯"""
    source_text = dspy.InputField(desc="原文")
    target_language = dspy.InputField(desc="目標語言")
    translation = dspy.OutputField(desc="翻譯結果")


class CodeExplanation(dspy.Signature):
    """程式碼解釋"""
    code = dspy.InputField(desc="程式碼片段")
    programming_language = dspy.InputField(desc="程式語言")
    explanation = dspy.OutputField(desc="詳細的程式碼解釋")


# ==================== 基本模組使用 ====================

def example_basic_predict():
    """
    範例 1：使用基本的 Predict 模組

    Predict 是最簡單的 DSPy 模組，直接根據簽名進行預測
    適合簡單的任務，不需要複雜推理
    """
    print("\n" + "="*60)
    print("範例 1：基本 Predict 模組")
    print("="*60)

    # 創建預測模組
    qa = dspy.Predict(BasicQA)

    # 使用模組進行預測
    questions = [
        "什麼是機器學習？",
        "Python 和 JavaScript 的主要區別是什麼？",
        "如何學習深度學習？"
    ]

    for question in questions:
        result = qa(question=question)
        print(f"\n問題：{question}")
        print(f"答案：{result.answer}")


def example_chain_of_thought():
    """
    範例 2：使用 ChainOfThought 模組

    ChainOfThought 會先進行思考推理，再給出答案
    適合需要複雜推理的任務
    """
    print("\n" + "="*60)
    print("範例 2：ChainOfThought 模組")
    print("="*60)

    # 創建思維鏈模組
    cot_qa = dspy.ChainOfThought(BasicQA)

    # 測試複雜問題
    complex_questions = [
        "如果一個人每天學習 2 小時，一週學習 5 天，那麼一年能學習多少小時？",
        "為什麼深度學習需要大量數據？",
        "區塊鏈技術的主要優勢和劣勢是什麼？"
    ]

    for question in complex_questions:
        result = cot_qa(question=question)
        print(f"\n問題：{question}")
        print(f"推理過程：{result.rationale}")
        print(f"答案：{result.answer}")


def example_sentiment_analysis():
    """
    範例 3：情感分析

    展示如何使用 DSPy 進行文本情感分析
    """
    print("\n" + "="*60)
    print("範例 3：情感分析")
    print("="*60)

    # 創建情感分析模組
    sentiment = dspy.Predict(SentimentAnalysis)

    # 測試文本
    texts = [
        "這個產品真的很棒！質量超出預期，非常滿意！",
        "服務態度很差，完全不推薦。",
        "還可以，符合預期。",
        "今天天氣不錯，適合出門。"
    ]

    for text in texts:
        result = sentiment(text=text)
        print(f"\n文本：{text}")
        print(f"情感：{result.sentiment}")
        print(f"置信度：{result.confidence}")


def example_summarization():
    """
    範例 4：文本摘要

    展示如何使用 DSPy 進行文本摘要生成
    """
    print("\n" + "="*60)
    print("範例 4：文本摘要")
    print("="*60)

    # 創建摘要模組
    summarizer = dspy.ChainOfThought(TextSummarization)

    # 長文本範例
    long_text = """
    人工智能（Artificial Intelligence，AI）是計算機科學的一個分支，
    旨在創建能夠執行通常需要人類智能的任務的系統。這些任務包括視覺感知、
    語音識別、決策制定和語言翻譯等。AI 的發展經歷了多個階段，從早期的
    符號主義到現代的機器學習和深度學習。深度學習是 AI 的一個子領域，
    使用多層神經網絡來學習數據的複雜模式。近年來，隨著計算能力的提升
    和大數據的可用性，AI 取得了顯著進展，特別是在自然語言處理、計算機
    視覺和自動駕駛等領域。然而，AI 也面臨著倫理、隱私和安全等挑戰，
    需要社會各界共同努力來確保 AI 技術的負責任發展和應用。
    """

    # 生成不同長度的摘要
    for max_words in [30, 50, 80]:
        result = summarizer(text=long_text, max_words=str(max_words))
        print(f"\n摘要（{max_words} 字以內）：")
        print(result.summary)


def example_translation():
    """
    範例 5：語言翻譯

    展示如何使用 DSPy 進行語言翻譯
    """
    print("\n" + "="*60)
    print("範例 5：語言翻譯")
    print("="*60)

    # 創建翻譯模組
    translator = dspy.Predict(LanguageTranslation)

    # 翻譯範例
    translations = [
        ("Hello, how are you?", "中文"),
        ("機器學習是人工智能的一個重要分支", "英文"),
        ("こんにちは、元気ですか？", "中文"),
    ]

    for source, target in translations:
        result = translator(source_text=source, target_language=target)
        print(f"\n原文：{source}")
        print(f"目標語言：{target}")
        print(f"翻譯：{result.translation}")


def example_code_explanation():
    """
    範例 6：程式碼解釋

    展示如何使用 DSPy 解釋程式碼
    """
    print("\n" + "="*60)
    print("範例 6：程式碼解釋")
    print("="*60)

    # 創建程式碼解釋模組
    explainer = dspy.ChainOfThought(CodeExplanation)

    # 程式碼範例
    code_snippet = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
    """

    result = explainer(
        code=code_snippet,
        programming_language="Python"
    )

    print(f"\n程式碼：\n{code_snippet}")
    print(f"\n推理過程：{result.rationale}")
    print(f"\n解釋：{result.explanation}")


# ==================== 實用工具函數 ====================

class QuickProcessor:
    """
    快速處理器類

    封裝常用的 DSPy 操作，提供更簡潔的 API
    """

    def __init__(self, model_name="gpt-4"):
        """初始化處理器"""
        self.model_name = model_name
        self.qa_module = dspy.Predict(BasicQA)
        self.sentiment_module = dspy.Predict(SentimentAnalysis)

    def ask(self, question: str) -> str:
        """快速問答"""
        result = self.qa_module(question=question)
        return result.answer

    def analyze_sentiment(self, text: str) -> tuple:
        """快速情感分析"""
        result = self.sentiment_module(text=text)
        return result.sentiment, result.confidence


def batch_process_questions(questions: List[str]) -> List[str]:
    """
    批量處理問題

    Args:
        questions: 問題列表

    Returns:
        答案列表
    """
    qa = dspy.Predict(BasicQA)
    answers = []

    for question in questions:
        result = qa(question=question)
        answers.append(result.answer)

    return answers


def compare_predict_vs_cot(question: str):
    """
    比較 Predict 和 ChainOfThought 的輸出

    Args:
        question: 要測試的問題
    """
    print(f"\n問題：{question}")
    print("-" * 60)

    # 使用 Predict
    predict = dspy.Predict(BasicQA)
    predict_result = predict(question=question)
    print(f"\nPredict 答案：{predict_result.answer}")

    # 使用 ChainOfThought
    cot = dspy.ChainOfThought(BasicQA)
    cot_result = cot(question=question)
    print(f"\nChainOfThought 推理：{cot_result.rationale}")
    print(f"ChainOfThought 答案：{cot_result.answer}")


# ==================== 主程序 ====================

def main():
    """
    主函數：演示所有功能
    """
    print("="*60)
    print("DSPy 快速開始教學")
    print("="*60)

    # 步驟 1：配置 DSPy
    print("\n步驟 1：配置 DSPy")
    print("-" * 60)
    try:
        setup_dspy_openai()
    except Exception as e:
        print(f"配置失敗：{e}")
        print("請設置正確的 OPENAI_API_KEY 環境變數")
        return

    # 步驟 2：運行範例
    print("\n步驟 2：運行各種範例")
    print("-" * 60)

    try:
        # 範例 1：基本 Predict
        example_basic_predict()

        # 範例 2：ChainOfThought
        example_chain_of_thought()

        # 範例 3：情感分析
        example_sentiment_analysis()

        # 範例 4：文本摘要
        example_summarization()

        # 範例 5：翻譯
        example_translation()

        # 範例 6：程式碼解釋
        example_code_explanation()

        # 步驟 3：使用快速處理器
        print("\n" + "="*60)
        print("步驟 3：使用快速處理器")
        print("="*60)

        processor = QuickProcessor()
        answer = processor.ask("什麼是 DSPy？")
        print(f"\n快速問答結果：{answer}")

        sentiment, confidence = processor.analyze_sentiment("這個框架真的很棒！")
        print(f"\n快速情感分析：{sentiment}（置信度：{confidence}）")

        # 步驟 4：批量處理
        print("\n" + "="*60)
        print("步驟 4：批量處理")
        print("="*60)

        questions = [
            "什麼是深度學習？",
            "如何開始學習 Python？",
            "什麼是向量數據庫？"
        ]

        answers = batch_process_questions(questions)
        for q, a in zip(questions, answers):
            print(f"\nQ: {q}")
            print(f"A: {a}")

        # 步驟 5：比較不同模組
        print("\n" + "="*60)
        print("步驟 5：比較 Predict vs ChainOfThought")
        print("="*60)

        compare_predict_vs_cot("為什麼海水是鹹的？")

    except Exception as e:
        print(f"\n執行錯誤：{e}")
        import traceback
        traceback.print_exc()

    # 總結
    print("\n" + "="*60)
    print("教學完成！")
    print("="*60)
    print("""
    你已經學會了：
    1. ✓ 配置 DSPy 環境
    2. ✓ 定義基本簽名
    3. ✓ 使用 Predict 模組
    4. ✓ 使用 ChainOfThought 模組
    5. ✓ 處理各種 NLP 任務
    6. ✓ 批量處理和工具封裝

    下一步：
    - 學習更複雜的簽名定義（02_簽名定義.py）
    - 學習模組組合（03_模組組合.py）
    - 學習提示優化（04_提示優化.py）
    """)


if __name__ == "__main__":
    main()
