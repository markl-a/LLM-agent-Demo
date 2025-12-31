"""
統一日誌配置模組

此模組提供了一個統一的日誌配置系統，支持：
- 控制台和文件輸出
- 彩色日誌顯示（使用 rich）
- 不同級別的格式化
- JSON 格式日誌選項
- 日誌輪轉配置
- 靈活的配置選項

作者: LLM Agent Demo
日期: 2025-12-31
"""

import logging
import logging.handlers
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from rich.console import Console
    from rich.logging import RichHandler
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class JSONFormatter(logging.Formatter):
    """JSON 格式化器

    將日誌記錄格式化為 JSON 格式，便於日誌分析和處理
    """

    def format(self, record: logging.LogRecord) -> str:
        """格式化日誌記錄為 JSON

        Args:
            record: 日誌記錄對象

        Returns:
            JSON 格式的日誌字符串
        """
        log_data: Dict[str, Any] = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # 添加異常信息
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # 添加額外的字段
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data

        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """彩色格式化器（非 Rich 版本）

    當 Rich 不可用時，使用 ANSI 顏色碼提供基本的彩色輸出
    """

    # ANSI 顏色碼
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 綠色
        'WARNING': '\033[33m',    # 黃色
        'ERROR': '\033[31m',      # 紅色
        'CRITICAL': '\033[35m',   # 紫色
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        """格式化日誌記錄並添加顏色

        Args:
            record: 日誌記錄對象

        Returns:
            帶有 ANSI 顏色碼的日誌字符串
        """
        # 保存原始級別名稱
        levelname = record.levelname

        # 添加顏色
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"

        # 格式化消息
        result = super().format(record)

        # 恢復原始級別名稱
        record.levelname = levelname

        return result


class LogConfig:
    """日誌配置類

    提供統一的日誌配置接口，支持多種輸出方式和格式
    """

    # 默認配置
    DEFAULT_LEVEL = logging.INFO
    DEFAULT_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    DEFAULT_LOG_DIR = 'logs'
    DEFAULT_LOG_FILE = 'app.log'

    def __init__(
        self,
        name: str = 'app',
        level: int = DEFAULT_LEVEL,
        log_dir: Optional[str] = None,
        log_file: Optional[str] = None,
        console_output: bool = True,
        file_output: bool = True,
        json_format: bool = False,
        use_rich: bool = True,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        encoding: str = 'utf-8',
    ):
        """初始化日誌配置

        Args:
            name: 日誌器名稱
            level: 日誌級別
            log_dir: 日誌目錄路徑
            log_file: 日誌文件名
            console_output: 是否輸出到控制台
            file_output: 是否輸出到文件
            json_format: 是否使用 JSON 格式
            use_rich: 是否使用 Rich 進行彩色輸出
            max_bytes: 單個日誌文件最大大小（字節）
            backup_count: 保留的備份文件數量
            encoding: 文件編碼
        """
        self.name = name
        self.level = level
        self.log_dir = Path(log_dir or self.DEFAULT_LOG_DIR)
        self.log_file = log_file or self.DEFAULT_LOG_FILE
        self.console_output = console_output
        self.file_output = file_output
        self.json_format = json_format
        self.use_rich = use_rich and RICH_AVAILABLE
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.encoding = encoding

        # 確保日誌目錄存在
        if self.file_output:
            self.log_dir.mkdir(parents=True, exist_ok=True)

    def get_console_handler(self) -> logging.Handler:
        """獲取控制台處理器

        Returns:
            配置好的控制台處理器
        """
        if self.use_rich:
            # 使用 Rich 的彩色處理器
            console = Console()
            handler = RichHandler(
                console=console,
                rich_tracebacks=True,
                tracebacks_show_locals=True,
                show_time=True,
                show_level=True,
                show_path=True,
            )
            handler.setFormatter(logging.Formatter('%(message)s'))
        else:
            # 使用標準控制台處理器
            handler = logging.StreamHandler(sys.stdout)

            if self.json_format:
                handler.setFormatter(JSONFormatter())
            else:
                # 使用彩色格式化器
                formatter = ColoredFormatter(
                    fmt=self.DEFAULT_FORMAT,
                    datefmt=self.DEFAULT_DATE_FORMAT,
                )
                handler.setFormatter(formatter)

        handler.setLevel(self.level)
        return handler

    def get_file_handler(self) -> logging.Handler:
        """獲取文件處理器（帶輪轉功能）

        Returns:
            配置好的文件處理器
        """
        log_path = self.log_dir / self.log_file

        # 使用輪轉文件處理器
        handler = logging.handlers.RotatingFileHandler(
            filename=log_path,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding=self.encoding,
        )

        if self.json_format:
            handler.setFormatter(JSONFormatter())
        else:
            formatter = logging.Formatter(
                fmt=self.DEFAULT_FORMAT,
                datefmt=self.DEFAULT_DATE_FORMAT,
            )
            handler.setFormatter(formatter)

        handler.setLevel(self.level)
        return handler

    def get_time_rotating_handler(
        self,
        when: str = 'midnight',
        interval: int = 1,
    ) -> logging.Handler:
        """獲取時間輪轉文件處理器

        Args:
            when: 輪轉時間單位 ('S', 'M', 'H', 'D', 'midnight', 'W0'-'W6')
            interval: 輪轉間隔

        Returns:
            配置好的時間輪轉文件處理器
        """
        log_path = self.log_dir / self.log_file

        handler = logging.handlers.TimedRotatingFileHandler(
            filename=log_path,
            when=when,
            interval=interval,
            backupCount=self.backup_count,
            encoding=self.encoding,
        )

        if self.json_format:
            handler.setFormatter(JSONFormatter())
        else:
            formatter = logging.Formatter(
                fmt=self.DEFAULT_FORMAT,
                datefmt=self.DEFAULT_DATE_FORMAT,
            )
            handler.setFormatter(formatter)

        handler.setLevel(self.level)
        return handler

    def setup_logger(
        self,
        logger: Optional[logging.Logger] = None,
        use_time_rotation: bool = False,
        **rotation_kwargs
    ) -> logging.Logger:
        """設置並配置日誌器

        Args:
            logger: 現有的日誌器對象（如果為 None 則創建新的）
            use_time_rotation: 是否使用時間輪轉而非大小輪轉
            **rotation_kwargs: 傳遞給時間輪轉處理器的參數

        Returns:
            配置好的日誌器對象
        """
        if logger is None:
            logger = logging.getLogger(self.name)

        # 設置日誌級別
        logger.setLevel(self.level)

        # 移除現有的處理器（避免重複）
        logger.handlers.clear()

        # 添加控制台處理器
        if self.console_output:
            logger.addHandler(self.get_console_handler())

        # 添加文件處理器
        if self.file_output:
            if use_time_rotation:
                logger.addHandler(self.get_time_rotating_handler(**rotation_kwargs))
            else:
                logger.addHandler(self.get_file_handler())

        # 防止日誌傳播到父級
        logger.propagate = False

        return logger


