"""
Gradio 自定義組件示例

本示例展示：
1. Blocks API 使用
2. 自定義布局
3. 事件處理
4. 狀態管理

運行方式：
    python 06_自定義組件.py
"""

import gradio as gr
import time
from datetime import datetime
import random


# ==================== 自定義組件函數 ====================

def custom_calculator(num1: float, num2: float, operation: str) -> str:
    """自定義計算器"""
    try:
        if operation == "+":
            result = num1 + num2
        elif operation == "-":
            result = num1 - num2
        elif operation == "×":
            result = num1 * num2
        elif operation == "÷":
            if num2 == 0:
                return "❌ 錯誤：不能除以零"
            result = num1 / num2
        else:
            return "❌ 不支持的運算"

        return f"""
計算結果：{num1} {operation} {num2} = {result}
        """
    except Exception as e:
        return f"❌ 錯誤：{str(e)}"


def update_counter(current: int, action: str) -> int:
    """更新計數器"""
    if action == "增加":
        return current + 1
    elif action == "減少":
        return max(0, current - 1)
    elif action == "重置":
        return 0
    return current


def process_with_progress(text: str, progress=gr.Progress()) -> str:
    """帶進度條的處理"""
    progress(0, desc="開始處理...")
    time.sleep(0.5)

    progress(0.3, desc="分析文本...")
    time.sleep(0.5)

    progress(0.6, desc="生成結果...")
    time.sleep(0.5)

    progress(0.9, desc="即將完成...")
    time.sleep(0.5)

    progress(1.0, desc="完成！")

    return f"""
處理完成！

輸入文本：{text}
處理時間：2 秒
狀態：✅ 成功
    """


def interactive_demo(slider: float, dropdown: str, checkbox: bool) -> str:
    """互動示例"""
    return f"""
📊 **當前設置**

• 滑塊值：{slider}
• 下拉選單：{dropdown}
• 複選框：{'✅ 已選中' if checkbox else '❌ 未選中'}

所有控件都會實時更新結果！
    """


def todo_app(task: str, todo_list: list, action: str) -> tuple:
    """簡單的待辦事項應用"""
    if action == "添加" and task.strip():
        todo_list.append({
            'task': task,
            'completed': False,
            'time': datetime.now().strftime("%H:%M:%S")
        })
        return "", todo_list, format_todo_list(todo_list)
    elif action == "清空":
        return "", [], "待辦事項列表為空"

    return task, todo_list, format_todo_list(todo_list)


def format_todo_list(todo_list: list) -> str:
    """格式化待辦事項列表"""
    if not todo_list:
        return "暫無待辦事項"

    result = "📝 **待辦事項列表**\n\n"
    for i, item in enumerate(todo_list, 1):
        result += f"{i}. [{item['time']}] {item['task']}\n"

    return result


# ==================== Gradio 界面 ====================

