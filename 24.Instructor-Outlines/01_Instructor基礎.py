"""
Instructor 基礎範例
====================

本範例展示 Instructor 的基本使用方法，包括：
1. 基本設定和初始化
2. 定義 Pydantic 模型
3. 從 LLM 提取結構化資料
4. 多種提供商的使用（OpenAI、Anthropic）

Instructor 是一個強大的函式庫，讓您能夠從 LLM 中可靠地提取結構化資料。
它使用 Pydantic 進行資料驗證和型別安全。
"""

import os
from typing import List
from pydantic import BaseModel, Field
import instructor

# ============================================================================
# 範例 1：基本使用 - OpenAI
# ============================================================================

def example_basic_openai():
    """使用 OpenAI 的基本 Instructor 範例"""
    print("=" * 60)
    print("範例 1：OpenAI 基本使用")
    print("=" * 60)

    try:
        from openai import OpenAI

        # 定義資料模型
        class User(BaseModel):
            """使用者資訊模型"""
            name: str = Field(description="使用者的全名")
            age: int = Field(description="使用者的年齡")
            email: str = Field(description="使用者的電子郵件地址")

        # 初始化 Instructor 客戶端
        # 這會包裝標準的 OpenAI 客戶端，添加結構化輸出功能
        client = instructor.from_openai(OpenAI())

        # 使用 Instructor 進行結構化提取
        # response_model 參數指定我們期望的輸出結構
        user = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_model=User,
            messages=[
                {
                    "role": "user",
                    "content": "提取以下資訊：張小明今年 28 歲，email 是 xiaoming@example.com"
                }
            ]
        )

        print(f"\n提取的使用者資訊：")
        print(f"姓名：{user.name}")
        print(f"年齡：{user.age}")
        print(f"Email：{user.email}")
        print(f"\nPydantic 模型：{user}")
        print(f"JSON 格式：{user.model_dump_json(indent=2)}")

    except ImportError:
        print("❌ 請先安裝 openai: pip install openai")
    except Exception as e:
        print(f"❌ 錯誤：{e}")
        print("提示：請確保已設定 OPENAI_API_KEY 環境變數")


# ============================================================================
# 範例 2：使用 Anthropic Claude
# ============================================================================

def example_anthropic():
    """使用 Anthropic Claude 的 Instructor 範例"""
    print("\n" + "=" * 60)
    print("範例 2：Anthropic Claude 使用")
    print("=" * 60)

    try:
        from anthropic import Anthropic

        # 定義產品資訊模型
        class Product(BaseModel):
            """產品資訊模型"""
            name: str = Field(description="產品名稱")
            price: float = Field(description="產品價格（美元）")
            category: str = Field(description="產品類別")
            in_stock: bool = Field(description="是否有庫存")

        # 初始化 Anthropic 客戶端
        client = instructor.from_anthropic(Anthropic())

        # 提取產品資訊
        product = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            response_model=Product,
            messages=[
                {
                    "role": "user",
                    "content": "iPhone 15 Pro 售價 999 美元，屬於電子產品類別，目前有貨"
                }
            ]
        )

        print(f"\n提取的產品資訊：")
        print(f"產品名稱：{product.name}")
        print(f"價格：${product.price}")
        print(f"類別：{product.category}")
        print(f"庫存狀態：{'有貨' if product.in_stock else '缺貨'}")

    except ImportError:
        print("❌ 請先安裝 anthropic: pip install anthropic")
    except Exception as e:
        print(f"❌ 錯誤：{e}")
        print("提示：請確保已設定 ANTHROPIC_API_KEY 環境變數")


# ============================================================================
# 範例 3：提取多個物件
# ============================================================================

def example_multiple_objects():
    """提取多個結構化物件的範例"""
    print("\n" + "=" * 60)
    print("範例 3：提取多個物件")
    print("=" * 60)

    try:
        from openai import OpenAI

        # 定義單個聯絡人模型
        class Contact(BaseModel):
            """聯絡人資訊"""
            name: str = Field(description="聯絡人姓名")
            phone: str = Field(description="電話號碼")
            role: str = Field(description="職位或角色")

        # 定義聯絡人列表模型
        class ContactList(BaseModel):
            """聯絡人列表"""
            contacts: List[Contact] = Field(description="聯絡人列表")

        client = instructor.from_openai(OpenAI())

        # 從文本中提取多個聯絡人
        result = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_model=ContactList,
            messages=[
                {
                    "role": "user",
                    "content": """
                    從以下文本提取所有聯絡人資訊：

                    公司通訊錄：
                    - 王經理，電話 0912-345-678，總經理
                    - 李秘書，電話 0923-456-789，行政秘書
                    - 陳工程師，電話 0934-567-890，技術主管
                    """
                }
            ]
        )

        print(f"\n成功提取 {len(result.contacts)} 位聯絡人：\n")
        for i, contact in enumerate(result.contacts, 1):
            print(f"{i}. {contact.name}")
            print(f"   電話：{contact.phone}")
            print(f"   職位：{contact.role}\n")

    except Exception as e:
        print(f"❌ 錯誤：{e}")


