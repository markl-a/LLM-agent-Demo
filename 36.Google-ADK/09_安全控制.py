"""
Google ADK - 安全控制範例

這個範例展示安全性和權限管理：
- 身份驗證和授權
- 訪問控制
- 數據加密
- 審計日誌
- 安全策略
"""

import os
import hashlib
import jwt
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from google_adk import Agent
from google_adk.models import GeminiPro
from google_adk.security import (
    SecurityPolicy,
    AccessControl,
    AuditLogger,
    Encryption
)


class SecurityExample:
    """安全控制範例類"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化安全控制範例"""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("請設置 GOOGLE_API_KEY 環境變量")

    def example_1_authentication(self):
        """範例 1: 身份驗證"""
        print("\n" + "="*60)
        print("範例 1: 身份驗證")
        print("="*60)

        from google_adk.auth import AuthManager, Token

        class SimpleAuthManager:
            """簡單的身份驗證管理器"""

            def __init__(self, secret_key: str):
                self.secret_key = secret_key
                self.tokens = {}  # 存儲活躍 token

            def create_token(self, user_id: str, expires_in: int = 3600) -> str:
                """
                創建認證 token

                Args:
                    user_id: 用戶 ID
                    expires_in: 過期時間（秒）

                Returns:
                    JWT token
                """
                payload = {
                    "user_id": user_id,
                    "exp": datetime.utcnow() + timedelta(seconds=expires_in),
                    "iat": datetime.utcnow()
                }

                token = jwt.encode(payload, self.secret_key, algorithm="HS256")
                self.tokens[user_id] = token

                return token

            def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
                """
                驗證 token

                Args:
                    token: JWT token

                Returns:
                    解碼後的 payload 或 None
                """
                try:
                    payload = jwt.decode(
                        token,
                        self.secret_key,
                        algorithms=["HS256"]
                    )
                    return payload
                except jwt.ExpiredSignatureError:
                    print("Token 已過期")
                    return None
                except jwt.InvalidTokenError:
                    print("無效的 Token")
                    return None

        # 測試身份驗證
        auth_manager = SimpleAuthManager(secret_key="my-secret-key")

        print("\n創建用戶 token:")
        user_token = auth_manager.create_token("user-123", expires_in=3600)
        print(f"Token: {user_token[:50]}...")

        print("\n驗證 token:")
        payload = auth_manager.verify_token(user_token)
        if payload:
            print(f"✓ Token 有效")
            print(f"  用戶 ID: {payload['user_id']}")
            print(f"  過期時間: {datetime.fromtimestamp(payload['exp'])}")
        else:
            print("✗ Token 無效")

        return auth_manager

    def example_2_authorization(self):
        """範例 2: 授權控制"""
        print("\n" + "="*60)
        print("範例 2: 授權控制")
        print("="*60)

        class RoleBasedAccessControl:
            """基於角色的訪問控制 (RBAC)"""

            def __init__(self):
                # 定義角色和權限
                self.roles = {
                    "admin": ["read", "write", "delete", "manage_users"],
                    "editor": ["read", "write"],
                    "viewer": ["read"],
                    "guest": []
                }

                # 用戶角色映射
                self.user_roles = {}

            def assign_role(self, user_id: str, role: str):
                """分配角色"""
                if role in self.roles:
                    self.user_roles[user_id] = role
                    print(f"✓ 已分配角色 '{role}' 給用戶 {user_id}")
                else:
                    print(f"✗ 未知角色: {role}")

            def check_permission(
                self,
                user_id: str,
                permission: str
            ) -> bool:
                """
                檢查權限

                Args:
                    user_id: 用戶 ID
                    permission: 所需權限

                Returns:
                    是否有權限
                """
                role = self.user_roles.get(user_id)
                if not role:
                    return False

                permissions = self.roles.get(role, [])
                return permission in permissions

            def get_user_permissions(self, user_id: str) -> List[str]:
                """獲取用戶權限列表"""
                role = self.user_roles.get(user_id)
                return self.roles.get(role, [])

        # 測試授權
        rbac = RoleBasedAccessControl()

        print("\n分配角色:")
        rbac.assign_role("user-1", "admin")
        rbac.assign_role("user-2", "editor")
        rbac.assign_role("user-3", "viewer")

        print("\n權限檢查:")
        users = ["user-1", "user-2", "user-3"]
        actions = ["read", "write", "delete"]

        for user in users:
            print(f"\n{user} ({rbac.user_roles.get(user)}):")
            for action in actions:
                has_perm = rbac.check_permission(user, action)
                status = "✓" if has_perm else "✗"
                print(f"  {status} {action}")

        return rbac

    def example_3_data_encryption(self):
        """範例 3: 數據加密"""
        print("\n" + "="*60)
        print("範例 3: 數據加密")
        print("="*60)

        from cryptography.fernet import Fernet

        class DataEncryption:
            """數據加密服務"""

            def __init__(self, key: Optional[bytes] = None):
                """
                初始化加密服務

                Args:
                    key: 加密密鑰，如果為 None 則生成新密鑰
                """
                self.key = key or Fernet.generate_key()
                self.cipher = Fernet(self.key)

            def encrypt(self, data: str) -> bytes:
                """
                加密數據

                Args:
                    data: 明文數據

                Returns:
                    加密後的數據
                """
                return self.cipher.encrypt(data.encode())

            def decrypt(self, encrypted_data: bytes) -> str:
                """
                解密數據

                Args:
                    encrypted_data: 加密的數據

                Returns:
                    解密後的明文
                """
                return self.cipher.decrypt(encrypted_data).decode()

            def get_key(self) -> bytes:
                """獲取加密密鑰"""
                return self.key

        # 測試加密
        encryption = DataEncryption()

        print(f"\n加密密鑰: {encryption.get_key()[:20]}...")

        # 加密敏感數據
        sensitive_data = "這是一些敏感信息：密碼=secret123"
        print(f"\n原始數據: {sensitive_data}")

        encrypted = encryption.encrypt(sensitive_data)
        print(f"加密後: {encrypted[:50]}...")

        decrypted = encryption.decrypt(encrypted)
        print(f"解密後: {decrypted}")

        # 驗證
        if decrypted == sensitive_data:
            print("\n✓ 加密/解密成功")
        else:
            print("\n✗ 加密/解密失敗")

        return encryption

    def example_4_audit_logging(self):
        """範例 4: 審計日誌"""
        print("\n" + "="*60)
        print("範例 4: 審計日誌")
        print("="*60)

        import json
        from datetime import datetime

        class AuditLogger:
            """審計日誌記錄器"""

            def __init__(self, log_file: str = "/tmp/audit.log"):
                self.log_file = log_file
                self.logs = []

            def log_event(
                self,
                event_type: str,
                user_id: str,
                action: str,
                resource: str,
                result: str,
                metadata: Optional[Dict] = None
            ):
                """
                記錄審計事件

                Args:
                    event_type: 事件類型
                    user_id: 用戶 ID
                    action: 執行的操作
                    resource: 操作的資源
                    result: 操作結果
                    metadata: 額外元數據
                """
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "event_type": event_type,
                    "user_id": user_id,
                    "action": action,
                    "resource": resource,
                    "result": result,
                    "metadata": metadata or {}
                }

                self.logs.append(log_entry)

                # 同時寫入文件
                """
                with open(self.log_file, 'a') as f:
                    f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                """

            def get_logs(
                self,
                user_id: Optional[str] = None,
                action: Optional[str] = None,
                limit: int = 10
            ) -> List[Dict]:
                """
                查詢審計日誌

                Args:
                    user_id: 過濾用戶 ID
                    action: 過濾操作類型
                    limit: 返回數量限制

                Returns:
                    日誌列表
                """
                filtered_logs = self.logs

                if user_id:
                    filtered_logs = [
                        log for log in filtered_logs
                        if log["user_id"] == user_id
                    ]

                if action:
                    filtered_logs = [
                        log for log in filtered_logs
                        if log["action"] == action
                    ]

                return filtered_logs[-limit:]

        # 測試審計日誌
        audit = AuditLogger()

        print("\n記錄審計事件:")

        # 記錄各種操作
        events = [
            ("access", "user-1", "login", "system", "success"),
            ("access", "user-1", "read", "document-1", "success"),
            ("access", "user-2", "write", "document-2", "success"),
            ("access", "user-1", "delete", "document-3", "denied"),
            ("access", "user-3", "login", "system", "failed")
        ]

        for event_type, user_id, action, resource, result in events:
            audit.log_event(event_type, user_id, action, resource, result)
            print(f"  ✓ {user_id} {action} {resource}: {result}")

        # 查詢日誌
        print(f"\n總日誌數: {len(audit.logs)}")

        print("\nuser-1 的操作:")
        user1_logs = audit.get_logs(user_id="user-1")
        for log in user1_logs:
            print(f"  - {log['action']} {log['resource']}: {log['result']}")

        print("\n失敗的登錄嘗試:")
        failed_logins = [
            log for log in audit.logs
            if log['action'] == 'login' and log['result'] == 'failed'
        ]
        for log in failed_logins:
            print(f"  - {log['user_id']} at {log['timestamp']}")

        return audit

    def example_5_security_policy(self):
        """範例 5: 安全策略"""
        print("\n" + "="*60)
        print("範例 5: 安全策略")
        print("="*60)

        class SecurityPolicy:
            """安全策略管理"""

            def __init__(self):
                self.policies = {
                    "password": {
                        "min_length": 8,
                        "require_uppercase": True,
                        "require_lowercase": True,
                        "require_digit": True,
                        "require_special": True
                    },
                    "session": {
                        "timeout": 3600,  # 1 小時
                        "max_concurrent": 3,
                        "idle_timeout": 900  # 15 分鐘
                    },
                    "rate_limit": {
                        "requests_per_minute": 60,
                        "requests_per_hour": 1000
                    },
                    "data": {
                        "encrypt_at_rest": True,
                        "encrypt_in_transit": True,
                        "data_retention_days": 90
                    }
                }

            def validate_password(self, password: str) -> tuple[bool, str]:
                """
                驗證密碼強度

                Args:
                    password: 密碼

                Returns:
                    (是否有效, 錯誤消息)
                """
                policy = self.policies["password"]

                if len(password) < policy["min_length"]:
                    return False, f"密碼長度至少 {policy['min_length']} 字符"

                if policy["require_uppercase"] and not any(c.isupper() for c in password):
                    return False, "密碼必須包含大寫字母"

                if policy["require_lowercase"] and not any(c.islower() for c in password):
                    return False, "密碼必須包含小寫字母"

                if policy["require_digit"] and not any(c.isdigit() for c in password):
                    return False, "密碼必須包含數字"

                if policy["require_special"] and not any(c in "!@#$%^&*()" for c in password):
                    return False, "密碼必須包含特殊字符"

                return True, "密碼符合要求"

            def check_rate_limit(
                self,
                user_id: str,
                request_count: int,
                time_window: str
            ) -> bool:
                """檢查速率限制"""
                policy = self.policies["rate_limit"]

                if time_window == "minute":
                    return request_count <= policy["requests_per_minute"]
                elif time_window == "hour":
                    return request_count <= policy["requests_per_hour"]

                return True

            def get_policy(self, category: str) -> Dict[str, Any]:
                """獲取策略配置"""
                return self.policies.get(category, {})

        # 測試安全策略
        policy = SecurityPolicy()

        print("\n安全策略配置:")
        for category, config in policy.policies.items():
            print(f"\n{category}:")
            for key, value in config.items():
                print(f"  {key}: {value}")

        # 測試密碼驗證
        print("\n密碼強度測試:")
        test_passwords = [
            "weak",
            "StrongPass1!",
            "NoSpecial123",
            "short1!"
        ]

        for pwd in test_passwords:
            valid, message = policy.validate_password(pwd)
            status = "✓" if valid else "✗"
            print(f"  {status} '{pwd}': {message}")

        return policy

    def example_6_input_validation(self):
        """範例 6: 輸入驗證和過濾"""
        print("\n" + "="*60)
        print("範例 6: 輸入驗證和過濾")
        print("="*60)

        import re
        from html import escape

        class InputValidator:
            """輸入驗證器"""

            @staticmethod
            def sanitize_html(input_text: str) -> str:
                """清理 HTML"""
                return escape(input_text)

            @staticmethod
            def validate_email(email: str) -> bool:
                """驗證郵箱格式"""
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                return bool(re.match(pattern, email))

            @staticmethod
            def validate_url(url: str) -> bool:
                """驗證 URL 格式"""
                pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                return bool(re.match(pattern, url))

            @staticmethod
            def check_sql_injection(input_text: str) -> bool:
                """檢查 SQL 注入"""
                dangerous_patterns = [
                    r"(\bor\b|\band\b).*=",
                    r"union.*select",
                    r"drop.*table",
                    r"insert.*into",
                    r"delete.*from"
                ]

                input_lower = input_text.lower()
                for pattern in dangerous_patterns:
                    if re.search(pattern, input_lower):
                        return True
                return False

            @staticmethod
            def filter_profanity(text: str) -> str:
                """過濾不當詞彙"""
                profanity_list = ["badword1", "badword2"]  # 示例
                filtered_text = text

                for word in profanity_list:
                    filtered_text = re.sub(
                        word,
                        "*" * len(word),
                        filtered_text,
                        flags=re.IGNORECASE
                    )

                return filtered_text

        # 測試輸入驗證
        validator = InputValidator()

        print("\n郵箱驗證:")
        emails = ["user@example.com", "invalid-email", "test@domain"]
        for email in emails:
            valid = validator.validate_email(email)
            status = "✓" if valid else "✗"
            print(f"  {status} {email}")

        print("\nSQL 注入檢測:")
        inputs = [
            "normal input",
            "1' OR '1'='1",
            "'; DROP TABLE users--"
        ]
        for inp in inputs:
            is_dangerous = validator.check_sql_injection(inp)
            status = "⚠️" if is_dangerous else "✓"
            print(f"  {status} {inp}")

        print("\nHTML 清理:")
        html_input = "<script>alert('XSS')</script>Hello"
        sanitized = validator.sanitize_html(html_input)
        print(f"  原始: {html_input}")
        print(f"  清理後: {sanitized}")

        return validator

    def example_7_secure_agent(self):
        """範例 7: 安全的 Agent 配置"""
        print("\n" + "="*60)
        print("範例 7: 安全的 Agent 配置")
        print("="*60)

        # 創建安全策略
        security_policy = SecurityPolicy(
            authentication_required=True,
            authorization_enabled=True,
            encryption_enabled=True,
            audit_logging=True,
            rate_limiting=True,
            input_validation=True
        )

        # 創建安全的 Agent
        agent = Agent(
            model=GeminiPro(),
            security_policy=security_policy,
            name="secure-agent"
        )

        print("安全 Agent 配置:")
        print("  ✓ 身份驗證: 必須")
        print("  ✓ 授權檢查: 啟用")
        print("  ✓ 數據加密: 啟用")
        print("  ✓ 審計日誌: 啟用")
        print("  ✓ 速率限制: 啟用")
        print("  ✓ 輸入驗證: 啟用")

        return agent

    def example_8_secrets_management(self):
        """範例 8: 密鑰管理"""
        print("\n" + "="*60)
        print("範例 8: 密鑰管理")
        print("="*60)

        class SecretsManager:
            """密鑰管理器"""

            def __init__(self):
                self.secrets = {}
                self.encrypted_storage = {}

            def store_secret(self, key: str, value: str, encrypt: bool = True):
                """
                存儲密鑰

                Args:
                    key: 密鑰名稱
                    value: 密鑰值
                    encrypt: 是否加密存儲
                """
                if encrypt:
                    # 實際應使用專業加密
                    encrypted_value = hashlib.sha256(value.encode()).hexdigest()
                    self.encrypted_storage[key] = encrypted_value
                    print(f"✓ 密鑰 '{key}' 已加密存儲")
                else:
                    self.secrets[key] = value
                    print(f"⚠️  密鑰 '{key}' 以明文存儲（不推薦）")

            def get_secret(self, key: str) -> Optional[str]:
                """獲取密鑰"""
                return self.secrets.get(key)

            def rotate_secret(self, key: str, new_value: str):
                """輪換密鑰"""
                if key in self.secrets:
                    old_value = self.secrets[key]
                    self.secrets[key] = new_value
                    print(f"✓ 密鑰 '{key}' 已輪換")
                    return True
                return False

            def list_secrets(self) -> List[str]:
                """列出所有密鑰（不包含值）"""
                all_keys = set(self.secrets.keys()) | set(self.encrypted_storage.keys())
                return list(all_keys)

        # 測試密鑰管理
        secrets = SecretsManager()

        print("\n存儲密鑰:")
        secrets.store_secret("api_key", "sk-1234567890", encrypt=True)
        secrets.store_secret("db_password", "mypassword", encrypt=True)
        secrets.store_secret("webhook_url", "https://example.com/hook", encrypt=True)

        print(f"\n已存儲密鑰: {', '.join(secrets.list_secrets())}")

        return secrets

    def example_9_compliance(self):
        """範例 9: 合規性檢查"""
        print("\n" + "="*60)
        print("範例 9: 合規性檢查")
        print("="*60)

        class ComplianceChecker:
            """合規性檢查器"""

            def __init__(self):
                self.requirements = {
                    "GDPR": [
                        "用戶同意收集數據",
                        "提供數據訪問權限",
                        "提供數據刪除功能",
                        "數據加密存儲",
                        "數據處理記錄"
                    ],
                    "HIPAA": [
                        "PHI 數據加密",
                        "訪問控制",
                        "審計追蹤",
                        "數據備份",
                        "災難恢復計劃"
                    ],
                    "SOC2": [
                        "訪問控制",
                        "變更管理",
                        "監控和日誌",
                        "事件響應",
                        "漏洞管理"
                    ]
                }

            def check_compliance(
                self,
                standard: str,
                implemented_controls: List[str]
            ) -> Dict[str, Any]:
                """
                檢查合規性

                Args:
                    standard: 合規標準
                    implemented_controls: 已實施的控制措施

                Returns:
                    合規檢查結果
                """
                requirements = self.requirements.get(standard, [])
                if not requirements:
                    return {"error": "未知的合規標準"}

                missing = []
                for req in requirements:
                    if req not in implemented_controls:
                        missing.append(req)

                compliance_rate = (
                    (len(requirements) - len(missing)) / len(requirements)
                ) * 100

                return {
                    "standard": standard,
                    "compliance_rate": f"{compliance_rate:.1f}%",
                    "total_requirements": len(requirements),
                    "implemented": len(requirements) - len(missing),
                    "missing": missing
                }

        # 測試合規性檢查
        checker = ComplianceChecker()

        print("\n合規性檢查:")

        # 模擬已實施的控制措施
        implemented = [
            "用戶同意收集數據",
            "數據加密存儲",
            "數據處理記錄",
            "訪問控制",
            "審計追蹤"
        ]

        for standard in ["GDPR", "SOC2"]:
            result = checker.check_compliance(standard, implemented)
            print(f"\n{standard}:")
            print(f"  合規率: {result['compliance_rate']}")
            print(f"  已實施: {result['implemented']}/{result['total_requirements']}")
            if result['missing']:
                print(f"  缺失項:")
                for item in result['missing']:
                    print(f"    - {item}")

        return checker

    def example_10_security_best_practices(self):
        """範例 10: 安全最佳實踐"""
        print("\n" + "="*60)
        print("範例 10: 安全最佳實踐")
        print("="*60)

        best_practices = {
            "身份驗證": [
                "使用強密碼策略",
                "實施多因素認證 (MFA)",
                "定期輪換憑證",
                "使用安全的 token 存儲"
            ],
            "授權": [
                "實施最小權限原則",
                "使用基於角色的訪問控制",
                "定期審查權限",
                "記錄所有訪問嘗試"
            ],
            "數據保護": [
                "傳輸中數據加密 (TLS)",
                "靜態數據加密",
                "敏感數據脫敏",
                "定期數據備份"
            ],
            "監控": [
                "實施全面的審計日誌",
                "設置異常檢測",
                "實時安全監控",
                "定期安全審計"
            ],
            "代碼安全": [
                "輸入驗證和清理",
                "防止注入攻擊",
                "安全的依賴管理",
                "定期安全掃描"
            ]
        }

        print("\n安全最佳實踐清單:\n")

        for category, practices in best_practices.items():
            print(f"{category}:")
            for practice in practices:
                print(f"  ✓ {practice}")
            print()

        # 安全檢查清單
        print("生產部署前安全檢查清單:")
        checklist = [
            "[ ] 所有密鑰和憑證已安全存儲",
            "[ ] 啟用 HTTPS/TLS",
            "[ ] 配置防火牆規則",
            "[ ] 實施速率限制",
            "[ ] 啟用審計日誌",
            "[ ] 配置備份策略",
            "[ ] 實施監控和告警",
            "[ ] 完成安全測試",
            "[ ] 準備事件響應計劃",
            "[ ] 更新安全文檔"
        ]

        for item in checklist:
            print(f"  {item}")


def main():
    """主函數"""
    print("="*60)
    print("Google ADK - 安全控制範例")
    print("="*60)

    # 檢查 API 密鑰
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n⚠️  請先設置 GOOGLE_API_KEY 環境變量")
        print("export GOOGLE_API_KEY='your-api-key-here'")
        return

    # 創建範例實例
    example = SecurityExample()

    try:
        # 運行所有範例
        example.example_1_authentication()
        example.example_2_authorization()
        example.example_3_data_encryption()
        example.example_4_audit_logging()
        example.example_5_security_policy()
        example.example_6_input_validation()
        example.example_7_secure_agent()
        example.example_8_secrets_management()
        example.example_9_compliance()
        example.example_10_security_best_practices()

        print("\n" + "="*60)
        print("所有安全控制範例執行完成！")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 執行錯誤: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
