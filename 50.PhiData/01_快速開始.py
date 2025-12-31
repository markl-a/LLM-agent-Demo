"""
PhiData 快速開始示例

這個腳本展示了 PhiData 框架的基礎使用方法，包括：
1. 創建基礎 Agent
2. 配置模型參數
3. 設置 Agent 指令
4. 實現對話功能
5. 使用流式輸出
6. 管理對話歷史
7. 自定義 Agent 行為
8. 錯誤處理
9. 性能優化
10. 最佳實踐

作者: PhiData Team
日期: 2025
"""

import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

# PhiData 核心導入
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.utils.log import logger

# 環境變量管理
from dotenv import load_dotenv

# 載入環境變量
load_dotenv()


class PhiDataQuickStart:
    """
    PhiData 快速開始類

    這個類封裝了 PhiData 的基礎功能，提供了簡單易用的接口。
    包含了創建 Agent、配置參數、執行對話等功能。
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 PhiData 快速開始實例

        參數:
            api_key: OpenAI API 密鑰，如果不提供則從環境變量讀取
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("未找到 OPENAI_API_KEY，請設置環境變量或傳入參數")

        # 設置日誌
        logger.info("初始化 PhiData 快速開始示例")

        # Agent 實例將在需要時創建
        self.agent: Optional[Agent] = None
        self.conversation_history: List[Dict[str, Any]] = []

    def create_basic_agent(self) -> Agent:
        """
        創建一個基礎的 Agent

        這是最簡單的 Agent 配置，只包含必要的參數。
        適合快速測試和原型開發。

        返回:
            配置好的 Agent 實例
        """
        logger.info("創建基礎 Agent")

        agent = Agent(
            # 使用的 AI 模型
            model=OpenAIChat(
                id="gpt-4",  # 模型 ID
                api_key=self.api_key,
            ),
            # Agent 描述
            description="一個友好的 AI 助手",
            # 是否使用 Markdown 格式化輸出
            markdown=True,
        )

        return agent

    def create_configured_agent(
        self,
        name: str = "智能助手",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> Agent:
        """
        創建一個配置完整的 Agent

        這個方法展示了如何詳細配置 Agent 的各種參數。

        參數:
            name: Agent 名稱
            temperature: 生成溫度（0-1），越高越隨機
            max_tokens: 最大生成 token 數

        返回:
            配置好的 Agent 實例
        """
        logger.info(f"創建配置 Agent: {name}")

        agent = Agent(
            # Agent 基本信息
            name=name,
            description=f"{name} - 由 PhiData 驅動的智能助手",

            # 模型配置
            model=OpenAIChat(
                id="gpt-4",
                api_key=self.api_key,
                temperature=temperature,  # 控制輸出隨機性
                max_tokens=max_tokens,    # 限制輸出長度
                top_p=0.9,                # 核採樣參數
            ),

            # Agent 指令 - 定義 Agent 的行為
            instructions=[
                "你是一個友好、專業的 AI 助手",
                "始終使用繁體中文回應",
                "提供清晰、準確、有幫助的答案",
                "如果不確定答案，誠實地說明",
                "保持回答簡潔但完整",
            ],

            # 輸出格式
            markdown=True,          # 使用 Markdown 格式
            show_tool_calls=True,   # 顯示工具調用

            # 調試選項
            debug_mode=False,       # 調試模式
        )

        return agent

    def create_agent_with_system_prompt(self, system_prompt: str) -> Agent:
        """
        使用自定義系統提示創建 Agent

        系統提示是定義 Agent 行為的關鍵，它會影響 Agent 的所有回應。

        參數:
            system_prompt: 自定義的系統提示

        返回:
            配置好的 Agent 實例
        """
        logger.info("使用自定義系統提示創建 Agent")

        agent = Agent(
            model=OpenAIChat(
                id="gpt-4",
                api_key=self.api_key,
            ),
            description="自定義行為的 Agent",
            instructions=[system_prompt],
            markdown=True,
        )

        return agent

    def simple_chat(self, agent: Agent, message: str) -> str:
        """
        簡單的對話功能

        發送消息給 Agent 並獲取回應。

        參數:
            agent: Agent 實例
            message: 用戶消息

        返回:
            Agent 的回應文本
        """
        logger.info(f"發送消息: {message[:50]}...")

        # 使用 get_response 獲取回應
        response = agent.run(message)

        # 記錄對話歷史
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user": message,
            "agent": response.content if hasattr(response, 'content') else str(response),
        })

        return response.content if hasattr(response, 'content') else str(response)

    def stream_chat(self, agent: Agent, message: str) -> None:
        """
        流式對話功能

        使用流式輸出，可以實時看到 Agent 的回應過程。
        這提供了更好的用戶體驗，特別是對於長回應。

        參數:
            agent: Agent 實例
            message: 用戶消息
        """
        logger.info(f"開始流式對話: {message[:50]}...")

        print(f"\n用戶: {message}")
        print(f"Agent: ", end="", flush=True)

        # 使用 print_response 進行流式輸出
        agent.print_response(message, stream=True)

        print("\n")  # 換行

    def chat_with_context(
        self,
        agent: Agent,
        message: str,
        context: Optional[str] = None
    ) -> str:
        """
        帶上下文的對話

        在對話中提供額外的上下文信息，幫助 Agent 更好地理解和回應。

        參數:
            agent: Agent 實例
            message: 用戶消息
            context: 上下文信息

        返回:
            Agent 的回應
        """
        logger.info("執行帶上下文的對話")

        # 如果有上下文，將其添加到消息中
        if context:
            full_message = f"上下文信息:\n{context}\n\n用戶問題:\n{message}"
        else:
            full_message = message

        response = agent.run(full_message)
        return response.content if hasattr(response, 'content') else str(response)

    def multi_turn_conversation(
        self,
        agent: Agent,
        messages: List[str]
    ) -> List[str]:
        """
        多輪對話

        執行多輪連續對話，Agent 會記住之前的對話內容。

        參數:
            agent: Agent 實例
            messages: 消息列表

        返回:
            回應列表
        """
        logger.info(f"開始多輪對話，共 {len(messages)} 輪")

        responses = []

        for i, message in enumerate(messages, 1):
            print(f"\n--- 第 {i} 輪對話 ---")
            print(f"用戶: {message}")

            response = agent.run(message)
            response_text = response.content if hasattr(response, 'content') else str(response)

            print(f"Agent: {response_text}")
            responses.append(response_text)

        return responses

    def save_conversation_history(self, filepath: str) -> None:
        """
        保存對話歷史

        將對話歷史保存到 JSON 文件中，便於後續分析和審查。

        參數:
            filepath: 保存路徑
        """
        logger.info(f"保存對話歷史到: {filepath}")

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)

        print(f"對話歷史已保存到: {filepath}")

    def load_conversation_history(self, filepath: str) -> List[Dict[str, Any]]:
        """
        載入對話歷史

        從 JSON 文件載入之前的對話歷史。

        參數:
            filepath: 文件路徑

        返回:
            對話歷史列表
        """
        logger.info(f"載入對話歷史從: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            self.conversation_history = json.load(f)

        return self.conversation_history

    def get_agent_info(self, agent: Agent) -> Dict[str, Any]:
        """
        獲取 Agent 信息

        返回 Agent 的配置和狀態信息。

        參數:
            agent: Agent 實例

        返回:
            Agent 信息字典
        """
        info = {
            "name": agent.name if hasattr(agent, 'name') else "未命名",
            "description": agent.description if hasattr(agent, 'description') else "無描述",
            "model": agent.model.id if hasattr(agent.model, 'id') else "未知",
            "markdown": agent.markdown if hasattr(agent, 'markdown') else False,
        }

        return info


def demonstration_basic_usage():
    """
    演示基礎用法

    這個函數展示了 PhiData 的最基本用法。
    """
    print("\n" + "="*60)
    print("演示 1: 基礎 Agent 使用")
    print("="*60)

    # 創建快速開始實例
    quick_start = PhiDataQuickStart()

    # 創建基礎 Agent
    agent = quick_start.create_basic_agent()

    # 簡單對話
    response = quick_start.simple_chat(
        agent,
        "你好！請用一句話介紹什麼是 PhiData。"
    )
    print(f"\nAgent 回應: {response}")


def demonstration_configured_agent():
    """
    演示配置完整的 Agent

    展示如何創建一個配置詳細的 Agent。
    """
    print("\n" + "="*60)
    print("演示 2: 配置完整的 Agent")
    print("="*60)

    quick_start = PhiDataQuickStart()

    # 創建配置 Agent
    agent = quick_start.create_configured_agent(
        name="專業顧問",
        temperature=0.5,  # 較低的溫度，更確定性的回應
        max_tokens=1000,
    )

    # 顯示 Agent 信息
    info = quick_start.get_agent_info(agent)
    print(f"\nAgent 信息:")
    for key, value in info.items():
        print(f"  {key}: {value}")

    # 對話
    response = quick_start.simple_chat(
        agent,
        "請解釋一下什麼是人工智能中的「溫度」參數？"
    )
    print(f"\nAgent 回應: {response}")


def demonstration_stream_output():
    """
    演示流式輸出

    展示如何使用流式輸出提升用戶體驗。
    """
    print("\n" + "="*60)
    print("演示 3: 流式輸出")
    print("="*60)

    quick_start = PhiDataQuickStart()
    agent = quick_start.create_basic_agent()

    # 流式對話
    quick_start.stream_chat(
        agent,
        "請寫一首關於人工智能的短詩。"
    )


def demonstration_context_chat():
    """
    演示帶上下文的對話

    展示如何在對話中提供上下文信息。
    """
    print("\n" + "="*60)
    print("演示 4: 帶上下文的對話")
    print("="*60)

    quick_start = PhiDataQuickStart()
    agent = quick_start.create_basic_agent()

    # 定義上下文
    context = """
    PhiData 是一個開源的 AI Agent 框架，由 Phidata Inc. 開發。
    它支持多種 AI 模型，包括 OpenAI、Anthropic 等。
    主要特點包括：多 Agent 協作、知識庫集成、工具使用等。
    """

    # 帶上下文對話
    response = quick_start.chat_with_context(
        agent,
        "PhiData 的主要特點是什麼？",
        context=context
    )
    print(f"\n用戶: PhiData 的主要特點是什麼？")
    print(f"Agent: {response}")


def demonstration_multi_turn():
    """
    演示多輪對話

    展示如何進行連續的多輪對話。
    """
    print("\n" + "="*60)
    print("演示 5: 多輪對話")
    print("="*60)

    quick_start = PhiDataQuickStart()
    agent = quick_start.create_basic_agent()

    # 多輪對話
    messages = [
        "我想學習 Python 編程，你有什麼建議嗎？",
        "我應該從哪些基礎概念開始？",
        "有推薦的學習資源嗎？",
    ]

    quick_start.multi_turn_conversation(agent, messages)


def demonstration_custom_system_prompt():
    """
    演示自定義系統提示

    展示如何使用自定義系統提示來定義 Agent 行為。
    """
    print("\n" + "="*60)
    print("演示 6: 自定義系統提示")
    print("="*60)

    quick_start = PhiDataQuickStart()

    # 創建一個專門的技術顧問 Agent
    system_prompt = """
    你是一位資深的軟體工程師和技術顧問，專長於：
    1. 系統架構設計
    2. 代碼質量評審
    3. 性能優化建議
    4. 技術選型指導

    回答問題時，請：
    - 提供具體、可操作的建議
    - 說明技術方案的優缺點
    - 考慮實際應用場景
    - 使用專業但易懂的語言
    """

    agent = quick_start.create_agent_with_system_prompt(system_prompt)

    response = quick_start.simple_chat(
        agent,
        "我正在設計一個電商系統，應該選擇微服務架構還是單體架構？"
    )
    print(f"\nAgent 回應: {response}")


def demonstration_save_and_load():
    """
    演示保存和載入對話歷史

    展示如何持久化對話數據。
    """
    print("\n" + "="*60)
    print("演示 7: 保存和載入對話歷史")
    print("="*60)

    quick_start = PhiDataQuickStart()
    agent = quick_start.create_basic_agent()

    # 進行一些對話
    quick_start.simple_chat(agent, "你好！")
    quick_start.simple_chat(agent, "今天天氣如何？")
    quick_start.simple_chat(agent, "謝謝你的幫助！")

    # 保存對話歷史
    history_file = "conversation_history.json"
    quick_start.save_conversation_history(history_file)

    # 載入對話歷史
    loaded_history = quick_start.load_conversation_history(history_file)

    print(f"\n已載入 {len(loaded_history)} 條對話記錄")
    for i, record in enumerate(loaded_history, 1):
        print(f"\n對話 {i}:")
        print(f"  時間: {record['timestamp']}")
        print(f"  用戶: {record['user']}")
        print(f"  Agent: {record['agent'][:100]}...")  # 只顯示前100字符


def main():
    """
    主函數

    運行所有演示示例。
    """
    print("\n" + "="*60)
    print("PhiData 快速開始 - 完整示例")
    print("="*60)

    try:
        # 運行各個演示
        demonstration_basic_usage()
        demonstration_configured_agent()
        demonstration_stream_output()
        demonstration_context_chat()
        demonstration_multi_turn()
        demonstration_custom_system_prompt()
        demonstration_save_and_load()

        print("\n" + "="*60)
        print("所有演示完成！")
        print("="*60)

        print("\n提示：")
        print("1. 確保設置了 OPENAI_API_KEY 環境變量")
        print("2. 根據需求調整 Agent 配置參數")
        print("3. 查看其他示例文件了解更多功能")
        print("4. 訪問 https://docs.phidata.com 查看完整文檔")

    except Exception as e:
        logger.error(f"運行錯誤: {e}")
        print(f"\n錯誤: {e}")
        print("\n請確認：")
        print("1. 已安裝所有依賴: pip install -r requirements.txt")
        print("2. 已設置 OPENAI_API_KEY 環境變量")
        print("3. API 密鑰有效且有足夠額度")


if __name__ == "__main__":
    main()
