"""
簡單對話示例
這是最基礎的 AutoGen 對話示例
"""

import os
from dotenv import load_dotenv
import autogen

# 加載環境變量
load_dotenv()

# 配置 LLM
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

def main():
    """運行簡單對話"""
    # 創建 Assistant Agent
    assistant = autogen.AssistantAgent(
        name="助理",
        system_message="你是一個樂於助人的 AI 助理，擅長回答各種問題。",
        llm_config=llm_config
    )

    # 創建 User Proxy Agent
    user_proxy = autogen.UserProxyAgent(
        name="用戶",
        human_input_mode="TERMINATE",  # 最後需要人工確認
        max_consecutive_auto_reply=5,
        code_execution_config=False  # 不執行代碼
    )

    # 開始對話
    message = """請告訴我 AutoGen 的三個主要優勢，
    並用簡單的例子說明每個優勢。"""

    print(f"\n{'='*60}")
    print("開始對話...")
    print('='*60)

    user_proxy.initiate_chat(
        assistant,
        message=message
    )

if __name__ == "__main__":
    main()
