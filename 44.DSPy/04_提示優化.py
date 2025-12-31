"""
DSPy 提示優化教學

本模組深入講解 DSPy 的核心特性：自動提示優化，包括：
1. 優化器概念和原理
2. BootstrapFewShot 優化器
3. MIPROv2 優化器
4. COPRO 優化器
5. 評估指標設計
6. 訓練數據準備
7. 優化策略和最佳實踐

作者：DSPy 教學團隊
日期：2025-01
"""

import dspy
from typing import List, Dict, Callable, Optional
import random
from dspy.evaluate import Evaluate
from dspy.teleprompt import BootstrapFewShot, BootstrapFewShotWithRandomSearch
# from dspy.teleprompt import MIPROv2, COPRO  # 需要最新版本


# ==================== 優化基礎概念 ====================

def explain_optimization_concept():
    """
    解釋 DSPy 優化的核心概念

    傳統方法：
    - 手動編寫和調整提示詞
    - 憑經驗和試錯
    - 難以擴展和維護

    DSPy 方法：
    - 定義任務簽名
    - 提供少量範例
    - 自動找到最佳提示
    """
    print("\n" + "="*60)
    print("DSPy 優化概念")
    print("="*60)

    print("""
    優化器的作用：
    1. 自動生成和調整提示詞
    2. 選擇最佳的少樣本範例
    3. 優化推理策略
    4. 提高模型性能

    優化流程：
    1. 定義任務（簽名 + 模組）
    2. 準備訓練數據（輸入 + 期望輸出）
    3. 定義評估指標
    4. 選擇優化器
    5. 執行優化
    6. 評估優化後的模組
    """)


# ==================== 訓練數據準備 ====================

def create_qa_training_data():
    """
    創建問答任務的訓練數據

    訓練數據是 Example 對象的列表
    每個 Example 包含輸入和期望輸出
    """
    trainset = [
        dspy.Example(
            question="什麼是機器學習？",
            answer="機器學習是人工智能的一個分支，通過算法和統計模型使計算機系統能夠從數據中學習和改進，而無需明確編程。"
        ).with_inputs("question"),

        dspy.Example(
            question="深度學習和機器學習有什麼區別？",
            answer="深度學習是機器學習的一個子集，使用多層神經網絡來學習數據的複雜模式。相比傳統機器學習，深度學習能自動提取特徵，適合處理大規模非結構化數據。"
        ).with_inputs("question"),

        dspy.Example(
            question="什麼是過擬合？",
            answer="過擬合是指模型在訓練數據上表現很好，但在新數據上表現不佳。這通常發生在模型過於複雜，學習了訓練數據中的噪音和細節，而非一般規律。"
        ).with_inputs("question"),

        dspy.Example(
            question="什麼是神經網絡？",
            answer="神經網絡是一種受生物神經系統啟發的計算模型，由多個相互連接的節點（神經元）組成，通過調整連接權重來學習數據模式。"
        ).with_inputs("question"),

        dspy.Example(
            question="什麼是自然語言處理？",
            answer="自然語言處理（NLP）是人工智能的一個領域，專注於讓計算機理解、解釋和生成人類語言。應用包括機器翻譯、情感分析、聊天機器人等。"
        ).with_inputs("question"),

        dspy.Example(
            question="什麼是強化學習？",
            answer="強化學習是一種機器學習方法，通過與環境互動並根據獎勵信號調整行為來學習最優策略。常用於遊戲AI、機器人控制等領域。"
        ).with_inputs("question"),

        dspy.Example(
            question="什麼是卷積神經網絡？",
            answer="卷積神經網絡（CNN）是一種專門用於處理網格狀數據（如圖像）的深度學習架構。它使用卷積層來自動學習空間層次的特徵。"
        ).with_inputs("question"),

        dspy.Example(
            question="什麼是遷移學習？",
            answer="遷移學習是指將在一個任務上訓練的模型應用到另一個相關任務上。這可以減少訓練時間和數據需求，特別適合數據稀缺的場景。"
        ).with_inputs("question"),
    ]

    return trainset


