#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prefect 監控面板與 UI
======================

這個示例展示了 Prefect 的監控和觀測功能，包括：
1. Prefect UI 使用
2. 日誌記錄和查詢
3. 性能監控
4. 執行歷史
5. 儀表板配置
6. API 查詢
"""

from prefect import task, flow, get_run_logger
from prefect.client import get_client
from prefect.context import get_run_context
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List
import asyncio


# ============================================================================
# 帶豐富日誌的任務
# ============================================================================

@task(name="數據驗證任務")
def validate_data_task(data: List[int]) -> Dict:
    """
    數據驗證任務（帶詳細日誌）

    Args:
        data: 要驗證的數據

    Returns:
        驗證結果
    """
    logger = get_run_logger()

    # 開始日誌
    logger.info("=" * 50)
    logger.info("開始數據驗證")
    logger.info(f"數據量：{len(data)} 項")
    logger.info("=" * 50)

    # 詳細的驗證過程
    issues = []

    # 檢查空值
    logger.info("→ 檢查空值...")
    if not data:
        issues.append("數據為空")
        logger.warning("⚠️ 發現問題：數據為空")
    else:
        logger.info("✓ 無空值問題")

    # 檢查數據類型
    logger.info("→ 檢查數據類型...")
    invalid_types = [x for x in data if not isinstance(x, (int, float))]
    if invalid_types:
        issues.append(f"發現 {len(invalid_types)} 個無效類型")
        logger.warning(f"⚠️ 發現問題：{len(invalid_types)} 個無效類型")
    else:
        logger.info("✓ 數據類型正確")

    # 檢查範圍
    logger.info("→ 檢查數值範圍...")
    outliers = [x for x in data if isinstance(x, (int, float)) and (x < 0 or x > 1000)]
    if outliers:
        issues.append(f"發現 {len(outliers)} 個異常值")
        logger.warning(f"⚠️ 發現問題：{len(outliers)} 個異常值")
    else:
        logger.info("✓ 數值範圍正常")

    # 生成報告
    result = {
        "total_count": len(data),
        "valid_count": len(data) - len(invalid_types) - len(outliers),
        "issues": issues,
        "is_valid": len(issues) == 0,
        "validated_at": datetime.now().isoformat()
    }

    # 結果日誌
    logger.info("\n" + "=" * 50)
    logger.info("驗證完成")
    logger.info(f"總計：{result['total_count']} 項")
    logger.info(f"有效：{result['valid_count']} 項")
    logger.info(f"問題：{len(issues)} 個")
    if result['is_valid']:
        logger.info("✅ 驗證通過")
    else:
        logger.error("❌ 驗證失敗")
    logger.info("=" * 50)

    return result


@task(name="數據處理任務")
def process_data_with_progress(data: List[int]) -> Dict:
    """
    帶進度日誌的數據處理任務

    Args:
        data: 要處理的數據

    Returns:
        處理結果
    """
    logger = get_run_logger()
    logger.info(f"開始處理 {len(data)} 項數據")

    results = []
    total = len(data)

    for i, value in enumerate(data):
        # 模擬處理
        time.sleep(0.1)
        processed = value * 2

        results.append(processed)

        # 進度日誌
        progress = (i + 1) / total * 100
        if (i + 1) % 10 == 0 or (i + 1) == total:
            logger.info(f"進度：{progress:.1f}% ({i + 1}/{total})")

    result = {
        "processed_count": len(results),
        "total_value": sum(results),
        "average_value": sum(results) / len(results) if results else 0
    }

    logger.info(f"處理完成：{result}")
    return result


@task(name="性能監控任務")
def performance_monitored_task(iterations: int = 100) -> Dict:
    """
    帶性能監控的任務

    Args:
        iterations: 迭代次數

    Returns:
        性能統計
    """
    logger = get_run_logger()
    logger.info(f"開始性能測試（{iterations} 次迭代）")

    start_time = time.time()
    execution_times = []

    for i in range(iterations):
        iter_start = time.time()

        # 模擬工作負載
        time.sleep(random.uniform(0.01, 0.05))

        iter_time = time.time() - iter_start
        execution_times.append(iter_time)

        # 定期報告
        if (i + 1) % 20 == 0:
            avg_time = sum(execution_times) / len(execution_times)
            logger.info(f"迭代 {i + 1}: 平均耗時 {avg_time*1000:.2f}ms")

    total_time = time.time() - start_time

    result = {
        "iterations": iterations,
        "total_time": total_time,
        "avg_time": sum(execution_times) / len(execution_times),
        "min_time": min(execution_times),
        "max_time": max(execution_times)
    }

    logger.info("\n" + "=" * 50)
    logger.info("性能統計")
    logger.info(f"總迭代：{result['iterations']}")
    logger.info(f"總耗時：{result['total_time']:.2f}s")
    logger.info(f"平均：{result['avg_time']*1000:.2f}ms")
    logger.info(f"最小：{result['min_time']*1000:.2f}ms")
    logger.info(f"最大：{result['max_time']*1000:.2f}ms")
    logger.info("=" * 50)

    return result


# ============================================================================
# 監控工作流
# ============================================================================

@flow(name="可觀測的工作流", description="帶完整監控和日誌的工作流")
def observable_workflow(data_size: int = 50):
    """
    可觀測的工作流

    這個工作流展示了如何添加豐富的日誌和監控。

    Args:
        data_size: 數據大小
    """
    logger = get_run_logger()

    # 工作流開始
    logger.info("\n" + "=" * 70)
    logger.info("可觀測工作流開始")
    logger.info("=" * 70)
    logger.info(f"參數：data_size={data_size}")
    logger.info(f"開始時間：{datetime.now()}")

    try:
        # 生成測試數據
        logger.info("\n→ 階段 1：生成測試數據")
        data = list(range(data_size))
        logger.info(f"✓ 生成了 {len(data)} 項數據")

        # 驗證數據
        logger.info("\n→ 階段 2：驗證數據")
        validation_result = validate_data_task(data)

        if not validation_result['is_valid']:
            logger.error("數據驗證失敗，中止工作流")
            return {"status": "failed", "reason": "validation_failed"}

        # 處理數據
        logger.info("\n→ 階段 3：處理數據")
        process_result = process_data_with_progress(data)

        # 性能測試
        logger.info("\n→ 階段 4：性能測試")
        perf_result = performance_monitored_task(iterations=50)

        # 工作流完成
        final_result = {
            "status": "completed",
            "validation": validation_result,
            "processing": process_result,
            "performance": perf_result,
            "completed_at": datetime.now().isoformat()
        }

        logger.info("\n" + "=" * 70)
        logger.info("✅ 工作流成功完成")
        logger.info("=" * 70)

        return final_result

    except Exception as e:
        logger.error("\n" + "=" * 70)
        logger.error(f"❌ 工作流失敗：{e}")
        logger.error("=" * 70)
        raise


# ============================================================================
# Prefect UI 使用指南
# ============================================================================

def show_ui_guide():
    """
    顯示 Prefect UI 使用指南
    """
    print("\n" + "=" * 70)
    print("Prefect UI 使用指南")
    print("=" * 70)

    guide = """
