"""
Helicone 快速開始指南
====================

本文件展示如何快速開始使用 Helicone AI Gateway。
Helicone 提供了最簡單的集成方式 - 只需一行代碼改動即可開始追蹤和監控您的 AI 應用。

主要內容:
1. 環境設置和配置
2. 一行代碼集成 (推薦方式)
3. 使用 SDK 集成
4. 基本請求追蹤
5. 驗證集成是否成功
6. 多種模型提供商示例

作者: Helicone Team
日期: 2025-12-31
"""

import os
import sys
from typing import Dict, List, Optional
from datetime import datetime
import json
from dotenv import load_dotenv

# 導入所需的庫
try:
    import openai
    from anthropic import Anthropic
    import httpx
except ImportError as e:
    print(f"❌ 缺少必要的依賴庫: {e}")
    print("請運行: pip install -r requirements.txt")
    sys.exit(1)


class HeliconeQuickStart:
    """
    Helicone 快速開始類

    這個類展示了使用 Helicone 的多種方式,從最簡單的一行集成
    到更高級的配置選項。
    """

    def __init__(self):
        """
        初始化 Helicone 快速開始環境

        主要步驟:
        1. 加載環境變量
        2. 驗證必要的 API 密鑰
        3. 設置 Helicone 配置
        """
        # 加載 .env 文件中的環境變量
        load_dotenv()

        # 獲取必要的 API 密鑰
        self.helicone_api_key = os.getenv("HELICONE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        # Helicone 代理 URL
        # 這是 Helicone 的核心 - 它作為您和 AI 提供商之間的代理
        self.helicone_base_url = "https://oai.helicone.ai/v1"
        self.helicone_anthropic_url = "https://anthropic.helicone.ai"

        # 驗證配置
        self._validate_configuration()

        print("✅ Helicone 快速開始環境已初始化")
        print(f"📅 時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 80)

    def _validate_configuration(self):
        """
        驗證必要的配置是否已設置

        這是一個重要的步驟,確保所有必要的 API 密鑰都已配置。
        如果缺少任何密鑰,將提供清晰的錯誤信息。
        """
        missing_keys = []

        if not self.helicone_api_key:
            missing_keys.append("HELICONE_API_KEY")
        if not self.openai_api_key:
            missing_keys.append("OPENAI_API_KEY")

        if missing_keys:
            print("❌ 缺少必要的環境變量:")
            for key in missing_keys:
                print(f"   - {key}")
            print("\n請在 .env 文件中設置這些變量,或使用以下命令:")
            for key in missing_keys:
                print(f"   export {key}='your-api-key-here'")
            sys.exit(1)

    def method_1_one_line_integration(self):
        """
        方法 1: 一行代碼集成 (最推薦的方式)

        這是使用 Helicone 最簡單的方法。您只需要:
        1. 將 base_url 指向 Helicone 代理
        2. 在 headers 中添加您的 Helicone API 密鑰

        優點:
        - 最少的代碼改動
        - 不需要額外的 SDK
        - 與現有代碼完全兼容
        """
        print("\n" + "="*80)
        print("方法 1: 一行代碼集成 (One-Line Integration)")
        print("="*80)

        try:
            # 創建 OpenAI 客戶端,但指向 Helicone 代理
            # 這是唯一需要改動的地方!
            client = openai.OpenAI(
                api_key=self.openai_api_key,
                base_url=self.helicone_base_url,  # ← 改動 1: 使用 Helicone URL
                default_headers={
                    # ← 改動 2: 添加 Helicone 認證
                    "Helicone-Auth": f"Bearer {self.helicone_api_key}"
                }
            )

            print("\n📝 發送測試請求到 GPT-3.5-Turbo...")

            # 現在正常使用 OpenAI API
            # Helicone 會自動追蹤這個請求
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一個有幫助的AI助手。"
                    },
                    {
                        "role": "user",
                        "content": "用一句話解釋什麼是 Helicone。"
                    }
                ],
                max_tokens=100,
                temperature=0.7
            )

            # 顯示響應
            print("\n✅ 請求成功!")
            print(f"模型: {response.model}")
            print(f"回應: {response.choices[0].message.content}")
            print(f"使用 tokens: {response.usage.total_tokens}")

            # 計算成本 (GPT-3.5-Turbo 定價)
            input_cost = response.usage.prompt_tokens * 0.0005 / 1000
            output_cost = response.usage.completion_tokens * 0.0015 / 1000
            total_cost = input_cost + output_cost

            print(f"\n💰 成本估算:")
            print(f"   輸入: ${input_cost:.6f}")
            print(f"   輸出: ${output_cost:.6f}")
            print(f"   總計: ${total_cost:.6f}")

            print("\n📊 這個請求已經被 Helicone 追蹤!")
            print("   前往 https://helicone.ai/dashboard 查看詳細信息")

            return response

        except Exception as e:
            print(f"\n❌ 錯誤: {str(e)}")
            return None

    def method_2_with_custom_headers(self):
        """
        方法 2: 使用自定義 Headers 進行更詳細的追蹤

        除了基本集成,Helicone 還支持大量的自定義 headers
        來提供更豐富的追蹤和分析功能。

        常用的 headers:
        - Helicone-User-Id: 追蹤特定用戶
        - Helicone-Session-Id: 追蹤對話會話
        - Helicone-Property-*: 自定義屬性
        - Helicone-Cache-Enabled: 啟用快取
        """
        print("\n" + "="*80)
        print("方法 2: 使用自定義 Headers 進行詳細追蹤")
        print("="*80)

        try:
            # 創建客戶端
            client = openai.OpenAI(
                api_key=self.openai_api_key,
                base_url=self.helicone_base_url,
                default_headers={
                    "Helicone-Auth": f"Bearer {self.helicone_api_key}"
                }
            )

            print("\n📝 發送帶有自定義 headers 的請求...")

            # 發送請求,包含豐富的追蹤信息
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "user",
                        "content": "寫一個簡短的產品描述,關於 AI 監控工具。"
                    }
                ],
                extra_headers={
                    # 用戶標識 - 用於追蹤特定用戶的使用情況
                    "Helicone-User-Id": "user_12345",

                    # 會話標識 - 用於追蹤整個對話
                    "Helicone-Session-Id": "session_abc_" + datetime.now().strftime("%Y%m%d_%H%M%S"),

                    # 自定義屬性 - 可以添加任何您需要的元數據
                    "Helicone-Property-Environment": "development",
                    "Helicone-Property-Feature": "product-description",
                    "Helicone-Property-Version": "v1.0",
                    "Helicone-Property-Team": "marketing",

                    # 啟用快取 - 相同的請求會從快取返回
                    "Helicone-Cache-Enabled": "true",

                    # 提示詞 ID - 用於版本控制和 A/B 測試
                    "Helicone-Prompt-Id": "product-description-prompt-v1"
                }
            )

            print("\n✅ 請求成功!")
            print(f"模型: {response.model}")
            print(f"回應長度: {len(response.choices[0].message.content)} 字符")
            print(f"\n生成的產品描述:")
            print("-" * 40)
            print(response.choices[0].message.content)
            print("-" * 40)

            print("\n📊 追蹤信息:")
            print("   用戶 ID: user_12345")
            print("   功能: product-description")
            print("   團隊: marketing")
            print("   快取: 已啟用")

            return response

        except Exception as e:
            print(f"\n❌ 錯誤: {str(e)}")
            return None

    def method_3_anthropic_claude(self):
        """
        方法 3: 使用 Anthropic Claude 模型

        Helicone 不僅支持 OpenAI,也支持其他主流 AI 提供商。
        這個示例展示如何使用 Claude 模型。
        """
        print("\n" + "="*80)
        print("方法 3: 使用 Anthropic Claude 模型")
        print("="*80)

        if not self.anthropic_api_key:
            print("\n⚠️  未設置 ANTHROPIC_API_KEY,跳過此示例")
            return None

        try:
            # 創建 Anthropic 客戶端,指向 Helicone 代理
            client = Anthropic(
                api_key=self.anthropic_api_key,
                base_url=self.helicone_anthropic_url,
                default_headers={
                    "Helicone-Auth": f"Bearer {self.helicone_api_key}",
                    "Helicone-User-Id": "claude_user_001",
                    "Helicone-Property-Model-Type": "claude"
                }
            )

            print("\n📝 發送請求到 Claude 3.5 Sonnet...")

            # 使用 Claude API
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                messages=[
                    {
                        "role": "user",
                        "content": "簡要說明 AI Gateway 的三個主要優勢。"
                    }
                ]
            )

            print("\n✅ 請求成功!")
            print(f"模型: {message.model}")
            print(f"回應:")
            print("-" * 40)
            print(message.content[0].text)
            print("-" * 40)

            print(f"\n使用 tokens:")
            print(f"   輸入: {message.usage.input_tokens}")
            print(f"   輸出: {message.usage.output_tokens}")

            return message

        except Exception as e:
            print(f"\n❌ 錯誤: {str(e)}")
            return None

    def method_4_streaming_response(self):
        """
        方法 4: 流式響應 (Streaming)

        Helicone 完全支持流式響應,這對於實時應用非常重要。
        流式響應可以讓用戶更快地看到結果。
        """
        print("\n" + "="*80)
        print("方法 4: 流式響應 (Streaming)")
        print("="*80)

        try:
            client = openai.OpenAI(
                api_key=self.openai_api_key,
                base_url=self.helicone_base_url,
                default_headers={
                    "Helicone-Auth": f"Bearer {self.helicone_api_key}",
                    "Helicone-Stream-Force-Format": "true"
                }
            )

            print("\n📝 發送流式請求...")
            print("回應: ", end="", flush=True)

            # 啟用 stream=True
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": "用三個句子描述機器學習。"
                    }
                ],
                stream=True,  # 啟用流式響應
                extra_headers={
                    "Helicone-Property-Request-Type": "streaming"
                }
            )

            # 實時顯示響應
            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content

            print("\n" + "-" * 40)
            print("\n✅ 流式響應完成!")
            print(f"總長度: {len(full_response)} 字符")

            print("\n💡 注意: Helicone 也會追蹤流式請求!")

            return full_response

        except Exception as e:
            print(f"\n❌ 錯誤: {str(e)}")
            return None

    def verify_integration(self):
        """
        驗證 Helicone 集成是否正常工作

        這個方法執行一系列測試來確保:
        1. API 密鑰正確
        2. 網絡連接正常
        3. Helicone 服務可訪問
        4. 請求被正確追蹤
        """
        print("\n" + "="*80)
        print("驗證 Helicone 集成")
        print("="*80)

        checks = {
            "API 密鑰配置": False,
            "網絡連接": False,
            "Helicone 服務": False,
            "請求追蹤": False
        }

        # 檢查 1: API 密鑰
        print("\n🔍 檢查 1: API 密鑰配置...")
        if self.helicone_api_key and self.openai_api_key:
            checks["API 密鑰配置"] = True
            print("   ✅ API 密鑰已配置")
        else:
            print("   ❌ API 密鑰缺失")

        # 檢查 2: 網絡連接
        print("\n🔍 檢查 2: 網絡連接...")
        try:
            response = httpx.get("https://helicone.ai", timeout=10)
            if response.status_code == 200:
                checks["網絡連接"] = True
                print("   ✅ 網絡連接正常")
            else:
                print(f"   ⚠️  狀態碼: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 網絡錯誤: {str(e)}")

        # 檢查 3: Helicone 服務
        print("\n🔍 檢查 3: Helicone 服務...")
        try:
            client = openai.OpenAI(
                api_key=self.openai_api_key,
                base_url=self.helicone_base_url,
                default_headers={
                    "Helicone-Auth": f"Bearer {self.helicone_api_key}"
                }
            )
            checks["Helicone 服務"] = True
            print("   ✅ Helicone 客戶端創建成功")
        except Exception as e:
            print(f"   ❌ 客戶端錯誤: {str(e)}")

        # 檢查 4: 請求追蹤
        print("\n🔍 檢查 4: 發送測試請求...")
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5
            )
            checks["請求追蹤"] = True
            print("   ✅ 測試請求成功")
            print(f"   回應: {response.choices[0].message.content}")
        except Exception as e:
            print(f"   ❌ 請求錯誤: {str(e)}")

        # 總結
        print("\n" + "="*80)
        print("驗證結果總結")
        print("="*80)

        all_passed = all(checks.values())
        for check_name, status in checks.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {check_name}")

        if all_passed:
            print("\n🎉 所有檢查通過! Helicone 已正確集成。")
            print("📊 前往 https://helicone.ai/dashboard 查看您的請求")
        else:
            print("\n⚠️  部分檢查失敗,請檢查配置。")

        return all_passed


def main():
    """
    主函數 - 執行所有示例

    這個函數會運行所有的集成方法,展示 Helicone 的各種用法。
    """
    print("🚀 Helicone 快速開始指南")
    print("=" * 80)

    # 初始化
    quickstart = HeliconeQuickStart()

    # 執行所有示例
    try:
        # 方法 1: 一行集成
        quickstart.method_1_one_line_integration()

        # 方法 2: 自定義 Headers
        quickstart.method_2_with_custom_headers()

        # 方法 3: Claude 模型
        quickstart.method_3_anthropic_claude()

        # 方法 4: 流式響應
        quickstart.method_4_streaming_response()

        # 驗證集成
        quickstart.verify_integration()

    except KeyboardInterrupt:
        print("\n\n⚠️  用戶中斷程序")
    except Exception as e:
        print(f"\n❌ 發生錯誤: {str(e)}")

    print("\n" + "="*80)
    print("✅ 快速開始指南完成!")
    print("📚 查看其他示例文件以了解更多高級功能")
    print("="*80)


if __name__ == "__main__":
    main()
