"""
NeMo Guardrails - 主題控制示例
展示如何限制對話主題在特定範圍內
"""

import os
from nemoguardrails import RailsConfig, LLMRails
from nemoguardrails.actions import action

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")


def basic_topic_restriction():
    """
    基本主題限制
    """
    print("=" * 60)
    print("基本主題限制示例")
    print("=" * 60)

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    rails:
      input:
        flows:
          - restrict topics
    """

    colang_content = """
    # 定義允許的主題
    define user ask about programming
      "how to code"
      "programming language"
      "software development"

    # 定義不允許的主題
    define user ask about politics
      "political"
      "government"
      "election"

    define user ask about religion
      "religious"
      "faith"
      "belief system"

    # 拒絕不允許的主題
    define bot refuse politics
      "I'm a programming assistant and cannot discuss political topics."

    define bot refuse religion
      "I'm focused on programming topics and cannot discuss religious matters."

    # 主題限制流程
    define flow restrict topics
      user ask about politics
      bot refuse politics
      stop

    or user ask about religion
      bot refuse religion
      stop
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)

        test_inputs = [
            "How do I learn Python?",
            "What do you think about the current government?",
            "Can you help me with JavaScript?",
            "What's your religious belief?"
        ]

        print("\n測試主題限制:")
        print("-" * 60)

        for user_input in test_inputs:
            print(f"\n👤 用戶: {user_input}")

            response = rails.generate(messages=[{
                "role": "user",
                "content": user_input
            }])

            print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 主題限制測試完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def whitelist_topics():
    """
    白名單主題模式
    """
    print("\n" + "=" * 60)
    print("白名單主題模式示例")
    print("=" * 60)

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    rails:
      input:
        flows:
          - check allowed topics
    """

    colang_content = """
    # 定義白名單主題
    define user ask about python
      "python"
      "django"
      "flask"

    define user ask about javascript
      "javascript"
      "react"
      "node"

    define user ask about databases
      "database"
      "sql"
      "mongodb"

    # 定義通用的拒絕回應
    define bot refuse off topic
      "I can only help with Python, JavaScript, and Database topics."

    # 白名單檢查流程
    define flow check allowed topics
      user ...

      # 如果不是允許的主題，拒絕
      if not (user ask about python or user ask about javascript or user ask about databases)
        bot refuse off topic
        stop
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)

        test_inputs = [
            "How do I use Flask?",
            "Tell me about React",
            "What is SQL?",
            "Can you help me with Java?"
        ]

        print("\n測試白名單主題:")
        print("-" * 60)

        for user_input in test_inputs:
            print(f"\n👤 用戶: {user_input}")

            response = rails.generate(messages=[{
                "role": "user",
                "content": user_input
            }])

            print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 白名單測試完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def domain_specific_assistant():
    """
    領域專用助手
    """
    print("\n" + "=" * 60)
    print("領域專用助手示例")
    print("=" * 60)

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    instructions:
      - type: general
        content: |
          You are a Python programming assistant.
          You can only help with Python-related questions.
          Politely decline questions about other topics.

    rails:
      input:
        flows:
          - check python topic
    """

    colang_content = """
    # 定義 Python 相關主題
    define user ask about python
      "python"
      "pip"
      "virtualenv"
      "pandas"
      "numpy"

    # 定義其他編程語言
    define user ask about other language
      "java"
      "c++"
      "ruby"
      "go"
      "rust"

    # 拒絕其他語言
    define bot refuse other language
      "I specialize in Python only. For other languages, please consult a general programming assistant."

    define flow check python topic
      user ask about other language
      bot refuse other language
      stop
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)

        test_inputs = [
            "How do I use pandas?",
            "What's the difference between Java and Python?",
            "Explain Python decorators",
            "How do I compile C++ code?"
        ]

        print("\n測試領域專用助手:")
        print("-" * 60)

        for user_input in test_inputs:
            print(f"\n👤 用戶: {user_input}")

            response = rails.generate(messages=[{
                "role": "user",
                "content": user_input
            }])

            print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 領域專用測試完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def dynamic_topic_classification():
    """
    動態主題分類
    """
    print("\n" + "=" * 60)
    print("動態主題分類示例")
    print("=" * 60)

    @action(name="classify_topic")
    async def classify_topic(context: dict):
        """分類用戶輸入的主題"""
        user_message = context.get("user_message", "").lower()

        # 簡單的主題分類
        if any(word in user_message for word in ["python", "programming", "code"]):
            return "programming"
        elif any(word in user_message for word in ["weather", "temperature", "forecast"]):
            return "weather"
        elif any(word in user_message for word in ["news", "politics", "election"]):
            return "news"
        else:
            return "unknown"

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    rails:
      input:
        flows:
          - classify and check topic
    """

    colang_content = """
    define flow classify and check topic
      user ...
      $topic = execute classify_topic

      if $topic == "news"
        bot refuse news topic
        stop
      elif $topic == "unknown"
        bot ask clarification
        stop

    define bot refuse news topic
      "I don't discuss news or political topics."

    define bot ask clarification
      "I'm not sure what topic you're asking about. Could you be more specific?"
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)
        rails.register_action(classify_topic)

        test_inputs = [
            "How do I learn Python?",
            "What's the weather like?",
            "Tell me the latest news",
            "Something random"
        ]

        print("\n測試動態主題分類:")
        print("-" * 60)

        for user_input in test_inputs:
            print(f"\n👤 用戶: {user_input}")

            response = rails.generate(messages=[{
                "role": "user",
                "content": user_input
            }])

            print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 動態分類完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def context_aware_topic_control():
    """
    上下文感知的主題控制
    """
    print("\n" + "=" * 60)
    print("上下文感知主題控制示例")
    print("=" * 60)

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    rails:
      dialog:
        flows:
          - maintain context topic
    """

    colang_content = """
    # 定義對話狀態
    define flow maintain context topic
      user ...
      # 這裡可以檢查對話歷史並維護主題一致性
      bot ...
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)

        # 模擬多輪對話
        conversation = [
            {"role": "user", "content": "Tell me about Python"},
            {"role": "user", "content": "What about its libraries?"},
            {"role": "user", "content": "Can you recommend some?"}
        ]

        print("\n測試上下文感知:")
        print("-" * 60)

        messages = []
        for turn in conversation:
            messages.append(turn)

            print(f"\n👤 用戶: {turn['content']}")

            response = rails.generate(messages=messages)

            print(f"🤖 助手: {response['content']}")

            messages.append({
                "role": "assistant",
                "content": response['content']
            })

        print("\n" + "-" * 60)
        print("✅ 上下文感知測試完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def main():
    """
    主函數：運行所有主題控制示例
    """
    print("\n🛡️  NeMo Guardrails - 主題控制")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        return

    # 運行各種主題控制示例
    basic_topic_restriction()
    whitelist_topics()
    domain_specific_assistant()
    dynamic_topic_classification()
    context_aware_topic_control()

    print("\n" + "=" * 60)
    print("✅ 所有主題控制示例執行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
