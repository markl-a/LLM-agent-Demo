"""
LiteLLM 多供應商支援範例

這個檔案展示如何使用 LiteLLM 整合多個 LLM 供應商：
1. OpenAI (GPT-4, GPT-3.5)
2. Anthropic (Claude)
3. AWS Bedrock (多種模型)
4. Google (Gemini)
5. Azure OpenAI
6. Cohere
7. 本地模型 (Ollama)
8. 供應商間的動態切換
9. 成本比較和優化
10. 統一的錯誤處理

LiteLLM 的最大優勢是提供統一的介面來呼叫所有這些供應商。
"""

import os
from typing import List, Dict, Any, Optional, Tuple
import json
from litellm import completion, cost_per_token
import time
from dataclasses import dataclass
from datetime import datetime


# ============================================================================
# 資料類別定義
# ============================================================================

@dataclass
class ModelConfig:
    """模型配置類別"""
    name: str  # 模型名稱
    provider: str  # 供應商
    cost_per_1k_prompt: float  # 每 1K prompt tokens 的成本（美元）
    cost_per_1k_completion: float  # 每 1K completion tokens 的成本（美元）
    max_tokens: int  # 最大 token 數
    supports_streaming: bool  # 是否支援串流
    supports_function_calling: bool  # 是否支援函數呼叫


# ============================================================================
# 第一部分：OpenAI 整合
# ============================================================================

def openai_examples():
    """
    OpenAI 模型整合範例

    支援的模型包括：
    - GPT-4o
    - GPT-4 Turbo
    - GPT-3.5 Turbo
    """
    print("=" * 80)
    print("OpenAI 模型整合")
    print("=" * 80)

    # OpenAI 模型列表
    openai_models = [
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
    ]

    prompt = "用一句話解釋量子計算"

    for model in openai_models:
        print(f"\n模型：{model}")
        print("-" * 40)

        try:
            start_time = time.time()

            response = completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )

            end_time = time.time()
            duration = end_time - start_time

            content = response.choices[0].message.content
            usage = response.usage

            print(f"回應：{content}")
            print(f"\n統計：")
            print(f"  - 延遲：{duration:.2f} 秒")
            print(f"  - Prompt tokens：{usage.prompt_tokens}")
            print(f"  - Completion tokens：{usage.completion_tokens}")
            print(f"  - 總計 tokens：{usage.total_tokens}")

        except Exception as e:
            print(f"錯誤：{e}")


