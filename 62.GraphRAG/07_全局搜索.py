"""
GraphRAG 全局搜索示例

這個示例展示了如何實現 Global Search：
1. 基於社區摘要的搜索
2. 多層次信息聚合
3. 主題發現和總結
4. Map-Reduce 答案生成

Author: GraphRAG Team
Date: 2025-12-31
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class GlobalSearchResult:
    """全局搜索結果數據類"""
    answer: str
    communities: List[Dict[str, Any]]
    key_points: List[str]
    confidence: float
    reasoning: str


class GlobalSearchEngine:
    """全局搜索引擎：基於社區摘要的宏觀查詢"""

    def __init__(self, communities: List[Dict[str, Any]]):
        """
        初始化全局搜索引擎

        Args:
            communities: 社區列表（包含摘要）
        """
        self.communities = communities

    def search(
            self,
            query: str,
            top_k: int = 10,
            level: int = 0
    ) -> GlobalSearchResult:
        """
        執行全局搜索

        Args:
            query: 查詢問題
            top_k: 返回最相關的 K 個社區
            level: 社區層級（0=最細粒度）

        Returns:
            搜索結果
        """
        print(f"\n🌍 執行全局搜索")
        print(f"   查詢: {query}")
        print(f"   參數: top_k={top_k}, level={level}")

        # 步驟 1: 過濾指定層級的社區
        print(f"\n   步驟 1: 過濾層級 {level} 的社區...")
        level_communities = [
            comm for comm in self.communities
            if comm.get("level", 0) == level
        ]
        print(f"   ✓ 找到 {len(level_communities)} 個社區")

        # 步驟 2: 計算社區相關性
        print(f"\n   步驟 2: 計算社區相關性...")
        scored_communities = self._rank_communities(query, level_communities)
        top_communities = scored_communities[:top_k]
        print(f"   ✓ 選擇了 {len(top_communities)} 個最相關的社區")

        # 步驟 3: Map 階段 - 為每個社區生成局部答案
        print(f"\n   步驟 3: Map 階段 - 生成局部答案...")
        partial_answers = self._map_phase(query, top_communities)
        print(f"   ✓ 生成了 {len(partial_answers)} 個局部答案")

        # 步驟 4: Reduce 階段 - 聚合為最終答案
        print(f"\n   步驟 4: Reduce 階段 - 聚合最終答案...")
        final_answer, key_points = self._reduce_phase(query, partial_answers)
        print(f"   ✓ 答案生成完成")

        # 構建結果
        result = GlobalSearchResult(
            answer=final_answer,
            communities=[comm for comm, _ in top_communities],
            key_points=key_points,
            confidence=0.88,
            reasoning=f"基於 {len(top_communities)} 個社區的摘要生成答案"
        )

        print(f"   ✓ 搜索完成")

        return result

    def _rank_communities(
            self,
            query: str,
            communities: List[Dict[str, Any]]
    ) -> List[tuple]:
        """
        對社區進行相關性排序

        Args:
            query: 查詢文本
            communities: 社區列表

        Returns:
            排序後的 (社區, 分數) 列表
        """
        scored = []

        for comm in communities:
            score = self._calculate_relevance(query, comm)
            scored.append((comm, score))

        # 按分數降序排序
        scored.sort(key=lambda x: x[1], reverse=True)

        return scored

    def _calculate_relevance(
            self,
            query: str,
            community: Dict[str, Any]
    ) -> float:
        """
        計算社區與查詢的相關性

        Args:
            query: 查詢文本
            community: 社區對象

        Returns:
            相關性分數 (0-1)
        """
        # 簡化的相關性計算
        # 實際應用中會使用嵌入向量相似度

        score = 0.0
        query_lower = query.lower()

        # 1. 標題匹配
        title = community.get("title", "").lower()
        if any(word in title for word in query_lower.split()):
            score += 0.3

        # 2. 摘要匹配
        summary = community.get("summary", "").lower()
        matching_words = sum(1 for word in query_lower.split() if word in summary)
        score += min(0.4, matching_words * 0.1)

        # 3. 實體匹配
        entities = community.get("entities", [])
        entity_matches = sum(1 for entity in entities if entity.lower() in query_lower)
        score += min(0.3, entity_matches * 0.15)

        return min(1.0, score)

    def _map_phase(
            self,
            query: str,
            communities: List[tuple]
    ) -> List[Dict[str, Any]]:
        """
        Map 階段：為每個社區生成局部答案

        Args:
            query: 查詢問題
            communities: 社區列表（帶分數）

        Returns:
            局部答案列表
        """
        partial_answers = []

        for comm, relevance_score in communities:
            # 生成局部答案
            partial_answer = self._generate_partial_answer(query, comm, relevance_score)
            partial_answers.append(partial_answer)

        return partial_answers

    def _generate_partial_answer(
            self,
            query: str,
            community: Dict[str, Any],
            relevance_score: float
    ) -> Dict[str, Any]:
        """
        為單個社區生成局部答案

        Args:
            query: 查詢問題
            community: 社區對象
            relevance_score: 相關性分數

        Returns:
            局部答案字典
        """
        # 實際應用中會調用 LLM
        # 這裡使用模擬邏輯

        comm_id = community.get("id", 0)
        title = community.get("title", "")
        summary = community.get("summary", "")
        entities = community.get("entities", [])

        # 模擬生成局部答案
        if relevance_score > 0.5:
            partial_text = (
                f"從「{title}」社區的角度來看，{summary} "
                f"相關實體包括：{', '.join(entities[:3])}。"
            )
        else:
            partial_text = f"{title}社區提供了一些背景信息。"

        return {
            "community_id": comm_id,
            "community_title": title,
            "text": partial_text,
            "relevance_score": relevance_score,
            "entities": entities
        }

    def _reduce_phase(
            self,
            query: str,
            partial_answers: List[Dict[str, Any]]
    ) -> tuple:
        """
        Reduce 階段：聚合局部答案為最終答案

        Args:
            query: 查詢問題
            partial_answers: 局部答案列表

        Returns:
            (最終答案, 關鍵點列表)
        """
        # 實際應用中會調用 LLM 進行高級聚合
        # 這裡使用簡化的聚合邏輯

        # 按相關性排序
        sorted_answers = sorted(
            partial_answers,
            key=lambda x: x["relevance_score"],
            reverse=True
        )

        # 提取關鍵點
        key_points = []
        for answer in sorted_answers[:5]:
            if answer["relevance_score"] > 0.3:
                key_points.append(
                    f"• {answer['community_title']}: {answer['text']}"
                )

        # 生成最終答案
        if sorted_answers:
            top_answer = sorted_answers[0]
            final_answer = self._synthesize_final_answer(query, sorted_answers)
        else:
            final_answer = "無法找到相關信息來回答這個問題。"
            key_points = []

        return final_answer, key_points

    def _synthesize_final_answer(
            self,
            query: str,
            partial_answers: List[Dict[str, Any]]
    ) -> str:
        """
        合成最終答案

        Args:
            query: 查詢問題
            partial_answers: 局部答案列表

        Returns:
            最終答案字符串
        """
        # 簡化的答案合成
        high_relevance_answers = [
            ans for ans in partial_answers
            if ans["relevance_score"] > 0.4
        ]

        if not high_relevance_answers:
            return "基於可用信息，無法提供確切答案。"

        # 收集所有社區的主題
        themes = [ans["community_title"] for ans in high_relevance_answers[:5]]

        # 收集關鍵實體
        all_entities = []
        for ans in high_relevance_answers:
            all_entities.extend(ans.get("entities", []))
        unique_entities = list(set(all_entities))[:10]

        # 構建答案
        answer_parts = []

        # 開頭
        if "主要" in query or "主題" in query or "趨勢" in query:
            answer_parts.append(f"根據對數據的分析，主要主題包括：{', '.join(themes[:3])}。")
        else:
            answer_parts.append(f"基於多個社區的信息，")

        # 中間部分 - 整合局部答案
        for i, ans in enumerate(high_relevance_answers[:3], 1):
            answer_parts.append(ans["text"])

        # 結尾 - 總結
        if unique_entities:
            answer_parts.append(
                f"\n\n關鍵實體包括：{', '.join(unique_entities[:8])}等。"
            )

        return " ".join(answer_parts)


def display_global_search_result(result: GlobalSearchResult):
    """
    顯示全局搜索結果

    Args:
        result: 搜索結果
    """
    print(f"\n" + "=" * 70)
    print("🌍 全局搜索結果")
    print("=" * 70)

    print(f"\n答案:")
    print(f"  {result.answer}")

    print(f"\n置信度: {result.confidence:.2%}")
    print(f"推理過程: {result.reasoning}")

    if result.key_points:
        print(f"\n關鍵要點:")
        for point in result.key_points:
            print(f"  {point}")

    if result.communities:
        print(f"\n相關社區 ({len(result.communities)} 個):")
        for i, comm in enumerate(result.communities[:5], 1):
            print(f"\n  {i}. {comm.get('title', 'Unknown')}")
            print(f"     大小: {comm.get('size', 0)} 個實體")
            print(f"     摘要: {comm.get('summary', '')[:150]}...")


def create_sample_communities() -> List[Dict[str, Any]]:
    """創建示例社區數據"""
    communities = [
        {
            "id": 0,
            "level": 0,
            "title": "深度學習先驅",
            "summary": "這個社區聚焦於深度學習領域的開創性人物和他們的貢獻。Geoffrey Hinton、Yoshua Bengio 和 Yann LeCun 被稱為深度學習三巨頭，他們的研究奠定了現代深度學習的基礎。",
            "entities": ["Geoffrey Hinton", "Yoshua Bengio", "Yann LeCun", "深度學習", "神經網絡"],
            "size": 5
        },
        {
            "id": 1,
            "level": 0,
            "title": "大型語言模型",
            "summary": "這個社區包含了當前主流的大型語言模型產品和開發公司。OpenAI 的 ChatGPT、Google 的 Bard 和 Anthropic 的 Claude 代表了 LLM 技術的最新進展。",
            "entities": ["ChatGPT", "GPT-4", "OpenAI", "Bard", "Google", "Claude", "Anthropic"],
            "size": 7
        },
        {
            "id": 2,
            "level": 0,
            "title": "知識圖譜技術",
            "summary": "這個社區關注知識圖譜及相關技術。Google 在 2012 年提出知識圖譜概念，GraphRAG 則是 Microsoft 開發的新型 RAG 框架，結合了知識圖譜和檢索增強生成技術。",
            "entities": ["Knowledge Graph", "GraphRAG", "Microsoft", "RAG", "DBpedia"],
            "size": 5
        },
        {
            "id": 3,
            "level": 0,
            "title": "AI 發展歷史",
            "summary": "追溯人工智能的發展歷程。從 1956 年 John McCarthy 提出 AI 概念，到符號主義、專家系統，再到深度學習革命，AI 經歷了多個重要階段。",
            "entities": ["人工智能", "John McCarthy", "達特茅斯會議", "專家系統"],
            "size": 4
        },
        {
            "id": 4,
            "level": 0,
            "title": "向量數據庫與嵌入",
            "summary": "這個社區涉及向量數據庫和嵌入技術，這些是現代 RAG 系統的核心組件。向量嵌入能夠將文本轉換為數值表示，支持語義搜索。",
            "entities": ["Vector Database", "Embedding", "Semantic Search", "FAISS", "Pinecone"],
            "size": 5
        }
    ]

    return communities


def main():
    """
    主函數：演示全局搜索
    """
    print("=" * 70)
    print("🌍 GraphRAG 全局搜索示例".center(70))
    print("=" * 70)
    print()

    # 加載環境變量
    load_dotenv()

    # 準備數據
    print("準備示例社區數據...")
    communities = create_sample_communities()
    print(f"✓ 加載了 {len(communities)} 個社區")
    print()

    # 創建搜索引擎
    search_engine = GlobalSearchEngine(communities)

    # 示例查詢（適合全局搜索的問題）
    queries = [
        "這個數據集的主要主題是什麼？",
        "AI 領域有哪些重要的發展趨勢？",
        "知識圖譜技術如何應用於 RAG？",
        "誰是深度學習領域的關鍵人物？"
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{'=' * 70}")
        print(f"查詢 {i}: {query}")
        print(f"{'=' * 70}")

        result = search_engine.search(query, top_k=5, level=0)
        display_global_search_result(result)

        if i < len(queries):
            print("\n" + "-" * 70)

    # 總結
    print("\n\n" + "=" * 70)
    print("💡 Global Search 要點")
    print("=" * 70)
    print("""
    1. 適用場景：
       • 需要全局理解的問題
       • 主題發現和總結
       • 趨勢分析
       • 開放式探索

    2. Map-Reduce 流程：
       • Map: 為每個社區生成局部答案
       • Reduce: 聚合局部答案為最終答案
       • 支持大規模並行處理

    3. 與 Local Search 對比：
       ┌─────────────────┬──────────────┬──────────────┐
       │                 │ Local Search │ Global Search│
       ├─────────────────┼──────────────┼──────────────┤
       │ 查詢類型        │ 特定事實     │ 主題總結     │
       │ 數據源          │ 實體+關係    │ 社區摘要     │
       │ 答案類型        │ 精確         │ 概括性       │
       │ 計算成本        │ 中           │ 高           │
       │ 可擴展性        │ 中           │ 優秀         │
       └─────────────────┴──────────────┴──────────────┘

    4. 優勢：
       • 能回答需要全局視角的問題
       • 自動發現主題和模式
       • 適合大規模數據集
       • 提供多角度的綜合答案

    5. 優化策略：
       • 層次化社區結構（粗粒度到細粒度）
       • 緩存社區摘要
       • 並行處理 Map 階段
       • 動態調整 top_k 參數

    6. 實際應用：
       • 文獻綜述
       • 市場分析
       • 競爭情報
       • 知識發現

    📚 下一步：查看 08_混合查詢.py 了解如何結合兩種搜索方式
    """)

    print("✅ 全局搜索示例完成！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  程序被用戶中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 程序執行出錯: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
