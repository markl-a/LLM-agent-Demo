"""
LiteLLM 流式輸出範例
====================

這個範例展示如何使用 LiteLLM 的串流功能：
1. 基本的串流輸出
2. 處理串流事件
3. 異步串流
4. 串流成本追蹤
5. 多模型串流比較

串流輸出可以讓用戶更快地看到回應，改善用戶體驗。
"""

import os
from litellm import completion
import litellm
import asyncio
import time
from typing import AsyncIterator

# 設定日誌
litellm.set_verbose = False


def basic_streaming():
    """基本的串流輸出範例"""
    print("=" * 60)
    print("範例 1: 基本串流輸出")
    print("=" * 60)

    try:
        # 啟用 stream=True
        response = completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "寫一個關於 Python 的短文（約 50 字）"}],
            stream=True  # 啟用串流
        )

        print("\n串流輸出：")
        print("-" * 40)

        # 逐塊處理回應
        for chunk in response:
            # 提取內容（如果存在）
            if hasattr(chunk.choices[0].delta, 'content'):
                content = chunk.choices[0].delta.content
                if content:
                    print(content, end='', flush=True)

        print("\n" + "-" * 40)
        print("串流結束")

    except Exception as e:
        print(f"錯誤: {e}")


def streaming_with_details():
    """帶詳細資訊的串流輸出"""
    print("\n" + "=" * 60)
    print("範例 2: 串流輸出與詳細資訊")
    print("=" * 60)

    try:
        response = completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "列出 3 個 Python 的優點"}],
            stream=True
        )

        print("\n開始接收串流...")
        chunk_count = 0
        total_content = ""

        for chunk in response:
            chunk_count += 1

            # 檢查是否有內容
            if hasattr(chunk.choices[0].delta, 'content'):
                content = chunk.choices[0].delta.content
                if content:
                    total_content += content
                    print(content, end='', flush=True)

            # 檢查是否有 finish_reason
            if chunk.choices[0].finish_reason:
                print(f"\n\n完成原因: {chunk.choices[0].finish_reason}")

        print(f"\n總共接收 {chunk_count} 個區塊")
        print(f"總內容長度: {len(total_content)} 字元")

    except Exception as e:
        print(f"錯誤: {e}")


def streaming_with_role():
    """處理包含 role 的串流輸出"""
    print("\n" + "=" * 60)
    print("範例 3: 處理完整的串流資訊")
    print("=" * 60)

    try:
        response = completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello!"}],
            stream=True
        )

        print("\n串流詳細資訊：")

        for chunk in response:
            delta = chunk.choices[0].delta

            # 第一個區塊可能包含 role
            if hasattr(delta, 'role') and delta.role:
                print(f"\nRole: {delta.role}")

            # 內容區塊
            if hasattr(delta, 'content') and delta.content:
                print(delta.content, end='', flush=True)

            # 完成標記
            if chunk.choices[0].finish_reason:
                print(f"\n\nFinish reason: {chunk.choices[0].finish_reason}")

    except Exception as e:
        print(f"錯誤: {e}")


async def async_streaming():
    """異步串流輸出範例"""
    print("\n" + "=" * 60)
    print("範例 4: 異步串流輸出")
    print("=" * 60)

    from litellm import acompletion

    try:
        response = await acompletion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "用 3 句話介紹機器學習"}],
            stream=True
        )

        print("\n異步串流輸出：")
        print("-" * 40)

        async for chunk in response:
            if hasattr(chunk.choices[0].delta, 'content'):
                content = chunk.choices[0].delta.content
                if content:
                    print(content, end='', flush=True)

        print("\n" + "-" * 40)

    except Exception as e:
        print(f"錯誤: {e}")


async def multiple_async_streams():
    """並發處理多個異步串流"""
    print("\n" + "=" * 60)
    print("範例 5: 並發多個異步串流")
    print("=" * 60)

    from litellm import acompletion

    async def stream_model(model: str, prompt: str, label: str):
        """處理單個模型的串流"""
        try:
            print(f"\n[{label}] 開始串流...")
            response = await acompletion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )

            content = ""
            async for chunk in response:
                if hasattr(chunk.choices[0].delta, 'content'):
                    delta_content = chunk.choices[0].delta.content
                    if delta_content:
                        content += delta_content

            print(f"\n[{label}] 完成: {content[:100]}...")
            return {label: content}

        except Exception as e:
            print(f"\n[{label}] 錯誤: {e}")
            return {label: f"Error: {e}"}

    # 並發調用兩個模型
    try:
        tasks = [
            stream_model("gpt-3.5-turbo", "What is AI?", "GPT-3.5"),
            stream_model("gpt-4", "What is AI?", "GPT-4"),
        ]

        results = await asyncio.gather(*tasks)
        print("\n所有串流完成！")

    except Exception as e:
        print(f"錯誤: {e}")


def streaming_with_timing():
    """測量串流輸出的時間"""
    print("\n" + "=" * 60)
    print("範例 6: 串流輸出時間測量")
    print("=" * 60)

    try:
        start_time = time.time()
        first_token_time = None

        response = completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "解釋什麼是深度學習"}],
            stream=True
        )

        print("\n串流輸出（帶時間戳）：")
        print("-" * 40)

        for i, chunk in enumerate(response):
            if hasattr(chunk.choices[0].delta, 'content'):
                content = chunk.choices[0].delta.content
                if content:
                    # 記錄第一個 token 的時間
                    if first_token_time is None:
                        first_token_time = time.time() - start_time
                        print(f"\n[首個 token 時間: {first_token_time:.3f}s]\n")

                    print(content, end='', flush=True)

        total_time = time.time() - start_time

        print("\n" + "-" * 40)
        print(f"首個 token 延遲: {first_token_time:.3f} 秒")
        print(f"總耗時: {total_time:.3f} 秒")

    except Exception as e:
        print(f"錯誤: {e}")


