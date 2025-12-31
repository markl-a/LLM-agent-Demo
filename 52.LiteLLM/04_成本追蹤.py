"""
LiteLLM 成本追蹤範例

這個檔案展示如何使用 LiteLLM 進行成本追蹤和管理：
1. 即時成本計算
2. 成本追蹤和記錄
3. 預算控制和告警
4. 成本分析和報告
5. 不同模型的成本比較
6. 使用者級別的成本追蹤
7. 成本優化建議
8. 成本預測
9. 多租戶成本管理
10. 成本資料匯出和視覺化

成本管理對於生產環境的 LLM 應用至關重要。
"""

import os
from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import sqlite3
from litellm import completion, cost_per_token, token_counter
import time
from collections import defaultdict


# ============================================================================
# 資料類別定義
# ============================================================================

@dataclass
class CostRecord:
    """成本記錄類別"""
    timestamp: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    prompt_cost: float
    completion_cost: float
    total_cost: float
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Budget:
    """預算類別"""
    name: str
    limit: float  # 美元
    spent: float = 0.0
    period: str = "monthly"  # daily, weekly, monthly
    start_date: Optional[str] = None
    alert_threshold: float = 0.8  # 80% 時告警


# ============================================================================
# 第一部分：基本成本計算
# ============================================================================

def calculate_basic_cost():
    """
    基本的成本計算範例

    展示如何計算單次 API 呼叫的成本。
    """
    print("=" * 80)
    print("基本成本計算")
    print("=" * 80)

    models = [
        "gpt-4o",
        "gpt-3.5-turbo",
        "claude-3-5-sonnet-20241022",
        "claude-3-haiku-20240307"
    ]

    prompt = "請解釋什麼是機器學習"

    print("\n比較不同模型的成本：\n")

    for model in models:
        try:
            # 呼叫模型
            response = completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )

            # 取得 token 使用量
            usage = response.usage
            prompt_tokens = usage.prompt_tokens
            completion_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens

            # 計算成本
            cost = cost_per_token(
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens
            )

            print(f"模型：{model}")
            print("-" * 40)
            print(f"  Prompt tokens：{prompt_tokens}")
            print(f"  Completion tokens：{completion_tokens}")
            print(f"  總計 tokens：{total_tokens}")
            print(f"  成本：${cost:.6f}")
            print(f"  每 1K tokens 平均成本：${(cost / total_tokens * 1000):.6f}")
            print()

        except Exception as e:
            print(f"模型 {model} 錯誤：{e}\n")


def token_estimation():
    """
    Token 數量預估

    在實際呼叫 API 之前，可以預估 token 數量和成本。
    """
    print("=" * 80)
    print("Token 數量預估")
    print("=" * 80)

    # 測試文本
    texts = [
        "你好",
        "這是一段較長的文字，用來測試 token 計數功能。",
        "In English, this is a test to see how tokens are counted.",
        """這是一段很長的文字，包含多個句子。
        第一句話介紹主題。
        第二句話提供細節。
        第三句話總結要點。"""
    ]

    models = ["gpt-4o", "claude-3-5-sonnet-20241022"]

    for model in models:
        print(f"\n模型：{model}")
        print("-" * 40)

        for i, text in enumerate(texts, 1):
            try:
                # 計算 token 數量
                tokens = token_counter(model=model, text=text)

                # 預估成本（假設輸入和輸出各佔一半）
                estimated_cost = cost_per_token(
                    model=model,
                    prompt_tokens=tokens,
                    completion_tokens=tokens
                )

                print(f"\n文本 {i}：{text[:50]}...")
                print(f"  Tokens：{tokens}")
                print(f"  預估成本：${estimated_cost:.6f}")

            except Exception as e:
                print(f"  錯誤：{e}")


# ============================================================================
# 第二部分：成本追蹤系統
# ============================================================================

