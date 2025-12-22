"""
Hub 整合 - 分享和使用社區工具
============================

Hugging Face Hub 是 AI 社區的中心！
smolagents 與 Hub 深度整合。

本範例展示：
1. 上傳工具到 Hub
2. 從 Hub 載入工具
3. 版本管理
4. 搜索和發現工具
5. 私有工具倉庫
"""

from smolagents import tool, CodeAgent, HfApiModel
import os


# ============================================================================
# 範例 1: 創建可分享的工具
# ============================================================================

@tool
def taiwan_weather(city: str) -> dict:
    """
    獲取台灣城市天氣（示例工具）

    Args:
        city: 城市名稱（台北、台中、台南、高雄等）

    Returns:
        天氣信息字典
    """
    # 模擬天氣數據
    weather_data = {
        "台北": {"temp": 28, "condition": "多雲", "humidity": 75},
        "台中": {"temp": 30, "condition": "晴天", "humidity": 65},
        "台南": {"temp": 31, "condition": "晴天", "humidity": 70},
        "高雄": {"temp": 32, "condition": "多雲", "humidity": 80},
    }

    result = weather_data.get(city, {"temp": 25, "condition": "未知", "humidity": 60})
    result["city"] = city

    return result


def example_1_create_shareable_tool():
    """創建可分享的工具"""
    print("\n" + "="*70)
    print("範例 1: 創建可分享的工具")
    print("="*70)

    print("\n創建優質工具的要點：")
    print("1. 清晰的文檔字符串")
    print("2. 完整的類型註解")
    print("3. 良好的錯誤處理")
    print("4. 實用的功能")
    print("5. 示例用法")

    print("\n示例工具：taiwan_weather")
    print(taiwan_weather.__doc__)

    # 測試工具
    result = taiwan_weather("台北")
    print(f"\n測試結果: {result}")


# ============================================================================
# 範例 2: 上傳工具到 Hub
# ============================================================================

def example_2_push_to_hub():
    """上傳工具到 Hugging Face Hub"""
    print("\n" + "="*70)
    print("範例 2: 上傳工具到 Hub")
    print("="*70)

    print("\n上傳步驟：\n")

    print("1. 登入 Hugging Face")
    print("   方法 1: huggingface-cli login")
    print("   方法 2: 設置 HF_TOKEN 環境變數\n")

    print("2. 上傳工具")
    print("   ```python")
    print("   from smolagents import push_to_hub")
    print("")
    print("   push_to_hub(")
    print("       tool=taiwan_weather,")
    print("       repo_id='username/taiwan-weather-tool',")
    print("       commit_message='初始版本',")
    print("       private=False  # 公開分享")
    print("   )")
    print("   ```")

    print("\n3. 工具將被上傳到：")
    print("   https://huggingface.co/username/taiwan-weather-tool")

    # 檢查是否已登入
    if os.getenv("HF_TOKEN"):
        print("\n✓ 檢測到 HF_TOKEN，可以上傳工具")
        print("  （本範例不會實際上傳）")
    else:
        print("\n提示：設置 HF_TOKEN 以啟用上傳功能")
        print("  export HF_TOKEN='your-token'")


# ============================================================================
# 範例 3: 從 Hub 載入工具
# ============================================================================

def example_3_load_from_hub():
    """從 Hub 載入工具"""
    print("\n" + "="*70)
    print("範例 3: 從 Hub 載入工具")
    print("="*70)

    print("\n載入工具非常簡單：\n")

    print("```python")
    print("from smolagents import load_tool")
    print("")
    print("# 載入社區工具")
    print("weather_tool = load_tool('username/taiwan-weather-tool')")
    print("")
    print("# 直接使用")
    print("result = weather_tool('台北')")
    print("print(result)")
    print("```")

    print("\n載入時的選項：")
    print("  - 指定版本：load_tool('repo@v1.0.0')")
    print("  - 私有倉庫：需要登入和權限")
    print("  - 本地緩存：自動緩存以加快載入")

    print("\n在 Agent 中使用：")
    print("```python")
    print("from smolagents import CodeAgent, load_tool")
    print("")
    print("# 載入多個社區工具")
    print("tools = [")
    print("    load_tool('user1/weather-tool'),")
    print("    load_tool('user2/stock-tool'),")
    print("    load_tool('user3/news-tool'),")
    print("]")
    print("")
    print("agent = CodeAgent(tools=tools, model=model)")
    print("```")


# ============================================================================
# 範例 4: 搜索和發現工具
# ============================================================================

def example_4_discover_tools():
    """搜索和發現 Hub 上的工具"""
    print("\n" + "="*70)
    print("範例 4: 搜索和發現工具")
    print("="*70)

    print("\n發現工具的方法：\n")

    print("1. Hub 網站搜索")
    print("   https://huggingface.co/models?library=smolagents")

    print("\n2. 使用 API 搜索")
    print("   ```python")
    print("   from huggingface_hub import HfApi")
    print("")
    print("   api = HfApi()")
    print("   tools = api.list_models(")
    print("       filter='smolagents',")
    print("       sort='downloads',")
    print("       direction=-1")
    print("   )")
    print("")
    print("   for tool in tools[:10]:")
    print("       print(f'{tool.modelId} - {tool.downloads} downloads')")
    print("   ```")

    print("\n3. 按類別瀏覽")
    print("   - 數據處理")
    print("   - API 集成")
    print("   - 多模態工具")
    print("   - 專業領域工具")

    print("\n4. 社區推薦")
    print("   - 查看熱門工具")
    print("   - 閱讀評論和評分")
    print("   - 檢查更新頻率")


