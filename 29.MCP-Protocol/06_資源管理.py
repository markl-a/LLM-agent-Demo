"""
MCP 資源管理
============

本模組介紹 MCP 的資源（Resources）功能。
資源允許服務器向客戶端公開結構化數據，如文件、數據庫記錄、API 端點等。

學習目標：
- 理解資源的概念和用途
- 定義和公開資源
- 實現資源的讀取和訂閱
- 處理資源變更通知

作者：Claude (Anthropic)
日期：2025-12-22
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json


# ============================================================================
# 第一部分：資源基礎概念
# ============================================================================

class ResourceType(Enum):
    """資源類型"""
    FILE = "file"
    DATABASE = "database"
    API = "api"
    MEMORY = "memory"
    STREAM = "stream"


@dataclass
class Resource:
    """資源定義"""
    uri: str  # 唯一標識符，使用 URI 格式
    name: str  # 人類可讀的名稱
    description: str  # 資源描述
    mime_type: str  # MIME 類型（如 text/plain, application/json）
    metadata: Optional[Dict[str, Any]] = None  # 額外的元數據


@dataclass
class ResourceContent:
    """資源內容"""
    uri: str
    mime_type: str
    text: Optional[str] = None  # 文本內容
    blob: Optional[bytes] = None  # 二進制內容
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# 第二部分：資源提供器
# ============================================================================

class FileSystemResourceProvider:
    """
    文件系統資源提供器

    將文件系統中的文件作為 MCP 資源公開
    """

    def __init__(self, root_path: str):
        self.root_path = root_path
        self.resources: Dict[str, Resource] = {}

    def register_file(self, file_path: str, name: Optional[str] = None) -> Resource:
        """
        註冊文件為資源

        Args:
            file_path: 文件路徑
            name: 資源名稱（可選）

        Returns:
            註冊的資源對象
        """
        import os

        # 生成 URI
        uri = f"file://{os.path.abspath(file_path)}"

        # 確定 MIME 類型
        mime_type = self._guess_mime_type(file_path)

        # 獲取文件元數據
        stat = os.stat(file_path)
        metadata = {
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "path": file_path
        }

        # 創建資源
        resource = Resource(
            uri=uri,
            name=name or os.path.basename(file_path),
            description=f"文件: {file_path}",
            mime_type=mime_type,
            metadata=metadata
        )

        self.resources[uri] = resource
        return resource

    def _guess_mime_type(self, file_path: str) -> str:
        """猜測文件的 MIME 類型"""
        import mimetypes

        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or "application/octet-stream"

    async def read_resource(self, uri: str) -> ResourceContent:
        """
        讀取資源內容

        Args:
            uri: 資源 URI

        Returns:
            資源內容
        """
        if uri not in self.resources:
            raise ValueError(f"資源不存在: {uri}")

        resource = self.resources[uri]
        file_path = resource.metadata["path"]

        # 讀取文件
        if resource.mime_type.startswith("text/"):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return ResourceContent(
                uri=uri,
                mime_type=resource.mime_type,
                text=content,
                metadata=resource.metadata
            )
        else:
            with open(file_path, 'rb') as f:
                content = f.read()

            return ResourceContent(
                uri=uri,
                mime_type=resource.mime_type,
                blob=content,
                metadata=resource.metadata
            )

    def list_resources(self) -> List[Resource]:
        """列出所有資源"""
        return list(self.resources.values())


# ============================================================================
# 第三部分：數據庫資源提供器
# ============================================================================

class DatabaseResourceProvider:
    """
    數據庫資源提供器

    將數據庫表和查詢結果作為資源公開
    """

    def __init__(self, database_name: str):
        self.database_name = database_name
        self.resources: Dict[str, Resource] = {}

    def register_table(
        self,
        table_name: str,
        description: Optional[str] = None
    ) -> Resource:
        """註冊數據庫表為資源"""

        uri = f"db://{self.database_name}/tables/{table_name}"

        resource = Resource(
            uri=uri,
            name=table_name,
            description=description or f"數據庫表: {table_name}",
            mime_type="application/json",
            metadata={
                "database": self.database_name,
                "table": table_name,
                "type": "table"
            }
        )

        self.resources[uri] = resource
        return resource

    def register_query(
        self,
        query_name: str,
        sql: str,
        description: Optional[str] = None
    ) -> Resource:
        """註冊 SQL 查詢為資源"""

        uri = f"db://{self.database_name}/queries/{query_name}"

        resource = Resource(
            uri=uri,
            name=query_name,
            description=description or f"查詢: {query_name}",
            mime_type="application/json",
            metadata={
                "database": self.database_name,
                "sql": sql,
                "type": "query"
            }
        )

        self.resources[uri] = resource
        return resource

    async def read_resource(self, uri: str) -> ResourceContent:
        """讀取資源內容（執行查詢）"""

        if uri not in self.resources:
            raise ValueError(f"資源不存在: {uri}")

        resource = self.resources[uri]

        # 模擬數據庫查詢
        # 實際實現中會連接真實數據庫
        if resource.metadata["type"] == "table":
            result = {
                "table": resource.metadata["table"],
                "rows": [
                    {"id": 1, "name": "示例記錄 1"},
                    {"id": 2, "name": "示例記錄 2"}
                ]
            }
        else:
            result = {
                "query": resource.name,
                "rows": []
            }

        return ResourceContent(
            uri=uri,
            mime_type="application/json",
            text=json.dumps(result, ensure_ascii=False, indent=2),
            metadata=resource.metadata
        )

    def list_resources(self) -> List[Resource]:
        """列出所有資源"""
        return list(self.resources.values())


# ============================================================================
# 第四部分：API 資源提供器
# ============================================================================

class APIResourceProvider:
    """
    API 資源提供器

    將 API 端點作為資源公開
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.resources: Dict[str, Resource] = {}

    def register_endpoint(
        self,
        path: str,
        method: str = "GET",
        description: Optional[str] = None
    ) -> Resource:
        """註冊 API 端點為資源"""

        uri = f"api://{self.base_url}{path}"

        resource = Resource(
            uri=uri,
            name=f"{method} {path}",
            description=description or f"API 端點: {method} {path}",
            mime_type="application/json",
            metadata={
                "base_url": self.base_url,
                "path": path,
                "method": method
            }
        )

        self.resources[uri] = resource
        return resource

    async def read_resource(self, uri: str) -> ResourceContent:
        """讀取資源內容（調用 API）"""

        if uri not in self.resources:
            raise ValueError(f"資源不存在: {uri}")

        resource = self.resources[uri]

        # 模擬 API 調用
        # 實際實現中會發送 HTTP 請求
        result = {
            "endpoint": resource.name,
            "data": {"message": "API 響應示例"}
        }

        return ResourceContent(
            uri=uri,
            mime_type="application/json",
            text=json.dumps(result, ensure_ascii=False, indent=2),
            metadata=resource.metadata
        )

    def list_resources(self) -> List[Resource]:
        """列出所有資源"""
        return list(self.resources.values())


