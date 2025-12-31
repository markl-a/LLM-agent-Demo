"""
Langfuse 用戶反饋收集示例

這個示例展示如何使用 Langfuse 收集和管理用戶反饋，包括：
- 顯式反饋收集
- 隱式反饋追蹤
- 評分系統整合
- 反饋分析
- 改進循環
- A/B 測試反饋

主要內容：
1. 基本反饋收集
2. 多種反饋類型
3. 反饋與追蹤關聯
4. 反饋分析和統計
5. 反饋驅動的優化
6. 反饋可視化
7. 反饋工作流自動化

作者: Langfuse Team
日期: 2025-01-01
"""

import os
import time
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from langfuse import Langfuse


# ============================================================================
# 第一部分：基本反饋收集
# ============================================================================

class FeedbackCollection:
    """
    反饋收集管理

    提供基本的用戶反饋收集功能。
    """

    def __init__(self, langfuse: Langfuse):
        """
        初始化反饋收集器

        Args:
            langfuse: Langfuse 客戶端實例
        """
        self.langfuse = langfuse

    def explicit_feedback_example(self):
        """
        顯式反饋收集示例

        用戶主動提供的反饋（如點贊、評分等）。
        """
        print("\n" + "="*60)
        print("顯式反饋收集示例")
        print("="*60)

        # 模擬一個聊天交互
        print("💬 模擬聊天交互...")

        trace = self.langfuse.trace(
            name="chat-with-feedback",
            user_id="user-feedback-001",
            input={"message": "如何學習 Python？"},
            metadata={"channel": "web-chat"}
        )

        # 模擬 AI 響應
        ai_response = "學習 Python 的建議：1. 從基礎語法開始 2. 做實際項目 3. 閱讀優質代碼 4. 參與開源社區"

        trace.update(
            output={"response": ai_response}
        )

        print(f"   用戶問題: 如何學習 Python？")
        print(f"   AI 回答: {ai_response}")

        # 用戶提供反饋
        print(f"\n👍 用戶反饋...")

        # 反饋類型 1: 點贊/踩
        thumbs_up = True

        trace.score(
            name="user_feedback_thumbs",
            value=1 if thumbs_up else 0,
            data_type="CATEGORICAL",
            comment="用戶點贊" if thumbs_up else "用戶踩",
            metadata={
                "feedback_type": "thumbs",
                "feedback_time": datetime.now().isoformat(),
                "feedback_source": "ui_button"
            }
        )

        print(f"   反饋類型: {'👍 點贊' if thumbs_up else '👎 踩'}")

        # 反饋類型 2: 星級評分
        star_rating = 4  # 1-5 星

        trace.score(
            name="user_feedback_stars",
            value=star_rating / 5.0,  # 歸一化到 0-1
            comment=f"用戶評分 {star_rating}/5 星",
            metadata={
                "feedback_type": "star_rating",
                "stars": star_rating,
                "max_stars": 5
            }
        )

        print(f"   星級評分: {'⭐' * star_rating} ({star_rating}/5)")

        # 反饋類型 3: 文字評論
        user_comment = "解釋得很清楚，但希望能提供更多具體的學習資源鏈接。"

        trace.score(
            name="user_feedback_comment",
            value=1.0,  # 有評論就設為 1
            comment=user_comment,
            metadata={
                "feedback_type": "text_comment",
                "comment_length": len(user_comment)
            }
        )

        print(f"   用戶評論: {user_comment}")

        print(f"\n✅ 反饋收集完成")

        return trace

    def implicit_feedback_example(self):
        """
        隱式反饋追蹤示例

        通過用戶行為推斷的反饋（如點擊、停留時間等）。
        """
        print("\n" + "="*60)
        print("隱式反饋追蹤示例")
        print("="*60)

        print("📊 追蹤用戶行為...")

        trace = self.langfuse.trace(
            name="response-with-implicit-feedback",
            user_id="user-behavior-001",
            metadata={"interaction_type": "search_result"}
        )

        # 模擬用戶行為數據
        user_behavior = {
            "clicked_result": True,
            "time_on_page": 45.5,  # 秒
            "scrolled_percent": 85,  # 滾動百分比
            "copied_text": True,
            "shared": False,
            "followed_link": True
        }

        print(f"\n用戶行為數據:")
        print(f"   點擊結果: {'是' if user_behavior['clicked_result'] else '否'}")
        print(f"   停留時間: {user_behavior['time_on_page']:.1f} 秒")
        print(f"   滾動深度: {user_behavior['scrolled_percent']}%")
        print(f"   複製文本: {'是' if user_behavior['copied_text'] else '否'}")
        print(f"   分享內容: {'是' if user_behavior['shared'] else '否'}")
        print(f"   點擊鏈接: {'是' if user_behavior['followed_link'] else '否'}")

        # 基於行為計算隱式滿意度
        satisfaction_score = 0

        # 點擊表示感興趣
        if user_behavior['clicked_result']:
            satisfaction_score += 0.2

        # 停留時間長表示內容有價值
        if user_behavior['time_on_page'] > 30:
            satisfaction_score += 0.3
        elif user_behavior['time_on_page'] > 10:
            satisfaction_score += 0.1

        # 滾動深度表示閱讀完整度
        if user_behavior['scrolled_percent'] > 70:
            satisfaction_score += 0.2
        elif user_behavior['scrolled_percent'] > 40:
            satisfaction_score += 0.1

        # 複製文本表示有用
        if user_behavior['copied_text']:
            satisfaction_score += 0.15

        # 分享表示高度認可
        if user_behavior['shared']:
            satisfaction_score += 0.15

        # 點擊鏈接表示進一步探索
        if user_behavior['followed_link']:
            satisfaction_score += 0.1

        # 添加隱式反饋評分
        trace.score(
            name="implicit_satisfaction",
            value=min(satisfaction_score, 1.0),
            comment="基於用戶行為推斷的滿意度",
            metadata={
                "feedback_type": "implicit",
                "behavior_data": user_behavior,
                "calculation_method": "weighted_behavior_scoring"
            }
        )

        print(f"\n📈 隱式滿意度評分: {satisfaction_score:.2f}")

        print(f"\n✅ 隱式反饋追蹤完成")

        return trace


