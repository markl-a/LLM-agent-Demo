#!/usr/bin/env python3
"""
Semantic Kernel - 高級技巧與優化示例

本示例展示：
1. 批量處理
2. 緩存優化
3. 成本控制
4. 並發控制
5. 性能監控
"""

import asyncio
import os
import time
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

try:
    import semantic_kernel as sk
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
    from semantic_kernel.contents import ChatHistory
except ImportError:
    print("❌ 請安裝 Semantic Kernel:")
    print("   pip install semantic-kernel")
    exit(1)


async def example_batch_processing():
    """示例 1: 批量處理"""
    print("\n" + "=" * 60)
    print("示例 1: 批量處理")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    # 批量分類任務
    classify_prompt = """
    將以下文本分類為：正面、負面、中性

    文本：{{$text}}

    只返回分類：
    """

    classify_function = kernel.add_function(
        function_name="classify",
        plugin_name="BatchProcessing",
        prompt=classify_prompt,
        description="情感分類",
    )

    # 大量文本
    texts = [
        "這個產品太棒了！",
        "質量很差，不推薦。",
        "還可以，一般般。",
        "非常滿意，值得購買！",
        "浪費錢，不值得。",
        "符合預期。",
        "超出預期，驚喜！",
        "有點失望。",
    ]

    print(f"📊 批量處理 {len(texts)} 條文本\n")

    # 方法 1: 順序處理（慢）
    start_time = time.time()
    sequential_results = []

    for text in texts:
        result = await kernel.invoke(classify_function, text=text)
        sequential_results.append((text, str(result).strip()))

    sequential_time = time.time() - start_time
    print(f"⏱️  順序處理時間: {sequential_time:.2f}秒\n")

    # 方法 2: 並行處理（快）
    start_time = time.time()

    async def process_text(text: str):
        result = await kernel.invoke(classify_function, text=text)
        return (text, str(result).strip())

    parallel_results = await asyncio.gather(*[process_text(t) for t in texts])

    parallel_time = time.time() - start_time
    print(f"⚡ 並行處理時間: {parallel_time:.2f}秒")
    print(f"📈 速度提升: {sequential_time / parallel_time:.1f}倍\n")

    # 顯示結果
    print("📝 分類結果:")
    for text, classification in parallel_results[:3]:
        print(f"  - '{text}' → {classification}")
    print(f"  ... 共 {len(parallel_results)} 條")


async def example_caching():
    """示例 2: 緩存優化"""
    print("\n" + "=" * 60)
    print("示例 2: 緩存優化")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    # 簡單的內存緩存
    cache: Dict[str, str] = {}

    async def cached_query(kernel, question: str) -> str:
        """帶緩存的查詢"""
        # 檢查緩存
        if question in cache:
            print(f"  ✓ 緩存命中: {question}")
            return cache[question]

        # 調用 API
        print(f"  ⏳ API 調用: {question}")

        service = kernel.get_service("chat-gpt")
        chat_history = ChatHistory()
        chat_history.add_user_message(question)

        response = await service.get_chat_message_content(
            chat_history=chat_history, settings=None
        )

        # 存入緩存
        answer = response.content
        cache[question] = answer

        return answer

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    # 測試緩存
    questions = [
        "什麼是機器學習？",
        "什麼是深度學習？",
        "什麼是機器學習？",  # 重複問題
        "什麼是深度學習？",  # 重複問題
    ]

    print("🔍 測試緩存機制:\n")

    start_time = time.time()

    for q in questions:
        print(f"\n💬 問題: {q}")
        answer = await cached_query(kernel, q)
        print(f"📝 回答: {answer[:100]}...")

    total_time = time.time() - start_time

    print(f"\n⏱️  總時間: {total_time:.2f}秒")
    print(f"📊 緩存命中率: {(sum(1 for q in questions if q in cache[:len(questions)-2]) / len(questions)) * 100:.0f}%")


async def example_cost_control():
    """示例 3: 成本控制"""
    print("\n" + "=" * 60)
    print("示例 3: 成本控制")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    # 成本追蹤器
    class CostTracker:
        def __init__(self, max_cost: float = 1.0):
            self.total_cost = 0.0
            self.max_cost = max_cost
            self.requests = 0

        def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
            """估算成本（簡化版）"""
            # GPT-4o-mini 價格（估計）
            prompt_cost = (prompt_tokens / 1000) * 0.00015
            completion_cost = (completion_tokens / 1000) * 0.0006
            return prompt_cost + completion_cost

        def add_request(self, prompt_tokens: int, completion_tokens: int) -> bool:
            """添加請求，返回是否超出預算"""
            cost = self.estimate_cost(prompt_tokens, completion_tokens)
            self.total_cost += cost
            self.requests += 1

            return self.total_cost < self.max_cost

        def get_summary(self) -> str:
            return f"請求數: {self.requests}, 總成本: ${self.total_cost:.4f}, 預算: ${self.max_cost}"

    tracker = CostTracker(max_cost=0.10)  # 預算 $0.10

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    print("💰 成本控制測試\n")

    # 模擬請求
    for i in range(10):
        # 估算 token 數（簡化）
        prompt_tokens = 50
        completion_tokens = 100

        if tracker.add_request(prompt_tokens, completion_tokens):
            print(f"✅ 請求 {i+1}: 已處理 ({tracker.get_summary()})")
        else:
            print(f"❌ 請求 {i+1}: 超出預算！")
            break

    print(f"\n📊 最終統計: {tracker.get_summary()}")


