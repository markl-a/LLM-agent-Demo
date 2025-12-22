"""
Rasa 表單處理 - Forms 和槽位填充

本文件涵蓋：
1. Form 表單定義
2. 槽位類型和驗證
3. 必填槽位和條件邏輯
4. 自定義槽位驗證
5. 表單激活、中斷和取消
"""

from typing import Any, Text, Dict, List, Optional
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet, EventType
import re


# ==================== 1. 表單基礎 ====================

def form_basics():
    """
    表單基礎概念
    """
    print("=" * 60)
    print("表單（Forms）基礎")
    print("=" * 60)

    print("""
    【什麼是 Forms】
    Forms 用於結構化數據收集，例如：
    - 餐廳預訂（時間、人數、日期）
    - 訂單創建（產品、數量、地址）
    - 客戶信息（姓名、電話、郵箱）
    - 工單提交（問題類型、描述）

    【表單工作流程】
    1. 激活表單（triggered by intent）
    2. 收集必填槽位
    3. 驗證每個槽位
    4. 完成後執行動作
    5. 停用表單

    【表單優勢】
    - 自動詢問缺失信息
    - 內建驗證機制
    - 處理用戶更正
    - 支持中斷和恢復
    """)


# ==================== 2. 簡單表單示例 ====================

def simple_form_example():
    """
    簡單表單配置示例
    """
    print("\n" + "=" * 60)
    print("簡單表單示例：餐廳預訂")
    print("=" * 60)

    # domain.yml 配置
    domain_config = """
version: "3.1"

intents:
  - request_restaurant        # 觸發預訂
  - inform                    # 提供信息

entities:
  - time
  - number
  - date

slots:
  time:
    type: text
    mappings:
    - type: from_entity
      entity: time

  number_of_people:
    type: float
    mappings:
    - type: from_entity
      entity: number

  date:
    type: text
    mappings:
    - type: from_entity
      entity: date

forms:
  restaurant_form:
    required_slots:
      - time
      - number_of_people
      - date

responses:
  utter_ask_time:
  - text: "請問您想預訂幾點？"

  utter_ask_number_of_people:
  - text: "請問有幾位用餐？"

  utter_ask_date:
  - text: "請問哪一天？"

  utter_submit:
  - text: "好的！已為您預訂 {date} {time}，{number_of_people} 位。"
"""

    print("\ndomain.yml 配置:")
    print(domain_config)

    # stories.yml 配置
    stories_config = """
version: "3.1"

stories:
  - story: restaurant booking
    steps:
    - intent: request_restaurant
    - action: restaurant_form          # 激活表單
    - active_loop: restaurant_form     # 表單循環
    - active_loop: null                # 表單結束
    - action: utter_submit
"""

    print("\nstories.yml 配置:")
    print(stories_config)

    # rules.yml 配置
    rules_config = """
version: "3.1"

rules:
  - rule: Activate restaurant form
    steps:
    - intent: request_restaurant
    - action: restaurant_form
    - active_loop: restaurant_form

  - rule: Submit restaurant form
    condition:
    - active_loop: restaurant_form
    steps:
    - action: restaurant_form
    - active_loop: null
    - slot_was_set:
      - requested_slot: null
    - action: utter_submit
"""

    print("\nrules.yml 配置:")
    print(rules_config)


# ==================== 3. 自定義槽位驗證 ====================