def streaming_vs_non_streaming():
    """比較串流與非串流的用戶體驗"""
    print("\n" + "=" * 60)
    print("範例 7: 串流 vs 非串流比較")
    print("=" * 60)

    prompt = "寫一個關於人工智慧的短文（約 100 字）"

    # 非串流模式
    print("\n1. 非串流模式：")
    print("-" * 40)
    try:
        start = time.time()
        response = completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        elapsed = time.time() - start

        print(f"等待 {elapsed:.2f} 秒後收到完整回應：")
        print(response.choices[0].message.content)

    except Exception as e:
        print(f"錯誤: {e}")

    # 串流模式
    print("\n2. 串流模式：")
    print("-" * 40)
    try:
        start = time.time()
        first_token = None

        response = completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        for chunk in response:
            if hasattr(chunk.choices[0].delta, 'content'):
                content = chunk.choices[0].delta.content
                if content:
                    if first_token is None:
                        first_token = time.time() - start
                    print(content, end='', flush=True)

        total = time.time() - start
        print(f"\n\n首個字符: {first_token:.2f}s, 總計: {total:.2f}s")

    except Exception as e:
        print(f"錯誤: {e}")


def streaming_with_callback():
    """使用回調函數處理串流"""
    print("\n" + "=" * 60)
    print("範例 8: 使用回調函數處理串流")
    print("=" * 60)

    collected_messages = []
    token_count = 0

    def process_chunk(chunk):
        """處理每個串流區塊的回調函數"""
        nonlocal token_count

        if hasattr(chunk.choices[0].delta, 'content'):
            content = chunk.choices[0].delta.content
            if content:
                collected_messages.append(content)
                token_count += 1
                return content
        return None

    try:
        response = completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "列出 5 個程式語言"}],
            stream=True
        )

        print("\n串流輸出：")
        for chunk in response:
            content = process_chunk(chunk)
            if content:
                print(content, end='', flush=True)

        # 顯示統計
        print("\n\n統計資訊：")
        print(f"  總區塊數: {token_count}")
        print(f"  完整內容: {''.join(collected_messages)}")

    except Exception as e:
        print(f"錯誤: {e}")


def streaming_different_models():
    """比較不同模型的串流速度"""
    print("\n" + "=" * 60)
    print("範例 9: 不同模型的串流速度比較")
    print("=" * 60)

    models = ["gpt-3.5-turbo", "gpt-4"]
    prompt = "什麼是雲端運算？"

    for model in models:
        try:
            print(f"\n模型: {model}")
            print("-" * 40)

            start_time = time.time()
            first_token_time = None
            chunk_count = 0

            response = completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )

            for chunk in response:
                if hasattr(chunk.choices[0].delta, 'content'):
                    content = chunk.choices[0].delta.content
                    if content:
                        if first_token_time is None:
                            first_token_time = time.time() - start_time
                        chunk_count += 1
                        print(content, end='', flush=True)

            total_time = time.time() - start_time

            print(f"\n\n性能指標:")
            print(f"  首個 token: {first_token_time:.3f}s")
            print(f"  總耗時: {total_time:.3f}s")
            print(f"  區塊數: {chunk_count}")
            if chunk_count > 0:
                print(f"  平均每區塊: {total_time/chunk_count:.3f}s")

        except Exception as e:
            print(f"錯誤 ({model}): {e}")


def streaming_with_system_message():
    """帶系統訊息的串流輸出"""
    print("\n" + "=" * 60)
    print("範例 10: 帶系統訊息的串流")
    print("=" * 60)

    try:
        response = completion(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一個專業的技術文件撰寫者，回答要簡潔專業"},
                {"role": "user", "content": "什麼是 REST API？"}
            ],
            stream=True,
            temperature=0.7
        )

        print("\n串流輸出：")
        print("-" * 40)

        full_response = ""
        for chunk in response:
            if hasattr(chunk.choices[0].delta, 'content'):
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    print(content, end='', flush=True)

        print("\n" + "-" * 40)
        print(f"完整回應長度: {len(full_response)} 字元")

    except Exception as e:
        print(f"錯誤: {e}")


def main():
    """主函數：運行所有範例"""
    print("\n" + "=" * 60)
    print("LiteLLM 流式輸出範例")
    print("=" * 60)

    # 同步範例
    basic_streaming()
    streaming_with_details()
    streaming_with_role()
    streaming_with_timing()
    streaming_vs_non_streaming()
    streaming_with_callback()
    streaming_different_models()
    streaming_with_system_message()

    # 異步範例
    print("\n執行異步串流範例...")
    try:
        asyncio.run(async_streaming())
        asyncio.run(multiple_async_streams())
    except Exception as e:
        print(f"異步範例錯誤: {e}")

    print("\n" + "=" * 60)
    print("所有範例執行完畢！")
    print("=" * 60)


if __name__ == "__main__":
    main()
