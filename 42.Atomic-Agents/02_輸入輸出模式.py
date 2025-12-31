"""
Atomic Agents 輸入輸出模式設計
==============================

本文件深入探討如何使用 Pydantic 定義清晰的輸入輸出模式 (Schema)。
Schema 是 Atomic Agents 的核心，確保類型安全和自動驗證。

主要內容：
1. Pydantic 基礎模型
2. 複雜數據結構設計
3. 自定義驗證器
4. 嵌套模型
5. 動態模型生成
6. 最佳實踐

作者：Atomic Agents 團隊
日期：2025-12-31
"""

from pydantic import (
    BaseModel,
    Field,
    validator,
    root_validator,
    EmailStr,
    HttpUrl,
    constr,
    conint,
    confloat
)
from typing import Optional, List, Dict, Any, Union, Literal
from datetime import datetime, date
from enum import Enum
from uuid import UUID, uuid4
from decimal import Decimal


# ============================================================================
# 第一部分：基礎 Schema 設計
# ============================================================================

class Priority(str, Enum):
    """優先級枚舉"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    """任務狀態枚舉"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SimpleTask(BaseModel):
    """
    簡單任務模型

    展示基本的 Schema 設計原則。
    """
    id: UUID = Field(
        default_factory=uuid4,
        description="任務唯一標識符"
    )
    title: constr(min_length=1, max_length=200) = Field(
        ...,
        description="任務標題",
        example="完成專案文檔"
    )
    description: Optional[str] = Field(
        None,
        description="任務詳細描述",
        max_length=2000
    )
    priority: Priority = Field(
        default=Priority.MEDIUM,
        description="任務優先級"
    )
    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        description="任務當前狀態"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="創建時間"
    )
    due_date: Optional[date] = Field(
        None,
        description="截止日期"
    )

    class Config:
        """Pydantic 配置"""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
        }

    @validator('due_date')
    def validate_due_date(cls, v, values):
        """驗證截止日期不能早於創建日期"""
        if v and 'created_at' in values:
            created_date = values['created_at'].date()
            if v < created_date:
                raise ValueError('截止日期不能早於創建日期')
        return v


# ============================================================================
# 第二部分：複雜嵌套模型
# ============================================================================

class Address(BaseModel):
    """地址模型"""
    street: str = Field(..., description="街道地址")
    city: str = Field(..., description="城市")
    state: str = Field(..., description="省/州")
    postal_code: str = Field(..., description="郵政編碼")
    country: str = Field(default="Taiwan", description="國家")

    @validator('postal_code')
    def validate_postal_code(cls, v):
        """驗證郵政編碼格式（台灣格式）"""
        if not v.isdigit() or len(v) not in [3, 5]:
            raise ValueError('郵政編碼格式不正確')
        return v


class ContactInfo(BaseModel):
    """聯絡信息模型"""
    email: EmailStr = Field(..., description="電子郵件")
    phone: constr(regex=r'^\+?[0-9\-\s()]+$') = Field(
        ...,
        description="電話號碼"
    )
    website: Optional[HttpUrl] = Field(None, description="網站")
    address: Optional[Address] = Field(None, description="地址")


class User(BaseModel):
    """
    用戶模型

    展示嵌套模型和複雜驗證。
    """
    id: UUID = Field(default_factory=uuid4)
    username: constr(min_length=3, max_length=50, regex=r'^[a-zA-Z0-9_]+$') = Field(
        ...,
        description="用戶名（只能包含字母、數字和下劃線）"
    )
    full_name: str = Field(..., description="全名")
    age: conint(ge=0, le=150) = Field(..., description="年齡")
    contact: ContactInfo = Field(..., description="聯絡信息")
    is_active: bool = Field(default=True, description="是否啟用")
    tags: List[str] = Field(default_factory=list, description="用戶標籤")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="額外元數據")

    @validator('full_name')
    def validate_full_name(cls, v):
        """驗證全名不為空且格式正確"""
        if not v.strip():
            raise ValueError('全名不能為空')
        if len(v.strip()) < 2:
            raise ValueError('全名至少需要 2 個字符')
        return v.strip()

    @root_validator
    def validate_user(cls, values):
        """根級驗證器：驗證整個用戶對象"""
        # 確保用戶名和郵箱不相同
        username = values.get('username')
        contact = values.get('contact')
        if contact and username and username in contact.email:
            raise ValueError('用戶名不應該包含在郵箱中')
        return values


