"""
PromptFlow Tool 定義範例
========================

本範例展示如何在 PromptFlow 中定義和使用自定義工具。

Tool 功能：
1. 自定義 Python 工具
2. LLM 工具
3. Prompt 工具
4. 工具組合

安裝依賴：
pip install promptflow promptflow-tools
"""

import os
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

# ============================================================
# PromptFlow Tool 裝飾器模擬
# ============================================================

def tool(func):
    """
    工具裝飾器

    模擬 PromptFlow 的 @tool 裝飾器
    """
    func._is_tool = True
    return func


# ============================================================
# 基礎工具定義
# ============================================================

@tool
def echo(text: str) -> str:
    """
    簡單的回聲工具

    Args:
        text: 輸入文本

    Returns:
        相同的文本
    """
    return text


@tool
def string_length(text: str) -> int:
    """
    計算字符串長度

    Args:
        text: 輸入字符串

    Returns:
        字符串長度
    """
    return len(text)


@tool
def join_strings(strings: List[str], separator: str = ", ") -> str:
    """
    連接字符串列表

    Args:
        strings: 字符串列表
        separator: 分隔符

    Returns:
        連接後的字符串
    """
    return separator.join(strings)


# ============================================================
# 數據處理工具
# ============================================================

@tool
def parse_json(json_string: str) -> Dict[str, Any]:
    """
    解析 JSON 字符串

    Args:
        json_string: JSON 字符串

    Returns:
        解析後的字典
    """
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        return {"error": str(e)}


@tool
def format_json(data: Dict[str, Any], indent: int = 2) -> str:
    """
    格式化 JSON

    Args:
        data: 數據字典
        indent: 縮進空格數

    Returns:
        格式化的 JSON 字符串
    """
    return json.dumps(data, indent=indent, ensure_ascii=False)


@tool
def extract_field(data: Dict[str, Any], field_path: str) -> Any:
    """
    從嵌套字典中提取字段

    Args:
        data: 數據字典
        field_path: 字段路徑（如 "user.name"）

    Returns:
        提取的值
    """
    keys = field_path.split(".")
    result = data

    for key in keys:
        if isinstance(result, dict) and key in result:
            result = result[key]
        else:
            return None

    return result


# ============================================================
# 文本處理工具
# ============================================================

