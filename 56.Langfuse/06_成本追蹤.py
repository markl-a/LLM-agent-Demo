"""
Langfuse 成本追蹤示例

這個示例展示如何使用 Langfuse 追蹤和分析 LLM API 調用成本，包括：
- Token 使用追蹤
- 成本計算
- 預算管理
- 成本優化建議
- 多模型成本對比
- 成本報告生成

主要內容：
1. 基本成本追蹤
2. 多模型成本對比
3. 用戶級成本追蹤
4. 預算警報系統
5. 成本優化分析
6. 成本趨勢報告
7. 成本節省策略

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
# 第一部分：基本成本追蹤
# ============================================================================

class CostTracking:
    """
    成本追蹤管理

    提供基本的成本追蹤和計算功能。
    """

    # 模型定價（每 1000 tokens 的美元價格）
    MODEL_PRICING = {
        "gpt-4": {
            "input": 0.03,
            "output": 0.06
        },
        "gpt-4-turbo": {
            "input": 0.01,
            "output": 0.03
        },
        "gpt-3.5-turbo": {
            "input": 0.0005,
            "output": 0.0015
        },
        "claude-3-opus": {
            "input": 0.015,
            "output": 0.075
        },
        "claude-3-sonnet": {
            "input": 0.003,
            "output": 0.015
        }
    }

    def __init__(self, langfuse: Langfuse):
        """
        初始化成本追蹤器

        Args:
            langfuse: Langfuse 客戶端實例
        """
        self.langfuse = langfuse
        self.openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "sk-demo")
        )

    def calculate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """
        計算 API 調用成本

        Args:
            model: 模型名稱
            prompt_tokens: 輸入 tokens
            completion_tokens: 輸出 tokens

        Returns:
            成本（美元）
        """
        pricing = self.MODEL_PRICING.get(model, {
            "input": 0.001,
            "output": 0.002
        })

        input_cost = (prompt_tokens / 1000) * pricing["input"]
        output_cost = (completion_tokens / 1000) * pricing["output"]

        return input_cost + output_cost

    def basic_cost_tracking_example(self):
        """
        基本成本追蹤示例

        展示如何追蹤單次 API 調用的成本。
        """
        print("\n" + "="*60)
        print("基本成本追蹤示例")
        print("="*60)

        # 創建追蹤
        trace = self.langfuse.trace(
            name="cost-tracking-demo",
            user_id="user-cost-001",
            metadata={"purpose": "cost_tracking"}
        )

        # 調用 LLM
        model = "gpt-3.5-turbo"
        messages = [
            {"role": "user", "content": "請用 100 字介紹人工智慧。"}
        ]

        print(f"🤖 使用模型: {model}")
        print(f"📝 發送請求...")

        generation = trace.generation(
            name="ai-response",
            model=model,
            input=messages
        )

        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages
            )

            output = response.choices[0].message.content
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens

            # 計算成本
            cost = self.calculate_cost(model, prompt_tokens, completion_tokens)

            # 記錄使用量和成本
            generation.end(
                output=output,
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                },
                metadata={
                    "cost_usd": cost,
                    "cost_breakdown": {
                        "input_tokens": prompt_tokens,
                        "output_tokens": completion_tokens,
                        "input_cost": (prompt_tokens / 1000) * self.MODEL_PRICING[model]["input"],
                        "output_cost": (completion_tokens / 1000) * self.MODEL_PRICING[model]["output"]
                    }
                }
            )

            print(f"\n✅ 請求完成")
            print(f"\n💰 成本分析:")
            print(f"   輸入 Tokens: {prompt_tokens}")
            print(f"   輸出 Tokens: {completion_tokens}")
            print(f"   總 Tokens: {total_tokens}")
            print(f"   總成本: ${cost:.6f} USD")
            print(f"   約 NT${cost * 30:.4f}")

        except Exception as e:
            generation.end(level="ERROR", status_message=str(e))
            print(f"❌ 請求失敗: {e}")

        return trace

    def batch_cost_tracking(self):
        """
        批量成本追蹤示例

        追蹤多次調用的總成本。
        """
        print("\n" + "="*60)
        print("批量成本追蹤示例")
        print("="*60)

        # 模擬 20 次 API 調用
        total_cost = 0
        total_tokens = 0
        call_count = 20

        print(f"📊 模擬 {call_count} 次 API 調用...\n")

        for i in range(call_count):
            # 隨機選擇模型
            model = random.choice(["gpt-3.5-turbo", "gpt-4"])

            # 模擬 token 使用
            prompt_tokens = random.randint(50, 200)
            completion_tokens = random.randint(100, 500)

            # 計算成本
            cost = self.calculate_cost(model, prompt_tokens, completion_tokens)

            # 創建追蹤
            trace = self.langfuse.trace(
                name=f"batch-call-{i+1}",
                metadata={
                    "batch_id": "batch-001",
                    "call_number": i + 1
                }
            )

            generation = trace.generation(
                name="batch-generation",
                model=model,
                input={"prompt": f"Request {i+1}"},
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                },
                metadata={
                    "cost_usd": cost,
                    "model": model
                }
            )

            generation.end(output={"response": f"Response {i+1}"})

            total_cost += cost
            total_tokens += (prompt_tokens + completion_tokens)

            if (i + 1) % 5 == 0:
                print(f"   完成 {i+1}/{call_count} 次調用...")

        # 統計結果
        avg_cost = total_cost / call_count
        avg_tokens = total_tokens / call_count

        print(f"\n💰 批量成本統計:")
        print(f"   總調用次數: {call_count}")
        print(f"   總 Tokens: {total_tokens:,}")
        print(f"   平均 Tokens/次: {avg_tokens:.0f}")
        print(f"   總成本: ${total_cost:.4f} USD")
        print(f"   平均成本/次: ${avg_cost:.6f} USD")
        print(f"   約 NT${total_cost * 30:.2f}")

        print(f"\n✅ 批量追蹤完成")


# ============================================================================
# 第二部分：多模型成本對比
# ============================================================================

class ModelCostComparison:
    """
    模型成本對比

    比較不同模型的成本效益。
    """

    def __init__(self, langfuse: Langfuse):
        self.langfuse = langfuse
        self.cost_tracker = CostTracking(langfuse)

    def compare_models_example(self):
        """
        模型成本對比示例

        對比使用不同模型的成本差異。
        """
        print("\n" + "="*60)
        print("多模型成本對比示例")
        print("="*60)

        # 測試相同任務在不同模型上的成本
        task = "請用 200 字解釋機器學習的基本概念。"

        models = [
            "gpt-3.5-turbo",
            "gpt-4-turbo",
            "gpt-4"
        ]

        print(f"📋 測試任務: {task[:50]}...")
        print(f"🔬 測試模型: {', '.join(models)}\n")

        results = []

        for model in models:
            print(f"測試模型: {model}")

            # 模擬調用（實際應該真實調用）
            # 這裡使用模擬數據以避免實際成本
            if model == "gpt-3.5-turbo":
                prompt_tokens = 25
                completion_tokens = 150
            elif model == "gpt-4-turbo":
                prompt_tokens = 25
                completion_tokens = 180
            else:  # gpt-4
                prompt_tokens = 25
                completion_tokens = 200

            cost = self.cost_tracker.calculate_cost(
                model,
                prompt_tokens,
                completion_tokens
            )

            # 記錄追蹤
            trace = self.langfuse.trace(
                name=f"model-comparison-{model}",
                metadata={
                    "comparison_task": "model_cost_comparison",
                    "model": model
                }
            )

            generation = trace.generation(
                name="comparison-generation",
                model=model,
                input={"task": task},
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                },
                metadata={"cost_usd": cost}
            )

            generation.end(output={"response": f"Response from {model}"})

            results.append({
                "model": model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "cost": cost
            })

            print(f"   Tokens: {prompt_tokens + completion_tokens}")
            print(f"   成本: ${cost:.6f} USD\n")

        # 對比分析
        print("="*60)
        print("📊 成本對比分析:")
        print("="*60)

        # 找出最便宜和最貴的
        cheapest = min(results, key=lambda x: x["cost"])
        most_expensive = max(results, key=lambda x: x["cost"])

        print(f"\n💰 成本排名:")
        for idx, result in enumerate(sorted(results, key=lambda x: x["cost"]), 1):
            print(f"   {idx}. {result['model']:20s} ${result['cost']:.6f} USD")

        cost_diff = most_expensive["cost"] - cheapest["cost"]
        cost_ratio = most_expensive["cost"] / cheapest["cost"] if cheapest["cost"] > 0 else 0

        print(f"\n📈 成本差異:")
        print(f"   最便宜: {cheapest['model']} (${cheapest['cost']:.6f})")
        print(f"   最昂貴: {most_expensive['model']} (${most_expensive['cost']:.6f})")
        print(f"   差額: ${cost_diff:.6f} ({cost_ratio:.1f}x)")

        print(f"\n💡 建議:")
        if cost_ratio > 10:
            print(f"   考慮使用 {cheapest['model']} 以大幅降低成本")
        else:
            print(f"   根據任務複雜度選擇合適的模型")

        print(f"\n✅ 模型對比完成")


# ============================================================================
# 第三部分：用戶級成本追蹤
# ============================================================================

class UserCostTracking:
    """
    用戶級成本追蹤

    追蹤每個用戶的成本使用情況。
    """

    def __init__(self, langfuse: Langfuse):
        self.langfuse = langfuse
        self.cost_tracker = CostTracking(langfuse)

    def track_user_costs_example(self):
        """
        用戶成本追蹤示例

        追蹤和分析不同用戶的成本。
        """
        print("\n" + "="*60)
        print("用戶級成本追蹤示例")
        print("="*60)

        # 模擬多個用戶的使用
        users = ["user-001", "user-002", "user-003", "user-004", "user-005"]
        user_costs = {user: 0 for user in users}
        user_requests = {user: 0 for user in users}

        print(f"👥 追蹤 {len(users)} 個用戶的成本...")

        # 模擬 50 次請求
        for i in range(50):
            user_id = random.choice(users)
            model = random.choice(["gpt-3.5-turbo", "gpt-4"])

            # 模擬 token 使用
            prompt_tokens = random.randint(50, 150)
            completion_tokens = random.randint(100, 400)

            cost = self.cost_tracker.calculate_cost(
                model,
                prompt_tokens,
                completion_tokens
            )

            # 記錄追蹤
            trace = self.langfuse.trace(
                name=f"user-request-{i+1}",
                user_id=user_id,
                metadata={
                    "cost_usd": cost,
                    "model": model
                }
            )

            generation = trace.generation(
                name="user-generation",
                model=model,
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                },
                metadata={"cost_usd": cost}
            )

            generation.end(output={"response": "..."})

            # 累計用戶成本
            user_costs[user_id] += cost
            user_requests[user_id] += 1

        # 分析結果
        print(f"\n📊 用戶成本統計:")
        print(f"{'用戶 ID':<12} {'請求次數':<10} {'總成本':<15} {'平均成本/次':<15}")
        print("-" * 60)

        for user_id in sorted(users):
            total_cost = user_costs[user_id]
            requests = user_requests[user_id]
            avg_cost = total_cost / requests if requests > 0 else 0

            print(f"{user_id:<12} {requests:<10} ${total_cost:<14.6f} ${avg_cost:<14.6f}")

        # 總計
        total_cost = sum(user_costs.values())
        total_requests = sum(user_requests.values())

        print("-" * 60)
        print(f"{'總計':<12} {total_requests:<10} ${total_cost:<14.4f}")

        # 找出高成本用戶
        high_cost_users = [(uid, cost) for uid, cost in user_costs.items() if cost > total_cost / len(users)]

        print(f"\n⚠️  高成本用戶 (超過平均值):")
        for user_id, cost in sorted(high_cost_users, key=lambda x: x[1], reverse=True):
            print(f"   {user_id}: ${cost:.4f} USD")

        print(f"\n✅ 用戶成本追蹤完成")


# ============================================================================
# 第四部分：預算警報系統
# ============================================================================

class BudgetAlertSystem:
    """
    預算警報系統

    監控成本並在接近預算時發出警報。
    """

    def __init__(self, langfuse: Langfuse):
        self.langfuse = langfuse
        self.cost_tracker = CostTracking(langfuse)

    def budget_monitoring_example(self):
        """
        預算監控示例

        實時監控成本並發出預算警報。
        """
        print("\n" + "="*60)
        print("預算警報系統示例")
        print("="*60)

        # 設定預算
        daily_budget = 10.00  # 美元
        alert_threshold = 0.80  # 80% 時警報
        critical_threshold = 0.95  # 95% 時嚴重警報

        print(f"💵 預算設定:")
        print(f"   每日預算: ${daily_budget:.2f} USD")
        print(f"   警報閾值: {alert_threshold*100:.0f}%")
        print(f"   嚴重閾值: {critical_threshold*100:.0f}%")

        print(f"\n🔍 開始監控...")

        current_cost = 0
        request_count = 0
        alerts = []

        # 模擬持續的 API 調用
        for i in range(100):
            model = random.choice(["gpt-3.5-turbo", "gpt-4"])

            prompt_tokens = random.randint(50, 200)
            completion_tokens = random.randint(100, 500)

            cost = self.cost_tracker.calculate_cost(
                model,
                prompt_tokens,
                completion_tokens
            )

            current_cost += cost
            request_count += 1

            # 計算預算使用百分比
            budget_usage = current_cost / daily_budget

            # 檢查預算狀態
            status = "正常"
            if budget_usage >= critical_threshold:
                status = "🔴 嚴重"
                if len(alerts) == 0 or alerts[-1]["level"] != "critical":
                    alerts.append({
                        "level": "critical",
                        "message": f"預算使用已達 {budget_usage*100:.1f}%！",
                        "request": request_count,
                        "cost": current_cost
                    })
                    print(f"\n   🚨 嚴重警報！預算使用: {budget_usage*100:.1f}%")

            elif budget_usage >= alert_threshold:
                status = "🟡 警告"
                if len(alerts) == 0 or (alerts[-1]["level"] != "warning" and alerts[-1]["level"] != "critical"):
                    alerts.append({
                        "level": "warning",
                        "message": f"預算使用已達 {budget_usage*100:.1f}%",
                        "request": request_count,
                        "cost": current_cost
                    })
                    print(f"\n   ⚠️  預算警告！預算使用: {budget_usage*100:.1f}%")

            # 記錄追蹤
            trace = self.langfuse.trace(
                name=f"budget-monitored-request-{i+1}",
                metadata={
                    "cost_usd": cost,
                    "cumulative_cost": current_cost,
                    "budget_usage_percent": budget_usage * 100,
                    "budget_status": status,
                    "daily_budget": daily_budget
                },
                tags=["budget-monitoring", status.split()[0] if status != "正常" else "normal"]
            )

            # 如果超過預算，停止
            if current_cost >= daily_budget:
                print(f"\n   🛑 預算耗盡！停止請求。")
                break

            # 每 20 次請求報告一次
            if (i + 1) % 20 == 0:
                print(f"   第 {i+1} 次請求 - 已使用: ${current_cost:.4f} ({budget_usage*100:.1f}%)")

        # 最終報告
        print(f"\n" + "="*60)
        print("📊 預算使用報告:")
        print(f"   總請求數: {request_count}")
        print(f"   總成本: ${current_cost:.4f} USD")
        print(f"   預算使用: {(current_cost/daily_budget)*100:.1f}%")
        print(f"   剩餘預算: ${max(0, daily_budget - current_cost):.4f} USD")

        if alerts:
            print(f"\n⚠️  警報記錄:")
            for alert in alerts:
                print(f"   [{alert['level'].upper()}] 第 {alert['request']} 次請求")
                print(f"       {alert['message']}")
                print(f"       當時成本: ${alert['cost']:.4f}")

        print(f"\n✅ 預算監控完成")


# ============================================================================
# 第五部分：成本優化分析
# ============================================================================

class CostOptimization:
    """
    成本優化分析

    提供成本優化建議。
    """

    def __init__(self, langfuse: Langfuse):
        self.langfuse = langfuse
        self.cost_tracker = CostTracking(langfuse)

    def optimization_analysis_example(self):
        """
        成本優化分析示例

        分析使用模式並提供優化建議。
        """
        print("\n" + "="*60)
        print("成本優化分析示例")
        print("="*60)

        # 模擬一週的使用數據
        print("📊 分析過去一週的使用數據...")

        total_cost = 0
        model_usage = {}
        task_costs = {}

        # 模擬不同類型的任務
        tasks = {
            "simple_qa": {"count": 100, "avg_tokens": 200, "model": "gpt-3.5-turbo"},
            "complex_analysis": {"count": 20, "avg_tokens": 1500, "model": "gpt-4"},
            "translation": {"count": 50, "avg_tokens": 500, "model": "gpt-3.5-turbo"},
            "summarization": {"count": 30, "avg_tokens": 800, "model": "gpt-4"}
        }

        for task_type, stats in tasks.items():
            prompt_tokens = int(stats["avg_tokens"] * 0.4)
            completion_tokens = int(stats["avg_tokens"] * 0.6)

            cost_per_request = self.cost_tracker.calculate_cost(
                stats["model"],
                prompt_tokens,
                completion_tokens
            )

            total_task_cost = cost_per_request * stats["count"]

            task_costs[task_type] = {
                "count": stats["count"],
                "model": stats["model"],
                "cost_per_request": cost_per_request,
                "total_cost": total_task_cost
            }

            total_cost += total_task_cost

            # 統計模型使用
            if stats["model"] not in model_usage:
                model_usage[stats["model"]] = {"count": 0, "cost": 0}

            model_usage[stats["model"]]["count"] += stats["count"]
            model_usage[stats["model"]]["cost"] += total_task_cost

        # 顯示當前使用情況
        print(f"\n📈 當前使用情況:")
        print(f"{'任務類型':<20} {'次數':<10} {'模型':<20} {'總成本':<15}")
        print("-" * 70)

        for task_type, data in task_costs.items():
            print(f"{task_type:<20} {data['count']:<10} {data['model']:<20} ${data['total_cost']:<14.4f}")

        print("-" * 70)
        print(f"{'總計':<20} {sum(t['count'] for t in task_costs.values()):<10} {'':<20} ${total_cost:<14.4f}")

        # 優化建議
        print(f"\n💡 成本優化建議:")

        # 建議 1: 簡單任務使用更便宜的模型
        simple_tasks_on_expensive = [
            task for task, data in task_costs.items()
            if "simple" in task.lower() and data["model"] == "gpt-4"
        ]

        if simple_tasks_on_expensive:
            print(f"\n   1. 簡單任務降級:")
            for task in simple_tasks_on_expensive:
                current_cost = task_costs[task]["total_cost"]
                # 計算如果使用 gpt-3.5-turbo 的成本
                cheaper_cost = current_cost * 0.1  # 大約便宜 90%
                savings = current_cost - cheaper_cost

                print(f"      • {task}: 從 gpt-4 改用 gpt-3.5-turbo")
                print(f"        預估節省: ${savings:.4f} USD/週 ({(savings/current_cost)*100:.1f}%)")

        # 建議 2: 批量處理
        print(f"\n   2. 批量處理優化:")
        print(f"      • 將相似請求批量處理可減少重複的 prompt tokens")
        print(f"      • 預估節省: 10-15%")

        # 建議 3: 提示優化
        print(f"\n   3. 提示詞優化:")
        print(f"      • 精簡提示詞可減少 token 使用")
        print(f"      • 使用系統消息代替重複的上下文")
        print(f"      • 預估節省: 15-20%")

        # 建議 4: 緩存策略
        print(f"\n   4. 實施緩存策略:")
        print(f"      • 對常見問題使用緩存答案")
        print(f"      • 可減少約 30% 的重複調用")

        # 計算總潛在節省
        potential_savings = total_cost * 0.40  # 保守估計 40% 節省

        print(f"\n💰 潛在節省:")
        print(f"   當前週成本: ${total_cost:.4f} USD")
        print(f"   優化後預估: ${total_cost - potential_savings:.4f} USD")
        print(f"   預估節省: ${potential_savings:.4f} USD/週 ({(potential_savings/total_cost)*100:.1f}%)")
        print(f"   年度節省: ${potential_savings * 52:.2f} USD")

        print(f"\n✅ 優化分析完成")


# ============================================================================
# 第六部分：成本報告生成
# ============================================================================

class CostReporting:
    """
    成本報告生成

    生成詳細的成本報告。
    """

    def __init__(self, langfuse: Langfuse):
        self.langfuse = langfuse
        self.cost_tracker = CostTracking(langfuse)

    def generate_cost_report(self):
        """
        生成成本報告示例

        創建一個詳細的成本分析報告。
        """
        print("\n" + "="*60)
        print("成本報告生成示例")
        print("="*60)

        # 模擬一個月的數據
        print("📋 生成月度成本報告...\n")

        report_date = datetime.now()
        month_name = report_date.strftime("%Y年%m月")

        print("="*70)
        print(f"                  LLM API 成本報告")
        print(f"                     {month_name}")
        print("="*70)

        # 1. 總體統計
        total_requests = 1250
        total_cost = 125.50
        total_tokens = 3500000

        print(f"\n📊 總體統計:")
        print(f"   總請求數: {total_requests:,}")
        print(f"   總 Tokens: {total_tokens:,}")
        print(f"   總成本: ${total_cost:.2f} USD (約 NT${total_cost * 30:.2f})")
        print(f"   平均成本/請求: ${total_cost/total_requests:.4f} USD")

        # 2. 模型使用分布
        print(f"\n🤖 模型使用分布:")
        model_stats = {
            "gpt-3.5-turbo": {"requests": 900, "cost": 25.50, "percent": 72},
            "gpt-4": {"requests": 250, "cost": 85.00, "percent": 20},
            "gpt-4-turbo": {"requests": 100, "cost": 15.00, "percent": 8}
        }

        print(f"   {'模型':<20} {'請求數':<12} {'成本':<15} {'占比':<10}")
        print(f"   {'-'*60}")

        for model, stats in model_stats.items():
            print(f"   {model:<20} {stats['requests']:<12} ${stats['cost']:<14.2f} {stats['percent']:<9}%")

        # 3. 每日成本趨勢
        print(f"\n📈 每日成本趨勢 (最近 7 天):")
        daily_costs = [4.2, 3.8, 4.5, 5.1, 4.3, 3.9, 4.7]

        for i, cost in enumerate(daily_costs):
            day = (report_date - timedelta(days=6-i)).strftime("%m/%d")
            bar_length = int(cost * 5)
            bar = "█" * bar_length
            print(f"   {day}: {bar} ${cost:.2f}")

        # 4. 用戶成本排名
        print(f"\n👥 用戶成本排名 (Top 5):")
        top_users = [
            ("user-enterprise-01", 45.20),
            ("user-premium-05", 28.50),
            ("user-standard-12", 15.30),
            ("user-premium-03", 12.80),
            ("user-standard-08", 8.90)
        ]

        print(f"   {'用戶 ID':<20} {'成本':<15} {'占比':<10}")
        print(f"   {'-'*48}")

        for user_id, cost in top_users:
            percent = (cost / total_cost) * 100
            print(f"   {user_id:<20} ${cost:<14.2f} {percent:<9.1f}%")

        # 5. 成本趨勢分析
        print(f"\n📉 成本趨勢分析:")
        last_month_cost = 142.30
        cost_change = total_cost - last_month_cost
        percent_change = (cost_change / last_month_cost) * 100

        if cost_change < 0:
            trend = "下降"
            emoji = "✅"
        else:
            trend = "上升"
            emoji = "⚠️"

        print(f"   上月成本: ${last_month_cost:.2f} USD")
        print(f"   本月成本: ${total_cost:.2f} USD")
        print(f"   變化: {emoji} {trend} ${abs(cost_change):.2f} ({abs(percent_change):.1f}%)")

        # 6. 建議
        print(f"\n💡 成本優化建議:")
        print(f"   1. GPT-4 使用占總成本的 67.7%，考慮將部分任務遷移到 GPT-3.5-turbo")
        print(f"   2. 實施請求緩存可節省約 25-30% 的成本")
        print(f"   3. 優化提示詞長度可減少 15-20% 的 token 使用")

        print("\n" + "="*70)
        print(f"報告生成時間: {report_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)

        print(f"\n✅ 成本報告生成完成")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """
    主函數：運行所有成本追蹤示例
    """
    print("\n" + "="*70)
    print("Langfuse 成本追蹤示例")
    print("="*70)

    # 初始化 Langfuse
    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY", "pk-demo"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY", "sk-demo"),
        debug=True
    )

    try:
        # 1. 基本成本追蹤
        print("\n第一部分：基本成本追蹤")
        print("="*70)
        cost_tracking = CostTracking(langfuse)
        cost_tracking.basic_cost_tracking_example()
        cost_tracking.batch_cost_tracking()

        # 2. 模型成本對比
        print("\n第二部分：多模型成本對比")
        print("="*70)
        model_comparison = ModelCostComparison(langfuse)
        model_comparison.compare_models_example()

        # 3. 用戶級成本追蹤
        print("\n第三部分：用戶級成本追蹤")
        print("="*70)
        user_tracking = UserCostTracking(langfuse)
        user_tracking.track_user_costs_example()

        # 4. 預算警報系統
        print("\n第四部分：預算警報系統")
        print("="*70)
        budget_system = BudgetAlertSystem(langfuse)
        budget_system.budget_monitoring_example()

        # 5. 成本優化分析
        print("\n第五部分：成本優化分析")
        print("="*70)
        optimization = CostOptimization(langfuse)
        optimization.optimization_analysis_example()

        # 6. 成本報告生成
        print("\n第六部分：成本報告生成")
        print("="*70)
        reporting = CostReporting(langfuse)
        reporting.generate_cost_report()

        print("\n" + "="*70)
        print("✅ 所有成本追蹤示例運行完成！")
        print("="*70)

        print("\n💡 成本管理最佳實踐:")
        print("   1. 始終追蹤每次 API 調用的 token 使用和成本")
        print("   2. 設定合理的預算並實施警報機制")
        print("   3. 定期分析成本數據並優化模型選擇")
        print("   4. 根據任務複雜度選擇合適的模型")
        print("   5. 實施緩存和批處理策略降低成本")
        print("   6. 監控用戶級成本防止異常使用")

        # 刷新數據
        langfuse.flush()

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
