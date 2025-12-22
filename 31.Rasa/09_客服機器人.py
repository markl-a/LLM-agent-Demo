"""
Rasa 客服機器人 - 完整實現案例

本文件涵蓋：
1. 客服系統需求分析
2. 多意圖處理
3. 工單創建和管理
4. 人工轉接
5. 客戶信息查詢
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowUpAction
import yaml
import json
from datetime import datetime
import sqlite3


# ==================== 1. 需求分析 ====================

def requirements_analysis():
    """
    客服系統需求分析
    """
    print("=" * 60)
    print("客服機器人需求分析")
    print("=" * 60)

    print("""
    【核心功能】
    1. 訂單查詢
       - 訂單狀態查詢
       - 物流追蹤
       - 訂單修改

    2. 產品諮詢
       - 產品信息查詢
       - 庫存查詢
       - 價格查詢

    3. 售後服務
       - 退換貨申請
       - 退款處理
       - 投訴處理

    4. 工單管理
       - 創建工單
       - 查詢工單
       - 更新工單

    5. 人工轉接
       - 複雜問題轉接
       - VIP 客戶優先
       - 工作時間檢查

    【對話流程】
    1. 問候識別客戶
    2. 意圖識別和分類
    3. 信息收集（表單）
    4. 業務處理（API/數據庫）
    5. 結果反饋
    6. 滿意度調查
    """)


# ==================== 2. Domain 配置 ====================

def customer_service_domain():
    """
    客服機器人 Domain 配置
    """
    print("\n" + "=" * 60)
    print("Domain 配置")
    print("=" * 60)

    domain = """
version: "3.1"

# ========== 意圖定義 ==========
intents:
  # 基本意圖
  - greet
  - goodbye
  - affirm
  - deny
  - thanks
  - bot_challenge

  # 查詢類
  - check_order_status
  - track_shipment
  - check_product_info
  - check_price
  - check_stock

  # 操作類
  - cancel_order
  - modify_order
  - request_refund
  - request_return
  - apply_warranty

  # 服務類
  - create_ticket
  - check_ticket
  - complaint
  - human_handoff
  - rate_service

# ========== 實體定義 ==========
entities:
  - order_id
  - product_name
  - ticket_id
  - phone_number
  - email
  - customer_id

# ========== 槽位定義 ==========
slots:
  # 客戶信息
  customer_id:
    type: text
    influence_conversation: true
    mappings:
    - type: from_entity
      entity: customer_id

  customer_name:
    type: text
    influence_conversation: false
    mappings:
    - type: custom

  customer_tier:
    type: categorical
    values:
      - VIP
      - Gold
      - Silver
      - Regular
    influence_conversation: true
    mappings:
    - type: custom

  phone_number:
    type: text
    influence_conversation: false
    mappings:
    - type: from_entity
      entity: phone_number

  email:
    type: text
    influence_conversation: false
    mappings:
    - type: from_entity
      entity: email

  # 訂單信息
  order_id:
    type: text
    influence_conversation: true
    mappings:
    - type: from_entity
      entity: order_id

  order_status:
    type: text
    influence_conversation: false
    mappings:
    - type: custom

  # 工單信息
  ticket_id:
    type: text
    influence_conversation: false
    mappings:
    - type: custom

  ticket_status:
    type: text
    influence_conversation: false
    mappings:
    - type: custom

  # 產品信息
  product_name:
    type: text
    influence_conversation: false
    mappings:
    - type: from_entity
      entity: product_name

  # 業務狀態
  authenticated:
    type: bool
    initial_value: false
    influence_conversation: true
    mappings:
    - type: custom

  issue_resolved:
    type: bool
    influence_conversation: false
    mappings:
    - type: custom

