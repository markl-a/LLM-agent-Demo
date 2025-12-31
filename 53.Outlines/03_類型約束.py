"""
Outlines 類型約束生成示例
========================

本示例展示如何使用 Outlines 進行類型約束生成。

主要內容:
1. 整數類型生成
2. 浮點數類型生成
3. 布爾類型生成
4. 日期時間類型
5. 自定義類型約束

作者: Outlines 教學團隊
日期: 2025-01
"""

import outlines
from outlines import models, generate
import torch
from typing import List, Dict, Optional, Union, Any, Tuple
from pydantic import BaseModel, Field, validator
from datetime import datetime, date, time
from decimal import Decimal
import logging
import json
import sys
import re
from enum import Enum

# ==================== 設置日誌 ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== 類型定義 ====================

class Priority(str, Enum):
    """優先級枚舉"""
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"
    CRITICAL = "緊急"


class Status(str, Enum):
    """狀態枚舉"""
    PENDING = "待處理"
    IN_PROGRESS = "進行中"
    COMPLETED = "已完成"
    CANCELLED = "已取消"


# ==================== 類型約束管理器 ====================

class TypeConstraintManager:
    """
    類型約束管理器

    管理和執行各種類型約束的生成任務
    """

    def __init__(self, model_name: str = "mistralai/Mistral-7B-v0.1"):
        """
        初始化類型約束管理器

        Args:
            model_name: 使用的模型名稱
        """
        self.model_name = model_name
        self.model = None
        self.load_model()

        logger.info(f"類型約束管理器初始化完成,模型: {model_name}")

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

    def generate_with_type(
        self,
        prompt: str,
        target_type: type
    ) -> Any:
        """
        生成指定類型的輸出

        Args:
            prompt: 輸入提示
            target_type: 目標類型

        Returns:
            生成的結果(指定類型)
        """
        try:
            logger.info(f"生成類型: {target_type.__name__}")

            # 創建類型生成器
            generator = generate.format(self.model, target_type)

            # 生成結果
            result = generator(prompt)

            logger.info(f"生成結果: {result} (類型: {type(result).__name__})")
            return result

        except Exception as e:
            logger.error(f"類型生成失敗: {str(e)}")
            raise


# ==================== 整數生成器 ====================

class IntegerGenerator:
    """
    整數生成器

    生成各種整數值
    """

    def __init__(self, manager: TypeConstraintManager):
        """
        初始化整數生成器

        Args:
            manager: 類型約束管理器
        """
        self.manager = manager
        logger.info("整數生成器初始化完成")

    def generate(self, prompt: str) -> int:
        """
        生成整數

        Args:
            prompt: 輸入提示

        Returns:
            生成的整數
        """
        return self.manager.generate_with_type(prompt, int)

    def generate_age(self, description: str = "成年人") -> int:
        """
        生成年齡

        Args:
            description: 人物描述

        Returns:
            年齡(整數)
        """
        prompt = f"生成一個{description}的年齡(只返回數字)"
        age = self.generate(prompt)

        # 驗證年齡範圍
        if not 0 <= age <= 120:
            logger.warning(f"年齡超出合理範圍: {age}")

        return age

    def generate_quantity(
        self,
        item: str,
        context: str = "訂單"
    ) -> int:
        """
        生成數量

        Args:
            item: 物品名稱
            context: 上下文

        Returns:
            數量(整數)
        """
        prompt = f"{context}中{item}的數量(只返回數字)"
        quantity = self.generate(prompt)

        if quantity < 0:
            logger.warning(f"數量為負數: {quantity}")

        return quantity

    def generate_year(self, event: str) -> int:
        """
        生成年份

        Args:
            event: 事件描述

        Returns:
            年份(整數)
        """
        prompt = f"{event}的年份(只返回數字)"
        year = self.generate(prompt)

        # 驗證年份範圍
        if not 1900 <= year <= 2100:
            logger.warning(f"年份超出常見範圍: {year}")

        return year

    def generate_score(
        self,
        subject: str,
        scale: int = 100
    ) -> int:
        """
        生成分數

        Args:
            subject: 科目或評分對象
            scale: 分數範圍(默認 100 分制)

        Returns:
            分數(整數)
        """
        prompt = f"{subject}的分數(0-{scale}分,只返回數字)"
        score = self.generate(prompt)

        if not 0 <= score <= scale:
            logger.warning(f"分數超出範圍: {score} (0-{scale})")

        return score


