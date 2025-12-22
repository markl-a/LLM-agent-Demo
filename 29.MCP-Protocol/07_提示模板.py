"""
MCP 提示模板
===========

本模組介紹 MCP 的提示模板（Prompts）功能。
提示模板允許服務器提供預定義的、參數化的提示詞。

學習目標：
- 理解提示模板的用途
- 定義參數化提示
- 實現提示模板管理
- 使用上下文和動態內容

作者：Claude (Anthropic)
日期：2025-12-22
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# 第一部分：提示模板基礎
# ============================================================================

@dataclass
class PromptArgument:
    """提示參數定義"""
    name: str
    description: str
    required: bool = False
    default: Optional[Any] = None


@dataclass
class PromptTemplate:
    """提示模板"""
    name: str
    description: str
    arguments: List[PromptArgument]
    template: str
    metadata: Optional[Dict[str, Any]] = None


class PromptCategory(Enum):
    """提示類別"""
    CODE_REVIEW = "代碼審查"
    DOCUMENTATION = "文檔生成"
    TESTING = "測試生成"
    DEBUGGING = "調試輔助"
    OPTIMIZATION = "優化建議"
    EXPLANATION = "代碼解釋"


# ============================================================================
# 第二部分：常見提示模板
# ============================================================================

class CommonPrompts:
    """常見提示模板集合"""

    @staticmethod
    def code_review_prompt() -> PromptTemplate:
        """代碼審查提示"""
        return PromptTemplate(
            name="code_review",
            description="進行全面的代碼審查",
            arguments=[
                PromptArgument("language", "程式語言", required=True),
                PromptArgument("focus", "審查重點", required=False, default="all"),
                PromptArgument("code", "要審查的代碼", required=True)
            ],
            template="""請對以下 {language} 代碼進行審查：

```{language}
{code}
```

審查重點：{focus}

請檢查：
1. **代碼質量**
   - 可讀性和維護性
   - 命名規範
   - 代碼結構

2. **潛在問題**
   - Bug 和錯誤
   - 安全漏洞
   - 性能問題

3. **最佳實踐**
   - 設計模式
   - 錯誤處理
   - 文檔註釋

請提供具體的改進建議。
""",
            metadata={"category": PromptCategory.CODE_REVIEW.value}
        )

    @staticmethod
    def documentation_prompt() -> PromptTemplate:
        """文檔生成提示"""
        return PromptTemplate(
            name="generate_docs",
            description="為代碼生成文檔",
            arguments=[
                PromptArgument("language", "程式語言", required=True),
                PromptArgument("code", "要文檔化的代碼", required=True),
                PromptArgument("style", "文檔風格", required=False, default="google")
            ],
            template="""請為以下 {language} 代碼生成詳細文檔：

```{language}
{code}
```

文檔風格：{style}

請包含：
- 功能概述
- 參數說明
- 返回值
- 使用示例
- 注意事項
""",
            metadata={"category": PromptCategory.DOCUMENTATION.value}
        )

    @staticmethod
    def test_generation_prompt() -> PromptTemplate:
        """測試生成提示"""
        return PromptTemplate(
            name="generate_tests",
            description="生成單元測試",
            arguments=[
                PromptArgument("language", "程式語言", required=True),
                PromptArgument("function", "要測試的函數", required=True),
                PromptArgument("framework", "測試框架", required=False, default="auto")
            ],
            template="""請為以下 {language} 函數生成單元測試：

```{language}
{function}
```

測試框架：{framework}

請生成測試用例覆蓋：
- 正常情況
- 邊界情況
- 異常情況
- 性能測試（如適用）
""",
            metadata={"category": PromptCategory.TESTING.value}
        )

    @staticmethod
    def debug_prompt() -> PromptTemplate:
        """調試輔助提示"""
        return PromptTemplate(
            name="debug_help",
            description="幫助調試代碼問題",
            arguments=[
                PromptArgument("language", "程式語言", required=True),
                PromptArgument("code", "有問題的代碼", required=True),
                PromptArgument("error", "錯誤信息", required=True),
                PromptArgument("context", "額外上下文", required=False, default="")
            ],
            template="""請幫助調試以下 {language} 代碼：

