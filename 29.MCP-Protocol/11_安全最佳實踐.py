"""
MCP 安全最佳實踐
================

本模組介紹 MCP 服務器和客戶端的安全考慮和防護措施。
學習如何構建安全、可靠的 MCP 應用。

學習目標：
- 理解 MCP 的安全威脅模型
- 實現輸入驗證和清理
- 配置訪問控制和權限管理
- 處理敏感數據和憑證

作者：Claude (Anthropic)
日期：2025-12-22
"""

import hashlib
import secrets
import re
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


# ============================================================================
# 第一部分：安全威脅模型
# ============================================================================

class SecurityThreatModel:
    """MCP 安全威脅模型"""

    THREATS = {
        "代碼注入": {
            "描述": "惡意代碼通過工具參數注入並執行",
            "風險等級": "嚴重",
            "影響": "任意代碼執行，系統完全被控制",
            "防護": [
                "嚴格的輸入驗證",
                "使用白名單而非黑名單",
                "沙箱隔離執行環境",
                "禁用危險函數（exec, eval 等）"
            ]
        },

        "路徑遍歷": {
            "描述": "訪問系統中未授權的文件或目錄",
            "風險等級": "高",
            "影響": "讀取敏感文件，數據洩露",
            "防護": [
                "規範化路徑",
                "檢查路徑是否在允許範圍內",
                "使用絕對路徑",
                "禁止符號鏈接（可選）"
            ]
        },

        "資源耗盡": {
            "描述": "惡意或錯誤的操作消耗過多資源",
            "風險等級": "中",
            "影響": "服務拒絕，性能下降",
            "防護": [
                "設置超時限制",
                "限制內存使用",
                "限制並發請求數",
                "實現速率限制"
            ]
        },

        "權限提升": {
            "描述": "獲取超出授權的訪問權限",
            "風險等級": "高",
            "影響": "訪問受限資源",
            "防護": [
                "最小權限原則",
                "明確的權限模型",
                "定期審計權限",
                "使用專用服務賬戶"
            ]
        },

        "數據洩露": {
            "描述": "敏感信息被未授權訪問或傳輸",
            "風險等級": "嚴重",
            "影響": "隱私洩露，合規問題",
            "防護": [
                "加密敏感數據",
                "審計日誌",
                "脫敏輸出",
                "安全的憑證管理"
            ]
        }
    }


# ============================================================================
# 第二部分：輸入驗證
# ============================================================================

class InputValidator:
    """輸入驗證器"""

    @staticmethod
    def validate_string(
        value: str,
        max_length: int = 10000,
        pattern: Optional[str] = None,
        forbidden_chars: Optional[Set[str]] = None
    ) -> tuple[bool, Optional[str]]:
        """
        驗證字符串輸入

        Args:
            value: 要驗證的值
            max_length: 最大長度
            pattern: 正則表達式模式
            forbidden_chars: 禁止的字符集

        Returns:
            (是否有效, 錯誤消息)
        """
        # 長度檢查
        if len(value) > max_length:
            return False, f"字符串過長（最大 {max_length} 字符）"

        # 模式匹配
        if pattern and not re.match(pattern, value):
            return False, f"格式不符合要求"

        # 禁止字符檢查
        if forbidden_chars:
            found = set(value) & forbidden_chars
            if found:
                return False, f"包含禁止字符: {found}"

        return True, None

    @staticmethod
    def validate_path(
        path: str,
        allowed_directories: List[str],
        allow_symlinks: bool = False
    ) -> tuple[bool, Optional[str]]:
        """
        驗證文件路徑

        Args:
            path: 文件路徑
            allowed_directories: 允許的目錄列表
            allow_symlinks: 是否允許符號鏈接

        Returns:
            (是否有效, 錯誤消息)
        """
        try:
            # 轉換為絕對路徑
            abs_path = Path(path).resolve()

            # 檢查符號鏈接
            if not allow_symlinks and abs_path.is_symlink():
                return False, "不允許符號鏈接"

            # 檢查是否在允許的目錄中
            is_allowed = False
            for allowed_dir in allowed_directories:
                allowed_abs = Path(allowed_dir).resolve()
                try:
                    abs_path.relative_to(allowed_abs)
                    is_allowed = True
                    break
                except ValueError:
                    continue

            if not is_allowed:
                return False, f"路徑不在允許的目錄中"

            return True, None

        except Exception as e:
            return False, f"路徑驗證失敗: {e}"

    @staticmethod
    def sanitize_sql(query: str) -> str:
        """
        清理 SQL 查詢（基礎版）

        注意：這不能替代參數化查詢！
        """
        # 移除註釋
        query = re.sub(r'--.*?$', '', query, flags=re.MULTILINE)
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)

        # 移除多餘空白
        query = ' '.join(query.split())

        return query

    @staticmethod
    def validate_code_safety(code: str) -> tuple[bool, List[str]]:
        """
        驗證代碼安全性

        檢查是否包含危險操作
        """
        issues = []

        # 危險關鍵字
        dangerous_keywords = [
            'exec', 'eval', 'compile', '__import__',
            'open', 'file', 'input', 'raw_input',
            'os.system', 'subprocess', 'commands'
        ]

        for keyword in dangerous_keywords:
            if keyword in code:
                issues.append(f"包含危險關鍵字: {keyword}")

        # 檢查導入
        import_pattern = r'import\s+(\w+)'
        imports = re.findall(import_pattern, code)

        allowed_modules = {'math', 'datetime', 'json', 'random', 'statistics'}
        for module in imports:
            if module not in allowed_modules:
                issues.append(f"不允許導入模組: {module}")

        is_safe = len(issues) == 0
        return is_safe, issues


