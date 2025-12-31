"""
統一日誌系統使用示例

此示例展示了如何使用統一日誌配置系統和日誌工具類：
1. 基本日誌記錄
2. 不同級別的日誌
3. 上下文管理器（計時）
4. 裝飾器（函數追蹤）
5. 結構化日誌
6. 性能監控
7. 不同環境的日誌配置

作者: LLM Agent Demo
日期: 2025-12-31
"""

import sys
import time
import logging
from pathlib import Path

# 添加 src 目錄到路徑
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from logging_config import (
    setup_logging,
    get_development_logger,
    get_production_logger,
    LogConfig,
)
from logger import (
    get_logger,
    LogTimer,
    log_execution,
    log_exception,
    StructuredLogger,
    PerformanceLogger,
    create_file_logger,
    create_console_logger,
)


def demo_basic_logging():
    """演示基本日誌記錄"""
    print("\n" + "=" * 60)
    print("示例 1: 基本日誌記錄")
    print("=" * 60)

    # 創建一個簡單的日誌器
    logger = get_logger('basic_demo', level=logging.DEBUG)

    # 記錄不同級別的日誌
    logger.debug("這是 DEBUG 級別的消息 - 用於詳細的調試信息")
    logger.info("這是 INFO 級別的消息 - 用於一般信息")
    logger.warning("這是 WARNING 級別的消息 - 用於警告信息")
    logger.error("這是 ERROR 級別的消息 - 用於錯誤信息")
    logger.critical("這是 CRITICAL 級別的消息 - 用於嚴重錯誤")


def demo_log_timer():
    """演示計時上下文管理器"""
    print("\n" + "=" * 60)
    print("示例 2: 計時上下文管理器")
    print("=" * 60)

    logger = get_logger('timer_demo')

    # 使用 LogTimer 測量代碼塊執行時間
    print("\n2.1 測量快速操作:")
    with LogTimer(logger, '快速數據處理'):
        time.sleep(0.5)
        # 模擬一些處理
        data = [i ** 2 for i in range(1000)]

    print("\n2.2 測量較慢操作:")
    with LogTimer(logger, '複雜計算', level=logging.WARNING):
        time.sleep(1.0)
        # 模擬複雜計算
        result = sum(i ** 3 for i in range(10000))

    print("\n2.3 處理帶異常的操作:")
    try:
        with LogTimer(logger, '可能失敗的操作'):
            time.sleep(0.3)
            # 模擬錯誤
            raise ValueError("模擬的錯誤")
    except ValueError:
        print("異常已被捕獲並記錄")


def demo_execution_decorator():
    """演示函數執行追蹤裝飾器"""
    print("\n" + "=" * 60)
    print("示例 3: 函數執行追蹤裝飾器")
    print("=" * 60)

    logger = get_logger('decorator_demo')

    # 定義帶有裝飾器的函數
    @log_execution(logger=logger, log_args=True, log_result=True)
    def calculate_sum(numbers):
        """計算數字總和"""
        time.sleep(0.2)  # 模擬處理時間
        return sum(numbers)

    @log_execution(logger=logger, log_args=False, log_result=True)
    def process_data(data, multiplier=2):
        """處理數據"""
        time.sleep(0.3)
        return [x * multiplier for x in data]

    @log_execution(logger=logger)
    def complex_operation(x, y, z):
        """複雜操作"""
        time.sleep(0.1)
        return (x + y) * z

    # 調用函數
    print("\n3.1 計算總和:")
    result1 = calculate_sum([1, 2, 3, 4, 5])
    print(f"結果: {result1}")

    print("\n3.2 處理數據:")
    result2 = process_data([10, 20, 30], multiplier=3)
    print(f"結果: {result2}")

    print("\n3.3 複雜操作:")
    result3 = complex_operation(5, 10, 2)
    print(f"結果: {result3}")


