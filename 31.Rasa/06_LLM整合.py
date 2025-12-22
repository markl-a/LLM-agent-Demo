"""
Rasa LLM 整合 - 與大語言模型整合

本文件涵蓋：
1. Rasa Pro CALM（Conversational AI with Language Models）
2. LLM 作為 NLU 後端
3. 混合對話策略（傳統 + LLM）
4. Prompt 工程
5. Fallback 和錯誤處理
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import openai
import os


# ==================== 1. LLM 整合概述 ====================

def llm_integration_overview():
    """
    LLM 整合概述
    """
    print("=" * 60)
    print("Rasa LLM 整合概述")
    print("=" * 60)

    print("""
    【為什麼整合 LLM】
    1. 處理開放式問題
    2. 生成自然的回覆
    3. 理解複雜意圖
    4. 減少訓練數據需求
    5. 提供創意性回答

    【整合方式】
    1. Rasa Pro CALM
       - 官方 LLM 整合方案
       - 結合傳統 NLU 和 LLM
       - 企業級支持

    2. 自定義 Action 調用 LLM
       - OpenAI API
       - Azure OpenAI
       - 本地部署的 LLM（Llama, ChatGLM 等）

    3. LLM 輔助 NLU
       - 意圖分類增強
       - 實體提取增強
       - Zero-shot/Few-shot 學習

    【混合策略】
    - 簡單查詢：傳統 NLU（快速、準確）
    - 複雜問題：LLM（靈活、智能）
    - 關鍵業務：傳統規則（可控、穩定）
    """)


# ==================== 2. 使用 OpenAI API ====================

class ActionLLMResponse(Action):
    """
    使用 OpenAI GPT 生成回覆
    """

    def name(self) -> Text:
        return "action_llm_response"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 獲取用戶輸入
        user_message = tracker.latest_message.get('text')

        # 獲取對話歷史
        conversation_history = self._get_conversation_history(tracker)

        try:
            # 設置 OpenAI API Key
            openai.api_key = os.getenv("OPENAI_API_KEY")

            # 構建 prompt
            messages = [
                {
                    "role": "system",
                    "content": "你是一個友好的客服助手，專門幫助用戶解決問題。"
                }
            ]

            # 添加歷史對話
            messages.extend(conversation_history)

            # 添加當前用戶訊息
            messages.append({
                "role": "user",
                "content": user_message
            })

            # 調用 OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=200
            )

            # 提取回覆
            llm_response = response.choices[0].message.content

            # 發送回覆
            dispatcher.utter_message(text=llm_response)

        except Exception as e:
            # 錯誤處理
            dispatcher.utter_message(
                text="抱歉，我遇到了一些問題。請稍後再試。"
            )
            print(f"LLM Error: {str(e)}")

        return []

    def _get_conversation_history(self, tracker: Tracker, max_turns: int = 5) -> List[Dict]:
        """獲取最近的對話歷史"""
        history = []
        events = tracker.events

        # 反向遍歷事件
        user_turns = 0
        for event in reversed(events):
            if user_turns >= max_turns:
                break

            if event.get("event") == "user":
                history.insert(0, {
                    "role": "user",
                    "content": event.get("text", "")
                })
                user_turns += 1

            elif event.get("event") == "bot":
                history.insert(0, {
                    "role": "assistant",
                    "content": event.get("text", "")
                })

        return history


# ==================== 3. 上下文感知的 LLM ====================

class ActionContextualLLM(Action):
    """
    帶上下文的 LLM 回覆（考慮槽位和用戶信息）
    """

    def name(self) -> Text:
        return "action_contextual_llm"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get('text')

        # 獲取用戶上下文
        user_name = tracker.get_slot("user_name") or "客戶"
        customer_tier = tracker.get_slot("customer_tier") or "Regular"
        order_id = tracker.get_slot("order_id")

        # 構建系統 prompt（包含上下文）
        system_prompt = f"""
你是一個專業的客服助手。

當前用戶信息：
- 姓名：{user_name}
- 會員等級：{customer_tier}
- 當前訂單：{order_id if order_id else "無"}

請根據用戶信息提供個性化的服務：
- VIP 客戶提供額外優惠
- Gold 客戶提供優先處理
- Regular 客戶提供標準服務

保持友好、專業的態度。
"""

        try:
            openai.api_key = os.getenv("OPENAI_API_KEY")

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=200
            )

            llm_response = response.choices[0].message.content
            dispatcher.utter_message(text=llm_response)

        except Exception as e:
            dispatcher.utter_message(text="抱歉，服務暫時不可用。")
            print(f"Error: {str(e)}")

        return []


# ==================== 4. LLM 輔助意圖分類 ====================

class ActionLLMIntentClassification(Action):
    """
    使用 LLM 進行意圖分類（Zero-shot）
    """

    def name(self) -> Text:
        return "action_llm_intent_classification"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get('text')

        # 定義可能的意圖
        intents = [
            "check_order - 查詢訂單狀態",
            "request_refund - 申請退款",
            "product_inquiry - 產品諮詢",
            "complaint - 投訴",
            "general_question - 一般問題"
        ]

        prompt = f"""
