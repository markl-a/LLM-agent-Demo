"""
Marvin 快速開始示例

本示例展示：
1. Marvin 的基本概念
2. 環境配置
3. 第一個 AI 函數
4. 基本使用模式

運行方式：
    python 01_快速開始.py

環境要求：
    export OPENAI_API_KEY='your-key-here'
"""

import os
from typing import Optional
import marvin
from pydantic import BaseModel


# ==================== 環境配置 ====================

def setup_environment():
    """
    設置 Marvin 環境
    確保 API 密鑰已配置
    """
    try:
        # 檢查環境變量
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️ 警告: OPENAI_API_KEY 未設置")
            print("請設置環境變量: export OPENAI_API_KEY='your-key-here'")
            return False

        # 配置 Marvin
        marvin.settings.openai.api_key = api_key

        # 可選：配置其他設置
        # marvin.settings.log_level = "INFO"
        # marvin.settings.openai.organization = "your-org-id"

        print("✅ Marvin 環境配置成功")
        return True

    except Exception as e:
        print(f"❌ 環境配置失敗: {e}")
        return False


# ==================== 第一個 AI 函數 ====================

@marvin.fn
def generate_greeting(name: str) -> str:
    """
    為指定的人生成一個友好的問候語

    Args:
        name: 要問候的人的名字

    Returns:
        友好的問候語
    """
    # 函數體可以為空，Marvin 會根據文檔字符串生成實現


@marvin.fn
def translate_text(text: str, target_language: str) -> str:
    """
    將文本翻譯成目標語言

    Args:
        text: 要翻譯的文本
        target_language: 目標語言（如：中文、英文、日文）

    Returns:
        翻譯後的文本
    """


@marvin.fn
def sentiment_analysis(text: str) -> str:
    """
    分析文本的情感傾向
    返回 'positive'、'negative' 或 'neutral'

    Args:
        text: 要分析的文本

    Returns:
        情感分類：positive、negative 或 neutral
    """


# ==================== 基本使用示例 ====================

def example_basic_ai_function():
    """示例 1: 基本 AI 函數使用"""
    print("\n" + "="*50)
    print("示例 1: 基本 AI 函數")
    print("="*50)

    try:
        # 調用 AI 函數就像調用普通函數
        greeting = generate_greeting("小明")
        print(f"✅ 問候語: {greeting}")

        # 再次調用，每次可能得到不同的結果
        greeting2 = generate_greeting("Alice")
        print(f"✅ 問候語: {greeting2}")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_translation():
    """示例 2: 翻譯功能"""
    print("\n" + "="*50)
    print("示例 2: 文本翻譯")
    print("="*50)

    try:
        # 英文翻譯成中文
        result1 = translate_text("Hello, how are you?", "中文")
        print(f"✅ 英文 → 中文: {result1}")

        # 中文翻譯成英文
        result2 = translate_text("你好，很高興見到你", "英文")
        print(f"✅ 中文 → 英文: {result2}")

        # 翻譯成日文
        result3 = translate_text("Good morning", "日文")
        print(f"✅ 英文 → 日文: {result3}")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_sentiment():
    """示例 3: 情感分析"""
    print("\n" + "="*50)
    print("示例 3: 情感分析")
    print("="*50)

    try:
        # 測試不同情感的文本
        texts = [
            "這個產品太棒了！我非常喜歡！",
            "這個服務很糟糕，我很失望。",
            "今天天氣還可以。",
            "Amazing product! Highly recommended!",
            "Terrible experience, won't use again."
        ]

        for text in texts:
            sentiment = sentiment_analysis(text)
            emoji = {
                "positive": "😊",
                "negative": "😞",
                "neutral": "😐"
            }.get(sentiment, "❓")

            print(f"{emoji} \"{text[:30]}...\" → {sentiment}")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 帶類型的 AI 函數 ====================

class Person(BaseModel):
    """人物信息模型"""
    name: str
    age: int
    occupation: str


@marvin.fn
def extract_person_info(text: str) -> Person:
    """
    從文本中提取人物信息

    Args:
        text: 包含人物信息的文本

    Returns:
        Person 對象
    """


