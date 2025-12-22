"""
MCP SDK 安裝與配置
==================

本模組介紹如何安裝和配置 MCP SDK，包括 Python 和 TypeScript 兩種官方 SDK。

支持的環境：
- Python 3.10+
- Node.js 18+
- 作業系統：macOS, Linux, Windows

作者：Claude (Anthropic)
日期：2025-12-22
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


# ============================================================================
# 第一部分：環境檢查
# ============================================================================

@dataclass
class EnvironmentInfo:
    """環境資訊"""
    python_version: str
    node_version: Optional[str]
    npm_version: Optional[str]
    platform: str
    home_dir: str


class EnvironmentChecker:
    """環境檢查工具"""

    @staticmethod
    def check_python_version() -> tuple[bool, str]:
        """檢查 Python 版本"""
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"

        if version.major == 3 and version.minor >= 10:
            return True, version_str
        else:
            return False, version_str

    @staticmethod
    def check_node_version() -> tuple[bool, Optional[str]]:
        """檢查 Node.js 版本"""
        try:
            result = subprocess.run(
                ['node', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            version = result.stdout.strip()

            # 提取版本號（格式：v18.x.x）
            major_version = int(version.split('.')[0].replace('v', ''))

            if major_version >= 18:
                return True, version
            else:
                return False, version

        except (subprocess.SubprocessError, FileNotFoundError, ValueError):
            return False, None

    @staticmethod
    def get_environment_info() -> EnvironmentInfo:
        """獲取完整環境資訊"""
        _, py_version = EnvironmentChecker.check_python_version()
        _, node_version = EnvironmentChecker.check_node_version()

        npm_version = None
        try:
            result = subprocess.run(
                ['npm', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            npm_version = result.stdout.strip()
        except:
            pass

        return EnvironmentInfo(
            python_version=py_version,
            node_version=node_version,
            npm_version=npm_version,
            platform=sys.platform,
            home_dir=str(Path.home())
        )


# ============================================================================
# 第二部分：Python SDK 安裝
# ============================================================================

class PythonSDKInstaller:
    """Python MCP SDK 安裝器"""

    PACKAGE_NAME = "mcp"
    RECOMMENDED_VERSION = ">=1.0.0"

    @staticmethod
    def generate_requirements() -> str:
        """生成 requirements.txt 內容"""
        return f"""# MCP Python SDK
mcp{PythonSDKInstaller.RECOMMENDED_VERSION}

# 可選依賴（根據需要選擇）

# 用於 HTTP 傳輸
httpx>=0.25.0

# 用於增強的異步功能
anyio>=4.0.0

# 用於 JSON schema 驗證
jsonschema>=4.19.0

# 用於日誌記錄
structlog>=23.1.0

# 用於類型檢查
typing-extensions>=4.8.0
"""

    @staticmethod
    def install_commands() -> Dict[str, str]:
        """返回安裝命令"""
        return {
            "基本安裝": "pip install mcp",
            "指定版本": f"pip install mcp{PythonSDKInstaller.RECOMMENDED_VERSION}",
            "開發模式": "pip install -e .",
            "包含可選依賴": "pip install mcp[all]",
            "從源碼安裝": "pip install git+https://github.com/modelcontextprotocol/python-sdk.git"
        }

    @staticmethod
    def verify_installation() -> bool:
        """驗證安裝"""
        try:
            import mcp
            print(f"✓ MCP SDK 已安裝，版本：{mcp.__version__}")
            return True
        except ImportError:
            print("✗ MCP SDK 未安裝")
            return False


# ============================================================================
# 第三部分：TypeScript SDK 安裝
# ============================================================================

class TypeScriptSDKInstaller:
    """TypeScript MCP SDK 安裝器"""

    PACKAGE_NAME = "@modelcontextprotocol/sdk"

    @staticmethod
    def generate_package_json() -> Dict:
        """生成 package.json 內容"""
        return {
            "name": "mcp-project",
            "version": "1.0.0",
            "type": "module",
            "description": "MCP 專案",
            "main": "index.js",
            "scripts": {
                "dev": "tsx watch src/index.ts",
                "build": "tsc",
                "start": "node dist/index.js"
            },
            "dependencies": {
                "@modelcontextprotocol/sdk": "^1.0.0"
            },
            "devDependencies": {
                "@types/node": "^20.0.0",
                "typescript": "^5.3.0",
                "tsx": "^4.7.0"
            }
        }

    @staticmethod
    def generate_tsconfig() -> Dict:
        """生成 tsconfig.json 內容"""
        return {
            "compilerOptions": {
                "target": "ES2022",
                "module": "Node16",
                "moduleResolution": "Node16",
                "outDir": "./dist",
                "rootDir": "./src",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "resolveJsonModule": True,
                "declaration": True,
                "declarationMap": True,
                "sourceMap": True
            },
            "include": ["src/**/*"],
            "exclude": ["node_modules", "dist"]
        }

    @staticmethod
    def install_commands() -> Dict[str, str]:
        """返回安裝命令"""
        return {
            "使用 npm": "npm install @modelcontextprotocol/sdk",
            "使用 pnpm": "pnpm add @modelcontextprotocol/sdk",
            "使用 yarn": "yarn add @modelcontextprotocol/sdk",
            "全局安裝 CLI": "npm install -g @modelcontextprotocol/cli"
        }


# ============================================================================
# 第四部分：Claude Desktop 配置
# ============================================================================

class ClaudeDesktopConfig:
    """Claude Desktop 配置管理"""

    @staticmethod
    def get_config_path() -> Path:
        """獲取配置文件路徑"""
        platform = sys.platform

        if platform == "darwin":  # macOS
            return Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
        elif platform == "win32":  # Windows
            return Path(os.environ.get("APPDATA", "")) / "Claude/claude_desktop_config.json"
        else:  # Linux
            return Path.home() / ".config/Claude/claude_desktop_config.json"

    @staticmethod
    def generate_basic_config() -> Dict:
        """生成基本配置"""
        return {
            "mcpServers": {
                "example-server": {
                    "command": "python",
                    "args": ["/path/to/your/server.py"]
                }
            }
        }

    @staticmethod
    def generate_advanced_config() -> Dict:
        """生成進階配置"""
        return {
            "mcpServers": {
                # Python 服務器示例
                "filesystem": {
                    "command": "python",
                    "args": ["-m", "mcp_server_filesystem"],
                    "env": {
                        "ALLOWED_DIRECTORIES": "/Users/username/Documents"
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

                # 自定義服務器示例
                "my-custom-server": {
                    "command": "python",
                    "args": [
                        "/Users/username/projects/my-mcp-server/server.py"
                    ],
                    "env": {
                        "LOG_LEVEL": "INFO",
                        "DATA_PATH": "/Users/username/data"
                    }
                }
            },

            # 全局設定
            "globalSettings": {
                "timeout": 30000,  # 30 秒超時
                "logLevel": "info"
            }
        }

    @staticmethod
    def save_config(config: Dict, path: Optional[Path] = None) -> bool:
        """保存配置文件"""
        if path is None:
            path = ClaudeDesktopConfig.get_config_path()

        try:
            # 確保目錄存在
            path.parent.mkdir(parents=True, exist_ok=True)

            # 寫入配置
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            print(f"✓ 配置已保存到：{path}")
            return True

        except Exception as e:
            print(f"✗ 保存配置失敗：{e}")
            return False


# ============================================================================
# 第五部分：開發工具配置
# ============================================================================

class DevelopmentTools:
    """開發工具配置"""

    @staticmethod
    def setup_vscode_settings() -> Dict:
        """生成 VSCode 設定"""
        return {
            "python.analysis.typeCheckingMode": "basic",
            "python.linting.enabled": True,
            "python.linting.pylintEnabled": True,
            "python.formatting.provider": "black",
            "editor.formatOnSave": True,
            "files.associations": {
                "*.mcpconfig": "json"
            }
        }

    @staticmethod
    def setup_git_ignore() -> str:
        """生成 .gitignore 內容"""
        return """# MCP 相關
