"""
Pydantic AI - 工具定義範例

本範例展示：
1. 使用 @agent.tool 裝飾器
2. 工具參數和返回值
3. 工具描述最佳實踐
4. 多工具協作
5. 工具錯誤處理

工具是 Agent 與外部世界交互的主要方式
"""

import asyncio
import json
from typing import Annotated, Literal
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from dataclasses import dataclass


# ============================================================================
# 範例 1: 最簡單的工具
# ============================================================================

def example_1_simple_tool():
    """定義和使用最簡單的工具"""
    print("\n" + "="*60)
    print("範例 1: 最簡單的工具")
    print("="*60)

    agent = Agent('openai:gpt-4')

    # 使用 @agent.tool 裝飾器定義工具
    @agent.tool
    def get_current_time() -> str:
        """獲取當前時間"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Agent 會自動決定是否調用工具
    result = agent.run_sync('現在幾點了？')
    print(f"AI 回應：{result.data}")


# ============================================================================
# 範例 2: 帶參數的工具
# ============================================================================

def example_2_tool_with_parameters():
    """工具可以接收參數"""
    print("\n" + "="*60)
    print("範例 2: 帶參數的工具")
    print("="*60)

    agent = Agent('openai:gpt-4')

    @agent.tool
    def calculate_bmi(
        weight_kg: Annotated[float, Field(gt=0, description="體重（公斤）")],
        height_m: Annotated[float, Field(gt=0, description="身高（公尺）")]
    ) -> dict:
        """
        計算 BMI（身體質量指數）

        Args:
            weight_kg: 體重，單位公斤
            height_m: 身高，單位公尺

        Returns:
            包含 BMI 值和健康建議的字典
        """
        bmi = weight_kg / (height_m ** 2)

        if bmi < 18.5:
            category = "體重過輕"
        elif bmi < 24:
            category = "正常體重"
        elif bmi < 27:
            category = "體重過重"
        else:
            category = "肥胖"

        return {
            "bmi": round(bmi, 2),
            "category": category,
            "weight": weight_kg,
            "height": height_m
        }

    result = agent.run_sync('我 70 公斤，身高 1.75 公尺，我的 BMI 是多少？')
    print(f"AI 回應：{result.data}")


# ============================================================================
# 範例 3: 多個工具協作
# ============================================================================

def example_3_multiple_tools():
    """Agent 可以使用多個工具"""
    print("\n" + "="*60)
    print("範例 3: 多個工具協作")
    print("="*60)

    agent = Agent('openai:gpt-4')

    @agent.tool
    def search_products(
        keyword: str,
        category: Literal["electronics", "books", "clothing", "all"] = "all"
    ) -> list[dict]:
        """搜索產品"""
        # 模擬數據庫查詢
        products = {
            "electronics": [
                {"name": "iPhone 15", "price": 33900},
                {"name": "MacBook Pro", "price": 59900},
            ],
            "books": [
                {"name": "Python 編程", "price": 580},
                {"name": "AI 入門", "price": 680},
            ],
            "clothing": [
                {"name": "T-shirt", "price": 390},
                {"name": "Jeans", "price": 1290},
            ]
        }

        if category == "all":
            result = []
            for items in products.values():
                result.extend(items)
            return result

        return products.get(category, [])

    @agent.tool
    def get_product_details(product_name: str) -> dict:
        """獲取產品詳細信息"""
        # 模擬產品詳情
        details = {
            "iPhone 15": {
                "name": "iPhone 15",
                "price": 33900,
                "stock": 50,
                "rating": 4.5,
                "description": "最新款 iPhone"
            },
            "MacBook Pro": {
                "name": "MacBook Pro",
                "price": 59900,
                "stock": 20,
                "rating": 4.8,
                "description": "專業筆記型電腦"
            }
        }
        return details.get(product_name, {"error": "產品不存在"})

    @agent.tool
    def calculate_discount(price: float, discount_percent: float) -> dict:
        """計算折扣後價格"""
        discount_amount = price * (discount_percent / 100)
        final_price = price - discount_amount

        return {
            "original_price": price,
            "discount_percent": discount_percent,
            "discount_amount": round(discount_amount, 2),
            "final_price": round(final_price, 2)
        }

    # Agent 會根據需要調用多個工具
    result = agent.run_sync(
        '幫我找找電子產品，然後告訴我 iPhone 15 打 9 折是多少錢'
    )
    print(f"AI 回應：{result.data}")


# ============================================================================
# 範例 4: 使用 RunContext 訪問依賴
# ============================================================================

@dataclass
class ShopContext:
    """商店上下文"""
    shop_name: str
    user_id: int
    is_vip: bool


def example_4_tool_with_context():
    """工具可以通過 RunContext 訪問依賴"""
    print("\n" + "="*60)
    print("範例 4: 工具使用上下文")
    print("="*60)

    agent: Agent[ShopContext, str] = Agent(
        'openai:gpt-4',
        deps_type=ShopContext,
    )

    @agent.tool
    def get_user_discount(ctx: RunContext[ShopContext]) -> dict:
        """獲取用戶折扣"""
        # 通過 ctx.deps 訪問依賴
        shop = ctx.deps.shop_name
        user_id = ctx.deps.user_id
        is_vip = ctx.deps.is_vip

        discount = 20 if is_vip else 10

        return {
            "shop": shop,
            "user_id": user_id,
            "is_vip": is_vip,
            "discount_percent": discount,
            "message": f"{'VIP' if is_vip else '普通'}會員享 {discount}% 折扣"
        }

    # 創建上下文
    context = ShopContext(
        shop_name="科技商城",
        user_id=12345,
        is_vip=True
    )

    result = agent.run_sync(
        '我可以享有什麼折扣？',
        deps=context
    )
    print(f"AI 回應：{result.data}")


# ============================================================================
# 範例 5: 異步工具
# ============================================================================

async def example_5_async_tools():
    """工具可以是異步函數"""
    print("\n" + "="*60)
    print("範例 5: 異步工具")
    print("="*60)

    agent = Agent('openai:gpt-4')

    @agent.tool
    async def fetch_weather(city: str) -> dict:
        """獲取天氣信息（模擬 API 調用）"""
        # 模擬異步 API 調用
        await asyncio.sleep(0.5)

        # 假數據
        weather_data = {
            "台北": {"temp": 28, "condition": "晴天"},
            "台中": {"temp": 30, "condition": "多雲"},
            "高雄": {"temp": 32, "condition": "晴天"},
        }

        data = weather_data.get(city, {"temp": 25, "condition": "未知"})
        return {
            "city": city,
            "temperature": data["temp"],
            "condition": data["condition"],
            "timestamp": datetime.now().isoformat()
        }

    @agent.tool
    async def fetch_air_quality(city: str) -> dict:
        """獲取空氣品質（模擬 API 調用）"""
        await asyncio.sleep(0.3)

        return {
            "city": city,
            "aqi": 45,
            "level": "良好",
            "main_pollutant": "PM2.5"
        }

    result = await agent.run(
        '台北現在的天氣和空氣品質如何？'
    )
    print(f"AI 回應：{result.data}")


# ============================================================================
# 範例 6: 工具錯誤處理
# ============================================================================

class ToolError(Exception):
    """工具錯誤"""
    pass


def example_6_tool_error_handling():
    """處理工具執行錯誤"""
    print("\n" + "="*60)
    print("範例 6: 工具錯誤處理")
    print("="*60)

    agent = Agent('openai:gpt-4')

    @agent.tool
    def divide_numbers(a: float, b: float) -> dict:
        """除法運算"""
        if b == 0:
            raise ToolError("除數不能為零")

        result = a / b
        return {
            "a": a,
            "b": b,
            "result": round(result, 4),
            "operation": f"{a} ÷ {b} = {result:.4f}"
        }

    @agent.tool
    def validate_email(email: str) -> dict:
        """驗證 email 格式"""
        if "@" not in email or "." not in email:
            raise ToolError(f"無效的 email 格式：{email}")

        return {
            "email": email,
            "valid": True,
            "domain": email.split("@")[1]
        }

    # Agent 會處理工具錯誤並給出合理的回應
    result1 = agent.run_sync('計算 10 除以 2')
    print(f"正常計算：{result1.data}\n")

    # 工具會拋出錯誤，Agent 會適當處理
    result2 = agent.run_sync('計算 10 除以 0')
    print(f"錯誤處理：{result2.data}")


# ============================================================================
# 範例 7: 複雜的工具返回類型
# ============================================================================

class SearchResult(BaseModel):
    """搜索結果"""
    title: str
    url: str
    snippet: str
    relevance_score: float


async def example_7_complex_return_types():
    """工具可以返回複雜的 Pydantic 模型"""
    print("\n" + "="*60)
    print("範例 7: 複雜返回類型")
    print("="*60)

    agent = Agent('openai:gpt-4')

    @agent.tool
    def search_web(query: str, max_results: int = 3) -> list[dict]:
        """
        網頁搜索

        Returns:
            搜索結果列表
        """
        # 模擬搜索結果
        results = [
            {
                "title": f"結果 {i+1}: {query}",
                "url": f"https://example.com/result{i+1}",
                "snippet": f"關於 {query} 的信息...",
                "relevance_score": 0.9 - (i * 0.1)
            }
            for i in range(max_results)
        ]

        return results

    result = await agent.run('搜索 Pydantic AI 教學')
    print(f"AI 回應：{result.data}")


# ============================================================================
# 範例 8: 工具文檔最佳實踐
# ============================================================================

def example_8_tool_documentation():
    """良好的工具文檔幫助 AI 更好地使用工具"""
    print("\n" + "="*60)
    print("範例 8: 工具文檔最佳實踐")
    print("="*60)

    agent = Agent('openai:gpt-4')

    @agent.tool
    def book_flight(
        departure: Annotated[str, Field(description="出發城市，例如：台北")],
        destination: Annotated[str, Field(description="目的地城市，例如：東京")],
        date: Annotated[str, Field(description="出發日期，格式 YYYY-MM-DD")],
        passengers: Annotated[int, Field(gt=0, le=9, description="乘客人數，1-9 人")],
        class_type: Annotated[
            Literal["economy", "business", "first"],
            Field(description="艙等：economy(經濟艙), business(商務艙), first(頭等艙)")
        ] = "economy"
    ) -> dict:
        """
        預訂機票

        這個工具用於搜索和預訂航班。

        參數說明：
        - departure: 出發城市名稱
        - destination: 目的地城市名稱
        - date: 出發日期（ISO 格式）
        - passengers: 乘客總數
        - class_type: 艙等選擇

        返回值包含航班信息和價格。

        範例：
        - book_flight("台北", "東京", "2024-12-25", 2, "economy")
        """
        # 模擬預訂
        price_map = {"economy": 8000, "business": 25000, "first": 50000}
        base_price = price_map[class_type]
        total_price = base_price * passengers

        return {
            "booking_id": "FL-2024-001",
            "departure": departure,
            "destination": destination,
            "date": date,
            "passengers": passengers,
            "class": class_type,
            "price_per_person": base_price,
            "total_price": total_price,
            "currency": "TWD",
            "status": "confirmed"
        }

    result = agent.run_sync(
        '我想預訂 12 月 25 日從台北到東京的商務艙機票，2 個人'
    )
    print(f"AI 回應：{result.data}")


# ============================================================================
# 範例 9: 條件工具（根據上下文決定可用性）
# ============================================================================

@dataclass
class UserContext:
    """用戶上下文"""
    user_id: int
    is_admin: bool
    subscription_level: Literal["free", "pro", "enterprise"]


async def example_9_conditional_tools():
    """根據用戶權限提供不同的工具"""
    print("\n" + "="*60)
    print("範例 9: 條件工具")
    print("="*60)

    agent: Agent[UserContext, str] = Agent(
        'openai:gpt-4',
        deps_type=UserContext,
    )

    @agent.tool
    def basic_analysis(ctx: RunContext[UserContext], data: str) -> dict:
        """基礎分析（所有用戶）"""
        return {
            "type": "basic",
            "result": f"基礎分析結果：{len(data)} 個字符",
            "available_to": "all users"
        }

    @agent.tool
    def advanced_analysis(ctx: RunContext[UserContext], data: str) -> dict:
        """進階分析（Pro 用戶以上）"""
        if ctx.deps.subscription_level == "free":
            raise ToolError("此功能需要 Pro 訂閱")

        return {
            "type": "advanced",
            "result": f"進階分析：{data}",
            "sentiment": "positive",
            "keywords": ["AI", "Python"],
            "available_to": "pro+ users"
        }

    @agent.tool
    def admin_operation(ctx: RunContext[UserContext]) -> dict:
        """管理員操作"""
        if not ctx.deps.is_admin:
            raise ToolError("需要管理員權限")

        return {
            "type": "admin",
            "result": "管理員操作成功",
            "available_to": "admin only"
        }

    # Pro 用戶
    pro_context = UserContext(
        user_id=1,
        is_admin=False,
        subscription_level="pro"
    )

    result = await agent.run(
        '幫我進行進階分析',
        deps=pro_context
    )
    print(f"Pro 用戶：{result.data}")


# ============================================================================
# 主程式
# ============================================================================

async def main():
    """運行所有範例"""
    print("\n" + "🔧 " + "="*58)
    print("Pydantic AI - 工具定義範例")
    print("="*60)

    example_1_simple_tool()
    example_2_tool_with_parameters()
    example_3_multiple_tools()
    example_4_tool_with_context()
    await example_5_async_tools()
    example_6_tool_error_handling()
    await example_7_complex_return_types()
    example_8_tool_documentation()
    await example_9_conditional_tools()

    print("\n" + "="*60)
    print("✓ 工具定義範例完成！")
    print("💡 工具設計技巧：")
    print("   1. 清晰的命名和文檔")
    print("   2. 適當的參數驗證")
    print("   3. 合理的錯誤處理")
    print("   4. 一個工具做好一件事")
    print("="*60)


if __name__ == '__main__':
    import os
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  請設置 OPENAI_API_KEY 環境變量")
    else:
        asyncio.run(main())
