"""
Atomic Agents 測試策略
======================

本文件展示如何為 Atomic Agents 編寫測試。
完善的測試策略確保代碼質量和可靠性。

主要內容：
1. 單元測試
2. 集成測試
3. Mock 和 Stub
4. 測試固件
5. 參數化測試
6. 性能測試

作者：Atomic Agents 團隊
日期：2025-12-31
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
import time
from datetime import datetime
from dataclasses import dataclass


# ============================================================================
# 第一部分：測試基礎設施
# ============================================================================

class TestResult(BaseModel):
    """測試結果"""
    test_name: str = Field(..., description="測試名稱")
    passed: bool = Field(..., description="是否通過")
    execution_time: float = Field(..., description="執行時間")
    error_message: Optional[str] = Field(None, description="錯誤消息")
    timestamp: datetime = Field(default_factory=datetime.now)


class TestSuite:
    """
    測試套件

    管理和運行測試。
    """

    def __init__(self, name: str):
        self.name = name
        self.tests: List[callable] = []
        self.results: List[TestResult] = []

    def add_test(self, test_func: callable) -> None:
        """添加測試"""
        self.tests.append(test_func)

    def run(self) -> None:
        """運行所有測試"""
        print(f"\n{'='*60}")
        print(f"運行測試套件: {self.name}")
        print(f"{'='*60}\n")

        for test_func in self.tests:
            self._run_test(test_func)

        self._print_summary()

    def _run_test(self, test_func: callable) -> None:
        """運行單個測試"""
        test_name = test_func.__name__
        print(f"運行: {test_name}...", end=" ")

        start_time = time.time()

        try:
            test_func()
            execution_time = time.time() - start_time

            result = TestResult(
                test_name=test_name,
                passed=True,
                execution_time=execution_time
            )
            print(f"✓ 通過 ({execution_time:.3f}s)")

        except AssertionError as e:
            execution_time = time.time() - start_time

            result = TestResult(
                test_name=test_name,
                passed=False,
                execution_time=execution_time,
                error_message=str(e)
            )
            print(f"✗ 失敗: {str(e)}")

        except Exception as e:
            execution_time = time.time() - start_time

            result = TestResult(
                test_name=test_name,
                passed=False,
                execution_time=execution_time,
                error_message=f"異常: {str(e)}"
            )
            print(f"✗ 錯誤: {str(e)}")

        self.results.append(result)

    def _print_summary(self) -> None:
        """打印測試摘要"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed

        print(f"\n{'='*60}")
        print(f"測試摘要")
        print(f"{'='*60}")
        print(f"總計: {total}")
        print(f"通過: {passed}")
        print(f"失敗: {failed}")
        print(f"成功率: {(passed/total*100):.1f}%")
        print(f"{'='*60}\n")


# ============================================================================
# 第二部分：Mock 對象
# ============================================================================

class MockLLMClient:
    """
    Mock LLM 客戶端

    用於測試，不實際調用 API。
    """

    def __init__(self, responses: Optional[List[str]] = None):
        self.responses = responses or ["這是一個 mock 響應"]
        self.call_count = 0
        self.call_history: List[Dict[str, Any]] = []

    def complete(self, messages: List[Dict[str, str]]) -> str:
        """模擬完成請求"""
        self.call_count += 1

        # 記錄調用
        self.call_history.append({
            'messages': messages,
            'timestamp': datetime.now()
        })

        # 返回預設響應
        response_index = (self.call_count - 1) % len(self.responses)
        return self.responses[response_index]

    def reset(self) -> None:
        """重置狀態"""
        self.call_count = 0
        self.call_history.clear()


class MockDatabase:
    """Mock 數據庫"""

    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.operations: List[str] = []

    def get(self, key: str) -> Optional[Any]:
        """獲取數據"""
        self.operations.append(f"GET:{key}")
        return self.data.get(key)

    def set(self, key: str, value: Any) -> None:
        """設置數據"""
        self.operations.append(f"SET:{key}")
        self.data[key] = value

    def delete(self, key: str) -> None:
        """刪除數據"""
        self.operations.append(f"DELETE:{key}")
        if key in self.data:
            del self.data[key]

    def clear(self) -> None:
        """清空數據"""
        self.data.clear()
        self.operations.clear()


# ============================================================================
# 第三部分：測試固件
# ============================================================================

