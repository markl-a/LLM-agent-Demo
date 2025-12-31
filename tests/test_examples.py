"""
測試所有示例文件的語法和結構

此測試文件會：
1. 檢查示例文件的語法正確性
2. 驗證示例文件的結構
3. 檢查示例文件中的常見問題
4. 確保示例文件遵循最佳實踐

作者: LLM Agent Demo
日期: 2025-12-31
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Any

import pytest


@pytest.mark.unit
def test_examples_directory_exists(project_root):
    """測試 examples 目錄存在"""
    examples_dir = project_root / 'examples'
    assert examples_dir.exists(), "examples 目錄應該存在"
    assert examples_dir.is_dir(), "examples 應該是一個目錄"


@pytest.mark.unit
def test_example_files_have_docstrings(example_files):
    """測試示例文件是否有文檔字符串"""
    if not example_files:
        pytest.skip("沒有找到示例文件")

    files_without_docstring = []

    for py_file in example_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                source_code = f.read()

            tree = ast.parse(source_code)

            # 檢查模組級別的 docstring
            has_docstring = (
                tree.body and
                isinstance(tree.body[0], ast.Expr) and
                isinstance(tree.body[0].value, ast.Constant) and
                isinstance(tree.body[0].value.value, str)
            )

            if not has_docstring:
                files_without_docstring.append(py_file.name)

        except Exception:
            # 如果解析失敗，跳過此文件
            continue

    if files_without_docstring:
        print(f"\n{len(files_without_docstring)} 個示例文件沒有模組級文檔字符串:")
        for filename in files_without_docstring[:10]:
            print(f"  - {filename}")

        # 只是警告，不讓測試失敗
        print("\n建議為所有示例文件添加模組級文檔字符串")


@pytest.mark.unit
def test_example_files_no_hardcoded_keys(example_files):
    """測試示例文件中沒有硬編碼的 API keys"""
    if not example_files:
        pytest.skip("沒有找到示例文件")

    # 常見的 API key 模式
    api_key_patterns = [
        r'sk-[a-zA-Z0-9]{48}',  # OpenAI API key
        r'sk-proj-[a-zA-Z0-9_-]{48,}',  # OpenAI Project API key
        r'AIza[a-zA-Z0-9_-]{35}',  # Google API key
        r'sk-ant-[a-zA-Z0-9_-]{95}',  # Anthropic API key
    ]

    files_with_keys = []

    for py_file in example_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            for pattern in api_key_patterns:
                if re.search(pattern, content):
                    files_with_keys.append({
                        'file': py_file.name,
                        'pattern': pattern
                    })
                    break  # 找到一個就夠了

        except Exception:
            continue

    if files_with_keys:
        print(f"\n警告：發現 {len(files_with_keys)} 個文件可能包含硬編碼的 API keys:")
        for item in files_with_keys:
            print(f"  - {item['file']}")

        pytest.fail("示例文件中不應包含硬編碼的 API keys")


@pytest.mark.unit
def test_example_files_use_env_vars(example_files):
    """測試示例文件是否使用環境變數來獲取敏感信息"""
    if not example_files:
        pytest.skip("沒有找到示例文件")

    files_with_env_vars = []
    files_checked = 0

    for py_file in example_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            files_checked += 1

            # 檢查是否使用了 os.getenv 或 os.environ
            if 'os.getenv' in content or 'os.environ' in content:
                files_with_env_vars.append(py_file.name)

        except Exception:
            continue

    print(f"\n檢查了 {files_checked} 個示例文件")
    print(f"{len(files_with_env_vars)} 個文件使用環境變數獲取配置")

    # 這是個好的實踐，但不強制要求
    if files_with_env_vars:
        print("\n使用環境變數的文件（推薦做法）:")
        for filename in files_with_env_vars[:5]:
            print(f"  ✓ {filename}")


@pytest.mark.unit
def test_example_files_have_main_block(example_files):
    """測試示例文件是否有 if __name__ == '__main__': 代碼塊"""
    if not example_files:
        pytest.skip("沒有找到示例文件")

    files_with_main = []
    files_without_main = []

    for py_file in example_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if "__name__" in content and "__main__" in content:
                files_with_main.append(py_file.name)
            else:
                files_without_main.append(py_file.name)

        except Exception:
            continue

    print(f"\n{len(files_with_main)} 個示例文件有 main 代碼塊")

    if files_without_main:
        print(f"\n{len(files_without_main)} 個示例文件沒有 main 代碼塊:")
        for filename in files_without_main[:10]:
            print(f"  - {filename}")


@pytest.mark.unit
def test_example_files_imports_structure(example_files):
    """測試示例文件的導入語句結構是否合理"""
    if not example_files:
        pytest.skip("沒有找到示例文件")

    files_with_issues = []

    for py_file in example_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                source_code = f.read()

            tree = ast.parse(source_code)

            # 檢查導入語句順序
            import_nodes = []
            first_non_import_index = None

            for i, node in enumerate(tree.body):
                # 跳過文檔字符串
                if i == 0 and isinstance(node, ast.Expr):
                    continue

                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_nodes.append((i, node))
                elif first_non_import_index is None:
                    first_non_import_index = i

            # 檢查是否有導入語句在非導入語句之後
            if import_nodes and first_non_import_index:
                late_imports = [
                    (idx, node) for idx, node in import_nodes
                    if idx > first_non_import_index
                ]

                if late_imports:
                    files_with_issues.append({
                        'file': py_file.name,
                        'issue': '導入語句應該在文件開頭'
                    })

        except Exception:
            continue

    if files_with_issues:
        print(f"\n{len(files_with_issues)} 個文件的導入語句結構有問題:")
        for item in files_with_issues[:5]:
            print(f"  - {item['file']}: {item['issue']}")


@pytest.mark.unit
def test_example_files_no_print_statements(example_files):
    """測試示例文件是否過度使用 print 語句（建議使用 logging）"""
    if not example_files:
        pytest.skip("沒有找到示例文件")

    files_with_many_prints = []

    for py_file in example_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                source_code = f.read()

            tree = ast.parse(source_code)

            # 統計 print 調用次數
            print_count = 0
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id == 'print':
                        print_count += 1

            # 如果 print 語句超過 10 個，建議使用 logging
            if print_count > 10:
                files_with_many_prints.append({
                    'file': py_file.name,
                    'count': print_count
                })

        except Exception:
            continue

    if files_with_many_prints:
        print(f"\n{len(files_with_many_prints)} 個文件使用了大量 print 語句:")
        for item in files_with_many_prints[:5]:
            print(f"  - {item['file']}: {item['count']} 個 print 語句")
        print("\n建議使用 logging 模組替代 print 語句")


@pytest.mark.unit
def test_example_files_have_error_handling(example_files):
    """測試示例文件是否包含錯誤處理"""
    if not example_files:
        pytest.skip("沒有找到示例文件")

    files_with_try_except = []
    files_without_try_except = []

    for py_file in example_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                source_code = f.read()

            tree = ast.parse(source_code)

            # 檢查是否有 try-except 代碼塊
            has_error_handling = False
            for node in ast.walk(tree):
                if isinstance(node, ast.Try):
                    has_error_handling = True
                    break

            if has_error_handling:
                files_with_try_except.append(py_file.name)
            else:
                files_without_try_except.append(py_file.name)

        except Exception:
            continue

    print(f"\n{len(files_with_try_except)} 個示例文件包含錯誤處理")

    if files_without_try_except:
        print(f"\n{len(files_without_try_except)} 個示例文件沒有錯誤處理:")
        for filename in files_without_try_except[:10]:
            print(f"  - {filename}")
        print("\n建議添加適當的錯誤處理來提高代碼健壯性")


@pytest.mark.unit
def test_framework_example_files_syntax(framework_dirs):
    """測試框架目錄中的示例文件語法"""
    syntax_errors = []
    total_files = 0

    for framework_dir in framework_dirs:
        # 查找可能的示例文件
        example_patterns = ['*example*.py', '*demo*.py', '*sample*.py']
        example_files = []

        for pattern in example_patterns:
            example_files.extend(framework_dir.glob(f'**/{pattern}'))

        for py_file in example_files:
            total_files += 1
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    source_code = f.read()

                ast.parse(source_code, filename=str(py_file))

            except SyntaxError as e:
                syntax_errors.append({
                    'file': str(py_file),
                    'line': e.lineno,
                    'error': str(e),
                })

    print(f"\n掃描了 {total_files} 個框架示例文件")

    if syntax_errors:
        print(f"\n發現 {len(syntax_errors)} 個語法錯誤:")
        for error in syntax_errors[:5]:
            print(f"  - {error['file']}:{error['line']} - {error['error']}")

        pytest.fail(f"發現 {len(syntax_errors)} 個語法錯誤")


@pytest.mark.unit
def test_example_files_no_todos(example_files):
    """測試示例文件中的 TODO 註釋（可能表示未完成的工作）"""
    if not example_files:
        pytest.skip("沒有找到示例文件")

    files_with_todos = []

    for py_file in example_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 查找 TODO, FIXME, XXX 等標記
            todo_patterns = [r'# TODO', r'# FIXME', r'# XXX', r'# HACK']
            todos_found = []

            for pattern in todo_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    todos_found.append(pattern)

            if todos_found:
                files_with_todos.append({
                    'file': py_file.name,
                    'markers': todos_found
                })

        except Exception:
            continue

    if files_with_todos:
        print(f"\n{len(files_with_todos)} 個示例文件包含 TODO 標記:")
        for item in files_with_todos[:10]:
            print(f"  - {item['file']}: {', '.join(item['markers'])}")
        print("\n建議完成所有 TODO 項目後再發布")


@pytest.mark.unit
def test_example_files_reasonable_size(example_files):
    """測試示例文件大小是否合理"""
    if not example_files:
        pytest.skip("沒有找到示例文件")

    large_files = []
    small_files = []

    for py_file in example_files:
        file_size = py_file.stat().st_size

        # 大於 50KB 的文件可能太複雜
        if file_size > 50 * 1024:
            large_files.append({
                'file': py_file.name,
                'size': file_size // 1024
            })
        # 小於 100 字節的文件可能太簡單或為空
        elif file_size < 100:
            small_files.append({
                'file': py_file.name,
                'size': file_size
            })

    if large_files:
        print(f"\n{len(large_files)} 個示例文件較大:")
        for item in large_files[:5]:
            print(f"  - {item['file']}: {item['size']} KB")

    if small_files:
        print(f"\n{len(small_files)} 個示例文件較小:")
        for item in small_files:
            print(f"  - {item['file']}: {item['size']} 字節")


@pytest.mark.unit
def test_example_files_function_docstrings(example_files):
    """測試示例文件中的函數是否有文檔字符串"""
    if not example_files:
        pytest.skip("沒有找到示例文件")

    files_stats = []

    for py_file in example_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                source_code = f.read()

            tree = ast.parse(source_code)

            # 統計函數數量和有文檔字符串的函數數量
            total_functions = 0
            functions_with_docstring = 0

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    total_functions += 1

                    # 檢查函數是否有 docstring
                    if (
                        node.body and
                        isinstance(node.body[0], ast.Expr) and
                        isinstance(node.body[0].value, ast.Constant) and
                        isinstance(node.body[0].value.value, str)
                    ):
                        functions_with_docstring += 1

            if total_functions > 0:
                coverage = functions_with_docstring / total_functions
                files_stats.append({
                    'file': py_file.name,
                    'total': total_functions,
                    'documented': functions_with_docstring,
                    'coverage': coverage
                })

        except Exception:
            continue

    if files_stats:
        low_coverage = [s for s in files_stats if s['coverage'] < 0.5 and s['total'] >= 3]

        if low_coverage:
            print(f"\n{len(low_coverage)} 個文件的函數文檔覆蓋率較低:")
            for stat in low_coverage[:5]:
                print(
                    f"  - {stat['file']}: "
                    f"{stat['documented']}/{stat['total']} "
                    f"({stat['coverage']*100:.0f}%)"
                )
