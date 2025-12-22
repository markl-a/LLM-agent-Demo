"""
Pydantic AI - 基礎 Agent 範例

本範例展示：
1. 創建最簡單的 Agent
2. 同步和異步運行
3. Agent 配置參數
4. 基本錯誤處理
5. 運行結果的使用

安裝：pip install 'pydantic-ai[openai]'
"""

import asyncio
from typing import Optional
from pydantic_ai import Agent
from pydantic_ai.exceptions import UnexpectedModelBehavior, UserError


# ============================================================================
# 範例 1: 最簡單的 Agent
# ============================================================================

def example_1_simple_agent():
    """創建和運行最簡單的 Agent"""
    print("\n" + "="*60)
    print("範例 1: 最簡單的 Agent")
    print("="*60)

    # 創建一個使用 OpenAI GPT-4 的 Agent
    # 格式：'provider:model'
    agent = Agent('openai:gpt-4')

    # 同步運行 Agent
    result = agent.run_sync('你好，請介紹一下自己')

    # 輸出結果
    print(f"AI 回應：{result.data}")
    print(f"使用的 tokens：{result.usage()}")


# ============================================================================
# 範例 2: 異步運行
# ============================================================================

async def example_2_async_agent():
    """使用異步方式運行 Agent"""
    print("\n" + "="*60)
    print("範例 2: 異步運行 Agent")
    print("="*60)

    agent = Agent('openai:gpt-4')

    # 異步運行 Agent（推薦方式）
    result = await agent.run('講一個簡短的笑話')

    print(f"AI 回應：{result.data}")

    # 訪問更多運行信息
    print(f"\n運行詳情：")
    print(f"- 使用的 tokens：{result.usage()}")
    print(f"- 請求 ID：{result.new_message_index}")


# ============================================================================
# 範例 3: Agent 配置參數
# ============================================================================

def example_3_agent_configuration():
    """配置 Agent 的各種參數"""
    print("\n" + "="*60)
    print("範例 3: Agent 配置參數")
    print("="*60)

    # 配置 Agent 的系統提示詞
    agent = Agent(
        'openai:gpt-4',
        system_prompt='你是一個專業的 Python 程式教師，擅長用簡單的語言解釋複雜的概念。'
    )

    result = agent.run_sync('什麼是裝飾器？')
    print(f"教師回應：{result.data}\n")

    # 配置重試次數
    agent_with_retry = Agent(
        'openai:gpt-4',
        retries=3  # API 失敗時自動重試 3 次
    )

    print("✓ Agent 已配置自動重試機制")


# ============================================================================
# 範例 4: 動態系統提示詞
# ============================================================================

def example_4_dynamic_system_prompt():
    """使用函數動態生成系統提示詞"""
    print("\n" + "="*60)
    print("範例 4: 動態系統提示詞")
    print("="*60)

    agent = Agent('openai:gpt-4')

    # 使用裝飾器定義系統提示詞
    @agent.system_prompt
    def get_system_prompt() -> str:
        """動態生成系統提示詞"""
        import datetime
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        return f"""你是一個時間感知的助手。
        當前時間：{current_time}
        請在回答時考慮當前的時間背景。
        """

    result = agent.run_sync('現在是什麼時候？')
    print(f"AI 回應：{result.data}")


# ============================================================================
# 範例 5: 錯誤處理
# ============================================================================

def example_5_error_handling():
    """處理 Agent 運行時可能出現的錯誤"""
    print("\n" + "="*60)
    print("範例 5: 錯誤處理")
    print("="*60)

    agent = Agent('openai:gpt-4')

    try:
        # 正常運行
        result = agent.run_sync('計算 2 + 2')
        print(f"✓ 成功：{result.data}")

    except UnexpectedModelBehavior as e:
        # 模型行為異常（如格式錯誤、解析失敗等）
        print(f"✗ 模型行為異常：{e}")

    except UserError as e:
        # 用戶錯誤（如無效的提示詞等）
        print(f"✗ 用戶錯誤：{e}")

    except Exception as e:
        # 其他錯誤（網絡問題、API 限制等）
        print(f"✗ 未知錯誤：{e}")


# ============================================================================
# 範例 6: 訪問運行結果的詳細信息
# ============================================================================

async def example_6_result_details():
    """探索運行結果對象的各種屬性"""
    print("\n" + "="*60)
    print("範例 6: 運行結果詳情")
    print("="*60)

    agent = Agent('openai:gpt-4')

    result = await agent.run('用一句話描述 Python')

    # 主要數據
    print(f"回應內容：{result.data}")

    # Token 使用情況
    usage = result.usage()
    print(f"\nToken 使用：")
    print(f"- 請求 tokens：{usage.request_tokens}")
    print(f"- 回應 tokens：{usage.response_tokens}")
    print(f"- 總計 tokens：{usage.total_tokens}")

    # 對話歷史
    print(f"\n對話消息數：{len(result.all_messages())}")

    # 新消息的索引
    print(f"新消息索引：{result.new_message_index}")


