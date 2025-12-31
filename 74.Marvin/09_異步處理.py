"""
Marvin 異步處理示例

本示例展示：
1. 異步 AI 函數
2. 並發處理
3. 流式響應
4. 批量處理
5. 性能優化

運行方式：
    python 09_異步處理.py
"""

import os
import asyncio
import marvin
from typing import List
from pydantic import BaseModel
import time


# ==================== 異步 AI 函數 ====================

@marvin.fn
async def async_translate(text: str, target_lang: str) -> str:
    """異步翻譯函數"""


@marvin.fn
async def async_summarize(text: str) -> str:
    """異步摘要函數"""


@marvin.fn
async def async_classify(text: str, labels: List[str]) -> str:
    """異步分類函數"""


async def example_async_functions():
    """示例 1: 異步 AI 函數"""
    print("\n" + "="*60)
    print("示例 1: 異步 AI 函數")
    print("="*60)

    try:
        print("異步函數使用示例:\n")

        # 單個異步調用
        result = await async_translate("Hello World", "中文")
        print(f"✅ 翻譯結果: {result}")

        # 多個異步調用
        text = "這是一段需要處理的文本。包含多個句子和想法。"

        summary_task = async_summarize(text)
        classify_task = async_classify(text, ["技術", "生活", "其他"])

        summary, category = await asyncio.gather(
            summary_task,
            classify_task
        )

        print(f"✅ 摘要: {summary}")
        print(f"✅ 分類: {category}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 並發處理 ====================

async def example_concurrent_processing():
    """示例 2: 並發處理多個任務"""
    print("\n" + "="*60)
    print("示例 2: 並發處理")
    print("="*60)

    try:
        print("並發處理示例:\n")

        # 待處理的文本列表
        texts = [
            "人工智能正在改變世界",
            "Machine learning is powerful",
            "深度學習需要大量數據",
            "Natural language processing",
            "計算機視覺應用廣泛"
        ]

        # 同步處理（較慢）
        print("同步處理:")
        sync_start = time.time()
        sync_results = []
        for text in texts:
            result = await async_translate(text, "英文")
            sync_results.append(result)
        sync_time = time.time() - sync_start

        print(f"  完成時間: {sync_time:.2f} 秒")
        print(f"  處理了 {len(sync_results)} 條文本\n")

        # 並發處理（更快）
        print("並發處理:")
        async_start = time.time()
        tasks = [async_translate(text, "英文") for text in texts]
        async_results = await asyncio.gather(*tasks)
        async_time = time.time() - async_start

        print(f"  完成時間: {async_time:.2f} 秒")
        print(f"  處理了 {len(async_results)} 條文本")
        print(f"  ⚡ 速度提升: {sync_time/async_time:.2f}x\n")

        # 顯示結果
        print("處理結果:")
        for i, (orig, trans) in enumerate(zip(texts, async_results), 1):
            print(f"  {i}. {orig[:30]:<30} → {trans[:30]}")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 批量處理 ====================

class Article(BaseModel):
    """文章信息"""
    title: str
    summary: str
    category: str
    keywords: List[str]


@marvin.fn
async def analyze_article(text: str) -> Article:
    """異步分析文章"""


async def example_batch_processing():
    """示例 3: 批量處理"""
    print("\n" + "="*60)
    print("示例 3: 批量處理")
    print("="*60)

    try:
        print("批量處理文章:\n")

        articles = [
            "文章1: AI技術的最新發展...",
            "文章2: 量子計算的應用前景...",
            "文章3: 機器學習實戰指南...",
            "文章4: 深度學習模型優化...",
            "文章5: 自然語言處理進展..."
        ]

        # 批量分析
        start_time = time.time()
        tasks = [analyze_article(article) for article in articles]
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start_time

        print(f"✅ 處理了 {len(results)} 篇文章")
        print(f"⏱️  用時: {elapsed:.2f} 秒")
        print(f"📊 平均: {elapsed/len(results):.2f} 秒/篇\n")

        # 顯示結果
        print("分析結果:")
        for i, article in enumerate(results, 1):
            print(f"\n  {i}. {article.title}")
            print(f"     分類: {article.category}")
            print(f"     關鍵詞: {', '.join(article.keywords[:3])}")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 流式響應 ====================

async def example_streaming():
    """示例 4: 流式響應"""
    print("\n" + "="*60)
    print("示例 4: 流式響應")
    print("="*60)

    try:
        print("流式響應示例:\n")

        print("示例代碼（概念演示）:")
        print("""
        @marvin.fn(stream=True)
        async def streaming_generate(prompt: str) -> str:
            '''生成長文本，支持流式輸出'''

        # 流式處理
        async for chunk in streaming_generate("寫一個故事"):
            print(chunk, end='', flush=True)
        print()

        # 或者累積結果
        result = []
        async for chunk in streaming_generate("生成文章"):
            result.append(chunk)
            # 可以實時顯示進度
            print(f"已生成: {len(''.join(result))} 字符", end='\\r')

        final_text = ''.join(result)
        print(f"\\n最終文本: {final_text}")
        """)

        print("\n流式響應優勢:")
        print("  ⚡ 更快的首字響應")
        print("  👁️ 實時進度展示")
        print("  💰 可以提前終止，節省成本")
        print("  🎯 更好的用戶體驗\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 錯誤處理 ====================

async def example_error_handling():
    """示例 5: 異步錯誤處理"""
    print("\n" + "="*60)
    print("示例 5: 異步錯誤處理")
    print("="*60)

    try:
        print("異步錯誤處理示例:\n")

        @marvin.fn
        async def risky_function(text: str) -> str:
            """可能失敗的函數"""
            if not text:
                raise ValueError("文本不能為空")
            return "處理結果"

        # 單個任務錯誤處理
        try:
            result = await risky_function("")
        except ValueError as e:
            print(f"⚠️ 捕獲錯誤: {e}")

        # 批量任務錯誤處理
        texts = ["正常文本", "", "另一個文本", None]

        results = []
        for text in texts:
            try:
                result = await risky_function(text or "")
                results.append({"status": "success", "result": result})
            except Exception as e:
                results.append({"status": "error", "error": str(e)})

        print("\n批量處理結果:")
        for i, result in enumerate(results, 1):
            status = "✅" if result["status"] == "success" else "❌"
            print(f"  {status} 任務 {i}: {result.get('result', result.get('error'))}")

        # 使用 gather 的 return_exceptions
        print("\n使用 return_exceptions:")
        tasks = [risky_function(text or "") for text in texts]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                print(f"  ❌ 任務 {i}: {result}")
            else:
                print(f"  ✅ 任務 {i}: {result}")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 超時控制 ====================

async def example_timeout():
    """示例 6: 超時控制"""
    print("\n" + "="*60)
    print("示例 6: 超時控制")
    print("="*60)

    try:
        print("超時控制示例:\n")

        @marvin.fn
        async def slow_task(text: str) -> str:
            """可能很慢的任務"""
            return "結果"

        # 設置超時
        try:
            result = await asyncio.wait_for(
                slow_task("處理文本"),
                timeout=5.0  # 5 秒超時
            )
            print(f"✅ 完成: {result}")
        except asyncio.TimeoutError:
            print("⏰ 任務超時")

        # 批量任務的超時控制
        tasks = [slow_task(f"文本{i}") for i in range(3)]

        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks),
                timeout=10.0
            )
            print(f"\n✅ 批量完成: {len(results)} 個任務")
        except asyncio.TimeoutError:
            print("\n⏰ 批量任務超時")

        print("\n超時策略:")
        print("  ⏱️ 為每個任務設置合理超時")
        print("  🔄 超時後重試")
        print("  💾 保存部分結果")
        print("  📊 監控任務執行時間")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 性能優化 ====================

