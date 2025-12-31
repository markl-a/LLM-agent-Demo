"""
Marvin 分類任務示例

本示例展示：
1. marvin.classify() 的使用
2. 枚舉分類
3. 多標籤分類
4. 自定義標籤
5. 置信度評分

運行方式：
    python 03_分類任務.py
"""

import os
import marvin
from enum import Enum
from typing import List, Literal
from pydantic import BaseModel


# ==================== 簡單分類 ====================

def example_simple_classification():
    """示例 1: 簡單文本分類"""
    print("\n" + "="*60)
    print("示例 1: 簡單文本分類")
    print("="*60)

    try:
        # 定義分類標籤
        labels = ["技術", "體育", "娛樂", "政治", "財經"]

        # 測試文本
        texts = [
            "Python 是一門優秀的編程語言",
            "NBA 總決賽即將開始",
            "最新電影票房突破10億",
            "政府宣布新的經濟政策",
            "股市今日大漲3%"
        ]

        print("文本分類結果:\n")
        for text in texts:
            category = marvin.classify(text, labels=labels)
            print(f"📄 \"{text}\"")
            print(f"   → 分類: {category}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 枚舉分類 ====================

class Sentiment(str, Enum):
    """情感分類枚舉"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class Priority(str, Enum):
    """優先級枚舉"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    URGENT = "urgent"


class Language(str, Enum):
    """語言分類"""
    CHINESE = "chinese"
    ENGLISH = "english"
    JAPANESE = "japanese"
    KOREAN = "korean"
    SPANISH = "spanish"


def example_enum_classification():
    """示例 2: 使用枚舉進行分類"""
    print("\n" + "="*60)
    print("示例 2: 使用枚舉進行分類")
    print("="*60)

    try:
        # 情感分類
        print("情感分類:")
        sentiment_texts = [
            "這個產品太棒了！強烈推薦！",
            "服務很差，非常失望。",
            "還可以，沒什麼特別的。",
            "Amazing experience! Love it!",
            "Terrible, waste of money."
        ]

        for text in sentiment_texts:
            sentiment = marvin.classify(text, labels=Sentiment)
            emoji = {
                Sentiment.POSITIVE: "😊",
                Sentiment.NEGATIVE: "😞",
                Sentiment.NEUTRAL: "😐"
            }[sentiment]
            print(f"{emoji} {text[:40]:<40} → {sentiment.value}")

        # 優先級分類
        print("\n優先級分類:")
        task_texts = [
            "系統崩潰！所有用戶無法訪問！",
            "下週需要更新文檔",
            "有空的時候優化一下代碼",
            "客戶投訴需要立即處理"
        ]

        for task in task_texts:
            priority = marvin.classify(task, labels=Priority)
            print(f"📋 {task}")
            print(f"   優先級: {priority.value}\n")

        # 語言分類
        print("語言分類:")
        language_texts = [
            "你好，很高興見到你",
            "Hello, how are you?",
            "こんにちは、元気ですか？",
            "안녕하세요",
            "Hola, ¿cómo estás?"
        ]

        for text in language_texts:
            language = marvin.classify(text, labels=Language)
            print(f"🌍 {text} → {language.value}")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 多類別分類 ====================

class ContentType(str, Enum):
    """內容類型"""
    QUESTION = "question"
    STATEMENT = "statement"
    COMMAND = "command"
    GREETING = "greeting"
    COMPLAINT = "complaint"
    PRAISE = "praise"


class Topic(str, Enum):
    """主題分類"""
    TECHNOLOGY = "technology"
    BUSINESS = "business"
    HEALTH = "health"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    SCIENCE = "science"
    SPORTS = "sports"


def example_multi_category():
    """示例 3: 多類別分類"""
    print("\n" + "="*60)
    print("示例 3: 多類別分類")
    print("="*60)

    try:
        messages = [
            "你能幫我解釋一下量子計算嗎？",
            "謝謝你的幫助，非常有用！",
            "請立即處理這個問題",
            "你好！今天天氣不錯。",
            "你們的服務太差了！"
        ]

        print("消息分類:\n")
        for msg in messages:
            # 同時分類類型和主題（如果適用）
            content_type = marvin.classify(msg, labels=ContentType)

            print(f"💬 {msg}")
            print(f"   類型: {content_type.value}")

            # 如果不是問候或命令，嘗試識別主題
            if content_type not in [ContentType.GREETING, ContentType.COMMAND]:
                try:
                    topic = marvin.classify(msg, labels=Topic)
                    print(f"   主題: {topic.value}")
                except:
                    print(f"   主題: 無法確定")
            print()

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 字面量類型分類 ====================

def example_literal_classification():
    """示例 4: 使用字面量類型"""
    print("\n" + "="*60)
    print("示例 4: 使用字面量類型")
    print("="*60)

    try:
        # 使用 Literal 類型
        Size = Literal["small", "medium", "large", "extra-large"]

        size_descriptions = [
            "我需要一個小杯咖啡",
            "給我一個大份的",
            "中杯就好",
            "要最大號的"
        ]

        print("尺寸分類:")
        for desc in size_descriptions:
            # 注意：Literal 需要在函數定義中使用
            # 這裡我們使用列表代替
            size = marvin.classify(
                desc,
                labels=["small", "medium", "large", "extra-large"]
            )
            print(f"📏 {desc} → {size}")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 複雜分類場景 ====================

class EmailCategory(str, Enum):
    """郵件分類"""
    SPAM = "spam"
    PROMOTION = "promotion"
    SOCIAL = "social"
    WORK = "work"
    PERSONAL = "personal"
    URGENT = "urgent"


class Intent(str, Enum):
    """用戶意圖"""
    INFORMATION_REQUEST = "information_request"
    COMPLAINT = "complaint"
    PURCHASE = "purchase"
    SUPPORT = "support"
    FEEDBACK = "feedback"
    CANCEL = "cancel"


def example_complex_classification():
    """示例 5: 複雜分類場景"""
    print("\n" + "="*60)
    print("示例 5: 複雜分類場景")
    print("="*60)

    try:
        # 郵件分類
        print("郵件分類:")
        emails = [
            {
                "subject": "限時優惠！全場5折！",
                "preview": "親愛的客戶，我們的年度大促銷開始了..."
            },
            {
                "subject": "會議通知",
                "preview": "明天下午3點在會議室A開會..."
            },
            {
                "subject": "恭喜中獎！",
                "preview": "你已被選中，點擊領取100萬獎金..."
            },
            {
                "subject": "緊急：服務器宕機",
                "preview": "生產環境服務器無法訪問，需要立即處理..."
            }
        ]

        for email in emails:
            full_text = f"{email['subject']} - {email['preview']}"
            category = marvin.classify(full_text, labels=EmailCategory)

            icon = {
                EmailCategory.SPAM: "🚫",
                EmailCategory.PROMOTION: "🎁",
                EmailCategory.SOCIAL: "👥",
                EmailCategory.WORK: "💼",
                EmailCategory.PERSONAL: "📧",
                EmailCategory.URGENT: "🚨"
            }[category]

            print(f"{icon} {email['subject']}")
            print(f"   分類: {category.value}\n")

        # 用戶意圖識別
        print("\n用戶意圖識別:")
        user_messages = [
            "我想了解一下這個產品的功能",
            "我要投訴，你們的服務太差了",
            "我想購買Pro版本",
            "我的帳號登錄不了，需要幫助",
            "你們的應用很好用，給個五星好評",
            "我要取消訂閱"
        ]

        for msg in user_messages:
            intent = marvin.classify(msg, labels=Intent)
            print(f"💬 {msg}")
            print(f"   意圖: {intent.value}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 批量分類 ====================

def example_batch_classification():
    """示例 6: 批量分類"""
    print("\n" + "="*60)
    print("示例 6: 批量分類")
    print("="*60)

    try:
        # 批量處理評論
        reviews = [
            "產品質量很好，非常滿意！",
            "配送速度太慢了",
            "價格合理，性價比高",
            "客服態度很差",
            "包裝完好，商品完美",
            "與描述不符，要退貨",
            "物流很快，好評！",
            "質量一般般"
        ]

        print("批量評論分類:\n")

        # 統計各類情感的數量
        sentiment_count = {
            "positive": 0,
            "negative": 0,
            "neutral": 0
        }

        for review in reviews:
            sentiment = marvin.classify(review, labels=Sentiment)

            emoji = {
                Sentiment.POSITIVE: "👍",
                Sentiment.NEGATIVE: "👎",
                Sentiment.NEUTRAL: "🤷"
            }[sentiment]

            print(f"{emoji} {review}")
            sentiment_count[sentiment.value] += 1

        # 顯示統計結果
        print(f"\n統計結果:")
        print(f"  正面: {sentiment_count['positive']} 條")
        print(f"  負面: {sentiment_count['negative']} 條")
        print(f"  中性: {sentiment_count['neutral']} 條")

        total = len(reviews)
        positive_rate = (sentiment_count['positive'] / total) * 100
        print(f"\n  正面率: {positive_rate:.1f}%")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 條件分類 ====================

class AgeGroup(str, Enum):
    """年齡組"""
    CHILD = "child"
    TEENAGER = "teenager"
    ADULT = "adult"
    SENIOR = "senior"


class SkillLevel(str, Enum):
    """技能等級"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


def example_contextual_classification():
    """示例 7: 條件分類"""
    print("\n" + "="*60)
    print("示例 7: 條件分類")
    print("="*60)

    try:
        # 根據描述推斷年齡組
        print("年齡組推斷:")
        descriptions = [
            "他還在上小學",
            "她剛上高中",
            "他是一名職場人士",
            "她已經退休了"
        ]

        for desc in descriptions:
            age_group = marvin.classify(desc, labels=AgeGroup)
            print(f"👤 {desc} → {age_group.value}")

        # 根據表現評估技能等級
        print("\n技能等級評估:")
        performances = [
            "剛開始學習Python，還在看教程",
            "能獨立完成中等難度的項目",
            "精通多種框架，能解決複雜問題",
            "是某個領域的專家，經常發表論文"
        ]

        for perf in performances:
            skill = marvin.classify(perf, labels=SkillLevel)
            print(f"💻 {perf[:30]}...")
            print(f"   等級: {skill.value}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║        Marvin 分類任務示例                ║
╚══════════════════════════════════════════╝

marvin.classify() 功能:
✅ 簡單直觀的 API
✅ 支持枚舉和字面量
✅ 多種分類場景
✅ 高準確度
✅ 批量處理
    """)

    # 檢查環境
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 請設置 OPENAI_API_KEY 環境變量")
        return

    # 配置 Marvin
    marvin.settings.openai.api_key = os.getenv("OPENAI_API_KEY")

    # 運行示例
    example_simple_classification()
    example_enum_classification()
    example_multi_category()
    example_literal_classification()
    example_complex_classification()
    example_batch_classification()
    example_contextual_classification()

    print("\n" + "="*60)
    print("✅ 所有示例運行完成！")
    print("="*60)


if __name__ == "__main__":
    main()
