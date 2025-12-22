"""
Rasa 對話故事 - Stories 和 Rules

本文件涵蓋：
1. Stories（對話故事）編寫
2. Rules（對話規則）定義
3. 對話策略（Policies）配置
4. 多輪對話設計
5. 對話分支和檢查點
"""

import yaml
from typing import List, Dict


# ==================== 1. Stories 基礎 ====================

def basic_stories():
    """
    Stories 基礎 - 對話流程示例
    """
    print("=" * 60)
    print("Stories（對話故事）")
    print("=" * 60)

    print("\nStories 是什麼？")
    print("""
    Stories 是用戶和機器人對話的訓練示例，包含：
    - 用戶意圖（intent）
    - 機器人動作（action）
    - 對話上下文（slots, entities）

    用於訓練對話策略模型，使機器人能夠預測下一步動作。
    """)

    # 簡單故事示例
    simple_stories = """
version: "3.1"

stories:

# 故事 1: 簡單問候
- story: simple greet
  steps:
  - intent: greet              # 用戶：你好
  - action: utter_greet        # 機器人：你好！

# 故事 2: 問候後告別
- story: greet and goodbye
  steps:
  - intent: greet
  - action: utter_greet
  - intent: goodbye            # 用戶：再見
  - action: utter_goodbye      # 機器人：拜拜！

# 故事 3: 開心路徑
- story: happy path
  steps:
  - intent: greet
  - action: utter_greet
  - intent: mood_great         # 用戶：我很開心
  - action: utter_happy        # 機器人：太好了！

# 故事 4: 不開心路徑
- story: sad path
  steps:
  - intent: greet
  - action: utter_greet
  - intent: mood_unhappy       # 用戶：我不開心
  - action: utter_cheer_up     # 機器人：這能讓你開心
  - action: utter_did_that_help
  - intent: affirm             # 用戶：是的
  - action: utter_happy
"""

    print("\n簡單故事示例:")
    print(simple_stories)


def stories_with_entities():
    """
    帶有實體的故事
    """
    print("\n" + "=" * 60)
    print("帶有實體的 Stories")
    print("=" * 60)

    entity_stories = """
version: "3.1"

stories:

# 訂單查詢故事
- story: check order with ID
  steps:
  - intent: check_order
    entities:                  # 提取的實體
    - order_id: "ORD123456"
  - slot_was_set:             # 設置槽位
    - order_id: "ORD123456"
  - action: action_check_order_status  # 自定義動作
  - action: utter_order_status

# 餐廳預訂故事
- story: book restaurant
  steps:
  - intent: book_restaurant
    entities:
    - time: "7pm"
    - number: "2"
    - date: "tomorrow"
  - slot_was_set:
    - time: "7pm"
    - number: "2"
    - date: "tomorrow"
  - action: action_book_table
  - action: utter_booking_confirmed

# 產品查詢故事
- story: product inquiry
  steps:
  - intent: search_product
    entities:
    - product: "iPhone 14"
  - slot_was_set:
    - product: "iPhone 14"
  - action: action_search_product
  - action: utter_product_info
"""

    print("\n帶實體的故事:")
    print(entity_stories)

    print("\n關鍵概念:")
    print("""
    1. entities: NLU 提取的實體
    2. slot_was_set: 槽位被設置（存儲狀態）
    3. 槽位影響對話流程（如果配置了 influence_conversation）
    """)


# ==================== 2. Rules 基礎 ====================

def basic_rules():
    """
    Rules 基礎 - 固定對話規則
    """
    print("\n" + "=" * 60)
    print("Rules（對話規則）")
    print("=" * 60)

    print("\nRules 是什麼？")
    print("""
    Rules 定義固定的對話模式，不需要機器學習：
    - 在任何時候都應該觸發的行為
    - 固定的問答對
    - FAQ 回答
    - 單輪對話

    與 Stories 的區別：
    - Stories: 需要訓練，處理複雜對話
    - Rules: 不需要訓練，處理固定模式
    """)

    simple_rules = """
version: "3.1"

rules:

# 規則 1: 隨時說再見
- rule: Say goodbye anytime
  steps:
  - intent: goodbye
  - action: utter_goodbye

# 規則 2: 隨時說謝謝
- rule: Say you're welcome
  steps:
  - intent: thanks
  - action: utter_youre_welcome

# 規則 3: 機器人挑戰
- rule: Bot challenge
  steps:
  - intent: bot_challenge
  - action: utter_iamabot

# 規則 4: 範圍外問題
- rule: Out of scope
  steps:
  - intent: out_of_scope
  - action: utter_out_of_scope

# 規則 5: 激活表單
- rule: Activate form
  steps:
  - intent: request_restaurant
  - action: restaurant_form          # 激活表單
  - active_loop: restaurant_form    # 表單循環

# 規則 6: 提交表單
- rule: Submit form
  condition:
  - active_loop: restaurant_form
  steps:
  - action: restaurant_form
  - active_loop: null               # 結束表單
  - slot_was_set:
    - requested_slot: null
  - action: utter_submit
"""

    print("\n基本規則示例:")
    print(simple_rules)


