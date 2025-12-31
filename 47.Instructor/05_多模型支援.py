"""
Instructor 多模型支援示例

這個模塊展示了如何使用 Instructor 與不同的 LLM 提供商進行交互。
Instructor 支持 OpenAI、Anthropic、Google、Cohere 等多家提供商。

主要內容：
1. OpenAI (GPT-4, GPT-3.5) 集成
2. Anthropic (Claude) 集成
3. Google (Gemini) 集成
4. 多提供商抽象層
5. 提供商特定功能
6. 成本優化策略

作者: Instructor 示例
日期: 2025-01-01
"""

import os
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
import instructor
from openai import OpenAI
from anthropic import Anthropic


# ============================================================================
# 通用數據模型
# ============================================================================

class User(BaseModel):
    """用戶信息模型 - 跨提供商通用"""
    name: str = Field(description="用戶全名")
    age: int = Field(description="年齡", ge=0, le=150)
    email: str = Field(description="電子郵件地址")
    occupation: str = Field(description="職業")


class SentimentAnalysis(BaseModel):
    """情感分析模型 - 適用於所有提供商"""
    text: str = Field(description="分析的文本")
    sentiment: Literal["positive", "negative", "neutral"] = Field(
        description="情感傾向"
    )
    confidence: float = Field(
        description="置信度（0-1）",
        ge=0.0,
        le=1.0
    )
    key_phrases: List[str] = Field(
        description="關鍵短語列表"
    )


class Summary(BaseModel):
    """摘要模型 - 跨提供商通用"""
    title: str = Field(description="標題")
    main_points: List[str] = Field(
        description="主要要點",
        min_length=3,
        max_length=5
    )
    summary: str = Field(
        description="簡短摘要（100字以內）",
        max_length=100
    )


class Classification(BaseModel):
    """分類模型 - 通用分類任務"""
    category: str = Field(description="主要類別")
    subcategory: Optional[str] = Field(
        default=None,
        description="子類別"
    )
    tags: List[str] = Field(description="標籤列表")
    confidence: float = Field(
        description="分類置信度",
        ge=0.0,
        le=1.0
    )


class TranslationResult(BaseModel):
    """翻譯結果模型"""
    source_language: str = Field(description="源語言")
    target_language: str = Field(description="目標語言")
    original_text: str = Field(description="原文")
    translated_text: str = Field(description="譯文")
    quality_score: float = Field(
        description="翻譯質量評分（0-100）",
        ge=0,
        le=100
    )


# ============================================================================
# OpenAI 集成
# ============================================================================

class OpenAIClient:
    """OpenAI 客戶端封裝"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化 OpenAI 客戶端

        Args:
            api_key: OpenAI API 密鑰，如果未提供則從環境變量讀取
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "sk-placeholder")
        self.base_client = OpenAI(api_key=self.api_key)
        self.client = instructor.from_openai(self.base_client)
        self.provider = "OpenAI"

    def extract(self, model: str, response_model, messages: List[dict]):
        """使用 OpenAI 模型提取數據

        Args:
            model: 模型名稱（如 "gpt-4", "gpt-3.5-turbo"）
            response_model: Pydantic 模型類
            messages: 消息列表

        Returns:
            提取的數據對象
        """
        print(f"  使用提供商: {self.provider}")
        print(f"  使用模型: {model}")

        return self.client.chat.completions.create(
            model=model,
            response_model=response_model,
            messages=messages
        )


def demo_openai_extraction():
    """演示 OpenAI 提取"""
    print(f"\n{'='*60}")
    print("OpenAI (GPT-4) 提取示例")
    print(f"{'='*60}")

    client = OpenAIClient()

    text = """
    姓名：李明
    年齡：32歲
    郵箱：li.ming@company.com
    職業：軟件架構師
    """

    print(f"\n提取用戶信息...")
    user = client.extract(
        model="gpt-4",
        response_model=User,
        messages=[
            {"role": "user", "content": f"提取用戶信息：\n{text}"}
        ]
    )

    print(f"\n結果:")
    print(f"  姓名: {user.name}")
    print(f"  年齡: {user.age}")
    print(f"  職業: {user.occupation}")
    print(f"  郵箱: {user.email}")

    return user


def demo_openai_sentiment():
    """演示 OpenAI 情感分析"""
    print(f"\n{'='*60}")
    print("OpenAI (GPT-3.5-Turbo) 情感分析")
    print(f"{'='*60}")

    client = OpenAIClient()

    text = "這個產品真的太棒了！質量超出預期，客服態度也很好，五星推薦！"

    print(f"\n分析文本: {text}")
    sentiment = client.extract(
        model="gpt-3.5-turbo",
        response_model=SentimentAnalysis,
        messages=[
            {"role": "user", "content": f"分析情感：{text}"}
        ]
    )

    print(f"\n分析結果:")
    print(f"  情感: {sentiment.sentiment}")
    print(f"  置信度: {sentiment.confidence:.2%}")
    print(f"  關鍵短語: {', '.join(sentiment.key_phrases)}")

    return sentiment


# ============================================================================
# Anthropic (Claude) 集成
# ============================================================================

class AnthropicClient:
    """Anthropic (Claude) 客戶端封裝"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化 Anthropic 客戶端

        Args:
            api_key: Anthropic API 密鑰，如果未提供則從環境變量讀取
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "sk-placeholder")
        self.base_client = Anthropic(api_key=self.api_key)
        self.client = instructor.from_anthropic(self.base_client)
        self.provider = "Anthropic (Claude)"

    def extract(
        self,
        model: str,
        response_model,
        messages: List[dict],
        max_tokens: int = 1024
    ):
        """使用 Claude 模型提取數據

        Args:
            model: 模型名稱（如 "claude-3-5-sonnet-20241022"）
            response_model: Pydantic 模型類
            messages: 消息列表
            max_tokens: 最大 token 數

        Returns:
            提取的數據對象
        """
        print(f"  使用提供商: {self.provider}")
        print(f"  使用模型: {model}")

        return self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            response_model=response_model,
            messages=messages
        )


