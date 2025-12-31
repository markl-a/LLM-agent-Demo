"""
Mastra 監控和日誌示例

本示例展示如何實現全面的監控和日誌系統。

功能：
1. 結構化日誌
2. 性能監控
3. 追蹤和可觀測性
4. 指標收集
5. 儀表板和告警
"""

import os
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import json
from datetime import datetime
import time

load_dotenv()


class MastraMonitoring:
    """Mastra 監控客戶端"""

    def __init__(self, api_url: str = None):
        """初始化監控客戶端"""
        self.api_url = api_url or os.getenv('MASTRA_API_URL', 'http://localhost:3000')
        self.api_key = os.getenv('MASTRA_API_KEY')

        self.headers = {
            'Content-Type': 'application/json',
        }
        if self.api_key:
            self.headers['Authorization'] = f'Bearer {self.api_key}'


def example_1_structured_logging():
    """示例 1：結構化日誌"""
    print("=" * 60)
    print("示例 1：結構化日誌")
    print("=" * 60)

    logging_config = {
        'format': 'json',
        'levels': {
            'DEBUG': {
                'value': 10,
                'color': 'gray',
                'description': '詳細調試信息'
            },
            'INFO': {
                'value': 20,
                'color': 'blue',
                'description': '一般信息'
            },
            'WARN': {
                'value': 30,
                'color': 'yellow',
                'description': '警告信息'
            },
            'ERROR': {
                'value': 40,
                'color': 'red',
                'description': '錯誤信息'
            },
            'FATAL': {
                'value': 50,
                'color': 'magenta',
                'description': '嚴重錯誤'
            }
        },
        'fields': {
            'required': [
                'timestamp',      # ISO 8601 時間戳
                'level',          # 日誌級別
                'message',        # 日誌消息
                'service',        # 服務名稱
            ],
            'optional': [
                'trace_id',       # 追蹤 ID
                'span_id',        # 跨度 ID
                'user_id',        # 用戶 ID
                'session_id',     # 會話 ID
                'agent_name',     # Agent 名稱
                'duration_ms',    # 持續時間
                'error',          # 錯誤詳情
                'metadata'        # 額外元數據
            ]
        },
        'destinations': [
            {
                'type': 'console',
                'level': 'INFO',
                'format': 'pretty'
            },
            {
                'type': 'file',
                'level': 'DEBUG',
                'path': '/var/log/mastra/app.log',
                'rotation': {
                    'size': '100MB',
                    'keep': 10
                }
            },
            {
                'type': 'remote',
                'level': 'WARN',
                'service': 'datadog',
                'config': {
                    'api_key': '{{env.DATADOG_API_KEY}}',
                    'tags': ['env:production', 'service:mastra']
                }
            }
        ]
    }

    print(f"\n日誌配置: {json.dumps(logging_config, indent=2, ensure_ascii=False)}")

    # 日誌示例
    log_examples = [
        {
            'timestamp': '2025-01-15T10:30:45.123Z',
            'level': 'INFO',
            'message': 'Agent started successfully',
            'service': 'mastra-api',
            'agent_name': 'customer-service-agent',
            'metadata': {
                'version': '1.0.0',
                'config': 'default'
            }
        },
        {
            'timestamp': '2025-01-15T10:30:46.456Z',
            'level': 'DEBUG',
            'message': 'Processing user query',
            'service': 'mastra-api',
            'trace_id': 'trace-123',
            'span_id': 'span-456',
            'user_id': 'user-789',
            'session_id': 'session-abc',
            'agent_name': 'customer-service-agent',
            'metadata': {
                'query': 'How do I reset my password?',
                'query_length': 27
            }
        },
        {
            'timestamp': '2025-01-15T10:30:47.789Z',
            'level': 'ERROR',
            'message': 'LLM API call failed',
            'service': 'mastra-api',
            'trace_id': 'trace-123',
            'agent_name': 'customer-service-agent',
            'duration_ms': 1500,
            'error': {
                'type': 'RateLimitError',
                'message': 'Rate limit exceeded',
                'code': 'rate_limit_exceeded',
                'retryable': True,
                'retry_after': 30
            }
        }
    ]

    print("\n日誌示例:")
    for log in log_examples:
        print(json.dumps(log, indent=2, ensure_ascii=False))
        print()


