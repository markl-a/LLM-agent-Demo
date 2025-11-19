#!/usr/bin/env python3
"""
Semantic Kernel - 翻譯與摘要示例

本示例展示：
1. 多語言翻譯
2. 文本摘要
3. 關鍵字提取
4. 文本改寫
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


async def example_translation():
    """示例 1: 多語言翻譯"""
    print("\n" + "=" * 60)
    print("示例 1: 多語言翻譯")
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
    將以下文本從{{$source_lang}}翻譯成{{$target_lang}}：

    {{$text}}

    翻譯：
    """

    translate_function = kernel.add_function(
        function_name="translate",
        plugin_name="Translation",
        prompt=translate_prompt,
        description="翻譯文本",
    )

    # 測試翻譯
    texts = [
        {
            "text": "人工智能正在改變我們的世界",
            "source_lang": "繁體中文",
            "target_lang": "英文",
        },
        {
            "text": "Machine learning is a subset of artificial intelligence",
            "source_lang": "English",
            "target_lang": "日文",
        },
        {
            "text": "La vie est belle",
            "source_lang": "法文",
            "target_lang": "繁體中文",
        },
    ]

    for t in texts:
        print(f"\n原文 ({t['source_lang']}): {t['text']}")

        result = await kernel.invoke(
            translate_function,
            text=t["text"],
            source_lang=t["source_lang"],
            target_lang=t["target_lang"],
        )

        print(f"譯文 ({t['target_lang']}): {result}")


async def example_summarization():
    """示例 2: 文本摘要"""
    print("\n" + "=" * 60)
    print("示例 2: 文本摘要")
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

    summarize_prompt = """
    為以下文本生成{{$length}}摘要：

    {{$text}}

    摘要：
    """

    summarize_function = kernel.add_function(
        function_name="summarize",
        plugin_name="Summarization",
        prompt=summarize_prompt,
        description="生成摘要",
    )

    # 長文本
    long_text = """
    人工智能（Artificial Intelligence, AI）是計算機科學的一個分支，致力於創建能夠執行通常需要人類智能的任務的系統。
    這些任務包括視覺感知、語音識別、決策制定和語言翻譯等。AI 的發展可以追溯到 1950 年代，當時計算機科學家開始探索
    機器是否能夠思考的可能性。近年來，隨著計算能力的提升和大數據的可用性，AI 技術取得了顯著進展。深度學習，一種基於
    人工神經網絡的機器學習方法，已經在圖像識別、自然語言處理和遊戲等領域取得了突破性成果。AI 的應用範圍廣泛，從智能
    助手和推薦系統到自動駕駛汽車和醫療診斷。然而，AI 的發展也帶來了倫理和社會挑戰，包括隱私問題、就業影響和決策透明度。
    """

    # 不同長度的摘要
    lengths = ["一句話", "50字", "100字"]

    for length in lengths:
        print(f"\n📊 摘要長度: {length}")

        result = await kernel.invoke(
            summarize_function,
            text=long_text,
            length=length,
        )

        print(f"📝 摘要: {result}\n")
        print("-" * 60)


async def example_keyword_extraction():
    """示例 3: 關鍵字提取"""
    print("\n" + "=" * 60)
    print("示例 3: 關鍵字提取")
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

    keyword_prompt = """
    從以下文本中提取 {{$count}} 個最重要的關鍵字：

    {{$text}}

    關鍵字（用逗號分隔）：
    """

    keyword_function = kernel.add_function(
        function_name="extract_keywords",
        plugin_name="TextAnalysis",
        prompt=keyword_prompt,
        description="提取關鍵字",
    )

    texts = [
        {
            "text": "深度學習是機器學習的一個子集，使用多層神經網絡來學習數據的複雜模式。它在計算機視覺和自然語言處理領域取得了巨大成功。",
            "count": "5",
        },
        {
            "text": "區塊鏈技術通過分散式賬本和加密技術，為數字交易提供了安全性和透明度。它最著名的應用是加密貨幣，但也在供應鏈管理和智能合約等領域有所應用。",
            "count": "6",
        },
    ]

    for t in texts:
        print(f"\n📄 文本: {t['text']}")

        result = await kernel.invoke(
            keyword_function,
            text=t["text"],
            count=t["count"],
        )

        print(f"🔑 關鍵字: {result}\n")
        print("-" * 60)


async def example_text_rewriting():
    """示例 4: 文本改寫"""
    print("\n" + "=" * 60)
    print("示例 4: 文本改寫")
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

    rewrite_prompt = """
    將以下文本改寫為{{$style}}風格：

    {{$text}}

    改寫後的文本：
    """

    rewrite_function = kernel.add_function(
        function_name="rewrite",
        plugin_name="TextRewriting",
        prompt=rewrite_prompt,
        description="改寫文本",
    )

    original_text = "這個產品很好用，我非常喜歡它的設計和功能。"

    styles = ["正式商務", "口語化", "詩意", "簡潔"]

    print(f"📝 原文: {original_text}\n")

    for style in styles:
        print(f"🎨 風格: {style}")

        result = await kernel.invoke(
            rewrite_function,
            text=original_text,
            style=style,
        )

        print(f"📄 改寫: {result}\n")
        print("-" * 60)


async def example_bullet_points():
    """示例 5: 要點提取"""
    print("\n" + "=" * 60)
    print("示例 5: 要點提取")
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

    bullet_points_prompt = """
    將以下文本轉換為簡潔的要點列表（bullet points）：

    {{$text}}

    要點：
    """

    bullet_function = kernel.add_function(
        function_name="to_bullet_points",
        plugin_name="TextFormatting",
        prompt=bullet_points_prompt,
        description="轉換為要點",
    )

    text = """
    我們的新產品具有多項創新功能。首先，它採用了最新的 AI 技術，可以智能識別用戶需求。
    其次，產品界面經過精心設計，簡潔直觀，易於使用。第三，它支持多平台使用，包括手機、
    平板和電腦。最後，產品提供了強大的數據分析功能，幫助用戶做出更好的決策。
    """

    print(f"📄 原文:\n{text}\n")

    result = await kernel.invoke(bullet_function, text=text)

    print(f"📋 要點:\n{result}")


async def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🚀 Semantic Kernel - 翻譯與摘要示例")
    print("=" * 60)

    try:
        await example_translation()
        await example_summarization()
        await example_keyword_extraction()
        await example_text_rewriting()
        await example_bullet_points()

    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ 所有示例運行完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
