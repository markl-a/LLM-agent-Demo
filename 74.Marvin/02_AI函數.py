"""
Marvin AI 函數詳解

本示例展示：
1. @marvin.fn 裝飾器的使用
2. 函數參數和返回值
3. 類型注解的重要性
4. 文檔字符串作為提示
5. 錯誤處理

運行方式：
    python 02_AI函數.py
"""

import os
import marvin
from typing import Optional, List, Dict, Union
from pydantic import BaseModel, Field
from enum import Enum


# ==================== 基本 AI 函數 ====================

@marvin.fn
def simple_function(input_text: str) -> str:
    """簡單地重複輸入的文本"""


@marvin.fn
def add_emoji(text: str) -> str:
    """在文本後面添加一個合適的 emoji 表情符號"""


@marvin.fn
def make_professional(casual_text: str) -> str:
    """
    將隨意的文本改寫成專業的表達方式

    Args:
        casual_text: 隨意的文本

    Returns:
        專業化的文本
    """


def example_basic_functions():
    """示例 1: 基本 AI 函數"""
    print("\n" + "="*60)
    print("示例 1: 基本 AI 函數")
    print("="*60)

    try:
        # 簡單函數
        result1 = simple_function("Hello Marvin")
        print(f"簡單函數: {result1}")

        # 添加 emoji
        result2 = add_emoji("今天天氣真好")
        print(f"添加 emoji: {result2}")

        result3 = add_emoji("I love programming")
        print(f"添加 emoji: {result3}")

        # 專業化文本
        casual = "嘿，能不能快點把那個東西給我？"
        professional = make_professional(casual)
        print(f"\n隨意文本: {casual}")
        print(f"專業文本: {professional}")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 帶詳細提示的函數 ====================

@marvin.fn
def generate_product_description(
    product_name: str,
    features: List[str]
) -> str:
    """
    為產品生成吸引人的描述

    要求：
    - 長度約 100-150 字
    - 突出產品特點
    - 使用積極的語言
    - 包含行動呼籲

    Args:
        product_name: 產品名稱
        features: 產品特點列表

    Returns:
        產品描述
    """


@marvin.fn
def create_email(
    recipient_name: str,
    purpose: str,
    tone: str = "formal"
) -> str:
    """
    創建電子郵件

    要求：
    - 包含適當的稱呼和結尾
    - 根據 tone 調整語氣（formal/casual/friendly）
    - 清晰表達目的
    - 使用適當的格式

    Args:
        recipient_name: 收件人姓名
        purpose: 郵件目的
        tone: 語氣風格（formal/casual/friendly）

    Returns:
        完整的電子郵件內容
    """


