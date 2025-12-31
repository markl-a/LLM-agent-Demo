"""
Marvin 圖像處理示例

本示例展示：
1. 圖像描述生成
2. 視覺問答
3. 圖像分類
4. OCR 識別
5. 多圖像處理

注意：
- 需要安裝 marvin[images]
- 需要實際的圖像文件

運行方式：
    python 06_圖像處理.py
"""

import os
import marvin
from pathlib import Path
from typing import List
from pydantic import BaseModel


# ==================== 圖像描述 ====================

def example_image_caption():
    """示例 1: 圖像描述生成"""
    print("\n" + "="*60)
    print("示例 1: 圖像描述生成")
    print("="*60)

    try:
        # 注意：這裡使用模擬路徑，實際使用時替換為真實圖像
        print("圖像描述功能示例:")
        print("使用 marvin.caption() 可以為圖像生成描述\n")

        # 示例代碼（需要真實圖像文件）
        print("示例代碼:")
        print("""
        # 為單張圖像生成描述
        description = marvin.caption("path/to/image.jpg")
        print(f"圖像描述: {description}")

        # 自定義描述要求
        description = marvin.caption(
            "path/to/image.jpg",
            instructions="用一句話描述圖像的主要內容"
        )
        """)

        print("\n功能特點:")
        print("  ✅ 自動生成詳細描述")
        print("  ✅ 識別物體和場景")
        print("  ✅ 理解圖像語境")
        print("  ✅ 支持多種圖像格式")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 視覺問答 ====================

def example_visual_qa():
    """示例 2: 視覺問答"""
    print("\n" + "="*60)
    print("示例 2: 視覺問答")
    print("="*60)

    try:
        print("視覺問答功能示例:")
        print("使用 marvin.vision.ask() 對圖像進行提問\n")

        print("示例代碼:")
        print("""
        # 詢問圖像內容
        answer = marvin.vision.ask(
            "這張圖片裡有什麼？",
            image="product.jpg"
        )
        print(f"回答: {answer}")

        # 詢問具體細節
        answer = marvin.vision.ask(
            "圖片中的人穿什麼顏色的衣服？",
            image="photo.jpg"
        )

        # 詢問數量
        answer = marvin.vision.ask(
            "圖片中有幾個人？",
            image="group.jpg"
        )
        """)

        print("\n應用場景:")
        print("  📸 產品信息提取")
        print("  🏷️ 內容理解")
        print("  🔍 細節識別")
        print("  📊 視覺分析")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 圖像分類 ====================

class ImageCategory(BaseModel):
    """圖像分類結果"""
    category: str
    confidence: str
    description: str


def example_image_classification():
    """示例 3: 圖像分類"""
    print("\n" + "="*60)
    print("示例 3: 圖像分類")
    print("="*60)

    try:
        print("圖像分類功能示例:")
        print("結合 classify() 和 vision 功能進行圖像分類\n")

        print("示例代碼:")
        print("""
        from enum import Enum

        class ImageType(str, Enum):
            PRODUCT = "product"
            LANDSCAPE = "landscape"
            PORTRAIT = "portrait"
            DOCUMENT = "document"
            FOOD = "food"

        # 先獲取圖像描述
        description = marvin.caption("image.jpg")

        # 基於描述分類
        category = marvin.classify(
            description,
            labels=ImageType
        )

        print(f"圖像類型: {category}")
        """)

        print("\n分類類別示例:")
        print("  🖼️ 產品圖片")
        print("  🌄 風景照片")
        print("  👤 人像照片")
        print("  📄 文檔掃描")
        print("  🍔 美食圖片")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== OCR 識別 ====================

class DocumentInfo(BaseModel):
    """文檔信息"""
    title: str
    text_content: str
    language: str


def example_ocr():
    """示例 4: OCR 文字識別"""
    print("\n" + "="*60)
    print("示例 4: OCR 文字識別")
    print("="*60)

    try:
        print("OCR 功能示例:")
        print("從圖像中提取文字內容\n")

        print("示例代碼:")
        print("""
        # 提取圖像中的文字
        text = marvin.vision.ask(
            "請提取圖像中的所有文字",
            image="document.jpg"
        )
        print(f"提取的文字: {text}")

        # 結構化提取
        doc_info = marvin.extract_from_image(
            "receipt.jpg",
            target=DocumentInfo
        )
        print(f"標題: {doc_info.title}")
        print(f"內容: {doc_info.text_content}")
        """)

        print("\n應用場景:")
        print("  📝 收據識別")
        print("  💳 名片掃描")
        print("  📋 表單處理")
        print("  📖 文檔數字化")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 多圖像處理 ====================

