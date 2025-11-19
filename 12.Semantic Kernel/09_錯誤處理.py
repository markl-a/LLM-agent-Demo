#!/usr/bin/env python3
"""
Semantic Kernel - 錯誤處理與重試示例

本示例展示：
1. 基本錯誤處理
2. 自動重試機制
3. 超時處理
4. 錯誤恢復策略
"""

import asyncio
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

try:
    import semantic_kernel as sk
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
    from semantic_kernel.contents import ChatHistory
    from semantic_kernel.exceptions import ServiceResponseException
except ImportError:
    print("❌ 請安裝 Semantic Kernel:")
    print("   pip install semantic-kernel")
    exit(1)


async def example_basic_error_handling():
    """示例 1: 基本錯誤處理"""
    print("\n" + "=" * 60)
    print("示例 1: 基本錯誤處理")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()

    try:
        service = OpenAIChatCompletion(
            service_id="chat-gpt",
            ai_model_id="gpt-4o-mini",
            api_key=api_key,
        )
        kernel.add_service(service)

        chat_history = ChatHistory()
        chat_history.add_user_message("你好！")

        response = await service.get_chat_message_content(
            chat_history=chat_history, settings=None
        )

        print(f"✅ 成功: {response.content}")

    except ServiceResponseException as e:
        print(f"❌ 服務響應錯誤: {e}")
    except Exception as e:
        print(f"❌ 未知錯誤: {e}")


async def example_retry_mechanism():
    """示例 2: 自動重試機制"""
    print("\n" + "=" * 60)
    print("示例 2: 自動重試機制")
    print("=" * 60)

    async def call_with_retry(
        func, max_retries: int = 3, delay: float = 1.0
    ) -> Optional[str]:
        """帶重試的函數調用"""
        for attempt in range(max_retries):
            try:
                print(f"🔄 嘗試 {attempt + 1}/{max_retries}...")
                result = await func()
                print(f"✅ 成功!")
                return result

            except Exception as e:
                print(f"❌ 失敗: {e}")

                if attempt < max_retries - 1:
                    print(f"⏳ 等待 {delay} 秒後重試...")
                    await asyncio.sleep(delay)
                    delay *= 2  # 指數退避
                else:
                    print(f"❌ 達到最大重試次數")
                    return None

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    async def make_request():
        """發送請求"""
        chat_history = ChatHistory()
        chat_history.add_user_message("你好！")

        response = await service.get_chat_message_content(
            chat_history=chat_history, settings=None
        )
        return response.content

    result = await call_with_retry(make_request, max_retries=3)
    if result:
        print(f"\n📝 最終結果: {result}")


async def example_timeout_handling():
    """示例 3: 超時處理"""
    print("\n" + "=" * 60)
    print("示例 3: 超時處理")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    async def request_with_timeout(timeout: float = 10.0):
        """帶超時的請求"""
        chat_history = ChatHistory()
        chat_history.add_user_message("請詳細解釋量子計算")

        try:
            print(f"⏱️  設置超時: {timeout} 秒")

            response = await asyncio.wait_for(
                service.get_chat_message_content(
                    chat_history=chat_history, settings=None
                ),
                timeout=timeout,
            )

            print(f"✅ 成功: {response.content}")

        except asyncio.TimeoutError:
            print(f"❌ 請求超時（超過 {timeout} 秒）")
        except Exception as e:
            print(f"❌ 錯誤: {e}")

    await request_with_timeout(timeout=30.0)


async def example_fallback_strategy():
    """示例 4: 降級策略"""
    print("\n" + "=" * 60)
    print("示例 4: 降級策略")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()

    # 主服務
    primary_service = OpenAIChatCompletion(
        service_id="primary",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )

    # 備用服務（使用更快/便宜的模型）
    fallback_service = OpenAIChatCompletion(
        service_id="fallback",
        ai_model_id="gpt-4o-mini",  # 在實際中可以用更便宜的模型
        api_key=api_key,
    )

    kernel.add_service(primary_service)
    kernel.add_service(fallback_service)

    async def request_with_fallback(question: str) -> str:
        """帶降級的請求"""
        chat_history = ChatHistory()
        chat_history.add_user_message(question)

        # 嘗試主服務
        try:
            print("🎯 嘗試主服務 (GPT-4)...")
            response = await primary_service.get_chat_message_content(
                chat_history=chat_history, settings=None
            )
            print("✅ 主服務成功")
            return response.content

        except Exception as e:
            print(f"⚠️  主服務失敗: {e}")

            # 降級到備用服務
            try:
                print("🔄 降級到備用服務...")
                response = await fallback_service.get_chat_message_content(
                    chat_history=chat_history, settings=None
                )
                print("✅ 備用服務成功")
                return response.content

            except Exception as e2:
                print(f"❌ 備用服務也失敗: {e2}")
                return "抱歉，服務暫時不可用，請稍後再試。"

    result = await request_with_fallback("什麼是機器學習？")
    print(f"\n📝 回答: {result}")


async def example_graceful_degradation():
    """示例 5: 優雅降級"""
    print("\n" + "=" * 60)
    print("示例 5: 優雅降級")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")

    async def smart_response(question: str) -> str:
        """智能響應（帶降級）"""

        # 級別 1: 嘗試 AI 服務
        if api_key:
            try:
                kernel = sk.Kernel()
                service = OpenAIChatCompletion(
                    service_id="chat-gpt",
                    ai_model_id="gpt-4o-mini",
                    api_key=api_key,
                )
                kernel.add_service(service)

                chat_history = ChatHistory()
                chat_history.add_user_message(question)

                response = await service.get_chat_message_content(
                    chat_history=chat_history, settings=None
                )

                print("✅ 使用 AI 服務回答")
                return response.content

            except Exception as e:
                print(f"⚠️  AI 服務失敗: {e}，降級到規則引擎")

        # 級別 2: 規則引擎
        simple_responses = {
            "你好": "您好！有什麼我可以幫助您的嗎？",
            "再見": "再見！祝您有美好的一天！",
            "謝謝": "不客氣！很高興能幫助您。",
        }

        for keyword, response in simple_responses.items():
            if keyword in question:
                print("✅ 使用規則引擎回答")
                return response

        # 級別 3: 默認響應
        print("✅ 使用默認回答")
        return "抱歉，我現在無法回答這個問題。請稍後再試或聯繫客服。"

    # 測試不同情況
    questions = [
        "什麼是深度學習？",  # AI 回答
        "你好",  # 規則回答
        "請解釋相對論",  # 可能是默認回答（如果 AI 失敗）
    ]

    for q in questions:
        print(f"\n💬 問題: {q}")
        answer = await smart_response(q)
        print(f"🤖 回答: {answer}")


async def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🚀 Semantic Kernel - 錯誤處理示例")
    print("=" * 60)

    try:
        await example_basic_error_handling()
        await example_retry_mechanism()
        await example_timeout_handling()
        await example_fallback_strategy()
        await example_graceful_degradation()

    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ 所有示例運行完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