class TestFixture:
    """
    測試固件

    提供測試所需的設置和清理。
    """

    def __init__(self):
        self.mock_client: Optional[MockLLMClient] = None
        self.mock_db: Optional[MockDatabase] = None

    def setup(self) -> None:
        """設置測試環境"""
        print("  → 設置測試環境...")
        self.mock_client = MockLLMClient()
        self.mock_db = MockDatabase()

    def teardown(self) -> None:
        """清理測試環境"""
        print("  → 清理測試環境...")
        if self.mock_client:
            self.mock_client.reset()
        if self.mock_db:
            self.mock_db.clear()

    def run_with_fixture(self, test_func: callable) -> None:
        """在固件中運行測試"""
        self.setup()
        try:
            test_func(self)
        finally:
            self.teardown()


# ============================================================================
# 第四部分：Agent 測試示例
# ============================================================================

class SimpleAgent:
    """簡單的 Agent 用於測試"""

    def __init__(self, llm_client):
        self.llm_client = llm_client

    def process(self, user_input: str) -> str:
        """處理用戶輸入"""
        messages = [
            {"role": "system", "content": "你是一個助手"},
            {"role": "user", "content": user_input}
        ]
        return self.llm_client.complete(messages)


def test_agent_basic_functionality():
    """測試 Agent 基本功能"""
    # 創建 mock 客戶端
    mock_client = MockLLMClient(responses=["測試響應"])

    # 創建 Agent
    agent = SimpleAgent(mock_client)

    # 測試處理
    result = agent.process("你好")

    # 斷言
    assert result == "測試響應", "響應不匹配"
    assert mock_client.call_count == 1, "調用次數不正確"


def test_agent_multiple_calls():
    """測試 Agent 多次調用"""
    mock_client = MockLLMClient(responses=["響應1", "響應2"])
    agent = SimpleAgent(mock_client)

    # 第一次調用
    result1 = agent.process("問題1")
    assert result1 == "響應1"

    # 第二次調用
    result2 = agent.process("問題2")
    assert result2 == "響應2"

    # 檢查調用歷史
    assert len(mock_client.call_history) == 2


# ============================================================================
# 第五部分：集成測試
# ============================================================================

class DataProcessor:
    """數據處理器"""

    def __init__(self, database, llm_client):
        self.database = database
        self.llm_client = llm_client

    def process_and_store(self, key: str, input_data: str) -> str:
        """處理並存儲數據"""
        # 使用 LLM 處理
        messages = [{"role": "user", "content": input_data}]
        result = self.llm_client.complete(messages)

        # 存儲到數據庫
        self.database.set(key, result)

        return result

    def retrieve(self, key: str) -> Optional[str]:
        """檢索數據"""
        return self.database.get(key)


def test_integration_process_and_store():
    """集成測試：處理和存儲"""
    # 設置 mock 對象
    mock_db = MockDatabase()
    mock_client = MockLLMClient(responses=["處理結果"])

    # 創建處理器
    processor = DataProcessor(mock_db, mock_client)

    # 執行操作
    result = processor.process_and_store("test_key", "測試數據")

    # 驗證結果
    assert result == "處理結果"

    # 驗證數據庫操作
    stored = processor.retrieve("test_key")
    assert stored == "處理結果"

    # 驗證操作歷史
    assert "SET:test_key" in mock_db.operations


# ============================================================================
# 第六部分：參數化測試
# ============================================================================

class ParameterizedTest:
    """參數化測試"""

    def __init__(self, test_func: callable):
        self.test_func = test_func
        self.test_cases: List[tuple] = []

    def add_case(self, *args, expected=None) -> None:
        """添加測試用例"""
        self.test_cases.append((args, expected))

    def run(self) -> List[TestResult]:
        """運行所有測試用例"""
        results = []

        for i, (args, expected) in enumerate(self.test_cases):
            test_name = f"{self.test_func.__name__}_case_{i+1}"
            print(f"運行: {test_name}...", end=" ")

            start_time = time.time()

            try:
                result = self.test_func(*args)

                if expected is not None:
                    assert result == expected, f"期望 {expected}，得到 {result}"

                execution_time = time.time() - start_time
                test_result = TestResult(
                    test_name=test_name,
                    passed=True,
                    execution_time=execution_time
                )
                print(f"✓ 通過")

            except AssertionError as e:
                execution_time = time.time() - start_time
                test_result = TestResult(
                    test_name=test_name,
                    passed=False,
                    execution_time=execution_time,
                    error_message=str(e)
                )
                print(f"✗ 失敗: {str(e)}")

            results.append(test_result)

        return results


