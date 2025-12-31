"""
Microsoft Agent Framework - Azure 部署

這個檔案展示如何將 Agent 部署到 Azure AI Foundry。
Azure AI Foundry 提供企業級的 AI 應用部署和管理平台。

主要內容:
1. Azure AI Foundry 介紹
2. 環境設定和認證
3. Agent 部署配置
4. 監控和日誌
5. 擴展和負載均衡
6. 安全性設定
7. 成本優化
8. CI/CD 整合

作者: Microsoft Agent Framework Team
日期: 2025-12-31
版本: 1.0.0
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

# Azure SDK
try:
    from azure.identity import DefaultAzureCredential, ClientSecretCredential
    from azure.ai.inference import ChatCompletionsClient
    from azure.core.credentials import AzureKeyCredential
    from azure.monitor.opentelemetry import configure_azure_monitor
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    print("⚠️  Azure SDK 未安裝,部分功能將無法使用")

# Agent Framework
from agent_framework import Agent, AgentThread
from agent_framework.models import AzureOpenAIModel
from agent_framework.deployment import DeploymentConfig, AzureDeployment

# ============================================================================
# 1. Azure AI Foundry 介紹
# ============================================================================

def explain_azure_ai_foundry():
    """
    介紹 Azure AI Foundry 平台

    Azure AI Foundry 是微軟的統一 AI 開發和部署平台
    """
    print("="*70)
    print("Azure AI Foundry 介紹")
    print("="*70)

    print("\n📚 Azure AI Foundry 核心功能:")

    features = [
        ("1. 統一開發環境", [
            "整合的 AI 開發體驗",
            "支援多種 AI 模型和框架",
            "豐富的預建 AI 服務"
        ]),
        ("2. 企業級部署", [
            "自動擴展和負載均衡",
            "全球分散式部署",
            "高可用性保證"
        ]),
        ("3. 監控和管理", [
            "即時監控儀表板",
            "詳細的使用分析",
            "成本追蹤和優化"
        ]),
        ("4. 安全性和合規", [
            "企業級安全控制",
            "資料隱私保護",
            "符合各種合規要求"
        ]),
        ("5. 整合生態系", [
            "與 Azure 服務深度整合",
            "支援 DevOps 工作流",
            "豐富的第三方整合"
        ]),
    ]

    for title, points in features:
        print(f"\n   {title}")
        for point in points:
            print(f"      - {point}")


# ============================================================================
# 2. 環境設定
# ============================================================================

class AzureConfig:
    """
    Azure 配置管理

    統一管理 Azure 相關配置
    """

    def __init__(self):
        """載入 Azure 配置"""
        load_dotenv()

        # Azure OpenAI 配置
        self.openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.openai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
        self.openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

        # Azure AI Foundry 配置
        self.ai_project_connection = os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING")
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        self.resource_group = os.getenv("AZURE_RESOURCE_GROUP")
        self.workspace_name = os.getenv("AZURE_WORKSPACE_NAME")

        # 認證配置
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET")

    def validate(self) -> bool:
        """驗證配置完整性"""
        required_fields = [
            ("AZURE_OPENAI_ENDPOINT", self.openai_endpoint),
            ("AZURE_OPENAI_API_KEY", self.openai_api_key),
        ]

        missing = []
        for name, value in required_fields:
            if not value:
                missing.append(name)

        if missing:
            print(f"❌ 缺少必要的環境變數: {', '.join(missing)}")
            return False

        print("✅ Azure 配置驗證通過")
        return True

    def get_credential(self):
        """獲取 Azure 認證憑證"""
        if self.client_id and self.client_secret and self.tenant_id:
            # 使用服務主體認證
            return ClientSecretCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
        else:
            # 使用預設認證鏈
            return DefaultAzureCredential()


# ============================================================================
# 3. Agent 部署配置
# ============================================================================

@dataclass
class DeploymentSettings:
    """
    部署設定

    定義 Agent 在 Azure 上的部署參數
    """
    # 基本設定
    agent_name: str
    version: str
    environment: str  # dev, staging, production

    # 擴展設定
    min_instances: int = 1
    max_instances: int = 10
    target_cpu_utilization: float = 0.7

    # 資源配置
    cpu_cores: float = 1.0
    memory_gb: float = 2.0

    # 網路設定
    enable_public_endpoint: bool = False
    allowed_ip_ranges: List[str] = None

    # 監控設定
    enable_app_insights: bool = True
    log_level: str = "INFO"

    # 成本控制
    max_monthly_cost: Optional[float] = None
    auto_shutdown_idle_minutes: int = 30

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "agent_name": self.agent_name,
            "version": self.version,
            "environment": self.environment,
            "scaling": {
                "min_instances": self.min_instances,
                "max_instances": self.max_instances,
                "target_cpu_utilization": self.target_cpu_utilization,
            },
            "resources": {
                "cpu_cores": self.cpu_cores,
                "memory_gb": self.memory_gb,
            },
            "network": {
                "enable_public_endpoint": self.enable_public_endpoint,
                "allowed_ip_ranges": self.allowed_ip_ranges or [],
            },
            "monitoring": {
                "enable_app_insights": self.enable_app_insights,
                "log_level": self.log_level,
            },
            "cost_control": {
                "max_monthly_cost": self.max_monthly_cost,
                "auto_shutdown_idle_minutes": self.auto_shutdown_idle_minutes,
            }
        }


# ============================================================================
# 4. Azure 部署管理器
# ============================================================================

class AzureDeploymentManager:
    """
    Azure 部署管理器

    負責將 Agent 部署到 Azure AI Foundry
    """

    def __init__(self, config: AzureConfig):
        """
        初始化部署管理器

        Args:
            config: Azure 配置
        """
        self.config = config
        self.credential = config.get_credential()
        self.deployments: Dict[str, Dict[str, Any]] = {}

    def create_deployment(
        self,
        agent: Agent,
        settings: DeploymentSettings
    ) -> str:
        """
        創建新的部署

        Args:
            agent: 要部署的 Agent
            settings: 部署設定

        Returns:
            部署 ID
        """
        print(f"\n🚀 創建 Azure 部署: {settings.agent_name}")
        print(f"   環境: {settings.environment}")
        print(f"   版本: {settings.version}")

        # 生成部署 ID
        deployment_id = f"{settings.agent_name}-{settings.environment}-{settings.version}"

        # 部署配置
        deployment_config = {
            "id": deployment_id,
            "agent": agent.name,
            "settings": settings.to_dict(),
            "status": "creating",
            "created_at": datetime.now().isoformat(),
            "endpoint": None,
        }

        # 模擬部署步驟
        steps = [
            "驗證配置",
            "建立容器映像",
            "配置網路",
            "部署到 Azure",
            "執行健康檢查",
            "註冊端點",
        ]

        for step in steps:
            print(f"   ⏳ {step}...")

        # 生成端點 URL
        endpoint = f"https://{deployment_id}.azurewebsites.net/api/chat"
        deployment_config["endpoint"] = endpoint
        deployment_config["status"] = "running"

        # 儲存部署資訊
        self.deployments[deployment_id] = deployment_config

        print(f"\n   ✅ 部署完成!")
        print(f"   端點: {endpoint}")
        print(f"   部署 ID: {deployment_id}")

        return deployment_id

    def update_deployment(
        self,
        deployment_id: str,
        agent: Agent,
        settings: DeploymentSettings
    ):
        """
        更新現有部署

        Args:
            deployment_id: 部署 ID
            agent: 新的 Agent
            settings: 新的設定
        """
        print(f"\n🔄 更新部署: {deployment_id}")

        if deployment_id not in self.deployments:
            raise ValueError(f"部署不存在: {deployment_id}")

        # 藍綠部署策略
        print("   使用藍綠部署策略...")
        print("   ⏳ 創建新版本 (綠)...")
        print("   ⏳ 健康檢查...")
        print("   ⏳ 切換流量到新版本...")
        print("   ⏳ 移除舊版本 (藍)...")

        # 更新配置
        self.deployments[deployment_id].update({
            "agent": agent.name,
            "settings": settings.to_dict(),
            "updated_at": datetime.now().isoformat(),
        })

        print("   ✅ 更新完成!")

    def scale_deployment(
        self,
        deployment_id: str,
        min_instances: int,
        max_instances: int
    ):
        """
        調整部署規模

        Args:
            deployment_id: 部署 ID
            min_instances: 最小實例數
            max_instances: 最大實例數
        """
        print(f"\n📊 調整部署規模: {deployment_id}")
        print(f"   實例範圍: {min_instances} - {max_instances}")

        if deployment_id not in self.deployments:
            raise ValueError(f"部署不存在: {deployment_id}")

        # 更新擴展設定
        self.deployments[deployment_id]["settings"]["scaling"].update({
            "min_instances": min_instances,
            "max_instances": max_instances,
        })

        print("   ✅ 規模調整完成!")

    def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """
        獲取部署狀態

        Args:
            deployment_id: 部署 ID

        Returns:
            部署狀態資訊
        """
        if deployment_id not in self.deployments:
            raise ValueError(f"部署不存在: {deployment_id}")

        deployment = self.deployments[deployment_id]

        # 模擬狀態資訊
        status = {
            "deployment_id": deployment_id,
            "status": deployment["status"],
            "endpoint": deployment["endpoint"],
            "instances": {
                "current": 3,
                "min": deployment["settings"]["scaling"]["min_instances"],
                "max": deployment["settings"]["scaling"]["max_instances"],
            },
            "health": {
                "healthy_instances": 3,
                "unhealthy_instances": 0,
                "uptime_percentage": 99.9,
            },
            "metrics": {
                "requests_per_minute": 120,
                "average_latency_ms": 85,
                "error_rate": 0.001,
            }
        }

        return status

    def delete_deployment(self, deployment_id: str):
        """
        刪除部署

        Args:
            deployment_id: 部署 ID
        """
        print(f"\n🗑️  刪除部署: {deployment_id}")

        if deployment_id not in self.deployments:
            raise ValueError(f"部署不存在: {deployment_id}")

        print("   ⏳ 停止實例...")
        print("   ⏳ 清理資源...")
        print("   ⏳ 移除端點...")

        del self.deployments[deployment_id]

        print("   ✅ 部署已刪除!")


# ============================================================================
# 5. 監控和日誌
# ============================================================================

class AzureMonitoring:
    """
    Azure 監控整合

    整合 Azure Application Insights 進行監控
    """

    def __init__(self, config: AzureConfig):
        """初始化監控"""
        self.config = config
        self.instrumentation_key = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

    def setup_monitoring(self):
        """設定監控"""
        print("\n📊 設定 Azure 監控")

        if not AZURE_AVAILABLE:
            print("   ⚠️  Azure SDK 未安裝")
            return

        if self.instrumentation_key:
            # 配置 Azure Monitor
            # configure_azure_monitor(connection_string=self.instrumentation_key)
            print("   ✅ Application Insights 已啟用")
        else:
            print("   ⚠️  未設定 Application Insights")

        print("\n   監控指標:")
        print("      - 請求數量和延遲")
        print("      - 錯誤率和異常")
        print("      - 資源使用率")
        print("      - 自定義業務指標")

    def log_agent_execution(
        self,
        agent_name: str,
        duration: float,
        success: bool,
        metadata: Dict[str, Any]
    ):
        """
        記錄 Agent 執行日誌

        Args:
            agent_name: Agent 名稱
            duration: 執行時間
            success: 是否成功
            metadata: 額外元資料
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "duration_ms": duration * 1000,
            "success": success,
            "metadata": metadata,
        }

        # 實際環境中會發送到 Application Insights
        print(f"\n📝 日誌: {json.dumps(log_entry, indent=2, ensure_ascii=False)}")

    def get_metrics(self, deployment_id: str) -> Dict[str, Any]:
        """
        獲取部署指標

        Args:
            deployment_id: 部署 ID

        Returns:
            指標資料
        """
        # 模擬指標資料
        metrics = {
            "deployment_id": deployment_id,
            "period": "last_24_hours",
            "requests": {
                "total": 15234,
                "successful": 15198,
                "failed": 36,
                "average_duration_ms": 125,
            },
            "resources": {
                "cpu_utilization": 0.45,
                "memory_utilization": 0.62,
                "network_bytes_in": 1024 * 1024 * 500,
                "network_bytes_out": 1024 * 1024 * 800,
            },
            "costs": {
                "compute": 45.23,
                "storage": 2.15,
                "network": 3.50,
                "total": 50.88,
                "currency": "USD",
            }
        }

        return metrics


