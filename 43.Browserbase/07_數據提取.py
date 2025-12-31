"""
Browserbase 數據提取示例
========================

本模塊展示了如何使用 Browserbase 進行網頁數據提取和爬蟲。
包括 DOM 解析、數據清洗、結構化提取、分頁處理等。

主要內容:
1. 基礎數據提取
2. 結構化數據提取
3. 列表數據爬取
4. 分頁數據處理
5. 動態內容提取
6. 數據清洗和驗證

作者: Browserbase 示例團隊
日期: 2025-12-31
"""

import os
import re
import json
import time
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from collections import defaultdict
from dotenv import load_dotenv


# 加載環境變量
load_dotenv()


class DataType(Enum):
    """數據類型"""
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    URL = "url"
    EMAIL = "email"
    PRICE = "price"
    IMAGE = "image"


@dataclass
class ExtractionRule:
    """提取規則"""
    name: str
    selector: str
    data_type: DataType
    attribute: Optional[str] = None  # 提取屬性（如 href, src）
    transform: Optional[Callable] = None  # 轉換函數
    required: bool = False
    default_value: Any = None

    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            "name": self.name,
            "selector": self.selector,
            "type": self.data_type.value,
            "attribute": self.attribute,
            "required": self.required
        }


@dataclass
class ExtractedData:
    """提取的數據"""
    url: str
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            "url": self.url,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "metadata": self.metadata
        }


class DataExtractor:
    """
    數據提取器

    從網頁中提取結構化數據。
    """

    def __init__(self):
        """初始化數據提取器"""
        self.extracted_items = []
        print("[DataExtractor] 初始化完成")

    def extract_single(
        self,
        rules: List[ExtractionRule],
        url: str = "https://example.com"
    ) -> Optional[ExtractedData]:
        """
        提取單條數據

        Args:
            rules: 提取規則列表
            url: 頁面 URL

        Returns:
            提取的數據
        """
        print(f"\n[DataExtractor] 從 {url} 提取數據")
        print(f"  使用 {len(rules)} 條規則")

        data = {}

        for rule in rules:
            try:
                value = self._extract_by_rule(rule)
                data[rule.name] = value
                print(f"  ✓ {rule.name}: {value}")

            except Exception as e:
                if rule.required:
                    print(f"  ✗ {rule.name}: 必填字段提取失敗")
                    return None
                else:
                    data[rule.name] = rule.default_value
                    print(f"  - {rule.name}: 使用默認值")

        extracted = ExtractedData(
            url=url,
            timestamp=datetime.now(),
            data=data
        )

        self.extracted_items.append(extracted)
        return extracted

    def extract_list(
        self,
        list_selector: str,
        rules: List[ExtractionRule],
        url: str = "https://example.com",
        max_items: Optional[int] = None
    ) -> List[ExtractedData]:
        """
        提取列表數據

        Args:
            list_selector: 列表容器選擇器
            rules: 每個項目的提取規則
            url: 頁面 URL
            max_items: 最大提取數量

        Returns:
            提取的數據列表
        """
        print(f"\n[DataExtractor] 提取列表數據: {list_selector}")

        # 模擬找到的項目數量
        total_items = 15
        if max_items:
            total_items = min(total_items, max_items)

        print(f"  找到 {total_items} 個項目")

        results = []

        for i in range(total_items):
            print(f"\n  項目 {i + 1}/{total_items}:")

            # 模擬提取每個項目
            item_data = {}
            for rule in rules:
                value = self._extract_by_rule(rule, index=i)
                item_data[rule.name] = value
                print(f"    - {rule.name}: {value}")

            extracted = ExtractedData(
                url=f"{url}#item-{i}",
                timestamp=datetime.now(),
                data=item_data
            )

            results.append(extracted)

        print(f"\n  共提取 {len(results)} 個項目")
        self.extracted_items.extend(results)

        return results

    def _extract_by_rule(
        self,
        rule: ExtractionRule,
        index: int = 0
    ) -> Any:
        """
        根據規則提取數據

        Args:
            rule: 提取規則
            index: 項目索引（用於生成模擬數據）

        Returns:
            提取的值
        """
        # 模擬提取（實際應該使用真實的 DOM 解析）
        mock_value = self._generate_mock_value(rule.data_type, index)

        # 應用轉換
        if rule.transform:
            mock_value = rule.transform(mock_value)

        return mock_value

    def _generate_mock_value(self, data_type: DataType, index: int) -> Any:
        """生成模擬值"""
        if data_type == DataType.TEXT:
            return f"示例文本 {index + 1}"
        elif data_type == DataType.NUMBER:
            return index + 1
        elif data_type == DataType.DATE:
            return datetime.now().strftime("%Y-%m-%d")
        elif data_type == DataType.URL:
            return f"https://example.com/page/{index + 1}"
        elif data_type == DataType.EMAIL:
            return f"user{index + 1}@example.com"
        elif data_type == DataType.PRICE:
            return f"NT$ {(index + 1) * 100}"
        elif data_type == DataType.IMAGE:
            return f"https://example.com/images/{index + 1}.jpg"
        return None


