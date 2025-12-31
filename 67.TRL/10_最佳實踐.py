"""
TRL 訓練最佳實踐與生產建議

這個文件總結了 TRL 訓練的最佳實踐，包括：
1. 訓練流程優化
2. 超參數調優
3. 記憶體優化
4. 分布式訓練
5. 生產部署建議
6. 常見問題解決

這些經驗可以幫助您更高效地訓練和部署 RLHF 模型。
"""

import os
import sys
from typing import Optional, Dict, List, Any
import warnings

warnings.filterwarnings('ignore')


def training_pipeline_best_practices():
    """
    訓練流程最佳實踐
    """
    print("\n" + "=" * 60)
    print("訓練流程最佳實踐")
    print("=" * 60)

    guide = """
1. 完整的 RLHF 訓練流程:

   階段 1: 數據準備 (最重要！)
   ├── 收集高質量數據
   ├── 數據清洗和驗證
   ├── 格式統一
   └── 劃分訓練/驗證/測試集

   階段 2: 監督微調 (SFT)
   ├── 使用高質量指令數據
   ├── 訓練 3-5 個 epochs
   ├── 監控驗證損失
   └── 保存最佳檢查點

   階段 3: 偏好優化 (選擇一種)

   方案 A - PPO (傳統但靈活):
   ├── 訓練獎勵模型
   ├── 驗證獎勵模型準確性
   ├── PPO 訓練優化策略
   └── 監控 KL 散度

   方案 B - DPO (推薦):
   ├── 準備偏好數據
   ├── 直接 DPO 訓練
   └── 更簡單、更穩定

   方案 C - ORPO (最簡化):
   └── 從基礎模型直接訓練
       (適合資源受限)

   階段 4: 評估和迭代
   ├── 自動評估指標
   ├── 人工評估
   ├── A/B 測試
   └── 持續改進

2. 數據準備建議:

   ✓ 質量 > 數量
     • 100 個高質量樣本 > 1000 個低質量樣本
     • 定期審查和清理數據
     • 移除矛盾或低質量樣本

   ✓ 多樣性
     • 涵蓋不同主題
     • 包含不同難度
     • 平衡不同類型

   ✓ 偏好數據要求
     • chosen 和 rejected 要有明顯差異
     • 避免過於主觀的比較
     • 保持標註一致性

3. SFT 訓練建議:

   超參數推薦:
   • Learning Rate: 2e-5 to 5e-5
   • Batch Size: 4-8 per device
   • Epochs: 3-5
   • Warmup: 10% of steps
   • Weight Decay: 0.01

   監控指標:
   • 訓練損失持續下降
   • 驗證損失不上升（過擬合信號）
   • 定期生成樣本檢查質量

   技巧:
   ✓ 使用梯度累積增加有效 batch size
   ✓ 使用 gradient checkpointing 節省記憶體
   ✓ LoRA 訓練更快更省記憶體
   ✓ 定期保存檢查點

4. DPO 訓練建議:

   超參數推薦:
   • Learning Rate: 5e-6 to 5e-5
   • Beta: 0.1 (標準值)
   • Batch Size: 4-8 per device
   • Epochs: 1-3

   關鍵點:
   ✓ Beta 控制偏好強度
     • 太小：優化不明顯
     • 太大：可能過度優化
   ✓ 參考模型很重要
     • 使用 SFT 後的模型作為參考
   ✓ 監控 KL 散度
     • 不要偏離參考模型太遠

5. PPO 訓練建議:

   超參數推薦:
   • Learning Rate: 1e-5 to 5e-5
   • KL Coef: 0.1-0.2
   • Clip Range: 0.2
   • PPO Epochs: 4
   • Batch Size: 64-256

   關鍵點:
   ✓ 獎勵模型質量至關重要
   ✓ 監控 KL 散度，防止模式崩潰
   ✓ 獎勵函數要平衡多個目標
   ✓ 訓練不穩定時降低學習率

6. 訓練流程檢查清單:

   開始前:
   □ 數據質量驗證
   □ 基礎模型選擇
   □ 計算資源確認
   □ 評估指標確定

   訓練中:
   □ 監控損失曲線
   □ 定期生成樣本
   □ 檢查記憶體使用
   □ 保存檢查點

   訓練後:
   □ 全面評估
   □ 對比基線
   □ 安全性檢查
   □ 文檔記錄

7. 常見錯誤:

   ✗ 數據質量差
   ✗ 過度訓練（過擬合）
   ✗ 學習率過大
   ✗ 忽略驗證集
   ✗ 不保存檢查點
   ✗ 不做評估就部署
"""

    print(guide)


