#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Composio 認證管理範例
=====================

本範例展示如何使用 Composio 管理應用程式認證，包括：
1. OAuth 2.0 認證流程
2. API Key 管理
3. 多實體認證
4. 令牌刷新和管理
5. 連接狀態檢查
6. 認證安全最佳實踐
7. 企業級認證管理

Composio 提供統一的認證管理系統，支援多種認證方式。

作者: Composio 團隊
日期: 2025-01-01
"""

import os
import sys
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
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


class AuthenticationManager:
    """
    認證管理類別

    提供完整的認證管理功能，包括：
    - OAuth 流程管理
    - API Key 管理
    - 多實體支援
    - 令牌生命週期管理
    - 安全性檢查
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化認證管理器

        Args:
            api_key: Composio API 金鑰
        """
        print("=" * 70)
        print("初始化認證管理器")
        print("=" * 70)

        self.api_key = api_key or os.getenv("COMPOSIO_API_KEY")

        if not self.api_key:
            raise ValueError("COMPOSIO_API_KEY 未設置")

        try:
            # 初始化 Composio 客戶端
            self.client = Composio(api_key=self.api_key)
            print("✓ Composio 客戶端初始化成功")

            # 實體字典，用於管理多個實體
            self.entities = {}

        except Exception as e:
            print(f"✗ 初始化失敗: {e}")
            raise

    def create_entity(self, entity_id: str) -> Any:
        """
        創建或獲取實體

        實體代表一個用戶或組織，每個實體可以有自己的連接。

        Args:
            entity_id: 實體 ID

        Returns:
            實體對象
        """
        print("\n" + "=" * 70)
        print(f"創建/獲取實體: {entity_id}")
        print("=" * 70)

        try:
            # 獲取或創建實體
            entity = self.client.get_entity(id=entity_id)

            # 保存到實體字典
            self.entities[entity_id] = entity

            print(f"✓ 實體 '{entity_id}' 已就緒")
            return entity

        except Exception as e:
            print(f"✗ 創建實體失敗: {e}")
            return None

    def get_entity(self, entity_id: str = "default") -> Any:
        """
        獲取實體

        Args:
            entity_id: 實體 ID

        Returns:
            實體對象
        """
        if entity_id not in self.entities:
            return self.create_entity(entity_id)
        return self.entities[entity_id]

    def initiate_oauth_connection(self, app_name: str, entity_id: str = "default",
                                  redirect_url: str = "http://localhost:8000/callback",
                                  labels: Optional[List[str]] = None) -> Optional[str]:
        """
        啟動 OAuth 認證流程

        Args:
            app_name: 應用程式名稱
            entity_id: 實體 ID
            redirect_url: OAuth 回調 URL
            labels: 連接標籤

        Returns:
            授權 URL
        """
        print("\n" + "=" * 70)
        print(f"啟動 OAuth 認證: {app_name}")
        print("=" * 70)

        try:
            # 獲取實體
            entity = self.get_entity(entity_id)

            # 構建參數
            params = {
                "redirect_url": redirect_url
            }

            if labels:
                params["labels"] = labels

            # 啟動連接
            connection_request = entity.initiate_connection(
                app_name=app_name,
                **params
            )

            if hasattr(connection_request, 'redirectUrl'):
                auth_url = connection_request.redirectUrl
                connection_id = connection_request.connectionId

                print(f"\n✓ OAuth 流程已啟動")
                print(f"  連接 ID: {connection_id}")
                print(f"  授權 URL: {auth_url}")
                print(f"\n請訪問以下 URL 完成授權:")
                print(f"{auth_url}")

                return auth_url
            else:
                print("✓ 連接已建立（無需 OAuth）")
                return None

        except Exception as e:
            print(f"✗ 啟動 OAuth 失敗: {e}")
            return None

    def add_api_key_connection(self, app_name: str, api_key: str,
                              entity_id: str = "default",
                              additional_params: Optional[Dict] = None) -> bool:
        """
        添加 API Key 認證連接

        Args:
            app_name: 應用程式名稱
            api_key: API Key
            entity_id: 實體 ID
            additional_params: 額外參數

        Returns:
            是否成功
        """
        print("\n" + "=" * 70)
        print(f"添加 API Key 連接: {app_name}")
        print("=" * 70)

        try:
            # 獲取實體
            entity = self.get_entity(entity_id)

            # 構建認證數據
            auth_config = {
                "api_key": api_key
            }

            if additional_params:
                auth_config.update(additional_params)

            # 創建連接
            connection = entity.create_connection(
                app_name=app_name,
                auth_mode="API_KEY",
                auth_config=auth_config
            )

            print(f"\n✓ API Key 連接已添加")
            print(f"  連接 ID: {connection.id}")

            return True

        except Exception as e:
            print(f"✗ 添加 API Key 連接失敗: {e}")
            return False

    def list_connections(self, entity_id: str = "default",
                        app_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        列出實體的所有連接

        Args:
            entity_id: 實體 ID
            app_name: 過濾特定應用程式（可選）

        Returns:
            連接列表
        """
        print("\n" + "=" * 70)
        if app_name:
            print(f"列出 {app_name} 的連接")
        else:
            print(f"列出實體 '{entity_id}' 的所有連接")
        print("=" * 70)

        try:
            # 獲取實體
            entity = self.get_entity(entity_id)

            # 獲取連接
            if app_name:
                connections = entity.get_connections(app_name=app_name)
            else:
                connections = entity.get_connections()

            print(f"\n找到 {len(connections)} 個連接:")
            print("-" * 70)

            for i, conn in enumerate(connections, 1):
                print(f"{i}. 連接 ID: {conn.id}")
                print(f"   應用: {conn.appName}")
                print(f"   狀態: {conn.status}")
                print(f"   創建時間: {conn.createdAt}")
                if hasattr(conn, 'labels') and conn.labels:
                    print(f"   標籤: {', '.join(conn.labels)}")
                print()

            return connections

        except Exception as e:
            print(f"✗ 列出連接失敗: {e}")
            return []

    def get_connection_info(self, connection_id: str,
                           entity_id: str = "default") -> Dict[str, Any]:
        """
        獲取連接詳細資訊

        Args:
            connection_id: 連接 ID
            entity_id: 實體 ID

        Returns:
            連接資訊
        """
        print("\n" + "=" * 70)
        print(f"獲取連接資訊: {connection_id}")
        print("=" * 70)

        try:
            # 獲取實體
            entity = self.get_entity(entity_id)

            # 獲取連接
            connection = entity.get_connection(id=connection_id)

            print(f"\n連接詳細資訊:")
            print("-" * 70)
            print(f"  ID: {connection.id}")
            print(f"  應用: {connection.appName}")
            print(f"  狀態: {connection.status}")
            print(f"  創建時間: {connection.createdAt}")
            print(f"  更新時間: {connection.updatedAt}")

            if hasattr(connection, 'integrationId'):
                print(f"  整合 ID: {connection.integrationId}")

            return connection.__dict__

        except Exception as e:
            print(f"✗ 獲取連接資訊失敗: {e}")
            return {}

    def check_connection_status(self, app_name: str,
                               entity_id: str = "default") -> Dict[str, Any]:
        """
        檢查應用程式連接狀態

        Args:
            app_name: 應用程式名稱
            entity_id: 實體 ID

        Returns:
            狀態資訊
        """
        print("\n" + "=" * 70)
        print(f"檢查連接狀態: {app_name}")
        print("=" * 70)

        try:
            # 獲取實體
            entity = self.get_entity(entity_id)

            # 獲取連接
            connections = entity.get_connections(app_name=app_name)

            status_info = {
                "app_name": app_name,
                "is_connected": len(connections) > 0,
                "connection_count": len(connections),
                "connections": []
            }

            if connections:
                print(f"✓ {app_name} 已連接")
                print(f"  連接數量: {len(connections)}")

                for conn in connections:
                    status_info["connections"].append({
                        "id": conn.id,
                        "status": conn.status,
                        "created_at": conn.createdAt
                    })
            else:
                print(f"✗ {app_name} 尚未連接")

            return status_info

        except Exception as e:
            print(f"✗ 檢查連接狀態失敗: {e}")
            return {
                "app_name": app_name,
                "is_connected": False,
                "error": str(e)
            }

    def delete_connection(self, connection_id: str,
                         entity_id: str = "default") -> bool:
        """
        刪除連接

        Args:
            connection_id: 連接 ID
            entity_id: 實體 ID

        Returns:
            是否成功
        """
        print("\n" + "=" * 70)
        print(f"刪除連接: {connection_id}")
        print("=" * 70)

        try:
            # 獲取實體
            entity = self.get_entity(entity_id)

            # 刪除連接
            entity.delete_connection(id=connection_id)

            print(f"✓ 連接已刪除")
            return True

        except Exception as e:
            print(f"✗ 刪除連接失敗: {e}")
            return False

    def refresh_connection(self, connection_id: str,
                          entity_id: str = "default") -> bool:
        """
        刷新連接（令牌）

        Args:
            connection_id: 連接 ID
            entity_id: 實體 ID

        Returns:
            是否成功
        """
        print("\n" + "=" * 70)
        print(f"刷新連接: {connection_id}")
        print("=" * 70)

        try:
            # 獲取實體
            entity = self.get_entity(entity_id)

            # 刷新連接
            # 注意: 實際的刷新方法可能因 SDK 版本而異
            print(f"⚠ 令牌刷新通常由 Composio 自動處理")
            print(f"  如遇到認證問題，請重新建立連接")

            return True

        except Exception as e:
            print(f"✗ 刷新連接失敗: {e}")
            return False

    def get_connected_apps(self, entity_id: str = "default") -> List[str]:
        """
        獲取所有已連接的應用程式

        Args:
            entity_id: 實體 ID

        Returns:
            應用程式名稱列表
        """
        print("\n" + "=" * 70)
        print("獲取已連接的應用程式")
        print("=" * 70)

        try:
            # 獲取所有連接
            connections = self.list_connections(entity_id=entity_id)

            # 提取唯一的應用程式名稱
            apps = list(set([conn.appName for conn in connections]))

            print(f"\n已連接的應用程式:")
            print("-" * 70)
            for i, app in enumerate(apps, 1):
                print(f"{i}. {app}")

            return apps

        except Exception as e:
            print(f"✗ 獲取已連接應用程式失敗: {e}")
            return []

    def validate_connection(self, app_name: str,
                           entity_id: str = "default") -> bool:
        """
        驗證連接是否有效

        Args:
            app_name: 應用程式名稱
            entity_id: 實體 ID

        Returns:
            是否有效
        """
        print("\n" + "=" * 70)
        print(f"驗證連接: {app_name}")
        print("=" * 70)

        try:
            # 檢查連接狀態
            status = self.check_connection_status(app_name, entity_id)

            if not status["is_connected"]:
                print(f"✗ 未連接")
                return False

            # 嘗試執行一個簡單的操作來驗證連接
            entity = self.get_entity(entity_id)

            # 獲取應用的工具列表作為驗證
            tools = self.client.actions.get(apps=[app_name])

            if tools:
                print(f"✓ 連接有效")
                print(f"  可用工具數量: {len(tools)}")
                return True
            else:
                print(f"✗ 連接可能無效（無可用工具）")
                return False

        except Exception as e:
            print(f"✗ 驗證連接失敗: {e}")
            return False