class PaginationHandler:
    """
    分頁處理器

    處理分頁數據的爬取。
    """

    def __init__(self, extractor: DataExtractor):
        """
        初始化分頁處理器

        Args:
            extractor: 數據提取器
        """
        self.extractor = extractor
        self.current_page = 1
        self.total_pages = 0
        print("[PaginationHandler] 初始化完成")

    def extract_all_pages(
        self,
        base_url: str,
        list_selector: str,
        rules: List[ExtractionRule],
        max_pages: Optional[int] = None,
        next_button_selector: str = ".next-page"
    ) -> List[ExtractedData]:
        """
        提取所有分頁數據

        Args:
            base_url: 基礎 URL
            list_selector: 列表選擇器
            rules: 提取規則
            max_pages: 最大頁數
            next_button_selector: 下一頁按鈕選擇器

        Returns:
            所有提取的數據
        """
        print(f"\n[PaginationHandler] 開始爬取分頁數據")
        print(f"  基礎 URL: {base_url}")
        print(f"  最大頁數: {max_pages or '不限'}")
        print("=" * 60)

        all_results = []
        page = 1

        while True:
            if max_pages and page > max_pages:
                print(f"\n已達到最大頁數限制: {max_pages}")
                break

            current_url = f"{base_url}?page={page}"
            print(f"\n頁面 {page}:")
            print(f"  URL: {current_url}")

            # 提取當前頁數據
            page_results = self.extractor.extract_list(
                list_selector,
                rules,
                url=current_url
            )

            all_results.extend(page_results)
            print(f"  本頁提取: {len(page_results)} 個項目")

            # 檢查是否有下一頁
            has_next = self._check_next_page(next_button_selector)

            if not has_next:
                print("\n沒有更多頁面")
                break

            print("  等待後加載下一頁...")
            time.sleep(1)  # 避免請求過快

            page += 1

        self.total_pages = page

        print("\n" + "=" * 60)
        print(f"爬取完成:")
        print(f"  總頁數: {self.total_pages}")
        print(f"  總項目: {len(all_results)}")
        print("=" * 60 + "\n")

        return all_results

    def _check_next_page(self, selector: str) -> bool:
        """檢查是否有下一頁"""
        # 模擬檢查（前3頁有下一頁）
        has_next = self.current_page < 3
        self.current_page += 1
        return has_next


