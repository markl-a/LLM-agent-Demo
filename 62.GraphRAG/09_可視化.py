"""
GraphRAG 可視化示例

這個示例展示了如何可視化知識圖譜：
1. 網絡圖可視化
2. 社區結構可視化
3. 互動式圖表
4. 統計報表生成

Author: GraphRAG Team
Date: 2025-12-31
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import networkx as nx
from dotenv import load_dotenv


class GraphVisualizer:
    """圖譜可視化器"""

    def __init__(self, graph: nx.Graph):
        """
        初始化可視化器

        Args:
            graph: NetworkX 圖對象
        """
        self.graph = graph

    def visualize_with_matplotlib(
            self,
            output_path: str = "./output/graph_viz.png",
            figsize: tuple = (15, 10)
    ):
        """
        使用 Matplotlib 生成靜態圖

        Args:
            output_path: 輸出文件路徑
            figsize: 圖片大小
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches

            print(f"\n📊 使用 Matplotlib 生成圖譜可視化...")

            # 創建圖形
            fig, ax = plt.subplots(figsize=figsize)

            # 計算佈局
            pos = nx.spring_layout(self.graph, k=2, iterations=50, seed=42)

            # 獲取節點類型並分配顏色
            node_types = {}
            for node in self.graph.nodes():
                node_type = self.graph.nodes[node].get('type', 'UNKNOWN')
                if node_type not in node_types:
                    node_types[node_type] = []
                node_types[node_type].append(node)

            # 顏色映射
            color_map = {
                'PERSON': '#FF6B6B',
                'ORGANIZATION': '#4ECDC4',
                'TECHNOLOGY': '#45B7D1',
                'CONCEPT': '#FFA07A',
                'PRODUCT': '#98D8C8',
                'UNKNOWN': '#CCCCCC'
            }

            # 繪製不同類型的節點
            for node_type, nodes in node_types.items():
                color = color_map.get(node_type, '#CCCCCC')
                nx.draw_networkx_nodes(
                    self.graph,
                    pos,
                    nodelist=nodes,
                    node_color=color,
                    node_size=1000,
                    alpha=0.8,
                    ax=ax,
                    label=node_type
                )

            # 繪製邊
            nx.draw_networkx_edges(
                self.graph,
                pos,
                edge_color='gray',
                alpha=0.3,
                arrows=True,
                arrowsize=20,
                ax=ax
            )

            # 繪製標籤
            nx.draw_networkx_labels(
                self.graph,
                pos,
                font_size=8,
                font_family='sans-serif',
                ax=ax
            )

            # 添加圖例
            ax.legend(loc='upper left', fontsize=10)

            # 設置標題
            ax.set_title(
                f'知識圖譜可視化\n節點數: {self.graph.number_of_nodes()}, '
                f'邊數: {self.graph.number_of_edges()}',
                fontsize=14,
                fontweight='bold'
            )

            ax.axis('off')
            plt.tight_layout()

            # 保存圖片
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

            print(f"   ✓ 圖片已保存到: {output_path}")

        except ImportError:
            print(f"   ⚠️  未安裝 matplotlib，跳過靜態圖生成")
        except Exception as e:
            print(f"   ✗ 可視化失敗: {e}")

    def visualize_with_plotly(
            self,
            output_path: str = "./output/graph_interactive.html"
    ):
        """
        使用 Plotly 生成互動式圖

        Args:
            output_path: 輸出 HTML 文件路徑
        """
        try:
            import plotly.graph_objects as go

            print(f"\n📊 使用 Plotly 生成互動式可視化...")

            # 計算佈局
            pos = nx.spring_layout(self.graph, k=2, iterations=50, seed=42)

            # 創建邊的軌跡
            edge_trace = []
            for edge in self.graph.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]

                edge_trace.append(
                    go.Scatter(
                        x=[x0, x1, None],
                        y=[y0, y1, None],
                        mode='lines',
                        line=dict(width=1, color='#888'),
                        hoverinfo='none',
                        showlegend=False
                    )
                )

            # 創建節點的軌跡
            node_types = {}
            for node in self.graph.nodes():
                node_type = self.graph.nodes[node].get('type', 'UNKNOWN')
                if node_type not in node_types:
                    node_types[node_type] = {
                        'x': [],
                        'y': [],
                        'text': [],
                        'description': []
                    }

                x, y = pos[node]
                node_types[node_type]['x'].append(x)
                node_types[node_type]['y'].append(y)
                node_types[node_type]['text'].append(node)
                desc = self.graph.nodes[node].get('description', '')
                node_types[node_type]['description'].append(desc)

            # 顏色映射
            color_map = {
                'PERSON': '#FF6B6B',
                'ORGANIZATION': '#4ECDC4',
                'TECHNOLOGY': '#45B7D1',
                'CONCEPT': '#FFA07A',
                'PRODUCT': '#98D8C8',
                'UNKNOWN': '#CCCCCC'
            }

            node_traces = []
            for node_type, data in node_types.items():
                hover_text = [
                    f"{name}<br>{desc}" if desc else name
                    for name, desc in zip(data['text'], data['description'])
                ]

                node_trace = go.Scatter(
                    x=data['x'],
                    y=data['y'],
                    mode='markers+text',
                    text=data['text'],
                    textposition='top center',
                    hovertext=hover_text,
                    hoverinfo='text',
                    name=node_type,
                    marker=dict(
                        size=20,
                        color=color_map.get(node_type, '#CCCCCC'),
                        line=dict(width=2, color='white')
                    )
                )
                node_traces.append(node_trace)

            # 創建圖形
            fig = go.Figure(
                data=edge_trace + node_traces,
                layout=go.Layout(
                    title=dict(
                        text=f'知識圖譜互動可視化<br>節點: {self.graph.number_of_nodes()}, '
                             f'邊: {self.graph.number_of_edges()}',
                        x=0.5,
                        xanchor='center'
                    ),
                    showlegend=True,
                    hovermode='closest',
                    margin=dict(b=0, l=0, r=0, t=100),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    height=800
                )
            )

            # 保存 HTML
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            fig.write_html(output_path)

            print(f"   ✓ 互動式圖表已保存到: {output_path}")
            print(f"   💡 在瀏覽器中打開此文件以查看互動式圖表")

        except ImportError:
            print(f"   ⚠️  未安裝 plotly，跳過互動式圖生成")
        except Exception as e:
            print(f"   ✗ 可視化失敗: {e}")

    def visualize_communities(
            self,
            communities: List[Dict[str, Any]],
            output_path: str = "./output/communities_viz.png"
    ):
        """
        可視化社區結構

        Args:
            communities: 社區列表
            output_path: 輸出文件路徑
        """
        try:
            import matplotlib.pyplot as plt

            print(f"\n📊 生成社區結構可視化...")

            # 創建社區到節點的映射
            node_to_community = {}
            for comm in communities:
                comm_id = comm.get('id', 0)
                for entity in comm.get('entities', []):
                    node_to_community[entity] = comm_id

            # 生成社區顏色
            num_communities = len(communities)
            colors = plt.cm.Set3(range(num_communities))

            # 創建圖形
            fig, ax = plt.subplots(figsize=(15, 10))

            # 計算佈局
            pos = nx.spring_layout(self.graph, k=2, iterations=50, seed=42)

            # 按社區繪製節點
            for comm in communities:
                comm_id = comm.get('id', 0)
                nodes = [
                    n for n in comm.get('entities', [])
                    if n in self.graph.nodes()
                ]

                if nodes:
                    nx.draw_networkx_nodes(
                        self.graph,
                        pos,
                        nodelist=nodes,
                        node_color=[colors[comm_id % len(colors)]],
                        node_size=1000,
                        alpha=0.8,
                        ax=ax,
                        label=f"社區 {comm_id}: {comm.get('title', 'Unknown')}"
                    )

            # 繪製邊
            nx.draw_networkx_edges(
                self.graph,
                pos,
                edge_color='gray',
                alpha=0.2,
                arrows=True,
                ax=ax
            )

            # 繪製標籤
            nx.draw_networkx_labels(
                self.graph,
                pos,
                font_size=8,
                ax=ax
            )

            # 添加圖例
            ax.legend(loc='upper left', fontsize=9, ncol=2)
            ax.set_title(
                f'社區結構可視化\n共 {num_communities} 個社區',
                fontsize=14,
                fontweight='bold'
            )
            ax.axis('off')
            plt.tight_layout()

            # 保存
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

            print(f"   ✓ 社區結構圖已保存到: {output_path}")

        except ImportError:
            print(f"   ⚠️  未安裝 matplotlib，跳過社區可視化")
        except Exception as e:
            print(f"   ✗ 可視化失敗: {e}")


