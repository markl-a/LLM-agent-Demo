"""
OpenAI Agents SDK - 客服系統完整範例

構建一個生產級的智能客服系統
包含：多部門協作、會話管理、知識庫、性能追蹤
"""

import os
from datetime import datetime
from typing import Dict, List
from openai_agents import (
    Agent, tool, handoff_to, run, Session,
    Guardrail, trace_run, configure
)

# ============================================================================
# 1. 知識庫和數據層
# ============================================================================

class KnowledgeBase:
    """模擬知識庫"""

    def __init__(self):
        self.faqs = {
            "退款政策": "購買後 7 天內可無條件退款，需保持商品完整。",
            "配送時間": "標準配送 3-5 個工作日，快速配送 1-2 個工作日。",
            "會員等級": "分為普通、銀卡、金卡、鑽石卡四個等級。",
            "積分規則": "每消費 1 元獲得 1 積分，積分可兌換優惠券。"
        }

        self.products = {
            "P001": {"name": "筆記本電腦", "price": 30000, "stock": 50},
            "P002": {"name": "手機", "price": 15000, "stock": 100},
            "P003": {"name": "平板", "price": 12000, "stock": 30}
        }

        self.orders = {
            "O001": {
                "order_id": "O001",
                "customer_id": "C001",
                "product": "筆記本電腦",
                "status": "已發貨",
                "date": "2024-01-15",
                "total": 30000
            },
            "O002": {
                "order_id": "O002",
                "customer_id": "C002",
                "product": "手機",
                "status": "處理中",
                "date": "2024-01-20",
                "total": 15000
            }
        }

    def search_faq(self, query: str) -> str:
        """搜索常見問題"""
        for topic, answer in self.faqs.items():
            if query in topic or topic in query:
                return f"【{topic}】\n{answer}"
        return "未找到相關FAQ"

    def get_product_info(self, product_id: str) -> Dict:
        """獲取產品信息"""
        return self.products.get(product_id, {"error": "產品不存在"})

    def get_order_info(self, order_id: str) -> Dict:
        """獲取訂單信息"""
        return self.orders.get(order_id, {"error": "訂單不存在"})


# 全局知識庫實例
kb = KnowledgeBase()


# ============================================================================
# 2. 工具函數
# ============================================================================

@tool
def search_knowledge_base(query: str) -> str:
    """搜索知識庫

    Args:
        query: 搜索關鍵詞

    Returns:
        相關信息
    """
    return kb.search_faq(query)


@tool
def查詢訂單(order_id: str) -> Dict:
    """查詢訂單狀態

    Args:
        order_id: 訂單編號

    Returns:
        訂單詳細信息
    """
    return kb.get_order_info(order_id)


@tool
def查詢產品(product_id: str) -> Dict:
    """查詢產品信息

    Args:
        product_id: 產品編號

    Returns:
        產品詳細信息
    """
    return kb.get_product_info(product_id)


@tool
def創建退款申請(order_id: str, reason: str) -> Dict:
    """創建退款申請

    Args:
        order_id: 訂單編號
        reason: 退款原因

    Returns:
        退款申請結果
    """
    return {
        "status": "已提交",
        "refund_id": f"R{order_id}",
        "order_id": order_id,
        "reason": reason,
        "estimated_days": 3
    }


@tool
def創建技術工單(issue: str, priority: str = "normal") -> Dict:
    """創建技術支持工單

    Args:
        issue: 問題描述
        priority: 優先級 (low, normal, high, urgent)

    Returns:
        工單信息
    """
    ticket_id = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}"
    return {
        "ticket_id": ticket_id,
        "issue": issue,
        "priority": priority,
        "status": "已創建",
        "eta": "24小時內回應"
    }


# ============================================================================
# 3. 安全 Guardrails
# ============================================================================

def validate_customer_input(message: str) -> bool:
    """驗證客戶輸入"""
    # 長度限制
    if len(message) > 2000:
        return False

    # 禁止辱罵
    forbidden = ["髒話", "笨蛋", "白痴"]
    return not any(word in message for word in forbidden)


def validate_no_data_leakage(message: str) -> bool:
    """防止數據洩露"""
    import re
    # 檢查信用卡號
    if re.search(r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}', message):
        return False
    return True


input_guardrail = Guardrail(
    type="input",
    validator=validate_customer_input,
    error_message="輸入不符合規範，請重新輸入"
)

output_guardrail = Guardrail(
    type="output",
    validator=validate_no_data_leakage,
    error_message="回應包含敏感信息"
)


