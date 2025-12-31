"""
Instructor 流式提取示例

這個模塊展示了如何使用 Instructor 進行流式結構化數據提取。
流式提取允許在 LLM 生成數據時實時獲取和處理部分結果。

主要內容：
1. 基礎流式提取
2. Partial 模型使用
3. 實時數據更新
4. 流式列表提取
5. 進度顯示
6. 流式錯誤處理

作者: Instructor 示例
日期: 2025-01-01
"""

import os
import time
from typing import List, Optional, Iterable
from pydantic import BaseModel, Field
import instructor
from openai import OpenAI
from instructor import Partial


# ============================================================================
# 基礎模型定義
# ============================================================================

class User(BaseModel):
    """用戶信息模型"""
    name: str = Field(description="用戶姓名")
    age: int = Field(description="年齡")
    email: str = Field(description="電子郵件")
    bio: str = Field(description="個人簡介")


class Article(BaseModel):
    """文章模型"""
    title: str = Field(description="文章標題")
    author: str = Field(description="作者")
    summary: str = Field(description="摘要")
    content: str = Field(description="正文內容")
    keywords: List[str] = Field(description="關鍵詞列表")


class Product(BaseModel):
    """產品模型"""
    name: str = Field(description="產品名稱")
    description: str = Field(description="產品描述")
    features: List[str] = Field(description="功能特性列表")
    price: float = Field(description="價格")
    category: str = Field(description="類別")


class TodoItem(BaseModel):
    """待辦事項模型"""
    title: str = Field(description="任務標題")
    description: str = Field(description="任務描述")
    priority: str = Field(description="優先級")
    estimated_hours: int = Field(description="預估工時")


class TodoList(BaseModel):
    """待辦事項列表模型"""
    project_name: str = Field(description="項目名稱")
    items: List[TodoItem] = Field(description="待辦事項列表")


class StreamingReport(BaseModel):
    """流式報告模型"""
    title: str = Field(description="報告標題")
    executive_summary: str = Field(description="執行摘要")
    sections: List[str] = Field(description="章節列表")
    findings: List[str] = Field(description="發現列表")
    recommendations: List[str] = Field(description="建議列表")
    conclusion: str = Field(description="結論")


class AnalysisResult(BaseModel):
    """分析結果模型"""
    title: str = Field(description="分析標題")
    data_points: List[str] = Field(description="數據點")
    insights: List[str] = Field(description="洞察列表")
    score: float = Field(description="評分", ge=0, le=100)


# ============================================================================
# 輔助函數
# ============================================================================

def setup_client():
    """設置 Instructor 客戶端"""
    api_key = os.getenv("OPENAI_API_KEY", "sk-placeholder")
    openai_client = OpenAI(api_key=api_key)
    return instructor.from_openai(openai_client)


def print_progress_bar(current: int, total: int, prefix: str = "進度"):
    """打印進度條"""
    bar_length = 40
    filled = int(bar_length * current / total)
    bar = '█' * filled + '░' * (bar_length - filled)
    percent = 100 * current / total
    print(f'\r{prefix}: |{bar}| {percent:.1f}%', end='', flush=True)


# ============================================================================
# 基礎流式提取示例
# ============================================================================

def basic_streaming_extraction(client):
    """基礎流式提取示例

    展示如何使用流式模式逐步獲取用戶信息。
    """
    print(f"\n{'='*60}")
    print("基礎流式提取示例")
    print(f"{'='*60}")

    text = """
    用戶信息：
    姓名：張小明
    年齡：28歲
    郵箱：zhang.xiaoming@example.com
    個人簡介：熱愛編程的軟件工程師，擁有5年開發經驗，
    專注於後端開發和系統架構設計。喜歡學習新技術，
    積極參與開源社區。
    """

    print("\n開始流式提取用戶信息...")
    print("-" * 60)

    # 使用 Partial 模型進行流式提取
    user_stream = client.chat.completions.create_partial(
        model="gpt-4",
        response_model=Partial[User],
        messages=[
            {"role": "user", "content": f"提取用戶信息：\n{text}"}
        ],
        stream=True
    )

    # 逐步接收和顯示數據
    final_user = None
    for partial_user in user_stream:
        # 清除當前行並打印更新
        print("\r" + " " * 80, end='')  # 清除行
        print(f"\r姓名: {getattr(partial_user, 'name', '...')}", end='')
        time.sleep(0.1)  # 模擬處理延遲

        final_user = partial_user

    print()  # 換行
    print("-" * 60)
    print("✓ 提取完成！")
    print(f"\n完整信息：")
    print(f"  姓名: {final_user.name}")
    print(f"  年齡: {final_user.age}")
    print(f"  郵箱: {final_user.email}")
    print(f"  簡介: {final_user.bio[:50]}...")


