"""
Strands Agents 對話記憶管理示例

這個示例展示了如何在 Strands Agents 中管理對話記憶：
1. 基本的對話歷史記錄
2. 滑動窗口記憶策略
3. 摘要記憶（Summary Memory）
4. 向量記憶（Vector Memory）
5. 實體記憶（Entity Memory）
6. 持久化和恢復
7. 記憶優化策略
8. 多會話管理

良好的記憶管理是構建智能對話 Agent 的核心，
它使 Agent 能夠理解上下文並保持連貫的對話。

作者: Strands Agents Team
日期: 2025-01
"""

import os
import sys
import json
import pickle
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from collections import deque
import hashlib

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# 基礎數據結構
# ============================================================================

@dataclass
class Message:
    """
    對話消息

    Attributes:
        role: 角色（user, assistant, system）
        content: 消息內容
        timestamp: 時間戳
        metadata: 元數據
    """
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """從字典創建"""
        data = data.copy()
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

    def __len__(self) -> int:
        """返回消息的 token 數量估計"""
        # 簡單估計：1個中文字符約等於1.5個token，英文單詞約1個token
        chinese_chars = sum(1 for c in self.content if '\u4e00' <= c <= '\u9fff')
        english_words = len(self.content.split()) - chinese_chars
        return int(chinese_chars * 1.5 + english_words)


@dataclass
class ConversationSummary:
    """
    對話摘要

    Attributes:
        summary: 摘要文本
        message_count: 被摘要的消息數量
        start_time: 開始時間
        end_time: 結束時間
    """
    summary: str
    message_count: int
    start_time: datetime
    end_time: datetime

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "summary": self.summary,
            "message_count": self.message_count,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat()
        }


# ============================================================================
# 記憶策略基類
# ============================================================================

class BaseMemory(ABC):
    """
    記憶策略基類

    所有記憶策略都應繼承此類並實現相應方法
    """

    @abstractmethod
    def add_message(self, message: Message):
        """添加消息到記憶"""
        pass

    @abstractmethod
    def get_messages(self) -> List[Message]:
        """獲取所有記憶中的消息"""
        pass

    @abstractmethod
    def clear(self):
        """清空記憶"""
        pass

    def add_user_message(self, content: str, metadata: Optional[Dict] = None):
        """添加用戶消息"""
        message = Message(
            role="user",
            content=content,
            metadata=metadata or {}
        )
        self.add_message(message)

    def add_assistant_message(self, content: str, metadata: Optional[Dict] = None):
        """添加助手消息"""
        message = Message(
            role="assistant",
            content=content,
            metadata=metadata or {}
        )
        self.add_message(message)

    def get_context_string(self) -> str:
        """獲取格式化的上下文字符串"""
        messages = self.get_messages()
        context_parts = []

        for msg in messages:
            role_name = "用戶" if msg.role == "user" else "助手"
            context_parts.append(f"{role_name}: {msg.content}")

        return "\n".join(context_parts)


# ============================================================================
# 簡單記憶策略
# ============================================================================

class SimpleMemory(BaseMemory):
    """
    簡單記憶策略

    保存所有對話歷史，不做任何限制。
    適用於短對話場景。
    """

    def __init__(self):
        self.messages: List[Message] = []
        logger.info("初始化簡單記憶策略")

    def add_message(self, message: Message):
        """添加消息"""
        self.messages.append(message)
        logger.debug(f"添加消息: {message.role} - {len(message.content)} 字符")

    def get_messages(self) -> List[Message]:
        """獲取所有消息"""
        return self.messages.copy()

    def clear(self):
        """清空記憶"""
        count = len(self.messages)
        self.messages.clear()
        logger.info(f"清空記憶，刪除了 {count} 條消息")

    def get_token_count(self) -> int:
        """獲取總 token 數量估計"""
        return sum(len(msg) for msg in self.messages)


# ============================================================================
# 滑動窗口記憶策略
# ============================================================================

