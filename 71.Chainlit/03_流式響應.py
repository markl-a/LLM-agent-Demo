"""
Chainlit 流式響應示例

本示例展示：
1. Token 級別流式傳輸
2. OpenAI 流式整合
3. 進度展示
4. 錯誤處理
5. 流式響應的最佳實踐

運行方式：
    chainlit run 03_流式響應.py -w

環境變量：
    需要設置 OPENAI_API_KEY
"""

import chainlit as cl
from openai import AsyncOpenAI
import asyncio
import os
from dotenv import load_dotenv
from typing import Optional, AsyncIterator

# 載入環境變量
load_dotenv()


# ==================== 全局配置 ====================

# 初始化 OpenAI 客戶端
client: Optional[AsyncOpenAI] = None


def init_openai_client():
    """初始化 OpenAI 客戶端"""
    global client

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("⚠️ 警告: 未設置 OPENAI_API_KEY，將使用模擬模式")
        client = None
    else:
        client = AsyncOpenAI(api_key=api_key)
        print("✅ OpenAI 客戶端已初始化")


# ==================== 會話初始化 ====================

@cl.on_chat_start
async def on_chat_start():
    """初始化聊天會話"""
    try:
        # 初始化 OpenAI 客戶端
        init_openai_client()

        # 初始化對話歷史
        cl.user_session.set("messages", [
            {
                "role": "system",
                "content": "你是一個友善、專業的 AI 助手。請用繁體中文回答問題。"
            }
        ])

        # 發送歡迎消息
        welcome_msg = """
# 🌊 流式響應示例

這個示例展示了 Chainlit 的流式響應功能。

## ✨ 功能特點

- ⚡ **實時響應** - Token 逐個顯示
- 🚀 **更好的體驗** - 減少等待時間
- 💬 **自然對話** - 模擬真實打字效果
- 🎯 **OpenAI 整合** - 無縫對接 GPT 模型

## 🎮 試試這些

- 問我任何問題
- 請我寫一段代碼
- 讓我講個故事
- 要我解釋複雜概念

**開始提問吧！** 你會看到答案逐字出現 ✨
        """

        await cl.Message(content=welcome_msg, author="系統").send()

        print("✅ 流式響應會話已初始化")

    except Exception as e:
        error_msg = f"❌ 初始化失敗: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()


# ==================== 消息處理 ====================

@cl.on_message
async def on_message(message: cl.Message):
    """
    處理用戶消息，使用流式響應
    """
    try:
        # 獲取對話歷史
        messages = cl.user_session.get("messages", [])

        # 添加用戶消息
        messages.append({
            "role": "user",
            "content": message.content
        })

        # 根據是否有 API Key 選擇模式
        if client:
            await stream_openai_response(messages)
        else:
            await stream_mock_response(message.content)

    except Exception as e:
        error_msg = f"❌ 處理消息時出錯: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()


# ==================== OpenAI 流式響應 ====================

async def stream_openai_response(messages: list):
    """
    使用 OpenAI API 生成流式響應

    Args:
        messages: 對話歷史
    """
    # 創建一個新的消息對象用於流式更新
    msg = cl.Message(content="", author="AI 助手")
    await msg.send()

    try:
        # 調用 OpenAI API（流式模式）
        stream = await client.chat.completions.create(
            model="gpt-4o-mini",  # 或使用 "gpt-4"
            messages=messages,
            stream=True,
            temperature=0.7,
            max_tokens=2000,
        )

        # 收集完整的響應
        full_response = ""

        # 逐個處理流式 token
        async for chunk in stream:
            # 檢查是否有內容
            if chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content

                # 添加到完整響應
                full_response += token

                # 流式更新消息
                await msg.stream_token(token)

        # 完成流式傳輸
        await msg.update()

        # 將助手回應添加到歷史
        messages.append({
            "role": "assistant",
            "content": full_response
        })

        cl.user_session.set("messages", messages)

        print(f"✅ 流式響應完成，長度: {len(full_response)}")

    except Exception as e:
        error_msg = f"\n\n❌ OpenAI API 錯誤: {str(e)}"
        await msg.stream_token(error_msg)
        await msg.update()
        print(f"❌ OpenAI 錯誤: {str(e)}")


# ==================== 模擬流式響應 ====================

async def stream_mock_response(user_message: str):
    """
    模擬流式響應（當沒有 API Key 時使用）

    Args:
        user_message: 用戶消息
    """
    # 創建響應消息
    msg = cl.Message(content="", author="AI 助手（模擬模式）")
    await msg.send()

    try:
        # 生成模擬響應
        mock_response = generate_mock_response(user_message)

        # 模擬逐字輸出
        for char in mock_response:
            await msg.stream_token(char)
            # 添加小延遲，模擬真實打字效果
            await asyncio.sleep(0.02)

        # 完成流式傳輸
        await msg.update()

        print(f"✅ 模擬流式響應完成")

    except Exception as e:
        error_msg = f"\n\n❌ 模擬響應錯誤: {str(e)}"
        await msg.stream_token(error_msg)
        await msg.update()


