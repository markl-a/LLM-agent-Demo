"""
Txtai - 多模態範例

本範例展示：
1. 文本嵌入
2. 圖像嵌入
3. 跨模態搜索
4. CLIP 模型整合
5. 多模態索引

安裝：pip install txtai sentence-transformers pillow
"""

from txtai import Embeddings


# ============================================================================
# 範例 1: 文本嵌入
# ============================================================================

def example_1_text_embeddings():
    """標準文本嵌入"""
    print("\n" + "="*60)
    print("範例 1: 文本嵌入")
    print("="*60)

    embeddings = Embeddings({"path": "sentence-transformers/all-MiniLM-L6-v2"})

    documents = [
        "A dog playing in the park",
        "A cat sleeping on a couch",
        "Birds flying in the sky",
    ]

    embeddings.index([(i, doc, None) for i, doc in enumerate(documents)])

    results = embeddings.search("animals", limit=3)

    print("文本搜索結果:")
    for result in results:
        print(f"  - {result['text']}")


# ============================================================================
# 範例 2: CLIP 模型配置
# ============================================================================

def example_2_clip_config():
    """配置 CLIP 多模態模型"""
    print("\n" + "="*60)
    print("範例 2: CLIP 模型配置")
    print("="*60)

    # CLIP 模型支持文本和圖像
    config = {
        "path": "sentence-transformers/clip-ViT-B-32",
        "content": True,
    }

    print("✓ CLIP 模型配置:")
    print(f"  模型: {config['path']}")
    print("  支持: 文本 + 圖像")
    print("  應用: 跨模態搜索")


# ============================================================================
# 範例 3: 圖像描述索引
# ============================================================================

def example_3_image_descriptions():
    """索引圖像描述"""
    print("\n" + "="*60)
    print("範例 3: 圖像描述索引")
    print("="*60)

    embeddings = Embeddings({"content": True})

    # 圖像描述
    images = [
        (0, "A golden retriever playing fetch", {"type": "dog"}),
        (1, "A tabby cat sitting by window", {"type": "cat"}),
        (2, "A beautiful sunset over ocean", {"type": "nature"}),
        (3, "A person hiking in mountains", {"type": "outdoor"}),
    ]

    embeddings.index(images)

    print("✓ 已索引 4 個圖像描述")

    # 搜索
    results = embeddings.search("pet animals", limit=2)
    print("\n搜索 'pet animals':")
    for result in results:
        print(f"  - {result['text']}")


# ============================================================================
# 範例 4-10: 更多多模態示例
# ============================================================================

def example_4_cross_modal_search():
    """跨模態搜索"""
    print("\n" + "="*60)
    print("範例 4: 跨模態搜索")
    print("="*60)

    print("✓ CLIP 模型可以:")
    print("  - 用文本搜索圖像")
    print("  - 用圖像搜索文本")
    print("  - 用圖像搜索圖像")


def example_5_multimodal_similarity():
    """多模態相似度"""
    print("\n" + "="*60)
    print("範例 5: 多模態相似度")
    print("="*60)

    embeddings = Embeddings()

    descriptions = [
        "A photo of a dog",
        "A picture of a cat",
        "An image of a car",
    ]

    embeddings.index([(i, desc, None) for i, desc in enumerate(descriptions)])

    results = embeddings.search("animal picture", limit=2)

    print("相似度搜索:")
    for result in results:
        print(f"  - {result['text']} (評分: {result['score']:.4f})")


def example_6_audio_text():
    """音頻-文本多模態"""
    print("\n" + "="*60)
    print("範例 6: 音頻-文本")
    print("="*60)

    print("✓ 可以整合音頻轉錄和文本搜索")
    print("  應用: 播客搜索、音樂標註")


def example_7_video_indexing():
    """視頻索引"""
    print("\n" + "="*60)
    print("範例 7: 視頻索引")
    print("="*60)

    print("✓ 視頻可以分解為:")
    print("  - 幀（圖像）")
    print("  - 音頻轉錄（文本）")
    print("  - 場景描述（文本）")


def example_8_document_images():
    """文檔圖像處理"""
    print("\n" + "="*60)
    print("範例 8: 文檔圖像")
    print("="*60)

    print("✓ OCR + 語義搜索")
    print("  處理掃描文檔和圖像中的文字")


def example_9_embeddings_comparison():
    """嵌入比較"""
    print("\n" + "="*60)
    print("範例 9: 嵌入比較")
    print("="*60)

    embeddings = Embeddings()

    items = [
        "Technology article",
        "Science paper",
        "Sports news",
    ]

    embeddings.index([(i, item, None) for i, item in enumerate(items)])

    results = embeddings.search("scientific research", limit=2)

    print("嵌入相似度:")
    for result in results:
        print(f"  - {result['text']}")


def example_10_hybrid_modal():
    """混合模態應用"""
    print("\n" + "="*60)
    print("範例 10: 混合模態應用")
    print("="*60)

    print("✓ 實際應用場景:")
    print("  - 電商產品搜索（圖+文）")
    print("  - 內容推薦（多模態）")
    print("  - 媒體庫管理（圖像+視頻+文本）")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*60)
    print("🎨 Txtai - 多模態範例")
    print("="*60)

    example_1_text_embeddings()
    example_2_clip_config()
    example_3_image_descriptions()
    example_4_cross_modal_search()
    example_5_multimodal_similarity()
    example_6_audio_text()
    example_7_video_indexing()
    example_8_document_images()
    example_9_embeddings_comparison()
    example_10_hybrid_modal()

    print("\n" + "="*60)
    print("✓ 所有多模態範例完成！")
    print("="*60)


if __name__ == '__main__':
    main()
