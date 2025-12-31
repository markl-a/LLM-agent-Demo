"""
Gradio 圖像處理示例

本示例展示：
1. Image 組件使用
2. PIL 圖像操作
3. 圖像濾鏡和效果
4. 圖像分析功能

運行方式：
    python 03_圖像處理.py
"""

import gradio as gr
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw, ImageFont
import numpy as np
from typing import Tuple
import io


# ==================== 圖像處理函數 ====================

def apply_filter(image: Image.Image, filter_type: str) -> Image.Image:
    """
    應用圖像濾鏡

    Args:
        image: 輸入圖像
        filter_type: 濾鏡類型

    Returns:
        處理後的圖像
    """
    if image is None:
        return None

    filters = {
        "模糊": ImageFilter.BLUR,
        "輪廓": ImageFilter.CONTOUR,
        "細節增強": ImageFilter.DETAIL,
        "邊緣增強": ImageFilter.EDGE_ENHANCE,
        "銳化": ImageFilter.SHARPEN,
        "平滑": ImageFilter.SMOOTH,
        "浮雕": ImageFilter.EMBOSS,
        "查找邊緣": ImageFilter.FIND_EDGES
    }

    selected_filter = filters.get(filter_type, ImageFilter.BLUR)
    return image.filter(selected_filter)


def adjust_image(
    image: Image.Image,
    brightness: float,
    contrast: float,
    saturation: float,
    sharpness: float
) -> Image.Image:
    """
    調整圖像參數

    Args:
        image: 輸入圖像
        brightness: 亮度 (0.0 - 2.0)
        contrast: 對比度 (0.0 - 2.0)
        saturation: 飽和度 (0.0 - 2.0)
        sharpness: 銳度 (0.0 - 2.0)

    Returns:
        調整後的圖像
    """
    if image is None:
        return None

    # 應用調整
    img = ImageEnhance.Brightness(image).enhance(brightness)
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = ImageEnhance.Color(img).enhance(saturation)
    img = ImageEnhance.Sharpness(img).enhance(sharpness)

    return img


def resize_image(image: Image.Image, width: int, height: int, keep_ratio: bool) -> Tuple[Image.Image, str]:
    """
    調整圖像尺寸

    Args:
        image: 輸入圖像
        width: 目標寬度
        height: 目標高度
        keep_ratio: 是否保持寬高比

    Returns:
        調整後的圖像和信息
    """
    if image is None:
        return None, "請上傳圖像！"

    original_size = image.size

    if keep_ratio:
        image.thumbnail((width, height), Image.Resampling.LANCZOS)
        new_size = image.size
    else:
        image = image.resize((width, height), Image.Resampling.LANCZOS)
        new_size = (width, height)

    info = f"""
🖼️ **調整尺寸完成**

原始尺寸：{original_size[0]} × {original_size[1]}
新尺寸：{new_size[0]} × {new_size[1]}
保持寬高比：{'是' if keep_ratio else '否'}
    """

    return image, info


def rotate_and_flip(image: Image.Image, rotation: int, flip_type: str) -> Image.Image:
    """
    旋轉和翻轉圖像

    Args:
        image: 輸入圖像
        rotation: 旋轉角度
        flip_type: 翻轉類型

    Returns:
        處理後的圖像
    """
    if image is None:
        return None

    # 旋轉
    if rotation != 0:
        image = image.rotate(rotation, expand=True)

    # 翻轉
    if flip_type == "水平翻轉":
        image = ImageOps.mirror(image)
    elif flip_type == "垂直翻轉":
        image = ImageOps.flip(image)
    elif flip_type == "水平+垂直":
        image = ImageOps.mirror(image)
        image = ImageOps.flip(image)

    return image


def color_effects(image: Image.Image, effect: str) -> Image.Image:
    """
    顏色效果處理

    Args:
        image: 輸入圖像
        effect: 效果類型

    Returns:
        處理後的圖像
    """
    if image is None:
        return None

    if effect == "灰度":
        return ImageOps.grayscale(image)
    elif effect == "反色":
        return ImageOps.invert(image.convert("RGB"))
    elif effect == "黑白":
        return image.convert("1")
    elif effect == "色調分離":
        return ImageOps.posterize(image.convert("RGB"), 3)
    elif effect == "自動對比度":
        return ImageOps.autocontrast(image.convert("RGB"))
    elif effect == "均衡化":
        return ImageOps.equalize(image.convert("RGB"))
    else:
        return image