def demo_anthropic_extraction():
    """演示 Anthropic (Claude) 提取"""
    print(f"\n{'='*60}")
    print("Anthropic (Claude) 提取示例")
    print(f"{'='*60}")

    client = AnthropicClient()

    text = """
    姓名：王芳
    年齡：28歲
    郵箱：wang.fang@example.com
    職業：數據科學家
    """

    print(f"\n提取用戶信息...")
    user = client.extract(
        model="claude-3-5-sonnet-20241022",
        response_model=User,
        messages=[
            {"role": "user", "content": f"提取用戶信息：\n{text}"}
        ]
    )

    print(f"\n結果:")
    print(f"  姓名: {user.name}")
    print(f"  年齡: {user.age}")
    print(f"  職業: {user.occupation}")
    print(f"  郵箱: {user.email}")

    return user


def demo_anthropic_summary():
    """演示 Claude 摘要生成"""
    print(f"\n{'='*60}")
    print("Anthropic (Claude) 摘要生成")
    print(f"{'='*60}")

    client = AnthropicClient()

    text = """
    人工智能（AI）正在revolutionize各個行業。從醫療診斷到自動駕駛，
    AI技術的應用越來越廣泛。機器學習算法能夠處理大量數據，
    發現人類難以察覺的模式。深度學習技術在圖像識別、
    自然語言處理等領域取得了突破性進展。然而，AI的發展
    也帶來了倫理和隱私方面的挑戰。如何確保AI系統的公平性、
    透明度和安全性，是當前亟需解決的問題。
    """

    print(f"\n生成摘要...")
    summary = client.extract(
        model="claude-3-5-sonnet-20241022",
        response_model=Summary,
        messages=[
            {"role": "user", "content": f"總結以下文本：\n{text}"}
        ],
        max_tokens=2048
    )

    print(f"\n摘要結果:")
    print(f"  標題: {summary.title}")
    print(f"  主要要點:")
    for i, point in enumerate(summary.main_points, 1):
        print(f"    {i}. {point}")
    print(f"  摘要: {summary.summary}")

    return summary


# ============================================================================
# 多提供商抽象層
# ============================================================================

