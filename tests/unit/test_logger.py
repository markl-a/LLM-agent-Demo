"""日誌管理模組的單元測試"""

import pytest
import logging
import json
import sys
from pathlib import Path
from io import StringIO
from unittest.mock import patch, MagicMock

# 檢查是否安裝了核心模組
try:
    from src.llm_agent_demo.utils.logger import (
        ColoredFormatter,
        JSONFormatter,
        setup_logging,
        get_logger,
        LoggerAdapter,
        get_app_logger,
        get_langchain_logger,
        get_llamaindex_logger,
        get_autogen_logger,
        get_crewai_logger,
        get_metagpt_logger,
    )

    CORE_MODULE_AVAILABLE = True
except ImportError:
    CORE_MODULE_AVAILABLE = False
    pytest.skip("核心模組未安裝", allow_module_level=True)


@pytest.fixture
def clean_logger():
    """清理日誌配置的 fixture"""
    import src.llm_agent_demo.utils.logger as logger_module

    # 保存原始 handlers
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers.copy()
    original_level = root_logger.level
    original_configured = getattr(logger_module, '_logging_configured', False)

    # 重置全局配置標誌以允許重新配置
    logger_module._logging_configured = False

    yield

    # 測試後恢復
    root_logger.handlers.clear()
    for handler in original_handlers:
        root_logger.addHandler(handler)
    root_logger.setLevel(original_level)
    logger_module._logging_configured = original_configured


@pytest.fixture
def temp_log_file(tmp_path):
    """創建臨時日誌文件的 fixture"""
    log_file = tmp_path / "test.log"
    return str(log_file)


@pytest.fixture
def log_record():
    """創建測試用的日誌記錄"""
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="/path/to/file.py",
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None,
    )
    record.module = "test_module"
    record.funcName = "test_function"
    return record


@pytest.mark.unit
class TestColoredFormatter:
    """測試 ColoredFormatter 類"""

    def test_colored_formatter_initialization(self):
        """測試彩色格式化器初始化"""
        formatter = ColoredFormatter(
            "%(levelname)s - %(message)s",
            datefmt="%Y-%m-%d"
        )
        assert formatter is not None
        assert isinstance(formatter, logging.Formatter)

    def test_format_info_level(self, log_record):
        """測試 INFO 級別的格式化"""
        formatter = ColoredFormatter("%(levelname)s - %(message)s")
        log_record.levelname = "INFO"

        formatted = formatter.format(log_record)

        # 檢查是否包含顏色代碼和重置代碼
        assert "\033[32m" in formatted  # 綠色
        assert "\033[0m" in formatted   # 重置
        assert "INFO" in formatted
        assert "Test message" in formatted

    def test_format_error_level(self, log_record):
        """測試 ERROR 級別的格式化"""
        formatter = ColoredFormatter("%(levelname)s - %(message)s")
        log_record.levelname = "ERROR"

        formatted = formatter.format(log_record)

        # 檢查是否包含紅色代碼
        assert "\033[31m" in formatted  # 紅色
        assert "ERROR" in formatted

    def test_format_warning_level(self, log_record):
        """測試 WARNING 級別的格式化"""
        formatter = ColoredFormatter("%(levelname)s - %(message)s")
        log_record.levelname = "WARNING"

        formatted = formatter.format(log_record)

        # 檢查是否包含黃色代碼
        assert "\033[33m" in formatted  # 黃色
        assert "WARNING" in formatted

    def test_format_debug_level(self, log_record):
        """測試 DEBUG 級別的格式化"""
        formatter = ColoredFormatter("%(levelname)s - %(message)s")
        log_record.levelname = "DEBUG"

        formatted = formatter.format(log_record)

        # 檢查是否包含青色代碼
        assert "\033[36m" in formatted  # 青色
        assert "DEBUG" in formatted

    def test_format_critical_level(self, log_record):
        """測試 CRITICAL 級別的格式化"""
        formatter = ColoredFormatter("%(levelname)s - %(message)s")
        log_record.levelname = "CRITICAL"

        formatted = formatter.format(log_record)

        # 檢查是否包含紫色代碼
        assert "\033[35m" in formatted  # 紫色
        assert "CRITICAL" in formatted

    def test_levelname_reset_after_format(self, log_record):
        """測試格式化後 levelname 被重置"""
        formatter = ColoredFormatter("%(levelname)s - %(message)s")
        original_levelname = log_record.levelname

        formatter.format(log_record)

        # 確認 levelname 被重置為原始值
        assert log_record.levelname == original_levelname

    def test_format_with_custom_format_string(self, log_record):
        """測試自定義格式字串"""
        formatter = ColoredFormatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        formatted = formatter.format(log_record)

        assert "test_logger" in formatted
        assert "Test message" in formatted


