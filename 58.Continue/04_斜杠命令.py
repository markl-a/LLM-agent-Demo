"""
Continue AI 編程助手 - 斜杠命令系統

這個文件展示了如何創建和使用自定義斜杠命令。
斜杠命令提供了快速執行常見任務的方式。

主要內容:
1. 斜杠命令基類
2. 內置命令實現
3. 自定義命令創建
4. 命令註冊和管理
5. 命令參數處理
6. 命令鏈和組合
7. 命令擴展

Author: Continue Team
Date: 2025
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import re
import json


# =====================================================
# 第一部分: 命令類型和參數定義
# =====================================================

class CommandCategory(Enum):
    """
    命令分類
    """
    EDIT = "edit"  # 編輯相關
    GENERATE = "generate"  # 生成相關
    ANALYZE = "analyze"  # 分析相關
    REFACTOR = "refactor"  # 重構相關
    TEST = "test"  # 測試相關
    DOCUMENTATION = "documentation"  # 文檔相關
    NAVIGATION = "navigation"  # 導航相關
    CUSTOM = "custom"  # 自定義


@dataclass
class CommandParameter:
    """
    命令參數定義
    """
    name: str  # 參數名
    description: str  # 參數描述
    required: bool = False  # 是否必需
    default: Any = None  # 默認值
    type: type = str  # 參數類型
    choices: Optional[List[Any]] = None  # 可選值列表


@dataclass
class CommandResult:
    """
    命令執行結果
    """
    success: bool  # 是否成功
    message: str  # 結果消息
    data: Dict[str, Any] = field(default_factory=dict)  # 結果數據
    suggestions: List[str] = field(default_factory=list)  # 後續建議


class CommandContext:
    """
    命令執行上下文

    包含命令執行所需的所有上下文信息
    """

    def __init__(
        self,
        current_file: Optional[str] = None,
        selected_text: Optional[str] = None,
        cursor_position: Optional[int] = None,
        workspace_root: Optional[str] = None
    ):
        """
        初始化命令上下文

        Args:
            current_file: 當前文件路徑
            selected_text: 選中的文本
            cursor_position: 光標位置
            workspace_root: 工作區根目錄
        """
        self.current_file = current_file
        self.selected_text = selected_text
        self.cursor_position = cursor_position
        self.workspace_root = workspace_root
        self.metadata: Dict[str, Any] = {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        獲取元數據

        Args:
            key: 鍵
            default: 默認值

        Returns:
            值
        """
        return self.metadata.get(key, default)

    def set(self, key: str, value: Any):
        """
        設置元數據

        Args:
            key: 鍵
            value: 值
        """
        self.metadata[key] = value


# =====================================================
# 第二部分: 斜杠命令基類
# =====================================================

class SlashCommand(ABC):
    """
    斜杠命令抽象基類

    所有斜杠命令都應繼承此類
    """

    def __init__(
        self,
        name: str,
        description: str,
        category: CommandCategory,
        aliases: Optional[List[str]] = None
    ):
        """
        初始化斜杠命令

        Args:
            name: 命令名稱
            description: 命令描述
            category: 命令分類
            aliases: 命令別名
        """
        self.name = name
        self.description = description
        self.category = category
        self.aliases = aliases or []
        self.parameters: List[CommandParameter] = []

    @abstractmethod
    def execute(
        self,
        args: List[str],
        context: CommandContext
    ) -> CommandResult:
        """
        執行命令

        Args:
            args: 命令參數
            context: 命令上下文

        Returns:
            命令執行結果
        """
        pass

    def add_parameter(self, parameter: CommandParameter):
        """
        添加參數定義

        Args:
            parameter: 參數對象
        """
        self.parameters.append(parameter)

    def parse_args(self, args: List[str]) -> Dict[str, Any]:
        """
        解析參數

        Args:
            args: 參數列表

        Returns:
            解析後的參數字典
        """
        parsed = {}

        # 簡單的參數解析實現
        for i, param in enumerate(self.parameters):
            if i < len(args):
                # 轉換類型
                try:
                    value = param.type(args[i])
                    parsed[param.name] = value
                except ValueError:
                    if param.required:
                        raise ValueError(f"參數 {param.name} 類型錯誤")
                    parsed[param.name] = param.default
            else:
                if param.required:
                    raise ValueError(f"缺少必需參數: {param.name}")
                parsed[param.name] = param.default

        return parsed

    def get_help(self) -> str:
        """
        獲取命令幫助信息

        Returns:
            幫助信息
        """
        help_text = f"/{self.name} - {self.description}\n"
        help_text += f"分類: {self.category.value}\n"

        if self.aliases:
            help_text += f"別名: {', '.join(self.aliases)}\n"

        if self.parameters:
            help_text += "\n參數:\n"
            for param in self.parameters:
                required = "(必需)" if param.required else "(可選)"
                help_text += f"  {param.name} {required}: {param.description}\n"
                if param.default is not None:
                    help_text += f"    默認值: {param.default}\n"

        return help_text