class CostTracker:
    """成本追蹤器"""

    def __init__(self, db_path: str = "cost_tracking.db"):
        """
        初始化成本追蹤器

        Args:
            db_path: SQLite 資料庫路徑
        """
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """初始化資料庫"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 建立成本記錄表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cost_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                model TEXT NOT NULL,
                prompt_tokens INTEGER NOT NULL,
                completion_tokens INTEGER NOT NULL,
                total_tokens INTEGER NOT NULL,
                prompt_cost REAL NOT NULL,
                completion_cost REAL NOT NULL,
                total_cost REAL NOT NULL,
                user_id TEXT,
                request_id TEXT,
                metadata TEXT
            )
        """)

        # 建立索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON cost_records(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_model
            ON cost_records(model)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_id
            ON cost_records(user_id)
        """)

        conn.commit()
        conn.close()

    def track_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Tuple[Any, CostRecord]:
        """
        追蹤一次完成呼叫的成本

        Args:
            model: 模型名稱
            messages: 訊息列表
            user_id: 使用者 ID
            metadata: 額外的元資料
            **kwargs: 傳遞給 completion 的其他參數

        Returns:
            (回應物件, 成本記錄)
        """
        # 呼叫 LLM
        response = completion(model=model, messages=messages, **kwargs)

        # 取得使用量
        usage = response.usage
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        total_tokens = usage.total_tokens

        # 計算成本
        total_cost = cost_per_token(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens
        )

        # 計算各部分成本（近似）
        prompt_cost = cost_per_token(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=0
        )
        completion_cost = total_cost - prompt_cost

        # 建立成本記錄
        record = CostRecord(
            timestamp=datetime.now().isoformat(),
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            prompt_cost=prompt_cost,
            completion_cost=completion_cost,
            total_cost=total_cost,
            user_id=user_id,
            request_id=response.id,
            metadata=metadata
        )

        # 儲存記錄
        self.save_record(record)

        return response, record

    def save_record(self, record: CostRecord):
        """儲存成本記錄到資料庫"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO cost_records (
                timestamp, model, prompt_tokens, completion_tokens,
                total_tokens, prompt_cost, completion_cost, total_cost,
                user_id, request_id, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.timestamp,
            record.model,
            record.prompt_tokens,
            record.completion_tokens,
            record.total_tokens,
            record.prompt_cost,
            record.completion_cost,
            record.total_cost,
            record.user_id,
            record.request_id,
            json.dumps(record.metadata) if record.metadata else None
        ))

        conn.commit()
        conn.close()

    def get_total_cost(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        user_id: Optional[str] = None,
        model: Optional[str] = None
    ) -> float:
        """
        取得總成本

        Args:
            start_date: 開始日期（ISO 格式）
            end_date: 結束日期（ISO 格式）
            user_id: 使用者 ID
            model: 模型名稱

        Returns:
            總成本（美元）
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT SUM(total_cost) FROM cost_records WHERE 1=1"
        params = []

        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        if model:
            query += " AND model = ?"
            params.append(model)

        cursor.execute(query, params)
        result = cursor.fetchone()[0]
        conn.close()

        return result if result else 0.0

    def get_cost_by_model(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, float]:
        """按模型統計成本"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT model, SUM(total_cost)
            FROM cost_records
            WHERE 1=1
        """
        params = []

        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)

        query += " GROUP BY model ORDER BY SUM(total_cost) DESC"

        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        return {model: cost for model, cost in results}

    def get_cost_by_user(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, float]:
        """按使用者統計成本"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT user_id, SUM(total_cost)
            FROM cost_records
            WHERE user_id IS NOT NULL
        """
        params = []

        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)

        query += " GROUP BY user_id ORDER BY SUM(total_cost) DESC"

        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        return {user_id: cost for user_id, cost in results}

    def generate_report(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成成本報告"""
        total_cost = self.get_total_cost(start_date, end_date)
        cost_by_model = self.get_cost_by_model(start_date, end_date)
        cost_by_user = self.get_cost_by_user(start_date, end_date)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 取得請求數量
        query = "SELECT COUNT(*) FROM cost_records WHERE 1=1"
        params = []
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)

        cursor.execute(query, params)
        total_requests = cursor.fetchone()[0]

        # 取得總 tokens
        query = "SELECT SUM(total_tokens) FROM cost_records WHERE 1=1"
        params = []
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)

        cursor.execute(query, params)
        total_tokens = cursor.fetchone()[0] or 0

        conn.close()

        return {
            "period": {
                "start": start_date,
                "end": end_date
            },
            "summary": {
                "total_cost": total_cost,
                "total_requests": total_requests,
                "total_tokens": total_tokens,
                "average_cost_per_request": total_cost / total_requests if total_requests > 0 else 0
            },
            "by_model": cost_by_model,
            "by_user": cost_by_user
        }


