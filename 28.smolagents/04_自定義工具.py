"""
自定義工具開發指南
================

smolagents 讓創建自定義工具變得極其簡單！
只需要一個 @tool 裝飾器。

本範例展示：
1. 基本工具創建
2. 帶參數的工具
3. 工具最佳實踐
4. 錯誤處理
5. 異步工具
6. 工具組合
"""

from smolagents import CodeAgent, HfApiModel, tool
from typing import List, Dict, Optional
import requests
import json
import time
from datetime import datetime


# ============================================================================
# 範例 1: 最簡單的工具
# ============================================================================

@tool
def hello_world() -> str:
    """
    最簡單的工具示例

    Returns:
        問候語
    """
    return "Hello from smolagents!"


def example_1_simplest_tool():
    """創建最簡單的工具"""
    print("\n" + "="*70)
    print("範例 1: 最簡單的工具")
    print("="*70)

    print("\n創建工具只需要：")
    print("1. 定義函數")
    print("2. 添加 @tool 裝飾器")
    print("3. 寫清楚 docstring\n")

    model = HfApiModel()
    agent = CodeAgent(tools=[hello_world], model=model, max_steps=3)

    result = agent.run("使用 hello_world 工具")
    print(f"\n結果: {result}")


# ============================================================================
# 範例 2: 帶參數的工具
# ============================================================================

@tool
def calculate_bmi(weight: float, height: float) -> dict:
    """
    計算 BMI（身體質量指數）

    Args:
        weight: 體重（公斤）
        height: 身高（公尺）

    Returns:
        包含 BMI 值和健康狀態的字典
    """
    bmi = weight / (height ** 2)

    if bmi < 18.5:
        status = "過輕"
    elif bmi < 24:
        status = "正常"
    elif bmi < 27:
        status = "過重"
    else:
        status = "肥胖"

    return {
        "bmi": round(bmi, 2),
        "status": status,
        "weight": weight,
        "height": height
    }


def example_2_tool_with_parameters():
    """帶參數的工具"""
    print("\n" + "="*70)
    print("範例 2: 帶參數的工具")
    print("="*70)

    print("\n工具可以接收參數，LLM 會自動提供正確的值\n")

    model = HfApiModel()
    agent = CodeAgent(tools=[calculate_bmi], model=model, max_steps=3)

    result = agent.run("計算體重 70 公斤、身高 1.75 公尺的人的 BMI")
    print(f"\n結果: {result}")


# ============================================================================
# 範例 3: 複雜工具 - API 調用
# ============================================================================

@tool
def get_exchange_rate(from_currency: str, to_currency: str) -> dict:
    """
    獲取匯率（使用公開 API）

    Args:
        from_currency: 源貨幣代碼（如 'USD'）
        to_currency: 目標貨幣代碼（如 'TWD'）

    Returns:
        包含匯率信息的字典
    """
    # 模擬匯率數據（實際應用中應該調用真實 API）
    rates = {
        ("USD", "TWD"): 31.5,
        ("USD", "EUR"): 0.92,
        ("EUR", "TWD"): 34.2,
        ("TWD", "USD"): 0.032,
    }

    rate = rates.get((from_currency, to_currency), 1.0)

    return {
        "from": from_currency,
        "to": to_currency,
        "rate": rate,
        "timestamp": datetime.now().isoformat()
    }


@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """
    轉換貨幣

    Args:
        amount: 金額
        from_currency: 源貨幣
        to_currency: 目標貨幣

    Returns:
        轉換結果
    """
    rate_info = get_exchange_rate(from_currency, to_currency)
    converted = amount * rate_info["rate"]

    return {
        "original_amount": amount,
        "from_currency": from_currency,
        "converted_amount": round(converted, 2),
        "to_currency": to_currency,
        "rate": rate_info["rate"]
    }


def example_3_api_tool():
    """調用 API 的工具"""
    print("\n" + "="*70)
    print("範例 3: API 調用工具")
    print("="*70)

    model = HfApiModel()
    agent = CodeAgent(
        tools=[get_exchange_rate, convert_currency],
        model=model,
        max_steps=5
    )

    result = agent.run("轉換 100 美元為台幣")
    print(f"\n結果: {result}")