class StatisticsReporter:
    """統計報表生成器"""

    def __init__(self, graph: nx.Graph):
        """
        初始化報表生成器

        Args:
            graph: NetworkX 圖對象
        """
        self.graph = graph

    def generate_report(self, output_path: str = "./output/graph_report.txt"):
        """
        生成文本報表

        Args:
            output_path: 輸出文件路徑
        """
        print(f"\n📄 生成統計報表...")

        report_lines = []
        report_lines.append("=" * 70)
        report_lines.append("知識圖譜統計報表".center(70))
        report_lines.append("=" * 70)
        report_lines.append("")

        # 基本統計
        report_lines.append("基本統計")
        report_lines.append("-" * 70)
        report_lines.append(f"節點數量: {self.graph.number_of_nodes()}")
        report_lines.append(f"邊數量: {self.graph.number_of_edges()}")
        report_lines.append(f"圖密度: {nx.density(self.graph):.4f}")

        # 轉換為無向圖進行連通性分析
        undirected = self.graph.to_undirected()
        report_lines.append(f"連通分量數: {nx.number_connected_components(undirected)}")
        report_lines.append("")

        # 節點類型分布
        report_lines.append("節點類型分布")
        report_lines.append("-" * 70)
        type_count = {}
        for node in self.graph.nodes():
            node_type = self.graph.nodes[node].get('type', 'UNKNOWN')
            type_count[node_type] = type_count.get(node_type, 0) + 1

        for node_type, count in sorted(type_count.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / self.graph.number_of_nodes()) * 100
            report_lines.append(f"  {node_type}: {count} ({percentage:.1f}%)")
        report_lines.append("")

        # 度數統計
        report_lines.append("度數統計")
        report_lines.append("-" * 70)
        degrees = [d for n, d in self.graph.degree()]
        if degrees:
            report_lines.append(f"  平均度數: {sum(degrees) / len(degrees):.2f}")
            report_lines.append(f"  最大度數: {max(degrees)}")
            report_lines.append(f"  最小度數: {min(degrees)}")
        report_lines.append("")

        # Top 節點（按度數）
        report_lines.append("最重要的節點（按度數）")
        report_lines.append("-" * 70)
        degree_dict = dict(self.graph.degree())
        sorted_nodes = sorted(degree_dict.items(), key=lambda x: x[1], reverse=True)

        for i, (node, degree) in enumerate(sorted_nodes[:10], 1):
            node_type = self.graph.nodes[node].get('type', 'UNKNOWN')
            report_lines.append(f"  {i}. {node} ({node_type}): {degree} 個連接")
        report_lines.append("")

        # 關係類型分布
        report_lines.append("關係類型分布")
        report_lines.append("-" * 70)
        edge_types = {}
        for u, v, data in self.graph.edges(data=True):
            # 處理 MultiDiGraph
            if isinstance(data, dict):
                edge_type = data.get('type', 'UNKNOWN')
            else:
                edge_type = 'UNKNOWN'
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1

        for edge_type, count in sorted(edge_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / self.graph.number_of_edges()) * 100
            report_lines.append(f"  {edge_type}: {count} ({percentage:.1f}%)")
        report_lines.append("")

        # 保存報表
        report_text = "\n".join(report_lines)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_text)

        print(f"   ✓ 報表已保存到: {output_path}")

        # 同時打印到控制台
        print(f"\n{report_text}")


