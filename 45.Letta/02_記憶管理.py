"""
Letta 記憶管理深度解析

本模組詳細介紹 Letta 的三層記憶架構：
1. 核心記憶（Core Memory）- 工作記憶
2. 歸檔記憶（Archival Memory）- 長期存儲
3. 回憶記憶（Recall Memory）- 對話歷史

展示如何有效管理和優化 Agent 的記憶系統。

作者：Letta 框架示例
日期：2025-01
"""

import os
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class MemoryBlock:
    """記憶塊數據結構"""
    content: str
    timestamp: str
    category: str
    importance: float  # 0-1 的重要性分數
    metadata: Dict[str, Any]


class CoreMemoryManager:
    """
    核心記憶管理器

    核心記憶是 Agent 的"工作記憶"，類似於 CPU 緩存。
    容量有限（通常 2-4K tokens），但每次交互都會加載。
    """

    def __init__(self, max_size: int = 2048):
        """
        初始化核心記憶管理器

        參數:
            max_size: 核心記憶的最大大小（tokens）
        """
        self.max_size = max_size
        self.persona = ""
        self.human = ""
        self.custom_sections = {}

        print(f"核心記憶管理器初始化完成（容量: {max_size} tokens）")

    def set_persona(self, persona: str) -> None:
        """
        設置 Agent 的人格設定

        參數:
            persona: 人格描述
        """
        self.persona = persona
        print(f"[核心記憶] Persona 已更新")
        print(f"內容: {persona[:100]}...")

    def set_human(self, human: str) -> None:
        """
        設置用戶信息

        參數:
            human: 用戶描述
        """
        self.human = human
        print(f"[核心記憶] Human 已更新")
        print(f"內容: {human[:100]}...")

    def append_to_section(self, section: str, content: str) -> None:
        """
        向指定區域追加內容

        參數:
            section: 區域名稱（'persona' 或 'human'）
            content: 要追加的內容
        """
        if section == "persona":
            self.persona += f"\n{content}"
            print(f"[核心記憶] 已向 Persona 追加內容")
        elif section == "human":
            self.human += f"\n{content}"
            print(f"[核心記憶] 已向 Human 追加內容")
        else:
            if section not in self.custom_sections:
                self.custom_sections[section] = ""
            self.custom_sections[section] += f"\n{content}"
            print(f"[核心記憶] 已向自定義區域 '{section}' 追加內容")

    def replace_in_section(self, section: str, old_content: str, new_content: str) -> bool:
        """
        替換指定區域的內容

        參數:
            section: 區域名稱
            old_content: 要替換的舊內容
            new_content: 新內容

        返回:
            是否成功替換
        """
        if section == "persona":
            if old_content in self.persona:
                self.persona = self.persona.replace(old_content, new_content)
                print(f"[核心記憶] Persona 內容已替換")
                return True
        elif section == "human":
            if old_content in self.human:
                self.human = self.human.replace(old_content, new_content)
                print(f"[核心記憶] Human 內容已替換")
                return True
        elif section in self.custom_sections:
            if old_content in self.custom_sections[section]:
                self.custom_sections[section] = self.custom_sections[section].replace(
                    old_content, new_content
                )
                print(f"[核心記憶] 自定義區域 '{section}' 內容已替換")
                return True

        print(f"[核心記憶] 未找到要替換的內容")
        return False

    def get_memory_usage(self) -> Dict[str, int]:
        """
        獲取記憶使用情況

        返回:
            各區域的大小（近似 tokens）
        """
        usage = {
            "persona": len(self.persona) // 4,  # 粗略估計 tokens
            "human": len(self.human) // 4,
            "custom": sum(len(v) for v in self.custom_sections.values()) // 4,
            "total": (len(self.persona) + len(self.human) +
                     sum(len(v) for v in self.custom_sections.values())) // 4
        }

        print(f"\n[記憶使用情況]")
        print(f"  Persona: {usage['persona']} tokens")
        print(f"  Human: {usage['human']} tokens")
        print(f"  Custom: {usage['custom']} tokens")
        print(f"  Total: {usage['total']}/{self.max_size} tokens")
        print(f"  使用率: {usage['total']/self.max_size*100:.1f}%")

        return usage

    def optimize_memory(self) -> None:
        """
        優化核心記憶

        當記憶接近容量上限時，壓縮或總結內容。
        """
        usage = self.get_memory_usage()

        if usage['total'] > self.max_size * 0.8:  # 超過 80% 容量
            print("\n[記憶優化] 核心記憶接近上限，開始優化...")

            # 壓縮策略：移除重複內容、總結長文本
            # 在實際應用中，可能會使用 LLM 來總結
            print("  - 移除重複內容")
            print("  - 總結長文本")
            print("  - 將不常用信息移至歸檔記憶")

            print("✓ 記憶優化完成")


