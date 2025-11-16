"""
AI 程式碼助手
使用 LangChain + AutoGen 構建的智能代碼輔助系統

功能特點:
- 代碼分析和解釋
- 代碼生成和補全
- Bug 檢測和修復建議
- 代碼審查輔助
- 重構建議
- 文檔生成
"""

import os
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import (
    Language,
    RecursiveCharacterTextSplitter
)


# ============ 枚舉類型 ============
class CodeLanguage(Enum):
    """支持的程式語言"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    GO = "go"
    RUST = "rust"


class AssistantMode(Enum):
    """助手模式"""
    EXPLAIN = "explain"  # 解釋代碼
    GENERATE = "generate"  # 生成代碼
    DEBUG = "debug"  # 調試代碼
    REVIEW = "review"  # 代碼審查
    REFACTOR = "refactor"  # 重構建議
    DOCUMENT = "document"  # 生成文檔
    OPTIMIZE = "optimize"  # 性能優化


# ============ 數據模型 ============
@dataclass
class CodeAnalysis:
    """代碼分析結果"""
    language: str
    summary: str
    complexity: str  # low, medium, high
    issues: List[str]
    suggestions: List[str]


@dataclass
class CodeReview:
    """代碼審查結果"""
    overall_score: int  # 0-100
    strengths: List[str]
    weaknesses: List[str]
    bugs: List[str]
    security_issues: List[str]
    performance_issues: List[str]
    style_issues: List[str]
    recommendations: List[str]


# ============ 程式碼助手類 ============
class CodeAssistant:
    """AI 程式碼助手"""

    def __init__(
        self,
        model: str = "gpt-4o",
        temperature: float = 0.3
    ):
        """
        初始化程式碼助手

        Args:
            model: 使用的 LLM 模型
            temperature: 溫度參數（0-1）
        """
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.code_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON,
            chunk_size=1000,
            chunk_overlap=100
        )

    def detect_language(self, code: str) -> str:
        """
        檢測代碼語言

        Args:
            code: 代碼字符串

        Returns:
            檢測到的語言
        """
        # 簡單的語言檢測邏輯
        if "def " in code or "import " in code or "class " in code:
            return "python"
        elif "function " in code or "const " in code or "let " in code:
            return "javascript"
        elif "interface " in code or "type " in code:
            return "typescript"
        elif "public class " in code or "private " in code:
            return "java"
        elif "#include" in code or "std::" in code:
            return "cpp"
        elif "func " in code or "package " in code:
            return "go"
        elif "fn " in code or "impl " in code:
            return "rust"
        else:
            return "unknown"

    def explain_code(self, code: str, language: Optional[str] = None) -> str:
        """
        解釋代碼

        Args:
            code: 要解釋的代碼
            language: 代碼語言（可選）

        Returns:
            代碼解釋
        """
        if not language:
            language = self.detect_language(code)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一個資深的程式設計導師，擅長解釋代碼。

            請用清晰、易懂的語言解釋以下代碼：

            1. 代碼的主要目的和功能
            2. 逐步解釋關鍵部分的邏輯
            3. 指出使用的重要概念或模式
            4. 如果有複雜的部分，用類比或例子說明

            語言風格：
            - 使用繁體中文
            - 通俗易懂，適合初學者
            - 適當使用技術術語，但要解釋清楚
            """),
            ("human", "程式語言: {language}\n\n代碼:\n```{language}\n{code}\n```\n\n請解釋這段代碼:")
        ])

        chain = prompt | self.llm | StrOutputParser()

        explanation = chain.invoke({
            "language": language,
            "code": code
        })

        return explanation

    def generate_code(
        self,
        description: str,
        language: str = "python",
        include_tests: bool = False
    ) -> str:
        """
        根據描述生成代碼

        Args:
            description: 功能描述
            language: 目標語言
            include_tests: 是否包含測試代碼

        Returns:
            生成的代碼
        """
        test_instruction = ""
        if include_tests:
            test_instruction = "\n4. 包含單元測試代碼"

        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一個專業的程式設計師，擅長編寫高質量代碼。

            根據用戶的需求描述生成代碼。

            要求：
            1. 代碼應該清晰、高效、可維護
            2. 遵循語言的最佳實踐和編碼規範
            3. 包含適當的註釋和文檔字符串{test_instruction}
            5. 處理邊界情況和錯誤

            只返回代碼，使用 markdown 代碼塊格式。
            """),
            ("human", "語言: {language}\n\n需求描述:\n{description}\n\n請生成代碼:")
        ])

        chain = prompt | self.llm | StrOutputParser()

        code = chain.invoke({
            "language": language,
            "description": description,
            "test_instruction": test_instruction
        })

        return code

    def debug_code(self, code: str, error_message: Optional[str] = None) -> str:
        """
        調試代碼並提供修復建議

        Args:
            code: 有問題的代碼
            error_message: 錯誤信息（可選）

        Returns:
            調試分析和修復建議
        """
        language = self.detect_language(code)

        error_context = ""
        if error_message:
            error_context = f"\n\n錯誤信息:\n{error_message}"

        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一個經驗豐富的調試專家。

            分析代碼中的問題並提供解決方案。

            請提供：
            1. 問題診斷：識別錯誤的根本原因
            2. 詳細解釋：為什麼會出現這個問題
            3. 修復方案：提供修正後的代碼
            4. 預防建議：如何避免類似問題

            格式化輸出，使用 markdown。
            """),
            ("human", "程式語言: {language}\n\n代碼:\n```{language}\n{code}\n```{error_context}\n\n請分析並提供修復建議:")
        ])

        chain = prompt | self.llm | StrOutputParser()

        debug_result = chain.invoke({
            "language": language,
            "code": code,
            "error_context": error_context
        })

        return debug_result

    def review_code(self, code: str) -> CodeReview:
        """
        進行代碼審查

        Args:
            code: 要審查的代碼

        Returns:
            代碼審查結果
        """
        language = self.detect_language(code)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一個資深的代碼審查專家。

            進行全面的代碼審查，評估以下方面：

            1. 代碼質量和可讀性
            2. 潛在的 Bug 和錯誤
            3. 安全漏洞
            4. 性能問題
            5. 代碼風格和規範
            6. 最佳實踐

            請以 JSON 格式返回結果：
            {{
                "overall_score": 85,
                "strengths": ["優點1", "優點2"],
                "weaknesses": ["缺點1", "缺點2"],
                "bugs": ["潛在Bug1"],
                "security_issues": ["安全問題1"],
                "performance_issues": ["性能問題1"],
                "style_issues": ["風格問題1"],
                "recommendations": ["建議1", "建議2"]
            }}
            """),
            ("human", "程式語言: {language}\n\n代碼:\n```{language}\n{code}\n```\n\n請進行代碼審查:")
        ])

        chain = prompt | self.llm | StrOutputParser()

        result_text = chain.invoke({
            "language": language,
            "code": code
        })

        # 解析 JSON 結果
        import json
        try:
            # 提取 JSON 部分
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                result_json = json.loads(json_match.group())
            else:
                # 如果無法解析，使用默認值
                result_json = {
                    "overall_score": 70,
                    "strengths": ["代碼可讀性良好"],
                    "weaknesses": ["需要進一步改進"],
                    "bugs": [],
                    "security_issues": [],
                    "performance_issues": [],
                    "style_issues": [],
                    "recommendations": ["請參考上述分析"]
                }

            review = CodeReview(
                overall_score=result_json.get("overall_score", 70),
                strengths=result_json.get("strengths", []),
                weaknesses=result_json.get("weaknesses", []),
                bugs=result_json.get("bugs", []),
                security_issues=result_json.get("security_issues", []),
                performance_issues=result_json.get("performance_issues", []),
                style_issues=result_json.get("style_issues", []),
                recommendations=result_json.get("recommendations", [])
            )

        except Exception as e:
            print(f"解析審查結果失敗: {e}")
            # 返回默認審查結果
            review = CodeReview(
                overall_score=70,
                strengths=["代碼結構清晰"],
                weaknesses=["需要更多改進"],
                bugs=[],
                security_issues=[],
                performance_issues=[],
                style_issues=[],
                recommendations=["建議進行更詳細的審查"]
            )

        return review

    def suggest_refactoring(self, code: str) -> str:
        """
        提供重構建議

        Args:
            code: 要重構的代碼

        Returns:
            重構建議和改進後的代碼
        """
        language = self.detect_language(code)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一個代碼重構專家。

            分析代碼並提供重構建議。

            重構原則：
            1. 提高可讀性
            2. 減少複雜度
            3. 消除重複代碼
            4. 改善命名
            5. 應用設計模式

            請提供：
            1. 當前代碼的問題分析
            2. 重構建議和理由
            3. 重構後的代碼
            4. 重構帶來的好處
            """),
            ("human", "程式語言: {language}\n\n代碼:\n```{language}\n{code}\n```\n\n請提供重構建議:")
        ])

        chain = prompt | self.llm | StrOutputParser()

        refactoring = chain.invoke({
            "language": language,
            "code": code
        })

        return refactoring

    def generate_documentation(self, code: str) -> str:
        """
        生成代碼文檔

        Args:
            code: 要生成文檔的代碼

        Returns:
            生成的文檔
        """
        language = self.detect_language(code)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一個技術文檔專家。

            為提供的代碼生成完整的文檔。

            文檔應包括：
            1. 概述：代碼的主要功能
            2. 參數說明：每個參數的類型和用途
            3. 返回值：返回值的類型和含義
            4. 使用範例：如何使用這段代碼
            5. 注意事項：需要注意的特殊情況
            6. 異常處理：可能拋出的異常

            使用 markdown 格式。
            """),
            ("human", "程式語言: {language}\n\n代碼:\n```{language}\n{code}\n```\n\n請生成文檔:")
        ])

        chain = prompt | self.llm | StrOutputParser()

        documentation = chain.invoke({
            "language": language,
            "code": code
        })

        return documentation

    def optimize_code(self, code: str) -> str:
        """
        優化代碼性能

        Args:
            code: 要優化的代碼

        Returns:
            優化建議和改進後的代碼
        """
        language = self.detect_language(code)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一個性能優化專家。

            分析代碼並提供性能優化建議。

            優化方向：
            1. 時間複雜度優化
            2. 空間複雜度優化
            3. 算法改進
            4. 數據結構選擇
            5. 緩存策略
            6. 並行處理

            請提供：
            1. 性能瓶頸分析
            2. 優化建議和理由
            3. 優化後的代碼
            4. 性能提升預估
            """),
            ("human", "程式語言: {language}\n\n代碼:\n```{language}\n{code}\n```\n\n請提供性能優化建議:")
        ])

        chain = prompt | self.llm | StrOutputParser()

        optimization = chain.invoke({
            "language": language,
            "code": code
        })

        return optimization


