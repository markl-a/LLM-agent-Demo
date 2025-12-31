"""
Gradio 快速開始示例

本示例展示：
1. Gradio 的基本結構
2. Interface API 使用
3. 簡單的輸入輸出
4. Hello World 示例

運行方式：
    python 01_快速開始.py

訪問：
    http://localhost:7860
"""

import gradio as gr
from datetime import datetime
from typing import Optional
import random


# ==================== 基礎示例 ====================

def greet(name: str) -> str:
    """
    簡單的問候函數

    Args:
        name: 用戶名稱

    Returns:
        問候消息
    """
    if not name or name.strip() == "":
        return "請輸入你的名字！"

    return f"👋 你好，{name}！歡迎使用 Gradio！"


def greet_with_time(name: str) -> str:
    """
    帶時間的問候函數

    Args:
        name: 用戶名稱

    Returns:
        帶時間的問候消息
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hour = datetime.now().hour

    # 根據時間決定問候語
    if 5 <= hour < 12:
        greeting = "早安"
    elif 12 <= hour < 18:
        greeting = "午安"
    else:
        greeting = "晚安"

    return f"""
{greeting}，{name}！

當前時間：{current_time}
感謝使用 Gradio 框架！
    """


def calculate(num1: float, num2: float, operation: str) -> str:
    """
    簡單的計算器

    Args:
        num1: 第一個數字
        num2: 第二個數字
        operation: 運算符（+, -, *, /）

    Returns:
        計算結果
    """
    try:
        if operation == "加法 (+)":
            result = num1 + num2
            symbol = "+"
        elif operation == "減法 (-)":
            result = num1 - num2
            symbol = "-"
        elif operation == "乘法 (×)":
            result = num1 * num2
            symbol = "×"
        elif operation == "除法 (÷)":
            if num2 == 0:
                return "❌ 錯誤：不能除以零！"
            result = num1 / num2
            symbol = "÷"
        else:
            return "❌ 不支持的運算"

        return f"""
📊 **計算結果**

{num1} {symbol} {num2} = {result}

✅ 計算完成！
        """

    except Exception as e:
        return f"❌ 計算錯誤：{str(e)}"


def text_analyzer(text: str) -> str:
    """
    文本分析器

    Args:
        text: 輸入文本

    Returns:
        分析結果
    """
    if not text:
        return "請輸入文本進行分析！"

    # 統計信息
    char_count = len(text)
    char_no_space = len(text.replace(" ", ""))
    word_count = len(text.split())
    line_count = len(text.split("\n"))

    # 查找最長的單詞
    words = text.split()
    longest_word = max(words, key=len) if words else ""

    return f"""
📝 **文本分析結果**

• 總字符數：{char_count}
• 字符數（不含空格）：{char_no_space}
• 單詞數：{word_count}
• 行數：{line_count}
• 最長單詞：{longest_word} ({len(longest_word)} 字符)

✅ 分析完成！
    """


def random_quote() -> str:
    """
    隨機名言生成器

    Returns:
        隨機名言
    """
    quotes = [
        "生活就像騎自行車，要保持平衡就得不斷前進。 —— 愛因斯坦",
        "成功不是終點，失敗也不是終結，勇氣才是最重要的。 —— 邱吉爾",
        "開始行動是最困難的部分，一旦開始，事情就會變得容易。 —— 亞里士多德",
        "你今天的努力，是幸運的伏筆。 —— 佚名",
        "不要等待機會，而要創造機會。 —— 喬治·伯納德·蕭",
        "世界上只有一種真正的英雄主義，那就是認清生活的真相後依然熱愛它。 —— 羅曼·羅蘭"
    ]

    selected_quote = random.choice(quotes)

    return f"""
💡 **今日名言**

{selected_quote}

