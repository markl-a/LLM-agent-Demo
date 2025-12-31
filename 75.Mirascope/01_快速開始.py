"""
Mirascope 快速開始示例

本示例展示：
1. Mirascope 基本概念
2. 環境配置
3. 第一個調用
4. 基本使用模式

運行方式：
    python 01_快速開始.py

環境要求：
    export OPENAI_API_KEY='your-key-here'
"""

import os
from mirascope.openai import OpenAICall
from pydantic import BaseModel
from typing import List


# ==================== 環境配置 ====================

def setup_environment():
    """設置環境"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ 警告: OPENAI_API_KEY 未設置")
        return False
    print("✅ 環境配置成功")
    return True


# ==================== 第一個 Mirascope 調用 ====================

class SimpleGreeting(OpenAICall):
    """簡單的問候調用"""
    prompt_template = "用友好的方式向用戶問好"


class PersonalizedGreeting(OpenAICall):
    """個性化問候"""
    prompt_template = "向{name}問好，並祝他{wish}"

    name: str
    wish: str = "今天愉快"


def example_basic_calls():
    """示例 1: 基本調用"""
    print("\n" + "="*60)
    print("示例 1: 基本調用")
    print("="*60)

    try:
        # 簡單調用
        response = SimpleGreeting().call()
        print(f"\n簡單問候:\n{response.content}\n")

        # 帶參數的調用
        response = PersonalizedGreeting(
            name="小明",
            wish="工作順利"
        ).call()
        print(f"個性化問候:\n{response.content}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 不同類型的提示 ====================

class Translator(OpenAICall):
    """翻譯器"""
    prompt_template = "將以下文本翻譯成{target_language}：\n{text}"

    text: str
    target_language: str


class Summarizer(OpenAICall):
    """摘要生成器"""
    prompt_template = """
    請總結以下文本的主要內容：

    {text}

    要求：簡潔明了，不超過{max_length}字
    """

    text: str
    max_length: int = 100


def example_different_prompts():
    """示例 2: 不同類型的提示"""
    print("\n" + "="*60)
    print("示例 2: 不同類型的提示")
    print("="*60)

    try:
        # 翻譯
        response = Translator(
            text="Hello, how are you?",
            target_language="中文"
        ).call()
        print(f"翻譯結果:\n{response.content}\n")

        # 摘要
        long_text = """
        人工智能（AI）正在迅速改變我們的生活和工作方式。
        從智能助手到自動駕駛，AI 技術已經滲透到各個領域。
        機器學習和深度學習是 AI 的核心技術，使計算機能夠
        從數據中學習並做出決策。未來，AI 將在醫療、教育、
        交通等領域發揮更大的作用。
        """

        response = Summarizer(
            text=long_text,
            max_length=50
        ).call()
        print(f"摘要:\n{response.content}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 結構化輸出 ====================

class Person(BaseModel):
    """人物模型"""
    name: str
    age: int
    occupation: str


class PersonExtractor(OpenAICall):
    """人物信息提取器"""
    prompt_template = "從以下文本中提取人物信息：{text}"

    text: str
    call_params = {"response_model": Person}


def example_structured_output():
    """示例 3: 結構化輸出"""
    print("\n" + "="*60)
    print("示例 3: 結構化輸出")
    print("="*60)

    try:
        # 提取人物信息
        text = "張三今年30歲，是一名軟件工程師。"
        person = PersonExtractor(text=text).call()

        print(f"提取的信息:")
        print(f"  姓名: {person.name}")
        print(f"  年齡: {person.age}")
        print(f"  職業: {person.occupation}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 配置模型參數 ====================

class CreativeWriter(OpenAICall):
    """創意寫作"""
    prompt_template = "寫一個關於{topic}的短故事"

    topic: str
    call_params = {
        "model": "gpt-3.5-turbo",
        "temperature": 0.9,  # 高創造性
        "max_tokens": 200
    }


class FactualAnswer(OpenAICall):
    """事實性回答"""
    prompt_template = "請回答：{question}"

    question: str
    call_params = {
        "model": "gpt-3.5-turbo",
        "temperature": 0.1,  # 低創造性，更準確
        "max_tokens": 150
    }


def example_model_params():
    """示例 4: 配置模型參數"""
    print("\n" + "="*60)
    print("示例 4: 配置模型參數")
    print("="*60)

    try:
        # 創意寫作
        response = CreativeWriter(topic="未來城市").call()
        print(f"創意故事:\n{response.content}\n")

        # 事實性回答
        response = FactualAnswer(
            question="什麼是人工智能？"
        ).call()
        print(f"事實性回答:\n{response.content}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 訪問響應詳情 ====================

class DetailedCall(OpenAICall):
    """詳細調用"""
    prompt_template = "分析：{text}"

    text: str


def example_response_details():
    """示例 5: 訪問響應詳情"""
    print("\n" + "="*60)
    print("示例 5: 訪問響應詳情")
    print("="*60)

    try:
        response = DetailedCall(text="Hello World").call()

        print("響應詳情:")
        print(f"  內容: {response.content[:50]}...")
        print(f"  模型: {response.model}")

        # 使用統計
        if hasattr(response, 'usage'):
            print(f"  Token 使用:")
            print(f"    提示: {response.usage.get('prompt_tokens', 'N/A')}")
            print(f"    完成: {response.usage.get('completion_tokens', 'N/A')}")
            print(f"    總計: {response.usage.get('total_tokens', 'N/A')}")

        print()

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 鏈式調用 ====================

class Analyzer(OpenAICall):
    """分析器"""
    prompt_template = "分析以下文本的情感：{text}"
    text: str


class Responder(OpenAICall):
    """響應器"""
    prompt_template = """
    基於以下情感分析：{sentiment}

    為原文本生成適當的回應：{original_text}
    """

    sentiment: str
    original_text: str


def example_chained_calls():
    """示例 6: 鏈式調用"""
    print("\n" + "="*60)
    print("示例 6: 鏈式調用")
    print("="*60)

    try:
        text = "這個產品太棒了！我非常滿意！"

        # 步驟 1: 分析情感
        sentiment_response = Analyzer(text=text).call()
        print(f"情感分析: {sentiment_response.content}\n")

        # 步驟 2: 生成回應
        response = Responder(
            sentiment=sentiment_response.content,
            original_text=text
        ).call()
        print(f"生成的回應: {response.content}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 批量處理 ====================

class BatchProcessor(OpenAICall):
    """批量處理器"""
    prompt_template = "分類：{text}"
    text: str


def example_batch_processing():
    """示例 7: 批量處理"""
    print("\n" + "="*60)
    print("示例 7: 批量處理")
    print("="*60)

    try:
        texts = [
            "Python 是一門優秀的編程語言",
            "今天天氣真好",
            "股市今日上漲",
            "最新電影上映了"
        ]

        print("批量處理結果:\n")
        for i, text in enumerate(texts, 1):
            response = BatchProcessor(text=text).call()
            print(f"{i}. {text[:30]}")
            print(f"   → {response.content[:50]}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║      Mirascope 快速開始示例               ║
╚══════════════════════════════════════════╝

Mirascope 核心特點:
✅ 簡潔的類定義
✅ 靈活的提示模板
✅ 結構化輸出
✅ 類型安全
✅ 易於使用
    """)

    # 設置環境
    if not setup_environment():
        print("\n❌ 請先設置 OPENAI_API_KEY 環境變量")
        return

    # 運行示例
    example_basic_calls()
    example_different_prompts()
    example_structured_output()
    example_model_params()
    example_response_details()
    example_chained_calls()
    example_batch_processing()

    print("\n" + "="*60)
    print("✅ 所有示例運行完成！")
    print("="*60)
    print("\n下一步: 查看 02_提示模板.py 了解更多模板功能")


if __name__ == "__main__":
    main()
