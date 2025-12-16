"""
DSPy 進階技巧範例
================

本範例展示 DSPy 的進階使用技巧。

進階技巧：
1. 自定義 Signature
2. 複雜推理鏈
3. 錯誤處理
4. 性能優化
5. 調試技巧

安裝依賴：
pip install dspy-ai
"""

import dspy
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import json
import time
from functools import wraps

# ============================================================
# 配置
# ============================================================

turbo = dspy.OpenAI(model='gpt-3.5-turbo')
dspy.settings.configure(lm=turbo)


# ============================================================
# 1. 高級 Signature 定義
# ============================================================

class StructuredOutputSignature(dspy.Signature):
    """結構化輸出簽名"""
    query = dspy.InputField(desc="用戶查詢")
    context = dspy.InputField(desc="背景信息", optional=True)

    thought_process = dspy.OutputField(desc="思考過程")
    confidence = dspy.OutputField(desc="置信度 (0-1)")
    answer = dspy.OutputField(desc="最終答案")
    sources = dspy.OutputField(desc="信息來源列表")


class MultiStepSignature(dspy.Signature):
    """多步驟推理簽名"""
    problem = dspy.InputField(desc="需要解決的問題")
    constraints = dspy.InputField(desc="約束條件", optional=True)

    step1_analysis = dspy.OutputField(desc="第一步：問題分析")
    step2_approach = dspy.OutputField(desc="第二步：解決方案")
    step3_execution = dspy.OutputField(desc="第三步：執行細節")
    final_answer = dspy.OutputField(desc="最終答案")


class TypedSignature(dspy.Signature):
    """帶類型提示的簽名"""
    numbers = dspy.InputField(desc="數字列表，如 [1, 2, 3]")
    operation = dspy.InputField(desc="操作: sum, avg, max, min")

    result = dspy.OutputField(desc="計算結果 (數字)")
    explanation = dspy.OutputField(desc="計算說明")


# ============================================================
# 2. 高級 Module 模式
# ============================================================

class SelfRefiningModule(dspy.Module):
    """自我改進模組"""

    def __init__(self, max_refinements: int = 3):
        super().__init__()
        self.max_refinements = max_refinements
        self.initial_answer = dspy.ChainOfThought("question -> answer")
        self.critic = dspy.Predict("question, answer -> critique, score")
        self.refiner = dspy.ChainOfThought("question, answer, critique -> refined_answer")

    def forward(self, question: str):
        # 初始回答
        current = self.initial_answer(question=question)
        answer = current.answer

        for i in range(self.max_refinements):
            # 批評
            critique = self.critic(question=question, answer=answer)

            # 檢查分數
            try:
                score = float(critique.score)
                if score >= 0.9:
                    break
            except (ValueError, AttributeError):
                pass

            # 改進
            refined = self.refiner(
                question=question,
                answer=answer,
                critique=critique.critique
            )
            answer = refined.refined_answer

        return dspy.Prediction(answer=answer, refinements=i + 1)


class EnsembleModule(dspy.Module):
    """集成模組"""

    def __init__(self, num_samples: int = 3):
        super().__init__()
        self.num_samples = num_samples
        self.predictor = dspy.Predict("question -> answer")
        self.aggregator = dspy.Predict("answers -> best_answer")

    def forward(self, question: str):
        # 多次採樣
        answers = []
        for _ in range(self.num_samples):
            result = self.predictor(question=question)
            answers.append(result.answer)

        # 聚合
        answers_str = "\n".join([f"{i+1}. {a}" for i, a in enumerate(answers)])
        final = self.aggregator(answers=answers_str)

        return dspy.Prediction(
            answer=final.best_answer,
            candidates=answers
        )


class HierarchicalModule(dspy.Module):
    """層次化模組"""

    def __init__(self):
        super().__init__()
        self.decompose = dspy.ChainOfThought("complex_task -> subtasks")
        self.solve_subtask = dspy.ChainOfThought("subtask -> solution")
        self.synthesize = dspy.ChainOfThought("subtasks, solutions -> final_answer")

    def forward(self, complex_task: str):
        # 分解任務
        decomposed = self.decompose(complex_task=complex_task)
        subtasks = decomposed.subtasks.split('\n')

        # 解決子任務
        solutions = []
        for subtask in subtasks:
            if subtask.strip():
                solution = self.solve_subtask(subtask=subtask)
                solutions.append(solution.solution)

        # 綜合答案
        subtasks_str = "\n".join(subtasks)
        solutions_str = "\n".join(solutions)
        final = self.synthesize(subtasks=subtasks_str, solutions=solutions_str)

        return dspy.Prediction(
            answer=final.final_answer,
            subtasks=subtasks,
            solutions=solutions
        )


