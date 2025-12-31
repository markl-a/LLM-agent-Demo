"""
Instructor 複雜結構提取示例

這個模塊展示了如何使用 Instructor 提取和處理複雜的嵌套數據結構。
包括多層嵌套、循環引用、圖結構等高級場景。

主要內容：
1. 多層嵌套結構
2. 樹形結構提取
3. 圖形結構和關係
4. 遞歸模型定義
5. 複雜業務對象
6. 知識圖譜構建

作者: Instructor 示例
日期: 2025-01-01
"""

import os
from typing import List, Optional, Dict, Any, Union
from datetime import date, datetime
from pydantic import BaseModel, Field
import instructor
from openai import OpenAI


# ============================================================================
# 組織架構樹形結構
# ============================================================================

class Employee(BaseModel):
    """員工模型 - 支持自引用"""
    name: str = Field(description="員工姓名")
    employee_id: str = Field(description="員工ID")
    title: str = Field(description="職位")
    department: str = Field(description="部門")
    email: str = Field(description="郵箱")
    direct_reports: List['Employee'] = Field(
        default_factory=list,
        description="直接下屬列表"
    )

    def get_team_size(self) -> int:
        """獲取團隊總人數（包括自己）"""
        return 1 + sum(emp.get_team_size() for emp in self.direct_reports)

    def print_hierarchy(self, indent: int = 0):
        """打印組織架構"""
        print("  " * indent + f"├─ {self.name} ({self.title})")
        for report in self.direct_reports:
            report.print_hierarchy(indent + 1)


class Organization(BaseModel):
    """組織架構模型"""
    company_name: str = Field(description="公司名稱")
    ceo: Employee = Field(description="CEO（首席執行官）")
    total_employees: int = Field(description="總員工數")

    def validate_employee_count(self) -> bool:
        """驗證員工數量是否匹配"""
        actual_count = self.ceo.get_team_size()
        return actual_count == self.total_employees


# ============================================================================
# 知識圖譜結構
# ============================================================================

class Entity(BaseModel):
    """實體模型"""
    id: str = Field(description="實體唯一標識符")
    name: str = Field(description="實體名稱")
    type: str = Field(description="實體類型（人物、地點、組織等）")
    properties: Dict[str, str] = Field(
        default_factory=dict,
        description="實體屬性"
    )


class Relationship(BaseModel):
    """關係模型"""
    source_id: str = Field(description="源實體ID")
    target_id: str = Field(description="目標實體ID")
    relation_type: str = Field(description="關係類型")
    properties: Dict[str, str] = Field(
        default_factory=dict,
        description="關係屬性"
    )


class KnowledgeGraph(BaseModel):
    """知識圖譜模型"""
    name: str = Field(description="圖譜名稱")
    entities: List[Entity] = Field(description="實體列表")
    relationships: List[Relationship] = Field(description="關係列表")

    def get_entity_by_id(self, entity_id: str) -> Optional[Entity]:
        """根據ID獲取實體"""
        for entity in self.entities:
            if entity.id == entity_id:
                return entity
        return None

    def get_entity_relationships(self, entity_id: str) -> List[Relationship]:
        """獲取實體的所有關係"""
        return [
            rel for rel in self.relationships
            if rel.source_id == entity_id or rel.target_id == entity_id
        ]

    def print_graph(self):
        """打印知識圖譜"""
        print(f"\n知識圖譜: {self.name}")
        print(f"實體數: {len(self.entities)}")
        print(f"關係數: {len(self.relationships)}")

        print("\n實體:")
        for entity in self.entities:
            print(f"  - [{entity.type}] {entity.name} (ID: {entity.id})")

        print("\n關係:")
        for rel in self.relationships:
            source = self.get_entity_by_id(rel.source_id)
            target = self.get_entity_by_id(rel.target_id)
            print(f"  - {source.name} --[{rel.relation_type}]--> {target.name}")


