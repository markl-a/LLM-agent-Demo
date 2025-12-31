"""
NeMo Guardrails - 快速開始示例
展示 NeMo Guardrails 的基本使用方法
"""

import os
from nemoguardrails import RailsConfig, LLMRails

# 設置 OpenAI API 密鑰
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")


def basic_rails_example():
    """
    最基本的 Rails 示例
    創建一個簡單的對話系統
    """
    print("=" * 60)
    print("基本 Rails 示例")
    print("=" * 60)

    # 定義配置（使用 YAML 格式的字符串）
    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    rails:
      input:
        flows:
          - check greeting

      output:
        flows:
          - check response
    """

    # 定義 Colang 流程
    colang_content = """
    # 定義用戶問候
    define user express greeting
      "hello"
      "hi"
      "hey"

    # 定義機器人問候
    define bot express greeting
      "Hello! I'm a helpful assistant."

    # 問候流程
    define flow greeting
      user express greeting
      bot express greeting
    """

    try:
        # 創建配置（從內存）
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        # 創建 Rails 實例
        rails = LLMRails(config)

        # 測試對話
        messages = [
            "Hello!",
            "What can you do?",
            "Tell me about Python"
        ]

        print("\n開始對話:")
        print("-" * 60)

        for user_message in messages:
            print(f"\n👤 用戶: {user_message}")

            response = rails.generate(messages=[{
                "role": "user",
                "content": user_message
            }])

            bot_message = response["content"]
            print(f"🤖 助手: {bot_message}")

        print("\n" + "-" * 60)
        print("✅ 對話完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def simple_topic_control():
    """
    簡單的主題控制示例
    """
    print("\n" + "=" * 60)
    print("簡單主題控制示例")
    print("=" * 60)

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    rails:
      input:
        flows:
          - check topic
    """

    colang_content = """
    # 定義允許的主題
    define user ask about programming
      "tell me about Python"
      "how to code"
      "programming tutorial"

    define user ask about cooking
      "how to cook"
      "recipe for"
      "cooking tips"

    # 定義機器人回應
    define bot refuse cooking topic
      "I'm sorry, I can only help with programming topics."

    # 主題控制流程
    define flow topic control
      user ask about cooking
      bot refuse cooking topic
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)

        test_messages = [
            "How do I learn Python?",
            "What's a good recipe for pasta?",
            "Tell me about variables in programming"
        ]

        print("\n測試主題控制:")
        print("-" * 60)

        for msg in test_messages:
            print(f"\n👤 用戶: {msg}")

            response = rails.generate(messages=[{
                "role": "user",
                "content": msg
            }])

            print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 主題控制測試完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def basic_input_rail():
    """
    基本輸入護欄示例
    """
    print("\n" + "=" * 60)
    print("基本輸入護欄示例")
    print("=" * 60)

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    rails:
      input:
        flows:
          - self check input
    """

    colang_content = """
    # 定義不當輸入模式
    define user express inappropriate
      "bad word"
      "offensive content"

    # 定義機器人回應
    define bot refuse inappropriate input
      "I cannot respond to inappropriate content."

    # 輸入檢查流程
    define flow self check input
      user ...
      $allowed = execute self_check_input

      if not $allowed
        bot refuse inappropriate input
        stop
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)

        print("\n測試輸入護欄:")
        print("-" * 60)

        test_message = "Can you help me with Python?"

        print(f"\n👤 用戶: {test_message}")

        response = rails.generate(messages=[{
            "role": "user",
            "content": test_message
        }])

        print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 輸入護欄測試完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def stateless_conversation():
    """
    無狀態對話示例
    """
    print("\n" + "=" * 60)
    print("無狀態對話示例")
    print("=" * 60)

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo
    """

    colang_content = """
    define flow
      user ...
      bot ...
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)

        queries = [
            "What is Python?",
            "How do I install it?",
            "Show me an example"
        ]

        print("\n無狀態對話測試:")
        print("-" * 60)

        for query in queries:
            print(f"\n👤 用戶: {query}")

            # 每次都是新的對話（無狀態）
            response = rails.generate(messages=[{
                "role": "user",
                "content": query
            }])

            print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 無狀態對話測試完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def config_from_dict():
    """
    從字典創建配置示例
    """
    print("\n" + "=" * 60)
    print("從字典創建配置示例")
    print("=" * 60)

    # 使用 Python 字典定義配置
    config_dict = {
        "models": [
            {
                "type": "main",
                "engine": "openai",
                "model": "gpt-3.5-turbo"
            }
        ]
    }

    colang_content = """
    define flow
      user ...
      bot ...
    """

    try:
        # 從字典創建配置
        config = RailsConfig.from_content(
            config=config_dict,
            colang_content=colang_content
        )

        rails = LLMRails(config)

        print("\n使用字典配置的對話:")
        print("-" * 60)

        message = "Explain machine learning in simple terms"

        print(f"\n👤 用戶: {message}")

        response = rails.generate(messages=[{
            "role": "user",
            "content": message
        }])

        print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 字典配置測試完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def main():
    """
    主函數：運行所有快速開始示例
    """
    print("\n🛡️  NeMo Guardrails - 快速開始")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        print("請設置環境變量: export OPENAI_API_KEY='your-api-key'")
        return

    # 運行各種示例
    basic_rails_example()
    simple_topic_control()
    basic_input_rail()
    stateless_conversation()
    config_from_dict()

    print("\n" + "=" * 60)
    print("✅ 所有示例執行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
