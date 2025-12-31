"""
Outlines Pydantic 模型整合示例
===============================

本示例展示如何使用 Outlines 與 Pydantic 模型深度整合。

主要內容:
1. Pydantic 模型定義
2. 自定義驗證器
3. 嵌套模型生成
4. 模型繼承
5. 複雜數據結構

作者: Outlines 教學團隊
日期: 2025-01
"""

import outlines
from outlines import models, generate
import torch
from typing import List, Dict, Optional, Any, Union, Literal
from pydantic import (
    BaseModel, Field, validator, root_validator,
    EmailStr, HttpUrl, constr, conint, confloat
)
from datetime import datetime, date, time
from decimal import Decimal
from enum import Enum
import logging
import json
import sys
from uuid import uuid4

# ==================== 設置日誌 ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== 枚舉定義 ====================

class TaskPriority(str, Enum):
    """任務優先級"""
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"
    URGENT = "緊急"


class TaskStatus(str, Enum):
    """任務狀態"""
    TODO = "待辦"
    IN_PROGRESS = "進行中"
    REVIEW = "審核中"
    DONE = "完成"
    CANCELLED = "取消"


class PaymentMethod(str, Enum):
    """支付方式"""
    CREDIT_CARD = "信用卡"
    DEBIT_CARD = "借記卡"
    PAYPAL = "PayPal"
    BANK_TRANSFER = "銀行轉賬"
    CASH = "現金"


class OrderStatus(str, Enum):
    """訂單狀態"""
    PENDING = "待處理"
    CONFIRMED = "已確認"
    SHIPPED = "已發貨"
    DELIVERED = "已送達"
    CANCELLED = "已取消"
    REFUNDED = "已退款"


# ==================== 基礎模型 ====================

class BaseEntity(BaseModel):
    """基礎實體模型"""
    id: int = Field(description="ID", ge=1)
    created_at: str = Field(description="創建時間")
    updated_at: Optional[str] = Field(None, description="更新時間")

    class Config:
        """Pydantic 配置"""
        use_enum_values = True
        validate_assignment = True


class TimestampMixin(BaseModel):
    """時間戳混入"""
    created_at: str = Field(description="創建時間")
    updated_at: Optional[str] = Field(None, description="更新時間")


# ==================== 用戶相關模型 ====================

class UserProfile(BaseModel):
    """用戶檔案"""
    bio: Optional[str] = Field(None, description="個人簡介", max_length=500)
    avatar_url: Optional[str] = Field(None, description="頭像URL")
    website: Optional[str] = Field(None, description="個人網站")
    location: Optional[str] = Field(None, description="所在地")
    birth_date: Optional[str] = Field(None, description="生日")


class UserPreferences(BaseModel):
    """用戶偏好設置"""
    language: str = Field(default="zh-TW", description="語言")
    timezone: str = Field(default="Asia/Taipei", description="時區")
    notifications_enabled: bool = Field(default=True, description="啟用通知")
    email_notifications: bool = Field(default=True, description="郵件通知")
    theme: str = Field(default="light", description="主題")


class AdvancedUser(BaseEntity):
    """高級用戶模型"""
    username: constr(min_length=3, max_length=20) = Field(description="用戶名")
    email: EmailStr = Field(description="郵箱")
    full_name: str = Field(description="全名")
    age: conint(ge=0, le=120) = Field(description="年齡")
    profile: Optional[UserProfile] = Field(None, description="用戶檔案")
    preferences: UserPreferences = Field(
        default_factory=UserPreferences,
        description="偏好設置"
    )
    is_verified: bool = Field(default=False, description="是否已驗證")
    is_premium: bool = Field(default=False, description="是否為高級用戶")

    @validator('username')
    def validate_username(cls, v):
        """驗證用戶名"""
        if not v.isalnum():
            raise ValueError('用戶名只能包含字母和數字')
        return v

    @validator('age')
    def validate_age(cls, v):
        """驗證年齡"""
        if v < 18:
            logger.warning(f'用戶年齡未成年: {v}')
        return v


# ==================== 任務管理模型 ====================

class TaskLabel(BaseModel):
    """任務標籤"""
    name: str = Field(description="標籤名稱")
    color: str = Field(description="顏色代碼")


