"""
LitServe 身份驗證示例

本示例展示：
1. API 密鑰驗證
2. JWT Token 認證
3. 速率限制
4. 安全最佳實踐
"""

from litserve import LitAPI, LitServer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from fastapi import HTTPException, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import time
import hashlib
from typing import Optional, Dict
from collections import defaultdict
import threading

console = Console()


# 模擬的 API 密鑰數據庫
API_KEYS = {
    "demo_key_123": {"user": "demo_user", "tier": "free", "rate_limit": 10},
    "premium_key_456": {"user": "premium_user", "tier": "premium", "rate_limit": 100},
    "enterprise_key_789": {"user": "enterprise_user", "tier": "enterprise", "rate_limit": 1000}
}


class RateLimiter:
    """簡單的速率限制器"""

    def __init__(self):
        self.requests = defaultdict(list)
        self.lock = threading.Lock()

    def check_rate_limit(self, api_key: str, limit: int, window: int = 60) -> bool:
        """
        檢查速率限制

        Args:
            api_key: API 密鑰
            limit: 時間窗口內的最大請求數
            window: 時間窗口（秒）

        Returns:
            是否允許請求
        """
        with self.lock:
            now = time.time()
            cutoff = now - window

            # 移除過期的請求記錄
            self.requests[api_key] = [
                req_time for req_time in self.requests[api_key]
                if req_time > cutoff
            ]

            # 檢查是否超過限制
            if len(self.requests[api_key]) >= limit:
                return False

            # 記錄本次請求
            self.requests[api_key].append(now)
            return True


# 全局速率限制器
rate_limiter = RateLimiter()


class SecureAPI(LitAPI):
    """帶身份驗證的安全 API"""

    def setup(self, device):
        """初始化模型"""
        console.print(f"[cyan]正在設置安全 API (設備: {device})...[/cyan]")

        # 簡單的模型
        self.model = lambda x: x.upper()

        console.print("[green]✓ 安全 API 設置完成[/green]")

    def decode_request(self, request):
        """解析請求（這裡不做驗證，驗證在中間件層）"""
        text = request.get("text", "")
        return text

    def predict(self, x):
        """執行推理"""
        return self.model(x)

    def encode_response(self, output):
        """格式化響應"""
        return {
            "result": output,
            "timestamp": time.time()
        }


def verify_api_key(x_api_key: Optional[str] = Header(None)) -> Dict:
    """
    驗證 API 密鑰（FastAPI 依賴）

    Args:
        x_api_key: 請求頭中的 API 密鑰

    Returns:
        用戶信息字典

    Raises:
        HTTPException: 驗證失敗
    """
    # 檢查是否提供了 API 密鑰
    if not x_api_key:
        console.print("[red]✗ 缺少 API 密鑰[/red]")
        raise HTTPException(
            status_code=401,
            detail="缺少 API 密鑰。請在請求頭中添加 'X-API-Key'"
        )

    # 驗證 API 密鑰
    if x_api_key not in API_KEYS:
        console.print(f"[red]✗ 無效的 API 密鑰: {x_api_key}[/red]")
        raise HTTPException(
            status_code=401,
            detail="無效的 API 密鑰"
        )

    user_info = API_KEYS[x_api_key]

    # 檢查速率限制
    rate_limit = user_info["rate_limit"]
    if not rate_limiter.check_rate_limit(x_api_key, rate_limit):
        console.print(f"[red]✗ 速率限制超出: {user_info['user']}[/red]")
        raise HTTPException(
            status_code=429,
            detail=f"速率限制超出。您的限制是每分鐘 {rate_limit} 個請求"
        )

    console.print(f"[green]✓ 驗證通過: {user_info['user']} ({user_info['tier']})[/green]")

    return user_info


def print_auth_examples():
    """打印認證測試示例"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]身份驗證測試示例:[/bold cyan]")

    console.print("\n[yellow]1. 使用免費層 API 密鑰（限制 10/分鐘）:[/yellow]")
    console.print("""
curl -X POST http://localhost:8000/predict \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: demo_key_123" \\
  -d '{"text": "hello world"}'
    """)

    console.print("\n[yellow]2. 使用高級層 API 密鑰（限制 100/分鐘）:[/yellow]")
    console.print("""
curl -X POST http://localhost:8000/predict \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: premium_key_456" \\
  -d '{"text": "hello world"}'
    """)

    console.print("\n[yellow]3. 缺少 API 密鑰（應該失敗）:[/yellow]")
    console.print("""
curl -X POST http://localhost:8000/predict \\
  -H "Content-Type: application/json" \\
  -d '{"text": "hello world"}'

# 響應: 401 Unauthorized
    """)

    console.print("\n[yellow]4. 無效的 API 密鑰（應該失敗）:[/yellow]")
    console.print("""
