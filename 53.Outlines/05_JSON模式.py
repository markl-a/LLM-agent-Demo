"""
Outlines JSON Schema 生成示例
=============================

本示例展示如何使用 Outlines 的 JSON Schema 約束進行結構化生成。

主要內容:
1. 基本 JSON Schema 生成
2. 嵌套對象生成
3. 數組和列表生成
4. 複雜數據模型
5. Schema 驗證

作者: Outlines 教學團隊
日期: 2025-01
"""

import outlines
from outlines import models, generate
import torch
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime, date
from enum import Enum
import logging
import json
import sys

# ==================== 設置日誌 ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== 數據模型定義 ====================

class UserRole(str, Enum):
    """用戶角色"""
    ADMIN = "管理員"
    USER = "普通用戶"
    GUEST = "訪客"


class Gender(str, Enum):
    """性別"""
    MALE = "男"
    FEMALE = "女"
    OTHER = "其他"


class Address(BaseModel):
    """地址模型"""
    street: str = Field(description="街道地址")
    city: str = Field(description="城市")
    state: Optional[str] = Field(None, description="州/省")
    country: str = Field(description="國家")
    postal_code: str = Field(description="郵政編碼")


class ContactInfo(BaseModel):
    """聯繫信息模型"""
    email: str = Field(description="電子郵件")
    phone: str = Field(description="電話號碼")
    address: Address = Field(description="地址")


class User(BaseModel):
    """用戶模型"""
    id: int = Field(description="用戶ID", ge=1)
    username: str = Field(description="用戶名", min_length=3, max_length=20)
    email: str = Field(description="郵箱地址")
    age: int = Field(description="年齡", ge=0, le=120)
    gender: Gender = Field(description="性別")
    role: UserRole = Field(default=UserRole.USER, description="角色")
    is_active: bool = Field(default=True, description="是否活躍")
    created_at: str = Field(description="創建時間")

    @validator('email')
    def validate_email(cls, v):
        """驗證郵箱格式"""
        if '@' not in v:
            raise ValueError('無效的郵箱地址')
        return v


class Product(BaseModel):
    """產品模型"""
    id: int = Field(description="產品ID", ge=1)
    name: str = Field(description="產品名稱")
    description: str = Field(description="產品描述")
    price: float = Field(description="價格", gt=0)
    quantity: int = Field(description="庫存數量", ge=0)
    category: str = Field(description="類別")
    tags: List[str] = Field(default_factory=list, description="標籤")
    is_available: bool = Field(default=True, description="是否可用")


class OrderItem(BaseModel):
    """訂單項目模型"""
    product_id: int = Field(description="產品ID")
    product_name: str = Field(description="產品名稱")
    quantity: int = Field(description="數量", ge=1)
    unit_price: float = Field(description="單價", gt=0)
    subtotal: float = Field(description="小計", gt=0)


class Order(BaseModel):
    """訂單模型"""
    order_id: str = Field(description="訂單號")
    user_id: int = Field(description="用戶ID")
    items: List[OrderItem] = Field(description="訂單項目")
    total_amount: float = Field(description="總金額", gt=0)
    status: str = Field(description="訂單狀態")
    created_at: str = Field(description="創建時間")
    shipping_address: Address = Field(description="配送地址")


class BlogPost(BaseModel):
    """博客文章模型"""
    title: str = Field(description="標題", min_length=1, max_length=200)
    content: str = Field(description="內容", min_length=10)
    author: str = Field(description="作者")
    tags: List[str] = Field(default_factory=list, description="標籤")
    views: int = Field(default=0, description="瀏覽次數", ge=0)
    likes: int = Field(default=0, description="點讚數", ge=0)
    published: bool = Field(default=False, description="是否發布")
    published_at: Optional[str] = Field(None, description="發布時間")


class Comment(BaseModel):
    """評論模型"""
    id: int = Field(description="評論ID")
    user_id: int = Field(description="用戶ID")
    content: str = Field(description="評論內容", min_length=1)
    rating: Optional[int] = Field(None, description="評分", ge=1, le=5)
    created_at: str = Field(description="創建時間")


class Review(BaseModel):
    """評價模型"""
    product_id: int = Field(description="產品ID")
    user_id: int = Field(description="用戶ID")
    rating: int = Field(description="評分", ge=1, le=5)
    title: str = Field(description="評價標題")
    content: str = Field(description="評價內容")
    helpful_count: int = Field(default=0, description="有用計數", ge=0)
    verified_purchase: bool = Field(description="是否已驗證購買")
    created_at: str = Field(description="創建時間")


