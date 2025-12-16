"""
PromptFlow 快速開始指南

這個範例展示了 PromptFlow 的基礎概念和使用方式：
1. 基本安裝和配置
2. 簡單的 LLM 調用
3. 使用 Prompty 模板
4. Trace 追蹤功能
5. 基礎錯誤處理

作者：LLM Agent Demo Project
日期：2025-12-15
"""

import os
from dotenv import load_dotenv

# 載入環境變量
load_dotenv()


# ============================================
# 範例 1: 基本的函數調用與 Trace
# ============================================
def example_1_basic_trace():
    """
    展示如何使用 @trace 裝飾器追蹤函數執行

    @trace 裝飾器會自動記錄函數的輸入、輸出和執行時間，
    這對於調試和性能分析非常有用。
    """
    print("=" * 50)
    print("範例 1: 基本的函數追蹤")
    print("=" * 50)

    from promptflow.tracing import trace

    @trace
    def greet(name: str) -> str:
        """簡單的問候函數，帶有 trace 追蹤"""
        return f"你好，{name}！歡迎使用 PromptFlow。"

    # 調用函數
    result = greet("開發者")
    print(f"結果: {result}")
    print()


# ============================================
# 範例 2: 使用 Prompty 進行 LLM 調用
# ============================================
def example_2_basic_llm_call():
    """
    展示如何使用 Prompty 類進行基本的 LLM 調用

    Prompty 是 PromptFlow 中用於執行提示詞的核心類，
    它可以加載 .prompty 文件或直接使用字典配置。
    """
    print("=" * 50)
    print("範例 2: 基本的 LLM 調用")
    print("=" * 50)

    try:
        from promptflow.core import Prompty
        from promptflow.tracing import trace

        @trace
        def chat_with_llm(question: str) -> str:
            """使用 LLM 回答問題"""

            # 定義提示詞模板
            prompt_template = """
            你是一個友善的 AI 助手。請用繁體中文回答以下問題：

            問題：{{question}}

            回答：
            """

            # 創建 Prompty 配置
            # 注意：這裡使用字典配置而不是 .prompty 文件
            prompty_config = {
                "name": "basic_chat",
                "description": "基本的對話功能",
                "model": {
                    "api": "chat",
                    "configuration": {
                        "type": "azure_openai",
                        "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
                        "azure_deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                        "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
                        "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
                    },
                    "parameters": {
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                },
                "inputs": {
                    "question": {
                        "type": "string"
                    }
                },
                "outputs": {
                    "answer": {
                        "type": "string"
                    }
                },
                "template": prompt_template
            }

            # 如果沒有配置 Azure OpenAI，使用 OpenAI
            if not os.getenv("AZURE_OPENAI_ENDPOINT"):
                prompty_config["model"]["configuration"] = {
                    "type": "openai",
                    "api_key": os.getenv("OPENAI_API_KEY"),
                    "organization": os.getenv("OPENAI_ORG_ID", "")
                }

            # 注意：實際使用時需要有效的 API 配置
            # 這裡僅展示結構，實際執行需要真實的 API 密鑰
            print("提示：實際執行需要配置有效的 API 密鑰")
            print(f"問題: {question}")

            # 模擬回答（實際使用時會調用 LLM）
            simulated_answer = f"這是對「{question}」的模擬回答。實際使用時會調用真實的 LLM。"

            return simulated_answer

        # 測試調用
        question = "什麼是 PromptFlow？"
        answer = chat_with_llm(question)
        print(f"\n回答: {answer}")
        print()

    except ImportError as e:
        print(f"導入錯誤: {e}")
        print("請確保已安裝: pip install promptflow promptflow-tools")
        print()


# ============================================
# 範例 3: 創建簡單的 Prompty 文件
# ============================================
def example_3_create_prompty_file():
    """
    展示如何創建和使用 .prompty 文件

    .prompty 文件是一種特殊的 Markdown 文件，
    包含 YAML frontmatter 和提示詞模板。
    """
    print("=" * 50)
    print("範例 3: 創建 Prompty 文件")
    print("=" * 50)

    # Prompty 文件內容
    prompty_content = """---
name: Simple Chat
description: 簡單的對話提示詞模板
model:
  api: chat
  configuration:
    type: azure_openai
    azure_endpoint: ${env:AZURE_OPENAI_ENDPOINT}
    azure_deployment: ${env:AZURE_OPENAI_DEPLOYMENT_NAME}
  parameters:
    temperature: 0.7
    max_tokens: 500
inputs:
  question:
    type: string
outputs:
  answer:
    type: string
---

# 系統提示詞
你是一個專業的 AI 助手，擅長回答技術問題。

# 用戶問題
{{question}}

# 回答要求
請用繁體中文回答，並確保答案準確、清晰、有條理。
"""

    # 保存到文件
    prompty_file_path = "/home/user/LLM-agent-Demo/20.PromptFlow/simple_chat.prompty"

    try:
        with open(prompty_file_path, 'w', encoding='utf-8') as f:
            f.write(prompty_content)

        print(f"✓ Prompty 文件已創建: {prompty_file_path}")
        print("\n文件內容:")
        print(prompty_content)

        # 展示如何使用這個文件
        print("\n使用方式:")
        print("from promptflow.core import Prompty")
        print("prompty = Prompty.load('simple_chat.prompty')")
        print("result = prompty(question='你的問題')")
        print()

    except Exception as e:
        print(f"創建文件時發生錯誤: {e}")
        print()


# ============================================
# 範例 4: 使用 PFClient 管理流程
# ============================================
def example_4_pf_client():
    """
    展示如何使用 PFClient 管理和執行流程

    PFClient 是 PromptFlow 的主要客戶端，
    用於創建、運行和管理流程。
    """
    print("=" * 50)
    print("範例 4: 使用 PFClient")
    print("=" * 50)

    try:
        from promptflow.client import PFClient

        # 創建客戶端實例
        pf = PFClient()

        print("✓ PFClient 已創建")
        print(f"工作目錄: {pf._client._config.get_connection_provider().conn_provider_path}")

        # 列出可用的連接（如果有）
        print("\n可用的操作:")
        print("- pf.run() - 運行流程")
        print("- pf.stream() - 串流查看運行結果")
        print("- pf.test() - 測試流程")
        print("- pf.connections.list() - 列出連接")
        print("- pf.runs.list() - 列出運行記錄")
        print()

    except ImportError as e:
        print(f"導入錯誤: {e}")
        print("請確保已安裝: pip install promptflow")
        print()
    except Exception as e:
        print(f"發生錯誤: {e}")
        print()


# ============================================
# 範例 5: 環境配置檢查
# ============================================
def example_5_check_environment():
    """
    檢查 PromptFlow 環境配置

    這個函數會檢查必要的環境變量和依賴包是否正確配置。
    """
    print("=" * 50)
    print("範例 5: 環境配置檢查")
    print("=" * 50)

    # 檢查環境變量
    required_env_vars = [
        "OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_DEPLOYMENT_NAME"
    ]

    print("環境變量檢查:")
    for var in required_env_vars:
        value = os.getenv(var)
        if value:
            # 隱藏敏感信息
            if "KEY" in var:
                display_value = value[:8] + "..." if len(value) > 8 else "***"
            else:
                display_value = value
            print(f"✓ {var}: {display_value}")
        else:
            print(f"✗ {var}: 未設置")

    print()

    # 檢查依賴包
    print("依賴包檢查:")
    packages = [
        "promptflow",
        "promptflow-tools",
        "promptflow-core",
        "openai",
        "python-dotenv"
    ]

    for package in packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package}: 已安裝")
        except ImportError:
            print(f"✗ {package}: 未安裝")

    print()


