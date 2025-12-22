"""
OpenAI Agents SDK - LiteLLM 整合範例

展示如何使用 LiteLLM 支持 100+ LLM 提供商
包含：Anthropic Claude、Google Gemini、本地模型、成本對比
"""

import os
from openai_agents import Agent, tool, run, Session, configure

print("""
="*80)
OpenAI Agents SDK + LiteLLM 整合
="*80)

# ============================================================================
# 什麼是 LiteLLM？
# ============================================================================

LiteLLM 是一個統一的 LLM API 接口，支持 100+ 模型提供商：

支持的提供商：
✓ OpenAI (GPT-4, GPT-3.5)
✓ Anthropic (Claude 3 Opus, Sonnet, Haiku)
✓ Google (Gemini Pro, Gemini Ultra)
✓ Cohere (Command, Command-R)
✓ Azure OpenAI
✓ AWS Bedrock
✓ Hugging Face
✓ Ollama (本地模型)
✓ Together AI
✓ Replicate
✓ ... 還有更多

# ============================================================================
# 為什麼需要 LiteLLM？
# ============================================================================

1. **多提供商支持**
   - 不被單一提供商鎖定
   - 根據需求選擇最佳模型
   - 成本優化

2. **統一接口**
   - 相同的代碼適用所有提供商
   - 輕鬆切換模型
   - 簡化開發

3. **降低成本**
   - Claude 某些任務更便宜
   - Gemini Pro 免費額度
   - 本地模型零成本

4. **提高可用性**
   - 主提供商故障時切換
   - 分散請求負載
   - 避免限流

# ============================================================================
# 安裝
# ============================================================================

pip install openai-agents[litellm]

# 或單獨安裝
pip install litellm

# ============================================================================
# 配置
# ============================================================================

# 環境變量
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export GOOGLE_API_KEY=...
export COHERE_API_KEY=...

# 或在代碼中配置
import os
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."
os.environ["GOOGLE_API_KEY"] = "..."
""")


# ============================================================================
# 1. 基礎使用
# ============================================================================

def test_openai():
    """使用 OpenAI 模型"""
    print("\n" + "="*60)
    print("範例 1: OpenAI GPT-4")
    print("="*60)

    configure(api_key=os.getenv("OPENAI_API_KEY"))

    agent = Agent(
        name="GPT4助手",
        model="gpt-4",  # OpenAI 模型
        instructions="你是助手，使用繁體中文。"
    )

    response = run(
        agent=agent,
        messages=[{"role": "user", "content": "解釋量子糾纏"}]
    )

    print(f"\n模型: {agent.model}")
    print(f"回應: {response.messages[-1]['content'][:200]}...")


def test_claude():
    """使用 Anthropic Claude"""
    print("\n" + "="*60)
    print("範例 2: Anthropic Claude")
    print("="*60)

    # 注意：需要設置 ANTHROPIC_API_KEY
    configure(litellm_provider="anthropic")

    agent = Agent(
        name="Claude助手",
        model="claude-3-sonnet-20240229",  # Claude 模型
        instructions="你是助手，使用繁體中文。"
    )

    print(f"\n模型: {agent.model}")
    print("（需要 ANTHROPIC_API_KEY 才能運行）")

    # response = run(
    #     agent=agent,
    #     messages=[{"role": "user", "content": "解釋量子糾纏"}]
    # )
    # print(f"回應: {response.messages[-1]['content'][:200]}...")


def test_gemini():
    """使用 Google Gemini"""
    print("\n" + "="*60)
    print("範例 3: Google Gemini")
    print("="*60)

    configure(litellm_provider="google")

    agent = Agent(
        name="Gemini助手",
        model="gemini/gemini-pro",  # Gemini 模型
        instructions="你是助手，使用繁體中文。"
    )

    print(f"\n模型: {agent.model}")
    print("（需要 GOOGLE_API_KEY 才能運行）")


def test_ollama():
    """使用 Ollama 本地模型"""
    print("\n" + "="*60)
    print("範例 4: Ollama 本地模型")
    print("="*60)

    configure(litellm_provider="ollama")

    agent = Agent(
        name="本地助手",
        model="ollama/llama2",  # 本地 Llama2
        instructions="你是助手，使用繁體中文。"
    )

    print(f"\n模型: {agent.model}")
    print("（需要本地運行 Ollama 服務）")
    print("啟動方法: ollama run llama2")


# ============================================================================
# 2. 模型對比
# ============================================================================

