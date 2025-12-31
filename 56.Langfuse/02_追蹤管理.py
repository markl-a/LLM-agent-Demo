"""
Langfuse 追蹤管理示例

這個示例深入展示 Langfuse 的追蹤和 Span 管理功能，包括：
- 層級追蹤結構
- Span 的創建和管理
- 複雜的追蹤關係
- 追蹤鏈路分析
- 性能監控
- 分布式追蹤

主要內容：
1. Trace 的高級用法
2. Span 的層級管理
3. 追蹤關聯和分組
4. 自定義屬性和標籤
5. 追蹤查詢和過濾
6. 性能分析
7. 分布式系統追蹤

作者: Langfuse Team
日期: 2025-01-01
"""

import os
import time
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from langfuse import Langfuse
from openai import OpenAI
import random


# ============================================================================
# 第一部分：層級追蹤結構
# ============================================================================

class TraceManager:
    """
    追蹤管理器

    提供完整的追蹤管理功能，包括創建、更新、查詢等操作。
    """

    def __init__(self, langfuse: Langfuse):
        """
        初始化追蹤管理器

        Args:
            langfuse: Langfuse 客戶端實例
        """
        self.langfuse = langfuse
        self.active_traces = {}

    def hierarchical_trace_example(self):
        """
        層級追蹤示例

        展示如何創建複雜的層級追蹤結構，模擬一個完整的
        AI 應用處理流程。
        """
        print("\n" + "="*60)
        print("層級追蹤結構示例")
        print("="*60)

        # 創建根追蹤
        root_trace = self.langfuse.trace(
            name="complex-ai-pipeline",
            user_id="user-pipeline-001",
            session_id=f"session-{uuid.uuid4()}",
            metadata={
                "pipeline_type": "full-stack-ai",
                "version": "2.0",
                "environment": "production"
            },
            tags=["pipeline", "production", "complex"]
        )

        print(f"🌳 創建根追蹤: {root_trace.id}")

        # 第一層：輸入處理
        input_span = root_trace.span(
            name="input-processing",
            input={"raw_query": "分析這段文本的情感"},
            metadata={"layer": "input"}
        )
        print("  📥 第 1 層: 輸入處理")

        # 第二層：數據驗證
        validation_span = root_trace.span(
            name="input-validation",
            parent_observation_id=input_span.id,
            input={"query": "分析這段文本的情感"},
            metadata={"layer": "validation"}
        )
        time.sleep(0.1)
        validation_span.end(
            output={"valid": True, "sanitized": True},
            metadata={"validation_time": 0.1}
        )
        print("    ✓ 第 2 層: 數據驗證完成")

        # 第二層：查詢增強
        enhancement_span = root_trace.span(
            name="query-enhancement",
            parent_observation_id=input_span.id,
            input={"original_query": "分析這段文本的情感"},
            metadata={"layer": "enhancement"}
        )
        time.sleep(0.15)
        enhancement_span.end(
            output={"enhanced_query": "請分析以下文本的情感傾向（正面/負面/中性）"},
            metadata={"enhancement_time": 0.15}
        )
        print("    ✓ 第 2 層: 查詢增強完成")

        # 完成輸入處理層
        input_span.end(
            output={"processed": True},
            metadata={"total_time": 0.25}
        )

        # 第一層：模型推理
        inference_span = root_trace.span(
            name="model-inference",
            metadata={"layer": "inference"}
        )
        print("  🤖 第 1 層: 模型推理")

        # 第二層：模型選擇
        selection_span = root_trace.span(
            name="model-selection",
            parent_observation_id=inference_span.id,
            metadata={"layer": "selection"}
        )
        time.sleep(0.05)
        selected_model = "gpt-4"
        selection_span.end(
            output={"selected_model": selected_model},
            metadata={"selection_strategy": "cost-optimized"}
        )
        print(f"    ✓ 第 2 層: 選擇模型 {selected_model}")

        # 第二層：提示構建
        prompt_span = root_trace.span(
            name="prompt-construction",
            parent_observation_id=inference_span.id,
            metadata={"layer": "prompt"}
        )
        time.sleep(0.08)
        prompt_span.end(
            output={"prompt_tokens": 150},
            metadata={"template": "sentiment-analysis-v2"}
        )
        print("    ✓ 第 2 層: 提示構建完成")

        # 第二層：實際 LLM 調用
        llm_generation = root_trace.generation(
            name="llm-call",
            parent_observation_id=inference_span.id,
            model=selected_model,
            input=[{"role": "user", "content": "請分析以下文本的情感傾向"}],
            metadata={"layer": "generation"}
        )
        time.sleep(0.5)
        llm_generation.end(
            output="這段文本呈現正面情感",
            usage={
                "prompt_tokens": 150,
                "completion_tokens": 50,
                "total_tokens": 200
            },
            metadata={"latency": 500}
        )
        print("    ✓ 第 2 層: LLM 調用完成")

        # 完成推理層
        inference_span.end(
            output={"result": "這段文本呈現正面情感"},
            metadata={"total_inference_time": 0.63}
        )

        # 第一層：後處理
        postprocess_span = root_trace.span(
            name="output-postprocessing",
            input={"raw_output": "這段文本呈現正面情感"},
            metadata={"layer": "postprocessing"}
        )
        print("  📤 第 1 層: 輸出後處理")

        # 第二層：格式化
        format_span = root_trace.span(
            name="output-formatting",
            parent_observation_id=postprocess_span.id,
            metadata={"layer": "formatting"}
        )
        time.sleep(0.05)
        format_span.end(
            output={
                "sentiment": "positive",
                "confidence": 0.92,
                "text": "這段文本呈現正面情感"
            }
        )
        print("    ✓ 第 2 層: 輸出格式化完成")

        # 第二層：質量檢查
        quality_span = root_trace.span(
            name="quality-check",
            parent_observation_id=postprocess_span.id,
            metadata={"layer": "quality"}
        )
        time.sleep(0.03)
        quality_span.end(
            output={"passed": True, "score": 0.95}
        )
        print("    ✓ 第 2 層: 質量檢查完成")

        # 完成後處理層
        postprocess_span.end(
            output={
                "final_result": {
                    "sentiment": "positive",
                    "confidence": 0.92
                }
            }
        )

        # 完成根追蹤
        root_trace.update(
            output={
                "sentiment": "positive",
                "confidence": 0.92,
                "processing_time": 0.91
            },
            metadata={
                "total_spans": 9,
                "success": True
            }
        )

        print(f"✅ 層級追蹤完成，共 9 個 Span")

        return root_trace