# ============================================================================
# 6. 示範部署流程
# ============================================================================

def demonstrate_deployment_workflow():
    """示範完整的部署工作流程"""
    print("\n" + "="*70)
    print("🎯 Azure 部署工作流程示範")
    print("="*70)

    # 1. 載入配置
    config = AzureConfig()
    if not config.validate():
        print("\n⚠️  請先設定 Azure 環境變數")
        print_environment_setup_guide()
        return

    # 2. 創建 Agent
    print("\n步驟 1: 創建 Agent")
    model = AzureOpenAIModel(
        endpoint=config.openai_endpoint,
        api_key=config.openai_api_key,
        deployment=config.openai_deployment,
        api_version=config.openai_api_version
    )

    agent = Agent(
        name="customer_service_agent",
        model=model,
        instructions="你是客服助手,幫助客戶解決問題",
    )
    print(f"   ✅ Agent 創建完成: {agent.name}")

    # 3. 配置部署設定
    print("\n步驟 2: 配置部署設定")
    settings = DeploymentSettings(
        agent_name="customer-service",
        version="v1.0.0",
        environment="production",
        min_instances=2,
        max_instances=10,
        cpu_cores=2.0,
        memory_gb=4.0,
        enable_app_insights=True,
    )
    print(f"   ✅ 部署設定完成")

    # 4. 創建部署
    print("\n步驟 3: 部署到 Azure")
    manager = AzureDeploymentManager(config)
    deployment_id = manager.create_deployment(agent, settings)

    # 5. 設定監控
    print("\n步驟 4: 設定監控")
    monitoring = AzureMonitoring(config)
    monitoring.setup_monitoring()

    # 6. 檢查部署狀態
    print("\n步驟 5: 檢查部署狀態")
    status = manager.get_deployment_status(deployment_id)
    print(f"\n部署狀態:")
    print(f"   狀態: {status['status']}")
    print(f"   端點: {status['endpoint']}")
    print(f"   實例數: {status['instances']['current']}")
    print(f"   健康度: {status['health']['uptime_percentage']}%")

    # 7. 獲取指標
    print("\n步驟 6: 查看指標")
    metrics = monitoring.get_metrics(deployment_id)
    print(f"\n使用指標:")
    print(f"   總請求數: {metrics['requests']['total']}")
    print(f"   成功率: {metrics['requests']['successful'] / metrics['requests']['total'] * 100:.2f}%")
    print(f"   平均延遲: {metrics['requests']['average_duration_ms']} ms")
    print(f"   CPU 使用率: {metrics['resources']['cpu_utilization'] * 100:.1f}%")
    print(f"\n成本 (24 小時):")
    print(f"   總計: ${metrics['costs']['total']:.2f} USD")


