"""
Atomic Agents 原子工具設計
=========================

本文件展示如何創建和使用原子工具（Atomic Tools）。
原子工具是具有清晰輸入輸出接口的可重用組件。

主要內容：
1. 工具基礎類
2. 內置工具實現
3. 自定義工具創建
4. 工具組合
5. 工具註冊和發現
6. 異步工具

作者：Atomic Agents 團隊
日期：2025-12-31
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, TypeVar, Generic
from pydantic import BaseModel, Field, validator
from dataclasses import dataclass, field
from datetime import datetime
import json
import hashlib
import re
from enum import Enum


# ============================================================================
# 第一部分：工具基礎架構
# ============================================================================

class ToolInput(BaseModel):
    """工具輸入基類"""
    pass


class ToolOutput(BaseModel):
    """工具輸出基類"""
    success: bool = Field(..., description="操作是否成功")
    error: Optional[str] = Field(None, description="錯誤信息")
    timestamp: datetime = Field(default_factory=datetime.now)


T_Input = TypeVar('T_Input', bound=ToolInput)
T_Output = TypeVar('T_Output', bound=ToolOutput)


class BaseTool(ABC, Generic[T_Input, T_Output]):
    """
    工具基類

    所有原子工具都應該繼承這個類。
    """

    def __init__(self, name: str, description: str):
        """
        初始化工具

        Args:
            name: 工具名稱
            description: 工具描述
        """
        self.name = name
        self.description = description
        self.execution_count = 0
        self.total_execution_time = 0.0

    @abstractmethod
    def execute(self, input_data: T_Input) -> T_Output:
        """
        執行工具

        Args:
            input_data: 輸入數據

        Returns:
            輸出數據
        """
        pass

    def run(self, input_data: T_Input) -> T_Output:
        """
        運行工具（包含統計和日誌）

        Args:
            input_data: 輸入數據

        Returns:
            輸出數據
        """
        start_time = datetime.now()
        print(f"\n[{self.name}] 開始執行...")

        try:
            result = self.execute(input_data)
            self.execution_count += 1

            execution_time = (datetime.now() - start_time).total_seconds()
            self.total_execution_time += execution_time

            print(f"[{self.name}] 執行成功 ({execution_time:.2f}秒)")
            return result

        except Exception as e:
            print(f"[{self.name}] 執行失敗: {str(e)}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """獲取工具統計信息"""
        avg_time = (
            self.total_execution_time / self.execution_count
            if self.execution_count > 0
            else 0
        )
        return {
            'name': self.name,
            'execution_count': self.execution_count,
            'total_time': self.total_execution_time,
            'average_time': avg_time
        }


# ============================================================================
# 第二部分：文本處理工具
# ============================================================================

class TextInput(ToolInput):
    """文本輸入"""
    text: str = Field(..., description="要處理的文本")


class TextOutput(ToolOutput):
    """文本輸出"""
    result: str = Field(..., description="處理結果")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TextLengthTool(BaseTool[TextInput, TextOutput]):
    """文本長度分析工具"""

    def __init__(self):
        super().__init__(
            name="TextLength",
            description="計算文本的長度統計信息"
        )

    def execute(self, input_data: TextInput) -> TextOutput:
        """執行文本長度分析"""
        text = input_data.text
        char_count = len(text)
        word_count = len(text.split())
        line_count = len(text.splitlines())

        result = f"字符數: {char_count}, 詞數: {word_count}, 行數: {line_count}"

        return TextOutput(
            success=True,
            result=result,
            metadata={
                'char_count': char_count,
                'word_count': word_count,
                'line_count': line_count
            }
        )


class TextCleanerTool(BaseTool[TextInput, TextOutput]):
    """文本清理工具"""

    def __init__(self, remove_punctuation: bool = False):
        super().__init__(
            name="TextCleaner",
            description="清理和規範化文本"
        )
        self.remove_punctuation = remove_punctuation

    def execute(self, input_data: TextInput) -> TextOutput:
        """執行文本清理"""
        text = input_data.text

        # 移除多餘空白
        text = ' '.join(text.split())

        # 移除標點符號（可選）
        if self.remove_punctuation:
            text = re.sub(r'[^\w\s]', '', text)

        return TextOutput(
            success=True,
            result=text,
            metadata={'original_length': len(input_data.text)}
        )


class KeywordExtractorTool(BaseTool[TextInput, TextOutput]):
    """關鍵詞提取工具"""

    def __init__(self, top_k: int = 5):
        super().__init__(
            name="KeywordExtractor",
            description="從文本中提取關鍵詞"
        )
        self.top_k = top_k

    def execute(self, input_data: TextInput) -> TextOutput:
        """執行關鍵詞提取"""
        text = input_data.text.lower()
        words = re.findall(r'\w+', text)

        # 簡單的詞頻統計
        word_freq = {}
        for word in words:
            if len(word) > 3:  # 只考慮長度大於3的詞
                word_freq[word] = word_freq.get(word, 0) + 1

        # 獲取前 k 個關鍵詞
        top_keywords = sorted(
            word_freq.items(),
            key=lambda x: x[1],
            reverse=True
        )[:self.top_k]

        keywords = [word for word, _ in top_keywords]
        result = ', '.join(keywords)

        return TextOutput(
            success=True,
            result=result,
            metadata={'keywords': keywords, 'frequencies': dict(top_keywords)}
        )


# ============================================================================
# 第三部分：數據處理工具
# ============================================================================

class DataInput(ToolInput):
    """數據輸入"""
    data: Dict[str, Any] = Field(..., description="要處理的數據")


class DataOutput(ToolOutput):
    """數據輸出"""
    data: Dict[str, Any] = Field(..., description="處理後的數據")


class DataValidatorTool(BaseTool[DataInput, DataOutput]):
    """數據驗證工具"""

    def __init__(self, required_fields: List[str]):
        super().__init__(
            name="DataValidator",
            description="驗證數據是否包含必需字段"
        )
        self.required_fields = required_fields

    def execute(self, input_data: DataInput) -> DataOutput:
        """執行數據驗證"""
        data = input_data.data
        missing_fields = []

        for field in self.required_fields:
            if field not in data:
                missing_fields.append(field)

        if missing_fields:
            return DataOutput(
                success=False,
                error=f"缺少必需字段: {', '.join(missing_fields)}",
                data=data
            )

        return DataOutput(
            success=True,
            data=data
        )


class DataTransformerTool(BaseTool[DataInput, DataOutput]):
    """數據轉換工具"""

    def __init__(self, transformations: Dict[str, Callable]):
        super().__init__(
            name="DataTransformer",
            description="對數據字段應用轉換函數"
        )
        self.transformations = transformations

    def execute(self, input_data: DataInput) -> DataOutput:
        """執行數據轉換"""
        data = input_data.data.copy()

        for field, transform_func in self.transformations.items():
            if field in data:
                try:
                    data[field] = transform_func(data[field])
                except Exception as e:
                    return DataOutput(
                        success=False,
                        error=f"轉換字段 {field} 失敗: {str(e)}",
                        data=data
                    )

        return DataOutput(
            success=True,
            data=data
        )


class DataFilterTool(BaseTool[DataInput, DataOutput]):
    """數據過濾工具"""

    def __init__(self, allowed_fields: Optional[List[str]] = None):
        super().__init__(
            name="DataFilter",
            description="過濾數據字段"
        )
        self.allowed_fields = allowed_fields

    def execute(self, input_data: DataInput) -> DataOutput:
        """執行數據過濾"""
        data = input_data.data

        if self.allowed_fields:
            filtered_data = {
                k: v for k, v in data.items()
                if k in self.allowed_fields
            }
        else:
            filtered_data = data

        return DataOutput(
            success=True,
            data=filtered_data
        )


# ============================================================================
# 第四部分：計算和分析工具
# ============================================================================

class CalculationInput(ToolInput):
    """計算輸入"""
    values: List[float] = Field(..., description="數值列表")


class CalculationOutput(ToolOutput):
    """計算輸出"""
    result: float = Field(..., description="計算結果")
    details: Dict[str, Any] = Field(default_factory=dict)


class StatisticsTool(BaseTool[CalculationInput, CalculationOutput]):
    """統計計算工具"""

    def __init__(self):
        super().__init__(
            name="Statistics",
            description="計算數值的統計信息"
        )

    def execute(self, input_data: CalculationInput) -> CalculationOutput:
        """執行統計計算"""
        values = input_data.values

        if not values:
            return CalculationOutput(
                success=False,
                error="數值列表為空",
                result=0.0
            )

        mean = sum(values) / len(values)
        sorted_values = sorted(values)
        median = sorted_values[len(values) // 2]
        min_val = min(values)
        max_val = max(values)

        # 計算標準差
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5

        return CalculationOutput(
            success=True,
            result=mean,
            details={
                'mean': mean,
                'median': median,
                'min': min_val,
                'max': max_val,
                'std_dev': std_dev,
                'count': len(values)
            }
        )


# ============================================================================
# 第五部分：工具組合器
# ============================================================================

class ToolPipeline:
    """
    工具管道

    將多個工具串聯成一個處理管道。
    """

    def __init__(self, name: str):
        self.name = name
        self.tools: List[BaseTool] = []

    def add_tool(self, tool: BaseTool) -> 'ToolPipeline':
        """添加工具到管道"""
        self.tools.append(tool)
        return self

    def execute(self, initial_input: Any) -> Any:
        """執行管道"""
        print(f"\n{'='*60}")
        print(f"執行工具管道: {self.name}")
        print(f"{'='*60}")

        current_output = initial_input

        for i, tool in enumerate(self.tools, 1):
            print(f"\n步驟 {i}: {tool.name}")
            current_output = tool.run(current_output)

            if hasattr(current_output, 'success') and not current_output.success:
                print(f"\n管道在步驟 {i} 失敗")
                return current_output

        print(f"\n{'='*60}")
        print("管道執行完成")
        print(f"{'='*60}")

        return current_output


# ============================================================================
# 第六部分：工具註冊表
# ============================================================================

class ToolRegistry:
    """
    工具註冊表

    管理和發現可用的工具。
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """註冊工具"""
        self._tools[tool.name] = tool
        print(f"工具已註冊: {tool.name}")

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """獲取工具"""
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, str]]:
        """列出所有工具"""
        return [
            {'name': tool.name, 'description': tool.description}
            for tool in self._tools.values()
        ]

    def search_tools(self, query: str) -> List[BaseTool]:
        """搜索工具"""
        query = query.lower()
        results = []

        for tool in self._tools.values():
            if (query in tool.name.lower() or
                query in tool.description.lower()):
                results.append(tool)

        return results


