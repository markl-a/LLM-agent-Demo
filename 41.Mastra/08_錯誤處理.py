"""
Mastra 錯誤處理和重試機制示例

本示例展示如何處理錯誤和實現可靠的重試策略。

功能：
1. 錯誤類型和分類
2. 重試策略
3. 降級方案
4. 斷路器模式
5. 錯誤恢復
"""

import os
import requests
from typing import Dict, Any, List, Optional, Callable
from dotenv import load_dotenv
import json
import time
from datetime import datetime
import random

load_dotenv()


class MastraErrorHandler:
    """Mastra 錯誤處理客戶端"""

    def __init__(self, api_url: str = None):
        """初始化錯誤處理客戶端"""
        self.api_url = api_url or os.getenv('MASTRA_API_URL', 'http://localhost:3000')
        self.api_key = os.getenv('MASTRA_API_KEY')

        self.headers = {
            'Content-Type': 'application/json',
        }
        if self.api_key:
            self.headers['Authorization'] = f'Bearer {self.api_key}'


def example_1_error_types():
    """示例 1：錯誤類型和分類"""
    print("=" * 60)
    print("示例 1：錯誤類型和分類")
    print("=" * 60)

    error_types = {
        'transient': {
            'description': '暫時性錯誤（可重試）',
            'examples': [
                {
                    'type': 'NetworkError',
                    'message': '網絡連接超時',
                    'retry': True,
                    'strategy': 'exponential_backoff'
                },
                {
                    'type': 'RateLimitError',
                    'message': 'API 速率限制',
                    'retry': True,
                    'strategy': 'wait_and_retry',
                    'waitTime': '{{response.headers.retry-after}}'
                },
                {
                    'type': 'ServiceUnavailable',
                    'message': '服務暫時不可用',
                    'retry': True,
                    'strategy': 'exponential_backoff',
                    'maxRetries': 3
                }
            ]
        },
        'permanent': {
            'description': '永久性錯誤（不應重試）',
            'examples': [
                {
                    'type': 'AuthenticationError',
                    'message': 'API 密鑰無效',
                    'retry': False,
                    'action': 'notify_admin'
                },
                {
                    'type': 'ValidationError',
                    'message': '輸入參數無效',
                    'retry': False,
                    'action': 'return_error_to_user'
                },
                {
                    'type': 'NotFoundError',
                    'message': '資源不存在',
                    'retry': False,
                    'action': 'use_fallback'
                }
            ]
        },
        'application': {
            'description': '應用邏輯錯誤',
            'examples': [
                {
                    'type': 'BusinessRuleError',
                    'message': '違反業務規則',
                    'retry': False,
                    'action': 'log_and_notify'
                },
                {
                    'type': 'DataInconsistency',
                    'message': '數據不一致',
                    'retry': False,
                    'action': 'rollback_transaction'
                }
            ]
        },
        'llm_specific': {
            'description': 'LLM 特定錯誤',
            'examples': [
                {
                    'type': 'ContentFilterError',
                    'message': '內容被過濾',
                    'retry': False,
                    'action': 'rephrase_prompt'
                },
                {
                    'type': 'ContextLengthExceeded',
                    'message': '超過上下文長度',
                    'retry': True,
                    'action': 'compress_context'
                },
                {
                    'type': 'ModelOverloaded',
                    'message': '模型過載',
                    'retry': True,
                    'strategy': 'exponential_backoff'
                }
            ]
        }
    }

    print("\n錯誤類型分類:")
    for category, info in error_types.items():
        print(f"\n{category.upper()}: {info['description']}")
        for example in info['examples']:
            print(f"  • {example['type']}: {example['message']}")
            print(f"    可重試: {example.get('retry', False)}")
            if 'strategy' in example:
                print(f"    策略: {example['strategy']}")
            if 'action' in example:
                print(f"    行動: {example['action']}")


