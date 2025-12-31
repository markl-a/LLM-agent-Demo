"""
ControlFlow 條件分支詳解
========================

本文件深入探討 ControlFlow 中的條件分支和路由,包括:
1. 基本條件判斷
2. 多路分支
3. 智能路由
4. 基於 AI 的決策
5. 動態工作流選擇
6. 複雜條件組合
7. 錯誤處理和降級

作者: ControlFlow 示例團隊
日期: 2025
"""

import os
from typing import Optional, List, Dict, Any, Union, Literal
from datetime import datetime
from enum import Enum
import controlflow as cf
from controlflow import Agent, Task, Flow
from pydantic import BaseModel, Field
from dotenv import load_dotenv


# ========== 配置 ==========

load_dotenv()


# ========== 數據模型 ==========

class Priority(str, Enum):
    """優先級枚舉"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskType(str, Enum):
    """任務類型枚舉"""
    RESEARCH = "research"
    ANALYSIS = "analysis"
    CREATION = "creation"
    REVIEW = "review"
    DEPLOYMENT = "deployment"


class RoutingDecision(BaseModel):
    """路由決策模型"""
    route: str = Field(description="選擇的路由")
    confidence: float = Field(ge=0, le=1, description="決策信心度")
    reason: str = Field(description="決策原因")
    alternative_routes: List[str] = Field(default_factory=list, description="備選路由")


class RequestAnalysis(BaseModel):
    """請求分析模型"""
    complexity: Literal["simple", "medium", "complex"] = Field(description="複雜度")
    urgency: Priority = Field(description="緊急程度")
    estimated_duration: int = Field(description="預計耗時(分鐘)")
    required_resources: List[str] = Field(description="所需資源")


# ========== 基本條件分支 ==========

class BasicConditionals:
    """
    基本條件分支示例

    演示基礎的條件判斷和分支
    """

    @staticmethod
    @cf.flow
    def simple_if_else(value: int):
        """
        簡單 if-else 分支

        Args:
            value: 輸入值
        """
        print(f"🔀 簡單 If-Else 分支 (值: {value})...")

        if value > 50:
            print("  ➡️ 執行高值處理路徑")
            task = Task(
                objective="處理高值數據",
                instructions="使用高精度算法處理",
                context={"value": value}
            )
        else:
            print("  ➡️ 執行低值處理路徑")
            task = Task(
                objective="處理低值數據",
                instructions="使用標準算法處理",
                context={"value": value}
            )

        result = task.run()
        print("✅ 分支執行完成!")
        return result

    @staticmethod
    @cf.flow
    def multi_way_branch(category: str):
        """
        多路分支

        Args:
            category: 類別
        """
        print(f"🔀 多路分支 (類別: {category})...")

        # 根據類別選擇不同的處理邏輯
        if category == "urgent":
            print("  🚨 緊急處理路徑")
            task = Task(
                objective="緊急任務處理",
                instructions="立即處理,優先級最高",
                priority=Priority.CRITICAL
            )

        elif category == "important":
            print("  ⚡ 重要處理路徑")
            task = Task(
                objective="重要任務處理",
                instructions="優先處理,確保質量",
                priority=Priority.HIGH
            )

        elif category == "normal":
            print("  📋 標準處理路徑")
            task = Task(
                objective="標準任務處理",
                instructions="按正常流程處理",
                priority=Priority.MEDIUM
            )

        else:
            print("  📝 低優先級處理路徑")
            task = Task(
                objective="低優先級任務處理",
                instructions="在資源允許時處理",
                priority=Priority.LOW
            )

        result = task.run()
        print("✅ 多路分支完成!")
        return result

    @staticmethod
    @cf.flow
    def nested_conditions(user_type: str, is_premium: bool):
        """
        嵌套條件

        Args:
            user_type: 用戶類型
            is_premium: 是否為高級用戶
        """
        print(f"🔀 嵌套條件 (類型: {user_type}, 高級: {is_premium})...")

        if user_type == "enterprise":
            if is_premium:
                print("  👑 企業高級用戶路徑")
                service_level = "platinum"
            else:
                print("  🏢 企業標準用戶路徑")
                service_level = "gold"
        elif user_type == "individual":
            if is_premium:
                print("  ⭐ 個人高級用戶路徑")
                service_level = "silver"
            else:
                print("  👤 個人標準用戶路徑")
                service_level = "bronze"
        else:
            print("  🆓 訪客路徑")
            service_level = "free"

        task = Task(
            objective=f"提供{service_level}級別服務",
            instructions=f"根據{service_level}服務級別提供支持",
            context={
                "user_type": user_type,
                "is_premium": is_premium,
                "service_level": service_level
            }
        )

        result = task.run()
        print("✅ 嵌套條件處理完成!")
        return result


# ========== 智能路由 ==========

class IntelligentRouting:
    """
    智能路由示例

    使用 AI 進行智能路由決策
    """

    def __init__(self):
        """初始化路由器"""
        self.router_agent = Agent(
            name="路由決策器",
            instructions="""
            你是一個智能路由決策系統。
            分析輸入請求,選擇最合適的處理路徑。
            考慮複雜度、緊急程度、資源需求等因素。
            """,
            model="gpt-4"
        )

    @cf.flow
    def ai_based_routing(self, request: str):
        """
        基於 AI 的智能路由

        Args:
            request: 用戶請求
        """
        print(f"🤖 AI 智能路由...")
        print(f"   請求: {request[:100]}...")

        # 步驟 1: 分析請求
        print("\n  📊 分析請求...")
        analysis_task = Task(
            objective="分析請求特徵",
            instructions="""
            分析用戶請求,評估:
            1. 複雜度 (simple/medium/complex)
            2. 緊急程度 (low/medium/high/critical)
            3. 預計耗時
            4. 所需資源

            返回結構化的分析結果。
            """,
            result_type=RequestAnalysis,
            agent=self.router_agent,
            context={"request": request}
        )

        analysis = analysis_task.run()
        print(f"     複雜度: {analysis.complexity}")
        print(f"     緊急度: {analysis.urgency}")
        print(f"     預計耗時: {analysis.estimated_duration} 分鐘")

        # 步驟 2: 選擇路由
        print("\n  🚦 選擇處理路徑...")
        routing_task = Task(
            objective="決定處理路徑",
            instructions="""
            基於請求分析結果,選擇最合適的處理路徑:
            - express_path: 簡單快速處理
            - standard_path: 標準處理流程
            - expert_path: 複雜深度處理
            - custom_path: 定制化處理

            返回詳細的路由決策。
            """,
            result_type=RoutingDecision,
            agent=self.router_agent,
            context={"analysis": analysis.dict()}
        )

        decision = routing_task.run()
        print(f"     選擇路由: {decision.route}")
        print(f"     信心度: {decision.confidence:.2%}")
        print(f"     原因: {decision.reason}")

        # 步驟 3: 執行選擇的路徑
        print(f"\n  ▶️ 執行路徑: {decision.route}")
        result = self._execute_route(decision.route, request, analysis)

        print("\n✅ AI 路由完成!")
        return result

    def _execute_route(
        self,
        route: str,
        request: str,
        analysis: RequestAnalysis
    ):
        """
        執行選定的路由

        Args:
            route: 路由名稱
            request: 原始請求
            analysis: 請求分析結果
        """
        route_tasks = {
            "express_path": Task(
                objective="快速處理請求",
                instructions="使用快速算法,優先速度",
                context={"request": request}
            ),
            "standard_path": Task(
                objective="標準處理請求",
                instructions="使用標準流程,平衡速度和質量",
                context={"request": request}
            ),
            "expert_path": Task(
                objective="專家級處理請求",
                instructions="使用高級算法,優先質量",
                context={"request": request}
            ),
            "custom_path": Task(
                objective="定制化處理請求",
                instructions="根據具體需求定制處理方案",
                context={"request": request, "analysis": analysis.dict()}
            )
        }

        task = route_tasks.get(route, route_tasks["standard_path"])
        return task.run()

    @cf.flow
    def load_based_routing(self, current_load: float):
        """
        基於負載的路由

        Args:
            current_load: 當前系統負載 (0-1)
        """
        print(f"⚖️ 負載感知路由 (當前負載: {current_load:.2%})...")

        if current_load < 0.3:
            print("  🟢 低負載 - 使用完整處理管道")
            processing_mode = "full_pipeline"
            task = Task(
                objective="完整處理管道",
                instructions="執行所有處理步驟,包括優化和增強",
                context={"load": current_load}
            )

        elif current_load < 0.7:
            print("  🟡 中等負載 - 使用標準處理")
            processing_mode = "standard"
            task = Task(
                objective="標準處理",
                instructions="執行核心處理步驟",
                context={"load": current_load}
            )

        else:
            print("  🔴 高負載 - 使用快速模式")
            processing_mode = "fast_mode"
            task = Task(
                objective="快速處理",
                instructions="使用最小化處理,確保系統穩定",
                context={"load": current_load}
            )

        result = task.run()
        print(f"✅ 負載路由完成 (模式: {processing_mode})!")
        return result


# ========== 動態工作流選擇 ==========

class DynamicWorkflowSelection:
    """
    動態工作流選擇

    根據條件動態選擇不同的工作流
    """

    @staticmethod
    @cf.flow
    def content_type_workflow(content_type: str, content: str):
        """
        根據內容類型選擇工作流

        Args:
            content_type: 內容類型
            content: 內容
        """
        print(f"🔄 動態工作流選擇 (類型: {content_type})...")

        if content_type == "code":
            return DynamicWorkflowSelection._code_review_workflow(content)
        elif content_type == "document":
            return DynamicWorkflowSelection._document_analysis_workflow(content)
        elif content_type == "data":
            return DynamicWorkflowSelection._data_processing_workflow(content)
        else:
            return DynamicWorkflowSelection._generic_workflow(content)

    @staticmethod
    def _code_review_workflow(code: str):
        """代碼審查工作流"""
        print("  💻 執行代碼審查工作流...")

        # 步驟 1: 語法檢查
        syntax_task = Task(
            objective="語法檢查",
            instructions="檢查代碼語法錯誤",
            context={"code": code}
        )
        syntax_result = syntax_task.run()

        # 步驟 2: 風格檢查
        style_task = Task(
            objective="代碼風格檢查",
            instructions="檢查代碼風格和最佳實踐",
            context={"code": code}
        )
        style_result = style_task.run()

        # 步驟 3: 安全審計
        security_task = Task(
            objective="安全審計",
            instructions="檢查潛在的安全漏洞",
            context={"code": code}
        )
        security_result = security_task.run()

        # 步驟 4: 生成報告
        report_task = Task(
            objective="生成審查報告",
            instructions="整合所有檢查結果,生成詳細報告",
            context={
                "syntax": syntax_result,
                "style": style_result,
                "security": security_result
            }
        )

        return report_task.run()

    @staticmethod
    def _document_analysis_workflow(document: str):
        """文檔分析工作流"""
        print("  📄 執行文檔分析工作流...")

        # 步驟 1: 提取關鍵信息
        extract_task = Task(
            objective="提取關鍵信息",
            context={"document": document}
        )
        key_info = extract_task.run()

        # 步驟 2: 情感分析
        sentiment_task = Task(
            objective="情感分析",
            context={"document": document}
        )
        sentiment = sentiment_task.run()

        # 步驟 3: 生成摘要
        summary_task = Task(
            objective="生成文檔摘要",
            context={
                "document": document,
                "key_info": key_info,
                "sentiment": sentiment
            }
        )

        return summary_task.run()

    @staticmethod
    def _data_processing_workflow(data: str):
        """數據處理工作流"""
        print("  📊 執行數據處理工作流...")

        # 步驟 1: 數據清洗
        clean_task = Task(
            objective="數據清洗",
            context={"data": data}
        )
        clean_data = clean_task.run()

        # 步驟 2: 數據分析
        analysis_task = Task(
            objective="數據統計分析",
            context={"data": clean_data}
        )
        analysis = analysis_task.run()

        # 步驟 3: 可視化建議
        viz_task = Task(
            objective="生成可視化建議",
            context={"analysis": analysis}
        )

        return viz_task.run()

    @staticmethod
    def _generic_workflow(content: str):
        """通用工作流"""
        print("  🔧 執行通用工作流...")

        task = Task(
            objective="通用內容處理",
            instructions="對未知類型的內容進行通用處理",
            context={"content": content}
        )

        return task.run()


# ========== 複雜條件組合 ==========

class ComplexConditions:
    """
    複雜條件組合

    處理多個條件的組合和複雜邏輯
    """

    @staticmethod
    @cf.flow
    def multi_criteria_decision(criteria: Dict[str, Any]):
        """
        多標準決策

        Args:
            criteria: 決策標準字典
        """
        print("🎯 多標準決策...")
        print(f"   標準: {list(criteria.keys())}")

        # 評分系統
        score = 0

        # 標準 1: 用戶級別
        user_level = criteria.get("user_level", "basic")
        if user_level == "premium":
            score += 30
        elif user_level == "enterprise":
            score += 50

        # 標準 2: 請求複雜度
        complexity = criteria.get("complexity", "medium")
        if complexity == "simple":
            score += 10
        elif complexity == "complex":
            score += 40

        # 標準 3: 數據量
        data_size = criteria.get("data_size", 0)
        if data_size > 1000:
            score += 20
        elif data_size > 100:
            score += 10

        # 標準 4: 時間限制
        time_limit = criteria.get("time_limit", 60)
        if time_limit < 10:
            score += 30  # 緊急
        elif time_limit < 30:
            score += 20

        print(f"   總評分: {score}")

        # 根據總評分選擇策略
        if score >= 80:
            print("  🚀 選擇高性能策略")
            strategy = "high_performance"
            task = Task(
                objective="高性能處理",
                instructions="使用最優資源配置,確保最佳性能",
                context=criteria
            )
        elif score >= 50:
            print("  ⚡ 選擇優化策略")
            strategy = "optimized"
            task = Task(
                objective="優化處理",
                instructions="平衡性能和資源消耗",
                context=criteria
            )
        elif score >= 25:
            print("  📋 選擇標準策略")
            strategy = "standard"
            task = Task(
                objective="標準處理",
                instructions="使用標準配置",
                context=criteria
            )
        else:
            print("  💤 選擇節能策略")
            strategy = "economical"
            task = Task(
                objective="經濟處理",
                instructions="最小化資源使用",
                context=criteria
            )

        result = task.run()
        print(f"✅ 多標準決策完成 (策略: {strategy})!")
        return result

    @staticmethod
    @cf.flow
    def rule_based_routing(rules: List[Dict[str, Any]], input_data: Dict[str, Any]):
        """
        基於規則的路由

        Args:
            rules: 規則列表
            input_data: 輸入數據
        """
        print("📏 基於規則的路由...")
        print(f"   規則數量: {len(rules)}")

        # 評估每條規則
        matched_rules = []

        for i, rule in enumerate(rules):
            print(f"\n  評估規則 {i+1}...")

            # 檢查規則條件
            conditions = rule.get("conditions", {})
            all_match = True

            for key, expected_value in conditions.items():
                actual_value = input_data.get(key)
                if actual_value != expected_value:
                    all_match = False
                    break

            if all_match:
                print(f"    ✅ 規則 {i+1} 匹配!")
                matched_rules.append(rule)

        # 執行匹配的規則
        if matched_rules:
            # 使用優先級最高的規則
            selected_rule = max(matched_rules, key=lambda r: r.get("priority", 0))
            print(f"\n  🎯 執行規則: {selected_rule.get('name', '未命名')}")

            task = Task(
                objective=selected_rule.get("action", "執行默認操作"),
                instructions=selected_rule.get("instructions", ""),
                context=input_data
            )

            result = task.run()
        else:
            print("\n  ⚠️ 無匹配規則,執行默認處理")
            task = Task(
                objective="默認處理",
                instructions="沒有匹配的規則,執行默認邏輯",
                context=input_data
            )
            result = task.run()

        print("✅ 規則路由完成!")
        return result


# ========== 錯誤處理和降級 ==========

class ErrorHandlingAndFallback:
    """
    錯誤處理和降級策略

    處理異常情況和實現優雅降級
    """

    @staticmethod
    @cf.flow
    def try_with_fallback(primary_method: str, fallback_method: str):
        """
        嘗試主方法,失敗則使用備用方法

        Args:
            primary_method: 主要方法
            fallback_method: 備用方法
        """
        print(f"🔄 嘗試主方法,帶降級...")
        print(f"   主方法: {primary_method}")
        print(f"   備用: {fallback_method}")

        try:
            print("\n  ▶️ 嘗試主方法...")
            primary_task = Task(
                objective=f"執行主方法: {primary_method}",
                instructions="嘗試使用首選方法處理",
                context={"method": primary_method}
            )

            result = primary_task.run()
            print("  ✅ 主方法成功!")
            return {"success": True, "method": "primary", "result": result}

        except Exception as e:
            print(f"  ❌ 主方法失敗: {str(e)}")
            print(f"\n  🔄 切換到備用方法...")

            fallback_task = Task(
                objective=f"執行備用方法: {fallback_method}",
                instructions="使用備用方法處理",
                context={"method": fallback_method, "error": str(e)}
            )

            result = fallback_task.run()
            print("  ✅ 備用方法成功!")
            return {"success": True, "method": "fallback", "result": result}

    @staticmethod
    @cf.flow
    def multi_level_fallback(methods: List[str]):
        """
        多級降級

        Args:
            methods: 方法列表(按優先級排序)
        """
        print(f"🔄 多級降級策略...")
        print(f"   方法鏈: {' -> '.join(methods)}")

        last_error = None

        for i, method in enumerate(methods):
            try:
                print(f"\n  📍 嘗試方法 {i+1}/{len(methods)}: {method}")

                task = Task(
                    objective=f"執行方法: {method}",
                    instructions=f"使用 {method} 處理請求",
                    context={"method": method, "attempt": i+1}
                )

                result = task.run()
                print(f"  ✅ 方法 {method} 成功!")
                return {
                    "success": True,
                    "method": method,
                    "attempt": i+1,
                    "result": result
                }

            except Exception as e:
                print(f"  ❌ 方法 {method} 失敗: {str(e)}")
                last_error = e

                if i < len(methods) - 1:
                    print(f"  🔄 降級到下一個方法...")
                else:
                    print(f"  ⛔ 所有方法都失敗了!")

        # 所有方法都失敗
        return {
            "success": False,
            "error": str(last_error),
            "attempted_methods": methods
        }

    @staticmethod
    @cf.flow
    def graceful_degradation(feature_flags: Dict[str, bool]):
        """
        優雅降級

        根據功能開關提供降級服務

        Args:
            feature_flags: 功能開關字典
        """
        print("🎚️ 優雅降級...")
        print(f"   功能狀態: {feature_flags}")

        # 檢查高級功能
        if feature_flags.get("advanced_analytics", False):
            print("  🚀 提供完整高級分析")
            task = Task(
                objective="高級分析",
                instructions="執行完整的高級分析功能"
            )

        # 檢查標準功能
        elif feature_flags.get("standard_analytics", False):
            print("  📊 提供標準分析")
            task = Task(
                objective="標準分析",
                instructions="執行標準分析功能"
            )

        # 基礎功能
        elif feature_flags.get("basic_analytics", False):
            print("  📈 提供基礎分析")
            task = Task(
                objective="基礎分析",
                instructions="執行基礎分析功能"
            )

        # 最小功能
        else:
            print("  📝 提供最小功能")
            task = Task(
                objective="最小功能",
                instructions="提供基本的數據展示"
            )

        result = task.run()
        print("✅ 優雅降級完成!")
        return result


# ========== 主程序 ==========

def main():
    """
    主程序入口

    演示各種條件分支模式
    """
    print("=" * 70)
    print("  ControlFlow 條件分支示例")
    print("=" * 70)
    print()

    try:
        # 1. 基本條件分支
        print("\n" + "=" * 70)
        print("1. 基本條件分支")
        print("=" * 70)

        basic = BasicConditionals()
        # basic.simple_if_else(75)
        # basic.multi_way_branch("urgent")
        # basic.nested_conditions("enterprise", True)
        print("✅ 基本條件分支示例已定義")

        # 2. 智能路由
        print("\n" + "=" * 70)
        print("2. 智能路由")
        print("=" * 70)

        router = IntelligentRouting()
        # router.ai_based_routing("幫我分析這個複雜的數據集...")
        # router.load_based_routing(0.45)
        print("✅ 智能路由示例已定義")

        # 3. 動態工作流
        print("\n" + "=" * 70)
        print("3. 動態工作流選擇")
        print("=" * 70)

        dynamic = DynamicWorkflowSelection()
        # dynamic.content_type_workflow("code", "def example(): pass")
        print("✅ 動態工作流示例已定義")

        # 4. 複雜條件
        print("\n" + "=" * 70)
        print("4. 複雜條件組合")
        print("=" * 70)

        complex_cond = ComplexConditions()
        # complex_cond.multi_criteria_decision({
        #     "user_level": "enterprise",
        #     "complexity": "complex",
        #     "data_size": 1500,
        #     "time_limit": 5
        # })
        print("✅ 複雜條件示例已定義")

        # 5. 錯誤處理
        print("\n" + "=" * 70)
        print("5. 錯誤處理和降級")
        print("=" * 70)

        error_handler = ErrorHandlingAndFallback()
        # error_handler.multi_level_fallback(["method_a", "method_b", "method_c"])
        # error_handler.graceful_degradation({
        #     "advanced_analytics": False,
        #     "standard_analytics": True,
        #     "basic_analytics": True
        # })
        print("✅ 錯誤處理示例已定義")

        print("\n" + "=" * 70)
        print("演示完成")
        print("=" * 70)
        print("\n✅ 所有條件分支模式已成功展示!")
        print("\n💡 條件分支要點:")
        print("   - 基本分支: if-else, switch-case")
        print("   - 智能路由: AI 驅動的決策")
        print("   - 動態選擇: 運行時工作流選擇")
        print("   - 複雜條件: 多標準評分和規則引擎")
        print("   - 錯誤處理: 降級策略和容錯機制")
        print("\n💡 下一步:")
        print("   - 查看 05_Agent創建.py 學習 Agent 配置")
        print("   - 查看 06_工具整合.py 學習工具開發")
        print()

    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
