"""
DSPy Signature 定義詳解
========================

本範例深入探討 DSPy 中 Signature（簽名）的各種定義方式和最佳實踐：
1. 簡短字符串形式
2. 類形式定義
3. 帶描述的字段
4. 複雜類型處理
5. Signature 的最佳實踐

Signature 是 DSPy 的核心概念，它聲明式地定義了模型應該完成的任務。

作者：DSPy 學習示例
日期：2025-12-15
"""

import dspy
from typing import List, Dict, Optional, Union
from pydantic import BaseModel, Field


# ============================================================================
# 1. 簡短字符串形式的 Signature
# ============================================================================

def short_string_signatures():
    """
    最簡潔的簽名定義方式
    適合快速原型開發和簡單任務
    """
    print("\n" + "="*60)
    print("1. 簡短字符串形式的 Signature")
    print("="*60)

    # 基本形式：input -> output
    qa = dspy.Predict("question -> answer")
    result = qa(question="什麼是 Signature？")
    print(f"\n基本形式 'question -> answer'")
    print(f"Q: 什麼是 Signature？")
    print(f"A: {result.answer[:150]}...")

    # 多輸入：input1, input2 -> output
    context_qa = dspy.Predict("context, question -> answer")
    result = context_qa(
        context="DSPy 是 Stanford 開發的 LLM 編程框架",
        question="誰開發了 DSPy？"
    )
    print(f"\n多輸入 'context, question -> answer'")
    print(f"A: {result.answer}")

    # 多輸出：input -> output1, output2
    analyzer = dspy.Predict("text -> summary, sentiment")
    result = analyzer(text="這個產品很棒！我非常滿意，強烈推薦給大家。")
    print(f"\n多輸出 'text -> summary, sentiment'")
    print(f"摘要: {result.summary}")
    print(f"情感: {result.sentiment}")

    # 帶類型標註：input -> output: type
    classifier = dspy.Predict("text -> is_positive: bool, confidence: float")
    result = classifier(text="這次經驗很糟糕")
    print(f"\n帶類型 'text -> is_positive: bool, confidence: float'")
    print(f"是正面: {result.is_positive}")
    print(f"置信度: {result.confidence}")

    # 列表類型：input -> output: list[type]
    extractor = dspy.Predict("text -> keywords: list[str]")
    result = extractor(text="人工智能、機器學習和深度學習是現代科技的重要領域")
    print(f"\n列表類型 'text -> keywords: list[str]'")
    print(f"關鍵詞: {result.keywords}")


# ============================================================================
# 2. 類形式的 Signature 定義
# ============================================================================

class DetailedQA(dspy.Signature):
    """
    詳細的問答簽名
    提供更多的上下文和約束
    """
    # 文檔字符串會被用作任務描述
    question = dspy.InputField(desc="用戶提出的問題")
    answer = dspy.OutputField(desc="準確、詳細的答案，不少於50字")


class SentimentWithReasoning(dspy.Signature):
    """分析文本的情感傾向，並提供推理過程"""

    text = dspy.InputField(desc="要分析的文本內容")
    sentiment = dspy.OutputField(desc="情感分類：正面、負面或中性")
    reasoning = dspy.OutputField(desc="分析的推理過程")
    confidence_score = dspy.OutputField(desc="置信度分數（0-100）")


class MultilingualTranslation(dspy.Signature):
    """專業的多語言翻譯服務"""

    source_text = dspy.InputField(desc="源語言文本")
    source_lang = dspy.InputField(desc="源語言代碼（如 zh, en, ja）")
    target_lang = dspy.InputField(desc="目標語言代碼")
    context = dspy.InputField(desc="翻譯的上下文或領域（可選）", default="general")

    translation = dspy.OutputField(desc="翻譯後的文本")
    notes = dspy.OutputField(desc="翻譯注意事項或說明（可選）")


