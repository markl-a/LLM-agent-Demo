"""
Cline 快速開始示例

這個示例展示如何使用 Cline Python SDK 進行基本操作：
1. 初始化 Cline 客戶端
2. 發送簡單的任務請求
3. 接收和處理響應
4. 基本的對話交互

Cline 是一個 VS Code 擴展，這裡我們模擬其 API 使用方式。
"""

import os
import json
from typing import Optional, Dict, Any, List
from anthropic import Anthropic
from dotenv import load_dotenv

# 載入環境變量
load_dotenv()


class ClineClient:
    """Cline 客戶端類 - 模擬 Cline 的核心功能"""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        """
        初始化 Cline 客戶端

        Args:
            api_key: Anthropic API 密鑰（如果為 None，從環境變量讀取）
            model: 使用的模型名稱
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("需要提供 ANTHROPIC_API_KEY")

        self.model = model
        self.client = Anthropic(api_key=self.api_key)
        self.conversation_history: List[Dict[str, str]] = []

        # Cline 的系統提示詞
        self.system_prompt = """你是 Cline，一個 VS Code 自主編程助手。
你可以：
1. 讀取和分析項目文件
2. 搜索代碼內容
3. 執行終端命令
4. 自動修改代碼文件
5. 規劃和執行複雜任務

