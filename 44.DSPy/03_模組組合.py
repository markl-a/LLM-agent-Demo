"""
DSPy 模組組合進階教學

本模組展示如何組合和編排 DSPy 模組來構建複雜的 AI 系統：
1. 內建模組概覽（Predict, ChainOfThought, ReAct 等）
2. 自定義模組開發
3. 模組的串聯和並聯
4. 模組的條件執行
5. 複雜工作流設計
6. 模組狀態管理和數據流

作者：DSPy 教學團隊
日期：2025-01
"""

import dspy
from typing import List, Dict, Optional, Any, Tuple
import json


# ==================== 內建模組回顧 ====================

def demonstrate_builtin_modules():
    """
    演示 DSPy 內建模組

    DSPy 提供了多種預建模組，每種適合不同的任務
    """
    print("\n" + "="*60)
    print("DSPy 內建模組")
    print("="*60)

    class QA(dspy.Signature):
        """問答簽名"""
        question = dspy.InputField()
        answer = dspy.OutputField()

    question = "什麼是量子計算？"

    # 1. Predict - 最基本的預測模組
    print("\n1. Predict 模組")
    print("-" * 60)
    predict = dspy.Predict(QA)
    result = predict(question=question)
    print(f"答案：{result.answer}")

    # 2. ChainOfThought - 思維鏈推理
    print("\n2. ChainOfThought 模組")
    print("-" * 60)
    cot = dspy.ChainOfThought(QA)
    result = cot(question=question)
    print(f"推理：{result.rationale}")
    print(f"答案：{result.answer}")

    # 3. ProgramOfThought - 程式化思維（生成程式碼）
    print("\n3. ProgramOfThought 模組")
    print("-" * 60)
    print("適用於需要計算的問題")

    # 4. MultiChainComparison - 多鏈比較
    print("\n4. MultiChainComparison 模組")
    print("-" * 60)
    print("生成多個推理鏈並比較選擇最佳答案")


# ==================== 自定義簡單模組 ====================

class SimpleClassifier(dspy.Module):
    """
    簡單分類器模組

    展示如何創建最基本的自定義模組
    """

    def __init__(self):
        super().__init__()
        # 定義簽名
        class Classify(dspy.Signature):
            """文本分類"""
            text = dspy.InputField()
            category = dspy.OutputField()

        # 創建預測器
        self.classifier = dspy.Predict(Classify)

    def forward(self, text):
        """
        前向傳播方法

        Args:
            text: 輸入文本

        Returns:
            分類結果
        """
        return self.classifier(text=text)


class SentimentAnalyzer(dspy.Module):
    """
    情感分析器模組

    包含預處理和後處理邏輯
    """

    def __init__(self, use_cot=True):
        super().__init__()

        class AnalyzeSentiment(dspy.Signature):
            """分析文本情感"""
            text = dspy.InputField()
            sentiment = dspy.OutputField(desc="positive, negative, 或 neutral")
            confidence = dspy.OutputField(desc="置信度（0-100）")

        # 根據參數選擇模組類型
        if use_cot:
            self.analyzer = dspy.ChainOfThought(AnalyzeSentiment)
        else:
            self.analyzer = dspy.Predict(AnalyzeSentiment)

    def preprocess(self, text):
        """預處理文本"""
        # 移除多餘空白
        text = " ".join(text.split())
        # 截斷過長文本
        if len(text) > 1000:
            text = text[:1000] + "..."
        return text

    def forward(self, text):
        """執行情感分析"""
        # 預處理
        processed_text = self.preprocess(text)

        # 分析
        result = self.analyzer(text=processed_text)

        # 後處理
        return dspy.Prediction(
            sentiment=result.sentiment,
            confidence=result.confidence,
            original_text=text
        )


# ==================== 串聯式模組組合 ====================