def rules_with_conditions():
    """
    帶有條件的規則
    """
    print("\n" + "=" * 60)
    print("帶有條件的 Rules")
    print("=" * 60)

    conditional_rules = """
version: "3.1"

rules:

# 條件規則：只在特定槽位值時觸發
- rule: Ask for confirmation if high value
  condition:
  - slot_was_set:
    - order_value: 1000           # 訂單金額 > 1000
  steps:
  - intent: place_order
  - action: utter_ask_confirmation

# 條件規則：基於上下文
- rule: VIP customer greeting
  condition:
  - slot_was_set:
    - customer_tier: "VIP"
  steps:
  - intent: greet
  - action: utter_greet_vip        # VIP 專屬問候

# 條件規則：處理表單中斷
- rule: Handle form interruption
  condition:
  - active_loop: booking_form
  steps:
  - intent: stop
  - action: utter_ask_continue
  - intent: affirm
  - action: booking_form
  - active_loop: booking_form

# 條件規則：FAQ 回答
- rule: FAQ - Return policy
  steps:
  - intent: faq
    entities:
    - faq_type: "return_policy"
  - action: utter_faq_return_policy
"""

    print("\n條件規則示例:")
    print(conditional_rules)


# ==================== 3. 對話策略配置 ====================

def policies_configuration():
    """
    對話策略（Policies）配置
    """
    print("\n" + "=" * 60)
    print("對話策略（Policies）配置")
    print("=" * 60)

    policies = {
        'policies': [
            # 1. RulePolicy - 處理規則
            {
                'name': 'RulePolicy',
                'core_fallback_threshold': 0.3,
                'core_fallback_action_name': 'action_default_fallback'
            },

            # 2. MemoizationPolicy - 記憶訓練故事
            {
                'name': 'MemoizationPolicy',
                'max_history': 5  # 記住最近 5 輪對話
            },

            # 3. TEDPolicy - 主要對話策略
            {
                'name': 'TEDPolicy',
                'max_history': 5,
                'epochs': 100,
                'constrain_similarities': True,
                'batch_size': [32, 64]
            },

            # 4. UnexpecTEDIntentPolicy - 處理意外意圖
            {
                'name': 'UnexpecTEDIntentPolicy',
                'max_history': 5,
                'epochs': 100
            }
        ]
    }

    print("\n策略配置:")
    print(yaml.dump(policies, allow_unicode=True))

    print("\n策略說明:")
    print("""
    【RulePolicy】
    - 處理 Rules 定義的固定模式
    - 不需要訓練數據
    - 優先級最高

    【MemoizationPolicy】
    - 記住訓練故事的精確序列
    - 如果當前對話與訓練故事匹配，直接預測
    - 適合處理常見路徑

    【TEDPolicy】
    - Transformer Embedding Dialogue Policy
    - 主要對話策略，處理複雜對話
    - 可以泛化到未見過的對話路徑

    【UnexpecTEDIntentPolicy】
    - 檢測意外意圖
    - 處理對話中的突然轉折
    """)


# ==================== 4. 多輪對話設計 ====================