def class_based_signatures():
    """
    演示類形式的簽名定義
    提供更好的可讀性和文檔
    """
    print("\n" + "="*60)
    print("2. 類形式的 Signature 定義")
    print("="*60)

    # 使用 DetailedQA
    qa = dspy.Predict(DetailedQA)
    result = qa(question="解釋一下什麼是注意力機制？")
    print(f"\nDetailedQA 簽名：")
    print(f"Q: 解釋一下什麼是注意力機制？")
    print(f"A: {result.answer}")

    # 使用 SentimentWithReasoning
    analyzer = dspy.Predict(SentimentWithReasoning)
    result = analyzer(text="雖然有些小問題，但總體來說這是一次不錯的體驗。")
    print(f"\nSentimentWithReasoning 簽名：")
    print(f"情感: {result.sentiment}")
    print(f"推理: {result.reasoning}")
    print(f"置信度: {result.confidence_score}")

    # 使用 MultilingualTranslation
    translator = dspy.Predict(MultilingualTranslation)
    result = translator(
        source_text="Hello, world!",
        source_lang="en",
        target_lang="zh",
        context="軟件開發"
    )
    print(f"\nMultilingualTranslation 簽名：")
    print(f"翻譯: {result.translation}")
    print(f"注意事項: {result.notes}")


# ============================================================================
# 3. 複雜數據類型的處理
# ============================================================================

class StructuredDataExtraction(dspy.Signature):
    """從文本中提取結構化信息"""

    text = dspy.InputField(desc="包含實體信息的文本")

    # 複雜類型輸出
    entities = dspy.OutputField(desc="提取的實體列表：list[dict]，每個字典包含 'name', 'type', 'description'")
    relationships = dspy.OutputField(desc="實體間的關係列表")
    summary = dspy.OutputField(desc="一句話總結")


class CodeAnalysis(dspy.Signature):
    """分析代碼片段並提供詳細報告"""

    code = dspy.InputField(desc="要分析的代碼")
    language = dspy.InputField(desc="編程語言")

    purpose = dspy.OutputField(desc="代碼的目的")
    complexity = dspy.OutputField(desc="複雜度評估：簡單、中等、複雜")
    issues = dspy.OutputField(desc="潛在問題列表")
    suggestions = dspy.OutputField(desc="改進建議列表")


class MathProblemSolver(dspy.Signature):
    """解決數學問題並提供步驟"""

    problem = dspy.InputField(desc="數學問題描述")
    difficulty = dspy.InputField(desc="難度級別：簡單、中等、困難", default="中等")

    solution_steps = dspy.OutputField(desc="解題步驟的有序列表")
    final_answer = dspy.OutputField(desc="最終答案")
    alternative_methods = dspy.OutputField(desc="其他可能的解法")


def complex_type_signatures():
    """
    演示複雜數據類型的簽名處理
    """
    print("\n" + "="*60)
    print("3. 複雜數據類型的處理")
    print("="*60)

    # 結構化數據提取
    extractor = dspy.Predict(StructuredDataExtraction)
    result = extractor(
        text="蘋果公司由史蒂夫·喬布斯創立於1976年。微軟公司由比爾·蓋茨和保羅·艾倫創立。"
    )
    print(f"\n結構化數據提取：")
    print(f"實體: {result.entities}")
    print(f"關係: {result.relationships}")
    print(f"摘要: {result.summary}")

    # 代碼分析
    code_analyzer = dspy.Predict(CodeAnalysis)
    result = code_analyzer(
        code="def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)",
        language="Python"
    )
    print(f"\n代碼分析：")
    print(f"目的: {result.purpose}")
    print(f"複雜度: {result.complexity}")
    print(f"問題: {result.issues}")
    print(f"建議: {result.suggestions}")


# ============================================================================
# 4. 帶有默認值和可選字段的 Signature
# ============================================================================

