"""
自定義角色示例
展示如何創建和使用自定義角色

這個示例演示:
1. 創建自定義 Action
2. 創建自定義 Role
3. 在團隊中使用自定義角色
"""

import asyncio
from metagpt.roles import Role
from metagpt.actions import Action
from metagpt.schema import Message
from metagpt.team import Team
from metagpt.logs import logger


# ==================== 自定義 Actions ====================

class WriteCodeReview(Action):
    """代碼審查 Action"""

    name: str = "WriteCodeReview"

    async def run(self, code: str) -> str:
        """
        執行代碼審查

        Args:
            code: 要審查的代碼

        Returns:
            審查報告
        """
        prompt = f"""
        請審查以下代碼，並提供改進建議:

        {code}

        請從以下角度審查:
        1. 代碼質量和可讀性
        2. 潛在的性能問題
        3. 安全漏洞
        4. 最佳實踐
        5. 可維護性

        提供具體的改進建議。
        """

        # 調用 LLM 進行審查
        result = await self._aask(prompt)
        return result


class GenerateDocumentation(Action):
    """文檔生成 Action"""

    name: str = "GenerateDocumentation"

    async def run(self, code: str) -> str:
        """
        生成代碼文檔

        Args:
            code: 要生成文檔的代碼

        Returns:
            文檔內容
        """
        prompt = f"""
        為以下代碼生成詳細的文檔:

        {code}

        請包含:
        1. 功能概述
        2. 函數/類的詳細說明
        3. 參數說明
        4. 返回值說明
        5. 使用示例
        6. 注意事項
        """

        result = await self._aask(prompt)
        return result


# ==================== 自定義 Roles ====================

class CodeReviewer(Role):
    """
    代碼審查員角色
    負責審查代碼質量並提供改進建議
    """

    name: str = "CodeReviewer"
    profile: str = "代碼審查專家"
    goal: str = "確保代碼質量，發現潛在問題"
    constraints: str = "基於最佳實踐和編碼規範進行審查"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([WriteCodeReview])

    async def _act(self) -> Message:
        """
        執行代碼審查
        """
        logger.info(f"{self.name}: 開始代碼審查...")

        # 獲取要審查的代碼
        todo = self.rc.todo
        memories = self.get_memories()

        # 執行審查
        code = str(memories) if memories else "# 示例代碼"
        review = await todo.run(code)

        # 創建消息
        msg = Message(
            content=review,
            role=self.profile,
            cause_by=type(todo)
        )

        return msg


class TechnicalWriter(Role):
    """
    技術文檔撰寫員
    負責生成技術文檔
    """

    name: str = "TechnicalWriter"
    profile: str = "技術文檔專家"
    goal: str = "撰寫清晰、完整的技術文檔"
    constraints: str = "文檔應易於理解，包含詳細示例"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([GenerateDocumentation])

    async def _act(self) -> Message:
        """
        生成技術文檔
        """
        logger.info(f"{self.name}: 開始撰寫文檔...")

        todo = self.rc.todo
        memories = self.get_memories()

        code = str(memories) if memories else "# 示例代碼"
        docs = await todo.run(code)

        msg = Message(
            content=docs,
            role=self.profile,
            cause_by=type(todo)
        )

        return msg


# ==================== 使用示例 ====================

async def demo_custom_roles():
    """
    演示自定義角色的使用
    """
    print("="*60)
    print("自定義角色示例")
    print("="*60)

    # 創建團隊
    team = Team()

    # 添加標準角色和自定義角色
    from metagpt.roles import ProductManager, Engineer

    team.hire([
        ProductManager(),      # 標準角色
        Engineer(),           # 標準角色
        CodeReviewer(),       # 自定義角色
        TechnicalWriter()     # 自定義角色
    ])

    print("\n團隊成員:")
    for role in [ProductManager(), Engineer(), CodeReviewer(), TechnicalWriter()]:
        print(f"  • {role.name} - {role.profile}")

    # 定義項目需求
    requirement = """
    創建一個簡單的 Python 模組，用於處理 JSON 數據:
    - 讀取 JSON 文件
    - 驗證 JSON 結構
    - 轉換和過濾數據
    - 保存處理後的數據

    要求:
    - 代碼質量高
    - 包含錯誤處理
    - 提供完整文檔
    """

    print("\n項目需求:")
    print(requirement)

    # 設置預算
    team.invest(investment=3.0)

    # 運行項目
    print("\n開始項目開發（包含自定義角色）...")
    team.run_project(requirement)

    # 注意: 實際運行會調用 LLM API
    # await team.run(n_round=4)

    print("\n提示: 取消上面代碼的註釋以實際運行")
    print("="*60)


async def demo_custom_action():
    """
    演示單獨使用自定義 Action
    """
    print("\n" + "="*60)
    print("自定義 Action 示例")
    print("="*60)

    # 創建 Action 實例
    reviewer = WriteCodeReview()

    # 示例代碼
    sample_code = """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total = total + num
    return total
    """

    print("\n要審查的代碼:")
    print(sample_code)

    # 執行審查
    print("\n執行代碼審查...")
    # review = await reviewer.run(sample_code)
    # print("\n審查結果:")
    # print(review)

    print("\n提示: 取消註釋以實際運行代碼審查")
    print("="*60)


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 錯誤: 未檢測到 OPENAI_API_KEY")
        print("請在 .env 文件中設置 API 密鑰")
    else:
        print("✓ API 密鑰已配置\n")

        # 運行示例
        # asyncio.run(demo_custom_roles())
        # asyncio.run(demo_custom_action())

        print("提示: 取消主函數中的註釋以運行示例")
        print("⚠️  運行會調用 OpenAI API 並產生費用")