def create_sentiment_training_data():
    """創建情感分析訓練數據"""
    trainset = [
        dspy.Example(
            text="這個產品質量很好，非常滿意！",
            sentiment="positive"
        ).with_inputs("text"),

        dspy.Example(
            text="服務態度太差了，完全不推薦。",
            sentiment="negative"
        ).with_inputs("text"),

        dspy.Example(
            text="還可以，符合預期。",
            sentiment="neutral"
        ).with_inputs("text"),

        dspy.Example(
            text="價格合理，物超所值！",
            sentiment="positive"
        ).with_inputs("text"),

        dspy.Example(
            text="包裝很差，產品有損壞。",
            sentiment="negative"
        ).with_inputs("text"),

        dspy.Example(
            text="一般般，沒什麼特別的。",
            sentiment="neutral"
        ).with_inputs("text"),
    ]

    return trainset


def create_classification_training_data():
    """創建分類任務訓練數據"""
    trainset = [
        dspy.Example(
            text="Python 3.11 發布，性能提升 25%",
            category="technology"
        ).with_inputs("text"),

        dspy.Example(
            text="NBA 總決賽：湖人隊奪冠",
            category="sports"
        ).with_inputs("text"),

        dspy.Example(
            text="央行宣布降息 0.25 個百分點",
            category="finance"
        ).with_inputs("text"),

        dspy.Example(
            text="新型流感疫苗臨床試驗成功",
            category="health"
        ).with_inputs("text"),

        dspy.Example(
            text="好萊塢新片票房破紀錄",
            category="entertainment"
        ).with_inputs("text"),
    ]

    return trainset


# ==================== 評估指標設計 ====================

