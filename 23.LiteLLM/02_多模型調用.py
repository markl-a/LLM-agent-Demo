"""
LiteLLM 多模型調用範例
======================

這個範例展示如何在 LiteLLM 中使用多個模型和提供商：
1. 同時調用多個不同的模型
2. 比較不同模型的回應
3. 使用 Router 進行智能路由
4. 模型效能比較

LiteLLM 的優勢之一就是可以輕鬆切換和比較不同的模型。
"""

import os
from litellm import completion, Router
import time
import asyncio
from typing import List, Dict
import litellm

# 啟用詳細日誌
litellm.set_verbose = False


def compare_models():
    """比較不同模型對相同問題的回應"""
    print("=" * 60)
    print("範例 1: 比較不同模型的回應")
    print("=" * 60)

    # 定義要測試的模型
    models = [
        "gpt-3.5-turbo",
        "gpt-4",
        # "claude-3-sonnet-20240229",  # 需要 Anthropic API key
        # "gemini-pro",  # 需要 Google API key
    ]

    prompt = "用一句話解釋量子計算"

    results = {}

    for model in models:
        try:
            print(f"\n測試模型: {model}")
            start_time = time.time()

            response = completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            elapsed_time = time.time() - start_time

            results[model] = {
                "response": response.choices[0].message.content,
                "time": elapsed_time,
                "tokens": response.usage.total_tokens
            }

            print(f"回應: {results[model]['response']}")
            print(f"耗時: {elapsed_time:.2f} 秒")
            print(f"Token 使用: {results[model]['tokens']}")

        except Exception as e:
            print(f"錯誤 ({model}): {e}")
            results[model] = {"error": str(e)}

    # 總結比較
    print("\n" + "=" * 60)
    print("比較總結")
    print("=" * 60)
    for model, data in results.items():
        if "error" not in data:
            print(f"\n{model}:")
            print(f"  回應長度: {len(data['response'])} 字元")
            print(f"  速度: {data['time']:.2f} 秒")
            print(f"  Token: {data['tokens']}")


def use_router_basic():
    """使用 Router 進行基本的模型路由"""
    print("\n" + "=" * 60)
    print("範例 2: 使用 Router 進行模型路由")
    print("=" * 60)

    # 定義模型列表
    model_list = [
        {
            "model_name": "gpt-3.5",  # 路由器中使用的名稱
            "litellm_params": {
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY"),
            }
        },
        {
            "model_name": "gpt-4",
            "litellm_params": {
                "model": "gpt-4",
                "api_key": os.getenv("OPENAI_API_KEY"),
            }
        },
    ]

    # 創建路由器
    router = Router(model_list=model_list)

    try:
        # 使用路由器進行調用
        response = router.completion(
            model="gpt-3.5",  # 使用 model_name
            messages=[{"role": "user", "content": "Hi, how are you?"}]
        )

        print(f"回應: {response.choices[0].message.content}")

    except Exception as e:
        print(f"錯誤: {e}")


def use_router_with_fallback():
    """使用 Router 實現故障轉移"""
    print("\n" + "=" * 60)
    print("範例 3: Router 故障轉移機制")
    print("=" * 60)

    # 配置多個部署作為備援
    model_list = [
        {
            "model_name": "my-model",
            "litellm_params": {
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY"),
            }
        },
        {
            "model_name": "my-model",  # 相同的 model_name 作為備援
            "litellm_params": {
                "model": "gpt-4",  # 備援模型
                "api_key": os.getenv("OPENAI_API_KEY"),
            }
        },
    ]

    # 創建具有重試功能的路由器
    router = Router(
        model_list=model_list,
        fallbacks=[{"gpt-3.5-turbo": ["gpt-4"]}],  # 如果 GPT-3.5 失敗，使用 GPT-4
        num_retries=3,  # 重試次數
        timeout=30,  # 超時時間（秒）
    )

    try:
        response = router.completion(
            model="my-model",
            messages=[{"role": "user", "content": "Hello!"}]
        )

        print(f"成功回應: {response.choices[0].message.content}")
        print(f"使用的模型: {response.model}")

    except Exception as e:
        print(f"錯誤: {e}")


