"""
GraphRAG 混合查詢示例

這個示例展示了如何結合 Local 和 Global Search：
1. 查詢意圖識別
2. 動態搜索策略選擇
3. 多模式結果融合
4. 自適應查詢優化

Author: GraphRAG Team
Date: 2025-12-31
"""

import os
import sys
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv


class QueryType(Enum):
    """查詢類型枚舉"""
    SPECIFIC_FACT = "specific_fact"      # 特定事實查詢
    GENERAL_TOPIC = "general_topic"      # 一般主題查詢
    RELATIONSHIP = "relationship"         # 關係查詢
    COMPARISON = "comparison"            # 比較查詢
    TREND_ANALYSIS = "trend_analysis"    # 趨勢分析
    MIXED = "mixed"                      # 混合查詢


@dataclass
class HybridSearchResult:
    """混合搜索結果"""
    answer: str
    query_type: QueryType
    search_strategy: str
    local_results: Optional[Dict[str, Any]] = None
    global_results: Optional[Dict[str, Any]] = None
    confidence: float = 0.0
    reasoning: str = ""


class QueryAnalyzer:
    """查詢分析器：識別查詢意圖和類型"""

    # 查詢模式關鍵詞
    PATTERNS = {
        QueryType.SPECIFIC_FACT: [
            "是誰", "是什麼", "何時", "在哪", "多少", "哪個",
            "誰是", "什麼是", "when", "who", "what", "where"
        ],
        QueryType.GENERAL_TOPIC: [
            "主要", "主題", "內容", "概述", "總結", "介紹",
            "overview", "summary", "main topic"
        ],
        QueryType.RELATIONSHIP: [
            "關係", "連接", "如何關聯", "之間", "與...有關",
            "relationship", "connected", "related to"
        ],
        QueryType.COMPARISON: [
            "比較", "區別", "不同", "相似", "對比", "vs",
            "compare", "difference", "similarity"
        ],
        QueryType.TREND_ANALYSIS: [
            "趨勢", "發展", "變化", "演進", "歷史", "未來",
            "trend", "evolution", "history", "development"
        ]
    }

    def analyze(self, query: str) -> Tuple[QueryType, Dict[str, Any]]:
        """
        分析查詢類型和特徵

        Args:
            query: 查詢文本

        Returns:
            (查詢類型, 查詢特徵字典)
        """
        query_lower = query.lower()

        # 計算每種類型的匹配分數
        scores = {}
        for query_type, patterns in self.PATTERNS.items():
            score = sum(1 for pattern in patterns if pattern in query_lower)
            scores[query_type] = score

        # 選擇得分最高的類型
        if max(scores.values()) == 0:
            detected_type = QueryType.GENERAL_TOPIC
        else:
            detected_type = max(scores, key=scores.get)

        # 提取查詢特徵
        features = {
            "length": len(query),
            "word_count": len(query.split()),
            "has_question_mark": "?" in query or "？" in query,
            "scores": scores
        }

        print(f"   查詢類型: {detected_type.value}")
        print(f"   特徵: 字數={features['word_count']}, 問句={features['has_question_mark']}")

        return detected_type, features


class SearchStrategySelector:
    """搜索策略選擇器：根據查詢類型選擇最佳策略"""

    # 策略映射
    STRATEGY_MAP = {
        QueryType.SPECIFIC_FACT: "local",
        QueryType.GENERAL_TOPIC: "global",
        QueryType.RELATIONSHIP: "local",
        QueryType.COMPARISON: "hybrid",
        QueryType.TREND_ANALYSIS: "global",
        QueryType.MIXED: "hybrid"
    }

    def select_strategy(
            self,
            query_type: QueryType,
            features: Dict[str, Any]
    ) -> str:
        """
        選擇搜索策略

        Args:
            query_type: 查詢類型
            features: 查詢特徵

        Returns:
            策略名稱：'local', 'global', 或 'hybrid'
        """
        # 基於類型的基本策略
        base_strategy = self.STRATEGY_MAP.get(query_type, "hybrid")

        # 基於特徵的調整
        # 例如：很長的查詢可能需要全局搜索
        if features["word_count"] > 15:
            if base_strategy == "local":
                base_strategy = "hybrid"

        # 如果是問句，傾向於本地搜索
        if features["has_question_mark"] and base_strategy == "global":
            base_strategy = "hybrid"

        print(f"   選擇策略: {base_strategy}")

        return base_strategy