# ============================================================================
# 第七部分：高級工具示例
# ============================================================================

class CacheInput(ToolInput):
    """緩存輸入"""
    key: str = Field(..., description="緩存鍵")
    value: Optional[Any] = Field(None, description="要緩存的值")
    operation: str = Field(..., description="操作: get/set/delete")


class CacheOutput(ToolOutput):
    """緩存輸出"""
    value: Optional[Any] = Field(None, description="緩存的值")
    hit: bool = Field(default=False, description="是否命中緩存")


class CacheTool(BaseTool[CacheInput, CacheOutput]):
    """緩存工具"""

    def __init__(self):
        super().__init__(
            name="Cache",
            description="簡單的內存緩存工具"
        )
        self._cache: Dict[str, Any] = {}

    def execute(self, input_data: CacheInput) -> CacheOutput:
        """執行緩存操作"""
        operation = input_data.operation
        key = input_data.key

        if operation == "get":
            value = self._cache.get(key)
            return CacheOutput(
                success=True,
                value=value,
                hit=key in self._cache
            )

        elif operation == "set":
            self._cache[key] = input_data.value
            return CacheOutput(
                success=True,
                value=input_data.value
            )

        elif operation == "delete":
            if key in self._cache:
                del self._cache[key]
            return CacheOutput(success=True)

        else:
            return CacheOutput(
                success=False,
                error=f"未知操作: {operation}"
            )