# ========== 響應模板 ==========
responses:
  utter_greet:
  - text: "您好！歡迎來到客服中心。我能為您做什麼？"

  utter_greet_vip:
  - text: "尊敬的 VIP 客戶，您好！我是您的專屬客服助手。"

  utter_ask_authenticate:
  - text: "為了保護您的隱私，請提供訂單編號或手機號碼進行驗證。"

  utter_authenticated:
  - text: "驗證成功！{customer_name} 您好。"

  utter_goodbye:
  - text: "感謝您的諮詢，祝您生活愉快！"
  - text: "再見！有任何問題隨時聯繫我們。"

  utter_thanks:
  - text: "不客氣！很高興能幫到您。"

  utter_iamabot:
  - text: "我是 AI 客服助手，可以幫您處理訂單、退換貨等問題。"

  utter_ask_satisfaction:
  - text: "請問這次服務您滿意嗎？"
    buttons:
    - title: "非常滿意"
      payload: "/rate_service{\"rating\": \"5\"}"
    - title: "滿意"
      payload: "/rate_service{\"rating\": \"4\"}"
    - title: "一般"
      payload: "/rate_service{\"rating\": \"3\"}"
    - title: "不滿意"
      payload: "/rate_service{\"rating\": \"2\"}"

  utter_transfer_to_human:
  - text: "我將為您轉接人工客服，請稍候..."

  utter_working_hours:
  - text: "目前非工作時間（9:00-18:00），我已為您創建工單，客服會盡快處理。"

# ========== 動作定義 ==========
actions:
  - action_authenticate_customer
  - action_check_order_status
  - action_track_shipment
  - action_search_product
  - action_create_ticket
  - action_check_ticket
  - action_process_refund
  - action_transfer_to_human
  - action_check_working_hours
  - action_save_rating

# ========== 表單定義 ==========
forms:
  refund_form:
    required_slots:
      - order_id
      - refund_reason
      - refund_amount

  ticket_form:
    required_slots:
      - issue_type
      - issue_description
      - contact_method
