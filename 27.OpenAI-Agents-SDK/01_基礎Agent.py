"""
OpenAI Agents SDK - 基礎 Agent 範例

展示如何創建和使用最基本的 Agent
包含：基本配置、簡單對話、模型選擇

與 Swarm 的主要區別：
1. 不需要創建 client 實例
2. 支持更多配置選項
3. 內建錯誤處理
"""

import os
from openai_agents import Agent, run, configure

# ============================================================================
# 1. 環境配置
# ============================================================================

def setup_environment():
    """配置 OpenAI Agents SDK 環境"""
    configure(
        api_key=os.getenv("OPENAI_API_KEY"),
        default_model="gpt-4",  # 默認模型
        timeout=60,  # 請求超時（秒）
        max_retries=3,  # 最大重試次數
        retry_on_rate_limit=True  # 遇到限流時自動重試
    )
    print("✓ 環境配置完成")


# ============================================================================
# 2. 創建基礎 Agent
# ============================================================================

def create_basic_agent():
    """創建最簡單的 Agent"""
    agent = Agent(
        name="基礎助手",
        model="gpt-4",
        instructions="你是一個友善的助手，用繁體中文回答問題。"
    )
    return agent


def create_agent_with_config():
    """創建帶進階配置的 Agent"""
    agent = Agent(
        name="進階助手",
        model="gpt-4",
        instructions="""你是一個專業的助手，遵循以下原則：
        1. 使用繁體中文回答
        2. 回答要簡潔明確
        3. 不確定時承認不知道
        4. 保持友善和專業的態度
        """,
        # 進階配置
        temperature=0.7,  # 創造性程度
        max_tokens=500,  # 最大回應長度
        top_p=0.9,  # 採樣閾值
    )
    return agent


# ============================================================================
# 3. 運行 Agent
# ============================================================================

def simple_conversation():
    """簡單的單輪對話"""
    print("\n" + "="*60)
    print("範例 1: 簡單對話")
    print("="*60)

    agent = create_basic_agent()

    # 創建消息
    messages = [
        {"role": "user", "content": "你好！請介紹一下自己。"}
    ]

    # 運行對話
    response = run(agent=agent, messages=messages)

    # 顯示結果
    print(f"\n用戶: {messages[0]['content']}")
    print(f"助手: {response.messages[-1]['content']}")

    # 顯示元數據
    print(f"\n[元數據]")
    print(f"  使用模型: {response.model}")
    print(f"  Token 使用: {response.usage.total_tokens}")
    print(f"  完成原因: {response.finish_reason}")


def multi_turn_conversation():
    """多輪對話（手動管理歷史）"""
    print("\n" + "="*60)
    print("範例 2: 多輪對話")
    print("="*60)

    agent = create_basic_agent()

    # 初始化對話歷史
    messages = []

    # 第一輪
    user_msg_1 = "我叫小明，請記住我的名字。"
    messages.append({"role": "user", "content": user_msg_1})

    response_1 = run(agent=agent, messages=messages)
    messages = response_1.messages  # 更新歷史

    print(f"\n第 1 輪:")
    print(f"  用戶: {user_msg_1}")
    print(f"  助手: {messages[-1]['content']}")

    # 第二輪（測試是否記住名字）
    user_msg_2 = "我剛才告訴你我叫什麼名字？"
    messages.append({"role": "user", "content": user_msg_2})

    response_2 = run(agent=agent, messages=messages)
    messages = response_2.messages

    print(f"\n第 2 輪:")
    print(f"  用戶: {user_msg_2}")
    print(f"  助手: {messages[-1]['content']}")

    # 顯示完整對話歷史
    print(f"\n[完整對話歷史] 共 {len(messages)} 條消息")
    for i, msg in enumerate(messages, 1):
        role = "用戶" if msg["role"] == "user" else "助手"
        print(f"  {i}. {role}: {msg['content'][:50]}...")


# ============================================================================
# 4. 不同模型對比
# ============================================================================

def compare_models():
    """比較不同模型的表現"""
    print("\n" + "="*60)
    print("範例 3: 模型對比")
    print("="*60)

    question = "請用一句話解釋什麼是量子糾纏。"

    models = [
        ("gpt-4", "GPT-4"),
        ("gpt-4-turbo", "GPT-4 Turbo"),
        ("gpt-3.5-turbo", "GPT-3.5 Turbo")
    ]

    for model_id, model_name in models:
        agent = Agent(
            name=f"{model_name}助手",
            model=model_id,
            instructions="用最簡潔的方式回答問題。"
        )

        messages = [{"role": "user", "content": question}]
        response = run(agent=agent, messages=messages)

        print(f"\n【{model_name}】")
        print(f"回答: {response.messages[-1]['content']}")
        print(f"Token: {response.usage.total_tokens}")


