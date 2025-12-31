"""
Marvin 自定義模型示例

本示例展示：
1. 自定義 LLM 配置
2. 模型選擇
3. 參數調整
4. 提示詞工程
5. 溫度和 top_p 設置

運行方式：
    python 08_自定義模型.py
"""

import os
import marvin
from marvin.settings import Settings
from typing import Optional
from pydantic import BaseModel


# ==================== 模型選擇 ====================

def example_model_selection():
    """示例 1: 選擇不同的 LLM 模型"""
    print("\n" + "="*60)
    print("示例 1: 選擇不同的 LLM 模型")
    print("="*60)

    try:
        print("模型選擇示例:\n")

        # 使用 GPT-4
        @marvin.fn(model="gpt-4")
        def complex_analysis(text: str) -> str:
            """進行複雜的文本分析"""

        # 使用 GPT-3.5 Turbo（更快更便宜）
        @marvin.fn(model="gpt-3.5-turbo")
        def simple_task(text: str) -> str:
            """處理簡單任務"""

        # 使用特定版本
        @marvin.fn(model="gpt-4-turbo-preview")
        def latest_features(text: str) -> str:
            """使用最新功能"""

        print("示例代碼:")
        print("""
        # 不同任務使用不同模型

        # 複雜任務 - 使用 GPT-4
        @marvin.fn(model="gpt-4")
        def analyze_complex_data(data: str) -> dict:
            '''深度分析複雜數據'''

        # 簡單任務 - 使用 GPT-3.5
        @marvin.fn(model="gpt-3.5-turbo")
        def simple_classification(text: str) -> str:
            '''簡單分類任務'''

        # 成本優化策略
        complex_result = analyze_complex_data(complex_data)
        simple_result = simple_classification(simple_text)
        """)

        print("\n可用模型:")
        print("  🚀 gpt-4 - 最強大，適合複雜任務")
        print("  ⚡ gpt-3.5-turbo - 快速且經濟")
        print("  🆕 gpt-4-turbo - 新功能和更大上下文")
        print("  💰 根據任務選擇合適的模型")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 溫度參數調整 ====================

def example_temperature():
    """示例 2: 調整溫度參數"""
    print("\n" + "="*60)
    print("示例 2: 調整溫度參數")
    print("="*60)

    try:
        print("溫度參數影響輸出的隨機性:\n")

        print("示例代碼:")
        print("""
        # 低溫度 (0.0-0.3) - 更確定性的輸出
        @marvin.fn(model_kwargs={"temperature": 0.1})
        def factual_answer(question: str) -> str:
            '''提供準確的事實性回答'''

        # 中等溫度 (0.5-0.7) - 平衡創意和準確性
        @marvin.fn(model_kwargs={"temperature": 0.7})
        def balanced_response(prompt: str) -> str:
            '''平衡的響應'''

        # 高溫度 (0.8-1.0) - 更有創意
        @marvin.fn(model_kwargs={"temperature": 0.9})
        def creative_writing(topic: str) -> str:
            '''創意寫作'''

        # 比較不同溫度的輸出
        question = "什麼是人工智能？"

        precise = factual_answer(question)      # temperature=0.1
        balanced = balanced_response(question)   # temperature=0.7
        creative = creative_writing(question)    # temperature=0.9

        print(f"精確回答: {precise}")
        print(f"平衡回答: {balanced}")
        print(f"創意回答: {creative}")
        """)

        print("\n溫度選擇指南:")
        print("  ❄️ 0.0-0.3: 事實性任務、數據提取、分類")
        print("  🌤️ 0.4-0.7: 一般對話、摘要、翻譯")
        print("  🔥 0.8-1.0: 創意寫作、頭腦風暴、故事生成")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== Top-p 參數 ====================