"""

    print(domain)
    return domain


# ==================== 3. 自定義動作實現 ====================

class ActionAuthenticateCustomer(Action):
    """
    客戶身份驗證
    """

    def name(self) -> Text:
        return "action_authenticate_customer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 獲取驗證信息
        order_id = tracker.get_slot("order_id")
        phone_number = tracker.get_slot("phone_number")

        if not order_id and not phone_number:
            dispatcher.utter_message(response="utter_ask_authenticate")
            return []

        # 查詢客戶信息（模擬數據庫查詢）
        customer_data = self._verify_customer(order_id, phone_number)

        if customer_data:
            dispatcher.utter_message(
                text=f"驗證成功！{customer_data['name']} 您好。"
            )

            return [
                SlotSet("authenticated", True),
                SlotSet("customer_id", customer_data['id']),
                SlotSet("customer_name", customer_data['name']),
                SlotSet("customer_tier", customer_data['tier']),
                SlotSet("email", customer_data['email'])
            ]
        else:
            dispatcher.utter_message(
                text="抱歉，驗證失敗。請確認訂單編號或手機號碼是否正確。"
            )
            return [SlotSet("authenticated", False)]

    def _verify_customer(self, order_id, phone_number):
        """驗證客戶（實際應查詢數據庫）"""
        # 模擬客戶數據
        customers = {
            "ORD123456": {
                "id": "CUST001",
                "name": "張小明",
                "tier": "VIP",
                "email": "zhang@example.com",
                "phone": "0912345678"
            }
        }

        if order_id in customers:
            return customers[order_id]
        return None


class ActionCheckOrderStatus(Action):
    """
    查詢訂單狀態
    """

    def name(self) -> Text:
        return "action_check_order_status"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        order_id = tracker.get_slot("order_id")

        if not order_id:
            dispatcher.utter_message(text="請提供訂單編號。")
            return []

        # 查詢訂單（模擬）
        order = self._get_order_info(order_id)

        if order:
            message = f"訂單 {order_id} 狀態：\n\n"
            message += f"📦 訂單狀態：{order['status']}\n"
            message += f"📅 下單時間：{order['order_date']}\n"
            message += f"💰 訂單金額：${order['amount']}\n"
            message += f"🚚 預計送達：{order['estimated_delivery']}\n"

            if order.get('tracking_number'):
                message += f"📍 追蹤號碼：{order['tracking_number']}"

            dispatcher.utter_message(text=message)

            return [
                SlotSet("order_status", order['status']),
                SlotSet("issue_resolved", True)
            ]
        else:
            dispatcher.utter_message(
                text=f"抱歉，找不到訂單 {order_id}。請確認訂單編號是否正確。"
            )
            return [SlotSet("issue_resolved", False)]

    def _get_order_info(self, order_id):
        """獲取訂單信息（實際應查詢數據庫）"""
        orders = {
            "ORD123456": {
                "status": "運送中",
                "order_date": "2024-12-15",
                "amount": 999,
                "estimated_delivery": "2024-12-20",
                "tracking_number": "TW1234567890"
            }
        }
        return orders.get(order_id)


class ActionCreateTicket(Action):
    """
    創建客服工單
    """

    def name(self) -> Text:
        return "action_create_ticket"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 收集工單信息
        customer_id = tracker.get_slot("customer_id")
        issue_type = tracker.get_slot("issue_type")
        issue_description = tracker.latest_message.get('text')
        order_id = tracker.get_slot("order_id")

        # 創建工單（模擬）
        ticket_id = self._create_ticket(
            customer_id, issue_type, issue_description, order_id
        )

        message = f"✅ 工單已創建\n\n"
        message += f"工單編號：{ticket_id}\n"
        message += f"問題類型：{issue_type}\n"
        message += f"狀態：待處理\n\n"
        message += f"我們會在 24 小時內回覆您。"

        dispatcher.utter_message(text=message)

        return [
            SlotSet("ticket_id", ticket_id),
            SlotSet("ticket_status", "pending")
        ]

    def _create_ticket(self, customer_id, issue_type, description, order_id):
        """創建工單（實際應寫入數據庫）"""
        import uuid
        ticket_id = f"TKT{str(uuid.uuid4())[:8].upper()}"

        # 模擬數據庫插入
        # INSERT INTO tickets (id, customer_id, type, description, order_id, status, created_at)
        # VALUES (ticket_id, customer_id, issue_type, description, order_id, 'pending', NOW())

        return ticket_id


class ActionTransferToHuman(Action):
    """
    轉接人工客服
    """

    def name(self) -> Text:
        return "action_transfer_to_human"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        customer_tier = tracker.get_slot("customer_tier")

        # 檢查工作時間
        if not self._is_working_hours():
            dispatcher.utter_message(response="utter_working_hours")
            # 自動創建工單
            return [FollowUpAction("action_create_ticket")]

        # VIP 客戶優先處理
        if customer_tier == "VIP":
            priority = "high"
            message = "正在為您連接 VIP 專屬客服..."
        else:
            priority = "normal"
            message = "正在為您轉接客服人員..."

        dispatcher.utter_message(text=message)

        # 通知客服系統（實際應調用 API）
        self._notify_agent(tracker, priority)

        return []

    def _is_working_hours(self):
        """檢查是否在工作時間"""
        now = datetime.now()
        hour = now.hour
        # 工作時間：9:00 - 18:00
        return 9 <= hour < 18

    def _notify_agent(self, tracker, priority):
        """通知人工客服（實際應調用客服系統 API）"""
        # 發送通知給客服系統
        # POST /api/agent/assign
        pass


# ==================== 4. 表單驗證 ====================

class ValidateRefundForm(FormValidationAction):
    """
    退款表單驗證
    """

    def name(self) -> Text:
        return "validate_refund_form"

    def validate_order_id(
        self, slot_value, dispatcher, tracker, domain
    ) -> Dict[Text, Any]:
        """驗證訂單編號"""

        # 檢查訂單是否存在
        order = self._check_order_exists(slot_value)

        if not order:
            dispatcher.utter_message(text="找不到該訂單，請確認訂單編號。")
            return {"order_id": None}

        # 檢查是否可退款
        if not self._can_refund(order):
            dispatcher.utter_message(
                text="抱歉，該訂單不符合退款條件（超過退款期限或已退款）。"
            )
            return {"order_id": None}

        return {"order_id": slot_value}

    def validate_refund_reason(
        self, slot_value, dispatcher, tracker, domain
    ) -> Dict[Text, Any]:
        """驗證退款原因"""

        valid_reasons = [
            "商品瑕疵", "尺寸不合", "與描述不符",
            "不需要了", "重複下單", "其他"
        ]

        if slot_value in valid_reasons:
            return {"refund_reason": slot_value}
        else:
            dispatcher.utter_message(
                text=f"請選擇退款原因：{', '.join(valid_reasons)}"
            )
            return {"refund_reason": None}

    def _check_order_exists(self, order_id):
        """檢查訂單是否存在"""
        # 模擬數據庫查詢
        return {"order_id": order_id, "status": "delivered"}

    def _can_refund(self, order):
        """檢查是否可以退款"""
        # 檢查退款條件
        return order['status'] == 'delivered'


# ==================== 5. Stories 配置 ====================

def customer_service_stories():
    """
    客服機器人對話故事
    """
    print("\n" + "=" * 60)
    print("對話故事")
    print("=" * 60)

    stories = """
