"""
Instructor/Outlines 進階技巧範例
================================

本範例展示 Instructor 和 Outlines 的進階使用技巧。

內容：
1. 自定義驗證器
2. 鉤子和中間件
3. 模型組合
4. 性能優化
5. 調試技巧

安裝依賴：
pip install instructor outlines pydantic
"""

import instructor
from openai import OpenAI
from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Dict, Any, Optional, Callable, TypeVar
from functools import wraps
import time
import json
from dataclasses import dataclass

# ============================================================
# 1. 高級驗證器
# ============================================================

class AdvancedValidation(BaseModel):
    """帶高級驗證的模型"""
    email: str
    phone: str
    age: int
    password: str

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v or '.' not in v:
            raise ValueError('無效的電子郵件格式')
        return v.lower()

    @validator('phone')
    def validate_phone(cls, v):
        # 移除非數字字符
        digits = ''.join(filter(str.isdigit, v))
        if len(digits) < 10:
            raise ValueError('電話號碼至少需要 10 位數字')
        return digits

    @validator('age')
    def validate_age(cls, v):
        if v < 0 or v > 150:
            raise ValueError('年齡必須在 0-150 之間')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('密碼至少需要 8 個字符')
        if not any(c.isupper() for c in v):
            raise ValueError('密碼需要至少一個大寫字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密碼需要至少一個數字')
        return v


class CrossFieldValidation(BaseModel):
    """跨字段驗證"""
    start_date: str
    end_date: str
    min_value: float
    max_value: float

    @root_validator
    def validate_ranges(cls, values):
        if values.get('start_date') and values.get('end_date'):
            if values['start_date'] > values['end_date']:
                raise ValueError('開始日期必須早於結束日期')

        if values.get('min_value') and values.get('max_value'):
            if values['min_value'] > values['max_value']:
                raise ValueError('最小值必須小於最大值')

        return values


VALIDATION_EXAMPLE = '''
import instructor
from openai import OpenAI

client = instructor.from_openai(OpenAI())

# 使用帶驗證的模型
try:
    result = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_model=AdvancedValidation,
        max_retries=3,  # 驗證失敗時自動重試
        messages=[
            {"role": "user", "content": "生成一個用戶註冊資料"}
        ]
    )
    print(f"驗證通過: {result}")
except Exception as e:
    print(f"驗證失敗: {e}")
'''


# ============================================================
# 2. 自定義鉤子
# ============================================================

T = TypeVar('T', bound=BaseModel)


class HookManager:
    """鉤子管理器"""

    def __init__(self):
        self.pre_hooks: List[Callable] = []
        self.post_hooks: List[Callable] = []
        self.error_hooks: List[Callable] = []

    def add_pre_hook(self, hook: Callable):
        """添加前置鉤子"""
        self.pre_hooks.append(hook)

    def add_post_hook(self, hook: Callable):
        """添加後置鉤子"""
        self.post_hooks.append(hook)

    def add_error_hook(self, hook: Callable):
        """添加錯誤鉤子"""
        self.error_hooks.append(hook)

    def run_pre_hooks(self, **kwargs):
        """運行前置鉤子"""
        for hook in self.pre_hooks:
            hook(**kwargs)

    def run_post_hooks(self, result: Any, **kwargs):
        """運行後置鉤子"""
        for hook in self.post_hooks:
            result = hook(result, **kwargs)
        return result

    def run_error_hooks(self, error: Exception, **kwargs):
        """運行錯誤鉤子"""
        for hook in self.error_hooks:
            hook(error, **kwargs)


class HookedClient:
    """帶鉤子的客戶端"""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.client = instructor.from_openai(OpenAI())
        self.model = model
        self.hooks = HookManager()

    def create(
        self,
        response_model: type,
        messages: List[Dict],
        **kwargs
    ):
        """帶鉤子的創建調用"""
        # 前置鉤子
        self.hooks.run_pre_hooks(
            response_model=response_model,
            messages=messages,
            **kwargs
        )

        try:
            result = self.client.chat.completions.create(
                model=self.model,
                response_model=response_model,
                messages=messages,
                **kwargs
            )

            # 後置鉤子
            result = self.hooks.run_post_hooks(result, messages=messages)
            return result

        except Exception as e:
            # 錯誤鉤子
            self.hooks.run_error_hooks(e, messages=messages)
            raise


