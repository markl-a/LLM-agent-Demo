#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Composio Slack 整合範例
=======================

本範例展示如何使用 Composio 整合 Slack，包括：
1. Slack 認證和連接
2. 發送訊息到頻道和用戶
3. 創建和管理頻道
4. 文件上傳和分享
5. 用戶和團隊管理
6. 事件監聽和回應
7. Slack Bot 自動化

Slack 是領先的團隊協作平台，Composio 提供完整的 Slack API 整合。

作者: Composio 團隊
日期: 2025-01-01
"""

import os
import sys
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 導入 Composio SDK
try:
    from composio import Composio, App, Action
    from composio.client.exceptions import ComposioException
except ImportError as e:
    print("錯誤：請先安裝 Composio SDK")
    print("執行: pip install composio-core")
    sys.exit(1)


class SlackIntegration:
    """
    Slack 整合類別

    提供完整的 Slack 整合功能，包括：
    - 訊息發送和管理
    - 頻道操作
    - 文件分享
    - 用戶互動
    - 自動化工作流程
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 Slack 整合

        Args:
            api_key: Composio API 金鑰
        """
        print("=" * 70)
        print("初始化 Slack 整合")
        print("=" * 70)

        self.api_key = api_key or os.getenv("COMPOSIO_API_KEY")

        try:
            # 初始化 Composio 客戶端
            self.client = Composio(api_key=self.api_key)
            self.entity = self.client.get_entity(id="default")
            print("✓ Composio 客戶端初始化成功")

            # 檢查 Slack 連接
            self._check_slack_connection()

        except Exception as e:
            print(f"✗ 初始化失敗: {e}")
            raise

    def _check_slack_connection(self) -> bool:
        """
        檢查 Slack 連接狀態

        Returns:
            是否已連接
        """
        try:
            connections = self.entity.get_connections(app_name="slack")

            if connections:
                print("✓ Slack 已連接")
                return True
            else:
                print("⚠ Slack 尚未連接")
                print("\n要連接 Slack，請執行:")
                print("  connection = entity.initiate_connection('slack')")
                print("  然後訪問返回的 URL 進行授權")
                return False

        except Exception as e:
            print(f"✗ 檢查連接失敗: {e}")
            return False

    def connect_slack(self, redirect_url: str = "http://localhost:8000/callback") -> Optional[str]:
        """
        連接 Slack 工作區

        Args:
            redirect_url: OAuth 回調 URL

        Returns:
            授權 URL
        """
        print("\n" + "=" * 70)
        print("連接 Slack 工作區")
        print("=" * 70)

        try:
            # 啟動 OAuth 流程
            connection_request = self.entity.initiate_connection(
                app_name="slack",
                redirect_url=redirect_url
            )

            if hasattr(connection_request, 'redirectUrl'):
                auth_url = connection_request.redirectUrl
                print(f"\n請訪問以下 URL 進行授權:")
                print(f"{auth_url}")
                return auth_url
            else:
                print("✓ Slack 連接已建立")
                return None

        except Exception as e:
            print(f"✗ 連接 Slack 失敗: {e}")
            return None

    def send_message(self, channel: str, text: str,
                    thread_ts: Optional[str] = None,
                    attachments: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        發送訊息到 Slack 頻道

        Args:
            channel: 頻道 ID 或名稱
            text: 訊息內容
            thread_ts: 回覆的訊息時間戳（用於線程回覆）
            attachments: 訊息附件

        Returns:
            發送結果
        """
        print("\n" + "=" * 70)
        print(f"發送訊息到頻道: {channel}")
        print("=" * 70)

        try:
            # 構建參數
            params = {
                "channel": channel,
                "text": text
            }

            if thread_ts:
                params["thread_ts"] = thread_ts

            if attachments:
                params["attachments"] = attachments

            # 執行操作
            result = self.entity.execute(
                action="SLACK_SEND_MESSAGE",
                params=params
            )

            message = result.get('data', {})
            print(f"\n✓ 訊息發送成功!")
            print(f"  頻道: {message.get('channel')}")
            print(f"  時間戳: {message.get('ts')}")
            print(f"  內容: {text[:50]}...")

            return message

        except Exception as e:
            print(f"✗ 發送訊息失敗: {e}")
            return {}

    def send_direct_message(self, user_id: str, text: str) -> Dict[str, Any]:
        """
        發送直接訊息給用戶

        Args:
            user_id: 用戶 ID
            text: 訊息內容

        Returns:
            發送結果
        """
        print("\n" + "=" * 70)
        print(f"發送直接訊息給用戶: {user_id}")
        print("=" * 70)

        try:
            # 首先打開 DM 頻道
            dm_result = self.entity.execute(
                action="SLACK_OPEN_CONVERSATION",
                params={"users": user_id}
            )

            channel_id = dm_result.get('data', {}).get('channel', {}).get('id')

            if not channel_id:
                raise Exception("無法打開 DM 頻道")

            # 發送訊息
            return self.send_message(channel=channel_id, text=text)

        except Exception as e:
            print(f"✗ 發送直接訊息失敗: {e}")
            return {}

    def send_rich_message(self, channel: str, blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        發送富文本訊息（使用 Block Kit）

        Args:
            channel: 頻道 ID 或名稱
            blocks: Block Kit 區塊列表

        Returns:
            發送結果
        """
        print("\n" + "=" * 70)
        print(f"發送富文本訊息到頻道: {channel}")
        print("=" * 70)

        try:
            # 執行操作
            result = self.entity.execute(
                action="SLACK_SEND_MESSAGE",
                params={
                    "channel": channel,
                    "blocks": blocks,
                    "text": "富文本訊息"  # 備用文字
                }
            )

            message = result.get('data', {})
            print(f"\n✓ 富文本訊息發送成功!")
            print(f"  頻道: {message.get('channel')}")

            return message

        except Exception as e:
            print(f"✗ 發送富文本訊息失敗: {e}")
            return {}

    def create_channel(self, name: str, is_private: bool = False) -> Dict[str, Any]:
        """
        創建新的 Slack 頻道

        Args:
            name: 頻道名稱
            is_private: 是否為私有頻道

        Returns:
            創建的頻道資訊
        """
        print("\n" + "=" * 70)
        print(f"創建頻道: {name}")
        print("=" * 70)

        try:
            # 執行操作
            result = self.entity.execute(
                action="SLACK_CREATE_CHANNEL",
                params={
                    "name": name,
                    "is_private": is_private
                }
            )

            channel = result.get('data', {}).get('channel', {})
            print(f"\n✓ 頻道創建成功!")
            print(f"  名稱: {channel.get('name')}")
            print(f"  ID: {channel.get('id')}")
            print(f"  類型: {'私有' if is_private else '公開'}")

            return channel

        except Exception as e:
            print(f"✗ 創建頻道失敗: {e}")
            return {}

    def list_channels(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        列出所有頻道

        Args:
            limit: 限制返回的頻道數量

        Returns:
            頻道列表
        """
        print("\n" + "=" * 70)
        print("列出 Slack 頻道")
        print("=" * 70)

        try:
            # 執行操作
            result = self.entity.execute(
                action="SLACK_LIST_CHANNELS",
                params={"limit": limit}
            )

            channels = result.get('data', {}).get('channels', [])
            print(f"\n找到 {len(channels)} 個頻道:")
            print("-" * 70)

            for i, channel in enumerate(channels, 1):
                name = channel.get('name', 'Unknown')
                channel_id = channel.get('id', 'Unknown')
                members = channel.get('num_members', 0)
                is_private = channel.get('is_private', False)

                print(f"{i}. #{name} ({channel_id})")
                print(f"   成員: {members} | 類型: {'私有' if is_private else '公開'}")
                print()

            return channels

        except Exception as e:
            print(f"✗ 列出頻道失敗: {e}")
            return []

    def invite_user_to_channel(self, channel: str, user: str) -> Dict[str, Any]:
        """
        邀請用戶加入頻道

        Args:
            channel: 頻道 ID
            user: 用戶 ID

        Returns:
            操作結果
        """
        print("\n" + "=" * 70)
        print(f"邀請用戶到頻道")
        print("=" * 70)

        try:
            # 執行操作
            result = self.entity.execute(
                action="SLACK_INVITE_TO_CHANNEL",
                params={
                    "channel": channel,
                    "users": user
                }
            )

            print(f"\n✓ 用戶邀請成功!")
            return result.get('data', {})

        except Exception as e:
            print(f"✗ 邀請用戶失敗: {e}")
            return {}

    def upload_file(self, channels: List[str], file_path: str,
                   title: Optional[str] = None,
                   initial_comment: Optional[str] = None) -> Dict[str, Any]:
        """
        上傳文件到 Slack

        Args:
            channels: 頻道列表
            file_path: 文件路徑
            title: 文件標題
            initial_comment: 初始評論

        Returns:
            上傳結果
        """
        print("\n" + "=" * 70)
        print(f"上傳文件: {file_path}")
        print("=" * 70)

        try:
            # 讀取文件
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")

            with open(file_path, 'rb') as f:
                file_content = f.read()

            # 構建參數
            params = {
                "channels": ",".join(channels),
                "file": file_content,
                "filename": os.path.basename(file_path)
            }

            if title:
                params["title"] = title

            if initial_comment:
                params["initial_comment"] = initial_comment

            # 執行操作
            result = self.entity.execute(
                action="SLACK_UPLOAD_FILE",
                params=params
            )

            file_info = result.get('data', {}).get('file', {})
            print(f"\n✓ 文件上傳成功!")
            print(f"  文件名: {file_info.get('name')}")
            print(f"  大小: {file_info.get('size')} bytes")

            return file_info

        except Exception as e:
            print(f"✗ 上傳文件失敗: {e}")
            return {}

    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """
        獲取用戶資訊

        Args:
            user_id: 用戶 ID

        Returns:
            用戶資訊
        """
        print("\n" + "=" * 70)
        print(f"獲取用戶資訊: {user_id}")
        print("=" * 70)

        try:
            # 執行操作
            result = self.entity.execute(
                action="SLACK_GET_USER_INFO",
                params={"user": user_id}
            )

            user = result.get('data', {}).get('user', {})
            profile = user.get('profile', {})

            print(f"\n用戶資訊:")
            print("-" * 70)
            print(f"  名稱: {profile.get('real_name', 'Unknown')}")
            print(f"  顯示名稱: {profile.get('display_name', 'Unknown')}")
            print(f"  Email: {profile.get('email', 'Unknown')}")
            print(f"  時區: {user.get('tz', 'Unknown')}")

            return user

        except Exception as e:
            print(f"✗ 獲取用戶資訊失敗: {e}")
            return {}

    def list_users(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        列出工作區用戶

        Args:
            limit: 限制返回的用戶數量

        Returns:
            用戶列表
        """
        print("\n" + "=" * 70)
        print("列出工作區用戶")
        print("=" * 70)

        try:
            # 執行操作
            result = self.entity.execute(
                action="SLACK_LIST_USERS",
                params={"limit": limit}
            )

            members = result.get('data', {}).get('members', [])
            print(f"\n找到 {len(members)} 個用戶:")
            print("-" * 70)

            for i, member in enumerate(members, 1):
                profile = member.get('profile', {})
                name = profile.get('real_name', 'Unknown')
                display_name = profile.get('display_name', 'Unknown')
                is_bot = member.get('is_bot', False)

                print(f"{i}. {name} (@{display_name})")
                print(f"   類型: {'Bot' if is_bot else '用戶'}")
                print()

            return members

        except Exception as e:
            print(f"✗ 列出用戶失敗: {e}")
            return []

    def add_reaction(self, channel: str, timestamp: str, emoji: str) -> Dict[str, Any]:
        """
        添加表情符號反應

        Args:
            channel: 頻道 ID
            timestamp: 訊息時間戳
            emoji: 表情符號名稱（不含冒號）

        Returns:
            操作結果
        """
        print("\n" + "=" * 70)
        print(f"添加反應: :{emoji}:")
        print("=" * 70)

        try:
            # 執行操作
            result = self.entity.execute(
                action="SLACK_ADD_REACTION",
                params={
                    "channel": channel,
                    "timestamp": timestamp,
                    "name": emoji
                }
            )

            print(f"\n✓ 反應添加成功!")
            return result.get('data', {})

        except Exception as e:
            print(f"✗ 添加反應失敗: {e}")
            return {}


def demo_messaging():
    """
    演示訊息發送功能
    """
    print("\n" + "=" * 80)
    print("Slack 訊息發送演示")
    print("=" * 80)

    try:
        slack = SlackIntegration()

        # 示例頻道（請替換為實際的頻道）
        CHANNEL = "#general"

        print(f"\n使用頻道: {CHANNEL}")
        print("（請替換為實際的頻道名稱或 ID）")

        # 1. 發送簡單訊息
        print("\n1. 發送簡單訊息（示例）")
        print(f"   slack.send_message('{CHANNEL}', 'Hello from Composio!')")

        # 2. 發送富文本訊息
        print("\n2. 發送富文本訊息（示例）")
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "系統通知"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*重要更新*\n我們的系統已成功部署新版本。"
                }
            }
        ]
        print(f"   slack.send_rich_message('{CHANNEL}', blocks)")

    except Exception as e:
        print(f"\n演示過程中發生錯誤: {e}")


def demo_channel_management():
    """
    演示頻道管理功能
    """
    print("\n" + "=" * 80)
    print("Slack 頻道管理演示")
    print("=" * 80)

    try:
        slack = SlackIntegration()

        # 1. 列出頻道
        print("\n1. 列出所有頻道")
        channels = slack.list_channels(limit=5)

        # 2. 創建頻道
        print("\n2. 創建新頻道（示例）")
        print("   slack.create_channel('project-updates', is_private=False)")

    except Exception as e:
        print(f"\n演示過程中發生錯誤: {e}")


def demo_automation_workflow():
    """
    演示自動化工作流程
    """
    print("\n" + "=" * 80)
    print("Slack 自動化工作流程演示")
    print("=" * 80)

    workflows = [
        ("每日站會提醒", [
            "設置定時任務",
            "發送提醒訊息到團隊頻道",
            "包含會議連結和議程"
        ]),
        ("代碼審查通知", [
            "監聽 GitHub PR 事件",
            "自動發送通知到 Slack",
            "標記相關的審查者"
        ]),
        ("錯誤告警", [
            "監控系統日誌",
            "檢測錯誤和異常",
            "即時通知到告警頻道"
        ]),
        ("新成員歡迎", [
            "檢測新成員加入",
            "自動發送歡迎訊息",
            "分享入職指南和資源"
        ])
    ]

    print("\n常見自動化場景:")
    print("-" * 80)
    for workflow, steps in workflows:
        print(f"\n{workflow}:")
        for i, step in enumerate(steps, 1):
            print(f"  {i}. {step}")


def main():
    """
    主函數
    """
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║              Composio Slack 整合範例                             ║
    ║                                                                  ║
    ║              自動化您的團隊溝通                                  ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)

    # 演示訊息發送
    demo_messaging()

    # 演示頻道管理
    demo_channel_management()

    # 演示自動化工作流程
    demo_automation_workflow()

    print("\n" + "=" * 80)
    print("Slack 整合最佳實踐:")
    print("  • 使用有意義的頻道名稱")
    print("  • 避免過度發送通知")
    print("  • 使用線程保持對話組織")
    print("  • 善用富文本格式提升可讀性")
    print("  • 定期清理不活躍的頻道")
    print("=" * 80)


if __name__ == "__main__":
    main()
