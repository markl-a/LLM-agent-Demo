#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SWE-Agent 沙箱執行範例
======================

這個範例展示如何使用 Docker 沙箱安全執行代碼：
1. Docker 容器管理
2. 隔離環境配置
3. 資源限制設置
4. 安全執行策略
5. 容器網路配置
6. 持久化數據管理

沙箱執行確保 AI Agent 在修復代碼時不會影響主系統，
並且可以安全地測試不受信任的代碼。

作者: SWE-Agent 團隊
日期: 2025-12-31
"""

import os
import sys
import time
import json
import tempfile
import tarfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import shutil

# Docker SDK
try:
    import docker
    from docker.models.containers import Container
    from docker.types import Mount, LogConfig
except ImportError:
    print("請安裝: pip install docker")

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.layout import Layout


@dataclass
class SandboxConfig:
    """
    沙箱配置
    """
    # Docker 配置
    image: str = "python:3.9-slim"
    container_name: Optional[str] = None

    # 資源限制
    memory_limit: str = "512m"
    cpu_quota: int = 50000  # 50% CPU
    cpu_period: int = 100000

    # 網路配置
    network_disabled: bool = False
    network_mode: str = "bridge"

    # 安全配置
    read_only: bool = False
    privileged: bool = False
    security_opt: List[str] = field(default_factory=lambda: ["no-new-privileges"])

    # 超時設置
    timeout: int = 300  # 5分鐘

    # 工作目錄
    working_dir: str = "/workspace"

    # 環境變量
    environment: Dict[str, str] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """
    執行結果
    """
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    duration: float
    container_id: Optional[str] = None
    error_message: Optional[str] = None


class DockerSandbox:
    """
    Docker 沙箱管理器

    管理 Docker 容器的生命周期，提供安全的代碼執行環境
    """

    def __init__(self, config: Optional[SandboxConfig] = None):
        """
        初始化沙箱

        Args:
            config: 沙箱配置
        """
        self.config = config or SandboxConfig()
        self.console = Console()

        # 初始化 Docker 客戶端
        try:
            self.client = docker.from_env()
            self.client.ping()
            logger.info("Docker 連接成功")
        except Exception as e:
            logger.error(f"Docker 連接失敗: {e}")
            raise

        self.containers = {}  # 容器追蹤

    def create_container(
        self,
        command: Optional[str] = None,
        volumes: Optional[Dict[str, Dict]] = None
    ) -> Container:
        """
        創建容器

        Args:
            command: 要執行的命令
            volumes: 卷掛載配置

        Returns:
            容器對象
        """
        self.console.print("[bold]創建沙箱容器...[/bold]")

        try:
            # 確保映像存在
            self._ensure_image(self.config.image)

            # 準備容器配置
            container_config = {
                "image": self.config.image,
                "command": command,
                "detach": True,
                "name": self.config.container_name,
                "working_dir": self.config.working_dir,
                "environment": self.config.environment,

                # 資源限制
                "mem_limit": self.config.memory_limit,
                "cpu_quota": self.config.cpu_quota,
                "cpu_period": self.config.cpu_period,

                # 網路配置
                "network_disabled": self.config.network_disabled,
                "network_mode": self.config.network_mode,

                # 安全配置
                "read_only": self.config.read_only,
                "privileged": self.config.privileged,
                "security_opt": self.config.security_opt,

                # 自動刪除
                "auto_remove": False,

                # 卷掛載
                "volumes": volumes or {}
            }

            # 創建容器
            container = self.client.containers.create(**container_config)

            self.containers[container.id] = container

            self.console.print(f"[green]✓ 容器已創建: {container.short_id}[/green]")

            return container

        except Exception as e:
            logger.error(f"創建容器失敗: {e}")
            raise

    def run_command(
        self,
        command: str,
        workspace_path: Optional[Path] = None,
        capture_output: bool = True
    ) -> ExecutionResult:
        """
        在沙箱中運行命令

        Args:
            command: 要執行的命令
            workspace_path: 工作空間路徑（主機）
            capture_output: 是否捕獲輸出

        Returns:
            執行結果
        """
        self.console.print(f"[bold]執行命令: {command}[/bold]")

        start_time = time.time()

        # 準備工作空間
        volumes = {}
        if workspace_path:
            volumes = {
                str(workspace_path): {
                    'bind': self.config.working_dir,
                    'mode': 'rw'
                }
            }

        # 創建容器
        container = self.create_container(command=command, volumes=volumes)

        try:
            # 啟動容器
            container.start()

            # 等待執行完成
            exit_code = container.wait(timeout=self.config.timeout)

            # 獲取輸出
            stdout = ""
            stderr = ""

            if capture_output:
                logs = container.logs(stdout=True, stderr=True).decode('utf-8')
                stdout = logs

            duration = time.time() - start_time

            # 清理容器
            container.remove(force=True)

            result = ExecutionResult(
                success=(exit_code['StatusCode'] == 0),
                exit_code=exit_code['StatusCode'],
                stdout=stdout,
                stderr=stderr,
                duration=duration,
                container_id=container.short_id
            )

            self._display_result(result)

            return result

        except Exception as e:
            logger.error(f"執行失敗: {e}")

            # 清理
            try:
                container.remove(force=True)
            except:
                pass

            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                duration=time.time() - start_time,
                error_message=str(e)
            )

    def run_python_code(
        self,
        code: str,
        workspace_path: Optional[Path] = None
    ) -> ExecutionResult:
        """
        運行 Python 代碼

        Args:
            code: Python 代碼
            workspace_path: 工作空間路徑

        Returns:
            執行結果
        """
        # 創建臨時文件
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False
        ) as f:
            f.write(code)
            temp_file = Path(f.name)

        try:
            # 如果沒有工作空間，創建臨時工作空間
            if not workspace_path:
                workspace_path = Path(tempfile.mkdtemp())
                shutil.copy(temp_file, workspace_path / "script.py")
            else:
                shutil.copy(temp_file, workspace_path / "script.py")

            # 運行
            result = self.run_command(
                "python /workspace/script.py",
                workspace_path=workspace_path
            )

            return result

        finally:
            temp_file.unlink()

    def run_tests(
        self,
        test_command: str,
        workspace_path: Path
    ) -> ExecutionResult:
        """
        在沙箱中運行測試

        Args:
            test_command: 測試命令
            workspace_path: 工作空間路徑

        Returns:
            執行結果
        """
        self.console.print("[bold]在沙箱中運行測試...[/bold]")

        # 首先安裝依賴
        if (workspace_path / "requirements.txt").exists():
            self.console.print("  安裝依賴...")
            install_result = self.run_command(
                "pip install -r /workspace/requirements.txt",
                workspace_path=workspace_path
            )

            if not install_result.success:
                self.console.print("[red]依賴安裝失敗[/red]")
                return install_result

        # 運行測試
        return self.run_command(test_command, workspace_path=workspace_path)

    def _ensure_image(self, image: str):
        """
        確保 Docker 映像存在

        Args:
            image: 映像名稱
        """
        try:
            self.client.images.get(image)
            logger.info(f"映像已存在: {image}")
        except docker.errors.ImageNotFound:
            self.console.print(f"[yellow]拉取映像: {image}...[/yellow]")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"拉取 {image}", total=None)

                self.client.images.pull(image)

                progress.update(task, completed=True)

            self.console.print("[green]✓ 映像拉取完成[/green]")

    def _display_result(self, result: ExecutionResult):
        """顯示執行結果"""
        status = "[green]成功[/green]" if result.success else "[red]失敗[/red]"

        info = f"""
        狀態: {status}
        退出碼: {result.exit_code}
        耗時: {result.duration:.2f} 秒
        容器: {result.container_id or 'N/A'}
        """

        self.console.print(Panel(info, title="執行結果", border_style="blue"))

        if result.stdout:
            self.console.print("\n[bold]標準輸出:[/bold]")
            self.console.print(result.stdout)

        if result.stderr:
            self.console.print("\n[bold]標準錯誤:[/bold]")
            self.console.print(result.stderr)

    def cleanup(self):
        """清理所有容器"""
        self.console.print("[bold]清理容器...[/bold]")

        for container_id, container in self.containers.items():
            try:
                container.remove(force=True)
                self.console.print(f"  ✓ 已刪除容器: {container.short_id}")
            except Exception as e:
                logger.warning(f"刪除容器失敗 {container_id}: {e}")

        self.containers.clear()

    def list_containers(self) -> List[Dict]:
        """
        列出所有容器

        Returns:
            容器信息列表
        """
        containers = self.client.containers.list(all=True)

        container_info = []
        for container in containers:
            info = {
                "id": container.short_id,
                "name": container.name,
                "image": container.image.tags[0] if container.image.tags else "unknown",
                "status": container.status,
                "created": container.attrs['Created']
            }
            container_info.append(info)

        return container_info

    def get_container_stats(self, container_id: str) -> Dict:
        """
        獲取容器統計信息

        Args:
            container_id: 容器 ID

        Returns:
            統計信息
        """
        container = self.client.containers.get(container_id)
        stats = container.stats(stream=False)

        return stats


class SandboxPool:
    """
    沙箱池

    管理多個沙箱實例，支援並行執行
    """

    def __init__(self, pool_size: int = 3):
        """
        初始化沙箱池

        Args:
            pool_size: 池大小
        """
        self.pool_size = pool_size
        self.sandboxes = []
        self.console = Console()

        # 創建沙箱池
        for i in range(pool_size):
            config = SandboxConfig(
                container_name=f"swe-agent-sandbox-{i}"
            )
            sandbox = DockerSandbox(config)
            self.sandboxes.append(sandbox)

        logger.info(f"沙箱池初始化完成，大小: {pool_size}")

    def execute_parallel(
        self,
        commands: List[str],
        workspace_paths: Optional[List[Path]] = None
    ) -> List[ExecutionResult]:
        """
        並行執行命令

        Args:
            commands: 命令列表
            workspace_paths: 工作空間路徑列表

        Returns:
            執行結果列表
        """
        self.console.print(f"[bold]並行執行 {len(commands)} 個命令...[/bold]")

        results = []

        # 簡單的輪詢調度
        for i, command in enumerate(commands):
            sandbox_index = i % self.pool_size
            sandbox = self.sandboxes[sandbox_index]

            workspace = workspace_paths[i] if workspace_paths else None

            result = sandbox.run_command(command, workspace_path=workspace)
            results.append(result)

        return results

    def cleanup_all(self):
        """清理所有沙箱"""
        for sandbox in self.sandboxes:
            sandbox.cleanup()


class SecureExecutor:
    """
    安全執行器

    提供額外的安全檢查和限制
    """

    def __init__(self):
        """初始化"""
        self.console = Console()

        # 危險操作模式
        self.dangerous_patterns = [
            r'rm\s+-rf\s+/',
            r':\(\)\{.*\}',  # Fork bomb
            r'dd\s+if=/dev/zero',
            r'chmod\s+777',
            r'curl.*\|\s*bash',
            r'eval\(',
            r'exec\('
        ]

    def is_safe_command(self, command: str) -> Tuple[bool, Optional[str]]:
        """
        檢查命令是否安全

        Args:
            command: 命令字符串

        Returns:
            (是否安全, 原因)
        """
        import re

        for pattern in self.dangerous_patterns:
            if re.search(pattern, command):
                return False, f"檢測到危險操作: {pattern}"

        return True, None

    def execute_safely(
        self,
        command: str,
        sandbox: DockerSandbox,
        workspace_path: Optional[Path] = None
    ) -> ExecutionResult:
        """
        安全執行命令

        Args:
            command: 命令
            sandbox: 沙箱實例
            workspace_path: 工作空間路徑

        Returns:
            執行結果
        """
        # 安全檢查
        is_safe, reason = self.is_safe_command(command)

        if not is_safe:
            self.console.print(f"[red]命令被拒絕: {reason}[/red]")

            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Security check failed: {reason}",
                duration=0,
                error_message=reason
            )

        # 執行
        return sandbox.run_command(command, workspace_path)


class EnvironmentManager:
    """
    環境管理器

    管理不同的執行環境配置
    """

    def __init__(self):
        """初始化"""
        self.console = Console()

        # 預定義環境
        self.environments = {
            "python3.9": SandboxConfig(
                image="python:3.9-slim",
                environment={"PYTHONPATH": "/workspace"}
            ),
            "python3.11": SandboxConfig(
                image="python:3.11-slim",
                environment={"PYTHONPATH": "/workspace"}
            ),
            "node16": SandboxConfig(
                image="node:16-slim",
                working_dir="/app"
            ),
            "ubuntu": SandboxConfig(
                image="ubuntu:22.04"
            ),
        }

    def get_environment(self, name: str) -> Optional[SandboxConfig]:
        """
        獲取環境配置

        Args:
            name: 環境名稱

        Returns:
            配置對象
        """
        return self.environments.get(name)

    def create_custom_environment(
        self,
        name: str,
        base_image: str,
        install_commands: List[str]
    ) -> SandboxConfig:
        """
        創建自定義環境

        Args:
            name: 環境名稱
            base_image: 基礎映像
            install_commands: 安裝命令

        Returns:
            配置對象
        """
        # 構建自定義映像
        dockerfile = f"""