HOOKS_EXAMPLE = '''
# 鉤子使用範例

client = HookedClient()

# 添加日誌鉤子
def log_pre(response_model, messages, **kwargs):
    print(f"[PRE] 模型: {response_model.__name__}")

def log_post(result, messages, **kwargs):
    print(f"[POST] 結果: {result}")
    return result

def log_error(error, messages, **kwargs):
    print(f"[ERROR] 錯誤: {error}")

client.hooks.add_pre_hook(log_pre)
client.hooks.add_post_hook(log_post)
client.hooks.add_error_hook(log_error)

# 使用
result = client.create(
    response_model=MyModel,
    messages=[{"role": "user", "content": "..."}]
)
'''


# ============================================================
# 3. 模型組合
# ============================================================

class Step1Output(BaseModel):
    """第一步輸出"""
    analysis: str
    key_points: List[str]


class Step2Output(BaseModel):
    """第二步輸出"""
    recommendations: List[str]
    priority: str


class FinalOutput(BaseModel):
    """最終輸出"""
    summary: str
    action_items: List[str]
    confidence: float


class ChainedProcessor:
    """鏈式處理器"""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.client = instructor.from_openai(OpenAI())
        self.model = model

    def process_chain(self, input_text: str) -> FinalOutput:
        """執行處理鏈"""
        # 步驟 1: 分析
        step1 = self.client.chat.completions.create(
            model=self.model,
            response_model=Step1Output,
            messages=[
                {"role": "system", "content": "分析輸入文本並提取關鍵點"},
                {"role": "user", "content": input_text}
            ]
        )

        # 步驟 2: 建議
        step2 = self.client.chat.completions.create(
            model=self.model,
            response_model=Step2Output,
            messages=[
                {"role": "system", "content": "基於分析提供建議"},
                {"role": "user", "content": f"分析: {step1.analysis}\n關鍵點: {step1.key_points}"}
            ]
        )

        # 步驟 3: 總結
        final = self.client.chat.completions.create(
            model=self.model,
            response_model=FinalOutput,
            messages=[
                {"role": "system", "content": "整合所有信息生成最終報告"},
                {"role": "user", "content": f"""
                分析: {step1.analysis}
                關鍵點: {step1.key_points}
                建議: {step2.recommendations}
                優先級: {step2.priority}
                """}
            ]
        )

        return final


CHAIN_EXAMPLE = '''
# 模型組合範例

processor = ChainedProcessor()

result = processor.process_chain(
    "我們的銷售額在上個季度下降了 15%，主要原因是..."
)

print(f"摘要: {result.summary}")
print(f"行動項目: {result.action_items}")
print(f"置信度: {result.confidence}")
'''


# ============================================================
# 4. 性能優化
# ============================================================

class CacheDecorator:
    """緩存裝飾器"""

    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成緩存鍵
            key = self._generate_key(args, kwargs)

            if key in self.cache:
                return self.cache[key]

            result = func(*args, **kwargs)

            # 緩存結果
            if len(self.cache) >= self.max_size:
                self.cache.pop(next(iter(self.cache)))
            self.cache[key] = result

            return result

        return wrapper

    def _generate_key(self, args, kwargs) -> str:
        return str(args) + str(sorted(kwargs.items()))


@dataclass
class PerformanceMetrics:
    """性能指標"""
    call_count: int = 0
    total_time: float = 0
    cache_hits: int = 0
    cache_misses: int = 0
    errors: int = 0

    @property
    def avg_time(self) -> float:
        return self.total_time / self.call_count if self.call_count > 0 else 0

    @property
    def cache_hit_rate(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0


class OptimizedClient:
    """優化的客戶端"""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.client = instructor.from_openai(OpenAI())
        self.model = model
        self.metrics = PerformanceMetrics()
        self.cache = {}

    def create_cached(
        self,
        response_model: type,
        messages: List[Dict],
        use_cache: bool = True,
        **kwargs
    ):
        """帶緩存的創建"""
        start_time = time.time()

        # 檢查緩存
        cache_key = self._get_cache_key(messages)
        if use_cache and cache_key in self.cache:
            self.metrics.cache_hits += 1
            return self.cache[cache_key]

        self.metrics.cache_misses += 1

        try:
            result = self.client.chat.completions.create(
                model=self.model,
                response_model=response_model,
                messages=messages,
                **kwargs
            )

            # 存入緩存
            if use_cache:
                self.cache[cache_key] = result

            self.metrics.call_count += 1
            self.metrics.total_time += time.time() - start_time

            return result

        except Exception as e:
            self.metrics.errors += 1
            raise

    def _get_cache_key(self, messages: List[Dict]) -> str:
        return json.dumps(messages, sort_keys=True)

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "call_count": self.metrics.call_count,
            "avg_time": f"{self.metrics.avg_time:.3f}s",
            "cache_hit_rate": f"{self.metrics.cache_hit_rate:.1%}",
            "errors": self.metrics.errors
        }


