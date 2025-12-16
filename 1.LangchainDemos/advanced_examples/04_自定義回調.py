"""
LangChain 自定義回調範例
======================

本範例展示如何在 LangChain 中使用和自定義回調。

回調類型：
1. 內置回調
2. 自定義回調處理器
3. 異步回調
4. 流式回調

安裝依賴：
pip install langchain langchain-openai
"""

from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks import StdOutCallbackHandler
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, BaseMessage
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
import time
import json
from datetime import datetime

# ============================================================
# 1. 內置回調處理器
# ============================================================

BUILTIN_CALLBACKS_EXAMPLE = '''
from langchain.callbacks import StdOutCallbackHandler
from langchain_openai import ChatOpenAI

# 標準輸出回調
llm = ChatOpenAI(
    callbacks=[StdOutCallbackHandler()]
)

# 調用時會在控制台輸出詳細信息
response = llm.invoke("Hello!")
'''


# ============================================================
# 2. 自定義回調處理器
# ============================================================

class CustomCallbackHandler(BaseCallbackHandler):
    """自定義回調處理器"""

    def __init__(self, name: str = "CustomHandler"):
        self.name = name
        self.events: List[Dict] = []
        self.start_time: Optional[float] = None

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        **kwargs
    ) -> None:
        """LLM 開始時"""
        self.start_time = time.time()
        self.events.append({
            "event": "llm_start",
            "timestamp": datetime.now().isoformat(),
            "prompts": prompts
        })
        print(f"[{self.name}] LLM 開始，提示數: {len(prompts)}")

    def on_llm_end(self, response, **kwargs) -> None:
        """LLM 結束時"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        self.events.append({
            "event": "llm_end",
            "timestamp": datetime.now().isoformat(),
            "elapsed": elapsed
        })
        print(f"[{self.name}] LLM 結束，耗時: {elapsed:.2f}s")

    def on_llm_error(self, error: Exception, **kwargs) -> None:
        """LLM 錯誤時"""
        self.events.append({
            "event": "llm_error",
            "timestamp": datetime.now().isoformat(),
            "error": str(error)
        })
        print(f"[{self.name}] LLM 錯誤: {error}")

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        **kwargs
    ) -> None:
        """Chain 開始時"""
        print(f"[{self.name}] Chain 開始: {serialized.get('name', 'Unknown')}")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        """Chain 結束時"""
        print(f"[{self.name}] Chain 結束")

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        **kwargs
    ) -> None:
        """Tool 開始時"""
        print(f"[{self.name}] Tool 開始: {serialized.get('name', 'Unknown')}")

    def on_tool_end(self, output: str, **kwargs) -> None:
        """Tool 結束時"""
        print(f"[{self.name}] Tool 結束")

    def get_events(self) -> List[Dict]:
        """獲取所有事件"""
        return self.events


CUSTOM_CALLBACK_EXAMPLE = '''
# 使用自定義回調
handler = CustomCallbackHandler(name="MyHandler")

llm = ChatOpenAI(callbacks=[handler])

response = llm.invoke("什麼是人工智能？")

# 查看事件
for event in handler.get_events():
    print(f"{event['event']}: {event['timestamp']}")
'''


# ============================================================
# 3. 日誌回調處理器
# ============================================================

class LoggingCallbackHandler(BaseCallbackHandler):
    """日誌回調處理器"""

    def __init__(self, log_file: str = "langchain.log"):
        self.log_file = log_file
        self.logs = []

    def _log(self, level: str, message: str, data: Dict = None):
        """記錄日誌"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "data": data or {}
        }
        self.logs.append(entry)

        # 寫入文件
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def on_llm_start(self, serialized, prompts, **kwargs):
        self._log("INFO", "LLM started", {"prompt_count": len(prompts)})

    def on_llm_end(self, response, **kwargs):
        self._log("INFO", "LLM completed", {"response": str(response)[:100]})

    def on_llm_error(self, error, **kwargs):
        self._log("ERROR", "LLM error", {"error": str(error)})

    def on_chain_start(self, serialized, inputs, **kwargs):
        self._log("INFO", "Chain started", {"chain": serialized.get("name")})

    def on_chain_end(self, outputs, **kwargs):
        self._log("INFO", "Chain completed")

    def on_chain_error(self, error, **kwargs):
        self._log("ERROR", "Chain error", {"error": str(error)})


# ============================================================
# 4. 指標收集回調
# ============================================================

@dataclass
class Metrics:
    """指標數據"""
    llm_calls: int = 0
    chain_calls: int = 0
    tool_calls: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    total_time: float = 0.0
    errors: int = 0


class MetricsCallbackHandler(BaseCallbackHandler):
    """指標收集回調處理器"""

    def __init__(self):
        self.metrics = Metrics()
        self._start_times: Dict[str, float] = {}

    def on_llm_start(self, serialized, prompts, **kwargs):
        self._start_times["llm"] = time.time()

    def on_llm_end(self, response, **kwargs):
        self.metrics.llm_calls += 1
        if "llm" in self._start_times:
            self.metrics.total_time += time.time() - self._start_times["llm"]

        # 嘗試獲取 token 使用
        if hasattr(response, "llm_output") and response.llm_output:
            usage = response.llm_output.get("token_usage", {})
            self.metrics.total_tokens += usage.get("total_tokens", 0)

    def on_llm_error(self, error, **kwargs):
        self.metrics.errors += 1

    def on_chain_start(self, serialized, inputs, **kwargs):
        self._start_times["chain"] = time.time()

    def on_chain_end(self, outputs, **kwargs):
        self.metrics.chain_calls += 1

    def on_tool_start(self, serialized, input_str, **kwargs):
        pass

    def on_tool_end(self, output, **kwargs):
        self.metrics.tool_calls += 1

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "llm_calls": self.metrics.llm_calls,
            "chain_calls": self.metrics.chain_calls,
            "tool_calls": self.metrics.tool_calls,
            "total_tokens": self.metrics.total_tokens,
            "total_time": f"{self.metrics.total_time:.2f}s",
            "errors": self.metrics.errors,
            "avg_time_per_call": f"{self.metrics.total_time / max(self.metrics.llm_calls, 1):.2f}s"
        }


