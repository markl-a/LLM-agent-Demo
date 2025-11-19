#!/usr/bin/env python3
"""
Semantic Kernel - 郵件自動化示例

本示例展示：
1. 郵件生成
2. 郵件分類
3. 自動回復
4. 郵件摘要
5. 郵件翻譯
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


async def example_email_generation():
    """示例 1: 郵件生成"""
    print("\n" + "=" * 60)
    print("示例 1: 郵件生成")
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

    email_prompt = """
    生成一封{{$type}}郵件：

    收件人：{{$recipient}}
    主題：{{$subject}}
    關鍵點：{{$key_points}}
    語氣：{{$tone}}

    郵件內容：
    """

    email_function = kernel.add_function(
        function_name="generate_email",
        plugin_name="EmailAutomation",
        prompt=email_prompt,
        description="生成郵件",
    )

    # 郵件生成任務
    email_tasks = [
        {
            "type": "商務",
            "recipient": "張總經理",
            "subject": "第三季度業績報告",
            "key_points": "營收增長15%，成本控制良好，市場份額提升",
            "tone": "正式、專業",
        },
        {
            "type": "感謝信",
            "recipient": "李教授",
            "subject": "感謝您的指導",
            "key_points": "項目成功完成，您的建議非常寶貴",
            "tone": "真誠、感激",
        },
        {
            "type": "邀請",
            "recipient": "團隊成員",
            "subject": "團隊建設活動邀請",
            "key_points": "時間：下週六，地點：陽明山，活動：登山郊遊",
            "tone": "友善、熱情",
        },
    ]

    for task in email_tasks:
        print(f"\n📧 郵件類型: {task['type']}")
        print(f"📬 收件人: {task['recipient']}")
        print(f"📌 主題: {task['subject']}\n")

        result = await kernel.invoke(
            email_function,
            type=task["type"],
            recipient=task["recipient"],
            subject=task["subject"],
            key_points=task["key_points"],
            tone=task["tone"],
        )

        print(f"📄 郵件內容:\n{result}\n")
        print("-" * 60)


async def example_email_classification():
    """示例 2: 郵件分類"""
    print("\n" + "=" * 60)
    print("示例 2: 郵件分類")
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

    classify_prompt = """
    將以下郵件分類到適當的類別：

    類別：緊急、重要、一般、垃圾郵件、促銷

    郵件：
    主題：{{$subject}}
    內容：{{$body}}

    返回 JSON 格式：
    {
        "category": "類別",
        "priority": "high/medium/low",
        "action_required": true/false,
        "reason": "分類理由"
    }

    分類：
    """

    classify_function = kernel.add_function(
        function_name="classify_email",
        plugin_name="EmailManagement",
        prompt=classify_prompt,
        description="郵件分類",
    )

    # 測試郵件
    emails = [
        {
            "subject": "系統故障 - 需要立即處理",
            "body": "生產環境數據庫無法連接，請立即檢查！",
        },
        {
            "subject": "下週會議議程確認",
            "body": "請確認下週三的項目會議議程是否正確。",
        },
        {
            "subject": "限時優惠！8折促銷",
            "body": "本週末所有商品8折優惠，不要錯過！",
        },
    ]

    for email in emails:
        print(f"\n📧 主題: {email['subject']}")
        print(f"📄 內容: {email['body']}\n")

        result = await kernel.invoke(
            classify_function,
            subject=email["subject"],
            body=email["body"],
        )

        print(f"🏷️  分類結果:\n{result}\n")
        print("-" * 60)


async def example_auto_reply():
    """示例 3: 自動回復"""
    print("\n" + "=" * 60)
    print("示例 3: 自動回復")
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

    auto_reply_prompt = """
    為以下郵件生成自動回復：

    收到的郵件：
    {{$email}}

    回復策略：{{$strategy}}

    生成一封合適的回復郵件：
    """

    auto_reply_function = kernel.add_function(
        function_name="auto_reply",
        plugin_name="EmailBot",
        prompt=auto_reply_prompt,
        description="自動回復",
    )

    # 收到的郵件和回復策略
    scenarios = [
        {
            "email": "你好，我想詢問貴公司的產品價格和功能。",
            "strategy": "提供產品信息連結，邀請預約演示",
        },
        {
            "email": "我的訂單 #12345 什麼時候能送達？",
            "strategy": "告知查詢訂單狀態的方法，提供客服聯繫方式",
        },
        {
            "email": "我對你們的服務很滿意，特此致謝！",
            "strategy": "表達感謝，鼓勵留下評價或推薦",
        },
    ]

    for scenario in scenarios:
        print(f"\n📧 收到的郵件: {scenario['email']}")
        print(f"📋 策略: {scenario['strategy']}\n")

        result = await kernel.invoke(
            auto_reply_function,
            email=scenario["email"],
            strategy=scenario["strategy"],
        )

        print(f"✉️  自動回復:\n{result}\n")
        print("-" * 60)


async def example_email_summary():
    """示例 4: 郵件摘要"""
    print("\n" + "=" * 60)
    print("示例 4: 郵件摘要")
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

    summary_prompt = """
    為以下郵件串生成摘要：

    {{$email_thread}}

    摘要應包括：
    - 主要討論點
    - 關鍵決定
    - 待辦事項
    - 截止日期（如有）

    摘要：
    """

    summary_function = kernel.add_function(
        function_name="summarize_thread",
        plugin_name="EmailDigest",
        prompt=summary_prompt,
        description="郵件摘要",
    )

    # 郵件串
    email_thread = """
    [1] 張三 -> 團隊: 我們需要討論新產品發布的時間表。建議在下季度初發布。

    [2] 李四 -> 張三: 同意，但我們需要先完成測試。預計需要2週時間。

    [3] 王五 -> 全部: 市場部門已準備好推廣材料，可以配合技術部門的時間表。

    [4] 張三 -> 全部: 好的，那麼確定在3月15日發布。李四負責測試，王五負責市場推廣。
    請大家在2月底前完成各自的準備工作。
    """

    print("📧 郵件串:")
    print(email_thread)
    print("\n🔍 生成摘要...\n")

    result = await kernel.invoke(summary_function, email_thread=email_thread)

    print(f"📝 摘要:\n{result}")


async def example_email_translation():
    """示例 5: 郵件翻譯"""
    print("\n" + "=" * 60)
    print("示例 5: 郵件翻譯")
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

    translate_prompt = """
    將以下郵件翻譯成{{$target_language}}，保持專業語氣和格式：

    {{$email}}

    翻譯：
    """

    translate_function = kernel.add_function(
        function_name="translate_email",
        plugin_name="EmailTranslation",
        prompt=translate_prompt,
        description="郵件翻譯",
    )

    # 測試郵件
    emails = [
        {
            "email": """親愛的客戶：

感謝您購買我們的產品。您的訂單已經發貨，預計3-5個工作日送達。

如有任何問題，請隨時聯繫我們。

祝好，
ABC公司""",
            "target_language": "英文",
        },
        {
            "email": """Dear Team,

The quarterly review meeting is scheduled for next Friday at 2 PM. Please prepare your department reports.

Best regards,
John""",
            "target_language": "繁體中文",
        },
    ]

    for item in emails:
        print(f"\n📧 原始郵件:")
        print(item["email"])
        print(f"\n🌍 目標語言: {item['target_language']}\n")

        result = await kernel.invoke(
            translate_function,
            email=item["email"],
            target_language=item["target_language"],
        )

        print(f"✅ 翻譯結果:\n{result}\n")
        print("-" * 60)


async def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🚀 Semantic Kernel - 郵件自動化示例")
    print("=" * 60)

    try:
        await example_email_generation()
        await example_email_classification()
        await example_auto_reply()
        await example_email_summary()
        await example_email_translation()

    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ 所有示例運行完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