def example_2_retry_strategies():
    """示例 2：重試策略"""
    print("\n" + "=" * 60)
    print("示例 2：重試策略")
    print("=" * 60)

    retry_strategies = {
        'simple': {
            'description': '簡單重試',
            'config': {
                'maxRetries': 3,
                'delay': 1000,  # 固定延遲 1 秒
            },
            'implementation': '''
                async function simpleRetry(fn, maxRetries = 3) {
                    for (let i = 0; i < maxRetries; i++) {
                        try {
                            return await fn();
                        } catch (error) {
                            if (i === maxRetries - 1) throw error;
                            await sleep(1000);
                        }
                    }
                }
            '''
        },
        'exponential_backoff': {
            'description': '指數退避',
            'config': {
                'maxRetries': 5,
                'initialDelay': 1000,
                'maxDelay': 32000,
                'multiplier': 2,
                'jitter': True  # 添加隨機性
            },
            'implementation': '''
                async function exponentialBackoff(fn, config) {
                    let delay = config.initialDelay;

                    for (let i = 0; i < config.maxRetries; i++) {
                        try {
                            return await fn();
                        } catch (error) {
                            if (i === config.maxRetries - 1) throw error;

                            // 計算延遲
                            const actualDelay = config.jitter
                                ? delay * (0.5 + Math.random())
                                : delay;

                            await sleep(Math.min(actualDelay, config.maxDelay));
                            delay *= config.multiplier;
                        }
                    }
                }
            ''',
            'delays': [1000, 2000, 4000, 8000, 16000]  # 示例延遲序列
        },
        'adaptive': {
            'description': '自適應重試',
            'config': {
                'maxRetries': 10,
                'baseDelay': 1000,
                'successWindow': 100,  # 最近 100 次請求
                'adjustmentFactor': 1.5
            },
            'implementation': '''
                class AdaptiveRetry {
                    constructor() {
                        this.recentRequests = [];
                        this.successRate = 1.0;
                    }

                    async retry(fn) {
                        // 根據最近的成功率調整重試策略
                        const maxRetries = this.successRate > 0.9 ? 3 : 5;
                        const delay = this.baseDelay / this.successRate;

                        // 執行重試...
                    }

                    updateSuccessRate(success) {
                        this.recentRequests.push(success);
                        if (this.recentRequests.length > this.successWindow) {
                            this.recentRequests.shift();
                        }
                        this.successRate = this.recentRequests.filter(s => s).length /
                                         this.recentRequests.length;
                    }
                }
            '''
        },
        'circuit_breaker': {
            'description': '斷路器模式',
            'config': {
                'failureThreshold': 5,      # 失敗閾值
                'successThreshold': 2,      # 成功閾值
                'timeout': 60000,           # 超時時間
                'halfOpenRequests': 3       # 半開狀態允許的請求數
            },
            'states': {
                'closed': '正常狀態，允許所有請求',
                'open': '斷開狀態，拒絕所有請求',
                'half_open': '半開狀態，允許少量測試請求'
            },
            'implementation': '''
                class CircuitBreaker {
                    constructor(config) {
                        this.state = 'closed';
                        this.failureCount = 0;
                        this.successCount = 0;
                        this.nextAttempt = Date.now();
                    }

                    async execute(fn) {
                        if (this.state === 'open') {
                            if (Date.now() < this.nextAttempt) {
                                throw new Error('Circuit breaker is open');
                            }
                            this.state = 'half_open';
                        }

                        try {
                            const result = await fn();
                            this.onSuccess();
                            return result;
                        } catch (error) {
                            this.onFailure();
                            throw error;
                        }
                    }

                    onSuccess() {
                        this.failureCount = 0;
                        if (this.state === 'half_open') {
                            this.successCount++;
                            if (this.successCount >= this.successThreshold) {
                                this.state = 'closed';
                                this.successCount = 0;
                            }
                        }
                    }

                    onFailure() {
                        this.failureCount++;
                        this.successCount = 0;
                        if (this.failureCount >= this.failureThreshold) {
                            this.state = 'open';
                            this.nextAttempt = Date.now() + this.timeout;
                        }
                    }
                }
            '''
        }
    }

    print("\n重試策略對比:")
    for name, strategy in retry_strategies.items():
        print(f"\n{name.upper()}:")
        print(f"  描述: {strategy['description']}")
        print(f"  配置: {json.dumps(strategy['config'], indent=4, ensure_ascii=False)}")
        if 'delays' in strategy:
            print(f"  延遲序列: {strategy['delays']}")


