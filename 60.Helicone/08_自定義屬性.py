"""
Helicone 自定義屬性與元數據
===========================

本文件展示如何使用 Helicone 的自定義屬性功能來增強請求追蹤。
自定義屬性讓您可以添加任何業務相關的元數據。

主要內容:
1. 基本自定義屬性
2. 結構化元數據
3. 標籤系統
4. 環境和版本追蹤
5. 業務指標關聯
6. A/B 測試標記
7. 自定義搜索和過濾

作者: Helicone Team
日期: 2025-12-31
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
from dotenv import load_dotenv

try:
    import openai
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.tree import Tree
    from rich.syntax import Syntax
    import pandas as pd
except ImportError as e:
    print(f"❌ 缺少必要的依賴: {e}")
    print("請運行: pip install openai rich pandas")
    sys.exit(1)


class Environment(Enum):
    """環境類型"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class Priority(Enum):
    """優先級"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class CustomProperties:
    """
    自定義屬性集合

    這個類定義了所有可能的自定義屬性。
    Helicone 會將這些屬性添加到請求元數據中。
    """
    # 環境和部署
    environment: str
    version: str
    deployment_id: Optional[str] = None
    region: Optional[str] = None

    # 業務上下文
    feature: str
    category: Optional[str] = None
    team: Optional[str] = None
    project: Optional[str] = None

    # 用戶和會話
    user_tier: Optional[str] = None
    organization_id: Optional[str] = None
    tenant_id: Optional[str] = None

    # 請求特徵
    priority: str = "medium"
    request_source: Optional[str] = None
    device_type: Optional[str] = None
    platform: Optional[str] = None

    # A/B 測試
    experiment_id: Optional[str] = None
    variant: Optional[str] = None
    treatment_group: Optional[str] = None

    # 業務指標
    conversion_value: Optional[float] = None
    customer_lifetime_value: Optional[float] = None
    risk_score: Optional[float] = None

    # 技術指標
    cache_strategy: Optional[str] = None
    retry_count: int = 0
    timeout_seconds: Optional[int] = None

    # 自定義標籤
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_helicone_headers(self) -> Dict[str, str]:
        """
        轉換為 Helicone headers

        Helicone 使用特殊的 HTTP headers 來接收自定義屬性。
        格式: Helicone-Property-{PropertyName}
        """
        headers = {}

        # 基本屬性
        headers["Helicone-Property-Environment"] = self.environment
        headers["Helicone-Property-Version"] = self.version
        headers["Helicone-Property-Feature"] = self.feature
        headers["Helicone-Property-Priority"] = self.priority

        # 可選屬性
        optional_fields = {
            "deployment_id": "DeploymentId",
            "region": "Region",
            "category": "Category",
            "team": "Team",
            "project": "Project",
            "user_tier": "UserTier",
            "organization_id": "OrganizationId",
            "tenant_id": "TenantId",
            "request_source": "RequestSource",
            "device_type": "DeviceType",
            "platform": "Platform",
            "experiment_id": "ExperimentId",
            "variant": "Variant",
            "treatment_group": "TreatmentGroup",
            "cache_strategy": "CacheStrategy",
        }

        for field_name, header_name in optional_fields.items():
            value = getattr(self, field_name)
            if value is not None:
                headers[f"Helicone-Property-{header_name}"] = str(value)

        # 數值屬性
        numeric_fields = {
            "conversion_value": "ConversionValue",
            "customer_lifetime_value": "CustomerLifetimeValue",
            "risk_score": "RiskScore",
            "retry_count": "RetryCount",
            "timeout_seconds": "TimeoutSeconds",
        }

        for field_name, header_name in numeric_fields.items():
            value = getattr(self, field_name)
            if value is not None and (isinstance(value, (int, float))):
                headers[f"Helicone-Property-{header_name}"] = str(value)

        # 標籤 (轉換為逗號分隔的字符串)
        if self.tags:
            headers["Helicone-Property-Tags"] = ",".join(self.tags)

        # 額外的元數據
        for key, value in self.metadata.items():
            headers[f"Helicone-Property-{key}"] = str(value)

        return headers


class HeliconePropertyManager:
    """
    Helicone 屬性管理器

    管理和追蹤自定義屬性的使用。
    """

    def __init__(self):
        """初始化屬性管理器"""
        load_dotenv()

        # API 配置
        self.helicone_api_key = os.getenv("HELICONE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.helicone_base_url = "https://oai.helicone.ai/v1"

        # 初始化客戶端
        self.client = openai.OpenAI(
            api_key=self.openai_api_key,
            base_url=self.helicone_base_url,
            default_headers={
                "Helicone-Auth": f"Bearer {self.helicone_api_key}"
            }
        )

        self.console = Console()

        # 請求歷史
        self.requests: List[Dict] = []

        # 屬性使用統計
        self.property_usage: Dict[str, int] = defaultdict(int)

        self.console.print("✅ [green]屬性管理器已初始化[/green]")

    def send_request_with_properties(
        self,
        prompt: str,
        properties: CustomProperties,
        model: str = "gpt-3.5-turbo",
        **kwargs
    ) -> Dict:
        """
        發送帶有自定義屬性的請求

        這是核心方法,將自定義屬性附加到請求上。
        """
        try:
            start_time = time.time()

            # 轉換屬性為 headers
            property_headers = properties.to_helicone_headers()

            # 追蹤屬性使用
            for header_name in property_headers.keys():
                self.property_usage[header_name] += 1

            # 顯示將要發送的屬性
            self.console.print(f"\n📤 [cyan]發送請求[/cyan]")
            self.console.print(f"   模型: {model}")
            self.console.print(f"   自定義屬性數: {len(property_headers)}")

            # 發送請求
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                extra_headers=property_headers,
                **kwargs
            )

            end_time = time.time()

            # 記錄請求
            request_record = {
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt,
                "response": response.choices[0].message.content,
                "model": response.model,
                "properties": asdict(properties),
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "duration": end_time - start_time
            }

            self.requests.append(request_record)

            self.console.print(f"✅ [green]請求成功[/green]")
            self.console.print(f"   Tokens: {response.usage.total_tokens}")

            return {
                "success": True,
                "response": response.choices[0].message.content,
                "request_record": request_record
            }

        except Exception as e:
            self.console.print(f"❌ [red]請求失敗: {str(e)}[/red]")
            return {
                "success": False,
                "error": str(e)
            }

    def display_property_headers(self, properties: CustomProperties):
        """顯示屬性將如何轉換為 headers"""
        self.console.print("\n[bold cyan]🏷️  自定義屬性 Headers[/bold cyan]")
        self.console.print("=" * 80)

        headers = properties.to_helicone_headers()

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Header Name", style="cyan")
        table.add_column("Value", style="green")

        for header_name, value in sorted(headers.items()):
            table.add_row(header_name, str(value))

        self.console.print(table)

    def analyze_by_property(self, property_name: str) -> Dict:
        """
        按屬性分析請求

        例如: 分析不同環境的請求分布
        """
        if not self.requests:
            return {"message": "沒有請求記錄"}

        # 按屬性值分組
        groups = defaultdict(lambda: {
            "count": 0,
            "total_tokens": 0,
            "avg_tokens": 0
        })

        for request in self.requests:
            props = request["properties"]

            # 獲取屬性值
            value = props.get(property_name, "未設置")

            groups[str(value)]["count"] += 1
            groups[str(value)]["total_tokens"] += request["usage"]["total_tokens"]

        # 計算平均值
        for value in groups:
            if groups[value]["count"] > 0:
                groups[value]["avg_tokens"] = groups[value]["total_tokens"] / groups[value]["count"]

        return dict(groups)

    def display_property_analysis(self, property_name: str):
        """顯示屬性分析"""
        analysis = self.analyze_by_property(property_name)

        if "message" in analysis:
            self.console.print(f"⚠️  [yellow]{analysis['message']}[/yellow]")
            return

        self.console.print(f"\n[bold cyan]📊 按 '{property_name}' 分析[/bold cyan]")
        self.console.print("=" * 80)

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column(property_name, style="cyan")
        table.add_column("請求數", justify="right")
        table.add_column("總 Tokens", justify="right")
        table.add_column("平均 Tokens", justify="right")

        for value, stats in sorted(analysis.items(), key=lambda x: x[1]["count"], reverse=True):
            table.add_row(
                str(value),
                str(stats["count"]),
                f"{stats['total_tokens']:,}",
                f"{stats['avg_tokens']:.0f}"
            )

        self.console.print(table)

    def get_property_usage_stats(self):
        """獲取屬性使用統計"""
        self.console.print("\n[bold cyan]📈 屬性使用統計[/bold cyan]")
        self.console.print("=" * 80)

        if not self.property_usage:
            self.console.print("⚠️  [yellow]沒有屬性使用記錄[/yellow]")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("屬性名稱", style="cyan")
        table.add_column("使用次數", justify="right", style="green")

        # 排序並顯示
        for prop_name, count in sorted(self.property_usage.items(), key=lambda x: x[1], reverse=True):
            # 移除 "Helicone-Property-" 前綴
            display_name = prop_name.replace("Helicone-Property-", "")
            table.add_row(display_name, str(count))

        self.console.print(table)

    def export_with_properties(self, filename: str = "requests_with_properties.csv"):
        """導出包含屬性的請求記錄"""
        if not self.requests:
            self.console.print("⚠️  [yellow]沒有請求可導出[/yellow]")
            return

        # 扁平化數據
        flat_data = []
        for request in self.requests:
            flat_record = {
                "時間": request["timestamp"],
                "提示詞": request["prompt"][:50] + "...",
                "模型": request["model"],
                "總Tokens": request["usage"]["total_tokens"],
            }

            # 添加屬性
            props = request["properties"]
            for key, value in props.items():
                if key not in ["tags", "metadata"]:
                    flat_record[f"屬性_{key}"] = value

            flat_data.append(flat_record)

        df = pd.DataFrame(flat_data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')

        self.console.print(f"✅ [green]已導出 {len(flat_data)} 條記錄到 {filename}[/green]")


def demo_basic_properties():
    """演示基本自定義屬性"""
    console = Console()
    console.print("[bold cyan]演示 1: 基本自定義屬性[/bold cyan]")
    console.print("=" * 80)

    manager = HeliconePropertyManager()

    # 創建自定義屬性
    properties = CustomProperties(
        environment="production",
        version="v1.2.3",
        feature="customer-support",
        team="support-team",
        priority="high",
        tags=["urgent", "customer-facing"]
    )

    # 顯示屬性如何轉換為 headers
    manager.display_property_headers(properties)

    # 發送請求
    result = manager.send_request_with_properties(
        prompt="幫我解決客戶的問題: 產品無法登錄",
        properties=properties,
        max_tokens=200
    )

    if result["success"]:
        console.print(f"\n[green]回應: {result['response'][:200]}...[/green]")

    return manager


def demo_ab_testing_properties():
    """演示 A/B 測試屬性"""
    console = Console()
    console.print("\n[bold cyan]演示 2: A/B 測試追蹤[/bold cyan]")
    console.print("=" * 80)

    manager = HeliconePropertyManager()

    # 模擬 A/B 測試
    experiments = [
        {
            "variant": "A",
            "experiment_id": "exp_001",
            "prompt": "生成產品標題 (簡短版)",
            "treatment_group": "control"
        },
        {
            "variant": "B",
            "experiment_id": "exp_001",
            "prompt": "生成產品標題 (詳細版)",
            "treatment_group": "treatment"
        },
    ]

    for exp in experiments:
        properties = CustomProperties(
            environment="production",
            version="v2.0.0",
            feature="title-generation",
            experiment_id=exp["experiment_id"],
            variant=exp["variant"],
            treatment_group=exp["treatment_group"],
            tags=["ab-test", "product"]
        )

        console.print(f"\n🧪 測試變體 {exp['variant']}:")
        manager.send_request_with_properties(
            prompt=exp["prompt"],
            properties=properties,
            max_tokens=50
        )

        time.sleep(0.5)

    # 分析實驗結果
    manager.display_property_analysis("variant")

    return manager


def demo_business_context_properties():
    """演示業務上下文屬性"""
    console = Console()
    console.print("\n[bold cyan]演示 3: 業務上下文追蹤[/bold cyan]")
    console.print("=" * 80)

    manager = HeliconePropertyManager()

    # 不同的業務場景
    scenarios = [
        {
            "feature": "lead-qualification",
            "team": "sales",
            "conversion_value": 1000.0,
            "risk_score": 0.3,
            "prompt": "評估這個潛在客戶的購買意向"
        },
        {
            "feature": "customer-retention",
            "team": "support",
            "customer_lifetime_value": 5000.0,
            "risk_score": 0.7,
            "prompt": "生成挽留客戶的個性化優惠"
        },
        {
            "feature": "product-recommendation",
            "team": "marketing",
            "conversion_value": 500.0,
            "risk_score": 0.2,
            "prompt": "推薦相關產品給這個客戶"
        },
    ]

    for scenario in scenarios:
        properties = CustomProperties(
            environment="production",
            version="v3.1.0",
            feature=scenario["feature"],
            team=scenario["team"],
            conversion_value=scenario.get("conversion_value"),
            customer_lifetime_value=scenario.get("customer_lifetime_value"),
            risk_score=scenario.get("risk_score"),
            tags=["business-critical", scenario["team"]]
        )

        console.print(f"\n💼 場景: {scenario['feature']}")
        manager.send_request_with_properties(
            prompt=scenario["prompt"],
            properties=properties,
            max_tokens=100
        )

        time.sleep(0.5)

    # 按團隊分析
    manager.display_property_analysis("team")

    # 按功能分析
    manager.display_property_analysis("feature")

    return manager


def demo_multi_environment_tracking():
    """演示多環境追蹤"""
    console = Console()
    console.print("\n[bold cyan]演示 4: 多環境追蹤[/bold cyan]")
    console.print("=" * 80)

    manager = HeliconePropertyManager()

    # 不同環境的配置
    environments = [
        {
            "env": Environment.DEVELOPMENT,
            "region": "local",
            "deployment_id": "dev-001"
        },
        {
            "env": Environment.STAGING,
            "region": "us-west-2",
            "deployment_id": "stg-123"
        },
        {
            "env": Environment.PRODUCTION,
            "region": "us-east-1",
            "deployment_id": "prod-456"
        },
    ]

    for env_config in environments:
        properties = CustomProperties(
            environment=env_config["env"].value,
            version="v1.0.0",
            feature="api-endpoint",
            deployment_id=env_config["deployment_id"],
            region=env_config["region"],
            tags=["deployment", env_config["env"].value]
        )

        console.print(f"\n🌍 環境: {env_config['env'].value.upper()}")
        manager.send_request_with_properties(
            prompt="測試 API 響應",
            properties=properties,
            max_tokens=50
        )

        time.sleep(0.3)

    # 按環境分析
    manager.display_property_analysis("environment")

    return manager


def demo_comprehensive_properties():
    """演示完整的屬性使用"""
    console = Console()
    console.print("\n[bold cyan]演示 5: 完整屬性示例[/bold cyan]")
    console.print("=" * 80)

    manager = HeliconePropertyManager()

    # 創建包含所有類型屬性的請求
    comprehensive_props = CustomProperties(
        # 環境
        environment="production",
        version="v2.5.1",
        deployment_id="prod-789",
        region="ap-northeast-1",

        # 業務
        feature="premium-support",
        category="enterprise",
        team="vip-support",
        project="customer-success-2024",

        # 用戶
        user_tier="enterprise",
        organization_id="org_12345",
        tenant_id="tenant_abc",

        # 請求
        priority="critical",
        request_source="mobile-app",
        device_type="ios",
        platform="iPhone 15 Pro",

        # A/B 測試
        experiment_id="exp_premium_response",
        variant="premium_model",
        treatment_group="treatment",

        # 業務指標
        conversion_value=10000.0,
        customer_lifetime_value=50000.0,
        risk_score=0.1,

        # 技術
        cache_strategy="semantic",
        retry_count=0,
        timeout_seconds=30,

        # 標籤
        tags=["vip", "premium", "critical", "mobile"],

        # 額外元數據
        metadata={
            "ticket_id": "TKT-98765",
            "customer_satisfaction_score": "9.5",
            "response_time_sla": "15min"
        }
    )

    # 顯示所有屬性
    manager.display_property_headers(comprehensive_props)

    # 發送請求
    console.print("\n發送請求...")
    result = manager.send_request_with_properties(
        prompt="為 VIP 客戶提供高優先級支持響應",
        properties=comprehensive_props,
        max_tokens=150
    )

    if result["success"]:
        console.print(f"\n[bold green]✅ 請求成功![/bold green]")

        # 顯示請求記錄的 JSON
        console.print("\n[bold cyan]📋 完整請求記錄:[/bold cyan]")
        record_json = json.dumps(result["request_record"], indent=2, ensure_ascii=False, default=str)
        syntax = Syntax(record_json, "json", theme="monokai", line_numbers=True)
        console.print(syntax)

    return manager


def main():
    """主函數"""
    console = Console()
    console.print("[bold green]🎯 Helicone 自定義屬性演示[/bold green]\n")

    try:
        # 演示 1: 基本屬性
        demo_basic_properties()

        # 演示 2: A/B 測試
        demo_ab_testing_properties()

        # 演示 3: 業務上下文
        manager = demo_business_context_properties()

        # 演示 4: 多環境
        demo_multi_environment_tracking()

        # 演示 5: 完整屬性
        demo_comprehensive_properties()

        # 顯示統計
        manager.get_property_usage_stats()

        # 導出數據
        manager.export_with_properties()

        console.print("\n✅ [green]演示完成![/green]")
        console.print("📊 所有自定義屬性都已記錄在 Helicone 儀表板中")
        console.print("🔍 您可以使用這些屬性進行高級過濾和分析")

    except Exception as e:
        console.print(f"\n❌ [red]錯誤: {str(e)}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
