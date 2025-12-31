"""
Instructor 快速開始示例

這個模塊展示了如何使用 Instructor 進行基本的結構化數據提取。
包含了最基礎的設置、簡單的數據模型定義和提取示例。

主要內容：
1. Instructor 基本設置
2. 簡單的 Pydantic 模型定義
3. 基礎數據提取示例
4. 不同數據類型的處理
5. 錯誤處理基礎

作者: Instructor 示例
日期: 2025-01-01
"""

import os
from typing import Optional, List
from pydantic import BaseModel, Field
import instructor
from openai import OpenAI


# ============================================================================
# 基礎數據模型定義
# ============================================================================

class User(BaseModel):
    """用戶信息模型

    這是一個簡單的用戶信息模型，包含基本的用戶屬性。
    """
    name: str = Field(description="用戶的全名")
    age: int = Field(description="用戶的年齡")
    email: str = Field(description="用戶的電子郵件地址")

    class Config:
        """Pydantic 配置"""
        json_schema_extra = {
            "example": {
                "name": "張三",
                "age": 30,
                "email": "zhangsan@example.com"
            }
        }


class Product(BaseModel):
    """產品信息模型

    用於提取產品相關信息的數據模型。
    """
    name: str = Field(description="產品名稱")
    price: float = Field(description="產品價格（美元）")
    category: str = Field(description="產品類別")
    description: Optional[str] = Field(default=None, description="產品描述")
    in_stock: bool = Field(default=True, description="是否有貨")


class Article(BaseModel):
    """文章信息模型

    用於從文本中提取文章的關鍵信息。
    """
    title: str = Field(description="文章標題")
    author: str = Field(description="文章作者")
    publish_date: str = Field(description="發布日期")
    summary: str = Field(description="文章摘要（100字以內）")
    tags: List[str] = Field(description="文章標籤列表")


class ContactInfo(BaseModel):
    """聯繫信息模型

    從文本中提取完整的聯繫信息。
    """
    name: str = Field(description="聯繫人姓名")
    phone: Optional[str] = Field(default=None, description="電話號碼")
    email: Optional[str] = Field(default=None, description="電子郵件")
    address: Optional[str] = Field(default=None, description="地址")
    company: Optional[str] = Field(default=None, description="公司名稱")


class Sentiment(BaseModel):
    """情感分析模型

    分析文本的情感傾向。
    """
    sentiment: str = Field(description="情感類別：正面、負面或中性")
    confidence: float = Field(
        description="置信度（0-1之間）",
        ge=0.0,
        le=1.0
    )
    reasoning: str = Field(description="判斷理由")


# ============================================================================
# Instructor 客戶端設置
# ============================================================================

def setup_instructor_client():
    """設置 Instructor 客戶端

    這個函數展示了如何正確設置 Instructor 客戶端。
    支持從環境變量讀取 API 密鑰。

    Returns:
        配置好的 Instructor 客戶端
    """
    # 從環境變量獲取 API 密鑰
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("警告: 未設置 OPENAI_API_KEY 環境變量")
        print("請設置: export OPENAI_API_KEY='your-api-key'")
        # 為演示目的使用占位符
        api_key = "sk-placeholder-key"

    # 創建 OpenAI 客戶端
    openai_client = OpenAI(api_key=api_key)

    # 使用 Instructor 包裝客戶端
    # 這會為客戶端添加結構化輸出功能
    client = instructor.from_openai(openai_client)

    print("✓ Instructor 客戶端設置完成")
    return client


# ============================================================================
# 基礎提取示例
# ============================================================================