# ============================================================================
# 範例 4：模式（Mode）選擇
# ============================================================================

def example_modes():
    """Instructor 不同模式的範例"""
    print("\n" + "=" * 60)
    print("範例 4：Instructor 模式")
    print("=" * 60)

    try:
        from openai import OpenAI
        import instructor

        class Person(BaseModel):
            name: str
            age: int

        # Mode.TOOLS - 使用 OpenAI 的 function calling（預設，推薦）
        print("\n1. TOOLS 模式（推薦）：")
        client_tools = instructor.from_openai(
            OpenAI(),
            mode=instructor.Mode.TOOLS  # 使用 function calling
        )

        # Mode.JSON - 使用 JSON mode
        print("2. JSON 模式：")
        client_json = instructor.from_openai(
            OpenAI(),
            mode=instructor.Mode.JSON  # 使用 JSON mode
        )

        # Mode.MD_JSON - 使用 Markdown JSON（適用於不支援 function calling 的模型）
        print("3. MD_JSON 模式（相容性最佳）：")
        client_md = instructor.from_openai(
            OpenAI(),
            mode=instructor.Mode.MD_JSON  # 使用 markdown 包裝的 JSON
        )

        print("\n✅ 不同模式說明：")
        print("- TOOLS: 最可靠，使用 OpenAI function calling")
        print("- JSON: 使用 OpenAI JSON mode，較快但可能不太穩定")
        print("- MD_JSON: 最佳相容性，適用於所有模型")

    except Exception as e:
        print(f"❌ 錯誤：{e}")


# ============================================================================
# 範例 5：基本錯誤處理
# ============================================================================

def example_error_handling():
    """基本的錯誤處理範例"""
    print("\n" + "=" * 60)
    print("範例 5：錯誤處理")
    print("=" * 60)

    try:
        from openai import OpenAI
        from pydantic import ValidationError

        class StrictUser(BaseModel):
            name: str = Field(min_length=2, max_length=50)
            age: int = Field(ge=0, le=150)  # 0-150 歲

        client = instructor.from_openai(OpenAI())

        # 嘗試提取資料（可能會因驗證失敗而重試）
        try:
            user = client.chat.completions.create(
                model="gpt-3.5-turbo",
                response_model=StrictUser,
                messages=[
                    {
                        "role": "user",
                        "content": "提取：小明今年 25 歲"
                    }
                ]
            )
            print(f"✅ 成功提取：{user}")

        except ValidationError as e:
            print(f"❌ 驗證錯誤：{e}")
        except Exception as e:
            print(f"❌ 其他錯誤：{e}")

    except Exception as e:
        print(f"❌ 錯誤：{e}")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """執行所有範例"""
    print("\n" + "🎯" * 30)
    print("Instructor 基礎範例")
    print("🎯" * 30)

    print("\n📝 Instructor 是什麼？")
    print("-" * 60)
    print("Instructor 是一個 Python 函式庫，讓您能夠從 LLM 中")
    print("可靠地提取結構化、型別安全的資料。")
    print("\n主要特點：")
    print("✅ 使用 Pydantic 進行資料驗證")
    print("✅ 自動重試失敗的驗證")
    print("✅ 支援多種 LLM 提供商")
    print("✅ 完整的型別提示和 IDE 支援")
    print("-" * 60)

    # 檢查 API 金鑰
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  警告：未設定 OPENAI_API_KEY 環境變數")
        print("某些範例可能無法執行")

    # 執行範例
    example_basic_openai()
    example_anthropic()
    example_multiple_objects()
    example_modes()
    example_error_handling()

    print("\n" + "=" * 60)
    print("✅ 所有範例執行完畢！")
    print("=" * 60)
    print("\n💡 下一步：")
    print("- 查看 02_Pydantic驗證.py 學習資料驗證")
    print("- 查看 03_複雜結構.py 學習嵌套模型")
    print("- 閱讀官方文檔：https://python.useinstructor.com/")


if __name__ == "__main__":
    main()