# ============================================================================
# 文檔結構樹
# ============================================================================

class Section(BaseModel):
    """文檔章節模型 - 遞歸結構"""
    title: str = Field(description="章節標題")
    content: str = Field(description="章節內容")
    level: int = Field(description="章節級別（1-6）", ge=1, le=6)
    subsections: List['Section'] = Field(
        default_factory=list,
        description="子章節列表"
    )

    def get_total_sections(self) -> int:
        """獲取總章節數"""
        return 1 + sum(sub.get_total_sections() for sub in self.subsections)

    def print_toc(self, indent: int = 0):
        """打印目錄"""
        prefix = "  " * indent + "#" * self.level
        print(f"{prefix} {self.title}")
        for subsection in self.subsections:
            subsection.print_toc(indent + 1)


class Document(BaseModel):
    """文檔模型"""
    title: str = Field(description="文檔標題")
    author: str = Field(description="作者")
    created_date: date = Field(description="創建日期")
    sections: List[Section] = Field(description="頂級章節列表")
    tags: List[str] = Field(default_factory=list, description="標籤")

    def get_total_sections(self) -> int:
        """獲取文檔總章節數"""
        return sum(section.get_total_sections() for section in self.sections)


# ============================================================================
# 電商產品層級
# ============================================================================

class ProductVariant(BaseModel):
    """產品變體（如不同顏色、尺寸）"""
    sku: str = Field(description="庫存單位")
    name: str = Field(description="變體名稱")
    attributes: Dict[str, str] = Field(description="屬性（顏色、尺寸等）")
    price: float = Field(description="價格", gt=0)
    stock: int = Field(description="庫存數量", ge=0)
    is_available: bool = Field(default=True, description="是否可售")


class ProductImage(BaseModel):
    """產品圖片"""
    url: str = Field(description="圖片URL")
    alt_text: str = Field(description="替代文本")
    is_primary: bool = Field(default=False, description="是否為主圖")


class ProductReview(BaseModel):
    """產品評論"""
    reviewer_name: str = Field(description="評論者姓名")
    rating: int = Field(description="評分（1-5星）", ge=1, le=5)
    title: str = Field(description="評論標題")
    content: str = Field(description="評論內容")
    review_date: date = Field(description="評論日期")
    verified_purchase: bool = Field(default=False, description="是否認證購買")


class Category(BaseModel):
    """產品類別 - 支持多層級"""
    name: str = Field(description="類別名稱")
    slug: str = Field(description="URL slug")
    parent_category: Optional['Category'] = Field(
        default=None,
        description="父類別"
    )
    subcategories: List['Category'] = Field(
        default_factory=list,
        description="子類別列表"
    )


class Product(BaseModel):
    """完整的產品模型"""
    product_id: str = Field(description="產品ID")
    name: str = Field(description="產品名稱")
    brand: str = Field(description="品牌")
    description: str = Field(description="產品描述")
    category: Category = Field(description="產品類別")
    variants: List[ProductVariant] = Field(description="產品變體列表")
    images: List[ProductImage] = Field(description="產品圖片列表")
    reviews: List[ProductReview] = Field(
        default_factory=list,
        description="評論列表"
    )
    specifications: Dict[str, str] = Field(
        default_factory=dict,
        description="產品規格"
    )
    features: List[str] = Field(description="功能特性列表")

    def get_average_rating(self) -> float:
        """計算平均評分"""
        if not self.reviews:
            return 0.0
        return sum(r.rating for r in self.reviews) / len(self.reviews)

    def get_price_range(self) -> tuple:
        """獲取價格範圍"""
        if not self.variants:
            return (0, 0)
        prices = [v.price for v in self.variants]
        return (min(prices), max(prices))


# ============================================================================
# 項目管理複雜結構
# ============================================================================