當用戶提出需求時，你應該：
1. 理解需求
2. 制定計劃（如果在 Plan 模式）
3. 執行任務
4. 報告結果
"""

    def send_message(self, message: str, mode: str = "act") -> str:
        """
        發送消息給 Cline

        Args:
            message: 用戶消息
            mode: 模式（"plan" 或 "act"）

        Returns:
            Cline 的響應
        """
        # 添加模式指示
        if mode == "plan":
            enhanced_message = f"[PLAN MODE] {message}\n請先制定詳細計劃，不要立即執行。"
        else:
            enhanced_message = f"[ACT MODE] {message}\n請直接執行任務。"

        # 添加到對話歷史
        self.conversation_history.append({
            "role": "user",
            "content": enhanced_message
        })

        # 調用 Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=self.system_prompt,
            messages=self.conversation_history
        )

        # 提取響應文本
        assistant_message = response.content[0].text

        # 添加到對話歷史
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def clear_history(self):
        """清除對話歷史"""
        self.conversation_history = []

    def get_history(self) -> List[Dict[str, str]]:
        """獲取對話歷史"""
        return self.conversation_history.copy()


def example_basic_usage():
    """示例 1: 基本使用"""
    print("=" * 60)
    print("示例 1: Cline 基本使用")
    print("=" * 60)

    # 初始化客戶端
    client = ClineClient()

    # 發送簡單的代碼生成請求
    response = client.send_message(
        "創建一個 Python 函數，用於計算斐波那契數列"
    )

    print("\n用戶請求: 創建一個 Python 函數，用於計算斐波那契數列")
    print("\nCline 響應:")
    print(response)
    print()


def example_plan_mode():
    """示例 2: 使用 Plan 模式"""
    print("=" * 60)
    print("示例 2: Plan 模式 - 先規劃再執行")
    print("=" * 60)

    client = ClineClient()

    # 使用 Plan 模式處理複雜任務
    task = """
    重構一個 Python Web 應用：
    1. 將單體應用拆分為微服務架構
    2. 添加 Redis 緩存層
    3. 實現 API 限流
    """

    response = client.send_message(task, mode="plan")

    print("\n用戶請求:")
    print(task)
    print("\nCline Plan 模式響應:")
    print(response)
    print()


def example_act_mode():
    """示例 3: 使用 Act 模式"""
    print("=" * 60)
    print("示例 3: Act 模式 - 直接執行")
    print("=" * 60)

    client = ClineClient()

    # 使用 Act 模式快速完成簡單任務
    task = "編寫一個函數來驗證電子郵件地址格式"

    response = client.send_message(task, mode="act")

    print("\n用戶請求:", task)
    print("\nCline Act 模式響應:")
    print(response)
    print()


def example_multi_turn_conversation():
    """示例 4: 多輪對話"""
    print("=" * 60)
    print("示例 4: 多輪對話交互")
    print("=" * 60)

    client = ClineClient()

    # 第一輪：創建基礎代碼
    print("\n[第 1 輪] 創建基礎代碼")
    response1 = client.send_message(
        "創建一個簡單的 Python 類來管理待辦事項"
    )
    print("響應:", response1[:200] + "...\n")

    # 第二輪：添加功能
    print("[第 2 輪] 添加功能")
    response2 = client.send_message(
        "為這個類添加保存到文件的功能"
    )
    print("響應:", response2[:200] + "...\n")

    # 第三輪：添加測試
    print("[第 3 輪] 添加測試")
    response3 = client.send_message(
        "為這個類編寫單元測試"
    )
    print("響應:", response3[:200] + "...\n")

    # 顯示對話歷史
    print(f"\n總共進行了 {len(client.get_history())} 輪對話")


def example_with_context():
    """示例 5: 帶上下文的請求"""
    print("=" * 60)
    print("示例 5: 提供項目上下文")
    print("=" * 60)

    client = ClineClient()

    # 提供項目上下文
    context = """
    項目結構:
    - src/
      - models/
        - user.py
        - product.py
      - api/
        - routes.py
      - utils/
        - auth.py

    當前使用技術棧:
    - FastAPI
    - SQLAlchemy
    - PostgreSQL
    - Redis
    """

    task = f"""
    {context}

    請在 src/api/routes.py 中添加一個新的產品搜索端點，
    要求：
    1. 支持關鍵詞搜索
    2. 支持分頁
    3. 使用 Redis 緩存結果
    4. 遵循現有的代碼風格
    """

    response = client.send_message(task, mode="plan")

    print("\n任務（帶上下文）:")
    print(task)
    print("\nCline 響應:")
    print(response)
    print()


def example_error_handling():
    """示例 6: 錯誤處理"""
    print("=" * 60)
    print("示例 6: 錯誤處理")
    print("=" * 60)

    try:
        # 嘗試使用無效的 API 密鑰
        client = ClineClient(api_key="invalid-key")
        response = client.send_message("Hello")
    except Exception as e:
        print(f"\n捕獲到錯誤: {type(e).__name__}")
        print(f"錯誤信息: {str(e)}")

    # 正確的錯誤處理方式
    try:
        client = ClineClient()
        response = client.send_message("創建一個函數")
        print("\n請求成功!")
        print(f"響應長度: {len(response)} 字符")
    except ValueError as e:
        print(f"\n配置錯誤: {e}")
        print("請設置 ANTHROPIC_API_KEY 環境變量")
    except Exception as e:
        print(f"\n發生錯誤: {e}")

    print()


def example_streaming_response():
    """示例 7: 流式響應（模擬）"""
    print("=" * 60)
    print("示例 7: 流式響應")
    print("=" * 60)

    client = ClineClient()

    print("\n用戶: 創建一個計算器類")
    print("\nCline 響應（流式）:")
    print("-" * 40)

    # 注意：實際的流式響應需要使用 Anthropic 的 stream API
    # 這裡僅作示意
    response = client.send_message("創建一個簡單的計算器類")

    # 模擬流式輸出
    import time
    for i in range(0, len(response), 50):
        chunk = response[i:i+50]
        print(chunk, end='', flush=True)
        time.sleep(0.1)  # 模擬延遲

    print("\n" + "-" * 40)
    print()


def main():
    """主函數 - 運行所有示例"""
    print("\n" + "=" * 60)
    print("Cline 快速開始示例集")
    print("=" * 60 + "\n")

    # 檢查 API 密鑰
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  警告: 未設置 ANTHROPIC_API_KEY 環境變量")
        print("請在 .env 文件中設置或通過環境變量設置")
        print("\n示例 .env 文件:")
        print("ANTHROPIC_API_KEY=sk-ant-api03-...")
        return

    try:
        # 運行示例（注釋掉以節省 API 調用）
        # example_basic_usage()
        # example_plan_mode()
        # example_act_mode()
        # example_multi_turn_conversation()
        # example_with_context()
        example_error_handling()
        # example_streaming_response()

        print("\n✅ 所有示例運行完成!")
        print("\n💡 提示:")
        print("1. 取消注釋 main() 中的函數來運行具體示例")
        print("2. 設置 ANTHROPIC_API_KEY 以使用完整功能")
        print("3. 使用 Plan 模式處理複雜任務")
        print("4. 使用 Act 模式快速完成簡單任務")

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
