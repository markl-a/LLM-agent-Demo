"""
Continue AI 編程助手 - 模型配置管理

這個文件展示了如何配置和管理不同的 AI 模型。
支持 OpenAI、Anthropic、本地模型等多種模型提供商。

主要內容:
1. 模型提供商配置
2. 模型參數設置
3. 多模型管理
4. 模型切換策略
5. 成本管理
6. 性能優化
7. 自定義模型集成

Author: Continue Team
Date: 2025
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
import os
from datetime import datetime


# =====================================================
# 第一部分: 模型類型和配置定義
# =====================================================

class ModelProvider(Enum):
    """
    模型提供商
    """
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    AZURE_OPENAI = "azure-openai"
    GOOGLE = "google"
    CUSTOM = "custom"


class ModelCapability(Enum):
    """
    模型能力
    """
    CHAT = "chat"  # 聊天
    COMPLETION = "completion"  # 補全
    EMBEDDING = "embedding"  # 嵌入
    CODE_GENERATION = "code_generation"  # 代碼生成
    CODE_REVIEW = "code_review"  # 代碼審查
    REFACTORING = "refactoring"  # 重構
    DEBUGGING = "debugging"  # 調試


@dataclass
class ModelParameters:
    """
    模型參數配置
    """
    temperature: float = 0.7  # 溫度(0-2)
    max_tokens: int = 2000  # 最大生成 token 數
    top_p: float = 1.0  # 核採樣參數
    frequency_penalty: float = 0.0  # 頻率懲罰
    presence_penalty: float = 0.0  # 存在懲罰
    stop_sequences: List[str] = field(default_factory=list)  # 停止序列

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "stop": self.stop_sequences
        }


@dataclass
class ModelCost:
    """
    模型成本配置
    """
    input_cost_per_1k: float  # 每 1K 輸入 token 成本(美元)
    output_cost_per_1k: float  # 每 1K 輸出 token 成本(美元)
    currency: str = "USD"  # 貨幣單位

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        計算成本

        Args:
            input_tokens: 輸入 token 數
            output_tokens: 輸出 token 數

        Returns:
            總成本
        """
        input_cost = (input_tokens / 1000) * self.input_cost_per_1k
        output_cost = (output_tokens / 1000) * self.output_cost_per_1k
        return input_cost + output_cost


# =====================================================
# 第二部分: 模型配置基類
# =====================================================

