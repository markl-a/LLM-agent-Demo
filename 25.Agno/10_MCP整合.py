"""
10_MCP整合.py - Agno 與 Model Context Protocol (MCP) 整合

本範例展示如何將 Agno 與 Model Context Protocol (MCP) 整合，包括：
- MCP 協議介紹
- MCP 服務器設置
- 工具註冊與發現
- 跨模型工具共享
- MCP 客戶端配置
- 安全性與認證
- 最佳實踐

作者：LLM-agent-Demo Team
日期：2025-12
框架：Agno (原 Phidata) + MCP
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Agno 核心導入
from agno.agent import Agent
from agno.models.openai import OpenAIChat

# 載入環境變數
load_dotenv()


# ============================================================================
# 範例 1: MCP 協議介紹
# ============================================================================
def example_1_mcp_introduction():
    """
    Model Context Protocol (MCP) 介紹

    MCP 是什麼：
    - 統一的工具和資源協議
    - 跨模型、跨框架的標準
    - 由 Anthropic 開發和維護
    """
    print("\n" + "="*80)
    print("範例 1: MCP 協議介紹")
    print("="*80)

    print("""
    Model Context Protocol (MCP) 概述：

    🎯 核心概念：
    - MCP 是一個開放協議，用於連接 AI 模型與外部工具和數據源
    - 提供標準化的方式讓 LLM 訪問資源和執行操作
    - 支持工具發現、調用、和結果返回的完整流程

    📦 主要組件：

    1. MCP Server (服務器)：
       - 提供工具和資源的服務端
       - 實現工具邏輯和數據訪問
       - 處理來自客戶端的請求

    2. MCP Client (客戶端)：
       - 連接到 MCP 服務器
       - 發現可用的工具
       - 調用工具並處理結果

    3. Resources (資源)：
       - 文件、數據庫、API 等數據源
       - 通過標準化接口訪問
       - 支持讀取和寫入操作

    4. Tools (工具)：
       - 可執行的功能
       - 標準化的參數和返回格式
       - 支持同步和異步執行

    🔗 MCP 工作流程：

    ```
    AI Model (Agno Agent)
         ↓
    MCP Client
         ↓
    MCP Server
         ↓
    Tools & Resources
    ```

    🌟 MCP 的優勢：

    1. 標準化：統一的工具接口
    2. 可移植：跨框架、跨模型
    3. 可發現：自動工具發現
    4. 安全：內建認證和授權
    5. 可擴展：易於添加新工具

    🔧 Agno 與 MCP 整合：

    Agno 原生支持 MCP 協議，可以：
    - 連接到任何 MCP 服務器
    - 自動發現和使用工具
    - 與其他 MCP 客戶端共享工具
    - 實現企業級工具管理
    """)


# ============================================================================
# 範例 2: 設置 MCP 服務器
# ============================================================================
def example_2_mcp_server_setup():
    """
    配置和啟動 MCP 服務器

    步驟：
    1. 安裝 MCP SDK
    2. 定義工具
    3. 創建服務器
    4. 啟動服務
    """
    print("\n" + "="*80)
    print("範例 2: 設置 MCP 服務器")
    print("="*80)

    print("""
    MCP 服務器設置：

    1. 安裝 MCP SDK：

    ```bash
    pip install mcp
    ```

    2. 創建 MCP 服務器 (mcp_server.py)：

    ```python
    from mcp.server import Server
    from mcp.types import Tool, TextContent

    # 創建服務器實例
    server = Server("my-tools-server")

    # 定義工具 1: 天氣查詢
    @server.tool()
    async def get_weather(city: str) -> str:
        '''查詢指定城市的天氣

        Args:
            city: 城市名稱

        Returns:
            天氣信息字符串
        '''
        # 實際應用中會調用天氣 API
        return f"{city} 的天氣：晴天，溫度 25°C"

    # 定義工具 2: 計算器
    @server.tool()
    async def calculator(expression: str) -> float:
        '''執行數學計算

        Args:
            expression: 數學表達式

        Returns:
            計算結果
        '''
        try:
            result = eval(expression)
            return float(result)
        except Exception as e:
            raise ValueError(f"無效的表達式: {e}")

    # 定義工具 3: 數據庫查詢
    @server.tool()
    async def query_database(sql: str) -> List[Dict]:
        '''執行數據庫查詢

        Args:
            sql: SQL 查詢語句

        Returns:
            查詢結果列表
        '''
        # 安全檢查
        if any(keyword in sql.upper() for keyword in ["DROP", "DELETE", "UPDATE"]):
            raise ValueError("不允許的SQL操作")

        # 模擬查詢
        return [
            {"id": 1, "name": "產品A", "price": 100},
            {"id": 2, "name": "產品B", "price": 200}
        ]

    # 啟動服務器
    if __name__ == "__main__":
        import asyncio
        from mcp.server.stdio import stdio_server

        async def main():
            async with stdio_server() as streams:
                await server.run(
                    streams[0],
                    streams[1],
                    server.create_initialization_options()
                )

        asyncio.run(main())
    ```

    3. 啟動服務器：

    ```bash
    python mcp_server.py
    ```

    4. 配置文件 (mcp_config.json)：

    ```json
    {
      "mcpServers": {
        "my-tools": {
          "command": "python",
          "args": ["mcp_server.py"],
          "env": {
            "API_KEY": "your_api_key"
          }
        }
      }
    }
    ```
    """)


# ============================================================================
# 範例 3: Agno 連接 MCP 服務器
# ============================================================================
def example_3_agno_mcp_client():
    """
    配置 Agno Agent 連接 MCP 服務器

    功能：
    - 連接到 MCP 服務器
    - 自動發現工具
    - 調用 MCP 工具
    """
    print("\n" + "="*80)
    print("範例 3: Agno 連接 MCP 服務器")
    print("="*80)

    print("""
    Agno MCP 客戶端配置：

    ```python
    from agno.agent import Agent
    from agno.models.openai import OpenAIChat
    from agno.tools.mcp import MCPTools

    # 配置 MCP 工具
    mcp_tools = MCPTools(
        server_config={
            "command": "python",
            "args": ["mcp_server.py"],
            "env": {
                "API_KEY": os.getenv("MCP_API_KEY")
            }
        }
    )

    # 創建 Agent 並連接 MCP
    agent = Agent(
        name="mcp_agent",
        model=OpenAIChat(id="gpt-4"),

        # 添加 MCP 工具
        tools=[mcp_tools],

        instructions=[
            "你可以使用 MCP 服務器提供的工具",
            "自動發現可用工具並智能選擇",
            "正確解析工具返回的結果"
        ],

        show_tool_calls=True,
        markdown=True
    )

    # 使用 MCP 工具
    response = agent.run("查詢台北的天氣")
    print(response.content)

    response = agent.run("計算 (123 + 456) * 2")
    print(response.content)

    response = agent.run("從數據庫查詢所有產品")
    print(response.content)
    ```

    自動工具發現：

    ```python
    # MCP 客戶端會自動發現服務器上的所有工具
    tools = mcp_tools.list_tools()

    for tool in tools:
        print(f"工具名稱: {tool.name}")
        print(f"描述: {tool.description}")
        print(f"參數: {tool.parameters}")
        print()
    ```
    """)


# ============================================================================
# 範例 4: 企業級 MCP 工具管理
# ============================================================================
def example_4_enterprise_mcp():
    """
    企業級 MCP 工具管理

    特性：
    - 多服務器管理
    - 工具命名空間
    - 訪問控制
    - 審計日誌
    """
    print("\n" + "="*80)
    print("範例 4: 企業級 MCP 工具管理")
    print("="*80)

    print("""
    企業級 MCP 架構：

    1. 多服務器配置 (enterprise_mcp_config.json)：

    ```json
    {
      "mcpServers": {
        "database-tools": {
          "command": "python",
          "args": ["servers/database_server.py"],
          "namespace": "db",
          "permissions": ["read", "query"]
        },
        "api-tools": {
          "command": "python",
          "args": ["servers/api_server.py"],
          "namespace": "api",
          "permissions": ["read", "write"]
        },
        "file-tools": {
          "command": "python",
          "args": ["servers/file_server.py"],
          "namespace": "file",
          "permissions": ["read"]
        }
      },
      "authentication": {
        "type": "api_key",
        "rotation_days": 30
      },
      "audit": {
        "enabled": true,
        "log_path": "/var/log/mcp_audit.log"
      }
    }
    ```

    2. 使用命名空間工具：

    ```python
    from agno.agent import Agent
    from agno.tools.mcp import MCPToolsManager

    # 加載所有 MCP 服務器
    mcp_manager = MCPToolsManager(
        config_file="enterprise_mcp_config.json"
    )

    # 創建 Agent
    agent = Agent(
        name="enterprise_agent",
        model=OpenAIChat(id="gpt-4"),
        tools=[mcp_manager],

        instructions=[
            "使用 db.* 工具訪問數據庫",
            "使用 api.* 工具調用外部 API",
            "使用 file.* 工具讀取文件",
            "遵守權限限制"
        ]
    )

    # 示例查詢
    response = agent.run(
        "使用 db.query 查詢用戶表，然後用 api.send_email 發送報告"
    )
    ```

    3. 訪問控制：

    ```python
    from mcp.server import Server, require_permission

    server = Server("secure-server")

    @server.tool()
    @require_permission("write")
    async def delete_record(record_id: int):
        '''刪除記錄（需要寫入權限）'''
        # 檢查權限後執行
        pass

    @server.tool()
    @require_permission("admin")
    async def admin_operation():
        '''管理員操作（需要管理員權限）'''
        pass
    ```

    4. 審計日誌：

    ```python
    import logging
    from datetime import datetime

    audit_logger = logging.getLogger("mcp_audit")

    def log_tool_call(tool_name, user_id, parameters, result):
        '''記錄工具調用'''
        audit_logger.info({
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "user": user_id,
            "parameters": parameters,
            "result_status": "success" if result else "failure"
        })
    ```
    """)


# ============================================================================
# 範例 5: MCP 與 RAG 整合
# ============================================================================
def example_5_mcp_rag_integration():
    """
    將 MCP 工具與 RAG 系統整合

    應用：
    - 動態知識檢索
    - 實時數據更新
    - 多源信息融合
    """
    print("\n" + "="*80)
    print("範例 5: MCP 與 RAG 整合")
    print("="*80)

    print("""
    MCP + RAG 整合架構：

    ```python
    from agno.agent import Agent
    from agno.models.openai import OpenAIChat
    from agno.knowledge.text import TextKnowledgeBase
    from agno.tools.mcp import MCPTools
    from agno.vectordb.lancedb import LanceDb

    # 1. 設置知識庫
    knowledge_base = TextKnowledgeBase(
        path="company_docs",
        vector_db=LanceDb(
            table_name="docs",
            uri="/tmp/lancedb"
        )
    )

    # 2. 設置 MCP 工具（實時數據訪問）
    mcp_tools = MCPTools(
        server_config={
            "command": "python",
            "args": ["realtime_data_server.py"]
        }
    )

    # 3. 創建混合 Agent
    hybrid_agent = Agent(
        name="hybrid_rag_mcp_agent",
        model=OpenAIChat(id="gpt-4"),

        # 結合知識庫和 MCP 工具
        knowledge_base=knowledge_base,
        search_knowledge=True,
        tools=[mcp_tools],

        instructions=[
            "優先從知識庫檢索歷史和靜態信息",
            "使用 MCP 工具獲取實時和動態數據",
            "綜合兩種來源提供完整答案",
            "標註信息來源和時效性"
        ],

        show_tool_calls=True,
        markdown=True
    )

    # 使用示例
    # 這個查詢會結合知識庫（公司政策）和 MCP 工具（實時庫存）
    response = hybrid_agent.run(
        "根據公司退貨政策，檢查產品 SKU-123 的庫存，告訴我是否可以退貨並重新發貨？"
    )

    # Agent 會：
    # 1. 從知識庫檢索退貨政策
    # 2. 使用 MCP 工具查詢實時庫存
    # 3. 綜合兩者給出答案
    ```

    實時數據服務器示例：

    ```python
    from mcp.server import Server

    server = Server("realtime-data")

    @server.tool()
    async def get_inventory(sku: str) -> Dict:
        '''查詢產品實時庫存'''
        # 連接到實時庫存數據庫
        return {
            "sku": sku,
            "quantity": 150,
            "warehouse": "台北倉",
            "last_updated": "2025-12-22T10:30:00Z"
        }

    @server.tool()
    async def get_stock_price(symbol: str) -> Dict:
        '''查詢股票實時價格'''
        # 調用金融 API
        return {
            "symbol": symbol,
            "price": 150.25,
            "change": +2.5,
            "timestamp": "2025-12-22T10:30:00Z"
        }
    ```
    """)


# ============================================================================
# 範例 6: MCP 安全性最佳實踐
# ============================================================================
def example_6_mcp_security():
    """
    MCP 安全性配置

    措施：
    - 認證授權
    - 輸入驗證
    - 速率限制
    - 審計追蹤
    """
    print("\n" + "="*80)
    print("範例 6: MCP 安全性最佳實踐")
    print("="*80)

    print("""
    MCP 安全性配置：

    1. API Key 認證：

    ```python
    from mcp.server import Server, require_auth

    server = Server("secure-server")

    @server.tool()
    @require_auth
    async def sensitive_operation(data: str) -> str:
        '''需要認證的敏感操作'''
        # 只有通過認證的客戶端才能調用
        return f"處理: {data}"

    # 客戶端配置
    mcp_tools = MCPTools(
        server_config={
            "command": "python",
            "args": ["secure_server.py"],
            "env": {
                "MCP_API_KEY": os.getenv("MCP_API_KEY")
            }
        }
    )
    ```

    2. 輸入驗證：

    ```python
    from pydantic import BaseModel, Field, validator

    class QueryParams(BaseModel):
        user_id: int = Field(..., ge=1)
        limit: int = Field(10, ge=1, le=100)

        @validator('user_id')
        def validate_user_id(cls, v):
            # 自定義驗證邏輯
            if v < 0:
                raise ValueError('無效的用戶 ID')
            return v

    @server.tool()
    async def get_user_data(params: QueryParams) -> Dict:
        '''獲取用戶數據（帶驗證）'''
        # params 已經過驗證
        return {"user_id": params.user_id, "data": [...]}
    ```

    3. 速率限制：

    ```python
    from functools import wraps
    from time import time
    from collections import defaultdict

    # 簡單的速率限制器
    rate_limits = defaultdict(list)

    def rate_limit(max_calls=10, period=60):
        '''限制速率裝飾器'''
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                now = time()
                client_id = kwargs.get('client_id', 'default')

                # 清理過期記錄
                rate_limits[client_id] = [
                    t for t in rate_limits[client_id]
                    if now - t < period
                ]

                # 檢查限制
                if len(rate_limits[client_id]) >= max_calls:
                    raise Exception("速率限制：請稍後再試")

                rate_limits[client_id].append(now)
                return await func(*args, **kwargs)

            return wrapper
        return decorator

    @server.tool()
    @rate_limit(max_calls=100, period=60)
    async def api_call(endpoint: str):
        '''受速率限制的 API 調用'''
        pass
    ```

    4. 審計日誌：

    ```python
    import logging
    from functools import wraps

    audit_logger = logging.getLogger('mcp_audit')

    def audit_log(func):
        '''審計日誌裝飾器'''
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 記錄調用
            audit_logger.info(f"Tool called: {func.__name__}")
            audit_logger.info(f"Args: {args}, Kwargs: {kwargs}")

            try:
                result = await func(*args, **kwargs)
                audit_logger.info(f"Result: Success")
                return result
            except Exception as e:
                audit_logger.error(f"Result: Failed - {e}")
                raise

        return wrapper

    @server.tool()
    @audit_log
    async def critical_operation(data: str):
        '''關鍵操作（帶審計）'''
        pass
    ```
    """)


# ============================================================================
# 主函數：運行所有範例
# ============================================================================
def main():
    """展示 MCP 整合指南"""

    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║        Agno 與 Model Context Protocol (MCP) 整合指南           ║
    ║                                                                ║
    ║  展示如何使用 MCP 實現標準化的工具管理和共享                   ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

    try:
        # 展示各個範例
        example_1_mcp_introduction()
        example_2_mcp_server_setup()
        example_3_agno_mcp_client()
        example_4_enterprise_mcp()
        example_5_mcp_rag_integration()
        example_6_mcp_security()

        print("\n" + "="*80)
        print("✅ MCP 整合指南展示完成！")
        print("="*80)

        print("\n📚 相關資源：")
        print("- MCP 官方網站: https://modelcontextprotocol.io")
        print("- MCP GitHub: https://github.com/modelcontextprotocol")
        print("- Agno MCP 文檔: https://docs.agno.com/mcp")

        print("\n🎯 恭喜！您已完成所有 Agno 教程！")
        print("\n下一步建議：")
        print("1. 實際動手構建一個 Agno 項目")
        print("2. 探索 Agno 的進階功能")
        print("3. 加入 Agno 社群分享經驗")

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
📚 MCP 整合學習要點：

1. **MCP 核心概念**
   - 標準化工具協議
   - 服務器-客戶端架構
   - 工具發現和調用
   - 資源訪問管理

2. **MCP 服務器**
   ```python
   from mcp.server import Server

   server = Server("my-server")

   @server.tool()
   async def my_tool(param: str) -> str:
       return f"結果: {param}"
   ```

3. **Agno MCP 客戶端**
   ```python
   from agno.tools.mcp import MCPTools

   mcp_tools = MCPTools(
       server_config={
           "command": "python",
           "args": ["server.py"]
       }
   )

   agent = Agent(tools=[mcp_tools])
   ```

4. **工具命名空間**
   - 組織工具為邏輯組
   - 避免命名衝突
   - 清晰的工具分類
   - 權限隔離

5. **安全性**
   - API Key 認證
   - 輸入驗證
   - 速率限制
   - 審計日誌
   - 權限控制

6. **企業級功能**
   - 多服務器管理
   - 集中式配置
   - 訪問控制
   - 審計追蹤
   - 高可用性

7. **與其他技術整合**
   - RAG 系統
   - 數據庫
   - API 服務
   - 文件系統
   - 實時數據

8. **最佳實踐**
   - 清晰的工具文檔
   - 完善的錯誤處理
   - 詳細的審計日誌
   - 安全的認證機制
   - 合理的速率限制

💡 MCP 使用建議：
- 為工具提供清晰的描述
- 實施嚴格的輸入驗證
- 使用命名空間組織工具
- 配置適當的權限
- 監控工具使用情況

🔗 相關資源：
- MCP 規範: https://spec.modelcontextprotocol.io
- MCP SDK: https://github.com/modelcontextprotocol/python-sdk
- Agno MCP 指南: https://docs.agno.com/mcp/guide

⚡ MCP 優勢：
- 標準化工具接口
- 跨框架兼容
- 企業級管理
- 安全性保障
- 易於擴展

🎓 學習完成：
恭喜完成 Agno 框架的完整學習之旅！
現在你已經掌握了：
- 基礎入門
- 工具使用
- 多模態處理
- Agentic RAG
- 團隊協作
- 記憶管理
- 高級推理
- 結構化輸出
- 生產部署
- MCP 整合

繼續探索 Agno 的無限可能！
"""