class WindowMemory(BaseMemory):
    """
    滑動窗口記憶策略

    只保留最近的 N 條消息，適用於長對話場景。

    Attributes:
        window_size: 窗口大小（消息數量）
        keep_system: 是否保留系統消息
    """

    def __init__(self, window_size: int = 10, keep_system: bool = True):
        self.window_size = window_size
        self.keep_system = keep_system
        self.messages: deque = deque(maxlen=window_size)
        self.system_messages: List[Message] = []

        logger.info(f"初始化滑動窗口記憶策略: window_size={window_size}")

    def add_message(self, message: Message):
        """添加消息"""
        if message.role == "system" and self.keep_system:
            self.system_messages.append(message)
        else:
            self.messages.append(message)

        logger.debug(f"添加消息到窗口: {message.role}")

    def get_messages(self) -> List[Message]:
        """獲取消息（系統消息 + 窗口消息）"""
        return self.system_messages + list(self.messages)

    def clear(self):
        """清空記憶"""
        self.messages.clear()
        self.system_messages.clear()
        logger.info("清空窗口記憶")

    def get_overflow_count(self) -> int:
        """獲取被移除的消息數量估計"""
        # 這個方法在實際實現中需要追蹤歷史
        return 0


# ============================================================================
# Token 限制記憶策略
# ============================================================================

class TokenBufferMemory(BaseMemory):
    """
    Token 限制記憶策略

    根據 token 數量限制來管理記憶，而不是消息數量。
    當超過限制時，自動刪除最早的消息。

    Attributes:
        max_tokens: 最大 token 數量
    """

    def __init__(self, max_tokens: int = 2000):
        self.max_tokens = max_tokens
        self.messages: List[Message] = []
        self.current_tokens = 0

        logger.info(f"初始化 Token 限制記憶策略: max_tokens={max_tokens}")

    def add_message(self, message: Message):
        """添加消息"""
        message_tokens = len(message)
        self.messages.append(message)
        self.current_tokens += message_tokens

        # 如果超過限制，移除最早的消息
        while self.current_tokens > self.max_tokens and len(self.messages) > 1:
            removed = self.messages.pop(0)
            self.current_tokens -= len(removed)
            logger.debug(f"移除舊消息以保持 token 限制")

        logger.debug(f"當前 tokens: {self.current_tokens}/{self.max_tokens}")

    def get_messages(self) -> List[Message]:
        """獲取所有消息"""
        return self.messages.copy()

    def clear(self):
        """清空記憶"""
        self.messages.clear()
        self.current_tokens = 0
        logger.info("清空 Token 限制記憶")

    def get_available_tokens(self) -> int:
        """獲取可用的 token 數量"""
        return self.max_tokens - self.current_tokens


# ============================================================================
# 摘要記憶策略
# ============================================================================

class SummaryMemory(BaseMemory):
    """
    摘要記憶策略

    將舊的對話壓縮成摘要，只保留最近的詳細消息。
    適用於超長對話場景。

    Attributes:
        max_messages: 保留的最大詳細消息數量
        summary_threshold: 觸發摘要的消息數量閾值
    """

    def __init__(
        self,
        max_messages: int = 20,
        summary_threshold: int = 30
    ):
        self.max_messages = max_messages
        self.summary_threshold = summary_threshold
        self.messages: List[Message] = []
        self.summaries: List[ConversationSummary] = []

        logger.info(
            f"初始化摘要記憶策略: max_messages={max_messages}, "
            f"threshold={summary_threshold}"
        )

    def add_message(self, message: Message):
        """添加消息"""
        self.messages.append(message)

        # 檢查是否需要生成摘要
        if len(self.messages) >= self.summary_threshold:
            self._create_summary()

    def _create_summary(self):
        """創建摘要"""
        # 計算需要摘要的消息數量
        num_to_summarize = len(self.messages) - self.max_messages

        if num_to_summarize <= 0:
            return

        # 獲取要摘要的消息
        messages_to_summarize = self.messages[:num_to_summarize]

        # 生成摘要（這裡是簡化版本，實際應使用 LLM）
        summary_text = self._generate_summary(messages_to_summarize)

        # 創建摘要對象
        summary = ConversationSummary(
            summary=summary_text,
            message_count=num_to_summarize,
            start_time=messages_to_summarize[0].timestamp,
            end_time=messages_to_summarize[-1].timestamp
        )

        self.summaries.append(summary)

        # 移除已摘要的消息
        self.messages = self.messages[num_to_summarize:]

        logger.info(f"創建摘要，壓縮了 {num_to_summarize} 條消息")

    def _generate_summary(self, messages: List[Message]) -> str:
        """
        生成摘要文本

        實際應用中應該調用 LLM 來生成更智能的摘要
        """
        # 簡化的摘要生成
        user_messages = [m for m in messages if m.role == "user"]
        assistant_messages = [m for m in messages if m.role == "assistant"]

        summary_parts = [
            f"對話包含 {len(user_messages)} 條用戶消息和 "
            f"{len(assistant_messages)} 條助手回復。"
        ]

        # 添加一些關鍵信息
        if user_messages:
            first_user_msg = user_messages[0].content[:50]
            summary_parts.append(f"對話開始於: {first_user_msg}...")

        return " ".join(summary_parts)

    def get_messages(self) -> List[Message]:
        """獲取消息（包含摘要作為系統消息）"""
        result = []

        # 添加摘要作為系統消息
        for summary in self.summaries:
            result.append(Message(
                role="system",
                content=f"[對話摘要] {summary.summary}",
                timestamp=summary.end_time
            ))

        # 添加詳細消息
        result.extend(self.messages)

        return result

    def clear(self):
        """清空記憶"""
        self.messages.clear()
        self.summaries.clear()
        logger.info("清空摘要記憶")


