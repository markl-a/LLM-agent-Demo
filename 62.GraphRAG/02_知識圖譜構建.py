"""
GraphRAG 知識圖譜構建示例

這個示例展示了如何構建知識圖譜：
1. 文檔加載和分塊
2. 實體和關係提取
3. 圖譜構建和存儲
4. 圖譜統計分析

Author: GraphRAG Team
Date: 2025-12-31
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import json
from dotenv import load_dotenv
import networkx as nx
import pandas as pd


class DocumentProcessor:
    """文檔處理器：負責加載和分塊文檔"""

    def __init__(self, chunk_size: int = 1200, chunk_overlap: int = 100):
        """
        初始化文檔處理器

        Args:
            chunk_size: 文本塊大小（字符數）
            chunk_overlap: 文本塊重疊大小
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_documents(self, input_dir: str) -> List[Dict[str, str]]:
        """
        從目錄加載所有文檔

        Args:
            input_dir: 輸入目錄路徑

        Returns:
            文檔列表，每個文檔包含 id 和 text
        """
        documents = []
        input_path = Path(input_dir)

        if not input_path.exists():
            print(f"⚠️  輸入目錄不存在: {input_dir}")
            return documents

        # 支持的文件格式
        supported_extensions = [".txt", ".md", ".csv"]

        for file_path in input_path.iterdir():
            if file_path.suffix.lower() in supported_extensions:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        documents.append({
                            "id": file_path.stem,
                            "text": content,
                            "source": str(file_path)
                        })
                except Exception as e:
                    print(f"⚠️  讀取文件失敗 {file_path}: {e}")

        print(f"✅ 加載了 {len(documents)} 個文檔")
        return documents

    def chunk_text(self, text: str, doc_id: str) -> List[Dict[str, Any]]:
        """
        將文本分塊

        Args:
            text: 要分塊的文本
            doc_id: 文檔 ID

        Returns:
            文本塊列表
        """
        chunks = []
        text_length = len(text)

        # 如果文本小於塊大小，直接返回
        if text_length <= self.chunk_size:
            return [{
                "chunk_id": f"{doc_id}_0",
                "text": text,
                "start": 0,
                "end": text_length
            }]

        # 分塊處理
        start = 0
        chunk_index = 0

        while start < text_length:
            end = min(start + self.chunk_size, text_length)

            # 嘗試在句子邊界分割
            if end < text_length:
                # 查找最近的句號、問號或換行符
                for delimiter in ["。", ".", "!", "?", "\n\n"]:
                    last_delimiter = text.rfind(delimiter, start, end)
                    if last_delimiter != -1:
                        end = last_delimiter + 1
                        break

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    "chunk_id": f"{doc_id}_{chunk_index}",
                    "text": chunk_text,
                    "start": start,
                    "end": end
                })
                chunk_index += 1

            # 移動到下一個塊（考慮重疊）
            start = end - self.chunk_overlap if end < text_length else end

        return chunks

    def process_documents(self, documents: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        處理所有文檔並返回文本塊

        Args:
            documents: 文檔列表

        Returns:
            所有文本塊的列表
        """
        all_chunks = []

        for doc in documents:
            chunks = self.chunk_text(doc["text"], doc["id"])
            for chunk in chunks:
                chunk["doc_id"] = doc["id"]
                chunk["source"] = doc.get("source", "")
            all_chunks.extend(chunks)

        print(f"✅ 生成了 {len(all_chunks)} 個文本塊")
        return all_chunks


class KnowledgeGraphBuilder:
    """知識圖譜構建器"""

    def __init__(self):
        """初始化知識圖譜構建器"""
        self.graph = nx.MultiDiGraph()
        self.entities = {}
        self.relationships = []

    def extract_entities_mock(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        模擬實體提取（實際應用中使用 LLM）

        在實際應用中，這裡會調用 LLM API 來提取實體

        Args:
            chunks: 文本塊列表

        Returns:
            提取的實體列表
        """
        print("📊 提取實體（使用模擬數據）...")
        print("   實際使用中會調用 LLM API 進行實體識別")

        # 模擬提取的實體
        mock_entities = [
            {
                "name": "John McCarthy",
                "type": "PERSON",
                "description": "AI 領域先驅，提出人工智能概念",
                "source_chunks": ["doc1_0"]
            },
            {
                "name": "Geoffrey Hinton",
                "type": "PERSON",
                "description": "深度學習三巨頭之一",
                "source_chunks": ["doc1_0"]
            },
            {
                "name": "Yoshua Bengio",
                "type": "PERSON",
                "description": "深度學習三巨頭之一",
                "source_chunks": ["doc1_0"]
            },
            {
                "name": "Yann LeCun",
                "type": "PERSON",
                "description": "深度學習三巨頭之一",
                "source_chunks": ["doc1_0"]
            },
            {
                "name": "OpenAI",
                "type": "ORGANIZATION",
                "description": "AI 研究公司，開發了 ChatGPT",
                "source_chunks": ["doc1_0"]
            },
            {
                "name": "ChatGPT",
                "type": "PRODUCT",
                "description": "大型語言模型產品",
                "source_chunks": ["doc1_0"]
            },
            {
                "name": "Google",
                "type": "ORGANIZATION",
                "description": "科技公司，提出知識圖譜概念",
                "source_chunks": ["doc2_0"]
            },
            {
                "name": "Knowledge Graph",
                "type": "CONCEPT",
                "description": "結構化知識表示方法",
                "source_chunks": ["doc2_0"]
            },
            {
                "name": "GraphRAG",
                "type": "TECHNOLOGY",
                "description": "Microsoft 的知識圖譜增強 RAG 框架",
                "source_chunks": ["doc3_0"]
            },
            {
                "name": "Microsoft Research",
                "type": "ORGANIZATION",
                "description": "微軟研究院",
                "source_chunks": ["doc3_0"]
            }
        ]

        print(f"✅ 提取了 {len(mock_entities)} 個實體")
        return mock_entities

    def extract_relationships_mock(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        模擬關係提取（實際應用中使用 LLM）

        Args:
            entities: 實體列表

        Returns:
            關係列表
        """
        print("📊 提取關係（使用模擬數據）...")
        print("   實際使用中會調用 LLM API 進行關係識別")

        # 模擬提取的關係
        mock_relationships = [
            {
                "source": "John McCarthy",
                "target": "人工智能",
                "type": "PROPOSED",
                "description": "提出人工智能概念",
                "weight": 1.0
            },
            {
                "source": "Geoffrey Hinton",
                "target": "深度學習",
                "type": "CONTRIBUTED_TO",
                "description": "對深度學習做出重要貢獻",
                "weight": 0.95
            },
            {
                "source": "Yoshua Bengio",
                "target": "深度學習",
                "type": "CONTRIBUTED_TO",
                "description": "對深度學習做出重要貢獻",
                "weight": 0.95
            },
            {
                "source": "Yann LeCun",
                "target": "深度學習",
                "type": "CONTRIBUTED_TO",
                "description": "對深度學習做出重要貢獻",
                "weight": 0.95
            },
            {
                "source": "OpenAI",
                "target": "ChatGPT",
                "type": "DEVELOPED",
                "description": "開發了 ChatGPT",
                "weight": 1.0
            },
            {
                "source": "Google",
                "target": "Knowledge Graph",
                "type": "PROPOSED",
                "description": "提出知識圖譜概念",
                "weight": 1.0
            },
            {
                "source": "Microsoft Research",
                "target": "GraphRAG",
                "type": "DEVELOPED",
                "description": "開發了 GraphRAG",
                "weight": 1.0
            },
            {
                "source": "GraphRAG",
                "target": "Knowledge Graph",
                "type": "USES",
                "description": "使用知識圖譜技術",
                "weight": 0.9
            }
        ]

        print(f"✅ 提取了 {len(mock_relationships)} 個關係")
        return mock_relationships

    def build_graph(self, entities: List[Dict[str, Any]], relationships: List[Dict[str, Any]]):
        """
        構建知識圖譜

        Args:
            entities: 實體列表
            relationships: 關係列表
        """
        print("🔨 構建知識圖譜...")

        # 添加實體節點
        for entity in entities:
            self.graph.add_node(
                entity["name"],
                type=entity["type"],
                description=entity.get("description", ""),
                source_chunks=entity.get("source_chunks", [])
            )
            self.entities[entity["name"]] = entity

        # 添加關係邊
        for rel in relationships:
            self.graph.add_edge(
                rel["source"],
                rel["target"],
                type=rel["type"],
                description=rel.get("description", ""),
                weight=rel.get("weight", 1.0)
            )
            self.relationships.append(rel)

        print(f"✅ 圖譜構建完成")
        print(f"   節點數: {self.graph.number_of_nodes()}")
        print(f"   邊數: {self.graph.number_of_edges()}")

    def get_graph_statistics(self) -> Dict[str, Any]:
        """
        獲取圖譜統計信息

        Returns:
            統計信息字典
        """
        stats = {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "density": nx.density(self.graph),
            "is_connected": nx.is_weakly_connected(self.graph)
        }

        # 實體類型分布
        entity_types = {}
        for node in self.graph.nodes():
            node_type = self.graph.nodes[node].get("type", "UNKNOWN")
            entity_types[node_type] = entity_types.get(node_type, 0) + 1

        stats["entity_types"] = entity_types

        # 度數統計
        degrees = [degree for node, degree in self.graph.degree()]
        if degrees:
            stats["avg_degree"] = sum(degrees) / len(degrees)
            stats["max_degree"] = max(degrees)

        return stats

    def save_graph(self, output_path: str):
        """
        保存圖譜到文件

        Args:
            output_path: 輸出文件路徑
        """
        try:
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)

            # 保存為 GraphML 格式（可被多種工具讀取）
            graphml_path = str(Path(output_path).with_suffix(".graphml"))
            nx.write_graphml(self.graph, graphml_path)
            print(f"✅ 圖譜已保存到: {graphml_path}")

            # 同時保存為 JSON 格式（更易讀）
            json_path = str(Path(output_path).with_suffix(".json"))
            graph_data = {
                "nodes": [
                    {
                        "id": node,
                        **self.graph.nodes[node]
                    }
                    for node in self.graph.nodes()
                ],
                "edges": [
                    {
                        "source": u,
                        "target": v,
                        **self.graph[u][v][0]
                    }
                    for u, v in self.graph.edges()
                ]
            }

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(graph_data, f, ensure_ascii=False, indent=2)
            print(f"✅ 圖譜已保存到: {json_path}")

        except Exception as e:
            print(f"❌ 保存圖譜失敗: {e}")


def display_graph_info(graph_builder: KnowledgeGraphBuilder):
    """
    顯示圖譜信息

    Args:
        graph_builder: 知識圖譜構建器
    """
    print("\n" + "=" * 70)
    print("📊 知識圖譜統計信息")
    print("=" * 70)

    stats = graph_builder.get_graph_statistics()

    print(f"\n基本信息:")
    print(f"  節點數量: {stats['nodes']}")
    print(f"  邊數量: {stats['edges']}")
    print(f"  圖密度: {stats['density']:.4f}")
    print(f"  是否連通: {'是' if stats['is_connected'] else '否'}")

    print(f"\n實體類型分布:")
    for entity_type, count in stats['entity_types'].items():
        print(f"  {entity_type}: {count}")

    if 'avg_degree' in stats:
        print(f"\n度數統計:")
        print(f"  平均度數: {stats['avg_degree']:.2f}")
        print(f"  最大度數: {stats['max_degree']}")

    # 顯示一些重要節點
    print(f"\n重要節點（按度數排序）:")
    degrees = dict(graph_builder.graph.degree())
    sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:5]

    for node, degree in sorted_nodes:
        node_type = graph_builder.graph.nodes[node].get("type", "UNKNOWN")
        print(f"  {node} ({node_type}): {degree} 個連接")


def main():
    """
    主函數：演示知識圖譜構建流程
    """
    print("=" * 70)
    print("🔨 GraphRAG 知識圖譜構建示例".center(70))
    print("=" * 70)
    print()

    # 加載環境變量
    load_dotenv()

    # 步驟 1: 文檔處理
    print("步驟 1: 文檔加載和分塊")
    print("-" * 70)

    processor = DocumentProcessor(chunk_size=1200, chunk_overlap=100)

    # 假設文檔在 ./data/input 目錄
    input_dir = "./data/input"
    documents = processor.load_documents(input_dir)

    if not documents:
        print("⚠️  未找到文檔，使用示例數據")
        # 創建示例文檔
        from pathlib import Path
        Path(input_dir).mkdir(parents=True, exist_ok=True)

        sample_doc = """
        人工智能的發展歷程
        人工智能（AI）由 John McCarthy 在 1956 年提出。
        Geoffrey Hinton、Yoshua Bengio 和 Yann LeCun 是深度學習三巨頭。
        OpenAI 開發了 ChatGPT，Google 提出了知識圖譜概念。
        Microsoft Research 開發了 GraphRAG 框架。
        """

        with open(f"{input_dir}/sample.txt", "w", encoding="utf-8") as f:
            f.write(sample_doc.strip())

        documents = processor.load_documents(input_dir)

    chunks = processor.process_documents(documents)
    print()

    # 步驟 2: 實體提取
    print("步驟 2: 實體提取")
    print("-" * 70)

    builder = KnowledgeGraphBuilder()
    entities = builder.extract_entities_mock(chunks)

    print("\n提取的實體示例:")
    for entity in entities[:3]:
        print(f"  • {entity['name']} ({entity['type']})")
        print(f"    {entity['description']}")
    print()

    # 步驟 3: 關係提取
    print("步驟 3: 關係提取")
    print("-" * 70)

    relationships = builder.extract_relationships_mock(entities)

    print("\n提取的關係示例:")
    for rel in relationships[:3]:
        print(f"  • {rel['source']} --[{rel['type']}]--> {rel['target']}")
        print(f"    {rel['description']}")
    print()

    # 步驟 4: 構建圖譜
    print("步驟 4: 構建知識圖譜")
    print("-" * 70)

    builder.build_graph(entities, relationships)
    print()

    # 步驟 5: 圖譜分析
    display_graph_info(builder)
    print()

    # 步驟 6: 保存圖譜
    print("\n步驟 5: 保存知識圖譜")
    print("-" * 70)

    output_path = "./output/knowledge_graph.graphml"
    builder.save_graph(output_path)
    print()

    # 總結
    print("\n" + "=" * 70)
    print("💡 關鍵要點")
    print("=" * 70)
    print("""
    1. 實體提取：
       • 使用 LLM 識別文本中的關鍵實體
       • 支持多種實體類型（人物、組織、概念等）
       • 提取實體描述和屬性

    2. 關係提取：
       • 識別實體之間的語義關係
       • 支持多種關係類型
       • 計算關係權重

    3. 圖譜構建：
       • 使用 NetworkX 構建有向多重圖
       • 支持節點和邊的屬性
       • 可導出多種格式

    4. 實際應用建議：
       • 使用 GraphRAG 的內置 LLM 提取功能
       • 配置 settings.yaml 定義實體類型
       • 使用並行處理加速大規模數據
       • 定期驗證提取質量

    📚 下一步：查看 03_實體抽取.py 了解實體提取的詳細配置
    """)

    print("✅ 知識圖譜構建示例完成！")


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