請判斷以下用戶訊息屬於哪個意圖，只返回意圖名稱：

可能的意圖：
{chr(10).join(intents)}

用戶訊息："{user_message}"

意圖：
"""

        try:
            openai.api_key = os.getenv("OPENAI_API_KEY")

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一個意圖分類助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=50
            )

            predicted_intent = response.choices[0].message.content.strip()

            # 記錄預測的意圖（用於分析）
            print(f"LLM Predicted Intent: {predicted_intent}")

            # 可以基於 LLM 的預測觸發不同的動作
            # ...

        except Exception as e:
            print(f"Intent classification error: {str(e)}")

        return []


# ==================== 5. LLM 生成式 FAQ ====================

class ActionGenerativeFAQ(Action):
    """
    使用 LLM 生成 FAQ 回答
    """

    def name(self) -> Text:
        return "action_generative_faq"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_question = tracker.latest_message.get('text')

        # 知識庫（可以從數據庫加載）
        knowledge_base = """
公司政策：
1. 退貨政策：購買後 7 天內可無條件退貨
2. 運送時間：一般 3-5 個工作日
3. 付款方式：支持信用卡、貨到付款、ATM 轉帳
4. 保固期限：所有產品 1 年保固
5. 客服時間：週一至週五 9:00-18:00

產品信息：
- iPhone 14：$999，黑色/白色/藍色
- MacBook Pro：$1999，14吋/16吋
- iPad Air：$599，64GB/256GB
"""

        prompt = f"""
基於以下知識庫，回答用戶問題。
如果知識庫中沒有相關信息，請禮貌地告知用戶並建議聯繫客服。

知識庫：
{knowledge_base}

用戶問題：{user_question}

