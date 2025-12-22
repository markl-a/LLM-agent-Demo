"""
01_基礎入門.py - Agno 框架基礎入門

本範例展示 Agno 框架的核心概念和基本用法，包括：
- 創建第一個 Agent
- Agent 基本配置與參數
- 簡單對話與交互
- 模型選擇與切換
- 調試與日誌輸出
- 錯誤處理機制

作者：LLM-agent-Demo Team
日期：2025-12
框架：Agno (原 Phidata)
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Agno 核心導入
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.groq import GroqChat
from agno.utils.log import logger

# 載入環境變數
load_dotenv()


# ============================================================================
# 範例 1: 創建第一個 Agent
# ============================================================================
def example_1_first_agent():
    """
    創建最簡單的 Agno Agent

    這是 Agno 最基本的用法，展示如何快速創建一個能夠對話的 Agent
    """
    print("\n" + "="*80)
    print("範例 1: 創建第一個 Agent")
    print("="*80)

    # 創建 Agent（使用預設配置）
    agent = Agent(
        model=OpenAIChat(id="gpt-4"),
        description="一個友好的助手"
    )

    # 執行對話
    response = agent.run("你好！請介紹一下自己。")

    print(f"\nAgent 回應:\n{response.content}")

    return agent


# ============================================================================
# 範例 2: Agent 詳細配置
# ============================================================================
def example_2_agent_configuration():
    """
    展示 Agent 的詳細配置選項

    重要參數：
    - name: Agent 名稱（用於團隊協作時識別）
    - role: Agent 角色定位
    - instructions: 詳細的行為指導
    - model: 使用的 LLM 模型
    - markdown: 是否使用 Markdown 格式輸出
    - show_tool_calls: 是否顯示工具調用過程
    - debug_mode: 調試模式
    """
    print("\n" + "="*80)
    print("範例 2: Agent 詳細配置")
    print("="*80)

    # 創建具有詳細配置的 Agent
    agent = Agent(
        name="python_tutor",
        role="專業的 Python 程式設計導師",
        model=OpenAIChat(id="gpt-4"),

        # 詳細的行為指導
        instructions=[
            "你是一位經驗豐富的 Python 導師",
            "用清晰、易懂的方式解釋概念",
            "提供實際的程式碼範例",
            "鼓勵最佳實踐和良好的程式設計習慣",
            "對初學者保持耐心和友善"
        ],

        # 輸出配置
        markdown=True,          # 使用 Markdown 格式
        show_tool_calls=True,   # 顯示工具調用

        # 調試配置
        debug_mode=False
    )

    # 測試 Agent
    query = "請解釋 Python 中的列表推導式（list comprehension），並給個例子。"
    print(f"\n提問: {query}\n")

    response = agent.run(query)
    print(f"回應:\n{response.content}")

    return agent


# ============================================================================
# 範例 3: 模型選擇與切換
# ============================================================================
def example_3_model_selection():
    """
    展示如何選擇和切換不同的 LLM 模型

    Agno 支持多種模型提供者：
    - OpenAI: GPT-3.5, GPT-4, GPT-4 Turbo
    - Groq: Mixtral, Llama3 (超快速度)
    - Anthropic: Claude 系列
    - Google: Gemini 系列
    - Ollama: 本地模型
    """
    print("\n" + "="*80)
    print("範例 3: 模型選擇與切換")
    print("="*80)

    # 測試問題
    question = "什麼是機器學習？用一句話回答。"

    # 1. OpenAI GPT-3.5 (快速、經濟)
    print("\n--- 使用 GPT-3.5 Turbo ---")
    agent_gpt35 = Agent(
        model=OpenAIChat(id="gpt-3.5-turbo"),
        description="使用 GPT-3.5 的 Agent"
    )
    response1 = agent_gpt35.run(question)
    print(f"GPT-3.5: {response1.content}\n")

    # 2. OpenAI GPT-4 (高質量)
    print("--- 使用 GPT-4 ---")
    agent_gpt4 = Agent(
        model=OpenAIChat(id="gpt-4"),
        description="使用 GPT-4 的 Agent"
    )
    response2 = agent_gpt4.run(question)
    print(f"GPT-4: {response2.content}\n")

    # 3. Groq (超快速度)
    if os.getenv("GROQ_API_KEY"):
        print("--- 使用 Groq Mixtral (超快) ---")
        agent_groq = Agent(
            model=GroqChat(id="mixtral-8x7b-32768"),
            description="使用 Groq 的 Agent"
        )
        response3 = agent_groq.run(question)
        print(f"Groq: {response3.content}\n")
    else:
        print("⚠️  未設置 GROQ_API_KEY，跳過 Groq 測試")


# ============================================================================
# 範例 4: 多輪對話
# ============================================================================
def example_4_multi_turn_conversation():
    """
    展示多輪對話能力

    Agno Agent 自動維護對話歷史，支持上下文理解
    """
    print("\n" + "="*80)
    print("範例 4: 多輪對話")
    print("="*80)

    # 創建 Agent
    agent = Agent(
        name="conversation_agent",
        model=OpenAIChat(id="gpt-4"),
        description="擅長多輪對話的助手",
        markdown=True
    )

    # 第一輪對話
    print("\n第一輪對話:")
    print("用戶: 我想學習 Python，應該從哪裡開始？")
    response1 = agent.run("我想學習 Python，應該從哪裡開始？")
    print(f"Agent: {response1.content}\n")

    # 第二輪對話（基於上下文）
    print("第二輪對話:")
    print("用戶: 那需要多長時間？")
    response2 = agent.run("那需要多長時間？")
    print(f"Agent: {response2.content}\n")

    # 第三輪對話（繼續上下文）
    print("第三輪對話:")
    print("用戶: 有推薦的學習資源嗎？")
    response3 = agent.run("有推薦的學習資源嗎？")
    print(f"Agent: {response3.content}\n")


# ============================================================================
# 範例 5: Agent 溫度參數控制
# ============================================================================
def example_5_temperature_control():
    """
    展示溫度參數對輸出的影響

    溫度（temperature）控制輸出的隨機性：
    - 0.0: 確定性輸出，每次都相同
    - 0.7: 平衡創造性和一致性（預設）
    - 1.0+: 高創造性，輸出更多樣化
    """
    print("\n" + "="*80)
    print("範例 5: 溫度參數控制")
    print("="*80)

    prompt = "寫一句關於春天的詩。"

    # 低溫度 (確定性)
    print("\n--- 低溫度 (temperature=0) ---")
    agent_low_temp = Agent(
        model=OpenAIChat(id="gpt-3.5-turbo", temperature=0.0)
    )
    print(f"提示: {prompt}")
    print(f"輸出: {agent_low_temp.run(prompt).content}\n")

    # 中溫度 (平衡)
    print("--- 中溫度 (temperature=0.7) ---")
    agent_mid_temp = Agent(
        model=OpenAIChat(id="gpt-3.5-turbo", temperature=0.7)
    )
    print(f"提示: {prompt}")
    print(f"輸出: {agent_mid_temp.run(prompt).content}\n")

    # 高溫度 (創造性)
    print("--- 高溫度 (temperature=1.2) ---")
    agent_high_temp = Agent(
        model=OpenAIChat(id="gpt-3.5-turbo", temperature=1.2)
    )
    print(f"提示: {prompt}")
    print(f"輸出: {agent_high_temp.run(prompt).content}\n")


# ============================================================================
# 範例 6: 調試模式與日誌
# ============================================================================
def example_6_debugging_and_logging():
    """
    展示如何使用調試模式和日誌

    調試技巧：
    - debug_mode: 顯示詳細的執行過程
    - show_tool_calls: 顯示工具調用
    - logger: 自定義日誌輸出
    """
    print("\n" + "="*80)
    print("範例 6: 調試模式與日誌")
    print("="*80)

    # 啟用調試模式
    agent = Agent(
        name="debug_agent",
        model=OpenAIChat(id="gpt-3.5-turbo"),
        debug_mode=True,        # 啟用調試模式
        show_tool_calls=True,   # 顯示工具調用
    )

    print("\n執行任務（調試模式開啟）:")
    response = agent.run("2的10次方是多少？")

    print(f"\n最終回答: {response.content}")


# ============================================================================
# 範例 7: 錯誤處理
# ============================================================================
def example_7_error_handling():
    """
    展示如何處理常見錯誤

    常見錯誤類型：
    - API Key 錯誤
    - 網絡連接錯誤
    - 模型不可用
    - 輸入驗證錯誤
    """
    print("\n" + "="*80)
    print("範例 7: 錯誤處理")
    print("="*80)

    try:
        # 創建 Agent
        agent = Agent(
            model=OpenAIChat(id="gpt-4"),
            description="測試錯誤處理"
        )

        # 執行任務
        response = agent.run("解釋什麼是 Agno 框架？")
        print(f"\n成功執行！\n回應: {response.content}")

    except Exception as e:
        # 捕獲並處理錯誤
        error_type = type(e).__name__
        print(f"\n❌ 發生錯誤: {error_type}")
        print(f"錯誤訊息: {str(e)}")

        # 根據錯誤類型提供解決方案
        if "API key" in str(e).lower():
            print("\n💡 解決方案: 請檢查 OPENAI_API_KEY 環境變數是否正確設置")
        elif "connection" in str(e).lower():
            print("\n💡 解決方案: 請檢查網絡連接")
        else:
            print("\n💡 解決方案: 請查看完整錯誤堆疊以獲取更多信息")


# ============================================================================
# 範例 8: 使用系統提示詞
# ============================================================================
def example_8_system_prompt():
    """
    展示如何使用系統提示詞定制 Agent 行為

    系統提示詞用於：
    - 定義 Agent 的角色和專業領域
    - 設置輸出格式和風格
    - 限制 Agent 的行為範圍
    """
    print("\n" + "="*80)
    print("範例 8: 使用系統提示詞")
    print("="*80)

    # 創建專業的技術文檔撰寫 Agent
    tech_writer = Agent(
        name="tech_writer",
        role="專業技術文檔撰寫專家",
        model=OpenAIChat(id="gpt-4"),

        # 詳細的系統提示詞
        instructions=[
            "你是一位專業的技術文檔撰寫專家",
            "使用清晰、準確的技術語言",
            "提供結構化的文檔格式",
            "包含程式碼範例和最佳實踐",
            "使用 Markdown 格式輸出",
            "避免過度技術化的術語，保持可讀性"
        ],

        markdown=True
    )

    # 請求撰寫文檔
    query = "請撰寫一個關於如何使用 Python requests 庫發送 HTTP 請求的簡短教程。"
    print(f"\n任務: {query}\n")

    response = tech_writer.run(query)
    print(f"生成的文檔:\n{response.content}")


# ============================================================================
# 範例 9: 流式輸出
# ============================================================================
def example_9_streaming_output():
    """
    展示流式輸出功能

    優點：
    - 即時看到生成過程
    - 降低首字延遲
    - 改善用戶體驗
    """
    print("\n" + "="*80)
    print("範例 9: 流式輸出")
    print("="*80)

    agent = Agent(
        model=OpenAIChat(id="gpt-4"),
        description="支持流式輸出的 Agent"
    )

    query = "用三句話介紹 Agno 框架的主要優勢。"
    print(f"\n提問: {query}\n")
    print("流式輸出: ", end="", flush=True)

    # 使用流式輸出
    response = agent.run(query, stream=True)

    # 逐字輸出
    for chunk in response:
        print(chunk, end="", flush=True)

    print("\n")


# ============================================================================
# 主函數：運行所有範例
# ============================================================================
def main():
    """運行所有基礎範例"""

    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║                  Agno 框架基礎入門教程                         ║
    ║                                                                ║
    ║  本腳本展示 Agno 框架的核心概念和基本用法                      ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

    # 檢查環境變數
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 錯誤: 請設置 OPENAI_API_KEY 環境變數")
        print("\n請在 .env 文件中添加：")
        print("OPENAI_API_KEY=your_api_key_here")
        return

    try:
        # 運行各個範例
        example_1_first_agent()
        example_2_agent_configuration()
        example_3_model_selection()
        example_4_multi_turn_conversation()
        example_5_temperature_control()
        example_6_debugging_and_logging()
        example_7_error_handling()
        example_8_system_prompt()
        example_9_streaming_output()

        print("\n" + "="*80)
        print("✅ 所有範例執行完成！")
        print("="*80)

        print("\n📚 下一步學習：")
        print("- 02_工具使用.py - 學習如何使用內建工具")
        print("- 03_多模態Agent.py - 探索多模態處理能力")
        print("- 04_Agentic_RAG.py - 深入了解智能 RAG 系統")

    except Exception as e:
        print(f"\n❌ 執行過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


# ============================================================================
# 學習要點總結
# ============================================================================
"""
📚 Agno 基礎學習要點：