🌐 訪問 Prefect UI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 啟動 Prefect 服務器：
   $ prefect server start

2. 訪問 UI：
   http://localhost:4200

3. 或使用 Prefect Cloud：
   $ prefect cloud login
   訪問：https://app.prefect.cloud


📊 主要功能區域
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Dashboard（儀表板）
   - 概覽所有 Flow Runs
   - 實時狀態監控
   - 成功率統計
   - 最近執行記錄

2. Flows（流程）
   - 查看所有已註冊的 Flow
   - Flow 執行歷史
   - Flow 詳細信息
   - 運行統計

3. Deployments（部署）
   - 查看所有部署
   - 部署配置
   - 調度設置
   - 手動觸發運行

4. Work Pools（工作池）
   - 管理 Work Pool
   - 查看 Worker 狀態
   - 配置基礎設施

5. Blocks（區塊）
   - 管理配置
   - 存儲憑證
   - 共享資源

6. Notifications（通知）
   - 配置通知規則
   - 查看通知歷史


🔍 查看 Flow Run 詳情
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

點擊任意 Flow Run 可以查看：

1. 概覽
   - 執行狀態
   - 開始/結束時間
   - 執行時長
   - 參數

2. 任務流
   - 可視化任務依賴圖
   - 任務執行狀態
   - 任務執行時間

3. 日誌
   - 完整的執行日誌
   - 按時間排序
   - 支持搜索和過濾
   - 不同級別（INFO、WARNING、ERROR）

4. 結果
   - 任務返回值
   - 中間結果
   - 最終輸出

5. 重新運行
   - 重新執行 Flow
   - 修改參數
   - 選擇性重試失敗任務


📈 監控儀表板功能
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 實時監控
   - 正在運行的 Flow
   - 排隊中的任務
   - 活躍的 Worker