def cost_tracking_example():
    """成本追蹤範例"""
    print("\n" + "=" * 80)
    print("成本追蹤範例")
    print("=" * 80)

    # 建立追蹤器
    tracker = CostTracker("example_costs.db")

    # 模擬一些請求
    print("\n模擬請求...")

    test_data = [
        {
            "model": "gpt-4o",
            "user": "user_1",
            "prompt": "什麼是 Python？"
        },
        {
            "model": "gpt-3.5-turbo",
            "user": "user_1",
            "prompt": "解釋變數的概念"
        },
        {
            "model": "gpt-4o",
            "user": "user_2",
            "prompt": "寫一個排序演算法"
        },
        {
            "model": "claude-3-haiku-20240307",
            "user": "user_2",
            "prompt": "什麼是函數？"
        }
    ]

    for i, data in enumerate(test_data, 1):
        print(f"\n請求 {i}/{len(test_data)}：{data['prompt']}")

        try:
            response, record = tracker.track_completion(
                model=data["model"],
                messages=[{"role": "user", "content": data["prompt"]}],
                user_id=data["user"],
                metadata={"request_type": "example"},
                max_tokens=100
            )

            print(f"  模型：{record.model}")
            print(f"  使用者：{record.user_id}")
            print(f"  Tokens：{record.total_tokens}")
            print(f"  成本：${record.total_cost:.6f}")

        except Exception as e:
            print(f"  錯誤：{e}")

    # 生成報告
    print("\n" + "=" * 80)
    print("成本報告")
    print("=" * 80)

    report = tracker.generate_report()

    print(f"\n總覽：")
    print(f"  總成本：${report['summary']['total_cost']:.6f}")
    print(f"  總請求數：{report['summary']['total_requests']}")
    print(f"  總 Tokens：{report['summary']['total_tokens']}")
    print(f"  平均每次請求成本：${report['summary']['average_cost_per_request']:.6f}")

    print(f"\n按模型統計：")
    for model, cost in report['by_model'].items():
        print(f"  {model}: ${cost:.6f}")

    print(f"\n按使用者統計：")
    for user, cost in report['by_user'].items():
        print(f"  {user}: ${cost:.6f}")


# ============================================================================
# 第三部分：預算管理
# ============================================================================

