"""
OpenAI Agents SDK - Handoffs（控制權轉移）範例

展示如何在多個 Agent 之間轉移控制權
包含：基礎轉移、條件轉移、雙向轉移、轉移鏈

與 Swarm 的主要區別：
1. 使用 handoff_to() 函數（更明確）
2. 支持轉移元數據
3. 更好的轉移追蹤
"""

import os
from openai_agents import Agent, tool, handoff_to, run, configure

# ============================================================================
# 1. 基礎 Handoff
# ============================================================================

def create_basic_handoff_system():
    """創建基礎的 Agent 轉移系統"""

    # 專家 Agent
    specialist = Agent(
        name="技術專家",
        model="gpt-4",
        instructions="""你是技術專家，負責回答技術問題。
        使用繁體中文，提供專業且詳細的技術解答。"""
    )

    # 轉移函數
    def transfer_to_specialist():
        """轉移到技術專家"""
        return handoff_to(specialist)

    # 總機 Agent
    receptionist = Agent(
        name="總機",
        model="gpt-4",
        instructions="""你是總機人員。
        當遇到技術問題時，使用 transfer_to_specialist 轉給技術專家。
        使用繁體中文回答。""",
        tools=[transfer_to_specialist]
    )

    return receptionist, specialist


def test_basic_handoff():
    """測試基礎轉移"""
    print("\n" + "="*60)
    print("範例 1: 基礎 Handoff")
    print("="*60)

    receptionist, specialist = create_basic_handoff_system()

    # 技術問題（應該轉移）
    messages = [{"role": "user", "content": "如何部署 Docker 容器？"}]

    response = run(agent=receptionist, messages=messages)

    print(f"\n用戶: {messages[0]['content']}")
    print(f"最終回答: {response.messages[-1]['content']}")
    print(f"處理 Agent: {response.agent.name}")


# ============================================================================
# 2. 多專家系統
# ============================================================================

def create_multi_specialist_system():
    """創建多專家系統"""

    # 銷售專家
    sales_agent = Agent(
        name="銷售專家",
        model="gpt-4",
        instructions="""你是銷售專家，負責：
        1. 產品推薦
        2. 價格查詢
        3. 促銷活動
        使用繁體中文，保持友善和專業。"""
    )

    # 技術專家
    tech_agent = Agent(
        name="技術專家",
        model="gpt-4",
        instructions="""你是技術專家，負責：
        1. 技術規格說明
        2. 安裝和設置指導
        3. 故障排除
        使用繁體中文，提供詳細的技術資訊。"""
    )

    # 客服專家
    support_agent = Agent(
        name="客服專家",
        model="gpt-4",
        instructions="""你是客服專家，負責：
        1. 退換貨處理
        2. 訂單查詢
        3. 投訴處理
        使用繁體中文，保持同理心。"""
    )

    # 轉移函數
    def transfer_to_sales():
        """轉移到銷售專家"""
        print("  → 轉移到銷售專家")
        return handoff_to(sales_agent)

    def transfer_to_tech():
        """轉移到技術專家"""
        print("  → 轉移到技術專家")
        return handoff_to(tech_agent)

    def transfer_to_support():
        """轉移到客服專家"""
        print("  → 轉移到客服專家")
        return handoff_to(support_agent)

    # 總機 Agent
    receptionist = Agent(
        name="總機",
        model="gpt-4",
        instructions="""你是智能總機，根據客戶需求轉接到合適的部門：

        - 產品推薦、價格、購買 → 銷售專家 (transfer_to_sales)
        - 技術問題、安裝、故障 → 技術專家 (transfer_to_tech)
        - 退換貨、訂單、投訴 → 客服專家 (transfer_to_support)

        如果不確定，詢問客戶以獲取更多信息。
        使用繁體中文。""",
        tools=[transfer_to_sales, transfer_to_tech, transfer_to_support]
    )

    return receptionist


def test_multi_specialist():
    """測試多專家系統"""
    print("\n" + "="*60)
    print("範例 2: 多專家系統")
    print("="*60)

    receptionist = create_multi_specialist_system()

    test_cases = [
        "我想買一台筆記本電腦，有什麼推薦？",
        "我的電腦無法開機，怎麼辦？",
        "我要退貨，訂單號是 12345"
    ]

    for question in test_cases:
        print(f"\n問題: {question}")
        messages = [{"role": "user", "content": question}]

        response = run(agent=receptionist, messages=messages)

        print(f"處理部門: {response.agent.name}")
        print(f"回答: {response.messages[-1]['content'][:100]}...")


# ============================================================================
# 3. 雙向轉移
# ============================================================================

