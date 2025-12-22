"""
Magentic-One 與 AutoGen 對比
===================================

本範例詳細對比 Magentic-One 和基礎 AutoGen 框架的區別。

主要差異：
1. 定位和目標
2. Agent 架構
3. 任務處理方式
4. 易用性
5. 適用場景

Magentic-One 是基於 AutoGen 構建的，專注於實際任務執行，
而 AutoGen 是更通用的多 Agent 對話框架。
"""

import os
from typing import Dict, List, Any
from datetime import datetime
import json


def compare_architecture():
    """比較架構差異"""
    print("=" * 60)
    print("對比 1: 架構設計")
    print("=" * 60)

    comparison = {
        "AutoGen": {
            "定位": "通用多 Agent 對話框架",
            "核心概念": "ConversableAgent - 可對話的 Agent",
            "Agent 類型": "需要自行定義和配置",
            "協調機制": "基於對話的協調",
            "典型用法": "創建自定義 Agent 和對話流程"
        },
        "Magentic-One": {
            "定位": "任務導向的多 Agent 系統",
            "核心概念": "Orchestrator + 專門化 Agents",
            "Agent 類型": "預定義的專門 Agent（WebSurfer、Coder 等）",
            "協調機制": "中央 Orchestrator 協調",
            "典型用法": "直接執行複雜的實際任務"
        }
    }

    print("\nAutoGen 架構:")
    print(json.dumps(comparison["AutoGen"], indent=2, ensure_ascii=False))

    print("\nMagentic-One 架構:")
    print(json.dumps(comparison["Magentic-One"], indent=2, ensure_ascii=False))

    print("\n關鍵區別:")
    print("  • AutoGen: 靈活但需要更多配置")
    print("  • Magentic-One: 開箱即用，專注任務執行")


def compare_code_examples():
    """比較代碼示例"""
    print("\n" + "=" * 60)
    print("對比 2: 代碼示例")
    print("=" * 60)

    print("\n【AutoGen 示例】")
    print("創建簡單的對話:")

    autogen_example = '''
# AutoGen - 需要定義 Agents 和配置對話
from autogen import ConversableAgent, GroupChat, GroupChatManager

# 1. 定義 Agents
user_proxy = ConversableAgent(
    name="user_proxy",
    system_message="你是用戶代理",
    llm_config=llm_config,
    human_input_mode="NEVER"
)

assistant = ConversableAgent(
    name="assistant",
    system_message="你是助手",
    llm_config=llm_config
)

# 2. 設置 GroupChat
groupchat = GroupChat(
    agents=[user_proxy, assistant],
    messages=[],
    max_round=10
)

manager = GroupChatManager(
    groupchat=groupchat,
    llm_config=llm_config
)

# 3. 開始對話
user_proxy.initiate_chat(
    manager,
    message="幫我搜索 Python 最佳實踐"
)
'''

    print(autogen_example)

    print("\n【Magentic-One 示例】")
    print("執行相同任務:")

    magentic_example = '''
# Magentic-One - 直接執行任務
from autogen.agentchat.contrib.magentic_one import MagenticOne

# 1. 創建系統（Agents 已預配置）
magentic_one = MagenticOne(
    llm_config={"model": "gpt-4", "api_key": "your_key"}
)

# 2. 直接執行任務
result = magentic_one.run(
    task="搜索 Python 最佳實踐並生成報告"
)

# 完成！Orchestrator 自動協調 WebSurfer、Coder 等 Agents
'''

    print(magentic_example)

    print("\n對比總結:")
    print("  • AutoGen: 需要明確定義 Agents 和對話流程")
    print("  • Magentic-One: 一行代碼執行複雜任務")