def openai_advanced_features():
    """
    OpenAI 進階功能範例

    包括：
    - Vision（影像理解）
    - Function Calling（函數呼叫）
    - JSON Mode（JSON 模式）
    """
    print("\n" + "=" * 80)
    print("OpenAI 進階功能")
    print("=" * 80)

    # 1. JSON Mode
    print("\n1. JSON Mode 範例：")
    print("-" * 40)

    try:
        response = completion(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": "請提供三個程式語言的資訊，包括名稱、類型和主要用途"
                }
            ],
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        print("JSON 回應：")
        print(json.dumps(json.loads(content), indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"錯誤：{e}")

    # 2. Function Calling
    print("\n2. Function Calling 範例：")
    print("-" * 40)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "取得指定城市的當前天氣",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "城市名稱，例如：台北"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "溫度單位"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ]

    try:
        response = completion(
            model="gpt-4o",
            messages=[{"role": "user", "content": "台北現在天氣如何？"}],
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message

        if hasattr(message, 'tool_calls') and message.tool_calls:
            tool_call = message.tool_calls[0]
            print(f"函數名稱：{tool_call.function.name}")
            print(f"參數：{tool_call.function.arguments}")
        else:
            print(f"一般回應：{message.content}")

    except Exception as e:
        print(f"錯誤：{e}")


# ============================================================================
# 第二部分：Anthropic Claude 整合
# ============================================================================

def anthropic_examples():
    """
    Anthropic Claude 模型整合範例

    支援的模型包括：
    - Claude 3.5 Sonnet
    - Claude 3 Opus
    - Claude 3 Sonnet
    - Claude 3 Haiku
    """
    print("\n" + "=" * 80)
    print("Anthropic Claude 模型整合")
    print("=" * 80)

    # Claude 模型列表
    claude_models = [
        "claude-3-5-sonnet-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ]

    prompt = "解釋機器學習和深度學習的差異"

    for model in claude_models:
        print(f"\n模型：{model}")
        print("-" * 40)

        try:
            start_time = time.time()

            response = completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )

            end_time = time.time()
            duration = end_time - start_time

            content = response.choices[0].message.content
            usage = response.usage

            print(f"回應：{content[:200]}...")
            print(f"\n統計：")
            print(f"  - 延遲：{duration:.2f} 秒")
            print(f"  - Prompt tokens：{usage.prompt_tokens}")
            print(f"  - Completion tokens：{usage.completion_tokens}")

        except Exception as e:
            print(f"錯誤：{e}")


def claude_system_prompts():
    """
    Claude 特色：強大的系統提示詞支援

    Claude 對系統提示詞的處理特別好，可以用來精確控制行為。
    """
    print("\n" + "=" * 80)
    print("Claude 系統提示詞範例")
    print("=" * 80)

    system_prompts = {
        "技術文件撰寫": """你是一位專業的技術文件撰寫專家。
        請遵循以下準則：
        1. 使用清晰、準確的技術語言
        2. 提供具體的程式碼範例
        3. 包含使用注意事項
        4. 結構化組織內容""",

        "程式碼審查": """你是一位資深的程式碼審查專家。
        審查程式碼時請關注：
        1. 程式碼品質和可讀性
        2. 潛在的錯誤和邊界情況
        3. 效能優化建議
        4. 安全性問題""",

        "創意寫作": """你是一位富有創意的作家。
        寫作時請：
        1. 使用生動的描述
        2. 創造有趣的情節
        3. 保持故事連貫性
        4. 加入適當的情感元素"""
    }

    for task, system_msg in system_prompts.items():
        print(f"\n任務：{task}")
        print("-" * 40)

        try:
            response = completion(
                model="claude-3-5-sonnet-20241022",
                messages=[
                    {"role": "system", "content": system_msg},
                    {
                        "role": "user",
                        "content": "請展示一個簡單的 Python 範例"
                    }
                ],
                max_tokens=300
            )

            content = response.choices[0].message.content
            print(f"{content}\n")

        except Exception as e:
            print(f"錯誤：{e}")


# ============================================================================
# 第三部分：AWS Bedrock 整合
# ============================================================================

def aws_bedrock_examples():
    """
    AWS Bedrock 模型整合範例

    Bedrock 提供多個基礎模型的託管服務，包括：
    - Anthropic Claude
    - Meta Llama
    - Amazon Titan
    - AI21 Jurassic
    """
    print("\n" + "=" * 80)
    print("AWS Bedrock 模型整合")
    print("=" * 80)

    # Bedrock 模型列表
    bedrock_models = [
        "bedrock/anthropic.claude-3-sonnet-20240229-v1:0",
        "bedrock/anthropic.claude-3-haiku-20240307-v1:0",
        # "bedrock/meta.llama3-70b-instruct-v1:0",
        # "bedrock/amazon.titan-text-express-v1",
    ]

    prompt = "什麼是雲端運算？"

    for model in bedrock_models:
        print(f"\n模型：{model}")
        print("-" * 40)

        try:
            # Bedrock 需要 AWS 憑證
            response = completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                # AWS 區域可以透過環境變數或參數指定
                aws_region_name="us-east-1"
            )

            content = response.choices[0].message.content
            print(f"回應：{content}")

        except Exception as e:
            print(f"錯誤：{e}")
            print("提示：確保已設定 AWS 憑證（AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY）")