# ============================================================================
# 4. 專業客服 Agents
# ============================================================================

def create_customer_service_system():
    """創建完整的客服系統"""

    # 退款專員
    refund_specialist = Agent(
        name="退款專員",
        model="gpt-4",
        instructions="""你是退款專員，負責處理退款相關問題：
        1. 解釋退款政策
        2. 協助創建退款申請
        3. 追蹤退款進度

        使用繁體中文，保持同理心和專業態度。""",
        tools=[search_knowledge_base, 查詢訂單, 創建退款申請],
        guardrails=[output_guardrail]
    )

    # 技術支持
    tech_support = Agent(
        name="技術支持",
        model="gpt-4",
        instructions="""你是技術支持專員，負責：
        1. 診斷技術問題
        2. 提供解決方案
        3. 創建技術工單

        使用繁體中文，提供清晰的技術指導。""",
        tools=[創建技術工單, search_knowledge_base],
        guardrails=[output_guardrail]
    )

    # 訂單查詢專員
    order_specialist = Agent(
        name="訂單專員",
        model="gpt-4",
        instructions="""你是訂單專員，負責：
        1. 查詢訂單狀態
        2. 追蹤物流信息
        3. 處理訂單問題

        使用繁體中文，提供準確的訂單信息。""",
        tools=[查詢訂單, 查詢產品, search_knowledge_base],
        guardrails=[output_guardrail]
    )

    # 產品顧問
    product_consultant = Agent(
        name="產品顧問",
        model="gpt-4",
        instructions="""你是產品顧問，負責：
        1. 產品推薦
        2. 產品比較
        3. 解答產品疑問

        使用繁體中文，專業且友善。""",
        tools=[查詢產品, search_knowledge_base],
        guardrails=[output_guardrail]
    )

    # 轉移函數
    def to_refund():
        """轉移到退款專員"""
        return handoff_to(refund_specialist)

    def to_tech():
        """轉移到技術支持"""
        return handoff_to(tech_support)

    def to_order():
        """轉移到訂單專員"""
        return handoff_to(order_specialist)

    def to_product():
        """轉移到產品顧問"""
        return handoff_to(product_consultant)

    # 智能總機
    receptionist = Agent(
        name="智能客服",
        model="gpt-4",
        instructions="""你是智能客服總機，負責：
        1. 友善接待客戶
        2. 理解客戶需求
        3. 轉接到合適的專員：
           - 退款、退貨問題 → to_refund
           - 技術問題、故障 → to_tech
           - 訂單查詢、物流 → to_order
           - 產品諮詢、推薦 → to_product

        如果可以直接回答簡單問題，就直接回答。
        使用繁體中文，保持專業和友善。""",
        tools=[
            search_knowledge_base,
            to_refund, to_tech, to_order, to_product
        ],
        guardrails=[input_guardrail, output_guardrail]
    )

    return receptionist


# ============================================================================
# 5. 客服會話管理器
# ============================================================================

class CustomerServiceSession:
    """客服會話管理器"""

    def __init__(self, customer_id: str):
        self.customer_id = customer_id
        self.agent = create_customer_service_system()
        self.session = Session(
            agent=self.agent,
            session_id=f"cs_{customer_id}_{int(datetime.now().timestamp())}",
            storage="memory",
            metadata={
                "customer_id": customer_id,
                "started_at": datetime.now().isoformat(),
                "channel": "web"
            }
        )

    def chat(self, message: str) -> str:
        """處理客戶消息"""
        with trace_run(name=f"客服對話_{self.customer_id}") as tracer:
            tracer.add_metadata({
                "customer_id": self.customer_id,
                "message_length": len(message)
            })

            try:
                response = self.session.run(message)
                reply = response.messages[-1]['content']

                # 記錄指標
                tracer.log_metric("response_time", tracer.elapsed_time)
                tracer.log_metric("tokens_used", tracer.total_tokens)

                return reply

            except Exception as e:
                tracer.log_event(f"錯誤: {str(e)}")
                return "抱歉，系統暫時無法處理您的請求，請稍後再試。"

    def get_conversation_history(self) -> List[Dict]:
        """獲取對話歷史"""
        return self.session.get_history()

    def get_statistics(self) -> Dict:
        """獲取會話統計"""
        history = self.session.get_history()
        return {
            "total_messages": len(history),
            "customer_messages": len([m for m in history if m['role'] == 'user']),
            "agent_messages": len([m for m in history if m['role'] == 'assistant'])
        }


# ============================================================================
# 6. 測試場景
# ============================================================================

