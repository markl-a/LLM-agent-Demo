"""
複雜任務處理
===================================

本範例展示 Magentic-One 如何處理端到端的複雜任務。

複雜任務特點：
1. 多步驟執行
2. 跨多個領域
3. 需要多種能力
4. 可能有錯誤和重試
5. 需要人機協作

示例任務：
- 市場調研報告生成
- 數據分析和可視化
- 自動化測試流程
- 網站內容爬取和分析
- 代碼審查和優化
"""

import os
from typing import Dict, List, Any
from datetime import datetime
import json


class ComplexTaskExecutor:
    """
    複雜任務執行器

    協調多個 Agent 完成端到端的複雜任務
    """

    def __init__(self, magentic_one_system: Any):
        """
        初始化執行器

        Args:
            magentic_one_system: Magentic-One 系統實例
        """
        self.system = magentic_one_system
        self.task_history: List[Dict] = []

    def execute_market_research(
        self,
        topic: str,
        sources: List[str] = None
    ) -> Dict[str, Any]:
        """
        執行市場調研任務

        Args:
            topic: 調研主題
            sources: 信息來源列表

        Returns:
            調研報告
        """
        print(f"\n{'='*60}")
        print(f"任務: 市場調研 - {topic}")
        print(f"{'='*60}\n")

        sources = sources or ["官網", "行業報告", "新聞媒體"]

        # 定義任務流程
        workflow = [
            {
                'phase': '信息收集',
                'description': f'從 {len(sources)} 個來源收集關於 {topic} 的信息',
                'agent': 'web_surfer',
                'actions': [
                    f'搜索 {topic} 相關信息',
                    '提取關鍵數據點',
                    '保存原始數據'
                ]
            },
            {
                'phase': '數據分析',
                'description': '分析收集的數據',
                'agent': 'coder',
                'actions': [
                    '清理和結構化數據',
                    '執行統計分析',
                    '識別趨勢和模式'
                ]
            },
            {
                'phase': '可視化',
                'description': '創建數據可視化',
                'agent': 'coder',
                'actions': [
                    '生成圖表代碼',
                    '創建可視化',
                    '導出圖表'
                ]
            },
            {
                'phase': '報告生成',
                'description': '編寫調研報告',
                'agent': 'file_surfer',
                'actions': [
                    '組織報告結構',
                    '整合分析結果',
                    '保存最終報告'
                ]
            }
        ]

        results = self._execute_workflow(workflow)

        # 生成最終報告
        report = {
            'topic': topic,
            'sources': sources,
            'completion_time': datetime.now().isoformat(),
            'workflow_results': results,
            'summary': self._generate_summary(results)
        }

        self.task_history.append(report)

        print(f"\n✓ 市場調研完成")
        return report

    def execute_data_analysis_pipeline(
        self,
        data_source: str,
        analysis_type: str = "descriptive"
    ) -> Dict[str, Any]:
        """
        執行數據分析流程

        Args:
            data_source: 數據來源
            analysis_type: 分析類型 (descriptive/predictive/prescriptive)

        Returns:
            分析結果
        """
        print(f"\n{'='*60}")
        print(f"任務: 數據分析流程 - {analysis_type}")
        print(f"數據源: {data_source}")
        print(f"{'='*60}\n")

        workflow = [
            {
                'phase': '數據獲取',
                'description': f'從 {data_source} 獲取數據',
                'agent': 'file_surfer' if 'file' in data_source else 'web_surfer',
                'actions': [
                    '讀取數據',
                    '驗證數據格式',
                    '初步檢查'
                ]
            },
            {
                'phase': '數據清理',
                'description': '清理和預處理數據',
                'agent': 'coder',
                'actions': [
                    '處理缺失值',
                    '移除重複項',
                    '數據類型轉換',
                    '異常值處理'
                ]
            },
            {
                'phase': '探索性分析',
                'description': '執行 EDA',
                'agent': 'coder',
                'actions': [
                    '計算描述統計',
                    '生成分布圖',
                    '相關性分析',
                    '識別模式'
                ]
            },
            {
                'phase': '深度分析',
                'description': f'執行 {analysis_type} 分析',
                'agent': 'coder',
                'actions': [
                    '應用分析模型',
                    '生成洞察',
                    '驗證結果'
                ]
            },
            {
                'phase': '結果展示',
                'description': '創建分析報告',
                'agent': 'file_surfer',
                'actions': [
                    '生成可視化',
                    '編寫發現',
                    '創建報告',
                    '保存結果'
                ]
            }
        ]

        results = self._execute_workflow(workflow)

        analysis_result = {
            'data_source': data_source,
            'analysis_type': analysis_type,
            'completion_time': datetime.now().isoformat(),
            'workflow_results': results,
            'insights': self._extract_insights(results)
        }

        self.task_history.append(analysis_result)

        print(f"\n✓ 數據分析完成")
        return analysis_result

    def execute_automated_testing(
        self,
        code_repository: str,
        test_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        執行自動化測試流程

        Args:
            code_repository: 代碼倉庫路徑
            test_types: 測試類型列表

        Returns:
            測試結果
        """
        print(f"\n{'='*60}")
        print(f"任務: 自動化測試")
        print(f"倉庫: {code_repository}")
        print(f"{'='*60}\n")

        test_types = test_types or ['unit', 'integration', 'e2e']

        workflow = [
            {
                'phase': '環境準備',
                'description': '設置測試環境',
                'agent': 'terminal',
                'actions': [
                    '克隆代碼倉庫',
                    '安裝依賴',
                    '配置環境變量'
                ]
            },
            {
                'phase': '代碼分析',
                'description': '分析代碼結構',
                'agent': 'file_surfer',
                'actions': [
                    '掃描代碼文件',
                    '識別測試點',
                    '生成測試計劃'
                ]
            },
            {
                'phase': '測試生成',
                'description': '生成測試用例',
                'agent': 'coder',
                'actions': [
                    f'為每種類型生成測試: {", ".join(test_types)}',
                    '創建測試數據',
                    '配置測試框架'
                ]
            },
            {
                'phase': '執行測試',
                'description': '運行所有測試',
                'agent': 'terminal',
                'actions': [
                    '執行單元測試',
                    '執行集成測試',
                    '執行端到端測試',
                    '收集測試結果'
                ]
            },
            {
                'phase': '結果分析',
                'description': '分析測試結果',
                'agent': 'coder',
                'actions': [
                    '統計測試覆蓋率',
                    '分析失敗原因',
                    '生成測試報告'
                ]
            },
            {
                'phase': '報告生成',
                'description': '創建測試報告',
                'agent': 'file_surfer',
                'actions': [
                    '編譯測試結果',
                    '生成 HTML 報告',
                    '保存報告文件'
                ]
            }
        ]

        results = self._execute_workflow(workflow)

        test_result = {
            'repository': code_repository,
            'test_types': test_types,
            'completion_time': datetime.now().isoformat(),
            'workflow_results': results,
            'test_summary': self._summarize_tests(results)
        }

        self.task_history.append(test_result)

        print(f"\n✓ 自動化測試完成")
        return test_result

    def execute_web_scraping_analysis(
        self,
        target_websites: List[str],
        data_points: List[str]
    ) -> Dict[str, Any]:
        """
        執行網站爬取和分析

        Args:
            target_websites: 目標網站列表
            data_points: 要提取的數據點

        Returns:
            爬取和分析結果
        """
        print(f"\n{'='*60}")
        print(f"任務: 網站爬取和分析")
        print(f"目標: {len(target_websites)} 個網站")
        print(f"{'='*60}\n")

        workflow = [
            {
                'phase': '爬取規劃',
                'description': '制定爬取策略',
                'agent': 'web_surfer',
                'actions': [
                    '分析網站結構',
                    '識別數據位置',
                    '規劃爬取路徑'
                ]
            },
            {
                'phase': '數據爬取',
                'description': f'從 {len(target_websites)} 個網站爬取數據',
                'agent': 'web_surfer',
                'actions': [
                    '訪問目標網站',
                    f'提取數據點: {", ".join(data_points)}',
                    '處理動態內容',
                    '保存原始數據'
                ]
            },
            {
                'phase': '數據清理',
                'description': '清理爬取的數據',
                'agent': 'coder',
                'actions': [
                    '去除 HTML 標籤',
                    '標準化數據格式',
                    '去重處理'
                ]
            },
            {
                'phase': '數據分析',
                'description': '分析爬取的數據',
                'agent': 'coder',
                'actions': [
                    '統計分析',
                    '趨勢識別',
                    '異常檢測'
                ]
            },
            {
                'phase': '可視化',
                'description': '創建數據可視化',
                'agent': 'coder',
                'actions': [
                    '生成圖表',
                    '創建儀表板',
                    '導出可視化'
                ]
            },
            {
                'phase': '報告生成',
                'description': '生成分析報告',
                'agent': 'file_surfer',
                'actions': [
                    '整理分析結果',
                    '編寫報告',
                    '保存數據和報告'
                ]
            }
        ]

        results = self._execute_workflow(workflow)

        scraping_result = {
            'target_websites': target_websites,
            'data_points': data_points,
            'completion_time': datetime.now().isoformat(),
            'workflow_results': results,
            'data_summary': self._summarize_scraped_data(results)
        }

        self.task_history.append(scraping_result)

        print(f"\n✓ 網站爬取和分析完成")
        return scraping_result

    def execute_code_review_optimization(
        self,
        code_files: List[str]
    ) -> Dict[str, Any]:
        """
        執行代碼審查和優化

        Args:
            code_files: 代碼文件列表

        Returns:
            審查和優化結果
        """
        print(f"\n{'='*60}")
        print(f"任務: 代碼審查和優化")
        print(f"文件數: {len(code_files)}")
        print(f"{'='*60}\n")

        workflow = [
            {
                'phase': '代碼讀取',
                'description': '讀取所有代碼文件',
                'agent': 'file_surfer',
                'actions': [
                    '讀取代碼文件',
                    '解析代碼結構',
                    '識別模塊依賴'
                ]
            },
            {
                'phase': '靜態分析',
                'description': '執行靜態代碼分析',
                'agent': 'coder',
                'actions': [
                    '檢查語法錯誤',
                    '檢測代碼異味',
                    '分析複雜度',
                    '檢查安全問題'
                ]
            },
            {
                'phase': '代碼審查',
                'description': '深度代碼審查',
                'agent': 'coder',
                'actions': [
                    '檢查命名規範',
                    '檢查文檔完整性',
                    '檢查最佳實踐',
                    '性能分析'
                ]
            },
            {
                'phase': '優化建議',
                'description': '生成優化建議',
                'agent': 'coder',
                'actions': [
                    '識別優化機會',
                    '生成重構建議',
                    '提供代碼示例'
                ]
            },
            {
                'phase': '自動優化',
                'description': '應用自動優化',
                'agent': 'coder',
                'actions': [
                    '應用安全修復',
                    '格式化代碼',
                    '優化導入'
                ]
            },
            {
                'phase': '驗證測試',
                'description': '驗證優化結果',
                'agent': 'terminal',
                'actions': [
                    '運行測試套件',
                    '檢查性能改進',
                    '驗證功能完整性'
                ]
            },
            {
                'phase': '報告生成',
                'description': '生成審查報告',
                'agent': 'file_surfer',
                'actions': [
                    '編譯審查結果',
                    '創建改進清單',
                    '保存優化後的代碼',
                    '生成報告文檔'
                ]
            }
        ]

        results = self._execute_workflow(workflow)

        review_result = {
            'code_files': code_files,
            'completion_time': datetime.now().isoformat(),
            'workflow_results': results,
            'review_summary': self._summarize_code_review(results)
        }

        self.task_history.append(review_result)

        print(f"\n✓ 代碼審查和優化完成")
        return review_result

    # 內部輔助方法

    def _execute_workflow(self, workflow: List[Dict]) -> List[Dict]:
        """執行工作流"""
        results = []

        for i, phase in enumerate(workflow, 1):
            print(f"\n階段 {i}/{len(workflow)}: {phase['phase']}")
            print(f"  描述: {phase['description']}")
            print(f"  負責: {phase['agent']}")

            phase_result = {
                'phase': phase['phase'],
                'agent': phase['agent'],
                'actions_completed': [],
                'timestamp': datetime.now().isoformat()
            }

            # 執行各個動作
            for action in phase['actions']:
                print(f"    • {action}")
                phase_result['actions_completed'].append(action)

            phase_result['status'] = 'completed'
            results.append(phase_result)

            print(f"  ✓ {phase['phase']} 完成")

        return results

    def _generate_summary(self, results: List[Dict]) -> str:
        """生成摘要"""
        return f"成功完成 {len(results)} 個階段的工作流程"

    def _extract_insights(self, results: List[Dict]) -> List[str]:
        """提取洞察"""
        return [
            "數據質量良好",
            "發現明顯趨勢",
            "建議進一步分析"
        ]

    def _summarize_tests(self, results: List[Dict]) -> Dict:
        """總結測試結果"""
        return {
            'total_tests': 150,
            'passed': 145,
            'failed': 5,
            'coverage': '92%',
            'duration': '3.5 minutes'
        }

    def _summarize_scraped_data(self, results: List[Dict]) -> Dict:
        """總結爬取數據"""
        return {
            'total_pages': 50,
            'data_points_collected': 500,
            'unique_items': 350,
            'quality_score': '85%'
        }

    def _summarize_code_review(self, results: List[Dict]) -> Dict:
        """總結代碼審查"""
        return {
            'files_reviewed': 25,
            'issues_found': 48,
            'critical': 3,
            'warnings': 15,
            'suggestions': 30,
            'quality_score': 78
        }

    def get_task_history(self) -> List[Dict]:
        """獲取任務歷史"""
        return self.task_history


# 模擬 Magentic-One 系統
class MockMagenticOne:
    """模擬 Magentic-One 系統"""
    pass


def demo_market_research():
    """市場調研示範"""
    print("=" * 60)
    print("範例 1: 市場調研任務")
    print("=" * 60)

    system = MockMagenticOne()
    executor = ComplexTaskExecutor(system)

    result = executor.execute_market_research(
        topic="AI 代理框架市場",
        sources=["GitHub", "論文網站", "技術博客"]
    )

    print("\n任務完成摘要:")
    print(json.dumps(result['summary'], indent=2, ensure_ascii=False))


def demo_data_analysis():
    """數據分析示範"""
    print("\n" + "=" * 60)
    print("範例 2: 數據分析流程")
    print("=" * 60)

    system = MockMagenticOne()
    executor = ComplexTaskExecutor(system)

    result = executor.execute_data_analysis_pipeline(
        data_source="sales_data.csv",
        analysis_type="predictive"
    )

    print("\n分析洞察:")
    for insight in result['insights']:
        print(f"  • {insight}")


def demo_automated_testing():
    """自動化測試示範"""
    print("\n" + "=" * 60)
    print("範例 3: 自動化測試")
    print("=" * 60)

    system = MockMagenticOne()
    executor = ComplexTaskExecutor(system)

    result = executor.execute_automated_testing(
        code_repository="https://github.com/example/project",
        test_types=['unit', 'integration', 'e2e', 'performance']
    )

    print("\n測試摘要:")
    summary = result['test_summary']
    print(f"  總測試數: {summary['total_tests']}")
    print(f"  通過: {summary['passed']}")
    print(f"  失敗: {summary['failed']}")
    print(f"  覆蓋率: {summary['coverage']}")


def demo_web_scraping():
    """網站爬取示範"""
    print("\n" + "=" * 60)
    print("範例 4: 網站爬取和分析")
    print("=" * 60)

    system = MockMagenticOne()
    executor = ComplexTaskExecutor(system)

    result = executor.execute_web_scraping_analysis(
        target_websites=[
            "https://news.ycombinator.com",
            "https://www.reddit.com/r/MachineLearning",
            "https://arxiv.org"
        ],
        data_points=["標題", "分數", "評論數", "發布時間"]
    )

    print("\n爬取摘要:")
    summary = result['data_summary']
    print(f"  爬取頁面: {summary['total_pages']}")
    print(f"  收集數據點: {summary['data_points_collected']}")
    print(f"  唯一項目: {summary['unique_items']}")


def demo_code_review():
    """代碼審查示範"""
    print("\n" + "=" * 60)
    print("範例 5: 代碼審查和優化")
    print("=" * 60)

    system = MockMagenticOne()
    executor = ComplexTaskExecutor(system)

    result = executor.execute_code_review_optimization(
        code_files=[
            "src/main.py",
            "src/utils.py",
            "src/models.py",
            "tests/test_main.py"
        ]
    )

    print("\n審查摘要:")
    summary = result['review_summary']
    print(f"  審查文件數: {summary['files_reviewed']}")
    print(f"  發現問題: {summary['issues_found']}")
    print(f"    嚴重: {summary['critical']}")
    print(f"    警告: {summary['warnings']}")
    print(f"    建議: {summary['suggestions']}")
    print(f"  質量分數: {summary['quality_score']}/100")


if __name__ == "__main__":
    demo_market_research()
    demo_data_analysis()
    demo_automated_testing()
    demo_web_scraping()
    demo_code_review()

    print("\n" + "=" * 60)
    print("複雜任務處理示範完成！")
    print("=" * 60)
