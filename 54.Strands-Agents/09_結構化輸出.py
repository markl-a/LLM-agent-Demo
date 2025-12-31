"""
Strands Agents 結構化輸出示例

這個示例展示了如何實現和驗證結構化輸出：
1. Pydantic 模型定義
2. JSON Schema 生成
3. 輸出驗證
4. 自動修復
5. 類型轉換
6. 嵌套結構處理
7. 可選字段處理
8. 自定義驗證規則

結構化輸出確保 Agent 響應的格式一致性和可靠性，
是構建生產級應用的重要基礎。

作者: Strands Agents Team
日期: 2025-01
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional, Union, Literal
from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from enum import Enum
import re

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Pydantic 風格的模型定義（簡化實現）
# ============================================================================

class ValidationError(Exception):
    """驗證錯誤"""
    pass


class BaseModel:
    """
    基礎模型類

    提供類似 Pydantic 的驗證和序列化功能
    """

    def __init__(self, **data):
        """初始化模型"""
        self._validate_and_set(data)

    def _validate_and_set(self, data: Dict[str, Any]):
        """驗證並設置數據"""
        # 獲取類型註解
        annotations = getattr(self.__class__, '__annotations__', {})

        for field_name, field_type in annotations.items():
            value = data.get(field_name)

            # 檢查必需字段
            if value is None and not self._is_optional(field_type):
                # 檢查是否有默認值
                if not hasattr(self, field_name):
                    raise ValidationError(f"缺少必需字段: {field_name}")
                continue

            # 驗證類型
            if value is not None:
                validated_value = self._validate_type(field_name, value, field_type)
                setattr(self, field_name, validated_value)
            elif hasattr(self, field_name):
                # 使用默認值
                pass
            else:
                setattr(self, field_name, None)

    def _is_optional(self, field_type) -> bool:
        """檢查字段是否可選"""
        return (
            hasattr(field_type, '__origin__') and
            field_type.__origin__ is Union and
            type(None) in field_type.__args__
        )

    def _validate_type(self, field_name: str, value: Any, expected_type: Any) -> Any:
        """驗證類型"""
        # 處理 Optional
        if self._is_optional(expected_type):
            if value is None:
                return None
            # 獲取實際類型
            actual_type = [t for t in expected_type.__args__ if t != type(None)][0]
            return self._validate_type(field_name, value, actual_type)

        # 處理 List
        if hasattr(expected_type, '__origin__') and expected_type.__origin__ is list:
            if not isinstance(value, list):
                raise ValidationError(f"{field_name} 必須是列表")

            item_type = expected_type.__args__[0]
            return [self._validate_type(f"{field_name}[{i}]", item, item_type)
                    for i, item in enumerate(value)]

        # 處理 Dict
        if hasattr(expected_type, '__origin__') and expected_type.__origin__ is dict:
            if not isinstance(value, dict):
                raise ValidationError(f"{field_name} 必須是字典")
            return value

        # 處理嵌套模型
        if isinstance(expected_type, type) and issubclass(expected_type, BaseModel):
            if isinstance(value, dict):
                return expected_type(**value)
            elif isinstance(value, expected_type):
                return value
            else:
                raise ValidationError(f"{field_name} 類型不匹配")

        # 基本類型驗證
        if not isinstance(value, expected_type):
            try:
                return expected_type(value)
            except (ValueError, TypeError):
                raise ValidationError(
                    f"{field_name} 期望類型 {expected_type.__name__}，"
                    f"得到 {type(value).__name__}"
                )

        return value

    def dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        result = {}
        annotations = getattr(self.__class__, '__annotations__', {})

        for field_name in annotations.keys():
            value = getattr(self, field_name, None)

            if value is None:
                result[field_name] = None
            elif isinstance(value, BaseModel):
                result[field_name] = value.dict()
            elif isinstance(value, list):
                result[field_name] = [
                    item.dict() if isinstance(item, BaseModel) else item
                    for item in value
                ]
            else:
                result[field_name] = value

        return result

    def json(self) -> str:
        """轉換為 JSON 字符串"""
        return json.dumps(self.dict(), ensure_ascii=False, indent=2)

    @classmethod
    def schema(cls) -> Dict[str, Any]:
        """生成 JSON Schema"""
        properties = {}
        required = []
        annotations = getattr(cls, '__annotations__', {})

        for field_name, field_type in annotations.items():
            prop = cls._type_to_schema(field_type)
            properties[field_name] = prop

            # 檢查是否必需
            if not cls._is_optional_static(field_type):
                if not hasattr(cls, field_name):  # 沒有默認值
                    required.append(field_name)

        return {
            "type": "object",
            "properties": properties,
            "required": required,
            "title": cls.__name__
        }

    @classmethod
    def _is_optional_static(cls, field_type) -> bool:
        """靜態方法：檢查是否可選"""
        return (
            hasattr(field_type, '__origin__') and
            field_type.__origin__ is Union and
            type(None) in field_type.__args__
        )

    @classmethod
    def _type_to_schema(cls, field_type: Any) -> Dict[str, Any]:
        """將 Python 類型轉換為 JSON Schema"""
        # 處理 Optional
        if cls._is_optional_static(field_type):
            actual_type = [t for t in field_type.__args__ if t != type(None)][0]
            schema = cls._type_to_schema(actual_type)
            return schema

        # 處理 List
        if hasattr(field_type, '__origin__') and field_type.__origin__ is list:
            item_type = field_type.__args__[0]
            return {
                "type": "array",
                "items": cls._type_to_schema(item_type)
            }

        # 處理 Dict
        if hasattr(field_type, '__origin__') and field_type.__origin__ is dict:
            return {"type": "object"}

        # 處理嵌套模型
        if isinstance(field_type, type) and issubclass(field_type, BaseModel):
            return field_type.schema()

        # 基本類型
        type_mapping = {
            str: {"type": "string"},
            int: {"type": "integer"},
            float: {"type": "number"},
            bool: {"type": "boolean"}
        }

        return type_mapping.get(field_type, {"type": "string"})


# ============================================================================
# 示例模型定義
# ============================================================================

class TaskPriority(str, Enum):
    """任務優先級"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Address(BaseModel):
    """地址模型"""
    street: str
    city: str
    country: str
    postal_code: Optional[str] = None


