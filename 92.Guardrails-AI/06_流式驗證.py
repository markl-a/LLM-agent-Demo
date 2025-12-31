"""
Guardrails AI - 流式驗證示例
展示如何對流式輸出進行實時驗證
"""

import os
from guardrails import Guard
from guardrails.hub import ValidLength, RegexMatch
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


def basic_streaming_validation():
    """
    基本流式驗證示例
    """
    print("=" * 60)
    print("基本流式驗證示例")
    print("=" * 60)

    # 創建 Guard
    guard = Guard().use(
        ValidLength(min=50, max=200, on_fail="exception")
    )

    prompt = "用 100 字左右描述 Python 編程語言的特點"

    print(f"\n提示: {prompt}")
    print("\n流式輸出:")
    print("-" * 60)

    try:
        # 使用 streaming=True 啟用流式輸出
        stream_result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=300,
            stream=True
        )

        # 收集流式數據
        collected_text = ""

        for chunk in stream_result:
            if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    content = delta.content
                    collected_text += content
                    print(content, end='', flush=True)

        print("\n" + "-" * 60)
        print(f"\n完整輸出長度: {len(collected_text)} 字符")
        print(f"✅ 流式驗證完成")

    except Exception as e:
        print(f"\n❌ 流式驗證失敗: {str(e)}")


def streaming_with_chunk_validation():
    """
    分塊驗證：驗證每個數據塊
    """
    print("\n" + "=" * 60)
    print("分塊驗證示例")
    print("=" * 60)

    prompt = "講一個關於 AI 的簡短故事"

    print(f"\n提示: {prompt}")
    print("\n流式輸出（實時驗證每個塊）:")
    print("-" * 60)

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            stream=True
        )

        collected_text = ""
        chunk_count = 0

        for chunk in stream:
            if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    content = delta.content
                    collected_text += content
                    chunk_count += 1

                    # 打印內容
                    print(content, end='', flush=True)

                    # 驗證累積的文本（可選）
                    # 這裡可以添加實時驗證邏輯

        print("\n" + "-" * 60)
        print(f"\n總塊數: {chunk_count}")
        print(f"總字符數: {len(collected_text)}")
        print(f"✅ 分塊驗證完成")

    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")


def streaming_with_buffer():
    """
    帶緩衝區的流式驗證
    """
    print("\n" + "=" * 60)
    print("緩衝區流式驗證示例")
    print("=" * 60)

    prompt = "解釋什麼是深度學習"

    print(f"\n提示: {prompt}")
    print("\n流式輸出（每 50 字符驗證一次）:")
    print("-" * 60)

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            stream=True
        )

        buffer = ""
        buffer_size = 50  # 每 50 字符驗證一次
        validation_count = 0

        for chunk in stream:
            if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    content = delta.content
                    buffer += content
                    print(content, end='', flush=True)

                    # 當緩衝區達到閾值時進行驗證
                    if len(buffer) >= buffer_size:
                        validation_count += 1
                        # 這裡可以執行驗證邏輯
                        # 例如：檢查是否包含不當內容
                        buffer = ""  # 清空緩衝區

        # 驗證剩餘內容
        if buffer:
            validation_count += 1

        print("\n" + "-" * 60)
        print(f"\n驗證次數: {validation_count}")
        print(f"✅ 緩衝區驗證完成")

    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")


def streaming_with_early_stopping():
    """
    早停機制：檢測到問題時立即停止
    """
    print("\n" + "=" * 60)
    print("早停機制示例")
    print("=" * 60)

    # 禁止詞列表
    forbidden_words = ["error", "fail", "wrong"]

    prompt = "描述一個成功的項目案例"

    print(f"\n提示: {prompt}")
    print(f"禁止詞: {', '.join(forbidden_words)}")
    print("\n流式輸出（檢測到禁止詞會停止）:")
    print("-" * 60)

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            stream=True
        )

        collected_text = ""
        stopped_early = False

        for chunk in stream:
            if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    content = delta.content
                    collected_text += content
                    print(content, end='', flush=True)

                    # 檢查禁止詞
                    text_lower = collected_text.lower()
                    for word in forbidden_words:
                        if word in text_lower:
                            print(f"\n\n⚠️  檢測到禁止詞 '{word}'，停止生成")
                            stopped_early = True
                            break

                    if stopped_early:
                        break

        print("\n" + "-" * 60)
        if stopped_early:
            print(f"⚠️  提前停止")
        else:
            print(f"✅ 正常完成")

        print(f"生成的文本長度: {len(collected_text)}")

    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")


