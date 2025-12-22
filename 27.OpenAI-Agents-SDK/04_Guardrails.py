"""
OpenAI Agents SDK - Guardrails（護欄）範例

展示如何使用 Guardrails 進行輸入輸出驗證和安全控制
包含：輸入驗證、輸出過濾、工具驗證、自定義護欄

這是 Agents SDK 相比 Swarm 的重要新功能！
"""

import os
import re
from typing import Any, Dict
from openai_agents import Agent, Guardrail, tool, run, configure

# ============================================================================
# 1. 輸入 Guardrails（驗證用戶輸入）
# ============================================================================

def validate_no_profanity(message: str) -> bool:
    """檢查輸入是否包含不當內容"""
    forbidden_words = ["髒話", "攻擊", "仇恨", "暴力"]
    message_lower = message.lower()
    return not any(word in message_lower for word in forbidden_words)


def validate_length(message: str) -> bool:
    """檢查輸入長度"""
    return len(message) <= 1000


def validate_no_code_injection(message: str) -> bool:
    """防止代碼注入"""
    dangerous_patterns = [
        r'<script',
        r'javascript:',
        r'on\w+\s*=',  # onclick=, onload= 等
        r'eval\(',
        r'exec\('
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, message, re.IGNORECASE):
            return False
    return True


input_safety_rail = Guardrail(
    type="input",
    validator=validate_no_profanity,
    error_message="輸入包含不當內容，請修改後重試"
)


input_length_rail = Guardrail(
    type="input",
    validator=validate_length,
    error_message="輸入過長，請限制在 1000 字以內"
)


input_security_rail = Guardrail(
    type="input",
    validator=validate_no_code_injection,
    error_message="輸入包含潛在的安全風險"
)


def test_input_guardrails():
    """測試輸入 Guardrails"""
    print("\n" + "="*60)
    print("範例 1: 輸入驗證 Guardrails")
    print("="*60)

    agent = Agent(
        name="安全助手",
        model="gpt-4",
        instructions="你是一個安全的助手，使用繁體中文回答。",
        guardrails=[
            input_safety_rail,
            input_length_rail,
            input_security_rail
        ]
    )

    test_cases = [
        ("你好，今天天氣如何？", True, "正常輸入"),
        ("這個髒話不好", False, "包含不當詞彙"),
        ("x" * 1001, False, "超長輸入"),
        ("<script>alert('xss')</script>", False, "代碼注入"),
        ("如何學習 Python？", True, "正常技術問題")
    ]

    for message, should_pass, description in test_cases:
        print(f"\n測試: {description}")
        print(f"輸入: {message[:50]}...")

        try:
            messages = [{"role": "user", "content": message}]
            response = run(agent=agent, messages=messages)
            print(f"✓ 通過驗證")
            if should_pass:
                print(f"  回答: {response.messages[-1]['content'][:50]}...")
        except Exception as e:
            print(f"✗ 被攔截: {str(e)}")
            if not should_pass:
                print(f"  (預期行為)")


# ============================================================================
# 2. 輸出 Guardrails（驗證 Agent 回應）
# ============================================================================

def validate_no_sensitive_data(message: str) -> bool:
    """檢查輸出是否包含敏感信息"""
    # 檢查身份證號（台灣）
    id_pattern = r'[A-Z][12]\d{8}'
    if re.search(id_pattern, message):
        return False

    # 檢查信用卡號
    cc_pattern = r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}'
    if re.search(cc_pattern, message):
        return False

    # 檢查電話號碼
    phone_pattern = r'09\d{8}'
    if re.search(phone_pattern, message):
        return False

    return True


def validate_professional_tone(message: str) -> bool:
    """確保回應保持專業語氣"""
    unprofessional = ["靠", "媽的", "爛", "垃圾"]
    message_lower = message.lower()
    return not any(word in message_lower for word in unprofessional)