def example_2_performance_metrics():
    """示例 2：性能指標"""
    print("\n" + "=" * 60)
    print("示例 2：性能指標收集")
    print("=" * 60)

    metrics_config = {
        'agent_metrics': {
            'request_count': {
                'type': 'counter',
                'description': '請求總數',
                'labels': ['agent_name', 'status']
            },
            'request_duration': {
                'type': 'histogram',
                'description': '請求持續時間',
                'labels': ['agent_name'],
                'buckets': [10, 50, 100, 500, 1000, 5000, 10000]  # ms
            },
            'active_sessions': {
                'type': 'gauge',
                'description': '活躍會話數',
                'labels': ['agent_name']
            },
            'error_rate': {
                'type': 'gauge',
                'description': '錯誤率',
                'labels': ['agent_name', 'error_type']
            }
        },
        'llm_metrics': {
            'llm_calls': {
                'type': 'counter',
                'description': 'LLM 調用次數',
                'labels': ['provider', 'model', 'status']
            },
            'llm_latency': {
                'type': 'histogram',
                'description': 'LLM 響應延遲',
                'labels': ['provider', 'model'],
                'buckets': [100, 500, 1000, 2000, 5000, 10000]
            },
            'token_usage': {
                'type': 'counter',
                'description': 'Token 使用量',
                'labels': ['provider', 'model', 'type'],  # type: prompt/completion
            },
            'llm_cost': {
                'type': 'counter',
                'description': 'LLM 調用成本',
                'labels': ['provider', 'model']
            }
        },
        'system_metrics': {
            'cpu_usage': {
                'type': 'gauge',
                'description': 'CPU 使用率',
                'unit': 'percent'
            },
            'memory_usage': {
                'type': 'gauge',
                'description': '內存使用',
                'unit': 'bytes'
            },
            'network_io': {
                'type': 'counter',
                'description': '網絡 I/O',
                'labels': ['direction'],  # in/out
                'unit': 'bytes'
            }
        },
        'business_metrics': {
            'user_satisfaction': {
                'type': 'gauge',
                'description': '用戶滿意度',
                'labels': ['agent_name'],
                'unit': 'score'  # 0-5
            },
            'conversation_length': {
                'type': 'histogram',
                'description': '對話長度',
                'labels': ['agent_name'],
                'buckets': [1, 3, 5, 10, 20, 50]
            },
            'resolution_rate': {
                'type': 'gauge',
                'description': '問題解決率',
                'labels': ['agent_name'],
                'unit': 'percent'
            }
        }
    }

    print(f"\n指標配置: {json.dumps(metrics_config, indent=2, ensure_ascii=False)}")

    # Prometheus 格式示例
    print("\nPrometheus 指標示例:")
    prometheus_metrics = '''
# HELP mastra_request_count Total number of requests
# TYPE mastra_request_count counter
mastra_request_count{agent_name="customer-service",status="success"} 1542
mastra_request_count{agent_name="customer-service",status="error"} 23

# HELP mastra_request_duration Request duration in milliseconds
# TYPE mastra_request_duration histogram
mastra_request_duration_bucket{agent_name="customer-service",le="100"} 850
mastra_request_duration_bucket{agent_name="customer-service",le="500"} 1420
mastra_request_duration_bucket{agent_name="customer-service",le="1000"} 1520
mastra_request_duration_bucket{agent_name="customer-service",le="+Inf"} 1565
mastra_request_duration_sum{agent_name="customer-service"} 425000
mastra_request_duration_count{agent_name="customer-service"} 1565

# HELP mastra_llm_latency LLM response latency
# TYPE mastra_llm_latency histogram
mastra_llm_latency_bucket{provider="openai",model="gpt-4",le="1000"} 150
mastra_llm_latency_bucket{provider="openai",model="gpt-4",le="2000"} 280
mastra_llm_latency_bucket{provider="openai",model="gpt-4",le="5000"} 295
mastra_llm_latency_bucket{provider="openai",model="gpt-4",le="+Inf"} 300

# HELP mastra_token_usage Token usage
# TYPE mastra_token_usage counter
mastra_token_usage{provider="openai",model="gpt-4",type="prompt"} 125000
mastra_token_usage{provider="openai",model="gpt-4",type="completion"} 89000
    '''
    print(prometheus_metrics)


