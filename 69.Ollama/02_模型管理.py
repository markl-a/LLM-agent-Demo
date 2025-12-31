"""
Ollama 模型管理示例

本示例展示：
1. 列出所有模型
2. 下載模型
3. 刪除模型
4. 查看模型詳情
5. 複製和重命名模型
"""

import ollama
import subprocess
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def list_models():
    """列出所有已下載的模型"""
    try:
        console.print("\n[bold cyan]已下載的模型列表[/bold cyan]")

        response = ollama.list()
        models = response.get('models', [])

        if not models:
            console.print("[yellow]尚未下載任何模型[/yellow]")
            return []

        # 創建表格
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("模型名稱", style="cyan", width=30)
        table.add_column("大小", justify="right", style="green")
        table.add_column("修改時間", style="yellow")
        table.add_column("參數量", style="blue")

        for model in models:
            name = model.get('name', 'Unknown')
            size = model.get('size', 0)
            size_gb = size / (1024**3)
            modified = model.get('modified_at', 'Unknown')

            # 提取修改時間（只顯示日期）
            if modified != 'Unknown':
                modified = modified.split('T')[0]

            # 嘗試從名稱推斷參數量
            param_count = "Unknown"
            if '70b' in name.lower():
                param_count = "70B"
            elif '13b' in name.lower():
                param_count = "13B"
            elif '7b' in name.lower():
                param_count = "7B"
            elif '3b' in name.lower():
                param_count = "3B"
            elif '1b' in name.lower():
                param_count = "1B"

            table.add_row(name, f"{size_gb:.2f} GB", modified, param_count)

        console.print(table)
        console.print(f"\n[dim]共 {len(models)} 個模型[/dim]")

        return models

    except Exception as e:
        console.print(f"[red]獲取模型列表失敗: {e}[/red]")
        return []


def show_model_details(model_name):
    """顯示模型詳細信息"""
    try:
        console.print(f"\n[bold cyan]模型詳情: {model_name}[/bold cyan]")

        response = ollama.show(model_name)

        # 顯示基本信息
        console.print("\n[bold]基本信息:[/bold]")
        console.print(f"  模型名稱: {model_name}")

        # Modelfile 內容
        modelfile = response.get('modelfile', '')
        if modelfile:
            console.print("\n[bold]Modelfile 內容:[/bold]")
            console.print(Panel(modelfile, border_style="blue"))

        # 參數設置
        parameters = response.get('parameters', '')
        if parameters:
            console.print("\n[bold]參數設置:[/bold]")
            console.print(f"  {parameters}")

        # 模板
        template = response.get('template', '')
        if template:
            console.print("\n[bold]提示詞模板:[/bold]")
            console.print(Panel(template[:200] + "...", border_style="yellow"))

        return response

    except Exception as e:
        console.print(f"[red]獲取模型詳情失敗: {e}[/red]")
        return None


def pull_model(model_name, show_progress=True):
    """
    下載模型

    Args:
        model_name: 模型名稱，如 'llama3.2', 'mistral', 'gemma2:2b'
        show_progress: 是否顯示下載進度
    """
    try:
        console.print(f"\n[bold cyan]開始下載模型: {model_name}[/bold cyan]")

        if show_progress:
            # 使用進度條顯示
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"下載 {model_name}...", total=None)

                # 流式下載
                current_digest = None
                for part in ollama.pull(model_name, stream=True):
                    status = part.get('status', '')
                    digest = part.get('digest', '')
                    total = part.get('total', 0)
                    completed = part.get('completed', 0)

                    # 更新進度描述
                    if digest and digest != current_digest:
                        current_digest = digest
                        progress.update(task, description=f"{status}: {digest[:12]}...")
                    else:
                        progress.update(task, description=status)

                    # 如果有總大小，更新進度
                    if total > 0:
                        progress.update(task, total=total, completed=completed)

                progress.update(task, description=f"✓ {model_name} 下載完成")

        else:
            # 不顯示進度，直接下載
            ollama.pull(model_name)

        console.print(f"[green]✓ 模型 {model_name} 下載成功[/green]")
        return True

    except Exception as e:
        console.print(f"[red]下載模型失敗: {e}[/red]")
        return False


def delete_model(model_name):
    """刪除模型"""
    try:
        console.print(f"\n[bold yellow]刪除模型: {model_name}[/bold yellow]")

        # 確認刪除
        console.print("[yellow]警告: 此操作將永久刪除模型文件[/yellow]")

        ollama.delete(model_name)

        console.print(f"[green]✓ 模型 {model_name} 已刪除[/green]")
        return True

    except Exception as e:
        console.print(f"[red]刪除模型失敗: {e}[/red]")
        return False


def copy_model(source, destination):
    """複製模型（創建別名）"""
    try:
        console.print(f"\n[bold cyan]複製模型[/bold cyan]")
        console.print(f"  源模型: {source}")
        console.print(f"  目標模型: {destination}")

        ollama.copy(source, destination)

        console.print(f"[green]✓ 模型複製成功[/green]")
        return True

    except Exception as e:
        console.print(f"[red]複製模型失敗: {e}[/red]")
        return False


