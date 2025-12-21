"""
Dify 工作流創建範例
===================

本範例展示如何使用 Dify 創建和執行工作流（Workflow）。
包含以下內容：
1. 工作流的基本概念
2. 執行工作流
3. 串流式工作流執行
4. 工作流狀態查詢
5. 工作流與對話流的區別

工作流類型：
- Workflow（工作流）：單輪生成，適合自動化和批處理任務
- Chatflow（對話流）：多輪對話，支持記憶和上下文

作者：Dify 範例教程
日期：2025
"""

import os
import json
import time
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
import requests


class DifyWorkflowManager:
    """Dify 工作流管理類"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化工作流管理器

        參數：
            api_key: Dify API 金鑰
            base_url: API 基礎 URL
        """
        load_dotenv()

        self.api_key = api_key or os.getenv("DIFY_API_KEY")
        if not self.api_key:
            raise ValueError("請設置 DIFY_API_KEY")

        self.base_url = base_url or os.getenv("DIFY_API_BASE", "https://api.dify.ai/v1")

        print("✓ 工作流管理器初始化完成")

    def run_workflow(
        self,
        inputs: Dict[str, Any],
        user_id: str = "default-user",
        response_mode: str = "blocking"
    ) -> Dict[str, Any]:
        """
        執行工作流（阻塞模式）

        參數：
            inputs: 工作流輸入參數（字典格式）
            user_id: 用戶 ID
            response_mode: 回應模式 - "blocking" 或 "streaming"

        返回：
            工作流執行結果
        """
        print(f"\n{'='*60}")
        print("執行工作流")
        print(f"{'='*60}")
        print(f"輸入參數：{json.dumps(inputs, ensure_ascii=False, indent=2)}")
        print(f"回應模式：{response_mode}")

        url = f"{self.base_url}/workflows/run"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": inputs,
            "user": user_id,
            "response_mode": response_mode
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            result = response.json()

            print(f"\n執行狀態：{result.get('status', 'unknown')}")
            print(f"工作流 ID：{result.get('workflow_run_id', 'N/A')}")

            # 顯示輸出
            outputs = result.get('data', {}).get('outputs', {})
            if outputs:
                print(f"\n輸出結果：")
                print(json.dumps(outputs, ensure_ascii=False, indent=2))

            return result

        except requests.exceptions.RequestException as e:
            print(f"執行工作流失敗：{e}")
            return {"error": str(e)}

    def run_workflow_streaming(self, inputs: Dict[str, Any], user_id: str = "default-user"):
        """
        以串流方式執行工作流

        參數：
            inputs: 工作流輸入參數
            user_id: 用戶 ID
        """
        print(f"\n{'='*60}")
        print("串流執行工作流")
        print(f"{'='*60}")
        print(f"輸入參數：{json.dumps(inputs, ensure_ascii=False, indent=2)}")

        url = f"{self.base_url}/workflows/run"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": inputs,
            "user": user_id,
            "response_mode": "streaming"
        }

        try:
            response = requests.post(url, headers=headers, json=payload, stream=True, timeout=60)
            response.raise_for_status()

            print("\n執行過程（串流）：")
            workflow_run_id = None
            outputs = {}

            # 處理 Server-Sent Events
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')

                    if line_str.startswith('data: '):
                        data_str = line_str[6:]

                        try:
                            data = json.loads(data_str)
                            event = data.get('event')

                            if event == 'workflow_started':
                                # 工作流開始
                                workflow_run_id = data.get('workflow_run_id')
                                print(f"✓ 工作流已啟動 - ID: {workflow_run_id}")

                            elif event == 'node_started':
                                # 節點開始執行
                                node_data = data.get('data', {})
                                print(f"  → 開始執行節點: {node_data.get('title', 'unknown')}")

                            elif event == 'node_finished':
                                # 節點執行完成
                                node_data = data.get('data', {})
                                print(f"  ✓ 完成節點: {node_data.get('title', 'unknown')}")
                                print(f"    執行時間: {node_data.get('execution_metadata', {}).get('total_time', 0):.2f}秒")

                            elif event == 'workflow_finished':
                                # 工作流完成
                                outputs = data.get('data', {}).get('outputs', {})
                                print(f"\n✓ 工作流執行完成")
                                print(f"總執行時間: {data.get('data', {}).get('elapsed_time', 0):.2f}秒")

                            elif event == 'text_chunk':
                                # 文字塊（如果有生成文字）
                                print(data.get('data', {}).get('text', ''), end='', flush=True)

                            elif event == 'error':
                                # 錯誤
                                print(f"\n✗ 錯誤: {data.get('message', 'unknown error')}")

                        except json.JSONDecodeError:
                            continue

            # 顯示最終輸出
            if outputs:
                print(f"\n\n最終輸出：")
                print(json.dumps(outputs, ensure_ascii=False, indent=2))

            return {"workflow_run_id": workflow_run_id, "outputs": outputs}

        except requests.exceptions.RequestException as e:
            print(f"\n執行工作流失敗：{e}")
            return {"error": str(e)}

    def get_workflow_run_status(self, workflow_run_id: str) -> Dict[str, Any]:
        """
        查詢工作流執行狀態

        參數：
            workflow_run_id: 工作流執行 ID

        返回：
            工作流狀態資訊
        """
        print(f"\n{'='*60}")
        print(f"查詢工作流狀態 - ID: {workflow_run_id}")
        print(f"{'='*60}")

        # 注意：此 API 端點可能需要根據實際的 Dify 版本調整
        url = f"{self.base_url}/workflows/runs/{workflow_run_id}"

        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            status = response.json()

            print(f"狀態：{status.get('status', 'unknown')}")
            print(f"創建時間：{status.get('created_at', 'N/A')}")
            print(f"完成時間：{status.get('finished_at', 'N/A')}")

            return status

        except requests.exceptions.RequestException as e:
            print(f"查詢狀態失敗：{e}")
            return {"error": str(e)}

    def batch_run_workflow(self, inputs_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量執行工作流

        參數：
            inputs_list: 輸入參數列表

        返回：
            執行結果列表
        """
        print(f"\n{'='*60}")
        print(f"批量執行工作流 - 共 {len(inputs_list)} 個任務")
        print(f"{'='*60}")

        results = []

        for idx, inputs in enumerate(inputs_list, 1):
            print(f"\n執行任務 {idx}/{len(inputs_list)}")
            result = self.run_workflow(inputs, user_id=f"batch-user-{idx}")
            results.append(result)

            # 避免請求過快
            if idx < len(inputs_list):
                time.sleep(1)

        print(f"\n{'='*60}")
        print("批量執行完成")
        print(f"成功：{sum(1 for r in results if 'error' not in r)} 個")
        print(f"失敗：{sum(1 for r in results if 'error' in r)} 個")
        print(f"{'='*60}")

        return results


class WorkflowExamples:
    """工作流範例集合"""

    def __init__(self, manager: DifyWorkflowManager):
        """
        初始化範例

        參數：
            manager: 工作流管理器實例
        """
        self.manager = manager

    def example_text_processing(self):
        """
        範例：文字處理工作流
        場景：文章摘要、關鍵字提取、情感分析
        """
        print("\n\n📝 範例 1：文字處理工作流")

        inputs = {
            "text": """
            人工智慧（AI）正在改變我們的生活方式。從智能手機到自動駕駛汽車，
            AI 技術已經滲透到各個領域。機器學習和深度學習的進步使得計算機能夠
            執行以前只有人類才能完成的任務。然而，我們也需要關注 AI 的倫理問題，
            確保技術的發展造福全人類。
            """,
            "task": "請生成文章摘要、提取關鍵字並分析情感傾向"
        }

        result = self.manager.run_workflow(inputs)
        return result

    def example_data_transformation(self):
        """
        範例：數據轉換工作流
        場景：格式轉換、數據清洗、結構化輸出
        """
        print("\n\n📝 範例 2：數據轉換工作流")

        inputs = {
            "raw_data": [
                "張三,25,工程師,台北",
                "李四,30,設計師,台中",
                "王五,28,產品經理,高雄"
            ],
            "output_format": "JSON"
        }

        result = self.manager.run_workflow(inputs)
        return result

    def example_content_generation(self):
        """
        範例：內容生成工作流
        場景：文章撰寫、SEO 優化、多語言翻譯
        """
        print("\n\n📝 範例 3：內容生成工作流")

        inputs = {
            "topic": "永續發展與綠色科技",
            "style": "專業但易懂",
            "length": "300字",
            "keywords": ["環保", "創新", "未來"]
        }

        result = self.manager.run_workflow(inputs)
        return result

    def example_streaming_workflow(self):
        """
        範例：串流式工作流
        展示實時處理過程
        """
        print("\n\n📝 範例 4：串流式工作流")

        inputs = {
            "question": "請解釋量子計算的基本原理和應用前景",
            "detail_level": "詳細"
        }

        result = self.manager.run_workflow_streaming(inputs)
        return result

    def example_batch_processing(self):
        """
        範例：批量處理工作流
        處理多個輸入
        """
        print("\n\n📝 範例 5：批量處理工作流")

        inputs_list = [
            {"text": "今天天氣真好", "task": "情感分析"},
            {"text": "這個產品質量太差了", "task": "情感分析"},
            {"text": "服務態度一般般", "task": "情感分析"},
        ]

        results = self.manager.batch_run_workflow(inputs_list)
        return results


def workflow_best_practices():
    """
    工作流最佳實踐說明
    """
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║           Dify 工作流最佳實踐                            ║
    ╚══════════════════════════════════════════════════════════╝

    1. 工作流 vs 對話流的選擇
    -------------------------
    ✓ 使用工作流（Workflow）當：
      - 單次任務執行（如數據處理、報告生成）
      - 自動化流程（如定時任務、批量處理）
      - 不需要記憶上下文的場景

    ✓ 使用對話流（Chatflow）當：
      - 需要多輪對話
      - 需要維持上下文記憶
      - 互動式應用（如客服、助手）

    2. 工作流設計原則
    -----------------
    ✓ 模塊化：將複雜任務分解為小節點
    ✓ 可重用：設計通用的工作流組件
    ✓ 錯誤處理：添加適當的錯誤處理節點
    ✓ 測試優先：先測試單個節點，再組合

    3. 性能優化
    ----------
    ✓ 並行執行：使用並行節點提高效率
    ✓ 條件分支：使用 IF/ELSE 節點避免不必要的執行
    ✓ 緩存結果：重複使用中間結果
    ✓ 限制迭代：設置迭代節點的最大次數

    4. 常用節點類型
    --------------
    - LLM 節點：調用語言模型
    - 代碼節點：執行自定義 Python/JavaScript 代碼
    - HTTP 請求節點：調用外部 API
    - 條件節點：IF/ELSE 邏輯判斷
    - 迭代節點：循環處理列表數據
    - 知識檢索節點：查詢知識庫
    - 工具節點：使用內建或自定義工具

    5. 監控與調試
    ------------
    ✓ 使用串流模式觀察執行過程
    ✓ 記錄每個節點的輸入輸出
    ✓ 監控執行時間和資源消耗
    ✓ 設置日誌和告警
    """)


