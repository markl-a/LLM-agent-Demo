"""
Google ADK - 快速開始範例

這個範例展示如何快速創建和使用 Google ADK Agent。
包含基礎的 Agent 初始化、配置和簡單的對話功能。
"""

import os
from typing import Optional
import google.generativeai as genai
from google_adk import Agent
from google_adk.models import GeminiPro


class QuickStartExample:
    """快速開始範例類"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化範例

        Args:
            api_key: Google API 密鑰，如果不提供則從環境變量讀取
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("請設置 GOOGLE_API_KEY 環境變量")

        # 配置 Gemini API
        genai.configure(api_key=self.api_key)

    def example_1_basic_agent(self):
        """範例 1: 創建基礎 Agent"""
        print("\n" + "="*60)
        print("範例 1: 創建基礎 Agent")
        print("="*60)

        # 創建一個簡單的 Agent
        agent = Agent(
            model=GeminiPro(),
            name="hello-agent",
            instructions="你是一個友好且專業的 AI 助手，使用繁體中文回答問題。"
        )

        # 運行 Agent
        prompt = "你好！請簡單介紹一下你自己。"
        print(f"\n用戶: {prompt}")

        response = agent.run(prompt)
        print(f"Agent: {response.content}")

        return agent

    def example_2_custom_parameters(self):
        """範例 2: 自定義參數配置"""
        print("\n" + "="*60)
        print("範例 2: 自定義參數配置")
        print("="*60)

        # 創建具有自定義參數的 Agent
        agent = Agent(
            model=GeminiPro(
                temperature=0.9,      # 提高創造性
                top_p=0.95,          # Top-p 採樣
                top_k=40,            # Top-k 採樣
                max_output_tokens=1024  # 最大輸出 token 數
            ),
            name="creative-agent",
            instructions="你是一個富有創意的故事創作者，擅長編寫有趣的短故事。"
        )

        prompt = "請創作一個關於 AI 機器人學習人類情感的 100 字短故事。"
        print(f"\n用戶: {prompt}")

        response = agent.run(prompt)
        print(f"Agent: {response.content}")

        return agent

    def example_3_multi_turn_conversation(self):
        """範例 3: 多輪對話"""
        print("\n" + "="*60)
        print("範例 3: 多輪對話")
        print("="*60)

        # 創建支持上下文的 Agent
        agent = Agent(
            model=GeminiPro(),
            name="context-agent",
            instructions="你是一個記性很好的助手，能記住對話中的所有細節。"
        )

        # 第一輪對話
        prompt1 = "我叫小明，今年 25 歲，喜歡打籃球。"
        print(f"\n用戶: {prompt1}")
        response1 = agent.run(prompt1)
        print(f"Agent: {response1.content}")

        # 第二輪對話（測試記憶）
        prompt2 = "請告訴我，我叫什麼名字？我喜歡什麼運動？"
        print(f"\n用戶: {prompt2}")
        response2 = agent.run(prompt2)
        print(f"Agent: {response2.content}")

        return agent

    def example_4_system_instructions(self):
        """範例 4: 角色設定和系統指令"""
        print("\n" + "="*60)
        print("範例 4: 角色設定和系統指令")
        print("="*60)

        # 創建具有特定角色的 Agent
        agent = Agent(
            model=GeminiPro(),
            name="teacher-agent",
            instructions="""
            你是一位經驗豐富的程式設計教師，具有以下特點：
            1. 擅長用簡單的比喻解釋複雜概念
            2. 總是提供實際的代碼範例
            3. 鼓勵學生思考和提問
            4. 使用循序漸進的教學方式
            5. 回答時保持耐心和友善
            """
        )

        prompt = "請解釋什麼是遞迴（Recursion）？"
        print(f"\n學生: {prompt}")

        response = agent.run(prompt)
        print(f"老師: {response.content}")

        return agent

    def example_5_error_handling(self):
        """範例 5: 錯誤處理"""
        print("\n" + "="*60)
        print("範例 5: 錯誤處理")
        print("="*60)

        try:
            # 創建 Agent
            agent = Agent(
                model=GeminiPro(),
                name="error-handling-agent"
            )

            # 正常請求
            response = agent.run("測試正常請求")
            print(f"成功: {response.content[:50]}...")

        except Exception as e:
            print(f"錯誤: {type(e).__name__}: {str(e)}")

        # 處理空輸入
        try:
            agent = Agent(model=GeminiPro())
            response = agent.run("")
            print(f"空輸入響應: {response.content}")
        except ValueError as e:
            print(f"空輸入錯誤: {e}")

    def example_6_response_metadata(self):
        """範例 6: 響應元數據"""
        print("\n" + "="*60)
        print("範例 6: 響應元數據")
        print("="*60)

        agent = Agent(
            model=GeminiPro(),
            name="metadata-agent"
        )

        prompt = "請用一句話解釋量子計算。"
        print(f"\n用戶: {prompt}")

        response = agent.run(prompt)

        # 顯示響應內容
        print(f"\nAgent 響應: {response.content}")

        # 顯示元數據
        print(f"\n元數據:")
        print(f"  - 使用的模型: {response.model_name}")
        print(f"  - Token 使用: {response.token_count}")
        print(f"  - 完成原因: {response.finish_reason}")
        print(f"  - 安全評級: {response.safety_ratings}")

        return response

    def example_7_safety_settings(self):
        """範例 7: 安全設置"""
        print("\n" + "="*60)
        print("範例 7: 安全設置")
        print("="*60)

        from google.generativeai.types import HarmCategory, HarmBlockThreshold

        # 配置安全設置
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }

        agent = Agent(
            model=GeminiPro(safety_settings=safety_settings),
            name="safe-agent"
        )

        prompt = "請介紹一些健康的生活習慣。"
        print(f"\n用戶: {prompt}")

        response = agent.run(prompt)
        print(f"Agent: {response.content}")

        return agent


def main():
    """主函數"""
    print("="*60)
    print("Google ADK 快速開始範例")
    print("="*60)

    # 檢查 API 密鑰
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n⚠️  請先設置 GOOGLE_API_KEY 環境變量")
        print("export GOOGLE_API_KEY='your-api-key-here'")
        return

    # 創建範例實例
    example = QuickStartExample()

    try:
        # 運行所有範例
        example.example_1_basic_agent()
        example.example_2_custom_parameters()
        example.example_3_multi_turn_conversation()
        example.example_4_system_instructions()
        example.example_5_error_handling()
        example.example_6_response_metadata()
        example.example_7_safety_settings()

        print("\n" + "="*60)
        print("所有範例執行完成！")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 執行錯誤: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