class TaskComment(BaseModel):
    """任務評論"""
    user_id: int = Field(description="用戶ID")
    content: str = Field(description="評論內容", min_length=1)
    created_at: str = Field(description="創建時間")


class TaskAttachment(BaseModel):
    """任務附件"""
    filename: str = Field(description="文件名")
    file_url: str = Field(description="文件URL")
    file_size: int = Field(description="文件大小(字節)", ge=0)
    uploaded_at: str = Field(description="上傳時間")


class Task(BaseEntity):
    """任務模型"""
    title: str = Field(description="任務標題", min_length=1, max_length=200)
    description: str = Field(description="任務描述")
    priority: TaskPriority = Field(description="優先級")
    status: TaskStatus = Field(default=TaskStatus.TODO, description="狀態")
    assignee_id: Optional[int] = Field(None, description="負責人ID")
    due_date: Optional[str] = Field(None, description="截止日期")
    estimated_hours: Optional[float] = Field(None, description="預計工時", ge=0)
    actual_hours: Optional[float] = Field(None, description="實際工時", ge=0)
    labels: List[TaskLabel] = Field(default_factory=list, description="標籤")
    comments: List[TaskComment] = Field(default_factory=list, description="評論")
    attachments: List[TaskAttachment] = Field(default_factory=list, description="附件")
    progress: confloat(ge=0, le=100) = Field(default=0, description="進度百分比")

    @root_validator
    def validate_task(cls, values):
        """任務整體驗證"""
        status = values.get('status')
        progress = values.get('progress')

        # 如果任務完成,進度應該是 100%
        if status == TaskStatus.DONE and progress < 100:
            logger.warning('已完成任務進度不是 100%')

        return values


# ==================== 電商模型 ====================

class ProductImage(BaseModel):
    """產品圖片"""
    url: str = Field(description="圖片URL")
    is_primary: bool = Field(default=False, description="是否為主圖")
    alt_text: Optional[str] = Field(None, description="替代文字")


class ProductVariant(BaseModel):
    """產品變體"""
    sku: str = Field(description="SKU")
    name: str = Field(description="變體名稱")
    price: Decimal = Field(description="價格", gt=0)
    stock: int = Field(description="庫存", ge=0)
    attributes: Dict[str, str] = Field(description="屬性")


class AdvancedProduct(BaseEntity):
    """高級產品模型"""
    name: str = Field(description="產品名稱", min_length=1, max_length=200)
    slug: str = Field(description="URL別名")
    description: str = Field(description="產品描述")
    short_description: Optional[str] = Field(None, description="簡短描述", max_length=200)
    base_price: Decimal = Field(description="基礎價格", gt=0)
    sale_price: Optional[Decimal] = Field(None, description="促銷價格", gt=0)
    currency: str = Field(default="USD", description="貨幣")
    sku: str = Field(description="SKU")
    barcode: Optional[str] = Field(None, description="條碼")
    category_id: int = Field(description="類別ID")
    brand: Optional[str] = Field(None, description="品牌")
    tags: List[str] = Field(default_factory=list, description="標籤")
    images: List[ProductImage] = Field(default_factory=list, description="圖片")
    variants: List[ProductVariant] = Field(default_factory=list, description="變體")
    is_featured: bool = Field(default=False, description="是否精選")
    is_available: bool = Field(default=True, description="是否可用")
    stock_quantity: int = Field(description="總庫存", ge=0)
    weight: Optional[float] = Field(None, description="重量(公斤)", gt=0)
    dimensions: Optional[Dict[str, float]] = Field(None, description="尺寸")

    @validator('sale_price')
    def validate_sale_price(cls, v, values):
        """驗證促銷價格"""
        if v is not None:
            base_price = values.get('base_price')
            if base_price and v >= base_price:
                raise ValueError('促銷價格必須低於基礎價格')
        return v

    @validator('slug')
    def validate_slug(cls, v):
        """驗證 URL 別名"""
        if not v.replace('-', '').isalnum():
            raise ValueError('URL別名只能包含字母、數字和連字符')
        return v.lower()


