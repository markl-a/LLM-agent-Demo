"""
CAMEL-AI 快速開始

這個範例展示如何快速開始使用 CAMEL 框架：
1. 創建基礎 Agent
2. 發送和接收消息
3. 簡單的對話交互
4. 配置 Agent 參數

CAMEL (Communicative Agents for "Mind" Exploration of Large Language Model Society)
是一個專注於多 Agent 角色扮演和協作的框架。
"""

import os
from dotenv import load_dotenv
from colorama import init, Fore, Style

# 初始化 colorama 用於彩色輸出
init(autoreset=True)

# 載入環境變量
load_dotenv()

# 驗證 API 密鑰
if not os.getenv("OPENAI_API_KEY"):
    print(f"{Fore.RED}錯誤: 請在 .env 文件中設置 OPENAI_API_KEY{Style.RESET_ALL}")
    print("創建 .env 文件並添加: OPENAI_API_KEY=your_api_key_here")
    exit(1)


def example1_basic_agent():
    """範例1: 創建基礎 Agent"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例1: 創建基礎 Agent")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage
        from camel.types import RoleType

        # 創建一個簡單的 ChatAgent
        print(f"{Fore.YELLOW}創建 ChatAgent...{Style.RESET_ALL}")

        assistant_sys_msg = BaseMessage.make_assistant_message(
            role_name="助手",
            content="你是一位友善且專業的 AI 助手，擅長回答各種問題。"
        )

        agent = ChatAgent(
            system_message=assistant_sys_msg,
            model_type="gpt-3.5-turbo"  # 使用 GPT-3.5 節省成本
        )

        print(f"{Fore.GREEN}Agent 創建成功！{Style.RESET_ALL}")
        print(f"模型: gpt-3.5-turbo")
        print(f"角色: 助手\n")

        # 發送消息
        print(f"{Fore.YELLOW}發送消息給 Agent...{Style.RESET_ALL}")

        user_msg = BaseMessage.make_user_message(
            role_name="用戶",
            content="你好！請簡單介紹一下 CAMEL 框架。"
        )

        print(f"{Fore.BLUE}用戶:{Style.RESET_ALL} {user_msg.content}\n")

        # 獲取回應
        response = agent.step(user_msg)

        print(f"{Fore.GREEN}助手:{Style.RESET_ALL} {response.msg.content}\n")

        # 查看消息元數據
        print(f"{Fore.CYAN}消息元數據:{Style.RESET_ALL}")
        print(f"  - 角色類型: {response.msg.role_type}")
        print(f"  - 角色名稱: {response.msg.role_name}")
        print(f"  - Token 使用: {response.info.get('usage', {})}")

    except ImportError as e:
        print(f"{Fore.RED}錯誤: 缺少必要的套件{Style.RESET_ALL}")
        print(f"請執行: pip install camel-ai[all]")
        print(f"詳細錯誤: {e}")
    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example2_multi_turn_conversation():
    """範例2: 多輪對話"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例2: 多輪對話")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        # 創建 Agent
        assistant_sys_msg = BaseMessage.make_assistant_message(
            role_name="Python 導師",
            content="你是一位經驗豐富的 Python 程式設計導師，善於用簡單的例子解釋概念。"
        )

        agent = ChatAgent(
            system_message=assistant_sys_msg,
            model_type="gpt-3.5-turbo"
        )

        # 多輪對話
        questions = [
            "什麼是 Python 裝飾器？",
            "能給我一個簡單的例子嗎？",
            "裝飾器的實際應用場景有哪些？"
        ]

        print(f"{Fore.YELLOW}開始多輪對話...{Style.RESET_ALL}\n")

        for i, question in enumerate(questions, 1):
            print(f"{Fore.CYAN}[第 {i} 輪]{Style.RESET_ALL}")
            print(f"{Fore.BLUE}用戶:{Style.RESET_ALL} {question}\n")

            user_msg = BaseMessage.make_user_message(
                role_name="學生",
                content=question
            )

            response = agent.step(user_msg)

            print(f"{Fore.GREEN}導師:{Style.RESET_ALL} {response.msg.content}\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

        # 查看對話歷史
        print(f"{Fore.CYAN}對話歷史記錄:{Style.RESET_ALL}")
        print(f"總共 {len(agent.memory.get_messages())} 條消息")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example3_custom_configuration():
    """範例3: 自定義配置"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例3: 自定義 Agent 配置")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage
        from camel.configs import ChatGPTConfig
        from camel.types import ModelType

        # 創建自定義配置
        print(f"{Fore.YELLOW}配置 Agent 參數...{Style.RESET_ALL}")

        config = ChatGPTConfig(
            temperature=0.8,      # 增加創造性
            max_tokens=500,       # 限制輸出長度
            top_p=0.9,           # 核採樣
            presence_penalty=0.1, # 減少重複
            frequency_penalty=0.1 # 減少重複
        )

        print(f"{Fore.CYAN}配置參數:{Style.RESET_ALL}")
        print(f"  - Temperature: {config.temperature}")
        print(f"  - Max Tokens: {config.max_tokens}")
        print(f"  - Top P: {config.top_p}")
        print(f"  - Presence Penalty: {config.presence_penalty}")
        print(f"  - Frequency Penalty: {config.frequency_penalty}\n")

        # 創建使用自定義配置的 Agent
        assistant_sys_msg = BaseMessage.make_assistant_message(
            role_name="創意作家",
            content="你是一位富有創造力的作家，擅長寫故事和詩歌。"
        )

        agent = ChatAgent(
            system_message=assistant_sys_msg,
            model_type=ModelType.GPT_3_5_TURBO,
            model_config=config
        )

        print(f"{Fore.YELLOW}測試創意輸出...{Style.RESET_ALL}\n")

        user_msg = BaseMessage.make_user_message(
            role_name="讀者",
            content="請為我創作一首關於「AI 與人類合作」的短詩。"
        )

        print(f"{Fore.BLUE}讀者:{Style.RESET_ALL} {user_msg.content}\n")

        response = agent.step(user_msg)

        print(f"{Fore.GREEN}作家:{Style.RESET_ALL}")
        print(response.msg.content)

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example4_message_types():
    """範例4: 不同類型的消息"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例4: 不同類型的消息")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.messages import BaseMessage
        from camel.types import RoleType

        # 創建不同類型的消息
        print(f"{Fore.YELLOW}創建不同角色的消息...{Style.RESET_ALL}\n")

        # 系統消息
        system_msg = BaseMessage(
            role_name="系統",
            role_type=RoleType.ASSISTANT,
            meta_dict={},
            content="你是一位專業的數據分析師。"
        )

        print(f"{Fore.CYAN}1. 系統消息:{Style.RESET_ALL}")
        print(f"   角色: {system_msg.role_name}")
        print(f"   類型: {system_msg.role_type}")
        print(f"   內容: {system_msg.content}\n")

        # 用戶消息
        user_msg = BaseMessage.make_user_message(
            role_name="客戶",
            content="請分析這組銷售數據的趨勢。"
        )

        print(f"{Fore.CYAN}2. 用戶消息:{Style.RESET_ALL}")
        print(f"   角色: {user_msg.role_name}")
        print(f"   類型: {user_msg.role_type}")
        print(f"   內容: {user_msg.content}\n")

        # 助手消息
        assistant_msg = BaseMessage.make_assistant_message(
            role_name="分析師",
            content="我會為您分析數據並提供詳細報告。"
        )

        print(f"{Fore.CYAN}3. 助手消息:{Style.RESET_ALL}")
        print(f"   角色: {assistant_msg.role_name}")
        print(f"   類型: {assistant_msg.role_type}")
        print(f"   內容: {assistant_msg.content}\n")

        # 帶元數據的消息
        meta_msg = BaseMessage(
            role_name="用戶",
            role_type=RoleType.USER,
            meta_dict={
                "timestamp": "2024-01-01 10:00:00",
                "priority": "high",
                "category": "數據分析"
            },
            content="這是一條帶元數據的消息。"
        )

        print(f"{Fore.CYAN}4. 帶元數據的消息:{Style.RESET_ALL}")
        print(f"   角色: {meta_msg.role_name}")
        print(f"   元數據: {meta_msg.meta_dict}")
        print(f"   內容: {meta_msg.content}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example5_error_handling():
    """範例5: 錯誤處理和重試機制"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例5: 錯誤處理和重試機制")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage
        import time

        print(f"{Fore.YELLOW}演示錯誤處理機制...{Style.RESET_ALL}\n")

        assistant_sys_msg = BaseMessage.make_assistant_message(
            role_name="助手",
            content="你是一位有幫助的助手。"
        )

        agent = ChatAgent(
            system_message=assistant_sys_msg,
            model_type="gpt-3.5-turbo"
        )

        # 實施重試邏輯
        max_retries = 3
        retry_delay = 2

        user_msg = BaseMessage.make_user_message(
            role_name="用戶",
            content="介紹一下你自己。"
        )

        for attempt in range(max_retries):
            try:
                print(f"{Fore.CYAN}嘗試 {attempt + 1}/{max_retries}{Style.RESET_ALL}")

                response = agent.step(user_msg)

                print(f"{Fore.GREEN}成功！{Style.RESET_ALL}")
                print(f"回應: {response.msg.content[:100]}...\n")
                break

            except Exception as e:
                print(f"{Fore.YELLOW}發生錯誤: {e}{Style.RESET_ALL}")

                if attempt < max_retries - 1:
                    print(f"等待 {retry_delay} 秒後重試...\n")
                    time.sleep(retry_delay)
                else:
                    print(f"{Fore.RED}已達到最大重試次數{Style.RESET_ALL}")
                    raise

        # 輸入驗證示例
        print(f"{Fore.YELLOW}輸入驗證示例...{Style.RESET_ALL}\n")

        def validate_and_send(content: str):
            """驗證並發送消息"""
            # 檢查消息長度
            if len(content) > 4000:
                print(f"{Fore.RED}錯誤: 消息太長（超過 4000 字符）{Style.RESET_ALL}")
                return None

            # 檢查空消息
            if not content.strip():
                print(f"{Fore.RED}錯誤: 消息不能為空{Style.RESET_ALL}")
                return None

            # 發送消息
            msg = BaseMessage.make_user_message(
                role_name="用戶",
                content=content
            )

            response = agent.step(msg)
            return response

        # 測試驗證
        test_cases = [
            ("你好", True),
            ("", False),
            ("x" * 5000, False)
        ]

        for content, should_succeed in test_cases:
            desc = content[:20] if content else "(空消息)"
            print(f"{Fore.CYAN}測試: {desc}{Style.RESET_ALL}")

            result = validate_and_send(content)

            if should_succeed:
                if result:
                    print(f"{Fore.GREEN}✓ 驗證通過{Style.RESET_ALL}\n")
                else:
                    print(f"{Fore.RED}✗ 應該成功但失敗了{Style.RESET_ALL}\n")
            else:
                if not result:
                    print(f"{Fore.GREEN}✓ 正確拒絕無效輸入{Style.RESET_ALL}\n")
                else:
                    print(f"{Fore.RED}✗ 應該失敗但成功了{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def main():
    """主函數"""
    print(f"\n{Fore.GREEN}{'='*60}")
    print(f"  CAMEL-AI 快速開始範例")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    print(f"{Fore.YELLOW}CAMEL 框架簡介:{Style.RESET_ALL}")
    print("CAMEL (Communicative Agents for 'Mind' Exploration)")
    print("是一個專注於多 Agent 角色扮演和協作的開源框架。\n")

    # 執行所有範例
    try:
        example1_basic_agent()
        example2_multi_turn_conversation()
        example3_custom_configuration()
        example4_message_types()
        example5_error_handling()

        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"  所有範例執行完成！")
        print(f"{'='*60}{Style.RESET_ALL}\n")

        print(f"{Fore.CYAN}下一步建議:{Style.RESET_ALL}")
        print("1. 查看 02_角色扮演.py 學習角色定義")
        print("2. 查看 04_雙Agent對話.py 學習 Agent 協作")
        print("3. 閱讀 README.md 了解更多功能\n")

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}程序被用戶中斷{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}執行過程中發生錯誤: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