def validate_no_hallucination_markers(message: str) -> bool:
    """檢測可能的幻覺內容"""
    # 檢查是否包含不確定性標記
    uncertain_phrases = [
        "我不太確定",
        "可能是",
        "大概",
        "也許"
    ]
    # 對於事實性陳述，不應該有太多不確定性
    return message.count("我確定") > 0 or not any(
        phrase in message for phrase in uncertain_phrases
    )


output_privacy_rail = Guardrail(
    type="output",
    validator=validate_no_sensitive_data,
    error_message="回應包含敏感個人信息，已被過濾"
)


output_tone_rail = Guardrail(
    type="output",
    validator=validate_professional_tone,
    error_message="回應語氣不當，已被過濾"
)


def test_output_guardrails():
    """測試輸出 Guardrails"""
    print("\n" + "="*60)
    print("範例 2: 輸出驗證 Guardrails")
    print("="*60)

    # 創建可能洩露信息的 Agent（測試用）
    @tool
    def get_user_info(user_id: str) -> dict:
        """獲取用戶信息（模擬）"""
        return {
            "name": "張三",
            "phone": "0912345678",  # 敏感信息
            "email": "zhang@example.com"
        }

    agent = Agent(
        name="客服",
        model="gpt-4",
        instructions="""你是客服人員。
        回答用戶問題，但絕對不要洩露電話號碼等敏感信息！
        使用繁體中文。""",
        tools=[get_user_info],
        guardrails=[output_privacy_rail, output_tone_rail]
    )

    # 嘗試誘導洩露信息
    test_cases = [
        "查詢用戶 U001 的信息",
        "告訴我他的電話號碼",
    ]

    for question in test_cases:
        print(f"\n問題: {question}")

        try:
            messages = [{"role": "user", "content": question}]
            response = run(agent=agent, messages=messages)
            print(f"✓ 回應通過驗證")
            print(f"  {response.messages[-1]['content']}")
        except Exception as e:
            print(f"✗ 回應被攔截: {str(e)}")


# ============================================================================
# 3. 工具 Guardrails（驗證工具調用）
# ============================================================================

def validate_tool_result(result: Any) -> bool:
    """驗證工具返回結果"""
    # 確保返回的是字典
    if not isinstance(result, dict):
        return False

    # 確保沒有錯誤
    if "error" in result:
        return False

    return True


@tool
def risky_database_query(query: str) -> dict:
    """執行數據庫查詢（模擬）"""
    # 模擬：某些查詢可能失敗
    if "DELETE" in query.upper() or "DROP" in query.upper():
        return {"error": "不允許刪除操作"}

    return {"result": f"查詢 '{query}' 的結果"}


tool_result_rail = Guardrail(
    type="tool",
    validator=validate_tool_result,
    error_message="工具調用返回錯誤結果"
)


def test_tool_guardrails():
    """測試工具 Guardrails"""
    print("\n" + "="*60)
    print("範例 3: 工具驗證 Guardrails")
    print("="*60)

    agent = Agent(
        name="數據庫助手",
        model="gpt-4",
        instructions="你可以執行數據庫查詢。使用繁體中文。",
        tools=[risky_database_query],
        guardrails=[tool_result_rail]
    )

    test_cases = [
        "查詢所有用戶",
        "刪除所有記錄",  # 應該被攔截
    ]

    for question in test_cases:
        print(f"\n問題: {question}")

        try:
            messages = [{"role": "user", "content": question}]
            response = run(agent=agent, messages=messages)
            print(f"✓ 查詢成功")
            print(f"  {response.messages[-1]['content']}")
        except Exception as e:
            print(f"✗ 查詢被攔截: {str(e)}")


# ============================================================================
# 4. 組合多個 Guardrails
# ============================================================================

