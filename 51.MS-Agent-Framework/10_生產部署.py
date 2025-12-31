"""
Microsoft Agent Framework - 生產部署

這個檔案展示如何將 Agent 系統部署到生產環境。
涵蓋架構設計、監控、安全性、性能優化等生產環境關鍵議題。

主要內容:
1. 生產環境架構
2. 部署檢查清單
3. 監控和告警
4. 日誌管理
5. 性能優化
6. 安全性強化
7. 災難恢復
8. 運維最佳實踐

作者: Microsoft Agent Framework Team
日期: 2025-12-31
版本: 1.0.0
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

# Agent Framework
from agent_framework import Agent, AgentThread
from agent_framework.models import OpenAIModel

# ============================================================================
# 1. 生產環境架構
# ============================================================================

def explain_production_architecture():
    """
    解釋生產環境架構

    展示完整的 Agent 系統生產架構
    """
    print("="*70)
    print("生產環境架構設計")
    print("="*70)

    print("\n🏗️  系統架構層次:")

    layers = [
        ("1. 前端層", [
            "Web UI / Mobile App",
            "API Gateway",
            "負載均衡器"
        ]),
        ("2. 應用層", [
            "Agent 服務集群",
            "工作流引擎",
            "業務邏輯處理"
        ]),
        ("3. 服務層", [
            "認證服務",
            "快取服務 (Redis)",
            "訊息佇列 (RabbitMQ/Kafka)"
        ]),
        ("4. 資料層", [
            "關聯式資料庫 (PostgreSQL)",
            "向量資料庫 (Pinecone/Weaviate)",
            "物件儲存 (Azure Blob)"
        ]),
        ("5. AI/ML 層", [
            "LLM 服務 (Azure OpenAI)",
            "模型管理",
            "特徵存儲"
        ]),
        ("6. 基礎設施層", [
            "容器編排 (Kubernetes)",
            "CI/CD Pipeline",
            "監控和日誌系統"
        ]),
    ]

    for title, components in layers:
        print(f"\n   {title}")
        for component in components:
            print(f"      - {component}")


# ============================================================================
# 2. 部署檢查清單
# ============================================================================

@dataclass
class DeploymentChecklistItem:
    """部署檢查項目"""
    category: str
    item: str
    status: bool = False
    notes: str = ""


class ProductionDeploymentChecklist:
    """
    生產部署檢查清單

    確保所有必要的準備工作都已完成
    """

    def __init__(self):
        """初始化檢查清單"""
        self.items = self._create_checklist()

    def _create_checklist(self) -> List[DeploymentChecklistItem]:
        """創建檢查清單"""
        return [
            # 環境配置
            DeploymentChecklistItem("環境配置", "設定環境變數"),
            DeploymentChecklistItem("環境配置", "配置資料庫連接"),
            DeploymentChecklistItem("環境配置", "設定 Redis 快取"),
            DeploymentChecklistItem("環境配置", "配置 Azure OpenAI"),

            # 安全性
            DeploymentChecklistItem("安全性", "啟用 HTTPS/TLS"),
            DeploymentChecklistItem("安全性", "配置防火牆規則"),
            DeploymentChecklistItem("安全性", "設定 API 金鑰輪換"),
            DeploymentChecklistItem("安全性", "實施速率限制"),
            DeploymentChecklistItem("安全性", "配置 WAF (Web Application Firewall)"),

            # 監控和日誌
            DeploymentChecklistItem("監控", "設定 Application Insights"),
            DeploymentChecklistItem("監控", "配置告警規則"),
            DeploymentChecklistItem("監控", "設定日誌聚合"),
            DeploymentChecklistItem("監控", "配置儀表板"),

            # 性能
            DeploymentChecklistItem("性能", "啟用快取策略"),
            DeploymentChecklistItem("性能", "配置自動擴展"),
            DeploymentChecklistItem("性能", "優化資料庫索引"),
            DeploymentChecklistItem("性能", "實施連接池"),

            # 可靠性
            DeploymentChecklistItem("可靠性", "設定健康檢查"),
            DeploymentChecklistItem("可靠性", "配置重試機制"),
            DeploymentChecklistItem("可靠性", "實施熔斷器模式"),
            DeploymentChecklistItem("可靠性", "設定備份策略"),

            # 測試
            DeploymentChecklistItem("測試", "執行單元測試"),
            DeploymentChecklistItem("測試", "執行整合測試"),
            DeploymentChecklistItem("測試", "執行負載測試"),
            DeploymentChecklistItem("測試", "執行安全掃描"),

            # 文檔
            DeploymentChecklistItem("文檔", "更新 API 文檔"),
            DeploymentChecklistItem("文檔", "準備運維手冊"),
            DeploymentChecklistItem("文檔", "編寫故障排除指南"),

            # 合規
            DeploymentChecklistItem("合規", "資料隱私審查"),
            DeploymentChecklistItem("合規", "安全合規檢查"),
            DeploymentChecklistItem("合規", "授權和許可證確認"),
        ]

    def print_checklist(self):
        """顯示檢查清單"""
        print("\n" + "="*70)
        print("📋 生產部署檢查清單")
        print("="*70)

        categories = {}
        for item in self.items:
            if item.category not in categories:
                categories[item.category] = []
            categories[item.category].append(item)

        for category, items in categories.items():
            print(f"\n{category}:")
            for item in items:
                status = "✅" if item.status else "⬜"
                print(f"   {status} {item.item}")
                if item.notes:
                    print(f"      註: {item.notes}")

    def validate_deployment(self) -> bool:
        """驗證是否所有項目都已完成"""
        completed = sum(1 for item in self.items if item.status)
        total = len(self.items)
        percentage = (completed / total) * 100

        print(f"\n完成度: {completed}/{total} ({percentage:.1f}%)")

        return percentage == 100


# ============================================================================
# 3. 日誌管理
# ============================================================================

class ProductionLogger:
    """
    生產環境日誌管理

    結構化日誌,支援多種輸出
    """

    def __init__(self, service_name: str, environment: str):
        """
        初始化日誌器

        Args:
            service_name: 服務名稱
            environment: 環境 (dev/staging/production)
        """
        self.service_name = service_name
        self.environment = environment
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """設定日誌器"""
        logger = logging.getLogger(self.service_name)

        # 設定日誌級別
        if self.environment == "production":
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.DEBUG)

        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # 控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 檔案處理器 (生產環境)
        if self.environment == "production":
            file_handler = logging.FileHandler(
                f"{self.service_name}.log"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger

    def log_agent_execution(
        self,
        agent_name: str,
        thread_id: str,
        duration_ms: float,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        記錄 Agent 執行日誌

        Args:
            agent_name: Agent 名稱
            thread_id: Thread ID
            duration_ms: 執行時間 (毫秒)
            success: 是否成功
            metadata: 額外元資料
        """
        log_data = {
            "event": "agent_execution",
            "agent_name": agent_name,
            "thread_id": thread_id,
            "duration_ms": duration_ms,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "environment": self.environment,
        }

        if metadata:
            log_data["metadata"] = metadata

        if success:
            self.logger.info(json.dumps(log_data, ensure_ascii=False))
        else:
            self.logger.error(json.dumps(log_data, ensure_ascii=False))

    def log_error(
        self,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        記錄錯誤

        Args:
            error_type: 錯誤類型
            error_message: 錯誤訊息
            stack_trace: 堆疊追蹤
            context: 上下文資訊
        """
        log_data = {
            "event": "error",
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat(),
        }

        if stack_trace:
            log_data["stack_trace"] = stack_trace

        if context:
            log_data["context"] = context

        self.logger.error(json.dumps(log_data, ensure_ascii=False))


# ============================================================================
# 4. 監控指標
# ============================================================================

@dataclass
class MetricData:
    """指標資料"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str]


class MetricsCollector:
    """
    指標收集器

    收集和報告系統指標
    """

    def __init__(self):
        """初始化收集器"""
        self.metrics: List[MetricData] = []

    def record_metric(
        self,
        name: str,
        value: float,
        unit: str = "count",
        tags: Optional[Dict[str, str]] = None
    ):
        """
        記錄指標

        Args:
            name: 指標名稱
            value: 指標值
            unit: 單位
            tags: 標籤
        """
        metric = MetricData(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            tags=tags or {}
        )

        self.metrics.append(metric)

        # 實際環境中會發送到監控系統
        print(f"📊 指標: {name} = {value} {unit}")

    def get_summary(self) -> Dict[str, Any]:
        """獲取指標摘要"""
        if not self.metrics:
            return {}

        # 按名稱分組
        grouped = {}
        for metric in self.metrics:
            if metric.name not in grouped:
                grouped[metric.name] = []
            grouped[metric.name].append(metric.value)

        # 計算統計
        summary = {}
        for name, values in grouped.items():
            summary[name] = {
                "count": len(values),
                "sum": sum(values),
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
            }

        return summary


# ============================================================================
# 5. 健康檢查
# ============================================================================

class HealthCheckStatus(str, Enum):
    """健康狀態"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheckResult:
    """健康檢查結果"""
    component: str
    status: HealthCheckStatus
    message: str
    response_time_ms: float


class HealthChecker:
    """
    健康檢查器

    檢查系統各組件的健康狀態
    """

    def __init__(self):
        """初始化檢查器"""
        self.checks: List[callable] = []

    def add_check(self, check_func: callable):
        """添加檢查函數"""
        self.checks.append(check_func)

    def run_checks(self) -> List[HealthCheckResult]:
        """執行所有檢查"""
        results = []

        for check in self.checks:
            try:
                import time
                start = time.time()
                result = check()
                duration = (time.time() - start) * 1000

                results.append(HealthCheckResult(
                    component=result["component"],
                    status=result["status"],
                    message=result["message"],
                    response_time_ms=duration
                ))
            except Exception as e:
                results.append(HealthCheckResult(
                    component="unknown",
                    status=HealthCheckStatus.UNHEALTHY,
                    message=f"檢查失敗: {str(e)}",
                    response_time_ms=0
                ))

        return results

    def get_overall_status(
        self,
        results: List[HealthCheckResult]
    ) -> HealthCheckStatus:
        """獲取整體健康狀態"""
        if any(r.status == HealthCheckStatus.UNHEALTHY for r in results):
            return HealthCheckStatus.UNHEALTHY
        elif any(r.status == HealthCheckStatus.DEGRADED for r in results):
            return HealthCheckStatus.DEGRADED
        else:
            return HealthCheckStatus.HEALTHY


# ============================================================================
# 6. 性能優化策略
# ============================================================================

class PerformanceOptimizer:
    """
    性能優化器

    實施各種性能優化策略
    """

    @staticmethod
    def implement_caching():
        """實施快取策略"""
        print("\n🚀 性能優化: 快取策略")

        strategies = [
            "1. LLM 回應快取 - 快取常見問題的回應",
            "2. 工具結果快取 - 快取外部 API 調用結果",
            "3. 會話快取 - 使用 Redis 快取對話狀態",
            "4. 設定 TTL (Time-To-Live) 避免過期資料",
            "5. 實施快取失效策略",
        ]

        for strategy in strategies:
            print(f"   {strategy}")

    @staticmethod
    def implement_connection_pooling():
        """實施連接池"""
        print("\n🚀 性能優化: 連接池")

        print("   資料庫連接池:")
        print("      - 最小連接數: 5")
        print("      - 最大連接數: 20")
        print("      - 連接超時: 30 秒")

        print("   Redis 連接池:")
        print("      - 最大連接數: 50")
        print("      - 閒置超時: 300 秒")

    @staticmethod
    def implement_batch_processing():
        """實施批次處理"""
        print("\n🚀 性能優化: 批次處理")

        print("   策略:")
        print("      - 批次處理多個 LLM 請求")
        print("      - 合併資料庫查詢")
        print("      - 批次寫入日誌")
        print("      - 批次大小: 10-50")

    @staticmethod
    def implement_async_processing():
        """實施非同步處理"""
        print("\n🚀 性能優化: 非同步處理")

        print("   應用:")
        print("      - 使用非同步 I/O 操作")
        print("      - 並行處理獨立任務")
        print("      - 使用訊息佇列處理長任務")
        print("      - Worker 池大小: 根據 CPU 核心數調整")


# ============================================================================
# 7. 安全性強化
# ============================================================================

class SecurityHardening:
    """
    安全性強化

    實施各種安全措施
    """

    @staticmethod
    def implement_authentication():
        """實施認證機制"""
        print("\n🔒 安全性: 認證")

        print("   措施:")
        print("      - OAuth 2.0 / OpenID Connect")
        print("      - JWT Token 驗證")
        print("      - API 金鑰管理")
        print("      - 多因素認證 (MFA)")

    @staticmethod
    def implement_authorization():
        """實施授權機制"""
        print("\n🔒 安全性: 授權")

        print("   策略:")
        print("      - 角色基礎存取控制 (RBAC)")
        print("      - 屬性基礎存取控制 (ABAC)")
        print("      - 最小權限原則")
        print("      - 定期審查權限")

    @staticmethod
    def implement_input_validation():
        """實施輸入驗證"""
        print("\n🔒 安全性: 輸入驗證")

        print("   檢查:")
        print("      - 驗證所有用戶輸入")
        print("      - 過濾惡意內容")
        print("      - SQL 注入防護")
        print("      - XSS 攻擊防護")

    @staticmethod
    def implement_data_encryption():
        """實施資料加密"""
        print("\n🔒 安全性: 資料加密")

        print("   層級:")
        print("      - 傳輸加密: TLS 1.3")
        print("      - 靜態加密: AES-256")
        print("      - 敏感欄位加密")
        print("      - 金鑰輪換策略")

    @staticmethod
    def implement_rate_limiting():
        """實施速率限制"""
        print("\n🔒 安全性: 速率限制")

        print("   限制:")
        print("      - 每 IP: 100 請求/分鐘")
        print("      - 每用戶: 1000 請求/小時")
        print("      - 每 API 金鑰: 10000 請求/天")
        print("      - 動態調整策略")


# ============================================================================
# 8. 災難恢復
# ============================================================================

class DisasterRecovery:
    """
    災難恢復計劃

    確保系統能從故障中恢復
    """

    @staticmethod
    def implement_backup_strategy():
        """實施備份策略"""
        print("\n💾 災難恢復: 備份策略")

        print("   資料庫備份:")
        print("      - 每日完整備份")
        print("      - 每小時增量備份")
        print("      - 保留 30 天")
        print("      - 異地備份")

        print("\n   配置備份:")
        print("      - 版本控制 (Git)")
        print("      - 自動備份到雲端")
        print("      - 加密備份資料")

    @staticmethod
    def implement_failover():
        """實施故障轉移"""
        print("\n🔄 災難恢復: 故障轉移")

        print("   策略:")
        print("      - 多區域部署")
        print("      - 自動故障檢測")
        print("      - 自動切換到備用系統")
        print("      - RTO (恢復時間目標): < 5 分鐘")
        print("      - RPO (恢復點目標): < 1 小時")

    @staticmethod
    def create_runbook():
        """創建運維手冊"""
        print("\n📖 災難恢復: 運維手冊")

        scenarios = [
            "1. 資料庫故障恢復步驟",
            "2. API 服務中斷處理",
            "3. LLM 服務不可用應對",
            "4. 資料洩露事件響應",
            "5. 系統全面故障恢復",
        ]

        for scenario in scenarios:
            print(f"   {scenario}")


# ============================================================================
# 9. 示範完整部署流程
# ============================================================================

def demonstrate_production_deployment():
    """示範完整的生產部署流程"""
    print("\n" + "="*70)
    print("🎯 生產部署完整流程")
    print("="*70)

    # 1. 檢查清單
    print("\n步驟 1: 檢查部署清單")
    checklist = ProductionDeploymentChecklist()
    checklist.print_checklist()

    # 2. 設定日誌
    print("\n步驟 2: 設定日誌系統")
    logger = ProductionLogger("agent_service", "production")
    logger.logger.info("生產環境日誌系統已啟動")

    # 3. 設定監控
    print("\n步驟 3: 設定監控")
    metrics = MetricsCollector()
    metrics.record_metric("service_started", 1, "count")

    # 4. 健康檢查
    print("\n步驟 4: 健康檢查")
    health_checker = HealthChecker()

    def check_database():
        return {
            "component": "database",
            "status": HealthCheckStatus.HEALTHY,
            "message": "資料庫連接正常"
        }

    def check_redis():
        return {
            "component": "redis",
            "status": HealthCheckStatus.HEALTHY,
            "message": "Redis 連接正常"
        }

    health_checker.add_check(check_database)
    health_checker.add_check(check_redis)

    results = health_checker.run_checks()
    for result in results:
        print(f"   {result.component}: {result.status.value}")

    # 5. 性能優化
    print("\n步驟 5: 性能優化")
    optimizer = PerformanceOptimizer()
    optimizer.implement_caching()
    optimizer.implement_connection_pooling()

    # 6. 安全性強化
    print("\n步驟 6: 安全性強化")
    security = SecurityHardening()
    security.implement_authentication()
    security.implement_rate_limiting()

    # 7. 災難恢復
    print("\n步驟 7: 災難恢復準備")
    dr = DisasterRecovery()
    dr.implement_backup_strategy()

    print("\n✅ 生產部署流程完成!")


# ============================================================================
# 10. 運維最佳實踐
# ============================================================================

def print_operations_best_practices():
    """輸出運維最佳實踐"""
    print("\n" + "="*70)
    print("💡 生產運維最佳實踐")
    print("="*70)

    practices = [
        ("1. 持續監控", [
            "24/7 監控系統健康狀態",
            "設定合理的告警閾值",
            "定期審查監控指標",
            "建立值班輪換制度"
        ]),
        ("2. 自動化", [
            "自動化部署流程 (CI/CD)",
            "自動化測試和驗證",
            "自動化故障恢復",
            "自動化資源調整"
        ]),
        ("3. 文檔維護", [
            "保持文檔最新",
            "記錄所有變更",
            "維護故障排除指南",
            "分享經驗教訓"
        ]),
        ("4. 性能調優", [
            "定期性能測試",
            "識別性能瓶頸",
            "優化資源使用",
            "容量規劃"
        ]),
        ("5. 安全審計", [
            "定期安全掃描",
            "漏洞修補",
            "訪問日誌審查",
            "合規性檢查"
        ]),
        ("6. 成本優化", [
            "監控雲端成本",
            "優化資源配置",
            "使用保留實例",
            "清理未使用資源"
        ]),
        ("7. 團隊協作", [
            "明確職責分工",
            "有效溝通機制",
            "知識共享",
            "定期回顧會議"
        ]),
        ("8. 持續改進", [
            "收集用戶反饋",
            "分析系統指標",
            "實驗新技術",
            "迭代優化"
        ]),
    ]

    for title, points in practices:
        print(f"\n   {title}")
        for point in points:
            print(f"      - {point}")


# ============================================================================
# 11. 主程式
# ============================================================================

def main():
    """主程式"""
    print("="*70)
    print("Microsoft Agent Framework - 生產部署")
    print("="*70)

    # 架構介紹
    explain_production_architecture()

    # 完整部署流程
    demonstrate_production_deployment()

    # 運維最佳實踐
    print_operations_best_practices()

    print("\n" + "="*70)
    print("✅ 生產部署指南完成!")
    print("="*70)

    print("\n💡 關鍵要點:")
    print("   1. 完整的部署檢查清單確保準備充分")
    print("   2. 全面的監控和日誌系統")
    print("   3. 多層次的安全性措施")
    print("   4. 性能優化和擴展策略")
    print("   5. 災難恢復和業務連續性計劃")

    print("\n🎓 學習總結:")
    print("   恭喜!你已經完成 Microsoft Agent Framework 的完整學習")
    print("\n   你已經學會:")
    print("      ✅ Agent Framework 基礎概念和使用")
    print("      ✅ 多 Agent 編排和協作")
    print("      ✅ 工作流定義和管理")
    print("      ✅ MCP 協議整合")
    print("      ✅ Azure 雲端部署")
    print("      ✅ 狀態持久化")
    print("      ✅ 人機協作 (HITL)")
    print("      ✅ 生產環境最佳實踐")

    print("\n📚 進階學習建議:")
    print("   1. 深入研究 Azure AI Foundry 文檔")
    print("   2. 實踐構建實際應用案例")
    print("   3. 參與開源社群貢獻")
    print("   4. 關注 AI Agent 最新發展")
    print("   5. 探索其他 Agent 框架的差異")

    print("\n🌟 下一步行動:")
    print("   - 選擇一個實際問題,設計 Agent 解決方案")
    print("   - 構建 MVP (最小可行產品)")
    print("   - 部署到測試環境驗證")
    print("   - 收集反饋並迭代優化")
    print("   - 最終部署到生產環境")

    print("\n" + "="*70)
    print("祝你在 AI Agent 開發之旅上一切順利!")
    print("="*70)


if __name__ == "__main__":
    main()
