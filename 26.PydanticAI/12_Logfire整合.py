"""
Pydantic AI - Logfire 整合範例

本範例展示：
1. Logfire 設置和配置
2. 實時監控
3. 性能追蹤
4. 成本分析
5. 調試工具

Logfire 是 Pydantic 團隊開發的監控平台，與 Pydantic AI 深度整合

注意：需要安裝 logfire
pip install 'pydantic-ai[logfire]'
"""

import asyncio
import time
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext


# ============================================================================
# 範例 1: 基本 Logfire 設置
# ============================================================================

def example_1_basic_setup():
    """基本的 Logfire 設置"""
    print("\n" + "="*60)
    print("範例 1: Logfire 基本設置")
    print("="*60)

    try:
        import logfire

        # 配置 Logfire（需要 API token）
        # logfire.configure(token='your-token-here')

        print("Logfire 配置步驟：")
        print("1. 訪問 https://logfire.pydantic.dev")
        print("2. 創建賬號並獲取 API token")
        print("3. 運行：logfire.configure(token='your-token')")
        print("4. 或設置環境變量：LOGFIRE_TOKEN")

        print("\n配置後，所有 Pydantic AI 操作將自動記錄到 Logfire")

    except ImportError:
        print("⚠️  Logfire 未安裝")
        print("   安裝：pip install 'pydantic-ai[logfire]'")


# ============================================================================
# 範例 2: 自動追蹤 Agent 執行
# ============================================================================

async def example_2_auto_tracking():
    """自動追蹤 Agent 執行"""
    print("\n" + "="*60)
    print("範例 2: 自動追蹤")
    print("="*60)

    try:
        import logfire

        # 配置 Logfire（使用環境變量或直接配置）
        # logfire.configure()

        agent = Agent('openai:gpt-4')

        print("執行 Agent（所有操作將記錄到 Logfire）...")

        # Logfire 自動追蹤：
        # - Agent 調用
        # - LLM 請求/響應
        # - Token 使用
        # - 執行時間
        # - 錯誤信息

        result = await agent.run('解釋什麼是 Pydantic AI')

        print(f"✓ 完成（查看 Logfire 儀表板了解詳情）")
        print(f"回應：{result.data[:100]}...")

    except ImportError:
        print("⚠️  Logfire 未安裝")


# ============================================================================
# 範例 3: 手動日誌記錄
# ============================================================================

async def example_3_manual_logging():
    """手動添加自定義日誌"""
    print("\n" + "="*60)
    print("範例 3: 手動日誌記錄")
    print("="*60)

    try:
        import logfire

        # 手動記錄日誌
        with logfire.span('custom_operation'):
            logfire.info('開始自定義操作')

            # 模擬操作
            await asyncio.sleep(0.5)

            logfire.info('操作完成', extra={
                'duration': 0.5,
                'status': 'success'
            })

        print("✓ 自定義日誌已記錄")

    except ImportError:
        print("⚠️  使用標準日誌記錄")
        print("開始自定義操作")
        await asyncio.sleep(0.5)
        print("✓ 操作完成")


# ============================================================================
# 範例 4: 性能監控
# ============================================================================

