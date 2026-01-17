"""
Letta 狀態序列化系統

本模組展示 Agent 狀態的序列化和反序列化：
1. 完整狀態導出
2. 增量狀態保存
3. 跨平台狀態遷移
4. 版本控制和兼容性
5. 壓縮和加密
6. 狀態恢復和驗證

實現 Agent 狀態的持久化和遷移。

作者：Letta 框架示例
日期：2025-01
"""

import os
import json
import pickle
import gzip
import hashlib
import base64
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field, asdict
from pathlib import Path
import copy


@dataclass
class AgentState:
    """Agent 完整狀態"""
    agent_id: str
    agent_name: str
    persona: str
    human: str
    core_memory: Dict[str, str]
    messages: List[Dict[str, Any]]
    archival_memory: List[Dict[str, Any]]
    tools: List[str]
    metadata: Dict[str, Any]
    version: str = "1.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class StateSnapshot:
    """狀態快照"""
    snapshot_id: str
    agent_id: str
    timestamp: str
    state_hash: str
    compressed: bool = False
    encrypted: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class StateSerializer:
    """
    狀態序列化器

    負責將 Agent 狀態序列化為不同格式。
    """

    def __init__(self):
        """初始化狀態序列化器"""
        print("狀態序列化器初始化完成")

    def to_json(self, state: AgentState, pretty: bool = True) -> str:
        """
        序列化為 JSON

        參數:
            state: Agent 狀態
            pretty: 是否格式化輸出

        返回:
            JSON 字符串
        """
        state_dict = asdict(state)

        if pretty:
            json_str = json.dumps(state_dict, indent=2, ensure_ascii=False)
        else:
            json_str = json.dumps(state_dict, ensure_ascii=False)

        print(f"\n[JSON 序列化] 大小: {len(json_str)} 字節")

        return json_str

    def from_json(self, json_str: str) -> AgentState:
        """
        從 JSON 反序列化

        參數:
            json_str: JSON 字符串

        返回:
            Agent 狀態
        """
        state_dict = json.loads(json_str)
        state = AgentState(**state_dict)

        print(f"\n[JSON 反序列化] Agent: {state.agent_name}")

        return state

    def to_pickle(self, state: AgentState) -> bytes:
        """
        序列化為 Pickle

        ⚠️ 安全警告：pickle 序列化已棄用，建議使用 to_json() 方法。
        pickle 存在遠程代碼執行 (RCE) 風險。

        參數:
            state: Agent 狀態

        返回:
            二進制數據
        """
        import warnings
        warnings.warn(
            "pickle serialization is deprecated due to security risks. "
            "Use to_json() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        pickle_data = pickle.dumps(state)

        print(f"\n[Pickle 序列化] ⚠️ 已棄用 - 大小: {len(pickle_data)} 字節")
        print("  建議使用 to_json() 方法替代")

        return pickle_data

    def from_pickle(self, pickle_data: bytes) -> AgentState:
        """
        從 Pickle 反序列化

        ⚠️ 安全警告：此方法存在嚴重的 RCE（遠程代碼執行）漏洞！
        pickle.loads() 可以執行任意代碼，切勿用於不信任的數據。
        請使用 from_json() 方法替代。

        參數:
            pickle_data: 二進制數據（僅接受可信來源）

        返回:
            Agent 狀態
        """
        import warnings
        warnings.warn(
            "SECURITY WARNING: pickle.loads() can execute arbitrary code. "
            "This method is deprecated. Use from_json() instead.",
            DeprecationWarning,
            stacklevel=2
        )

        # 安全提醒：僅在數據來源可信時使用
        print("\n⚠️ [安全警告] pickle 反序列化存在 RCE 風險！")
        print("  切勿用於不信任的數據來源，建議使用 from_json() 替代")

        state = pickle.loads(pickle_data)

        print(f"[Pickle 反序列化] Agent: {state.agent_name}")

        return state

    def to_dict(self, state: AgentState) -> Dict[str, Any]:
        """
        轉換為字典

        參數:
            state: Agent 狀態

        返回:
            字典
        """
        return asdict(state)

    def from_dict(self, state_dict: Dict[str, Any]) -> AgentState:
        """
        從字典創建

        參數:
            state_dict: 狀態字典

        返回:
            Agent 狀態
        """
        return AgentState(**state_dict)


class StateCompressor:
    """
    狀態壓縮器

    壓縮和解壓狀態數據。
    """

    def __init__(self):
        """初始化狀態壓縮器"""
        print("狀態壓縮器初始化完成")

    def compress(self, data: bytes) -> bytes:
        """
        壓縮數據

        參數:
            data: 原始數據

        返回:
            壓縮後的數據
        """
        compressed = gzip.compress(data)

        compression_ratio = len(compressed) / len(data)

        print(f"\n[壓縮] 原始: {len(data)} 字節 -> 壓縮: {len(compressed)} 字節")
        print(f"  壓縮率: {compression_ratio:.2%}")

        return compressed

    def decompress(self, compressed_data: bytes) -> bytes:
        """
        解壓數據

        參數:
            compressed_data: 壓縮數據

        返回:
            原始數據
        """
        data = gzip.decompress(compressed_data)

        print(f"\n[解壓] 壓縮: {len(compressed_data)} 字節 -> 原始: {len(data)} 字節")

        return data


class StateEncryptor:
    """
    狀態加密器

    加密和解密狀態數據（簡化實現）。
    """

    def __init__(self, key: Optional[str] = None):
        """
        初始化狀態加密器

        參數:
            key: 加密密鑰
        """
        self.key = key or "default_encryption_key"
        print("狀態加密器初始化完成")

    def encrypt(self, data: bytes) -> bytes:
        """
        加密數據（簡化實現）

        參數:
            data: 原始數據

        返回:
            加密後的數據
        """
        # 這是一個簡化的示例，實際應使用真正的加密算法
        # 例如 AES, Fernet 等

        # 使用 XOR 作為簡單示例（不安全，僅用於演示）
        key_bytes = self.key.encode()
        encrypted = bytearray()

        for i, byte in enumerate(data):
            encrypted.append(byte ^ key_bytes[i % len(key_bytes)])

        encrypted_data = bytes(encrypted)

        print(f"\n[加密] 原始: {len(data)} 字節 -> 加密: {len(encrypted_data)} 字節")

        return encrypted_data

    def decrypt(self, encrypted_data: bytes) -> bytes:
        """
        解密數據

        參數:
            encrypted_data: 加密數據

        返回:
            原始數據
        """
        # XOR 加密的特性：加密和解密使用相同操作
        decrypted = self.encrypt(encrypted_data)

        print(f"\n[解密] 加密: {len(encrypted_data)} 字節 -> 原始: {len(decrypted)} 字節")

        return decrypted


class StateManager:
    """
    狀態管理器

    統一管理狀態的序列化、壓縮和加密。
    """

    def __init__(self, storage_path: str = "./agent_states"):
        """
        初始化狀態管理器

        參數:
            storage_path: 存儲路徑
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.serializer = StateSerializer()
        self.compressor = StateCompressor()
        self.encryptor = StateEncryptor()

        self.snapshots: Dict[str, StateSnapshot] = {}

        print(f"\n狀態管理器初始化完成")
        print(f"存儲路徑: {self.storage_path.absolute()}")

    def save_state(self, state: AgentState, compress: bool = True,
                  encrypt: bool = False, format: str = "json") -> str:
        """
        保存狀態

        參數:
            state: Agent 狀態
            compress: 是否壓縮
            encrypt: 是否加密
            format: 格式（'json' 或 'pickle'）

        返回:
            快照 ID
        """
        print(f"\n[保存狀態] Agent: {state.agent_name}")

        # 序列化
        if format == "json":
            data = self.serializer.to_json(state, pretty=False).encode()
        elif format == "pickle":
            data = self.serializer.to_pickle(state)
        else:
            raise ValueError(f"不支持的格式: {format}")

        # 壓縮
        if compress:
            data = self.compressor.compress(data)

        # 加密
        if encrypt:
            data = self.encryptor.encrypt(data)

        # 計算哈希
        state_hash = hashlib.sha256(data).hexdigest()

        # 生成快照 ID
        snapshot_id = f"{state.agent_id}_{int(datetime.now().timestamp())}"

        # 保存到文件
        file_path = self.storage_path / f"{snapshot_id}.{format}"
        with open(file_path, 'wb') as f:
            f.write(data)

        # 記錄快照
        snapshot = StateSnapshot(
            snapshot_id=snapshot_id,
            agent_id=state.agent_id,
            timestamp=datetime.now().isoformat(),
            state_hash=state_hash,
            compressed=compress,
            encrypted=encrypt,
            metadata={
                "format": format,
                "file_size": len(data),
                "file_path": str(file_path)
            }
        )

        self.snapshots[snapshot_id] = snapshot

        print(f"✓ 狀態已保存")
        print(f"  快照 ID: {snapshot_id}")
        print(f"  文件大小: {len(data)} 字節")
        print(f"  哈希: {state_hash[:16]}...")

        return snapshot_id

    def load_state(self, snapshot_id: str) -> AgentState:
        """
        加載狀態

        參數:
            snapshot_id: 快照 ID

        返回:
            Agent 狀態
        """
        if snapshot_id not in self.snapshots:
            raise ValueError(f"快照 {snapshot_id} 不存在")

        snapshot = self.snapshots[snapshot_id]

        print(f"\n[加載狀態] 快照: {snapshot_id}")

        # 讀取文件
        file_path = Path(snapshot.metadata["file_path"])
        with open(file_path, 'rb') as f:
            data = f.read()

        # 解密
        if snapshot.encrypted:
            data = self.encryptor.decrypt(data)

        # 解壓
        if snapshot.compressed:
            data = self.compressor.decompress(data)

        # 反序列化
        format = snapshot.metadata["format"]
        if format == "json":
            state = self.serializer.from_json(data.decode())
        elif format == "pickle":
            state = self.serializer.from_pickle(data)
        else:
            raise ValueError(f"不支持的格式: {format}")

        print(f"✓ 狀態已加載: {state.agent_name}")

        return state

    def list_snapshots(self, agent_id: Optional[str] = None) -> List[StateSnapshot]:
        """
        列出快照

        參數:
            agent_id: 過濾特定 Agent 的快照

        返回:
            快照列表
        """
        snapshots = list(self.snapshots.values())

        if agent_id:
            snapshots = [s for s in snapshots if s.agent_id == agent_id]

        snapshots.sort(key=lambda s: s.timestamp, reverse=True)

        print(f"\n[快照列表] 共 {len(snapshots)} 個快照")
        for snapshot in snapshots:
            print(f"  - {snapshot.snapshot_id}")
            print(f"    時間: {snapshot.timestamp}")
            print(f"    大小: {snapshot.metadata['file_size']} 字節")

        return snapshots

    def delete_snapshot(self, snapshot_id: str) -> None:
        """
        刪除快照

        參數:
            snapshot_id: 快照 ID
        """
        if snapshot_id not in self.snapshots:
            raise ValueError(f"快照 {snapshot_id} 不存在")

        snapshot = self.snapshots[snapshot_id]
        file_path = Path(snapshot.metadata["file_path"])

        # 刪除文件
        if file_path.exists():
            file_path.unlink()

        # 刪除記錄
        del self.snapshots[snapshot_id]

        print(f"\n[刪除快照] {snapshot_id}")

    def export_state(self, state: AgentState, export_path: str,
                    include_metadata: bool = True) -> None:
        """
        導出狀態為可讀格式

        參數:
            state: Agent 狀態
            export_path: 導出路徑
            include_metadata: 是否包含元數據
        """
        export_data = {
            "agent_state": asdict(state),
            "export_info": {
                "exported_at": datetime.now().isoformat(),
                "version": state.version,
                "format": "letta_state_export_v1"
            }
        }

        if include_metadata:
            export_data["metadata"] = {
                "message_count": len(state.messages),
                "archival_count": len(state.archival_memory),
                "tools_count": len(state.tools)
            }

        export_file = Path(export_path)
        export_file.parent.mkdir(parents=True, exist_ok=True)

        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"\n[導出] 狀態已導出到: {export_file.absolute()}")

    def import_state(self, import_path: str) -> AgentState:
        """
        從導出文件導入狀態

        參數:
            import_path: 導入路徑

        返回:
            Agent 狀態
        """
        with open(import_path, 'r', encoding='utf-8') as f:
            import_data = json.load(f)

        # 驗證格式
        if import_data.get("export_info", {}).get("format") != "letta_state_export_v1":
            print("警告: 未知的導出格式")

        state_dict = import_data["agent_state"]
        state = AgentState(**state_dict)

        print(f"\n[導入] 狀態已導入: {state.agent_name}")

        return state


class IncrementalStateManager:
    """
    增量狀態管理器

    只保存狀態的變化，節省存儲空間。
    """

    def __init__(self):
        """初始化增量狀態管理器"""
        self.base_state: Optional[AgentState] = None
        self.deltas: List[Dict[str, Any]] = []

        print("增量狀態管理器初始化完成")

    def set_base_state(self, state: AgentState) -> None:
        """
        設置基礎狀態

        參數:
            state: 基礎 Agent 狀態
        """
        self.base_state = copy.deepcopy(state)
        self.deltas = []

        print(f"\n[基礎狀態] 設置: {state.agent_name}")

    def save_delta(self, current_state: AgentState) -> None:
        """
        保存增量變化

        參數:
            current_state: 當前狀態
        """
        if self.base_state is None:
            raise ValueError("必須先設置基礎狀態")

        delta = self._compute_delta(self.base_state, current_state)

        if delta:
            delta["timestamp"] = datetime.now().isoformat()
            self.deltas.append(delta)

            print(f"\n[增量保存] 變化數: {len(delta) - 1}")
        else:
            print(f"\n[增量保存] 無變化")

    def reconstruct_state(self) -> AgentState:
        """
        重建完整狀態

        返回:
            完整的 Agent 狀態
        """
        if self.base_state is None:
            raise ValueError("沒有基礎狀態")

        # 從基礎狀態開始
        state = copy.deepcopy(self.base_state)

        # 應用所有增量
        for delta in self.deltas:
            state = self._apply_delta(state, delta)

        print(f"\n[狀態重建] 應用了 {len(self.deltas)} 個增量")

        return state

    def _compute_delta(self, old_state: AgentState, new_state: AgentState) -> Dict[str, Any]:
        """計算狀態差異"""
        delta = {}

        # 比較消息
        if len(new_state.messages) > len(old_state.messages):
            delta["new_messages"] = new_state.messages[len(old_state.messages):]

        # 比較核心記憶
        if new_state.core_memory != old_state.core_memory:
            delta["core_memory"] = new_state.core_memory

        # 比較歸檔記憶
        if len(new_state.archival_memory) > len(old_state.archival_memory):
            delta["new_archival"] = new_state.archival_memory[len(old_state.archival_memory):]

        return delta

    def _apply_delta(self, state: AgentState, delta: Dict[str, Any]) -> AgentState:
        """應用增量到狀態"""
        if "new_messages" in delta:
            state.messages.extend(delta["new_messages"])

        if "core_memory" in delta:
            state.core_memory = delta["core_memory"]

        if "new_archival" in delta:
            state.archival_memory.extend(delta["new_archival"])

        return state


def demonstrate_basic_serialization():
    """演示基本序列化"""
    print("\n" + "=" * 60)
    print("基本序列化演示")
    print("=" * 60)

    # 創建示例狀態
    state = AgentState(
        agent_id="agent_001",
        agent_name="測試助手",
        persona="友善的 AI 助手",
        human="普通用戶",
        core_memory={"user_name": "小明", "preferences": "喜歡 Python"},
        messages=[
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！我是測試助手。"}
        ],
        archival_memory=[
            {"content": "用戶是 Python 開發者", "importance": 0.8}
        ],
        tools=["search", "calculator"],
        metadata={"session_count": 1}
    )

    serializer = StateSerializer()

    # JSON 序列化
    json_str = serializer.to_json(state)
    restored_state = serializer.from_json(json_str)

    print(f"\n驗證: 恢復的狀態匹配 = {restored_state.agent_name == state.agent_name}")

    # Pickle 序列化
    pickle_data = serializer.to_pickle(state)
    restored_state2 = serializer.from_pickle(pickle_data)

    print(f"驗證: Pickle 恢復成功 = {restored_state2.agent_name == state.agent_name}")


def demonstrate_compression():
    """演示壓縮功能"""
    print("\n" + "=" * 60)
    print("壓縮功能演示")
    print("=" * 60)

    # 創建包含大量數據的狀態
    state = AgentState(
        agent_id="agent_002",
        agent_name="大數據助手",
        persona="處理大量數據的助手",
        human="數據分析師",
        core_memory={},
        messages=[
            {"role": "user", "content": f"消息 {i}"}
            for i in range(100)
        ],
        archival_memory=[],
        tools=[],
        metadata={}
    )

    serializer = StateSerializer()
    compressor = StateCompressor()

    # 序列化
    json_data = serializer.to_json(state, pretty=False).encode()

    print(f"\n原始 JSON 大小: {len(json_data)} 字節")

    # 壓縮
    compressed = compressor.compress(json_data)

    # 解壓
    decompressed = compressor.decompress(compressed)

    # 驗證
    print(f"\n驗證: 數據完整性 = {decompressed == json_data}")


def demonstrate_state_manager():
    """演示狀態管理器"""
    print("\n" + "=" * 60)
    print("狀態管理器演示")
    print("=" * 60)

    manager = StateManager("./demo_states")

    # 創建狀態
    state = AgentState(
        agent_id="agent_003",
        agent_name="持久化助手",
        persona="支持狀態持久化的助手",
        human="測試用戶",
        core_memory={"status": "active"},
        messages=[{"role": "user", "content": "測試消息"}],
        archival_memory=[],
        tools=["memory_manager"],
        metadata={"test": True}
    )

    # 保存狀態（不同選項）
    snapshot1 = manager.save_state(state, compress=True, encrypt=False, format="json")
    snapshot2 = manager.save_state(state, compress=True, encrypt=True, format="json")
    snapshot3 = manager.save_state(state, compress=False, encrypt=False, format="pickle")

    # 列出快照
    manager.list_snapshots()

    # 加載狀態
    loaded_state = manager.load_state(snapshot1)

    print(f"\n驗證: {loaded_state.agent_name == state.agent_name}")


def demonstrate_incremental_state():
    """演示增量狀態管理"""
    print("\n" + "=" * 60)
    print("增量狀態管理演示")
    print("=" * 60)

    manager = IncrementalStateManager()

    # 初始狀態
    state = AgentState(
        agent_id="agent_004",
        agent_name="增量助手",
        persona="支持增量保存的助手",
        human="用戶",
        core_memory={},
        messages=[],
        archival_memory=[],
        tools=[],
        metadata={}
    )

    manager.set_base_state(state)

    # 模擬狀態變化
    state.messages.append({"role": "user", "content": "消息 1"})
    manager.save_delta(state)

    state.messages.append({"role": "assistant", "content": "回復 1"})
    state.core_memory["user_name"] = "小明"
    manager.save_delta(state)

    state.messages.append({"role": "user", "content": "消息 2"})
    manager.save_delta(state)

    # 重建狀態
    reconstructed = manager.reconstruct_state()

    print(f"\n驗證: 消息數匹配 = {len(reconstructed.messages) == len(state.messages)}")
    print(f"驗證: 核心記憶匹配 = {reconstructed.core_memory == state.core_memory}")


def demonstrate_export_import():
    """演示導出導入"""
    print("\n" + "=" * 60)
    print("導出導入演示")
    print("=" * 60)

    manager = StateManager("./demo_states")

    # 創建狀態
    state = AgentState(
        agent_id="agent_005",
        agent_name="可遷移助手",
        persona="支持跨平台遷移的助手",
        human="遷移用戶",
        core_memory={"platform": "original"},
        messages=[
            {"role": "user", "content": "準備遷移"},
            {"role": "assistant", "content": "開始遷移過程"}
        ],
        archival_memory=[{"content": "遷移記錄", "importance": 0.9}],
        tools=["migration"],
        metadata={"migration": True}
    )

    # 導出
    export_path = "./demo_states/exported_state.json"
    manager.export_state(state, export_path)

    # 導入
    imported_state = manager.import_state(export_path)

    print(f"\n驗證: Agent 名稱匹配 = {imported_state.agent_name == state.agent_name}")
    print(f"驗證: 消息數匹配 = {len(imported_state.messages) == len(state.messages)}")


def main():
    """主函數：運行所有演示"""
    print("\n" + "=" * 70)
    print(" " * 20 + "Letta 狀態序列化系統")
    print("=" * 70)

    # 基本序列化
    demonstrate_basic_serialization()

    # 壓縮功能
    demonstrate_compression()

    # 狀態管理器
    demonstrate_state_manager()

    # 增量狀態
    demonstrate_incremental_state()

    # 導出導入
    demonstrate_export_import()

    print("\n" + "=" * 70)
    print("狀態序列化演示完成！")
    print("=" * 70)
    print("\n關鍵要點：")
    print("  1. 支持多種序列化格式（JSON, Pickle）")
    print("  2. 壓縮減少存儲空間")
    print("  3. 加密保護敏感數據")
    print("  4. 增量保存節省資源")
    print("  5. 導出導入實現狀態遷移")
    print("\n下一步：查看 10_生產部署.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