# =====================================================
# 第三部分: 內置編輯命令
# =====================================================

class EditCommand(SlashCommand):
    """
    /edit 命令 - 修改選中的代碼
    """

    def __init__(self):
        super().__init__(
            name="edit",
            description="根據指令修改選中的代碼",
            category=CommandCategory.EDIT,
            aliases=["modify", "change"]
        )

        self.add_parameter(CommandParameter(
            name="instruction",
            description="修改指令",
            required=True,
            type=str
        ))

    def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """執行編輯命令"""
        if not context.selected_text:
            return CommandResult(
                success=False,
                message="請先選擇要編輯的代碼"
            )

        try:
            params = self.parse_args(args)
            instruction = params["instruction"]

            # 這裡應該調用 AI 模型來修改代碼
            modified_code = self._modify_code(
                context.selected_text,
                instruction
            )

            return CommandResult(
                success=True,
                message="代碼已修改",
                data={"modified_code": modified_code},
                suggestions=[
                    "使用 /test 生成測試",
                    "使用 /review 審查修改"
                ]
            )

        except Exception as e:
            return CommandResult(
                success=False,
                message=f"編輯失敗: {str(e)}"
            )

    def _modify_code(self, code: str, instruction: str) -> str:
        """
        修改代碼(模擬)

        Args:
            code: 原始代碼
            instruction: 修改指令

        Returns:
            修改後的代碼
        """
        # 實際實現會調用 AI 模型
        return f"# 根據指令 '{instruction}' 修改後的代碼\n{code}"


class CommentCommand(SlashCommand):
    """
    /comment 命令 - 為代碼添加註釋
    """

    def __init__(self):
        super().__init__(
            name="comment",
            description="為選中的代碼添加詳細註釋",
            category=CommandCategory.DOCUMENTATION,
            aliases=["doc", "document"]
        )

        self.add_parameter(CommandParameter(
            name="style",
            description="註釋風格",
            required=False,
            default="detailed",
            choices=["brief", "detailed", "docstring"]
        ))

    def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """執行註釋命令"""
        if not context.selected_text:
            return CommandResult(
                success=False,
                message="請先選擇要添加註釋的代碼"
            )

        try:
            params = self.parse_args(args)
            style = params.get("style", "detailed")

            commented_code = self._add_comments(
                context.selected_text,
                style
            )

            return CommandResult(
                success=True,
                message=f"已添加 {style} 風格的註釋",
                data={"commented_code": commented_code}
            )

        except Exception as e:
            return CommandResult(
                success=False,
                message=f"添加註釋失敗: {str(e)}"
            )

    def _add_comments(self, code: str, style: str) -> str:
        """
        添加註釋

        Args:
            code: 原始代碼
            style: 註釋風格

        Returns:
            添加註釋後的代碼
        """
        # 實際實現會調用 AI 模型
        if style == "docstring":
            return f'"""\n函數說明\n"""\n{code}'
        else:
            return f"# {style} 註釋\n{code}"


class FixCommand(SlashCommand):
    """
    /fix 命令 - 修復代碼錯誤
    """

    def __init__(self):
        super().__init__(
            name="fix",
            description="自動修復代碼中的錯誤",
            category=CommandCategory.EDIT,
            aliases=["repair", "correct"]
        )

        self.add_parameter(CommandParameter(
            name="error_message",
            description="錯誤消息(可選)",
            required=False,
            type=str
        ))

    def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """執行修復命令"""
        if not context.selected_text:
            return CommandResult(
                success=False,
                message="請先選擇要修復的代碼"
            )

        try:
            params = self.parse_args(args)
            error_msg = params.get("error_message")

            fixed_code = self._fix_code(
                context.selected_text,
                error_msg
            )

            return CommandResult(
                success=True,
                message="代碼已修復",
                data={
                    "fixed_code": fixed_code,
                    "changes": "修復說明..."
                },
                suggestions=["使用 /test 驗證修復"]
            )

        except Exception as e:
            return CommandResult(
                success=False,
                message=f"修復失敗: {str(e)}"
            )

    def _fix_code(self, code: str, error_msg: Optional[str]) -> str:
        """
        修復代碼

        Args:
            code: 有錯誤的代碼
            error_msg: 錯誤消息

        Returns:
            修復後的代碼
        """
        # 實際實現會調用 AI 模型
        return f"# 已修復\n{code}"


