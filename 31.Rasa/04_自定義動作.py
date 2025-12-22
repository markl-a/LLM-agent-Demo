"""
Rasa 自定義動作 - Custom Actions

本文件涵蓋：
1. Action Server 設置
2. 自定義 Action 類開發
3. API 調用和外部服務整合
4. 數據庫操作
5. 槽位操作和事件處理
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowUpAction, UserUtteranceReverted, AllSlotsReset
import requests
import json


# ==================== 1. Action Server 設置 ====================

def action_server_setup():
    """
    Action Server 設置說明
    """
    print("=" * 60)
    print("Action Server 設置")
    print("=" * 60)

    print("""
    【什麼是 Action Server】
    Action Server 是一個獨立的服務，用於執行自定義動作：
    - 調用外部 API
    - 數據庫操作
    - 業務邏輯處理
    - 動態生成回覆

    【啟動 Action Server】
    命令：rasa run actions

    默認端口：5055

    【endpoints.yml 配置】
    """)

    endpoints_config = """
action_endpoint:
  url: "http://localhost:5055/webhook"
"""

    print(endpoints_config)

    print("\n【actions/actions.py 結構】")
    print("""
    actions/
    ├── __init__.py
    └── actions.py          # 自定義動作定義
    """)


# ==================== 2. 基本自定義動作 ====================

class ActionHelloWorld(Action):
    """
    最簡單的自定義動作示例
    """

    def name(self) -> Text:
        """動作名稱"""
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """執行動作"""

        # 發送訊息給用戶
        dispatcher.utter_message(text="Hello World!")

        return []


class ActionTellTime(Action):
    """
    回覆當前時間
    """

    def name(self) -> Text:
        return "action_tell_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        from datetime import datetime

        # 獲取當前時間
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 發送訊息
        message = f"現在時間是：{current_time}"
        dispatcher.utter_message(text=message)

        return []


class ActionTellJoke(Action):
    """
    講笑話
    """

    def name(self) -> Text:
        return "action_tell_joke"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        import random

        jokes = [
            "為什麼程式設計師總是分不清萬聖節和聖誕節？\n因為 Oct 31 = Dec 25",
            "有 10 種人：懂二進制的和不懂二進制的。",
            "程式設計師最討厭的事情：\n1. 寫註釋\n2. 別人不寫註釋",
        ]

        joke = random.choice(jokes)
        dispatcher.utter_message(text=joke)

        return []


# ==================== 3. 槽位操作 ====================

class ActionSaveUserInfo(Action):
    """
    保存用戶信息到槽位
    """

    def name(self) -> Text:
        return "action_save_user_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 從實體中獲取用戶信息
        name = next(tracker.get_latest_entity_values("name"), None)
        email = next(tracker.get_latest_entity_values("email"), None)

        events = []

        # 設置槽位
        if name:
            events.append(SlotSet("user_name", name))

        if email:
            events.append(SlotSet("user_email", email))

        # 確認訊息
        if name and email:
            message = f"已保存您的信息：{name}, {email}"
        else:
            message = "請提供您的姓名和電子郵件"

        dispatcher.utter_message(text=message)

        return events


class ActionGetSlotValues(Action):
    """
    獲取和顯示槽位值
    """

    def name(self) -> Text:
        return "action_get_slot_values"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 獲取槽位值
        user_name = tracker.get_slot("user_name")
        user_email = tracker.get_slot("user_email")
        customer_tier = tracker.get_slot("customer_tier")

        # 構建訊息
        message = "當前槽位值：\n"
        message += f"- 姓名: {user_name}\n"
        message += f"- 電子郵件: {user_email}\n"
        message += f"- 客戶等級: {customer_tier}"

        dispatcher.utter_message(text=message)

        return []


class ActionResetSlots(Action):
    """
    重置所有槽位
    """

    def name(self) -> Text:
        return "action_reset_slots"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="已重置所有信息")

        # 重置所有槽位
        return [AllSlotsReset()]


# ==================== 4. API 調用 ====================

class ActionCheckWeather(Action):
    """
    調用天氣 API
    """

    def name(self) -> Text:
        return "action_check_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 獲取城市
        city = next(tracker.get_latest_entity_values("city"), "台北")

        try:
            # 調用天氣 API（示例）
            # api_key = "YOUR_API_KEY"
            # url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
            # response = requests.get(url)
            # data = response.json()

            # 模擬數據
            weather_data = {
                "temp": 25,
                "description": "晴天",
                "humidity": 60
            }

            message = f"{city} 的天氣：\n"
            message += f"溫度：{weather_data['temp']}°C\n"
            message += f"狀況：{weather_data['description']}\n"
            message += f"濕度：{weather_data['humidity']}%"

            dispatcher.utter_message(text=message)

        except Exception as e:
            dispatcher.utter_message(text=f"抱歉，無法獲取天氣信息：{str(e)}")

        return []


class ActionSearchProduct(Action):
    """
    搜索產品
    """

    def name(self) -> Text:
        return "action_search_product"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 獲取產品名稱
        product_name = next(tracker.get_latest_entity_values("product"), None)

        if not product_name:
            dispatcher.utter_message(text="請告訴我您想搜索的產品")
            return []

        try:
            # 調用產品 API（示例）
            # url = f"https://api.example.com/products/search?q={product_name}"
            # response = requests.get(url)
            # products = response.json()

            # 模擬產品數據
            products = [
                {"name": "iPhone 14", "price": 999, "stock": 10},
                {"name": "iPhone 14 Pro", "price": 1099, "stock": 5}
            ]

            if products:
                message = f"找到 {len(products)} 個產品：\n"
                for p in products:
                    message += f"\n- {p['name']}: ${p['price']} (庫存: {p['stock']})"
            else:
                message = f"未找到 '{product_name}' 相關產品"

            dispatcher.utter_message(text=message)

            # 保存搜索結果到槽位
            return [SlotSet("search_results", json.dumps(products))]

        except Exception as e:
            dispatcher.utter_message(text=f"搜索失敗：{str(e)}")
            return []


# ==================== 5. 數據庫操作 ====================

class ActionCheckOrderStatus(Action):
    """
    查詢訂單狀態（數據庫操作示例）
    """

    def name(self) -> Text:
        return "action_check_order_status"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 獲取訂單 ID
        order_id = next(tracker.get_latest_entity_values("order_id"), None)

        if not order_id:
            dispatcher.utter_message(text="請提供訂單編號")
            return []

        try:
            # 數據庫查詢（示例）
            # import sqlite3
            # conn = sqlite3.connect('orders.db')
            # cursor = conn.cursor()
            # cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
            # order = cursor.fetchone()
            # conn.close()

            # 模擬訂單數據
            order = {
                "order_id": order_id,
                "status": "運送中",
                "estimated_delivery": "2024-12-25",
                "tracking_number": "1234567890"
            }

            if order:
                message = f"訂單 {order_id} 狀態：\n"
                message += f"狀態：{order['status']}\n"
                message += f"預計送達：{order['estimated_delivery']}\n"
                message += f"追蹤號碼：{order['tracking_number']}"

                # 保存訂單信息到槽位
                return [
                    SlotSet("order_status", order['status']),
                    SlotSet("tracking_number", order['tracking_number'])
                ]
            else:
                message = f"找不到訂單 {order_id}"

            dispatcher.utter_message(text=message)

        except Exception as e:
            dispatcher.utter_message(text=f"查詢失敗：{str(e)}")

        return []


class ActionCreateTicket(Action):
    """
    創建客服工單
    """

    def name(self) -> Text:
        return "action_create_ticket"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 獲取用戶信息和問題
        user_email = tracker.get_slot("user_email")
        problem_description = tracker.latest_message.get('text')

        try:
            # 創建工單（數據庫操作）
            # import uuid
            # ticket_id = str(uuid.uuid4())[:8]
            # conn = sqlite3.connect('tickets.db')
            # cursor = conn.cursor()
            # cursor.execute(
            #     "INSERT INTO tickets (ticket_id, email, description, status) VALUES (?, ?, ?, ?)",
            #     (ticket_id, user_email, problem_description, 'open')
            # )
            # conn.commit()
            # conn.close()

            # 模擬工單創建
            ticket_id = "TKT12345"

            message = f"已創建工單 {ticket_id}\n"
            message += f"我們會在 24 小時內回覆到 {user_email}"

            dispatcher.utter_message(text=message)

            return [SlotSet("ticket_id", ticket_id)]

        except Exception as e:
            dispatcher.utter_message(text=f"創建工單失敗：{str(e)}")
            return []


# ==================== 6. 條件邏輯 ====================

class ActionCheckVIPStatus(Action):
    """
    檢查 VIP 狀態並提供不同回應
    """

    def name(self) -> Text:
        return "action_check_vip_status"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        customer_tier = tracker.get_slot("customer_tier")

        if customer_tier == "VIP":
            message = "尊敬的 VIP 客戶，您好！\n"
            message += "您享有以下特權：\n"
            message += "- 專屬客服通道\n"
            message += "- 優先處理訂單\n"
            message += "- 額外折扣優惠"

            # 觸發 VIP 專屬流程
            return [FollowUpAction("action_vip_benefits")]

        elif customer_tier == "Gold":
            message = "Gold 會員您好！\n"
            message += "感謝您的支持！"
        else:
            message = "歡迎！我能為您做什麼？"

        dispatcher.utter_message(text=message)

        return []


class ActionDecideNextAction(Action):
    """
    根據條件決定下一個動作
    """

    def name(self) -> Text:
        return "action_decide_next_action"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        order_value = tracker.get_slot("order_value")

        # 根據訂單金額決定流程
        if order_value and order_value > 1000:
            # 高價值訂單需要確認
            return [FollowUpAction("action_request_confirmation")]
        else:
            # 直接處理
            return [FollowUpAction("action_process_order")]


# ==================== 7. 錯誤處理和回退 ====================

class ActionDefaultFallback(Action):
    """
    自定義回退動作
    """

    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 獲取用戶輸入
        user_message = tracker.latest_message.get('text')

        # 記錄未能理解的訊息（用於改進）
        # log_unhandled_message(user_message)

        message = "抱歉，我沒有理解您的意思。\n"
        message += "您可以試試：\n"
        message += "- 查詢訂單\n"
        message += "- 搜索產品\n"
        message += "- 聯繫客服"

        dispatcher.utter_message(text=message)

        # 撤銷最後一次用戶輸入
        return [UserUtteranceReverted()]


class ActionHandleError(Action):
    """
    錯誤處理
    """

    def name(self) -> Text:
        return "action_handle_error"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        error_type = tracker.get_slot("error_type")

        if error_type == "order_not_found":
            message = "抱歉，找不到該訂單。\n"
            message += "請檢查訂單編號是否正確。"
        elif error_type == "product_out_of_stock":
            message = "抱歉，該產品已售罄。\n"
            message += "我可以為您推薦類似產品嗎？"
        else:
            message = "發生錯誤，請稍後再試。"

        dispatcher.utter_message(text=message)

        return []


# ==================== 8. 使用示例 ====================

def usage_examples():
    """
    使用示例
    """
    print("\n" + "=" * 60)
    print("自定義動作使用示例")
    print("=" * 60)

    # domain.yml 配置
    domain_config = """
