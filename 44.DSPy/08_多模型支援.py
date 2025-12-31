"""
DSPy 多模型支援教學

本模組展示如何在 DSPy 中使用多個不同的 LLM 提供商：
1. 支援的 LLM 提供商概覽
2. OpenAI 模型配置
3. Anthropic Claude 配置
4. Google Gemini 配置
5. 本地模型（Ollama）配置
6. 多模型協作
7. 模型選擇策略
8. 成本和性能優化

作者：DSPy 教學團隊
日期：2025-01
"""

import dspy
from typing import List, Dict, Optional, Any
import os


# ==================== 多模型概念 ====================

def explain_multi_model_concept():
    """
    解釋多模型支援的概念和優勢

    為什麼使用多個模型？
    - 成本優化
    - 性能優化
    - 容錯備援
    - 任務專精
    """
    print("\n" + "="*60)
    print("多模型支援概念")
    print("="*60)

    print("""
    多模型支援的優勢：
    1. 成本優化：簡單任務用便宜模型，複雜任務用強大模型
    2. 性能優化：選擇最適合特定任務的模型
    3. 容錯備援：一個模型失敗時切換到另一個
    4. 任務專精：不同模型擅長不同任務

    常見 LLM 提供商：
    - OpenAI：GPT-4, GPT-3.5 Turbo
    - Anthropic：Claude 3.5 Sonnet, Claude Opus
    - Google：Gemini Pro, Gemini Ultra
    - Cohere：Command, Command Light
    - 本地模型：Ollama, vLLM

    模型選擇考量：
    - 成本：每 1K tokens 的價格
    - 速度：響應時間
    - 質量：輸出準確度
    - 上下文長度：支援的 token 數
    - 特殊能力：函數調用、視覺理解等

    DSPy 多模型策略：
    - 單一模型：所有任務用同一個模型
    - 分層模型：不同模組用不同模型
    - 動態選擇：根據任務特徵選擇模型
    - 並行調用：同時調用多個模型取最佳結果
    """)


# ==================== OpenAI 配置 ====================

def setup_openai_models():
    """
    配置 OpenAI 模型

    OpenAI 是最常用的提供商，提供多種模型
    """
    print("\n" + "="*60)
    print("OpenAI 模型配置")
    print("="*60)

    api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")

    # GPT-4：最強大的模型
    gpt4 = dspy.OpenAI(
        model="gpt-4",
        max_tokens=1000,
        temperature=0.7,
        api_key=api_key
    )
    print("✓ GPT-4 配置完成")
    print("  - 用途：複雜推理、創意任務")
    print("  - 成本：高")
    print("  - 速度：較慢")

    # GPT-3.5 Turbo：快速且經濟
    gpt35 = dspy.OpenAI(
        model="gpt-3.5-turbo",
        max_tokens=500,
        temperature=0.7,
        api_key=api_key
    )
    print("\n✓ GPT-3.5 Turbo 配置完成")
    print("  - 用途：簡單問答、分類")
    print("  - 成本：低")
    print("  - 速度：快")

    # GPT-4 Turbo：平衡性能和成本
    gpt4_turbo = dspy.OpenAI(
        model="gpt-4-turbo-preview",
        max_tokens=1000,
        temperature=0.7,
        api_key=api_key
    )
    print("\n✓ GPT-4 Turbo 配置完成")
    print("  - 用途：需要高質量但要控制成本")
    print("  - 成本：中等")
    print("  - 速度：中等")

    return {
        "gpt-4": gpt4,
        "gpt-3.5-turbo": gpt35,
        "gpt-4-turbo": gpt4_turbo
    }


# ==================== Anthropic Claude 配置 ====================

def setup_anthropic_models():
    """
    配置 Anthropic Claude 模型

    Claude 在長文本理解和推理上表現優異
    """
    print("\n" + "="*60)
    print("Anthropic Claude 模型配置")
    print("="*60)

    api_key = os.getenv("ANTHROPIC_API_KEY", "your-api-key-here")

    try:
        # Claude 3.5 Sonnet：最新最強
        claude_sonnet = dspy.Claude(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            api_key=api_key
        )
        print("✓ Claude 3.5 Sonnet 配置完成")
        print("  - 用途：複雜推理、程式碼生成")
        print("  - 成本：中高")
        print("  - 速度：快")
        print("  - 特點：200K 上下文窗口")

        # Claude 3 Opus：最強大（如果可用）
        # claude_opus = dspy.Claude(
        #     model="claude-3-opus-20240229",
        #     max_tokens=1000,
        #     api_key=api_key
        # )

        # Claude 3 Haiku：快速經濟
        claude_haiku = dspy.Claude(
            model="claude-3-haiku-20240307",
            max_tokens=500,
            api_key=api_key
        )
        print("\n✓ Claude 3 Haiku 配置完成")
        print("  - 用途：快速回應、簡單任務")
        print("  - 成本：低")
        print("  - 速度：非常快")

        return {
            "claude-3.5-sonnet": claude_sonnet,
            "claude-3-haiku": claude_haiku
        }
    except Exception as e:
        print(f"Claude 配置失敗：{e}")
        return {}


