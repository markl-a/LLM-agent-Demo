"""
範例 11: LLM 基礎使用

功能：
1. 連接 LLM API
2. 執行基本的文字生成
3. 結構化輸出示例

學習要點：
- LLM API 調用
- 異步編程基礎
- 錯誤處理

執行：python 11_llm_basic.py

前置準備：
1. 設置環境變數 OPENAI_API_KEY 或修改 .env 文件
2. pip install openai python-dotenv
"""

import asyncio
import json
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

async def example_1_basic_generation():
    """範例 1: 基礎文字生成"""
    print("\n" + "=" * 60)
    print("範例 1: 基礎文字生成")
    print("=" * 60)

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        print("\n提問: 什麼是 RPA？請用一句話解釋。")

        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "什麼是 RPA？請用一句話解釋。"}
            ],
            temperature=0.7,
            max_tokens=100
        )

        answer = response.choices[0].message.content
        print(f"\nLLM 回答: {answer}")

    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")
        print("請確認 OPENAI_API_KEY 已正確設置")

async def example_2_structured_output():
    """範例 2: 結構化輸出"""
    print("\n" + "=" * 60)
    print("範例 2: 結構化輸出（JSON）")
    print("=" * 60)

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        prompt = """
從這段文字中提取產品資訊：

"蘋果 iPhone 15 Pro，售價 $999，顏色：太空黑，儲存容量：256GB"

以 JSON 格式返回，包含以下欄位：
- brand: 品牌
- model: 型號
- price: 價格（數字）
- color: 顏色
- storage: 儲存容量

只返回 JSON，不要其他說明。
"""

        print(f"\n提問: {prompt.strip()}")

        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1  # 低溫度提高確定性
        )

        answer = response.choices[0].message.content
        print(f"\nLLM 回答:\n{answer}")

        # 嘗試解析 JSON
        try:
            data = json.loads(answer)
            print("\n✅ JSON 解析成功:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print("\n⚠️  回應不是有效的 JSON")

    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")

async def example_3_conversation():
    """範例 3: 多輪對話"""
    print("\n" + "=" * 60)
    print("範例 3: 多輪對話")
    print("=" * 60)

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # 構建對話歷史
        messages = [
            {"role": "system", "content": "你是一個 RPA 專家助手。"},
            {"role": "user", "content": "什麼是 RPA？"},
        ]

        print("\n用戶: 什麼是 RPA？")

        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        assistant_msg = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_msg})

        print(f"助手: {assistant_msg}")

        # 第二輪對話
        messages.append({"role": "user", "content": "它和傳統自動化有什麼區別？"})
        print("\n用戶: 它和傳統自動化有什麼區別？")

        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        assistant_msg = response.choices[0].message.content
        print(f"助手: {assistant_msg}")

    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")

async def example_4_cost_tracking():
    """範例 4: 成本追蹤"""
    print("\n" + "=" * 60)
    print("範例 4: 成本追蹤")
    print("=" * 60)

    try:
        from openai import AsyncOpenAI
        import tiktoken

        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        prompt = "請詳細解釋什麼是 RPA，包括它的優點和應用場景。"

        # 計算 Token 數量
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        input_tokens = len(encoding.encode(prompt))

        print(f"\n輸入文字: {prompt}")
        print(f"輸入 Tokens: {input_tokens}")

        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )

        answer = response.choices[0].message.content
        output_tokens = len(encoding.encode(answer))

        # 計算成本（GPT-3.5-Turbo 價格：$0.0015/1K input, $0.002/1K output）
        input_cost = (input_tokens / 1000) * 0.0015
        output_cost = (output_tokens / 1000) * 0.002
        total_cost = input_cost + output_cost

        print(f"\nLLM 回答: {answer}")
        print(f"\n{'=' * 40}")
        print("成本分析:")
        print(f"  輸入 Tokens: {input_tokens}")
        print(f"  輸出 Tokens: {output_tokens}")
        print(f"  總 Tokens: {input_tokens + output_tokens}")
        print(f"  預估成本: ${total_cost:.6f}")
        print(f"{'=' * 40}")

    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")

async def main():
    """主函數"""
    print("\n🚀 LLM 基礎使用範例")
    print("=" * 60)

    # 檢查 API Key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ 錯誤: 未設置 OPENAI_API_KEY 環境變數")
        print("\n請先設置 API Key:")
        print("  方法 1: export OPENAI_API_KEY='your-api-key'")
        print("  方法 2: 在 .env 文件中設置 OPENAI_API_KEY=your-api-key")
        return

    # 運行所有範例
    await example_1_basic_generation()
    await asyncio.sleep(1)

    await example_2_structured_output()
    await asyncio.sleep(1)

    await example_3_conversation()
    await asyncio.sleep(1)

    await example_4_cost_tracking()

    print("\n" + "=" * 60)
    print("✅ 所有範例執行完成！")
    print("=" * 60)

if __name__ == "__main__":
    # 檢查依賴
    try:
        import openai
        import tiktoken
        from dotenv import load_dotenv
    except ImportError as e:
        print(f"❌ 缺少依賴: {e}")
        print("\n請安裝依賴:")
        print("  pip install openai tiktoken python-dotenv")
        exit(1)

    # 運行主函數
    asyncio.run(main())
