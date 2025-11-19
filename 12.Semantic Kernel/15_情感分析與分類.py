#!/usr/bin/env python3
"""
Semantic Kernel - 情感分析與文本分類示例

本示例展示：
1. 情感分析
2. 主題分類
3. 垃圾郵件檢測
4. 內容審核
5. 實體識別
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

try:
    import semantic_kernel as sk
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
except ImportError:
    print("❌ 請安裝 Semantic Kernel:")
    print("   pip install semantic-kernel")
    exit(1)


async def example_sentiment_analysis():
    """示例 1: 情感分析"""
    print("\n" + "=" * 60)
    print("示例 1: 情感分析")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    sentiment_prompt = """
    分析以下文本的情感，並以 JSON 格式返回：

    文本：{{$text}}

    返回格式：
    {
        "sentiment": "positive/negative/neutral",
        "confidence": 0.0-1.0,
        "emotions": ["主要情緒"],
        "explanation": "簡短解釋"
    }

    分析：
    """

    sentiment_function = kernel.add_function(
        function_name="analyze_sentiment",
        plugin_name="Sentiment",
        prompt=sentiment_prompt,
        description="分析情感",
    )

    # 測試文本
    test_texts = [
        "這個產品太棒了！完全超出我的期待，強烈推薦！",
        "質量很差，浪費了我的錢，非常失望。",
        "產品還可以，符合基本需求。",
        "雖然價格有點貴，但是質量確實不錯，值得購買。",
        "客服態度惡劣，等了一個小時才有回應！",
    ]

    for text in test_texts:
        print(f"\n📝 文本: {text}")

        result = await kernel.invoke(sentiment_function, text=text)

        print(f"📊 情感分析:\n{result}\n")
        print("-" * 60)


async def example_topic_classification():
    """示例 2: 主題分類"""
    print("\n" + "=" * 60)
    print("示例 2: 主題分類")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    classification_prompt = """
    將以下文本分類到適當的類別：

    類別：科技、體育、娛樂、財經、健康、教育、政治、其他

    文本：{{$text}}

    只返回類別名稱：
    """

    classify_function = kernel.add_function(
        function_name="classify_topic",
        plugin_name="Classification",
        prompt=classification_prompt,
        description="主題分類",
    )

    # 測試新聞
    news_items = [
        "蘋果公司發布了最新的 iPhone 15，搭載 A17 芯片",
        "台灣籃球隊在亞錦賽中獲得銀牌",
        "最新研究顯示，地中海飲食有助於心臟健康",
        "央行宣布降息 0.25 個百分點",
        "新電影《星際探索》票房突破 10 億",
        "教育部推出新的課綱改革方案",
    ]

    for news in news_items:
        print(f"\n📰 新聞: {news}")

        category = await kernel.invoke(classify_function, text=news)

        print(f"🏷️  分類: {category}")


async def example_spam_detection():
    """示例 3: 垃圾郵件檢測"""
    print("\n" + "=" * 60)
    print("示例 3: 垃圾郵件檢測")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    spam_prompt = """
    判斷以下郵件是否為垃圾郵件，並返回 JSON：

    郵件：{{$email}}

    返回格式：
    {
        "is_spam": true/false,
        "confidence": 0.0-1.0,
        "reasons": ["判斷理由"],
        "category": "垃圾郵件類型（如果是垃圾郵件）"
    }

    判斷：
    """

    spam_function = kernel.add_function(
        function_name="detect_spam",
        plugin_name="SpamDetection",
        prompt=spam_prompt,
        description="檢測垃圾郵件",
    )

    # 測試郵件
    emails = [
        "親愛的客戶，您的訂單已發貨，預計明天送達。",
        "恭喜！您中獎了！點擊此鏈接領取 100 萬獎金！",
        "會議時間更改為明天下午 3 點，請準時參加。",
        "限時優惠！買一送一！立即購買！",
        "您的銀行賬戶異常，請點擊鏈接驗證身份。",
    ]

    for email in emails:
        print(f"\n📧 郵件: {email}")

        result = await kernel.invoke(spam_function, email=email)

        print(f"🔍 檢測結果:\n{result}\n")
        print("-" * 60)


async def example_content_moderation():
    """示例 4: 內容審核"""
    print("\n" + "=" * 60)
    print("示例 4: 內容審核")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    moderation_prompt = """
    審核以下內容，判斷是否違反社區規範：

    內容：{{$content}}

    檢查項目：
    - 暴力或威脅
    - 仇恨言論
    - 性相關內容
    - 騷擾或霸凌
    - 虛假信息

    返回 JSON 格式：
    {
        "approved": true/false,
        "violations": ["違規類型"],
        "severity": "low/medium/high",
        "action": "建議的處理措施"
    }

    審核結果：
    """

    moderate_function = kernel.add_function(
        function_name="moderate_content",
        plugin_name="Moderation",
        prompt=moderation_prompt,
        description="內容審核",
    )

    # 測試內容
    contents = [
        "這是一個很棒的產品分享，推薦給大家！",
        "我認為這個政策需要改進，建議增加透明度。",
        "今天天氣真好，適合出去散步。",
    ]

    for content in contents:
        print(f"\n📝 內容: {content}")

        result = await kernel.invoke(moderate_function, content=content)

        print(f"✅ 審核結果:\n{result}\n")
        print("-" * 60)


async def example_entity_recognition():
    """示例 5: 實體識別"""
    print("\n" + "=" * 60)
    print("示例 5: 實體識別（NER）")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    ner_prompt = """
    從以下文本中識別並提取實體：

    文本：{{$text}}

    提取以下類型的實體：
    - 人名（PERSON）
    - 組織（ORGANIZATION）
    - 地點（LOCATION）
    - 日期（DATE）
    - 金額（MONEY）

    返回 JSON 格式：
    {
        "entities": [
            {"text": "實體文本", "type": "類型", "context": "上下文"}
        ]
    }

    識別結果：
    """

    ner_function = kernel.add_function(
        function_name="recognize_entities",
        plugin_name="NER",
        prompt=ner_prompt,
        description="實體識別",
    )

    # 測試文本
    texts = [
        "蘋果公司的執行長 Tim Cook 於 2023 年 9 月在加州庫比蒂諾發布了 iPhone 15。",
        "台積電計劃在台南投資 1000 億美元建設新廠。",
        "張三於昨天在台北 101 購物中心花費了 5000 元。",
    ]

    for text in texts:
        print(f"\n📄 文本: {text}")

        result = await kernel.invoke(ner_function, text=text)

        print(f"🔍 識別實體:\n{result}\n")
        print("-" * 60)


async def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🚀 Semantic Kernel - 情感分析與分類示例")
    print("=" * 60)

    try:
        await example_sentiment_analysis()
        await example_topic_classification()
        await example_spam_detection()
        await example_content_moderation()
        await example_entity_recognition()

    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ 所有示例運行完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