# =====================================================
# 第四部分: 生成相關命令
# =====================================================

class GenerateCommand(SlashCommand):
    """
    /generate 命令 - 生成代碼
    """

    def __init__(self):
        super().__init__(
            name="generate",
            description="根據描述生成代碼",
            category=CommandCategory.GENERATE,
            aliases=["gen", "create"]
        )

        self.add_parameter(CommandParameter(
            name="what",
            description="要生成的內容(function/class/test等)",
            required=True,
            type=str
        ))

        self.add_parameter(CommandParameter(
            name="description",
            description="功能描述",
            required=True,
            type=str
        ))

    def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """執行生成命令"""
        try:
            if len(args) < 2:
                return CommandResult(
                    success=False,
                    message="用法: /generate <類型> <描述>"
                )

            what = args[0]
            description = " ".join(args[1:])

            generated_code = self._generate_code(what, description)

            return CommandResult(
                success=True,
                message=f"已生成 {what}",
                data={"generated_code": generated_code},
                suggestions=[
                    "使用 /comment 添加註釋",
                    "使用 /test 生成測試"
                ]
            )

        except Exception as e:
            return CommandResult(
                success=False,
                message=f"生成失敗: {str(e)}"
            )

    def _generate_code(self, what: str, description: str) -> str:
        """
        生成代碼

        Args:
            what: 生成類型
            description: 描述

        Returns:
            生成的代碼
        """
        templates = {
            "function": f"def new_function():\n    '''{description}'''\n    pass\n",
            "class": f"class NewClass:\n    '''{description}'''\n    pass\n",
            "test": f"def test_feature():\n    '''{description}'''\n    assert True\n"
        }

        return templates.get(what, f"# 生成: {what}\n# {description}\n")


class TestCommand(SlashCommand):
    """
    /test 命令 - 生成測試代碼
    """

    def __init__(self):
        super().__init__(
            name="test",
            description="為選中的代碼生成單元測試",
            category=CommandCategory.TEST,
            aliases=["unittest", "pytest"]
        )

        self.add_parameter(CommandParameter(
            name="framework",
            description="測試框架",
            required=False,
            default="pytest",
            choices=["pytest", "unittest", "jest"]
        ))

    def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """執行測試生成命令"""
        if not context.selected_text:
            return CommandResult(
                success=False,
                message="請先選擇要測試的代碼"
            )

        try:
            params = self.parse_args(args)
            framework = params.get("framework", "pytest")

            test_code = self._generate_tests(
                context.selected_text,
                framework
            )

            return CommandResult(
                success=True,
                message=f"已生成 {framework} 測試",
                data={"test_code": test_code}
            )

        except Exception as e:
            return CommandResult(
                success=False,
                message=f"測試生成失敗: {str(e)}"
            )

    def _generate_tests(self, code: str, framework: str) -> str:
        """
        生成測試代碼

        Args:
            code: 原始代碼
            framework: 測試框架

        Returns:
            測試代碼
        """
        if framework == "pytest":
            return f"import pytest\n\n# 測試代碼\ndef test_function():\n    # TODO: 實現測試\n    pass\n"
        else:
            return f"# {framework} 測試\n# TODO: 實現\n"


# =====================================================
# 第五部分: 重構相關命令
# =====================================================