# ============================================================================
# 第二部分：Span 管理
# ============================================================================

class SpanManager:
    """
    Span 管理器

    提供 Span 的創建、更新、嵌套等功能。
    """

    def __init__(self, langfuse: Langfuse):
        self.langfuse = langfuse

    def span_lifecycle_example(self):
        """
        Span 生命週期示例

        展示 Span 從創建到結束的完整生命週期。
        """
        print("\n" + "="*60)
        print("Span 生命週期示例")
        print("="*60)

        trace = self.langfuse.trace(
            name="span-lifecycle-demo",
            metadata={"demo_type": "span_management"}
        )

        # 創建 Span
        span = trace.span(
            name="data-processing",
            input={"data": "raw input"},
            metadata={
                "status": "initializing",
                "priority": "high"
            }
        )

        print(f"📍 Span 創建: {span.id}")
        print(f"   名稱: data-processing")
        print(f"   狀態: initializing")

        # 模擬處理的不同階段
        stages = [
            ("loading", 0.2),
            ("validating", 0.15),
            ("transforming", 0.3),
            ("saving", 0.1)
        ]

        for stage, duration in stages:
            print(f"   ⏳ {stage}...")

            # 更新 Span 的元數據
            span.update(
                metadata={
                    "status": stage,
                    "current_stage": stage
                }
            )

            time.sleep(duration)

        # 結束 Span
        span.end(
            output={"data": "processed output", "records": 1000},
            metadata={
                "status": "completed",
                "total_duration": sum(d for _, d in stages),
                "stages_completed": len(stages)
            }
        )

        print(f"✅ Span 完成")

        return trace

    def nested_spans_example(self):
        """
        嵌套 Span 示例

        展示如何創建深度嵌套的 Span 結構。
        """
        print("\n" + "="*60)
        print("嵌套 Span 示例")
        print("="*60)

        trace = self.langfuse.trace(
            name="nested-operations",
            metadata={"pattern": "nested"}
        )

        def recursive_operation(parent_trace, depth: int, max_depth: int):
            """遞歸創建嵌套 Span"""
            if depth > max_depth:
                return

            span = parent_trace.span(
                name=f"operation-level-{depth}",
                input={"depth": depth},
                metadata={"level": depth}
            )

            print("  " * depth + f"📊 Level {depth}")

            time.sleep(0.1)

            # 遞歸調用
            if depth < max_depth:
                recursive_operation(parent_trace, depth + 1, max_depth)

            span.end(
                output={"completed": True},
                metadata={"depth": depth}
            )

        # 創建 5 層深的嵌套結構
        recursive_operation(trace, 1, 5)

        print(f"✅ 嵌套 Span 完成（5 層深）")

        return trace

    def parallel_spans_example(self):
        """
        並行 Span 示例

        展示如何追蹤並行執行的操作。
        """
        print("\n" + "="*60)
        print("並行 Span 示例")
        print("="*60)

        trace = self.langfuse.trace(
            name="parallel-processing",
            metadata={"pattern": "parallel"}
        )

        # 模擬並行處理多個任務
        tasks = ["task-A", "task-B", "task-C", "task-D"]
        spans = []

        print("🚀 啟動並行任務:")

        # 創建所有 Span
        for task_name in tasks:
            span = trace.span(
                name=task_name,
                input={"task": task_name},
                metadata={
                    "type": "parallel",
                    "started_at": datetime.now().isoformat()
                }
            )
            spans.append((task_name, span))
            print(f"   • {task_name} 啟動")

        # 模擬任務完成（不同的耗時）
        durations = [0.3, 0.5, 0.2, 0.4]
        for (task_name, span), duration in zip(spans, durations):
            time.sleep(duration)
            span.end(
                output={"result": f"{task_name} completed"},
                metadata={
                    "duration": duration,
                    "completed_at": datetime.now().isoformat()
                }
            )
            print(f"   ✓ {task_name} 完成 ({duration}s)")

        trace.update(
            metadata={
                "total_tasks": len(tasks),
                "pattern": "fan-out-fan-in"
            }
        )

        print(f"✅ 所有並行任務完成")

        return trace