class FlexibleSearch(dspy.Signature):
    """靈活的搜索簽名，帶有可選參數"""

    query = dspy.InputField(desc="搜索查詢")
    max_results = dspy.InputField(desc="最大結果數", default=10)
    language = dspy.InputField(desc="語言偏好", default="zh")
    category = dspy.InputField(desc="搜索類別", default="general")

    results = dspy.OutputField(desc="搜索結果摘要")
    result_count = dspy.OutputField(desc="實際返回的結果數")


class ContentGenerator(dspy.Signature):
    """內容生成器，帶有多個可選配置"""

    topic = dspy.InputField(desc="主題")
    tone = dspy.InputField(desc="語氣：正式、非正式、友好、專業", default="友好")
    length = dspy.InputField(desc="期望長度：短、中、長", default="中")
    audience = dspy.InputField(desc="目標受眾", default="一般讀者")

    content = dspy.OutputField(desc="生成的內容")
    word_count = dspy.OutputField(desc="字數統計")


def optional_fields_signatures():
    """
    演示帶有默認值和可選字段的簽名
    """
    print("\n" + "="*60)
    print("4. 帶有默認值和可選字段的 Signature")
    print("="*60)

    # 使用默認值
    search = dspy.Predict(FlexibleSearch)
    result = search(query="人工智能")
    print(f"\n使用默認值的搜索：")
    print(f"結果: {result.results[:100]}...")
    print(f"數量: {result.result_count}")

    # 覆蓋默認值
    result = search(
        query="machine learning",
        max_results=5,
        language="en",
        category="academic"
    )
    print(f"\n自定義參數的搜索：")
    print(f"結果: {result.results[:100]}...")

    # 內容生成
    generator = dspy.Predict(ContentGenerator)
    result = generator(
        topic="深度學習",
        tone="專業",
        length="長"
    )
    print(f"\n內容生成：")
    print(f"內容: {result.content[:150]}...")
    print(f"字數: {result.word_count}")


# ============================================================================
# 5. Signature 的繼承和組合
# ============================================================================

class BaseSignature(dspy.Signature):
    """基礎簽名類"""
    input_text = dspy.InputField(desc="輸入文本")


class AnalysisSignature(BaseSignature):
    """繼承基礎簽名，添加分析功能"""
    analysis = dspy.OutputField(desc="文本分析結果")
    key_points = dspy.OutputField(desc="關鍵要點")


class DetailedAnalysisSignature(AnalysisSignature):
    """進一步擴展分析功能"""
    sentiment = dspy.OutputField(desc="情感分析")
    topics = dspy.OutputField(desc="主題標籤")
    entities = dspy.OutputField(desc="命名實體")


def signature_inheritance():
    """
    演示簽名的繼承和擴展
    """
    print("\n" + "="*60)
    print("5. Signature 的繼承和組合")
    print("="*60)

    # 使用基礎簽名
    analyzer = dspy.Predict(AnalysisSignature)
    result = analyzer(input_text="這是一篇關於人工智能發展的文章")
    print(f"\n基礎分析：")
    print(f"分析: {result.analysis}")
    print(f"要點: {result.key_points}")

    # 使用詳細分析簽名
    detailed_analyzer = dspy.Predict(DetailedAnalysisSignature)
    result = detailed_analyzer(input_text="這是一篇關於人工智能發展的文章")
    print(f"\n詳細分析：")
    print(f"分析: {result.analysis}")
    print(f"情感: {result.sentiment}")
    print(f"主題: {result.topics}")
    print(f"實體: {result.entities}")


# ============================================================================
# 6. Signature 最佳實踐
# ============================================================================

