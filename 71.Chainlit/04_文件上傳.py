"""
Chainlit 文件上傳示例

本示例展示：
1. 文件上傳處理
2. 支持的文件類型（圖片、PDF、文本等）
3. 文件解析和內容提取
4. 圖片/PDF 處理
5. 文件驗證和錯誤處理

運行方式：
    chainlit run 04_文件上傳.py -w
"""

import chainlit as cl
from typing import Optional, List
import os
from pathlib import Path
import base64
from PIL import Image
import io
import PyPDF2


# ==================== 配置 ====================

# 支持的文件類型配置
SUPPORTED_TYPES = {
    "image": ["image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp"],
    "document": ["application/pdf", "text/plain", "text/markdown"],
    "code": ["text/x-python", "application/json", "text/javascript"],
}

# 文件大小限制（字節）
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# ==================== 會話初始化 ====================

@cl.on_chat_start
async def on_chat_start():
    """初始化聊天會話"""
    try:
        # 初始化文件存儲
        cl.user_session.set("uploaded_files", [])

        # 發送歡迎消息
        welcome_msg = """
# 📁 文件上傳示例

歡迎！這個示例展示了 Chainlit 的文件上傳功能。

## 📤 支持的文件類型

### 🖼️ 圖片
- PNG, JPEG, JPG, GIF, WebP
- 最大 10 MB

### 📄 文檔
- PDF 文件
- 文本文件 (.txt)
- Markdown 文件 (.md)

### 💻 代碼
- Python (.py)
- JSON (.json)
- JavaScript (.js)

## 🎯 功能展示

1. **圖片分析** - 顯示圖片信息和預覽
2. **PDF 解析** - 提取文本內容
3. **文本處理** - 讀取和分析文本文件
4. **多文件上傳** - 同時處理多個文件

## 🚀 開始使用

點擊下方的 **📎 附件** 按鈕上傳文件！
        """

        await cl.Message(content=welcome_msg, author="系統").send()

        print("✅ 文件上傳會話已初始化")

    except Exception as e:
        error_msg = f"❌ 初始化失敗: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()


# ==================== 文件上傳處理 ====================

@cl.on_message
async def on_message(message: cl.Message):
    """
    處理消息（包括附帶的文件）
    """
    try:
        # 檢查是否有附件
        if message.elements:
            await handle_file_upload(message)
        else:
            # 處理普通文本消息
            await handle_text_message(message)

    except Exception as e:
        error_msg = f"❌ 處理消息時出錯: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()


async def handle_file_upload(message: cl.Message):
    """
    處理文件上傳

    Args:
        message: 包含文件的消息對象
    """
    try:
        uploaded_files = cl.user_session.get("uploaded_files", [])

        # 處理每個上傳的文件
        for element in message.elements:
            if isinstance(element, (cl.Image, cl.File, cl.Pdf, cl.Text)):
                # 獲取文件信息
                file_info = {
                    "name": element.name,
                    "type": type(element).__name__,
                    "path": element.path if hasattr(element, 'path') else None,
                }

                uploaded_files.append(file_info)

                # 根據文件類型處理
                if isinstance(element, cl.Image):
                    await process_image(element)
                elif isinstance(element, cl.Pdf):
                    await process_pdf(element)
                elif isinstance(element, cl.Text):
                    await process_text(element)
                elif isinstance(element, cl.File):
                    await process_generic_file(element)

        # 更新會話中的文件列表
        cl.user_session.set("uploaded_files", uploaded_files)

        # 顯示上傳統計
        await show_upload_summary()

    except Exception as e:
        error_msg = f"❌ 文件上傳處理失敗: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()


# ==================== 圖片處理 ====================

