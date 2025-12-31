"""
CAMEL-AI 雙 Agent 對話

這個範例展示兩個 Agent 之間的協作對話：
1. User Agent 和 Assistant Agent 的交互
2. 角色互換和對話控制
3. 任務驅動的協作模式
4. 對話終止條件
5. 協作解決問題

雙 Agent 對話是 CAMEL 最核心的協作模式。
"""

import os
from dotenv import load_dotenv
from colorama import init, Fore, Style

init(autoreset=True)
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print(f"{Fore.RED}錯誤: 請設置 OPENAI_API_KEY{Style.RESET_ALL}")
    exit(1)


def example1_basic_two_agent_chat():
    """範例1: 基礎雙 Agent 對話"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例1: 基礎雙 Agent 對話")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.societies import RolePlaying
        from camel.types import TaskType

        print(f"{Fore.YELLOW}設置雙 Agent 場景...{Style.RESET_ALL}\n")

        # 定義角色和任務
        assistant_role = "Python 資深工程師"
        user_role = "初級開發者"
        task = "學習如何實現一個簡單的 REST API"

        print(f"{Fore.CYAN}場景配置:{Style.RESET_ALL}")
        print(f"  Assistant: {assistant_role}")
        print(f"  User: {user_role}")
        print(f"  任務: {task}\n")

        # 創建角色扮演
        role_play = RolePlaying(
            assistant_role_name=assistant_role,
            user_role_name=user_role,
            task_prompt=task,
            task_type=TaskType.CODE,
        )

        print(f"{Fore.YELLOW}開始對話...{Style.RESET_ALL}\n")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        # 初始化對話
        input_msg = role_play.init_chat()

        # 進行多輪對話
        max_turns = 6
        turn = 0

        while turn < max_turns:
            turn += 1

            # Assistant 的回應
            assistant_response, _ = role_play.step(input_msg)

            if assistant_response.terminated:
                print(f"{Fore.YELLOW}Assistant 結束對話{Style.RESET_ALL}")
                break

            print(f"{Fore.CYAN}[第 {turn} 輪 - Assistant]{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{assistant_role}:{Style.RESET_ALL}")
            print(f"{assistant_response.msg.content}\n")

            # User 的回應
            user_response, _ = role_play.step(assistant_response.msg)

            if user_response.terminated:
                print(f"{Fore.YELLOW}User 結束對話{Style.RESET_ALL}")
                break

            print(f"{Fore.CYAN}[第 {turn} 輪 - User]{Style.RESET_ALL}")
            print(f"{Fore.BLUE}{user_role}:{Style.RESET_ALL}")
            print(f"{user_response.msg.content}\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

            # 準備下一輪
            input_msg = user_response.msg

        print(f"{Fore.GREEN}對話完成！總共 {turn} 輪{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()


def example2_collaborative_problem_solving():
    """範例2: 協作解決問題"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例2: 協作解決問題")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.societies import RolePlaying
        from camel.types import TaskType

        print(f"{Fore.YELLOW}設置協作場景...{Style.RESET_ALL}\n")

        # 數據分析場景
        scenarios = [
            {
                "assistant": "數據科學家",
                "user": "業務分析師",
                "task": "分析用戶流失率並提出改進建議",
                "type": TaskType.AI_SOCIETY
            },
            {
                "assistant": "系統架構師",
                "user": "DevOps 工程師",
                "task": "設計可擴展的微服務架構",
                "type": TaskType.CODE
            }
        ]

        for i, scenario in enumerate(scenarios, 1):
            print(f"{Fore.CYAN}場景 {i}:{Style.RESET_ALL}")
            print(f"  Assistant: {scenario['assistant']}")
            print(f"  User: {scenario['user']}")
            print(f"  任務: {scenario['task']}\n")

            role_play = RolePlaying(
                assistant_role_name=scenario['assistant'],
                user_role_name=scenario['user'],
                task_prompt=scenario['task'],
                task_type=scenario['type'],
            )

            # 執行 3 輪對話
            input_msg = role_play.init_chat()

            for turn in range(1, 4):
                # Assistant 回應
                assistant_response, _ = role_play.step(input_msg)

                if assistant_response.terminated:
                    break

                print(f"{Fore.GREEN}[輪 {turn}] {scenario['assistant']}:{Style.RESET_ALL}")
                print(f"{assistant_response.msg.content[:200]}...\n")

                # User 回應
                user_response, _ = role_play.step(assistant_response.msg)

                if user_response.terminated:
                    break

                print(f"{Fore.BLUE}[輪 {turn}] {scenario['user']}:{Style.RESET_ALL}")
                print(f"{user_response.msg.content[:200]}...\n")

                input_msg = user_response.msg

            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example3_debate_scenario():
    """範例3: 辯論場景"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例3: Agent 辯論場景")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}創建辯論 Agents...{Style.RESET_ALL}\n")

        # 創建正方 Agent
        pro_msg = BaseMessage.make_assistant_message(
            role_name="正方辯手",
            content="""你是一位專業辯手，支持「微服務架構優於單體架構」的觀點。
