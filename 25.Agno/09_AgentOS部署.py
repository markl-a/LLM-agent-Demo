"""
09_AgentOS部署.py - Agno Agent 生產環境部署指南

本範例展示如何將 Agno Agent 部署到生產環境，包括：
- AgentOS 平台介紹
- 本地開發環境配置
- API 服務部署
- 性能監控與追蹤
- 錯誤處理與日誌
- 擴展與負載均衡
- 安全性配置

作者：LLM-agent-Demo Team
日期：2025-12
框架：Agno (原 Phidata)
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Agno 核心導入
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools

# 載入環境變數
load_dotenv()


# ============================================================================
# 範例 1: 基礎 API 服務
# ============================================================================
def example_1_basic_api_service():
    """
    創建基礎的 Agent API 服務

    架構：
    - Agent 作為後端服務
    - REST API 接口
    - 請求/響應處理
    """
    print("\n" + "="*80)
    print("範例 1: 基礎 API 服務")
    print("="*80)

    print("""
    基礎 API 服務架構：

    ```python
    from fastapi import FastAPI
    from agno.agent import Agent
    from agno.models.openai import OpenAIChat

    app = FastAPI()

    # 創建 Agent
    agent = Agent(
        name="api_agent",
        model=OpenAIChat(id="gpt-4"),
        description="API 服務 Agent"
    )

    @app.post("/chat")
    async def chat(message: str):
        '''處理聊天請求'''
        response = agent.run(message)
        return {
            "response": response.content,
            "model": "gpt-4",
            "timestamp": datetime.now().isoformat()
        }

    @app.get("/health")
    async def health_check():
        '''健康檢查'''
        return {"status": "healthy"}

    # 啟動服務
    # uvicorn main:app --host 0.0.0.0 --port 8000
    ```

    使用方式：
    ```bash
    curl -X POST "http://localhost:8000/chat" \\
         -H "Content-Type: application/json" \\
         -d '{"message": "你好"}'
    ```
    """)


# ============================================================================
# 範例 2: 環境配置管理
# ============================================================================
def example_2_environment_config():
    """
    生產環境配置管理

    配置項：
    - API Keys
    - 數據庫連接
    - 日誌級別
    - 性能參數
    """
    print("\n" + "="*80)
    print("範例 2: 環境配置管理")
    print("="*80)

    print("""
    環境變數配置（.env 文件）：

    ```env
    # 開發環境配置
    ENV=development
    DEBUG=true
    LOG_LEVEL=DEBUG

    # API Keys
    OPENAI_API_KEY=sk-...
    ANTHROPIC_API_KEY=sk-ant-...

    # AgentOS 配置
    AGNO_API_KEY=your_agno_key
    AGNO_WORKSPACE=your_workspace

    # 數據庫配置
    DATABASE_URL=postgresql://user:pass@localhost/dbname

    # Redis 配置（緩存）
    REDIS_URL=redis://localhost:6379/0

    # 性能配置
    MAX_CONCURRENT_REQUESTS=100
    REQUEST_TIMEOUT=30
    RATE_LIMIT=100/minute

    # 監控配置
    SENTRY_DSN=https://...
    ENABLE_METRICS=true
    ```

    加載配置：

    ```python
    from pydantic_settings import BaseSettings

    class Settings(BaseSettings):
        env: str = "development"
        debug: bool = False
        log_level: str = "INFO"

        openai_api_key: str
        agno_api_key: Optional[str] = None

        database_url: str
        redis_url: str

        max_concurrent_requests: int = 100
        request_timeout: int = 30

        class Config:
            env_file = ".env"

    settings = Settings()
    ```
    """)


# ============================================================================
# 範例 3: 日誌與監控
# ============================================================================
def example_3_logging_monitoring():
    """
    實施完善的日誌和監控系統

    組件：
    - 結構化日誌
    - 性能追蹤
    - 錯誤報告
    - 指標收集
    """
    print("\n" + "="*80)
    print("範例 3: 日誌與監控")
    print("="*80)

    print("""
    日誌配置：

    ```python
    import logging
    from logging.handlers import RotatingFileHandler

    # 配置日誌
    logger = logging.getLogger("agno_app")
    logger.setLevel(logging.INFO)

    # 文件處理器（自動輪轉）
    file_handler = RotatingFileHandler(
        "agno_app.log",
        maxBytes=10_000_000,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(
        logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    )

    logger.addHandler(file_handler)

    # 使用日誌
    logger.info("Agent 啟動")
    logger.error("發生錯誤", exc_info=True)
    ```

    性能監控：

    ```python
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.metrics import MeterProvider

    # 設置追蹤
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)

    # 追蹤 Agent 調用
    with tracer.start_as_current_span("agent_run") as span:
        span.set_attribute("agent.name", "my_agent")
        span.set_attribute("model", "gpt-4")

        response = agent.run(query)

        span.set_attribute("response.length", len(response.content))
        span.set_attribute("tokens.used", response.tokens)
    ```

    錯誤追蹤（Sentry）：

    ```python
    import sentry_sdk

    sentry_sdk.init(
        dsn="your_sentry_dsn",
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

    try:
        response = agent.run(query)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise
    ```
    """)


# ============================================================================
# 範例 4: 錯誤處理與重試
# ============================================================================
def example_4_error_handling():
    """
    生產級錯誤處理

    策略：
    - 優雅降級
    - 自動重試
    - 熔斷器模式
    - 降級響應
    """
    print("\n" + "="*80)
    print("範例 4: 錯誤處理與重試")
    print("="*80)

    print("""
    重試機制：

    ```python
    from tenacity import retry, stop_after_attempt, wait_exponential

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def run_agent_with_retry(agent, query):
        '''帶重試的 Agent 調用'''
        try:
            return agent.run(query)
        except Exception as e:
            logger.error(f"Agent 調用失敗: {e}")
            raise
    ```

    熔斷器模式：

    ```python
    from pybreaker import CircuitBreaker

    # 創建熔斷器
    breaker = CircuitBreaker(
        fail_max=5,          # 5次失敗後開啟
        timeout_duration=60  # 60秒後嘗試恢復
    )

    @breaker
    def call_agent(query):
        return agent.run(query)

    # 使用
    try:
        response = call_agent(query)
    except CircuitBreakerError:
        # 熔斷器開啟，使用降級響應
        response = fallback_response()
    ```

    降級策略：

    ```python
    def run_with_fallback(query):
        '''帶降級的執行'''
        try:
            # 嘗試主 Agent（GPT-4）
            response = primary_agent.run(query)
            return response
        except Exception as e:
            logger.warning(f"主 Agent 失敗，使用備用: {e}")

            try:
                # 降級到 GPT-3.5
                response = fallback_agent.run(query)
                return response
            except Exception as e2:
                logger.error(f"備用 Agent 也失敗: {e2}")

                # 返回預設響應
                return "抱歉，服務暫時不可用，請稍後再試。"
    ```
    """)


# ============================================================================
# 範例 5: 性能優化
# ============================================================================
def example_5_performance_optimization():
    """
    性能優化策略

    技術：
    - 緩存機制
    - 連接池
    - 異步處理
    - 批量處理
    """
    print("\n" + "="*80)
    print("範例 5: 性能優化")
    print("="*80)

    print("""
    緩存策略：

    ```python
    import redis
    import hashlib
    import json

    # Redis 客戶端
    redis_client = redis.Redis(host='localhost', port=6379, db=0)

    def get_cached_response(query, agent):
        '''使用緩存的響應'''
        # 生成緩存鍵
        cache_key = f"agent:{hashlib.md5(query.encode()).hexdigest()}"

        # 檢查緩存
        cached = redis_client.get(cache_key)
        if cached:
            logger.info("緩存命中")
            return json.loads(cached)

        # 調用 Agent
        response = agent.run(query)

        # 存入緩存（1小時過期）
        redis_client.setex(
            cache_key,
            3600,
            json.dumps({"content": response.content})
        )

        return {"content": response.content}
    ```

    異步處理：

    ```python
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    executor = ThreadPoolExecutor(max_workers=10)

    async def async_agent_run(agent, query):
        '''異步 Agent 調用'''
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            executor,
            agent.run,
            query
        )
        return response

    # 並行處理多個查詢
    async def process_batch(queries):
        tasks = [async_agent_run(agent, q) for q in queries]
        results = await asyncio.gather(*tasks)
        return results
    ```

    連接池：

    ```python
    from sqlalchemy import create_engine
    from sqlalchemy.pool import QueuePool

    # 數據庫連接池
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=3600
    )
    ```
    """)


# ============================================================================
# 範例 6: AgentOS 部署
# ============================================================================
def example_6_agentos_deployment():
    """
    部署到 AgentOS 平台

    步驟：
    1. 準備 Agent 代碼
    2. 配置部署文件
    3. 部署到 AgentOS
    4. 監控運行狀態
    """
    print("\n" + "="*80)
    print("範例 6: AgentOS 部署")
    print("="*80)

    print("""
    AgentOS 部署流程：

    1. 安裝 AgentOS CLI：

    ```bash
    pip install agno[agentos]
    ```

    2. 登錄 AgentOS：

    ```bash
    agno login
    # 輸入 API Key
    ```

    3. 初始化項目：

    ```bash
    agno init
    ```

    4. 配置 agent.yaml：

    ```yaml
    name: my-agent
    description: 生產環境 Agent
    version: 1.0.0

    runtime:
      python: "3.11"
      dependencies:
        - agno
        - openai
        - langchain

    agent:
      model: gpt-4
      tools:
        - duckduckgo
        - calculator
      memory: true
      monitoring: true

    resources:
      cpu: 2
      memory: 4Gi
      replicas: 3

    scaling:
      min_replicas: 2
      max_replicas: 10
      target_cpu: 70

    monitoring:
      enabled: true
      log_level: INFO
      metrics: true

    security:
      api_key_required: true
      rate_limit: 100/minute
    ```

    5. 部署：

    ```bash
    agno deploy
    ```

    6. 監控：

    ```bash
    # 查看狀態
    agno status

    # 查看日誌
    agno logs --follow

    # 查看指標
    agno metrics
    ```

    7. 更新：

    ```bash
    agno update --version 1.1.0
    ```

    8. 縮放：

    ```bash
    agno scale --replicas 5
    ```
    """)


# ============================================================================
# 範例 7: Docker 容器化
# ============================================================================
def example_7_docker_deployment():
    """
    使用 Docker 容器化部署
    """
    print("\n" + "="*80)
    print("範例 7: Docker 容器化")
    print("="*80)

    print("""
    Dockerfile：

    ```dockerfile
    FROM python:3.11-slim

    WORKDIR /app

    # 安裝依賴
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    # 複製代碼
    COPY . .

    # 暴露端口
    EXPOSE 8000

    # 健康檢查
    HEALTHCHECK --interval=30s --timeout=3s \\
      CMD curl -f http://localhost:8000/health || exit 1

    # 啟動服務
    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
    ```

    docker-compose.yml：

    ```yaml
    version: '3.8'

    services:
      agent:
        build: .
        ports:
          - "8000:8000"
        environment:
          - OPENAI_API_KEY=${OPENAI_API_KEY}
          - ENV=production
        depends_on:
          - redis
          - postgres
        restart: unless-stopped

      redis:
        image: redis:7-alpine
        ports:
          - "6379:6379"
        volumes:
          - redis_data:/data

      postgres:
        image: postgres:15
        environment:
          - POSTGRES_PASSWORD=secretpassword
        volumes:
          - postgres_data:/var/lib/postgresql/data

    volumes:
      redis_data:
      postgres_data:
    ```

    構建和運行：

    ```bash
    # 構建鏡像
    docker build -t my-agent:latest .

    # 運行容器
    docker-compose up -d

    # 查看日誌
    docker-compose logs -f agent

    # 擴展
    docker-compose up -d --scale agent=3
    ```
    """)


# ============================================================================
# 主函數：運行所有範例
# ============================================================================
def main():
    """展示生產環境部署指南"""

    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║          Agno Agent 生產環境部署完整指南                       ║
    ║                                                                ║
    ║  展示如何將 Agent 部署到生產環境並確保可靠運行                 ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

    try:
        # 展示各個範例
        example_1_basic_api_service()
        example_2_environment_config()
        example_3_logging_monitoring()
        example_4_error_handling()
        example_5_performance_optimization()
        example_6_agentos_deployment()
        example_7_docker_deployment()

        print("\n" + "="*80)
        print("✅ 部署指南展示完成！")
        print("="*80)

        print("\n📚 下一步學習：")
        print("- 10_MCP整合.py - Model Context Protocol 整合")
        print("- 查看 AgentOS 文檔: https://docs.agno.com/agentos")

    except Exception as e:
        print(f"\n❌ 展示過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


# ============================================================================
# 學習要點總結
# ============================================================================
"""
📚 生產環境部署學習要點：

