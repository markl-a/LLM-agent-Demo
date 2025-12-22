"""
LangChain 工具整合
==================

smolagents 與 LangChain 生態系統兼容！
可以直接使用 LangChain 的豐富工具庫。

本範例展示：
1. 使用 LangChain 工具
2. 轉換 LangChain 工具
3. 混合使用兩個生態
4. 常用 LangChain 工具
5. 最佳實踐
"""

from smolagents import CodeAgent, HfApiModel, tool


# ============================================================================
# 範例 1: 為什麼要整合 LangChain
# ============================================================================

def example_1_why_langchain():
    """為什麼要整合 LangChain"""
    print("\n" + "="*70)
    print("範例 1: 為什麼要整合 LangChain")
    print("="*70)

    print("\nLangChain 生態系統的優勢：")
    print("  ✓ 豐富的工具庫（100+ 工具）")
    print("  ✓ 成熟的社區")
    print("  ✓ 大量的集成")
    print("  ✓ 持續更新")

    print("\nLangChain 工具類別：")
    print("  - API 集成（Google、Wikipedia、Wolfram Alpha）")
    print("  - 數據庫（SQL、MongoDB、Redis）")
    print("  - 搜索引擎（Google、Bing、DuckDuckGo）")
    print("  - 文件處理（PDF、Word、Excel）")
    print("  - 瀏覽器自動化（Selenium）")
    print("  - 計算工具（Python REPL、Calculator）")

    print("\nsmolagents + LangChain = 最佳組合：")
    print("  - smolagents 的極簡和強大")
    print("  - LangChain 的豐富工具生態")


# ============================================================================
# 範例 2: 使用 LangChain 工具
# ============================================================================

def example_2_using_langchain_tools():
    """使用 LangChain 工具"""
    print("\n" + "="*70)
    print("範例 2: 使用 LangChain 工具")
    print("="*70)

    print("\n安裝 LangChain：")
    print("  pip install smolagents[langchain]")
    print("  pip install langchain-community")

    print("\n使用 LangChain 工具：")
    print("```python")
    print("from smolagents import CodeAgent, HfApiModel")
    print("from smolagents.langchain import from_langchain")
    print("from langchain_community.tools import WikipediaQueryRun")
    print("from langchain_community.utilities import WikipediaAPIWrapper")
    print("")
    print("# 創建 LangChain 工具")
    print("wikipedia = WikipediaQueryRun(")
    print("    api_wrapper=WikipediaAPIWrapper()")
    print(")")
    print("")
    print("# 轉換為 smolagents 工具")
    print("wiki_tool = from_langchain(wikipedia)")
    print("")
    print("# 在 Agent 中使用")
    print("agent = CodeAgent(")
    print("    tools=[wiki_tool],")
    print("    model=HfApiModel()")
    print(")")
    print("")
    print("result = agent.run('搜索維基百科：人工智能')")
    print("```")

    print("\n就這麼簡單！LangChain 工具可以直接使用。")


# ============================================================================
# 範例 3: 常用 LangChain 工具示例
# ============================================================================

def example_3_common_langchain_tools():
    """常用 LangChain 工具"""
    print("\n" + "="*70)
    print("範例 3: 常用 LangChain 工具")
    print("="*70)

    tools_examples = [
        {
            "工具": "WikipediaQueryRun",
            "用途": "搜索維基百科",
            "代碼": """
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
wiki_tool = from_langchain(wiki)
"""
        },
        {
            "工具": "DuckDuckGoSearchRun",
            "用途": "網頁搜索",
            "代碼": """
from langchain_community.tools import DuckDuckGoSearchRun

search = DuckDuckGoSearchRun()
search_tool = from_langchain(search)
"""
        },
        {
            "工具": "PythonREPLTool",
            "用途": "執行 Python 代碼",
            "代碼": """
from langchain.tools import PythonREPLTool

python_repl = PythonREPLTool()
repl_tool = from_langchain(python_repl)
"""
        },
        {
            "工具": "RequestsGetTool",
            "用途": "HTTP GET 請求",
            "代碼": """
from langchain_community.tools import RequestsGetTool

requests_tool = RequestsGetTool()
get_tool = from_langchain(requests_tool)
"""
        },
        {
            "工具": "SQLDatabaseToolkit",
            "用途": "SQL 數據庫查詢",
            "代碼": """
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri("sqlite:///example.db")
toolkit = SQLDatabaseToolkit(db=db)
sql_tools = [from_langchain(tool) for tool in toolkit.get_tools()]
"""
        },
    ]

    for example in tools_examples:
        print(f"\n{example['工具']}")
        print(f"用途: {example['用途']}")
        print(f"示例代碼:{example['代碼']}")


