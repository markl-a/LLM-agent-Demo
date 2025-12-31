"""
Outlines 正則表達式生成示例
==========================

本示例展示如何使用 Outlines 的正則表達式約束進行結構化生成。

主要內容:
1. 電子郵件格式生成
2. 電話號碼格式生成
3. 日期時間格式生成
4. URL 格式生成
5. 自定義格式生成

作者: Outlines 教學團隊
日期: 2025-01
"""

import outlines
from outlines import models, generate
import torch
from typing import List, Dict, Optional, Tuple, Pattern
import re
import logging
import json
from datetime import datetime
from dataclasses import dataclass
import sys

# ==================== 設置日誌 ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== 正則模式庫 ====================

class RegexPatterns:
    """
    正則模式庫

    包含常用的正則表達式模式
    """

    # 電子郵件
    EMAIL = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    # 電話號碼
    PHONE_US = r"\d{3}-\d{3}-\d{4}"  # 美國格式: 123-456-7890
    PHONE_CN = r"1[3-9]\d{9}"  # 中國大陸: 13912345678
    PHONE_TW = r"09\d{8}"  # 台灣: 0912345678

    # 日期
    DATE_ISO = r"\d{4}-\d{2}-\d{2}"  # ISO 格式: 2024-01-31
    DATE_US = r"\d{2}/\d{2}/\d{4}"  # 美國格式: 01/31/2024
    DATE_CN = r"\d{4}年\d{1,2}月\d{1,2}日"  # 中文格式: 2024年1月31日

    # 時間
    TIME_24H = r"([01]\d|2[0-3]):[0-5]\d:[0-5]\d"  # 24小時制: 23:59:59
    TIME_12H = r"(0?\d|1[0-2]):[0-5]\d (AM|PM)"  # 12小時制: 11:59 PM

    # URL
    URL = r"https?://[a-zA-Z0-9]+([\-\.]{1}[a-zA-Z0-9]+)*\.[a-zA-Z]{2,}(:[0-9]{1,5})?(/.*)?"

    # IP 地址
    IPV4 = r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"

    # MAC 地址
    MAC = r"([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}"

    # 信用卡號
    CREDIT_CARD = r"\d{4}-\d{4}-\d{4}-\d{4}"

    # 郵政編碼
    ZIP_US = r"\d{5}(-\d{4})?"  # 美國: 12345 或 12345-6789
    ZIP_CN = r"\d{6}"  # 中國: 100000

    # 身份證號(簡化)
    ID_CARD_CN = r"[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[0-9Xx]"

    # 顏色代碼
    COLOR_HEX = r"#[0-9A-Fa-f]{6}"
    COLOR_RGB = r"rgb\(\d{1,3}, \d{1,3}, \d{1,3}\)"

    # 文件路徑
    PATH_UNIX = r"(/[a-zA-Z0-9_.-]+)+"
    PATH_WINDOWS = r"[A-Z]:(\\[a-zA-Z0-9_.-]+)+"

    # 版本號
    VERSION_SEMVER = r"\d+\.\d+\.\d+"  # 語義化版本: 1.2.3


# ==================== 正則生成管理器 ====================

class RegexGenerationManager:
    """
    正則生成管理器

    管理基於正則表達式的文本生成
    """

    def __init__(self, model_name: str = "mistralai/Mistral-7B-v0.1"):
        """
        初始化正則生成管理器

        Args:
            model_name: 使用的模型名稱
        """
        self.model_name = model_name
        self.model = None
        self.patterns = RegexPatterns()
        self.load_model()

        logger.info(f"正則生成管理器初始化完成,模型: {model_name}")

    def load_model(self):
        """載入語言模型"""
        try:
            logger.info(f"開始載入模型: {self.model_name}")

            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"使用設備: {device}")

            self.model = models.transformers(
                self.model_name,
                device=device
            )

            logger.info("模型載入完成")

        except Exception as e:
            logger.error(f"模型載入失敗: {str(e)}")
            raise

    def generate_with_regex(
        self,
        prompt: str,
        pattern: str
    ) -> str:
        """
        使用正則表達式約束生成文本

        Args:
            prompt: 輸入提示
            pattern: 正則表達式模式

        Returns:
            符合模式的生成文本
        """
        try:
            logger.info(f"使用正則模式生成: {pattern[:50]}...")

            # 創建正則生成器
            generator = generate.regex(self.model, pattern)

            # 生成結果
            result = generator(prompt)

            # 驗證結果
            if not re.fullmatch(pattern, result):
                logger.warning(f"生成結果不符合正則模式: {result}")

            logger.info(f"生成結果: {result}")
            return result

        except Exception as e:
            logger.error(f"正則生成失敗: {str(e)}")
            raise

    def batch_generate(
        self,
        prompts: List[str],
        pattern: str
    ) -> List[str]:
        """
        批量生成

        Args:
            prompts: 提示列表
            pattern: 正則表達式模式

        Returns:
            生成結果列表
        """
        results = []

        for prompt in prompts:
            result = self.generate_with_regex(prompt, pattern)
            results.append(result)

        return results