# ============================================================================
# 範例 4: 錯誤處理
# ============================================================================

@tool
def safe_divide(a: float, b: float) -> dict:
    """
    安全的除法運算（帶錯誤處理）

    Args:
        a: 被除數
        b: 除數

    Returns:
        計算結果或錯誤信息
    """
    try:
        if b == 0:
            return {
                "success": False,
                "error": "除數不能為零",
                "result": None
            }

        result = a / b
        return {
            "success": True,
            "error": None,
            "result": round(result, 4)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "result": None
        }


def example_4_error_handling():
    """工具中的錯誤處理"""
    print("\n" + "="*70)
    print("範例 4: 錯誤處理")
    print("="*70)

    print("\n良好的工具應該：")
    print("1. 處理預期的錯誤")
    print("2. 返回清晰的錯誤信息")
    print("3. 不要讓異常中斷 Agent\n")

    model = HfApiModel()
    agent = CodeAgent(tools=[safe_divide], model=model, max_steps=5)

    # 測試正常情況
    result1 = agent.run("計算 10 除以 2")
    print(f"\n正常情況: {result1}")

    # 測試錯誤情況
    result2 = agent.run("計算 10 除以 0")
    print(f"\n錯誤處理: {result2}")


# ============================================================================
# 範例 5: 有狀態的工具
# ============================================================================

class DataStore:
    """簡單的數據存儲（演示有狀態工具）"""

    def __init__(self):
        self.data = {}

    @tool
    def store_data(self, key: str, value: str) -> str:
        """
        存儲數據

        Args:
            key: 鍵名
            value: 值

        Returns:
            確認消息
        """
        self.data[key] = value
        return f"已存儲: {key} = {value}"

    @tool
    def get_data(self, key: str) -> str:
        """
        獲取數據

        Args:
            key: 鍵名

        Returns:
            存儲的值或錯誤消息
        """
        value = self.data.get(key)
        if value is None:
            return f"找不到鍵: {key}"
        return f"{key} = {value}"

    @tool
    def list_all_data(self) -> dict:
        """
        列出所有數據

        Returns:
            所有存儲的數據
        """
        return self.data.copy()


def example_5_stateful_tools():
    """有狀態的工具"""
    print("\n" + "="*70)
    print("範例 5: 有狀態的工具")
    print("="*70)

    print("\n工具可以維護狀態（使用類方法）\n")

    store = DataStore()
    model = HfApiModel()

    agent = CodeAgent(
        tools=[store.store_data, store.get_data, store.list_all_data],
        model=model,
        max_steps=8
    )

    result = agent.run(
        "存儲三個數據：name='Alice', age='30', city='Taipei'，"
        "然後列出所有數據"
    )

    print(f"\n結果: {result}")


# ============================================================================
# 範例 6: 工具組合和鏈接
# ============================================================================

@tool
def fetch_user_data(user_id: int) -> dict:
    """
    獲取用戶數據

    Args:
        user_id: 用戶 ID

    Returns:
        用戶信息
    """
    users = {
        1: {"name": "Alice", "email": "alice@example.com", "credits": 100},
        2: {"name": "Bob", "email": "bob@example.com", "credits": 50},
        3: {"name": "Charlie", "email": "charlie@example.com", "credits": 200},
    }
    return users.get(user_id, {"error": "用戶不存在"})


@tool
def send_email(email: str, subject: str, body: str) -> bool:
    """
    發送郵件（模擬）

    Args:
        email: 收件人郵箱
        subject: 郵件主題
        body: 郵件內容

    Returns:
        是否成功發送
    """
    print(f"\n📧 發送郵件:")
    print(f"   收件人: {email}")
    print(f"   主題: {subject}")
    print(f"   內容: {body}\n")
    return True


