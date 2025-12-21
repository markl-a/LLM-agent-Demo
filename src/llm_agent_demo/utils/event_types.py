"""事件類型定義 - 定義事件類型和優先級枚舉"""

from enum import Enum


class EventType(str, Enum):
    """內建事件類型枚舉"""

    # API 相關事件
    API_CALL = "api_call"
    API_SUCCESS = "api_success"
    API_ERROR = "api_error"
    API_RETRY = "api_retry"

    # 成本追蹤事件
    COST_TRACKED = "cost_tracked"
    COST_LIMIT_WARNING = "cost_limit_warning"
    COST_LIMIT_EXCEEDED = "cost_limit_exceeded"

    # 錯誤事件
    ERROR = "error"
    WARNING = "warning"
    CRITICAL = "critical"

    # Agent 相關事件
    AGENT_START = "agent_start"
    AGENT_STEP = "agent_step"
    AGENT_COMPLETE = "agent_complete"
    AGENT_ERROR = "agent_error"

    # 工具執行事件
    TOOL_START = "tool_start"
    TOOL_COMPLETE = "tool_complete"
    TOOL_ERROR = "tool_error"

    # 數據事件
    DATA_LOADED = "data_loaded"
    DATA_SAVED = "data_saved"
    DATA_ERROR = "data_error"

    # 自定義事件
    CUSTOM = "custom"

    def __str__(self) -> str:
        """返回枚舉值作為字符串"""
        return self.value


class EventPriority(int, Enum):
    """事件優先級"""

    LOWEST = 0
    LOW = 1
    NORMAL = 2
    HIGH = 3
    HIGHEST = 4


__all__ = ["EventType", "EventPriority"]
