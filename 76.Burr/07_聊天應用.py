"""
Burr 聊天應用 - 構建對話系統

這個示例展示如何：
1. 使用 Burr 構建聊天機器人
2. 管理對話歷史
3. 實現多輪對話
4. 集成 LLM

Burr 的狀態機非常適合構建複雜的對話流程。
"""

from burr.core import action, State, ApplicationBuilder, expr
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from typing import List, Dict
from datetime import datetime
import os
from dotenv import load_dotenv

# 嘗試導入 OpenAI（如果可用）
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

console = Console()
load_dotenv()


# ============================================================================
# 示例 1：簡單聊天流程
# ============================================================================

@action(reads=[], writes=["conversation_history", "current_topic"])
def start_conversation(state: State) -> State:
    """開始對話"""
    history = [{
        "role": "assistant",
        "content": "你好！我是 AI 助手。有什麼我可以幫助你的嗎？",
        "timestamp": datetime.now().isoformat()
    }]

    return state.update(
        conversation_history=history,
        current_topic=None
    )


@action(reads=["conversation_history"], writes=["conversation_history", "current_topic"])
def process_user_message(state: State, user_message: str) -> State:
    """處理用戶消息"""
    history = state["conversation_history"]

    # 添加用戶消息
    history.append({
        "role": "user",
        "content": user_message,
        "timestamp": datetime.now().isoformat()
    })

    # 簡單的主題檢測
    if "天氣" in user_message:
        topic = "weather"
    elif "時間" in user_message:
        topic = "time"
    elif any(word in user_message for word in ["謝謝", "感謝", "再見"]):
        topic = "goodbye"
    else:
        topic = "general"

    return state.update(
        conversation_history=history,
        current_topic=topic
    )


@action(reads=["current_topic", "conversation_history"], writes=["conversation_history"])
def generate_response(state: State) -> State:
    """生成回應"""
    topic = state["current_topic"]
    history = state["conversation_history"]

    # 根據主題生成回應
    responses = {
        "weather": "抱歉，我無法獲取實時天氣信息。你可以查看天氣應用獲取最新信息。",
        "time": f"現在的時間是 {datetime.now().strftime('%H:%M:%S')}",
        "goodbye": "很高興能幫到你！再見！",
        "general": "我明白了。還有其他我可以幫助你的嗎？"
    }

    response = responses.get(topic, "我不太明白，能再說一次嗎？")

    # 添加助手回應
    history.append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.now().isoformat()
    })

    return state.update(conversation_history=history)


def simple_chat_example():
    """示例 1：簡單聊天流程"""
    console.print(Panel("[bold cyan]示例 1：簡單聊天流程[/bold cyan]"))

    # 構建聊天應用
    app = (
        ApplicationBuilder()
        .with_actions(
            start_conversation,
            process_user_message,
            generate_response
        )
        .with_transitions(
            ("start_conversation", "process_user_message"),
            ("process_user_message", "generate_response"),
            ("generate_response", "process_user_message",
             expr("current_topic != 'goodbye'")),
        )
        .with_entrypoint("start_conversation")
        .build()
    )

    # 開始對話
    console.print("\n[yellow]對話開始[/yellow]\n")
    action_result, state, _ = app.step()

    # 顯示歡迎消息
    history = state["conversation_history"]
    console.print(f"[green]助手：[/green]{history[-1]['content']}\n")

    # 模擬用戶輸入
    user_messages = [
        "今天天氣怎麼樣？",
        "現在幾點了？",
        "謝謝你的幫助！"
    ]

    for msg in user_messages:
        console.print(f"[cyan]用戶：[/cyan]{msg}")

        # 處理用戶消息
        app = (
            ApplicationBuilder()
            .with_state(**dict(state._state))
            .with_actions(
                process_user_message.bind(user_message=msg),
                generate_response
            )
            .with_transitions(
                ("process_user_message", "generate_response"),
                ("generate_response", "process_user_message",
                 expr("current_topic != 'goodbye'")),
            )
            .build()
        )

        # 處理並生成回應
        action_result, state, _ = app.step()  # process_user_message
        action_result, state, _ = app.step()  # generate_response

        history = state["conversation_history"]
        console.print(f"[green]助手：[/green]{history[-1]['content']}\n")

        # 如果是再見，結束對話
        if state["current_topic"] == "goodbye":
            console.print("[yellow]對話結束[/yellow]")
            break


