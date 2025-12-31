"""
LiteLLM 快速開始範例

這個檔案展示了 LiteLLM 的基礎使用方法，包括：
1. 基本的模型呼叫
2. 訊息格式化
3. 參數設定
4. 錯誤處理
5. 同步和非同步呼叫
6. 回應解析

LiteLLM 的核心優勢是提供統一的介面來呼叫不同的 LLM 供應商。
"""

import os
from typing import List, Dict, Any, Optional
import json
from litellm import completion, acompletion
import asyncio
from datetime import datetime


# ============================================================================
# 第一部分：基礎設定和環境準備
# ============================================================================

def setup_environment():
    """
    設定環境變數和 API 金鑰

    在實際應用中，建議使用環境變數或配置檔案來管理 API 金鑰，
    而不是直接寫在程式碼中。
    """
    print("=" * 80)
    print("設定環境變數")
    print("=" * 80)

    # OpenAI API 金鑰
    # os.environ["OPENAI_API_KEY"] = "sk-..."

    # Anthropic API 金鑰
    # os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."

    # AWS Bedrock 憑證
    # os.environ["AWS_ACCESS_KEY_ID"] = "..."
    # os.environ["AWS_SECRET_ACCESS_KEY"] = "..."
    # os.environ["AWS_REGION_NAME"] = "us-east-1"

    print("✓ 環境變數設定完成")
    print("注意：請確保已設定相應的 API 金鑰\n")


# ============================================================================
# 第二部分：基本的 LLM 呼叫
# ============================================================================

def basic_completion_example():
    """
    最基本的 LiteLLM 使用範例

    LiteLLM 使用與 OpenAI 相同的介面格式，讓您可以輕鬆切換不同的模型。
    """
    print("=" * 80)
    print("基本完成呼叫範例")
    print("=" * 80)

    try:
        # 呼叫 OpenAI GPT-4
        print("\n1. 呼叫 OpenAI GPT-4o...")
        response = completion(
            model="gpt-4o",  # 模型名稱
            messages=[
                {
                    "role": "user",
                    "content": "用一句話解釋什麼是 LiteLLM"
                }
            ]
        )

        # 取得回應內容
        content = response.choices[0].message.content
        print(f"回應：{content}")

        # 顯示使用統計
        print(f"\n使用統計：")
        print(f"  - 提示 tokens：{response.usage.prompt_tokens}")
        print(f"  - 完成 tokens：{response.usage.completion_tokens}")
        print(f"  - 總計 tokens：{response.usage.total_tokens}")

    except Exception as e:
        print(f"錯誤：{e}")


def multi_model_example():
    """
    展示如何使用相同的程式碼呼叫不同的模型

    這是 LiteLLM 最核心的功能：統一的介面支援多種模型。
    只需要更改模型名稱，就可以切換到不同的供應商。
    """
    print("\n" + "=" * 80)
    print("多模型呼叫範例")
    print("=" * 80)

    # 定義要測試的模型列表
    models = [
        "gpt-4o",  # OpenAI
        "gpt-3.5-turbo",  # OpenAI
        # "claude-3-5-sonnet-20241022",  # Anthropic
        # "gemini-pro",  # Google
        # "bedrock/anthropic.claude-3-sonnet-20240229-v1:0",  # AWS Bedrock
    ]

    prompt = "什麼是人工智慧？用一句話回答。"

    for model in models:
        try:
            print(f"\n使用模型：{model}")
            print("-" * 40)

            response = completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100  # 限制回應長度
            )

            content = response.choices[0].message.content
            print(f"回應：{content}")

        except Exception as e:
            print(f"錯誤：{e}")


# ============================================================================
# 第三部分：訊息格式和對話管理
# ============================================================================

def conversation_example():
    """
    展示如何進行多輪對話

    LiteLLM 支援完整的對話歷史管理，可以進行多輪互動。
    """
    print("\n" + "=" * 80)
    print("對話範例")
    print("=" * 80)

    # 初始化對話歷史
    messages = [
        {
            "role": "system",
            "content": "你是一個友善的 AI 助手，專門幫助開發者了解 LiteLLM。"
        }
    ]

    # 第一輪對話
    print("\n第一輪對話：")
    print("-" * 40)
    user_message_1 = "什麼是 LiteLLM？"
    print(f"使用者：{user_message_1}")

    messages.append({"role": "user", "content": user_message_1})

    try:
        response = completion(
            model="gpt-4o",
            messages=messages
        )

        assistant_message_1 = response.choices[0].message.content
        print(f"助手：{assistant_message_1}")

        # 將助手的回應加入歷史
        messages.append({"role": "assistant", "content": assistant_message_1})

        # 第二輪對話
        print("\n第二輪對話：")
        print("-" * 40)
        user_message_2 = "它支援哪些 LLM 供應商？"
        print(f"使用者：{user_message_2}")

        messages.append({"role": "user", "content": user_message_2})

        response = completion(
            model="gpt-4o",
            messages=messages
        )

        assistant_message_2 = response.choices[0].message.content
        print(f"助手：{assistant_message_2}")

        # 顯示完整的對話歷史
        print("\n完整對話歷史：")
        print("-" * 40)
        for i, msg in enumerate(messages, 1):
            role = msg["role"]
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            print(f"{i}. [{role}] {content}")

    except Exception as e:
        print(f"錯誤：{e}")


