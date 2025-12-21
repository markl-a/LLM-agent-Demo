"""
Dify 對話應用範例
================

本範例展示如何使用 Dify 構建對話型應用（聊天機器人）。

對話應用特點：
1. 支持多輪對話記憶
2. 可配置對話變數
3. 支持流式響應
4. 內建對話管理

安裝依賴：
pip install requests
"""

import os
import json
import requests
import time
from typing import Dict, Any, Optional, Generator, List
from dataclasses import dataclass, field
from datetime import datetime

# ============================================================
# 配置
# ============================================================

DIFY_API_KEY = os.getenv("DIFY_API_KEY", "app-xxxxxxxxxxxxxxxx")
DIFY_BASE_URL = os.getenv("DIFY_BASE_URL", "https://api.dify.ai/v1")


# ============================================================
# 對話應用客戶端
# ============================================================

class DifyChatClient:
    """
    Dify 對話應用客戶端

    提供完整的對話功能，包括對話管理、消息收發等
    """

    def __init__(self, api_key: str, base_url: str = "https://api.dify.ai/v1"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def send_message(
        self,
        query: str,
        user: str,
        conversation_id: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
        files: Optional[List[Dict[str, str]]] = None,
        auto_generate_name: bool = True
    ) -> Dict[str, Any]:
        """
        發送對話消息（阻塞模式）

        Args:
            query: 用戶輸入
            user: 用戶標識
            conversation_id: 對話 ID
            inputs: 變數輸入
            files: 文件列表
            auto_generate_name: 自動生成對話名稱

        Returns:
            對話響應
        """
        url = f"{self.base_url}/chat-messages"

        payload = {
            "query": query,
            "user": user,
            "response_mode": "blocking",
            "inputs": inputs or {},
            "auto_generate_name": auto_generate_name
        }

        if conversation_id:
            payload["conversation_id"] = conversation_id

        if files:
            payload["files"] = files

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()

        return response.json()

    def send_message_stream(
        self,
        query: str,
        user: str,
        conversation_id: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        發送對話消息（流式模式）

        Args:
            query: 用戶輸入
            user: 用戶標識
            conversation_id: 對話 ID
            inputs: 變數輸入

        Yields:
            流式事件
        """
        url = f"{self.base_url}/chat-messages"

        payload = {
            "query": query,
            "user": user,
            "response_mode": "streaming",
            "inputs": inputs or {}
        }

        if conversation_id:
            payload["conversation_id"] = conversation_id

        response = requests.post(
            url,
            headers=self.headers,
            json=payload,
            stream=True
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    try:
                        yield json.loads(line[6:])
                    except json.JSONDecodeError:
                        continue

    def stop_generation(
        self,
        task_id: str,
        user: str
    ) -> Dict[str, Any]:
        """
        停止生成

        Args:
            task_id: 任務 ID
            user: 用戶標識

        Returns:
            停止結果
        """
        url = f"{self.base_url}/chat-messages/{task_id}/stop"

        payload = {"user": user}

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()

        return response.json()

    def get_conversations(
        self,
        user: str,
        last_id: Optional[str] = None,
        limit: int = 20,
        pinned: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        獲取對話列表

        Args:
            user: 用戶標識
            last_id: 最後一個對話 ID
            limit: 返回數量
            pinned: 是否置頂

        Returns:
            對話列表
        """
        url = f"{self.base_url}/conversations"

        params = {
            "user": user,
            "limit": limit
        }

        if last_id:
            params["last_id"] = last_id
        if pinned is not None:
            params["pinned"] = pinned

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        return response.json()

    def get_messages(
        self,
        conversation_id: str,
        user: str,
        first_id: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        獲取對話消息歷史

        Args:
            conversation_id: 對話 ID
            user: 用戶標識
            first_id: 第一條消息 ID
            limit: 返回數量

        Returns:
            消息列表
        """
        url = f"{self.base_url}/messages"

        params = {
            "conversation_id": conversation_id,
            "user": user,
            "limit": limit
        }

        if first_id:
            params["first_id"] = first_id

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        return response.json()

    def rename_conversation(
        self,
        conversation_id: str,
        user: str,
        name: str,
        auto_generate: bool = False
    ) -> Dict[str, Any]:
        """
        重命名對話

        Args:
            conversation_id: 對話 ID
            user: 用戶標識
            name: 新名稱
            auto_generate: 自動生成名稱

        Returns:
            更新結果
        """
        url = f"{self.base_url}/conversations/{conversation_id}/name"

        payload = {
            "user": user,
            "name": name,
            "auto_generate": auto_generate
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()

        return response.json()

    def delete_conversation(
        self,
        conversation_id: str,
        user: str
    ) -> bool:
        """
        刪除對話

        Args:
            conversation_id: 對話 ID
            user: 用戶標識

        Returns:
            是否成功
        """
        url = f"{self.base_url}/conversations/{conversation_id}"

        payload = {"user": user}

        response = requests.delete(url, headers=self.headers, json=payload)
        response.raise_for_status()

        return True

    def message_feedback(
        self,
        message_id: str,
        user: str,
        rating: str,
        content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        消息反饋

        Args:
            message_id: 消息 ID
            user: 用戶標識
            rating: 評分 (like/dislike/null)
            content: 反饋內容

        Returns:
            反饋結果
        """
        url = f"{self.base_url}/messages/{message_id}/feedbacks"

        payload = {
            "user": user,
            "rating": rating
        }

        if content:
            payload["content"] = content

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()

        return response.json()

    def get_suggested_questions(
        self,
        message_id: str,
        user: str
    ) -> Dict[str, Any]:
        """
        獲取建議問題

        Args:
            message_id: 消息 ID
            user: 用戶標識

        Returns:
            建議問題列表
        """
        url = f"{self.base_url}/messages/{message_id}/suggested"

        params = {"user": user}

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        return response.json()


# ============================================================
# 對話管理器
# ============================================================

@dataclass
class Message:
    """消息數據類"""
    id: str
    role: str  # user/assistant
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Conversation:
    """對話數據類"""
    id: str
    name: str
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class ChatManager:
    """
    對話管理器

    管理多個對話會話，提供高級對話功能
    """

    def __init__(self, client: DifyChatClient, user: str):
        self.client = client
        self.user = user
        self.conversations: Dict[str, Conversation] = {}
        self.current_conversation_id: Optional[str] = None

    def start_new_conversation(
        self,
        initial_message: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        開始新對話

        Args:
            initial_message: 初始消息
            inputs: 初始變數

        Returns:
            對話 ID
        """
        if initial_message:
            response = self.client.send_message(
                query=initial_message,
                user=self.user,
                inputs=inputs
            )

            conv_id = response.get('conversation_id')

            self.conversations[conv_id] = Conversation(
                id=conv_id,
                name=initial_message[:30],
                messages=[
                    Message(
                        id=response.get('message_id', ''),
                        role='user',
                        content=initial_message
                    ),
                    Message(
                        id=response.get('message_id', ''),
                        role='assistant',
                        content=response.get('answer', '')
                    )
                ]
            )

            self.current_conversation_id = conv_id
            return conv_id
        else:
            # 創建空對話，等待第一條消息
            self.current_conversation_id = None
            return ""

    def send(
        self,
        message: str,
        stream: bool = False
    ) -> str:
        """
        發送消息到當前對話

        Args:
            message: 消息內容
            stream: 是否使用流式響應

        Returns:
            助手回覆
        """
        if stream:
            return self._send_stream(message)
        else:
            return self._send_blocking(message)

    def _send_blocking(self, message: str) -> str:
        """阻塞模式發送"""
        response = self.client.send_message(
            query=message,
            user=self.user,
            conversation_id=self.current_conversation_id
        )

        conv_id = response.get('conversation_id')

        # 更新對話記錄
        if conv_id not in self.conversations:
            self.conversations[conv_id] = Conversation(
                id=conv_id,
                name=message[:30]
            )

        self.current_conversation_id = conv_id

        self.conversations[conv_id].messages.extend([
            Message(id=response.get('message_id', ''), role='user', content=message),
            Message(id=response.get('message_id', ''), role='assistant', content=response.get('answer', ''))
        ])

        return response.get('answer', '')

    def _send_stream(self, message: str) -> str:
        """流式模式發送"""
        full_response = []
        conv_id = None

        print("助手: ", end="", flush=True)

        for event in self.client.send_message_stream(
            query=message,
            user=self.user,
            conversation_id=self.current_conversation_id
        ):
            event_type = event.get('event')

            if event_type == 'message':
                chunk = event.get('answer', '')
                print(chunk, end="", flush=True)
                full_response.append(chunk)

            elif event_type == 'message_end':
                conv_id = event.get('conversation_id')

        print()  # 換行

        answer = ''.join(full_response)

        if conv_id:
            if conv_id not in self.conversations:
                self.conversations[conv_id] = Conversation(
                    id=conv_id,
                    name=message[:30]
                )

            self.current_conversation_id = conv_id

            self.conversations[conv_id].messages.extend([
                Message(id='', role='user', content=message),
                Message(id='', role='assistant', content=answer)
            ])

        return answer

    def switch_conversation(self, conversation_id: str):
        """切換對話"""
        self.current_conversation_id = conversation_id

    def get_history(self) -> List[Message]:
        """獲取當前對話歷史"""
        if self.current_conversation_id and self.current_conversation_id in self.conversations:
            return self.conversations[self.current_conversation_id].messages
        return []


# ============================================================
# 使用範例
# ============================================================

def example_basic_chat():
    """
    範例 1: 基礎對話

    展示簡單的對話流程
    """
    print("=" * 50)
    print("範例 1: 基礎對話")
    print("=" * 50)

    client = DifyChatClient(api_key=DIFY_API_KEY, base_url=DIFY_BASE_URL)

    try:
        # 發送第一條消息
        response = client.send_message(
            query="你好，請介紹一下你自己",
            user="user-001"
        )

        print(f"助手: {response.get('answer', '')}")
        print(f"對話 ID: {response.get('conversation_id')}")

        # 繼續對話
        conv_id = response.get('conversation_id')
        response2 = client.send_message(
            query="你能幫我做什麼？",
            user="user-001",
            conversation_id=conv_id
        )

        print(f"助手: {response2.get('answer', '')}")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_streaming_chat():
    """
    範例 2: 流式對話

    展示流式響應的對話
    """
    print("\n" + "=" * 50)
    print("範例 2: 流式對話")
    print("=" * 50)

    client = DifyChatClient(api_key=DIFY_API_KEY, base_url=DIFY_BASE_URL)

    try:
        print("助手: ", end="", flush=True)

        conversation_id = None

        for event in client.send_message_stream(
            query="請用一段話介紹人工智能的發展歷史",
            user="user-002"
        ):
            event_type = event.get('event')

            if event_type == 'message':
                print(event.get('answer', ''), end="", flush=True)

            elif event_type == 'message_end':
                conversation_id = event.get('conversation_id')
                print()  # 換行
                print(f"\n[對話 ID: {conversation_id}]")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_with_variables():
    """
    範例 3: 帶變數的對話

    展示如何使用對話變數
    """
    print("\n" + "=" * 50)
    print("範例 3: 帶變數的對話")
    print("=" * 50)

    client = DifyChatClient(api_key=DIFY_API_KEY, base_url=DIFY_BASE_URL)

    try:
        # 假設應用配置了 language 和 style 變數
        response = client.send_message(
            query="幫我寫一首詩",
            user="user-003",
            inputs={
                "language": "繁體中文",
                "style": "唐詩風格",
                "theme": "春天"
            }
        )

        print(f"助手: {response.get('answer', '')}")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_conversation_management():
    """
    範例 4: 對話管理

    展示如何管理對話列表
    """
    print("\n" + "=" * 50)
    print("範例 4: 對話管理")
    print("=" * 50)

    client = DifyChatClient(api_key=DIFY_API_KEY, base_url=DIFY_BASE_URL)
    user = "user-004"

    try:
        # 獲取對話列表
        conversations = client.get_conversations(user=user, limit=5)

        print(f"共有 {conversations.get('has_more', False) and '更多' or len(conversations.get('data', []))} 個對話")

        for conv in conversations.get('data', [])[:3]:
            print(f"  - {conv.get('id')}: {conv.get('name', '未命名')}")

            # 獲取對話消息
            messages = client.get_messages(
                conversation_id=conv.get('id'),
                user=user,
                limit=3
            )

            for msg in messages.get('data', []):
                print(f"      Q: {msg.get('query', '')[:30]}...")
                print(f"      A: {msg.get('answer', '')[:30]}...")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_message_feedback():
    """
    範例 5: 消息反饋

    展示如何對消息進行評價
    """
    print("\n" + "=" * 50)
    print("範例 5: 消息反饋")
    print("=" * 50)

    client = DifyChatClient(api_key=DIFY_API_KEY, base_url=DIFY_BASE_URL)
    user = "user-005"

    try:
        # 發送消息
        response = client.send_message(
            query="什麼是機器學習？",
            user=user
        )

        message_id = response.get('message_id')
        print(f"助手: {response.get('answer', '')[:100]}...")

        # 給予反饋
        feedback = client.message_feedback(
            message_id=message_id,
            user=user,
            rating="like",
            content="回答很清晰易懂"
        )

        print(f"\n已提交反饋: {feedback}")

        # 獲取建議問題
        suggested = client.get_suggested_questions(
            message_id=message_id,
            user=user
        )

        print(f"建議問題: {suggested.get('data', [])}")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_chat_manager():
    """
    範例 6: 使用對話管理器

    展示高級對話管理功能
    """
    print("\n" + "=" * 50)
    print("範例 6: 使用對話管理器")
    print("=" * 50)

    client = DifyChatClient(api_key=DIFY_API_KEY, base_url=DIFY_BASE_URL)
    manager = ChatManager(client, user="user-006")

    try:
        # 開始新對話
        print("開始新對話...")
        manager.start_new_conversation("你好，我想學習 Python 編程")

        # 繼續對話
        print("\n繼續對話...")
        response = manager.send("從哪裡開始學比較好？")
        print(f"助手: {response[:100]}...")

        # 查看歷史
        print("\n對話歷史:")
        for msg in manager.get_history():
            print(f"  [{msg.role}]: {msg.content[:50]}...")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_interactive_chat():
    """
    範例 7: 互動對話

    模擬完整的互動對話流程
    """
    print("\n" + "=" * 50)
    print("範例 7: 互動對話（模擬）")
    print("=" * 50)

    client = DifyChatClient(api_key=DIFY_API_KEY, base_url=DIFY_BASE_URL)
    user = "user-007"

    # 模擬用戶輸入
    user_inputs = [
        "你好！",
        "我想了解如何使用 Dify 構建 AI 應用",
        "能給我一個簡單的例子嗎？",
        "謝謝你的幫助！"
    ]

    conversation_id = None

    try:
        for user_input in user_inputs:
            print(f"\n用戶: {user_input}")

            response = client.send_message(
                query=user_input,
                user=user,
                conversation_id=conversation_id
            )

            conversation_id = response.get('conversation_id')
            print(f"助手: {response.get('answer', '')}")

            time.sleep(0.5)  # 模擬對話間隔

        print(f"\n對話完成，對話 ID: {conversation_id}")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    print("Dify 對話應用範例")
    print("請確保已設置 DIFY_API_KEY 環境變數")
    print()

    example_basic_chat()
    example_streaming_chat()
    example_with_variables()
    example_conversation_management()
    example_message_feedback()
    example_chat_manager()
    example_interactive_chat()