# ============================================================================
# 第三部分：訪問控制
# ============================================================================

class Permission(Enum):
    """權限類型"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DELETE = "delete"
    ADMIN = "admin"


@dataclass
class AccessPolicy:
    """訪問策略"""
    resource: str  # 資源標識
    permissions: Set[Permission]  # 允許的權限
    conditions: Optional[Dict[str, Any]] = None  # 條件（如時間範圍）


class AccessControlList:
    """訪問控制列表（ACL）"""

    def __init__(self):
        self.policies: Dict[str, List[AccessPolicy]] = {}

    def grant(
        self,
        user_id: str,
        resource: str,
        permissions: Set[Permission]
    ):
        """授予權限"""
        if user_id not in self.policies:
            self.policies[user_id] = []

        policy = AccessPolicy(
            resource=resource,
            permissions=permissions
        )

        self.policies[user_id].append(policy)

    def check(
        self,
        user_id: str,
        resource: str,
        permission: Permission
    ) -> bool:
        """檢查權限"""
        if user_id not in self.policies:
            return False

        for policy in self.policies[user_id]:
            # 檢查資源匹配（支持通配符）
            if self._match_resource(policy.resource, resource):
                if permission in policy.permissions:
                    return True

        return False

    def _match_resource(self, pattern: str, resource: str) -> bool:
        """匹配資源模式"""
        # 簡單的通配符匹配
        if pattern == "*":
            return True

        if pattern.endswith("/*"):
            prefix = pattern[:-2]
            return resource.startswith(prefix)

        return pattern == resource


# ============================================================================
# 第四部分：憑證管理
# ============================================================================

class CredentialManager:
    """憑證管理器"""

    def __init__(self):
        self.credentials: Dict[str, str] = {}

    def store_credential(
        self,
        key: str,
        value: str,
        encrypt: bool = True
    ):
        """存儲憑證"""
        if encrypt:
            # 實際應用中應使用真正的加密
            encrypted_value = self._simple_encrypt(value)
            self.credentials[key] = encrypted_value
        else:
            self.credentials[key] = value

    def get_credential(
        self,
        key: str,
        decrypt: bool = True
    ) -> Optional[str]:
        """獲取憑證"""
        if key not in self.credentials:
            return None

        value = self.credentials[key]

        if decrypt:
            return self._simple_decrypt(value)
        else:
            return value

    def _simple_encrypt(self, value: str) -> str:
        """簡單加密（僅示例，生產環境應使用真正的加密）"""
        return hashlib.sha256(value.encode()).hexdigest()

    def _simple_decrypt(self, value: str) -> str:
        """簡單解密（僅示例）"""
        # 實際應用中應該能夠解密
        return value

    @staticmethod
    def generate_api_key() -> str:
        """生成 API 密鑰"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
        """脫敏敏感數據"""
        if len(data) <= visible_chars:
            return "*" * len(data)

        return data[:visible_chars] + "*" * (len(data) - visible_chars)


# ============================================================================
# 第五部分：安全 MCP 服務器實現
# ============================================================================