# ============================================================================
# 5. 錯誤處理
# ============================================================================

def handle_errors():
    """展示錯誤處理機制"""
    print("\n" + "="*60)
    print("範例 4: 錯誤處理")
    print("="*60)

    # 情況 1: API Key 錯誤（模擬）
    print("\n情況 1: 正常請求")
    try:
        agent = Agent(name="測試", model="gpt-4", instructions="你是助手")
        response = run(
            agent=agent,
            messages=[{"role": "user", "content": "你好"}]
        )
        print(f"✓ 請求成功: {response.messages[-1]['content'][:50]}...")
    except Exception as e:
        print(f"✗ 錯誤: {e}")

    # 情況 2: 超時處理
    print("\n情況 2: 設置短超時")
    try:
        configure(timeout=0.001)  # 設置非常短的超時
        agent = Agent(name="測試", model="gpt-4", instructions="你是助手")
        response = run(
            agent=agent,
            messages=[{"role": "user", "content": "你好"}]
        )
        print(f"✓ 請求成功")
    except Exception as e:
        print(f"✗ 預期的超時錯誤: {type(e).__name__}")
    finally:
        # 恢復正常超時
        configure(timeout=60)

    # 情況 3: 無效的模型名稱
    print("\n情況 3: 無效模型")
    try:
        agent = Agent(name="測試", model="invalid-model", instructions="你是助手")
        response = run(
            agent=agent,
            messages=[{"role": "user", "content": "你好"}]
        )
        print(f"✓ 請求成功")
    except Exception as e:
        print(f"✗ 預期的錯誤: {type(e).__name__}")


# ============================================================================
# 6. Agent 屬性檢查
# ============================================================================

def inspect_agent():
    """檢查 Agent 的屬性和配置"""
    print("\n" + "="*60)
    print("範例 5: 檢查 Agent 屬性")
    print("="*60)

    agent = Agent(
        name="檢查對象",
        model="gpt-4",
        instructions="這是一個測試 Agent",
        temperature=0.8,
        max_tokens=1000
    )

    print(f"\nAgent 基本信息:")
    print(f"  名稱: {agent.name}")
    print(f"  模型: {agent.model}")
    print(f"  指令: {agent.instructions}")
    print(f"  溫度: {agent.temperature}")
    print(f"  最大 Token: {agent.max_tokens}")
    print(f"  工具數量: {len(agent.tools) if agent.tools else 0}")
    print(f"  護欄數量: {len(agent.guardrails) if agent.guardrails else 0}")


# ============================================================================
# 7. 與 Swarm 對比
# ============================================================================

def swarm_vs_agents_sdk():
    """展示與 Swarm 的代碼對比"""
    print("\n" + "="*60)
    print("範例 6: Swarm vs Agents SDK")
    print("="*60)

    print("\n【Swarm 風格】")
    print("""
    from swarm import Swarm, Agent

    client = Swarm()
    agent = Agent(
        name="助手",
        instructions="你是助手"
    )

    response = client.run(
        agent=agent,
        messages=[{"role": "user", "content": "你好"}]
    )
    """)

    print("\n【Agents SDK 風格】")
    print("""
    from openai_agents import Agent, run, configure

    configure(api_key="...", timeout=60)  # 全局配置

    agent = Agent(
        name="助手",
        instructions="你是助手",
        temperature=0.7,  # 更多配置選項
        max_tokens=500
    )

    response = run(  # 不需要 client
        agent=agent,
        messages=[{"role": "user", "content": "你好"}]
    )
    """)

    print("\n主要差異:")
    print("  1. Agents SDK 不需要創建 client 實例")
    print("  2. 支持全局配置 (configure)")
    print("  3. Agent 有更多配置選項")
    print("  4. 內建更好的錯誤處理和重試機制")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """運行所有範例"""
    print("="*60)
    print("OpenAI Agents SDK - 基礎 Agent 範例")
    print("="*60)

    # 設置環境
    setup_environment()

    # 運行各個範例
    try:
        simple_conversation()
        multi_turn_conversation()
        compare_models()
        handle_errors()
        inspect_agent()
        swarm_vs_agents_sdk()
    except Exception as e:
        print(f"\n錯誤: {e}")
        print("請確保已設置 OPENAI_API_KEY 環境變量")

    print("\n" + "="*60)
    print("所有範例運行完成！")
    print("="*60)


if __name__ == "__main__":
    main()
