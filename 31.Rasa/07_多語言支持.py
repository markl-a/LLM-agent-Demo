"""
Rasa 多語言支持 - 構建多語言對話系統

本文件涵蓋：
1. 多語言 NLU 訓練
2. 語言檢測
3. 跨語言實體提取
4. 多語言響應管理
5. 語言切換處理
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from langdetect import detect
import yaml


# ==================== 1. 多語言配置 ====================

def multilingual_configuration():
    """
    多語言配置說明
    """
    print("=" * 60)
    print("多語言配置")
    print("=" * 60)

    # 配置文件示例
    config_zh = """
# config.yml - 中文配置
language: zh

pipeline:
  - name: JiebaTokenizer              # 中文分詞
  - name: CountVectorsFeaturizer
  - name: CountVectorsFeaturizer
    analyzer: char_wb
    min_ngram: 1
    max_ngram: 4
  - name: DIETClassifier
    epochs: 100
  - name: EntitySynonymMapper
"""

    config_en = """
# config.yml - 英文配置
language: en

pipeline:
  - name: WhitespaceTokenizer         # 英文分詞
  - name: RegexFeaturizer
  - name: LexicalSyntacticFeaturizer
  - name: CountVectorsFeaturizer
  - name: CountVectorsFeaturizer
    analyzer: char_wb
    min_ngram: 1
    max_ngram: 4
  - name: DIETClassifier
    epochs: 100
  - name: EntitySynonymMapper
"""

    print("\n中文配置:")
    print(config_zh)

    print("\n英文配置:")
    print(config_en)

    print("""
    【多語言策略】
    1. 單一模型多語言
       - 優點：維護簡單
       - 缺點：性能可能不如分開
       - 適用：語言相似、數據量小

    2. 多個模型分開訓練
       - 優點：性能更好
       - 缺點：維護複雜
       - 適用：語言差異大、數據充足

    3. 零樣本跨語言（Zero-shot Cross-lingual）
       - 使用多語言預訓練模型（mBERT, XLM-R）
       - 在一種語言訓練，其他語言也能使用
    """)


# ==================== 2. 多語言訓練數據 ====================

def multilingual_training_data():
    """
    多語言訓練數據示例
    """
    print("\n" + "=" * 60)
    print("多語言訓練數據")
    print("=" * 60)

    # 繁體中文 + 英文
    multilingual_nlu = """
version: "3.1"

nlu:
# ========== 中文 ==========
- intent: greet
  examples: |
    - 你好
    - 嗨
    - 早安
    - 午安
    - 您好

- intent: goodbye
  examples: |
    - 再見
    - 拜拜
    - 回見
    - 掰掰

- intent: check_order
  examples: |
    - 我想查詢訂單 [ORD123](order_id)
    - 訂單 [ORD456](order_id) 在哪裡
    - 幫我查一下 [ORD789](order_id)

# ========== 英文 ==========
- intent: greet
  examples: |
    - hello
    - hi
    - good morning
    - good afternoon
    - hey

- intent: goodbye
  examples: |
    - goodbye
    - bye
    - see you
    - talk to you later

- intent: check_order
  examples: |
    - check order [ORD123](order_id)
    - where is order [ORD456](order_id)
    - track my order [ORD789](order_id)

# ========== 日文 ==========
- intent: greet
  examples: |
    - こんにちは
    - おはよう
    - こんばんは

- intent: goodbye
  examples: |
    - さようなら
    - またね
    - バイバイ
"""

    print("\n多語言 NLU 數據:")
    print(multilingual_nlu)


# ==================== 3. 語言檢測 ====================

class ActionDetectLanguage(Action):
    """
    檢測用戶使用的語言
    """

    def name(self) -> Text:
        return "action_detect_language"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get('text', '')

        try:
            # 檢測語言
            detected_lang = detect(user_message)

            # 語言映射
            lang_map = {
                'zh-cn': '簡體中文',
                'zh-tw': '繁體中文',
                'en': 'English',
                'ja': '日本語',
                'ko': '한국어'
            }

            language_name = lang_map.get(detected_lang, detected_lang)

            # 保存語言到槽位
            return [SlotSet("user_language", detected_lang)]

        except Exception as e:
            print(f"Language detection error: {str(e)}")
            # 默認使用繁體中文
            return [SlotSet("user_language", "zh-tw")]


class ActionLanguageGreeting(Action):
    """
    根據檢測到的語言問候
    """

    def name(self) -> Text:
        return "action_language_greeting"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_language = tracker.get_slot("user_language") or "zh-tw"

        # 多語言問候
        greetings = {
            "zh-tw": "您好！我能為您做什麼？",
            "zh-cn": "您好！我能为您做什么？",
            "en": "Hello! How can I help you?",
            "ja": "こんにちは！何かお手伝いできますか？",
            "ko": "안녕하세요! 무엇을 도와드릴까요?"
        }

        greeting = greetings.get(user_language, greetings["zh-tw"])
        dispatcher.utter_message(text=greeting)

        return []


# ==================== 4. 多語言響應 ====================

def multilingual_responses():
    """
    多語言響應配置
    """
    print("\n" + "=" * 60)
    print("多語言響應")
    print("=" * 60)

    # domain.yml 多語言響應
    domain_responses = """