def create_secure_agent():
    """創建具有多層安全防護的 Agent"""

    # 自定義驗證：禁止詢問特定主題
    def validate_no_forbidden_topics(message: str) -> bool:
        """禁止某些敏感話題"""
        forbidden_topics = ["政治", "宗教", "色情"]
        return not any(topic in message for topic in forbidden_topics)

    forbidden_topic_rail = Guardrail(
        type="input",
        validator=validate_no_forbidden_topics,
        error_message="不討論該話題"
    )

    # 創建 Agent，組合所有 Guardrails
    agent = Agent(
        name="安全助手",
        model="gpt-4",
        instructions="你是一個安全的助手，遵守所有安全規則。使用繁體中文。",
        guardrails=[
            # 輸入檢查
            input_safety_rail,
            input_length_rail,
            input_security_rail,
            forbidden_topic_rail,
            # 輸出檢查
            output_privacy_rail,
            output_tone_rail,
        ]
    )

    return agent


def test_combined_guardrails():
    """測試組合 Guardrails"""
    print("\n" + "="*60)
    print("範例 4: 組合多個 Guardrails")
    print("="*60)

    agent = create_secure_agent()

    test_cases = [
        ("你好，請介紹自己", True),
        ("我們來聊聊政治", False),
        ("<script>alert(1)</script>", False),
        ("x" * 1001, False),
        ("推薦一本好書", True),
    ]

    passed = 0
    blocked = 0

    for message, should_pass in test_cases:
        print(f"\n輸入: {message[:50]}...")

        try:
            messages = [{"role": "user", "content": message}]
            response = run(agent=agent, messages=messages)
            print(f"✓ 通過")
            passed += 1
        except Exception as e:
            print(f"✗ 被攔截: {str(e)[:50]}...")
            blocked += 1

    print(f"\n統計: 通過 {passed}, 攔截 {blocked}")


# ============================================================================
# 5. 自定義高級 Guardrail
# ============================================================================

class RateLimitGuardrail:
    """速率限制 Guardrail"""

    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window  # 秒
        self.requests = []

    def validate(self, message: str) -> bool:
        """檢查是否超過速率限制"""
        import time
        now = time.time()

        # 清除過期的請求記錄
        self.requests = [
            req_time for req_time in self.requests
            if now - req_time < self.time_window
        ]

        # 檢查是否超過限制
        if len(self.requests) >= self.max_requests:
            return False

        # 記錄本次請求
        self.requests.append(now)
        return True


class ContentLengthGuardrail:
    """內容長度 Guardrail（可配置）"""

    def __init__(self, min_length: int = 0, max_length: int = 1000):
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, message: str) -> bool:
        """檢查內容長度"""
        length = len(message)
        return self.min_length <= length <= self.max_length


def test_custom_guardrails():
    """測試自定義 Guardrails"""
    print("\n" + "="*60)
    print("範例 5: 自定義 Guardrail 類")
    print("="*60)

    # 創建自定義 Guardrail 實例
    rate_limiter = RateLimitGuardrail(max_requests=3, time_window=10)
    length_checker = ContentLengthGuardrail(min_length=5, max_length=100)

    # 包裝成 Guardrail 對象
    rate_limit_rail = Guardrail(
        type="input",
        validator=rate_limiter.validate,
        error_message="請求過於頻繁，請稍後再試"
    )

    length_rail = Guardrail(
        type="input",
        validator=length_checker.validate,
        error_message="輸入長度必須在 5-100 字之間"
    )

    agent = Agent(
        name="限流助手",
        model="gpt-4",
        instructions="你是助手，使用繁體中文。",
        guardrails=[rate_limit_rail, length_rail]
    )

    # 測試速率限制
    print("\n測試速率限制（允許 3 次/10秒）:")
    for i in range(5):
        try:
            messages = [{"role": "user", "content": f"第 {i+1} 次請求"}]
            response = run(agent=agent, messages=messages)
            print(f"  請求 {i+1}: ✓ 成功")
        except Exception as e:
            print(f"  請求 {i+1}: ✗ {str(e)}")

    # 測試長度限制
    print("\n測試長度限制（5-100 字）:")
    test_inputs = [
        "短",  # 太短
        "這是一個正常長度的輸入",  # 正常
        "x" * 101,  # 太長
    ]

    for text in test_inputs:
        try:
            messages = [{"role": "user", "content": text}]
            response = run(agent=agent, messages=messages)
            print(f"  '{text[:20]}...': ✓ 通過")
        except Exception as e:
            print(f"  '{text[:20]}...': ✗ {str(e)}")