# ==================== 浮點數生成器 ====================

class FloatGenerator:
    """
    浮點數生成器

    生成各種浮點數值
    """

    def __init__(self, manager: TypeConstraintManager):
        """
        初始化浮點數生成器

        Args:
            manager: 類型約束管理器
        """
        self.manager = manager
        logger.info("浮點數生成器初始化完成")

    def generate(self, prompt: str) -> float:
        """
        生成浮點數

        Args:
            prompt: 輸入提示

        Returns:
            生成的浮點數
        """
        return self.manager.generate_with_type(prompt, float)

    def generate_price(
        self,
        product: str,
        currency: str = "USD"
    ) -> float:
        """
        生成價格

        Args:
            product: 產品名稱
            currency: 貨幣單位

        Returns:
            價格(浮點數)
        """
        prompt = f"{product}的價格({currency},只返回數字)"
        price = self.generate(prompt)

        if price < 0:
            logger.warning(f"價格為負數: {price}")

        return round(price, 2)

    def generate_temperature(
        self,
        location: str,
        season: str = "夏季"
    ) -> float:
        """
        生成溫度

        Args:
            location: 地點
            season: 季節

        Returns:
            溫度(攝氏度)
        """
        prompt = f"{location}{season}的平均溫度(攝氏度,只返回數字)"
        temp = self.generate(prompt)

        if not -50 <= temp <= 60:
            logger.warning(f"溫度超出常見範圍: {temp}°C")

        return round(temp, 1)

    def generate_percentage(
        self,
        description: str
    ) -> float:
        """
        生成百分比

        Args:
            description: 百分比描述

        Returns:
            百分比(0-100)
        """
        prompt = f"{description}的百分比(0-100,只返回數字)"
        percentage = self.generate(prompt)

        if not 0 <= percentage <= 100:
            logger.warning(f"百分比超出範圍: {percentage}%")

        return round(percentage, 2)

    def generate_rating(
        self,
        item: str,
        max_rating: float = 5.0
    ) -> float:
        """
        生成評分

        Args:
            item: 評分對象
            max_rating: 最高分

        Returns:
            評分(浮點數)
        """
        prompt = f"{item}的評分(0-{max_rating},只返回數字)"
        rating = self.generate(prompt)

        if not 0 <= rating <= max_rating:
            logger.warning(f"評分超出範圍: {rating} (0-{max_rating})")

        return round(rating, 1)

    def generate_distance(
        self,
        start: str,
        end: str,
        unit: str = "公里"
    ) -> float:
        """
        生成距離

        Args:
            start: 起點
            end: 終點
            unit: 單位

        Returns:
            距離(浮點數)
        """
        prompt = f"從{start}到{end}的距離({unit},只返回數字)"
        distance = self.generate(prompt)

        if distance < 0:
            logger.warning(f"距離為負數: {distance}")

        return round(distance, 2)


# ==================== 布爾生成器 ====================

class BooleanGenerator:
    """
    布爾生成器

    生成布爾值
    """

    def __init__(self, manager: TypeConstraintManager):
        """
        初始化布爾生成器

        Args:
            manager: 類型約束管理器
        """
        self.manager = manager
        logger.info("布爾生成器初始化完成")

    def generate(self, prompt: str) -> bool:
        """
        生成布爾值

        Args:
            prompt: 輸入提示

        Returns:
            生成的布爾值
        """
        return self.manager.generate_with_type(prompt, bool)

    def check_validity(self, item: str, validation: str) -> bool:
        """
        檢查有效性

        Args:
            item: 檢查對象
            validation: 驗證條件

        Returns:
            是否有效
        """
        prompt = f"{item}是否{validation}?(是/否)"
        return self.generate(prompt)

    def check_availability(self, resource: str) -> bool:
        """
        檢查可用性

        Args:
            resource: 資源名稱

        Returns:
            是否可用
        """
        prompt = f"{resource}是否可用?(是/否)"
        return self.generate(prompt)

    def check_permission(
        self,
        user: str,
        action: str
    ) -> bool:
        """
        檢查權限

        Args:
            user: 用戶
            action: 操作

        Returns:
            是否有權限
        """
        prompt = f"{user}是否有權限{action}?(是/否)"
        return self.generate(prompt)

    def verify_condition(self, condition: str) -> bool:
        """
        驗證條件

        Args:
            condition: 條件描述

        Returns:
            條件是否成立
        """
        prompt = f"{condition}是否成立?(是/否)"
        return self.generate(prompt)


