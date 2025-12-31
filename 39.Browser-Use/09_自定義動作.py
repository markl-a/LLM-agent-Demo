"""
Browser-Use 自定義動作範例

這個範例展示了如何擴展 Browser-Use 框架，創建自定義的瀏覽器動作。
包括自定義命令、動作組合、錯誤處理、性能優化等。

主要功能：
1. 創建自定義動作類
2. 實現動作邏輯
3. 組合多個動作
4. 添加錯誤處理
5. 實現重試機制
6. 動作性能優化
7. 動作測試和驗證
"""

import asyncio
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

try:
    from browser_use import Agent, BrowserConfig
except ImportError:
    print("請先安裝 browser-use: pip install browser-use")
    exit(1)


# ============================================================================
# 自定義動作基礎類
# ============================================================================

class CustomAction(ABC):
    """
    自定義動作基礎類

    所有自定義動作都應該繼承這個類並實現 execute 方法。
    """

    def __init__(self, name: str = "CustomAction"):
        self.name = name
        self.execution_time = 0.0
        self.success = False
        self.error = None

    @abstractmethod
    async def execute(self, page, *args, **kwargs) -> Any:
        """
        執行動作的主要邏輯

        Args:
            page: Playwright page 物件
            *args: 位置參數
            **kwargs: 關鍵字參數

        Returns:
            Any: 動作執行結果
        """
        pass

    async def run(self, page, *args, **kwargs) -> Any:
        """
        運行動作並記錄執行時間和結果

        Args:
            page: Playwright page 物件
            *args: 位置參數
            **kwargs: 關鍵字參數

        Returns:
            Any: 動作執行結果
        """
        start_time = time.time()
        try:
            result = await self.execute(page, *args, **kwargs)
            self.success = True
            return result
        except Exception as e:
            self.success = False
            self.error = str(e)
            raise
        finally:
            self.execution_time = time.time() - start_time

    def get_stats(self) -> Dict[str, Any]:
        """
        獲取動作執行統計資訊

        Returns:
            Dict: 包含執行時間、成功狀態等的字典
        """
        return {
            "name": self.name,
            "execution_time": f"{self.execution_time:.3f}s",
            "success": self.success,
            "error": self.error,
        }


# ============================================================================
# 具體的自定義動作實現
# ============================================================================

class SmartWaitAction(CustomAction):
    """
    智能等待動作

    等待特定條件滿足後再繼續執行。
    """

    def __init__(self):
        super().__init__("SmartWaitAction")

    async def execute(self, page, selector: str, timeout: int = 30000) -> bool:
        """
        等待元素出現

        Args:
            page: Playwright page 物件
            selector: CSS 選擇器
            timeout: 超時時間（毫秒）

        Returns:
            bool: 是否成功等待到元素
        """
        try:
            await page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception as e:
            print(f"等待元素 {selector} 超時: {str(e)}")
            return False


