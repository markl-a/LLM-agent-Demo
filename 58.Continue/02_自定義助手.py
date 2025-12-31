"""
Continue AI 編程助手 - 自定義助手開發

這個文件展示了如何創建和配置自定義 AI 助手。
自定義助手可以針對特定任務、領域或團隊需求進行優化。

主要內容:
1. 自定義助手基類
2. 專業領域助手(Python、前端、後端等)
3. 任務特定助手(代碼審查、測試、重構等)
4. 團隊助手配置
5. 助手行為定制
6. 知識庫集成
7. 多助手協作

Author: Continue Team
Date: 2025
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import re


# =====================================================
# 第一部分: 助手基礎類型定義
# =====================================================

class AssistantType(Enum):
    """
    助手類型枚舉

    定義不同類型的助手
    """
    GENERAL = "general"  # 通用助手
    CODE_REVIEW = "code_review"  # 代碼審查
    TESTING = "testing"  # 測試專家
    DEBUGGING = "debugging"  # 調試專家
    REFACTORING = "refactoring"  # 重構專家
    DOCUMENTATION = "documentation"  # 文檔編寫
    SECURITY = "security"  # 安全審計
    PERFORMANCE = "performance"  # 性能優化
    ARCHITECTURE = "architecture"  # 架構設計
    LANGUAGE_SPECIFIC = "language_specific"  # 特定語言


class SkillLevel(Enum):
    """
    技能等級

    定義助手的專業程度
    """
    BEGINNER = "beginner"  # 初級
    INTERMEDIATE = "intermediate"  # 中級
    ADVANCED = "advanced"  # 高級
    EXPERT = "expert"  # 專家


@dataclass
class AssistantCapability:
    """
    助手能力定義

    描述助手具備的特定能力
    """
    name: str  # 能力名稱
    description: str  # 能力描述
    skill_level: SkillLevel  # 技能等級
    examples: List[str] = field(default_factory=list)  # 使用示例


@dataclass
class AssistantPersonality:
    """
    助手個性設置

    定義助手的回答風格和個性特徵
    """
    tone: str = "professional"  # 語氣(專業/友好/嚴肅等)
    verbosity: str = "balanced"  # 詳細程度(簡潔/平衡/詳細)
    formality: str = "semi-formal"  # 正式程度
    teaching_style: str = "explanatory"  # 教學風格
    code_style: str = "clean"  # 代碼風格偏好


# =====================================================
# 第二部分: 自定義助手基類
# =====================================================

class CustomAssistant(ABC):
    """
    自定義助手抽象基類

    所有自定義助手都應繼承此類並實現必要的方法
    """

    def __init__(
        self,
        name: str,
        description: str,
        assistant_type: AssistantType,
        model: str = "gpt-4",
        personality: Optional[AssistantPersonality] = None
    ):
        """
        初始化自定義助手

        Args:
            name: 助手名稱
            description: 助手描述
            assistant_type: 助手類型
            model: 使用的 AI 模型
            personality: 助手個性設置
        """
        self.name = name
        self.description = description
        self.assistant_type = assistant_type
        self.model = model
        self.personality = personality or AssistantPersonality()
        self.capabilities: List[AssistantCapability] = []
        self.knowledge_base: Dict[str, Any] = {}
        self.conversation_history: List[Dict[str, str]] = []

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        獲取系統提示詞

        這是定義助手行為的核心方法

        Returns:
            系統提示詞字符串
        """
        pass

    @abstractmethod
    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        處理用戶查詢

        Args:
            query: 用戶查詢
            context: 上下文信息

        Returns:
            助手回覆
        """
        pass

    def add_capability(self, capability: AssistantCapability):
        """
        添加助手能力

        Args:
            capability: 能力對象
        """
        self.capabilities.append(capability)
        print(f"已為 {self.name} 添加能力: {capability.name}")

    def add_knowledge(self, key: str, value: Any):
        """
        添加知識到知識庫

        Args:
            key: 知識鍵
            value: 知識內容
        """
        self.knowledge_base[key] = value
        print(f"已添加知識: {key}")

    def get_capabilities_description(self) -> str:
        """
        獲取能力描述

        Returns:
            能力描述字符串
        """
        if not self.capabilities:
            return "暫無特定能力定義"

        desc = "我具備以下能力:\n"
        for cap in self.capabilities:
            desc += f"- {cap.name} ({cap.skill_level.value}): {cap.description}\n"
        return desc

    def format_response(self, content: str) -> str:
        """
        根據個性設置格式化回覆

        Args:
            content: 原始回覆內容

        Returns:
            格式化後的回覆
        """
        # 根據詳細程度調整
        if self.personality.verbosity == "concise":
            # 簡化回覆
            content = self._make_concise(content)
        elif self.personality.verbosity == "detailed":
            # 增加詳細說明
            content = self._add_details(content)

        return content

    def _make_concise(self, content: str) -> str:
        """使回覆更簡潔"""
        # 實際實現會更複雜
        return content

    def _add_details(self, content: str) -> str:
        """添加更多細節"""
        # 實際實現會更複雜
        return content


# =====================================================
# 第三部分: 語言特定助手
# =====================================================

class PythonExpert(CustomAssistant):
    """
    Python 專家助手

    專注於 Python 開發的各個方面
    """

    def __init__(self):
        super().__init__(
            name="Python 專家",
            description="精通 Python 開發的 AI 助手",
            assistant_type=AssistantType.LANGUAGE_SPECIFIC,
            model="gpt-4"
        )

        # 添加 Python 相關能力
        self._setup_capabilities()

        # 添加 Python 知識
        self._setup_knowledge_base()

    def _setup_capabilities(self):
        """設置 Python 專家能力"""
        capabilities = [
            AssistantCapability(
                name="代碼編寫",
                description="編寫高質量、符合 PEP 8 規範的 Python 代碼",
                skill_level=SkillLevel.EXPERT,
                examples=["編寫類", "實現算法", "創建裝飾器"]
            ),
            AssistantCapability(
                name="性能優化",
                description="優化 Python 代碼性能,使用適當的數據結構和算法",
                skill_level=SkillLevel.EXPERT,
                examples=["使用生成器", "優化循環", "並發處理"]
            ),
            AssistantCapability(
                name="異步編程",
                description="熟練使用 asyncio 和異步編程模式",
                skill_level=SkillLevel.ADVANCED,
                examples=["async/await", "事件循環", "並發任務"]
            ),
            AssistantCapability(
                name="測試驅動開發",
                description="編寫全面的單元測試和集成測試",
                skill_level=SkillLevel.EXPERT,
                examples=["pytest", "unittest", "測試覆蓋率"]
            )
        ]

        for cap in capabilities:
            self.add_capability(cap)

    def _setup_knowledge_base(self):
        """設置 Python 知識庫"""
        self.add_knowledge("best_practices", {
            "naming": "使用 snake_case 命名變量和函數",
            "imports": "按標準庫、第三方庫、本地模塊順序組織導入",
            "docstrings": "使用 Google 或 NumPy 風格的文檔字符串",
            "type_hints": "使用類型註解提高代碼可讀性"
        })

        self.add_knowledge("common_patterns", {
            "context_manager": "使用 with 語句管理資源",
            "comprehension": "優先使用列表/字典推導式",
            "generator": "對大數據集使用生成器",
            "decorator": "使用裝飾器增強函數功能"
        })

    def get_system_prompt(self) -> str:
        """獲取 Python 專家系統提示詞"""
        return f"""你是一位 Python 編程專家,擁有以下特質:

{self.get_capabilities_description()}

最佳實踐:
- 始終遵循 PEP 8 代碼規範
- 使用類型註解提高代碼質量
- 編寫清晰的文檔字符串
- 優先考慮代碼可讀性和可維護性
- 適當使用 Python 特性(生成器、上下文管理器等)

回答風格:
- 提供完整、可運行的代碼示例
- 解釋代碼背後的原理
- 指出潛在的問題和改進空間
- 給出最佳實踐建議

請以專業、友好的方式幫助用戶解決 Python 相關問題。
"""

    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """處理 Python 相關查詢"""
        # 分析查詢類型
        query_lower = query.lower()

        if "優化" in query or "性能" in query:
            return self._handle_optimization_query(query, context)
        elif "測試" in query:
            return self._handle_testing_query(query, context)
        elif "異步" in query or "async" in query:
            return self._handle_async_query(query, context)
        else:
            return self._handle_general_query(query, context)

    def _handle_optimization_query(self, query: str, context: Optional[Dict[str, Any]]) -> str:
        """處理優化相關查詢"""
        response = f"[Python 性能優化建議]\n\n"
        response += "讓我幫你分析代碼性能並提供優化建議...\n"
        return response

    def _handle_testing_query(self, query: str, context: Optional[Dict[str, Any]]) -> str:
        """處理測試相關查詢"""
        response = f"[Python 測試建議]\n\n"
        response += "我會幫你編寫全面的測試代碼...\n"
        return response

    def _handle_async_query(self, query: str, context: Optional[Dict[str, Any]]) -> str:
        """處理異步編程查詢"""
        response = f"[Python 異步編程]\n\n"
        response += "讓我解釋異步編程的概念和最佳實踐...\n"
        return response

    def _handle_general_query(self, query: str, context: Optional[Dict[str, Any]]) -> str:
        """處理一般查詢"""
        response = f"[Python 專家回覆]\n\n"
        response += f"查詢: {query}\n"
        return response


class JavaScriptExpert(CustomAssistant):
    """
    JavaScript/TypeScript 專家助手
    """

    def __init__(self):
        super().__init__(
            name="JavaScript 專家",
            description="精通 JavaScript/TypeScript 和前端開發",
            assistant_type=AssistantType.LANGUAGE_SPECIFIC,
            model="gpt-4"
        )
        self._setup_capabilities()

    def _setup_capabilities(self):
        """設置 JavaScript 專家能力"""
        capabilities = [
            AssistantCapability(
                name="現代 JavaScript",
                description="ES6+ 特性,包括 async/await、解構、箭頭函數等",
                skill_level=SkillLevel.EXPERT
            ),
            AssistantCapability(
                name="TypeScript",
                description="類型系統、接口、泛型等高級特性",
                skill_level=SkillLevel.EXPERT
            ),
            AssistantCapability(
                name="React/Vue/Angular",
                description="主流前端框架的最佳實踐",
                skill_level=SkillLevel.ADVANCED
            ),
            AssistantCapability(
                name="Node.js",
                description="後端 JavaScript 開發",
                skill_level=SkillLevel.ADVANCED
            )
        ]

        for cap in capabilities:
            self.add_capability(cap)

    def get_system_prompt(self) -> str:
        """獲取 JavaScript 專家系統提示詞"""
        return f"""你是一位 JavaScript/TypeScript 專家,精通:

{self.get_capabilities_description()}

專長領域:
- 現代 JavaScript (ES6+)
- TypeScript 類型系統
- React、Vue、Angular 等前端框架
- Node.js 後端開發
- 異步編程和 Promise
- 前端性能優化
- 工具鏈配置 (Webpack, Vite 等)

請提供清晰、現代的 JavaScript 解決方案。
"""

    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """處理 JavaScript 相關查詢"""
        response = f"[JavaScript 專家回覆]\n\n"
        response += f"處理查詢: {query}\n"
        return response


# =====================================================
# 第四部分: 任務特定助手
# =====================================================

class CodeReviewAssistant(CustomAssistant):
    """
    代碼審查助手

    專門用於代碼審查和質量檢查
    """

    def __init__(self):
        super().__init__(
            name="代碼審查專家",
            description="專業的代碼審查和質量檢查助手",
            assistant_type=AssistantType.CODE_REVIEW,
            model="gpt-4"
        )

        # 設置審查標準
        self.review_criteria = {
            "correctness": "代碼邏輯正確性",
            "readability": "代碼可讀性",
            "maintainability": "可維護性",
            "performance": "性能",
            "security": "安全性",
            "testing": "測試覆蓋率",
            "documentation": "文檔完整性"
        }

    def get_system_prompt(self) -> str:
        """獲取代碼審查系統提示詞"""
        return """你是一位資深的代碼審查專家,負責:

1. 檢查代碼質量和規範性
2. 發現潛在的 bug 和問題
3. 提供改進建議
4. 確保代碼安全性
5. 評估代碼性能

審查標準:
- 代碼邏輯是否正確
- 是否遵循最佳實踐
- 代碼可讀性和可維護性
- 潛在的性能問題
- 安全漏洞
- 錯誤處理是否完善
- 測試覆蓋是否充分