def example_3_fallback_strategies():
    """示例 3：降級方案"""
    print("\n" + "=" * 60)
    print("示例 3：降級方案和備援策略")
    print("=" * 60)

    fallback_config = {
        'llm_fallback': {
            'description': 'LLM 降級鏈',
            'chain': [
                {
                    'provider': 'openai',
                    'model': 'gpt-4',
                    'priority': 1
                },
                {
                    'provider': 'anthropic',
                    'model': 'claude-3-opus',
                    'priority': 2
                },
                {
                    'provider': 'openai',
                    'model': 'gpt-3.5-turbo',
                    'priority': 3
                },
                {
                    'provider': 'local',
                    'model': 'llama-2-70b',
                    'priority': 4
                }
            ],
            'logic': '''
                async function callWithFallback(prompt) {
                    for (const option of fallbackChain) {
                        try {
                            return await callLLM(option, prompt);
                        } catch (error) {
                            console.log(`${option.model} failed, trying next...`);
                            continue;
                        }
                    }
                    throw new Error('All LLM providers failed');
                }
            '''
        },
        'cache_fallback': {
            'description': '緩存降級',
            'strategy': '''
                1. 嘗試調用 LLM
                2. 如果失敗，檢查緩存
                3. 如果緩存存在，返回緩存結果（標記為緩存）
                4. 如果緩存不存在，返回通用響應
            ''',
            'example': '''
                async function withCacheFallback(query) {
                    try {
                        const result = await callLLM(query);
                        await cache.set(query, result);
                        return result;
                    } catch (error) {
                        const cached = await cache.get(query);
                        if (cached) {
                            return {
                                ...cached,
                                fromCache: true,
                                warning: 'Using cached response due to service error'
                            };
                        }
                        return getGenericResponse(query);
                    }
                }
            '''
        },
        'simplified_response': {
            'description': '簡化響應',
            'strategy': '''
                當完整響應失敗時，提供簡化版本：
                1. 減少輸出長度
                2. 降低複雜度
                3. 使用模板響應
            ''',
            'example': {
                'full_response': '詳細的技術解釋，包含代碼示例和最佳實踐...',
                'fallback_response': '這是一個簡化的回答。詳細信息暫時無法提供。'
            }
        },
        'hybrid_approach': {
            'description': '混合方法',
            'strategy': '''
                結合多種降級策略：
                1. 主要: 嘗試主 LLM
                2. 降級 1: 嘗試備用 LLM
                3. 降級 2: 使用緩存
                4. 降級 3: 使用規則基礎系統
                5. 最後: 返回錯誤消息
            '''
        }
    }

    print(f"\n降級配置: {json.dumps(fallback_config, indent=2, ensure_ascii=False)}")