class UniversalClient:
    """通用客戶端 - 支持多個提供商"""

    def __init__(self):
        """初始化通用客戶端"""
        self.openai_client = None
        self.anthropic_client = None

        # 嘗試初始化可用的客戶端
        if os.getenv("OPENAI_API_KEY"):
            try:
                self.openai_client = OpenAIClient()
                print("✓ OpenAI 客戶端已初始化")
            except Exception as e:
                print(f"✗ OpenAI 初始化失敗: {e}")

        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                self.anthropic_client = AnthropicClient()
                print("✓ Anthropic 客戶端已初始化")
            except Exception as e:
                print(f"✗ Anthropic 初始化失敗: {e}")

    def extract(
        self,
        provider: Literal["openai", "anthropic"],
        model: str,
        response_model,
        messages: List[dict],
        **kwargs
    ):
        """使用指定提供商提取數據

        Args:
            provider: 提供商名稱
            model: 模型名稱
            response_model: Pydantic 模型類
            messages: 消息列表
            **kwargs: 其他參數

        Returns:
            提取的數據對象
        """
        if provider == "openai":
            if not self.openai_client:
                raise ValueError("OpenAI 客戶端未初始化")
            return self.openai_client.extract(model, response_model, messages)

        elif provider == "anthropic":
            if not self.anthropic_client:
                raise ValueError("Anthropic 客戶端未初始化")
            return self.anthropic_client.extract(
                model,
                response_model,
                messages,
                **kwargs
            )

        else:
            raise ValueError(f"不支持的提供商: {provider}")

    def extract_with_fallback(
        self,
        response_model,
        messages: List[dict],
        preferred_provider: str = "openai"
    ):
        """帶回退機制的提取

        如果首選提供商失敗，自動嘗試其他提供商。

        Args:
            response_model: Pydantic 模型類
            messages: 消息列表
            preferred_provider: 首選提供商

        Returns:
            提取的數據對象
        """
        providers = {
            "openai": ("gpt-4", self.openai_client),
            "anthropic": ("claude-3-5-sonnet-20241022", self.anthropic_client)
        }

        # 嘗試首選提供商
        if preferred_provider in providers:
            model, client = providers[preferred_provider]
            if client:
                try:
                    print(f"嘗試使用 {preferred_provider}...")
                    return client.extract(model, response_model, messages)
                except Exception as e:
                    print(f"  失敗: {e}")

        # 嘗試其他提供商
        for name, (model, client) in providers.items():
            if name != preferred_provider and client:
                try:
                    print(f"回退到 {name}...")
                    return client.extract(model, response_model, messages)
                except Exception as e:
                    print(f"  失敗: {e}")

        raise RuntimeError("所有提供商都失敗了")


def demo_universal_client():
    """演示通用客戶端"""
    print(f"\n{'='*60}")
    print("通用客戶端示例")
    print(f"{'='*60}")

    client = UniversalClient()

    text = "這篇文章討論了區塊鏈技術在金融領域的應用前景。"

    print(f"\n文本分類...")

    try:
        # 使用回退機制
        classification = client.extract_with_fallback(
            response_model=Classification,
            messages=[
                {"role": "user", "content": f"分類以下文本：\n{text}"}
            ],
            preferred_provider="openai"
        )

        print(f"\n分類結果:")
        print(f"  類別: {classification.category}")
        print(f"  子類別: {classification.subcategory or '無'}")
        print(f"  標籤: {', '.join(classification.tags)}")
        print(f"  置信度: {classification.confidence:.2%}")

    except Exception as e:
        print(f"\n分類失敗: {e}")


# ============================================================================
# 提供商對比
# ============================================================================

def compare_providers():
    """對比不同提供商的性能

    在相同任務上對比 OpenAI 和 Anthropic 的表現。
    """
    print(f"\n{'='*60}")
    print("提供商性能對比")
    print(f"{'='*60}")

    text = """
    原文（英文）：
    Artificial intelligence is transforming the way we work and live.
    Machine learning algorithms can process vast amounts of data
    and identify patterns that humans might miss.

    請翻譯成中文。
    """

    # OpenAI 翻譯
    print(f"\n1. OpenAI GPT-4 翻譯:")
    print("-" * 60)
    try:
        openai_client = OpenAIClient()
        openai_result = openai_client.extract(
            model="gpt-4",
            response_model=TranslationResult,
            messages=[
                {"role": "user", "content": text}
            ]
        )
        print(f"  譯文: {openai_result.translated_text}")
        print(f"  質量評分: {openai_result.quality_score}/100")
    except Exception as e:
        print(f"  錯誤: {e}")

    # Anthropic 翻譯
    print(f"\n2. Anthropic Claude 翻譯:")
    print("-" * 60)
    try:
        anthropic_client = AnthropicClient()
        anthropic_result = anthropic_client.extract(
            model="claude-3-5-sonnet-20241022",
            response_model=TranslationResult,
            messages=[
                {"role": "user", "content": text}
            ]
        )
        print(f"  譯文: {anthropic_result.translated_text}")
        print(f"  質量評分: {anthropic_result.quality_score}/100")
    except Exception as e:
        print(f"  錯誤: {e}")