def hyperparameter_tuning_guide():
    """
    超參數調優指南
    """
    print("\n" + "=" * 60)
    print("超參數調優指南")
    print("=" * 60)

    guide = """
超參數調優策略:

1. 學習率 (Learning Rate):

   重要性: ★★★★★ (最重要)

   推薦範圍:
   • 全量微調: 1e-5 to 5e-5
   • LoRA: 1e-4 to 3e-4
   • DPO: 5e-6 to 5e-5
   • PPO: 1e-5 to 5e-5

   調優策略:
   1. 從較小值開始（如 1e-5）
   2. 如果收斂太慢，增大
   3. 如果不穩定，減小
   4. 使用學習率調度器

   學習率調度器:
   • Linear: 線性衰減（常用）
   • Cosine: 餘弦衰減（推薦）
   • Constant: 固定學習率

2. Batch Size:

   重要性: ★★★★☆

   考慮因素:
   • 記憶體限制
   • 訓練穩定性
   • 收斂速度

   推薦:
   • Per-device batch size: 2-8
   • 使用梯度累積達到更大的有效 batch size
   • 有效 batch size = per_device × devices × accumulation

   示例:
   per_device=4, devices=2, accumulation=4
   → 有效 batch size = 32

3. 訓練輪數 (Epochs):

   重要性: ★★★★☆

   推薦:
   • SFT: 3-5 epochs
   • DPO: 1-3 epochs
   • 獎勵模型: 3-5 epochs

   監控:
   • 訓練損失 vs 驗證損失
   • 驗證損失開始上升 → 過擬合
   • 使用早停法（Early Stopping）

4. Warmup:

   重要性: ★★★☆☆

   推薦:
   • Warmup ratio: 0.05 - 0.1
   • 或 warmup steps: 100-500

   作用:
   • 防止訓練初期不穩定
   • 逐漸增加學習率到目標值

5. Weight Decay:

   重要性: ★★★☆☆

   推薦: 0.01 - 0.1

   作用:
   • 正則化，防止過擬合
   • 對大模型更重要

6. Gradient Clipping:

   重要性: ★★★★☆

   推薦: max_grad_norm = 1.0

   作用:
   • 防止梯度爆炸
   • 提高訓練穩定性

7. DPO 特定參數:

   Beta:
   • 推薦: 0.1
   • 範圍: 0.01 - 0.5
   • 控制偏好優化強度

8. PPO 特定參數:

   KL Coefficient:
   • 推薦: 0.1 - 0.2
   • 控制與參考模型的距離

   Clip Range:
   • 推薦: 0.2
   • PPO 裁剪範圍

9. LoRA 特定參數:

   Rank (r):
   • 簡單任務: 4-8
   • 通用: 16
   • 複雜任務: 32-64

   Alpha:
   • 推薦: 2 × r
   • 縮放因子

   Dropout:
   • 推薦: 0.05 - 0.1
   • 防止過擬合

10. 調優流程:

    階段 1: 粗調
    ├── 使用默認值
    ├── 快速實驗
    └── 確定大致範圍

    階段 2: 精調
    ├── 網格搜索關鍵參數
    ├── 學習率最重要
    └── batch size 次之

    階段 3: 驗證
    ├── 多次運行確認穩定性
    ├── 不同隨機種子
    └── 選擇最佳配置

11. 自動調優工具:

    • Optuna - 貝葉斯優化
    • Ray Tune - 分布式調優
    • Weights & Biases Sweeps

12. 經驗法則:

    ✓ 先確保訓練收斂
    ✓ 再追求最優性能
    ✓ 記錄所有實驗
    ✓ 不要過度調優（過擬合測試集）
"""

    print(guide)


