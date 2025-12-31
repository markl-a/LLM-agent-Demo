"""
Gradio 多模態示例

本示例展示：
1. 多種輸入類型組合
2. 圖片、音頻、視頻處理
3. 文件上傳
4. 複雜輸出展示

運行方式：
    python 05_多模態.py
"""

import gradio as gr
from PIL import Image
import numpy as np
from typing import Tuple, Dict, Any
import json


# ==================== 多模態處理函數 ====================

def multi_input_processor(
    text: str,
    image: Image.Image,
    slider_value: float,
    checkbox: bool,
    radio: str
) -> Tuple[str, Image.Image]:
    """
    處理多種輸入類型

    Args:
        text: 文本輸入
        image: 圖像輸入
        slider_value: 滑塊值
        checkbox: 複選框狀態
        radio: 單選按鈕值

    Returns:
        處理結果文本和圖像
    """
    # 生成結果文本
    result_text = f"""
📊 **多輸入處理結果**

**接收到的輸入：**
• 文本：{text if text else '(空)'}
• 滑塊值：{slider_value}
• 複選框：{'✅ 已選中' if checkbox else '❌ 未選中'}
• 單選按鈕：{radio}
• 圖像：{'✅ 已上傳' if image else '❌ 未上傳'}

**處理狀態：**
✅ 所有輸入已成功接收和處理！
    """

    # 處理圖像（如果有）
    if image:
        # 根據滑塊值調整亮度
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Brightness(image)
        processed_image = enhancer.enhance(slider_value / 50)
    else:
        # 創建一個默認圖像
        processed_image = Image.new('RGB', (400, 300), color=(200, 200, 200))

    return result_text, processed_image


def image_and_text_analyzer(image: Image.Image, text: str) -> Dict[str, Any]:
    """
    同時分析圖像和文本

    Args:
        image: 輸入圖像
        text: 輸入文本

    Returns:
        分析結果字典
    """
    result = {}

    # 圖像分析
    if image:
        result['image_size'] = f"{image.width} × {image.height}"
        result['image_mode'] = image.mode
        result['image_pixels'] = image.width * image.height
    else:
        result['image_size'] = "未上傳"

    # 文本分析
    if text:
        result['text_length'] = len(text)
        result['word_count'] = len(text.split())
        result['has_chinese'] = any('\u4e00' <= char <= '\u9fff' for char in text)
    else:
        result['text_length'] = 0

    return result


def multi_output_generator(prompt: str) -> Tuple[str, str, Dict, Image.Image]:
    """
    生成多種輸出類型

    Args:
        prompt: 輸入提示

    Returns:
        多種類型的輸出
    """
    # 文本輸出 1
    text1 = f"""
🎯 **主要輸出**

輸入提示：{prompt}
處理時間：已完成
狀態：✅ 成功
    """

    # 文本輸出 2
    text2 = f"""
📝 **詳細信息**

- 字符數：{len(prompt)}
- 處理模式：多模態
- 輸出類型：4 種
    """

    # JSON 輸出
    json_output = {
        "prompt": prompt,
        "length": len(prompt),
        "timestamp": "2024-01-01 12:00:00",
        "status": "completed",
        "metadata": {
            "version": "1.0",
            "type": "multi-modal"
        }
    }

    # 圖像輸出
    img = Image.new('RGB', (400, 300), color=(100, 150, 200))

    return text1, text2, json_output, img


def file_analyzer(file) -> str:
    """
    分析上傳的文件

    Args:
        file: 上傳的文件

    Returns:
        文件分析結果
    """
    if file is None:
        return "請上傳文件！"

    try:
        # 獲取文件信息
        file_name = file.name if hasattr(file, 'name') else "unknown"
        file_size = 0

        # 讀取文件內容
        if isinstance(file, str):
            # 文件路徑
            with open(file, 'rb') as f:
                content = f.read()
                file_size = len(content)
        else:
            # 文件對象
            content = file.read() if hasattr(file, 'read') else b''
            file_size = len(content)

        result = f"""
📁 **文件分析結果**

**基本信息：**
• 文件名：{file_name}
• 文件大小：{file_size:,} 字節 ({file_size / 1024:.2f} KB)
• 文件類型：{file_name.split('.')[-1] if '.' in file_name else '未知'}

**內容預覽：**
{content[:200].decode('utf-8', errors='ignore') if file_size > 0 else '(空文件)'}...

✅ 分析完成！
        """

        return result

    except Exception as e:
        return f"❌ 文件分析失敗：{str(e)}"