class RefactorCommand(SlashCommand):
    """
    /refactor 命令 - 重構代碼
    """

    def __init__(self):
        super().__init__(
            name="refactor",
            description="重構選中的代碼",
            category=CommandCategory.REFACTOR
        )

        self.add_parameter(CommandParameter(
            name="technique",
            description="重構技術",
            required=False,
            default="auto",
            choices=["auto", "extract_method", "extract_class", "simplify"]
        ))

    def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """執行重構命令"""
        if not context.selected_text:
            return CommandResult(
                success=False,
                message="請先選擇要重構的代碼"
            )

        try:
            params = self.parse_args(args)
            technique = params.get("technique", "auto")

            refactored_code = self._refactor_code(
                context.selected_text,
                technique
            )

            return CommandResult(
                success=True,
                message=f"已應用 {technique} 重構",
                data={
                    "refactored_code": refactored_code,
                    "explanation": "重構說明..."
                },
                suggestions=["使用 /test 確保功能不變"]
            )

        except Exception as e:
            return CommandResult(
                success=False,
                message=f"重構失敗: {str(e)}"
            )

    def _refactor_code(self, code: str, technique: str) -> str:
        """
        重構代碼

        Args:
            code: 原始代碼
            technique: 重構技術

        Returns:
            重構後的代碼
        """
        return f"# 重構後的代碼 ({technique})\n{code}"


class OptimizeCommand(SlashCommand):
    """
    /optimize 命令 - 優化代碼性能
    """

    def __init__(self):
        super().__init__(
            name="optimize",
            description="優化代碼性能",
            category=CommandCategory.REFACTOR,
            aliases=["perf", "improve"]
        )

    def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """執行優化命令"""
        if not context.selected_text:
            return CommandResult(
                success=False,
                message="請先選擇要優化的代碼"
            )

        try:
            optimized_code = self._optimize_code(context.selected_text)

            return CommandResult(
                success=True,
                message="代碼已優化",
                data={
                    "optimized_code": optimized_code,
                    "improvements": [
                        "使用列表推導式",
                        "減少循環嵌套",
                        "優化算法複雜度"
                    ]
                }
            )

        except Exception as e:
            return CommandResult(
                success=False,
                message=f"優化失敗: {str(e)}"
            )

    def _optimize_code(self, code: str) -> str:
        """
        優化代碼

        Args:
            code: 原始代碼

        Returns:
            優化後的代碼
        """
        return f"# 優化後的代碼\n{code}"


# =====================================================
# 第六部分: 分析相關命令
# =====================================================

class ExplainCommand(SlashCommand):
    """
    /explain 命令 - 解釋代碼
    """

    def __init__(self):
        super().__init__(
            name="explain",
            description="解釋選中代碼的功能",
            category=CommandCategory.ANALYZE,
            aliases=["describe", "what"]
        )

    def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """執行解釋命令"""
        if not context.selected_text:
            return CommandResult(
                success=False,
                message="請先選擇要解釋的代碼"
            )

        try:
            explanation = self._explain_code(context.selected_text)

            return CommandResult(
                success=True,
                message="代碼解釋",
                data={"explanation": explanation}
            )

        except Exception as e:
            return CommandResult(
                success=False,
                message=f"解釋失敗: {str(e)}"
            )

    def _explain_code(self, code: str) -> str:
        """
        解釋代碼

        Args:
            code: 代碼

        Returns:
            解釋文本
        """
        return f"""
代碼功能解釋:
1. 這段代碼實現了...
2. 主要邏輯是...
3. 使用了以下技術...

詳細說明:
{code}
"""


class ReviewCommand(SlashCommand):
    """
    /review 命令 - 審查代碼
    """

    def __init__(self):
        super().__init__(
            name="review",
            description="審查代碼質量",
            category=CommandCategory.ANALYZE
        )

    def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """執行審查命令"""
        if not context.selected_text:
            return CommandResult(
                success=False,
                message="請先選擇要審查的代碼"
            )

        try:
            review = self._review_code(context.selected_text)

            return CommandResult(
                success=True,
                message="代碼審查完成",
                data={"review": review},
                suggestions=[
                    "根據建議使用 /refactor 重構",
                    "使用 /fix 修復問題"
                ]
            )

        except Exception as e:
            return CommandResult(
                success=False,
                message=f"審查失敗: {str(e)}"
            )

    def _review_code(self, code: str) -> Dict[str, Any]:
        """
        審查代碼

        Args:
            code: 代碼

        Returns:
            審查結果
        """
        return {
            "quality_score": 85,
            "issues": [
                "建議添加錯誤處理",
                "變量命名可以更清晰"
            ],
            "strengths": [
                "代碼結構清晰",
                "邏輯正確"
            ],
            "suggestions": [
                "添加類型註解",
                "增加文檔字符串"
            ]
        }


# =====================================================
# 第七部分: 命令管理器
# =====================================================

