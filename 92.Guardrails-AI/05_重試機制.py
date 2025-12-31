"""
Guardrails AI - 重試機制示例
展示如何配置和使用自動重試與修正策略
"""

import os
import time
from guardrails import Guard
from guardrails.hub import ValidLength, RegexMatch, ValidChoices
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


def basic_retry_example():
    """
    基本重試示例：驗證失敗時自動重試
    """
    print("=" * 60)
    print("基本重試示例")
    print("=" * 60)

    # on_fail="reask" 會在驗證失敗時重新詢問 LLM
    guard = Guard().use(
        ValidLength(min=20, max=50, on_fail="reask")
    )

    prompt = "用一句話描述雲計算"

    print(f"\n提示: {prompt}")
    print("驗證要求: 長度在 20-50 字符之間")
    print("\n開始執行（可能會自動重試）...")

    start_time = time.time()

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=100,
            num_reasks=3  # 最多重試 3 次
        )

        elapsed_time = time.time() - start_time

        print(f"\n✅ 驗證成功！")
        print(f"最終輸出: {result.validated_output}")
        print(f"輸出長度: {len(result.validated_output)}")
        print(f"總耗時: {elapsed_time:.2f} 秒")

        # 顯示重試歷史
        if hasattr(result, 'reask_history') and result.reask_history:
            print(f"\n重試次數: {len(result.reask_history)}")
            for i, reask in enumerate(result.reask_history, 1):
                print(f"  第 {i} 次重試原因: {reask.get('reason', 'N/A')}")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def retry_with_max_attempts():
    """
    限制最大重試次數
    """
    print("\n" + "=" * 60)
    print("限制重試次數示例")
    print("=" * 60)

    guard = Guard().use(
        RegexMatch(regex="^[0-9]+$", on_fail="reask")  # 只接受數字
    )

    prompt = "生成一個純數字的字符串（只包含數字，不要其他字符）"

    print(f"\n提示: {prompt}")
    print("驗證要求: 只包含數字字符")
    print("最大重試次數: 2")

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=20,
            num_reasks=2  # 最多重試 2 次
        )

        print(f"\n✅ 驗證成功！")
        print(f"輸出: {result.validated_output}")

    except Exception as e:
        print(f"❌ 達到最大重試次數或驗證失敗")
        print(f"錯誤: {str(e)}")


def retry_with_fix_strategy():
    """
    使用修復策略而非重試
    """
    print("\n" + "=" * 60)
    print("修復策略示例")
    print("=" * 60)

    # on_fail="fix" 會嘗試自動修復而不是重試
    guard = Guard().use(
        ValidLength(min=10, max=30, on_fail="fix")
    )

    prompt = "生成一個簡短的句子"

    print(f"\n提示: {prompt}")
    print("驗證要求: 長度 10-30 字符")
    print("策略: 自動修復（而非重試）")

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=100,
        )

        print(f"\n✅ 處理完成！")
        print(f"輸出: {result.validated_output}")
        print(f"長度: {len(result.validated_output)}")

        if hasattr(result, 'fixed_output') and result.fixed_output:
            print("（輸出已被自動修復）")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def retry_with_filter_strategy():
    """
    使用過濾策略
    """
    print("\n" + "=" * 60)
    print("過濾策略示例")
    print("=" * 60)

    # on_fail="filter" 會過濾掉不符合要求的部分
    guard = Guard().use(
        RegexMatch(regex="[A-Za-z]+", on_fail="filter")
    )

    prompt = "生成包含字母和數字的混合文本"

    print(f"\n提示: {prompt}")
    print("策略: 過濾掉非字母字符")

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=100,
        )

        print(f"\n✅ 處理完成！")
        print(f"過濾後的輸出: {result.validated_output}")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def retry_with_custom_prompt():
    """
    自定義重試提示詞
    """
    print("\n" + "=" * 60)
    print("自定義重試提示詞示例")
    print("=" * 60)

    guard = Guard().use(
        ValidChoices(
            choices=["red", "green", "blue", "yellow"],
            on_fail="reask"
        )
    )

    prompt = "從顏色列表中選擇一個：red, green, blue, yellow（只返回顏色名稱）"
    reask_prompt = "請重新選擇，必須是以下之一：red, green, blue, yellow"

    print(f"\n初始提示: {prompt}")
    print(f"重試提示: {reask_prompt}")

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=20,
            num_reasks=2,
            reask_prompt=reask_prompt
        )

        print(f"\n✅ 驗證成功！")
        print(f"選擇的顏色: {result.validated_output}")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def progressive_retry():
    """
    漸進式重試：逐步放寬限制
    """
    print("\n" + "=" * 60)
    print("漸進式重試示例")
    print("=" * 60)

    # 嚴格的初始驗證
    strict_guard = Guard().use(
        ValidLength(min=30, max=40, on_fail="reask")
    )

    # 寬鬆的備用驗證
    lenient_guard = Guard().use(
        ValidLength(min=20, max=60, on_fail="reask")
    )

    prompt = "用一句話描述機器學習"

    print(f"\n提示: {prompt}")
    print("策略: 先嘗試嚴格驗證，失敗後使用寬鬆驗證")

    # 首先嘗試嚴格驗證
    print("\n第一階段: 嚴格驗證（30-40 字符）")
    try:
        result = strict_guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=100,
            num_reasks=1
        )

        print(f"✅ 嚴格驗證通過！")
        print(f"輸出: {result.validated_output}")
        print(f"長度: {len(result.validated_output)}")

    except Exception as e:
        print(f"⚠️  嚴格驗證失敗，嘗試寬鬆驗證...")

        # 使用寬鬆驗證
        print("\n第二階段: 寬鬆驗證（20-60 字符）")
        try:
            result = lenient_guard(
                llm_api=openai.chat.completions.create,
                prompt=prompt,
                model="gpt-3.5-turbo",
                max_tokens=150,
                num_reasks=2
            )

            print(f"✅ 寬鬆驗證通過！")
            print(f"輸出: {result.validated_output}")
            print(f"長度: {len(result.validated_output)}")

        except Exception as e2:
            print(f"❌ 所有驗證都失敗: {str(e2)}")