def demo_oauth_flow():
    """
    演示 OAuth 認證流程
    """
    print("\n" + "=" * 80)
    print("OAuth 認證流程演示")
    print("=" * 80)

    try:
        auth_manager = AuthenticationManager()

        # OAuth 流程步驟
        print("\nOAuth 2.0 認證流程:")
        print("-" * 80)

        steps = [
            ("1. 啟動 OAuth 流程", "調用 initiate_oauth_connection()"),
            ("2. 用戶訪問授權 URL", "在瀏覽器中打開返回的 URL"),
            ("3. 用戶授權應用", "在第三方應用中授權"),
            ("4. 重定向回調", "用戶被重定向到回調 URL"),
            ("5. 交換令牌", "Composio 自動交換訪問令牌"),
            ("6. 保存連接", "連接資訊被保存")
        ]

        for step, description in steps:
            print(f"{step}")
            print(f"   {description}")
            print()

        # 示例：啟動 GitHub OAuth
        print("示例：啟動 GitHub OAuth 認證")
        print("-" * 80)
        print("auth_url = auth_manager.initiate_oauth_connection('github')")
        print("# 訪問 auth_url 完成授權")

    except Exception as e:
        print(f"\n演示過程中發生錯誤: {e}")


def demo_api_key_auth():
    """
    演示 API Key 認證
    """
    print("\n" + "=" * 80)
    print("API Key 認證演示")
    print("=" * 80)

    try:
        auth_manager = AuthenticationManager()

        # API Key 認證步驟
        print("\nAPI Key 認證流程:")
        print("-" * 80)

        steps = [
            ("1. 從應用獲取 API Key", "在第三方應用中生成 API Key"),
            ("2. 添加到 Composio", "調用 add_api_key_connection()"),
            ("3. 驗證連接", "測試 API Key 是否有效"),
            ("4. 開始使用", "使用工具執行操作")
        ]

        for step, description in steps:
            print(f"{step}")
            print(f"   {description}")
            print()

        # 示例代碼
        print("示例代碼:")
        print("-" * 80)
        print("""
auth_manager.add_api_key_connection(
    app_name='openai',
    api_key='sk-...',
    additional_params={
        'organization': 'org-...'
    }
)
        """)

    except Exception as e:
        print(f"\n演示過程中發生錯誤: {e}")