# ============================================================================
# 第三部分：追蹤關聯和分組
# ============================================================================

class TraceGrouping:
    """
    追蹤分組管理

    提供追蹤的關聯、分組和組織功能。
    """

    def __init__(self, langfuse: Langfuse):
        self.langfuse = langfuse

    def user_session_grouping(self):
        """
        用戶會話分組示例

        展示如何將相關的追蹤組織到用戶會話中。
        """
        print("\n" + "="*60)
        print("用戶會話分組示例")
        print("="*60)

        user_id = "user-session-demo"
        session_id = f"session-{uuid.uuid4()}"

        print(f"👤 用戶: {user_id}")
        print(f"🔗 會話: {session_id}")

        # 模擬用戶的多個操作
        operations = [
            ("search-products", {"query": "筆記本電腦"}),
            ("view-product", {"product_id": "laptop-001"}),
            ("add-to-cart", {"product_id": "laptop-001", "quantity": 1}),
            ("checkout", {"cart_total": 35000}),
            ("payment", {"amount": 35000, "method": "credit_card"})
        ]

        for idx, (operation, data) in enumerate(operations, 1):
            trace = self.langfuse.trace(
                name=operation,
                user_id=user_id,
                session_id=session_id,
                input=data,
                metadata={
                    "sequence": idx,
                    "timestamp": datetime.now().isoformat()
                },
                tags=["e-commerce", operation.split("-")[0]]
            )

            time.sleep(0.1)

            trace.update(
                output={"success": True},
                metadata={"duration": 0.1}
            )

            print(f"  {idx}. {operation} ✓")

        print(f"\n✅ 會話完成，共 {len(operations)} 個操作")

        return session_id

    def feature_based_grouping(self):
        """
        功能導向分組示例

        展示如何按功能模塊組織追蹤。
        """
        print("\n" + "="*60)
        print("功能導向分組示例")
        print("="*60)

        features = {
            "authentication": [
                "login",
                "verify-token",
                "refresh-token"
            ],
            "data-processing": [
                "ingest-data",
                "transform-data",
                "export-data"
            ],
            "ai-inference": [
                "preprocess",
                "model-predict",
                "postprocess"
            ]
        }

        for feature, operations in features.items():
            print(f"\n📦 功能模塊: {feature}")

            for operation in operations:
                trace = self.langfuse.trace(
                    name=f"{feature}/{operation}",
                    metadata={
                        "feature": feature,
                        "operation": operation,
                        "module": feature.split("-")[0]
                    },
                    tags=[feature, operation]
                )

                time.sleep(0.05)

                trace.update(
                    output={"status": "completed"}
                )

                print(f"  • {operation} ✓")

        print(f"\n✅ 所有功能模塊追蹤完成")


