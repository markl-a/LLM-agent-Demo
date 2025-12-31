"""
Ollama 多模態示例

本示例展示：
1. Vision 模型基礎使用
2. 圖像描述生成
3. 視覺問答（VQA）
4. 圖像內容分析
5. 多圖比較
"""

import ollama
import base64
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
import os

console = Console()


def check_vision_model(model='llava'):
    """檢查 Vision 模型是否可用"""
    try:
        console.print(f"\n[bold cyan]檢查 Vision 模型: {model}[/bold cyan]")

        models = ollama.list()
        available_models = [m['name'] for m in models.get('models', [])]

        if any(model in m for m in available_models):
            console.print(f"[green]✓ {model} 模型已安裝[/green]")
            return True
        else:
            console.print(f"[yellow]! {model} 模型未安裝[/yellow]")
            console.print(f"[dim]請運行: ollama pull {model}[/dim]")
            return False

    except Exception as e:
        console.print(f"[red]檢查模型失敗: {e}[/red]")
        return False


def encode_image(image_path):
    """將圖像編碼為 base64"""
    try:
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        console.print(f"[red]圖像編碼失敗: {e}[/red]")
        return None


def create_sample_image_url():
    """返回示例圖像 URL"""
    # 這裡使用公開的示例圖像 URL
    return "https://images.unsplash.com/photo-1506905925346-21bda4d32df4"


def image_description(image_path, model='llava'):
    """圖像描述生成"""
    try:
        console.print("\n[bold cyan]圖像描述生成[/bold cyan]")
        console.print(f"[dim]模型: {model}[/dim]")
        console.print(f"[dim]圖像: {image_path}[/dim]")

        # 檢查圖像是否存在
        if not os.path.exists(image_path):
            console.print(f"[yellow]圖像文件不存在，使用示例說明[/yellow]")
            console.print("\n[bold]使用方法:[/bold]")
            console.print("""
# 基本用法
response = ollama.chat(
    model='llava',
    messages=[
        {
            'role': 'user',
            'content': '請描述這張圖片',
            'images': ['path/to/image.jpg']
        }
    ]
)
""")
            return None

        console.print("\n[dim]正在分析圖像...[/dim]")

        # 使用 Ollama 分析圖像
        response = ollama.chat(
            model=model,
            messages=[
                {
                    'role': 'user',
                    'content': '請詳細描述這張圖片中的內容',
                    'images': [image_path]
                }
            ]
        )

        description = response['message']['content']

        console.print(Panel(
            Markdown(description),
            title="[bold green]圖像描述[/bold green]",
            border_style="green"
        ))

        return description

    except Exception as e:
        console.print(f"[red]圖像描述失敗: {e}[/red]")
        return None


def visual_question_answering(image_path, question, model='llava'):
    """視覺問答（VQA）"""
    try:
        console.print("\n[bold cyan]視覺問答（VQA）[/bold cyan]")
        console.print(f"[dim]模型: {model}[/dim]")

        if not os.path.exists(image_path):
            console.print(f"[yellow]圖像文件不存在，顯示示例用法[/yellow]")
            console.print(f"\n[bold]問題:[/bold] {question}")
            console.print("\n[bold]示例代碼:[/bold]")
            console.print("""
response = ollama.chat(
    model='llava',
    messages=[
        {
            'role': 'user',
            'content': '圖片中有幾個人？',
            'images': ['image.jpg']
        }
    ]
)
""")
            return None

        console.print(f"\n[bold]問題:[/bold] {question}")
        console.print("[dim]分析中...[/dim]")

        response = ollama.chat(
            model=model,
            messages=[
                {
                    'role': 'user',
                    'content': question,
                    'images': [image_path]
                }
            ]
        )

        answer = response['message']['content']

        console.print(Panel(
            Markdown(answer),
            title="[bold green]回答[/bold green]",
            border_style="green"
        ))

        return answer

    except Exception as e:
        console.print(f"[red]視覺問答失敗: {e}[/red]")
        return None


def multi_image_comparison(images, question, model='llava'):
    """多圖像比較"""
    try:
        console.print("\n[bold cyan]多圖像比較[/bold cyan]")

        # 檢查圖像
        existing_images = [img for img in images if os.path.exists(img)]

        if not existing_images:
            console.print("[yellow]圖像文件不存在，顯示示例用法[/yellow]")
            console.print("\n[bold]示例代碼:[/bold]")
            console.print("""
# 比較多張圖片
response = ollama.chat(
    model='llava',
    messages=[
        {
            'role': 'user',
            'content': '比較這兩張圖片的異同',
            'images': ['image1.jpg', 'image2.jpg']
        }
    ]
)
""")
            return None

        console.print(f"[dim]圖像數量: {len(existing_images)}[/dim]")
        console.print(f"[bold]問題:[/bold] {question}")

        response = ollama.chat(
            model=model,
            messages=[
                {
                    'role': 'user',
                    'content': question,
                    'images': existing_images
                }
            ]
        )

        answer = response['message']['content']

        console.print(Panel(
            Markdown(answer),
            title="[bold green]比較結果[/bold green]",
            border_style="green"
        ))

        return answer

    except Exception as e:
        console.print(f"[red]多圖像比較失敗: {e}[/red]")
        return None