class Person(BaseModel):
    """人員模型"""
    name: str
    age: int
    email: str
    phone: Optional[str] = None
    address: Optional[Address] = None


class Task(BaseModel):
    """任務模型"""
    title: str
    description: str
    priority: str  # TaskPriority
    assigned_to: Optional[str] = None
    due_date: Optional[str] = None
    tags: List[str] = []
    completed: bool = False


class ProjectSummary(BaseModel):
    """項目摘要模型"""
    project_name: str
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    team_members: List[str]
    key_milestones: List[str]
    risk_assessment: str
    recommendations: List[str]


class AnalysisResult(BaseModel):
    """分析結果模型"""
    summary: str
    confidence_score: float
    key_findings: List[str]
    data_points: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class ConversationTurn(BaseModel):
    """對話輪次模型"""
    speaker: str
    message: str
    timestamp: str
    intent: Optional[str] = None
    entities: List[Dict[str, str]] = []


class DialogueSummary(BaseModel):
    """對話摘要模型"""
    participants: List[str]
    turn_count: int
    main_topics: List[str]
    action_items: List[str]
    sentiment: str
    summary: str


# ============================================================================
# 結構化輸出生成器
# ============================================================================

class StructuredOutputGenerator:
    """
    結構化輸出生成器

    將 LLM 的文本輸出轉換為結構化對象
    """

    def __init__(self):
        logger.info("初始化結構化輸出生成器")

    def generate(
        self,
        text: str,
        model_class: type,
        auto_fix: bool = True
    ) -> BaseModel:
        """
        生成結構化輸出

        Args:
            text: LLM 輸出的文本
            model_class: 目標模型類
            auto_fix: 是否自動修復

        Returns:
            BaseModel: 結構化對象
        """
        try:
            # 嘗試從文本中提取 JSON
            json_data = self._extract_json(text)

            # 驗證和創建模型
            model_instance = model_class(**json_data)

            logger.info(f"成功生成結構化輸出: {model_class.__name__}")

            return model_instance

        except ValidationError as e:
            logger.error(f"驗證錯誤: {str(e)}")

            if auto_fix:
                # 嘗試自動修復
                logger.info("嘗試自動修復...")
                fixed_data = self._auto_fix(json_data, model_class)

                try:
                    return model_class(**fixed_data)
                except Exception as fix_error:
                    logger.error(f"自動修復失敗: {str(fix_error)}")
                    raise

            raise

        except Exception as e:
            logger.error(f"生成結構化輸出失敗: {str(e)}")
            raise

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        從文本中提取 JSON

        Args:
            text: 文本

        Returns:
            Dict: 提取的 JSON 數據
        """
        # 嘗試直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 嘗試從 Markdown 代碼塊中提取
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # 嘗試查找任何 JSON 對象
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        raise ValueError("無法從文本中提取有效的 JSON")

    def _auto_fix(
        self,
        data: Dict[str, Any],
        model_class: type
    ) -> Dict[str, Any]:
        """
        自動修復數據

        Args:
            data: 原始數據
            model_class: 模型類

        Returns:
            Dict: 修復後的數據
        """
        fixed_data = data.copy()
        annotations = getattr(model_class, '__annotations__', {})

        for field_name, field_type in annotations.items():
            if field_name not in fixed_data:
                # 添加缺失的必需字段
                if not model_class._is_optional_static(field_type):
                    fixed_data[field_name] = self._get_default_value(field_type)

        return fixed_data

    def _get_default_value(self, field_type: Any) -> Any:
        """獲取類型的默認值"""
        if field_type == str:
            return ""
        elif field_type == int:
            return 0
        elif field_type == float:
            return 0.0
        elif field_type == bool:
            return False
        elif hasattr(field_type, '__origin__') and field_type.__origin__ is list:
            return []
        elif hasattr(field_type, '__origin__') and field_type.__origin__ is dict:
            return {}
        else:
            return None


# ============================================================================
# 提示詞生成器
# ============================================================================

class PromptGenerator:
    """
    提示詞生成器

    生成包含結構化輸出要求的提示詞
    """

    @staticmethod
    def generate_schema_prompt(
        task_description: str,
        model_class: type,
        examples: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        生成包含 Schema 的提示詞

        Args:
            task_description: 任務描述
            model_class: 模型類
            examples: 示例數據

        Returns:
            str: 提示詞
        """
        schema = model_class.schema()

        prompt_parts = [
            task_description,
            "\n\n請按照以下 JSON Schema 格式輸出結果：\n",
            json.dumps(schema, indent=2, ensure_ascii=False),
            "\n\n輸出格式要求：",
            "- 必須是有效的 JSON 格式",
            "- 包含所有必需字段",
            "- 遵循指定的數據類型",
            "- 不要包含 Schema 中未定義的額外字段"
        ]

        if examples:
            prompt_parts.append("\n\n示例輸出：")
            for i, example in enumerate(examples, 1):
                prompt_parts.append(f"\n示例 {i}:")
                prompt_parts.append(json.dumps(example, indent=2, ensure_ascii=False))

        return "\n".join(prompt_parts)


