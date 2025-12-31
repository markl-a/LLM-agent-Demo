"""
Microsoft Agent Framework - 快速開始範例

這個檔案展示了如何使用 Microsoft Agent Framework 的基礎功能。
Agent Framework 是 AutoGen 和 Semantic Kernel 的統一框架,
提供了強大的 AI Agent 開發能力。

主要內容:
1. 環境設定和初始化
2. 創建基本的 Agent
3. 執行簡單的對話
4. 使用內聯工具 (Inline Tools)
5. 基礎錯誤處理

作者: Microsoft Agent Framework Team
日期: 2025-12-31
版本: 1.0.0
"""

import os
import asyncio
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# 導入 Agent Framework 核心模組
from agent_framework import Agent, AgentThread, AgentRunResult
from agent_framework.models import OpenAIModel, AzureOpenAIModel
from agent_framework.tools import Tool, ToolResult
from agent_framework.exceptions import AgentError, ModelError

# ============================================================================
# 1. 環境設定
# ============================================================================

def setup_environment():
    """
    設定環境變數和配置

    Agent Framework 需要以下環境變數:
    - OPENAI_API_KEY: OpenAI API 金鑰
    - OPENAI_MODEL: 使用的模型名稱 (如 gpt-4)
    - 或者使用 Azure OpenAI 的相關配置
    """
    # 載入 .env 檔案中的環境變數
    load_dotenv()

    # 檢查必要的環境變數
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  警告: 未設定 OPENAI_API_KEY 環境變數")
        print("請在 .env 檔案中設定:")
        print("OPENAI_API_KEY=your_api_key_here")
        return False

    print("✅ 環境設定完成")
    print(f"📦 使用模型: {os.getenv('OPENAI_MODEL', 'gpt-4')}")
    return True


# ============================================================================
# 2. 創建基礎模型
# ============================================================================

def create_model() -> OpenAIModel:
    """
    創建 OpenAI 模型實例

    Agent Framework 支援多種模型後端:
    - OpenAI (GPT-4, GPT-3.5-turbo)
    - Azure OpenAI
    - 其他 OpenAI 相容的端點

    Returns:
        配置好的模型實例
    """
    model_name = os.getenv("OPENAI_MODEL", "gpt-4")

    # 檢查是否使用 Azure OpenAI
    if os.getenv("AZURE_OPENAI_ENDPOINT"):
        print("🔵 使用 Azure OpenAI")
        model = AzureOpenAIModel(
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", model_name),
            api_version="2024-08-01-preview"
        )
    else:
        print("🟢 使用 OpenAI")
        model = OpenAIModel(
            model=model_name,
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.7,  # 控制隨機性 (0-2)
            max_tokens=2000,  # 最大輸出長度
        )

    return model


# ============================================================================
# 3. 定義工具函數
# ============================================================================

def get_current_weather(location: str, unit: str = "celsius") -> str:
    """
    獲取指定位置的當前天氣 (模擬函數)

    這是一個工具函數範例,展示如何為 Agent 提供外部能力。
    在實際應用中,這裡會調用真實的天氣 API。

    Args:
        location: 城市或地區名稱
        unit: 溫度單位,可選 "celsius" 或 "fahrenheit"

    Returns:
        天氣資訊的 JSON 字串
    """
    # 模擬天氣資料
    weather_data = {
        "台北": {"temp": 25, "condition": "晴天", "humidity": 65},
        "高雄": {"temp": 28, "condition": "多雲", "humidity": 70},
        "台中": {"temp": 26, "condition": "陰天", "humidity": 60},
        "台南": {"temp": 27, "condition": "晴天", "humidity": 68},
    }

    # 取得天氣資訊
    data = weather_data.get(location, {"temp": 22, "condition": "未知", "humidity": 50})

    # 溫度單位轉換
    temp = data["temp"]
    if unit == "fahrenheit":
        temp = temp * 9/5 + 32
        unit_symbol = "°F"
    else:
        unit_symbol = "°C"

    # 格式化輸出
    result = f"{location}的天氣:\n"
    result += f"  溫度: {temp}{unit_symbol}\n"
    result += f"  狀況: {data['condition']}\n"
    result += f"  濕度: {data['humidity']}%"

    return result


def calculate(expression: str) -> str:
    """
    計算數學表達式

    這個工具允許 Agent 執行數學計算。
    注意:在生產環境中,應該使用更安全的計算方法。

    Args:
        expression: 數學表達式字串,如 "2 + 3 * 4"

    Returns:
        計算結果
    """
    try:
        # 注意:eval 在生產環境中可能不安全,這裡僅用於示範
        result = eval(expression, {"__builtins__": {}}, {})
        return f"計算結果: {expression} = {result}"
    except Exception as e:
        return f"計算錯誤: {str(e)}"


