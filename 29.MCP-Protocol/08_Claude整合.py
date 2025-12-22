"""
與 Claude 整合
=============

本模組展示如何將 MCP 服務器與 Claude Desktop 整合。
學習配置、測試和調試 Claude + MCP 的完整流程。

學習目標：
- 配置 Claude Desktop 使用 MCP 服務器
- 測試 MCP 工具在 Claude 中的使用
- 調試常見問題
- 優化用戶體驗

作者：Claude (Anthropic)
日期：2025-12-22
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


# ============================================================================
# 第一部分：Claude Desktop 配置
# ============================================================================

class ClaudeDesktopIntegration:
    """Claude Desktop MCP 整合"""

    @staticmethod
    def get_config_path() -> Path:
        """獲取 Claude Desktop 配置文件路徑"""
        if sys.platform == "darwin":  # macOS
            return Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
        elif sys.platform == "win32":  # Windows
            import os
            appdata = os.environ.get("APPDATA", "")
            return Path(appdata) / "Claude/claude_desktop_config.json"
        else:  # Linux
            return Path.home() / ".config/Claude/claude_desktop_config.json"

    @staticmethod
    def create_basic_config(
        server_name: str,
        command: str,
        args: List[str],
        env: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        創建基本的 MCP 服務器配置

        Args:
            server_name: 服務器名稱
            command: 啟動命令（如 "python", "node"）
            args: 命令參數
            env: 環境變數

        Returns:
            配置字典
        """
        config = {
            "mcpServers": {
                server_name: {
                    "command": command,
                    "args": args
                }
            }
        }

        if env:
            config["mcpServers"][server_name]["env"] = env

        return config

    @staticmethod
    def create_multi_server_config() -> Dict[str, Any]:
        """創建多服務器配置示例"""
        return {
            "mcpServers": {
                # Python 服務器示例
                "filesystem": {
                    "command": "python",
                    "args": ["-m", "mcp_server_filesystem"],
                    "env": {
                        "ALLOWED_DIRECTORIES": str(Path.home() / "Documents")
                    }
                },

                # Node.js 服務器示例
                "github": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@modelcontextprotocol/server-github"
                    ],
                    "env": {
                        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
                    }
                },

                # 自定義 Python 服務器
                "my-tools": {
                    "command": "python",
                    "args": [
                        str(Path.home() / "mcp-servers/my_server.py")
                    ],
                    "env": {
                        "LOG_LEVEL": "INFO",
                        "DEBUG": "false"
                    }
                },

                # SQLite 數據庫服務器
                "database": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@modelcontextprotocol/server-sqlite",
                        str(Path.home() / "data/mydb.sqlite")
                    ]
                }
            }
        }


# ============================================================================
# 第二部分：服務器實現示例
# ============================================================================

# 完整的 MCP 服務器示例（用於 Claude Desktop）
EXAMPLE_SERVER_CODE = '''
"""
示例 MCP 服務器 - 用於 Claude Desktop
"""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncio
import os
from pathlib import Path

# 創建服務器實例
app = Server("example-tools")


@app.tool()
async def search_files(
    directory: str,
    pattern: str,
    max_results: int = 10
) -> str:
    """
    在目錄中搜索文件

    Args:
        directory: 要搜索的目錄
        pattern: 文件名模式（支持通配符）
        max_results: 最大結果數
    """
    import glob

    search_path = Path(directory) / pattern
    matches = glob.glob(str(search_path), recursive=True)[:max_results]

    if not matches:
        return f"未找到匹配 '{pattern}' 的文件"

    result = f"找到 {len(matches)} 個文件:\\n\\n"
    for match in matches:
        result += f"  • {match}\\n"

    return result


@app.tool()
async def read_file_summary(file_path: str, max_lines: int = 50) -> str:
    """
    讀取文件摘要

    Args:
        file_path: 文件路徑
        max_lines: 最大行數
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:max_lines]

        content = ''.join(lines)
        total_lines = len(lines)

        result = f"文件: {file_path}\\n"
        result += f"顯示前 {total_lines} 行:\\n\\n"
        result += content

        return result

    except Exception as e:
        return f"讀取文件失敗: {e}"


@app.tool()
async def get_system_info() -> str:
    """獲取系統信息"""
    import platform
    import psutil

    info = {
        "系統": platform.system(),
        "版本": platform.version(),
        "處理器": platform.processor(),
        "CPU 核心": psutil.cpu_count(),
        "內存": f"{psutil.virtual_memory().total / (1024**3):.1f} GB",
        "可用內存": f"{psutil.virtual_memory().available / (1024**3):.1f} GB"
    }

    result = "系統信息:\\n\\n"
    for key, value in info.items():
        result += f"  {key}: {value}\\n"

    return result


# 運行服務器
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
'''