class ArchivalMemoryManager:
    """
    歸檔記憶管理器

    歸檔記憶是 Agent 的"長期存儲"，類似於硬碟。
    容量幾乎無限，通過向量搜索訪問。
    """

    def __init__(self, embedding_model: str = "text-embedding-ada-002"):
        """
        初始化歸檔記憶管理器

        參數:
            embedding_model: 用於生成向量的模型
        """
        self.embedding_model = embedding_model
        self.memories: List[MemoryBlock] = []
        self.embeddings = []  # 在實際應用中，這裡存儲向量

        print(f"歸檔記憶管理器初始化完成（嵌入模型: {embedding_model}）")

    def insert(self, content: str, category: str = "general",
               importance: float = 0.5, metadata: Optional[Dict] = None) -> str:
        """
        插入新的記憶到歸檔

        參數:
            content: 記憶內容
            category: 分類
            importance: 重要性（0-1）
            metadata: 額外的元數據

        返回:
            記憶 ID
        """
        memory = MemoryBlock(
            content=content,
            timestamp=datetime.now().isoformat(),
            category=category,
            importance=importance,
            metadata=metadata or {}
        )

        self.memories.append(memory)

        # 在實際應用中，這裡會生成並存儲向量
        # embedding = self._generate_embedding(content)
        # self.embeddings.append(embedding)

        memory_id = f"mem_{len(self.memories)}"

        print(f"[歸檔記憶] 已插入新記憶")
        print(f"  ID: {memory_id}")
        print(f"  分類: {category}")
        print(f"  重要性: {importance}")
        print(f"  內容: {content[:50]}...")

        return memory_id

    def search(self, query: str, limit: int = 5,
               min_importance: float = 0.0) -> List[MemoryBlock]:
        """
        搜索歸檔記憶

        參數:
            query: 搜索查詢
            limit: 返回結果數量上限
            min_importance: 最小重要性閾值

        返回:
            匹配的記憶列表
        """
        print(f"\n[歸檔搜索] 查詢: '{query}'")

        # 在實際應用中，這裡會使用向量相似度搜索
        # 這裡使用簡單的關鍵詞匹配
        results = []
        for memory in self.memories:
            if memory.importance >= min_importance:
                # 簡單的關鍵詞匹配
                if any(word in memory.content.lower() for word in query.lower().split()):
                    results.append(memory)

        # 按重要性和時間排序
        results.sort(key=lambda m: (m.importance, m.timestamp), reverse=True)
        results = results[:limit]

        print(f"找到 {len(results)} 條相關記憶:")
        for i, memory in enumerate(results, 1):
            print(f"  {i}. [{memory.category}] {memory.content[:60]}...")
            print(f"     重要性: {memory.importance}, 時間: {memory.timestamp}")

        return results

    def search_by_category(self, category: str) -> List[MemoryBlock]:
        """
        按分類搜索記憶

        參數:
            category: 分類名稱

        返回:
            該分類的所有記憶
        """
        results = [m for m in self.memories if m.category == category]
        print(f"\n[分類搜索] 分類 '{category}': 找到 {len(results)} 條記憶")
        return results

    def search_by_date_range(self, start_date: str, end_date: str) -> List[MemoryBlock]:
        """
        按日期範圍搜索記憶

        參數:
            start_date: 開始日期（ISO 格式）
            end_date: 結束日期（ISO 格式）

        返回:
            日期範圍內的記憶
        """
        results = [
            m for m in self.memories
            if start_date <= m.timestamp <= end_date
        ]
        print(f"\n[日期搜索] {start_date} 到 {end_date}: 找到 {len(results)} 條記憶")
        return results

    def update_importance(self, memory_index: int, new_importance: float) -> None:
        """
        更新記憶的重要性

        參數:
            memory_index: 記憶索引
            new_importance: 新的重要性分數
        """
        if 0 <= memory_index < len(self.memories):
            old_importance = self.memories[memory_index].importance
            self.memories[memory_index].importance = new_importance
            print(f"[更新重要性] 記憶 {memory_index}: {old_importance} -> {new_importance}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        獲取歸檔記憶統計信息

        返回:
            統計信息字典
        """
        if not self.memories:
            return {"total": 0}

        categories = {}
        for memory in self.memories:
            categories[memory.category] = categories.get(memory.category, 0) + 1

        stats = {
            "total": len(self.memories),
            "categories": categories,
            "avg_importance": sum(m.importance for m in self.memories) / len(self.memories),
            "oldest": min(m.timestamp for m in self.memories),
            "newest": max(m.timestamp for m in self.memories)
        }

        print(f"\n[歸檔統計]")
        print(f"  總記憶數: {stats['total']}")
        print(f"  平均重要性: {stats['avg_importance']:.2f}")
        print(f"  分類分布: {stats['categories']}")

        return stats


class RecallMemoryManager:
    """
    回憶記憶管理器

    回憶記憶存儲完整的對話歷史，按時間順序組織。
    """

    def __init__(self, max_messages: int = 1000):
        """
        初始化回憶記憶管理器

        參數:
            max_messages: 最大消息數量
        """
        self.max_messages = max_messages
        self.messages: List[Dict[str, Any]] = []

        print(f"回憶記憶管理器初始化完成（容量: {max_messages} 條消息）")

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """
        添加消息到回憶記憶

        參數:
            role: 角色（'user' 或 'assistant'）
            content: 消息內容
            metadata: 額外的元數據
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        self.messages.append(message)

        # 如果超過最大容量，移除最舊的消息
        if len(self.messages) > self.max_messages:
            removed = self.messages.pop(0)
            print(f"[回憶記憶] 已移除最舊的消息（{removed['timestamp']}）")

        print(f"[回憶記憶] 已添加 {role} 消息")

    def get_recent_messages(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        獲取最近的消息

        參數:
            count: 消息數量

        返回:
            最近的消息列表
        """
        recent = self.messages[-count:]
        print(f"\n[最近消息] 獲取最後 {len(recent)} 條消息")
        return recent

    def search_messages(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜索消息歷史

        參數:
            query: 搜索查詢
            limit: 返回結果上限

        返回:
            匹配的消息列表
        """
        results = [
            msg for msg in self.messages
            if query.lower() in msg['content'].lower()
        ][:limit]

        print(f"\n[消息搜索] 查詢 '{query}': 找到 {len(results)} 條消息")
        return results

    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        獲取對話摘要

        返回:
            對話統計信息
        """
        if not self.messages:
            return {"total": 0}

        user_msgs = sum(1 for m in self.messages if m['role'] == 'user')
        assistant_msgs = sum(1 for m in self.messages if m['role'] == 'assistant')

        summary = {
            "total_messages": len(self.messages),
            "user_messages": user_msgs,
            "assistant_messages": assistant_msgs,
            "first_message": self.messages[0]['timestamp'] if self.messages else None,
            "last_message": self.messages[-1]['timestamp'] if self.messages else None
        }

        print(f"\n[對話摘要]")
        print(f"  總消息數: {summary['total_messages']}")
        print(f"  用戶消息: {summary['user_messages']}")
        print(f"  助手消息: {summary['assistant_messages']}")

        return summary


class IntegratedMemorySystem:
    """
    集成記憶系統

    整合核心記憶、歸檔記憶和回憶記憶，提供統一的接口。
    """

    def __init__(self):
        """初始化集成記憶系統"""
        self.core = CoreMemoryManager(max_size=2048)
        self.archival = ArchivalMemoryManager()
        self.recall = RecallMemoryManager(max_messages=1000)

        print("\n" + "=" * 60)
        print("集成記憶系統已初始化")
        print("=" * 60)

    def process_user_message(self, message: str) -> None:
        """
        處理用戶消息，自動更新各層記憶

        參數:
            message: 用戶消息
        """
        print(f"\n[處理消息] {message}")

        # 1. 添加到回憶記憶
        self.recall.add_message("user", message)

        # 2. 提取重要信息並更新核心記憶
        self._update_core_from_message(message)

        # 3. 將消息存入歸檔記憶
        importance = self._calculate_importance(message)
        self.archival.insert(
            content=message,
            category="user_message",
            importance=importance
        )

    def process_assistant_response(self, response: str) -> None:
        """
        處理助手響應

        參數:
            response: 助手響應
        """
        # 添加到回憶記憶
        self.recall.add_message("assistant", response)

        # 存入歸檔記憶
        self.archival.insert(
            content=response,
            category="assistant_response",
            importance=0.3
        )

    def _update_core_from_message(self, message: str) -> None:
        """從消息中提取關鍵信息更新核心記憶"""
        # 簡單的關鍵信息提取（實際應用中會使用 NLP）
        if "我叫" in message or "我是" in message:
            # 提取姓名
            self.core.append_to_section("human", f"從對話中了解到: {message}")

    def _calculate_importance(self, message: str) -> float:
        """計算消息的重要性"""
        # 簡單的重要性評估
        importance = 0.5

        # 包含個人信息的消息更重要
        if any(keyword in message for keyword in ["我叫", "我是", "我的"]):
            importance += 0.3

        # 較長的消息可能更重要
        if len(message) > 100:
            importance += 0.1

        return min(importance, 1.0)

    def smart_recall(self, query: str) -> Dict[str, Any]:
        """
        智能回憶：從所有記憶層檢索相關信息

        參數:
            query: 查詢內容

        返回:
            綜合的回憶結果
        """
        print(f"\n{'=' * 60}")
        print(f"智能回憶: '{query}'")
        print("=" * 60)

        results = {
            "core_memory": {},
            "archival_results": [],
            "recall_results": []
        }

        # 1. 檢查核心記憶
        print("\n[1/3] 檢查核心記憶...")
        results["core_memory"] = {
            "persona": self.core.persona,
            "human": self.core.human
        }

        # 2. 搜索歸檔記憶
        print("\n[2/3] 搜索歸檔記憶...")
        results["archival_results"] = self.archival.search(query, limit=5)

        # 3. 搜索回憶記憶
        print("\n[3/3] 搜索對話歷史...")
        results["recall_results"] = self.recall.search_messages(query, limit=5)

        print(f"\n{'=' * 60}")
        print("智能回憶完成")
        print("=" * 60)

        return results


def demonstrate_core_memory():
    """演示核心記憶管理"""
    print("\n" + "=" * 60)
    print("核心記憶管理演示")
    print("=" * 60)

    core = CoreMemoryManager(max_size=2048)

    # 設置初始記憶
    core.set_persona("你是一個專業的 AI 助手，擅長技術支持。")
    core.set_human("用戶是一名軟件工程師。")

    # 追加信息
    core.append_to_section("human", "用戶名稱：李明")
    core.append_to_section("human", "技能：Python, JavaScript")

    # 替換信息
    core.replace_in_section("human", "軟件工程師", "高級軟件工程師")

    # 查看使用情況
    core.get_memory_usage()


def demonstrate_archival_memory():
    """演示歸檔記憶管理"""
    print("\n" + "=" * 60)
    print("歸檔記憶管理演示")
    print("=" * 60)

    archival = ArchivalMemoryManager()

    # 插入不同類型的記憶
    archival.insert(
        "用戶喜歡使用 Python 進行數據分析",
        category="preference",
        importance=0.8
    )

    archival.insert(
        "用戶在 2024 年 3 月完成了機器學習課程",
        category="achievement",
        importance=0.7
    )

    archival.insert(
        "用戶對深度學習特別感興趣",
        category="interest",
        importance=0.9
    )

    # 搜索記憶
    archival.search("Python")
    archival.search("學習")

    # 按分類搜索
    archival.search_by_category("preference")

    # 統計信息
    archival.get_statistics()


def demonstrate_recall_memory():
    """演示回憶記憶管理"""
    print("\n" + "=" * 60)
    print("回憶記憶管理演示")
    print("=" * 60)

    recall = RecallMemoryManager()

    # 模擬對話
    messages = [
        ("user", "你好，我想學習 Python"),
        ("assistant", "很高興幫助你！Python 是一門很棒的語言。"),
        ("user", "我應該從哪裡開始？"),
        ("assistant", "建議從基礎語法開始，然後學習數據結構。"),
        ("user", "有推薦的學習資源嗎？"),
        ("assistant", "推薦 Python 官方教程和《Python Crash Course》。")
    ]

    for role, content in messages:
        recall.add_message(role, content)

    # 獲取最近消息
    recall.get_recent_messages(3)

    # 搜索消息
    recall.search_messages("學習")

    # 對話摘要
    recall.get_conversation_summary()


def demonstrate_integrated_system():
    """演示集成記憶系統"""
    print("\n" + "=" * 60)
    print("集成記憶系統演示")
    print("=" * 60)

    system = IntegratedMemorySystem()

    # 設置基本信息
    system.core.set_persona("你是一個學習輔導 AI 助手")
    system.core.set_human("用戶是一個想學習編程的初學者")

    # 模擬對話
    system.process_user_message("我叫王小明，想學習 Python 編程")
    system.process_assistant_response("很高興認識你，王小明！Python 是個很好的選擇。")

    system.process_user_message("我之前沒有編程經驗")
    system.process_assistant_response("沒關係，我們從基礎開始，一步步來。")

    # 智能回憶
    time.sleep(1)
    system.smart_recall("王小明")
    time.sleep(1)
    system.smart_recall("Python")


def main():
    """主函數：運行所有演示"""
    print("\n" + "=" * 70)
    print(" " * 20 + "Letta 記憶管理深度解析")
    print("=" * 70)

    # 核心記憶演示
    demonstrate_core_memory()

    # 歸檔記憶演示
    demonstrate_archival_memory()

    # 回憶記憶演示
    demonstrate_recall_memory()

    # 集成系統演示
    demonstrate_integrated_system()

    print("\n" + "=" * 70)
    print("記憶管理演示完成！")
    print("=" * 70)
    print("\n關鍵要點：")
    print("  1. 核心記憶：存儲最重要的信息，容量有限")
    print("  2. 歸檔記憶：長期存儲，通過向量搜索訪問")
    print("  3. 回憶記憶：完整的對話歷史")
    print("  4. 三層協同：共同構建完整的記憶系統")
    print("\n下一步：查看 03_對話持久化.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