class Task(BaseModel):
    """任務模型"""
    task_id: str = Field(description="任務ID")
    title: str = Field(description="任務標題")
    description: str = Field(description="任務描述")
    status: str = Field(description="狀態")
    priority: str = Field(description="優先級")
    assignee: str = Field(description="負責人")
    estimated_hours: int = Field(description="預估工時", ge=0)
    actual_hours: Optional[int] = Field(default=None, description="實際工時")
    dependencies: List[str] = Field(
        default_factory=list,
        description="依賴任務ID列表"
    )
    subtasks: List['Task'] = Field(
        default_factory=list,
        description="子任務列表"
    )
    tags: List[str] = Field(default_factory=list, description="標籤")


class Sprint(BaseModel):
    """衝刺模型"""
    sprint_id: str = Field(description="衝刺ID")
    name: str = Field(description="衝刺名稱")
    start_date: date = Field(description="開始日期")
    end_date: date = Field(description="結束日期")
    goal: str = Field(description="衝刺目標")
    tasks: List[Task] = Field(description="任務列表")

    def get_total_estimated_hours(self) -> int:
        """獲取總預估工時"""
        return sum(task.estimated_hours for task in self.tasks)


class Project(BaseModel):
    """項目模型 - 複雜項目管理結構"""
    project_id: str = Field(description="項目ID")
    name: str = Field(description="項目名稱")
    description: str = Field(description="項目描述")
    start_date: date = Field(description="開始日期")
    end_date: Optional[date] = Field(default=None, description="結束日期")
    team_members: List[str] = Field(description="團隊成員列表")
    sprints: List[Sprint] = Field(description="衝刺列表")
    milestones: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="里程碑"
    )
    budget: float = Field(description="預算", gt=0)
    status: str = Field(description="項目狀態")

    def get_total_tasks(self) -> int:
        """獲取總任務數"""
        return sum(len(sprint.tasks) for sprint in self.sprints)


# ============================================================================
# JSON Schema / API 響應結構
# ============================================================================

class APIError(BaseModel):
    """API錯誤模型"""
    code: str = Field(description="錯誤代碼")
    message: str = Field(description="錯誤消息")
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="錯誤詳情"
    )


class PaginationMeta(BaseModel):
    """分頁元數據"""
    current_page: int = Field(description="當前頁", ge=1)
    per_page: int = Field(description="每頁數量", gt=0)
    total_pages: int = Field(description="總頁數", ge=1)
    total_items: int = Field(description="總項目數", ge=0)


class APIResponse(BaseModel):
    """通用API響應模型"""
    success: bool = Field(description="是否成功")
    data: Optional[Union[Dict, List, str]] = Field(
        default=None,
        description="響應數據"
    )
    meta: Optional[PaginationMeta] = Field(
        default=None,
        description="元數據"
    )
    errors: List[APIError] = Field(
        default_factory=list,
        description="錯誤列表"
    )
    timestamp: datetime = Field(description="時間戳")


# ============================================================================
# 輔助函數
# ============================================================================

def setup_client():
    """設置 Instructor 客戶端"""
    api_key = os.getenv("OPENAI_API_KEY", "sk-placeholder")
    openai_client = OpenAI(api_key=api_key)
    return instructor.from_openai(openai_client)


def extract_organization(client):
    """提取組織架構"""
    print(f"\n{'='*60}")
    print("提取組織架構（樹形結構）")
    print(f"{'='*60}")

    text = """
    公司：科技創新有限公司
    總員工數：7人

    CEO：張總（zhang.ceo@company.com，EMP001）

    直接向CEO彙報的有兩位副總：
    1. CTO李總（li.cto@company.com，EMP002）- 技術副總裁
       李總管理著3名工程師：
       - 王工程師（wang.dev@company.com，EMP003）- 高級工程師
       - 趙工程師（zhao.dev@company.com，EMP004）- 工程師
       - 錢工程師（qian.dev@company.com，EMP005）- 初級工程師

    2. COO孫總（sun.coo@company.com，EMP006）- 運營副總裁
       孫總管理著1名運營經理：
       - 周經理（zhou.ops@company.com，EMP007）- 運營經理
    """

    org = client.chat.completions.create(
        model="gpt-4",
        response_model=Organization,
        messages=[
            {"role": "user", "content": f"提取組織架構：\n{text}"}
        ]
    )

    print(f"\n組織架構: {org.company_name}")
    print(f"總員工數: {org.total_employees}")
    print(f"\n組織樹:")
    org.ceo.print_hierarchy()

    print(f"\n驗證: 員工數量{'匹配' if org.validate_employee_count() else '不匹配'}")

    return org