# ============================================================
# 5. 流式回調處理器
# ============================================================

class StreamingCallbackHandler(BaseCallbackHandler):
    """流式輸出回調處理器"""

    def __init__(self, output_func=None):
        self.output_func = output_func or print
        self.tokens = []

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """新 token 生成時"""
        self.tokens.append(token)
        self.output_func(token, end="", flush=True)

    def on_llm_end(self, response, **kwargs) -> None:
        """結束時換行"""
        self.output_func("")  # 換行

    def get_full_response(self) -> str:
        """獲取完整回應"""
        return "".join(self.tokens)


STREAMING_EXAMPLE = '''
from langchain_openai import ChatOpenAI

# 流式回調
handler = StreamingCallbackHandler()

llm = ChatOpenAI(
    streaming=True,
    callbacks=[handler]
)

# 調用（會實時輸出 tokens）
response = llm.invoke("寫一首短詩")

# 獲取完整回應
full_text = handler.get_full_response()
'''


# ============================================================
# 6. 異步回調處理器
# ============================================================

ASYNC_CALLBACK_EXAMPLE = '''
from langchain.callbacks.base import AsyncCallbackHandler
import asyncio

class AsyncLoggingHandler(AsyncCallbackHandler):
    """異步日誌處理器"""

    async def on_llm_start(self, serialized, prompts, **kwargs):
        print(f"[Async] LLM 開始")

    async def on_llm_end(self, response, **kwargs):
        print(f"[Async] LLM 結束")

    async def on_llm_new_token(self, token, **kwargs):
        # 異步處理每個 token
        await asyncio.sleep(0)  # 讓出控制權
        print(token, end="", flush=True)

# 使用
async def main():
    handler = AsyncLoggingHandler()
    llm = ChatOpenAI(streaming=True, callbacks=[handler])

    response = await llm.ainvoke("Hello!")

asyncio.run(main())
'''


# ============================================================
# 7. 回調管理器
# ============================================================

class CallbackManager:
    """回調管理器"""

    def __init__(self):
        self.handlers: List[BaseCallbackHandler] = []

    def add_handler(self, handler: BaseCallbackHandler):
        """添加處理器"""
        self.handlers.append(handler)

    def remove_handler(self, handler: BaseCallbackHandler):
        """移除處理器"""
        self.handlers.remove(handler)

    def get_callbacks(self) -> List[BaseCallbackHandler]:
        """獲取所有回調"""
        return self.handlers

    def clear(self):
        """清除所有處理器"""
        self.handlers.clear()


CALLBACK_MANAGER_EXAMPLE = '''
# 使用回調管理器
manager = CallbackManager()

# 添加多個處理器
manager.add_handler(CustomCallbackHandler("Logger"))
manager.add_handler(MetricsCallbackHandler())
manager.add_handler(StreamingCallbackHandler())

# 創建 LLM 使用所有回調
llm = ChatOpenAI(
    streaming=True,
    callbacks=manager.get_callbacks()
)

response = llm.invoke("Hello!")
'''


# ============================================================
# 使用範例
# ============================================================

def example_builtin():
    """範例 1: 內置回調"""
    print("=" * 50)
    print("範例 1: 內置回調處理器")
    print("=" * 50)
    print(BUILTIN_CALLBACKS_EXAMPLE)


def example_custom():
    """範例 2: 自定義回調"""
    print("\n" + "=" * 50)
    print("範例 2: 自定義回調處理器")
    print("=" * 50)
    print(CUSTOM_CALLBACK_EXAMPLE)


def example_logging():
    """範例 3: 日誌回調"""
    print("\n" + "=" * 50)
    print("範例 3: 日誌回調處理器")
    print("=" * 50)

    handler = LoggingCallbackHandler()
    print(f"日誌文件: {handler.log_file}")
    print("方法: on_llm_start, on_llm_end, on_chain_start, on_chain_end")


def example_metrics():
    """範例 4: 指標收集"""
    print("\n" + "=" * 50)
    print("範例 4: 指標收集回調")
    print("=" * 50)

    handler = MetricsCallbackHandler()

    # 模擬一些調用
    handler.on_llm_start({}, ["test"])
    handler.on_llm_end(None)
    handler.on_chain_start({}, {})
    handler.on_chain_end({})

    print(f"指標: {handler.get_metrics()}")


def example_streaming():
    """範例 5: 流式回調"""
    print("\n" + "=" * 50)
    print("範例 5: 流式回調處理器")
    print("=" * 50)
    print(STREAMING_EXAMPLE)


def example_async():
    """範例 6: 異步回調"""
    print("\n" + "=" * 50)
    print("範例 6: 異步回調處理器")
    print("=" * 50)
    print(ASYNC_CALLBACK_EXAMPLE)


def example_manager():
    """範例 7: 回調管理器"""
    print("\n" + "=" * 50)
    print("範例 7: 回調管理器")
    print("=" * 50)
    print(CALLBACK_MANAGER_EXAMPLE)


if __name__ == "__main__":
    print("LangChain 自定義回調範例\n")
    example_builtin()
    example_custom()
    example_logging()
    example_metrics()
    example_streaming()
    example_async()
    example_manager()
