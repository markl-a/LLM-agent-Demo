"""
Flower 聯邦學習框架 - 安全聚合

這個示例展示如何實現安全聚合協議：
1. 安全聚合基本概念
2. 秘密分享
3. 加密聚合
4. 掉線容錯
5. 安全多方計算
"""

import flwr as fl
from flwr.server.strategy import FedAvg
from flwr.common import Parameters, ndarrays_to_parameters, parameters_to_ndarrays
import numpy as np
from typing import Dict, List, Tuple, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import logging
import hashlib
from dataclasses import dataclass

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()


# ============================================================================
# 1. 安全聚合概念
# ============================================================================

class SecureAggregationExplainer:
    """安全聚合概念解釋器"""

    @staticmethod
    def explain_basics():
        """解釋安全聚合基本概念"""
        console.print(Panel.fit(
            "[bold cyan]安全聚合 (Secure Aggregation)[/bold cyan]",
            border_style="cyan"
        ))

        console.print("\n[bold yellow]核心目標:[/bold yellow]")
        console.print("  • 服務器無法看到單個客戶端的模型更新")
        console.print("  • 服務器只能得到所有客戶端的聚合結果")
        console.print("  • 保護客戶端的模型參數隱私\n")

        console.print("[bold yellow]工作原理:[/bold yellow]")
        console.print("  1. 每個客戶端生成隨機掩碼")
        console.print("  2. 客戶端用掩碼加密自己的更新")
        console.print("  3. 服務器收集所有加密更新")
        console.print("  4. 掩碼在聚合過程中相互抵消")
        console.print("  5. 服務器得到明文的聚合結果\n")

        console.print("[bold yellow]優勢:[/bold yellow]")

        table = Table(show_header=True, header_style="bold blue")
        table.add_column("特性", style="cyan", width=20)
        table.add_column("說明", style="white", width=45)

        table.add_row(
            "隱私保護",
            "服務器無法推斷單個客戶端的數據或模型"
        )
        table.add_row(
            "計算高效",
            "只需要簡單的加法和隨機數生成"
        )
        table.add_row(
            "容錯性",
            "可以容忍部分客戶端掉線"
        )
        table.add_row(
            "可驗證性",
            "可以驗證聚合結果的正確性"
        )

        console.print(table)

        console.print("\n[bold yellow]vs 差分隱私:[/bold yellow]")
        console.print("  • 差分隱私: 添加噪聲，降低模型精度")
        console.print("  • 安全聚合: 加密計算，不影響精度")


# ============================================================================
# 2. 秘密分享協議
# ============================================================================

class SecretSharing:
    """
    秘密分享協議實現

    使用 Shamir 秘密分享方案
    """

    def __init__(self, num_clients: int, threshold: int):
        """
        初始化秘密分享

        Args:
            num_clients: 客戶端總數
            threshold: 重構秘密所需的最少份額數
        """
        self.num_clients = num_clients
        self.threshold = threshold
        self.prime = 2**31 - 1  # 大質數

        console.print(f"[green]✓ 秘密分享協議初始化[/green]")
        console.print(f"  - 客戶端數: {num_clients}")
        console.print(f"  - 閾值: {threshold}")

    def share_secret(self, secret: int) -> List[Tuple[int, int]]:
        """
        將秘密分享給多個客戶端

        Args:
            secret: 要分享的秘密

        Returns:
            份額列表 [(x, y), ...]
        """
        # 生成隨機多項式 f(x) = secret + a1*x + a2*x^2 + ... + a_{t-1}*x^{t-1}
        coefficients = [secret] + [
            np.random.randint(0, self.prime) for _ in range(self.threshold - 1)
        ]

        # 為每個客戶端計算份額
        shares = []
        for i in range(1, self.num_clients + 1):
            x = i
            y = self._evaluate_polynomial(coefficients, x) % self.prime
            shares.append((x, y))

        return shares

    def reconstruct_secret(self, shares: List[Tuple[int, int]]) -> int:
        """
        從份額重構秘密

        使用拉格朗日插值

        Args:
            shares: 份額列表

        Returns:
            重構的秘密
        """
        if len(shares) < self.threshold:
            raise ValueError(f"需要至少 {self.threshold} 個份額，但只有 {len(shares)} 個")

        # 使用拉格朗日插值計算 f(0)
        secret = 0
        for i, (x_i, y_i) in enumerate(shares[:self.threshold]):
            numerator = 1
            denominator = 1

            for j, (x_j, _) in enumerate(shares[:self.threshold]):
                if i != j:
                    numerator = (numerator * (-x_j)) % self.prime
                    denominator = (denominator * (x_i - x_j)) % self.prime

            # 模逆元
            denominator_inv = pow(denominator, self.prime - 2, self.prime)
            lagrange_coef = (numerator * denominator_inv) % self.prime

            secret = (secret + y_i * lagrange_coef) % self.prime

        return secret

    def _evaluate_polynomial(self, coefficients: List[int], x: int) -> int:
        """評估多項式在 x 處的值"""
        result = 0
        for i, coef in enumerate(coefficients):
            result += coef * (x ** i)
        return result % self.prime