def example_4_error_recovery():
    """示例 4：錯誤恢復機制"""
    print("\n" + "=" * 60)
    print("示例 4：錯誤恢復和補償")
    print("=" * 60)

    recovery_patterns = {
        'compensation': {
            'description': '補償事務',
            'scenario': '''
                場景: 多步驟工作流中的第 3 步失敗

                步驟:
                1. 創建訂單 ✓
                2. 扣款 ✓
                3. 發貨 ✗ (失敗)

                補償操作:
                1. 回滾發貨（不需要，未成功）
                2. 退款（補償步驟 2）
                3. 取消訂單（補償步驟 1）
            ''',
            'implementation': '''
                class SagaOrchestrator {
                    async execute(steps) {
                        const completed = [];

                        try {
                            for (const step of steps) {
                                const result = await step.execute();
                                completed.push({ step, result });
                            }
                            return completed;
                        } catch (error) {
                            // 回滾已完成的步驟
                            for (const { step, result } of completed.reverse()) {
                                await step.compensate(result);
                            }
                            throw error;
                        }
                    }
                }
            '''
        },
        'checkpoint': {
            'description': '檢查點恢復',
            'scenario': '''
                在長時間運行的任務中保存檢查點：
                1. 定期保存進度
                2. 失敗時從最近的檢查點恢復
                3. 避免重新開始
            ''',
            'example': '''
                async function processLargeDataset(data) {
                    const checkpointInterval = 100;
                    let checkpoint = await loadCheckpoint();

                    for (let i = checkpoint.lastProcessed; i < data.length; i++) {
                        try {
                            await processItem(data[i]);

                            if (i % checkpointInterval === 0) {
                                await saveCheckpoint({ lastProcessed: i });
                            }
                        } catch (error) {
                            await saveCheckpoint({ lastProcessed: i });
                            throw error;
                        }
                    }
                }
            '''
        },
        'graceful_degradation': {
            'description': '優雅降級',
            'levels': [
                '100%: 完整功能',
                '80%: 禁用非關鍵功能',
                '60%: 只提供核心功能',
                '40%: 只讀模式',
                '20%: 緊急模式（最小功能）',
                '0%: 完全不可用'
            ],
            'implementation': '''
                function getDegradationLevel() {
                    if (errorRate < 0.01) return 100;
                    if (errorRate < 0.05) return 80;
                    if (errorRate < 0.10) return 60;
                    if (errorRate < 0.20) return 40;
                    if (errorRate < 0.50) return 20;
                    return 0;
                }

                async function handleRequest(req) {
                    const level = getDegradationLevel();

                    if (level >= 80) {
                        return await fullFeatureHandler(req);
                    } else if (level >= 60) {
                        return await coreFeatureHandler(req);
                    } else if (level >= 40) {
                        return await readOnlyHandler(req);
                    } else {
                        return emergencyResponse();
                    }
                }
            '''
        }
    }

    print("\n恢復模式:")
    for name, pattern in recovery_patterns.items():
        print(f"\n{name.upper()}:")
        print(f"  {pattern['description']}")
        if 'scenario' in pattern:
            print(pattern['scenario'])


def example_5_error_logging():
    """示例 5：錯誤日誌和監控"""
    print("\n" + "=" * 60)
    print("示例 5：錯誤日誌和監控")
    print("=" * 60)

    logging_config = {
        'structured_logging': {
            'format': 'json',
            'fields': {
                'timestamp': 'ISO 8601 格式',
                'level': 'ERROR, WARN, INFO, DEBUG',
                'error_type': '錯誤類型',
                'error_message': '錯誤消息',
                'stack_trace': '堆棧跟蹤',
                'context': {
                    'user_id': '用戶 ID',
                    'session_id': '會話 ID',
                    'request_id': '請求 ID',
                    'agent_name': 'Agent 名稱'
                },
                'metadata': '額外信息'
            },
            'example': {
                'timestamp': '2025-01-15T10:30:45.123Z',
                'level': 'ERROR',
                'error_type': 'RateLimitError',
                'error_message': 'OpenAI API rate limit exceeded',
                'stack_trace': 'Error: Rate limit...',
                'context': {
                    'user_id': 'user-123',
                    'session_id': 'session-456',
                    'request_id': 'req-789',
                    'agent_name': 'customer-service-agent'
                },
                'metadata': {
                    'retry_count': 3,
                    'last_retry_at': '2025-01-15T10:30:40.000Z'
                }
            }
        },
        'error_tracking': {
            'platform': 'Sentry / Datadog / New Relic',
            'features': [
                '錯誤聚合和分組',
                '錯誤趨勢分析',
                '實時告警',
                '堆棧跟蹤分析',
                '錯誤重現步驟',
                '影響範圍評估'
            ]
        },
        'metrics': {
            'error_rate': {
                'description': '錯誤率',
                'formula': 'errors / total_requests',
                'alert_threshold': '> 1%'
            },
            'error_by_type': {
                'description': '按類型統計錯誤',
                'categories': ['NetworkError', 'ValidationError', 'LLMError', ...]
            },
            'mttr': {
                'description': '平均恢復時間',
                'formula': '總恢復時間 / 錯誤次數',
                'target': '< 5 minutes'
            },
            'error_budget': {
                'description': '錯誤預算',
                'formula': '(1 - SLO) * total_requests',
                'example': 'SLO 99.9% → 允許 0.1% 錯誤'
            }
        }
    }

    print(f"\n日誌配置: {json.dumps(logging_config, indent=2, ensure_ascii=False)}")