def compare_agent_types():
    """比較 Agent 類型"""
    print("\n" + "=" * 60)
    print("對比 3: Agent 類型")
    print("=" * 60)

    agent_comparison = {
        "AutoGen Agents": [
            {
                "名稱": "ConversableAgent",
                "描述": "基礎可對話 Agent",
                "需要配置": "是 - 需要定義行為"
            },
            {
                "名稱": "AssistantAgent",
                "描述": "助手 Agent",
                "需要配置": "是 - 需要系統消息"
            },
            {
                "名稱": "UserProxyAgent",
                "描述": "用戶代理",
                "需要配置": "是 - 需要工具配置"
            },
            {
                "名稱": "自定義 Agent",
                "描述": "繼承基類創建",
                "需要配置": "是 - 需要完整實現"
            }
        ],
        "Magentic-One Agents": [
            {
                "名稱": "Orchestrator",
                "描述": "任務協調者",
                "需要配置": "否 - 開箱即用",
                "能力": "任務分解、規劃、協調"
            },
            {
                "名稱": "WebSurfer",
                "描述": "網頁瀏覽專家",
                "需要配置": "否 - 預配置",
                "能力": "搜索、爬取、信息提取"
            },
            {
                "名稱": "FileSurfer",
                "描述": "文件操作專家",
                "需要配置": "否 - 預配置",
                "能力": "文件讀寫、搜索、處理"
            },
            {
                "名稱": "Coder",
                "描述": "代碼生成專家",
                "需要配置": "否 - 預配置",
                "能力": "代碼生成、執行、調試"
            },
            {
                "名稱": "ComputerTerminal",
                "描述": "終端操作專家",
                "需要配置": "否 - 預配置",
                "能力": "命令執行、腳本運行"
            }
        ]
    }

    print("\nAutoGen Agents (通用，需配置):")
    for agent in agent_comparison["AutoGen Agents"]:
        print(f"\n  {agent['名稱']}:")
        print(f"    描述: {agent['描述']}")
        print(f"    需要配置: {agent['需要配置']}")

    print("\n\nMagentic-One Agents (專門化，預配置):")
    for agent in agent_comparison["Magentic-One Agents"]:
        print(f"\n  {agent['名稱']}:")
        print(f"    描述: {agent['描述']}")
        print(f"    配置: {agent['需要配置']}")
        print(f"    能力: {agent['能力']}")


def compare_task_handling():
    """比較任務處理方式"""
    print("\n" + "=" * 60)
    print("對比 4: 任務處理方式")
    print("=" * 60)

    print("\n複雜任務：「調研 AI 代理市場並生成報告」")

    print("\n【AutoGen 方式】")
    autogen_steps = """
1. 創建研究員 Agent
   - 定義系統消息
   - 配置工具（搜索、分析）

2. 創建作家 Agent
   - 定義寫作風格
   - 配置報告模板

3. 創建評審 Agent
   - 定義評審標準

4. 設置 GroupChat
   - 定義對話流程
   - 設置發言順序

5. 啟動對話
   - 研究員搜索信息
   - 作家撰寫初稿
   - 評審提供反饋
   - 迭代改進

總代碼量: ~150-200 行
配置時間: 30-60 分鐘
"""
    print(autogen_steps)

    print("\n【Magentic-One 方式】")
    magentic_steps = """
1. 創建 Magentic-One 實例

2. 執行任務
   magentic_one.run("調研 AI 代理市場並生成報告")

3. 完成！
   - Orchestrator 自動分解任務
   - WebSurfer 搜索信息
   - Coder 分析數據
   - FileSurfer 生成報告

總代碼量: ~10 行
配置時間: 5 分鐘
"""
    print(magentic_steps)

    print("\n效率對比:")
    print("  • AutoGen: 靈活但複雜，適合研究和定制")
    print("  • Magentic-One: 簡單快速，適合實際應用")


def compare_use_cases():
    """比較適用場景"""
    print("\n" + "=" * 60)
    print("對比 5: 適用場景")
    print("=" * 60)

    use_cases = {
        "AutoGen 最適合": [
            "研究和實驗新的 Agent 架構",
            "需要完全自定義的對話流程",
            "教學和學習多 Agent 系統",
            "開發特定領域的框架",
            "需要精細控制 Agent 行為"
        ],
        "Magentic-One 最適合": [
            "實際生產環境的任務",
            "快速原型開發",
            "標準化的複雜任務",
            "需要開箱即用的解決方案",
            "企業級應用"
        ]
    }

    print("\nAutoGen 最適合的場景:")
    for i, case in enumerate(use_cases["AutoGen 最適合"], 1):
        print(f"  {i}. {case}")

    print("\nMagentic-One 最適合的場景:")
    for i, case in enumerate(use_cases["Magentic-One 最適合"], 1):
        print(f"  {i}. {case}")