# ============================================================================
# 第五部分：資源訂閱和變更通知
# ============================================================================

class ResourceSubscriptionManager:
    """
    資源訂閱管理器

    管理資源的訂閱和變更通知
    """

    def __init__(self):
        self.subscriptions: Dict[str, List[str]] = {}  # uri -> [client_ids]
        self.watchers: Dict[str, Any] = {}  # uri -> watcher

    def subscribe(self, uri: str, client_id: str):
        """訂閱資源變更"""
        if uri not in self.subscriptions:
            self.subscriptions[uri] = []

        if client_id not in self.subscriptions[uri]:
            self.subscriptions[uri].append(client_id)
            print(f"✓ 客戶端 {client_id} 訂閱了資源 {uri}")

    def unsubscribe(self, uri: str, client_id: str):
        """取消訂閱"""
        if uri in self.subscriptions and client_id in self.subscriptions[uri]:
            self.subscriptions[uri].remove(client_id)
            print(f"✓ 客戶端 {client_id} 取消訂閱資源 {uri}")

    async def notify_change(self, uri: str, change_type: str):
        """通知資源變更"""
        if uri not in self.subscriptions:
            return

        notification = {
            "jsonrpc": "2.0",
            "method": "notifications/resources/updated",
            "params": {
                "uri": uri,
                "changeType": change_type
            }
        }

        for client_id in self.subscriptions[uri]:
            print(f"發送變更通知給 {client_id}: {uri} ({change_type})")
            # 實際實現中會通過傳輸層發送通知

    def get_subscribers(self, uri: str) -> List[str]:
        """獲取資源的訂閱者列表"""
        return self.subscriptions.get(uri, [])