def bedrock_streaming_example():
    """
    AWS Bedrock 串流回應範例
    """
    print("\n" + "=" * 80)
    print("Bedrock 串流回應範例")
    print("=" * 80)

    try:
        print("\n開始串流回應...\n")

        response = completion(
            model="bedrock/anthropic.claude-3-haiku-20240307-v1:0",
            messages=[
                {
                    "role": "user",
                    "content": "寫一首關於人工智慧的短詩"
                }
            ],
            stream=True,
            aws_region_name="us-east-1"
        )

        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content

        print("\n\n串流完成！")
        print(f"完整回應長度：{len(full_response)} 字元")

    except Exception as e:
        print(f"錯誤：{e}")


# ============================================================================
# 第四部分：Google Gemini 整合
# ============================================================================

def google_gemini_examples():
    """
    Google Gemini 模型整合範例
    """
    print("\n" + "=" * 80)
    print("Google Gemini 模型整合")
    print("=" * 80)

    gemini_models = [
        "gemini-pro",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
    ]

    prompt = "解釋什麼是自然語言處理"

    for model in gemini_models:
        print(f"\n模型：{model}")
        print("-" * 40)

        try:
            response = completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )

            content = response.choices[0].message.content
            usage = response.usage

            print(f"回應：{content}")
            print(f"\nTokens 使用：{usage.total_tokens}")

        except Exception as e:
            print(f"錯誤：{e}")


# ============================================================================
# 第五部分：Azure OpenAI 整合
# ============================================================================

def azure_openai_examples():
    """
    Azure OpenAI 服務整合範例

    Azure OpenAI 需要特殊的配置，包括：
    - API 金鑰
    - API 基礎 URL
    - API 版本
    - 部署名稱
    """
    print("\n" + "=" * 80)
    print("Azure OpenAI 整合")
    print("=" * 80)

    # Azure OpenAI 配置
    azure_config = {
        "model": "azure/gpt-4",  # azure/ 前綴表示使用 Azure
        "api_base": os.environ.get("AZURE_API_BASE", "https://your-resource.openai.azure.com"),
        "api_key": os.environ.get("AZURE_API_KEY", "your-api-key"),
        "api_version": "2024-02-01"
    }

    print(f"\nAzure 配置：")
    print(f"  - API Base：{azure_config['api_base']}")
    print(f"  - API Version：{azure_config['api_version']}")

    try:
        response = completion(
            model=azure_config["model"],
            messages=[
                {"role": "user", "content": "什麼是 Azure OpenAI Service？"}
            ],
            api_base=azure_config["api_base"],
            api_key=azure_config["api_key"],
            api_version=azure_config["api_version"],
            max_tokens=200
        )

        content = response.choices[0].message.content
        print(f"\n回應：{content}")

    except Exception as e:
        print(f"\n錯誤：{e}")
        print("提示：確保已正確設定 Azure OpenAI 配置")


# ============================================================================
# 第六部分：多供應商比較
# ============================================================================

def compare_providers():
    """
    比較不同供應商的模型表現

    這個函數會用相同的提示詞測試多個供應商，
    並比較回應品質、速度和成本。
    """
    print("\n" + "=" * 80)
    print("多供應商比較")
    print("=" * 80)

    # 定義要比較的模型
    models = [
        {"name": "gpt-4o", "provider": "OpenAI"},
        {"name": "gpt-3.5-turbo", "provider": "OpenAI"},
        {"name": "claude-3-5-sonnet-20241022", "provider": "Anthropic"},
        {"name": "claude-3-haiku-20240307", "provider": "Anthropic"},
    ]

    prompt = "用 50 字以內解釋區塊鏈技術"

    results = []

    for model_info in models:
        model = model_info["name"]
        provider = model_info["provider"]

        print(f"\n測試：{provider} - {model}")
        print("-" * 40)

        try:
            start_time = time.time()

            response = completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )

            end_time = time.time()
            duration = end_time - start_time

            content = response.choices[0].message.content
            usage = response.usage

            result = {
                "provider": provider,
                "model": model,
                "response": content,
                "duration": duration,
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens
            }

            results.append(result)

            print(f"回應：{content}")
            print(f"延遲：{duration:.2f} 秒")
            print(f"Tokens：{usage.total_tokens}")

        except Exception as e:
            print(f"錯誤：{e}")

    # 顯示比較摘要
    print("\n" + "=" * 80)
    print("比較摘要")
    print("=" * 80)

    if results:
        print("\n延遲排序（由快到慢）：")
        sorted_by_speed = sorted(results, key=lambda x: x["duration"])
        for i, r in enumerate(sorted_by_speed, 1):
            print(f"{i}. {r['provider']} {r['model']}: {r['duration']:.2f} 秒")

        print("\nToken 使用排序（由少到多）：")
        sorted_by_tokens = sorted(results, key=lambda x: x["total_tokens"])
        for i, r in enumerate(sorted_by_tokens, 1):
            print(f"{i}. {r['provider']} {r['model']}: {r['total_tokens']} tokens")