def memory_optimization_techniques():
    """
    記憶體優化技巧
    """
    print("\n" + "=" * 60)
    print("記憶體優化技巧")
    print("=" * 60)

    guide = """
記憶體優化完整指南:

1. 使用 LoRA/QLoRA:

   效果: ★★★★★ (最有效)

   LoRA:
   • 減少 99% 可訓練參數
   • 節省 ~50% 記憶體

   QLoRA (4-bit):
   • 基礎模型量化到 4-bit
   • 節省 ~75% 記憶體
   • 可在單 GPU 訓練 65B 模型

   實現:
   ```python
   from peft import LoraConfig
   from transformers import BitsAndBytesConfig

   # LoRA 配置
   lora_config = LoraConfig(
       r=16,
       lora_alpha=32,
       lora_dropout=0.05,
   )

   # 4-bit 量化配置
   quant_config = BitsAndBytesConfig(
       load_in_4bit=True,
       bnb_4bit_compute_dtype=torch.float16,
   )
   ```

2. Gradient Checkpointing:

   效果: ★★★★☆

   節省: ~50% 記憶體
   代價: ~20% 訓練時間

   實現:
   ```python
   training_args = TrainingArguments(
       gradient_checkpointing=True,
   )
   ```

3. 混合精度訓練:

   效果: ★★★★☆

   FP16:
   • 節省 50% 記憶體
   • 加快訓練速度
   • 適用於大多數 GPU

   BF16:
   • A100/H100 推薦
   • 更好的數值穩定性

   實現:
   ```python
   training_args = TrainingArguments(
       fp16=True,  # 或 bf16=True
   )
   ```

4. Gradient Accumulation:

   效果: ★★★☆☆

   作用:
   • 模擬大 batch size
   • 不增加記憶體

   實現:
   ```python
   training_args = TrainingArguments(
       per_device_train_batch_size=2,
       gradient_accumulation_steps=8,
       # 有效 batch size = 2 × 8 = 16
   )
   ```

5. 優化器選擇:

   效果: ★★★☆☆

   記憶體對比:
   • AdamW: 2× 模型參數
   • AdaFactor: ~0.5× 模型參數
   • SGD: 最少

   推薦: AdamW（效果好）
   記憶體緊張時: AdaFactor

6. 批次大小優化:

   策略:
   1. 找到最大可用 batch size
   2. 使用梯度累積增加有效 batch
   3. 平衡速度和記憶體

7. 序列長度控制:

   效果: ★★★★☆

   記憶體與序列長度平方成正比

   策略:
   • 設置合理的 max_length
   • 使用動態 padding
   • 分組相似長度的樣本

8. DeepSpeed ZeRO:

   效果: ★★★★★ (多 GPU)

   ZeRO Stage 1: 優化器狀態分片
   ZeRO Stage 2: + 梯度分片
   ZeRO Stage 3: + 模型參數分片

   可在多 GPU 上訓練超大模型

9. CPU Offloading:

   效果: ★★★☆☆

   將部分計算/存儲轉移到 CPU
   • 節省 GPU 記憶體
   • 但會降低速度

10. 記憶體使用分析:

    工具:
    • nvidia-smi - 監控 GPU 記憶體
    • torch.cuda.memory_summary() - 詳細分析
    • memory_profiler - Python 記憶體

11. 實用技巧:

    ✓ 清理未使用的變量
    ```python
    del model
    torch.cuda.empty_cache()
    ```

    ✓ 使用較小的評估 batch size
    ```python
    per_device_eval_batch_size=1
    ```

    ✓ 不保存過多檢查點
    ```python
    save_total_limit=3
    ```

12. 記憶體需求估算:

    公式:
    記憶體 ≈ 模型參數 × (2 + 訓練因子)

    訓練因子:
    • 全量微調: 12-16
    • LoRA: 4-6
    • QLoRA: 2-3

    示例 (7B 模型，FP16):
    • 全量微調: 7B × 2 bytes × 14 ≈ 196GB
    • LoRA: 7B × 2 × 5 ≈ 70GB
    • QLoRA: 7B × 0.5 × 3 ≈ 10.5GB

13. 推薦配置:

    24GB GPU (RTX 3090/4090):
    • 7B 模型 + QLoRA
    • 或 3B 模型 + LoRA

    40GB GPU (A100):
    • 13B 模型 + LoRA
    • 或 7B 模型全量微調

    80GB GPU (A100 80GB):
    • 30B 模型 + LoRA
    • 或 13B 模型全量微調
"""

    print(guide)