def create_bidirectional_handoff():
    """創建可以互相轉移的 Agent 系統"""

    # 需要先聲明 Agent，稍後定義工具
    general_agent = None
    specialist_agent = None

    # 定義轉移函數
    def back_to_general():
        """返回總機"""
        print("  ← 返回總機")
        return handoff_to(general_agent)

    def to_specialist():
        """轉給專家"""
        print("  → 轉給專家")
        return handoff_to(specialist_agent)

    # 創建專家 Agent（可以返回總機）
    specialist_agent = Agent(
        name="專家",
        model="gpt-4",
        instructions="""你是專家，處理複雜問題。
        如果問題已解決，可以使用 back_to_general 讓客戶返回總機。
        使用繁體中文。""",
        tools=[back_to_general]
    )

    # 創建總機 Agent（可以轉給專家）
    general_agent = Agent(
        name="總機",
        model="gpt-4",
        instructions="""你是總機，處理一般問題。
        遇到複雜問題時，使用 to_specialist 轉給專家。
        使用繁體中文。""",
        tools=[to_specialist]
    )

    return general_agent


def test_bidirectional_handoff():
    """測試雙向轉移"""
    print("\n" + "="*60)
    print("範例 3: 雙向轉移")
    print("="*60)

    agent = create_bidirectional_handoff()

    # 模擬多輪對話
    messages = []

    # 第 1 輪：簡單問題
    messages.append({"role": "user", "content": "你好"})
    response = run(agent=agent, messages=messages)
    messages = response.messages

    print(f"\n第 1 輪:")
    print(f"  用戶: 你好")
    print(f"  處理者: {response.agent.name}")

    # 第 2 輪：複雜問題（可能轉移）
    messages.append({"role": "user", "content": "我需要配置複雜的網絡架構"})
    response = run(agent=response.agent, messages=messages)
    messages = response.messages

    print(f"\n第 2 輪:")
    print(f"  用戶: 我需要配置複雜的網絡架構")
    print(f"  處理者: {response.agent.name}")


# ============================================================================
# 4. 條件轉移
# ============================================================================

@tool
def check_vip_status(user_id: str) -> dict:
    """檢查用戶 VIP 狀態"""
    # 模擬數據
    vip_users = {"U001", "U003", "U005"}
    is_vip = user_id in vip_users

    return {
        "user_id": user_id,
        "is_vip": is_vip,
        "level": "VIP" if is_vip else "普通"
    }


def create_conditional_handoff():
    """創建基於條件的轉移系統"""

    # VIP 專屬客服
    vip_agent = Agent(
        name="VIP客服",
        model="gpt-4",
        instructions="""你是 VIP 專屬客服，提供頂級服務。
        使用繁體中文，態度要特別友善和周到。"""
    )

    # 普通客服
    regular_agent = Agent(
        name="普通客服",
        model="gpt-4",
        instructions="""你是普通客服，提供標準服務。
        使用繁體中文，保持專業態度。"""
    )

    # 條件轉移函數
    def route_by_vip_status(user_id: str):
        """根據 VIP 狀態路由

        Args:
            user_id: 用戶 ID
        """
        status = check_vip_status(user_id)

        if status["is_vip"]:
            print(f"  → VIP 用戶，轉 VIP 客服")
            return handoff_to(vip_agent)
        else:
            print(f"  → 普通用戶，轉普通客服")
            return handoff_to(regular_agent)

    # 路由 Agent
    router = Agent(
        name="智能路由",
        model="gpt-4",
        instructions="""你是智能路由系統。
        當用戶提供 ID 時，使用 route_by_vip_status 分配客服。
        使用繁體中文。""",
        tools=[route_by_vip_status, check_vip_status]
    )

    return router


def test_conditional_handoff():
    """測試條件轉移"""
    print("\n" + "="*60)
    print("範例 4: 條件轉移")
    print("="*60)

    router = create_conditional_handoff()

    test_cases = [
        ("U001", "VIP"),
        ("U002", "普通"),
        ("U003", "VIP")
    ]

    for user_id, expected in test_cases:
        print(f"\n用戶 {user_id} (預期: {expected}):")
        messages = [{"role": "user", "content": f"我的 ID 是 {user_id}，需要幫助"}]

        response = run(agent=router, messages=messages)

        print(f"  分配到: {response.agent.name}")


# ============================================================================
# 5. 轉移鏈
# ============================================================================

def create_transfer_chain():
    """創建轉移鏈（A → B → C）"""

    # 第三級：最終處理者
    final_agent = Agent(
        name="高級專家",
        model="gpt-4",
        instructions="""你是高級專家，處理最複雜的問題。
        使用繁體中文，提供最專業的解答。"""
    )

    # 第二級：中級專家
    def escalate_to_senior():
        """升級到高級專家"""
        print("    ↑ 升級到高級專家")
        return handoff_to(final_agent)

    mid_agent = Agent(
        name="中級專家",
        model="gpt-4",
        instructions="""你是中級專家，處理一般技術問題。
        如果問題超出能力範圍，使用 escalate_to_senior 升級。
        使用繁體中文。""",
        tools=[escalate_to_senior]
    )

    # 第一級：初級客服
    def escalate_to_mid():
        """升級到中級專家"""
        print("  ↑ 升級到中級專家")
        return handoff_to(mid_agent)

    junior_agent = Agent(
        name="初級客服",
        model="gpt-4",
        instructions="""你是初級客服，處理基礎問題。
        如果問題較複雜，使用 escalate_to_mid 升級。
        使用繁體中文。""",
        tools=[escalate_to_mid]
    )

    return junior_agent