class PerformanceMonitor:
    """性能監控器"""

    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
        self.metrics = {}

    def __enter__(self):
        """進入上下文"""
        self.start_time = time.time()
        print(f"  ⏱️  開始：{self.operation_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        self.end_time = time.time()
        duration = self.end_time - self.start_time

        print(f"  ✓ 完成：{self.operation_name} ({duration:.2f}s)")

        try:
            import logfire
            logfire.info(
                f'{self.operation_name} completed',
                extra={
                    'duration': duration,
                    'metrics': self.metrics
                }
            )
        except ImportError:
            pass

    def record_metric(self, name: str, value: any):
        """記錄指標"""
        self.metrics[name] = value


async def example_4_performance_monitoring():
    """性能監控"""
    print("\n" + "="*60)
    print("範例 4: 性能監控")
    print("="*60)

    agent = Agent('openai:gpt-4')

    with PerformanceMonitor('AI 查詢') as monitor:
        result = await agent.run('用一句話解釋機器學習')

        # 記錄自定義指標
        monitor.record_metric('response_length', len(result.data))
        monitor.record_metric('model', 'gpt-4')


# ============================================================================
# 範例 5: 成本追蹤
# ============================================================================

class CostTracker:
    """成本追蹤器"""

    # 簡化的定價（實際價格請查看官方文檔）
    PRICING = {
        'gpt-4': {
            'input': 0.03 / 1000,   # $ per 1K tokens
            'output': 0.06 / 1000,
        },
        'gpt-3.5-turbo': {
            'input': 0.0015 / 1000,
            'output': 0.002 / 1000,
        }
    }

    def __init__(self):
        self.total_cost = 0.0
        self.operations = []

    def track_operation(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """追蹤單次操作成本"""
        model_key = model.split(':')[-1]  # 從 'openai:gpt-4' 提取 'gpt-4'

        pricing = self.PRICING.get(model_key, self.PRICING['gpt-3.5-turbo'])

        cost = (
            input_tokens * pricing['input'] +
            output_tokens * pricing['output']
        )

        self.total_cost += cost

        operation = {
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost': cost,
            'timestamp': datetime.now().isoformat()
        }

        self.operations.append(operation)

        return cost

    def get_summary(self) -> dict:
        """獲取成本摘要"""
        return {
            'total_cost': self.total_cost,
            'total_operations': len(self.operations),
            'average_cost': self.total_cost / len(self.operations) if self.operations else 0,
            'operations': self.operations
        }


async def example_5_cost_tracking():
    """成本追蹤"""
    print("\n" + "="*60)
    print("範例 5: 成本追蹤")
    print("="*60)

    tracker = CostTracker()
    agent = Agent('openai:gpt-4')

    # 執行多個查詢
    queries = [
        "什麼是 AI？",
        "解釋機器學習",
        "什麼是深度學習？"
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n查詢 {i}: {query}")

        result = await agent.run(query)

        # 獲取 token 使用情況
        usage = result.usage()

        # 追蹤成本
        cost = tracker.track_operation(
            model='gpt-4',
            input_tokens=usage.request_tokens or 0,
            output_tokens=usage.response_tokens or 0
        )

        print(f"  Tokens: {usage.request_tokens} 輸入 + {usage.response_tokens} 輸出")
        print(f"  成本: ${cost:.4f}")

    # 顯示總成本
    summary = tracker.get_summary()
    print(f"\n總成本摘要：")
    print(f"  總操作數: {summary['total_operations']}")
    print(f"  總成本: ${summary['total_cost']:.4f}")
    print(f"  平均成本: ${summary['average_cost']:.4f}")


# ============================================================================
# 範例 6: 錯誤追蹤
# ============================================================================

async def example_6_error_tracking():
    """錯誤追蹤和日誌記錄"""
    print("\n" + "="*60)
    print("範例 6: 錯誤追蹤")
    print("="*60)

    agent = Agent('openai:gpt-4')

    try:
        import logfire

        # 使用 Logfire 追蹤錯誤
        with logfire.span('risky_operation'):
            try:
                # 模擬可能出錯的操作
                result = await agent.run('這是一個測試')

                logfire.info('操作成功', extra={
                    'response_length': len(result.data)
                })

            except Exception as e:
                # 記錄錯誤
                logfire.error('操作失敗', exc_info=e, extra={
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                })
                raise

        print("✓ 操作完成（錯誤已追蹤）")

    except ImportError:
        print("⚠️  使用標準錯誤處理")

        try:
            result = await agent.run('這是一個測試')
            print(f"✓ 操作成功")
        except Exception as e:
            print(f"✗ 錯誤：{e}")


# ============================================================================
# 範例 7: 自定義儀表板指標
# ============================================================================

class CustomMetrics:
    """自定義指標收集器"""

    def __init__(self):
        self.metrics = {
            'requests': 0,
            'successes': 0,
            'failures': 0,
            'total_tokens': 0,
            'total_duration': 0.0
        }

    async def tracked_request(
        self,
        agent: Agent,
        prompt: str
    ) -> Optional[any]:
        """追蹤的請求"""
        self.metrics['requests'] += 1

        start_time = time.time()

        try:
            result = await agent.run(prompt)

            # 成功
            self.metrics['successes'] += 1

            usage = result.usage()
            self.metrics['total_tokens'] += (
                (usage.request_tokens or 0) +
                (usage.response_tokens or 0)
            )

            duration = time.time() - start_time
            self.metrics['total_duration'] += duration

            # 記錄到 Logfire
            try:
                import logfire
                logfire.info('request_completed', extra={
                    'duration': duration,
                    'tokens': usage.total_tokens,
                    'success': True
                })
            except ImportError:
                pass

            return result

        except Exception as e:
            # 失敗
            self.metrics['failures'] += 1

            duration = time.time() - start_time
            self.metrics['total_duration'] += duration

            # 記錄錯誤
            try:
                import logfire
                logfire.error('request_failed', exc_info=e, extra={
                    'duration': duration,
                    'error': str(e)
                })
            except ImportError:
                pass

            return None

    def get_dashboard_data(self) -> dict:
        """獲取儀表板數據"""
        total_requests = self.metrics['requests']

        return {
            'total_requests': total_requests,
            'success_rate': (
                self.metrics['successes'] / total_requests * 100
                if total_requests > 0 else 0
            ),
            'failure_rate': (
                self.metrics['failures'] / total_requests * 100
                if total_requests > 0 else 0
            ),
            'avg_duration': (
                self.metrics['total_duration'] / total_requests
                if total_requests > 0 else 0
            ),
            'total_tokens': self.metrics['total_tokens'],
            'avg_tokens_per_request': (
                self.metrics['total_tokens'] / total_requests
                if total_requests > 0 else 0
            )
        }


async def example_7_custom_dashboard():
    """自定義儀表板指標"""
    print("\n" + "="*60)
    print("範例 7: 自定義儀表板")
    print("="*60)

    metrics = CustomMetrics()
    agent = Agent('openai:gpt-4')

    # 執行多個請求
    prompts = [
        "什麼是 Python？",
        "解釋列表推導式",
        "什麼是裝飾器？",
        "async/await 是什麼？"
    ]

    for prompt in prompts:
        print(f"\n處理：{prompt[:30]}...")
        await metrics.tracked_request(agent, prompt)

    # 顯示儀表板數據
    dashboard = metrics.get_dashboard_data()

    print("\n" + "="*60)
    print("儀表板摘要")
    print("="*60)
    print(f"總請求數：{dashboard['total_requests']}")
    print(f"成功率：{dashboard['success_rate']:.1f}%")
    print(f"失敗率：{dashboard['failure_rate']:.1f}%")
    print(f"平均響應時間：{dashboard['avg_duration']:.2f}s")
    print(f"總 Tokens：{dashboard['total_tokens']}")
    print(f"平均 Tokens/請求：{dashboard['avg_tokens_per_request']:.0f}")


# ============================================================================
# 範例 8: 分布式追蹤
# ============================================================================

async def example_8_distributed_tracing():
    """分布式追蹤（多個 Agent 協作）"""
    print("\n" + "="*60)
    print("範例 8: 分布式追蹤")
    print("="*60)

    try:
        import logfire

        # 創建多個 Agent
        researcher = Agent('openai:gpt-4', name='researcher')
        analyzer = Agent('openai:gpt-4', name='analyzer')
        writer = Agent('openai:gpt-4', name='writer')

        # 追蹤整個工作流
        with logfire.span('research_workflow'):

            # 步驟 1: 研究
            with logfire.span('research_step'):
                print("  → 研究階段")
                research = await researcher.run('列出 AI 的三個應用領域')

            # 步驟 2: 分析
            with logfire.span('analysis_step'):
                print("  → 分析階段")
                analysis = await analyzer.run(
                    f'分析這些領域：{research.data}'
                )

            # 步驟 3: 寫作
            with logfire.span('writing_step'):
                print("  → 寫作階段")
                report = await writer.run(
                    f'基於分析撰寫摘要：{analysis.data}'
                )

        print("\n✓ 工作流完成")
        print("  查看 Logfire 儀表板了解完整的執行追蹤")

    except ImportError:
        print("⚠️  Logfire 未安裝，使用標準輸出")

        researcher = Agent('openai:gpt-4')
        print("  → 執行研究...")
        result = await researcher.run('列出 AI 的三個應用領域')
        print(f"  ✓ 完成：{result.data[:50]}...")


# ============================================================================
# 主程式
# ============================================================================

async def main():
    """運行所有範例"""
    print("\n" + "📊 " + "="*58)
    print("Pydantic AI - Logfire 整合範例")
    print("="*60)

    example_1_basic_setup()
    await example_2_auto_tracking()
    await example_3_manual_logging()
    await example_4_performance_monitoring()
    await example_5_cost_tracking()
    await example_6_error_tracking()
    await example_7_custom_dashboard()
    await example_8_distributed_tracing()

    print("\n" + "="*60)
    print("✓ Logfire 整合範例完成！")
    print("💡 監控最佳實踐：")
    print("   1. 追蹤所有關鍵操作")
    print("   2. 監控成本和性能")
    print("   3. 記錄錯誤和異常")
    print("   4. 創建自定義儀表板")
    print("   5. 使用分布式追蹤")
    print("\n📚 Logfire 資源：")
    print("   - 官網：https://logfire.pydantic.dev")
    print("   - 文檔：https://docs.pydantic.dev/logfire")
    print("="*60)


if __name__ == '__main__':
    import os
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  請設置 OPENAI_API_KEY 環境變量")
    else:
        asyncio.run(main())