async def example_performance():
    """示例 7: 性能優化"""
    print("\n" + "="*60)
    print("示例 7: 性能優化")
    print("="*60)

    try:
        print("異步性能優化技巧:\n")

        print("1. 控制並發數量:")
        print("""
        # 使用信號量限制並發
        semaphore = asyncio.Semaphore(5)  # 最多5個並發

        async def limited_task(text: str):
            async with semaphore:
                return await async_translate(text, "英文")

        tasks = [limited_task(text) for text in texts]
        results = await asyncio.gather(*tasks)
        """)

        print("\n2. 使用任務隊列:")
        print("""
        async def worker(queue, results):
            while True:
                text = await queue.get()
                if text is None:
                    break
                result = await async_translate(text, "英文")
                results.append(result)
                queue.task_done()

        queue = asyncio.Queue()
        workers = [worker(queue, results) for _ in range(5)]

        for text in texts:
            await queue.put(text)

        await queue.join()
        """)

        print("\n3. 緩存結果:")
        print("""
        from functools import lru_cache

        @lru_cache(maxsize=100)
        @marvin.fn
        async def cached_translate(text: str, lang: str) -> str:
            '''帶緩存的翻譯'''
        """)

        print("\n優化建議:")
        print("  🎯 限制並發數量（避免過載）")
        print("  📦 批量處理相似任務")
        print("  💾 緩存常見結果")
        print("  ⚡ 使用連接池")
        print("  📊 監控和調優")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 主函數 ====================

async def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║        Marvin 異步處理示例                ║
╚══════════════════════════════════════════╝

異步特性:
✅ 並發處理
✅ 流式響應
✅ 批量操作
✅ 錯誤處理
✅ 超時控制
✅ 性能優化
    """)

    # 檢查環境
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 請設置 OPENAI_API_KEY 環境變量")
        return

    # 配置 Marvin
    marvin.settings.openai.api_key = os.getenv("OPENAI_API_KEY")

    # 運行示例
    await example_async_functions()
    await example_concurrent_processing()
    await example_batch_processing()
    await example_streaming()
    await example_error_handling()
    await example_timeout()
    await example_performance()

    print("\n" + "="*60)
    print("✅ 所有示例運行完成！")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
