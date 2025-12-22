"""
OpenAI Agents SDK - Sessions（會話管理）範例

展示如何使用 Sessions 管理對話歷史和狀態
包含：基礎會話、持久化存儲、會話恢復、並發會話

這是 Agents SDK 相比 Swarm 的重要改進！
"""

import os
from datetime import datetime
from openai_agents import Agent, Session, tool, configure

# ============================================================================
# 1. 基礎 Session
# ============================================================================

def test_basic_session():
    """測試基礎 Session 功能"""
    print("\n" + "="*60)
    print("範例 1: 基礎 Session")
    print("="*60)

    agent = Agent(
        name="助手",
        model="gpt-4",
        instructions="你是一個友善的助手，記住用戶告訴你的信息。使用繁體中文。"
    )

    # 創建 Session（內存存儲）
    session = Session(
        agent=agent,
        storage="memory"  # 內存存儲，僅用於測試
    )

    print("\n多輪對話（自動保存歷史）：")

    # 第 1 輪
    response1 = session.run("我叫小明，今年25歲")
    print(f"\n第 1 輪:")
    print(f"  用戶: 我叫小明，今年25歲")
    print(f"  助手: {response1.messages[-1]['content']}")

    # 第 2 輪（測試記憶）
    response2 = session.run("我幾歲？叫什麼名字？")
    print(f"\n第 2 輪:")
    print(f"  用戶: 我幾歲？叫什麼名字？")
    print(f"  助手: {response2.messages[-1]['content']}")

    # 第 3 輪
    response3 = session.run("我喜歡打籃球")
    print(f"\n第 3 輪:")
    print(f"  用戶: 我喜歡打籃球")
    print(f"  助手: {response3.messages[-1]['content']}")

    # 第 4 輪（測試所有記憶）
    response4 = session.run("總結一下你對我的了解")
    print(f"\n第 4 輪:")
    print(f"  用戶: 總結一下你對我的了解")
    print(f"  助手: {response4.messages[-1]['content']}")

    # 顯示完整歷史
    history = session.get_history()
    print(f"\n[會話歷史] 共 {len(history)} 條消息")


def test_session_vs_manual():
    """對比 Session 和手動管理歷史"""
    print("\n" + "="*60)
    print("範例 2: Session vs 手動管理")
    print("="*60)

    agent = Agent(
        name="助手",
        model="gpt-4",
        instructions="你是助手，使用繁體中文。"
    )

    print("\n【手動管理（Swarm 風格）】")
    print("""
    from openai_agents import run

    messages = []

    # 第 1 輪
    messages.append({"role": "user", "content": "你好"})
    response = run(agent, messages)
    messages = response.messages  # 手動更新

    # 第 2 輪
    messages.append({"role": "user", "content": "再見"})
    response = run(agent, messages)
    messages = response.messages  # 再次手動更新
    """)

    print("\n【Session 管理（Agents SDK 風格）】")
    print("""
    from openai_agents import Session

    session = Session(agent=agent)

    # 第 1 輪
    session.run("你好")  # 自動保存歷史

    # 第 2 輪
    session.run("再見")  # 自動保存歷史

    # 就這麼簡單！
    """)

    print("\n優勢:")
    print("  ✓ 不需要手動管理 messages 列表")
    print("  ✓ 自動保存對話歷史")
    print("  ✓ 支持持久化存儲")
    print("  ✓ 可以隨時恢復會話")


# ============================================================================
# 2. 持久化存儲
# ============================================================================

def test_persistent_storage():
    """測試持久化存儲"""
    print("\n" + "="*60)
    print("範例 3: 持久化存儲")
    print("="*60)

    agent = Agent(
        name="客服",
        model="gpt-4",
        instructions="你是客服，使用繁體中文。"
    )

    print("\n支持的存儲後端：")
    print("  1. memory - 內存（不持久）")
    print("  2. redis://host:port/db - Redis")
    print("  3. mongodb://host:port/db - MongoDB")
    print("  4. postgresql://user:pass@host:port/db - PostgreSQL")
    print("  5. file://path/to/dir - 文件系統")

    # 使用文件存儲（演示用）
    print("\n使用文件存儲：")

    session_id = f"user_123_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    session = Session(
        agent=agent,
        session_id=session_id,
        storage="file:///tmp/agent_sessions",  # 存儲路徑
        ttl=3600  # 會話有效期 1 小時
    )

    print(f"  Session ID: {session_id}")
    print(f"  存儲位置: /tmp/agent_sessions/")

    # 進行對話
    session.run("我的訂單號是 12345")
    session.run("請幫我查詢訂單狀態")

    print("  ✓ 對話已保存到文件")

    # 模擬：稍後恢復會話
    print("\n模擬會話恢復：")

    new_session = Session(
        agent=agent,
        session_id=session_id,  # 使用相同 ID
        storage="file:///tmp/agent_sessions"
    )

    # 繼續對話
    response = new_session.run("我剛才的訂單號是多少？")
    print(f"  用戶: 我剛才的訂單號是多少？")
    print(f"  助手: {response.messages[-1]['content']}")
    print("  ✓ 成功恢復上下文！")