# ============================================
# 範例 6: 簡單的數據處理流程
# ============================================
def example_6_simple_data_flow():
    """
    展示一個簡單的數據處理流程

    這個範例展示如何創建一個包含多個步驟的數據處理流程。
    """
    print("=" * 50)
    print("範例 6: 簡單的數據處理流程")
    print("=" * 50)

    from promptflow.tracing import trace

    @trace
    def preprocess_text(text: str) -> str:
        """預處理文本：清理和標準化"""
        # 移除多餘空格
        text = " ".join(text.split())
        # 轉換為小寫
        text = text.lower()
        return text

    @trace
    def extract_keywords(text: str) -> list:
        """提取關鍵字（簡化版）"""
        # 簡單的關鍵字提取（實際應用中可能使用 NLP 工具）
        stopwords = {"的", "是", "在", "和", "與", "或", "a", "an", "the", "is", "in", "and", "or"}
        words = text.split()
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        return list(set(keywords))

    @trace
    def generate_summary(keywords: list) -> str:
        """根據關鍵字生成摘要"""
        if not keywords:
            return "沒有發現關鍵字"
        return f"文本包含 {len(keywords)} 個關鍵字: {', '.join(keywords[:5])}"

    # 執行完整流程
    input_text = "PromptFlow 是一個強大的 LLM 應用開發工具，它可以幫助開發者快速構建和部署 AI 應用。"

    print(f"輸入文本: {input_text}\n")

    # 步驟 1: 預處理
    processed = preprocess_text(input_text)
    print(f"步驟 1 - 預處理: {processed}\n")

    # 步驟 2: 提取關鍵字
    keywords = extract_keywords(processed)
    print(f"步驟 2 - 關鍵字: {keywords}\n")

    # 步驟 3: 生成摘要
    summary = generate_summary(keywords)
    print(f"步驟 3 - 摘要: {summary}\n")

    print("✓ 流程執行完成")
    print()


