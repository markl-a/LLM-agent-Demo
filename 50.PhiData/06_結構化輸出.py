"""
PhiData 結構化輸出示例

這個腳本展示了如何使用 PhiData 生成結構化輸出，包括：
1. Pydantic 模型定義
2. JSON Schema 輸出
3. 數據驗證
4. 類型安全
5. 複雜數據結構
6. 嵌套模型
7. 列表和字典
8. 可選字段
9. 默認值處理
10. 輸出格式化

作者: PhiData Team
日期: 2025
"""

import os
import json
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from enum import Enum

# Pydantic 導入
from pydantic import BaseModel, Field, validator

# PhiData 核心導入
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.utils.log import logger

# 環境變量管理
from dotenv import load_dotenv

# 載入環境變量
load_dotenv()


# ============================================================================
# Pydantic 模型定義
# ============================================================================

class Priority(str, Enum):
    """任務優先級枚舉"""
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"
    URGENT = "緊急"


class TaskStatus(str, Enum):
    """任務狀態枚舉"""
    TODO = "待辦"
    IN_PROGRESS = "進行中"
    COMPLETED = "已完成"
    CANCELLED = "已取消"


class Task(BaseModel):
    """任務模型"""
    title: str = Field(..., description="任務標題")
    description: str = Field(..., description="任務描述")
    priority: Priority = Field(default=Priority.MEDIUM, description="優先級")
    status: TaskStatus = Field(default=TaskStatus.TODO, description="狀態")
    due_date: Optional[str] = Field(None, description="截止日期 (YYYY-MM-DD)")
    tags: List[str] = Field(default_factory=list, description="標籤列表")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "完成項目報告",
                "description": "撰寫Q1季度項目總結報告",
                "priority": "高",
                "status": "待辦",
                "due_date": "2025-01-31",
                "tags": ["報告", "重要"]
            }
        }


class Person(BaseModel):
    """人員模型"""
    name: str = Field(..., description="姓名")
    age: int = Field(..., gt=0, lt=150, description="年齡")
    email: str = Field(..., description="電子郵件")
    phone: Optional[str] = Field(None, description="電話號碼")
    address: Optional[str] = Field(None, description="地址")


class Product(BaseModel):
    """產品模型"""
    name: str = Field(..., description="產品名稱")
    description: str = Field(..., description="產品描述")
    price: float = Field(..., gt=0, description="價格")
    category: str = Field(..., description="類別")
    in_stock: bool = Field(default=True, description="是否有貨")
    tags: List[str] = Field(default_factory=list, description="標籤")


class StockInfo(BaseModel):
    """股票信息模型"""
    symbol: str = Field(..., description="股票代碼")
    company_name: str = Field(..., description="公司名稱")
    current_price: float = Field(..., description="當前價格")
    change_percent: float = Field(..., description="漲跌幅 (%)")
    market_cap: str = Field(..., description="市值")
    pe_ratio: Optional[float] = Field(None, description="市盈率")


class Article(BaseModel):
    """文章模型"""
    title: str = Field(..., description="文章標題")
    author: str = Field(..., description="作者")
    summary: str = Field(..., description="摘要")
    content: str = Field(..., description="正文內容")
    published_date: str = Field(..., description="發布日期")
    tags: List[str] = Field(default_factory=list, description="標籤")
    word_count: int = Field(..., gt=0, description="字數")


class Recipe(BaseModel):
    """食譜模型"""
    name: str = Field(..., description="菜名")
    cuisine: str = Field(..., description="菜系")
    difficulty: str = Field(..., description="難度")
    prep_time: int = Field(..., description="準備時間（分鐘）")
    cook_time: int = Field(..., description="烹飪時間（分鐘）")
    servings: int = Field(..., description="份數")
    ingredients: List[str] = Field(..., description="食材列表")
    instructions: List[str] = Field(..., description="步驟列表")
    nutrition: Optional[Dict[str, Any]] = Field(None, description="營養信息")


class MovieReview(BaseModel):
    """電影評論模型"""
    movie_title: str = Field(..., description="電影名稱")
    director: str = Field(..., description="導演")
    genre: List[str] = Field(..., description="類型")
    rating: float = Field(..., ge=0, le=10, description="評分 (0-10)")
    review_summary: str = Field(..., description="評論摘要")
    pros: List[str] = Field(..., description="優點")
    cons: List[str] = Field(..., description="缺點")
    recommendation: str = Field(..., description="推薦意見")


class MeetingNotes(BaseModel):
    """會議記錄模型"""
    title: str = Field(..., description="會議標題")
    date: str = Field(..., description="日期")
    attendees: List[str] = Field(..., description="參與者")
    agenda: List[str] = Field(..., description="議程")
    key_points: List[str] = Field(..., description="要點")
    action_items: List[Task] = Field(..., description="行動項目")
    next_meeting: Optional[str] = Field(None, description="下次會議時間")


# ============================================================================
# 結構化輸出 Agent 類
# ============================================================================

