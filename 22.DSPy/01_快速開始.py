"""
DSPy 快速開始範例
=================

本範例展示 DSPy 的基礎使用方法：
1. 配置語言模型
2. 定義簽名（Signature）
3. 使用基本的 Predict 模塊
4. 處理輸入輸出

作者：DSPy 學習示例
日期：2025-12-15
"""

import dspy
from typing import Optional


# ============================================================================
# 1. 配置語言模型
# ============================================================================

def configure_language_model():
    """
    配置 DSPy 使用的語言模型

    DSPy 通過 LiteLLM 支持 100+ 種模型提供商：
    - OpenAI: 'openai/gpt-4o-mini', 'openai/gpt-4o'
    - Anthropic: 'anthropic/claude-3-5-sonnet-20241022'
    - Cohere: 'cohere/command-r-plus'
    - 本地模型: 'ollama/llama2'
    """

    # 方式 1: 使用 OpenAI 模型（需要 OPENAI_API_KEY 環境變數）
    lm = dspy.LM('openai/gpt-4o-mini')

    # 方式 2: 直接傳入 API 密鑰
    # lm = dspy.LM('openai/gpt-4o-mini', api_key='your-api-key-here')

    # 方式 3: 使用其他提供商
    # lm = dspy.LM('anthropic/claude-3-5-sonnet-20241022', api_key='your-key')

    # 方式 4: 使用本地模型（需要先啟動 Ollama）
    # lm = dspy.LM('ollama/llama2', api_base='http://localhost:11434')

    # 配置為默認模型
    dspy.configure(lm=lm)

    print(f"✓ 已配置語言模型: {lm.model}")
    return lm


# ============================================================================
# 2. 定義簽名（Signature）
# ============================================================================

class BasicQA(dspy.Signature):
    """回答用戶的問題"""

    # 輸入字段
    question = dspy.InputField(desc="用戶的問題")

    # 輸出字段
    answer = dspy.OutputField(desc="問題的答案")


class TranslationSignature(dspy.Signature):
    """將文本從一種語言翻譯為另一種語言"""

    text = dspy.InputField(desc="要翻譯的文本")
    source_language = dspy.InputField(desc="源語言")
    target_language = dspy.InputField(desc="目標語言")
    translation = dspy.OutputField(desc="翻譯後的文本")


class SentimentAnalysis(dspy.Signature):
    """分析文本的情感傾向"""

    text = dspy.InputField()
    sentiment = dspy.OutputField(desc="情感：正面、負面或中性")
    confidence = dspy.OutputField(desc="置信度分數（0-1）")


# ============================================================================
# 3. 使用 Predict 模塊
# ============================================================================

def basic_prediction_example():
    """
    基礎預測範例
    使用 dspy.Predict 進行簡單的問答
    """
    print("\n" + "="*60)
    print("基礎預測範例")
    print("="*60)

    # 創建預測器
    predictor = dspy.Predict(BasicQA)

    # 進行預測
    questions = [
        "什麼是機器學習？",
        "Python 和 JavaScript 的主要區別是什麼？",
        "如何優化深度學習模型？"
    ]

    for question in questions:
        response = predictor(question=question)
        print(f"\n問題：{question}")
        print(f"答案：{response.answer}")


def translation_example():
    """
    翻譯範例
    展示如何使用多個輸入字段
    """
    print("\n" + "="*60)
    print("翻譯範例")
    print("="*60)

    # 創建翻譯器
    translator = dspy.Predict(TranslationSignature)

    # 進行翻譯
    translations = [
        ("Hello, world!", "English", "Chinese"),
        ("機器學習很有趣", "Chinese", "English"),
        ("Bonjour", "French", "Japanese")
    ]

    for text, src_lang, tgt_lang in translations:
        result = translator(
            text=text,
            source_language=src_lang,
            target_language=tgt_lang
        )
        print(f"\n原文 ({src_lang}): {text}")
        print(f"譯文 ({tgt_lang}): {result.translation}")


def sentiment_analysis_example():
    """
    情感分析範例
    展示如何處理多個輸出字段
    """
    print("\n" + "="*60)
    print("情感分析範例")
    print("="*60)

    # 創建分析器
    analyzer = dspy.Predict(SentimentAnalysis)

    # 分析文本
    texts = [
        "這部電影太棒了！我非常喜歡！",
        "產品質量很差，完全浪費錢。",
        "還可以，沒有特別好也沒有特別差。"
    ]

    for text in texts:
        result = analyzer(text=text)
        print(f"\n文本：{text}")
        print(f"情感：{result.sentiment}")
        print(f"置信度：{result.confidence}")


