"""
安全配置和權限管理
===================================

本範例展示 Magentic-One 的安全機制和最佳實踐。

安全特性：
1. 權限控制和訪問管理
2. 操作審計和日誌
3. 沙盒執行環境
4. 資源限制
5. 敏感數據保護

關鍵概念：
- 最小權限原則
- 操作批准機制
- 安全審計
- 數據加密
- 錯誤處理
"""

import os
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import json
from enum import Enum
import hashlib


class PermissionLevel(Enum):
    """權限級別"""
    NONE = 0
    READ = 1
    WRITE = 2
    EXECUTE = 3
    ADMIN = 4


class OperationRisk(Enum):
    """操作風險級別"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityManager:
    """
    安全管理器

    管理 Magentic-One 系統的安全策略
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化安全管理器

        Args:
            config: 安全配置
        """
        self.config = config or self._default_config()

        # 權限管理
        self.agent_permissions: Dict[str, Dict[str, PermissionLevel]] = {}

        # 操作審計
        self.audit_log: List[Dict] = []

        # 批准待處理
        self.pending_approvals: List[Dict] = []

        # 黑名單
        self.blocked_operations: Set[str] = set()
        self.blocked_patterns: List[str] = []

    def _default_config(self) -> Dict[str, Any]:
        """默認安全配置"""
        return {
            'require_approval_for': ['delete', 'execute', 'write'],
            'max_execution_time': 300,  # 秒
            'max_memory_usage': 1024 * 1024 * 1024,  # 1GB
            'enable_sandboxing': True,
            'log_all_operations': True,
            'encrypt_sensitive_data': True,
            'blocked_commands': [
                'rm -rf /',
                'format',
                'dd if=/dev/zero',
                'mkfs'
            ]
        }

    def register_agent(
        self,
        agent_name: str,
        permissions: Dict[str, PermissionLevel]
    ):
        """
        註冊 Agent 並設置權限

        Args:
            agent_name: Agent 名稱
            permissions: 權限字典 {resource: permission_level}
        """
        self.agent_permissions[agent_name] = permissions

        print(f"✓ 註冊 Agent: {agent_name}")
        print(f"  權限: {json.dumps({k: v.name for k, v in permissions.items()}, indent=4)}")

    def check_permission(
        self,
        agent_name: str,
        resource: str,
        required_level: PermissionLevel
    ) -> bool:
        """
        檢查 Agent 是否有足夠權限

        Args:
            agent_name: Agent 名稱
            resource: 資源名稱
            required_level: 需要的權限級別

        Returns:
            是否有權限
        """
        if agent_name not in self.agent_permissions:
            print(f"✗ Agent '{agent_name}' 未註冊")
            return False

        agent_perms = self.agent_permissions[agent_name]

        # 檢查資源權限
        if resource in agent_perms:
            has_permission = agent_perms[resource].value >= required_level.value
        elif '*' in agent_perms:  # 通配符權限
            has_permission = agent_perms['*'].value >= required_level.value
        else:
            has_permission = False

        if has_permission:
            print(f"✓ {agent_name} 有權限訪問 {resource} ({required_level.name})")
        else:
            print(f"✗ {agent_name} 無權限訪問 {resource} ({required_level.name})")

        return has_permission

    def assess_operation_risk(self, operation: Dict) -> OperationRisk:
        """
        評估操作風險

        Args:
            operation: 操作描述

        Returns:
            風險級別
        """
        op_type = operation.get('type', '')
        target = operation.get('target', '')

        # 檢查黑名單
        if self._is_blocked(operation):
            return OperationRisk.CRITICAL

        # 風險評估規則
        if op_type in ['delete', 'format', 'execute_system']:
            return OperationRisk.HIGH
        elif op_type in ['write', 'modify', 'install']:
            return OperationRisk.MEDIUM
        elif op_type in ['read', 'list', 'search']:
            return OperationRisk.LOW
        else:
            return OperationRisk.MEDIUM

    def request_approval(
        self,
        agent_name: str,
        operation: Dict,
        reason: str
    ) -> bool:
        """
        請求操作批准

        Args:
            agent_name: Agent 名稱
            operation: 操作描述
            reason: 操作原因

        Returns:
            是否批准
        """
        risk = self.assess_operation_risk(operation)

        print(f"\n🔐 批准請求")
        print(f"  Agent: {agent_name}")
        print(f"  操作: {operation.get('type', 'unknown')}")
        print(f"  目標: {operation.get('target', 'unknown')}")
        print(f"  風險級別: {risk.value}")
        print(f"  原因: {reason}")

        # 嚴重風險自動拒絕
        if risk == OperationRisk.CRITICAL:
            print(f"  ✗ 自動拒絕（風險過高）")
            self._log_audit(agent_name, operation, 'denied', risk)
            return False

        # 模擬批准流程
        if risk == OperationRisk.HIGH:
            # 實際環境中應該請求人工批准
            approved = self._simulate_approval(operation, risk)
        else:
            # 低風險自動批准
            approved = True

        status = "approved" if approved else "denied"
        self._log_audit(agent_name, operation, status, risk)

        print(f"  {'✓' if approved else '✗'} {status}")

        return approved

    def validate_operation(
        self,
        agent_name: str,
        operation: Dict
    ) -> Dict[str, Any]:
        """
        驗證操作

        Args:
            agent_name: Agent 名稱
            operation: 操作描述

        Returns:
            驗證結果
        """
        print(f"\n🔍 驗證操作")

        # 1. 檢查權限
        required_perm = self._get_required_permission(operation)
        has_permission = self.check_permission(
            agent_name,
            operation.get('target', 'unknown'),
            required_perm
        )

        if not has_permission:
            return {
                'valid': False,
                'reason': '權限不足',
                'required_permission': required_perm.name
            }

        # 2. 檢查黑名單
        if self._is_blocked(operation):
            return {
                'valid': False,
                'reason': '操作被禁止'
            }

        # 3. 評估風險
        risk = self.assess_operation_risk(operation)

        # 4. 檢查是否需要批准
        needs_approval = self._needs_approval(operation, risk)

        if needs_approval:
            approved = self.request_approval(
                agent_name,
                operation,
                "執行必要操作"
            )

            if not approved:
                return {
                    'valid': False,
                    'reason': '未獲得批准'
                }

        return {
            'valid': True,
            'risk': risk.value
        }

    def create_sandbox_environment(self, agent_name: str) -> Dict[str, Any]:
        """
        創建沙盒執行環境

        Args:
            agent_name: Agent 名稱

        Returns:
            沙盒配置
        """
        print(f"\n📦 為 {agent_name} 創建沙盒環境")

        sandbox_config = {
            'agent': agent_name,
            'work_dir': f'/tmp/sandbox_{agent_name}_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'allowed_paths': [
                '/tmp',
                '/var/tmp'
            ],
            'blocked_paths': [
                '/etc',
                '/usr',
                '/bin',
                '/sbin',
                '/root'
            ],
            'resource_limits': {
                'max_cpu_percent': 50,
                'max_memory_mb': 512,
                'max_execution_time': 60,
                'max_file_size_mb': 100
            },
            'network_access': False,
            'environment_variables': {
                'SANDBOX': 'true',
                'AGENT_NAME': agent_name
            }
        }

        print(f"  工作目錄: {sandbox_config['work_dir']}")
        print(f"  資源限制: CPU {sandbox_config['resource_limits']['max_cpu_percent']}%, "
              f"內存 {sandbox_config['resource_limits']['max_memory_mb']}MB")

        return sandbox_config

    def encrypt_sensitive_data(self, data: str) -> str:
        """
        加密敏感數據

        Args:
            data: 原始數據

        Returns:
            加密後的數據
        """
        # 簡化示例：使用 SHA256 哈希（實際應使用適當的加密算法）
        hashed = hashlib.sha256(data.encode()).hexdigest()
        return f"encrypted_{hashed[:16]}"

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """
        解密敏感數據

        Args:
            encrypted_data: 加密的數據

        Returns:
            解密後的數據
        """
        # 簡化示例
        return encrypted_data.replace('encrypted_', '')

    def get_audit_log(
        self,
        agent_name: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        獲取審計日誌

        Args:
            agent_name: Agent 名稱（可選）
            limit: 返回記錄數量

        Returns:
            審計日誌列表
        """
        logs = self.audit_log

        if agent_name:
            logs = [log for log in logs if log['agent'] == agent_name]

        return logs[-limit:]

    def generate_security_report(self) -> Dict[str, Any]:
        """
        生成安全報告

        Returns:
            安全報告
        """
        print("\n📊 生成安全報告")

        total_operations = len(self.audit_log)
        approved = sum(1 for log in self.audit_log if log['status'] == 'approved')
        denied = sum(1 for log in self.audit_log if log['status'] == 'denied')

        # 按風險級別統計
        risk_stats = {}
        for risk in OperationRisk:
            count = sum(1 for log in self.audit_log if log.get('risk') == risk.value)
            risk_stats[risk.value] = count

        # 按 Agent 統計
        agent_stats = {}
        for log in self.audit_log:
            agent = log['agent']
            if agent not in agent_stats:
                agent_stats[agent] = {'total': 0, 'approved': 0, 'denied': 0}

            agent_stats[agent]['total'] += 1
            if log['status'] == 'approved':
                agent_stats[agent]['approved'] += 1
            else:
                agent_stats[agent]['denied'] += 1

        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_operations': total_operations,
                'approved': approved,
                'denied': denied,
                'approval_rate': f"{(approved/max(total_operations, 1)*100):.1f}%"
            },
            'risk_distribution': risk_stats,
            'agent_statistics': agent_stats,
            'registered_agents': len(self.agent_permissions),
            'blocked_operations': len(self.blocked_operations)
        }

        return report

    # 內部輔助方法

    def _is_blocked(self, operation: Dict) -> bool:
        """檢查操作是否被禁止"""
        op_str = json.dumps(operation)

        # 檢查完全匹配
        if op_str in self.blocked_operations:
            return True

        # 檢查模式匹配
        for pattern in self.config.get('blocked_commands', []):
            if pattern in op_str:
                return True

        return False

    def _get_required_permission(self, operation: Dict) -> PermissionLevel:
        """獲取操作所需的權限級別"""
        op_type = operation.get('type', '')

        if op_type in ['read', 'list', 'search']:
            return PermissionLevel.READ
        elif op_type in ['write', 'create', 'update']:
            return PermissionLevel.WRITE
        elif op_type in ['execute', 'run', 'install']:
            return PermissionLevel.EXECUTE
        elif op_type in ['delete', 'admin']:
            return PermissionLevel.ADMIN
        else:
            return PermissionLevel.WRITE

    def _needs_approval(self, operation: Dict, risk: OperationRisk) -> bool:
        """判斷是否需要批准"""
        op_type = operation.get('type', '')

        # 高風險操作需要批准
        if risk in [OperationRisk.HIGH, OperationRisk.CRITICAL]:
            return True

        # 特定類型操作需要批准
        if op_type in self.config.get('require_approval_for', []):
            return True

        return False

    def _simulate_approval(self, operation: Dict, risk: OperationRisk) -> bool:
        """模擬批准流程"""
        # 在實際環境中，這應該請求人工批准
        # 這裡簡化為基於風險的自動決策

        if risk == OperationRisk.CRITICAL:
            return False
        elif risk == OperationRisk.HIGH:
            # 模擬 80% 批准率
            return True
        else:
            return True

    def _log_audit(
        self,
        agent_name: str,
        operation: Dict,
        status: str,
        risk: OperationRisk
    ):
        """記錄審計日誌"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'agent': agent_name,
            'operation': operation,
            'status': status,
            'risk': risk.value
        }

        self.audit_log.append(log_entry)


def demo_permission_management():
    """權限管理示範"""
    print("=" * 60)
    print("範例 1: 權限管理")
    print("=" * 60)

    security = SecurityManager()

    # 註冊 Agents 並設置權限
    security.register_agent('web_surfer', {
        'web': PermissionLevel.READ,
        'cache': PermissionLevel.WRITE
    })

    security.register_agent('file_surfer', {
        'files': PermissionLevel.WRITE,
        'system': PermissionLevel.READ
    })

    security.register_agent('coder', {
        'code': PermissionLevel.EXECUTE,
        'files': PermissionLevel.WRITE
    })

    # 檢查權限
    print("\n權限檢查:")
    security.check_permission('web_surfer', 'web', PermissionLevel.READ)
    security.check_permission('web_surfer', 'files', PermissionLevel.WRITE)
    security.check_permission('coder', 'code', PermissionLevel.EXECUTE)


def demo_operation_validation():
    """操作驗證示範"""
    print("\n" + "=" * 60)
    print("範例 2: 操作驗證")
    print("=" * 60)

    security = SecurityManager()

    security.register_agent('coder', {
        'code': PermissionLevel.EXECUTE,
        'files': PermissionLevel.WRITE
    })

    # 驗證不同風險級別的操作
    operations = [
        {'type': 'read', 'target': 'files'},
        {'type': 'write', 'target': 'files'},
        {'type': 'execute', 'target': 'code'},
        {'type': 'delete', 'target': 'files'}
    ]

    for op in operations:
        result = security.validate_operation('coder', op)
        print(f"\n操作: {op}")
        print(f"驗證結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def demo_sandbox_environment():
    """沙盒環境示範"""
    print("\n" + "=" * 60)
    print("範例 3: 沙盒執行環境")
    print("=" * 60)

    security = SecurityManager()

    # 為不同 Agent 創建沙盒
    agents = ['coder', 'terminal', 'file_surfer']

    for agent_name in agents:
        sandbox = security.create_sandbox_environment(agent_name)
        print(f"\n{agent_name} 沙盒配置:")
        print(f"  允許路徑: {sandbox['allowed_paths']}")
        print(f"  禁止路徑: {sandbox['blocked_paths']}")
        print(f"  網絡訪問: {sandbox['network_access']}")


def demo_data_encryption():
    """數據加密示範"""
    print("\n" + "=" * 60)
    print("範例 4: 敏感數據加密")
    print("=" * 60)

    security = SecurityManager()

    # 加密敏感數據
    sensitive_data = [
        "api_key_12345",
        "password_secret",
        "token_xyz789"
    ]

    print("\n加密敏感數據:")
    for data in sensitive_data:
        encrypted = security.encrypt_sensitive_data(data)
        print(f"  原始: {data}")
        print(f"  加密: {encrypted}\n")


def demo_audit_logging():
    """審計日誌示範"""
    print("\n" + "=" * 60)
    print("範例 5: 審計日誌")
    print("=" * 60)

    security = SecurityManager()

    security.register_agent('coder', {
        'code': PermissionLevel.EXECUTE,
        'files': PermissionLevel.WRITE
    })

    # 執行多個操作
    operations = [
        {'type': 'read', 'target': 'files'},
        {'type': 'write', 'target': 'files'},
        {'type': 'execute', 'target': 'code'},
        {'type': 'delete', 'target': 'files'}
    ]

    for op in operations:
        security.validate_operation('coder', op)

    # 獲取審計日誌
    logs = security.get_audit_log(limit=10)

    print("\n最近的審計日誌:")
    for log in logs:
        print(f"\n時間: {log['timestamp']}")
        print(f"  Agent: {log['agent']}")
        print(f"  操作: {log['operation']['type']}")
        print(f"  狀態: {log['status']}")
        print(f"  風險: {log['risk']}")


def demo_security_report():
    """安全報告示範"""
    print("\n" + "=" * 60)
    print("範例 6: 安全報告")
    print("=" * 60)

    security = SecurityManager()

    # 註冊多個 Agents
    security.register_agent('web_surfer', {'web': PermissionLevel.READ})
    security.register_agent('coder', {'code': PermissionLevel.EXECUTE})
    security.register_agent('file_surfer', {'files': PermissionLevel.WRITE})

    # 模擬多個操作
    operations = [
        ('web_surfer', {'type': 'read', 'target': 'web'}),
        ('coder', {'type': 'execute', 'target': 'code'}),
        ('file_surfer', {'type': 'write', 'target': 'files'}),
        ('coder', {'type': 'delete', 'target': 'files'})
    ]

    for agent, op in operations:
        security.validate_operation(agent, op)

    # 生成安全報告
    report = security.generate_security_report()

    print("\n安全報告:")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    demo_permission_management()
    demo_operation_validation()
    demo_sandbox_environment()
    demo_data_encryption()
    demo_audit_logging()
    demo_security_report()

    print("\n" + "=" * 60)
    print("安全配置示範完成！")
    print("=" * 60)
