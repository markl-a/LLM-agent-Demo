"""
06_記憶和知識.py - Agno Agent 記憶和知識管理

本範例展示 Agno 的記憶和知識管理能力，包括：
- Agent 記憶系統（短期、長期）
- 會話歷史管理
- 知識庫構建與更新
- 記憶檢索策略
- 持久化存儲
- 個性化記憶

作者：LLM-agent-Demo Team
日期：2025-12
框架：Agno (原 Phidata)
"""

import os
from typing import List, Dict
from dotenv import load_dotenv

# Agno 核心導入
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.memory.db import SqliteMemory
from agno.storage.agent.sqlite import SqliteAgentStorage

# 載入環境變數
load_dotenv()


# ============================================================================
# 範例 1: 基礎記憶 - 會話歷史
# ============================================================================
def example_1_basic_memory():
    """
    Agent 的基礎記憶功能

    預設行為：
    - 自動記錄對話歷史
    - 維護上下文理解
    - 支持多輪對話
    """
    print("\n" + "="*80)
    print("範例 1: 基礎記憶 - 會話歷史")
    print("="*80)

    # 創建帶記憶的 Agent
    agent = Agent(
        name="memory_agent",
        role="記憶助手",
        model=OpenAIChat(id="gpt-4"),

        instructions=[
            "記住對話中的所有信息",
            "根據上下文回答問題",
            "引用之前的對話內容"
        ],

        markdown=True
    )

    print("\n多輪對話測試:\n")

    # 第一輪：告訴 Agent 信息
    print("用戶: 我叫張三，今年 30 歲，是一名軟體工程師。")
    response1 = agent.run("我叫張三，今年 30 歲，是一名軟體工程師。")
    print(f"Agent: {response1.content}\n")

    # 第二輪：基於記憶回答
    print("用戶: 我叫什麼名字？")
    response2 = agent.run("我叫什麼名字？")
    print(f"Agent: {response2.content}\n")

    # 第三輪：複合信息回憶
    print("用戶: 綜合我之前說的信息，介紹一下我。")
    response3 = agent.run("綜合我之前說的信息，介紹一下我。")
    print(f"Agent: {response3.content}\n")


# ============================================================================
# 範例 2: 持久化記憶 - 使用 SQLite
# ============================================================================
def example_2_persistent_memory():
    """
    使用 SQLite 實現持久化記憶

    特點：
    - 記憶存儲到數據庫
    - 跨會話保持記憶
    - 可查詢歷史記錄
    """
    print("\n" + "="*80)
    print("範例 2: 持久化記憶 - SQLite")
    print("="*80)

    # 創建持久化存儲
    agent_storage = SqliteAgentStorage(
        db_file="/tmp/agno_memory.db",
        table_name="agent_sessions"
    )

    # 創建帶持久化記憶的 Agent
    agent = Agent(
        name="persistent_agent",
        role="持久化記憶助手",
        model=OpenAIChat(id="gpt-4"),

        # 使用持久化存儲
        storage=agent_storage,

        # 會話ID（用於識別用戶）
        session_id="user_123",

        instructions=[
            "記住所有對話內容",
            "下次用戶回來時記得他們",
            "提供個性化服務"
        ],

        markdown=True
    )

    print("\n第一次會話:")
    print("用戶: 請記住，我最喜歡的顏色是藍色。")
    response1 = agent.run("請記住，我最喜歡的顏色是藍色。")
    print(f"Agent: {response1.content}\n")

    print("第二次會話（模擬重啟）:")
    print("創建新的 Agent 實例，但使用相同的 session_id...")

    # 創建新 Agent 實例（模擬程序重啟）
    agent_new = Agent(
        name="persistent_agent",
        model=OpenAIChat(id="gpt-4"),
        storage=agent_storage,
        session_id="user_123",  # 相同的 session_id
        markdown=True
    )

    print("\n用戶: 我最喜歡的顏色是什麼？")
    response2 = agent_new.run("我最喜歡的顏色是什麼？")
    print(f"Agent: {response2.content}\n")


