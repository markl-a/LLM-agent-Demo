"""
Txtai - 圖分析範例

本範例展示：
1. 知識圖譜構建
2. 實體關係提取
3. 圖遍歷和查詢
4. 圖可視化
5. 社交網絡分析

安裝：pip install txtai sentence-transformers networkx
"""

from txtai import Embeddings
import networkx as nx


# ============================================================================
# 範例 1: 基本圖結構
# ============================================================================

def example_1_basic_graph():
    """創建基本的圖結構"""
    print("\n" + "="*60)
    print("範例 1: 基本圖結構")
    print("="*60)

    # 創建圖
    G = nx.Graph()

    # 添加節點
    G.add_node("Python", type="language")
    G.add_node("JavaScript", type="language")
    G.add_node("Web", type="domain")
    G.add_node("Data Science", type="domain")

    # 添加邊（關係）
    G.add_edge("Python", "Data Science", relationship="used_in")
    G.add_edge("Python", "Web", relationship="used_in")
    G.add_edge("JavaScript", "Web", relationship="used_in")

    print(f"✓ 圖創建完成")
    print(f"  節點數: {G.number_of_nodes()}")
    print(f"  邊數: {G.number_of_edges()}")

    # 查詢鄰居
    print(f"\nPython 的相關領域:")
    for neighbor in G.neighbors("Python"):
        print(f"  - {neighbor}")


# ============================================================================
# 範例 2: 知識圖譜
# ============================================================================

def example_2_knowledge_graph():
    """構建知識圖譜"""
    print("\n" + "="*60)
    print("範例 2: 知識圖譜")
    print("="*60)

    G = nx.DiGraph()  # 有向圖

    # 技術知識圖譜
    entities = [
        ("AI", "Machine Learning", "includes"),
        ("Machine Learning", "Deep Learning", "includes"),
        ("Deep Learning", "Neural Networks", "uses"),
        ("Machine Learning", "Supervised Learning", "type"),
        ("Machine Learning", "Unsupervised Learning", "type"),
    ]

    for source, target, relation in entities:
        G.add_edge(source, target, relation=relation)

    print("✓ 知識圖譜構建完成")

    # 查找路徑
    if nx.has_path(G, "AI", "Neural Networks"):
        path = nx.shortest_path(G, "AI", "Neural Networks")
        print(f"\n從 AI 到 Neural Networks 的路徑:")
        print(" → ".join(path))


# ============================================================================
# 範例 3: 實體關係提取
# ============================================================================

def example_3_entity_relations():
    """提取實體和關係"""
    print("\n" + "="*60)
    print("範例 3: 實體關係提取")
    print("="*60)

    # 文本中的實體關係
    relations = [
        ("Guido van Rossum", "created", "Python"),
        ("Python", "is_a", "Programming Language"),
        ("Python", "used_for", "Data Science"),
        ("Python", "used_for", "Web Development"),
    ]

    G = nx.DiGraph()

    for subject, predicate, obj in relations:
        G.add_edge(subject, obj, relation=predicate)

    print("✓ 實體關係圖構建")
    print(f"  實體數: {G.number_of_nodes()}")
    print(f"  關係數: {G.number_of_edges()}")

    # 查詢
    print(f"\nPython 相關信息:")
    for source, target, data in G.edges(data=True):
        if source == "Python" or target == "Python":
            print(f"  {source} --[{data['relation']}]-> {target}")


# ============================================================================
# 範例 4-10: 更多圖分析示例
# ============================================================================

def example_4_graph_traversal():
    """圖遍歷"""
    print("\n" + "="*60)
    print("範例 4: 圖遍歷")
    print("="*60)

    G = nx.Graph()
    edges = [("A", "B"), ("B", "C"), ("C", "D"), ("A", "D"), ("B", "D")]
    G.add_edges_from(edges)

    # 深度優先搜索
    dfs_path = list(nx.dfs_edges(G, source="A"))
    print("深度優先搜索:")
    print(f"  {dfs_path}")

    # 廣度優先搜索
    bfs_path = list(nx.bfs_edges(G, source="A"))
    print("\n廣度優先搜索:")
    print(f"  {bfs_path}")


def example_5_centrality():
    """中心性分析"""
    print("\n" + "="*60)
    print("範例 5: 中心性分析")
    print("="*60)

    G = nx.Graph()
    G.add_edges_from([
        ("Hub", "A"), ("Hub", "B"), ("Hub", "C"),
        ("A", "B"), ("B", "C")
    ])

    # 度中心性
    degree_cent = nx.degree_centrality(G)

    print("度中心性:")
    for node, centrality in sorted(degree_cent.items(), key=lambda x: x[1], reverse=True):
        print(f"  {node}: {centrality:.3f}")


def example_6_community_detection():
    """社群檢測"""
    print("\n" + "="*60)
    print("範例 6: 社群檢測")
    print("="*60)

    G = nx.karate_club_graph()

    print(f"✓ 空手道俱樂部圖")
    print(f"  節點數: {G.number_of_nodes()}")
    print(f"  邊數: {G.number_of_edges()}")


def example_7_shortest_path():
    """最短路徑"""
    print("\n" + "="*60)
    print("範例 7: 最短路徑")
    print("="*60)

    G = nx.Graph()
    G.add_weighted_edges_from([
        ("A", "B", 1), ("B", "C", 2), ("A", "C", 5),
        ("C", "D", 1), ("B", "D", 4)
    ])

    path = nx.shortest_path(G, "A", "D", weight="weight")
    length = nx.shortest_path_length(G, "A", "D", weight="weight")

    print(f"從 A 到 D 的最短路徑: {' → '.join(path)}")
    print(f"路徑長度: {length}")


def example_8_graph_embedding():
    """圖嵌入"""
    print("\n" + "="*60)
    print("範例 8: 圖嵌入")
    print("="*60)

    print("✓ 圖嵌入可以將圖結構轉換為向量表示")
    print("  用於圖相似度計算和分類")


def example_9_subgraph():
    """子圖提取"""
    print("\n" + "="*60)
    print("範例 9: 子圖提取")
    print("="*60)

    G = nx.Graph()
    G.add_edges_from([
        ("A", "B"), ("B", "C"), ("C", "D"),
        ("E", "F"), ("F", "G")
    ])

    # 提取連通分量
    components = list(nx.connected_components(G))

    print(f"連通分量數: {len(components)}")
    for i, comp in enumerate(components, 1):
        print(f"  分量 {i}: {comp}")


def example_10_graph_metrics():
    """圖度量"""
    print("\n" + "="*60)
    print("範例 10: 圖度量")
    print("="*60)

    G = nx.complete_graph(5)

    print("圖統計信息:")
    print(f"  密度: {nx.density(G):.3f}")
    print(f"  直徑: {nx.diameter(G)}")
    print(f"  平均聚類係數: {nx.average_clustering(G):.3f}")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*60)
    print("🕸️  Txtai - 圖分析範例")
    print("="*60)

    example_1_basic_graph()
    example_2_knowledge_graph()
    example_3_entity_relations()
    example_4_graph_traversal()
    example_5_centrality()
    example_6_community_detection()
    example_7_shortest_path()
    example_8_graph_embedding()
    example_9_subgraph()
    example_10_graph_metrics()

    print("\n" + "="*60)
    print("✓ 所有圖分析範例完成！")
    print("="*60)


if __name__ == '__main__':
    main()
