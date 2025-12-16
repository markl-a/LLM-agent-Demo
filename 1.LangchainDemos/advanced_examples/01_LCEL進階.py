"""
01_LCEL進階.py - LangChain Expression Language 進階用法

本範例展示 LCEL (LangChain Expression Language) 的進階特性，包括：
- 複雜鏈組合與管道操作
- 動態參數傳遞與配置
- 串流處理與非同步執行
- 錯誤處理與重試機制
- Fallback 降級策略
- 並行執行與分支
- 自定義 Runnable 組件

作者：LLM-agent-Demo Team
日期：2025-12
"""

import os
from typing import Dict, List, Any, Optional
from operator import itemgetter

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import (
    RunnablePassthrough,
    RunnableParallel,
    RunnableLambda,
    RunnableBranch,
    Runnable,
    RunnableConfig
)
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()


# ============================================================================
# 範例 1: 基礎 LCEL 鏈組合
# ============================================================================
def example_1_basic_chain():
    """
    展示基礎的 LCEL 鏈組合，使用管道操作符 | 連接各個組件

    流程: Prompt → LLM → Output Parser
    """
    print("\n" + "="*80)
    print("範例 1: 基礎 LCEL 鏈組合")
    print("="*80)

    # 創建提示模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一位專業的翻譯專家，請將用戶的輸入翻譯成{target_language}。"),
        ("human", "{text}")
    ])

    # 創建 LLM
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    # 創建輸出解析器
    output_parser = StrOutputParser()

    # 使用 LCEL 組合鏈
    chain = prompt | llm | output_parser

    # 執行鏈
    result = chain.invoke({
        "target_language": "英文",
        "text": "今天天氣真好，適合出去散步。"
    })

    print(f"翻譯結果: {result}")

    return chain


# ============================================================================
# 範例 2: 並行執行 - RunnableParallel
# ============================================================================
def example_2_parallel_execution():
    """
    展示如何使用 RunnableParallel 並行執行多個任務

    特點：
    - 多個任務同時執行，提高效率
    - 結果以字典形式返回
    - 適合需要多角度分析的場景
    """
    print("\n" + "="*80)
    print("範例 2: 並行執行 - RunnableParallel")
    print("="*80)

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

    # 創建多個提示模板
    sentiment_prompt = ChatPromptTemplate.from_template(
        "分析以下文本的情感（正面/負面/中性）：\n\n{text}\n\n只返回情感類型。"
    )

    summary_prompt = ChatPromptTemplate.from_template(
        "用一句話總結以下文本：\n\n{text}"
    )

    keywords_prompt = ChatPromptTemplate.from_template(
        "提取以下文本的 3 個關鍵詞，用逗號分隔：\n\n{text}"
    )

    # 創建並行鏈
    parallel_chain = RunnableParallel({
        "sentiment": sentiment_prompt | llm | StrOutputParser(),
        "summary": summary_prompt | llm | StrOutputParser(),
        "keywords": keywords_prompt | llm | StrOutputParser()
    })

    # 執行
    text = """
    人工智能技術正在快速發展，深度學習模型在各個領域都取得了突破性進展。
    從自然語言處理到計算機視覺，AI 的應用越來越廣泛，極大地提升了生產效率。
    """

    results = parallel_chain.invoke({"text": text})

    print(f"情感分析: {results['sentiment']}")
    print(f"內容摘要: {results['summary']}")
    print(f"關鍵詞: {results['keywords']}")

    return parallel_chain


