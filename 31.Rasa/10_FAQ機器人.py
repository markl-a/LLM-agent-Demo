"""
Rasa FAQ 機器人 - 智能問答系統

本文件涵蓋：
1. Response Selector 配置
2. FAQ 數據準備
3. 相似問題匹配
4. 知識庫管理
5. 多輪澄清對話
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import yaml


# ==================== 1. Response Selector 概述 ====================

def response_selector_overview():
    """
    Response Selector 概述
    """
    print("=" * 60)
    print("Response Selector 概述")
    print("=" * 60)

    print("""
    【什麼是 Response Selector】
    Response Selector 是 Rasa 用於處理 FAQ 和檢索式回覆的組件：
    - 從大量候選回覆中選擇最合適的
    - 支持多個檢索意圖（retrieval intents）
    - 高效處理大規模 FAQ

    【使用場景】
    1. FAQ 問答系統
    2. 閒聊（Chitchat）
    3. 小型對話（Small Talk）
    4. 產品說明
    5. 政策解釋

    【優勢】
    - 易於擴展（添加新 FAQ 不需要重新設計對話）
    - 性能高效（單次預測選擇回覆）
    - 易於維護（FAQ 集中管理）
    """)


# ==================== 2. 配置 Response Selector ====================

def configure_response_selector():
    """
    配置 Response Selector
    """
    print("\n" + "=" * 60)
    print("配置 Response Selector")
    print("=" * 60)

    # config.yml
    config = """
# config.yml
language: zh

pipeline:
  # 分詞
  - name: JiebaTokenizer

  # 特徵提取
  - name: CountVectorsFeaturizer
  - name: CountVectorsFeaturizer
    analyzer: char_wb
    min_ngram: 1
    max_ngram: 4

  # 意圖分類
  - name: DIETClassifier
    epochs: 100

  # Response Selector（處理 FAQ）
  - name: ResponseSelector
    epochs: 100
    retrieval_intent: faq           # FAQ 意圖名稱

  # 可以有多個 Response Selector
  - name: ResponseSelector
    epochs: 100
    retrieval_intent: chitchat      # 閒聊意圖

policies:
  - name: RulePolicy
  - name: MemoizationPolicy
  - name: TEDPolicy
    max_history: 5
    epochs: 100
"""

    print(config)


# ==================== 3. FAQ 訓練數據 ====================

def faq_training_data():
    """
    FAQ 訓練數據示例
    """
    print("\n" + "=" * 60)
    print("FAQ 訓練數據")
    print("=" * 60)

    # data/nlu.yml
    nlu_data = """
version: "3.1"

nlu:
# ========== FAQ - 檢索意圖 ==========

# 運送政策
- intent: faq/shipping
  examples: |
    - 運送需要多久？
    - 多久會到貨？
    - 什麼時候能收到？
    - 配送時間
    - 快遞幾天到
    - 運費多少
    - 免運條件
    - 可以指定送貨時間嗎

# 退貨政策
- intent: faq/return_policy
  examples: |
    - 可以退貨嗎？
    - 退貨政策
    - 退款流程
    - 不滿意可以退嗎
    - 退貨期限
    - 如何辦理退貨
    - 退貨運費誰付

# 付款方式
- intent: faq/payment_methods
  examples: |
    - 支持什麼付款方式？
    - 可以用信用卡嗎
    - 能貨到付款嗎
    - 接受哪些支付方式
    - 可以分期付款嗎
    - 支持電子錢包嗎

# 保固政策
- intent: faq/warranty
  examples: |
    - 保固多久？
    - 保固期限
    - 保固範圍
    - 如何申請保固
    - 保固包括什麼
    - 延長保固

# 會員制度
- intent: faq/membership
  examples: |
    - 如何成為會員？
    - 會員有什麼優惠
    - 會員等級
    - VIP 條件
    - 會員積分

# 訂單修改
- intent: faq/order_modification
  examples: |
    - 可以改訂單嗎？
    - 修改收貨地址
    - 取消訂單
    - 更改訂單
    - 訂單出錯了

# 產品資訊
- intent: faq/product_info
  examples: |
    - 產品規格
    - 產品參數
    - 產品介紹
    - 產品尺寸
    - 產品材質