def example_3_distributed_tracing():
    """示例 3：分佈式追蹤"""
    print("\n" + "=" * 60)
    print("示例 3：分佈式追蹤（OpenTelemetry）")
    print("=" * 60)

    tracing_config = {
        'provider': 'opentelemetry',
        'exporter': {
            'type': 'otlp',
            'endpoint': 'https://otel-collector:4318',
            'headers': {
                'api-key': '{{env.OTEL_API_KEY}}'
            }
        },
        'sampling': {
            'strategy': 'probabilistic',
            'rate': 0.1  # 採樣 10% 的請求
        },
        'instrumentation': {
            'http': {
                'enabled': True,
                'capture_headers': True,
                'capture_body': False
            },
            'database': {
                'enabled': True,
                'capture_queries': True
            },
            'llm': {
                'enabled': True,
                'capture_prompts': True,
                'capture_completions': True
            }
        }
    }

    print(f"\n追蹤配置: {json.dumps(tracing_config, indent=2, ensure_ascii=False)}")

    # Trace 示例
    trace_example = {
        'trace_id': 'trace-abc123',
        'spans': [
            {
                'span_id': 'span-001',
                'parent_span_id': None,
                'name': 'POST /api/agents/customer-service/chat',
                'kind': 'SERVER',
                'start_time': '2025-01-15T10:30:45.000Z',
                'end_time': '2025-01-15T10:30:47.500Z',
                'duration_ms': 2500,
                'attributes': {
                    'http.method': 'POST',
                    'http.url': '/api/agents/customer-service/chat',
                    'http.status_code': 200,
                    'user.id': 'user-789',
                    'session.id': 'session-abc'
                }
            },
            {
                'span_id': 'span-002',
                'parent_span_id': 'span-001',
                'name': 'retrieve_context',
                'kind': 'INTERNAL',
                'start_time': '2025-01-15T10:30:45.100Z',
                'end_time': '2025-01-15T10:30:45.350Z',
                'duration_ms': 250,
                'attributes': {
                    'db.system': 'pinecone',
                    'db.operation': 'query',
                    'vector.topk': 5
                }
            },
            {
                'span_id': 'span-003',
                'parent_span_id': 'span-001',
                'name': 'openai.chat.completions',
                'kind': 'CLIENT',
                'start_time': '2025-01-15T10:30:45.400Z',
                'end_time': '2025-01-15T10:30:47.200Z',
                'duration_ms': 1800,
                'attributes': {
                    'llm.provider': 'openai',
                    'llm.model': 'gpt-4',
                    'llm.temperature': 0.7,
                    'llm.prompt_tokens': 450,
                    'llm.completion_tokens': 220,
                    'llm.total_tokens': 670
                }
            },
            {
                'span_id': 'span-004',
                'parent_span_id': 'span-001',
                'name': 'save_to_memory',
                'kind': 'INTERNAL',
                'start_time': '2025-01-15T10:30:47.250Z',
                'end_time': '2025-01-15T10:30:47.450Z',
                'duration_ms': 200,
                'attributes': {
                    'db.system': 'redis',
                    'db.operation': 'set'
                }
            }
        ],
        'total_duration_ms': 2500,
        'span_count': 4
    }

    print(f"\nTrace 示例: {json.dumps(trace_example, indent=2, ensure_ascii=False)}")

    print("\n可視化追蹤:")
    print("""
    POST /api/agents/customer-service/chat [2500ms]
    ├─ retrieve_context [250ms]
    │  └─ pinecone.query
    ├─ openai.chat.completions [1800ms]
    │  └─ HTTP POST to api.openai.com
    └─ save_to_memory [200ms]
       └─ redis.set
    """)


