"""
Pydantic AI - 對話歷史範例

本範例展示：
1. 對話上下文管理
2. 歷史記錄存取
3. 多輪對話
4. 上下文窗口控制
5. 對話持久化

對話歷史是實現有狀態對話的關鍵
"""

import asyncio
import json
from typing import Optional
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    UserPromptPart,
    TextPart,
)


# ============================================================================
# 範例 1: 基本多輪對話
# ============================================================================

async def example_1_basic_conversation():
    """最基本的多輪對話"""
    print("\n" + "="*60)
    print("範例 1: 基本多輪對話")
    print("="*60)

    agent = Agent('openai:gpt-4')

    # 第一輪對話
    print("用戶：我最喜歡的顏色是藍色")
    result1 = await agent.run('我最喜歡的顏色是藍色')
    print(f"AI：{result1.data}\n")

    # 第二輪 - 使用歷史記錄
    print("用戶：我剛才說我喜歡什麼顏色？")
    result2 = await agent.run(
        '我剛才說我喜歡什麼顏色？',
        message_history=result1.all_messages()  # 傳入歷史
    )
    print(f"AI：{result2.data}\n")

    # 第三輪 - 繼續對話
    print("用戶：你能推薦一些這個顏色的衣服嗎？")
    result3 = await agent.run(
        '你能推薦一些這個顏色的衣服嗎？',
        message_history=result2.all_messages()  # 使用累積的歷史
    )
    print(f"AI：{result3.data}")


# ============================================================================
# 範例 2: 訪問和檢查消息歷史
# ============================================================================

async def example_2_inspect_history():
    """檢查消息歷史的結構"""
    print("\n" + "="*60)
    print("範例 2: 檢查消息歷史")
    print("="*60)

    agent = Agent('openai:gpt-4')

    # 進行對話
    result = await agent.run('你好，我叫 Alice')

    # 獲取所有消息
    messages = result.all_messages()

    print(f"總消息數：{len(messages)}\n")

    for i, msg in enumerate(messages, 1):
        print(f"消息 {i}：")
        print(f"  類型：{type(msg).__name__}")

        # 根據消息類型顯示內容
        if isinstance(msg, ModelRequest):
            print(f"  角色：用戶請求")
            for part in msg.parts:
                if isinstance(part, UserPromptPart):
                    print(f"  內容：{part.content}")

        elif isinstance(msg, ModelResponse):
            print(f"  角色：AI 回應")
            for part in msg.parts:
                if isinstance(part, TextPart):
                    print(f"  內容：{part.content}")

        print()


# ============================================================================
# 範例 3: 對話管理類
# ============================================================================

class ConversationManager:
    """對話管理器"""

    def __init__(self, agent: Agent):
        self.agent = agent
        self.message_history: list[ModelMessage] = []
        self.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    async def send_message(self, user_message: str) -> str:
        """發送消息並更新歷史"""
        result = await self.agent.run(
            user_message,
            message_history=self.message_history
        )

        # 更新歷史
        self.message_history = result.all_messages()

        return result.data

    def get_message_count(self) -> int:
        """獲取消息數量"""
        return len(self.message_history)

    def clear_history(self):
        """清空歷史"""
        self.message_history = []

    def get_summary(self) -> dict:
        """獲取對話摘要"""
        return {
            "conversation_id": self.conversation_id,
            "message_count": len(self.message_history),
            "started_at": self.conversation_id,
        }


async def example_3_conversation_manager():
    """使用對話管理器"""
    print("\n" + "="*60)
    print("範例 3: 對話管理器")
    print("="*60)

    agent = Agent('openai:gpt-4')
    manager = ConversationManager(agent)

    # 多輪對話
    messages = [
        "你好，我想預訂餐廳",
        "我想訂明天晚上 7 點",
        "2 個人",
        "好的，謝謝"
    ]

    for user_msg in messages:
        print(f"用戶：{user_msg}")
        response = await manager.send_message(user_msg)
        print(f"AI：{response}\n")

    # 顯示摘要
    summary = manager.get_summary()
    print(f"對話摘要：")
    print(f"  ID：{summary['conversation_id']}")
    print(f"  消息數：{summary['message_count']}")


# ============================================================================
# 範例 4: 限制上下文窗口
# ============================================================================