# ============================================================================
# 第四部分：自定義屬性和標籤
# ============================================================================

class CustomAttributes:
    """
    自定義屬性管理

    展示如何使用自定義屬性和標籤來增強追蹤。
    """

    def __init__(self, langfuse: Langfuse):
        self.langfuse = langfuse

    def rich_metadata_example(self):
        """
        豐富的元數據示例

        展示如何添加詳細的元數據來提供上下文信息。
        """
        print("\n" + "="*60)
        print("豐富元數據示例")
        print("="*60)

        trace = self.langfuse.trace(
            name="api-request",
            user_id="user-metadata-demo",
            metadata={
                # 請求信息
                "request": {
                    "method": "POST",
                    "path": "/api/v1/chat",
                    "headers": {
                        "content-type": "application/json",
                        "user-agent": "Mozilla/5.0"
                    },
                    "ip_address": "192.168.1.100"
                },
                # 用戶信息
                "user": {
                    "id": "user-123",
                    "tier": "premium",
                    "region": "asia-east",
                    "language": "zh-TW"
                },
                # 系統信息
                "system": {
                    "service": "chat-api",
                    "version": "2.1.0",
                    "environment": "production",
                    "datacenter": "taipei-1",
                    "instance_id": "i-0abc123"
                },
                # 業務信息
                "business": {
                    "feature": "ai-chat",
                    "campaign": "summer-2025",
                    "ab_test_group": "variant-B"
                },
                # 技術信息
                "technical": {
                    "cache_hit": False,
                    "database_queries": 3,
                    "external_api_calls": 1
                }
            },
            tags=[
                "api",
                "production",
                "premium-user",
                "ai-chat",
                "variant-B"
            ]
        )

        print("📋 元數據已設置:")
        print("   • 請求信息: ✓")
        print("   • 用戶信息: ✓")
        print("   • 系統信息: ✓")
        print("   • 業務信息: ✓")
        print("   • 技術信息: ✓")
        print(f"   • 標籤: {len(trace.tags)} 個")

        # 處理過程中動態更新元數據
        time.sleep(0.2)

        trace.update(
            output={"response": "處理完成"},
            metadata={
                "performance": {
                    "total_duration_ms": 200,
                    "db_duration_ms": 50,
                    "llm_duration_ms": 120,
                    "other_duration_ms": 30
                },
                "resources": {
                    "cpu_usage_percent": 45.2,
                    "memory_usage_mb": 256,
                    "network_kb": 15
                }
            }
        )

        print("\n📊 性能和資源數據已添加")
        print("✅ 豐富元數據追蹤完成")

        return trace

    def dynamic_tagging_example(self):
        """
        動態標籤示例

        展示如何基於運行時條件動態添加標籤。
        """
        print("\n" + "="*60)
        print("動態標籤示例")
        print("="*60)

        # 模擬處理請求
        request_data = {
            "response_time": random.uniform(0.1, 2.0),
            "error_occurred": random.choice([True, False]),
            "cache_hit": random.choice([True, False]),
            "user_tier": random.choice(["free", "premium", "enterprise"])
        }

        # 基礎標籤
        tags = ["api-request"]

        # 根據響應時間添加標籤
        if request_data["response_time"] < 0.5:
            tags.append("fast")
        elif request_data["response_time"] < 1.0:
            tags.append("normal")
        else:
            tags.append("slow")

        # 根據狀態添加標籤
        if request_data["error_occurred"]:
            tags.append("error")
        else:
            tags.append("success")

        # 根據緩存添加標籤
        if request_data["cache_hit"]:
            tags.append("cache-hit")
        else:
            tags.append("cache-miss")

        # 根據用戶層級添加標籤
        tags.append(f"tier-{request_data['user_tier']}")

        # 創建追蹤
        trace = self.langfuse.trace(
            name="dynamic-tagging-demo",
            metadata=request_data,
            tags=tags
        )

        print(f"🏷️  動態標籤: {tags}")
        print(f"   響應時間: {request_data['response_time']:.2f}s")
        print(f"   錯誤: {'是' if request_data['error_occurred'] else '否'}")
        print(f"   緩存命中: {'是' if request_data['cache_hit'] else '否'}")
        print(f"   用戶層級: {request_data['user_tier']}")

        print("✅ 動態標籤追蹤完成")

        return trace


