#!/usr/bin/env python3
"""
銷售外展自動化專案 - 自動化設置腳本
========================================

此腳本會自動完成以下任務：
1. 檢查系統環境和 Python 版本
2. 克隆原始專案倉庫
3. 創建 Python 虛擬環境
4. 安裝所有依賴套件（包括 html2text）
5. 生成配置文件模板
6. 提供後續配置指南

作者：LLM Agent Demo
版本：2.0
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

# ANSI 顏色代碼（用於美化輸出）
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(message):
    """打印標題"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message:^70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_success(message):
    """打印成功消息"""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_warning(message):
    """打印警告消息"""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def print_error(message):
    """打印錯誤消息"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_info(message):
    """打印信息消息"""
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")

def print_step(step_num, total_steps, message):
    """打印步驟信息"""
    print(f"\n{Colors.OKBLUE}{Colors.BOLD}[步驟 {step_num}/{total_steps}] {message}{Colors.ENDC}")

def run_command(command, description="", show_output=True):
    """
    執行 shell 命令並處理輸出

    Args:
        command: 要執行的命令
        description: 命令描述
        show_output: 是否顯示命令輸出

    Returns:
        bool: 命令是否成功執行
    """
    if description:
        print_info(f"{description}...")

    try:
        if show_output:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                text=True
            )
        else:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )

        if result.returncode == 0:
            if description:
                print_success(f"{description} - 完成")
            return True
    except subprocess.CalledProcessError as e:
        print_error(f"命令執行失敗: {command}")
        if e.stderr:
            print_error(f"錯誤信息: {e.stderr}")
        return False
    except Exception as e:
        print_error(f"未預期的錯誤: {str(e)}")
        return False

def check_python_version():
    """檢查 Python 版本"""
    print_step(1, 8, "檢查 Python 版本")

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    print_info(f"檢測到 Python 版本: {version_str}")

    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print_error("Python 版本過低！需要 Python 3.9 或更高版本")
        print_info("請訪問 https://www.python.org/downloads/ 下載最新版本")
        return False

    print_success(f"Python 版本符合要求 (>= 3.9)")
    return True

def check_git_installed():
    """檢查 Git 是否安裝"""
    print_info("檢查 Git 是否安裝...")

    try:
        result = subprocess.run(
            "git --version",
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        print_success(f"Git 已安裝: {result.stdout.strip()}")
        return True
    except:
        print_error("Git 未安裝或未添加到 PATH")
        print_info("請訪問 https://git-scm.com/downloads 安裝 Git")
        return False

def check_internet_connection():
    """檢查網絡連接"""
    print_info("檢查網絡連接...")

    try:
        import urllib.request
        urllib.request.urlopen('https://www.google.com', timeout=5)
        print_success("網絡連接正常")
        return True
    except:
        print_warning("無法連接到互聯網，可能影響專案克隆和依賴安裝")
        response = input("是否繼續？(y/n): ")
        return response.lower() == 'y'

def clone_repository():
    """克隆專案倉庫"""
    print_step(2, 8, "克隆專案倉庫")

    repo_url = "https://github.com/kaymen99/sales-outreach-automation-langgraph.git"
    repo_dir = "sales-outreach-automation-langgraph"

    if os.path.exists(repo_dir):
        print_warning(f"目錄 '{repo_dir}' 已存在")

        # 檢查是否是 git 倉庫
        if os.path.exists(os.path.join(repo_dir, ".git")):
            print_info("檢測到現有的 Git 倉庫")
            response = input("是否更新倉庫？(y/n): ")

            if response.lower() == 'y':
                os.chdir(repo_dir)
                if run_command("git pull", "更新倉庫", show_output=False):
                    os.chdir("..")
                    return True
                else:
                    os.chdir("..")
                    print_warning("倉庫更新失敗，將使用現有版本")
                    return True
            else:
                print_info("跳過倉庫更新，使用現有版本")
                return True
        else:
            print_error(f"目錄 '{repo_dir}' 存在但不是 Git 倉庫")
            response = input("是否刪除並重新克隆？(y/n): ")

            if response.lower() == 'y':
                try:
                    shutil.rmtree(repo_dir)
                    print_success("舊目錄已刪除")
                except Exception as e:
                    print_error(f"刪除目錄失敗: {str(e)}")
                    return False
            else:
                print_warning("保留現有目錄，但可能影響後續步驟")
                return True

    print_info(f"正在克隆倉庫: {repo_url}")
    if run_command(f"git clone {repo_url}", "克隆倉庫", show_output=False):
        print_success("倉庫克隆成功")
        return True
    else:
        print_error("倉庫克隆失敗")
        return False

def create_virtual_environment():
    """創建 Python 虛擬環境"""
    print_step(3, 8, "創建 Python 虛擬環境")

    repo_dir = "sales-outreach-automation-langgraph"
    venv_dir = os.path.join(repo_dir, "venv")

    if os.path.exists(venv_dir):
        print_warning("虛擬環境已存在")
        response = input("是否刪除並重新創建？(y/n): ")

        if response.lower() == 'y':
            try:
                shutil.rmtree(venv_dir)
                print_success("舊虛擬環境已刪除")
            except Exception as e:
                print_error(f"刪除虛擬環境失敗: {str(e)}")
                return False
        else:
            print_info("使用現有虛擬環境")
            return True

    os.chdir(repo_dir)

    if run_command("python -m venv venv", "創建虛擬環境", show_output=False):
        print_success("虛擬環境創建成功")
        os.chdir("..")
        return True
    else:
        print_error("虛擬環境創建失敗")
        os.chdir("..")
        return False

def get_pip_path():
    """獲取虛擬環境中的 pip 路徑"""
    system = platform.system()

    if system == "Windows":
        return "sales-outreach-automation-langgraph\\venv\\Scripts\\pip.exe"
    else:
        return "sales-outreach-automation-langgraph/venv/bin/pip"

def install_dependencies():
    """安裝項目依賴"""
    print_step(4, 8, "安裝專案依賴")

    pip_path = get_pip_path()
    repo_dir = "sales-outreach-automation-langgraph"
    requirements_file = os.path.join(repo_dir, "requirements.txt")

    if not os.path.exists(requirements_file):
        print_warning(f"找不到 requirements.txt 文件")
        print_info("跳過依賴安裝")
        return True

    # 升級 pip
    print_info("升級 pip...")
    run_command(f"{pip_path} install --upgrade pip", show_output=False)

    # 安裝依賴
    print_info("安裝專案依賴（這可能需要幾分鐘）...")
    if not run_command(f"{pip_path} install -r {requirements_file}", show_output=False):
        print_error("依賴安裝失敗")
        return False

    print_success("專案依賴安裝完成")

    # 安裝額外的依賴 html2text
    print_step(5, 8, "安裝額外依賴")
    print_info("安裝 html2text...")

    if run_command(f"{pip_path} install html2text", show_output=False):
        print_success("html2text 安裝完成")
        return True
    else:
        print_error("html2text 安裝失敗")
        return False

def setup_environment_file():
    """設置環境變數文件"""
    print_step(6, 8, "設置環境變數文件")

    repo_dir = "sales-outreach-automation-langgraph"
    env_example = os.path.join(repo_dir, ".env.example")
    env_file = os.path.join(repo_dir, ".env")

    if os.path.exists(env_file):
        print_warning(".env 文件已存在")
        response = input("是否覆蓋？(y/n): ")

        if response.lower() != 'y':
            print_info("保留現有 .env 文件")
            return True

    if os.path.exists(env_example):
        try:
            shutil.copy(env_example, env_file)
            print_success(".env 文件已從 .env.example 創建")
            print_warning("請記得編輯 .env 文件並填入你的 API 金鑰！")
            return True
        except Exception as e:
            print_error(f"創建 .env 文件失敗: {str(e)}")
            return False
    else:
        print_warning("未找到 .env.example 文件")
        print_info("你需要手動創建 .env 文件")
        return True

def create_docs_directory():
    """創建文檔目錄"""
    print_step(7, 8, "創建文檔目錄結構")

    docs_dir = "docs"
    examples_dir = "examples"

    try:
        os.makedirs(docs_dir, exist_ok=True)
        print_success(f"'{docs_dir}/' 目錄已創建")

        os.makedirs(examples_dir, exist_ok=True)
        print_success(f"'{examples_dir}/' 目錄已創建")

        return True
    except Exception as e:
        print_error(f"創建目錄失敗: {str(e)}")
        return False

def print_next_steps():
    """打印後續步驟"""
    print_step(8, 8, "設置完成")

    system = platform.system()

    print_header("🎉 設置成功完成！")

    print(f"{Colors.BOLD}後續步驟：{Colors.ENDC}\n")

    print(f"{Colors.OKCYAN}1. 啟動虛擬環境：{Colors.ENDC}")
    if system == "Windows":
        print(f"   {Colors.BOLD}cd sales-outreach-automation-langgraph{Colors.ENDC}")
        print(f"   {Colors.BOLD}venv\\Scripts\\activate{Colors.ENDC}\n")
    else:
        print(f"   {Colors.BOLD}cd sales-outreach-automation-langgraph{Colors.ENDC}")
        print(f"   {Colors.BOLD}source venv/bin/activate{Colors.ENDC}\n")

    print(f"{Colors.OKCYAN}2. 配置 API 金鑰：{Colors.ENDC}")
    print(f"   編輯 {Colors.BOLD}.env{Colors.ENDC} 文件，填入你的 API 金鑰")
    print(f"   詳細說明請參考: {Colors.BOLD}../docs/config-guide.md{Colors.ENDC}\n")

    print(f"{Colors.OKCYAN}3. 設置 Google API 憑證：{Colors.ENDC}")
    print(f"   - 訪問 {Colors.UNDERLINE}https://developers.google.com/gmail/api/quickstart/python{Colors.ENDC}")
    print(f"   - 下載 {Colors.BOLD}credentials.json{Colors.ENDC} 並放到專案根目錄\n")

    print(f"{Colors.OKCYAN}4. 配置 CRM（選擇其中一個）：{Colors.ENDC}")
    print(f"   - Airtable: https://airtable.com/create/tokens")
    print(f"   - HubSpot: https://developers.hubspot.com/")
    print(f"   - Google Sheets: 在 .env 中設置 SHEET_ID\n")

    print(f"{Colors.OKCYAN}5. 運行專案：{Colors.ENDC}")
    print(f"   {Colors.BOLD}python main.py{Colors.ENDC}\n")

    print(f"{Colors.WARNING}重要提醒：{Colors.ENDC}")
    print(f"   - 確保所有必需的 API 金鑰都已配置")
    print(f"   - 首次運行時會要求授權 Gmail API 訪問權限")
    print(f"   - 如使用 Airtable，記得在表格中添加 'status' 欄位\n")

    print(f"{Colors.OKGREEN}需要幫助？{Colors.ENDC}")
    print(f"   - 查看 README.md 獲取完整文檔")
    print(f"   - 查看 docs/troubleshooting.md 解決常見問題")
    print(f"   - 查看 examples/ 目錄獲取使用示例\n")

def verify_setup():
    """驗證設置"""
    print_info("驗證設置...")

    repo_dir = "sales-outreach-automation-langgraph"

    checks = [
        (os.path.exists(repo_dir), "專案目錄存在"),
        (os.path.exists(os.path.join(repo_dir, "venv")), "虛擬環境存在"),
        (os.path.exists(os.path.join(repo_dir, "main.py")), "主程式文件存在"),
        (os.path.exists(os.path.join(repo_dir, ".env")), ".env 配置文件存在"),
    ]

    all_passed = True
    for check, description in checks:
        if check:
            print_success(description)
        else:
            print_error(f"{description} - 失敗")
            all_passed = False

    return all_passed

def main():
    """主函數"""
    print_header("銷售外展自動化專案 - 自動化設置")

    print_info(f"作業系統: {platform.system()} {platform.release()}")
    print_info(f"Python 版本: {sys.version.split()[0]}")
    print_info(f"當前目錄: {os.getcwd()}\n")

    # 步驟 1: 檢查 Python 版本
    if not check_python_version():
        sys.exit(1)

    # 檢查 Git
    if not check_git_installed():
        sys.exit(1)

    # 檢查網絡連接
    if not check_internet_connection():
        print_warning("網絡連接有問題，設置可能失敗")

    # 步驟 2: 克隆倉庫
    if not clone_repository():
        print_error("專案設置失敗於：克隆倉庫")
        sys.exit(1)

    # 步驟 3: 創建虛擬環境
    if not create_virtual_environment():
        print_error("專案設置失敗於：創建虛擬環境")
        sys.exit(1)

    # 步驟 4-5: 安裝依賴
    if not install_dependencies():
        print_error("專案設置失敗於：安裝依賴")
        sys.exit(1)

    # 步驟 6: 設置環境變數
    if not setup_environment_file():
        print_warning("環境變數文件設置有問題，可能需要手動配置")

    # 步驟 7: 創建文檔目錄
    if not create_docs_directory():
        print_warning("文檔目錄創建失敗，但不影響專案運行")

    # 驗證設置
    if not verify_setup():
        print_warning("部分檢查未通過，請檢查上述錯誤")

    # 步驟 8: 打印後續步驟
    print_next_steps()

    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_warning("\n\n設置被用戶中斷")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\n未預期的錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