# ============================================================================
# 4. 使用簡短字符串形式的簽名
# ============================================================================

def short_signature_example():
    """
    使用簡短字符串定義簽名
    這是最快捷的方式，適合簡單任務
    """
    print("\n" + "="*60)
    print("簡短簽名範例")
    print("="*60)

    # 方式 1: question -> answer
    qa = dspy.Predict("question -> answer")
    result = qa(question="DSPy 和 LangChain 有什麼區別？")
    print(f"\n問題：DSPy 和 LangChain 有什麼區別？")
    print(f"答案：{result.answer}")

    # 方式 2: 帶類型的簽名
    classifier = dspy.Predict("text -> is_spam: bool")
    result = classifier(text="恭喜你中獎了！點擊這裡領取獎品！")
    print(f"\n文本：恭喜你中獎了！點擊這裡領取獎品！")
    print(f"是否為垃圾信息：{result.is_spam}")

    # 方式 3: 多輸入多輸出
    summarizer = dspy.Predict("document, max_words: int -> summary, key_points: list[str]")
    result = summarizer(
        document="人工智能是計算機科學的一個分支。它試圖理解智能的實質，並生產出一種新的能以人類智能相似的方式做出反應的智能機器。",
        max_words=20
    )
    print(f"\n摘要：{result.summary}")
    print(f"關鍵點：{result.key_points}")


# ============================================================================
# 5. 批量處理
# ============================================================================

def batch_processing_example():
    """
    批量處理範例
    展示如何高效處理多個輸入
    """
    print("\n" + "="*60)
    print("批量處理範例")
    print("="*60)

    predictor = dspy.Predict(BasicQA)

    # 準備批量數據
    questions = [
        "什麼是深度學習？",
        "什麼是自然語言處理？",
        "什麼是計算機視覺？"
    ]

    # 逐個處理
    print("\n處理結果：")
    for i, question in enumerate(questions, 1):
        result = predictor(question=question)
        print(f"\n{i}. Q: {question}")
        print(f"   A: {result.answer[:100]}...")  # 只顯示前100字符


# ============================================================================
# 6. 檢查生成的提示詞
# ============================================================================

def inspect_prompts():
    """
    檢查 DSPy 自動生成的提示詞
    這對於理解和調試很有幫助
    """
    print("\n" + "="*60)
    print("檢查生成的提示詞")
    print("="*60)

    predictor = dspy.Predict(BasicQA)

    # 進行一次預測
    result = predictor(question="什麼是 DSPy？")

    # 檢查最後使用的提示詞
    print("\n生成的提示詞：")
    print("-" * 60)
    # 注意：具體的檢查方法可能因 DSPy 版本而異
    # 可以通過 lm.inspect_history() 查看歷史記錄
    print(result.answer)


# ============================================================================
# 主程序
# ============================================================================

def main():
    """
    主函數：運行所有範例
    """
    print("DSPy 快速開始範例")
    print("=" * 60)

    try:
        # 配置語言模型
        lm = configure_language_model()

        # 運行各種範例
        basic_prediction_example()
        translation_example()
        sentiment_analysis_example()
        short_signature_example()
        batch_processing_example()
        inspect_prompts()

        print("\n" + "="*60)
        print("所有範例運行完成！")
        print("="*60)

    except Exception as e:
        print(f"\n錯誤：{e}")
        print("\n提示：")
        print("1. 確保已安裝 DSPy: pip install dspy-ai")
        print("2. 設置環境變數: export OPENAI_API_KEY='your-key'")
        print("3. 或在代碼中直接傳入 api_key 參數")


if __name__ == "__main__":
    # 注意：實際運行前需要設置 API 密鑰
    # 方式 1: 設置環境變數
    #   export OPENAI_API_KEY='your-api-key'
    # 方式 2: 在 configure_language_model() 函數中直接傳入

    main()


"""
使用說明
========

1. 安裝依賴：
   pip install dspy-ai

2. 設置 API 密鑰：
   export OPENAI_API_KEY='your-openai-api-key'

3. 運行程序：
   python 01_快速開始.py

4. 關鍵概念：
   - Signature: 定義輸入輸出的規範
   - Predict: 基礎預測模塊
   - InputField/OutputField: 字段定義
   - dspy.configure(): 配置默認模型

5. 下一步學習：
   - 02_Signature定義.py - 深入學習簽名定義
   - 06_ChainOfThought.py - 學習思維鏈推理
"""
