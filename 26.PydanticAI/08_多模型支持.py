"""
Pydantic AI - 多模型支持範例

本範例展示：
1. 使用不同 LLM 提供商
2. 模型切換
3. Fallback 機制
4. 模型比較
5. 成本優化策略

Pydantic AI 支持所有主流 LLM 提供商
"""

import asyncio
import time
from typing import Optional
from pydantic import BaseModel
from pydantic_ai import Agent


# ============================================================================
# 範例 1: OpenAI 模型
# ============================================================================

def example_1_openai_models():
    """使用 OpenAI 的不同模型"""
    print("\n" + "="*60)
    print("範例 1: OpenAI 模型")
    print("="*60)

    # GPT-4（最強大）
    agent_gpt4 = Agent('openai:gpt-4')

    # GPT-3.5 Turbo（快速且便宜）
    agent_gpt35 = Agent('openai:gpt-3.5-turbo')

    # GPT-4 Turbo（性能與成本平衡）
    agent_gpt4_turbo = Agent('openai:gpt-4-turbo-preview')

    prompt = "用一句話解釋什麼是機器學習"

    print("GPT-3.5 Turbo 回應：")
    result = agent_gpt35.run_sync(prompt)
    print(f"{result.data}\n")

    print("模型選擇建議：")
    print("  - GPT-3.5: 簡單任務、快速回應")
    print("  - GPT-4 Turbo: 平衡性能和成本")
    print("  - GPT-4: 複雜推理、最高質量")


# ============================================================================
# 範例 2: Anthropic Claude 模型
# ============================================================================

async def example_2_anthropic_models():
    """使用 Anthropic Claude 模型"""
    print("\n" + "="*60)
    print("範例 2: Anthropic Claude 模型")
    print("="*60)

    # 需要設置 ANTHROPIC_API_KEY
    try:
        # Claude 3.5 Sonnet（最新最強）
        agent_claude = Agent('anthropic:claude-3-5-sonnet-20241022')

        # Claude 3 Haiku（快速便宜）
        # agent_haiku = Agent('anthropic:claude-3-haiku-20240307')

        result = await agent_claude.run(
            '用繁體中文解釋什麼是神經網絡'
        )

        print(f"Claude 3.5 Sonnet 回應：")
        print(f"{result.data}\n")

        print("Claude 模型特點：")
        print("  - 長上下文窗口（200K tokens）")
        print("  - 強大的分析能力")
        print("  - 良好的繁體中文支持")

    except Exception as e:
        print(f"⚠️  無法使用 Claude：{e}")
        print("   請設置 ANTHROPIC_API_KEY 環境變量")


# ============================================================================
# 範例 3: Google Gemini 模型
# ============================================================================

async def example_3_google_models():
    """使用 Google Gemini 模型"""
    print("\n" + "="*60)
    print("範例 3: Google Gemini 模型")
    print("="*60)

    try:
        # Gemini Pro
        agent_gemini = Agent('google:gemini-pro')

        result = await agent_gemini.run(
            '列出 Python 的三個主要特點'
        )

        print(f"Gemini Pro 回應：")
        print(f"{result.data}\n")

        print("Gemini 模型特點：")
        print("  - 多模態支持（文本、圖片）")
        print("  - 免費額度較高")
        print("  - Google 生態整合")

    except Exception as e:
        print(f"⚠️  無法使用 Gemini：{e}")
        print("   請設置 GOOGLE_API_KEY 環境變量")


# ============================================================================
# 範例 4: 本地模型（Ollama）
# ============================================================================

async def example_4_local_models():
    """使用 Ollama 運行本地模型"""
    print("\n" + "="*60)
    print("範例 4: 本地模型 (Ollama)")
    print("="*60)

    try:
        # 需要先安裝並運行 Ollama
        # 支持 llama3, mistral, phi 等模型
        agent_llama = Agent('ollama:llama3')

        result = await agent_llama.run(
            'What is Python in one sentence?'
        )

        print(f"Llama3 回應：")
        print(f"{result.data}\n")

        print("本地模型優勢：")
        print("  - 完全私密，數據不離開本機")
        print("  - 無 API 調用成本")
        print("  - 無網絡依賴")
        print("  - 可自定義微調")

    except Exception as e:
        print(f"⚠️  無法使用 Ollama：{e}")
        print("   請確保 Ollama 已安裝並運行")
        print("   安裝：https://ollama.ai")