# ============================================================================
# 實體記憶策略
# ============================================================================

class EntityMemory(BaseMemory):
    """
    實體記憶策略

    提取和記住對話中提到的實體（人物、地點、事件等），
    提供基於實體的上下文檢索。

    Attributes:
        entities: 實體字典
        messages: 消息列表
    """

    def __init__(self):
        self.messages: List[Message] = []
        self.entities: Dict[str, Dict[str, Any]] = {}

        logger.info("初始化實體記憶策略")

    def add_message(self, message: Message):
        """添加消息並提取實體"""
        self.messages.append(message)

        # 提取實體
        entities = self._extract_entities(message.content)

        for entity_name, entity_info in entities.items():
            if entity_name not in self.entities:
                self.entities[entity_name] = {
                    "name": entity_name,
                    "type": entity_info["type"],
                    "mentions": [],
                    "attributes": {}
                }

            self.entities[entity_name]["mentions"].append({
                "message_index": len(self.messages) - 1,
                "timestamp": message.timestamp,
                "context": message.content[:100]
            })

            # 更新屬性
            if "attributes" in entity_info:
                self.entities[entity_name]["attributes"].update(
                    entity_info["attributes"]
                )

        logger.debug(f"提取到 {len(entities)} 個實體")

    def _extract_entities(self, text: str) -> Dict[str, Dict[str, Any]]:
        """
        提取文本中的實體

        簡化版本，實際應使用 NER 模型
        """
        entities = {}

        # 簡單的關鍵字匹配（實際應使用 NLP 工具）
        keywords = {
            "人物": ["張三", "李四", "王五", "用戶", "客戶"],
            "地點": ["台北", "台中", "高雄", "辦公室", "會議室"],
            "產品": ["產品", "服務", "系統", "平台"],
            "時間": ["今天", "明天", "下週", "本月"]
        }

        for entity_type, keywords_list in keywords.items():
            for keyword in keywords_list:
                if keyword in text:
                    entities[keyword] = {
                        "type": entity_type,
                        "attributes": {}
                    }

        return entities

    def get_messages(self) -> List[Message]:
        """獲取所有消息"""
        return self.messages.copy()

    def get_entity_context(self, entity_name: str) -> Optional[Dict[str, Any]]:
        """獲取特定實體的上下文"""
        return self.entities.get(entity_name)

    def search_by_entity(self, entity_name: str) -> List[Message]:
        """根據實體搜索相關消息"""
        if entity_name not in self.entities:
            return []

        entity_info = self.entities[entity_name]
        relevant_messages = []

        for mention in entity_info["mentions"]:
            msg_index = mention["message_index"]
            if msg_index < len(self.messages):
                relevant_messages.append(self.messages[msg_index])

        return relevant_messages

    def clear(self):
        """清空記憶"""
        self.messages.clear()
        self.entities.clear()
        logger.info("清空實體記憶")