# ==================== 電子郵件生成器 ====================

class EmailGenerator:
    """
    電子郵件生成器

    生成符合格式的電子郵件地址
    """

    def __init__(self, manager: RegexGenerationManager):
        """
        初始化電子郵件生成器

        Args:
            manager: 正則生成管理器
        """
        self.manager = manager
        logger.info("電子郵件生成器初始化完成")

    def generate(
        self,
        name: str = "用戶",
        domain_hint: Optional[str] = None
    ) -> str:
        """
        生成電子郵件地址

        Args:
            name: 用戶名稱
            domain_hint: 域名提示

        Returns:
            電子郵件地址
        """
        if domain_hint:
            prompt = f"為{name}生成一個{domain_hint}的郵箱地址"
        else:
            prompt = f"為{name}生成一個郵箱地址"

        email = self.manager.generate_with_regex(
            prompt,
            self.manager.patterns.EMAIL
        )

        return email

    def generate_corporate(self, company: str, employee: str) -> str:
        """
        生成企業郵箱

        Args:
            company: 公司名稱
            employee: 員工名稱

        Returns:
            企業郵箱地址
        """
        prompt = f"為{company}公司的員工{employee}生成企業郵箱"

        email = self.manager.generate_with_regex(
            prompt,
            self.manager.patterns.EMAIL
        )

        return email

    def generate_batch(
        self,
        count: int,
        context: str = "測試用戶"
    ) -> List[str]:
        """
        批量生成郵箱

        Args:
            count: 生成數量
            context: 上下文描述

        Returns:
            郵箱地址列表
        """
        emails = []

        for i in range(count):
            prompt = f"為{context}{i+1}生成郵箱地址"
            email = self.manager.generate_with_regex(
                prompt,
                self.manager.patterns.EMAIL
            )
            emails.append(email)

        return emails


# ==================== 電話號碼生成器 ====================

class PhoneNumberGenerator:
    """
    電話號碼生成器

    生成符合各種格式的電話號碼
    """

    def __init__(self, manager: RegexGenerationManager):
        """
        初始化電話號碼生成器

        Args:
            manager: 正則生成管理器
        """
        self.manager = manager
        logger.info("電話號碼生成器初始化完成")

    def generate_us(self, area_code: Optional[str] = None) -> str:
        """
        生成美國電話號碼

        Args:
            area_code: 區號(可選)

        Returns:
            美國格式電話號碼
        """
        if area_code:
            prompt = f"生成區號為{area_code}的美國電話號碼"
        else:
            prompt = "生成一個美國電話號碼"

        phone = self.manager.generate_with_regex(
            prompt,
            self.manager.patterns.PHONE_US
        )

        return phone

    def generate_cn(self) -> str:
        """
        生成中國大陸電話號碼

        Returns:
            中國大陸手機號碼
        """
        prompt = "生成一個中國大陸手機號碼"

        phone = self.manager.generate_with_regex(
            prompt,
            self.manager.patterns.PHONE_CN
        )

        return phone

    def generate_tw(self) -> str:
        """
        生成台灣電話號碼

        Returns:
            台灣手機號碼
        """
        prompt = "生成一個台灣手機號碼"

        phone = self.manager.generate_with_regex(
            prompt,
            self.manager.patterns.PHONE_TW
        )

        return phone

    def generate_by_region(self, region: str) -> str:
        """
        根據地區生成電話號碼

        Args:
            region: 地區(us/cn/tw)

        Returns:
            對應格式的電話號碼
        """
        patterns = {
            "us": self.manager.patterns.PHONE_US,
            "cn": self.manager.patterns.PHONE_CN,
            "tw": self.manager.patterns.PHONE_TW
        }

        pattern = patterns.get(region.lower(), self.manager.patterns.PHONE_US)
        prompt = f"生成一個{region}的電話號碼"

        phone = self.manager.generate_with_regex(prompt, pattern)

        return phone


# ==================== 日期時間生成器 ====================