class PaymentInfo(BaseModel):
    """支付信息"""
    method: PaymentMethod = Field(description="支付方式")
    transaction_id: str = Field(description="交易ID")
    amount: Decimal = Field(description="金額", gt=0)
    currency: str = Field(default="USD", description="貨幣")
    status: str = Field(description="支付狀態")
    paid_at: Optional[str] = Field(None, description="支付時間")


class ShippingInfo(BaseModel):
    """配送信息"""
    recipient_name: str = Field(description="收件人姓名")
    phone: str = Field(description="聯繫電話")
    address_line1: str = Field(description="地址行1")
    address_line2: Optional[str] = Field(None, description="地址行2")
    city: str = Field(description="城市")
    state: Optional[str] = Field(None, description="州/省")
    postal_code: str = Field(description="郵政編碼")
    country: str = Field(description="國家")
    shipping_method: str = Field(description="配送方式")
    tracking_number: Optional[str] = Field(None, description="追踪號碼")


class OrderItem(BaseModel):
    """訂單項目"""
    product_id: int = Field(description="產品ID")
    product_name: str = Field(description="產品名稱")
    sku: str = Field(description="SKU")
    quantity: int = Field(description="數量", ge=1)
    unit_price: Decimal = Field(description="單價", gt=0)
    subtotal: Decimal = Field(description="小計", gt=0)
    discount: Decimal = Field(default=Decimal(0), description="折扣", ge=0)
    tax: Decimal = Field(default=Decimal(0), description="稅", ge=0)
    total: Decimal = Field(description="總計", gt=0)

    @root_validator
    def calculate_total(cls, values):
        """計算總計"""
        quantity = values.get('quantity', 0)
        unit_price = values.get('unit_price', Decimal(0))
        discount = values.get('discount', Decimal(0))
        tax = values.get('tax', Decimal(0))

        subtotal = Decimal(quantity) * unit_price
        total = subtotal - discount + tax

        values['subtotal'] = subtotal
        values['total'] = total

        return values


class AdvancedOrder(BaseEntity):
    """高級訂單模型"""
    order_number: str = Field(description="訂單號")
    user_id: int = Field(description="用戶ID")
    items: List[OrderItem] = Field(description="訂單項目")
    subtotal: Decimal = Field(description="小計", gt=0)
    discount_total: Decimal = Field(default=Decimal(0), description="折扣總計", ge=0)
    tax_total: Decimal = Field(default=Decimal(0), description="稅總計", ge=0)
    shipping_cost: Decimal = Field(default=Decimal(0), description="運費", ge=0)
    total: Decimal = Field(description="總計", gt=0)
    currency: str = Field(default="USD", description="貨幣")
    status: OrderStatus = Field(description="訂單狀態")
    payment_info: PaymentInfo = Field(description="支付信息")
    shipping_info: ShippingInfo = Field(description="配送信息")
    notes: Optional[str] = Field(None, description="備註")

    @root_validator
    def validate_order(cls, values):
        """訂單整體驗證"""
        items = values.get('items', [])
        if not items:
            raise ValueError('訂單必須至少包含一個項目')

        # 驗證總計
        subtotal = sum(item.subtotal for item in items)
        discount_total = values.get('discount_total', Decimal(0))
        tax_total = values.get('tax_total', Decimal(0))
        shipping_cost = values.get('shipping_cost', Decimal(0))

        expected_total = subtotal - discount_total + tax_total + shipping_cost
        actual_total = values.get('total', Decimal(0))

        if abs(expected_total - actual_total) > Decimal('0.01'):
            logger.warning(f'訂單總計不匹配: 期望 {expected_total}, 實際 {actual_total}')

        return values


# ==================== Pydantic 生成管理器 ====================

class PydanticGenerationManager:
    """
    Pydantic 生成管理器

    管理基於 Pydantic 模型的生成
    """

    def __init__(self, model_name: str = "mistralai/Mistral-7B-v0.1"):
        """
        初始化管理器

        Args:
            model_name: 模型名稱
        """
        self.model_name = model_name
        self.model = None
        self.load_model()

        logger.info(f"Pydantic 生成管理器初始化完成")

    def load_model(self):
        """載入模型"""
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = models.transformers(self.model_name, device=device)
            logger.info("模型載入完成")
        except Exception as e:
            logger.error(f"模型載入失敗: {str(e)}")
            raise

    def generate(
        self,
        prompt: str,
        schema: type[BaseModel]
    ) -> BaseModel:
        """
        生成 Pydantic 模型實例

        Args:
            prompt: 提示
            schema: Pydantic 模型

        Returns:
            模型實例
        """
        try:
            generator = generate.json(self.model, schema)
            result = generator(prompt)
            logger.info(f"生成成功: {schema.__name__}")
            return result
        except Exception as e:
            logger.error(f"生成失敗: {str(e)}")
            raise


