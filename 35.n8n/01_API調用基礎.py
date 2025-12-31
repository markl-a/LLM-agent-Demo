"""
n8n API 調用基礎
================

本範例展示如何使用 n8n REST API 進行基礎操作，包括：
- 認證配置
- 獲取工作流列表
- 執行工作流
- 查詢執行歷史

安裝依賴:
pip install requests python-dotenv

作者: n8n Demo
日期: 2025-12-31
"""

import os
import requests
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from datetime import datetime

# 加載環境變量
load_dotenv()


class N8NAPIClient:
    """
    n8n REST API 客戶端基礎類

    提供與 n8n 服務器交互的基礎方法
    """

    def __init__(
        self,
        base_url: str = "http://localhost:5678",
        api_key: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        初始化 n8n API 客戶端

        參數:
            base_url: n8n 服務器地址
            api_key: API 密鑰（推薦）
            username: 基本認證用戶名
            password: 基本認證密碼
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv("N8N_API_KEY")
        self.username = username or os.getenv("N8N_USERNAME")
        self.password = password or os.getenv("N8N_PASSWORD")

        # 創建會話以重用連接
        self.session = requests.Session()
        self._setup_auth()

        print(f"✓ n8n API 客戶端已初始化")
        print(f"  服務器地址: {self.base_url}")
        print(f"  認證方式: {'API Key' if self.api_key else 'Basic Auth' if self.username else '無'}")

    def _setup_auth(self):
        """設置認證方式"""
        if self.api_key:
            # 使用 API Key 認證
            self.session.headers.update({
                "X-N8N-API-KEY": self.api_key,
                "Content-Type": "application/json"
            })
        elif self.username and self.password:
            # 使用基本認證
            self.session.auth = (self.username, self.password)
            self.session.headers.update({
                "Content-Type": "application/json"
            })
        else:
            # 無認證
            self.session.headers.update({
                "Content-Type": "application/json"
            })

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        發送 HTTP 請求的通用方法

        參數:
            method: HTTP 方法 (GET, POST, PUT, DELETE, PATCH)
            endpoint: API 端點
            data: 請求體數據
            params: URL 查詢參數

        返回:
            響應的 JSON 數據
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=30
            )

            response.raise_for_status()

            # 處理空響應
            if response.status_code == 204 or not response.content:
                return {}

            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"✗ API 請求錯誤: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"  錯誤詳情: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
                except:
                    print(f"  響應內容: {e.response.text}")
            raise

    def example_1_get_workflows(self) -> List[Dict[str, Any]]:
        """
        示例 1: 獲取所有工作流列表

        返回:
            工作流列表
        """
        print("\n" + "="*60)
        print("示例 1: 獲取所有工作流列表")
        print("="*60)

        try:
            # 調用 API 獲取工作流
            workflows = self._make_request("GET", "/api/v1/workflows")

            print(f"\n找到 {len(workflows)} 個工作流:")

            for i, workflow in enumerate(workflows, 1):
                print(f"\n{i}. {workflow.get('name', 'Unnamed')}")
                print(f"   ID: {workflow.get('id')}")
                print(f"   狀態: {'啟用' if workflow.get('active') else '未啟用'}")
                print(f"   創建時間: {workflow.get('createdAt', 'N/A')}")
                print(f"   更新時間: {workflow.get('updatedAt', 'N/A')}")
                print(f"   節點數量: {len(workflow.get('nodes', []))}")

            print("\n✓ 工作流列表獲取成功")
            return workflows

        except Exception as e:
            print(f"\n✗ 獲取工作流失敗: {str(e)}")
            return []

    def example_2_get_workflow_by_id(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        示例 2: 獲取特定工作流的詳細信息

        參數:
            workflow_id: 工作流 ID

        返回:
            工作流詳細信息
        """
        print("\n" + "="*60)
        print("示例 2: 獲取特定工作流詳細信息")
        print("="*60)

        try:
            # 調用 API 獲取工作流詳情
            workflow = self._make_request("GET", f"/api/v1/workflows/{workflow_id}")

            print(f"\n工作流: {workflow.get('name')}")
            print(f"ID: {workflow.get('id')}")
            print(f"狀態: {'啟用' if workflow.get('active') else '未啟用'}")

            # 顯示節點信息
            nodes = workflow.get('nodes', [])
            print(f"\n節點列表 ({len(nodes)} 個):")
            for node in nodes:
                print(f"  - {node.get('name')} ({node.get('type')})")

            # 顯示連接信息
            connections = workflow.get('connections', {})
            print(f"\n連接數量: {len(connections)}")

            print("\n✓ 工作流詳情獲取成功")
            return workflow

        except Exception as e:
            print(f"\n✗ 獲取工作流詳情失敗: {str(e)}")
            return None

    def example_3_execute_workflow(
        self,
        workflow_id: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        示例 3: 執行工作流

        參數:
            workflow_id: 工作流 ID
            input_data: 輸入數據

        返回:
            執行結果
        """
        print("\n" + "="*60)
        print("示例 3: 執行工作流")
        print("="*60)

        try:
            # 準備執行數據
            execution_data = input_data or {}

            print(f"\n執行工作流 ID: {workflow_id}")
            if execution_data:
                print(f"輸入數據: {json.dumps(execution_data, indent=2, ensure_ascii=False)}")

            # 調用 API 執行工作流
            result = self._make_request(
                "POST",
                f"/api/v1/workflows/{workflow_id}/execute",
                data=execution_data
            )

            print(f"\n執行 ID: {result.get('id')}")
            print(f"狀態: {result.get('finished', False) and '完成' or '運行中'}")
            print(f"開始時間: {result.get('startedAt', 'N/A')}")

            if result.get('finished'):
                print(f"結束時間: {result.get('stoppedAt', 'N/A')}")

                # 顯示執行結果
                data = result.get('data', {})
                if data:
                    print("\n執行結果:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))

            print("\n✓ 工作流執行成功")
            return result

        except Exception as e:
            print(f"\n✗ 執行工作流失敗: {str(e)}")
            return None

    def example_4_get_executions(
        self,
        workflow_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        示例 4: 獲取執行歷史

        參數:
            workflow_id: 工作流 ID（可選，不指定則獲取所有）
            limit: 返回數量限制

        返回:
            執行歷史列表
        """
        print("\n" + "="*60)
        print("示例 4: 獲取執行歷史")
        print("="*60)

        try:
            # 準備查詢參數
            params = {"limit": limit}
            if workflow_id:
                params["workflowId"] = workflow_id

            # 調用 API 獲取執行歷史
            executions = self._make_request(
                "GET",
                "/api/v1/executions",
                params=params
            )

            # 處理分頁響應
            if isinstance(executions, dict) and 'data' in executions:
                executions_data = executions['data']
                print(f"\n找到 {executions.get('count', len(executions_data))} 次執行記錄:")
            else:
                executions_data = executions
                print(f"\n找到 {len(executions_data)} 次執行記錄:")

            for i, execution in enumerate(executions_data, 1):
                print(f"\n{i}. 執行 ID: {execution.get('id')}")
                print(f"   工作流: {execution.get('workflowId')}")
                print(f"   狀態: {execution.get('status', 'unknown')}")
                print(f"   開始時間: {execution.get('startedAt', 'N/A')}")
                if execution.get('finished'):
                    print(f"   完成時間: {execution.get('stoppedAt', 'N/A')}")
                print(f"   模式: {execution.get('mode', 'N/A')}")

            print("\n✓ 執行歷史獲取成功")
            return executions_data

        except Exception as e:
            print(f"\n✗ 獲取執行歷史失敗: {str(e)}")
            return []

    def example_5_get_execution_by_id(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        示例 5: 獲取特定執行的詳細信息

        參數:
            execution_id: 執行 ID

        返回:
            執行詳細信息
        """
        print("\n" + "="*60)
        print("示例 5: 獲取特定執行詳細信息")
        print("="*60)

        try:
            # 調用 API 獲取執行詳情
            execution = self._make_request("GET", f"/api/v1/executions/{execution_id}")

            print(f"\n執行 ID: {execution.get('id')}")
            print(f"工作流 ID: {execution.get('workflowId')}")
            print(f"狀態: {execution.get('status')}")
            print(f"模式: {execution.get('mode')}")
            print(f"開始時間: {execution.get('startedAt')}")

            if execution.get('finished'):
                print(f"完成時間: {execution.get('stoppedAt')}")

            # 顯示執行數據
            data = execution.get('data', {})
            if data:
                print("\n執行數據:")
                result_data = data.get('resultData', {})
                if result_data:
                    runs = result_data.get('runData', {})
                    print(f"  節點執行數量: {len(runs)}")

                    for node_name, node_runs in runs.items():
                        print(f"\n  節點: {node_name}")
                        for run_idx, run in enumerate(node_runs):
                            print(f"    運行 {run_idx + 1}:")
                            print(f"      開始時間: {run.get('startTime', 'N/A')}")
                            print(f"      執行時間: {run.get('executionTime', 0)} ms")
                            if run.get('data'):
                                main_data = run['data'].get('main', [[]])
                                if main_data and main_data[0]:
                                    print(f"      輸出項數: {len(main_data[0])}")

            print("\n✓ 執行詳情獲取成功")
            return execution

        except Exception as e:
            print(f"\n✗ 獲取執行詳情失敗: {str(e)}")
            return None

    def example_6_delete_execution(self, execution_id: str) -> bool:
        """
        示例 6: 刪除執行記錄

        參數:
            execution_id: 執行 ID

        返回:
            是否成功
        """
        print("\n" + "="*60)
        print("示例 6: 刪除執行記錄")
        print("="*60)

        try:
            print(f"\n刪除執行 ID: {execution_id}")

            # 調用 API 刪除執行記錄
            self._make_request("DELETE", f"/api/v1/executions/{execution_id}")

            print("\n✓ 執行記錄刪除成功")
            return True

        except Exception as e:
            print(f"\n✗ 刪除執行記錄失敗: {str(e)}")
            return False


def main():
    """
    主函數：演示所有 API 調用示例
    """
    print("\n" + "="*60)
    print("n8n API 調用基礎示例")
    print("="*60)

    # 配置參數（從環境變量讀取）
    BASE_URL = os.getenv("N8N_API_URL", "http://localhost:5678")
    API_KEY = os.getenv("N8N_API_KEY")
    USERNAME = os.getenv("N8N_USERNAME")
    PASSWORD = os.getenv("N8N_PASSWORD")

    # 初始化 API 客戶端
    client = N8NAPIClient(
        base_url=BASE_URL,
        api_key=API_KEY,
        username=USERNAME,
        password=PASSWORD
    )

    # 示例 1: 獲取所有工作流
    workflows = client.example_1_get_workflows()

    # 如果有工作流，執行後續示例
    if workflows:
        first_workflow = workflows[0]
        workflow_id = first_workflow['id']

        # 示例 2: 獲取工作流詳情
        client.example_2_get_workflow_by_id(workflow_id)

        # 示例 3: 執行工作流
        execution_result = client.example_3_execute_workflow(
            workflow_id=workflow_id,
            input_data={
                "message": "Hello from Python!",
                "timestamp": datetime.now().isoformat()
            }
        )

        # 示例 4: 獲取執行歷史
        executions = client.example_4_get_executions(
            workflow_id=workflow_id,
            limit=5
        )

        # 示例 5: 獲取執行詳情
        if executions:
            execution_id = executions[0]['id']
            client.example_5_get_execution_by_id(execution_id)

            # 示例 6: 刪除執行記錄（謹慎使用）
            # client.example_6_delete_execution(execution_id)

    else:
        print("\n提示: 當前沒有工作流。請在 n8n UI 中創建一個工作流後再運行示例。")

    print("\n" + "="*60)
    print("所有示例運行完成！")
    print("="*60)

    # 使用提示
    print("\n使用提示:")
    print("1. 確保 n8n 服務正在運行（默認端口 5678）")
    print("2. 設置環境變量:")
    print("   export N8N_API_URL='http://localhost:5678'")
    print("   export N8N_API_KEY='your-api-key'  # 如果啟用了 API 認證")
    print("3. 或使用基本認證:")
    print("   export N8N_USERNAME='admin'")
    print("   export N8N_PASSWORD='password'")
    print("4. 在 n8n UI 中創建至少一個工作流進行測試")


if __name__ == "__main__":
    # 運行示例
    main()

    # 額外說明
    print("\n" + "-"*60)
    print("n8n API 最佳實踐:")
    print("-"*60)
    print("""
    1. 認證方式
       - 優先使用 API Key 認證（更安全）
       - 在 n8n 設置中生成 API Key
       - 使用環境變量存儲敏感信息

    2. 錯誤處理
       - 始終檢查 HTTP 狀態碼
       - 處理網絡超時和連接錯誤
       - 記錄詳細的錯誤信息

    3. 性能優化
       - 使用 Session 重用 HTTP 連接
       - 設置合理的超時時間
       - 分頁獲取大量數據

    4. 安全性
       - 不要在代碼中硬編碼密鑰
       - 使用 HTTPS 連接（生產環境）
       - 定期輪換 API Key

    5. 工作流管理
       - 使用有意義的工作流名稱
       - 定期備份工作流配置
       - 監控執行狀態和錯誤
    """)