def example_multi_image():
    """示例 5: 多圖像處理"""
    print("\n" + "="*60)
    print("示例 5: 多圖像處理")
    print("="*60)

    try:
        print("多圖像處理示例:")
        print("批量處理和比較多張圖像\n")

        print("示例代碼:")
        print("""
        import asyncio

        async def process_images(image_paths: List[str]):
            # 並發處理多張圖像
            tasks = [
                marvin.caption_async(path)
                for path in image_paths
            ]
            descriptions = await asyncio.gather(*tasks)
            return descriptions

        # 比較兩張圖像
        answer = marvin.vision.ask(
            "這兩張圖片有什麼不同？",
            images=["image1.jpg", "image2.jpg"]
        )
        """)

        print("\n應用場景:")
        print("  📊 批量圖像分析")
        print("  🔄 圖像對比")
        print("  📸 相冊整理")
        print("  🎨 風格分析")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 圖像內容提取 ====================

class ProductInfo(BaseModel):
    """產品信息"""
    name: str
    brand: str
    color: str
    price: str
    features: List[str]


def example_image_extraction():
    """示例 6: 從圖像提取結構化信息"""
    print("\n" + "="*60)
    print("示例 6: 圖像內容提取")
    print("="*60)

    try:
        print("從圖像提取結構化信息:")
        print("結合視覺理解和數據提取\n")

        print("示例代碼:")
        print("""
        # 從產品圖提取信息
        description = marvin.caption("product.jpg")
        product = marvin.extract(description, target=ProductInfo)

        print(f"產品名稱: {product.name}")
        print(f"品牌: {product.brand}")
        print(f"顏色: {product.color}")
        print(f"價格: {product.price}")
        print(f"特點: {', '.join(product.features)}")

        # 直接從圖像提取
        info = marvin.vision.extract(
            image="product.jpg",
            target=ProductInfo
        )
        """)

        print("\n提取內容類型:")
        print("  🏷️ 產品詳情")
        print("  📊 表格數據")
        print("  📝 表單字段")
        print("  🗺️ 地圖信息")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 圖像質量評估 ====================

class ImageQuality(BaseModel):
    """圖像質量"""
    clarity: str  # clear, blurry
    lighting: str  # good, poor, overexposed, underexposed
    composition: str  # good, poor
    issues: List[str]


def example_image_quality():
    """示例 7: 圖像質量評估"""
    print("\n" + "="*60)
    print("示例 7: 圖像質量評估")
    print("="*60)

    try:
        print("圖像質量評估示例:")
        print("自動評估圖像的質量和問題\n")

        print("示例代碼:")
        print("""
        # 評估圖像質量
        quality = marvin.vision.analyze(
            image="photo.jpg",
            target=ImageQuality
        )

        print(f"清晰度: {quality.clarity}")
        print(f"光線: {quality.lighting}")
        print(f"構圖: {quality.composition}")
        if quality.issues:
            print(f"問題: {', '.join(quality.issues)}")
        """)

        print("\n評估維度:")
        print("  🔍 清晰度")
        print("  💡 光線質量")
        print("  📐 構圖")
        print("  ⚠️ 問題檢測")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║        Marvin 圖像處理示例                ║
╚══════════════════════════════════════════╝

Marvin 圖像功能:
✅ 圖像描述生成
✅ 視覺問答
✅ 圖像分類
✅ OCR 文字識別
✅ 多圖像處理

注意：
⚠️ 需要安裝: pip install marvin[images]
⚠️ 需要提供實際的圖像文件
⚠️ 圖像處理會消耗更多 API 調用
    """)

    # 檢查環境
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 請設置 OPENAI_API_KEY 環境變量")
        return

    # 配置 Marvin
    marvin.settings.openai.api_key = os.getenv("OPENAI_API_KEY")

    # 運行示例（演示性質，不實際調用 API）
    example_image_caption()
    example_visual_qa()
    example_image_classification()
    example_ocr()
    example_multi_image()
    example_image_extraction()
    example_image_quality()

    print("\n" + "="*60)
    print("✅ 所有示例演示完成！")
    print("="*60)
    print("\n💡 提示: 要運行實際的圖像處理，請:")
    print("   1. 準備圖像文件")
    print("   2. 修改示例代碼中的圖像路徑")
    print("   3. 取消註釋相關代碼")


if __name__ == "__main__":
    main()
