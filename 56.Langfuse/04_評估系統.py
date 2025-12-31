"""
Langfuse 評估系統示例

這個示例展示 Langfuse 的評估和評分功能，包括：
- 自定義評分標準
- 人工評估整合
- 自動化評估
- 評估數據分析
- 質量監控
- 評估工作流

主要內容：
1. 基本評分功能
2. 多維度評估
3. 自動評估系統
4. 人工評估工作流
5. 評估數據分析
6. 質量閾值監控
7. 評估最佳實踐

作者: Langfuse Team
日期: 2025-01-01
"""

import os
import time
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from langfuse import Langfuse
from openai import OpenAI


# ============================================================================
# 第一部分：基本評分功能
# ============================================================================

class BasicScoring:
    """
    基本評分管理

    展示如何為追蹤和 generation 添加評分。
    """

    def __init__(self, langfuse: Langfuse):
        """
        初始化評分管理器

        Args:
            langfuse: Langfuse 客戶端實例
        """
        self.langfuse = langfuse
        self.openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "sk-demo")
        )

    def simple_score_example(self):
        """
        簡單評分示例

        展示如何為追蹤添加基本評分。
        """
        print("\n" + "="*60)
        print("簡單評分示例")
        print("="*60)

        # 創建追蹤
        trace = self.langfuse.trace(
            name="chatbot-response",
            user_id="user-score-demo",
            input={"message": "什麼是機器學習？"},
            metadata={"channel": "web-chat"}
        )

        # 模擬 AI 響應
        generation = trace.generation(
            name="ai-response",
            model="gpt-3.5-turbo",
            input=[{"role": "user", "content": "什麼是機器學習？"}]
        )

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "什麼是機器學習？"}]
            )

            output = response.choices[0].message.content

            generation.end(
                output=output,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            )

            print(f"💬 AI 響應已生成")

        except Exception as e:
            generation.end(level="ERROR", status_message=str(e))
            print(f"❌ 生成失敗: {e}")
            return

        # 添加評分
        # 評分方式 1: 數值評分（0-1）
        trace.score(
            name="quality",
            value=0.85,
            comment="回答準確且清晰"
        )
        print(f"⭐ 添加評分: quality = 0.85")

        # 評分方式 2: 分類評分
        trace.score(
            name="accuracy",
            value=1,  # 1 = 準確, 0 = 不準確
            data_type="CATEGORICAL",
            comment="內容準確無誤"
        )
        print(f"⭐ 添加評分: accuracy = 準確")

        # 評分方式 3: 帶詳細數據的評分
        trace.score(
            name="user_satisfaction",
            value=0.9,
            comment="用戶給予正面反饋",
            metadata={
                "feedback_source": "in-app-survey",
                "user_comment": "解釋得很清楚",
                "timestamp": datetime.now().isoformat()
            }
        )
        print(f"⭐ 添加評分: user_satisfaction = 0.9")

        print(f"\n✅ 評分添加完成")

        return trace

    def multi_dimensional_scoring(self):
        """
        多維度評分示例

        展示如何從多個維度評估 LLM 輸出。
        """
        print("\n" + "="*60)
        print("多維度評分示例")
        print("="*60)

        # 創建追蹤
        trace = self.langfuse.trace(
            name="content-generation",
            metadata={"task": "article-writing"}
        )

        print("📝 生成內容並進行多維度評估...")

        # 模擬內容生成
        time.sleep(0.2)

        # 定義評估維度
        evaluation_dimensions = {
            "relevance": {
                "value": 0.92,
                "comment": "內容與主題高度相關",
                "weight": 0.25
            },
            "coherence": {
                "value": 0.88,
                "comment": "邏輯連貫，結構清晰",
                "weight": 0.20
            },
            "fluency": {
                "value": 0.95,
                "comment": "語言流暢自然",
                "weight": 0.15
            },
            "accuracy": {
                "value": 0.90,
                "comment": "信息準確可靠",
                "weight": 0.25
            },
            "creativity": {
                "value": 0.75,
                "comment": "有一定創意但可以更好",
                "weight": 0.15
            }
        }

        print(f"\n評估維度:")

        # 添加各維度評分
        weighted_sum = 0
        total_weight = 0

        for dimension, metrics in evaluation_dimensions.items():
            trace.score(
                name=dimension,
                value=metrics["value"],
                comment=metrics["comment"],
                metadata={
                    "weight": metrics["weight"],
                    "dimension": dimension
                }
            )

            weighted_sum += metrics["value"] * metrics["weight"]
            total_weight += metrics["weight"]

            print(f"  • {dimension}: {metrics['value']:.2f} "
                  f"(權重: {metrics['weight']:.0%}) - {metrics['comment']}")

        # 計算加權平均分
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0

        # 添加總分
        trace.score(
            name="overall_quality",
            value=overall_score,
            comment=f"加權平均分",
            metadata={
                "calculation": "weighted_average",
                "dimensions": list(evaluation_dimensions.keys())
            }
        )

        print(f"\n📊 總體評分: {overall_score:.2f}")
        print(f"✅ 多維度評估完成")

        return trace


