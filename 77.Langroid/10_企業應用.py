"""
Langroid 企業應用 - 生產級應用開發

這個示例展示：
1. 企業級架構設計
2. 安全性考慮
3. 性能優化
4. 監控和日誌

將 Langroid 應用於企業環境的最佳實踐。
"""

from rich.console import Console
from rich.panel import Panel

console = Console()


def enterprise_architecture():
    """企業級架構"""
    console.print(Panel("[bold cyan]企業級架構設計[/bold cyan]"))

    console.print("""
[yellow]企業應用架構層次：[/yellow]

1. [cyan]表示層[/cyan]
   - API 接口
   - Web UI
   - 移動應用

2. [cyan]業務邏輯層[/cyan]
   - Agent 協調
   - 任務編排
   - 業務規則

3. [cyan]數據訪問層[/cyan]
   - 向量數據庫
   - 關係數據庫
   - 緩存層

4. [cyan]基礎設施層[/cyan]
   - 認證授權
   - 日誌監控
   - 配置管理

[yellow]架構示例：[/yellow]
    """)

    arch_code = '''
from dataclasses import dataclass
from typing import Optional
import langroid as lr

@dataclass
class EnterpriseConfig:
    """企業配置"""
    # LLM 配置
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"

    # 數據庫配置
    vecdb_type: str = "qdrant"
    vecdb_url: Optional[str] = None

    # 安全配置
    api_key_encryption: bool = True
    rate_limiting: bool = True

    # 監控配置
    logging_level: str = "INFO"
    metrics_enabled: bool = True

class EnterpriseAgent:
    """企業級 Agent 系統"""

    def __init__(self, config: EnterpriseConfig):
        self.config = config
        self._setup_agents()
        self._setup_monitoring()
        self._setup_security()

    def _setup_agents(self):
        """設置 Agents"""
        # 主 Agent
        self.main_agent = lr.ChatAgent(...)

        # 專家 Agents
        self.experts = {
            "tech": lr.ChatAgent(...),
            "business": lr.ChatAgent(...),
            "legal": lr.ChatAgent(...),
        }

    def _setup_monitoring(self):
        """設置監控"""
        # 設置日誌
        # 設置指標收集
        # 設置告警
        pass

    def _setup_security(self):
        """設置安全"""
        # API 密鑰管理
        # 訪問控制
        # 數據加密
        pass

    def process_request(self, request: dict) -> dict:
        """處理請求"""
        # 1. 驗證請求
        self._validate_request(request)

        # 2. 路由到合適的 Agent
        agent = self._route_request(request)

        # 3. 處理
        result = self._process(agent, request)

        # 4. 記錄和監控
        self._log_transaction(request, result)

        return result
    '''

    console.print(Panel(arch_code, border_style="blue"))


def security_best_practices():
    """安全最佳實踐"""
    console.print(Panel("[bold cyan]安全最佳實踐[/bold cyan]"))

    console.print("""
[yellow]企業應用安全要點：[/yellow]

1. [cyan]API 密鑰管理[/cyan]
   - 使用環境變量或密鑰管理服務
   - 加密存儲
   - 定期輪換

2. [cyan]輸入驗證[/cyan]
   - 驗證所有用戶輸入
   - 防止注入攻擊
   - 限制輸入長度

3. [cyan]輸出過濾[/cyan]
   - 過濾敏感信息
   - 防止數據洩露
   - 內容審核

4. [cyan]訪問控制[/cyan]
   - 基於角色的訪問控制（RBAC）
   - API 限流
   - 審計日誌

[yellow]安全實現示例：[/yellow]
    """)

    security_code = '''
import os
from functools import wraps

class SecurityManager:
    """安全管理器"""

    def __init__(self):
        self.api_keys = self._load_encrypted_keys()
        self.rate_limiter = RateLimiter()

    @staticmethod
    def validate_input(text: str) -> bool:
        """驗證輸入"""
        # 長度檢查
        if len(text) > 10000:
            return False

        # 內容檢查
        forbidden_patterns = [
            "DELETE FROM",
            "<script>",
            # 更多模式...
        ]

        for pattern in forbidden_patterns:
            if pattern.lower() in text.lower():
                return False

        return True

    @staticmethod
    def sanitize_output(text: str) -> str:
        """清理輸出"""
        # 移除敏感信息
        sensitive_patterns = [
            r"\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b",  # Email
            r"\\b\\d{3}-\\d{2}-\\d{4}\\b",  # SSN
            # 更多模式...
        ]

        cleaned = text
        for pattern in sensitive_patterns:
            cleaned = re.sub(pattern, "[REDACTED]", cleaned)

        return cleaned

    def check_rate_limit(self, user_id: str) -> bool:
        """檢查速率限制"""
        return self.rate_limiter.check(user_id)

# 使用裝飾器保護 Agent
def secure_agent(func):
    @wraps(func)
    def wrapper(self, message: str):
        # 驗證輸入
        if not SecurityManager.validate_input(message):
            raise ValueError("Invalid input")

        # 調用原函數
        result = func(self, message)

        # 清理輸出
        result = SecurityManager.sanitize_output(result)

        return result

    return wrapper

class SecureAgent(lr.ChatAgent):
    @secure_agent
    def llm_response(self, message: str):
        return super().llm_response(message)
    '''

    console.print(Panel(security_code, border_style="blue"))


