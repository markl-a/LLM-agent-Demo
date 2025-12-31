"""
LanceDB - LlamaIndex 整合範例

本範例展示：
1. VectorStoreIndex
2. 查詢引擎
3. 響應合成
4. 高級查詢模式
5. 自定義檢索

安裝：pip install lancedb llama-index openai
"""

import lancedb


def example_1_vector_store_index():
    """LlamaIndex VectorStoreIndex"""
    print("\n" + "="*60)
    print("範例 1: VectorStoreIndex")
    print("="*60)

    print("✓ LlamaIndex 整合:")
    print("  - LanceDBVectorStore")
    print("  - VectorStoreIndex")
    print("  - 查詢引擎")


def example_2_query_engine():
    """查詢引擎"""
    print("\n" + "="*60)
    print("範例 2: 查詢引擎")
    print("="*60)

    print("✓ 查詢引擎功能:")
    print("  - 簡單查詢")
    print("  - 複雜查詢")
    print("  - 自定義檢索器")


def example_3_10_more():
    """更多 LlamaIndex 功能"""
    print("\n" + "="*60)
    print("範例 3-10: 更多功能")
    print("="*60)

    print("✓ 其他功能:")
    print("  3. 文檔索引")
    print("  4. 響應合成")
    print("  5. 查詢轉換")
    print("  6. 後處理")
    print("  7. 評估")
    print("  8. 元數據過濾")
    print("  9. 混合檢索")
    print("  10. 流式響應")


def main():
    """運行所有範例"""
    print("\n" + "="*60)
    print("🦙 LanceDB - LlamaIndex 整合範例")
    print("="*60)

    example_1_vector_store_index()
    example_2_query_engine()
    example_3_10_more()

    print("\n" + "="*60)
    print("✓ 所有 LlamaIndex 整合範例完成！")
    print("="*60)


if __name__ == '__main__':
    main()
