#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prefect 通知告警配置
====================

這個示例展示了 Prefect 的通知和告警功能，包括：
1. 狀態變化通知
2. 失敗告警
3. 成功通知
4. 自定義通知邏輯
5. 多渠道通知（Email、Slack等）
6. 通知過濾和條件
"""

from prefect import task, flow, get_run_logger
from prefect.blocks.notifications import (
    SlackWebhook,
    EmailServerCredentials,
    PagerDutyWebHook
)
import os
import time
import random
from datetime import datetime
from typing import Optional


# ============================================================================
# 基本通知鉤子
# ============================================================================

def send_notification(message: str, level: str = "info"):
    """
    發送通知（模擬）

    在實際應用中，這裡會調用真實的通知服務。

    Args:
        message: 通知消息
        level: 級別（info, warning, error）
    """
    logger = get_run_logger()

    icons = {
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "❌",
        "success": "✅"
    }

    icon = icons.get(level, "📢")
    logger.info(f"{icon} 通知: {message}")


def success_notification(task, task_run, state):
    """
    任務成功時的通知

    Args:
        task: 任務對象
        task_run: 任務運行對象
        state: 狀態對象
    """
    message = f"""
    ✅ 任務成功完成
    ━━━━━━━━━━━━━━━━━━
    任務名稱: {task.name}
    完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    狀態: {state.type}
    ━━━━━━━━━━━━━━━━━━
    """
    send_notification(message, "success")


def failure_notification(task, task_run, state):
    """
    任務失敗時的通知

    Args:
        task: 任務對象
        task_run: 任務運行對象
        state: 狀態對象
    """
    message = f"""
    ❌ 任務執行失敗
    ━━━━━━━━━━━━━━━━━━
    任務名稱: {task.name}
    失敗時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    狀態: {state.type}
    錯誤信息: {state.message}
    ━━━━━━━━━━━━━━━━━━
    ⚠️ 請立即檢查並處理！
    """
    send_notification(message, "error")


# ============================================================================
# 帶通知的任務
# ============================================================================

@task(
    name="關鍵業務任務",
    on_completion=[success_notification],
    on_failure=[failure_notification]
)
def critical_task(should_succeed: bool = True) -> str:
    """
    關鍵業務任務（帶通知）

    Args:
        should_succeed: 是否應該成功

    Returns:
        結果

    Raises:
        RuntimeError: 當 should_succeed 為 False 時
    """
    logger = get_run_logger()
    logger.info("執行關鍵業務任務")

    # 模擬處理
    time.sleep(1)

    if not should_succeed:
        raise RuntimeError("業務邏輯錯誤")

    return "任務成功完成"


@flow(name="基本通知示例")
def basic_notification_demo():
    """
    演示基本的通知功能
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("基本通知示例")
    logger.info("=" * 60)

    # 成功的任務
    logger.info("\n--- 執行成功的任務 ---")
    try:
        result = critical_task(should_succeed=True)
        logger.info(f"結果：{result}")
    except Exception as e:
        logger.error(f"錯誤：{e}")

    # 失敗的任務
    logger.info("\n--- 執行會失敗的任務 ---")
    try:
        result = critical_task(should_succeed=False)
        logger.info(f"結果：{result}")
    except Exception as e:
        logger.error(f"錯誤：{e}")


# ============================================================================
# 條件通知
# ============================================================================

def conditional_notification(task, task_run, state):
    """
    條件通知 - 只在特定條件下發送

    Args:
        task: 任務對象
        task_run: 任務運行對象
        state: 狀態對象
    """
    # 獲取任務結果
    result = state.result() if hasattr(state, 'result') else None

    # 只在結果超過閾值時通知
    if result and isinstance(result, dict):
        value = result.get('value', 0)
        if value > 100:
            message = f"""
            ⚠️ 數值異常告警
            ━━━━━━━━━━━━━━━━━━
            任務: {task.name}
            數值: {value}
            閾值: 100
            時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            ━━━━━━━━━━━━━━━━━━
            """
            send_notification(message, "warning")


