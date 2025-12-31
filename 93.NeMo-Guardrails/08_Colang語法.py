"""
NeMo Guardrails - Colang 語法示例
展示 Colang 語言的詳細用法
"""

import os
from nemoguardrails import RailsConfig, LLMRails

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")


def basic_colang_syntax():
    """
    基本 Colang 語法
    """
    print("=" * 60)
    print("基本 Colang 語法示例")
    print("=" * 60)

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo
    """

    # Colang 基本語法
    colang_content = """
    # 1. 定義用戶消息模式
    define user ask about syntax
      "what is colang"
      "explain colang"
      "colang syntax"

    # 2. 定義機器人回應
    define bot explain colang
      "Colang is the Conversation Language used to define rules and flows in NeMo Guardrails."

    # 3. 定義流程
    define flow colang explanation
      user ask about syntax
      bot explain colang
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)

        test_input = "What is Colang?"

        print("\n測試基本語法:")
        print("-" * 60)
        print(f"\n👤 用戶: {test_input}")

        response = rails.generate(messages=[{
            "role": "user",
            "content": test_input
        }])

        print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 基本語法測試完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def conditional_flows():
    """
    條件流程語法
    """
    print("\n" + "=" * 60)
    print("條件流程語法示例")
    print("=" * 60)

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo
    """

    colang_content = """
    # 定義用戶技能等級
    define user beginner level
      "i'm new to"
      "just started"
      "beginner"

    define user advanced level
      "i'm experienced"
      "advanced"
      "expert"

    # 定義不同的回應
    define bot beginner response
      "Great! Let's start with the basics."

    define bot advanced response
      "Excellent! Let's dive into advanced topics."

    # 條件流程
    define flow skill based response
      user beginner level
      bot beginner response

    or user advanced level
      bot advanced response
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)

        test_inputs = [
            "I'm new to Python",
            "I'm an experienced developer"
        ]

        print("\n測試條件流程:")
        print("-" * 60)

        for user_input in test_inputs:
            print(f"\n👤 用戶: {user_input}")

            response = rails.generate(messages=[{
                "role": "user",
                "content": user_input
            }])

            print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 條件流程測試完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def variables_in_colang():
    """
    Colang 中的變量使用
    """
    print("\n" + "=" * 60)
    print("Colang 變量使用示例")
    print("=" * 60)

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo
    """

    colang_content = """
    # 使用變量的流程
    define flow greeting with name
      user express greeting
      $user_name = "there"  # 默認值
      bot greeting with name

    define user express greeting
      "hello"
      "hi"

    define bot greeting with name
      "Hello $user_name! How can I help you?"
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)

        test_input = "Hello"

        print("\n測試變量使用:")
        print("-" * 60)
        print(f"\n👤 用戶: {test_input}")

        response = rails.generate(messages=[{
            "role": "user",
            "content": test_input
        }])

        print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 變量使用測試完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def sequential_flows():
    """
    順序流程語法
    """
    print("\n" + "=" * 60)
    print("順序流程語法示例")
    print("=" * 60)

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo
    """

    colang_content = """
    # 定義順序流程
    define flow learning path
      user express interest
      bot acknowledge interest
      user ask how to start
      bot provide guidance
      bot offer resources

    define user express interest
      "i want to learn"
      "interested in"

    define bot acknowledge interest
      "That's great!"

    define user ask how to start
      "how do i start"
      "where to begin"

    define bot provide guidance
      "Here's how to get started..."

    define bot offer resources
      "I can provide additional resources if needed."
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)

        conversation = [
            "I want to learn Python",
            "How do I start?"
        ]

        print("\n測試順序流程:")
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
        print("✅ 順序流程測試完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def pattern_matching():
    """
    模式匹配語法
    """
    print("\n" + "=" * 60)
    print("模式匹配語法示例")
    print("=" * 60)

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo
    """

    colang_content = """
    # 使用通配符的模式匹配
    define user ask about language
      "what is *"
      "tell me about *"
      "explain *"

    define bot provide explanation
      "I'll explain that for you."

    # 精確匹配
    define user ask specific question
      "what is python"

    define bot answer python
      "Python is a high-level programming language."

    # 流程
    define flow question answering
      user ask specific question
      bot answer python

    or user ask about language
      bot provide explanation
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)

        test_inputs = [
            "What is Python",
            "Tell me about JavaScript",
            "Explain variables"
        ]

        print("\n測試模式匹配:")
        print("-" * 60)

        for user_input in test_inputs:
            print(f"\n👤 用戶: {user_input}")

            response = rails.generate(messages=[{
                "role": "user",
                "content": user_input
            }])

            print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 模式匹配測試完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def comments_and_formatting():
    """
    註釋和格式化語法
    """
    print("\n" + "=" * 60)
    print("註釋和格式化語法示例")
    print("=" * 60)

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo
    """

    colang_content = """
    # ==========================================
    # 這是一個多行註釋的示例
    # 用於解釋 Colang 中的格式化規則
    # ==========================================

    # 定義用戶意圖 - 請求幫助
    define user request help
      "help"
      "can you help"
      "i need assistance"

    # 定義機器人回應 - 提供幫助
    define bot offer help
      "Of course! I'm here to help."
      "I'll be happy to assist you."

    # 流程定義 - 幫助請求處理
    define flow help request
      # 步驟 1: 用戶請求幫助
      user request help

      # 步驟 2: 機器人提供幫助
      bot offer help
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)

        test_input = "Can you help me?"

        print("\n測試註釋和格式化:")
        print("-" * 60)
        print(f"\n👤 用戶: {test_input}")

        response = rails.generate(messages=[{
            "role": "user",
            "content": test_input
        }])

        print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 格式化測試完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def main():
    """
    主函數：運行所有 Colang 語法示例
    """
    print("\n🛡️  NeMo Guardrails - Colang 語法")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        return

    # 運行各種 Colang 語法示例
    basic_colang_syntax()
    conditional_flows()
    variables_in_colang()
    sequential_flows()
    pattern_matching()
    comments_and_formatting()

    print("\n" + "=" * 60)
    print("✅ 所有 Colang 語法示例執行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
