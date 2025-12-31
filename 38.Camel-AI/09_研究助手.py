"""
CAMEL-AI 研究助手

這個範例展示如何使用 CAMEL 輔助學術研究：
1. 文獻綜述
2. 研究假設生成
3. 實驗設計
4. 數據分析建議
5. 論文撰寫協助

CAMEL 的多 Agent 協作特別適合學術研究場景。
"""

import os
from dotenv import load_dotenv
from colorama import init, Fore, Style

init(autoreset=True)
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print(f"{Fore.RED}錯誤: 請設置 OPENAI_API_KEY{Style.RESET_ALL}")
    exit(1)


def example1_literature_review():
    """範例1: 文獻綜述協助"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例1: 文獻綜述協助")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}創建文獻研究 Agent...{Style.RESET_ALL}\n")

        # 創建文獻研究員
        lit_reviewer_msg = BaseMessage.make_assistant_message(
            role_name="文獻研究員",
            content="""你是一位經驗豐富的文獻研究員。
你擅長：
1. 識別研究主題的關鍵論文
2. 總結研究現狀和趨勢
3. 找出研究空白
4. 提供批判性分析
5. 建議研究方向"""
        )

        lit_reviewer = ChatAgent(
            system_message=lit_reviewer_msg,
            model_type="gpt-3.5-turbo"
        )

        # 研究主題
        research_topics = [
            "大型語言模型的涌現能力",
            "多 Agent 系統的協作機制",
            "檢索增強生成 (RAG) 技術"
        ]

        for topic in research_topics:
            print(f"{Fore.CYAN}研究主題:{Style.RESET_ALL} {topic}\n")

            msg = BaseMessage.make_user_message(
                role_name="研究生",
                content=f"""請針對以下研究主題提供文獻綜述框架：

主題：{topic}