請提供詳細、建設性的審查意見。
"""

    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """處理代碼審查請求"""
        if context and "code" in context:
            return self.review_code(context["code"])
        return "請提供需要審查的代碼"

    def review_code(self, code: str) -> str:
        """
        審查代碼

        Args:
            code: 待審查的代碼

        Returns:
            審查報告
        """
        report = "=== 代碼審查報告 ===\n\n"

        # 檢查各個方面
        for criterion, description in self.review_criteria.items():
            report += f"【{description}】\n"
            report += f"  評分: 待評估\n"
            report += f"  建議: ...\n\n"

        report += "=== 總體評價 ===\n"
        report += "代碼整體質量良好,建議按以上意見進行改進。\n"

        return report


class TestingAssistant(CustomAssistant):
    """
    測試專家助手

    專門幫助編寫和優化測試代碼
    """

    def __init__(self):
        super().__init__(
            name="測試專家",
            description="專注於測試驅動開發和測試優化",
            assistant_type=AssistantType.TESTING,
            model="gpt-4"
        )

    def get_system_prompt(self) -> str:
        """獲取測試專家系統提示詞"""
        return """你是一位測試專家,擅長:

1. 單元測試設計
2. 集成測試
3. 端到端測試
4. 測試覆蓋率優化
5. 測試框架使用 (pytest, jest, mocha 等)
6. Mock 和 Stub 技巧
7. TDD/BDD 實踐

測試原則:
- 測試應該獨立且可重複
- 測試應該快速執行
- 測試應該易於理解
- 覆蓋邊界情況和異常情況
- 使用有意義的測試名稱

請幫助用戶編寫高質量的測試代碼。
"""

    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """處理測試相關查詢"""
        response = "[測試專家]\n\n"

        if context and "code" in context:
            response += self.generate_tests(context["code"])
        else:
            response += "請提供需要測試的代碼"

        return response

    def generate_tests(self, code: str) -> str:
        """
        生成測試代碼

        Args:
            code: 待測試的代碼

        Returns:
            測試代碼
        """
        tests = "# 生成的測試代碼\n\n"
        tests += "import pytest\n\n"
        tests += "# TODO: 根據代碼生成具體測試\n"
        return tests


class RefactoringAssistant(CustomAssistant):
    """
    重構專家助手

    幫助進行代碼重構和優化
    """

    def __init__(self):
        super().__init__(
            name="重構專家",
            description="專注於代碼重構和架構改進",
            assistant_type=AssistantType.REFACTORING,
            model="gpt-4"
        )

        # 重構模式
        self.refactoring_patterns = {
            "extract_method": "提取方法",
            "extract_class": "提取類",
            "inline": "內聯",
            "move_method": "移動方法",
            "rename": "重命名",
            "simplify": "簡化條件"
        }

    def get_system_prompt(self) -> str:
        """獲取重構專家系統提示詞"""
        return """你是一位代碼重構專家,擅長:

1. 識別代碼異味 (Code Smells)
2. 應用重構模式
3. 改善代碼結構
4. 提高代碼可讀性
5. 優化設計模式應用

重構原則:
- 小步快跑,每次改進一點
- 保持測試通過
- 不改變外部行為
- 提高代碼可讀性和可維護性

常用重構技巧:
- 提取方法/類
- 消除重複代碼
- 簡化複雜條件
- 引入設計模式
- 優化命名

