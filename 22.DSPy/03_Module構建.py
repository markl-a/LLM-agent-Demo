"""
DSPy Module 構建詳解
====================

本範例展示如何在 DSPy 中構建自定義模塊：
1. 理解內置模塊（Predict, ChainOfThought 等）
2. 創建簡單的自定義模塊
3. 創建複雜的組合模塊
4. 模塊的最佳實踐
5. 模塊的重用和組合

Module 是 DSPy 中封裝邏輯的基本單位，類似於 PyTorch 的 nn.Module。

作者：DSPy 學習示例
日期：2025-12-15
"""

import dspy
from typing import List, Optional, Union


# ============================================================================
# 1. 理解內置模塊
# ============================================================================

def explore_builtin_modules():
    """
    探索 DSPy 的內置模塊
    """
    print("\n" + "="*60)
    print("1. 內置模塊概覽")
    print("="*60)

    # 1.1 Predict - 最基礎的模塊
    print("\n1.1 dspy.Predict - 基礎預測模塊")
    predictor = dspy.Predict("question -> answer")
    result = predictor(question="什麼是模塊？")
    print(f"Predict 結果: {result.answer[:100]}...")

    # 1.2 ChainOfThought - 添加推理步驟
    print("\n1.2 dspy.ChainOfThought - 思維鏈模塊")
    cot = dspy.ChainOfThought("question -> answer")
    result = cot(question="為什麼天空是藍色的？")
    print(f"推理過程: {result.reasoning if hasattr(result, 'reasoning') else '自動生成'}...")
    print(f"最終答案: {result.answer[:100]}...")

    # 1.3 ProgramOfThought - 代碼輔助推理
    print("\n1.3 類 ProgramOfThought 的推理")
    # 注意：這是概念性示例，實際 API 可能略有不同
    print("可以讓模型生成代碼來輔助推理過程")


# ============================================================================
# 2. 創建簡單的自定義模塊
# ============================================================================

class SimpleQAModule(dspy.Module):
    """
    最簡單的自定義模塊
    封裝一個預測器
    """

    def __init__(self):
        super().__init__()
        # 在初始化時定義所需的子模塊
        self.predictor = dspy.Predict("question -> answer")

    def forward(self, question: str) -> dspy.Prediction:
        """
        前向傳播方法
        類似於 PyTorch 的 forward()
        """
        # 調用預測器
        prediction = self.predictor(question=question)
        return prediction


class TemperatureControlledQA(dspy.Module):
    """
    帶有溫度控制的問答模塊
    展示如何添加配置參數
    """

    def __init__(self, temperature: float = 0.7):
        super().__init__()
        self.temperature = temperature
        self.predictor = dspy.ChainOfThought("question -> answer")

    def forward(self, question: str) -> dspy.Prediction:
        """
        使用指定溫度進行預測
        """
        # 在 DSPy 中，溫度通常在 LM 配置層面設置
        # 這裡展示模塊如何攜帶配置信息
        result = self.predictor(question=question)
        return result


def simple_module_examples():
    """
    演示簡單的自定義模塊
    """
    print("\n" + "="*60)
    print("2. 創建簡單的自定義模塊")
    print("="*60)

    # 使用 SimpleQAModule
    print("\n2.1 SimpleQAModule")
    qa_module = SimpleQAModule()
    result = qa_module(question="DSPy 模塊的優勢是什麼？")
    print(f"答案: {result.answer[:150]}...")

    # 使用 TemperatureControlledQA
    print("\n2.2 TemperatureControlledQA")
    qa_module = TemperatureControlledQA(temperature=0.3)
    result = qa_module(question="解釋神經網絡")
    print(f"答案: {result.answer[:150]}...")


# ============================================================================
# 3. 創建複雜的組合模塊
# ============================================================================

