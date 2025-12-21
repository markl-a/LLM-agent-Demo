"""
LiteLLM 快速開始範例
===================

這個範例展示了 LiteLLM 的基礎使用方式，包括：
1. 基本的模型調用
2. 不同提供商的使用
3. 訊息格式處理
4. 回應內容提取

LiteLLM 提供統一的 API 介面，讓您可以使用相同的代碼調用不同的 LLM 提供商。
"""

import os
from litellm import completion
import litellm

# 設定是否顯示詳細日誌（對除錯很有幫助）
litellm.set_verbose = True  # 設為 True 可看到詳細的請求日誌


def basic_completion():
    """最基本的 completion 調用範例"""
    print("=" * 60)
    print("範例 1: 基本的 Completion 調用")
    print("=" * 60)

    # 確保設定了 OpenAI API 金鑰
    # os.environ["OPENAI_API_KEY"] = "your-api-key-here"

    try:
        response = completion(
            model="gpt-3.5-turbo",  # 模型名稱
            messages=[
                {"role": "user", "content": "用一句話解釋什麼是 LiteLLM"}
            ]
        )

        # 提取回應內容
        print(f"回應: {response.choices[0].message.content}")
        print(f"模型: {response.model}")
        print(f"Token 使用: {response.usage}")

    except Exception as e:
        print(f"錯誤: {e}")


def multiple_messages():
    """使用多輪對話的範例"""
    print("\n" + "=" * 60)
    print("範例 2: 多輪對話")
    print("=" * 60)

    try:
        messages = [
            {"role": "system", "content": "你是一個專業的 Python 程式設計助手"},
            {"role": "user", "content": "什麼是裝飾器？"},
            {"role": "assistant", "content": "裝飾器是 Python 中修改函數行為的特殊語法"},
            {"role": "user", "content": "給我一個簡單的例子"}
        ]

        response = completion(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7  # 控制回應的隨機性 (0-2)
        )

        print(f"回應: {response.choices[0].message.content}")

    except Exception as e:
        print(f"錯誤: {e}")


def different_providers():
    """使用不同提供商的範例"""
    print("\n" + "=" * 60)
    print("範例 3: 使用不同的 LLM 提供商")
    print("=" * 60)

    # LiteLLM 支援多種提供商，格式為 "provider/model"
    providers = [
        "gpt-3.5-turbo",  # OpenAI (預設)
        # "claude-3-sonnet-20240229",  # Anthropic Claude
        # "command-nightly",  # Cohere
        # "gemini-pro",  # Google Gemini
    ]

    message = "Hello! Respond in one sentence."

    for model in providers:
        try:
            print(f"\n使用模型: {model}")
            response = completion(
                model=model,
                messages=[{"role": "user", "content": message}]
            )
            print(f"回應: {response.choices[0].message.content}")

        except Exception as e:
            print(f"錯誤 ({model}): {e}")


def with_parameters():
    """使用各種參數的範例"""
    print("\n" + "=" * 60)
    print("範例 4: 使用不同的參數控制回應")
    print("=" * 60)

    try:
        response = completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "寫一個關於 AI 的俳句"}],

            # 常用參數
            temperature=0.9,      # 創意度 (0-2)，越高越有創意
            max_tokens=100,       # 最大回應 token 數
            top_p=1,              # 核心採樣參數 (0-1)
            frequency_penalty=0,  # 頻率懲罰 (-2 to 2)
            presence_penalty=0,   # 存在懲罰 (-2 to 2)
            n=1,                  # 生成多少個回應
        )

        print(f"回應: {response.choices[0].message.content}")
        print(f"\n使用的 Token:")
        print(f"  - 提示 (Prompt): {response.usage.prompt_tokens}")
        print(f"  - 完成 (Completion): {response.usage.completion_tokens}")
        print(f"  - 總計: {response.usage.total_tokens}")

    except Exception as e:
        print(f"錯誤: {e}")


