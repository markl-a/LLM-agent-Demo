#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Guidance 正則約束示例
====================================================

本模塊展示如何使用正則表達式約束來控制 LLM 輸出格式:
1. 基本正則表達式約束
2. 常見格式驗證 (郵箱、電話、URL)
3. 數字和日期格式
4. 自定義模式匹配
5. 複雜正則組合
6. 代碼格式約束
7. 數據提取應用
8. 表單驗證

正則約束是 Guidance 最強大的功能之一，能夠在 token 級別
確保輸出嚴格符合指定的模式，實現零錯誤率的格式控制。

作者: Guidance 示例團隊
日期: 2025-01-01
"""

import os
import sys
import re
from typing import List, Dict, Any, Optional, Pattern
import json
from datetime import datetime

try:
    from guidance import models, gen, select, regex
    import guidance
except ImportError:
    print("錯誤: 請先安裝 guidance 庫")
    sys.exit(1)


class RegexConstraintDemo:
    """
    正則約束演示類

    展示 Guidance 正則表達式約束的各種應用場景。

    Attributes:
        model_name: 模型名稱
        api_key: API 密鑰
        validation_results: 驗證結果記錄
    """

    def __init__(self, model_name: str = "gpt-4", api_key: Optional[str] = None):
        """初始化正則約束演示器"""
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.validation_results: List[Dict] = []

        # 常用正則模式
        self.patterns = {
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "phone": r"\d{3}-\d{3}-\d{4}",
            "phone_intl": r"\+\d{1,3}-\d{3,4}-\d{4,}",
            "url": r"https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?",
            "ipv4": r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
            "date_iso": r"\d{4}-\d{2}-\d{2}",
            "date_us": r"\d{2}/\d{2}/\d{4}",
            "time_24h": r"\d{2}:\d{2}",
            "hex_color": r"#[0-9A-Fa-f]{6}",
            "uuid": r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            "mac_address": r"([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}",
            "credit_card": r"\d{4}-\d{4}-\d{4}-\d{4}",
            "zip_code": r"\d{5}",
            "ssn": r"\d{3}-\d{2}-\d{4}",
        }

    def example_basic_regex(self) -> None:
        """
        示例 1: 基本正則約束

        演示最基本的正則表達式約束用法。
        """
        print(f"\n{'='*60}")
        print("示例 1: 基本正則約束")
        print(f"{'='*60}\n")

        # 數字約束
        print("生成數字:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "請提供一個 1-100 之間的數字: "
        lm += gen(name="number", regex=r"\d{1,3}")

        print(f"生成的數字: {lm['number']}\n")

        # 字母約束
        print("生成英文單詞:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "請提供一個英文單詞 (只包含字母): "
        lm += gen(name="word", regex=r"[a-zA-Z]+")

        print(f"生成的單詞: {lm['word']}\n")

        # 字母數字組合
        print("生成用戶名:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "生成一個用戶名 (3-16位字母數字下劃線): "
        lm += gen(name="username", regex=r"[a-z0-9_]{3,16}")

        print(f"用戶名: {lm['username']}\n")

        # 指定長度
        print("生成驗證碼:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "生成一個6位數字驗證碼: "
        lm += gen(name="code", regex=r"\d{6}")

        print(f"驗證碼: {lm['code']}\n")

    def example_common_formats(self) -> Dict[str, str]:
        """
        示例 2: 常見格式驗證

        演示郵箱、電話、URL 等常見格式的正則約束。

        Returns:
            生成的格式化數據
        """
        print(f"\n{'='*60}")
        print("示例 2: 常見格式驗證")
        print(f"{'='*60}\n")

        results = {}

        # 郵箱地址
        print("生成郵箱地址:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "請提供一個有效的電子郵箱地址: "
        lm += gen(name="email", regex=self.patterns["email"])
        results["email"] = lm["email"]
        print(f"郵箱: {lm['email']}\n")

        # 電話號碼
        print("生成電話號碼:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "請提供一個電話號碼 (格式: 123-456-7890): "
        lm += gen(name="phone", regex=self.patterns["phone"])
        results["phone"] = lm["phone"]
        print(f"電話: {lm['phone']}\n")

        # URL
        print("生成 URL:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "請提供一個網站 URL: "
        lm += gen(name="url", regex=self.patterns["url"])
        results["url"] = lm["url"]
        print(f"URL: {lm['url']}\n")

        # IP 地址
        print("生成 IP 地址:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "請提供一個 IPv4 地址: "
        lm += gen(name="ip", regex=self.patterns["ipv4"])
        results["ip"] = lm["ip"]
        print(f"IP: {lm['ip']}\n")

        # MAC 地址
        print("生成 MAC 地址:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "請提供一個 MAC 地址: "
        lm += gen(name="mac", regex=self.patterns["mac_address"])
        results["mac"] = lm["mac"]
        print(f"MAC: {lm['mac']}\n")

        return results

    def example_date_time_formats(self) -> None:
        """
        示例 3: 日期時間格式

        演示各種日期和時間格式的約束。
        """
        print(f"\n{'='*60}")
        print("示例 3: 日期時間格式")
        print(f"{'='*60}\n")

        # ISO 8601 日期格式
        print("ISO 8601 日期格式 (YYYY-MM-DD):")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "請提供一個日期 (格式: YYYY-MM-DD): "
        lm += gen(name="date_iso", regex=self.patterns["date_iso"])
        print(f"日期: {lm['date_iso']}\n")

        # 美國日期格式
        print("美國日期格式 (MM/DD/YYYY):")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "請提供一個日期 (格式: MM/DD/YYYY): "
        lm += gen(name="date_us", regex=self.patterns["date_us"])
        print(f"日期: {lm['date_us']}\n")

        # 24小時時間格式
        print("24小時時間格式 (HH:MM):")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "請提供一個時間 (格式: HH:MM): "
        lm += gen(name="time", regex=self.patterns["time_24h"])
        print(f"時間: {lm['time']}\n")

        # 完整時間戳
        print("完整日期時間 (YYYY-MM-DD HH:MM):")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "請提供一個完整的日期時間: "
        lm += gen(name="datetime", regex=r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}")
        print(f"日期時間: {lm['datetime']}\n")

        # 年份範圍
        print("生成年份 (2000-2099):")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "請提供一個21世紀的年份: "
        lm += gen(name="year", regex=r"20\d{2}")
        print(f"年份: {lm['year']}\n")

    def example_number_formats(self) -> None:
        """
        示例 4: 數字格式

        演示各種數字格式的約束，包括整數、小數、貨幣等。
        """
        print(f"\n{'='*60}")
        print("示例 4: 數字格式")
        print(f"{'='*60}\n")

        # 整數
        print("生成正整數:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "請提供一個正整數: "
        lm += gen(name="integer", regex=r"[1-9]\d*")
        print(f"整數: {lm['integer']}\n")

        # 小數 (兩位)
        print("生成小數 (保留兩位):")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "請提供一個小數 (兩位小數): "
        lm += gen(name="decimal", regex=r"\d+\.\d{2}")
        print(f"小數: {lm['decimal']}\n")

        # 貨幣格式
        print("生成貨幣金額 ($X,XXX.XX):")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "請提供一個美元金額: "
        lm += gen(name="currency", regex=r"\$\d{1,3}(,\d{3})*\.\d{2}")
        print(f"金額: {lm['currency']}\n")

        # 百分比
        print("生成百分比:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "請提供一個百分比 (0-100%): "
        lm += gen(name="percentage", regex=r"\d{1,3}%")
        print(f"百分比: {lm['percentage']}\n")

        # 科學記數法
        print("生成科學記數法:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "請用科學記數法表示一個數: "
        lm += gen(name="scientific", regex=r"\d+\.\d+e[+-]?\d+")
        print(f"科學記數法: {lm['scientific']}\n")

        # 負數
        print("生成負數:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "請提供一個負數: "
        lm += gen(name="negative", regex=r"-\d+")
        print(f"負數: {lm['negative']}\n")

    def example_code_formats(self) -> None:
        """
        示例 5: 代碼格式約束

        演示如何約束生成特定格式的代碼片段。
        """
        print(f"\n{'='*60}")
        print("示例 5: 代碼格式約束")
        print(f"{'='*60}\n")

        # Python 變量名
        print("生成 Python 變量名:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "請提供一個合法的 Python 變量名: "
        lm += gen(name="var_name", regex=r"[a-z_][a-z0-9_]*")
        print(f"變量名: {lm['var_name']}\n")

        # Python 函數簽名
        print("生成 Python 函數簽名:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "生成一個簡單的 Python 函數定義: "
        lm += "def "
        lm += gen(name="func_name", regex=r"[a-z_][a-z0-9_]*")
        lm += "("
        lm += gen(name="params", regex=r"[a-z_][a-z0-9_]*(?:, [a-z_][a-z0-9_]*)*")
        lm += "):"
        print(f"函數: def {lm['func_name']}({lm['params']}):\n")

        # 十六進制顏色代碼
        print("生成十六進制顏色代碼:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "請提供一個十六進制顏色代碼: "
        lm += gen(name="color", regex=self.patterns["hex_color"])
        print(f"顏色: {lm['color']}\n")

        # JSON 鍵名
        print("生成 JSON 鍵名:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "生成一個 JSON 鍵名 (駝峰命名): "
        lm += gen(name="json_key", regex=r"[a-z][a-zA-Z0-9]*")
        print(f"JSON 鍵: {lm['json_key']}\n")

        # SQL 表名
        print("生成 SQL 表名:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "生成一個 SQL 表名 (snake_case): "
        lm += gen(name="table_name", regex=r"[a-z][a-z0-9_]*")
        print(f"表名: {lm['table_name']}\n")

        # CSS 類名
        print("生成 CSS 類名:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "生成一個 CSS 類名 (kebab-case): "
        lm += gen(name="css_class", regex=r"[a-z][a-z0-9-]*")
        print(f"CSS 類: {lm['css_class']}\n")

    def example_custom_patterns(self) -> None:
        """
        示例 6: 自定義模式

        演示如何創建和使用自定義的複雜正則模式。
        """
        print(f"\n{'='*60}")
        print("示例 6: 自定義模式")
        print(f"{'='*60}\n")

        # 密碼強度 (至少8位，包含大小寫字母和數字)
        print("生成強密碼:")
        password_pattern = r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}"
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "生成一個強密碼 (至少8位，含大小寫字母和數字): "
        lm += gen(name="password", regex=password_pattern)
        print(f"密碼: {lm['password']}\n")

        # 版本號 (語義化版本)
        print("生成語義化版本號:")
        version_pattern = r"\d+\.\d+\.\d+"
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "生成一個語義化版本號 (major.minor.patch): "
        lm += gen(name="version", regex=version_pattern)
        print(f"版本: {lm['version']}\n")

        # 車牌號 (簡化版)
        print("生成車牌號:")
        plate_pattern = r"[A-Z]{3}-\d{4}"
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "生成一個車牌號 (格式: ABC-1234): "
        lm += gen(name="plate", regex=plate_pattern)
        print(f"車牌: {lm['plate']}\n")

        # 座標 (經緯度)
        print("生成地理座標:")
        coord_pattern = r"\d{1,3}\.\d+, \d{1,3}\.\d+"
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "生成一個地理座標 (lat, lng): "
        lm += gen(name="coords", regex=coord_pattern)
        print(f"座標: {lm['coords']}\n")

        # 信用卡號
        print("生成信用卡號:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "生成一個信用卡號 (格式: XXXX-XXXX-XXXX-XXXX): "
        lm += gen(name="card", regex=self.patterns["credit_card"])
        print(f"卡號: {lm['card']}\n")

        # ISBN (國際標準書號)
        print("生成 ISBN:")
        isbn_pattern = r"978-\d{10}"
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "生成一個 ISBN-13: "
        lm += gen(name="isbn", regex=isbn_pattern)
        print(f"ISBN: {lm['isbn']}\n")

    def example_data_extraction(self) -> Dict[str, Any]:
        """
        示例 7: 數據提取

        演示如何使用正則約束從文本中提取結構化數據。

        Returns:
            提取的數據
        """
        print(f"\n{'='*60}")
        print("示例 7: 數據提取")
        print(f"{'='*60}\n")

        # 從文本中提取聯繫信息
        print("提取聯繫信息:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "請從以下信息中提取聯繫方式:\n"
        lm += "張三，郵箱 zhang@example.com，電話 123-456-7890\n\n"

        lm += "姓名: "
        lm += gen(name="name", regex=r"[一-龥]{2,4}")
        lm += "\n郵箱: "
        lm += gen(name="email", regex=self.patterns["email"])
        lm += "\n電話: "
        lm += gen(name="phone", regex=self.patterns["phone"])

        contact_info = {
            "name": lm["name"],
            "email": lm["email"],
            "phone": lm["phone"]
        }

        print(f"\n提取結果:")
        print(json.dumps(contact_info, indent=2, ensure_ascii=False))

        # 提取產品信息
        print("\n\n提取產品信息:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "從產品描述中提取信息:\n"
        lm += "產品: iPhone 15 Pro，價格 $999.99，發布日期 2023-09-15\n\n"

        lm += "產品名稱: "
        lm += gen(name="product", regex=r"[a-zA-Z0-9 ]+")
        lm += "\n價格: "
        lm += gen(name="price", regex=r"\$\d+\.\d{2}")
        lm += "\n日期: "
        lm += gen(name="date", regex=self.patterns["date_iso"])

        product_info = {
            "product": lm["product"],
            "price": lm["price"],
            "date": lm["date"]
        }

        print(f"\n提取結果:")
        print(json.dumps(product_info, indent=2, ensure_ascii=False))

        # 提取技術規格
        print("\n\n提取技術規格:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "從服務器規格中提取信息:\n"
        lm += "IP: 192.168.1.100，RAM: 16GB，CPU: 8核心\n\n"

        lm += "IP: "
        lm += gen(name="ip", regex=self.patterns["ipv4"])
        lm += "\nRAM: "
        lm += gen(name="ram", regex=r"\d+GB")
        lm += "\nCPU: "
        lm += gen(name="cpu", regex=r"\d+")
        lm += "核心"

        server_specs = {
            "ip": lm["ip"],
            "ram": lm["ram"],
            "cpu_cores": lm["cpu"]
        }

        print(f"\n提取結果:")
        print(json.dumps(server_specs, indent=2, ensure_ascii=False))

        return {
            "contact": contact_info,
            "product": product_info,
            "server": server_specs
        }

    def example_form_validation(self) -> None:
        """
        示例 8: 表單驗證

        演示如何使用正則約束實現表單字段驗證。
        """
        print(f"\n{'='*60}")
        print("示例 8: 表單驗證")
        print(f"{'='*60}\n")

        # 用戶註冊表單
        print("用戶註冊表單:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "請填寫註冊信息:\n\n"

        # 用戶名 (3-16位字母數字)
        lm += "用戶名 (3-16位字母數字): "
        lm += gen(name="username", regex=r"[a-zA-Z0-9]{3,16}")
        lm += "\n"

        # 郵箱
        lm += "郵箱: "
        lm += gen(name="email", regex=self.patterns["email"])
        lm += "\n"

        # 密碼
        lm += "密碼 (至少8位): "
        lm += gen(name="password", regex=r".{8,}")
        lm += "\n"

        # 電話
        lm += "電話 (XXX-XXX-XXXX): "
        lm += gen(name="phone", regex=self.patterns["phone"])
        lm += "\n"

        # 郵遞區號
        lm += "郵遞區號 (5位數字): "
        lm += gen(name="zip", regex=self.patterns["zip_code"])
        lm += "\n"

        print(f"註冊信息:")
        print(f"  用戶名: {lm['username']}")
        print(f"  郵箱: {lm['email']}")
        print(f"  密碼: {'*' * len(lm['password'])}")
        print(f"  電話: {lm['phone']}")
        print(f"  郵遞區號: {lm['zip']}")

        # 信用卡表單
        print("\n\n信用卡信息表單:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "請填寫信用卡信息:\n\n"

        # 卡號
        lm += "卡號 (XXXX-XXXX-XXXX-XXXX): "
        lm += gen(name="card_number", regex=self.patterns["credit_card"])
        lm += "\n"

        # 有效期
        lm += "有效期 (MM/YY): "
        lm += gen(name="expiry", regex=r"\d{2}/\d{2}")
        lm += "\n"

        # CVV
        lm += "CVV (3位數字): "
        lm += gen(name="cvv", regex=r"\d{3}")
        lm += "\n"

        print(f"信用卡信息:")
        print(f"  卡號: {lm['card_number']}")
        print(f"  有效期: {lm['expiry']}")
        print(f"  CVV: {lm['cvv']}")

    def example_complex_patterns(self) -> None:
        """
        示例 9: 複雜模式組合

        演示如何組合多個正則模式創建複雜的約束。
        """
        print(f"\n{'='*60}")
        print("示例 9: 複雜模式組合")
        print(f"{'='*60}\n")

        # 完整地址
        print("生成完整地址:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "街道: "
        lm += gen(name="street", regex=r"\d+ [A-Z][a-z]+ (St|Ave|Rd|Blvd)")
        lm += "\n"

        lm += "城市: "
        lm += gen(name="city", regex=r"[A-Z][a-z]+")
        lm += "\n"

        lm += "州: "
        lm += gen(name="state", regex=r"[A-Z]{2}")
        lm += "\n"

        lm += "郵遞區號: "
        lm += gen(name="zip", regex=r"\d{5}")

        print(f"\n地址:")
        print(f"  {lm['street']}")
        print(f"  {lm['city']}, {lm['state']} {lm['zip']}")

        # 服務器日誌格式
        print("\n\n生成服務器日誌條目:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "生成一條訪問日誌:\n"
        lm += gen(name="ip", regex=self.patterns["ipv4"])
        lm += " - - ["
        lm += gen(name="timestamp", regex=r"\d{2}/[A-Z][a-z]{2}/\d{4}:\d{2}:\d{2}:\d{2}")
        lm += "] \"GET "
        lm += gen(name="path", regex=r"/[a-z/]*")
        lm += " HTTP/1.1\" "
        lm += gen(name="status", regex=r"\d{3}")
        lm += " "
        lm += gen(name="bytes", regex=r"\d+")

        print(f"\n日誌條目:")
        print(f'{lm["ip"]} - - [{lm["timestamp"]}] "GET {lm["path"]} HTTP/1.1" {lm["status"]} {lm["bytes"]}')

        # 配置文件格式
        print("\n\n生成配置文件條目:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        for i in range(3):
            lm += gen(name=f"key_{i}", regex=r"[a-z_]+")
            lm += " = "
            lm += gen(name=f"value_{i}", regex=r'"[^"]*"')
            lm += "\n"

        print(f"\n配置文件:")
        for i in range(3):
            print(f"  {lm[f'key_{i}']} = {lm[f'value_{i}']}")

    def example_validation_pipeline(self) -> Dict[str, bool]:
        """
        示例 10: 驗證流水線

        演示如何構建完整的數據驗證流水線。

        Returns:
            驗證結果
        """
        print(f"\n{'='*60}")
        print("示例 10: 驗證流水線")
        print(f"{'='*60}\n")

        validation_results = {}

        # 驗證郵箱
        print("驗證郵箱格式:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "提供一個郵箱: "
        lm += gen(name="email", regex=self.patterns["email"])

        email = lm["email"]
        is_valid_email = bool(re.match(self.patterns["email"], email))
        validation_results["email"] = is_valid_email
        print(f"  郵箱: {email}")
        print(f"  驗證: {'✓ 通過' if is_valid_email else '✗ 失敗'}\n")

        # 驗證電話
        print("驗證電話格式:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "提供一個電話號碼: "
        lm += gen(name="phone", regex=self.patterns["phone"])

        phone = lm["phone"]
        is_valid_phone = bool(re.match(self.patterns["phone"], phone))
        validation_results["phone"] = is_valid_phone
        print(f"  電話: {phone}")
        print(f"  驗證: {'✓ 通過' if is_valid_phone else '✗ 失敗'}\n")

        # 驗證URL
        print("驗證 URL 格式:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "提供一個 URL: "
        lm += gen(name="url", regex=self.patterns["url"])

        url = lm["url"]
        is_valid_url = bool(re.match(self.patterns["url"], url))
        validation_results["url"] = is_valid_url
        print(f"  URL: {url}")
        print(f"  驗證: {'✓ 通過' if is_valid_url else '✗ 失敗'}\n")

        # 驗證日期
        print("驗證日期格式:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += "提供一個日期: "
        lm += gen(name="date", regex=self.patterns["date_iso"])

        date = lm["date"]
        is_valid_date = bool(re.match(self.patterns["date_iso"], date))
        validation_results["date"] = is_valid_date
        print(f"  日期: {date}")
        print(f"  驗證: {'✓ 通過' if is_valid_date else '✗ 失敗'}\n")

        # 總結
        total = len(validation_results)
        passed = sum(validation_results.values())

        print(f"驗證摘要: {passed}/{total} 通過")

        return validation_results

    def run_all_examples(self) -> None:
        """運行所有示例"""
        print(f"\n{'='*60}")
        print("Guidance 正則約束 - 完整示例")
        print(f"{'='*60}")

        self.example_basic_regex()
        formats = self.example_common_formats()
        self.example_date_time_formats()
        self.example_number_formats()
        self.example_code_formats()
        self.example_custom_patterns()
        extracted_data = self.example_data_extraction()
        self.example_form_validation()
        self.example_complex_patterns()
        validation_results = self.example_validation_pipeline()

        print(f"\n{'='*60}")
        print("執行摘要")
        print(f"{'='*60}")
        print(f"✓ 所有正則約束示例執行完成!")
        print(f"\n生成的格式數據:")
        print(json.dumps(formats, indent=2, ensure_ascii=False))
        print(f"\n驗證結果:")
        print(json.dumps(validation_results, indent=2, ensure_ascii=False))


def main():
    """主函數"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║         Guidance 框架 - 正則約束示例                       ║
    ║                                                            ║
    ║  使用正則表達式確保 LLM 輸出符合精確格式                   ║
    ║  適用於數據提取、表單驗證、格式控制等場景                  ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        return

    demo = RegexConstraintDemo(
        model_name="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    try:
        demo.run_all_examples()
    except KeyboardInterrupt:
        print("\n\n⚠️  用戶中斷執行")
    except Exception as e:
        print(f"\n✗ 執行出錯: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
