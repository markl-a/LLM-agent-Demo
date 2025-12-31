"""
Instructor 部分提取示例

這個模塊專注於部分數據提取和流式處理的高級技巧。
展示了如何優雅地處理不完整數據、增量更新和實時反饋。

主要內容：
1. Partial 模型使用
2. 流式部分提取
3. 增量數據更新
4. 實時進度反饋
5. 容錯和優雅降級
6. 部分數據的業務處理

作者: Instructor 示例
日期: 2025-01-01
"""

import os
import time
from typing import List, Optional, Dict
from datetime import date
from pydantic import BaseModel, Field
import instructor
from instructor import Partial
from openai import OpenAI


# ============================================================================
# 基礎模型定義
# ============================================================================

class ArticleMetadata(BaseModel):
    """文章元數據模型"""
    title: str = Field(description="文章標題")
    author: str = Field(description="作者")
    publish_date: date = Field(description="發布日期")
    category: str = Field(description="類別")
    tags: List[str] = Field(description="標籤列表")
    word_count: int = Field(description="字數", gt=0)
    reading_time: int = Field(description="閱讀時間（分鐘）", gt=0)


class ProgressReport(BaseModel):
    """進度報告模型"""
    project_name: str = Field(description="項目名稱")
    overall_progress: int = Field(description="總體進度（0-100）", ge=0, le=100)
    completed_tasks: List[str] = Field(description="已完成任務列表")
    in_progress_tasks: List[str] = Field(description="進行中任務列表")
    pending_tasks: List[str] = Field(description="待辦任務列表")
    blockers: List[str] = Field(
        default_factory=list,
        description="阻礙因素列表"
    )
    next_steps: List[str] = Field(description="下一步行動")


class DataAnalysis(BaseModel):
    """數據分析模型"""
    dataset_name: str = Field(description="數據集名稱")
    total_records: int = Field(description="總記錄數", gt=0)
    key_metrics: Dict[str, float] = Field(description="關鍵指標")
    insights: List[str] = Field(description="洞察列表")
    recommendations: List[str] = Field(description="建議列表")
    visualizations: List[str] = Field(
        default_factory=list,
        description="可視化建議"
    )


class ResearchSummary(BaseModel):
    """研究摘要模型"""
    title: str = Field(description="研究標題")
    abstract: str = Field(description="摘要")
    research_questions: List[str] = Field(description="研究問題")
    methodology: str = Field(description="研究方法")
    key_findings: List[str] = Field(description="主要發現")
    conclusions: List[str] = Field(description="結論")
    limitations: List[str] = Field(
        default_factory=list,
        description="研究局限性"
    )
    future_work: List[str] = Field(
        default_factory=list,
        description="未來工作方向"
    )


# ============================================================================
# 輔助函數
# ============================================================================

def setup_client():
    """設置 Instructor 客戶端"""
    api_key = os.getenv("OPENAI_API_KEY", "sk-placeholder")
    openai_client = OpenAI(api_key=api_key)
    return instructor.from_openai(openai_client)


def print_field_status(obj: Any, field_name: str, prefix: str = ""):
    """打印字段狀態"""
    if hasattr(obj, field_name):
        value = getattr(obj, field_name)
        if isinstance(value, list):
            print(f"{prefix}✓ {field_name}: {len(value)} 項")
        elif isinstance(value, dict):
            print(f"{prefix}✓ {field_name}: {len(value)} 個鍵")
        else:
            print(f"{prefix}✓ {field_name}: {str(value)[:50]}")
    else:
        print(f"{prefix}⋯ {field_name}: 等待中...")


# ============================================================================
# 基礎部分提取
# ============================================================================