@pytest.mark.unit
class TestJSONFormatter:
    """測試 JSONFormatter 類"""

    def test_json_formatter_initialization(self):
        """測試 JSON 格式化器初始化"""
        formatter = JSONFormatter()
        assert formatter is not None
        assert isinstance(formatter, logging.Formatter)

    def test_format_basic_log_record(self, log_record):
        """測試基本日誌記錄的 JSON 格式化"""
        formatter = JSONFormatter()

        formatted = formatter.format(log_record)
        log_data = json.loads(formatted)

        # 驗證基本欄位
        assert "timestamp" in log_data
        assert log_data["level"] == "INFO"
        assert log_data["logger"] == "test_logger"
        assert log_data["message"] == "Test message"
        # 新的結構化格式將模組信息放在 source 字典中
        assert "source" in log_data
        assert log_data["source"]["module"] == "test_module"
        assert log_data["source"]["function"] == "test_function"
        assert log_data["source"]["line"] == 42

    def test_format_with_exception(self, log_record):
        """測試包含異常信息的格式化"""
        formatter = JSONFormatter()

        try:
            raise ValueError("Test error")
        except ValueError:
            import sys
            log_record.exc_info = sys.exc_info()

        formatted = formatter.format(log_record)
        log_data = json.loads(formatted)

        # 驗證異常欄位存在（新的結構化格式）
        assert "exception" in log_data
        assert log_data["exception"]["type"] == "ValueError"
        assert log_data["exception"]["message"] == "Test error"
        assert "traceback" in log_data["exception"]
        assert "ValueError" in log_data["exception"]["traceback"]

    def test_format_with_extra_data(self, log_record):
        """測試包含額外數據的格式化"""
        formatter = JSONFormatter()
        log_record.extra_data = {
            "user_id": "123",
            "request_id": "abc-456"
        }

        formatted = formatter.format(log_record)
        log_data = json.loads(formatted)

        # 驗證額外欄位
        assert log_data["user_id"] == "123"
        assert log_data["request_id"] == "abc-456"

    def test_format_with_chinese_characters(self, log_record):
        """測試中文字符的格式化"""
        formatter = JSONFormatter()
        log_record.msg = "測試中文訊息"

        formatted = formatter.format(log_record)
        log_data = json.loads(formatted)

        # 確認中文正確編碼
        assert log_data["message"] == "測試中文訊息"

    def test_json_output_is_valid(self, log_record):
        """測試輸出是有效的 JSON"""
        formatter = JSONFormatter()

        formatted = formatter.format(log_record)

        # 應該能夠解析為 JSON，不拋出異常
        try:
            json.loads(formatted)
            assert True
        except json.JSONDecodeError:
            pytest.fail("輸出不是有效的 JSON")


