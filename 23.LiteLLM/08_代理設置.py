"""
LiteLLM 代理設置範例
===================

本範例展示如何在 LiteLLM 中配置代理服務器。

代理類型：
1. HTTP 代理
2. SOCKS 代理
3. LiteLLM Proxy Server
4. 自定義代理

安裝依賴：
pip install litellm httpx[socks]
"""

import litellm
from litellm import completion
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# ============================================================
# 1. HTTP 代理配置
# ============================================================

HTTP_PROXY_EXAMPLE = '''
import litellm
import os

# 方法 1: 環境變數
os.environ["HTTP_PROXY"] = "http://proxy.example.com:8080"
os.environ["HTTPS_PROXY"] = "http://proxy.example.com:8080"

# 方法 2: 帶認證的代理
os.environ["HTTP_PROXY"] = "http://user:password@proxy.example.com:8080"
os.environ["HTTPS_PROXY"] = "http://user:password@proxy.example.com:8080"

# 使用 LiteLLM
response = litellm.completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello"}]
)
'''


# ============================================================
# 2. SOCKS 代理配置
# ============================================================

SOCKS_PROXY_EXAMPLE = '''
import litellm
import os

# SOCKS5 代理
os.environ["ALL_PROXY"] = "socks5://127.0.0.1:1080"

# 或者使用 SOCKS5h（DNS 也通過代理解析）
os.environ["ALL_PROXY"] = "socks5h://127.0.0.1:1080"

# 帶認證的 SOCKS5
os.environ["ALL_PROXY"] = "socks5://user:password@127.0.0.1:1080"

# 使用
response = litellm.completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello"}]
)
'''


# ============================================================
# 3. LiteLLM Proxy Server
# ============================================================

PROXY_SERVER_CONFIG = '''
# config.yaml - LiteLLM Proxy 配置文件

model_list:
  - model_name: gpt-4
    litellm_params:
      model: gpt-4
      api_key: sk-xxx
  - model_name: gpt-3.5-turbo
    litellm_params:
      model: gpt-3.5-turbo
      api_key: sk-xxx
  - model_name: claude-3-sonnet
    litellm_params:
      model: claude-3-sonnet-20240229
      api_key: sk-ant-xxx

litellm_settings:
  drop_params: True
  set_verbose: True

general_settings:
  master_key: sk-1234  # 代理 API 密鑰
  database_url: postgresql://user:pass@localhost/litellm
'''

START_PROXY_EXAMPLE = '''
# 啟動 LiteLLM Proxy Server

# 方法 1: 命令行
litellm --config config.yaml --port 4000

# 方法 2: Docker
docker run -d \\
  -p 4000:4000 \\
  -v $(pwd)/config.yaml:/app/config.yaml \\
  ghcr.io/berriai/litellm:main-latest \\
  --config /app/config.yaml

# 方法 3: Python
from litellm import proxy_server
proxy_server.start(config="config.yaml", port=4000)
'''

USE_PROXY_EXAMPLE = '''
import litellm

# 使用 LiteLLM Proxy
response = litellm.completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello"}],
    api_base="http://localhost:4000",  # 代理地址
    api_key="sk-1234"  # 代理 API 密鑰
)

# 或者使用 OpenAI SDK
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:4000",
    api_key="sk-1234"
)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello"}]
)
'''


# ============================================================
# 4. 代理配置管理器
# ============================================================

@dataclass
class ProxyConfig:
    """代理配置"""
    type: str  # http, https, socks5
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    no_proxy: Optional[List[str]] = None


