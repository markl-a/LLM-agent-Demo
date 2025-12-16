"""
03_長文本處理.py - 長文檔處理策略

本範例展示處理長文本的各種策略，包括：
- 文檔分割策略 (Chunking Strategies)
- Map-Reduce 模式
- Refine 模式
- 階層式摘要 (Hierarchical Summarization)
- 長上下文窗口處理
- 增量處理 (Incremental Processing)
- 記憶管理與壓縮

適用場景：學術論文分析、法律文件審查、技術文檔處理等

作者：LLM-agent-Demo Team
日期：2025-12
"""

import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    TokenTextSplitter,
    CharacterTextSplitter,
    MarkdownTextSplitter,
    PythonCodeTextSplitter
)
from langchain.chains.summarize import load_summarize_chain
from langchain.chains import (
    MapReduceDocumentsChain,
    ReduceDocumentsChain,
    StuffDocumentsChain
)
from langchain_community.vectorstores import Chroma

import tiktoken

# 載入環境變數
load_dotenv()


# ============================================================================
# 工具函數
# ============================================================================

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """計算文本的 token 數量"""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def generate_long_document() -> str:
    """生成一個長文檔示例"""
    return """
人工智能的發展歷程

第一章：早期探索（1950-1970）

人工智能的概念最早可以追溯到1950年代。1950年，艾倫·圖靈發表了著名的論文《計算機器與智能》，
提出了圖靈測試的概念。這個測試成為衡量機器是否具有智能的重要標準。

1956年，在達特茅斯會議上，約翰·麥卡錫首次提出"人工智能"這個術語。這次會議被認為是人工智能
作為一個學科領域的誕生標誌。參會者包括馬文·明斯基、克勞德·香農等先驅人物。

早期的人工智能研究主要集中在問題求解和符號推理上。研究者們開發了許多早期系統，如Logic Theorist
和General Problem Solver。這些系統展示了計算機在某些特定領域模仿人類推理的能力。

第二章：專家系統時代（1970-1990）

1970年代到1980年代，專家系統成為人工智能研究的主流。專家系統是一種模擬人類專家決策能力的程序，
通過規則庫來表示領域知識。

DENDRAL是最早的成功專家系統之一，用於推斷有機化合物的分子結構。MYCIN系統則在醫療診斷領域
展示了專家系統的潛力，其診斷準確率甚至超過了一些醫學專家。

日本在1982年啟動了第五代計算機計劃，投入大量資源發展人工智能。雖然這個計劃最終未能達到
預期目標，但它推動了並行處理和邏輯程式設計的發展。

第三章：機器學習興起（1990-2010）

1990年代，機器學習開始嶄露頭角。研究重點從規則庫轉向從數據中學習。支持向量機（SVM）、
決策樹、隨機森林等算法得到廣泛應用。

1997年，IBM的深藍計算機擊敗了國際象棋世界冠軍卡斯帕羅夫，這是人工智能發展的重要里程碑。
深藍每秒可以評估2億個棋局，展示了計算能力的巨大進步。

2000年代，隨著互聯網的發展和數據的爆炸式增長，機器學習算法得到了前所未有的數據支持。
Google、Amazon等科技公司開始將機器學習應用於搜索、推薦系統等實際產品中。

第四章：深度學習革命（2010-2020）

2012年，深度學習在ImageNet圖像識別競賽中取得突破性進展。Alex Krizhevsky開發的AlexNet
使用深度卷積神經網絡，大幅降低了錯誤率。這標誌著深度學習時代的開始。

2016年，Google DeepMind的AlphaGo擊敗圍棋世界冠軍李世石，震驚了全世界。圍棋被認為是
最複雜的棋類遊戲之一，AlphaGo的成功展示了深度強化學習的強大能力。

深度學習在計算機視覺、自然語言處理、語音識別等領域都取得了重大突破。卷積神經網絡（CNN）、
循環神經網絡（RNN）、長短期記憶網絡（LSTM）等架構被廣泛應用。

2017年，Google發表了Transformer架構，徹底改變了自然語言處理的範式。Transformer使用
注意力機制，能夠更好地捕捉長距離依賴關係。

第五章：大型語言模型時代（2020至今）

2020年，OpenAI發布了GPT-3，參數量達到1750億。GPT-3展示了驚人的語言理解和生成能力，
能夠完成翻譯、問答、代碼生成等多種任務。

2022年11月，ChatGPT發布，在短短5天內用戶數突破100萬。ChatGPT展示了大型語言模型在
對話系統中的巨大潛力，引發了全球對人工智能的新一輪關注。

2023年，多模態大型模型開始興起。GPT-4、Google Gemini等模型不僅能處理文本，還能處理
圖像、音頻等多種模態的數據。

大型語言模型的發展也帶來了新的挑戰，包括計算資源需求、數據隱私、模型偏見、幻覺問題等。
研究者們正在探索更高效的訓練方法和更可靠的應用方式。

第六章：未來展望

人工智能的未來發展方向包括：

1. 通用人工智能（AGI）：開發能夠在各種任務中達到或超過人類水平的人工智能系統。

2. 可解釋AI：提高AI系統的透明度和可解釋性，讓人類能夠理解AI的決策過程。

3. 節能AI：開發更節能的算法和硬件，降低AI的環境影響。

4. 人機協作：設計能夠與人類有效協作的AI系統，而不是完全替代人類。

5. 安全與倫理：建立完善的AI安全機制和倫理規範，確保AI的發展符合人類利益。

人工智能正在深刻改變我們的生活和工作方式。從醫療診斷到自動駕駛，從教育到娛樂，AI的應用
越來越廣泛。我們需要在推動技術進步的同時，認真思考和應對AI帶來的社會、倫理和法律挑戰。

結語

人工智能的發展是一個漫長而曲折的過程，經歷了多次高潮和低谷。從早期的符號推理到現在的
大型語言模型，每一次重大突破都推動了整個領域的進步。

未來的人工智能將更加智能、更加通用、更加安全。我們有理由相信，在研究者和工程師的共同
努力下，人工智能將為人類社會帶來更多福祉。
"""


