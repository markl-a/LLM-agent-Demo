"""
Julep 自適應上下文管理示例

這個模塊展示了 Julep 平台的自適應上下文管理功能。
包括智能上下文窗口管理、動態優先級調整、上下文壓縮和優化。

主要功能：
1. 動態上下文窗口管理
2. 消息優先級排序
3. 上下文壓縮和摘要
4. 智能消息裁剪
5. 上下文相關性評分
6. 記憶管理

作者：Julep 示例
日期：2025-12-31
"""

import time
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from collections import deque
import math


class MessagePriority(Enum):
    """消息優先級"""
    CRITICAL = 5  # 系統消息、重要指令
    HIGH = 4  # 用戶明確的問題
    NORMAL = 3  # 普通對話
    LOW = 2  # 背景信息
    MINIMAL = 1  # 可以丟棄的內容


class ContextStrategy(Enum):
    """上下文策略"""
    RECENT_FIRST = "recent_first"  # 優先保留最近的消息
    PRIORITY_BASED = "priority_based"  # 基於優先級
    RELEVANCE_BASED = "relevance_based"  # 基於相關性
    HYBRID = "hybrid"  # 混合策略


@dataclass
class Message:
    """消息類"""
    id: str
    role: str  # user, assistant, system
    content: str
    timestamp: datetime
    priority: MessagePriority = MessagePriority.NORMAL
    metadata: Dict[str, Any] = None
    relevance_score: float = 0.0
    token_count: int = 0

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.token_count == 0:
            # 簡單估算 token 數
            self.token_count = len(self.content) // 4

    def to_dict(self) -> Dict[str, str]:
        """轉換為字典格式（用於 API 調用）"""
        return {
            "role": self.role,
            "content": self.content
        }