def test_simple_query():
    """測試簡單查詢"""
    print("\n" + "="*60)
    print("場景 1: 簡單問題（總機直接回答）")
    print("="*60)

    cs = CustomerServiceSession(customer_id="C001")

    print("\n客戶: 你們的配送時間是多久？")
    reply = cs.chat("你們的配送時間是多久？")
    print(f"客服: {reply}")


def test_order_inquiry():
    """測試訂單查詢"""
    print("\n" + "="*60)
    print("場景 2: 訂單查詢（轉接訂單專員）")
    print("="*60)

    cs = CustomerServiceSession(customer_id="C001")

    print("\n客戶: 我想查詢訂單 O001 的狀態")
    reply = cs.chat("我想查詢訂單 O001 的狀態")
    print(f"客服: {reply}")


def test_refund_request():
    """測試退款申請"""
    print("\n" + "="*60)
    print("場景 3: 退款申請（轉接退款專員）")
    print("="*60)

    cs = CustomerServiceSession(customer_id="C002")

    print("\n客戶: 我要退貨，訂單是 O002")
    reply = cs.chat("我要退貨，訂單是 O002")
    print(f"客服: {reply[:200]}...")


def test_technical_issue():
    """測試技術問題"""
    print("\n" + "="*60)
    print("場景 4: 技術支持（轉接技術支持）")
    print("="*60)

    cs = CustomerServiceSession(customer_id="C003")

    print("\n客戶: 我的手機無法開機")
    reply = cs.chat("我的手機無法開機")
    print(f"客服: {reply[:200]}...")


def test_multi_turn_conversation():
    """測試多輪對話"""
    print("\n" + "="*60)
    print("場景 5: 多輪對話（上下文保持）")
    print("="*60)

    cs = CustomerServiceSession(customer_id="C004")

    conversations = [
        "我想買筆記本電腦",
        "P001 還有貨嗎？",
        "價格多少？",
        "好的，我要下單"
    ]

    for msg in conversations:
        print(f"\n客戶: {msg}")
        reply = cs.chat(msg)
        print(f"客服: {reply[:150]}...")

    # 顯示統計
    stats = cs.get_statistics()
    print(f"\n[會話統計]")
    for key, value in stats.items():
        print(f"  {key}: {value}")


def test_guardrail_protection():
    """測試 Guardrail 保護"""
    print("\n" + "="*60)
    print("場景 6: 安全防護（Guardrail 攔截）")
    print("="*60)

    cs = CustomerServiceSession(customer_id="C005")

    # 測試不當輸入
    print("\n客戶: （發送過長或不當內容）")
    try:
        reply = cs.chat("x" * 2001)  # 超長輸入
        print(f"客服: {reply}")
    except Exception as e:
        print(f"✓ 被 Guardrail 攔截: {e}")


# ============================================================================
# 7. 性能監控
# ============================================================================

def test_performance_monitoring():
    """測試性能監控"""
    print("\n" + "="*60)
    print("場景 7: 性能監控")
    print("="*60)

    cs = CustomerServiceSession(customer_id="C006")

    with trace_run(name="性能測試") as tracer:
        # 執行多次對話
        for i in range(3):
            cs.chat(f"問題 {i+1}")

    print("\n性能指標：")
    print(f"  總耗時: {tracer.elapsed_time:.2f}s")
    print(f"  Token 使用: {tracer.total_tokens}")
    print(f"  估算成本: ${tracer.estimated_cost:.4f}")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """運行所有測試場景"""
    print("="*60)
    print("OpenAI Agents SDK - 智能客服系統")
    print("="*60)

    configure(
        api_key=os.getenv("OPENAI_API_KEY"),
        timeout=60
    )
    print("✓ 環境配置完成")

    try:
        test_simple_query()
        test_order_inquiry()
        test_refund_request()
        test_technical_issue()
        test_multi_turn_conversation()
        test_guardrail_protection()
        test_performance_monitoring()
    except Exception as e:
        print(f"\n錯誤: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)
    print("所有場景測試完成！")
    print("="*60)

    print("\n系統特點：")
    print("  ✓ 多專員協作（退款、技術、訂單、產品）")
    print("  ✓ 智能路由（自動分配到合適專員）")
    print("  ✓ 知識庫整合（FAQ、訂單、產品）")
    print("  ✓ 會話管理（自動保存上下文）")
    print("  ✓ 安全防護（Guardrails 保護）")
    print("  ✓ 性能追蹤（完整的監控數據）")


if __name__ == "__main__":
    main()
