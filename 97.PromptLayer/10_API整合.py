"""
PromptLayer API 整合示例

本示例展示：
1. REST API 使用
2. 高級功能
3. 自定義整合
4. 最佳實踐
"""

import os
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


def rest_api_examples():
    """REST API 示例"""
    console.print("\n[cyan]REST API 使用[/cyan]\n")

    code = """import requests

API_BASE = "https://api.promptlayer.com/rest"
API_KEY = os.getenv("PROMPTLAYER_API_KEY")

# 1. 獲取請求列表
def get_requests(limit=10):
    url = f"{API_BASE}/get-requests"
    params = {"api_key": API_KEY, "limit": limit}
    return requests.get(url, params=params).json()

# 2. 獲取特定請求
def get_request(request_id):
    url = f"{API_BASE}/get-request/{request_id}"
    params = {"api_key": API_KEY}
    return requests.get(url, params=params).json()

# 3. 搜索請求
def search_requests(tags=None, template_name=None):
    url = f"{API_BASE}/search-requests"
    data = {
        "api_key": API_KEY,
        "tags": tags,
        "template_name": template_name
    }
    return requests.post(url, json=data).json()

# 4. 評分請求
def score_request(request_id, score):
    url = f"{API_BASE}/track-score"
    data = {
        "api_key": API_KEY,
        "request_id": request_id,
        "score": score
    }
    return requests.post(url, json=data).json()

# 使用示例
requests_list = get_requests(limit=5)
print(f"獲取了 {len(requests_list)} 個請求")
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def best_practices():
    """最佳實踐"""
    console.print("[cyan]API 整合最佳實踐[/cyan]\n")

    practices = """1. 認證安全
   • 使用環境變量存儲 API Key
   • 不要在代碼中硬編碼
   • 定期輪換密鑰

2. 錯誤處理
   • 實施重試邏輯
   • 處理速率限制
   • 記錄錯誤日誌

3. 性能優化
   • 批量操作減少請求數
   • 使用緩存
   • 異步處理

4. 數據管理
   • 定期清理舊數據
   • 導出重要數據
   • 備份關鍵信息

5. 監控和告警
   • 監控 API 調用
   • 設置使用量告警
   • 追蹤異常

6. 文檔和測試
   • 記錄整合代碼
   • 編寫單元測試
   • 維護更新日誌"""

    console.print(Panel(practices, border_style="cyan"))
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]PromptLayer API 整合示例[/bold cyan]\n"
        "[dim]學習高級 API 使用[/dim]",
        border_style="cyan"
    ))

    rest_api_examples()
    best_practices()

    console.print("="*60)
    console.print("[bold green]✓ 所有 PromptLayer 示例完成！[/bold green]\n")
    console.print("[cyan]恭喜！您已掌握 PromptLayer 的核心功能！[/cyan]")


if __name__ == "__main__":
    main()
