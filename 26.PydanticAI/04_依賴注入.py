"""
Pydantic AI - 依賴注入範例

本範例展示：
1. RunContext 的使用
2. 依賴項定義
3. 狀態管理
4. 上下文傳遞
5. 依賴生命週期

依賴注入是 Pydantic AI 的核心設計模式
"""

import asyncio
from typing import Optional, Annotated
from dataclasses import dataclass, field
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext


# ============================================================================
# 範例 1: 基本依賴注入
# ============================================================================

@dataclass
class AppConfig:
    """應用程式配置"""
    app_name: str
    version: str
    debug: bool = False


def example_1_basic_dependency():
    """最基本的依賴注入"""
    print("\n" + "="*60)
    print("範例 1: 基本依賴注入")
    print("="*60)

    # 定義 Agent 的依賴類型
    agent: Agent[AppConfig, str] = Agent(
        'openai:gpt-4',
        deps_type=AppConfig,
    )

    @agent.tool
    def get_app_info(ctx: RunContext[AppConfig]) -> dict:
        """獲取應用程式信息"""
        # 通過 ctx.deps 訪問依賴
        config = ctx.deps

        return {
            "name": config.app_name,
            "version": config.version,
            "debug_mode": config.debug,
            "status": "running"
        }

    # 創建依賴實例並傳入
    config = AppConfig(
        app_name="MyApp",
        version="1.0.0",
        debug=True
    )

    result = agent.run_sync(
        '告訴我應用程式的信息',
        deps=config  # 注入依賴
    )
    print(f"AI 回應：{result.data}")


# ============================================================================
# 範例 2: 複雜依賴對象
# ============================================================================

class Database:
    """模擬數據庫"""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connected = False

    def connect(self):
        """連接數據庫"""
        self.connected = True
        print(f"  ✓ 已連接到數據庫：{self.connection_string}")

    def query(self, sql: str) -> list[dict]:
        """執行查詢"""
        if not self.connected:
            raise RuntimeError("數據庫未連接")

        # 模擬查詢結果
        return [
            {"id": 1, "name": "Alice", "age": 30},
            {"id": 2, "name": "Bob", "age": 25},
        ]

    def close(self):
        """關閉連接"""
        self.connected = False
        print("  ✓ 數據庫連接已關閉")


class Cache:
    """模擬緩存"""

    def __init__(self):
        self._cache: dict[str, any] = {}

    def get(self, key: str) -> Optional[any]:
        """獲取緩存"""
        return self._cache.get(key)

    def set(self, key: str, value: any, ttl: int = 300):
        """設置緩存"""
        self._cache[key] = value
        print(f"  ✓ 緩存已設置：{key}")


@dataclass
class AppDependencies:
    """應用程式依賴集合"""
    database: Database
    cache: Cache
    api_key: str
    environment: str = "production"


def example_2_complex_dependencies():
    """使用複雜的依賴對象"""
    print("\n" + "="*60)
    print("範例 2: 複雜依賴對象")
    print("="*60)

    agent: Agent[AppDependencies, str] = Agent(
        'openai:gpt-4',
        deps_type=AppDependencies,
    )

    @agent.tool
    def get_users(ctx: RunContext[AppDependencies]) -> list[dict]:
        """從數據庫獲取用戶列表"""
        deps = ctx.deps

        # 先檢查緩存
        cached = deps.cache.get("users")
        if cached:
            print("  ✓ 從緩存獲取用戶")
            return cached

        # 從數據庫查詢
        users = deps.database.query("SELECT * FROM users")

        # 存入緩存
        deps.cache.set("users", users)

        return users

    @agent.tool
    def get_environment(ctx: RunContext[AppDependencies]) -> dict:
        """獲取環境信息"""
        return {
            "environment": ctx.deps.environment,
            "api_configured": bool(ctx.deps.api_key),
            "db_connected": ctx.deps.database.connected
        }

    # 創建依賴
    db = Database("postgresql://localhost/mydb")
    db.connect()

    cache = Cache()

    deps = AppDependencies(
        database=db,
        cache=cache,
        api_key="secret-key-123",
        environment="development"
    )

    # 運行 Agent
    result = agent.run_sync(
        '獲取所有用戶並告訴我當前環境',
        deps=deps
    )
    print(f"\nAI 回應：{result.data}")

    # 清理
    db.close()