version: "3.1"

responses:
  # 方法 1: 使用變量選擇語言
  utter_greet:
  - condition:
    - type: slot
      name: user_language
      value: zh-tw
    text: "您好！有什麼可以幫您的嗎？"

  - condition:
    - type: slot
      name: user_language
      value: en
    text: "Hello! How can I help you?"

  - condition:
    - type: slot
      name: user_language
      value: ja
    text: "こんにちは！何かお手伝いできますか？"

  # 方法 2: 所有語言一起（由 Action 選擇）
  utter_goodbye:
  - text: "再見！"          # 中文
  - text: "Goodbye!"      # 英文
  - text: "さようなら！"    # 日文

  utter_thanks:
  - text: "謝謝！"
  - text: "Thank you!"
  - text: "ありがとう！"
"""

    print(domain_responses)


class ActionMultilingualResponse(Action):
    """
    自定義多語言響應
    """

    def name(self) -> Text:
        return "action_multilingual_response"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_language = tracker.get_slot("user_language") or "zh-tw"
        intent = tracker.latest_message.get('intent', {}).get('name')

        # 多語言響應庫
        responses = {
            "check_order": {
                "zh-tw": "讓我幫您查詢訂單",
                "en": "Let me check your order",
                "ja": "ご注文を確認させていただきます"
            },
            "request_refund": {
                "zh-tw": "我將協助您處理退款",
                "en": "I'll help you with the refund",
                "ja": "返金のお手続きをさせていただきます"
            },
            "product_inquiry": {
                "zh-tw": "您想了解哪個產品？",
                "en": "Which product would you like to know about?",
                "ja": "どの製品についてお知りになりたいですか？"
            }
        }

        # 獲取對應語言的響應
        response_dict = responses.get(intent, {})
        response_text = response_dict.get(
            user_language,
            response_dict.get("zh-tw", "我能為您做什麼？")
        )

        dispatcher.utter_message(text=response_text)

        return []


# ==================== 5. 語言切換 ====================

class ActionSwitchLanguage(Action):
    """
    處理語言切換
    """

    def name(self) -> Text:
        return "action_switch_language"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 從實體中獲取目標語言
        target_language = next(
            tracker.get_latest_entity_values("language"),
            None
        )

        if not target_language:
            dispatcher.utter_message(
                text="請選擇語言：中文/English/日本語"
            )
            return []

        # 語言標準化
        language_map = {
            "中文": "zh-tw",
            "繁體中文": "zh-tw",
            "简体中文": "zh-cn",
            "英文": "en",
            "english": "en",
            "日文": "ja",
            "日本語": "ja",
            "한국어": "ko",
            "韓文": "ko"
        }

        lang_code = language_map.get(target_language.lower())

        if lang_code:
            # 切換確認訊息
            confirmations = {
                "zh-tw": f"已切換到繁體中文",
                "zh-cn": f"已切换到简体中文",
                "en": f"Switched to English",
                "ja": f"日本語に切り替えました",
                "ko": f"한국어로 전환되었습니다"
            }

            confirmation = confirmations.get(lang_code, "Language switched")
            dispatcher.utter_message(text=confirmation)

            return [SlotSet("user_language", lang_code)]
        else:
            dispatcher.utter_message(text="不支持的語言")
            return []


# ==================== 6. 多語言實體處理 ====================

def multilingual_entities():
    """
    多語言實體提取
    """
    print("\n" + "=" * 60)
    print("多語言實體提取")
    print("=" * 60)

    entity_examples = """
version: "3.1"

nlu:
# 產品名稱（多語言）
- intent: search_product
  examples: |
    - 我想買 [iPhone](product)
    - 有 [MacBook](product) 嗎
    - I want to buy [iPhone](product)
    - Do you have [MacBook](product)
    - [iPhone](product)を買いたい

# 同義詞（多語言）
- synonym: "iPhone"
  examples: |
    - 愛瘋
    - 蘋果手機
    - Apple phone
    - アイフォン

- synonym: "MacBook"
  examples: |
    - 蘋果筆電
    - Apple laptop
    - マックブック

# 日期（多語言）
- intent: book_appointment
  examples: |
    - 預約 [明天](date)
    - [下週一](date) 可以嗎
    - book for [tomorrow](date)
    - [next Monday](date) please
    - [明日](date)予約したい