def streaming_with_token_limit():
    """
    流式輸出中的 Token 限制
    """
    print("\n" + "=" * 60)
    print("Token 限制流式輸出示例")
    print("=" * 60)

    prompt = "詳細介紹雲計算的概念和應用"

    max_chars = 150  # 字符限制

    print(f"\n提示: {prompt}")
    print(f"字符限制: {max_chars}")
    print("\n流式輸出:")
    print("-" * 60)

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            stream=True
        )

        collected_text = ""

        for chunk in stream:
            if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    content = delta.content

                    # 檢查是否會超過限制
                    if len(collected_text) + len(content) > max_chars:
                        # 只添加部分內容以達到限制
                        remaining = max_chars - len(collected_text)
                        content = content[:remaining]
                        collected_text += content
                        print(content, end='', flush=True)
                        print("\n\n⚠️  達到字符限制，停止生成")
                        break

                    collected_text += content
                    print(content, end='', flush=True)

        print("\n" + "-" * 60)
        print(f"最終長度: {len(collected_text)} / {max_chars}")
        print(f"✅ 完成")

    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")


def streaming_with_format_validation():
    """
    流式輸出格式驗證
    """
    print("\n" + "=" * 60)
    print("格式驗證流式輸出示例")
    print("=" * 60)

    prompt = "生成一個 JSON 格式的用戶資料，包含 name 和 age 字段"

    print(f"\n提示: {prompt}")
    print("\n流式輸出:")
    print("-" * 60)

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            stream=True
        )

        collected_text = ""

        for chunk in stream:
            if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    content = delta.content
                    collected_text += content
                    print(content, end='', flush=True)

        print("\n" + "-" * 60)

        # 最後驗證格式
        print("\n驗證 JSON 格式...")
        import json
        try:
            parsed = json.loads(collected_text.strip())
            print(f"✅ JSON 格式有效")
            print(f"解析結果: {json.dumps(parsed, indent=2, ensure_ascii=False)}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON 格式無效: {str(e)}")

    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")


def streaming_progress_indicator():
    """
    帶進度指示器的流式輸出
    """
    print("\n" + "=" * 60)
    print("進度指示器流式輸出示例")
    print("=" * 60)

    prompt = "寫一段關於量子計算的介紹"

    print(f"\n提示: {prompt}")
    print("\n流式輸出:")
    print("-" * 60)

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250,
            stream=True
        )

        collected_text = ""
        char_count = 0
        word_count = 0

        for chunk in stream:
            if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    content = delta.content
                    collected_text += content
                    char_count += len(content)
                    word_count = len(collected_text.split())
                    print(content, end='', flush=True)

        print("\n" + "-" * 60)
        print(f"\n📊 統計:")
        print(f"字符數: {char_count}")
        print(f"詞數: {word_count}")
        print(f"平均詞長: {char_count / word_count if word_count > 0 else 0:.2f}")
        print(f"✅ 完成")

    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")


def main():
    """
    主函數：運行所有流式驗證示例
    """
    print("\n🛡️  Guardrails AI - 流式驗證")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        return

    # 運行各種流式驗證示例
    basic_streaming_validation()
    streaming_with_chunk_validation()
    streaming_with_buffer()
    streaming_with_early_stopping()
    streaming_with_token_limit()
    streaming_with_format_validation()
    streaming_progress_indicator()

    print("\n" + "=" * 60)
    print("✅ 所有流式驗證示例執行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
