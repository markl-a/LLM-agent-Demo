"""
LangChain 動態路由範例
=====================

本範例展示如何在 LangChain 中實現動態路由。

路由類型：
1. 基於關鍵詞的路由
2. 基於 LLM 的智能路由
3. 多級路由
4. 帶回退的路由

安裝依賴：
pip install langchain langchain-openai
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from typing import Dict, Any, Callable, List, Optional
from dataclasses import dataclass
import re

# ============================================================
# 1. 基於關鍵詞的路由
# ============================================================

class KeywordRouter:
    """關鍵詞路由器"""

    def __init__(self):
        self.routes: Dict[str, Callable] = {}
        self.default_handler: Optional[Callable] = None

    def add_route(self, keywords: List[str], handler: Callable):
        """添加路由規則"""
        for keyword in keywords:
            self.routes[keyword.lower()] = handler

    def set_default(self, handler: Callable):
        """設置默認處理器"""
        self.default_handler = handler

    def route(self, text: str) -> Callable:
        """路由到處理器"""
        text_lower = text.lower()
        for keyword, handler in self.routes.items():
            if keyword in text_lower:
                return handler
        return self.default_handler or (lambda x: "未找到匹配的處理器")

    def execute(self, text: str) -> Any:
        """執行路由"""
        handler = self.route(text)
        return handler(text)


KEYWORD_ROUTER_EXAMPLE = '''
# 關鍵詞路由使用

router = KeywordRouter()

# 定義處理器
def handle_question(text):
    return f"這是一個問題: {text}"

def handle_command(text):
    return f"執行命令: {text}"

def handle_default(text):
    return f"默認處理: {text}"

# 添加路由
router.add_route(["什麼", "怎麼", "為什麼", "?", "？"], handle_question)
router.add_route(["執行", "運行", "開始"], handle_command)
router.set_default(handle_default)

# 使用
result = router.execute("什麼是人工智能？")  # -> handle_question
result = router.execute("執行任務")          # -> handle_command
result = router.execute("你好")              # -> handle_default
'''


# ============================================================
# 2. LLM 智能路由
# ============================================================

ROUTER_PROMPT = """分析以下用戶輸入，判斷它屬於哪個類別：

類別：
- question: 詢問問題，尋求信息
- command: 執行命令或操作
- chat: 閒聊，打招呼
- feedback: 反饋或評價

用戶輸入: {input}

