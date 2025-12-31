"""
Guardrails AI - 毒性檢測示例
展示如何檢測和過濾有毒、不當或攻擊性內容
"""

import os
from guardrails import Guard
from guardrails.hub import ToxicLanguage
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


def basic_toxicity_detection():
    """
    基本毒性檢測
    """
    print("=" * 60)
    print("基本毒性檢測示例")
    print("=" * 60)

    # 使用 ToxicLanguage 驗證器
    guard = Guard().use(
        ToxicLanguage(
            threshold=0.5,  # 毒性閾值（0-1）
            validation_method="sentence",
            on_fail="exception"
        )
    )

    prompt = "生成一段關於團隊合作的積極文字"

    print(f"\n提示: {prompt}")
    print("毒性閾值: 0.5")

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=150,
        )

        print(f"\n輸出: {result.validated_output}")
        print(f"✅ 內容安全，無毒性")

    except Exception as e:
        print(f"⚠️  檢測到有毒內容")
        print(f"詳情: {str(e)}")


def toxicity_with_filtering():
    """
    毒性檢測與過濾
    """
    print("\n" + "=" * 60)
    print("毒性過濾示例")
    print("=" * 60)

    # 使用 filter 策略自動移除有毒內容
    guard = Guard().use(
        ToxicLanguage(
            threshold=0.3,
            validation_method="sentence",
            on_fail="filter"
        )
    )

    prompt = "生成一段產品評論"

    print(f"\n提示: {prompt}")
    print("策略: 過濾有毒內容")

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=200,
        )

        print(f"\n過濾後的輸出: {result.validated_output}")
        print(f"✅ 有毒內容已被過濾")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def severity_levels():
    """
    不同嚴重程度的毒性檢測
    """
    print("\n" + "=" * 60)
    print("毒性嚴重程度檢測示例")
    print("=" * 60)

    thresholds = [
        (0.1, "極低容忍度"),
        (0.3, "低容忍度"),
        (0.5, "中等容忍度"),
        (0.7, "高容忍度")
    ]

    prompt = "生成一段中性的產品描述"

    for threshold, level in thresholds:
        print(f"\n{level}（閾值: {threshold}）")

        guard = Guard().use(
            ToxicLanguage(
                threshold=threshold,
                validation_method="sentence",
                on_fail="exception"
            )
        )

        try:
            result = guard(
                llm_api=openai.chat.completions.create,
                prompt=prompt,
                model="gpt-3.5-turbo",
                max_tokens=100,
            )

            print(f"✅ 通過驗證")
            print(f"輸出: {result.validated_output[:100]}...")

        except Exception as e:
            print(f"⚠️  未通過驗證")


def profanity_detection():
    """
    褻瀆語言檢測
    """
    print("\n" + "=" * 60)
    print("褻瀆語言檢測示例")
    print("=" * 60)

    # 簡化的褻瀆詞列表
    profanity_list = [
        "damn", "hell", "stupid", "idiot", "fool"
    ]

    def contains_profanity(text):
        """檢查是否包含褻瀆詞"""
        text_lower = text.lower()
        found = [word for word in profanity_list if word in text_lower]
        return found

    prompt = "生成一段專業的商務溝通文字"

    print(f"\n提示: {prompt}")
    print(f"檢測詞彙: {', '.join(profanity_list)}")

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
        )

        text = response.choices[0].message.content
        profanities = contains_profanity(text)

        print(f"\n輸出: {text}")

        if profanities:
            print(f"\n⚠️  檢測到褻瀆詞: {', '.join(profanities)}")
        else:
            print(f"\n✅ 未檢測到褻瀆詞")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def hate_speech_detection():
    """
    仇恨言論檢測
    """
    print("\n" + "=" * 60)
    print("仇恨言論檢測示例")
    print("=" * 60)

    # 使用較低的閾值以嚴格檢測仇恨言論
    guard = Guard().use(
        ToxicLanguage(
            threshold=0.2,
            validation_method="full",  # 檢查整個文本
            on_fail="exception"
        )
    )

    prompt = "生成一段包容性的多元文化宣言"

    print(f"\n提示: {prompt}")
    print("檢測: 仇恨言論（低閾值）")

    try:
        result = guard(
            llm_api=openai.chat.completions.create,
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=150,
        )

        print(f"\n輸出: {result.validated_output}")
        print(f"✅ 內容安全，無仇恨言論")

    except Exception as e:
        print(f"⚠️  檢測到潛在仇恨言論")
        print(f"詳情: {str(e)}")


