"""
NeMo Guardrails - 多輪對話示例
展示如何管理有狀態的多輪對話
"""

import os
from nemoguardrails import RailsConfig, LLMRails
from nemoguardrails.actions import action

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")


def basic_multi_turn():
    """
    基本多輪對話
    """
    print("=" * 60)
    print("基本多輪對話示例")
    print("=" * 60)

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo
    """

    colang_content = """
    # 定義多輪對話流程
    define flow learning conversation
      user express interest
      bot ask level
      user provide level
      bot suggest resources

    define user express interest
      "want to learn"
      "interested in"

    define bot ask level
      "What is your current skill level?"

    define user provide level
      "beginner"
      "intermediate"
      "advanced"

    define bot suggest resources
      "Based on your level, here are some recommendations..."
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)

        conversation = [
            "I want to learn Python",
            "I'm a beginner"
        ]

        print("\n多輪對話測試:")
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
        print("✅ 多輪對話測試完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def stateful_conversation():
    """
    有狀態對話
    """
    print("\n" + "=" * 60)
    print("有狀態對話示例")
    print("=" * 60)

    @action(name="remember_context")
    async def remember_context(context: dict):
        """記住對話上下文"""
        # 從上下文中提取並存儲信息
        user_message = context.get("user_message", "")

        if "python" in user_message.lower():
            context["topic"] = "python"
        elif "javascript" in user_message.lower():
            context["topic"] = "javascript"

        return context.get("topic", "unknown")

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    rails:
      dialog:
        flows:
          - maintain state
    """

    colang_content = """
    define flow maintain state
      user ...
      execute remember_context
      bot ...
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)
        rails.register_action(remember_context)

        conversation = [
            "Tell me about Python",
            "What are its features?",
            "How do I install it?"
        ]

        print("\n有狀態對話測試:")
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
        print("✅ 有狀態對話完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def context_switching():
    """
    上下文切換處理
    """
    print("\n" + "=" * 60)
    print("上下文切換處理示例")
    print("=" * 60)

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo
    """

    colang_content = """
    # 檢測上下文切換
    define user change topic
      "by the way"
      "on another note"
      "switching topics"

    define bot acknowledge topic change
      "Sure, let's talk about something else."

    define flow handle topic change
      user change topic
      bot acknowledge topic change
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)

        conversation = [
            "Tell me about Python",
            "By the way, what about JavaScript?",
            "How do they compare?"
        ]

        print("\n上下文切換測試:")
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
        print("✅ 上下文切換完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def follow_up_questions():
    """
    追問處理
    """
    print("\n" + "=" * 60)
    print("追問處理示例")
    print("=" * 60)

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo
    """

    colang_content = """
    # 定義追問模式
    define user ask follow up
      "what about"
      "and"
      "also"
      "how about"

    # 追問流程
    define flow handle follow up
      user ask follow up
      bot provide additional info

    define bot provide additional info
      "Here's more information about that..."
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)

        conversation = [
            "What is a function in Python?",
            "What about classes?",
            "And decorators?"
        ]

        print("\n追問處理測試:")
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
        print("✅ 追問處理完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def conversation_reset():
    """
    對話重置處理
    """
    print("\n" + "=" * 60)
    print("對話重置處理示例")
    print("=" * 60)

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo
    """

    colang_content = """
    # 定義重置觸發器
    define user request reset
      "start over"
      "new conversation"
      "reset"

    define bot confirm reset
      "Let's start fresh. How can I help you?"

    define flow reset conversation
      user request reset
      bot confirm reset
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)

        conversation = [
            "Tell me about Python",
            "Start over",
            "What is JavaScript?"
        ]

        print("\n對話重置測試:")
        print("-" * 60)

        messages = []
        for i, turn in enumerate(conversation):
            if "start over" in turn.lower():
                # 重置對話
                messages = []

            messages.append({"role": "user", "content": turn})

            print(f"\n👤 用戶: {turn}")

            response = rails.generate(messages=messages)

            print(f"🤖 助手: {response['content']}")

            messages.append({
                "role": "assistant",
                "content": response['content']
            })

        print("\n" + "-" * 60)
        print("✅ 對話重置完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def conversation_history_management():
    """
    對話歷史管理
    """
    print("\n" + "=" * 60)
    print("對話歷史管理示例")
    print("=" * 60)

    @action(name="summarize_history")
    async def summarize_history(context: dict):
        """總結對話歷史"""
        # 實際應用中會分析整個對話歷史
        # 這裡簡化處理
        messages = context.get("messages", [])

        if len(messages) > 10:
            return "We've had a long conversation. Would you like me to summarize?"

        return None

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    rails:
      dialog:
        flows:
          - manage history
    """

    colang_content = """
    define flow manage history
      user ...
      $summary = execute summarize_history
      bot ...
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)
        rails.register_action(summarize_history)

        conversation = [
            "Tell me about Python",
            "What are variables?",
            "Explain functions",
            "How about classes?"
        ]

        print("\n對話歷史管理測試:")
        print("-" * 60)

        messages = []
        for turn in conversation:
            messages.append({"role": "user", "content": turn})

            print(f"\n👤 用戶: {turn}")

            response = rails.generate(messages=messages)

            print(f"🤖 助手: {response['content']}")
            print(f"   (歷史長度: {len(messages) + 1})")

            messages.append({
                "role": "assistant",
                "content": response['content']
            })

        print("\n" + "-" * 60)
        print("✅ 歷史管理完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def main():
    """
    主函數：運行所有多輪對話示例
    """
    print("\n🛡️  NeMo Guardrails - 多輪對話")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        return

    # 運行各種多輪對話示例
    basic_multi_turn()
    stateful_conversation()
    context_switching()
    follow_up_questions()
    conversation_reset()
    conversation_history_management()

    print("\n" + "=" * 60)
    print("✅ 所有多輪對話示例執行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
