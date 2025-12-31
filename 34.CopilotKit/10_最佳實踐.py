"""
CopilotKit 最佳實踐總結

這個文檔總結了使用 CopilotKit 的最佳實踐，包括：
1. 架構設計模式
2. 性能優化技巧
3. 安全最佳實踐
4. 代碼組織
5. 測試策略
6. 常見陷阱避免
7. 用戶體驗優化
8. 可維護性建議

這是學習 CopilotKit 系列的最後一課，綜合所有知識點
"""

import os
from typing import Any, Dict, List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from copilotkit import CopilotKitSDK, Action, LangGraphAgent
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from pydantic import BaseModel, validator
from functools import lru_cache
import asyncio
import logging
import uvicorn


# ============================================================================
# 第一部分：配置管理最佳實踐
# ============================================================================

class Settings(BaseModel):
    """
    集中式配置管理
    使用 Pydantic 進行類型驗證和環境變量加載
    """
    # 應用配置
    app_name: str = "CopilotKit App"
    debug: bool = False
    log_level: str = "INFO"

    # API Keys
    openai_api_key: str
    anthropic_api_key: str = None

    # 數據庫
    database_url: str = "sqlite:///./copilotkit.db"
    redis_url: str = "redis://localhost:6379"

    # 安全
    secret_key: str
    allowed_origins: List[str] = ["http://localhost:3000"]

    # 性能
    max_workers: int = 4
    request_timeout: int = 30
    cache_ttl: int = 3600

    # 速率限制
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = False

    @validator('secret_key')
    def secret_key_must_be_strong(cls, v):
        if len(v) < 32:
            raise ValueError('Secret key must be at least 32 characters')
        return v


@lru_cache()
def get_settings() -> Settings:
    """緩存設置實例"""
    return Settings()


# ============================================================================
# 第二部分：日誌配置最佳實踐
# ============================================================================

def setup_logging():
    """
    配置結構化日誌
    生產環境使用 JSON 格式，開發環境使用可讀格式
    """
    import sys
    from loguru import logger

    # 移除默認處理器
    logger.remove()

    # 根據環境配置不同的日誌格式
    settings = get_settings()

    if settings.debug:
        # 開發環境：彩色、可讀
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=settings.log_level
        )
    else:
        # 生產環境：JSON 格式
        logger.add(
            sys.stderr,
            format="{time} {level} {name}:{function}:{line} {message}",
            level=settings.log_level,
            serialize=True
        )

    # 文件日誌
    logger.add(
        "logs/copilotkit_{time}.log",
        rotation="100 MB",
        retention="30 days",
        compression="zip",
        level=settings.log_level
    )

    return logger


logger = setup_logging()


# ============================================================================
# 第三部分：錯誤處理最佳實踐
# ============================================================================

class BaseError(Exception):
    """基礎錯誤類"""
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ActionError(BaseError):
    """Action 執行錯誤"""
    pass


class ValidationError(BaseError):
    """驗證錯誤"""
    pass


def handle_errors(func):
    """錯誤處理裝飾器"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ActionError as e:
            logger.error(f"Action error: {e.message}", code=e.code)
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }
        except ValidationError as e:
            logger.warning(f"Validation error: {e.message}")
            return {
                "success": False,
                "error": e.message,
                "code": "VALIDATION_ERROR"
            }
        except Exception as e:
            logger.exception("Unexpected error")
            return {
                "success": False,
                "error": "An unexpected error occurred",
                "code": "INTERNAL_ERROR"
            }
    return wrapper


# ============================================================================
# 第四部分：Action 設計最佳實踐
# ============================================================================

class ActionRegistry:
    """
    Action 註冊器
    集中管理所有 Actions，便於維護和測試
    """

    def __init__(self):
        self.actions: Dict[str, Action] = {}

    def register(self, name: str, description: str, parameters: List[Dict], handler):
        """註冊 Action"""
        action = Action(
            name=name,
            description=description,
            parameters=parameters,
            handler=handler
        )
        self.actions[name] = action
        logger.info(f"Registered action: {name}")
        return action

    def get_all(self) -> List[Action]:
        """獲取所有 Actions"""
        return list(self.actions.values())


# 創建全局註冊器
action_registry = ActionRegistry()


# 使用註冊器定義 Actions
@handle_errors
async def optimized_search(
    query: str,
    limit: int = 10,
    filters: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    優化的搜索 Action
    - 參數驗證
    - 錯誤處理
    - 性能優化（緩存）
    - 日誌記錄
    """
    logger.info(f"Searching for: {query}", limit=limit, filters=filters)

    # 參數驗證
    if not query or len(query.strip()) == 0:
        raise ValidationError("Search query cannot be empty")

    if limit < 1 or limit > 100:
        raise ValidationError("Limit must be between 1 and 100")

    # 這裡實現實際的搜索邏輯
    # 示例：從緩存或數據庫中搜索
    await asyncio.sleep(0.1)  # 模擬 I/O

    results = [
        {"id": i, "title": f"Result {i}", "score": 1.0 - (i * 0.1)}
        for i in range(min(limit, 10))
    ]

    logger.info(f"Found {len(results)} results")

    return {
        "success": True,
        "query": query,
        "count": len(results),
        "results": results
    }