class ContextWindow:
    """上下文窗口

    管理有限的上下文窗口，智能選擇保留哪些消息。
    """

    def __init__(
        self,
        max_tokens: int = 4000,
        strategy: ContextStrategy = ContextStrategy.HYBRID
    ):
        """初始化上下文窗口

        Args:
            max_tokens: 最大 token 數
            strategy: 上下文管理策略
        """
        self.max_tokens = max_tokens
        self.strategy = strategy
        self.messages: List[Message] = []
        self.system_message: Optional[str] = None

    def add_message(
        self,
        role: str,
        content: str,
        priority: MessagePriority = MessagePriority.NORMAL,
        metadata: Optional[Dict] = None
    ) -> Message:
        """添加消息

        Args:
            role: 角色
            content: 內容
            priority: 優先級
            metadata: 元數據

        Returns:
            創建的消息
        """
        message = Message(
            id=f"msg_{len(self.messages)}_{int(time.time())}",
            role=role,
            content=content,
            timestamp=datetime.now(),
            priority=priority,
            metadata=metadata
        )

        self.messages.append(message)
        return message

    def calculate_relevance(
        self,
        message: Message,
        query: Optional[str] = None
    ) -> float:
        """計算消息的相關性分數

        Args:
            message: 消息
            query: 查詢文本（可選）

        Returns:
            相關性分數 (0-1)
        """
        score = 0.0

        # 基於優先級
        priority_weight = message.priority.value / 5.0
        score += priority_weight * 0.3

        # 基於時間（越新越相關）
        age = datetime.now() - message.timestamp
        time_weight = max(0, 1 - age.total_seconds() / 3600)  # 1小時衰減
        score += time_weight * 0.3

        # 基於角色
        role_weights = {"system": 0.9, "user": 0.8, "assistant": 0.7}
        role_weight = role_weights.get(message.role, 0.5)
        score += role_weight * 0.2

        # 如果有查詢，計算文本相似度
        if query:
            # 簡單的關鍵詞匹配
            query_words = set(query.lower().split())
            message_words = set(message.content.lower().split())
            overlap = len(query_words & message_words)
            if query_words:
                similarity = overlap / len(query_words)
                score += similarity * 0.2

        return min(1.0, score)

    def get_context_messages(
        self,
        current_query: Optional[str] = None,
        reserve_tokens: int = 500
    ) -> List[Dict[str, str]]:
        """獲取適應上下文窗口的消息

        Args:
            current_query: 當前查詢（用於相關性計算）
            reserve_tokens: 為響應預留的 token 數

        Returns:
            消息列表
        """
        available_tokens = self.max_tokens - reserve_tokens

        # 更新相關性分數
        for msg in self.messages:
            msg.relevance_score = self.calculate_relevance(msg, current_query)

        # 根據策略選擇消息
        if self.strategy == ContextStrategy.RECENT_FIRST:
            selected = self._select_recent_first(available_tokens)
        elif self.strategy == ContextStrategy.PRIORITY_BASED:
            selected = self._select_priority_based(available_tokens)
        elif self.strategy == ContextStrategy.RELEVANCE_BASED:
            selected = self._select_relevance_based(available_tokens)
        else:  # HYBRID
            selected = self._select_hybrid(available_tokens)

        # 轉換為 API 格式
        result = []

        # 添加系統消息
        if self.system_message:
            result.append({"role": "system", "content": self.system_message})

        # 添加選中的消息（保持時間順序）
        selected.sort(key=lambda m: m.timestamp)
        result.extend([msg.to_dict() for msg in selected])

        print(f"[CONTEXT] 選擇了 {len(selected)}/{len(self.messages)} 條消息")
        print(f"[CONTEXT] 使用策略: {self.strategy.value}")

        return result

    def _select_recent_first(self, max_tokens: int) -> List[Message]:
        """選擇最近的消息"""
        selected = []
        current_tokens = 0

        # 從最新的消息開始
        for msg in reversed(self.messages):
            if current_tokens + msg.token_count <= max_tokens:
                selected.append(msg)
                current_tokens += msg.token_count
            else:
                break

        return selected

    def _select_priority_based(self, max_tokens: int) -> List[Message]:
        """基於優先級選擇消息"""
        # 按優先級排序
        sorted_msgs = sorted(
            self.messages,
            key=lambda m: (m.priority.value, m.timestamp),
            reverse=True
        )

        selected = []
        current_tokens = 0

        for msg in sorted_msgs:
            if current_tokens + msg.token_count <= max_tokens:
                selected.append(msg)
                current_tokens += msg.token_count

        return selected

    def _select_relevance_based(self, max_tokens: int) -> List[Message]:
        """基於相關性選擇消息"""
        # 按相關性排序
        sorted_msgs = sorted(
            self.messages,
            key=lambda m: m.relevance_score,
            reverse=True
        )

        selected = []
        current_tokens = 0

        for msg in sorted_msgs:
            if current_tokens + msg.token_count <= max_tokens:
                selected.append(msg)
                current_tokens += msg.token_count

        return selected

    def _select_hybrid(self, max_tokens: int) -> List[Message]:
        """混合策略：結合多個因素"""
        # 計算綜合分數
        for msg in self.messages:
            # 時間因素
            age = datetime.now() - msg.timestamp
            time_score = max(0, 1 - age.total_seconds() / 3600)

            # 綜合分數
            msg.relevance_score = (
                msg.relevance_score * 0.4 +
                (msg.priority.value / 5.0) * 0.3 +
                time_score * 0.3
            )

        # 按綜合分數排序
        sorted_msgs = sorted(
            self.messages,
            key=lambda m: m.relevance_score,
            reverse=True
        )

        selected = []
        current_tokens = 0

        for msg in sorted_msgs:
            if current_tokens + msg.token_count <= max_tokens:
                selected.append(msg)
                current_tokens += msg.token_count

        return selected

    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        total_tokens = sum(msg.token_count for msg in self.messages)
        avg_tokens = total_tokens / len(self.messages) if self.messages else 0

        return {
            "total_messages": len(self.messages),
            "total_tokens": total_tokens,
            "avg_tokens_per_message": avg_tokens,
            "max_tokens": self.max_tokens,
            "strategy": self.strategy.value
        }


class ContextCompressor:
    """上下文壓縮器

    將長對話歷史壓縮成摘要。
    """

    def __init__(self):
        """初始化壓縮器"""
        pass

    def summarize_messages(
        self,
        messages: List[Message],
        max_length: int = 200
    ) -> str:
        """摘要消息

        Args:
            messages: 消息列表
            max_length: 最大摘要長度

        Returns:
            摘要文本
        """
        if not messages:
            return ""

        print(f"[COMPRESS] 壓縮 {len(messages)} 條消息...")

        # 提取關鍵信息
        user_messages = [m for m in messages if m.role == "user"]
        assistant_messages = [m for m in messages if m.role == "assistant"]

        # 生成摘要
        summary_parts = []

        if user_messages:
            summary_parts.append(
                f"用戶詢問了 {len(user_messages)} 個問題，"
                f"主要關於：{self._extract_keywords(user_messages)}"
            )

        if assistant_messages:
            summary_parts.append(
                f"助手提供了 {len(assistant_messages)} 個回答"
            )

        summary = "。".join(summary_parts)
        return summary[:max_length]

    def _extract_keywords(self, messages: List[Message], top_k: int = 3) -> str:
        """提取關鍵詞

        Args:
            messages: 消息列表
            top_k: 提取數量

        Returns:
            關鍵詞字符串
        """
        # 簡單的詞頻統計
        word_freq = {}
        stop_words = {"的", "了", "是", "在", "我", "你", "他", "她", "它"}

        for msg in messages:
            words = msg.content.split()
            for word in words:
                if word not in stop_words and len(word) > 1:
                    word_freq[word] = word_freq.get(word, 0) + 1

        # 取前 K 個
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return "、".join([word for word, _ in top_words])

    def compress_context(
        self,
        window: ContextWindow,
        keep_recent: int = 5
    ) -> str:
        """壓縮上下文窗口

        Args:
            window: 上下文窗口
            keep_recent: 保留最近 N 條消息

        Returns:
            壓縮後的摘要
        """
        if len(window.messages) <= keep_recent:
            return ""

        # 分割消息：舊的壓縮，新的保留
        old_messages = window.messages[:-keep_recent]
        recent_messages = window.messages[-keep_recent:]

        # 壓縮舊消息
        summary = self.summarize_messages(old_messages)

        # 更新窗口
        window.messages = recent_messages

        # 添加摘要作為系統消息
        if summary:
            window.system_message = f"對話歷史摘要：{summary}"

        print(f"[COMPRESS] 壓縮完成，保留 {keep_recent} 條最近消息")
        return summary


