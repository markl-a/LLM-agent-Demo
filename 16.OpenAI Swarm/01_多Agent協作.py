"""
OpenAI Swarm 多 Agent 協作示例
演示如何使用 Swarm 框架構建智能客服系統

功能：
1. 多個專業 Agent（接待員、銷售、技術支持、退款處理）
2. Agent 之間智能切換
3. 函數工具調用
4. 上下文共享
5. 完整的工作流程
"""

import os
from swarm import Swarm, Agent
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 初始化 Swarm 客戶端
client = Swarm()


# ============================================================================
# 工具函數定義
# ============================================================================

def get_product_info(product_name: str) -> str:
    """獲取產品信息"""
    products = {
        "筆記本電腦": {
            "價格": "8999元",
            "特點": "16GB RAM, 512GB SSD, Intel i7",
            "庫存": "充足"
        },
        "智能手機": {
            "價格": "4999元",
            "特點": "6.7英寸屏幕, 128GB存儲, 5000mAh電池",
            "庫存": "有貨"
        },
        "無線耳機": {
            "價格": "899元",
            "特點": "主動降噪, 30小時續航",
            "庫存": "少量"
        }
    }

    if product_name in products:
        info = products[product_name]
        return f"{product_name}：價格 {info['價格']}, {info['特點']}, 庫存狀態：{info['庫存']}"
    else:
        return f"抱歉，未找到 {product_name} 的信息"


def check_order_status(order_id: str) -> str:
    """查詢訂單狀態"""
    orders = {
        "ORD001": "已發貨，預計明天送達",
        "ORD002": "處理中，預計今天發貨",
        "ORD003": "已完成"
    }
    return orders.get(order_id, "訂單不存在")


def create_ticket(issue_type: str, description: str) -> str:
    """創建技術支持工單"""
    ticket_id = f"TKT{hash(description) % 10000:04d}"
    return f"已創建工單 {ticket_id}，問題類型：{issue_type}。技術團隊將在24小時內處理。"


def process_refund(order_id: str, reason: str) -> str:
    """處理退款請求"""
    return f"退款請求已提交（訂單：{order_id}），原因：{reason}。退款將在3-5個工作日內到賬。"


def escalate_to_human() -> str:
    """轉接人工客服"""
    return "正在為您轉接人工客服，請稍候..."


# ============================================================================
# Agent 切換函數
# ============================================================================

def transfer_to_sales():
    """轉接到銷售專員"""
    return sales_agent


def transfer_to_support():
    """轉接到技術支持"""
    return support_agent


def transfer_to_refund():
    """轉接到退款處理"""
    return refund_agent


def transfer_back_to_receptionist():
    """返回接待員"""
    return receptionist_agent


# ============================================================================
# 定義 Agent
# ============================================================================

# 1. 接待員 Agent - 第一接觸點，負責路由
receptionist_agent = Agent(
    name="接待員小雨",
    instructions="""你是友好的客服接待員小雨。你的職責：

1. 熱情歡迎客戶
2. 理解客戶需求
3. 根據需求將客戶轉接到合適的專員：
   - 產品諮詢、購買建議 → 轉接銷售專員
   - 技術問題、使用指導 → 轉接技術支持
   - 退款、退貨 → 轉接退款處理
   - 訂單查詢 → 可以直接處理

4. 語氣要友好、專業、有耐心
5. 轉接前要簡單說明原因

記住：你只負責接待和路由，專業問題請轉給對應專員。""",

    functions=[check_order_status, transfer_to_sales, transfer_to_support, transfer_to_refund],
)

# 2. 銷售專員 Agent - 負責產品推薦和銷售
sales_agent = Agent(
    name="銷售專員小李",
    instructions="""你是專業的銷售顧問小李。你的職責：

1. 提供產品信息和建議
2. 根據客戶需求推薦合適的產品
3. 解答價格、規格、庫存相關問題
4. 幫助客戶做出購買決策
5. 如遇非銷售問題，轉回接待員

銷售技巧：
- 了解客戶需求後再推薦
- 強調產品優勢和性價比
- 提供專業建議
- 態度積極但不強推""",

    functions=[get_product_info, transfer_back_to_receptionist],
)

# 3. 技術支持 Agent - 負責技術問題
support_agent = Agent(
    name="技術支持小張",
    instructions="""你是技術支持工程師小張。你的職責：

1. 解決技術問題和使用疑問
2. 提供故障排查指導
3. 創建技術工單
4. 如問題複雜，可轉人工或創建工單
5. 非技術問題轉回接待員

技術支持原則：
- 耐心聽取問題描述
- 提供清晰的步驟指導
- 複雜問題創建工單跟進
- 確認問題解決""",

    functions=[create_ticket, escalate_to_human, transfer_back_to_receptionist],
)

# 4. 退款處理 Agent - 負責退款退貨
refund_agent = Agent(
    name="退款專員小王",
    instructions="""你是退款處理專員小王。你的職責：

1. 處理退款和退貨請求
2. 了解退款原因
3. 說明退款流程和時間
4. 處理退款申請
5. 非退款問題轉回接待員

處理原則：
- 先了解情況和原因
- 表達理解和歉意（如適用）
- 清楚說明流程
- 高效處理請求
- 嘗試挽留客戶（適度）""",

    functions=[process_refund, check_order_status, transfer_back_to_receptionist],
)


# ============================================================================
# 主程序
# ============================================================================

def run_demo():
    """運行演示"""

    print("=" * 70)
    print("OpenAI Swarm 多 Agent 協作演示 - 智能客服系統")
    print("=" * 70)
    print()

    # 測試場景列表
    test_scenarios = [
        {
            "name": "場景1：產品諮詢",
            "messages": [
                "你好，我想了解一下你們的筆記本電腦",
                "價格怎麼樣？有什麼特點？",
                "好的，謝謝"
            ]
        },
        {
            "name": "場景2：技術支持",
            "messages": [
                "我的手機連接WiFi總是斷開，怎麼辦？",
                "試過了還是不行",
                "好的，謝謝"
            ]
        },
        {
            "name": "場景3：退款處理",
            "messages": [
                "我要申請退款，訂單號是ORD001",
                "收到的產品有質量問題",
                "明白了，謝謝"
            ]
        },
        {
            "name": "場景4：訂單查詢",
            "messages": [
                "你好，我想查詢訂單ORD002的狀態",
                "好的，謝謝"
            ]
        }
    ]

    # 運行每個場景
    for scenario in test_scenarios:
        print(f"\n{'=' * 70}")
        print(f"  {scenario['name']}")
        print(f"{'=' * 70}\n")

        # 每個場景都從接待員開始
        messages = []
        current_agent = receptionist_agent

        for user_message in scenario['messages']:
            print(f"客戶: {user_message}")
            messages.append({"role": "user", "content": user_message})

            # 運行 Swarm
            response = client.run(
                agent=current_agent,
                messages=messages,
            )

            # 獲取回應
            assistant_message = response.messages[-1]["content"]
            print(f"{response.agent.name}: {assistant_message}")
            print()

            # 更新消息歷史
            messages.extend(response.messages)

            # 更新當前 Agent
            current_agent = response.agent

        print("-" * 70)


if __name__ == "__main__":
    # 檢查 API Key
    if not os.getenv("OPENAI_API_KEY"):
        print("錯誤：請設置 OPENAI_API_KEY 環境變數")
        print("可以創建 .env 文件並添加：")
        print("OPENAI_API_KEY=your-api-key-here")
    else:
        run_demo()