# ============================================================================
# 第三部分：Agent 專用 Schema
# ============================================================================

class MessageRole(str, Enum):
    """消息角色"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class Message(BaseModel):
    """聊天消息模型"""
    role: MessageRole = Field(..., description="消息角色")
    content: str = Field(..., description="消息內容")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = Field(default=None)


class ConversationContext(BaseModel):
    """
    對話上下文模型

    用於管理多輪對話的上下文信息。
    """
    conversation_id: UUID = Field(default_factory=uuid4)
    messages: List[Message] = Field(
        default_factory=list,
        description="對話歷史"
    )
    user_id: Optional[str] = Field(None, description="用戶 ID")
    session_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="會話數據"
    )
    max_history: int = Field(
        default=10,
        description="最大保留的歷史消息數",
        ge=1,
        le=100
    )

    def add_message(self, role: MessageRole, content: str) -> None:
        """添加消息到上下文"""
        message = Message(role=role, content=content)
        self.messages.append(message)

        # 限制歷史長度
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]

    def get_context_string(self) -> str:
        """獲取格式化的上下文字符串"""
        context_parts = []
        for msg in self.messages:
            context_parts.append(f"{msg.role.value}: {msg.content}")
        return "\n".join(context_parts)


class AgentInput(BaseModel):
    """
    通用 Agent 輸入模型

    可用於各種 Agent 的標準輸入格式。
    """
    query: str = Field(..., description="用戶查詢或指令")
    context: Optional[ConversationContext] = Field(
        None,
        description="對話上下文"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="額外參數"
    )
    max_tokens: conint(ge=50, le=4000) = Field(
        default=1000,
        description="最大 token 數"
    )
    temperature: confloat(ge=0.0, le=2.0) = Field(
        default=0.7,
        description="生成溫度"
    )
    stream: bool = Field(
        default=False,
        description="是否使用流式輸出"
    )


class AgentOutput(BaseModel):
    """
    通用 Agent 輸出模型

    標準化的 Agent 響應格式。
    """
    response: str = Field(..., description="Agent 回應")
    confidence: confloat(ge=0.0, le=1.0) = Field(
        ...,
        description="信心分數"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="響應元數據"
    )
    tokens_used: Optional[int] = Field(None, description="使用的 token 數")
    processing_time: Optional[float] = Field(None, description="處理時間（秒）")
    model: str = Field(default="gpt-4", description="使用的模型")
    timestamp: datetime = Field(default_factory=datetime.now)


# ============================================================================
# 第四部分：特定領域模型
# ============================================================================

class DocumentType(str, Enum):
    """文檔類型"""
    PDF = "pdf"
    WORD = "word"
    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"


class Document(BaseModel):
    """文檔模型"""
    id: UUID = Field(default_factory=uuid4)
    title: str = Field(..., description="文檔標題")
    content: str = Field(..., description="文檔內容")
    doc_type: DocumentType = Field(..., description="文檔類型")
    author: Optional[str] = Field(None, description="作者")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)
    word_count: Optional[int] = Field(None, description="字數")

    @root_validator
    def calculate_word_count(cls, values):
        """自動計算字數"""
        content = values.get('content', '')
        if content:
            values['word_count'] = len(content.split())
        return values


class AnalysisInput(BaseModel):
    """文檔分析輸入"""
    document: Document = Field(..., description="要分析的文檔")
    analysis_type: List[str] = Field(
        ...,
        description="分析類型（如：sentiment, summary, keywords）"
    )
    language: str = Field(default="zh-TW", description="文檔語言")
    detailed: bool = Field(default=False, description="是否需要詳細分析")


class AnalysisOutput(BaseModel):
    """文檔分析輸出"""
    document_id: UUID = Field(..., description="文檔 ID")
    summary: Optional[str] = Field(None, description="摘要")
    sentiment: Optional[Dict[str, float]] = Field(
        None,
        description="情感分析結果"
    )
    keywords: Optional[List[str]] = Field(None, description="關鍵詞")
    topics: Optional[List[str]] = Field(None, description="主題")
    insights: List[str] = Field(default_factory=list, description="洞察")
    confidence: float = Field(..., description="整體信心分數")


# ============================================================================
# 第五部分：動態模型和工廠模式
# ============================================================================

class ModelFactory:
    """模型工廠類"""

    @staticmethod
    def create_simple_input(field_name: str, field_type: type) -> type:
        """
        動態創建簡單輸入模型

        Args:
            field_name: 字段名稱
            field_type: 字段類型

        Returns:
            動態創建的 Pydantic 模型
        """
        return type(
            'DynamicInput',
            (BaseModel,),
            {
                field_name: (field_type, Field(..., description=f"動態字段: {field_name}"))
            }
        )

    @staticmethod
    def create_response_model(fields: Dict[str, tuple]) -> type:
        """
        創建響應模型

        Args:
            fields: 字段定義字典 {name: (type, description)}

        Returns:
            動態模型類
        """
        model_fields = {}
        for name, (field_type, description) in fields.items():
            model_fields[name] = (field_type, Field(..., description=description))

        return type('DynamicResponse', (BaseModel,), model_fields)


# ============================================================================
# 第六部分：Schema 組合和繼承
# ============================================================================

class BaseEntity(BaseModel):
    """基礎實體模型"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        """配置"""
        validate_assignment = True


class NamedEntity(BaseEntity):
    """命名實體"""
    name: str = Field(..., description="名稱", min_length=1)
    description: Optional[str] = Field(None, description="描述")


class Product(NamedEntity):
    """產品模型（繼承自 NamedEntity）"""
    price: Decimal = Field(..., description="價格", gt=0)
    stock: conint(ge=0) = Field(..., description="庫存")
    category: str = Field(..., description="類別")
    is_available: bool = Field(default=True, description="是否可用")

    @validator('price')
    def validate_price(cls, v):
        """驗證價格精度"""
        if v.as_tuple().exponent < -2:
            raise ValueError('價格最多保留兩位小數')
        return v


class Order(BaseEntity):
    """訂單模型"""
    customer_id: UUID = Field(..., description="客戶 ID")
    products: List[Product] = Field(..., description="產品列表")
    total_amount: Decimal = Field(..., description="總金額")
    status: str = Field(default="pending", description="訂單狀態")

    @root_validator
    def calculate_total(cls, values):
        """自動計算總金額"""
        products = values.get('products', [])
        total = sum(p.price for p in products)
        values['total_amount'] = total
        return values


# ============================================================================
# 第七部分：Schema 驗證和測試工具
# ============================================================================

def validate_schema(model_class: type, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    驗證數據是否符合 Schema

    Args:
        model_class: Pydantic 模型類
        data: 要驗證的數據

    Returns:
        (是否有效, 錯誤消息)
    """
    try:
        model_class(**data)
        return True, None
    except Exception as e:
        return False, str(e)