@task(on_completion=[conditional_notification])
def monitored_task(value: int) -> dict:
    """
    被監控的任務

    Args:
        value: 數值

    Returns:
        結果字典
    """
    logger = get_run_logger()
    logger.info(f"執行監控任務，值：{value}")

    time.sleep(0.5)

    return {
        "value": value,
        "status": "completed",
        "timestamp": datetime.now().isoformat()
    }


@flow(name="條件通知示例")
def conditional_notification_demo():
    """
    演示條件通知
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("條件通知示例")
    logger.info("=" * 60)

    # 正常值（不會觸發告警）
    logger.info("\n--- 正常值 ---")
    monitored_task(50)

    # 異常值（會觸發告警）
    logger.info("\n--- 異常值 ---")
    monitored_task(150)


# ============================================================================
# 多級通知
# ============================================================================

def info_notification(task, task_run, state):
    """信息級別通知"""
    message = f"ℹ️ 任務 {task.name} 完成"
    send_notification(message, "info")


def warning_notification(task, task_run, state):
    """警告級別通知"""
    message = f"⚠️ 任務 {task.name} 需要注意"
    send_notification(message, "warning")


def error_notification(task, task_run, state):
    """錯誤級別通知"""
    message = f"❌ 任務 {task.name} 發生錯誤：{state.message}"
    send_notification(message, "error")


@task(on_completion=[info_notification])
def low_priority_task() -> str:
    """低優先級任務"""
    logger = get_run_logger()
    logger.info("執行低優先級任務")
    time.sleep(0.5)
    return "完成"


@task(
    on_completion=[warning_notification],
    on_failure=[error_notification]
)
def medium_priority_task() -> str:
    """中優先級任務"""
    logger = get_run_logger()
    logger.info("執行中優先級任務")
    time.sleep(0.5)
    return "完成"


@task(
    on_completion=[success_notification],
    on_failure=[error_notification]
)
def high_priority_task(should_fail: bool = False) -> str:
    """
    高優先級任務

    Args:
        should_fail: 是否應該失敗

    Returns:
        結果

    Raises:
        RuntimeError: 當 should_fail 為 True 時
    """
    logger = get_run_logger()
    logger.info("執行高優先級任務")

    time.sleep(0.5)

    if should_fail:
        raise RuntimeError("高優先級任務失敗")

    return "完成"


@flow(name="多級通知示例")
def multi_level_notification_demo():
    """
    演示多級通知系統
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("多級通知示例")
    logger.info("=" * 60)

    # 低優先級
    logger.info("\n--- 低優先級任務 ---")
    low_priority_task()

    # 中優先級
    logger.info("\n--- 中優先級任務 ---")
    medium_priority_task()

    # 高優先級（成功）
    logger.info("\n--- 高優先級任務（成功）---")
    high_priority_task(should_fail=False)

    # 高優先級（失敗）
    logger.info("\n--- 高優先級任務（失敗）---")
    try:
        high_priority_task(should_fail=True)
    except Exception as e:
        logger.error(f"捕獲錯誤：{e}")


# ============================================================================
# Email 通知配置（示例）
# ============================================================================

def show_email_notification_config():
    """
    顯示 Email 通知配置示例
    """
    print("\n" + "=" * 70)
    print("Email 通知配置")
    print("=" * 70)

    config_example = '''
# 1. 創建 Email Block
from prefect.blocks.notifications import EmailServerCredentials

email_block = EmailServerCredentials(
    username="your-email@gmail.com",
    password="your-app-password",  # 使用應用專用密碼
    smtp_server="smtp.gmail.com",
    smtp_port=587
)

# 保存 Block
email_block.save("my-email-credentials")

# 2. 在任務中使用
def email_notification_hook(task, task_run, state):
    """發送郵件通知"""
    from prefect.blocks.notifications import EmailServerCredentials

    email_block = EmailServerCredentials.load("my-email-credentials")

    subject = f"任務 {task.name} 失敗"
    body = f"""
    任務: {task.name}
    狀態: {state.type}
    時間: {datetime.now()}
    錯誤: {state.message}
    """

    email_block.notify(
        subject=subject,
        body=body,
        email_to=["admin@example.com"]
    )

@task(on_failure=[email_notification_hook])
def important_task():
    # 任務邏輯
    pass

# 3. 使用環境變量
import os

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    '''

    print(config_example)


# ============================================================================
# Slack 通知配置（示例）
# ============================================================================