*.mcpconfig.local
.mcp-server-logs/
mcp-cache/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# Node.js
node_modules/
dist/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# 環境變數
.env
.env.local
"""

    @staticmethod
    def setup_pre_commit() -> Dict:
        """生成 pre-commit 配置"""
        return {
            "repos": [
                {
                    "repo": "https://github.com/pre-commit/pre-commit-hooks",
                    "rev": "v4.5.0",
                    "hooks": [
                        {"id": "trailing-whitespace"},
                        {"id": "end-of-file-fixer"},
                        {"id": "check-yaml"},
                        {"id": "check-json"}
                    ]
                },
                {
                    "repo": "https://github.com/psf/black",
                    "rev": "23.12.0",
                    "hooks": [{"id": "black"}]
                }
            ]
        }


# ============================================================================
# 主程式示例
# ============================================================================

def main():
    """主程式：環境檢查和配置指南"""

    print("=" * 70)
    print("MCP SDK 安裝與配置")
    print("=" * 70)

    # 1. 環境檢查
    print("\n【步驟 1：環境檢查】")
    checker = EnvironmentChecker()
    env_info = checker.get_environment_info()

    print(f"  • Python: {env_info.python_version}")
    print(f"  • Node.js: {env_info.node_version or '未安裝'}")
    print(f"  • npm: {env_info.npm_version or '未安裝'}")
    print(f"  • 平台: {env_info.platform}")

    py_ok, _ = checker.check_python_version()
    if py_ok:
        print("  ✓ Python 版本符合要求")
    else:
        print("  ✗ Python 版本過低，需要 3.10+")

    # 2. Python SDK 安裝
    print("\n【步驟 2：安裝 Python SDK】")
    py_installer = PythonSDKInstaller()
    for name, command in py_installer.install_commands().items():
        print(f"  • {name}:")
        print(f"    {command}")

    # 3. TypeScript SDK 安裝（如果有 Node.js）
    if env_info.node_version:
        print("\n【步驟 3：安裝 TypeScript SDK】")
        ts_installer = TypeScriptSDKInstaller()
        for name, command in ts_installer.install_commands().items():
            print(f"  • {name}:")
            print(f"    {command}")

    # 4. Claude Desktop 配置
    print("\n【步驟 4：配置 Claude Desktop】")
    config_path = ClaudeDesktopConfig.get_config_path()
    print(f"  配置文件位置：{config_path}")

    print("\n  基本配置示例：")
    basic_config = ClaudeDesktopConfig.generate_basic_config()
    print(f"  {json.dumps(basic_config, indent=2, ensure_ascii=False)}")

    # 5. 驗證安裝
    print("\n【步驟 5：驗證安裝】")
    PythonSDKInstaller.verify_installation()

    print("\n" + "=" * 70)
    print("配置完成！下一步：查看 03_創建MCP服務器.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
