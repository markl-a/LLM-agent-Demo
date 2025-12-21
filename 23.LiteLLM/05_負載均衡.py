"""
LiteLLM 負載均衡範例
====================

這個範例展示 LiteLLM Router 的負載均衡功能：
1. 基本的負載均衡配置
2. 不同的路由策略
3. RPM/TPM 限制
4. 權重分配
5. 故障轉移
6. Redis 分散式狀態
7. 健康檢查和熔斷器

Router 是 LiteLLM 的核心功能，提供智能路由和負載均衡。
"""

import os
from litellm import Router
import time
import asyncio
from typing import List

def basic_load_balancing():
    """基本的負載均衡配置"""
    print("=" * 60)
    print("範例 1: 基本負載均衡")
    print("=" * 60)

    # 配置多個相同模型的部署
    model_list = [
        {
            "model_name": "gpt-3.5",  # 邏輯模型名稱
            "litellm_params": {
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
            "model_info": {"id": "deployment-1"}  # 用於識別不同的部署
        },
        {
            "model_name": "gpt-3.5",  # 相同的名稱會自動負載均衡
            "litellm_params": {
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
            "model_info": {"id": "deployment-2"}
        },
        {
            "model_name": "gpt-3.5",
            "litellm_params": {
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
            "model_info": {"id": "deployment-3"}
        },
    ]

    # 創建路由器
    router = Router(model_list=model_list)

    try:
        print("\n發送多個請求，觀察負載分配...")

        for i in range(5):
            response = router.completion(
                model="gpt-3.5",
                messages=[{"role": "user", "content": f"Say hello #{i+1}"}]
            )

            # 顯示使用的部署
            print(f"請求 {i+1}: {response.choices[0].message.content[:50]}...")
            # 注意：實際使用的部署資訊可能在 response._hidden_params 中

    except Exception as e:
        print(f"錯誤: {e}")


def routing_strategies():
    """不同的路由策略"""
    print("\n" + "=" * 60)
    print("範例 2: 不同的路由策略")
    print("=" * 60)

    model_list = [
        {
            "model_name": "my-model",
            "litellm_params": {
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
            "model_info": {"id": "deployment-1", "latency": 0.1}
        },
        {
            "model_name": "my-model",
            "litellm_params": {
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
            "model_info": {"id": "deployment-2", "latency": 0.2}
        },
    ]

    # 測試不同的路由策略
    strategies = [
        "simple-shuffle",      # 隨機選擇（預設）
        "least-busy",          # 選擇最不繁忙的
        "usage-based-routing", # 基於使用量
        "latency-based-routing" # 基於延遲
    ]

    for strategy in strategies:
        try:
            print(f"\n測試策略: {strategy}")
            print("-" * 40)

            router = Router(
                model_list=model_list,
                routing_strategy=strategy
            )

            # 發送幾個請求
            for i in range(3):
                response = router.completion(
                    model="my-model",
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=10
                )
                print(f"  請求 {i+1} 完成")

        except Exception as e:
            print(f"  錯誤 ({strategy}): {e}")


def rpm_tpm_limits():
    """配置 RPM/TPM 限制"""
    print("\n" + "=" * 60)
    print("範例 3: RPM/TPM 限制配置")
    print("=" * 60)

    # 配置不同的速率限制
    model_list = [
        {
            "model_name": "limited-model",
            "litellm_params": {
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
            "rpm": 10,  # 每分鐘最多 10 個請求
            "tpm": 1000,  # 每分鐘最多 1000 個 tokens
            "model_info": {"id": "low-limit-deployment"}
        },
        {
            "model_name": "limited-model",
            "litellm_params": {
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
            "rpm": 100,  # 更高的限制
            "tpm": 10000,
            "model_info": {"id": "high-limit-deployment"}
        },
    ]

    router = Router(
        model_list=model_list,
        routing_strategy="usage-based-routing"  # 根據可用額度智能路由
    )

    try:
        print("\n發送請求，Router 會根據限制智能分配...")

        for i in range(5):
            response = router.completion(
                model="limited-model",
                messages=[{"role": "user", "content": "Quick test"}],
                max_tokens=20
            )
            print(f"請求 {i+1} 完成")

        print("\n✓ Router 自動處理了速率限制")

    except Exception as e:
        print(f"錯誤: {e}")


def weighted_routing():
    """基於權重的路由"""
    print("\n" + "=" * 60)
    print("範例 4: 權重路由")
    print("=" * 60)

    # 當設定 RPM 時，LiteLLM 會使用加權隨機選擇
    model_list = [
        {
            "model_name": "weighted-model",
            "litellm_params": {
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
            "rpm": 3000,  # 較低的權重
            "model_info": {"id": "weight-30"}
        },
        {
            "model_name": "weighted-model",
            "litellm_params": {
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
            "rpm": 7000,  # 較高的權重
            "model_info": {"id": "weight-70"}
        },
    ]

    router = Router(
        model_list=model_list,
        routing_strategy="usage-based-routing"
    )

    try:
        print("\n發送多個請求，觀察權重分配（70/30）...")

        deployment_counts = {}

        for i in range(10):
            response = router.completion(
                model="weighted-model",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )

            # 這裡簡化展示，實際需要從 response 中提取部署資訊
            print(f"請求 {i+1} 完成")

        print("\n理論上，deployment-2 應該收到約 70% 的請求")

    except Exception as e:
        print(f"錯誤: {e}")


def fallback_configuration():
    """配置故障轉移"""
    print("\n" + "=" * 60)
    print("範例 5: 故障轉移配置")
    print("=" * 60)

    model_list = [
        {
            "model_name": "primary-model",
            "litellm_params": {
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY"),
            }
        },
        {
            "model_name": "backup-model",
            "litellm_params": {
                "model": "gpt-4",  # 備用模型
                "api_key": os.getenv("OPENAI_API_KEY"),
            }
        },
    ]

    # 配置故障轉移：如果 primary 失敗，使用 backup
    router = Router(
        model_list=model_list,
        fallbacks=[{"gpt-3.5-turbo": ["gpt-4"]}],  # 故障轉移映射
        num_retries=2,  # 重試次數
        timeout=5,  # 超時時間（秒）
    )

    try:
        # 正常情況下使用 primary
        print("\n1. 正常請求（使用 primary）:")
        response = router.completion(
            model="primary-model",
            messages=[{"role": "user", "content": "Hello"}]
        )
        print(f"   成功: {response.choices[0].message.content[:50]}...")

        # 如果 primary 失敗（例如超時），會自動使用 backup
        print("\n2. 故障轉移機制:")
        print("   如果 primary-model 失敗，會自動切換到 backup-model")

    except Exception as e:
        print(f"錯誤: {e}")


def multiple_fallback_levels():
    """多層故障轉移"""
    print("\n" + "=" * 60)
    print("範例 6: 多層故障轉移")
    print("=" * 60)

    model_list = [
        {
            "model_name": "tier1",
            "litellm_params": {"model": "gpt-3.5-turbo", "api_key": os.getenv("OPENAI_API_KEY")}
        },
        {
            "model_name": "tier2",
            "litellm_params": {"model": "gpt-4", "api_key": os.getenv("OPENAI_API_KEY")}
        },
        # 可以添加更多層級
    ]

    router = Router(
        model_list=model_list,
        fallbacks=[
            {"gpt-3.5-turbo": ["gpt-4"]},  # 第一層備援
            # {"gpt-4": ["claude-3-sonnet-20240229"]},  # 第二層備援
        ],
        num_retries=3,
        retry_after=2,  # 重試前等待秒數
    )

    try:
        print("\n故障轉移鏈: GPT-3.5 → GPT-4 → ...")
        response = router.completion(
            model="tier1",
            messages=[{"role": "user", "content": "Test fallback"}]
        )
        print(f"成功: {response.choices[0].message.content[:50]}...")

    except Exception as e:
        print(f"錯誤: {e}")


def cooldown_configuration():
    """熔斷器（Cooldown）配置"""
    print("\n" + "=" * 60)
    print("範例 7: 熔斷器配置")
    print("=" * 60)

    model_list = [
        {
            "model_name": "auto-recovery",
            "litellm_params": {
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY"),
            }
        },
    ]

    router = Router(
        model_list=model_list,
        # 熔斷器設定
        allowed_fails=3,  # 允許失敗次數
        cooldown_time=60,  # 冷卻時間（秒）
    )

    print("\n熔斷器配置:")
    print("  - 允許失敗: 3 次")
    print("  - 冷卻時間: 60 秒")
    print("  - 如果部署連續失敗 3 次，將被暫時移除 60 秒")
    print("  - 冷卻期後自動恢復")

    try:
        response = router.completion(
            model="auto-recovery",
            messages=[{"role": "user", "content": "Test"}]
        )
        print(f"\n正常請求: {response.choices[0].message.content[:50]}...")

    except Exception as e:
        print(f"錯誤: {e}")


def redis_distributed_state():
    """使用 Redis 進行分散式狀態管理"""
    print("\n" + "=" * 60)
    print("範例 8: Redis 分散式狀態")
    print("=" * 60)

    print("\n配置範例:")
    print("""
    # 在多個 LiteLLM 實例之間共享狀態
    router = Router(
        model_list=model_list,
        redis_host="localhost",      # Redis 主機
        redis_port=6379,              # Redis 端口
        redis_password="your-pass",   # Redis 密碼（如果有）
        routing_strategy="usage-based-routing"
    )

    使用場景:
    1. Kubernetes 多 Pod 部署
    2. 多伺服器負載均衡
    3. 共享 RPM/TPM 限制狀態
    4. 共享熔斷器狀態
    """)

    # 實際配置（需要 Redis）
    try:
        # model_list = [...]  # 您的模型列表

        # router = Router(
        #     model_list=model_list,
        #     redis_host=os.getenv("REDIS_HOST", "localhost"),
        #     redis_port=int(os.getenv("REDIS_PORT", 6379)),
        #     routing_strategy="usage-based-routing"
        # )

        print("\n注意: 此範例需要運行 Redis 服務器")

    except Exception as e:
        print(f"錯誤: {e}")


def router_with_retries():
    """配置重試邏輯"""
    print("\n" + "=" * 60)
    print("範例 9: 重試邏輯配置")
    print("=" * 60)

    model_list = [
        {
            "model_name": "retry-model",
            "litellm_params": {
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY"),
            }
        },
    ]

    router = Router(
        model_list=model_list,
        num_retries=3,  # 最多重試 3 次
        timeout=30,  # 每次請求超時 30 秒
        retry_after=2,  # 重試前等待 2 秒
        # 可以配置指數退避
        # context_window_fallbacks=[...]  # 處理 context 超出的情況
    )

    try:
        print("\n重試配置:")
        print("  - 最多重試: 3 次")
        print("  - 超時時間: 30 秒")
        print("  - 重試間隔: 2 秒")

        response = router.completion(
            model="retry-model",
            messages=[{"role": "user", "content": "Test retry logic"}]
        )

        print(f"\n成功: {response.choices[0].message.content[:50]}...")

    except Exception as e:
        print(f"錯誤（所有重試後）: {e}")


async def async_load_balancing():
    """異步負載均衡"""
    print("\n" + "=" * 60)
    print("範例 10: 異步負載均衡")
    print("=" * 60)

    model_list = [
        {
            "model_name": "async-model",
            "litellm_params": {
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
            "model_info": {"id": f"deployment-{i}"}
        }
        for i in range(3)
    ]

    router = Router(model_list=model_list)

    async def make_request(request_id: int):
        """發送異步請求"""
        try:
            response = await router.acompletion(
                model="async-model",
                messages=[{"role": "user", "content": f"Request {request_id}"}],
                max_tokens=20
            )
            return f"請求 {request_id} 完成"
        except Exception as e:
            return f"請求 {request_id} 失敗: {e}"

    try:
        # 並發發送多個請求
        tasks = [make_request(i) for i in range(10)]
        results = await asyncio.gather(*tasks)

        print("\n異步請求結果:")
        for result in results:
            print(f"  {result}")

        print("\n✓ Router 自動在多個部署之間分配了負載")

    except Exception as e:
        print(f"錯誤: {e}")


def health_check_example():
    """健康檢查配置"""
    print("\n" + "=" * 60)
    print("範例 11: 健康檢查")
    print("=" * 60)

    print("""
    Router 自動追蹤每個部署的健康狀態：

    1. 成功率監控
       - 追蹤每個部署的成功/失敗比率

    2. 延遲監控
       - 使用 latency-based-routing 時監控回應時間

    3. 自動熔斷
       - 失敗次數超過 allowed_fails 時觸發
       - 冷卻 cooldown_time 秒後自動恢復

    4. 故障轉移
       - 不健康的部署被跳過
       - 自動使用配置的 fallback 模型

    配置範例:
    router = Router(
        model_list=model_list,
        routing_strategy="latency-based-routing",
        allowed_fails=3,
        cooldown_time=60,
        fallbacks=[...],
        # 啟用健康檢查日誌
        set_verbose=True
    )
    """)


def advanced_router_config():
    """進階 Router 配置"""
    print("\n" + "=" * 60)
    print("範例 12: 進階配置綜合範例")
    print("=" * 60)

    model_list = [
        # 主要部署組
        {
            "model_name": "production",
            "litellm_params": {
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
            "rpm": 5000,
            "tpm": 80000,
            "model_info": {"id": "prod-1", "region": "us-east"}
        },
        {
            "model_name": "production",
            "litellm_params": {
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
            "rpm": 5000,
            "tpm": 80000,
            "model_info": {"id": "prod-2", "region": "eu-west"}
        },
        # 備用高級模型
        {
            "model_name": "premium",
            "litellm_params": {
                "model": "gpt-4",
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
            "rpm": 500,
            "tpm": 10000,
        },
    ]

    router = Router(
        model_list=model_list,

        # 路由策略
        routing_strategy="usage-based-routing",

        # 可靠性設定
        num_retries=3,
        timeout=30,
        retry_after=2,

        # 熔斷器
        allowed_fails=5,
        cooldown_time=120,

        # 故障轉移
        fallbacks=[{"gpt-3.5-turbo": ["gpt-4"]}],

        # Redis（如果需要分散式狀態）
        # redis_host="localhost",
        # redis_port=6379,

        # 日誌
        set_verbose=False,
    )

    try:
        print("\n進階配置已啟用:")
        print("  ✓ 使用量路由")
        print("  ✓ 3 次重試")
        print("  ✓ 熔斷器（5 次失敗，120 秒冷卻）")
        print("  ✓ 故障轉移到 GPT-4")
        print("  ✓ RPM/TPM 限制")

        response = router.completion(
            model="production",
            messages=[{"role": "user", "content": "Test production config"}]
        )

        print(f"\n成功回應: {response.choices[0].message.content[:50]}...")

    except Exception as e:
        print(f"錯誤: {e}")


def main():
    """主函數：運行所有範例"""
    print("\n" + "=" * 60)
    print("LiteLLM 負載均衡範例")
    print("=" * 60)

    basic_load_balancing()
    routing_strategies()
    rpm_tpm_limits()
    weighted_routing()
    fallback_configuration()
    multiple_fallback_levels()
    cooldown_configuration()
    redis_distributed_state()
    router_with_retries()
    health_check_example()
    advanced_router_config()

    # 異步範例
    print("\n執行異步範例...")
    try:
        asyncio.run(async_load_balancing())
    except Exception as e:
        print(f"異步範例錯誤: {e}")

    print("\n" + "=" * 60)
    print("所有範例執行完畢！")
    print("=" * 60)


if __name__ == "__main__":
    main()
