"""
GraphRAG 本地搜索示例

這個示例展示了如何實現 Local Search：
1. 基於實體的精確檢索
2. 關係路徑查找
3. 上下文擴展
4. 答案生成

Author: GraphRAG Team
Date: 2025-12-31
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv
import networkx as nx


@dataclass
class SearchResult:
    """搜索結果數據類"""
    answer: str
    entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    source_chunks: List[str]
    confidence: float
    reasoning: str


class LocalSearchEngine:
    """本地搜索引擎：基於實體和關係的精確搜索"""

    def __init__(
            self,
            graph: nx.MultiDiGraph,
            entities: Dict[str, Dict[str, Any]],
            text_chunks: Dict[str, str]
    ):
        """
        初始化本地搜索引擎

        Args:
            graph: 知識圖譜
            entities: 實體字典
            text_chunks: 文本塊字典
        """
        self.graph = graph
        self.entities = entities
        self.text_chunks = text_chunks

    def search(
            self,
            query: str,
            top_k: int = 5,
            max_hops: int = 2
    ) -> SearchResult:
        """
        執行本地搜索

        Args:
            query: 查詢問題
            top_k: 返回最相關的 K 個結果
            max_hops: 最大跳數（關係路徑長度）

        Returns:
            搜索結果
        """
        print(f"\n🔍 執行本地搜索")
        print(f"   查詢: {query}")
        print(f"   參數: top_k={top_k}, max_hops={max_hops}")

        # 步驟 1: 實體識別
        print(f"\n   步驟 1: 識別查詢中的實體...")
        query_entities = self._extract_query_entities(query)
        print(f"   ✓ 識別到 {len(query_entities)} 個實體: {query_entities}")

        if not query_entities:
            print(f"   ⚠️  未識別到實體，使用關鍵詞搜索")
            return self._keyword_fallback_search(query)

        # 步驟 2: 獲取相關實體和關係
        print(f"\n   步驟 2: 獲取相關實體和關係...")
        relevant_entities, relevant_relationships = self._get_relevant_context(
            query_entities,
            max_hops
        )
        print(f"   ✓ 找到 {len(relevant_entities)} 個相關實體")
        print(f"   ✓ 找到 {len(relevant_relationships)} 個相關關係")

        # 步驟 3: 獲取源文本
        print(f"\n   步驟 3: 獲取源文本...")
        source_chunks = self._get_source_chunks(relevant_entities)
        print(f"   ✓ 找到 {len(source_chunks)} 個源文本塊")

        # 步驟 4: 生成答案
        print(f"\n   步驟 4: 生成答案...")
        answer, confidence, reasoning = self._generate_answer(
            query,
            relevant_entities,
            relevant_relationships,
            source_chunks
        )

        # 構建結果
        result = SearchResult(
            answer=answer,
            entities=relevant_entities,
            relationships=relevant_relationships,
            source_chunks=list(source_chunks),
            confidence=confidence,
            reasoning=reasoning
        )

        print(f"   ✓ 搜索完成")

        return result

    def _extract_query_entities(self, query: str) -> List[str]:
        """
        從查詢中提取實體

        Args:
            query: 查詢文本

        Returns:
            實體名稱列表
        """
        # 簡化的實體識別（實際應使用 NER 或 LLM）
        found_entities = []

        # 檢查查詢中是否包含已知實體
        for entity_name in self.entities.keys():
            if entity_name.lower() in query.lower():
                found_entities.append(entity_name)

        # 也檢查圖中的節點
        for node in self.graph.nodes():
            if node.lower() in query.lower() and node not in found_entities:
                found_entities.append(node)

        return found_entities

    def _get_relevant_context(
            self,
            query_entities: List[str],
            max_hops: int
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        獲取相關的實體和關係

        Args:
            query_entities: 查詢實體列表
            max_hops: 最大跳數

        Returns:
            (相關實體列表, 相關關係列表)
        """
        relevant_entities = []
        relevant_relationships = []
        visited_nodes = set()

        # 從每個查詢實體開始擴展
        for entity in query_entities:
            if entity not in self.graph:
                continue

            # 獲取 N 跳範圍內的鄰居
            neighbors = self._get_neighbors_within_hops(entity, max_hops)

            for neighbor in neighbors:
                if neighbor not in visited_nodes:
                    visited_nodes.add(neighbor)

                    # 獲取實體信息
                    entity_info = {
                        "name": neighbor,
                        "type": self.graph.nodes[neighbor].get("type", "UNKNOWN"),
                        "description": self.graph.nodes[neighbor].get("description", "")
                    }
                    relevant_entities.append(entity_info)

                    # 獲取相關關係
                    for pred in self.graph.predecessors(neighbor):
                        if pred in visited_nodes or pred == neighbor:
                            continue

                        edge_data = self.graph.get_edge_data(pred, neighbor)
                        if edge_data:
                            # 對於 MultiDiGraph
                            if isinstance(edge_data, dict) and 0 in edge_data:
                                edge_info = edge_data[0]
                            else:
                                edge_info = edge_data

                            rel_info = {
                                "source": pred,
                                "target": neighbor,
                                "type": edge_info.get("type", "RELATED_TO"),
                                "description": edge_info.get("description", "")
                            }
                            relevant_relationships.append(rel_info)

                    for succ in self.graph.successors(neighbor):
                        if succ in visited_nodes or succ == neighbor:
                            continue

                        edge_data = self.graph.get_edge_data(neighbor, succ)
                        if edge_data:
                            if isinstance(edge_data, dict) and 0 in edge_data:
                                edge_info = edge_data[0]
                            else:
                                edge_info = edge_data

                            rel_info = {
                                "source": neighbor,
                                "target": succ,
                                "type": edge_info.get("type", "RELATED_TO"),
                                "description": edge_info.get("description", "")
                            }
                            relevant_relationships.append(rel_info)

        return relevant_entities, relevant_relationships

    def _get_neighbors_within_hops(self, node: str, max_hops: int) -> set:
        """
        獲取 N 跳範圍內的所有鄰居

        Args:
            node: 起始節點
            max_hops: 最大跳數

        Returns:
            鄰居節點集合
        """
        if node not in self.graph:
            return set()

        neighbors = {node}
        current_level = {node}

        for _ in range(max_hops):
            next_level = set()

            for current_node in current_level:
                # 獲取所有鄰居（前驅和後繼）
                preds = set(self.graph.predecessors(current_node))
                succs = set(self.graph.successors(current_node))
                next_level.update(preds | succs)

            # 添加新發現的節點
            new_nodes = next_level - neighbors
            if not new_nodes:
                break

            neighbors.update(new_nodes)
            current_level = new_nodes

        return neighbors

    def _get_source_chunks(self, entities: List[Dict[str, Any]]) -> set:
        """
        獲取實體的源文本塊

        Args:
            entities: 實體列表

        Returns:
            源文本塊 ID 集合
        """
        source_chunks = set()

        for entity in entities:
            entity_name = entity["name"]
            if entity_name in self.graph.nodes():
                chunks = self.graph.nodes[entity_name].get("source_chunks", [])
                source_chunks.update(chunks)

        return source_chunks

    def _generate_answer(
            self,
            query: str,
            entities: List[Dict[str, Any]],
            relationships: List[Dict[str, Any]],
            source_chunks: set
    ) -> Tuple[str, float, str]:
        """
        生成答案

        Args:
            query: 查詢問題
            entities: 相關實體
            relationships: 相關關係
            source_chunks: 源文本塊

        Returns:
            (答案, 置信度, 推理過程)
        """
        # 實際應用中會調用 LLM
        # 這裡使用簡化的模擬邏輯

        # 構建上下文
        context_parts = []

        # 添加實體信息
        context_parts.append("相關實體:")
        for entity in entities[:10]:  # 限制數量
            context_parts.append(
                f"- {entity['name']} ({entity['type']}): {entity.get('description', '')}"
            )

        # 添加關係信息
        context_parts.append("\n相關關係:")
        for rel in relationships[:10]:
            context_parts.append(
                f"- {rel['source']} --[{rel['type']}]--> {rel['target']}"
            )

        # 添加源文本
        if source_chunks and self.text_chunks:
            context_parts.append("\n源文本:")
            for chunk_id in list(source_chunks)[:3]:
                if chunk_id in self.text_chunks:
                    text = self.text_chunks[chunk_id][:200]  # 限制長度
                    context_parts.append(f"- {text}...")

        context = "\n".join(context_parts)

        # 模擬答案生成
        answer = self._mock_answer_generation(query, entities, relationships)
        confidence = 0.85
        reasoning = f"基於 {len(entities)} 個實體和 {len(relationships)} 個關係生成答案"

        return answer, confidence, reasoning

    def _mock_answer_generation(
            self,
            query: str,
            entities: List[Dict[str, Any]],
            relationships: List[Dict[str, Any]]
    ) -> str:
        """
        模擬答案生成

        Args:
            query: 查詢問題
            entities: 實體列表
            relationships: 關係列表

        Returns:
            答案字符串
        """
        # 簡單的啟發式答案生成
        if not entities:
            return "抱歉，我無法找到相關信息來回答這個問題。"

        # 提取關鍵信息
        entity_names = [e["name"] for e in entities]

        # 根據查詢類型生成答案
        if "是誰" in query or "是什麼人" in query:
            # 人物查詢
            persons = [e for e in entities if e.get("type") == "PERSON"]
            if persons:
                person = persons[0]
                answer = f"{person['name']} {person.get('description', '是一位重要人物')}。"
            else:
                answer = f"相關的人物包括：{', '.join(entity_names[:3])}。"

        elif "什麼時候" in query or "何時" in query:
            # 時間查詢
            answer = "根據現有信息，具體時間信息需要進一步查詢。"

        elif "為什麼" in query or "原因" in query:
            # 原因查詢
            answer = f"這涉及到 {', '.join(entity_names[:3])} 等多個因素。"

        else:
            # 一般查詢
            if relationships:
                rel = relationships[0]
                answer = (
                    f"{rel['source']} 與 {rel['target']} 之間存在 {rel['type']} 關係。"
                    f"相關實體還包括：{', '.join(entity_names[:3])}。"
                )
            else:
                answer = f"相關的主要實體包括：{', '.join(entity_names[:5])}。"

        return answer

    def _keyword_fallback_search(self, query: str) -> SearchResult:
        """
        關鍵詞回退搜索（當無法識別實體時）

        Args:
            query: 查詢文本

        Returns:
            搜索結果
        """
        # 簡化的關鍵詞搜索
        return SearchResult(
            answer="無法識別查詢中的實體，請嘗試更具體的問題。",
            entities=[],
            relationships=[],
            source_chunks=[],
            confidence=0.3,
            reasoning="關鍵詞回退搜索"
        )