def example_4_real_time_monitoring():
    """示例 4：實時監控儀表板"""
    print("\n" + "=" * 60)
    print("示例 4：實時監控儀表板")
    print("=" * 60)

    dashboard_config = {
        'name': 'Mastra Production Dashboard',
        'refresh_interval': '30s',
        'panels': [
            {
                'id': 'requests',
                'title': '請求吞吐量',
                'type': 'graph',
                'metrics': ['mastra_request_count'],
                'aggregation': 'rate',
                'timeRange': '1h',
                'visualization': 'line'
            },
            {
                'id': 'latency',
                'title': '響應延遲 (P50, P95, P99)',
                'type': 'graph',
                'metrics': ['mastra_request_duration'],
                'percentiles': [50, 95, 99],
                'timeRange': '1h',
                'visualization': 'multi-line'
            },
            {
                'id': 'error_rate',
                'title': '錯誤率',
                'type': 'single-stat',
                'metrics': ['mastra_request_count{status="error"}'],
                'calculation': 'percentage',
                'thresholds': {
                    'good': '< 1%',
                    'warning': '1-5%',
                    'critical': '> 5%'
                }
            },
            {
                'id': 'llm_usage',
                'title': 'LLM Token 使用',
                'type': 'graph',
                'metrics': ['mastra_token_usage'],
                'groupBy': ['provider', 'model'],
                'timeRange': '24h',
                'visualization': 'stacked-area'
            },
            {
                'id': 'active_sessions',
                'title': '活躍會話',
                'type': 'single-stat',
                'metrics': ['mastra_active_sessions'],
                'aggregation': 'current'
            },
            {
                'id': 'cost',
                'title': 'LLM 成本',
                'type': 'graph',
                'metrics': ['mastra_llm_cost'],
                'groupBy': ['provider'],
                'timeRange': '7d',
                'visualization': 'bar'
            },
            {
                'id': 'top_agents',
                'title': '最活躍的 Agents',
                'type': 'table',
                'metrics': ['mastra_request_count'],
                'groupBy': ['agent_name'],
                'sortBy': 'count',
                'limit': 10
            },
            {
                'id': 'error_distribution',
                'title': '錯誤分佈',
                'type': 'pie',
                'metrics': ['mastra_request_count{status="error"}'],
                'groupBy': ['error_type']
            }
        ],
        'alerts': [
            {
                'name': 'High Error Rate',
                'condition': 'error_rate > 5% for 5m',
                'severity': 'critical',
                'notification': ['pagerduty', 'slack']
            },
            {
                'name': 'Slow Response Time',
                'condition': 'p95_latency > 3s for 10m',
                'severity': 'warning',
                'notification': ['slack']
            },
            {
                'name': 'High Cost',
                'condition': 'daily_cost > $1000',
                'severity': 'warning',
                'notification': ['email']
            }
        ]
    }

    print(f"\n儀表板配置: {json.dumps(dashboard_config, indent=2, ensure_ascii=False)}")


def example_5_log_aggregation():
    """示例 5：日誌聚合和分析"""
    print("\n" + "=" * 60)
    print("示例 5：日誌聚合和分析")
    print("=" * 60)

    log_analysis = {
        'aggregation_queries': [
            {
                'name': '錯誤統計',
                'query': '''
                    SELECT
                        error.type,
                        COUNT(*) as count,
                        COUNT(DISTINCT user_id) as affected_users
                    FROM logs
                    WHERE level = 'ERROR'
                      AND timestamp > NOW() - INTERVAL 1 HOUR
                    GROUP BY error.type
                    ORDER BY count DESC
                ''',
                'visualization': 'table'
            },
            {
                'name': '慢查詢',
                'query': '''
                    SELECT
                        agent_name,
                        AVG(duration_ms) as avg_duration,
                        MAX(duration_ms) as max_duration,
                        COUNT(*) as count
                    FROM logs
                    WHERE duration_ms > 2000
                      AND timestamp > NOW() - INTERVAL 1 HOUR
                    GROUP BY agent_name
                ''',
                'visualization': 'bar-chart'
            },
            {
                'name': '用戶活動時間分佈',
                'query': '''
                    SELECT
                        DATE_TRUNC('hour', timestamp) as hour,
                        COUNT(DISTINCT user_id) as active_users
                    FROM logs
                    WHERE timestamp > NOW() - INTERVAL 24 HOUR
                    GROUP BY hour
                    ORDER BY hour
                ''',
                'visualization': 'line-chart'
            },
            {
                'name': 'Agent 性能對比',
                'query': '''
                    SELECT
                        agent_name,
                        COUNT(*) as requests,
                        AVG(duration_ms) as avg_latency,
                        SUM(CASE WHEN level = 'ERROR' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as error_rate
                    FROM logs
                    WHERE timestamp > NOW() - INTERVAL 1 DAY
                    GROUP BY agent_name
                ''',
                'visualization': 'table'
            }
        ],
        'anomaly_detection': {
            'enabled': True,
            'algorithms': [
                {
                    'name': 'statistical',
                    'method': 'z-score',
                    'threshold': 3,
                    'metrics': ['request_duration', 'error_rate']
                },
                {
                    'name': 'machine_learning',
                    'method': 'isolation_forest',
                    'training_window': '7d',
                    'metrics': ['all']
                }
            ],
            'actions': [
                'log_anomaly',
                'send_alert',
                'create_incident'
            ]
        }
    }

    print(f"\n日誌分析配置: {json.dumps(log_analysis, indent=2, ensure_ascii=False)}")