def example_top_p():
    """示例 3: Top-p（Nucleus Sampling）參數"""
    print("\n" + "="*60)
    print("示例 3: Top-p 參數")
    print("="*60)

    try:
        print("Top-p 控制採樣的多樣性:\n")

        print("示例代碼:")
        print("""
        # 低 top-p - 更保守的選擇
        @marvin.fn(model_kwargs={"top_p": 0.1})
        def conservative_response(text: str) -> str:
            '''保守的響應'''

        # 高 top-p - 更多樣化的選擇
        @marvin.fn(model_kwargs={"top_p": 0.9})
        def diverse_response(text: str) -> str:
            '''多樣化的響應'''

        # 結合溫度和 top-p
        @marvin.fn(model_kwargs={
            "temperature": 0.7,
            "top_p": 0.9
        })
        def optimized_response(text: str) -> str:
            '''優化的響應'''
        """)

        print("\nTop-p 使用建議:")
        print("  📊 0.1-0.5: 需要一致性的任務")
        print("  🎯 0.5-0.9: 一般用途")
        print("  🎲 0.9-1.0: 需要多樣性的任務")
        print("\n  💡 通常調整溫度或 top-p 之一，不要同時調整")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 自定義提示詞 ====================

def example_custom_prompts():
    """示例 4: 自定義提示詞工程"""
    print("\n" + "="*60)
    print("示例 4: 自定義提示詞工程")
    print("="*60)

    try:
        print("通過文檔字符串自定義提示詞:\n")

        @marvin.fn
        def analyze_sentiment_detailed(text: str) -> dict:
            """
            深度分析文本的情感

            要求：
            1. 識別主要情感（positive/negative/neutral）
            2. 計算情感強度（0-1 分數）
            3. 提取情感關鍵詞
            4. 給出情感理由

            返回格式：
            {
                "sentiment": "主要情感",
                "intensity": 強度分數,
                "keywords": ["關鍵詞列表"],
                "reason": "判斷理由"
            }
            """

        @marvin.fn
        def extract_with_context(text: str, context: str) -> list:
            """
            根據上下文提取信息

            上下文：{context}

            從文本中提取與上下文相關的所有信息，
            以列表形式返回。每個項目都應該是獨立的、
            完整的信息單元。
            """

        print("提示詞工程示例:")
        print("""
        @marvin.fn
        def structured_extraction(text: str) -> dict:
            '''
            從文本中提取結構化信息

            步驟：
            1. 識別所有實體（人名、地名、組織）
            2. 提取時間信息
            3. 識別關鍵動作
            4. 總結主要內容

            輸出格式：
            {
                "entities": {
                    "people": [],
                    "places": [],
                    "organizations": []
                },
                "time": "",
                "actions": [],
                "summary": ""
            }

            注意：
            - 確保所有字段都有值，沒有則為空
            - 使用原文的表達方式
            - 保持客觀中立
            '''
        """)

        print("\n提示詞最佳實踐:")
        print("  ✅ 明確具體的指令")
        print("  ✅ 提供輸出格式示例")
        print("  ✅ 列出處理步驟")
        print("  ✅ 說明邊界情況處理")
        print("  ✅ 指定輸出約束")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 全局配置 ====================

def example_global_settings():
    """示例 5: 全局設置配置"""
    print("\n" + "="*60)
    print("示例 5: 全局設置配置")
    print("="*60)

    try:
        print("配置 Marvin 全局設置:\n")

        print("示例代碼:")
        print("""
        import marvin

        # 配置 OpenAI
        marvin.settings.openai.api_key = "your-api-key"
        marvin.settings.openai.organization = "your-org-id"
        marvin.settings.openai.api_base = "https://api.openai.com/v1"

        # 設置默認模型
        marvin.settings.llm_model = "gpt-4"

        # 設置默認溫度
        marvin.settings.llm_temperature = 0.7

        # 配置日誌
        marvin.settings.log_level = "INFO"
        marvin.settings.log_verbose = True

        # 配置緩存
        marvin.settings.cache_enabled = True
        marvin.settings.cache_ttl = 3600  # 秒

        # 配置重試
        marvin.settings.max_retries = 3
        marvin.settings.retry_delay = 1  # 秒
        """)

        print("\n可配置項:")
        print("  🔑 API 密鑰和組織")
        print("  🤖 默認模型")
        print("  🌡️ 默認溫度")
        print("  📝 日誌級別")
        print("  💾 緩存設置")
        print("  🔄 重試策略")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 自定義提供商 ====================