# ============================================================================
# 3. Session 元數據
# ============================================================================

def test_session_metadata():
    """測試 Session 元數據"""
    print("\n" + "="*60)
    print("範例 4: Session 元數據")
    print("="*60)

    agent = Agent(
        name="助手",
        model="gpt-4",
        instructions="你是助手，使用繁體中文。"
    )

    session = Session(
        agent=agent,
        metadata={
            "user_id": "U12345",
            "user_name": "張小明",
            "user_tier": "VIP",
            "started_at": datetime.now().isoformat()
        }
    )

    print("\nSession 元數據:")
    metadata = session.get_metadata()
    for key, value in metadata.items():
        print(f"  {key}: {value}")

    # 更新元數據
    session.update_metadata({
        "last_topic": "產品查詢",
        "messages_count": len(session.get_history())
    })

    print("\n更新後的元數據:")
    metadata = session.get_metadata()
    for key, value in metadata.items():
        print(f"  {key}: {value}")


# ============================================================================
# 4. 並發 Session 管理
# ============================================================================

def test_concurrent_sessions():
    """測試並發 Session"""
    print("\n" + "="*60)
    print("範例 5: 並發 Session 管理")
    print("="*60)

    agent = Agent(
        name="助手",
        model="gpt-4",
        instructions="你是助手，記住用戶信息。使用繁體中文。"
    )

    # 模擬多個用戶的並發會話
    users = [
        {"id": "U001", "name": "小明", "question": "我喜歡藍色"},
        {"id": "U002", "name": "小華", "question": "我喜歡紅色"},
        {"id": "U003", "name": "小李", "question": "我喜歡綠色"},
    ]

    sessions = {}

    # 創建多個 Session
    print("\n創建並發會話：")
    for user in users:
        session = Session(
            agent=agent,
            session_id=user["id"],
            metadata={"user_name": user["name"]}
        )
        sessions[user["id"]] = session

        response = session.run(user["question"])
        print(f"  {user['name']}: {user['question']}")

    # 測試會話隔離
    print("\n測試會話隔離（每個用戶只知道自己的信息）：")
    for user in users:
        session = sessions[user["id"]]
        response = session.run("我喜歡什麼顏色？")
        print(f"  {user['name']}: {response.messages[-1]['content']}")


# ============================================================================
# 5. Session 生命週期管理
# ============================================================================

def test_session_lifecycle():
    """測試 Session 生命週期"""
    print("\n" + "="*60)
    print("範例 6: Session 生命週期")
    print("="*60)

    agent = Agent(
        name="助手",
        model="gpt-4",
        instructions="你是助手，使用繁體中文。"
    )

    session = Session(
        agent=agent,
        session_id="lifecycle_test",
        ttl=3600  # 1 小時過期
    )

    # 1. 開始會話
    print("\n1. 開始會話")
    session.run("你好")
    print(f"   消息數量: {len(session.get_history())}")

    # 2. 進行多輪對話
    print("\n2. 多輪對話")
    for i in range(3):
        session.run(f"第 {i+1} 個問題")
    print(f"   消息數量: {len(session.get_history())}")

    # 3. 獲取統計信息
    print("\n3. 會話統計")
    stats = session.get_stats()
    print(f"   總消息數: {stats.get('total_messages', 'N/A')}")
    print(f"   用戶消息: {stats.get('user_messages', 'N/A')}")
    print(f"   助手消息: {stats.get('assistant_messages', 'N/A')}")

    # 4. 清除歷史
    print("\n4. 清除歷史")
    session.clear_history()
    print(f"   消息數量: {len(session.get_history())}")

    # 5. 刪除會話
    print("\n5. 刪除會話")
    session.delete()
    print("   ✓ 會話已刪除")


# ============================================================================
# 6. Session 與工具整合
# ============================================================================

@tool
def save_user_preference(preference: str) -> dict:
    """保存用戶偏好"""
    return {
        "status": "saved",
        "preference": preference,
        "timestamp": datetime.now().isoformat()
    }