version: "3.1"

stories:

# ========== 訂單查詢流程 ==========
- story: check order status
  steps:
  - intent: greet
  - action: utter_greet
  - intent: check_order_status
    entities:
    - order_id: "ORD123456"
  - action: action_authenticate_customer
  - slot_was_set:
    - authenticated: true
  - action: action_check_order_status
  - action: utter_ask_satisfaction
  - intent: thanks
  - action: utter_thanks
  - intent: goodbye
  - action: utter_goodbye

# ========== 退款流程 ==========
- story: refund request
  steps:
  - intent: request_refund
    entities:
    - order_id: "ORD123456"
  - action: action_authenticate_customer
  - action: refund_form
  - active_loop: refund_form
  - active_loop: null
  - action: action_process_refund
  - action: utter_ask_satisfaction

# ========== 投訴處理流程 ==========
- story: handle complaint
  steps:
  - intent: complaint
  - action: action_create_ticket
  - action: utter_ask_satisfaction

# ========== 人工轉接流程 ==========
- story: escalate to human
  steps:
  - intent: human_handoff
  - action: action_check_working_hours
  - action: action_transfer_to_human

# ========== VIP 客戶流程 ==========
- story: vip customer service
  steps:
  - intent: greet
  - action: action_authenticate_customer
  - slot_was_set:
    - customer_tier: "VIP"
  - action: utter_greet_vip
  - intent: check_order_status
  - action: action_check_order_status
"""

    print(stories)


# ==================== 主程序 ====================

def main():
    """
    主程序
    """
    print("\n" + "=" * 70)
    print("Rasa 客服機器人 - 完整實現")
    print("=" * 70)

    # 1. 需求分析
    requirements_analysis()

    # 2. Domain 配置
    customer_service_domain()

    # 3. Stories
    customer_service_stories()

    # 總結
    print("\n" + "=" * 70)
    print("實現要點")
    print("=" * 70)
    print("""
    【核心功能】
    ✓ 客戶身份驗證
    ✓ 訂單狀態查詢
    ✓ 工單創建管理
    ✓ 退款處理
    ✓ 人工轉接

    【技術特點】
    1. 多輪對話管理
    2. 表單數據收集
    3. 條件邏輯處理
    4. 外部系統整合
    5. 客戶分級服務

    【優化建議】
    1. 添加更多產品知識
    2. 整合真實訂單系統
    3. 實現智能推薦
    4. 添加情感分析
    5. 持續學習優化

    【下一步】
    學習 10_FAQ機器人.py - 實現 FAQ 問答系統
    """)


if __name__ == "__main__":
    main()