class ProxyManager:
    """代理管理器"""

    def __init__(self):
        self.current_proxy: Optional[ProxyConfig] = None
        self.original_env: Dict[str, Optional[str]] = {}

    def _build_proxy_url(self, config: ProxyConfig) -> str:
        """構建代理 URL"""
        if config.username and config.password:
            auth = f"{config.username}:{config.password}@"
        else:
            auth = ""

        return f"{config.type}://{auth}{config.host}:{config.port}"

    def set_proxy(self, config: ProxyConfig):
        """設置代理"""
        # 保存原始環境變數
        for key in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY"]:
            self.original_env[key] = os.environ.get(key)

        # 設置新代理
        proxy_url = self._build_proxy_url(config)

        if config.type in ["http", "https"]:
            os.environ["HTTP_PROXY"] = proxy_url
            os.environ["HTTPS_PROXY"] = proxy_url
        elif config.type.startswith("socks"):
            os.environ["ALL_PROXY"] = proxy_url

        if config.no_proxy:
            os.environ["NO_PROXY"] = ",".join(config.no_proxy)

        self.current_proxy = config
        print(f"代理已設置: {config.type}://{config.host}:{config.port}")

    def clear_proxy(self):
        """清除代理"""
        # 恢復原始環境變數
        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

        self.current_proxy = None
        print("代理已清除")

    def get_current_proxy(self) -> Optional[str]:
        """獲取當前代理"""
        if self.current_proxy:
            return self._build_proxy_url(self.current_proxy)
        return None


# ============================================================
# 5. 自定義代理客戶端
# ============================================================

class ProxiedLLMClient:
    """帶代理的 LLM 客戶端"""

    def __init__(
        self,
        proxy_url: Optional[str] = None,
        litellm_proxy_url: Optional[str] = None,
        litellm_proxy_key: Optional[str] = None
    ):
        self.proxy_url = proxy_url
        self.litellm_proxy_url = litellm_proxy_url
        self.litellm_proxy_key = litellm_proxy_key

    def completion(self, model: str, messages: List[Dict], **kwargs) -> Any:
        """帶代理的完成調用"""
        # 如果使用 LiteLLM Proxy
        if self.litellm_proxy_url:
            kwargs["api_base"] = self.litellm_proxy_url
            kwargs["api_key"] = self.litellm_proxy_key

        # 如果使用網絡代理
        if self.proxy_url:
            os.environ["HTTPS_PROXY"] = self.proxy_url

        return completion(model=model, messages=messages, **kwargs)


# ============================================================
# 6. 代理健康檢查
# ============================================================

class ProxyHealthChecker:
    """代理健康檢查器"""

    def __init__(self, proxy_url: str):
        self.proxy_url = proxy_url

    def check(self) -> Dict[str, Any]:
        """檢查代理健康狀態"""
        import httpx

        result = {
            "proxy_url": self.proxy_url,
            "reachable": False,
            "latency_ms": None,
            "error": None
        }

        try:
            import time
            start = time.time()

            with httpx.Client(proxy=self.proxy_url, timeout=10) as client:
                response = client.get("https://api.openai.com/v1/models")

            latency = (time.time() - start) * 1000
            result["reachable"] = True
            result["latency_ms"] = latency
            result["status_code"] = response.status_code

        except Exception as e:
            result["error"] = str(e)

        return result

    def check_litellm_proxy(self, url: str, api_key: str) -> Dict[str, Any]:
        """檢查 LiteLLM Proxy 健康狀態"""
        import httpx

        result = {
            "proxy_url": url,
            "healthy": False,
            "models": [],
            "error": None
        }

        try:
            headers = {"Authorization": f"Bearer {api_key}"}

            with httpx.Client(timeout=10) as client:
                # 檢查健康端點
                health_response = client.get(f"{url}/health")
                result["healthy"] = health_response.status_code == 200

                # 獲取可用模型
                models_response = client.get(
                    f"{url}/v1/models",
                    headers=headers
                )
                if models_response.status_code == 200:
                    data = models_response.json()
                    result["models"] = [m["id"] for m in data.get("data", [])]

        except Exception as e:
            result["error"] = str(e)

        return result


# ============================================================
# 7. 代理負載均衡
# ============================================================

