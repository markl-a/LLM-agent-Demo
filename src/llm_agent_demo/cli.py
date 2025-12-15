"""命令行界面工具 - 提供便捷的 CLI 命令來管理和監控 LLM Agent"""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
import json

# 導入內部模組
try:
    from llm_agent_demo import __version__
    from llm_agent_demo.utils.config import get_settings, reload_settings, Settings
    from llm_agent_demo.utils.cost_tracker import CostTracker, PRICING
    from llm_agent_demo.utils.validators import (
        validate_openai_api_key,
        validate_anthropic_api_key,
        mask_sensitive_data,
    )
    from llm_agent_demo.utils.exceptions import APIKeyError, ConfigurationError
except ImportError as e:
    # 如果導入失敗，提供友好的錯誤訊息
    click.echo(f"錯誤: 無法導入必要的模組: {e}", err=True)
    click.echo("請確保已正確安裝專案: pip install -e .", err=True)
    sys.exit(1)

console = Console()


# ==================== 主命令組 ====================
@click.group()
@click.version_option(version=__version__, prog_name="llm-agent-demo")
@click.pass_context
def cli(ctx):
    """
    🤖 LLM Agent Demo - 多框架 LLM Agent 開發工具

    支援的框架: LangChain, LlamaIndex, AutoGen, CrewAI, MetaGPT

    使用 --help 查看各子命令的詳細說明
    """
    ctx.ensure_object(dict)


# ==================== config 命令 ====================
@cli.command()
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["openai", "anthropic", "google", "groq", "all"], case_sensitive=False),
    default="all",
    help="指定要查看的 LLM 提供商配置",
)
@click.option(
    "--show-keys",
    "-s",
    is_flag=True,
    help="顯示 API 金鑰（默認會遮蔽）",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json"], case_sensitive=False),
    default="table",
    help="輸出格式",
)
@click.option(
    "--reload",
    "-r",
    is_flag=True,
    help="重新載入配置（清除快取）",
)
def config(provider: str, show_keys: bool, format: str, reload: bool):
    """
    查看當前配置和環境變數

    範例:
      llm-agent config                    # 查看所有配置
      llm-agent config -p openai          # 只查看 OpenAI 配置
      llm-agent config --show-keys        # 顯示完整的 API 金鑰
      llm-agent config -f json            # 以 JSON 格式輸出
      llm-agent config --reload           # 重新載入配置
    """
    try:
        # 重新載入配置（如果需要）
        if reload:
            settings = reload_settings()
            console.print("[green]✓[/green] 配置已重新載入", style="bold")
        else:
            settings = get_settings()

        # JSON 格式輸出
        if format == "json":
            config_data = _get_config_data(settings, provider, show_keys)
            console.print_json(data=config_data)
            return

        # 表格格式輸出
        console.print(
            Panel.fit(
                "📋 LLM Agent Demo 配置信息",
                style="bold cyan",
            )
        )

        # 應用程式設定
        _display_app_settings(settings)

        # LLM 提供商配置
        if provider.lower() == "all":
            for prov in ["openai", "anthropic", "google", "groq"]:
                _display_provider_config(settings, prov, show_keys)
        else:
            _display_provider_config(settings, provider, show_keys)

        # RAG 設定
        _display_rag_settings(settings)

        # 向量數據庫設定
        _display_vector_db_settings(settings)

    except Exception as e:
        console.print(f"[red]✗[/red] 錯誤: {e}", style="bold red")
        sys.exit(1)


def _get_config_data(settings: Settings, provider: str, show_keys: bool) -> dict:
    """獲取配置數據（用於 JSON 輸出）"""
    config = {
        "app": {
            "environment": settings.app_env,
            "debug": settings.debug,
            "log_level": settings.log_level,
        },
        "llm_providers": {},
        "rag": {
            "chunk_size": settings.chunk_size,
            "chunk_overlap": settings.chunk_overlap,
            "top_k": settings.top_k,
            "embedding_model": settings.embedding_model,
        },
    }

    providers = ["openai", "anthropic", "google", "groq"] if provider == "all" else [provider]

    for prov in providers:
        key_field = f"{prov}_api_key"
        model_field = f"{prov}_model"
        api_key = getattr(settings, key_field, None)

        config["llm_providers"][prov] = {
            "api_key": api_key if show_keys else mask_sensitive_data(api_key or ""),
            "model": getattr(settings, model_field, ""),
            "configured": bool(api_key),
        }

    return config