class StructuredOutputAgent:
    """
    結構化輸出 Agent 類

    提供各種結構化輸出功能，確保 AI 輸出符合預定義的數據結構。
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化結構化輸出 Agent

        參數:
            api_key: OpenAI API 密鑰
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("未找到 OPENAI_API_KEY")

        logger.info("初始化結構化輸出 Agent")

    def create_structured_agent(
        self,
        response_model: type[BaseModel],
        agent_name: str = "結構化輸出 Agent"
    ) -> Agent:
        """
        創建結構化輸出 Agent

        參數:
            response_model: Pydantic 模型類
            agent_name: Agent 名稱

        返回:
            配置好的 Agent
        """
        logger.info(f"創建結構化輸出 Agent: {agent_name}")

        agent = Agent(
            name=agent_name,
            model=OpenAIChat(
                id="gpt-4",
                api_key=self.api_key,
            ),
            response_model=response_model,  # 指定輸出模型
            description=f"生成 {response_model.__name__} 格式的結構化輸出",
            instructions=[
                "嚴格按照指定的數據結構生成輸出",
                "確保所有必填字段都有值",
                "數據類型必須正確",
                "使用繁體中文",
            ],
            markdown=True,
        )

        return agent

    def generate_task(self, agent: Agent, description: str) -> Task:
        """
        生成任務對象

        參數:
            agent: Agent 實例
            description: 任務描述

        返回:
            Task 對象
        """
        logger.info(f"生成任務: {description}")

        prompt = f"請創建一個任務：{description}"
        response = agent.run(prompt)

        # 如果是 Pydantic 模型，直接返回
        if isinstance(response, Task):
            return response

        # 否則嘗試解析
        if hasattr(response, 'content'):
            task_data = json.loads(response.content)
            return Task(**task_data)

        return response

    def generate_person_profile(
        self,
        agent: Agent,
        description: str
    ) -> Person:
        """
        生成人員資料

        參數:
            agent: Agent 實例
            description: 人員描述

        返回:
            Person 對象
        """
        logger.info(f"生成人員資料: {description}")

        prompt = f"請創建一個人員資料：{description}"
        response = agent.run(prompt)

        if isinstance(response, Person):
            return response

        if hasattr(response, 'content'):
            person_data = json.loads(response.content)
            return Person(**person_data)

        return response

    def generate_product(
        self,
        agent: Agent,
        description: str
    ) -> Product:
        """
        生成產品信息

        參數:
            agent: Agent 實例
            description: 產品描述

        返回:
            Product 對象
        """
        logger.info(f"生成產品信息: {description}")

        prompt = f"請創建一個產品：{description}"
        response = agent.run(prompt)

        if isinstance(response, Product):
            return response

        if hasattr(response, 'content'):
            product_data = json.loads(response.content)
            return Product(**product_data)

        return response

    def generate_article(
        self,
        agent: Agent,
        topic: str
    ) -> Article:
        """
        生成文章

        參數:
            agent: Agent 實例
            topic: 文章主題

        返回:
            Article 對象
        """
        logger.info(f"生成文章: {topic}")

        prompt = f"請撰寫一篇關於「{topic}」的文章"
        response = agent.run(prompt)

        if isinstance(response, Article):
            return response

        if hasattr(response, 'content'):
            article_data = json.loads(response.content)
            return Article(**article_data)

        return response

    def generate_recipe(
        self,
        agent: Agent,
        dish_name: str
    ) -> Recipe:
        """
        生成食譜

        參數:
            agent: Agent 實例
            dish_name: 菜名

        返回:
            Recipe 對象
        """
        logger.info(f"生成食譜: {dish_name}")

        prompt = f"請創建「{dish_name}」的食譜"
        response = agent.run(prompt)

        if isinstance(response, Recipe):
            return response

        if hasattr(response, 'content'):
            recipe_data = json.loads(response.content)
            return Recipe(**recipe_data)

        return response

    def generate_movie_review(
        self,
        agent: Agent,
        movie_title: str
    ) -> MovieReview:
        """
        生成電影評論

        參數:
            agent: Agent 實例
            movie_title: 電影名稱

        返回:
            MovieReview 對象
        """
        logger.info(f"生成電影評論: {movie_title}")

        prompt = f"請撰寫「{movie_title}」的影評"
        response = agent.run(prompt)

        if isinstance(response, MovieReview):
            return response

        if hasattr(response, 'content'):
            review_data = json.loads(response.content)
            return MovieReview(**review_data)

        return response

    def generate_meeting_notes(
        self,
        agent: Agent,
        meeting_info: str
    ) -> MeetingNotes:
        """
        生成會議記錄

        參數:
            agent: Agent 實例
            meeting_info: 會議信息

        返回:
            MeetingNotes 對象
        """
        logger.info(f"生成會議記錄: {meeting_info}")

        prompt = f"請創建會議記錄：{meeting_info}"
        response = agent.run(prompt)

        if isinstance(response, MeetingNotes):
            return response

        if hasattr(response, 'content'):
            notes_data = json.loads(response.content)
            return MeetingNotes(**notes_data)

        return response

    def validate_and_display(
        self,
        model_instance: BaseModel,
        title: str
    ) -> None:
        """
        驗證並顯示模型實例

        參數:
            model_instance: Pydantic 模型實例
            title: 顯示標題
        """
        print(f"\n{'='*60}")
        print(f"{title}")
        print(f"{'='*60}\n")

        # 顯示為格式化的 JSON
        print(json.dumps(
            model_instance.model_dump(),
            ensure_ascii=False,
            indent=2
        ))
        print()


# ============================================================================
# 演示函數
# ============================================================================

def demonstration_task_generation():
    """演示任務生成"""
    print("\n" + "="*60)
    print("演示 1: 結構化任務生成")
    print("="*60)

    agent_system = StructuredOutputAgent()
    agent = agent_system.create_structured_agent(Task, "任務生成器")

    task = agent_system.generate_task(
        agent,
        "完成 Q1 財務報告，需要收集所有部門的數據並進行分析"
    )

    agent_system.validate_and_display(task, "生成的任務")


def demonstration_person_profile():
    """演示人員資料生成"""
    print("\n" + "="*60)
    print("演示 2: 人員資料生成")
    print("="*60)

    agent_system = StructuredOutputAgent()
    agent = agent_system.create_structured_agent(Person, "人員資料生成器")

    person = agent_system.generate_person_profile(
        agent,
        "一位35歲的軟體工程師，住在台北，專長是全端開發"
    )

    agent_system.validate_and_display(person, "生成的人員資料")


def demonstration_product_info():
    """演示產品信息生成"""
    print("\n" + "="*60)
    print("演示 3: 產品信息生成")
    print("="*60)

    agent_system = StructuredOutputAgent()
    agent = agent_system.create_structured_agent(Product, "產品信息生成器")

    product = agent_system.generate_product(
        agent,
        "一款高性能的無線藍牙耳機，支持主動降噪"
    )

    agent_system.validate_and_display(product, "生成的產品信息")


def demonstration_article_generation():
    """演示文章生成"""
    print("\n" + "="*60)
    print("演示 4: 結構化文章生成")
    print("="*60)

    agent_system = StructuredOutputAgent()
    agent = agent_system.create_structured_agent(Article, "文章生成器")

    article = agent_system.generate_article(
        agent,
        "人工智能在教育領域的應用"
    )

    agent_system.validate_and_display(article, "生成的文章")


def demonstration_recipe_generation():
    """演示食譜生成"""
    print("\n" + "="*60)
    print("演示 5: 食譜生成")
    print("="*60)

    agent_system = StructuredOutputAgent()
    agent = agent_system.create_structured_agent(Recipe, "食譜生成器")

    recipe = agent_system.generate_recipe(
        agent,
        "宮保雞丁"
    )

    agent_system.validate_and_display(recipe, "生成的食譜")


def demonstration_movie_review():
    """演示電影評論生成"""
    print("\n" + "="*60)
    print("演示 6: 電影評論生成")
    print("="*60)

    agent_system = StructuredOutputAgent()
    agent = agent_system.create_structured_agent(MovieReview, "影評生成器")

    review = agent_system.generate_movie_review(
        agent,
        "星際效應 (Interstellar)"
    )

    agent_system.validate_and_display(review, "生成的電影評論")


def demonstration_meeting_notes():
    """演示會議記錄生成"""
    print("\n" + "="*60)
    print("演示 7: 會議記錄生成")
    print("="*60)

    agent_system = StructuredOutputAgent()
    agent = agent_system.create_structured_agent(MeetingNotes, "會議記錄生成器")

    notes = agent_system.generate_meeting_notes(
        agent,
        "2025年1月產品規劃會議，討論新功能開發和市場策略"
    )

    agent_system.validate_and_display(notes, "生成的會議記錄")


def main():
    """主函數"""
    print("\n" + "="*60)
    print("PhiData 結構化輸出 - 完整示例")
    print("="*60)

    try:
        # 運行所有演示
        demonstration_task_generation()
        demonstration_person_profile()
        demonstration_product_info()
        demonstration_article_generation()
        demonstration_recipe_generation()
        demonstration_movie_review()
        demonstration_meeting_notes()

        print("\n" + "="*60)
        print("所有演示完成！")
        print("="*60)

        print("\n結構化輸出的優勢：")
        print("1. 類型安全 - 自動驗證數據類型")
        print("2. 數據一致性 - 確保輸出格式統一")
        print("3. 易於處理 - 可直接用於程序邏輯")
        print("4. 減少錯誤 - 自動驗證和錯誤提示")
        print("5. 文檔清晰 - 模型即文檔")

    except Exception as e:
        logger.error(f"運行錯誤: {e}")
        print(f"\n錯誤: {e}")


if __name__ == "__main__":
    main()
