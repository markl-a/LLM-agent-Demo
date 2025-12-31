"""
Claude Code SDK 文件處理示例

本示例展示：
1. 圖像處理和分析
2. PDF 文檔處理
3. 多模態輸入
4. 文件批量處理
"""

import os
import base64
from pathlib import Path
from anthropic import Anthropic
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv

console = Console()
load_dotenv()


def encode_image(image_path: str) -> tuple:
    """編碼圖像為 base64"""
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")

    # 根據文件擴展名確定 MIME 類型
    ext = Path(image_path).suffix.lower()
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp"
    }

    media_type = mime_types.get(ext, "image/jpeg")

    return image_data, media_type


def demo_image_analysis():
    """圖像分析示例"""
    console.print("\n[bold cyan]1. 圖像分析[/bold cyan]\n")

    client = Anthropic()

    # 創建示例圖像（實際使用時替換為真實圖像路徑）
    console.print("[yellow]提示：此示例需要實際圖像文件[/yellow]")
    console.print("[dim]請將圖像路徑替換為實際文件[/dim]\n")

    # 模擬圖像分析代碼
    example_code = '''
# 分析圖像示例
image_data, media_type = encode_image("path/to/image.jpg")

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": image_data
                    }
                },
                {
                    "type": "text",
                    "text": "請描述這張圖片的內容"
                }
            ]
        }
    ]
)

response = message.content[0].text
print(response)
'''

    console.print(Panel(example_code, title="圖像分析代碼", border_style="cyan"))
    console.print()


def demo_multiple_images():
    """多圖像處理示例"""
    console.print("[bold cyan]2. 多圖像處理[/bold cyan]\n")

    example_code = '''
# 比較多個圖像
images = ["image1.jpg", "image2.jpg", "image3.jpg"]

content = []
for img_path in images:
    image_data, media_type = encode_image(img_path)
    content.append({
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": media_type,
            "data": image_data
        }
    })

content.append({
    "type": "text",
    "text": "請比較這些圖片的異同"
})

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": content}]
)
'''

    console.print(Panel(example_code, title="多圖像處理", border_style="cyan"))
    console.print()


def demo_image_with_text():
    """圖像與文本混合處理"""
    console.print("[bold cyan]3. 圖像與文本混合[/bold cyan]\n")

    example_code = '''
# 圖像 + 文本上下文
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "這是我們產品的設計稿："
                },
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": design_image_data
                    }
                },
                {
                    "type": "text",
                    "text": "請從用戶體驗角度提供改進建議"
                }
            ]
        }
    ]
)
'''

    console.print(Panel(example_code, title="圖像與文本混合", border_style="cyan"))
    console.print()


def demo_image_tasks():
    """圖像處理任務示例"""
    console.print("[bold cyan]4. 常見圖像處理任務[/bold cyan]\n")

    tasks = {
        "圖像描述": "請詳細描述這張圖片的內容",
        "物體識別": "識別圖片中的所有物體並列出",
        "文字提取 (OCR)": "提取圖片中的所有文字",
        "場景理解": "這張圖片是在什麼場景下拍攝的？",
        "情感分析": "描述這張圖片傳達的情感和氛圍",
        "設計評估": "從設計角度評估這個界面的優缺點",
        "代碼解讀": "解釋截圖中的代碼在做什麼",
        "圖表分析": "分析這個圖表並總結關鍵數據",
    }

    table = Table(title="圖像處理任務")
    table.add_column("任務類型", style="cyan", width=20)
    table.add_column("提示詞示例", style="green", width=40)

    for task, prompt in tasks.items():
        table.add_row(task, prompt)

    console.print(table)
    console.print()


def demo_pdf_processing():
    """PDF 處理示例"""
    console.print("[bold cyan]5. PDF 文檔處理[/bold cyan]\n")

    console.print("[yellow]PDF 處理方法：[/yellow]\n")

    methods = [
        ("方法 1：轉換為圖像", "將 PDF 頁面轉換為圖像後分析"),
        ("方法 2：提取文本", "使用 PyPDF 等工具提取文本後處理"),
        ("方法 3：混合處理", "結合圖像和文本進行全面分析"),
    ]

    for method, description in methods:
        console.print(f"[cyan]{method}：[/cyan]{description}")

    console.print()

    example_code = '''
# PDF 處理示例（使用 PyPDF）
from pypdf import PdfReader

# 提取 PDF 文本
reader = PdfReader("document.pdf")
text_content = ""

for page in reader.pages:
    text_content += page.extract_text()

# 使用 Claude 分析
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2048,
    messages=[
        {
            "role": "user",
            "content": f"請總結以下文檔的要點：\\n\\n{text_content}"
        }
    ]
)
'''

    console.print(Panel(example_code, title="PDF 處理代碼", border_style="cyan"))
    console.print()


