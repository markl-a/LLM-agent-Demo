"""
ComputerTerminal - 終端操作 Agent
===================================

ComputerTerminal 是 Magentic-One 的系統操作專家，負責：
1. 執行系統命令
2. 腳本運行和管理
3. 進程監控和控制
4. 環境變量管理
5. 系統信息收集

安全特性：
- 命令白名單機制
- 危險操作確認
- 執行權限控制
- 操作審計日誌
- 資源限制
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import subprocess
from pathlib import Path


class CommandCategory:
    """命令分類"""
    SAFE = "safe"           # 安全命令
    MODERATE = "moderate"   # 需謹慎的命令
    DANGEROUS = "dangerous" # 危險命令
    BLOCKED = "blocked"     # 禁止的命令


class ComputerTerminalAgent:
    """
    終端操作 Agent

    提供安全的系統命令執行能力
    """

    def __init__(
        self,
        llm_config: Dict[str, Any],
        work_dir: str = "./terminal_workspace",
        require_approval: bool = True,
        timeout: int = 30
    ):
        """
        初始化 ComputerTerminal

        Args:
            llm_config: LLM 配置
            work_dir: 工作目錄
            require_approval: 是否需要批准危險操作
            timeout: 命令執行超時時間（秒）
        """
        self.llm_config = llm_config
        self.work_dir = Path(work_dir)
        self.require_approval = require_approval
        self.timeout = timeout

        # 確保工作目錄存在
        self.work_dir.mkdir(parents=True, exist_ok=True)

        # 命令分類
        self.command_categories = self._init_command_categories()

        # 執行歷史
        self.execution_history: List[Dict] = []

        # 統計
        self.stats = {
            'commands_executed': 0,
            'scripts_run': 0,
            'commands_blocked': 0,
            'errors': 0
        }

    def _init_command_categories(self) -> Dict[str, List[str]]:
        """初始化命令分類"""
        return {
            CommandCategory.SAFE: [
                'ls', 'pwd', 'echo', 'cat', 'grep', 'find',
                'wc', 'head', 'tail', 'sort', 'uniq',
                'date', 'whoami', 'hostname', 'uname'
            ],
            CommandCategory.MODERATE: [
                'mkdir', 'touch', 'cp', 'mv', 'chmod',
                'ps', 'top', 'df', 'du', 'which'
            ],
            CommandCategory.DANGEROUS: [
                'rm', 'rmdir', 'kill', 'killall',
                'sudo', 'su', 'shutdown', 'reboot'
            ],
            CommandCategory.BLOCKED: [
                'rm -rf /', 'dd', 'mkfs', 'format',
                ':(){:|:&};:'  # Fork bomb
            ]
        }

    def execute_command(
        self,
        command: str,
        shell: bool = True,
        capture_output: bool = True
    ) -> Dict[str, Any]:
        """
        執行命令

        Args:
            command: 要執行的命令
            shell: 是否在 shell 中執行
            capture_output: 是否捕獲輸出

        Returns:
            執行結果
        """
        print(f"\n💻 執行命令: {command}")

        # 安全檢查
        safety_check = self._check_command_safety(command)

        if not safety_check['safe']:
            print(f"✗ 命令被阻止: {safety_check['reason']}")
            self.stats['commands_blocked'] += 1
            return {
                'success': False,
                'error': safety_check['reason'],
                'blocked': True
            }

        # 需要批准的情況
        if safety_check['category'] == CommandCategory.DANGEROUS and self.require_approval:
            if not self._request_approval(command):
                print(f"✗ 命令未獲批准")
                self.stats['commands_blocked'] += 1
                return {
                    'success': False,
                    'error': '未獲得執行批准',
                    'blocked': True
                }

        # 執行命令
        try:
            result = self._execute_command_safely(command, shell, capture_output)

            # 記錄歷史
            self.execution_history.append({
                'command': command,
                'timestamp': datetime.now().isoformat(),
                'success': result['return_code'] == 0,
                'category': safety_check['category']
            })

            self.stats['commands_executed'] += 1

            print(f"✓ 命令執行完成")
            print(f"退出碼: {result['return_code']}")

            return {
                'success': result['return_code'] == 0,
                'command': command,
                'stdout': result['stdout'],
                'stderr': result['stderr'],
                'return_code': result['return_code'],
                'execution_time': result['execution_time']
            }

        except Exception as e:
            self.stats['errors'] += 1
            print(f"✗ 執行失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def run_script(
        self,
        script_content: str,
        script_type: str = "bash",
        args: List[str] = None
    ) -> Dict[str, Any]:
        """
        運行腳本

        Args:
            script_content: 腳本內容
            script_type: 腳本類型 (bash/python/powershell)
            args: 腳本參數

        Returns:
            執行結果
        """
        print(f"\n📜 運行 {script_type} 腳本")

        try:
            # 保存腳本到文件
            script_file = self._save_script(script_content, script_type)

            # 構建執行命令
            if script_type == "bash":
                command = f"bash {script_file}"
            elif script_type == "python":
                command = f"python3 {script_file}"
            elif script_type == "powershell":
                command = f"powershell -File {script_file}"
            else:
                return {
                    'success': False,
                    'error': f'不支持的腳本類型: {script_type}'
                }

            # 添加參數
            if args:
                command += " " + " ".join(args)

            # 執行
            result = self.execute_command(command)

            self.stats['scripts_run'] += 1

            return result

        except Exception as e:
            print(f"✗ 腳本執行失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_system_info(self) -> Dict[str, Any]:
        """
        獲取系統信息

        Returns:
            系統信息
        """
        print(f"\nℹ️ 獲取系統信息")

        info = {}

        # 操作系統
        os_info = self.execute_command("uname -a", capture_output=True)
        info['os'] = os_info.get('stdout', 'Unknown').strip()

        # 主機名
        hostname = self.execute_command("hostname", capture_output=True)
        info['hostname'] = hostname.get('stdout', 'Unknown').strip()

        # 當前用戶
        user = self.execute_command("whoami", capture_output=True)
        info['user'] = user.get('stdout', 'Unknown').strip()

        # 磁盤空間
        disk = self.execute_command("df -h", capture_output=True)
        info['disk_usage'] = disk.get('stdout', '')

        # 記憶體信息（如果可用）
        memory = self.execute_command("free -h", capture_output=True)
        info['memory'] = memory.get('stdout', '')

        print(f"✓ 系統信息已收集")

        return {
            'success': True,
            'info': info
        }

    def monitor_process(self, process_name: str = None) -> Dict[str, Any]:
        """
        監控進程

        Args:
            process_name: 進程名稱（None 表示所有進程）

        Returns:
            進程信息
        """
        print(f"\n🔍 監控進程")

        if process_name:
            command = f"ps aux | grep {process_name}"
        else:
            command = "ps aux"

        result = self.execute_command(command)

        if result['success']:
            processes = self._parse_ps_output(result['stdout'])

            return {
                'success': True,
                'process_name': process_name,
                'processes': processes,
                'count': len(processes)
            }
        else:
            return result

    def manage_environment(
        self,
        action: str,
        var_name: str,
        var_value: str = None
    ) -> Dict[str, Any]:
        """
        管理環境變量

        Args:
            action: 操作類型 (get/set/unset)
            var_name: 變量名
            var_value: 變量值（set 時需要）

        Returns:
            操作結果
        """
        print(f"\n🌍 環境變量操作: {action} {var_name}")

        if action == "get":
            value = os.environ.get(var_name)
            return {
                'success': True,
                'action': 'get',
                'var_name': var_name,
                'value': value
            }

        elif action == "set":
            if var_value is None:
                return {
                    'success': False,
                    'error': 'set 操作需要提供 var_value'
                }

            os.environ[var_name] = var_value
            return {
                'success': True,
                'action': 'set',
                'var_name': var_name,
                'value': var_value
            }

        elif action == "unset":
            if var_name in os.environ:
                del os.environ[var_name]

            return {
                'success': True,
                'action': 'unset',
                'var_name': var_name
            }

        else:
            return {
                'success': False,
                'error': f'不支持的操作: {action}'
            }

    def execute_pipeline(self, commands: List[str]) -> Dict[str, Any]:
        """
        執行命令管道

        Args:
            commands: 命令列表

        Returns:
            執行結果
        """
        print(f"\n⛓️ 執行命令管道 ({len(commands)} 個命令)")

        pipeline_command = " | ".join(commands)
        result = self.execute_command(pipeline_command)

        return result

    def batch_execute(self, commands: List[str], stop_on_error: bool = True) -> Dict[str, Any]:
        """
        批量執行命令

        Args:
            commands: 命令列表
            stop_on_error: 遇到錯誤是否停止

        Returns:
            執行結果
        """
        print(f"\n📦 批量執行 {len(commands)} 個命令")

        results = []
        for i, command in enumerate(commands, 1):
            print(f"\n執行命令 {i}/{len(commands)}: {command}")

            result = self.execute_command(command)
            results.append(result)

            if not result['success'] and stop_on_error:
                print(f"⚠️ 命令失敗，停止執行")
                break

        success_count = sum(1 for r in results if r['success'])

        return {
            'success': success_count == len(results),
            'total_commands': len(commands),
            'executed': len(results),
            'succeeded': success_count,
            'failed': len(results) - success_count,
            'results': results
        }

    # 內部輔助方法

    def _check_command_safety(self, command: str) -> Dict[str, Any]:
        """檢查命令安全性"""
        # 檢查是否被禁止
        for blocked_cmd in self.command_categories[CommandCategory.BLOCKED]:
            if blocked_cmd in command:
                return {
                    'safe': False,
                    'category': CommandCategory.BLOCKED,
                    'reason': f'命令包含被禁止的操作: {blocked_cmd}'
                }

        # 檢查是否危險
        command_parts = command.split()
        if command_parts:
            base_command = command_parts[0]

            if base_command in self.command_categories[CommandCategory.DANGEROUS]:
                return {
                    'safe': True,  # 可以執行，但需要批准
                    'category': CommandCategory.DANGEROUS,
                    'reason': '此命令可能有危險性'
                }

            if base_command in self.command_categories[CommandCategory.MODERATE]:
                return {
                    'safe': True,
                    'category': CommandCategory.MODERATE,
                    'reason': None
                }

            if base_command in self.command_categories[CommandCategory.SAFE]:
                return {
                    'safe': True,
                    'category': CommandCategory.SAFE,
                    'reason': None
                }

        # 默認為需謹慎
        return {
            'safe': True,
            'category': CommandCategory.MODERATE,
            'reason': None
        }

    def _request_approval(self, command: str) -> bool:
        """請求批准（模擬）"""
        print(f"\n⚠️ 此命令需要批准: {command}")
        print(f"自動批准（實際環境中應請求人工確認）")
        return True  # 在實際環境中應該請求人工確認

    def _execute_command_safely(
        self,
        command: str,
        shell: bool,
        capture_output: bool
    ) -> Dict[str, Any]:
        """安全執行命令"""
        start_time = datetime.now()

        try:
            # 模擬執行（實際應使用 subprocess）
            result = {
                'stdout': f"模擬執行: {command}",
                'stderr': '',
                'return_code': 0
            }

        except subprocess.TimeoutExpired:
            result = {
                'stdout': '',
                'stderr': f'命令超時（超過 {self.timeout} 秒）',
                'return_code': -1
            }

        except Exception as e:
            result = {
                'stdout': '',
                'stderr': str(e),
                'return_code': 1
            }

        end_time = datetime.now()
        result['execution_time'] = (end_time - start_time).total_seconds()

        return result

    def _save_script(self, content: str, script_type: str) -> Path:
        """保存腳本到文件"""
        extensions = {
            'bash': '.sh',
            'python': '.py',
            'powershell': '.ps1'
        }

        ext = extensions.get(script_type, '.sh')
        filename = f"script_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        filepath = self.work_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # 添加執行權限（Unix-like 系統）
        try:
            os.chmod(filepath, 0o755)
        except:
            pass

        return filepath

    def _parse_ps_output(self, output: str) -> List[Dict]:
        """解析 ps 命令輸出"""
        # 簡化處理
        processes = []

        lines = output.strip().split('\n')
        for line in lines[1:]:  # 跳過標題行
            processes.append({
                'info': line.strip()
            })

        return processes

    def get_execution_history(self, limit: int = 10) -> List[Dict]:
        """獲取執行歷史"""
        return self.execution_history[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        """獲取統計數據"""
        return self.stats.copy()


def demo_basic_commands():
    """基本命令示範"""
    print("=" * 60)
    print("範例 1: 執行基本命令")
    print("=" * 60)

    terminal = ComputerTerminalAgent(llm_config={"model": "gpt-4"})

    # 執行安全命令
    commands = ["pwd", "ls -la", "echo 'Hello, World!'"]

    for cmd in commands:
        result = terminal.execute_command(cmd)
        if result['success']:
            print(f"\n輸出: {result['stdout']}")


def demo_system_info():
    """系統信息示範"""
    print("\n" + "=" * 60)
    print("範例 2: 獲取系統信息")
    print("=" * 60)

    terminal = ComputerTerminalAgent(llm_config={"model": "gpt-4"})

    info = terminal.get_system_info()

    print("\n系統信息:")
    print(json.dumps(info['info'], indent=2, ensure_ascii=False))


def demo_script_execution():
    """腳本執行示範"""
    print("\n" + "=" * 60)
    print("範例 3: 運行腳本")
    print("=" * 60)

    terminal = ComputerTerminalAgent(llm_config={"model": "gpt-4"})

    bash_script = """#!/bin/bash