def system_message_example():
    """
    展示如何使用系統訊息來設定 AI 的行為

    系統訊息用於定義 AI 助手的角色、語氣和行為準則。
    """
    print("\n" + "=" * 80)
    print("系統訊息範例")
    print("=" * 80)

    # 不同的系統訊息範例
    system_messages = {
        "專業技術專家": "你是一位經驗豐富的軟體工程師，使用專業、精確的語言回答技術問題。",
        "友善導師": "你是一位友善、耐心的導師，用淺顯易懂的方式解釋複雜的技術概念。",
        "簡潔回答者": "你是一個注重效率的助手，總是用最簡潔的方式回答問題，避免冗長的解釋。"
    }

    question = "什麼是 API？"

    for persona, system_msg in system_messages.items():
        print(f"\n角色設定：{persona}")
        print("-" * 40)
        print(f"系統訊息：{system_msg}")
        print(f"問題：{question}")

        try:
            response = completion(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": question}
                ],
                max_tokens=150
            )

            content = response.choices[0].message.content
            print(f"回應：{content}\n")

        except Exception as e:
            print(f"錯誤：{e}\n")


# ============================================================================
# 第四部分：參數設定和控制
# ============================================================================

def parameter_control_example():
    """
    展示如何使用各種參數來控制模型的行為

    LiteLLM 支援所有常見的模型參數，包括：
    - temperature：控制隨機性
    - max_tokens：限制輸出長度
    - top_p：核採樣
    - frequency_penalty：降低重複
    - presence_penalty：鼓勵多樣性
    """
    print("\n" + "=" * 80)
    print("參數控制範例")
    print("=" * 80)

    prompt = "寫一個關於貓咪的短故事"

    # 不同的 temperature 設定
    temperatures = [0.0, 0.5, 1.0, 1.5]

    print("\n測試不同的 temperature 值：")
    print("(temperature 越高，輸出越有創意和隨機性)\n")

    for temp in temperatures:
        print(f"Temperature = {temp}")
        print("-" * 40)

        try:
            response = completion(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=temp,
                max_tokens=100
            )

            content = response.choices[0].message.content
            print(f"{content}\n")

        except Exception as e:
            print(f"錯誤：{e}\n")


def max_tokens_example():
    """
    展示如何控制輸出長度
    """
    print("\n" + "=" * 80)
    print("輸出長度控制範例")
    print("=" * 80)

    prompt = "詳細解釋機器學習的概念"

    # 不同的 max_tokens 設定
    token_limits = [50, 100, 200, 500]

    for max_tokens in token_limits:
        print(f"\nMax Tokens = {max_tokens}")
        print("-" * 40)

        try:
            response = completion(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )

            content = response.choices[0].message.content
            actual_tokens = response.usage.completion_tokens

            print(f"實際使用 tokens：{actual_tokens}")
            print(f"內容：{content}")

        except Exception as e:
            print(f"錯誤：{e}")


# ============================================================================
# 第五部分：非同步呼叫
# ============================================================================

async def async_completion_example():
    """
    展示如何使用非同步呼叫來提高效能

    當需要同時呼叫多個模型或處理多個請求時，
    非同步呼叫可以顯著提高效能。
    """
    print("\n" + "=" * 80)
    print("非同步呼叫範例")
    print("=" * 80)

    prompts = [
        "什麼是 Python？",
        "什麼是 JavaScript？",
        "什麼是 Go？",
        "什麼是 Rust？"
    ]

    print(f"\n同時處理 {len(prompts)} 個請求...")
    start_time = datetime.now()

    # 建立非同步任務列表
    tasks = []
    for prompt in prompts:
        task = acompletion(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50
        )
        tasks.append(task)

    # 並行執行所有任務
    try:
        responses = await asyncio.gather(*tasks)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"\n所有請求完成！總耗時：{duration:.2f} 秒\n")

        for i, (prompt, response) in enumerate(zip(prompts, responses), 1):
            content = response.choices[0].message.content
            print(f"{i}. 問題：{prompt}")
            print(f"   回答：{content}\n")

    except Exception as e:
        print(f"錯誤：{e}")


def run_async_example():
    """執行非同步範例的包裝函數"""
    asyncio.run(async_completion_example())


# ============================================================================
# 第六部分：錯誤處理
# ============================================================================

