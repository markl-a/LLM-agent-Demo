"""
簡單的任務管理器示例
展示如何使用 MetaGPT 生成一個簡單的 CLI 應用

運行方式:
    python examples/simple_task_manager.py

注意: 需要設置 OPENAI_API_KEY 環境變數
成本: 約 1-2 美元
"""

import asyncio
import os
from dotenv import load_dotenv

# 加載環境變數
load_dotenv()

async def main():
    """
    使用 MetaGPT 創建任務管理器
    """
    try:
        from metagpt.team import Team

        print("="*60)
        print("MetaGPT 示例：創建任務管理器")
        print("="*60)

        # 定義需求
        requirement = """
        創建一個命令行任務管理工具（Task Manager CLI）:

        核心功能:
        1. 添加任務 - add <title> <description>
        2. 列出任務 - list [--status pending|completed]
        3. 完成任務 - complete <task_id>
        4. 刪除任務 - delete <task_id>

        技術要求:
        - Python 3.8+
        - 使用 argparse 處理命令行參數
        - 使用 JSON 文件存儲數據 (tasks.json)
        - 代碼結構清晰，易於維護
        - 包含錯誤處理

        數據結構:
        - 每個任務包含: id, title, description, status, created_at
        - status 可以是: pending 或 completed

        示例用法:
        $ python task_manager.py add "學習 Python" "完成 Python 基礎教程"
        $ python task_manager.py list
        $ python task_manager.py complete 1
        """

        print("\n項目需求:")
        print(requirement)
        print("\n" + "="*60)

        # 創建團隊
        team = Team()

        # 設置預算（控制成本）
        print("\n設置項目預算: 2.0 美元")
        team.invest(investment=2.0)

        # 運行項目
        print("\n開始項目開發...")
        print("階段 1: 產品經理分析需求...")
        print("階段 2: 架構師設計系統...")
        print("階段 3: 工程師編寫代碼...")

        team.run_project(requirement)

        # 執行開發
        await team.run(n_round=4)

        print("\n" + "="*60)
        print("✓ 項目開發完成！")
        print(f"✓ 生成的文件保存在: {team.env.workspace.path}")
        print("="*60)

    except ImportError:
        print("❌ 錯誤: MetaGPT 未安裝")
        print("請運行: pip install metagpt")
        return
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        return

if __name__ == "__main__":
    # 檢查 API 密鑰
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 錯誤: 未檢測到 OPENAI_API_KEY")
        print("請在 .env 文件中設置: OPENAI_API_KEY=your-api-key")
    else:
        print("✓ API 密鑰已配置")
        print("\n⚠️  警告: 此操作會調用 OpenAI API 並產生費用（約 1-2 美元）")
        print("確認要繼續嗎? (yes/no): ")

        # 在實際使用中應該等待用戶輸入
        # 這裡為了示例，直接註釋掉執行部分
        print("\n提示: 請手動運行此腳本並確認繼續")

        # 取消下面的註釋以實際運行
        # asyncio.run(main())