def create_demo():
    """創建 Gradio 應用"""

    with gr.Blocks(
        theme=gr.themes.Soft(),
        title="🎨 Gradio 自定義組件",
        css="""
        .custom-box {
            border: 2px solid #4CAF50;
            padding: 20px;
            border-radius: 10px;
            background: #f0f0f0;
        }
        """
    ) as demo:

        gr.Markdown("# 🎨 Gradio 自定義組件和布局")
        gr.Markdown("使用 Blocks API 創建自定義界面")

        with gr.Tabs():

            # Tab 1: 自定義布局
            with gr.TabItem("📐 自定義布局"):
                gr.Markdown("### 使用 Row 和 Column 組織布局")

                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("**左側欄**")
                        input1 = gr.Textbox(label="輸入 1")
                        input2 = gr.Textbox(label="輸入 2")

                    with gr.Column(scale=2):
                        gr.Markdown("**主要內容區（寬度是左側的 2 倍）**")
                        output = gr.Textbox(label="輸出", lines=5)

                    with gr.Column(scale=1):
                        gr.Markdown("**右側欄**")
                        btn1 = gr.Button("按鈕 1")
                        btn2 = gr.Button("按鈕 2")

                gr.Markdown("---")

                with gr.Row(equal_height=True):
                    box1 = gr.Textbox(label="等高框 1")
                    box2 = gr.Textbox(label="等高框 2")
                    box3 = gr.Textbox(label="等高框 3")

            # Tab 2: 事件處理
            with gr.TabItem("⚡ 事件處理"):
                gr.Markdown("### 各種事件監聽")

                with gr.Row():
                    with gr.Column():
                        event_text = gr.Textbox(
                            label="輸入文本",
                            placeholder="輸入後會觸發事件..."
                        )
                        event_btn = gr.Button("點擊我", variant="primary")
                        event_slider = gr.Slider(0, 100, label="拖動滑塊")

                    with gr.Column():
                        event_log = gr.Textbox(
                            label="事件日誌",
                            lines=10
                        )

                def log_event(event_type: str, value: str = "") -> str:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    return f"[{timestamp}] {event_type}: {value}"

                # 綁定事件
                event_text.change(
                    fn=lambda x: log_event("文本改變", x),
                    inputs=event_text,
                    outputs=event_log
                )

                event_btn.click(
                    fn=lambda: log_event("按鈕點擊"),
                    outputs=event_log
                )

                event_slider.change(
                    fn=lambda x: log_event("滑塊改變", str(x)),
                    inputs=event_slider,
                    outputs=event_log
                )

            # Tab 3: 狀態管理
            with gr.TabItem("💾 狀態管理"):
                gr.Markdown("### 使用 State 管理數據")

                # 創建狀態變量
                counter_state = gr.State(value=0)

                with gr.Row():
                    with gr.Column():
                        gr.Markdown("**計數器**")
                        counter_display = gr.Number(
                            label="當前計數",
                            value=0,
                            interactive=False
                        )

                        with gr.Row():
                            btn_inc = gr.Button("➕ 增加")
                            btn_dec = gr.Button("➖ 減少")
                            btn_reset = gr.Button("🔄 重置")

                    with gr.Column():
                        gr.Markdown("**操作歷史**")
                        history = gr.Textbox(
                            label="歷史記錄",
                            lines=8
                        )

                def update_with_history(current: int, action: str, hist: str) -> tuple:
                    new_val = update_counter(current, action)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    new_hist = f"[{timestamp}] {action}: {current} → {new_val}\n{hist}"
                    return new_val, new_val, new_hist

                btn_inc.click(
                    fn=lambda c, h: update_with_history(c, "增加", h),
                    inputs=[counter_state, history],
                    outputs=[counter_state, counter_display, history]
                )

                btn_dec.click(
                    fn=lambda c, h: update_with_history(c, "減少", h),
                    inputs=[counter_state, history],
                    outputs=[counter_state, counter_display, history]
                )

                btn_reset.click(
                    fn=lambda c, h: update_with_history(c, "重置", h),
                    inputs=[counter_state, history],
                    outputs=[counter_state, counter_display, history]
                )

            # Tab 4: 進度條
            with gr.TabItem("📊 進度追蹤"):
                gr.Markdown("### 顯示處理進度")

                with gr.Row():
                    with gr.Column():
                        progress_input = gr.Textbox(
                            label="輸入內容",
                            placeholder="輸入要處理的內容...",
                            value="測試進度條功能"
                        )
                        progress_btn = gr.Button("🚀 開始處理", variant="primary")

                    with gr.Column():
                        progress_output = gr.Textbox(
                            label="處理結果",
                            lines=8
                        )

                progress_btn.click(
                    fn=process_with_progress,
                    inputs=progress_input,
                    outputs=progress_output
                )

            # Tab 5: 互動示例
            with gr.TabItem("🎮 實時互動"):
                gr.Markdown("### 實時更新的互動組件")

                with gr.Row():
                    with gr.Column():
                        interactive_slider = gr.Slider(
                            0, 100,
                            value=50,
                            label="調整數值"
                        )
                        interactive_dropdown = gr.Dropdown(
                            choices=["選項 A", "選項 B", "選項 C"],
                            value="選項 A",
                            label="選擇選項"
                        )
                        interactive_checkbox = gr.Checkbox(
                            label="啟用特性",
                            value=True
                        )

                    with gr.Column():
                        interactive_output = gr.Textbox(
                            label="實時結果",
                            lines=10
                        )

                # 任何組件改變時都更新輸出
                for component in [interactive_slider, interactive_dropdown, interactive_checkbox]:
                    component.change(
                        fn=interactive_demo,
                        inputs=[interactive_slider, interactive_dropdown, interactive_checkbox],
                        outputs=interactive_output
                    )

            # Tab 6: 待辦事項
            with gr.TabItem("📝 待辦應用"):
                gr.Markdown("### 簡單的待辦事項管理")

                todo_state = gr.State(value=[])

                with gr.Row():
                    with gr.Column():
                        todo_input = gr.Textbox(
                            label="新任務",
                            placeholder="輸入待辦事項..."
                        )
                        with gr.Row():
                            add_btn = gr.Button("➕ 添加", variant="primary")
                            clear_btn = gr.Button("🗑️ 清空")

                    with gr.Column():
                        todo_display = gr.Textbox(
                            label="待辦列表",
                            lines=15
                        )

                add_btn.click(
                    fn=lambda t, l: todo_app(t, l, "添加"),
                    inputs=[todo_input, todo_state],
                    outputs=[todo_input, todo_state, todo_display]
                )

                clear_btn.click(
                    fn=lambda t, l: todo_app(t, l, "清空"),
                    inputs=[todo_input, todo_state],
                    outputs=[todo_input, todo_state, todo_display]
                )

            # Tab 7: 自定義 CSS
            with gr.TabItem("🎨 自定義樣式"):
                gr.Markdown("### 使用自定義 CSS 美化界面")

                with gr.Row():
                    with gr.Column(elem_classes="custom-box"):
                        gr.Markdown("**自定義樣式框**")
                        gr.Markdown("這個框使用了自定義 CSS 樣式")
                        styled_text = gr.Textbox(label="樣式化輸入")

                    with gr.Column():
                        gr.Markdown("**普通框**")
                        gr.Markdown("這個框使用默認樣式")
                        normal_text = gr.Textbox(label="普通輸入")

                gr.Markdown("""
**CSS 代碼：**
```css
.custom-box {
    border: 2px solid #4CAF50;
    padding: 20px;
    border-radius: 10px;
    background: #f0f0f0;
}
```
                """)

        gr.Markdown("""
---
### 💡 Blocks API 特點

**布局組件：**
- `gr.Row()` - 水平排列
- `gr.Column()` - 垂直排列
- `gr.Tabs()` - 標籤頁
- `gr.Accordion()` - 折疊面板

**狀態管理：**
- `gr.State()` - 存儲會話數據
- 在多個組件間共享數據

**事件處理：**
- `.click()` - 點擊事件
- `.change()` - 改變事件
- `.submit()` - 提交事件
- `.upload()` - 上傳事件

**進度追蹤：**
- `gr.Progress()` - 顯示處理進度
- 支持自定義進度消息

更多信息請查看 [Gradio Blocks 文檔](https://gradio.app/docs/#blocks)
        """)

    return demo


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║      Gradio 自定義組件示例               ║
╚══════════════════════════════════════════╝

功能特點：
✅ 自定義布局（Row/Column）
✅ 事件處理和監聽
✅ 狀態管理
✅ 進度條展示
✅ 實時互動
✅ 待辦事項應用
✅ 自定義 CSS 樣式

啟動應用...
    """)

    demo = create_demo()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )


if __name__ == "__main__":
    main()