# ============================================================
# 3. 錯誤處理
# ============================================================

class DSPyError(Exception):
    """DSPy 基礎錯誤"""
    pass


class RetryError(DSPyError):
    """重試錯誤"""
    pass


class ValidationError(DSPyError):
    """驗證錯誤"""
    pass


def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    """重試裝飾器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    print(f"嘗試 {attempt + 1} 失敗: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(delay * (attempt + 1))
            raise RetryError(f"重試 {max_retries} 次後仍失敗: {last_error}")
        return wrapper
    return decorator


class RobustModule(dspy.Module):
    """健壯的模組（帶錯誤處理）"""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict("question -> answer")
        self.fallback_answer = "抱歉，無法處理您的問題"

    @retry_on_error(max_retries=3)
    def _predict(self, question: str):
        return self.predictor(question=question)

    def forward(self, question: str):
        try:
            result = self._predict(question)
            return result
        except RetryError:
            return dspy.Prediction(answer=self.fallback_answer, error=True)


# ============================================================
# 4. 性能優化
# ============================================================

class CacheManager:
    """緩存管理器"""

    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None

    def set(self, key: str, value: Any):
        if len(self.cache) >= self.max_size:
            # 簡單的 FIFO 清理
            oldest = next(iter(self.cache))
            del self.cache[oldest]
        self.cache[key] = value

    def get_stats(self) -> Dict[str, Any]:
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / total if total > 0 else 0,
            "size": len(self.cache)
        }


class CachedModule(dspy.Module):
    """帶緩存的模組"""

    def __init__(self, cache: CacheManager = None):
        super().__init__()
        self.cache = cache or CacheManager()
        self.predictor = dspy.Predict("question -> answer")

    def _get_cache_key(self, question: str) -> str:
        return f"q:{question}"

    def forward(self, question: str):
        key = self._get_cache_key(question)

        # 檢查緩存
        cached = self.cache.get(key)
        if cached is not None:
            return dspy.Prediction(answer=cached, from_cache=True)

        # 執行預測
        result = self.predictor(question=question)

        # 存入緩存
        self.cache.set(key, result.answer)

        return dspy.Prediction(answer=result.answer, from_cache=False)


class BatchProcessor:
    """批處理器"""

    def __init__(self, module: dspy.Module, batch_size: int = 10):
        self.module = module
        self.batch_size = batch_size

    def process(self, items: List[Dict[str, Any]]) -> List[Any]:
        results = []

        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_results = []

            for item in batch:
                try:
                    result = self.module(**item)
                    batch_results.append(result)
                except Exception as e:
                    batch_results.append({"error": str(e)})

            results.extend(batch_results)
            print(f"處理進度: {min(i + self.batch_size, len(items))}/{len(items)}")

        return results


# ============================================================
# 5. 調試工具
# ============================================================

class DebugModule(dspy.Module):
    """調試模組"""

    def __init__(self, module: dspy.Module, verbose: bool = True):
        super().__init__()
        self.module = module
        self.verbose = verbose
        self.call_history = []

    def forward(self, **kwargs):
        start_time = time.time()

        if self.verbose:
            print(f"\n{'='*50}")
            print(f"輸入: {json.dumps(kwargs, ensure_ascii=False, indent=2)}")

        try:
            result = self.module(**kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)

        elapsed = time.time() - start_time

        # 記錄歷史
        self.call_history.append({
            "inputs": kwargs,
            "outputs": str(result) if result else None,
            "success": success,
            "error": error,
            "elapsed_ms": elapsed * 1000
        })

        if self.verbose:
            print(f"輸出: {result}")
            print(f"耗時: {elapsed*1000:.2f}ms")
            print(f"{'='*50}")

        if not success:
            raise Exception(error)

        return result

    def get_history(self) -> List[Dict[str, Any]]:
        return self.call_history

    def print_summary(self):
        total = len(self.call_history)
        successes = sum(1 for h in self.call_history if h["success"])
        avg_time = sum(h["elapsed_ms"] for h in self.call_history) / total if total > 0 else 0

        print(f"\n調試摘要:")
        print(f"  總調用: {total}")
        print(f"  成功: {successes}")
        print(f"  失敗: {total - successes}")
        print(f"  平均耗時: {avg_time:.2f}ms")


class InspectSignature:
    """簽名檢查器"""

    @staticmethod
    def inspect(signature: type):
        """檢查簽名定義"""
        print(f"\n簽名: {signature.__name__}")
        print(f"描述: {signature.__doc__ or 'N/A'}")

        print("\n輸入字段:")
        for name, field in signature.model_fields.items():
            if hasattr(field, 'json_schema_extra'):
                desc = field.json_schema_extra.get('desc', 'N/A')
                print(f"  - {name}: {desc}")

        print("\n輸出字段:")
        # DSPy 特定的字段處理
        for attr in dir(signature):
            if not attr.startswith('_'):
                field = getattr(signature, attr, None)
                if isinstance(field, dspy.OutputField):
                    print(f"  - {attr}")


# ============================================================
# 6. 最佳實踐
# ============================================================

BEST_PRACTICES = """
DSPy 最佳實踐
=============