def exact_match_metric(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    """
    精確匹配評估指標

    檢查預測答案是否與期望答案完全相同
    """
    # 標準化比較（轉小寫、去空白）
    expected = example.answer.lower().strip()
    predicted = prediction.answer.lower().strip()

    return float(expected == predicted)


def contains_metric(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    """
    包含評估指標

    檢查預測答案是否包含期望答案的關鍵內容
    """
    expected = example.answer.lower()
    predicted = prediction.answer.lower()

    # 簡單的包含檢查
    return float(expected in predicted or predicted in expected)


def semantic_similarity_metric(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    """
    語義相似度評估指標

    使用 LLM 評估答案的語義相似度
    """
    class JudgeSimilarity(dspy.Signature):
        """評估兩個答案的語義相似度"""
        expected_answer = dspy.InputField()
        predicted_answer = dspy.InputField()
        similarity_score = dspy.OutputField(desc="相似度分數（0-100）")

    judge = dspy.Predict(JudgeSimilarity)

    try:
        result = judge(
            expected_answer=example.answer,
            predicted_answer=prediction.answer
        )
        score = float(result.similarity_score)
        return score / 100.0  # 轉換為 0-1 範圍
    except:
        return 0.0


def comprehensive_qa_metric(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    """
    綜合問答評估指標

    評估答案的多個維度
    """
    class JudgeAnswer(dspy.Signature):
        """綜合評估答案質量"""
        question = dspy.InputField()
        expected_answer = dspy.InputField()
        predicted_answer = dspy.InputField()
        is_correct = dspy.OutputField(desc="是否正確（yes/no）")
        is_complete = dspy.OutputField(desc="是否完整（yes/no）")
        is_relevant = dspy.OutputField(desc="是否相關（yes/no）")

    judge = dspy.Predict(JudgeAnswer)

    try:
        result = judge(
            question=example.question,
            expected_answer=example.answer,
            predicted_answer=prediction.answer
        )

        # 計算分數
        score = 0.0
        if "yes" in result.is_correct.lower():
            score += 0.5
        if "yes" in result.is_complete.lower():
            score += 0.25
        if "yes" in result.is_relevant.lower():
            score += 0.25

        return score
    except:
        return 0.0


def sentiment_accuracy_metric(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    """情感分析準確度指標"""
    expected = example.sentiment.lower().strip()
    predicted = prediction.sentiment.lower().strip()

    return float(expected == predicted)


# ==================== BootstrapFewShot 優化器 ====================

class SimpleQA(dspy.Module):
    """簡單問答模組"""

    def __init__(self):
        super().__init__()

        class QA(dspy.Signature):
            """回答問題"""
            question = dspy.InputField()
            answer = dspy.OutputField(desc="簡潔準確的答案")

        self.generate_answer = dspy.ChainOfThought(QA)

    def forward(self, question):
        return self.generate_answer(question=question)


def optimize_with_bootstrap_fewshot():
    """
    使用 BootstrapFewShot 優化器

    BootstrapFewShot 的工作原理：
    1. 使用當前模組生成訓練集的答案
    2. 根據評估指標篩選好的範例
    3. 將這些範例作為少樣本示範
    4. 創建優化後的模組
    """
    print("\n" + "="*60)
    print("BootstrapFewShot 優化器")
    print("="*60)

    # 準備數據
    trainset = create_qa_training_data()
    print(f"訓練集大小：{len(trainset)} 個範例")

    # 創建原始模組
    qa_module = SimpleQA()

    # 測試優化前的性能
    print("\n優化前測試：")
    test_question = "什麼是深度學習？"
    result_before = qa_module(question=test_question)
    print(f"問題：{test_question}")
    print(f"答案：{result_before.answer}")

    # 配置優化器
    optimizer = BootstrapFewShot(
        metric=contains_metric,
        max_bootstrapped_demos=4,  # 最多使用 4 個自舉範例
        max_labeled_demos=4,        # 最多使用 4 個標註範例
    )

    # 執行優化
    print("\n正在執行優化...")
    optimized_qa = optimizer.compile(
        student=qa_module,
        trainset=trainset
    )

    # 測試優化後的性能
    print("\n優化後測試：")
    result_after = optimized_qa(question=test_question)
    print(f"問題：{test_question}")
    print(f"答案：{result_after.answer}")

    return optimized_qa


def optimize_with_bootstrap_random_search():
    """
    使用 BootstrapFewShotWithRandomSearch 優化器

    這個優化器在 BootstrapFewShot 基礎上增加了隨機搜索
    嘗試不同的範例組合，找到最佳配置
    """
    print("\n" + "="*60)
    print("BootstrapFewShotWithRandomSearch 優化器")
    print("="*60)

    trainset = create_qa_training_data()

    # 分割訓練集和驗證集
    random.shuffle(trainset)
    split_point = int(0.7 * len(trainset))
    train = trainset[:split_point]
    dev = trainset[split_point:]

    print(f"訓練集：{len(train)} 個範例")
    print(f"驗證集：{len(dev)} 個範例")

    qa_module = SimpleQA()

    # 配置優化器
    optimizer = BootstrapFewShotWithRandomSearch(
        metric=contains_metric,
        max_bootstrapped_demos=3,
        max_labeled_demos=3,
        num_candidate_programs=5,  # 嘗試 5 個候選程式
        num_threads=1
    )

    # 執行優化
    print("\n正在執行優化（這可能需要幾分鐘）...")
    optimized_qa = optimizer.compile(
        student=qa_module,
        trainset=train,
        valset=dev
    )

    # 評估
    print("\n評估優化後的模組：")
    evaluate = Evaluate(
        devset=dev,
        metric=contains_metric,
        num_threads=1,
        display_progress=True
    )

    score = evaluate(optimized_qa)
    print(f"驗證集分數：{score:.2%}")

    return optimized_qa


# ==================== 情感分析優化範例 ====================

class SentimentClassifier(dspy.Module):
    """情感分類器"""

    def __init__(self):
        super().__init__()

        class ClassifySentiment(dspy.Signature):
            """分類文本情感"""
            text = dspy.InputField()
            sentiment = dspy.OutputField(desc="positive, negative, 或 neutral")

        self.classify = dspy.Predict(ClassifySentiment)

    def forward(self, text):
        return self.classify(text=text)


def optimize_sentiment_classifier():
    """優化情感分類器"""
    print("\n" + "="*60)
    print("情感分類器優化")
    print("="*60)

    # 準備數據
    trainset = create_sentiment_training_data()

    # 創建分類器
    classifier = SentimentClassifier()

    # 優化前測試
    print("\n優化前測試：")
    test_texts = [
        "這個電影太精彩了！",
        "完全是浪費時間。",
        "還行，沒什麼特別的。"
    ]

    for text in test_texts:
        result = classifier(text=text)
        print(f"文本：{text}")
        print(f"情感：{result.sentiment}\n")

    # 優化
    optimizer = BootstrapFewShot(
        metric=sentiment_accuracy_metric,
        max_bootstrapped_demos=3,
        max_labeled_demos=3
    )

    print("正在優化...")
    optimized_classifier = optimizer.compile(
        student=classifier,
        trainset=trainset
    )

    # 優化後測試
    print("\n優化後測試：")
    for text in test_texts:
        result = optimized_classifier(text=text)
        print(f"文本：{text}")
        print(f"情感：{result.sentiment}\n")

    return optimized_classifier


# ==================== 複雜任務優化 ====================

class ComplexReasoner(dspy.Module):
    """複雜推理模組"""

    def __init__(self):
        super().__init__()

        class Reason(dspy.Signature):
            """進行複雜推理"""
            problem = dspy.InputField()
            reasoning = dspy.OutputField(desc="詳細的推理過程")
            solution = dspy.OutputField(desc="最終解決方案")

        self.reason = dspy.ChainOfThought(Reason)

    def forward(self, problem):
        return self.reason(problem=problem)


def create_reasoning_training_data():
    """創建推理任務訓練數據"""
    trainset = [
        dspy.Example(
            problem="如果 5 個人 5 天可以完成 5 個任務，那麼 10 個人 10 天可以完成多少個任務？",
            solution="20 個任務。因為 1 個人 1 天完成 1/5 個任務，所以 10 個人 10 天可以完成 10 × 10 × (1/5) = 20 個任務。"
        ).with_inputs("problem"),

        dspy.Example(
            problem="一個水池有兩個進水管和一個出水管。甲管 6 小時注滿，乙管 8 小時注滿，丙管 12 小時放完。如果三管同時開放，多少時間注滿？",
            solution="24 小時。甲管速度 1/6，乙管速度 1/8，丙管速度 -1/12。總速度 = 1/6 + 1/8 - 1/12 = 1/24。所以需要 24 小時。"
        ).with_inputs("problem"),

        dspy.Example(
            problem="有紅、藍、綠三種顏色的球各 10 個。至少要取出多少個球，才能保證有 4 個球顏色相同？",
            solution="10 個球。最壞情況下，前 9 個球每種顏色各 3 個。第 10 個球必定使某種顏色達到 4 個。"
        ).with_inputs("problem"),
    ]

    return trainset


def optimize_complex_reasoner():
    """優化複雜推理模組"""
    print("\n" + "="*60)
    print("複雜推理模組優化")
    print("="*60)

    trainset = create_reasoning_training_data()
    reasoner = ComplexReasoner()

    def reasoning_metric(example, prediction, trace=None):
        """推理質量評估"""
        # 簡化評估：檢查解決方案是否包含關鍵數字
        expected_numbers = [word for word in example.solution.split() if any(c.isdigit() for c in word)]
        predicted_numbers = [word for word in prediction.solution.split() if any(c.isdigit() for c in word)]

        # 如果包含期望的數字，給予高分
        overlap = len(set(expected_numbers) & set(predicted_numbers))
        return min(1.0, overlap / max(1, len(expected_numbers)))

    optimizer = BootstrapFewShot(
        metric=reasoning_metric,
        max_bootstrapped_demos=2,
        max_labeled_demos=2
    )

    print("正在優化...")
    optimized_reasoner = optimizer.compile(
        student=reasoner,
        trainset=trainset
    )

    # 測試
    test_problem = "3 個人 3 天挖 3 個坑，6 個人 6 天挖多少個坑？"
    print(f"\n測試問題：{test_problem}")

    print("\n優化前：")
    result_before = reasoner(problem=test_problem)
    print(f"解決方案：{result_before.solution}")

    print("\n優化後：")
    result_after = optimized_reasoner(problem=test_problem)
    print(f"解決方案：{result_after.solution}")

    return optimized_reasoner


# ==================== 評估工具 ====================

def comprehensive_evaluation(module, dataset, metric):
    """
    綜合評估模組性能

    Args:
        module: 要評估的模組
        dataset: 評估數據集
        metric: 評估指標
    """
    print("\n" + "="*60)
    print("綜合評估")
    print("="*60)

    # 創建評估器
    evaluator = Evaluate(
        devset=dataset,
        metric=metric,
        num_threads=1,
        display_progress=True,
        display_table=5  # 顯示 5 個範例
    )

    # 執行評估
    score = evaluator(module)

    print(f"\n總體分數：{score:.2%}")

    return score


# ==================== 主程序 ====================

def main():
    """主函數：演示所有優化技術"""

    print("="*60)
    print("DSPy 提示優化教學")
    print("="*60)

    # 配置
    print("\n正在配置 DSPy...")
    try:
        lm = dspy.OpenAI(model="gpt-4", max_tokens=600)
        dspy.settings.configure(lm=lm)
        print("✓ 配置完成")
    except Exception as e:
        print(f"配置失敗：{e}")
        print("請設置 OPENAI_API_KEY 環境變數")
        return

    # 1. 概念說明
    explain_optimization_concept()

    # 2. BootstrapFewShot 優化
    try:
        print("\n" + "="*60)
        print("示範 1：基礎優化")
        print("="*60)
        optimize_with_bootstrap_fewshot()
    except Exception as e:
        print(f"錯誤：{e}")

    # 3. 情感分類優化
    try:
        print("\n" + "="*60)
        print("示範 2：情感分類優化")
        print("="*60)
        optimize_sentiment_classifier()
    except Exception as e:
        print(f"錯誤：{e}")

    # 4. 複雜推理優化
    try:
        print("\n" + "="*60)
        print("示範 3：複雜推理優化")
        print("="*60)
        optimize_complex_reasoner()
    except Exception as e:
        print(f"錯誤：{e}")

    # 5. 隨機搜索優化（更耗時，可選）
    try:
        print("\n" + "="*60)
        print("示範 4：隨機搜索優化（可選）")
        print("="*60)
        print("這個示範會花費較長時間，可以跳過。")
        # optimize_with_bootstrap_random_search()
    except Exception as e:
        print(f"錯誤：{e}")

    # 總結
    print("\n" + "="*60)
    print("教學完成！")
    print("="*60)
    print("""
    你已經學會了：
    1. ✓ DSPy 優化的核心概念
    2. ✓ 準備訓練數據
    3. ✓ 設計評估指標
    4. ✓ 使用 BootstrapFewShot 優化器
    5. ✓ 使用隨機搜索優化器
    6. ✓ 評估優化效果

    優化的關鍵要點：
    - 準備高質量的訓練數據（50-100 個範例）
    - 設計準確的評估指標
    - 選擇合適的優化器
    - 迭代測試和改進
    - 監控優化過程

    優化器選擇指南：
    - BootstrapFewShot：適合大多數場景，快速簡單
    - BootstrapRS：需要更好性能，有較多訓練數據
    - MIPROv2：最先進，需要更多計算資源
    - COPRO：需要協同優化多個模組

    下一步：
    - 學習 RAG 管道構建（05_RAG管道.py）
    - 學習 Agent 構建（06_Agent構建.py）
    - 實際應用優化技術到你的項目
    """)


if __name__ == "__main__":
    main()
