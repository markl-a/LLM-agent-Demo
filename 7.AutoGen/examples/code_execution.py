"""
代碼執行示例
展示如何讓 Agent 生成並執行代碼
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
    "temperature": 0.5  # 降低溫度以獲得更穩定的代碼
}

def main():
    """運行代碼執行示例"""
    # 創建 AI 程序員
    coder = autogen.AssistantAgent(
        name="程序員",
        system_message="""你是一個專業的 Python 程序員。
        當用戶請求時，請編寫清晰、高效的 Python 代碼。
        代碼應該包含：
        1. 詳細的註釋
        2. 錯誤處理
        3. 測試用例
        """,
        llm_config=llm_config
    )

    # 創建代碼執行器
    executor = autogen.UserProxyAgent(
        name="執行器",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={
            "work_dir": "coding",
            "use_docker": False,  # 改為 True 以使用 Docker
        }
    )

    # 任務列表
    tasks = [
        # 任務 1：數學計算
        """
        請寫一個函數來計算斐波那契數列的前 n 項，
        然後計算前 20 項並打印結果。
        """,

        # 任務 2：數據處理
        """
        請生成一個包含 100 個隨機數（0-100之間）的列表，
        然後：
        1. 計算平均值、中位數、標準差
        2. 找出最大值和最小值
        3. 繪製直方圖並保存為 histogram.png
        """,

        # 任務 3：文件操作
        """
        請創建一個 CSV 文件包含以下數據：
        姓名、年齡、城市
        張三、25、北京
        李四、30、上海
        王五、28、深圳

        然後讀取這個文件並打印每一行。
        """
    ]

    # 執行任務
    for i, task in enumerate(tasks, 1):
        print(f"\n{'='*60}")
        print(f"任務 {i}:")
        print('='*60)
        print(task.strip())
        print('='*60)

        executor.initiate_chat(
            coder,
            message=task
        )

        print(f"\n任務 {i} 完成！\n")

if __name__ == "__main__":
    main()