def create_gallery() -> list:
    """
    創建圖片畫廊

    Returns:
        圖片列表
    """
    images = []

    # 生成一些示例圖片
    colors = [
        (255, 0, 0),    # 紅
        (0, 255, 0),    # 綠
        (0, 0, 255),    # 藍
        (255, 255, 0),  # 黃
        (255, 0, 255),  # 洋紅
        (0, 255, 255),  # 青
    ]

    for i, color in enumerate(colors):
        img = Image.new('RGB', (200, 200), color=color)
        images.append((img, f"顏色 {i+1}"))

    return images


# ==================== Gradio 界面 ====================

def create_demo():
    """創建 Gradio 應用"""

    with gr.Blocks(theme=gr.themes.Soft(), title="🎭 Gradio 多模態") as demo:

        gr.Markdown("# 🎭 Gradio 多模態處理示例")
        gr.Markdown("展示多種輸入輸出類型的組合使用")

        with gr.Tabs():

            # Tab 1: 多輸入處理
            with gr.TabItem("📥 多輸入處理"):
                gr.Markdown("### 組合多種輸入類型")

                with gr.Row():
                    with gr.Column():
                        text_input = gr.Textbox(
                            label="文本輸入",
                            placeholder="輸入一些文字..."
                        )
                        image_input = gr.Image(
                            type="pil",
                            label="圖像輸入"
                        )
                        slider_input = gr.Slider(
                            minimum=0,
                            maximum=100,
                            value=50,
                            label="亮度調整"
                        )
                        checkbox_input = gr.Checkbox(
                            label="啟用特殊處理",
                            value=False
                        )
                        radio_input = gr.Radio(
                            choices=["選項 A", "選項 B", "選項 C"],
                            label="處理模式",
                            value="選項 A"
                        )
                        btn_multi = gr.Button("🎯 處理所有輸入", variant="primary")

                    with gr.Column():
                        output_text = gr.Textbox(
                            label="處理結果",
                            lines=12
                        )
                        output_image = gr.Image(
                            type="pil",
                            label="處理後的圖像"
                        )

                btn_multi.click(
                    fn=multi_input_processor,
                    inputs=[text_input, image_input, slider_input, checkbox_input, radio_input],
                    outputs=[output_text, output_image]
                )

            # Tab 2: 多輸出生成
            with gr.TabItem("📤 多輸出生成"):
                gr.Markdown("### 一次生成多種輸出")

                with gr.Row():
                    with gr.Column():
                        prompt_input = gr.Textbox(
                            label="輸入提示",
                            placeholder="輸入提示詞...",
                            value="測試多輸出"
                        )
                        btn_generate = gr.Button("🎨 生成多種輸出", variant="primary")

                    with gr.Column():
                        output1 = gr.Textbox(label="輸出 1：主要信息", lines=5)
                        output2 = gr.Textbox(label="輸出 2：詳細信息", lines=5)
                        output3 = gr.JSON(label="輸出 3：JSON 數據")
                        output4 = gr.Image(type="pil", label="輸出 4：生成圖像")

                btn_generate.click(
                    fn=multi_output_generator,
                    inputs=prompt_input,
                    outputs=[output1, output2, output3, output4]
                )

            # Tab 3: 文件上傳
            with gr.TabItem("📁 文件處理"):
                gr.Markdown("### 上傳和分析文件")

                with gr.Row():
                    with gr.Column():
                        file_input = gr.File(
                            label="上傳文件",
                            file_types=[".txt", ".py", ".json", ".md"],
                            type="filepath"
                        )
                        btn_analyze = gr.Button("📊 分析文件", variant="primary")

                    with gr.Column():
                        file_output = gr.Textbox(
                            label="分析結果",
                            lines=15
                        )

                btn_analyze.click(
                    fn=file_analyzer,
                    inputs=file_input,
                    outputs=file_output
                )

            # Tab 4: 圖片畫廊
            with gr.TabItem("🖼️ 圖片畫廊"):
                gr.Markdown("### Gallery 組件展示")

                btn_gallery = gr.Button("🎨 生成圖片畫廊", variant="primary")

                gallery_output = gr.Gallery(
                    label="圖片畫廊",
                    columns=3,
                    height="auto"
                )

                btn_gallery.click(
                    fn=create_gallery,
                    inputs=None,
                    outputs=gallery_output
                )

            # Tab 5: DataFrame 展示
            with gr.TabItem("📊 數據表格"):
                gr.Markdown("### DataFrame 組件")

                def create_dataframe(rows: int):
                    import pandas as pd
                    data = {
                        'ID': range(1, rows + 1),
                        '名稱': [f'項目 {i}' for i in range(1, rows + 1)],
                        '數值': np.random.randint(0, 100, rows),
                        '狀態': np.random.choice(['完成', '進行中', '待處理'], rows)
                    }
                    return pd.DataFrame(data)

                with gr.Row():
                    with gr.Column():
                        rows_input = gr.Slider(
                            minimum=5,
                            maximum=50,
                            value=10,
                            step=5,
                            label="數據行數"
                        )
                        btn_df = gr.Button("📊 生成數據表", variant="primary")

                    with gr.Column():
                        df_output = gr.DataFrame(
                            label="數據表格",
                            interactive=True
                        )

                btn_df.click(
                    fn=create_dataframe,
                    inputs=rows_input,
                    outputs=df_output
                )

            # Tab 6: HTML 輸出
            with gr.TabItem("🌐 HTML 展示"):
                gr.Markdown("### HTML 組件")

                def generate_html(title: str, color: str):
                    return f"""
                    <div style="padding: 20px; background: linear-gradient(135deg, {color} 0%, #667eea 100%); border-radius: 10px; color: white;">
                        <h1 style="margin: 0;">{title}</h1>
                        <p style="margin: 10px 0;">這是一個自定義的 HTML 組件示例</p>
                        <ul>
                            <li>支持完整的 HTML 和 CSS</li>
                            <li>可以創建豐富的界面</li>
                            <li>支持動態生成內容</li>
                        </ul>
                        <button style="padding: 10px 20px; background: white; color: #667eea; border: none; border-radius: 5px; cursor: pointer;">
                            點擊按鈕
                        </button>
                    </div>
                    """

                with gr.Row():
                    with gr.Column():
                        title_input = gr.Textbox(
                            label="標題",
                            value="歡迎使用 Gradio"
                        )
                        color_input = gr.ColorPicker(
                            label="背景顏色",
                            value="#f093fb"
                        )
                        btn_html = gr.Button("🎨 生成 HTML", variant="primary")

                    with gr.Column():
                        html_output = gr.HTML(label="HTML 輸出")

                btn_html.click(
                    fn=generate_html,
                    inputs=[title_input, color_input],
                    outputs=html_output
                )

        gr.Markdown("""
---
### 💡 功能說明

本示例展示了 Gradio 的多模態處理能力：

**輸入組件：**
- Textbox（文本）
- Image（圖像）
- Slider（滑塊）
- Checkbox（複選框）
- Radio（單選按鈕）
- File（文件上傳）
- ColorPicker（顏色選擇器）

**輸出組件：**
- Textbox（文本）
- Image（圖像）
- JSON（JSON 數據）
- Gallery（圖片畫廊）
- DataFrame（數據表格）
- HTML（HTML 內容）

所有組件都可以自由組合使用！
        """)

    return demo


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║      Gradio 多模態示例                   ║
╚══════════════════════════════════════════╝

功能特點：
✅ 多種輸入類型組合
✅ 多種輸出類型展示
✅ 文件上傳和處理
✅ 圖片畫廊
✅ 數據表格
✅ HTML 自定義輸出

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