# ============================================================================
# 範例 5: 版本管理
# ============================================================================

def example_5_version_management():
    """工具版本管理"""
    print("\n" + "="*70)
    print("範例 5: 版本管理")
    print("="*70)

    print("\nHub 提供完整的版本控制：\n")

    print("1. 創建新版本")
    print("   ```python")
    print("   push_to_hub(")
    print("       tool=taiwan_weather,")
    print("       repo_id='username/taiwan-weather-tool',")
    print("       commit_message='v1.1.0: 添加濕度信息',")
    print("       create_pr=False")
    print("   )")
    print("   ```")

    print("\n2. 使用特定版本")
    print("   ```python")
    print("   # 載入特定提交")
    print("   tool_v1 = load_tool('username/tool@abc123')")
    print("")
    print("   # 載入特定分支")
    print("   tool_dev = load_tool('username/tool@dev')")
    print("   ```")

    print("\n3. 版本標記最佳實踐")
    print("   - 使用語義化版本：v1.0.0, v1.1.0, v2.0.0")
    print("   - 主版本：不兼容的 API 更改")
    print("   - 次版本：新功能，向後兼容")
    print("   - 修訂版本：bug 修復")

    print("\n4. 變更日誌")
    print("   在 README.md 中維護變更日誌")
    print("   記錄每個版本的更新內容")


# ============================================================================
# 範例 6: 私有工具倉庫
# ============================================================================

def example_6_private_tools():
    """私有工具倉庫"""
    print("\n" + "="*70)
    print("範例 6: 私有工具倉庫")
    print("="*70)

    print("\n企業和團隊可以使用私有倉庫：\n")

    print("1. 創建私有工具")
    print("   ```python")
    print("   push_to_hub(")
    print("       tool=proprietary_tool,")
    print("       repo_id='company/internal-tool',")
    print("       private=True  # 私有倉庫")
    print("   )")
    print("   ```")

    print("\n2. 團隊訪問")
    print("   - 添加團隊成員到組織")
    print("   - 設置訪問權限")
    print("   - 使用組織命名空間")

    print("\n3. 載入私有工具")
    print("   ```python")
    print("   # 需要登入並有權限")
    print("   tool = load_tool('company/internal-tool')")
    print("   ```")

    print("\n4. 使用場景")
    print("   - 專有算法")
    print("   - 內部 API 集成")
    print("   - 敏感數據處理")
    print("   - 企業工作流程")


# ============================================================================
# 範例 7: Hub 最佳實踐
# ============================================================================

def example_7_hub_best_practices():
    """Hub 使用最佳實踐"""
    print("\n" + "="*70)
    print("範例 7: Hub 最佳實踐")
    print("="*70)

    print("\n1. 完整的文檔")
    print("   README.md 應包含：")
    print("   - 工具描述")
    print("   - 安裝說明")
    print("   - 使用示例")
    print("   - API 參考")
    print("   - 限制和注意事項")

    print("\n2. 清晰的命名")
    print("   - 使用描述性名稱")
    print("   - 遵循命名約定")
    print("   - 避免過於通用的名稱")

    print("\n3. 標籤和元數據")
    print("   - 添加相關標籤")
    print("   - 設置正確的庫標記")
    print("   - 提供示例代碼")

    print("\n4. 維護和更新")
    print("   - 定期更新工具")
    print("   - 回應社區反饋")
    print("   - 修復報告的問題")

    print("\n5. 測試")
    print("   - 提供測試用例")
    print("   - 確保跨版本兼容")
    print("   - 文檔與代碼同步")

    print("\n6. 許可證")
    print("   - 明確指定許可證")
    print("   - 常用：MIT, Apache 2.0")
    print("   - 考慮使用限制")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*70)
    print("Hub 整合 - 分享和使用社區工具")
    print("="*70)

    examples = [
        ("範例 1: 創建可分享的工具", example_1_create_shareable_tool),
        ("範例 2: 上傳到 Hub", example_2_push_to_hub),
        ("範例 3: 從 Hub 載入", example_3_load_from_hub),
        ("範例 4: 搜索和發現", example_4_discover_tools),
        ("範例 5: 版本管理", example_5_version_management),
        ("範例 6: 私有工具", example_6_private_tools),
        ("範例 7: 最佳實踐", example_7_hub_best_practices),
    ]

    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n{name} 執行失敗: {e}")

    print("\n" + "="*70)
    print("Hub 整合完成！")
    print("="*70)

    print("\n關鍵要點：")
    print("  - Hub 是分享工具的最佳平台")
    print("  - 一行代碼載入社區工具")
    print("  - 完整的版本控制")
    print("  - 支持私有倉庫")
    print("  - 強大的社區生態")

    print("\n下一步: 查看 08_多Agent系統.py 學習多 Agent 協作")


if __name__ == "__main__":
    main()
