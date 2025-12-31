"""
Gradio LLM 整合示例

本示例展示：
1. OpenAI 整合
2. HuggingFace 模型
3. 流式生成
4. 提示工程

運行方式：
    python 09_LLM整合.py

需要設置環境變量：
    export OPENAI_API_KEY='your-api-key'
"""

import gradio as gr
from openai import OpenAI
import os
from typing import List, Tuple, Generator
import time


# ==================== 配置 ====================

# 初始化 OpenAI 客戶端
client = None
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        client = OpenAI(api_key=api_key)
except Exception as e:
    print(f"⚠️ OpenAI 初始化失敗: {e}")


# ==================== LLM 處理函數 ====================

def basic_completion(prompt: str, model: str, temperature: float, max_tokens: int) -> str:
    """
    基礎文本生成

    Args:
        prompt: 提示詞
        model: 模型名稱
        temperature: 溫度參數
        max_tokens: 最大 token 數

    Returns:
        生成的文本
    """
    if client is None:
        return "❌ OpenAI API 未配置"

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ 錯誤：{str(e)}"


def streaming_completion(prompt: str, model: str, temperature: float) -> Generator:
    """
    流式文本生成

    Args:
        prompt: 提示詞
        model: 模型名稱
        temperature: 溫度參數

    Yields:
        逐字生成的文本
    """
    if client is None:
        yield "❌ OpenAI API 未配置"
        return

    try:
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=500,
            stream=True
        )

        full_text = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_text += chunk.choices[0].delta.content
                yield full_text

    except Exception as e:
        yield f"❌ 錯誤：{str(e)}"


def chat_with_system_prompt(
    message: str,
    history: List[Tuple[str, str]],
    system_prompt: str,
    model: str
) -> str:
    """
    帶系統提示的聊天

    Args:
        message: 用戶消息
        history: 對話歷史
        system_prompt: 系統提示
        model: 模型名稱

    Returns:
        AI 回覆
    """
    if client is None:
        return "❌ OpenAI API 未配置"

    try:
        messages = [{"role": "system", "content": system_prompt}]

        for user_msg, bot_msg in history:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": bot_msg})

        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ 錯誤：{str(e)}"


def prompt_engineering_demo(
    task: str,
    input_text: str,
    technique: str
) -> Tuple[str, str]:
    """
    提示工程演示

    Args:
        task: 任務類型
        input_text: 輸入文本
        technique: 提示技術

    Returns:
        構建的提示和生成結果
    """
    if client is None:
        return "❌ OpenAI API 未配置", ""

    # 根據任務和技術構建提示
    prompts = {
        "翻譯": {
            "基礎": f"將以下文本翻譯成英文：\n{input_text}",
            "零樣本": f"請將以下繁體中文文本翻譯成英文。保持原意和語氣。\n\n文本：{input_text}",
            "少樣本": f"""請將繁體中文翻譯成英文。

示例 1:
中文：你好，世界
英文：Hello, World

示例 2:
中文：今天天氣很好
英文：The weather is nice today

現在翻譯：
中文：{input_text}
英文：""",
            "思維鏈": f"""讓我們逐步翻譯這段文本。

1. 首先理解中文的意思
2. 找到對應的英文表達
3. 確保語法正確
4. 潤色翻譯

中文：{input_text}

讓我們開始："""
        },
        "摘要": {
            "基礎": f"總結以下文本：\n{input_text}",
            "零樣本": f"請用一句話總結以下內容的核心要點：\n{input_text}",
            "少樣本": f"""請總結以下文本的要點。

示例：
原文：人工智能是計算機科學的一個分支，旨在創建能夠執行通常需要人類智能的任務的系統。
摘要：AI 是創建智能系統的計算機科學分支。

現在總結：
原文：{input_text}
摘要：""",
            "思維鏈": f"""讓我們分步驟總結這段文本：

1. 識別主題
2. 找出關鍵點
3. 合併相似信息
4. 形成簡潔摘要

文本：{input_text}

分析："""
        },
        "分類": {
            "基礎": f"分類以下文本：\n{input_text}",
            "零樣本": f"將以下文本分類為正面、負面或中性：\n{input_text}",
            "少樣本": f"""將文本分類為正面、負面或中性。

示例：
文本：這個產品太棒了！
分類：正面

文本：質量很差，不推薦。
分類：負面

文本：{input_text}
分類：""",
            "思維鏈": f"""讓我們分析這段文本的情感：

1. 找出情感詞彙
2. 評估整體語氣
3. 考慮上下文
4. 做出分類

文本：{input_text}

分析："""
        }
    }

    # 獲取提示
    prompt = prompts.get(task, {}).get(technique, input_text)

    # 調用 API
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )

        result = response.choices[0].message.content

        return prompt, result

    except Exception as e:
        return prompt, f"❌ 錯誤：{str(e)}"


