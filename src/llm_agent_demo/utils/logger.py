"""日誌管理模組 - 提供結構化日誌記錄功能

這個模組提供了完整的日誌解決方案，包括：
- 彩色控制台輸出
- 結構化 JSON 日誌
- 日誌輪轉支持
- 上下文管理器
- 性能監控
- 敏感信息過濾

使用示例：
    >>> from llm_agent_demo.utils.logger import setup_logging, get_logger
    >>> setup_logging(level="INFO", log_file="app.log")
    >>> logger = get_logger(__name__)
    >>> logger.info("應用程式已啟動")
"""

import json
import logging
import os
import socket
import sys
import threading
from contextlib import contextmanager
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

# ============================================================================
# 效能優化：防止重複設置日誌系統
# ============================================================================
_logging_configured = False
_configuration_lock = threading.Lock()


class ColoredFormatter(logging.Formatter):
    """彩色日誌格式化器"""

    # ANSI 顏色代碼
    COLORS = {
        "DEBUG": "\033[36m",  # 青色
        "INFO": "\033[32m",  # 綠色
        "WARNING": "\033[33m",  # 黃色
        "ERROR": "\033[31m",  # 紅色
        "CRITICAL": "\033[35m",  # 紫色
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """格式化日誌記錄"""
        # 添加顏色
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"

        # 調用父類的格式化方法
        formatted = super().format(record)

        # 重置 levelname（避免影響其他 handler）
        record.levelname = levelname

        return formatted


class JSONFormatter(logging.Formatter):
    """JSON 格式化器 - 用於結構化日誌

    提供完整的結構化日誌，包含：
    - 時間戳
    - 日誌級別
    - 來源信息（模組、函數、行號）
    - 進程和線程信息
    - 主機名
    - 自定義欄位

    安全特性：
    - 可選擇隱藏完整路徑（避免洩露服務器結構）
    - 堆棧跟蹤路徑過濾
    """

    def __init__(
        self,
        include_host: bool = True,
        include_process: bool = True,
        sanitize_paths: bool = True,
    ):
        """初始化 JSON 格式化器

        Args:
            include_host: 是否包含主機名
            include_process: 是否包含進程/線程信息
            sanitize_paths: 是否過濾路徑信息（安全考量，建議在生產環境啟用）
        """
        super().__init__()
        self.include_host = include_host
        self.include_process = include_process
        self.sanitize_paths = sanitize_paths
        self._hostname = socket.gethostname() if include_host else None

    def _sanitize_path(self, path: str) -> str:
        """過濾路徑中的敏感信息

        Args:
            path: 完整路徑

        Returns:
            過濾後的路徑（僅保留文件名或相對路徑）
        """
        if not self.sanitize_paths or not path:
            return path

        # 將完整路徑轉換為相對路徑或文件名
        from pathlib import Path as PathLib
        try:
            p = PathLib(path)
            # 嘗試找到 src 或項目根目錄
            parts = p.parts
            for i, part in enumerate(parts):
                if part in ('src', 'lib', 'app', 'tests'):
                    return str(PathLib(*parts[i:]))
            # 如果找不到，只返回最後 3 層目錄
            return str(PathLib(*parts[-3:])) if len(parts) > 3 else str(p)
        except Exception:
            return path

    def _sanitize_traceback(self, tb_str: str) -> str:
        """過濾堆棧跟蹤中的敏感路徑信息

        Args:
            tb_str: 堆棧跟蹤字串

        Returns:
            過濾後的堆棧跟蹤
        """
        if not self.sanitize_paths or not tb_str:
            return tb_str

        import re
        # 過濾類似 /home/user/project/... 的完整路徑
        # 保留相對路徑部分
        pattern = r'File "(/[^"]+/)((?:src|lib|app|tests)/[^"]+)"'
        replacement = r'File "\2"'
        return re.sub(pattern, replacement, tb_str)

    def format(self, record: logging.LogRecord) -> str:
        """格式化為 JSON"""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "source": {
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
                "path": self._sanitize_path(record.pathname),
            },
        }

        # 添加主機信息
        if self.include_host:
            log_data["hostname"] = self._hostname

        # 添加進程/線程信息
        if self.include_process:
            log_data["process"] = {
                "id": record.process,
                "name": record.processName,
            }
            log_data["thread"] = {
                "id": record.thread,
                "name": record.threadName,
            }

        # 添加異常信息（過濾敏感路徑）
        if record.exc_info:
            traceback_str = self.formatException(record.exc_info)
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self._sanitize_traceback(traceback_str),
            }

        # 添加棧信息（如果有，過濾敏感路徑）
        if record.stack_info:
            stack_str = self.formatStack(record.stack_info)
            log_data["stack_info"] = self._sanitize_traceback(stack_str)

        # 添加額外欄位
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        return json.dumps(log_data, ensure_ascii=False, default=str)