# ==================== 本地模型配置 ====================

def setup_local_models():
    """
    配置本地模型（Ollama）

    本地模型的優勢：
    - 完全免費
    - 數據隱私
    - 無網路依賴
    """
    print("\n" + "="*60)
    print("本地模型配置（Ollama）")
    print("="*60)

    try:
        # 配置 Ollama
        # 需要先安裝並運行 Ollama
        # 下載模型：ollama pull llama2

        # 使用自定義 LM 類
        class OllamaLM(dspy.LM):
            def __init__(self, model="llama2", base_url="http://localhost:11434"):
                self.model = model
                self.base_url = base_url

            def __call__(self, prompt, **kwargs):
                # 這裡需要實現實際的 Ollama API 調用
                # 這只是一個示例框架
                import requests

                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                )

                if response.status_code == 200:
                    return response.json()["response"]
                else:
                    raise Exception(f"Ollama 錯誤：{response.status_code}")

        # llama2 = OllamaLM(model="llama2")
        print("✓ Ollama 配置說明")
        print("  - 安裝：curl -fsSL https://ollama.com/install.sh | sh")
        print("  - 下載模型：ollama pull llama2")
        print("  - 運行：ollama serve")
        print("  - 用途：本地開發、隱私保護")
        print("  - 成本：免費")
        print("  - 速度：取決於硬體")

        return {}
    except Exception as e:
        print(f"本地模型配置說明：{e}")
        return {}


# ==================== 模型選擇策略 ====================

class ModelSelector:
    """
    智能模型選擇器

    根據任務特徵自動選擇最合適的模型
    """

    def __init__(self, models: Dict[str, Any]):
        """
        初始化模型選擇器

        Args:
            models: 可用模型字典 {name: model_instance}
        """
        self.models = models

    def select_by_task_type(self, task_type: str) -> Any:
        """
        根據任務類型選擇模型

        Args:
            task_type: 任務類型（simple, complex, creative, analytical）

        Returns:
            選擇的模型實例
        """
        if task_type == "simple":
            # 簡單任務：優先選擇快速便宜的模型
            if "gpt-3.5-turbo" in self.models:
                return self.models["gpt-3.5-turbo"]
            elif "claude-3-haiku" in self.models:
                return self.models["claude-3-haiku"]

        elif task_type == "complex":
            # 複雜任務：選擇最強大的模型
            if "gpt-4" in self.models:
                return self.models["gpt-4"]
            elif "claude-3.5-sonnet" in self.models:
                return self.models["claude-3.5-sonnet"]

        elif task_type == "creative":
            # 創意任務：選擇創意性強的模型
            if "gpt-4" in self.models:
                return self.models["gpt-4"]

        elif task_type == "analytical":
            # 分析任務：選擇推理能力強的模型
            if "claude-3.5-sonnet" in self.models:
                return self.models["claude-3.5-sonnet"]
            elif "gpt-4" in self.models:
                return self.models["gpt-4"]

        # 默認選擇第一個可用模型
        return list(self.models.values())[0] if self.models else None

    def select_by_cost(self, budget: str) -> Any:
        """
        根據預算選擇模型

        Args:
            budget: 預算水平（low, medium, high）

        Returns:
            選擇的模型實例
        """
        if budget == "low":
            # 低預算：選擇最便宜的模型
            if "gpt-3.5-turbo" in self.models:
                return self.models["gpt-3.5-turbo"]
            elif "claude-3-haiku" in self.models:
                return self.models["claude-3-haiku"]

        elif budget == "medium":
            # 中等預算
            if "gpt-4-turbo" in self.models:
                return self.models["gpt-4-turbo"]
            elif "claude-3.5-sonnet" in self.models:
                return self.models["claude-3.5-sonnet"]

        elif budget == "high":
            # 高預算：使用最好的模型
            if "gpt-4" in self.models:
                return self.models["gpt-4"]

        return list(self.models.values())[0] if self.models else None


# ==================== 多模型協作 ====================