def multi_turn_conversations():
    """
    多輪對話設計
    """
    print("\n" + "=" * 60)
    print("多輪對話設計")
    print("=" * 60)

    multi_turn_stories = """
version: "3.1"

stories:

# 複雜的訂單處理流程
- story: complete order process
  steps:
  # 第 1 輪：開始
  - intent: greet
  - action: utter_greet

  # 第 2 輪：產品查詢
  - intent: search_product
    entities:
    - product: "iPhone 14"
  - action: action_search_product
  - action: utter_product_info

  # 第 3 輪：詢問詳情
  - intent: ask_details
  - action: utter_product_details

  # 第 4 輪：加入購物車
  - intent: add_to_cart
  - action: action_add_to_cart
  - action: utter_added_to_cart

  # 第 5 輪：結帳
  - intent: checkout
  - action: checkout_form          # 啟動結帳表單
  - active_loop: checkout_form

  # 第 6 輪：確認訂單
  - action: checkout_form
  - active_loop: null
  - action: action_place_order
  - action: utter_order_confirmed

  # 第 7 輪：結束
  - intent: thanks
  - action: utter_youre_welcome

# 客戶服務對話
- story: customer service flow
  steps:
  # 問題識別
  - intent: have_problem
  - action: utter_ask_problem_type

  # 問題分類
  - intent: inform
    entities:
    - problem_type: "delivery"
  - slot_was_set:
    - problem_type: "delivery"

  # 收集訂單信息
  - action: utter_ask_order_id
  - intent: provide_order_id
    entities:
    - order_id: "ORD123"
  - slot_was_set:
    - order_id: "ORD123"

  # 查詢訂單
  - action: action_check_order
  - action: utter_order_status

  # 提供解決方案
  - action: utter_solution
  - intent: affirm
  - action: action_create_ticket
  - action: utter_ticket_created
"""

    print("\n多輪對話示例:")
    print(multi_turn_stories)


# ==================== 5. 對話分支和檢查點 ====================

def conversation_branches():
    """
    對話分支處理
    """
    print("\n" + "=" * 60)
    print("對話分支和檢查點")
    print("=" * 60)

    branching_stories = """
version: "3.1"

stories:

# 使用檢查點（Checkpoints）重用對話片段
- story: start of conversation
  steps:
  - intent: greet
  - action: utter_greet
  - checkpoint: greeted           # 檢查點

# 分支 1: 查詢訂單
- story: branch - check order
  steps:
  - checkpoint: greeted           # 從檢查點開始
  - intent: check_order
    entities:
    - order_id: "ORD123"
  - action: action_check_order
  - checkpoint: order_handled     # 新檢查點

# 分支 2: 產品查詢
- story: branch - search product
  steps:
  - checkpoint: greeted
  - intent: search_product
    entities:
    - product: "iPhone"
  - action: action_search_product
  - checkpoint: product_handled

# 統一結束
- story: end conversation from order
  steps:
  - checkpoint: order_handled
  - intent: thanks
  - action: utter_youre_welcome
  - intent: goodbye
  - action: utter_goodbye

- story: end conversation from product
  steps:
  - checkpoint: product_handled
  - intent: thanks
  - action: utter_youre_welcome
  - intent: goodbye
  - action: utter_goodbye

# OR 語句 - 處理多種可能
- story: product inquiry with variations
  steps:
  - intent: greet
  - action: utter_greet
  - or:                          # OR 語句
    - intent: search_product
    - intent: browse_products
    - intent: product_inquiry
  - action: action_show_products
"""

    print("\n分支對話示例:")
    print(branching_stories)

    print("\n檢查點使用場景:")
    print("""
    1. 重用對話片段
       - 避免重複編寫相同的對話流程
       - 提高維護性

    2. 處理多個入口
       - 多個對話路徑匯聚到同一點

    3. OR 語句
       - 處理語義相同的多個意圖
       - 減少故事數量

    注意：過度使用檢查點會降低可讀性
    """)


# ==================== 6. 最佳實踐 ====================

def best_practices():
    """
    Stories 和 Rules 最佳實踐
    """
    print("\n" + "=" * 60)
    print("Stories 和 Rules 最佳實踐")
    print("=" * 60)

    print("""
    【何時使用 Stories】
    ✓ 多輪對話流程
    ✓ 上下文相關的對話
    ✓ 需要預測下一步動作
    ✓ 複雜的業務流程

    【何時使用 Rules】
    ✓ 單輪問答
    ✓ FAQ
    ✓ 固定的回應模式
    ✓ 表單啟動和提交
    ✓ 任何時候都應該觸發的行為

    【Stories 編寫技巧】
    1. 涵蓋主要對話路徑
    2. 包含成功和失敗場景
    3. 考慮用戶可能的打斷
    4. 保持故事簡潔（5-15 步）
    5. 使用有意義的故事名稱
    6. 添加註釋說明業務邏輯

    【Rules 編寫技巧】
    1. 一個 Rule 處理一個固定模式
    2. 使用條件限制規則觸發
    3. 避免 Rules 之間衝突
    4. 優先使用 Rules 處理簡單場景

    【常見錯誤】
    ✗ Stories 過長（>20 步）
    ✗ 每個可能的對話都寫一個 Story
    ✗ Rules 和 Stories 處理相同場景
    ✗ 過度使用檢查點
    ✗ 忽略異常處理

    【測試建議】
    1. 使用 rasa test 驗證 Stories
    2. 創建測試故事（test_stories.yml）
    3. 檢查故事覆蓋率
    4. 使用 rasa shell --debug 調試
    """)