# ============================================================================
# 範例 5: 模型切換與比較
# ============================================================================

class ModelComparison(BaseModel):
    """模型比較結果"""
    model_name: str
    response: str
    response_time: float
    success: bool
    error: Optional[str] = None


async def test_model(
    model: str,
    prompt: str
) -> ModelComparison:
    """測試單個模型"""
    start_time = time.time()

    try:
        agent = Agent(model)
        result = await agent.run(prompt)

        return ModelComparison(
            model_name=model,
            response=result.data,
            response_time=time.time() - start_time,
            success=True
        )

    except Exception as e:
        return ModelComparison(
            model_name=model,
            response="",
            response_time=time.time() - start_time,
            success=False,
            error=str(e)
        )


async def example_5_model_comparison():
    """比較不同模型的表現"""
    print("\n" + "="*60)
    print("範例 5: 模型比較")
    print("="*60)

    prompt = "用一句話解釋什麼是人工智慧"

    # 測試的模型列表
    models = [
        'openai:gpt-3.5-turbo',
        'openai:gpt-4',
        # 'anthropic:claude-3-5-sonnet-20241022',
        # 'google:gemini-pro',
    ]

    print(f"測試提示：{prompt}\n")

    results = []
    for model in models:
        print(f"測試 {model}...", end=' ', flush=True)
        result = await test_model(model, prompt)
        results.append(result)

        if result.success:
            print(f"✓ ({result.response_time:.2f}s)")
        else:
            print(f"✗ ({result.error})")

    # 顯示結果
    print("\n比較結果：")
    print("="*60)

    for result in results:
        if result.success:
            print(f"\n{result.model_name}:")
            print(f"  回應：{result.response}")
            print(f"  時間：{result.response_time:.2f} 秒")


# ============================================================================
# 範例 6: Fallback 機制
# ============================================================================

async def run_with_fallback(
    primary_model: str,
    fallback_models: list[str],
    prompt: str
) -> tuple[str, str]:
    """
    使用 fallback 機制運行

    Returns:
        (使用的模型, 響應內容)
    """
    # 嘗試主要模型
    models_to_try = [primary_model] + fallback_models

    for model in models_to_try:
        try:
            print(f"  嘗試 {model}...", end=' ', flush=True)
            agent = Agent(model)
            result = await agent.run(prompt)
            print("✓")
            return model, result.data

        except Exception as e:
            print(f"✗ ({type(e).__name__})")
            continue

    raise RuntimeError("所有模型都失敗了")


async def example_6_fallback_mechanism():
    """實現模型 fallback 機制"""
    print("\n" + "="*60)
    print("範例 6: Fallback 機制")
    print("="*60)

    # 定義 fallback 鏈
    primary = 'openai:gpt-4'
    fallbacks = [
        'openai:gpt-3.5-turbo',
        # 'anthropic:claude-3-5-sonnet-20241022',
    ]

    print(f"主要模型：{primary}")
    print(f"備用模型：{', '.join(fallbacks)}\n")

    try:
        model_used, response = await run_with_fallback(
            primary,
            fallbacks,
            "解釋什麼是深度學習"
        )

        print(f"\n✓ 成功使用：{model_used}")
        print(f"回應：{response}")

    except Exception as e:
        print(f"\n✗ 所有模型都失敗：{e}")


# ============================================================================
# 範例 7: 成本優化策略
# ============================================================================

class TaskComplexity:
    """任務複雜度評估"""

    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


def select_model_by_complexity(complexity: str) -> str:
    """根據任務複雜度選擇模型"""
    model_map = {
        TaskComplexity.SIMPLE: 'openai:gpt-3.5-turbo',  # 便宜快速
        TaskComplexity.MEDIUM: 'openai:gpt-4-turbo-preview',  # 平衡
        TaskComplexity.COMPLEX: 'openai:gpt-4',  # 強大但貴
    }

    return model_map.get(complexity, 'openai:gpt-3.5-turbo')