def generate_mock_response(user_message: str) -> str:
    """
    生成模擬響應

    Args:
        user_message: 用戶消息

    Returns:
        模擬的 AI 響應
    """
    # 簡單的關鍵詞匹配
    user_msg_lower = user_message.lower()

    if "你好" in user_msg_lower or "hello" in user_msg_lower:
        return """你好！我是 AI 助手（模擬模式）。

由於未設置 OPENAI_API_KEY，我現在運行在模擬模式下。

要啟用真實的 AI 功能，請：
1. 在 .env 文件中設置 OPENAI_API_KEY
2. 或在環境變量中設置
3. 重啟應用

有什麼我可以幫助你的嗎？"""

    elif "代碼" in user_msg_lower or "code" in user_msg_lower:
        return """這是一個 Python 代碼示例：

```python
def hello_world():
    \"\"\"一個簡單的 Hello World 函數\"\"\"
    print("Hello, World!")
    return "Success"

# 調用函數
result = hello_world()
print(f"結果: {result}")
```

這段代碼展示了：
1. 函數定義
2. 文檔字符串
3. 打印輸出
4. 返回值

需要更多說明嗎？"""

    elif "故事" in user_msg_lower or "story" in user_msg_lower:
        return """從前，在一個遙遠的數字王國裡，住著一個叫做 AI 的智慧生物。

AI 每天都在學習新的知識，幫助人們解決各種問題。它可以：

📚 回答問題
💻 編寫代碼
✍️ 創作故事
🎨 激發創意

有一天，一位程序員使用 Chainlit 創建了一個美麗的界面，讓 AI 能夠以流式的方式與人類交流。

從此，AI 和人類的對話變得更加自然和流暢...

（這是一個模擬響應。設置 OPENAI_API_KEY 以獲得更豐富的故事！）"""

    else:
        return f"""我收到了你的消息：「{user_message}」

這是一個模擬的流式響應示例。你可以看到文字是逐個出現的，這就是流式響應的效果！

💡 **模擬模式說明**：
- 當前未設置 OPENAI_API_KEY
- 使用預設的模擬響應
- 演示流式輸出效果

🔑 **啟用真實 AI**：
```bash
export OPENAI_API_KEY="your-api-key-here"
```

試試問我：
- 你好
- 寫一段代碼
- 講個故事

我會給你不同的模擬響應！"""


# ==================== 高級流式功能 ====================

async def stream_with_steps(user_message: str):
    """
    展示帶步驟的流式響應
    結合 Step 組件展示處理過程
    """
    try:
        # 步驟 1: 理解問題
        async with cl.Step(name="🔍 理解問題") as step:
            step.output = f"分析用戶輸入：{user_message[:50]}..."
            await asyncio.sleep(0.5)

        # 步驟 2: 生成回應
        async with cl.Step(name="💭 生成回應") as step:
            msg = cl.Message(content="", author="AI 助手")
            await msg.send()

            if client:
                # 使用真實 API
                messages = cl.user_session.get("messages", [])
                await stream_openai_response(messages)
            else:
                # 使用模擬響應
                await stream_mock_response(user_message)

            step.output = "回應生成完成"

        # 步驟 3: 完成
        async with cl.Step(name="✅ 完成") as step:
            step.output = "流式響應已完成"

    except Exception as e:
        print(f"❌ 帶步驟的流式響應失敗: {str(e)}")


# ==================== 自定義流式生成器 ====================

async def custom_stream_generator(text: str, delay: float = 0.03) -> AsyncIterator[str]:
    """
    自定義流式文本生成器

    Args:
        text: 要流式輸出的文本
        delay: 每個字符之間的延遲（秒）

    Yields:
        逐個字符
    """
    for char in text:
        yield char
        await asyncio.sleep(delay)


async def demo_custom_stream():
    """演示自定義流式生成器"""
    msg = cl.Message(content="", author="自定義流式")
    await msg.send()

    text = """這是一個自定義的流式生成器示例。

它可以：
1. 控制輸出速度
2. 自定義延遲時間
3. 處理任何文本內容

非常靈活！✨"""

    async for char in custom_stream_generator(text, delay=0.02):
        await msg.stream_token(char)

    await msg.update()


# ==================== 錯誤處理示例 ====================

async def stream_with_error_handling(messages: list):
    """
    帶完整錯誤處理的流式響應
    """
    msg = cl.Message(content="", author="AI 助手")
    await msg.send()

    try:
        # 設置超時
        async with asyncio.timeout(30):
            stream = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=True,
            )

            full_response = ""

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    full_response += token
                    await msg.stream_token(token)

            await msg.update()

            # 保存到歷史
            messages.append({
                "role": "assistant",
                "content": full_response
            })

            cl.user_session.set("messages", messages)

    except asyncio.TimeoutError:
        error = "\n\n⏱️ 請求超時，請重試。"
        await msg.stream_token(error)
        await msg.update()

    except Exception as e:
        error = f"\n\n❌ 發生錯誤: {str(e)}"
        await msg.stream_token(error)
        await msg.update()


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║   Chainlit 流式響應示例                  ║
╚══════════════════════════════════════════╝

運行命令：
    chainlit run 03_流式響應.py -w

環境變量設置：
    export OPENAI_API_KEY="your-key-here"

功能特點：
✅ Token 級別流式傳輸
✅ OpenAI API 整合
✅ 模擬模式（無需 API Key）
✅ 實時進度展示
✅ 完整錯誤處理
✅ 超時控制
✅ 自定義流式生成器

流式響應優勢：
⚡ 更快的感知響應速度
💬 更自然的對話體驗
🎯 更好的用戶體驗
📊 實時進度反饋

訪問 http://localhost:8000 體驗流式響應！
    """)


if __name__ == "__main__":
    main()
