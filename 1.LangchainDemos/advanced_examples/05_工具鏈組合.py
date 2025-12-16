"""
LangChain 工具鏈組合範例
=======================

本範例展示如何組合多個工具形成複雜的處理鏈。

組合方式：
1. 順序執行
2. 並行執行
3. 條件分支
4. 動態路由

安裝依賴：
pip install langchain langchain-openai
"""

from langchain_openai import ChatOpenAI
from langchain.tools import BaseTool, tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableParallel
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import json

# ============================================================
# 1. 定義工具
# ============================================================

@tool
def search_web(query: str) -> str:
    """搜索網頁獲取信息"""
    # 模擬搜索結果
    return f"搜索結果: 找到關於 '{query}' 的 10 條相關信息"


@tool
def calculate(expression: str) -> str:
    """計算數學表達式"""
    try:
        result = eval(expression)
        return f"計算結果: {expression} = {result}"
    except Exception as e:
        return f"計算錯誤: {e}"


@tool
def translate(text: str, target_language: str = "英文") -> str:
    """翻譯文本"""
    # 模擬翻譯
    return f"翻譯結果 ({target_language}): [翻譯後的內容]"


@tool
def summarize(text: str) -> str:
    """總結文本"""
    words = text.split()
    summary = " ".join(words[:20]) + "..." if len(words) > 20 else text
    return f"摘要: {summary}"


@tool
def extract_keywords(text: str) -> str:
    """提取關鍵詞"""
    # 模擬關鍵詞提取
    words = text.split()[:5]
    return f"關鍵詞: {', '.join(words)}"


# ============================================================
# 2. 工具組合類
# ============================================================

class ToolChain:
    """工具鏈"""

    def __init__(self, tools: List[BaseTool]):
        self.tools = {t.name: t for t in tools}

    def run_sequential(self, tool_names: List[str], initial_input: str) -> str:
        """順序執行工具"""
        current_input = initial_input

        for name in tool_names:
            if name in self.tools:
                result = self.tools[name].run(current_input)
                current_input = result
                print(f"[{name}] -> {result[:100]}...")

        return current_input

    def run_parallel(self, tool_names: List[str], input_text: str) -> Dict[str, str]:
        """並行執行工具（模擬）"""
        results = {}

        for name in tool_names:
            if name in self.tools:
                results[name] = self.tools[name].run(input_text)

        return results

    def run_conditional(
        self,
        condition_func,
        true_tools: List[str],
        false_tools: List[str],
        input_text: str
    ) -> str:
        """條件執行"""
        if condition_func(input_text):
            return self.run_sequential(true_tools, input_text)
        else:
            return self.run_sequential(false_tools, input_text)


TOOL_CHAIN_EXAMPLE = '''
# 工具鏈使用範例

tools = [search_web, calculate, translate, summarize]
chain = ToolChain(tools)

# 順序執行
result = chain.run_sequential(
    ["search_web", "summarize"],
    "人工智能最新發展"
)

# 並行執行
results = chain.run_parallel(
    ["summarize", "extract_keywords"],
    "這是一段需要處理的長文本..."
)

# 條件執行
result = chain.run_conditional(
    lambda x: "數學" in x,
    ["calculate"],
    ["search_web"],
    "計算 2 + 2"
)
'''


# ============================================================
# 3. LCEL 工具組合
# ============================================================

LCEL_TOOL_EXAMPLE = '''
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()

# 並行處理
parallel_chain = RunnableParallel(
    summary=summarize_chain,
    keywords=keyword_chain,
    translation=translate_chain
)

# 順序處理
sequential_chain = (
    {"input": RunnablePassthrough()}
    | search_chain
    | summarize_chain
    | translate_chain
)

# 執行
result = parallel_chain.invoke("輸入文本")
'''


# ============================================================
# 4. 自定義工具類
# ============================================================

class DataProcessorInput(BaseModel):
    """數據處理器輸入"""
    data: str = Field(description="要處理的數據")
    operation: str = Field(description="操作類型: clean, transform, validate")


class DataProcessorTool(BaseTool):
    """數據處理工具"""
    name = "data_processor"
    description = "處理和轉換數據"
    args_schema = DataProcessorInput

    def _run(self, data: str, operation: str) -> str:
        if operation == "clean":
            return f"清理後的數據: {data.strip()}"
        elif operation == "transform":
            return f"轉換後的數據: {data.upper()}"
        elif operation == "validate":
            return f"驗證結果: 數據有效" if data else "驗證結果: 數據無效"
        else:
            return f"未知操作: {operation}"

    async def _arun(self, data: str, operation: str) -> str:
        return self._run(data, operation)


# ============================================================
# 5. 工具路由器
# ============================================================

