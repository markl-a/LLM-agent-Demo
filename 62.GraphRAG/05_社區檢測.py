"""
GraphRAG 社區檢測示例

這個示例展示了如何進行社區發現：
1. 使用 Leiden 算法進行社區檢測
2. 層次化社區結構
3. 社區摘要生成
4. 社區質量評估

Author: GraphRAG Team
Date: 2025-12-31
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, asdict
from collections import defaultdict
import networkx as nx
from dotenv import load_dotenv


@dataclass
class Community:
    """社區數據類"""
    id: int
    level: int
    title: str
    summary: str
    entities: List[str]
    relationships: List[Dict[str, str]]
    size: int
    attributes: Dict[str, Any] = None

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return asdict(self)


class CommunityDetector:
    """社區檢測器：使用圖算法進行社區發現"""

    def __init__(self, graph: nx.Graph):
        """
        初始化社區檢測器

        Args:
            graph: NetworkX 圖對象
        """
        self.graph = graph
        self.communities = []

    def detect_communities_louvain(self, resolution: float = 1.0) -> Dict[str, int]:
        """
        使用 Louvain 算法進行社區檢測

        Args:
            resolution: 分辨率參數（控制社區大小）

        Returns:
            節點到社區 ID 的映射
        """
        try:
            import community as community_louvain

            print(f"   使用 Louvain 算法進行社區檢測...")
            print(f"   分辨率: {resolution}")

            # 轉換為無向圖
            undirected_graph = self.graph.to_undirected()

            # 執行 Louvain 算法
            partition = community_louvain.best_partition(
                undirected_graph,
                resolution=resolution
            )

            num_communities = len(set(partition.values()))
            print(f"   ✓ 發現 {num_communities} 個社區")

            return partition

        except ImportError:
            print("   ⚠️  未安裝 python-louvain，使用替代方法")
            return self._detect_communities_greedy()

    def _detect_communities_greedy(self) -> Dict[str, int]:
        """
        使用貪心算法進行社區檢測（備選方法）

        Returns:
            節點到社區 ID 的映射
        """
        print(f"   使用貪心模塊化算法進行社區檢測...")

        undirected_graph = self.graph.to_undirected()

        # 使用 NetworkX 內置的貪心模塊化社區檢測
        from networkx.algorithms import community

        communities_generator = community.greedy_modularity_communities(
            undirected_graph,
            weight='weight'
        )

        # 轉換為字典格式
        partition = {}
        for comm_id, comm_nodes in enumerate(communities_generator):
            for node in comm_nodes:
                partition[node] = comm_id

        num_communities = len(set(partition.values()))
        print(f"   ✓ 發現 {num_communities} 個社區")

        return partition

    def detect_hierarchical_communities(
            self,
            max_levels: int = 3
    ) -> List[Dict[str, int]]:
        """
        檢測層次化社區結構

        Args:
            max_levels: 最大層級數

        Returns:
            每層的社區劃分列表
        """
        print(f"\n   檢測層次化社區（最大 {max_levels} 層）...")

        hierarchical_partitions = []

        # 第一層：細粒度社區
        resolution_values = [2.0, 1.0, 0.5][:max_levels]

        for level, resolution in enumerate(resolution_values):
            print(f"\n   層級 {level}: 分辨率 = {resolution}")
            partition = self.detect_communities_louvain(resolution)
            hierarchical_partitions.append(partition)

        return hierarchical_partitions

    def create_community_objects(
            self,
            partition: Dict[str, int],
            level: int = 0
    ) -> List[Community]:
        """
        創建社區對象

        Args:
            partition: 社區劃分
            level: 層級

        Returns:
            社區對象列表
        """
        # 按社區 ID 分組節點
        community_nodes = defaultdict(list)
        for node, comm_id in partition.items():
            community_nodes[comm_id].append(node)

        communities = []

        for comm_id, nodes in community_nodes.items():
            # 獲取社區內的關係
            community_edges = []
            for u, v in self.graph.edges():
                if u in nodes and v in nodes:
                    edge_data = self.graph.get_edge_data(u, v)
                    if edge_data:
                        # 對於 MultiDiGraph，取第一條邊
                        if isinstance(edge_data, dict) and 0 in edge_data:
                            edge_info = edge_data[0]
                        else:
                            edge_info = edge_data

                        community_edges.append({
                            "source": u,
                            "target": v,
                            "type": edge_info.get("type", "RELATED_TO")
                        })

            # 創建社區對象（暫無標題和摘要）
            community = Community(
                id=comm_id,
                level=level,
                title=f"Community {comm_id}",
                summary="",
                entities=nodes,
                relationships=community_edges,
                size=len(nodes)
            )

            communities.append(community)

        return communities


class CommunitySummarizer:
    """社區摘要生成器：使用 LLM 生成社區摘要"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"):
        """
        初始化摘要生成器

        Args:
            api_key: OpenAI API 密鑰
            model: 使用的模型名稱
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

    def create_summary_prompt(self, community: Community) -> str:
        """
        創建摘要生成提示詞

        Args:
            community: 社區對象

        Returns:
            提示詞字符串
        """
        entities_str = ", ".join(community.entities)

        relationships_str = "\n".join([
            f"- {rel['source']} --[{rel['type']}]--> {rel['target']}"
            for rel in community.relationships[:20]  # 限制數量
        ])

        prompt = f"""請為以下社區生成一個簡潔的標題和摘要。