# ============================================================================
# 第七部分：成本分析
# ============================================================================

def cost_analysis():
    """
    分析不同供應商和模型的成本

    這對於優化 LLM 使用成本非常重要。
    """
    print("\n" + "=" * 80)
    print("成本分析")
    print("=" * 80)

    # 模型成本配置（每 1K tokens 的美元成本）
    model_costs = [
        {
            "model": "gpt-4o",
            "provider": "OpenAI",
            "input_cost": 0.005,
            "output_cost": 0.015
        },
        {
            "model": "gpt-3.5-turbo",
            "provider": "OpenAI",
            "input_cost": 0.0005,
            "output_cost": 0.0015
        },
        {
            "model": "claude-3-5-sonnet-20241022",
            "provider": "Anthropic",
            "input_cost": 0.003,
            "output_cost": 0.015
        },
        {
            "model": "claude-3-haiku-20240307",
            "provider": "Anthropic",
            "input_cost": 0.00025,
            "output_cost": 0.00125
        },
    ]

    # 假設的使用場景
    scenarios = [
        {"name": "簡短問答", "input_tokens": 100, "output_tokens": 50},
        {"name": "文章摘要", "input_tokens": 2000, "output_tokens": 200},
        {"name": "程式碼生成", "input_tokens": 500, "output_tokens": 1000},
        {"name": "長文本分析", "input_tokens": 5000, "output_tokens": 500},
    ]

    for scenario in scenarios:
        print(f"\n場景：{scenario['name']}")
        print(f"輸入：{scenario['input_tokens']} tokens，輸出：{scenario['output_tokens']} tokens")
        print("-" * 40)

        costs = []

        for model_cost in model_costs:
            # 計算成本
            input_cost = (scenario['input_tokens'] / 1000) * model_cost['input_cost']
            output_cost = (scenario['output_tokens'] / 1000) * model_cost['output_cost']
            total_cost = input_cost + output_cost

            costs.append({
                "model": model_cost['model'],
                "provider": model_cost['provider'],
                "cost": total_cost
            })

            print(f"{model_cost['provider']:12} {model_cost['model']:30} ${total_cost:.6f}")

        # 找出最便宜的選項
        cheapest = min(costs, key=lambda x: x['cost'])
        most_expensive = max(costs, key=lambda x: x['cost'])
        savings = ((most_expensive['cost'] - cheapest['cost']) / most_expensive['cost']) * 100

        print(f"\n最便宜：{cheapest['provider']} {cheapest['model']} (${cheapest['cost']:.6f})")
        print(f"相比最貴選項可節省：{savings:.1f}%")


# ============================================================================
# 第八部分：智慧路由
# ============================================================================