1. Signature 設計
   - 使用清晰的描述
   - 指定輸入/輸出類型
   - 考慮可選字段

2. Module 組織
   - 單一職責原則
   - 組合而非繼承
   - 保持模組小而專注

3. 優化策略
   - 從小數據集開始
   - 使用合適的優化器
   - 迭代改進

4. 錯誤處理
   - 實現重試邏輯
   - 提供回退方案
   - 記錄錯誤日誌

5. 性能優化
   - 使用緩存
   - 批處理請求
   - 選擇合適的模型

6. 調試技巧
   - 使用 verbose 模式
   - 記錄調用歷史
   - 單元測試
"""


# ============================================================
# 使用範例
# ============================================================

def example_advanced_signatures():
    """範例 1: 高級 Signature"""
    print("=" * 50)
    print("範例 1: 高級 Signature 定義")
    print("=" * 50)

    print("""
結構化輸出簽名:
    class StructuredOutputSignature(dspy.Signature):
        query = dspy.InputField(desc="用戶查詢")
        context = dspy.InputField(desc="背景信息", optional=True)

        thought_process = dspy.OutputField(desc="思考過程")
        confidence = dspy.OutputField(desc="置信度 (0-1)")
        answer = dspy.OutputField(desc="最終答案")
        sources = dspy.OutputField(desc="信息來源列表")
""")


def example_self_refining():
    """範例 2: 自我改進模組"""
    print("\n" + "=" * 50)
    print("範例 2: 自我改進模組")
    print("=" * 50)

    print("""
使用示例:
    module = SelfRefiningModule(max_refinements=3)
    result = module(question="解釋量子計算")

    print(f"答案: {result.answer}")
    print(f"改進次數: {result.refinements}")
""")


def example_error_handling():
    """範例 3: 錯誤處理"""
    print("\n" + "=" * 50)
    print("範例 3: 錯誤處理")
    print("=" * 50)

    print("""
重試裝飾器:
    @retry_on_error(max_retries=3, delay=1.0)
    def risky_operation():
        # 可能失敗的操作
        pass

健壯模組:
    module = RobustModule()
    result = module(question="...")
    if hasattr(result, 'error') and result.error:
        print("使用了回退答案")
""")


def example_caching():
    """範例 4: 緩存優化"""
    print("\n" + "=" * 50)
    print("範例 4: 緩存優化")
    print("=" * 50)

    cache = CacheManager(max_size=100)
    module = CachedModule(cache=cache)

    # 模擬使用
    print("第一次調用（無緩存）")
    print("第二次調用（有緩存）")

    # 統計
    stats = cache.get_stats()
    print(f"\n緩存統計: {stats}")


def example_debugging():
    """範例 5: 調試技巧"""
    print("\n" + "=" * 50)
    print("範例 5: 調試技巧")
    print("=" * 50)

    print("""
使用調試模組:
    original_module = MyModule()
    debug_module = DebugModule(original_module, verbose=True)

    # 執行幾次調用
    debug_module(question="問題1")
    debug_module(question="問題2")

    # 查看摘要
    debug_module.print_summary()
""")


def example_best_practices():
    """範例 6: 最佳實踐"""
    print("\n" + "=" * 50)
    print("範例 6: 最佳實踐")
    print("=" * 50)
    print(BEST_PRACTICES)


if __name__ == "__main__":
    print("DSPy 進階技巧範例\n")
    example_advanced_signatures()
    example_self_refining()
    example_error_handling()
    example_caching()
    example_debugging()
    example_best_practices()
