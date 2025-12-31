"""
Chainlit 快速開始示例

本示例展示：
1. Chainlit 的基本結構
2. 生命週期鉤子函數
3. 消息發送和接收
4. Hello World 示例

運行方式：
    chainlit run 01_快速開始.py -w

訪問：
    http://localhost:8000
"""

import chainlit as cl
from datetime import datetime
from typing import Optional


# ==================== 生命週期鉤子 ====================

@cl.on_chat_start
async def on_chat_start():
    """
    當用戶開始新的聊天會話時調用
    用於初始化設置、歡迎消息等
    """
    try:
        # 發送歡迎消息
        welcome_message = """
👋 **歡迎使用 Chainlit！**

這是一個快速開始示例。你可以：

1️⃣ 發送任何消息給我
2️⃣ 我會回覆你的消息
3️⃣ 體驗 Chainlit 的基本功能

試著發送「你好」或「幫助」給我！
        """

        await cl.Message(
            content=welcome_message,
            author="系統"
        ).send()

        # 初始化會話數據
        cl.user_session.set("start_time", datetime.now())
        cl.user_session.set("message_count", 0)

        print("✅ 新會話已啟動")

    except Exception as e:
        error_msg = f"❌ 初始化錯誤: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()


@cl.on_message
async def on_message(message: cl.Message):
    """
    當接收到用戶消息時調用
    這是處理用戶輸入的主要函數

    Args:
        message: 用戶發送的消息對象
    """
    try:
        # 更新消息計數
        count = cl.user_session.get("message_count", 0)
        count += 1
        cl.user_session.set("message_count", count)

        # 獲取用戶消息內容
        user_message = message.content.strip().lower()

        # 根據不同的輸入返回不同的響應
        if user_message in ["你好", "hello", "hi", "嗨"]:
            response = handle_greeting()
        elif user_message in ["幫助", "help", "?"]:
            response = handle_help()
        elif user_message in ["狀態", "status", "info"]:
            response = handle_status()
        elif "時間" in user_message or "time" in user_message:
            response = handle_time()
        else:
            response = handle_echo(message.content)

        # 發送響應
        await cl.Message(
            content=response,
            author="AI 助手"
        ).send()

        print(f"📨 已處理第 {count} 條消息: {user_message[:50]}...")

    except Exception as e:
        error_msg = f"❌ 處理消息時出錯: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()


@cl.on_chat_end
async def on_chat_end():
    """
    當聊天會話結束時調用
    用於清理資源、記錄日誌等
    """
    try:
        # 獲取會話統計信息
        start_time = cl.user_session.get("start_time")
        message_count = cl.user_session.get("message_count", 0)

        if start_time:
            duration = (datetime.now() - start_time).total_seconds()
            print(f"📊 會話結束 - 持續時間: {duration:.1f}秒, 消息數: {message_count}")

    except Exception as e:
        print(f"❌ 結束會話時出錯: {str(e)}")


@cl.on_stop
async def on_stop():
    """
    當用戶點擊停止按鈕時調用
    用於中止正在進行的操作
    """
    print("⏸️ 用戶停止了執行")


# ==================== 消息處理函數 ====================

def handle_greeting() -> str:
    """處理問候消息"""
    return """
👋 你好！很高興見到你！

我是一個簡單的 Chainlit 示例機器人。

**我可以做什麼：**
- 回覆你的消息
- 顯示當前時間
- 提供幫助信息
- 展示會話狀態

輸入「幫助」了解更多！
    """


def handle_help() -> str:
    """處理幫助請求"""
    return """
📚 **幫助信息**

**可用命令：**

• `你好` / `hello` - 問候
• `幫助` / `help` - 顯示此幫助信息
• `狀態` / `status` - 顯示會話狀態
• `時間` / `time` - 顯示當前時間
• 其他任何消息 - 我會回覆你

**快捷鍵：**
• `Ctrl + Enter` - 發送消息
• `Esc` - 清空輸入框

**提示：**
Chainlit 支持 Markdown 格式，你可以發送 **粗體**、*斜體* 等格式化文本！
    """


def handle_status() -> str:
    """處理狀態查詢"""
    try:
        start_time = cl.user_session.get("start_time")
        message_count = cl.user_session.get("message_count", 0)

        if start_time:
            duration = (datetime.now() - start_time).total_seconds()
            minutes = int(duration // 60)
            seconds = int(duration % 60)

            return f"""
📊 **會話狀態**

• **會話時長**: {minutes} 分 {seconds} 秒
• **消息數量**: {message_count} 條
• **開始時間**: {start_time.strftime('%Y-%m-%d %H:%M:%S')}
• **當前時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ 一切正常！
            """
        else:
            return "⚠️ 無法獲取會話信息"

    except Exception as e:
        return f"❌ 獲取狀態失敗: {str(e)}"


def handle_time() -> str:
    """處理時間查詢"""
    now = datetime.now()
    return f"""
🕐 **當前時間**

• **日期**: {now.strftime('%Y年%m月%d日')}
• **時間**: {now.strftime('%H:%M:%S')}
• **星期**: {now.strftime('%A')}
• **時區**: UTC+8

⏰ 時間飛逝，珍惜每一刻！
    """


def handle_echo(message: str) -> str:
    """處理一般消息（回聲）"""
    return f"""
💬 **你說：** {message}

我收到了你的消息！這是一個簡單的回聲示例。

🔔 **提示**:
- 輸入「幫助」查看可用命令
- 輸入「狀態」查看會話信息
- 輸入「時間」查看當前時間
    """


# ==================== 主函數 ====================

def main():
    """
    主函數 - Chainlit 應用的入口

    注意：
    - Chainlit 應用通過 chainlit run 命令運行，不是直接運行 Python 文件
    - 此 main 函數僅用於文檔和測試目的
    """
    print("""
╔══════════════════════════════════════════╗
║   Chainlit 快速開始示例                  ║
╚══════════════════════════════════════════╝

運行命令：
    chainlit run 01_快速開始.py -w

參數說明：
    -w, --watch     : 監聽文件變化，自動重載
    -h, --host      : 指定主機地址（默認 localhost）
    -p, --port      : 指定端口（默認 8000）
    --headless      : 無頭模式，不自動打開瀏覽器

訪問地址：
    http://localhost:8000

功能特點：
✅ 生命週期鉤子展示
✅ 消息發送和接收
✅ 會話數據管理
✅ 錯誤處理
✅ 多種消息類型處理

按 Ctrl+C 停止服務器
    """)


if __name__ == "__main__":
    # Chainlit 應用不應該直接運行
    # 應該使用：chainlit run 01_快速開始.py
    main()