def test_transfer_chain():
    """測試轉移鏈"""
    print("\n" + "="*60)
    print("範例 5: 轉移鏈（逐級升級）")
    print("="*60)

    agent = create_transfer_chain()

    # 非常複雜的問題（可能需要多次轉移）
    question = "我需要設計一個高可用性的分布式系統架構，包含負載均衡、容錯和自動擴展"

    print(f"\n問題: {question}")
    messages = [{"role": "user", "content": question}]

    response = run(agent=agent, messages=messages)

    print(f"\n最終處理者: {response.agent.name}")
    print(f"回答: {response.messages[-1]['content'][:150]}...")


# ============================================================================
# 6. 轉移追蹤
# ============================================================================

def track_handoffs():
    """追蹤轉移歷史"""
    print("\n" + "="*60)
    print("範例 6: 轉移追蹤")
    print("="*60)

    receptionist = create_multi_specialist_system()

    messages = [{"role": "user", "content": "我的產品壞了，要退貨"}]

    print(f"\n問題: {messages[0]['content']}")
    print(f"\n轉移歷程:")

    response = run(agent=receptionist, messages=messages)

    # 分析對話歷史，找出所有 Agent 轉移
    agents_involved = []
    current_agent = "總機"

    for msg in response.messages:
        if msg.get("tool_calls"):
            for tc in msg["tool_calls"]:
                func_name = tc["function"]["name"]
                if "transfer" in func_name:
                    agents_involved.append(current_agent)
                    # 從函數名推斷目標 Agent
                    if "sales" in func_name:
                        current_agent = "銷售專家"
                    elif "tech" in func_name:
                        current_agent = "技術專家"
                    elif "support" in func_name:
                        current_agent = "客服專家"

    agents_involved.append(current_agent)

    for i, agent in enumerate(agents_involved, 1):
        print(f"  {i}. {agent}")


# ============================================================================
# 7. 與 Swarm 對比
# ============================================================================

def swarm_vs_agents_handoff():
    """對比 Swarm 和 Agents SDK 的 Handoff"""
    print("\n" + "="*60)
    print("範例 7: Handoff 對比")
    print("="*60)

    print("\n【Swarm 風格】")
    print("""
    from swarm import Agent

    specialist = Agent(name="專家")

    def transfer_to_specialist():
        return specialist  # 直接返回 Agent 對象

    general = Agent(
        name="總機",
        functions=[transfer_to_specialist]
    )
    """)

    print("\n【Agents SDK 風格】")
    print("""
    from openai_agents import Agent, handoff_to

    specialist = Agent(name="專家")

    def transfer_to_specialist():
        return handoff_to(specialist)  # 使用 handoff_to()

    general = Agent(
        name="總機",
        tools=[transfer_to_specialist]  # 使用 tools
    )
    """)

    print("\n主要差異:")
    print("  1. Agents SDK 使用 handoff_to() 函數（更明確）")
    print("  2. 可以在 handoff_to() 中傳遞元數據")
    print("  3. 更好的轉移追蹤和日誌")
    print("  4. 支持轉移前的驗證和條件檢查")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """運行所有範例"""
    print("="*60)
    print("OpenAI Agents SDK - Handoffs 範例")
    print("="*60)

    # 配置環境
    configure(
        api_key=os.getenv("OPENAI_API_KEY"),
        timeout=60
    )
    print("✓ 環境配置完成")

    # 運行各個範例
    try:
        test_basic_handoff()
        test_multi_specialist()
        test_bidirectional_handoff()
        test_conditional_handoff()
        test_transfer_chain()
        track_handoffs()
        swarm_vs_agents_handoff()
    except Exception as e:
        print(f"\n錯誤: {e}")
        print("請確保已設置 OPENAI_API_KEY 環境變量")

    print("\n" + "="*60)
    print("所有範例運行完成！")
    print("="*60)

    # 總結
    print("\nHandoff 最佳實踐：")
    print("  1. 每個 Agent 應有明確的職責範圍")
    print("  2. 轉移函數要有清晰的文檔說明")
    print("  3. 考慮實現雙向轉移（允許返回）")
    print("  4. 使用條件轉移實現智能路由")
    print("  5. 追蹤轉移歷史以優化流程")


if __name__ == "__main__":
    main()