def basic_partial_extraction(client):
    """基礎部分提取示例

    展示如何使用 Partial 模型逐步接收數據。
    """
    print(f"\n{'='*60}")
    print("基礎部分提取示例")
    print(f"{'='*60}")

    text = """
    標題：深入理解 Python 異步編程
    作者：技術專家王老師
    發布日期：2025-01-15
    類別：編程教程
    標籤：Python, 異步編程, async/await, 並發
    字數：3500
    預計閱讀時間：15分鐘
    """

    print("\n開始流式提取文章元數據...")
    print("-" * 60)

    article_stream = client.chat.completions.create_partial(
        model="gpt-4",
        response_model=Partial[ArticleMetadata],
        messages=[
            {"role": "user", "content": f"提取文章元數據：\n{text}"}
        ],
        stream=True
    )

    print("\n實時更新:")
    final_article = None
    for partial_article in article_stream:
        # 清屏效果（可選）
        print("\033[K", end='')  # 清除當前行

        # 顯示已接收的字段
        fields = []
        for field in ['title', 'author', 'category', 'tags', 'word_count']:
            if hasattr(partial_article, field):
                fields.append(field)

        print(f"\r  已接收字段: {', '.join(fields)}", end='', flush=True)
        time.sleep(0.05)  # 模擬處理延遲

        final_article = partial_article

    print("\n")
    print("-" * 60)
    print("✓ 提取完成！\n")
    print(f"標題: {final_article.title}")
    print(f"作者: {final_article.author}")
    print(f"類別: {final_article.category}")
    print(f"標籤: {', '.join(final_article.tags)}")

    return final_article


# ============================================================================
# 增量列表提取
# ============================================================================

def incremental_list_extraction(client):
    """增量列表提取示例

    展示如何逐步接收列表數據並實時處理。
    """
    print(f"\n{'='*60}")
    print("增量列表提取示例")
    print(f"{'='*60}")

    text = """
    項目進度報告 - 網站重構項目

    總體進度：75%

    已完成任務：
    - UI設計完成
    - 數據庫遷移完成
    - 用戶認證模塊開發完成
    - API端點實現完成
    - 單元測試編寫完成

    進行中任務：
    - 前端頁面開發（80%）
    - 性能優化（60%）
    - 安全審計（40%）

    待辦任務：
    - 集成測試
    - 用戶驗收測試
    - 部署準備
    - 文檔編寫

    阻礙因素：
    - 第三方API響應緩慢
    - 需要額外的設計資源

    下一步行動：
    - 完成前端開發
    - 開始集成測試
    - 安排性能測試
    """

    print("\n開始流式提取進度報告...")
    print()

    report_stream = client.chat.completions.create_partial(
        model="gpt-4",
        response_model=Partial[ProgressReport],
        messages=[
            {"role": "user", "content": f"提取進度報告：\n{text}"}
        ],
        stream=True
    )

    # 追蹤已顯示的項目數量
    displayed_counts = {
        'completed_tasks': 0,
        'in_progress_tasks': 0,
        'pending_tasks': 0,
        'blockers': 0,
        'next_steps': 0
    }

    final_report = None
    for partial_report in report_stream:
        # 顯示新接收到的已完成任務
        if hasattr(partial_report, 'completed_tasks'):
            current_count = len(partial_report.completed_tasks)
            if current_count > displayed_counts['completed_tasks']:
                if displayed_counts['completed_tasks'] == 0:
                    print("✓ 已完成任務:")
                new_tasks = partial_report.completed_tasks[
                    displayed_counts['completed_tasks']:
                ]
                for task in new_tasks:
                    print(f"  • {task}")
                displayed_counts['completed_tasks'] = current_count

        # 顯示進行中任務
        if hasattr(partial_report, 'in_progress_tasks'):
            current_count = len(partial_report.in_progress_tasks)
            if current_count > displayed_counts['in_progress_tasks']:
                if displayed_counts['in_progress_tasks'] == 0:
                    print("\n⚙ 進行中任務:")
                new_tasks = partial_report.in_progress_tasks[
                    displayed_counts['in_progress_tasks']:
                ]
                for task in new_tasks:
                    print(f"  • {task}")
                displayed_counts['in_progress_tasks'] = current_count

        # 顯示待辦任務
        if hasattr(partial_report, 'pending_tasks'):
            current_count = len(partial_report.pending_tasks)
            if current_count > displayed_counts['pending_tasks']:
                if displayed_counts['pending_tasks'] == 0:
                    print("\n☐ 待辦任務:")
                new_tasks = partial_report.pending_tasks[
                    displayed_counts['pending_tasks']:
                ]
                for task in new_tasks:
                    print(f"  • {task}")
                displayed_counts['pending_tasks'] = current_count

        # 顯示阻礙因素
        if hasattr(partial_report, 'blockers'):
            current_count = len(partial_report.blockers)
            if current_count > displayed_counts['blockers']:
                if displayed_counts['blockers'] == 0:
                    print("\n⚠ 阻礙因素:")
                new_blockers = partial_report.blockers[
                    displayed_counts['blockers']:
                ]
                for blocker in new_blockers:
                    print(f"  ! {blocker}")
                displayed_counts['blockers'] = current_count

        # 顯示下一步行動
        if hasattr(partial_report, 'next_steps'):
            current_count = len(partial_report.next_steps)
            if current_count > displayed_counts['next_steps']:
                if displayed_counts['next_steps'] == 0:
                    print("\n→ 下一步行動:")
                new_steps = partial_report.next_steps[
                    displayed_counts['next_steps']:
                ]
                for step in new_steps:
                    print(f"  → {step}")
                displayed_counts['next_steps'] = current_count

        final_report = partial_report

    print(f"\n總體進度: {final_report.overall_progress}%")
    print("\n✓ 進度報告提取完成！")

    return final_report


