"""
Browserbase 表單自動化示例
==========================

本模塊展示了如何使用 Browserbase 進行表單自動化處理。
包括表單填寫、驗證、提交、文件上傳等功能。

主要內容:
1. 基礎表單填寫
2. 複雜表單處理
3. 文件上傳
4. 表單驗證
5. 動態表單處理
6. 批量表單提交

作者: Browserbase 示例團隊
日期: 2025-12-31
"""

import os
import time
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from pathlib import Path
from dotenv import load_dotenv


# 加載環境變量
load_dotenv()


class InputType(Enum):
    """輸入類型"""
    TEXT = "text"
    EMAIL = "email"
    PASSWORD = "password"
    NUMBER = "number"
    TEL = "tel"
    URL = "url"
    DATE = "date"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    SELECT = "select"
    TEXTAREA = "textarea"
    FILE = "file"


class ValidationRule(Enum):
    """驗證規則"""
    REQUIRED = "required"
    EMAIL = "email"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    PATTERN = "pattern"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"


@dataclass
class FormField:
    """表單字段"""
    name: str
    selector: str
    input_type: InputType
    value: Any
    label: Optional[str] = None
    placeholder: Optional[str] = None
    required: bool = False
    validations: List[Dict] = field(default_factory=list)
    wait_after_input: float = 0.1  # 輸入後等待時間

    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            "name": self.name,
            "selector": self.selector,
            "type": self.input_type.value,
            "value": self.value,
            "label": self.label,
            "required": self.required
        }


@dataclass
class FormData:
    """表單數據"""
    fields: List[FormField]
    submit_button_selector: str = "#submit"
    form_selector: str = "form"
    wait_before_submit: float = 0.5
    wait_after_submit: float = 2.0

    def get_field(self, name: str) -> Optional[FormField]:
        """獲取字段"""
        for field in self.fields:
            if field.name == name:
                return field
        return None

    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            "fields": [f.to_dict() for f in self.fields],
            "submit_button": self.submit_button_selector,
            "form_selector": self.form_selector
        }