class MultiModelPipeline(dspy.Module):
    """
    多模型協作管道

    不同的任務步驟使用不同的模型
    """

    def __init__(self, models: Dict[str, Any]):
        super().__init__()
        self.models = models

        # 定義簽名
        class Analyze(dspy.Signature):
            """分析問題"""
            question = dspy.InputField()
            analysis = dspy.OutputField()

        class GenerateAnswer(dspy.Signature):
            """生成詳細答案"""
            question = dspy.InputField()
            analysis = dspy.InputField()
            answer = dspy.OutputField()

        class RefineAnswer(dspy.Signature):
            """優化答案"""
            answer = dspy.InputField()
            refined_answer = dspy.OutputField()

        # 為不同步驟配置不同模型
        # 步驟 1：快速分析 - 使用便宜的模型
        if "gpt-3.5-turbo" in models:
            with dspy.context(lm=models["gpt-3.5-turbo"]):
                self.analyze = dspy.Predict(Analyze)
        else:
            self.analyze = dspy.Predict(Analyze)

        # 步驟 2：生成答案 - 使用強大的模型
        if "gpt-4" in models:
            with dspy.context(lm=models["gpt-4"]):
                self.generate = dspy.ChainOfThought(GenerateAnswer)
        else:
            self.generate = dspy.ChainOfThought(GenerateAnswer)

        # 步驟 3：優化 - 使用中等模型
        if "claude-3.5-sonnet" in models:
            with dspy.context(lm=models["claude-3.5-sonnet"]):
                self.refine = dspy.Predict(RefineAnswer)
        else:
            self.refine = dspy.Predict(RefineAnswer)

    def forward(self, question):
        """執行多模型管道"""
        # 步驟 1：分析（快速模型）
        analysis_result = self.analyze(question=question)

        # 步驟 2：生成（強大模型）
        generation_result = self.generate(
            question=question,
            analysis=analysis_result.analysis
        )

        # 步驟 3：優化（中等模型）
        refinement_result = self.refine(
            answer=generation_result.answer
        )

        return dspy.Prediction(
            analysis=analysis_result.analysis,
            initial_answer=generation_result.answer,
            final_answer=refinement_result.refined_answer
        )


class EnsembleModel(dspy.Module):
    """
    集成模型

    並行調用多個模型，綜合結果
    """

    def __init__(self, models: List[Any]):
        super().__init__()
        self.models = models

        class Answer(dspy.Signature):
            """回答問題"""
            question = dspy.InputField()
            answer = dspy.OutputField()

        class Synthesize(dspy.Signature):
            """綜合多個答案"""
            question = dspy.InputField()
            answers = dspy.InputField()
            best_answer = dspy.OutputField()

        # 為每個模型創建預測器
        self.predictors = []
        for model in models:
            with dspy.context(lm=model):
                self.predictors.append(dspy.Predict(Answer))

        # 使用第一個模型進行綜合
        with dspy.context(lm=models[0]):
            self.synthesizer = dspy.Predict(Synthesize)

    def forward(self, question):
        """並行調用多個模型"""
        # 收集所有答案
        answers = []
        for i, predictor in enumerate(self.predictors):
            try:
                result = predictor(question=question)
                answers.append(f"模型 {i+1}: {result.answer}")
            except Exception as e:
                print(f"模型 {i+1} 錯誤：{e}")
                continue

        # 綜合答案
        if answers:
            answers_text = "\n".join(answers)
            synthesis = self.synthesizer(
                question=question,
                answers=answers_text
            )
            return dspy.Prediction(
                individual_answers=answers,
                final_answer=synthesis.best_answer
            )
        else:
            return dspy.Prediction(
                individual_answers=[],
                final_answer="所有模型都失敗了"
            )


# ==================== 成本優化策略 ====================

class CostOptimizedModule(dspy.Module):
    """
    成本優化模組

    根據問題複雜度動態選擇模型
    """

    def __init__(self, cheap_model, expensive_model):
        super().__init__()
        self.cheap_model = cheap_model
        self.expensive_model = expensive_model

        # 複雜度評估
        class AssessComplexity(dspy.Signature):
            """評估問題複雜度"""
            question = dspy.InputField()
            complexity = dspy.OutputField(desc="simple 或 complex")

        # 簡單答案
        class SimpleAnswer(dspy.Signature):
            """回答簡單問題"""
            question = dspy.InputField()
            answer = dspy.OutputField()

        # 複雜答案
        class ComplexAnswer(dspy.Signature):
            """回答複雜問題"""
            question = dspy.InputField()
            answer = dspy.OutputField()

        # 使用便宜模型評估複雜度
        with dspy.context(lm=cheap_model):
            self.assess = dspy.Predict(AssessComplexity)
            self.simple_answer = dspy.Predict(SimpleAnswer)

        # 使用昂貴模型處理複雜問題
        with dspy.context(lm=expensive_model):
            self.complex_answer = dspy.ChainOfThought(ComplexAnswer)

    def forward(self, question):
        """動態選擇模型"""
        # 評估複雜度
        assessment = self.assess(question=question)

        # 根據複雜度選擇模型
        if "simple" in assessment.complexity.lower():
            result = self.simple_answer(question=question)
            model_used = "cheap"
        else:
            result = self.complex_answer(question=question)
            model_used = "expensive"

        return dspy.Prediction(
            answer=result.answer,
            model_used=model_used,
            complexity=assessment.complexity
        )