class SequentialPipeline(dspy.Module):
    """
    串聯式管道

    多個模組按順序執行，前一個模組的輸出作為後一個模組的輸入
    """

    def __init__(self):
        super().__init__()

        # 步驟 1：理解問題
        class UnderstandQuestion(dspy.Signature):
            """理解問題的意圖"""
            question = dspy.InputField()
            intent = dspy.OutputField(desc="問題的意圖和關鍵點")
            keywords = dspy.OutputField(desc="關鍵詞列表")

        # 步驟 2：生成答案
        class GenerateAnswer(dspy.Signature):
            """基於意圖生成答案"""
            question = dspy.InputField()
            intent = dspy.InputField()
            keywords = dspy.InputField()
            answer = dspy.OutputField()

        # 步驟 3：優化答案
        class RefineAnswer(dspy.Signature):
            """優化和完善答案"""
            original_answer = dspy.InputField()
            refined_answer = dspy.OutputField(desc="更清晰、更準確的答案")

        self.understand = dspy.ChainOfThought(UnderstandQuestion)
        self.generate = dspy.ChainOfThought(GenerateAnswer)
        self.refine = dspy.Predict(RefineAnswer)

    def forward(self, question):
        """執行串聯處理"""
        # 步驟 1
        understanding = self.understand(question=question)

        # 步驟 2
        initial_answer = self.generate(
            question=question,
            intent=understanding.intent,
            keywords=understanding.keywords
        )

        # 步驟 3
        final = self.refine(original_answer=initial_answer.answer)

        return dspy.Prediction(
            intent=understanding.intent,
            keywords=understanding.keywords,
            initial_answer=initial_answer.answer,
            final_answer=final.refined_answer
        )


class DataProcessingPipeline(dspy.Module):
    """
    數據處理管道

    展示複雜的數據轉換流程
    """

    def __init__(self):
        super().__init__()

        # 提取
        class Extract(dspy.Signature):
            """從文本提取資訊"""
            text = dspy.InputField()
            entities = dspy.OutputField(desc="實體列表")
            facts = dspy.OutputField(desc="事實列表")

        # 轉換
        class Transform(dspy.Signature):
            """轉換提取的資訊"""
            entities = dspy.InputField()
            facts = dspy.InputField()
            structured_data = dspy.OutputField(desc="結構化的 JSON 數據")

        # 驗證
        class Validate(dspy.Signature):
            """驗證數據正確性"""
            structured_data = dspy.InputField()
            is_valid = dspy.OutputField(desc="是否有效（yes/no）")
            errors = dspy.OutputField(desc="錯誤列表（如果有）")

        self.extract = dspy.Predict(Extract)
        self.transform = dspy.Predict(Transform)
        self.validate = dspy.Predict(Validate)

    def forward(self, text):
        """執行 ETL 流程"""
        # Extract
        extracted = self.extract(text=text)

        # Transform
        transformed = self.transform(
            entities=extracted.entities,
            facts=extracted.facts
        )

        # Validate
        validated = self.validate(
            structured_data=transformed.structured_data
        )

        return dspy.Prediction(
            entities=extracted.entities,
            facts=extracted.facts,
            structured_data=transformed.structured_data,
            is_valid=validated.is_valid,
            errors=validated.errors
        )


# ==================== 並聯式模組組合 ====================

class ParallelEnsemble(dspy.Module):
    """
    並聯集成模組

    多個模組並行執行，然後綜合結果
    """

    def __init__(self, num_predictors=3):
        super().__init__()

        class Answer(dspy.Signature):
            """回答問題"""
            question = dspy.InputField()
            answer = dspy.OutputField()

        class Synthesize(dspy.Signature):
            """綜合多個答案"""
            question = dspy.InputField()
            answers = dspy.InputField(desc="多個候選答案")
            best_answer = dspy.OutputField(desc="最佳答案")
            reasoning = dspy.OutputField(desc="選擇理由")

        # 創建多個預測器
        self.predictors = [
            dspy.ChainOfThought(Answer)
            for _ in range(num_predictors)
        ]

        # 創建綜合器
        self.synthesizer = dspy.ChainOfThought(Synthesize)

    def forward(self, question):
        """並行生成並綜合答案"""
        # 並行生成多個答案
        answers = []
        for predictor in self.predictors:
            result = predictor(question=question)
            answers.append(result.answer)

        # 綜合答案
        answers_text = "\n".join([
            f"{i+1}. {ans}"
            for i, ans in enumerate(answers)
        ])

        synthesis = self.synthesizer(
            question=question,
            answers=answers_text
        )

        return dspy.Prediction(
            candidate_answers=answers,
            best_answer=synthesis.best_answer,
            reasoning=synthesis.reasoning
        )