class DateTimeGenerator:
    """
    日期時間生成器

    生成符合各種格式的日期時間
    """

    def __init__(self, manager: RegexGenerationManager):
        """
        初始化日期時間生成器

        Args:
            manager: 正則生成管理器
        """
        self.manager = manager
        logger.info("日期時間生成器初始化完成")

    def generate_date_iso(self, event: str = "重要事件") -> str:
        """
        生成 ISO 格式日期

        Args:
            event: 事件描述

        Returns:
            ISO 格式日期(YYYY-MM-DD)
        """
        prompt = f"{event}的日期(ISO格式)"

        date = self.manager.generate_with_regex(
            prompt,
            self.manager.patterns.DATE_ISO
        )

        return date

    def generate_date_us(self, event: str = "重要事件") -> str:
        """
        生成美國格式日期

        Args:
            event: 事件描述

        Returns:
            美國格式日期(MM/DD/YYYY)
        """
        prompt = f"{event}的日期(美國格式)"

        date = self.manager.generate_with_regex(
            prompt,
            self.manager.patterns.DATE_US
        )

        return date

    def generate_date_cn(self, event: str = "重要事件") -> str:
        """
        生成中文格式日期

        Args:
            event: 事件描述

        Returns:
            中文格式日期(YYYY年MM月DD日)
        """
        prompt = f"{event}的日期(中文格式)"

        date = self.manager.generate_with_regex(
            prompt,
            self.manager.patterns.DATE_CN
        )

        return date

    def generate_time_24h(self, activity: str = "活動") -> str:
        """
        生成24小時制時間

        Args:
            activity: 活動描述

        Returns:
            24小時制時間(HH:MM:SS)
        """
        prompt = f"{activity}的時間(24小時制)"

        time = self.manager.generate_with_regex(
            prompt,
            self.manager.patterns.TIME_24H
        )

        return time

    def generate_time_12h(self, activity: str = "活動") -> str:
        """
        生成12小時制時間

        Args:
            activity: 活動描述

        Returns:
            12小時制時間(HH:MM AM/PM)
        """
        prompt = f"{activity}的時間(12小時制)"

        time = self.manager.generate_with_regex(
            prompt,
            self.manager.patterns.TIME_12H
        )

        return time


# ==================== URL 生成器 ====================

class URLGenerator:
    """
    URL 生成器

    生成符合格式的 URL
    """

    def __init__(self, manager: RegexGenerationManager):
        """
        初始化 URL 生成器

        Args:
            manager: 正則生成管理器
        """
        self.manager = manager
        logger.info("URL 生成器初始化完成")

    def generate(
        self,
        description: str,
        protocol: str = "https"
    ) -> str:
        """
        生成 URL

        Args:
            description: 網站描述
            protocol: 協議(http/https)

        Returns:
            URL
        """
        prompt = f"為{description}生成一個{protocol}網址"

        url = self.manager.generate_with_regex(
            prompt,
            self.manager.patterns.URL
        )

        return url

    def generate_api_endpoint(
        self,
        service: str,
        version: str = "v1"
    ) -> str:
        """
        生成 API 端點

        Args:
            service: 服務名稱
            version: API 版本

        Returns:
            API 端點 URL
        """
        prompt = f"為{service}服務生成{version} API端點"

        url = self.manager.generate_with_regex(
            prompt,
            self.manager.patterns.URL
        )

        return url


# ==================== 網絡地址生成器 ====================

class NetworkAddressGenerator:
    """
    網絡地址生成器

    生成 IP、MAC 等網絡地址
    """

    def __init__(self, manager: RegexGenerationManager):
        """
        初始化網絡地址生成器

        Args:
            manager: 正則生成管理器
        """
        self.manager = manager
        logger.info("網絡地址生成器初始化完成")

    def generate_ipv4(self, device: str = "設備") -> str:
        """
        生成 IPv4 地址

        Args:
            device: 設備名稱

        Returns:
            IPv4 地址
        """
        prompt = f"為{device}生成一個IPv4地址"

        ip = self.manager.generate_with_regex(
            prompt,
            self.manager.patterns.IPV4
        )

        return ip

    def generate_mac(self, device: str = "網卡") -> str:
        """
        生成 MAC 地址

        Args:
            device: 設備名稱

        Returns:
            MAC 地址
        """
        prompt = f"為{device}生成一個MAC地址"

        mac = self.manager.generate_with_regex(
            prompt,
            self.manager.patterns.MAC
        )

        return mac


# ==================== 自定義格式生成器 ====================

class CustomFormatGenerator:
    """
    自定義格式生成器

    生成自定義格式的數據
    """

    def __init__(self, manager: RegexGenerationManager):
        """
        初始化自定義格式生成器

        Args:
            manager: 正則生成管理器
        """
        self.manager = manager
        logger.info("自定義格式生成器初始化完成")

    def generate_license_plate(self, region: str = "台灣") -> str:
        """
        生成車牌號

        Args:
            region: 地區

        Returns:
            車牌號
        """
        # 台灣車牌格式: ABC-1234
        pattern = r"[A-Z]{3}-\d{4}"
        prompt = f"生成一個{region}車牌號"

        plate = self.manager.generate_with_regex(prompt, pattern)

        return plate

    def generate_serial_number(self, product: str) -> str:
        """
        生成產品序列號

        Args:
            product: 產品名稱

        Returns:
            序列號
        """
        # 序列號格式: SN-YYYYMMDD-NNNN
        pattern = r"SN-\d{8}-\d{4}"
        prompt = f"為{product}生成序列號"

        serial = self.manager.generate_with_regex(prompt, pattern)

        return serial

    def generate_order_id(self, platform: str = "電商") -> str:
        """
        生成訂單號

        Args:
            platform: 平台名稱

        Returns:
            訂單號
        """
        # 訂單號格式: ORD-YYYYMMDDHHMMSS-NNNN
        pattern = r"ORD-\d{14}-\d{4}"
        prompt = f"為{platform}平台生成訂單號"

        order_id = self.manager.generate_with_regex(prompt, pattern)

        return order_id