class FormFiller:
    """
    表單填充器

    自動填充表單字段。
    """

    def __init__(self, simulate_human: bool = True):
        """
        初始化表單填充器

        Args:
            simulate_human: 是否模擬人類行為
        """
        self.simulate_human = simulate_human
        self.filled_forms = 0
        print(f"[FormFiller] 初始化完成 (模擬人類: {simulate_human})")

    def fill_field(self, field: FormField) -> bool:
        """
        填充單個字段

        Args:
            field: 表單字段

        Returns:
            是否成功
        """
        print(f"[FormFiller] 填充字段: {field.name} ({field.input_type.value})")

        try:
            # 根據類型處理不同的輸入
            if field.input_type == InputType.TEXT:
                self._fill_text_input(field)

            elif field.input_type == InputType.EMAIL:
                self._fill_email_input(field)

            elif field.input_type == InputType.PASSWORD:
                self._fill_password_input(field)

            elif field.input_type == InputType.NUMBER:
                self._fill_number_input(field)

            elif field.input_type == InputType.SELECT:
                self._fill_select(field)

            elif field.input_type == InputType.CHECKBOX:
                self._fill_checkbox(field)

            elif field.input_type == InputType.RADIO:
                self._fill_radio(field)

            elif field.input_type == InputType.TEXTAREA:
                self._fill_textarea(field)

            elif field.input_type == InputType.DATE:
                self._fill_date_input(field)

            elif field.input_type == InputType.FILE:
                self._fill_file_input(field)

            # 等待
            if field.wait_after_input > 0:
                time.sleep(field.wait_after_input)

            print(f"  ✓ 填充成功")
            return True

        except Exception as e:
            print(f"  ✗ 填充失敗: {str(e)}")
            return False

    def fill_form(self, form_data: FormData) -> bool:
        """
        填充整個表單

        Args:
            form_data: 表單數據

        Returns:
            是否成功
        """
        print(f"\n[FormFiller] 開始填充表單 ({len(form_data.fields)} 個字段)")
        print("=" * 50)

        success_count = 0

        for i, field in enumerate(form_data.fields, 1):
            print(f"\n字段 {i}/{len(form_data.fields)}:")

            if self.fill_field(field):
                success_count += 1

        # 提交前等待
        if form_data.wait_before_submit > 0:
            print(f"\n等待 {form_data.wait_before_submit}秒後提交...")
            time.sleep(form_data.wait_before_submit)

        # 提交表單
        print(f"\n提交表單: {form_data.submit_button_selector}")
        self._submit_form(form_data.submit_button_selector)

        # 提交後等待
        if form_data.wait_after_submit > 0:
            time.sleep(form_data.wait_after_submit)

        self.filled_forms += 1

        print("=" * 50)
        print(f"表單填充完成: {success_count}/{len(form_data.fields)} 個字段成功\n")

        return success_count == len(form_data.fields)

    def _fill_text_input(self, field: FormField):
        """填充文本輸入"""
        text = str(field.value)
        print(f"  輸入文本: {text}")

        if self.simulate_human:
            # 模擬逐字符輸入
            delay = 0.05
            for char in text:
                time.sleep(delay)

    def _fill_email_input(self, field: FormField):
        """填充郵箱輸入"""
        email = str(field.value)
        print(f"  輸入郵箱: {email}")

        # 驗證郵箱格式
        if '@' not in email:
            raise ValueError("無效的郵箱格式")

    def _fill_password_input(self, field: FormField):
        """填充密碼輸入"""
        password = str(field.value)
        print(f"  輸入密碼: {'*' * len(password)}")

    def _fill_number_input(self, field: FormField):
        """填充數字輸入"""
        number = field.value
        print(f"  輸入數字: {number}")

    def _fill_select(self, field: FormField):
        """填充下拉選擇"""
        value = str(field.value)
        print(f"  選擇: {value}")

    def _fill_checkbox(self, field: FormField):
        """填充複選框"""
        checked = bool(field.value)
        print(f"  複選框: {'勾選' if checked else '取消勾選'}")

    def _fill_radio(self, field: FormField):
        """填充單選按鈕"""
        value = str(field.value)
        print(f"  單選: {value}")

    def _fill_textarea(self, field: FormField):
        """填充文本區域"""
        text = str(field.value)
        print(f"  輸入多行文本 ({len(text)} 字符)")

    def _fill_date_input(self, field: FormField):
        """填充日期輸入"""
        date_value = field.value
        if isinstance(date_value, str):
            print(f"  輸入日期: {date_value}")
        elif isinstance(date_value, date):
            print(f"  輸入日期: {date_value.isoformat()}")

    def _fill_file_input(self, field: FormField):
        """填充文件輸入"""
        file_path = str(field.value)
        print(f"  上傳文件: {file_path}")

        # 檢查文件是否存在
        if not Path(file_path).exists():
            print(f"  警告: 文件不存在: {file_path}")

    def _submit_form(self, selector: str):
        """提交表單"""
        print(f"  點擊提交按鈕...")
        # 實際應該調用瀏覽器 API 點擊按鈕


