"""
CAMEL-AI 多 Agent 社會

這個範例展示多個 Agent 協作的社會模擬：
1. 多 Agent 協作模式
2. Agent 社會的組織結構
3. 角色分工和協調
4. 集體決策和投票
5. 複雜任務的分散處理

多 Agent 社會模擬是研究 AI 協作和涌現行為的重要方法。
"""

import os
from dotenv import load_dotenv
from colorama import init, Fore, Style
from typing import List, Dict

init(autoreset=True)
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print(f"{Fore.RED}錯誤: 請設置 OPENAI_API_KEY{Style.RESET_ALL}")
    exit(1)


def example1_dev_team_collaboration():
    """範例1: 開發團隊協作"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例1: 開發團隊協作模擬")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}創建開發團隊...{Style.RESET_ALL}\n")

        # 定義團隊成員
        team_roles = {
            "產品經理": "負責需求分析和產品規劃",
            "架構師": "負責系統架構設計",
            "後端工程師": "負責後端實現",
            "前端工程師": "負責前端實現",
            "測試工程師": "負責質量保證"
        }

        # 創建團隊 Agents
        team = {}
        for role, responsibility in team_roles.items():
            msg = BaseMessage.make_assistant_message(
                role_name=role,
                content=f"你是一位{role}，{responsibility}。"
            )
            team[role] = ChatAgent(
                system_message=msg,
                model_type="gpt-3.5-turbo"
            )

        print(f"{Fore.CYAN}團隊成員:{Style.RESET_ALL}")
        for role, resp in team_roles.items():
            print(f"  • {role}: {resp}")
        print()

        # 項目任務
        project_task = "開發一個在線預約系統"

        print(f"{Fore.CYAN}項目任務: {project_task}{Style.RESET_ALL}\n")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        # 每個角色提供意見
        workflow = [
            ("產品經理", "請分析這個項目的核心需求和功能模塊。"),
            ("架構師", "基於需求，請設計系統架構。"),
            ("後端工程師", "請說明後端需要實現哪些 API。"),
            ("前端工程師", "請說明前端需要哪些頁面和組件。"),
            ("測試工程師", "請提出測試策略和關鍵測試點。")
        ]

        context = f"項目: {project_task}\n\n"

        for role, question in workflow:
            print(f"{Fore.GREEN}[{role}]{Style.RESET_ALL}")

            msg = BaseMessage.make_user_message(
                role_name="協調者",
                content=f"{context}{question}"
            )

            response = team[role].step(msg)
            output = response.msg.content

            print(f"{output[:300]}...\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

            # 累積上下文
            context += f"\n{role}的意見:\n{output}\n"

        print(f"{Fore.GREEN}團隊協作完成！{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example2_research_lab_simulation():
    """範例2: 研究實驗室模擬"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例2: 研究實驗室協作")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}創建研究團隊...{Style.RESET_ALL}\n")

        # 研究團隊
        research_team = {
            "首席研究員": "領導研究方向，評估研究價值",
            "理論研究員": "負責理論分析和數學建模",
            "實驗研究員": "設計和執行實驗",
            "數據分析師": "分析實驗數據，提取洞察",
            "論文撰寫員": "撰寫研究論文"
        }

        team = {}
        for role, description in research_team.items():
            msg = BaseMessage.make_assistant_message(
                role_name=role,
                content=f"你是{role}，專長是{description}。"
            )
            team[role] = ChatAgent(
                system_message=msg,
                model_type="gpt-3.5-turbo"
            )

        # 研究課題
        research_topic = "研究大型語言模型的涌現能力"

        print(f"{Fore.CYAN}研究課題: {research_topic}{Style.RESET_ALL}\n")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        # 研究流程
        research_flow = [
            ("首席研究員", "請評估這個研究課題的重要性和可行性。"),
            ("理論研究員", "請提出理論框架和研究假設。"),
            ("實驗研究員", "請設計驗證假設的實驗方案。"),
            ("數據分析師", "請說明需要收集和分析哪些數據。")
        ]

        for role, task in research_flow:
            print(f"{Fore.GREEN}[{role}]{Style.RESET_ALL}")

            msg = BaseMessage.make_user_message(
                role_name="主任",
                content=f"課題: {research_topic}\n\n{task}"
            )

            response = team[role].step(msg)
            print(f"{response.msg.content[:250]}...\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

        print(f"{Fore.GREEN}研究規劃完成！{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example3_voting_and_consensus():
    """範例3: 投票和共識機制"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例3: Agent 投票和共識")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}創建決策委員會...{Style.RESET_ALL}\n")

        # 委員會成員
        committee = {
            "技術專家": "從技術可行性角度評估",
            "商業顧問": "從商業價值角度評估",
            "用戶代表": "從用戶需求角度評估",
            "風險評估員": "從風險控制角度評估"
        }

        members = {}
        for role, perspective in committee.items():
            msg = BaseMessage.make_assistant_message(
                role_name=role,
                content=f"""你是{role}，{perspective}。
在評估方案時，請給出：
1. 你的觀點（贊成/反對/中立）
2. 理由
3. 評分（0-10分）
"""
            )
            members[role] = ChatAgent(
                system_message=msg,
                model_type="gpt-3.5-turbo"
            )

        # 待決策的提案
        proposal = "是否應該重構現有系統為微服務架構？"

        print(f"{Fore.CYAN}提案: {proposal}{Style.RESET_ALL}\n")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        # 收集意見
        votes = {}
        scores = {}

        for role in committee.keys():
            print(f"{Fore.GREEN}[{role} 的評估]{Style.RESET_ALL}")

            msg = BaseMessage.make_user_message(
                role_name="主席",
                content=f"請評估以下提案：\n{proposal}"
            )

            response = members[role].step(msg)
            opinion = response.msg.content

            print(f"{opinion}\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

            # 簡單的投票統計（實際應用中需要解析回應）
            if "贊成" in opinion or "支持" in opinion:
                votes[role] = "贊成"
            elif "反對" in opinion:
                votes[role] = "反對"
            else:
                votes[role] = "中立"

        # 統計結果
        print(f"{Fore.CYAN}投票結果統計:{Style.RESET_ALL}")
        vote_count = {"贊成": 0, "反對": 0, "中立": 0}

        for role, vote in votes.items():
            vote_count[vote] += 1
            print(f"  {role}: {vote}")

        print(f"\n{Fore.GREEN}總計:{Style.RESET_ALL}")
        for vote_type, count in vote_count.items():
            print(f"  {vote_type}: {count} 票")

        # 決策結果
        if vote_count["贊成"] > vote_count["反對"]:
            result = "通過"
            color = Fore.GREEN
        elif vote_count["贊成"] < vote_count["反對"]:
            result = "否決"
            color = Fore.RED
        else:
            result = "需要進一步討論"
            color = Fore.YELLOW

        print(f"\n{color}決策結果: {result}{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example4_agent_marketplace():
    """範例4: Agent 市場模擬"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例4: Agent 市場交互")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}創建市場參與者...{Style.RESET_ALL}\n")

        # 市場角色
        market_agents = {
            "賣家1": "你是一位軟體服務提供商，提供 AI 諮詢服務。",
            "賣家2": "你是一位數據分析服務提供商。",
            "買家": "你是一位尋找 AI 解決方案的企業採購者。",
            "平台": "你是市場平台的協調者，幫助匹配買賣雙方。"
        }

        agents = {}
        for role, description in market_agents.items():
            msg = BaseMessage.make_assistant_message(
                role_name=role,
                content=description
            )
            agents[role] = ChatAgent(
                system_message=msg,
                model_type="gpt-3.5-turbo"
            )

        print(f"{Fore.CYAN}市場場景: 企業尋找 AI 服務提供商{Style.RESET_ALL}\n")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        # 買家發布需求
        print(f"{Fore.BLUE}[買家發布需求]{Style.RESET_ALL}")
        buyer_msg = BaseMessage.make_user_message(
            role_name="系統",
            content="請描述你的需求。"
        )
        buyer_req = agents["買家"].step(buyer_msg)
        print(f"{buyer_req.msg.content}\n")

        # 賣家回應
        print(f"{Fore.GREEN}[賣家回應]{Style.RESET_ALL}\n")

        for seller in ["賣家1", "賣家2"]:
            print(f"{Fore.CYAN}{seller}:{Style.RESET_ALL}")

            msg = BaseMessage.make_user_message(
                role_name="平台",
                content=f"買家需求: {buyer_req.msg.content}\n\n請提出你的方案和報價。"
            )

            response = agents[seller].step(msg)
            print(f"{response.msg.content}\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

        print(f"{Fore.GREEN}市場交互完成！{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example5_hierarchical_organization():
    """範例5: 階層式組織結構"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例5: 階層式組織協作")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}創建階層式組織...{Style.RESET_ALL}\n")

        # 組織結構
        organization = {
            "CEO": {
                "role": "制定戰略方向",
                "reports": ["CTO", "CMO", "CFO"]
            },
            "CTO": {
                "role": "技術戰略和研發",
                "reports": ["開發主管", "架構主管"]
            },
            "CMO": {
                "role": "市場營銷策略",
                "reports": []
            },
            "CFO": {
                "role": "財務規劃和控制",
                "reports": []
            },
            "開發主管": {
                "role": "管理開發團隊",
                "reports": []
            },
            "架構主管": {
                "role": "管理架構設計",
                "reports": []
            }
        }

        # 創建 Agents
        agents = {}
        for position, info in organization.items():
            msg = BaseMessage.make_assistant_message(
                role_name=position,
                content=f"你是{position}，負責{info['role']}。"
            )
            agents[position] = ChatAgent(
                system_message=msg,
                model_type="gpt-3.5-turbo"
            )

        print(f"{Fore.CYAN}組織結構:{Style.RESET_ALL}")
        for pos, info in organization.items():
            reports = ", ".join(info['reports']) if info['reports'] else "無"
            print(f"  {pos}: {info['role']}")
            print(f"    下屬: {reports}")
        print()

        # 決策流程：自上而下
        strategic_decision = "公司計劃推出新的 AI 產品線"

        print(f"{Fore.CYAN}戰略決策: {strategic_decision}{Style.RESET_ALL}\n")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        # CEO 發起
        print(f"{Fore.GREEN}[CEO - 戰略層]{Style.RESET_ALL}")
        ceo_msg = BaseMessage.make_user_message(
            role_name="董事會",
            content=f"決策: {strategic_decision}\n請制定戰略計劃。"
        )
        ceo_plan = agents["CEO"].step(ceo_msg)
        print(f"{ceo_plan.msg.content[:200]}...\n")

        # CTO 執行層
        print(f"{Fore.GREEN}[CTO - 執行層]{Style.RESET_ALL}")
        cto_msg = BaseMessage.make_user_message(
            role_name="CEO",
            content=f"CEO 的戰略:\n{ceo_plan.msg.content}\n\n請制定技術實施計劃。"
        )
        cto_plan = agents["CTO"].step(cto_msg)
        print(f"{cto_plan.msg.content[:200]}...\n")

        # 開發主管 操作層
        print(f"{Fore.GREEN}[開發主管 - 操作層]{Style.RESET_ALL}")
        dev_msg = BaseMessage.make_user_message(
            role_name="CTO",
            content=f"CTO 的計劃:\n{cto_plan.msg.content}\n\n請分配開發任務。"
        )
        dev_plan = agents["開發主管"].step(dev_msg)
        print(f"{dev_plan.msg.content[:200]}...\n")

        print(f"{Fore.GREEN}階層式決策流程完成！{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example6_emergent_behavior():
    """範例6: 涌現行為觀察"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例6: 觀察 Agent 社會的涌現行為")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}創建自組織團隊...{Style.RESET_ALL}\n")

        # 創建通用 Agents（沒有明確分工）
        agents = {}
        for i in range(1, 5):
            msg = BaseMessage.make_assistant_message(
                role_name=f"Agent{i}",
                content=f"""你是 Agent{i}，團隊成員之一。
你需要和其他 Agents 協作完成任務。
你可以主動承擔適合的角色，與他人協調。"""
            )
            agents[f"Agent{i}"] = ChatAgent(
                system_message=msg,
                model_type="gpt-3.5-turbo"
            )

        # 給定開放式任務
        task = "團隊需要策劃一場技術分享會"

        print(f"{Fore.CYAN}開放式任務: {task}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}觀察 Agents 如何自組織...{Style.RESET_ALL}\n")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        # 讓每個 Agent 提出自己的角色
        for agent_name in agents.keys():
            print(f"{Fore.GREEN}[{agent_name}]{Style.RESET_ALL}")

            msg = BaseMessage.make_user_message(
                role_name="協調者",
                content=f"""任務: {task}

請說明：
1. 你願意承擔什麼角色？
2. 你能做什麼貢獻？
3. 你需要其他成員做什麼？"""
            )

            response = agents[agent_name].step(msg)
            print(f"{response.msg.content}\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

        print(f"{Fore.CYAN}觀察:{Style.RESET_ALL}")
        print("在沒有預設角色的情況下，Agents 會自發地：")
        print("1. 識別任務需求")
        print("2. 選擇適合的角色")
        print("3. 提出協作方式")
        print("4. 形成分工結構\n")

        print(f"{Fore.GREEN}這展示了 Agent 社會的自組織能力！{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def main():
    """主函數"""
    print(f"\n{Fore.GREEN}{'='*60}")
    print(f"  CAMEL-AI 多 Agent 社會範例")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    print(f"{Fore.YELLOW}關於多 Agent 社會:{Style.RESET_ALL}")
    print("多 Agent 社會是由多個 AI Agent 組成的協作系統。")
    print("這些系統可以模擬：")
    print("1. 組織結構（團隊、公司、研究機構）")
    print("2. 市場機制（買賣、競爭、合作）")
    print("3. 決策過程（投票、共識、談判）")
    print("4. 涌現行為（自組織、分工、創新）\n")

    try:
        example1_dev_team_collaboration()
        example2_research_lab_simulation()
        example3_voting_and_consensus()
        example4_agent_marketplace()
        example5_hierarchical_organization()
        example6_emergent_behavior()

        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"  所有範例執行完成！")
        print(f"{'='*60}{Style.RESET_ALL}\n")

        print(f"{Fore.CYAN}多 Agent 社會的研究價值:{Style.RESET_ALL}")
        print("1. 理解 AI 協作機制")
        print("2. 發現涌現行為模式")
        print("3. 優化組織結構")
        print("4. 提升集體智能")
        print("5. 探索自主協作的邊界\n")

        print(f"{Fore.CYAN}下一步:{Style.RESET_ALL}")
        print("查看 06_工具整合.py 學習如何讓 Agent 使用外部工具\n")

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}程序被用戶中斷{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}執行過程中發生錯誤: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
