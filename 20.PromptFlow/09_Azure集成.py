"""
PromptFlow Azure 集成範例
=========================

本範例展示如何將 PromptFlow 與 Azure 服務集成。

Azure 集成：
1. Azure OpenAI
2. Azure ML
3. Azure Cognitive Search
4. Azure Blob Storage
5. Azure Key Vault

安裝依賴：
pip install promptflow promptflow-azure azure-identity azure-ai-ml
"""

import os
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# ============================================================
# Azure 配置
# ============================================================

@dataclass
class AzureConfig:
    """Azure 配置"""
    subscription_id: str = ""
    resource_group: str = ""
    workspace_name: str = ""
    location: str = "eastus"

    @classmethod
    def from_env(cls) -> "AzureConfig":
        """從環境變數載入"""
        return cls(
            subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID", ""),
            resource_group=os.getenv("AZURE_RESOURCE_GROUP", ""),
            workspace_name=os.getenv("AZURE_ML_WORKSPACE", ""),
            location=os.getenv("AZURE_LOCATION", "eastus")
        )


# ============================================================
# Azure OpenAI 集成
# ============================================================

AZURE_OPENAI_CONNECTION = '''
# azure_openai_connection.yaml

$schema: https://azuremlschemas.azureedge.net/promptflow/latest/AzureOpenAIConnection.schema.json
name: azure_openai
type: azure_openai

api_key: ${env:AZURE_OPENAI_API_KEY}
api_base: ${env:AZURE_OPENAI_ENDPOINT}
api_version: "2024-02-15-preview"
'''

AZURE_OPENAI_TOOL = '''
# azure_openai_tool.yaml

name: azure_openai_chat
type: llm
source:
  type: code
  path: llm_tool.py

inputs:
  prompt:
    type: string
  deployment_name:
    type: string
    default: gpt-4
  temperature:
    type: float
    default: 0.7

connection: azure_openai
api: chat
'''