2. 性能指標
   - 執行時間趨勢
   - 成功率統計
   - 資源使用情況

3. 告警和通知
   - 失敗告警
   - 性能告警
   - 自定義通知

4. 搜索和過濾
   - 按狀態過濾
   - 按標籤過濾
   - 按時間範圍過濾
   - 按 Flow 名稱搜索


🛠️ 常用操作
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 手動觸發 Deployment
   - 進入 Deployments 頁面
   - 選擇要運行的 Deployment
   - 點擊 "Run" 按鈕
   - 可以修改參數

2. 查看日誌
   - 點擊 Flow Run
   - 切換到 "Logs" 標籤
   - 使用搜索框過濾日誌

3. 取消運行
   - 點擊 Flow Run
   - 點擊 "Cancel" 按鈕

4. 重新運行
   - 點擊 Flow Run
   - 點擊 "Rerun" 按鈕
   - 選擇重試選項

5. 暫停/恢復 Deployment
   - 進入 Deployment 詳情
   - 點擊 "Pause" 或 "Resume"


📱 移動端訪問
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Prefect UI 是響應式設計，可以在移動設備上訪問：
- 查看執行狀態
- 查看日誌
- 手動觸發運行
- 接收通知


🎨 自定義儀表板
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Prefect Cloud 提供自定義儀表板功能：
- 創建自定義視圖
- 添加圖表和指標
- 設置團隊儀表板
- 導出報告


💡 最佳實踐
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 使用有意義的名稱
   - Flow 名稱要清晰
   - Task 名稱要描述性
   - Deployment 名稱要規範

2. 添加描述
   - 為 Flow 添加 description
   - 為 Task 添加文檔字符串
   - 為 Deployment 添加說明

3. 使用標籤
   - 環境標籤（production、staging）
   - 類型標籤（etl、ml、reporting）
   - 團隊標籤（data、ops）

4. 結構化日誌
   - 使用清晰的日誌格式
   - 區分不同日誌級別
   - 添加進度信息

5. 監控關鍵指標
   - 執行時間
   - 成功率
   - 資源使用
   - 錯誤率
    """

    print(guide)


# ============================================================================
# API 查詢示例
# ============================================================================

async def query_flow_runs_api():
    """
    使用 API 查詢 Flow Runs

    這個示例展示如何通過 Prefect API 查詢執行信息。
    """
    print("\n" + "=" * 70)
    print("API 查詢示例")
    print("=" * 70)

    print("""
使用 Prefect Client API 查詢數據：

from prefect.client import get_client
from datetime import datetime, timedelta

async def query_recent_runs():
    async with get_client() as client:
        # 查詢最近 24 小時的 Flow Runs
        flow_runs = await client.read_flow_runs(
            limit=10,
            sort="START_TIME_DESC"
        )

        for run in flow_runs:
            print(f"Flow: {run.flow_id}")
            print(f"狀態: {run.state.type}")
            print(f"開始時間: {run.start_time}")
            print(f"耗時: {run.total_run_time}")
            print("-" * 50)

# 運行查詢
import asyncio
asyncio.run(query_recent_runs())

更多 API 查詢示例：

# 1. 查詢特定 Flow 的運行
flow_runs = await client.read_flow_runs(
    flow_filter=FlowFilter(name={"any_": ["my-flow"]})
)

# 2. 查詢失敗的運行
failed_runs = await client.read_flow_runs(
    flow_run_filter=FlowRunFilter(
        state={"type": {"any_": ["FAILED"]}}
    )
)

# 3. 查詢特定時間範圍
from datetime import datetime, timedelta

recent_runs = await client.read_flow_runs(
    flow_run_filter=FlowRunFilter(
        start_time={"after_": datetime.now() - timedelta(days=7)}
    )
)

# 4. 獲取 Flow Run 的日誌
logs = await client.read_logs(
    log_filter=LogFilter(
        flow_run_id={"any_": [flow_run_id]}
    )
)

for log in logs:
    print(f"[{log.timestamp}] {log.level}: {log.message}")
    """)


def show_monitoring_cli_commands():
    """
    顯示監控相關的 CLI 命令
    """
    print("\n" + "=" * 70)
    print("監控 CLI 命令")
    print("=" * 70)

    commands = """
# 查看 Flow Runs
prefect flow-run ls
prefect flow-run ls --limit 20
prefect flow-run ls --state FAILED

# 查看特定 Flow Run 的詳情
prefect flow-run inspect <flow-run-id>

# 查看日誌
prefect flow-run logs <flow-run-id>

