"""
Coder - 代碼生成 Agent
===================================

Coder 是 Magentic-One 的編程專家，負責：
1. 代碼生成和重構
2. 代碼執行和調試
3. 測試用例創建
4. 代碼審查和優化
5. 多語言支持

支持語言：
- Python
- JavaScript/TypeScript
- Java
- C/C++
- Go
- Rust
- Shell/Bash
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import subprocess
from pathlib import Path


class CoderAgent:
    """
    代碼生成和執行 Agent

    負責所有與代碼相關的任務
    """

    def __init__(
        self,
        llm_config: Dict[str, Any],
        work_dir: str = "./code_workspace",
        use_docker: bool = False,
        timeout: int = 60
    ):
        """
        初始化 Coder

        Args:
            llm_config: LLM 配置
            work_dir: 工作目錄
            use_docker: 是否使用 Docker 沙盒
            timeout: 執行超時時間（秒）
        """
        self.llm_config = llm_config
        self.work_dir = Path(work_dir)
        self.use_docker = use_docker
        self.timeout = timeout

        # 確保工作目錄存在
        self.work_dir.mkdir(parents=True, exist_ok=True)

        # 統計
        self.stats = {
            'code_generated': 0,
            'code_executed': 0,
            'tests_created': 0,
            'errors_fixed': 0
        }

        # 語言配置
        self.language_config = {
            'python': {
                'extension': '.py',
                'executor': 'python3',
                'template': '# Python Code\n\n'
            },
            'javascript': {
                'extension': '.js',
                'executor': 'node',
                'template': '// JavaScript Code\n\n'
            },
            'bash': {
                'extension': '.sh',
                'executor': 'bash',
                'template': '#!/bin/bash\n\n'
            }
        }

    def generate_code(
        self,
        requirement: str,
        language: str = "python",
        include_tests: bool = False
    ) -> Dict[str, Any]:
        """
        生成代碼

        Args:
            requirement: 需求描述
            language: 編程語言
            include_tests: 是否包含測試

        Returns:
            生成的代碼
        """
        print(f"\n💻 生成 {language} 代碼")
        print(f"需求: {requirement}")

        try:
            # 使用 LLM 生成代碼（這裡簡化處理）
            code = self._generate_code_with_llm(requirement, language)

            # 生成測試（如果需要）
            tests = None
            if include_tests:
                tests = self._generate_tests(code, language)
                self.stats['tests_created'] += 1

            self.stats['code_generated'] += 1

            print(f"✓ 代碼生成完成")

            return {
                'success': True,
                'language': language,
                'code': code,
                'tests': tests,
                'requirement': requirement
            }

        except Exception as e:
            print(f"✗ 代碼生成失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def execute_code(
        self,
        code: str,
        language: str = "python",
        input_data: str = None
    ) -> Dict[str, Any]:
        """
        執行代碼

        Args:
            code: 代碼內容
            language: 編程語言
            input_data: 輸入數據

        Returns:
            執行結果
        """
        print(f"\n▶️ 執行 {language} 代碼")

        try:
            # 保存代碼到文件
            code_file = self._save_code_to_file(code, language)

            # 執行代碼
            if self.use_docker:
                result = self._execute_in_docker(code_file, language, input_data)
            else:
                result = self._execute_locally(code_file, language, input_data)

            self.stats['code_executed'] += 1

            print(f"✓ 執行完成")
            print(f"退出碼: {result['return_code']}")

            return {
                'success': result['return_code'] == 0,
                'output': result['stdout'],
                'error': result['stderr'],
                'return_code': result['return_code'],
                'execution_time': result['execution_time']
            }

        except Exception as e:
            print(f"✗ 執行失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def debug_code(self, code: str, error_message: str, language: str = "python") -> Dict[str, Any]:
        """
        調試代碼

        Args:
            code: 原始代碼
            error_message: 錯誤信息
            language: 編程語言

        Returns:
            修復後的代碼
        """
        print(f"\n🐛 調試代碼")
        print(f"錯誤: {error_message[:100]}...")

        try:
            # 分析錯誤
            error_analysis = self._analyze_error(code, error_message, language)

            # 生成修復後的代碼
            fixed_code = self._fix_code(code, error_analysis, language)

            # 驗證修復
            validation = self.execute_code(fixed_code, language)

            if validation['success']:
                self.stats['errors_fixed'] += 1
                print(f"✓ 錯誤已修復")
            else:
                print(f"⚠️ 修復後仍有問題")

            return {
                'success': validation['success'],
                'original_code': code,
                'fixed_code': fixed_code,
                'error_analysis': error_analysis,
                'validation_result': validation
            }

        except Exception as e:
            print(f"✗ 調試失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def optimize_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        優化代碼

        Args:
            code: 原始代碼
            language: 編程語言

        Returns:
            優化後的代碼
        """
        print(f"\n⚡ 優化代碼")

        try:
            # 分析代碼性能
            analysis = self._analyze_performance(code, language)

            # 生成優化建議
            suggestions = self._generate_optimization_suggestions(analysis)

            # 應用優化
            optimized_code = self._apply_optimizations(code, suggestions, language)

            print(f"✓ 優化完成")
            print(f"優化項目: {len(suggestions)}")

            return {
                'success': True,
                'original_code': code,
                'optimized_code': optimized_code,
                'suggestions': suggestions,
                'performance_analysis': analysis
            }

        except Exception as e:
            print(f"✗ 優化失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def create_tests(
        self,
        code: str,
        language: str = "python",
        test_framework: str = "pytest"
    ) -> Dict[str, Any]:
        """
        創建測試用例

        Args:
            code: 代碼內容
            language: 編程語言
            test_framework: 測試框架

        Returns:
            測試代碼
        """
        print(f"\n🧪 創建測試用例 ({test_framework})")

        try:
            # 分析代碼結構
            code_structure = self._analyze_code_structure(code, language)

            # 生成測試用例
            test_code = self._generate_test_cases(code_structure, language, test_framework)

            self.stats['tests_created'] += 1

            print(f"✓ 測試用例已生成")

            return {
                'success': True,
                'test_code': test_code,
                'test_framework': test_framework,
                'code_structure': code_structure
            }

        except Exception as e:
            print(f"✗ 測試生成失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def review_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        審查代碼

        Args:
            code: 代碼內容
            language: 編程語言

        Returns:
            審查報告
        """
        print(f"\n👀 審查代碼")

        try:
            # 檢查代碼風格
            style_issues = self._check_code_style(code, language)

            # 檢查潛在問題
            potential_bugs = self._detect_potential_bugs(code, language)

            # 檢查安全問題
            security_issues = self._check_security(code, language)

            # 檢查性能問題
            performance_issues = self._check_performance_issues(code, language)

            # 生成總體評分
            score = self._calculate_code_quality_score(
                style_issues,
                potential_bugs,
                security_issues,
                performance_issues
            )

            print(f"✓ 審查完成")
            print(f"代碼質量分數: {score}/100")

            return {
                'success': True,
                'quality_score': score,
                'style_issues': style_issues,
                'potential_bugs': potential_bugs,
                'security_issues': security_issues,
                'performance_issues': performance_issues
            }

        except Exception as e:
            print(f"✗ 審查失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def refactor_code(
        self,
        code: str,
        refactor_type: str,
        language: str = "python"
    ) -> Dict[str, Any]:
        """
        重構代碼

        Args:
            code: 原始代碼
            refactor_type: 重構類型 (extract_function/rename/simplify)
            language: 編程語言

        Returns:
            重構後的代碼
        """
        print(f"\n🔧 重構代碼 (類型: {refactor_type})")

        try:
            if refactor_type == "extract_function":
                refactored = self._extract_functions(code, language)
            elif refactor_type == "rename":
                refactored = self._rename_variables(code, language)
            elif refactor_type == "simplify":
                refactored = self._simplify_code(code, language)
            else:
                refactored = code

            print(f"✓ 重構完成")

            return {
                'success': True,
                'original_code': code,
                'refactored_code': refactored,
                'refactor_type': refactor_type
            }

        except Exception as e:
            print(f"✗ 重構失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # 內部輔助方法

    def _generate_code_with_llm(self, requirement: str, language: str) -> str:
        """使用 LLM 生成代碼"""
        # 簡化示例
        template = self.language_config[language]['template']

        if language == "python":
            code = f"""{template}def solution():
    \"\"\"
    {requirement}
    \"\"\"
    # TODO: 實現功能
    pass


if __name__ == "__main__":
    result = solution()
    print(result)
"""
        else:
            code = f"{template}// {requirement}\n// TODO: 實現功能\n"

        return code

    def _generate_tests(self, code: str, language: str) -> str:
        """生成測試代碼"""
        if language == "python":
            return """import pytest


def test_solution():
    \"\"\"測試主要功能\"\"\"
    # TODO: 添加測試用例
    assert True


def test_edge_cases():
    \"\"\"測試邊界情況\"\"\"
    # TODO: 添加邊界測試
    assert True
"""
        return "// 測試代碼"

    def _save_code_to_file(self, code: str, language: str) -> Path:
        """保存代碼到文件"""
        config = self.language_config.get(language, self.language_config['python'])
        filename = f"code_{datetime.now().strftime('%Y%m%d_%H%M%S')}{config['extension']}"
        filepath = self.work_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)

        return filepath

    def _execute_locally(
        self,
        code_file: Path,
        language: str,
        input_data: Optional[str]
    ) -> Dict[str, Any]:
        """在本地執行代碼"""
        config = self.language_config.get(language, self.language_config['python'])
        executor = config['executor']

        start_time = datetime.now()

        try:
            # 模擬執行（實際應使用 subprocess）
            result = {
                'stdout': f"執行輸出: {code_file.name}",
                'stderr': '',
                'return_code': 0
            }

        except subprocess.TimeoutExpired:
            result = {
                'stdout': '',
                'stderr': f'執行超時（超過 {self.timeout} 秒）',
                'return_code': -1
            }

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        result['execution_time'] = execution_time

        return result

    def _execute_in_docker(
        self,
        code_file: Path,
        language: str,
        input_data: Optional[str]
    ) -> Dict[str, Any]:
        """在 Docker 容器中執行代碼"""
        print("  使用 Docker 沙盒執行...")

        # 簡化處理
        return self._execute_locally(code_file, language, input_data)

    def _analyze_error(self, code: str, error_message: str, language: str) -> Dict:
        """分析錯誤"""
        return {
            'error_type': '語法錯誤',
            'location': '第 5 行',
            'suggestion': '檢查語法'
        }

    def _fix_code(self, code: str, error_analysis: Dict, language: str) -> str:
        """修復代碼"""
        # 簡化處理：返回原代碼加註釋
        return f"# 已修復: {error_analysis['error_type']}\n{code}"

    def _analyze_performance(self, code: str, language: str) -> Dict:
        """分析性能"""
        return {
            'complexity': 'O(n)',
            'memory_usage': '適中',
            'bottlenecks': []
        }

    def _generate_optimization_suggestions(self, analysis: Dict) -> List[str]:
        """生成優化建議"""
        return [
            '使用列表推導式代替循環',
            '減少重複計算',
            '使用生成器節省記憶體'
        ]

    def _apply_optimizations(self, code: str, suggestions: List[str], language: str) -> str:
        """應用優化"""
        return f"# 已優化代碼\n{code}"

    def _analyze_code_structure(self, code: str, language: str) -> Dict:
        """分析代碼結構"""
        return {
            'functions': ['solution'],
            'classes': [],
            'imports': []
        }

    def _generate_test_cases(self, structure: Dict, language: str, framework: str) -> str:
        """生成測試用例"""
        return self._generate_tests("", language)

    def _check_code_style(self, code: str, language: str) -> List[str]:
        """檢查代碼風格"""
        return ['變量命名不符合規範', '缺少文檔字符串']

    def _detect_potential_bugs(self, code: str, language: str) -> List[str]:
        """檢測潛在問題"""
        return ['未處理的異常', '可能的空指針']

    def _check_security(self, code: str, language: str) -> List[str]:
        """檢查安全問題"""
        return ['SQL 注入風險', '未驗證用戶輸入']

    def _check_performance_issues(self, code: str, language: str) -> List[str]:
        """檢查性能問題"""
        return ['循環中的重複計算']

    def _calculate_code_quality_score(
        self,
        style_issues: List,
        bugs: List,
        security: List,
        performance: List
    ) -> int:
        """計算代碼質量分數"""
        total_issues = len(style_issues) + len(bugs) + len(security) + len(performance)
        return max(0, 100 - (total_issues * 5))

    def _extract_functions(self, code: str, language: str) -> str:
        """提取函數"""
        return f"# 已提取函數\n{code}"

    def _rename_variables(self, code: str, language: str) -> str:
        """重命名變量"""
        return code

    def _simplify_code(self, code: str, language: str) -> str:
        """簡化代碼"""
        return f"# 已簡化\n{code}"

    def get_statistics(self) -> Dict[str, Any]:
        """獲取統計數據"""
        return self.stats.copy()


def demo_code_generation():
    """代碼生成示範"""
    print("=" * 60)
    print("範例 1: 代碼生成")
    print("=" * 60)

    coder = CoderAgent(llm_config={"model": "gpt-4"})

    result = coder.generate_code(
        "創建一個計算斐波那契數列的函數",
        language="python",
        include_tests=True
    )

    print("\n生成的代碼:")
    print(result['code'])

    if result['tests']:
        print("\n生成的測試:")
        print(result['tests'])


def demo_code_execution():
    """代碼執行示範"""
    print("\n" + "=" * 60)
    print("範例 2: 代碼執行")
    print("=" * 60)

    coder = CoderAgent(llm_config={"model": "gpt-4"})

    code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(f"5! = {factorial(5)}")
"""

    result = coder.execute_code(code, language="python")

    print("\n執行結果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


def demo_code_debugging():
    """代碼調試示範"""
    print("\n" + "=" * 60)
    print("範例 3: 代碼調試")
    print("=" * 60)

    coder = CoderAgent(llm_config={"model": "gpt-4"})

    buggy_code = """
def divide(a, b):
    return a / b  # 沒有處理除零錯誤

result = divide(10, 0)
"""

    result = coder.debug_code(
        buggy_code,
        "ZeroDivisionError: division by zero",
        language="python"
    )

    print("\n修復後的代碼:")
    print(result['fixed_code'])


def demo_code_review():
    """代碼審查示範"""
    print("\n" + "=" * 60)
    print("範例 4: 代碼審查")
    print("=" * 60)

    coder = CoderAgent(llm_config={"model": "gpt-4"})

    code_to_review = """
def process_data(data):
    result = []
    for i in range(len(data)):
        result.append(data[i] * 2)
    return result
"""

    result = coder.review_code(code_to_review, language="python")

    print("\n審查報告:")
    print(f"質量分數: {result['quality_score']}/100")
    print(f"\n風格問題: {result['style_issues']}")
    print(f"潛在問題: {result['potential_bugs']}")


def demo_code_optimization():
    """代碼優化示範"""
    print("\n" + "=" * 60)
    print("範例 5: 代碼優化")
    print("=" * 60)

    coder = CoderAgent(llm_config={"model": "gpt-4"})

    code_to_optimize = """
def find_duplicates(numbers):
    duplicates = []
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            if numbers[i] == numbers[j] and numbers[i] not in duplicates:
                duplicates.append(numbers[i])
    return duplicates
"""

    result = coder.optimize_code(code_to_optimize, language="python")

    print("\n優化建議:")
    for suggestion in result['suggestions']:
        print(f"  - {suggestion}")


if __name__ == "__main__":
    demo_code_generation()
    demo_code_execution()
    demo_code_debugging()
    demo_code_review()
    demo_code_optimization()

    print("\n" + "=" * 60)
    print("Coder 示範完成！")
    print("=" * 60)