# ============================================================================
# 第二部分：自動評估系統
# ============================================================================

class AutomatedEvaluation:
    """
    自動評估系統

    實現基於規則和 LLM 的自動評估。
    """

    def __init__(self, langfuse: Langfuse):
        self.langfuse = langfuse
        self.openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "sk-demo")
        )

    def rule_based_evaluation(self):
        """
        基於規則的自動評估

        使用預定義規則自動評估輸出質量。
        """
        print("\n" + "="*60)
        print("基於規則的自動評估示例")
        print("="*60)

        # 模擬生成的文本
        generated_texts = [
            {
                "text": "這是一個很長的回答，包含了詳細的解釋和具體的例子。內容豐富且準確。",
                "user_query": "請解釋什麼是深度學習"
            },
            {
                "text": "好的。",
                "user_query": "請解釋什麼是深度學習"
            },
            {
                "text": "深度學習是機器學習的一個分支，使用多層神經網絡來學習數據的表示。",
                "user_query": "請解釋什麼是深度學習"
            }
        ]

        for idx, item in enumerate(generated_texts, 1):
            print(f"\n📄 評估文本 {idx}:")
            print(f"   查詢: {item['user_query']}")
            print(f"   回答: {item['text']}")

            trace = self.langfuse.trace(
                name=f"auto-eval-{idx}",
                input={"query": item["user_query"]},
                output={"response": item["text"]},
                metadata={"evaluation_type": "rule-based"}
            )

            # 規則 1: 長度檢查
            text_length = len(item["text"])
            length_score = min(text_length / 50, 1.0)  # 期望至少 50 字

            trace.score(
                name="length_adequacy",
                value=length_score,
                comment=f"文本長度: {text_length} 字符",
                metadata={"rule": "length_check", "length": text_length}
            )

            # 規則 2: 關鍵詞檢查
            keywords = ["深度學習", "神經網絡", "機器學習", "學習"]
            keyword_matches = sum(1 for kw in keywords if kw in item["text"])
            keyword_score = keyword_matches / len(keywords)

            trace.score(
                name="keyword_coverage",
                value=keyword_score,
                comment=f"包含 {keyword_matches}/{len(keywords)} 個關鍵詞",
                metadata={
                    "rule": "keyword_check",
                    "matches": keyword_matches,
                    "total": len(keywords)
                }
            )

            # 規則 3: 完整性檢查
            has_punctuation = any(p in item["text"] for p in ["。", ".", "！", "!"])
            completeness_score = 1.0 if has_punctuation else 0.5

            trace.score(
                name="completeness",
                value=completeness_score,
                comment="包含標點符號" if has_punctuation else "缺少標點符號",
                metadata={"rule": "completeness_check"}
            )

            # 計算總分
            overall_score = (length_score + keyword_score + completeness_score) / 3

            trace.score(
                name="auto_eval_overall",
                value=overall_score,
                comment=f"自動評估總分",
                metadata={
                    "evaluation_method": "rule-based",
                    "rules_applied": 3
                }
            )

            print(f"   📊 評估結果:")
            print(f"      長度充分性: {length_score:.2f}")
            print(f"      關鍵詞覆蓋: {keyword_score:.2f}")
            print(f"      完整性: {completeness_score:.2f}")
            print(f"      總分: {overall_score:.2f}")

        print(f"\n✅ 基於規則的評估完成")

    def llm_based_evaluation(self):
        """
        基於 LLM 的自動評估

        使用 LLM 來評估另一個 LLM 的輸出。
        """
        print("\n" + "="*60)
        print("基於 LLM 的自動評估示例")
        print("="*60)

        # 要評估的內容
        user_query = "請解釋量子計算的基本原理"
        ai_response = "量子計算利用量子力學的疊加和糾纏特性來進行計算。與傳統計算機使用比特不同，量子計算機使用量子比特（qubit）。"

        print(f"📋 待評估內容:")
        print(f"   查詢: {user_query}")
        print(f"   回答: {ai_response}")

        # 創建追蹤
        trace = self.langfuse.trace(
            name="llm-eval-demo",
            input={"query": user_query},
            output={"response": ai_response},
            metadata={"evaluation_type": "llm-based"}
        )

        # 使用 LLM 進行評估
        eval_prompt = f"""請評估以下 AI 回答的質量。

用戶問題：{user_query}

AI 回答：{ai_response}

請從以下維度評分（0-10）：
1. 準確性 (Accuracy)
2. 完整性 (Completeness)
3. 清晰度 (Clarity)

請以 JSON 格式返回評分和理由：
{{
    "accuracy": {{"score": X, "reason": "..."}},
    "completeness": {{"score": X, "reason": "..."}},
    "clarity": {{"score": X, "reason": "..."}}
}}"""

        print(f"\n🤖 使用 LLM 進行評估...")

        eval_generation = trace.generation(
            name="llm-evaluator",
            model="gpt-3.5-turbo",
            input=[{"role": "user", "content": eval_prompt}],
            metadata={"purpose": "evaluation"}
        )

        try:
            eval_response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": eval_prompt}],
                temperature=0.3
            )

            eval_result = eval_response.choices[0].message.content

            eval_generation.end(
                output=eval_result,
                usage={
                    "prompt_tokens": eval_response.usage.prompt_tokens,
                    "completion_tokens": eval_response.usage.completion_tokens,
                    "total_tokens": eval_response.usage.total_tokens
                }
            )

            print(f"   ✓ 評估完成")

            # 解析評估結果（簡化處理）
            try:
                # 嘗試解析 JSON
                import re
                json_match = re.search(r'\{.*\}', eval_result, re.DOTALL)
                if json_match:
                    eval_data = json.loads(json_match.group())

                    # 添加評分
                    for dimension, metrics in eval_data.items():
                        if isinstance(metrics, dict) and "score" in metrics:
                            normalized_score = metrics["score"] / 10.0
                            trace.score(
                                name=f"llm_eval_{dimension}",
                                value=normalized_score,
                                comment=metrics.get("reason", ""),
                                metadata={
                                    "evaluation_method": "llm-based",
                                    "evaluator_model": "gpt-3.5-turbo"
                                }
                            )

                            print(f"   • {dimension}: {normalized_score:.2f} - {metrics.get('reason', '')}")

            except Exception as e:
                print(f"   ⚠️  無法解析評估結果: {e}")

        except Exception as e:
            eval_generation.end(level="ERROR", status_message=str(e))
            print(f"   ✗ 評估失敗: {e}")

        print(f"\n✅ 基於 LLM 的評估完成")

        return trace