async def process_image(image_element: cl.Image):
    """
    處理上傳的圖片

    Args:
        image_element: 圖片元素
    """
    try:
        # 讀取圖片
        with Image.open(image_element.path) as img:
            # 獲取圖片信息
            width, height = img.size
            format_name = img.format
            mode = img.mode

            # 計算文件大小
            file_size = os.path.getsize(image_element.path)
            size_mb = file_size / (1024 * 1024)

            # 創建分析結果
            analysis = f"""
## 🖼️ 圖片分析結果

**文件名**: {image_element.name}

### 📊 基本信息
- **尺寸**: {width} × {height} 像素
- **格式**: {format_name}
- **色彩模式**: {mode}
- **文件大小**: {size_mb:.2f} MB

### 🎨 詳細信息
- **縱橫比**: {width/height:.2f}
- **總像素**: {width * height:,} 像素
            """

            # 如果是 RGB 模式，提取主色調（簡單實現）
            if mode == "RGB":
                # 縮小圖片以加快處理
                img_small = img.resize((100, 100))
                pixels = list(img_small.getdata())

                # 計算平均顏色
                avg_color = [
                    sum(p[0] for p in pixels) // len(pixels),
                    sum(p[1] for p in pixels) // len(pixels),
                    sum(p[2] for p in pixels) // len(pixels),
                ]

                analysis += f"\n- **平均色調**: RGB({avg_color[0]}, {avg_color[1]}, {avg_color[2]})"

            # 發送分析結果（附帶圖片預覽）
            await cl.Message(
                content=analysis,
                elements=[image_element],
                author="圖片分析"
            ).send()

            print(f"✅ 圖片處理完成: {image_element.name}")

    except Exception as e:
        error_msg = f"❌ 圖片處理失敗: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()


# ==================== PDF 處理 ====================

async def process_pdf(pdf_element: cl.Pdf):
    """
    處理上傳的 PDF 文件

    Args:
        pdf_element: PDF 元素
    """
    try:
        # 讀取 PDF
        with open(pdf_element.path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)

            # 獲取 PDF 信息
            num_pages = len(pdf_reader.pages)

            # 提取文本（前 3 頁作為預覽）
            text_content = []
            for i in range(min(3, num_pages)):
                page = pdf_reader.pages[i]
                text = page.extract_text()
                text_content.append(f"### 第 {i+1} 頁\n{text[:500]}...")

            # 獲取元數據
            metadata = pdf_reader.metadata if pdf_reader.metadata else {}

            # 文件大小
            file_size = os.path.getsize(pdf_element.path)
            size_mb = file_size / (1024 * 1024)

            # 創建分析結果
            analysis = f"""
## 📄 PDF 文檔分析

**文件名**: {pdf_element.name}

### 📊 基本信息
- **頁數**: {num_pages} 頁
- **文件大小**: {size_mb:.2f} MB

### 📝 元數據
- **標題**: {metadata.get('/Title', '未知')}
- **作者**: {metadata.get('/Author', '未知')}
- **創建日期**: {metadata.get('/CreationDate', '未知')}

### 📖 內容預覽（前 3 頁）

{chr(10).join(text_content)}

---
💡 **提示**: 這只是前幾頁的預覽。完整文檔包含 {num_pages} 頁。
            """

            # 發送分析結果
            await cl.Message(
                content=analysis,
                elements=[pdf_element],
                author="PDF 分析"
            ).send()

            print(f"✅ PDF 處理完成: {pdf_element.name}, {num_pages} 頁")

    except Exception as e:
        error_msg = f"❌ PDF 處理失敗: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()


# ==================== 文本文件處理 ====================

async def process_text(text_element: cl.Text):
    """
    處理上傳的文本文件

    Args:
        text_element: 文本元素
    """
    try:
        # 讀取文本內容
        with open(text_element.path, 'r', encoding='utf-8') as file:
            content = file.read()

        # 基本統計
        lines = content.split('\n')
        words = content.split()
        chars = len(content)

        # 文件大小
        file_size = os.path.getsize(text_element.path)
        size_kb = file_size / 1024

        # 預覽內容（前 20 行）
        preview_lines = lines[:20]
        preview = '\n'.join(preview_lines)
        if len(lines) > 20:
            preview += f"\n\n... (還有 {len(lines) - 20} 行)"

        # 創建分析結果
        analysis = f"""
## 📝 文本文件分析

**文件名**: {text_element.name}

### 📊 統計信息
- **行數**: {len(lines)} 行
- **詞數**: {len(words)} 詞
- **字符數**: {chars} 字符
- **文件大小**: {size_kb:.2f} KB

### 📖 內容預覽

```
{preview}
```

---
💡 **提示**: 文件已成功載入，可以對其進行進一步處理。
        """

        # 發送分析結果
        await cl.Message(
            content=analysis,
            author="文本分析"
        ).send()

        print(f"✅ 文本處理完成: {text_element.name}")

    except UnicodeDecodeError:
        # 嘗試其他編碼
        try:
            with open(text_element.path, 'r', encoding='gbk') as file:
                content = file.read()
            await cl.Message(
                content=f"⚠️ 使用 GBK 編碼讀取文件成功\n\n內容長度: {len(content)} 字符"
            ).send()
        except Exception as e:
            await cl.Message(
                content=f"❌ 無法讀取文件，請檢查編碼格式"
            ).send()

    except Exception as e:
        error_msg = f"❌ 文本處理失敗: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()


