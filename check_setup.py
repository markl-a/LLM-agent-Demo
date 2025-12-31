#!/usr/bin/env python3
"""
LLM-Agent-Demo 環境診斷腳本

快速檢查您的開發環境是否正確配置。
運行方式: python check_setup.py

作者: LLM-Agent-Demo Team
更新日期: 2025-12-31
"""

import sys
import os
import subprocess
import importlib.util
from pathlib import Path

# 顏色輸出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """打印標題"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(text: str):
    """打印成功信息"""
    print(f"  {Colors.GREEN}✓{Colors.RESET} {text}")

def print_error(text: str):
    """打印錯誤信息"""
    print(f"  {Colors.RED}✗{Colors.RESET} {text}")

def print_warning(text: str):
    """打印警告信息"""
    print(f"  {Colors.YELLOW}⚠{Colors.RESET} {text}")

def print_info(text: str):
    """打印信息"""
    print(f"  {Colors.BLUE}ℹ{Colors.RESET} {text}")

def check_python_version() -> bool:
    """檢查 Python 版本"""
    print_header("1. Python 版本檢查")

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    if version.major == 3 and version.minor >= 9:
        print_success(f"Python 版本: {version_str}")
        if version.minor >= 11:
            print_info("推薦版本，性能最佳！")
        return True
    else:
        print_error(f"Python 版本: {version_str}")
        print_error("需要 Python 3.9 或更高版本")
        return False

def check_virtual_env() -> bool:
    """檢查虛擬環境"""
    print_header("2. 虛擬環境檢查")

    in_venv = sys.prefix != sys.base_prefix
    venv_path = os.environ.get('VIRTUAL_ENV', '')
    conda_env = os.environ.get('CONDA_DEFAULT_ENV', '')

    if in_venv:
        print_success("正在使用虛擬環境")
        print_info(f"路徑: {sys.prefix}")
        return True
    elif conda_env:
        print_success(f"正在使用 Conda 環境: {conda_env}")
        return True
    else:
        print_warning("未檢測到虛擬環境")
        print_info("建議創建虛擬環境:")
        print_info("  python -m venv venv")
        print_info("  source venv/bin/activate  # Linux/Mac")
        print_info("  .\\venv\\Scripts\\activate  # Windows")
        return False

def check_core_packages() -> dict:
    """檢查核心依賴包"""
    print_header("3. 核心依賴檢查")

    packages = {
        'openai': '1.50.0',
        'anthropic': '0.37.0',
        'langchain': '0.3.0',
        'python-dotenv': '1.0.0',
        'pydantic': '2.0.0',
        'rich': '13.0.0',
        'httpx': '0.25.0',
    }

    results = {}
    for package, min_version in packages.items():
        try:
            spec = importlib.util.find_spec(package.replace('-', '_'))
            if spec:
                try:
                    mod = importlib.import_module(package.replace('-', '_'))
                    version = getattr(mod, '__version__', 'unknown')
                    print_success(f"{package}: {version}")
                    results[package] = True
                except:
                    print_success(f"{package}: 已安裝")
                    results[package] = True
            else:
                print_warning(f"{package}: 未安裝 (建議 >= {min_version})")
                results[package] = False
        except:
            print_warning(f"{package}: 未安裝 (建議 >= {min_version})")
            results[package] = False

    return results

def check_api_keys() -> dict:
    """檢查 API 密鑰"""
    print_header("4. API 密鑰檢查")

    # 嘗試加載 .env 文件
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print_warning("python-dotenv 未安裝，無法加載 .env 文件")

    api_keys = {
        'OPENAI_API_KEY': 'OpenAI (GPT-4, GPT-3.5)',
        'ANTHROPIC_API_KEY': 'Anthropic (Claude)',
        'GOOGLE_API_KEY': 'Google (Gemini)',
        'GROQ_API_KEY': 'Groq (快速推理)',
        'COHERE_API_KEY': 'Cohere',
    }

    results = {}
    for key, description in api_keys.items():
        value = os.environ.get(key, '')
        if value:
            # 隱藏部分密鑰
            masked = value[:8] + '...' + value[-4:] if len(value) > 12 else '***'
            print_success(f"{key}: {masked} ({description})")
            results[key] = True
        else:
            print_warning(f"{key}: 未設置 ({description})")
            results[key] = False

    if not any(results.values()):
        print_info("\n提示: 創建 .env 文件並添加 API 密鑰:")
        print_info("  echo 'OPENAI_API_KEY=sk-xxx...' > .env")

    return results