# ============================================================================
# 第二部分：反饋類型管理
# ============================================================================

class FeedbackTypes:
    """
    反饋類型管理

    支持多種反饋類型和格式。
    """

    def __init__(self, langfuse: Langfuse):
        self.langfuse = langfuse

    def multi_type_feedback_example(self):
        """
        多類型反饋示例

        展示不同類型的反饋收集。
        """
        print("\n" + "="*60)
        print("多類型反饋示例")
        print("="*60)

        # 創建一個內容生成追蹤
        trace = self.langfuse.trace(
            name="content-generation-with-feedback",
            metadata={"content_type": "blog_post"}
        )

        print("📝 收集多維度反饋...\n")

        # 1. 二元反饋（是/否）
        binary_feedbacks = {
            "helpful": True,
            "accurate": True,
            "clear": True,
            "complete": False,
            "relevant": True
        }

        print("1️⃣ 二元反饋:")
        for metric, value in binary_feedbacks.items():
            trace.score(
                name=f"binary_{metric}",
                value=1 if value else 0,
                data_type="CATEGORICAL",
                comment=f"{'是' if value else '否'}",
                metadata={"feedback_type": "binary"}
            )
            print(f"   {metric}: {'✅' if value else '❌'}")

        # 2. 數值評分（1-10）
        numeric_feedbacks = {
            "quality": 8,
            "readability": 9,
            "depth": 6,
            "originality": 7
        }

        print(f"\n2️⃣ 數值評分 (1-10):")
        for metric, score in numeric_feedbacks.items():
            trace.score(
                name=f"numeric_{metric}",
                value=score / 10.0,
                comment=f"評分: {score}/10",
                metadata={
                    "feedback_type": "numeric",
                    "scale": "1-10",
                    "raw_score": score
                }
            )
            bar = "█" * score + "░" * (10 - score)
            print(f"   {metric:12s}: {bar} {score}/10")

        # 3. 分類反饋
        categorical_feedbacks = {
            "tone": "professional",  # professional, casual, formal
            "difficulty": "intermediate",  # beginner, intermediate, advanced
            "length": "appropriate",  # too_short, appropriate, too_long
            "style": "informative"  # informative, persuasive, entertaining
        }

        print(f"\n3️⃣ 分類反饋:")
        for metric, category in categorical_feedbacks.items():
            trace.score(
                name=f"categorical_{metric}",
                value=1,  # 分類反饋用 1 表示有效
                data_type="CATEGORICAL",
                comment=category,
                metadata={
                    "feedback_type": "categorical",
                    "category": category,
                    "metric": metric
                }
            )
            print(f"   {metric}: {category}")

        # 4. 多選反饋
        multi_select_feedback = {
            "strengths": ["clear_structure", "good_examples", "actionable_advice"],
            "weaknesses": ["lacks_depth", "needs_more_sources"]
        }

        print(f"\n4️⃣ 多選反饋:")
        for category, selections in multi_select_feedback.items():
            trace.score(
                name=f"multi_select_{category}",
                value=len(selections) / 5.0,  # 假設最多 5 個選項
                comment=", ".join(selections),
                metadata={
                    "feedback_type": "multi_select",
                    "selections": selections,
                    "count": len(selections)
                }
            )
            print(f"   {category}:")
            for item in selections:
                print(f"      • {item}")

        print(f"\n✅ 多類型反饋收集完成")

        return trace

    def contextual_feedback_example(self):
        """
        情境化反饋示例

        根據使用情境收集特定反饋。
        """
        print("\n" + "="*60)
        print("情境化反饋示例")
        print("="*60)

        # 不同使用場景的反饋
        scenarios = [
            {
                "name": "customer_support",
                "context": "客戶支援對話",
                "metrics": {
                    "resolved_issue": True,
                    "response_time_satisfaction": 0.9,
                    "agent_politeness": 0.95,
                    "would_recommend": True
                }
            },
            {
                "name": "code_generation",
                "context": "代碼生成任務",
                "metrics": {
                    "code_works": True,
                    "code_quality": 0.85,
                    "follows_best_practices": 0.80,
                    "well_documented": 0.75
                }
            },
            {
                "name": "creative_writing",
                "context": "創意寫作",
                "metrics": {
                    "creativity": 0.88,
                    "grammar": 0.95,
                    "engaging": 0.82,
                    "meets_requirements": 0.90
                }
            }
        ]

        for scenario in scenarios:
            print(f"\n📍 場景: {scenario['context']}")

            trace = self.langfuse.trace(
                name=f"feedback-{scenario['name']}",
                metadata={
                    "scenario": scenario['name'],
                    "context": scenario['context']
                }
            )

            for metric, value in scenario['metrics'].items():
                # 處理布爾值和浮點值
                if isinstance(value, bool):
                    score_value = 1 if value else 0
                    comment = "是" if value else "否"
                else:
                    score_value = value
                    comment = f"{value:.0%}"

                trace.score(
                    name=f"{scenario['name']}_{metric}",
                    value=score_value,
                    comment=comment,
                    metadata={
                        "scenario": scenario['name'],
                        "metric_type": "boolean" if isinstance(value, bool) else "numeric"
                    }
                )

                print(f"   • {metric}: {comment}")

            print(f"   ✓ 情境反饋已記錄")

        print(f"\n✅ 情境化反饋完成")