def analyze_image(image: Image.Image) -> str:
    """
    分析圖像信息

    Args:
        image: 輸入圖像

    Returns:
        分析結果
    """
    if image is None:
        return "請上傳圖像！"

    # 基本信息
    width, height = image.size
    mode = image.mode
    format_name = image.format if hasattr(image, 'format') else "Unknown"

    # 計算文件大小（估算）
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    file_size = len(img_byte_arr.getvalue())

    # 顏色統計
    if mode == "RGB" or mode == "RGBA":
        # 轉換為 numpy 數組
        img_array = np.array(image)

        if mode == "RGBA":
            img_array = img_array[:, :, :3]  # 移除 alpha 通道

        # 計算平均顏色
        avg_color = img_array.mean(axis=(0, 1))
        r, g, b = avg_color

        # 計算亮度
        brightness = (r * 0.299 + g * 0.587 + b * 0.114)
    else:
        r = g = b = 0
        brightness = 0

    result = f"""
📊 **圖像分析報告**

**基本信息：**
• 尺寸：{width} × {height} 像素
• 寬高比：{width/height:.2f}:1
• 總像素數：{width * height:,}
• 顏色模式：{mode}
• 格式：{format_name}
• 估算大小：{file_size / 1024:.2f} KB

**顏色分析：**
• 平均紅色：{r:.0f}
• 平均綠色：{g:.0f}
• 平均藍色：{b:.0f}
• 整體亮度：{brightness:.0f} / 255

**分類：**
• 圖像方向：{'橫向' if width > height else '縱向' if height > width else '正方形'}
• 亮度級別：{'明亮' if brightness > 170 else '中等' if brightness > 85 else '昏暗'}

✅ 分析完成！
    """

    return result


