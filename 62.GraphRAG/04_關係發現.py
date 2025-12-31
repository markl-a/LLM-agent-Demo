"""
GraphRAG 關係發現示例

這個示例展示了如何發現和提取實體之間的關係：
1. 關係類型定義
2. 使用 LLM 提取關係
3. 關係驗證和過濾
4. 關係權重計算

Author: GraphRAG Team
Date: 2025-12-31
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
from collections import defaultdict


@dataclass
class Relationship:
    """關係數據類"""
    source: str
    target: str
    type: str
    description: str
    weight: float = 1.0
    source_chunks: List[str] = None
    attributes: Dict[str, Any] = None
    confidence: float = 1.0

    def __post_init__(self):
        if self.source_chunks is None:
            self.source_chunks = []
        if self.attributes is None:
            self.attributes = {}

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return asdict(self)

    def __hash__(self):
        """支持集合操作"""
        return hash((self.source, self.target, self.type))


class RelationshipExtractor:
    """關係提取器：使用 LLM 從文本中提取實體關係"""

    # 常見關係類型
    RELATIONSHIP_TYPES = [
        "FOUNDED",              # 創立
        "DEVELOPED",            # 開發
        "WORKS_AT",             # 工作於
        "COLLABORATES_WITH",    # 合作
        "PART_OF",              # 屬於
        "LEADS",                # 領導
        "LOCATED_IN",           # 位於
        "HAPPENED_AT",          # 發生於
        "USES",                 # 使用
        "PRODUCES",             # 生產
        "ACQUIRED",             # 收購
        "INVESTED_IN",          # 投資
        "COMPETES_WITH",        # 競爭
        "RELATED_TO",           # 相關
        "SIMILAR_TO",           # 相似
        "CONTRIBUTED_TO",       # 貢獻於
    ]

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"):
        """
        初始化關係提取器

        Args:
            api_key: OpenAI API 密鑰
            model: 使用的模型名稱
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.extraction_count = 0

    def create_extraction_prompt(
            self,
            text: str,
            entities: List[str],
            relationship_types: List[str] = None
    ) -> str:
        """
        創建關係提取提示詞

        Args:
            text: 要處理的文本
            entities: 已識別的實體列表
            relationship_types: 要提取的關係類型列表

        Returns:
            提示詞字符串
        """
        if relationship_types is None:
            relationship_types = self.RELATIONSHIP_TYPES

        entities_str = ", ".join(entities)

        prompt = f"""你是一個專業的關係提取助手。請從以下文本中提取實體之間的關係。

文本：
{text}

已識別的實體：
{entities_str}

請提取這些實體之間的關係。關係類型包括但不限於：
{', '.join(relationship_types)}

對於每個關係，請提供：
1. source: 源實體名稱（必須來自已識別實體）
2. target: 目標實體名稱（必須來自已識別實體）
3. type: 關係類型（從上述列表選擇或自定義）
4. description: 關係描述（簡短說明）
5. weight: 關係強度（0.0-1.0，可選，默認 1.0）
6. confidence: 置信度（0.0-1.0）

請以 JSON 格式返回：
{{
    "relationships": [
        {{
            "source": "實體A",
            "target": "實體B",
            "type": "RELATIONSHIP_TYPE",
            "description": "描述",
            "weight": 0.9,
            "confidence": 0.95
        }}
    ]
}}

注意：
- 只提取明確的關係，不要推測
- source 和 target 必須是已識別的實體
- 提供足夠的描述以理解關係的上下文

只返回 JSON，不要包含其他說明文字。"""

        return prompt

    def extract_relationships_with_llm(
            self,
            text: str,
            entities: List[str],
            chunk_id: str
    ) -> List[Relationship]:
        """
        使用 LLM 提取關係

        Args:
            text: 文本內容
            entities: 實體列表
            chunk_id: 文本塊 ID

        Returns:
            提取的關係列表
        """
        try:
            print(f"   正在提取關係（chunk: {chunk_id}）...")

            # 模擬 API 調用
            import time
            time.sleep(0.1)

            # 實際應用中的 API 調用
            # response = openai.ChatCompletion.create(
            #     model=self.model,
            #     messages=[
            #         {"role": "system", "content": "你是一個關係提取專家。"},
            #         {"role": "user", "content": self.create_extraction_prompt(text, entities)}
            #     ],
            #     temperature=0
            # )
            # result = json.loads(response.choices[0].message.content)

            # 使用模擬數據
            result = self._mock_extraction(text, entities, chunk_id)

            # 轉換為 Relationship 對象
            relationships = []
            for rel_data in result.get("relationships", []):
                relationship = Relationship(
                    source=rel_data["source"],
                    target=rel_data["target"],
                    type=rel_data["type"],
                    description=rel_data["description"],
                    weight=rel_data.get("weight", 1.0),
                    source_chunks=[chunk_id],
                    confidence=rel_data.get("confidence", 0.9)
                )
                relationships.append(relationship)

            self.extraction_count += len(relationships)
            print(f"   ✓ 提取了 {len(relationships)} 個關係")

            return relationships

        except Exception as e:
            print(f"   ✗ 提取失敗: {e}")
            return []

    def _mock_extraction(
            self,
            text: str,
            entities: List[str],
            chunk_id: str
    ) -> Dict[str, Any]:
        """
        模擬關係提取

        Args:
            text: 文本內容
            entities: 實體列表
            chunk_id: 文本塊 ID

        Returns:
            模擬的提取結果
        """
        mock_relationships = []

        # 定義一些已知的關係模式
        patterns = [
            ("John McCarthy", "人工智能", "PROPOSED", "提出了人工智能概念", 1.0),
            ("Geoffrey Hinton", "深度學習", "CONTRIBUTED_TO", "對深度學習做出重要貢獻", 0.95),
            ("Yoshua Bengio", "深度學習", "CONTRIBUTED_TO", "對深度學習做出重要貢獻", 0.95),
            ("Yann LeCun", "深度學習", "CONTRIBUTED_TO", "對深度學習做出重要貢獻", 0.95),
            ("OpenAI", "ChatGPT", "DEVELOPED", "開發了 ChatGPT", 1.0),
            ("Google", "Bard", "DEVELOPED", "開發了 Bard", 1.0),
            ("Anthropic", "Claude", "DEVELOPED", "開發了 Claude", 1.0),
            ("Google", "Knowledge Graph", "PROPOSED", "提出了知識圖譜概念", 1.0),
            ("Microsoft Research", "GraphRAG", "DEVELOPED", "開發了 GraphRAG", 1.0),
            ("GraphRAG", "Knowledge Graph", "USES", "使用知識圖譜技術", 0.9),
            ("ChatGPT", "GPT-4", "USES", "基於 GPT-4 模型", 0.95),
        ]

        # 檢查文本中是否包含這些關係
        for source, target, rel_type, desc, weight in patterns:
            # 簡化的匹配邏輯
            if source in text and target in text:
                mock_relationships.append({
                    "source": source,
                    "target": target,
                    "type": rel_type,
                    "description": desc,
                    "weight": weight,
                    "confidence": 0.9
                })

        return {"relationships": mock_relationships}