# 註冊 Action
action_registry.register(
    name="search",
    description="執行優化的搜索操作",
    parameters=[
        {
            "name": "query",
            "type": "string",
            "description": "搜索查詢",
            "required": True
        },
        {
            "name": "limit",
            "type": "number",
            "description": "結果數量限制 (1-100)",
            "required": False
        },
        {
            "name": "filters",
            "type": "object",
            "description": "過濾條件",
            "required": False
        }
    ],
    handler=optimized_search
)


# ============================================================================
# 第五部分：性能優化最佳實踐
# ============================================================================

class CacheManager:
    """
    緩存管理器
    使用 Redis 或內存緩存提升性能
    """

    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.ttl: Dict[str, float] = {}

    async def get(self, key: str) -> Any:
        """獲取緩存"""
        if key in self.cache:
            import time
            if key in self.ttl and time.time() < self.ttl[key]:
                logger.debug(f"Cache hit: {key}")
                return self.cache[key]
            else:
                # 過期，刪除
                del self.cache[key]
                if key in self.ttl:
                    del self.ttl[key]
        logger.debug(f"Cache miss: {key}")
        return None

    async def set(self, key: str, value: Any, ttl: int = 3600):
        """設置緩存"""
        import time
        self.cache[key] = value
        self.ttl[key] = time.time() + ttl
        logger.debug(f"Cache set: {key}, TTL: {ttl}s")

    async def delete(self, key: str):
        """刪除緩存"""
        if key in self.cache:
            del self.cache[key]
        if key in self.ttl:
            del self.ttl[key]


cache_manager = CacheManager()


def cached(ttl: int = 3600):
    """緩存裝飾器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 生成緩存鍵
            import hashlib
            import json
            cache_key = f"{func.__name__}:{hashlib.md5(json.dumps({'args': args, 'kwargs': kwargs}, default=str).encode()).hexdigest()}"

            # 嘗試從緩存獲取
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

            # 執行函數
            result = await func(*args, **kwargs)

            # 存入緩存
            await cache_manager.set(cache_key, result, ttl)

            return result
        return wrapper
    return decorator


# 使用緩存的示例
@cached(ttl=300)
@handle_errors
async def get_expensive_data(data_id: int) -> Dict[str, Any]:
    """獲取耗時數據（帶緩存）"""
    logger.info(f"Fetching expensive data: {data_id}")
    await asyncio.sleep(2)  # 模擬耗時操作
    return {
        "success": True,
        "data_id": data_id,
        "data": f"Expensive data {data_id}"
    }


# ============================================================================
# 第六部分：安全最佳實踐
# ============================================================================

class SecurityManager:
    """安全管理器"""

    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """清理用戶輸入"""
        # 移除潛在危險字符
        import re
        # 移除 HTML 標籤
        clean = re.sub(r'<[^>]+>', '', input_str)
        # 移除特殊字符
        clean = re.sub(r'[<>&"\\']', '', clean)
        return clean.strip()

    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """驗證 API Key"""
        settings = get_settings()
        # 實際應用中從數據庫驗證
        return api_key == settings.secret_key

    @staticmethod
    def check_rate_limit(user_id: str) -> bool:
        """檢查速率限制"""
        # 實際應用中使用 Redis
        # 這裡簡化處理
        return True


# ============================================================================
# 第七部分：測試最佳實踐
# ============================================================================

# 測試示例（使用 pytest）
TEST_CODE = """
# tests/test_actions.py

