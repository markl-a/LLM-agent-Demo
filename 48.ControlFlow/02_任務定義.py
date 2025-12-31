"""
ControlFlow 任務定義詳解
========================

本文件深入探討 ControlFlow 中任務(Task)的定義和配置,包括:
1. 任務的基本屬性和配置
2. 任務依賴關係
3. 任務結果類型定義
4. 任務優先級和調度
5. 任務重試和超時
6. 任務狀態管理
7. 高級任務模式

作者: ControlFlow 示例團隊
日期: 2025
"""

import os
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import controlflow as cf
from controlflow import Agent, Task, Flow
from pydantic import BaseModel, Field
from dotenv import load_dotenv


# ========== 配置 ==========

load_dotenv()


# ========== 任務結果類型定義 ==========

class TaskPriority(str, Enum):
    """任務優先級枚舉"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ResearchResult(BaseModel):
    """研究任務的結果模型"""
    topic: str = Field(description="研究主題")
    summary: str = Field(description="研究摘要")
    key_points: List[str] = Field(description="關鍵要點")
    sources: List[str] = Field(default_factory=list, description="資料來源")
    confidence: float = Field(ge=0, le=1, description="結果可信度")


class AnalysisResult(BaseModel):
    """分析任務的結果模型"""
    input_data: str = Field(description="輸入數據")
    findings: List[str] = Field(description="分析發現")
    recommendations: List[str] = Field(description="建議")
    risk_level: str = Field(description="風險級別")
    timestamp: datetime = Field(default_factory=datetime.now)


class ValidationResult(BaseModel):
    """驗證任務的結果模型"""
    is_valid: bool = Field(description="是否有效")
    errors: List[str] = Field(default_factory=list, description="錯誤列表")
    warnings: List[str] = Field(default_factory=list, description="警告列表")
    score: float = Field(ge=0, le=100, description="驗證分數")


# ========== 基本任務配置 ==========

class BasicTaskConfiguration:
    """
    基本任務配置示例類

    演示如何配置任務的基本屬性
    """

    @staticmethod
    def create_simple_task() -> Task:
        """
        創建最簡單的任務

        Returns:
            Task: 簡單任務實例
        """
        print("📋 創建簡單任務...")

        task = Task(
            objective="完成一個基本任務"
        )

        print(f"   任務 ID: {task.id}")
        print(f"   目標: {task.objective}")
        print()

        return task

    @staticmethod
    def create_task_with_instructions() -> Task:
        """
        創建帶詳細指令的任務

        Returns:
            Task: 配置了詳細指令的任務
        """
        print("📋 創建帶指令的任務...")

        task = Task(
            objective="分析用戶反饋",
            instructions="""
            請執行以下步驟:
            1. 閱讀並理解所有用戶反饋
            2. 識別常見的主題和模式
            3. 分類反饋為正面、負面和建議
            4. 總結主要發現
            5. 提供改進建議

            請確保分析全面、客觀,並提供具體的行動建議。
            """
        )

        print(f"   目標: {task.objective}")
        print(f"   指令: 已設置詳細執行步驟")
        print()

        return task

    @staticmethod
    def create_task_with_context() -> Task:
        """
        創建帶上下文的任務

        Returns:
            Task: 包含上下文信息的任務
        """
        print("📋 創建帶上下文的任務...")

        context = {
            "user_feedback": [
                "產品很好用,但加載速度慢",
                "希望能增加深色模式",
                "客服響應很及時"
            ],
            "product_version": "2.0.1",
            "analysis_date": datetime.now().isoformat()
        }

        task = Task(
            objective="分析用戶反饋趨勢",
            instructions="基於提供的上下文數據進行分析",
            context=context
        )

        print(f"   目標: {task.objective}")
        print(f"   上下文鍵: {list(context.keys())}")
        print()

        return task


# ========== 任務結果類型 ==========

class TaskResultTypes:
    """
    任務結果類型示例類

    演示如何定義和使用強類型的任務結果
    """

    @staticmethod
    def create_typed_task() -> Task:
        """
        創建帶類型定義的任務

        Returns:
            Task: 具有明確結果類型的任務
        """
        print("📋 創建類型化任務...")

        task = Task(
            objective="研究人工智能的最新進展",
            result_type=ResearchResult,
            instructions="""
            請研究人工智能領域的最新進展,並提供結構化的結果。
            結果應包含摘要、關鍵要點和資料來源。
            """
        )

        print(f"   目標: {task.objective}")
        print(f"   結果類型: {ResearchResult.__name__}")
        print()

        return task

    @staticmethod
    def create_list_result_task() -> Task:
        """
        創建返回列表的任務

        Returns:
            Task: 返回列表結果的任務
        """
        print("📋 創建列表結果任務...")

        task = Task(
            objective="生成機器學習算法列表",
            result_type=List[str],
            instructions="列出常用的機器學習算法,每個算法一行"
        )

        print(f"   目標: {task.objective}")
        print(f"   結果類型: List[str]")
        print()

        return task

    @staticmethod
    def create_dict_result_task() -> Task:
        """
        創建返回字典的任務

        Returns:
            Task: 返回字典結果的任務
        """
        print("📋 創建字典結果任務...")

        task = Task(
            objective="分析編程語言特點",
            result_type=Dict[str, str],
            instructions="""
            分析幾種主流編程語言的特點。
            返回字典,鍵為語言名稱,值為特點描述。
            """
        )

        print(f"   目標: {task.objective}")
        print(f"   結果類型: Dict[str, str]")
        print()

        return task


# ========== 任務依賴關係 ==========

class TaskDependencies:
    """
    任務依賴關係示例類

    演示如何定義任務之間的依賴關係
    """

    @staticmethod
    @cf.flow
    def sequential_tasks_flow():
        """
        順序依賴任務流

        演示任務按順序執行的場景
        """
        print("🌊 執行順序任務流...")

        # 任務 1: 數據收集
        task1 = Task(
            objective="收集用戶數據",
            instructions="從系統中收集最近30天的用戶行為數據"
        )

        # 任務 2: 數據清洗(依賴任務1)
        task2 = Task(
            objective="清洗數據",
            instructions="清理和標準化收集到的數據",
            depends_on=[task1]  # 明確依賴關係
        )

        # 任務 3: 數據分析(依賴任務2)
        task3 = Task(
            objective="分析數據",
            instructions="對清洗後的數據進行統計分析",
            depends_on=[task2]
        )

        # 任務 4: 生成報告(依賴任務3)
        task4 = Task(
            objective="生成報告",
            instructions="基於分析結果生成可視化報告",
            depends_on=[task3]
        )

        # 執行最後一個任務會自動執行所有依賴任務
        result = task4.run()

        print("✅ 順序任務流完成!")
        return result

    @staticmethod
    @cf.flow
    def parallel_tasks_with_join():
        """
        並行任務後匯合

        演示多個並行任務的結果被後續任務使用
        """
        print("🌊 執行並行匯合任務流...")

        # 並行任務組
        task_a = Task(
            objective="分析市場趨勢",
            instructions="分析當前市場的主要趨勢"
        )

        task_b = Task(
            objective="分析競爭對手",
            instructions="研究主要競爭對手的策略"
        )

        task_c = Task(
            objective="分析用戶需求",
            instructions="總結用戶的核心需求"
        )

        # 匯合任務(依賴所有並行任務)
        task_final = Task(
            objective="制定綜合策略",
            instructions="基於市場、競爭和用戶分析,制定綜合策略",
            depends_on=[task_a, task_b, task_c]
        )

        result = task_final.run()

        print("✅ 並行匯合任務流完成!")
        return result

    @staticmethod
    def demonstrate_complex_dependencies():
        """
        演示複雜的依賴關係圖
        """
        print("🔄 演示複雜依賴關係...")

        # 根任務
        root = Task(objective="初始化項目")

        # 第二層任務
        branch_a = Task(objective="開發功能 A", depends_on=[root])
        branch_b = Task(objective="開發功能 B", depends_on=[root])

        # 第三層任務
        test_a = Task(objective="測試功能 A", depends_on=[branch_a])
        test_b = Task(objective="測試功能 B", depends_on=[branch_b])

        # 最終任務
        integration = Task(
            objective="集成測試",
            depends_on=[test_a, test_b]
        )

        print("   依賴關係已設置")
        print(f"   總任務數: 6")
        print()

        return integration


# ========== 任務配置選項 ==========

class TaskAdvancedOptions:
    """
    任務高級配置選項

    演示任務的高級配置功能
    """

    @staticmethod
    def create_task_with_timeout() -> Task:
        """
        創建帶超時設置的任務

        Returns:
            Task: 配置了超時的任務
        """
        print("📋 創建帶超時的任務...")

        task = Task(
            objective="執行長時間運算",
            instructions="這是一個可能需要較長時間的任務",
            timeout=timedelta(minutes=5)  # 5分鐘超時
        )

        print(f"   目標: {task.objective}")
        print(f"   超時設置: 5 分鐘")
        print()

        return task

    @staticmethod
    def create_task_with_retry() -> Task:
        """
        創建帶重試配置的任務

        Returns:
            Task: 配置了重試的任務
        """
        print("📋 創建帶重試的任務...")

        task = Task(
            objective="調用外部 API",
            instructions="獲取外部數據,失敗時自動重試",
            retry_count=3,  # 最多重試3次
            retry_delay=timedelta(seconds=2)  # 重試間隔2秒
        )

        print(f"   目標: {task.objective}")
        print(f"   重試次數: 3")
        print(f"   重試間隔: 2 秒")
        print()

        return task

    @staticmethod
    def create_task_with_priority() -> Task:
        """
        創建帶優先級的任務

        Returns:
            Task: 配置了優先級的任務
        """
        print("📋 創建帶優先級的任務...")

        task = Task(
            objective="緊急安全修復",
            instructions="立即處理安全漏洞",
            priority=TaskPriority.URGENT
        )

        print(f"   目標: {task.objective}")
        print(f"   優先級: {TaskPriority.URGENT}")
        print()

        return task

    @staticmethod
    def create_task_with_agent() -> Task:
        """
        創建帶專屬 Agent 的任務

        Returns:
            Task: 配置了特定 Agent 的任務
        """
        print("📋 創建帶專屬 Agent 的任務...")

        # 創建專業 Agent
        specialist = Agent(
            name="安全專家",
            instructions="你是一個網絡安全專家,專注於識別和修復安全漏洞",
            model="gpt-4"
        )

        task = Task(
            objective="執行安全審計",
            instructions="全面審查系統的安全性",
            agent=specialist
        )

        print(f"   目標: {task.objective}")
        print(f"   專屬 Agent: {specialist.name}")
        print()

        return task


# ========== 任務模板 ==========

class TaskTemplates:
    """
    常用任務模板

    提供一些預定義的任務模板,方便快速創建常見類型的任務
    """

    @staticmethod
    def create_research_task(topic: str, depth: str = "medium") -> Task:
        """
        創建研究任務

        Args:
            topic: 研究主題
            depth: 研究深度 (shallow/medium/deep)

        Returns:
            Task: 研究任務實例
        """
        instructions = {
            "shallow": "提供主題的概述和主要要點",
            "medium": "進行中等深度研究,包含詳細分析和例子",
            "deep": "進行深入研究,包含全面分析、多個來源和詳細見解"
        }

        return Task(
            objective=f"研究主題: {topic}",
            instructions=instructions.get(depth, instructions["medium"]),
            result_type=ResearchResult,
            context={"topic": topic, "depth": depth}
        )

    @staticmethod
    def create_analysis_task(data: Any, analysis_type: str) -> Task:
        """
        創建分析任務

        Args:
            data: 要分析的數據
            analysis_type: 分析類型

        Returns:
            Task: 分析任務實例
        """
        return Task(
            objective=f"執行{analysis_type}分析",
            instructions=f"""
            請對提供的數據執行{analysis_type}分析。
            分析應該包含:
            1. 數據概覽
            2. 關鍵發現
            3. 趨勢和模式
            4. 建議和結論
            """,
            result_type=AnalysisResult,
            context={"data": data, "type": analysis_type}
        )

    @staticmethod
    def create_validation_task(content: str, rules: List[str]) -> Task:
        """
        創建驗證任務

        Args:
            content: 要驗證的內容
            rules: 驗證規則列表

        Returns:
            Task: 驗證任務實例
        """
        return Task(
            objective="驗證內容",
            instructions=f"""
            請根據以下規則驗證內容:
            {chr(10).join(f'{i+1}. {rule}' for i, rule in enumerate(rules))}

            提供詳細的驗證結果,包括任何錯誤或警告。
            """,
            result_type=ValidationResult,
            context={"content": content, "rules": rules}
        )

    @staticmethod
    def create_summary_task(source: str, max_length: int = 200) -> Task:
        """
        創建摘要任務

        Args:
            source: 源文本
            max_length: 最大摘要長度

        Returns:
            Task: 摘要任務實例
        """
        return Task(
            objective="生成內容摘要",
            instructions=f"""
            請為提供的內容生成摘要。
            摘要應該:
            - 不超過 {max_length} 字
            - 保留關鍵信息
            - 清晰簡潔
            """,
            result_type=str,
            context={"source": source, "max_length": max_length}
        )

    @staticmethod
    def create_translation_task(
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Task:
        """
        創建翻譯任務

        Args:
            text: 要翻譯的文本
            source_lang: 源語言
            target_lang: 目標語言

        Returns:
            Task: 翻譯任務實例
        """
        return Task(
            objective=f"翻譯文本從{source_lang}到{target_lang}",
            instructions=f"""
            請將提供的文本從{source_lang}翻譯成{target_lang}。
            翻譯應該:
            - 準確傳達原意
            - 符合目標語言習慣
            - 保持專業術語的準確性
            """,
            result_type=str,
            context={
                "text": text,
                "source_lang": source_lang,
                "target_lang": target_lang
            }
        )


# ========== 任務執行模式 ==========

class TaskExecutionPatterns:
    """
    任務執行模式示例

    演示各種任務執行模式和最佳實踐
    """

    @staticmethod
    @cf.flow
    def batch_processing_pattern(items: List[str]):
        """
        批量處理模式

        Args:
            items: 要處理的項目列表
        """
        print(f"🔄 批量處理 {len(items)} 個項目...")

        results = []

        for item in items:
            task = Task(
                objective=f"處理項目: {item}",
                instructions="執行標準處理流程"
            )
            result = task.run()
            results.append(result)

        print(f"✅ 已處理 {len(results)} 個項目")
        return results

    @staticmethod
    @cf.flow
    def map_reduce_pattern(data_chunks: List[Any]):
        """
        Map-Reduce 模式

        Args:
            data_chunks: 數據塊列表
        """
        print("🗺️ 執行 Map-Reduce 模式...")

        # Map 階段: 並行處理每個數據塊
        map_tasks = []
        for i, chunk in enumerate(data_chunks):
            task = Task(
                objective=f"處理數據塊 {i+1}",
                instructions="分析數據塊並提取關鍵信息",
                context={"chunk": chunk}
            )
            map_tasks.append(task)

        # Reduce 階段: 匯總所有結果
        reduce_task = Task(
            objective="匯總所有結果",
            instructions="整合所有數據塊的分析結果",
            depends_on=map_tasks
        )

        final_result = reduce_task.run()

        print("✅ Map-Reduce 完成!")
        return final_result

    @staticmethod
    @cf.flow
    def pipeline_pattern(input_data: str):
        """
        管道模式

        Args:
            input_data: 輸入數據
        """
        print("🔧 執行管道模式...")

        # 階段 1: 預處理
        preprocess = Task(
            objective="預處理數據",
            context={"data": input_data}
        )

        # 階段 2: 轉換
        transform = Task(
            objective="轉換數據",
            depends_on=[preprocess]
        )

        # 階段 3: 增強
        enhance = Task(
            objective="增強數據",
            depends_on=[transform]
        )

        # 階段 4: 後處理
        postprocess = Task(
            objective="後處理數據",
            depends_on=[enhance]
        )

        result = postprocess.run()

        print("✅ 管道處理完成!")
        return result


# ========== 主程序 ==========

def main():
    """
    主程序入口

    演示各種任務定義和配置方法
    """
    print("=" * 70)
    print("  ControlFlow 任務定義示例")
    print("=" * 70)
    print()

    try:
        # 1. 基本任務配置
        print("\n" + "=" * 70)
        print("1. 基本任務配置")
        print("=" * 70 + "\n")

        basic_config = BasicTaskConfiguration()
        basic_config.create_simple_task()
        basic_config.create_task_with_instructions()
        basic_config.create_task_with_context()

        # 2. 任務結果類型
        print("\n" + "=" * 70)
        print("2. 任務結果類型")
        print("=" * 70 + "\n")

        result_types = TaskResultTypes()
        result_types.create_typed_task()
        result_types.create_list_result_task()
        result_types.create_dict_result_task()

        # 3. 任務依賴關係
        print("\n" + "=" * 70)
        print("3. 任務依賴關係")
        print("=" * 70 + "\n")

        dependencies = TaskDependencies()
        dependencies.demonstrate_complex_dependencies()

        # 4. 高級選項
        print("\n" + "=" * 70)
        print("4. 任務高級選項")
        print("=" * 70 + "\n")

        advanced = TaskAdvancedOptions()
        advanced.create_task_with_timeout()
        advanced.create_task_with_retry()
        advanced.create_task_with_priority()
        advanced.create_task_with_agent()

        # 5. 任務模板
        print("\n" + "=" * 70)
        print("5. 任務模板示例")
        print("=" * 70 + "\n")

        templates = TaskTemplates()
        research_task = templates.create_research_task("量子計算", "medium")
        print(f"✅ 創建研究任務: {research_task.objective}")

        validation_task = templates.create_validation_task(
            "示例內容",
            ["規則1: 不能為空", "規則2: 長度<100"]
        )
        print(f"✅ 創建驗證任務: {validation_task.objective}")

        summary_task = templates.create_summary_task("長文本內容...", 100)
        print(f"✅ 創建摘要任務: {summary_task.objective}")

        print("\n" + "=" * 70)
        print("演示完成")
        print("=" * 70)
        print("\n✅ 所有任務定義示例已成功執行!")
        print("\n💡 下一步:")
        print("   - 查看 03_流程控制.py 學習流程控制模式")
        print("   - 查看 04_條件分支.py 學習條件邏輯")
        print()

    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