class FormValidator:
    """
    表單驗證器

    驗證表單數據的有效性。
    """

    def __init__(self):
        """初始化驗證器"""
        self.validation_errors: List[Dict] = []
        print("[FormValidator] 初始化完成")

    def validate_field(self, field: FormField) -> bool:
        """
        驗證單個字段

        Args:
            field: 表單字段

        Returns:
            是否通過驗證
        """
        self.validation_errors.clear()

        # 必填驗證
        if field.required:
            if not field.value or (isinstance(field.value, str) and not field.value.strip()):
                self._add_error(field.name, "此字段為必填項")
                return False

        # 執行其他驗證
        for validation in field.validations:
            rule = validation.get("rule")

            if rule == ValidationRule.EMAIL.value:
                if not self._validate_email(field.value):
                    self._add_error(field.name, "無效的郵箱格式")

            elif rule == ValidationRule.MIN_LENGTH.value:
                min_len = validation.get("value", 0)
                if len(str(field.value)) < min_len:
                    self._add_error(field.name, f"至少需要 {min_len} 個字符")

            elif rule == ValidationRule.MAX_LENGTH.value:
                max_len = validation.get("value", 0)
                if len(str(field.value)) > max_len:
                    self._add_error(field.name, f"最多 {max_len} 個字符")

            elif rule == ValidationRule.PATTERN.value:
                pattern = validation.get("value", "")
                # 簡化的模式匹配檢查
                if not self._validate_pattern(field.value, pattern):
                    self._add_error(field.name, f"格式不符合要求: {pattern}")

        is_valid = len(self.validation_errors) == 0

        if is_valid:
            print(f"[FormValidator] ✓ {field.name} 驗證通過")
        else:
            print(f"[FormValidator] ✗ {field.name} 驗證失敗:")
            for error in self.validation_errors:
                print(f"    - {error['message']}")

        return is_valid

    def validate_form(self, form_data: FormData) -> Dict:
        """
        驗證整個表單

        Args:
            form_data: 表單數據

        Returns:
            驗證結果
        """
        print("\n[FormValidator] 開始驗證表單")
        print("=" * 50)

        all_errors = []
        valid_fields = 0

        for field in form_data.fields:
            self.validation_errors.clear()

            if self.validate_field(field):
                valid_fields += 1
            else:
                all_errors.extend(self.validation_errors)

        result = {
            "is_valid": len(all_errors) == 0,
            "total_fields": len(form_data.fields),
            "valid_fields": valid_fields,
            "errors": all_errors
        }

        print("=" * 50)
        print(f"驗證結果: {valid_fields}/{len(form_data.fields)} 個字段通過")

        if all_errors:
            print(f"\n發現 {len(all_errors)} 個錯誤:")
            for error in all_errors:
                print(f"  - {error['field']}: {error['message']}")

        print()

        return result

    def _add_error(self, field_name: str, message: str):
        """添加錯誤"""
        self.validation_errors.append({
            "field": field_name,
            "message": message
        })

    def _validate_email(self, email: str) -> bool:
        """驗證郵箱"""
        if not isinstance(email, str):
            return False
        return '@' in email and '.' in email.split('@')[-1]

    def _validate_pattern(self, value: str, pattern: str) -> bool:
        """驗證模式（簡化版）"""
        # 這裡應該使用正則表達式
        return True  # 簡化處理


class DynamicFormHandler:
    """
    動態表單處理器

    處理動態加載和變化的表單。
    """

    def __init__(self):
        """初始化動態表單處理器"""
        print("[DynamicFormHandler] 初始化完成")

    def wait_for_field(
        self,
        selector: str,
        timeout: float = 10.0
    ) -> bool:
        """
        等待字段出現

        Args:
            selector: 字段選擇器
            timeout: 超時時間

        Returns:
            是否出現
        """
        print(f"[DynamicFormHandler] 等待字段: {selector}")

        start_time = time.time()

        while time.time() - start_time < timeout:
            # 模擬檢查字段是否存在
            if random.choice([True, False, False]):  # 33% 機率找到
                print(f"  ✓ 字段已出現")
                return True

            time.sleep(0.1)

        print(f"  ✗ 等待超時")
        return False

    def handle_conditional_fields(
        self,
        trigger_field: FormField,
        conditional_fields: List[FormField]
    ):
        """
        處理條件顯示的字段

        Args:
            trigger_field: 觸發字段
            conditional_fields: 條件字段列表
        """
        print(f"\n[DynamicFormHandler] 處理條件字段")
        print(f"  觸發字段: {trigger_field.name} = {trigger_field.value}")

        # 模擬條件邏輯
        show_fields = trigger_field.value == "yes"

        if show_fields:
            print(f"  顯示 {len(conditional_fields)} 個條件字段")
            for field in conditional_fields:
                print(f"    - {field.name}")
        else:
            print(f"  隱藏條件字段")

    def handle_cascading_select(
        self,
        parent_field: FormField,
        child_field: FormField,
        options_map: Dict[str, List[str]]
    ):
        """
        處理級聯選擇

        Args:
            parent_field: 父級字段
            child_field: 子級字段
            options_map: 選項映射
        """
        print(f"\n[DynamicFormHandler] 處理級聯選擇")
        print(f"  父級: {parent_field.name} = {parent_field.value}")

        parent_value = str(parent_field.value)
        child_options = options_map.get(parent_value, [])

        print(f"  子級選項: {child_options}")

        if child_options:
            child_field.value = child_options[0]
            print(f"  選擇: {child_field.value}")