def compare_models():
    """對比不同模型的表現"""
    print("\n" + "="*60)
    print("範例 5: 模型對比")
    print("="*60)

    question = "什麼是機器學習？用一句話解釋。"

    models_config = [
        ("gpt-4", "OpenAI GPT-4", "openai"),
        ("gpt-3.5-turbo", "OpenAI GPT-3.5", "openai"),
        # ("claude-3-sonnet-20240229", "Claude 3 Sonnet", "anthropic"),
        # ("gemini/gemini-pro", "Gemini Pro", "google"),
    ]

    print(f"\n問題: {question}\n")

    for model_id, model_name, provider in models_config:
        try:
            configure(
                api_key=os.getenv("OPENAI_API_KEY"),
                litellm_provider=provider
            )

            agent = Agent(
                name=f"{model_name}助手",
                model=model_id,
                instructions="用最簡潔的方式回答。使用繁體中文。"
            )

            response = run(
                agent=agent,
                messages=[{"role": "user", "content": question}]
            )

            print(f"【{model_name}】")
            print(f"{response.messages[-1]['content']}\n")

        except Exception as e:
            print(f"【{model_name}】")
            print(f"無法測試: {str(e)[:50]}...\n")


# ============================================================================
# 3. 成本優化
# ============================================================================

def cost_comparison():
    """成本對比分析"""
    print("\n" + "="*60)
    print("範例 6: 成本對比（估算）")
    print("="*60)

    # 價格數據（每百萬 tokens，USD）
    pricing = {
        "gpt-4": {
            "input": 30.0,
            "output": 60.0,
            "quality": "最高"
        },
        "gpt-3.5-turbo": {
            "input": 0.5,
            "output": 1.5,
            "quality": "良好"
        },
        "claude-3-opus": {
            "input": 15.0,
            "output": 75.0,
            "quality": "最高"
        },
        "claude-3-sonnet": {
            "input": 3.0,
            "output": 15.0,
            "quality": "優秀"
        },
        "claude-3-haiku": {
            "input": 0.25,
            "output": 1.25,
            "quality": "良好"
        },
        "gemini-pro": {
            "input": 0.0,  # 免費額度
            "output": 0.0,
            "quality": "優秀"
        },
        "ollama/llama2": {
            "input": 0.0,  # 本地運行
            "output": 0.0,
            "quality": "中等"
        }
    }

    print("\n價格對比表（每百萬 tokens）：\n")
    print(f"{'模型':<20} {'輸入':<10} {'輸出':<10} {'質量':<10}")
    print("-" * 50)

    for model, data in pricing.items():
        print(f"{model:<20} ${data['input']:<9.2f} ${data['output']:<9.2f} {data['quality']:<10}")

    # 使用場景建議
    print("\n使用場景建議：")
    print("""
    高質量任務（如代碼生成、複雜分析）:
      → GPT-4 或 Claude 3 Opus

    一般對話、客服:
      → GPT-3.5 或 Claude 3 Sonnet

    大量簡單任務:
      → Claude 3 Haiku 或 Gemini Pro

    開發測試、實驗:
      → Gemini Pro（免費）或 Ollama（本地）

    成本敏感場景:
      → 混合使用，根據任務難度動態選擇
    """)


# ============================================================================
# 4. 智能模型路由
# ============================================================================

def intelligent_routing():
    """根據任務類型智能選擇模型"""
    print("\n" + "="*60)
    print("範例 7: 智能模型路由")
    print("="*60)

    def select_model(task_type: str, complexity: str) -> str:
        """根據任務選擇最佳模型

        Args:
            task_type: 任務類型 (chat, code, analysis, translation)
            complexity: 複雜度 (simple, medium, complex)

        Returns:
            模型 ID
        """
        routing_table = {
            "chat": {
                "simple": "gpt-3.5-turbo",
                "medium": "gpt-3.5-turbo",
                "complex": "gpt-4"
            },
            "code": {
                "simple": "gpt-3.5-turbo",
                "medium": "gpt-4",
                "complex": "gpt-4"
            },
            "analysis": {
                "simple": "gpt-3.5-turbo",
                "medium": "gpt-4",
                "complex": "gpt-4"
            },
            "translation": {
                "simple": "gpt-3.5-turbo",
                "medium": "gpt-3.5-turbo",
                "complex": "gpt-3.5-turbo"
            }
        }

        return routing_table.get(task_type, {}).get(complexity, "gpt-3.5-turbo")

    # 測試路由
    test_cases = [
        ("chat", "simple", "你好"),
        ("code", "complex", "寫一個二叉樹實現"),
        ("analysis", "medium", "分析市場趨勢"),
        ("translation", "simple", "翻譯: Hello")
    ]

    for task_type, complexity, query in test_cases:
        model = select_model(task_type, complexity)
        print(f"\n任務: {query}")
        print(f"  類型: {task_type}, 複雜度: {complexity}")
        print(f"  選擇模型: {model}")