def demo_exception_decorator():
    """演示異常捕獲裝飾器"""
    print("\n" + "=" * 60)
    print("示例 4: 異常捕獲裝飾器")
    print("=" * 60)

    logger = get_logger('exception_demo')

    @log_exception(logger=logger, reraise=False)
    def risky_operation_1(value):
        """可能失敗的操作（不重新拋出異常）"""
        if value < 0:
            raise ValueError("值不能為負數")
        return value * 2

    @log_exception(logger=logger, reraise=True, message="自定義錯誤消息")
    def risky_operation_2(value):
        """可能失敗的操作（重新拋出異常）"""
        if value == 0:
            raise ZeroDivisionError("不能除以零")
        return 100 / value

    # 測試異常處理
    print("\n4.1 處理負數（不重新拋出）:")
    result = risky_operation_1(-5)
    print(f"返回值: {result}")

    print("\n4.2 處理正常值:")
    result = risky_operation_1(10)
    print(f"返回值: {result}")

    print("\n4.3 處理零除錯誤（重新拋出）:")
    try:
        result = risky_operation_2(0)
    except ZeroDivisionError:
        print("異常被捕獲")


def demo_structured_logging():
    """演示結構化日誌"""
    print("\n" + "=" * 60)
    print("示例 5: 結構化日誌")
    print("=" * 60)

    logger = get_logger('structured_demo')
    struct_logger = StructuredLogger(logger)

    # 設置全局上下文
    struct_logger.set_context(
        app='demo_app',
        version='1.0.0',
        environment='development'
    )

    print("\n5.1 帶全局上下文的日誌:")
    struct_logger.info('應用程序啟動')
    struct_logger.info('連接數據庫', db='postgresql', host='localhost')

    print("\n5.2 帶臨時上下文的日誌:")
    with struct_logger.context_scope(request_id='req-12345', user_id=100):
        struct_logger.info('處理用戶請求')
        struct_logger.info('查詢用戶數據', table='users')
        struct_logger.warning('查詢耗時較長', duration=2.5)

    print("\n5.3 上下文範圍外的日誌:")
    struct_logger.info('請求處理完成')


def demo_performance_logging():
    """演示性能日誌記錄"""
    print("\n" + "=" * 60)
    print("示例 6: 性能日誌記錄")
    print("=" * 60)

    logger = get_logger('performance_demo', level=logging.DEBUG)
    perf_logger = PerformanceLogger(logger, threshold=0.5)

    print("\n6.1 快速操作（低於閾值）:")
    with perf_logger.measure('快速查詢', table='cache', rows=10):
        time.sleep(0.2)

    print("\n6.2 慢速操作（超過閾值）:")
    with perf_logger.measure('慢速查詢', table='users', rows=10000):
        time.sleep(0.8)

    print("\n6.3 帶元數據的性能監控:")
    with perf_logger.measure('API 請求', endpoint='/api/users', method='GET'):
        time.sleep(0.3)


def demo_different_configurations():
    """演示不同的日誌配置"""
    print("\n" + "=" * 60)
    print("示例 7: 不同環境的日誌配置")
    print("=" * 60)

    print("\n7.1 開發環境日誌器:")
    dev_logger = get_development_logger('dev_app')
    dev_logger.debug("開發環境 - DEBUG 消息可見")
    dev_logger.info("開發環境 - INFO 消息")
    dev_logger.warning("開發環境 - WARNING 消息")

    print("\n7.2 生產環境日誌器:")
    prod_logger = get_production_logger('prod_app')
    prod_logger.debug("生產環境 - DEBUG 消息不可見")
    prod_logger.info("生產環境 - INFO 消息")
    prod_logger.error("生產環境 - ERROR 消息")

    print("\n7.3 自定義配置:")
    custom_logger = setup_logging(
        name='custom_app',
        level=logging.INFO,
        log_dir='demo_logs',
        log_file='custom.log',
        console_output=True,
        file_output=True,
        json_format=False,
        use_rich=True,
    )
    custom_logger.info("自定義配置的日誌消息")

    print("\n7.4 僅文件日誌器:")
    file_logger = create_file_logger(
        'file_only',
        'demo_logs/file_only.log',
        level=logging.DEBUG
    )
    file_logger.info("此消息僅寫入文件")
    print("（此消息已寫入 demo_logs/file_only.log）")

    print("\n7.5 僅控制台日誌器:")
    console_logger = create_console_logger('console_only', use_rich=True)
    console_logger.info("此消息僅輸出到控制台")