def example_6_alerting_system():
    """示例 6：告警系統"""
    print("\n" + "=" * 60)
    print("示例 6：智能告警系統")
    print("=" * 60)

    alerting_config = {
        'alert_rules': [
            {
                'name': 'api_down',
                'type': 'availability',
                'condition': 'up == 0',
                'duration': '1m',
                'severity': 'critical',
                'description': 'API 服務不可用',
                'runbook': 'https://docs.example.com/runbooks/api-down',
                'notifications': [
                    {
                        'channel': 'pagerduty',
                        'priority': 'high',
                        'escalation': 'on-call-engineer'
                    },
                    {
                        'channel': 'slack',
                        'channel_id': '#incidents'
                    }
                ]
            },
            {
                'name': 'high_error_rate',
                'type': 'threshold',
                'condition': 'error_rate > 0.05',
                'duration': '5m',
                'severity': 'high',
                'description': '錯誤率過高（>5%）',
                'notifications': [
                    {
                        'channel': 'slack',
                        'channel_id': '#alerts'
                    },
                    {
                        'channel': 'email',
                        'recipients': ['team@example.com']
                    }
                ]
            },
            {
                'name': 'slow_response',
                'type': 'latency',
                'condition': 'p95_latency > 3000',
                'duration': '10m',
                'severity': 'medium',
                'description': 'P95 延遲超過 3 秒',
                'notifications': [
                    {
                        'channel': 'slack',
                        'channel_id': '#performance'
                    }
                ]
            },
            {
                'name': 'budget_exceeded',
                'type': 'cost',
                'condition': 'daily_llm_cost > 1000',
                'severity': 'medium',
                'description': '每日 LLM 成本超過 $1000',
                'notifications': [
                    {
                        'channel': 'email',
                        'recipients': ['finance@example.com', 'team-lead@example.com']
                    }
                ]
            }
        ],
        'notification_channels': {
            'slack': {
                'webhook_url': '{{env.SLACK_WEBHOOK_URL}}',
                'default_channel': '#alerts',
                'mention_on_critical': '@here'
            },
            'pagerduty': {
                'integration_key': '{{env.PAGERDUTY_KEY}}',
                'severity_mapping': {
                    'critical': 'critical',
                    'high': 'error',
                    'medium': 'warning',
                    'low': 'info'
                }
            },
            'email': {
                'smtp_server': 'smtp.gmail.com',
                'from': 'alerts@example.com',
                'template': 'alert-email-template'
            }
        },
        'alert_grouping': {
            'enabled': True,
            'window': '5m',
            'max_alerts': 10,
            'group_by': ['severity', 'alert_name']
        },
        'suppression': {
            'enabled': True,
            'rules': [
                {
                    'name': 'maintenance_window',
                    'schedule': 'cron: 0 2 * * 0',  # 每週日凌晨 2 點
                    'duration': '2h',
                    'suppress_all': True
                },
                {
                    'name': 'known_issue',
                    'condition': 'alert_name == "slow_response" AND agent_name == "legacy-agent"',
                    'until': '2025-02-01'
                }
            ]
        }
    }

    print(f"\n告警配置: {json.dumps(alerting_config, indent=2, ensure_ascii=False)}")


