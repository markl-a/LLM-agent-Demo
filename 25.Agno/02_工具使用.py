"""
02_工具使用.py - Agno 內建工具使用指南

本範例展示如何使用 Agno 豐富的內建工具包，包括：
- 網頁搜索工具（DuckDuckGo, Tavily）
- 計算器與數學工具
- 文件操作工具
- Python 代碼執行工具
- 自定義工具開發
- 工具組合使用策略

作者：LLM-agent-Demo Team
日期：2025-12
框架：Agno (原 Phidata)
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Agno 核心導入
from agno.agent import Agent
from agno.models.openai import OpenAIChat

# 內建工具導入
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.python import PythonTools
from agno.tools.file import FileTools
from agno.tools.shell import ShellTools
from agno.tools.calculator import CalculatorTools

# Tavily 搜索（需要 API Key）
try:
    from agno.tools.tavily import TavilyTools
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False

# 載入環境變數
load_dotenv()


# ============================================================================
# 範例 1: 使用 DuckDuckGo 網頁搜索
# ============================================================================
def example_1_web_search():
    """
    使用 DuckDuckGo 進行網頁搜索

    DuckDuckGo 工具特點：
    - 無需 API Key
    - 快速搜索
    - 隱私保護
    - 適合一般信息查詢
    """
    print("\n" + "="*80)
    print("範例 1: 使用 DuckDuckGo 網頁搜索")
    print("="*80)

    # 創建帶搜索工具的 Agent
    agent = Agent(
        name="web_researcher",
        role="網路研究專員",
        model=OpenAIChat(id="gpt-4"),

        # 添加 DuckDuckGo 搜索工具
        tools=[DuckDuckGoTools()],

        instructions=[
            "使用網頁搜索工具查找最新、準確的信息",
            "引用搜索結果來源",
            "綜合多個來源提供全面的答案"
        ],

        show_tool_calls=True,  # 顯示工具調用過程
        markdown=True
    )

    # 執行搜索任務
    queries = [
        "2024年諾貝爾物理學獎得主是誰？",
        "Agno 框架的主要特點有哪些？"
    ]

    for query in queries:
        print(f"\n查詢: {query}")
        print("-" * 80)
        response = agent.run(query)
        print(f"\n回答:\n{response.content}\n")


# ============================================================================
# 範例 2: 使用計算器工具
# ============================================================================
def example_2_calculator():
    """
    使用計算器工具進行數學計算

    支持的操作：
    - 基本算術（加減乘除）
    - 複雜數學運算
    - 統計計算
    - 單位轉換
    """
    print("\n" + "="*80)
    print("範例 2: 使用計算器工具")
    print("="*80)

    # 創建數學助手 Agent
    math_agent = Agent(
        name="math_assistant",
        role="數學計算助手",
        model=OpenAIChat(id="gpt-4"),

        # 添加計算器工具
        tools=[CalculatorTools()],

        instructions=[
            "使用計算器工具進行精確的數學計算",
            "展示計算步驟",
            "驗證結果的合理性"
        ],

        show_tool_calls=True,
        markdown=True
    )

    # 數學問題
    problems = [
        "計算 (123.45 * 67.89) + (987.65 / 4.32)",
        "如果我每月存款 5000 元，年利率 3%，複利計算，5 年後有多少錢？",
        "一個圓的半徑是 7.5 公分，計算它的面積和周長"
    ]

    for problem in problems:
        print(f"\n問題: {problem}")
        print("-" * 80)
        response = math_agent.run(problem)
        print(f"\n解答:\n{response.content}\n")


# ============================================================================
# 範例 3: 使用 Python 工具執行代碼
# ============================================================================
def example_3_python_tools():
    """
    使用 Python 工具執行代碼

    功能：
    - 執行 Python 代碼
    - 數據分析
    - 自動化腳本
    - 算法實現
    """
    print("\n" + "="*80)
    print("範例 3: 使用 Python 工具執行代碼")
    print("="*80)

    # 創建 Python 編程助手
    python_agent = Agent(
        name="python_expert",
        role="Python 編程專家",
        model=OpenAIChat(id="gpt-4"),

        # 添加 Python 工具
        tools=[PythonTools()],

        instructions=[
            "使用 Python 代碼解決問題",
            "編寫清晰、高效的代碼",
            "測試代碼並確保正確性",
            "解釋代碼的工作原理"
        ],

        show_tool_calls=True,
        markdown=True
    )

    # 編程任務
    tasks = [
        "生成斐波那契數列的前 10 個數字",
        "創建一個包含 1-20 的列表，找出所有質數",
        "計算列表 [23, 45, 12, 67, 34, 89, 15] 的平均值、中位數和標準差"
    ]

    for task in tasks:
        print(f"\n任務: {task}")
        print("-" * 80)
        response = python_agent.run(task)
        print(f"\n結果:\n{response.content}\n")


# ============================================================================
# 範例 4: 使用文件工具
# ============================================================================
def example_4_file_tools():
    """
    使用文件工具進行文件操作

    支持操作：
    - 讀取文件
    - 寫入文件
    - 列出目錄
    - 文件搜索
    """
    print("\n" + "="*80)
    print("範例 4: 使用文件工具")
    print("="*80)

    # 創建文件管理 Agent
    file_agent = Agent(
        name="file_manager",
        role="文件管理專員",
        model=OpenAIChat(id="gpt-4"),

        # 添加文件工具
        tools=[FileTools()],

        instructions=[
            "安全地執行文件操作",
            "確認操作前先檢查文件是否存在",
            "提供清晰的操作結果報告"
        ],

        show_tool_calls=True,
        markdown=True
    )

    # 測試創建和讀取文件
    print("\n任務: 創建一個測試文件並讀取內容")
    print("-" * 80)

    task = """
    請執行以下操作：
    1. 創建一個名為 'test_agno.txt' 的文件
    2. 寫入內容：'這是 Agno 框架的測試文件'
    3. 讀取文件內容並確認
    """

    response = file_agent.run(task)
    print(f"\n結果:\n{response.content}\n")


# ============================================================================
# 範例 5: 多工具組合使用
# ============================================================================
def example_5_multiple_tools():
    """
    組合使用多個工具完成複雜任務

    展示如何讓 Agent 智能選擇和組合使用多個工具
    """
    print("\n" + "="*80)
    print("範例 5: 多工具組合使用")
    print("="*80)

    # 創建全能助手 Agent
    multi_tool_agent = Agent(
        name="universal_assistant",
        role="全能智能助手",
        model=OpenAIChat(id="gpt-4"),

        # 添加多個工具
        tools=[
            DuckDuckGoTools(),   # 網頁搜索
            PythonTools(),       # Python 執行
            CalculatorTools(),   # 計算器
            FileTools()          # 文件操作
        ],

        instructions=[
            "根據任務需求智能選擇合適的工具",
            "可以組合使用多個工具完成複雜任務",
            "先搜索信息，再進行計算或分析",
            "提供詳細的執行步驟說明"
        ],

        show_tool_calls=True,
        markdown=True
    )

    # 複雜任務
    complex_tasks = [
        "搜索 Python 最新版本號，然後計算從 3.0 到最新版本經過了多少個主要版本",
        "查找台北今天的天氣，如果溫度超過 25 度，計算華氏溫度是多少"
    ]

    for task in complex_tasks:
        print(f"\n任務: {task}")
        print("-" * 80)
        response = multi_tool_agent.run(task)
        print(f"\n結果:\n{response.content}\n")


# ============================================================================
# 範例 6: 自定義工具
# ============================================================================
def example_6_custom_tool():
    """
    創建和使用自定義工具

    展示如何開發自己的工具並集成到 Agent 中
    """
    print("\n" + "="*80)
    print("範例 6: 自定義工具")
    print("="*80)

    from agno.tools import Tool
    from typing import Dict, Any

    # 定義自定義工具：文本分析器
    def analyze_text(text: str) -> Dict[str, Any]:
        """
        分析文本的基本統計信息

        參數：
            text: 要分析的文本

        返回：
            包含統計信息的字典
        """
        words = text.split()
        chars = len(text)
        chars_no_spaces = len(text.replace(" ", ""))

        return {
            "total_characters": chars,
            "characters_without_spaces": chars_no_spaces,
            "total_words": len(words),
            "average_word_length": round(chars_no_spaces / len(words), 2) if words else 0,
            "longest_word": max(words, key=len) if words else "",
            "shortest_word": min(words, key=len) if words else ""
        }

    # 創建工具對象
    text_analyzer_tool = Tool(
        name="text_analyzer",
        description="分析文本的統計信息，包括字符數、詞數等",
        func=analyze_text
    )

    # 創建使用自定義工具的 Agent
    custom_agent = Agent(
        name="text_analyst",
        role="文本分析專家",
        model=OpenAIChat(id="gpt-4"),

        # 添加自定義工具
        tools=[text_analyzer_tool],

        instructions=[
            "使用文本分析工具獲取統計信息",
            "提供詳細的分析報告",
            "給出文本優化建議"
        ],

        show_tool_calls=True,
        markdown=True
    )

    # 測試自定義工具
    sample_text = "Agno 是新一代的 AI Agent 框架，專為構建生產級的多模態 Agent 應用而設計。"

    print(f"\n分析文本: {sample_text}")
    print("-" * 80)

    response = custom_agent.run(f"請分析這段文本：{sample_text}")
    print(f"\n分析結果:\n{response.content}\n")


# ============================================================================
# 範例 7: Tavily 深度搜索（需要 API Key）
# ============================================================================
def example_7_tavily_search():
    """
    使用 Tavily 進行深度網頁搜索

    Tavily 特點：
    - AI 優化的搜索
    - 高質量結果
    - 支持深度研究
    - 需要 API Key
    """
    print("\n" + "="*80)
    print("範例 7: Tavily 深度搜索")
    print("="*80)

    if not os.getenv("TAVILY_API_KEY"):
        print("⚠️  未設置 TAVILY_API_KEY，跳過此範例")
        print("可以到 https://tavily.com 獲取免費 API Key")
        return

    if not TAVILY_AVAILABLE:
        print("⚠️  未安裝 Tavily 工具包，請執行: pip install tavily-python")
        return

    # 創建深度研究 Agent
    research_agent = Agent(
        name="deep_researcher",
        role="深度研究專員",
        model=OpenAIChat(id="gpt-4"),

        # 使用 Tavily 工具
        tools=[TavilyTools()],

        instructions=[
            "使用 Tavily 進行深入的網頁研究",
            "綜合多個高質量來源",
            "提供詳細、準確的研究報告",
            "引用權威來源"
        ],

        show_tool_calls=True,
        markdown=True
    )

    # 深度研究任務
    research_query = "Agno 框架與 LangGraph 的性能對比研究"

    print(f"\n研究主題: {research_query}")
    print("-" * 80)

    response = research_agent.run(research_query)
    print(f"\n研究報告:\n{response.content}\n")


# ============================================================================
# 範例 8: 工具調用控制
# ============================================================================
def example_8_tool_control():
    """
    展示如何控制工具的調用行為

    控制選項：
    - tool_choice: "auto" | "required" | "none"
    - max_tool_calls: 最大工具調用次數
    - tool_timeout: 工具執行超時時間
    """
    print("\n" + "="*80)
    print("範例 8: 工具調用控制")
    print("="*80)

    # 1. 自動選擇工具（預設）
    print("\n--- 模式 1: 自動選擇工具 ---")
    auto_agent = Agent(
        model=OpenAIChat(id="gpt-4"),
        tools=[DuckDuckGoTools(), CalculatorTools()],
        tool_choice="auto"  # 讓 Agent 自行決定是否使用工具
    )

    response1 = auto_agent.run("什麼是機器學習？")
    print(f"回答（可能不使用工具）: {response1.content[:100]}...\n")

    # 2. 強制使用工具
    print("--- 模式 2: 強制使用工具 ---")
    required_agent = Agent(
        model=OpenAIChat(id="gpt-4"),
        tools=[DuckDuckGoTools()],
        tool_choice="required"  # 強制使用工具
    )

    response2 = required_agent.run("什麼是機器學習？")
    print(f"回答（必定使用工具）: {response2.content[:100]}...\n")

    # 3. 禁用工具
    print("--- 模式 3: 禁用工具 ---")
    no_tool_agent = Agent(
        model=OpenAIChat(id="gpt-4"),
        tools=[DuckDuckGoTools()],  # 雖然有工具，但不使用
        tool_choice="none"  # 禁用所有工具
    )

    response3 = no_tool_agent.run("什麼是機器學習？")
    print(f"回答（不使用工具）: {response3.content[:100]}...\n")


# ============================================================================
# 主函數：運行所有範例
# ============================================================================
def main():
    """運行所有工具使用範例"""

    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║              Agno 內建工具使用完整示範                         ║
    ║                                                                ║
    ║  展示 100+ 內建工具包的使用方法和最佳實踐                      ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

    # 檢查環境變數
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 錯誤: 請設置 OPENAI_API_KEY 環境變數")
        return

    try:
        # 運行各個範例
        example_1_web_search()
        example_2_calculator()
        example_3_python_tools()
        example_4_file_tools()
        example_5_multiple_tools()
        example_6_custom_tool()
        example_7_tavily_search()
        example_8_tool_control()

        print("\n" + "="*80)
        print("✅ 所有範例執行完成！")
        print("="*80)

        print("\n📚 下一步學習：")
        print("- 03_多模態Agent.py - 探索圖像、音頻處理能力")
        print("- 04_Agentic_RAG.py - 學習智能 RAG 系統")
        print("- 05_團隊協作.py - 構建多 Agent 團隊")

    except Exception as e:
        print(f"\n❌ 執行過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


# ============================================================================
# 學習要點總結
# ============================================================================
"""
📚 Agno 工具使用學習要點：

