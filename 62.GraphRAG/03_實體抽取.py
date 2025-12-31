"""
GraphRAG 實體抽取示例

這個示例展示了如何進行實體識別和抽取：
1. 配置實體提取參數
2. 使用 LLM 進行實體識別
3. 實體消歧和合併
4. 實體屬性增強

Author: GraphRAG Team
Date: 2025-12-31
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv


@dataclass
class Entity:
    """實體數據類"""
    name: str
    type: str
    description: str
    source_chunks: List[str]
    attributes: Dict[str, Any] = None
    aliases: List[str] = None
    confidence: float = 1.0

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}
        if self.aliases is None:
            self.aliases = []

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return asdict(self)


class EntityExtractor:
    """實體提取器：使用 LLM 從文本中提取實體"""

    # 支持的實體類型
    ENTITY_TYPES = [
        "PERSON",           # 人物
        "ORGANIZATION",     # 組織
        "LOCATION",         # 地點
        "EVENT",            # 事件
        "PRODUCT",          # 產品
        "TECHNOLOGY",       # 技術
        "CONCEPT",          # 概念
        "DATE",             # 日期
        "METRIC",           # 指標
        "OTHER"             # 其他
    ]

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"):
        """
        初始化實體提取器

        Args:
            api_key: OpenAI API 密鑰
            model: 使用的模型名稱
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.extraction_count = 0

    def create_extraction_prompt(self, text: str, entity_types: List[str] = None) -> str:
        """
        創建實體提取提示詞

        Args:
            text: 要處理的文本
            entity_types: 要提取的實體類型列表

        Returns:
            提示詞字符串
        """
        if entity_types is None:
            entity_types = self.ENTITY_TYPES

        prompt = f"""你是一個專業的實體提取助手。請從以下文本中提取所有相關實體。

文本：
{text}

請提取以下類型的實體：
{', '.join(entity_types)}

對於每個實體，請提供：
1. name: 實體名稱（標準化形式）
2. type: 實體類型（從上述列表中選擇）
3. description: 簡短描述（1-2 句話）
4. aliases: 別名列表（如果有）
5. attributes: 相關屬性（如職位、成立時間等）

請以 JSON 格式返回，格式如下：
{{
    "entities": [
        {{
            "name": "實體名稱",
            "type": "實體類型",
            "description": "描述",
            "aliases": ["別名1", "別名2"],
            "attributes": {{"key": "value"}}
        }}
    ]
}}

只返回 JSON，不要包含其他說明文字。"""

        return prompt

    def extract_entities_with_llm(self, text: str, chunk_id: str) -> List[Entity]:
        """
        使用 LLM 提取實體（實際實現）

        Args:
            text: 文本內容
            chunk_id: 文本塊 ID

        Returns:
            提取的實體列表
        """
        try:
            # 在實際應用中，這裡會調用 OpenAI API
            # 由於這是示例代碼，我們使用模擬數據

            print(f"   正在提取實體（chunk: {chunk_id}）...")

            # 模擬 API 調用延遲
            import time
            time.sleep(0.1)

            # 這裡應該是實際的 API 調用
            # response = openai.ChatCompletion.create(
            #     model=self.model,
            #     messages=[
            #         {"role": "system", "content": "你是一個實體提取專家。"},
            #         {"role": "user", "content": self.create_extraction_prompt(text)}
            #     ],
            #     temperature=0
            # )
            # result = json.loads(response.choices[0].message.content)

            # 模擬提取結果
            result = self._mock_extraction(text, chunk_id)

            # 轉換為 Entity 對象
            entities = []
            for entity_data in result.get("entities", []):
                entity = Entity(
                    name=entity_data["name"],
                    type=entity_data["type"],
                    description=entity_data["description"],
                    source_chunks=[chunk_id],
                    attributes=entity_data.get("attributes", {}),
                    aliases=entity_data.get("aliases", []),
                    confidence=entity_data.get("confidence", 0.9)
                )
                entities.append(entity)

            self.extraction_count += len(entities)
            print(f"   ✓ 提取了 {len(entities)} 個實體")

            return entities

        except Exception as e:
            print(f"   ✗ 提取失敗: {e}")
            return []

    def _mock_extraction(self, text: str, chunk_id: str) -> Dict[str, Any]:
        """
        模擬實體提取（用於演示）

        Args:
            text: 文本內容
            chunk_id: 文本塊 ID

        Returns:
            模擬的提取結果
        """
        # 簡單的關鍵詞匹配（實際使用 LLM）
        mock_entities = []

        # 人物
        persons = ["John McCarthy", "Geoffrey Hinton", "Yoshua Bengio", "Yann LeCun", "Patrick Lewis"]
        for person in persons:
            if person in text:
                mock_entities.append({
                    "name": person,
                    "type": "PERSON",
                    "description": f"{person} 是 AI 領域的重要人物",
                    "aliases": [],
                    "attributes": {"field": "人工智能"},
                    "confidence": 0.95
                })

        # 組織
        orgs = ["OpenAI", "Google", "Microsoft", "Meta AI", "Anthropic"]
        for org in orgs:
            if org in text:
                mock_entities.append({
                    "name": org,
                    "type": "ORGANIZATION",
                    "description": f"{org} 是科技公司",
                    "aliases": [],
                    "attributes": {"industry": "科技"},
                    "confidence": 0.98
                })

        # 技術/產品
        techs = ["ChatGPT", "GPT-4", "Bard", "Claude", "GraphRAG", "Knowledge Graph", "RAG"]
        for tech in techs:
            if tech in text:
                mock_entities.append({
                    "name": tech,
                    "type": "TECHNOLOGY",
                    "description": f"{tech} 是一種技術或產品",
                    "aliases": [],
                    "attributes": {"category": "AI"},
                    "confidence": 0.92
                })

        return {"entities": mock_entities}