def example_6_timeout_handling():
    """示例 6：超時處理"""
    print("\n" + "=" * 60)
    print("示例 6：超時處理策略")
    print("=" * 60)

    timeout_strategies = {
        'simple_timeout': {
            'description': '簡單超時',
            'example': '''
                async function withTimeout(promise, timeoutMs) {
                    const timeout = new Promise((_, reject) =>
                        setTimeout(() => reject(new Error('Timeout')), timeoutMs)
                    );
                    return Promise.race([promise, timeout]);
                }

                // 使用
                try {
                    const result = await withTimeout(
                        callLLM(prompt),
                        30000  // 30 秒超時
                    );
                } catch (error) {
                    if (error.message === 'Timeout') {
                        // 處理超時
                    }
                }
            '''
        },
        'cascading_timeout': {
            'description': '級聯超時',
            'config': {
                'total_timeout': 60000,      # 總超時 60 秒
                'llm_timeout': 30000,        # LLM 調用 30 秒
                'database_timeout': 10000,   # 數據庫 10 秒
                'cache_timeout': 5000        # 緩存 5 秒
            },
            'example': '''
                async function cascadingTimeout() {
                    const startTime = Date.now();
                    const totalTimeout = 60000;

                    // 第一步: 緩存查詢 (5s)
                    const remaining1 = totalTimeout - (Date.now() - startTime);
                    const cached = await withTimeout(cache.get(), Math.min(5000, remaining1));

                    if (cached) return cached;

                    // 第二步: LLM 調用 (30s)
                    const remaining2 = totalTimeout - (Date.now() - startTime);
                    return await withTimeout(callLLM(), Math.min(30000, remaining2));
                }
            '''
        },
        'adaptive_timeout': {
            'description': '自適應超時',
            'strategy': '''
                根據歷史數據調整超時時間：
                1. 追蹤請求的 P95 延遲
                2. 設置超時 = P95 * 2
                3. 定期更新
            ''',
            'example': '''
                class AdaptiveTimeout {
                    constructor() {
                        this.latencies = [];
                        this.defaultTimeout = 30000;
                    }

                    getTimeout() {
                        if (this.latencies.length < 100) {
                            return this.defaultTimeout;
                        }

                        // 計算 P95
                        const sorted = this.latencies.sort((a, b) => a - b);
                        const p95 = sorted[Math.floor(sorted.length * 0.95)];

                        return Math.min(p95 * 2, this.defaultTimeout * 3);
                    }

                    recordLatency(latency) {
                        this.latencies.push(latency);
                        if (this.latencies.length > 1000) {
                            this.latencies.shift();
                        }
                    }
                }
            '''
        }
    }

    print("\n超時策略:")
    for name, strategy in timeout_strategies.items():
        print(f"\n{name.upper()}:")
        print(f"  {strategy['description']}")
        if 'config' in strategy:
            print(f"  配置: {json.dumps(strategy['config'], indent=4, ensure_ascii=False)}")


def example_7_error_notification():
    """示例 7：錯誤通知和告警"""
    print("\n" + "=" * 60)
    print("示例 7：錯誤通知和告警")
    print("=" * 60)

    notification_config = {
        'severity_levels': {
            'critical': {
                'description': '嚴重錯誤，立即處理',
                'examples': ['服務完全不可用', '數據丟失', '安全漏洞'],
                'notification': {
                    'channels': ['pagerduty', 'phone', 'slack', 'email'],
                    'recipients': ['on-call-engineer', 'team-lead', 'manager'],
                    'response_time': '< 5 minutes'
                }
            },
            'high': {
                'description': '高優先級錯誤',
                'examples': ['部分功能不可用', '性能嚴重下降'],
                'notification': {
                    'channels': ['slack', 'email'],
                    'recipients': ['on-call-engineer', 'team'],
                    'response_time': '< 30 minutes'
                }
            },
            'medium': {
                'description': '中等錯誤',
                'examples': ['非關鍵功能異常', '偶爾失敗'],
                'notification': {
                    'channels': ['slack'],
                    'recipients': ['team'],
                    'response_time': '< 4 hours'
                }
            },
            'low': {
                'description': '低優先級錯誤',
                'examples': ['日誌警告', '輕微異常'],
                'notification': {
                    'channels': ['dashboard'],
                    'recipients': ['team'],
                    'response_time': '< 24 hours'
                }
            }
        },
        'alert_rules': [
            {
                'name': 'high_error_rate',
                'condition': 'error_rate > 5% for 5 minutes',
                'severity': 'critical',
                'action': 'notify_oncall'
            },
            {
                'name': 'llm_failures',
                'condition': 'llm_error_count > 10 in 1 minute',
                'severity': 'high',
                'action': 'activate_fallback'
            },
            {
                'name': 'slow_response',
                'condition': 'p95_latency > 5s for 10 minutes',
                'severity': 'medium',
                'action': 'investigate'
            }
        ],
        'notification_template': {
            'title': '{{severity}} Alert: {{error_type}}',
            'body': '''
                錯誤類型: {{error_type}}
                發生時間: {{timestamp}}
                影響範圍: {{affected_users}} 用戶
                錯誤率: {{error_rate}}%
                錯誤消息: {{error_message}}

                儀表板: {{dashboard_link}}
                Runbook: {{runbook_link}}
            ''',
            'actions': [
                {'label': 'Acknowledge', 'action': 'acknowledge'},
                {'label': 'View Logs', 'action': 'view_logs'},
                {'label': 'Start Investigation', 'action': 'create_incident'}
            ]
        }
    }

    print(f"\n通知配置: {json.dumps(notification_config, indent=2, ensure_ascii=False)}")


