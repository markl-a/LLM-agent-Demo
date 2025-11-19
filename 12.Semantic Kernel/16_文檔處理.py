#!/usr/bin/env python3
"""
Semantic Kernel - 文檔處理示例

本示例展示：
1. 文檔摘要
2. 文檔問答
3. 文檔比較
4. 文檔生成
5. 格式轉換
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


async def example_document_summarization():
    """示例 1: 文檔摘要"""
    print("\n" + "=" * 60)
    print("示例 1: 文檔摘要")
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
    為以下文檔生成{{$length}}摘要：

    {{$document}}

    摘要要求：
    - 保留關鍵信息
    - 結構清晰
    - 易於理解

    摘要：
    """

    summary_function = kernel.add_function(
        function_name="summarize_document",
        plugin_name="DocProcessing",
        prompt=summary_prompt,
        description="文檔摘要",
    )

    # 示例文檔
    document = """
    人工智能（AI）技術正在快速發展，並在多個領域產生深遠影響。在醫療領域，AI 幫助醫生更準確地
    診斷疾病，通過分析大量醫學影像數據來識別早期癌症等疾病跡象。在金融領域，AI 用於風險評估、
    欺詐檢測和自動化交易。教育領域中，AI 提供個性化學習體驗，根據學生的學習節奏和風格調整教學
    內容。此外，AI 在製造業中提高了生產效率，通過預測性維護減少停機時間，並優化供應鏈管理。
    然而，AI 的發展也帶來了挑戰，包括就業市場的變化、隱私問題和倫理考量。未來，AI 技術的發展
    需要在創新和責任之間找到平衡，確保技術進步能夠惠及全人類。
    """

    lengths = ["一句話", "3句話", "一段話"]

    for length in lengths:
        print(f"\n📊 摘要長度: {length}")

        result = await kernel.invoke(
            summary_function,
            document=document,
            length=length,
        )

        print(f"📝 摘要:\n{result}\n")
        print("-" * 60)


async def example_document_qa():
    """示例 2: 文檔問答"""
    print("\n" + "=" * 60)
    print("示例 2: 文檔問答")
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

    qa_prompt = """
    基於以下文檔回答問題：

    文檔：
    {{$document}}

    問題：{{$question}}

    要求：
    - 只基於文檔內容回答
    - 如果文檔中沒有相關信息，明確說明
    - 引用文檔中的具體內容

    回答：
    """

    qa_function = kernel.add_function(
        function_name="answer_from_document",
        plugin_name="DocQA",
        prompt=qa_prompt,
        description="文檔問答",
    )

    # 文檔內容
    company_doc = """
    ABC 科技公司成立於 2010 年，總部位於台北。公司專注於 AI 和大數據解決方案。
    目前員工人數超過 500 人，在台灣、日本和新加坡設有辦公室。

    主要產品：
    1. SmartAnalytics - 企業數據分析平台
    2. AIAssist - 智能客服系統
    3. CloudSync - 雲端協作工具

    公司文化：
    - 創新為本
    - 客戶至上
    - 團隊協作
    - 持續學習

    福利待遇：
    - 彈性工作時間
    - 遠程工作選項
    - 年度健康檢查
    - 教育訓練補助
    """

    # 問題列表
    questions = [
        "公司什麼時候成立的？",
        "公司有哪些主要產品？",
        "公司的辦公室在哪裡？",
        "員工福利有哪些？",
        "公司的營收是多少？",  # 文檔中沒有的信息
    ]

    for question in questions:
        print(f"\n❓ 問題: {question}")

        result = await kernel.invoke(
            qa_function,
            document=company_doc,
            question=question,
        )

        print(f"💡 回答: {result}\n")
        print("-" * 60)