class DataCleaner:
    """
    數據清洗器

    清洗和規範化提取的數據。
    """

    def __init__(self):
        """初始化數據清洗器"""
        print("[DataCleaner] 初始化完成")

    def clean_text(self, text: str) -> str:
        """
        清洗文本

        Args:
            text: 原始文本

        Returns:
            清洗後的文本
        """
        if not text:
            return ""

        # 移除多餘空白
        text = re.sub(r'\s+', ' ', text)

        # 去除首尾空白
        text = text.strip()

        # 移除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?-]', '', text)

        return text

    def clean_price(self, price_str: str) -> Optional[float]:
        """
        清洗價格

        Args:
            price_str: 價格字符串

        Returns:
            清洗後的價格數字
        """
        if not price_str:
            return None

        # 移除貨幣符號和逗號
        price_str = re.sub(r'[NT$€¥£,\s]', '', price_str)

        # 提取數字
        match = re.search(r'[\d.]+', price_str)
        if match:
            try:
                return float(match.group())
            except ValueError:
                return None

        return None

    def clean_url(self, url: str, base_url: str = "") -> str:
        """
        清洗 URL

        Args:
            url: 原始 URL
            base_url: 基礎 URL

        Returns:
            完整的 URL
        """
        if not url:
            return ""

        # 如果是相對路徑，補充完整 URL
        if url.startswith('/'):
            url = base_url.rstrip('/') + url
        elif not url.startswith(('http://', 'https://')):
            url = base_url.rstrip('/') + '/' + url.lstrip('/')

        return url

    def clean_email(self, email: str) -> Optional[str]:
        """
        清洗郵箱

        Args:
            email: 郵箱字符串

        Returns:
            清洗後的郵箱
        """
        if not email:
            return None

        email = email.strip().lower()

        # 驗證郵箱格式
        if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            return email

        return None

    def clean_date(self, date_str: str) -> Optional[str]:
        """
        清洗日期

        Args:
            date_str: 日期字符串

        Returns:
            標準化的日期字符串
        """
        if not date_str:
            return None

        # 嘗試解析常見日期格式
        patterns = [
            r'(\d{4})-(\d{2})-(\d{2})',
            r'(\d{4})/(\d{2})/(\d{2})',
            r'(\d{2})/(\d{2})/(\d{4})',
        ]

        for pattern in patterns:
            match = re.search(pattern, date_str)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    # 統一為 YYYY-MM-DD 格式
                    if len(groups[0]) == 4:
                        return f"{groups[0]}-{groups[1]}-{groups[2]}"
                    else:
                        return f"{groups[2]}-{groups[0]}-{groups[1]}"

        return None

    def clean_data_item(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        清洗數據項

        Args:
            data: 原始數據

        Returns:
            清洗後的數據
        """
        cleaned = {}

        for key, value in data.items():
            if isinstance(value, str):
                # 判斷數據類型並清洗
                if 'price' in key.lower():
                    cleaned[key] = self.clean_price(value)
                elif 'email' in key.lower():
                    cleaned[key] = self.clean_email(value)
                elif 'url' in key.lower() or 'link' in key.lower():
                    cleaned[key] = self.clean_url(value)
                elif 'date' in key.lower():
                    cleaned[key] = self.clean_date(value)
                else:
                    cleaned[key] = self.clean_text(value)
            else:
                cleaned[key] = value

        return cleaned


class DataValidator:
    """
    數據驗證器

    驗證提取數據的完整性和有效性。
    """

    def __init__(self):
        """初始化數據驗證器"""
        self.validation_errors = []
        print("[DataValidator] 初始化完成")

    def validate_item(
        self,
        data: Dict[str, Any],
        required_fields: List[str] = None,
        validators: Dict[str, Callable] = None
    ) -> Dict:
        """
        驗證數據項

        Args:
            data: 數據項
            required_fields: 必填字段列表
            validators: 自定義驗證器字典

        Returns:
            驗證結果
        """
        self.validation_errors.clear()

        # 檢查必填字段
        if required_fields:
            for field in required_fields:
                if field not in data or not data[field]:
                    self.validation_errors.append({
                        "field": field,
                        "error": "必填字段缺失或為空"
                    })

        # 執行自定義驗證
        if validators:
            for field, validator in validators.items():
                if field in data:
                    try:
                        if not validator(data[field]):
                            self.validation_errors.append({
                                "field": field,
                                "error": "驗證失敗"
                            })
                    except Exception as e:
                        self.validation_errors.append({
                            "field": field,
                            "error": f"驗證錯誤: {str(e)}"
                        })

        is_valid = len(self.validation_errors) == 0

        return {
            "is_valid": is_valid,
            "errors": self.validation_errors.copy()
        }

    def validate_batch(
        self,
        items: List[Dict[str, Any]],
        **kwargs
    ) -> Dict:
        """
        批量驗證

        Args:
            items: 數據項列表
            **kwargs: 驗證參數

        Returns:
            驗證結果統計
        """
        print(f"\n[DataValidator] 驗證 {len(items)} 個數據項")

        valid_count = 0
        all_errors = []

        for i, item in enumerate(items):
            result = self.validate_item(item, **kwargs)

            if result["is_valid"]:
                valid_count += 1
            else:
                all_errors.append({
                    "item_index": i,
                    "errors": result["errors"]
                })

        print(f"  有效: {valid_count}/{len(items)}")

        if all_errors:
            print(f"  發現 {len(all_errors)} 個項目有錯誤")

        return {
            "total": len(items),
            "valid": valid_count,
            "invalid": len(items) - valid_count,
            "errors": all_errors
        }


class DataExporter:
    """
    數據導出器

    將提取的數據導出為不同格式。
    """

    def __init__(self, output_dir: str = "./data"):
        """
        初始化數據導出器

        Args:
            output_dir: 輸出目錄
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        print(f"[DataExporter] 初始化完成，輸出目錄: {output_dir}")

    def export_json(
        self,
        data: List[Dict[str, Any]],
        filename: str = "data.json"
    ) -> str:
        """
        導出為 JSON

        Args:
            data: 數據列表
            filename: 文件名

        Returns:
            文件路徑
        """
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"[DataExporter] JSON 已導出: {filepath} ({len(data)} 項)")
        return filepath

    def export_csv(
        self,
        data: List[Dict[str, Any]],
        filename: str = "data.csv"
    ) -> str:
        """
        導出為 CSV

        Args:
            data: 數據列表
            filename: 文件名

        Returns:
            文件路徑
        """
        if not data:
            print("[DataExporter] 警告: 沒有數據可導出")
            return ""

        filepath = os.path.join(self.output_dir, filename)

        # 獲取所有字段
        fields = set()
        for item in data:
            fields.update(item.keys())
        fields = sorted(fields)

        # 寫入 CSV
        with open(filepath, 'w', encoding='utf-8') as f:
            # 寫入表頭
            f.write(','.join(fields) + '\n')

            # 寫入數據
            for item in data:
                row = [str(item.get(field, '')) for field in fields]
                f.write(','.join(row) + '\n')

        print(f"[DataExporter] CSV 已導出: {filepath} ({len(data)} 項)")
        return filepath