def search_knowledge(query: str) -> str:
    """
    搜尋知識庫 (模擬函數)

    這個工具模擬知識庫搜尋功能。
    在實際應用中,這裡會連接到向量資料庫或搜尋引擎。

    Args:
        query: 搜尋查詢字串

    Returns:
        搜尋結果
    """
    # 模擬知識庫
    knowledge_base = {
        "agent framework": "Microsoft Agent Framework 是 AutoGen 和 Semantic Kernel 的統一框架",
        "mcp": "Model Context Protocol (MCP) 是 Anthropic 提出的標準化協議",
        "azure": "Azure AI 提供企業級的 AI 服務和基礎設施",
    }

    # 簡單的關鍵字匹配
    for key, value in knowledge_base.items():
        if key in query.lower():
            return f"找到相關資訊:\n{value}"

    return "未找到相關資訊"


# ============================================================================
# 4. 創建基礎 Agent
# ============================================================================

def create_basic_agent(model: OpenAIModel) -> Agent:
    """
    創建一個基礎的 Agent

    Agent 是 Agent Framework 的核心概念,代表一個具有特定能力和行為的 AI 實體。
    每個 Agent 包含:
    - name: Agent 的唯一識別名稱
    - model: 使用的 LLM 模型
    - instructions: 系統提示詞,定義 Agent 的行為
    - tools: Agent 可以使用的工具列表

    Args:
        model: 配置好的模型實例

    Returns:
        配置好的 Agent 實例
    """
    agent = Agent(
        name="assistant",
        model=model,
        instructions="""
        你是一個友善且專業的助手,名叫小智。
        你的職責是幫助用戶解答問題、查詢資訊、執行計算等任務。

        請遵循以下原則:
        1. 總是以友善和專業的態度回應
        2. 如果不確定答案,誠實告知用戶
        3. 適時使用提供的工具來獲取資訊或執行操作
        4. 提供清晰、結構化的回答
        5. 使用繁體中文回應
        """,
        tools=[
            get_current_weather,  # 天氣查詢工具
            calculate,            # 計算工具
            search_knowledge,     # 知識搜尋工具
        ]
    )

    print(f"✅ Agent '{agent.name}' 創建成功")
    print(f"   工具數量: {len(agent.tools)}")

    return agent


# ============================================================================
# 5. 執行對話
# ============================================================================

def run_simple_conversation(agent: Agent):
    """
    執行簡單的對話

    這個函數展示如何使用 Agent 進行基本對話。
    Thread 代表一個對話會話,保存對話歷史和上下文。

    Args:
        agent: 配置好的 Agent 實例
    """
    print("\n" + "="*70)
    print("🎯 範例 1: 簡單對話")
    print("="*70)

    # 創建對話線程
    thread = AgentThread()

    # 測試對話列表
    test_messages = [
        "你好,請自我介紹一下",
        "台北今天的天氣如何?",
        "幫我計算 15 * 23 + 100",
        "什麼是 MCP 協議?",
    ]

    for i, message in enumerate(test_messages, 1):
        print(f"\n👤 用戶 [{i}]: {message}")

        try:
            # 執行對話
            response = agent.run(
                thread=thread,
                messages=message
            )

            print(f"🤖 助手 [{i}]: {response.content}")

            # 顯示工具調用資訊
            if response.tool_calls:
                print(f"   ⚙️  調用了 {len(response.tool_calls)} 個工具:")
                for tool_call in response.tool_calls:
                    print(f"      - {tool_call.function.name}")

        except AgentError as e:
            print(f"❌ Agent 錯誤: {str(e)}")
        except Exception as e:
            print(f"❌ 未預期的錯誤: {str(e)}")


# ============================================================================
# 6. 多輪對話
# ============================================================================

def run_multi_turn_conversation(agent: Agent):
    """
    執行多輪對話

    展示 Agent 如何維護對話上下文,進行連貫的多輪對話。
    Thread 會自動保存對話歷史,使 Agent 能夠理解上下文。

    Args:
        agent: 配置好的 Agent 實例
    """
    print("\n" + "="*70)
    print("🎯 範例 2: 多輪對話 (含上下文)")
    print("="*70)

    # 創建新的對話線程
    thread = AgentThread()

    # 多輪對話,後續問題依賴前面的上下文
    conversation = [
        ("台北的天氣如何?", "查詢台北天氣"),
        ("那高雄呢?", "基於上下文查詢高雄天氣"),
        ("兩個城市的溫度相差多少?", "基於前兩次查詢進行計算"),
    ]

    for i, (message, description) in enumerate(conversation, 1):
        print(f"\n👤 用戶 [{i}] ({description}): {message}")

        response = agent.run(
            thread=thread,
            messages=message
        )

        print(f"🤖 助手 [{i}]: {response.content}")


# ============================================================================
# 7. 非同步執行
# ============================================================================