# ============================================================================
# 示例 2：帶 LLM 的聊天
# ============================================================================

@action(reads=["conversation_history"], writes=["conversation_history"])
def llm_generate_response(state: State) -> State:
    """使用 LLM 生成回應"""
    history = state["conversation_history"]

    if not OPENAI_AVAILABLE:
        # 降級到簡單回應
        response = "（LLM 不可用）這是一個模擬回應。"
    else:
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            # 準備消息
            messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in history
            ]

            # 調用 LLM
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )

            response = completion.choices[0].message.content

        except Exception as e:
            response = f"（錯誤：{e}）抱歉，我現在無法回應。"

    # 添加回應
    history.append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.now().isoformat()
    })

    return state.update(conversation_history=history)


def llm_chat_example():
    """示例 2：帶 LLM 的聊天"""
    console.print(Panel("[bold cyan]示例 2：帶 LLM 的聊天[/bold cyan]"))

    if not OPENAI_AVAILABLE:
        console.print("[yellow]注意：OpenAI 未安裝，使用模擬回應[/yellow]\n")
    elif not os.getenv("OPENAI_API_KEY"):
        console.print("[yellow]注意：未設置 OPENAI_API_KEY，使用模擬回應[/yellow]\n")

    # 初始化對話
    history = [{
        "role": "system",
        "content": "你是一個友好的 AI 助手，用中文回答問題。",
        "timestamp": datetime.now().isoformat()
    }]

    console.print("[yellow]使用 LLM 的聊天機器人[/yellow]\n")

    test_message = "請用一句話介紹什麼是機器學習"

    console.print(f"[cyan]用戶：[/cyan]{test_message}")

    # 添加用戶消息
    history.append({
        "role": "user",
        "content": test_message,
        "timestamp": datetime.now().isoformat()
    })

    # 構建應用
    app = (
        ApplicationBuilder()
        .with_state(conversation_history=history)
        .with_actions(llm_generate_response)
        .with_entrypoint("llm_generate_response")
        .build()
    )

    # 生成回應
    action_result, state, _ = app.step()

    response = state["conversation_history"][-1]["content"]
    console.print(f"[green]助手：[/green]{response}\n")


# ============================================================================
# 示例 3：多輪對話管理
# ============================================================================

@action(reads=["conversation_history"], writes=["conversation_summary", "turn_count"])
def summarize_conversation(state: State) -> State:
    """總結對話"""
    history = state["conversation_history"]

    # 統計對話輪次
    user_messages = [msg for msg in history if msg["role"] == "user"]
    assistant_messages = [msg for msg in history if msg["role"] == "assistant"]

    summary = {
        "total_turns": len(user_messages),
        "total_messages": len(history),
        "user_messages": len(user_messages),
        "assistant_messages": len(assistant_messages),
        "duration": "N/A"  # 可以計算時間跨度
    }

    return state.update(
        conversation_summary=summary,
        turn_count=len(user_messages)
    )


def multi_turn_example():
    """示例 3：多輪對話管理"""
    console.print(Panel("[bold cyan]示例 3：多輪對話管理[/bold cyan]"))

    # 模擬一個完整的對話歷史
    conversation_history = [
        {"role": "assistant", "content": "你好！", "timestamp": datetime.now().isoformat()},
        {"role": "user", "content": "你好，請問你是誰？", "timestamp": datetime.now().isoformat()},
        {"role": "assistant", "content": "我是 AI 助手。", "timestamp": datetime.now().isoformat()},
        {"role": "user", "content": "你能幫我做什麼？", "timestamp": datetime.now().isoformat()},
        {"role": "assistant", "content": "我可以回答問題、提供建議等。", "timestamp": datetime.now().isoformat()},
        {"role": "user", "content": "太好了，謝謝！", "timestamp": datetime.now().isoformat()},
        {"role": "assistant", "content": "不客氣！", "timestamp": datetime.now().isoformat()},
    ]

    # 構建應用
    app = (
        ApplicationBuilder()
        .with_state(conversation_history=conversation_history)
        .with_actions(summarize_conversation)
        .with_entrypoint("summarize_conversation")
        .build()
    )

    console.print("\n[yellow]對話歷史：[/yellow]")
    for msg in conversation_history:
        role = "助手" if msg["role"] == "assistant" else "用戶"
        console.print(f"  [{role}] {msg['content']}")

    # 生成總結
    action_result, state, _ = app.step()
    summary = state["conversation_summary"]

    console.print("\n[green]對話統計：[/green]")
    console.print(f"  總輪次: {summary['total_turns']}")
    console.print(f"  總消息數: {summary['total_messages']}")
    console.print(f"  用戶消息: {summary['user_messages']}")
    console.print(f"  助手消息: {summary['assistant_messages']}")