class ProxyLoadBalancer:
    """代理負載均衡器"""

    def __init__(self, proxies: List[ProxyConfig]):
        self.proxies = proxies
        self.proxy_stats: Dict[str, Dict] = {}
        self.current_index = 0

        for proxy in proxies:
            key = f"{proxy.host}:{proxy.port}"
            self.proxy_stats[key] = {
                "requests": 0,
                "failures": 0,
                "latency_sum": 0
            }

    def get_proxy_key(self, proxy: ProxyConfig) -> str:
        return f"{proxy.host}:{proxy.port}"

    def select_proxy(self, strategy: str = "round_robin") -> ProxyConfig:
        """選擇代理"""
        if strategy == "round_robin":
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            return proxy

        elif strategy == "least_connections":
            return min(
                self.proxies,
                key=lambda p: self.proxy_stats[self.get_proxy_key(p)]["requests"]
            )

        elif strategy == "lowest_latency":
            def avg_latency(p):
                stats = self.proxy_stats[self.get_proxy_key(p)]
                if stats["requests"] == 0:
                    return float('inf')
                return stats["latency_sum"] / stats["requests"]

            return min(self.proxies, key=avg_latency)

        return self.proxies[0]

    def record_request(self, proxy: ProxyConfig, latency: float, success: bool):
        """記錄請求"""
        key = self.get_proxy_key(proxy)
        self.proxy_stats[key]["requests"] += 1
        self.proxy_stats[key]["latency_sum"] += latency
        if not success:
            self.proxy_stats[key]["failures"] += 1

    def get_stats(self) -> Dict[str, Dict]:
        """獲取統計信息"""
        return self.proxy_stats


# ============================================================
# 使用範例
# ============================================================

def example_http_proxy():
    """範例 1: HTTP 代理"""
    print("=" * 50)
    print("範例 1: HTTP 代理配置")
    print("=" * 50)
    print(HTTP_PROXY_EXAMPLE)


def example_socks_proxy():
    """範例 2: SOCKS 代理"""
    print("\n" + "=" * 50)
    print("範例 2: SOCKS 代理配置")
    print("=" * 50)
    print(SOCKS_PROXY_EXAMPLE)


def example_litellm_proxy():
    """範例 3: LiteLLM Proxy Server"""
    print("\n" + "=" * 50)
    print("範例 3: LiteLLM Proxy Server")
    print("=" * 50)
    print("配置文件:")
    print(PROXY_SERVER_CONFIG)
    print("\n啟動代理:")
    print(START_PROXY_EXAMPLE)
    print("\n使用代理:")
    print(USE_PROXY_EXAMPLE)


def example_proxy_manager():
    """範例 4: 代理管理器"""
    print("\n" + "=" * 50)
    print("範例 4: 代理管理器")
    print("=" * 50)

    manager = ProxyManager()

    # 設置代理
    config = ProxyConfig(
        type="http",
        host="proxy.example.com",
        port=8080,
        no_proxy=["localhost", "127.0.0.1"]
    )

    print(f"代理配置: {config}")
    print("\n使用方法:")
    print("  manager.set_proxy(config)  # 設置代理")
    print("  manager.clear_proxy()      # 清除代理")


def example_health_check():
    """範例 5: 健康檢查"""
    print("\n" + "=" * 50)
    print("範例 5: 代理健康檢查")
    print("=" * 50)

    print("""
checker = ProxyHealthChecker("http://proxy.example.com:8080")

# 檢查網絡代理
result = checker.check()
print(f"可達: {result['reachable']}")
print(f"延遲: {result['latency_ms']}ms")

# 檢查 LiteLLM Proxy
result = checker.check_litellm_proxy(
    url="http://localhost:4000",
    api_key="sk-1234"
)
print(f"健康: {result['healthy']}")
print(f"可用模型: {result['models']}")
""")


def example_load_balancer():
    """範例 6: 負載均衡"""
    print("\n" + "=" * 50)
    print("範例 6: 代理負載均衡")
    print("=" * 50)

    proxies = [
        ProxyConfig(type="http", host="proxy1.example.com", port=8080),
        ProxyConfig(type="http", host="proxy2.example.com", port=8080),
        ProxyConfig(type="http", host="proxy3.example.com", port=8080),
    ]

    balancer = ProxyLoadBalancer(proxies)

    print("代理列表:")
    for p in proxies:
        print(f"  - {p.host}:{p.port}")

    print("\n負載均衡策略:")
    print("  - round_robin: 輪詢")
    print("  - least_connections: 最少連接")
    print("  - lowest_latency: 最低延遲")


if __name__ == "__main__":
    print("LiteLLM 代理設置範例\n")
    example_http_proxy()
    example_socks_proxy()
    example_litellm_proxy()
    example_proxy_manager()
    example_health_check()
    example_load_balancer()