class MultiPerspectiveAnalysis(dspy.Module):
    """
    多角度分析模組

    從不同角度並行分析同一個問題
    """

    def __init__(self):
        super().__init__()

        # 技術角度
        class TechnicalAnalysis(dspy.Signature):
            """技術分析"""
            topic = dspy.InputField()
            analysis = dspy.OutputField(desc="技術層面的分析")

        # 商業角度
        class BusinessAnalysis(dspy.Signature):
            """商業分析"""
            topic = dspy.InputField()
            analysis = dspy.OutputField(desc="商業層面的分析")

        # 社會角度
        class SocialAnalysis(dspy.Signature):
            """社會影響分析"""
            topic = dspy.InputField()
            analysis = dspy.OutputField(desc="社會影響分析")

        # 綜合報告
        class ComprehensiveReport(dspy.Signature):
            """生成綜合報告"""
            topic = dspy.InputField()
            technical = dspy.InputField()
            business = dspy.InputField()
            social = dspy.InputField()
            report = dspy.OutputField(desc="綜合分析報告")

        self.technical = dspy.ChainOfThought(TechnicalAnalysis)
        self.business = dspy.ChainOfThought(BusinessAnalysis)
        self.social = dspy.ChainOfThought(SocialAnalysis)
        self.reporter = dspy.Predict(ComprehensiveReport)

    def forward(self, topic):
        """執行多角度分析"""
        # 並行分析
        tech_result = self.technical(topic=topic)
        biz_result = self.business(topic=topic)
        social_result = self.social(topic=topic)

        # 生成綜合報告
        report = self.reporter(
            topic=topic,
            technical=tech_result.analysis,
            business=biz_result.analysis,
            social=social_result.analysis
        )

        return dspy.Prediction(
            technical_analysis=tech_result.analysis,
            business_analysis=biz_result.analysis,
            social_analysis=social_result.analysis,
            comprehensive_report=report.report
        )


# ==================== 條件式模組組合 ====================

class ConditionalRouter(dspy.Module):
    """
    條件路由模組

    根據輸入條件選擇不同的處理路徑
    """

    def __init__(self):
        super().__init__()

        # 分類器：判斷問題類型
        class ClassifyQuestion(dspy.Signature):
            """分類問題類型"""
            question = dspy.InputField()
            question_type = dspy.OutputField(
                desc="factual（事實性）, opinion（觀點性）, "
                     "calculation（計算性）, creative（創造性）"
            )

        # 不同類型的處理器
        class FactualQA(dspy.Signature):
            """回答事實性問題"""
            question = dspy.InputField()
            answer = dspy.OutputField(desc="基於事實的準確答案")

        class OpinionQA(dspy.Signature):
            """回答觀點性問題"""
            question = dspy.InputField()
            answer = dspy.OutputField(desc="平衡的觀點分析")

        class CalculationQA(dspy.Signature):
            """回答計算性問題"""
            question = dspy.InputField()
            steps = dspy.OutputField(desc="計算步驟")
            answer = dspy.OutputField(desc="計算結果")

        class CreativeQA(dspy.Signature):
            """回答創造性問題"""
            question = dspy.InputField()
            answer = dspy.OutputField(desc="創意性答案")

        self.classifier = dspy.Predict(ClassifyQuestion)
        self.factual_qa = dspy.Predict(FactualQA)
        self.opinion_qa = dspy.ChainOfThought(OpinionQA)
        self.calculation_qa = dspy.ChainOfThought(CalculationQA)
        self.creative_qa = dspy.ChainOfThought(CreativeQA)

    def forward(self, question):
        """根據問題類型路由到適當的處理器"""
        # 分類
        classification = self.classifier(question=question)
        q_type = classification.question_type.lower()

        # 路由
        if "factual" in q_type:
            result = self.factual_qa(question=question)
            answer = result.answer
            steps = None
        elif "opinion" in q_type:
            result = self.opinion_qa(question=question)
            answer = result.answer
            steps = result.rationale
        elif "calculation" in q_type:
            result = self.calculation_qa(question=question)
            answer = result.answer
            steps = result.steps
        else:  # creative
            result = self.creative_qa(question=question)
            answer = result.answer
            steps = result.rationale

        return dspy.Prediction(
            question_type=q_type,
            answer=answer,
            processing_steps=steps
        )


