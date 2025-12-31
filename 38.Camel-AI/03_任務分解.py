"""
CAMEL-AI 任務分解

這個範例展示如何使用 CAMEL 進行任務分解：
1. 將複雜任務分解為子任務
2. Task Specifier 的使用
3. 層次化任務規劃
4. 任務依賴關係管理
5. 自動化任務執行

任務分解是將複雜問題轉化為可執行步驟的關鍵能力。
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


def example1_task_specification():
    """範例1: 任務具體化"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例1: 使用 Task Specifier 具體化任務")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import TaskSpecifierAgent

        print(f"{Fore.YELLOW}創建 TaskSpecifierAgent...{Style.RESET_ALL}\n")

        # 創建任務具體化 Agent
        task_specifier = TaskSpecifierAgent(
            model_type="gpt-3.5-turbo"
        )

        # 模糊的任務描述
        vague_tasks = [
            "開發一個網站",
            "改進系統性能",
            "實現用戶功能"
        ]

        print(f"{Fore.CYAN}將模糊任務轉化為具體任務:{Style.RESET_ALL}\n")

        for i, vague_task in enumerate(vague_tasks, 1):
            print(f"{Fore.MAGENTA}[任務 {i}]{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}模糊描述:{Style.RESET_ALL} {vague_task}")

            # 具體化任務
            specified_task = task_specifier.run(
                task_prompt=vague_task,
                meta_dict={
                    "assistant_role": "軟體工程師",
                    "user_role": "產品經理",
                    "word_limit": 100
                }
            )

            print(f"{Fore.GREEN}具體描述:{Style.RESET_ALL}")
            print(f"{specified_task}\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()


def example2_hierarchical_decomposition():
    """範例2: 層次化任務分解"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例2: 層次化任務分解")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}創建任務分解 Agent...{Style.RESET_ALL}\n")

        # 創建專門用於任務分解的 Agent
        decomposer_msg = BaseMessage.make_assistant_message(
            role_name="任務規劃師",
            content="""你是一位專業的任務規劃師。
當給你一個複雜任務時，你會：
1. 識別主要目標
2. 分解為主要階段
3. 每個階段細分為具體步驟
4. 標注依賴關係
5. 估計時間和資源

請使用清晰的層次結構組織任務。"""
        )

        decomposer = ChatAgent(
            system_message=decomposer_msg,
            model_type="gpt-3.5-turbo"
        )

        # 複雜任務
        complex_task = "開發一個包含用戶認證、數據管理和 API 的 Web 應用"

        print(f"{Fore.CYAN}複雜任務:{Style.RESET_ALL}")
        print(f"{complex_task}\n")

        # 請求分解
        decompose_msg = BaseMessage.make_user_message(
            role_name="項目經理",
            content=f"""請將以下任務分解為層次化的執行計劃：

任務: {complex_task}

請提供：
1. 主要階段（Phase）
2. 每個階段的具體步驟（Steps）
3. 步驟之間的依賴關係
4. 預估時間"""
        )

        print(f"{Fore.YELLOW}正在分解任務...{Style.RESET_ALL}\n")

        response = decomposer.step(decompose_msg)

        print(f"{Fore.GREEN}任務分解結果:{Style.RESET_ALL}\n")
        print(response.msg.content)

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example3_task_dependency_graph():
    """範例3: 任務依賴關係圖"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例3: 分析任務依賴關係")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}創建依賴分析 Agent...{Style.RESET_ALL}\n")

        # 創建依賴分析 Agent
        dependency_analyzer_msg = BaseMessage.make_assistant_message(
            role_name="依賴分析師",
            content="""你是一位專業的任務依賴分析師。
你會分析任務之間的依賴關係，包括：
1. 前置任務（Prerequisites）
2. 並行任務（Parallel）
3. 阻塞關係（Blocking）
4. 關鍵路徑（Critical Path）

以結構化的方式呈現依賴關係。"""
        )

        analyzer = ChatAgent(
            system_message=dependency_analyzer_msg,
            model_type="gpt-3.5-turbo"
        )

        # 任務列表
        tasks = """
任務列表：
1. 設計數據庫架構
2. 實現用戶認證
3. 創建 API 端點
4. 開發前端界面
5. 編寫測試
6. 部署系統
"""

        print(f"{Fore.CYAN}任務列表:{Style.RESET_ALL}")
        print(tasks)

        # 分析依賴
        analysis_msg = BaseMessage.make_user_message(
            role_name="項目經理",
            content=f"""請分析以下任務的依賴關係：

{tasks}

請提供：
1. 每個任務的前置任務
2. 可以並行執行的任務組
3. 關鍵路徑
4. 建議的執行順序"""
        )

        print(f"{Fore.YELLOW}正在分析依賴關係...{Style.RESET_ALL}\n")

        response = analyzer.step(analysis_msg)

        print(f"{Fore.GREEN}依賴關係分析:{Style.RESET_ALL}\n")
        print(response.msg.content)

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example4_adaptive_planning():
    """範例4: 自適應任務規劃"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例4: 自適應任務規劃")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}創建自適應規劃 Agent...{Style.RESET_ALL}\n")

        # 創建規劃 Agent
        planner_msg = BaseMessage.make_assistant_message(
            role_name="敏捷規劃師",
            content="""你是一位敏捷開發規劃師。