@pytest.mark.unit
class TestSetupLogging:
    """測試 setup_logging 函數"""

    def test_setup_logging_default(self, clean_logger):
        """測試默認配置"""
        setup_logging()

        root_logger = logging.getLogger()

        # 驗證默認級別為 INFO
        assert root_logger.level == logging.INFO
        # 驗證至少有一個 handler
        assert len(root_logger.handlers) > 0

    def test_setup_logging_debug_level(self, clean_logger):
        """測試 DEBUG 級別設置"""
        setup_logging(level="DEBUG")

        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG

    def test_setup_logging_warning_level(self, clean_logger):
        """測試 WARNING 級別設置"""
        setup_logging(level="WARNING")

        root_logger = logging.getLogger()
        assert root_logger.level == logging.WARNING

    def test_setup_logging_error_level(self, clean_logger):
        """測試 ERROR 級別設置"""
        setup_logging(level="ERROR")

        root_logger = logging.getLogger()
        assert root_logger.level == logging.ERROR

    def test_setup_logging_critical_level(self, clean_logger):
        """測試 CRITICAL 級別設置"""
        setup_logging(level="CRITICAL")

        root_logger = logging.getLogger()
        assert root_logger.level == logging.CRITICAL

    def test_setup_logging_with_file(self, clean_logger, temp_log_file):
        """測試文件日誌配置"""
        setup_logging(level="INFO", log_file=temp_log_file)

        root_logger = logging.getLogger()

        # 驗證有文件 handler
        file_handlers = [h for h in root_logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) > 0

        # 寫入測試日誌
        test_logger = logging.getLogger("test")
        test_logger.info("Test log message")

        # 確保日誌被寫入
        for handler in file_handlers:
            handler.flush()

        # 驗證文件存在且有內容
        assert Path(temp_log_file).exists()
        content = Path(temp_log_file).read_text()
        assert "Test log message" in content

    def test_setup_logging_with_json_format(self, clean_logger):
        """測試 JSON 格式配置"""
        setup_logging(level="INFO", json_format=True)

        root_logger = logging.getLogger()
        handlers = root_logger.handlers

        # 驗證 handler 使用 JSON formatter
        assert len(handlers) > 0
        for handler in handlers:
            assert isinstance(handler.formatter, JSONFormatter)

    def test_setup_logging_with_colorize(self, clean_logger):
        """測試彩色輸出配置"""
        setup_logging(level="INFO", colorize=True)

        root_logger = logging.getLogger()
        console_handlers = [h for h in root_logger.handlers if isinstance(h, logging.StreamHandler)]

        # 驗證有控制台 handler 使用 ColoredFormatter
        assert len(console_handlers) > 0
        assert any(isinstance(h.formatter, ColoredFormatter) for h in console_handlers)

    def test_setup_logging_without_colorize(self, clean_logger):
        """測試無彩色輸出配置"""
        setup_logging(level="INFO", colorize=False)

        root_logger = logging.getLogger()
        console_handlers = [h for h in root_logger.handlers if isinstance(h, logging.StreamHandler)]

        # 驗證沒有使用 ColoredFormatter
        assert len(console_handlers) > 0
        assert all(not isinstance(h.formatter, ColoredFormatter) for h in console_handlers)

    def test_setup_logging_clears_existing_handlers(self, clean_logger):
        """測試清除現有 handlers"""
        root_logger = logging.getLogger()

        # 添加一個測試 handler
        test_handler = logging.StreamHandler()
        root_logger.addHandler(test_handler)
        initial_count = len(root_logger.handlers)

        # 重新設置
        setup_logging()

        # 驗證 handlers 被重置
        assert test_handler not in root_logger.handlers

    def test_setup_logging_creates_log_directory(self, clean_logger, tmp_path):
        """測試自動創建日誌目錄"""
        log_file = tmp_path / "logs" / "app" / "test.log"

        setup_logging(level="INFO", log_file=str(log_file))

        # 驗證目錄被創建
        assert log_file.parent.exists()

    def test_setup_logging_third_party_loggers(self, clean_logger):
        """測試第三方庫日誌級別設置"""
        setup_logging(level="DEBUG")

        # 驗證第三方庫的日誌級別被設置為 WARNING
        assert logging.getLogger("httpx").level == logging.WARNING
        assert logging.getLogger("httpcore").level == logging.WARNING
        assert logging.getLogger("openai").level == logging.WARNING
        assert logging.getLogger("anthropic").level == logging.WARNING
        assert logging.getLogger("chromadb").level == logging.WARNING

    def test_setup_logging_with_file_and_json(self, clean_logger, temp_log_file):
        """測試文件日誌使用 JSON 格式"""
        setup_logging(level="INFO", log_file=temp_log_file, json_format=True)

        # 寫入測試日誌
        test_logger = logging.getLogger("test")
        test_logger.info("Test JSON log")

        # 確保日誌被寫入
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            handler.flush()

        # 驗證文件內容是 JSON 格式
        content = Path(temp_log_file).read_text().strip()
        log_data = json.loads(content)
        assert log_data["message"] == "Test JSON log"