def stream_with_visualization(client):
    """帶可視化的流式提取

    展示如何在流式提取過程中顯示進度和狀態。
    """
    print(f"\n{'='*60}")
    print("帶可視化的流式提取示例")
    print(f"{'='*60}")

    text = """
    文章標題：深入理解 Python 異步編程
    作者：技術專家王老師
    摘要：本文詳細介紹了 Python 中的異步編程概念
    關鍵詞：Python, 異步, async/await, 並發
    """

    print("\n正在提取文章信息...")

    article_stream = client.chat.completions.create_partial(
        model="gpt-4",
        response_model=Partial[Article],
        messages=[
            {"role": "user", "content": f"提取文章信息：\n{text}"}
        ],
        stream=True
    )

    fields_received = []
    for partial_article in article_stream:
        # 檢查哪些字段已經接收到
        if hasattr(partial_article, 'title') and 'title' not in fields_received:
            fields_received.append('title')
            print(f"✓ 接收到標題: {partial_article.title}")

        if hasattr(partial_article, 'author') and 'author' not in fields_received:
            fields_received.append('author')
            print(f"✓ 接收到作者: {partial_article.author}")

        if hasattr(partial_article, 'summary') and 'summary' not in fields_received:
            fields_received.append('summary')
            print(f"✓ 接收到摘要")

        if hasattr(partial_article, 'keywords') and 'keywords' not in fields_received:
            fields_received.append('keywords')
            print(f"✓ 接收到關鍵詞: {', '.join(partial_article.keywords)}")

    print("\n✓ 文章信息提取完成！")


# ============================================================================
# 流式列表提取
# ============================================================================

def stream_list_extraction(client):
    """流式列表提取示例

    展示如何流式提取包含列表的複雜結構。
    """
    print(f"\n{'='*60}")
    print("流式列表提取示例")
    print(f"{'='*60}")

    text = """
    產品名稱：智能手錶 Pro

    產品描述：
    這是一款功能強大的智能手錶，結合了健康監測、
    運動追蹤和智能通知等多項功能。

    主要功能：
    1. 心率監測 - 24小時持續監測心率
    2. 睡眠追蹤 - 深度分析睡眠質量
    3. 運動模式 - 支持50+種運動模式
    4. GPS定位 - 精準的位置追蹤
    5. 防水設計 - 5ATM防水等級
    6. 長續航 - 一次充電可用7天

    價格：$299
    類別：可穿戴設備
    """

    print("\n開始流式提取產品信息...")
    print("-" * 60)

    product_stream = client.chat.completions.create_partial(
        model="gpt-4",
        response_model=Partial[Product],
        messages=[
            {"role": "user", "content": f"提取產品信息：\n{text}"}
        ],
        stream=True
    )

    feature_count = 0
    for partial_product in product_stream:
        # 實時顯示接收到的功能特性
        if hasattr(partial_product, 'features'):
            current_count = len(partial_product.features)
            if current_count > feature_count:
                new_features = partial_product.features[feature_count:]
                for feature in new_features:
                    print(f"  + 功能: {feature}")
                feature_count = current_count

        final_product = partial_product

    print("-" * 60)
    print(f"\n✓ 提取完成！")
    print(f"\n產品: {final_product.name}")
    print(f"價格: ${final_product.price}")
    print(f"總共 {len(final_product.features)} 個功能特性")