# ============================================================================
# 帶狀態追蹤的部分提取
# ============================================================================

def extraction_with_status_tracking(client):
    """帶狀態追蹤的部分提取

    展示如何追蹤提取進度並提供實時反饋。
    """
    print(f"\n{'='*60}")
    print("帶狀態追蹤的部分提取")
    print(f"{'='*60}")

    text = """
    數據集：用戶行為分析

    總記錄數：1,500,000

    關鍵指標：
    - 日活躍用戶：450,000
    - 平均會話時長：8.5分鐘
    - 轉化率：3.2%
    - 留存率（7天）：65%
    - 平均收入（ARPU）：$12.50

    主要洞察：
    1. 移動端用戶增長迅速，佔比達到68%
    2. 晚上8-10點是使用高峰期
    3. 新用戶前3天的留存是關鍵
    4. 推送通知可以提升20%的活躍度
    5. 用戶更偏好視頻內容而非文字

    建議：
    1. 優化移動端體驗
    2. 在高峰時段推送內容
    3. 加強新用戶引導
    4. 個性化推送策略
    5. 增加視頻內容比例

    可視化建議：
    - 用戶增長趨勢圖
    - 時段活躍度熱力圖
    - 漏斗轉化圖
    """

    print("\n開始提取數據分析...")
    print()

    analysis_stream = client.chat.completions.create_partial(
        model="gpt-4",
        response_model=Partial[DataAnalysis],
        messages=[
            {"role": "user", "content": f"提取數據分析：\n{text}"}
        ],
        stream=True
    )

    # 狀態追蹤
    status = {
        'dataset_name': False,
        'total_records': False,
        'key_metrics': False,
        'insights': False,
        'recommendations': False,
        'visualizations': False
    }

    insights_count = 0
    recommendations_count = 0

    print("提取進度:")
    for partial_analysis in analysis_stream:
        # 更新狀態
        if hasattr(partial_analysis, 'dataset_name') and not status['dataset_name']:
            status['dataset_name'] = True
            print(f"  [1/6] ✓ 數據集名稱: {partial_analysis.dataset_name}")

        if hasattr(partial_analysis, 'total_records') and not status['total_records']:
            status['total_records'] = True
            print(f"  [2/6] ✓ 總記錄數: {partial_analysis.total_records:,}")

        if hasattr(partial_analysis, 'key_metrics') and not status['key_metrics']:
            status['key_metrics'] = True
            print(f"  [3/6] ✓ 關鍵指標: {len(partial_analysis.key_metrics)} 個")

        if hasattr(partial_analysis, 'insights'):
            current_count = len(partial_analysis.insights)
            if current_count > insights_count:
                if not status['insights']:
                    status['insights'] = True
                    print(f"  [4/6] ✓ 洞察:")
                new_insights = partial_analysis.insights[insights_count:]
                for insight in new_insights:
                    print(f"        • {insight}")
                insights_count = current_count

        if hasattr(partial_analysis, 'recommendations'):
            current_count = len(partial_analysis.recommendations)
            if current_count > recommendations_count:
                if not status['recommendations']:
                    status['recommendations'] = True
                    print(f"  [5/6] ✓ 建議:")
                new_recs = partial_analysis.recommendations[recommendations_count:]
                for rec in new_recs:
                    print(f"        → {rec}")
                recommendations_count = current_count

        if hasattr(partial_analysis, 'visualizations') and not status['visualizations']:
            if len(partial_analysis.visualizations) > 0:
                status['visualizations'] = True
                print(f"  [6/6] ✓ 可視化: {len(partial_analysis.visualizations)} 個建議")

        final_analysis = partial_analysis

    # 顯示完整進度
    completed = sum(1 for v in status.values() if v)
    total = len(status)
    print(f"\n提取完成度: {completed}/{total} ({completed/total*100:.0f}%)")

    return final_analysis