"""

    print(entity_examples)


# ==================== 7. 使用預訓練多語言模型 ====================

def pretrained_multilingual_models():
    """
    使用預訓練多語言模型
    """
    print("\n" + "=" * 60)
    print("預訓練多語言模型")
    print("=" * 60)

    # 使用 mBERT 或 XLM-RoBERTa
    config_multilingual = """
# config.yml - 使用多語言 BERT
language: zh  # 主要語言

pipeline:
  # 使用 HuggingFace 的多語言模型
  - name: LanguageModelFeaturizer
    model_name: "bert-base-multilingual-cased"
    # 或使用 XLM-RoBERTa
    # model_name: "xlm-roberta-base"

  - name: DIETClassifier
    epochs: 100
    entity_recognition: True

  - name: EntitySynonymMapper

  - name: ResponseSelector
    epochs: 100
"""

    print(config_multilingual)

    print("""
    【預訓練多語言模型優勢】
    1. 零樣本跨語言能力
       - 在中文訓練，英文也能使用
       - 減少多語言訓練數據需求

    2. 更好的語義理解
       - 跨語言語義對齊
       - 處理代碼混合（code-mixing）

    3. 推薦模型
       - bert-base-multilingual-cased (104 語言)
       - xlm-roberta-base (100 語言)
       - distilbert-base-multilingual-cased (輕量版)
    """)


# ==================== 8. 完整多語言示例 ====================

def complete_multilingual_example():
    """
    完整的多語言客服示例
    """
    print("\n" + "=" * 60)
    print("完整多語言客服示例")
    print("=" * 60)

    # 完整配置
    complete_config = """
# domain.yml
version: "3.1"

intents:
  - greet
  - goodbye
  - switch_language
  - check_order
  - request_refund

entities:
  - language
  - order_id

slots:
  user_language:
    type: text
    initial_value: "zh-tw"
    influence_conversation: true

  order_id:
    type: text
    influence_conversation: false

actions:
  - action_detect_language
  - action_language_greeting
  - action_switch_language
  - action_multilingual_response

responses:
  utter_ask_language:
  - text: "請選擇語言 / Please select language / 言語を選択してください"
    buttons:
    - title: "繁體中文"
      payload: "/switch_language{\"language\": \"zh-tw\"}"
    - title: "English"
      payload: "/switch_language{\"language\": \"en\"}"
    - title: "日本語"
      payload: "/switch_language{\"language\": \"ja\"}"

# stories.yml
stories:
  - story: multilingual greeting
    steps:
    - intent: greet
    - action: action_detect_language
    - action: action_language_greeting

  - story: switch language
    steps:
    - intent: switch_language
      entities:
      - language: "en"
    - action: action_switch_language

# rules.yml
rules:
  - rule: Detect language on first message
    steps:
    - intent: greet
    - action: action_detect_language
"""

    print(complete_config)


# ==================== 主程序 ====================

def main():
    """
    主程序
    """
    print("\n" + "=" * 70)
    print("Rasa 多語言支持 - 完整指南")
    print("=" * 70)

    # 1. 配置
    multilingual_configuration()

    # 2. 訓練數據
    multilingual_training_data()

    # 3. 響應管理
    multilingual_responses()

    # 4. 實體處理
    multilingual_entities()

    # 5. 預訓練模型
    pretrained_multilingual_models()

    # 6. 完整示例
    complete_multilingual_example()

    # 最佳實踐
    print("\n" + "=" * 70)
    print("多語言支持最佳實踐")
    print("=" * 70)
    print("""
    【策略選擇】
    1. 少量語言（2-3種）：分開訓練模型
    2. 多種語言（4+種）：使用多語言預訓練模型
    3. 語言檢測：自動或讓用戶選擇

    【數據準備】
    1. 平衡各語言的訓練數據
    2. 使用母語者校對
    3. 考慮文化差異
    4. 處理方言和口語

    【響應管理】
    1. 集中管理翻譯
    2. 使用專業翻譯服務
    3. 保持術語一致性
    4. 定期更新翻譯

    【測試】
    1. 每種語言都要測試
    2. 測試語言切換流程
    3. 測試混合語言輸入
    4. 檢查字符編碼

    【性能優化】
    1. 緩存語言檢測結果
    2. 預加載常用翻譯
    3. 異步加載多語言模型

    【常見問題】
    Q: 如何處理代碼混合（中英混合）？
    A: 使用多語言模型，或分別提取不同語言的實體

    Q: 如何選擇默認語言？
    A: 基於用戶地理位置、瀏覽器語言或讓用戶選擇

    Q: 是否需要為每種語言訓練模型？
    A: 不一定。使用 mBERT/XLM-R 可以零樣本跨語言

    【下一步】
    學習 08_部署上線.py - 將機器人部署到生產環境
    """)


if __name__ == "__main__":
    main()
