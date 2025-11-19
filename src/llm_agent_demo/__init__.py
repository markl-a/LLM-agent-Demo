"""
LLM Agent Demo - 多框架 LLM Agent 開發教學庫

本模組提供了多個主流 LLM Agent 框架的實用工具和範例實現。

支援的框架：
- LangChain: 建立 RAG、Agent 和鏈式應用
- LlamaIndex: 高效的索引和查詢引擎
- AutoGen: 多 Agent 對話系統
- CrewAI: 團隊協作式 AI Agent
- MetaGPT: 軟體開發 Agent 系統

主要功能：
- 向量存儲和檢索
- RAG（檢索增強生成）
- Agent 工具和鏈
- 成本追蹤和監控
- 配置管理
"""

__version__ = "2.0.0"
__author__ = "markl-a"
__license__ = "MIT"

from typing import Optional

# 可選導入，避免強制依賴
try:
    from .utils.config import Settings, get_settings
    from .utils.logger import get_logger
    from .utils.cost_tracker import CostTracker
except ImportError:
    Settings = None
    get_settings = None
    get_logger = None
    CostTracker = None

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "Settings",
    "get_settings",
    "get_logger",
    "CostTracker",
]