def distributed_training_guide():
    """
    分布式訓練指南
    """
    print("\n" + "=" * 60)
    print("分布式訓練指南")
    print("=" * 60)

    guide = """
分布式訓練策略:

1. 單機多卡 (Multi-GPU):

   方法 A: DataParallel (不推薦)
   • 簡單但效率低
   • 存在通信瓶頸

   方法 B: DistributedDataParallel (推薦)
   • 高效並行
   • 線性加速

   使用 TRL:
   ```bash
   torchrun --nproc_per_node=4 train.py
   ```

2. 多機多卡:

   配置:
   ```bash
   torchrun \
     --nproc_per_node=4 \
     --nnodes=2 \
     --node_rank=0 \
     --master_addr="192.168.1.1" \
     --master_port=29500 \
     train.py
   ```

3. DeepSpeed:

   優勢:
   • ZeRO 優化
   • 支持超大模型
   • 高效通信

   配置示例:
   ```json
   {
     "train_batch_size": 32,
     "gradient_accumulation_steps": 1,
     "optimizer": {
       "type": "AdamW",
       "params": {
         "lr": 2e-5
       }
     },
     "zero_optimization": {
       "stage": 2
     }
   }
   ```

   使用:
   ```python
   training_args = TrainingArguments(
       deepspeed="ds_config.json",
   )
   ```

4. FSDP (Fully Sharded Data Parallel):

   PyTorch 原生支持
   • 類似 DeepSpeed ZeRO-3
   • 更好的集成

   配置:
   ```python
   training_args = TrainingArguments(
       fsdp="full_shard auto_wrap",
       fsdp_config={
           "min_num_params": 1e8,
       },
   )
   ```

5. 性能優化:

   通信優化:
   • 使用 InfiniBand
   • NCCL 後端
   • 梯度壓縮

   計算優化:
   • 混合精度
   • Gradient checkpointing
   • 編譯優化

6. 實際建議:

   2-4 GPU:
   • DistributedDataParallel
   • 簡單高效

   4-8 GPU:
   • DeepSpeed ZeRO-2
   • 或 FSDP

   8+ GPU:
   • DeepSpeed ZeRO-3
   • 可訓練超大模型

7. 監控和調試:

   工具:
   • TensorBoard
   • Weights & Biases
   • 分布式性能分析器

   關鍵指標:
   • GPU 利用率
   • 通信開銷
   • 訓練吞吐量
"""

    print(guide)


def production_deployment_guide():
    """
    生產部署指南
    """
    print("\n" + "=" * 60)
    print("生產部署指南")
    print("=" * 60)

    guide = """
生產部署完整指南:

1. 模型準備:

   模型優化:
   ✓ 合併 LoRA 權重（如果使用）
   ✓ 量化（INT8/INT4）
   ✓ 剪枝（可選）
   ✓ 編譯優化

   示例:
   ```python
   # 合併 LoRA
   merged_model = model.merge_and_unload()
   merged_model.save_pretrained("merged_model")

   # 量化
   quantized_model = torch.quantization.quantize_dynamic(
       model, {torch.nn.Linear}, dtype=torch.qint8
   )
   ```

2. 推理優化:

   方法 A: vLLM
   • 高吞吐量
   • PagedAttention
   • 動態批處理

   方法 B: TensorRT-LLM
   • NVIDIA GPU 優化
   • 最低延遲

   方法 C: llama.cpp
   • CPU 推理
   • 量化支持

3. 服務部署:

   架構:
   ```
   Client → Load Balancer → API Servers → Model Servers
                                ↓
                            Cache Layer
                                ↓
                            Monitoring
   ```

   API 框架:
   • FastAPI (推薦)
   • Flask
   • gRPC

   示例 (FastAPI):
   ```python
   from fastapi import FastAPI
   from transformers import pipeline

   app = FastAPI()
   model = pipeline("text-generation", model="./model")

   @app.post("/generate")
   async def generate(prompt: str):
       result = model(prompt, max_length=100)
       return {"text": result[0]["generated_text"]}
   ```

4. 容器化:

   Dockerfile 示例:
   ```dockerfile
   FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

   RUN pip install transformers torch

   COPY model /app/model
   COPY server.py /app/

   CMD ["python", "/app/server.py"]
   ```

5. 擴展策略:

   水平擴展:
   • 多個模型實例
   • 負載均衡

   垂直擴展:
   • 更強大的 GPU
   • 批處理優化

   自動擴展:
   • 基於負載
   • Kubernetes HPA

6. 監控:

   關鍵指標:
   • 延遲 (P50, P95, P99)
   • 吞吐量 (requests/second)
   • GPU 利用率
   • 記憶體使用
   • 錯誤率

   工具:
   • Prometheus + Grafana
   • ELK Stack
   • Custom dashboards

7. 安全性:

   ✓ API 認證和授權
   ✓ 速率限制
   ✓ 輸入驗證和清理
   ✓ 內容過濾
   ✓ 輸出審核
   ✓ 日誌審計

8. 成本優化:

   策略:
   • 使用 Spot 實例
   • 自動擴展
   • 模型量化
   • 批處理請求
   • 緩存常見查詢

9. A/B 測試:

   流程:
   1. 部署新版本（金絲雀發布）
   2. 分配小部分流量
   3. 監控指標
   4. 逐步增加流量
   5. 全量上線或回滾

10. 災備和恢復:

    ✓ 多區域部署
    ✓ 定期備份
    ✓ 快速回滾機制
    ✓ 監控告警

11. 文檔:

    必備文檔:
    • API 文檔
    • 部署指南
    • 故障排除
    • 性能調優
    • 安全指南

12. 檢查清單:

    部署前:
    □ 全面測試（功能、性能、安全）
    □ 負載測試
    □ 安全審計
    □ 文檔完整
    □ 監控就緒
    □ 回滾計劃

    部署後:
    □ 監控指標
    □ 收集反饋
    □ 性能分析
    □ 持續優化
"""

    print(guide)