# ============================================================================
# 範例 4: 混合使用 smolagents 和 LangChain 工具
# ============================================================================

def example_4_mixed_tools():
    """混合使用兩個生態的工具"""
    print("\n" + "="*70)
    print("範例 4: 混合使用工具")
    print("="*70)

    print("\n可以同時使用兩個生態的工具：\n")

    # 自定義 smolagents 工具
    @tool
    def custom_calculator(expression: str) -> float:
        """
        自定義計算器（smolagents 工具）

        Args:
            expression: 數學表達式

        Returns:
            計算結果
        """
        try:
            return eval(expression, {"__builtins__": {}}, {})
        except:
            return 0.0

    print("示例：混合工具集")
    print("```python")
    print("from smolagents import CodeAgent, tool")
    print("from smolagents.langchain import from_langchain")
    print("from langchain_community.tools import WikipediaQueryRun")
    print("")
    print("# smolagents 工具")
    print("@tool")
    print("def my_tool(x: int) -> int:")
    print("    return x * 2")
    print("")
    print("# LangChain 工具")
    print("wiki = WikipediaQueryRun(...)")
    print("wiki_tool = from_langchain(wiki)")
    print("")
    print("# 混合使用")
    print("agent = CodeAgent(")
    print("    tools=[my_tool, wiki_tool],")
    print("    model=HfApiModel()")
    print(")")
    print("```")

    print("\n優勢：")
    print("  - 結合兩個生態的優點")
    print("  - 自定義工具補充 LangChain")
    print("  - 靈活選擇最適合的工具")


# ============================================================================
# 範例 5: LangChain 工具轉換細節
# ============================================================================

def example_5_conversion_details():
    """工具轉換的細節"""
    print("\n" + "="*70)
    print("範例 5: 工具轉換細節")
    print("="*70)

    print("\nfrom_langchain() 函數的作用：")
    print("  1. 解析 LangChain 工具的描述")
    print("  2. 提取參數和類型")
    print("  3. 創建兼容的包裝器")
    print("  4. 保留原始功能")

    print("\n轉換過程：")
    print("  LangChain Tool → Wrapper → smolagents Tool")

    print("\n兼容性：")
    print("  ✓ BaseTool 的所有子類")
    print("  ✓ 工具描述自動提取")
    print("  ✓ 參數模式保留")
    print("  ✓ 錯誤處理繼承")

    print("\n示例：查看轉換後的工具")
    print("```python")
    print("from langchain_community.tools import WikipediaQueryRun")
    print("from smolagents.langchain import from_langchain")
    print("")
    print("wiki = WikipediaQueryRun(...)")
    print("wiki_tool = from_langchain(wiki)")
    print("")
    print("# 查看工具信息")
    print("print(wiki_tool.name)")
    print("print(wiki_tool.description)")
    print("print(wiki_tool.inputs)")
    print("```")


# ============================================================================
# 範例 6: 實際應用示例
# ============================================================================