# ============================================================================
# 7. 環境設定指南
# ============================================================================

def print_environment_setup_guide():
    """輸出環境設定指南"""
    print("\n" + "="*70)
    print("📖 Azure 環境設定指南")
    print("="*70)

    print("\n請在 .env 檔案中設定以下環境變數:")
    print("\n# Azure OpenAI 配置")
    print("AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/")
    print("AZURE_OPENAI_API_KEY=your_api_key")
    print("AZURE_OPENAI_DEPLOYMENT=gpt-4")
    print("AZURE_OPENAI_API_VERSION=2024-08-01-preview")

    print("\n# Azure AI Foundry 配置")
    print("AZURE_SUBSCRIPTION_ID=your_subscription_id")
    print("AZURE_RESOURCE_GROUP=your_resource_group")
    print("AZURE_WORKSPACE_NAME=your_workspace_name")

    print("\n# Azure 認證 (服務主體)")
    print("AZURE_TENANT_ID=your_tenant_id")
    print("AZURE_CLIENT_ID=your_client_id")
    print("AZURE_CLIENT_SECRET=your_client_secret")

    print("\n# Application Insights (可選)")
    print("APPLICATIONINSIGHTS_CONNECTION_STRING=your_connection_string")


# ============================================================================
# 8. 成本優化建議
# ============================================================================

