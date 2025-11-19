"""日誌管理模組 - 提供結構化日誌記錄功能"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import json


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
    """JSON 格式化器 - 用於結構化日誌"""

    def format(self, record: logging.LogRecord) -> str:
        """格式化為 JSON"""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加異常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # 添加額外欄位
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    json_format: bool = False,
    colorize: bool = True,
) -> None:
    """
    設置日誌系統

    Args:
        level: 日誌級別（DEBUG, INFO, WARNING, ERROR, CRITICAL）
        log_file: 日誌文件路徑（可選）
        json_format: 是否使用 JSON 格式
        colorize: 是否使用彩色輸出（僅控制台）
    """
    # 獲取根日誌記錄器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # 清除現有的 handlers
    root_logger.handlers.clear()

    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))

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
    root_logger.addHandler(console_handler)

    # 文件 handler（如果指定）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(getattr(logging, level.upper()))

        if json_format:
            file_formatter = JSONFormatter()
        else:
            file_formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # 設置第三方庫的日誌級別（避免過多日誌）
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)


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

    def process(self, msg, kwargs):
        """處理日誌消息，添加額外信息"""
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
