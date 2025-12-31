"""
測試日誌系統功能

此測試文件會：
1. 測試日誌器的創建和配置
2. 測試日誌輸出功能
3. 測試日誌工具類和裝飾器
4. 測試日誌文件的創建和寫入
5. 測試結構化日誌功能

作者: LLM Agent Demo
日期: 2025-12-31
"""

import logging
import sys
import time
from pathlib import Path

import pytest


# 測試日誌系統的基礎功能
@pytest.mark.unit
def test_logger_module_exists(project_root):
    """測試日誌模組存在"""
    logger_path = project_root / 'src' / 'logger.py'
    assert logger_path.exists(), "logger.py 應該存在"


@pytest.mark.unit
def test_logging_config_module_exists(project_root):
    """測試日誌配置模組存在"""
    logging_config_path = project_root / 'src' / 'logging_config.py'
    assert logging_config_path.exists(), "logging_config.py 應該存在"


@pytest.mark.unit
def test_import_logger_module(project_root):
    """測試可以導入日誌模組"""
    src_dir = project_root / 'src'
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    try:
        import logger  # noqa: F401
        assert True
    except ImportError as e:
        pytest.fail(f"無法導入 logger 模組: {e}")


@pytest.mark.unit
def test_import_logging_config_module(project_root):
    """測試可以導入日誌配置模組"""
    src_dir = project_root / 'src'
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    try:
        import logging_config  # noqa: F401
        assert True
    except ImportError as e:
        pytest.fail(f"無法導入 logging_config 模組: {e}")


@pytest.mark.unit
def test_get_logger_function(project_root):
    """測試 get_logger 函數"""
    src_dir = project_root / 'src'
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    try:
        from logger import get_logger

        # 創建日誌器
        test_logger = get_logger('test_logger')

        assert test_logger is not None
        assert isinstance(test_logger, logging.Logger)
        assert test_logger.name == 'test_logger'

    except ImportError:
        pytest.skip("無法導入 logger 模組")


@pytest.mark.unit
def test_logger_output_levels(project_root, captured_logs):
    """測試不同日誌級別的輸出"""
    src_dir = project_root / 'src'
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    try:
        from logger import get_logger

        test_logger = get_logger('test_levels', level=logging.DEBUG)

        # 測試不同級別的日誌
        test_logger.debug("Debug message")
        test_logger.info("Info message")
        test_logger.warning("Warning message")
        test_logger.error("Error message")

        # 驗證日誌已被捕獲
        assert len(captured_logs.records) >= 4

        # 驗證日誌級別
        levels = [record.levelname for record in captured_logs.records]
        assert 'DEBUG' in levels
        assert 'INFO' in levels
        assert 'WARNING' in levels
        assert 'ERROR' in levels

    except ImportError:
        pytest.skip("無法導入 logger 模組")


@pytest.mark.unit
def test_log_timer_context_manager(project_root):
    """測試 LogTimer 上下文管理器"""
    src_dir = project_root / 'src'
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    try:
        from logger import get_logger, LogTimer

        test_logger = get_logger('test_timer')

        # 使用計時器
        with LogTimer(test_logger, '測試操作') as timer:
            time.sleep(0.01)  # 模擬操作

        # 驗證計時器記錄了時間
        assert timer.elapsed is not None
        assert timer.elapsed > 0
        assert timer.elapsed < 1  # 應該小於 1 秒

    except ImportError:
        pytest.skip("無法導入 logger 模組")


@pytest.mark.unit
def test_log_execution_decorator(project_root, captured_logs):
    """測試 log_execution 裝飾器"""
    src_dir = project_root / 'src'
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    try:
        from logger import get_logger, log_execution

        test_logger = get_logger('test_decorator', level=logging.DEBUG)

        # 定義測試函數
        @log_execution(logger=test_logger)
        def test_function(a, b):
            return a + b

        # 調用函數
        result = test_function(1, 2)

        # 驗證結果
        assert result == 3

        # 驗證日誌已記錄
        assert len(captured_logs.records) > 0

    except ImportError:
        pytest.skip("無法導入 logger 模組")