class BatchFormSubmitter:
    """
    批量表單提交器

    批量提交多個表單。
    """

    def __init__(self, form_filler: FormFiller):
        """
        初始化批量提交器

        Args:
            form_filler: 表單填充器
        """
        self.form_filler = form_filler
        self.results: List[Dict] = []
        print("[BatchFormSubmitter] 初始化完成")

    def submit_batch(
        self,
        forms: List[FormData],
        delay_between_forms: float = 1.0
    ) -> List[Dict]:
        """
        批量提交表單

        Args:
            forms: 表單數據列表
            delay_between_forms: 表單之間的延遲

        Returns:
            提交結果列表
        """
        print(f"\n[BatchFormSubmitter] 開始批量提交 {len(forms)} 個表單")
        print("=" * 60)

        self.results.clear()

        for i, form_data in enumerate(forms, 1):
            print(f"\n表單 {i}/{len(forms)}")
            print("-" * 60)

            start_time = time.time()

            try:
                success = self.form_filler.fill_form(form_data)
                elapsed = time.time() - start_time

                result = {
                    "index": i,
                    "success": success,
                    "elapsed_time": elapsed,
                    "fields_count": len(form_data.fields)
                }

                self.results.append(result)

                print(f"結果: {'成功' if success else '失敗'} ({elapsed:.2f}秒)")

            except Exception as e:
                print(f"錯誤: {str(e)}")
                self.results.append({
                    "index": i,
                    "success": False,
                    "error": str(e)
                })

            # 延遲
            if i < len(forms) and delay_between_forms > 0:
                print(f"\n等待 {delay_between_forms}秒...")
                time.sleep(delay_between_forms)

        # 統計
        success_count = sum(1 for r in self.results if r.get("success"))

        print("\n" + "=" * 60)
        print(f"批量提交完成: {success_count}/{len(forms)} 個成功")
        print("=" * 60 + "\n")

        return self.results

    def get_statistics(self) -> Dict:
        """獲取統計信息"""
        if not self.results:
            return {}

        success_count = sum(1 for r in self.results if r.get("success"))
        total_time = sum(r.get("elapsed_time", 0) for r in self.results)
        avg_time = total_time / len(self.results) if self.results else 0

        return {
            "total_forms": len(self.results),
            "successful": success_count,
            "failed": len(self.results) - success_count,
            "success_rate": (success_count / len(self.results) * 100) if self.results else 0,
            "total_time": total_time,
            "average_time": avg_time
        }


def example_basic_form():
    """示例1: 基礎表單填寫"""
    print("\n" + "=" * 60)
    print("示例1: 基礎表單填寫")
    print("=" * 60 + "\n")

    # 創建表單數據
    form_data = FormData(
        fields=[
            FormField("username", "#username", InputType.TEXT, "john_doe"),
            FormField("email", "#email", InputType.EMAIL, "john@example.com"),
            FormField("password", "#password", InputType.PASSWORD, "SecurePass123"),
            FormField("age", "#age", InputType.NUMBER, 25),
        ],
        submit_button_selector="#submit"
    )

    # 填充表單
    filler = FormFiller(simulate_human=True)
    filler.fill_form(form_data)