def example_8_validation_errors():
    """示例 8：輸入驗證和錯誤處理"""
    print("\n" + "=" * 60)
    print("示例 8：輸入驗證")
    print("=" * 60)

    validation_examples = '''
    1. 參數驗證
    ✅ 檢查必需字段
    ✅ 驗證數據類型
    ✅ 檢查值範圍
    ✅ 驗證格式（email, URL, etc.）

    示例:
    ```python
    def validate_agent_config(config):
        errors = []

        # 檢查必需字段
        if 'name' not in config:
            errors.append("Missing required field: name")

        # 驗證類型
        if not isinstance(config.get('temperature'), (int, float)):
            errors.append("temperature must be a number")

        # 檢查範圍
        temp = config.get('temperature', 0.7)
        if not 0 <= temp <= 2:
            errors.append("temperature must be between 0 and 2")

        # 驗證格式
        if 'email' in config:
            if not re.match(r'^[^@]+@[^@]+\.[^@]+$', config['email']):
                errors.append("Invalid email format")

        if errors:
            raise ValidationError(errors)

        return config
    ```

    2. 內容過濾
    ✅ 檢測有害內容
    ✅ PII 檢測
    ✅ 敏感信息過濾

    3. 速率限制驗證
    ✅ 檢查請求頻率
    ✅ 用戶配額檢查

    4. 業務規則驗證
    ✅ 檢查業務邏輯約束
    ✅ 驗證狀態轉換
    '''

    print(validation_examples)