def _display_app_settings(settings: Settings):
    """顯示應用程式設定"""
    table = Table(title="應用程式設定", show_header=True, header_style="bold magenta")
    table.add_column("設定項", style="cyan", width=25)
    table.add_column("值", style="green")

    table.add_row("環境", settings.app_env)
    table.add_row("除錯模式", "✓ 啟用" if settings.debug else "✗ 禁用")
    table.add_row("日誌級別", settings.log_level)
    table.add_row("最大重試次數", str(settings.max_retries))
    table.add_row("請求超時", f"{settings.timeout} 秒")
    table.add_row("成本追蹤", "✓ 啟用" if settings.enable_cost_tracking else "✗ 禁用")

    console.print(table)
    console.print()


def _display_provider_config(settings: Settings, provider: str, show_keys: bool):
    """顯示 LLM 提供商配置"""
    provider_upper = provider.upper()
    key_field = f"{provider}_api_key"
    model_field = f"{provider}_model"

    api_key = getattr(settings, key_field, None)
    model = getattr(settings, model_field, "")

    # 構建表格
    table = Table(
        title=f"{provider_upper} 配置",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("設定項", style="cyan", width=25)
    table.add_column("值", style="green")

    # API 金鑰狀態
    if api_key:
        key_display = api_key if show_keys else mask_sensitive_data(api_key)
        table.add_row("API 金鑰", f"[green]✓[/green] {key_display}")
    else:
        table.add_row("API 金鑰", "[red]✗ 未配置[/red]")

    table.add_row("預設模型", model)

    # OpenAI 特殊配置
    if provider == "openai":
        table.add_row("API Base", settings.openai_api_base or "")

    console.print(table)
    console.print()


def _display_rag_settings(settings: Settings):
    """顯示 RAG 設定"""
    table = Table(title="RAG 設定", show_header=True, header_style="bold magenta")
    table.add_column("設定項", style="cyan", width=25)
    table.add_column("值", style="green")

    table.add_row("分塊大小", str(settings.chunk_size))
    table.add_row("分塊重疊", str(settings.chunk_overlap))
    table.add_row("檢索數量 (Top-K)", str(settings.top_k))
    table.add_row("嵌入模型", settings.embedding_model)
    table.add_row("最大 Token 數", str(settings.max_tokens))
    table.add_row("生成溫度", str(settings.temperature))

    console.print(table)
    console.print()


def _display_vector_db_settings(settings: Settings):
    """顯示向量數據庫設定"""
    table = Table(title="向量數據庫設定", show_header=True, header_style="bold magenta")
    table.add_column("數據庫", style="cyan", width=25)
    table.add_column("配置狀態", style="green")

    # Chroma
    table.add_row("Chroma", f"[green]✓[/green] {settings.chroma_persist_directory}")

    # Pinecone
    if settings.pinecone_api_key:
        table.add_row(
            "Pinecone",
            f"[green]✓[/green] 環境: {settings.pinecone_environment or 'N/A'}",
        )
    else:
        table.add_row("Pinecone", "[yellow]⚠[/yellow] 未配置")

    # Qdrant
    if settings.qdrant_url:
        status = "[green]✓[/green]" if settings.qdrant_api_key else "[yellow]⚠[/yellow]"
        table.add_row("Qdrant", f"{status} {settings.qdrant_url}")
    else:
        table.add_row("Qdrant", "[yellow]⚠[/yellow] 未配置")

    console.print(table)
    console.print()


# ==================== cost 命令 ====================
@cli.command()
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True),
    help="成本追蹤記錄文件路徑",
)
@click.option(
    "--model",
    "-m",
    help="只顯示特定模型的統計",
)
@click.option(
    "--format",
    type=click.Choice(["table", "json"], case_sensitive=False),
    default="table",
    help="輸出格式",
)
@click.option(
    "--pricing",
    "-p",
    is_flag=True,
    help="顯示價格表",
)
def cost(file: Optional[str], model: Optional[str], format: str, pricing: bool):
    """
    查看 API 成本統計

    範例:
      llm-agent cost                      # 查看成本摘要（如果有記錄文件）
      llm-agent cost -f usage.json        # 從指定文件載入成本記錄
      llm-agent cost -m gpt-4o            # 只顯示 gpt-4o 的統計
      llm-agent cost --pricing            # 顯示價格表
      llm-agent cost -f usage.json --format json  # 以 JSON 格式輸出
    """
    try:
        # 顯示價格表
        if pricing:
            _display_pricing_table()
            return

        # 載入成本追蹤器
        tracker = CostTracker(save_path=file)

        if not tracker.usage_history:
            console.print(
                "[yellow]⚠[/yellow] 沒有找到使用記錄",
                style="bold yellow",
            )
            if not file:
                console.print(
                    "\n提示: 使用 -f 選項指定記錄文件，例如:\n"
                    "  llm-agent cost -f ./cost_usage.json"
                )
            return

        # 獲取摘要
        summary = tracker.get_summary()

        # 過濾特定模型
        if model:
            if model not in summary["models"]:
                console.print(
                    f"[red]✗[/red] 找不到模型 '{model}' 的記錄",
                    style="bold red",
                )
                console.print(f"可用的模型: {', '.join(summary['models'].keys())}")
                return
            summary["models"] = {model: summary["models"][model]}

        # JSON 格式輸出
        if format == "json":
            console.print_json(data=summary)
            return

        # 表格格式輸出
        _display_cost_summary(summary)

    except Exception as e:
        console.print(f"[red]✗[/red] 錯誤: {e}", style="bold red")
        sys.exit(1)