# ============ 互動式界面 ============
class InteractiveCodeAssistant:
    """互動式程式碼助手"""

    def __init__(self):
        self.assistant = CodeAssistant()
        self.current_code = ""

    def display_menu(self):
        """顯示功能選單"""
        print("\n" + "=" * 60)
        print("🤖 AI 程式碼助手")
        print("=" * 60)
        print("\n可用功能：")
        print("1. 解釋代碼 (explain)")
        print("2. 生成代碼 (generate)")
        print("3. 調試代碼 (debug)")
        print("4. 代碼審查 (review)")
        print("5. 重構建議 (refactor)")
        print("6. 生成文檔 (document)")
        print("7. 性能優化 (optimize)")
        print("8. 設置當前代碼 (set-code)")
        print("9. 顯示當前代碼 (show-code)")
        print("0. 退出 (quit)")
        print("=" * 60)

    def handle_explain(self):
        """處理解釋代碼"""
        if not self.current_code:
            code = input("\n請輸入要解釋的代碼 (輸入 END 結束):\n")
            lines = [code]
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
            code = "\n".join(lines)
        else:
            code = self.current_code

        print("\n🔍 正在分析代碼...")
        explanation = self.assistant.explain_code(code)

        print("\n" + "=" * 60)
        print("📖 代碼解釋:")
        print("=" * 60)
        print(explanation)
        print("=" * 60)

    def handle_generate(self):
        """處理生成代碼"""
        description = input("\n請描述您需要的功能:\n")
        language = input("目標語言 (默認 python): ").strip() or "python"
        include_tests = input("是否包含測試? (y/n, 默認 n): ").lower() == 'y'

        print("\n⚙️ 正在生成代碼...")
        code = self.assistant.generate_code(
            description,
            language,
            include_tests
        )

        print("\n" + "=" * 60)
        print("✨ 生成的代碼:")
        print("=" * 60)
        print(code)
        print("=" * 60)

        save = input("\n是否保存為當前代碼? (y/n): ").lower()
        if save == 'y':
            # 提取代碼塊
            code_match = re.search(r'```[\w]*\n([\s\S]*?)\n```', code)
            if code_match:
                self.current_code = code_match.group(1)
            else:
                self.current_code = code
            print("✅ 已保存為當前代碼")

    def handle_debug(self):
        """處理調試代碼"""
        if not self.current_code:
            print("\n❌ 請先設置當前代碼")
            return

        error_msg = input("\n錯誤信息 (可選，按 Enter 跳過):\n").strip()

        print("\n🐛 正在分析問題...")
        debug_result = self.assistant.debug_code(
            self.current_code,
            error_msg if error_msg else None
        )

        print("\n" + "=" * 60)
        print("🔧 調試結果:")
        print("=" * 60)
        print(debug_result)
        print("=" * 60)

    def handle_review(self):
        """處理代碼審查"""
        if not self.current_code:
            print("\n❌ 請先設置當前代碼")
            return

        print("\n📋 正在進行代碼審查...")
        review = self.assistant.review_code(self.current_code)

        print("\n" + "=" * 60)
        print("📊 代碼審查報告")
        print("=" * 60)
        print(f"\n總體評分: {review.overall_score}/100")

        if review.strengths:
            print("\n✅ 優點:")
            for strength in review.strengths:
                print(f"  - {strength}")

        if review.weaknesses:
            print("\n⚠️ 缺點:")
            for weakness in review.weaknesses:
                print(f"  - {weakness}")

        if review.bugs:
            print("\n🐛 潛在 Bug:")
            for bug in review.bugs:
                print(f"  - {bug}")

        if review.security_issues:
            print("\n🔒 安全問題:")
            for issue in review.security_issues:
                print(f"  - {issue}")

        if review.performance_issues:
            print("\n⚡ 性能問題:")
            for issue in review.performance_issues:
                print(f"  - {issue}")

        if review.style_issues:
            print("\n🎨 風格問題:")
            for issue in review.style_issues:
                print(f"  - {issue}")

        if review.recommendations:
            print("\n💡 建議:")
            for rec in review.recommendations:
                print(f"  - {rec}")

        print("=" * 60)

    def handle_refactor(self):
        """處理重構建議"""
        if not self.current_code:
            print("\n❌ 請先設置當前代碼")
            return

        print("\n🔨 正在分析重構機會...")
        refactoring = self.assistant.suggest_refactoring(self.current_code)

        print("\n" + "=" * 60)
        print("♻️ 重構建議:")
        print("=" * 60)
        print(refactoring)
        print("=" * 60)

    def handle_document(self):
        """處理生成文檔"""
        if not self.current_code:
            print("\n❌ 請先設置當前代碼")
            return

        print("\n📝 正在生成文檔...")
        documentation = self.assistant.generate_documentation(self.current_code)

        print("\n" + "=" * 60)
        print("📚 生成的文檔:")
        print("=" * 60)
        print(documentation)
        print("=" * 60)

    def handle_optimize(self):
        """處理性能優化"""
        if not self.current_code:
            print("\n❌ 請先設置當前代碼")
            return

        print("\n⚡ 正在分析性能優化機會...")
        optimization = self.assistant.optimize_code(self.current_code)

        print("\n" + "=" * 60)
        print("🚀 性能優化建議:")
        print("=" * 60)
        print(optimization)
        print("=" * 60)

    def handle_set_code(self):
        """設置當前代碼"""
        print("\n請輸入代碼 (輸入 END 結束):")
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)

        self.current_code = "\n".join(lines)
        print("\n✅ 代碼已設置")

    def handle_show_code(self):
        """顯示當前代碼"""
        if not self.current_code:
            print("\n❌ 尚未設置當前代碼")
        else:
            print("\n" + "=" * 60)
            print("當前代碼:")
            print("=" * 60)
            print(self.current_code)
            print("=" * 60)

    def run(self):
        """運行互動式助手"""
        while True:
            self.display_menu()
            choice = input("\n請選擇功能: ").strip()

            if choice in ['0', 'quit', 'exit', '退出']:
                print("\n感謝使用！👋")
                break
            elif choice in ['1', 'explain']:
                self.handle_explain()
            elif choice in ['2', 'generate']:
                self.handle_generate()
            elif choice in ['3', 'debug']:
                self.handle_debug()
            elif choice in ['4', 'review']:
                self.handle_review()
            elif choice in ['5', 'refactor']:
                self.handle_refactor()
            elif choice in ['6', 'document']:
                self.handle_document()
            elif choice in ['7', 'optimize']:
                self.handle_optimize()
            elif choice in ['8', 'set-code']:
                self.handle_set_code()
            elif choice in ['9', 'show-code']:
                self.handle_show_code()
            else:
                print("\n❌ 無效的選擇，請重試")


# ============ 主程序 ============
def main():
    """主程序"""
    # 檢查環境變數
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 錯誤: 請設置 OPENAI_API_KEY 環境變數")
        print("   export OPENAI_API_KEY='your-api-key'")
        exit(1)

    # 啟動互動式助手
    assistant = InteractiveCodeAssistant()
    assistant.run()


if __name__ == "__main__":
    main()