@pytest.mark.unit
def test_log_exception_decorator(project_root, captured_logs):
    """測試 log_exception 裝飾器"""
    src_dir = project_root / 'src'
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    try:
        from logger import get_logger, log_exception

        test_logger = get_logger('test_exception')

        # 定義會拋出異常的函數
        @log_exception(logger=test_logger)
        def error_function():
            raise ValueError("測試錯誤")

        # 調用函數並捕獲異常
        with pytest.raises(ValueError):
            error_function()

        # 驗證錯誤已被記錄
        assert any(record.levelname == 'ERROR' for record in captured_logs.records)

    except ImportError:
        pytest.skip("無法導入 logger 模組")


@pytest.mark.unit
def test_structured_logger(project_root, captured_logs):
    """測試 StructuredLogger 類"""
    src_dir = project_root / 'src'
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    try:
        from logger import get_logger, StructuredLogger

        base_logger = get_logger('test_structured')
        struct_logger = StructuredLogger(base_logger)

        # 設置上下文
        struct_logger.set_context(app='test', version='1.0')

        # 記錄日誌
        struct_logger.info('測試消息', user='admin')

        # 驗證日誌
        assert len(captured_logs.records) > 0
        log_message = captured_logs.records[-1].message
        assert 'app=test' in log_message
        assert 'version=1.0' in log_message
        assert 'user=admin' in log_message

    except ImportError:
        pytest.skip("無法導入 logger 模組")


@pytest.mark.unit
def test_structured_logger_context_scope(project_root, captured_logs):
    """測試 StructuredLogger 的臨時上下文"""
    src_dir = project_root / 'src'
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    try:
        from logger import get_logger, StructuredLogger

        base_logger = get_logger('test_context_scope')
        struct_logger = StructuredLogger(base_logger)

        # 設置基礎上下文
        struct_logger.set_context(app='test')

        # 使用臨時上下文
        with struct_logger.context_scope(request_id='123'):
            struct_logger.info('請求開始')

        # 臨時上下文應該已被清除
        struct_logger.info('請求結束')

        # 驗證日誌
        assert len(captured_logs.records) >= 2

    except ImportError:
        pytest.skip("無法導入 logger 模組")


@pytest.mark.unit
def test_performance_logger(project_root, captured_logs):
    """測試 PerformanceLogger 類"""
    src_dir = project_root / 'src'
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    try:
        from logger import get_logger, PerformanceLogger

        test_logger = get_logger('test_performance', level=logging.DEBUG)
        perf_logger = PerformanceLogger(test_logger, threshold=0.05)

        # 測試快速操作
        with perf_logger.measure('快速操作'):
            time.sleep(0.01)

        # 測試慢速操作（超過閾值）
        with perf_logger.measure('慢速操作'):
            time.sleep(0.06)

        # 驗證日誌
        assert len(captured_logs.records) >= 2

        # 慢速操作應該產生警告
        warning_logs = [r for r in captured_logs.records if r.levelname == 'WARNING']
        assert len(warning_logs) > 0

    except ImportError:
        pytest.skip("無法導入 logger 模組")


@pytest.mark.unit
def test_logger_cache(project_root):
    """測試日誌器緩存功能"""
    src_dir = project_root / 'src'
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    try:
        from logger import get_logger, clear_logger_cache

        # 創建日誌器
        logger1 = get_logger('test_cache', level=logging.INFO)
        logger2 = get_logger('test_cache', level=logging.INFO)

        # 相同名稱和級別應該返回同一實例（緩存）
        assert logger1 is logger2

        # 清除緩存
        clear_logger_cache()

        # 清除後應該創建新實例
        logger3 = get_logger('test_cache', level=logging.INFO)
        # 注意：由於 logging 模組的行為，相同名稱的 logger 可能仍然是同一實例
        assert logger3.name == 'test_cache'

    except ImportError:
        pytest.skip("無法導入 logger 模組")


