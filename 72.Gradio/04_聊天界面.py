"""
Gradio 聊天界面示例

本示例展示：
1. ChatInterface 組件使用
2. 對話歷史管理
3. 流式響應
4. LLM 整合（OpenAI）

運行方式：
    python 04_聊天界面.py

需要設置環境變量：
    export OPENAI_API_KEY='your-api-key'
"""

import gradio as gr
from openai import OpenAI
import os
from typing import List, Tuple
import time
from datetime import datetime


# ==================== 配置 ====================

# 初始化 OpenAI 客戶端
client = None
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        client = OpenAI(api_key=api_key)
except Exception as e:
    print(f"⚠️ OpenAI 客戶端初始化失敗: {e}")


# ==================== 聊天函數 ====================

def simple_chat(message: str, history: List[Tuple[str, str]]) -> str:
    """
    簡單的回聲聊天機器人

    Args:
        message: 用戶消息
        history: 對話歷史

    Returns:
        回覆消息
    """
    # 簡單的模擬回覆
    responses = {
        "你好": "你好！很高興見到你！我是 Gradio 聊天助手。",
        "幫助": "我可以回答你的問題。試著和我聊聊天吧！",
        "時間": f"現在是 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    }

    # 檢查關鍵詞
    for keyword, response in responses.items():
        if keyword in message.lower():
            return response

    # 默認回覆
    return f"你說：「{message}」\n\n我理解了你的消息。需要什麼幫助嗎？"


def chat_with_memory(message: str, history: List[Tuple[str, str]]) -> str:
    """
    帶記憶的聊天機器人

    Args:
        message: 用戶消息
        history: 對話歷史

    Returns:
        回覆消息
    """
    # 統計對話輪數
    turn_count = len(history) + 1

    # 檢查歷史中的關鍵信息
    user_name = None
    for user_msg, bot_msg in history:
        if "我叫" in user_msg or "我是" in user_msg:
            # 簡單提取名字
            parts = user_msg.replace("我叫", "").replace("我是", "").split()
            if parts:
                user_name = parts[0]

    # 生成回覆
    response = f"【第 {turn_count} 輪對話】\n\n"

    if user_name:
        response += f"{user_name}，"
    else:
        response += "你好，"

    response += f"你說：「{message}」\n\n"

    # 根據消息內容回覆
    if "記得" in message:
        if user_name:
            response += f"當然記得！你是 {user_name}。"
        else:
            response += "我會記住我們的對話！"
    elif "忘記" in message:
        response += "我會一直記得我們的對話內容。"
    else:
        response += f"我理解了。我們已經聊了 {turn_count} 輪了。"

    return response


def chat_with_openai(message: str, history: List[Tuple[str, str]]) -> str:
    """
    使用 OpenAI API 的聊天機器人

    Args:
        message: 用戶消息
        history: 對話歷史

    Returns:
        AI 回覆
    """
    if client is None:
        return "❌ OpenAI API 未配置。請設置 OPENAI_API_KEY 環境變量。"

    try:
        # 構建消息歷史
        messages = [
            {"role": "system", "content": "你是一個友好、有幫助的 AI 助手。用繁體中文回答問題。"}
        ]

        # 添加歷史對話
        for user_msg, bot_msg in history:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": bot_msg})

        # 添加當前消息
        messages.append({"role": "user", "content": message})

        # 調用 API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ 錯誤：{str(e)}"


def streaming_chat(message: str, history: List[Tuple[str, str]]):
    """
    流式響應聊天機器人

    Args:
        message: 用戶消息
        history: 對話歷史

    Yields:
        逐字生成的回覆
    """
    if client is None:
        yield "❌ OpenAI API 未配置。請設置 OPENAI_API_KEY 環境變量。"
        return

    try:
        # 構建消息歷史
        messages = [
            {"role": "system", "content": "你是一個友好、有幫助的 AI 助手。用繁體中文回答問題。"}
        ]

        for user_msg, bot_msg in history:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": bot_msg})

        messages.append({"role": "user", "content": message})

        # 流式調用 API
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=500,
            stream=True
        )

        # 逐字返回
        response_text = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                response_text += chunk.choices[0].delta.content
                yield response_text

    except Exception as e:
        yield f"❌ 錯誤：{str(e)}"


def chat_with_context(message: str, history: List[Tuple[str, str]], system_prompt: str) -> str:
    """
    可自定義系統提示的聊天機器人

    Args:
        message: 用戶消息
        history: 對話歷史
        system_prompt: 系統提示

    Returns:
        AI 回覆
    """
    if client is None:
        return "❌ OpenAI API 未配置。請設置 OPENAI_API_KEY 環境變量。"

    try:
        # 構建消息
        messages = [{"role": "system", "content": system_prompt}]

        for user_msg, bot_msg in history:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": bot_msg})

        messages.append({"role": "user", "content": message})

        # 調用 API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ 錯誤：{str(e)}"


# ==================== Gradio 界面 ====================