請包括：
1. 主要研究方向
2. 關鍵發現
3. 研究空白
4. 未來方向"""
            )

            response = lit_reviewer.step(msg)

            print(f"{Fore.GREEN}文獻綜述框架:{Style.RESET_ALL}\n")
            print(f"{response.msg.content[:400]}...\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example2_hypothesis_generation():
    """範例2: 研究假設生成"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例2: 研究假設生成")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.societies import RolePlaying
        from camel.types import TaskType

        print(f"{Fore.YELLOW}創建研究討論場景...{Style.RESET_ALL}\n")

        # 研究討論
        role_play = RolePlaying(
            assistant_role_name="資深研究員",
            user_role_name="博士生",
            task_prompt="討論並形成關於『AI Agent 協作效率』的研究假設",
            task_type=TaskType.AI_SOCIETY,
        )

        print(f"{Fore.CYAN}研究問題: AI Agent 協作效率的影響因素{Style.RESET_ALL}\n")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        # 進行研究討論
        input_msg = role_play.init_chat()

        for turn in range(1, 4):
            print(f"{Fore.CYAN}[討論輪次 {turn}]{Style.RESET_ALL}\n")

            # 資深研究員的觀點
            senior_response, _ = role_play.step(input_msg)

            if senior_response.terminated:
                break

            print(f"{Fore.GREEN}資深研究員:{Style.RESET_ALL}")
            print(f"{senior_response.msg.content}\n")

            # 博士生的回應
            student_response, _ = role_play.step(senior_response.msg)

            if student_response.terminated:
                break

            print(f"{Fore.BLUE}博士生:{Style.RESET_ALL}")
            print(f"{student_response.msg.content}\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

            input_msg = student_response.msg

        print(f"{Fore.GREEN}研究假設討論完成！{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example3_experiment_design():
    """範例3: 實驗設計協助"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例3: 實驗設計協助")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}創建實驗設計專家...{Style.RESET_ALL}\n")

        # 創建實驗設計專家
        exp_designer_msg = BaseMessage.make_assistant_message(
            role_name="實驗設計專家",
            content="""你是實驗設計專家，擅長：
1. 設計嚴謹的實驗方案
2. 確定自變量和因變量
3. 控制混淆變量
4. 選擇適當的統計方法
5. 評估實驗的內外效度"""
        )

        exp_designer = ChatAgent(
            system_message=exp_designer_msg,
            model_type="gpt-3.5-turbo"
        )

        # 研究假設
        hypothesis = """
研究假設：
增加 AI Agent 之間的通信頻率會提高協作任務的完成質量，
但過高的通信頻率會導致效率下降。
"""

        print(f"{Fore.CYAN}研究假設:{Style.RESET_ALL}")
        print(hypothesis)
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        # 請求實驗設計
        msg = BaseMessage.make_user_message(
            role_name="研究者",
            content=f"""{hypothesis}

請設計一個實驗來驗證這個假設。

請包括：
1. 實驗設計類型
2. 自變量和因變量
3. 控制變量
4. 實驗流程
5. 數據收集方法
6. 統計分析計劃"""
        )

        print(f"{Fore.YELLOW}生成實驗設計...{Style.RESET_ALL}\n")

        response = exp_designer.step(msg)

        print(f"{Fore.GREEN}實驗設計方案:{Style.RESET_ALL}\n")
        print(response.msg.content)

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example4_data_analysis_consultation():
    """範例4: 數據分析諮詢"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例4: 數據分析諮詢")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}創建數據分析顧問...{Style.RESET_ALL}\n")

        # 創建數據分析顧問
        analyst_msg = BaseMessage.make_assistant_message(
            role_name="統計分析師",
            content="""你是統計分析專家，擅長：
1. 選擇合適的統計檢驗
2. 解釋統計結果
3. 識別數據模式
4. 提供可視化建議
5. 確保統計假設得到滿足"""
        )

        analyst = ChatAgent(
            system_message=analyst_msg,
            model_type="gpt-3.5-turbo"
        )

        # 數據分析問題
        analysis_questions = [
            {
                "scenario": "比較三種不同 Agent 架構的性能",
                "data": "每種架構測試 30 次，記錄任務完成時間",
                "question": "應該使用什麼統計方法？"
            },
            {
                "scenario": "分析通信頻率與任務質量的關係",
                "data": "100 個任務的通信頻率和質量評分",
                "question": "如何量化這種關係？"
            }
        ]

        for i, item in enumerate(analysis_questions, 1):
            print(f"{Fore.CYAN}分析場景 {i}:{Style.RESET_ALL}")
            print(f"場景: {item['scenario']}")
            print(f"數據: {item['data']}")
            print(f"問題: {item['question']}\n")

            msg = BaseMessage.make_user_message(
                role_name="研究者",
                content=f"""場景：{item['scenario']}
數據：{item['data']}
問題：{item['question']}

請提供詳細的分析建議。"""
            )

            response = analyst.step(msg)

            print(f"{Fore.GREEN}分析建議:{Style.RESET_ALL}")
            print(f"{response.msg.content[:300]}...\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example5_paper_writing_assistance():
    """範例5: 論文撰寫協助"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例5: 論文撰寫協助")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}創建論文寫作團隊...{Style.RESET_ALL}\n")

        # 創建寫作顧問
        writer_msg = BaseMessage.make_assistant_message(
            role_name="學術寫作顧問",
            content="""你是學術寫作專家，擅長：
1. 組織論文結構
2. 撰寫清晰的論述
3. 遵循學術寫作規範
4. 提供語言修改建議
5. 確保邏輯連貫性"""
        )

        writer = ChatAgent(
            system_message=writer_msg,
            model_type="gpt-3.5-turbo"
        )

        # 論文部分
        paper_sections = [
            {
                "section": "Abstract",
                "content": "研究了多 Agent 系統中的協作機制..."
            },
            {
                "section": "Introduction",
                "content": "多 Agent 系統在近年來受到廣泛關注..."
            },
            {
                "section": "Methodology",
                "content": "我們設計了一個實驗來測試不同的協作策略..."
            }
        ]

        print(f"{Fore.CYAN}論文部分修改建議:{Style.RESET_ALL}\n")

        for section_info in paper_sections:
            section = section_info["section"]
            content = section_info["content"]

            print(f"{Fore.YELLOW}[{section}]{Style.RESET_ALL}")
            print(f"草稿: {content}\n")

            msg = BaseMessage.make_user_message(
                role_name="作者",
                content=f"""這是論文 {section} 部分的草稿：

"{content}"

請提供：
1. 結構建議
2. 內容完善建議
3. 語言改進建議"""
            )

            response = writer.step(msg)

            print(f"{Fore.GREEN}修改建議:{Style.RESET_ALL}")
            print(f"{response.msg.content[:250]}...\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example6_research_collaboration():
    """範例6: 研究團隊協作"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例6: 研究團隊協作模擬")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}創建研究團隊...{Style.RESET_ALL}\n")

        # 創建研究團隊
        team = {}

        roles = {
            "首席研究員": "負責研究方向和整體規劃",
            "理論研究員": "負責理論分析和建模",
            "實驗研究員": "負責實驗設計和執行",
            "數據分析師": "負責數據分析和統計",
            "論文撰寫員": "負責論文撰寫和修改"
        }

        for role, responsibility in roles.items():
            msg = BaseMessage.make_assistant_message(
                role_name=role,
                content=f"你是{role}，{responsibility}。"
            )
            team[role] = ChatAgent(
                system_message=msg,
                model_type="gpt-3.5-turbo"
            )

        print(f"{Fore.CYAN}研究團隊成員:{Style.RESET_ALL}")
        for role, resp in roles.items():
            print(f"  • {role}: {resp}")
        print()

        # 研究項目
        project = "研究大型語言模型在多 Agent 協作中的應用"

        print(f"{Fore.CYAN}研究項目:{Style.RESET_ALL} {project}\n")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        # 研究流程
        workflow = [
            ("首席研究員", "請制定研究計劃和里程碑。"),
            ("理論研究員", "請提出理論框架。"),
            ("實驗研究員", "請設計驗證實驗。"),
            ("數據分析師", "請規劃數據分析策略。")
        ]

        for role, task in workflow:
            print(f"{Fore.GREEN}[{role}]{Style.RESET_ALL}")

            msg = BaseMessage.make_user_message(
                role_name="協調者",
                content=f"項目：{project}\n\n{task}"
            )

            response = team[role].step(msg)
            print(f"{response.msg.content[:200]}...\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

        print(f"{Fore.GREEN}研究團隊協作演示完成！{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def main():
    """主函數"""
    print(f"\n{Fore.GREEN}{'='*60}")
    print(f"  CAMEL-AI 研究助手範例")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    print(f"{Fore.YELLOW}關於研究助手:{Style.RESET_ALL}")
    print("CAMEL 可以協助學術研究的各個階段：")
    print("1. 文獻綜述 - 總結研究現狀")
    print("2. 假設生成 - 形成研究問題")
    print("3. 實驗設計 - 規劃驗證方案")
    print("4. 數據分析 - 統計分析建議")
    print("5. 論文撰寫 - 寫作和修改協助\n")

    try:
        example1_literature_review()
        example2_hypothesis_generation()
        example3_experiment_design()
        example4_data_analysis_consultation()
        example5_paper_writing_assistance()
        example6_research_collaboration()

        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"  所有範例執行完成！")
        print(f"{'='*60}{Style.RESET_ALL}\n")

        print(f"{Fore.CYAN}研究助手的優勢:{Style.RESET_ALL}")
        print("1. 多角度分析問題")
        print("2. 系統化研究流程")
        print("3. 協作式討論")
        print("4. 專業知識整合")
        print("5. 提高研究效率\n")

        print(f"{Fore.CYAN}下一步:{Style.RESET_ALL}")
        print("查看 10_進階技巧.py 學習高級配置和優化\n")

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}程序被用戶中斷{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}執行過程中發生錯誤: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
