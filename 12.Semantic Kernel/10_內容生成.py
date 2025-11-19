#!/usr/bin/env python3
"""
Semantic Kernel - 內容生成示例

本示例展示：
1. 文章生成
2. 代碼生成
3. 創意寫作
4. 數據格式轉換
5. 模板填充
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

try:
    import semantic_kernel as sk
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
    from semantic_kernel.contents import ChatHistory
except ImportError:
    print("❌ 請安裝 Semantic Kernel:")
    print("   pip install semantic-kernel")
    exit(1)


async def example_article_generation():
    """示例 1: 文章生成"""
    print("\n" + "=" * 60)
    print("示例 1: 文章生成")
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

    prompt_template = """
    撰寫一篇關於 {{$topic}} 的文章。

    要求：
    - 字數約 {{$word_count}} 字
    - 風格：{{$style}}
    - 包含引言、正文、結論

    文章：
    """

    article_function = kernel.add_function(
        function_name="generate_article",
        plugin_name="ContentGen",
        prompt=prompt_template,
        description="生成文章",
    )

    topics = [
        {"topic": "人工智能的未來", "word_count": "300", "style": "專業"},
        {"topic": "可持續發展", "word_count": "200", "style": "通俗易懂"},
    ]

    for t in topics:
        print(f"\n📝 主題: {t['topic']}")
        print(f"📏 字數: {t['word_count']}")
        print(f"🎨 風格: {t['style']}\n")

        result = await kernel.invoke(
            article_function,
            topic=t["topic"],
            word_count=t["word_count"],
            style=t["style"],
        )

        print(f"📄 文章:\n{result}\n")
        print("-" * 60)


async def example_code_generation():
    """示例 2: 代碼生成"""
    print("\n" + "=" * 60)
    print("示例 2: 代碼生成")
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

    prompt_template = """
    用 {{$language}} 語言編寫一個函數來實現：{{$description}}

    要求：
    - 包含完整的函數定義
    - 添加必要的注釋
    - 包含示例用法

    代碼：
    """

    code_function = kernel.add_function(
        function_name="generate_code",
        plugin_name="CodeGen",
        prompt=prompt_template,
        description="生成代碼",
    )

    tasks = [
        {"language": "Python", "description": "二分搜索算法"},
        {"language": "JavaScript", "description": "防抖函數"},
        {"language": "Python", "description": "計算斐波那契數列"},
    ]

    for task in tasks:
        print(f"\n💻 語言: {task['language']}")
        print(f"📋 任務: {task['description']}\n")

        result = await kernel.invoke(
            code_function,
            language=task["language"],
            description=task["description"],
        )

        print(f"```{task['language'].lower()}\n{result}\n```\n")
        print("-" * 60)


async def example_creative_writing():
    """示例 3: 創意寫作"""
    print("\n" + "=" * 60)
    print("示例 3: 創意寫作")
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

    # 詩歌生成
    poem_prompt = """
    創作一首關於 {{$theme}} 的{{$style}}詩。

    詩歌：
    """

    poem_function = kernel.add_function(
        function_name="generate_poem",
        plugin_name="Creative",
        prompt=poem_prompt,
        description="生成詩歌",
    )

    print("📜 詩歌創作:\n")

    poem_themes = [
        {"theme": "秋天", "style": "現代"},
        {"theme": "月光", "style": "古典"},
    ]

    for theme in poem_themes:
        print(f"🎭 主題: {theme['theme']}, 風格: {theme['style']}\n")

        result = await kernel.invoke(
            poem_function,
            theme=theme["theme"],
            style=theme["style"],
        )

        print(f"{result}\n")
        print("-" * 60)

    # 故事生成
    story_prompt = """
    寫一個關於 {{$character}} 的短故事，故事發生在 {{$setting}}。

    故事應該：
    - 有引人入勝的開頭
    - 包含衝突和轉折
    - 有圓滿的結局
    - 字數約 200 字

    故事：
    """

    story_function = kernel.add_function(
        function_name="generate_story",
        plugin_name="Creative",
        prompt=story_prompt,
        description="生成故事",
    )

    print("\n📖 故事創作:\n")

    story_ideas = [
        {"character": "勇敢的機器人", "setting": "未來城市"},
        {"character": "迷失的小貓", "setting": "魔法森林"},
    ]

    for idea in story_ideas:
        print(f"👤 角色: {idea['character']}")
        print(f"🌍 場景: {idea['setting']}\n")

        result = await kernel.invoke(
            story_function,
            character=idea["character"],
            setting=idea["setting"],
        )

        print(f"{result}\n")
        print("-" * 60)


async def example_data_format_conversion():
    """示例 4: 數據格式轉換"""
    print("\n" + "=" * 60)
    print("示例 4: 數據格式轉換")
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

    # CSV to JSON
    csv_to_json_prompt = """
    將以下 CSV 數據轉換為 JSON 格式：

    {{$csv_data}}

    JSON 格式：
    """

    csv_to_json_function = kernel.add_function(
        function_name="csv_to_json",
        plugin_name="DataConversion",
        prompt=csv_to_json_prompt,
        description="CSV 轉 JSON",
    )

    csv_data = """Name,Age,City
John,25,New York
Mary,30,Los Angeles
Peter,28,Chicago"""

    print("📊 CSV 數據:")
    print(csv_data)
    print("\n🔄 轉換為 JSON...\n")

    result = await kernel.invoke(csv_to_json_function, csv_data=csv_data)
    print(f"📄 JSON 結果:\n{result}")


async def example_template_filling():
    """示例 5: 模板填充"""
    print("\n" + "=" * 60)
    print("示例 5: 模板填充")
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

    # 郵件模板
    email_prompt = """
    生成一封{{$type}}郵件：

    收件人：{{$recipient}}
    主題：{{$subject}}
    關鍵內容：{{$content}}

    請生成一封專業、禮貌的郵件。

    郵件：
    """

    email_function = kernel.add_function(
        function_name="generate_email",
        plugin_name="Template",
        prompt=email_prompt,
        description="生成郵件",
    )

    emails = [
        {
            "type": "商務",
            "recipient": "張經理",
            "subject": "項目進度更新",
            "content": "報告本週完成的任務和下週計劃",
        },
        {
            "type": "感謝",
            "recipient": "李教授",
            "subject": "感謝您的指導",
            "content": "感謝在項目期間提供的寶貴建議",
        },
    ]

    for email in emails:
        print(f"\n📧 郵件類型: {email['type']}")
        print(f"📬 收件人: {email['recipient']}")
        print(f"📌 主題: {email['subject']}\n")

        result = await kernel.invoke(
            email_function,
            type=email["type"],
            recipient=email["recipient"],
            subject=email["subject"],
            content=email["content"],
        )

        print(f"{result}\n")
        print("-" * 60)


async def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🚀 Semantic Kernel - 內容生成示例")
    print("=" * 60)

    try:
        await example_article_generation()
        await example_code_generation()
        await example_creative_writing()
        await example_data_format_conversion()
        await example_template_filling()

    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ 所有示例運行完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