class HashInput(ToolInput):
    """雜湊輸入"""
    data: str = Field(..., description="要雜湊的數據")
    algorithm: str = Field(default="sha256", description="雜湊算法")


class HashOutput(ToolOutput):
    """雜湊輸出"""
    hash_value: str = Field(..., description="雜湊值")


class HashTool(BaseTool[HashInput, HashOutput]):
    """雜湊工具"""

    def __init__(self):
        super().__init__(
            name="Hash",
            description="生成數據的雜湊值"
        )

    def execute(self, input_data: HashInput) -> HashOutput:
        """執行雜湊計算"""
        data = input_data.data.encode('utf-8')
        algorithm = input_data.algorithm

        try:
            if algorithm == "sha256":
                hash_obj = hashlib.sha256(data)
            elif algorithm == "md5":
                hash_obj = hashlib.md5(data)
            else:
                return HashOutput(
                    success=False,
                    error=f"不支持的算法: {algorithm}",
                    hash_value=""
                )

            hash_value = hash_obj.hexdigest()

            return HashOutput(
                success=True,
                hash_value=hash_value
            )

        except Exception as e:
            return HashOutput(
                success=False,
                error=str(e),
                hash_value=""
            )


# ============================================================================
# 第八部分：使用示例
# ============================================================================