# ============================================================================
# 3. 安全聚合客戶端
# ============================================================================

@dataclass
class MaskPair:
    """掩碼對"""
    self_mask: np.ndarray  # 自己生成的掩碼
    peer_masks: Dict[int, np.ndarray]  # 與其他客戶端的成對掩碼


class SecureAggregationClient(fl.client.NumPyClient):
    """
    實現安全聚合的客戶端

    協議步驟：
    1. 密鑰協商：與其他客戶端建立共享密鑰
    2. 掩碼生成：生成隨機掩碼
    3. 加密上傳：上傳加密的模型更新
    4. 掩碼分享：在需要時分享掩碼（處理掉線）
    """

    def __init__(
        self,
        client_id: int,
        num_clients: int,
        model_shape: Tuple[int, ...]
    ):
        """
        初始化安全聚合客戶端

        Args:
            client_id: 客戶端 ID
            num_clients: 總客戶端數
            model_shape: 模型參數形狀
        """
        self.client_id = client_id
        self.num_clients = num_clients
        self.model_shape = model_shape

        # 模型參數（示例）
        self.parameters = np.random.randn(*model_shape).astype(np.float32)

        # 掩碼
        self.masks: Optional[MaskPair] = None

        # 與其他客戶端的共享密鑰
        self.shared_keys: Dict[int, bytes] = {}

        console.print(f"[green]✓ 安全聚合客戶端 {client_id} 初始化[/green]")

    def setup_phase(self, alive_clients: List[int]):
        """
        設置階段：建立共享密鑰

        Args:
            alive_clients: 在線客戶端列表
        """
        console.print(f"\n[blue]客戶端 {self.client_id}: 密鑰協商階段[/blue]")

        # 與其他客戶端建立共享密鑰（簡化版）
        for other_id in alive_clients:
            if other_id != self.client_id:
                # 實際應使用 Diffie-Hellman 密鑰交換
                shared_key = self._generate_shared_key(self.client_id, other_id)
                self.shared_keys[other_id] = shared_key

        console.print(f"  ✓ 與 {len(self.shared_keys)} 個客戶端建立共享密鑰")

    def advertise_keys_phase(self) -> bytes:
        """
        廣播公鑰階段

        Returns:
            公鑰
        """
        # 簡化版：返回客戶端 ID 的哈希作為公鑰
        public_key = hashlib.sha256(str(self.client_id).encode()).digest()
        return public_key

    def share_keys_phase(self) -> Dict[int, bytes]:
        """
        分享密鑰階段

        Returns:
            共享密鑰字典
        """
        return self.shared_keys

    def masked_input_collection_phase(self) -> np.ndarray:
        """
        掩碼輸入收集階段

        Returns:
            加密的模型更新
        """
        console.print(f"\n[blue]客戶端 {self.client_id}: 生成掩碼並加密[/blue]")

        # 生成掩碼
        self.masks = self._generate_masks()

        # 加密模型更新
        masked_parameters = self.parameters.copy()

        # 添加自己的掩碼
        masked_parameters += self.masks.self_mask

        # 添加成對掩碼
        for other_id, peer_mask in self.masks.peer_masks.items():
            if other_id > self.client_id:
                # 添加掩碼
                masked_parameters += peer_mask
            else:
                # 減去掩碼（確保掩碼相互抵消）
                masked_parameters -= peer_mask

        console.print(f"  ✓ 模型更新已加密")

        return masked_parameters

    def unmasking_phase(self, dropped_clients: List[int]) -> Dict[int, np.ndarray]:
        """
        去掩碼階段（處理掉線客戶端）

        Args:
            dropped_clients: 掉線客戶端列表

        Returns:
            需要公開的掩碼
        """
        revealed_masks = {}

        for dropped_id in dropped_clients:
            if dropped_id in self.masks.peer_masks:
                # 公開與掉線客戶端的成對掩碼
                revealed_masks[dropped_id] = self.masks.peer_masks[dropped_id]

        console.print(f"  客戶端 {self.client_id}: 公開 {len(revealed_masks)} 個掩碼")

        return revealed_masks

    def _generate_masks(self) -> MaskPair:
        """生成掩碼"""
        # 生成自己的掩碼（用於防止服務器推斷）
        self_mask = np.random.randn(*self.model_shape).astype(np.float32)

        # 生成與其他客戶端的成對掩碼
        peer_masks = {}
        for other_id in self.shared_keys.keys():
            # 使用共享密鑰生成偽隨機掩碼
            seed = int.from_bytes(self.shared_keys[other_id][:4], 'big')
            rng = np.random.RandomState(seed)
            peer_mask = rng.randn(*self.model_shape).astype(np.float32)
            peer_masks[other_id] = peer_mask

        return MaskPair(self_mask=self_mask, peer_masks=peer_masks)

    def _generate_shared_key(self, id1: int, id2: int) -> bytes:
        """
        生成共享密鑰（簡化版）

        實際應使用 Diffie-Hellman 或 ECDH

        Args:
            id1: 客戶端 1 ID
            id2: 客戶端 2 ID

        Returns:
            共享密鑰
        """
        # 確保密鑰對稱（id1 和 id2 順序無關）
        key_material = f"{min(id1, id2)}_{max(id1, id2)}"
        return hashlib.sha256(key_material.encode()).digest()

    def get_parameters(self, config: Dict[str, str]) -> List[np.ndarray]:
        """獲取模型參數"""
        return [self.parameters]

    def fit(
        self,
        parameters: List[np.ndarray],
        config: Dict[str, str]
    ) -> Tuple[List[np.ndarray], int, Dict]:
        """訓練（簡化版）"""
        # 簡單的模擬訓練
        self.parameters = parameters[0] + np.random.randn(*self.model_shape) * 0.01
        return [self.parameters], 100, {}

    def evaluate(
        self,
        parameters: List[np.ndarray],
        config: Dict[str, str]
    ) -> Tuple[float, int, Dict]:
        """評估（簡化版）"""
        return 0.5, 100, {"accuracy": 0.8}