@pytest.mark.unit
class TestGetLogger:
    """測試 get_logger 函數"""

    def test_get_logger_basic(self):
        """測試基本的 logger 獲取"""
        logger = get_logger("test_logger")

        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"

    def test_get_logger_with_level(self):
        """測試帶級別的 logger 獲取"""
        logger = get_logger("test_logger", level="DEBUG")

        assert logger.level == logging.DEBUG

    def test_get_logger_with_different_levels(self):
        """測試不同級別設置"""
        logger_info = get_logger("logger_info", level="INFO")
        logger_debug = get_logger("logger_debug", level="DEBUG")
        logger_error = get_logger("logger_error", level="ERROR")

        assert logger_info.level == logging.INFO
        assert logger_debug.level == logging.DEBUG
        assert logger_error.level == logging.ERROR

    def test_get_logger_same_name_returns_same_instance(self):
        """測試相同名稱返回相同實例"""
        logger1 = get_logger("same_logger")
        logger2 = get_logger("same_logger")

        assert logger1 is logger2

    def test_get_logger_without_level(self):
        """測試不指定級別的 logger"""
        logger = get_logger("test_logger_no_level")

        # 應該使用根 logger 的級別
        assert logger is not None


@pytest.mark.unit
class TestLoggerAdapter:
    """測試 LoggerAdapter 類"""

    def test_logger_adapter_initialization(self):
        """測試 LoggerAdapter 初始化"""
        logger = get_logger("test_logger")
        extra = {"user_id": "123", "request_id": "abc"}

        adapter = LoggerAdapter(logger, extra)

        assert adapter is not None
        assert adapter.logger is logger
        assert adapter.extra == extra

    def test_logger_adapter_process_message(self):
        """測試消息處理"""
        logger = get_logger("test_logger")
        extra = {"user_id": "123"}
        adapter = LoggerAdapter(logger, extra)

        msg, kwargs = adapter.process("Test message", {})

        assert msg == "Test message"
        assert "extra" in kwargs
        assert "extra_data" in kwargs["extra"]
        assert kwargs["extra"]["extra_data"] == extra

    def test_logger_adapter_with_existing_extra(self):
        """測試已有 extra 參數的情況"""
        logger = get_logger("test_logger")
        adapter_extra = {"user_id": "123"}
        adapter = LoggerAdapter(logger, adapter_extra)

        existing_kwargs = {"extra": {"other_field": "value"}}
        msg, kwargs = adapter.process("Test message", existing_kwargs)

        # 驗證 extra_data 被添加
        assert "extra_data" in kwargs["extra"]
        assert kwargs["extra"]["extra_data"] == adapter_extra
        # 驗證原有的 extra 也保留
        assert kwargs["extra"]["other_field"] == "value"

    def test_logger_adapter_logging_with_context(self, clean_logger):
        """測試帶上下文的日誌記錄"""
        # 使用自定義 handler 來捕獲日誌
        from io import StringIO
        import sys

        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(JSONFormatter())

        logger = get_logger("test_logger")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        adapter = LoggerAdapter(logger, {"user_id": "123", "request_id": "abc"})
        adapter.info("Processing request")

        # 獲取日誌輸出
        log_output = log_stream.getvalue()
        assert len(log_output) > 0

        # 驗證 JSON 格式和上下文信息
        log_data = json.loads(log_output.strip())
        assert log_data["message"] == "Processing request"
        assert log_data["user_id"] == "123"
        assert log_data["request_id"] == "abc"

    def test_logger_adapter_multiple_contexts(self):
        """測試多個上下文"""
        logger = get_logger("test_logger")

        adapter1 = LoggerAdapter(logger, {"user_id": "123"})
        adapter2 = LoggerAdapter(logger, {"session_id": "xyz"})

        msg1, kwargs1 = adapter1.process("Message 1", {})
        msg2, kwargs2 = adapter2.process("Message 2", {})

        assert kwargs1["extra"]["extra_data"]["user_id"] == "123"
        assert kwargs2["extra"]["extra_data"]["session_id"] == "xyz"


