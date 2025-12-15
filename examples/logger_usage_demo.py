#!/usr/bin/env python3
"""日誌系統使用示例

演示日誌系統的各種功能：
1. 基本日誌配置
2. 結構化日誌
3. 日誌輪轉
4. 上下文管理器
5. 性能監控
6. 敏感信息過濾
"""

import time
from pathlib import Path

# 導入日誌系統
import sys
from pathlib import Path

# 添加項目根目錄到路徑
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm_agent_demo.utils.logger import (
    setup_logging,
    get_logger,
    log_context,
    log_execution_time,
    log_function_call,
    StructuredLogger,
    LogStats,
)


def demo_basic_logging():
    """演示基本日誌功能"""
    print("\n" + "=" * 60)
    print("1. 基本日誌功能演示")
    print("=" * 60)

    # 設置日誌系統
    setup_logging(level="INFO", colorize=True)

    # 獲取日誌記錄器
    logger = get_logger(__name__)

    # 不同級別的日誌
    logger.debug("這是 DEBUG 訊息（不會顯示，因為級別是 INFO）")
    logger.info("這是 INFO 訊息")
    logger.warning("這是 WARNING 訊息")
    logger.error("這是 ERROR 訊息")

    # 帶異常信息的日誌
    try:
        result = 10 / 0
    except ZeroDivisionError:
        logger.exception("除以零錯誤")


def demo_json_logging():
    """演示 JSON 格式日誌"""
    print("\n" + "=" * 60)
    print("2. JSON 格式日誌演示")
    print("=" * 60)

    # 設置 JSON 格式日誌
    log_file = Path("logs/app.json")
    setup_logging(level="INFO", log_file=str(log_file), json_format=True)

    logger = get_logger(__name__)
    logger.info("這是 JSON 格式的日誌")
    logger.warning("JSON 日誌包含完整的元數據")

    print(f"JSON 日誌已寫入: {log_file.absolute()}")
    if log_file.exists():
        print("日誌內容預覽:")
        print(log_file.read_text()[:500] + "...")


def demo_log_rotation():
    """演示日誌輪轉"""
    print("\n" + "=" * 60)
    print("3. 日誌輪轉演示")
    print("=" * 60)

    # 設置按大小輪轉的日誌（1KB，保留3個備份）
    log_file = Path("logs/rotating.log")
    setup_logging(
        level="INFO",
        log_file=str(log_file),
        enable_rotation=True,
        max_bytes=1024,  # 1KB
        backup_count=3,
        rotation_type="size",
    )

    logger = get_logger(__name__)

    # 寫入大量日誌觸發輪轉
    for i in range(100):
        logger.info(f"日誌輪轉測試訊息 #{i} - " + "x" * 50)

    print(f"日誌文件已創建: {log_file.absolute()}")
    print(f"檢查目錄中的輪轉文件: {log_file.parent.absolute()}")


def demo_context_logging():
    """演示上下文日誌"""
    print("\n" + "=" * 60)
    print("4. 上下文日誌演示")
    print("=" * 60)

    setup_logging(level="INFO", json_format=True)
    logger = get_logger(__name__)

    # 使用上下文管理器添加上下文信息
    with log_context(logger, {"user_id": "12345", "request_id": "abc-def"}):
        logger.info("處理用戶請求")
        logger.info("執行業務邏輯")

    # 不同的上下文
    with log_context(logger, {"session_id": "xyz-789", "ip": "192.168.1.1"}):
        logger.info("用戶登入")


def demo_execution_time():
    """演示執行時間記錄"""
    print("\n" + "=" * 60)
    print("5. 執行時間記錄演示")
    print("=" * 60)

    setup_logging(level="INFO")
    logger = get_logger(__name__)

    # 記錄代碼塊執行時間
    with log_execution_time(logger, "數據處理操作"):
        time.sleep(0.5)  # 模擬耗時操作
        print("  執行中...")

    with log_execution_time(logger, "數據庫查詢", level="DEBUG"):
        time.sleep(0.2)


@log_function_call(get_logger(__name__))
def example_function(a: int, b: int) -> int:
    """示例函數（帶日誌裝飾器）"""
    time.sleep(0.1)
    return a + b