def example_text_tools():
    """文本工具示例"""
    print("\n" + "="*60)
    print("示例 1: 文本處理工具")
    print("="*60)

    text = """
    Atomic Agents 是一個輕量級、模組化的框架。
    它專注於構建具有清晰輸入輸出模式的 AI 代理。
    框架強調可預測性和可測試性。
    """

    # 文本長度分析
    length_tool = TextLengthTool()
    result = length_tool.run(TextInput(text=text))
    print(f"\n長度分析結果: {result.result}")
    print(f"元數據: {result.metadata}")

    # 關鍵詞提取
    keyword_tool = KeywordExtractorTool(top_k=5)
    result = keyword_tool.run(TextInput(text=text))
    print(f"\n關鍵詞: {result.result}")


def example_data_tools():
    """數據工具示例"""
    print("\n" + "="*60)
    print("示例 2: 數據處理工具")
    print("="*60)

    data = {
        'name': 'John Doe',
        'age': '30',
        'email': 'john@example.com',
        'score': '95.5'
    }

    # 數據驗證
    validator = DataValidatorTool(required_fields=['name', 'email'])
    result = validator.run(DataInput(data=data))
    print(f"\n驗證結果: {'通過' if result.success else '失敗'}")

    # 數據轉換
    transformer = DataTransformerTool({
        'age': int,
        'score': float
    })
    result = transformer.run(DataInput(data=data))
    print(f"\n轉換後的數據: {result.data}")


def example_tool_pipeline():
    """工具管道示例"""
    print("\n" + "="*60)
    print("示例 3: 工具管道")
    print("="*60)

    # 創建管道
    pipeline = ToolPipeline("文本分析管道")
    pipeline.add_tool(TextCleanerTool())
    pipeline.add_tool(TextLengthTool())
    pipeline.add_tool(KeywordExtractorTool())

    # 執行管道
    text = "   Atomic   Agents   框架   非常   強大！！！   "
    result = pipeline.execute(TextInput(text=text))


def example_tool_registry():
    """工具註冊表示例"""
    print("\n" + "="*60)
    print("示例 4: 工具註冊表")
    print("="*60)

    # 創建註冊表
    registry = ToolRegistry()

    # 註冊工具
    registry.register(TextLengthTool())
    registry.register(KeywordExtractorTool())
    registry.register(DataValidatorTool(['name']))
    registry.register(HashTool())

    # 列出所有工具
    print("\n可用的工具:")
    for tool_info in registry.list_tools():
        print(f"  - {tool_info['name']}: {tool_info['description']}")

    # 搜索工具
    print("\n搜索 'text' 相關的工具:")
    results = registry.search_tools('text')
    for tool in results:
        print(f"  - {tool.name}")


def example_advanced_tools():
    """高級工具示例"""
    print("\n" + "="*60)
    print("示例 5: 高級工具")
    print("="*60)

    # 緩存工具
    cache_tool = CacheTool()

    # 設置緩存
    cache_tool.run(CacheInput(
        key="user_123",
        value={"name": "Alice", "age": 25},
        operation="set"
    ))

    # 獲取緩存
    result = cache_tool.run(CacheInput(
        key="user_123",
        operation="get"
    ))
    print(f"\n緩存值: {result.value}")
    print(f"緩存命中: {result.hit}")

    # 雜湊工具
    hash_tool = HashTool()
    result = hash_tool.run(HashInput(
        data="Atomic Agents",
        algorithm="sha256"
    ))
    print(f"\nSHA-256 雜湊: {result.hash_value}")


def example_statistics():
    """統計工具示例"""
    print("\n" + "="*60)
    print("示例 6: 統計計算")
    print("="*60)

    stats_tool = StatisticsTool()
    values = [10.5, 20.3, 15.7, 30.2, 25.1, 18.9, 22.4]

    result = stats_tool.run(CalculationInput(values=values))

    print(f"\n統計結果:")
    print(f"  平均值: {result.details['mean']:.2f}")
    print(f"  中位數: {result.details['median']:.2f}")
    print(f"  最小值: {result.details['min']:.2f}")
    print(f"  最大值: {result.details['max']:.2f}")
    print(f"  標準差: {result.details['std_dev']:.2f}")


def main():
    """主函數"""
    print("\n" + "="*60)
    print("Atomic Agents 原子工具設計")
    print("="*60)

    # 運行示例
    example_text_tools()
    example_data_tools()
    example_tool_pipeline()
    example_tool_registry()
    example_advanced_tools()
    example_statistics()

    print("\n" + "="*60)
    print("所有示例運行完成！")
    print("="*60)


if __name__ == "__main__":
    main()