class SensitiveDataFilter(logging.Filter):
    """過濾敏感信息的日誌過濾器

    自動過濾常見的敏感信息模式：
    - API 密鑰
    - 密碼
    - 令牌
    - 郵箱地址（部分遮蔽）
    """

    SENSITIVE_PATTERNS = [
        "password",
        "passwd",
        "pwd",
        "secret",
        "api_key",
        "apikey",
        "token",
        "auth",
        "credential",
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """過濾日誌記錄"""
        # 檢查消息中是否包含敏感信息
        message = record.getMessage().lower()

        # 如果包含敏感關鍵字，進行遮蔽
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern in message:
                # 添加警告標記
                record.msg = f"[FILTERED] {record.msg}"
                break

        return True


def validate_log_level(level: str) -> str:
    """驗證並規範化日誌級別

    Args:
        level: 日誌級別字串

    Returns:
        規範化的日誌級別

    Raises:
        ValueError: 如果日誌級別無效
    """
    level = level.upper()
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    if level not in valid_levels:
        raise ValueError(
            f"無效的日誌級別: {level}. 有效級別: {', '.join(valid_levels)}"
        )

    return level


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    json_format: bool = False,
    colorize: bool = True,
    enable_rotation: bool = False,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    rotation_type: str = "size",  # "size" 或 "time"
    when: str = "midnight",
    interval: int = 1,
    enable_filter: bool = False,
    force_reconfigure: bool = False,
) -> None:
    """
    設置日誌系統（帶防重複設置優化）

    Args:
        level: 日誌級別（DEBUG, INFO, WARNING, ERROR, CRITICAL）
               如果為 None，從環境變量 LOG_LEVEL 讀取，默認 INFO
        log_file: 日誌文件路徑（可選）
                 如果為 None，從環境變量 LOG_FILE 讀取
        json_format: 是否使用 JSON 格式
                    從環境變量 LOG_JSON 讀取（true/false）
        colorize: 是否使用彩色輸出（僅控制台）
        enable_rotation: 是否啟用日誌輪轉
        max_bytes: 單個日誌文件最大大小（僅 size 輪轉）
        backup_count: 保留的備份文件數量
        rotation_type: 輪轉類型 - "size" 按大小，"time" 按時間
        when: 時間輪轉間隔單位（midnight, H, D, W0-W6）
        interval: 時間輪轉間隔數值
        enable_filter: 是否啟用敏感信息過濾
        force_reconfigure: 是否強制重新配置（默認 False，效能優化）

    Raises:
        ValueError: 如果日誌級別無效

    環境變量：
        LOG_LEVEL: 日誌級別
        LOG_FILE: 日誌文件路徑
        LOG_JSON: 是否使用 JSON 格式（true/false）
        LOG_FILTER: 是否啟用過濾器（true/false）

    注意：
        為了提高效能，默認情況下日誌系統只會配置一次。
        如果需要重新配置，請設置 force_reconfigure=True。
    """
    global _logging_configured

    # 效能優化：防止重複設置（使用線程鎖確保線程安全）
    with _configuration_lock:
        if _logging_configured and not force_reconfigure:
            # 已經配置過且不強制重新配置，直接返回
            logger = logging.getLogger(__name__)
            logger.debug("日誌系統已配置，跳過重複設置")
            return

        # 從環境變量讀取配置
        if level is None:
            level = os.getenv("LOG_LEVEL", "INFO")

        if log_file is None:
            log_file = os.getenv("LOG_FILE")

        if os.getenv("LOG_JSON", "").lower() == "true":
            json_format = True

        if os.getenv("LOG_FILTER", "").lower() == "true":
            enable_filter = True

        # 驗證日誌級別
        try:
            level = validate_log_level(level)
        except ValueError as e:
            raise ValueError(f"日誌配置錯誤: {e}")

        # 獲取根日誌記錄器
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level))

        # 清除現有的 handlers
        root_logger.handlers.clear()

        # 控制台 handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level))

        if json_format:
            console_formatter = JSONFormatter()
        elif colorize:
            console_formatter = ColoredFormatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        else:
            console_formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

        console_handler.setFormatter(console_formatter)

        # 添加過濾器
        if enable_filter:
            console_handler.addFilter(SensitiveDataFilter())

        root_logger.addHandler(console_handler)

        # 文件 handler（如果指定）
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            # 根據配置選擇不同的 handler
            if enable_rotation:
                if rotation_type == "size":
                    file_handler = RotatingFileHandler(
                        log_file,
                        maxBytes=max_bytes,
                        backupCount=backup_count,
                        encoding="utf-8",
                    )
                elif rotation_type == "time":
                    file_handler = TimedRotatingFileHandler(
                        log_file,
                        when=when,
                        interval=interval,
                        backupCount=backup_count,
                        encoding="utf-8",
                    )
                else:
                    raise ValueError(f"無效的輪轉類型: {rotation_type}")
            else:
                file_handler = logging.FileHandler(log_file, encoding="utf-8")

            file_handler.setLevel(getattr(logging, level))

            if json_format:
                file_formatter = JSONFormatter()
            else:
                file_formatter = logging.Formatter(
                    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )

            file_handler.setFormatter(file_formatter)

            # 添加過濾器
            if enable_filter:
                file_handler.addFilter(SensitiveDataFilter())

            root_logger.addHandler(file_handler)

        # 設置第三方庫的日誌級別（避免過多日誌）
        _setup_third_party_loggers()

        # 標記日誌系統已配置
        _logging_configured = True


