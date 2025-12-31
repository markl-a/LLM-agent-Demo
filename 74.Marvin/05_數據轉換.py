"""
Marvin 數據轉換示例

本示例展示：
1. marvin.cast() 的使用
2. 格式轉換
3. 數據清理
4. 單位轉換
5. 跨語言轉換

運行方式：
    python 05_數據轉換.py
"""

import os
import marvin
from typing import List, Dict
from pydantic import BaseModel
from datetime import datetime


# ==================== 基本數據轉換 ====================

def example_basic_casting():
    """示例 1: 基本數據轉換"""
    print("\n" + "="*60)
    print("示例 1: 基本數據轉換")
    print("="*60)

    try:
        # 字符串轉數字
        result1 = marvin.cast("一百二十三", target=int)
        print(f"✅ '一百二十三' → {result1} (int)")

        result2 = marvin.cast("三點一四一五九", target=float)
        print(f"✅ '三點一四一五九' → {result2} (float)")

        # 帶單位的數字
        result3 = marvin.cast("100美元", target=float)
        print(f"✅ '100美元' → {result3} (float)")

        result4 = marvin.cast("兩公斤", target=float)
        print(f"✅ '兩公斤' → {result4} (float)")

        # 布爾值轉換
        result5 = marvin.cast("是的", target=bool)
        print(f"✅ '是的' → {result5} (bool)")

        result6 = marvin.cast("否", target=bool)
        print(f"✅ '否' → {result6} (bool)\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 格式轉換 ====================

def example_format_conversion():
    """示例 2: 格式轉換"""
    print("\n" + "="*60)
    print("示例 2: 格式轉換")
    print("="*60)

    try:
        # 日期格式轉換
        dates = [
            "2025年1月15日",
            "Jan 15, 2025",
            "15/01/2025",
            "2025-01-15"
        ]

        print("日期格式標準化:")
        for date_str in dates:
            standard = marvin.cast(date_str, target=str, instructions="轉換為 YYYY-MM-DD 格式")
            print(f"  {date_str:<20} → {standard}")

        # 時間格式轉換
        print("\n時間格式轉換:")
        times = [
            "下午3點",
            "15:30",
            "3:30 PM",
            "三點半"
        ]

        for time_str in times:
            standard = marvin.cast(time_str, target=str, instructions="轉換為 HH:MM 24小時制")
            print(f"  {time_str:<20} → {standard}")

        # 電話號碼格式化
        print("\n電話號碼格式化:")
        phones = [
            "13812345678",
            "138 1234 5678",
            "+86 138-1234-5678",
            "(138) 1234-5678"
        ]

        for phone in phones:
            formatted = marvin.cast(phone, target=str, instructions="格式化為 XXX-XXXX-XXXX")
            print(f"  {phone:<25} → {formatted}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 數據清理 ====================

def example_data_cleaning():
    """示例 3: 數據清理"""
    print("\n" + "="*60)
    print("示例 3: 數據清理")
    print("="*60)

    try:
        # 移除特殊字符
        messy_texts = [
            "Hello!!!  World???",
            "價格：$$$100元",
            "電話: +86-138****5678",
            "郵箱: user@@@example.com"
        ]

        print("清理特殊字符:")
        for text in messy_texts:
            cleaned = marvin.cast(text, target=str, instructions="移除多餘的特殊字符和空格")
            print(f"  {text:<30} → {cleaned}")

        # 標準化文本
        print("\n文本標準化:")
        texts = [
            "   hello   world   ",
            "HELLO WORLD",
            "HeLLo WoRLd"
        ]

        for text in texts:
            normalized = marvin.cast(text, target=str, instructions="轉為小寫並移除多餘空格")
            print(f"  '{text}' → '{normalized}'\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 單位轉換 ====================

class Measurement(BaseModel):
    """測量值"""
    value: float
    unit: str


def example_unit_conversion():
    """示例 4: 單位轉換"""
    print("\n" + "="*60)
    print("示例 4: 單位轉換")
    print("="*60)

    try:
        # 長度轉換
        print("長度轉換:")
        lengths = [
            "100厘米",
            "5英尺",
            "2米",
            "10英寸"
        ]

        for length in lengths:
            meters = marvin.cast(length, target=float, instructions="轉換為米")
            print(f"  {length:<15} → {meters} 米")

        # 重量轉換
        print("\n重量轉換:")
        weights = [
            "500克",
            "2磅",
            "1公斤",
            "16盎司"
        ]

        for weight in weights:
            kg = marvin.cast(weight, target=float, instructions="轉換為公斤")
            print(f"  {weight:<15} → {kg} 公斤")

        # 溫度轉換
        print("\n溫度轉換:")
        temps = [
            "32華氏度",
            "0攝氏度",
            "100°F",
            "25°C"
        ]

        for temp in temps:
            celsius = marvin.cast(temp, target=float, instructions="轉換為攝氏度")
            print(f"  {temp:<15} → {celsius}°C\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 貨幣轉換 ====================

class Money(BaseModel):
    """貨幣"""
    amount: float
    currency: str


def example_currency_conversion():
    """示例 5: 貨幣轉換"""
    print("\n" + "="*60)
    print("示例 5: 貨幣處理")
    print("="*60)

    try:
        # 解析貨幣
        print("貨幣解析:")
        amounts = [
            "$100",
            "¥500",
            "€50",
            "£30",
            "100美元",
            "500人民幣"
        ]

        for amount in amounts:
            money = marvin.cast(amount, target=Money)
            print(f"  {amount:<15} → {money.amount} {money.currency}")

        # 標準化金額
        print("\n金額標準化:")
        messy_amounts = [
            "一百美元",
            "$100.50",
            "100.5美金",
            "USD 100.50"
        ]

        for amount in messy_amounts:
            standard = marvin.cast(
                amount,
                target=str,
                instructions="轉換為 '$XX.XX' 格式"
            )
            print(f"  {amount:<20} → {standard}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 列表轉換 ====================

def example_list_transformation():
    """示例 6: 列表轉換"""
    print("\n" + "="*60)
    print("示例 6: 列表轉換")
    print("="*60)

    try:
        # 字符串轉列表
        text = "蘋果、香蕉、橙子和葡萄"
        fruits = marvin.cast(text, target=List[str])
        print(f"文本轉列表:")
        print(f"  輸入: {text}")
        print(f"  輸出: {fruits}\n")

        # 混亂列表標準化
        messy_list = "1.蘋果  2)香蕉  3、橙子  4-葡萄"
        clean_list = marvin.cast(messy_list, target=List[str])
        print(f"列表標準化:")
        print(f"  輸入: {messy_list}")
        print(f"  輸出: {clean_list}\n")

        # 數字列表提取
        text = "成績分別是95分、87分、92分和88分"
        scores = marvin.cast(text, target=List[int])
        print(f"數字提取:")
        print(f"  輸入: {text}")
        print(f"  輸出: {scores}")
        print(f"  平均: {sum(scores)/len(scores):.1f}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 結構轉換 ====================

class Address(BaseModel):
    """地址"""
    country: str
    city: str
    street: str
    postal_code: str


def example_structure_conversion():
    """示例 7: 結構轉換"""
    print("\n" + "="*60)
    print("示例 7: 結構轉換")
    print("="*60)

    try:
        # 非結構化文本轉結構化
        addresses = [
            "中國北京市朝陽區某某街123號 100000",
            "北京朝陽區某某路456號, 郵編: 100001",
            "100002, 中國, 北京, 海淀區中關村大街789號"
        ]

        print("地址結構化:")
        for addr_text in addresses:
            addr = marvin.cast(addr_text, target=Address)
            print(f"\n  原始: {addr_text}")
            print(f"  結構化:")
            print(f"    國家: {addr.country}")
            print(f"    城市: {addr.city}")
            print(f"    街道: {addr.street}")
            print(f"    郵編: {addr.postal_code}")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 跨語言轉換 ====================

def example_cross_language():
    """示例 8: 跨語言轉換"""
    print("\n" + "="*60)
    print("示例 8: 跨語言轉換")
    print("="*60)

    try:
        # 數字的跨語言轉換
        numbers = [
            "一百二十三",
            "one hundred twenty three",
            "123",
            "百二十三"
        ]

        print("數字標準化:")
        for num in numbers:
            standard = marvin.cast(num, target=int)
            print(f"  {num:<30} → {standard}")

        # 日期的跨語言轉換
        print("\n日期標準化:")
        dates = [
            "2025年1月15日",
            "January 15, 2025",
            "15 janvier 2025",  # 法語
            "2025-01-15"
        ]

        for date in dates:
            standard = marvin.cast(
                date,
                target=str,
                instructions="轉換為 YYYY-MM-DD 格式"
            )
            print(f"  {date:<25} → {standard}\n")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║        Marvin 數據轉換示例                ║
╚══════════════════════════════════════════╝

marvin.cast() 功能:
✅ 智能數據轉換
✅ 格式標準化
✅ 數據清理
✅ 單位轉換
✅ 跨語言支持
    """)

    # 檢查環境
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 請設置 OPENAI_API_KEY 環境變量")
        return

    # 配置 Marvin
    marvin.settings.openai.api_key = os.getenv("OPENAI_API_KEY")

    # 運行示例
    example_basic_casting()
    example_format_conversion()
    example_data_cleaning()
    example_unit_conversion()
    example_currency_conversion()
    example_list_transformation()
    example_structure_conversion()
    example_cross_language()

    print("\n" + "="*60)
    print("✅ 所有示例運行完成！")
    print("="*60)


if __name__ == "__main__":
    main()
