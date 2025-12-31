"""
日誌工具類模組

此模組提供了方便的日誌工具函數、裝飾器和上下文管理器：
- get_logger(): 獲取配置好的日誌器
- LogTimer: 計時上下文管理器
- log_execution: 函數執行追蹤裝飾器
- log_exception: 異常捕獲裝飾器
- StructuredLogger: 結構化日誌工具

作者: LLM Agent Demo
日期: 2025-12-31
"""

import logging
import functools
import time
import traceback
from typing import Optional, Callable, Any, Dict
from contextlib import contextmanager
from pathlib import Path

from logging_config import setup_logging, LogConfig


# 全局日誌器緩存
_logger_cache: Dict[str, logging.Logger] = {}


def get_logger(
    name: Optional[str] = None,
    level: int = logging.INFO,
    **kwargs
) -> logging.Logger:
    """獲取或創建日誌器

    此函數會緩存日誌器實例，避免重複創建

    Args:
        name: 日誌器名稱（如果為 None，使用調用者的模組名）
        level: 日誌級別
        **kwargs: 傳遞給 setup_logging 的其他參數

    Returns:
        配置好的日誌器對象

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info('這是一條日誌消息')
    """
    # 如果未提供名稱，使用調用者的模組名
    if name is None:
        import inspect
        frame = inspect.currentframe()
        if frame and frame.f_back:
            name = frame.f_back.f_globals.get('__name__', 'unknown')
        else:
            name = 'unknown'

    # 檢查緩存
    cache_key = f"{name}_{level}"
    if cache_key in _logger_cache:
        return _logger_cache[cache_key]

    # 創建新的日誌器
    logger = setup_logging(name=name, level=level, **kwargs)
    _logger_cache[cache_key] = logger

    return logger


def clear_logger_cache() -> None:
    """清除日誌器緩存

    在需要重新配置日誌系統時調用
    """
    global _logger_cache
    _logger_cache.clear()


class LogTimer:
    """計時上下文管理器

    用於測量代碼塊的執行時間並記錄日誌

    Example:
        >>> logger = get_logger(__name__)
        >>> with LogTimer(logger, '數據處理'):
        ...     process_data()
        # 輸出: 數據處理 完成，耗時: 1.23 秒
    """

    def __init__(
        self,
        logger: logging.Logger,
        operation: str = '操作',
        level: int = logging.INFO,
        log_start: bool = True,
        log_end: bool = True,
    ):
        """初始化計時器

        Args:
            logger: 日誌器對象
            operation: 操作名稱
            level: 日誌級別
            log_start: 是否記錄開始日誌
            log_end: 是否記錄結束日誌
        """
        self.logger = logger
        self.operation = operation
        self.level = level
        self.log_start = log_start
        self.log_end = log_end
        self.start_time = None
        self.end_time = None
        self.elapsed = None

    def __enter__(self):
        """進入上下文"""
        self.start_time = time.time()
        if self.log_start:
            self.logger.log(self.level, f"{self.operation} 開始...")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        self.end_time = time.time()
        self.elapsed = self.end_time - self.start_time

        if exc_type is not None:
            # 發生異常
            self.logger.error(
                f"{self.operation} 失敗（耗時: {self.elapsed:.2f} 秒）: {exc_val}"
            )
        elif self.log_end:
            # 正常完成
            self.logger.log(
                self.level,
                f"{self.operation} 完成，耗時: {self.elapsed:.2f} 秒"
            )

        return False  # 不抑制異常

    def get_elapsed_time(self) -> Optional[float]:
        """獲取已耗時間

        Returns:
            耗時（秒），如果尚未完成則返回 None
        """
        return self.elapsed


@contextmanager
def log_time(
    logger: logging.Logger,
    operation: str = '操作',
    level: int = logging.INFO,
):
    """計時上下文管理器的函數版本

    Args:
        logger: 日誌器對象
        operation: 操作名稱
        level: 日誌級別

    Yields:
        LogTimer 實例

    Example:
        >>> logger = get_logger(__name__)
        >>> with log_time(logger, '數據庫查詢'):
        ...     query_database()
    """
    timer = LogTimer(logger, operation, level)
    with timer:
        yield timer