請幫助用戶改善代碼質量。
"""

    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """處理重構相關查詢"""
        response = "[重構專家]\n\n"

        if context and "code" in context:
            response += self.suggest_refactoring(context["code"])
        else:
            response += "請提供需要重構的代碼"

        return response

    def suggest_refactoring(self, code: str) -> str:
        """
        提供重構建議

        Args:
            code: 待重構的代碼

        Returns:
            重構建議
        """
        suggestions = "重構建議:\n\n"

        # 檢測代碼異味
        suggestions += "1. 代碼異味檢測:\n"
        suggestions += "   - 方法過長\n"
        suggestions += "   - 類職責過多\n"
        suggestions += "   - 重複代碼\n\n"

        suggestions += "2. 建議的重構操作:\n"
        for pattern, desc in self.refactoring_patterns.items():
            suggestions += f"   - {desc}\n"

        return suggestions


# =====================================================
# 第五部分: 團隊助手管理
# =====================================================

class TeamAssistantManager:
    """
    團隊助手管理器

    管理團隊中的多個自定義助手
    """

    def __init__(self):
        """初始化團隊助手管理器"""
        self.assistants: Dict[str, CustomAssistant] = {}
        self.active_assistant: Optional[CustomAssistant] = None

    def register_assistant(self, assistant: CustomAssistant):
        """
        註冊助手

        Args:
            assistant: 自定義助手實例
        """
        self.assistants[assistant.name] = assistant
        print(f"已註冊助手: {assistant.name}")

        # 如果沒有活躍助手,設置為默認
        if not self.active_assistant:
            self.active_assistant = assistant

    def switch_assistant(self, name: str) -> bool:
        """
        切換當前助手

        Args:
            name: 助手名稱

        Returns:
            是否切換成功
        """
        if name in self.assistants:
            self.active_assistant = self.assistants[name]
            print(f"已切換到助手: {name}")
            return True
        else:
            print(f"未找到助手: {name}")
            return False

    def list_assistants(self) -> List[str]:
        """
        列出所有助手

        Returns:
            助手名稱列表
        """
        return list(self.assistants.keys())

    def get_assistant_info(self, name: str) -> Optional[str]:
        """
        獲取助手信息

        Args:
            name: 助手名稱

        Returns:
            助手信息
        """
        if name in self.assistants:
            assistant = self.assistants[name]
            info = f"助手名稱: {assistant.name}\n"
            info += f"描述: {assistant.description}\n"
            info += f"類型: {assistant.assistant_type.value}\n"
            info += f"模型: {assistant.model}\n"
            info += f"\n{assistant.get_capabilities_description()}"
            return info
        return None

    def route_query(self, query: str) -> str:
        """
        智能路由查詢到合適的助手

        Args:
            query: 用戶查詢

        Returns:
            助手回覆
        """
        # 分析查詢,選擇最合適的助手
        best_assistant = self._select_best_assistant(query)

        if best_assistant:
            print(f"使用助手: {best_assistant.name}")
            return best_assistant.process_query(query)
        else:
            return "未找到合適的助手處理此查詢"

    def _select_best_assistant(self, query: str) -> Optional[CustomAssistant]:
        """
        選擇最合適的助手

        Args:
            query: 用戶查詢

        Returns:
            選中的助手
        """
        query_lower = query.lower()

        # 簡單的關鍵詞匹配邏輯
        if "python" in query_lower:
            return self.assistants.get("Python 專家")
        elif "javascript" in query_lower or "typescript" in query_lower:
            return self.assistants.get("JavaScript 專家")
        elif "審查" in query or "review" in query_lower:
            return self.assistants.get("代碼審查專家")
        elif "測試" in query or "test" in query_lower:
            return self.assistants.get("測試專家")
        elif "重構" in query or "refactor" in query_lower:
            return self.assistants.get("重構專家")

        # 默認返回當前活躍助手
        return self.active_assistant


# =====================================================
# 第六部分: 使用示例
# =====================================================

def create_custom_assistants():
    """
    創建自定義助手示例
    """
    print("=" * 60)
    print("創建自定義助手")
    print("=" * 60)

    # 創建 Python 專家
    python_expert = PythonExpert()
    print(f"\n創建: {python_expert.name}")
    print(python_expert.get_system_prompt())

    # 創建 JavaScript 專家
    js_expert = JavaScriptExpert()
    print(f"\n創建: {js_expert.name}")

    # 創建任務特定助手
    code_reviewer = CodeReviewAssistant()
    testing_expert = TestingAssistant()
    refactoring_expert = RefactoringAssistant()

    return [python_expert, js_expert, code_reviewer, testing_expert, refactoring_expert]


def team_assistant_example():
    """
    團隊助手管理示例
    """
    print("\n" + "=" * 60)
    print("團隊助手管理")
    print("=" * 60)

    # 創建管理器
    manager = TeamAssistantManager()

    # 註冊所有助手
    assistants = create_custom_assistants()
    for assistant in assistants:
        manager.register_assistant(assistant)

    # 列出所有助手
    print("\n可用助手:")
    for name in manager.list_assistants():
        print(f"  - {name}")

    # 測試智能路由
    print("\n測試智能路由:")
    queries = [
        "如何優化 Python 代碼性能?",
        "請審查這段代碼",
        "如何編寫單元測試?",
        "這段代碼需要重構"
    ]

    for query in queries:
        print(f"\n查詢: {query}")
        response = manager.route_query(query)
        print(f"回覆: {response[:100]}...")


def main():
    """
    主函數
    """
    print("Continue - 自定義助手開發\n")

    # 創建自定義助手
    create_custom_assistants()

    # 團隊助手管理
    team_assistant_example()

    print("\n" + "=" * 60)
    print("示例運行完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
