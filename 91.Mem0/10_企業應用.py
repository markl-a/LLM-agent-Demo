"""
Mem0 企業應用示例

本示例展示:
1. 企業級配置
2. 多租戶管理
3. 性能優化
4. 生產部署
"""

from mem0 import Memory
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv
import os
from datetime import datetime

console = Console()
load_dotenv()

def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Mem0 企業應用示例[/bold cyan]\n"
        "[dim]展示企業級部署方案[/dim]",
        border_style="cyan"
    ))
    
    # 企業級配置
    console.print("\n[cyan]1. 企業級配置[/cyan]\n")
    
    config_example = """
config = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": "gpt-4",
            "api_key": os.getenv("OPENAI_API_KEY")
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "qdrant.example.com",
            "port": 6333,
            "api_key": os.getenv("QDRANT_API_KEY")
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-small"
        }
    }
}
"""
    
    console.print(Panel(config_example, border_style="green", title="配置示例"))
    console.print()
    
    # 多租戶架構
    console.print("[cyan]2. 多租戶架構[/cyan]\n")
    
    tenants = [
        {"id": "company_a", "name": "公司A", "users": 100},
        {"id": "company_b", "name": "公司B", "users": 50},
        {"id": "company_c", "name": "公司C", "users": 200}
    ]
    
    table = Table(title="租戶管理")
    table.add_column("租戶ID", style="cyan")
    table.add_column("名稱", style="green")
    table.add_column("用戶數", style="yellow")
    
    for tenant in tenants:
        table.add_row(tenant["id"], tenant["name"], str(tenant["users"]))
    
    console.print(table)
    console.print()
    
    # 性能優化
    console.print("[cyan]3. 性能優化策略[/cyan]\n")
    
    optimizations = [
        "✅ 向量數據庫優化 - 使用Qdrant/Milvus提升搜索速度",
        "✅ 批量操作 - 減少API調用次數",
        "✅ 緩存策略 - Redis緩存熱點記憶",
        "✅ 異步處理 - 非阻塞記憶寫入",
        "✅ 索引優化 - 合理設計索引結構"
    ]
    
    for opt in optimizations:
        console.print(f"  {opt}")
    
    console.print()
    
    # 監控指標
    console.print("[cyan]4. 監控指標[/cyan]\n")
    
    metrics = Table(title="生產監控指標")
    metrics.add_column("指標", style="cyan")
    metrics.add_column("目標值", style="green")
    metrics.add_column("當前值", style="yellow")
    
    metrics.add_row("記憶添加延遲", "< 100ms", "85ms")
    metrics.add_row("記憶搜索延遲", "< 50ms", "42ms")
    metrics.add_row("系統可用性", "> 99.9%", "99.95%")
    metrics.add_row("API成功率", "> 99%", "99.8%")
    
    console.print(metrics)
    console.print()
    
    # 部署檢查清單
    console.print("[cyan]5. 生產部署檢查清單[/cyan]\n")
    
    checklist = [
        "✅ 環境變量配置完成",
        "✅ 向量數據庫已部署",
        "✅ API限流已配置",
        "✅ 監控告警已設置",
        "✅ 備份策略已實施",
        "✅ 安全審計已通過",
        "✅ 性能測試已完成",
        "✅ 文檔已更新"
    ]
    
    for item in checklist:
        console.print(f"  {item}")
    
    console.print()
    console.print("="*60)
    console.print("[bold green]✓ 企業應用示例完成！[/bold green]")
    console.print("\n[cyan]企業部署要點:[/cyan]")
    console.print("  • 高性能: 使用專業向量數據庫")
    console.print("  • 可擴展: 支持多租戶架構")
    console.print("  • 可靠性: 完善的監控和備份")
    console.print("  • 安全性: 嚴格的訪問控制")
    console.print("\n[cyan]下一步:[/cyan]")
    console.print("  1. 根據需求調整配置")
    console.print("  2. 進行壓力測試")
    console.print("  3. 建立監控系統")
    console.print("  4. 準備上線運營")

if __name__ == "__main__":
    main()