你的論點應該：
1. 基於事實和數據
2. 邏輯清晰
3. 回應對方的論點
4. 提供具體例子"""
        )

        pro_agent = ChatAgent(
            system_message=pro_msg,
            model_type="gpt-3.5-turbo"
        )

        # 創建反方 Agent
        con_msg = BaseMessage.make_assistant_message(
            role_name="反方辯手",
            content="""你是一位專業辯手，支持「單體架構在很多場景下優於微服務」的觀點。
你的論點應該：
1. 基於事實和數據
2. 邏輯清晰
3. 回應對方的論點
4. 提供具體例子"""
        )

        con_agent = ChatAgent(
            system_message=con_msg,
            model_type="gpt-3.5-turbo"
        )

        print(f"{Fore.CYAN}辯題: 微服務架構 vs 單體架構{Style.RESET_ALL}\n")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        # 開始辯論
        current_msg = BaseMessage.make_user_message(
            role_name="主持人",
            content="請正方開始陳述你的觀點：為什麼微服務架構更好？"
        )

        debate_rounds = 3

        for round_num in range(1, debate_rounds + 1):
            print(f"{Fore.CYAN}[第 {round_num} 輪辯論]{Style.RESET_ALL}\n")

            # 正方發言
            pro_response = pro_agent.step(current_msg)
            print(f"{Fore.GREEN}正方:{Style.RESET_ALL}")
            print(f"{pro_response.msg.content}\n")

            # 反方回應
            con_msg_content = f"正方剛才說：{pro_response.msg.content}\n\n請你回應並陳述你的觀點。"
            con_current_msg = BaseMessage.make_user_message(
                role_name="主持人",
                content=con_msg_content
            )

            con_response = con_agent.step(con_current_msg)
            print(f"{Fore.BLUE}反方:{Style.RESET_ALL}")
            print(f"{con_response.msg.content}\n")

            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

            # 準備下一輪
            current_msg = BaseMessage.make_user_message(
                role_name="主持人",
                content=f"反方剛才說：{con_response.msg.content}\n\n請你繼續回應。"
            )

        print(f"{Fore.GREEN}辯論結束！{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example4_teacher_student_interaction():
    """範例4: 師生互動場景"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例4: 師生互動場景")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.societies import RolePlaying
        from camel.types import TaskType

        print(f"{Fore.YELLOW}創建教學場景...{Style.RESET_ALL}\n")

        # 蘇格拉底式教學
        role_play = RolePlaying(
            assistant_role_name="蘇格拉底式導師",
            user_role_name="好奇的學生",
            task_prompt="理解遞迴的概念和應用",
            task_type=TaskType.CODE,
        )

        print(f"{Fore.CYAN}教學目標: 理解遞迴{Style.RESET_ALL}\n")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        input_msg = role_play.init_chat()

        # 進行教學對話
        for turn in range(1, 6):
            # 導師提問或解釋
            teacher_response, _ = role_play.step(input_msg)

            if teacher_response.terminated:
                break

            print(f"{Fore.GREEN}導師:{Style.RESET_ALL}")
            print(f"{teacher_response.msg.content}\n")

            # 學生回答或提問
            student_response, _ = role_play.step(teacher_response.msg)

            if student_response.terminated:
                break

            print(f"{Fore.BLUE}學生:{Style.RESET_ALL}")
            print(f"{student_response.msg.content}\n")

            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

            input_msg = student_response.msg

        print(f"{Fore.GREEN}教學互動完成！{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example5_negotiation_scenario():
    """範例5: 談判場景"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例5: 商業談判場景")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}創建談判 Agents...{Style.RESET_ALL}\n")

        # 買方 Agent
        buyer_msg = BaseMessage.make_assistant_message(
            role_name="採購經理",
            content="""你是一位精明的採購經理。
目標：以最優價格購買軟體服務
預算：$50,000
策略：
1. 從低價開始出價
2. 強調競爭對手的報價
3. 要求額外服務
4. 展現購買意願但保持談判空間"""
        )

        buyer = ChatAgent(
            system_message=buyer_msg,
            model_type="gpt-3.5-turbo"
        )

        # 賣方 Agent
        seller_msg = BaseMessage.make_assistant_message(
            role_name="銷售經理",
            content="""你是一位經驗豐富的銷售經理。
目標：以最高價格銷售軟體服務
底價：$60,000
策略：
1. 強調產品價值
2. 提供套餐優惠
3. 建立緊迫感
4. 靈活調整但不能低於底價"""
        )

        seller = ChatAgent(
            system_message=seller_msg,
            model_type="gpt-3.5-turbo"
        )

        print(f"{Fore.CYAN}談判場景: 軟體服務採購{Style.RESET_ALL}\n")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        # 開始談判
        current_msg = BaseMessage.make_user_message(
            role_name="中介",
            content="採購經理想要購買你們的企業軟體服務，請開始洽談。"
        )

        # 賣方開場
        print(f"{Fore.GREEN}[開場]{Style.RESET_ALL}\n")
        seller_response = seller.step(current_msg)
        print(f"{Fore.GREEN}銷售經理:{Style.RESET_ALL}")
        print(f"{seller_response.msg.content}\n")

        # 進行談判
        for round_num in range(1, 5):
            print(f"{Fore.CYAN}[第 {round_num} 輪談判]{Style.RESET_ALL}\n")

            # 買方回應
            buyer_msg_content = BaseMessage.make_user_message(
                role_name="銷售經理",
                content=seller_response.msg.content
            )

            buyer_response = buyer.step(buyer_msg_content)
            print(f"{Fore.BLUE}採購經理:{Style.RESET_ALL}")
            print(f"{buyer_response.msg.content}\n")

            # 賣方回應
            seller_msg_content = BaseMessage.make_user_message(
                role_name="採購經理",
                content=buyer_response.msg.content
            )

            seller_response = seller.step(seller_msg_content)
            print(f"{Fore.GREEN}銷售經理:{Style.RESET_ALL}")
            print(f"{seller_response.msg.content}\n")

            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

        print(f"{Fore.GREEN}談判結束！{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example6_code_review_session():
    """範例6: 代碼審查場景"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例6: 代碼審查對話")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.societies import RolePlaying
        from camel.types import TaskType

        print(f"{Fore.YELLOW}設置代碼審查場景...{Style.RESET_ALL}\n")

        # 代碼審查對話
        role_play = RolePlaying(
            assistant_role_name="資深代碼審查者",
            user_role_name="提交者",
            task_prompt="審查一個用戶認證模塊的實現",
            task_type=TaskType.CODE,
        )

        print(f"{Fore.CYAN}審查目標: 用戶認證模塊{Style.RESET_ALL}\n")

        # 提交的代碼
        code_sample = """
class UserAuth:
    def __init__(self):
        self.users = {}

    def register(self, username, password):
        self.users[username] = password
        return True

    def login(self, username, password):
        if username in self.users:
            if self.users[username] == password:
                return True
        return False
"""

        print(f"{Fore.YELLOW}提交的代碼:{Style.RESET_ALL}")
        print(code_sample)
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        # 初始化對話（包含代碼）
        input_msg = role_play.init_chat()

        # 進行審查對話
        for turn in range(1, 5):
            # 審查者的意見
            reviewer_response, _ = role_play.step(input_msg)

            if reviewer_response.terminated:
                break

            print(f"{Fore.GREEN}審查者:{Style.RESET_ALL}")
            print(f"{reviewer_response.msg.content}\n")

            # 提交者的回應
            submitter_response, _ = role_play.step(reviewer_response.msg)

            if submitter_response.terminated:
                break

            print(f"{Fore.BLUE}提交者:{Style.RESET_ALL}")
            print(f"{submitter_response.msg.content}\n")

            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

            input_msg = submitter_response.msg

        print(f"{Fore.GREEN}代碼審查完成！{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def main():
    """主函數"""
    print(f"\n{Fore.GREEN}{'='*60}")
    print(f"  CAMEL-AI 雙 Agent 對話範例")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    print(f"{Fore.YELLOW}關於雙 Agent 對話:{Style.RESET_ALL}")
    print("雙 Agent 對話是 CAMEL 的核心協作模式。")
    print("兩個 Agent 通過交替對話來完成任務：")
    print("1. User Agent - 提出需求和問題")
    print("2. Assistant Agent - 提供解決方案")
    print("3. 持續互動直到任務完成或達到終止條件\n")

    try:
        example1_basic_two_agent_chat()
        example2_collaborative_problem_solving()
        example3_debate_scenario()
        example4_teacher_student_interaction()
        example5_negotiation_scenario()
        example6_code_review_session()

        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"  所有範例執行完成！")
        print(f"{'='*60}{Style.RESET_ALL}\n")

        print(f"{Fore.CYAN}雙 Agent 對話的應用場景:{Style.RESET_ALL}")
        print("1. 教學輔導 - 師生互動")
        print("2. 代碼審查 - 審查者與開發者")
        print("3. 需求分析 - PM 與工程師")
        print("4. 商業談判 - 買賣雙方")
        print("5. 學術辯論 - 正反雙方")
        print("6. 諮詢服務 - 顧問與客戶\n")

        print(f"{Fore.CYAN}下一步:{Style.RESET_ALL}")
        print("查看 05_多Agent社會.py 學習多個 Agent 的協作\n")

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}程序被用戶中斷{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}執行過程中發生錯誤: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