class ModelConfig(ABC):
    """
    模型配置抽象基類
    """

    def __init__(
        self,
        name: str,
        provider: ModelProvider,
        model_id: str,
        api_key: Optional[str] = None,
        capabilities: Optional[List[ModelCapability]] = None
    ):
        """
        初始化模型配置

        Args:
            name: 模型顯示名稱
            provider: 提供商
            model_id: 模型 ID
            api_key: API 密鑰
            capabilities: 模型能力列表
        """
        self.name = name
        self.provider = provider
        self.model_id = model_id
        self.api_key = api_key or os.getenv(f"{provider.value.upper()}_API_KEY")
        self.capabilities = capabilities or []
        self.parameters = ModelParameters()
        self.cost: Optional[ModelCost] = None
        self.enabled = True

    @abstractmethod
    def validate_config(self) -> bool:
        """
        驗證配置

        Returns:
            配置是否有效
        """
        pass

    @abstractmethod
    def get_api_endpoint(self) -> str:
        """
        獲取 API 端點

        Returns:
            API 端點 URL
        """
        pass

    def has_capability(self, capability: ModelCapability) -> bool:
        """
        檢查是否具備某種能力

        Args:
            capability: 能力類型

        Returns:
            是否具備
        """
        return capability in self.capabilities

    def set_parameters(self, **kwargs):
        """
        設置模型參數

        Args:
            **kwargs: 參數鍵值對
        """
        for key, value in kwargs.items():
            if hasattr(self.parameters, key):
                setattr(self.parameters, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """
        轉換為字典格式

        Returns:
            配置字典
        """
        return {
            "name": self.name,
            "provider": self.provider.value,
            "model": self.model_id,
            "apiKey": self.api_key,
            "capabilities": [c.value for c in self.capabilities],
            "parameters": self.parameters.to_dict(),
            "enabled": self.enabled
        }


# =====================================================
# 第三部分: OpenAI 模型配置
# =====================================================

class OpenAIModelConfig(ModelConfig):
    """
    OpenAI 模型配置
    """

    # OpenAI 模型列表
    MODELS = {
        "gpt-4-turbo": {
            "input_cost": 0.01,
            "output_cost": 0.03,
            "max_tokens": 128000
        },
        "gpt-4": {
            "input_cost": 0.03,
            "output_cost": 0.06,
            "max_tokens": 8192
        },
        "gpt-3.5-turbo": {
            "input_cost": 0.0005,
            "output_cost": 0.0015,
            "max_tokens": 16385
        }
    }

    def __init__(self, model_id: str = "gpt-4-turbo", api_key: Optional[str] = None):
        """
        初始化 OpenAI 模型配置

        Args:
            model_id: 模型 ID
            api_key: API 密鑰
        """
        super().__init__(
            name=f"OpenAI {model_id}",
            provider=ModelProvider.OPENAI,
            model_id=model_id,
            api_key=api_key,
            capabilities=[
                ModelCapability.CHAT,
                ModelCapability.COMPLETION,
                ModelCapability.CODE_GENERATION,
                ModelCapability.CODE_REVIEW
            ]
        )

        # 設置成本
        if model_id in self.MODELS:
            model_info = self.MODELS[model_id]
            self.cost = ModelCost(
                input_cost_per_1k=model_info["input_cost"],
                output_cost_per_1k=model_info["output_cost"]
            )

    def validate_config(self) -> bool:
        """驗證配置"""
        if not self.api_key:
            print("錯誤: 未設置 OpenAI API 密鑰")
            return False

        if not self.api_key.startswith("sk-"):
            print("警告: OpenAI API 密鑰格式可能不正確")
            return False

        if self.model_id not in self.MODELS:
            print(f"警告: 未知的 OpenAI 模型 {self.model_id}")

        return True

    def get_api_endpoint(self) -> str:
        """獲取 API 端點"""
        return "https://api.openai.com/v1/chat/completions"


class AzureOpenAIModelConfig(ModelConfig):
    """
    Azure OpenAI 模型配置
    """

    def __init__(
        self,
        deployment_name: str,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        api_version: str = "2024-02-01"
    ):
        """
        初始化 Azure OpenAI 配置

        Args:
            deployment_name: 部署名稱
            api_key: API 密鑰
            endpoint: Azure 端點
            api_version: API 版本
        """
        super().__init__(
            name=f"Azure OpenAI {deployment_name}",
            provider=ModelProvider.AZURE_OPENAI,
            model_id=deployment_name,
            api_key=api_key,
            capabilities=[
                ModelCapability.CHAT,
                ModelCapability.CODE_GENERATION
            ]
        )

        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = api_version

    def validate_config(self) -> bool:
        """驗證配置"""
        if not self.api_key:
            print("錯誤: 未設置 Azure OpenAI API 密鑰")
            return False

        if not self.endpoint:
            print("錯誤: 未設置 Azure OpenAI 端點")
            return False

        return True

    def get_api_endpoint(self) -> str:
        """獲取 API 端點"""
        return f"{self.endpoint}/openai/deployments/{self.model_id}/chat/completions?api-version={self.api_version}"


# =====================================================
# 第四部分: Anthropic 模型配置
# =====================================================

class AnthropicModelConfig(ModelConfig):
    """
    Anthropic Claude 模型配置
    """

    # Anthropic 模型列表
    MODELS = {
        "claude-3-opus-20240229": {
            "input_cost": 0.015,
            "output_cost": 0.075,
            "max_tokens": 200000
        },
        "claude-3-sonnet-20240229": {
            "input_cost": 0.003,
            "output_cost": 0.015,
            "max_tokens": 200000
        },
        "claude-3-haiku-20240307": {
            "input_cost": 0.00025,
            "output_cost": 0.00125,
            "max_tokens": 200000
        }
    }

    def __init__(self, model_id: str = "claude-3-opus-20240229", api_key: Optional[str] = None):
        """
        初始化 Anthropic 模型配置

        Args:
            model_id: 模型 ID
            api_key: API 密鑰
        """
        super().__init__(
            name=f"Claude {model_id.split('-')[2].title()}",
            provider=ModelProvider.ANTHROPIC,
            model_id=model_id,
            api_key=api_key,
            capabilities=[
                ModelCapability.CHAT,
                ModelCapability.CODE_GENERATION,
                ModelCapability.CODE_REVIEW,
                ModelCapability.REFACTORING
            ]
        )

        # 設置成本
        if model_id in self.MODELS:
            model_info = self.MODELS[model_id]
            self.cost = ModelCost(
                input_cost_per_1k=model_info["input_cost"],
                output_cost_per_1k=model_info["output_cost"]
            )

    def validate_config(self) -> bool:
        """驗證配置"""
        if not self.api_key:
            print("錯誤: 未設置 Anthropic API 密鑰")
            return False

        if not self.api_key.startswith("sk-ant-"):
            print("警告: Anthropic API 密鑰格式可能不正確")

        return True

    def get_api_endpoint(self) -> str:
        """獲取 API 端點"""
        return "https://api.anthropic.com/v1/messages"


# =====================================================
# 第五部分: 本地模型配置
# =====================================================

class OllamaModelConfig(ModelConfig):
    """
    Ollama 本地模型配置
    """

    def __init__(
        self,
        model_id: str = "llama2",
        base_url: str = "http://localhost:11434"
    ):
        """
        初始化 Ollama 模型配置

        Args:
            model_id: 模型 ID
            base_url: Ollama 服務地址
        """
        super().__init__(
            name=f"Ollama {model_id}",
            provider=ModelProvider.OLLAMA,
            model_id=model_id,
            api_key=None,  # Ollama 不需要 API 密鑰
            capabilities=[
                ModelCapability.CHAT,
                ModelCapability.CODE_GENERATION
            ]
        )

        self.base_url = base_url

        # 本地模型無成本
        self.cost = ModelCost(
            input_cost_per_1k=0.0,
            output_cost_per_1k=0.0
        )

    def validate_config(self) -> bool:
        """驗證配置"""
        # 可以嘗試連接 Ollama 服務
        import requests
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                return True
            else:
                print(f"警告: Ollama 服務響應異常: {response.status_code}")
                return False
        except Exception as e:
            print(f"錯誤: 無法連接到 Ollama 服務: {e}")
            return False

    def get_api_endpoint(self) -> str:
        """獲取 API 端點"""
        return f"{self.base_url}/api/generate"


# =====================================================
# 第六部分: 模型管理器
# =====================================================

class ModelManager:
    """
    模型管理器

    管理多個模型配置,支持模型切換和選擇
    """

    def __init__(self):
        """初始化模型管理器"""
        self.models: Dict[str, ModelConfig] = {}
        self.active_model: Optional[ModelConfig] = None
        self.usage_stats: Dict[str, Dict[str, Any]] = {}

    def add_model(self, model: ModelConfig) -> bool:
        """
        添加模型配置

        Args:
            model: 模型配置

        Returns:
            是否添加成功
        """
        if not model.validate_config():
            print(f"模型配置驗證失敗: {model.name}")
            return False

        self.models[model.name] = model

        # 初始化使用統計
        self.usage_stats[model.name] = {
            "total_requests": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost": 0.0,
            "last_used": None
        }

        print(f"已添加模型: {model.name}")

        # 如果沒有活躍模型,設置為默認
        if not self.active_model:
            self.active_model = model

        return True

    def remove_model(self, name: str) -> bool:
        """
        移除模型配置

        Args:
            name: 模型名稱

        Returns:
            是否移除成功
        """
        if name in self.models:
            del self.models[name]
            print(f"已移除模型: {name}")
            return True
        return False

    def set_active_model(self, name: str) -> bool:
        """
        設置活躍模型

        Args:
            name: 模型名稱

        Returns:
            是否設置成功
        """
        if name in self.models:
            self.active_model = self.models[name]
            print(f"已切換到模型: {name}")
            return True
        else:
            print(f"未找到模型: {name}")
            return False

    def get_model_by_capability(self, capability: ModelCapability) -> List[ModelConfig]:
        """
        根據能力獲取模型

        Args:
            capability: 能力類型

        Returns:
            具備該能力的模型列表
        """
        return [
            model for model in self.models.values()
            if model.has_capability(capability) and model.enabled
        ]

    def select_best_model(
        self,
        capability: ModelCapability,
        prefer_cost: bool = False
    ) -> Optional[ModelConfig]:
        """
        選擇最佳模型

        Args:
            capability: 所需能力
            prefer_cost: 是否優先考慮成本

        Returns:
            選中的模型
        """
        candidates = self.get_model_by_capability(capability)

        if not candidates:
            return None

        if prefer_cost:
            # 選擇成本最低的模型
            return min(
                candidates,
                key=lambda m: m.cost.input_cost_per_1k if m.cost else float('inf')
            )
        else:
            # 選擇性能最好的模型(簡化:選第一個)
            return candidates[0]

    def record_usage(
        self,
        model_name: str,
        input_tokens: int,
        output_tokens: int
    ):
        """
        記錄使用情況

        Args:
            model_name: 模型名稱
            input_tokens: 輸入 token 數
            output_tokens: 輸出 token 數
        """
        if model_name not in self.usage_stats:
            return

        stats = self.usage_stats[model_name]
        model = self.models[model_name]

        # 更新統計
        stats["total_requests"] += 1
        stats["total_input_tokens"] += input_tokens
        stats["total_output_tokens"] += output_tokens
        stats["last_used"] = datetime.now()

        # 計算成本
        if model.cost:
            cost = model.cost.calculate_cost(input_tokens, output_tokens)
            stats["total_cost"] += cost

    def get_usage_report(self) -> str:
        """
        獲取使用報告

        Returns:
            使用報告文本
        """
        report = "=== 模型使用報告 ===\n\n"

        for model_name, stats in self.usage_stats.items():
            if stats["total_requests"] == 0:
                continue

            report += f"{model_name}:\n"
            report += f"  總請求數: {stats['total_requests']}\n"
            report += f"  輸入 Tokens: {stats['total_input_tokens']:,}\n"
            report += f"  輸出 Tokens: {stats['total_output_tokens']:,}\n"
            report += f"  總成本: ${stats['total_cost']:.4f}\n"
            report += f"  最後使用: {stats['last_used']}\n\n"

        # 計算總計
        total_cost = sum(s["total_cost"] for s in self.usage_stats.values())
        total_requests = sum(s["total_requests"] for s in self.usage_stats.values())

        report += f"總計:\n"
        report += f"  總請求數: {total_requests}\n"
        report += f"  總成本: ${total_cost:.4f}\n"

        return report

    def list_models(self) -> List[str]:
        """
        列出所有模型

        Returns:
            模型名稱列表
        """
        return list(self.models.keys())

    def save_config(self, filepath: str):
        """
        保存配置到文件

        Args:
            filepath: 文件路徑
        """
        config = {
            "models": [model.to_dict() for model in self.models.values()],
            "active_model": self.active_model.name if self.active_model else None
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"配置已保存到: {filepath}")

    def load_config(self, filepath: str):
        """
        從文件加載配置

        Args:
            filepath: 文件路徑
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 重新創建模型配置
        # 這裡需要根據 provider 類型創建相應的配置對象
        # 簡化實現

        print(f"配置已從文件加載: {filepath}")


# =====================================================
# 第七部分: 使用示例
# =====================================================

def setup_models_example():
    """
    設置模型示例
    """
    print("=" * 60)
    print("示例 1: 設置多個模型")
    print("=" * 60)

    # 創建模型管理器
    manager = ModelManager()

    # 添加 OpenAI 模型
    gpt4 = OpenAIModelConfig("gpt-4-turbo")
    gpt4.set_parameters(temperature=0.7, max_tokens=2000)
    manager.add_model(gpt4)

    # 添加 Anthropic 模型
    claude = AnthropicModelConfig("claude-3-opus-20240229")
    claude.set_parameters(temperature=0.5, max_tokens=4000)
    manager.add_model(claude)

    # 添加本地模型
    ollama = OllamaModelConfig("llama2")
    # manager.add_model(ollama)  # 如果 Ollama 服務未運行會失敗

    # 列出所有模型
    print("\n可用模型:")
    for name in manager.list_models():
        print(f"  - {name}")


def model_selection_example():
    """
    模型選擇示例
    """
    print("\n" + "=" * 60)
    print("示例 2: 智能模型選擇")
    print("=" * 60)

    manager = ModelManager()

    # 添加模型
    manager.add_model(OpenAIModelConfig("gpt-4-turbo"))
    manager.add_model(OpenAIModelConfig("gpt-3.5-turbo"))
    manager.add_model(AnthropicModelConfig("claude-3-haiku-20240307"))

    # 根據能力選擇模型
    print("\n選擇代碼生成模型:")
    code_models = manager.get_model_by_capability(ModelCapability.CODE_GENERATION)
    for model in code_models:
        print(f"  - {model.name}")

    # 選擇成本最優模型
    print("\n選擇成本最優模型:")
    best_model = manager.select_best_model(
        ModelCapability.CODE_GENERATION,
        prefer_cost=True
    )
    if best_model:
        print(f"  選中: {best_model.name}")


def usage_tracking_example():
    """
    使用追蹤示例
    """
    print("\n" + "=" * 60)
    print("示例 3: 使用追蹤")
    print("=" * 60)

    manager = ModelManager()
    manager.add_model(OpenAIModelConfig("gpt-4-turbo"))
    manager.add_model(OpenAIModelConfig("gpt-3.5-turbo"))

    # 模擬一些使用
    manager.record_usage("OpenAI gpt-4-turbo", 1000, 500)
    manager.record_usage("OpenAI gpt-4-turbo", 2000, 1000)
    manager.record_usage("OpenAI gpt-3.5-turbo", 3000, 1500)

    # 顯示使用報告
    print("\n" + manager.get_usage_report())


def main():
    """
    主函數
    """
    print("Continue - 模型配置管理\n")

    setup_models_example()
    model_selection_example()
    usage_tracking_example()

    print("=" * 60)
    print("示例運行完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