def show_slack_notification_config():
    """
    顯示 Slack 通知配置示例
    """
    print("\n" + "=" * 70)
    print("Slack 通知配置")
    print("=" * 70)

    config_example = '''
# 1. 創建 Slack Webhook Block
from prefect.blocks.notifications import SlackWebhook

slack_webhook = SlackWebhook(
    url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
)

# 保存 Block
slack_webhook.save("my-slack-webhook")

# 2. 在任務中使用
def slack_notification_hook(task, task_run, state):
    """發送 Slack 通知"""
    from prefect.blocks.notifications import SlackWebhook

    slack_webhook = SlackWebhook.load("my-slack-webhook")

    message = f"""
    🚨 任務失敗告警

    *任務:* {task.name}
    *狀態:* {state.type}
    *時間:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    *錯誤:* {state.message}

    請立即處理！
    """

    slack_webhook.notify(message)

@task(on_failure=[slack_notification_hook])
def monitored_task():
    # 任務邏輯
    pass

# 3. 富文本格式
def slack_rich_notification(task, task_run, state):
    """發送富文本 Slack 通知"""
    slack_webhook = SlackWebhook.load("my-slack-webhook")

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🚨 任務失敗告警"
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*任務:*\\n{task.name}"},
                {"type": "mrkdwn", "text": f"*狀態:*\\n{state.type}"}
            ]
        }
    ]

    # 使用 blocks 發送
    # slack_webhook.notify(blocks=blocks)
    '''

    print(config_example)


# ============================================================================
# 自定義通知服務
# ============================================================================

class CustomNotificationService:
    """
    自定義通知服務

    可以集成多種通知渠道
    """

    def __init__(self):
        self.logger = get_run_logger()

    def send_email(self, subject: str, body: str, to: list):
        """
        發送郵件（模擬）

        Args:
            subject: 主題
            body: 內容
            to: 收件人列表
        """
        self.logger.info(f"📧 發送郵件：{subject}")
        self.logger.info(f"   收件人：{', '.join(to)}")
        self.logger.info(f"   內容：{body}")

    def send_slack(self, channel: str, message: str):
        """
        發送 Slack 消息（模擬）

        Args:
            channel: 頻道
            message: 消息
        """
        self.logger.info(f"💬 發送 Slack 消息到 {channel}")
        self.logger.info(f"   消息：{message}")

    def send_sms(self, phone: str, message: str):
        """
        發送短信（模擬）

        Args:
            phone: 電話號碼
            message: 消息
        """
        self.logger.info(f"📱 發送短信到 {phone}")
        self.logger.info(f"   消息：{message}")

    def send_webhook(self, url: str, data: dict):
        """
        發送 Webhook（模擬）

        Args:
            url: Webhook URL
            data: 數據
        """
        self.logger.info(f"🔗 發送 Webhook 到 {url}")
        self.logger.info(f"   數據：{data}")


# 創建全局通知服務實例
notification_service = CustomNotificationService()


def multi_channel_notification(task, task_run, state):
    """
    多渠道通知

    Args:
        task: 任務對象
        task_run: 任務運行對象
        state: 狀態對象
    """
    # 郵件通知
    notification_service.send_email(
        subject=f"任務 {task.name} 失敗",
        body=f"錯誤：{state.message}",
        to=["admin@example.com", "ops@example.com"]
    )

    # Slack 通知
    notification_service.send_slack(
        channel="#alerts",
        message=f"❌ 任務 {task.name} 失敗：{state.message}"
    )

    # 緊急情況發送短信
    if "critical" in task.tags:
        notification_service.send_sms(
            phone="+1234567890",
            message=f"緊急：任務 {task.name} 失敗"
        )


@task(
    on_failure=[multi_channel_notification],
    tags=["critical"]
)
def critical_business_task(should_fail: bool = False) -> str:
    """
    關鍵業務任務（多渠道通知）

    Args:
        should_fail: 是否應該失敗

    Returns:
        結果

    Raises:
        RuntimeError: 當 should_fail 為 True 時
    """
    logger = get_run_logger()
    logger.info("執行關鍵業務任務")

    time.sleep(1)

    if should_fail:
        raise RuntimeError("關鍵業務失敗")

    return "成功"


