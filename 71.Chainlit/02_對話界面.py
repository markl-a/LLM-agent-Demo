"""
Chainlit 對話界面示例

本示例展示：
1. 聊天界面配置
2. 對話歷史管理
3. 用戶會話處理
4. 不同類型的消息
5. 對話上下文維護

運行方式：
    chainlit run 02_對話界面.py -w
"""

import chainlit as cl
from datetime import datetime
from typing import List, Dict
import json


# ==================== 會話初始化 ====================

@cl.on_chat_start
async def on_chat_start():
    """
    初始化聊天會話
    設置對話歷史、用戶配置等
    """
    try:
        # 初始化對話歷史列表
        cl.user_session.set("conversation_history", [])

        # 初始化用戶配置
        cl.user_session.set("user_config", {
            "name": "訪客",
            "language": "zh-TW",
            "theme": "light"
        })

        # 初始化統計信息
        cl.user_session.set("stats", {
            "total_messages": 0,
            "user_messages": 0,
            "bot_messages": 0,
            "start_time": datetime.now().isoformat()
        })

        # 發送歡迎消息
        welcome = await cl.Message(
            content="""
# 🎯 歡迎來到 Chainlit 對話界面示例！

這個示例展示了如何管理完整的對話界面。

## ✨ 主要功能

- 📝 **對話歷史管理** - 自動記錄和管理對話
- 💬 **多種消息類型** - 支持文本、Markdown、代碼等
- 👤 **用戶會話** - 為每個用戶維護獨立會話
- 📊 **統計信息** - 追蹤對話統計數據
- 🔄 **上下文感知** - 基於歷史對話進行回應

## 🚀 試試這些命令

- `/help` - 顯示幫助信息
- `/history` - 查看對話歷史
- `/stats` - 查看統計信息
- `/clear` - 清除對話歷史
- `/config` - 查看/設置配置

**開始聊天吧！** 👇
            """,
            author="系統"
        ).send()

        # 添加到對話歷史
        add_to_history("system", welcome.content)

        print("✅ 對話會話已初始化")

    except Exception as e:
        error_msg = f"❌ 初始化失敗: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()


# ==================== 消息處理 ====================

@cl.on_message
async def on_message(message: cl.Message):
    """
    處理用戶消息
    維護對話歷史，提供上下文感知的回應
    """
    try:
        # 獲取用戶消息
        user_message = message.content.strip()

        # 添加用戶消息到歷史
        add_to_history("user", user_message)

        # 更新統計
        update_stats("user")

        # 處理命令
        if user_message.startswith("/"):
            response = await handle_command(user_message)
        else:
            response = await handle_conversation(user_message)

        # 發送響應
        bot_msg = await cl.Message(
            content=response,
            author="AI 助手"
        ).send()

        # 添加機器人回應到歷史
        add_to_history("assistant", bot_msg.content)

        # 更新統計
        update_stats("bot")

    except Exception as e:
        error_msg = f"❌ 處理消息時出錯: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()


# ==================== 命令處理 ====================

async def handle_command(command: str) -> str:
    """
    處理用戶命令

    Args:
        command: 用戶輸入的命令

    Returns:
        命令執行結果
    """
    cmd = command.lower().split()[0]

    command_handlers = {
        "/help": show_help,
        "/history": show_history,
        "/stats": show_stats,
        "/clear": clear_history,
        "/config": show_config,
        "/export": export_conversation,
    }

    handler = command_handlers.get(cmd)
    if handler:
        return await handler()
    else:
        return f"""
❌ **未知命令**: {cmd}

輸入 `/help` 查看可用命令列表。
        """


async def show_help() -> str:
    """顯示幫助信息"""
    return """
# 📚 幫助信息

## 可用命令

### 📝 對話管理
- `/history` - 查看完整對話歷史
- `/clear` - 清除當前對話歷史
- `/export` - 導出對話記錄

### 📊 信息查詢
- `/stats` - 查看對話統計信息
- `/config` - 查看當前配置

### ❓ 其他
- `/help` - 顯示此幫助信息

## 💡 使用提示

1. **Markdown 支持**: 你可以使用 Markdown 格式化文本
2. **代碼塊**: 使用 \\`\\`\\` 包裹代碼
3. **上下文**: 我會記住我們的對話內容

試試發送一些普通消息，我會基於對話歷史回應你！
    """