def example_basic_extraction():
    """示例1: 基礎數據提取"""
    print("\n" + "=" * 60)
    print("示例1: 基礎數據提取")
    print("=" * 60 + "\n")

    extractor = DataExtractor()

    rules = [
        ExtractionRule("title", "h1.title", DataType.TEXT, required=True),
        ExtractionRule("author", ".author", DataType.TEXT),
        ExtractionRule("date", ".publish-date", DataType.DATE),
        ExtractionRule("views", ".view-count", DataType.NUMBER),
    ]

    result = extractor.extract_single(rules, "https://example.com/article/1")

    if result:
        print("\n提取結果:")
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


def example_list_extraction():
    """示例2: 列表數據提取"""
    print("\n" + "=" * 60)
    print("示例2: 列表數據提取")
    print("=" * 60 + "\n")

    extractor = DataExtractor()

    rules = [
        ExtractionRule("title", ".product-title", DataType.TEXT),
        ExtractionRule("price", ".product-price", DataType.PRICE),
        ExtractionRule("image", ".product-img", DataType.IMAGE, attribute="src"),
        ExtractionRule("link", "a.product-link", DataType.URL, attribute="href"),
    ]

    results = extractor.extract_list(
        list_selector=".product-list .product-item",
        rules=rules,
        max_items=5
    )

    print(f"\n共提取 {len(results)} 個商品")