# ============================================================================
# 範例 3: 記憶檢索與搜索
# ============================================================================
def example_3_memory_retrieval():
    """
    記憶檢索：從大量記憶中找到相關信息

    應用場景：
    - 長期對話歷史
    - 知識積累
    - 個性化推薦
    """
    print("\n" + "="*80)
    print("範例 3: 記憶檢索與搜索")
    print("="*80)

    agent = Agent(
        name="retrieval_agent",
        model=OpenAIChat(id="gpt-4"),

        instructions=[
            "記住用戶的所有偏好和信息",
            "根據需要檢索相關記憶",
            "提供個性化建議"
        ],

        markdown=True
    )

    print("\n建立記憶庫...\n")

    # 添加多條記憶
    memories = [
        "我喜歡喝咖啡，尤其是拿鐵。",
        "我住在台北市。",
        "我的工作是 AI 工程師。",
        "我最喜歡的電影類型是科幻片。",
        "我每天早上 7 點起床。"
    ]

    for memory in memories:
        print(f"用戶: {memory}")
        agent.run(memory)

    print("\n\n記憶檢索測試:\n")

    # 測試記憶檢索
    queries = [
        "根據我的喜好，推薦一家咖啡店。",
        "根據我的作息，建議早餐時間。",
        "推薦一部我可能喜歡的電影。"
    ]

    for query in queries:
        print(f"用戶: {query}")
        response = agent.run(query)
        print(f"Agent: {response.content}\n")


# ============================================================================
# 範例 4: 結構化記憶 - 使用字典
# ============================================================================
def example_4_structured_memory():
    """
    結構化記憶管理

    優勢：
    - 有組織的信息存儲
    - 易於查詢和更新
    - 支持複雜數據結構
    """
    print("\n" + "="*80)
    print("範例 4: 結構化記憶")
    print("="*80)

    # 用戶資料結構
    user_profile = {
        "name": "李四",
        "age": 28,
        "occupation": "數據科學家",
        "interests": ["機器學習", "數據可視化", "Python"],
        "preferences": {
            "communication_style": "技術性強",
            "detail_level": "詳細"
        }
    }

    agent = Agent(
        name="profile_agent",
        model=OpenAIChat(id="gpt-4"),

        instructions=[
            f"用戶資料: {user_profile}",
            "根據用戶資料提供個性化服務",
            "使用適合用戶的溝通風格"
        ],

        markdown=True
    )

    print(f"\n用戶資料已載入:\n{user_profile}\n")

    # 測試個性化回應
    queries = [
        "介紹一下機器學習的最新趨勢。",
        "推薦一些學習資源。"
    ]

    for query in queries:
        print(f"\n用戶: {query}")
        response = agent.run(query)
        print(f"Agent: {response.content}\n")


# ============================================================================
# 範例 5: 記憶總結 - 長期記憶壓縮
# ============================================================================
def example_5_memory_summarization():
    """
    記憶總結：壓縮長期記憶

    策略：
    - 定期總結對話
    - 提取關鍵信息
    - 減少記憶負擔
    - 保持重要信息
    """
    print("\n" + "="*80)
    print("範例 5: 記憶總結")
    print("="*80)

    # 主 Agent
    main_agent = Agent(
        name="main_agent",
        model=OpenAIChat(id="gpt-4"),
        markdown=True
    )

    # 記憶總結 Agent
    summarizer = Agent(
        name="memory_summarizer",
        role="記憶總結專員",
        model=OpenAIChat(id="gpt-4"),

        instructions=[
            "總結對話歷史",
            "提取關鍵信息和重要事實",
            "以結構化格式輸出",
            "保持簡潔但完整"
        ],

        markdown=True
    )

    print("\n模擬長對話...\n")

    # 模擬多輪對話
    conversation = [
        ("我計劃下個月去日本旅遊。", None),
        ("我想去東京和京都。", None),
        ("我預算大約 5 萬台幣。", None),
        ("我對日本料理和文化很感興趣。", None)
    ]

    full_context = ""
    for user_msg, _ in conversation:
        print(f"用戶: {user_msg}")
        response = main_agent.run(user_msg)
        print(f"Agent: {response.content}\n")
        full_context += f"用戶: {user_msg}\nAgent: {response.content}\n\n"

    # 總結記憶
    print("\n開始總結記憶...")
    print("-" * 80)

    summary = summarizer.run(
        f"總結以下對話，提取關鍵信息：\n\n{full_context}"
    )

    print(f"\n記憶總結:\n{summary.content}\n")


