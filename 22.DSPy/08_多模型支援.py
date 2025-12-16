"""
DSPy 多模型支援範例
==================

本範例展示如何在 DSPy 中使用多種語言模型。

支援的模型：
1. OpenAI GPT 系列
2. Anthropic Claude
3. Google Gemini
4. 本地模型 (Ollama, vLLM)
5. Azure OpenAI

安裝依賴：
pip install dspy-ai openai anthropic google-generativeai
"""

import dspy
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# ============================================================
# 1. OpenAI 模型配置
# ============================================================

OPENAI_CONFIG = '''
import dspy

# GPT-3.5 Turbo
gpt35 = dspy.OpenAI(
    model='gpt-3.5-turbo',
    api_key='your-api-key',
    max_tokens=1000,
    temperature=0.7
)

# GPT-4
gpt4 = dspy.OpenAI(
    model='gpt-4',
    api_key='your-api-key',
    max_tokens=2000,
    temperature=0.5
)

# GPT-4 Turbo
gpt4_turbo = dspy.OpenAI(
    model='gpt-4-turbo-preview',
    api_key='your-api-key',
    max_tokens=4000
)

# 設置默認模型
dspy.settings.configure(lm=gpt35)
'''


# ============================================================
# 2. Anthropic Claude 配置
# ============================================================

CLAUDE_CONFIG = '''
import dspy

# Claude 3 Opus
claude_opus = dspy.Claude(
    model='claude-3-opus-20240229',
    api_key='your-anthropic-key',
    max_tokens=2000
)

# Claude 3 Sonnet
claude_sonnet = dspy.Claude(
    model='claude-3-sonnet-20240229',
    api_key='your-anthropic-key'
)

# Claude 3 Haiku (快速)
claude_haiku = dspy.Claude(
    model='claude-3-haiku-20240307',
    api_key='your-anthropic-key'
)

dspy.settings.configure(lm=claude_sonnet)
'''


# ============================================================
# 3. Google Gemini 配置
# ============================================================

GEMINI_CONFIG = '''
import dspy

# Gemini Pro
gemini = dspy.Google(
    model='gemini-pro',
    api_key='your-google-key'
)

# Gemini Pro Vision (多模態)
gemini_vision = dspy.Google(
    model='gemini-pro-vision',
    api_key='your-google-key'
)

dspy.settings.configure(lm=gemini)
'''


# ============================================================
# 4. 本地模型配置
# ============================================================

OLLAMA_CONFIG = '''
import dspy

# Ollama 本地模型
ollama_llama = dspy.OllamaLocal(
    model='llama2',
    base_url='http://localhost:11434'
)

# Mistral
ollama_mistral = dspy.OllamaLocal(
    model='mistral',
    base_url='http://localhost:11434'
)

# CodeLlama
ollama_codellama = dspy.OllamaLocal(
    model='codellama',
    base_url='http://localhost:11434'
)

dspy.settings.configure(lm=ollama_llama)
'''

VLLM_CONFIG = '''
import dspy

# vLLM 服務器
vllm = dspy.HFClientVLLM(
    model='meta-llama/Llama-2-7b-chat-hf',
    port=8000,
    url='http://localhost'
)

dspy.settings.configure(lm=vllm)
'''


# ============================================================
# 5. Azure OpenAI 配置
# ============================================================

AZURE_CONFIG = '''
import dspy

# Azure OpenAI
azure_openai = dspy.AzureOpenAI(
    api_base='https://your-resource.openai.azure.com/',
    api_version='2024-02-15-preview',
    deployment_id='your-deployment',
    api_key='your-azure-key'
)

dspy.settings.configure(lm=azure_openai)
'''


# ============================================================
# 6. 多模型管理器
# ============================================================

class ModelManager:
    """多模型管理器"""

    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.default_model: str = None

    def register_model(self, name: str, model: Any, set_default: bool = False):
        """註冊模型"""
        self.models[name] = model
        if set_default or self.default_model is None:
            self.default_model = name

    def get_model(self, name: str = None) -> Any:
        """獲取模型"""
        name = name or self.default_model
        return self.models.get(name)

    def set_default(self, name: str):
        """設置默認模型"""
        if name in self.models:
            self.default_model = name
            dspy.settings.configure(lm=self.models[name])

    def list_models(self) -> List[str]:
        """列出所有模型"""
        return list(self.models.keys())

    def switch_model(self, name: str):
        """切換模型"""
        if name in self.models:
            dspy.settings.configure(lm=self.models[name])
            return True
        return False