def generate_example_data(model_class: type) -> Dict[str, Any]:
    """
    為模型生成示例數據

    Args:
        model_class: Pydantic 模型類

    Returns:
        示例數據字典
    """
    schema = model_class.schema()
    example_data = {}

    for field_name, field_info in schema.get('properties', {}).items():
        if 'example' in field_info:
            example_data[field_name] = field_info['example']
        elif field_info.get('type') == 'string':
            example_data[field_name] = f"example_{field_name}"
        elif field_info.get('type') == 'integer':
            example_data[field_name] = 42
        elif field_info.get('type') == 'number':
            example_data[field_name] = 3.14

    return example_data


# ============================================================================
# 第八部分：使用示例
# ============================================================================

def example_basic_models():
    """基礎模型示例"""
    print("\n" + "="*60)
    print("示例 1: 基礎模型")
    print("="*60)

    # 創建任務
    task = SimpleTask(
        title="完成 Atomic Agents 教程",
        description="學習所有核心概念",
        priority=Priority.HIGH,
        due_date=date(2025, 12, 31)
    )

    print(f"\n任務 ID: {task.id}")
    print(f"標題: {task.title}")
    print(f"優先級: {task.priority}")
    print(f"狀態: {task.status}")
    print(f"\nJSON 輸出:\n{task.json(indent=2)}")