def setup_logging(
    name: str = 'app',
    level: int = logging.INFO,
    **kwargs
) -> logging.Logger:
    """快速設置日誌系統的便捷函數

    Args:
        name: 日誌器名稱
        level: 日誌級別
        **kwargs: 傳遞給 LogConfig 的其他參數

    Returns:
        配置好的日誌器對象

    Example:
        >>> logger = setup_logging('my_app', level=logging.DEBUG)
        >>> logger.info('應用程序已啟動')
    """
    config = LogConfig(name=name, level=level, **kwargs)
    return config.setup_logger()


def get_log_levels() -> Dict[str, int]:
    """獲取所有可用的日誌級別

    Returns:
        日誌級別名稱到級別值的映射
    """
    return {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }


def set_level_from_string(logger: logging.Logger, level_str: str) -> None:
    """從字符串設置日誌級別

    Args:
        logger: 日誌器對象
        level_str: 日誌級別字符串（不區分大小寫）

    Raises:
        ValueError: 如果級別字符串無效
    """
    levels = get_log_levels()
    level_str = level_str.upper()

    if level_str not in levels:
        raise ValueError(
            f"無效的日誌級別: {level_str}. "
            f"可用級別: {', '.join(levels.keys())}"
        )

    logger.setLevel(levels[level_str])


# 預配置的日誌配置
def get_development_logger(name: str = 'dev') -> logging.Logger:
    """獲取開發環境日誌器

    特點：
    - DEBUG 級別
    - 彩色控制台輸出
    - 詳細的日誌格式

    Args:
        name: 日誌器名稱

    Returns:
        配置好的開發環境日誌器
    """
    return setup_logging(
        name=name,
        level=logging.DEBUG,
        console_output=True,
        file_output=False,
        use_rich=True,
    )


def get_production_logger(
    name: str = 'prod',
    log_dir: str = 'logs',
) -> logging.Logger:
    """獲取生產環境日誌器

    特點：
    - INFO 級別
    - JSON 格式
    - 文件輪轉
    - 同時輸出到控制台和文件

    Args:
        name: 日誌器名稱
        log_dir: 日誌目錄

    Returns:
        配置好的生產環境日誌器
    """
    return setup_logging(
        name=name,
        level=logging.INFO,
        log_dir=log_dir,
        console_output=True,
        file_output=True,
        json_format=True,
        use_rich=False,
    )


def get_testing_logger(name: str = 'test') -> logging.Logger:
    """獲取測試環境日誌器

    特點：
    - WARNING 級別（減少測試輸出噪音）
    - 僅控制台輸出
    - 簡潔格式

    Args:
        name: 日誌器名稱

    Returns:
        配置好的測試環境日誌器
    """
    return setup_logging(
        name=name,
        level=logging.WARNING,
        console_output=True,
        file_output=False,
        use_rich=False,
    )


if __name__ == '__main__':
    # 測試不同的日誌配置
    print("=== 開發環境日誌器測試 ===")
    dev_logger = get_development_logger()
    dev_logger.debug("這是調試消息")
    dev_logger.info("這是信息消息")
    dev_logger.warning("這是警告消息")
    dev_logger.error("這是錯誤消息")

    print("\n=== 生產環境日誌器測試 ===")
    prod_logger = get_production_logger()
    prod_logger.info("生產環境信息")
    prod_logger.error("生產環境錯誤")

    print("\n=== 自定義配置測試 ===")
    custom_logger = setup_logging(
        name='custom',
        level=logging.DEBUG,
        log_dir='custom_logs',
        log_file='custom.log',
        json_format=False,
        use_rich=True,
    )
    custom_logger.info("自定義日誌配置測試")