async def example_concurrency_control():
    """示例 4: 並發控制"""
    print("\n" + "=" * 60)
    print("示例 4: 並發控制")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    # 信號量限制並發數
    MAX_CONCURRENT = 3
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    translate_prompt = """
    將以下文本翻譯成{{$lang}}：
    {{$text}}

    翻譯：
    """

    translate_function = kernel.add_function(
        function_name="translate",
        plugin_name="ConcurrencyControl",
        prompt=translate_prompt,
        description="翻譯",
    )

    async def controlled_translate(text: str, lang: str, task_id: int):
        """受控的翻譯任務"""
        async with semaphore:  # 限制並發數
            print(f"  🔄 任務 {task_id} 開始 (當前並發: {MAX_CONCURRENT - semaphore._value})")

            result = await kernel.invoke(
                translate_function,
                text=text,
                lang=lang,
            )

            print(f"  ✅ 任務 {task_id} 完成")
            return result

    # 創建多個任務
    tasks = [
        ("Hello", "中文", 1),
        ("World", "日文", 2),
        ("AI", "韓文", 3),
        ("Python", "法文", 4),
        ("Future", "德文", 5),
    ]

    print(f"🚦 並發控制: 最多 {MAX_CONCURRENT} 個並發請求\n")

    results = await asyncio.gather(
        *[controlled_translate(text, lang, i) for text, lang, i in tasks]
    )

    print(f"\n✅ 完成 {len(results)} 個任務")


async def example_performance_monitoring():
    """示例 5: 性能監控"""
    print("\n" + "=" * 60)
    print("示例 5: 性能監控")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        return

    # 性能監控器
    class PerformanceMonitor:
        def __init__(self):
            self.metrics = []

        async def track_execution(self, func, *args, **kwargs):
            """追蹤函數執行"""
            start_time = time.time()
            start_memory = 0  # 簡化，實際可以用 tracemalloc

            try:
                result = await func(*args, **kwargs)
                success = True
                error = None
            except Exception as e:
                result = None
                success = False
                error = str(e)

            elapsed_time = time.time() - start_time

            self.metrics.append({
                "function": func.__name__,
                "duration": elapsed_time,
                "success": success,
                "error": error,
            })

            return result

        def get_report(self) -> str:
            """生成報告"""
            if not self.metrics:
                return "無數據"

            total_requests = len(self.metrics)
            successful = sum(1 for m in self.metrics if m["success"])
            failed = total_requests - successful
            avg_duration = sum(m["duration"] for m in self.metrics) / total_requests

            report = f"""
📊 性能報告
-----------
總請求數: {total_requests}
成功: {successful} ({successful/total_requests*100:.1f}%)
失敗: {failed} ({failed/total_requests*100:.1f}%)
平均響應時間: {avg_duration:.2f}秒
最快: {min(m['duration'] for m in self.metrics):.2f}秒
最慢: {max(m['duration'] for m in self.metrics):.2f}秒
"""
            return report

    monitor = PerformanceMonitor()

    kernel = sk.Kernel()
    service = OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id="gpt-4o-mini",
        api_key=api_key,
    )
    kernel.add_service(service)

    async def simple_query(question: str):
        """簡單查詢"""
        chat_history = ChatHistory()
        chat_history.add_user_message(question)

        response = await service.get_chat_message_content(
            chat_history=chat_history, settings=None
        )
        return response.content

    # 執行監控
    print("🔍 執行性能監控...\n")

    questions = [
        "什麼是 AI？",
        "Python 是什麼？",
        "什麼是雲計算？",
        "解釋區塊鏈",
        "什麼是物聯網？",
    ]

    for q in questions:
        print(f"💬 問題: {q}")
        result = await monitor.track_execution(simple_query, q)
        if result:
            print(f"✅ 回答: {result[:50]}...\n")

    # 生成報告
    print(monitor.get_report())


async def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🚀 Semantic Kernel - 高級技巧與優化示例")
    print("=" * 60)

    try:
        await example_batch_processing()
        await example_caching()
        await example_cost_control()
        await example_concurrency_control()
        await example_performance_monitoring()

    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ 所有示例運行完成")
    print("✨ Semantic Kernel 20 個完整示例已創建！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