class ToolRouter:
    """工具路由器"""

    def __init__(self, tools: List[BaseTool]):
        self.tools = {t.name: t for t in tools}
        self.routes = {}

    def add_route(self, pattern: str, tool_name: str):
        """添加路由規則"""
        self.routes[pattern] = tool_name

    def route(self, input_text: str) -> Optional[str]:
        """根據輸入路由到工具"""
        for pattern, tool_name in self.routes.items():
            if pattern.lower() in input_text.lower():
                return tool_name
        return None

    def execute(self, input_text: str) -> str:
        """執行路由後的工具"""
        tool_name = self.route(input_text)

        if tool_name and tool_name in self.tools:
            return self.tools[tool_name].run(input_text)
        else:
            return "無法找到合適的工具處理此請求"


ROUTER_EXAMPLE = '''
# 工具路由器使用

router = ToolRouter([search_web, calculate, translate, summarize])

# 添加路由規則
router.add_route("搜索", "search_web")
router.add_route("計算", "calculate")
router.add_route("翻譯", "translate")
router.add_route("總結", "summarize")

# 自動路由執行
result = router.execute("搜索人工智能")  # 使用 search_web
result = router.execute("計算 10 * 5")    # 使用 calculate
'''


# ============================================================
# 6. 工具流水線
# ============================================================

class ToolPipeline:
    """工具流水線"""

    def __init__(self):
        self.stages: List[Dict] = []

    def add_stage(
        self,
        name: str,
        tool: BaseTool,
        input_key: str = "input",
        output_key: str = "output"
    ):
        """添加階段"""
        self.stages.append({
            "name": name,
            "tool": tool,
            "input_key": input_key,
            "output_key": output_key
        })
        return self

    def execute(self, initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """執行流水線"""
        data = initial_data.copy()

        for stage in self.stages:
            input_value = data.get(stage["input_key"], "")
            print(f"執行階段: {stage['name']}")

            result = stage["tool"].run(input_value)
            data[stage["output_key"]] = result

        return data


PIPELINE_EXAMPLE = '''
# 工具流水線使用

pipeline = ToolPipeline()
pipeline.add_stage("search", search_web, "query", "search_result")
pipeline.add_stage("summarize", summarize, "search_result", "summary")
pipeline.add_stage("translate", translate, "summary", "translated")

result = pipeline.execute({
    "query": "機器學習的應用"
})

print(result["summary"])
print(result["translated"])
'''


# ============================================================
# 7. 組合 Agent
# ============================================================

COMBINED_AGENT_EXAMPLE = '''
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4")

# 所有工具
tools = [search_web, calculate, translate, summarize, extract_keywords]

# 創建提示
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一個多功能助手，可以使用各種工具完成任務。"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

# 創建 Agent
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 執行複雜任務
result = agent_executor.invoke({
    "input": "搜索最新的 AI 新聞，然後總結並翻譯成英文"
})
'''


# ============================================================
# 使用範例
# ============================================================

def example_basic_tools():
    """範例 1: 基本工具"""
    print("=" * 50)
    print("範例 1: 基本工具定義")
    print("=" * 50)

    tools = [search_web, calculate, translate, summarize, extract_keywords]
    for t in tools:
        print(f"  - {t.name}: {t.description}")


def example_tool_chain():
    """範例 2: 工具鏈"""
    print("\n" + "=" * 50)
    print("範例 2: 工具鏈組合")
    print("=" * 50)
    print(TOOL_CHAIN_EXAMPLE)


def example_lcel():
    """範例 3: LCEL 組合"""
    print("\n" + "=" * 50)
    print("範例 3: LCEL 工具組合")
    print("=" * 50)
    print(LCEL_TOOL_EXAMPLE)


def example_custom_tool():
    """範例 4: 自定義工具"""
    print("\n" + "=" * 50)
    print("範例 4: 自定義工具類")
    print("=" * 50)

    tool = DataProcessorTool()
    print(f"工具名: {tool.name}")
    print(f"描述: {tool.description}")
    print(f"輸入 Schema: {tool.args_schema.schema()}")


def example_router():
    """範例 5: 工具路由"""
    print("\n" + "=" * 50)
    print("範例 5: 工具路由器")
    print("=" * 50)
    print(ROUTER_EXAMPLE)


def example_pipeline():
    """範例 6: 工具流水線"""
    print("\n" + "=" * 50)
    print("範例 6: 工具流水線")
    print("=" * 50)
    print(PIPELINE_EXAMPLE)


def example_combined_agent():
    """範例 7: 組合 Agent"""
    print("\n" + "=" * 50)
    print("範例 7: 組合 Agent")
    print("=" * 50)
    print(COMBINED_AGENT_EXAMPLE)


if __name__ == "__main__":
    print("LangChain 工具鏈組合範例\n")
    example_basic_tools()
    example_tool_chain()
    example_lcel()
    example_custom_tool()
    example_router()
    example_pipeline()
    example_combined_agent()