# ============================================================================
# 持久化記憶管理
# ============================================================================

class PersistentMemory:
    """
    持久化記憶管理

    支援記憶的保存和恢復

    Attributes:
        memory: 底層記憶策略
        storage_path: 存儲路徑
    """

    def __init__(self, memory: BaseMemory, storage_path: str = "./memory_storage"):
        self.memory = memory
        self.storage_path = storage_path

        # 創建存儲目錄
        os.makedirs(storage_path, exist_ok=True)

        logger.info(f"初始化持久化記憶管理: {storage_path}")

    def save(self, session_id: str):
        """
        保存記憶到文件

        Args:
            session_id: 會話 ID
        """
        messages = self.memory.get_messages()

        # 轉換為可序列化格式
        data = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "message_count": len(messages),
            "messages": [msg.to_dict() for msg in messages]
        }

        # 保存到文件
        file_path = os.path.join(self.storage_path, f"{session_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"保存記憶到 {file_path}: {len(messages)} 條消息")

    def load(self, session_id: str) -> bool:
        """
        從文件恢復記憶

        Args:
            session_id: 會話 ID

        Returns:
            bool: 是否成功恢復
        """
        file_path = os.path.join(self.storage_path, f"{session_id}.json")

        if not os.path.exists(file_path):
            logger.warning(f"記憶文件不存在: {file_path}")
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 清空現有記憶
            self.memory.clear()

            # 恢復消息
            for msg_data in data["messages"]:
                message = Message.from_dict(msg_data)
                self.memory.add_message(message)

            logger.info(f"恢復記憶: {len(data['messages'])} 條消息")
            return True

        except Exception as e:
            logger.error(f"恢復記憶失敗: {str(e)}")
            return False

    def list_sessions(self) -> List[str]:
        """列出所有保存的會話"""
        sessions = []
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                session_id = filename[:-5]  # 移除 .json
                sessions.append(session_id)

        return sessions

    def delete_session(self, session_id: str) -> bool:
        """刪除會話記憶"""
        file_path = os.path.join(self.storage_path, f"{session_id}.json")

        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"刪除會話記憶: {session_id}")
            return True

        return False


# ============================================================================
# 示例和測試
# ============================================================================

def demonstrate_simple_memory():
    """演示簡單記憶"""
    print("\n" + "="*60)
    print("示例 1: 簡單記憶策略")
    print("="*60 + "\n")

    memory = SimpleMemory()

    # 添加對話
    memory.add_user_message("你好，我是新用戶")
    memory.add_assistant_message("您好！很高興為您服務。")
    memory.add_user_message("我想了解 Strands Agents")
    memory.add_assistant_message("Strands Agents 是 AWS 推出的企業級 AI Agent SDK。")

    # 獲取消息
    messages = memory.get_messages()
    print(f"總消息數: {len(messages)}")
    print(f"總 token 數（估計）: {memory.get_token_count()}\n")

    print("對話內容:")
    print(memory.get_context_string())


def demonstrate_window_memory():
    """演示滑動窗口記憶"""
    print("\n" + "="*60)
    print("示例 2: 滑動窗口記憶")
    print("="*60 + "\n")

    memory = WindowMemory(window_size=4)

    # 添加多條消息
    for i in range(8):
        memory.add_user_message(f"用戶消息 {i+1}")
        memory.add_assistant_message(f"助手回復 {i+1}")

    # 獲取消息（只有最近的 4 條）
    messages = memory.get_messages()
    print(f"窗口大小: 4")
    print(f"實際保留消息數: {len(messages)}\n")

    print("保留的消息:")
    for msg in messages:
        print(f"  {msg.role}: {msg.content}")


