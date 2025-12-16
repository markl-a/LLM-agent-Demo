"""
Dify Agent 應用範例
==================

本範例展示如何使用 Dify 構建 Agent（自主代理）應用。

Agent 特點：
1. 自主規劃和執行任務
2. 工具調用能力
3. 推理過程可視化
4. ReAct 推理模式

安裝依賴：
pip install requests
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List, Generator
from dataclasses import dataclass
from enum import Enum

# ============================================================
# 配置
# ============================================================

DIFY_API_KEY = os.getenv("DIFY_API_KEY", "app-xxxxxxxxxxxxxxxx")
DIFY_BASE_URL = os.getenv("DIFY_BASE_URL", "https://api.dify.ai/v1")


# ============================================================
# Agent 類型枚舉
# ============================================================

class AgentMode(Enum):
    """Agent 模式"""
    FUNCTION_CALL = "function_call"  # 函數調用模式
    REACT = "react"  # ReAct 推理模式


class ToolType(Enum):
    """工具類型"""
    BUILTIN = "builtin"  # 內建工具
    API = "api"  # API 工具
    WORKFLOW = "workflow"  # 工作流工具


# ============================================================
# Agent 客戶端
# ============================================================

class DifyAgentClient:
    """
    Dify Agent API 客戶端

    提供 Agent 應用的完整功能
    """

    def __init__(self, api_key: str, base_url: str = "https://api.dify.ai/v1"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def run_agent(
        self,
        query: str,
        user: str,
        conversation_id: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
        response_mode: str = "blocking"
    ) -> Dict[str, Any]:
        """
        執行 Agent

        Args:
            query: 用戶查詢
            user: 用戶標識
            conversation_id: 對話 ID
            inputs: 輸入變數
            response_mode: 響應模式

        Returns:
            Agent 執行結果
        """
        url = f"{self.base_url}/chat-messages"

        payload = {
            "query": query,
            "user": user,
            "response_mode": response_mode,
            "inputs": inputs or {}
        }

        if conversation_id:
            payload["conversation_id"] = conversation_id

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()

        return response.json()

    def run_agent_stream(
        self,
        query: str,
        user: str,
        conversation_id: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        流式執行 Agent

        可以觀察 Agent 的思考和執行過程

        Args:
            query: 用戶查詢
            user: 用戶標識
            conversation_id: 對話 ID
            inputs: 輸入變數

        Yields:
            流式事件
        """
        url = f"{self.base_url}/chat-messages"

        payload = {
            "query": query,
            "user": user,
            "response_mode": "streaming",
            "inputs": inputs or {}
        }

        if conversation_id:
            payload["conversation_id"] = conversation_id

        response = requests.post(
            url,
            headers=self.headers,
            json=payload,
            stream=True
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    try:
                        yield json.loads(line[6:])
                    except json.JSONDecodeError:
                        continue

    def get_agent_logs(
        self,
        conversation_id: str,
        message_id: str,
        user: str
    ) -> Dict[str, Any]:
        """
        獲取 Agent 執行日誌

        Args:
            conversation_id: 對話 ID
            message_id: 消息 ID
            user: 用戶標識

        Returns:
            執行日誌
        """
        url = f"{self.base_url}/messages/{message_id}/agent-logs"

        params = {
            "conversation_id": conversation_id,
            "user": user
        }

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        return response.json()


# ============================================================
# Agent 執行追蹤器
# ============================================================

@dataclass
class ToolCall:
    """工具調用記錄"""
    tool_name: str
    tool_input: Dict[str, Any]
    tool_output: str
    status: str


@dataclass
class ThoughtStep:
    """思考步驟"""
    thought: str
    action: Optional[str] = None
    action_input: Optional[Dict[str, Any]] = None
    observation: Optional[str] = None


class AgentExecutionTracker:
    """
    Agent 執行追蹤器

    追蹤和記錄 Agent 的執行過程
    """

    def __init__(self):
        self.thoughts: List[ThoughtStep] = []
        self.tool_calls: List[ToolCall] = []
        self.final_answer: str = ""
        self.total_tokens: int = 0
        self.execution_time: float = 0

    def track_stream(
        self,
        event_stream: Generator[Dict[str, Any], None, None]
    ) -> str:
        """
        追蹤流式執行

        Args:
            event_stream: 事件流

        Returns:
            最終答案
        """
        import time
        start_time = time.time()

        current_thought = ""
        answer_parts = []

        for event in event_stream:
            event_type = event.get('event')

            if event_type == 'agent_thought':
                # Agent 思考過程
                thought_data = event.get('data', {})
                current_thought = thought_data.get('thought', '')
                print(f"\n[思考] {current_thought}")

                self.thoughts.append(ThoughtStep(thought=current_thought))

            elif event_type == 'agent_action':
                # Agent 執行動作
                action_data = event.get('data', {})
                action = action_data.get('action', '')
                action_input = action_data.get('action_input', {})
                print(f"[動作] {action}: {action_input}")

                if self.thoughts:
                    self.thoughts[-1].action = action
                    self.thoughts[-1].action_input = action_input

            elif event_type == 'tool_call':
                # 工具調用
                tool_data = event.get('data', {})
                tool_name = tool_data.get('tool_name', '')
                tool_input = tool_data.get('tool_input', {})
                print(f"[工具調用] {tool_name}")

                self.tool_calls.append(ToolCall(
                    tool_name=tool_name,
                    tool_input=tool_input,
                    tool_output="",
                    status="running"
                ))

            elif event_type == 'tool_output':
                # 工具輸出
                output_data = event.get('data', {})
                tool_output = output_data.get('output', '')
                print(f"[工具輸出] {tool_output[:100]}...")

                if self.tool_calls:
                    self.tool_calls[-1].tool_output = tool_output
                    self.tool_calls[-1].status = "completed"

                if self.thoughts:
                    self.thoughts[-1].observation = tool_output

            elif event_type == 'message':
                # 最終答案
                answer = event.get('answer', '')
                answer_parts.append(answer)
                print(answer, end="", flush=True)

            elif event_type == 'message_end':
                # 執行結束
                metadata = event.get('metadata', {})
                self.total_tokens = metadata.get('usage', {}).get('total_tokens', 0)

        self.final_answer = ''.join(answer_parts)
        self.execution_time = time.time() - start_time

        print(f"\n\n[執行完成] 耗時: {self.execution_time:.2f}s, Tokens: {self.total_tokens}")

        return self.final_answer

    def get_summary(self) -> Dict[str, Any]:
        """獲取執行摘要"""
        return {
            "total_thoughts": len(self.thoughts),
            "total_tool_calls": len(self.tool_calls),
            "execution_time": self.execution_time,
            "total_tokens": self.total_tokens,
            "final_answer": self.final_answer[:200] + "..." if len(self.final_answer) > 200 else self.final_answer
        }


# ============================================================
# 使用範例
# ============================================================

def example_basic_agent():
    """
    範例 1: 基礎 Agent 調用

    展示簡單的 Agent 執行
    """
    print("=" * 50)
    print("範例 1: 基礎 Agent 調用")
    print("=" * 50)

    client = DifyAgentClient(api_key=DIFY_API_KEY, base_url=DIFY_BASE_URL)

    try:
        result = client.run_agent(
            query="幫我查詢今天北京的天氣",
            user="user-001"
        )

        print(f"回答: {result.get('answer', '')}")

        # 查看 Agent 的執行過程
        metadata = result.get('metadata', {})
        if 'agent_thoughts' in metadata:
            print("\nAgent 思考過程:")
            for thought in metadata['agent_thoughts']:
                print(f"  - {thought.get('thought', '')}")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_agent_with_tools():
    """
    範例 2: 使用工具的 Agent

    展示 Agent 調用工具完成任務
    """
    print("\n" + "=" * 50)
    print("範例 2: 使用工具的 Agent")
    print("=" * 50)

    client = DifyAgentClient(api_key=DIFY_API_KEY, base_url=DIFY_BASE_URL)

    try:
        # 執行需要工具的任務
        result = client.run_agent(
            query="搜索最近的人工智能新聞，並總結主要內容",
            user="user-002",
            inputs={
                "max_results": 5
            }
        )

        print(f"回答: {result.get('answer', '')}")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_streaming_agent():
    """
    範例 3: 流式 Agent 執行

    實時觀察 Agent 的思考和執行過程
    """
    print("\n" + "=" * 50)
    print("範例 3: 流式 Agent 執行")
    print("=" * 50)

    client = DifyAgentClient(api_key=DIFY_API_KEY, base_url=DIFY_BASE_URL)
    tracker = AgentExecutionTracker()

    try:
        event_stream = client.run_agent_stream(
            query="分析一下蘋果公司最近的股票走勢，並給出投資建議",
            user="user-003"
        )

        final_answer = tracker.track_stream(event_stream)

        print("\n執行摘要:")
        print(json.dumps(tracker.get_summary(), indent=2, ensure_ascii=False))

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_multi_step_agent():
    """
    範例 4: 多步驟任務

    展示 Agent 完成複雜的多步驟任務
    """
    print("\n" + "=" * 50)
    print("範例 4: 多步驟任務")
    print("=" * 50)

    client = DifyAgentClient(api_key=DIFY_API_KEY, base_url=DIFY_BASE_URL)

    complex_task = """
    請幫我完成以下任務：
    1. 搜索最近一周的科技新聞
    2. 從中找出與 AI 相關的新聞
    3. 總結這些新聞的主要趨勢
    4. 預測未來可能的發展方向
    """

    try:
        print(f"任務: {complex_task}")
        print("\nAgent 執行中...")

        for event in client.run_agent_stream(
            query=complex_task,
            user="user-004"
        ):
            event_type = event.get('event')

            if event_type == 'agent_thought':
                print(f"\n[思考] {event.get('data', {}).get('thought', '')}")

            elif event_type == 'tool_call':
                print(f"[工具] {event.get('data', {}).get('tool_name', '')}")

            elif event_type == 'message':
                print(event.get('answer', ''), end="", flush=True)

        print()

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_agent_with_context():
    """
    範例 5: 帶上下文的 Agent

    展示在多輪對話中使用 Agent
    """
    print("\n" + "=" * 50)
    print("範例 5: 帶上下文的 Agent")
    print("=" * 50)

    client = DifyAgentClient(api_key=DIFY_API_KEY, base_url=DIFY_BASE_URL)
    user = "user-005"

    try:
        # 第一輪：建立上下文
        result1 = client.run_agent(
            query="我正在研究自然語言處理技術",
            user=user
        )

        conv_id = result1.get('conversation_id')
        print(f"第一輪: {result1.get('answer', '')[:100]}...")

        # 第二輪：基於上下文繼續
        result2 = client.run_agent(
            query="幫我找一些相關的最新論文",
            user=user,
            conversation_id=conv_id
        )

        print(f"\n第二輪: {result2.get('answer', '')[:100]}...")

        # 第三輪：進一步深入
        result3 = client.run_agent(
            query="這些論文中哪個最有影響力？",
            user=user,
            conversation_id=conv_id
        )

        print(f"\n第三輪: {result3.get('answer', '')[:100]}...")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_code_interpreter_agent():
    """
    範例 6: 代碼解釋器 Agent

    展示 Agent 執行代碼的能力
    """
    print("\n" + "=" * 50)
    print("範例 6: 代碼解釋器 Agent")
    print("=" * 50)

    client = DifyAgentClient(api_key=DIFY_API_KEY, base_url=DIFY_BASE_URL)

    code_task = """
    請幫我用 Python 完成以下任務：
    1. 生成 1 到 100 的斐波那契數列
    2. 計算這些數的平均值
    3. 找出最大的 3 個數
    """

    try:
        print(f"任務: {code_task}")
        print("\nAgent 執行中...")

        for event in client.run_agent_stream(
            query=code_task,
            user="user-006"
        ):
            event_type = event.get('event')

            if event_type == 'tool_call':
                tool_name = event.get('data', {}).get('tool_name', '')
                if 'code' in tool_name.lower():
                    print(f"\n[執行代碼]")

            elif event_type == 'tool_output':
                output = event.get('data', {}).get('output', '')
                print(f"[代碼輸出]\n{output[:500]}")

            elif event_type == 'message':
                print(event.get('answer', ''), end="", flush=True)

        print()

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_research_agent():
    """
    範例 7: 研究型 Agent

    展示 Agent 進行深度研究的能力
    """
    print("\n" + "=" * 50)
    print("範例 7: 研究型 Agent")
    print("=" * 50)

    client = DifyAgentClient(api_key=DIFY_API_KEY, base_url=DIFY_BASE_URL)

    research_query = """
    請對「大型語言模型的安全性問題」進行深入研究：
    1. 列出主要的安全風險
    2. 搜索相關的學術研究
    3. 總結業界的應對措施
    4. 提出改進建議
    """

    try:
        print(f"研究主題: {research_query}")
        print("\nAgent 研究中...")

        tracker = AgentExecutionTracker()

        event_stream = client.run_agent_stream(
            query=research_query,
            user="user-007"
        )

        tracker.track_stream(event_stream)

        print("\n研究完成！")
        print(f"- 思考步驟: {len(tracker.thoughts)}")
        print(f"- 工具調用: {len(tracker.tool_calls)}")
        print(f"- 執行時間: {tracker.execution_time:.2f}s")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    print("Dify Agent 應用範例")
    print("請確保已設置 DIFY_API_KEY 環境變數")
    print()

    example_basic_agent()
    example_agent_with_tools()
    example_streaming_agent()
    example_multi_step_agent()
    example_agent_with_context()
    example_code_interpreter_agent()
    example_research_agent()