async def run_async_conversation(agent: Agent):
    """
    非同步執行對話

    Agent Framework 支援非同步操作,提高並發效能。
    這對於處理多個用戶或並行任務特別有用。

    Args:
        agent: 配置好的 Agent 實例
    """
    print("\n" + "="*70)
    print("🎯 範例 3: 非同步執行")
    print("="*70)

    # 創建多個獨立的對話線程
    threads = [AgentThread() for _ in range(3)]

    # 不同用戶的問題
    messages = [
        "台北天氣如何?",
        "幫我計算 50 * 60",
        "什麼是 Agent Framework?",
    ]

    # 並行執行多個對話
    tasks = []
    for i, (thread, message) in enumerate(zip(threads, messages), 1):
        print(f"\n👤 用戶 {i}: {message}")
        # 在實際的非同步版本中,這裡會使用 agent.run_async()
        # task = agent.run_async(thread=thread, messages=message)
        # tasks.append(task)

    # 等待所有任務完成
    # results = await asyncio.gather(*tasks)

    # 目前使用同步版本示範
    for i, (thread, message) in enumerate(zip(threads, messages), 1):
        response = agent.run(thread=thread, messages=message)
        print(f"🤖 助手 {i}: {response.content}")


# ============================================================================
# 8. 錯誤處理
# ============================================================================

def demonstrate_error_handling(agent: Agent):
    """
    展示錯誤處理機制

    在生產環境中,適當的錯誤處理至關重要。
    Agent Framework 提供多種異常類型來處理不同的錯誤情況。

    Args:
        agent: 配置好的 Agent 實例
    """
    print("\n" + "="*70)
    print("🎯 範例 4: 錯誤處理")
    print("="*70)

    thread = AgentThread()

    # 測試各種錯誤情況
    error_cases = [
        ("幫我計算 1/0", "觸發計算錯誤"),
        ("", "空訊息"),
    ]

    for message, description in error_cases:
        print(f"\n測試: {description}")
        print(f"👤 用戶: {message}")

        try:
            if not message:
                raise ValueError("訊息不能為空")

            response = agent.run(
                thread=thread,
                messages=message,
                max_turns=5  # 限制最大輪次,防止無限循環
            )

            print(f"🤖 助手: {response.content}")

        except ValueError as e:
            print(f"❌ 驗證錯誤: {str(e)}")
        except AgentError as e:
            print(f"❌ Agent 錯誤: {str(e)}")
        except ModelError as e:
            print(f"❌ 模型錯誤: {str(e)}")
        except Exception as e:
            print(f"❌ 系統錯誤: {str(e)}")


# ============================================================================
# 9. 主程式
# ============================================================================

def main():
    """
    主程式入口

    執行所有範例展示 Agent Framework 的基礎功能:
    1. 環境設定
    2. 模型和 Agent 創建
    3. 各種對話模式
    4. 錯誤處理
    """
    print("="*70)
    print("Microsoft Agent Framework - 快速開始")
    print("="*70)

    # 1. 設定環境
    if not setup_environment():
        print("\n❌ 環境設定失敗,請檢查配置")
        return

    try:
        # 2. 創建模型
        print("\n📦 正在創建模型...")
        model = create_model()

        # 3. 創建 Agent
        print("\n🤖 正在創建 Agent...")
        agent = create_basic_agent(model)

        # 4. 執行各種範例
        run_simple_conversation(agent)
        run_multi_turn_conversation(agent)

        # 非同步範例 (需要事件循環)
        # asyncio.run(run_async_conversation(agent))

        demonstrate_error_handling(agent)

        print("\n" + "="*70)
        print("✅ 所有範例執行完成!")
        print("="*70)

        # 5. 顯示使用統計
        print("\n📊 使用統計:")
        print(f"   Agent 名稱: {agent.name}")
        print(f"   可用工具: {len(agent.tools)}")
        print(f"   模型: {model.model if hasattr(model, 'model') else 'Azure OpenAI'}")

    except Exception as e:
        print(f"\n❌ 執行失敗: {str(e)}")
        import traceback
        traceback.print_exc()


# ============================================================================
# 10. 進階提示
# ============================================================================

def print_advanced_tips():
    """
    輸出進階使用提示
    """
    print("\n" + "="*70)
    print("💡 進階提示")
    print("="*70)

    tips = [
        "1. 使用 agent.run_stream() 可以獲得串流式回應",
        "2. Thread 可以持久化保存,用於長期對話",
        "3. 可以創建多個 Agent 組成團隊協作",
        "4. 使用 MCP 協議可以整合外部工具和服務",
        "5. Azure AI Foundry 提供完整的部署和監控方案",
        "6. 工具函數支援複雜的參數類型 (Pydantic models)",
        "7. 可以使用 Workflow 定義複雜的執行流程",
        "8. 支援自定義的工具和插件擴展",
        "9. 使用結構化輸出確保 Agent 回應格式",
        "10. 查看其他範例檔案學習更多進階功能",
    ]

    for tip in tips:
        print(f"   {tip}")

    print("\n📚 相關檔案:")
    print("   - 02_Agent創建.py: 深入了解 Agent 配置")
    print("   - 03_多Agent編排.py: 多 Agent 協作模式")
    print("   - 04_線程管理.py: 對話線程管理")
    print("   - 更多範例請查看專案目錄...")


# 執行主程式
if __name__ == "__main__":
    main()
    print_advanced_tips()