def example_complex_form():
    """示例2: 複雜表單處理"""
    print("\n" + "=" * 60)
    print("示例2: 複雜表單處理")
    print("=" * 60 + "\n")

    # 創建複雜表單
    form_data = FormData(
        fields=[
            FormField("name", "#name", InputType.TEXT, "張三", required=True),
            FormField("email", "#email", InputType.EMAIL, "zhang@example.com", required=True,
                     validations=[{"rule": ValidationRule.EMAIL.value}]),
            FormField("phone", "#phone", InputType.TEL, "0912-345-678"),
            FormField("gender", "#gender", InputType.RADIO, "male"),
            FormField("interests", "#interests", InputType.CHECKBOX, True),
            FormField("country", "#country", InputType.SELECT, "Taiwan"),
            FormField("bio", "#bio", InputType.TEXTAREA, "這是一段個人簡介..."),
            FormField("birthdate", "#birthdate", InputType.DATE, "1990-01-01"),
        ]
    )

    # 驗證並填充
    validator = FormValidator()
    validation_result = validator.validate_form(form_data)

    if validation_result["is_valid"]:
        filler = FormFiller()
        filler.fill_form(form_data)


def example_file_upload():
    """示例3: 文件上傳"""
    print("\n" + "=" * 60)
    print("示例3: 文件上傳表單")
    print("=" * 60 + "\n")

    # 創建文件上傳表單
    form_data = FormData(
        fields=[
            FormField("title", "#title", InputType.TEXT, "文檔標題"),
            FormField("description", "#description", InputType.TEXTAREA, "文檔描述"),
            FormField("file", "#file", InputType.FILE, "/path/to/document.pdf"),
            FormField("category", "#category", InputType.SELECT, "documents"),
        ]
    )

    filler = FormFiller()
    filler.fill_form(form_data)


def example_dynamic_form():
    """示例4: 動態表單"""
    print("\n" + "=" * 60)
    print("示例4: 動態表單處理")
    print("=" * 60 + "\n")

    handler = DynamicFormHandler()

    # 條件字段
    trigger = FormField("has_company", "#has_company", InputType.RADIO, "yes")
    conditional = [
        FormField("company_name", "#company_name", InputType.TEXT, "ABC Company"),
        FormField("position", "#position", InputType.TEXT, "Engineer"),
    ]

    handler.handle_conditional_fields(trigger, conditional)

    # 級聯選擇
    country = FormField("country", "#country", InputType.SELECT, "Taiwan")
    city = FormField("city", "#city", InputType.SELECT, "")

    options_map = {
        "Taiwan": ["Taipei", "Taichung", "Kaohsiung"],
        "Japan": ["Tokyo", "Osaka", "Kyoto"],
    }

    handler.handle_cascading_select(country, city, options_map)


def example_batch_submission():
    """示例5: 批量提交"""
    print("\n" + "=" * 60)
    print("示例5: 批量表單提交")
    print("=" * 60 + "\n")

    # 創建多個表單
    forms = []
    for i in range(3):
        form = FormData(
            fields=[
                FormField("name", "#name", InputType.TEXT, f"User {i + 1}"),
                FormField("email", "#email", InputType.EMAIL, f"user{i + 1}@example.com"),
                FormField("message", "#message", InputType.TEXTAREA, f"Message from user {i + 1}"),
            ]
        )
        forms.append(form)

    # 批量提交
    filler = FormFiller(simulate_human=False)  # 不模擬人類行為以加快速度
    submitter = BatchFormSubmitter(filler)
    results = submitter.submit_batch(forms, delay_between_forms=0.5)

    # 顯示統計
    stats = submitter.get_statistics()
    print("\n批量提交統計:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  - {key}: {value:.2f}")
        else:
            print(f"  - {key}: {value}")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Browserbase 表單自動化示例")
    print("=" * 60)

    # 添加 random 導入以支持動態表單示例
    import random
    globals()['random'] = random

    # 運行所有示例
    example_basic_form()
    example_complex_form()
    example_file_upload()
    example_dynamic_form()
    example_batch_submission()

    print("\n" + "=" * 60)
    print("所有示例完成！")
    print("=" * 60 + "\n")

    print("最佳實踐:")
    print("- 填寫表單前先進行驗證")
    print("- 模擬人類行為避免被檢測")
    print("- 處理動態加載的字段")
    print("- 適當添加延遲和等待")
    print("- 批量操作時控制速率")


if __name__ == "__main__":
    main()