def example_nested_models():
    """嵌套模型示例"""
    print("\n" + "="*60)
    print("示例 2: 嵌套模型")
    print("="*60)

    # 創建用戶
    user = User(
        username="atomic_user",
        full_name="張三",
        age=30,
        contact=ContactInfo(
            email="atomic@example.com",
            phone="+886-2-1234-5678",
            address=Address(
                street="信義路五段7號",
                city="台北市",
                state="台灣",
                postal_code="110"
            )
        ),
        tags=["developer", "ai-enthusiast"]
    )

    print(f"\n用戶名: {user.username}")
    print(f"全名: {user.full_name}")
    print(f"郵箱: {user.contact.email}")
    print(f"城市: {user.contact.address.city}")


def example_conversation_context():
    """對話上下文示例"""
    print("\n" + "="*60)
    print("示例 3: 對話上下文")
    print("="*60)

    # 創建對話上下文
    context = ConversationContext(max_history=5)

    # 添加消息
    context.add_message(MessageRole.USER, "你好，Atomic Agents！")
    context.add_message(MessageRole.ASSISTANT, "你好！我能幫你什麼？")
    context.add_message(MessageRole.USER, "請介紹一下 Schema 設計")

    print(f"\n對話 ID: {context.conversation_id}")
    print(f"消息數量: {len(context.messages)}")
    print(f"\n對話內容:")
    print(context.get_context_string())


def example_dynamic_models():
    """動態模型示例"""
    print("\n" + "="*60)
    print("示例 4: 動態模型")
    print("="*60)

    # 創建動態輸入模型
    DynamicInput = ModelFactory.create_simple_input("query", str)
    dynamic_input = DynamicInput(query="動態創建的查詢")
    print(f"\n動態輸入: {dynamic_input.json()}")

    # 創建動態響應模型
    ResponseModel = ModelFactory.create_response_model({
        'result': (str, "處理結果"),
        'score': (float, "分數"),
        'success': (bool, "是否成功")
    })

    response = ResponseModel(
        result="成功",
        score=0.95,
        success=True
    )
    print(f"\n動態響應: {response.json()}")


def example_validation():
    """驗證示例"""
    print("\n" + "="*60)
    print("示例 5: Schema 驗證")
    print("="*60)

    # 有效數據
    valid_data = {
        'title': '測試任務',
        'priority': 'high',
        'status': 'pending'
    }
    is_valid, error = validate_schema(SimpleTask, valid_data)
    print(f"\n有效數據驗證: {is_valid}")

    # 無效數據
    invalid_data = {
        'title': '',  # 標題太短
        'priority': 'invalid'  # 無效的優先級
    }
    is_valid, error = validate_schema(SimpleTask, invalid_data)
    print(f"無效數據驗證: {is_valid}")
    if error:
        print(f"錯誤: {error}")


def main():
    """主函數"""
    print("\n" + "="*60)
    print("Atomic Agents 輸入輸出模式設計")
    print("="*60)

    # 運行示例
    example_basic_models()
    example_nested_models()
    example_conversation_context()
    example_dynamic_models()
    example_validation()

    print("\n" + "="*60)
    print("所有示例運行完成！")
    print("="*60)


if __name__ == "__main__":
    main()