class ValidateRestaurantForm(FormValidationAction):
    """
    餐廳預訂表單驗證
    """

    def name(self) -> Text:
        return "validate_restaurant_form"

    def validate_time(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """驗證時間槽位"""

        # 接受的時間格式
        valid_times = [
            "11:00", "11:30", "12:00", "12:30",
            "17:00", "17:30", "18:00", "18:30",
            "19:00", "19:30", "20:00", "20:30"
        ]

        if slot_value in valid_times:
            return {"time": slot_value}
        else:
            dispatcher.utter_message(
                text=f"抱歉，{slot_value} 不在可預訂時段。\n"
                     f"請選擇以下時間：\n"
                     f"午餐：11:00-12:30\n"
                     f"晚餐：17:00-20:30"
            )
            return {"time": None}

    def validate_number_of_people(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """驗證人數槽位"""

        try:
            num = int(slot_value)
            if 1 <= num <= 10:
                return {"number_of_people": num}
            else:
                dispatcher.utter_message(
                    text="抱歉，我們只接受 1-10 人的預訂。\n"
                         "超過 10 人請致電預訂。"
                )
                return {"number_of_people": None}
        except (ValueError, TypeError):
            dispatcher.utter_message(text="請提供有效的人數（1-10）")
            return {"number_of_people": None}

    def validate_date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """驗證日期槽位"""

        from datetime import datetime, timedelta

        # 簡單日期解析
        today = datetime.now().date()
        max_date = today + timedelta(days=30)

        # 接受 "今天"、"明天"、"後天" 等
        if slot_value == "今天":
            date = today
        elif slot_value == "明天":
            date = today + timedelta(days=1)
        elif slot_value == "後天":
            date = today + timedelta(days=2)
        else:
            # 嘗試解析日期格式
            try:
                date = datetime.strptime(slot_value, "%Y-%m-%d").date()
            except ValueError:
                dispatcher.utter_message(
                    text="請提供有效的日期（例如：今天、明天、2024-12-25）"
                )
                return {"date": None}

        # 檢查日期範圍
        if today <= date <= max_date:
            return {"date": date.strftime("%Y-%m-%d")}
        else:
            dispatcher.utter_message(
                text=f"抱歉，只能預訂 30 天內的日期。"
            )
            return {"date": None}


# ==================== 4. 複雜表單示例 ====================

class ValidateOrderForm(FormValidationAction):
    """
    訂單表單驗證 - 複雜示例
    """

    def name(self) -> Text:
        return "validate_order_form"

    def validate_email(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """驗證電子郵件"""

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if re.match(email_pattern, slot_value):
            return {"email": slot_value}
        else:
            dispatcher.utter_message(text="請提供有效的電子郵件地址")
            return {"email": None}

    def validate_phone(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """驗證電話號碼"""

        # 台灣手機格式：09xxxxxxxx
        phone_pattern = r'^09\d{8}$'

        # 移除空格和破折號
        clean_phone = slot_value.replace(" ", "").replace("-", "")

        if re.match(phone_pattern, clean_phone):
            return {"phone": clean_phone}
        else:
            dispatcher.utter_message(
                text="請提供有效的手機號碼（格式：09xxxxxxxx）"
            )
            return {"phone": None}

    def validate_address(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """驗證地址"""

        if len(slot_value) >= 10:
            return {"address": slot_value}
        else:
            dispatcher.utter_message(
                text="請提供完整的地址（至少 10 個字符）"
            )
            return {"address": None}

    def validate_payment_method(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """驗證付款方式"""

        valid_methods = ["信用卡", "貨到付款", "ATM轉帳", "電子錢包"]

        if slot_value in valid_methods:
            return {"payment_method": slot_value}
        else:
            dispatcher.utter_message(
                text=f"請選擇付款方式：{', '.join(valid_methods)}"
            )
            return {"payment_method": None}


# ==================== 5. 動態槽位 ====================

def dynamic_slots_example():
    """
    動態必填槽位示例
    """
    print("\n" + "=" * 60)
    print("動態必填槽位")
    print("=" * 60)

    example_code = '''
from typing import Text, List, Any, Dict
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

class ValidateShippingForm(FormValidationAction):
    """
    根據條件動態調整必填槽位
    """

    def name(self) -> Text:
        return "validate_shipping_form"

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Text]:
        """動態決定必填槽位"""

        required_slots = ["recipient_name", "phone", "address"]

        # 如果選擇公司地址，需要公司名稱
        address_type = tracker.get_slot("address_type")
        if address_type == "公司":
            required_slots.append("company_name")

        # 如果需要發票，需要統編
        need_invoice = tracker.get_slot("need_invoice")
        if need_invoice:
            required_slots.extend(["company_title", "tax_id"])

        return required_slots
'''

    print("\n動態槽位代碼示例:")
    print(example_code)


# ==================== 6. 表單中斷處理 ====================

def form_interruption_handling():
    """
    表單中斷處理
    """
    print("\n" + "=" * 60)
    print("表單中斷處理")
    print("=" * 60)

    # 處理表單中斷的規則
    interruption_rules = """
version: "3.1"

rules:
  # 允許在表單中查詢幫助
  - rule: Ask for help during form
    condition:
    - active_loop: restaurant_form
    steps:
    - intent: help
    - action: utter_help
    - action: restaurant_form
    - active_loop: restaurant_form

  # 允許在表單中取消
  - rule: Cancel form
    condition:
    - active_loop: restaurant_form
    steps:
    - intent: stop
    - action: utter_ask_continue
    - action: action_deactivate_loop
    - active_loop: null

  # 允許在表單中修改已填寫的信息
  - rule: Change slot during form
    condition:
    - active_loop: restaurant_form
    steps:
    - intent: inform
      entities:
      - time
    - action: restaurant_form
    - active_loop: restaurant_form
"""

    print("\n表單中斷規則:")
    print(interruption_rules)

    # 自定義中斷處理動作
    interruption_action = '''
from rasa_sdk import Action
from rasa_sdk.events import Form

class ActionAskContinue(Action):
    """詢問用戶是否繼續表單"""

    def name(self) -> Text:
        return "action_ask_continue"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(
            text="您想取消預訂嗎？",
            buttons=[
                {"title": "是的，取消", "payload": "/stop"},
                {"title": "不，繼續", "payload": "/affirm"}
            ]
        )
        return []

class ActionDeactivateLoop(Action):
    """停用表單"""

    def name(self) -> Text:
        return "action_deactivate_loop"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="好的，已取消預訂。")
        return [Form(None), SlotSet("requested_slot", None)]
'''

    print("\n中斷處理動作:")
    print(interruption_action)


# ==================== 7. 完整表單示例 ====================

def complete_form_example():
    """
    完整的客戶註冊表單示例
    """
    print("\n" + "=" * 60)
    print("完整示例：客戶註冊表單")
    print("=" * 60)

    # domain.yml
    domain = """
version: "3.1"

intents:
  - register
  - inform
  - affirm
  - deny
  - stop

entities:
  - name
  - email
  - phone
  - age

slots:
  name:
    type: text
    mappings:
    - type: from_entity
      entity: name

  email:
    type: text
    mappings:
    - type: from_entity
      entity: email

  phone:
    type: text
    mappings:
    - type: from_entity
      entity: phone

  age:
    type: float
    mappings:
    - type: from_entity
      entity: age

  agree_terms:
    type: bool
    mappings:
    - type: from_intent
      intent: affirm
      value: true
      conditions:
      - active_loop: registration_form
        requested_slot: agree_terms
    - type: from_intent
      intent: deny
      value: false
      conditions:
      - active_loop: registration_form
        requested_slot: agree_terms

forms:
  registration_form:
    required_slots:
      - name
      - email
      - phone
      - age
      - agree_terms

responses:
  utter_ask_name:
  - text: "請問您的姓名？"

  utter_ask_email:
  - text: "請提供您的電子郵件"

  utter_ask_phone:
  - text: "請提供您的手機號碼"

  utter_ask_age:
  - text: "請問您的年齡？"

  utter_ask_agree_terms:
  - text: "請閱讀並同意我們的服務條款"
    buttons:
    - title: "同意"
      payload: "/affirm"
    - title: "不同意"
      payload: "/deny"

  utter_registration_complete:
  - text: "註冊成功！歡迎 {name}！"

  utter_registration_failed:
  - text: "您必須同意服務條款才能註冊"
"""

    print("\ndomain.yml:")
    print(domain)

    # 驗證類
    validation_code = '''
class ValidateRegistrationForm(FormValidationAction):
    """註冊表單驗證"""

    def name(self) -> Text:
        return "validate_registration_form"

    def validate_name(self, slot_value, dispatcher, tracker, domain):
        """驗證姓名"""
        if len(slot_value) >= 2:
            return {"name": slot_value}
        else:
            dispatcher.utter_message(text="姓名至少需要 2 個字符")
            return {"name": None}

    def validate_email(self, slot_value, dispatcher, tracker, domain):
        """驗證郵箱"""
        if "@" in slot_value and "." in slot_value:
            return {"email": slot_value}
        else:
            dispatcher.utter_message(text="請提供有效的電子郵件")
            return {"email": None}

    def validate_age(self, slot_value, dispatcher, tracker, domain):
        """驗證年齡"""
        try:
            age = int(slot_value)
            if 18 <= age <= 120:
                return {"age": age}
            elif age < 18:
                dispatcher.utter_message(text="抱歉，您必須年滿 18 歲才能註冊")
                return {"age": None}
            else:
                dispatcher.utter_message(text="請提供有效的年齡")
                return {"age": None}
        except (ValueError, TypeError):
            dispatcher.utter_message(text="請提供有效的年齡數字")
            return {"age": None}

    def validate_agree_terms(self, slot_value, dispatcher, tracker, domain):
        """驗證是否同意條款"""
        if slot_value is True:
            return {"agree_terms": True}
        else:
            dispatcher.utter_message(text="感謝您的考慮。如果改變主意請隨時回來！")
            # 停止表單
            return {"agree_terms": False}
'''

    print("\n驗證代碼:")
    print(validation_code)


# ==================== 主程序 ====================

def main():
    """
    主程序
    """
    print("\n" + "=" * 70)
    print("Rasa 表單處理 - 完整指南")
    print("=" * 70)

    # 1. 基礎概念
    form_basics()

    # 2. 簡單示例
    simple_form_example()

    # 3. 動態槽位
    dynamic_slots_example()

    # 4. 中斷處理
    form_interruption_handling()

    # 5. 完整示例
    complete_form_example()

    # 6. 最佳實踐
    print("\n" + "=" * 70)
    print("表單處理最佳實踐")
    print("=" * 70)
    print("""
    【表單設計】
    1. 保持表單簡短（3-7 個槽位）
    2. 按邏輯順序排列槽位
    3. 提供清晰的提示問題
    4. 使用友好的錯誤訊息

    【槽位驗證】
    1. 驗證數據格式和範圍
    2. 提供具體的錯誤提示
    3. 允許多次嘗試
    4. 提供示例格式

    【用戶體驗】
    1. 允許中斷和恢復
    2. 支持修改已填寫的信息
    3. 顯示進度（可選）
    4. 提供取消選項

    【性能優化】
    1. 避免複雜的驗證邏輯
    2. 使用緩存減少 API 調用
    3. 異步處理耗時操作

    【常見槽位類型】
    - text: 文本（姓名、地址）
    - float: 數字（年齡、金額）
    - bool: 布爾值（是否同意）
    - categorical: 分類（VIP/Gold/Regular）
    - list: 列表（多選）

    【調試技巧】
    1. 使用 rasa shell --debug 查看槽位狀態
    2. 檢查 tracker.slots 查看當前值
    3. 記錄驗證失敗原因
    4. 測試各種輸入場景

    【下一步】
    學習 06_LLM整合.py - 將 LLM 整合到 Rasa
    """)


if __name__ == "__main__":
    main()