class BudgetManager:
    """預算管理器"""

    def __init__(self, db_path: str = "budgets.db"):
        self.db_path = db_path
        self.budgets: Dict[str, Budget] = {}
        self._init_database()

    def _init_database(self):
        """初始化資料庫"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                name TEXT PRIMARY KEY,
                limit_amount REAL NOT NULL,
                spent REAL DEFAULT 0.0,
                period TEXT NOT NULL,
                start_date TEXT,
                alert_threshold REAL DEFAULT 0.8
            )
        """)

        conn.commit()
        conn.close()

    def create_budget(
        self,
        name: str,
        limit: float,
        period: str = "monthly",
        alert_threshold: float = 0.8
    ) -> Budget:
        """建立預算"""
        budget = Budget(
            name=name,
            limit=limit,
            period=period,
            start_date=datetime.now().isoformat(),
            alert_threshold=alert_threshold
        )

        self.budgets[name] = budget
        self._save_budget(budget)

        return budget

    def _save_budget(self, budget: Budget):
        """儲存預算到資料庫"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO budgets
            (name, limit_amount, spent, period, start_date, alert_threshold)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            budget.name,
            budget.limit,
            budget.spent,
            budget.period,
            budget.start_date,
            budget.alert_threshold
        ))

        conn.commit()
        conn.close()

    def add_expense(self, budget_name: str, amount: float) -> Dict[str, Any]:
        """
        新增支出到預算

        Returns:
            包含狀態和告警資訊的字典
        """
        if budget_name not in self.budgets:
            return {"error": "預算不存在"}

        budget = self.budgets[budget_name]
        budget.spent += amount
        self._save_budget(budget)

        # 檢查是否超過告警閾值
        usage_percentage = budget.spent / budget.limit
        alert = None

        if usage_percentage >= 1.0:
            alert = {
                "level": "critical",
                "message": f"預算已超支！已使用 ${budget.spent:.2f} / ${budget.limit:.2f}"
            }
        elif usage_percentage >= budget.alert_threshold:
            alert = {
                "level": "warning",
                "message": f"預算即將用完！已使用 {usage_percentage * 100:.1f}%"
            }

        return {
            "budget_name": budget_name,
            "spent": budget.spent,
            "limit": budget.limit,
            "remaining": budget.limit - budget.spent,
            "usage_percentage": usage_percentage,
            "alert": alert
        }

    def check_budget(self, budget_name: str, amount: float) -> bool:
        """檢查預算是否足夠"""
        if budget_name not in self.budgets:
            return True  # 如果預算不存在，不限制

        budget = self.budgets[budget_name]
        return (budget.spent + amount) <= budget.limit

    def get_budget_status(self, budget_name: str) -> Dict[str, Any]:
        """取得預算狀態"""
        if budget_name not in self.budgets:
            return {"error": "預算不存在"}

        budget = self.budgets[budget_name]
        usage_percentage = budget.spent / budget.limit

        return {
            "name": budget.name,
            "limit": budget.limit,
            "spent": budget.spent,
            "remaining": budget.limit - budget.spent,
            "usage_percentage": usage_percentage,
            "period": budget.period,
            "start_date": budget.start_date
        }


def budget_management_example():
    """預算管理範例"""
    print("\n" + "=" * 80)
    print("預算管理範例")
    print("=" * 80)

    manager = BudgetManager("example_budgets.db")

    # 建立預算
    print("\n建立預算...")

    budgets = [
        {"name": "開發團隊", "limit": 100.0, "period": "monthly"},
        {"name": "測試環境", "limit": 20.0, "period": "weekly"},
        {"name": "生產環境", "limit": 1000.0, "period": "monthly"}
    ]

    for budget_data in budgets:
        budget = manager.create_budget(**budget_data)
        print(f"✓ {budget.name}：${budget.limit}/{budget.period}")

    # 模擬支出
    print("\n模擬支出...")

    expenses = [
        {"budget": "開發團隊", "amount": 30.0, "desc": "GPT-4 API 呼叫"},
        {"budget": "開發團隊", "amount": 25.0, "desc": "Claude API 呼叫"},
        {"budget": "測試環境", "amount": 15.0, "desc": "測試用 API 呼叫"},
        {"budget": "開發團隊", "amount": 50.0, "desc": "大量資料處理"}
    ]

    for expense in expenses:
        print(f"\n支出：{expense['desc']} - ${expense['amount']}")

        result = manager.add_expense(expense["budget"], expense["amount"])

        print(f"  預算：{result['budget_name']}")
        print(f"  已使用：${result['spent']:.2f} / ${result['limit']:.2f}")
        print(f"  剩餘：${result['remaining']:.2f}")
        print(f"  使用率：{result['usage_percentage'] * 100:.1f}%")

        if result.get("alert"):
            alert = result["alert"]
            print(f"  ⚠️  告警（{alert['level']}）：{alert['message']}")

    # 顯示所有預算狀態
    print("\n" + "=" * 80)
    print("預算狀態總覽")
    print("=" * 80)

    for budget_name in manager.budgets.keys():
        status = manager.get_budget_status(budget_name)
        print(f"\n{status['name']}：")
        print(f"  限額：${status['limit']:.2f}")
        print(f"  已用：${status['spent']:.2f}")
        print(f"  剩餘：${status['remaining']:.2f}")
        print(f"  使用率：{status['usage_percentage'] * 100:.1f}%")


# ============================================================================
# 第四部分：成本優化建議
# ============================================================================

class CostOptimizer:
    """成本優化器"""

    def __init__(self, cost_tracker: CostTracker):
        self.cost_tracker = cost_tracker

    def analyze_usage_patterns(self) -> Dict[str, Any]:
        """分析使用模式"""
        print("\n分析使用模式...")

        # 取得所有記錄
        conn = sqlite3.connect(self.cost_tracker.db_path)
        cursor = conn.cursor()

        # 按模型分析平均 token 使用量
        cursor.execute("""
            SELECT
                model,
                AVG(prompt_tokens) as avg_prompt,
                AVG(completion_tokens) as avg_completion,
                AVG(total_cost) as avg_cost,
                COUNT(*) as request_count
            FROM cost_records
            GROUP BY model
        """)

        model_stats = {}
        for row in cursor.fetchall():
            model, avg_prompt, avg_completion, avg_cost, count = row
            model_stats[model] = {
                "avg_prompt_tokens": avg_prompt,
                "avg_completion_tokens": avg_completion,
                "avg_cost": avg_cost,
                "request_count": count
            }

        conn.close()

        return model_stats

    def suggest_model_alternatives(self, current_model: str) -> List[Dict[str, Any]]:
        """建議替代模型"""
        # 模型映射：從高成本到低成本
        alternatives_map = {
            "gpt-4o": [
                {"model": "gpt-3.5-turbo", "savings": "~90%", "tradeoff": "品質稍降"},
                {"model": "claude-3-haiku-20240307", "savings": "~95%", "tradeoff": "適合簡單任務"}
            ],
            "claude-3-5-sonnet-20241022": [
                {"model": "claude-3-haiku-20240307", "savings": "~90%", "tradeoff": "速度更快，品質稍降"},
                {"model": "gpt-3.5-turbo", "savings": "~85%", "tradeoff": "不同的模型特性"}
            ],
            "gpt-3.5-turbo": [
                {"model": "claude-3-haiku-20240307", "savings": "~50%", "tradeoff": "不同的模型特性"}
            ]
        }

        return alternatives_map.get(current_model, [])

    def generate_optimization_report(self) -> Dict[str, Any]:
        """生成優化報告"""
        usage_patterns = self.analyze_usage_patterns()

        recommendations = []

        for model, stats in usage_patterns.items():
            # 如果平均成本較高且請求數多，建議優化
            if stats["avg_cost"] > 0.01 and stats["request_count"] > 10:
                alternatives = self.suggest_model_alternatives(model)

                if alternatives:
                    # 計算潛在節省
                    total_cost = stats["avg_cost"] * stats["request_count"]
                    potential_savings = total_cost * 0.8  # 假設可節省 80%

                    recommendations.append({
                        "current_model": model,
                        "current_cost": total_cost,
                        "request_count": stats["request_count"],
                        "alternatives": alternatives,
                        "potential_savings": potential_savings
                    })

        return {
            "usage_patterns": usage_patterns,
            "recommendations": recommendations
        }


def cost_optimization_example():
    """成本優化範例"""
    print("\n" + "=" * 80)
    print("成本優化範例")
    print("=" * 80)

    # 使用之前建立的追蹤器
    tracker = CostTracker("example_costs.db")
    optimizer = CostOptimizer(tracker)

    # 生成優化報告
    report = optimizer.generate_optimization_report()

    print("\n使用模式分析：")
    print("-" * 40)
    for model, stats in report["usage_patterns"].items():
        print(f"\n{model}：")
        print(f"  平均 prompt tokens：{stats['avg_prompt_tokens']:.1f}")
        print(f"  平均 completion tokens：{stats['avg_completion_tokens']:.1f}")
        print(f"  平均成本：${stats['avg_cost']:.6f}")
        print(f"  請求次數：{stats['request_count']}")

    if report["recommendations"]:
        print("\n" + "=" * 80)
        print("優化建議")
        print("=" * 80)

        for i, rec in enumerate(report["recommendations"], 1):
            print(f"\n建議 {i}：")
            print(f"  當前模型：{rec['current_model']}")
            print(f"  當前總成本：${rec['current_cost']:.6f}")
            print(f"  請求次數：{rec['request_count']}")
            print(f"\n  替代方案：")

            for alt in rec["alternatives"]:
                print(f"    • {alt['model']}")
                print(f"      - 可節省約：{alt['savings']}")
                print(f"      - 權衡：{alt['tradeoff']}")

            print(f"\n  預估可節省：${rec['potential_savings']:.6f}")
    else:
        print("\n✓ 目前使用模式已經很優化了！")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """主程式"""
    print("\n")
    print("=" * 80)
    print("LiteLLM 成本追蹤與管理完整教學")
    print("=" * 80)
    print()

    # 基本成本計算
    # calculate_basic_cost()
    # token_estimation()

    # 成本追蹤
    # cost_tracking_example()

    # 預算管理
    budget_management_example()

    # 成本優化
    # cost_optimization_example()

    print("\n" + "=" * 80)
    print("教學完成！")
    print("=" * 80)
    print("\n重點回顧：")
    print("1. 使用 cost_per_token() 計算成本")
    print("2. CostTracker 類別追蹤所有請求的成本")
    print("3. BudgetManager 類別管理預算和告警")
    print("4. CostOptimizer 類別提供優化建議")
    print("5. 定期分析成本報告，持續優化支出")
    print()


if __name__ == "__main__":
    main()