# ==================== 複合類型生成器 ====================

class NumberRange(BaseModel):
    """數字範圍模型"""
    min_value: int = Field(description="最小值")
    max_value: int = Field(description="最大值")

    @validator('max_value')
    def max_must_be_greater(cls, v, values):
        if 'min_value' in values and v <= values['min_value']:
            raise ValueError('最大值必須大於最小值')
        return v


class Coordinate(BaseModel):
    """座標模型"""
    latitude: float = Field(description="緯度", ge=-90, le=90)
    longitude: float = Field(description="經度", ge=-180, le=180)


class Measurement(BaseModel):
    """測量數據模型"""
    value: float = Field(description="測量值")
    unit: str = Field(description="單位")
    precision: int = Field(description="精度", ge=0)
    is_estimated: bool = Field(description="是否為估計值")


class Statistics(BaseModel):
    """統計數據模型"""
    count: int = Field(description="計數", ge=0)
    mean: float = Field(description="平均值")
    median: float = Field(description="中位數")
    std_dev: float = Field(description="標準差", ge=0)
    min_value: float = Field(description="最小值")
    max_value: float = Field(description="最大值")


class ComplexTypeGenerator:
    """
    複合類型生成器

    生成包含多種基本類型的複合數據
    """

    def __init__(self, manager: TypeConstraintManager):
        """
        初始化複合類型生成器

        Args:
            manager: 類型約束管理器
        """
        self.manager = manager
        logger.info("複合類型生成器初始化完成")

    def generate_range(
        self,
        description: str
    ) -> NumberRange:
        """
        生成數字範圍

        Args:
            description: 範圍描述

        Returns:
            數字範圍對象
        """
        generator = generate.json(self.manager.model, NumberRange)
        prompt = f"生成{description}的數字範圍"
        return generator(prompt)

    def generate_coordinate(
        self,
        location: str
    ) -> Coordinate:
        """
        生成座標

        Args:
            location: 地點名稱

        Returns:
            座標對象
        """
        generator = generate.json(self.manager.model, Coordinate)
        prompt = f"生成{location}的座標"
        return generator(prompt)

    def generate_measurement(
        self,
        item: str,
        property_name: str
    ) -> Measurement:
        """
        生成測量數據

        Args:
            item: 測量對象
            property_name: 屬性名稱

        Returns:
            測量數據對象
        """
        generator = generate.json(self.manager.model, Measurement)
        prompt = f"生成{item}的{property_name}測量數據"
        return generator(prompt)

    def generate_statistics(
        self,
        dataset_description: str
    ) -> Statistics:
        """
        生成統計數據

        Args:
            dataset_description: 數據集描述

        Returns:
            統計數據對象
        """
        generator = generate.json(self.manager.model, Statistics)
        prompt = f"生成{dataset_description}的統計數據"
        return generator(prompt)


# ==================== 數據驗證器 ====================

class DataValidator:
    """
    數據驗證器

    驗證生成的數據是否符合類型約束
    """

    @staticmethod
    def validate_integer(value: Any) -> Tuple[bool, str]:
        """
        驗證整數

        Args:
            value: 待驗證的值

        Returns:
            (是否有效, 錯誤信息) 元組
        """
        if not isinstance(value, int):
            return False, f"類型錯誤: 期望 int,實際 {type(value).__name__}"

        return True, "驗證通過"

    @staticmethod
    def validate_float(value: Any) -> Tuple[bool, str]:
        """
        驗證浮點數

        Args:
            value: 待驗證的值

        Returns:
            (是否有效, 錯誤信息) 元組
        """
        if not isinstance(value, (float, int)):
            return False, f"類型錯誤: 期望 float,實際 {type(value).__name__}"

        return True, "驗證通過"

    @staticmethod
    def validate_boolean(value: Any) -> Tuple[bool, str]:
        """
        驗證布爾值

        Args:
            value: 待驗證的值

        Returns:
            (是否有效, 錯誤信息) 元組
        """
        if not isinstance(value, bool):
            return False, f"類型錯誤: 期望 bool,實際 {type(value).__name__}"

        return True, "驗證通過"

    @staticmethod
    def validate_range(
        value: Union[int, float],
        min_val: Optional[Union[int, float]] = None,
        max_val: Optional[Union[int, float]] = None
    ) -> Tuple[bool, str]:
        """
        驗證數值範圍

        Args:
            value: 待驗證的值
            min_val: 最小值
            max_val: 最大值

        Returns:
            (是否有效, 錯誤信息) 元組
        """
        if min_val is not None and value < min_val:
            return False, f"值 {value} 小於最小值 {min_val}"

        if max_val is not None and value > max_val:
            return False, f"值 {value} 大於最大值 {max_val}"

        return True, "驗證通過"


