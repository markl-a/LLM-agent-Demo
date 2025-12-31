"""
Guardrails AI - 快速開始示例
展示最基本的 Guardrails 使用方法
"""

import os
from guardrails import Guard
from guardrails.hub import RegexMatch
import openai

# 設置 OpenAI API 密鑰
openai.api_key = os.getenv("OPENAI_API_KEY")


def basic_guard_example():
    """
    最基本的 Guard 示例
    創建一個簡單的護欄來驗證 LLM 輸出
    """
    print("=" * 60)
    print("基本 Guard 示例")
    print("=" * 60)

    # 創建一個 Guard，使用正則表達式驗證器
    # 確保輸出只包含字母和空格
    guard = Guard().use(
        RegexMatch(regex="^[A-Za-z\\s]+$"),
        on_fail="reask"  # 驗證失敗時重新詢問 LLM
    )

    # 調用 LLM 並應用 Guard
    prompt = "生成一個簡單的英文問候語（只使用英文字母和空格）"

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=50,
        )

        print(f"\n提示: {prompt}")
        print(f"驗證通過的輸出: {result.validated_output}")
        print(f"驗證狀態: {result.validation_passed}")

    except Exception as e:
        print(f"錯誤: {str(e)}")


def guard_with_multiple_validations():
    """
    使用多個驗證規則的 Guard
    """
    print("\n" + "=" * 60)
    print("多重驗證示例")
    print("=" * 60)

    from guardrails.hub import ValidLength

    # 創建帶有多個驗證器的 Guard
    guard = Guard().use_many(
        RegexMatch(regex="^[A-Za-z\\s]+$", on_fail="reask"),  # 只允許字母和空格
        ValidLength(min=10, max=100, on_fail="reask")  # 長度在 10-100 之間
    )

    prompt = "生成一個 20 字左右的英文句子，描述天氣"

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=100,
        )

        print(f"\n提示: {prompt}")
        print(f"驗證通過的輸出: {result.validated_output}")
        print(f"輸出長度: {len(result.validated_output)}")

    except Exception as e:
        print(f"錯誤: {str(e)}")


def simple_text_generation():
    """
    簡單的文本生成與驗證
    """
    print("\n" + "=" * 60)
    print("簡單文本生成示例")
    print("=" * 60)

    # 創建一個不帶驗證器的基本 Guard
    guard = Guard()

    prompt = "請用一句話介紹 Python 編程語言"

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=100,
        )

        print(f"\n提示: {prompt}")
        print(f"LLM 輸出: {result.validated_output}")

    except Exception as e:
        print(f"錯誤: {str(e)}")


def guard_with_metadata():
    """
    帶有元數據的 Guard
    可以記錄驗證過程的詳細信息
    """
    print("\n" + "=" * 60)
    print("帶元數據的 Guard 示例")
    print("=" * 60)

    guard = Guard().use(
        RegexMatch(regex="^[A-Z][a-z\\s]+$"),  # 首字母大寫
        on_fail="fix"  # 嘗試修復
    )

    prompt = "生成一個首字母大寫的英文句子"

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=50,
            metadata={"user_id": "demo_user", "session_id": "session_001"}
        )

        print(f"\n提示: {prompt}")
        print(f"驗證通過的輸出: {result.validated_output}")

        # 打印驗證歷史
        if hasattr(result, 'validation_logs'):
            print(f"\n驗證日誌:")
            for log in result.validation_logs:
                print(f"  - {log}")

    except Exception as e:
        print(f"錯誤: {str(e)}")


def main():
    """
    主函數：運行所有示例
    """
    print("\n")
    print("🛡️  Guardrails AI - 快速開始")
    print("=" * 60)

    # 檢查 API 密鑰
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        print("請設置環境變量: export OPENAI_API_KEY='your-api-key'")
        return

    # 運行各種示例
    basic_guard_example()
    guard_with_multiple_validations()
    simple_text_generation()
    guard_with_metadata()

    print("\n" + "=" * 60)
    print("✅ 所有示例執行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