def extract_user_info(client, text: str) -> User:
    """從文本中提取用戶信息

    這是最基本的提取示例，展示了如何使用 Instructor
    從非結構化文本中提取結構化的用戶信息。

    Args:
        client: Instructor 客戶端
        text: 包含用戶信息的文本

    Returns:
        User: 提取的用戶信息對象
    """
    print(f"\n{'='*60}")
    print("提取用戶信息")
    print(f"{'='*60}")
    print(f"輸入文本: {text}")

    try:
        # 使用 Instructor 進行結構化提取
        user = client.chat.completions.create(
            model="gpt-4",
            response_model=User,
            messages=[
                {
                    "role": "system",
                    "content": "你是一個數據提取助手。從用戶提供的文本中提取結構化的用戶信息。"
                },
                {
                    "role": "user",
                    "content": f"請從以下文本中提取用戶信息：\n{text}"
                }
            ]
        )

        print(f"\n提取結果:")
        print(f"  姓名: {user.name}")
        print(f"  年齡: {user.age}")
        print(f"  郵箱: {user.email}")

        return user

    except Exception as e:
        print(f"錯誤: {str(e)}")
        raise


def extract_product_info(client, text: str) -> Product:
    """從文本中提取產品信息

    展示如何提取包含可選字段的產品信息。

    Args:
        client: Instructor 客戶端
        text: 包含產品信息的文本

    Returns:
        Product: 提取的產品信息對象
    """
    print(f"\n{'='*60}")
    print("提取產品信息")
    print(f"{'='*60}")
    print(f"輸入文本: {text}")

    product = client.chat.completions.create(
        model="gpt-4",
        response_model=Product,
        messages=[
            {
                "role": "user",
                "content": f"提取產品信息：\n{text}"
            }
        ]
    )

    print(f"\n產品詳情:")
    print(f"  名稱: {product.name}")
    print(f"  價格: ${product.price}")
    print(f"  類別: {product.category}")
    print(f"  描述: {product.description or '無'}")
    print(f"  庫存: {'有貨' if product.in_stock else '缺貨'}")

    return product


def extract_article_metadata(client, text: str) -> Article:
    """從文本中提取文章元數據

    展示如何提取包含列表字段的複雜信息。

    Args:
        client: Instructor 客戶端
        text: 文章文本

    Returns:
        Article: 提取的文章元數據
    """
    print(f"\n{'='*60}")
    print("提取文章元數據")
    print(f"{'='*60}")
    print(f"文章預覽: {text[:100]}...")

    article = client.chat.completions.create(
        model="gpt-4",
        response_model=Article,
        messages=[
            {
                "role": "user",
                "content": f"請分析以下文章並提取元數據：\n\n{text}"
            }
        ]
    )

    print(f"\n文章信息:")
    print(f"  標題: {article.title}")
    print(f"  作者: {article.author}")
    print(f"  日期: {article.publish_date}")
    print(f"  摘要: {article.summary}")
    print(f"  標籤: {', '.join(article.tags)}")

    return article


def extract_contact_info(client, text: str) -> ContactInfo:
    """從名片或簡介中提取聯繫信息

    展示如何處理多個可選字段。

    Args:
        client: Instructor 客戶端
        text: 包含聯繫信息的文本

    Returns:
        ContactInfo: 提取的聯繫信息
    """
    print(f"\n{'='*60}")
    print("提取聯繫信息")
    print(f"{'='*60}")
    print(f"輸入: {text}")

    contact = client.chat.completions.create(
        model="gpt-4",
        response_model=ContactInfo,
        messages=[
            {
                "role": "user",
                "content": f"從以下名片信息中提取聯繫方式：\n{text}"
            }
        ]
    )

    print(f"\n聯繫信息:")
    print(f"  姓名: {contact.name}")
    if contact.phone:
        print(f"  電話: {contact.phone}")
    if contact.email:
        print(f"  郵箱: {contact.email}")
    if contact.address:
        print(f"  地址: {contact.address}")
    if contact.company:
        print(f"  公司: {contact.company}")

    return contact