def create_demo():
    """創建 Gradio 應用"""

    with gr.Blocks(theme=gr.themes.Soft(), title="💬 Gradio 聊天界面") as demo:

        gr.Markdown("# 💬 Gradio 聊天界面示例")
        gr.Markdown("展示 ChatInterface 組件的各種用法")

        with gr.Tabs():

            # Tab 1: 簡單聊天
            with gr.TabItem("💭 簡單聊天"):
                gr.Markdown("### 基礎的回聲聊天機器人")

                chat1 = gr.ChatInterface(
                    fn=simple_chat,
                    title="簡單聊天機器人",
                    description="試著輸入「你好」、「幫助」或「時間」",
                    examples=["你好", "幫助", "時間"],
                    theme=gr.themes.Soft(),
                    retry_btn="🔄 重試",
                    undo_btn="↩️ 撤銷",
                    clear_btn="🗑️ 清空"
                )

            # Tab 2: 帶記憶的聊天
            with gr.TabItem("🧠 記憶聊天"):
                gr.Markdown("### 能記住對話內容的聊天機器人")

                chat2 = gr.ChatInterface(
                    fn=chat_with_memory,
                    title="記憶聊天機器人",
                    description="我會記住我們的對話！試著說「我叫小明」然後問我「記得我的名字嗎？」",
                    examples=[
                        "我叫小明",
                        "記得我的名字嗎？",
                        "我們聊了多久了？"
                    ],
                    retry_btn="🔄 重試",
                    undo_btn="↩️ 撤銷",
                    clear_btn="🗑️ 清空"
                )

            # Tab 3: OpenAI 聊天
            with gr.TabItem("🤖 AI 聊天"):
                gr.Markdown("### 使用 OpenAI GPT 模型的聊天機器人")

                if client:
                    chat3 = gr.ChatInterface(
                        fn=chat_with_openai,
                        title="OpenAI 聊天機器人",
                        description="由 GPT-4o-mini 驅動的智能對話",
                        examples=[
                            "介紹一下 Gradio 框架",
                            "什麼是機器學習？",
                            "寫一個 Python 排序函數"
                        ],
                        retry_btn="🔄 重試",
                        undo_btn="↩️ 撤銷",
                        clear_btn="🗑️ 清空"
                    )
                else:
                    gr.Markdown("""
⚠️ **OpenAI API 未配置**

請設置環境變量：
```bash
export OPENAI_API_KEY='your-api-key-here'
```

然後重新運行應用。
                    """)

            # Tab 4: 流式聊天
            with gr.TabItem("⚡ 流式聊天"):
                gr.Markdown("### 支持流式輸出的聊天機器人")

                if client:
                    chat4 = gr.ChatInterface(
                        fn=streaming_chat,
                        title="流式聊天機器人",
                        description="實時顯示 AI 生成的內容",
                        examples=[
                            "寫一首關於春天的詩",
                            "解釋量子計算的原理",
                            "給我講個故事"
                        ],
                        retry_btn="🔄 重試",
                        undo_btn="↩️ 撤銷",
                        clear_btn="🗑️ 清空"
                    )
                else:
                    gr.Markdown("⚠️ OpenAI API 未配置")

            # Tab 5: 自定義角色
            with gr.TabItem("🎭 角色扮演"):
                gr.Markdown("### 可自定義系統提示的聊天機器人")

                with gr.Row():
                    with gr.Column(scale=1):
                        system_prompt = gr.Textbox(
                            label="系統提示（定義 AI 角色）",
                            value="你是一個專業的 Python 程式導師，用繁體中文教學。",
                            lines=3
                        )
                        gr.Markdown("""
**預設角色：**
- Python 導師
- 寫作助手
- 翻譯專家
- 創意顧問
                        """)

                        # 快速切換角色
                        def set_teacher_role():
                            return "你是一個專業的 Python 程式導師，用繁體中文教學。"

                        def set_writer_role():
                            return "你是一個專業的寫作助手，擅長撰寫各類文章，用繁體中文回答。"

                        def set_translator_role():
                            return "你是一個專業的中英翻譯專家，提供準確的翻譯服務。"

                        gr.Button("🎓 Python 導師").click(
                            fn=set_teacher_role,
                            outputs=system_prompt
                        )
                        gr.Button("✍️ 寫作助手").click(
                            fn=set_writer_role,
                            outputs=system_prompt
                        )
                        gr.Button("🌐 翻譯專家").click(
                            fn=set_translator_role,
                            outputs=system_prompt
                        )

                    with gr.Column(scale=2):
                        if client:
                            chat5 = gr.ChatInterface(
                                fn=lambda msg, hist: chat_with_context(msg, hist, system_prompt.value),
                                title="角色扮演聊天",
                                description="根據左側的系統提示扮演不同角色",
                                additional_inputs=[system_prompt],
                                retry_btn="🔄 重試",
                                undo_btn="↩️ 撤銷",
                                clear_btn="🗑️ 清空"
                            )
                        else:
                            gr.Markdown("⚠️ OpenAI API 未配置")

        gr.Markdown("""
---
### 💡 使用提示

- **簡單聊天**：基礎的問答功能
- **記憶聊天**：能記住對話上下文
- **AI 聊天**：使用 GPT 模型的智能對話
- **流式聊天**：實時展示生成過程
- **角色扮演**：自定義 AI 的行為和專長

### 🔑 API 配置

需要使用 OpenAI API 的功能需要先設置環境變量：
```bash
export OPENAI_API_KEY='your-api-key-here'
```

### 📚 相關資源

- [Gradio ChatInterface 文檔](https://gradio.app/docs/#chatinterface)
- [OpenAI API 文檔](https://platform.openai.com/docs)
        """)

    return demo


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║      Gradio 聊天界面示例                 ║
╚══════════════════════════════════════════╝

功能特點：
✅ 5 種不同的聊天模式
✅ 簡單聊天機器人
✅ 帶記憶的對話
✅ OpenAI GPT 整合
✅ 流式響應支持
✅ 自定義角色扮演

API 狀態：
    """)

    if client:
        print("✅ OpenAI API 已配置")
    else:
        print("⚠️  OpenAI API 未配置")
        print("    設置方法：export OPENAI_API_KEY='your-key'")

    print("\n啟動應用...")

    demo = create_demo()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )


if __name__ == "__main__":
    main()