# ==================== Gradio 界面 ====================

def create_demo():
    """創建 Gradio 應用"""

    with gr.Blocks(theme=gr.themes.Soft(), title="🤖 Gradio LLM 整合") as demo:

        gr.Markdown("# 🤖 Gradio LLM 整合示例")
        gr.Markdown("展示 LLM 模型的各種整合方式")

        if client is None:
            gr.Markdown("""
⚠️ **OpenAI API 未配置**

請設置環境變量：
```bash
export OPENAI_API_KEY='your-api-key'
```
            """)

        with gr.Tabs():

            # Tab 1: 基礎生成
            with gr.TabItem("📝 基礎生成"):
                gr.Markdown("### 簡單的文本生成")

                with gr.Row():
                    with gr.Column():
                        basic_prompt = gr.Textbox(
                            label="提示詞",
                            placeholder="輸入你的提示...",
                            lines=5,
                            value="寫一首關於人工智能的詩"
                        )

                        with gr.Row():
                            basic_model = gr.Dropdown(
                                choices=["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
                                label="模型",
                                value="gpt-4o-mini"
                            )
                            basic_temp = gr.Slider(
                                minimum=0,
                                maximum=2,
                                value=0.7,
                                step=0.1,
                                label="Temperature"
                            )
                            basic_tokens = gr.Slider(
                                minimum=50,
                                maximum=2000,
                                value=500,
                                step=50,
                                label="Max Tokens"
                            )

                        basic_btn = gr.Button("🚀 生成", variant="primary")

                    with gr.Column():
                        basic_output = gr.Textbox(
                            label="生成結果",
                            lines=15
                        )

                basic_btn.click(
                    fn=basic_completion,
                    inputs=[basic_prompt, basic_model, basic_temp, basic_tokens],
                    outputs=basic_output
                )

                gr.Examples(
                    examples=[
                        ["寫一首關於春天的詩"],
                        ["解釋什麼是機器學習"],
                        ["給我 5 個 Python 學習建議"]
                    ],
                    inputs=basic_prompt
                )

            # Tab 2: 流式生成
            with gr.TabItem("⚡ 流式生成"):
                gr.Markdown("### 實時顯示生成過程")

                with gr.Row():
                    with gr.Column():
                        stream_prompt = gr.Textbox(
                            label="提示詞",
                            placeholder="輸入你的提示...",
                            lines=5,
                            value="講一個關於機器人的故事"
                        )

                        stream_model = gr.Dropdown(
                            choices=["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
                            label="模型",
                            value="gpt-4o-mini"
                        )

                        stream_temp = gr.Slider(
                            minimum=0,
                            maximum=2,
                            value=0.8,
                            step=0.1,
                            label="Temperature（創造力）"
                        )

                        stream_btn = gr.Button("⚡ 開始生成", variant="primary")

                    with gr.Column():
                        stream_output = gr.Textbox(
                            label="實時輸出",
                            lines=15
                        )

                stream_btn.click(
                    fn=streaming_completion,
                    inputs=[stream_prompt, stream_model, stream_temp],
                    outputs=stream_output
                )

            # Tab 3: 聊天對話
            with gr.TabItem("💬 聊天對話"):
                gr.Markdown("### 帶系統提示的對話")

                with gr.Row():
                    with gr.Column(scale=1):
                        chat_system = gr.Textbox(
                            label="系統提示（定義 AI 角色）",
                            value="你是一個專業的 Python 程式設計導師，用繁體中文教學。",
                            lines=3
                        )

                        chat_model = gr.Dropdown(
                            choices=["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
                            label="模型",
                            value="gpt-4o-mini"
                        )

                        # 預設角色按鈕
                        with gr.Row():
                            gr.Button("🎓 程式導師").click(
                                lambda: "你是一個專業的 Python 程式設計導師，用繁體中文教學。",
                                outputs=chat_system
                            )
                            gr.Button("✍️ 寫作助手").click(
                                lambda: "你是一個專業的寫作助手，擅長各類文章創作，用繁體中文回答。",
                                outputs=chat_system
                            )
                            gr.Button("🔬 科學解說").click(
                                lambda: "你是一個科學解說專家，用簡單易懂的方式解釋複雜概念，用繁體中文回答。",
                                outputs=chat_system
                            )

                    with gr.Column(scale=2):
                        chatbot = gr.ChatInterface(
                            fn=lambda msg, hist: chat_with_system_prompt(
                                msg, hist, chat_system.value, chat_model.value
                            ),
                            title=None,
                            retry_btn="🔄 重試",
                            undo_btn="↩️ 撤銷",
                            clear_btn="🗑️ 清空"
                        )

            # Tab 4: 提示工程
            with gr.TabItem("🎯 提示工程"):
                gr.Markdown("### 不同的提示技術對比")

                with gr.Row():
                    with gr.Column():
                        pe_task = gr.Radio(
                            choices=["翻譯", "摘要", "分類"],
                            label="任務類型",
                            value="翻譯"
                        )

                        pe_input = gr.Textbox(
                            label="輸入文本",
                            placeholder="輸入要處理的文本...",
                            lines=4,
                            value="人工智能正在改變我們的世界"
                        )

                        pe_technique = gr.Radio(
                            choices=["基礎", "零樣本", "少樣本", "思維鏈"],
                            label="提示技術",
                            value="基礎"
                        )

                        pe_btn = gr.Button("🎯 生成", variant="primary")

                    with gr.Column():
                        pe_prompt = gr.Textbox(
                            label="構建的提示",
                            lines=8
                        )

                        pe_result = gr.Textbox(
                            label="生成結果",
                            lines=8
                        )

                pe_btn.click(
                    fn=prompt_engineering_demo,
                    inputs=[pe_task, pe_input, pe_technique],
                    outputs=[pe_prompt, pe_result]
                )

                gr.Markdown("""
### 提示技術說明

**基礎提示：**
- 直接陳述任務
- 適合簡單任務

**零樣本（Zero-shot）：**
- 詳細描述任務要求
- 不提供示例
- 依賴模型的預訓練知識

**少樣本（Few-shot）：**
- 提供幾個示例
- 幫助模型理解格式
- 提高輸出質量

**思維鏈（Chain-of-Thought）：**
- 引導模型逐步推理
- 適合複雜任務
- 提高準確性
                """)

            # Tab 5: 參數調優
            with gr.TabItem("⚙️ 參數調優"):
                gr.Markdown("### 了解和調整 LLM 參數")

                gr.Markdown("""
### 重要參數說明

#### 1. Temperature（溫度）
- **範圍：** 0.0 - 2.0
- **作用：** 控制輸出的隨機性
- **0.0：** 確定性輸出（總是選擇最可能的詞）
- **0.7：** 平衡創造力和連貫性
- **1.5+：** 高度隨機和創造性

**使用建議：**
- 事實性任務：0.0-0.3
- 創意寫作：0.7-1.2
- 實驗性內容：1.5+

#### 2. Max Tokens（最大令牌數）
- **作用：** 限制輸出長度
- **1 token ≈ 0.75 個英文單詞**
- **1 token ≈ 0.5-1 個中文字**

#### 3. Top P（Nucleus Sampling）
- **範圍：** 0.0 - 1.0
- **作用：** 從累計概率達到 p 的詞中採樣
- **建議：** 使用 temperature 或 top_p，不要同時使用

#### 4. Frequency Penalty（頻率懲罰）
- **範圍：** -2.0 - 2.0
- **作用：** 降低重複詞彙的概率
- **正值：** 鼓勵多樣性
- **負值：** 允許重複

#### 5. Presence Penalty（存在懲罰）
- **範圍：** -2.0 - 2.0
- **作用：** 鼓勵討論新話題
- **正值：** 更多新話題
- **負值：** 聚焦當前話題

### 實驗建議

不同任務的推薦設置：

**代碼生成：**
```
temperature: 0.2
max_tokens: 1000
```

**創意寫作：**
```
temperature: 0.9
max_tokens: 1500
frequency_penalty: 0.5
```

**事實問答：**
```
temperature: 0.0
max_tokens: 300
```

**對話聊天：**
```
temperature: 0.7
max_tokens: 500
presence_penalty: 0.6
```
                """)

        gr.Markdown("""
---
### 💡 最佳實踐

**提示工程技巧：**
1. 明確指定輸出格式
2. 提供清晰的上下文
3. 使用示例引導
4. 分步驟處理複雜任務
5. 迭代優化提示

**成本優化：**
1. 使用合適的模型（不一定最大）
2. 限制 max_tokens
3. 緩存常見查詢
4. 批量處理請求

**質量提升：**
1. 明確角色定位
2. 提供充分上下文
3. 要求思考過程
4. 驗證和修正輸出

### 📚 相關資源

- [OpenAI API 文檔](https://platform.openai.com/docs)
- [提示工程指南](https://platform.openai.com/docs/guides/prompt-engineering)
- [最佳實踐](https://platform.openai.com/docs/guides/production-best-practices)
        """)

    return demo


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║      Gradio LLM 整合示例                 ║
╚══════════════════════════════════════════╝

功能特點：
✅ OpenAI API 整合
✅ 基礎文本生成
✅ 流式輸出
✅ 聊天對話
✅ 提示工程技術
✅ 參數調優指南

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