只回覆類別名稱，不要其他內容。
類別:"""


class LLMRouter:
    """LLM 智能路由器"""

    def __init__(self, llm=None):
        self.llm = llm or ChatOpenAI(temperature=0)
        self.routes: Dict[str, Callable] = {}
        self.prompt = ChatPromptTemplate.from_template(ROUTER_PROMPT)

    def add_route(self, category: str, handler: Callable):
        """添加類別路由"""
        self.routes[category] = handler

    def classify(self, text: str) -> str:
        """使用 LLM 分類"""
        chain = self.prompt | self.llm | StrOutputParser()
        category = chain.invoke({"input": text})
        return category.strip().lower()

    def execute(self, text: str) -> Any:
        """分類並執行"""
        category = self.classify(text)
        handler = self.routes.get(category)

        if handler:
            return handler(text)
        return f"未找到類別 '{category}' 的處理器"


LLM_ROUTER_EXAMPLE = '''
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()
router = LLMRouter(llm)

# 添加路由
router.add_route("question", lambda x: f"回答問題: {x}")
router.add_route("command", lambda x: f"執行命令: {x}")
router.add_route("chat", lambda x: f"閒聊: {x}")
router.add_route("feedback", lambda x: f"處理反饋: {x}")

# 使用
result = router.execute("今天天氣怎麼樣？")  # -> question
result = router.execute("幫我搜索資料")      # -> command
result = router.execute("你好啊")           # -> chat
'''


# ============================================================
# 3. LCEL 分支路由
# ============================================================

LCEL_BRANCH_EXAMPLE = '''
from langchain_core.runnables import RunnableBranch

# 定義處理鏈
question_chain = ChatPromptTemplate.from_template(
    "回答問題: {input}"
) | llm | StrOutputParser()

command_chain = ChatPromptTemplate.from_template(
    "執行命令: {input}"
) | llm | StrOutputParser()

default_chain = ChatPromptTemplate.from_template(
    "一般處理: {input}"
) | llm | StrOutputParser()

# 創建分支
branch = RunnableBranch(
    (lambda x: "?" in x["input"] or "什麼" in x["input"], question_chain),
    (lambda x: "執行" in x["input"], command_chain),
    default_chain  # 默認分支
)

# 執行
result = branch.invoke({"input": "什麼是機器學習？"})
'''


# ============================================================
# 4. 多級路由
# ============================================================

@dataclass
class RouteNode:
    """路由節點"""
    name: str
    condition: Callable[[str], bool]
    handler: Optional[Callable] = None
    children: List['RouteNode'] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []


class HierarchicalRouter:
    """層級路由器"""

    def __init__(self):
        self.root_nodes: List[RouteNode] = []

    def add_root(self, node: RouteNode):
        """添加根節點"""
        self.root_nodes.append(node)

    def find_route(self, text: str, nodes: List[RouteNode] = None) -> Optional[RouteNode]:
        """遞歸查找匹配的路由"""
        nodes = nodes if nodes is not None else self.root_nodes

        for node in nodes:
            if node.condition(text):
                # 檢查子節點
                if node.children:
                    child_match = self.find_route(text, node.children)
                    if child_match:
                        return child_match
                return node

        return None

    def execute(self, text: str) -> Any:
        """執行路由"""
        node = self.find_route(text)
        if node and node.handler:
            return node.handler(text)
        return "未找到匹配的路由"


HIERARCHICAL_EXAMPLE = '''
# 層級路由使用

router = HierarchicalRouter()

# 第一級：技術 vs 非技術
tech_node = RouteNode(
    name="tech",
    condition=lambda x: any(w in x for w in ["代碼", "編程", "技術", "AI"]),
    children=[
        RouteNode(
            name="coding",
            condition=lambda x: "代碼" in x or "編程" in x,
            handler=lambda x: f"處理編程問題: {x}"
        ),
        RouteNode(
            name="ai",
            condition=lambda x: "AI" in x or "人工智能" in x,
            handler=lambda x: f"處理 AI 問題: {x}"
        )
    ]
)

general_node = RouteNode(
    name="general",
    condition=lambda x: True,  # 默認
    handler=lambda x: f"一般處理: {x}"
)

router.add_root(tech_node)
router.add_root(general_node)

result = router.execute("如何寫 Python 代碼？")  # -> coding
result = router.execute("AI 的發展趨勢")        # -> ai
'''


# ============================================================
# 5. 帶回退的路由
# ============================================================

class FallbackRouter:
    """帶回退的路由器"""

    def __init__(self):
        self.primary_routes: List[tuple] = []
        self.fallback_handler: Optional[Callable] = None
        self.error_handler: Optional[Callable] = None

    def add_route(self, condition: Callable, handler: Callable, priority: int = 0):
        """添加路由（帶優先級）"""
        self.primary_routes.append((priority, condition, handler))
        self.primary_routes.sort(key=lambda x: x[0], reverse=True)

    def set_fallback(self, handler: Callable):
        """設置回退處理器"""
        self.fallback_handler = handler

    def set_error_handler(self, handler: Callable):
        """設置錯誤處理器"""
        self.error_handler = handler

    def execute(self, text: str) -> Any:
        """執行路由"""
        # 嘗試主路由
        for priority, condition, handler in self.primary_routes:
            try:
                if condition(text):
                    result = handler(text)
                    if result is not None:
                        return result
            except Exception as e:
                if self.error_handler:
                    return self.error_handler(text, e)

        # 回退處理
        if self.fallback_handler:
            return self.fallback_handler(text)

        return "無法處理此請求"


# ============================================================
# 6. 語義路由
# ============================================================

SEMANTIC_ROUTER_EXAMPLE = '''
from langchain_openai import OpenAIEmbeddings
import numpy as np

class SemanticRouter:
    """語義路由器"""

    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.routes = []  # (embedding, handler, description)

    def add_route(self, description: str, handler: Callable):
        """添加語義路由"""
        embedding = self.embeddings.embed_query(description)
        self.routes.append((np.array(embedding), handler, description))

    def _cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def route(self, text: str) -> Callable:
        """語義匹配路由"""
        query_embedding = np.array(self.embeddings.embed_query(text))

        best_match = None
        best_score = -1

        for emb, handler, desc in self.routes:
            score = self._cosine_similarity(query_embedding, emb)
            if score > best_score:
                best_score = score
                best_match = handler

        return best_match

# 使用
router = SemanticRouter()
router.add_route("詢問技術問題", tech_handler)
router.add_route("日常閒聊", chat_handler)
router.add_route("執行任務", task_handler)

handler = router.route("Python 怎麼安裝套件？")
result = handler("Python 怎麼安裝套件？")
'''


# ============================================================
# 使用範例
# ============================================================

def example_keyword():
    """範例 1: 關鍵詞路由"""
    print("=" * 50)
    print("範例 1: 關鍵詞路由")
    print("=" * 50)
    print(KEYWORD_ROUTER_EXAMPLE)


def example_llm_router():
    """範例 2: LLM 智能路由"""
    print("\n" + "=" * 50)
    print("範例 2: LLM 智能路由")
    print("=" * 50)
    print(LLM_ROUTER_EXAMPLE)


def example_lcel_branch():
    """範例 3: LCEL 分支路由"""
    print("\n" + "=" * 50)
    print("範例 3: LCEL 分支路由")
    print("=" * 50)
    print(LCEL_BRANCH_EXAMPLE)


def example_hierarchical():
    """範例 4: 多級路由"""
    print("\n" + "=" * 50)
    print("範例 4: 層級路由")
    print("=" * 50)
    print(HIERARCHICAL_EXAMPLE)


def example_fallback():
    """範例 5: 帶回退的路由"""
    print("\n" + "=" * 50)
    print("範例 5: 帶回退的路由")
    print("=" * 50)

    router = FallbackRouter()

    router.add_route(
        lambda x: "問題" in x,
        lambda x: f"處理問題: {x}",
        priority=10
    )
    router.set_fallback(lambda x: f"默認處理: {x}")
    router.set_error_handler(lambda x, e: f"錯誤: {e}")

    print("路由器配置完成")
    print(f"測試: {router.execute('這是一個問題')}")
    print(f"測試: {router.execute('你好')}")


def example_semantic():
    """範例 6: 語義路由"""
    print("\n" + "=" * 50)
    print("範例 6: 語義路由")
    print("=" * 50)
    print(SEMANTIC_ROUTER_EXAMPLE)


if __name__ == "__main__":
    print("LangChain 動態路由範例\n")
    example_keyword()
    example_llm_router()
    example_lcel_branch()
    example_hierarchical()
    example_fallback()
    example_semantic()