# ============================================================================
# 範例 1: 基礎文檔分割策略
# ============================================================================

def example_1_text_splitting_strategies():
    """
    展示不同的文檔分割策略

    策略類型：
    1. RecursiveCharacterTextSplitter - 遞歸字符分割（推薦）
    2. TokenTextSplitter - 基於 token 分割
    3. CharacterTextSplitter - 基於字符分割
    4. MarkdownTextSplitter - Markdown 特定分割
    """
    print("\n" + "="*80)
    print("範例 1: 文檔分割策略比較")
    print("="*80)

    document = generate_long_document()
    print(f"原始文檔長度: {len(document)} 字符")
    print(f"Token 數量: {count_tokens(document)}")

    # 策略 1: RecursiveCharacterTextSplitter
    print("\n--- 策略 1: RecursiveCharacterTextSplitter ---")
    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "，", " ", ""],
        length_function=len
    )
    recursive_chunks = recursive_splitter.split_text(document)
    print(f"分割後的塊數: {len(recursive_chunks)}")
    print(f"第一塊預覽: {recursive_chunks[0][:100]}...")

    # 策略 2: TokenTextSplitter
    print("\n--- 策略 2: TokenTextSplitter ---")
    token_splitter = TokenTextSplitter(
        chunk_size=200,
        chunk_overlap=20
    )
    token_chunks = token_splitter.split_text(document)
    print(f"分割後的塊數: {len(token_chunks)}")
    print(f"第一塊 token 數: {count_tokens(token_chunks[0])}")

    # 策略 3: 基於語義的智能分割
    print("\n--- 策略 3: 基於標題的智能分割 ---")

    def smart_split_by_headers(text: str) -> List[str]:
        """基於章節標題分割文檔"""
        sections = []
        current_section = []

        for line in text.split('\n'):
            if line.startswith('第') and '章' in line:
                if current_section:
                    sections.append('\n'.join(current_section))
                current_section = [line]
            else:
                current_section.append(line)

        if current_section:
            sections.append('\n'.join(current_section))

        return sections

    smart_chunks = smart_split_by_headers(document)
    print(f"章節數量: {len(smart_chunks)}")
    for i, chunk in enumerate(smart_chunks[:3], 1):
        print(f"\n章節 {i} 標題: {chunk.split(chr(10))[0]}")
        print(f"章節 {i} 長度: {len(chunk)} 字符")

    return recursive_chunks


