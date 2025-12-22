"""
08_結構化輸出.py - Agno 結構化輸出與 Pydantic 整合

本範例展示如何使用 Pydantic 模型實現結構化輸出，包括：
- Pydantic 模型定義
- 結構化數據提取
- 類型驗證與約束
- 複雜對象建模
- JSON Schema 生成
- 批量數據處理

作者：LLM-agent-Demo Team
日期：2025-12
框架：Agno (原 Phidata)
"""

import os
from typing import List, Optional
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator

# Agno 核心導入
from agno.agent import Agent
from agno.models.openai import OpenAIChat

# 載入環境變數
load_dotenv()


# ============================================================================
# 範例 1: 基礎結構化輸出
# ============================================================================

class MovieInfo(BaseModel):
    """電影信息模型"""
    title: str = Field(..., description="電影標題")
    year: int = Field(..., description="上映年份", ge=1900, le=2100)
    director: str = Field(..., description="導演姓名")
    genre: List[str] = Field(..., description="電影類型列表")
    rating: float = Field(..., description="評分", ge=0.0, le=10.0)

def example_1_basic_structured_output():
    """
    基礎結構化輸出：提取電影信息

    優勢：
    - 保證輸出格式一致
    - 自動類型驗證
    - 易於程序處理
    """
    print("\n" + "="*80)
    print("範例 1: 基礎結構化輸出")
    print("="*80)

    # 創建 Agent 並指定響應模型
    agent = Agent(
        name="movie_extractor",
        model=OpenAIChat(id="gpt-4"),
        response_model=MovieInfo,
        markdown=False
    )

    # 提取電影信息
    text = """
    《全面啟動》是2010年上映的科幻動作片，由克里斯多福·諾蘭執導。
    這部電影獲得了極高的評價，在 IMDb 上的評分達到 8.8 分。
    """

    print(f"\n原始文本:\n{text}\n")
    print("提取結構化信息...")
    print("-" * 80)

    response = agent.run(f"從以下文本中提取電影信息：\n{text}")

    # response 是 MovieInfo 對象
    print(f"\n結構化輸出:")
    print(f"  標題: {response.title}")
    print(f"  年份: {response.year}")
    print(f"  導演: {response.director}")
    print(f"  類型: {', '.join(response.genre)}")
    print(f"  評分: {response.rating}\n")

    # 轉換為 JSON
    print(f"JSON 格式:\n{response.model_dump_json(indent=2)}\n")


# ============================================================================
# 範例 2: 複雜嵌套結構
# ============================================================================

class Address(BaseModel):
    """地址模型"""
    street: str = Field(..., description="街道地址")
    city: str = Field(..., description="城市")
    country: str = Field(..., description="國家")
    postal_code: Optional[str] = Field(None, description="郵遞區號")

class Contact(BaseModel):
    """聯絡方式"""
    email: Optional[str] = Field(None, description="電子郵件")
    phone: Optional[str] = Field(None, description="電話號碼")

class Person(BaseModel):
    """人員信息（嵌套結構）"""
    name: str = Field(..., description="姓名")
    age: int = Field(..., description="年齡", ge=0, le=150)
    occupation: str = Field(..., description="職業")
    address: Address = Field(..., description="地址信息")
    contact: Contact = Field(..., description="聯絡方式")
    skills: List[str] = Field(default=[], description="技能列表")