def _display_pricing_table():
    """顯示價格表"""
    console.print(
        Panel.fit(
            "💰 LLM API 價格表 (USD/1K tokens)",
            style="bold cyan",
        )
    )

    # 按提供商分組
    providers = {
        "OpenAI": [],
        "Anthropic": [],
        "Google": [],
        "Groq": [],
        "Embeddings": [],
    }

    for model_name, prices in PRICING.items():
        if model_name.startswith("gpt-"):
            providers["OpenAI"].append((model_name, prices))
        elif model_name.startswith("claude-"):
            providers["Anthropic"].append((model_name, prices))
        elif model_name.startswith("gemini-"):
            providers["Google"].append((model_name, prices))
        elif "llama" in model_name or "mixtral" in model_name:
            providers["Groq"].append((model_name, prices))
        elif "embedding" in model_name:
            providers["Embeddings"].append((model_name, prices))

    for provider_name, models in providers.items():
        if not models:
            continue

        table = Table(title=provider_name, show_header=True, header_style="bold magenta")
        table.add_column("模型", style="cyan", width=35)
        table.add_column("輸入價格", style="green", justify="right")
        table.add_column("輸出價格", style="yellow", justify="right")

        for model_name, prices in sorted(models):
            table.add_row(
                model_name,
                f"${prices['prompt']:.6f}",
                f"${prices['completion']:.6f}",
            )

        console.print(table)
        console.print()


def _display_cost_summary(summary: dict):
    """顯示成本摘要"""
    console.print(
        Panel.fit(
            "💰 API 成本統計",
            style="bold cyan",
        )
    )

    # 總覽表格
    overview_table = Table(show_header=True, header_style="bold magenta")
    overview_table.add_column("項目", style="cyan", width=25)
    overview_table.add_column("數值", style="green", justify="right")

    overview_table.add_row("總請求次數", f"{summary['total_requests']:,}")
    overview_table.add_row(
        "總 Token 數",
        f"{summary['total_tokens']['total_tokens']:,}",
    )
    overview_table.add_row(
        "  └─ 輸入",
        f"{summary['total_tokens']['prompt_tokens']:,}",
    )
    overview_table.add_row(
        "  └─ 輸出",
        f"{summary['total_tokens']['completion_tokens']:,}",
    )
    overview_table.add_row(
        "總成本",
        f"[bold green]${summary['total_cost']:.6f}[/bold green]",
    )

    console.print(overview_table)
    console.print()

    # 按模型統計
    if summary["models"]:
        model_table = Table(
            title="按模型統計",
            show_header=True,
            header_style="bold magenta",
        )
        model_table.add_column("模型", style="cyan", width=35)
        model_table.add_column("請求次數", style="blue", justify="right")
        model_table.add_column("Token 數", style="yellow", justify="right")
        model_table.add_column("成本", style="green", justify="right")

        for model_name, stats in sorted(
            summary["models"].items(),
            key=lambda x: x[1]["cost"],
            reverse=True,
        ):
            model_table.add_row(
                model_name,
                f"{stats['count']:,}",
                f"{stats['tokens']:,}",
                f"${stats['cost']:.6f}",
            )

        console.print(model_table)