def create_sample_graph() -> nx.MultiDiGraph:
    """創建示例圖"""
    G = nx.MultiDiGraph()

    # 添加節點和邊
    entities = [
        ("Geoffrey Hinton", "PERSON"),
        ("Yoshua Bengio", "PERSON"),
        ("Yann LeCun", "PERSON"),
        ("深度學習", "CONCEPT"),
        ("神經網絡", "CONCEPT"),
        ("OpenAI", "ORGANIZATION"),
        ("ChatGPT", "PRODUCT"),
        ("GPT-4", "TECHNOLOGY"),
        ("Google", "ORGANIZATION"),
        ("Bard", "PRODUCT"),
        ("Knowledge Graph", "CONCEPT"),
        ("GraphRAG", "TECHNOLOGY"),
    ]

    for name, node_type in entities:
        G.add_node(name, type=node_type, description=f"{name} 相關描述")

    # 添加關係
    edges = [
        ("Geoffrey Hinton", "深度學習", "CONTRIBUTED_TO"),
        ("Yoshua Bengio", "深度學習", "CONTRIBUTED_TO"),
        ("Yann LeCun", "深度學習", "CONTRIBUTED_TO"),
        ("深度學習", "神經網絡", "BASED_ON"),
        ("OpenAI", "ChatGPT", "DEVELOPED"),
        ("ChatGPT", "GPT-4", "USES"),
        ("GPT-4", "深度學習", "BASED_ON"),
        ("Google", "Bard", "DEVELOPED"),
        ("Google", "Knowledge Graph", "PROPOSED"),
        ("GraphRAG", "Knowledge Graph", "USES"),
    ]

    for source, target, rel_type in edges:
        G.add_edge(source, target, type=rel_type)

    return G