# ============================================================================
# 示例 4：對話狀態管理
# ============================================================================

def conversation_state_example():
    """示例 4：對話狀態管理"""
    console.print(Panel("[bold cyan]示例 4：對話狀態管理[/bold cyan]"))

    console.print("""
[yellow]對話狀態管理策略：[/yellow]

1. [cyan]短期記憶[/cyan]（對話歷史）
   - 保存最近 N 輪對話
   - 用於上下文理解
   - 控制 token 使用

2. [cyan]長期記憶[/cyan]（用戶資料）
   - 用戶偏好設置
   - 歷史交互記錄
   - 個性化信息

3. [cyan]會話狀態[/cyan]
   - 當前對話主題
   - 待完成的任務
   - 上下文變量

4. [cyan]元數據[/cyan]
   - 時間戳
   - 情感分析
   - 意圖識別

[yellow]示例狀態結構：[/yellow]
    """)

    state_structure = '''
{
    "conversation_history": [
        {"role": "user", "content": "...", "timestamp": "..."},
        {"role": "assistant", "content": "...", "timestamp": "..."}
    ],
    "user_profile": {
        "name": "張三",
        "preferences": ["技術", "AI"],
        "language": "zh-CN"
    },
    "session_state": {
        "current_topic": "機器學習",
        "pending_tasks": ["查詢資料"],
        "context": {"last_query": "..."}
    },
    "metadata": {
        "session_id": "abc123",
        "start_time": "2024-01-01T10:00:00",
        "turn_count": 5
    }
}
    '''

    console.print(Panel(state_structure, border_style="blue", title="狀態結構"))


# ============================================================================
# 主函數
# ============================================================================

def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]Burr 聊天應用 - 構建對話系統[/bold green]",
        border_style="green"
    ))

    console.print("\n[bold]聊天應用核心概念：[/bold]")
    console.print("1. [cyan]對話歷史[/cyan]: 管理消息列表")
    console.print("2. [cyan]狀態追蹤[/cyan]: 追蹤對話狀態")
    console.print("3. [cyan]LLM 集成[/cyan]: 集成語言模型")
    console.print("4. [cyan]多輪管理[/cyan]: 處理複雜對話\n")

    # 運行示例
    simple_chat_example()
    console.print("\n" + "="*60 + "\n")

    llm_chat_example()
    console.print("\n" + "="*60 + "\n")

    multi_turn_example()
    console.print("\n" + "="*60 + "\n")

    conversation_state_example()

    # 總結
    console.print(Panel("""
[bold green]聊天應用完成！[/bold green]

關鍵要點：
1. 使用狀態機管理對話流程
2. 保存完整的對話歷史
3. 支持 LLM 集成
4. 實現上下文管理
5. 可以持久化對話狀態

Burr 在聊天應用的優勢：
- 清晰的對話流程
- 易於實現複雜對話邏輯
- 支持狀態持久化
- 完整的追蹤和調試

聊天應用模式：
- 簡單問答: 單輪對話
- 任務導向: 多輪對話完成任務
- 開放式聊天: 自由對話
- 混合模式: 結合多種模式

最佳實踐：
- 限制對話歷史長度
- 實現對話總結功能
- 處理異常輸入
- 添加安全檢查
- 優雅處理錯誤

下一步：
- 查看 08_Agent循環.py 了解 Agent 系統
- 查看 10_生產部署.py 部署聊天應用
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()