# ============================================================================
# 容錯處理
# ============================================================================

def extraction_with_fallback(client):
    """帶容錯的部分提取

    展示如何處理部分提取失敗的情況。
    """
    print(f"\n{'='*60}")
    print("帶容錯的部分提取")
    print(f"{'='*60}")

    text = """
    研究標題：機器學習在醫療診斷中的應用

    摘要：本研究探討了深度學習技術在醫療影像診斷中的應用...

    研究問題：
    1. 深度學習如何提高診斷準確率？
    2. 模型的可解釋性如何保證？
    3. 如何處理醫療數據的隱私問題？
    """

    print("\n開始提取研究摘要...")
    print()

    try:
        summary_stream = client.chat.completions.create_partial(
            model="gpt-4",
            response_model=Partial[ResearchSummary],
            messages=[
                {"role": "user", "content": f"提取研究摘要：\n{text}"}
            ],
            stream=True
        )

        # 收集所有部分結果
        partial_results = []
        received_fields = set()

        for partial_summary in partial_results:
            partial_results.append(partial_summary)

            # 追蹤接收到的字段
            for field in ['title', 'abstract', 'research_questions',
                         'methodology', 'key_findings', 'conclusions']:
                if hasattr(partial_summary, field) and field not in received_fields:
                    received_fields.add(field)
                    print(f"  ✓ 接收到: {field}")

        # 獲取最後一個結果
        if partial_results:
            final_summary = partial_results[-1]

            print("\n提取結果:")
            print(f"  標題: {getattr(final_summary, 'title', '未獲取')}")
            print(f"  研究問題數: {len(getattr(final_summary, 'research_questions', []))}")

            # 檢查缺失的字段
            expected_fields = [
                'title', 'abstract', 'research_questions',
                'methodology', 'key_findings', 'conclusions'
            ]
            missing_fields = [
                f for f in expected_fields
                if not hasattr(final_summary, f)
            ]

            if missing_fields:
                print(f"\n  ⚠ 缺失字段: {', '.join(missing_fields)}")
                print("  可能需要重試或使用默認值")
            else:
                print("\n  ✓ 所有必需字段都已獲取")

            return final_summary

    except Exception as e:
        print(f"\n✗ 提取過程出錯: {str(e)}")
        print("  已接收的字段:", ', '.join(received_fields))
        return None