# ============================================================================
# 第三部分：反饋分析
# ============================================================================

class FeedbackAnalytics:
    """
    反饋分析

    分析和統計用戶反饋數據。
    """

    def __init__(self, langfuse: Langfuse):
        self.langfuse = langfuse

    def feedback_statistics_example(self):
        """
        反饋統計示例

        生成反饋數據的統計報告。
        """
        print("\n" + "="*60)
        print("反饋統計分析示例")
        print("="*60)

        # 模擬收集 100 條反饋
        print("📊 生成反饋統計數據...\n")

        feedback_data = {
            "thumbs_up": 0,
            "thumbs_down": 0,
            "star_ratings": [],
            "satisfaction_scores": [],
            "categories": {
                "helpful": 0,
                "not_helpful": 0,
                "needs_improvement": 0
            }
        }

        for i in range(100):
            # 模擬反饋（偏向正面）
            thumbs = random.choice([True] * 7 + [False] * 3)
            stars = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30])[0]
            satisfaction = random.gauss(0.75, 0.15)
            satisfaction = max(0, min(1, satisfaction))

            if thumbs:
                feedback_data["thumbs_up"] += 1
            else:
                feedback_data["thumbs_down"] += 1

            feedback_data["star_ratings"].append(stars)
            feedback_data["satisfaction_scores"].append(satisfaction)

            # 分類
            if satisfaction > 0.8:
                feedback_data["categories"]["helpful"] += 1
            elif satisfaction < 0.5:
                feedback_data["categories"]["not_helpful"] += 1
            else:
                feedback_data["categories"]["needs_improvement"] += 1

            # 記錄到 Langfuse
            trace = self.langfuse.trace(
                name=f"feedback-sample-{i+1}",
                metadata={"sample_id": i+1}
            )

            trace.score(
                name="user_satisfaction",
                value=satisfaction,
                metadata={
                    "thumbs": thumbs,
                    "stars": stars
                }
            )

        # 計算統計數據
        total_feedback = feedback_data["thumbs_up"] + feedback_data["thumbs_down"]
        thumbs_up_rate = feedback_data["thumbs_up"] / total_feedback if total_feedback > 0 else 0

        avg_stars = sum(feedback_data["star_ratings"]) / len(feedback_data["star_ratings"])
        avg_satisfaction = sum(feedback_data["satisfaction_scores"]) / len(feedback_data["satisfaction_scores"])

        # 顯示統計結果
        print("="*60)
        print("               反饋統計報告")
        print("="*60)

        print(f"\n📊 總體統計:")
        print(f"   總反饋數: {total_feedback}")
        print(f"   點贊率: {thumbs_up_rate:.1%} ({feedback_data['thumbs_up']}/{total_feedback})")
        print(f"   平均星級: {'⭐' * int(avg_stars)} {avg_stars:.2f}/5")
        print(f"   平均滿意度: {avg_satisfaction:.2%}")

        print(f"\n📈 星級分布:")
        for stars in range(5, 0, -1):
            count = feedback_data["star_ratings"].count(stars)
            percent = count / len(feedback_data["star_ratings"])
            bar_length = int(percent * 40)
            bar = "█" * bar_length
            print(f"   {stars}⭐ {bar:40s} {count:3d} ({percent:.1%})")

        print(f"\n🏷️  反饋分類:")
        for category, count in feedback_data["categories"].items():
            percent = count / total_feedback
            print(f"   {category:20s}: {count:3d} ({percent:.1%})")

        print(f"\n📉 滿意度分布:")
        satisfaction_ranges = [
            (0.9, 1.0, "非常滿意"),
            (0.7, 0.9, "滿意"),
            (0.5, 0.7, "一般"),
            (0.3, 0.5, "不滿意"),
            (0.0, 0.3, "非常不滿意")
        ]

        for min_val, max_val, label in satisfaction_ranges:
            count = sum(1 for s in feedback_data["satisfaction_scores"] if min_val <= s < max_val)
            percent = count / len(feedback_data["satisfaction_scores"])
            print(f"   {label:12s} ({min_val:.1f}-{max_val:.1f}): {count:3d} ({percent:.1%})")

        print(f"\n✅ 反饋統計完成")

    def sentiment_trend_analysis(self):
        """
        情感趨勢分析示例

        分析反饋的時間趨勢。
        """
        print("\n" + "="*60)
        print("反饋趨勢分析示例")
        print("="*60)

        print("📈 分析過去 30 天的反饋趨勢...\n")

        # 模擬 30 天的數據
        daily_feedback = []

        for day in range(30):
            date = datetime.now() - timedelta(days=29-day)

            # 模擬每日反饋（趨勢向上）
            base_satisfaction = 0.65 + (day / 30) * 0.20  # 從 0.65 提升到 0.85
            noise = random.gauss(0, 0.05)
            satisfaction = max(0, min(1, base_satisfaction + noise))

            feedback_count = random.randint(15, 35)

            daily_feedback.append({
                "date": date,
                "satisfaction": satisfaction,
                "count": feedback_count
            })

        # 顯示趨勢
        print("每日滿意度趨勢:")
        print(f"{'日期':<12} {'滿意度':<10} {'反饋數':<10} {'圖表':<30}")
        print("-" * 70)

        for data in daily_feedback[-14:]:  # 顯示最近 14 天
            date_str = data["date"].strftime("%m/%d")
            bar_length = int(data["satisfaction"] * 30)
            bar = "█" * bar_length

            print(f"{date_str:<12} {data['satisfaction']:.2%}   {data['count']:<10} {bar}")

        # 計算趨勢
        first_week_avg = sum(d["satisfaction"] for d in daily_feedback[:7]) / 7
        last_week_avg = sum(d["satisfaction"] for d in daily_feedback[-7:]) / 7
        trend = last_week_avg - first_week_avg

        print(f"\n📊 趨勢分析:")
        print(f"   首週平均: {first_week_avg:.2%}")
        print(f"   末週平均: {last_week_avg:.2%}")

        if trend > 0:
            print(f"   趨勢: ⬆️  上升 {trend:.2%} (正向)")
        elif trend < 0:
            print(f"   趨勢: ⬇️  下降 {abs(trend):.2%} (需關注)")
        else:
            print(f"   趨勢: ➡️  持平")

        print(f"\n✅ 趨勢分析完成")