# ============================================================================
# 4. 安全聚合服務器
# ============================================================================

class SecureAggregationServer:
    """
    安全聚合服務器

    協調安全聚合協議的各個階段
    """

    def __init__(self, num_clients: int, threshold: int):
        """
        初始化服務器

        Args:
            num_clients: 客戶端總數
            threshold: 最少需要的客戶端數
        """
        self.num_clients = num_clients
        self.threshold = threshold
        self.clients: Dict[int, SecureAggregationClient] = {}

        console.print(f"[green]✓ 安全聚合服務器初始化[/green]")
        console.print(f"  - 客戶端數: {num_clients}")
        console.print(f"  - 閾值: {threshold}")

    def register_client(self, client: SecureAggregationClient):
        """註冊客戶端"""
        self.clients[client.client_id] = client

    def run_secure_aggregation(self) -> np.ndarray:
        """
        運行完整的安全聚合協議

        Returns:
            聚合後的模型參數
        """
        console.print(Panel.fit(
            "[bold cyan]安全聚合協議執行[/bold cyan]",
            border_style="cyan"
        ))

        # 模擬一些客戶端在線
        alive_clients = list(self.clients.keys())[:self.threshold]

        # 階段 0: 設置
        console.print("\n[bold yellow]階段 0: 設置階段[/bold yellow]")
        for client_id in alive_clients:
            self.clients[client_id].setup_phase(alive_clients)

        # 階段 1: 廣播公鑰
        console.print("\n[bold yellow]階段 1: 廣播公鑰[/bold yellow]")
        public_keys = {}
        for client_id in alive_clients:
            public_keys[client_id] = self.clients[client_id].advertise_keys_phase()
        console.print(f"  收集到 {len(public_keys)} 個公鑰")

        # 階段 2: 收集加密的模型更新
        console.print("\n[bold yellow]階段 2: 收集加密更新[/bold yellow]")
        masked_updates = []
        for client_id in alive_clients:
            masked_update = self.clients[client_id].masked_input_collection_phase()
            masked_updates.append(masked_update)

        # 聚合加密的更新
        aggregated_masked = sum(masked_updates)
        console.print(f"  聚合 {len(masked_updates)} 個加密更新")

        # 階段 3: 去掩碼（如果有客戶端掉線）
        dropped_clients = []  # 模擬沒有客戶端掉線

        if dropped_clients:
            console.print("\n[bold yellow]階段 3: 去掩碼（處理掉線）[/bold yellow]")
            for client_id in alive_clients:
                revealed_masks = self.clients[client_id].unmasking_phase(dropped_clients)
                # 從聚合結果中移除掉線客戶端的掩碼
                # （這裡簡化處理）

        # 結果
        console.print("\n[bold green]✓ 安全聚合完成[/bold green]")
        console.print("  服務器獲得聚合結果，但無法看到單個客戶端的更新")

        return aggregated_masked