# ============================================================================
# 示例和測試
# ============================================================================

def demonstrate_basic_models():
    """演示基本模型"""
    print("\n" + "="*60)
    print("示例 1: 基本模型定義和驗證")
    print("="*60 + "\n")

    # 創建人員對象
    person = Person(
        name="張三",
        age=30,
        email="zhangsan@example.com",
        phone="0912-345-678",
        address=Address(
            street="信義路五段7號",
            city="台北市",
            country="台灣",
            postal_code="110"
        )
    )

    print("人員信息:")
    print(person.json())

    print("\nJSON Schema:")
    print(json.dumps(Person.schema(), indent=2, ensure_ascii=False))


def demonstrate_task_model():
    """演示任務模型"""
    print("\n" + "="*60)
    print("示例 2: 任務模型")
    print("="*60 + "\n")

    # 創建任務
    task = Task(
        title="實現結構化輸出",
        description="為 Strands Agents 添加結構化輸出功能",
        priority="high",
        assigned_to="張三",
        due_date="2025-02-01",
        tags=["開發", "功能", "優先"],
        completed=False
    )

    print("任務信息:")
    print(task.json())


def demonstrate_structured_generation():
    """演示結構化輸出生成"""
    print("\n" + "="*60)
    print("示例 3: 從文本生成結構化輸出")
    print("="*60 + "\n")

    generator = StructuredOutputGenerator()

    # 模擬 LLM 輸出（包含 JSON）
    llm_output = """
    這是項目的分析結果：

    ```json
    {
        "summary": "項目進展順利，已完成 70% 的任務",
        "confidence_score": 0.85,
        "key_findings": [
            "團隊協作良好",
            "技術實現符合預期",
            "存在一些小的性能問題"
        ],
        "data_points": {
            "completion_rate": 0.7,
            "bug_count": 5,
            "test_coverage": 0.82
        }
    }
    ```
    """

    # 生成結構化輸出
    result = generator.generate(llm_output, AnalysisResult)

    print("生成的結構化輸出:")
    print(result.json())