# ============================================================================
# 5. 故障轉移
# ============================================================================

def failover_example():
    """演示故障轉移機制"""
    print("\n" + "="*60)
    print("範例 8: 故障轉移")
    print("="*60)

    def run_with_failover(query: str, models: list) -> dict:
        """嘗試多個模型，直到成功

        Args:
            query: 查詢內容
            models: 模型列表（優先級排序）

        Returns:
            結果字典
        """
        for model_id in models:
            try:
                print(f"  嘗試: {model_id}...")

                agent = Agent(
                    name="助手",
                    model=model_id,
                    instructions="使用繁體中文。"
                )

                response = run(
                    agent=agent,
                    messages=[{"role": "user", "content": query}]
                )

                print(f"  ✓ 成功")
                return {
                    "success": True,
                    "model": model_id,
                    "response": response.messages[-1]['content']
                }

            except Exception as e:
                print(f"  ✗ 失敗: {str(e)[:50]}...")
                continue

        return {"success": False, "error": "所有模型都失敗"}

    # 測試故障轉移
    print("\n測試故障轉移:")
    models = [
        "gpt-4",  # 優先使用
        "gpt-3.5-turbo",  # 備用
        # "claude-3-sonnet-20240229",  # 第三選擇
    ]

    result = run_with_failover("你好", models)

    if result["success"]:
        print(f"\n最終使用: {result['model']}")
        print(f"回應: {result['response'][:100]}...")
    else:
        print(f"\n失敗: {result['error']}")


# ============================================================================
# 6. 配置最佳實踐
# ============================================================================

def configuration_best_practices():
    """配置最佳實踐"""
    print("\n" + "="*60)
    print("範例 9: 配置最佳實踐")
    print("="*60)

    print("""
最佳實踐：

1. 環境變量管理
   ✓ 使用 .env 文件
   ✓ 不要硬編碼 API 密鑰
   ✓ 分離開發/生產配置

   # .env
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=sk-ant-...
   GOOGLE_API_KEY=...
   DEFAULT_MODEL=gpt-4
   FALLBACK_MODEL=gpt-3.5-turbo

2. 成本控制
   ✓ 設置月度預算
   ✓ 監控 Token 使用
   ✓ 使用便宜模型處理簡單任務
   ✓ 實施請求限流

3. 性能優化
   ✓ 緩存常見問題答案
   ✓ 批量處理請求
   ✓ 使用流式輸出
   ✓ 設置合理的超時

4. 可靠性
   ✓ 實施重試機制
   ✓ 配置故障轉移
   ✓ 監控 API 健康狀態
   ✓ 記錄錯誤日誌

5. 安全性
   ✓ 密鑰輪換
   ✓ 最小權限原則
   ✓ 審計日誌
   ✓ 輸入輸出驗證

示例配置類：
    """)

    print("""
class LLMConfig:
    def __init__(self):
        self.primary_model = os.getenv("PRIMARY_MODEL", "gpt-4")
        self.fallback_model = os.getenv("FALLBACK_MODEL", "gpt-3.5-turbo")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "2000"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        self.timeout = int(os.getenv("TIMEOUT", "60"))

    def get_model_for_task(self, task_type: str) -> str:
        # 根據任務類型選擇模型
        ...

config = LLMConfig()
    """)


# ============================================================================
# 主程序
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*60)
    print("開始測試 LiteLLM 整合")
    print("="*60)

    try:
        test_openai()
        test_claude()
        test_gemini()
        test_ollama()
        compare_models()
        cost_comparison()
        intelligent_routing()
        failover_example()
        configuration_best_practices()
    except Exception as e:
        print(f"\n錯誤: {e}")
        print("注意：某些範例需要對應的 API 密鑰")

    print("\n" + "="*60)
    print("LiteLLM 整合指南完成！")
    print("="*60)

    print("""
總結：

✓ LiteLLM 讓 Agents SDK 支持 100+ 模型
✓ 統一接口，輕鬆切換
✓ 成本優化，選擇最佳模型
✓ 提高可靠性，故障轉移
✓ 避免供應商鎖定

下一步：
1. 設置多個 API 密鑰
2. 實驗不同模型表現
3. 實施智能路由策略
4. 監控成本和性能
5. 建立故障轉移機制
    """)


if __name__ == "__main__":
    main()