# ============================================================================
# 範例 2: Map-Reduce 摘要模式
# ============================================================================

def example_2_map_reduce_summarization():
    """
    展示 Map-Reduce 模式處理長文檔

    流程：
    1. Map: 對每個文檔塊生成摘要
    2. Reduce: 將所有摘要合併成最終摘要

    優點：可以處理任意長度的文檔
    """
    print("\n" + "="*80)
    print("範例 2: Map-Reduce 摘要模式")
    print("="*80)

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    # 準備文檔
    document = generate_long_document()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    docs = [Document(page_content=chunk) for chunk in text_splitter.split_text(document)]

    print(f"文檔分割為 {len(docs)} 塊")

    # Map 階段：摘要每個塊
    map_prompt = PromptTemplate.from_template(
        """請為以下文本生成簡潔的摘要：

        {text}

        摘要："""
    )

    map_chain = map_prompt | llm | StrOutputParser()

    # Reduce 階段：合併所有摘要
    reduce_prompt = PromptTemplate.from_template(
        """以下是多個文本塊的摘要，請將它們整合成一份完整、連貫的總摘要：

        {text}

        總摘要："""
    )

    reduce_chain = reduce_prompt | llm | StrOutputParser()

    # 使用 load_summarize_chain（簡化版）
    chain = load_summarize_chain(
        llm,
        chain_type="map_reduce",
        map_prompt=map_prompt,
        combine_prompt=reduce_prompt,
        verbose=True
    )

    print("\n開始處理...")
    summary = chain.run(docs)

    print("\n" + "="*80)
    print("Map-Reduce 摘要結果：")
    print("="*80)
    print(summary)

    return summary


# ============================================================================
# 範例 3: Refine 模式
# ============================================================================

def example_3_refine_summarization():
    """
    展示 Refine 模式處理長文檔

    流程：
    1. 處理第一個塊，生成初始摘要
    2. 依次處理後續塊，不斷精煉摘要
    3. 最終得到綜合的摘要

    優點：能夠保持上下文連貫性
    缺點：必須順序處理，無法並行
    """
    print("\n" + "="*80)
    print("範例 3: Refine 精煉模式")
    print("="*80)

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    # 準備文檔
    document = generate_long_document()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    docs = [Document(page_content=chunk) for chunk in text_splitter.split_text(document)]

    # 初始提示
    initial_prompt = PromptTemplate.from_template(
        """請為以下文本生成摘要：

        {text}

        摘要："""
    )

    # 精煉提示
    refine_prompt = PromptTemplate.from_template(
        """你已有的摘要：
        {existing_answer}

        現在有新的文本內容：
        {text}

        請根據新內容精煉和擴展摘要。如果新內容不相關，保持原摘要不變。

        精煉後的摘要："""
    )

    # 使用 refine 鏈
    chain = load_summarize_chain(
        llm,
        chain_type="refine",
        question_prompt=initial_prompt,
        refine_prompt=refine_prompt,
        verbose=True
    )

    print("\n開始精煉處理...")
    summary = chain.run(docs)

    print("\n" + "="*80)
    print("Refine 摘要結果：")
    print("="*80)
    print(summary)

    return summary


# ============================================================================
# 範例 4: 階層式摘要
# ============================================================================