def add_watermark(image: Image.Image, text: str, position: str, opacity: int) -> Image.Image:
    """
    添加水印

    Args:
        image: 輸入圖像
        text: 水印文字
        position: 位置
        opacity: 透明度 (0-100)

    Returns:
        添加水印後的圖像
    """
    if image is None:
        return None

    if not text:
        return image

    # 創建副本
    img = image.copy().convert("RGBA")
    txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)

    # 設置字體（使用默認字體）
    try:
        # 嘗試使用系統字體
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        # 使用默認字體
        font = ImageFont.load_default()

    # 計算文本位置
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    positions = {
        "左上": (10, 10),
        "右上": (img.width - text_width - 10, 10),
        "左下": (10, img.height - text_height - 10),
        "右下": (img.width - text_width - 10, img.height - text_height - 10),
        "中心": ((img.width - text_width) // 2, (img.height - text_height) // 2)
    }

    pos = positions.get(position, (10, 10))

    # 計算透明度
    alpha = int(255 * (opacity / 100))

    # 繪製水印
    draw.text(pos, text, fill=(255, 255, 255, alpha), font=font)

    # 合併圖層
    watermarked = Image.alpha_composite(img, txt_layer)

    return watermarked.convert("RGB")


def batch_process(image: Image.Image, operations: list) -> Image.Image:
    """
    批量處理圖像

    Args:
        image: 輸入圖像
        operations: 操作列表

    Returns:
        處理後的圖像
    """
    if image is None:
        return None

    result = image.copy()

    for op in operations:
        if op == "銳化":
            result = result.filter(ImageFilter.SHARPEN)
        elif op == "增強對比度":
            result = ImageOps.autocontrast(result.convert("RGB"))
        elif op == "去噪":
            result = result.filter(ImageFilter.SMOOTH_MORE)

    return result


# ==================== Gradio 界面 ====================

def create_demo():
    """創建 Gradio 應用"""

    with gr.Blocks(theme=gr.themes.Soft(), title="🖼️ Gradio 圖像處理") as demo:

        gr.Markdown("# 🖼️ Gradio 圖像處理工具集")
        gr.Markdown("展示 Image 組件和 PIL 圖像處理功能")

        with gr.Tabs():

            # Tab 1: 濾鏡效果
            with gr.TabItem("🎨 濾鏡效果"):
                gr.Markdown("### 應用各種圖像濾鏡")

                with gr.Row():
                    with gr.Column():
                        input_filter = gr.Image(
                            type="pil",
                            label="上傳圖像"
                        )
                        filter_type = gr.Radio(
                            choices=[
                                "模糊", "輪廓", "細節增強", "邊緣增強",
                                "銳化", "平滑", "浮雕", "查找邊緣"
                            ],
                            label="選擇濾鏡",
                            value="模糊"
                        )
                        btn_filter = gr.Button("🎨 應用濾鏡", variant="primary")

                    with gr.Column():
                        output_filter = gr.Image(
                            type="pil",
                            label="處理結果"
                        )

                btn_filter.click(
                    fn=apply_filter,
                    inputs=[input_filter, filter_type],
                    outputs=output_filter
                )

            # Tab 2: 參數調整
            with gr.TabItem("⚙️ 參數調整"):
                gr.Markdown("### 調整圖像的亮度、對比度等參數")

                with gr.Row():
                    with gr.Column():
                        input_adjust = gr.Image(
                            type="pil",
                            label="上傳圖像"
                        )
                        brightness = gr.Slider(
                            minimum=0.0,
                            maximum=2.0,
                            value=1.0,
                            step=0.1,
                            label="亮度"
                        )
                        contrast = gr.Slider(
                            minimum=0.0,
                            maximum=2.0,
                            value=1.0,
                            step=0.1,
                            label="對比度"
                        )
                        saturation = gr.Slider(
                            minimum=0.0,
                            maximum=2.0,
                            value=1.0,
                            step=0.1,
                            label="飽和度"
                        )
                        sharpness = gr.Slider(
                            minimum=0.0,
                            maximum=2.0,
                            value=1.0,
                            step=0.1,
                            label="銳度"
                        )
                        btn_adjust = gr.Button("⚙️ 調整參數", variant="primary")

                    with gr.Column():
                        output_adjust = gr.Image(
                            type="pil",
                            label="調整結果"
                        )

                btn_adjust.click(
                    fn=adjust_image,
                    inputs=[input_adjust, brightness, contrast, saturation, sharpness],
                    outputs=output_adjust
                )

            # Tab 3: 尺寸調整
            with gr.TabItem("📏 尺寸調整"):
                gr.Markdown("### 調整圖像尺寸")

                with gr.Row():
                    with gr.Column():
                        input_resize = gr.Image(
                            type="pil",
                            label="上傳圖像"
                        )
                        target_width = gr.Slider(
                            minimum=100,
                            maximum=2000,
                            value=800,
                            step=50,
                            label="目標寬度"
                        )
                        target_height = gr.Slider(
                            minimum=100,
                            maximum=2000,
                            value=600,
                            step=50,
                            label="目標高度"
                        )
                        keep_ratio = gr.Checkbox(
                            label="保持寬高比",
                            value=True
                        )
                        btn_resize = gr.Button("📏 調整尺寸", variant="primary")

                    with gr.Column():
                        output_resize = gr.Image(
                            type="pil",
                            label="調整結果"
                        )
                        info_resize = gr.Textbox(
                            label="尺寸信息",
                            lines=5
                        )

                btn_resize.click(
                    fn=resize_image,
                    inputs=[input_resize, target_width, target_height, keep_ratio],
                    outputs=[output_resize, info_resize]
                )

            # Tab 4: 旋轉翻轉
            with gr.TabItem("🔄 旋轉翻轉"):
                gr.Markdown("### 旋轉和翻轉圖像")

                with gr.Row():
                    with gr.Column():
                        input_rotate = gr.Image(
                            type="pil",
                            label="上傳圖像"
                        )
                        rotation = gr.Slider(
                            minimum=0,
                            maximum=360,
                            value=0,
                            step=15,
                            label="旋轉角度"
                        )
                        flip_type = gr.Radio(
                            choices=["不翻轉", "水平翻轉", "垂直翻轉", "水平+垂直"],
                            label="翻轉方式",
                            value="不翻轉"
                        )
                        btn_rotate = gr.Button("🔄 應用變換", variant="primary")

                    with gr.Column():
                        output_rotate = gr.Image(
                            type="pil",
                            label="處理結果"
                        )

                btn_rotate.click(
                    fn=rotate_and_flip,
                    inputs=[input_rotate, rotation, flip_type],
                    outputs=output_rotate
                )

            # Tab 5: 顏色效果
            with gr.TabItem("🌈 顏色效果"):
                gr.Markdown("### 應用顏色效果")

                with gr.Row():
                    with gr.Column():
                        input_color = gr.Image(
                            type="pil",
                            label="上傳圖像"
                        )
                        effect = gr.Radio(
                            choices=[
                                "灰度", "反色", "黑白",
                                "色調分離", "自動對比度", "均衡化"
                            ],
                            label="選擇效果",
                            value="灰度"
                        )
                        btn_color = gr.Button("🌈 應用效果", variant="primary")

                    with gr.Column():
                        output_color = gr.Image(
                            type="pil",
                            label="處理結果"
                        )

                btn_color.click(
                    fn=color_effects,
                    inputs=[input_color, effect],
                    outputs=output_color
                )

            # Tab 6: 圖像分析
            with gr.TabItem("📊 圖像分析"):
                gr.Markdown("### 分析圖像信息")

                with gr.Row():
                    with gr.Column():
                        input_analyze = gr.Image(
                            type="pil",
                            label="上傳圖像"
                        )
                        btn_analyze = gr.Button("📊 分析圖像", variant="primary")

                    with gr.Column():
                        output_analyze = gr.Textbox(
                            label="分析結果",
                            lines=20
                        )

                btn_analyze.click(
                    fn=analyze_image,
                    inputs=input_analyze,
                    outputs=output_analyze
                )

            # Tab 7: 添加水印
            with gr.TabItem("💧 添加水印"):
                gr.Markdown("### 為圖像添加文字水印")

                with gr.Row():
                    with gr.Column():
                        input_watermark = gr.Image(
                            type="pil",
                            label="上傳圖像"
                        )
                        watermark_text = gr.Textbox(
                            label="水印文字",
                            placeholder="輸入水印內容...",
                            value="Sample Watermark"
                        )
                        watermark_position = gr.Radio(
                            choices=["左上", "右上", "左下", "右下", "中心"],
                            label="水印位置",
                            value="右下"
                        )
                        watermark_opacity = gr.Slider(
                            minimum=0,
                            maximum=100,
                            value=50,
                            step=5,
                            label="透明度"
                        )
                        btn_watermark = gr.Button("💧 添加水印", variant="primary")

                    with gr.Column():
                        output_watermark = gr.Image(
                            type="pil",
                            label="添加水印後"
                        )

                btn_watermark.click(
                    fn=add_watermark,
                    inputs=[input_watermark, watermark_text, watermark_position, watermark_opacity],
                    outputs=output_watermark
                )

        gr.Markdown("""
---
### 💡 使用提示

- **濾鏡效果**：快速應用各種藝術濾鏡
- **參數調整**：精細控制圖像的視覺效果
- **尺寸調整**：調整圖像大小，支持保持寬高比
- **旋轉翻轉**：任意角度旋轉和鏡像翻轉
- **顏色效果**：轉換顏色模式和風格
- **圖像分析**：查看詳細的圖像信息
- **添加水印**：為圖像添加版權保護

支持 PNG、JPG、JPEG、GIF 等常見格式！
        """)

    return demo


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║      Gradio 圖像處理示例                 ║
╚══════════════════════════════════════════╝

功能特點：
✅ 7 種圖像處理工具
✅ 多種濾鏡效果
✅ 參數精細調整
✅ 尺寸調整
✅ 旋轉翻轉
✅ 顏色效果
✅ 圖像分析
✅ 水印添加

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
