#!/usr/bin/env python3
"""
Semantic Kernel - 提示詞工程示例

本示例展示：
1. 提示詞模板
2. 變量插值
3. Few-shot 學習
4. 提示詞鏈
5. 條件提示詞
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

try:
    import semantic_kernel as sk
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
    from semantic_kernel.prompt_template import PromptTemplateConfig
    from semantic_kernel.functions import KernelArguments
except ImportError:
    print("❌ 請安裝 Semantic Kernel:")
    print("   pip install semantic-kernel")
    exit(1)


async def example_basic_template():
    """示例 1: 基本提示詞模板"""
    print("\n" + "=" * 60)
    print("示例 1: 基本提示詞模板")
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

    # 創建提示詞模板
    prompt_template = """
    你是一個專業的{{$role}}。請用{{$style}}的方式回答以下問題：

    問題：{{$question}}

    回答：
    """

    # 創建函數
    summarize_function = kernel.add_function(
        function_name="answer_as_role",
        plugin_name="PromptEngineering",
        prompt=prompt_template,
        description="以特定角色和風格回答問題",
    )

    # 測試不同的角色和風格
    test_cases = [
        {
            "role": "科學家",
            "style": "專業嚴謹",
            "question": "什麼是光合作用？",
        },
        {
            "role": "小學老師",
            "style": "簡單易懂",
            "question": "什麼是光合作用？",
        },
        {
            "role": "詩人",
            "style": "優美抒情",
            "question": "什麼是光合作用？",
        },
    ]

    for case in test_cases:
        print(f"\n📝 角色: {case['role']}, 風格: {case['style']}")
        print(f"💬 問題: {case['question']}")

        result = await kernel.invoke(
            summarize_function,
            role=case["role"],
            style=case["style"],
            question=case["question"],
        )

        print(f"🤖 回答: {result}")


async def example_few_shot_learning():
    """示例 2: Few-shot 學習"""
    print("\n" + "=" * 60)
    print("示例 2: Few-shot 學習")
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

    # Few-shot 情感分析提示詞
    prompt_template = """
    請分析以下文本的情感（正面、負面、中性）。

    範例 1:
    文本: "這個產品真是太棒了！"
    情感: 正面

    範例 2:
    文本: "服務態度很差，非常失望。"
    情感: 負面

    範例 3:
    文本: "今天天氣還可以。"
    情感: 中性

    現在分析：
    文本: "{{$text}}"
    情感:
    """

    sentiment_function = kernel.add_function(
        function_name="analyze_sentiment",
        plugin_name="NLP",
        prompt=prompt_template,
        description="分析文本情感",
    )

    test_texts = [
        "這家餐廳的食物美味極了，服務也很好！",
        "等了一個小時才上菜，真是浪費時間。",
        "產品質量一般，價格也一般。",
        "驚喜連連，超出預期！",
    ]

    for text in test_texts:
        print(f"\n📝 文本: {text}")

        result = await kernel.invoke(sentiment_function, text=text)

        print(f"😊 情感: {result}")


async def example_prompt_chaining():
    """示例 3: 提示詞鏈"""
    print("\n" + "=" * 60)
    print("示例 3: 提示詞鏈")
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

    # 步驟 1: 生成創意
    generate_idea = kernel.add_function(
        function_name="generate_idea",
        plugin_name="Creative",
        prompt="生成一個關於 {{$topic}} 的創意想法（一句話）：",
        description="生成創意想法",
    )

    # 步驟 2: 擴展想法
    expand_idea = kernel.add_function(
        function_name="expand_idea",
        plugin_name="Creative",
        prompt="將以下想法擴展成一段話（50字左右）：\n\n{{$idea}}",
        description="擴展想法",
    )

    # 步驟 3: 總結要點
    summarize_points = kernel.add_function(
        function_name="summarize_points",
        plugin_name="Creative",
        prompt="從以下文本中提取 3 個關鍵要點：\n\n{{$text}}",
        description="提取要點",
    )

    topic = "未來的教育"
    print(f"📝 主題: {topic}")

    # 執行鏈式調用
    print("\n🔗 步驟 1: 生成創意...")
    idea = await kernel.invoke(generate_idea, topic=topic)
    print(f"💡 創意: {idea}")

    print("\n🔗 步驟 2: 擴展想法...")
    expanded = await kernel.invoke(expand_idea, idea=str(idea))
    print(f"📝 擴展: {expanded}")

    print("\n🔗 步驟 3: 總結要點...")
    points = await kernel.invoke(summarize_points, text=str(expanded))
    print(f"📋 要點:\n{points}")


async def example_conditional_prompts():
    """示例 4: 條件提示詞"""
    print("\n" + "=" * 60)
    print("示例 4: 條件提示詞")
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

    # 根據用戶級別調整回答詳細程度
    prompt_template = """
    {{#if (eq $level "beginner")}}
    請用非常簡單的語言，像對小學生一樣解釋：
    {{else if (eq $level "intermediate")}}
    請用清晰但技術性的語言解釋：
    {{else}}
    請用專業術語和深入的技術細節解釋：
    {{/if}}

    問題：{{$question}}
    """

    # 注意：Semantic Kernel 的模板不直接支持 if/else
    # 我們使用 Python 來實現條件邏輯

    async def answer_by_level(level: str, question: str):
        """根據級別回答問題"""
        if level == "beginner":
            prompt = f"請用非常簡單的語言，像對小學生一樣解釋：\n\n問題：{question}"
        elif level == "intermediate":
            prompt = f"請用清晰但技術性的語言解釋：\n\n問題：{question}"
        else:
            prompt = f"請用專業術語和深入的技術細節解釋：\n\n問題：{question}"

        func = kernel.add_function(
            function_name=f"answer_{level}",
            plugin_name="Conditional",
            prompt=prompt,
            description=f"以 {level} 級別回答",
        )

        result = await kernel.invoke(func)
        return result

    question = "什麼是神經網絡？"
    levels = ["beginner", "intermediate", "advanced"]

    for level in levels:
        print(f"\n📚 級別: {level}")
        print(f"💬 問題: {question}")

        answer = await answer_by_level(level, question)
        print(f"🤖 回答: {answer}\n")


async def example_output_formatting():
    """示例 5: 輸出格式化"""
    print("\n" + "=" * 60)
    print("示例 5: 輸出格式化")
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

    # JSON 格式輸出
    json_prompt = """
    分析以下產品評論，並以 JSON 格式輸出結果：

    評論：{{$review}}

    請輸出格式：
    {
        "sentiment": "正面/負面/中性",
        "rating": 1-5,
        "key_points": ["要點1", "要點2"],
        "recommendation": "推薦/不推薦"
    }
    """

    analyze_review = kernel.add_function(
        function_name="analyze_review_json",
        plugin_name="Format",
        prompt=json_prompt,
        description="分析評論並返回 JSON",
    )

    review = "這個產品質量不錯，但是價格有點貴。客服態度很好，物流也很快。"
    print(f"📝 評論: {review}\n")

    result = await kernel.invoke(analyze_review, review=review)
    print(f"📊 分析結果（JSON）:\n{result}")

    # Markdown 格式輸出
    print("\n" + "-" * 60)

    md_prompt = """
    將以下信息整理成 Markdown 格式的會議記錄：

    {{$notes}}

    請包含：標題、日期、參與者、討論要點、行動項目
    """

    format_meeting = kernel.add_function(
        function_name="format_meeting_md",
        plugin_name="Format",
        prompt=md_prompt,
        description="格式化會議記錄",
    )

    notes = "討論了新產品的發布計劃，決定在下月15號上線。張三負責技術準備，李四負責市場推廣。"
    print(f"📝 會議筆記: {notes}\n")

    md_result = await kernel.invoke(format_meeting, notes=notes)
    print(f"📋 會議記錄（Markdown）:\n{md_result}")


async def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🚀 Semantic Kernel - 提示詞工程示例")
    print("=" * 60)

    try:
        await example_basic_template()
        await example_few_shot_learning()
        await example_prompt_chaining()
        await example_conditional_prompts()
        await example_output_formatting()

    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ 所有示例運行完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
