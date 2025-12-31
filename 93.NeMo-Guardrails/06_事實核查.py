"""
NeMo Guardrails - 事實核查示例
展示如何驗證 LLM 輸出的準確性
"""

import os
from nemoguardrails import RailsConfig, LLMRails
from nemoguardrails.actions import action

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")


def basic_fact_checking():
    """
    基本事實核查
    """
    print("=" * 60)
    print("基本事實核查示例")
    print("=" * 60)

    @action(name="check_facts")
    async def check_facts(context: dict):
        """簡單的事實核查"""
        bot_message = context.get("bot_message", "")

        # 檢測過度絕對的陳述
        absolute_terms = ["always", "never", "impossible", "certainly", "100%"]

        has_absolute = any(term in bot_message.lower() for term in absolute_terms)

        return not has_absolute

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    rails:
      output:
        flows:
          - verify facts
    """

    colang_content = """
    define flow verify facts
      bot ...
      $facts_verified = execute check_facts

      if not $facts_verified
        bot add disclaimer
        stop

    define bot add disclaimer
      "Please note that this information may not be entirely accurate. I recommend verifying from authoritative sources."
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
            "What are some advantages of Python?",
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


def source_verification():
    """
    來源驗證
    """
    print("\n" + "=" * 60)
    print("來源驗證示例")
    print("=" * 60)

    @action(name="verify_sources")
    async def verify_sources(context: dict):
        """驗證回應是否包含來源"""
        bot_message = context.get("bot_message", "")

        # 檢查是否提到來源
        source_indicators = ["according to", "based on", "research shows", "studies indicate"]

        has_source = any(indicator in bot_message.lower() for indicator in source_indicators)

        # 對於事實性陳述，應該有來源
        factual_keywords = ["statistics", "percentage", "year", "discovered", "invented"]

        is_factual = any(keyword in bot_message.lower() for keyword in factual_keywords)

        if is_factual and not has_source:
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
          - check sources
    """

    colang_content = """
    define flow check sources
      bot ...
      $has_sources = execute verify_sources

      if not $has_sources
        bot request sources
        stop

    define bot request sources
      "For factual claims, please verify information from authoritative sources."
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)
        rails.register_action(verify_sources)

        test_inputs = [
            "When was Python created?",
            "What is a function?",
            "How many Python users are there?"
        ]

        print("\n測試來源驗證:")
        print("-" * 60)

        for user_input in test_inputs:
            print(f"\n👤 用戶: {user_input}")

            response = rails.generate(messages=[{
                "role": "user",
                "content": user_input
            }])

            print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 來源驗證完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def confidence_scoring():
    """
    可信度評分
    """
    print("\n" + "=" * 60)
    print("可信度評分示例")
    print("=" * 60)

    @action(name="score_confidence")
    async def score_confidence(context: dict):
        """評估回應的可信度"""
        bot_message = context.get("bot_message", "")

        confidence = 1.0

        # 降低可信度的因素
        if any(term in bot_message.lower() for term in ["might", "maybe", "possibly", "perhaps"]):
            confidence -= 0.2

        if any(term in bot_message.lower() for term in ["always", "never", "certainly"]):
            confidence -= 0.3

        if len(bot_message) > 500:
            confidence -= 0.1

        return max(0.0, min(1.0, confidence))

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    rails:
      output:
        flows:
          - evaluate confidence
    """

    colang_content = """
    define flow evaluate confidence
      bot ...
      $confidence = execute score_confidence

      if $confidence < 0.5
        bot low confidence warning
        stop

    define bot low confidence warning
      "Note: This response has low confidence. Please verify the information."
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)
        rails.register_action(score_confidence)

        test_inputs = [
            "What is Python used for?",
            "Is Python always better than Java?",
            "Tell me everything about Python in detail"
        ]

        print("\n測試可信度評分:")
        print("-" * 60)

        for user_input in test_inputs:
            print(f"\n👤 用戶: {user_input}")

            response = rails.generate(messages=[{
                "role": "user",
                "content": user_input
            }])

            print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 可信度評分完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def cross_reference_checking():
    """
    交叉引用檢查
    """
    print("\n" + "=" * 60)
    print("交叉引用檢查示例")
    print("=" * 60)

    @action(name="cross_reference")
    async def cross_reference(context: dict):
        """交叉引用檢查（模擬）"""
        bot_message = context.get("bot_message", "")

        # 模擬檢查多個來源
        # 實際應用中會調用外部 API

        # 簡化版：檢查是否包含具體數據
        has_data = any(char.isdigit() for char in bot_message)

        if has_data:
            # 如果包含數據，標記需要驗證
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
          - cross reference facts
    """

    colang_content = """
    define flow cross reference facts
      bot ...
      $verified = execute cross_reference

      if not $verified
        bot suggest verification
        stop

    define bot suggest verification
      "This information contains specific data. Please verify with official sources."
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)
        rails.register_action(cross_reference)

        test_inputs = [
            "What is a variable?",
            "How many versions of Python exist?",
            "Explain loops"
        ]

        print("\n測試交叉引用:")
        print("-" * 60)

        for user_input in test_inputs:
            print(f"\n👤 用戶: {user_input}")

            response = rails.generate(messages=[{
                "role": "user",
                "content": user_input
            }])

            print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 交叉引用完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def hallucination_detection():
    """
    幻覺檢測
    """
    print("\n" + "=" * 60)
    print("幻覺檢測示例")
    print("=" * 60)

    @action(name="detect_hallucination")
    async def detect_hallucination(context: dict):
        """檢測可能的幻覺內容"""
        bot_message = context.get("bot_message", "")

        # 檢測可疑模式
        suspicious_patterns = [
            "as far as i know",
            "i believe",
            "i think",
            "probably",
            "most likely"
        ]

        has_suspicious = any(pattern in bot_message.lower() for pattern in suspicious_patterns)

        # 檢測過於具體的細節（可能是編造的）
        has_specific_numbers = len([c for c in bot_message if c.isdigit()]) > 10

        if has_suspicious or has_specific_numbers:
            return True

        return False

    config_yaml = """
    models:
      - type: main
        engine: openai
        model: gpt-3.5-turbo

    rails:
      output:
        flows:
          - detect hallucinations
    """

    colang_content = """
    define flow detect hallucinations
      bot ...
      $might_hallucinate = execute detect_hallucination

      if $might_hallucinate
        bot warn possible hallucination
        stop

    define bot warn possible hallucination
      "Please note: Some details in this response may not be entirely accurate. Verify important information."
    """

    try:
        config = RailsConfig.from_content(
            config=config_yaml,
            colang_content=colang_content
        )

        rails = LLMRails(config)
        rails.register_action(detect_hallucination)

        test_inputs = [
            "What is Python?",
            "Tell me specific statistics about Python usage",
            "I think Python was created in which year?"
        ]

        print("\n測試幻覺檢測:")
        print("-" * 60)

        for user_input in test_inputs:
            print(f"\n👤 用戶: {user_input}")

            response = rails.generate(messages=[{
                "role": "user",
                "content": user_input
            }])

            print(f"🤖 助手: {response['content']}")

        print("\n" + "-" * 60)
        print("✅ 幻覺檢測完成")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def main():
    """
    主函數：運行所有事實核查示例
    """
    print("\n🛡️  NeMo Guardrails - 事實核查")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        return

    # 運行各種事實核查示例
    basic_fact_checking()
    source_verification()
    confidence_scoring()
    cross_reference_checking()
    hallucination_detection()

    print("\n" + "=" * 60)
    print("✅ 所有事實核查示例執行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
