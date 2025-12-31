"""
Agent-S 自定義模型模組

此模組展示如何在 Agent-S 中使用自定義模型：
1. 模型配置 - 配置不同的 LLM 提供商
2. 模型切換 - 根據任務類型選擇合適的模型
3. 本地模型 - 使用本地部署的模型
4. 模型組合 - 結合多個模型的優勢

Agent-S 支持靈活的模型配置，包括 OpenAI、Anthropic、本地模型等。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from enum import Enum
from datetime import datetime
import time
import json


class ModelProvider(Enum):
    """模型提供商"""
    OPENAI = "OpenAI"
    ANTHROPIC = "Anthropic"
    GOOGLE = "Google"
    LOCAL = "本地模型"
    AZURE = "Azure OpenAI"
    HUGGINGFACE = "HuggingFace"


class ModelCapability(Enum):
    """模型能力"""
    TEXT_GENERATION = "文本生成"
    CODE_GENERATION = "代碼生成"
    VISION = "視覺理解"
    FUNCTION_CALLING = "函數調用"
    REASONING = "推理"
    LONG_CONTEXT = "長上下文"


@dataclass
class ModelConfig:
    """模型配置"""
    model_id: str
    provider: ModelProvider
    model_name: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    capabilities: List[ModelCapability] = field(default_factory=list)
    context_window: int = 4096
    max_tokens: int = 2048
    temperature: float = 0.7
    cost_per_1k_tokens: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self):
        return f"{self.provider.value}: {self.model_name}"


@dataclass
class ModelResponse:
    """模型響應"""
    content: str
    model_id: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency: float  # 秒
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def cost(self) -> float:
        """計算成本"""
        # 簡化的成本計算
        return (self.total_tokens / 1000) * 0.01

    def __str__(self):
        return f"Response ({self.total_tokens} tokens, {self.latency:.2f}s): {self.content[:100]}..."


class ModelRegistry:
    """
    模型註冊表

    管理可用的模型配置
    """

    def __init__(self):
        self.models: Dict[str, ModelConfig] = {}
        self._register_default_models()

    def _register_default_models(self):
        """註冊默認模型"""
        default_models = [
            # OpenAI 模型
            ModelConfig(
                model_id="gpt-4",
                provider=ModelProvider.OPENAI,
                model_name="gpt-4",
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CODE_GENERATION,
                    ModelCapability.REASONING,
                    ModelCapability.FUNCTION_CALLING
                ],
                context_window=8192,
                cost_per_1k_tokens=0.03
            ),
            ModelConfig(
                model_id="gpt-3.5-turbo",
                provider=ModelProvider.OPENAI,
                model_name="gpt-3.5-turbo",
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CODE_GENERATION,
                    ModelCapability.FUNCTION_CALLING
                ],
                context_window=4096,
                cost_per_1k_tokens=0.001
            ),

            # Anthropic 模型
            ModelConfig(
                model_id="claude-3-opus",
                provider=ModelProvider.ANTHROPIC,
                model_name="claude-3-opus-20240229",
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CODE_GENERATION,
                    ModelCapability.VISION,
                    ModelCapability.REASONING,
                    ModelCapability.LONG_CONTEXT
                ],
                context_window=200000,
                cost_per_1k_tokens=0.015
            ),
            ModelConfig(
                model_id="claude-3-sonnet",
                provider=ModelProvider.ANTHROPIC,
                model_name="claude-3-sonnet-20240229",
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CODE_GENERATION,
                    ModelCapability.VISION
                ],
                context_window=200000,
                cost_per_1k_tokens=0.003
            ),

            # 本地模型
            ModelConfig(
                model_id="llama-2-7b",
                provider=ModelProvider.LOCAL,
                model_name="llama-2-7b",
                api_base="http://localhost:11434",
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CODE_GENERATION
                ],
                context_window=4096,
                cost_per_1k_tokens=0.0  # 本地免費
            ),
        ]

        for model in default_models:
            self.register(model)

    def register(self, config: ModelConfig):
        """註冊模型"""
        self.models[config.model_id] = config
        print(f"註冊模型: {config}")

    def get(self, model_id: str) -> Optional[ModelConfig]:
        """獲取模型配置"""
        return self.models.get(model_id)

    def find_by_capability(self, capability: ModelCapability) -> List[ModelConfig]:
        """根據能力查找模型"""
        return [
            model for model in self.models.values()
            if capability in model.capabilities
        ]

    def list_all(self) -> List[ModelConfig]:
        """列出所有模型"""
        return list(self.models.values())


class ModelClient:
    """
    模型客戶端

    與各種 LLM 提供商交互
    """

    def __init__(self, config: ModelConfig):
        self.config = config

    def complete(self, prompt: str, **kwargs) -> ModelResponse:
        """
        生成文本補全

        Args:
            prompt: 輸入提示
            **kwargs: 額外參數

        Returns:
            模型響應
        """
        print(f"\n使用模型: {self.config}")
        print(f"提示長度: {len(prompt)} 字符")

        start_time = time.time()

        # 模擬 API 調用
        content = self._simulate_completion(prompt, **kwargs)

        latency = time.time() - start_time

        # 模擬 token 計數
        prompt_tokens = len(prompt) // 4
        completion_tokens = len(content) // 4

        response = ModelResponse(
            content=content,
            model_id=self.config.model_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            latency=latency
        )

        print(f"生成完成: {response.total_tokens} tokens, {response.latency:.2f}s")

        return response

    def _simulate_completion(self, prompt: str, **kwargs) -> str:
        """模擬文本生成"""
        time.sleep(0.3)  # 模擬 API 延遲

        # 根據提示生成簡單響應
        if "代碼" in prompt or "code" in prompt.lower():
            return "def example_function():\n    return 'Hello, World!'"
        elif "總結" in prompt or "summary" in prompt.lower():
            return "這是一個簡短的總結。"
        elif "翻譯" in prompt or "translate" in prompt.lower():
            return "This is the translated text."
        else:
            return f"這是使用 {self.config.model_name} 生成的響應。"


class ModelSelector:
    """
    模型選擇器

    根據任務特徵自動選擇最合適的模型
    """

    def __init__(self, registry: ModelRegistry):
        self.registry = registry
        self.selection_history: List[Dict[str, Any]] = []

    def select(self, task_description: str, required_capabilities: List[ModelCapability],
               budget: Optional[float] = None) -> ModelConfig:
        """
        選擇最佳模型

        Args:
            task_description: 任務描述
            required_capabilities: 所需能力
            budget: 預算限制（每1k tokens）

        Returns:
            選擇的模型配置
        """
        print(f"\n選擇模型...")
        print(f"任務: {task_description}")
        print(f"所需能力: {[c.value for c in required_capabilities]}")
        if budget:
            print(f"預算: ${budget}/1k tokens")

        # 過濾具備所需能力的模型
        candidates = []
        for model in self.registry.list_all():
            if all(cap in model.capabilities for cap in required_capabilities):
                # 檢查預算
                if budget is None or model.cost_per_1k_tokens <= budget:
                    candidates.append(model)

        if not candidates:
            raise ValueError("沒有找到符合條件的模型")

        # 評分並選擇最佳模型
        best_model = self._score_and_select(candidates, task_description)

        print(f"選擇: {best_model}")

        # 記錄選擇
        self.selection_history.append({
            "task": task_description,
            "model": best_model.model_id,
            "timestamp": datetime.now().isoformat()
        })

        return best_model

    def _score_and_select(self, candidates: List[ModelConfig], task: str) -> ModelConfig:
        """評分並選擇模型"""
        scores = []

        for model in candidates:
            score = 0.0

            # 上下文窗口越大越好
            score += model.context_window / 10000

            # 成本越低越好（反向）
            score += max(0, 1.0 - model.cost_per_1k_tokens)

            # 能力越多越好
            score += len(model.capabilities) * 0.1

            # 根據任務類型調整
            if "代碼" in task and ModelCapability.CODE_GENERATION in model.capabilities:
                score += 0.5
            if "推理" in task and ModelCapability.REASONING in model.capabilities:
                score += 0.5
            if "長文" in task and ModelCapability.LONG_CONTEXT in model.capabilities:
                score += 0.5

            scores.append((model, score))

        # 返回得分最高的
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[0][0]


class MultiModelAgent:
    """
    多模型代理

    可以使用多個模型協同工作
    """

    def __init__(self, registry: ModelRegistry):
        self.registry = registry
        self.selector = ModelSelector(registry)
        self.clients: Dict[str, ModelClient] = {}

    def execute_task(self, task: str, strategy: str = "auto") -> str:
        """
        執行任務

        Args:
            task: 任務描述
            strategy: 選擇策略（auto, fast, quality, cheap）

        Returns:
            執行結果
        """
        print("\n" + "="*60)
        print(f"執行任務: {task}")
        print(f"策略: {strategy}")
        print("="*60)

        # 根據策略選擇模型
        model = self._select_model_by_strategy(task, strategy)

        # 獲取或創建客戶端
        client = self._get_client(model)

        # 執行任務
        response = client.complete(task)

        print(f"\n結果: {response.content}")
        print(f"成本: ${response.cost:.4f}")

        return response.content

    def _select_model_by_strategy(self, task: str, strategy: str) -> ModelConfig:
        """根據策略選擇模型"""
        if strategy == "fast":
            # 選擇最快（最小）的模型
            return self.registry.get("gpt-3.5-turbo")

        elif strategy == "quality":
            # 選擇質量最好的模型
            return self.registry.get("gpt-4") or self.registry.get("claude-3-opus")

        elif strategy == "cheap":
            # 選擇最便宜的模型
            models = self.registry.list_all()
            models.sort(key=lambda m: m.cost_per_1k_tokens)
            return models[0]

        else:  # auto
            # 自動選擇
            capabilities = [ModelCapability.TEXT_GENERATION]
            return self.selector.select(task, capabilities)

    def _get_client(self, config: ModelConfig) -> ModelClient:
        """獲取或創建模型客戶端"""
        if config.model_id not in self.clients:
            self.clients[config.model_id] = ModelClient(config)
        return self.clients[config.model_id]

    def ensemble_generate(self, prompt: str, model_ids: List[str]) -> str:
        """
        集成生成

        使用多個模型生成並選擇最佳結果
        """
        print("\n" + "="*60)
        print(f"集成生成（使用 {len(model_ids)} 個模型）")
        print("="*60)

        responses = []

        for model_id in model_ids:
            config = self.registry.get(model_id)
            if not config:
                print(f"跳過未知模型: {model_id}")
                continue

            client = self._get_client(config)
            response = client.complete(prompt)
            responses.append(response)

            print(f"\n{config.model_name}: {response.content[:100]}...")

        # 選擇最佳響應（這裡簡單選擇最長的）
        best = max(responses, key=lambda r: len(r.content))

        print(f"\n選擇最佳響應來自: {best.model_id}")
        return best.content


def 示例1_模型註冊():
    """示例：註冊和管理模型"""
    print("\n" + "="*60)
    print("示例 1: 模型註冊")
    print("="*60)

    registry = ModelRegistry()

    # 列出所有模型
    print("\n可用模型:")
    for i, model in enumerate(registry.list_all(), 1):
        print(f"{i}. {model}")
        print(f"   能力: {[c.value for c in model.capabilities]}")
        print(f"   成本: ${model.cost_per_1k_tokens}/1k tokens")

    # 按能力查找
    print("\n具有代碼生成能力的模型:")
    code_models = registry.find_by_capability(ModelCapability.CODE_GENERATION)
    for model in code_models:
        print(f"  - {model}")

    return registry


def 示例2_模型選擇():
    """示例：自動選擇模型"""
    print("\n" + "="*60)
    print("示例 2: 自動模型選擇")
    print("="*60)

    registry = ModelRegistry()
    selector = ModelSelector(registry)

    # 場景1：代碼生成任務
    model1 = selector.select(
        "生成 Python 函數來處理 CSV 文件",
        [ModelCapability.CODE_GENERATION],
        budget=0.01
    )

    # 場景2：長文檔總結
    model2 = selector.select(
        "總結一篇 10000 字的長文檔",
        [ModelCapability.TEXT_GENERATION, ModelCapability.LONG_CONTEXT]
    )

    # 場景3：複雜推理任務
    model3 = selector.select(
        "解決複雜的數學推理問題",
        [ModelCapability.REASONING]
    )

    return selector


def 示例3_使用模型():
    """示例：使用模型生成內容"""
    print("\n" + "="*60)
    print("示例 3: 使用模型")
    print("="*60)

    registry = ModelRegistry()

    # 使用 GPT-3.5
    config = registry.get("gpt-3.5-turbo")
    client = ModelClient(config)

    # 生成文本
    response = client.complete("寫一個關於人工智能的簡短段落")
    print(f"\n生成內容:\n{response.content}")
    print(f"\n統計:")
    print(f"  Tokens: {response.total_tokens}")
    print(f"  延遲: {response.latency:.2f}s")
    print(f"  成本: ${response.cost:.4f}")

    return response


def 示例4_多模型協同():
    """示例：多模型代理"""
    print("\n" + "="*60)
    print("示例 4: 多模型代理")
    print("="*60)

    registry = ModelRegistry()
    agent = MultiModelAgent(registry)

    # 使用不同策略執行任務
    tasks = [
        ("快速回答：什麼是 Python？", "fast"),
        ("詳細解釋機器學習的概念", "quality"),
        ("總結今天的天氣", "cheap"),
    ]

    for task, strategy in tasks:
        print("\n" + "-"*60)
        agent.execute_task(task, strategy)

    return agent


def 示例5_集成生成():
    """示例：使用多個模型集成生成"""
    print("\n" + "="*60)
    print("示例 5: 集成生成")
    print("="*60)

    registry = ModelRegistry()
    agent = MultiModelAgent(registry)

    # 使用多個模型生成
    prompt = "解釋什麼是 Agent-S 框架"
    model_ids = ["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet"]

    result = agent.ensemble_generate(prompt, model_ids)

    print(f"\n最終結果:\n{result}")

    return result


if __name__ == "__main__":
    print("Agent-S 自定義模型演示\n")

    示例1_模型註冊()
    示例2_模型選擇()
    示例3_使用模型()
    示例4_多模型協同()
    示例5_集成生成()

    print("\n所有示例執行完成！")