@tool
def update_credits(user_id: int, amount: int) -> dict:
    """
    更新用戶積分（模擬）

    Args:
        user_id: 用戶 ID
        amount: 積分變化量

    Returns:
        更新結果
    """
    print(f"更新用戶 {user_id} 的積分: {amount:+d}")
    return {"user_id": user_id, "new_credits": amount}


def example_6_tool_composition():
    """工具組合使用"""
    print("\n" + "="*70)
    print("範例 6: 工具組合和鏈接")
    print("="*70)

    print("\nCode Agent 可以自動組合多個工具完成複雜任務\n")

    model = HfApiModel()
    agent = CodeAgent(
        tools=[fetch_user_data, send_email, update_credits],
        model=model,
        max_steps=10
    )

    result = agent.run(
        "獲取用戶 1 的信息，給他發送一封積分獎勵郵件，"
        "然後增加他 50 積分"
    )

    print(f"\n結果: {result}")


# ============================================================================
# 範例 7: 工具最佳實踐
# ============================================================================

def example_7_best_practices():
    """工具開發最佳實踐"""
    print("\n" + "="*70)
    print("範例 7: 工具開發最佳實踐")
    print("="*70)

    print("\n1. 清晰的文檔字符串")
    print("   - 描述工具的功能")
    print("   - 說明每個參數")
    print("   - 說明返回值")

    print("\n2. 類型註解")
    print("   - 幫助 LLM 理解參數類型")
    print("   - 提供自動檢查")

    print("\n3. 錯誤處理")
    print("   - 捕獲預期的異常")
    print("   - 返回有用的錯誤信息")

    print("\n4. 單一職責")
    print("   - 每個工具做一件事")
    print("   - 讓工具可組合")

    print("\n5. 冪等性")
    print("   - 相同輸入產生相同輸出")
    print("   - 避免不必要的副作用")

    print("\n6. 返回結構化數據")
    print("   - 使用字典而不是字符串")
    print("   - 方便後續處理")

    print("\n示例：良好的工具設計\n")

    @tool
    def process_order(
        order_id: str,
        action: str,
        reason: Optional[str] = None
    ) -> dict:
        """
        處理訂單（展示最佳實踐）

        Args:
            order_id: 訂單 ID
            action: 操作類型（'confirm', 'cancel', 'refund'）
            reason: 操作原因（可選）

        Returns:
            處理結果，包含狀態和消息

        Examples:
            >>> process_order("ORD-123", "confirm")
            {"success": True, "order_id": "ORD-123", ...}
        """
        # 參數驗證
        valid_actions = ["confirm", "cancel", "refund"]
        if action not in valid_actions:
            return {
                "success": False,
                "error": f"無效的操作: {action}",
                "valid_actions": valid_actions
            }

        # 執行操作（模擬）
        try:
            # 實際的業務邏輯...
            return {
                "success": True,
                "order_id": order_id,
                "action": action,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "order_id": order_id
            }

    print(process_order.__doc__)


# ============================================================================
# 主程式
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*70)
    print("自定義工具開發指南")
    print("="*70)

    examples = [
        ("範例 1: 最簡單的工具", example_1_simplest_tool),
        ("範例 2: 帶參數的工具", example_2_tool_with_parameters),
        ("範例 3: API 調用工具", example_3_api_tool),
        ("範例 4: 錯誤處理", example_4_error_handling),
        ("範例 5: 有狀態的工具", example_5_stateful_tools),
        ("範例 6: 工具組合", example_6_tool_composition),
        ("範例 7: 最佳實踐", example_7_best_practices),
    ]

    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n{name} 執行失敗: {e}")

    print("\n" + "="*70)
    print("自定義工具開發完成！")
    print("="*70)

    print("\n關鍵要點：")
    print("  - 使用 @tool 裝飾器")
    print("  - 寫清楚 docstring 和類型註解")
    print("  - 單一職責、可組合")
    print("  - 良好的錯誤處理")
    print("  - 返回結構化數據")

    print("\n下一步: 查看 05_多模態Agent.py 學習處理圖像和音頻")


if __name__ == "__main__":
    main()