回答：
"""

        try:
            openai.api_key = os.getenv("OPENAI_API_KEY")

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一個客服助手，基於知識庫準確回答問題。"
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # 較低的溫度以確保準確性
                max_tokens=200
            )

            answer = response.choices[0].message.content
            dispatcher.utter_message(text=answer)

        except Exception as e:
            dispatcher.utter_message(text="抱歉，無法處理您的問題。")
            print(f"FAQ Error: {str(e)}")

        return []


# ==================== 6. 混合策略 ====================

class ActionHybridResponse(Action):
    """
    混合策略：結合傳統 NLU 和 LLM
    """

    def name(self) -> Text:
        return "action_hybrid_response"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 獲取 NLU 的意圖和置信度
        intent = tracker.latest_message.get('intent', {}).get('name')
        confidence = tracker.latest_message.get('intent', {}).get('confidence', 0)

        user_message = tracker.latest_message.get('text')

        # 決策邏輯
        if confidence > 0.8:
            # 高置信度：使用傳統回覆
            print(f"Using traditional response for intent: {intent}")
            # 返回空，讓預定義的 utter 處理
            return []

        elif confidence > 0.5:
            # 中等置信度：結合傳統和 LLM
            print(f"Using hybrid approach for intent: {intent}")

            # 先給出傳統回覆
            if intent == "check_order":
                dispatcher.utter_message(text="讓我幫您查詢訂單。")

            # 然後用 LLM 補充
            self._llm_supplement(user_message, dispatcher)

        else:
            # 低置信度：完全使用 LLM
            print("Using LLM for low confidence input")
            self._llm_fallback(user_message, dispatcher)

        return []

    def _llm_supplement(self, message: str, dispatcher: CollectingDispatcher):
        """LLM 補充信息"""
        try:
            openai.api_key = os.getenv("OPENAI_API_KEY")

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "提供簡短的補充說明（1-2 句話）"
                    },
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=100
            )

            supplement = response.choices[0].message.content
            dispatcher.utter_message(text=supplement)

        except Exception as e:
            print(f"LLM supplement error: {str(e)}")

    def _llm_fallback(self, message: str, dispatcher: CollectingDispatcher):
        """LLM 回退處理"""
        try:
            openai.api_key = os.getenv("OPENAI_API_KEY")

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "你是客服助手。如果不確定，請禮貌地要求澄清。"
                    },
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=150
            )

            fallback_response = response.choices[0].message.content
            dispatcher.utter_message(text=fallback_response)

        except Exception as e:
            dispatcher.utter_message(text="抱歉，我沒有理解。能否換個方式說明？")
            print(f"LLM fallback error: {str(e)}")


# ==================== 7. 本地 LLM 整合 ====================

def local_llm_integration():
    """
    本地 LLM 整合示例（使用 Llama, ChatGLM 等）
    """
    print("\n" + "=" * 60)
    print("本地 LLM 整合")
    print("=" * 60)

    example_code = '''
from transformers import AutoTokenizer, AutoModel
import torch

class ActionLocalLLM(Action):
    """使用本地部署的 LLM"""

    def __init__(self):
        super().__init__()
        # 加載模型（僅一次）
        self.tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b")
        self.model = AutoModel.from_pretrained("THUDM/chatglm-6b").half().cuda()
        self.model.eval()

    def name(self) -> Text:
        return "action_local_llm"

    def run(self, dispatcher, tracker, domain):
        user_message = tracker.latest_message.get('text')

        # 生成回覆
        with torch.no_grad():
            response, history = self.model.chat(
                self.tokenizer,
                user_message,
                history=[]
            )

        dispatcher.utter_message(text=response)
        return []

# 使用 Llama.cpp（更快，CPU 友好）
from llama_cpp import Llama

class ActionLlamaCpp(Action):
    """使用 Llama.cpp"""

    def __init__(self):
        super().__init__()
        self.llm = Llama(
            model_path="./models/llama-2-7b-chat.gguf",
            n_ctx=2048
        )

    def name(self) -> Text:
        return "action_llama_cpp"

    def run(self, dispatcher, tracker, domain):
        user_message = tracker.latest_message.get('text')

        prompt = f"User: {user_message}\\nAssistant:"

        output = self.llm(
            prompt,
            max_tokens=200,
            temperature=0.7,
            stop=["User:", "\\n\\n"]
        )

        response = output['choices'][0]['text'].strip()
        dispatcher.utter_message(text=response)
        return []
'''

    print(example_code)


# ==================== 8. Prompt 工程最佳實踐 ====================

def prompt_engineering_best_practices():
    """
    Prompt 工程最佳實踐
    """
    print("\n" + "=" * 60)
    print("Prompt 工程最佳實踐")
    print("=" * 60)

    print("""
    【系統 Prompt 設計】
    1. 明確角色定位
       "你是一個專業的客服助手..."

    2. 設定行為準則
       "保持友好、專業的態度..."
       "如果不確定，請要求澄清..."

    3. 提供上下文
       "當前用戶是 VIP 客戶..."

    4. 限制範圍
       "只回答與產品相關的問題..."

    【Few-shot 示例】
    提供示例幫助 LLM 理解任務：

    示例 1：
    用戶：訂單在哪裡？
    助手：請提供您的訂單編號，我來幫您查詢。

    示例 2：
    用戶：我要退款
    助手：請告訴我訂單編號和退款原因。

    【溫度設置】
    - 0.0-0.3：事實性問答、分類任務
    - 0.4-0.7：一般對話、客服
    - 0.8-1.0：創意性任務

    【長度控制】
    - max_tokens 限制回覆長度
    - 客服場景建議 100-200 tokens

    【成本優化】
    1. 使用較小的模型（gpt-3.5-turbo）
    2. 限制對話歷史長度
    3. 實施緩存機制
    4. 只在必要時調用 LLM

    【安全性】
    1. 內容過濾
    2. 敏感信息保護
    3. 防止 prompt injection
    4. 設置 rate limiting
    """)


# ==================== 主程序 ====================

def main():
    """
    主程序
    """
    print("\n" + "=" * 70)
    print("Rasa LLM 整合 - 完整指南")
    print("=" * 70)

    # 1. 概述
    llm_integration_overview()

    # 2. 本地 LLM
    local_llm_integration()

    # 3. Prompt 工程
    prompt_engineering_best_practices()

    # 4. 配置示例
    print("\n" + "=" * 70)
    print("配置示例")
    print("=" * 70)

    config = """
# domain.yml
version: "3.1"

actions:
  - action_llm_response
  - action_contextual_llm
  - action_generative_faq
  - action_hybrid_response

# stories.yml
stories:
  - story: use LLM for complex question
    steps:
    - intent: complex_question
    - action: action_llm_response

  - story: hybrid approach
    steps:
    - intent: nlu_fallback
    - action: action_hybrid_response

# config.yml (添加 FallbackClassifier)
pipeline:
  - name: FallbackClassifier
    threshold: 0.7
    ambiguity_threshold: 0.1

policies:
  - name: RulePolicy
    core_fallback_threshold: 0.3
    core_fallback_action_name: "action_hybrid_response"
"""

    print(config)

    # 總結
    print("\n" + "=" * 70)
    print("總結")
    print("=" * 70)
    print("""
    【LLM 整合優勢】
    ✓ 處理開放式問題
    ✓ 生成自然回覆
    ✓ 減少訓練數據需求
    ✓ 提高用戶體驗

    【混合策略建議】
    1. 簡單任務：傳統 NLU（快、準）
    2. 複雜問題：LLM（靈活、智能）
    3. 關鍵業務：規則（可控、穩定）

    【注意事項】
    - 控制成本（API 調用費用）
    - 處理延遲（LLM 響應時間）
    - 確保安全（內容過濾）
    - 監控質量（定期評估）

    【下一步】
    學習 07_多語言支持.py - 構建多語言對話系統
    """)


if __name__ == "__main__":
    main()
