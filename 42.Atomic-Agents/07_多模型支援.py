"""
Atomic Agents 多模型支援
========================

本文件展示如何支援多個 LLM 提供商和模型。
靈活的模型支援對於生產環境至關重要。

主要內容：
1. 統一的模型接口
2. OpenAI 集成
3. Anthropic 集成
4. 本地模型支援
5. 模型選擇策略
6. 模型切換和負載均衡

作者：Atomic Agents 團隊
日期：2025-12-31
"""

from typing import Any, Dict, List, Optional, Union, AsyncIterator
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
import os


# ============================================================================
# 第一部分：統一模型接口
# ============================================================================

class ModelProvider(str, Enum):
    """模型提供商"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    AZURE = "azure"


class ModelCapability(str, Enum):
    """模型能力"""
    TEXT_GENERATION = "text_generation"
    CHAT = "chat"
    EMBEDDING = "embedding"
    FUNCTION_CALLING = "function_calling"
    VISION = "vision"
    STREAMING = "streaming"


class ModelConfig(BaseModel):
    """模型配置"""
    provider: ModelProvider = Field(..., description="提供商")
    model_name: str = Field(..., description="模型名稱")
    api_key: Optional[str] = Field(None, description="API 密鑰")
    api_base: Optional[str] = Field(None, description="API 基礎 URL")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, ge=1)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    timeout: int = Field(default=60, description="超時時間（秒）")
    capabilities: List[ModelCapability] = Field(
        default_factory=list,
        description="模型能力"
    )


class Message(BaseModel):
    """消息模型"""
    role: str = Field(..., description="角色")
    content: str = Field(..., description="內容")


class CompletionRequest(BaseModel):
    """完成請求"""
    messages: List[Message] = Field(..., description="消息列表")
    temperature: Optional[float] = Field(None)
    max_tokens: Optional[int] = Field(None)
    stream: bool = Field(default=False)
    additional_params: Dict[str, Any] = Field(default_factory=dict)


class CompletionResponse(BaseModel):
    """完成響應"""
    content: str = Field(..., description="生成的內容")
    model: str = Field(..., description="使用的模型")
    usage: Dict[str, int] = Field(default_factory=dict)
    finish_reason: Optional[str] = Field(None)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseModelClient(ABC):
    """
    基礎模型客戶端

    所有模型客戶端的抽象基類。
    """

    def __init__(self, config: ModelConfig):
        self.config = config

    @abstractmethod
    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """
        生成完成

        Args:
            request: 完成請求

        Returns:
            完成響應
        """
        pass

    @abstractmethod
    def stream_complete(
        self,
        request: CompletionRequest
    ) -> AsyncIterator[str]:
        """
        流式生成

        Args:
            request: 完成請求

        Yields:
            生成的文本塊
        """
        pass

    def get_capabilities(self) -> List[ModelCapability]:
        """獲取模型能力"""
        return self.config.capabilities


# ============================================================================
# 第二部分：OpenAI 客戶端
# ============================================================================

class OpenAIClient(BaseModelClient):
    """
    OpenAI 客戶端

    與 OpenAI API 集成。
    """

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        # 在實際使用中，這裡會初始化 OpenAI 客戶端
        # from openai import OpenAI
        # self.client = OpenAI(api_key=config.api_key)

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """生成完成"""
        print(f"\n[OpenAI] 調用模型: {self.config.model_name}")
        print(f"消息數: {len(request.messages)}")

        # 模擬 API 調用
        # 實際代碼：
        # response = self.client.chat.completions.create(
        #     model=self.config.model_name,
        #     messages=[{"role": m.role, "content": m.content} for m in request.messages],
        #     temperature=request.temperature or self.config.temperature,
        #     max_tokens=request.max_tokens or self.config.max_tokens
        # )

        # 模擬響應
        content = f"[OpenAI {self.config.model_name}] 這是一個模擬響應。"

        return CompletionResponse(
            content=content,
            model=self.config.model_name,
            usage={
                'prompt_tokens': 50,
                'completion_tokens': 20,
                'total_tokens': 70
            },
            finish_reason='stop'
        )

    def stream_complete(self, request: CompletionRequest) -> AsyncIterator[str]:
        """流式生成（模擬）"""
        # 實際實現會使用異步生成器
        chunks = ["這是", "流式", "響應", "的", "示例"]
        for chunk in chunks:
            yield chunk


# ============================================================================
# 第三部分：Anthropic 客戶端
# ============================================================================

class AnthropicClient(BaseModelClient):
    """
    Anthropic 客戶端

    與 Anthropic Claude API 集成。
    """

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        # 在實際使用中，這裡會初始化 Anthropic 客戶端
        # from anthropic import Anthropic
        # self.client = Anthropic(api_key=config.api_key)

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """生成完成"""
        print(f"\n[Anthropic] 調用模型: {self.config.model_name}")
        print(f"消息數: {len(request.messages)}")

        # 轉換消息格式
        system_message = None
        messages = []

        for msg in request.messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                messages.append({"role": msg.role, "content": msg.content})

        # 模擬 API 調用
        # 實際代碼：
        # response = self.client.messages.create(
        #     model=self.config.model_name,
        #     system=system_message,
        #     messages=messages,
        #     max_tokens=request.max_tokens or self.config.max_tokens,
        #     temperature=request.temperature or self.config.temperature
        # )

        # 模擬響應
        content = f"[Anthropic {self.config.model_name}] 這是一個模擬響應。"

        return CompletionResponse(
            content=content,
            model=self.config.model_name,
            usage={
                'input_tokens': 45,
                'output_tokens': 25
            },
            finish_reason='end_turn'
        )

    def stream_complete(self, request: CompletionRequest) -> AsyncIterator[str]:
        """流式生成（模擬）"""
        chunks = ["Claude", "流式", "響應", "示例"]
        for chunk in chunks:
            yield chunk


# ============================================================================
# 第四部分：本地模型客戶端
# ============================================================================

class LocalModelClient(BaseModelClient):
    """
    本地模型客戶端

    支援本地運行的模型（如 llama.cpp, Ollama 等）。
    """

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        # 初始化本地模型
        # 這裡可以使用 llama-cpp-python, transformers 等

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """生成完成"""
        print(f"\n[本地模型] 調用: {self.config.model_name}")
        print(f"消息數: {len(request.messages)}")

        # 構建提示詞
        prompt = self._build_prompt(request.messages)

        # 模擬本地推理
        # 實際代碼會調用本地模型
        content = f"[本地 {self.config.model_name}] 這是一個模擬響應。"

        return CompletionResponse(
            content=content,
            model=self.config.model_name,
            usage={
                'prompt_tokens': 40,
                'completion_tokens': 30,
                'total_tokens': 70
            },
            finish_reason='stop',
            metadata={'inference_time': 1.2}
        )

    def _build_prompt(self, messages: List[Message]) -> str:
        """構建提示詞"""
        prompt_parts = []
        for msg in messages:
            prompt_parts.append(f"{msg.role.upper()}: {msg.content}")
        return "\n".join(prompt_parts)

    def stream_complete(self, request: CompletionRequest) -> AsyncIterator[str]:
        """流式生成（模擬）"""
        chunks = ["本地", "模型", "流式", "輸出"]
        for chunk in chunks:
            yield chunk


# ============================================================================
# 第五部分：模型工廠
# ============================================================================

class ModelFactory:
    """
    模型工廠

    根據配置創建適當的模型客戶端。
    """

    @staticmethod
    def create_client(config: ModelConfig) -> BaseModelClient:
        """
        創建模型客戶端

        Args:
            config: 模型配置

        Returns:
            模型客戶端實例
        """
        if config.provider == ModelProvider.OPENAI:
            return OpenAIClient(config)
        elif config.provider == ModelProvider.ANTHROPIC:
            return AnthropicClient(config)
        elif config.provider == ModelProvider.LOCAL:
            return LocalModelClient(config)
        else:
            raise ValueError(f"不支持的提供商: {config.provider}")

    @staticmethod
    def create_from_name(
        provider: str,
        model_name: str,
        **kwargs
    ) -> BaseModelClient:
        """
        從名稱創建客戶端

        Args:
            provider: 提供商名稱
            model_name: 模型名稱
            **kwargs: 額外配置

        Returns:
            模型客戶端
        """
        config = ModelConfig(
            provider=ModelProvider(provider),
            model_name=model_name,
            **kwargs
        )
        return ModelFactory.create_client(config)


# ============================================================================
# 第六部分：模型選擇策略
# ============================================================================

class SelectionStrategy(str, Enum):
    """選擇策略"""
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    LEAST_LOADED = "least_loaded"
    COST_OPTIMIZED = "cost_optimized"
    PERFORMANCE = "performance"


class ModelSelector:
    """
    模型選擇器

    根據策略選擇最適合的模型。
    """

    def __init__(self, strategy: SelectionStrategy = SelectionStrategy.ROUND_ROBIN):
        self.strategy = strategy
        self.models: List[BaseModelClient] = []
        self.current_index = 0
        self.usage_stats: Dict[str, int] = {}

    def add_model(self, client: BaseModelClient) -> None:
        """添加模型"""
        self.models.append(client)
        self.usage_stats[client.config.model_name] = 0

    def select_model(
        self,
        requirements: Optional[List[ModelCapability]] = None
    ) -> BaseModelClient:
        """
        選擇模型

        Args:
            requirements: 能力要求

        Returns:
            選中的模型客戶端
        """
        # 過濾符合要求的模型
        candidates = self.models

        if requirements:
            candidates = [
                model for model in self.models
                if all(cap in model.get_capabilities() for cap in requirements)
            ]

        if not candidates:
            raise ValueError("沒有符合要求的模型")

        # 根據策略選擇
        if self.strategy == SelectionStrategy.ROUND_ROBIN:
            selected = self._round_robin(candidates)
        elif self.strategy == SelectionStrategy.LEAST_LOADED:
            selected = self._least_loaded(candidates)
        else:
            selected = candidates[0]

        # 更新統計
        self.usage_stats[selected.config.model_name] += 1

        return selected

    def _round_robin(self, candidates: List[BaseModelClient]) -> BaseModelClient:
        """輪詢策略"""
        selected = candidates[self.current_index % len(candidates)]
        self.current_index += 1
        return selected

    def _least_loaded(self, candidates: List[BaseModelClient]) -> BaseModelClient:
        """最少負載策略"""
        return min(
            candidates,
            key=lambda m: self.usage_stats.get(m.config.model_name, 0)
        )

    def get_stats(self) -> Dict[str, Any]:
        """獲取使用統計"""
        return {
            'total_requests': sum(self.usage_stats.values()),
            'usage_by_model': self.usage_stats.copy()
        }


# ============================================================================
# 第七部分：模型路由器
# ============================================================================

class ModelRouter:
    """
    模型路由器

    智能路由請求到不同的模型。
    """

    def __init__(self):
        self.routes: Dict[str, BaseModelClient] = {}
        self.default_client: Optional[BaseModelClient] = None

    def add_route(self, route_name: str, client: BaseModelClient) -> None:
        """添加路由"""
        self.routes[route_name] = client

    def set_default(self, client: BaseModelClient) -> None:
        """設置默認客戶端"""
        self.default_client = client

    def route(
        self,
        request: CompletionRequest,
        route_name: Optional[str] = None
    ) -> CompletionResponse:
        """
        路由請求

        Args:
            request: 完成請求
            route_name: 路由名稱

        Returns:
            完成響應
        """
        # 自動選擇路由
        if not route_name:
            route_name = self._auto_route(request)

        # 獲取客戶端
        client = self.routes.get(route_name, self.default_client)

        if not client:
            raise ValueError(f"找不到路由: {route_name}")

        # 執行請求
        return client.complete(request)

    def _auto_route(self, request: CompletionRequest) -> str:
        """
        自動選擇路由

        Args:
            request: 完成請求

        Returns:
            路由名稱
        """
        # 簡單的啟發式規則
        message_count = len(request.messages)
        total_length = sum(len(m.content) for m in request.messages)

        # 短對話使用快速模型
        if message_count <= 3 and total_length < 500:
            return "fast"

        # 長對話使用高級模型
        if message_count > 10 or total_length > 2000:
            return "advanced"

        return "default"


# ============================================================================
# 第八部分：使用示例
# ============================================================================

def example_model_clients():
    """模型客戶端示例"""
    print("\n" + "="*60)
    print("示例 1: 不同的模型客戶端")
    print("="*60)

    # OpenAI 客戶端
    openai_config = ModelConfig(
        provider=ModelProvider.OPENAI,
        model_name="gpt-4",
        temperature=0.7,
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STREAMING
        ]
    )
    openai_client = OpenAIClient(openai_config)

    # Anthropic 客戶端
    anthropic_config = ModelConfig(
        provider=ModelProvider.ANTHROPIC,
        model_name="claude-3-opus",
        temperature=0.7,
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.VISION,
            ModelCapability.STREAMING
        ]
    )
    anthropic_client = AnthropicClient(anthropic_config)

    # 測試請求
    request = CompletionRequest(
        messages=[
            Message(role="system", content="你是一個助手。"),
            Message(role="user", content="你好！")
        ]
    )

    # 調用不同的模型
    openai_response = openai_client.complete(request)
    print(f"\nOpenAI 響應: {openai_response.content}")

    anthropic_response = anthropic_client.complete(request)
    print(f"Anthropic 響應: {anthropic_response.content}")


def example_model_factory():
    """模型工廠示例"""
    print("\n" + "="*60)
    print("示例 2: 模型工廠")
    print("="*60)

    # 使用工廠創建客戶端
    client = ModelFactory.create_from_name(
        provider="openai",
        model_name="gpt-3.5-turbo",
        temperature=0.5
    )

    request = CompletionRequest(
        messages=[Message(role="user", content="測試消息")]
    )

    response = client.complete(request)
    print(f"\n響應: {response.content}")
    print(f"使用情況: {response.usage}")


def example_model_selector():
    """模型選擇器示例"""
    print("\n" + "="*60)
    print("示例 3: 模型選擇器")
    print("="*60)

    # 創建選擇器
    selector = ModelSelector(strategy=SelectionStrategy.ROUND_ROBIN)

    # 添加多個模型
    selector.add_model(ModelFactory.create_from_name("openai", "gpt-4"))
    selector.add_model(ModelFactory.create_from_name("openai", "gpt-3.5-turbo"))
    selector.add_model(ModelFactory.create_from_name("anthropic", "claude-3-opus"))

    # 測試請求
    request = CompletionRequest(
        messages=[Message(role="user", content="測試")]
    )

    # 進行多次請求，觀察輪詢
    for i in range(5):
        model = selector.select_model()
        print(f"\n請求 {i+1}: 使用 {model.config.model_name}")
        response = model.complete(request)

    # 查看統計
    stats = selector.get_stats()
    print(f"\n使用統計: {stats}")


def example_model_router():
    """模型路由器示例"""
    print("\n" + "="*60)
    print("示例 4: 模型路由器")
    print("="*60)

    # 創建路由器
    router = ModelRouter()

    # 添加路由
    router.add_route("fast", ModelFactory.create_from_name("openai", "gpt-3.5-turbo"))
    router.add_route("advanced", ModelFactory.create_from_name("openai", "gpt-4"))
    router.add_route("default", ModelFactory.create_from_name("anthropic", "claude-3-sonnet"))

    router.set_default(router.routes["default"])

    # 測試不同的請求
    requests = [
        CompletionRequest(messages=[Message(role="user", content="Hi")]),
        CompletionRequest(messages=[
            Message(role="user", content="這是一個很長的問題..." * 20)
        ]),
    ]

    for req in requests:
        response = router.route(req)
        print(f"\n使用模型: {response.model}")
        print(f"響應: {response.content[:50]}...")


def example_streaming():
    """流式輸出示例"""
    print("\n" + "="*60)
    print("示例 5: 流式輸出")
    print("="*60)

    client = ModelFactory.create_from_name("openai", "gpt-4")

    request = CompletionRequest(
        messages=[Message(role="user", content="講個故事")],
        stream=True
    )

    print("\n開始流式輸出:")
    for chunk in client.stream_complete(request):
        print(chunk, end=" ", flush=True)
    print()


def example_capability_matching():
    """能力匹配示例"""
    print("\n" + "="*60)
    print("示例 6: 能力匹配")
    print("="*60)

    selector = ModelSelector()

    # 添加具有不同能力的模型
    config1 = ModelConfig(
        provider=ModelProvider.OPENAI,
        model_name="gpt-4-vision",
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING
        ]
    )
    selector.add_model(OpenAIClient(config1))

    config2 = ModelConfig(
        provider=ModelProvider.OPENAI,
        model_name="gpt-3.5-turbo",
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.FUNCTION_CALLING
        ]
    )
    selector.add_model(OpenAIClient(config2))

    # 選擇具有視覺能力的模型
    model = selector.select_model(requirements=[ModelCapability.VISION])
    print(f"\n選擇的模型: {model.config.model_name}")
    print(f"模型能力: {model.get_capabilities()}")


def main():
    """主函數"""
    print("\n" + "="*60)
    print("Atomic Agents 多模型支援")
    print("="*60)

    # 運行示例
    example_model_clients()
    example_model_factory()
    example_model_selector()
    example_model_router()
    example_streaming()
    example_capability_matching()

    print("\n" + "="*60)
    print("所有示例運行完成！")
    print("="*60)


if __name__ == "__main__":
    main()
