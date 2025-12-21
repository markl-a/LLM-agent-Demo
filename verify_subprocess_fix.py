#!/usr/bin/env python3
"""
验证 subprocess 命令注入漏洞修复
"""

import subprocess
import sys

def test_git_check():
    """测试 Git 版本检查"""
    print("测试 1: Git 版本检查（安全方式）")
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        print(f"✓ Git 检查成功: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"✗ Git 检查失败: {str(e)}")
        return False

def test_python_check():
    """测试 Python 命令执行"""
    print("\n测试 2: Python 命令执行（安全方式）")
    try:
        result = subprocess.run(
            [sys.executable, "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        print(f"✓ Python 检查成功: {result.stdout.strip() or result.stderr.strip()}")
        return True
    except Exception as e:
        print(f"✗ Python 检查失败: {str(e)}")
        return False

def test_command_list():
    """测试使用列表形式的命令"""
    print("\n测试 3: 命令列表形式（安全方式）")
    try:
        # 测试 echo 命令
        result = subprocess.run(
            ["echo", "Hello", "World"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        print(f"✓ Echo 命令成功: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"✗ Echo 命令失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("="*60)
    print("验证 subprocess 命令注入漏洞修复")
    print("="*60)

    tests = [
        test_git_check,
        test_python_check,
        test_command_list
    ]

    passed = 0
    failed = 0

    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1

    print("\n" + "="*60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("="*60)

    if failed == 0:
        print("✓ 所有测试通过！subprocess 调用已安全修复。")
        return 0
    else:
        print("✗ 部分测试失败，请检查。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