# ============================================================
# 5. 調試工具
# ============================================================

class DebugClient:
    """調試客戶端"""

    def __init__(self, model: str = "gpt-3.5-turbo", verbose: bool = True):
        self.client = instructor.from_openai(OpenAI())
        self.model = model
        self.verbose = verbose
        self.history = []

    def create(
        self,
        response_model: type,
        messages: List[Dict],
        **kwargs
    ):
        """帶調試的創建"""
        entry = {
            "timestamp": time.time(),
            "model": self.model,
            "response_model": response_model.__name__,
            "messages": messages,
            "kwargs": kwargs,
            "result": None,
            "error": None,
            "elapsed": 0
        }

        start = time.time()

        if self.verbose:
            print(f"\n{'='*50}")
            print(f"[DEBUG] 模型: {self.model}")
            print(f"[DEBUG] 輸出類型: {response_model.__name__}")
            print(f"[DEBUG] 消息數: {len(messages)}")

        try:
            result = self.client.chat.completions.create(
                model=self.model,
                response_model=response_model,
                messages=messages,
                **kwargs
            )

            entry["result"] = result.model_dump() if hasattr(result, 'model_dump') else str(result)
            entry["elapsed"] = time.time() - start

            if self.verbose:
                print(f"[DEBUG] 成功! 耗時: {entry['elapsed']:.3f}s")
                print(f"[DEBUG] 結果: {result}")

            return result

        except Exception as e:
            entry["error"] = str(e)
            entry["elapsed"] = time.time() - start

            if self.verbose:
                print(f"[DEBUG] 錯誤: {e}")

            raise

        finally:
            self.history.append(entry)

    def get_history(self) -> List[Dict]:
        return self.history

    def export_history(self, file_path: str):
        """導出歷史"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2, default=str)


DEBUG_EXAMPLE = '''
# 調試客戶端使用範例

client = DebugClient(verbose=True)

result = client.create(
    response_model=MyModel,
    messages=[{"role": "user", "content": "..."}]
)

# 導出調試歷史
client.export_history("debug_log.json")

# 分析歷史
for entry in client.get_history():
    print(f"耗時: {entry['elapsed']:.3f}s")
    print(f"錯誤: {entry['error']}")
'''


# ============================================================
# 6. 最佳實踐
# ============================================================

BEST_PRACTICES = """
Instructor/Outlines 最佳實踐
============================

1. 模型設計
   - 使用清晰的字段描述
   - 添加適當的驗證器
   - 考慮可選字段和默認值

2. 錯誤處理
   - 設置合理的 max_retries
   - 實現自定義錯誤處理
   - 記錄失敗案例以改進

3. 性能優化
   - 使用緩存避免重複調用
   - 批量處理相似請求
   - 選擇合適的模型大小

4. 調試技巧
   - 使用 verbose 模式
   - 記錄所有調用歷史
   - 分析失敗模式

5. 安全考慮
   - 驗證所有輸入
   - 限制輸出大小
   - 保護敏感數據
"""


# ============================================================
# 使用範例
# ============================================================

def example_validation():
    """範例 1: 高級驗證"""
    print("=" * 50)
    print("範例 1: 高級驗證器")
    print("=" * 50)
    print(VALIDATION_EXAMPLE)


def example_hooks():
    """範例 2: 鉤子"""
    print("\n" + "=" * 50)
    print("範例 2: 自定義鉤子")
    print("=" * 50)
    print(HOOKS_EXAMPLE)


def example_chain():
    """範例 3: 模型組合"""
    print("\n" + "=" * 50)
    print("範例 3: 模型組合")
    print("=" * 50)
    print(CHAIN_EXAMPLE)


def example_optimization():
    """範例 4: 性能優化"""
    print("\n" + "=" * 50)
    print("範例 4: 性能優化")
    print("=" * 50)

    client = OptimizedClient()
    print(f"優化客戶端已創建")
    print(f"  緩存大小: {len(client.cache)}")
    print(f"  指標: {client.get_metrics()}")


def example_debug():
    """範例 5: 調試"""
    print("\n" + "=" * 50)
    print("範例 5: 調試工具")
    print("=" * 50)
    print(DEBUG_EXAMPLE)


def example_best_practices():
    """範例 6: 最佳實踐"""
    print("\n" + "=" * 50)
    print("範例 6: 最佳實踐")
    print("=" * 50)
    print(BEST_PRACTICES)


if __name__ == "__main__":
    print("Instructor/Outlines 進階技巧範例\n")
    example_validation()
    example_hooks()
    example_chain()
    example_optimization()
    example_debug()
    example_best_practices()