def example_structured_output():
    """示例 4: 結構化輸出"""
    print("\n" + "="*50)
    print("示例 4: 結構化輸出")
    print("="*50)

    try:
        # 從文本中提取結構化信息
        text = "張三今年30歲，是一名軟件工程師。"
        person = extract_person_info(text)

        print(f"✅ 提取的信息:")
        print(f"   姓名: {person.name}")
        print(f"   年齡: {person.age}")
        print(f"   職業: {person.occupation}")

        # 處理英文文本
        text2 = "John is a 25-year-old doctor."
        person2 = extract_person_info(text2)

        print(f"\n✅ 提取的信息 (英文):")
        print(f"   Name: {person2.name}")
        print(f"   Age: {person2.age}")
        print(f"   Occupation: {person2.occupation}")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 帶參數的 AI 函數 ====================

@marvin.fn
def generate_story(
    topic: str,
    length: str = "short",
    style: str = "adventure"
) -> str:
    """
    根據主題生成故事

    Args:
        topic: 故事主題
        length: 故事長度（short、medium、long）
        style: 故事風格（adventure、romance、mystery、sci-fi）

    Returns:
        生成的故事
    """


def example_with_parameters():
    """示例 5: 帶參數的 AI 函數"""
    print("\n" + "="*50)
    print("示例 5: 帶參數的 AI 函數")
    print("="*50)

    try:
        # 生成短篇冒險故事
        story1 = generate_story(
            topic="太空探險",
            length="short",
            style="adventure"
        )
        print(f"✅ 冒險故事:\n{story1}\n")

        # 生成浪漫故事
        story2 = generate_story(
            topic="咖啡廳邂逅",
            length="short",
            style="romance"
        )
        print(f"✅ 浪漫故事:\n{story2}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 列表處理 ====================

@marvin.fn
def extract_keywords(text: str, max_keywords: int = 5) -> list[str]:
    """
    從文本中提取關鍵詞

    Args:
        text: 輸入文本
        max_keywords: 最多返回的關鍵詞數量

    Returns:
        關鍵詞列表
    """


def example_list_output():
    """示例 6: 列表輸出"""
    print("\n" + "="*50)
    print("示例 6: 列表輸出")
    print("="*50)

    try:
        text = """
        人工智能正在改變世界。機器學習和深度學習技術使得計算機
        能夠從數據中學習並做出決策。自然語言處理讓機器理解人類語言，
        而計算機視覺則讓機器能夠"看見"世界。
        """

        keywords = extract_keywords(text, max_keywords=5)
        print(f"✅ 提取的關鍵詞:")
        for i, keyword in enumerate(keywords, 1):
            print(f"   {i}. {keyword}")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 錯誤處理 ====================

def example_error_handling():
    """示例 7: 錯誤處理"""
    print("\n" + "="*50)
    print("示例 7: 錯誤處理")
    print("="*50)

    try:
        # 正常調用
        result = sentiment_analysis("這是一個測試")
        print(f"✅ 正常結果: {result}")

    except marvin.exceptions.MarvinError as e:
        print(f"❌ Marvin 錯誤: {e}")
    except Exception as e:
        print(f"❌ 其他錯誤: {e}")


# ==================== 主函數 ====================

def main():
    """
    主函數 - 運行所有示例
    """
    print("""
╔══════════════════════════════════════════╗
║      Marvin 快速開始示例                  ║
╚══════════════════════════════════════════╝

Marvin 是一個輕量級 AI 函數庫，讓你能夠
像使用普通 Python 函數一樣使用 AI 功能。

核心特點:
✅ 簡單的 @marvin.fn 裝飾器
✅ 類型安全的輸入輸出
✅ 自動處理提示詞
✅ Pydantic 模型支持
    """)

    # 設置環境
    if not setup_environment():
        print("\n❌ 請先設置 OPENAI_API_KEY 環境變量")
        return

    # 運行所有示例
    example_basic_ai_function()
    example_translation()
    example_sentiment()
    example_structured_output()
    example_with_parameters()
    example_list_output()
    example_error_handling()

    print("\n" + "="*50)
    print("✅ 所有示例運行完成！")
    print("="*50)
    print("\n下一步: 查看 02_AI函數.py 了解更多 AI 函數的用法")


if __name__ == "__main__":
    main()