# ==================== 示例運行器 ====================

def run_user_model_example():
    """運行用戶模型示例"""
    print("\n" + "="*60)
    print("示例 1: 高級用戶模型")
    print("="*60)

    manager = PydanticGenerationManager()

    # 生成用戶
    print("\n生成用戶:")
    user = manager.generate("生成一個高級用戶的完整信息", AdvancedUser)
    print(f"  用戶名: {user.username}")
    print(f"  郵箱: {user.email}")
    print(f"  全名: {user.full_name}")
    print(f"  年齡: {user.age}")
    print(f"  已驗證: {user.is_verified}")
    print(f"  高級用戶: {user.is_premium}")

    if user.profile:
        print(f"  簡介: {user.profile.bio}")
        print(f"  位置: {user.profile.location}")

    print(f"  語言: {user.preferences.language}")
    print(f"  主題: {user.preferences.theme}")


def run_task_model_example():
    """運行任務模型示例"""
    print("\n" + "="*60)
    print("示例 2: 任務管理模型")
    print("="*60)

    manager = PydanticGenerationManager()

    # 生成任務
    print("\n生成任務:")
    task = manager.generate("生成一個緊急的軟件開發任務", Task)
    print(f"  標題: {task.title}")
    print(f"  優先級: {task.priority.value}")
    print(f"  狀態: {task.status.value}")
    print(f"  進度: {task.progress}%")
    print(f"  描述: {task.description[:100]}...")

    if task.labels:
        print(f"  標籤: {', '.join(label.name for label in task.labels)}")

    if task.estimated_hours:
        print(f"  預計工時: {task.estimated_hours}小時")


def run_product_model_example():
    """運行產品模型示例"""
    print("\n" + "="*60)
    print("示例 3: 高級產品模型")
    print("="*60)

    manager = PydanticGenerationManager()

    # 生成產品
    print("\n生成產品:")
    product = manager.generate("生成一個高端智能手機產品", AdvancedProduct)
    print(f"  名稱: {product.name}")
    print(f"  SKU: {product.sku}")
    print(f"  基礎價格: ${product.base_price}")

    if product.sale_price:
        print(f"  促銷價格: ${product.sale_price}")

    print(f"  品牌: {product.brand}")
    print(f"  庫存: {product.stock_quantity}")
    print(f"  精選: {product.is_featured}")
    print(f"  標籤: {', '.join(product.tags)}")

    if product.variants:
        print(f"  變體數量: {len(product.variants)}")


def run_order_model_example():
    """運行訂單模型示例"""
    print("\n" + "="*60)
    print("示例 4: 高級訂單模型")
    print("="*60)

    manager = PydanticGenerationManager()

    # 生成訂單
    print("\n生成訂單:")
    order = manager.generate("生成一個包含多個商品的完整訂單", AdvancedOrder)
    print(f"  訂單號: {order.order_number}")
    print(f"  項目數量: {len(order.items)}")
    print(f"  小計: ${order.subtotal}")
    print(f"  折扣: ${order.discount_total}")
    print(f"  稅: ${order.tax_total}")
    print(f"  運費: ${order.shipping_cost}")
    print(f"  總計: ${order.total}")
    print(f"  狀態: {order.status.value}")
    print(f"  支付方式: {order.payment_info.method.value}")
    print(f"  收件人: {order.shipping_info.recipient_name}")
    print(f"  配送地址: {order.shipping_info.city}, {order.shipping_info.country}")


def main():
    """主函數"""
    try:
        print("\n開始運行 Pydantic 模型示例...")

        run_user_model_example()
        run_task_model_example()
        run_product_model_example()
        run_order_model_example()

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