# ============================================================================
# 範例 6: 多用戶記憶隔離
# ============================================================================
def example_6_multi_user_memory():
    """
    多用戶記憶管理

    要求：
    - 不同用戶的記憶隔離
    - 使用 session_id 區分
    - 個性化體驗
    """
    print("\n" + "="*80)
    print("範例 6: 多用戶記憶隔離")
    print("="*80)

    # 創建存儲
    storage = SqliteAgentStorage(
        db_file="/tmp/multi_user.db",
        table_name="user_sessions"
    )

    # 用戶 1
    print("\n--- 用戶 A 的會話 ---")
    agent_user_a = Agent(
        name="assistant",
        model=OpenAIChat(id="gpt-4"),
        storage=storage,
        session_id="user_a",
        markdown=True
    )

    print("用戶 A: 我喜歡貓。")
    agent_user_a.run("我喜歡貓。")

    # 用戶 2
    print("\n--- 用戶 B 的會話 ---")
    agent_user_b = Agent(
        name="assistant",
        model=OpenAIChat(id="gpt-4"),
        storage=storage,
        session_id="user_b",
        markdown=True
    )

    print("用戶 B: 我喜歡狗。")
    agent_user_b.run("我喜歡狗。")

    # 驗證記憶隔離
    print("\n--- 驗證記憶隔離 ---")

    print("\n用戶 A: 我喜歡什麼動物？")
    response_a = agent_user_a.run("我喜歡什麼動物？")
    print(f"Agent: {response_a.content}")

    print("\n用戶 B: 我喜歡什麼動物？")
    response_b = agent_user_b.run("我喜歡什麼動物？")
    print(f"Agent: {response_b.content}\n")


# ============================================================================
# 主函數：運行所有範例
# ============================================================================
def main():
    """運行所有記憶管理範例"""

    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║          Agno Agent 記憶和知識管理完整示範                     ║
    ║                                                                ║
    ║  展示如何實現 Agent 的記憶和知識管理系統                       ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

    # 檢查環境變數
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 錯誤: 請設置 OPENAI_API_KEY 環境變數")
        return

    try:
        # 運行各個範例
        example_1_basic_memory()
        example_2_persistent_memory()
        example_3_memory_retrieval()
        example_4_structured_memory()
        example_5_memory_summarization()
        example_6_multi_user_memory()

        print("\n" + "="*80)
        print("✅ 所有範例執行完成！")
        print("="*80)

        print("\n📚 下一步學習：")
        print("- 07_推理Agent.py - 高級推理能力")
        print("- 08_結構化輸出.py - 使用 Pydantic 模型")
        print("- 09_AgentOS部署.py - 生產環境部署")

    except Exception as e:
        print(f"\n❌ 執行過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


# ============================================================================
# 學習要點總結
# ============================================================================
"""
📚 Agno 記憶和知識管理學習要點：

1. **記憶類型**

   短期記憶（Session Memory）：
   - 當前會話的對話歷史
   - 自動維護上下文
   - 程序關閉後清除

   長期記憶（Persistent Memory）：
   - 存儲到數據庫
   - 跨會話保持
   - 需要顯式配置

2. **持久化存儲**
   ```python
   from agno.storage.agent.sqlite import SqliteAgentStorage

   storage = SqliteAgentStorage(
       db_file="agent_memory.db",
       table_name="sessions"
   )

   agent = Agent(
       storage=storage,
       session_id="user_123"
   )
   ```

3. **記憶管理策略**

   完整保留：
   - 保存所有對話
   - 適合短期會話
   - 可能超出上下文限制

   滾動窗口：
   - 只保留最近 N 條
   - 平衡記憶和性能
   - 可能丟失早期信息

   總結壓縮：
   - 定期總結歷史
   - 提取關鍵信息
   - 減少 token 使用

4. **會話管理**
   ```python
   # 為不同用戶創建隔離的會話
   agent_user1 = Agent(
       session_id="user_001",
       storage=storage
   )

   agent_user2 = Agent(
       session_id="user_002",
       storage=storage
   )
   ```

5. **記憶檢索**
   - 基於相似度檢索相關記憶
   - 結合向量搜索提高精度
   - 過濾無關信息
   - 排序和重排序

6. **結構化記憶**
   ```python
   user_profile = {
       "name": "張三",
       "preferences": {...},
       "history": [...]
   }

   agent = Agent(
       instructions=[f"用戶資料: {user_profile}"]
   )
   ```

7. **記憶優化**
   - 定期清理舊記憶
   - 壓縮冗餘信息
   - 使用索引加速檢索
   - 實施緩存機制

8. **隱私與安全**
   - 加密敏感記憶
   - 實施訪問控制
   - 數據保留政策
   - 用戶同意機制

💡 最佳實踐：
- 根據應用需求選擇記憶策略
- 實施記憶清理機制
- 保護用戶隱私
- 監控記憶使用量
- 定期備份重要記憶

🔗 相關資源：
- Agno 記憶文檔: https://docs.agno.com/memory
- 存儲選項: https://docs.agno.com/storage
- 最佳實踐: https://docs.agno.com/memory/best-practices

⚡ 記憶管理優勢：
- 提供個性化體驗
- 支持長期對話
- 減少重複輸入
- 提升用戶滿意度
"""