def example_detailed_prompts():
    """示例 2: 詳細提示的函數"""
    print("\n" + "="*60)
    print("示例 2: 詳細提示的函數")
    print("="*60)

    try:
        # 生成產品描述
        description = generate_product_description(
            product_name="智能手錶 Pro",
            features=[
                "心率監測",
                "GPS 定位",
                "7天續航",
                "防水設計",
                "50+ 運動模式"
            ]
        )
        print(f"產品描述:\n{description}\n")

        # 創建正式郵件
        email = create_email(
            recipient_name="王經理",
            purpose="申請年假",
            tone="formal"
        )
        print(f"正式郵件:\n{email}\n")

        # 創建友好郵件
        email2 = create_email(
            recipient_name="小明",
            purpose="週末聚會邀請",
            tone="friendly"
        )
        print(f"友好郵件:\n{email2}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 複雜類型返回值 ====================

class Article(BaseModel):
    """文章模型"""
    title: str = Field(description="文章標題")
    summary: str = Field(description="文章摘要")
    tags: List[str] = Field(description="文章標籤")
    estimated_reading_time: int = Field(description="預計閱讀時間（分鐘）")


@marvin.fn
def analyze_article(article_text: str) -> Article:
    """
    分析文章並提取結構化信息

    Args:
        article_text: 文章內容

    Returns:
        Article 對象，包含標題、摘要、標籤和閱讀時間
    """


class Conversation(BaseModel):
    """對話分析模型"""
    participants: List[str] = Field(description="參與者列表")
    topic: str = Field(description="對話主題")
    sentiment: str = Field(description="整體情感")
    key_points: List[str] = Field(description="關鍵要點")


@marvin.fn
def analyze_conversation(conversation: str) -> Conversation:
    """
    分析對話內容

    Args:
        conversation: 對話文本

    Returns:
        Conversation 對象
    """


def example_complex_returns():
    """示例 3: 複雜類型返回值"""
    print("\n" + "="*60)
    print("示例 3: 複雜類型返回值")
    print("="*60)

    try:
        # 分析文章
        article_text = """
        人工智能的發展正在改變我們的生活方式。從智能助手到自動駕駛，
        AI 技術已經滲透到各個領域。機器學習算法使得計算機能夠從數據中
        學習，而深度學習則讓 AI 系統能夠處理更複雜的任務。未來，AI 將
        在醫療、教育、交通等領域發揮更大的作用，為人類社會帶來更多便利。
        """

        article = analyze_article(article_text)
        print(f"文章分析:")
        print(f"  標題: {article.title}")
        print(f"  摘要: {article.summary}")
        print(f"  標籤: {', '.join(article.tags)}")
        print(f"  閱讀時間: {article.estimated_reading_time} 分鐘\n")

        # 分析對話
        conversation_text = """
        張三: 嘿，你聽說公司要推出新產品了嗎？
        李四: 是的！聽說是一款 AI 助手，很期待。
        張三: 我也是，希望能提高工作效率。
        李四: 下週應該就會發布了，我們拿到後一起試試？
        張三: 好主意！
        """

        conversation = analyze_conversation(conversation_text)
        print(f"對話分析:")
        print(f"  參與者: {', '.join(conversation.participants)}")
        print(f"  主題: {conversation.topic}")
        print(f"  情感: {conversation.sentiment}")
        print(f"  關鍵要點:")
        for point in conversation.key_points:
            print(f"    - {point}")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 帶預設值的函數 ====================

@marvin.fn
def generate_text(
    topic: str,
    length: int = 100,
    style: str = "neutral",
    language: str = "中文"
) -> str:
    """
    生成指定主題的文本

    Args:
        topic: 文本主題
        length: 文本長度（字數）
        style: 寫作風格（neutral/formal/casual/humorous）
        language: 語言

    Returns:
        生成的文本
    """


@marvin.fn
def summarize_text(
    text: str,
    max_length: Optional[int] = None,
    bullet_points: bool = False
) -> str:
    """
    總結文本

    Args:
        text: 要總結的文本
        max_length: 摘要最大長度（字數），None 表示自動決定
        bullet_points: 是否使用要點形式

    Returns:
        文本摘要
    """


def example_default_parameters():
    """示例 4: 帶預設值的函數"""
    print("\n" + "="*60)
    print("示例 4: 帶預設值的函數")
    print("="*60)

    try:
        # 使用預設參數
        text1 = generate_text("機器學習")
        print(f"預設參數生成:\n{text1}\n")

        # 自定義參數
        text2 = generate_text(
            topic="機器學習",
            length=200,
            style="humorous",
            language="中文"
        )
        print(f"自定義參數生成:\n{text2}\n")

        # 總結文本 - 段落形式
        long_text = """
        深度學習是機器學習的一個分支，它使用多層神經網絡來學習數據的
        表示。深度學習在圖像識別、語音識別、自然語言處理等領域取得了
        突破性進展。卷積神經網絡（CNN）特別適合處理圖像數據，而循環
        神經網絡（RNN）和 Transformer 則在處理序列數據方面表現出色。
        """

        summary1 = summarize_text(long_text, max_length=50)
        print(f"段落摘要:\n{summary1}\n")

        # 總結文本 - 要點形式
        summary2 = summarize_text(long_text, bullet_points=True)
        print(f"要點摘要:\n{summary2}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 多返回值類型 ====================

class ProcessResult(BaseModel):
    """處理結果模型"""
    success: bool
    message: str
    data: Optional[Dict] = None


@marvin.fn
def process_command(command: str) -> ProcessResult:
    """
    處理用戶命令

    Args:
        command: 用戶輸入的命令

    Returns:
        ProcessResult 對象，包含執行結果
    """


def example_result_types():
    """示例 5: 多返回值類型"""
    print("\n" + "="*60)
    print("示例 5: 多返回值類型")
    print("="*60)

    try:
        commands = [
            "創建新用戶 admin",
            "刪除文件 important.txt",
            "查詢用戶列表"
        ]

        for cmd in commands:
            result = process_command(cmd)
            status = "✅" if result.success else "❌"
            print(f"{status} 命令: {cmd}")
            print(f"   消息: {result.message}")
            if result.data:
                print(f"   數據: {result.data}")
            print()

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 鏈式 AI 函數 ====================

@marvin.fn
def extract_facts(text: str) -> List[str]:
    """從文本中提取事實陳述"""


@marvin.fn
def verify_fact(fact: str) -> Dict[str, Union[bool, str]]:
    """
    驗證事實的真實性

    Returns:
        包含 'is_likely_true' 和 'reasoning' 的字典
    """


def example_chained_functions():
    """示例 6: 鏈式 AI 函數"""
    print("\n" + "="*60)
    print("示例 6: 鏈式 AI 函數")
    print("="*60)

    try:
        # 原始文本
        text = """
        地球是圓的，月球繞著地球轉。太陽是太陽系的中心。
        水在100攝氏度時沸騰。人類需要氧氣才能生存。
        """

        # 步驟 1: 提取事實
        facts = extract_facts(text)
        print("提取的事實:")
        for i, fact in enumerate(facts, 1):
            print(f"  {i}. {fact}")

        # 步驟 2: 驗證事實（只驗證前3個）
        print("\n事實驗證:")
        for fact in facts[:3]:
            verification = verify_fact(fact)
            status = "✅" if verification.get("is_likely_true") else "❌"
            print(f"{status} {fact}")
            print(f"   理由: {verification.get('reasoning')}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 錯誤處理 ====================

@marvin.fn
def strict_parser(data: str) -> Dict[str, int]:
    """
    嚴格解析數據為字典，值必須是整數

    Args:
        data: 輸入數據

    Returns:
        字典，鍵為字符串，值為整數
    """


def example_error_handling():
    """示例 7: 錯誤處理"""
    print("\n" + "="*60)
    print("示例 7: 錯誤處理")
    print("="*60)

    try:
        # 正常情況
        result = strict_parser("年齡: 25, 身高: 175, 體重: 70")
        print(f"✅ 成功解析: {result}")

    except marvin.exceptions.MarvinError as e:
        print(f"❌ Marvin 錯誤: {e}")
    except Exception as e:
        print(f"❌ 其他錯誤: {e}")

    try:
        # 可能失敗的情況
        result = strict_parser("這是一些隨機文本")
        print(f"結果: {result}")

    except marvin.exceptions.MarvinError as e:
        print(f"⚠️ 預期的 Marvin 錯誤: {type(e).__name__}")
    except Exception as e:
        print(f"❌ 其他錯誤: {e}")


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║        Marvin AI 函數詳解                ║
╚══════════════════════════════════════════╝

@marvin.fn 裝飾器核心特性:
✅ 自動生成 AI 實現
✅ 類型安全
✅ 文檔字符串作為提示
✅ 支持複雜類型
✅ 可組合和鏈式調用
    """)

    # 檢查環境
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 請設置 OPENAI_API_KEY 環境變量")
        return

    # 配置 Marvin
    marvin.settings.openai.api_key = os.getenv("OPENAI_API_KEY")

    # 運行示例
    example_basic_functions()
    example_detailed_prompts()
    example_complex_returns()
    example_default_parameters()
    example_result_types()
    example_chained_functions()
    example_error_handling()

    print("\n" + "="*60)
    print("✅ 所有示例運行完成！")
    print("="*60)


if __name__ == "__main__":
    main()