1. **Agent 創建**
   - 使用 Agent() 類創建
   - 指定 model 參數選擇 LLM
   - 通過 description/role/instructions 定制行為

2. **模型選擇**
   - OpenAIChat: GPT-3.5, GPT-4 系列
   - GroqChat: 超快速推理引擎
   - 根據任務選擇合適的模型

3. **Agent 配置**
   - name: Agent 名稱標識
   - role: 角色定位
   - instructions: 詳細行為指導
   - markdown: 輸出格式
   - debug_mode: 調試模式

4. **對話管理**
   - agent.run() 執行單次對話
   - 自動維護對話歷史
   - 支持多輪上下文理解

5. **溫度控制**
   - temperature=0: 確定性輸出
   - temperature=0.7: 平衡（預設）
   - temperature=1.0+: 高創造性

6. **調試技巧**
   - debug_mode=True: 詳細日誌
   - show_tool_calls=True: 顯示工具調用
   - 使用 logger 自定義日誌

7. **錯誤處理**
   - 使用 try-except 捕獲異常
   - 檢查 API Key 配置
   - 提供友好的錯誤訊息

8. **流式輸出**
   - stream=True 啟用流式輸出
   - 即時顯示生成過程
   - 改善用戶體驗

💡 最佳實踐：
- 為 Agent 提供清晰的角色定位
- 使用 instructions 詳細說明期望行為
- 根據任務選擇合適的模型和溫度
- 實施完善的錯誤處理機制
- 使用調試模式快速定位問題

🔗 相關資源：
- Agno 官方文檔: https://docs.agno.com
- 模型選擇指南: https://docs.agno.com/models
- 最佳實踐: https://docs.agno.com/best-practices

⚡ Agno 的優勢：
- 比 LangGraph 快 529 倍
- 內存使用低 24 倍
- 簡單直觀的 API
- 豐富的模型支持
"""