FROM {base_image}

{chr(10).join(f'RUN {cmd}' for cmd in install_commands)}

WORKDIR /workspace
"""

        # 使用 Docker 構建映像
        # TODO: 實現實際的映像構建邏輯

        config = SandboxConfig(image=name)
        self.environments[name] = config

        return config


def main():
    """主函數"""
    console = Console()

    console.print(Panel(
        "[bold]SWE-Agent 沙箱執行範例[/bold]\n\n"
        "展示如何在 Docker 沙箱中安全執行代碼",
        border_style="green"
    ))

    # 1. 創建沙箱
    console.print("\n[bold cyan]1. 創建沙箱[/bold cyan]")
    config = SandboxConfig(
        image="python:3.9-slim",
        memory_limit="256m",
        timeout=60
    )
    sandbox = DockerSandbox(config)

    # 2. 運行簡單命令
    console.print("\n[bold cyan]2. 運行簡單命令[/bold cyan]")
    result = sandbox.run_command("python --version")

    # 3. 運行 Python 代碼
    console.print("\n[bold cyan]3. 運行 Python 代碼[/bold cyan]")
    code = """
print("Hello from sandbox!")
import sys
print(f"Python version: {sys.version}")

# 簡單計算
result = sum(range(100))
print(f"Sum of 0-99: {result}")
"""
    result = sandbox.run_python_code(code)

    # 4. 安全檢查
    console.print("\n[bold cyan]4. 安全執行[/bold cyan]")
    executor = SecureExecutor()

    # 測試危險命令
    dangerous_cmd = "rm -rf /"
    is_safe, reason = executor.is_safe_command(dangerous_cmd)
    console.print(f"命令 '{dangerous_cmd}' 安全嗎? {is_safe}")
    if not is_safe:
        console.print(f"原因: {reason}")

    # 5. 清理
    console.print("\n[bold cyan]5. 清理[/bold cyan]")
    sandbox.cleanup()


if __name__ == "__main__":
    main()