@tool
def text_summarize_simple(text: str, max_sentences: int = 3) -> str:
    """
    簡單的文本摘要（取前幾句）

    Args:
        text: 輸入文本
        max_sentences: 最大句子數

    Returns:
        摘要文本
    """
    import re
    sentences = re.split(r'[。！？.!?]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    return '。'.join(sentences[:max_sentences]) + '。' if sentences else text


@tool
def keyword_extract(text: str, top_k: int = 5) -> List[str]:
    """
    簡單的關鍵詞提取

    Args:
        text: 輸入文本
        top_k: 返回前 k 個關鍵詞

    Returns:
        關鍵詞列表
    """
    import re
    from collections import Counter

    # 簡單分詞
    words = re.findall(r'\w+', text.lower())
    # 過濾短詞
    words = [w for w in words if len(w) > 2]
    # 統計頻率
    counter = Counter(words)
    # 返回最常見的詞
    return [word for word, _ in counter.most_common(top_k)]


@tool
def sentiment_simple(text: str) -> str:
    """
    簡單的情感分析

    Args:
        text: 輸入文本

    Returns:
        情感標籤（positive/negative/neutral）
    """
    positive_words = {'好', '棒', '喜歡', '開心', '優秀', 'good', 'great', 'love', 'happy'}
    negative_words = {'差', '糟', '討厭', '生氣', '失望', 'bad', 'poor', 'hate', 'angry'}

    text_lower = text.lower()
    pos_count = sum(1 for w in positive_words if w in text_lower)
    neg_count = sum(1 for w in negative_words if w in text_lower)

    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    else:
        return "neutral"


# ============================================================
# API 調用工具
# ============================================================

@tool
def http_get(url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    發送 HTTP GET 請求

    Args:
        url: 請求 URL
        headers: 請求頭

    Returns:
        響應數據
    """
    import requests

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return {
            "status_code": response.status_code,
            "data": response.json() if 'application/json' in response.headers.get('content-type', '') else response.text
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def http_post(
    url: str,
    data: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    發送 HTTP POST 請求

    Args:
        url: 請求 URL
        data: 請求數據
        headers: 請求頭

    Returns:
        響應數據
    """
    import requests

    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        return {
            "status_code": response.status_code,
            "data": response.json() if 'application/json' in response.headers.get('content-type', '') else response.text
        }
    except Exception as e:
        return {"error": str(e)}


# ============================================================
# 工具類封裝
# ============================================================

class ToolRegistry:
    """
    工具註冊表

    管理和組織工具
    """

    def __init__(self):
        self.tools: Dict[str, callable] = {}

    def register(self, name: str, func: callable):
        """註冊工具"""
        self.tools[name] = func

    def get(self, name: str) -> Optional[callable]:
        """獲取工具"""
        return self.tools.get(name)

    def execute(self, name: str, **kwargs) -> Any:
        """執行工具"""
        tool_func = self.get(name)
        if not tool_func:
            raise ValueError(f"工具不存在: {name}")
        return tool_func(**kwargs)

    def list_tools(self) -> List[str]:
        """列出所有工具"""
        return list(self.tools.keys())


# ============================================================
# LLM 工具模板
# ============================================================

@dataclass
class LLMToolConfig:
    """LLM 工具配置"""
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 1000
    api_key: str = ""


class LLMTool:
    """
    LLM 工具基類

    封裝 LLM 調用邏輯
    """

    def __init__(self, config: LLMToolConfig):
        self.config = config

    def generate(self, prompt: str) -> str:
        """
        生成文本

        Args:
            prompt: 提示詞

        Returns:
            生成的文本
        """
        # 這裡是模擬實現
        # 實際使用時應調用真實的 LLM API
        return f"[模擬 LLM 響應] 針對: {prompt[:50]}..."

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        聊天對話

        Args:
            messages: 消息列表

        Returns:
            助手回覆
        """
        last_message = messages[-1]['content'] if messages else ""
        return f"[模擬聊天響應] 回覆: {last_message[:50]}..."


# ============================================================
# 複合工具
# ============================================================

@tool
def analyze_text(text: str) -> Dict[str, Any]:
    """
    綜合文本分析工具

    Args:
        text: 輸入文本

    Returns:
        分析結果
    """
    return {
        "length": string_length(text),
        "keywords": keyword_extract(text),
        "sentiment": sentiment_simple(text),
        "summary": text_summarize_simple(text)
    }


@tool
def process_api_response(
    url: str,
    field_path: str,
    transform: str = "none"
) -> Any:
    """
    處理 API 響應

    Args:
        url: API URL
        field_path: 要提取的字段路徑
        transform: 轉換類型

    Returns:
        處理後的數據
    """
    response = http_get(url)

    if "error" in response:
        return response

    data = response.get("data", {})
    extracted = extract_field(data, field_path)

    if transform == "json":
        return format_json(extracted) if isinstance(extracted, dict) else str(extracted)
    elif transform == "length":
        return len(extracted) if extracted else 0

    return extracted


# ============================================================
# 使用範例
# ============================================================

def example_basic_tools():
    """
    範例 1: 基礎工具使用

    展示簡單工具的使用
    """
    print("=" * 50)
    print("範例 1: 基礎工具使用")
    print("=" * 50)

    # 使用 echo 工具
    result = echo("Hello, PromptFlow!")
    print(f"Echo: {result}")

    # 使用 string_length 工具
    length = string_length("這是一個測試字符串")
    print(f"字符串長度: {length}")

    # 使用 join_strings 工具
    joined = join_strings(["蘋果", "香蕉", "橙子"], " | ")
    print(f"連接結果: {joined}")


def example_data_tools():
    """
    範例 2: 數據處理工具

    展示 JSON 和數據處理
    """
    print("\n" + "=" * 50)
    print("範例 2: 數據處理工具")
    print("=" * 50)

    # 解析 JSON
    json_str = '{"name": "張三", "age": 25, "address": {"city": "台北"}}'
    parsed = parse_json(json_str)
    print(f"解析 JSON: {parsed}")

    # 提取字段
    city = extract_field(parsed, "address.city")
    print(f"提取城市: {city}")

    # 格式化 JSON
    formatted = format_json(parsed)
    print(f"格式化 JSON:\n{formatted}")


def example_text_tools():
    """
    範例 3: 文本處理工具

    展示文本分析功能
    """
    print("\n" + "=" * 50)
    print("範例 3: 文本處理工具")
    print("=" * 50)

    text = """
    人工智能技術正在快速發展。機器學習和深度學習是其中最重要的分支。
    這些技術已經被廣泛應用於各個領域。未來將會有更多創新應用出現。
    我們對 AI 的發展感到非常興奮和期待。
    """

    # 摘要
    summary = text_summarize_simple(text, max_sentences=2)
    print(f"摘要: {summary}")

    # 關鍵詞
    keywords = keyword_extract(text)
    print(f"關鍵詞: {keywords}")

    # 情感分析
    sentiment = sentiment_simple(text)
    print(f"情感: {sentiment}")


def example_tool_registry():
    """
    範例 4: 工具註冊表

    展示如何管理多個工具
    """
    print("\n" + "=" * 50)
    print("範例 4: 工具註冊表")
    print("=" * 50)

    registry = ToolRegistry()

    # 註冊工具
    registry.register("echo", echo)
    registry.register("length", string_length)
    registry.register("join", join_strings)
    registry.register("parse_json", parse_json)

    # 列出工具
    print(f"可用工具: {registry.list_tools()}")

    # 執行工具
    result = registry.execute("echo", text="Hello from registry!")
    print(f"執行 echo: {result}")

    result = registry.execute("length", text="測試")
    print(f"執行 length: {result}")


def example_llm_tool():
    """
    範例 5: LLM 工具

    展示 LLM 工具的使用
    """
    print("\n" + "=" * 50)
    print("範例 5: LLM 工具")
    print("=" * 50)

    config = LLMToolConfig(
        model="gpt-4",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY", "")
    )

    llm = LLMTool(config)

    # 生成文本
    response = llm.generate("請解釋什麼是機器學習")
    print(f"生成響應: {response}")

    # 聊天
    messages = [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好！有什麼可以幫助你的嗎？"},
        {"role": "user", "content": "我想學習 Python"}
    ]
    chat_response = llm.chat(messages)
    print(f"聊天響應: {chat_response}")


def example_composite_tools():
    """
    範例 6: 複合工具

    展示組合多個工具的功能
    """
    print("\n" + "=" * 50)
    print("範例 6: 複合工具")
    print("=" * 50)

    text = "這個產品非常好用，我很喜歡！推薦給大家。性價比很高，質量也不錯。"

    # 使用綜合分析工具
    analysis = analyze_text(text)

    print("文本分析結果:")
    print(f"  長度: {analysis['length']}")
    print(f"  關鍵詞: {analysis['keywords']}")
    print(f"  情感: {analysis['sentiment']}")
    print(f"  摘要: {analysis['summary']}")


def example_tool_definition_yaml():
    """
    範例 7: YAML 工具定義

    展示 PromptFlow 中的 YAML 工具定義格式
    """
    print("\n" + "=" * 50)
    print("範例 7: YAML 工具定義")
    print("=" * 50)

    yaml_definition = """
# PromptFlow 工具定義 (tools.yaml)

name: my_custom_tool
type: python
description: 自定義 Python 工具示例

inputs:
  text:
    type: string
    description: 輸入文本
  max_length:
    type: int
    default: 100
    description: 最大長度

outputs:
  result:
    type: string
    description: 處理結果

source:
  type: code
  path: tools/my_tool.py

---

# LLM 工具定義

name: llm_chat
type: llm
description: LLM 聊天工具

inputs:
  prompt:
    type: string
    description: 提示詞
  temperature:
    type: float
    default: 0.7

connection: azure_openai
api: chat
"""

    print("YAML 工具定義示例:")
    print(yaml_definition)


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    print("PromptFlow Tool 定義範例")
    print()

    example_basic_tools()
    example_data_tools()
    example_text_tools()
    example_tool_registry()
    example_llm_tool()
    example_composite_tools()
    example_tool_definition_yaml()