# ==================== 主程序 ====================

def main():
    """主函數：演示多模型支援"""

    print("="*60)
    print("DSPy 多模型支援教學")
    print("="*60)

    # 1. 概念說明
    explain_multi_model_concept()

    # 2. 配置各種模型
    print("\n" + "="*60)
    print("配置模型")
    print("="*60)

    all_models = {}

    # OpenAI 模型
    try:
        openai_models = setup_openai_models()
        all_models.update(openai_models)
    except Exception as e:
        print(f"OpenAI 配置失敗：{e}")

    # Anthropic 模型
    try:
        anthropic_models = setup_anthropic_models()
        all_models.update(anthropic_models)
    except Exception as e:
        print(f"Anthropic 配置失敗：{e}")

    # 本地模型
    try:
        local_models = setup_local_models()
        all_models.update(local_models)
    except Exception as e:
        print(f"本地模型配置失敗：{e}")

    print(f"\n總共配置了 {len(all_models)} 個模型")

    # 3. 模型選擇器演示
    if all_models:
        print("\n" + "="*60)
        print("模型選擇器演示")
        print("="*60)

        selector = ModelSelector(all_models)

        print("\n根據任務類型選擇：")
        for task_type in ["simple", "complex", "creative", "analytical"]:
            model = selector.select_by_task_type(task_type)
            if model:
                print(f"  {task_type}: {type(model).__name__}")

        print("\n根據預算選擇：")
        for budget in ["low", "medium", "high"]:
            model = selector.select_by_cost(budget)
            if model:
                print(f"  {budget}: {type(model).__name__}")

    # 4. 配置默認模型進行演示
    try:
        # 使用 GPT-3.5 作為演示
        default_lm = dspy.OpenAI(model="gpt-3.5-turbo", max_tokens=300)
        dspy.settings.configure(lm=default_lm)
        print("\n✓ 默認模型配置完成（GPT-3.5 Turbo）")
    except Exception as e:
        print(f"\n配置默認模型失敗：{e}")
        print("某些演示可能無法運行")

    # 5. 多模型協作演示（概念性）
    print("\n" + "="*60)
    print("多模型協作策略")
    print("="*60)
    print("""
    策略 1：分層處理
    - 簡單預處理：GPT-3.5 Turbo
    - 核心處理：GPT-4 或 Claude Sonnet
    - 後處理優化：GPT-4 Turbo

    策略 2：並行集成
    - 同時調用多個模型
    - 綜合所有結果
    - 提高答案可靠性

    策略 3：成本優化
    - 先評估問題複雜度
    - 簡單問題用便宜模型
    - 複雜問題用強大模型

    策略 4：容錯備援
    - 主模型失敗時
    - 自動切換到備用模型
    - 確保服務可用性
    """)

    # 總結
    print("\n" + "="*60)
    print("教學完成！")
    print("="*60)
    print("""
    你已經學會了：
    1. ✓ 多模型支援的概念和優勢
    2. ✓ 配置 OpenAI 模型
    3. ✓ 配置 Anthropic Claude 模型
    4. ✓ 配置本地模型（Ollama）
    5. ✓ 智能模型選擇策略
    6. ✓ 多模型協作模式
    7. ✓ 成本優化技巧

    模型選擇建議：

    開發階段：
    - 使用 GPT-3.5 Turbo 或本地模型
    - 快速迭代，降低成本

    測試階段：
    - 使用目標生產模型
    - 評估實際性能

    生產階段：
    - 根據任務選擇模型
    - 實施成本監控
    - 設置備用方案

    成本優化技巧：
    - 簡單任務用 GPT-3.5
    - 複雜任務用 GPT-4
    - 批量處理降低調用次數
    - 使用緩存避免重複調用
    - 考慮使用本地模型

    下一步：
    - 學習緩存策略（09_緩存策略.py）
    - 學習生產部署（10_生產部署.py）
    - 實施成本監控系統
    """)


if __name__ == "__main__":
    main()