class MultiStepReasoning(dspy.Module):
    """
    多步推理模塊
    將問題分解為多個子問題並逐步求解
    """

    def __init__(self):
        super().__init__()
        # 定義多個子模塊
        self.decompose = dspy.Predict("question -> sub_questions: list[str]")
        self.answer_sub = dspy.ChainOfThought("sub_question -> answer")
        self.synthesize = dspy.Predict("question, sub_answers: str -> final_answer")

    def forward(self, question: str) -> dspy.Prediction:
        """
        多步推理過程
        """
        # 步驟 1: 分解問題
        decomposition = self.decompose(question=question)
        print(f"  子問題: {decomposition.sub_questions}")

        # 步驟 2: 回答每個子問題
        sub_answers = []
        for sub_q in decomposition.sub_questions[:3]:  # 限制數量
            if isinstance(sub_q, str) and sub_q.strip():
                ans = self.answer_sub(sub_question=sub_q)
                sub_answers.append(f"Q: {sub_q}\nA: {ans.answer}")

        # 步驟 3: 綜合答案
        combined_answers = "\n\n".join(sub_answers)
        final = self.synthesize(
            question=question,
            sub_answers=combined_answers
        )

        return final


class RAGModule(dspy.Module):
    """
    檢索增強生成（RAG）模塊
    結合檢索和生成
    """

    def __init__(self, retriever_function=None):
        super().__init__()
        self.retriever = retriever_function
        self.generate_answer = dspy.ChainOfThought("context, question -> answer")

    def forward(self, question: str) -> dspy.Prediction:
        """
        RAG 流程：檢索 -> 生成
        """
        # 步驟 1: 檢索相關文檔
        if self.retriever:
            contexts = self.retriever(question)
        else:
            # 模擬檢索結果
            contexts = [
                "DSPy 是一個用於編程語言模型的框架。",
                "它由 Stanford NLP 團隊開發。",
                "DSPy 支持自動優化提示詞。"
            ]

        # 步驟 2: 組合上下文
        combined_context = "\n".join(contexts)

        # 步驟 3: 基於上下文生成答案
        result = self.generate_answer(
            context=combined_context,
            question=question
        )

        return result


class EnsembleModule(dspy.Module):
    """
    集成模塊
    使用多個預測器並組合結果
    """

    def __init__(self, num_predictors: int = 3):
        super().__init__()
        # 創建多個預測器
        self.predictors = [
            dspy.ChainOfThought("question -> answer")
            for _ in range(num_predictors)
        ]
        self.combiner = dspy.Predict(
            "question, answers: list[str] -> best_answer, reasoning"
        )

    def forward(self, question: str) -> dspy.Prediction:
        """
        集成多個預測結果
        """
        # 獲取多個預測
        predictions = []
        for i, predictor in enumerate(self.predictors):
            result = predictor(question=question)
            predictions.append(result.answer)
            print(f"  預測器 {i+1}: {result.answer[:80]}...")

        # 組合結果
        final = self.combiner(
            question=question,
            answers=predictions
        )

        return final


def complex_module_examples():
    """
    演示複雜的組合模塊
    """
    print("\n" + "="*60)
    print("3. 創建複雜的組合模塊")
    print("="*60)

    # 多步推理
    print("\n3.1 MultiStepReasoning")
    reasoning_module = MultiStepReasoning()
    result = reasoning_module(question="為什麼機器學習在現代 AI 中如此重要？")
    print(f"最終答案: {result.final_answer[:200]}...")

    # RAG 模塊
    print("\n3.2 RAGModule")
    rag_module = RAGModule()
    result = rag_module(question="DSPy 是誰開發的？")
    print(f"答案: {result.answer[:150]}...")

    # 集成模塊
    print("\n3.3 EnsembleModule")
    ensemble = EnsembleModule(num_predictors=2)
    result = ensemble(question="什麼是深度學習？")
    print(f"最佳答案: {result.best_answer[:150]}...")
    print(f"推理: {result.reasoning[:100]}...")


# ============================================================================
# 4. 帶有狀態管理的模塊
# ============================================================================

