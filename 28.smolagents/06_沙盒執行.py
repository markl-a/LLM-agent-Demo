"""
沙盒執行 - 安全的代碼執行環境
============================

Code Agent 生成並執行代碼，安全性至關重要！
smolagents 支持多種沙盒環境。

本範例展示：
1. 為什麼需要沙盒
2. E2B 雲端沙盒
3. Docker 容器沙盒
4. Local 沙盒（開發用）
5. 自定義沙盒執行器
"""

from smolagents import CodeAgent, HfApiModel, tool
import os


# ============================================================================
# 範例 1: 為什麼需要沙盒
# ============================================================================

def example_1_why_sandbox():
    """解釋沙盒的重要性"""
    print("\n" + "="*70)
    print("範例 1: 為什麼需要沙盒")
    print("="*70)

    print("\nCode Agent 生成的代碼可能：")
    print("❌ 訪問敏感文件")
    print("❌ 修改系統配置")
    print("❌ 刪除重要數據")
    print("❌ 發起網絡攻擊")
    print("❌ 消耗大量資源")

    print("\n沙盒環境提供：")
    print("✓ 隔離的執行環境")
    print("✓ 資源限制（CPU、內存、網絡）")
    print("✓ 文件系統隔離")
    print("✓ 超時保護")
    print("✓ 安全的包管理")

    print("\n危險代碼示例：")
    print("```python")
    print("# 不在沙盒中可能造成嚴重後果！")
    print("import os")
    print("os.system('rm -rf /')  # 刪除所有文件")
    print("```")

    print("\n在沙盒中：")
    print("✓ 代碼在隔離環境中執行")
    print("✓ 無法訪問主機文件系統")
    print("✓ 資源使用受限")
    print("✓ 執行超時自動終止")


# ============================================================================
# 範例 2: Local Executor（開發用）
# ============================================================================

def example_2_local_executor():
    """本地執行器 - 僅用於開發"""
    print("\n" + "="*70)
    print("範例 2: Local Executor（開發用）")
    print("="*70)

    print("\n⚠️  警告：LocalExecutor 不提供隔離！")
    print("只在開發和測試環境中使用。\n")

    @tool
    def safe_calculation(a: int, b: int) -> int:
        """安全的計算工具"""
        return a + b

    model = HfApiModel()

    # 默認使用 LocalExecutor
    agent = CodeAgent(
        tools=[safe_calculation],
        model=model,
        max_steps=5
    )

    print("LocalExecutor 特點：")
    print("  ✓ 無需額外配置")
    print("  ✓ 快速執行")
    print("  ✓ 適合開發調試")
    print("  ✗ 沒有安全隔離")
    print("  ✗ 不適合生產環境\n")

    result = agent.run("計算 10 + 20")
    print(f"\n結果: {result}")

    print("\n使用場景：")
    print("  - 本地開發")
    print("  - 單元測試")
    print("  - 可信任的代碼")


# ============================================================================
# 範例 3: E2B 雲端沙盒（推薦）
# ============================================================================

def example_3_e2b_sandbox():
    """E2B 雲端沙盒 - 推薦用於生產"""
    print("\n" + "="*70)
    print("範例 3: E2B 雲端沙盒（推薦）")
    print("="*70)

    print("\nE2B（Execute to Build）是專業的代碼執行平台\n")

    print("安裝：")
    print("  pip install smolagents[e2b]")

    print("\n配置：")
    print("  1. 註冊 E2B：https://e2b.dev")
    print("  2. 獲取 API key")
    print("  3. 設置環境變數：export E2B_API_KEY='your-key'")

    print("\n使用示例：")
    print("```python")
    print("from smolagents import CodeAgent")
    print("from smolagents.e2b import E2BExecutor")
    print("")
    print("# 創建 E2B 執行器")
    print("executor = E2BExecutor(")
    print("    api_key=os.getenv('E2B_API_KEY'),")
    print("    timeout=300  # 5 分鐘超時")
    print(")")
    print("")
    print("# 使用 E2B 執行器的 Agent")
    print("agent = CodeAgent(")
    print("    tools=tools,")
    print("    model=model,")
    print("    executor=executor")
    print(")")
    print("```")

    print("\nE2B 特點：")
    print("  ✓ 完全隔離的雲端環境")
    print("  ✓ 自動資源管理")
    print("  ✓ 支持多種編程語言")
    print("  ✓ 持久化沙盒選項")
    print("  ✓ 適合生產環境")

    print("\n優勢：")
    print("  - 零配置")
    print("  - 高安全性")
    print("  - 可擴展")
    print("  - 有免費額度")

    # 如果有 E2B API key，展示實際使用
    if os.getenv("E2B_API_KEY"):
        print("\n檢測到 E2B_API_KEY，可以使用 E2B 執行器")
        try:
            from smolagents.e2b import E2BExecutor

            @tool
            def complex_task(n: int) -> list:
                """複雜計算任務"""
                return [i**2 for i in range(n)]

            executor = E2BExecutor()
            agent = CodeAgent(
                tools=[complex_task],
                model=HfApiModel(),
                executor=executor,
                max_steps=5
            )

            result = agent.run("計算前 10 個數字的平方")
            print(f"\n使用 E2B 執行結果: {result}")

        except ImportError:
            print("\n需要安裝: pip install smolagents[e2b]")
    else:
        print("\n未設置 E2B_API_KEY，跳過實際執行示例")