async def example_4_context_window():
    """控制上下文窗口大小"""
    print("\n" + "="*60)
    print("範例 4: 限制上下文窗口")
    print("="*60)

    agent = Agent('openai:gpt-4')

    def limit_messages(
        messages: list[ModelMessage],
        max_messages: int = 10
    ) -> list[ModelMessage]:
        """
        限制消息數量，保留最近的消息

        Args:
            messages: 完整消息歷史
            max_messages: 最大消息數

        Returns:
            截斷後的消息列表
        """
        if len(messages) <= max_messages:
            return messages

        # 保留最近的消息
        return messages[-max_messages:]

    # 模擬長對話
    history = []

    for i in range(1, 16):
        message = f"這是第 {i} 條消息"
        print(f"發送：{message}")

        result = await agent.run(
            message,
            message_history=limit_messages(history, max_messages=6)
        )

        history = result.all_messages()
        print(f"  歷史記錄長度：{len(history)}")

        if i % 5 == 0:
            print()


# ============================================================================
# 範例 5: 對話持久化
# ============================================================================

class ConversationStorage:
    """對話存儲"""

    def __init__(self, storage_dir: str = "./conversations"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

    def save_conversation(
        self,
        conversation_id: str,
        messages: list[ModelMessage]
    ):
        """保存對話"""
        file_path = self.storage_dir / f"{conversation_id}.json"

        # 序列化消息（簡化版本）
        data = {
            "conversation_id": conversation_id,
            "message_count": len(messages),
            "saved_at": datetime.now().isoformat(),
            "messages": [
                self._serialize_message(msg)
                for msg in messages
            ]
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"  ✓ 對話已保存：{file_path}")

    def load_conversation(self, conversation_id: str) -> Optional[dict]:
        """加載對話"""
        file_path = self.storage_dir / f"{conversation_id}.json"

        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"  ✓ 對話已加載：{file_path}")
        return data

    def _serialize_message(self, message: ModelMessage) -> dict:
        """序列化消息（簡化）"""
        msg_dict = {
            "type": type(message).__name__,
            "timestamp": datetime.now().isoformat()
        }

        if isinstance(message, ModelRequest):
            msg_dict["role"] = "user"
            msg_dict["content"] = [
                str(part.content) if hasattr(part, 'content') else str(part)
                for part in message.parts
            ]

        elif isinstance(message, ModelResponse):
            msg_dict["role"] = "assistant"
            msg_dict["content"] = [
                str(part.content) if hasattr(part, 'content') else str(part)
                for part in message.parts
            ]

        return msg_dict


async def example_5_conversation_persistence():
    """持久化對話"""
    print("\n" + "="*60)
    print("範例 5: 對話持久化")
    print("="*60)

    agent = Agent('openai:gpt-4')
    storage = ConversationStorage()

    conversation_id = "conv_" + datetime.now().strftime("%Y%m%d_%H%M%S")

    # 進行對話
    result1 = await agent.run('你好，我是新用戶')
    print(f"用戶：你好，我是新用戶")
    print(f"AI：{result1.data}\n")

    result2 = await agent.run(
        '我想了解你的功能',
        message_history=result1.all_messages()
    )
    print(f"用戶：我想了解你的功能")
    print(f"AI：{result2.data}\n")

    # 保存對話
    storage.save_conversation(conversation_id, result2.all_messages())

    # 模擬加載對話
    print(f"\n載入之前的對話...")
    loaded = storage.load_conversation(conversation_id)

    if loaded:
        print(f"  對話 ID：{loaded['conversation_id']}")
        print(f"  消息數：{loaded['message_count']}")
        print(f"  保存時間：{loaded['saved_at']}")


# ============================================================================
# 範例 6: 帶摘要的長對話
# ============================================================================