def image_ocr(image_path, model='llava'):
    """圖像文字識別（OCR）"""
    try:
        console.print("\n[bold cyan]圖像文字識別（OCR）[/bold cyan]")

        if not os.path.exists(image_path):
            console.print("[yellow]圖像文件不存在，顯示示例用法[/yellow]")
            console.print("\n[bold]示例代碼:[/bold]")
            console.print("""
# 識別圖片中的文字
response = ollama.chat(
    model='llava',
    messages=[
        {
            'role': 'user',
            'content': '請提取並轉錄圖片中的所有文字',
            'images': ['document.jpg']
        }
    ]
)
""")
            return None

        console.print(f"[dim]圖像: {image_path}[/dim]")
        console.print("[dim]識別中...[/dim]")

        response = ollama.chat(
            model=model,
            messages=[
                {
                    'role': 'user',
                    'content': '請仔細提取並轉錄圖片中的所有文字。保持原有格式和排版。',
                    'images': [image_path]
                }
            ]
        )

        text = response['message']['content']

        console.print(Panel(
            text,
            title="[bold green]識別的文字[/bold green]",
            border_style="green"
        ))

        return text

    except Exception as e:
        console.print(f"[red]OCR 失敗: {e}[/red]")
        return None


def image_analysis_multi_turn(image_path, model='llava'):
    """多輪圖像分析對話"""
    try:
        console.print("\n[bold cyan]多輪圖像分析對話[/bold cyan]")

        if not os.path.exists(image_path):
            console.print("[yellow]圖像文件不存在，顯示示例用法[/yellow]")
            console.print("\n[bold]示例代碼:[/bold]")
            console.print("""
# 多輪對話
messages = [
    {
        'role': 'user',
        'content': '描述這張圖片',
        'images': ['image.jpg']
    }
]

# 第一輪
response1 = ollama.chat(model='llava', messages=messages)
messages.append(response1['message'])

# 第二輪（繼續提問，無需重複圖片）
messages.append({
    'role': 'user',
    'content': '圖片中的顏色主要是什麼？'
})

response2 = ollama.chat(model='llava', messages=messages)
""")
            return None

        console.print(f"[dim]圖像: {image_path}[/dim]\n")

        # 初始化對話
        messages = [
            {
                'role': 'user',
                'content': '請描述這張圖片',
                'images': [image_path]
            }
        ]

        # 第一輪
        console.print("[bold yellow]第 1 輪[/bold yellow]")
        console.print("[bold]用戶:[/bold] 請描述這張圖片")

        response1 = ollama.chat(model=model, messages=messages)
        messages.append(response1['message'])

        console.print(Panel(
            Markdown(response1['message']['content']),
            title="[bold green]助手[/bold green]",
            border_style="green"
        ))

        # 第二輪（無需重複圖片）
        console.print("\n[bold yellow]第 2 輪[/bold yellow]")
        console.print("[bold]用戶:[/bold] 圖片中最引人注目的元素是什麼？")

        messages.append({
            'role': 'user',
            'content': '圖片中最引人注目的元素是什麼？'
        })

        response2 = ollama.chat(model=model, messages=messages)
        messages.append(response2['message'])

        console.print(Panel(
            Markdown(response2['message']['content']),
            title="[bold green]助手[/bold green]",
            border_style="green"
        ))

        # 第三輪
        console.print("\n[bold yellow]第 3 輪[/bold yellow]")
        console.print("[bold]用戶:[/bold] 這張圖片適合用於什麼場景？")

        messages.append({
            'role': 'user',
            'content': '這張圖片適合用於什麼場景？'
        })

        response3 = ollama.chat(model=model, messages=messages)

        console.print(Panel(
            Markdown(response3['message']['content']),
            title="[bold green]助手[/bold green]",
            border_style="green"
        ))

        return messages

    except Exception as e:
        console.print(f"[red]多輪分析失敗: {e}[/red]")
        return None