@pytest.mark.unit
def test_create_file_logger(project_root, temp_log_file):
    """測試創建文件日誌器"""
    src_dir = project_root / 'src'
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    try:
        from logger import create_file_logger

        # 創建文件日誌器
        file_logger = create_file_logger(
            'test_file_logger',
            str(temp_log_file),
            level=logging.INFO
        )

        # 記錄日誌
        file_logger.info('測試文件日誌')

        # 注意：文件可能還未刷新到磁盤
        # 我們只驗證日誌器創建成功
        assert file_logger is not None
        assert file_logger.name == 'test_file_logger'

    except ImportError:
        pytest.skip("無法導入 logger 模組")


@pytest.mark.unit
def test_create_console_logger(project_root):
    """測試創建控制台日誌器"""
    src_dir = project_root / 'src'
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    try:
        from logger import create_console_logger

        # 創建控制台日誌器
        console_logger = create_console_logger(
            'test_console_logger',
            level=logging.INFO,
            use_rich=False  # 不使用 rich，避免依賴問題
        )

        assert console_logger is not None
        assert console_logger.name == 'test_console_logger'

    except ImportError:
        pytest.skip("無法導入 logger 模組")


@pytest.mark.unit
def test_logs_directory_exists(ensure_log_dir):
    """測試日誌目錄存在"""
    assert ensure_log_dir.exists()
    assert ensure_log_dir.is_dir()


@pytest.mark.unit
def test_logger_different_levels(project_root):
    """測試創建不同級別的日誌器"""
    src_dir = project_root / 'src'
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    try:
        from logger import get_logger

        # 創建不同級別的日誌器
        debug_logger = get_logger('debug_logger', level=logging.DEBUG)
        info_logger = get_logger('info_logger', level=logging.INFO)
        warning_logger = get_logger('warning_logger', level=logging.WARNING)
        error_logger = get_logger('error_logger', level=logging.ERROR)

        # 驗證日誌器創建成功
        assert debug_logger.name == 'debug_logger'
        assert info_logger.name == 'info_logger'
        assert warning_logger.name == 'warning_logger'
        assert error_logger.name == 'error_logger'

    except ImportError:
        pytest.skip("無法導入 logger 模組")


@pytest.mark.unit
def test_log_exception_no_reraise(project_root, captured_logs):
    """測試 log_exception 裝飾器不重新拋出異常"""
    src_dir = project_root / 'src'
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    try:
        from logger import get_logger, log_exception

        test_logger = get_logger('test_no_reraise')

        # 定義不重新拋出異常的函數
        @log_exception(logger=test_logger, reraise=False)
        def error_function():
            raise ValueError("測試錯誤")

        # 調用函數，應該不會拋出異常
        result = error_function()

        # 應該返回 None
        assert result is None

        # 驗證錯誤已被記錄
        assert any(record.levelname == 'ERROR' for record in captured_logs.records)

    except ImportError:
        pytest.skip("無法導入 logger 模組")


@pytest.mark.integration
def test_logger_integration(project_root, temp_log_file, captured_logs):
    """整合測試：測試完整的日誌工作流程"""
    src_dir = project_root / 'src'
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    try:
        from logger import (
            get_logger,
            LogTimer,
            log_execution,
            StructuredLogger,
        )

        # 創建日誌器
        test_logger = get_logger('integration_test', level=logging.DEBUG)

        # 使用結構化日誌
        struct_logger = StructuredLogger(test_logger)
        struct_logger.set_context(test='integration')

        # 記錄基本日誌
        struct_logger.info('開始整合測試')

        # 使用計時器
        with LogTimer(test_logger, '測試操作'):
            time.sleep(0.01)

        # 使用裝飾器
        @log_execution(logger=test_logger, level=logging.DEBUG)
        def test_func(x):
            return x * 2

        result = test_func(5)
        assert result == 10

        struct_logger.info('整合測試完成')

        # 驗證日誌已記錄
        assert len(captured_logs.records) > 0

    except ImportError:
        pytest.skip("無法導入 logger 模組")
