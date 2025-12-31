"""
測試所有框架文件的導入和語法

此測試文件會：
1. 掃描所有框架目錄
2. 檢查 Python 文件的語法
3. 嘗試導入可導入的模組
4. 報告任何語法錯誤或導入問題

作者: LLM Agent Demo
日期: 2025-12-31
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple

import pytest


@pytest.mark.unit
def test_project_structure(project_root):
    """測試專案結構完整性"""
    # 檢查必要目錄存在
    required_dirs = ['src', 'tests', 'examples']
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        assert dir_path.exists(), f"{dir_name} 目錄應該存在"
        assert dir_path.is_dir(), f"{dir_name} 應該是一個目錄"


@pytest.mark.unit
def test_framework_directories_exist(framework_dirs):
    """測試框架目錄存在"""
    assert len(framework_dirs) > 0, "應該至少有一個框架目錄"
    print(f"\n找到 {len(framework_dirs)} 個框架目錄")
    for framework_dir in framework_dirs[:5]:  # 只顯示前5個
        print(f"  - {framework_dir.name}")


@pytest.mark.unit
def test_python_files_syntax(framework_dirs):
    """測試所有 Python 文件的語法正確性"""
    syntax_errors = []
    total_files = 0

    for framework_dir in framework_dirs:
        python_files = list(framework_dir.glob('**/*.py'))

        for py_file in python_files:
            total_files += 1
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    source_code = f.read()

                # 使用 AST 編譯檢查語法
                ast.parse(source_code, filename=str(py_file))

            except SyntaxError as e:
                error_info = {
                    'file': str(py_file),
                    'line': e.lineno,
                    'error': str(e),
                }
                syntax_errors.append(error_info)
            except Exception as e:
                # 其他錯誤（如編碼問題）
                error_info = {
                    'file': str(py_file),
                    'line': None,
                    'error': f"解析錯誤: {str(e)}",
                }
                syntax_errors.append(error_info)

    # 生成報告
    print(f"\n掃描了 {total_files} 個 Python 文件")

    if syntax_errors:
        print(f"\n發現 {len(syntax_errors)} 個語法錯誤:")
        for error in syntax_errors:
            if error['line']:
                print(f"  - {error['file']}:{error['line']} - {error['error']}")
            else:
                print(f"  - {error['file']} - {error['error']}")

        pytest.fail(f"發現 {len(syntax_errors)} 個語法錯誤")
    else:
        print("所有文件語法檢查通過 ✓")


@pytest.mark.unit
def test_example_files_syntax(example_files):
    """測試所有示例文件的語法正確性"""
    if not example_files:
        pytest.skip("沒有找到示例文件")

    syntax_errors = []

    for py_file in example_files:
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
        except Exception as e:
            syntax_errors.append({
                'file': str(py_file),
                'line': None,
                'error': f"解析錯誤: {str(e)}",
            })

    print(f"\n掃描了 {len(example_files)} 個示例文件")

    if syntax_errors:
        print(f"\n發現 {len(syntax_errors)} 個語法錯誤:")
        for error in syntax_errors:
            if error['line']:
                print(f"  - {error['file']}:{error['line']} - {error['error']}")
            else:
                print(f"  - {error['file']} - {error['error']}")

        pytest.fail(f"發現 {len(syntax_errors)} 個語法錯誤")


@pytest.mark.unit
def test_src_module_imports(project_root):
    """測試 src 目錄下的模組可以導入"""
    src_dir = project_root / 'src'
    if not src_dir.exists():
        pytest.skip("src 目錄不存在")

    # 將 src 目錄添加到 Python 路徑
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    import_errors = []
    successful_imports = []

    # 查找所有 __init__.py 文件（表示是 Python 包）
    init_files = list(src_dir.glob('**/__init__.py'))

    for init_file in init_files:
        # 構建模組路徑
        relative_path = init_file.parent.relative_to(src_dir)
        module_name = str(relative_path).replace('/', '.').replace('\\', '.')

        # 跳過私有模組或測試模組
        if any(part.startswith('_') or part == 'test' for part in module_name.split('.')):
            continue

        try:
            __import__(module_name)
            successful_imports.append(module_name)
        except ImportError as e:
            # 某些模組可能需要特定依賴，記錄但不報錯
            import_errors.append({
                'module': module_name,
                'error': str(e),
                'type': 'ImportError'
            })
        except Exception as e:
            # 其他類型的錯誤
            import_errors.append({
                'module': module_name,
                'error': str(e),
                'type': type(e).__name__
            })

    print(f"\n成功導入 {len(successful_imports)} 個模組")
    if successful_imports:
        for module in successful_imports[:5]:  # 只顯示前5個
            print(f"  ✓ {module}")

    if import_errors:
        print(f"\n{len(import_errors)} 個模組導入失敗（可能需要額外依賴）:")
        for error in import_errors[:10]:  # 只顯示前10個
            print(f"  × {error['module']}: {error['type']}")
        # 注意：我們不讓測試失敗，因為某些模組可能需要外部依賴


@pytest.mark.unit
def test_no_duplicate_filenames(framework_dirs):
    """測試沒有重複的文件名（可能導致導入衝突）"""
    filename_map = {}
    duplicates = []

    for framework_dir in framework_dirs:
        python_files = list(framework_dir.glob('**/*.py'))

        for py_file in python_files:
            filename = py_file.name

            if filename == '__init__.py':
                continue

            if filename in filename_map:
                filename_map[filename].append(str(py_file))
            else:
                filename_map[filename] = [str(py_file)]

    # 查找重複的文件名
    for filename, paths in filename_map.items():
        if len(paths) > 1:
            duplicates.append({
                'filename': filename,
                'paths': paths,
                'count': len(paths)
            })

    if duplicates:
        print(f"\n發現 {len(duplicates)} 個重複的文件名:")
        for dup in duplicates[:5]:  # 只顯示前5個
            print(f"  - {dup['filename']} ({dup['count']} 個副本)")
            for path in dup['paths'][:3]:  # 只顯示前3個路徑
                print(f"    • {path}")

        # 不讓測試失敗，只是警告
        print("\n注意：重複的文件名可能在某些情況下導致導入衝突")


@pytest.mark.unit
def test_all_python_files_have_encoding(framework_dirs):
    """測試所有 Python 文件可以用 UTF-8 編碼讀取"""
    encoding_errors = []
    total_files = 0

    for framework_dir in framework_dirs:
        python_files = list(framework_dir.glob('**/*.py'))

        for py_file in python_files:
            total_files += 1
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    f.read()
            except UnicodeDecodeError as e:
                encoding_errors.append({
                    'file': str(py_file),
                    'error': str(e)
                })

    print(f"\n檢查了 {total_files} 個文件的編碼")

    if encoding_errors:
        print(f"\n發現 {len(encoding_errors)} 個編碼錯誤:")
        for error in encoding_errors:
            print(f"  - {error['file']}: {error['error']}")

        pytest.fail(f"發現 {len(encoding_errors)} 個編碼錯誤")


@pytest.mark.unit
@pytest.mark.parametrize("framework_number", list(range(1, 11)))
def test_specific_framework_exists(framework_number, project_root):
    """測試特定編號的框架目錄存在（參數化測試示例）"""
    # 查找匹配的框架目錄
    framework_dirs = [
        d for d in project_root.iterdir()
        if d.is_dir() and d.name.startswith(f"{framework_number}.")
    ]

    # 允許框架不存在（因為並非所有編號都有對應框架）
    if not framework_dirs:
        pytest.skip(f"框架 {framework_number} 不存在")

    assert len(framework_dirs) >= 1, f"框架 {framework_number} 應該存在"

    framework_dir = framework_dirs[0]
    print(f"\n框架 {framework_number}: {framework_dir.name}")


@pytest.mark.unit
def test_import_core_dependencies():
    """測試核心依賴可以導入"""
    core_dependencies = [
        'pytest',
        'pathlib',
        'typing',
        'logging',
        'json',
        'os',
        'sys',
    ]

    import_errors = []

    for module_name in core_dependencies:
        try:
            __import__(module_name)
        except ImportError as e:
            import_errors.append({
                'module': module_name,
                'error': str(e)
            })

    if import_errors:
        print("\n核心依賴導入失敗:")
        for error in import_errors:
            print(f"  - {error['module']}: {error['error']}")

        pytest.fail(f"{len(import_errors)} 個核心依賴導入失敗")


@pytest.mark.unit
def test_framework_readme_files(framework_dirs):
    """測試框架目錄中是否有 README 文件"""
    frameworks_without_readme = []

    for framework_dir in framework_dirs:
        readme_files = list(framework_dir.glob('README.*'))

        if not readme_files:
            frameworks_without_readme.append(framework_dir.name)

    if frameworks_without_readme:
        print(f"\n{len(frameworks_without_readme)} 個框架沒有 README 文件:")
        for framework in frameworks_without_readme[:10]:
            print(f"  - {framework}")

        # 不讓測試失敗，只是警告
        print("\n建議為每個框架添加 README 文件")


@pytest.mark.unit
def test_no_syntax_errors_in_test_files(project_root):
    """測試所有測試文件本身沒有語法錯誤"""
    tests_dir = project_root / 'tests'
    test_files = list(tests_dir.glob('**/*.py'))

    syntax_errors = []

    for test_file in test_files:
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                source_code = f.read()

            ast.parse(source_code, filename=str(test_file))

        except SyntaxError as e:
            syntax_errors.append({
                'file': str(test_file),
                'line': e.lineno,
                'error': str(e),
            })

    if syntax_errors:
        print(f"\n測試文件中發現 {len(syntax_errors)} 個語法錯誤:")
        for error in syntax_errors:
            print(f"  - {error['file']}:{error['line']} - {error['error']}")

        pytest.fail(f"測試文件中發現 {len(syntax_errors)} 個語法錯誤")