import pytest
from unittest.mock import Mock, AsyncMock
from main import optimized_search

@pytest.mark.asyncio
async def test_search_success():
    \"\"\"測試成功的搜索\"\"\"
    result = await optimized_search(query="test", limit=5)
    assert result["success"] == True
    assert result["count"] <= 5
    assert len(result["results"]) <= 5

@pytest.mark.asyncio
async def test_search_empty_query():
    \"\"\"測試空查詢\"\"\"
    result = await optimized_search(query="")
    assert result["success"] == False
    assert "error" in result

@pytest.mark.asyncio
async def test_search_invalid_limit():
    \"\"\"測試無效的限制\"\"\"
    result = await optimized_search(query="test", limit=200)
    assert result["success"] == False

@pytest.mark.asyncio
async def test_cache_functionality():
    \"\"\"測試緩存功能\"\"\"
    # 第一次調用
    result1 = await get_expensive_data(1)
    # 第二次調用（應該從緩存）
    result2 = await get_expensive_data(1)
    assert result1 == result2
"""


# ============================================================================
# 第八部分：FastAPI 應用設置
# ============================================================================

app = FastAPI(
    title="CopilotKit 最佳實踐",
    description="展示 CopilotKit 的所有最佳實踐",
    version="1.0.0"
)

# 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 初始化 SDK
sdk = CopilotKitSDK()

# 註冊所有 Actions
for action in action_registry.get_all():
    sdk.add_action(action)

# 添加 CopilotKit 端點
add_fastapi_endpoint(app, sdk, "/copilotkit")


# API 端點
@app.get("/")
async def root():
    return {
        "message": "CopilotKit 最佳實踐範例",
        "version": "1.0.0",
        "features": [
            "集中式配置管理",
            "結構化日誌",
            "統一錯誤處理",
            "性能緩存",
            "安全最佳實踐",
            "測試覆蓋"
        ]
    }


@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }


# ============================================================================
# 運行說明
# ============================================================================

if __name__ == "__main__":
    logger.info("Starting CopilotKit Best Practices Example")

    print("\\n" + "="*70)
    print("CopilotKit 最佳實踐總結")
    print("="*70)
    print("\\n1. 架構設計")
    print("   ✓ 分層架構（表現層、業務層、數據層）")
    print("   ✓ 依賴注入")
    print("   ✓ 模塊化設計")
    print("\\n2. 配置管理")
    print("   ✓ 使用 Pydantic 進行類型驗證")
    print("   ✓ 環境變量管理")
    print("   ✓ 配置集中化")
    print("\\n3. 日誌和監控")
    print("   ✓ 結構化日誌")
    print("   ✓ 分級日誌")
    print("   ✓ 日誌輪轉")
    print("\\n4. 錯誤處理")
    print("   ✓ 自定義異常類")
    print("   ✓ 統一錯誤格式")
    print("   ✓ 優雅降級")
    print("\\n5. 性能優化")
    print("   ✓ 緩存策略")
    print("   ✓ 異步處理")
    print("   ✓ 連接池")
    print("\\n6. 安全")
    print("   ✓ 輸入驗證和清理")
    print("   ✓ API Key 管理")
    print("   ✓ 速率限制")
    print("\\n7. 測試")
    print("   ✓ 單元測試")
    print("   ✓ 集成測試")
    print("   ✓ 測試覆蓋率")
    print("\\n8. 代碼質量")
    print("   ✓ 類型提示")
    print("   ✓ 文檔字符串")
    print("   ✓ Linting 和格式化")
    print("="*70 + "\\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=None  # 使用自定義日誌配置
    )


"""
===============================================================================
完整的最佳實踐檢查清單
===============================================================================