def log_execution(
    logger: Optional[logging.Logger] = None,
    level: int = logging.DEBUG,
    log_args: bool = True,
    log_result: bool = True,
    log_time: bool = True,
):
    """函數執行追蹤裝飾器

    記錄函數的調用、參數、返回值和執行時間

    Args:
        logger: 日誌器對象（如果為 None，使用函數所在模組的日誌器）
        level: 日誌級別
        log_args: 是否記錄參數
        log_result: 是否記錄返回值
        log_time: 是否記錄執行時間

    Returns:
        裝飾器函數

    Example:
        >>> @log_execution(logger=get_logger(__name__))
        ... def add(a, b):
        ...     return a + b
        >>> result = add(1, 2)
        # 輸出: 調用函數 add, 參數: (1, 2), {}
        # 輸出: 函數 add 返回: 3, 耗時: 0.00 秒
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 獲取日誌器
            nonlocal logger
            if logger is None:
                logger = get_logger(func.__module__)

            func_name = func.__name__

            # 記錄函數調用
            if log_args:
                logger.log(
                    level,
                    f"調用函數 {func_name}, 參數: {args}, {kwargs}"
                )
            else:
                logger.log(level, f"調用函數 {func_name}")

            # 執行函數並計時
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time

                # 記錄返回值和時間
                log_parts = [f"函數 {func_name}"]
                if log_result:
                    log_parts.append(f"返回: {result}")
                if log_time:
                    log_parts.append(f"耗時: {elapsed:.4f} 秒")

                logger.log(level, ", ".join(log_parts))

                return result

            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    f"函數 {func_name} 執行失敗（耗時: {elapsed:.4f} 秒）: {e}"
                )
                raise

        return wrapper
    return decorator


def log_exception(
    logger: Optional[logging.Logger] = None,
    level: int = logging.ERROR,
    reraise: bool = True,
    message: Optional[str] = None,
):
    """異常捕獲裝飾器

    捕獲並記錄函數執行過程中的異常

    Args:
        logger: 日誌器對象
        level: 日誌級別
        reraise: 是否重新拋出異常
        message: 自定義錯誤消息

    Returns:
        裝飾器函數

    Example:
        >>> @log_exception(logger=get_logger(__name__))
        ... def risky_operation():
        ...     raise ValueError("出錯了")
        >>> risky_operation()
        # 輸出錯誤日誌並重新拋出異常
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 獲取日誌器
            nonlocal logger
            if logger is None:
                logger = get_logger(func.__module__)

            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 構建錯誤消息
                error_msg = message or f"函數 {func.__name__} 執行時發生異常"
                logger.log(
                    level,
                    f"{error_msg}: {e}\n{traceback.format_exc()}"
                )

                if reraise:
                    raise
                return None

        return wrapper
    return decorator


class StructuredLogger:
    """結構化日誌工具

    提供結構化的日誌記錄功能，支持添加上下文信息

    Example:
        >>> logger = StructuredLogger(get_logger(__name__))
        >>> logger.info('用戶登錄', user_id=123, ip='192.168.1.1')
    """

    def __init__(self, logger: logging.Logger):
        """初始化結構化日誌器

        Args:
            logger: 基礎日誌器對象
        """
        self.logger = logger
        self.context: Dict[str, Any] = {}

    def set_context(self, **kwargs) -> None:
        """設置全局上下文信息

        Args:
            **kwargs: 上下文鍵值對
        """
        self.context.update(kwargs)

    def clear_context(self) -> None:
        """清除所有上下文信息"""
        self.context.clear()

    def _format_message(self, message: str, **kwargs) -> str:
        """格式化消息，添加上下文信息

        Args:
            message: 原始消息
            **kwargs: 額外的字段

        Returns:
            格式化後的消息
        """
        # 合併上下文和額外字段
        fields = {**self.context, **kwargs}

        if not fields:
            return message

        # 構建字段字符串
        field_str = ', '.join(f"{k}={v}" for k, v in fields.items())
        return f"{message} | {field_str}"

    def debug(self, message: str, **kwargs) -> None:
        """記錄 DEBUG 級別日誌"""
        self.logger.debug(self._format_message(message, **kwargs))

    def info(self, message: str, **kwargs) -> None:
        """記錄 INFO 級別日誌"""
        self.logger.info(self._format_message(message, **kwargs))

    def warning(self, message: str, **kwargs) -> None:
        """記錄 WARNING 級別日誌"""
        self.logger.warning(self._format_message(message, **kwargs))

    def error(self, message: str, **kwargs) -> None:
        """記錄 ERROR 級別日誌"""
        self.logger.error(self._format_message(message, **kwargs))

    def critical(self, message: str, **kwargs) -> None:
        """記錄 CRITICAL 級別日誌"""
        self.logger.critical(self._format_message(message, **kwargs))

    @contextmanager
    def context_scope(self, **kwargs):
        """臨時上下文範圍

        在上下文管理器範圍內添加臨時上下文信息

        Args:
            **kwargs: 臨時上下文鍵值對

        Example:
            >>> with logger.context_scope(request_id='abc123'):
            ...     logger.info('處理請求')
            # 輸出: 處理請求 | request_id=abc123
        """
        # 保存當前上下文
        old_context = self.context.copy()

        # 添加臨時上下文
        self.context.update(kwargs)

        try:
            yield self
        finally:
            # 恢復原始上下文
            self.context = old_context


