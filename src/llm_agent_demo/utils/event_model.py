"""事件數據模型 - 定義事件和監聽器數據類"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Coroutine, Dict, Optional, Union
from uuid import uuid4

from .event_types import EventPriority, EventType


@dataclass
class Event:
    """事件對象"""

    type: Union[EventType, str]
    data: Any = None
    timestamp: datetime = field(default_factory=datetime.now)
    event_id: str = field(default_factory=lambda: str(uuid4()))
    source: Optional[str] = None
    priority: EventPriority = EventPriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "type": str(self.type),
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "event_id": self.event_id,
            "source": self.source,
            "priority": self.priority.value,
            "metadata": self.metadata,
        }

    def __str__(self) -> str:
        return f"Event({self.type}, id={self.event_id[:8]}, priority={self.priority.name})"


@dataclass
class EventListener:
    """事件監聽器"""

    callback: Union[Callable[[Event], None], Callable[[Event], Coroutine]]
    priority: EventPriority = EventPriority.NORMAL
    once: bool = False  # 是否只執行一次
    filter_func: Optional[Callable[[Event], bool]] = None  # 事件過濾函數
    listener_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    is_async: bool = False

    def should_handle(self, event: Event) -> bool:
        """判斷是否應該處理此事件"""
        if self.filter_func:
            return self.filter_func(event)
        return True

    def __str__(self) -> str:
        return f"EventListener(id={self.listener_id[:8]}, priority={self.priority.name}, once={self.once})"


__all__ = ["Event", "EventListener"]