# ============================================================================
# 範例 3: 狀態管理
# ============================================================================

@dataclass
class StatefulContext:
    """有狀態的上下文"""
    user_id: int
    session_id: str
    request_count: int = 0
    history: list[str] = field(default_factory=list)

    def increment_requests(self):
        """增加請求計數"""
        self.request_count += 1

    def add_history(self, message: str):
        """添加歷史記錄"""
        self.history.append(message)


async def example_3_stateful_context():
    """使用有狀態的上下文"""
    print("\n" + "="*60)
    print("範例 3: 狀態管理")
    print("="*60)

    agent: Agent[StatefulContext, str] = Agent(
        'openai:gpt-4',
        deps_type=StatefulContext,
    )

    @agent.tool
    def record_action(
        ctx: RunContext[StatefulContext],
        action: str
    ) -> dict:
        """記錄用戶操作"""
        # 修改狀態
        ctx.deps.increment_requests()
        ctx.deps.add_history(action)

        return {
            "user_id": ctx.deps.user_id,
            "session_id": ctx.deps.session_id,
            "total_requests": ctx.deps.request_count,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }

    @agent.tool
    def get_user_stats(ctx: RunContext[StatefulContext]) -> dict:
        """獲取用戶統計"""
        return {
            "user_id": ctx.deps.user_id,
            "total_requests": ctx.deps.request_count,
            "history": ctx.deps.history,
            "session_duration": "active"
        }

    # 創建上下文
    context = StatefulContext(
        user_id=12345,
        session_id="sess-abc-123"
    )

    # 第一次請求
    result1 = await agent.run(
        '記錄我查看了產品頁面',
        deps=context
    )
    print(f"請求 1：{result1.data}\n")

    # 第二次請求 - 使用同一個 context
    result2 = await agent.run(
        '記錄我添加了商品到購物車',
        deps=context
    )
    print(f"請求 2：{result2.data}\n")

    # 查看統計
    result3 = await agent.run(
        '顯示我的活動統計',
        deps=context
    )
    print(f"統計：{result3.data}")


# ============================================================================
# 範例 4: 依賴工廠函數
# ============================================================================

@dataclass
class UserSession:
    """用戶會話"""
    username: str
    role: str
    permissions: set[str]
    login_time: datetime

    @classmethod
    def create_admin(cls, username: str) -> 'UserSession':
        """創建管理員會話"""
        return cls(
            username=username,
            role="admin",
            permissions={"read", "write", "delete", "admin"},
            login_time=datetime.now()
        )

    @classmethod
    def create_user(cls, username: str) -> 'UserSession':
        """創建普通用戶會話"""
        return cls(
            username=username,
            role="user",
            permissions={"read", "write"},
            login_time=datetime.now()
        )

    def has_permission(self, permission: str) -> bool:
        """檢查權限"""
        return permission in self.permissions


def example_4_dependency_factory():
    """使用工廠函數創建依賴"""
    print("\n" + "="*60)
    print("範例 4: 依賴工廠函數")
    print("="*60)

    agent: Agent[UserSession, str] = Agent(
        'openai:gpt-4',
        deps_type=UserSession,
    )

    @agent.tool
    def check_permission(
        ctx: RunContext[UserSession],
        action: str
    ) -> dict:
        """檢查權限"""
        session = ctx.deps

        required_permissions = {
            "read": "read",
            "write": "write",
            "delete": "delete",
            "admin": "admin"
        }

        required = required_permissions.get(action, "read")
        has_permission = session.has_permission(required)

        return {
            "user": session.username,
            "role": session.role,
            "action": action,
            "allowed": has_permission,
            "reason": "Authorized" if has_permission else "Insufficient permissions"
        }

    # 使用工廠創建不同類型的會話
    admin_session = UserSession.create_admin("alice")
    user_session = UserSession.create_user("bob")

    # 管理員操作
    print("管理員嘗試刪除：")
    result1 = agent.run_sync(
        '我可以刪除這個文件嗎？',
        deps=admin_session
    )
    print(f"{result1.data}\n")

    # 普通用戶操作
    print("普通用戶嘗試刪除：")
    result2 = agent.run_sync(
        '我可以刪除這個文件嗎？',
        deps=user_session
    )
    print(f"{result2.data}")


# ============================================================================
# 範例 5: 上下文管理器與依賴
# ============================================================================