def demo_real_world_scenario():
    """演示實際應用場景"""
    print("\n" + "=" * 60)
    print("示例 8: 實際應用場景 - 數據處理管道")
    print("=" * 60)

    # 設置日誌器
    logger = get_logger('data_pipeline', level=logging.INFO)
    struct_logger = StructuredLogger(logger)
    perf_logger = PerformanceLogger(logger, threshold=1.0)

    # 設置管道上下文
    struct_logger.set_context(pipeline='user_data_etl', version='2.1')

    @log_execution(logger=logger)
    @log_exception(logger=logger, reraise=False)
    def extract_data(source):
        """提取數據"""
        struct_logger.info('開始提取數據', source=source)
        time.sleep(0.3)
        # 模擬數據提取
        data = list(range(100))
        struct_logger.info('數據提取完成', records=len(data))
        return data

    @log_execution(logger=logger)
    def transform_data(data):
        """轉換數據"""
        with LogTimer(logger, '數據轉換'):
            # 模擬數據轉換
            transformed = [x * 2 for x in data]
            time.sleep(0.4)
        return transformed

    @log_execution(logger=logger)
    def load_data(data, destination):
        """載入數據"""
        with perf_logger.measure('數據載入', destination=destination, records=len(data)):
            # 模擬數據載入
            time.sleep(0.5)
            struct_logger.info('數據載入完成', destination=destination)

    # 執行 ETL 管道
    print("\n執行 ETL 管道:")
    with LogTimer(logger, '完整 ETL 管道', level=logging.INFO):
        # 提取
        raw_data = extract_data('database')

        if raw_data:
            # 轉換
            processed_data = transform_data(raw_data)

            # 載入
            load_data(processed_data, 'data_warehouse')

    struct_logger.info('管道執行完成', status='success')


def demo_error_handling():
    """演示錯誤處理"""
    print("\n" + "=" * 60)
    print("示例 9: 錯誤處理和異常日誌")
    print("=" * 60)

    logger = get_logger('error_demo')

    print("\n9.1 簡單異常日誌:")
    try:
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.error(f"發生除零錯誤: {e}")

    print("\n9.2 帶堆棧跟蹤的異常日誌:")
    try:
        data = {'key': 'value'}
        value = data['nonexistent_key']
    except KeyError as e:
        logger.exception(f"鍵錯誤: {e}")

    print("\n9.3 自定義異常處理:")
    @log_exception(logger=logger, message="數據驗證失敗")
    def validate_data(data):
        """驗證數據"""
        if not isinstance(data, dict):
            raise TypeError("數據必須是字典類型")
        if 'required_field' not in data:
            raise ValueError("缺少必需字段")
        return True

    try:
        validate_data([1, 2, 3])  # 錯誤類型
    except TypeError:
        pass

    try:
        validate_data({'other_field': 'value'})  # 缺少字段
    except ValueError:
        pass


def main():
    """主函數 - 運行所有示例"""
    print("\n" + "=" * 60)
    print("統一日誌系統示例")
    print("=" * 60)
    print("此示例展示了日誌系統的各種功能和用法")

    # 運行所有示例
    demo_basic_logging()
    demo_log_timer()
    demo_execution_decorator()
    demo_exception_decorator()
    demo_structured_logging()
    demo_performance_logging()
    demo_different_configurations()
    demo_real_world_scenario()
    demo_error_handling()

    print("\n" + "=" * 60)
    print("所有示例執行完成！")
    print("=" * 60)
    print("\n提示:")
    print("- 查看控制台輸出以查看彩色日誌")
    print("- 查看 logs/ 和 demo_logs/ 目錄以查看日誌文件")
    print("- 嘗試修改日誌級別以查看不同的輸出")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
