"""
NeMo Guardrails - 輸出護欄示例
展示如何驗證和過濾 LLM 的輸出
"""

import os
from nemoguardrails import RailsConfig, LLMRails
from nemoguardrails.actions import action

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")


def basic_output_filtering():
    """
    基本輸出過濾
    """
    print("=" * 60)
    print("基本輸出過濾示例")
    print("=" * 60)

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    rails:
      output:
        flows:
          - self check output
    """

    colang_content = """
    # 定義不當輸出
    define bot express inappropriate
      "I cannot help with that"
      "That's not allowed"

    # 輸出檢查流程
    define flow self check output
      bot ...
      $allowed = execute self_check_output

      if not $allowed
        bot inform cannot respond
        stop

    define bot inform cannot respond
      "I apologize, but I cannot provide that information."
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)

        test_inputs = [
            "What is Python?",
            "How do I learn programming?",
            "Explain machine learning"
        ]

        print("\n測試輸出過濾:")
        print("-" * 60)

        for user_input in test_inputs:
            print(f"\n👤 用戶: {user_input}")

            response = rails.generate(messages=[{
                "role": "user",
                "content": user_input
            }])

            print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 輸出過濾測試完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def fact_checking_output():
    """
    事實核查輸出
    """
    print("\n" + "=" * 60)
    print("事實核查輸出示例")
    print("=" * 60)

    @action(name="check_facts")
    async def check_facts(context: dict):
        """檢查輸出的事實準確性"""
        bot_message = context.get("bot_message", "")

        # 簡化的事實檢查（實際應使用專門的事實核查服務）
        suspicious_keywords = ["always", "never", "100%", "impossible", "certainly"]

        has_suspicious = any(keyword in bot_message.lower() for keyword in suspicious_keywords)

        # 返回是否通過檢查
        return not has_suspicious

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    rails:
      output:
        flows:
          - fact check response
    """

    colang_content = """
    define flow fact check response
      bot ...
      $facts_ok = execute check_facts

      if not $facts_ok
        bot inform uncertain
        stop

    define bot inform uncertain
      "I should clarify that I may not be entirely certain about this information."
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)
        rails.register_action(check_facts)

        test_inputs = [
            "Is Python always the best language?",
            "What are some use cases for Python?",
            "Is it impossible to learn Python?"
        ]

        print("\n測試事實核查:")
        print("-" * 60)

        for user_input in test_inputs:
            print(f"\n👤 用戶: {user_input}")

            response = rails.generate(messages=[{
                "role": "user",
                "content": user_input
            }])

            print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 事實核查完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def output_length_control():
    """
    輸出長度控制
    """
    print("\n" + "=" * 60)
    print("輸出長度控制示例")
    print("=" * 60)

    @action(name="check_output_length")
    async def check_output_length(context: dict):
        """檢查輸出長度"""
        bot_message = context.get("bot_message", "")

        max_length = 200

        if len(bot_message) > max_length:
            # 截斷並添加省略號
            context["bot_message"] = bot_message[:max_length] + "..."
            return False

        return True

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    rails:
      output:
        flows:
          - control length
    """

    colang_content = """
    define flow control length
      bot ...
      execute check_output_length
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)
        rails.register_action(check_output_length)

        test_input = "Explain Python in detail, covering its history, features, and use cases"

        print("\n測試輸出長度控制:")
        print("-" * 60)

        print(f"\n👤 用戶: {test_input}")

        response = rails.generate(messages=[{
            "role": "user",
            "content": test_input
        }])

        print(f"🤖 助手: {response['content']}")
        print(f"\n輸出長度: {len(response['content'])} 字符")

        print("\n" + "-" * 60)
        print("✅ 長度控制完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def sensitive_data_filtering():
    """
    敏感數據過濾
    """
    print("\n" + "=" * 60)
    print("敏感數據過濾示例")
    print("=" * 60)

    @action(name="filter_sensitive_data")
    async def filter_sensitive_data(context: dict):
        """過濾輸出中的敏感數據"""
        import re

        bot_message = context.get("bot_message", "")

        # 過濾郵箱地址
        bot_message = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            '[EMAIL]',
            bot_message
        )

        # 過濾電話號碼
        bot_message = re.sub(
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            '[PHONE]',
            bot_message
        )

        context["bot_message"] = bot_message
        return True

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    rails:
      output:
        flows:
          - filter sensitive
    """

    colang_content = """
    define flow filter sensitive
      bot ...
      execute filter_sensitive_data
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)
        rails.register_action(filter_sensitive_data)

        test_input = "How can I contact support?"

        print("\n測試敏感數據過濾:")
        print("-" * 60)

        print(f"\n👤 用戶: {test_input}")

        response = rails.generate(messages=[{
            "role": "user",
            "content": test_input
        }])

        print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 敏感數據過濾完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def toxicity_check():
    """
    毒性檢測
    """
    print("\n" + "=" * 60)
    print("輸出毒性檢測示例")
    print("=" * 60)

    @action(name="check_toxicity")
    async def check_toxicity(context: dict):
        """檢查輸出的毒性"""
        bot_message = context.get("bot_message", "")

        # 簡化的毒性檢測
        toxic_words = ["hate", "stupid", "idiot", "terrible"]

        is_toxic = any(word in bot_message.lower() for word in toxic_words)

        return not is_toxic

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    rails:
      output:
        flows:
          - check toxic content
    """

    colang_content = """
    define flow check toxic content
      bot ...
      $safe = execute check_toxicity

      if not $safe
        bot provide safe response
        stop

    define bot provide safe response
      "I apologize, but I need to rephrase my response in a more appropriate way."
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)
        rails.register_action(check_toxicity)

        test_inputs = [
            "What do you think about Python?",
            "Is Java good or bad?",
            "Tell me about programming languages"
        ]

        print("\n測試毒性檢測:")
        print("-" * 60)

        for user_input in test_inputs:
            print(f"\n👤 用戶: {user_input}")

            response = rails.generate(messages=[{
                "role": "user",
                "content": user_input
            }])

            print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 毒性檢測完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def format_validation():
    """
    格式驗證
    """
    print("\n" + "=" * 60)
    print("輸出格式驗證示例")
    print("=" * 60)

    @action(name="validate_format")
    async def validate_format(context: dict):
        """驗證輸出格式"""
        bot_message = context.get("bot_message", "")

        # 檢查是否是完整的句子（以標點結尾）
        valid_endings = ['.', '!', '?']

        is_valid = any(bot_message.strip().endswith(ending) for ending in valid_endings)

        if not is_valid:
            # 自動添加句號
            context["bot_message"] = bot_message.strip() + "."

        return True

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    rails:
      output:
        flows:
          - validate output format
    """

    colang_content = """
    define flow validate output format
      bot ...
      execute validate_format
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)
        rails.register_action(validate_format)

        test_input = "What is Python"

        print("\n測試格式驗證:")
        print("-" * 60)

        print(f"\n👤 用戶: {test_input}")

        response = rails.generate(messages=[{
            "role": "user",
            "content": test_input
        }])

        print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 格式驗證完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def main():
    """
    主函數：運行所有輸出護欄示例
    """
    print("\n🛡️  NeMo Guardrails - 輸出護欄")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        return

    # 運行各種輸出護欄示例
    basic_output_filtering()
    fact_checking_output()
    output_length_control()
    sensitive_data_filtering()
    toxicity_check()
    format_validation()

    print("\n" + "=" * 60)
    print("✅ 所有輸出護欄示例執行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