# ============================================================================
# 範例 3: 條件分支 - RunnableBranch
# ============================================================================
def example_3_conditional_branching():
    """
    展示如何使用 RunnableBranch 實現條件路由

    根據輸入的不同特徵，選擇不同的處理鏈
    """
    print("\n" + "="*80)
    print("範例 3: 條件分支 - RunnableBranch")
    print("="*80)

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    # 定義不同語言的處理鏈
    chinese_chain = (
        ChatPromptTemplate.from_template("用中文詳細回答：{question}")
        | llm
        | StrOutputParser()
    )

    english_chain = (
        ChatPromptTemplate.from_template("Answer in English: {question}")
        | llm
        | StrOutputParser()
    )

    technical_chain = (
        ChatPromptTemplate.from_template("用技術術語詳細解釋：{question}")
        | llm
        | StrOutputParser()
    )

    # 判斷函數
    def route_by_language(input_dict: Dict) -> str:
        """根據問題類型決定路由"""
        question = input_dict["question"].lower()

        if "技術" in question or "程式" in question or "algorithm" in question:
            return "technical"
        elif any(char in question for char in "abcdefghijklmnopqrstuvwxyz"):
            return "english"
        else:
            return "chinese"

    # 創建分支鏈
    branch_chain = RunnableBranch(
        (lambda x: route_by_language(x) == "technical", technical_chain),
        (lambda x: route_by_language(x) == "english", english_chain),
        chinese_chain  # 默認分支
    )

    # 測試不同類型的問題
    questions = [
        "什麼是機器學習？",
        "What is machine learning?",
        "解釋快速排序算法的技術原理"
    ]

    for q in questions:
        print(f"\n問題: {q}")
        result = branch_chain.invoke({"question": q})
        print(f"回答: {result[:100]}...")


# ============================================================================
# 範例 4: 動態參數傳遞與轉換
# ============================================================================
def example_4_dynamic_parameters():
    """
    展示如何在鏈中動態傳遞和轉換參數

    使用技巧：
    - RunnablePassthrough: 透傳參數
    - RunnableLambda: 自定義轉換函數
    - itemgetter: 提取字典中的特定鍵值
    """
    print("\n" + "="*80)
    print("範例 4: 動態參數傳遞與轉換")
    print("="*80)

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    # 定義轉換函數
    def format_context(docs: List[str]) -> str:
        """將文檔列表格式化為上下文字符串"""
        return "\n\n".join([f"文檔 {i+1}: {doc}" for i, doc in enumerate(docs)])

    def extract_keywords(text: str) -> str:
        """從問題中提取關鍵詞（簡化版）"""
        # 實際應用中可以使用更複雜的 NLP 技術
        keywords = [word for word in text.split() if len(word) > 2]
        return ", ".join(keywords[:3])

    # 創建複雜的數據處理鏈
    chain = (
        {
            "question": itemgetter("question"),
            "context": itemgetter("documents") | RunnableLambda(format_context),
            "keywords": itemgetter("question") | RunnableLambda(extract_keywords),
            "language": RunnablePassthrough() | (lambda x: x.get("language", "中文"))
        }
        | ChatPromptTemplate.from_template(
            """基於以下上下文回答問題。

            上下文：
            {context}

            關鍵詞：{keywords}
            語言：{language}

            問題：{question}

            請用{language}回答："""
        )
        | llm
        | StrOutputParser()
    )

    # 執行
    result = chain.invoke({
        "question": "人工智能如何改變醫療行業？",
        "documents": [
            "AI 在醫療影像診斷中可以提高準確率",
            "機器學習算法可以預測疾病風險",
            "自然語言處理幫助分析醫療記錄"
        ],
        "language": "中文"
    })

    print(f"回答:\n{result}")


# ============================================================================
# 範例 5: 串流處理
# ============================================================================
def example_5_streaming():
    """
    展示 LCEL 的串流處理能力

    優點：
    - 實時獲取生成結果
    - 改善用戶體驗
    - 降低首字延遲
    """
    print("\n" + "="*80)
    print("範例 5: 串流處理")
    print("="*80)

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, streaming=True)

    prompt = ChatPromptTemplate.from_template(
        "寫一個關於{topic}的簡短故事（50字以內）："
    )

    chain = prompt | llm | StrOutputParser()

    print("開始串流輸出（故事主題：太空探險）：\n")

    # 串流輸出
    for chunk in chain.stream({"topic": "太空探險"}):
        print(chunk, end="", flush=True)

    print("\n")