def example_9_error_recovery_workflow():
    """示例 9：錯誤恢復工作流"""
    print("\n" + "=" * 60)
    print("示例 9：完整的錯誤恢復工作流")
    print("=" * 60)

    workflow = '''
    錯誤恢復工作流程：

    1. 錯誤檢測
       ├─ 捕獲異常
       ├─ 記錄錯誤
       └─ 分類錯誤類型

    2. 初步響應
       ├─ 如果是暫時性錯誤 → 重試
       ├─ 如果是永久性錯誤 → 降級
       └─ 如果是關鍵錯誤 → 告警

    3. 重試邏輯（如適用）
       ├─ 檢查重試次數
       ├─ 計算退避延遲
       ├─ 執行重試
       └─ 如果成功 → 記錄恢復

    4. 降級處理（如重試失敗）
       ├─ 嘗試備用 LLM
       ├─ 使用緩存響應
       ├─ 提供簡化響應
       └─ 返回錯誤消息

    5. 記錄和監控
       ├─ 記錄結構化日誌
       ├─ 更新指標
       ├─ 發送告警（如需要）
       └─ 創建事件報告

    6. 用戶通知
       ├─ 友好的錯誤消息
       ├─ 建議的下一步操作
       └─ 支持聯繫信息

    7. 後續分析
       ├─ 錯誤模式識別
       ├─ 根本原因分析
       ├─ 改進措施
       └─ 更新文檔

    代碼示例:
    ```typescript
    async function robustExecute(fn) {
        const maxRetries = 3;
        let lastError;

        for (let attempt = 0; attempt < maxRetries; attempt++) {
            try {
                // 1. 嘗試執行
                const result = await fn();

                // 2. 成功 - 記錄和返回
                logger.info('Operation succeeded', { attempt });
                return result;

            } catch (error) {
                lastError = error;

                // 3. 記錄錯誤
                logger.error('Operation failed', {
                    attempt,
                    error: error.message,
                    stack: error.stack
                });

                // 4. 錯誤分類
                const errorType = classifyError(error);

                // 5. 決定策略
                if (errorType === 'permanent') {
                    break;  // 不重試
                }

                if (attempt < maxRetries - 1) {
                    // 6. 計算退避
                    const delay = Math.pow(2, attempt) * 1000;
                    await sleep(delay);
                }
            }
        }

        // 7. 所有重試都失敗 - 嘗試降級
        try {
            const fallback = await executeFallback(fn);
            logger.info('Fallback succeeded');
            return fallback;
        } catch (fallbackError) {
            // 8. 降級也失敗 - 記錄並拋出
            logger.error('All recovery attempts failed', {
                originalError: lastError,
                fallbackError
            });

            // 9. 發送告警
            await sendAlert({
                severity: 'high',
                message: 'Critical operation failed',
                error: lastError
            });

            throw lastError;
        }
    }
    ```
    '''

    print(workflow)


def example_10_best_practices():
    """示例 10：錯誤處理最佳實踐"""
    print("\n" + "=" * 60)
    print("示例 10：錯誤處理最佳實踐")
    print("=" * 60)

    best_practices = '''
    📚 錯誤處理最佳實踐

    1. 預防優於治療
       ✅ 輸入驗證
       ✅ 類型檢查
       ✅ 邊界條件測試
       ✅ 防禦性編程

    2. 錯誤要有意義
       ✅ 清晰的錯誤消息
       ✅ 提供上下文信息
       ✅ 建議解決方案
       ✅ 包含錯誤代碼

    3. 不要吞掉錯誤
       ❌ try { ... } catch (e) { }
       ✅ try { ... } catch (e) { logger.error(e); throw e; }

    4. 適當的錯誤粒度
       ✅ 自定義錯誤類型
       ✅ 錯誤層次結構
       ✅ 錯誤分類

    5. 優雅的降級
       ✅ 提供備選方案
       ✅ 部分功能可用
       ✅ 明確告知用戶

    6. 完善的日誌
       ✅ 結構化日誌
       ✅ 適當的日誌級別
       ✅ 上下文信息
       ✅ 可搜索和分析

    7. 監控和告警
       ✅ 實時監控
       ✅ 智能告警
       ✅ 錯誤趨勢分析
       ✅ 自動化響應

    8. 測試錯誤路徑
       ✅ 單元測試異常情況
       ✅ 集成測試錯誤場景
       ✅ 混沌工程
       ✅ 故障注入測試

    9. 文檔化
       ✅ 錯誤代碼文檔
       ✅ 故障排除指南
       ✅ Runbooks
       ✅ 已知問題清單

    10. 持續改進
        ✅ 事後分析
        ✅ 根本原因分析
        ✅ 改進措施跟蹤
        ✅ 知識分享

    反模式（避免）:
    ❌ 忽略錯誤
    ❌ 籠統的錯誤消息
    ❌ 無限重試
    ❌ 不記錄錯誤
    ❌ 向用戶顯示技術細節
    ❌ 沒有降級計劃
    ❌ 過度捕獲異常
    '''

    print(best_practices)


def main():
    """主函數"""
    print("\n⚠️  Mastra 錯誤處理和重試機制示例\n")

    try:
        example_1_error_types()
        example_2_retry_strategies()
        example_3_fallback_strategies()
        example_4_error_recovery()
        example_5_error_logging()
        example_6_timeout_handling()
        example_7_error_notification()
        example_8_validation_errors()
        example_9_error_recovery_workflow()
        example_10_best_practices()

        print("\n" + "=" * 60)
        print("✅ 所有示例運行完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")


if __name__ == "__main__":
    main()