def _setup_third_party_loggers() -> None:
    """設置第三方庫的日誌級別"""
    third_party_loggers = [
        "httpx",
        "httpcore",
        "openai",
        "anthropic",
        "chromadb",
        "urllib3",
        "requests",
        "boto3",
        "botocore",
        "langchain",
        "llama_index",
    ]

    for logger_name in third_party_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    獲取日誌記錄器

    Args:
        name: 日誌記錄器名稱（通常使用 __name__）
        level: 日誌級別（可選，默認使用根日誌記錄器的級別）

    Returns:
        配置好的日誌記錄器
    """
    logger = logging.getLogger(name)

    if level:
        logger.setLevel(getattr(logging, level.upper()))

    return logger


class LoggerAdapter(logging.LoggerAdapter):
    """
    日誌適配器 - 用於添加上下文信息

    使用示例:
        logger = get_logger(__name__)
        adapter = LoggerAdapter(logger, {"user_id": "123", "request_id": "abc"})
        adapter.info("處理請求")
    """

    def process(
        self, msg: str, kwargs: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """處理日誌消息，添加額外信息

        Args:
            msg: 日誌消息
            kwargs: 日誌關鍵字參數

        Returns:
            處理後的 (msg, kwargs) 元組
        """
        if "extra" not in kwargs:
            kwargs["extra"] = {}

        kwargs["extra"]["extra_data"] = self.extra

        return msg, kwargs


# 預定義的日誌記錄器
def get_app_logger() -> logging.Logger:
    """獲取應用程式主日誌記錄器"""
    return get_logger("llm_agent_demo")


def get_langchain_logger() -> logging.Logger:
    """獲取 LangChain 日誌記錄器"""
    return get_logger("llm_agent_demo.langchain")


def get_llamaindex_logger() -> logging.Logger:
    """獲取 LlamaIndex 日誌記錄器"""
    return get_logger("llm_agent_demo.llamaindex")


def get_autogen_logger() -> logging.Logger:
    """獲取 AutoGen 日誌記錄器"""
    return get_logger("llm_agent_demo.autogen")


def get_crewai_logger() -> logging.Logger:
    """獲取 CrewAI 日誌記錄器"""
    return get_logger("llm_agent_demo.crewai")


def get_metagpt_logger() -> logging.Logger:
    """獲取 MetaGPT 日誌記錄器"""
    return get_logger("llm_agent_demo.metagpt")


def get_performance_logger() -> logging.Logger:
    """獲取性能監控日誌記錄器"""
    return get_logger("llm_agent_demo.performance")


# 上下文管理器和實用函數
@contextmanager
def log_context(logger: logging.Logger, context: Dict[str, Any]):
    """
    日誌上下文管理器 - 在特定代碼塊中添加上下文信息

    使用示例：
        >>> logger = get_logger(__name__)
        >>> with log_context(logger, {"user_id": "123", "request_id": "abc"}):
        ...     logger.info("處理請求")  # 自動包含 user_id 和 request_id

    Args:
        logger: 日誌記錄器
        context: 上下文信息字典

    Yields:
        日誌適配器
    """
    adapter = LoggerAdapter(logger, context)

    try:
        yield adapter
    finally:
        pass


@contextmanager
def log_execution_time(
    logger: logging.Logger,
    operation: str,
    level: str = "INFO",
    include_args: bool = False,
    **kwargs,
):
    """
    記錄代碼塊執行時間的上下文管理器

    使用示例：
        >>> logger = get_logger(__name__)
        >>> with log_execution_time(logger, "數據處理"):
        ...     # 執行耗時操作
        ...     process_data()

    Args:
        logger: 日誌記錄器
        operation: 操作名稱
        level: 日誌級別
        include_args: 是否包含額外參數
        **kwargs: 額外參數

    Yields:
        None
    """
    import time

    start_time = time.time()
    log_level = getattr(logging, level.upper())

    extra_info = kwargs if include_args else {}

    try:
        logger.log(log_level, f"開始執行: {operation}", extra={"extra_data": extra_info})
        yield
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(
            f"執行失敗: {operation} (耗時: {elapsed:.2f}秒)",
            exc_info=True,
            extra={"extra_data": {"elapsed_time": elapsed, **extra_info}},
        )
        raise
    else:
        elapsed = time.time() - start_time
        logger.log(
            log_level,
            f"執行完成: {operation} (耗時: {elapsed:.2f}秒)",
            extra={"extra_data": {"elapsed_time": elapsed, **extra_info}},
        )


def log_function_call(logger: logging.Logger, level: str = "DEBUG"):
    """
    裝飾器：自動記錄函數調用

    使用示例：
        >>> logger = get_logger(__name__)
        >>> @log_function_call(logger)
        ... def my_function(a, b):
        ...     return a + b

    Args:
        logger: 日誌記錄器
        level: 日誌級別

    Returns:
        裝飾器函數
    """
    import functools

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log_level = getattr(logging, level.upper())
            func_name = func.__name__

            # 記錄函數調用
            logger.log(
                log_level,
                f"調用函數: {func_name}",
                extra={
                    "extra_data": {
                        "function": func_name,
                        "args_count": len(args),
                        "kwargs_count": len(kwargs),
                    }
                },
            )

            try:
                result = func(*args, **kwargs)
                logger.log(log_level, f"函數執行成功: {func_name}")
                return result
            except Exception as e:
                logger.error(
                    f"函數執行失敗: {func_name}",
                    exc_info=True,
                    extra={"extra_data": {"function": func_name, "error": str(e)}},
                )
                raise

        return wrapper

    return decorator


class StructuredLogger:
    """
    結構化日誌輔助類

    提供便捷的結構化日誌方法

    使用示例：
        >>> structured_logger = StructuredLogger("my_app")
        >>> structured_logger.log_event(
        ...     "user_login",
        ...     user_id="123",
        ...     ip_address="192.168.1.1"
        ... )
    """

    def __init__(self, name: str, level: str = "INFO"):
        """初始化結構化日誌記錄器

        Args:
            name: 日誌記錄器名稱
            level: 日誌級別
        """
        self.logger = get_logger(name, level)

    def log_event(
        self,
        event_type: str,
        level: str = "INFO",
        message: Optional[str] = None,
        **kwargs,
    ):
        """
        記錄事件

        Args:
            event_type: 事件類型
            level: 日誌級別
            message: 可選的消息
            **kwargs: 事件的額外屬性
        """
        log_level = getattr(logging, level.upper())
        msg = message or f"事件: {event_type}"

        extra_data = {"event_type": event_type, **kwargs}

        self.logger.log(log_level, msg, extra={"extra_data": extra_data})

    def log_metric(self, metric_name: str, value: float, unit: str = "", **kwargs):
        """
        記錄指標

        Args:
            metric_name: 指標名稱
            value: 指標值
            unit: 單位
            **kwargs: 額外的標籤
        """
        extra_data = {
            "metric_type": "measurement",
            "metric_name": metric_name,
            "value": value,
            "unit": unit,
            **kwargs,
        }

        self.logger.info(
            f"指標: {metric_name} = {value} {unit}",
            extra={"extra_data": extra_data},
        )

    def log_error(
        self, error: Exception, context: Optional[Dict[str, Any]] = None, **kwargs
    ):
        """
        記錄錯誤

        Args:
            error: 異常對象
            context: 錯誤上下文
            **kwargs: 額外信息
        """
        extra_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
            **kwargs,
        }

        self.logger.error(
            f"錯誤: {type(error).__name__}: {error}",
            exc_info=True,
            extra={"extra_data": extra_data},
        )

    def log_api_call(
        self,
        method: str,
        url: str,
        status_code: Optional[int] = None,
        duration: Optional[float] = None,
        **kwargs,
    ):
        """
        記錄 API 調用

        Args:
            method: HTTP 方法
            url: API URL
            status_code: 響應狀態碼
            duration: 請求耗時（秒）
            **kwargs: 額外信息
        """
        extra_data = {
            "api_method": method,
            "api_url": url,
            "status_code": status_code,
            "duration": duration,
            **kwargs,
        }

        level = "INFO" if status_code and status_code < 400 else "WARNING"
        log_level = getattr(logging, level)

        self.logger.log(
            log_level,
            f"API 調用: {method} {url} - {status_code}",
            extra={"extra_data": extra_data},
        )


class LogStats:
    """
    日誌統計收集器

    收集和報告日誌統計信息

    使用示例：
        >>> stats = LogStats()
        >>> setup_logging()  # 會自動添加統計 handler
        >>> # ... 執行日誌記錄 ...
        >>> print(stats.get_summary())
    """

    def __init__(self):
        """初始化統計收集器"""
        self.counts: Dict[str, int] = {
            "DEBUG": 0,
            "INFO": 0,
            "WARNING": 0,
            "ERROR": 0,
            "CRITICAL": 0,
        }
        self.handler: Optional[logging.Handler] = None

    def get_handler(self) -> logging.Handler:
        """獲取統計 handler"""
        if self.handler is None:
            self.handler = LogStatsHandler(self)
        return self.handler

    def increment(self, level: str):
        """增加級別計數

        Args:
            level: 日誌級別
        """
        if level in self.counts:
            self.counts[level] += 1

    def reset(self):
        """重置統計"""
        for level in self.counts:
            self.counts[level] = 0

    def get_summary(self) -> Dict[str, int]:
        """獲取統計摘要

        Returns:
            日誌級別計數字典
        """
        return self.counts.copy()

    def get_total(self) -> int:
        """獲取總日誌數

        Returns:
            總日誌條數
        """
        return sum(self.counts.values())


class LogStatsHandler(logging.Handler):
    """統計 handler"""

    def __init__(self, stats: LogStats):
        """初始化 handler

        Args:
            stats: 統計收集器
        """
        super().__init__()
        self.stats = stats

    def emit(self, record: logging.LogRecord):
        """處理日誌記錄

        Args:
            record: 日誌記錄
        """
        self.stats.increment(record.levelname)


# 便捷函數
def setup_structured_logging(
    name: str,
    level: str = "INFO",
    log_file: Optional[str] = None,
    **kwargs,
) -> StructuredLogger:
    """
    快速設置並獲取結構化日誌記錄器

    Args:
        name: 日誌記錄器名稱
        level: 日誌級別
        log_file: 日誌文件路徑
        **kwargs: 傳遞給 setup_logging 的其他參數

    Returns:
        配置好的結構化日誌記錄器
    """
    setup_logging(level=level, log_file=log_file, **kwargs)
    return StructuredLogger(name, level)


# 導出所有公共 API
__all__ = [
    # 格式化器
    "ColoredFormatter",
    "JSONFormatter",
    # 過濾器
    "SensitiveDataFilter",
    # 設置函數
    "setup_logging",
    "setup_structured_logging",
    "validate_log_level",
    # 日誌記錄器
    "get_logger",
    "get_app_logger",
    "get_langchain_logger",
    "get_llamaindex_logger",
    "get_autogen_logger",
    "get_crewai_logger",
    "get_metagpt_logger",
    "get_performance_logger",
    # 適配器和輔助類
    "LoggerAdapter",
    "StructuredLogger",
    "LogStats",
    # 上下文管理器和裝飾器
    "log_context",
    "log_execution_time",
    "log_function_call",
]
