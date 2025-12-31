"""
Google ADK - Gemini 整合範例

這個範例展示如何深度整合 Gemini 模型的各種功能：
- Gemini Pro 文本生成
- Gemini Pro Vision 多模態能力
- 模型參數調優
- 批次處理
- 流式輸出
"""

import os
import base64
from typing import List, Optional, Dict, Any
import google.generativeai as genai
from google_adk import Agent
from google_adk.models import GeminiPro, GeminiProVision


class GeminiIntegrationExample:
    """Gemini 整合範例類"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化 Gemini 整合範例"""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("請設置 GOOGLE_API_KEY 環境變量")

        genai.configure(api_key=self.api_key)

    def example_1_gemini_pro_basic(self):
        """範例 1: Gemini Pro 基礎使用"""
        print("\n" + "="*60)
        print("範例 1: Gemini Pro 基礎使用")
        print("="*60)

        # 創建 Gemini Pro Agent
        agent = Agent(
            model=GeminiPro(),
            name="gemini-pro-agent",
            instructions="你是一個專業的技術顧問，提供準確且詳細的技術建議。"
        )

        # 技術問題諮詢
        prompt = "請解釋什麼是微服務架構，以及它的主要優缺點？"
        print(f"\n問題: {prompt}")

        response = agent.run(prompt)
        print(f"\n回答: {response.content}")

        return agent

    def example_2_parameter_tuning(self):
        """範例 2: 模型參數調優"""
        print("\n" + "="*60)
        print("範例 2: 模型參數調優")
        print("="*60)

        # 測試不同的 temperature 設置
        temperatures = [0.0, 0.5, 1.0]
        prompt = "請用一句話描述人工智能。"

        for temp in temperatures:
            print(f"\n--- Temperature = {temp} ---")
            agent = Agent(
                model=GeminiPro(
                    temperature=temp,
                    top_p=0.95,
                    top_k=40
                ),
                name=f"gemini-temp-{temp}"
            )

            response = agent.run(prompt)
            print(f"回答: {response.content}")

    def example_3_advanced_generation(self):
        """範例 3: 高級生成配置"""
        print("\n" + "="*60)
        print("範例 3: 高級生成配置")
        print("="*60)

        # 配置詳細的生成參數
        agent = Agent(
            model=GeminiPro(
                temperature=0.7,
                top_p=0.9,
                top_k=40,
                max_output_tokens=2048,
                candidate_count=1,  # 生成候選數
                stop_sequences=["\n\n\n"]  # 停止序列
            ),
            name="advanced-gemini"
        )

        prompt = """
        請撰寫一個 Python 函數，實現快速排序算法。
        要求：
        1. 包含詳細的註釋
        2. 處理邊界情況
        3. 時間複雜度分析
        """

        print(f"需求: {prompt}")
        response = agent.run(prompt)
        print(f"\n生成的代碼:\n{response.content}")

        return agent

    def example_4_gemini_pro_vision(self):
        """範例 4: Gemini Pro Vision 圖像理解"""
        print("\n" + "="*60)
        print("範例 4: Gemini Pro Vision 圖像理解")
        print("="*60)

        # 創建 Vision Agent
        agent = Agent(
            model=GeminiProVision(),
            name="vision-agent",
            instructions="你是一個專業的圖像分析專家。"
        )

        # 模擬圖像數據（實際使用時應該是真實圖像）
        print("注意: 這個範例展示了如何處理圖像，實際使用時需要提供真實圖像文件")

        # 圖像理解提示
        prompt = """
        請分析這張圖片並回答：
        1. 圖片中有什麼主要物體？
        2. 圖片的整體色調如何？
        3. 這張圖片可能用於什麼場景？
        """

        print(f"\n分析需求: {prompt}")
        print("（需要實際圖像數據）")

        # 實際使用範例（需要圖像文件）
        """
        from PIL import Image

        image = Image.open("example.jpg")
        response = agent.run(
            prompt=prompt,
            images=[image]
        )
        print(f"分析結果: {response.content}")
        """

        return agent

    def example_5_multimodal_input(self):
        """範例 5: 多模態輸入處理"""
        print("\n" + "="*60)
        print("範例 5: 多模態輸入處理")
        print("="*60)

        agent = Agent(
            model=GeminiProVision(),
            name="multimodal-agent"
        )

        print("多模態輸入範例:")
        print("1. 文本 + 圖像: 圖像描述和問答")
        print("2. 文本 + 多張圖像: 圖像比較分析")
        print("3. 複雜場景理解")

        # 範例代碼結構
        example_code = """
        # 單圖像分析
        response = agent.run(
            prompt="描述這張圖片",
            images=[image1]
        )

        # 多圖像比較
        response = agent.run(
            prompt="比較這兩張圖片的異同",
            images=[image1, image2]
        )

        # 圖像中的文字識別
        response = agent.run(
            prompt="提取圖片中的所有文字",
            images=[document_image]
        )
        """

        print(f"\n使用範例:\n{example_code}")

    def example_6_batch_processing(self):
        """範例 6: 批次處理"""
        print("\n" + "="*60)
        print("範例 6: 批次處理")
        print("="*60)

        agent = Agent(
            model=GeminiPro(),
            name="batch-agent"
        )

        # 準備多個任務
        tasks = [
            "什麼是深度學習？",
            "解釋神經網絡的工作原理。",
            "介紹常見的優化算法。",
            "什麼是遷移學習？"
        ]

        print("批次處理任務:")
        results = []

        for i, task in enumerate(tasks, 1):
            print(f"\n任務 {i}: {task}")
            response = agent.run(task)
            results.append({
                "task": task,
                "response": response.content[:100] + "..."  # 截取前100字符
            })
            print(f"完成 ✓")

        print(f"\n共處理 {len(results)} 個任務")
        return results

    def example_7_streaming_response(self):
        """範例 7: 流式響應"""
        print("\n" + "="*60)
        print("範例 7: 流式響應")
        print("="*60)

        # 配置流式輸出
        agent = Agent(
            model=GeminiPro(),
            name="streaming-agent",
            stream=True  # 啟用流式輸出
        )

        prompt = "請詳細解釋區塊鏈技術的工作原理。"
        print(f"\n問題: {prompt}\n")
        print("流式回答: ", end="", flush=True)

        # 模擬流式輸出
        response = agent.run(prompt)

        # 在實際的 streaming 實現中
        """
        for chunk in agent.stream(prompt):
            print(chunk.content, end="", flush=True)
        print()
        """

        print(response.content)

    def example_8_context_caching(self):
        """範例 8: 上下文緩存"""
        print("\n" + "="*60)
        print("範例 8: 上下文緩存")
        print("="*60)

        # 配置緩存
        agent = Agent(
            model=GeminiPro(),
            name="cached-agent",
            cache_enabled=True,
            cache_ttl=3600  # 緩存 1 小時
        )

        # 第一次請求（未緩存）
        prompt = "請詳細介紹 Python 的 asyncio 庫。"
        print(f"\n第一次請求: {prompt}")
        response1 = agent.run(prompt)
        print(f"響應長度: {len(response1.content)} 字符")
        print(f"是否來自緩存: False")

        # 第二次相同請求（應該來自緩存）
        print(f"\n第二次相同請求: {prompt}")
        response2 = agent.run(prompt)
        print(f"響應長度: {len(response2.content)} 字符")
        print(f"是否來自緩存: True (模擬)")

    def example_9_token_counting(self):
        """範例 9: Token 計數和優化"""
        print("\n" + "="*60)
        print("範例 9: Token 計數和優化")
        print("="*60)

        agent = Agent(
            model=GeminiPro(),
            name="token-counter"
        )

        # 測試不同長度的輸入
        test_prompts = [
            "你好",
            "請簡單介紹一下 Python",
            "請詳細解釋機器學習的主要算法，包括監督學習、非監督學習和強化學習的區別。"
        ]

        print("Token 使用分析:")
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n提示 {i}: {prompt[:50]}...")
            response = agent.run(prompt)

            # 顯示 token 統計
            print(f"  輸入 tokens: ~{len(prompt.split())}")
            print(f"  輸出 tokens: ~{len(response.content.split())}")
            print(f"  總計: ~{len(prompt.split()) + len(response.content.split())}")

    def example_10_model_comparison(self):
        """範例 10: 模型比較"""
        print("\n" + "="*60)
        print("範例 10: 不同配置的模型比較")
        print("="*60)

        prompt = "用一段話介紹量子計算。"

        # 配置 1: 保守模式（低 temperature）
        conservative_agent = Agent(
            model=GeminiPro(temperature=0.1),
            name="conservative-model"
        )

        # 配置 2: 平衡模式
        balanced_agent = Agent(
            model=GeminiPro(temperature=0.7),
            name="balanced-model"
        )

        # 配置 3: 創意模式（高 temperature）
        creative_agent = Agent(
            model=GeminiPro(temperature=1.5),
            name="creative-model"
        )

        print(f"測試提示: {prompt}\n")

        print("--- 保守模式 (temperature=0.1) ---")
        response1 = conservative_agent.run(prompt)
        print(response1.content)

        print("\n--- 平衡模式 (temperature=0.7) ---")
        response2 = balanced_agent.run(prompt)
        print(response2.content)

        print("\n--- 創意模式 (temperature=1.5) ---")
        response3 = creative_agent.run(prompt)
        print(response3.content)


def main():
    """主函數"""
    print("="*60)
    print("Google ADK - Gemini 整合範例")
    print("="*60)

    # 檢查 API 密鑰
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n⚠️  請先設置 GOOGLE_API_KEY 環境變量")
        print("export GOOGLE_API_KEY='your-api-key-here'")
        return

    # 創建範例實例
    example = GeminiIntegrationExample()

    try:
        # 運行所有範例
        example.example_1_gemini_pro_basic()
        example.example_2_parameter_tuning()
        example.example_3_advanced_generation()
        example.example_4_gemini_pro_vision()
        example.example_5_multimodal_input()
        example.example_6_batch_processing()
        example.example_7_streaming_response()
        example.example_8_context_caching()
        example.example_9_token_counting()
        example.example_10_model_comparison()

        print("\n" + "="*60)
        print("所有 Gemini 整合範例執行完成！")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 執行錯誤: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
