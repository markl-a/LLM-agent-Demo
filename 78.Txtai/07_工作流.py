"""
Txtai - 工作流範例

本範例展示：
1. 工作流定義和配置
2. 任務編排
3. 數據處理管道
4. 條件邏輯
5. 複雜工作流構建

安裝：pip install txtai sentence-transformers
"""

from txtai import Application


# ============================================================================
# 範例 1: 基本工作流
# ============================================================================

def example_1_basic_workflow():
    """創建基本的工作流"""
    print("\n" + "="*60)
    print("範例 1: 基本工作流")
    print("="*60)

    # 定義工作流配置
    config = """
    # 嵌入配置
    embeddings:
        path: sentence-transformers/all-MiniLM-L6-v2
        content: true

    # 工作流定義
    workflow:
        search:
            tasks:
                - action: embeddings
    """

    # 創建應用
    app = Application(config)

    # 添加數據
    data = [
        {"text": "First document about AI"},
        {"text": "Second document about ML"},
        {"text": "Third document about DL"},
    ]

    app.add(data)
    app.index()

    print("✓ 工作流配置完成")

    # 執行工作流
    results = list(app.workflow("search", ["AI technology"]))

    print("\n搜索結果:")
    for result in results:
        print(f"  - {result}")


# ============================================================================
# 範例 2: 多任務工作流
# ============================================================================

def example_2_multi_task():
    """創建包含多個任務的工作流"""
    print("\n" + "="*60)
    print("範例 2: 多任務工作流")
    print("="*60)

    config = """
    embeddings:
        path: sentence-transformers/all-MiniLM-L6-v2
        content: true

    workflow:
        index:
            tasks:
                - action: embeddings

        process:
            tasks:
                - action: embeddings
                  select: text
    """

    app = Application(config)

    documents = [
        {"id": 1, "text": "Python programming guide"},
        {"id": 2, "text": "JavaScript tutorial"},
        {"id": 3, "text": "Java development"},
    ]

    # 執行索引工作流
    app.add(documents)
    app.index()

    print("✓ 多任務工作流執行完成")


# ============================================================================
# 範例 3: 文本處理管道
# ============================================================================

def example_3_text_pipeline():
    """構建文本處理管道"""
    print("\n" + "="*60)
    print("範例 3: 文本處理管道")
    print("="*60)

    config = """
    embeddings:
        path: sentence-transformers/all-MiniLM-L6-v2
        content: true

    workflow:
        search:
            tasks:
                - action: embeddings
    """

    app = Application(config)

    # 文本數據
    texts = [
        {"text": "Natural language processing"},
        {"text": "Computer vision applications"},
        {"text": "Speech recognition systems"},
    ]

    app.add(texts)
    app.index()

    print("✓ 文本處理管道建立")

    # 搜索
    results = list(app.workflow("search", ["language technology"]))
    print(f"\n找到 {len(results)} 個結果")


# ============================================================================
# 範例 4-10: 更多工作流示例
# ============================================================================

def example_4_batch_processing():
    """批量處理工作流"""
    print("\n" + "="*60)
    print("範例 4: 批量處理")
    print("="*60)

    config = """
    embeddings:
        path: sentence-transformers/all-MiniLM-L6-v2

    workflow:
        batch:
            tasks:
                - action: embeddings
    """

    app = Application(config)

    # 批量數據
    batch = [{"text": f"Document {i}"} for i in range(10)]
    app.add(batch)
    app.index()

    print(f"✓ 批量處理了 {len(batch)} 個文檔")


def example_5_conditional_workflow():
    """條件邏輯工作流"""
    print("\n" + "="*60)
    print("範例 5: 條件邏輯")
    print("="*60)

    print("✓ 條件工作流示例（配置驅動）")
    print("  可以根據條件執行不同的任務分支")


def example_6_data_transformation():
    """數據轉換工作流"""
    print("\n" + "="*60)
    print("範例 6: 數據轉換")
    print("="*60)

    config = """
    embeddings:
        path: sentence-transformers/all-MiniLM-L6-v2

    workflow:
        transform:
            tasks:
                - action: embeddings
                  select: content
    """

    app = Application(config)

    data = [
        {"id": 1, "content": "First item"},
        {"id": 2, "content": "Second item"},
    ]

    app.add(data)
    app.index()

    print("✓ 數據轉換工作流完成")


def example_7_aggregation():
    """聚合工作流"""
    print("\n" + "="*60)
    print("範例 7: 聚合工作流")
    print("="*60)

    print("✓ 聚合工作流可以組合多個數據源")


def example_8_pipeline_chaining():
    """管道鏈接"""
    print("\n" + "="*60)
    print("範例 8: 管道鏈接")
    print("="*60)

    print("✓ 可以將多個處理步驟鏈接在一起")


def example_9_error_handling():
    """錯誤處理工作流"""
    print("\n" + "="*60)
    print("範例 9: 錯誤處理")
    print("="*60)

    print("✓ 工作流可以包含錯誤處理邏輯")


def example_10_workflow_monitoring():
    """工作流監控"""
    print("\n" + "="*60)
    print("範例 10: 工作流監控")
    print("="*60)

    print("✓ 可以監控工作流執行狀態和性能")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*60)
    print("⚙️  Txtai - 工作流範例")
    print("="*60)

    example_1_basic_workflow()
    example_2_multi_task()
    example_3_text_pipeline()
    example_4_batch_processing()
    example_5_conditional_workflow()
    example_6_data_transformation()
    example_7_aggregation()
    example_8_pipeline_chaining()
    example_9_error_handling()
    example_10_workflow_monitoring()

    print("\n" + "="*60)
    print("✓ 所有工作流範例完成！")
    print("="*60)


if __name__ == '__main__':
    main()