1. **內建工具包**
   - DuckDuckGoTools: 免費網頁搜索
   - TavilyTools: AI 優化的深度搜索
   - PythonTools: Python 代碼執行
   - CalculatorTools: 數學計算
   - FileTools: 文件操作
   - ShellTools: Shell 命令執行

2. **工具配置**
   ```python
   agent = Agent(
       tools=[Tool1(), Tool2()],  # 添加工具
       tool_choice="auto",         # 工具選擇模式
       show_tool_calls=True        # 顯示調用過程
   )
   ```

3. **工具選擇模式**
   - "auto": Agent 自動決定（預設）
   - "required": 強制使用工具
   - "none": 禁用所有工具

4. **多工具組合**
   - 添加多個工具到 tools 列表
   - Agent 智能選擇合適的工具
   - 可以串聯使用多個工具

5. **自定義工具**
   ```python
   from agno.tools import Tool

   custom_tool = Tool(
       name="tool_name",
       description="工具描述",
       func=your_function
   )
   ```

6. **工具最佳實踐**
   - 選擇專用工具優於通用工具
   - 提供清晰的工具描述
   - 合理設置工具調用參數
   - 實施錯誤處理和重試

7. **常用工具場景**
   - 信息查詢 → DuckDuckGo/Tavily
   - 數學計算 → Calculator
   - 代碼執行 → Python
   - 數據分析 → Python + File
   - 自動化 → Shell + File

8. **工具性能優化**
   - 限制工具調用次數
   - 設置合理的超時時間
   - 使用緩存減少重複調用
   - 並行執行獨立工具

💡 最佳實踐：
- 為不同任務選擇合適的工具
- 組合使用多個工具解決複雜問題
- 監控工具調用過程（show_tool_calls=True）
- 開發自定義工具擴展功能
- 實施完善的錯誤處理

🔗 相關資源：
- Agno 工具文檔: https://docs.agno.com/tools
- 自定義工具開發: https://docs.agno.com/custom-tools
- 工具最佳實踐: https://docs.agno.com/tools/best-practices

⚡ Agno 工具優勢：
- 100+ 內建工具包
- 開箱即用，無需配置
- 智能工具選擇
- 高性能執行
"""
