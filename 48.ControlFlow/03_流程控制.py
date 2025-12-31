"""
ControlFlow 流程控制詳解
========================

本文件深入探討 ControlFlow 中的流程控制模式,包括:
1. 順序執行模式
2. 並行執行模式
3. 條件執行模式
4. 循環執行模式
5. 分支合併模式
6. 異常處理流程
7. 複雜流程編排

作者: ControlFlow 示例團隊
日期: 2025
"""

import os
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
import asyncio
import controlflow as cf
from controlflow import Agent, Task, Flow
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from enum import Enum


# ========== 配置 ==========

load_dotenv()


# ========== 數據模型 ==========

class ProcessStatus(str, Enum):
    """流程狀態枚舉"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowResult(BaseModel):
    """工作流結果模型"""
    status: ProcessStatus
    output: Any
    duration: float
    tasks_completed: int
    errors: List[str] = Field(default_factory=list)


class StepResult(BaseModel):
    """步驟結果模型"""
    step_name: str
    output: Any
    success: bool
    duration: float


# ========== 順序執行模式 ==========

class SequentialExecution:
    """
    順序執行模式

    演示任務按照固定順序依次執行的場景
    """

    @staticmethod
    @cf.flow
    def simple_sequential_flow():
        """
        簡單順序流程

        演示最基本的順序執行模式
        """
        print("🔄 執行簡單順序流程...")

        # 步驟 1
        print("  步驟 1: 初始化...")
        task1 = Task(
            objective="初始化系統",
            instructions="執行系統初始化檢查"
        )
        result1 = task1.run()
        print(f"  ✅ 步驟 1 完成")

        # 步驟 2
        print("  步驟 2: 載入配置...")
        task2 = Task(
            objective="載入配置",
            instructions="讀取並驗證配置文件",
            context={"init_result": result1}
        )
        result2 = task2.run()
        print(f"  ✅ 步驟 2 完成")

        # 步驟 3
        print("  步驟 3: 執行主邏輯...")
        task3 = Task(
            objective="執行主邏輯",
            instructions="根據配置執行核心業務邏輯",
            context={"config": result2}
        )
        result3 = task3.run()
        print(f"  ✅ 步驟 3 完成")

        print("✅ 順序流程完成!")
        return result3

    @staticmethod
    @cf.flow
    def data_pipeline_flow(raw_data: str):
        """
        數據管道流程

        演示數據處理的典型順序流程

        Args:
            raw_data: 原始數據
        """
        print(f"🔄 執行數據管道流程...")

        results = {}

        # 階段 1: 數據提取
        print("\n  📥 階段 1: 數據提取")
        extract_task = Task(
            objective="提取原始數據",
            instructions="從源系統提取並初步解析數據",
            context={"raw_data": raw_data}
        )
        results["extract"] = extract_task.run()
        print("  ✅ 數據提取完成")

        # 階段 2: 數據轉換
        print("\n  🔄 階段 2: 數據轉換")
        transform_task = Task(
            objective="轉換數據格式",
            instructions="將數據轉換為標準格式",
            context={"extracted_data": results["extract"]}
        )
        results["transform"] = transform_task.run()
        print("  ✅ 數據轉換完成")

        # 階段 3: 數據清洗
        print("\n  🧹 階段 3: 數據清洗")
        clean_task = Task(
            objective="清洗數據",
            instructions="移除無效數據,標準化格式",
            context={"transformed_data": results["transform"]}
        )
        results["clean"] = clean_task.run()
        print("  ✅ 數據清洗完成")

        # 階段 4: 數據驗證
        print("\n  ✓ 階段 4: 數據驗證")
        validate_task = Task(
            objective="驗證數據",
            instructions="檢查數據完整性和正確性",
            context={"clean_data": results["clean"]}
        )
        results["validate"] = validate_task.run()
        print("  ✅ 數據驗證完成")

        # 階段 5: 數據載入
        print("\n  📤 階段 5: 數據載入")
        load_task = Task(
            objective="載入數據",
            instructions="將處理後的數據載入目標系統",
            context={"validated_data": results["validate"]}
        )
        results["load"] = load_task.run()
        print("  ✅ 數據載入完成")

        print("\n✅ 數據管道流程完成!")
        return results

    @staticmethod
    @cf.flow
    def linear_dependency_chain():
        """
        線性依賴鏈

        演示任務間的線性依賴關係
        """
        print("🔄 執行線性依賴鏈...")

        # 創建線性依賴的任務鏈
        task1 = Task(objective="任務 1: 準備環境")
        task2 = Task(objective="任務 2: 安裝依賴", depends_on=[task1])
        task3 = Task(objective="任務 3: 配置系統", depends_on=[task2])
        task4 = Task(objective="任務 4: 運行測試", depends_on=[task3])
        task5 = Task(objective="任務 5: 部署應用", depends_on=[task4])

        # 執行最後一個任務會自動執行整個依賴鏈
        result = task5.run()

        print("✅ 線性依賴鏈完成!")
        return result


# ========== 並行執行模式 ==========

class ParallelExecution:
    """
    並行執行模式

    演示多個任務同時執行的場景
    """

    @staticmethod
    @cf.flow
    def parallel_independent_tasks():
        """
        並行獨立任務

        多個相互獨立的任務同時執行
        """
        print("🔄 執行並行獨立任務...")

        # 創建多個獨立任務
        task_a = Task(
            objective="分析市場數據",
            instructions="收集和分析最新市場趨勢"
        )

        task_b = Task(
            objective="分析用戶行為",
            instructions="分析用戶互動和行為模式"
        )

        task_c = Task(
            objective="分析競爭對手",
            instructions="研究競爭對手的策略和動向"
        )

        task_d = Task(
            objective="分析技術趨勢",
            instructions="評估相關技術的發展趨勢"
        )

        # 在 ControlFlow 中,這些任務可以並行執行
        # 因為它們之間沒有依賴關係
        print("  🚀 啟動並行任務...")

        results = {
            "market": task_a.run(),
            "user": task_b.run(),
            "competitor": task_c.run(),
            "technology": task_d.run()
        }

        print("✅ 所有並行任務完成!")
        return results

    @staticmethod
    @cf.flow
    def parallel_with_aggregation(data_sources: List[str]):
        """
        並行處理後匯總

        多個任務並行處理,最後匯總結果

        Args:
            data_sources: 數據源列表
        """
        print(f"🔄 並行處理 {len(data_sources)} 個數據源...")

        # 為每個數據源創建處理任務
        process_tasks = []
        for i, source in enumerate(data_sources):
            task = Task(
                objective=f"處理數據源 {i+1}",
                instructions=f"從 {source} 提取並處理數據",
                context={"source": source}
            )
            process_tasks.append(task)

        print(f"  🚀 啟動 {len(process_tasks)} 個並行處理任務...")

        # 創建匯總任務,依賴所有處理任務
        aggregation_task = Task(
            objective="匯總所有結果",
            instructions="整合來自所有數據源的結果",
            depends_on=process_tasks
        )

        # 執行匯總任務(會自動等待所有依賴任務完成)
        final_result = aggregation_task.run()

        print("✅ 並行處理和匯總完成!")
        return final_result

    @staticmethod
    @cf.flow
    def fan_out_fan_in_pattern():
        """
        扇出-扇入模式

        一個任務產生多個並行任務,最後匯總
        """
        print("🔄 執行扇出-扇入模式...")

        # 1. 準備階段(單一任務)
        print("  📍 準備階段...")
        prepare_task = Task(
            objective="準備數據分片",
            instructions="將大數據集分割成多個小塊"
        )
        prepare_result = prepare_task.run()

        # 2. 扇出階段(並行處理)
        print("  🌟 扇出階段...")
        parallel_tasks = []
        for i in range(5):  # 模擬5個並行處理任務
            task = Task(
                objective=f"處理數據塊 {i+1}",
                instructions=f"對數據塊 {i+1} 執行分析",
                context={"data_chunk": f"chunk_{i+1}"}
            )
            parallel_tasks.append(task)

        # 3. 扇入階段(匯總結果)
        print("  🎯 扇入階段...")
        merge_task = Task(
            objective="合併所有結果",
            instructions="將所有並行處理的結果合併",
            depends_on=parallel_tasks
        )
        final_result = merge_task.run()

        print("✅ 扇出-扇入完成!")
        return final_result


# ========== 條件執行模式 ==========

class ConditionalExecution:
    """
    條件執行模式

    根據條件決定執行路徑
    """

    @staticmethod
    @cf.flow
    def if_else_pattern(condition: bool):
        """
        If-Else 模式

        Args:
            condition: 條件判斷
        """
        print(f"🔄 執行 If-Else 模式 (條件: {condition})...")

        if condition:
            print("  ✅ 執行 True 分支...")
            task = Task(
                objective="執行條件為真時的任務",
                instructions="處理條件滿足的情況"
            )
        else:
            print("  ❌ 執行 False 分支...")
            task = Task(
                objective="執行條件為假時的任務",
                instructions="處理條件不滿足的情況"
            )

        result = task.run()
        print("✅ 條件執行完成!")
        return result

    @staticmethod
    @cf.flow
    def switch_case_pattern(option: str):
        """
        Switch-Case 模式

        根據選項選擇不同的執行路徑

        Args:
            option: 選項值
        """
        print(f"🔄 執行 Switch-Case 模式 (選項: {option})...")

        tasks = {
            "research": Task(
                objective="執行研究任務",
                instructions="深入研究指定主題"
            ),
            "analysis": Task(
                objective="執行分析任務",
                instructions="分析提供的數據"
            ),
            "summary": Task(
                objective="執行摘要任務",
                instructions="生成內容摘要"
            ),
            "translation": Task(
                objective="執行翻譯任務",
                instructions="翻譯文本內容"
            )
        }

        # 根據選項選擇任務
        task = tasks.get(option)
        if not task:
            print(f"  ⚠️ 未知選項: {option}, 使用默認任務")
            task = Task(
                objective="執行默認任務",
                instructions="處理未知類型的請求"
            )

        result = task.run()
        print("✅ Switch-Case 完成!")
        return result

    @staticmethod
    @cf.flow
    def dynamic_routing_pattern(input_data: Dict[str, Any]):
        """
        動態路由模式

        基於輸入數據的特徵動態選擇處理路徑

        Args:
            input_data: 輸入數據
        """
        print("🔄 執行動態路由模式...")

        # 步驟 1: 分析輸入,決定路由
        print("  📊 分析輸入數據...")
        analysis_task = Task(
            objective="分析輸入特徵",
            instructions="""
            分析輸入數據的特徵,返回建議的處理路徑。
            可能的路徑: fast_path, standard_path, detailed_path
            """,
            context=input_data
        )
        route = analysis_task.run()

        # 步驟 2: 根據路由執行相應任務
        print(f"  🚦 選擇路徑: {route}")

        if "fast" in str(route).lower():
            task = Task(
                objective="快速處理",
                instructions="使用快速算法處理",
                context=input_data
            )
        elif "detailed" in str(route).lower():
            task = Task(
                objective="詳細處理",
                instructions="使用深度分析算法處理",
                context=input_data
            )
        else:
            task = Task(
                objective="標準處理",
                instructions="使用標準算法處理",
                context=input_data
            )

        result = task.run()
        print("✅ 動態路由完成!")
        return result


# ========== 循環執行模式 ==========

class LoopExecution:
    """
    循環執行模式

    演示各種循環處理場景
    """

    @staticmethod
    @cf.flow
    def simple_loop_pattern(items: List[str]):
        """
        簡單循環模式

        對列表中的每個項目執行相同的任務

        Args:
            items: 要處理的項目列表
        """
        print(f"🔄 循環處理 {len(items)} 個項目...")

        results = []

        for i, item in enumerate(items, 1):
            print(f"  📌 處理項目 {i}/{len(items)}: {item}")

            task = Task(
                objective=f"處理項目: {item}",
                instructions="對項目執行標準處理流程",
                context={"item": item, "index": i}
            )

            result = task.run()
            results.append(result)

        print(f"✅ 已處理 {len(results)} 個項目!")
        return results

    @staticmethod
    @cf.flow
    def batch_loop_pattern(items: List[str], batch_size: int = 3):
        """
        批次循環模式

        將項目分批處理

        Args:
            items: 要處理的項目列表
            batch_size: 每批的大小
        """
        print(f"🔄 批次處理 {len(items)} 個項目 (批次大小: {batch_size})...")

        results = []
        batches = [items[i:i+batch_size] for i in range(0, len(items), batch_size)]

        for batch_num, batch in enumerate(batches, 1):
            print(f"\n  📦 處理批次 {batch_num}/{len(batches)} ({len(batch)} 項)...")

            # 為批次中的每個項目創建任務
            batch_tasks = []
            for item in batch:
                task = Task(
                    objective=f"處理: {item}",
                    context={"item": item}
                )
                batch_tasks.append(task)

            # 批次內的任務可以並行執行
            batch_results = [task.run() for task in batch_tasks]
            results.extend(batch_results)

            print(f"  ✅ 批次 {batch_num} 完成!")

        print(f"\n✅ 所有批次處理完成! 總計 {len(results)} 個結果")
        return results

    @staticmethod
    @cf.flow
    def iterative_refinement_pattern(initial_input: str, max_iterations: int = 3):
        """
        迭代優化模式

        通過多次迭代不斷優化結果

        Args:
            initial_input: 初始輸入
            max_iterations: 最大迭代次數
        """
        print(f"🔄 執行迭代優化 (最多 {max_iterations} 次)...")

        current_result = initial_input

        for iteration in range(1, max_iterations + 1):
            print(f"\n  🔁 迭代 {iteration}/{max_iterations}...")

            # 優化任務
            refine_task = Task(
                objective=f"優化結果 - 迭代 {iteration}",
                instructions="""
                基於當前結果進行優化:
                1. 識別可改進的地方
                2. 應用優化策略
                3. 生成改進的版本
                """,
                context={
                    "current_result": current_result,
                    "iteration": iteration
                }
            )

            current_result = refine_task.run()

            # 評估任務
            evaluate_task = Task(
                objective="評估優化質量",
                instructions="評估當前結果的質量,決定是否需要繼續優化",
                context={"result": current_result}
            )

            quality_score = evaluate_task.run()
            print(f"  📊 質量評分: {quality_score}")

            # 如果質量足夠好,提前結束
            if "excellent" in str(quality_score).lower():
                print(f"  🎯 在第 {iteration} 次迭代達到優秀質量!")
                break

        print("\n✅ 迭代優化完成!")
        return current_result

    @staticmethod
    @cf.flow
    def while_loop_pattern(threshold: float = 0.95):
        """
        While 循環模式

        持續執行直到滿足條件

        Args:
            threshold: 停止閾值
        """
        print(f"🔄 執行 While 循環模式 (閾值: {threshold})...")

        iteration = 0
        current_score = 0.0

        while current_score < threshold and iteration < 10:  # 最多10次迭代
            iteration += 1
            print(f"\n  🔁 迭代 {iteration} (當前分數: {current_score:.2f})...")

            task = Task(
                objective=f"改進方案 - 迭代 {iteration}",
                instructions=f"""
                當前分數: {current_score:.2f}
                目標分數: {threshold:.2f}
                請提供改進建議並估計新分數
                """,
                context={
                    "current_score": current_score,
                    "threshold": threshold,
                    "iteration": iteration
                }
            )

            result = task.run()

            # 模擬分數提升
            current_score = min(current_score + 0.15, 1.0)
            print(f"  📈 新分數: {current_score:.2f}")

        if current_score >= threshold:
            print(f"\n✅ 達到目標! 最終分數: {current_score:.2f}")
        else:
            print(f"\n⚠️ 達到最大迭代次數! 最終分數: {current_score:.2f}")

        return current_score


# ========== 複雜流程編排 ==========

class ComplexOrchestration:
    """
    複雜流程編排

    組合多種模式創建複雜的工作流
    """

    @staticmethod
    @cf.flow
    def hybrid_workflow(data: Dict[str, Any]):
        """
        混合工作流

        組合順序、並行和條件執行

        Args:
            data: 輸入數據
        """
        print("🔄 執行混合工作流...")

        # 階段 1: 順序預處理
        print("\n📍 階段 1: 預處理 (順序)")
        validate_task = Task(objective="驗證輸入", context=data)
        validation_result = validate_task.run()

        # 階段 2: 並行分析
        print("\n📍 階段 2: 分析 (並行)")
        analysis_tasks = [
            Task(objective="語法分析", context=data),
            Task(objective="語義分析", context=data),
            Task(objective="結構分析", context=data)
        ]

        # 階段 3: 匯總分析結果
        print("\n📍 階段 3: 匯總")
        merge_task = Task(
            objective="合併分析結果",
            depends_on=analysis_tasks
        )
        merged_result = merge_task.run()

        # 階段 4: 條件處理
        print("\n📍 階段 4: 條件處理")
        if "complex" in str(merged_result).lower():
            print("  ➡️ 執行複雜處理路徑")
            final_task = Task(
                objective="深度處理",
                context={"analysis": merged_result}
            )
        else:
            print("  ➡️ 執行簡單處理路徑")
            final_task = Task(
                objective="標準處理",
                context={"analysis": merged_result}
            )

        final_result = final_task.run()

        print("\n✅ 混合工作流完成!")
        return final_result

    @staticmethod
    @cf.flow
    def multi_stage_pipeline(input_data: str):
        """
        多階段管道

        演示具有多個階段的複雜管道

        Args:
            input_data: 輸入數據
        """
        print("🔄 執行多階段管道...")

        results = {"input": input_data}

        # 階段 A: 數據準備(順序)
        print("\n🅰️ 階段 A: 數據準備")
        stage_a_tasks = [
            Task(objective="載入數據", context=results),
            Task(objective="格式化數據", depends_on=[]),
            Task(objective="驗證數據", depends_on=[])
        ]

        for task in stage_a_tasks:
            results[f"a_{task.objective}"] = task.run()

        # 階段 B: 並行處理
        print("\n🅱️ 階段 B: 並行處理")
        stage_b_tasks = [
            Task(objective="特徵提取", context=results),
            Task(objective="統計分析", context=results),
            Task(objective="模式識別", context=results)
        ]

        # 階段 C: 結果整合
        print("\n🆎 階段 C: 結果整合")
        stage_c_task = Task(
            objective="整合所有結果",
            depends_on=stage_b_tasks,
            context=results
        )

        final_result = stage_c_task.run()

        print("\n✅ 多階段管道完成!")
        return final_result


# ========== 主程序 ==========

def main():
    """
    主程序入口

    演示各種流程控制模式
    """
    print("=" * 70)
    print("  ControlFlow 流程控制示例")
    print("=" * 70)
    print()

    try:
        # 1. 順序執行
        print("\n" + "=" * 70)
        print("1. 順序執行模式")
        print("=" * 70)

        seq = SequentialExecution()
        # seq.simple_sequential_flow()
        # seq.data_pipeline_flow("示例原始數據")
        print("✅ 順序執行示例已定義")

        # 2. 並行執行
        print("\n" + "=" * 70)
        print("2. 並行執行模式")
        print("=" * 70)

        par = ParallelExecution()
        # par.parallel_independent_tasks()
        # par.parallel_with_aggregation(["源1", "源2", "源3"])
        print("✅ 並行執行示例已定義")

        # 3. 條件執行
        print("\n" + "=" * 70)
        print("3. 條件執行模式")
        print("=" * 70)

        cond = ConditionalExecution()
        # cond.if_else_pattern(True)
        # cond.switch_case_pattern("research")
        print("✅ 條件執行示例已定義")

        # 4. 循環執行
        print("\n" + "=" * 70)
        print("4. 循環執行模式")
        print("=" * 70)

        loop = LoopExecution()
        # loop.simple_loop_pattern(["項目1", "項目2", "項目3"])
        # loop.batch_loop_pattern(["A", "B", "C", "D", "E"], batch_size=2)
        print("✅ 循環執行示例已定義")

        # 5. 複雜編排
        print("\n" + "=" * 70)
        print("5. 複雜流程編排")
        print("=" * 70)

        complex_orch = ComplexOrchestration()
        # complex_orch.hybrid_workflow({"type": "complex"})
        print("✅ 複雜編排示例已定義")

        print("\n" + "=" * 70)
        print("演示完成")
        print("=" * 70)
        print("\n✅ 所有流程控制模式已成功展示!")
        print("\n💡 流程控制模式總結:")
        print("   - 順序執行: 線性處理,步驟明確")
        print("   - 並行執行: 提高效率,適合獨立任務")
        print("   - 條件執行: 靈活路由,智能決策")
        print("   - 循環執行: 批量處理,迭代優化")
        print("   - 複雜編排: 組合模式,應對複雜場景")
        print("\n💡 下一步:")
        print("   - 查看 04_條件分支.py 深入學習條件邏輯")
        print("   - 查看 05_Agent創建.py 學習 Agent 配置")
        print()

    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
