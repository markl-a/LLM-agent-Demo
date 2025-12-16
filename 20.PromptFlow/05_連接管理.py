"""
PromptFlow 連接管理範例
======================

本範例展示如何在 PromptFlow 中管理各種連接。

連接類型：
1. Azure OpenAI 連接
2. OpenAI 連接
3. 自定義 LLM 連接
4. 向量數據庫連接
5. API 連接

安裝依賴：
pip install promptflow promptflow-tools
"""

import os
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

# ============================================================
# 連接類型枚舉
# ============================================================

class ConnectionType(Enum):
    """連接類型"""
    AZURE_OPENAI = "azure_openai"
    OPENAI = "openai"
    CUSTOM_LLM = "custom_llm"
    VECTOR_DB = "vector_db"
    API = "api"
    SERP = "serp"
    COGNITIVE_SEARCH = "cognitive_search"


# ============================================================
# 基礎連接類
# ============================================================

@dataclass
class BaseConnection(ABC):
    """
    基礎連接類

    所有連接類型的基類
    """
    name: str
    connection_type: ConnectionType
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)

    @abstractmethod
    def validate(self) -> bool:
        """驗證連接配置"""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        pass


# ============================================================
# Azure OpenAI 連接
# ============================================================

@dataclass
class AzureOpenAIConnection(BaseConnection):
    """
    Azure OpenAI 連接

    用於連接 Azure OpenAI 服務
    """
    api_key: str = ""
    api_base: str = ""
    api_version: str = "2024-02-15-preview"
    deployment_name: str = ""
    connection_type: ConnectionType = ConnectionType.AZURE_OPENAI

    def validate(self) -> bool:
        """驗證連接配置"""
        if not self.api_key:
            return False
        if not self.api_base:
            return False
        if not self.deployment_name:
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "name": self.name,
            "type": self.connection_type.value,
            "api_key": "***" if self.api_key else "",  # 隱藏敏感信息
            "api_base": self.api_base,
            "api_version": self.api_version,
            "deployment_name": self.deployment_name
        }

    @classmethod
    def from_env(cls, name: str = "azure_openai") -> "AzureOpenAIConnection":
        """從環境變數創建連接"""
        return cls(
            name=name,
            api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
            api_base=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
        )


# ============================================================
# OpenAI 連接
# ============================================================

@dataclass
class OpenAIConnection(BaseConnection):
    """
    OpenAI 連接

    用於連接 OpenAI API
    """
    api_key: str = ""
    organization: str = ""
    base_url: str = "https://api.openai.com/v1"
    connection_type: ConnectionType = ConnectionType.OPENAI

    def validate(self) -> bool:
        """驗證連接配置"""
        return bool(self.api_key)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "name": self.name,
            "type": self.connection_type.value,
            "api_key": "***" if self.api_key else "",
            "organization": self.organization,
            "base_url": self.base_url
        }

    @classmethod
    def from_env(cls, name: str = "openai") -> "OpenAIConnection":
        """從環境變數創建連接"""
        return cls(
            name=name,
            api_key=os.getenv("OPENAI_API_KEY", ""),
            organization=os.getenv("OPENAI_ORG_ID", "")
        )


# ============================================================
# 自定義 LLM 連接
# ============================================================

@dataclass
class CustomLLMConnection(BaseConnection):
    """
    自定義 LLM 連接

    用於連接自定義或本地 LLM
    """
    endpoint: str = ""
    api_key: str = ""
    model_name: str = ""
    extra_headers: Dict[str, str] = field(default_factory=dict)
    connection_type: ConnectionType = ConnectionType.CUSTOM_LLM

    def validate(self) -> bool:
        """驗證連接配置"""
        return bool(self.endpoint)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "name": self.name,
            "type": self.connection_type.value,
            "endpoint": self.endpoint,
            "api_key": "***" if self.api_key else "",
            "model_name": self.model_name,
            "extra_headers": self.extra_headers
        }


# ============================================================
# 向量數據庫連接
# ============================================================

@dataclass
class VectorDBConnection(BaseConnection):
    """
    向量數據庫連接

    支持多種向量數據庫
    """
    db_type: str = ""  # pinecone, weaviate, qdrant, etc.
    host: str = ""
    port: int = 0
    api_key: str = ""
    index_name: str = ""
    namespace: str = ""
    connection_type: ConnectionType = ConnectionType.VECTOR_DB

    def validate(self) -> bool:
        """驗證連接配置"""
        if not self.db_type:
            return False
        if self.db_type in ["pinecone", "weaviate"] and not self.api_key:
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "name": self.name,
            "type": self.connection_type.value,
            "db_type": self.db_type,
            "host": self.host,
            "port": self.port,
            "api_key": "***" if self.api_key else "",
            "index_name": self.index_name,
            "namespace": self.namespace
        }


# ============================================================
# API 連接
# ============================================================

