"""
CAMEL-AI 代碼生成

這個範例展示如何使用 CAMEL 進行代碼生成：
1. 基礎代碼生成
2. 代碼審查和優化
3. 測試用例生成
4. 文檔生成
5. 完整的開發流程

CAMEL 的多 Agent 協作特別適合軟體開發任務。
"""

import os
from dotenv import load_dotenv
from colorama import init, Fore, Style

init(autoreset=True)
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print(f"{Fore.RED}錯誤: 請設置 OPENAI_API_KEY{Style.RESET_ALL}")
    exit(1)


def example1_basic_code_generation():
    """範例1: 基礎代碼生成"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例1: 基礎代碼生成")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}創建代碼生成 Agent...{Style.RESET_ALL}\n")

        # 創建程式設計師 Agent
        coder_msg = BaseMessage.make_assistant_message(
            role_name="Python 程式設計師",
            content="""你是一位經驗豐富的 Python 程式設計師。
你的代碼特點：
1. 清晰易讀
2. 遵循 PEP 8 規範
3. 包含適當的註釋
4. 處理邊界情況
5. 提供使用範例"""
        )

        coder = ChatAgent(
            system_message=coder_msg,
            model_type="gpt-3.5-turbo"
        )

        # 代碼需求
        requirements = [
            "實現一個二分搜尋函數",
            "創建一個簡單的 LRU 緩存類",
            "寫一個計算斐波那契數列的函數（使用動態規劃）"
        ]

        for req in requirements:
            print(f"{Fore.CYAN}需求:{Style.RESET_ALL} {req}\n")

            msg = BaseMessage.make_user_message(
                role_name="需求方",
                content=f"請實現：{req}\n\n要求：包含文檔字符串和使用範例。"
            )

            response = coder.step(msg)

            print(f"{Fore.GREEN}生成的代碼:{Style.RESET_ALL}\n")
            print(response.msg.content)
            print(f"\n{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example2_code_review_workflow():
    """範例2: 代碼審查工作流"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例2: 代碼審查工作流")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.societies import RolePlaying
        from camel.types import TaskType

        print(f"{Fore.YELLOW}創建代碼審查場景...{Style.RESET_ALL}\n")

        # 設置角色扮演
        role_play = RolePlaying(
            assistant_role_name="代碼審查者",
            user_role_name="開發者",
            task_prompt="審查並改進一個用戶認證函數的實現",
            task_type=TaskType.CODE,
        )

        print(f"{Fore.CYAN}場景: 代碼審查{Style.RESET_ALL}\n")

        # 初始代碼
        initial_code = """
def authenticate(username, password):
    users = {'admin': '123456', 'user': 'password'}
    if username in users:
        if users[username] == password:
            return True
    return False
"""

        print(f"{Fore.YELLOW}初始代碼:{Style.RESET_ALL}")
        print(initial_code)
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        # 開始審查對話
        input_msg = role_play.init_chat()

        for turn in range(1, 4):
            print(f"{Fore.CYAN}[審查輪次 {turn}]{Style.RESET_ALL}\n")

            # 審查者評論
            reviewer_response, _ = role_play.step(input_msg)

            if reviewer_response.terminated:
                break

            print(f"{Fore.GREEN}審查者:{Style.RESET_ALL}")
            print(f"{reviewer_response.msg.content}\n")

            # 開發者回應
            developer_response, _ = role_play.step(reviewer_response.msg)

            if developer_response.terminated:
                break

            print(f"{Fore.BLUE}開發者:{Style.RESET_ALL}")
            print(f"{developer_response.msg.content}\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

            input_msg = developer_response.msg

        print(f"{Fore.GREEN}代碼審查完成！{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example3_test_generation():
    """範例3: 測試用例生成"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例3: 自動生成測試用例")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}創建測試工程師 Agent...{Style.RESET_ALL}\n")

        # 創建測試工程師
        tester_msg = BaseMessage.make_assistant_message(
            role_name="測試工程師",
            content="""你是一位經驗豐富的測試工程師。
你會為代碼生成全面的測試用例，包括：
1. 正常情況測試
2. 邊界條件測試
3. 異常情況測試
4. 性能測試考慮
使用 pytest 框架。"""
        )

        tester = ChatAgent(
            system_message=tester_msg,
            model_type="gpt-3.5-turbo"
        )

        # 待測試的代碼
        code_to_test = """
def calculate_discount(price, discount_percent):
    '''計算折扣後價格'''
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("折扣必須在 0-100 之間")
    return price * (1 - discount_percent / 100)
"""

        print(f"{Fore.CYAN}待測試代碼:{Style.RESET_ALL}")
        print(code_to_test)
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        # 請求生成測試
        msg = BaseMessage.make_user_message(
            role_name="開發者",
            content=f"""請為以下函數生成完整的測試用例：

{code_to_test}

要求使用 pytest，涵蓋各種測試場景。"""
        )

        print(f"{Fore.YELLOW}生成測試用例...{Style.RESET_ALL}\n")

        response = tester.step(msg)

        print(f"{Fore.GREEN}生成的測試代碼:{Style.RESET_ALL}\n")
        print(response.msg.content)

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example4_documentation_generation():
    """範例4: 文檔生成"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例4: 自動生成文檔")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}創建文檔工程師 Agent...{Style.RESET_ALL}\n")

        # 創建文檔工程師
        doc_writer_msg = BaseMessage.make_assistant_message(
            role_name="技術文檔工程師",
            content="""你是一位技術文檔工程師。
你會為代碼生成清晰的文檔，包括：
1. 功能說明
2. 參數描述
3. 返回值說明
4. 使用範例
5. 注意事項
使用 Google 風格的文檔字符串。"""
        )

        doc_writer = ChatAgent(
            system_message=doc_writer_msg,
            model_type="gpt-3.5-turbo"
        )

        # 需要文檔的類
        code_class = """
class DataProcessor:
    def __init__(self, config):
        self.config = config
        self.data = []

    def load_data(self, file_path):
        # 載入數據
        pass

    def process(self):
        # 處理數據
        pass

    def export(self, output_path):
        # 導出結果
        pass
"""

        print(f"{Fore.CYAN}需要文檔的類:{Style.RESET_ALL}")
        print(code_class)
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        # 請求生成文檔
        msg = BaseMessage.make_user_message(
            role_name="開發者",
            content=f"""請為以下類生成完整的文檔（docstring）：

{code_class}

使用 Google 風格的文檔字符串格式。"""
        )

        print(f"{Fore.YELLOW}生成文檔...{Style.RESET_ALL}\n")

        response = doc_writer.step(msg)

        print(f"{Fore.GREEN}生成的文檔:{Style.RESET_ALL}\n")
        print(response.msg.content)

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example5_full_development_pipeline():
    """範例5: 完整開發流程"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例5: 完整開發流程（需求 → 實現 → 測試 → 文檔）")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}創建開發團隊...{Style.RESET_ALL}\n")

        # 創建團隊成員
        team = {}

        # 產品經理
        pm_msg = BaseMessage.make_assistant_message(
            role_name="產品經理",
            content="你是產品經理，負責將需求轉化為詳細的功能規格。"
        )
        team["PM"] = ChatAgent(system_message=pm_msg, model_type="gpt-3.5-turbo")

        # 開發者
        dev_msg = BaseMessage.make_assistant_message(
            role_name="開發者",
            content="你是開發者，負責實現功能。代碼要清晰、高效。"
        )
        team["Dev"] = ChatAgent(system_message=dev_msg, model_type="gpt-3.5-turbo")

        # 測試工程師
        qa_msg = BaseMessage.make_assistant_message(
            role_name="QA",
            content="你是測試工程師，負責生成測試用例並驗證功能。"
        )
        team["QA"] = ChatAgent(system_message=qa_msg, model_type="gpt-3.5-turbo")

        # 初始需求
        requirement = "實現一個簡單的任務隊列，支持添加、獲取和查看任務"

        print(f"{Fore.CYAN}初始需求:{Style.RESET_ALL} {requirement}\n")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        # 階段 1: PM 細化需求
        print(f"{Fore.GREEN}[階段 1] 產品經理細化需求{Style.RESET_ALL}\n")

        pm_msg = BaseMessage.make_user_message(
            role_name="客戶",
            content=f"需求：{requirement}\n\n請提供詳細的功能規格。"
        )

        pm_response = team["PM"].step(pm_msg)
        spec = pm_response.msg.content

        print(f"{spec[:300]}...\n")
        print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

        # 階段 2: 開發者實現
        print(f"{Fore.GREEN}[階段 2] 開發者實現功能{Style.RESET_ALL}\n")

        dev_msg = BaseMessage.make_user_message(
            role_name="PM",
            content=f"功能規格：\n{spec}\n\n請實現這個任務隊列類。"
        )

        dev_response = team["Dev"].step(dev_msg)
        code = dev_response.msg.content

        print(f"{code[:400]}...\n")
        print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

        # 階段 3: QA 生成測試
        print(f"{Fore.GREEN}[階段 3] QA 生成測試用例{Style.RESET_ALL}\n")

        qa_msg = BaseMessage.make_user_message(
            role_name="Dev",
            content=f"已實現的代碼：\n{code[:500]}...\n\n請生成測試用例。"
        )

        qa_response = team["QA"].step(qa_msg)
        tests = qa_response.msg.content

        print(f"{tests[:300]}...\n")

        print(f"{Fore.GREEN}{'='*60}")
        print(f"完整開發流程完成！")
        print(f"{'='*60}{Style.RESET_ALL}\n")

        print(f"{Fore.CYAN}流程總結:{Style.RESET_ALL}")
        print("1. PM 細化需求 → 功能規格")
        print("2. Dev 實現代碼 → 可運行的代碼")
        print("3. QA 編寫測試 → 測試用例")
        print("4. (可選) 文檔工程師 → API 文檔\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example6_code_refactoring():
    """範例6: 代碼重構"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例6: 代碼重構建議")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}創建重構專家 Agent...{Style.RESET_ALL}\n")

        # 創建重構專家
        refactor_msg = BaseMessage.make_assistant_message(
            role_name="重構專家",
            content="""你是代碼重構專家。
你會分析代碼並提出改進建議：
1. 識別代碼異味
2. 提出重構方案
3. 展示改進後的代碼
4. 說明改進的好處"""
        )

        refactorer = ChatAgent(
            system_message=refactor_msg,
            model_type="gpt-3.5-turbo"
        )

        # 需要重構的代碼
        messy_code = """
def process_data(data):
    result = []
    for i in range(len(data)):
        if data[i] > 0:
            if data[i] % 2 == 0:
                result.append(data[i] * 2)
            else:
                result.append(data[i] * 3)
        else:
            if data[i] < -10:
                result.append(0)
            else:
                result.append(abs(data[i]))
    return result
"""

        print(f"{Fore.CYAN}原始代碼:{Style.RESET_ALL}")
        print(messy_code)
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        # 請求重構
        msg = BaseMessage.make_user_message(
            role_name="開發者",
            content=f"""請分析以下代碼並提供重構建議：

{messy_code}

請提供：
1. 問題分析
2. 重構後的代碼
3. 改進說明"""
        )

        print(f"{Fore.YELLOW}分析並重構...{Style.RESET_ALL}\n")

        response = refactorer.step(msg)

        print(f"{Fore.GREEN}重構建議:{Style.RESET_ALL}\n")
        print(response.msg.content)

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def main():
    """主函數"""
    print(f"\n{Fore.GREEN}{'='*60}")
    print(f"  CAMEL-AI 代碼生成範例")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    print(f"{Fore.YELLOW}關於代碼生成:{Style.RESET_ALL}")
    print("CAMEL 的多 Agent 協作特別適合軟體開發：")
    print("1. 需求分析 - PM Agent")
    print("2. 代碼實現 - Developer Agent")
    print("3. 代碼審查 - Reviewer Agent")
    print("4. 測試生成 - QA Agent")
    print("5. 文檔撰寫 - Doc Writer Agent\n")

    try:
        example1_basic_code_generation()
        example2_code_review_workflow()
        example3_test_generation()
        example4_documentation_generation()
        example5_full_development_pipeline()
        example6_code_refactoring()

        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"  所有範例執行完成！")
        print(f"{'='*60}{Style.RESET_ALL}\n")

        print(f"{Fore.CYAN}代碼生成最佳實踐:{Style.RESET_ALL}")
        print("1. 清晰的需求描述")
        print("2. 遵循編碼規範")
        print("3. 完整的錯誤處理")
        print("4. 全面的測試覆蓋")
        print("5. 詳細的文檔說明\n")

        print(f"{Fore.CYAN}下一步:{Style.RESET_ALL}")
        print("查看 09_研究助手.py 學習學術研究應用\n")

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}程序被用戶中斷{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}執行過程中發生錯誤: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