class AdaptiveMemory:
    """自適應記憶

    智能管理長期和短期記憶。
    """

    def __init__(self):
        """初始化記憶系統"""
        self.short_term: deque = deque(maxlen=20)  # 短期記憶
        self.long_term: List[Dict] = []  # 長期記憶
        self.important_facts: Dict[str, Any] = {}  # 重要事實

    def add_to_short_term(self, message: Message):
        """添加到短期記憶"""
        self.short_term.append(message)

    def promote_to_long_term(self, message: Message):
        """提升到長期記憶

        Args:
            message: 消息
        """
        # 只保存重要消息
        if message.priority.value >= MessagePriority.HIGH.value:
            memory_item = {
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
                "importance": message.priority.value
            }
            self.long_term.append(memory_item)
            print(f"[MEMORY] 提升到長期記憶: {message.content[:50]}...")

    def extract_fact(self, key: str, value: Any):
        """提取重要事實

        Args:
            key: 事實鍵
            value: 事實值
        """
        self.important_facts[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        print(f"[MEMORY] 記住事實: {key} = {value}")

    def recall(self, query: str, max_items: int = 5) -> List[Dict]:
        """回憶相關記憶

        Args:
            query: 查詢
            max_items: 最大返回數量

        Returns:
            相關記憶列表
        """
        # 簡單的關鍵詞匹配
        query_words = set(query.lower().split())
        scored_memories = []

        for memory in self.long_term:
            content_words = set(memory["content"].lower().split())
            overlap = len(query_words & content_words)
            if overlap > 0:
                score = overlap / len(query_words)
                scored_memories.append((score, memory))

        # 按分數排序
        scored_memories.sort(reverse=True, key=lambda x: x[0])

        return [mem for _, mem in scored_memories[:max_items]]

    def get_stats(self) -> Dict[str, Any]:
        """獲取記憶統計"""
        return {
            "short_term_count": len(self.short_term),
            "long_term_count": len(self.long_term),
            "facts_count": len(self.important_facts)
        }


def demo_context_strategies():
    """上下文策略示例"""
    print("\n" + "="*60)
    print("示例 1: 不同的上下文策略")
    print("="*60)

    # 創建測試消息
    strategies = [
        ContextStrategy.RECENT_FIRST,
        ContextStrategy.PRIORITY_BASED,
        ContextStrategy.HYBRID
    ]

    for strategy in strategies:
        print(f"\n使用策略: {strategy.value}")
        print("-" * 40)

        window = ContextWindow(max_tokens=500, strategy=strategy)
        window.system_message = "你是一個有幫助的助手"

        # 添加不同優先級的消息
        window.add_message("user", "你好", MessagePriority.NORMAL)
        window.add_message("assistant", "你好！有什麼可以幫助你的？", MessagePriority.NORMAL)
        window.add_message("user", "請記住我的名字是張三", MessagePriority.CRITICAL)
        window.add_message("assistant", "好的，我記住了你的名字是張三", MessagePriority.CRITICAL)
        window.add_message("user", "今天天氣怎麼樣？", MessagePriority.LOW)
        window.add_message("assistant", "抱歉，我無法獲取實時天氣信息", MessagePriority.LOW)
        window.add_message("user", "我的名字是什麼？", MessagePriority.HIGH)

        # 獲取上下文
        context = window.get_context_messages(current_query="我的名字是什麼？")

        print(f"選中的消息數: {len(context)}")
        print(f"統計: {window.get_stats()}")


def demo_context_compression():
    """上下文壓縮示例"""
    print("\n" + "="*60)
    print("示例 2: 上下文壓縮")
    print("="*60)

    window = ContextWindow(max_tokens=2000)
    compressor = ContextCompressor()

    # 添加大量消息
    print("\n添加 15 條消息...")
    for i in range(15):
        window.add_message("user", f"這是第 {i+1} 個用戶消息")
        window.add_message("assistant", f"這是對第 {i+1} 個消息的回復")

    print(f"壓縮前: {len(window.messages)} 條消息")

    # 壓縮上下文
    summary = compressor.compress_context(window, keep_recent=5)

    print(f"壓縮後: {len(window.messages)} 條消息")
    print(f"摘要: {summary}")
    print(f"系統消息: {window.system_message}")


def demo_adaptive_memory():
    """自適應記憶示例"""
    print("\n" + "="*60)
    print("示例 3: 自適應記憶")
    print("="*60)

    memory = AdaptiveMemory()

    # 添加消息到短期記憶
    messages = [
        Message("1", "user", "我叫張三", datetime.now(), MessagePriority.CRITICAL),
        Message("2", "user", "我住在北京", datetime.now(), MessagePriority.HIGH),
        Message("3", "user", "今天天氣不錯", datetime.now(), MessagePriority.LOW),
        Message("4", "user", "我是一名工程師", datetime.now(), MessagePriority.HIGH),
    ]

    print("\n處理消息...")
    for msg in messages:
        memory.add_to_short_term(msg)
        memory.promote_to_long_term(msg)

    # 提取事實
    memory.extract_fact("user_name", "張三")
    memory.extract_fact("user_location", "北京")
    memory.extract_fact("user_profession", "工程師")

    # 回憶
    print("\n回憶與'工程師'相關的記憶:")
    recalled = memory.recall("工程師")
    for mem in recalled:
        print(f"  - {mem['content']}")

    # 統計
    print(f"\n記憶統計: {memory.get_stats()}")
    print(f"重要事實: {list(memory.important_facts.keys())}")


def demo_dynamic_optimization():
    """動態優化示例"""
    print("\n" + "="*60)
    print("示例 4: 動態上下文優化")
    print("="*60)

    window = ContextWindow(max_tokens=1000, strategy=ContextStrategy.HYBRID)

    # 模擬對話過程中的動態調整
    print("\n模擬對話流程...")

    # 初始對話
    window.add_message("user", "介紹一下 Python", MessagePriority.NORMAL)
    window.add_message("assistant", "Python 是一種高級編程語言...", MessagePriority.NORMAL)

    # 用戶提供重要信息
    window.add_message("user", "我是初學者，需要簡單的例子", MessagePriority.CRITICAL)
    window.add_message("assistant", "明白了，我會提供簡單的例子", MessagePriority.CRITICAL)

    # 繼續對話
    for i in range(5):
        window.add_message("user", f"關於主題{i+1}的問題", MessagePriority.NORMAL)
        window.add_message("assistant", f"關於主題{i+1}的回答", MessagePriority.NORMAL)

    # 重要查詢
    current_query = "給我一個適合初學者的例子"

    print(f"\n當前查詢: {current_query}")
    context = window.get_context_messages(current_query=current_query)

    print(f"\n選中的消息:")
    for msg in context:
        print(f"  [{msg['role']}] {msg['content'][:50]}...")


def demo_memory_integration():
    """記憶系統集成示例"""
    print("\n" + "="*60)
    print("示例 5: 上下文與記憶集成")
    print("="*60)

    window = ContextWindow(max_tokens=1500)
    memory = AdaptiveMemory()
    compressor = ContextCompressor()

    # 模擬長對話
    print("\n模擬長對話...")

    important_info = [
        ("我的名字是李明", MessagePriority.CRITICAL),
        ("我在學習機器學習", MessagePriority.HIGH),
        ("我最喜歡 Python", MessagePriority.HIGH),
    ]

    # 添加重要信息
    for content, priority in important_info:
        msg = window.add_message("user", content, priority)
        memory.add_to_short_term(msg)
        memory.promote_to_long_term(msg)

    # 添加普通對話
    for i in range(10):
        msg = window.add_message(
            "user",
            f"普通問題 {i+1}",
            MessagePriority.NORMAL
        )
        memory.add_to_short_term(msg)

    # 壓縮舊上下文
    summary = compressor.compress_context(window, keep_recent=3)

    # 回憶重要信息
    recalled = memory.recall("學習")

    print(f"\n上下文摘要: {summary}")
    print(f"\n相關記憶:")
    for mem in recalled:
        print(f"  - {mem['content']}")

    print(f"\n最終統計:")
    print(f"  上下文: {window.get_stats()}")
    print(f"  記憶: {memory.get_stats()}")


def main():
    """主函數"""
    print("="*60)
    print("Julep 自適應上下文管理示例")
    print("="*60)

    try:
        demo_context_strategies()
        demo_context_compression()
        demo_adaptive_memory()
        demo_dynamic_optimization()
        demo_memory_integration()

        print("\n" + "="*60)
        print("所有示例執行完成！")
        print("="*60)

    except Exception as e:
        print(f"\n[ERROR] 執行出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