SECURE_SERVER_EXAMPLE = '''
"""
安全的 MCP 服務器實現示例
"""

from mcp.server import Server
from mcp.server.stdio import stdio_server
import asyncio
from pathlib import Path
import logging


# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/var/log/mcp-server.log'
)
logger = logging.getLogger(__name__)


class SecureMCPServer:
    """安全的 MCP 服務器"""

    def __init__(self, allowed_dirs: list[str]):
        self.app = Server("secure-server")
        self.allowed_dirs = [Path(d).resolve() for d in allowed_dirs]
        self.setup_tools()

    def setup_tools(self):
        """設置工具"""

        @self.app.tool()
        async def read_file(path: str) -> str:
            """安全的文件讀取"""
            try:
                # 1. 驗證路徑
                abs_path = Path(path).resolve()

                is_allowed = False
                for allowed_dir in self.allowed_dirs:
                    try:
                        abs_path.relative_to(allowed_dir)
                        is_allowed = True
                        break
                    except ValueError:
                        continue

                if not is_allowed:
                    logger.warning(f"拒絕訪問: {path}")
                    return "錯誤: 無權訪問此文件"

                # 2. 檢查文件大小
                if abs_path.stat().st_size > 10 * 1024 * 1024:  # 10MB
                    return "錯誤: 文件過大"

                # 3. 讀取文件
                with open(abs_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                logger.info(f"成功讀取: {path}")
                return content

            except Exception as e:
                logger.error(f"讀取文件失敗: {e}")
                return f"錯誤: {type(e).__name__}"

    async def run(self):
        """運行服務器"""
        async with stdio_server() as (read, write):
            await self.app.run(
                read,
                write,
                self.app.create_initialization_options()
            )


async def main():
    server = SecureMCPServer(allowed_dirs=["/home/user/safe-data"])
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
'''


# ============================================================================
# 第六部分：安全檢查清單
# ============================================================================

class SecurityChecklist:
    """安全檢查清單"""

    CHECKLIST = {
        "開發階段": [
            "☐ 所有輸入都經過驗證",
            "☐ 使用參數化查詢防止 SQL 注入",
            "☐ 實現路徑規範化和驗證",
            "☐ 限制允許的模組和函數",
            "☐ 設置資源限制（超時、內存等）",
            "☐ 實現錯誤處理，避免信息洩露",
            "☐ 使用最小權限原則",
            "☐ 加密敏感數據",
            "☐ 實現審計日誌"
        ],

        "配置階段": [
            "☐ 使用環境變數存儲憑證",
            "☐ 配置防火牆規則",
            "☐ 啟用 HTTPS（如使用 HTTP 傳輸）",
            "☐ 設置速率限制",
            "☐ 配置日誌輪換",
            "☐ 限制服務器監聽地址",
            "☐ 使用專用服務賬戶"
        ],

        "運行階段": [
            "☐ 監控異常活動",
            "☐ 定期審查日誌",
            "☐ 及時更新依賴包",
            "☐ 執行安全掃描",
            "☐ 測試災難恢復流程",
            "☐ 定期輪換憑證"
        ]
    }


# ============================================================================
# 主程式示例
# ============================================================================

def main():
    """主程式：安全最佳實踐示例"""

    print("=" * 70)
    print("MCP 安全最佳實踐")
    print("=" * 70)

    # 1. 威脅模型
    print("\n【示例 1：安全威脅】")
    for threat, details in list(SecurityThreatModel.THREATS.items())[:2]:
        print(f"\n{threat} ({details['風險等級']})")
        print(f"  描述: {details['描述']}")
        print(f"  防護措施:")
        for measure in details['防護'][:2]:
            print(f"    • {measure}")

    # 2. 輸入驗證
    print("\n【示例 2：輸入驗證】")
    validator = InputValidator()

    # 測試路徑驗證
    valid, error = validator.validate_path(
        "/home/user/documents/file.txt",
        allowed_directories=["/home/user/documents"]
    )
    print(f"路徑驗證: {'✓' if valid else '✗'} {error or ''}")

    # 測試代碼安全性
    test_code = "import math\nresult = math.sqrt(16)"
    safe, issues = validator.validate_code_safety(test_code)
    print(f"代碼安全: {'✓' if safe else '✗'}")
    if issues:
        for issue in issues:
            print(f"  • {issue}")

    # 3. 訪問控制
    print("\n【示例 3：訪問控制】")
    acl = AccessControlList()

    acl.grant("user1", "/data/*", {Permission.READ, Permission.WRITE})
    acl.grant("user2", "/data/*", {Permission.READ})

    print(f"user1 讀取 /data/file.txt: {acl.check('user1', '/data/file.txt', Permission.READ)}")
    print(f"user2 寫入 /data/file.txt: {acl.check('user2', '/data/file.txt', Permission.WRITE)}")

    # 4. 憑證管理
    print("\n【示例 4：憑證管理】")
    cred_mgr = CredentialManager()

    api_key = cred_mgr.generate_api_key()
    print(f"生成 API 密鑰: {cred_mgr.mask_sensitive_data(api_key)}")

    # 5. 安全檢查清單
    print("\n【示例 5：安全檢查清單】")
    for phase, items in list(SecurityChecklist.CHECKLIST.items())[:2]:
        print(f"\n{phase}:")
        for item in items[:3]:
            print(f"  {item}")

    print("\n" + "=" * 70)
    print("下一步：查看 12_生產部署.py 學習生產環境部署")
    print("=" * 70)


if __name__ == "__main__":
    main()