async def show_history() -> str:
    """顯示對話歷史"""
    try:
        history = cl.user_session.get("conversation_history", [])

        if not history:
            return "📭 **對話歷史為空**\n\n還沒有任何對話記錄。"

        # 格式化歷史記錄
        formatted_history = ["# 📜 對話歷史\n"]

        for i, entry in enumerate(history, 1):
            role = entry["role"]
            content = entry["content"]
            timestamp = entry.get("timestamp", "未知時間")

            # 角色圖標
            icon = {
                "user": "👤",
                "assistant": "🤖",
                "system": "⚙️"
            }.get(role, "💬")

            # 截斷過長的內容
            display_content = content[:100] + "..." if len(content) > 100 else content

            formatted_history.append(
                f"{i}. {icon} **{role.upper()}** ({timestamp})\n   {display_content}\n"
            )

        formatted_history.append(f"\n📊 **總計**: {len(history)} 條記錄")

        return "\n".join(formatted_history)

    except Exception as e:
        return f"❌ 獲取歷史失敗: {str(e)}"


async def show_stats() -> str:
    """顯示統計信息"""
    try:
        stats = cl.user_session.get("stats", {})
        history = cl.user_session.get("conversation_history", [])

        start_time = datetime.fromisoformat(stats.get("start_time", datetime.now().isoformat()))
        duration = (datetime.now() - start_time).total_seconds()

        minutes = int(duration // 60)
        seconds = int(duration % 60)

        return f"""
# 📊 對話統計

## 消息統計
- 👤 **用戶消息**: {stats.get('user_messages', 0)} 條
- 🤖 **助手回應**: {stats.get('bot_messages', 0)} 條
- 📝 **總消息數**: {stats.get('total_messages', 0)} 條
- 📜 **歷史記錄**: {len(history)} 條

## 時間統計
- ⏱️ **會話時長**: {minutes} 分 {seconds} 秒
- 🕐 **開始時間**: {start_time.strftime('%Y-%m-%d %H:%M:%S')}
- 🕐 **當前時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 平均速率
- 📈 **消息/分鐘**: {stats.get('total_messages', 0) / max(minutes, 1):.2f}

✅ 會話運行正常！
        """

    except Exception as e:
        return f"❌ 獲取統計失敗: {str(e)}"


async def clear_history() -> str:
    """清除對話歷史"""
    try:
        # 保存當前歷史記錄數
        history = cl.user_session.get("conversation_history", [])
        count = len(history)

        # 清除歷史
        cl.user_session.set("conversation_history", [])

        # 重置統計（保留開始時間）
        stats = cl.user_session.get("stats", {})
        start_time = stats.get("start_time", datetime.now().isoformat())

        cl.user_session.set("stats", {
            "total_messages": 0,
            "user_messages": 0,
            "bot_messages": 0,
            "start_time": start_time
        })

        return f"""
✅ **對話歷史已清除**

- 清除了 {count} 條歷史記錄
- 統計數據已重置
- 可以開始新的對話了！

💡 輸入任何消息開始新的對話。
        """

    except Exception as e:
        return f"❌ 清除歷史失敗: {str(e)}"


async def show_config() -> str:
    """顯示配置信息"""
    try:
        config = cl.user_session.get("user_config", {})

        return f"""
# ⚙️ 當前配置

- 👤 **用戶名**: {config.get('name', '未設置')}
- 🌐 **語言**: {config.get('language', '未設置')}
- 🎨 **主題**: {config.get('theme', '未設置')}

💡 **提示**: 配置功能正在開發中，即將支持動態修改。
        """

    except Exception as e:
        return f"❌ 獲取配置失敗: {str(e)}"


async def export_conversation() -> str:
    """導出對話記錄"""
    try:
        history = cl.user_session.get("conversation_history", [])
        stats = cl.user_session.get("stats", {})

        if not history:
            return "📭 沒有可導出的對話記錄。"

        # 創建導出數據
        export_data = {
            "export_time": datetime.now().isoformat(),
            "statistics": stats,
            "conversation": history
        }

        # 格式化為 JSON
        json_str = json.dumps(export_data, ensure_ascii=False, indent=2)

        return f"""
# 📦 對話記錄導出

```json
{json_str}
```

---

💾 **導出信息**:
- 總記錄數: {len(history)}
- 導出時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 你可以複製上面的 JSON 數據保存為文件。
        """

    except Exception as e:
        return f"❌ 導出失敗: {str(e)}"


# ==================== 對話處理 ====================

async def handle_conversation(user_message: str) -> str:
    """
    處理普通對話
    基於對話歷史提供上下文感知的回應

    Args:
        user_message: 用戶消息

    Returns:
        回應內容
    """
    try:
        # 獲取對話歷史
        history = cl.user_session.get("conversation_history", [])

        # 簡單的上下文感知回應
        response_parts = []

        # 問候檢測
        if any(word in user_message.lower() for word in ["你好", "hello", "hi", "嗨"]):
            user_msg_count = cl.user_session.get("stats", {}).get("user_messages", 0)
            if user_msg_count == 1:
                response_parts.append("👋 你好！很高興認識你！")
            else:
                response_parts.append("👋 你好！我們又見面了！")

        # 再見檢測
        elif any(word in user_message.lower() for word in ["再見", "bye", "goodbye", "拜拜"]):
            response_parts.append("👋 再見！期待下次再聊！")
            duration = (
                datetime.now() -
                datetime.fromisoformat(cl.user_session.get("stats", {}).get("start_time", datetime.now().isoformat()))
            ).total_seconds() / 60
            response_parts.append(f"\n我們聊了 {duration:.1f} 分鐘呢！")

        # 感謝檢測
        elif any(word in user_message.lower() for word in ["謝謝", "thanks", "thank you"]):
            response_parts.append("😊 不客氣！很高興能幫助你！")

        # 默認回應
        else:
            response_parts.append(f"💬 我收到了你的消息：「{user_message}」")

            # 基於歷史提供上下文
            if len(history) > 5:
                response_parts.append(
                    f"\n\n我們已經聊了 {len(history)} 輪了！"
                    "我會記住我們的對話內容。"
                )

            response_parts.append(
                "\n\n💡 **提示**: 這是一個對話界面演示。"
                "試試輸入 `/help` 查看更多功能！"
            )

        return "\n".join(response_parts)

    except Exception as e:
        return f"❌ 處理對話時出錯: {str(e)}"


# ==================== 輔助函數 ====================

def add_to_history(role: str, content: str):
    """
    添加消息到對話歷史

    Args:
        role: 消息角色 (user/assistant/system)
        content: 消息內容
    """
    try:
        history = cl.user_session.get("conversation_history", [])

        history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

        cl.user_session.set("conversation_history", history)

    except Exception as e:
        print(f"❌ 添加歷史失敗: {str(e)}")


def update_stats(message_type: str):
    """
    更新統計信息

    Args:
        message_type: 消息類型 (user/bot)
    """
    try:
        stats = cl.user_session.get("stats", {})

        stats["total_messages"] = stats.get("total_messages", 0) + 1

        if message_type == "user":
            stats["user_messages"] = stats.get("user_messages", 0) + 1
        elif message_type == "bot":
            stats["bot_messages"] = stats.get("bot_messages", 0) + 1

        cl.user_session.set("stats", stats)

    except Exception as e:
        print(f"❌ 更新統計失敗: {str(e)}")


# ==================== 會話結束 ====================

@cl.on_chat_end
async def on_chat_end():
    """會話結束時的清理工作"""
    try:
        stats = cl.user_session.get("stats", {})
        history = cl.user_session.get("conversation_history", [])

        print(f"""
╔══════════════════════════════════════════╗
║         會話已結束                       ║
╚══════════════════════════════════════════╝

統計信息:
- 總消息數: {stats.get('total_messages', 0)}
- 用戶消息: {stats.get('user_messages', 0)}
- 助手回應: {stats.get('bot_messages', 0)}
- 歷史記錄: {len(history)} 條

感謝使用！
        """)

    except Exception as e:
        print(f"❌ 結束會話時出錯: {str(e)}")


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║   Chainlit 對話界面示例                  ║
╚══════════════════════════════════════════╝

運行命令：
    chainlit run 02_對話界面.py -w

功能特點：
✅ 完整的對話歷史管理
✅ 多種消息類型支持
✅ 用戶會話管理
✅ 統計信息追蹤
✅ 上下文感知回應
✅ 命令系統
✅ 對話導出功能

訪問 http://localhost:8000 開始使用！
    """)


if __name__ == "__main__":
    main()