def extract_knowledge_graph(client):
    """提取知識圖譜"""
    print(f"\n{'='*60}")
    print("提取知識圖譜")
    print(f"{'='*60}")

    text = """
    知識圖譜：人工智能領域

    實體：
    1. 深度學習（ID: tech_dl）- 類型：技術
       屬性：發展年代=2010s, 應用領域=CV/NLP

    2. Geoffrey Hinton（ID: person_hinton）- 類型：人物
       屬性：職位=教授, 機構=多倫多大學

    3. ImageNet（ID: dataset_imagenet）- 類型：數據集
       屬性：規模=1400萬張圖片, 類別=1000

    4. 卷積神經網絡（ID: tech_cnn）- 類型：技術
       屬性：提出年代=1980s, 應用=圖像識別

    關係：
    - Hinton 開創了 深度學習
    - 深度學習 包含 卷積神經網絡
    - 卷積神經網絡 在 ImageNet 上取得突破
    - Hinton 貢獻於 ImageNet 競賽
    """

    kg = client.chat.completions.create(
        model="gpt-4",
        response_model=KnowledgeGraph,
        messages=[
            {"role": "user", "content": f"提取知識圖譜：\n{text}"}
        ]
    )

    kg.print_graph()
    return kg


def extract_document_structure(client):
    """提取文檔結構"""
    print(f"\n{'='*60}")
    print("提取文檔結構（遞歸章節）")
    print(f"{'='*60}")

    text = """
    文檔標題：Python 編程指南
    作者：技術專家
    創建日期：2025-01-01
    標籤：Python, 編程, 教程

    第一章：Python 基礎
    內容：介紹 Python 的基本概念和語法。

    1.1 變量和數據類型
    內容：講解 Python 中的變量定義和基本數據類型。

    1.2 控制流
    內容：介紹 if、for、while 等控制語句。

    第二章：高級特性
    內容：深入探討 Python 的高級功能。

    2.1 面向對象編程
    內容：類、對象、繼承等概念。

    2.1.1 類的定義
    內容：如何定義和使用類。

    2.1.2 繼承和多態
    內容：繼承機制和多態性。

    2.2 裝飾器
    內容：裝飾器的原理和應用。
    """

    doc = client.chat.completions.create(
        model="gpt-4",
        response_model=Document,
        messages=[
            {"role": "user", "content": f"提取文檔結構：\n{text}"}
        ]
    )

    print(f"\n文檔: {doc.title}")
    print(f"作者: {doc.author}")
    print(f"總章節數: {doc.get_total_sections()}")
    print(f"\n目錄:")
    for section in doc.sections:
        section.print_toc()

    return doc