async def example_6_conversation_with_summary():
    """長對話使用摘要來節省 tokens"""
    print("\n" + "="*60)
    print("範例 6: 帶摘要的長對話")
    print("="*60)

    agent = Agent('openai:gpt-4')
    summarizer = Agent('openai:gpt-3.5-turbo')

    async def create_summary(messages: list[ModelMessage]) -> str:
        """創建對話摘要"""
        # 提取對話內容
        conversation_text = []

        for msg in messages:
            if isinstance(msg, ModelRequest):
                for part in msg.parts:
                    if hasattr(part, 'content'):
                        conversation_text.append(f"用戶：{part.content}")

            elif isinstance(msg, ModelResponse):
                for part in msg.parts:
                    if hasattr(part, 'content'):
                        conversation_text.append(f"AI：{part.content}")

        # 生成摘要
        full_text = "\n".join(conversation_text)
        summary_result = await summarizer.run(
            f"請用一段話總結以下對話：\n\n{full_text}"
        )

        return summary_result.data

    # 進行多輪對話
    history = []

    conversations = [
        "我想買一台筆記本電腦",
        "預算大概 3 萬左右",
        "主要用來寫程式和處理數據",
    ]

    for msg in conversations:
        print(f"用戶：{msg}")
        result = await agent.run(msg, message_history=history)
        print(f"AI：{result.data}\n")
        history = result.all_messages()

    # 當對話太長時，創建摘要
    if len(history) > 4:
        print("📝 創建對話摘要...")
        summary = await create_summary(history)
        print(f"摘要：{summary}\n")

        # 使用摘要作為上下文繼續對話
        print("用戶：根據我的需求，你推薦什麼配置？")
        result = await agent.run(
            f"根據以下對話摘要回答：{summary}\n\n問題：根據我的需求，你推薦什麼配置？"
        )
        print(f"AI：{result.data}")


# ============================================================================
# 範例 7: 多會話管理
# ============================================================================

class SessionManager:
    """會話管理器"""

    def __init__(self, agent: Agent):
        self.agent = agent
        self.sessions: dict[str, list[ModelMessage]] = {}

    async def send_message(
        self,
        session_id: str,
        message: str
    ) -> str:
        """向指定會話發送消息"""
        # 獲取或創建會話
        if session_id not in self.sessions:
            self.sessions[session_id] = []

        # 運行 Agent
        result = await self.agent.run(
            message,
            message_history=self.sessions[session_id]
        )

        # 更新會話歷史
        self.sessions[session_id] = result.all_messages()

        return result.data

    def get_session_count(self) -> int:
        """獲取會話數量"""
        return len(self.sessions)

    def get_session_info(self, session_id: str) -> dict:
        """獲取會話信息"""
        if session_id not in self.sessions:
            return {"exists": False}

        return {
            "exists": True,
            "message_count": len(self.sessions[session_id])
        }


async def example_7_multi_session():
    """管理多個會話"""
    print("\n" + "="*60)
    print("範例 7: 多會話管理")
    print("="*60)

    agent = Agent('openai:gpt-4')
    manager = SessionManager(agent)

    # 會話 1
    print("=== 會話 1 ===")
    response = await manager.send_message("session_1", "我喜歡貓")
    print(f"用戶：我喜歡貓")
    print(f"AI：{response}\n")

    # 會話 2
    print("=== 會話 2 ===")
    response = await manager.send_message("session_2", "我喜歡狗")
    print(f"用戶：我喜歡狗")
    print(f"AI：{response}\n")

    # 回到會話 1
    print("=== 回到會話 1 ===")
    response = await manager.send_message("session_1", "我剛才說我喜歡什麼？")
    print(f"用戶：我剛才說我喜歡什麼？")
    print(f"AI：{response}\n")

    # 回到會話 2
    print("=== 回到會話 2 ===")
    response = await manager.send_message("session_2", "我剛才說我喜歡什麼？")
    print(f"用戶：我剛才說我喜歡什麼？")
    print(f"AI：{response}\n")

    print(f"總會話數：{manager.get_session_count()}")


# ============================================================================
# 主程式
# ============================================================================

async def main():
    """運行所有範例"""
    print("\n" + "💬 " + "="*58)
    print("Pydantic AI - 對話歷史範例")
    print("="*60)

    await example_1_basic_conversation()
    await example_2_inspect_history()
    await example_3_conversation_manager()
    await example_4_context_window()
    await example_5_conversation_persistence()
    await example_6_conversation_with_summary()
    await example_7_multi_session()

    print("\n" + "="*60)
    print("✓ 對話歷史範例完成！")
    print("💡 對話管理技巧：")
    print("   1. 合理限制上下文窗口")
    print("   2. 使用摘要處理長對話")
    print("   3. 持久化重要對話")
    print("   4. 支持多會話並行")
    print("="*60)


if __name__ == '__main__':
    import os
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  請設置 OPENAI_API_KEY 環境變量")
    else:
        asyncio.run(main())
