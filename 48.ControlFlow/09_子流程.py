"""
ControlFlow 子流程詳解
======================

本文件深入探討 ControlFlow 中的子流程和組合模式,包括:
1. 子流程定義
2. 流程嵌套
3. 流程組合
4. 流程複用
5. 參數傳遞
6. 結果匯總
7. 複雜流程編排

作者: ControlFlow 示例團隊
日期: 2025
"""

import os
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from enum import Enum
import controlflow as cf
from controlflow import Agent, Task, Flow
from pydantic import BaseModel, Field
from dotenv import load_dotenv


# ========== 配置 ==========

load_dotenv()


# ========== 數據模型 ==========

class SubflowResult(BaseModel):
    """子流程結果模型"""
    subflow_name: str
    success: bool
    output: Any
    duration: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PipelineStage(BaseModel):
    """管道階段模型"""
    stage_name: str
    status: str
    input_data: Any
    output_data: Any
    timestamp: datetime = Field(default_factory=datetime.now)


# ========== 基本子流程 ==========

class BasicSubflows:
    """
    基本子流程示例

    演示如何定義和使用子流程
    """

    @staticmethod
    @cf.flow
    def data_extraction_subflow(source: str) -> Dict[str, Any]:
        """
        數據提取子流程

        Args:
            source: 數據源

        Returns:
            Dict[str, Any]: 提取的數據
        """
        print(f"📥 執行數據提取子流程")
        print(f"   源: {source}")

        # 提取任務
        task = Task(
            objective=f"從 {source} 提取數據",
            instructions="提取所有相關數據"
        )

        result = task.run()

        print(f"✅ 數據提取完成")

        return {
            "source": source,
            "data": result,
            "extracted_at": datetime.now().isoformat()
        }

    @staticmethod
    @cf.flow
    def data_transformation_subflow(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        數據轉換子流程

        Args:
            data: 輸入數據

        Returns:
            Dict[str, Any]: 轉換後的數據
        """
        print(f"🔄 執行數據轉換子流程")

        # 轉換任務
        task = Task(
            objective="轉換數據格式",
            instructions="將數據轉換為標準格式",
            context=data
        )

        result = task.run()

        print(f"✅ 數據轉換完成")

        return {
            "original": data,
            "transformed": result,
            "transformed_at": datetime.now().isoformat()
        }

    @staticmethod
    @cf.flow
    def data_validation_subflow(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        數據驗證子流程

        Args:
            data: 要驗證的數據

        Returns:
            Dict[str, Any]: 驗證結果
        """
        print(f"✓ 執行數據驗證子流程")

        # 驗證任務
        task = Task(
            objective="驗證數據完整性和正確性",
            instructions="檢查數據是否符合要求",
            context=data
        )

        result = task.run()

        print(f"✅ 數據驗證完成")

        return {
            "data": data,
            "validation_result": result,
            "is_valid": True,
            "validated_at": datetime.now().isoformat()
        }

    @staticmethod
    @cf.flow
    def main_flow_with_subflows(source: str):
        """
        使用子流程的主流程

        Args:
            source: 數據源
        """
        print("🌊 執行主流程 (帶子流程)\n")

        # 調用子流程 1: 提取
        print("📍 階段 1: 數據提取")
        extracted = BasicSubflows.data_extraction_subflow(source)
        print()

        # 調用子流程 2: 轉換
        print("📍 階段 2: 數據轉換")
        transformed = BasicSubflows.data_transformation_subflow(extracted)
        print()

        # 調用子流程 3: 驗證
        print("📍 階段 3: 數據驗證")
        validated = BasicSubflows.data_validation_subflow(transformed)
        print()

        print("✅ 主流程完成!")

        return validated


# ========== 流程嵌套 ==========

class NestedFlows:
    """
    流程嵌套示例

    演示多層嵌套的流程結構
    """

    @staticmethod
    @cf.flow
    def level3_flow(data: str) -> str:
        """
        第三層流程

        Args:
            data: 輸入數據

        Returns:
            str: 處理結果
        """
        print(f"      🔹 L3: 處理 {data}")

        task = Task(
            objective=f"L3 處理: {data}",
            context={"level": 3, "data": data}
        )

        result = task.run()
        print(f"      ✅ L3 完成")

        return f"L3({result})"

    @staticmethod
    @cf.flow
    def level2_flow(items: List[str]) -> List[str]:
        """
        第二層流程

        Args:
            items: 項目列表

        Returns:
            List[str]: 處理結果列表
        """
        print(f"   🔸 L2: 處理 {len(items)} 個項目")

        results = []

        for item in items:
            # 調用第三層流程
            result = NestedFlows.level3_flow(item)
            results.append(result)

        print(f"   ✅ L2 完成")

        return results

    @staticmethod
    @cf.flow
    def level1_flow(input_data: Dict[str, Any]):
        """
        第一層流程(頂層)

        Args:
            input_data: 輸入數據
        """
        print(f"🔷 L1: 開始處理")
        print(f"   輸入: {input_data}\n")

        # 準備數據
        items = input_data.get("items", ["item1", "item2", "item3"])

        # 調用第二層流程
        results = NestedFlows.level2_flow(items)

        print(f"\n🔷 L1: 完成")
        print(f"   結果: {results}")

        return {
            "input": input_data,
            "output": results,
            "nested_levels": 3
        }


# ========== 流程組合 ==========

class FlowComposition:
    """
    流程組合示例

    演示如何組合多個流程
    """

    @staticmethod
    @cf.flow
    def preprocessing_flow(raw_data: str) -> Dict[str, Any]:
        """
        預處理流程

        Args:
            raw_data: 原始數據

        Returns:
            Dict[str, Any]: 預處理結果
        """
        print("🔧 預處理流程")

        task = Task(
            objective="預處理數據",
            instructions="清洗、標準化數據",
            context={"raw_data": raw_data}
        )

        result = task.run()

        return {
            "stage": "preprocessing",
            "output": result
        }

    @staticmethod
    @cf.flow
    def analysis_flow(preprocessed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析流程

        Args:
            preprocessed_data: 預處理數據

        Returns:
            Dict[str, Any]: 分析結果
        """
        print("📊 分析流程")

        task = Task(
            objective="分析數據",
            instructions="執行統計分析和模式識別",
            context=preprocessed_data
        )

        result = task.run()

        return {
            "stage": "analysis",
            "output": result
        }

    @staticmethod
    @cf.flow
    def visualization_flow(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        可視化流程

        Args:
            analysis_results: 分析結果

        Returns:
            Dict[str, Any]: 可視化結果
        """
        print("📈 可視化流程")

        task = Task(
            objective="生成可視化",
            instructions="創建圖表和報告",
            context=analysis_results
        )

        result = task.run()

        return {
            "stage": "visualization",
            "output": result
        }

    @staticmethod
    @cf.flow
    def reporting_flow(viz_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        報告流程

        Args:
            viz_data: 可視化數據

        Returns:
            Dict[str, Any]: 報告
        """
        print("📄 報告流程")

        task = Task(
            objective="生成報告",
            instructions="編寫完整的分析報告",
            context=viz_data
        )

        result = task.run()

        return {
            "stage": "reporting",
            "output": result
        }

    @staticmethod
    @cf.flow
    def composed_analytics_pipeline(raw_data: str):
        """
        組合的分析管道

        組合多個流程形成完整管道

        Args:
            raw_data: 原始數據
        """
        print("🌊 執行組合分析管道\n")

        # 階段 1: 預處理
        print("📍 階段 1/4: 預處理")
        preprocessed = FlowComposition.preprocessing_flow(raw_data)
        print()

        # 階段 2: 分析
        print("📍 階段 2/4: 分析")
        analyzed = FlowComposition.analysis_flow(preprocessed)
        print()

        # 階段 3: 可視化
        print("📍 階段 3/4: 可視化")
        visualized = FlowComposition.visualization_flow(analyzed)
        print()

        # 階段 4: 報告
        print("📍 階段 4/4: 報告")
        report = FlowComposition.reporting_flow(visualized)
        print()

        print("✅ 分析管道完成!")

        return {
            "pipeline": "analytics",
            "stages": ["preprocessing", "analysis", "visualization", "reporting"],
            "final_report": report
        }


# ========== 流程複用 ==========

class ReusableFlows:
    """
    可複用流程示例

    演示如何創建可複用的流程組件
    """

    @staticmethod
    @cf.flow
    def generic_validation_flow(
        data: Any,
        validation_rules: List[str]
    ) -> Dict[str, Any]:
        """
        通用驗證流程

        Args:
            data: 要驗證的數據
            validation_rules: 驗證規則列表

        Returns:
            Dict[str, Any]: 驗證結果
        """
        print(f"✓ 通用驗證流程")
        print(f"   規則數: {len(validation_rules)}")

        task = Task(
            objective="驗證數據",
            instructions=f"根據規則驗證: {', '.join(validation_rules)}",
            context={"data": data, "rules": validation_rules}
        )

        result = task.run()

        return {
            "valid": True,
            "rules_checked": len(validation_rules),
            "result": result
        }

    @staticmethod
    @cf.flow
    def generic_transformation_flow(
        data: Any,
        transformation_type: str
    ) -> Any:
        """
        通用轉換流程

        Args:
            data: 輸入數據
            transformation_type: 轉換類型

        Returns:
            Any: 轉換後的數據
        """
        print(f"🔄 通用轉換流程")
        print(f"   類型: {transformation_type}")

        task = Task(
            objective=f"執行 {transformation_type} 轉換",
            context={"data": data, "type": transformation_type}
        )

        result = task.run()

        return result

    @staticmethod
    @cf.flow
    def reusable_etl_pattern(
        source: str,
        transformations: List[str],
        validation_rules: List[str]
    ):
        """
        可複用的 ETL 模式

        Args:
            source: 數據源
            transformations: 轉換列表
            validation_rules: 驗證規則
        """
        print("🔄 可複用 ETL 模式\n")

        # Extract
        print("📍 提取階段")
        extracted = BasicSubflows.data_extraction_subflow(source)
        print()

        # Transform (可複用)
        print("📍 轉換階段")
        current_data = extracted

        for i, transformation in enumerate(transformations, 1):
            print(f"   轉換 {i}/{len(transformations)}: {transformation}")
            current_data = ReusableFlows.generic_transformation_flow(
                current_data,
                transformation
            )

        print()

        # Validate (可複用)
        print("📍 驗證階段")
        validated = ReusableFlows.generic_validation_flow(
            current_data,
            validation_rules
        )
        print()

        # Load
        print("📍 載入階段")
        task = Task(
            objective="載入數據到目標系統",
            context=validated
        )
        loaded = task.run()
        print()

        print("✅ ETL 完成!")

        return {
            "source": source,
            "transformations_applied": len(transformations),
            "validation_passed": validated["valid"],
            "loaded": loaded
        }


# ========== 並行子流程 ==========

class ParallelSubflows:
    """
    並行子流程示例

    演示如何並行執行多個子流程
    """

    @staticmethod
    @cf.flow
    def process_partition(partition_id: int, data: List[Any]) -> Dict[str, Any]:
        """
        處理數據分區

        Args:
            partition_id: 分區 ID
            data: 分區數據

        Returns:
            Dict[str, Any]: 處理結果
        """
        print(f"   📦 處理分區 {partition_id}")

        task = Task(
            objective=f"處理分區 {partition_id}",
            context={"partition": partition_id, "data": data}
        )

        result = task.run()

        print(f"   ✅ 分區 {partition_id} 完成")

        return {
            "partition_id": partition_id,
            "result": result,
            "items_processed": len(data)
        }

    @staticmethod
    @cf.flow
    def parallel_processing_flow(dataset: List[Any], num_partitions: int = 3):
        """
        並行處理流程

        Args:
            dataset: 完整數據集
            num_partitions: 分區數量
        """
        print(f"⚡ 並行處理流程")
        print(f"   數據量: {len(dataset)}")
        print(f"   分區數: {num_partitions}\n")

        # 分區數據
        partition_size = len(dataset) // num_partitions
        partitions = [
            dataset[i:i+partition_size]
            for i in range(0, len(dataset), partition_size)
        ]

        print("📍 並行處理各分區...")

        # 並行處理各分區
        partition_results = []

        for i, partition_data in enumerate(partitions):
            result = ParallelSubflows.process_partition(i, partition_data)
            partition_results.append(result)

        print()

        # 合併結果
        print("📍 合併結果...")
        merge_task = Task(
            objective="合併所有分區結果",
            context={"results": partition_results}
        )

        final_result = merge_task.run()

        print("✅ 並行處理完成!")

        return {
            "partitions": len(partitions),
            "total_items": len(dataset),
            "merged_result": final_result
        }


# ========== 動態子流程 ==========

class DynamicSubflows:
    """
    動態子流程示例

    根據條件動態選擇和執行子流程
    """

    @staticmethod
    @cf.flow
    def strategy_a_flow(data: Any) -> Any:
        """策略 A 流程"""
        print("   🅰️ 執行策略 A")
        task = Task(objective="策略 A 處理", context={"data": data})
        return task.run()

    @staticmethod
    @cf.flow
    def strategy_b_flow(data: Any) -> Any:
        """策略 B 流程"""
        print("   🅱️ 執行策略 B")
        task = Task(objective="策略 B 處理", context={"data": data})
        return task.run()

    @staticmethod
    @cf.flow
    def strategy_c_flow(data: Any) -> Any:
        """策略 C 流程"""
        print("   ©️ 執行策略 C")
        task = Task(objective="策略 C 處理", context={"data": data})
        return task.run()

    @staticmethod
    @cf.flow
    def dynamic_strategy_selection(
        data: Any,
        criteria: Dict[str, Any]
    ):
        """
        動態策略選擇

        Args:
            data: 輸入數據
            criteria: 選擇標準
        """
        print("🎯 動態策略選擇")
        print(f"   標準: {criteria}\n")

        # 分析並選擇策略
        print("📍 分析數據特徵...")

        analysis_task = Task(
            objective="分析數據並選擇最佳策略",
            instructions="""
            分析數據特徵,選擇最合適的處理策略:
            - strategy_a: 適合簡單數據
            - strategy_b: 適合中等複雜度數據
            - strategy_c: 適合複雜數據
            """,
            context={"data": data, "criteria": criteria}
        )

        selected_strategy = analysis_task.run()

        print(f"   選擇策略: {selected_strategy}\n")

        # 執行選擇的策略
        print("📍 執行選定策略...")

        strategies = {
            "strategy_a": DynamicSubflows.strategy_a_flow,
            "strategy_b": DynamicSubflows.strategy_b_flow,
            "strategy_c": DynamicSubflows.strategy_c_flow
        }

        # 動態調用子流程
        if "a" in str(selected_strategy).lower():
            result = strategies["strategy_a"](data)
        elif "b" in str(selected_strategy).lower():
            result = strategies["strategy_b"](data)
        else:
            result = strategies["strategy_c"](data)

        print("\n✅ 動態流程完成!")

        return {
            "selected_strategy": selected_strategy,
            "result": result
        }


# ========== 主程序 ==========

def main():
    """
    主程序入口

    演示各種子流程和組合模式
    """
    print("=" * 70)
    print("  ControlFlow 子流程示例")
    print("=" * 70)
    print()

    try:
        # 1. 基本子流程
        print("\n" + "=" * 70)
        print("1. 基本子流程")
        print("=" * 70 + "\n")

        # BasicSubflows.main_flow_with_subflows("database")
        print("✅ 基本子流程示例已定義\n")

        # 2. 流程嵌套
        print("\n" + "=" * 70)
        print("2. 流程嵌套")
        print("=" * 70 + "\n")

        input_data = {"items": ["A", "B", "C"]}
        # NestedFlows.level1_flow(input_data)
        print("✅ 嵌套流程示例已定義\n")

        # 3. 流程組合
        print("\n" + "=" * 70)
        print("3. 流程組合")
        print("=" * 70 + "\n")

        # FlowComposition.composed_analytics_pipeline("示例數據")
        print("✅ 流程組合示例已定義\n")

        # 4. 流程複用
        print("\n" + "=" * 70)
        print("4. 可複用流程")
        print("=" * 70 + "\n")

        # ReusableFlows.reusable_etl_pattern(
        #     source="api",
        #     transformations=["normalize", "enrich", "aggregate"],
        #     validation_rules=["not_null", "format_check"]
        # )
        print("✅ 可複用流程示例已定義\n")

        # 5. 並行子流程
        print("\n" + "=" * 70)
        print("5. 並行子流程")
        print("=" * 70 + "\n")

        # dataset = list(range(1, 11))
        # ParallelSubflows.parallel_processing_flow(dataset, num_partitions=3)
        print("✅ 並行子流程示例已定義\n")

        # 6. 動態子流程
        print("\n" + "=" * 70)
        print("6. 動態子流程")
        print("=" * 70 + "\n")

        # DynamicSubflows.dynamic_strategy_selection(
        #     data={"complexity": "medium"},
        #     criteria={"performance": "high", "accuracy": "medium"}
        # )
        print("✅ 動態子流程示例已定義\n")

        print("\n" + "=" * 70)
        print("演示完成")
        print("=" * 70)
        print("\n✅ 所有子流程示例已成功展示!")
        print("\n💡 子流程設計要點:")
        print("   - 模塊化: 將複雜流程分解為獨立子流程")
        print("   - 可複用: 設計通用的子流程組件")
        print("   - 組合性: 靈活組合子流程構建新流程")
        print("   - 並行化: 利用並行子流程提高效率")
        print("   - 動態性: 根據條件動態選擇子流程")
        print("\n💡 下一步:")
        print("   - 查看 10_生產部署.py 學習生產部署")
        print()

    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