# ============================================================================
# 第三部分：人工評估工作流
# ============================================================================

class HumanEvaluation:
    """
    人工評估工作流

    模擬人工評估的流程。
    """

    def __init__(self, langfuse: Langfuse):
        self.langfuse = langfuse

    def simulate_human_review(self):
        """
        模擬人工審核流程

        展示如何整合人工評估到 Langfuse。
        """
        print("\n" + "="*60)
        print("人工評估工作流示例")
        print("="*60)

        # 創建需要審核的內容
        items_for_review = [
            {
                "id": "item-001",
                "query": "推薦一家餐廳",
                "response": "我推薦市中心的「美味軒」中餐廳，環境優雅，菜品精緻。",
                "auto_score": 0.85
            },
            {
                "id": "item-002",
                "query": "如何學習 Python",
                "response": "建議從基礎語法開始，然後做一些小項目練習。",
                "auto_score": 0.72
            },
            {
                "id": "item-003",
                "query": "今天天氣如何",
                "response": "抱歉，我無法獲取實時天氣信息。",
                "auto_score": 0.60
            }
        ]

        print(f"📋 待審核項目: {len(items_for_review)} 個\n")

        reviewed_items = []

        for item in items_for_review:
            print(f"審核項目: {item['id']}")
            print(f"  查詢: {item['query']}")
            print(f"  回答: {item['response']}")
            print(f"  自動評分: {item['auto_score']:.2f}")

            # 創建追蹤
            trace = self.langfuse.trace(
                name=f"human-review-{item['id']}",
                input={"query": item["query"]},
                output={"response": item["response"]},
                metadata={
                    "review_status": "pending",
                    "auto_score": item["auto_score"]
                }
            )

            # 模擬人工評審
            # 在實際應用中，這裡會暫停等待人工評審
            print(f"  ⏳ 等待人工評審...")
            time.sleep(0.1)

            # 模擬人工給出的評分
            human_scores = {
                "item-001": {
                    "relevance": 0.9,
                    "helpfulness": 0.85,
                    "overall": 0.88,
                    "feedback": "回答相關且有幫助，但可以提供更多細節"
                },
                "item-002": {
                    "relevance": 0.8,
                    "helpfulness": 0.70,
                    "overall": 0.75,
                    "feedback": "回答正確但過於簡略"
                },
                "item-003": {
                    "relevance": 0.7,
                    "helpfulness": 0.5,
                    "overall": 0.60,
                    "feedback": "誠實回答但未能滿足需求"
                }
            }

            scores = human_scores.get(item["id"], {})

            # 添加人工評分
            for score_name, score_value in scores.items():
                if score_name != "feedback":
                    trace.score(
                        name=f"human_{score_name}",
                        value=score_value,
                        comment=scores.get("feedback", ""),
                        metadata={
                            "reviewer": "human_reviewer_001",
                            "review_date": datetime.now().isoformat(),
                            "review_method": "manual"
                        }
                    )

            # 更新追蹤狀態
            trace.update(
                metadata={
                    "review_status": "completed",
                    "auto_score": item["auto_score"],
                    "human_score": scores.get("overall", 0),
                    "reviewer_feedback": scores.get("feedback", "")
                }
            )

            print(f"  ✅ 審核完成")
            print(f"     人工評分: {scores.get('overall', 0):.2f}")
            print(f"     反饋: {scores.get('feedback', '')}\n")

            reviewed_items.append({
                **item,
                "human_score": scores.get("overall", 0),
                "feedback": scores.get("feedback", "")
            })

        # 分析自動評分和人工評分的一致性
        print(f"="*60)
        print(f"📊 評分一致性分析:")

        auto_scores = [item["auto_score"] for item in reviewed_items]
        human_scores_list = [item["human_score"] for item in reviewed_items]

        avg_auto = sum(auto_scores) / len(auto_scores)
        avg_human = sum(human_scores_list) / len(human_scores_list)

        print(f"   自動評分平均: {avg_auto:.2f}")
        print(f"   人工評分平均: {avg_human:.2f}")
        print(f"   差異: {abs(avg_auto - avg_human):.2f}")

        print(f"\n✅ 人工評估工作流完成")