def example_7_audit_logging():
    """示例 7：審計日誌"""
    print("\n" + "=" * 60)
    print("示例 7：審計日誌和合規性")
    print("=" * 60)

    audit_config = {
        'enabled': True,
        'events': {
            'user_actions': [
                'user.login',
                'user.logout',
                'user.password_change',
                'user.permissions_change'
            ],
            'data_access': [
                'data.read',
                'data.create',
                'data.update',
                'data.delete',
                'data.export'
            ],
            'system_changes': [
                'agent.create',
                'agent.update',
                'agent.delete',
                'config.change',
                'integration.add',
                'integration.remove'
            ],
            'security': [
                'auth.failed',
                'permission.denied',
                'api_key.created',
                'api_key.revoked'
            ]
        },
        'fields': {
            'required': [
                'event_type',
                'timestamp',
                'actor',
                'action',
                'resource',
                'result'
            ],
            'optional': [
                'ip_address',
                'user_agent',
                'geo_location',
                'before_state',
                'after_state',
                'reason'
            ]
        },
        'retention': {
            'period': '7y',  # 保留 7 年（合規要求）
            'storage': 'cold-storage',
            'encryption': 'AES-256'
        },
        'compliance': {
            'standards': ['SOC2', 'GDPR', 'HIPAA'],
            'features': [
                'immutable_logs',
                'tamper_detection',
                'access_control',
                'data_lineage'
            ]
        }
    }

    print(f"\n審計配置: {json.dumps(audit_config, indent=2, ensure_ascii=False)}")

    # 審計日誌示例
    audit_log_examples = [
        {
            'event_id': 'audit-001',
            'event_type': 'agent.create',
            'timestamp': '2025-01-15T10:30:45.123Z',
            'actor': {
                'user_id': 'user-admin',
                'email': 'admin@example.com',
                'role': 'admin'
            },
            'action': 'create',
            'resource': {
                'type': 'agent',
                'id': 'agent-customer-service',
                'name': 'Customer Service Agent'
            },
            'result': 'success',
            'metadata': {
                'ip_address': '192.168.1.100',
                'user_agent': 'Mozilla/5.0...',
                'after_state': {
                    'model': 'gpt-4',
                    'temperature': 0.7
                }
            }
        },
        {
            'event_id': 'audit-002',
            'event_type': 'data.export',
            'timestamp': '2025-01-15T11:00:00.000Z',
            'actor': {
                'user_id': 'user-analyst',
                'email': 'analyst@example.com',
                'role': 'analyst'
            },
            'action': 'export',
            'resource': {
                'type': 'conversation_history',
                'count': 1500,
                'date_range': '2025-01-01 to 2025-01-14'
            },
            'result': 'success',
            'metadata': {
                'reason': 'Monthly analytics report',
                'approved_by': 'manager@example.com'
            }
        },
        {
            'event_id': 'audit-003',
            'event_type': 'auth.failed',
            'timestamp': '2025-01-15T12:00:00.000Z',
            'actor': {
                'ip_address': '203.0.113.42',
                'attempted_user': 'admin'
            },
            'action': 'login',
            'result': 'failed',
            'metadata': {
                'reason': 'invalid_password',
                'attempt_count': 3
            }
        }
    ]

    print("\n審計日誌示例:")
    for log in audit_log_examples:
        print(json.dumps(log, indent=2, ensure_ascii=False))
        print()