@pytest.mark.unit
class TestPredefinedLoggers:
    """測試預定義的日誌記錄器"""

    def test_get_app_logger(self):
        """測試獲取應用程式主日誌記錄器"""
        logger = get_app_logger()

        assert logger is not None
        assert logger.name == "llm_agent_demo"

    def test_get_langchain_logger(self):
        """測試獲取 LangChain 日誌記錄器"""
        logger = get_langchain_logger()

        assert logger is not None
        assert logger.name == "llm_agent_demo.langchain"

    def test_get_llamaindex_logger(self):
        """測試獲取 LlamaIndex 日誌記錄器"""
        logger = get_llamaindex_logger()

        assert logger is not None
        assert logger.name == "llm_agent_demo.llamaindex"

    def test_get_autogen_logger(self):
        """測試獲取 AutoGen 日誌記錄器"""
        logger = get_autogen_logger()

        assert logger is not None
        assert logger.name == "llm_agent_demo.autogen"

    def test_get_crewai_logger(self):
        """測試獲取 CrewAI 日誌記錄器"""
        logger = get_crewai_logger()

        assert logger is not None
        assert logger.name == "llm_agent_demo.crewai"

    def test_get_metagpt_logger(self):
        """測試獲取 MetaGPT 日誌記錄器"""
        logger = get_metagpt_logger()

        assert logger is not None
        assert logger.name == "llm_agent_demo.metagpt"

    def test_all_predefined_loggers_are_unique(self):
        """測試所有預定義 logger 都是唯一的"""
        loggers = [
            get_app_logger(),
            get_langchain_logger(),
            get_llamaindex_logger(),
            get_autogen_logger(),
            get_crewai_logger(),
            get_metagpt_logger(),
        ]

        # 驗證所有 logger 的名稱都不同
        names = [logger.name for logger in loggers]
        assert len(names) == len(set(names))

    def test_predefined_loggers_hierarchy(self):
        """測試預定義 logger 的層級關係"""
        app_logger = get_app_logger()
        langchain_logger = get_langchain_logger()

        # 驗證 langchain logger 是 app logger 的子 logger
        assert langchain_logger.name.startswith(app_logger.name)