# ============================================================================
# 第五部分：追蹤查詢和過濾（模擬）
# ============================================================================

class TraceAnalytics:
    """
    追蹤分析

    提供追蹤的分析和統計功能（模擬）。
    """

    def __init__(self, langfuse: Langfuse):
        self.langfuse = langfuse
        self.traces = []

    def generate_sample_traces(self, count: int = 20):
        """
        生成樣本追蹤數據

        Args:
            count: 要生成的追蹤數量
        """
        print(f"\n📊 生成 {count} 個樣本追蹤...")

        for i in range(count):
            trace = self.langfuse.trace(
                name=random.choice([
                    "chat-completion",
                    "text-generation",
                    "image-analysis",
                    "data-processing"
                ]),
                user_id=f"user-{random.randint(1, 10)}",
                metadata={
                    "duration": random.uniform(0.1, 3.0),
                    "tokens": random.randint(50, 1000),
                    "cost": random.uniform(0.001, 0.1),
                    "success": random.choice([True, True, True, False])
                },
                tags=random.sample(
                    ["production", "staging", "test", "urgent", "batch"],
                    k=random.randint(1, 3)
                )
            )

            self.traces.append(trace)

        print(f"✅ 生成完成")

    def analyze_traces(self):
        """
        分析追蹤數據（模擬）
        """
        print("\n" + "="*60)
        print("追蹤分析示例（模擬）")
        print("="*60)

        print("📈 分析結果:")
        print(f"   總追蹤數: {len(self.traces)}")
        print(f"   獨立用戶: ~10")
        print(f"   平均耗時: ~1.5s")
        print(f"   成功率: ~75%")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """
    主函數：運行所有追蹤管理示例
    """
    print("\n" + "="*70)
    print("Langfuse 追蹤管理示例")
    print("="*70)

    # 初始化 Langfuse
    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY", "pk-demo"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY", "sk-demo"),
        debug=True
    )

    try:
        # 1. 層級追蹤結構
        trace_manager = TraceManager(langfuse)
        trace_manager.hierarchical_trace_example()

        # 2. Span 管理
        span_manager = SpanManager(langfuse)
        span_manager.span_lifecycle_example()
        span_manager.nested_spans_example()
        span_manager.parallel_spans_example()

        # 3. 追蹤分組
        trace_grouping = TraceGrouping(langfuse)
        trace_grouping.user_session_grouping()
        trace_grouping.feature_based_grouping()

        # 4. 自定義屬性
        custom_attrs = CustomAttributes(langfuse)
        custom_attrs.rich_metadata_example()
        custom_attrs.dynamic_tagging_example()

        # 5. 追蹤分析
        analytics = TraceAnalytics(langfuse)
        analytics.generate_sample_traces(20)
        analytics.analyze_traces()

        print("\n" + "="*70)
        print("✅ 所有追蹤管理示例運行完成！")
        print("="*70)

        # 刷新數據
        langfuse.flush()

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