def example_4_hierarchical_summarization():
    """
    展示階層式摘要策略

    流程：
    1. 將文檔分為多個部分
    2. 對每個部分生成摘要（第一層）
    3. 對第一層摘要再次摘要（第二層）
    4. 重複直到得到最終摘要

    優點：適合處理結構化的長文檔
    """
    print("\n" + "="*80)
    print("範例 4: 階層式摘要")
    print("="*80)

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    document = generate_long_document()

    # 第一層：按章節分割
    def split_by_chapter(text: str) -> List[str]:
        """按章節分割"""
        sections = []
        current_section = []

        for line in text.split('\n'):
            if line.startswith('第') and '章' in line:
                if current_section:
                    sections.append('\n'.join(current_section))
                current_section = [line]
            else:
                current_section.append(line)

        if current_section:
            sections.append('\n'.join(current_section))

        return sections

    chapters = split_by_chapter(document)
    print(f"第一層：分割為 {len(chapters)} 個章節")

    # 第二層：對每個章節生成摘要
    summarize_prompt = ChatPromptTemplate.from_template(
        "請用 2-3 句話總結以下內容：\n\n{text}\n\n摘要："
    )

    summarize_chain = summarize_prompt | llm | StrOutputParser()

    chapter_summaries = []
    print("\n第二層：生成各章節摘要")
    for i, chapter in enumerate(chapters, 1):
        if len(chapter.strip()) > 50:  # 跳過太短的章節
            summary = summarize_chain.invoke({"text": chapter})
            chapter_summaries.append(f"第{i}部分：{summary}")
            print(f"  章節 {i} 摘要: {summary[:60]}...")

    # 第三層：合併所有章節摘要
    print("\n第三層：生成總摘要")
    combined_summaries = "\n\n".join(chapter_summaries)

    final_prompt = ChatPromptTemplate.from_template(
        """以下是各個章節的摘要，請生成一份完整、連貫的總摘要：

        {summaries}

        總摘要（200字以內）："""
    )

    final_chain = final_prompt | llm | StrOutputParser()
    final_summary = final_chain.invoke({"summaries": combined_summaries})

    print("\n" + "="*80)
    print("階層式摘要結果：")
    print("="*80)
    print(final_summary)

    return final_summary


# ============================================================================
# 範例 5: 長上下文窗口處理
# ============================================================================

def example_5_long_context_window():
    """
    展示如何使用長上下文窗口模型處理長文檔

    GPT-4-turbo: 128K tokens
    Claude-3: 200K tokens
    Gemini 1.5 Pro: 1M tokens

    策略：
    - 直接處理整個文檔（如果在限制內）
    - 選擇性提取重要部分
    - 使用滑動窗口
    """
    print("\n" + "="*80)
    print("範例 5: 長上下文窗口處理")
    print("="*80)

    document = generate_long_document()
    token_count = count_tokens(document)

    print(f"文檔 token 數: {token_count}")

    # 使用長上下文模型
    llm_long_context = ChatOpenAI(
        model="gpt-4-turbo-preview",  # 128K context window
        temperature=0
    )

    if token_count < 100000:  # 在限制內
        print("\n文檔大小在長上下文窗口內，直接處理...")

        prompt = ChatPromptTemplate.from_template(
            """請分析以下長文檔並提供：
            1. 主要內容摘要
            2. 關鍵時間點和事件
            3. 重要人物或組織
            4. 主要結論

            文檔內容：
            {document}

            分析結果："""
        )

        chain = prompt | llm_long_context | StrOutputParser()

        # 注意：這裡為了演示，使用較小的模型
        # 實際使用時應該用 gpt-4-turbo 或 Claude-3
        llm_demo = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        chain_demo = prompt | llm_demo | StrOutputParser()

        # 由於上下文限制，這裡做簡化處理
        short_doc = document[:2000]  # 截取部分用於演示
        analysis = chain_demo.invoke({"document": short_doc})

        print("\n文檔分析結果：")
        print(analysis)
    else:
        print("\n文檔超出長上下文窗口，需要使用分塊策略...")


# ============================================================================
# 範例 6: 增量處理與記憶管理
# ============================================================================