# ============================================================================
# 第四部分：評估數據分析
# ============================================================================

class EvaluationAnalytics:
    """
    評估數據分析

    分析和可視化評估數據。
    """

    def __init__(self, langfuse: Langfuse):
        self.langfuse = langfuse

    def generate_evaluation_report(self):
        """
        生成評估報告

        創建一個模擬的評估數據報告。
        """
        print("\n" + "="*60)
        print("評估數據分析示例")
        print("="*60)

        # 生成模擬評估數據
        print(f"📊 生成評估數據...")

        evaluation_data = []

        for i in range(50):
            trace = self.langfuse.trace(
                name=f"eval-sample-{i+1}",
                metadata={
                    "sample_id": i+1,
                    "category": random.choice(["chat", "qa", "summarization", "translation"])
                }
            )

            # 生成隨機評分
            quality_score = random.gauss(0.75, 0.15)
            quality_score = max(0, min(1, quality_score))  # 限制在 0-1

            accuracy_score = random.gauss(0.80, 0.12)
            accuracy_score = max(0, min(1, accuracy_score))

            relevance_score = random.gauss(0.78, 0.14)
            relevance_score = max(0, min(1, relevance_score))

            trace.score(name="quality", value=quality_score)
            trace.score(name="accuracy", value=accuracy_score)
            trace.score(name="relevance", value=relevance_score)

            evaluation_data.append({
                "quality": quality_score,
                "accuracy": accuracy_score,
                "relevance": relevance_score
            })

        print(f"   ✓ 生成 {len(evaluation_data)} 個評估樣本")

        # 計算統計數據
        print(f"\n📈 評估統計:")

        for metric in ["quality", "accuracy", "relevance"]:
            values = [item[metric] for item in evaluation_data]
            avg = sum(values) / len(values)
            min_val = min(values)
            max_val = max(values)

            # 計算標準差
            variance = sum((x - avg) ** 2 for x in values) / len(values)
            std_dev = variance ** 0.5

            print(f"\n   {metric.upper()}:")
            print(f"      平均值: {avg:.3f}")
            print(f"      最小值: {min_val:.3f}")
            print(f"      最大值: {max_val:.3f}")
            print(f"      標準差: {std_dev:.3f}")

            # 分布統計
            excellent = sum(1 for v in values if v >= 0.9)
            good = sum(1 for v in values if 0.7 <= v < 0.9)
            fair = sum(1 for v in values if 0.5 <= v < 0.7)
            poor = sum(1 for v in values if v < 0.5)

            print(f"      分布:")
            print(f"         優秀 (≥0.9): {excellent} ({excellent/len(values)*100:.1f}%)")
            print(f"         良好 (0.7-0.9): {good} ({good/len(values)*100:.1f}%)")
            print(f"         一般 (0.5-0.7): {fair} ({fair/len(values)*100:.1f}%)")
            print(f"         較差 (<0.5): {poor} ({poor/len(values)*100:.1f}%)")

        print(f"\n✅ 評估數據分析完成")