# ============================================================================
# 第三部分：測試和調試
# ============================================================================

class MCPTestingGuide:
    """MCP 測試和調試指南"""

    @staticmethod
    def get_debugging_steps() -> List[str]:
        """獲取調試步驟"""
        return [
            "1. 驗證配置文件格式",
            "   - 檢查 JSON 語法",
            "   - 確認路徑正確",
            "   - 驗證環境變數",

            "2. 測試服務器獨立運行",
            "   - 直接運行服務器腳本",
            "   - 檢查是否有錯誤輸出",
            "   - 驗證依賴是否安裝",

            "3. 使用 MCP Inspector 測試",
            "   - npx @modelcontextprotocol/inspector python server.py",
            "   - 查看工具列表",
            "   - 測試工具調用",

            "4. 查看 Claude Desktop 日誌",
            "   - macOS: ~/Library/Logs/Claude/",
            "   - Windows: %APPDATA%\\Claude\\logs\\",
            "   - Linux: ~/.config/Claude/logs/",

            "5. 檢查常見問題",
            "   - Python 版本兼容性",
            "   - 包依賴缺失",
            "   - 權限問題",
            "   - 路徑錯誤"
        ]

    @staticmethod
    def get_common_issues() -> Dict[str, Dict[str, str]]:
        """常見問題和解決方案"""
        return {
            "服務器未出現在 Claude": {
                "原因": "配置文件格式錯誤或路徑不正確",
                "解決": "檢查 JSON 格式，確認配置文件路徑，重啟 Claude Desktop"
            },

            "工具調用失敗": {
                "原因": "服務器代碼錯誤或依賴缺失",
                "解決": "獨立運行服務器測試，檢查錯誤日誌，安裝缺失的包"
            },

            "權限被拒絕": {
                "原因": "訪問受限的文件或目錄",
                "解決": "在配置中明確允許的目錄，檢查文件權限"
            },

            "環境變數未生效": {
                "原因": "環境變數配置錯誤",
                "解決": "使用 ${VAR_NAME} 語法，或在 env 中直接設置值"
            },

            "服務器超時": {
                "原因": "工具執行時間過長",
                "解決": "優化工具性能，增加超時設置，使用異步處理"
            }
        }


# ============================================================================
# 第四部分：最佳實踐
# ============================================================================

class ClaudeMCPBestPractices:
    """Claude + MCP 最佳實踐"""

    GUIDELINES = {
        "工具設計": [
            "保持工具功能單一和專注",
            "提供清晰的工具描述",
            "使用描述性的參數名",
            "返回結構化、易讀的結果"
        ],

        "性能優化": [
            "避免長時間運行的操作",
            "實現超時機制",
            "緩存頻繁訪問的數據",
            "使用流式處理大文件"
        ],

        "用戶體驗": [
            "提供有用的錯誤消息",
            "包含使用示例在描述中",
            "返回格式化的輸出",
            "支持常見的使用場景"
        ],

        "安全性": [
            "限制文件系統訪問範圍",
            "驗證所有輸入",
            "不要暴露敏感信息",
            "記錄安全相關操作"
        ],

        "維護性": [
            "添加詳細的代碼註釋",
            "實現日誌記錄",
            "版本化配置",
            "提供文檔和示例"
        ]
    }

    @staticmethod
    def create_production_config() -> Dict[str, Any]:
        """創建生產環境配置"""
        return {
            "mcpServers": {
                "production-tools": {
                    "command": "python",
                    "args": [
                        "-u",  # 無緩衝輸出
                        "/path/to/production/server.py"
                    ],
                    "env": {
                        "PYTHONUNBUFFERED": "1",
                        "LOG_LEVEL": "INFO",
                        "LOG_FILE": "/var/log/mcp-server.log",
                        "MAX_RETRIES": "3",
                        "TIMEOUT": "30"
                    }
                }
            },
            "globalSettings": {
                "timeout": 30000,
                "logLevel": "info"
            }
        }