# ============================================================================
# 範例 6: 錯誤處理與重試
# ============================================================================
def example_6_error_handling():
    """
    展示如何在 LCEL 中實現錯誤處理和重試機制

    策略：
    - with_retry: 自動重試
    - with_fallbacks: 降級策略
    - 異常處理包裝
    """
    print("\n" + "="*80)
    print("範例 6: 錯誤處理與重試")
    print("="*80)

    # 創建主 LLM（可能失敗）
    primary_llm = ChatOpenAI(
        model="gpt-4",  # 假設這個模型可能超時
        temperature=0,
        request_timeout=5
    )

    # 創建備用 LLM
    fallback_llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0
    )

    prompt = ChatPromptTemplate.from_template(
        "簡單解釋：{concept}"
    )

    # 方式 1: 使用 with_fallbacks
    chain_with_fallback = (
        prompt
        | primary_llm.with_fallbacks([fallback_llm])
        | StrOutputParser()
    )

    # 方式 2: 使用自定義錯誤處理
    def safe_invoke(chain: Runnable, input_data: Dict, max_retries: int = 3):
        """安全執行鏈，帶重試機制"""
        for attempt in range(max_retries):
            try:
                return chain.invoke(input_data)
            except Exception as e:
                print(f"嘗試 {attempt + 1} 失敗: {str(e)[:50]}")
                if attempt == max_retries - 1:
                    return f"執行失敗，已達最大重試次數。錯誤: {str(e)[:100]}"

    # 執行
    try:
        result = chain_with_fallback.invoke({"concept": "量子計算"})
        print(f"結果: {result}")
    except Exception as e:
        print(f"錯誤: {e}")


# ============================================================================
# 範例 7: 自定義 Runnable 組件
# ============================================================================
class CustomTransformRunnable(Runnable):
    """
    自定義 Runnable 組件範例

    實現自己的數據轉換邏輯，可以無縫集成到 LCEL 鏈中
    """

    def __init__(self, transform_func):
        self.transform_func = transform_func

    def invoke(self, input: Any, config: Optional[RunnableConfig] = None) -> Any:
        """同步執行"""
        return self.transform_func(input)

    async def ainvoke(self, input: Any, config: Optional[RunnableConfig] = None) -> Any:
        """非同步執行"""
        return self.transform_func(input)


def example_7_custom_runnable():
    """展示如何創建和使用自定義 Runnable 組件"""
    print("\n" + "="*80)
    print("範例 7: 自定義 Runnable 組件")
    print("="*80)

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    # 自定義轉換函數
    def add_metadata(input_dict: Dict) -> Dict:
        """添加元數據到輸入"""
        import time
        input_dict["timestamp"] = time.time()
        input_dict["processed"] = True
        return input_dict

    def format_output(text: str) -> str:
        """格式化輸出"""
        return f"【AI 回答】\n{text}\n{'='*40}"

    # 創建自定義 Runnable
    metadata_adder = CustomTransformRunnable(add_metadata)
    output_formatter = CustomTransformRunnable(format_output)

    # 組合鏈
    chain = (
        metadata_adder
        | RunnablePassthrough.assign(
            answer=ChatPromptTemplate.from_template("回答: {question}") | llm | StrOutputParser()
        )
        | (lambda x: x["answer"])
        | output_formatter
    )

    # 執行
    result = chain.invoke({"question": "什麼是 LCEL？"})
    print(result)


# ============================================================================
# 範例 8: 複雜的數據流轉換
# ============================================================================
def example_8_complex_data_flow():
    """
    展示複雜的數據流轉換和組合

    場景：多步驟文檔分析流程
    1. 提取關鍵信息
    2. 並行進行情感分析和主題提取
    3. 生成綜合報告
    """
    print("\n" + "="*80)
    print("範例 8: 複雜的數據流轉換")
    print("="*80)

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    # 第一步：提取關鍵信息
    extraction_chain = (
        ChatPromptTemplate.from_template(
            "從以下文本中提取主要事實和數據：\n\n{text}"
        )
        | llm
        | StrOutputParser()
    )

    # 第二步：並行分析
    analysis_chain = RunnableParallel({
        "sentiment": ChatPromptTemplate.from_template(
            "分析情感傾向：{extracted_info}"
        ) | llm | StrOutputParser(),

        "topics": ChatPromptTemplate.from_template(
            "識別主要話題：{extracted_info}"
        ) | llm | StrOutputParser(),

        "key_points": RunnablePassthrough()
    })

    # 第三步：生成報告
    report_chain = (
        ChatPromptTemplate.from_template(
            """生成分析報告：

            關鍵信息：{key_points}
            情感分析：{sentiment}
            主要話題：{topics}

            請生成一份簡潔的綜合報告："""
        )
        | llm
        | StrOutputParser()
    )

    # 組合完整流程
    full_chain = (
        {"text": RunnablePassthrough()}
        | RunnablePassthrough.assign(extracted_info=extraction_chain)
        | (lambda x: {"extracted_info": x["extracted_info"]})
        | analysis_chain
        | report_chain
    )

    # 執行
    document = """
    本季度公司營收達到 1000 萬美元，同比增長 25%。
    客戶滿意度提升到 92%，員工士氣高昂。
    新產品線獲得市場積極反響，預計下季度將繼續保持增長態勢。
    """

    result = full_chain.invoke(document)
    print(f"綜合報告:\n{result}")