def example_custom_provider():
    """示例 6: 使用自定義 LLM 提供商"""
    print("\n" + "="*60)
    print("示例 6: 使用自定義 LLM 提供商")
    print("="*60)

    try:
        print("配置自定義 LLM 提供商:\n")

        print("示例代碼:")
        print("""
        import marvin

        # 使用 Azure OpenAI
        marvin.settings.openai.api_base = "https://your-resource.openai.azure.com/"
        marvin.settings.openai.api_type = "azure"
        marvin.settings.openai.api_version = "2023-05-15"
        marvin.settings.openai.api_key = "your-azure-key"

        # 使用兼容 OpenAI API 的服務
        marvin.settings.openai.api_base = "https://your-llm-service.com/v1"
        marvin.settings.openai.api_key = "your-service-key"

        # 使用本地 LLM（如 Ollama）
        marvin.settings.openai.api_base = "http://localhost:11434/v1"
        marvin.settings.openai.api_key = "not-needed"

        @marvin.fn(model="llama2")
        def local_function(text: str) -> str:
            '''使用本地模型的函數'''
        """)

        print("\n支持的提供商:")
        print("  ☁️ Azure OpenAI")
        print("  🏢 OpenAI 兼容服務")
        print("  💻 本地 LLM（Ollama 等）")
        print("  🌐 其他 API 提供商")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 性能優化 ====================

def example_performance_optimization():
    """示例 7: 性能優化配置"""
    print("\n" + "="*60)
    print("示例 7: 性能優化配置")
    print("="*60)

    try:
        print("優化 Marvin 性能:\n")

        print("示例代碼:")
        print("""
        import marvin

        # 1. 使用緩存
        @marvin.fn(cache=True)
        def cached_function(text: str) -> str:
            '''結果會被緩存，相同輸入直接返回'''

        # 2. 選擇合適的模型
        # 簡單任務使用更快的模型
        @marvin.fn(model="gpt-3.5-turbo")
        def fast_task(text: str) -> str:
            '''快速處理'''

        # 3. 批量處理
        texts = ["text1", "text2", "text3"]
        results = [cached_function(t) for t in texts]

        # 4. 異步處理
        import asyncio

        @marvin.fn
        async def async_task(text: str) -> str:
            '''異步處理'''

        async def batch_process(texts):
            tasks = [async_task(t) for t in texts]
            return await asyncio.gather(*tasks)

        # 5. 限制輸出長度
        @marvin.fn(model_kwargs={"max_tokens": 100})
        def short_response(text: str) -> str:
            '''限制響應長度'''

        # 6. 調整超時
        marvin.settings.timeout = 30  # 秒
        """)

        print("\n優化策略:")
        print("  💾 啟用緩存")
        print("  🎯 選擇合適的模型")
        print("  📦 批量處理")
        print("  ⚡ 異步調用")
        print("  ✂️ 限制輸出長度")
        print("  ⏱️ 合理設置超時")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║      Marvin 自定義模型配置示例            ║
╚══════════════════════════════════════════╝

配置選項:
✅ 模型選擇
✅ 溫度和 top-p 參數
✅ 自定義提示詞
✅ 全局設置
✅ 自定義提供商
✅ 性能優化
    """)

    # 檢查環境
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 請設置 OPENAI_API_KEY 環境變量")
        return

    # 配置 Marvin
    marvin.settings.openai.api_key = os.getenv("OPENAI_API_KEY")

    # 運行示例
    example_model_selection()
    example_temperature()
    example_top_p()
    example_custom_prompts()
    example_global_settings()
    example_custom_provider()
    example_performance_optimization()

    print("\n" + "="*60)
    print("✅ 所有示例演示完成！")
    print("="*60)


if __name__ == "__main__":
    main()