class RelationshipValidator:
    """關係驗證器：驗證和過濾提取的關係"""

    def __init__(
            self,
            min_confidence: float = 0.7,
            min_weight: float = 0.5
    ):
        """
        初始化驗證器

        Args:
            min_confidence: 最低置信度閾值
            min_weight: 最低權重閾值
        """
        self.min_confidence = min_confidence
        self.min_weight = min_weight

    def validate(self, relationships: List[Relationship]) -> List[Relationship]:
        """
        驗證關係列表

        Args:
            relationships: 原始關係列表

        Returns:
            驗證通過的關係列表
        """
        validated = []
        rejected = []

        for rel in relationships:
            # 檢查置信度
            if rel.confidence < self.min_confidence:
                rejected.append((rel, f"置信度過低: {rel.confidence:.2f}"))
                continue

            # 檢查權重
            if rel.weight < self.min_weight:
                rejected.append((rel, f"權重過低: {rel.weight:.2f}"))
                continue

            # 檢查源和目標不能相同
            if rel.source == rel.target:
                rejected.append((rel, "源和目標相同"))
                continue

            # 檢查必填字段
            if not rel.source or not rel.target or not rel.type:
                rejected.append((rel, "缺少必填字段"))
                continue

            validated.append(rel)

        print(f"   驗證完成：{len(validated)} 個通過，{len(rejected)} 個被拒絕")

        if rejected:
            print(f"\n   被拒絕的關係：")
            for rel, reason in rejected[:5]:  # 只顯示前 5 個
                print(f"     • {rel.source} -> {rel.target}: {reason}")

        return validated

    def deduplicate(self, relationships: List[Relationship]) -> List[Relationship]:
        """
        去重關係列表

        Args:
            relationships: 原始關係列表

        Returns:
            去重後的關係列表
        """
        # 使用字典來去重和合併
        rel_dict = {}

        for rel in relationships:
            key = (rel.source, rel.target, rel.type)

            if key not in rel_dict:
                rel_dict[key] = rel
            else:
                # 合併重複的關係
                existing = rel_dict[key]

                # 合併來源塊
                existing.source_chunks = list(set(existing.source_chunks + rel.source_chunks))

                # 更新權重和置信度（取平均）
                existing.weight = (existing.weight + rel.weight) / 2
                existing.confidence = (existing.confidence + rel.confidence) / 2

                # 選擇更詳細的描述
                if len(rel.description) > len(existing.description):
                    existing.description = rel.description

        deduplicated = list(rel_dict.values())
        print(f"   去重：從 {len(relationships)} 減少到 {len(deduplicated)} 個關係")

        return deduplicated