class ManagedResource:
    """需要管理生命週期的資源"""

    def __init__(self, resource_name: str):
        self.resource_name = resource_name
        self.is_open = False

    def __enter__(self):
        """進入上下文"""
        self.is_open = True
        print(f"  ✓ 資源已打開：{self.resource_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        self.is_open = False
        print(f"  ✓ 資源已關閉：{self.resource_name}")

    def use(self) -> str:
        """使用資源"""
        if not self.is_open:
            raise RuntimeError("資源未打開")
        return f"使用資源：{self.resource_name}"


@dataclass
class ManagedDependencies:
    """包含需要管理的資源"""
    resource: ManagedResource
    metadata: dict


def example_5_managed_dependencies():
    """使用上下文管理器管理依賴"""
    print("\n" + "="*60)
    print("範例 5: 受管理的依賴")
    print("="*60)

    agent: Agent[ManagedDependencies, str] = Agent(
        'openai:gpt-4',
        deps_type=ManagedDependencies,
    )

    @agent.tool
    def use_resource(ctx: RunContext[ManagedDependencies]) -> str:
        """使用受管理的資源"""
        return ctx.deps.resource.use()

    # 使用上下文管理器
    with ManagedResource("DatabaseConnection") as resource:
        deps = ManagedDependencies(
            resource=resource,
            metadata={"created_at": datetime.now().isoformat()}
        )

        result = agent.run_sync(
            '使用數據庫資源',
            deps=deps
        )
        print(f"\nAI 回應：{result.data}")

    # 資源自動關閉


# ============================================================================
# 範例 6: 多層依賴
# ============================================================================

@dataclass
class Logger:
    """日誌記錄器"""
    name: str

    def log(self, message: str):
        """記錄日誌"""
        print(f"  [LOG-{self.name}] {message}")


@dataclass
class ServiceLayer:
    """服務層"""
    logger: Logger
    service_name: str

    def process(self, data: str) -> str:
        """處理數據"""
        self.logger.log(f"{self.service_name} 處理數據：{data}")
        return f"已處理：{data}"


@dataclass
class ApplicationContext:
    """應用程式上下文（多層依賴）"""
    logger: Logger
    service: ServiceLayer
    config: dict


async def example_6_nested_dependencies():
    """處理多層依賴"""
    print("\n" + "="*60)
    print("範例 6: 多層依賴")
    print("="*60)

    agent: Agent[ApplicationContext, str] = Agent(
        'openai:gpt-4',
        deps_type=ApplicationContext,
    )

    @agent.tool
    def process_request(
        ctx: RunContext[ApplicationContext],
        request: str
    ) -> dict:
        """處理請求"""
        # 訪問嵌套的依賴
        ctx.deps.logger.log(f"收到請求：{request}")

        result = ctx.deps.service.process(request)

        ctx.deps.logger.log("請求處理完成")

        return {
            "request": request,
            "result": result,
            "service": ctx.deps.service.service_name,
            "config": ctx.deps.config
        }

    # 構建依賴層次
    logger = Logger(name="MainApp")
    service = ServiceLayer(logger=logger, service_name="DataProcessor")

    app_context = ApplicationContext(
        logger=logger,
        service=service,
        config={"timeout": 30, "retry": 3}
    )

    result = await agent.run(
        '處理用戶數據',
        deps=app_context
    )
    print(f"\nAI 回應：{result.data}")


# ============================================================================
# 主程式
# ============================================================================

async def main():
    """運行所有範例"""
    print("\n" + "💉 " + "="*58)
    print("Pydantic AI - 依賴注入範例")
    print("="*60)

    example_1_basic_dependency()
    example_2_complex_dependencies()
    await example_3_stateful_context()
    example_4_dependency_factory()
    example_5_managed_dependencies()
    await example_6_nested_dependencies()

    print("\n" + "="*60)
    print("✓ 依賴注入範例完成！")
    print("💡 依賴注入的好處：")
    print("   1. 解耦代碼，易於測試")
    print("   2. 靈活配置，易於擴展")
    print("   3. 資源管理，生命週期控制")
    print("   4. 類型安全，IDE 友好")
    print("="*60)


if __name__ == '__main__':
    import os
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  請設置 OPENAI_API_KEY 環境變量")
    else:
        asyncio.run(main())