@pytest.mark.unit
class TestLoggingIntegration:
    """測試日誌系統的集成功能"""

    def test_logging_output_to_console(self, clean_logger, temp_log_file):
        """測試控制台輸出"""
        setup_logging(level="INFO", log_file=temp_log_file)
        logger = get_logger("test")

        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")

        # 確保日誌被寫入
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            handler.flush()

        # 驗證所有消息都被記錄到文件
        content = Path(temp_log_file).read_text()
        assert "Test info message" in content
        assert "Test warning message" in content
        assert "Test error message" in content

    def test_logging_level_filtering(self, clean_logger, temp_log_file):
        """測試日誌級別過濾"""
        setup_logging(level="WARNING", log_file=temp_log_file)
        logger = get_logger("test")

        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        # 確保日誌被寫入
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            handler.flush()

        # 只有 WARNING 及以上級別的消息被記錄
        content = Path(temp_log_file).read_text()
        assert "Debug message" not in content
        assert "Info message" not in content
        assert "Warning message" in content
        assert "Error message" in content

    def test_logging_with_exception_info(self, clean_logger, temp_log_file):
        """測試異常信息記錄"""
        setup_logging(level="ERROR", log_file=temp_log_file)
        logger = get_logger("test")

        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.exception("An error occurred")

        # 確保日誌被寫入
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            handler.flush()

        # 驗證異常信息被記錄
        content = Path(temp_log_file).read_text()
        assert "An error occurred" in content
        assert "ValueError" in content
        assert "Test exception" in content

    def test_logging_formatting_consistency(self, clean_logger, temp_log_file):
        """測試日誌格式一致性"""
        setup_logging(level="INFO", log_file=temp_log_file, colorize=False)
        logger = get_logger("test.module")

        logger.info("Test message 1")
        logger.warning("Test message 2")
        logger.error("Test message 3")

        # 確保日誌被寫入
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            handler.flush()

        # 驗證格式一致性
        content = Path(temp_log_file).read_text()
        lines = content.strip().split("\n")

        # 每行都應該包含時間戳、級別、logger 名稱和消息
        for line in lines:
            assert "|" in line  # 使用 | 分隔
            assert "test.module" in line

    def test_concurrent_logging(self, clean_logger, temp_log_file):
        """測試並發日誌記錄"""
        import threading

        setup_logging(level="INFO", log_file=temp_log_file)

        def log_messages(thread_id):
            logger = get_logger(f"thread_{thread_id}")
            for i in range(10):
                logger.info(f"Thread {thread_id} - Message {i}")

        threads = []
        for i in range(5):
            thread = threading.Thread(target=log_messages, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # 確保日誌被寫入
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            handler.flush()

        # 驗證所有消息都被記錄
        content = Path(temp_log_file).read_text()
        lines = content.strip().split("\n")
        assert len(lines) == 50  # 5 threads * 10 messages


@pytest.mark.unit
class TestEdgeCases:
    """測試邊緣情況和異常處理"""

    def test_invalid_log_level_string(self, clean_logger):
        """測試無效的日誌級別字串"""
        # 新的實現使用更合適的 ValueError 而不是 AttributeError
        with pytest.raises(ValueError, match="無效的日誌級別"):
            setup_logging(level="INVALID_LEVEL")

    def test_empty_log_message(self, clean_logger, temp_log_file):
        """測試空日誌消息"""
        setup_logging(level="INFO", log_file=temp_log_file)
        logger = get_logger("test")

        logger.info("")

        # 確保日誌被寫入
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            handler.flush()

        # 空消息也應該被記錄
        content = Path(temp_log_file).read_text()
        assert len(content) > 0  # 文件不為空（至少有時間戳等信息）

    def test_log_with_special_characters(self, clean_logger, temp_log_file):
        """測試特殊字符的日誌"""
        setup_logging(level="INFO", log_file=temp_log_file)
        logger = get_logger("test")

        special_message = "Test !@#$%^&*() <> {} [] | \\ / ? ~ `"
        logger.info(special_message)

        # 確保日誌被寫入
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            handler.flush()

        # 驗證特殊字符被正確記錄
        content = Path(temp_log_file).read_text()
        assert special_message in content

    def test_log_with_newlines(self, clean_logger, temp_log_file):
        """測試包含換行符的日誌"""
        setup_logging(level="INFO", log_file=temp_log_file)
        logger = get_logger("test")

        multiline_message = "Line 1\nLine 2\nLine 3"
        logger.info(multiline_message)

        # 確保日誌被寫入
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            handler.flush()

        # 驗證換行符被保留
        content = Path(temp_log_file).read_text()
        assert "Line 1" in content
        assert "Line 2" in content
        assert "Line 3" in content

    def test_log_with_unicode_characters(self, clean_logger, temp_log_file):
        """測試 Unicode 字符的日誌"""
        setup_logging(level="INFO", log_file=temp_log_file)
        logger = get_logger("test")

        unicode_message = "測試中文 🎉 émojis ñ ü"
        logger.info(unicode_message)

        # 確保日誌被寫入
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            handler.flush()

        # 驗證 Unicode 字符被正確記錄
        content = Path(temp_log_file).read_text(encoding="utf-8")
        assert "測試中文" in content

    def test_logger_adapter_with_none_extra(self):
        """測試 LoggerAdapter 使用 None 作為 extra"""
        logger = get_logger("test")

        # 即使 extra 是 None，也不應該崩潰
        adapter = LoggerAdapter(logger, None)
        msg, kwargs = adapter.process("Test", {})

        assert "extra" in kwargs
        assert kwargs["extra"]["extra_data"] is None

    def test_json_formatter_with_very_long_message(self, log_record):
        """測試 JSON 格式化器處理超長消息"""
        formatter = JSONFormatter()

        # 創建一個很長的消息
        long_message = "A" * 10000
        log_record.msg = long_message

        formatted = formatter.format(log_record)
        log_data = json.loads(formatted)

        # 驗證長消息被正確處理
        assert log_data["message"] == long_message

    def test_setup_logging_multiple_times(self, clean_logger):
        """測試多次調用 setup_logging（使用 force_reconfigure）"""
        setup_logging(level="INFO")
        setup_logging(level="DEBUG", force_reconfigure=True)
        setup_logging(level="WARNING", force_reconfigure=True)

        root_logger = logging.getLogger()

        # 最後一次調用應該生效
        assert root_logger.level == logging.WARNING

    def test_colored_formatter_with_unknown_level(self, log_record):
        """測試 ColoredFormatter 處理未知級別"""
        formatter = ColoredFormatter("%(levelname)s - %(message)s")
        log_record.levelname = "CUSTOM_LEVEL"

        # 不應該崩潰，只是不添加顏色
        formatted = formatter.format(log_record)

        assert "CUSTOM_LEVEL" in formatted
        # 不應該包含顏色代碼（因為級別未知）
        assert formatted.count("\033[") == 0