# ============================================================
# 7. 模型路由器
# ============================================================

@dataclass
class ModelConfig:
    """模型配置"""
    name: str
    max_tokens: int
    cost_per_1k_tokens: float
    capabilities: List[str]


class ModelRouter:
    """智能模型路由器"""

    def __init__(self):
        self.models: Dict[str, ModelConfig] = {}
        self.model_instances: Dict[str, Any] = {}

    def add_model(self, config: ModelConfig, instance: Any):
        """添加模型"""
        self.models[config.name] = config
        self.model_instances[config.name] = instance

    def route(
        self,
        task_type: str,
        complexity: str = "medium",
        budget: str = "normal"
    ) -> str:
        """根據任務路由到合適的模型"""
        # 簡單的路由邏輯
        if task_type == "code":
            # 代碼任務
            if complexity == "high":
                return "gpt-4"
            return "codellama"

        elif task_type == "chat":
            # 對話任務
            if budget == "low":
                return "gpt-3.5-turbo"
            return "claude-3-sonnet"

        elif task_type == "analysis":
            # 分析任務
            if complexity == "high":
                return "gpt-4-turbo"
            return "gpt-4"

        elif task_type == "simple":
            # 簡單任務
            return "gpt-3.5-turbo"

        # 默認
        return "gpt-3.5-turbo"

    def get_model(self, name: str) -> Any:
        """獲取模型實例"""
        return self.model_instances.get(name)


# ============================================================
# 8. 模型集成
# ============================================================

class EnsemblePredictor(dspy.Module):
    """模型集成預測器"""

    def __init__(self, models: List[Any], aggregation: str = "voting"):
        super().__init__()
        self.models = models
        self.aggregation = aggregation
        self.predictors = [dspy.Predict("question -> answer") for _ in models]

    def forward(self, question: str):
        results = []

        # 使用每個模型預測
        for model, predictor in zip(self.models, self.predictors):
            original_lm = dspy.settings.lm
            dspy.settings.configure(lm=model)

            try:
                result = predictor(question=question)
                results.append(result.answer)
            except Exception as e:
                print(f"模型錯誤: {e}")
            finally:
                dspy.settings.configure(lm=original_lm)

        # 聚合結果
        if self.aggregation == "voting":
            # 多數投票
            from collections import Counter
            votes = Counter(results)
            final_answer = votes.most_common(1)[0][0] if votes else ""
        elif self.aggregation == "first":
            final_answer = results[0] if results else ""
        else:
            final_answer = " | ".join(results)

        return dspy.Prediction(answer=final_answer, all_answers=results)


# ============================================================
# 9. 模型回退
# ============================================================

class FallbackPredictor(dspy.Module):
    """帶回退的預測器"""

    def __init__(self, primary_model: Any, fallback_models: List[Any]):
        super().__init__()
        self.primary_model = primary_model
        self.fallback_models = fallback_models
        self.predictor = dspy.Predict("question -> answer")

    def forward(self, question: str):
        models = [self.primary_model] + self.fallback_models

        for i, model in enumerate(models):
            dspy.settings.configure(lm=model)

            try:
                result = self.predictor(question=question)
                return dspy.Prediction(
                    answer=result.answer,
                    model_index=i,
                    model_name=str(model)
                )
            except Exception as e:
                print(f"模型 {i} 失敗: {e}")
                continue

        return dspy.Prediction(answer="所有模型都失敗了", model_index=-1)


# ============================================================
# 10. 成本優化路由
# ============================================================