def retry_with_timeout():
    """
    帶超時的重試
    """
    print("\n" + "=" * 60)
    print("帶超時的重試示例")
    print("=" * 60)

    guard = Guard().use(
        ValidLength(min=15, max=25, on_fail="reask")
    )

    prompt = "生成一個 15-25 字符的句子"

    print(f"\n提示: {prompt}")
    print("超時限制: 10 秒")

    start_time = time.time()
    timeout = 10  # 10 秒超時

    try:
        # 這裡我們手動實現超時邏輯
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=100,
            num_reasks=5
        )

        elapsed = time.time() - start_time

        if elapsed > timeout:
            print(f"⚠️  超時（{elapsed:.2f} 秒）")
        else:
            print(f"✅ 在時限內完成（{elapsed:.2f} 秒）")
            print(f"輸出: {result.validated_output}")

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ 執行時間: {elapsed:.2f} 秒")
        print(f"錯誤: {str(e)}")


def retry_statistics():
    """
    重試統計信息
    """
    print("\n" + "=" * 60)
    print("重試統計示例")
    print("=" * 60)

    guard = Guard().use(
        ValidLength(min=18, max=22, on_fail="reask")
    )

    prompt = "生成一個恰好 20 字符左右的句子"

    print(f"\n提示: {prompt}")
    print("收集重試統計信息...")

    attempts = 0
    max_attempts = 4

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=100,
            num_reasks=max_attempts
        )

        print(f"\n✅ 驗證成功！")
        print(f"最終輸出: {result.validated_output}")
        print(f"長度: {len(result.validated_output)}")

        # 顯示統計
        print(f"\n📊 統計信息:")
        print(f"最大允許嘗試次數: {max_attempts + 1}")

        if hasattr(result, 'call_log'):
            print(f"實際 API 調用次數: {len(result.call_log)}")

    except Exception as e:
        print(f"❌ 達到最大重試次數")
        print(f"錯誤: {str(e)}")


def main():
    """
    主函數：運行所有重試機制示例
    """
    print("\n🛡️  Guardrails AI - 重試機制")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        return

    # 運行各種重試示例
    basic_retry_example()
    retry_with_max_attempts()
    retry_with_fix_strategy()
    retry_with_filter_strategy()
    retry_with_custom_prompt()
    progressive_retry()
    retry_with_timeout()
    retry_statistics()

    print("\n" + "=" * 60)
    print("✅ 所有重試機制示例執行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
