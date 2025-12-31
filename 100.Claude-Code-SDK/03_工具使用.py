"""
Claude Code SDK 工具使用示例

本示例展示：
1. 工具定義
2. 工具調用處理
3. 多工具協作
4. 工具鏈執行
"""

import os
import json
from datetime import datetime
from anthropic import Anthropic
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from dotenv import load_dotenv

console = Console()
load_dotenv()


# 定義工具
TOOLS = [
    {
        "name": "get_weather",
        "description": "獲取指定城市的天氣信息",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名稱，例如：台北、東京"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "溫度單位",
                    "default": "celsius"
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "calculate",
        "description": "執行數學計算",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "數學表達式，例如：2 + 2，10 * 5"
                }
            },
            "required": ["expression"]
        }
    },
    {
        "name": "get_current_time",
        "description": "獲取當前時間",
        "input_schema": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "時區，例如：Asia/Taipei",
                    "default": "UTC"
                }
            }
        }
    },
    {
        "name": "search_database",
        "description": "搜索數據庫中的用戶信息",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "用戶 ID"
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "要返回的字段列表"
                }
            },
            "required": ["user_id"]
        }
    }
]


def get_weather(city, unit="celsius"):
    """模擬獲取天氣"""
    # 模擬數據
    weather_data = {
        "台北": {"temp": 25, "condition": "晴朗", "humidity": 65},
        "東京": {"temp": 18, "condition": "多雲", "humidity": 70},
        "紐約": {"temp": 15, "condition": "陰天", "humidity": 60},
    }

    data = weather_data.get(city, {"temp": 20, "condition": "未知", "humidity": 50})

    if unit == "fahrenheit":
        data["temp"] = data["temp"] * 9/5 + 32

    return {
        "city": city,
        "temperature": data["temp"],
        "unit": unit,
        "condition": data["condition"],
        "humidity": data["humidity"]
    }


def calculate(expression):
    """執行數學計算"""
    try:
        # 安全評估數學表達式
        result = eval(expression, {"__builtins__": {}}, {})
        return {"expression": expression, "result": result}
    except Exception as e:
        return {"error": str(e)}


def get_current_time(timezone="UTC"):
    """獲取當前時間"""
    now = datetime.now()
    return {
        "timezone": timezone,
        "datetime": now.isoformat(),
        "unix_timestamp": int(now.timestamp())
    }


def search_database(user_id, fields=None):
    """模擬數據庫搜索"""
    # 模擬用戶數據
    users = {
        "001": {"name": "張三", "email": "zhang@example.com", "age": 28, "role": "工程師"},
        "002": {"name": "李四", "email": "li@example.com", "age": 32, "role": "產品經理"},
    }

    user = users.get(user_id)
    if not user:
        return {"error": "用戶不存在"}

    if fields:
        return {k: v for k, v in user.items() if k in fields}

    return user


def process_tool_call(tool_name, tool_input):
    """處理工具調用"""
    console.print(f"\n[cyan]🔧 調用工具：{tool_name}[/cyan]")
    console.print(f"[dim]參數：{json.dumps(tool_input, ensure_ascii=False)}[/dim]")

    # 根據工具名稱調用相應函數
    if tool_name == "get_weather":
        result = get_weather(**tool_input)
    elif tool_name == "calculate":
        result = calculate(**tool_input)
    elif tool_name == "get_current_time":
        result = get_current_time(**tool_input)
    elif tool_name == "search_database":
        result = search_database(**tool_input)
    else:
        result = {"error": f"未知工具：{tool_name}"}

    console.print(f"[green]✓ 結果：{json.dumps(result, ensure_ascii=False)}[/green]\n")
    return result


def demo_single_tool():
    """單一工具使用示例"""
    console.print("\n[bold cyan]1. 單一工具調用[/bold cyan]\n")

    client = Anthropic()

    # 用戶查詢
    user_query = "台北今天的天氣怎麼樣？"
    console.print(f"[yellow]用戶查詢：[/yellow] {user_query}\n")

    # 第一次請求
    messages = [{"role": "user", "content": user_query}]

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        tools=TOOLS,
        messages=messages
    )

    console.print(f"[blue]Claude 響應類型：{response.stop_reason}[/blue]")

    # 如果 Claude 要求使用工具
    if response.stop_reason == "tool_use":
        # 處理工具調用
        tool_use = next(block for block in response.content if block.type == "tool_use")

        tool_result = process_tool_call(tool_use.name, tool_use.input)

        # 將結果返回給 Claude
        messages.append({"role": "assistant", "content": response.content})
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(tool_result, ensure_ascii=False)
                }
            ]
        })

        # 獲取最終響應
        final_response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            tools=TOOLS,
            messages=messages
        )

        final_text = final_response.content[0].text
        console.print(Panel(final_text, title="最終回答", border_style="green"))