@tool
def get_conversation_summary() -> str:
    """獲取對話摘要"""
    return "這是對話的摘要..."


def test_session_with_tools():
    """測試 Session 與工具的整合"""
    print("\n" + "="*60)
    print("範例 7: Session 與工具整合")
    print("="*60)

    agent = Agent(
        name="個性化助手",
        model="gpt-4",
        instructions="""你是個性化助手，可以：
        1. 記住用戶偏好
        2. 生成對話摘要
        使用繁體中文。""",
        tools=[save_user_preference, get_conversation_summary]
    )

    session = Session(
        agent=agent,
        session_id="tool_test",
        metadata={"user_id": "U001"}
    )

    # 對話中使用工具
    print("\n對話:")
    response1 = session.run("我喜歡看科幻電影，請記住")
    print(f"  用戶: 我喜歡看科幻電影，請記住")
    print(f"  助手: {response1.messages[-1]['content']}")

    response2 = session.run("推薦一些內容給我")
    print(f"\n  用戶: 推薦一些內容給我")
    print(f"  助手: {response2.messages[-1]['content']}")

    # 工具調用會自動保存到 Session 歷史
    history = session.get_history()
    tool_calls = [msg for msg in history if msg.get("tool_calls")]
    print(f"\n  工具調用次數: {len(tool_calls)}")


# ============================================================================
# 7. Session 最佳實踐
# ============================================================================

def demonstrate_best_practices():
    """展示 Session 最佳實踐"""
    print("\n" + "="*60)
    print("範例 8: Session 最佳實踐")
    print("="*60)

    print("""
最佳實踐：

1. Session ID 設計
   ✓ 使用有意義的 ID（如 user_id）
   ✓ 包含時間戳避免衝突
   ✗ 避免使用隨機 UUID（難以追蹤）

   好: "user_12345_20241222"
   差: "a1b2c3d4-e5f6-..."

2. 存儲選擇
   - 開發環境: memory（快速測試）
   - 生產環境: Redis/PostgreSQL（可靠性）
   - 高併發: Redis（性能）
   - 需要查詢: PostgreSQL（SQL 支持）

3. TTL 設置
   - 聊天機器人: 24 小時
   - 客服系統: 7 天
   - 長期對話: 30 天
   - 記得定期清理過期會話

4. 元數據利用
   ✓ 存儲用戶信息
   ✓ 記錄會話上下文
   ✓ 追蹤業務指標

5. 錯誤處理
   ✓ 處理存儲連接失敗
   ✓ 優雅降級到內存存儲
   ✓ 記錄異常日誌

示例代碼：
    """)

    print("""
    class SessionManager:
        def __init__(self, storage_url, fallback_to_memory=True):
            self.storage_url = storage_url
            self.fallback_to_memory = fallback_to_memory

        def create_session(self, user_id, agent):
            try:
                return Session(
                    agent=agent,
                    session_id=f"{user_id}_{int(time.time())}",
                    storage=self.storage_url,
                    ttl=86400,  # 24 小時
                    metadata={
                        "user_id": user_id,
                        "created_at": datetime.now().isoformat()
                    }
                )
            except ConnectionError:
                if self.fallback_to_memory:
                    logger.warning("存儲連接失敗，降級到內存")
                    return Session(agent=agent, storage="memory")
                raise
    """)


# ============================================================================
# 主程序
# ============================================================================

def main():
    """運行所有範例"""
    print("="*60)
    print("OpenAI Agents SDK - Sessions 範例")
    print("="*60)

    # 配置環境
    configure(
        api_key=os.getenv("OPENAI_API_KEY"),
        timeout=60
    )
    print("✓ 環境配置完成")

    # 運行各個範例
    try:
        test_basic_session()
        test_session_vs_manual()
        test_persistent_storage()
        test_session_metadata()
        test_concurrent_sessions()
        test_session_lifecycle()
        test_session_with_tools()
        demonstrate_best_practices()
    except Exception as e:
        print(f"\n錯誤: {e}")
        print("請確保已設置 OPENAI_API_KEY 環境變量")

    print("\n" + "="*60)
    print("所有範例運行完成！")
    print("="*60)

    print("\nSession 核心優勢：")
    print("  ✓ 自動管理對話歷史")
    print("  ✓ 支持多種持久化存儲")
    print("  ✓ 會話隔離和並發支持")
    print("  ✓ 元數據和生命週期管理")
    print("  ✓ 相比 Swarm 大幅簡化代碼")


if __name__ == "__main__":
    main()