def vision_models_comparison():
    """比較不同的 Vision 模型"""
    try:
        console.print("\n[bold cyan]Vision 模型比較[/bold cyan]")

        models_info = [
            {
                'name': 'llava',
                'size': '7B',
                'desc': '通用視覺語言模型，基於 Llama',
                'use_case': '圖像描述、VQA、通用分析'
            },
            {
                'name': 'llava-phi3',
                'size': '3.8B',
                'desc': '基於 Phi-3 的輕量級模型',
                'use_case': '資源受限環境、快速推理'
            },
            {
                'name': 'llava-llama3',
                'size': '8B',
                'desc': '基於 Llama 3 的最新模型',
                'use_case': '高質量圖像理解'
            },
            {
                'name': 'bakllava',
                'size': '7B',
                'desc': 'Mistral 架構的視覺模型',
                'use_case': '詳細圖像分析'
            }
        ]

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("模型", style="cyan", width=20)
        table.add_column("大小", justify="right", style="yellow", width=8)
        table.add_column("描述", style="blue", width=25)
        table.add_column("適用場景", style="green", width=25)

        for model in models_info:
            table.add_row(
                model['name'],
                model['size'],
                model['desc'],
                model['use_case']
            )

        console.print(table)

        console.print("\n[bold]下載命令:[/bold]")
        console.print("  ollama pull llava")
        console.print("  ollama pull llava-phi3")
        console.print("  ollama pull bakllava")

    except Exception as e:
        console.print(f"[red]模型比較失敗: {e}[/red]")


def usage_examples():
    """使用示例說明"""
    console.print("\n[bold cyan]Vision 模型使用示例[/bold cyan]")

    examples = [
        {
            'title': '基礎圖像描述',
            'code': """response = ollama.chat(
    model='llava',
    messages=[{
        'role': 'user',
        'content': '描述這張圖片',
        'images': ['image.jpg']
    }]
)"""
        },
        {
            'title': '視覺問答',
            'code': """response = ollama.chat(
    model='llava',
    messages=[{
        'role': 'user',
        'content': '這張圖片中有幾個人？',
        'images': ['photo.jpg']
    }]
)"""
        },
        {
            'title': '圖像比較',
            'code': """response = ollama.chat(
    model='llava',
    messages=[{
        'role': 'user',
        'content': '比較這兩張圖片',
        'images': ['img1.jpg', 'img2.jpg']
    }]
)"""
        },
        {
            'title': 'OCR 文字識別',
            'code': """response = ollama.chat(
    model='llava',
    messages=[{
        'role': 'user',
        'content': '提取圖片中的所有文字',
        'images': ['document.jpg']
    }]
)"""
        }
    ]

    for example in examples:
        console.print(f"\n[bold yellow]{example['title']}:[/bold yellow]")
        console.print(Panel(
            example['code'],
            border_style="blue"
        ))


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Ollama 多模態示例[/bold cyan]",
        border_style="cyan"
    ))

    model = 'llava'

    # 檢查模型
    console.print("\n[bold]步驟 1: 檢查 Vision 模型[/bold]")
    check_vision_model(model)

    # 模型比較
    console.print("\n[bold]示例 1: Vision 模型比較[/bold]")
    vision_models_comparison()

    # 使用示例
    console.print("\n[bold]示例 2: 代碼使用示例[/bold]")
    usage_examples()

    # 以下示例需要實際圖像文件
    console.print("\n[bold]示例 3: 圖像描述生成[/bold]")
    sample_image = "sample_image.jpg"
    image_description(sample_image, model)

    console.print("\n[bold]示例 4: 視覺問答[/bold]")
    visual_question_answering(
        sample_image,
        "這張圖片中的主要物體是什麼？",
        model
    )

    console.print("\n[bold]示例 5: OCR 文字識別[/bold]")
    image_ocr(sample_image, model)

    console.print("\n[bold]示例 6: 多圖像比較[/bold]")
    multi_image_comparison(
        ["image1.jpg", "image2.jpg"],
        "比較這兩張圖片的異同",
        model
    )

    console.print("\n[bold]示例 7: 多輪圖像分析[/bold]")
    image_analysis_multi_turn(sample_image, model)

    # 完成
    console.print("\n" + "="*60)
    console.print("[bold green]✓ 多模態示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點:[/cyan]")
    console.print("  1. Vision 模型可以理解和分析圖像")
    console.print("  2. 支持圖像描述、VQA、OCR 等任務")
    console.print("  3. 可以一次處理多張圖片")
    console.print("  4. 支持多輪對話，無需重複傳圖")
    console.print("\n[yellow]注意事項:[/yellow]")
    console.print("  • 需要先下載 Vision 模型: ollama pull llava")
    console.print("  • Vision 模型佔用更多內存（通常 6GB+）")
    console.print("  • 圖像大小會影響處理速度")


if __name__ == "__main__":
    main()