# ============================================================================
# 第六部分：完整的資源管理器
# ============================================================================

class ResourceManager:
    """
    完整的資源管理器

    整合多個資源提供器
    """

    def __init__(self):
        self.providers: Dict[str, Any] = {}
        self.subscription_manager = ResourceSubscriptionManager()

    def register_provider(self, scheme: str, provider: Any):
        """註冊資源提供器"""
        self.providers[scheme] = provider
        print(f"✓ 註冊資源提供器: {scheme}://")

    def _get_provider(self, uri: str) -> Any:
        """根據 URI 獲取對應的提供器"""
        scheme = uri.split("://")[0]

        if scheme not in self.providers:
            raise ValueError(f"不支持的 URI 方案: {scheme}")

        return self.providers[scheme]

    async def list_all_resources(self) -> List[Resource]:
        """列出所有資源"""
        all_resources = []

        for provider in self.providers.values():
            all_resources.extend(provider.list_resources())

        return all_resources

    async def read_resource(self, uri: str) -> ResourceContent:
        """讀取資源"""
        provider = self._get_provider(uri)
        return await provider.read_resource(uri)

    def subscribe(self, uri: str, client_id: str):
        """訂閱資源"""
        self.subscription_manager.subscribe(uri, client_id)

    async def notify_change(self, uri: str, change_type: str):
        """通知資源變更"""
        await self.subscription_manager.notify_change(uri, change_type)


# ============================================================================
# 主程式示例
# ============================================================================

async def main():
    """主程式：展示資源管理"""

    print("=" * 70)
    print("MCP 資源管理示例")
    print("=" * 70)

    # 1. 文件系統資源
    print("\n【示例 1：文件系統資源】")
    fs_provider = FileSystemResourceProvider("/tmp")

    # 註冊文件
    # 注意：這裡使用模擬路徑
    print("註冊資源：")
    print("  • README.md")
    print("  • config.json")

    # 2. 數據庫資源
    print("\n【示例 2：數據庫資源】")
    db_provider = DatabaseResourceProvider("my_database")

    # 註冊表和查詢
    users_table = db_provider.register_table("users", "用戶表")
    print(f"註冊表資源: {users_table.uri}")

    user_query = db_provider.register_query(
        "active_users",
        "SELECT * FROM users WHERE active = true",
        "活躍用戶查詢"
    )
    print(f"註冊查詢資源: {user_query.uri}")

    # 讀取資源
    content = await db_provider.read_resource(users_table.uri)
    print(f"\n資源內容:\n{content.text}")

    # 3. API 資源
    print("\n【示例 3：API 資源】")
    api_provider = APIResourceProvider("https://api.example.com")

    # 註冊 API 端點
    endpoint = api_provider.register_endpoint(
        "/v1/users",
        "GET",
        "獲取用戶列表"
    )
    print(f"註冊 API 端點: {endpoint.uri}")

    # 4. 資源管理器
    print("\n【示例 4：統一資源管理】")
    manager = ResourceManager()

    # 註冊提供器
    manager.register_provider("db", db_provider)
    manager.register_provider("api", api_provider)

    # 列出所有資源
    all_resources = await manager.list_all_resources()
    print(f"\n所有資源 ({len(all_resources)}):")
    for res in all_resources:
        print(f"  • {res.uri}")
        print(f"    {res.description}")

    # 5. 資源訂閱
    print("\n【示例 5：資源訂閱】")
    manager.subscribe(users_table.uri, "client-123")
    manager.subscribe(users_table.uri, "client-456")

    # 通知變更
    await manager.notify_change(users_table.uri, "updated")

    print("\n" + "=" * 70)
    print("下一步：查看 07_提示模板.py 學習 MCP 提示")
    print("=" * 70)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