def analyze_sentiment(client, text: str) -> Sentiment:
    """分析文本情感

    展示如何使用 Instructor 進行分類任務。

    Args:
        client: Instructor 客戶端
        text: 要分析的文本

    Returns:
        Sentiment: 情感分析結果
    """
    print(f"\n{'='*60}")
    print("情感分析")
    print(f"{'='*60}")
    print(f"文本: {text}")

    sentiment = client.chat.completions.create(
        model="gpt-4",
        response_model=Sentiment,
        messages=[
            {
                "role": "user",
                "content": f"分析以下文本的情感傾向：\n{text}"
            }
        ]
    )

    print(f"\n分析結果:")
    print(f"  情感: {sentiment.sentiment}")
    print(f"  置信度: {sentiment.confidence:.2%}")
    print(f"  理由: {sentiment.reasoning}")

    return sentiment


# ============================================================================
# 批量處理示例
# ============================================================================

def batch_extract_users(client, texts: List[str]) -> List[User]:
    """批量提取多個用戶信息

    展示如何高效處理多個提取任務。

    Args:
        client: Instructor 客戶端
        texts: 包含用戶信息的文本列表

    Returns:
        List[User]: 提取的用戶列表
    """
    print(f"\n{'='*60}")
    print(f"批量提取 {len(texts)} 個用戶信息")
    print(f"{'='*60}")

    users = []
    for i, text in enumerate(texts, 1):
        print(f"\n處理第 {i}/{len(texts)} 個...")
        try:
            user = extract_user_info(client, text)
            users.append(user)
        except Exception as e:
            print(f"  跳過（錯誤: {str(e)}）")

    print(f"\n成功提取 {len(users)} 個用戶")
    return users


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主函數 - 運行所有示例"""
    print("="*60)
    print("Instructor 快速開始示例")
    print("="*60)

    # 設置客戶端
    client = setup_instructor_client()

    # 示例 1: 提取用戶信息
    user_text = """
    我叫李明，今年28歲，是一名軟件工程師。
    你可以通過 liming@tech.com 聯繫我。
    """
    extract_user_info(client, user_text)

    # 示例 2: 提取產品信息
    product_text = """
    產品名稱：無線藍牙耳機 Pro
    售價：$129.99
    類別：電子產品
    這是一款高品質的主動降噪無線耳機，電池續航可達30小時。
    目前有貨。
    """
    extract_product_info(client, product_text)

    # 示例 3: 提取文章元數據
    article_text = """
    標題：人工智能在醫療領域的應用前景
    作者：王教授
    發布日期：2025-01-15

    隨著深度學習技術的發展，人工智能在醫療診斷、藥物研發和
    個性化治療等領域展現出巨大潛力。本文探討了AI技術如何
    改變現代醫療實踐，以及面臨的挑戰和未來發展方向。

    關鍵詞：人工智能、醫療、深度學習、診斷、藥物研發
    """
    extract_article_metadata(client, article_text)

    # 示例 4: 提取聯繫信息
    contact_text = """
    張經理
    科技創新有限公司
    電話: +86 138-0000-1234
    郵箱: zhang.manager@techinnovate.com
    地址: 北京市朝陽區科技園路100號
    """
    extract_contact_info(client, contact_text)

    # 示例 5: 情感分析
    sentiment_text = "這個產品真的太棒了！質量超出預期，客服態度也很好，強烈推薦！"
    analyze_sentiment(client, sentiment_text)

    # 示例 6: 批量處理
    batch_texts = [
        "姓名：趙一，25歲，郵箱：zhaoyi@example.com",
        "王二，30歲，聯繫方式：wanger@example.com",
        "錢三，35歲，email: qiansan@example.com"
    ]
    batch_extract_users(client, batch_texts)

    print("\n" + "="*60)
    print("所有示例運行完成！")
    print("="*60)
    print("\n下一步:")
    print("- 查看 02_模型定義.py 學習更複雜的模型定義")
    print("- 查看 03_驗證重試.py 學習數據驗證")
    print("- 修改上面的示例，嘗試提取不同類型的數據")


if __name__ == "__main__":
    main()