def sentiment_based_toxicity():
    """
    基於情感的毒性分析
    """
    print("\n" + "=" * 60)
    print("情感毒性分析示例")
    print("=" * 60)

    def analyze_sentiment(text):
        """
        簡單的情感分析
        返回: positive, neutral, negative
        """
        positive_words = ['good', 'great', 'excellent', 'wonderful', 'amazing', 'love']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'hate', 'worst']

        text_lower = text.lower()

        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)

        if pos_count > neg_count:
            return "positive", pos_count - neg_count
        elif neg_count > pos_count:
            return "negative", neg_count - pos_count
        else:
            return "neutral", 0

    prompt = "寫一段客戶服務回覆"

    print(f"\n提示: {prompt}")

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
        )

        text = response.choices[0].message.content
        sentiment, score = analyze_sentiment(text)

        print(f"\n輸出: {text}")
        print(f"\n情感分析:")
        print(f"  類型: {sentiment}")
        print(f"  分數: {score}")

        if sentiment == "negative" and score > 3:
            print(f"⚠️  檢測到高度負面情感")
        else:
            print(f"✅ 情感適當")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def aggressive_language_detection():
    """
    攻擊性語言檢測
    """
    print("\n" + "=" * 60)
    print("攻擊性語言檢測示例")
    print("=" * 60)

    aggressive_markers = [
        "attack", "fight", "destroy", "kill", "war",
        "violent", "aggressive", "hostile"
    ]

    def detect_aggression(text):
        """檢測攻擊性語言"""
        text_lower = text.lower()
        found = [word for word in aggressive_markers if word in text_lower]
        return found

    prompt = "生成一段和平友善的社區公告"

    print(f"\n提示: {prompt}")
    print(f"檢測詞彙: {', '.join(aggressive_markers[:5])}...")

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
        )

        text = response.choices[0].message.content
        aggressive_words = detect_aggression(text)

        print(f"\n輸出: {text}")

        if aggressive_words:
            print(f"\n⚠️  檢測到攻擊性詞彙: {', '.join(aggressive_words)}")
        else:
            print(f"\n✅ 未檢測到攻擊性語言")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def content_moderation_pipeline():
    """
    完整的內容審核流程
    """
    print("\n" + "=" * 60)
    print("完整內容審核流程示例")
    print("=" * 60)

    class ContentModerator:
        """內容審核器"""

        def __init__(self):
            self.profanity_list = ["damn", "hell", "stupid"]
            self.aggressive_words = ["attack", "fight", "destroy"]

        def check_profanity(self, text):
            """檢查褻瀆詞"""
            text_lower = text.lower()
            return any(word in text_lower for word in self.profanity_list)

        def check_aggression(self, text):
            """檢查攻擊性"""
            text_lower = text.lower()
            return any(word in text_lower for word in self.aggressive_words)

        def moderate(self, text):
            """完整審核"""
            issues = []

            if self.check_profanity(text):
                issues.append("褻瀆語言")

            if self.check_aggression(text):
                issues.append("攻擊性語言")

            return {
                "safe": len(issues) == 0,
                "issues": issues,
                "text": text
            }

    moderator = ContentModerator()
    prompt = "生成一段友好的歡迎詞"

    print(f"\n提示: {prompt}")

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
        )

        text = response.choices[0].message.content
        result = moderator.moderate(text)

        print(f"\n輸出: {result['text']}")
        print(f"\n審核結果:")
        print(f"  安全: {'✅ 是' if result['safe'] else '⚠️  否'}")

        if result['issues']:
            print(f"  問題: {', '.join(result['issues'])}")
        else:
            print(f"  問題: 無")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def multilevel_toxicity_check():
    """
    多級毒性檢查
    """
    print("\n" + "=" * 60)
    print("多級毒性檢查示例")
    print("=" * 60)

    levels = [
        {"name": "Level 1: 嚴重", "threshold": 0.8},
        {"name": "Level 2: 中等", "threshold": 0.5},
        {"name": "Level 3: 輕微", "threshold": 0.2}
    ]

    prompt = "生成一段中性的新聞報導"

    print(f"\n提示: {prompt}")

    for level in levels:
        print(f"\n{level['name']}（閾值: {level['threshold']}）")

        guard = Guard().use(
            ToxicLanguage(
                threshold=level['threshold'],
                validation_method="sentence",
                on_fail="exception"
            )
        )

        try:
            result = guard(
                llm_api=openai.chat.completions.create,
                prompt=prompt,
                model="gpt-3.5-turbo",
                max_tokens=150,
            )

            print(f"✅ 通過 {level['name']}")

        except Exception as e:
            print(f"⚠️  未通過 {level['name']}")
            break
    else:
        print(f"\n✅ 通過所有級別的毒性檢查")


def main():
    """
    主函數：運行所有毒性檢測示例
    """
    print("\n🛡️  Guardrails AI - 毒性檢測")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        return

    # 運行各種毒性檢測示例
    basic_toxicity_detection()
    toxicity_with_filtering()
    severity_levels()
    profanity_detection()
    hate_speech_detection()
    sentiment_based_toxicity()
    aggressive_language_detection()
    content_moderation_pipeline()
    multilevel_toxicity_check()

    print("\n" + "=" * 60)
    print("✅ 所有毒性檢測示例執行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