class SmartRouter:
    """
    智慧路由器：根據不同條件選擇最佳模型

    考慮因素：
    - 成本
    - 速度
    - 品質
    - 可用性
    """

    def __init__(self):
        self.model_configs = {
            "gpt-4o": {
                "cost": "high",
                "speed": "medium",
                "quality": "very_high",
                "max_tokens": 128000
            },
            "gpt-3.5-turbo": {
                "cost": "low",
                "speed": "fast",
                "quality": "medium",
                "max_tokens": 16385
            },
            "claude-3-5-sonnet-20241022": {
                "cost": "high",
                "speed": "medium",
                "quality": "very_high",
                "max_tokens": 200000
            },
            "claude-3-haiku-20240307": {
                "cost": "very_low",
                "speed": "very_fast",
                "quality": "medium",
                "max_tokens": 200000
            }
        }

    def select_model(
        self,
        priority: str = "balanced",
        estimated_tokens: int = 1000,
        quality_required: str = "medium"
    ) -> str:
        """
        根據需求選擇最佳模型

        Args:
            priority: 優先考量 ("cost", "speed", "quality", "balanced")
            estimated_tokens: 預估的 token 數量
            quality_required: 需要的品質等級 ("low", "medium", "high", "very_high")

        Returns:
            選中的模型名稱
        """
        if priority == "cost":
            # 優先選擇成本最低的模型
            return "claude-3-haiku-20240307"
        elif priority == "speed":
            # 優先選擇速度最快的模型
            return "claude-3-haiku-20240307"
        elif priority == "quality":
            # 優先選擇品質最高的模型
            return "gpt-4o"
        else:  # balanced
            # 平衡考量
            if quality_required in ["high", "very_high"]:
                return "claude-3-5-sonnet-20241022"
            else:
                return "gpt-3.5-turbo"

    def route_request(self, prompt: str, priority: str = "balanced") -> Dict[str, Any]:
        """路由請求到最佳模型"""
        # 預估 token 數（簡化版本）
        estimated_tokens = len(prompt.split()) * 1.3

        # 選擇模型
        selected_model = self.select_model(
            priority=priority,
            estimated_tokens=int(estimated_tokens)
        )

        print(f"智慧路由選擇：{selected_model}")
        print(f"原因：優先級 = {priority}，預估 tokens = {int(estimated_tokens)}")

        return {
            "model": selected_model,
            "estimated_tokens": int(estimated_tokens)
        }


def smart_routing_example():
    """展示智慧路由的使用"""
    print("\n" + "=" * 80)
    print("智慧路由範例")
    print("=" * 80)

    router = SmartRouter()

    # 不同的使用場景
    scenarios = [
        {
            "prompt": "什麼是 Python？",
            "priority": "cost",
            "description": "簡單問答，優先考慮成本"
        },
        {
            "prompt": "請詳細分析這個複雜的演算法...",
            "priority": "quality",
            "description": "複雜分析，優先考慮品質"
        },
        {
            "prompt": "快速回答：1+1=?",
            "priority": "speed",
            "description": "簡單計算，優先考慮速度"
        },
        {
            "prompt": "請幫我審查這段程式碼",
            "priority": "balanced",
            "description": "程式碼審查，平衡考量"
        }
    ]

    for scenario in scenarios:
        print(f"\n場景：{scenario['description']}")
        print("-" * 40)
        print(f"提示詞：{scenario['prompt']}")

        routing_result = router.route_request(
            prompt=scenario['prompt'],
            priority=scenario['priority']
        )

        try:
            response = completion(
                model=routing_result['model'],
                messages=[{"role": "user", "content": scenario['prompt']}],
                max_tokens=100
            )

            content = response.choices[0].message.content
            print(f"回應：{content}\n")

        except Exception as e:
            print(f"錯誤：{e}\n")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """主程式"""
    print("\n")
    print("=" * 80)
    print("LiteLLM 多供應商整合教學")
    print("=" * 80)
    print()

    # 執行範例（註解掉需要 API 金鑰的部分）
    # openai_examples()
    # openai_advanced_features()
    # anthropic_examples()
    # claude_system_prompts()
    # aws_bedrock_examples()
    # bedrock_streaming_example()
    # google_gemini_examples()
    # azure_openai_examples()

    # 比較和分析
    # compare_providers()
    cost_analysis()
    smart_routing_example()

    print("\n" + "=" * 80)
    print("教學完成！")
    print("=" * 80)
    print("\n重點回顧：")
    print("1. LiteLLM 支援 100+ 個 LLM 模型")
    print("2. 使用統一的介面呼叫不同供應商")
    print("3. 可以輕鬆比較不同模型的表現和成本")
    print("4. 智慧路由可以自動選擇最佳模型")
    print()


if __name__ == "__main__":
    main()