def demonstrate_token_memory():
    """演示 Token 限制記憶"""
    print("\n" + "="*60)
    print("示例 3: Token 限制記憶")
    print("="*60 + "\n")

    memory = TokenBufferMemory(max_tokens=100)

    # 添加消息直到超過限制
    test_messages = [
        "這是第一條消息",
        "這是第二條比較長的消息，包含更多內容",
        "第三條消息也很長，繼續測試 token 限制功能",
        "第四條消息",
        "第五條消息，應該會觸發舊消息的移除"
    ]

    for i, content in enumerate(test_messages, 1):
        memory.add_user_message(content)
        print(f"添加消息 {i}: tokens={len(memory.messages[-1])}")
        print(f"  當前總 tokens: {memory.current_tokens}/{memory.max_tokens}")
        print(f"  保留消息數: {len(memory.get_messages())}\n")


def demonstrate_summary_memory():
    """演示摘要記憶"""
    print("\n" + "="*60)
    print("示例 4: 摘要記憶")
    print("="*60 + "\n")

    memory = SummaryMemory(max_messages=5, summary_threshold=8)

    # 添加多條消息觸發摘要
    topics = ["產品諮詢", "技術問題", "訂單查詢", "售後服務",
              "功能建議", "Bug 報告", "使用教程", "帳號問題"]

    for i, topic in enumerate(topics, 1):
        memory.add_user_message(f"關於{topic}的問題")
        memory.add_assistant_message(f"這是關於{topic}的回答")

    print(f"總消息數（含摘要）: {len(memory.get_messages())}")
    print(f"摘要數量: {len(memory.summaries)}")
    print(f"詳細消息數: {len(memory.messages)}\n")

    print("記憶內容:")
    for msg in memory.get_messages():
        print(f"  {msg.role}: {msg.content[:60]}...")


def demonstrate_entity_memory():
    """演示實體記憶"""
    print("\n" + "="*60)
    print("示例 5: 實體記憶")
    print("="*60 + "\n")

    memory = EntityMemory()

    # 添加包含實體的對話
    conversations = [
        ("我是張三，在台北工作", "assistant", "您好張三！"),
        ("user", "我們公司的產品很不錯"),
        ("assistant", "很高興您喜歡我們的產品"),
        ("user", "下週我要去高雄出差")
    ]

    for i, conv in enumerate(conversations):
        if len(conv) == 2:
            role, content = conv
        else:
            role, content, _ = conv

        if role == "user":
            memory.add_user_message(content)
        else:
            memory.add_assistant_message(content)

    print(f"提取的實體數量: {len(memory.entities)}\n")

    print("實體詳情:")
    for entity_name, entity_info in memory.entities.items():
        print(f"  {entity_name}:")
        print(f"    類型: {entity_info['type']}")
        print(f"    提及次數: {len(entity_info['mentions'])}")


def demonstrate_persistent_memory():
    """演示持久化記憶"""
    print("\n" + "="*60)
    print("示例 6: 持久化記憶")
    print("="*60 + "\n")

    # 創建臨時存儲目錄
    storage_path = "./temp_memory_storage"
    memory = SimpleMemory()
    persistent = PersistentMemory(memory, storage_path)

    # 添加一些對話
    memory.add_user_message("測試持久化功能")
    memory.add_assistant_message("記憶將被保存到文件")
    memory.add_user_message("稍後可以恢復")

    # 保存
    session_id = "test_session_001"
    persistent.save(session_id)
    print(f"保存會話: {session_id}")

    # 清空記憶
    memory.clear()
    print("清空當前記憶")
    print(f"當前消息數: {len(memory.get_messages())}")

    # 恢復
    print("\n恢復記憶...")
    persistent.load(session_id)
    print(f"恢復後消息數: {len(memory.get_messages())}\n")

    print("恢復的對話:")
    print(memory.get_context_string())

    # 清理
    import shutil
    if os.path.exists(storage_path):
        shutil.rmtree(storage_path)


def main():
    """主函數"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "對話記憶管理示例" + " "*20 + "║")
    print("╚" + "="*58 + "╝")

    try:
        demonstrate_simple_memory()
        demonstrate_window_memory()
        demonstrate_token_memory()
        demonstrate_summary_memory()
        demonstrate_entity_memory()
        demonstrate_persistent_memory()

        print("\n" + "="*60)
        print("所有示例執行完成！")
        print("="*60)

    except Exception as e:
        logger.error(f"執行錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