class HybridSearchEngine:
    """混合搜索引擎：整合 Local 和 Global 搜索"""

    def __init__(
            self,
            local_search_engine=None,
            global_search_engine=None
    ):
        """
        初始化混合搜索引擎

        Args:
            local_search_engine: 本地搜索引擎
            global_search_engine: 全局搜索引擎
        """
        self.local_engine = local_search_engine
        self.global_engine = global_search_engine
        self.query_analyzer = QueryAnalyzer()
        self.strategy_selector = SearchStrategySelector()

    def search(self, query: str) -> HybridSearchResult:
        """
        執行混合搜索

        Args:
            query: 查詢問題

        Returns:
            混合搜索結果
        """
        print(f"\n🔀 執行混合搜索")
        print(f"   查詢: {query}")

        # 步驟 1: 分析查詢
        print(f"\n   步驟 1: 分析查詢意圖...")
        query_type, features = self.query_analyzer.analyze(query)

        # 步驟 2: 選擇策略
        print(f"\n   步驟 2: 選擇搜索策略...")
        strategy = self.strategy_selector.select_strategy(query_type, features)

        # 步驟 3: 執行搜索
        print(f"\n   步驟 3: 執行搜索...")

        local_results = None
        global_results = None

        if strategy == "local":
            local_results = self._execute_local_search(query)
            answer = self._format_local_answer(local_results)
            confidence = local_results.get("confidence", 0.8)

        elif strategy == "global":
            global_results = self._execute_global_search(query)
            answer = self._format_global_answer(global_results)
            confidence = global_results.get("confidence", 0.85)

        else:  # hybrid
            local_results = self._execute_local_search(query)
            global_results = self._execute_global_search(query)
            answer, confidence = self._merge_results(
                query, query_type, local_results, global_results
            )

        # 構建結果
        result = HybridSearchResult(
            answer=answer,
            query_type=query_type,
            search_strategy=strategy,
            local_results=local_results,
            global_results=global_results,
            confidence=confidence,
            reasoning=f"使用 {strategy} 策略處理 {query_type.value} 類型查詢"
        )

        print(f"   ✓ 搜索完成")

        return result

    def _execute_local_search(self, query: str) -> Dict[str, Any]:
        """執行本地搜索"""
        print(f"      • 執行本地搜索...")

        if self.local_engine:
            # 使用實際的本地搜索引擎
            result = self.local_engine.search(query)
            return {
                "answer": result.answer,
                "entities": result.entities,
                "relationships": result.relationships,
                "confidence": result.confidence
            }
        else:
            # 模擬結果
            return {
                "answer": "這是本地搜索的答案，基於特定實體和關係。",
                "entities": ["實體A", "實體B"],
                "relationships": [{"source": "實體A", "target": "實體B", "type": "RELATED"}],
                "confidence": 0.82
            }

    def _execute_global_search(self, query: str) -> Dict[str, Any]:
        """執行全局搜索"""
        print(f"      • 執行全局搜索...")

        if self.global_engine:
            # 使用實際的全局搜索引擎
            result = self.global_engine.search(query)
            return {
                "answer": result.answer,
                "communities": result.communities,
                "key_points": result.key_points,
                "confidence": result.confidence
            }
        else:
            # 模擬結果
            return {
                "answer": "這是全局搜索的答案，基於社區摘要和主題分析。",
                "communities": [{"title": "主題A", "summary": "摘要..."}],
                "key_points": ["要點1", "要點2"],
                "confidence": 0.85
            }

    def _format_local_answer(self, results: Dict[str, Any]) -> str:
        """格式化本地搜索答案"""
        return results.get("answer", "無法找到答案")

    def _format_global_answer(self, results: Dict[str, Any]) -> str:
        """格式化全局搜索答案"""
        return results.get("answer", "無法找到答案")

    def _merge_results(
            self,
            query: str,
            query_type: QueryType,
            local_results: Dict[str, Any],
            global_results: Dict[str, Any]
    ) -> Tuple[str, float]:
        """
        合併本地和全局搜索結果

        Args:
            query: 原始查詢
            query_type: 查詢類型
            local_results: 本地搜索結果
            global_results: 全局搜索結果

        Returns:
            (合併後的答案, 置信度)
        """
        print(f"      • 合併搜索結果...")

        # 根據查詢類型決定權重
        if query_type == QueryType.COMPARISON:
            # 比較查詢：平衡兩種結果
            local_weight = 0.5
            global_weight = 0.5
        elif query_type == QueryType.RELATIONSHIP:
            # 關係查詢：偏重本地搜索
            local_weight = 0.7
            global_weight = 0.3
        else:
            # 默認：平衡
            local_weight = 0.6
            global_weight = 0.4

        # 提取答案
        local_answer = local_results.get("answer", "")
        global_answer = global_results.get("answer", "")

        # 合併答案
        if local_answer and global_answer:
            merged_answer = f"{local_answer}\n\n從整體來看，{global_answer}"
        elif local_answer:
            merged_answer = local_answer
        elif global_answer:
            merged_answer = global_answer
        else:
            merged_answer = "無法找到相關信息。"

        # 計算綜合置信度
        local_conf = local_results.get("confidence", 0.5)
        global_conf = global_results.get("confidence", 0.5)
        merged_confidence = local_weight * local_conf + global_weight * global_conf

        return merged_answer, merged_confidence