class AdaptiveProcessor(dspy.Module):
    """
    自適應處理器

    根據輸入複雜度調整處理策略
    """

    def __init__(self):
        super().__init__()

        class AssessComplexity(dspy.Signature):
            """評估問題複雜度"""
            question = dspy.InputField()
            complexity = dspy.OutputField(desc="simple, medium, complex")
            reasoning = dspy.OutputField(desc="評估理由")

        class SimpleQA(dspy.Signature):
            """簡單問答"""
            question = dspy.InputField()
            answer = dspy.OutputField()

        class ComplexQA(dspy.Signature):
            """複雜問答"""
            question = dspy.InputField()
            answer = dspy.OutputField()

        self.assessor = dspy.Predict(AssessComplexity)
        self.simple_qa = dspy.Predict(SimpleQA)
        self.medium_qa = dspy.ChainOfThought(SimpleQA)
        self.complex_qa = dspy.ChainOfThought(ComplexQA)

    def forward(self, question):
        """自適應處理"""
        # 評估複雜度
        assessment = self.assessor(question=question)
        complexity = assessment.complexity.lower()

        # 選擇適當的處理器
        if "simple" in complexity:
            result = self.simple_qa(question=question)
        elif "medium" in complexity:
            result = self.medium_qa(question=question)
        else:
            result = self.complex_qa(question=question)

        return dspy.Prediction(
            complexity=complexity,
            assessment_reasoning=assessment.reasoning,
            answer=result.answer
        )


# ==================== 循環式模組組合 ====================

class IterativeRefinement(dspy.Module):
    """
    迭代優化模組

    反覆優化結果直到達到質量標準
    """

    def __init__(self, max_iterations=3):
        super().__init__()
        self.max_iterations = max_iterations

        class GenerateAnswer(dspy.Signature):
            """生成答案"""
            question = dspy.InputField()
            previous_attempt = dspy.InputField(desc="之前的嘗試（如果有）")
            answer = dspy.OutputField()

        class EvaluateQuality(dspy.Signature):
            """評估答案質量"""
            question = dspy.InputField()
            answer = dspy.InputField()
            quality_score = dspy.OutputField(desc="質量分數（0-100）")
            improvements = dspy.OutputField(desc="改進建議")

        self.generator = dspy.ChainOfThought(GenerateAnswer)
        self.evaluator = dspy.Predict(EvaluateQuality)

    def forward(self, question):
        """迭代優化答案"""
        history = []
        current_answer = ""

        for i in range(self.max_iterations):
            # 生成答案
            result = self.generator(
                question=question,
                previous_attempt=current_answer if current_answer else "無"
            )
            current_answer = result.answer

            # 評估質量
            evaluation = self.evaluator(
                question=question,
                answer=current_answer
            )

            history.append({
                "iteration": i + 1,
                "answer": current_answer,
                "quality_score": evaluation.quality_score,
                "improvements": evaluation.improvements
            })

            # 如果質量足夠好，提前退出
            try:
                score = float(evaluation.quality_score)
                if score >= 90:
                    break
            except:
                pass

        return dspy.Prediction(
            final_answer=current_answer,
            iteration_history=history,
            iterations_used=len(history)
        )


# ==================== 複雜工作流範例 ====================

class ResearchAssistant(dspy.Module):
    """
    研究助手

    結合多種模組組合模式的複雜工作流
    """

    def __init__(self):
        super().__init__()

        # 問題分解
        class DecomposeQuestion(dspy.Signature):
            """將複雜問題分解為子問題"""
            question = dspy.InputField()
            sub_questions = dspy.OutputField(desc="子問題列表（用換行分隔）")

        # 回答子問題
        class AnswerSubQuestion(dspy.Signature):
            """回答子問題"""
            sub_question = dspy.InputField()
            answer = dspy.OutputField()

        # 綜合答案
        class SynthesizeAnswers(dspy.Signature):
            """綜合子問題的答案"""
            original_question = dspy.InputField()
            sub_qa_pairs = dspy.InputField(desc="子問題和答案對")
            final_answer = dspy.OutputField(desc="綜合後的完整答案")

        self.decomposer = dspy.ChainOfThought(DecomposeQuestion)
        self.sub_qa = dspy.ChainOfThought(AnswerSubQuestion)
        self.synthesizer = dspy.ChainOfThought(SynthesizeAnswers)

    def forward(self, question):
        """執行研究流程"""
        # 步驟 1：分解問題
        decomposition = self.decomposer(question=question)
        sub_questions = [
            q.strip()
            for q in decomposition.sub_questions.split("\n")
            if q.strip()
        ]

        # 步驟 2：並行回答所有子問題
        sub_answers = []
        for sub_q in sub_questions:
            result = self.sub_qa(sub_question=sub_q)
            sub_answers.append({
                "question": sub_q,
                "answer": result.answer
            })

        # 步驟 3：綜合答案
        qa_pairs_text = "\n\n".join([
            f"Q: {qa['question']}\nA: {qa['answer']}"
            for qa in sub_answers
        ])

        synthesis = self.synthesizer(
            original_question=question,
            sub_qa_pairs=qa_pairs_text
        )

        return dspy.Prediction(
            sub_questions=sub_questions,
            sub_answers=sub_answers,
            final_answer=synthesis.final_answer
        )