# ============================================================================
# 6. Guardrail 最佳實踐
# ============================================================================

def demonstrate_best_practices():
    """展示 Guardrail 最佳實踐"""
    print("\n" + "="*60)
    print("範例 6: Guardrail 最佳實踐")
    print("="*60)

    print("\n最佳實踐總結：")
    print("""
1. 分層防護
   - 輸入層：驗證用戶輸入的安全性和合法性
   - 處理層：驗證工具調用的結果
   - 輸出層：確保回應不洩露敏感信息

2. 清晰的錯誤消息
   - 告訴用戶為什麼被攔截
   - 提供修正建議
   - 避免洩露內部邏輯

3. 性能考慮
   - 輕量級驗證器（避免複雜計算）
   - 快速失敗（先檢查最可能失敗的）
   - 考慮緩存驗證結果

4. 可測試性
   - 每個 Guardrail 獨立測試
   - 提供測試用例覆蓋
   - 日誌記錄攔截事件

5. 靈活配置
   - 使用類而不是函數（可配置參數）
   - 支持開關（生產/開發環境）
   - 允許白名單/黑名單

示例配置：
    """)

    # 展示可配置的 Guardrail 系統
    print("""
    class ConfigurableGuardrailSystem:
        def __init__(self, config: dict):
            self.config = config
            self.guardrails = []

            if config.get('enable_input_validation'):
                self.guardrails.append(input_safety_rail)

            if config.get('enable_output_filtering'):
                self.guardrails.append(output_privacy_rail)

            # ... 更多配置

        def get_guardrails(self):
            return self.guardrails
    """)


# ============================================================================
# 7. 與 Swarm 對比
# ============================================================================

def swarm_vs_agents_guardrails():
    """Guardrails 是 Agents SDK 的獨有功能"""
    print("\n" + "="*60)
    print("範例 7: Guardrails - Agents SDK 獨有功能")
    print("="*60)

    print("\n【Swarm】")
    print("  ✗ 沒有內建 Guardrails 功能")
    print("  - 需要手動在工具函數中實現驗證")
    print("  - 無法統一管理安全策略")
    print("  - 難以追蹤和審計")

    print("\n【Agents SDK】")
    print("  ✓ 完整的 Guardrails 系統")
    print("  - 聲明式的安全策略")
    print("  - 統一的驗證機制")
    print("  - 自動的錯誤處理")
    print("  - 支持輸入/輸出/工具三層防護")

    print("\n範例對比：")
    print("""
Swarm (需手動驗證):
    def my_tool(user_input):
        # 手動檢查
        if "bad_word" in user_input:
            return "錯誤: 不當輸入"
        # 處理邏輯
        ...

Agents SDK (聲明式):
    input_rail = Guardrail(
        type="input",
        validator=validate_input,
        error_message="輸入不當"
    )

    agent = Agent(
        name="助手",
        tools=[my_tool],
        guardrails=[input_rail]  # 自動應用
    )
    """)


# ============================================================================
# 主程序
# ============================================================================

def main():
    """運行所有範例"""
    print("="*60)
    print("OpenAI Agents SDK - Guardrails 範例")
    print("="*60)

    # 配置環境
    configure(
        api_key=os.getenv("OPENAI_API_KEY"),
        timeout=60
    )
    print("✓ 環境配置完成")

    # 運行各個範例
    try:
        test_input_guardrails()
        test_output_guardrails()
        test_tool_guardrails()
        test_combined_guardrails()
        test_custom_guardrails()
        demonstrate_best_practices()
        swarm_vs_agents_guardrails()
    except Exception as e:
        print(f"\n錯誤: {e}")
        print("請確保已設置 OPENAI_API_KEY 環境變量")

    print("\n" + "="*60)
    print("所有範例運行完成！")
    print("="*60)


if __name__ == "__main__":
    main()