def main():
    """主函數"""

    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║           Dify 工作流創建範例                            ║
    ║                                                          ║
    ║  學習如何創建和執行 Dify 工作流                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    # 檢查 API Key
    if not os.getenv("DIFY_API_KEY"):
        print("\n⚠️  請先設置 DIFY_API_KEY 環境變數")
        print("參考 01_快速開始.py 了解如何設置")
        return

    try:
        # 初始化管理器
        manager = DifyWorkflowManager()

        # 創建範例實例
        examples = WorkflowExamples(manager)

        # 執行各種範例
        print("\n" + "="*60)
        print("開始執行工作流範例")
        print("="*60)

        # 範例 1：文字處理
        examples.example_text_processing()

        # 範例 2：數據轉換
        examples.example_data_transformation()

        # 範例 3：內容生成
        examples.example_content_generation()

        # 範例 4：串流式執行
        examples.example_streaming_workflow()

        # 範例 5：批量處理
        examples.example_batch_processing()

        # 顯示最佳實踐
        workflow_best_practices()

        print("""

        ✓ 工作流範例執行完成！

        下一步：
        --------
        1. 在 Dify Web 界面中設計自己的工作流
        2. 使用視覺化編輯器添加和連接節點
        3. 測試工作流並通過 API 調用
        4. 查看 03_知識庫管理.py 學習 RAG 功能

        進階學習：
        ---------
        - 工作流中的變量傳遞
        - 條件分支和循環控制
        - 與外部系統整合
        - 工作流版本管理
        """)

    except Exception as e:
        print(f"\n❌ 執行錯誤：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