def display_search_result(result: SearchResult):
    """
    顯示搜索結果

    Args:
        result: 搜索結果
    """
    print(f"\n" + "=" * 70)
    print("📊 搜索結果")
    print("=" * 70)

    print(f"\n答案:")
    print(f"  {result.answer}")

    print(f"\n置信度: {result.confidence:.2%}")
    print(f"推理過程: {result.reasoning}")

    if result.entities:
        print(f"\n相關實體 ({len(result.entities)} 個):")
        for entity in result.entities[:5]:
            print(f"  • {entity['name']} ({entity['type']})")
            if entity.get('description'):
                print(f"    {entity['description']}")

    if result.relationships:
        print(f"\n相關關係 ({len(result.relationships)} 個):")
        for rel in result.relationships[:5]:
            print(f"  • {rel['source']} --[{rel['type']}]--> {rel['target']}")

    if result.source_chunks:
        print(f"\n證據來源: {len(result.source_chunks)} 個文本塊")


def create_sample_data() -> Tuple[nx.MultiDiGraph, Dict, Dict]:
    """創建示例數據"""

    # 創建圖
    G = nx.MultiDiGraph()

    # 添加節點
    entities = {
        "Geoffrey Hinton": {
            "type": "PERSON",
            "description": "深度學習先驅，2018 年圖靈獎得主",
            "source_chunks": ["chunk_1"]
        },
        "Yoshua Bengio": {
            "type": "PERSON",
            "description": "深度學習專家，2018 年圖靈獎得主",
            "source_chunks": ["chunk_1"]
        },
        "Yann LeCun": {
            "type": "PERSON",
            "description": "深度學習專家，卷積神經網絡先驅",
            "source_chunks": ["chunk_1"]
        },
        "深度學習": {
            "type": "CONCEPT",
            "description": "機器學習的一個分支",
            "source_chunks": ["chunk_1", "chunk_2"]
        },
        "ChatGPT": {
            "type": "PRODUCT",
            "description": "OpenAI 開發的大型語言模型",
            "source_chunks": ["chunk_2"]
        },
        "OpenAI": {
            "type": "ORGANIZATION",
            "description": "AI 研究公司",
            "source_chunks": ["chunk_2"]
        }
    }

    for name, attrs in entities.items():
        G.add_node(name, **attrs)

    # 添加關係
    G.add_edge("Geoffrey Hinton", "深度學習", type="CONTRIBUTED_TO",
               description="對深度學習做出重要貢獻", weight=0.95)
    G.add_edge("Yoshua Bengio", "深度學習", type="CONTRIBUTED_TO",
               description="對深度學習做出重要貢獻", weight=0.95)
    G.add_edge("Yann LeCun", "深度學習", type="CONTRIBUTED_TO",
               description="對深度學習做出重要貢獻", weight=0.95)
    G.add_edge("OpenAI", "ChatGPT", type="DEVELOPED",
               description="開發了 ChatGPT", weight=1.0)
    G.add_edge("ChatGPT", "深度學習", type="BASED_ON",
               description="基於深度學習技術", weight=0.9)

    # 文本塊
    text_chunks = {
        "chunk_1": "Geoffrey Hinton、Yoshua Bengio 和 Yann LeCun 被稱為深度學習三巨頭，他們因對深度學習的貢獻而獲得 2018 年圖靈獎。",
        "chunk_2": "OpenAI 開發了 ChatGPT，這是一個基於深度學習技術的大型語言模型。"
    }

    return G, entities, text_chunks


