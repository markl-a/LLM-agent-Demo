#!/usr/bin/env python3
"""
LLM Agent Demo - Docker Health Check Script
容器健康檢查腳本，用於驗證應用是否正常運行

退出碼：
- 0: 健康
- 1: 不健康
"""

import os
import sys
from pathlib import Path


def check_python_environment():
    """檢查 Python 環境"""
    try:
        # 檢查 Python 版本
        if sys.version_info < (3, 9):
            print("Python version is too old")
            return False

        # 檢查關鍵包是否可導入
        critical_packages = [
            "langchain",
            "openai",
            "dotenv",
        ]

        for package in critical_packages:
            try:
                __import__(package)
            except ImportError:
                print(f"Critical package '{package}' is not available")
                return False

        return True
    except Exception as e:
        print(f"Python environment check failed: {e}")
        return False


def check_directories():
    """檢查必要的目錄"""
    try:
        required_dirs = [
            "/app/data",
            "/app/outputs",
            "/app/logs",
        ]

        for directory in required_dirs:
            path = Path(directory)
            if not path.exists():
                print(f"Required directory does not exist: {directory}")
                return False

            if not path.is_dir():
                print(f"Path is not a directory: {directory}")
                return False

            # 檢查寫入權限（嘗試創建臨時文件）
            try:
                test_file = path / ".healthcheck_test"
                test_file.touch()
                test_file.unlink()
            except PermissionError:
                print(f"Directory is not writable: {directory}")
                return False

        return True
    except Exception as e:
        print(f"Directory check failed: {e}")
        return False


def check_jupyter_service():
    """檢查 Jupyter 服務是否運行"""
    try:
        import socket

        # 檢查 Jupyter Lab 端口是否監聽
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("localhost", 8888))
        sock.close()

        if result == 0:
            return True
        else:
            # 如果 Jupyter 沒有運行，這可能是正常的（取決於啟動命令）
            # 所以我們只是警告而不是失敗
            print("Jupyter service is not listening on port 8888 (this may be normal)")
            return True
    except Exception as e:
        print(f"Jupyter service check warning: {e}")
        # 不將此作為失敗條件
        return True


def check_external_services():
    """檢查外部服務連接（可選）"""
    try:
        import urllib.request
        import urllib.error

        # 檢查 ChromaDB 連接（如果配置了）
        chromadb_host = os.getenv("CHROMADB_HOST")
        chromadb_port = os.getenv("CHROMADB_PORT", "8000")

        if chromadb_host:
            try:
                url = f"http://{chromadb_host}:{chromadb_port}/api/v1/heartbeat"
                req = urllib.request.Request(url, method="GET")
                urllib.request.urlopen(req, timeout=5)
            except urllib.error.URLError:
                print(f"ChromaDB is not accessible at {chromadb_host}:{chromadb_port}")
                # 不將此作為失敗條件，因為服務可能在獨立容器中
                pass

        # 檢查 Ollama 連接（如果配置了）
        ollama_host = os.getenv("OLLAMA_HOST")

        if ollama_host:
            try:
                url = f"{ollama_host}/api/tags"
                req = urllib.request.Request(url, method="GET")
                urllib.request.urlopen(req, timeout=5)
            except urllib.error.URLError:
                print(f"Ollama is not accessible at {ollama_host}")
                # 不將此作為失敗條件
                pass

        return True
    except Exception as e:
        print(f"External services check warning: {e}")
        # 不將此作為失敗條件
        return True


def main():
    """主健康檢查函數"""
    print("Running health check...")

    checks = [
        ("Python Environment", check_python_environment),
        ("Directories", check_directories),
        ("Jupyter Service", check_jupyter_service),
        ("External Services", check_external_services),
    ]

    all_passed = True

    for name, check_func in checks:
        try:
            result = check_func()
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {name}")

            if not result:
                all_passed = False
        except Exception as e:
            print(f"✗ ERROR: {name} - {e}")
            all_passed = False

    if all_passed:
        print("\n✓ Health check passed")
        sys.exit(0)
    else:
        print("\n✗ Health check failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