def compare_learning_curve():
    """比較學習曲線"""
    print("\n" + "=" * 60)
    print("對比 6: 學習曲線")
    print("=" * 60)

    learning_path = {
        "AutoGen": {
            "入門": {
                "時間": "1-2 天",
                "內容": [
                    "理解 ConversableAgent 概念",
                    "學習配置 llm_config",
                    "掌握基礎對話模式"
                ]
            },
            "進階": {
                "時間": "1-2 週",
                "內容": [
                    "GroupChat 和 GroupChatManager",
                    "自定義工具和函數調用",
                    "複雜對話流程設計",
                    "錯誤處理和重試"
                ]
            },
            "精通": {
                "時間": "1-2 個月",
                "內容": [
                    "創建自定義 Agent 類",
                    "高級對話模式",
                    "性能優化",
                    "生產環境部署"
                ]
            }
        },
        "Magentic-One": {
            "入門": {
                "時間": "30 分鐘 - 1 小時",
                "內容": [
                    "安裝和配置",
                    "執行第一個任務",
                    "理解基本概念"
                ]
            },
            "進階": {
                "時間": "1-3 天",
                "內容": [
                    "了解各個專門 Agent",
                    "任務規劃和優化",
                    "錯誤處理",
                    "結果驗證"
                ]
            },
            "精通": {
                "時間": "1-2 週",
                "內容": [
                    "自定義 Agent 集成",
                    "複雜工作流設計",
                    "性能調優",
                    "安全配置"
                ]
            }
        }
    }

    for framework, stages in learning_path.items():
        print(f"\n{framework} 學習路徑:")
        for stage, info in stages.items():
            print(f"\n  【{stage}】({info['時間']})")
            for item in info['內容']:
                print(f"    • {item}")


def compare_performance():
    """比較性能特徵"""
    print("\n" + "=" * 60)
    print("對比 7: 性能特徵")
    print("=" * 60)

    performance = {
        "指標": ["開發時間", "執行效率", "資源消耗", "可擴展性", "維護成本"],
        "AutoGen": {
            "開發時間": "較長（需要配置）",
            "執行效率": "取決於實現",
            "資源消耗": "可控（精細調整）",
            "可擴展性": "極高（完全自定義）",
            "維護成本": "較高（需要管理配置）"
        },
        "Magentic-One": {
            "開發時間": "很短（開箱即用）",
            "執行效率": "優化過的",
            "資源消耗": "預配置優化",
            "可擴展性": "中等（預定義 Agents）",
            "維護成本": "較低（標準化）"
        }
    }

    print("\n性能比較:")
    print(f"\n{'指標':<15} {'AutoGen':<25} {'Magentic-One':<25}")
    print("=" * 65)

    for metric in performance["指標"]:
        autogen_val = performance["AutoGen"][metric]
        magentic_val = performance["Magentic-One"][metric]
        print(f"{metric:<15} {autogen_val:<25} {magentic_val:<25}")


