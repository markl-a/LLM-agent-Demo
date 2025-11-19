#!/usr/bin/env python3
"""
Semantic Kernel - 數據分析示例

本示例展示：
1. 數據統計分析
2. 趨勢分析
3. 數據可視化建議
4. 異常檢測
5. 數據解釋
"""

import asyncio
import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

try:
    import semantic_kernel as sk
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
except ImportError:
    print("❌ 請安裝 Semantic Kernel:")
    print("   pip install semantic-kernel")
    exit(1)


async def example_data_statistics():
    """示例 1: 數據統計分析"""
    print("\n" + "=" * 60)
    print("示例 1: 數據統計分析")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    stats_prompt = """
    分析以下數據並提供統計摘要：

    {{$data}}

    請提供：
    1. 基本統計信息（均值、中位數、範圍等）
    2. 數據特點
    3. 主要發現

    分析：
    """

    stats_function = kernel.add_function(
        function_name="analyze_stats",
        plugin_name="DataAnalysis",
        prompt=stats_prompt,
        description="統計分析",
    )

    # 測試數據
    datasets = [
        {
            "name": "月銷售額",
            "data": "January: $50,000, February: $55,000, March: $48,000, April: $62,000, May: $58,000, June: $65,000",
        },
        {
            "name": "網站訪問量",
            "data": "Mon: 1200, Tue: 1350, Wed: 1180, Thu: 1420, Fri: 1600, Sat: 900, Sun: 800",
        },
    ]

    for dataset in datasets:
        print(f"\n📊 數據集: {dataset['name']}")
        print(f"📈 數據: {dataset['data']}\n")

        result = await kernel.invoke(stats_function, data=dataset["data"])

        print(f"📝 分析結果:\n{result}\n")
        print("-" * 60)


async def example_trend_analysis():
    """示例 2: 趨勢分析"""
    print("\n" + "=" * 60)
    print("示例 2: 趨勢分析")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    trend_prompt = """
    分析以下時間序列數據的趨勢：

    {{$data}}

    請提供：
    1. 整體趨勢（上升/下降/穩定）
    2. 顯著變化點
    3. 未來預測
    4. 建議

    分析：
    """

    trend_function = kernel.add_function(
        function_name="analyze_trend",
        plugin_name="DataAnalysis",
        prompt=trend_prompt,
        description="趨勢分析",
    )

    # 時間序列數據
    time_series = [
        {
            "name": "用戶增長",
            "data": "Q1: 10,000 users, Q2: 15,000 users, Q3: 22,000 users, Q4: 35,000 users",
        },
        {
            "name": "客服工單",
            "data": "Week1: 150, Week2: 145, Week3: 160, Week4: 180, Week5: 200, Week6: 220",
        },
    ]

    for ts in time_series:
        print(f"\n📈 指標: {ts['name']}")
        print(f"📊 數據: {ts['data']}\n")

        result = await kernel.invoke(trend_function, data=ts["data"])

        print(f"📝 趨勢分析:\n{result}\n")
        print("-" * 60)


async def example_visualization_suggestions():
    """示例 3: 數據可視化建議"""
    print("\n" + "=" * 60)
    print("示例 3: 數據可視化建議")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    viz_prompt = """
    為以下數據推薦最佳的可視化方式：

    數據類型：{{$data_type}}
    數據描述：{{$description}}
    目標受眾：{{$audience}}

    請推薦：
    1. 最適合的圖表類型（如柱狀圖、折線圖、餅圖等）
    2. 推薦理由
    3. 關鍵要素（標題、標籤、顏色等）

    建議：
    """

    viz_function = kernel.add_function(
        function_name="suggest_visualization",
        plugin_name="DataViz",
        prompt=viz_prompt,
        description="可視化建議",
    )

    # 測試案例
    cases = [
        {
            "data_type": "時間序列",
            "description": "過去 12 個月的銷售額變化",
            "audience": "管理層",
        },
        {
            "data_type": "分類數據",
            "description": "不同產品類別的市場份額",
            "audience": "市場團隊",
        },
        {
            "data_type": "多變量",
            "description": "用戶年齡、收入和購買頻率的關係",
            "audience": "數據分析師",
        },
    ]

    for case in cases:
        print(f"\n📊 數據類型: {case['data_type']}")
        print(f"📝 描述: {case['description']}")
        print(f"👥 受眾: {case['audience']}\n")

        result = await kernel.invoke(
            viz_function,
            data_type=case["data_type"],
            description=case["description"],
            audience=case["audience"],
        )

        print(f"💡 可視化建議:\n{result}\n")
        print("-" * 60)


async def example_anomaly_detection():
    """示例 4: 異常檢測"""
    print("\n" + "=" * 60)
    print("示例 4: 異常檢測")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    anomaly_prompt = """
    檢測以下數據中的異常值：

    {{$data}}

    請識別：
    1. 異常數據點
    2. 異常原因推測
    3. 建議的處理方式

    分析：
    """

    anomaly_function = kernel.add_function(
        function_name="detect_anomalies",
        plugin_name="DataQuality",
        prompt=anomaly_prompt,
        description="異常檢測",
    )

    # 包含異常值的數據
    datasets = [
        {
            "name": "每日訂單量",
            "data": "Mon: 120, Tue: 115, Wed: 118, Thu: 5, Fri: 122, Sat: 95, Sun: 88",
        },
        {
            "name": "響應時間（毫秒）",
            "data": "10:00: 45ms, 11:00: 42ms, 12:00: 48ms, 13:00: 2500ms, 14:00: 44ms",
        },
    ]

    for dataset in datasets:
        print(f"\n🔍 數據: {dataset['name']}")
        print(f"📊 值: {dataset['data']}\n")

        result = await kernel.invoke(anomaly_function, data=dataset["data"])

        print(f"⚠️  異常檢測:\n{result}\n")
        print("-" * 60)


async def example_data_interpretation():
    """示例 5: 數據解釋"""
    print("\n" + "=" * 60)
    print("示例 5: 數據解釋")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    interpret_prompt = """
    用通俗易懂的語言解釋以下數據發現：

    {{$findings}}

    受眾：{{$audience}}

    請提供：
    1. 簡單的解釋
    2. 實際意義
    3. 可行動的建議

    解釋：
    """

    interpret_function = kernel.add_function(
        function_name="interpret_data",
        plugin_name="DataCommunication",
        prompt=interpret_prompt,
        description="數據解釋",
    )

    # 數據發現
    findings = [
        {
            "findings": "用戶流失率從上季度的 5% 增加到本季度的 8%",
            "audience": "非技術管理層",
        },
        {
            "findings": "A/B 測試結果顯示新設計的轉化率提高了 15%（p < 0.05）",
            "audience": "產品經理",
        },
    ]

    for finding in findings:
        print(f"\n📊 數據發現: {finding['findings']}")
        print(f"👥 受眾: {finding['audience']}\n")

        result = await kernel.invoke(
            interpret_function,
            findings=finding["findings"],
            audience=finding["audience"],
        )

        print(f"💬 解釋:\n{result}\n")
        print("-" * 60)


async def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🚀 Semantic Kernel - 數據分析示例")
    print("=" * 60)

    try:
        await example_data_statistics()
        await example_trend_analysis()
        await example_visualization_suggestions()
        await example_anomaly_detection()
        await example_data_interpretation()

    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ 所有示例運行完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