version: "3.1"

actions:
  - action_hello_world
  - action_tell_time
  - action_tell_joke
  - action_save_user_info
  - action_check_weather
  - action_search_product
  - action_check_order_status
  - action_create_ticket
  - action_check_vip_status
  - action_default_fallback

slots:
  user_name:
    type: text
    influence_conversation: false

  user_email:
    type: text
    influence_conversation: false

  customer_tier:
    type: categorical
    values:
      - VIP
      - Gold
      - Regular
    influence_conversation: true

  order_status:
    type: text
    influence_conversation: true

  order_value:
    type: float
    influence_conversation: true
"""

    print("\ndomain.yml 配置:")
    print(domain_config)

    # stories.yml 使用
    stories_config = """
version: "3.1"

stories:
  - story: check weather
    steps:
    - intent: check_weather
      entities:
      - city: "台北"
    - action: action_check_weather

  - story: search and check order
    steps:
    - intent: check_order
      entities:
      - order_id: "ORD123"
    - action: action_check_order_status
    - intent: thanks
    - action: utter_youre_welcome
"""

    print("\nstories.yml 使用:")
    print(stories_config)


# ==================== 主程序 ====================

def main():
    """
    主程序
    """
    print("\n" + "=" * 70)
    print("Rasa 自定義動作 - 完整指南")
    print("=" * 70)

    # 1. 設置說明
    action_server_setup()

    # 2. 使用示例
    usage_examples()

    # 3. 最佳實踐
    print("\n" + "=" * 70)
    print("自定義動作最佳實踐")
    print("=" * 70)
    print("""
    【動作設計】
    1. 單一職責：一個動作做一件事
    2. 命名規範：使用 action_ 前綴
    3. 錯誤處理：捕獲異常並提供友好訊息
    4. 日誌記錄：記錄重要操作和錯誤

    【性能優化】
    1. 避免長時間阻塞操作
    2. 使用異步調用處理外部 API
    3. 實施緩存機制
    4. 設置超時限制

    【安全性】
    1. 驗證用戶輸入
    2. 保護敏感信息（API 密鑰等）
    3. 使用環境變量存儲配置
    4. 限制 API 調用頻率

    【測試】
    1. 單元測試每個動作
    2. 模擬外部服務
    3. 測試錯誤處理
    4. 集成測試完整流程

    【常見錯誤】
    ✗ 在動作中進行復雜的業務邏輯
    ✗ 忘記返回事件列表
    ✗ 沒有處理異常
    ✗ API 調用沒有超時設置

    【下一步】
    學習 05_表單處理.py - 實現結構化數據收集
    """)


if __name__ == "__main__":
    main()