class PerformanceLogger:
    """性能日誌記錄器

    專門用於記錄性能相關的指標
    """

    def __init__(self, logger: logging.Logger, threshold: float = 1.0):
        """初始化性能日誌器

        Args:
            logger: 日誌器對象
            threshold: 性能閾值（秒），超過此時間會記錄警告
        """
        self.logger = logger
        self.threshold = threshold

    @contextmanager
    def measure(self, operation: str, **metadata):
        """測量操作性能

        Args:
            operation: 操作名稱
            **metadata: 額外的元數據

        Example:
            >>> perf_logger = PerformanceLogger(get_logger(__name__))
            >>> with perf_logger.measure('數據庫查詢', table='users'):
            ...     query_users()
        """
        start_time = time.time()
        try:
            yield
        finally:
            elapsed = time.time() - start_time

            # 構建日誌消息
            msg_parts = [f"{operation}: {elapsed:.4f}秒"]
            if metadata:
                metadata_str = ', '.join(f"{k}={v}" for k, v in metadata.items())
                msg_parts.append(metadata_str)

            message = ' | '.join(msg_parts)

            # 根據閾值選擇日誌級別
            if elapsed > self.threshold:
                self.logger.warning(f"性能警告 - {message}")
            else:
                self.logger.debug(f"性能 - {message}")


def create_file_logger(
    name: str,
    log_file: str,
    level: int = logging.INFO,
    **kwargs
) -> logging.Logger:
    """創建專門輸出到文件的日誌器

    Args:
        name: 日誌器名稱
        log_file: 日誌文件路徑
        level: 日誌級別
        **kwargs: 其他配置參數

    Returns:
        配置好的文件日誌器
    """
    log_path = Path(log_file)
    log_dir = log_path.parent

    return setup_logging(
        name=name,
        level=level,
        log_dir=str(log_dir),
        log_file=log_path.name,
        console_output=False,
        file_output=True,
        **kwargs
    )


def create_console_logger(
    name: str,
    level: int = logging.INFO,
    use_rich: bool = True,
) -> logging.Logger:
    """創建專門輸出到控制台的日誌器

    Args:
        name: 日誌器名稱
        level: 日誌級別
        use_rich: 是否使用 Rich 彩色輸出

    Returns:
        配置好的控制台日誌器
    """
    return setup_logging(
        name=name,
        level=level,
        console_output=True,
        file_output=False,
        use_rich=use_rich,
    )


if __name__ == '__main__':
    # 測試日誌工具
    print("=== 測試 get_logger ===")
    logger = get_logger(__name__, level=logging.DEBUG)
    logger.debug("這是調試消息")
    logger.info("這是信息消息")

    print("\n=== 測試 LogTimer ===")
    with LogTimer(logger, '測試操作'):
        time.sleep(0.5)

    print("\n=== 測試裝飾器 ===")
    @log_execution(logger=logger)
    def test_function(x, y):
        """測試函數"""
        time.sleep(0.1)
        return x + y

    result = test_function(10, 20)

    print("\n=== 測試 StructuredLogger ===")
    struct_logger = StructuredLogger(logger)
    struct_logger.set_context(app='test_app', version='1.0')
    struct_logger.info('應用程序啟動', user='admin')

    print("\n=== 測試 PerformanceLogger ===")
    perf_logger = PerformanceLogger(logger, threshold=0.2)
    with perf_logger.measure('快速操作'):
        time.sleep(0.1)

    with perf_logger.measure('慢速操作'):
        time.sleep(0.3)
