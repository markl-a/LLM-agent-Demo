"""
PromptFlow 部署服務示例

本示例展示：
1. 本地服務部署
2. Docker 容器化
3. Azure 部署
4. API 調用示例
"""

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

console = Console()


def show_local_deployment():
    """本地部署"""
    console.print("\n[cyan]1. 本地服務部署[/cyan]\n")

    console.print("[yellow]快速啟動本地服務:[/yellow]\n")

    commands = """# 基本啟動
pf flow serve --source ./my_flow --port 8080 --host localhost

# 帶環境變量
pf flow serve \\
  --source ./my_flow \\
  --port 8080 \\
  --environment-variables \\
    AZURE_OPENAI_KEY=your_key \\
    AZURE_OPENAI_ENDPOINT=your_endpoint

# 帶靜態文件夾
pf flow serve \\
  --source ./my_flow \\
  --port 8080 \\
  --static-folder ./static

# 啟用自動重載（開發模式）
pf flow serve \\
  --source ./my_flow \\
  --port 8080 \\
  --reload"""

    syntax = Syntax(commands, "bash", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()

    console.print("[green]✓ 服務將運行在: http://localhost:8080[/green]\n")


def show_api_usage():
    """API 調用示例"""
    console.print("[cyan]2. API 調用示例[/cyan]\n")

    # Swagger UI
    console.print("[yellow]Swagger UI:[/yellow]")
    console.print("  訪問 http://localhost:8080/docs 查看 API 文檔\n")

    # cURL 示例
    curl_example = """# 使用 cURL 調用
curl -X POST http://localhost:8080/score \\
  -H "Content-Type: application/json" \\
  -d '{
    "question": "什麼是 PromptFlow？",
    "context": "PromptFlow 是微軟的提示工程工具"
  }'"""

    syntax = Syntax(curl_example, "bash", theme="monokai")
    console.print("[dim]cURL 示例:[/dim]")
    console.print(syntax)
    console.print()

    # Python 示例
    python_example = """import requests
import json

# API 端點
url = "http://localhost:8080/score"

# 請求數據
payload = {
    "question": "什麼是 PromptFlow？",
    "context": "PromptFlow 是微軟的提示工程工具"
}

# 發送請求
response = requests.post(
    url,
    headers={"Content-Type": "application/json"},
    json=payload
)

# 處理響應
if response.status_code == 200:
    result = response.json()
    print(f"答案: {result['answer']}")
else:
    print(f"錯誤: {response.status_code}")"""

    syntax = Syntax(python_example, "python", theme="monokai", line_numbers=True)
    console.print("[dim]Python 示例:[/dim]")
    console.print(syntax)
    console.print()

    # JavaScript 示例
    js_example = """// 使用 Fetch API
async function callFlowAPI(question, context) {
  const response = await fetch('http://localhost:8080/score', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question: question,
      context: context
    })
  });

  const result = await response.json();
  return result;
}

// 使用示例
callFlowAPI(
  "什麼是 PromptFlow？",
  "PromptFlow 是微軟的提示工程工具"
).then(result => {
  console.log("答案:", result.answer);
});"""

    syntax = Syntax(js_example, "javascript", theme="monokai", line_numbers=True)
    console.print("[dim]JavaScript 示例:[/dim]")
    console.print(syntax)
    console.print()


def show_docker_deployment():
    """Docker 部署"""
    console.print("[cyan]3. Docker 容器化部署[/cyan]\n")

    console.print("[yellow]步驟 1: 構建 Docker 鏡像[/yellow]\n")

    build_commands = """# 使用 PromptFlow 構建工具
pf flow build \\
  --source ./my_flow \\
  --output ./docker_build \\
  --format docker

# 生成的目錄結構
docker_build/
  ├── Dockerfile
  ├── flow/
  ├── connections/
  └── requirements.txt"""

    syntax = Syntax(build_commands, "bash", theme="monokai")
    console.print(syntax)
    console.print()

    console.print("[yellow]步驟 2: 構建和運行容器[/yellow]\n")

    docker_commands = """# 構建鏡像
cd docker_build
docker build -t my-flow-app:latest .

# 運行容器
docker run -d \\
  -p 8080:8080 \\
  -e AZURE_OPENAI_KEY=your_key \\
  -e AZURE_OPENAI_ENDPOINT=your_endpoint \\
  --name my-flow-container \\
  my-flow-app:latest

# 查看日誌
docker logs my-flow-container

# 停止容器
docker stop my-flow-container

# 刪除容器
docker rm my-flow-container"""

    syntax = Syntax(docker_commands, "bash", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()

    console.print("[yellow]步驟 3: 自定義 Dockerfile（可選）[/yellow]\n")

    dockerfile = """FROM python:3.10-slim

WORKDIR /app

# 複製依賴文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製 Flow 文件
COPY flow/ ./flow/
COPY connections/ ./connections/

# 暴露端口
EXPOSE 8080

# 啟動命令
CMD ["pf", "flow", "serve", "--source", "./flow", "--port", "8080", "--host", "0.0.0.0"]"""

    syntax = Syntax(dockerfile, "dockerfile", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_azure_deployment():
    """Azure 部署"""
    console.print("[cyan]4. Azure 部署[/cyan]\n")

    console.print("[yellow]方式 1: Azure ML 部署[/yellow]\n")

    azure_ml_commands = """# 前提：已配置 Azure ML 工作區

# 步驟 1: 創建在線端點
az ml online-endpoint create \\
  --name my-flow-endpoint \\
  --resource-group my-rg \\
  --workspace-name my-workspace

# 步驟 2: 部署 Flow
pf flow build \\
  --source ./my_flow \\
  --output ./azure_build \\
  --format docker

az ml online-deployment create \\
  --name my-deployment \\
  --endpoint my-flow-endpoint \\
  --model-path ./azure_build \\
  --instance-type Standard_DS3_v2 \\
  --instance-count 1

# 步驟 3: 分配流量
az ml online-endpoint update \\
  --name my-flow-endpoint \\
  --traffic "my-deployment=100"

# 步驟 4: 測試端點
az ml online-endpoint invoke \\
  --name my-flow-endpoint \\
  --request-file test_request.json"""

    syntax = Syntax(azure_ml_commands, "bash", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()

    console.print("[yellow]方式 2: Azure Container Apps 部署[/yellow]\n")

    aca_commands = """# 步驟 1: 推送鏡像到 Azure Container Registry
az acr build \\
  --registry myregistry \\
  --image my-flow-app:v1 \\
  ./docker_build

# 步驟 2: 創建 Container App
az containerapp create \\
  --name my-flow-app \\
  --resource-group my-rg \\
  --environment my-env \\
  --image myregistry.azurecr.io/my-flow-app:v1 \\
  --target-port 8080 \\
  --ingress external \\
  --cpu 1.0 \\
  --memory 2.0Gi \\
  --min-replicas 1 \\
  --max-replicas 5

# 步驟 3: 獲取端點 URL
az containerapp show \\
  --name my-flow-app \\
  --resource-group my-rg \\
  --query properties.configuration.ingress.fqdn"""

    syntax = Syntax(aca_commands, "bash", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_deployment_config():
    """部署配置"""
    console.print("[cyan]5. 部署配置文件[/cyan]\n")

    config = """# deployment.yaml
$schema: https://azuremlschemas.azureedge.net/latest/onlineDeployment.schema.json

name: my-flow-deployment
endpoint_name: my-flow-endpoint

model:
  path: ./flow

code_configuration:
  code: ./flow
  scoring_script: score.py

environment:
  image: mcr.microsoft.com/azureml/promptflow/promptflow-runtime:latest
  inference_config:
    liveness_route:
      path: /health
      port: 8080
    readiness_route:
      path: /health
      port: 8080
    scoring_route:
      path: /score
      port: 8080

instance_type: Standard_DS3_v2
instance_count: 1

environment_variables:
  AZURE_OPENAI_KEY: "{{azureml.secret:openai-key}}"
  AZURE_OPENAI_ENDPOINT: "{{azureml.secret:openai-endpoint}}"

request_settings:
  request_timeout_ms: 60000
  max_concurrent_requests_per_instance: 10

liveness_probe:
  initial_delay: 10
  period: 10
  timeout: 2
  success_threshold: 1
  failure_threshold: 3"""

    syntax = Syntax(config, "yaml", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_monitoring():
    """監控和日誌"""
    console.print("[cyan]6. 監控和日誌[/cyan]\n")

    monitoring_code = """# 添加監控到 Flow
from promptflow import tool
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@tool
def monitored_llm_call(question: str) -> dict:
    \"\"\"帶監控的 LLM 調用\"\"\"

    start_time = datetime.now()

    try:
        # LLM 調用
        response = call_llm(question)

        # 記錄成功
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"LLM 調用成功", extra={
            "duration": duration,
            "tokens": len(response.split()),
            "question_length": len(question)
        })

        return {
            "success": True,
            "answer": response,
            "latency": duration
        }

    except Exception as e:
        # 記錄失敗
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(f"LLM 調用失敗: {e}", extra={
            "duration": duration,
            "error": str(e)
        })

        return {
            "success": False,
            "error": str(e),
            "latency": duration
        }"""

    syntax = Syntax(monitoring_code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_best_practices():
    """部署最佳實踐"""
    console.print("[cyan]部署最佳實踐[/cyan]\n")

    practices = """1. 環境管理
   - 使用環境變量存儲敏感信息
   - 不要在代碼中硬編碼密鑰
   - 使用 Azure Key Vault

2. 性能優化
   - 啟用連接池
   - 設置合理的超時時間
   - 使用異步處理

3. 可靠性
   - 實施健康檢查
   - 配置自動重試
   - 設置告警

4. 擴展性
   - 使用自動擴展
   - 負載均衡
   - 緩存策略

5. 安全性
   - API 身份驗證
   - 速率限制
   - 輸入驗證

6. 監控
   - 記錄關鍵指標
   - 追蹤錯誤
   - 性能分析"""

    console.print(Panel(practices, border_style="cyan"))
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]PromptFlow 部署服務示例[/bold cyan]\n"
        "[dim]學習如何部署 Flow 為生產服務[/dim]",
        border_style="cyan"
    ))

    # 1. 本地部署
    show_local_deployment()

    # 2. API 調用
    show_api_usage()

    # 3. Docker 部署
    show_docker_deployment()

    # 4. Azure 部署
    show_azure_deployment()

    # 5. 部署配置
    show_deployment_config()

    # 6. 監控
    show_monitoring()

    # 7. 最佳實踐
    show_best_practices()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 部署服務示例完成！[/bold green]\n")
    console.print("[cyan]下一步:[/cyan]")
    console.print("  1. 查看 09_Azure整合.py - 學習 Azure 整合")
    console.print("  2. 查看 10_最佳實踐.py - 學習生產級實踐")
    console.print("  3. 實踐: 部署自己的 Flow 服務")


if __name__ == "__main__":
    main()