class APIResponse(BaseModel):
    """API 響應模型"""
    status: str = Field(description="狀態")
    code: int = Field(description="狀態碼")
    message: str = Field(description="消息")
    data: Optional[Dict[str, Any]] = Field(None, description="數據")
    errors: Optional[List[str]] = Field(None, description="錯誤列表")
    timestamp: str = Field(description="時間戳")


# ==================== JSON Schema 生成管理器 ====================

class JSONSchemaManager:
    """
    JSON Schema 生成管理器

    管理基於 JSON Schema 的結構化生成
    """

    def __init__(self, model_name: str = "mistralai/Mistral-7B-v0.1"):
        """
        初始化 JSON Schema 管理器

        Args:
            model_name: 使用的模型名稱
        """
        self.model_name = model_name
        self.model = None
        self.load_model()

        logger.info(f"JSON Schema 管理器初始化完成,模型: {model_name}")

    def load_model(self):
        """載入語言模型"""
        try:
            logger.info(f"開始載入模型: {self.model_name}")

            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"使用設備: {device}")

            self.model = models.transformers(
                self.model_name,
                device=device
            )

            logger.info("模型載入完成")

        except Exception as e:
            logger.error(f"模型載入失敗: {str(e)}")
            raise

    def generate_json(
        self,
        prompt: str,
        schema: type[BaseModel]
    ) -> BaseModel:
        """
        生成符合 Schema 的 JSON

        Args:
            prompt: 輸入提示
            schema: Pydantic 模型類

        Returns:
            模型實例
        """
        try:
            logger.info(f"生成 JSON,模型: {schema.__name__}")

            # 創建 JSON 生成器
            generator = generate.json(self.model, schema)

            # 生成結果
            result = generator(prompt)

            logger.info(f"生成成功: {schema.__name__}")
            return result

        except Exception as e:
            logger.error(f"JSON 生成失敗: {str(e)}")
            raise

    def batch_generate(
        self,
        prompts: List[str],
        schema: type[BaseModel]
    ) -> List[BaseModel]:
        """
        批量生成 JSON

        Args:
            prompts: 提示列表
            schema: Pydantic 模型類

        Returns:
            模型實例列表
        """
        results = []

        for prompt in prompts:
            result = self.generate_json(prompt, schema)
            results.append(result)

        return results


# ==================== 用戶數據生成器 ====================

class UserDataGenerator:
    """
    用戶數據生成器

    生成用戶相關的結構化數據
    """

    def __init__(self, manager: JSONSchemaManager):
        """
        初始化用戶數據生成器

        Args:
            manager: JSON Schema 管理器
        """
        self.manager = manager
        logger.info("用戶數據生成器初始化完成")

    def generate_user(
        self,
        description: str = "普通用戶"
    ) -> User:
        """
        生成用戶數據

        Args:
            description: 用戶描述

        Returns:
            用戶對象
        """
        prompt = f"生成一個{description}的用戶信息"
        user = self.manager.generate_json(prompt, User)

        logger.info(f"生成用戶: {user.username}")
        return user

    def generate_admin_user(self) -> User:
        """
        生成管理員用戶

        Returns:
            管理員用戶對象
        """
        prompt = "生成一個管理員用戶的完整信息"
        user = self.manager.generate_json(prompt, User)

        return user

    def generate_contact_info(
        self,
        context: str = "用戶"
    ) -> ContactInfo:
        """
        生成聯繫信息

        Args:
            context: 上下文描述

        Returns:
            聯繫信息對象
        """
        prompt = f"生成{context}的完整聯繫信息"
        contact = self.manager.generate_json(prompt, ContactInfo)

        return contact

    def generate_batch_users(
        self,
        count: int,
        role: Optional[UserRole] = None
    ) -> List[User]:
        """
        批量生成用戶

        Args:
            count: 生成數量
            role: 用戶角色(可選)

        Returns:
            用戶列表
        """
        users = []

        for i in range(count):
            if role:
                prompt = f"生成第{i+1}個{role.value}用戶"
            else:
                prompt = f"生成第{i+1}個用戶"

            user = self.manager.generate_json(prompt, User)
            users.append(user)

        logger.info(f"批量生成{count}個用戶完成")
        return users


# ==================== 電商數據生成器 ====================