def example_6_incremental_processing():
    """
    展示增量處理長文檔的策略

    特點：
    - 逐步處理文檔
    - 維護處理狀態
    - 壓縮歷史信息
    """
    print("\n" + "="*80)
    print("範例 6: 增量處理與記憶管理")
    print("="*80)

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    document = generate_long_document()

    # 分割文檔
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    chunks = splitter.split_text(document)

    print(f"文檔分為 {len(chunks)} 塊，開始增量處理...")

    # 初始化累積摘要
    accumulated_summary = ""

    # 逐塊處理
    for i, chunk in enumerate(chunks, 1):
        print(f"\n處理第 {i}/{len(chunks)} 塊...")

        if i == 1:
            # 第一塊：生成初始摘要
            prompt = ChatPromptTemplate.from_template(
                "請簡要總結以下內容（50字以內）：\n\n{text}"
            )
        else:
            # 後續塊：基於已有摘要更新
            prompt = ChatPromptTemplate.from_template(
                """已有摘要：{summary}

                新內容：{text}

                請更新摘要以包含新內容（保持在100字以內）："""
            )

        chain = prompt | llm | StrOutputParser()

        if i == 1:
            accumulated_summary = chain.invoke({"text": chunk})
        else:
            accumulated_summary = chain.invoke({
                "summary": accumulated_summary,
                "text": chunk
            })

        # 定期壓縮摘要（每3塊）
        if i % 3 == 0 and i < len(chunks):
            print("  壓縮累積摘要...")
            compress_prompt = ChatPromptTemplate.from_template(
                "請將以下摘要壓縮到 80 字以內，保留最重要的信息：\n\n{summary}"
            )
            compress_chain = compress_prompt | llm | StrOutputParser()
            accumulated_summary = compress_chain.invoke({"summary": accumulated_summary})

    print("\n" + "="*80)
    print("增量處理最終摘要：")
    print("="*80)
    print(accumulated_summary)

    return accumulated_summary


# ============================================================================
# 範例 7: 基於 RAG 的長文檔問答
# ============================================================================

def example_7_rag_for_long_documents():
    """
    展示使用 RAG 處理長文檔問答

    優點：
    - 只檢索相關部分
    - 減少 token 消耗
    - 適合多輪問答
    """
    print("\n" + "="*80)
    print("範例 7: 基於 RAG 的長文檔問答")
    print("="*80)

    # 準備文檔
    document = generate_long_document()

    # 分割並創建向量存儲
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = text_splitter.split_text(document)
    docs = [Document(page_content=chunk) for chunk in chunks]

    print(f"創建向量存儲，共 {len(docs)} 個文檔塊...")

    # 創建向量存儲
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        docs,
        embeddings,
        collection_name="long_doc_demo"
    )

    # 創建檢索器
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}  # 檢索最相關的3個塊
    )

    # 創建問答鏈
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    qa_prompt = ChatPromptTemplate.from_template(
        """基於以下上下文回答問題。如果上下文中沒有相關信息，請說"文檔中沒有提到"。

        上下文：
        {context}

        問題：{question}

        回答："""
    )

    def format_docs(docs):
        return "\n\n".join([doc.page_content for doc in docs])

    qa_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | qa_prompt
        | llm
        | StrOutputParser()
    )

    # 測試多個問題
    questions = [
        "人工智能是什麼時候開始的？",
        "深藍計算機在哪一年擊敗了國際象棋冠軍？",
        "GPT-3 有多少參數？",
        "未來人工智能的發展方向有哪些？"
    ]

    print("\n開始問答：")
    for q in questions:
        print(f"\n問題：{q}")
        answer = qa_chain.invoke(q)
        print(f"回答：{answer}")

    # 清理
    vectorstore.delete_collection()

    return qa_chain


# ============================================================================
# 主函數
# ============================================================================