# ============================================================================
# 範例 4: Docker 沙盒
# ============================================================================

def example_4_docker_sandbox():
    """Docker 容器沙盒"""
    print("\n" + "="*70)
    print("範例 4: Docker 沙盒")
    print("="*70)

    print("\nDocker 提供本地的容器化隔離\n")

    print("前置要求：")
    print("  1. 安裝 Docker")
    print("  2. Docker daemon 運行中")

    print("\n使用示例：")
    print("```python")
    print("from smolagents import CodeAgent")
    print("from smolagents.docker import DockerExecutor")
    print("")
    print("# 創建 Docker 執行器")
    print("executor = DockerExecutor(")
    print("    image='python:3.11-slim',  # 使用的 Docker 鏡像")
    print("    timeout=300,")
    print("    memory_limit='512m',  # 內存限制")
    print("    cpu_quota=50000  # CPU 限制")
    print(")")
    print("")
    print("agent = CodeAgent(")
    print("    tools=tools,")
    print("    model=model,")
    print("    executor=executor")
    print(")")
    print("```")

    print("\nDocker 特點：")
    print("  ✓ 本地執行，無需外部服務")
    print("  ✓ 完全隔離")
    print("  ✓ 自定義環境（選擇鏡像）")
    print("  ✓ 資源限制")
    print("  ✓ 可重現的環境")

    print("\n適用場景：")
    print("  - 自託管部署")
    print("  - 需要特定環境")
    print("  - 敏感數據處理（不離開本地）")
    print("  - CI/CD 流水線")

    print("\n配置選項：")
    print("  - image: Python 鏡像版本")
    print("  - timeout: 執行超時")
    print("  - memory_limit: 內存限制")
    print("  - cpu_quota: CPU 配額")
    print("  - network: 網絡模式")


# ============================================================================
# 範例 5: 沙盒執行對比
# ============================================================================

def example_5_sandbox_comparison():
    """對比不同沙盒選項"""
    print("\n" + "="*70)
    print("範例 5: 沙盒執行器對比")
    print("="*70)

    comparison = [
        {
            "執行器": "LocalExecutor",
            "安全性": "❌ 低",
            "性能": "⚡ 最快",
            "配置": "✓ 零配置",
            "成本": "免費",
            "適用": "開發/測試"
        },
        {
            "執行器": "E2BExecutor",
            "安全性": "✓ 高",
            "性能": "🌐 取決於網絡",
            "配置": "✓ 簡單（需 API key）",
            "成本": "有免費額度",
            "適用": "生產環境"
        },
        {
            "執行器": "DockerExecutor",
            "安全性": "✓ 高",
            "性能": "⚡ 快",
            "配置": "需要 Docker",
            "成本": "免費",
            "適用": "自託管"
        },
    ]

    print("\n詳細對比：\n")
    for item in comparison:
        print(f"{item['執行器']}")
        print(f"  安全性: {item['安全性']}")
        print(f"  性能: {item['性能']}")
        print(f"  配置: {item['配置']}")
        print(f"  成本: {item['成本']}")
        print(f"  適用: {item['適用']}\n")

    print("選擇建議：")
    print("  📝 開發調試 → LocalExecutor")
    print("  🚀 生產部署 → E2BExecutor")
    print("  🏠 自託管 → DockerExecutor")
    print("  🔒 敏感數據 → DockerExecutor（本地）")