class EcommerceDataGenerator:
    """
    電商數據生成器

    生成電商相關的結構化數據
    """

    def __init__(self, manager: JSONSchemaManager):
        """
        初始化電商數據生成器

        Args:
            manager: JSON Schema 管理器
        """
        self.manager = manager
        logger.info("電商數據生成器初始化完成")

    def generate_product(
        self,
        category: str = "電子產品"
    ) -> Product:
        """
        生成產品數據

        Args:
            category: 產品類別

        Returns:
            產品對象
        """
        prompt = f"生成一個{category}類別的產品信息"
        product = self.manager.generate_json(prompt, Product)

        logger.info(f"生成產品: {product.name}")
        return product

    def generate_order(
        self,
        user_context: str = "普通用戶"
    ) -> Order:
        """
        生成訂單數據

        Args:
            user_context: 用戶上下文

        Returns:
            訂單對象
        """
        prompt = f"為{user_context}生成一個完整的訂單信息"
        order = self.manager.generate_json(prompt, Order)

        logger.info(f"生成訂單: {order.order_id}")
        return order

    def generate_review(
        self,
        product_name: str,
        sentiment: str = "正面"
    ) -> Review:
        """
        生成產品評價

        Args:
            product_name: 產品名稱
            sentiment: 情感傾向

        Returns:
            評價對象
        """
        prompt = f"為{product_name}生成一個{sentiment}的產品評價"
        review = self.manager.generate_json(prompt, Review)

        logger.info(f"生成評價,評分: {review.rating}/5")
        return review

    def generate_catalog(
        self,
        category: str,
        count: int = 5
    ) -> List[Product]:
        """
        生成產品目錄

        Args:
            category: 產品類別
            count: 產品數量

        Returns:
            產品列表
        """
        products = []

        for i in range(count):
            prompt = f"生成{category}類別的第{i+1}個產品"
            product = self.manager.generate_json(prompt, Product)
            products.append(product)

        logger.info(f"生成{category}目錄,共{count}個產品")
        return products


# ==================== 內容數據生成器 ====================

class ContentDataGenerator:
    """
    內容數據生成器

    生成博客、評論等內容數據
    """

    def __init__(self, manager: JSONSchemaManager):
        """
        初始化內容數據生成器

        Args:
            manager: JSON Schema 管理器
        """
        self.manager = manager
        logger.info("內容數據生成器初始化完成")

    def generate_blog_post(
        self,
        topic: str,
        author: str = "匿名作者"
    ) -> BlogPost:
        """
        生成博客文章

        Args:
            topic: 文章主題
            author: 作者名稱

        Returns:
            博客文章對象
        """
        prompt = f"為{author}生成一篇關於{topic}的博客文章"
        post = self.manager.generate_json(prompt, BlogPost)

        logger.info(f"生成文章: {post.title}")
        return post

    def generate_comment(
        self,
        context: str,
        sentiment: str = "正面"
    ) -> Comment:
        """
        生成評論

        Args:
            context: 評論上下文
            sentiment: 情感傾向

        Returns:
            評論對象
        """
        prompt = f"為{context}生成一條{sentiment}的評論"
        comment = self.manager.generate_json(prompt, Comment)

        return comment

    def generate_blog_series(
        self,
        series_topic: str,
        count: int = 3
    ) -> List[BlogPost]:
        """
        生成系列博客文章

        Args:
            series_topic: 系列主題
            count: 文章數量

        Returns:
            博客文章列表
        """
        posts = []

        for i in range(count):
            prompt = f"生成{series_topic}系列的第{i+1}篇文章"
            post = self.manager.generate_json(prompt, BlogPost)
            posts.append(post)

        logger.info(f"生成{series_topic}系列,共{count}篇文章")
        return posts


# ==================== API 數據生成器 ====================

class APIDataGenerator:
    """
    API 數據生成器

    生成 API 響應等數據
    """

    def __init__(self, manager: JSONSchemaManager):
        """
        初始化 API 數據生成器

        Args:
            manager: JSON Schema 管理器
        """
        self.manager = manager
        logger.info("API 數據生成器初始化完成")

    def generate_success_response(
        self,
        operation: str,
        data: Optional[Dict[str, Any]] = None
    ) -> APIResponse:
        """
        生成成功響應

        Args:
            operation: 操作描述
            data: 響應數據

        Returns:
            API 響應對象
        """
        prompt = f"生成{operation}操作的成功響應"
        response = self.manager.generate_json(prompt, APIResponse)

        return response

    def generate_error_response(
        self,
        error_type: str
    ) -> APIResponse:
        """
        生成錯誤響應

        Args:
            error_type: 錯誤類型

        Returns:
            API 響應對象
        """
        prompt = f"生成{error_type}錯誤的API響應"
        response = self.manager.generate_json(prompt, APIResponse)

        return response


# ==================== 數據驗證器 ====================