def common_issues_and_solutions():
    """
    常見問題與解決方案
    """
    print("\n" + "=" * 60)
    print("常見問題與解決方案")
    print("=" * 60)

    guide = """
常見問題診斷和解決:

1. 訓練不收斂:

   症狀:
   • 損失不下降
   • 損失震盪
   • 損失變為 NaN

   解決方案:
   ✓ 降低學習率 (試試 1e-6)
   ✓ 增加 warmup
   ✓ 檢查數據質量
   ✓ 使用梯度裁剪
   ✓ 檢查是否有異常樣本
   ✓ 嘗試不同優化器

2. 記憶體不足 (OOM):

   症狀:
   • CUDA out of memory
   • 訓練中斷

   解決方案:
   ✓ 減小 batch size
   ✓ 使用梯度累積
   ✓ 啟用 gradient checkpointing
   ✓ 使用 LoRA/QLoRA
   ✓ 減小序列長度
   ✓ 使用混合精度 (FP16/BF16)
   ✓ 清理未使用的變量

3. 訓練過慢:

   症狀:
   • 迭代速度慢
   • GPU 利用率低

   解決方案:
   ✓ 增大 batch size
   ✓ 使用混合精度
   ✓ 減少日誌頻率
   ✓ 優化數據加載
   ✓ 使用多 GPU
   ✓ 檢查 I/O 瓶頸

4. 過擬合:

   症狀:
   • 訓練損失低，驗證損失高
   • 驗證損失上升

   解決方案:
   ✓ 增加訓練數據
   ✓ 使用數據增強
   ✓ 增加 dropout
   ✓ 使用 weight decay
   ✓ 減少訓練輪數
   ✓ 使用早停法
   ✓ 簡化模型（降低 LoRA rank）

5. 生成質量差:

   症狀:
   • 回答不相關
   • 重複生成
   • 邏輯混亂

   解決方案:
   ✓ 改進訓練數據質量
   ✓ 增加訓練數據
   ✓ 調整生成參數 (temperature, top_p)
   ✓ 使用更好的採樣策略
   ✓ 延長訓練時間
   ✓ 檢查偏好數據質量（DPO/PPO）

6. DPO 訓練問題:

   症狀:
   • 損失不下降
   • 模型退化

   解決方案:
   ✓ 檢查參考模型是否正確
   ✓ 確保 chosen > rejected
   ✓ 調整 beta 參數
   ✓ 使用更好的偏好數據
   ✓ 降低學習率

7. PPO 訓練不穩定:

   症狀:
   • 獎勵突然下降
   • KL 散度爆炸
   • 模式崩潰

   解決方案:
   ✓ 降低學習率
   ✓ 增加 KL coefficient
   ✓ 減小 clip range
   ✓ 檢查獎勵模型
   ✓ 使用更保守的更新
   ✓ 監控 KL 散度

8. 獎勵模型不準確:

   症狀:
   • 驗證準確率低
   • 獎勵與人類判斷不符

   解決方案:
   ✓ 增加偏好數據
   ✓ 改進數據質量
   ✓ 確保標註一致性
   ✓ 增加模型容量
   ✓ 延長訓練時間

9. LoRA 效果不好:

   症狀:
   • 性能不如全量微調
   • 訓練不收斂

   解決方案:
   ✓ 增加 LoRA rank
   ✓ 調整 alpha
   ✓ 增加目標模組
   ✓ 提高學習率
   ✓ 延長訓練時間

10. 模型退化:

    症狀:
    • 基本能力下降
    • 常識錯誤增加

    解決方案:
    ✓ 減小 KL 散度權重
    ✓ 使用更好的參考模型
    ✓ 增加多樣化訓練數據
    ✓ 定期在基準測試上評估

11. 調試技巧:

    ✓ 從小數據集開始
    ✓ 使用小模型驗證流程
    ✓ 逐步增加複雜度
    ✓ 記錄所有實驗
    ✓ 可視化訓練過程
    ✓ 定期檢查生成樣本

12. 獲取幫助:

    資源:
    • TRL GitHub Issues
    • HuggingFace Forums
    • Discord/Slack 社區
    • Stack Overflow
    • 研究論文

    提問技巧:
    ✓ 提供完整錯誤信息
    ✓ 說明環境配置
    ✓ 提供最小可復現示例
    ✓ 描述已嘗試的解決方案
"""

    print(guide)