def demo_multiple_tools():
    """多工具協作示例"""
    console.print("\n[bold cyan]2. 多工具協作[/bold cyan]\n")

    client = Anthropic()

    user_query = "現在幾點？台北的天氣如何？幫我計算 123 * 456。"
    console.print(f"[yellow]用戶查詢：[/yellow] {user_query}\n")

    messages = [{"role": "user", "content": user_query}]

    # 最多執行 5 輪工具調用
    for iteration in range(5):
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            tools=TOOLS,
            messages=messages
        )

        console.print(f"[blue]迭代 {iteration + 1}：{response.stop_reason}[/blue]")

        if response.stop_reason == "tool_use":
            # 處理所有工具調用
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = process_tool_call(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result, ensure_ascii=False)
                    })

            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            # 獲取最終文本響應
            final_text = next(
                (block.text for block in response.content if hasattr(block, "text")),
                None
            )
            if final_text:
                console.print(Panel(final_text, title="最終回答", border_style="green"))
            break


def demo_tool_chain():
    """工具鏈執行示例"""
    console.print("\n[bold cyan]3. 工具鏈執行[/bold cyan]\n")

    client = Anthropic()

    user_query = "查詢用戶 001 的信息，然後告訴我他的郵箱"
    console.print(f"[yellow]用戶查詢：[/yellow] {user_query}\n")

    messages = [{"role": "user", "content": user_query}]

    # 執行工具鏈
    step = 1
    while step <= 3:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            tools=TOOLS,
            messages=messages
        )

        console.print(f"[blue]步驟 {step}：{response.stop_reason}[/blue]")

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = process_tool_call(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result, ensure_ascii=False)
                    })

            messages.append({"role": "user", "content": tool_results})

        else:
            # 顯示最終結果
            for block in response.content:
                if hasattr(block, "text"):
                    console.print(Panel(block.text, title="最終結果", border_style="green"))
            break

        step += 1


def demo_tool_error_handling():
    """工具錯誤處理示例"""
    console.print("\n[bold cyan]4. 工具錯誤處理[/bold cyan]\n")

    client = Anthropic()

    # 故意使用會出錯的查詢
    user_query = "計算 10 除以 0"
    console.print(f"[yellow]用戶查詢：[/yellow] {user_query}\n")

    messages = [{"role": "user", "content": user_query}]

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        tools=TOOLS,
        messages=messages
    )

    if response.stop_reason == "tool_use":
        tool_use = next(block for block in response.content if block.type == "tool_use")

        # 處理工具調用（會產生錯誤）
        tool_result = process_tool_call(tool_use.name, tool_use.input)

        # 將錯誤結果返回給 Claude
        messages.append({"role": "assistant", "content": response.content})
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(tool_result, ensure_ascii=False),
                    "is_error": "error" in tool_result
                }
            ]
        })

        # 獲取 Claude 對錯誤的處理
        final_response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            tools=TOOLS,
            messages=messages
        )

        console.print(Panel(
            final_response.content[0].text,
            title="錯誤處理回答",
            border_style="yellow"
        ))


def show_tool_schema():
    """顯示工具定義"""
    console.print("\n[bold cyan]工具定義示例[/bold cyan]\n")

    for tool in TOOLS:
        schema = Syntax(
            json.dumps(tool, indent=2, ensure_ascii=False),
            "json",
            theme="monokai"
        )
        console.print(Panel(schema, title=f"工具：{tool['name']}", border_style="cyan"))


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Claude Code SDK 工具使用[/bold cyan]\n"
        "[dim]學習如何定義和使用工具擴展 Claude 的能力[/dim]",
        border_style="cyan"
    ))

    # 顯示工具定義
    show_tool_schema()

    # 1. 單一工具
    demo_single_tool()

    # 2. 多工具協作
    demo_multiple_tools()

    # 3. 工具鏈
    demo_tool_chain()

    # 4. 錯誤處理
    demo_tool_error_handling()

    # 完成
    console.print("\n" + "="*60)
    console.print("[bold green]✓ 工具使用示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點：[/cyan]")
    console.print("  • 明確定義工具的功能和參數")
    console.print("  • 實現完善的工具執行邏輯")
    console.print("  • 處理工具調用的錯誤情況")
    console.print("  • 支持多工具協作完成複雜任務")


if __name__ == "__main__":
    main()
