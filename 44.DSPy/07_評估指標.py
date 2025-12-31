"""
DSPy 評估指標教學

本模組深入講解如何設計和使用評估指標來衡量 DSPy 模組的性能：
1. 評估指標的重要性
2. 基礎評估指標（精確匹配、包含等）
3. 語義相似度評估
4. 基於 LLM 的評估
5. 多維度評估
6. 自定義評估指標
7. 評估框架使用

作者：DSPy 教學團隊
日期：2025-01
"""

import dspy
from typing import List, Dict, Optional, Callable
from dspy.evaluate import Evaluate
import re
import json


# ==================== 評估基礎概念 ====================

def explain_evaluation_concept():
    """
    解釋評估的核心概念

    為什麼需要評估？
    - 衡量模組性能
    - 指導優化過程
    - 比較不同方法
    - 持續監控質量
    """
    print("\n" + "="*60)
    print("評估指標核心概念")
    print("="*60)

    print("""
    評估的重要性：
    1. 量化性能：將主觀判斷轉為客觀數字
    2. 優化指導：告訴優化器什麼是"好"
    3. 進度追蹤：監控改進效果
    4. 模型對比：比較不同方法

    評估指標的類型：
    - 精確匹配（Exact Match）：完全相同
    - 包含匹配（Contains）：包含關鍵內容
    - F1 分數：精確率和召回率的調和平均
    - 語義相似度：意義相近
    - 基於 LLM 的評估：使用 LLM 判斷質量

    好的評估指標特徵：
    - 可靠性：結果一致、可重複
    - 有效性：真正衡量目標質量
    - 區分度：能區分好壞輸出
    - 效率：計算成本合理

    評估流程：
    1. 準備評估數據集（包含輸入和期望輸出）
    2. 定義評估指標
    3. 運行模組獲取預測
    4. 計算指標分數
    5. 分析結果並改進
    """)


# ==================== 基礎評估指標 ====================