class EntityDeduplicator:
    """實體去重和合併器"""

    def __init__(self, similarity_threshold: float = 0.85):
        """
        初始化去重器

        Args:
            similarity_threshold: 相似度閾值
        """
        self.similarity_threshold = similarity_threshold

    def calculate_similarity(self, entity1: Entity, entity2: Entity) -> float:
        """
        計算兩個實體的相似度

        Args:
            entity1: 實體 1
            entity2: 實體 2

        Returns:
            相似度分數（0-1）
        """
        # 簡化的相似度計算
        # 實際應用中可以使用更複雜的算法或嵌入向量

        score = 0.0

        # 1. 名稱完全匹配
        if entity1.name.lower() == entity2.name.lower():
            score += 0.5

        # 2. 類型匹配
        if entity1.type == entity2.type:
            score += 0.2

        # 3. 別名匹配
        all_names1 = {entity1.name.lower()} | {a.lower() for a in entity1.aliases}
        all_names2 = {entity2.name.lower()} | {a.lower() for a in entity2.aliases}

        if all_names1 & all_names2:  # 有交集
            score += 0.3

        return score

    def merge_entities(self, entity1: Entity, entity2: Entity) -> Entity:
        """
        合併兩個實體

        Args:
            entity1: 實體 1
            entity2: 實體 2

        Returns:
            合併後的實體
        """
        # 選擇置信度更高的作為主實體
        if entity1.confidence >= entity2.confidence:
            main_entity, other_entity = entity1, entity2
        else:
            main_entity, other_entity = entity2, entity1

        # 合併來源
        merged_sources = list(set(main_entity.source_chunks + other_entity.source_chunks))

        # 合併別名
        merged_aliases = list(set(main_entity.aliases + other_entity.aliases + [other_entity.name]))
        if main_entity.name in merged_aliases:
            merged_aliases.remove(main_entity.name)

        # 合併屬性
        merged_attributes = {**other_entity.attributes, **main_entity.attributes}

        # 合併描述（選擇更長的）
        merged_description = main_entity.description if len(main_entity.description) >= len(
            other_entity.description) else other_entity.description

        return Entity(
            name=main_entity.name,
            type=main_entity.type,
            description=merged_description,
            source_chunks=merged_sources,
            attributes=merged_attributes,
            aliases=merged_aliases,
            confidence=(main_entity.confidence + other_entity.confidence) / 2
        )

    def deduplicate(self, entities: List[Entity]) -> List[Entity]:
        """
        去重實體列表

        Args:
            entities: 原始實體列表

        Returns:
            去重後的實體列表
        """
        if not entities:
            return []

        print(f"   開始去重，原始實體數: {len(entities)}")

        deduplicated = []
        processed = set()

        for i, entity1 in enumerate(entities):
            if i in processed:
                continue

            # 查找相似實體
            similar_entities = [entity1]
            similar_indices = {i}

            for j, entity2 in enumerate(entities[i + 1:], start=i + 1):
                if j in processed:
                    continue

                similarity = self.calculate_similarity(entity1, entity2)
                if similarity >= self.similarity_threshold:
                    similar_entities.append(entity2)
                    similar_indices.add(j)

            # 合併相似實體
            merged = similar_entities[0]
            for entity in similar_entities[1:]:
                merged = self.merge_entities(merged, entity)

            deduplicated.append(merged)
            processed.update(similar_indices)

        print(f"   ✓ 去重完成，最終實體數: {len(deduplicated)}")
        print(f"   減少了 {len(entities) - len(deduplicated)} 個重複實體")

        return deduplicated


def extract_entities_from_documents(documents: List[Dict[str, str]]) -> List[Entity]:
    """
    從文檔列表中提取實體

    Args:
        documents: 文檔列表

    Returns:
        提取的實體列表
    """
    print("\n📊 實體提取過程")
    print("-" * 70)

    extractor = EntityExtractor()
    all_entities = []

    for doc in documents:
        print(f"\n處理文檔: {doc['id']}")
        entities = extractor.extract_entities_with_llm(doc['text'], doc['id'])
        all_entities.extend(entities)

    print(f"\n總共提取了 {len(all_entities)} 個實體（包含重複）")
    return all_entities