代碼組織：
□ 使用清晰的項目結構
□ 分離關注點（配置、業務邏輯、數據訪問）
□ 使用有意義的命名
□ 保持函數和類的單一職責
□ 適當的注釋和文檔

配置管理：
□ 使用環境變量
□ 不要硬編碼敏感信息
□ 使用類型驗證（Pydantic）
□ 提供默認值
□ 文檔化所有配置選項

錯誤處理：
□ 定義自定義異常類
□ 提供有用的錯誤消息
□ 記錄錯誤上下文
□ 優雅降級
□ 不要暴露敏感信息

性能優化：
□ 使用緩存
□ 異步處理 I/O
□ 數據庫查詢優化
□ 分頁大數據集
□ 監控性能瓶頸

安全：
□ 驗證所有輸入
□ 使用參數化查詢
□ 實施速率限制
□ 啟用 HTTPS
□ 定期更新依賴

測試：
□ 編寫單元測試
□ 集成測試
□ 測試邊界情況
□ 保持高測試覆蓋率
□ 自動化測試

日誌和監控：
□ 結構化日誌
□ 適當的日誌級別
□ 監控關鍵指標
□ 設置告警
□ 追蹤錯誤

文檔：
□ README 文件
□ API 文檔
□ 代碼注釋
□ 架構文檔
□ 部署指南

可維護性：
□ 保持代碼簡潔
□ 遵循 DRY 原則
□ 使用設計模式
□ 定期重構
□ 代碼審查

用戶體驗：
□ 快速響應時間
□ 清晰的錯誤消息
□ 進度指示
□ 優雅的錯誤處理
□ 一致的 UI/UX

===============================================================================
常見錯誤和如何避免
===============================================================================

❌ 錯誤 1：在代碼中硬編碼 API Keys
✅ 解決：使用環境變量和密鑰管理服務

❌ 錯誤 2：沒有輸入驗證
✅ 解決：使用 Pydantic 模型和自定義驗證器

❌ 錯誤 3：同步阻塞操作
✅ 解決：使用 async/await 處理 I/O

❌ 錯誤 4：沒有錯誤處理
✅ 解決：使用 try-except 和自定義異常

❌ 錯誤 5：暴露詳細錯誤信息
✅ 解決：返回通用錯誤，詳細信息記錄到日誌

❌ 錯誤 6：沒有速率限制
✅ 解決：實施 API 速率限制

❌ 錯誤 7：忽略安全頭
✅ 解決：配置適當的 CORS 和安全頭

❌ 錯誤 8：沒有監控
✅ 解決：設置 Prometheus、Grafana 等

❌ 錯誤 9：沒有測試
✅ 解決：編寫全面的測試套件

❌ 錯誤 10：過度優化
✅ 解決：先實現功能，再根據實際性能問題優化

===============================================================================
學習路徑總結
===============================================================================

初級（1-2 週）：
→ 01_快速開始.py      - 基礎設置
→ 02_React整合.py     - 前端整合
→ 03_CoAgent.py       - Agent 基礎

中級（2-4 週）：
→ 04_前端狀態.py      - 狀態管理
→ 05_後端Action.py    - Action 定義
→ 06_流式輸出.py      - 實時響應
→ 07_自定義UI.py      - UI 定制

高級（4-8 週）：
→ 08_多Agent.py       - 複雜協作
→ 09_部署指南.py      - 生產部署
→ 10_最佳實踐.py      - 綜合實踐

===============================================================================
推薦資源
===============================================================================

官方資源：
• 官網：https://www.copilotkit.ai/
• 文檔：https://docs.copilotkit.ai/
• GitHub：https://github.com/CopilotKit/CopilotKit
• Discord：https://discord.gg/copilotkit

相關技術：
• React：https://react.dev/
• LangChain：https://python.langchain.com/
• LangGraph：https://langchain-ai.github.io/langgraph/
• FastAPI：https://fastapi.tiangolo.com/

學習建議：
1. 從簡單開始，逐步深入
2. 動手實踐每個範例
3. 閱讀官方文檔
4. 參與社區討論
5. 構建實際項目

祝你在 CopilotKit 的學習之旅中取得成功！
"""
