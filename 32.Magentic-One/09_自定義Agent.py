"""
自定義 Agent 開發
===================================

本範例展示如何創建和集成自定義 Agent 到 Magentic-One 系統。

自定義 Agent 的場景：
1. 特定領域的專業能力
2. 與外部系統集成
3. 特殊數據處理需求
4. 自定義工具和 API

關鍵要素：
- Agent 基礎類
- 能力定義
- 消息處理
- 與 Orchestrator 集成
"""

import os
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import json
from abc import ABC, abstractmethod


class BaseCustomAgent(ABC):
    """
    自定義 Agent 基礎類

    所有自定義 Agent 應繼承此類
    """

    def __init__(
        self,
        name: str,
        description: str,
        llm_config: Dict[str, Any] = None
    ):
        """
        初始化 Agent

        Args:
            name: Agent 名稱
            description: Agent 描述
            llm_config: LLM 配置（可選）
        """
        self.name = name
        self.description = description
        self.llm_config = llm_config or {}

        # Agent 狀態
        self.status = "initialized"
        self.capabilities: List[str] = []

        # 執行歷史
        self.execution_history: List[Dict] = []

        # 統計
        self.stats = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_execution_time': 0.0
        }

    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        執行任務（子類必須實現）

        Args:
            task: 任務描述

        Returns:
            執行結果
        """
        pass

    def register_capability(self, capability: str):
        """註冊能力"""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
            print(f"✓ {self.name} 註冊能力: {capability}")

    def get_capabilities(self) -> List[str]:
        """獲取 Agent 能力列表"""
        return self.capabilities.copy()

    def get_status(self) -> Dict[str, Any]:
        """獲取 Agent 狀態"""
        return {
            'name': self.name,
            'status': self.status,
            'capabilities': self.capabilities,
            'stats': self.stats
        }

    def _record_execution(self, task: Dict, result: Dict, duration: float):
        """記錄執行歷史"""
        record = {
            'task': task,
            'result': result,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }

        self.execution_history.append(record)

        if result.get('success', False):
            self.stats['tasks_completed'] += 1
        else:
            self.stats['tasks_failed'] += 1

        self.stats['total_execution_time'] += duration


class DataProcessorAgent(BaseCustomAgent):
    """
    數據處理 Agent

    專門處理各種數據轉換和分析任務
    """

    def __init__(self, name: str = "DataProcessor", llm_config: Dict = None):
        super().__init__(
            name=name,
            description="專門的數據處理和轉換 Agent",
            llm_config=llm_config
        )

        # 註冊能力
        self.register_capability("data_cleaning")
        self.register_capability("data_transformation")
        self.register_capability("data_validation")
        self.register_capability("data_aggregation")

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """執行數據處理任務"""
        print(f"\n{self.name}: 執行任務")

        start_time = datetime.now()
        task_type = task.get('type', 'unknown')

        try:
            if task_type == 'data_cleaning':
                result = self._clean_data(task)
            elif task_type == 'data_transformation':
                result = self._transform_data(task)
            elif task_type == 'data_validation':
                result = self._validate_data(task)
            elif task_type == 'data_aggregation':
                result = self._aggregate_data(task)
            else:
                result = {
                    'success': False,
                    'error': f'不支持的任務類型: {task_type}'
                }

            duration = (datetime.now() - start_time).total_seconds()
            self._record_execution(task, result, duration)

            return result

        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e)
            }

            duration = (datetime.now() - start_time).total_seconds()
            self._record_execution(task, error_result, duration)

            return error_result

    def _clean_data(self, task: Dict) -> Dict:
        """清理數據"""
        print("  執行數據清理...")

        return {
            'success': True,
            'action': 'data_cleaning',
            'rows_processed': 1000,
            'rows_removed': 50,
            'quality_score': 95
        }

    def _transform_data(self, task: Dict) -> Dict:
        """轉換數據"""
        print("  執行數據轉換...")

        return {
            'success': True,
            'action': 'data_transformation',
            'transformations_applied': ['normalize', 'encode', 'scale']
        }

    def _validate_data(self, task: Dict) -> Dict:
        """驗證數據"""
        print("  執行數據驗證...")

        return {
            'success': True,
            'action': 'data_validation',
            'validation_passed': True,
            'errors_found': 0
        }

    def _aggregate_data(self, task: Dict) -> Dict:
        """聚合數據"""
        print("  執行數據聚合...")

        return {
            'success': True,
            'action': 'data_aggregation',
            'aggregation_results': {
                'total': 1000,
                'average': 50.5,
                'min': 1,
                'max': 100
            }
        }


class APIIntegrationAgent(BaseCustomAgent):
    """
    API 集成 Agent

    與外部 API 進行交互
    """

    def __init__(self, name: str = "APIIntegration", llm_config: Dict = None):
        super().__init__(
            name=name,
            description="與外部 API 集成的 Agent",
            llm_config=llm_config
        )

        self.api_endpoints: Dict[str, str] = {}
        self.api_keys: Dict[str, str] = {}

        # 註冊能力
        self.register_capability("api_call")
        self.register_capability("webhook_handling")
        self.register_capability("authentication")

    def register_api(self, name: str, endpoint: str, api_key: str = None):
        """註冊 API"""
        self.api_endpoints[name] = endpoint
        if api_key:
            self.api_keys[name] = api_key

        print(f"✓ 註冊 API: {name} -> {endpoint}")

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """執行 API 調用任務"""
        print(f"\n{self.name}: 執行 API 任務")

        start_time = datetime.now()
        task_type = task.get('type', 'unknown')

        try:
            if task_type == 'api_call':
                result = self._make_api_call(task)
            elif task_type == 'webhook':
                result = self._handle_webhook(task)
            else:
                result = {
                    'success': False,
                    'error': f'不支持的任務類型: {task_type}'
                }

            duration = (datetime.now() - start_time).total_seconds()
            self._record_execution(task, result, duration)

            return result

        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e)
            }

            duration = (datetime.now() - start_time).total_seconds()
            self._record_execution(task, error_result, duration)

            return error_result

    def _make_api_call(self, task: Dict) -> Dict:
        """執行 API 調用"""
        api_name = task.get('api_name', 'unknown')
        method = task.get('method', 'GET')

        print(f"  調用 API: {api_name} ({method})")

        # 模擬 API 調用
        return {
            'success': True,
            'api': api_name,
            'method': method,
            'status_code': 200,
            'response': {'data': 'API response data'}
        }

    def _handle_webhook(self, task: Dict) -> Dict:
        """處理 Webhook"""
        print("  處理 Webhook...")

        return {
            'success': True,
            'webhook_processed': True
        }


class NotificationAgent(BaseCustomAgent):
    """
    通知 Agent

    發送各種類型的通知
    """

    def __init__(self, name: str = "Notification", llm_config: Dict = None):
        super().__init__(
            name=name,
            description="發送通知的 Agent",
            llm_config=llm_config
        )

        self.notification_handlers: Dict[str, Callable] = {}

        # 註冊能力
        self.register_capability("email_notification")
        self.register_capability("slack_notification")
        self.register_capability("webhook_notification")

    def register_handler(self, notification_type: str, handler: Callable):
        """註冊通知處理器"""
        self.notification_handlers[notification_type] = handler
        print(f"✓ 註冊通知處理器: {notification_type}")

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """執行通知任務"""
        print(f"\n{self.name}: 發送通知")

        start_time = datetime.now()
        notification_type = task.get('type', 'email')

        try:
            if notification_type in self.notification_handlers:
                handler = self.notification_handlers[notification_type]
                result = handler(task)
            else:
                result = self._default_notification(task)

            duration = (datetime.now() - start_time).total_seconds()
            self._record_execution(task, result, duration)

            return result

        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e)
            }

            duration = (datetime.now() - start_time).total_seconds()
            self._record_execution(task, error_result, duration)

            return error_result

    def _default_notification(self, task: Dict) -> Dict:
        """默認通知處理"""
        message = task.get('message', '')
        recipients = task.get('recipients', [])

        print(f"  發送通知給 {len(recipients)} 個接收者")
        print(f"  消息: {message[:50]}...")

        return {
            'success': True,
            'type': task.get('type'),
            'recipients': len(recipients),
            'message_sent': True
        }


class MonitoringAgent(BaseCustomAgent):
    """
    監控 Agent

    監控系統狀態和性能
    """

    def __init__(self, name: str = "Monitoring", llm_config: Dict = None):
        super().__init__(
            name=name,
            description="監控系統狀態的 Agent",
            llm_config=llm_config
        )

        self.metrics: Dict[str, List] = {}
        self.alerts: List[Dict] = []

        # 註冊能力
        self.register_capability("metric_collection")
        self.register_capability("alert_detection")
        self.register_capability("performance_analysis")

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """執行監控任務"""
        print(f"\n{self.name}: 執行監控")

        start_time = datetime.now()
        task_type = task.get('type', 'collect_metrics')

        try:
            if task_type == 'collect_metrics':
                result = self._collect_metrics(task)
            elif task_type == 'check_alerts':
                result = self._check_alerts(task)
            elif task_type == 'analyze_performance':
                result = self._analyze_performance(task)
            else:
                result = {
                    'success': False,
                    'error': f'不支持的任務類型: {task_type}'
                }

            duration = (datetime.now() - start_time).total_seconds()
            self._record_execution(task, result, duration)

            return result

        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e)
            }

            duration = (datetime.now() - start_time).total_seconds()
            self._record_execution(task, error_result, duration)

            return error_result

    def _collect_metrics(self, task: Dict) -> Dict:
        """收集指標"""
        metric_names = task.get('metrics', ['cpu', 'memory', 'disk'])

        print(f"  收集指標: {', '.join(metric_names)}")

        metrics = {}
        for metric in metric_names:
            metrics[metric] = {
                'value': 75.5,
                'unit': '%',
                'timestamp': datetime.now().isoformat()
            }

            if metric not in self.metrics:
                self.metrics[metric] = []

            self.metrics[metric].append(metrics[metric])

        return {
            'success': True,
            'metrics': metrics
        }

    def _check_alerts(self, task: Dict) -> Dict:
        """檢查告警"""
        print("  檢查告警條件...")

        # 模擬告警檢查
        alerts_triggered = []

        return {
            'success': True,
            'alerts_triggered': len(alerts_triggered),
            'alerts': alerts_triggered
        }

    def _analyze_performance(self, task: Dict) -> Dict:
        """分析性能"""
        print("  分析性能數據...")

        return {
            'success': True,
            'analysis': {
                'overall_health': 'good',
                'bottlenecks': [],
                'recommendations': ['優化數據庫查詢', '增加緩存']
            }
        }


def demo_data_processor():
    """數據處理 Agent 示範"""
    print("=" * 60)
    print("範例 1: 數據處理 Agent")
    print("=" * 60)

    agent = DataProcessorAgent()

    # 執行不同類型的任務
    tasks = [
        {'type': 'data_cleaning', 'data': 'raw_data.csv'},
        {'type': 'data_transformation', 'transformations': ['normalize']},
        {'type': 'data_validation', 'schema': 'schema.json'},
        {'type': 'data_aggregation', 'group_by': 'category'}
    ]

    for task in tasks:
        result = agent.execute(task)
        print(f"\n結果: {json.dumps(result, indent=2, ensure_ascii=False)}")

    # 查看統計
    print("\nAgent 統計:")
    print(json.dumps(agent.stats, indent=2, ensure_ascii=False))


def demo_api_integration():
    """API 集成 Agent 示範"""
    print("\n" + "=" * 60)
    print("範例 2: API 集成 Agent")
    print("=" * 60)

    agent = APIIntegrationAgent()

    # 註冊 APIs
    agent.register_api("weather", "https://api.weather.com", "key123")
    agent.register_api("stocks", "https://api.stocks.com", "key456")

    # 執行 API 調用
    result = agent.execute({
        'type': 'api_call',
        'api_name': 'weather',
        'method': 'GET',
        'params': {'city': 'Taipei'}
    })

    print(f"\nAPI 調用結果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


def demo_notification():
    """通知 Agent 示範"""
    print("\n" + "=" * 60)
    print("範例 3: 通知 Agent")
    print("=" * 60)

    agent = NotificationAgent()

    # 註冊自定義處理器
    def slack_handler(task):
        print("  [Slack] 發送消息到 Slack")
        return {
            'success': True,
            'type': 'slack',
            'channel': task.get('channel', '#general')
        }

    agent.register_handler('slack', slack_handler)

    # 發送通知
    tasks = [
        {
            'type': 'email',
            'recipients': ['user1@example.com', 'user2@example.com'],
            'message': '任務已完成'
        },
        {
            'type': 'slack',
            'channel': '#alerts',
            'message': '系統告警'
        }
    ]

    for task in tasks:
        result = agent.execute(task)
        print(f"\n通知結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def demo_monitoring():
    """監控 Agent 示範"""
    print("\n" + "=" * 60)
    print("範例 4: 監控 Agent")
    print("=" * 60)

    agent = MonitoringAgent()

    # 收集指標
    result = agent.execute({
        'type': 'collect_metrics',
        'metrics': ['cpu', 'memory', 'disk', 'network']
    })

    print(f"\n收集的指標:")
    print(json.dumps(result['metrics'], indent=2, ensure_ascii=False))

    # 分析性能
    result = agent.execute({
        'type': 'analyze_performance'
    })

    print(f"\n性能分析:")
    print(json.dumps(result['analysis'], indent=2, ensure_ascii=False))


def demo_agent_integration():
    """Agent 集成示範"""
    print("\n" + "=" * 60)
    print("範例 5: 多個自定義 Agent 集成")
    print("=" * 60)

    # 創建多個 Agent
    data_agent = DataProcessorAgent()
    api_agent = APIIntegrationAgent()
    notify_agent = NotificationAgent()
    monitor_agent = MonitoringAgent()

    # 模擬工作流
    print("\n執行數據處理工作流:")

    # 1. 收集外部數據
    print("\n1. 從 API 獲取數據")
    api_agent.register_api("data_source", "https://api.example.com")
    api_result = api_agent.execute({
        'type': 'api_call',
        'api_name': 'data_source',
        'method': 'GET'
    })

    # 2. 處理數據
    print("\n2. 清理和轉換數據")
    data_result = data_agent.execute({
        'type': 'data_cleaning',
        'data': api_result.get('response')
    })

    # 3. 監控性能
    print("\n3. 監控處理性能")
    monitor_result = monitor_agent.execute({
        'type': 'collect_metrics',
        'metrics': ['processing_time', 'memory_usage']
    })

    # 4. 發送完成通知
    print("\n4. 發送完成通知")
    notify_result = notify_agent.execute({
        'type': 'email',
        'recipients': ['admin@example.com'],
        'message': '數據處理工作流完成'
    })

    print("\n✓ 工作流執行完成")

    # 顯示所有 Agent 的狀態
    print("\n所有 Agent 狀態:")
    for agent in [data_agent, api_agent, notify_agent, monitor_agent]:
        status = agent.get_status()
        print(f"\n{agent.name}:")
        print(f"  能力: {', '.join(status['capabilities'])}")
        print(f"  完成任務: {status['stats']['tasks_completed']}")


if __name__ == "__main__":
    demo_data_processor()
    demo_api_integration()
    demo_notification()
    demo_monitoring()
    demo_agent_integration()

    print("\n" + "=" * 60)
    print("自定義 Agent 示範完成！")
    print("=" * 60)