# ============================================================================
# 第四部分：反饋驅動的優化
# ============================================================================

class FeedbackDrivenOptimization:
    """
    反饋驅動的優化

    基於用戶反饋進行系統優化。
    """

    def __init__(self, langfuse: Langfuse):
        self.langfuse = langfuse

    def identify_improvement_areas(self):
        """
        識別改進領域示例

        基於反饋識別需要改進的地方。
        """
        print("\n" + "="*60)
        print("改進領域識別示例")
        print("="*60)

        print("🔍 分析反饋數據識別改進機會...\n")

        # 模擬不同功能的反饋數據
        features = {
            "response_accuracy": {
                "avg_score": 0.88,
                "feedback_count": 150,
                "negative_feedback": 18,
                "common_issues": ["有時信息過時", "缺少引用來源"]
            },
            "response_speed": {
                "avg_score": 0.72,
                "feedback_count": 150,
                "negative_feedback": 42,
                "common_issues": ["響應慢", "超時"]
            },
            "response_clarity": {
                "avg_score": 0.85,
                "feedback_count": 150,
                "negative_feedback": 22,
                "common_issues": ["解釋不夠清楚", "術語太多"]
            },
            "user_interface": {
                "avg_score": 0.65,
                "feedback_count": 150,
                "negative_feedback": 52,
                "common_issues": ["不直觀", "功能難找"]
            },
            "response_completeness": {
                "avg_score": 0.80,
                "feedback_count": 150,
                "negative_feedback": 30,
                "common_issues": ["回答不完整", "缺少細節"]
            }
        }

        # 排序找出最需要改進的功能
        sorted_features = sorted(
            features.items(),
            key=lambda x: (x[1]["avg_score"], -x[1]["negative_feedback"])
        )

        print("📊 功能評分排名:")
        print(f"{'功能':<25} {'平均分':<12} {'負面反饋':<12} {'狀態':<10}")
        print("-" * 70)

        for feature_name, data in sorted_features:
            score = data["avg_score"]
            negative = data["negative_feedback"]
            negative_rate = negative / data["feedback_count"]

            # 確定狀態
            if score >= 0.85 and negative_rate < 0.15:
                status = "✅ 良好"
            elif score >= 0.75:
                status = "⚠️  需關注"
            else:
                status = "🔴 需改進"

            print(f"{feature_name:<25} {score:<12.2%} {negative:<12} {status}")

        # 詳細改進建議
        print(f"\n💡 改進建議（優先級從高到低）:")

        priority = 1
        for feature_name, data in sorted_features:
            if data["avg_score"] < 0.80:  # 只顯示低分功能
                print(f"\n   {priority}. {feature_name} (評分: {data['avg_score']:.2%})")
                print(f"      常見問題:")
                for issue in data["common_issues"]:
                    print(f"         • {issue}")

                # 給出具體建議
                if "speed" in feature_name.lower():
                    print(f"      建議: 優化後端性能，實施緩存策略")
                elif "interface" in feature_name.lower():
                    print(f"      建議: 重新設計 UI，進行用戶體驗測試")
                elif "accuracy" in feature_name.lower():
                    print(f"      建議: 更新知識庫，添加引用來源")
                elif "clarity" in feature_name.lower():
                    print(f"      建議: 簡化語言，添加示例說明")
                else:
                    print(f"      建議: 增加回答深度，提供更多細節")

                priority += 1

        print(f"\n✅ 改進領域識別完成")

    def ab_test_feedback_comparison(self):
        """
        A/B 測試反饋對比示例

        比較不同版本的用戶反饋。
        """
        print("\n" + "="*60)
        print("A/B 測試反饋對比示例")
        print("="*60)

        print("🧪 對比兩個版本的用戶反饋...\n")

        # 模擬 A/B 測試數據
        variant_a = {
            "name": "原始版本",
            "users": 500,
            "feedback_count": 125,
            "avg_satisfaction": 0.72,
            "thumbs_up_rate": 0.68,
            "avg_response_time": 2.8
        }

        variant_b = {
            "name": "優化版本",
            "users": 500,
            "feedback_count": 130,
            "avg_satisfaction": 0.85,
            "thumbs_up_rate": 0.82,
            "avg_response_time": 1.5
        }

        # 顯示對比
        print("="*70)
        print(f"                  A/B 測試結果對比")
        print("="*70)

        metrics = [
            ("用戶數", "users", ""),
            ("反饋數", "feedback_count", ""),
            ("平均滿意度", "avg_satisfaction", "%"),
            ("點贊率", "thumbs_up_rate", "%"),
            ("平均響應時間", "avg_response_time", "s")
        ]

        print(f"\n{'指標':<20} {'版本 A':<15} {'版本 B':<15} {'改進':<15}")
        print("-" * 70)

        for metric_name, key, unit in metrics:
            val_a = variant_a[key]
            val_b = variant_b[key]

            if unit == "%":
                str_a = f"{val_a:.1%}"
                str_b = f"{val_b:.1%}"
                improvement = val_b - val_a
                str_imp = f"+{improvement:.1%}" if improvement > 0 else f"{improvement:.1%}"
            elif unit == "s":
                str_a = f"{val_a:.1f}s"
                str_b = f"{val_b:.1f}s"
                improvement = ((val_a - val_b) / val_a) if val_a > 0 else 0
                str_imp = f"-{improvement:.1%}" if improvement > 0 else f"+{abs(improvement):.1%}"
            else:
                str_a = str(val_a)
                str_b = str(val_b)
                improvement = val_b - val_a
                str_imp = f"+{improvement}" if improvement > 0 else str(improvement)

            print(f"{metric_name:<20} {str_a:<15} {str_b:<15} {str_imp:<15}")

        # 統計顯著性（簡化判斷）
        satisfaction_diff = variant_b["avg_satisfaction"] - variant_a["avg_satisfaction"]

        print(f"\n📊 統計分析:")
        print(f"   滿意度提升: {satisfaction_diff:.2%}")

        if satisfaction_diff > 0.10:
            significance = "顯著提升 ✅"
            recommendation = "建議採用版本 B"
        elif satisfaction_diff > 0.05:
            significance = "中等提升 ⚠️"
            recommendation = "可以考慮採用版本 B"
        else:
            significance = "輕微提升"
            recommendation = "需要更多數據"

        print(f"   統計意義: {significance}")
        print(f"   建議: {recommendation}")

        print(f"\n✅ A/B 測試對比完成")