def display_hybrid_result(result: HybridSearchResult):
    """
    顯示混合搜索結果

    Args:
        result: 搜索結果
    """
    print(f"\n" + "=" * 70)
    print("🔀 混合搜索結果")
    print("=" * 70)

    print(f"\n查詢類型: {result.query_type.value}")
    print(f"搜索策略: {result.search_strategy}")
    print(f"置信度: {result.confidence:.2%}")

    print(f"\n答案:")
    print(f"  {result.answer}")

    print(f"\n推理過程:")
    print(f"  {result.reasoning}")

    # 顯示詳細結果
    if result.local_results:
        print(f"\n本地搜索詳情:")
        print(f"  相關實體: {len(result.local_results.get('entities', []))} 個")
        print(f"  相關關係: {len(result.local_results.get('relationships', []))} 個")

    if result.global_results:
        print(f"\n全局搜索詳情:")
        print(f"  相關社區: {len(result.global_results.get('communities', []))} 個")
        if result.global_results.get('key_points'):
            print(f"  關鍵要點:")
            for point in result.global_results['key_points'][:3]:
                print(f"    • {point}")


def main():
    """
    主函數：演示混合查詢
    """
    print("=" * 70)
    print("🔀 GraphRAG 混合查詢示例".center(70))
    print("=" * 70)
    print()

    # 加載環境變量
    load_dotenv()

    # 創建混合搜索引擎
    # 注意：這裡使用 None，實際應傳入真實的搜索引擎實例
    hybrid_engine = HybridSearchEngine(
        local_search_engine=None,
        global_search_engine=None
    )

    # 不同類型的查詢示例
    queries = [
        # 特定事實查詢（應使用 Local Search）
        "Geoffrey Hinton 是誰？",

        # 一般主題查詢（應使用 Global Search）
        "這個數據集的主要內容是什麼？",

        # 關係查詢（應使用 Local Search）
        "OpenAI 和 ChatGPT 有什麼關係？",

        # 比較查詢（應使用 Hybrid Search）
        "ChatGPT 和 Bard 有什麼區別？",

        # 趨勢分析（應使用 Global Search）
        "AI 技術的發展趨勢是什麼？",

        # 混合查詢
        "深度學習三巨頭對整個 AI 領域有什麼影響？"
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{'=' * 70}")
        print(f"查詢 {i}: {query}")
        print(f"{'=' * 70}")

        result = hybrid_engine.search(query)
        display_hybrid_result(result)

        if i < len(queries):
            print("\n" + "-" * 70)

    # 總結
    print("\n\n" + "=" * 70)
    print("💡 混合查詢要點")
    print("=" * 70)
    print("""
    1. 查詢意圖識別：
       • 分析查詢關鍵詞和模式
       • 識別查詢類型（事實/主題/關係/比較/趨勢）
       • 提取查詢特徵（長度、結構等）

    2. 策略選擇矩陣：
       ┌──────────────────┬─────────────────┐
       │ 查詢類型         │ 推薦策略        │
       ├──────────────────┼─────────────────┤
       │ 特定事實         │ Local           │
       │ 一般主題         │ Global          │
       │ 關係查詢         │ Local           │
       │ 比較分析         │ Hybrid          │
       │ 趨勢分析         │ Global          │
       │ 複雜混合         │ Hybrid          │
       └──────────────────┴─────────────────┘

    3. 結果融合策略：
       • 基於查詢類型的權重調整
       • 置信度加權平均
       • 互補信息整合
       • 衝突解決機制

    4. 優化技巧：
       • 緩存常見查詢結果
       • 並行執行多種搜索
       • 動態調整策略權重
       • 學習用戶偏好

    5. 實際應用建議：
       • 從簡單策略開始（單一搜索）
       • 逐步增加複雜度
       • 收集用戶反饋優化策略
       • 監控性能指標

    6. 性能考慮：
       • Hybrid 模式成本較高（雙倍 API 調用）
       • 考慮實現智能緩存
       • 可選擇性地執行第二輪搜索
       • 設置超時和降級策略

    📚 下一步：查看 09_可視化.py 了解如何可視化知識圖譜
    """)

    print("✅ 混合查詢示例完成！")


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