def model_group_routing():
    """使用模型組進行智能路由"""
    print("\n" + "=" * 60)
    print("範例 4: 模型組智能路由")
    print("=" * 60)

    # 定義模型組 - 相同的 model_name 會自動進行負載均衡
    model_list = [
        # GPT-3.5 組 - 用於快速、便宜的請求
        {
            "model_name": "fast-model",
            "litellm_params": {
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
            "model_info": {"id": "gpt-3.5-deployment-1"}
        },
        {
            "model_name": "fast-model",
            "litellm_params": {
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
            "model_info": {"id": "gpt-3.5-deployment-2"}
        },
        # GPT-4 組 - 用於複雜的任務
        {
            "model_name": "smart-model",
            "litellm_params": {
                "model": "gpt-4",
                "api_key": os.getenv("OPENAI_API_KEY"),
            }
        },
    ]

    router = Router(
        model_list=model_list,
        routing_strategy="simple-shuffle",  # 隨機選擇
    )

    try:
        # 使用快速模型處理簡單請求
        print("使用 fast-model 處理簡單請求...")
        response1 = router.completion(
            model="fast-model",
            messages=[{"role": "user", "content": "Say hi"}]
        )
        print(f"回應: {response1.choices[0].message.content}")

        # 使用智能模型處理複雜請求
        print("\n使用 smart-model 處理複雜請求...")
        response2 = router.completion(
            model="smart-model",
            messages=[{"role": "user", "content": "Explain quantum entanglement"}]
        )
        print(f"回應: {response2.choices[0].message.content}")

    except Exception as e:
        print(f"錯誤: {e}")


def multi_provider_setup():
    """配置多個提供商的範例"""
    print("\n" + "=" * 60)
    print("範例 5: 多提供商配置")
    print("=" * 60)

    model_list = [
        # OpenAI
        {
            "model_name": "openai-gpt",
            "litellm_params": {
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY"),
            }
        },
        # Anthropic Claude (需要 API key)
        # {
        #     "model_name": "claude",
        #     "litellm_params": {
        #         "model": "claude-3-sonnet-20240229",
        #         "api_key": os.getenv("ANTHROPIC_API_KEY"),
        #     }
        # },
        # Azure OpenAI (需要配置)
        # {
        #     "model_name": "azure-gpt",
        #     "litellm_params": {
        #         "model": "azure/your-deployment",
        #         "api_key": os.getenv("AZURE_API_KEY"),
        #         "api_base": os.getenv("AZURE_API_BASE"),
        #         "api_version": "2024-02-15-preview"
        #     }
        # },
        # Cohere (需要 API key)
        # {
        #     "model_name": "cohere-cmd",
        #     "litellm_params": {
        #         "model": "command-nightly",
        #         "api_key": os.getenv("COHERE_API_KEY"),
        #     }
        # },
    ]

    router = Router(model_list=model_list)

    # 測試每個提供商
    for model_config in model_list:
        model_name = model_config["model_name"]
        try:
            print(f"\n測試 {model_name}...")
            response = router.completion(
                model=model_name,
                messages=[{"role": "user", "content": "Hello from LiteLLM!"}]
            )
            print(f"成功: {response.choices[0].message.content[:100]}...")

        except Exception as e:
            print(f"錯誤 ({model_name}): {e}")


async def async_multiple_calls():
    """異步並發調用多個模型"""
    print("\n" + "=" * 60)
    print("範例 6: 異步並發調用多個模型")
    print("=" * 60)

    from litellm import acompletion

    models = ["gpt-3.5-turbo", "gpt-4"]
    prompt = "What is AI? Answer in one sentence."

    async def call_model(model: str):
        """異步調用單個模型"""
        try:
            start_time = time.time()
            response = await acompletion(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            elapsed = time.time() - start_time

            return {
                "model": model,
                "response": response.choices[0].message.content,
                "time": elapsed
            }
        except Exception as e:
            return {"model": model, "error": str(e)}

    # 並發調用所有模型
    try:
        tasks = [call_model(model) for model in models]
        results = await asyncio.gather(*tasks)

        # 顯示結果
        for result in results:
            if "error" in result:
                print(f"\n{result['model']}: 錯誤 - {result['error']}")
            else:
                print(f"\n{result['model']}:")
                print(f"  回應: {result['response']}")
                print(f"  耗時: {result['time']:.2f} 秒")

    except Exception as e:
        print(f"錯誤: {e}")


def model_performance_test():
    """測試不同模型的性能"""
    print("\n" + "=" * 60)
    print("範例 7: 模型性能測試")
    print("=" * 60)

    test_cases = [
        {
            "name": "簡單問答",
            "messages": [{"role": "user", "content": "What is 2+2?"}]
        },
        {
            "name": "創意寫作",
            "messages": [{"role": "user", "content": "Write a haiku about programming"}]
        },
        {
            "name": "代碼生成",
            "messages": [{"role": "user", "content": "Write a Python function to reverse a string"}]
        },
    ]

    models = ["gpt-3.5-turbo"]  # 可以添加更多模型

    for test in test_cases:
        print(f"\n測試案例: {test['name']}")
        print("-" * 40)

        for model in models:
            try:
                start_time = time.time()
                response = completion(
                    model=model,
                    messages=test["messages"],
                    temperature=0.7
                )
                elapsed = time.time() - start_time

                print(f"\n{model}:")
                print(f"  回應: {response.choices[0].message.content[:100]}...")
                print(f"  速度: {elapsed:.2f} 秒")
                print(f"  Tokens: {response.usage.total_tokens}")

            except Exception as e:
                print(f"  錯誤: {e}")


def router_with_weights():
    """使用權重進行負載均衡"""
    print("\n" + "=" * 60)
    print("範例 8: 使用權重的負載均衡")
    print("=" * 60)

    # 配置不同的部署與權重
    model_list = [
        {
            "model_name": "balanced-model",
            "litellm_params": {
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
            "rpm": 6000,  # 每分鐘請求數限制
        },
        {
            "model_name": "balanced-model",
            "litellm_params": {
                "model": "gpt-4",
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
            "rpm": 3000,  # GPT-4 限制較低
        },
    ]

    router = Router(
        model_list=model_list,
        routing_strategy="usage-based-routing",  # 基於使用量的路由
    )

    try:
        # 發送多個請求，觀察路由分配
        for i in range(3):
            response = router.completion(
                model="balanced-model",
                messages=[{"role": "user", "content": f"Request {i+1}"}]
            )
            print(f"請求 {i+1}: {response.model}")

    except Exception as e:
        print(f"錯誤: {e}")


def main():
    """主函數：運行所有範例"""
    print("\n" + "=" * 60)
    print("LiteLLM 多模型調用範例")
    print("=" * 60)

    compare_models()
    use_router_basic()
    use_router_with_fallback()
    model_group_routing()
    multi_provider_setup()

    # 異步範例需要特殊處理
    print("\n執行異步範例...")
    try:
        asyncio.run(async_multiple_calls())
    except Exception as e:
        print(f"異步範例錯誤: {e}")

    model_performance_test()
    router_with_weights()

    print("\n" + "=" * 60)
    print("所有範例執行完畢！")
    print("=" * 60)


if __name__ == "__main__":
    main()