class RelationshipAnalyzer:
    """關係分析器：分析關係網絡"""

    def __init__(self, relationships: List[Relationship]):
        """
        初始化分析器

        Args:
            relationships: 關係列表
        """
        self.relationships = relationships

    def get_statistics(self) -> Dict[str, Any]:
        """
        獲取關係統計信息

        Returns:
            統計信息字典
        """
        stats = {
            "total_relationships": len(self.relationships),
            "unique_entities": len(self._get_unique_entities()),
            "relationship_types": self._count_relationship_types(),
            "avg_weight": self._calculate_avg_weight(),
            "avg_confidence": self._calculate_avg_confidence()
        }

        return stats

    def _get_unique_entities(self) -> set:
        """獲取所有唯一實體"""
        entities = set()
        for rel in self.relationships:
            entities.add(rel.source)
            entities.add(rel.target)
        return entities

    def _count_relationship_types(self) -> Dict[str, int]:
        """統計關係類型分布"""
        type_count = defaultdict(int)
        for rel in self.relationships:
            type_count[rel.type] += 1
        return dict(type_count)

    def _calculate_avg_weight(self) -> float:
        """計算平均權重"""
        if not self.relationships:
            return 0.0
        return sum(rel.weight for rel in self.relationships) / len(self.relationships)

    def _calculate_avg_confidence(self) -> float:
        """計算平均置信度"""
        if not self.relationships:
            return 0.0
        return sum(rel.confidence for rel in self.relationships) / len(self.relationships)

    def find_hub_entities(self, top_n: int = 5) -> List[Tuple[str, int]]:
        """
        找出樞紐實體（連接數最多）

        Args:
            top_n: 返回前 N 個

        Returns:
            (實體名, 連接數) 的列表
        """
        entity_degree = defaultdict(int)

        for rel in self.relationships:
            entity_degree[rel.source] += 1
            entity_degree[rel.target] += 1

        sorted_entities = sorted(
            entity_degree.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return sorted_entities[:top_n]


def display_relationships(
        relationships: List[Relationship],
        title: str = "關係列表",
        limit: int = 10
):
    """
    顯示關係信息

    Args:
        relationships: 關係列表
        title: 標題
        limit: 顯示數量限制
    """
    print(f"\n{title}")
    print("-" * 70)

    # 統計分析
    analyzer = RelationshipAnalyzer(relationships)
    stats = analyzer.get_statistics()

    print(f"\n統計信息:")
    print(f"  總關係數: {stats['total_relationships']}")
    print(f"  涉及實體數: {stats['unique_entities']}")
    print(f"  平均權重: {stats['avg_weight']:.2f}")
    print(f"  平均置信度: {stats['avg_confidence']:.2f}")

    print(f"\n關係類型分布:")
    for rel_type, count in sorted(stats['relationship_types'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {rel_type}: {count}")

    print(f"\n樞紐實體（連接數最多）:")
    hub_entities = analyzer.find_hub_entities(5)
    for entity, degree in hub_entities:
        print(f"  {entity}: {degree} 個連接")

    print(f"\n關係詳情（前 {limit} 個）:")
    for i, rel in enumerate(relationships[:limit], 1):
        print(f"\n{i}. {rel.source} --[{rel.type}]--> {rel.target}")
        print(f"   描述: {rel.description}")
        print(f"   權重: {rel.weight:.2f} | 置信度: {rel.confidence:.2f}")
        print(f"   來源: {', '.join(rel.source_chunks)}")


def save_relationships(relationships: List[Relationship], output_path: str):
    """
    保存關係到文件

    Args:
        relationships: 關係列表
        output_path: 輸出文件路徑
    """
    try:
        from pathlib import Path
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # 轉換為字典列表
        rel_data = [rel.to_dict() for rel in relationships]

        # 保存為 JSON
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(rel_data, f, ensure_ascii=False, indent=2)

        print(f"✅ 關係已保存到: {output_path}")

    except Exception as e:
        print(f"❌ 保存關係失敗: {e}")


def main():
    """
    主函數：演示關係提取流程
    """
    print("=" * 70)
    print("🔗 GraphRAG 關係發現示例".center(70))
    print("=" * 70)
    print()

    # 加載環境變量
    load_dotenv()

    # 準備示例數據
    sample_text = """
    人工智能的發展歷程

    人工智能（AI）由 John McCarthy 在 1956 年提出。
    Geoffrey Hinton、Yoshua Bengio 和 Yann LeCun 對深度學習做出了重要貢獻。

    OpenAI 開發了 ChatGPT，它基於 GPT-4 模型。
    Google 開發了 Bard，Anthropic 開發了 Claude。

    Google 在 2012 年提出了知識圖譜（Knowledge Graph）概念。
    Microsoft Research 開發了 GraphRAG，它使用知識圖譜技術來增強 RAG 系統。
    """

    sample_entities = [
        "John McCarthy", "Geoffrey Hinton", "Yoshua Bengio", "Yann LeCun",
        "OpenAI", "ChatGPT", "GPT-4", "Google", "Bard", "Anthropic", "Claude",
        "Knowledge Graph", "Microsoft Research", "GraphRAG", "人工智能", "深度學習"
    ]

    # 步驟 1: 提取關係
    print("步驟 1: 從文本中提取關係")
    print("=" * 70)

    extractor = RelationshipExtractor()
    relationships = extractor.extract_relationships_with_llm(
        sample_text,
        sample_entities,
        "sample_chunk"
    )

    print(f"\n提取了 {len(relationships)} 個關係")
    print()

    # 步驟 2: 驗證和過濾
    print("\n步驟 2: 驗證和過濾關係")
    print("=" * 70)

    validator = RelationshipValidator(min_confidence=0.7, min_weight=0.5)
    validated_relationships = validator.validate(relationships)
    deduplicated_relationships = validator.deduplicate(validated_relationships)
    print()

    # 步驟 3: 分析關係
    print("\n步驟 3: 分析關係網絡")
    print("=" * 70)
    display_relationships(deduplicated_relationships, "已驗證的關係")
    print()

    # 步驟 4: 保存關係
    print("\n步驟 4: 保存關係")
    print("=" * 70)
    save_relationships(deduplicated_relationships, "./output/relationships.json")
    print()

    # 總結
    print("\n" + "=" * 70)
    print("💡 關係提取要點")
    print("=" * 70)
    print("""
    1. 關係類型設計：
       • 根據領域定義合適的關係類型
       • 保持類型粒度一致
       • 考慮雙向關係（如 PART_OF 和 HAS_PART）

    2. 提取策略：
       • 提供實體列表以提高準確率
       • 使用上下文窗口捕捉長距離關係
       • 設置合理的置信度閾值

    3. 質量控制：
       • 驗證源和目標實體的有效性
       • 過濾低置信度關係
       • 去重和合併重複關係

    4. 關係權重：
       • 基於頻率計算權重
       • 考慮關係的重要性
       • 可使用 PageRank 等算法

    5. 優化建議：
       • 分批處理大規模數據
       • 緩存已提取的關係
       • 定期更新和維護

    📚 下一步：查看 05_社區檢測.py 了解如何進行社區發現
    """)

    print("✅ 關係發現示例完成！")


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