class CommandRegistry:
    """
    命令註冊表

    管理所有可用的斜杠命令
    """

    def __init__(self):
        """初始化命令註冊表"""
        self.commands: Dict[str, SlashCommand] = {}
        self._register_builtin_commands()

    def _register_builtin_commands(self):
        """註冊內置命令"""
        builtin_commands = [
            EditCommand(),
            CommentCommand(),
            FixCommand(),
            GenerateCommand(),
            TestCommand(),
            RefactorCommand(),
            OptimizeCommand(),
            ExplainCommand(),
            ReviewCommand()
        ]

        for cmd in builtin_commands:
            self.register(cmd)

    def register(self, command: SlashCommand):
        """
        註冊命令

        Args:
            command: 斜杠命令
        """
        self.commands[command.name] = command

        # 註冊別名
        for alias in command.aliases:
            self.commands[alias] = command

        print(f"已註冊命令: /{command.name}")

    def get_command(self, name: str) -> Optional[SlashCommand]:
        """
        獲取命令

        Args:
            name: 命令名稱

        Returns:
            命令對象或 None
        """
        return self.commands.get(name)

    def execute_command(
        self,
        command_line: str,
        context: CommandContext
    ) -> CommandResult:
        """
        執行命令

        Args:
            command_line: 命令行(如 "/edit 添加錯誤處理")
            context: 命令上下文

        Returns:
            命令執行結果
        """
        # 解析命令行
        parts = command_line.strip().split()
        if not parts or not parts[0].startswith('/'):
            return CommandResult(
                success=False,
                message="無效的命令格式"
            )

        cmd_name = parts[0][1:]  # 移除 /
        args = parts[1:]

        # 獲取命令
        command = self.get_command(cmd_name)
        if not command:
            return CommandResult(
                success=False,
                message=f"未知命令: /{cmd_name}"
            )

        # 執行命令
        return command.execute(args, context)

    def list_commands(self, category: Optional[CommandCategory] = None) -> List[str]:
        """
        列出所有命令

        Args:
            category: 可選的分類過濾

        Returns:
            命令名稱列表
        """
        seen = set()
        commands = []

        for name, cmd in self.commands.items():
            if cmd.name in seen:
                continue

            if category is None or cmd.category == category:
                commands.append(cmd.name)
                seen.add(cmd.name)

        return sorted(commands)

    def get_help(self, command_name: Optional[str] = None) -> str:
        """
        獲取幫助信息

        Args:
            command_name: 命令名稱(可選)

        Returns:
            幫助文本
        """
        if command_name:
            cmd = self.get_command(command_name)
            if cmd:
                return cmd.get_help()
            else:
                return f"未找到命令: /{command_name}"
        else:
            # 列出所有命令
            help_text = "可用命令:\n\n"

            for category in CommandCategory:
                commands = self.list_commands(category)
                if commands:
                    help_text += f"{category.value.upper()}:\n"
                    for cmd_name in commands:
                        cmd = self.get_command(cmd_name)
                        help_text += f"  /{cmd_name} - {cmd.description}\n"
                    help_text += "\n"

            return help_text


# =====================================================
# 第八部分: 使用示例
# =====================================================

def command_usage_examples():
    """
    命令使用示例
    """
    print("=" * 60)
    print("斜杠命令使用示例")
    print("=" * 60)

    # 創建命令註冊表
    registry = CommandRegistry()

    # 創建命令上下文
    context = CommandContext(
        current_file="example.py",
        selected_text="def old_function():\n    return 42",
        cursor_position=100
    )

    # 示例 1: 編輯代碼
    print("\n示例 1: 編輯代碼")
    result = registry.execute_command("/edit 添加錯誤處理", context)
    print(f"結果: {result.message}")

    # 示例 2: 添加註釋
    print("\n示例 2: 添加註釋")
    result = registry.execute_command("/comment docstring", context)
    print(f"結果: {result.message}")

    # 示例 3: 生成測試
    print("\n示例 3: 生成測試")
    result = registry.execute_command("/test pytest", context)
    print(f"結果: {result.message}")

    # 示例 4: 代碼審查
    print("\n示例 4: 代碼審查")
    result = registry.execute_command("/review", context)
    print(f"結果: {result.message}")
    if result.success:
        print(f"審查數據: {result.data.get('review')}")

    # 列出所有命令
    print("\n所有可用命令:")
    print(registry.get_help())


def main():
    """
    主函數
    """
    print("Continue - 斜杠命令系統\n")
    command_usage_examples()


if __name__ == "__main__":
    main()