# 庫存查詢
- intent: faq/stock
  examples: |
    - 有貨嗎？
    - 庫存狀況
    - 什麼時候補貨
    - 缺貨多久
    - 還有嗎

# ========== Chitchat - 閒聊 ==========

- intent: chitchat/ask_name
  examples: |
    - 你叫什麼名字？
    - 你的名字
    - 怎麼稱呼你
    - 你是誰

- intent: chitchat/ask_weather
  examples: |
    - 今天天氣如何？
    - 天氣好嗎
    - 會下雨嗎

- intent: chitchat/ask_time
  examples: |
    - 現在幾點？
    - 幾點了
    - 今天星期幾
"""

    print(nlu_data)

    # data/responses.yml
    responses_data = """
version: "3.1"

responses:
  # ========== FAQ 回覆 ==========

  utter_faq/shipping:
  - text: |
      📦 運送政策

      運送時間：
      • 一般商品：3-5 個工作日
      • 偏遠地區：5-7 個工作日

      運費：
      • 訂單滿 $500 免運費
      • 未滿 $500 運費 $60

      您可以在訂單詳情中追蹤物流狀態。

  utter_faq/return_policy:
  - text: |
      🔄 退貨政策

      退貨條件：
      • 購買後 7 天內
      • 商品未使用且包裝完整
      • 附上發票或收據

      退貨流程：
      1. 聯繫客服申請退貨
      2. 收到退貨編號
      3. 寄回商品
      4. 確認收貨後 7-14 天退款

      退貨運費：由顧客負擔（商品瑕疵除外）

  utter_faq/payment_methods:
  - text: |
      💳 付款方式

      我們支持以下付款方式：
      ✓ 信用卡（Visa、Master、JCB）
      ✓ ATM 轉帳
      ✓ 貨到付款（訂單 $2000 以下）
      ✓ 電子錢包（LINE Pay、街口支付）
      ✓ 分期付款（信用卡 3/6/12 期）

  utter_faq/warranty:
  - text: |
      🛡️ 保固政策

      保固期限：
      • 所有產品：1 年保固
      • 電子產品：2 年保固

      保固範圍：
      ✓ 製造瑕疵
      ✓ 功能故障

      不保固項目：
      ✗ 人為損壞
      ✗ 自然耗損

      保固服務：免費維修或更換

  utter_faq/membership:
  - text: |
      👑 會員制度

      會員等級：
      • Regular：註冊即享
      • Silver：累積消費 $5,000
      • Gold：累積消費 $20,000
      • VIP：累積消費 $50,000

      會員權益：
      ✓ 購物積分
      ✓ 生日優惠
      ✓ 優先客服
      ✓ 專屬折扣

  utter_faq/order_modification:
  - text: |
      ✏️ 訂單修改

      訂單成立後 24 小時內可以修改：
      • 收貨地址
      • 聯絡電話
      • 發票資訊

      如需修改，請：
      1. 提供訂單編號
      2. 說明要修改的內容

      注意：已出貨訂單無法修改

  utter_faq/product_info:
  - text: |
      📋 產品資訊

      請提供產品名稱，我會為您查詢詳細規格。

      或訪問我們的網站查看完整產品目錄：
      https://example.com/products

  utter_faq/stock:
  - text: |
      📦 庫存查詢

      請告訴我您想查詢的產品名稱，
      我會為您確認庫存狀況。

      熱門商品建議提前預訂！

  # ========== Chitchat 回覆 ==========

  utter_chitchat/ask_name:
  - text: "我是 AI 客服助手，您可以叫我小助手！"

  utter_chitchat/ask_weather:
  - text: "抱歉，我無法查詢天氣。我主要負責協助您處理購物相關問題。"

  utter_chitchat/ask_time:
  - text: "建議您查看手機或電腦上的時間。我主要負責協助購物相關問題喔！"
"""

    print("\n" + "=" * 60)
    print("FAQ 回覆數據")
    print("=" * 60)
    print(responses_data)


# ==================== 4. Rules 配置 ====================

def faq_rules():
    """
    FAQ Rules 配置
    """
    print("\n" + "=" * 60)
    print("FAQ Rules")
    print("=" * 60)

    rules = """
version: "3.1"

rules:

# FAQ 規則 - 自動回覆
- rule: Respond to FAQs
  steps:
  - intent: faq
  - action: utter_faq

# Chitchat 規則
- rule: Respond to chitchat
  steps:
  - intent: chitchat
  - action: utter_chitchat
"""

    print(rules)


# ==================== 5. 進階 FAQ 處理 ====================

class ActionSearchFAQ(Action):
    """
    智能 FAQ 搜索（支持相似問題匹配）
    """

    def name(self) -> Text:
        return "action_search_faq"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_question = tracker.latest_message.get('text')

        # 獲取 Response Selector 的預測
        retrieval_intent = tracker.latest_message.get('response', {}).get('intent_response_key')

        if retrieval_intent:
            # 如果 Response Selector 有高置信度的匹配
            confidence = tracker.latest_message.get('response', {}).get('confidence', 0)

            if confidence > 0.7:
                # 直接使用 Response Selector 的回覆
                return []
            else:
                # 置信度不高，提供相關 FAQ
                related_faqs = self._find_related_faqs(user_question)

                if related_faqs:
                    message = "您可能想問：\n"
                    for i, faq in enumerate(related_faqs, 1):
                        message += f"\n{i}. {faq['question']}"

                    dispatcher.utter_message(
                        text=message,
                        buttons=[
                            {"title": faq['question'], "payload": f"/faq/{faq['id']}"}
                            for faq in related_faqs
                        ]
                    )
                else:
                    dispatcher.utter_message(
                        text="抱歉，我沒有找到相關的常見問題。\n"
                             "您可以：\n"
                             "1. 換個方式描述您的問題\n"
                             "2. 聯繫人工客服"
                    )
        else:
            # 沒有匹配到檢索意圖
            dispatcher.utter_message(
                text="抱歉，我不太理解您的問題。請問您想了解：\n"
                     "• 運送政策\n"
                     "• 退貨政策\n"
                     "• 付款方式\n"
                     "• 保固政策\n"
                     "• 會員制度"
            )

        return []

    def _find_related_faqs(self, question):
        """查找相關 FAQ（實際應使用向量相似度）"""
        # 模擬相關 FAQ
        all_faqs = [
            {"id": "shipping", "question": "運送需要多久？"},
            {"id": "return", "question": "如何辦理退貨？"},
            {"id": "payment", "question": "支持哪些付款方式？"},
        ]

        # 簡單的關鍵詞匹配（實際應使用語義相似度）
        related = []
        keywords = question.lower()

        if "運送" in keywords or "配送" in keywords:
            related.append(all_faqs[0])
        if "退" in keywords:
            related.append(all_faqs[1])
        if "付款" in keywords or "支付" in keywords:
            related.append(all_faqs[2])

        return related[:3]


class ActionFeedbackFAQ(Action):
    """
    收集 FAQ 反饋
    """

    def name(self) -> Text:
        return "action_feedback_faq"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 詢問是否有幫助
        dispatcher.utter_message(
            text="這個回答對您有幫助嗎？",
            buttons=[
                {"title": "有幫助", "payload": "/affirm"},
                {"title": "沒幫助", "payload": "/deny"}
            ]
        )

        return []


class ActionHandleFAQDeny(Action):
    """
    處理 FAQ 無幫助的情況
    """

    def name(self) -> Text:
        return "action_handle_faq_deny"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            text="抱歉沒能幫到您。\n\n"
                 "您可以：\n"
                 "1. 換個方式描述問題\n"
                 "2. 轉接人工客服\n"
                 "3. 查看詳細幫助文檔"
        )

        return []


# ==================== 6. FAQ 知識庫管理 ====================

def faq_knowledge_base():
    """
    FAQ 知識庫管理
    """
    print("\n" + "=" * 60)
    print("FAQ 知識庫管理")
    print("=" * 60)

    print("""
    【知識庫結構】
    faq_knowledge_base/
    ├── categories.yml          # FAQ 分類
    ├── shipping.yml           # 運送相關
    ├── return.yml             # 退貨相關
    ├── payment.yml            # 付款相關
    └── product.yml            # 產品相關

    【categories.yml 示例】
    """)

    categories = """
