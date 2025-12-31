#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Composio 快速開始範例
====================

本範例展示如何快速開始使用 Composio 平台，包括：
1. 安裝和配置 Composio
2. 初始化客戶端
3. 探索可用的應用程式和工具
4. 執行基本的工具操作
5. 管理實體和連接
6. 錯誤處理和最佳實踐

Composio 是一個強大的 AI 工具整合平台，連接 250+ 應用程式和 10,000+ 工具。

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


class ComposioQuickStart:
    """
    Composio 快速開始類別

    提供 Composio 平台的基礎功能演示，包括：
    - 客戶端初始化
    - 應用程式探索
    - 工具使用
    - 連接管理
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 Composio 客戶端

        Args:
            api_key: Composio API 金鑰（可選，會從環境變數讀取）
        """
        print("=" * 60)
        print("初始化 Composio 客戶端")
        print("=" * 60)

        # 從參數或環境變數獲取 API 金鑰
        self.api_key = api_key or os.getenv("COMPOSIO_API_KEY")

        if not self.api_key:
            print("警告：未設定 COMPOSIO_API_KEY")
            print("請設定環境變數或在初始化時提供 API 金鑰")
            print("export COMPOSIO_API_KEY='your-api-key'")

        try:
            # 初始化 Composio 客戶端
            self.client = Composio(api_key=self.api_key)
            print("✓ Composio 客戶端初始化成功")

            # 獲取預設實體
            self.entity = self.client.get_entity(id="default")
            print("✓ 獲取預設實體成功")

        except ComposioException as e:
            print(f"✗ 初始化失敗: {e}")
            raise
        except Exception as e:
            print(f"✗ 未預期的錯誤: {e}")
            raise

    def list_available_apps(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        列出可用的應用程式

        Args:
            limit: 限制返回的應用程式數量

        Returns:
            應用程式列表
        """
        print("\n" + "=" * 60)
        print("探索可用的應用程式")
        print("=" * 60)

        try:
            # 獲取所有可用的應用程式
            apps = self.client.apps.get()

            print(f"\n找到 {len(apps)} 個可用的應用程式")
            print("\n常用應用程式範例：")
            print("-" * 60)

            # 顯示前 N 個應用程式
            for i, app in enumerate(apps[:limit], 1):
                app_key = app.key if hasattr(app, 'key') else 'unknown'
                app_name = app.name if hasattr(app, 'name') else 'Unknown'
                print(f"{i}. {app_name} ({app_key})")

            if len(apps) > limit:
                print(f"... 還有 {len(apps) - limit} 個應用程式")

            return apps

        except Exception as e:
            print(f"✗ 獲取應用程式列表失敗: {e}")
            return []

    def list_available_tools(self, app_name: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        列出可用的工具

        Args:
            app_name: 特定應用程式名稱（可選）
            limit: 限制返回的工具數量

        Returns:
            工具列表
        """
        print("\n" + "=" * 60)
        if app_name:
            print(f"探索 {app_name} 的可用工具")
        else:
            print("探索所有可用工具")
        print("=" * 60)

        try:
            # 獲取工具列表
            if app_name:
                tools = self.client.actions.get(apps=[app_name])
            else:
                tools = self.client.actions.get()

            print(f"\n找到 {len(tools)} 個可用的工具")
            print("\n工具範例：")
            print("-" * 60)

            # 顯示前 N 個工具
            for i, tool in enumerate(tools[:limit], 1):
                action_name = tool.name if hasattr(tool, 'name') else 'unknown'
                description = tool.description if hasattr(tool, 'description') else '無描述'
                print(f"{i}. {action_name}")
                print(f"   描述: {description[:80]}...")
                print()

            if len(tools) > limit:
                print(f"... 還有 {len(tools) - limit} 個工具")

            return tools

        except Exception as e:
            print(f"✗ 獲取工具列表失敗: {e}")
            return []

    def get_tool_details(self, action_name: str) -> Dict[str, Any]:
        """
        獲取工具的詳細資訊

        Args:
            action_name: 工具名稱

        Returns:
            工具詳細資訊
        """
        print("\n" + "=" * 60)
        print(f"獲取工具詳細資訊: {action_name}")
        print("=" * 60)

        try:
            # 獲取特定工具的詳細資訊
            action = self.client.actions.get(actions=[action_name])[0]

            print(f"\n工具名稱: {action.name}")
            print(f"描述: {action.description}")

            if hasattr(action, 'parameters'):
                print("\n參數:")
                print("-" * 60)
                for param_name, param_info in action.parameters.items():
                    required = param_info.get('required', False)
                    param_type = param_info.get('type', 'unknown')
                    param_desc = param_info.get('description', '無描述')

                    required_marker = "必填" if required else "可選"
                    print(f"  {param_name} ({param_type}) - {required_marker}")
                    print(f"    {param_desc}")

            return action

        except Exception as e:
            print(f"✗ 獲取工具詳細資訊失敗: {e}")
            return {}

    def check_connection_status(self, app_name: str) -> bool:
        """
        檢查應用程式連接狀態

        Args:
            app_name: 應用程式名稱

        Returns:
            是否已連接
        """
        print("\n" + "=" * 60)
        print(f"檢查 {app_name} 連接狀態")
        print("=" * 60)

        try:
            # 獲取連接狀態
            connections = self.entity.get_connections(app_name=app_name)

            if connections:
                print(f"✓ {app_name} 已連接")
                for conn in connections:
                    print(f"  連接 ID: {conn.id}")
                    print(f"  狀態: {conn.status}")
                return True
            else:
                print(f"✗ {app_name} 尚未連接")
                return False

        except Exception as e:
            print(f"✗ 檢查連接狀態失敗: {e}")
            return False

    def initiate_connection(self, app_name: str) -> Optional[str]:
        """
        啟動應用程式連接流程

        Args:
            app_name: 應用程式名稱

        Returns:
            授權 URL（如需要）
        """
        print("\n" + "=" * 60)
        print(f"啟動 {app_name} 連接流程")
        print("=" * 60)

        try:
            # 啟動連接
            connection_request = self.entity.initiate_connection(
                app_name=app_name,
                redirect_url="http://localhost:8000/callback"  # 回調 URL
            )

            if hasattr(connection_request, 'redirectUrl'):
                auth_url = connection_request.redirectUrl
                print(f"\n請訪問以下 URL 進行授權:")
                print(f"{auth_url}")
                print("\n授權完成後，連接將自動建立")
                return auth_url
            else:
                print("✓ 連接已建立（無需 OAuth）")
                return None

        except Exception as e:
            print(f"✗ 啟動連接失敗: {e}")
            return None

    def execute_simple_action(self, action_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        執行簡單的工具操作

        Args:
            action_name: 工具名稱
            params: 工具參數

        Returns:
            執行結果
        """
        print("\n" + "=" * 60)
        print(f"執行工具: {action_name}")
        print("=" * 60)

        print(f"\n參數:")
        print(json.dumps(params, indent=2, ensure_ascii=False))

        try:
            # 執行工具
            result = self.entity.execute(
                action=action_name,
                params=params
            )

            print("\n執行結果:")
            print("-" * 60)
            print(json.dumps(result, indent=2, ensure_ascii=False))

            return result

        except ComposioException as e:
            print(f"✗ 執行失敗: {e}")
            return {"error": str(e)}
        except Exception as e:
            print(f"✗ 未預期的錯誤: {e}")
            return {"error": str(e)}

    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        獲取執行歷史記錄

        Args:
            limit: 限制返回的記錄數量

        Returns:
            執行歷史列表
        """
        print("\n" + "=" * 60)
        print("獲取執行歷史記錄")
        print("=" * 60)

        try:
            # 獲取執行歷史
            history = self.client.get_execution_logs(
                entity_id="default",
                limit=limit
            )

            print(f"\n找到 {len(history)} 條執行記錄")
            print("\n最近的執行:")
            print("-" * 60)

            for i, record in enumerate(history[:limit], 1):
                action_name = record.get('action', 'unknown')
                status = record.get('status', 'unknown')
                timestamp = record.get('timestamp', 'unknown')

                print(f"{i}. {action_name} - {status}")
                print(f"   時間: {timestamp}")

            return history

        except Exception as e:
            print(f"✗ 獲取執行歷史失敗: {e}")
            return []


def demo_basic_workflow():
    """
    演示基本工作流程
    """
    print("\n" + "=" * 80)
    print("Composio 基本工作流程演示")
    print("=" * 80)

    try:
        # 1. 初始化客戶端
        composio = ComposioQuickStart()

        # 2. 探索可用的應用程式
        apps = composio.list_available_apps(limit=10)

        # 3. 探索可用的工具
        tools = composio.list_available_tools(limit=10)

        # 4. 獲取特定工具的詳細資訊
        # 注意：這裡使用示例工具名稱，實際使用時需要根據可用工具調整
        print("\n提示：要獲取特定工具的詳細資訊，請使用:")
        print("composio.get_tool_details('TOOL_NAME')")

        # 5. 檢查連接狀態（示例）
        print("\n提示：要檢查應用程式連接狀態，請使用:")
        print("composio.check_connection_status('APP_NAME')")

        print("\n" + "=" * 80)
        print("演示完成!")
        print("=" * 80)

    except Exception as e:
        print(f"\n演示過程中發生錯誤: {e}")


def demo_error_handling():
    """
    演示錯誤處理
    """
    print("\n" + "=" * 80)
    print("錯誤處理演示")
    print("=" * 80)

    try:
        # 嘗試使用無效的 API 金鑰
        print("\n1. 測試無效的 API 金鑰:")
        try:
            invalid_client = ComposioQuickStart(api_key="invalid-key")
        except Exception as e:
            print(f"   預期的錯誤: {e}")

        # 嘗試執行不存在的工具
        print("\n2. 測試執行不存在的工具:")
        composio = ComposioQuickStart()
        result = composio.execute_simple_action(
            action_name="NONEXISTENT_ACTION",
            params={}
        )

        print("\n3. 錯誤處理最佳實踐:")
        print("   - 總是使用 try-except 塊")
        print("   - 檢查 API 金鑰的有效性")
        print("   - 驗證工具名稱和參數")
        print("   - 處理網路錯誤和超時")
        print("   - 記錄錯誤以便除錯")

    except Exception as e:
        print(f"\n錯誤處理演示中的錯誤: {e}")


def print_best_practices():
    """
    印出最佳實踐建議
    """
    print("\n" + "=" * 80)
    print("Composio 使用最佳實踐")
    print("=" * 80)

    practices = [
        ("1. 安全管理 API 金鑰", [
            "使用環境變數存儲 API 金鑰",
            "不要將金鑰硬編碼在代碼中",
            "定期輪換金鑰",
            "使用 .env 文件並加入 .gitignore"
        ]),
        ("2. 錯誤處理", [
            "總是使用 try-except 塊",
            "處理特定的異常類型",
            "提供有用的錯誤訊息",
            "實現重試邏輯"
        ]),
        ("3. 性能優化", [
            "使用批次處理減少 API 調用",
            "快取常用的結果",
            "並行執行獨立的操作",
            "監控 API 使用量"
        ]),
        ("4. 測試", [
            "在生產環境前充分測試",
            "使用測試環境和測試帳號",
            "編寫單元測試",
            "模擬 API 回應"
        ]),
        ("5. 監控和日誌", [
            "啟用詳細的日誌記錄",
            "監控 API 調用頻率",
            "追蹤錯誤率",
            "設置告警機制"
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
    ║              Composio 快速開始範例                               ║
    ║                                                                  ║
    ║              AI 工具整合平台                                     ║
    ║              250+ 應用 | 10,000+ 工具                           ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)

    # 執行基本工作流程演示
    demo_basic_workflow()

    # 執行錯誤處理演示
    demo_error_handling()

    # 印出最佳實踐
    print_best_practices()

    print("\n" + "=" * 80)
    print("更多資源:")
    print("  • 官方文檔: https://docs.composio.dev")
    print("  • GitHub: https://github.com/ComposioHQ/composio")
    print("  • Discord: https://discord.gg/composio")
    print("=" * 80)


if __name__ == "__main__":
    main()