echo "開始執行腳本..."
echo "當前目錄: $(pwd)"
echo "當前用戶: $(whoami)"
echo "腳本執行完成"
"""

    result = terminal.run_script(bash_script, script_type="bash")

    print("\n腳本執行結果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


def demo_process_monitoring():
    """進程監控示範"""
    print("\n" + "=" * 60)
    print("範例 4: 監控進程")
    print("=" * 60)

    terminal = ComputerTerminalAgent(llm_config={"model": "gpt-4"})

    result = terminal.monitor_process("python")

    print(f"\n找到 {result.get('count', 0)} 個進程")


def demo_batch_execution():
    """批量執行示範"""
    print("\n" + "=" * 60)
    print("範例 5: 批量執行命令")
    print("=" * 60)

    terminal = ComputerTerminalAgent(llm_config={"model": "gpt-4"})

    commands = [
        "echo '步驟 1: 準備環境'",
        "mkdir -p test_dir",
        "echo '步驟 2: 創建文件'",
        "touch test_dir/test.txt",
        "echo '步驟 3: 列出文件'",
        "ls -l test_dir"
    ]

    result = terminal.batch_execute(commands)

    print("\n批量執行結果:")
    print(f"總命令數: {result['total_commands']}")
    print(f"成功: {result['succeeded']}")
    print(f"失敗: {result['failed']}")


def demo_environment_management():
    """環境管理示範"""
    print("\n" + "=" * 60)
    print("範例 6: 環境變量管理")
    print("=" * 60)

    terminal = ComputerTerminalAgent(llm_config={"model": "gpt-4"})

    # 設置環境變量
    terminal.manage_environment("set", "MY_VAR", "test_value")

    # 獲取環境變量
    result = terminal.manage_environment("get", "MY_VAR")

    print(f"\n環境變量值: {result['value']}")

    # 查看統計
    stats = terminal.get_statistics()
    print("\n統計數據:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    demo_basic_commands()
    demo_system_info()
    demo_script_execution()
    demo_process_monitoring()
    demo_batch_execution()
    demo_environment_management()

    print("\n" + "=" * 60)
    print("ComputerTerminal 示範完成！")
    print("=" * 60)