class WellDesignedSignature(dspy.Signature):
    """
    設計良好的簽名示例

    最佳實踐：
    1. 提供清晰的文檔字符串
    2. 為每個字段添加描述
    3. 使用有意義的字段名稱
    4. 指定合適的數據類型
    5. 提供默認值（如果適用）
    """

    # 輸入字段 - 清晰命名和描述
    user_query = dspy.InputField(
        desc="用戶的原始查詢，應該是一個清晰的問題或請求"
    )
    context_info = dspy.InputField(
        desc="相關的背景信息或上下文",
        default=""
    )
    response_style = dspy.InputField(
        desc="期望的回答風格：簡潔、詳細、技術性",
        default="詳細"
    )

    # 輸出字段 - 明確的期望
    main_response = dspy.OutputField(
        desc="對查詢的主要回答，應該直接回答問題"
    )
    additional_info = dspy.OutputField(
        desc="補充信息或相關建議"
    )
    confidence_level = dspy.OutputField(
        desc="回答的置信度：高、中、低"
    )


# 對比：設計不良的簽名
class PoorlyDesignedSignature(dspy.Signature):
    # 問題：
    # 1. 沒有文檔字符串
    # 2. 字段名稱不清晰
    # 3. 沒有描述
    # 4. 缺少類型信息

    x = dspy.InputField()
    y = dspy.InputField()
    z = dspy.OutputField()


def best_practices_comparison():
    """
    對比設計良好和設計不良的簽名
    """
    print("\n" + "="*60)
    print("6. Signature 最佳實踐")
    print("="*60)

    # 使用設計良好的簽名
    good_predictor = dspy.Predict(WellDesignedSignature)
    result = good_predictor(
        user_query="如何開始學習機器學習？",
        context_info="我有 Python 基礎",
        response_style="詳細"
    )
    print(f"\n設計良好的簽名結果：")
    print(f"回答: {result.main_response[:150]}...")
    print(f"補充: {result.additional_info[:100]}...")
    print(f"置信度: {result.confidence_level}")

    print("\n" + "-"*60)
    print("最佳實踐總結：")
    print("-"*60)
    print("✓ 1. 使用清晰、描述性的字段名稱")
    print("✓ 2. 為每個字段提供詳細的描述")
    print("✓ 3. 添加類的文檔字符串說明任務")
    print("✓ 4. 使用類型標註（bool, int, list[str]等）")
    print("✓ 5. 為可選字段提供合理的默認值")
    print("✓ 6. 輸入和輸出的語義應該清晰明確")
    print("✓ 7. 避免過於簡短或模糊的命名")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """
    主函數：運行所有 Signature 定義範例
    """
    print("DSPy Signature 定義詳解")
    print("=" * 60)

    try:
        # 配置語言模型
        lm = dspy.LM('openai/gpt-4o-mini')
        dspy.configure(lm=lm)
        print(f"✓ 已配置語言模型: {lm.model}")

        # 運行各種範例
        short_string_signatures()
        class_based_signatures()
        complex_type_signatures()
        optional_fields_signatures()
        signature_inheritance()
        best_practices_comparison()

        print("\n" + "="*60)
        print("所有 Signature 範例運行完成！")
        print("="*60)

    except Exception as e:
        print(f"\n錯誤：{e}")
        print("\n提示：請確保設置了 OPENAI_API_KEY 環境變數")


if __name__ == "__main__":
    main()


"""
Signature 設計指南
==================

1. 何時使用簡短字符串形式：
   - 快速原型開發
   - 簡單的單輸入單輸出任務
   - 臨時測試和實驗

2. 何時使用類形式：
   - 生產環境代碼
   - 需要詳細文檔的場景
   - 複雜的多字段任務
   - 需要類型檢查和IDE支持

3. 字段命名原則：
   - 使用清晰、描述性的名稱
   - 避免縮寫和模糊詞彙
   - 反映字段的語義角色
   - 遵循 Python 命名規範

4. 類型標註建議：
   - bool: 二分類任務
   - int/float: 數值輸出
   - str: 文本（默認）
   - list[str]: 列表輸出
   - dict: 結構化數據（需要額外解析）

5. 描述的重要性：
   - 描述會影響模型的行為
   - 清晰的描述能提高輸出質量
   - 可以在描述中添加約束和要求

下一步學習：
- 03_Module構建.py - 學習如何構建自定義模塊
- 04_優化器使用.py - 使用優化器改進簽名性能
"""