class SchemaValidator:
    """
    Schema 驗證器

    驗證生成的數據是否符合 Schema
    """

    @staticmethod
    def validate(instance: BaseModel) -> tuple[bool, Optional[str]]:
        """
        驗證模型實例

        Args:
            instance: 模型實例

        Returns:
            (是否有效, 錯誤信息) 元組
        """
        try:
            # Pydantic 會在創建時自動驗證
            instance.dict()
            return True, None

        except Exception as e:
            return False, str(e)

    @staticmethod
    def print_validation_result(
        instance: BaseModel,
        name: str = "對象"
    ):
        """
        打印驗證結果

        Args:
            instance: 模型實例
            name: 對象名稱
        """
        is_valid, error = SchemaValidator.validate(instance)

        if is_valid:
            print(f"✓ {name}驗證通過")
        else:
            print(f"✗ {name}驗證失敗: {error}")


# ==================== 示例運行器 ====================

def run_user_generation_example():
    """運行用戶數據生成示例"""
    print("\n" + "="*60)
    print("示例 1: 用戶數據生成")
    print("="*60)

    manager = JSONSchemaManager()
    generator = UserDataGenerator(manager)

    # 生成單個用戶
    print("\n生成普通用戶:")
    user = generator.generate_user("年輕的軟件工程師")
    print(f"  用戶名: {user.username}")
    print(f"  郵箱: {user.email}")
    print(f"  年齡: {user.age}")
    print(f"  性別: {user.gender.value}")
    print(f"  角色: {user.role.value}")

    # 生成管理員
    print("\n生成管理員用戶:")
    admin = generator.generate_admin_user()
    print(f"  用戶名: {admin.username}")
    print(f"  角色: {admin.role.value}")

    # 生成聯繫信息
    print("\n生成聯繫信息:")
    contact = generator.generate_contact_info()
    print(f"  郵箱: {contact.email}")
    print(f"  電話: {contact.phone}")
    print(f"  城市: {contact.address.city}")


def run_ecommerce_generation_example():
    """運行電商數據生成示例"""
    print("\n" + "="*60)
    print("示例 2: 電商數據生成")
    print("="*60)

    manager = JSONSchemaManager()
    generator = EcommerceDataGenerator(manager)

    # 生成產品
    print("\n生成產品:")
    product = generator.generate_product("智能手機")
    print(f"  名稱: {product.name}")
    print(f"  價格: ${product.price}")
    print(f"  庫存: {product.quantity}")
    print(f"  標籤: {', '.join(product.tags)}")

    # 生成訂單
    print("\n生成訂單:")
    order = generator.generate_order()
    print(f"  訂單號: {order.order_id}")
    print(f"  項目數: {len(order.items)}")
    print(f"  總金額: ${order.total_amount}")
    print(f"  狀態: {order.status}")

    # 生成評價
    print("\n生成產品評價:")
    review = generator.generate_review("iPhone 15", "正面")
    print(f"  標題: {review.title}")
    print(f"  評分: {review.rating}/5")
    print(f"  內容: {review.content[:100]}...")


def run_content_generation_example():
    """運行內容數據生成示例"""
    print("\n" + "="*60)
    print("示例 3: 內容數據生成")
    print("="*60)

    manager = JSONSchemaManager()
    generator = ContentDataGenerator(manager)

    # 生成博客文章
    print("\n生成博客文章:")
    post = generator.generate_blog_post("人工智能的未來", "AI專家")
    print(f"  標題: {post.title}")
    print(f"  作者: {post.author}")
    print(f"  標籤: {', '.join(post.tags)}")
    print(f"  瀏覽數: {post.views}")
    print(f"  內容預覽: {post.content[:100]}...")

    # 生成評論
    print("\n生成評論:")
    comment = generator.generate_comment("技術文章", "正面")
    print(f"  內容: {comment.content}")
    if comment.rating:
        print(f"  評分: {comment.rating}/5")


def run_api_generation_example():
    """運行 API 數據生成示例"""
    print("\n" + "="*60)
    print("示例 4: API 響應生成")
    print("="*60)

    manager = JSONSchemaManager()
    generator = APIDataGenerator(manager)

    # 生成成功響應
    print("\n生成成功響應:")
    success = generator.generate_success_response("用戶創建")
    print(f"  狀態: {success.status}")
    print(f"  代碼: {success.code}")
    print(f"  消息: {success.message}")

    # 生成錯誤響應
    print("\n生成錯誤響應:")
    error = generator.generate_error_response("驗證失敗")
    print(f"  狀態: {error.status}")
    print(f"  代碼: {error.code}")
    print(f"  消息: {error.message}")


def main():
    """主函數"""
    try:
        print("\n開始運行 JSON Schema 生成示例...")

        run_user_generation_example()
        run_ecommerce_generation_example()
        run_content_generation_example()
        run_api_generation_example()

        print("\n" + "="*60)
        print("所有示例運行完成!")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\n用戶中斷執行")
    except Exception as e:
        print(f"\n錯誤: {str(e)}")
        logger.error(f"主程序錯誤: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