class CostAwareRouter:
    """成本感知路由器"""

    def __init__(self, budget_limit: float = 1.0):
        self.budget_limit = budget_limit
        self.current_spend = 0.0
        self.model_costs = {
            "gpt-4": 0.03,
            "gpt-4-turbo": 0.01,
            "gpt-3.5-turbo": 0.001,
            "claude-3-opus": 0.015,
            "claude-3-sonnet": 0.003,
            "claude-3-haiku": 0.00025,
            "local": 0.0
        }

    def can_afford(self, model: str, estimated_tokens: int = 1000) -> bool:
        """檢查是否負擔得起"""
        cost = self.model_costs.get(model, 0.01) * (estimated_tokens / 1000)
        return self.current_spend + cost <= self.budget_limit

    def select_model(self, quality_required: str = "medium") -> str:
        """選擇成本效益最佳的模型"""
        if quality_required == "high":
            models = ["gpt-4", "claude-3-opus", "gpt-4-turbo", "claude-3-sonnet"]
        elif quality_required == "medium":
            models = ["gpt-3.5-turbo", "claude-3-sonnet", "claude-3-haiku"]
        else:
            models = ["claude-3-haiku", "gpt-3.5-turbo", "local"]

        for model in models:
            if self.can_afford(model):
                return model

        return "local"  # 最後使用本地模型

    def record_usage(self, model: str, tokens: int):
        """記錄使用"""
        cost = self.model_costs.get(model, 0.01) * (tokens / 1000)
        self.current_spend += cost


# ============================================================
# 使用範例
# ============================================================

def example_openai():
    """範例 1: OpenAI 配置"""
    print("=" * 50)
    print("範例 1: OpenAI 模型配置")
    print("=" * 50)
    print(OPENAI_CONFIG)


def example_claude():
    """範例 2: Claude 配置"""
    print("\n" + "=" * 50)
    print("範例 2: Anthropic Claude 配置")
    print("=" * 50)
    print(CLAUDE_CONFIG)


def example_local():
    """範例 3: 本地模型"""
    print("\n" + "=" * 50)
    print("範例 3: 本地模型配置")
    print("=" * 50)
    print("Ollama 配置:")
    print(OLLAMA_CONFIG)
    print("\nvLLM 配置:")
    print(VLLM_CONFIG)


def example_model_manager():
    """範例 4: 模型管理器"""
    print("\n" + "=" * 50)
    print("範例 4: 模型管理器")
    print("=" * 50)

    manager = ModelManager()
    print("""
使用示例:
    # 註冊模型
    manager.register_model("gpt35", gpt35, set_default=True)
    manager.register_model("gpt4", gpt4)
    manager.register_model("claude", claude)

    # 列出模型
    print(manager.list_models())  # ['gpt35', 'gpt4', 'claude']

    # 切換模型
    manager.switch_model("gpt4")

    # 使用模型
    model = manager.get_model("claude")
""")


def example_router():
    """範例 5: 模型路由器"""
    print("\n" + "=" * 50)
    print("範例 5: 智能路由器")
    print("=" * 50)

    router = ModelRouter()

    # 模擬路由
    tasks = [
        ("code", "high", "normal"),
        ("chat", "medium", "low"),
        ("analysis", "high", "high"),
        ("simple", "low", "low")
    ]

    for task_type, complexity, budget in tasks:
        model = router.route(task_type, complexity, budget)
        print(f"任務: {task_type}, 複雜度: {complexity}, 預算: {budget} -> 模型: {model}")


def example_ensemble():
    """範例 6: 模型集成"""
    print("\n" + "=" * 50)
    print("範例 6: 模型集成")
    print("=" * 50)

    print("""
集成預測器使用:
    # 創建集成預測器
    ensemble = EnsemblePredictor(
        models=[gpt35, gpt4, claude],
        aggregation="voting"  # 或 "first", "concat"
    )

    # 預測
    result = ensemble(question="什麼是人工智能？")
    print(f"最終答案: {result.answer}")
    print(f"所有答案: {result.all_answers}")
""")


def example_cost_routing():
    """範例 7: 成本優化"""
    print("\n" + "=" * 50)
    print("範例 7: 成本優化路由")
    print("=" * 50)

    router = CostAwareRouter(budget_limit=0.1)

    qualities = ["high", "medium", "low"]
    for quality in qualities:
        model = router.select_model(quality)
        print(f"質量要求: {quality} -> 選擇模型: {model}")

    # 記錄使用
    router.record_usage("gpt-3.5-turbo", 1000)
    print(f"\n當前花費: ${router.current_spend:.4f}")
    print(f"預算限制: ${router.budget_limit:.2f}")


if __name__ == "__main__":
    print("DSPy 多模型支援範例\n")
    example_openai()
    example_claude()
    example_local()
    example_model_manager()
    example_router()
    example_ensemble()
    example_cost_routing()