categories:
  - id: shipping
    name: 運送政策
    icon: 📦
    subcategories:
      - 運送時間
      - 運費計算
      - 物流追蹤

  - id: return
    name: 退換貨
    icon: 🔄
    subcategories:
      - 退貨流程
      - 退款時間
      - 換貨政策

  - id: payment
    name: 付款方式
    icon: 💳
    subcategories:
      - 信用卡
      - ATM轉帳
      - 電子支付
"""

    print(categories)

    print("""
    【知識庫更新流程】
    1. 收集常見問題
       - 分析用戶諮詢
       - 識別高頻問題
       - 整理相似問題

    2. 編寫 FAQ
       - 清晰的問題描述
       - 詳細的答案
       - 提供示例和連結

    3. 添加訓練數據
       - 多種問法
       - 同義詞
       - 口語化表達

    4. 測試和優化
       - 測試識別準確率
       - 調整訓練數據
       - 優化回覆內容

    5. 定期維護
       - 更新過時信息
       - 添加新問題
       - 刪除無效 FAQ
    """)


# ==================== 7. 完整示例 ====================

def complete_faq_example():
    """
    完整的 FAQ 機器人示例
    """
    print("\n" + "=" * 60)
    print("完整 FAQ 機器人配置")
    print("=" * 60)

    # domain.yml
    domain = """
version: "3.1"

intents:
  - greet
  - goodbye
  - affirm
  - deny
  - faq
  - chitchat

responses:
  utter_greet:
  - text: "您好！我是 FAQ 助手，可以回答常見問題。"

  utter_goodbye:
  - text: "再見！如有其他問題歡迎隨時詢問。"

  utter_default:
  - text: "抱歉，我不太理解。您可以試試問我關於運送、退貨、付款的問題。"

actions:
  - action_search_faq
  - action_feedback_faq
  - action_handle_faq_deny
"""

    print(domain)

    # stories.yml
    stories = """
version: "3.1"

stories:
  - story: FAQ with feedback
    steps:
    - intent: faq
    - action: utter_faq
    - action: action_feedback_faq
    - intent: affirm
    - action: utter_thanks

  - story: FAQ without help
    steps:
    - intent: faq
    - action: utter_faq
    - action: action_feedback_faq
    - intent: deny
    - action: action_handle_faq_deny
"""

    print("\n" + "=" * 60)
    print("Stories 配置")
    print("=" * 60)
    print(stories)


# ==================== 主程序 ====================

def main():
    """
    主程序
    """
    print("\n" + "=" * 70)
    print("Rasa FAQ 機器人 - 完整指南")
    print("=" * 70)

    # 1. 概述
    response_selector_overview()

    # 2. 配置
    configure_response_selector()

    # 3. 訓練數據
    faq_training_data()

    # 4. Rules
    faq_rules()

    # 5. 知識庫管理
    faq_knowledge_base()

    # 6. 完整示例
    complete_faq_example()

    # 總結
    print("\n" + "=" * 70)
    print("FAQ 機器人最佳實踐")
    print("=" * 70)
    print("""
    【設計原則】
    1. FAQ 分類清晰
       - 按主題分類
       - 易於導航
       - 層級不超過 3 層

    2. 問答質量
       - 問題表述清晰
       - 答案簡潔明了
       - 提供具體信息

    3. 用戶體驗
       - 快速找到答案
       - 提供相關推薦
       - 支持反饋

    【優化建議】
    1. 數據優化
       - 每個 FAQ 至少 5-10 個問法
       - 包含同義詞和變體
       - 定期更新

    2. 匹配優化
       - 調整置信度閾值
       - 使用語義相似度
       - 提供多個候選答案

    3. 反饋循環
       - 收集用戶反饋
       - 分析未匹配問題
       - 持續改進

    【常見問題】
    Q: Response Selector 和 Stories 有什麼區別？
    A: Response Selector 用於單輪 FAQ，Stories 用於多輪對話

    Q: 如何處理相似問題？
    A: 使用同義詞、訓練更多變體、調整特徵提取

    Q: FAQ 數量很多時如何優化？
    A: 分類管理、使用檢索意圖、考慮向量數據庫

    【下一步】
    學習 11_Rasa_X.py - 使用 Rasa X 優化機器人
    """)


if __name__ == "__main__":
    main()