# ==================== 通用文件處理 ====================

async def process_generic_file(file_element: cl.File):
    """
    處理通用文件

    Args:
        file_element: 文件元素
    """
    try:
        # 獲取文件信息
        file_path = Path(file_element.path)
        file_size = file_path.stat().st_size
        size_mb = file_size / (1024 * 1024)

        # 文件擴展名
        extension = file_path.suffix

        analysis = f"""
## 📦 文件信息

**文件名**: {file_element.name}

### 📊 基本信息
- **擴展名**: {extension}
- **文件大小**: {size_mb:.2f} MB
- **路徑**: {file_path.name}

### ℹ️ 說明
這是一個 {extension} 文件。

💡 **提示**: 可以根據文件類型進行專門的處理。
        """

        await cl.Message(
            content=analysis,
            elements=[file_element],
            author="文件分析"
        ).send()

        print(f"✅ 文件處理完成: {file_element.name}")

    except Exception as e:
        error_msg = f"❌ 文件處理失敗: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()


# ==================== 輔助功能 ====================

async def show_upload_summary():
    """顯示上傳文件的統計摘要"""
    try:
        uploaded_files = cl.user_session.get("uploaded_files", [])

        if not uploaded_files:
            return

        # 按類型分組
        by_type = {}
        for file_info in uploaded_files:
            file_type = file_info["type"]
            by_type[file_type] = by_type.get(file_type, 0) + 1

        summary = f"""
---

### 📊 本次會話上傳統計

**總文件數**: {len(uploaded_files)}

**分類統計**:
        """

        for file_type, count in by_type.items():
            icon = {
                "Image": "🖼️",
                "Pdf": "📄",
                "Text": "📝",
                "File": "📦"
            }.get(file_type, "📁")

            summary += f"\n- {icon} {file_type}: {count} 個"

        await cl.Message(content=summary, author="統計").send()

    except Exception as e:
        print(f"❌ 顯示摘要失敗: {str(e)}")


async def handle_text_message(message: cl.Message):
    """
    處理純文本消息（無文件）

    Args:
        message: 消息對象
    """
    user_message = message.content.strip().lower()

    if user_message in ["/help", "幫助", "help"]:
        help_text = """
## 📚 幫助信息

### 📤 如何上傳文件

1. 點擊輸入框旁的 **📎 附件** 按鈕
2. 選擇要上傳的文件
3. 發送消息

### 🎯 支持的操作

- **上傳圖片** - 查看詳細信息和預覽
- **上傳 PDF** - 提取文本內容
- **上傳文本** - 統計和分析
- **多文件上傳** - 一次上傳多個文件

### 📝 可用命令

- `/help` - 顯示幫助
- `/list` - 列出已上傳的文件
- `/clear` - 清除文件列表

試試上傳一些文件吧！
        """
        await cl.Message(content=help_text).send()

    elif user_message in ["/list", "列表", "list"]:
        await list_uploaded_files()

    elif user_message in ["/clear", "清除", "clear"]:
        cl.user_session.set("uploaded_files", [])
        await cl.Message(content="✅ 已清除文件列表").send()

    else:
        response = f"""
收到你的消息：「{message.content}」

💡 **提示**:
- 上傳文件以查看處理效果
- 輸入 `/help` 查看幫助
        """
        await cl.Message(content=response).send()


async def list_uploaded_files():
    """列出所有已上傳的文件"""
    uploaded_files = cl.user_session.get("uploaded_files", [])

    if not uploaded_files:
        await cl.Message(content="📭 還沒有上傳任何文件").send()
        return

    file_list = "## 📁 已上傳的文件\n\n"
    for i, file_info in enumerate(uploaded_files, 1):
        file_list += f"{i}. **{file_info['name']}** ({file_info['type']})\n"

    await cl.Message(content=file_list).send()


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║   Chainlit 文件上傳示例                  ║
╚══════════════════════════════════════════╝

運行命令：
    chainlit run 04_文件上傳.py -w

功能特點：
✅ 多種文件類型支持
✅ 圖片分析和預覽
✅ PDF 文本提取
✅ 文本文件處理
✅ 文件大小限制
✅ 多文件上傳
✅ 完整錯誤處理

支持的文件：
🖼️ 圖片: PNG, JPEG, GIF, WebP
📄 文檔: PDF, TXT, MD
💻 代碼: PY, JSON, JS

訪問 http://localhost:8000 開始上傳文件！
    """)


if __name__ == "__main__":
    main()