---
點擊「生成」按鈕獲取更多靈感！
    """


# ==================== Interface 創建 ====================

# 示例 1：最簡單的問候界面
demo1 = gr.Interface(
    fn=greet,
    inputs=gr.Textbox(label="請輸入你的名字", placeholder="例如：小明"),
    outputs=gr.Textbox(label="問候消息"),
    title="👋 Gradio 快速開始 - 示例 1",
    description="這是最簡單的 Gradio 應用示例",
    theme=gr.themes.Soft()
)


# 示例 2：帶時間的問候
demo2 = gr.Interface(
    fn=greet_with_time,
    inputs=gr.Textbox(
        label="你的名字",
        placeholder="請輸入...",
        lines=1
    ),
    outputs=gr.Textbox(
        label="問候語",
        lines=5
    ),
    title="🕐 時間問候器",
    description="根據當前時間給出不同的問候語",
    examples=[
        ["小明"],
        ["張三"],
        ["AI 愛好者"]
    ]
)


# 示例 3：簡單計算器
demo3 = gr.Interface(
    fn=calculate,
    inputs=[
        gr.Number(label="第一個數字", value=10),
        gr.Number(label="第二個數字", value=5),
        gr.Radio(
            choices=["加法 (+)", "減法 (-)", "乘法 (×)", "除法 (÷)"],
            label="選擇運算",
            value="加法 (+)"
        )
    ],
    outputs=gr.Textbox(label="計算結果", lines=5),
    title="🔢 簡單計算器",
    description="選擇運算類型並輸入數字進行計算",
    examples=[
        [10, 5, "加法 (+)"],
        [20, 4, "除法 (÷)"],
        [7, 8, "乘法 (×)"]
    ]
)


# 示例 4：文本分析器
demo4 = gr.Interface(
    fn=text_analyzer,
    inputs=gr.Textbox(
        label="輸入文本",
        placeholder="在這裡輸入要分析的文本...",
        lines=5
    ),
    outputs=gr.Textbox(label="分析結果", lines=10),
    title="📊 文本分析器",
    description="統計文本的字符數、單詞數等信息",
    examples=[
        ["Hello World! This is a Gradio demo."],
        ["人工智能正在改變世界"],
        ["The quick brown fox jumps over the lazy dog"]
    ]
)


# 示例 5：隨機名言生成器
demo5 = gr.Interface(
    fn=random_quote,
    inputs=None,  # 無輸入
    outputs=gr.Textbox(label="名言", lines=8),
    title="💡 隨機名言生成器",
    description="點擊「Submit」獲取隨機名言",
    allow_flagging="never"  # 禁用標記功能
)


# ==================== 組合界面 ====================

def create_combined_demo():
    """
    創建組合示例界面
    使用 TabbedInterface 組合多個界面
    """
    return gr.TabbedInterface(
        interface_list=[demo1, demo2, demo3, demo4, demo5],
        tab_names=[
            "👋 基礎問候",
            "🕐 時間問候",
            "🔢 計算器",
            "📊 文本分析",
            "💡 隨機名言"
        ],
        title="🚀 Gradio 快速開始示例集",
        theme=gr.themes.Soft()
    )


# ==================== 主函數 ====================

def main():
    """
    主函數 - 運行 Gradio 應用
    """
    print("""
╔══════════════════════════════════════════╗
║      Gradio 快速開始示例                 ║
╚══════════════════════════════════════════╝

功能特點：
✅ 5 個不同的示例界面
✅ 展示基本的輸入輸出
✅ 多種組件類型
✅ 標籤頁組織

啟動應用...
    """)

    # 創建並啟動組合界面
    demo = create_combined_demo()

    # 啟動應用
    demo.launch(
        server_name="0.0.0.0",  # 允許外部訪問
        server_port=7860,        # 默認端口
        share=False,             # 不創建公開連結
        show_error=True,         # 顯示錯誤信息
        quiet=False              # 顯示啟動日誌
    )

    print("\n✅ 應用已啟動！")
    print("📱 訪問 http://localhost:7860")
    print("🛑 按 Ctrl+C 停止服務器")


if __name__ == "__main__":
    main()