def print_cost_optimization_tips():
    """輸出成本優化建議"""
    print("\n" + "="*70)
    print("💰 Azure 成本優化建議")
    print("="*70)

    tips = [
        ("1. 選擇合適的定價層", [
            "開發環境使用較低規格",
            "生產環境根據負載選擇",
            "考慮保留實例折扣"
        ]),
        ("2. 自動擴展配置", [
            "設定合理的最小實例數",
            "根據實際負載調整最大實例數",
            "使用基於排程的擴展"
        ]),
        ("3. 閒置資源管理", [
            "啟用自動關閉閒置實例",
            "定期審查未使用的資源",
            "使用開發/測試定價"
        ]),
        ("4. 監控和預算", [
            "設定成本警報",
            "定期審查成本報告",
            "使用 Azure Cost Management"
        ]),
        ("5. 快取和優化", [
            "使用 CDN 減少流量成本",
            "實施快取策略",
            "優化 API 調用次數"
        ]),
    ]

    for title, points in tips:
        print(f"\n   {title}")
        for point in points:
            print(f"      - {point}")


# ============================================================================
# 9. 主程式
# ============================================================================

def main():
    """主程式"""
    print("="*70)
    print("Microsoft Agent Framework - Azure 部署")
    print("="*70)

    # Azure AI Foundry 介紹
    explain_azure_ai_foundry()

    # 部署工作流程示範
    demonstrate_deployment_workflow()

    # 成本優化建議
    print_cost_optimization_tips()

    print("\n" + "="*70)
    print("✅ Azure 部署示範完成!")
    print("="*70)

    print("\n💡 關鍵要點:")
    print("   1. Azure AI Foundry 提供完整的部署方案")
    print("   2. 支援自動擴展和高可用性")
    print("   3. 整合監控和日誌功能")
    print("   4. 需要合理配置以優化成本")
    print("   5. 提供企業級安全性和合規性")

    print("\n📚 下一步:")
    print("   查看 08_狀態持久化.py 學習狀態管理")


if __name__ == "__main__":
    main()
