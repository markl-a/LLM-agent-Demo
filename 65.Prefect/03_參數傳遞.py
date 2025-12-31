#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prefect 參數傳遞與結果處理
===========================

這個示例展示了 Prefect 中參數和結果的處理方法，包括：
1. 任務間參數傳遞
2. Flow 參數定義
3. 結果對象使用
4. 參數驗證
5. 默認值處理
6. 複雜數據類型傳遞
"""

from prefect import task, flow, get_run_logger
from prefect.task_runners import ConcurrentTaskRunner
from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel, Field, validator
from datetime import datetime
import json


# ============================================================================
# 數據模型定義
# ============================================================================

class UserData(BaseModel):
    """
    用戶數據模型

    使用 Pydantic 進行數據驗證
    """
    user_id: int = Field(..., description="用戶 ID")
    name: str = Field(..., description="用戶名稱")
    email: str = Field(..., description="電子郵件")
    age: Optional[int] = Field(None, ge=0, le=150, description="年齡")
    tags: List[str] = Field(default_factory=list, description="標籤列表")

    @validator('email')
    def validate_email(cls, v):
        """驗證郵箱格式"""
        if '@' not in v:
            raise ValueError('無效的郵箱地址')
        return v


class ProcessResult(BaseModel):
    """
    處理結果模型
    """
    success: bool = Field(..., description="是否成功")
    data: Dict = Field(default_factory=dict, description="結果數據")
    message: str = Field("", description="消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="時間戳")


# ============================================================================
# 基本參數傳遞
# ============================================================================

@task
def add_numbers(a: int, b: int) -> int:
    """
    最簡單的參數傳遞示例

    Args:
        a: 第一個數字
        b: 第二個數字

    Returns:
        兩數之和
    """
    logger = get_run_logger()
    logger.info(f"計算 {a} + {b}")
    return a + b


@task
def multiply_result(value: int, multiplier: int = 2) -> int:
    """
    帶默認值的參數

    Args:
        value: 要乘的值
        multiplier: 乘數（默認為 2）

    Returns:
        乘積
    """
    logger = get_run_logger()
    logger.info(f"計算 {value} × {multiplier}")
    return value * multiplier


@flow(name="基本參數傳遞")
def basic_parameter_flow(x: int, y: int, multiplier: int = 3):
    """
    演示基本參數傳遞

    Args:
        x: 第一個數字
        y: 第二個數字
        multiplier: 乘數
    """
    logger = get_run_logger()
    logger.info(f"輸入參數：x={x}, y={y}, multiplier={multiplier}")

    # 任務間傳遞參數
    sum_result = add_numbers(x, y)
    final_result = multiply_result(sum_result, multiplier)

    logger.info(f"最終結果：{final_result}")
    return final_result


# ============================================================================
# 複雜數據類型傳遞
# ============================================================================

@task
def process_list(items: List[int]) -> Dict[str, any]:
    """
    處理列表數據

    Args:
        items: 整數列表

    Returns:
        統計信息字典
    """
    logger = get_run_logger()
    logger.info(f"處理 {len(items)} 個項目")

    result = {
        "count": len(items),
        "sum": sum(items),
        "average": sum(items) / len(items) if items else 0,
        "max": max(items) if items else None,
        "min": min(items) if items else None
    }

    return result


@task
def process_dict(data: Dict[str, any]) -> str:
    """
    處理字典數據

    Args:
        data: 字典數據

    Returns:
        JSON 字符串
    """
    logger = get_run_logger()
    logger.info(f"處理字典數據：{len(data)} 個鍵")

    # 轉換為 JSON
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    logger.info(f"JSON 輸出：\n{json_str}")

    return json_str


@flow(name="複雜數據類型傳遞")
def complex_data_flow(numbers: List[int], metadata: Dict[str, any]):
    """
    演示複雜數據類型的傳遞

    Args:
        numbers: 數字列表
        metadata: 元數據字典
    """
    logger = get_run_logger()
    logger.info("處理複雜數據類型")

    # 處理列表
    stats = process_list(numbers)
    logger.info(f"統計結果：{stats}")

    # 處理字典
    json_output = process_dict(metadata)

    return {"stats": stats, "metadata_json": json_output}


# ============================================================================
# Pydantic 模型參數
# ============================================================================

@task
def validate_user(user_data: Dict) -> UserData:
    """
    驗證用戶數據

    Args:
        user_data: 用戶數據字典

    Returns:
        驗證後的 UserData 對象
    """
    logger = get_run_logger()
    logger.info(f"驗證用戶數據：{user_data.get('name')}")

    try:
        user = UserData(**user_data)
        logger.info(f"✓ 用戶數據有效：{user.name} ({user.email})")
        return user
    except Exception as e:
        logger.error(f"✗ 數據驗證失敗：{e}")
        raise


@task
def process_user(user: UserData) -> ProcessResult:
    """
    處理用戶數據

    Args:
        user: UserData 對象

    Returns:
        ProcessResult 對象
    """
    logger = get_run_logger()
    logger.info(f"處理用戶：{user.name}")

    # 模擬處理
    result = ProcessResult(
        success=True,
        data={
            "user_id": user.user_id,
            "processed_name": user.name.upper(),
            "domain": user.email.split('@')[1],
            "tag_count": len(user.tags)
        },
        message=f"成功處理用戶 {user.name}"
    )

    logger.info(f"處理完成：{result.message}")
    return result


@flow(name="Pydantic 模型示例")
def pydantic_model_flow(user_data: Dict):
    """
    使用 Pydantic 模型的工作流

    Args:
        user_data: 用戶數據字典
    """
    logger = get_run_logger()
    logger.info("開始 Pydantic 模型工作流")

    # 驗證數據
    user = validate_user(user_data)

    # 處理數據
    result = process_user(user)

    logger.info(f"工作流完成：{result.message}")
    return result


# ============================================================================
# 多返回值處理
# ============================================================================

@task
def split_data(data: List[int], split_ratio: float = 0.8) -> Tuple[List[int], List[int]]:
    """
    分割數據集

    Args:
        data: 數據列表
        split_ratio: 分割比例

    Returns:
        訓練集和測試集的元組
    """
    logger = get_run_logger()
    split_point = int(len(data) * split_ratio)

    train_data = data[:split_point]
    test_data = data[split_point:]

    logger.info(f"分割數據：{len(train_data)} 訓練 + {len(test_data)} 測試")
    return train_data, test_data


@task
def train_model(train_data: List[int]) -> Dict[str, any]:
    """
    訓練模型（模擬）

    Args:
        train_data: 訓練數據

    Returns:
        模型信息
    """
    logger = get_run_logger()
    logger.info(f"使用 {len(train_data)} 個樣本訓練模型")

    model = {
        "type": "linear",
        "train_size": len(train_data),
        "accuracy": 0.95
    }

    return model


@task
def evaluate_model(model: Dict[str, any], test_data: List[int]) -> Dict[str, any]:
    """
    評估模型（模擬）

    Args:
        model: 模型信息
        test_data: 測試數據

    Returns:
        評估結果
    """
    logger = get_run_logger()
    logger.info(f"使用 {len(test_data)} 個樣本評估模型")

    metrics = {
        "model_type": model["type"],
        "test_size": len(test_data),
        "accuracy": 0.93,
        "precision": 0.94,
        "recall": 0.92
    }

    return metrics


@flow(name="多返回值處理")
def multiple_returns_flow(data: List[int]):
    """
    演示多返回值處理

    Args:
        data: 數據列表
    """
    logger = get_run_logger()
    logger.info("開始機器學習工作流")

    # 分割數據（返回兩個值）
    train_data, test_data = split_data(data, split_ratio=0.8)

    # 訓練模型
    model = train_model(train_data)

    # 評估模型
    metrics = evaluate_model(model, test_data)

    logger.info(f"模型評估完成：準確率 {metrics['accuracy']:.2%}")
    return metrics


# ============================================================================
# 可選參數和默認值
# ============================================================================

@task
def fetch_data(
    source: str,
    limit: Optional[int] = None,
    filters: Optional[Dict] = None
) -> List[Dict]:
    """
    獲取數據（帶可選參數）

    Args:
        source: 數據源
        limit: 記錄限制（可選）
        filters: 過濾條件（可選）

    Returns:
        數據列表
    """
    logger = get_run_logger()
    logger.info(f"從 {source} 獲取數據")

    if limit:
        logger.info(f"限制：{limit} 條記錄")
    if filters:
        logger.info(f"過濾條件：{filters}")

    # 模擬數據獲取
    data = [
        {"id": i, "value": i * 10}
        for i in range(1, (limit or 5) + 1)
    ]

    return data


@flow(name="可選參數示例")
def optional_parameters_flow():
    """
    演示可選參數的使用
    """
    logger = get_run_logger()

    # 只傳必需參數
    logger.info("\n--- 只傳必需參數 ---")
    data1 = fetch_data("database")
    logger.info(f"獲取了 {len(data1)} 條記錄")

    # 傳入可選參數
    logger.info("\n--- 傳入可選參數 ---")
    data2 = fetch_data(
        "database",
        limit=10,
        filters={"status": "active"}
    )
    logger.info(f"獲取了 {len(data2)} 條記錄")


# ============================================================================
# 參數驗證
# ============================================================================

@task
def validate_parameters(
    value: int,
    min_value: int = 0,
    max_value: int = 100
) -> bool:
    """
    參數驗證示例

    Args:
        value: 要驗證的值
        min_value: 最小值
        max_value: 最大值

    Returns:
        是否有效

    Raises:
        ValueError: 當參數無效時
    """
    logger = get_run_logger()

    if value < min_value or value > max_value:
        error_msg = f"值 {value} 超出範圍 [{min_value}, {max_value}]"
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.info(f"✓ 值 {value} 有效")
    return True


@flow(name="參數驗證示例")
def parameter_validation_flow():
    """
    演示參數驗證
    """
    logger = get_run_logger()

    # 有效的參數
    logger.info("\n--- 測試有效參數 ---")
    try:
        validate_parameters(50, min_value=0, max_value=100)
    except ValueError as e:
        logger.error(f"驗證失敗：{e}")

    # 無效的參數
    logger.info("\n--- 測試無效參數 ---")
    try:
        validate_parameters(150, min_value=0, max_value=100)
    except ValueError as e:
        logger.error(f"驗證失敗（預期）：{e}")


# ============================================================================
# 動態參數生成
# ============================================================================

@task
def generate_tasks_params(count: int) -> List[Dict]:
    """
    動態生成任務參數

    Args:
        count: 要生成的參數數量

    Returns:
        參數列表
    """
    logger = get_run_logger()
    logger.info(f"生成 {count} 組參數")

    params = [
        {"id": i, "value": i * 10}
        for i in range(count)
    ]

    return params


@task
def process_with_params(params: Dict) -> str:
    """
    使用參數處理任務

    Args:
        params: 參數字典

    Returns:
        處理結果
    """
    logger = get_run_logger()
    logger.info(f"處理參數：{params}")

    result = f"已處理 ID={params['id']}, Value={params['value']}"
    return result


@flow(name="動態參數示例")
def dynamic_parameters_flow(task_count: int = 5):
    """
    演示動態參數生成

    Args:
        task_count: 任務數量
    """
    logger = get_run_logger()
    logger.info(f"動態生成 {task_count} 個任務")

    # 生成參數
    params_list = generate_tasks_params(task_count)

    # 為每組參數執行任務
    results = []
    for params in params_list:
        result = process_with_params(params)
        results.append(result)

    logger.info(f"完成 {len(results)} 個任務")
    return results


# ============================================================================
# 運行示例
# ============================================================================

def main():
    """
    主函數 - 運行所有示例
    """
    print("\n" + "=" * 70)
    print("Prefect 參數傳遞與結果處理")
    print("=" * 70)

    # 示例 1: 基本參數傳遞
    print("\n【示例 1】基本參數傳遞")
    print("-" * 70)
    result1 = basic_parameter_flow(10, 20, multiplier=3)
    print(f"結果：{result1}")

    # 示例 2: 複雜數據類型
    print("\n【示例 2】複雜數據類型傳遞")
    print("-" * 70)
    result2 = complex_data_flow(
        numbers=[1, 2, 3, 4, 5],
        metadata={"source": "test", "version": "1.0"}
    )
    print(f"結果：{result2}")

    # 示例 3: Pydantic 模型
    print("\n【示例 3】Pydantic 模型示例")
    print("-" * 70)
    user_data = {
        "user_id": 1,
        "name": "張三",
        "email": "zhangsan@example.com",
        "age": 30,
        "tags": ["VIP", "活躍用戶"]
    }
    result3 = pydantic_model_flow(user_data)
    print(f"結果：{result3}")

    # 示例 4: 多返回值
    print("\n【示例 4】多返回值處理")
    print("-" * 70)
    result4 = multiple_returns_flow(list(range(1, 101)))
    print(f"結果：{result4}")

    # 示例 5: 可選參數
    print("\n【示例 5】可選參數示例")
    print("-" * 70)
    optional_parameters_flow()

    # 示例 6: 參數驗證
    print("\n【示例 6】參數驗證示例")
    print("-" * 70)
    parameter_validation_flow()

    # 示例 7: 動態參數
    print("\n【示例 7】動態參數示例")
    print("-" * 70)
    result7 = dynamic_parameters_flow(task_count=3)
    print(f"結果：{result7}")

    # 使用說明
    print("\n" + "=" * 70)
    print("參數傳遞總結")
    print("=" * 70)
    print("""
1. 基本參數類型：
   - 簡單類型：int, str, float, bool
   - 複雜類型：List, Dict, Tuple, Set
   - 自定義類型：Pydantic 模型、dataclass

2. 參數傳遞方式：
   - 位置參數：按順序傳遞
   - 關鍵字參數：使用參數名傳遞
   - 默認參數：設置默認值
   - 可選參數：使用 Optional

3. 結果處理：
   - 單個返回值：直接使用
   - 多個返回值：使用元組解包
   - 結果對象：使用 Pydantic 模型

4. 最佳實踐：
   - 使用類型提示提高代碼可讀性
   - 使用 Pydantic 模型進行數據驗證
   - 為參數設置合理的默認值
   - 添加參數驗證邏輯

5. 下一步：
   - 查看 04_並行執行.py 了解任務並發
   - 查看 05_調度器.py 了解任務調度
    """)

    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