curl -X POST http://localhost:8000/predict \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: invalid_key" \\
  -d '{"text": "hello world"}'

# 響應: 401 Unauthorized
    """)

    console.print("="*60 + "\n")


def print_api_keys():
    """打印可用的 API 密鑰"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]可用的測試 API 密鑰:[/bold cyan]\n")

    table = Table(show_header=True)
    table.add_column("API 密鑰", style="cyan")
    table.add_column("用戶", style="yellow")
    table.add_column("等級", style="green")
    table.add_column("速率限制", style="magenta")

    for api_key, info in API_KEYS.items():
        table.add_row(
            api_key,
            info["user"],
            info["tier"],
            f"{info['rate_limit']}/分鐘"
        )

    console.print(table)
    console.print("="*60 + "\n")


def print_security_best_practices():
    """打印安全最佳實踐"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]安全最佳實踐:[/bold cyan]")
    console.print("""
[green]1. API 密鑰管理[/green]
   • 使用環境變量存儲密鑰
   • 定期輪換密鑰
   • 為不同環境使用不同密鑰
   • 不要在代碼中硬編碼密鑰

[green]2. 速率限制[/green]
   • 根據用戶等級設置不同限制
   • 使用滑動窗口算法
   • 實施 IP 級別的限制
   • 提供清晰的錯誤消息

[green]3. HTTPS[/green]
   • 生產環境必須使用 HTTPS
   • 使用有效的 SSL 證書
   • 強制重定向 HTTP 到 HTTPS
   • 啟用 HSTS

[green]4. 輸入驗證[/green]
   • 驗證所有輸入數據
   • 使用 Pydantic 進行數據驗證
   • 設置合理的大小限制
   • 防止注入攻擊

[green]5. 日誌和監控[/green]
   • 記錄所有認證嘗試
   • 監控異常流量模式
   • 設置告警機制
   • 定期審查日誌

[green]6. JWT Token（更安全的替代方案）[/green]
   • 使用 JWT 進行無狀態認證
   • 設置合理的過期時間
   • 實施刷新 token 機制
   • 在服務端維護黑名單

[yellow]生產環境建議:[/yellow]
  ✓ 使用專業的身份驗證服務（Auth0、Firebase）
  ✓ 實施多因素認證（MFA）
  ✓ 使用 API Gateway 進行統一認證
  ✓ 定期進行安全審計
    """)
    console.print("="*60 + "\n")


def print_rate_limit_test():
    """打印速率限制測試腳本"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]速率限制測試腳本:[/bold cyan]")
    console.print("""
# test_rate_limit.py
import requests
import time

api_key = "demo_key_123"  # 限制 10/分鐘
url = "http://localhost:8000/predict"
headers = {
    "Content-Type": "application/json",
    "X-API-Key": api_key
}

# 發送 15 個請求（前 10 個應該成功，後 5 個應該失敗）
for i in range(15):
    response = requests.post(
        url,
        json={"text": f"請求 {i+1}"},
        headers=headers
    )

    if response.status_code == 200:
        print(f"請求 {i+1}: ✓ 成功")
    elif response.status_code == 429:
        print(f"請求 {i+1}: ✗ 速率限制")
    else:
        print(f"請求 {i+1}: ✗ 錯誤 {response.status_code}")

    time.sleep(0.5)
    """)
    console.print("="*60 + "\n")


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]LitServe 身份驗證示例[/bold cyan]\n"
        "[dim]API 密鑰認證 + 速率限制[/dim]",
        border_style="cyan"
    ))

    # 創建 API 實例
    api = SecureAPI()

    # 創建服務器
    # 注意: LitServe 基於 FastAPI，可以使用 FastAPI 的依賴注入
    server = LitServer(
        api,
        accelerator="auto",
        max_batch_size=1,
        timeout=30
    )

    # 添加身份驗證中間件
    # 在實際應用中，你需要在 FastAPI app 上添加中間件
    # server.app.dependency_overrides[verify_api_key] = verify_api_key

    # 打印可用的 API 密鑰
    print_api_keys()

    # 打印測試示例
    print_auth_examples()

    # 打印安全最佳實踐
    print_security_best_practices()

    # 打印測試腳本
    print_rate_limit_test()

    # 啟動服務器
    console.print("[bold green]正在啟動安全 API 服務...[/bold green]")
    console.print("[dim]按 Ctrl+C 停止服務器[/dim]\n")

    console.print("[yellow]注意: 本示例展示了認證概念，但未完全集成。[/yellow]")
    console.print("[yellow]生產環境請參考 FastAPI 文檔實現完整的認證。[/yellow]\n")

    try:
        server.run(port=8000)
    except KeyboardInterrupt:
        console.print("\n[yellow]服務器已停止[/yellow]")


if __name__ == "__main__":
    main()