# ============================================
# 範例 7: 錯誤處理和日誌記錄
# ============================================
def example_7_error_handling():
    """
    展示如何在 PromptFlow 中進行錯誤處理

    良好的錯誤處理對於生產環境至關重要。
    """
    print("=" * 50)
    print("範例 7: 錯誤處理和日誌記錄")
    print("=" * 50)

    from promptflow.tracing import trace
    import logging

    # 配置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    @trace
    def safe_divide(a: float, b: float) -> dict:
        """安全的除法操作，包含錯誤處理"""
        try:
            logger.info(f"執行除法: {a} / {b}")

            if b == 0:
                raise ValueError("除數不能為零")

            result = a / b
            logger.info(f"結果: {result}")

            return {
                "success": True,
                "result": result,
                "error": None
            }

        except Exception as e:
            logger.error(f"錯誤: {str(e)}")

            return {
                "success": False,
                "result": None,
                "error": str(e)
            }

    # 測試正常情況
    print("測試 1: 正常除法")
    result1 = safe_divide(10, 2)
    print(f"結果: {result1}\n")

    # 測試錯誤情況
    print("測試 2: 除以零")
    result2 = safe_divide(10, 0)
    print(f"結果: {result2}\n")

    print("✓ 錯誤處理演示完成")
    print()


# ============================================
# 範例 8: 使用裝飾器創建工具
# ============================================
def example_8_tool_decorator():
    """
    展示如何使用 @tool 裝飾器創建自定義工具

    @tool 裝飾器是 PromptFlow 中創建可重用組件的核心。
    """
    print("=" * 50)
    print("範例 8: 使用 @tool 裝飾器")
    print("=" * 50)

    try:
        from promptflow.core import tool

        @tool
        def word_count(text: str) -> dict:
            """
            計算文本的各種統計信息

            Args:
                text: 輸入文本

            Returns:
                包含統計信息的字典
            """
            words = text.split()
            chars = len(text)
            sentences = text.count('。') + text.count('.') + text.count('!') + text.count('?')

            return {
                "words": len(words),
                "characters": chars,
                "sentences": max(sentences, 1),
                "avg_word_length": round(chars / len(words), 2) if words else 0
            }

        # 測試工具
        test_text = "PromptFlow 讓 LLM 應用開發變得簡單。它提供了豐富的功能。"
        stats = word_count(test_text)

        print(f"測試文本: {test_text}\n")
        print("統計結果:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

        print("\n✓ 工具創建和使用成功")
        print()

    except ImportError:
        print("無法導入 @tool 裝飾器")
        print("這是正常的，因為 @tool 需要完整的 PromptFlow 環境")
        print()


# ============================================
# 主函數
# ============================================
def main():
    """
    運行所有範例
    """
    print("\n")
    print("=" * 50)
    print("PromptFlow 快速開始 - 範例演示")
    print("=" * 50)
    print("\n")

    # 運行所有範例
    example_1_basic_trace()
    example_2_basic_llm_call()
    example_3_create_prompty_file()
    example_4_pf_client()
    example_5_check_environment()
    example_6_simple_data_flow()
    example_7_error_handling()
    example_8_tool_decorator()

    print("=" * 50)
    print("所有範例演示完成！")
    print("=" * 50)
    print("\n下一步:")
    print("1. 查看 02_Flow創建.py 學習如何創建完整的流程")
    print("2. 配置 .env 文件中的 API 密鑰")
    print("3. 嘗試修改範例代碼進行實驗")
    print()


if __name__ == "__main__":
    main()