async def example_7_cost_optimization():
    """成本優化策略"""
    print("\n" + "="*60)
    print("範例 7: 成本優化")
    print("="*60)

    tasks = [
        ("你好", TaskComplexity.SIMPLE),
        ("解釋量子糾纏", TaskComplexity.MEDIUM),
        ("設計一個分布式系統架構", TaskComplexity.COMPLEX),
    ]

    for prompt, complexity in tasks:
        model = select_model_by_complexity(complexity)

        print(f"\n任務：{prompt}")
        print(f"複雜度：{complexity}")
        print(f"選擇模型：{model}")

        agent = Agent(model)
        result = await agent.run(prompt)

        print(f"回應：{result.data[:100]}...")

    print("\n\n成本優化建議：")
    print("  1. 簡單任務用便宜模型")
    print("  2. 批量處理降低調用次數")
    print("  3. 使用緩存避免重複請求")
    print("  4. 考慮使用本地模型")


# ============================================================================
# 範例 8: 動態模型選擇
# ============================================================================

class SmartAgent:
    """智能 Agent - 自動選擇最佳模型"""

    def __init__(self):
        self.model_performance = {
            'openai:gpt-3.5-turbo': {'speed': 9, 'quality': 7, 'cost': 9},
            'openai:gpt-4': {'speed': 6, 'quality': 10, 'cost': 3},
            'openai:gpt-4-turbo-preview': {'speed': 8, 'quality': 9, 'cost': 6},
        }

    def select_best_model(
        self,
        priority: str = "balanced"
    ) -> str:
        """
        選擇最佳模型

        Args:
            priority: 優先級 - "speed", "quality", "cost", "balanced"
        """
        weights = {
            "speed": {'speed': 0.7, 'quality': 0.2, 'cost': 0.1},
            "quality": {'speed': 0.1, 'quality': 0.8, 'cost': 0.1},
            "cost": {'speed': 0.1, 'quality': 0.2, 'cost': 0.7},
            "balanced": {'speed': 0.33, 'quality': 0.34, 'cost': 0.33},
        }

        weight = weights.get(priority, weights["balanced"])

        best_model = None
        best_score = 0

        for model, metrics in self.model_performance.items():
            score = sum(
                metrics[metric] * weight[metric]
                for metric in weight
            )

            if score > best_score:
                best_score = score
                best_model = model

        return best_model

    async def run(self, prompt: str, priority: str = "balanced") -> str:
        """運行 Agent"""
        model = self.select_best_model(priority)
        agent = Agent(model)
        result = await agent.run(prompt)
        return result.data


async def example_8_dynamic_selection():
    """動態模型選擇"""
    print("\n" + "="*60)
    print("範例 8: 動態模型選擇")
    print("="*60)

    smart_agent = SmartAgent()
    prompt = "解釋機器學習"

    priorities = ["speed", "quality", "cost", "balanced"]

    for priority in priorities:
        model = smart_agent.select_best_model(priority)
        print(f"\n優先級 '{priority}'：選擇 {model}")

        result = await smart_agent.run(prompt, priority)
        print(f"回應：{result[:80]}...")


# ============================================================================
# 主程式
# ============================================================================

async def main():
    """運行所有範例"""
    print("\n" + "🌐 " + "="*58)
    print("Pydantic AI - 多模型支持範例")
    print("="*60)

    example_1_openai_models()
    await example_2_anthropic_models()
    await example_3_google_models()
    await example_4_local_models()
    await example_5_model_comparison()
    await example_6_fallback_mechanism()
    await example_7_cost_optimization()
    await example_8_dynamic_selection()

    print("\n" + "="*60)
    print("✓ 多模型支持範例完成！")
    print("💡 模型選擇建議：")
    print("   1. 根據任務選擇合適的模型")
    print("   2. 實現 fallback 提高可靠性")
    print("   3. 平衡成本與性能")
    print("   4. 考慮使用本地模型保護隱私")
    print("="*60)


if __name__ == '__main__':
    import os
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  請設置 OPENAI_API_KEY 環境變量")
    else:
        asyncio.run(main())