class AzureOpenAIClient:
    """
    Azure OpenAI 客戶端

    封裝 Azure OpenAI 的調用
    """

    def __init__(
        self,
        api_key: str,
        endpoint: str,
        api_version: str = "2024-02-15-preview"
    ):
        self.api_key = api_key
        self.endpoint = endpoint
        self.api_version = api_version

    def chat(
        self,
        deployment_name: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        發送聊天請求

        Args:
            deployment_name: 部署名稱
            messages: 消息列表
            temperature: 溫度
            max_tokens: 最大 token 數

        Returns:
            響應結果
        """
        import requests

        url = f"{self.endpoint}/openai/deployments/{deployment_name}/chat/completions"
        params = {"api-version": self.api_version}

        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = requests.post(url, headers=headers, params=params, json=payload)
        response.raise_for_status()

        return response.json()


# ============================================================
# Azure ML 集成
# ============================================================

AZURE_ML_CONFIG = '''
# azure_ml_config.yaml

subscription_id: ${env:AZURE_SUBSCRIPTION_ID}
resource_group: ${env:AZURE_RESOURCE_GROUP}
workspace_name: ${env:AZURE_ML_WORKSPACE}

# 計算資源
compute:
  name: promptflow-compute
  type: managed
  size: Standard_DS3_v2
  min_instances: 0
  max_instances: 4

# 數據存儲
datastore:
  name: promptflow-data
  type: azure_blob
  account_name: ${env:AZURE_STORAGE_ACCOUNT}
  container_name: promptflow-data
'''


class AzureMLWorkspace:
    """
    Azure ML 工作區管理

    管理 Azure ML 資源
    """

    def __init__(self, config: AzureConfig):
        self.config = config
        self._ml_client = None

    def connect(self):
        """連接到工作區"""
        from azure.ai.ml import MLClient
        from azure.identity import DefaultAzureCredential

        self._ml_client = MLClient(
            DefaultAzureCredential(),
            self.config.subscription_id,
            self.config.resource_group,
            self.config.workspace_name
        )
        print(f"已連接到工作區: {self.config.workspace_name}")

    def list_connections(self) -> List[str]:
        """列出連接"""
        if not self._ml_client:
            return []
        connections = self._ml_client.connections.list()
        return [c.name for c in connections]

    def create_compute(
        self,
        name: str,
        vm_size: str = "Standard_DS3_v2",
        min_instances: int = 0,
        max_instances: int = 4
    ):
        """創建計算資源"""
        from azure.ai.ml.entities import AmlCompute

        compute = AmlCompute(
            name=name,
            type="amlcompute",
            size=vm_size,
            min_instances=min_instances,
            max_instances=max_instances
        )

        self._ml_client.compute.begin_create_or_update(compute).result()
        print(f"計算資源已創建: {name}")


# ============================================================
# Azure Cognitive Search 集成
# ============================================================

COGNITIVE_SEARCH_CONNECTION = '''
# cognitive_search_connection.yaml

$schema: https://azuremlschemas.azureedge.net/promptflow/latest/CognitiveSearchConnection.schema.json
name: cognitive_search
type: cognitive_search

api_key: ${env:AZURE_SEARCH_API_KEY}
api_base: ${env:AZURE_SEARCH_ENDPOINT}
api_version: "2023-11-01"
'''


class AzureSearchClient:
    """
    Azure Cognitive Search 客戶端

    封裝搜索功能
    """

    def __init__(self, endpoint: str, api_key: str, index_name: str):
        self.endpoint = endpoint
        self.api_key = api_key
        self.index_name = index_name

    def search(
        self,
        query: str,
        top: int = 5,
        select: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        執行搜索

        Args:
            query: 搜索查詢
            top: 返回結果數
            select: 選擇的字段

        Returns:
            搜索結果列表
        """
        import requests

        url = f"{self.endpoint}/indexes/{self.index_name}/docs/search"
        params = {"api-version": "2023-11-01"}

        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "search": query,
            "top": top
        }

        if select:
            payload["select"] = ",".join(select)

        response = requests.post(url, headers=headers, params=params, json=payload)
        response.raise_for_status()

        return response.json().get("value", [])

    def vector_search(
        self,
        vector: List[float],
        top: int = 5,
        vector_field: str = "embedding"
    ) -> List[Dict[str, Any]]:
        """
        向量搜索

        Args:
            vector: 查詢向量
            top: 返回結果數
            vector_field: 向量字段名

        Returns:
            搜索結果列表
        """
        import requests

        url = f"{self.endpoint}/indexes/{self.index_name}/docs/search"
        params = {"api-version": "2023-11-01"}

        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "vectorQueries": [{
                "kind": "vector",
                "vector": vector,
                "fields": vector_field,
                "k": top
            }]
        }

        response = requests.post(url, headers=headers, params=params, json=payload)
        response.raise_for_status()

        return response.json().get("value", [])


# ============================================================
# 使用範例
# ============================================================

def example_azure_openai():
    """
    範例 1: Azure OpenAI 連接

    展示如何配置 Azure OpenAI 連接
    """
    print("=" * 50)
    print("範例 1: Azure OpenAI 連接")
    print("=" * 50)

    print("Azure OpenAI 連接配置:")
    print(AZURE_OPENAI_CONNECTION)

    print("\nAzure OpenAI Tool 配置:")
    print(AZURE_OPENAI_TOOL)


def example_azure_openai_client():
    """
    範例 2: Azure OpenAI 客戶端

    展示如何使用 Azure OpenAI
    """
    print("\n" + "=" * 50)
    print("範例 2: Azure OpenAI 客戶端")
    print("=" * 50)

    # 模擬客戶端使用
    print("Azure OpenAI 客戶端使用示例:")
    print("""
client = AzureOpenAIClient(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

response = client.chat(
    deployment_name="gpt-4",
    messages=[
        {"role": "system", "content": "你是一個有幫助的助手"},
        {"role": "user", "content": "什麼是機器學習？"}
    ]
)

print(response["choices"][0]["message"]["content"])
""")


def example_azure_ml():
    """
    範例 3: Azure ML 集成

    展示如何與 Azure ML 集成
    """
    print("\n" + "=" * 50)
    print("範例 3: Azure ML 集成")
    print("=" * 50)

    print("Azure ML 配置:")
    print(AZURE_ML_CONFIG)

    print("\nAzure ML CLI 命令:")
    print("""
# 設置默認工作區
az configure --defaults group=<resource_group> workspace=<workspace>

# 創建連接
pf connection create --file azure_openai_connection.yaml

# 列出連接
pf connection list

# 提交 Flow 運行
pf run create --flow ./my_flow --data ./data.jsonl --stream

# 查看運行結果
pf run show --name <run_name>
""")