def create_sample_communities() -> List[Dict[str, Any]]:
    """創建示例社區"""
    return [
        {
            "id": 0,
            "level": 0,
            "title": "深度學習先驅",
            "summary": "深度學習領域的重要人物",
            "entities": ["Geoffrey Hinton", "Yoshua Bengio", "Yann LeCun", "深度學習", "神經網絡"],
            "size": 5
        },
        {
            "id": 1,
            "level": 0,
            "title": "AI 產品",
            "summary": "主流 AI 產品和公司",
            "entities": ["OpenAI", "ChatGPT", "GPT-4", "Google", "Bard"],
            "size": 5
        },
        {
            "id": 2,
            "level": 0,
            "title": "知識圖譜",
            "summary": "知識圖譜相關技術",
            "entities": ["Knowledge Graph", "GraphRAG"],
            "size": 2
        }
    ]


def main():
    """
    主函數：演示圖譜可視化
    """
    print("=" * 70)
    print("📊 GraphRAG 可視化示例".center(70))
    print("=" * 70)
    print()

    # 加載環境變量
    load_dotenv()

    # 準備數據
    print("準備示例數據...")
    graph = create_sample_graph()
    communities = create_sample_communities()
    print(f"✓ 圖譜: {graph.number_of_nodes()} 個節點, {graph.number_of_edges()} 條邊")
    print(f"✓ 社區: {len(communities)} 個")
    print()

    # 創建可視化器
    visualizer = GraphVisualizer(graph)

    # 1. Matplotlib 靜態圖
    print("\n步驟 1: 生成靜態圖（Matplotlib）")
    print("=" * 70)
    visualizer.visualize_with_matplotlib("./output/graph_static.png")

    # 2. Plotly 互動式圖
    print("\n步驟 2: 生成互動式圖（Plotly）")
    print("=" * 70)
    visualizer.visualize_with_plotly("./output/graph_interactive.html")

    # 3. 社區可視化
    print("\n步驟 3: 生成社區結構圖")
    print("=" * 70)
    visualizer.visualize_communities(communities, "./output/communities.png")

    # 4. 統計報表
    print("\n步驟 4: 生成統計報表")
    print("=" * 70)
    reporter = StatisticsReporter(graph)
    reporter.generate_report("./output/graph_report.txt")

    # 總結
    print("\n\n" + "=" * 70)
    print("💡 可視化要點")
    print("=" * 70)
    print("""
    1. 可視化工具選擇：
       • Matplotlib: 靜態圖，出版質量
       • Plotly: 互動式圖，探索性分析
       • Pyvis: 網絡可視化專用
       • D3.js: Web 端高度自定義

    2. 佈局算法：
       • Spring Layout: 力導向，美觀自然
       • Circular Layout: 環形，適合小圖
       • Hierarchical Layout: 層次化，適合樹狀結構
       • Community Layout: 突出社區結構

    3. 大規模圖可視化：
       • 採樣和過濾（只顯示重要節點）
       • 層次化視圖（zoom in/out）
       • 聚合節點（fold/unfold）
       • 使用專業工具（Gephi, Cytoscape）

    4. 互動功能：
       • 懸停顯示詳情
       • 點擊展開鄰居
       • 搜索和高亮
       • 過濾和篩選

    5. 顏色編碼：
       • 按節點類型著色
       • 按社區著色
       • 按重要性（度數）著色
       • 按屬性值著色

    6. 實際應用：
       • 數據探索和理解
       • 結果展示和報告
       • 質量檢查和調試
       • 溝通和決策支持

    📚 下一步：查看 10_企業應用.py 了解企業級部署方案
    """)

    print("✅ 可視化示例完成！")
    print(f"\n生成的文件：")
    print(f"  • ./output/graph_static.png - 靜態圖")
    print(f"  • ./output/graph_interactive.html - 互動式圖")
    print(f"  • ./output/communities.png - 社區結構圖")
    print(f"  • ./output/graph_report.txt - 統計報表")


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