def example_6_real_world_example():
    """實際應用示例"""
    print("\n" + "="*70)
    print("範例 6: 實際應用示例")
    print("="*70)

    print("\n場景：創建一個研究助手")
    print("  - 使用 Wikipedia 搜索背景信息")
    print("  - 使用 DuckDuckGo 搜索最新資訊")
    print("  - 使用自定義工具整理結果\n")

    @tool
    def summarize_results(results: list) -> str:
        """
        整理研究結果（自定義工具）

        Args:
            results: 研究結果列表

        Returns:
            整理後的摘要
        """
        summary = "研究摘要：\n"
        for i, result in enumerate(results, 1):
            summary += f"{i}. {result[:100]}...\n"
        return summary

    print("完整代碼：")
    print("```python")
    print("from smolagents import CodeAgent, HfApiModel, tool")
    print("from smolagents.langchain import from_langchain")
    print("from langchain_community.tools import (")
    print("    WikipediaQueryRun,")
    print("    DuckDuckGoSearchRun")
    print(")")
    print("")
    print("# LangChain 工具")
    print("wiki = from_langchain(WikipediaQueryRun(...))")
    print("search = from_langchain(DuckDuckGoSearchRun())")
    print("")
    print("# 自定義工具")
    print("@tool")
    print("def summarize(results: list) -> str:")
    print("    # 整理結果")
    print("    pass")
    print("")
    print("# 創建研究助手")
    print("research_assistant = CodeAgent(")
    print("    tools=[wiki, search, summarize],")
    print("    model=HfApiModel()")
    print(")")
    print("")
    print("# 執行研究任務")
    print("result = research_assistant.run(")
    print("    '研究量子計算的歷史和最新進展'")
    print(")")
    print("```")


# ============================================================================
# 範例 7: 最佳實踐和注意事項
# ============================================================================

def example_7_best_practices():
    """最佳實踐"""
    print("\n" + "="*70)
    print("範例 7: 最佳實踐和注意事項")
    print("="*70)

    print("\n1. 選擇合適的工具")
    print("   - 優先使用 smolagents 原生工具")
    print("   - LangChain 補充特殊功能")
    print("   - 避免重複功能的工具")

    print("\n2. 工具數量控制")
    print("   - 不要給 Agent 太多工具")
    print("   - 5-10 個工具通常足夠")
    print("   - 太多工具會降低性能")

    print("\n3. API 密鑰管理")
    print("   - LangChain 工具可能需要 API 密鑰")
    print("   - 使用環境變數")
    print("   - 不要硬編碼密鑰")

    print("\n4. 錯誤處理")
    print("   - LangChain 工具可能有不同的錯誤")
    print("   - 添加適當的 try-except")
    print("   - 提供降級方案")

    print("\n5. 性能考慮")
    print("   - 某些 LangChain 工具較慢")
    print("   - 考慮添加緩存")
    print("   - 設置合理的超時")

    print("\n6. 文檔和測試")
    print("   - 記錄使用的 LangChain 工具")
    print("   - 測試工具集成")
    print("   - 保持依賴更新")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*70)
    print("LangChain 工具整合")
    print("="*70)

    examples = [
        ("範例 1: 為什麼整合", example_1_why_langchain),
        ("範例 2: 使用 LangChain 工具", example_2_using_langchain_tools),
        ("範例 3: 常用工具", example_3_common_langchain_tools),
        ("範例 4: 混合使用", example_4_mixed_tools),
        ("範例 5: 轉換細節", example_5_conversion_details),
        ("範例 6: 實際應用", example_6_real_world_example),
        ("範例 7: 最佳實踐", example_7_best_practices),
    ]

    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n{name} 執行失敗: {e}")

    print("\n" + "="*70)
    print("LangChain 整合完成！")
    print("="*70)

    print("\n關鍵要點：")
    print("  - smolagents 兼容 LangChain 工具")
    print("  - 使用 from_langchain() 轉換")
    print("  - 可以混合使用兩個生態")
    print("  - 100+ LangChain 工具可用")
    print("  - 最佳組合：極簡 + 豐富生態")

    print("\n下一步: 查看 10_本地模型.py 學習使用本地模型")


if __name__ == "__main__":
    main()