def demonstrate_validation():
    """演示驗證和錯誤處理"""
    print("\n" + "="*60)
    print("示例 4: 驗證和錯誤處理")
    print("="*60 + "\n")

    generator = StructuredOutputGenerator()

    # 缺少必需字段的數據
    invalid_json = """
    {
        "summary": "分析摘要",
        "key_findings": ["發現1", "發現2"]
    }
    """

    print("嘗試解析缺少必需字段的數據:")

    try:
        result = generator.generate(
            invalid_json,
            AnalysisResult,
            auto_fix=True
        )
        print("自動修復成功:")
        print(result.json())
    except Exception as e:
        print(f"驗證失敗: {str(e)}")


def demonstrate_prompt_generation():
    """演示提示詞生成"""
    print("\n" + "="*60)
    print("示例 5: 提示詞生成")
    print("="*60 + "\n")

    # 生成任務的提示詞
    prompt = PromptGenerator.generate_schema_prompt(
        task_description="請分析以下對話並生成摘要",
        model_class=DialogueSummary,
        examples=[{
            "participants": ["Alice", "Bob"],
            "turn_count": 5,
            "main_topics": ["項目規劃", "時間安排"],
            "action_items": ["準備文檔", "安排會議"],
            "sentiment": "positive",
            "summary": "討論了項目規劃和下一步行動"
        }]
    )

    print("生成的提示詞:")
    print(prompt)


def demonstrate_complex_model():
    """演示複雜嵌套模型"""
    print("\n" + "="*60)
    print("示例 6: 複雜嵌套模型")
    print("="*60 + "\n")

    # 創建項目摘要
    summary = ProjectSummary(
        project_name="Strands Agents 開發",
        total_tasks=20,
        completed_tasks=14,
        pending_tasks=6,
        team_members=["張三", "李四", "王五"],
        key_milestones=[
            "完成核心功能",
            "集成測試通過",
            "文檔編寫完成"
        ],
        risk_assessment="整體風險較低，進展順利",
        recommendations=[
            "加強性能測試",
            "增加更多示例",
            "完善錯誤處理"
        ]
    )

    print("項目摘要:")
    print(summary.json())

    print("\nSchema:")
    print(json.dumps(ProjectSummary.schema(), indent=2, ensure_ascii=False))


def main():
    """主函數"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*17 + "結構化輸出示例" + " "*20 + "║")
    print("╚" + "="*58 + "╝")

    try:
        demonstrate_basic_models()
        demonstrate_task_model()
        demonstrate_structured_generation()
        demonstrate_validation()
        demonstrate_prompt_generation()
        demonstrate_complex_model()

        print("\n" + "="*60)
        print("所有示例執行完成！")
        print("="*60)

        print("\n結構化輸出的優勢:")
        print("  1. 類型安全：編譯時檢查數據類型")
        print("  2. 自動驗證：確保數據完整性和正確性")
        print("  3. 一致性：保證輸出格式統一")
        print("  4. 易於集成：直接映射到應用程序對象")
        print("  5. 自文檔化：Schema 即文檔")

    except Exception as e:
        logger.error(f"執行錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