@dataclass
class APIConnection(BaseConnection):
    """
    通用 API 連接

    用於連接外部 API
    """
    base_url: str = ""
    api_key: str = ""
    auth_type: str = "bearer"  # bearer, api_key, basic
    headers: Dict[str, str] = field(default_factory=dict)
    connection_type: ConnectionType = ConnectionType.API

    def validate(self) -> bool:
        """驗證連接配置"""
        return bool(self.base_url)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "name": self.name,
            "type": self.connection_type.value,
            "base_url": self.base_url,
            "api_key": "***" if self.api_key else "",
            "auth_type": self.auth_type,
            "headers": self.headers
        }


# ============================================================
# 連接管理器
# ============================================================

class ConnectionManager:
    """
    連接管理器

    統一管理所有連接
    """

    def __init__(self):
        self.connections: Dict[str, BaseConnection] = {}

    def add(self, connection: BaseConnection):
        """添加連接"""
        if not connection.validate():
            raise ValueError(f"連接配置無效: {connection.name}")
        self.connections[connection.name] = connection

    def get(self, name: str) -> Optional[BaseConnection]:
        """獲取連接"""
        return self.connections.get(name)

    def remove(self, name: str) -> bool:
        """移除連接"""
        if name in self.connections:
            del self.connections[name]
            return True
        return False

    def list(self) -> List[str]:
        """列出所有連接"""
        return list(self.connections.keys())

    def list_by_type(self, conn_type: ConnectionType) -> List[str]:
        """按類型列出連接"""
        return [
            name for name, conn in self.connections.items()
            if conn.connection_type == conn_type
        ]

    def export_config(self) -> Dict[str, Any]:
        """導出配置"""
        return {
            name: conn.to_dict()
            for name, conn in self.connections.items()
        }

    def save_to_file(self, file_path: str):
        """保存到文件"""
        config = self.export_config()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, file_path: str) -> "ConnectionManager":
        """從文件加載"""
        manager = cls()
        with open(file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        # 注意：實際使用時需要根據類型創建對應的連接對象
        return manager


# ============================================================
# PromptFlow CLI 命令模擬
# ============================================================

class PFConnectionCLI:
    """
    模擬 PromptFlow CLI 連接命令

    pf connection create/list/show/delete
    """

    def __init__(self, manager: ConnectionManager):
        self.manager = manager

    def create_azure_openai(
        self,
        name: str,
        api_key: str,
        api_base: str,
        api_version: str,
        deployment_name: str
    ) -> str:
        """創建 Azure OpenAI 連接"""
        conn = AzureOpenAIConnection(
            name=name,
            api_key=api_key,
            api_base=api_base,
            api_version=api_version,
            deployment_name=deployment_name
        )
        self.manager.add(conn)
        return f"連接 '{name}' 創建成功"

    def create_openai(
        self,
        name: str,
        api_key: str,
        organization: str = ""
    ) -> str:
        """創建 OpenAI 連接"""
        conn = OpenAIConnection(
            name=name,
            api_key=api_key,
            organization=organization
        )
        self.manager.add(conn)
        return f"連接 '{name}' 創建成功"

    def list(self) -> List[Dict[str, Any]]:
        """列出連接"""
        return [
            {"name": name, "type": conn.connection_type.value}
            for name, conn in self.manager.connections.items()
        ]

    def show(self, name: str) -> Optional[Dict[str, Any]]:
        """顯示連接詳情"""
        conn = self.manager.get(name)
        return conn.to_dict() if conn else None

    def delete(self, name: str) -> str:
        """刪除連接"""
        if self.manager.remove(name):
            return f"連接 '{name}' 已刪除"
        return f"連接 '{name}' 不存在"


# ============================================================
# 使用範例
# ============================================================

def example_azure_openai_connection():
    """
    範例 1: Azure OpenAI 連接

    展示如何創建和使用 Azure OpenAI 連接
    """
    print("=" * 50)
    print("範例 1: Azure OpenAI 連接")
    print("=" * 50)

    # 從環境變數創建
    conn = AzureOpenAIConnection.from_env("my_azure_openai")

    print(f"連接名稱: {conn.name}")
    print(f"連接類型: {conn.connection_type.value}")
    print(f"API 版本: {conn.api_version}")
    print(f"配置有效: {conn.validate()}")


def example_openai_connection():
    """
    範例 2: OpenAI 連接

    展示如何創建 OpenAI 連接
    """
    print("\n" + "=" * 50)
    print("範例 2: OpenAI 連接")
    print("=" * 50)

    conn = OpenAIConnection(
        name="my_openai",
        api_key="sk-xxx",
        organization="org-xxx"
    )

    print(f"連接配置: {conn.to_dict()}")


def example_custom_llm():
    """
    範例 3: 自定義 LLM 連接

    展示如何連接本地或自定義 LLM
    """
    print("\n" + "=" * 50)
    print("範例 3: 自定義 LLM 連接")
    print("=" * 50)

    # Ollama 連接示例
    ollama_conn = CustomLLMConnection(
        name="ollama_local",
        endpoint="http://localhost:11434/api/generate",
        model_name="llama2"
    )

    print(f"Ollama 連接: {ollama_conn.to_dict()}")

    # vLLM 連接示例
    vllm_conn = CustomLLMConnection(
        name="vllm_server",
        endpoint="http://localhost:8000/v1/completions",
        model_name="mistral-7b",
        extra_headers={"X-Custom-Header": "value"}
    )

    print(f"vLLM 連接: {vllm_conn.to_dict()}")


def example_vector_db():
    """
    範例 4: 向量數據庫連接

    展示如何連接向量數據庫
    """
    print("\n" + "=" * 50)
    print("範例 4: 向量數據庫連接")
    print("=" * 50)

    # Pinecone 連接
    pinecone_conn = VectorDBConnection(
        name="pinecone_index",
        db_type="pinecone",
        api_key="xxx",
        index_name="my-index",
        namespace="default"
    )

    print(f"Pinecone 連接: {pinecone_conn.to_dict()}")

    # Qdrant 連接
    qdrant_conn = VectorDBConnection(
        name="qdrant_local",
        db_type="qdrant",
        host="localhost",
        port=6333
    )

    print(f"Qdrant 連接: {qdrant_conn.to_dict()}")


def example_connection_manager():
    """
    範例 5: 連接管理器

    展示如何統一管理連接
    """
    print("\n" + "=" * 50)
    print("範例 5: 連接管理器")
    print("=" * 50)

    manager = ConnectionManager()

    # 添加多個連接
    manager.add(OpenAIConnection(name="openai_1", api_key="sk-xxx"))
    manager.add(AzureOpenAIConnection(
        name="azure_1",
        api_key="xxx",
        api_base="https://xxx.openai.azure.com",
        deployment_name="gpt-4"
    ))
    manager.add(CustomLLMConnection(
        name="local_llm",
        endpoint="http://localhost:8000"
    ))

    # 列出連接
    print(f"所有連接: {manager.list()}")
    print(f"OpenAI 連接: {manager.list_by_type(ConnectionType.OPENAI)}")
    print(f"Azure 連接: {manager.list_by_type(ConnectionType.AZURE_OPENAI)}")

    # 導出配置
    config = manager.export_config()
    print(f"\n導出配置:")
    print(json.dumps(config, indent=2, ensure_ascii=False))


def example_cli_commands():
    """
    範例 6: CLI 命令模擬

    展示 PromptFlow CLI 連接命令
    """
    print("\n" + "=" * 50)
    print("範例 6: CLI 命令模擬")
    print("=" * 50)

    manager = ConnectionManager()
    cli = PFConnectionCLI(manager)

    # 創建連接
    result = cli.create_openai(
        name="my_openai",
        api_key="sk-test"
    )
    print(f"創建: {result}")

    result = cli.create_azure_openai(
        name="my_azure",
        api_key="xxx",
        api_base="https://xxx.openai.azure.com",
        api_version="2024-02-15-preview",
        deployment_name="gpt-4"
    )
    print(f"創建: {result}")

    # 列出連接
    connections = cli.list()
    print(f"\n連接列表:")
    for conn in connections:
        print(f"  - {conn['name']} ({conn['type']})")

    # 顯示詳情
    details = cli.show("my_openai")
    print(f"\n連接詳情: {details}")

    # 刪除連接
    result = cli.delete("my_openai")
    print(f"\n{result}")


def example_yaml_config():
    """
    範例 7: YAML 配置格式

    展示 PromptFlow 連接的 YAML 配置格式
    """
    print("\n" + "=" * 50)
    print("範例 7: YAML 配置格式")
    print("=" * 50)

    yaml_config = """
# connections.yaml - PromptFlow 連接配置

# Azure OpenAI 連接
azure_openai:
  type: azure_openai
  api_key: ${AZURE_OPENAI_API_KEY}
  api_base: ${AZURE_OPENAI_ENDPOINT}
  api_version: "2024-02-15-preview"
  deployment_name: "gpt-4"

# OpenAI 連接
openai:
  type: openai
  api_key: ${OPENAI_API_KEY}
  organization: ${OPENAI_ORG_ID}

# 自定義連接
custom_llm:
  type: custom
  endpoint: "http://localhost:8000/v1"
  model: "llama2"

# Serp API 連接（用於搜索）
serp:
  type: serp
  api_key: ${SERP_API_KEY}

# Cognitive Search 連接
cognitive_search:
  type: cognitive_search
  api_key: ${AZURE_SEARCH_API_KEY}
  endpoint: ${AZURE_SEARCH_ENDPOINT}
  index_name: "my-index"
"""

    print("YAML 配置示例:")
    print(yaml_config)


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    print("PromptFlow 連接管理範例")
    print()

    example_azure_openai_connection()
    example_openai_connection()
    example_custom_llm()
    example_vector_db()
    example_connection_manager()
    example_cli_commands()
    example_yaml_config()