def performance_optimization():
    """性能優化"""
    console.print(Panel("[bold cyan]性能優化策略[/bold cyan]"))

    console.print("""
[yellow]企業應用性能優化：[/yellow]

1. [cyan]緩存策略[/cyan]
   - 緩存 LLM 響應
   - 緩存向量檢索結果
   - 使用 Redis 等緩存系統

2. [cyan]批處理[/cyan]
   - 批量處理請求
   - 減少 API 調用
   - 提高吞吐量

3. [cyan]異步處理[/cyan]
   - 使用異步 IO
   - 並行處理獨立任務
   - 任務隊列

4. [cyan]資源管理[/cyan]
   - 連接池
   - 限制並發數
   - 資源回收

[yellow]性能優化示例：[/yellow]
    """)

    perf_code = '''
from functools import lru_cache
import redis
import asyncio

class PerformanceOptimizedAgent:
    """性能優化的 Agent"""

    def __init__(self):
        self.agent = lr.ChatAgent(...)
        self.redis_cache = redis.Redis(...)
        self.request_queue = asyncio.Queue()

    @lru_cache(maxsize=1000)
    def cached_response(self, message: str) -> str:
        """緩存響應"""
        # 檢查 Redis 緩存
        cached = self.redis_cache.get(f"response:{message}")
        if cached:
            return cached.decode()

        # 調用 Agent
        response = self.agent.llm_response(message)

        # 存入緩存
        self.redis_cache.setex(
            f"response:{message}",
            3600,  # 1小時過期
            response.content
        )

        return response.content

    async def batch_process(self, messages: list) -> list:
        """批處理"""
        tasks = [
            self.async_process(msg)
            for msg in messages
        ]

        results = await asyncio.gather(*tasks)
        return results

    async def async_process(self, message: str):
        """異步處理單個消息"""
        # 異步調用 LLM
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self.cached_response,
            message
        )
        return result

# 使用
agent = PerformanceOptimizedAgent()

# 單個請求（使用緩存）
response = agent.cached_response("你好")

# 批量請求（並行處理）
messages = ["問題1", "問題2", "問題3"]
results = asyncio.run(agent.batch_process(messages))
    '''

    console.print(Panel(perf_code, border_style="blue"))


def monitoring_logging():
    """監控和日誌"""
    console.print(Panel("[bold cyan]監控和日誌[/bold cyan]"))

    console.print("""
[yellow]企業級監控和日誌：[/yellow]

1. [cyan]結構化日誌[/cyan]
   - JSON 格式日誌
   - 包含上下文信息
   - 便於查詢和分析

2. [cyan]指標收集[/cyan]
   - 請求量、延遲
   - 錯誤率
   - Token 使用量
   - 成本追蹤

3. [cyan]告警機制[/cyan]
   - 異常檢測
   - 閾值告警
   - 自動通知

4. [cyan]可視化儀表板[/cyan]
   - 實時監控
   - 趨勢分析
   - 性能報表

[yellow]監控實現：[/yellow]
    """)

    monitoring_code = '''
import structlog
from prometheus_client import Counter, Histogram
import time

# 配置結構化日誌
logger = structlog.get_logger()

# Prometheus 指標
request_counter = Counter(
    'agent_requests_total',
    'Total agent requests',
    ['agent_name', 'status']
)

request_duration = Histogram(
    'agent_request_duration_seconds',
    'Agent request duration'
)

class MonitoredAgent:
    """帶監控的 Agent"""

    def __init__(self, agent_name: str):
        self.agent = lr.ChatAgent(...)
        self.agent_name = agent_name

    def process(self, message: str) -> str:
        """處理請求（帶監控）"""
        start_time = time.time()

        logger.info(
            "request_start",
            agent=self.agent_name,
            message_length=len(message)
        )

        try:
            # 處理
            result = self.agent.llm_response(message)

            # 記錄成功
            duration = time.time() - start_time
            request_counter.labels(
                agent_name=self.agent_name,
                status="success"
            ).inc()

            request_duration.observe(duration)

            logger.info(
                "request_complete",
                agent=self.agent_name,
                duration=duration,
                tokens_used=result.metadata.get("tokens")
            )

            return result.content

        except Exception as e:
            # 記錄錯誤
            request_counter.labels(
                agent_name=self.agent_name,
                status="error"
            ).inc()

            logger.error(
                "request_failed",
                agent=self.agent_name,
                error=str(e),
                exc_info=True
            )

            raise

# 使用
agent = MonitoredAgent("customer_service")
response = agent.process("用戶問題")
    '''

    console.print(Panel(monitoring_code, border_style="blue"))


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]Langroid 企業應用[/bold green]",
        border_style="green"
    ))

    enterprise_architecture()
    console.print("\n" + "="*60 + "\n")

    security_best_practices()
    console.print("\n" + "="*60 + "\n")

    performance_optimization()
    console.print("\n" + "="*60 + "\n")

    monitoring_logging()

    console.print(Panel("""
[bold green]企業應用完成！[/bold green]

關鍵要點：
1. 分層的企業級架構
2. 全面的安全措施
3. 性能優化策略
4. 完善的監控和日誌

企業部署檢查清單：
✓ 安全性評估
✓ 性能測試
✓ 監控配置
✓ 日誌系統
✓ 備份策略
✓ 災難恢復
✓ 文檔完整
✓ 培訓完成

恭喜完成 Langroid 框架學習！

你已經學習了：
1. Langroid 基礎和 Agent 使用
2. 任務系統和工具集成
3. 向量存儲和 RAG
4. 多 Agent 協作
5. 對話和文檔處理
6. 代碼生成應用
7. 企業級開發

下一步建議：
- 構建實際項目
- 探索 Langroid 高級功能
- 參與社區討論
- 閱讀官方文檔
- 分享你的經驗

訪問：https://langroid.github.io/langroid/

Langroid 的核心優勢：
- 簡潔優雅的 API
- 強大的類型安全
- 原生多 Agent 支持
- 優秀的工具集成
- 活躍的社區

祝你使用 Langroid 構建出色的應用！
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()