# ==================== 示例運行器 ====================

def run_integer_generation_example():
    """運行整數生成示例"""
    print("\n" + "="*60)
    print("示例 1: 整數類型生成")
    print("="*60)

    manager = TypeConstraintManager()
    generator = IntegerGenerator(manager)

    # 生成年齡
    print("\n生成年齡:")
    descriptions = ["青少年", "成年人", "老年人"]
    for desc in descriptions:
        age = generator.generate_age(desc)
        print(f"  {desc}: {age} 歲")

    # 生成數量
    print("\n生成數量:")
    items = [("蘋果", "購物車"), ("筆記本", "倉庫"), ("書籍", "圖書館")]
    for item, context in items:
        quantity = generator.generate_quantity(item, context)
        print(f"  {context}中的{item}: {quantity}")

    # 生成分數
    print("\n生成分數:")
    subjects = ["數學", "英語", "物理"]
    for subject in subjects:
        score = generator.generate_score(subject)
        print(f"  {subject}分數: {score}/100")


def run_float_generation_example():
    """運行浮點數生成示例"""
    print("\n" + "="*60)
    print("示例 2: 浮點數類型生成")
    print("="*60)

    manager = TypeConstraintManager()
    generator = FloatGenerator(manager)

    # 生成價格
    print("\n生成價格:")
    products = ["筆記本電腦", "智能手機", "咖啡"]
    for product in products:
        price = generator.generate_price(product)
        print(f"  {product}: ${price}")

    # 生成溫度
    print("\n生成溫度:")
    locations = [("北京", "冬季"), ("上海", "夏季"), ("廣州", "春季")]
    for location, season in locations:
        temp = generator.generate_temperature(location, season)
        print(f"  {location}{season}: {temp}°C")

    # 生成評分
    print("\n生成評分:")
    items = ["餐廳服務", "電影質量", "產品體驗"]
    for item in items:
        rating = generator.generate_rating(item)
        print(f"  {item}: {rating}/5.0")


def run_boolean_generation_example():
    """運行布爾生成示例"""
    print("\n" + "="*60)
    print("示例 3: 布爾類型生成")
    print("="*60)

    manager = TypeConstraintManager()
    generator = BooleanGenerator(manager)

    # 檢查有效性
    print("\n檢查有效性:")
    checks = [
        ("user@example.com", "有效的郵箱地址"),
        ("2024-01-01", "有效的日期格式"),
        ("123-456-7890", "有效的電話號碼")
    ]
    for item, validation in checks:
        is_valid = generator.check_validity(item, validation)
        print(f"  {item} {validation}: {is_valid}")

    # 檢查可用性
    print("\n檢查可用性:")
    resources = ["會議室A", "停車位B", "設備C"]
    for resource in resources:
        is_available = generator.check_availability(resource)
        print(f"  {resource}: {'可用' if is_available else '不可用'}")


def run_complex_type_example():
    """運行複合類型示例"""
    print("\n" + "="*60)
    print("示例 4: 複合類型生成")
    print("="*60)

    manager = TypeConstraintManager()
    generator = ComplexTypeGenerator(manager)

    # 生成數字範圍
    print("\n生成數字範圍:")
    number_range = generator.generate_range("產品價格")
    print(f"  最小值: {number_range.min_value}")
    print(f"  最大值: {number_range.max_value}")

    # 生成座標
    print("\n生成座標:")
    coordinate = generator.generate_coordinate("台北101")
    print(f"  緯度: {coordinate.latitude}")
    print(f"  經度: {coordinate.longitude}")

    # 生成測量數據
    print("\n生成測量數據:")
    measurement = generator.generate_measurement("建築物", "高度")
    print(f"  測量值: {measurement.value}")
    print(f"  單位: {measurement.unit}")
    print(f"  精度: {measurement.precision}")
    print(f"  估計值: {measurement.is_estimated}")


def main():
    """主函數"""
    try:
        print("\n開始運行類型約束示例...")

        run_integer_generation_example()
        run_float_generation_example()
        run_boolean_generation_example()
        run_complex_type_example()

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