def example_2_nested_structure():
    """
    複雜嵌套結構：提取人員完整信息
    """
    print("\n" + "="*80)
    print("範例 2: 複雜嵌套結構")
    print("="*80)

    agent = Agent(
        name="person_extractor",
        model=OpenAIChat(id="gpt-4"),
        response_model=Person
    )

    bio = """
    李明，35 歲，是一位資深的機器學習工程師。
    他住在台灣台北市信義路 100 號，郵遞區號 110。
    聯絡方式：email 是 liming@example.com，電話是 02-1234-5678。
    他精通 Python、TensorFlow 和 PyTorch。
    """

    print(f"\n簡歷文本:\n{bio}\n")
    print("提取人員信息...")
    print("-" * 80)

    person = agent.run(f"從以下簡歷中提取完整的人員信息：\n{bio}")

    print(f"\n結構化輸出:")
    print(f"  姓名: {person.name}")
    print(f"  年齡: {person.age}")
    print(f"  職業: {person.occupation}")
    print(f"  地址: {person.address.street}, {person.address.city}, {person.address.country}")
    print(f"  郵遞區號: {person.address.postal_code}")
    print(f"  Email: {person.contact.email}")
    print(f"  電話: {person.contact.phone}")
    print(f"  技能: {', '.join(person.skills)}\n")


# ============================================================================
# 範例 3: 列表數據提取
# ============================================================================

class Product(BaseModel):
    """產品模型"""
    name: str = Field(..., description="產品名稱")
    price: float = Field(..., description="價格", gt=0)
    category: str = Field(..., description="類別")
    in_stock: bool = Field(..., description="是否有貨")

class ProductList(BaseModel):
    """產品列表"""
    products: List[Product] = Field(..., description="產品列表")
    total_count: int = Field(..., description="產品總數")

def example_3_list_extraction():
    """
    批量提取：從文本中提取多個產品信息
    """
    print("\n" + "="*80)
    print("範例 3: 列表數據提取")
    print("="*80)

    agent = Agent(
        name="product_extractor",
        model=OpenAIChat(id="gpt-4"),
        response_model=ProductList
    )

    catalog = """
    我們的產品目錄：
    1. iPhone 15 Pro - 售價 $999，屬於智慧型手機類別，目前有貨
    2. MacBook Pro 14 - 售價 $1,999，屬於筆記型電腦類別，目前有貨
    3. AirPods Pro - 售價 $249，屬於音訊設備類別，目前缺貨
    4. iPad Air - 售價 $599，屬於平板電腦類別，目前有貨
    """

    print(f"\n產品目錄:\n{catalog}\n")
    print("提取產品列表...")
    print("-" * 80)

    result = agent.run(f"從以下目錄中提取所有產品信息：\n{catalog}")

    print(f"\n提取結果:")
    print(f"總共找到 {result.total_count} 個產品\n")

    for i, product in enumerate(result.products, 1):
        status = "有貨" if product.in_stock else "缺貨"
        print(f"{i}. {product.name}")
        print(f"   價格: ${product.price}")
        print(f"   類別: {product.category}")
        print(f"   庫存: {status}\n")


# ============================================================================
# 範例 4: 數據驗證與約束
# ============================================================================

class UserRegistration(BaseModel):
    """用戶註冊模型（帶驗證）"""
    username: str = Field(..., min_length=3, max_length=20, description="用戶名")
    email: str = Field(..., description="電子郵件")
    age: int = Field(..., ge=18, le=120, description="年齡（必須 >= 18）")
    password_strength: str = Field(..., description="密碼強度：weak/medium/strong")

    @validator('email')
    def validate_email(cls, v):
        """驗證郵箱格式"""
        if '@' not in v:
            raise ValueError('無效的電子郵件地址')
        return v.lower()

    @validator('password_strength')
    def validate_password_strength(cls, v):
        """驗證密碼強度"""
        valid_strengths = ['weak', 'medium', 'strong']
        if v.lower() not in valid_strengths:
            raise ValueError(f'密碼強度必須是: {", ".join(valid_strengths)}')
        return v.lower()