def example_8_cost_tracking():
    """示例 8：成本追蹤"""
    print("\n" + "=" * 60)
    print("示例 8：成本追蹤和優化")
    print("=" * 60)

    cost_tracking = {
        'llm_costs': {
            'openai': {
                'gpt-4': {
                    'input': 0.03,    # per 1K tokens
                    'output': 0.06
                },
                'gpt-3.5-turbo': {
                    'input': 0.0015,
                    'output': 0.002
                }
            },
            'anthropic': {
                'claude-3-opus': {
                    'input': 0.015,
                    'output': 0.075
                }
            }
        },
        'tracking_metrics': [
            {
                'name': 'total_cost',
                'description': '總成本',
                'formula': 'SUM(prompt_tokens * input_price + completion_tokens * output_price) / 1000'
            },
            {
                'name': 'cost_per_user',
                'description': '每用戶成本',
                'formula': 'total_cost / unique_users'
            },
            {
                'name': 'cost_per_conversation',
                'description': '每對話成本',
                'formula': 'total_cost / conversation_count'
            },
            {
                'name': 'cost_by_agent',
                'description': 'Agent 成本分佈',
                'groupBy': 'agent_name'
            }
        ],
        'budgets': {
            'daily': {
                'limit': 1000,
                'warning_threshold': 800,
                'actions': {
                    '80%': 'notify_team',
                    '100%': 'throttle_requests'
                }
            },
            'monthly': {
                'limit': 25000,
                'warning_threshold': 20000
            }
        },
        'optimization_recommendations': [
            {
                'rule': 'high_token_usage',
                'condition': 'avg_prompt_tokens > 2000',
                'suggestion': '考慮使用 prompt 壓縮或摘要'
            },
            {
                'rule': 'expensive_model_overuse',
                'condition': 'gpt4_usage > 80% AND task_complexity < 0.5',
                'suggestion': '簡單任務可以使用 gpt-3.5-turbo'
            },
            {
                'rule': 'cache_miss_rate_high',
                'condition': 'cache_miss_rate > 0.7',
                'suggestion': '優化緩存策略以減少 LLM 調用'
            }
        ]
    }

    print(f"\n成本追蹤配置: {json.dumps(cost_tracking, indent=2, ensure_ascii=False)}")

    # 成本報告示例
    cost_report = {
        'period': '2025-01-15',
        'total_cost': 452.30,
        'breakdown': {
            'by_provider': {
                'openai': {
                    'cost': 380.50,
                    'percentage': 84.1
                },
                'anthropic': {
                    'cost': 71.80,
                    'percentage': 15.9
                }
            },
            'by_agent': {
                'customer-service': 245.20,
                'technical-support': 132.40,
                'sales': 74.70
            },
            'by_model': {
                'gpt-4': 315.60,
                'gpt-3.5-turbo': 64.90,
                'claude-3-opus': 71.80
            }
        },
        'metrics': {
            'total_requests': 15420,
            'total_tokens': 8_456_000,
            'cost_per_request': 0.029,
            'cost_per_1k_tokens': 0.053
        },
        'budget_status': {
            'daily_budget': 1000,
            'used': 452.30,
            'remaining': 547.70,
            'percentage_used': 45.2
        }
    }

    print(f"\n成本報告示例: {json.dumps(cost_report, indent=2, ensure_ascii=False)}")


def example_9_slo_sli():
    """示例 9：SLO/SLI 監控"""
    print("\n" + "=" * 60)
    print("示例 9：SLO/SLI 定義和監控")
    print("=" * 60)

    slo_config = {
        'availability': {
            'slo': 99.9,  # 99.9% 可用性
            'sli': {
                'metric': 'successful_requests / total_requests',
                'window': '30d'
            },
            'error_budget': {
                'monthly': 0.1,  # 0.1% 錯誤預算
                'remaining': 0.045,
                'alert_threshold': 0.02
            }
        },
        'latency': {
            'slo': {
                'p50': 500,   # 50% 請求 < 500ms
                'p95': 2000,  # 95% 請求 < 2s
                'p99': 5000   # 99% 請求 < 5s
            },
            'sli': {
                'metric': 'request_duration_ms',
                'percentiles': [50, 95, 99]
            }
        },
        'quality': {
            'slo': {
                'user_satisfaction': 4.0,  # 平均評分 >= 4.0
                'resolution_rate': 0.85    # 85% 問題解決率
            },
            'sli': {
                'satisfaction_metric': 'AVG(user_rating)',
                'resolution_metric': 'resolved_issues / total_issues'
            }
        }
    }

    print(f"\nSLO 配置: {json.dumps(slo_config, indent=2, ensure_ascii=False)}")

    print("\nSLO 儀表板:")
    print("""
    ┌─────────────────────────────────────────┐
    │ Availability SLO: 99.9%                 │
    │ Current: 99.95% ✓                       │
    │ Error Budget Remaining: 45% ⚠️          │
    └─────────────────────────────────────────┘

    ┌─────────────────────────────────────────┐
    │ Latency SLO                             │
    │ P50: 450ms (target: <500ms) ✓           │
    │ P95: 1.8s (target: <2s) ✓               │
    │ P99: 4.2s (target: <5s) ✓               │
    └─────────────────────────────────────────┘

    ┌─────────────────────────────────────────┐
    │ Quality SLO                             │
    │ User Satisfaction: 4.2 ✓                │
    │ Resolution Rate: 87% ✓                  │
    └─────────────────────────────────────────┘
    """)