# ============================================================================
# 範例 6: 自定義執行器
# ============================================================================

def example_6_custom_executor():
    """創建自定義執行器"""
    print("\n" + "="*70)
    print("範例 6: 自定義執行器")
    print("="*70)

    print("\n可以創建自定義執行器以滿足特殊需求\n")

    print("示例：帶日誌記錄的執行器")
    print("```python")
    print("from smolagents import Executor")
    print("")
    print("class LoggingExecutor(Executor):")
    print("    def __init__(self, base_executor):")
    print("        self.base_executor = base_executor")
    print("        self.execution_log = []")
    print("")
    print("    def __call__(self, code: str) -> str:")
    print("        print(f'執行代碼: {code[:100]}...')")
    print("        ")
    print("        # 記錄執行")
    print("        self.execution_log.append({")
    print("            'code': code,")
    print("            'timestamp': time.time()")
    print("        })")
    print("        ")
    print("        # 委託給基礎執行器")
    print("        result = self.base_executor(code)")
    print("        ")
    print("        print(f'執行結果: {result[:100]}...')")
    print("        return result")
    print("```")

    print("\n自定義執行器用途：")
    print("  - 添加日誌記錄")
    print("  - 代碼審計")
    print("  - 性能監控")
    print("  - 自動重試邏輯")
    print("  - 結果緩存")


# ============================================================================
# 範例 7: 最佳實踐
# ============================================================================

def example_7_best_practices():
    """沙盒使用最佳實踐"""
    print("\n" + "="*70)
    print("範例 7: 最佳實踐")
    print("="*70)

    print("\n1. 永遠不要在生產環境使用 LocalExecutor")
    print("   ❌ 不安全")
    print("   ✓ 使用 E2B 或 Docker")

    print("\n2. 設置適當的超時")
    print("   - 簡單任務：30-60 秒")
    print("   - 複雜任務：2-5 分鐘")
    print("   - 數據處理：5-10 分鐘")

    print("\n3. 資源限制")
    print("   - 設置內存限制避免 OOM")
    print("   - 設置 CPU 配額防止佔用過高")

    print("\n4. 監控和日誌")
    print("   - 記錄所有代碼執行")
    print("   - 監控資源使用")
    print("   - 設置告警")

    print("\n5. 錯誤處理")
    print("   ```python")
    print("   try:")
    print("       result = agent.run(task)")
    print("   except TimeoutError:")
    print("       # 處理超時")
    print("   except ExecutionError:")
    print("       # 處理執行錯誤")
    print("   ```")

    print("\n6. 定期清理")
    print("   - Docker：清理停止的容器")
    print("   - E2B：監控使用配額")

    print("\n7. 安全審查")
    print("   - 審查生成的代碼")
    print("   - 限制可用的工具")
    print("   - 白名單允許的包")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*70)
    print("沙盒執行 - 安全的代碼執行環境")
    print("="*70)

    examples = [
        ("範例 1: 為什麼需要沙盒", example_1_why_sandbox),
        ("範例 2: Local Executor", example_2_local_executor),
        ("範例 3: E2B 沙盒", example_3_e2b_sandbox),
        ("範例 4: Docker 沙盒", example_4_docker_sandbox),
        ("範例 5: 沙盒對比", example_5_sandbox_comparison),
        ("範例 6: 自定義執行器", example_6_custom_executor),
        ("範例 7: 最佳實踐", example_7_best_practices),
    ]

    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n{name} 執行失敗: {e}")

    print("\n" + "="*70)
    print("沙盒執行完成！")
    print("="*70)

    print("\n關鍵要點：")
    print("  - 生產環境必須使用沙盒")
    print("  - E2B 雲端沙盒最簡單")
    print("  - Docker 適合自託管")
    print("  - LocalExecutor 僅用於開發")
    print("  - 設置超時和資源限制")

    print("\n下一步: 查看 07_Hub整合.py 學習分享和使用社區工具")


if __name__ == "__main__":
    main()