1. **部署架構**
   - API 服務層
   - Agent 處理層
   - 數據存儲層
   - 緩存層
   - 監控層

2. **關鍵配置**
   - 環境變數管理
   - API Key 安全
   - 數據庫連接
   - 緩存策略
   - 日誌級別

3. **可靠性保證**
   - 健康檢查
   - 自動重試
   - 熔斷器
   - 降級策略
   - 錯誤處理

4. **性能優化**
   - 響應緩存
   - 連接池
   - 異步處理
   - 批量操作
   - 負載均衡

5. **監控與追蹤**
   - 結構化日誌
   - 性能指標
   - 錯誤追蹤
   - 分佈式追蹤
   - 實時警報

6. **擴展策略**
   - 水平擴展
   - 自動縮放
   - 負載均衡
   - 服務發現
   - 容災備份

7. **安全措施**
   - API 認證
   - 速率限制
   - 輸入驗證
   - 輸出過濾
   - 數據加密

8. **DevOps 實踐**
   - CI/CD 流程
   - 容器化
   - 版本控制
   - 滾動更新
   - 快速回滾

💡 部署檢查清單：
- ✅ 環境變數配置完整
- ✅ 健康檢查端點就緒
- ✅ 日誌系統配置正確
- ✅ 錯誤處理機制完善
- ✅ 性能監控已啟用
- ✅ 緩存策略已實施
- ✅ 安全措施已部署
- ✅ 備份恢復計劃就位

🔗 相關資源：
- AgentOS 文檔: https://docs.agno.com/agentos
- 部署最佳實踐: https://docs.agno.com/deployment
- 性能優化指南: https://docs.agno.com/performance

⚡ AgentOS 優勢：
- 一鍵部署
- 自動擴展
- 內建監控
- 企業級安全
- 高可用性
"""