# ==================== validate 命令 ====================
@cli.command()
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["openai", "anthropic", "google", "groq", "all"], case_sensitive=False),
    default="all",
    help="指定要驗證的提供商",
)
@click.option(
    "--fix",
    is_flag=True,
    help="嘗試自動修復常見問題（例如移除空格）",
)
def validate(provider: str, fix: bool):
    """
    驗證 API 金鑰配置

    檢查 API 金鑰是否正確配置並符合格式要求。

    範例:
      llm-agent validate              # 驗證所有提供商的 API 金鑰
      llm-agent validate -p openai    # 只驗證 OpenAI API 金鑰
      llm-agent validate --fix        # 嘗試自動修復問題
    """
    try:
        settings = get_settings()

        console.print(
            Panel.fit(
                "🔑 API 金鑰驗證",
                style="bold cyan",
            )
        )

        providers = ["openai", "anthropic", "google", "groq"] if provider == "all" else [provider]

        results = []
        for prov in providers:
            result = _validate_provider_key(settings, prov, fix)
            results.append(result)

        # 顯示結果
        _display_validation_results(results)

        # 如果有任何驗證失敗，退出碼為 1
        if any(not r["valid"] for r in results):
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]✗[/red] 錯誤: {e}", style="bold red")
        sys.exit(1)


def _validate_provider_key(settings: Settings, provider: str, fix: bool) -> dict:
    """驗證單個提供商的 API 金鑰"""
    provider_upper = provider.upper()
    key_field = f"{provider}_api_key"
    api_key = getattr(settings, key_field, None)

    result = {
        "provider": provider_upper,
        "valid": False,
        "message": "",
        "details": [],
    }

    if not api_key:
        result["message"] = "未配置"
        result["details"].append(f"請設定環境變數 {provider.upper()}_API_KEY")
        return result

    try:
        # 應用修復（如果需要）
        if fix:
            api_key = api_key.strip()

        # 驗證
        if provider == "openai":
            validate_openai_api_key(api_key)
        elif provider == "anthropic":
            validate_anthropic_api_key(api_key)
        else:
            # Google 和 Groq 使用通用驗證
            from llm_agent_demo.utils.validators import validate_api_key

            validate_api_key(api_key, provider_upper)

        result["valid"] = True
        result["message"] = "驗證通過"
        result["details"].append(f"金鑰長度: {len(api_key)} 字符")

        # 顯示前綴（用於確認）
        prefix_len = 10 if len(api_key) >= 10 else len(api_key)
        result["details"].append(f"金鑰前綴: {api_key[:prefix_len]}...")

    except APIKeyError as e:
        result["message"] = "驗證失敗"
        result["details"].append(str(e))
    except Exception as e:
        result["message"] = "驗證錯誤"
        result["details"].append(str(e))

    return result


def _display_validation_results(results: list):
    """顯示驗證結果"""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("提供商", style="cyan", width=15)
    table.add_column("狀態", style="bold", width=12)
    table.add_column("詳情", style="dim")

    for result in results:
        status = "[green]✓ 通過[/green]" if result["valid"] else "[red]✗ 失敗[/red]"
        details = "\n".join(result["details"]) if result["details"] else result["message"]

        table.add_row(result["provider"], status, details)

    console.print(table)


# ==================== 入口點 ====================
def main():
    """CLI 主入口點"""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠[/yellow] 操作已取消", style="bold yellow")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]✗[/red] 未預期的錯誤: {e}", style="bold red")
        sys.exit(1)


if __name__ == "__main__":
    main()