def validate_input(text: str) -> bool:
    """驗證輸入"""
    return len(text) > 0 and len(text) <= 100


def test_parameterized_validation():
    """參數化測試示例"""
    param_test = ParameterizedTest(validate_input)

    # 添加測試用例
    param_test.add_case("有效輸入", expected=True)
    param_test.add_case("", expected=False)
    param_test.add_case("x" * 101, expected=False)
    param_test.add_case("正常文本", expected=True)

    # 運行測試
    results = param_test.run()

    # 檢查結果
    passed = sum(1 for r in results if r.passed)
    print(f"\n參數化測試: {passed}/{len(results)} 通過")


# ============================================================================
# 第七部分：性能測試
# ============================================================================

class PerformanceTest:
    """性能測試"""

    def __init__(self, name: str):
        self.name = name
        self.measurements: List[float] = []

    def measure(self, func: callable, iterations: int = 100) -> Dict[str, float]:
        """
        測量性能

        Args:
            func: 要測試的函數
            iterations: 迭代次數

        Returns:
            性能統計
        """
        self.measurements.clear()

        print(f"\n性能測試: {self.name}")
        print(f"迭代次數: {iterations}")

        for i in range(iterations):
            start_time = time.time()
            func()
            execution_time = time.time() - start_time
            self.measurements.append(execution_time)

        return self._calculate_statistics()

    def _calculate_statistics(self) -> Dict[str, float]:
        """計算統計數據"""
        if not self.measurements:
            return {}

        measurements = sorted(self.measurements)
        n = len(measurements)

        stats = {
            'min': measurements[0],
            'max': measurements[-1],
            'mean': sum(measurements) / n,
            'median': measurements[n // 2],
            'p95': measurements[int(n * 0.95)],
            'p99': measurements[int(n * 0.99)]
        }

        # 打印結果
        print(f"\n性能統計:")
        print(f"  最小值: {stats['min']*1000:.3f}ms")
        print(f"  最大值: {stats['max']*1000:.3f}ms")
        print(f"  平均值: {stats['mean']*1000:.3f}ms")
        print(f"  中位數: {stats['median']*1000:.3f}ms")
        print(f"  P95: {stats['p95']*1000:.3f}ms")
        print(f"  P99: {stats['p99']*1000:.3f}ms")

        return stats


def test_agent_performance():
    """測試 Agent 性能"""
    mock_client = MockLLMClient()
    agent = SimpleAgent(mock_client)

    perf_test = PerformanceTest("Agent 處理性能")

    def test_operation():
        agent.process("測試輸入")

    stats = perf_test.measure(test_operation, iterations=100)

    # 性能斷言
    assert stats['mean'] < 0.1, "平均執行時間過長"


# ============================================================================
# 第八部分：測試覆蓋率
# ============================================================================

class CoverageTracker:
    """測試覆蓋率追蹤器"""

    def __init__(self):
        self.covered_functions: set = set()
        self.total_functions: set = set()

    def register_function(self, func_name: str) -> None:
        """註冊函數"""
        self.total_functions.add(func_name)

    def mark_covered(self, func_name: str) -> None:
        """標記為已覆蓋"""
        self.covered_functions.add(func_name)

    def get_coverage(self) -> float:
        """獲取覆蓋率"""
        if not self.total_functions:
            return 0.0

        return len(self.covered_functions) / len(self.total_functions)

    def print_report(self) -> None:
        """打印覆蓋率報告"""
        coverage = self.get_coverage()

        print(f"\n{'='*60}")
        print("測試覆蓋率報告")
        print(f"{'='*60}")
        print(f"總函數數: {len(self.total_functions)}")
        print(f"已覆蓋: {len(self.covered_functions)}")
        print(f"覆蓋率: {coverage*100:.1f}%")

        # 未覆蓋的函數
        uncovered = self.total_functions - self.covered_functions
        if uncovered:
            print(f"\n未覆蓋的函數:")
            for func in uncovered:
                print(f"  - {func}")

        print(f"{'='*60}\n")


# ============================================================================
# 第九部分：斷言輔助函數
# ============================================================================

def assert_equals(actual, expected, message: str = ""):
    """斷言相等"""
    if actual != expected:
        raise AssertionError(
            f"{message}\n期望: {expected}\n實際: {actual}"
        )


def assert_not_none(value, message: str = "值不應為 None"):
    """斷言非空"""
    if value is None:
        raise AssertionError(message)


def assert_in_range(value, min_val, max_val, message: str = ""):
    """斷言在範圍內"""
    if not (min_val <= value <= max_val):
        raise AssertionError(
            f"{message}\n值 {value} 不在範圍 [{min_val}, {max_val}] 內"
        )


def assert_type(value, expected_type, message: str = ""):
    """斷言類型"""
    if not isinstance(value, expected_type):
        raise AssertionError(
            f"{message}\n期望類型: {expected_type}\n實際類型: {type(value)}"
        )


# ============================================================================
# 第十部分：使用示例
# ============================================================================

def example_basic_testing():
    """基礎測試示例"""
    print("\n" + "="*60)
    print("示例 1: 基礎單元測試")
    print("="*60)

    suite = TestSuite("Agent 單元測試")
    suite.add_test(test_agent_basic_functionality)
    suite.add_test(test_agent_multiple_calls)
    suite.run()


def example_integration_testing():
    """集成測試示例"""
    print("\n" + "="*60)
    print("示例 2: 集成測試")
    print("="*60)

    suite = TestSuite("集成測試")
    suite.add_test(test_integration_process_and_store)
    suite.run()


def example_mock_objects():
    """Mock 對象示例"""
    print("\n" + "="*60)
    print("示例 3: 使用 Mock 對象")
    print("="*60)

    # 創建 mock
    mock_client = MockLLMClient(responses=["響應1", "響應2", "響應3"])

    # 使用 mock
    for i in range(3):
        result = mock_client.complete([{"role": "user", "content": f"問題{i+1}"}])
        print(f"調用 {i+1}: {result}")

    print(f"\n總調用次數: {mock_client.call_count}")
    print(f"調用歷史長度: {len(mock_client.call_history)}")


def example_test_fixture():
    """測試固件示例"""
    print("\n" + "="*60)
    print("示例 4: 測試固件")
    print("="*60)

    fixture = TestFixture()

    def test_with_fixture(fix):
        """使用固件的測試"""
        print("  → 執行測試邏輯...")

        # 使用 mock 對象
        result = fix.mock_client.complete([{"role": "user", "content": "測試"}])
        print(f"  → Mock 響應: {result}")

        # 使用 mock 數據庫
        fix.mock_db.set("key", "value")
        value = fix.mock_db.get("key")
        print(f"  → 數據庫值: {value}")

    fixture.run_with_fixture(test_with_fixture)


def example_parameterized_testing():
    """參數化測試示例"""
    print("\n" + "="*60)
    print("示例 5: 參數化測試")
    print("="*60)

    test_parameterized_validation()


def example_performance_testing():
    """性能測試示例"""
    print("\n" + "="*60)
    print("示例 6: 性能測試")
    print("="*60)

    test_agent_performance()


def example_coverage_tracking():
    """覆蓋率追蹤示例"""
    print("\n" + "="*60)
    print("示例 7: 測試覆蓋率追蹤")
    print("="*60)

    tracker = CoverageTracker()

    # 註冊所有函數
    tracker.register_function("function_a")
    tracker.register_function("function_b")
    tracker.register_function("function_c")
    tracker.register_function("function_d")

    # 標記已測試的函數
    tracker.mark_covered("function_a")
    tracker.mark_covered("function_b")
    tracker.mark_covered("function_c")

    # 打印報告
    tracker.print_report()


def example_custom_assertions():
    """自定義斷言示例"""
    print("\n" + "="*60)
    print("示例 8: 自定義斷言")
    print("="*60)

    try:
        # 測試相等斷言
        assert_equals(5, 5, "數值應該相等")
        print("✓ 相等斷言通過")

        # 測試非空斷言
        assert_not_none("value")
        print("✓ 非空斷言通過")

        # 測試範圍斷言
        assert_in_range(50, 0, 100, "值應該在範圍內")
        print("✓ 範圍斷言通過")

        # 測試類型斷言
        assert_type("text", str, "應該是字符串類型")
        print("✓ 類型斷言通過")

    except AssertionError as e:
        print(f"✗ 斷言失敗: {e}")


def main():
    """主函數"""
    print("\n" + "="*60)
    print("Atomic Agents 測試策略")
    print("="*60)

    # 運行示例
    example_basic_testing()
    example_integration_testing()
    example_mock_objects()
    example_test_fixture()
    example_parameterized_testing()
    example_performance_testing()
    example_coverage_tracking()
    example_custom_assertions()

    print("\n" + "="*60)
    print("所有示例運行完成！")
    print("="*60)


if __name__ == "__main__":
    main()