def demo_multi_entity_management():
    """
    演示多實體管理
    """
    print("\n" + "=" * 80)
    print("多實體管理演示")
    print("=" * 80)

    try:
        auth_manager = AuthenticationManager()

        # 多實體使用場景
        print("\n多實體使用場景:")
        print("-" * 80)

        scenarios = [
            ("多租戶應用", "每個客戶是一個實體，有獨立的連接"),
            ("團隊協作", "每個團隊成員是一個實體"),
            ("多帳號管理", "同一用戶的不同帳號"),
            ("測試環境", "生產和測試環境分離")
        ]

        for scenario, description in scenarios:
            print(f"• {scenario}")
            print(f"  {description}")
            print()

        # 示例代碼
        print("示例代碼:")
        print("-" * 80)
        print("""
# 為不同用戶創建實體
user1_entity = auth_manager.create_entity('user_123')
user2_entity = auth_manager.create_entity('user_456')

# 每個實體有獨立的連接
auth_manager.initiate_oauth_connection('github', entity_id='user_123')
auth_manager.initiate_oauth_connection('github', entity_id='user_456')
        """)

    except Exception as e:
        print(f"\n演示過程中發生錯誤: {e}")


def print_security_best_practices():
    """
    印出安全最佳實踐
    """
    print("\n" + "=" * 80)
    print("認證安全最佳實踐")
    print("=" * 80)

    practices = [
        ("1. API Key 管理", [
            "永遠不要將 API Key 硬編碼在代碼中",
            "使用環境變數或密鑰管理服務",
            "定期輪換 API Key",
            "為不同環境使用不同的 Key",
            "立即撤銷洩露的 Key"
        ]),
        ("2. OAuth 安全", [
            "使用 HTTPS 重定向 URL",
            "驗證 state 參數防止 CSRF",
            "妥善保管客戶端密鑰",
            "使用最小權限原則",
            "實施令牌刷新機制"
        ]),
        ("3. 連接管理", [
            "定期審查活躍連接",
            "刪除不使用的連接",
            "監控異常活動",
            "實施訪問日誌",
            "使用連接標籤組織管理"
        ]),
        ("4. 多實體安全", [
            "實施實體隔離",
            "驗證實體訪問權限",
            "記錄實體操作",
            "防止跨實體數據洩露",
            "實施實體級別的配額限制"
        ]),
        ("5. 合規性", [
            "遵守數據保護法規（GDPR、CCPA）",
            "實施數據加密",
            "提供用戶數據刪除功能",
            "記錄和審計訪問",
            "定期安全評估"
        ])
    ]

    for title, items in practices:
        print(f"\n{title}")
        print("-" * 80)
        for item in items:
            print(f"  • {item}")


def main():
    """
    主函數
    """
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║              Composio 認證管理範例                               ║
    ║                                                                  ║
    ║              安全、統一的認證管理解決方案                        ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)

    # 演示 OAuth 流程
    demo_oauth_flow()

    # 演示 API Key 認證
    demo_api_key_auth()

    # 演示多實體管理
    demo_multi_entity_management()

    # 印出安全最佳實踐
    print_security_best_practices()

    print("\n" + "=" * 80)
    print("更多資源:")
    print("  • 認證文檔: https://docs.composio.dev/authentication")
    print("  • 安全指南: https://docs.composio.dev/security")
    print("  • API 參考: https://docs.composio.dev/api-reference")
    print("=" * 80)


if __name__ == "__main__":
    main()