def display_entities(entities: List[Entity], title: str = "實體列表", limit: int = 10):
    """
    顯示實體信息

    Args:
        entities: 實體列表
        title: 標題
        limit: 顯示數量限制
    """
    print(f"\n{title}")
    print("-" * 70)

    # 按類型分組
    by_type = {}
    for entity in entities:
        if entity.type not in by_type:
            by_type[entity.type] = []
        by_type[entity.type].append(entity)

    # 顯示統計
    print(f"\n實體類型分布:")
    for entity_type, type_entities in sorted(by_type.items()):
        print(f"  {entity_type}: {len(type_entities)}")

    # 顯示詳細信息
    print(f"\n實體詳情（前 {limit} 個）:")
    for i, entity in enumerate(entities[:limit], 1):
        print(f"\n{i}. {entity.name}")
        print(f"   類型: {entity.type}")
        print(f"   描述: {entity.description}")
        print(f"   置信度: {entity.confidence:.2f}")
        if entity.aliases:
            print(f"   別名: {', '.join(entity.aliases)}")
        if entity.attributes:
            print(f"   屬性: {entity.attributes}")
        print(f"   來源: {', '.join(entity.source_chunks)}")


def save_entities(entities: List[Entity], output_path: str):
    """
    保存實體到文件

    Args:
        entities: 實體列表
        output_path: 輸出文件路徑
    """
    try:
        from pathlib import Path
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # 轉換為字典列表
        entities_data = [entity.to_dict() for entity in entities]

        # 保存為 JSON
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(entities_data, f, ensure_ascii=False, indent=2)

        print(f"✅ 實體已保存到: {output_path}")

    except Exception as e:
        print(f"❌ 保存實體失敗: {e}")


def main():
    """
    主函數：演示實體提取流程
    """
    print("=" * 70)
    print("🔍 GraphRAG 實體抽取示例".center(70))
    print("=" * 70)
    print()

    # 加載環境變量
    load_dotenv()

    # 準備示例文檔
    documents = [
        {
            "id": "doc1",
            "text": """
            人工智能的發展歷程

            人工智能（Artificial Intelligence, AI）是計算機科學的一個分支，
            由 John McCarthy 在 1956 年的達特茅斯會議上首次提出。

            Geoffrey Hinton、Yoshua Bengio 和 Yann LeCun 因其在深度學習方面的貢獻
            而被稱為"深度學習三巨頭"。

            2022 年，OpenAI 發布了 ChatGPT，Google 發布了 Bard，
            Anthropic 發布了 Claude。
            """
        },
        {
            "id": "doc2",
            "text": """
            知識圖譜技術

            知識圖譜（Knowledge Graph）是一種結構化的知識表示方法，
            由 Google 在 2012 年提出。

            Microsoft Research 在 2024 年提出 GraphRAG，
            通過構建知識圖譜來增強 RAG 系統。
            """
        }
    ]

    # 步驟 1: 提取實體
    print("步驟 1: 從文檔中提取實體")
    print("=" * 70)
    entities = extract_entities_from_documents(documents)
    display_entities(entities, "原始提取的實體")
    print()

    # 步驟 2: 去重和合併
    print("\n步驟 2: 實體去重和合併")
    print("=" * 70)
    deduplicator = EntityDeduplicator(similarity_threshold=0.85)
    deduplicated_entities = deduplicator.deduplicate(entities)
    display_entities(deduplicated_entities, "去重後的實體")
    print()

    # 步驟 3: 保存實體
    print("\n步驟 3: 保存實體")
    print("=" * 70)
    save_entities(deduplicated_entities, "./output/entities.json")
    print()

    # 總結
    print("\n" + "=" * 70)
    print("💡 實體提取要點")
    print("=" * 70)
    print("""
    1. 實體類型定義：
       • 根據業務需求定義實體類型
       • 常見類型：人物、組織、地點、產品、概念等
       • 可以自定義領域特定的實體類型

    2. LLM 提示工程：
       • 清晰的指令和示例
       • 指定輸出格式（JSON）
       • 提供上下文和約束條件

    3. 實體消歧：
       • 識別同一實體的不同表述
       • 合併重複實體
       • 保留別名信息

    4. 質量控制：
       • 設置置信度閾值
       • 人工審核關鍵實體
       • 持續優化提示詞

    5. 性能優化：
       • 批處理減少 API 調用
       • 緩存已提取的實體
       • 增量更新而非全量重建

    📚 下一步：查看 04_關係發現.py 了解如何提取實體關係
    """)

    print("✅ 實體抽取示例完成！")


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