def main():
    """
    主函數：演示本地搜索
    """
    print("=" * 70)
    print("🔍 GraphRAG 本地搜索示例".center(70))
    print("=" * 70)
    print()

    # 加載環境變量
    load_dotenv()

    # 準備數據
    print("準備示例數據...")
    graph, entities, text_chunks = create_sample_data()
    print(f"✓ 圖譜: {graph.number_of_nodes()} 個節點, {graph.number_of_edges()} 條邊")
    print()

    # 創建搜索引擎
    search_engine = LocalSearchEngine(graph, entities, text_chunks)

    # 示例查詢
    queries = [
        "誰是深度學習三巨頭？",
        "OpenAI 開發了什麼產品？",
        "深度學習有什麼應用？",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{'=' * 70}")
        print(f"查詢 {i}: {query}")
        print(f"{'=' * 70}")

        result = search_engine.search(query, top_k=5, max_hops=2)
        display_search_result(result)

    # 總結
    print("\n\n" + "=" * 70)
    print("💡 Local Search 要點")
    print("=" * 70)
    print("""
    1. 適用場景：
       • 特定事實查詢（人物、日期、地點）
       • 需要精確答案的問題
       • 實體關係查詢

    2. 工作流程：
       • 識別查詢中的實體
       • 擴展到相關實體和關係
       • 獲取源文本作為證據
       • 生成答案並提供引用

    3. 優勢：
       • 精確度高
       • 可解釋性強（提供證據鏈）
       • 支持多跳推理

    4. 優化策略：
       • 實體鏈接優化
       • 動態調整跳數
       • 結果排序和過濾
       • 緩存常見查詢

    📚 下一步：查看 07_全局搜索.py 了解 Global Search 的實現
    """)

    print("✅ 本地搜索示例完成！")


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