def example_4_validation():
    """
    數據驗證：確保提取的數據符合業務規則
    """
    print("\n" + "="*80)
    print("範例 4: 數據驗證與約束")
    print("="*80)

    agent = Agent(
        name="registration_processor",
        model=OpenAIChat(id="gpt-4"),
        response_model=UserRegistration
    )

    registration_text = """
    用戶想要註冊：
    - 用戶名：john_doe
    - 郵箱：John.Doe@Example.com
    - 年齡：25 歲
    - 密碼是一個強密碼（包含大小寫、數字和符號）
    """

    print(f"\n註冊信息:\n{registration_text}\n")
    print("處理註冊...")
    print("-" * 80)

    try:
        user = agent.run(f"處理以下註冊信息：\n{registration_text}")

        print(f"\n驗證通過！")
        print(f"  用戶名: {user.username}")
        print(f"  郵箱: {user.email}")
        print(f"  年齡: {user.age}")
        print(f"  密碼強度: {user.password_strength}\n")

    except Exception as e:
        print(f"\n驗證失敗: {e}\n")


# ============================================================================
# 範例 5: 分類和標籤
# ============================================================================

class ArticleAnalysis(BaseModel):
    """文章分析結果"""
    title: str = Field(..., description="文章標題")
    summary: str = Field(..., max_length=200, description="簡短摘要（最多200字）")
    category: str = Field(..., description="類別：tech/business/science/entertainment/other")
    tags: List[str] = Field(..., max_items=5, description="關鍵標籤（最多5個）")
    sentiment: str = Field(..., description="情感：positive/neutral/negative")
    reading_time_minutes: int = Field(..., ge=1, description="預估閱讀時間（分鐘）")

def example_5_classification():
    """
    內容分類和分析
    """
    print("\n" + "="*80)
    print("範例 5: 分類和標籤")
    print("="*80)

    agent = Agent(
        name="content_analyzer",
        model=OpenAIChat(id="gpt-4"),
        response_model=ArticleAnalysis
    )

    article = """
    標題：Agno 框架革新 AI Agent 開發

    Agno（原 Phidata）是一個突破性的 AI Agent 框架，它的性能比競爭對手快 529 倍，
    內存使用低 24 倍。這個框架支持多模態處理，包括文本、圖像、音頻和視頻。
    開發者們對這個框架的簡單性和強大功能讚不絕口。它內建了 100 多個工具包，
    讓開發者能夠快速構建生產級的 AI 應用。Agno 還提供了 AgentOS 運行時環境，
    支持企業級部署。這個框架的出現，預示著 AI Agent 開發進入了一個新時代。
    """

    print(f"\n文章內容:\n{article}\n")
    print("分析文章...")
    print("-" * 80)

    analysis = agent.run(f"分析以下文章：\n{article}")

    print(f"\n分析結果:")
    print(f"  標題: {analysis.title}")
    print(f"  摘要: {analysis.summary}")
    print(f"  類別: {analysis.category}")
    print(f"  標籤: {', '.join(analysis.tags)}")
    print(f"  情感: {analysis.sentiment}")
    print(f"  閱讀時間: {analysis.reading_time_minutes} 分鐘\n")


# ============================================================================
# 範例 6: 實體關係提取
# ============================================================================

class Entity(BaseModel):
    """實體"""
    name: str = Field(..., description="實體名稱")
    type: str = Field(..., description="實體類型：person/organization/location/technology")

class Relationship(BaseModel):
    """關係"""
    source: str = Field(..., description="源實體")
    target: str = Field(..., description="目標實體")
    relation: str = Field(..., description="關係類型")

class KnowledgeGraph(BaseModel):
    """知識圖譜"""
    entities: List[Entity] = Field(..., description="實體列表")
    relationships: List[Relationship] = Field(..., description="關係列表")