# 實時跟蹤日誌
prefect flow-run logs <flow-run-id> --follow

# 取消運行
prefect flow-run cancel <flow-run-id>

# 查看 Deployment 運行歷史
prefect deployment run ls --deployment-name "my-deployment"

# 查看 Work Pool 狀態
prefect work-pool ls
prefect work-pool inspect "pool-name"

# 查看 Worker 狀態
prefect worker ls

# 查看服務器狀態
prefect server status

# 導出數據
prefect flow-run export <flow-run-id> --output run-data.json

# 查看統計信息
prefect flow-run stats
    """

    print(commands)


# ============================================================================
# 運行示例
# ============================================================================

def main():
    """
    主函數 - 運行監控示例
    """
    print("\n" + "=" * 70)
    print("Prefect 監控面板與 UI")
    print("=" * 70)

    # 運行可觀測的工作流
    print("\n【示例】運行可觀測的工作流")
    print("-" * 70)
    print("這個工作流會生成豐富的日誌，可以在 Prefect UI 中查看。")
    print()

    result = observable_workflow(data_size=30)
    print(f"\n最終結果：{result}")

    # 顯示 UI 指南
    show_ui_guide()

    # 顯示 API 查詢示例
    asyncio.run(query_flow_runs_api())

    # 顯示 CLI 命令
    show_monitoring_cli_commands()

    # 總結
    print("\n" + "=" * 70)
    print("監控和觀測總結")
    print("=" * 70)
    print("""
🎯 核心功能
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Prefect UI
   - 實時監控儀表板
   - 流程和任務可視化
   - 完整的日誌查看
   - 執行歷史追蹤

2. 日誌系統
   - 結構化日誌
   - 自動收集
   - 支持搜索和過濾
   - 多級別日誌

3. 性能監控
   - 執行時間追蹤
   - 資源使用監控
   - 趨勢分析
   - 性能優化建議

4. 告警通知
   - 失敗告警
   - 性能告警
   - 自定義通知規則


📊 查看數據的方式
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Prefect UI（推薦）
   http://localhost:4200
   - 最直觀的可視化界面
   - 實時更新
   - 豐富的功能

2. CLI 命令
   prefect flow-run ls
   prefect flow-run logs <id>
   - 適合腳本和自動化
   - 快速查看狀態

3. Python API
   使用 Prefect Client
   - 程序化查詢
   - 數據分析
   - 自定義工具


🔧 最佳實踐
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 結構化日誌
   - 使用清晰的日誌格式
   - 添加分隔符和標題
   - 標記重要事件

2. 進度報告
   - 為長時間任務添加進度日誌
   - 定期更新狀態
   - 提供預計完成時間

3. 錯誤處理
   - 詳細的錯誤信息
   - 包含上下文
   - 便於問題診斷

4. 性能追蹤
   - 記錄關鍵操作的耗時
   - 監控資源使用
   - 識別性能瓶頸


🚀 快速開始
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 啟動 Prefect 服務器：
   $ prefect server start

2. 訪問 UI：
   http://localhost:4200

3. 運行工作流：
   $ python 10_監控面板.py

4. 在 UI 中查看：
   - Dashboard 看概覽
   - Flow Runs 看詳情
   - Logs 看日誌


📚 相關資源
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- UI 文檔: https://docs.prefect.io/ui/overview
- API 文檔: https://docs.prefect.io/api-ref/
- 監控指南: https://docs.prefect.io/guides/monitoring
- Prefect Cloud: https://app.prefect.cloud


🎓 學習路徑
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ✓ 01_快速開始.py - 基本概念
2. ✓ 02_任務定義.py - 任務配置
3. ✓ 03_參數傳遞.py - 參數處理
4. ✓ 04_並行執行.py - 並發任務
5. ✓ 05_調度器.py - 任務調度
6. ✓ 06_狀態管理.py - 狀態處理
7. ✓ 07_緩存機制.py - 結果緩存
8. ✓ 08_通知告警.py - 通知配置
9. ✓ 09_部署配置.py - 部署管理
10. ✓ 10_監控面板.py - UI 和監控

恭喜你完成了 Prefect 學習！🎉


🌟 下一步建議
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 實踐項目
   - 創建實際的數據管道
   - 部署到生產環境
   - 集成現有系統

2. 深入學習
   - 探索高級功能
   - 閱讀源碼
   - 參與社區

3. 最佳實踐
   - 建立團隊規範
   - 優化工作流
   - 提升可靠性
    """)

    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