async def example_document_comparison():
    """示例 3: 文檔比較"""
    print("\n" + "=" * 60)
    print("示例 3: 文檔比較")
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

    compare_prompt = """
    比較以下兩個文檔，指出：

    文檔 A：
    {{$doc_a}}

    文檔 B：
    {{$doc_b}}

    請提供：
    1. 相同點
    2. 不同點
    3. 各自的特點
    4. 建議

    比較結果：
    """

    compare_function = kernel.add_function(
        function_name="compare_documents",
        plugin_name="DocAnalysis",
        prompt=compare_prompt,
        description="文檔比較",
    )

    # 兩個產品描述
    product_a = """
    產品 A 是一款智能手機，配備 6.1 英寸 OLED 螢幕，128GB 存儲空間，
    5000mAh 電池，支持 5G 網絡，售價 $699。
    """

    product_b = """
    產品 B 是一款智能手機，配備 6.5 英寸 AMOLED 螢幕，256GB 存儲空間，
    4500mAh 電池，支持 5G 網絡，售價 $799。
    """

    print("📄 文檔 A:")
    print(product_a)
    print("\n📄 文檔 B:")
    print(product_b)

    result = await kernel.invoke(
        compare_function,
        doc_a=product_a,
        doc_b=product_b,
    )

    print(f"\n📊 比較結果:\n{result}")


async def example_document_generation():
    """示例 4: 文檔生成"""
    print("\n" + "=" * 60)
    print("示例 4: 文檔生成")
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

    generate_prompt = """
    生成一份{{$doc_type}}文檔：

    主題：{{$topic}}
    要點：{{$points}}

    要求：
    - 格式專業
    - 內容完整
    - 結構清晰

    文檔：
    """

    generate_function = kernel.add_function(
        function_name="generate_document",
        plugin_name="DocGeneration",
        prompt=generate_prompt,
        description="生成文檔",
    )

    # 文檔生成任務
    tasks = [
        {
            "doc_type": "會議記錄",
            "topic": "產品發布計劃",
            "points": "時間、責任人、預算、市場策略",
        },
        {
            "doc_type": "項目提案",
            "topic": "AI 聊天機器人開發",
            "points": "背景、目標、技術方案、預算、時間表",
        },
    ]

    for task in tasks:
        print(f"\n📝 文檔類型: {task['doc_type']}")
        print(f"📋 主題: {task['topic']}")

        result = await kernel.invoke(
            generate_function,
            doc_type=task["doc_type"],
            topic=task["topic"],
            points=task["points"],
        )

        print(f"\n📄 生成的文檔:\n{result}\n")
        print("-" * 60)


async def example_format_conversion():
    """示例 5: 格式轉換"""
    print("\n" + "=" * 60)
    print("示例 5: 格式轉換")
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

    convert_prompt = """
    將以下內容從{{$from_format}}格式轉換為{{$to_format}}格式：

    {{$content}}

    轉換後的內容：
    """

    convert_function = kernel.add_function(
        function_name="convert_format",
        plugin_name="FormatConversion",
        prompt=convert_prompt,
        description="格式轉換",
    )

    # 轉換任務
    conversions = [
        {
            "from_format": "段落文本",
            "to_format": "要點列表",
            "content": "我們的產品具有三個主要優勢。首先是高性能，其次是易用性，最後是價格實惠。",
        },
        {
            "from_format": "列表",
            "to_format": "表格",
            "content": "產品A: $100, 產品B: $150, 產品C: $200",
        },
    ]

    for conv in conversions:
        print(f"\n🔄 轉換: {conv['from_format']} → {conv['to_format']}")
        print(f"📝 原始內容:\n{conv['content']}")

        result = await kernel.invoke(
            convert_function,
            from_format=conv["from_format"],
            to_format=conv["to_format"],
            content=conv["content"],
        )

        print(f"\n✅ 轉換結果:\n{result}\n")
        print("-" * 60)


async def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🚀 Semantic Kernel - 文檔處理示例")
    print("=" * 60)

    try:
        await example_document_summarization()
        await example_document_qa()
        await example_document_comparison()
        await example_document_generation()
        await example_format_conversion()

    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ 所有示例運行完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