# ============================================================================
# 實時業務處理
# ============================================================================

def real_time_business_processing(client):
    """實時業務處理示例

    展示如何在流式提取過程中進行實時業務處理。
    """
    print(f"\n{'='*60}")
    print("實時業務處理示例")
    print(f"{'='*60}")

    text = """
    項目進度：移動應用開發
    總體進度：60%

    已完成：
    - 需求分析
    - UI/UX設計
    - 數據庫設計
    - 後端API開發

    進行中：
    - 前端開發（70%）
    - 測試（30%）

    待辦：
    - 性能優化
    - 部署
    - 用戶培訓

    下一步：
    - 完成前端開發
    - 增加測試覆蓋率
    - 準備Beta測試
    """

    print("\n開始提取並處理進度報告...")
    print()

    report_stream = client.chat.completions.create_partial(
        model="gpt-4",
        response_model=Partial[ProgressReport],
        messages=[
            {"role": "user", "content": f"提取進度報告：\n{text}"}
        ],
        stream=True
    )

    # 業務邏輯：實時計算和判斷
    alert_triggered = False

    for partial_report in report_stream:
        # 實時檢查進度
        if hasattr(partial_report, 'overall_progress'):
            progress = partial_report.overall_progress

            if progress < 50 and not alert_triggered:
                print("  ⚠ 警報：項目進度低於50%")
                alert_triggered = True

        # 實時檢查阻礙因素
        if hasattr(partial_report, 'blockers'):
            if len(partial_report.blockers) > 0 and not alert_triggered:
                print(f"  ⚠ 發現 {len(partial_report.blockers)} 個阻礙因素")
                alert_triggered = True

        # 實時計算完成率
        if (hasattr(partial_report, 'completed_tasks') and
            hasattr(partial_report, 'pending_tasks')):
            total_tasks = (
                len(partial_report.completed_tasks) +
                len(getattr(partial_report, 'in_progress_tasks', [])) +
                len(partial_report.pending_tasks)
            )
            if total_tasks > 0:
                completion_rate = (
                    len(partial_report.completed_tasks) / total_tasks * 100
                )
                print(f"  任務完成率: {completion_rate:.1f}%")

        final_report = partial_report

    print("\n✓ 處理完成")
    return final_report


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主函數 - 運行所有部分提取示例"""
    print("="*60)
    print("Instructor 部分提取示例")
    print("="*60)

    client = setup_client()

    # 基礎示例
    basic_partial_extraction(client)

    # 增量列表提取
    incremental_list_extraction(client)

    # 狀態追蹤
    extraction_with_status_tracking(client)

    # 容錯處理
    extraction_with_fallback(client)

    # 實時業務處理
    real_time_business_processing(client)

    print("\n" + "="*60)
    print("部分提取要點總結")
    print("="*60)
    print("""
1. Partial 模型使用：
   - 導入：from instructor import Partial
   - 包裝：Partial[YourModel]
   - 允許接收不完整的數據

2. 流式處理：
   - 使用 create_partial() 方法
   - stream=True 啟用流式模式
   - 逐步接收和處理數據

3. 實時反饋：
   - 追蹤已接收的字段
   - 顯示提取進度
   - 提供狀態更新

4. 增量處理：
   - 處理列表的新增項
   - 實時業務邏輯判斷
   - 動態更新 UI

5. 容錯處理：
   - 收集部分結果
   - 檢測缺失字段
   - 優雅降級策略

6. 適用場景：
   - 長文本處理
   - 大量列表數據
   - 需要實時反饋的場景
   - 用戶體驗優化

7. 最佳實踐：
   - 合理使用 hasattr() 檢查字段
   - 追蹤數據完整性
   - 提供進度指示
   - 處理中斷情況
   - 保存最終完整結果
    """)


if __name__ == "__main__":
    main()