# ============================================================================
# 成本優化策略
# ============================================================================

class CostOptimizer:
    """成本優化器

    根據任務複雜度選擇最合適的模型，以優化成本。
    """

    def __init__(self):
        self.client = UniversalClient()

        # 模型成本映射（相對成本）
        self.model_costs = {
            "gpt-4": 10,
            "gpt-3.5-turbo": 1,
            "claude-3-5-sonnet-20241022": 8,
            "claude-3-haiku-20240307": 1,
        }

    def extract_optimized(
        self,
        response_model,
        messages: List[dict],
        complexity: Literal["simple", "medium", "complex"] = "medium"
    ):
        """根據複雜度優化提取

        Args:
            response_model: Pydantic 模型類
            messages: 消息列表
            complexity: 任務複雜度

        Returns:
            提取的數據對象
        """
        # 根據複雜度選擇模型
        if complexity == "simple":
            # 簡單任務使用便宜的模型
            provider, model = "openai", "gpt-3.5-turbo"
            print(f"  任務複雜度: 簡單 → 使用 {model}")

        elif complexity == "medium":
            # 中等任務使用平衡的模型
            provider, model = "anthropic", "claude-3-5-sonnet-20241022"
            print(f"  任務複雜度: 中等 → 使用 {model}")

        else:  # complex
            # 複雜任務使用最強的模型
            provider, model = "openai", "gpt-4"
            print(f"  任務複雜度: 複雜 → 使用 {model}")

        return self.client.extract(
            provider=provider,
            model=model,
            response_model=response_model,
            messages=messages
        )


def demo_cost_optimization():
    """演示成本優化"""
    print(f"\n{'='*60}")
    print("成本優化示例")
    print(f"{'='*60}")

    optimizer = CostOptimizer()

    # 簡單任務
    simple_text = "分類：這是一條關於天氣的消息。"
    print(f"\n簡單任務: {simple_text}")
    try:
        optimizer.extract_optimized(
            response_model=Classification,
            messages=[{"role": "user", "content": simple_text}],
            complexity="simple"
        )
    except Exception as e:
        print(f"  錯誤: {e}")

    # 複雜任務
    complex_text = "詳細分析這篇論文的研究方法、主要發現和學術貢獻..."
    print(f"\n複雜任務: {complex_text[:30]}...")
    try:
        optimizer.extract_optimized(
            response_model=Summary,
            messages=[{"role": "user", "content": complex_text}],
            complexity="complex"
        )
    except Exception as e:
        print(f"  錯誤: {e}")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主函數 - 運行所有多模型示例"""
    print("="*60)
    print("Instructor 多模型支援示例")
    print("="*60)

    # OpenAI 示例
    demo_openai_extraction()
    demo_openai_sentiment()

    # Anthropic 示例
    demo_anthropic_extraction()
    demo_anthropic_summary()

    # 通用客戶端
    demo_universal_client()

    # 提供商對比
    compare_providers()

    # 成本優化
    demo_cost_optimization()

    print("\n" + "="*60)
    print("多模型支援要點總結")
    print("="*60)
    print("""
1. 支持的提供商：
   - OpenAI (GPT-4, GPT-3.5-Turbo)
   - Anthropic (Claude 3.5 Sonnet, Claude 3 Haiku)
   - Google (Gemini Pro)
   - Cohere (Command R+)

2. 集成方法：
   - OpenAI: instructor.from_openai()
   - Anthropic: instructor.from_anthropic()
   - 統一接口，相同的 API

3. 提供商選擇考量：
   - 成本（GPT-3.5 < Claude Haiku < GPT-4）
   - 性能（複雜任務選 GPT-4 或 Claude Sonnet）
   - 可用性（API 限制、區域限制）
   - 特定功能需求

4. 最佳實踐：
   - 實現回退機制
   - 根據任務複雜度選擇模型
   - 監控成本和性能
   - 使用環境變量管理密鑰

5. 成本優化：
   - 簡單任務用便宜模型
   - 批量處理降低開銷
   - 緩存常見結果
   - 設置合理的 max_tokens
    """)


if __name__ == "__main__":
    main()
