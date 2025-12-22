"""事件統計 - 事件系統統計信息"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class EventStats:
    """事件統計信息"""

    total_emitted: int = 0
    total_handled: int = 0
    total_errors: int = 0
    events_by_type: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    handlers_by_type: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    last_event_time: Optional[datetime] = None
    average_handler_time: float = 0.0
    _handler_times: List[float] = field(default_factory=list, repr=False)

    def record_event(self, event_type: str) -> None:
        """記錄事件發射"""
        self.total_emitted += 1
        self.events_by_type[event_type] += 1
        self.last_event_time = datetime.now()

    def record_handle(self, event_type: str, duration: float) -> None:
        """記錄事件處理"""
        self.total_handled += 1
        self._handler_times.append(duration)
        # 保持最近 1000 次的平均值
        if len(self._handler_times) > 1000:
            self._handler_times.pop(0)
        self.average_handler_time = sum(self._handler_times) / len(self._handler_times)

    def record_error(self) -> None:
        """記錄錯誤"""
        self.total_errors += 1

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "total_emitted": self.total_emitted,
            "total_handled": self.total_handled,
            "total_errors": self.total_errors,
            "events_by_type": dict(self.events_by_type),
            "handlers_by_type": dict(self.handlers_by_type),
            "last_event_time": self.last_event_time.isoformat()
            if self.last_event_time
            else None,
            "average_handler_time": self.average_handler_time,
        }


__all__ = ["EventStats"]