# ============================================================================
# 第五部分：質量閾值監控
# ============================================================================

class QualityMonitoring:
    """
    質量閾值監控

    監控質量指標並在低於閾值時發出警報。
    """

    def __init__(self, langfuse: Langfuse):
        self.langfuse = langfuse
        self.quality_thresholds = {
            "accuracy": 0.80,
            "relevance": 0.75,
            "fluency": 0.85
        }

    def monitor_quality_example(self):
        """
        質量監控示例

        模擬實時質量監控。
        """
        print("\n" + "="*60)
        print("質量閾值監控示例")
        print("="*60)

        print(f"📋 質量閾值設定:")
        for metric, threshold in self.quality_thresholds.items():
            print(f"   {metric}: {threshold:.2f}")

        print(f"\n🔍 開始監控...")

        alerts = []

        # 模擬 20 個請求的監控
        for i in range(20):
            trace = self.langfuse.trace(
                name=f"monitored-request-{i+1}",
                metadata={"request_id": f"req-{i+1:03d}"}
            )

            # 生成隨機質量分數
            scores = {
                "accuracy": random.gauss(0.82, 0.15),
                "relevance": random.gauss(0.78, 0.12),
                "fluency": random.gauss(0.88, 0.10)
            }

            # 限制分數範圍
            for key in scores:
                scores[key] = max(0, min(1, scores[key]))

            # 添加評分
            violations = []

            for metric, score in scores.items():
                trace.score(
                    name=metric,
                    value=score,
                    metadata={
                        "threshold": self.quality_thresholds[metric],
                        "monitoring": True
                    }
                )

                # 檢查是否低於閾值
                threshold = self.quality_thresholds[metric]
                if score < threshold:
                    violations.append({
                        "metric": metric,
                        "score": score,
                        "threshold": threshold,
                        "deficit": threshold - score
                    })

            # 如果有違規，記錄警報
            if violations:
                alert_msg = f"請求 {i+1}: "
                for v in violations:
                    alert_msg += f"{v['metric']} ({v['score']:.2f} < {v['threshold']:.2f}) "

                alerts.append({
                    "request_id": i+1,
                    "violations": violations,
                    "message": alert_msg
                })

                print(f"   ⚠️  {alert_msg}")

                # 添加警報標記
                trace.update(
                    metadata={
                        "quality_alert": True,
                        "violations": violations
                    },
                    tags=["quality-alert", "below-threshold"]
                )
            else:
                print(f"   ✓ 請求 {i+1}: 所有指標正常")

            time.sleep(0.05)

        # 總結
        print(f"\n" + "="*60)
        print(f"監控總結:")
        print(f"   總請求數: 20")
        print(f"   警報數量: {len(alerts)}")
        print(f"   警報率: {len(alerts)/20*100:.1f}%")

        if alerts:
            print(f"\n   詳細警報:")
            for alert in alerts[:5]:  # 只顯示前 5 個
                print(f"      {alert['message']}")

        print(f"\n✅ 質量監控完成")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """
    主函數：運行所有評估系統示例
    """
    print("\n" + "="*70)
    print("Langfuse 評估系統示例")
    print("="*70)

    # 初始化 Langfuse
    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY", "pk-demo"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY", "sk-demo"),
        debug=True
    )

    try:
        # 1. 基本評分
        print("\n第一部分：基本評分功能")
        print("="*70)
        basic_scoring = BasicScoring(langfuse)
        basic_scoring.simple_score_example()
        basic_scoring.multi_dimensional_scoring()

        # 2. 自動評估
        print("\n第二部分：自動評估系統")
        print("="*70)
        auto_eval = AutomatedEvaluation(langfuse)
        auto_eval.rule_based_evaluation()
        auto_eval.llm_based_evaluation()

        # 3. 人工評估
        print("\n第三部分：人工評估工作流")
        print("="*70)
        human_eval = HumanEvaluation(langfuse)
        human_eval.simulate_human_review()

        # 4. 數據分析
        print("\n第四部分：評估數據分析")
        print("="*70)
        analytics = EvaluationAnalytics(langfuse)
        analytics.generate_evaluation_report()

        # 5. 質量監控
        print("\n第五部分：質量閾值監控")
        print("="*70)
        monitoring = QualityMonitoring(langfuse)
        monitoring.monitor_quality_example()

        print("\n" + "="*70)
        print("✅ 所有評估系統示例運行完成！")
        print("="*70)

        print("\n💡 最佳實踐:")
        print("   1. 結合自動和人工評估提高準確性")
        print("   2. 設定合理的質量閾值並持續監控")
        print("   3. 使用多維度評估獲得全面視角")
        print("   4. 定期分析評估數據優化系統")
        print("   5. 建立評估反饋循環持續改進")

        # 刷新數據
        langfuse.flush()

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
