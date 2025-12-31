"""
NeMo Guardrails - 自定義軌道示例
展示如何創建自定義護欄規則
"""

import os
from nemoguardrails import RailsConfig, LLMRails
from nemoguardrails.actions import action

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")


def custom_greeting_rail():
    """
    自定義問候軌道
    """
    print("=" * 60)
    print("自定義問候軌道示例")
    print("=" * 60)

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    rails:
      dialog:
        flows:
          - custom greeting
    """

    colang_content = """
    # 自定義問候流程
    define user express greeting
      "hello"
      "hi"
      "hey"
      "good morning"

    define bot express greeting
      "Hello! I'm your programming assistant. How can I help you today?"

    define flow custom greeting
      user express greeting
      bot express greeting
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)

        test_inputs = [
            "Hello!",
            "Hi there",
            "Good morning",
            "What is Python?"
        ]

        print("\n測試自定義問候:")
        print("-" * 60)

        for user_input in test_inputs:
            print(f"\n👤 用戶: {user_input}")

            response = rails.generate(messages=[{
                "role": "user",
                "content": user_input
            }])

            print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 自定義問候完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def custom_validation_rail():
    """
    自定義驗證軌道
    """
    print("\n" + "=" * 60)
    print("自定義驗證軌道示例")
    print("=" * 60)

    @action(name="validate_code_request")
    async def validate_code_request(context: dict):
        """驗證代碼請求的有效性"""
        user_message = context.get("user_message", "")

        # 檢查是否是有效的代碼請求
        code_keywords = ["code", "example", "function", "class", "how to"]

        is_valid = any(keyword in user_message.lower() for keyword in code_keywords)

        return is_valid

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    rails:
      input:
        flows:
          - validate request
    """

    colang_content = """
    define flow validate request
      user ...
      $is_valid = execute validate_code_request

      if not $is_valid
        bot ask for clarification
        stop

    define bot ask for clarification
      "I'm a programming assistant. Could you ask a specific programming question?"
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)
        rails.register_action(validate_code_request)

        test_inputs = [
            "Show me a code example",
            "What's the weather like?",
            "How to create a function?",
            "Tell me a joke"
        ]

        print("\n測試自定義驗證:")
        print("-" * 60)

        for user_input in test_inputs:
            print(f"\n👤 用戶: {user_input}")

            response = rails.generate(messages=[{
                "role": "user",
                "content": user_input
            }])

            print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 自定義驗證完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def custom_response_formatting():
    """
    自定義響應格式化軌道
    """
    print("\n" + "=" * 60)
    print("自定義響應格式化示例")
    print("=" * 60)

    @action(name="format_code_response")
    async def format_code_response(context: dict):
        """格式化代碼響應"""
        bot_message = context.get("bot_message", "")

        # 如果響應包含代碼，確保使用 markdown 格式
        if "def " in bot_message or "class " in bot_message:
            if "```python" not in bot_message:
                # 添加代碼塊標記
                lines = bot_message.split('\n')
                formatted_lines = []
                in_code = False

                for line in lines:
                    if not in_code and (line.strip().startswith("def ") or line.strip().startswith("class ")):
                        formatted_lines.append("```python")
                        in_code = True

                    formatted_lines.append(line)

                if in_code:
                    formatted_lines.append("```")

                context["bot_message"] = '\n'.join(formatted_lines)

        return True

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    rails:
      output:
        flows:
          - format response
    """

    colang_content = """
    define flow format response
      bot ...
      execute format_code_response
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)
        rails.register_action(format_code_response)

        test_input = "Show me a simple Python function"

        print("\n測試響應格式化:")
        print("-" * 60)

        print(f"\n👤 用戶: {test_input}")

        response = rails.generate(messages=[{
            "role": "user",
            "content": test_input
        }])

        print(f"🤖 助手:\n{response['content']}")

        print("\n" + "-" * 60)
        print("✅ 響應格式化完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def custom_context_rail():
    """
    自定義上下文軌道
    """
    print("\n" + "=" * 60)
    print("自定義上下文軌道示例")
    print("=" * 60)

    @action(name="track_topic")
    async def track_topic(context: dict):
        """追蹤對話主題"""
        user_message = context.get("user_message", "")

        # 簡單的主題識別
        if "python" in user_message.lower():
            context["current_topic"] = "python"
        elif "javascript" in user_message.lower():
            context["current_topic"] = "javascript"
        else:
            context["current_topic"] = "general"

        return context.get("current_topic")

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    rails:
      dialog:
        flows:
          - maintain context
    """

    colang_content = """
    define flow maintain context
      user ...
      $topic = execute track_topic
      bot ...
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)
        rails.register_action(track_topic)

        conversation = [
            "Tell me about Python",
            "What are its main features?",
            "How about JavaScript?",
            "Compare them"
        ]

        print("\n測試上下文追蹤:")
        print("-" * 60)

        messages = []
        for turn in conversation:
            messages.append({"role": "user", "content": turn})

            print(f"\n👤 用戶: {turn}")

            response = rails.generate(messages=messages)

            print(f"🤖 助手: {response['content']}")

            messages.append({
                "role": "assistant",
                "content": response['content']
            })

        print("\n" + "-" * 60)
        print("✅ 上下文追蹤完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def custom_error_handling_rail():
    """
    自定義錯誤處理軌道
    """
    print("\n" + "=" * 60)
    print("自定義錯誤處理軌道示例")
    print("=" * 60)

    @action(name="handle_error")
    async def handle_error(context: dict):
        """自定義錯誤處理"""
        error_type = context.get("error_type", "unknown")

        error_messages = {
            "rate_limit": "I'm currently experiencing high demand. Please try again in a moment.",
            "invalid_input": "I couldn't understand that request. Could you rephrase it?",
            "timeout": "The request took too long. Please try a simpler question.",
            "unknown": "Something went wrong. Please try again."
        }

        return error_messages.get(error_type, error_messages["unknown"])

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    rails:
      dialog:
        flows:
          - handle errors
    """

    colang_content = """
    define flow handle errors
      user ...
      try:
        bot ...
      except:
        $error_msg = execute handle_error
        bot $error_msg
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)
        rails.register_action(handle_error)

        test_input = "What is Python?"

        print("\n測試錯誤處理:")
        print("-" * 60)

        print(f"\n👤 用戶: {test_input}")

        response = rails.generate(messages=[{
            "role": "user",
            "content": test_input
        }])

        print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 錯誤處理完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def main():
    """
    主函數：運行所有自定義軌道示例
    """
    print("\n🛡️  NeMo Guardrails - 自定義軌道")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        return

    # 運行各種自定義軌道示例
    custom_greeting_rail()
    custom_validation_rail()
    custom_response_formatting()
    custom_context_rail()
    custom_error_handling_rail()

    print("\n" + "=" * 60)
    print("✅ 所有自定義軌道示例執行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