**代碼：**
```{language}
{code}
```

**錯誤信息：**
```
{error}
```

{context}

請：
1. 分析錯誤原因
2. 提供修復建議
3. 解釋如何避免類似問題
""",
            metadata={"category": PromptCategory.DEBUGGING.value}
        )


# ============================================================================
# 第三部分：提示模板管理器
# ============================================================================

class PromptManager:
    """提示模板管理器"""

    def __init__(self):
        self.prompts: Dict[str, PromptTemplate] = {}
        self._load_default_prompts()

    def _load_default_prompts(self):
        """載入默認提示模板"""
        common = CommonPrompts()

        self.register_prompt(common.code_review_prompt())
        self.register_prompt(common.documentation_prompt())
        self.register_prompt(common.test_generation_prompt())
        self.register_prompt(common.debug_prompt())

    def register_prompt(self, prompt: PromptTemplate):
        """註冊提示模板"""
        self.prompts[prompt.name] = prompt
        print(f"✓ 註冊提示模板: {prompt.name}")

    def get_prompt(self, name: str) -> Optional[PromptTemplate]:
        """獲取提示模板"""
        return self.prompts.get(name)

    def list_prompts(self) -> List[PromptTemplate]:
        """列出所有提示模板"""
        return list(self.prompts.values())

    def render_prompt(
        self,
        name: str,
        arguments: Dict[str, Any]
    ) -> str:
        """
        渲染提示模板

        Args:
            name: 模板名稱
            arguments: 參數值

        Returns:
            渲染後的提示文本
        """
        prompt = self.get_prompt(name)
        if not prompt:
            raise ValueError(f"提示模板不存在: {name}")

        # 驗證必需參數
        for arg in prompt.arguments:
            if arg.required and arg.name not in arguments:
                raise ValueError(f"缺少必需參數: {arg.name}")

        # 填充默認值
        render_args = {}
        for arg in prompt.arguments:
            if arg.name in arguments:
                render_args[arg.name] = arguments[arg.name]
            elif arg.default is not None:
                render_args[arg.name] = arg.default
            else:
                render_args[arg.name] = ""

        # 渲染模板
        try:
            return prompt.template.format(**render_args)
        except KeyError as e:
            raise ValueError(f"模板參數錯誤: {e}")


# ============================================================================
# 第四部分：特定領域提示模板
# ============================================================================

class DomainSpecificPrompts:
    """特定領域的提示模板"""

    @staticmethod
    def python_specific_prompts() -> List[PromptTemplate]:
        """Python 專用提示"""
        return [
            PromptTemplate(
                name="python_type_hints",
                description="添加 Python 類型提示",
                arguments=[
                    PromptArgument("code", "Python 代碼", required=True)
                ],
                template="""請為以下 Python 代碼添加類型提示：

```python
{code}
```

請使用 Python 3.10+ 的現代類型提示語法。
"""
            ),
            PromptTemplate(
                name="python_refactor_dataclass",
                description="重構為 dataclass",
                arguments=[
                    PromptArgument("class_code", "類定義", required=True)
                ],
                template="""請將以下類重構為使用 dataclass：

```python
{class_code}
```

使用 @dataclass 裝飾器和現代 Python 特性。
"""
            )
        ]

    @staticmethod
    def javascript_specific_prompts() -> List[PromptTemplate]:
        """JavaScript 專用提示"""
        return [
            PromptTemplate(
                name="js_convert_to_typescript",
                description="轉換為 TypeScript",
                arguments=[
                    PromptArgument("code", "JavaScript 代碼", required=True)
                ],
                template="""請將以下 JavaScript 代碼轉換為 TypeScript：

```javascript
{code}
```

添加適當的類型定義和接口。
"""
            ),
            PromptTemplate(
                name="js_modernize",
                description="現代化 JavaScript 代碼",
                arguments=[
                    PromptArgument("code", "舊版 JavaScript 代碼", required=True)
                ],
                template="""請將以下代碼現代化，使用 ES6+ 特性：