社區包含的實體：
{entities_str}

社區內的關係：
{relationships_str}

請分析這個社區的主題和內容，並提供：
1. title: 簡短的主題標題（5-10 個字）
2. summary: 詳細摘要（2-3 句話，說明這個社區的主要內容和關鍵點）

請以 JSON 格式返回：
{{
    "title": "社區標題",
    "summary": "社區摘要"
}}

只返回 JSON，不要包含其他說明文字。"""

        return prompt

    def generate_summary(self, community: Community) -> Community:
        """
        為社區生成摘要

        Args:
            community: 社區對象

        Returns:
            包含摘要的社區對象
        """
        try:
            print(f"   為社區 {community.id} 生成摘要...")

            # 實際應用中的 API 調用
            # response = openai.ChatCompletion.create(
            #     model=self.model,
            #     messages=[
            #         {"role": "system", "content": "你是一個專業的內容摘要助手。"},
            #         {"role": "user", "content": self.create_summary_prompt(community)}
            #     ],
            #     temperature=0.3
            # )
            # result = json.loads(response.choices[0].message.content)

            # 使用模擬摘要
            result = self._mock_summary(community)

            community.title = result["title"]
            community.summary = result["summary"]

            print(f"   ✓ 標題: {community.title}")

            return community

        except Exception as e:
            print(f"   ✗ 生成摘要失敗: {e}")
            return community

    def _mock_summary(self, community: Community) -> Dict[str, str]:
        """
        生成模擬摘要

        Args:
            community: 社區對象

        Returns:
            包含標題和摘要的字典
        """
        # 簡單的啟發式摘要生成
        entity_types = defaultdict(list)

        # 從圖中獲取實體類型
        for entity in community.entities:
            # 這裡需要實際的圖數據，簡化處理
            entity_types["entities"].append(entity)

        # 生成標題（基於第一個實體）
        if community.entities:
            first_entity = community.entities[0]
            title = f"{first_entity} 相關主題"
        else:
            title = f"社區 {community.id}"

        # 生成摘要
        summary = (
            f"這個社區包含 {community.size} 個實體，"
            f"涉及 {len(community.relationships)} 個關係。"
            f"主要實體包括：{', '.join(community.entities[:5])}等。"
        )

        return {
            "title": title,
            "summary": summary
        }

    def generate_summaries_batch(
            self,
            communities: List[Community]
    ) -> List[Community]:
        """
        批量生成社區摘要

        Args:
            communities: 社區列表

        Returns:
            包含摘要的社區列表
        """
        print(f"\n   為 {len(communities)} 個社區生成摘要...")

        summarized_communities = []
        for community in communities:
            summarized = self.generate_summary(community)
            summarized_communities.append(summarized)

        print(f"   ✓ 完成摘要生成")

        return summarized_communities


class CommunityAnalyzer:
    """社區分析器：評估社區質量"""

    def __init__(self, graph: nx.Graph, communities: List[Community]):
        """
        初始化分析器

        Args:
            graph: 圖對象
            communities: 社區列表
        """
        self.graph = graph
        self.communities = communities

    def calculate_modularity(self, partition: Dict[str, int]) -> float:
        """
        計算模塊度（衡量社區劃分質量）

        Args:
            partition: 社區劃分

        Returns:
            模塊度值（-0.5 到 1.0，越高越好）
        """
        try:
            undirected_graph = self.graph.to_undirected()

            # 轉換 partition 格式
            communities_list = defaultdict(set)
            for node, comm_id in partition.items():
                communities_list[comm_id].add(node)

            communities_sets = list(communities_list.values())

            modularity = nx.algorithms.community.modularity(
                undirected_graph,
                communities_sets,
                weight='weight'
            )

            return modularity

        except Exception as e:
            print(f"   計算模塊度失敗: {e}")
            return 0.0

    def get_community_statistics(self) -> Dict[str, Any]:
        """
        獲取社區統計信息

        Returns:
            統計信息字典
        """
        sizes = [comm.size for comm in self.communities]

        stats = {
            "num_communities": len(self.communities),
            "avg_size": sum(sizes) / len(sizes) if sizes else 0,
            "min_size": min(sizes) if sizes else 0,
            "max_size": max(sizes) if sizes else 0,
            "total_entities": sum(sizes),
            "size_distribution": self._get_size_distribution()
        }

        return stats

    def _get_size_distribution(self) -> Dict[str, int]:
        """獲取社區大小分布"""
        distribution = {
            "small (1-5)": 0,
            "medium (6-20)": 0,
            "large (21-50)": 0,
            "very_large (51+)": 0
        }

        for comm in self.communities:
            if comm.size <= 5:
                distribution["small (1-5)"] += 1
            elif comm.size <= 20:
                distribution["medium (6-20)"] += 1
            elif comm.size <= 50:
                distribution["large (21-50)"] += 1
            else:
                distribution["very_large (51+)"] += 1

        return distribution


def display_communities(communities: List[Community], title: str = "社區列表", limit: int = 5):
    """
    顯示社區信息

    Args:
        communities: 社區列表
        title: 標題
        limit: 顯示數量限制
    """
    print(f"\n{title}")
    print("-" * 70)

    # 按大小排序
    sorted_communities = sorted(communities, key=lambda c: c.size, reverse=True)

    print(f"\n社區總數: {len(communities)}")
    print(f"\n社區詳情（前 {limit} 個，按大小排序）:")

    for i, comm in enumerate(sorted_communities[:limit], 1):
        print(f"\n{i}. 社區 {comm.id} - {comm.title}")
        print(f"   大小: {comm.size} 個實體")
        print(f"   層級: {comm.level}")
        print(f"   摘要: {comm.summary}")
        print(f"   關鍵實體: {', '.join(comm.entities[:5])}")
        if len(comm.entities) > 5:
            print(f"   ... 還有 {len(comm.entities) - 5} 個實體")
        print(f"   關係數: {len(comm.relationships)}")


def save_communities(communities: List[Community], output_path: str):
    """
    保存社區到文件

    Args:
        communities: 社區列表
        output_path: 輸出文件路徑
    """
    try:
        from pathlib import Path
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # 轉換為字典列表
        comm_data = [comm.to_dict() for comm in communities]

        # 保存為 JSON
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(comm_data, f, ensure_ascii=False, indent=2)

        print(f"✅ 社區已保存到: {output_path}")

    except Exception as e:
        print(f"❌ 保存社區失敗: {e}")


def create_sample_graph() -> nx.MultiDiGraph:
    """創建示例圖"""
    G = nx.MultiDiGraph()

    # 添加節點和邊（模擬知識圖譜）
    # AI 社區
    ai_entities = [
        "人工智能", "機器學習", "深度學習", "神經網絡",
        "John McCarthy", "Geoffrey Hinton", "Yoshua Bengio"
    ]

    for entity in ai_entities:
        G.add_node(entity, type="AI")

    for i in range(len(ai_entities) - 1):
        G.add_edge(ai_entities[i], ai_entities[i + 1], type="RELATED_TO", weight=0.8)

    # 產品社區
    product_entities = [
        "ChatGPT", "GPT-4", "OpenAI", "Bard", "Google", "Claude", "Anthropic"
    ]

    for entity in product_entities:
        G.add_node(entity, type="PRODUCT")

    G.add_edge("OpenAI", "ChatGPT", type="DEVELOPED", weight=1.0)
    G.add_edge("OpenAI", "GPT-4", type="DEVELOPED", weight=1.0)
    G.add_edge("ChatGPT", "GPT-4", type="USES", weight=0.9)
    G.add_edge("Google", "Bard", type="DEVELOPED", weight=1.0)
    G.add_edge("Anthropic", "Claude", type="DEVELOPED", weight=1.0)

    # 技術社區
    tech_entities = [
        "GraphRAG", "Knowledge Graph", "RAG", "Vector Database", "Embedding"
    ]

    for entity in tech_entities:
        G.add_node(entity, type="TECHNOLOGY")

    G.add_edge("GraphRAG", "Knowledge Graph", type="USES", weight=0.9)
    G.add_edge("GraphRAG", "RAG", type="BASED_ON", weight=0.95)
    G.add_edge("RAG", "Vector Database", type="USES", weight=0.85)
    G.add_edge("RAG", "Embedding", type="USES", weight=0.85)

    # 跨社區連接
    G.add_edge("深度學習", "GPT-4", type="ENABLES", weight=0.7)
    G.add_edge("神經網絡", "Embedding", type="ENABLES", weight=0.7)

    return G


def main():
    """
    主函數：演示社區檢測流程
    """
    print("=" * 70)
    print("🔍 GraphRAG 社區檢測示例".center(70))
    print("=" * 70)
    print()

    # 加載環境變量
    load_dotenv()

    # 步驟 1: 創建示例圖
    print("步驟 1: 創建知識圖譜")
    print("=" * 70)

    graph = create_sample_graph()
    print(f"✓ 圖譜包含 {graph.number_of_nodes()} 個節點，{graph.number_of_edges()} 條邊")
    print()

    # 步驟 2: 社區檢測
    print("\n步驟 2: 執行社區檢測")
    print("=" * 70)

    detector = CommunityDetector(graph)
    partition = detector.detect_communities_louvain(resolution=1.0)

    print()

    # 步驟 3: 創建社區對象
    print("\n步驟 3: 創建社區對象")
    print("=" * 70)

    communities = detector.create_community_objects(partition, level=0)
    print(f"✓ 創建了 {len(communities)} 個社區對象")
    print()

    # 步驟 4: 生成摘要
    print("\n步驟 4: 生成社區摘要")
    print("=" * 70)

    summarizer = CommunitySummarizer()
    communities = summarizer.generate_summaries_batch(communities)
    print()

    # 步驟 5: 分析社區質量
    print("\n步驟 5: 分析社區質量")
    print("=" * 70)

    analyzer = CommunityAnalyzer(graph, communities)
    modularity = analyzer.calculate_modularity(partition)
    stats = analyzer.get_community_statistics()

    print(f"\n質量指標:")
    print(f"  模塊度: {modularity:.4f} {'(優秀)' if modularity > 0.3 else '(一般)'}")
    print(f"\n社區統計:")
    print(f"  社區數量: {stats['num_communities']}")
    print(f"  平均大小: {stats['avg_size']:.1f}")
    print(f"  大小範圍: {stats['min_size']} - {stats['max_size']}")
    print(f"\n大小分布:")
    for size_range, count in stats['size_distribution'].items():
        print(f"  {size_range}: {count}")
    print()

    # 步驟 6: 顯示社區
    display_communities(communities, "檢測到的社區")
    print()

    # 步驟 7: 保存社區
    print("\n步驟 6: 保存社區")
    print("=" * 70)
    save_communities(communities, "./output/communities.json")
    print()

    # 總結
    print("\n" + "=" * 70)
    print("💡 社區檢測要點")
    print("=" * 70)
    print("""
    1. 算法選擇：
       • Louvain: 快速，適合大規模圖
       • Leiden: 更準確，GraphRAG 默認使用
       • Label Propagation: 簡單快速
       • Girvan-Newman: 層次化檢測

    2. 參數調優：
       • resolution: 控制社區大小（越大社區越小）
       • weight: 考慮邊權重
       • 迭代次數: 影響收斂質量

    3. 層次化社區：
       • 多層次視圖（細粒度到粗粒度）
       • 支持不同層級的查詢
       • 層級間的一致性

    4. 摘要生成：
       • 使用 LLM 理解社區主題
       • 提取關鍵實體和關係
       • 生成人類可讀的描述

    5. 質量評估：
       • 模塊度（Modularity）
       • 覆蓋率（Coverage）
       • 導體性（Conductance）

    6. 應用場景：
       • Global Search: 基於社區摘要
       • 主題發現: 識別文檔主題
       • 知識組織: 結構化知識

    📚 下一步：查看 06_本地搜索.py 了解 Local Search 的實現
    """)

    print("✅ 社區檢測示例完成！")


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