def stream_todo_list(client):
    """流式待辦事項列表提取

    展示如何流式提取和處理待辦事項列表。
    """
    print(f"\n{'='*60}")
    print("流式待辦事項列表提取")
    print(f"{'='*60}")

    text = """
    項目：網站重構

    待辦任務：

    1. UI設計更新
       - 創建新的設計稿
       - 優先級：高
       - 預計：20小時

    2. 前端開發
       - 使用React重寫前端
       - 優先級：高
       - 預計：40小時

    3. API重構
       - 優化後端API
       - 優先級：中
       - 預計：30小時

    4. 測試和部署
       - 完整的測試覆蓋
       - 優先級：高
       - 預計：15小時
    """

    print("\n正在提取任務列表...")
    print()

    todo_stream = client.chat.completions.create_partial(
        model="gpt-4",
        response_model=Partial[TodoList],
        messages=[
            {"role": "user", "content": f"提取待辦事項列表：\n{text}"}
        ],
        stream=True
    )

    task_count = 0
    for partial_todos in todo_stream:
        if hasattr(partial_todos, 'items'):
            current_count = len(partial_todos.items)
            if current_count > task_count:
                # 有新任務
                new_tasks = partial_todos.items[task_count:]
                for task in new_tasks:
                    if hasattr(task, 'title'):
                        print(f"  [{task_count + 1}] {task.title}")
                        if hasattr(task, 'priority'):
                            print(f"      優先級: {task.priority}")
                        if hasattr(task, 'estimated_hours'):
                            print(f"      預估: {task.estimated_hours}小時")
                        print()
                task_count = current_count

    print("✓ 所有任務已提取！")


# ============================================================================
# 高級流式場景
# ============================================================================

def stream_long_form_content(client):
    """流式長文本內容提取

    展示如何處理長文本內容的流式提取。
    """
    print(f"\n{'='*60}")
    print("流式長文本內容提取")
    print(f"{'='*60}")

    prompt = """
    請生成一份關於"人工智能在教育領域的應用"的報告，包括：
    - 標題
    - 執行摘要（2-3句話）
    - 3個主要章節
    - 5個關鍵發現
    - 3個建議
    - 結論
    """

    print("\n正在生成報告...")
    print("=" * 60)

    report_stream = client.chat.completions.create_partial(
        model="gpt-4",
        response_model=Partial[StreamingReport],
        messages=[
            {"role": "user", "content": prompt}
        ],
        stream=True
    )

    sections_shown = False
    findings_count = 0
    recommendations_count = 0

    for partial_report in report_stream:
        # 顯示標題
        if hasattr(partial_report, 'title') and not sections_shown:
            print(f"\n標題: {partial_report.title}")
            print("-" * 60)

        # 顯示摘要
        if hasattr(partial_report, 'executive_summary') and not sections_shown:
            print(f"\n執行摘要:")
            print(f"{partial_report.executive_summary}")
            sections_shown = True

        # 流式顯示發現
        if hasattr(partial_report, 'findings'):
            current_count = len(partial_report.findings)
            if current_count > findings_count:
                if findings_count == 0:
                    print(f"\n主要發現:")
                new_findings = partial_report.findings[findings_count:]
                for finding in new_findings:
                    print(f"  • {finding}")
                findings_count = current_count

        # 流式顯示建議
        if hasattr(partial_report, 'recommendations'):
            current_count = len(partial_report.recommendations)
            if current_count > recommendations_count:
                if recommendations_count == 0:
                    print(f"\n建議:")
                new_recs = partial_report.recommendations[recommendations_count:]
                for rec in new_recs:
                    print(f"  → {rec}")
                recommendations_count = current_count

        final_report = partial_report

    # 顯示結論
    if hasattr(final_report, 'conclusion'):
        print(f"\n結論:")
        print(f"{final_report.conclusion}")

    print("\n" + "=" * 60)
    print("✓ 報告生成完成！")