def demo_function_logging():
    """演示函數調用日誌"""
    print("\n" + "=" * 60)
    print("6. 函數調用日誌演示")
    print("=" * 60)

    setup_logging(level="DEBUG")

    result = example_function(10, 20)
    print(f"  函數返回值: {result}")


def demo_structured_logging():
    """演示結構化日誌"""
    print("\n" + "=" * 60)
    print("7. 結構化日誌演示")
    print("=" * 60)

    # 創建結構化日誌記錄器
    structured_logger = StructuredLogger("my_app")

    # 記錄事件
    structured_logger.log_event(
        "user_login",
        user_id="12345",
        username="john_doe",
        ip_address="192.168.1.100",
    )

    # 記錄指標
    structured_logger.log_metric("response_time", 0.234, unit="秒", endpoint="/api/users")
    structured_logger.log_metric("memory_usage", 512.5, unit="MB")

    # 記錄 API 調用
    structured_logger.log_api_call(
        method="GET",
        url="/api/v1/users",
        status_code=200,
        duration=0.123,
    )

    structured_logger.log_api_call(
        method="POST",
        url="/api/v1/orders",
        status_code=500,
        duration=1.234,
        error="Internal Server Error",
    )

    # 記錄錯誤
    try:
        raise ValueError("無效的輸入參數")
    except ValueError as e:
        structured_logger.log_error(
            e, context={"function": "process_data", "input": "invalid_value"}
        )


def demo_sensitive_filter():
    """演示敏感信息過濾"""
    print("\n" + "=" * 60)
    print("8. 敏感信息過濾演示")
    print("=" * 60)

    # 啟用敏感信息過濾
    setup_logging(level="INFO", enable_filter=True)
    logger = get_logger(__name__)

    # 這些日誌會被標記為 [FILTERED]
    logger.info("用戶密碼是: my_password_123")
    logger.info("API Key: sk-1234567890abcdef")
    logger.info("Secret token: bearer_xyz")

    # 正常日誌不會被過濾
    logger.info("用戶成功登入")


def demo_log_stats():
    """演示日誌統計"""
    print("\n" + "=" * 60)
    print("9. 日誌統計演示")
    print("=" * 60)

    # 創建統計收集器
    stats = LogStats()

    setup_logging(level="DEBUG")
    logger = get_logger(__name__)

    # 添加統計 handler
    logger.addHandler(stats.get_handler())

    # 記錄不同級別的日誌
    logger.debug("Debug 訊息 1")
    logger.debug("Debug 訊息 2")
    logger.info("Info 訊息 1")
    logger.info("Info 訊息 2")
    logger.info("Info 訊息 3")
    logger.warning("Warning 訊息")
    logger.error("Error 訊息")

    # 顯示統計
    print("\n日誌統計:")
    for level, count in stats.get_summary().items():
        print(f"  {level}: {count}")
    print(f"  總計: {stats.get_total()}")


def demo_environment_config():
    """演示環境變量配置"""
    print("\n" + "=" * 60)
    print("10. 環境變量配置演示")
    print("=" * 60)

    import os

    # 設置環境變量
    os.environ["LOG_LEVEL"] = "WARNING"
    os.environ["LOG_JSON"] = "true"

    # setup_logging 會自動讀取環境變量
    setup_logging()  # 不傳遞參數，使用環境變量

    logger = get_logger(__name__)

    logger.debug("這不會顯示（級別太低）")
    logger.info("這也不會顯示（級別太低）")
    logger.warning("這會顯示（WARNING 級別）")
    logger.error("這也會顯示（ERROR 級別）")

    # 清理環境變量
    del os.environ["LOG_LEVEL"]
    del os.environ["LOG_JSON"]


def main():
    """運行所有演示"""
    print("\n" + "=" * 60)
    print("日誌系統功能演示")
    print("=" * 60)

    try:
        demo_basic_logging()
        demo_json_logging()
        demo_log_rotation()
        demo_context_logging()
        demo_execution_time()
        demo_function_logging()
        demo_structured_logging()
        demo_sensitive_filter()
        demo_log_stats()
        demo_environment_config()

        print("\n" + "=" * 60)
        print("所有演示完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n錯誤: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