def demo_document_analysis():
    """文檔分析任務"""
    console.print("[bold cyan]6. 文檔分析任務[/bold cyan]\n")

    client = Anthropic()

    # 模擬文檔內容
    sample_document = """
# 產品需求文檔

## 概述
開發一個待辦事項管理應用

## 功能需求
1. 用戶可以創建、編輯、刪除待辦事項
2. 支持設置優先級（高、中、低）
3. 支持設置截止日期
4. 支持分類標籤

## 技術要求
- 前端：React
- 後端：Node.js
- 數據庫：MongoDB
"""

    tasks = [
        ("提取關鍵信息", "列出這個文檔的主要功能需求"),
        ("生成任務清單", "根據需求生成開發任務清單"),
        ("評估複雜度", "評估每個功能的開發難度"),
        ("提出建議", "對這個需求文檔提出改進建議"),
    ]

    for task_name, query in tasks:
        console.print(f"[yellow]{task_name}：[/yellow]")

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            messages=[
                {
                    "role": "user",
                    "content": f"{query}\n\n文檔內容：\n{sample_document}"
                }
            ]
        )

        response = message.content[0].text
        console.print(f"[green]{response[:150]}...[/green]\n")


def demo_batch_file_processing():
    """批量文件處理示例"""
    console.print("[bold cyan]7. 批量文件處理[/bold cyan]\n")

    example_code = '''
# 批量處理圖像文件
import glob
from concurrent.futures import ThreadPoolExecutor

def process_image(image_path):
    """處理單個圖像"""
    image_data, media_type = encode_image(image_path)

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data
                        }
                    },
                    {
                        "type": "text",
                        "text": "簡要描述這張圖片"
                    }
                ]
            }
        ]
    )

    return {
        "file": image_path,
        "description": message.content[0].text
    }

# 批量處理
image_files = glob.glob("images/*.jpg")

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(process_image, image_files))

for result in results:
    print(f"{result['file']}: {result['description']}")
'''

    console.print(Panel(example_code, title="批量處理代碼", border_style="cyan"))
    console.print()


def demo_file_format_support():
    """支持的文件格式"""
    console.print("[bold cyan]8. 支持的文件格式[/bold cyan]\n")

    formats = [
        ("圖像", "JPEG, PNG, GIF, WebP", "直接上傳"),
        ("PDF", "PDF 文檔", "轉換為圖像或提取文本"),
        ("文本", "TXT, MD, CSV 等", "直接作為文本處理"),
        ("代碼", "Python, JS, Java 等", "作為文本分析"),
        ("Office", "Word, Excel, PPT", "需要轉換為文本或圖像"),
    ]

    table = Table(title="文件格式支持")
    table.add_column("類型", style="cyan")
    table.add_column("格式", style="yellow")
    table.add_column("處理方式", style="green")

    for file_type, formats_str, method in formats:
        table.add_row(file_type, formats_str, method)

    console.print(table)
    console.print()


def show_best_practices():
    """最佳實踐"""
    console.print("[bold cyan]文件處理最佳實踐[/bold cyan]\n")

    practices = [
        ("圖像優化", "壓縮圖像減少傳輸時間和成本"),
        ("批量處理", "使用並發處理提升效率"),
        ("錯誤處理", "處理文件讀取和編碼錯誤"),
        ("格式驗證", "驗證文件格式和大小"),
        ("安全考慮", "不要處理不可信的文件"),
        ("成本控制", "大量圖像處理會產生較高成本"),
    ]

    for practice, description in practices:
        console.print(f"[cyan]• {practice}：[/cyan]{description}")

    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Claude Code SDK 文件處理[/bold cyan]\n"
        "[dim]學習如何處理圖像、PDF 等多模態輸入[/dim]",
        border_style="cyan"
    ))

    # 1. 圖像分析
    demo_image_analysis()

    # 2. 多圖像
    demo_multiple_images()

    # 3. 混合處理
    demo_image_with_text()

    # 4. 圖像任務
    demo_image_tasks()

    # 5. PDF 處理
    demo_pdf_processing()

    # 6. 文檔分析
    demo_document_analysis()

    # 7. 批量處理
    demo_batch_file_processing()

    # 8. 格式支持
    demo_file_format_support()

    # 最佳實踐
    show_best_practices()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 文件處理示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點：[/cyan]")
    console.print("  • Claude 支持圖像、文本等多模態輸入")
    console.print("  • 使用 base64 編碼傳輸圖像")
    console.print("  • 可以混合圖像和文本提供上下文")
    console.print("  • 批量處理時注意成本控制")


if __name__ == "__main__":
    main()