# ==================== 驗證器 ====================

class FormatValidator:
    """
    格式驗證器

    驗證生成的數據是否符合正則模式
    """

    @staticmethod
    def validate(text: str, pattern: str) -> Tuple[bool, Optional[str]]:
        """
        驗證文本是否符合模式

        Args:
            text: 待驗證文本
            pattern: 正則模式

        Returns:
            (是否有效, 錯誤信息) 元組
        """
        try:
            if re.fullmatch(pattern, text):
                return True, None
            else:
                return False, f"文本不符合模式: {pattern}"

        except re.error as e:
            return False, f"正則表達式錯誤: {str(e)}"

    @staticmethod
    def batch_validate(
        texts: List[str],
        pattern: str
    ) -> Dict[str, int]:
        """
        批量驗證

        Args:
            texts: 文本列表
            pattern: 正則模式

        Returns:
            驗證統計
        """
        valid_count = 0
        invalid_count = 0

        for text in texts:
            is_valid, _ = FormatValidator.validate(text, pattern)
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1

        return {
            "total": len(texts),
            "valid": valid_count,
            "invalid": invalid_count,
            "success_rate": (valid_count / len(texts)) * 100 if texts else 0
        }


# ==================== 示例運行器 ====================

def run_email_generation_example():
    """運行電子郵件生成示例"""
    print("\n" + "="*60)
    print("示例 1: 電子郵件生成")
    print("="*60)

    manager = RegexGenerationManager()
    generator = EmailGenerator(manager)

    print("\n生成個人郵箱:")
    names = ["張三", "李四", "王五"]
    for name in names:
        email = generator.generate(name)
        print(f"  {name}: {email}")

    print("\n生成企業郵箱:")
    companies = [("科技公司", "工程師"), ("金融公司", "分析師")]
    for company, role in companies:
        email = generator.generate_corporate(company, role)
        print(f"  {company}-{role}: {email}")


def run_phone_generation_example():
    """運行電話號碼生成示例"""
    print("\n" + "="*60)
    print("示例 2: 電話號碼生成")
    print("="*60)

    manager = RegexGenerationManager()
    generator = PhoneNumberGenerator(manager)

    print("\n美國電話號碼:")
    for i in range(3):
        phone = generator.generate_us()
        print(f"  {phone}")

    print("\n中國大陸手機號碼:")
    for i in range(3):
        phone = generator.generate_cn()
        print(f"  {phone}")

    print("\n台灣手機號碼:")
    for i in range(3):
        phone = generator.generate_tw()
        print(f"  {phone}")


def run_datetime_generation_example():
    """運行日期時間生成示例"""
    print("\n" + "="*60)
    print("示例 3: 日期時間生成")
    print("="*60)

    manager = RegexGenerationManager()
    generator = DateTimeGenerator(manager)

    print("\n生成日期(ISO格式):")
    events = ["項目啟動", "產品發布", "會議召開"]
    for event in events:
        date = generator.generate_date_iso(event)
        print(f"  {event}: {date}")

    print("\n生成時間(24小時制):")
    activities = ["早會", "午餐", "下班"]
    for activity in activities:
        time = generator.generate_time_24h(activity)
        print(f"  {activity}: {time}")


def run_custom_format_example():
    """運行自定義格式示例"""
    print("\n" + "="*60)
    print("示例 4: 自定義格式生成")
    print("="*60)

    manager = RegexGenerationManager()
    generator = CustomFormatGenerator(manager)

    print("\n生成車牌號:")
    for i in range(3):
        plate = generator.generate_license_plate()
        print(f"  {plate}")

    print("\n生成序列號:")
    products = ["筆記本電腦", "智能手機", "平板電腦"]
    for product in products:
        serial = generator.generate_serial_number(product)
        print(f"  {product}: {serial}")

    print("\n生成訂單號:")
    for i in range(3):
        order_id = generator.generate_order_id()
        print(f"  {order_id}")


def main():
    """主函數"""
    try:
        print("\n開始運行正則生成示例...")

        run_email_generation_example()
        run_phone_generation_example()
        run_datetime_generation_example()
        run_custom_format_example()

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