# ============================================================================
# 第五部分：反饋工作流自動化
# ============================================================================

class FeedbackAutomation:
    """
    反饋工作流自動化

    自動化反饋收集和處理流程。
    """

    def __init__(self, langfuse: Langfuse):
        self.langfuse = langfuse

    def automated_feedback_workflow(self):
        """
        自動化反饋工作流示例

        展示自動化的反饋收集和響應流程。
        """
        print("\n" + "="*60)
        print("自動化反饋工作流示例")
        print("="*60)

        print("🤖 運行自動化反饋工作流...\n")

        # 模擬 10 個用戶交互
        for i in range(10):
            user_id = f"user-{i+1:03d}"

            trace = self.langfuse.trace(
                name=f"automated-interaction-{i+1}",
                user_id=user_id,
                metadata={"automation": True}
            )

            # 模擬用戶反饋
            satisfaction = random.gauss(0.75, 0.20)
            satisfaction = max(0, min(1, satisfaction))

            trace.score(
                name="user_satisfaction",
                value=satisfaction,
                metadata={"automated_collection": True}
            )

            # 自動化響應邏輯
            if satisfaction < 0.5:
                # 低滿意度：觸發人工審核
                action = "🚨 觸發人工審核"
                trace.update(
                    metadata={
                        "automated_action": "escalate_to_human",
                        "reason": "low_satisfaction"
                    },
                    tags=["needs-review", "low-satisfaction"]
                )

            elif satisfaction < 0.7:
                # 中等滿意度：發送反饋請求
                action = "📧 發送詳細反饋請求"
                trace.update(
                    metadata={
                        "automated_action": "request_detailed_feedback",
                        "reason": "medium_satisfaction"
                    },
                    tags=["feedback-requested"]
                )

            else:
                # 高滿意度：記錄為成功案例
                action = "✅ 記錄為成功案例"
                trace.update(
                    metadata={
                        "automated_action": "mark_as_success",
                        "reason": "high_satisfaction"
                    },
                    tags=["success-case"]
                )

            print(f"   用戶 {user_id}: 滿意度 {satisfaction:.2%} → {action}")

        print(f"\n✅ 自動化工作流完成")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """
    主函數：運行所有用戶反饋示例
    """
    print("\n" + "="*70)
    print("Langfuse 用戶反饋收集示例")
    print("="*70)

    # 初始化 Langfuse
    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY", "pk-demo"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY", "sk-demo"),
        debug=True
    )

    try:
        # 1. 基本反饋收集
        print("\n第一部分：基本反饋收集")
        print("="*70)
        collection = FeedbackCollection(langfuse)
        collection.explicit_feedback_example()
        collection.implicit_feedback_example()

        # 2. 反饋類型管理
        print("\n第二部分：反饋類型管理")
        print("="*70)
        types = FeedbackTypes(langfuse)
        types.multi_type_feedback_example()
        types.contextual_feedback_example()

        # 3. 反饋分析
        print("\n第三部分：反饋分析")
        print("="*70)
        analytics = FeedbackAnalytics(langfuse)
        analytics.feedback_statistics_example()
        analytics.sentiment_trend_analysis()

        # 4. 反饋驅動的優化
        print("\n第四部分：反饋驅動的優化")
        print("="*70)
        optimization = FeedbackDrivenOptimization(langfuse)
        optimization.identify_improvement_areas()
        optimization.ab_test_feedback_comparison()

        # 5. 反饋工作流自動化
        print("\n第五部分：反饋工作流自動化")
        print("="*70)
        automation = FeedbackAutomation(langfuse)
        automation.automated_feedback_workflow()

        print("\n" + "="*70)
        print("✅ 所有用戶反饋示例運行完成！")
        print("="*70)

        print("\n💡 反饋管理最佳實踐:")
        print("   1. 結合顯式和隱式反饋獲得全面視角")
        print("   2. 使用多種反饋類型滿足不同場景需求")
        print("   3. 定期分析反饋趨勢發現問題")
        print("   4. 基於反饋數據優先級排序改進事項")
        print("   5. 使用 A/B 測試驗證優化效果")
        print("   6. 自動化反饋收集和初步處理流程")
        print("   7. 對負面反饋建立及時響應機制")

        # 刷新數據
        langfuse.flush()

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