@flow(name="多渠道通知示例")
def multi_channel_notification_demo():
    """
    演示多渠道通知
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("多渠道通知示例")
    logger.info("=" * 60)

    try:
        critical_business_task(should_fail=True)
    except Exception as e:
        logger.error(f"任務失敗：{e}")


# ============================================================================
# 通知過濾
# ============================================================================

def filtered_notification(task, task_run, state):
    """
    過濾通知 - 只在特定時間段發送

    Args:
        task: 任務對象
        task_run: 任務運行對象
        state: 狀態對象
    """
    logger = get_run_logger()

    # 只在工作時間發送通知
    current_hour = datetime.now().hour
    if 9 <= current_hour <= 18:
        message = f"任務 {task.name} 在工作時間失敗"
        send_notification(message, "error")
    else:
        logger.info(f"非工作時間，跳過通知（任務：{task.name}）")


@task(on_failure=[filtered_notification])
def time_filtered_task(should_fail: bool = False) -> str:
    """
    時間過濾的任務

    Args:
        should_fail: 是否應該失敗

    Returns:
        結果

    Raises:
        RuntimeError: 當 should_fail 為 True 時
    """
    logger = get_run_logger()
    logger.info("執行時間過濾任務")

    if should_fail:
        raise RuntimeError("任務失敗")

    return "成功"


@flow(name="通知過濾示例")
def notification_filter_demo():
    """
    演示通知過濾
    """
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("通知過濾示例")
    logger.info("=" * 60)

    current_hour = datetime.now().hour
    logger.info(f"當前時間：{current_hour}:00")

    try:
        time_filtered_task(should_fail=True)
    except Exception as e:
        logger.error(f"任務失敗：{e}")


# ============================================================================
# 運行示例
# ============================================================================

def main():
    """
    主函數 - 運行所有示例
    """
    print("\n" + "=" * 70)
    print("Prefect 通知告警配置")
    print("=" * 70)

    # 示例 1: 基本通知
    print("\n【示例 1】基本通知")
    print("-" * 70)
    basic_notification_demo()

    # 示例 2: 條件通知
    print("\n【示例 2】條件通知")
    print("-" * 70)
    conditional_notification_demo()

    # 示例 3: 多級通知
    print("\n【示例 3】多級通知")
    print("-" * 70)
    multi_level_notification_demo()

    # 示例 4: 多渠道通知
    print("\n【示例 4】多渠道通知")
    print("-" * 70)
    multi_channel_notification_demo()

    # 示例 5: 通知過濾
    print("\n【示例 5】通知過濾")
    print("-" * 70)
    notification_filter_demo()

    # 配置示例
    show_email_notification_config()
    show_slack_notification_config()

    # 使用說明
    print("\n" + "=" * 70)
    print("通知告警總結")
    print("=" * 70)
    print("""
1. 通知鉤子：
   @task(
       on_completion=[success_hook],
       on_failure=[failure_hook]
   )

2. 支持的通知渠道：
   - Email（郵件）
   - Slack（即時通訊）
   - PagerDuty（事件管理）
   - Webhook（自定義集成）
   - SMS（短信，需第三方服務）

3. 通知級別：
   - Info: 一般信息
   - Warning: 警告
   - Error: 錯誤
   - Critical: 緊急

4. 最佳實踐：
   - 為關鍵任務設置失敗通知
   - 使用條件邏輯避免通知泛濫
   - 區分不同優先級
   - 設置適當的通知渠道

5. 通知過濾：
   - 時間過濾（工作時間/非工作時間）
   - 條件過濾（閾值、頻率）
   - 優先級過濾
   - 去重處理

6. 配置步驟：
   a. 創建通知 Block
   b. 保存配置
   c. 在任務中引用
   d. 測試通知

7. 環境配置：
   # .env 文件
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email
   SMTP_PASSWORD=your-password
   SLACK_WEBHOOK_URL=https://hooks.slack.com/...

8. 注意事項：
   - 保護敏感信息（使用 Blocks）
   - 避免通知風暴
   - 測試通知配置
   - 監控通知發送狀態

9. 下一步：
   - 查看 09_部署配置.py 了解部署選項
   - 查看 10_監控面板.py 了解監控功能
    """)

    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