# ============================================================================
# 範例 7: 多輪對話基礎
# ============================================================================

async def example_7_conversation():
    """使用 message history 進行多輪對話"""
    print("\n" + "="*60)
    print("範例 7: 多輪對話")
    print("="*60)

    agent = Agent('openai:gpt-4')

    # 第一輪對話
    result1 = await agent.run('我最喜歡的顏色是藍色')
    print(f"用戶：我最喜歡的顏色是藍色")
    print(f"AI：{result1.data}")

    # 第二輪對話 - 傳入之前的消息歷史
    result2 = await agent.run(
        '我剛才說我喜歡什麼顏色？',
        message_history=result1.all_messages()
    )
    print(f"\n用戶：我剛才說我喜歡什麼顏色？")
    print(f"AI：{result2.data}")


# ============================================================================
# 範例 8: 不同的模型選擇
# ============================================================================

def example_8_model_selection():
    """嘗試不同的 AI 模型"""
    print("\n" + "="*60)
    print("範例 8: 不同的模型選擇")
    print("="*60)

    # GPT-4（最強大，但較慢較貴）
    agent_gpt4 = Agent('openai:gpt-4')

    # GPT-3.5 Turbo（快速且便宜）
    agent_gpt35 = Agent('openai:gpt-3.5-turbo')

    # GPT-4 Turbo（平衡性能和成本）
    agent_gpt4_turbo = Agent('openai:gpt-4-turbo-preview')

    prompt = '簡單解釋什麼是機器學習'

    print("使用 GPT-3.5 Turbo（快速）：")
    result = agent_gpt35.run_sync(prompt)
    print(f"{result.data[:100]}...\n")

    print("✓ 可以根據需求選擇不同的模型")


# ============================================================================
# 範例 9: 設置最大 Token 數
# ============================================================================

async def example_9_max_tokens():
    """控制回應的長度"""
    print("\n" + "="*60)
    print("範例 9: 控制回應長度")
    print("="*60)

    agent = Agent('openai:gpt-4')

    # 短回應（最多 50 tokens）
    result_short = await agent.run(
        '介紹 Python',
        model_settings={'max_tokens': 50}
    )
    print(f"短回應（50 tokens）：")
    print(f"{result_short.data}\n")

    # 長回應（最多 200 tokens）
    result_long = await agent.run(
        '介紹 Python',
        model_settings={'max_tokens': 200}
    )
    print(f"長回應（200 tokens）：")
    print(f"{result_long.data}")


# ============================================================================
# 範例 10: Agent 名稱和元數據
# ============================================================================

def example_10_agent_metadata():
    """為 Agent 設置名稱和元數據"""
    print("\n" + "="*60)
    print("範例 10: Agent 元數據")
    print("="*60)

    # 創建一個有名稱的 Agent
    agent = Agent(
        'openai:gpt-4',
        name='PythonTutor',  # Agent 名稱
        system_prompt='你是一個 Python 教學專家'
    )

    print(f"Agent 名稱：{agent.name}")
    print(f"Agent 模型：{agent.model}")

    result = agent.run_sync('教我 list comprehension')
    print(f"\n{agent.name} 回應：")
    print(result.data)


# ============================================================================
# 主程式
# ============================================================================

async def main():
    """運行所有範例"""
    print("\n" + "🚀 " + "="*58)
    print("Pydantic AI - 基礎 Agent 範例")
    print("="*60)

    # 同步範例
    example_1_simple_agent()

    # 異步範例
    await example_2_async_agent()

    # 配置範例
    example_3_agent_configuration()
    example_4_dynamic_system_prompt()

    # 錯誤處理
    example_5_error_handling()

    # 結果詳情
    await example_6_result_details()

    # 對話
    await example_7_conversation()

    # 模型選擇
    example_8_model_selection()

    # Token 控制
    await example_9_max_tokens()

    # 元數據
    example_10_agent_metadata()

    print("\n" + "="*60)
    print("✓ 所有基礎範例完成！")
    print("="*60)


if __name__ == '__main__':
    # 提示：需要設置環境變量 OPENAI_API_KEY
    import os

    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  警告：請設置環境變量 OPENAI_API_KEY")
        print("   export OPENAI_API_KEY='your-key-here'")
    else:
        asyncio.run(main())