def check_model_exists(model_name):
    """檢查模型是否存在"""
    try:
        response = ollama.list()
        models = response.get('models', [])

        for model in models:
            if model.get('name', '').startswith(model_name):
                return True

        return False

    except Exception as e:
        console.print(f"[red]檢查模型失敗: {e}[/red]")
        return False


def recommend_models():
    """推薦模型列表"""
    console.print("\n[bold cyan]推薦模型列表[/bold cyan]")

    recommendations = [
        {
            'name': 'llama3.2:1b',
            'size': '1GB',
            'desc': '最輕量級，適合快速測試和資源受限環境'
        },
        {
            'name': 'llama3.2',
            'size': '2GB',
            'desc': '平衡性能和資源，適合日常使用'
        },
        {
            'name': 'mistral',
            'size': '4GB',
            'desc': '高性能 7B 模型，代碼和推理能力強'
        },
        {
            'name': 'gemma2:2b',
            'size': '2GB',
            'desc': 'Google 最新小型模型，性能優異'
        },
        {
            'name': 'qwen2.5:7b',
            'size': '4GB',
            'desc': '阿里通義千問，中文能力優秀'
        },
        {
            'name': 'phi4',
            'size': '8GB',
            'desc': '微軟小型模型，推理能力強'
        },
        {
            'name': 'llama3.3:70b',
            'size': '40GB',
            'desc': '最強性能，需要高配置硬件'
        },
    ]

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("模型名稱", style="cyan", width=20)
    table.add_column("大小", justify="right", style="green", width=10)
    table.add_column("描述", style="yellow", width=40)

    for rec in recommendations:
        table.add_row(rec['name'], rec['size'], rec['desc'])

    console.print(table)

    console.print("\n[bold]下載命令:[/bold]")
    console.print("  ollama pull <模型名稱>")
    console.print("\n[bold]例如:[/bold]")
    console.print("  ollama pull llama3.2")


def batch_download_models(model_names):
    """批量下載模型"""
    console.print(f"\n[bold cyan]批量下載 {len(model_names)} 個模型[/bold cyan]")

    success_count = 0
    failed_models = []

    for i, model_name in enumerate(model_names, 1):
        console.print(f"\n[bold]({i}/{len(model_names)}) 下載: {model_name}[/bold]")

        if pull_model(model_name, show_progress=True):
            success_count += 1
        else:
            failed_models.append(model_name)

        # 短暫等待
        if i < len(model_names):
            time.sleep(1)

    # 顯示結果
    console.print("\n" + "="*60)
    console.print(f"[bold]批量下載完成[/bold]")
    console.print(f"[green]成功: {success_count}/{len(model_names)}[/green]")

    if failed_models:
        console.print(f"[red]失敗的模型: {', '.join(failed_models)}[/red]")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Ollama 模型管理示例[/bold cyan]",
        border_style="cyan"
    ))

    # 1. 列出現有模型
    console.print("\n[bold]示例 1: 列出所有模型[/bold]")
    models = list_models()

    # 2. 推薦模型
    console.print("\n[bold]示例 2: 推薦模型[/bold]")
    recommend_models()

    # 3. 下載模型示例（註釋掉，避免實際下載）
    console.print("\n[bold]示例 3: 下載模型[/bold]")
    console.print("[dim]# 下載小型模型示例（已註釋）[/dim]")
    console.print("[dim]# pull_model('llama3.2:1b')[/dim]")

    # 如果沒有模型，建議下載
    if not models:
        console.print("\n[yellow]建議先下載一個模型:[/yellow]")
        console.print("  python -c \"import ollama; ollama.pull('llama3.2:1b')\"")
    else:
        # 4. 顯示第一個模型的詳情
        console.print("\n[bold]示例 4: 查看模型詳情[/bold]")
        first_model = models[0].get('name', '')
        if first_model:
            show_model_details(first_model)

        # 5. 複製模型示例
        console.print("\n[bold]示例 5: 複製模型[/bold]")
        console.print(f"[dim]# 創建模型別名示例（已註釋）[/dim]")
        console.print(f"[dim]# copy_model('{first_model}', 'my-custom-model')[/dim]")

        # 6. 刪除模型示例
        console.print("\n[bold]示例 6: 刪除模型[/bold]")
        console.print("[dim]# 刪除模型示例（已註釋）[/dim]")
        console.print("[dim]# delete_model('model-to-delete')[/dim]")

    # 7. 批量下載示例
    console.print("\n[bold]示例 7: 批量下載模型[/bold]")
    console.print("[dim]# 批量下載示例（已註釋）[/dim]")
    console.print("[dim]# batch_download_models(['llama3.2:1b', 'mistral'])[/dim]")

    # 完成
    console.print("\n" + "="*60)
    console.print("[bold green]✓ 模型管理示例完成！[/bold green]")
    console.print("\n[cyan]常用命令:[/cyan]")
    console.print("  ollama list              # 列出模型")
    console.print("  ollama pull <model>      # 下載模型")
    console.print("  ollama rm <model>        # 刪除模型")
    console.print("  ollama show <model>      # 查看詳情")


if __name__ == "__main__":
    main()
