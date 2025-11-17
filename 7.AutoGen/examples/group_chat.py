"""
群組對話示例
展示多個 Agent 如何協作完成任務
"""

import os
from dotenv import load_dotenv
import autogen

load_dotenv()

config_list = [
    {
        "model": "gpt-4",
        "api_key": os.getenv("OPENAI_API_KEY")
    }
]

llm_config = {
    "config_list": config_list,
    "temperature": 0.7
}

def create_writing_team():
    """創建寫作團隊"""

    # 研究員
    researcher = autogen.AssistantAgent(
        name="研究員",
        system_message="""你是一個研究員，負責收集和分析信息。
        你的職責：
        1. 研究主題背景
        2. 收集相關資料
        3. 提供事實和數據
        完成後在回復末尾添加 "研究完成"。
        """,
        llm_config=llm_config
    )

    # 作家
    writer = autogen.AssistantAgent(
        name="作家",
        system_message="""你是一個專業作家，負責撰寫文章。
        你的職責：
        1. 根據研究結果撰寫文章
        2. 使用清晰、引人入勝的語言
        3. 確保邏輯流暢
        完成後在回復末尾添加 "撰寫完成"。
        """,
        llm_config=llm_config
    )

    # 編輯
    editor = autogen.AssistantAgent(
        name="編輯",
        system_message="""你是一個專業編輯，負責審查和改進文章。
        你的職責：
        1. 檢查語法和拼寫
        2. 改進文章結構
        3. 提供修改建議
        4. 確保文章質量
        完成後在回復末尾添加 "TERMINATE"。
        """,
        llm_config=llm_config
    )

    # 用戶代理
    user_proxy = autogen.UserProxyAgent(
        name="用戶",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=15,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config=False
    )

    return [user_proxy, researcher, writer, editor]

def main():
    """運行群組對話示例"""
    # 創建團隊
    team = create_writing_team()

    # 創建群組聊天
    groupchat = autogen.GroupChat(
        agents=team,
        messages=[],
        max_round=15
    )

    # 創建管理器
    manager = autogen.GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config
    )

    # 寫作任務
    topic = """
    請撰寫一篇關於「人工智能如何改變教育行業」的文章。

    要求：
    1. 包含至少 3 個具體的應用案例
    2. 分析優勢和挑戰
    3. 展望未來發展
    4. 文章長度約 500 字

    流程：
    1. 研究員：進行背景調研
    2. 作家：撰寫初稿
    3. 編輯：審查並改進
    """

    print(f"\n{'='*60}")
    print("寫作團隊協作開始...")
    print('='*60)

    # 開始協作
    team[0].initiate_chat(
        manager,
        message=topic
    )

if __name__ == "__main__":
    main()