def example_6_knowledge_extraction():
    """
    知識圖譜：提取實體和關係
    """
    print("\n" + "="*80)
    print("範例 6: 實體關係提取")
    print("="*80)

    agent = Agent(
        name="knowledge_extractor",
        model=OpenAIChat(id="gpt-4"),
        response_model=KnowledgeGraph
    )

    text = """
    OpenAI 開發了 GPT-4 模型，該模型被整合到 Agno 框架中。
    Agno 由 Phidata 團隊創建，總部位於美國舊金山。
    GPT-4 是一個大型語言模型，支持多模態處理。
    """

    print(f"\n文本:\n{text}\n")
    print("提取知識圖譜...")
    print("-" * 80)

    kg = agent.run(f"從以下文本中提取實體和關係：\n{text}")

    print(f"\n實體:")
    for entity in kg.entities:
        print(f"  - {entity.name} ({entity.type})")

    print(f"\n關係:")
    for rel in kg.relationships:
        print(f"  - {rel.source} --[{rel.relation}]--> {rel.target}")

    print()


# ============================================================================
# 主函數：運行所有範例
# ============================================================================
def main():
    """運行所有結構化輸出範例"""

    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║          Agno 結構化輸出與 Pydantic 整合示範                   ║
    ║                                                                ║
    ║  展示如何使用 Pydantic 模型實現可靠的結構化輸出                ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

    # 檢查環境變數
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 錯誤: 請設置 OPENAI_API_KEY 環境變數")
        return

    try:
        # 運行各個範例
        example_1_basic_structured_output()
        example_2_nested_structure()
        example_3_list_extraction()
        example_4_validation()
        example_5_classification()
        example_6_knowledge_extraction()

        print("\n" + "="*80)
        print("✅ 所有範例執行完成！")
        print("="*80)

        print("\n📚 下一步學習：")
        print("- 09_AgentOS部署.py - 生產環境部署")
        print("- 10_MCP整合.py - Model Context Protocol")

    except Exception as e:
        print(f"\n❌ 執行過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


# ============================================================================
# 學習要點總結
# ============================================================================
"""
📚 Agno 結構化輸出學習要點：

1. **Pydantic 模型定義**
   ```python
   from pydantic import BaseModel, Field

   class MyModel(BaseModel):
       field1: str = Field(..., description="描述")
       field2: int = Field(..., ge=0, le=100)
   ```

2. **使用響應模型**
   ```python
   agent = Agent(
       model=OpenAIChat(id="gpt-4"),
       response_model=MyModel
   )

   result = agent.run("提取信息")
   # result 是 MyModel 的實例
   ```

3. **字段類型**
   - 基本類型：str, int, float, bool
   - 容器類型：List, Dict, Set, Tuple
   - 可選類型：Optional[T]
   - 嵌套模型：其他 BaseModel

4. **字段約束**
   ```python
   Field(
       ...,                    # 必填
       default=value,          # 默認值
       min_length=3,          # 最小長度
       max_length=100,        # 最大長度
       ge=0,                  # >= 0
       le=100,                # <= 100
       description="描述"
   )
   ```

5. **自定義驗證**
   ```python
   @validator('field_name')
   def validate_field(cls, v):
       if condition:
           raise ValueError('錯誤信息')
       return v
   ```

6. **嵌套結構**
   ```python
   class Address(BaseModel):
       street: str
       city: str

   class Person(BaseModel):
       name: str
       address: Address
   ```

7. **列表處理**
   ```python
   class ItemList(BaseModel):
       items: List[Item]
       total: int
   ```

8. **JSON 轉換**
   ```python
   # 轉換為字典
   data = model.model_dump()

   # 轉換為 JSON
   json_str = model.model_dump_json(indent=2)

   # 從 JSON 創建
   model = MyModel.model_validate_json(json_str)
   ```

💡 最佳實踐：
- 提供清晰的字段描述
- 使用適當的類型約束
- 實施自定義驗證
- 處理可選字段
- 編寫文檔字符串

🔗 相關資源：
- Pydantic 文檔: https://docs.pydantic.dev
- Agno 結構化輸出: https://docs.agno.com/structured-output
- JSON Schema: https://json-schema.org

⚡ 結構化輸出優勢：
- 保證數據格式一致
- 自動類型驗證
- 易於程序處理
- 減少錯誤
- 提高可靠性
"""