def example_pagination():
    """示例3: 分頁數據爬取"""
    print("\n" + "=" * 60)
    print("示例3: 分頁數據爬取")
    print("=" * 60 + "\n")

    extractor = DataExtractor()
    pagination = PaginationHandler(extractor)

    rules = [
        ExtractionRule("title", ".article-title", DataType.TEXT),
        ExtractionRule("summary", ".article-summary", DataType.TEXT),
        ExtractionRule("date", ".publish-date", DataType.DATE),
    ]

    results = pagination.extract_all_pages(
        base_url="https://example.com/articles",
        list_selector=".article-list .article",
        rules=rules,
        max_pages=3
    )


def example_data_cleaning():
    """示例4: 數據清洗"""
    print("\n" + "=" * 60)
    print("示例4: 數據清洗")
    print("=" * 60 + "\n")

    cleaner = DataCleaner()

    # 測試數據
    dirty_data = {
        "title": "  這是一個   標題  \n\n",
        "price": "NT$ 1,299",
        "email": "  USER@EXAMPLE.COM  ",
        "url": "/products/item-1",
        "date": "2025/12/31",
    }

    print("原始數據:")
    print(json.dumps(dirty_data, ensure_ascii=False, indent=2))

    cleaned_data = cleaner.clean_data_item(dirty_data)

    print("\n清洗後:")
    print(json.dumps(cleaned_data, ensure_ascii=False, indent=2))


def example_data_validation():
    """示例5: 數據驗證"""
    print("\n" + "=" * 60)
    print("示例5: 數據驗證")
    print("=" * 60 + "\n")

    validator = DataValidator()

    # 測試數據
    test_items = [
        {"title": "商品A", "price": 100, "stock": 10},
        {"title": "", "price": 200, "stock": 0},  # 缺少標題
        {"title": "商品C", "price": -50, "stock": 5},  # 價格無效
    ]

    # 驗證
    result = validator.validate_batch(
        test_items,
        required_fields=["title", "price"],
        validators={
            "price": lambda p: p > 0,
            "stock": lambda s: s >= 0,
        }
    )

    print(f"\n驗證結果:")
    print(f"  總數: {result['total']}")
    print(f"  有效: {result['valid']}")
    print(f"  無效: {result['invalid']}")


def example_data_export():
    """示例6: 數據導出"""
    print("\n" + "=" * 60)
    print("示例6: 數據導出")
    print("=" * 60 + "\n")

    # 生成測試數據
    data = [
        {"id": 1, "name": "商品A", "price": 100},
        {"id": 2, "name": "商品B", "price": 200},
        {"id": 3, "name": "商品C", "price": 300},
    ]

    exporter = DataExporter(output_dir="./extracted_data")

    # 導出 JSON
    json_file = exporter.export_json(data, "products.json")

    # 導出 CSV
    csv_file = exporter.export_csv(data, "products.csv")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Browserbase 數據提取示例")
    print("=" * 60)

    # 運行所有示例
    example_basic_extraction()
    example_list_extraction()
    example_pagination()
    example_data_cleaning()
    example_data_validation()
    example_data_export()

    print("\n" + "=" * 60)
    print("所有示例完成！")
    print("=" * 60 + "\n")

    print("最佳實踐:")
    print("- 提取後立即進行數據清洗")
    print("- 使用驗證器確保數據質量")
    print("- 處理分頁時控制請求速率")
    print("- 定期導出數據避免丟失")
    print("- 使用合適的數據結構存儲")


if __name__ == "__main__":
    main()