def compare_code_complexity():
    """比較代碼複雜度"""
    print("\n" + "=" * 60)
    print("對比 8: 相同任務的代碼複雜度")
    print("=" * 60)

    task = "搜索最新 AI 新聞，總結要點，生成報告"

    print(f"\n任務: {task}\n")

    print("【AutoGen 實現】(~100 行)")
    print("""
# 1. 導入和配置
from autogen import ConversableAgent, GroupChat, GroupChatManager

llm_config = {"model": "gpt-4", "api_key": "..."}

# 2. 創建搜索 Agent
searcher = ConversableAgent(
    name="searcher",
    system_message="你是搜索專家，負責搜索和收集信息",
    llm_config=llm_config,
    function_map={"search": search_function}
)

# 3. 創建分析 Agent
analyzer = ConversableAgent(
    name="analyzer",
    system_message="你是分析師，負責分析和總結信息",
    llm_config=llm_config
)

# 4. 創建報告 Agent
writer = ConversableAgent(
    name="writer",
    system_message="你是作家，負責撰寫報告",
    llm_config=llm_config
)

# 5. 創建用戶代理
user_proxy = ConversableAgent(
    name="user",
    human_input_mode="NEVER",
    llm_config=False
)

# 6. 設置 GroupChat
groupchat = GroupChat(
    agents=[searcher, analyzer, writer, user_proxy],
    messages=[],
    max_round=20,
    speaker_selection_method="round_robin"
)

# 7. 創建管理器
manager = GroupChatManager(
    groupchat=groupchat,
    llm_config=llm_config
)

# 8. 執行任務
user_proxy.initiate_chat(
    manager,
    message="搜索最新 AI 新聞，總結要點，生成報告"
)

# 9. 提取結果
result = groupchat.messages[-1]["content"]

# 還需要定義 search_function 等...
""")

    print("\n【Magentic-One 實現】(~5 行)")
    print("""
from autogen.agentchat.contrib.magentic_one import MagenticOne

magentic_one = MagenticOne(
    llm_config={"model": "gpt-4", "api_key": "..."}
)

result = magentic_one.run(
    task="搜索最新 AI 新聞，總結要點，生成報告"
)

# 完成！
""")


def compare_summary():
    """總結對比"""
    print("\n" + "=" * 60)
    print("總結：何時選擇哪個框架")
    print("=" * 60)

    summary = """
┌─────────────────────────────────────────────────────────────┐
│                     選擇 AutoGen                            │
├─────────────────────────────────────────────────────────────┤
│ ✓ 需要完全自定義的 Agent 行為                               │
│ ✓ 研究新的多 Agent 架構                                     │
│ ✓ 教學和學習目的                                            │
│ ✓ 需要精細控制對話流程                                      │
│ ✓ 特殊領域應用開發                                          │
│ ✓ 願意投入時間進行配置                                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  選擇 Magentic-One                          │
├─────────────────────────────────────────────────────────────┤
│ ✓ 需要快速實現實際任務                                      │
│ ✓ 標準的複雜任務（搜索、分析、報告等）                      │
│ ✓ 生產環境應用                                              │
│ ✓ 快速原型開發                                              │
│ ✓ 不想花太多時間配置                                        │
│ ✓ 需要開箱即用的解決方案                                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    最佳實踐                                 │
├─────────────────────────────────────────────────────────────┤
│ • 從 Magentic-One 開始，快速驗證想法                        │
│ • 如需深度定制，轉向 AutoGen                                │
│ • 可以混合使用：Magentic-One 處理標準任務，                 │
│   AutoGen 處理特殊需求                                      │
│ • 學習順序：先 Magentic-One，再深入 AutoGen                 │
└─────────────────────────────────────────────────────────────┘

關鍵理解：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Magentic-One 是基於 AutoGen 構建的高層抽象。

AutoGen 提供了構建塊（ConversableAgent、GroupChat 等），
Magentic-One 使用這些構建塊創建了專門的任務執行系統。

類比：
  AutoGen    = React（靈活的庫）
  Magentic-One = Next.js（有主見的框架）

兩者並非競爭關係，而是互補：
  • 需要靈活性 → AutoGen
  • 需要生產力 → Magentic-One
  • 學習和研究 → AutoGen
  • 實際應用 → Magentic-One
"""

    print(summary)


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Magentic-One vs AutoGen 全面對比")
    print("=" * 60)

    compare_architecture()
    compare_code_examples()
    compare_agent_types()
    compare_task_handling()
    compare_use_cases()
    compare_learning_curve()
    compare_performance()
    compare_code_complexity()
    compare_summary()

    print("\n" + "=" * 60)
    print("對比分析完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