def example_10_best_practices():
    """示例 10：監控最佳實踐"""
    print("\n" + "=" * 60)
    print("示例 10：監控和日誌最佳實踐")
    print("=" * 60)

    best_practices = '''
    📚 監控和日誌最佳實踐

    1. 日誌記錄
       ✅ 使用結構化日誌（JSON）
       ✅ 包含上下文信息（trace_id, user_id 等）
       ✅ 選擇適當的日誌級別
       ✅ 不記錄敏感信息
       ✅ 使用統一的時間格式（ISO 8601）

    2. 指標收集
       ✅ 遵循 USE 方法（Utilization, Saturation, Errors）
       ✅ 收集 RED 指標（Rate, Errors, Duration）
       ✅ 使用標籤進行維度分組
       ✅ 避免高基數標籤
       ✅ 定期清理過期指標

    3. 追蹤
       ✅ 為所有請求生成 trace_id
       ✅ 在服務間傳遞上下文
       ✅ 記錄關鍵操作的 span
       ✅ 適當的採樣策略

    4. 告警
       ✅ 告警應該可操作
       ✅ 避免告警疲勞
       ✅ 使用正確的嚴重程度
       ✅ 提供 runbook 鏈接
       ✅ 實現告警分組和抑制

    5. 儀表板
       ✅ 為不同受眾創建不同視圖
       ✅ 使用適當的可視化類型
       ✅ 包含關鍵指標和 SLO
       ✅ 保持簡潔和聚焦

    6. 成本優化
       ✅ 控制日誌量（採樣、過濾）
       ✅ 使用適當的保留期
       ✅ 冷存儲歸檔舊數據
       ✅ 監控監控系統本身的成本

    7. 安全和合規
       ✅ 加密敏感日誌
       ✅ 實現訪問控制
       ✅ 審計日誌的修改
       ✅ 滿足合規要求（GDPR, HIPAA 等）

    8. 可維護性
       ✅ 文檔化指標和日誌
       ✅ 版本控制儀表板和告警
       ✅ 定期審查和更新
       ✅ 團隊培訓

    9. 性能
       ✅ 異步日誌記錄
       ✅ 批量發送指標
       ✅ 使用本地代理聚合
       ✅ 避免阻塞主流程

    10. 可觀測性成熟度
        Level 1: 基礎日誌和指標
        Level 2: 結構化日誌、追蹤
        Level 3: 自動化告警、儀表板
        Level 4: 異常檢測、預測性監控
        Level 5: 自動修復、AIOps

    推薦工具棧:
    • 日誌: ELK, Loki, CloudWatch Logs
    • 指標: Prometheus, Datadog, New Relic
    • 追蹤: Jaeger, Zipkin, Tempo
    • 告警: PagerDuty, Opsgenie
    • 儀表板: Grafana, Kibana
    • APM: Datadog, New Relic, Dynatrace
    '''

    print(best_practices)


def main():
    """主函數"""
    print("\n📊 Mastra 監控和日誌示例\n")

    try:
        example_1_structured_logging()
        example_2_performance_metrics()
        example_3_distributed_tracing()
        example_4_real_time_monitoring()
        example_5_log_aggregation()
        example_6_alerting_system()
        example_7_audit_logging()
        example_8_cost_tracking()
        example_9_slo_sli()
        example_10_best_practices()

        print("\n" + "=" * 60)
        print("✅ 所有示例運行完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")


if __name__ == "__main__":
    main()