def main():
    """
    主函數：展示所有最佳實踐
    """
    print("=" * 60)
    print("TRL 訓練最佳實踐與生產建議")
    print("=" * 60)

    # 1. 訓練流程最佳實踐
    training_pipeline_best_practices()

    # 2. 超參數調優指南
    hyperparameter_tuning_guide()

    # 3. 記憶體優化技巧
    memory_optimization_techniques()

    # 4. 分布式訓練指南
    distributed_training_guide()

    # 5. 生產部署指南
    production_deployment_guide()

    # 6. 常見問題與解決方案
    common_issues_and_solutions()

    # 7. 總結
    print("\n" + "=" * 60)
    print("最佳實踐總結")
    print("=" * 60)

    summary = """
關鍵要點:

1. 數據第一
   • 高質量數據 > 複雜算法
   • 投入時間在數據準備上
   • 定期審查和改進數據

2. 循序漸進
   • 從小規模開始驗證
   • 逐步擴大規模
   • 不要一開始就追求完美

3. 全面評估
   • 多維度評估
   • 自動 + 人工
   • 持續監控

4. 優化資源
   • 使用 LoRA/QLoRA
   • 混合精度訓練
   • 梯度檢查點

5. 保持簡單
   • 優先 DPO/ORPO
   • 只在必要時用 PPO
   • 避免過度複雜化

6. 持續改進
   • 收集用戶反饋
   • A/B 測試
   • 迭代優化

7. 安全第一
   • 嚴格的安全評估
   • 內容過濾
   • 持續監控

成功的關鍵:
✓ 高質量數據
✓ 合理的超參數
✓ 全面的評估
✓ 持續的改進

記住:
• 沒有銀彈
• 需要實驗和迭代
• 從實踐中學習
• 保持耐心

祝訓練順利！
"""

    print(summary)

    print("\n" + "=" * 60)
    print("TRL 框架學習完成！")
    print("=" * 60)

    print("\n接下來:")
    print("  1. 選擇合適的訓練方法（SFT → DPO/ORPO）")
    print("  2. 準備高質量數據")
    print("  3. 開始小規模實驗")
    print("  4. 全面評估和優化")
    print("  5. 部署到生產環境")

    print("\n資源鏈接:")
    print("  • TRL 文檔: https://huggingface.co/docs/trl/")
    print("  • TRL GitHub: https://github.com/huggingface/trl")
    print("  • PEFT 文檔: https://huggingface.co/docs/peft/")
    print("  • 社區論壇: https://discuss.huggingface.co/")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用戶中斷")
    except Exception as e:
        print(f"\n程序執行出錯: {e}")
        import traceback
        traceback.print_exc()
