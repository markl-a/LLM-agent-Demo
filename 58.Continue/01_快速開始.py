"""
Continue AI 編程助手 - 快速開始指南

這個文件展示了如何快速開始使用 Continue AI 編程助手。
Continue 是一個開源的 IDE AI 助手,支持多種 AI 模型。

主要內容:
1. SDK 初始化和基本配置
2. 基本聊天功能
3. 代碼解釋和分析
4. 代碼生成
5. 代碼補全建議
6. 錯誤診斷和修復
7. 文檔查詢
8. 上下文管理

Author: Continue Team
Date: 2025
"""

import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import asyncio


# =====================================================
# 第一部分: SDK 初始化和配置
# =====================================================

class ContinueConfig:
    """
    Continue 配置管理類

    管理 Continue 的所有配置選項,包括:
    - API 密鑰
    - 模型選擇
    - 上下文設置
    - 自定義選項
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置

        Args:
            config_path: 配置文件路徑,默認為 ~/.continue/config.json
        """
        self.config_path = config_path or os.path.expanduser("~/.continue/config.json")
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        從文件加載配置

        Returns:
            配置字典
        """
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 返回默認配置
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """
        獲取默認配置

        Returns:
            默認配置字典
        """
        return {
            "models": [
                {
                    "title": "GPT-4",
                    "provider": "openai",
                    "model": "gpt-4",
                    "apiKey": os.getenv("OPENAI_API_KEY", "")
                },
                {
                    "title": "Claude 3",
                    "provider": "anthropic",
                    "model": "claude-3-opus-20240229",
                    "apiKey": os.getenv("ANTHROPIC_API_KEY", "")
                }
            ],
            "context": {
                "maxTokens": 4000,
                "includeFiles": True,
                "includeTerminal": True,
                "includeGit": False
            },
            "completions": {
                "enabled": True,
                "maxSuggestions": 3,
                "debounceMs": 300
            }
        }

    def save_config(self):
        """
        保存配置到文件
        """
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        print(f"配置已保存到: {self.config_path}")

    def add_model(self, title: str, provider: str, model: str, api_key: str):
        """
        添加新的 AI 模型配置

        Args:
            title: 模型顯示名稱
            provider: 提供商 (openai, anthropic, ollama 等)
            model: 模型名稱
            api_key: API 密鑰
        """
        model_config = {
            "title": title,
            "provider": provider,
            "model": model,
            "apiKey": api_key
        }
        self.config["models"].append(model_config)
        print(f"已添加模型: {title}")

    def set_context_options(self, max_tokens: int = 4000,
                           include_files: bool = True,
                           include_terminal: bool = True,
                           include_git: bool = False):
        """
        設置上下文選項

        Args:
            max_tokens: 最大 token 數量
            include_files: 是否包含文件上下文
            include_terminal: 是否包含終端輸出
            include_git: 是否包含 Git 信息
        """
        self.config["context"] = {
            "maxTokens": max_tokens,
            "includeFiles": include_files,
            "includeTerminal": include_terminal,
            "includeGit": include_git
        }
        print("上下文選項已更新")


class ContinueSDK:
    """
    Continue SDK 主類

    提供與 Continue AI 助手交互的主要接口
    """

    def __init__(self, config: Optional[ContinueConfig] = None):
        """
        初始化 SDK

        Args:
            config: Continue 配置對象
        """
        self.config = config or ContinueConfig()
        self.current_model = self._get_default_model()
        self.conversation_history = []
        print(f"Continue SDK 已初始化,當前模型: {self.current_model['title']}")

    def _get_default_model(self) -> Dict[str, Any]:
        """
        獲取默認模型配置

        Returns:
            模型配置字典
        """
        if self.config.config["models"]:
            return self.config.config["models"][0]
        else:
            raise ValueError("沒有配置任何模型,請先添加模型配置")

    def switch_model(self, model_title: str):
        """
        切換當前使用的 AI 模型

        Args:
            model_title: 模型標題
        """
        for model in self.config.config["models"]:
            if model["title"] == model_title:
                self.current_model = model
                print(f"已切換到模型: {model_title}")
                return
        print(f"未找到模型: {model_title}")

    def chat(self, message: str, include_context: bool = True) -> str:
        """
        與 AI 助手聊天

        Args:
            message: 用戶消息
            include_context: 是否包含上下文

        Returns:
            AI 回覆
        """
        print(f"\n用戶: {message}")

        # 添加到對話歷史
        self.conversation_history.append({
            "role": "user",
            "content": message
        })

        # 模擬 AI 回覆 (實際使用時會調用真實的 API)
        response = f"[{self.current_model['title']}]: 這是對 '{message}' 的回覆"

        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })

        print(f"助手: {response}")
        return response

    def clear_history(self):
        """
        清除對話歷史
        """
        self.conversation_history = []
        print("對話歷史已清除")


# =====================================================
# 第二部分: 代碼相關功能
# =====================================================

class CodeAnalyzer:
    """
    代碼分析器

    提供代碼解釋、分析和改進建議功能
    """

    def __init__(self, sdk: ContinueSDK):
        """
        初始化代碼分析器

        Args:
            sdk: ContinueSDK 實例
        """
        self.sdk = sdk

    def explain_code(self, code: str, language: str = "python") -> str:
        """
        解釋代碼的功能

        Args:
            code: 要解釋的代碼
            language: 編程語言

        Returns:
            代碼解釋
        """
        prompt = f"""請解釋以下 {language} 代碼的功能:

