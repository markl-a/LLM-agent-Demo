"""
ControlFlow 錯誤處理詳解
========================

本文件深入探討 ControlFlow 中的錯誤處理和恢復策略,包括:
1. 基本異常處理
2. 重試機制
3. 錯誤降級
4. 超時處理
5. 錯誤記錄和追蹤
6. 恢復策略
7. 容錯設計

作者: ControlFlow 示例團隊
日期: 2025
"""

import os
import time
import logging
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import controlflow as cf
from controlflow import Agent, Task, Flow
from pydantic import BaseModel, Field
from dotenv import load_dotenv


# ========== 配置 ==========

load_dotenv()

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ========== 數據模型 ==========

class ErrorSeverity(str, Enum):
    """錯誤嚴重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    """錯誤類別"""
    NETWORK = "network"
    TIMEOUT = "timeout"
    VALIDATION = "validation"
    PROCESSING = "processing"
    SYSTEM = "system"


class ErrorRecord(BaseModel):
    """錯誤記錄模型"""
    error_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    task_id: Optional[str] = None
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    resolved: bool = False


class RetryConfig(BaseModel):
    """重試配置模型"""
    max_attempts: int = Field(default=3, ge=1)
    initial_delay: float = Field(default=1.0, ge=0)
    backoff_factor: float = Field(default=2.0, ge=1)
    max_delay: float = Field(default=60.0, ge=0)


# ========== 基本異常處理 ==========

class BasicErrorHandling:
    """
    基本異常處理示例

    演示基礎的異常捕獲和處理
    """

    @staticmethod
    @cf.flow
    def simple_try_catch():
        """
        簡單的 try-catch 模式
        """
        print("🔄 簡單異常處理...\n")

        try:
            print("📍 執行可能失敗的任務")

            task = Task(
                objective="執行風險操作",
                instructions="這個操作可能會失敗"
            )

            result = task.run()
            print(f"✅ 任務成功: {result}")
            return result

        except Exception as e:
            print(f"❌ 捕獲異常: {type(e).__name__}")
            print(f"   錯誤信息: {str(e)}")

            # 記錄錯誤
            logger.error(f"任務失敗: {str(e)}", exc_info=True)

            # 返回默認值或錯誤信息
            return {"error": str(e), "success": False}

    @staticmethod
    @cf.flow
    def specific_exception_handling():
        """
        特定異常處理

        針對不同類型的異常採取不同的處理策略
        """
        print("🔄 特定異常處理...\n")

        try:
            print("📍 執行任務")

            # 模擬可能拋出不同異常的操作
            task = Task(
                objective="執行複雜操作",
                instructions="處理複雜邏輯"
            )

            result = task.run()
            return result

        except ValueError as e:
            print(f"❌ 值錯誤: {str(e)}")
            logger.warning(f"值錯誤: {str(e)}")
            return {"error": "invalid_value", "message": str(e)}

        except TimeoutError as e:
            print(f"❌ 超時錯誤: {str(e)}")
            logger.error(f"超時: {str(e)}")
            return {"error": "timeout", "message": str(e)}

        except ConnectionError as e:
            print(f"❌ 連接錯誤: {str(e)}")
            logger.error(f"網絡錯誤: {str(e)}")
            return {"error": "connection", "message": str(e)}

        except Exception as e:
            print(f"❌ 未知錯誤: {str(e)}")
            logger.critical(f"未知錯誤: {str(e)}", exc_info=True)
            return {"error": "unknown", "message": str(e)}

        finally:
            print("🔚 清理資源")
            # 執行清理操作

    @staticmethod
    @cf.flow
    def nested_error_handling():
        """
        嵌套錯誤處理

        在多層嵌套中處理錯誤
        """
        print("🔄 嵌套錯誤處理...\n")

        try:
            print("📍 外層操作開始")

            # 外層任務
            outer_task = Task(objective="外層任務")

            try:
                print("   📍 內層操作開始")

                # 內層任務
                inner_task = Task(objective="內層任務")
                inner_result = inner_task.run()

                print(f"   ✅ 內層成功")

            except Exception as inner_error:
                print(f"   ❌ 內層錯誤: {str(inner_error)}")
                # 內層錯誤處理,可能重新拋出
                raise RuntimeError(f"內層失敗: {str(inner_error)}")

            outer_result = outer_task.run()
            print(f"✅ 外層成功")

            return outer_result

        except Exception as outer_error:
            print(f"❌ 外層錯誤: {str(outer_error)}")
            logger.error(f"嵌套錯誤: {str(outer_error)}")
            return {"error": "nested_failure", "message": str(outer_error)}


# ========== 重試機制 ==========

class RetryMechanism:
    """
    重試機制

    實現智能重試策略
    """

    def __init__(self, config: Optional[RetryConfig] = None):
        """
        初始化重試機制

        Args:
            config: 重試配置
        """
        self.config = config or RetryConfig()
        self.attempt_count = 0

    def calculate_delay(self, attempt: int) -> float:
        """
        計算重試延遲

        Args:
            attempt: 當前嘗試次數

        Returns:
            float: 延遲秒數
        """
        delay = self.config.initial_delay * (self.config.backoff_factor ** attempt)
        return min(delay, self.config.max_delay)

    @cf.flow
    def retry_with_backoff(self, operation: Callable, *args, **kwargs) -> Any:
        """
        帶退避的重試

        Args:
            operation: 要執行的操作
            *args: 位置參數
            **kwargs: 關鍵字參數

        Returns:
            Any: 操作結果
        """
        print(f"🔄 重試機制 (最大嘗試: {self.config.max_attempts})...\n")

        last_error = None

        for attempt in range(self.config.max_attempts):
            try:
                print(f"📍 嘗試 {attempt + 1}/{self.config.max_attempts}")

                # 執行操作
                result = operation(*args, **kwargs)

                print(f"✅ 嘗試 {attempt + 1} 成功!")
                return result

            except Exception as e:
                last_error = e
                print(f"❌ 嘗試 {attempt + 1} 失敗: {str(e)}")

                if attempt < self.config.max_attempts - 1:
                    # 計算延遲
                    delay = self.calculate_delay(attempt)
                    print(f"⏳ 等待 {delay:.1f} 秒後重試...")
                    time.sleep(delay)
                else:
                    print(f"⛔ 所有重試都失敗了")

        # 所有嘗試都失敗
        raise RuntimeError(f"重試失敗: {str(last_error)}")

    @staticmethod
    @cf.flow
    def conditional_retry():
        """
        條件重試

        只對特定類型的錯誤進行重試
        """
        print("🔄 條件重試...\n")

        max_attempts = 3
        retryable_errors = (ConnectionError, TimeoutError)

        for attempt in range(max_attempts):
            try:
                print(f"📍 嘗試 {attempt + 1}/{max_attempts}")

                task = Task(objective="執行網絡操作")
                result = task.run()

                print(f"✅ 成功!")
                return result

            except retryable_errors as e:
                print(f"⚠️ 可重試錯誤: {type(e).__name__}")

                if attempt < max_attempts - 1:
                    print(f"🔄 重試...")
                    time.sleep(1)
                else:
                    print(f"❌ 重試次數已用完")
                    raise

            except Exception as e:
                print(f"❌ 不可重試錯誤: {type(e).__name__}")
                # 不重試,直接失敗
                raise

    @staticmethod
    def demonstrate_retry():
        """演示重試機制"""
        print("🔄 演示重試機制\n")

        # 創建重試配置
        config = RetryConfig(
            max_attempts=3,
            initial_delay=0.5,
            backoff_factor=2.0,
            max_delay=10.0
        )

        retry_mgr = RetryMechanism(config)

        # 定義可能失敗的操作
        def flaky_operation():
            import random
            if random.random() < 0.7:  # 70% 失敗率
                raise ConnectionError("連接失敗")
            return "操作成功"

        try:
            result = retry_mgr.retry_with_backoff(flaky_operation)
            print(f"\n最終結果: {result}")
        except Exception as e:
            print(f"\n最終失敗: {str(e)}")


# ========== 錯誤降級 ==========

class FallbackStrategies:
    """
    降級策略

    實現優雅降級
    """

    @staticmethod
    @cf.flow
    def primary_with_fallback():
        """
        主方法帶降級
        """
        print("🔄 主方法帶降級...\n")

        # 嘗試主方法
        try:
            print("📍 嘗試主方法 (高質量)")
            primary_task = Task(
                objective="使用高級算法處理",
                instructions="使用最先進的方法"
            )
            result = primary_task.run()
            print("✅ 主方法成功")
            return {"method": "primary", "result": result}

        except Exception as e:
            print(f"❌ 主方法失敗: {str(e)}")
            print("🔄 切換到降級方法")

            try:
                # 降級方法
                print("📍 使用降級方法 (標準質量)")
                fallback_task = Task(
                    objective="使用標準算法處理",
                    instructions="使用可靠但較簡單的方法"
                )
                result = fallback_task.run()
                print("✅ 降級方法成功")
                return {"method": "fallback", "result": result}

            except Exception as fallback_error:
                print(f"❌ 降級方法也失敗: {str(fallback_error)}")
                # 最後的備用方案
                print("📍 使用最小可行方案")
                return {"method": "minimal", "result": "默認響應"}

    @staticmethod
    @cf.flow
    def feature_toggle_fallback(features_enabled: Dict[str, bool]):
        """
        基於功能開關的降級

        Args:
            features_enabled: 功能開關狀態
        """
        print("🔄 功能開關降級...\n")
        print(f"功能狀態: {features_enabled}\n")

        # 檢查高級功能
        if features_enabled.get("ai_enhancement", False):
            try:
                print("📍 使用 AI 增強功能")
                task = Task(objective="AI 增強處理")
                return {"level": "enhanced", "result": task.run()}
            except Exception as e:
                print(f"❌ AI 增強失敗: {str(e)}")
                # 降級到標準功能

        # 標準功能
        if features_enabled.get("standard_processing", True):
            try:
                print("📍 使用標準處理")
                task = Task(objective="標準處理")
                return {"level": "standard", "result": task.run()}
            except Exception as e:
                print(f"❌ 標準處理失敗: {str(e)}")
                # 降級到基礎功能

        # 基礎功能
        print("📍 使用基礎功能")
        return {"level": "basic", "result": "基礎響應"}

    @staticmethod
    @cf.flow
    def cached_fallback(cache: Dict[str, Any], cache_key: str):
        """
        緩存降級

        失敗時使用緩存值

        Args:
            cache: 緩存字典
            cache_key: 緩存鍵
        """
        print("🔄 緩存降級...\n")

        try:
            print("📍 獲取最新數據")
            task = Task(objective="獲取實時數據")
            fresh_data = task.run()

            # 更新緩存
            cache[cache_key] = {
                "data": fresh_data,
                "timestamp": datetime.now().isoformat()
            }

            print("✅ 獲取最新數據成功")
            return fresh_data

        except Exception as e:
            print(f"❌ 獲取最新數據失敗: {str(e)}")

            # 使用緩存
            if cache_key in cache:
                cached = cache[cache_key]
                print(f"📦 使用緩存數據 (時間: {cached['timestamp']})")
                return cached["data"]
            else:
                print("❌ 無可用緩存")
                return None


# ========== 超時處理 ==========

class TimeoutHandling:
    """
    超時處理

    管理任務超時
    """

    @staticmethod
    @cf.flow
    def task_with_timeout(timeout_seconds: int = 30):
        """
        帶超時的任務

        Args:
            timeout_seconds: 超時秒數
        """
        print(f"🔄 帶超時的任務 ({timeout_seconds}秒)...\n")

        try:
            print("📍 執行任務")

            task = Task(
                objective="執行可能長時間運行的任務",
                timeout=timedelta(seconds=timeout_seconds)
            )

            result = task.run()
            print("✅ 任務在時限內完成")
            return result

        except TimeoutError as e:
            print(f"⏰ 任務超時: {str(e)}")
            logger.warning(f"任務超時: {timeout_seconds}秒")

            # 超時處理策略
            return {"status": "timeout", "partial_result": None}

    @staticmethod
    @cf.flow
    def progressive_timeout():
        """
        漸進式超時

        使用遞增的超時時間重試
        """
        print("🔄 漸進式超時...\n")

        timeouts = [5, 10, 20, 40]  # 秒

        for i, timeout in enumerate(timeouts):
            try:
                print(f"📍 嘗試 {i+1} (超時: {timeout}秒)")

                task = Task(
                    objective="長時間任務",
                    timeout=timedelta(seconds=timeout)
                )

                result = task.run()
                print(f"✅ 成功 (用時 < {timeout}秒)")
                return result

            except TimeoutError:
                print(f"⏰ 超時 (>{timeout}秒)")

                if i < len(timeouts) - 1:
                    print(f"🔄 增加超時時間重試...")
                else:
                    print(f"❌ 所有超時嘗試都失敗")
                    raise


# ========== 錯誤記錄和追蹤 ==========

class ErrorTracking:
    """
    錯誤追蹤系統

    記錄和分析錯誤
    """

    def __init__(self):
        """初始化錯誤追蹤"""
        self.errors: List[ErrorRecord] = []
        self.error_counter = 0

    def log_error(
        self,
        category: ErrorCategory,
        severity: ErrorSeverity,
        message: str,
        task_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ErrorRecord:
        """
        記錄錯誤

        Args:
            category: 錯誤類別
            severity: 嚴重程度
            message: 錯誤消息
            task_id: 任務 ID
            context: 上下文信息

        Returns:
            ErrorRecord: 錯誤記錄
        """
        self.error_counter += 1

        error = ErrorRecord(
            error_id=f"ERR_{self.error_counter:04d}",
            category=category,
            severity=severity,
            message=message,
            task_id=task_id,
            context=context or {}
        )

        self.errors.append(error)

        # 根據嚴重程度記錄日誌
        log_message = f"[{error.error_id}] {error.category.value}: {message}"

        if severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
        elif severity == ErrorSeverity.HIGH:
            logger.error(log_message)
        elif severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)

        print(f"📝 錯誤已記錄: {error.error_id} ({severity.value})")

        return error

    def get_error_statistics(self) -> Dict[str, Any]:
        """
        獲取錯誤統計

        Returns:
            Dict[str, Any]: 統計信息
        """
        stats = {
            "total_errors": len(self.errors),
            "by_category": {},
            "by_severity": {},
            "unresolved": sum(1 for e in self.errors if not e.resolved)
        }

        for error in self.errors:
            # 按類別統計
            category_key = error.category.value
            stats["by_category"][category_key] = stats["by_category"].get(category_key, 0) + 1

            # 按嚴重程度統計
            severity_key = error.severity.value
            stats["by_severity"][severity_key] = stats["by_severity"].get(severity_key, 0) + 1

        return stats

    def get_recent_errors(self, limit: int = 10) -> List[ErrorRecord]:
        """
        獲取最近的錯誤

        Args:
            limit: 數量限制

        Returns:
            List[ErrorRecord]: 錯誤記錄列表
        """
        return self.errors[-limit:]

    @staticmethod
    def demonstrate_tracking():
        """演示錯誤追蹤"""
        print("🔄 演示錯誤追蹤\n")

        tracker = ErrorTracking()

        # 記錄各種錯誤
        print("📍 記錄錯誤")
        tracker.log_error(
            ErrorCategory.NETWORK,
            ErrorSeverity.HIGH,
            "API 連接失敗",
            task_id="task_001",
            context={"url": "https://api.example.com", "timeout": 30}
        )

        tracker.log_error(
            ErrorCategory.VALIDATION,
            ErrorSeverity.MEDIUM,
            "輸入驗證失敗",
            task_id="task_002"
        )

        tracker.log_error(
            ErrorCategory.TIMEOUT,
            ErrorSeverity.LOW,
            "操作超時",
            task_id="task_003"
        )

        print()

        # 獲取統計
        print("📍 錯誤統計")
        stats = tracker.get_error_statistics()
        print(f"   總錯誤數: {stats['total_errors']}")
        print(f"   未解決: {stats['unresolved']}")
        print(f"   按類別: {stats['by_category']}")
        print(f"   按嚴重程度: {stats['by_severity']}")
        print()


# ========== 主程序 ==========

def main():
    """
    主程序入口

    演示各種錯誤處理方法
    """
    print("=" * 70)
    print("  ControlFlow 錯誤處理示例")
    print("=" * 70)
    print()

    try:
        # 1. 基本異常處理
        print("\n" + "=" * 70)
        print("1. 基本異常處理")
        print("=" * 70 + "\n")

        # BasicErrorHandling.simple_try_catch()
        # BasicErrorHandling.specific_exception_handling()
        print("✅ 基本異常處理示例已定義\n")

        # 2. 重試機制
        print("\n" + "=" * 70)
        print("2. 重試機制")
        print("=" * 70 + "\n")

        RetryMechanism.demonstrate_retry()

        # 3. 錯誤降級
        print("\n" + "=" * 70)
        print("3. 錯誤降級")
        print("=" * 70 + "\n")

        # FallbackStrategies.primary_with_fallback()
        print("✅ 降級策略示例已定義\n")

        # 4. 超時處理
        print("\n" + "=" * 70)
        print("4. 超時處理")
        print("=" * 70 + "\n")

        # TimeoutHandling.task_with_timeout(5)
        print("✅ 超時處理示例已定義\n")

        # 5. 錯誤追蹤
        print("\n" + "=" * 70)
        print("5. 錯誤追蹤")
        print("=" * 70 + "\n")

        ErrorTracking.demonstrate_tracking()

        print("\n" + "=" * 70)
        print("演示完成")
        print("=" * 70)
        print("\n✅ 所有錯誤處理示例已成功展示!")
        print("\n💡 錯誤處理要點:")
        print("   - 異常捕獲: 使用 try-except 捕獲和處理異常")
        print("   - 重試機制: 實現智能重試與退避策略")
        print("   - 優雅降級: 提供備用方案確保服務可用")
        print("   - 超時控制: 設置合理的超時避免無限等待")
        print("   - 錯誤追蹤: 記錄和分析錯誤便於排查")
        print("\n💡 下一步:")
        print("   - 查看 09_子流程.py 學習子流程組合")
        print("   - 查看 10_生產部署.py 學習生產部署")
        print()

    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