def main():
    """運行所有長文本處理範例"""

    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║            長文本處理策略 - 完整示範                           ║
    ║                                                                ║
    ║  展示處理長文檔的各種策略和最佳實踐                            ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

    # 檢查環境變數
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 錯誤: 請設置 OPENAI_API_KEY 環境變數")
        return

    try:
        # 運行範例
        example_1_text_splitting_strategies()
        example_2_map_reduce_summarization()
        example_3_refine_summarization()
        example_4_hierarchical_summarization()
        example_5_long_context_window()
        example_6_incremental_processing()
        example_7_rag_for_long_documents()

        print("\n" + "="*80)
        print("✅ 所有範例執行完成！")
        print("="*80)

    except Exception as e:
        print(f"\n❌ 執行過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


# ============================================================================
# 學習要點總結
# ============================================================================
"""
📚 長文本處理學習要點：

1. **文檔分割策略**

   a) RecursiveCharacterTextSplitter（推薦）
      - 遞歸使用多個分隔符
      - 保持文本的自然結構
      - 最靈活和常用

   b) TokenTextSplitter
      - 基於 token 數量分割
      - 精確控制長度
      - 避免超出模型限制

   c) 語義分割
      - 基於內容結構（章節、段落）
      - 保持語義完整性
      - 適合結構化文檔

2. **處理模式**

   a) Map-Reduce
      - 並行處理各個塊
      - 然後合併結果
      - 適合: 摘要、分類

   b) Refine
      - 順序處理，不斷精煉
      - 保持上下文連貫
      - 適合: 需要前後關聯的任務

   c) Stuff
      - 直接填充所有內容
      - 最簡單但受限於上下文長度
      - 適合: 較短文檔

3. **階層式處理**
   - 多層次摘要
   - 逐步壓縮信息
   - 保留重要細節
   - 適合: 長報告、論文

4. **長上下文窗口**
   - 使用長上下文模型（GPT-4-turbo, Claude-3, Gemini）
   - 直接處理整個文檔
   - 減少分塊帶來的信息損失
   - 注意: 成本較高

5. **增量處理**
   - 逐步處理文檔
   - 維護累積狀態
   - 定期壓縮記憶
   - 適合: 流式數據、超長文檔

6. **RAG 方法**
   - 向量化文檔塊
   - 按需檢索相關部分
   - 減少不必要的處理
   - 適合: 問答、信息提取

💡 選擇策略的考量因素：

1. 文檔長度
   - < 4K tokens: 直接處理（Stuff）
   - 4K - 16K: Map-Reduce 或 Refine
   - 16K - 100K: 階層式或長上下文模型
   - > 100K: RAG + 分塊處理

2. 任務類型
   - 摘要: Map-Reduce, 階層式
   - 問答: RAG
   - 分析: Refine, 長上下文
   - 信息提取: RAG

3. 資源限制
   - Token 預算: 選擇高效的分塊策略
   - 時間要求: 並行處理（Map-Reduce）
   - 質量要求: Refine 或長上下文

4. 文檔結構
   - 結構化（章節清晰）: 語義分割，階層式
   - 非結構化: 遞歸分割，RAG

🔧 最佳實踐：

1. 合理設置 chunk_size 和 chunk_overlap
   - chunk_size: 根據模型限制和任務需求
   - chunk_overlap: 10-20% 的 chunk_size

2. 使用合適的分隔符
   - 中文: \n\n, \n, 。, ，
   - 英文: \n\n, \n, ., ,
   - 代碼: 基於語法結構

3. Token 計數
   - 使用 tiktoken 精確計算
   - 預留空間給提示和響應

4. 記憶管理
   - 定期壓縮累積信息
   - 只保留關鍵內容
   - 避免記憶溢出

5. 測試與優化
   - 在真實數據上測試
   - 監控質量和成本
   - 迭代優化參數

🔗 相關資源：
- Text Splitters: https://python.langchain.com/docs/modules/data_connection/document_transformers/
- Summarization: https://python.langchain.com/docs/use_cases/summarization
- RAG: https://python.langchain.com/docs/use_cases/question_answering/
"""