```{language}
{code}
```

請提供詳細的解釋,包括:
1. 代碼的主要功能
2. 關鍵邏輯說明
3. 可能的使用場景
"""
        return self.sdk.chat(prompt)

    def analyze_complexity(self, code: str) -> str:
        """
        分析代碼複雜度

        Args:
            code: 要分析的代碼

        Returns:
            複雜度分析結果
        """
        prompt = f"""請分析以下代碼的複雜度:

```python
{code}
```

請提供:
1. 時間複雜度
2. 空間複雜度
3. 優化建議
"""
        return self.sdk.chat(prompt)

    def suggest_improvements(self, code: str) -> str:
        """
        提供代碼改進建議

        Args:
            code: 要改進的代碼

        Returns:
            改進建議
        """
        prompt = f"""請為以下代碼提供改進建議:

```python
{code}
```

請考慮:
1. 代碼可讀性
2. 性能優化
3. 最佳實踐
4. 錯誤處理
"""
        return self.sdk.chat(prompt)


class CodeGenerator:
    """
    代碼生成器

    根據需求生成代碼
    """

    def __init__(self, sdk: ContinueSDK):
        """
        初始化代碼生成器

        Args:
            sdk: ContinueSDK 實例
        """
        self.sdk = sdk

    def generate_function(self, description: str, language: str = "python") -> str:
        """
        根據描述生成函數

        Args:
            description: 函數功能描述
            language: 編程語言

        Returns:
            生成的函數代碼
        """
        prompt = f"""請用 {language} 編寫一個函數:

功能描述: {description}

要求:
1. 包含完整的文檔字符串
2. 添加類型註解
3. 包含錯誤處理
4. 遵循最佳實踐
"""
        return self.sdk.chat(prompt)

    def generate_class(self, description: str, language: str = "python") -> str:
        """
        根據描述生成類

        Args:
            description: 類功能描述
            language: 編程語言

        Returns:
            生成的類代碼
        """
        prompt = f"""請用 {language} 編寫一個類:

功能描述: {description}

要求:
1. 完整的類結構
2. 適當的方法和屬性
3. 文檔字符串
4. 使用示例
"""
        return self.sdk.chat(prompt)

    def generate_tests(self, code: str) -> str:
        """
        為代碼生成測試

        Args:
            code: 要測試的代碼

        Returns:
            測試代碼
        """
        prompt = f"""請為以下代碼生成單元測試:

```python
{code}
```

要求:
1. 使用 pytest 框架
2. 覆蓋主要功能
3. 包含邊界情況測試
4. 包含異常測試
"""
        return self.sdk.chat(prompt)


class CodeCompletion:
    """
    代碼補全助手

    提供智能代碼補全建議
    """

    def __init__(self, sdk: ContinueSDK):
        """
        初始化代碼補全助手

        Args:
            sdk: ContinueSDK 實例
        """
        self.sdk = sdk

    def get_completions(self, code_before: str, code_after: str = "") -> List[str]:
        """
        獲取代碼補全建議

        Args:
            code_before: 光標前的代碼
            code_after: 光標後的代碼

        Returns:
            補全建議列表
        """
        prompt = f"""請為以下代碼提供補全建議:

之前的代碼:
```python
{code_before}
```

之後的代碼:
```python
{code_after}
```

請提供 3 個最可能的補全選項。
"""
        response = self.sdk.chat(prompt)

        # 模擬返回補全列表
        return [
            "建議 1: ...",
            "建議 2: ...",
            "建議 3: ..."
        ]


# =====================================================
# 第三部分: 錯誤診斷和修復
# =====================================================

class ErrorDiagnostics:
    """
    錯誤診斷器

    幫助診斷和修復代碼錯誤
    """

    def __init__(self, sdk: ContinueSDK):
        """
        初始化錯誤診斷器

        Args:
            sdk: ContinueSDK 實例
        """
        self.sdk = sdk

    def diagnose_error(self, error_message: str, code: str = "") -> str:
        """
        診斷錯誤

        Args:
            error_message: 錯誤消息
            code: 相關代碼

        Returns:
            診斷結果
        """
        prompt = f"""請幫我診斷以下錯誤:

錯誤消息:
{error_message}

相關代碼:
```python
{code}
```

請提供:
1. 錯誤原因分析
2. 修復建議
3. 預防措施
"""
        return self.sdk.chat(prompt)

    def fix_code(self, code: str, error: str) -> str:
        """
        自動修復代碼

        Args:
            code: 有錯誤的代碼
            error: 錯誤描述

        Returns:
            修復後的代碼
        """
        prompt = f"""請修復以下代碼:

代碼:
```python
{code}
```

錯誤: {error}

請提供修復後的完整代碼。
"""
        return self.sdk.chat(prompt)


# =====================================================
# 第四部分: 使用示例
# =====================================================

def basic_usage_example():
    """
    基本使用示例

    展示 Continue SDK 的基本功能
    """
    print("=" * 60)
    print("示例 1: 基本設置和聊天")
    print("=" * 60)

    # 創建配置
    config = ContinueConfig()

    # 添加模型配置
    config.add_model(
        title="GPT-4 Turbo",
        provider="openai",
        model="gpt-4-turbo-preview",
        api_key=os.getenv("OPENAI_API_KEY", "your-api-key")
    )

    # 設置上下文選項
    config.set_context_options(
        max_tokens=8000,
        include_files=True,
        include_terminal=True
    )

    # 保存配置
    config.save_config()

    # 初始化 SDK
    sdk = ContinueSDK(config)

    # 基本聊天
    sdk.chat("你好,請介紹一下 Python 的 asyncio 庫")
    sdk.chat("如何使用 asyncio 處理並發任務?")

    # 切換模型
    sdk.switch_model("Claude 3")
    sdk.chat("同樣的問題,請用不同的角度解釋")


def code_analysis_example():
    """
    代碼分析示例

    展示如何使用 Continue 分析代碼
    """
    print("\n" + "=" * 60)
    print("示例 2: 代碼分析")
    print("=" * 60)

    sdk = ContinueSDK()
    analyzer = CodeAnalyzer(sdk)

    # 示例代碼
    sample_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

    # 解釋代碼
    print("\n解釋代碼:")
    analyzer.explain_code(sample_code)

    # 分析複雜度
    print("\n分析複雜度:")
    analyzer.analyze_complexity(sample_code)

    # 提供改進建議
    print("\n改進建議:")
    analyzer.suggest_improvements(sample_code)


def code_generation_example():
    """
    代碼生成示例

    展示如何使用 Continue 生成代碼
    """
    print("\n" + "=" * 60)
    print("示例 3: 代碼生成")
    print("=" * 60)

    sdk = ContinueSDK()
    generator = CodeGenerator(sdk)

    # 生成函數
    print("\n生成函數:")
    generator.generate_function("實現一個二分搜索算法")

    # 生成類
    print("\n生成類:")
    generator.generate_class("創建一個用戶管理類,支持增刪改查操作")

    # 生成測試
    print("\n生成測試:")
    test_code = """
def add(a, b):
    return a + b
"""
    generator.generate_tests(test_code)


def error_diagnosis_example():
    """
    錯誤診斷示例

    展示如何使用 Continue 診斷和修復錯誤
    """
    print("\n" + "=" * 60)
    print("示例 4: 錯誤診斷")
    print("=" * 60)

    sdk = ContinueSDK()
    diagnostics = ErrorDiagnostics(sdk)

    # 診斷錯誤
    error_msg = "IndexError: list index out of range"
    buggy_code = """
numbers = [1, 2, 3]
print(numbers[5])
"""

    print("\n診斷錯誤:")
    diagnostics.diagnose_error(error_msg, buggy_code)

    # 修復代碼
    print("\n修復代碼:")
    diagnostics.fix_code(buggy_code, error_msg)


async def async_usage_example():
    """
    異步使用示例

    展示如何異步使用 Continue
    """
    print("\n" + "=" * 60)
    print("示例 5: 異步操作")
    print("=" * 60)

    sdk = ContinueSDK()

    # 模擬異步操作
    tasks = [
        "解釋 Python 的裝飾器",
        "解釋 Python 的生成器",
        "解釋 Python 的上下文管理器"
    ]

    print("\n同時處理多個問題:")
    for task in tasks:
        sdk.chat(task)
        await asyncio.sleep(0.1)  # 模擬異步延遲


def main():
    """
    主函數

    運行所有示例
    """
    print("Continue AI 編程助手 - 快速開始")
    print("=" * 60)

    # 基本使用
    basic_usage_example()

    # 代碼分析
    code_analysis_example()

    # 代碼生成
    code_generation_example()

    # 錯誤診斷
    error_diagnosis_example()

    # 異步操作
    print("\n運行異步示例:")
    asyncio.run(async_usage_example())

    print("\n" + "=" * 60)
    print("所有示例運行完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