class ConversationalModule(dspy.Module):
    """
    對話模塊
    維護對話歷史狀態
    """

    def __init__(self, max_history: int = 5):
        super().__init__()
        self.max_history = max_history
        self.history = []
        self.respond = dspy.Predict("history: str, question -> answer")

    def forward(self, question: str) -> dspy.Prediction:
        """
        基於歷史的對話回復
        """
        # 格式化歷史
        history_text = "\n".join([
            f"Q: {h['question']}\nA: {h['answer']}"
            for h in self.history[-self.max_history:]
        ])

        # 生成回答
        result = self.respond(
            history=history_text,
            question=question
        )

        # 更新歷史
        self.history.append({
            "question": question,
            "answer": result.answer
        })

        return result

    def reset(self):
        """重置對話歷史"""
        self.history = []


class AdaptiveModule(dspy.Module):
    """
    自適應模塊
    根據反饋調整行為
    """

    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought("question -> answer")
        self.feedback_history = []
        self.success_count = 0
        self.total_count = 0

    def forward(self, question: str) -> dspy.Prediction:
        """
        自適應預測
        """
        result = self.predictor(question=question)
        self.total_count += 1
        return result

    def provide_feedback(self, is_correct: bool):
        """
        接收反饋並調整
        """
        self.feedback_history.append(is_correct)
        if is_correct:
            self.success_count += 1

    def get_performance_stats(self) -> dict:
        """
        獲取性能統計
        """
        return {
            "accuracy": self.success_count / self.total_count if self.total_count > 0 else 0,
            "total_queries": self.total_count,
            "successful_queries": self.success_count
        }


def stateful_module_examples():
    """
    演示帶有狀態管理的模塊
    """
    print("\n" + "="*60)
    print("4. 帶有狀態管理的模塊")
    print("="*60)

    # 對話模塊
    print("\n4.1 ConversationalModule")
    chat = ConversationalModule(max_history=3)

    questions = [
        "什麼是 Python？",
        "它有什麼優勢？",
        "如何開始學習？"
    ]

    for q in questions:
        result = chat(question=q)
        print(f"\nQ: {q}")
        print(f"A: {result.answer[:100]}...")

    # 自適應模塊
    print("\n4.2 AdaptiveModule")
    adaptive = AdaptiveModule()

    # 進行幾次預測並提供反饋
    result = adaptive(question="2 + 2 = ?")
    print(f"答案: {result.answer}")
    adaptive.provide_feedback(True)

    result = adaptive(question="3 * 3 = ?")
    print(f"答案: {result.answer}")
    adaptive.provide_feedback(True)

    stats = adaptive.get_performance_stats()
    print(f"性能統計: {stats}")


# ============================================================================
# 5. 模塊的組合和鏈接
# ============================================================================

class PreprocessModule(dspy.Module):
    """預處理模塊"""

    def __init__(self):
        super().__init__()
        self.cleaner = dspy.Predict("text -> cleaned_text, notes")

    def forward(self, text: str):
        return self.cleaner(text=text)


class AnalysisModule(dspy.Module):
    """分析模塊"""

    def __init__(self):
        super().__init__()
        self.analyzer = dspy.ChainOfThought("text -> analysis, key_points: list[str]")

    def forward(self, text: str):
        return self.analyzer(text=text)


class PostprocessModule(dspy.Module):
    """後處理模塊"""

    def __init__(self):
        super().__init__()
        self.formatter = dspy.Predict("analysis, key_points: str -> formatted_report")

    def forward(self, analysis: str, key_points):
        key_points_str = ", ".join(key_points) if isinstance(key_points, list) else str(key_points)
        return self.formatter(analysis=analysis, key_points=key_points_str)


class PipelineModule(dspy.Module):
    """
    流水線模塊
    組合多個模塊形成處理流水線
    """

    def __init__(self):
        super().__init__()
        self.preprocess = PreprocessModule()
        self.analyze = AnalysisModule()
        self.postprocess = PostprocessModule()

    def forward(self, text: str):
        """
        完整的處理流水線
        """
        # 階段 1: 預處理
        cleaned = self.preprocess(text=text)
        print(f"  預處理: {cleaned.cleaned_text[:50]}...")

        # 階段 2: 分析
        analysis = self.analyze(text=cleaned.cleaned_text)
        print(f"  分析: {analysis.analysis[:50]}...")
        print(f"  關鍵點: {analysis.key_points}")

        # 階段 3: 後處理
        report = self.postprocess(
            analysis=analysis.analysis,
            key_points=analysis.key_points
        )

        return report