def exact_match(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    """
    精確匹配評估指標

    檢查預測答案是否與期望答案完全相同

    Args:
        example: 包含期望輸出的範例
        prediction: 模組的預測結果
        trace: 執行軌跡（可選）

    Returns:
        1.0 如果完全匹配，否則 0.0
    """
    # 標準化處理
    expected = str(example.answer).lower().strip()
    predicted = str(prediction.answer).lower().strip()

    return 1.0 if expected == predicted else 0.0


def contains_match(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    """
    包含匹配評估指標

    檢查預測答案是否包含期望答案的關鍵內容

    Args:
        example: 包含期望輸出的範例
        prediction: 模組的預測結果
        trace: 執行軌跡（可選）

    Returns:
        1.0 如果包含，否則 0.0
    """
    expected = str(example.answer).lower()
    predicted = str(prediction.answer).lower()

    # 雙向檢查
    if expected in predicted or predicted in expected:
        return 1.0

    # 檢查關鍵詞重疊
    expected_words = set(expected.split())
    predicted_words = set(predicted.split())
    overlap = len(expected_words & predicted_words)

    # 如果有 50% 以上的詞重疊，認為匹配
    if overlap > 0:
        ratio = overlap / len(expected_words)
        return 1.0 if ratio >= 0.5 else 0.0

    return 0.0


def f1_score_metric(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    """
    F1 分數評估指標

    計算精確率和召回率的調和平均

    Args:
        example: 包含期望輸出的範例
        prediction: 模組的預測結果
        trace: 執行軌跡（可選）

    Returns:
        F1 分數（0-1）
    """
    expected = str(example.answer).lower().split()
    predicted = str(prediction.answer).lower().split()

    # 計算詞級別的精確率和召回率
    expected_set = set(expected)
    predicted_set = set(predicted)

    if len(predicted_set) == 0:
        return 0.0

    # True Positives
    tp = len(expected_set & predicted_set)

    # Precision
    precision = tp / len(predicted_set) if len(predicted_set) > 0 else 0

    # Recall
    recall = tp / len(expected_set) if len(expected_set) > 0 else 0

    # F1
    if precision + recall == 0:
        return 0.0

    f1 = 2 * (precision * recall) / (precision + recall)
    return f1


def partial_credit_metric(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    """
    部分分數評估指標

    根據答案的多個方面給予部分分數

    Args:
        example: 包含期望輸出的範例
        prediction: 模組的預測結果
        trace: 執行軌跡（可選）

    Returns:
        部分分數（0-1）
    """
    score = 0.0
    max_score = 3.0

    expected = str(example.answer).lower()
    predicted = str(prediction.answer).lower()

    # 檢查 1：是否包含關鍵詞
    expected_words = set(expected.split())
    predicted_words = set(predicted.split())
    overlap_ratio = len(expected_words & predicted_words) / len(expected_words)
    if overlap_ratio >= 0.5:
        score += 1.0

    # 檢查 2：長度是否合理
    len_ratio = len(predicted) / max(len(expected), 1)
    if 0.5 <= len_ratio <= 2.0:  # 長度在 0.5-2 倍之間
        score += 1.0

    # 檢查 3：是否包含數字/實體（如果有）
    expected_numbers = re.findall(r'\d+', expected)
    predicted_numbers = re.findall(r'\d+', predicted)
    if expected_numbers:
        if any(num in predicted_numbers for num in expected_numbers):
            score += 1.0
    else:
        score += 1.0  # 如果沒有數字要求，給予滿分

    return score / max_score


# ==================== 語義相似度評估 ====================

def semantic_similarity_metric(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    """
    語義相似度評估指標

    使用 LLM 評估兩個答案的語義相似度

    Args:
        example: 包含期望輸出的範例
        prediction: 模組的預測結果
        trace: 執行軌跡（可選）

    Returns:
        相似度分數（0-1）
    """
    class JudgeSimilarity(dspy.Signature):
        """評估兩個答案的語義相似度"""
        expected_answer = dspy.InputField(desc="期望的答案")
        predicted_answer = dspy.InputField(desc="預測的答案")
        similarity_score = dspy.OutputField(
            desc="語義相似度分數（0-100），0 表示完全不同，100 表示意思完全相同"
        )
        explanation = dspy.OutputField(desc="評分理由")

    judge = dspy.Predict(JudgeSimilarity)

    try:
        result = judge(
            expected_answer=str(example.answer),
            predicted_answer=str(prediction.answer)
        )

        # 提取分數
        score_text = result.similarity_score
        # 嘗試從文本中提取數字
        numbers = re.findall(r'\d+', score_text)
        if numbers:
            score = float(numbers[0])
            return min(100, max(0, score)) / 100.0  # 轉換為 0-1 範圍
        return 0.5  # 默認分數
    except Exception as e:
        print(f"語義評估錯誤：{e}")
        return 0.0


# ==================== 基於 LLM 的綜合評估 ====================

def llm_comprehensive_evaluation(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    """
    基於 LLM 的綜合評估

    使用 LLM 從多個維度評估答案質量

    Args:
        example: 包含期望輸出的範例
        prediction: 模組的預測結果
        trace: 執行軌跡（可選）

    Returns:
        綜合分數（0-1）
    """
    class ComprehensiveJudge(dspy.Signature):
        """綜合評估答案質量"""
        question = dspy.InputField(desc="原始問題")
        expected_answer = dspy.InputField(desc="參考答案")
        predicted_answer = dspy.InputField(desc="預測答案")

        is_correct = dspy.OutputField(desc="是否正確（yes/no）")
        is_complete = dspy.OutputField(desc="是否完整（yes/no）")
        is_relevant = dspy.OutputField(desc="是否相關（yes/no）")
        is_coherent = dspy.OutputField(desc="是否連貫（yes/no）")
        overall_score = dspy.OutputField(desc="總體分數（0-100）")

    judge = dspy.Predict(ComprehensiveJudge)

    try:
        result = judge(
            question=str(example.question) if hasattr(example, 'question') else "未提供問題",
            expected_answer=str(example.answer),
            predicted_answer=str(prediction.answer)
        )

        # 計算分數
        score = 0.0

        if "yes" in result.is_correct.lower():
            score += 0.3
        if "yes" in result.is_complete.lower():
            score += 0.25
        if "yes" in result.is_relevant.lower():
            score += 0.25
        if "yes" in result.is_coherent.lower():
            score += 0.2

        return score
    except Exception as e:
        print(f"LLM 評估錯誤：{e}")
        return 0.0


def llm_qa_evaluation(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    """
    專門針對問答任務的 LLM 評估

    Args:
        example: 包含期望輸出的範例
        prediction: 模組的預測結果
        trace: 執行軌跡（可選）

    Returns:
        評估分數（0-1）
    """
    class QAJudge(dspy.Signature):
        """評估問答質量"""
        question = dspy.InputField()
        reference_answer = dspy.InputField()
        predicted_answer = dspy.InputField()

        factually_correct = dspy.OutputField(desc="事實是否正確（yes/no）")
        answers_question = dspy.OutputField(desc="是否回答了問題（yes/no）")
        quality_score = dspy.OutputField(desc="答案質量（1-5）")

    judge = dspy.Predict(QAJudge)

    try:
        result = judge(
            question=str(example.question),
            reference_answer=str(example.answer),
            predicted_answer=str(prediction.answer)
        )

        score = 0.0

        # 事實正確性（50%）
        if "yes" in result.factually_correct.lower():
            score += 0.5

        # 是否回答問題（30%）
        if "yes" in result.answers_question.lower():
            score += 0.3

        # 質量分數（20%）
        try:
            quality = float(re.findall(r'\d+', result.quality_score)[0])
            score += (quality / 5.0) * 0.2
        except:
            pass

        return score
    except Exception as e:
        print(f"QA 評估錯誤：{e}")
        return 0.0


# ==================== 任務特定評估指標 ====================

def sentiment_accuracy(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    """
    情感分類準確度

    Args:
        example: 包含期望情感的範例
        prediction: 預測的情感
        trace: 執行軌跡（可選）

    Returns:
        1.0 如果正確，否則 0.0
    """
    expected = str(example.sentiment).lower().strip()
    predicted = str(prediction.sentiment).lower().strip()

    return 1.0 if expected == predicted else 0.0


def classification_accuracy(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    """
    分類準確度

    Args:
        example: 包含期望類別的範例
        prediction: 預測的類別
        trace: 執行軌跡（可選）

    Returns:
        1.0 如果正確，否則 0.0
    """
    expected = str(example.category).lower().strip()
    predicted = str(prediction.category).lower().strip()

    return 1.0 if expected == predicted else 0.0


def has_citation_metric(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    """
    檢查是否有引用來源

    Args:
        example: 範例
        prediction: 預測結果
        trace: 執行軌跡（可選）

    Returns:
        1.0 如果有引用，否則 0.0
    """
    # 檢查是否有引用標記（如 [1], [2] 等）
    citation_pattern = r'\[\d+\]'

    if hasattr(prediction, 'citations'):
        citations = str(prediction.citations)
        if re.search(citation_pattern, citations):
            return 1.0

    # 也檢查答案中是否有引用
    if hasattr(prediction, 'answer'):
        answer = str(prediction.answer)
        if re.search(citation_pattern, answer):
            return 1.0

    return 0.0


# ==================== 組合評估指標 ====================

def create_weighted_metric(metrics: List[tuple]) -> Callable:
    """
    創建加權組合評估指標

    Args:
        metrics: [(metric_function, weight), ...] 列表

    Returns:
        組合評估函數
    """
    def weighted_metric(example, prediction, trace=None):
        total_score = 0.0
        total_weight = sum(weight for _, weight in metrics)

        for metric_func, weight in metrics:
            try:
                score = metric_func(example, prediction, trace)
                total_score += score * weight
            except Exception as e:
                print(f"指標 {metric_func.__name__} 錯誤：{e}")
                continue

        return total_score / total_weight if total_weight > 0 else 0.0

    return weighted_metric


def create_threshold_metric(base_metric: Callable, threshold: float = 0.5) -> Callable:
    """
    創建閾值評估指標

    將連續分數轉換為二元分數

    Args:
        base_metric: 基礎評估指標
        threshold: 閾值

    Returns:
        二元評估函數
    """
    def threshold_metric(example, prediction, trace=None):
        score = base_metric(example, prediction, trace)
        return 1.0 if score >= threshold else 0.0

    return threshold_metric


# ==================== 評估框架使用 ====================

def run_comprehensive_evaluation(module, dataset, metrics_dict):
    """
    運行綜合評估

    Args:
        module: 要評估的 DSPy 模組
        dataset: 評估數據集
        metrics_dict: 指標字典 {name: metric_function}

    Returns:
        評估結果字典
    """
    print("\n" + "="*60)
    print("運行綜合評估")
    print("="*60)

    results = {}

    for metric_name, metric_func in metrics_dict.items():
        print(f"\n評估指標：{metric_name}")
        print("-" * 60)

        # 創建評估器
        evaluator = Evaluate(
            devset=dataset,
            metric=metric_func,
            num_threads=1,
            display_progress=True,
            display_table=0  # 不顯示詳細表格
        )

        # 運行評估
        try:
            score = evaluator(module)
            results[metric_name] = score
            print(f"✓ {metric_name}: {score:.2%}")
        except Exception as e:
            print(f"✗ {metric_name}: 評估失敗 - {e}")
            results[metric_name] = 0.0

    # 顯示總結
    print("\n" + "="*60)
    print("評估總結")
    print("="*60)
    for metric_name, score in results.items():
        print(f"{metric_name:30s}: {score:.2%}")

    return results


# ==================== 自定義評估指標範例 ====================

class CustomMetricBuilder:
    """自定義評估指標構建器"""

    @staticmethod
    def keyword_presence_metric(required_keywords: List[str]) -> Callable:
        """
        關鍵詞存在評估指標

        Args:
            required_keywords: 必須包含的關鍵詞列表

        Returns:
            評估函數
        """
        def metric(example, prediction, trace=None):
            answer = str(prediction.answer).lower()
            present_count = sum(
                1 for keyword in required_keywords
                if keyword.lower() in answer
            )
            return present_count / len(required_keywords)

        return metric

    @staticmethod
    def length_constraint_metric(min_length: int, max_length: int) -> Callable:
        """
        長度約束評估指標

        Args:
            min_length: 最小長度
            max_length: 最大長度

        Returns:
            評估函數
        """
        def metric(example, prediction, trace=None):
            answer = str(prediction.answer)
            length = len(answer.split())

            if min_length <= length <= max_length:
                return 1.0
            elif length < min_length:
                return length / min_length
            else:  # length > max_length
                return max_length / length

        return metric

    @staticmethod
    def format_compliance_metric(pattern: str) -> Callable:
        """
        格式合規性評估指標

        Args:
            pattern: 正則表達式模式

        Returns:
            評估函數
        """
        def metric(example, prediction, trace=None):
            answer = str(prediction.answer)
            return 1.0 if re.search(pattern, answer) else 0.0

        return metric


# ==================== 主程序 ====================

def main():
    """主函數：演示所有評估指標"""

    print("="*60)
    print("DSPy 評估指標教學")
    print("="*60)

    # 1. 概念說明
    explain_evaluation_concept()

    # 2. 配置 DSPy
    print("\n" + "="*60)
    print("配置 DSPy")
    print("="*60)
    try:
        lm = dspy.OpenAI(model="gpt-4", max_tokens=400)
        dspy.settings.configure(lm=lm)
        print("✓ 配置完成")
    except Exception as e:
        print(f"配置失敗：{e}")
        return

    # 3. 創建測試數據
    print("\n" + "="*60)
    print("創建測試數據")
    print("="*60)

    test_dataset = [
        dspy.Example(
            question="什麼是機器學習？",
            answer="機器學習是人工智能的一個分支，使計算機能夠從數據中學習。"
        ).with_inputs("question"),

        dspy.Example(
            question="深度學習的主要應用是什麼？",
            answer="深度學習主要應用於圖像識別、自然語言處理和語音識別。"
        ).with_inputs("question"),

        dspy.Example(
            question="什麼是過擬合？",
            answer="過擬合是指模型在訓練數據上表現好，但在新數據上表現差。"
        ).with_inputs("question"),
    ]

    print(f"測試數據集大小：{len(test_dataset)}")

    # 4. 創建簡單的 QA 模組
    print("\n" + "="*60)
    print("創建 QA 模組")
    print("="*60)

    class SimpleQA(dspy.Module):
        def __init__(self):
            super().__init__()
            class QA(dspy.Signature):
                question = dspy.InputField()
                answer = dspy.OutputField()
            self.generate = dspy.Predict(QA)

        def forward(self, question):
            return self.generate(question=question)

    qa_module = SimpleQA()
    print("✓ QA 模組創建完成")

    # 5. 測試各種評估指標
    print("\n" + "="*60)
    print("測試評估指標")
    print("="*60)

    # 測試單個範例
    test_example = test_dataset[0]
    test_prediction = qa_module(question=test_example.question)

    print(f"\n問題：{test_example.question}")
    print(f"期望答案：{test_example.answer}")
    print(f"預測答案：{test_prediction.answer}")

    # 測試各種指標
    print("\n指標測試結果：")
    print(f"精確匹配：{exact_match(test_example, test_prediction):.2f}")
    print(f"包含匹配：{contains_match(test_example, test_prediction):.2f}")
    print(f"F1 分數：{f1_score_metric(test_example, test_prediction):.2f}")
    print(f"部分分數：{partial_credit_metric(test_example, test_prediction):.2f}")

    # 6. 組合指標演示
    print("\n" + "="*60)
    print("組合評估指標演示")
    print("="*60)

    weighted = create_weighted_metric([
        (exact_match, 0.3),
        (f1_score_metric, 0.4),
        (partial_credit_metric, 0.3)
    ])

    score = weighted(test_example, test_prediction)
    print(f"加權組合分數：{score:.2f}")

    # 7. 自定義指標演示
    print("\n" + "="*60)
    print("自定義評估指標演示")
    print("="*60)

    builder = CustomMetricBuilder()

    # 關鍵詞指標
    keyword_metric = builder.keyword_presence_metric(["機器學習", "數據"])
    print(f"關鍵詞存在：{keyword_metric(test_example, test_prediction):.2f}")

    # 長度指標
    length_metric = builder.length_constraint_metric(10, 50)
    print(f"長度合規：{length_metric(test_example, test_prediction):.2f}")

    # 8. 綜合評估（可選，需要較長時間）
    print("\n" + "="*60)
    print("綜合評估（可選）")
    print("="*60)
    print("綜合評估會調用 LLM 多次，可能需要較長時間")
    print("在實際使用中，建議使用較小的測試集")

    # 總結
    print("\n" + "="*60)
    print("教學完成！")
    print("="*60)
    print("""
    你已經學會了：
    1. ✓ 評估的核心概念
    2. ✓ 基礎評估指標（精確匹配、F1 等）
    3. ✓ 語義相似度評估
    4. ✓ 基於 LLM 的評估
    5. ✓ 任務特定評估指標
    6. ✓ 組合評估指標
    7. ✓ 自定義評估指標

    設計評估指標的要點：
    - 明確評估目標
    - 選擇合適的指標類型
    - 考慮計算成本
    - 平衡多個維度
    - 持續迭代改進

    常見評估指標選擇：
    - 分類任務：準確率、F1 分數
    - 生成任務：BLEU、ROUGE、語義相似度
    - 問答任務：精確匹配、F1、基於 LLM 評估
    - RAG 任務：相關性、忠實度、引用質量

    下一步：
    - 學習多模型支援（08_多模型支援.py）
    - 學習緩存策略（09_緩存策略.py）
    - 將評估應用到實際項目
    """)


if __name__ == "__main__":
    main()