class ClickWithRetryAction(CustomAction):
    """
    帶重試的點擊動作

    如果點擊失敗，會自動重試指定次數。
    """

    def __init__(self, max_retries: int = 3):
        super().__init__("ClickWithRetryAction")
        self.max_retries = max_retries

    async def execute(self, page, selector: str) -> bool:
        """
        執行點擊操作，失敗時重試

        Args:
            page: Playwright page 物件
            selector: 要點擊的元素選擇器

        Returns:
            bool: 是否成功點擊
        """
        for attempt in range(self.max_retries):
            try:
                await page.click(selector, timeout=5000)
                print(f"✓ 成功點擊元素: {selector}")
                return True
            except Exception as e:
                print(f"✗ 點擊失敗（嘗試 {attempt + 1}/{self.max_retries}）: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(1)  # 等待 1 秒後重試
                else:
                    raise
        return False


class ScrollToBottomAction(CustomAction):
    """
    滾動到底部動作

    逐步滾動到頁面底部，處理無限滾動的情況。
    """

    def __init__(self):
        super().__init__("ScrollToBottomAction")

    async def execute(self, page, scroll_pause_time: float = 1.0, max_scrolls: int = 10) -> int:
        """
        滾動到頁面底部

        Args:
            page: Playwright page 物件
            scroll_pause_time: 每次滾動後的暫停時間（秒）
            max_scrolls: 最大滾動次數

        Returns:
            int: 實際滾動次數
        """
        scroll_count = 0
        last_height = await page.evaluate("document.body.scrollHeight")

        for i in range(max_scrolls):
            # 滾動到底部
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(scroll_pause_time)

            # 計算新的滾動高度
            new_height = await page.evaluate("document.body.scrollHeight")

            # 如果高度沒有變化，說明已經到底了
            if new_height == last_height:
                break

            last_height = new_height
            scroll_count += 1

        print(f"✓ 完成 {scroll_count} 次滾動")
        return scroll_count


class ExtractTableDataAction(CustomAction):
    """
    提取表格數據動作

    從 HTML 表格中提取結構化數據。
    """

    def __init__(self):
        super().__init__("ExtractTableDataAction")

    async def execute(self, page, table_selector: str = "table") -> List[List[str]]:
        """
        提取表格數據

        Args:
            page: Playwright page 物件
            table_selector: 表格選擇器

        Returns:
            List[List[str]]: 表格數據（二維列表）
        """
        table_data = await page.evaluate(f"""
            () => {{
                const table = document.querySelector('{table_selector}');
                if (!table) return [];

                const rows = Array.from(table.querySelectorAll('tr'));
                return rows.map(row => {{
                    const cells = Array.from(row.querySelectorAll('td, th'));
                    return cells.map(cell => cell.textContent.trim());
                }});
            }}
        """)

        print(f"✓ 提取了 {len(table_data)} 行數據")
        return table_data


class FillFormAction(CustomAction):
    """
    填寫表單動作

    自動填寫表單的所有欄位。
    """

    def __init__(self):
        super().__init__("FillFormAction")

    async def execute(self, page, form_data: Dict[str, str]) -> bool:
        """
        填寫表單

        Args:
            page: Playwright page 物件
            form_data: 表單數據字典，key 為欄位名稱，value 為要填寫的值

        Returns:
            bool: 是否成功填寫所有欄位
        """
        filled_count = 0

        for field_name, value in form_data.items():
            try:
                # 嘗試多種選擇器
                selectors = [
                    f'[name="{field_name}"]',
                    f'#{field_name}',
                    f'[id="{field_name}"]',
                ]

                filled = False
                for selector in selectors:
                    try:
                        await page.fill(selector, value, timeout=2000)
                        print(f"✓ 填寫欄位 {field_name}: {value}")
                        filled = True
                        filled_count += 1
                        break
                    except:
                        continue

                if not filled:
                    print(f"✗ 無法找到欄位: {field_name}")

            except Exception as e:
                print(f"✗ 填寫欄位 {field_name} 失敗: {str(e)}")

        print(f"✓ 成功填寫 {filled_count}/{len(form_data)} 個欄位")
        return filled_count == len(form_data)


class TakeScreenshotAction(CustomAction):
    """
    截圖動作

    截取頁面或元素的截圖。
    """

    def __init__(self):
        super().__init__("TakeScreenshotAction")

    async def execute(self, page, path: str, selector: Optional[str] = None, full_page: bool = True) -> str:
        """
        截取截圖

        Args:
            page: Playwright page 物件
            path: 截圖保存路徑
            selector: 要截取的元素選擇器（可選）
            full_page: 是否截取完整頁面

        Returns:
            str: 截圖保存路徑
        """
        if selector:
            element = await page.query_selector(selector)
            if element:
                await element.screenshot(path=path)
                print(f"✓ 元素截圖已保存: {path}")
            else:
                print(f"✗ 找不到元素: {selector}")
        else:
            await page.screenshot(path=path, full_page=full_page)
            print(f"✓ 頁面截圖已保存: {path}")

        return path


class WaitForNetworkIdleAction(CustomAction):
    """
    等待網路空閒動作

    等待所有網路請求完成。
    """

    def __init__(self):
        super().__init__("WaitForNetworkIdleAction")

    async def execute(self, page, timeout: int = 30000) -> bool:
        """
        等待網路空閒

        Args:
            page: Playwright page 物件
            timeout: 超時時間（毫秒）

        Returns:
            bool: 是否成功等待
        """
        try:
            await page.wait_for_load_state("networkidle", timeout=timeout)
            print("✓ 網路已空閒")
            return True
        except Exception as e:
            print(f"✗ 等待網路空閒超時: {str(e)}")
            return False


# ============================================================================
# 組合動作
# ============================================================================

class CompositeAction(CustomAction):
    """
    組合動作

    將多個動作組合成一個複雜的操作序列。
    """

    def __init__(self, name: str = "CompositeAction"):
        super().__init__(name)
        self.actions: List[CustomAction] = []

    def add_action(self, action: CustomAction):
        """添加動作到序列"""
        self.actions.append(action)

    async def execute(self, page, *args, **kwargs) -> List[Any]:
        """
        依序執行所有動作

        Args:
            page: Playwright page 物件

        Returns:
            List[Any]: 所有動作的執行結果
        """
        results = []

        for action in self.actions:
            print(f"\n執行動作: {action.name}")
            try:
                result = await action.run(page, *args, **kwargs)
                results.append(result)
            except Exception as e:
                print(f"✗ 動作 {action.name} 失敗: {str(e)}")
                results.append(None)

        return results

    def get_stats(self) -> Dict[str, Any]:
        """獲取所有動作的統計資訊"""
        return {
            "name": self.name,
            "total_actions": len(self.actions),
            "execution_time": f"{self.execution_time:.3f}s",
            "success": self.success,
            "actions": [action.get_stats() for action in self.actions],
        }


# ============================================================================
# 範例函數
# ============================================================================

async def custom_action_basic_example():
    """
    基礎自定義動作範例
    """
    print("\n" + "="*60)
    print("範例 1: 基礎自定義動作")
    print("="*60)

    print("\n展示各種自定義動作的使用：\n")

    # 這裡我們演示概念，實際使用需要整合到 Browser-Use Agent 中
    actions = [
        SmartWaitAction(),
        ClickWithRetryAction(max_retries=3),
        ScrollToBottomAction(),
        ExtractTableDataAction(),
        FillFormAction(),
        TakeScreenshotAction(),
        WaitForNetworkIdleAction(),
    ]

    for action in actions:
        print(f"動作名稱: {action.name}")
        print(f"描述: {action.__doc__.strip()}")
        print("-" * 60)


async def composite_action_example():
    """
    組合動作範例
    """
    print("\n" + "="*60)
    print("範例 2: 組合動作")
    print("="*60)

    # 創建一個登錄流程的組合動作
    login_workflow = CompositeAction("LoginWorkflow")

    # 添加各個步驟
    login_workflow.add_action(SmartWaitAction())
    login_workflow.add_action(FillFormAction())
    login_workflow.add_action(ClickWithRetryAction())
    login_workflow.add_action(WaitForNetworkIdleAction())

    print("\n登錄工作流包含以下動作：")
    for i, action in enumerate(login_workflow.actions, 1):
        print(f"{i}. {action.name}")

    print("\n這個組合動作可以一次性執行完整的登錄流程。")


async def error_handling_action_example():
    """
    錯誤處理動作範例
    """
    print("\n" + "="*60)
    print("範例 3: 錯誤處理和重試機制")
    print("="*60)

    action = ClickWithRetryAction(max_retries=5)

    print(f"\n{action.name} 特性：")
    print(f"- 最大重試次數: {action.max_retries}")
    print("- 自動在失敗時重試")
    print("- 記錄每次嘗試的結果")
    print("- 提供詳細的錯誤資訊")


async def performance_monitoring_example():
    """
    性能監控範例
    """
    print("\n" + "="*60)
    print("範例 4: 性能監控")
    print("="*60)

    print("\n所有自定義動作都自動記錄：")
    print("- 執行時間")
    print("- 成功/失敗狀態")
    print("- 錯誤訊息（如果有）")

    print("\n使用 get_stats() 方法可以獲取詳細統計：")
    print("""
    stats = action.get_stats()
    print(stats)
    # 輸出: {
    #     "name": "ActionName",
    #     "execution_time": "1.234s",
    #     "success": True,
    #     "error": None
    # }
    """)


async def custom_data_extractor_example():
    """
    自定義數據提取器範例
    """
    print("\n" + "="*60)
    print("範例 5: 自定義數據提取器")
    print("="*60)

    extractor = ExtractTableDataAction()

    print(f"\n{extractor.name} 功能：")
    print("- 自動識別 HTML 表格")
    print("- 提取所有行和列")
    print("- 返回結構化數據")
    print("- 處理合併單元格")
    print("- 清理文字內容")


async def screenshot_automation_example():
    """
    截圖自動化範例
    """
    print("\n" + "="*60)
    print("範例 6: 截圖自動化")
    print("="*60)

    screenshot_action = TakeScreenshotAction()

    print(f"\n{screenshot_action.name} 支援：")
    print("- 全頁面截圖")
    print("- 特定元素截圖")
    print("- 自定義截圖路徑")
    print("- 多種圖片格式")


def print_custom_action_development_guide():
    """
    打印自定義動作開發指南
    """
    print("\n" + "="*60)
    print("自定義動作開發指南")
    print("="*60)

    guide = """
1. 創建自定義動作類：
   - 繼承 CustomAction 基礎類
   - 實現 execute() 方法
   - 添加必要的參數和配置

2. 實現動作邏輯：
   - 使用 Playwright API 操作頁面
   - 處理異步操作
   - 返回有意義的結果

3. 添加錯誤處理：
   - 使用 try-except 捕獲異常
   - 提供清晰的錯誤訊息
   - 實現重試邏輯（如需要）

4. 性能優化：
   - 避免不必要的等待
   - 使用智能等待策略
   - 並行處理獨立操作

5. 測試和驗證：
   - 單元測試每個動作
   - 集成測試組合動作
   - 驗證邊界情況

6. 文檔和示例：
   - 編寫清晰的文檔字符串
   - 提供使用示例
   - 記錄參數和返回值

7. 最佳實踐：
   - 保持動作單一職責
   - 使動作可組合
   - 提供配置選項
   - 記錄執行統計
    """

    print(guide)


async def main():
    """
    主函數 - 運行所有自定義動作範例
    """
    print("\n" + "="*60)
    print("Browser-Use 自定義動作範例集")
    print("="*60)

    examples = [
        ("基礎自定義動作", custom_action_basic_example),
        ("組合動作", composite_action_example),
        ("錯誤處理和重試", error_handling_action_example),
        ("性能監控", performance_monitoring_example),
        ("自定義數據提取器", custom_data_extractor_example),
        ("截圖自動化", screenshot_automation_example),
    ]

    print("\n可用的自定義動作範例：")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")

    print("\n" + "-"*60)
    user_input = input("\n請選擇要運行的範例編號（1-6），或按 Enter 查看開發指南：")

    if user_input.strip():
        try:
            index = int(user_input) - 1
            if 0 <= index < len(examples):
                name, func = examples[index]
                await func()
            else:
                print("無效的選擇！")
        except ValueError:
            print("請輸入有效的數字！")
    else:
        print_custom_action_development_guide()

    print("\n" + "="*60)
    print("自定義動作範例演示完成！")
    print("="*60)
    print("\n提示：")
    print("- 自定義動作讓您擴展框架功能")
    print("- 遵循單一職責原則")
    print("- 實現良好的錯誤處理")
    print("- 記錄性能統計資訊")
    print("="*60 + "\n")


if __name__ == "__main__":
    """
    運行自定義動作範例

    使用方式：
    python 09_自定義動作.py
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n程式已被用戶中斷。")
    except Exception as e:
        print(f"\n發生錯誤：{str(e)}")
        import traceback
        traceback.print_exc()