def check_env_file() -> bool:
    """檢查 .env 文件"""
    print_header("5. 配置文件檢查")

    env_file = Path('.env')
    env_example = Path('.env.example')

    if env_file.exists():
        print_success(".env 文件存在")
        # 計算配置項數量
        with open(env_file) as f:
            lines = [l for l in f.readlines() if l.strip() and not l.startswith('#')]
            print_info(f"已配置 {len(lines)} 個環境變量")
        return True
    else:
        print_warning(".env 文件不存在")
        if env_example.exists():
            print_info("可以從 .env.example 複製:")
            print_info("  cp .env.example .env")
        return False

def check_network() -> bool:
    """檢查網絡連接"""
    print_header("6. 網絡連接檢查")

    import urllib.request
    import urllib.error

    endpoints = [
        ('https://api.openai.com', 'OpenAI API'),
        ('https://api.anthropic.com', 'Anthropic API'),
        ('https://huggingface.co', 'HuggingFace'),
    ]

    all_ok = True
    for url, name in endpoints:
        try:
            req = urllib.request.Request(url, method='HEAD')
            req.add_header('User-Agent', 'LLM-Agent-Demo/1.0')
            urllib.request.urlopen(req, timeout=5)
            print_success(f"{name}: 可連接")
        except urllib.error.URLError as e:
            print_warning(f"{name}: 連接失敗 ({e.reason})")
            all_ok = False
        except Exception as e:
            print_warning(f"{name}: 連接超時或錯誤")
            all_ok = False

    if not all_ok:
        print_info("\n如需使用代理:")
        print_info("  export HTTPS_PROXY=http://127.0.0.1:7890")

    return all_ok

def check_gpu() -> bool:
    """檢查 GPU 可用性"""
    print_header("7. GPU 檢查 (可選)")

    try:
        import torch
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print_success(f"CUDA 可用: {device_name}")
            print_info(f"顯存: {memory:.1f} GB")
            return True
        else:
            print_warning("CUDA 不可用")
            print_info("大多數示例使用 API 調用，不需要 GPU")
            return False
    except ImportError:
        print_warning("PyTorch 未安裝")
        print_info("如需本地模型運行，請安裝 PyTorch:")
        print_info("  pip install torch")
        return False

def quick_api_test() -> bool:
    """快速 API 測試"""
    print_header("8. 快速 API 測試")

    api_key = os.environ.get('OPENAI_API_KEY', '')
    if not api_key:
        print_warning("跳過 API 測試 (未設置 OPENAI_API_KEY)")
        return False

    try:
        from openai import OpenAI
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'Hello' in one word"}],
            max_tokens=10
        )
        result = response.choices[0].message.content
        print_success(f"OpenAI API 正常: {result}")
        return True
    except ImportError:
        print_warning("openai 包未安裝")
        return False
    except Exception as e:
        print_error(f"API 調用失敗: {str(e)[:50]}")
        return False

def print_summary(results: dict):
    """打印總結"""
    print_header("診斷總結")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"  通過檢查: {passed}/{total}")
    print()

    if passed == total:
        print(f"  {Colors.GREEN}{Colors.BOLD}🎉 環境配置完美！可以開始學習了！{Colors.RESET}")
    elif passed >= total * 0.7:
        print(f"  {Colors.YELLOW}{Colors.BOLD}⚡ 基本配置完成，部分功能可能受限{Colors.RESET}")
    else:
        print(f"  {Colors.RED}{Colors.BOLD}⚠️  請根據上述提示完成環境配置{Colors.RESET}")

    print()
    print_info("下一步:")
    print_info("  1. 閱讀 QUICKSTART.md 快速開始指南")
    print_info("  2. 運行第一個示例: python 16.OpenAI\\ Swarm/01_*.py")
    print_info("  3. 查看 FAQ.md 獲取幫助")

def main():
    """主函數"""
    print(f"\n{Colors.BOLD}LLM-Agent-Demo 環境診斷工具{Colors.RESET}")
    print(f"{'='*40}\n")

    results = {}

    # 執行各項檢查
    results['python'] = check_python_version()
    results['venv'] = check_virtual_env()
    pkg_results = check_core_packages()
    results['packages'] = sum(pkg_results.values()) >= len(pkg_results) * 0.5
    api_results = check_api_keys()
    results['api_keys'] = any(api_results.values())
    results['env_file'] = check_env_file()
    results['network'] = check_network()
    results['gpu'] = check_gpu()
    results['api_test'] = quick_api_test()

    # 打印總結
    print_summary(results)

if __name__ == "__main__":
    main()