你會根據約束條件調整任務計劃：
1. 時間約束
2. 資源約束
3. 優先級
4. 風險評估

你會提供可行的執行方案。"""
        )

        planner = ChatAgent(
            system_message=planner_msg,
            model_type="gpt-3.5-turbo"
        )

        # 不同約束下的規劃
        constraints = [
            {
                "name": "緊急項目",
                "constraint": "必須在 2 週內完成，團隊 3 人",
                "task": "開發電商系統的核心功能"
            },
            {
                "name": "資源受限",
                "constraint": "只有 1 名開發者，時間充足（3 個月）",
                "task": "開發電商系統的核心功能"
            },
            {
                "name": "高質量要求",
                "constraint": "需要完整測試和文檔，時間 1 個月，團隊 5 人",
                "task": "開發電商系統的核心功能"
            }
        ]

        for scenario in constraints:
            print(f"{Fore.CYAN}場景: {scenario['name']}{Style.RESET_ALL}")
            print(f"約束: {scenario['constraint']}")
            print(f"任務: {scenario['task']}\n")

            planning_msg = BaseMessage.make_user_message(
                role_name="項目經理",
                content=f"""請根據以下約束條件制定執行計劃：

任務: {scenario['task']}
約束: {scenario['constraint']}

請提供：
1. 優先執行的功能
2. 可能需要犧牲的部分
3. 具體時間表
4. 風險點"""
            )

            print(f"{Fore.YELLOW}生成計劃...{Style.RESET_ALL}\n")

            response = planner.step(planning_msg)

            print(f"{Fore.GREEN}執行計劃:{Style.RESET_ALL}")
            print(f"{response.msg.content[:400]}...\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example5_task_execution_flow():
    """範例5: 任務執行流程"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例5: 完整的任務執行流程")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.societies import RolePlaying
        from camel.types import TaskType

        print(f"{Fore.YELLOW}演示：從任務分解到執行{Style.RESET_ALL}\n")

        # 階段 1: 任務規劃
        print(f"{Fore.CYAN}[階段 1] 任務規劃{Style.RESET_ALL}\n")

        planning_session = RolePlaying(
            assistant_role_name="技術架構師",
            user_role_name="產品經理",
            task_prompt="規劃一個實時聊天系統的開發",
            task_type=TaskType.CODE,
        )

        input_msg = planning_session.init_chat()

        print(f"{Fore.GREEN}技術架構師:{Style.RESET_ALL}")
        assistant_response, _ = planning_session.step(input_msg)
        print(f"{assistant_response.msg.content[:300]}...\n")

        # 階段 2: 任務分解
        print(f"{Fore.CYAN}[階段 2] 詳細分解{Style.RESET_ALL}\n")

        user_response, _ = planning_session.step(assistant_response.msg)
        print(f"{Fore.BLUE}產品經理:{Style.RESET_ALL}")
        print(f"{user_response.msg.content[:300]}...\n")

        # 階段 3: 執行第一個子任務
        print(f"{Fore.CYAN}[階段 3] 執行第一個子任務{Style.RESET_ALL}\n")

        implementation_session = RolePlaying(
            assistant_role_name="後端開發工程師",
            user_role_name="技術主管",
            task_prompt="實現實時聊天系統的 WebSocket 連接",
            task_type=TaskType.CODE,
        )

        impl_input = implementation_session.init_chat()
        impl_response, _ = implementation_session.step(impl_input)

        print(f"{Fore.GREEN}後端開發工程師:{Style.RESET_ALL}")
        print(f"{impl_response.msg.content[:300]}...\n")

        print(f"{Fore.GREEN}任務執行流程演示完成！{Style.RESET_ALL}\n")

        print(f"{Fore.CYAN}流程總結:{Style.RESET_ALL}")
        print("1. 產品經理與架構師討論需求")
        print("2. 架構師規劃技術方案")
        print("3. 分解為具體的開發任務")
        print("4. 工程師執行具體任務")
        print("5. 持續迭代和優化\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


class TaskDecomposer:
    """任務分解器類"""

    def __init__(self):
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        decomposer_msg = BaseMessage.make_assistant_message(
            role_name="任務分解器",
            content="""你是一位任務分解專家。
分解任務時要：
1. 確保每個子任務獨立且可執行
2. 考慮依賴關係
3. 保持適當的粒度
4. 提供清晰的描述"""
        )

        self.agent = ChatAgent(
            system_message=decomposer_msg,
            model_type="gpt-3.5-turbo"
        )

    def decompose(self, task: str, depth: int = 2) -> List[str]:
        """分解任務"""
        from camel.messages import BaseMessage

        msg = BaseMessage.make_user_message(
            role_name="用戶",
            content=f"請將以下任務分解為 {depth} 層的子任務列表：\n{task}"
        )

        response = self.agent.step(msg)
        return response.msg.content


def example6_custom_decomposer():
    """範例6: 自定義任務分解器"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例6: 使用自定義任務分解器")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        print(f"{Fore.YELLOW}創建自定義分解器...{Style.RESET_ALL}\n")

        decomposer = TaskDecomposer()

        task = "構建一個機器學習模型用於圖像分類"

        print(f"{Fore.CYAN}原始任務:{Style.RESET_ALL}")
        print(f"{task}\n")

        print(f"{Fore.YELLOW}執行分解...{Style.RESET_ALL}\n")

        subtasks = decomposer.decompose(task, depth=2)

        print(f"{Fore.GREEN}分解結果:{Style.RESET_ALL}\n")
        print(subtasks)

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def main():
    """主函數"""
    print(f"\n{Fore.GREEN}{'='*60}")
    print(f"  CAMEL-AI 任務分解範例")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    print(f"{Fore.YELLOW}關於任務分解:{Style.RESET_ALL}")
    print("任務分解是將複雜問題轉化為可執行步驟的過程。")
    print("CAMEL 提供多種方式進行任務分解：")
    print("1. Task Specifier - 具體化模糊任務")
    print("2. 層次化分解 - 多層次的任務結構")
    print("3. 依賴分析 - 識別任務間關係")
    print("4. 自適應規劃 - 根據約束調整計劃\n")

    try:
        example1_task_specification()
        example2_hierarchical_decomposition()
        example3_task_dependency_graph()
        example4_adaptive_planning()
        example5_task_execution_flow()
        example6_custom_decomposer()

        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"  所有範例執行完成！")
        print(f"{'='*60}{Style.RESET_ALL}\n")

        print(f"{Fore.CYAN}任務分解最佳實踐:{Style.RESET_ALL}")
        print("1. 保持子任務的獨立性")
        print("2. 明確任務間的依賴關係")
        print("3. 適當的任務粒度（不要太粗或太細）")
        print("4. 考慮資源和時間約束")
        print("5. 保持靈活性以應對變化\n")

        print(f"{Fore.CYAN}下一步:{Style.RESET_ALL}")
        print("查看 04_雙Agent對話.py 學習兩個 Agent 的協作\n")

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}程序被用戶中斷{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}執行過程中發生錯誤: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