def composition_examples():
    """
    演示模塊的組合和鏈接
    """
    print("\n" + "="*60)
    print("5. 模塊的組合和鏈接")
    print("="*60)

    print("\n5.1 PipelineModule")
    pipeline = PipelineModule()
    result = pipeline(text="人工智能正在改變世界，特別是在醫療、教育和交通領域。")
    print(f"\n最終報告: {result.formatted_report[:200]}...")


# ============================================================================
# 6. 模塊最佳實踐
# ============================================================================

def module_best_practices():
    """
    模塊設計的最佳實踐
    """
    print("\n" + "="*60)
    print("6. 模塊最佳實踐")
    print("="*60)

    best_practices = """
    DSPy 模塊設計最佳實踐：

    ✓ 1. 單一職責原則
       - 每個模塊應該只做一件事
       - 保持模塊的簡單和專注

    ✓ 2. 在 __init__ 中定義子模塊
       - 所有子模塊應該在初始化時創建
       - 不要在 forward() 中創建新模塊

    ✓ 3. 使用清晰的 forward() 方法
       - forward() 應該表達清晰的邏輯流程
       - 避免過於複雜的嵌套邏輯

    ✓ 4. 參數化配置
       - 將可配置的參數作為 __init__ 參數
       - 使用有意義的默認值

    ✓ 5. 返回結構化的 Prediction 對象
       - 利用 DSPy 的 Prediction 對象
       - 包含所有相關信息

    ✓ 6. 模塊組合而非繼承
       - 優先使用組合而不是繼承
       - 使模塊更容易測試和重用

    ✓ 7. 添加文檔和註釋
       - 為每個模塊添加 docstring
       - 說明模塊的用途和參數

    ✓ 8. 狀態管理
       - 謹慎處理模塊狀態
       - 提供重置狀態的方法

    ✓ 9. 錯誤處理
       - 添加適當的錯誤處理
       - 提供有意義的錯誤信息

    ✓ 10. 可測試性
        - 設計易於測試的模塊
        - 考慮依賴注入
    """

    print(best_practices)


# ============================================================================
# 主程序
# ============================================================================

def main():
    """
    主函數：運行所有模塊構建範例
    """
    print("DSPy Module 構建詳解")
    print("=" * 60)

    try:
        # 配置語言模型
        lm = dspy.LM('openai/gpt-4o-mini')
        dspy.configure(lm=lm)
        print(f"✓ 已配置語言模型: {lm.model}")

        # 運行各種範例
        explore_builtin_modules()
        simple_module_examples()
        complex_module_examples()
        stateful_module_examples()
        composition_examples()
        module_best_practices()

        print("\n" + "="*60)
        print("所有 Module 範例運行完成！")
        print("="*60)

    except Exception as e:
        print(f"\n錯誤：{e}")
        print("\n提示：請確保設置了 OPENAI_API_KEY 環境變數")


if __name__ == "__main__":
    main()


"""
模塊設計模式總結
================

1. 簡單模塊模式：
   - 單一預測器封裝
   - 適合基礎任務

2. 鏈式模塊模式：
   - 多個步驟順序執行
   - 每步的輸出作為下一步的輸入

3. 並行模塊模式：
   - 多個預測器並行執行
   - 組合或選擇最佳結果

4. 條件模塊模式：
   - 根據條件選擇不同的處理路徑
   - 實現動態行為

5. 迭代模塊模式：
   - 重複執行直到滿足條件
   - 實現自我優化

下一步學習：
- 04_優化器使用.py - 學習如何優化模塊
- 05_檢索增強.py - 深入 RAG 模塊實現
"""