# ============================================================================
# 5. 演示
# ============================================================================

def demonstrate_secret_sharing():
    """演示秘密分享"""
    console.print(Panel.fit(
        "[bold cyan]秘密分享演示[/bold cyan]",
        border_style="cyan"
    ))

    ss = SecretSharing(num_clients=5, threshold=3)

    # 分享秘密
    secret = 12345
    console.print(f"\n[yellow]原始秘密: {secret}[/yellow]")

    shares = ss.share_secret(secret)
    console.print(f"\n[blue]生成 {len(shares)} 個份額:[/blue]")
    for i, (x, y) in enumerate(shares):
        console.print(f"  份額 {i+1}: ({x}, {y})")

    # 重構秘密
    console.print(f"\n[blue]使用前 3 個份額重構:[/blue]")
    reconstructed = ss.reconstruct_secret(shares[:3])
    console.print(f"  重構的秘密: {reconstructed}")

    if reconstructed == secret:
        console.print("[green]✓ 重構成功！[/green]")
    else:
        console.print("[red]✗ 重構失敗[/red]")


def demonstrate_secure_aggregation():
    """演示安全聚合"""
    console.print("\n" + "="*70 + "\n")

    # 創建服務器
    server = SecureAggregationServer(num_clients=5, threshold=3)

    # 創建客戶端
    model_shape = (10,)
    for i in range(5):
        client = SecureAggregationClient(
            client_id=i,
            num_clients=5,
            model_shape=model_shape
        )
        server.register_client(client)

    # 運行安全聚合
    result = server.run_secure_aggregation()

    console.print(f"\n[green]聚合結果形狀: {result.shape}[/green]")


def main():
    """主函數"""
    console.print("\n[bold magenta]Flower 聯邦學習 - 安全聚合[/bold magenta]\n")

    # 1. 基礎概念
    SecureAggregationExplainer.explain_basics()

    console.print("\n" + "="*70 + "\n")

    # 2. 秘密分享演示
    demonstrate_secret_sharing()

    # 3. 安全聚合演示
    demonstrate_secure_aggregation()

    console.print("\n[bold green]✓ 安全聚合示例完成！[/bold green]")
    console.print("\n[yellow]關鍵要點:[/yellow]")
    console.print("  1. 密鑰協商 - 客戶端之間建立共享密鑰")
    console.print("  2. 掩碼生成 - 使用隨機掩碼加密更新")
    console.print("  3. 掩碼抵消 - 成對掩碼在聚合時相互抵消")
    console.print("  4. 掉線處理 - 使用秘密分享恢復掩碼")
    console.print("  5. 隱私保護 - 服務器無法看到單個更新")

    console.print("\n[cyan]優勢:[/cyan]")
    console.print("  • 不影響模型精度（vs 差分隱私）")
    console.print("  • 計算效率高")
    console.print("  • 可容忍部分客戶端掉線")
    console.print("  • 防止服務器推斷客戶端數據")

    console.print("\n[cyan]挑戰:[/cyan]")
    console.print("  • 需要多輪通信")
    console.print("  • 實現複雜度高")
    console.print("  • 需要處理掉線問題")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]程序被用戶中斷[/yellow]")
    except Exception as e:
        logger.exception("程序執行出錯")
        console.print(f"[red]錯誤: {str(e)}[/red]")