def azure_openai_example():
    """使用 Azure OpenAI 的範例"""
    print("\n" + "=" * 60)
    print("範例 5: 使用 Azure OpenAI")
    print("=" * 60)

    # 需要設定以下環境變數：
    # os.environ["AZURE_API_KEY"] = "your-azure-api-key"
    # os.environ["AZURE_API_BASE"] = "https://your-endpoint.openai.azure.com/"
    # os.environ["AZURE_API_VERSION"] = "2024-02-15-preview"

    try:
        response = completion(
            model="azure/your-deployment-name",  # Azure 部署名稱
            messages=[{"role": "user", "content": "Hello from Azure!"}],
            # 可選：在這裡直接提供 Azure 配置
            # api_key="your-azure-api-key",
            # api_base="https://your-endpoint.openai.azure.com/",
            # api_version="2024-02-15-preview"
        )

        print(f"回應: {response.choices[0].message.content}")

    except Exception as e:
        print(f"注意: 此範例需要 Azure OpenAI 配置")
        print(f"錯誤: {e}")


def anthropic_example():
    """使用 Anthropic Claude 的範例"""
    print("\n" + "=" * 60)
    print("範例 6: 使用 Anthropic Claude")
    print("=" * 60)

    # 需要設定環境變數：
    # os.environ["ANTHROPIC_API_KEY"] = "your-anthropic-api-key"

    try:
        response = completion(
            model="claude-3-5-sonnet-20241022",  # Claude 3.5 Sonnet
            messages=[{"role": "user", "content": "用繁體中文介紹你自己"}],
            max_tokens=200  # Claude 需要明確指定 max_tokens
        )

        print(f"回應: {response.choices[0].message.content}")

    except Exception as e:
        print(f"注意: 此範例需要 Anthropic API 金鑰")
        print(f"錯誤: {e}")


def response_format_example():
    """使用結構化輸出的範例"""
    print("\n" + "=" * 60)
    print("範例 7: 結構化輸出 (JSON mode)")
    print("=" * 60)

    try:
        response = completion(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "你是一個有幫助的助手，以 JSON 格式回應"},
                {"role": "user", "content": "給我 3 個 Python 學習資源，包含名稱和 URL"}
            ],
            response_format={"type": "json_object"}  # 要求 JSON 格式輸出
        )

        print(f"JSON 回應:\n{response.choices[0].message.content}")

    except Exception as e:
        print(f"注意: JSON mode 需要支援的模型（如 gpt-4-turbo）")
        print(f"錯誤: {e}")


def custom_api_base():
    """使用自定義 API 端點的範例（如本地模型）"""
    print("\n" + "=" * 60)
    print("範例 8: 使用自定義 API 端點")
    print("=" * 60)

    try:
        # 例如：使用 Ollama 本地模型
        response = completion(
            model="ollama/llama2",  # Ollama 模型
            messages=[{"role": "user", "content": "Hello!"}],
            api_base="http://localhost:11434"  # Ollama 預設端點
        )

        print(f"回應: {response.choices[0].message.content}")

    except Exception as e:
        print(f"注意: 此範例需要本地運行 Ollama")
        print(f"錯誤: {e}")


def main():
    """主函數：運行所有範例"""
    print("\n" + "=" * 60)
    print("LiteLLM 快速開始範例")
    print("=" * 60)
    print("\n請確保已設定相關的 API 金鑰環境變數：")
    print("- OPENAI_API_KEY")
    print("- ANTHROPIC_API_KEY (可選)")
    print("- AZURE_API_KEY (可選)")
    print("\n" + "=" * 60 + "\n")

    # 運行各個範例
    basic_completion()
    multiple_messages()
    different_providers()
    with_parameters()
    azure_openai_example()
    anthropic_example()
    response_format_example()
    custom_api_base()

    print("\n" + "=" * 60)
    print("所有範例執行完畢！")
    print("=" * 60)


if __name__ == "__main__":
    # 提示：取消註解以下行來設定您的 API 金鑰
    # os.environ["OPENAI_API_KEY"] = "your-api-key-here"

    main()