```javascript
{code}
```

使用 const/let、箭頭函數、async/await 等現代語法。
"""
            )
        ]


# ============================================================================
# 第五部分：動態提示生成
# ============================================================================

class DynamicPromptGenerator:
    """動態提示生成器"""

    def __init__(self, context: Optional[Dict[str, Any]] = None):
        self.context = context or {}

    def generate_contextual_prompt(
        self,
        base_template: str,
        user_input: Dict[str, Any]
    ) -> str:
        """
        基於上下文生成提示

        結合系統上下文和用戶輸入
        """
        # 合併上下文
        full_context = {**self.context, **user_input}

        # 添加動態部分
        if "timestamp" not in full_context:
            from datetime import datetime
            full_context["timestamp"] = datetime.now().isoformat()

        return base_template.format(**full_context)

    def create_chain_of_thought_prompt(
        self,
        task: str,
        steps: List[str]
    ) -> str:
        """創建思維鏈提示"""
        prompt = f"任務：{task}\n\n請按以下步驟思考：\n\n"

        for i, step in enumerate(steps, 1):
            prompt += f"{i}. {step}\n"

        prompt += "\n請詳細說明每一步的思考過程。"
        return prompt

    def create_few_shot_prompt(
        self,
        task: str,
        examples: List[Dict[str, str]]
    ) -> str:
        """創建 Few-Shot 提示"""
        prompt = f"任務：{task}\n\n示例：\n\n"

        for i, example in enumerate(examples, 1):
            prompt += f"示例 {i}：\n"
            prompt += f"輸入：{example['input']}\n"
            prompt += f"輸出：{example['output']}\n\n"

        prompt += "現在請處理新的輸入。"
        return prompt


# ============================================================================
# 主程式示例
# ============================================================================

def main():
    """主程式：展示提示模板功能"""

    print("=" * 70)
    print("MCP 提示模板示例")
    print("=" * 70)

    # 1. 提示模板管理
    print("\n【示例 1：提示模板管理】")
    manager = PromptManager()

    print(f"\n可用提示模板 ({len(manager.list_prompts())}):")
    for prompt in manager.list_prompts():
        print(f"  • {prompt.name}: {prompt.description}")

    # 2. 渲染提示
    print("\n【示例 2：渲染代碼審查提示】")
    code_review = manager.render_prompt(
        "code_review",
        {
            "language": "Python",
            "focus": "security",
            "code": "def process_user_input(data):\n    exec(data)"
        }
    )
    print(code_review)

    # 3. 動態提示生成
    print("\n【示例 3：動態提示生成】")
    generator = DynamicPromptGenerator(context={"project": "MCP Demo"})

    chain_prompt = generator.create_chain_of_thought_prompt(
        "優化數據庫查詢",
        [
            "分析當前查詢的性能瓶頸",
            "識別可以添加的索引",
            "考慮查詢重寫的可能性",
            "評估緩存策略"
        ]
    )
    print(chain_prompt)

    # 4. Few-Shot 示例
    print("\n【示例 4：Few-Shot 提示】")
    few_shot = generator.create_few_shot_prompt(
        "將函數名從 snake_case 轉換為 camelCase",
        [
            {"input": "get_user_name", "output": "getUserName"},
            {"input": "calculate_total_price", "output": "calculateTotalPrice"}
        ]
    )
    print(few_shot)

    # 5. 特定領域提示
    print("\n【示例 5：Python 專用提示】")
    python_prompts = DomainSpecificPrompts.python_specific_prompts()
    print(f"Python 專用提示 ({len(python_prompts)}):")
    for prompt in python_prompts:
        print(f"  • {prompt.name}: {prompt.description}")

    print("\n" + "=" * 70)
    print("下一步：查看 08_Claude整合.py 學習與 Claude 整合")
    print("=" * 70)


if __name__ == "__main__":
    main()