def example_cognitive_search():
    """
    範例 4: Cognitive Search 集成

    展示如何集成 Azure Cognitive Search
    """
    print("\n" + "=" * 50)
    print("範例 4: Cognitive Search 集成")
    print("=" * 50)

    print("Cognitive Search 連接配置:")
    print(COGNITIVE_SEARCH_CONNECTION)

    print("\n使用示例:")
    print("""
# 在 Flow 中使用 Cognitive Search
from promptflow import tool

@tool
def search_documents(query: str, search_connection: str) -> list:
    from azure.search.documents import SearchClient
    from azure.core.credentials import AzureKeyCredential

    # 從連接獲取配置
    client = SearchClient(
        endpoint=search_connection.api_base,
        index_name="my-index",
        credential=AzureKeyCredential(search_connection.api_key)
    )

    results = client.search(query, top=5)
    return [doc for doc in results]
""")


def example_key_vault():
    """
    範例 5: Key Vault 集成

    展示如何使用 Azure Key Vault
    """
    print("\n" + "=" * 50)
    print("範例 5: Key Vault 集成")
    print("=" * 50)

    print("Key Vault 配置:")
    print("""
# 使用 Key Vault 存儲敏感信息

# 1. 創建 Key Vault
az keyvault create --name my-keyvault --resource-group my-rg

# 2. 設置密鑰
az keyvault secret set --vault-name my-keyvault \\
    --name AZURE-OPENAI-KEY --value <your-api-key>

# 3. 在 PromptFlow 中引用
# connection.yaml
api_key: ${keyvault:my-keyvault/AZURE-OPENAI-KEY}
""")


def example_blob_storage():
    """
    範例 6: Blob Storage 集成

    展示如何使用 Azure Blob Storage
    """
    print("\n" + "=" * 50)
    print("範例 6: Blob Storage 集成")
    print("=" * 50)

    print("Blob Storage 使用示例:")
    print("""
# 在 Flow 中使用 Blob Storage

from azure.storage.blob import BlobServiceClient

@tool
def load_data_from_blob(
    connection_string: str,
    container_name: str,
    blob_name: str
) -> str:
    '''從 Blob 加載數據'''
    blob_service = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service.get_blob_client(container_name, blob_name)

    data = blob_client.download_blob().readall()
    return data.decode('utf-8')

@tool
def save_results_to_blob(
    connection_string: str,
    container_name: str,
    blob_name: str,
    content: str
):
    '''保存結果到 Blob'''
    blob_service = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service.get_blob_client(container_name, blob_name)

    blob_client.upload_blob(content, overwrite=True)
""")


def example_end_to_end():
    """
    範例 7: 端到端 Azure 集成

    展示完整的 Azure 集成流程
    """
    print("\n" + "=" * 50)
    print("範例 7: 端到端 Azure 集成")
    print("=" * 50)

    flow_yaml = """
# flow.dag.yaml - Azure 集成 RAG Flow

inputs:
  question:
    type: string

outputs:
  answer:
    type: string
    reference: ${generate_answer.output}

nodes:
  - name: search_documents
    type: python
    source:
      type: code
      path: search.py
    inputs:
      query: ${inputs.question}
    connection: cognitive_search

  - name: generate_answer
    type: llm
    source:
      type: code
      path: chat.jinja2
    inputs:
      question: ${inputs.question}
      context: ${search_documents.output}
    connection: azure_openai
    api: chat
"""

    print("完整的 Azure RAG Flow:")
    print(flow_yaml)

    print("\n部署流程:")
    print("""
# 1. 設置連接
pf connection create --file azure_openai_connection.yaml
pf connection create --file cognitive_search_connection.yaml

# 2. 測試 Flow
pf flow test --flow . --inputs question="什麼是機器學習？"

# 3. 批量運行
pf run create --flow . --data ./test_data.jsonl

# 4. 部署到 Azure ML
pf flow deploy --source . \\
    --endpoint-name rag-endpoint \\
    --deployment-name v1
""")


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    print("PromptFlow Azure 集成範例")
    print()

    example_azure_openai()
    example_azure_openai_client()
    example_azure_ml()
    example_cognitive_search()
    example_key_vault()
    example_blob_storage()
    example_end_to_end()