# ==================== 7. 實戰示例 ====================

def practical_example():
    """
    實戰示例：電商客服對話流程
    """
    print("\n" + "=" * 60)
    print("實戰示例：電商客服完整對話流程")
    print("=" * 60)

    ecommerce_stories = """
version: "3.1"

stories:

# ========== 訂單查詢流程 ==========
- story: order inquiry happy path
  steps:
  - intent: greet
  - action: utter_greet
  - intent: check_order
    entities:
    - order_id: "ORD123456"
  - slot_was_set:
    - order_id: "ORD123456"
  - action: action_fetch_order
  - action: utter_order_found
  - action: utter_order_details
  - intent: thanks
  - action: utter_youre_welcome

# 訂單不存在
- story: order not found
  steps:
  - intent: check_order
    entities:
    - order_id: "ORD999999"
  - action: action_fetch_order
  - slot_was_set:
    - order_found: false
  - action: utter_order_not_found
  - action: utter_ask_retry

# ========== 退款流程 ==========
- story: refund request
  steps:
  - intent: request_refund
    entities:
    - order_id: "ORD123"
  - action: action_check_refund_eligibility
  - slot_was_set:
    - refund_eligible: true
  - action: refund_form
  - active_loop: refund_form
  - active_loop: null
  - action: action_process_refund
  - action: utter_refund_confirmed

# 不符合退款條件
- story: refund not eligible
  steps:
  - intent: request_refund
  - action: action_check_refund_eligibility
  - slot_was_set:
    - refund_eligible: false
  - action: utter_refund_not_eligible
  - action: utter_explain_policy

# ========== 轉人工客服 ==========
- story: escalate to human
  steps:
  - intent: human_handoff
  - action: utter_transfer_to_human
  - action: action_notify_agent

rules:

# ========== 基本規則 ==========
- rule: Say goodbye
  steps:
  - intent: goodbye
  - action: utter_goodbye

- rule: Say thanks
  steps:
  - intent: thanks
  - action: utter_youre_welcome

# FAQ 規則
- rule: FAQ - shipping
  steps:
  - intent: faq
    entities:
    - faq_type: "shipping"
  - action: utter_faq_shipping

- rule: FAQ - return policy
  steps:
  - intent: faq
    entities:
    - faq_type: "return"
  - action: utter_faq_return
"""

    print(ecommerce_stories)


# ==================== 主程序 ====================

def main():
    """
    主程序
    """
    print("\n" + "=" * 70)
    print("Rasa 對話故事 - 完整指南")
    print("=" * 70)

    # 1. Stories 基礎
    basic_stories()
    stories_with_entities()

    # 2. Rules 基礎
    basic_rules()
    rules_with_conditions()

    # 3. Policies
    policies_configuration()

    # 4. 多輪對話
    multi_turn_conversations()

    # 5. 分支處理
    conversation_branches()

    # 6. 最佳實踐
    best_practices()

    # 7. 實戰示例
    practical_example()

    # 總結
    print("\n" + "=" * 70)
    print("總結")
    print("=" * 70)
    print("""
    對話管理是 Rasa 的核心功能：

    【關鍵概念】
    1. Stories: 訓練對話流程，處理複雜多輪對話
    2. Rules: 固定模式，處理簡單場景和 FAQ
    3. Policies: 決定下一步動作的策略
    4. Checkpoints: 重用對話片段

    【設計原則】
    - Stories 處理複雜流程
    - Rules 處理固定模式
    - 保持對話自然流暢
    - 處理邊緣情況和錯誤

    【下一步】
    學習 04_自定義動作.py - 實現業務邏輯
    """)


if __name__ == "__main__":
    main()