# ==================== 主程序 ====================

def main():
    """主函數：演示所有模組組合模式"""

    print("="*60)
    print("DSPy 模組組合進階教學")
    print("="*60)

    # 配置
    print("\n正在配置 DSPy...")
    try:
        lm = dspy.OpenAI(model="gpt-4", max_tokens=800)
        dspy.settings.configure(lm=lm)
        print("✓ 配置完成")
    except Exception as e:
        print(f"配置失敗：{e}")
        return

    # 1. 內建模組演示
    print("\n" + "="*60)
    print("1. 內建模組演示")
    print("="*60)
    try:
        demonstrate_builtin_modules()
    except Exception as e:
        print(f"錯誤：{e}")

    # 2. 簡單自定義模組
    print("\n" + "="*60)
    print("2. 簡單自定義模組")
    print("="*60)
    try:
        analyzer = SentimentAnalyzer()
        result = analyzer(text="這個產品真的很棒，超出預期！")
        print(f"情感：{result.sentiment}")
        print(f"置信度：{result.confidence}")
    except Exception as e:
        print(f"錯誤：{e}")

    # 3. 串聯式管道
    print("\n" + "="*60)
    print("3. 串聯式管道")
    print("="*60)
    try:
        pipeline = SequentialPipeline()
        result = pipeline(question="什麼是區塊鏈技術？")
        print(f"意圖：{result.intent}")
        print(f"關鍵詞：{result.keywords}")
        print(f"最終答案：{result.final_answer}")
    except Exception as e:
        print(f"錯誤：{e}")

    # 4. 並聯集成
    print("\n" + "="*60)
    print("4. 並聯集成")
    print("="*60)
    try:
        ensemble = ParallelEnsemble(num_predictors=3)
        result = ensemble(question="人工智能的未來發展方向是什麼？")
        print(f"候選答案數量：{len(result.candidate_answers)}")
        print(f"最佳答案：{result.best_answer}")
        print(f"選擇理由：{result.reasoning}")
    except Exception as e:
        print(f"錯誤：{e}")

    # 5. 條件路由
    print("\n" + "="*60)
    print("5. 條件路由")
    print("="*60)
    try:
        router = ConditionalRouter()
        questions = [
            "法國的首都是哪裡？",  # factual
            "你認為人工智能好還是不好？",  # opinion
            "25 乘以 17 等於多少？",  # calculation
        ]
        for q in questions:
            result = router(question=q)
            print(f"\n問題：{q}")
            print(f"類型：{result.question_type}")
            print(f"答案：{result.answer}")
    except Exception as e:
        print(f"錯誤：{e}")

    # 6. 迭代優化
    print("\n" + "="*60)
    print("6. 迭代優化")
    print("="*60)
    try:
        refiner = IterativeRefinement(max_iterations=3)
        result = refiner(question="解釋相對論的基本概念")
        print(f"迭代次數：{result.iterations_used}")
        print(f"最終答案：{result.final_answer}")
    except Exception as e:
        print(f"錯誤：{e}")

    # 總結
    print("\n" + "="*60)
    print("教學完成！")
    print("="*60)
    print("""
    你已經學會了：
    1. ✓ DSPy 內建模組的使用
    2. ✓ 創建自定義模組
    3. ✓ 串聯式模組組合（順序執行）
    4. ✓ 並聯式模組組合（並行執行）
    5. ✓ 條件式模組路由
    6. ✓ 迭代式優化流程
    7. ✓ 複雜工作流設計

    模組組合的關鍵原則：
    - 單一職責：每個模組專注一個任務
    - 可組合性：模組應該容易組合
    - 數據流清晰：輸入輸出明確
    - 錯誤處理：適當處理異常情況

    下一步：
    - 學習提示優化（04_提示優化.py）
    - 學習 RAG 管道構建（05_RAG管道.py）
    """)


if __name__ == "__main__":
    main()