def stream_with_real_time_analysis(client):
    """帶實時分析的流式提取

    展示如何在流式提取過程中進行實時分析和處理。
    """
    print(f"\n{'='*60}")
    print("實時分析流式提取")
    print(f"{'='*60}")

    text = """
    分析以下產品的用戶反饋：

    用戶反饋集合包含了以下關鍵點：
    - 界面設計獲得一致好評
    - 性能表現優秀，響應迅速
    - 部分用戶反映學習曲線較陡
    - 客戶支持響應及時
    - 價格被認為物有所值
    - 缺少某些高級功能
    - 文檔質量需要改進
    - 移動端體驗良好

    請提供綜合分析和評分（0-100分）。
    """

    print("\n開始實時分析...")
    print()

    analysis_stream = client.chat.completions.create_partial(
        model="gpt-4",
        response_model=Partial[AnalysisResult],
        messages=[
            {"role": "user", "content": text}
        ],
        stream=True
    )

    insights_count = 0
    data_points_count = 0

    for partial_analysis in analysis_stream:
        # 實時顯示數據點
        if hasattr(partial_analysis, 'data_points'):
            current = len(partial_analysis.data_points)
            if current > data_points_count:
                if data_points_count == 0:
                    print("數據點:")
                for dp in partial_analysis.data_points[data_points_count:]:
                    print(f"  📊 {dp}")
                data_points_count = current

        # 實時顯示洞察
        if hasattr(partial_analysis, 'insights'):
            current = len(partial_analysis.insights)
            if current > insights_count:
                if insights_count == 0:
                    print("\n洞察:")
                for insight in partial_analysis.insights[insights_count:]:
                    print(f"  💡 {insight}")
                insights_count = current

        # 顯示評分
        if hasattr(partial_analysis, 'score'):
            final_analysis = partial_analysis

    print(f"\n最終評分: {final_analysis.score:.1f}/100")
    print("\n✓ 分析完成！")


# ============================================================================
# 流式錯誤處理
# ============================================================================

def stream_with_error_handling(client):
    """帶錯誤處理的流式提取

    展示如何在流式提取中處理錯誤和異常。
    """
    print(f"\n{'='*60}")
    print("流式錯誤處理示例")
    print(f"{'='*60}")

    text = "請生成一個用戶信息，包含姓名、年齡和郵箱"

    print("\n開始流式提取（帶錯誤處理）...")

    try:
        user_stream = client.chat.completions.create_partial(
            model="gpt-4",
            response_model=Partial[User],
            messages=[
                {"role": "user", "content": text}
            ],
            stream=True
        )

        received_fields = set()
        for partial_user in user_stream:
            # 跟蹤接收到的字段
            for field in ['name', 'age', 'email', 'bio']:
                if hasattr(partial_user, field) and field not in received_fields:
                    received_fields.add(field)
                    print(f"  ✓ 接收到字段: {field}")

        print("\n✓ 流式提取成功完成！")

    except Exception as e:
        print(f"\n✗ 流式提取過程中出錯: {str(e)}")
        print(f"  已接收字段: {', '.join(received_fields)}")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主函數 - 運行所有流式提取示例"""
    print("="*60)
    print("Instructor 流式提取示例")
    print("="*60)

    client = setup_client()

    # 基礎示例
    basic_streaming_extraction(client)
    stream_with_visualization(client)

    # 列表處理
    stream_list_extraction(client)
    stream_todo_list(client)

    # 高級場景
    stream_long_form_content(client)
    stream_with_real_time_analysis(client)

    # 錯誤處理
    stream_with_error_handling(client)

    print("\n" + "="*60)
    print("流式提取要點總結")
    print("="*60)
    print("""
1. 使用 Partial 模型：
   - 導入：from instructor import Partial
   - 包裝模型：Partial[YourModel]
   - 允許接收不完整的數據

2. 啟用流式模式：
   - 使用 create_partial() 方法
   - 設置 stream=True
   - 返回迭代器

3. 處理流式數據：
   - 遍歷部分結果
   - 使用 hasattr() 檢查字段
   - 追蹤接收進度

4. 適用場景：
   - 長文本生成
   - 實時反饋
   - 大量列表數據
   - 用戶體驗優化

5. 最佳實踐：
   - 優雅處理部分數據
   - 提供進度反饋
   - 處理流式錯誤
   - 保存最終結果
    """)


if __name__ == "__main__":
    main()
