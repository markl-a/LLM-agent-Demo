"""
Google ADK - 記憶管理範例

這個範例展示如何管理 Agent 的記憶系統：
- 對話記憶
- 長期記憶存儲
- 向量記憶（語義搜索）
- 記憶檢索和更新
- 記憶壓縮和清理
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
from google_adk import Agent
from google_adk.models import GeminiPro
from google_adk.memory import (
    ConversationMemory,
    LongTermMemory,
    VectorMemory,
    MemoryManager
)


class MemoryManagementExample:
    """記憶管理範例類"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化記憶管理範例"""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("請設置 GOOGLE_API_KEY 環境變量")

    def example_1_conversation_memory(self):
        """範例 1: 對話記憶"""
        print("\n" + "="*60)
        print("範例 1: 對話記憶")
        print("="*60)

        # 創建對話記憶
        memory = ConversationMemory(
            max_turns=10,        # 最多保留 10 輪對話
            summary_threshold=5  # 超過 5 輪後自動摘要
        )

        # 創建帶記憶的 Agent
        agent = Agent(
            model=GeminiPro(),
            memory=memory,
            name="memory-agent"
        )

        # 多輪對話
        conversations = [
            "我叫張三，今年 30 歲。",
            "我是一名軟體工程師。",
            "我喜歡打籃球和閱讀。",
            "請告訴我，我叫什麼名字？",
            "我的職業是什麼？",
            "我有什麼興趣愛好？"
        ]

        print("\n對話記錄:")
        for i, user_msg in enumerate(conversations, 1):
            print(f"\n輪次 {i}:")
            print(f"  用戶: {user_msg}")

            # 模擬 Agent 響應
            """
            response = agent.run(user_msg)
            print(f"  Agent: {response.content}")
            """

            # 記憶中的對話
            memory.add_turn(
                role="user",
                content=user_msg
            )

        # 顯示記憶統計
        print(f"\n記憶統計:")
        print(f"  對話輪數: {memory.turn_count}")
        print(f"  記憶大小: {memory.size} bytes")

        return agent

    def example_2_long_term_memory(self):
        """範例 2: 長期記憶"""
        print("\n" + "="*60)
        print("範例 2: 長期記憶")
        print("="*60)

        # 創建長期記憶
        lt_memory = LongTermMemory(
            backend="redis",  # 或 "postgres", "mongodb"
            namespace="user_profiles",
            ttl=None  # 永久存儲
        )

        # 存儲用戶信息
        user_data = {
            "user_id": "user-123",
            "name": "張三",
            "preferences": {
                "language": "zh-TW",
                "timezone": "Asia/Taipei",
                "interests": ["AI", "編程", "閱讀"]
            },
            "history": {
                "last_login": datetime.now().isoformat(),
                "interaction_count": 42
            }
        }

        print("存儲用戶數據:")
        print(json.dumps(user_data, indent=2, ensure_ascii=False))

        # 存儲到長期記憶
        lt_memory.store(
            key="user-123",
            value=user_data
        )

        # 檢索數據
        retrieved_data = lt_memory.retrieve("user-123")
        print(f"\n檢索成功: {retrieved_data is not None}")

        # 更新數據
        lt_memory.update(
            key="user-123",
            updates={
                "history.interaction_count": 43,
                "history.last_login": datetime.now().isoformat()
            }
        )

        print("✓ 數據更新完成")

        return lt_memory

    def example_3_vector_memory(self):
        """範例 3: 向量記憶（語義搜索）"""
        print("\n" + "="*60)
        print("範例 3: 向量記憶（語義搜索）")
        print("="*60)

        # 創建向量記憶
        vector_memory = VectorMemory(
            embedding_model="text-embedding-004",
            dimension=768,
            index_type="faiss"  # 或 "annoy", "hnsw"
        )

        # 添加知識條目
        knowledge_base = [
            {
                "id": "kb-1",
                "content": "Python 是一種高級編程語言，以其簡潔和可讀性著稱。",
                "metadata": {"category": "programming", "language": "python"}
            },
            {
                "id": "kb-2",
                "content": "機器學習是人工智能的一個分支，讓計算機從數據中學習。",
                "metadata": {"category": "AI", "topic": "machine_learning"}
            },
            {
                "id": "kb-3",
                "content": "深度學習使用神經網絡來處理複雜的模式識別任務。",
                "metadata": {"category": "AI", "topic": "deep_learning"}
            },
            {
                "id": "kb-4",
                "content": "自然語言處理讓計算機理解和生成人類語言。",
                "metadata": {"category": "AI", "topic": "NLP"}
            }
        ]

        print("構建知識庫:")
        for item in knowledge_base:
            vector_memory.add(
                id=item["id"],
                content=item["content"],
                metadata=item["metadata"]
            )
            print(f"  ✓ {item['id']}: {item['content'][:50]}...")

        # 語義搜索
        queries = [
            "什麼是編程語言？",
            "解釋人工智能",
            "神經網絡如何工作？"
        ]

        print("\n語義搜索:")
        for query in queries:
            print(f"\n查詢: {query}")
            results = vector_memory.search(
                query=query,
                top_k=2,
                threshold=0.7
            )

            print("  相關結果:")
            for i, result in enumerate(results, 1):
                print(f"    {i}. [{result['score']:.2f}] {result['content'][:60]}...")

        return vector_memory

    def example_4_memory_retrieval(self):
        """範例 4: 記憶檢索策略"""
        print("\n" + "="*60)
        print("範例 4: 記憶檢索策略")
        print("="*60)

        from google_adk.memory import MemoryRetriever

        # 創建記憶檢索器
        retriever = MemoryRetriever(
            strategies=[
                "recency",      # 最近使用
                "frequency",    # 使用頻率
                "relevance",    # 相關性
                "importance"    # 重要性
            ],
            weights={
                "recency": 0.3,
                "frequency": 0.2,
                "relevance": 0.4,
                "importance": 0.1
            }
        )

        # 模擬記憶條目
        memories = [
            {
                "id": "mem-1",
                "content": "用戶喜歡咖啡",
                "timestamp": datetime.now() - timedelta(hours=1),
                "access_count": 5,
                "importance": 0.8
            },
            {
                "id": "mem-2",
                "content": "用戶的生日是 3 月 15 日",
                "timestamp": datetime.now() - timedelta(days=30),
                "access_count": 2,
                "importance": 0.9
            },
            {
                "id": "mem-3",
                "content": "用戶在台北工作",
                "timestamp": datetime.now() - timedelta(hours=24),
                "access_count": 3,
                "importance": 0.7
            }
        ]

        print("記憶條目:")
        for mem in memories:
            print(f"  - {mem['id']}: {mem['content']}")

        # 檢索相關記憶
        query = "用戶的個人信息"
        relevant_memories = retriever.retrieve(
            query=query,
            memories=memories,
            top_k=2
        )

        print(f"\n查詢: {query}")
        print("檢索結果:")
        for mem in relevant_memories:
            print(f"  - {mem['content']} (得分: {mem.get('score', 0):.2f})")

        return retriever

    def example_5_memory_compression(self):
        """範例 5: 記憶壓縮"""
        print("\n" + "="*60)
        print("範例 5: 記憶壓縮")
        print("="*60)

        from google_adk.memory import MemoryCompressor

        # 創建記憶壓縮器
        compressor = MemoryCompressor(
            strategy="summarization",  # 摘要策略
            compression_ratio=0.3      # 壓縮到 30%
        )

        # 長對話記錄
        long_conversation = [
            {"role": "user", "content": "我想了解 Python"},
            {"role": "assistant", "content": "Python 是一種高級編程語言..."},
            {"role": "user", "content": "它有什麼特點？"},
            {"role": "assistant", "content": "Python 的主要特點包括..."},
            {"role": "user", "content": "如何開始學習？"},
            {"role": "assistant", "content": "學習 Python 可以從..."},
            # ... 更多對話
        ]

        print(f"原始對話長度: {len(long_conversation)} 輪")

        # 壓縮對話
        compressed = compressor.compress(long_conversation)

        print(f"壓縮後長度: {len(compressed)} 輪")
        print(f"壓縮比: {len(compressed)/len(long_conversation):.1%}")

        print("\n壓縮摘要:")
        print(compressed.get("summary", "用戶詢問了 Python 的基礎知識和學習方法..."))

        return compressor

    def example_6_memory_prioritization(self):
        """範例 6: 記憶優先級"""
        print("\n" + "="*60)
        print("範例 6: 記憶優先級")
        print("="*60)

        from google_adk.memory import MemoryPrioritizer

        # 創建優先級管理器
        prioritizer = MemoryPrioritizer(
            factors=[
                "recency",       # 新近度
                "frequency",     # 頻率
                "emotional",     # 情感強度
                "user_marked"    # 用戶標記
            ]
        )

        # 記憶條目
        memories = [
            {
                "content": "用戶的密碼提示問題",
                "recency_score": 0.5,
                "frequency_score": 0.3,
                "emotional_score": 0.2,
                "user_marked": True
            },
            {
                "content": "昨天的天氣查詢",
                "recency_score": 0.9,
                "frequency_score": 0.1,
                "emotional_score": 0.1,
                "user_marked": False
            },
            {
                "content": "用戶母親的生日",
                "recency_score": 0.4,
                "frequency_score": 0.8,
                "emotional_score": 0.9,
                "user_marked": True
            }
        ]

        print("計算記憶優先級:")
        for mem in memories:
            priority = prioritizer.calculate_priority(mem)
            mem["priority"] = priority
            print(f"  - {mem['content'][:30]}... : {priority:.2f}")

        # 排序
        sorted_memories = sorted(
            memories,
            key=lambda x: x["priority"],
            reverse=True
        )

        print("\n優先級排序:")
        for i, mem in enumerate(sorted_memories, 1):
            print(f"  {i}. [{mem['priority']:.2f}] {mem['content']}")

        return prioritizer

    def example_7_memory_cleanup(self):
        """範例 7: 記憶清理"""
        print("\n" + "="*60)
        print("範例 7: 記憶清理")
        print("="*60)

        from google_adk.memory import MemoryCleaner

        # 創建記憶清理器
        cleaner = MemoryCleaner(
            policies={
                "ttl": timedelta(days=30),      # 30 天過期
                "max_size": 1000,               # 最多 1000 條
                "importance_threshold": 0.3,    # 重要性閾值
                "access_threshold": 5           # 訪問次數閾值
            }
        )

        # 模擬記憶數據
        memories = []
        for i in range(50):
            memories.append({
                "id": f"mem-{i}",
                "content": f"記憶內容 {i}",
                "created_at": datetime.now() - timedelta(days=i),
                "access_count": i % 10,
                "importance": (i % 10) / 10
            })

        print(f"清理前記憶數量: {len(memories)}")

        # 執行清理
        cleaned_memories = cleaner.clean(memories)

        print(f"清理後記憶數量: {len(cleaned_memories)}")
        print(f"清理了 {len(memories) - len(cleaned_memories)} 條記憶")

        # 清理統計
        stats = cleaner.get_stats()
        print("\n清理統計:")
        print(f"  - 因過期刪除: {stats.get('expired', 0)}")
        print(f"  - 因重要性低刪除: {stats.get('low_importance', 0)}")
        print(f"  - 因訪問少刪除: {stats.get('low_access', 0)}")

        return cleaner

    def example_8_shared_memory(self):
        """範例 8: 共享記憶"""
        print("\n" + "="*60)
        print("範例 8: 共享記憶")
        print("="*60)

        from google_adk.memory import SharedMemory

        # 創建共享記憶空間
        shared_memory = SharedMemory(
            namespace="team_knowledge",
            access_control=True
        )

        # 多個 Agent 共享記憶
        agents = [
            Agent(model=GeminiPro(), name="agent-1", memory=shared_memory),
            Agent(model=GeminiPro(), name="agent-2", memory=shared_memory),
            Agent(model=GeminiPro(), name="agent-3", memory=shared_memory)
        ]

        print("共享記憶配置:")
        print(f"  命名空間: {shared_memory.namespace}")
        print(f"  訪問控制: {shared_memory.access_control}")
        print(f"  共享 Agent 數: {len(agents)}")

        # Agent-1 添加知識
        shared_memory.add(
            content="項目截止日期是下週五",
            added_by="agent-1",
            visibility="all"
        )

        # Agent-2 讀取知識
        knowledge = shared_memory.get_all(
            filter_by={"visibility": "all"}
        )

        print(f"\n共享知識條目: {len(knowledge)}")
        for item in knowledge:
            print(f"  - {item['content']} (來自: {item['added_by']})")

        return shared_memory

    def example_9_memory_export_import(self):
        """範例 9: 記憶導出和導入"""
        print("\n" + "="*60)
        print("範例 9: 記憶導出和導入")
        print("="*60)

        from google_adk.memory import MemoryIO

        # 創建記憶 I/O 管理器
        memory_io = MemoryIO()

        # 準備記憶數據
        memory_data = {
            "conversations": [
                {"role": "user", "content": "你好"},
                {"role": "assistant", "content": "你好！有什麼可以幫你的嗎？"}
            ],
            "facts": [
                {"key": "user_name", "value": "張三"},
                {"key": "user_age", "value": 30}
            ],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        }

        print("記憶數據:")
        print(json.dumps(memory_data, indent=2, ensure_ascii=False))

        # 導出記憶
        export_path = "/tmp/agent_memory.json"
        memory_io.export_memory(
            memory_data,
            path=export_path,
            format="json"  # 或 "pickle", "msgpack"
        )
        print(f"\n✓ 記憶已導出到: {export_path}")

        # 導入記憶
        imported_data = memory_io.import_memory(
            path=export_path,
            format="json"
        )
        print(f"✓ 記憶已導入: {len(imported_data)} 個鍵")

        return memory_io

    def example_10_memory_analytics(self):
        """範例 10: 記憶分析"""
        print("\n" + "="*60)
        print("範例 10: 記憶分析")
        print("="*60)

        from google_adk.memory import MemoryAnalytics

        # 創建記憶分析器
        analytics = MemoryAnalytics()

        # 模擬記憶數據
        memory_data = {
            "total_memories": 500,
            "active_memories": 350,
            "archived_memories": 150,
            "average_age_days": 15,
            "memory_categories": {
                "personal": 200,
                "work": 150,
                "general": 100,
                "temporary": 50
            },
            "access_patterns": {
                "daily_access": 50,
                "weekly_access": 200,
                "monthly_access": 250
            }
        }

        print("記憶統計分析:")
        print(f"  總記憶數: {memory_data['total_memories']}")
        print(f"  活躍記憶: {memory_data['active_memories']}")
        print(f"  歸檔記憶: {memory_data['archived_memories']}")
        print(f"  平均年齡: {memory_data['average_age_days']} 天")

        print("\n記憶分類:")
        for category, count in memory_data['memory_categories'].items():
            percentage = (count / memory_data['total_memories']) * 100
            print(f"  - {category}: {count} ({percentage:.1f}%)")

        print("\n訪問模式:")
        for pattern, count in memory_data['access_patterns'].items():
            print(f"  - {pattern}: {count}")

        # 生成建議
        recommendations = analytics.get_recommendations(memory_data)
        print("\n優化建議:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")

        return analytics


def main():
    """主函數"""
    print("="*60)
    print("Google ADK - 記憶管理範例")
    print("="*60)

    # 檢查 API 密鑰
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n⚠️  請先設置 GOOGLE_API_KEY 環境變量")
        print("export GOOGLE_API_KEY='your-api-key-here'")
        return

    # 創建範例實例
    example = MemoryManagementExample()

    try:
        # 運行所有範例
        example.example_1_conversation_memory()
        example.example_2_long_term_memory()
        example.example_3_vector_memory()
        example.example_4_memory_retrieval()
        example.example_5_memory_compression()
        example.example_6_memory_prioritization()
        example.example_7_memory_cleanup()
        example.example_8_shared_memory()
        example.example_9_memory_export_import()
        example.example_10_memory_analytics()

        print("\n" + "="*60)
        print("所有記憶管理範例執行完成！")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 執行錯誤: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
