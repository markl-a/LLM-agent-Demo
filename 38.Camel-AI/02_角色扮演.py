"""
CAMEL-AI 角色扮演

這個範例展示 CAMEL 的核心功能 - 角色扮演系統：
1. 定義 AI User 和 AI Assistant 角色
2. 創建角色扮演場景
3. 自動化角色對話
4. 任務驅動的協作
5. 自定義角色特性

角色扮演是 CAMEL 的核心機制，通過讓 AI 扮演不同角色來完成複雜任務。
"""

import os
from dotenv import load_dotenv
from colorama import init, Fore, Style

init(autoreset=True)
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print(f"{Fore.RED}錯誤: 請設置 OPENAI_API_KEY{Style.RESET_ALL}")
    exit(1)


def example1_basic_role_playing():
    """範例1: 基礎角色扮演"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例1: 基礎角色扮演")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.societies import RolePlaying
        from camel.types import TaskType

        print(f"{Fore.YELLOW}創建角色扮演場景...{Style.RESET_ALL}\n")

        # 定義角色
        assistant_role_name = "Python 程式設計師"
        user_role_name = "產品經理"
        task_prompt = "設計一個待辦事項管理應用的 API"

        print(f"{Fore.CYAN}場景設置:{Style.RESET_ALL}")
        print(f"  Assistant 角色: {assistant_role_name}")
        print(f"  User 角色: {user_role_name}")
        print(f"  任務: {task_prompt}\n")

        # 創建角色扮演
        role_play_session = RolePlaying(
            assistant_role_name=assistant_role_name,
            user_role_name=user_role_name,
            task_prompt=task_prompt,
            task_type=TaskType.CODE,  # 任務類型：編程
        )

        print(f"{Fore.GREEN}角色扮演場景創建成功！{Style.RESET_ALL}\n")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        # 執行對話（限制輪數）
        print(f"{Fore.YELLOW}開始角色扮演對話...{Style.RESET_ALL}\n")

        chat_turn_limit = 5
        n = 0

        input_msg = role_play_session.init_chat()

        while n < chat_turn_limit:
            n += 1

            # Assistant 回應
            assistant_response, _ = role_play_session.step(input_msg)

            # 檢查是否結束
            if assistant_response.terminated:
                print(f"{Fore.YELLOW}對話自然結束{Style.RESET_ALL}")
                break

            print(f"{Fore.CYAN}[輪次 {n}]{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{assistant_role_name}:{Style.RESET_ALL}")
            print(f"{assistant_response.msg.content}\n")

            # User 回應
            user_response, _ = role_play_session.step(assistant_response.msg)

            if user_response.terminated:
                print(f"{Fore.YELLOW}對話自然結束{Style.RESET_ALL}")
                break

            print(f"{Fore.BLUE}{user_role_name}:{Style.RESET_ALL}")
            print(f"{user_response.msg.content}\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

            # 準備下一輪
            input_msg = user_response.msg

        print(f"{Fore.GREEN}角色扮演完成！共進行了 {n} 輪對話{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()


def example2_custom_roles():
    """範例2: 自定義角色特性"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例2: 自定義角色特性")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage
        from camel.types import RoleType

        print(f"{Fore.YELLOW}創建具有特定性格的角色...{Style.RESET_ALL}\n")

        # 創建一個嚴格的代碼審查者
        strict_reviewer_msg = BaseMessage(
            role_name="嚴格的代碼審查者",
            role_type=RoleType.ASSISTANT,
            meta_dict={},
            content="""你是一位非常嚴格和細緻的代碼審查者。
你的特點：
1. 對代碼質量要求極高
2. 會指出所有潛在問題
3. 堅持最佳實踐和設計模式
4. 注重性能和安全性
5. 要求完善的文檔和測試

審查時要嚴格，但也要給出建設性的建議。"""
        )

        strict_reviewer = ChatAgent(
            system_message=strict_reviewer_msg,
            model_type="gpt-3.5-turbo"
        )

        # 創建一個友善的導師
        friendly_mentor_msg = BaseMessage(
            role_name="友善的導師",
            role_type=RoleType.ASSISTANT,
            meta_dict={},
            content="""你是一位友善且鼓勵學習的編程導師。
你的特點：
1. 耐心且善於解釋
2. 用簡單的例子說明概念
3. 鼓勵學生嘗試和犯錯
4. 提供正向反饋
5. 循序漸進地引導學習

教導時要友善，讓學生感到安全和被支持。"""
        )

        friendly_mentor = ChatAgent(
            system_message=friendly_mentor_msg,
            model_type="gpt-3.5-turbo"
        )

        # 測試相同的代碼，看不同角色的反應
        code_to_review = """
def calculate(a, b):
    return a + b
"""

        print(f"{Fore.CYAN}提交的代碼:{Style.RESET_ALL}")
        print(code_to_review)

        # 嚴格審查者的反饋
        print(f"\n{Fore.RED}{'='*60}")
        print(f"嚴格的代碼審查者 的反饋:")
        print(f"{'='*60}{Style.RESET_ALL}\n")

        review_msg = BaseMessage.make_user_message(
            role_name="開發者",
            content=f"請審查這段代碼：\n{code_to_review}"
        )

        strict_response = strict_reviewer.step(review_msg)
        print(strict_response.msg.content)

        # 友善導師的反饋
        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"友善的導師 的反饋:")
        print(f"{'='*60}{Style.RESET_ALL}\n")

        mentor_msg = BaseMessage.make_user_message(
            role_name="學生",
            content=f"老師，這是我寫的代碼，您覺得如何？\n{code_to_review}"
        )

        friendly_response = friendly_mentor.step(mentor_msg)
        print(friendly_response.msg.content)

        print(f"\n{Fore.CYAN}觀察:{Style.RESET_ALL}")
        print("相同的代碼，不同角色給出了不同風格的反饋。")
        print("這展示了角色定義對 Agent 行為的影響。\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example3_task_types():
    """範例3: 不同任務類型的角色扮演"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例3: 不同任務類型的角色扮演")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.societies import RolePlaying
        from camel.types import TaskType

        # 定義不同類型的任務場景
        scenarios = [
            {
                "task_type": TaskType.CODE,
                "assistant": "後端工程師",
                "user": "技術主管",
                "task": "實現用戶認證系統"
            },
            {
                "task_type": TaskType.AI_SOCIETY,
                "assistant": "AI 研究員",
                "user": "研究主任",
                "task": "設計多 Agent 協作框架"
            },
            {
                "task_type": TaskType.MISALIGNMENT,
                "assistant": "AI 安全專家",
                "user": "倫理委員會成員",
                "task": "評估 AI 系統的潛在風險"
            }
        ]

        for i, scenario in enumerate(scenarios, 1):
            print(f"{Fore.CYAN}場景 {i}: {scenario['task_type'].value}{Style.RESET_ALL}")
            print(f"Assistant: {scenario['assistant']}")
            print(f"User: {scenario['user']}")
            print(f"任務: {scenario['task']}\n")

            # 創建角色扮演
            role_play = RolePlaying(
                assistant_role_name=scenario['assistant'],
                user_role_name=scenario['user'],
                task_prompt=scenario['task'],
                task_type=scenario['task_type'],
            )

            # 執行一輪對話
            input_msg = role_play.init_chat()
            assistant_response, _ = role_play.step(input_msg)

            print(f"{Fore.GREEN}{scenario['assistant']}:{Style.RESET_ALL}")
            print(f"{assistant_response.msg.content[:200]}...\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example4_role_with_expertise():
    """範例4: 專業領域角色"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例4: 專業領域角色")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        # 創建不同專業領域的專家
        experts = {
            "安全專家": """你是一位網路安全專家，專精於：
- 漏洞分析和滲透測試
- 加密和認證機制
- 安全架構設計
- 威脅建模和風險評估
你會從安全角度分析所有問題。""",

            "性能優化專家": """你是一位性能優化專家，專精於：
- 算法優化和複雜度分析
- 系統性能調優
- 緩存策略
- 並發和異步處理
你會從性能角度分析所有問題。""",

            "用戶體驗專家": """你是一位 UX 設計專家，專精於：
- 用戶介面設計
- 可用性測試
- 交互設計
- 用戶研究
你會從用戶體驗角度分析所有問題。"""
        }

        # 問題：設計一個登錄功能
        question = "請從你的專業角度，分析設計一個登錄功能時需要考慮什麼？"

        print(f"{Fore.YELLOW}問題: {question}{Style.RESET_ALL}\n")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        for expert_name, expertise in experts.items():
            print(f"{Fore.CYAN}{expert_name} 的觀點:{Style.RESET_ALL}\n")

            expert_msg = BaseMessage.make_assistant_message(
                role_name=expert_name,
                content=expertise
            )

            expert_agent = ChatAgent(
                system_message=expert_msg,
                model_type="gpt-3.5-turbo"
            )

            user_msg = BaseMessage.make_user_message(
                role_name="產品經理",
                content=question
            )

            response = expert_agent.step(user_msg)
            print(f"{response.msg.content}\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

        print(f"{Fore.GREEN}總結:{Style.RESET_ALL}")
        print("不同專業背景的專家對同一問題提供了不同角度的見解。")
        print("這展示了如何利用角色定義來獲得多元化的觀點。\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example5_dynamic_role_switching():
    """範例5: 動態角色切換"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例5: 動態角色切換")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}創建可切換角色的 Agent...{Style.RESET_ALL}\n")

        class MultiRoleAgent:
            """支援多角色切換的 Agent"""

            def __init__(self):
                self.roles = {
                    "開發者": "你是一位經驗豐富的軟體開發者，專注於實現功能。",
                    "測試者": "你是一位嚴謹的 QA 測試工程師，專注於發現問題。",
                    "架構師": "你是一位資深架構師，專注於系統設計和最佳實踐。"
                }
                self.current_role = "開發者"
                self._create_agent()

            def _create_agent(self):
                """根據當前角色創建 Agent"""
                role_msg = BaseMessage.make_assistant_message(
                    role_name=self.current_role,
                    content=self.roles[self.current_role]
                )
                self.agent = ChatAgent(
                    system_message=role_msg,
                    model_type="gpt-3.5-turbo"
                )

            def switch_role(self, role_name: str):
                """切換角色"""
                if role_name in self.roles:
                    self.current_role = role_name
                    self._create_agent()
                    print(f"{Fore.GREEN}已切換到角色: {role_name}{Style.RESET_ALL}\n")
                else:
                    print(f"{Fore.RED}未知角色: {role_name}{Style.RESET_ALL}\n")

            def respond(self, message: str):
                """以當前角色回應"""
                user_msg = BaseMessage.make_user_message(
                    role_name="用戶",
                    content=message
                )
                response = self.agent.step(user_msg)
                return response.msg.content

        # 創建多角色 Agent
        multi_agent = MultiRoleAgent()

        # 同一個問題，不同角色的回答
        question = "如何實現一個緩存系統？"

        print(f"{Fore.CYAN}問題: {question}{Style.RESET_ALL}\n")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        for role in ["開發者", "測試者", "架構師"]:
            multi_agent.switch_role(role)

            print(f"{Fore.CYAN}[{role} 的回答]{Style.RESET_ALL}")
            response = multi_agent.respond(question)
            print(f"{response[:300]}...\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

        print(f"{Fore.GREEN}觀察:{Style.RESET_ALL}")
        print("同一個 Agent 可以通過角色切換來提供不同視角的回答。")
        print("這在需要多角度分析問題時非常有用。\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def main():
    """主函數"""
    print(f"\n{Fore.GREEN}{'='*60}")
    print(f"  CAMEL-AI 角色扮演範例")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    print(f"{Fore.YELLOW}關於角色扮演:{Style.RESET_ALL}")
    print("角色扮演是 CAMEL 框架的核心機制。")
    print("通過定義明確的角色，AI Agent 可以：")
    print("1. 保持一致的行為模式")
    print("2. 提供專業領域的見解")
    print("3. 進行多角度的協作")
    print("4. 完成複雜的任務\n")

    try:
        example1_basic_role_playing()
        example2_custom_roles()
        example3_task_types()
        example4_role_with_expertise()
        example5_dynamic_role_switching()

        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"  所有範例執行完成！")
        print(f"{'='*60}{Style.RESET_ALL}\n")

        print(f"{Fore.CYAN}重要概念:{Style.RESET_ALL}")
        print("1. 角色定義決定 Agent 的行為模式")
        print("2. 不同角色可以提供多元化的觀點")
        print("3. 任務類型影響角色扮演的方向")
        print("4. 角色可以動態切換以適應不同需求\n")

        print(f"{Fore.CYAN}下一步:{Style.RESET_ALL}")
        print("查看 03_任務分解.py 學習如何自動分解複雜任務\n")

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}程序被用戶中斷{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}執行過程中發生錯誤: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