def extract_product_details(client):
    """提取產品詳情"""
    print(f"\n{'='*60}")
    print("提取產品詳情（複雜電商結構）")
    print(f"{'='*60}")

    text = """
    產品ID: PROD-12345
    產品名稱：智能運動手環
    品牌：FitTech

    描述：一款功能全面的智能運動手環，支持多種運動模式和健康監測。

    類別：電子產品 > 可穿戴設備 > 智能手環

    變體：
    1. 黑色款（SKU-001）- 黑色，M碼，價格$99，庫存50
    2. 藍色款（SKU-002）- 藍色，M碼，價格$99，庫存30
    3. 紅色款（SKU-003）- 紅色，L碼，價格$109，庫存20

    功能特性：
    - 心率監測
    - 睡眠追蹤
    - 運動記錄
    - 消息提醒

    規格：
    - 屏幕：1.3英寸OLED
    - 電池：7天續航
    - 防水：5ATM

    評論：
    1. 用戶A，5星，"非常好用"，2025-01-10，已認證
    2. 用戶B，4星，"性價比高"，2025-01-08，已認證
    """

    product = client.chat.completions.create(
        model="gpt-4",
        response_model=Product,
        messages=[
            {"role": "user", "content": f"提取產品信息：\n{text}"}
        ]
    )

    print(f"\n產品: {product.name}")
    print(f"品牌: {product.brand}")
    print(f"變體數: {len(product.variants)}")
    print(f"價格範圍: ${product.get_price_range()[0]}-${product.get_price_range()[1]}")
    print(f"平均評分: {product.get_average_rating():.1f}星")

    return product


def extract_project(client):
    """提取項目信息"""
    print(f"\n{'='*60}")
    print("提取項目信息（項目管理結構）")
    print(f"{'='*60}")

    text = """
    項目ID: PROJ-2025-001
    項目名稱：移動應用開發
    描述：開發一款創新的移動應用
    開始日期：2025-01-15
    團隊成員：張三、李四、王五、趙六
    預算：$100,000
    狀態：進行中

    第一個衝刺（SPRINT-001）：設計階段
    時間：2025-01-15 至 2025-01-29
    目標：完成UI/UX設計

    任務：
    1. TASK-001：需求分析，負責人：張三，優先級：高，預估：16小時
    2. TASK-002：UI設計，負責人：李四，優先級：高，預估：24小時
       子任務：
       - TASK-002-1：首頁設計，負責人：李四，預估：8小時
       - TASK-002-2：詳情頁設計，負責人：李四，預估：8小時

    第二個衝刺（SPRINT-002）：開發階段
    時間：2025-02-01 至 2025-02-15
    目標：完成核心功能開發

    任務：
    1. TASK-003：前端開發，負責人：王五，優先級：高，預估：40小時
    2. TASK-004：後端API，負責人：趙六，優先級：高，預估：32小時
    """

    project = client.chat.completions.create(
        model="gpt-4",
        response_model=Project,
        messages=[
            {"role": "user", "content": f"提取項目信息：\n{text}"}
        ]
    )

    print(f"\n項目: {project.name}")
    print(f"團隊規模: {len(project.team_members)} 人")
    print(f"衝刺數: {len(project.sprints)}")
    print(f"總任務數: {project.get_total_tasks()}")
    print(f"預算: ${project.budget:,.2f}")

    return project


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主函數 - 運行所有複雜結構示例"""
    print("="*60)
    print("Instructor 複雜結構提取示例")
    print("="*60)

    client = setup_client()

    # 組織架構
    extract_organization(client)

    # 知識圖譜
    extract_knowledge_graph(client)

    # 文檔結構
    extract_document_structure(client)

    # 產品詳情
    extract_product_details(client)

    # 項目管理
    extract_project(client)

    print("\n" + "="*60)
    print("複雜結構提取要點總結")
    print("="*60)
    print("""
1. 樹形結構：
   - 使用自引用模型（Employee -> Employee）
   - 遞歸定義（Section -> Section）
   - 合理設計終止條件

2. 圖形結構：
   - 分離實體和關係
   - 使用ID進行引用
   - 提供圖遍歷方法

3. 多層嵌套：
   - 清晰的層級關係
   - 每層有明確的職責
   - 提供聚合方法

4. 複雜業務對象：
   - 組合多個子模型
   - 包含計算屬性
   - 提供業務邏輯方法

5. 設計原則：
   - 保持模型單一職責
   - 使用組合優於繼承
   - 提供有用的輔助方法
   - 添加驗證邏輯
   - 考慮性能和可維護性
    """)


if __name__ == "__main__":
    main()
