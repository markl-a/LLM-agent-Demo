"""
PromptFlow Azure 整合示例

本示例展示：
1. Azure OpenAI 連接
2. Azure ML 整合
3. Azure Key Vault
4. Application Insights 監控
"""

import os
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

console = Console()


def show_azure_openai_connection():
    """Azure OpenAI 連接配置"""
    console.print("\n[cyan]1. Azure OpenAI 連接[/cyan]\n")

    console.print("[yellow]創建連接配置文件:[/yellow]\n")

    # 連接配置
    connection_yaml = """# .promptflow/connections/azure_openai.yaml
$schema: https://azuremlschemas.azureedge.net/promptflow/latest/AzureOpenAIConnection.schema.json

name: azure_openai_connection
type: azure_open_ai

# API 配置
api_base: ${env:AZURE_OPENAI_ENDPOINT}
api_key: ${env:AZURE_OPENAI_KEY}
api_version: "2024-02-15-preview"
api_type: azure

# 可選配置
organization: ""
"""

    syntax = Syntax(connection_yaml, "yaml", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()

    console.print("[yellow]使用 CLI 創建連接:[/yellow]\n")

    cli_commands = """# 創建 Azure OpenAI 連接
pf connection create \\
  --file connections/azure_openai.yaml

# 列出所有連接
pf connection list

# 查看連接詳情
pf connection show --name azure_openai_connection

# 更新連接
pf connection update \\
  --name azure_openai_connection \\
  --set api_key=new_key

# 刪除連接
pf connection delete --name azure_openai_connection"""

    syntax = Syntax(cli_commands, "bash", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_azure_ml_integration():
    """Azure ML 整合"""
    console.print("[cyan]2. Azure ML 工作區整合[/cyan]\n")

    console.print("[yellow]配置 Azure ML 工作區:[/yellow]\n")

    config_code = """# 安裝 Azure ML SDK
# pip install azure-ai-ml azure-identity

from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

# 創建 ML 客戶端
ml_client = MLClient(
    credential=DefaultAzureCredential(),
    subscription_id="your-subscription-id",
    resource_group_name="your-resource-group",
    workspace_name="your-workspace-name"
)

print(f"已連接到工作區: {ml_client.workspace_name}")"""

    syntax = Syntax(config_code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()

    console.print("[yellow]在 Azure ML 中運行 Flow:[/yellow]\n")

    run_code = """from azure.ai.ml import MLClient, load_flow
from azure.identity import DefaultAzureCredential

# 連接到 Azure ML
ml_client = MLClient.from_config(DefaultAzureCredential())

# 加載 Flow
flow = load_flow(source="./my_flow")

# 創建運行
run = ml_client.flows.create_or_update(
    flow=flow,
    data="./test_data.jsonl",
    column_mapping={
        "question": "${data.question}",
        "context": "${data.context}"
    },
    name="azure_ml_run"
)

# 等待完成
ml_client.flows.stream(run)

# 獲取結果
metrics = ml_client.flows.get_metrics(run.name)
print(f"運行指標: {metrics}")"""

    syntax = Syntax(run_code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_key_vault_integration():
    """Azure Key Vault 整合"""
    console.print("[cyan]3. Azure Key Vault 密鑰管理[/cyan]\n")

    console.print("[yellow]設置 Key Vault:[/yellow]\n")

    keyvault_setup = """# 安裝 Azure Key Vault SDK
# pip install azure-keyvault-secrets azure-identity

from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

# 創建 Key Vault 客戶端
key_vault_uri = "https://your-keyvault.vault.azure.net/"
credential = DefaultAzureCredential()
client = SecretClient(vault_url=key_vault_uri, credential=credential)

# 存儲密鑰
client.set_secret("openai-api-key", "your-secret-key")
client.set_secret("openai-endpoint", "your-endpoint")

print("密鑰已存儲到 Key Vault")"""

    syntax = Syntax(keyvault_setup, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()

    console.print("[yellow]在 Flow 中使用 Key Vault:[/yellow]\n")

    flow_code = """from promptflow import tool
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
import os

# 初始化 Key Vault 客戶端
_kv_client = None

def get_secret(secret_name: str) -> str:
    \"\"\"從 Key Vault 獲取密鑰\"\"\"
    global _kv_client

    if _kv_client is None:
        key_vault_uri = os.getenv("KEY_VAULT_URI")
        credential = DefaultAzureCredential()
        _kv_client = SecretClient(vault_url=key_vault_uri, credential=credential)

    secret = _kv_client.get_secret(secret_name)
    return secret.value


@tool
def secure_api_call(question: str) -> str:
    \"\"\"使用 Key Vault 中的密鑰進行安全 API 調用\"\"\"

    # 從 Key Vault 獲取密鑰
    api_key = get_secret("openai-api-key")
    endpoint = get_secret("openai-endpoint")

    # 使用密鑰調用 API
    # ...

    return "處理完成"
"""

    syntax = Syntax(flow_code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_app_insights_monitoring():
    """Application Insights 監控"""
    console.print("[cyan]4. Application Insights 監控[/cyan]\n")

    console.print("[yellow]配置 Application Insights:[/yellow]\n")

    appinsights_setup = """# 安裝 SDK
# pip install opencensus-ext-azure

import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler

# 配置日誌處理器
logger = logging.getLogger(__name__)
logger.addHandler(
    AzureLogHandler(
        connection_string='InstrumentationKey=your-instrumentation-key'
    )
)
logger.setLevel(logging.INFO)

# 記錄日誌
logger.info("Flow 已啟動")"""

    syntax = Syntax(appinsights_setup, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()

    console.print("[yellow]在 Flow 中添加遙測:[/yellow]\n")

    telemetry_code = """from promptflow import tool
from opencensus.ext.azure import metrics_exporter
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module
from opencensus.tags import tag_map as tag_map_module
import time

# 設置指標導出器
exporter = metrics_exporter.new_metrics_exporter(
    connection_string='InstrumentationKey=your-key'
)

# 定義指標
stats = stats_module.stats
view_manager = stats.view_manager
view_manager.register_exporter(exporter)

# 創建度量
latency_measure = measure_module.MeasureFloat(
    "flow_latency",
    "Flow execution latency",
    "ms"
)

token_measure = measure_module.MeasureInt(
    "token_usage",
    "Token usage",
    "tokens"
)


@tool
def monitored_process(input_text: str) -> dict:
    \"\"\"帶監控的處理函數\"\"\"
    mmap = stats.stats_recorder.new_measurement_map()
    tmap = tag_map_module.TagMap()

    start_time = time.time()

    try:
        # 處理邏輯
        result = process_input(input_text)

        # 記錄指標
        latency = (time.time() - start_time) * 1000
        mmap.measure_float_put(latency_measure, latency)
        mmap.measure_int_put(token_measure, result['tokens'])

        # 添加標籤
        tmap.insert("status", "success")
        tmap.insert("input_length", str(len(input_text)))

        mmap.record(tmap)

        return result

    except Exception as e:
        # 記錄失敗
        tmap.insert("status", "failed")
        tmap.insert("error", str(e))
        mmap.record(tmap)
        raise
"""

    syntax = Syntax(telemetry_code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_azure_storage_integration():
    """Azure Storage 整合"""
    console.print("[cyan]5. Azure Storage 整合[/cyan]\n")

    storage_code = """# 使用 Azure Blob Storage 存儲結果
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
import json

@tool
def save_to_blob(data: dict, container_name: str, blob_name: str) -> str:
    \"\"\"保存數據到 Azure Blob Storage\"\"\"

    # 連接到 Blob Storage
    account_url = "https://your-account.blob.core.windows.net"
    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(
        account_url=account_url,
        credential=credential
    )

    # 獲取容器客戶端
    container_client = blob_service_client.get_container_client(container_name)

    # 上傳數據
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(
        json.dumps(data, ensure_ascii=False),
        overwrite=True
    )

    return f"已保存到: {container_name}/{blob_name}"


@tool
def load_from_blob(container_name: str, blob_name: str) -> dict:
    \"\"\"從 Azure Blob Storage 讀取數據\"\"\"

    account_url = "https://your-account.blob.core.windows.net"
    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(
        account_url=account_url,
        credential=credential
    )

    # 下載數據
    blob_client = blob_service_client.get_blob_client(
        container=container_name,
        blob=blob_name
    )
    data = blob_client.download_blob().readall()

    return json.loads(data)
"""

    syntax = Syntax(storage_code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_managed_identity():
    """託管標識"""
    console.print("[cyan]6. Azure 託管標識[/cyan]\n")

    identity_code = """# 使用系統分配的託管標識
from azure.identity import ManagedIdentityCredential, ChainedTokenCredential, DefaultAzureCredential

# 方式 1: 系統分配的標識
system_credential = ManagedIdentityCredential()

# 方式 2: 用戶分配的標識
user_credential = ManagedIdentityCredential(
    client_id="your-client-id"
)

# 方式 3: 鏈式憑證（本地開發 + 生產）
credential = ChainedTokenCredential(
    ManagedIdentityCredential(),  # 生產環境
    DefaultAzureCredential()       # 本地開發
)

# 使用託管標識訪問服務
from azure.keyvault.secrets import SecretClient

key_vault_uri = "https://your-keyvault.vault.azure.net/"
client = SecretClient(vault_url=key_vault_uri, credential=credential)

secret = client.get_secret("my-secret")
print(f"密鑰值: {secret.value}")"""

    syntax = Syntax(identity_code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_best_practices():
    """Azure 整合最佳實踐"""
    console.print("[cyan]Azure 整合最佳實踐[/cyan]\n")

    practices = """1. 安全性
   - 使用託管標識而非密鑰
   - 將密鑰存儲在 Key Vault
   - 啟用網絡隔離
   - 實施最小權限原則

2. 成本優化
   - 選擇合適的定價層
   - 使用預留容量
   - 監控資源使用
   - 自動擴展配置

3. 可靠性
   - 跨區域部署
   - 實施重試邏輯
   - 配置備份
   - 監控健康狀態

4. 性能
   - 使用 CDN 加速
   - 啟用緩存
   - 優化網絡配置
   - 並行處理

5. 監控和診斷
   - Application Insights 遙測
   - 日誌分析
   - 性能分析器
   - 告警規則

6. DevOps
   - Infrastructure as Code
   - CI/CD 自動化
   - 環境隔離
   - 版本控制"""

    console.print(Panel(practices, border_style="cyan"))
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]PromptFlow Azure 整合示例[/bold cyan]\n"
        "[dim]學習如何整合 Azure 服務[/dim]",
        border_style="cyan"
    ))

    # 1. Azure OpenAI 連接
    show_azure_openai_connection()

    # 2. Azure ML 整合
    show_azure_ml_integration()

    # 3. Key Vault
    show_key_vault_integration()

    # 4. Application Insights
    show_app_insights_monitoring()

    # 5. Azure Storage
    show_azure_storage_integration()

    # 6. 託管標識
    show_managed_identity()

    # 7. 最佳實踐
    show_best_practices()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ Azure 整合示例完成！[/bold green]\n")
    console.print("[cyan]下一步:[/cyan]")
    console.print("  1. 查看 10_最佳實踐.py - 學習生產級最佳實踐")
    console.print("  2. 實踐: 配置 Azure 服務並整合到 Flow")
    console.print("  3. 探索: Azure 文檔和最佳實踐")


if __name__ == "__main__":
    main()