def error_handling_example():
    """
    展示如何正確處理各種錯誤情況

    在生產環境中，完善的錯誤處理至關重要。
    """
    print("\n" + "=" * 80)
    print("錯誤處理範例")
    print("=" * 80)

    # 1. 處理無效的模型名稱
    print("\n1. 無效的模型名稱：")
    print("-" * 40)
    try:
        response = completion(
            model="invalid-model-name",
            messages=[{"role": "user", "content": "測試"}]
        )
    except Exception as e:
        print(f"捕獲到錯誤：{type(e).__name__}")
        print(f"錯誤訊息：{e}")

    # 2. 處理缺少 API 金鑰
    print("\n2. 缺少 API 金鑰：")
    print("-" * 40)
    # 暫時移除 API 金鑰
    original_key = os.environ.get("OPENAI_API_KEY")
    if original_key:
        os.environ.pop("OPENAI_API_KEY")

    try:
        response = completion(
            model="gpt-4o",
            messages=[{"role": "user", "content": "測試"}]
        )
    except Exception as e:
        print(f"捕獲到錯誤：{type(e).__name__}")
        print(f"錯誤訊息：{e}")
    finally:
        # 恢復 API 金鑰
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key

    # 3. 處理超時
    print("\n3. 超時處理：")
    print("-" * 40)
    try:
        response = completion(
            model="gpt-4o",
            messages=[{"role": "user", "content": "測試"}],
            timeout=0.001  # 設定極短的超時時間
        )
    except Exception as e:
        print(f"捕獲到錯誤：{type(e).__name__}")
        print(f"錯誤訊息：{e}")


# ============================================================================
# 第七部分：回應解析和元資料
# ============================================================================

def response_metadata_example():
    """
    展示如何解析回應物件並取得各種元資料
    """
    print("\n" + "=" * 80)
    print("回應元資料範例")
    print("=" * 80)

    try:
        response = completion(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": "請用三個詞描述 LiteLLM"}
            ]
        )

        # 基本資訊
        print("\n基本資訊：")
        print("-" * 40)
        print(f"模型：{response.model}")
        print(f"ID：{response.id}")
        print(f"物件類型：{response.object}")
        print(f"建立時間：{response.created}")

        # 訊息內容
        print("\n訊息內容：")
        print("-" * 40)
        choice = response.choices[0]
        print(f"索引：{choice.index}")
        print(f"角色：{choice.message.role}")
        print(f"內容：{choice.message.content}")
        print(f"結束原因：{choice.finish_reason}")

        # 使用統計
        print("\n使用統計：")
        print("-" * 40)
        usage = response.usage
        print(f"提示 tokens：{usage.prompt_tokens}")
        print(f"完成 tokens：{usage.completion_tokens}")
        print(f"總計 tokens：{usage.total_tokens}")

        # 轉換為字典
        print("\n完整回應（字典格式）：")
        print("-" * 40)
        response_dict = dict(response)
        print(json.dumps(response_dict, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"錯誤：{e}")


# ============================================================================
# 第八部分：實用工具函數
# ============================================================================

def create_simple_chatbot():
    """
    建立一個簡單的命令列聊天機器人

    這個範例展示如何結合前面學到的知識建立一個實用的應用。
    """
    print("\n" + "=" * 80)
    print("簡單聊天機器人")
    print("=" * 80)
    print("\n輸入訊息開始對話，輸入 'quit' 退出\n")

    messages = [
        {
            "role": "system",
            "content": "你是一個友善的 AI 助手，使用繁體中文回答問題。"
        }
    ]

    conversation_count = 0

    while True:
        # 取得使用者輸入
        user_input = input("你：").strip()

        if user_input.lower() in ['quit', 'exit', '退出', '結束']:
            print("再見！")
            break

        if not user_input:
            continue

        # 加入使用者訊息
        messages.append({"role": "user", "content": user_input})

        try:
            # 呼叫 LLM
            response = completion(
                model="gpt-4o",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )

            # 取得回應
            assistant_message = response.choices[0].message.content
            messages.append({"role": "assistant", "content": assistant_message})

            print(f"\nAI：{assistant_message}\n")

            conversation_count += 1

            # 顯示統計資訊
            if conversation_count % 5 == 0:
                total_tokens = sum(
                    len(msg["content"].split()) for msg in messages
                )
                print(f"[統計] 已進行 {conversation_count} 輪對話，累計約 {total_tokens} 個詞")

        except Exception as e:
            print(f"\n錯誤：{e}\n")
            # 移除最後一條使用者訊息，避免重複
            messages.pop()


# ============================================================================
# 主程式
# ============================================================================

def main():
    """
    主程式：執行所有範例
    """
    print("\n")
    print("=" * 80)
    print("LiteLLM 快速開始教學")
    print("=" * 80)
    print("\n這個教學將帶您了解 LiteLLM 的基礎使用方法\n")

    # 設定環境
    setup_environment()

    # 基本範例（註解掉需要 API 金鑰的部分，避免執行時錯誤）
    # basic_completion_example()
    # multi_model_example()
    # conversation_example()
    # system_message_example()
    # parameter_control_example()
    # max_tokens_example()

    # 非同步範例
    # run_async_example()

    # 錯誤處理
    # error_handling_example()

    # 回應解析
    # response_metadata_example()

    # 聊天機器人（互動式，可選擇執行）
    # create_simple_chatbot()

    print("\n" + "=" * 80)
    print("教學完成！")
    print("=" * 80)
    print("\n提示：")
    print("1. 取消註解上面的函數呼叫來執行相應的範例")
    print("2. 確保已正確設定 API 金鑰")
    print("3. 可以修改範例中的參數來實驗不同的效果")
    print("\n")


if __name__ == "__main__":
    main()