# ============================================================================
# 範例 9: 使用配置動態調整行為
# ============================================================================
def example_9_configurable_chain():
    """
    展示如何創建可配置的鏈，在運行時調整行為

    特點：
    - 動態模型選擇
    - 溫度參數調整
    - 輸出格式切換
    """
    print("\n" + "="*80)
    print("範例 9: 可配置的動態鏈")
    print("="*80)

    from langchain_core.runnables import ConfigurableField

    # 創建可配置的 LLM
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0
    ).configurable_fields(
        temperature=ConfigurableField(
            id="llm_temperature",
            name="LLM Temperature",
            description="溫度參數，控制輸出的隨機性"
        ),
        model=ConfigurableField(
            id="llm_model",
            name="LLM Model",
            description="使用的模型名稱"
        )
    )

    prompt = ChatPromptTemplate.from_template("寫一首關於{topic}的詩：")
    chain = prompt | llm | StrOutputParser()

    # 使用不同配置執行
    configs = [
        {"configurable": {"llm_temperature": 0.2}},
        {"configurable": {"llm_temperature": 0.9}},
    ]

    for i, config in enumerate(configs, 1):
        print(f"\n配置 {i} (溫度={config['configurable']['llm_temperature']}):")
        result = chain.invoke({"topic": "春天"}, config=config)
        print(result[:100] + "...")


# ============================================================================
# 主函數：運行所有範例
# ============================================================================
def main():
    """運行所有 LCEL 進階範例"""

    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║              LCEL 進階使用範例 - 完整示範                      ║
    ║                                                                ║
    ║  本腳本展示 LangChain Expression Language 的進階特性          ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

    # 檢查環境變數
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 錯誤: 請設置 OPENAI_API_KEY 環境變數")
        return

    try:
        # 運行各個範例
        example_1_basic_chain()
        example_2_parallel_execution()
        example_3_conditional_branching()
        example_4_dynamic_parameters()
        example_5_streaming()
        example_6_error_handling()
        example_7_custom_runnable()
        example_8_complex_data_flow()
        example_9_configurable_chain()

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
📚 LCEL 進階學習要點：

1. **管道操作符 |**
   - 連接各個 Runnable 組件
   - 數據自動在組件間流動
   - 清晰的鏈式調用語法

2. **並行執行 RunnableParallel**
   - 同時執行多個獨立任務
   - 提高處理效率
   - 結果以字典形式組織

3. **條件分支 RunnableBranch**
   - 根據條件選擇不同的處理路徑
   - 實現智能路由
   - 支持默認分支

4. **動態參數傳遞**
   - RunnablePassthrough: 透傳參數
   - RunnableLambda: 自定義轉換
   - itemgetter: 提取特定字段

5. **串流處理**
   - 實時輸出生成結果
   - 降低首字延遲
   - 改善用戶體驗

6. **錯誤處理**
   - with_fallbacks: 降級策略
   - with_retry: 自動重試
   - 自定義異常處理

7. **自定義 Runnable**
   - 繼承 Runnable 基類
   - 實現 invoke 和 ainvoke 方法
   - 無縫集成到 LCEL 鏈中

8. **可配置鏈**
   - ConfigurableField: 定義可配置項
   - 運行時動態調整參數
   - 提高鏈的靈活性

💡 最佳實踐：
- 保持鏈的簡潔性，避免過度複雜
- 合理使用並行處理提高效率
- 實施完善的錯誤處理機制
- 利用串流改善用戶體驗
- 使用類型提示提高代碼可維護性

🔗 相關資源：
- LangChain 官方文檔: https://python.langchain.com/docs/expression_language/
- LCEL Cookbook: https://python.langchain.com/docs/expression_language/cookbook/
"""