# ============================================================================
# 第五部分：實用工具
# ============================================================================

class ConfigurationHelper:
    """配置輔助工具"""

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> List[str]:
        """驗證配置"""
        errors = []

        if "mcpServers" not in config:
            errors.append("缺少 'mcpServers' 鍵")
            return errors

        for name, server_config in config["mcpServers"].items():
            if "command" not in server_config:
                errors.append(f"服務器 '{name}' 缺少 'command'")

            if "args" not in server_config:
                errors.append(f"服務器 '{name}' 缺少 'args'")

            # 檢查命令是否存在
            command = server_config.get("command")
            if command and not ConfigurationHelper._command_exists(command):
                errors.append(f"命令 '{command}' 不存在或不在 PATH 中")

        return errors

    @staticmethod
    def _command_exists(command: str) -> bool:
        """檢查命令是否存在"""
        import shutil
        return shutil.which(command) is not None

    @staticmethod
    def save_config(config: Dict[str, Any], backup: bool = True) -> bool:
        """保存配置（可選備份）"""
        config_path = ClaudeDesktopIntegration.get_config_path()

        try:
            # 備份現有配置
            if backup and config_path.exists():
                import shutil
                backup_path = config_path.with_suffix('.json.backup')
                shutil.copy2(config_path, backup_path)
                print(f"✓ 已備份現有配置到: {backup_path}")

            # 創建目錄
            config_path.parent.mkdir(parents=True, exist_ok=True)

            # 保存配置
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            print(f"✓ 配置已保存到: {config_path}")
            return True

        except Exception as e:
            print(f"✗ 保存配置失敗: {e}")
            return False


# ============================================================================
# 主程式示例
# ============================================================================

def main():
    """主程式：Claude Desktop 整合指南"""

    print("=" * 70)
    print("Claude Desktop MCP 整合")
    print("=" * 70)

    # 1. 獲取配置路徑
    print("\n【步驟 1：配置文件位置】")
    config_path = ClaudeDesktopIntegration.get_config_path()
    print(f"配置文件: {config_path}")

    # 2. 創建配置示例
    print("\n【步驟 2：配置示例】")
    config = ClaudeDesktopIntegration.create_multi_server_config()
    print("多服務器配置：")
    print(json.dumps(config, indent=2, ensure_ascii=False))

    # 3. 服務器代碼示例
    print("\n【步驟 3：服務器實現】")
    print("保存以下代碼為 server.py：")
    print(EXAMPLE_SERVER_CODE[:500] + "...\n[代碼已截斷，查看完整版本]")

    # 4. 測試步驟
    print("\n【步驟 4：測試和調試】")
    for step in MCPTestingGuide.get_debugging_steps():
        print(f"  {step}")

    # 5. 常見問題
    print("\n【步驟 5：常見問題】")
    issues = MCPTestingGuide.get_common_issues()
    for issue, details in list(issues.items())[:2]:
        print(f"\n  問題: {issue}")
        print(f"  原因: {details['原因']}")
        print(f"  解決: {details['解決']}")

    # 6. 最佳實踐
    print("\n【步驟 6：最佳實踐】")
    for category, practices in list(ClaudeMCPBestPractices.GUIDELINES.items())[:2]:
        print(f"\n  {category}:")
        for practice in practices:
            print(f"    • {practice}")

    print("\n" + "=" * 70)
    print("下一步：查看 09_OpenAI整合.py 學習與 OpenAI 整合")
    print("=" * 70)


if __name__ == "__main__":
    main()
