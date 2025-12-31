"""
Axolotl 最佳實踐示例

本示例展示：
1. 完整工作流程
2. 常見陷阱和解決方案
3. 超參數調優策略
4. 生產級訓練配置
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def show_complete_workflow():
    """顯示完整工作流程"""
    console.print("\n[cyan]完整工作流程:[/cyan]\n")

    workflow = [
        ("1. 需求分析", [
            "明確任務目標和評估標準",
            "估算所需資源（GPU、時間、預算）",
            "選擇基礎模型",
        ]),
        ("2. 數據準備", [
            "收集或創建訓練數據（建議 1K-10K 高質量樣本）",
            "數據清洗和格式化",
            "劃分訓練集/驗證集（90/10 或 85/15）",
            "數據驗證和質量檢查",
        ]),
        ("3. 實驗設計", [
            "選擇微調方法（LoRA/QLoRA/全量）",
            "設計超參數搜索空間",
            "準備評估方案",
        ]),
        ("4. 快速原型", [
            "使用小數據集（100-500 樣本）",
            "使用小 rank（r=8）快速迭代",
            "驗證訓練管道正常工作",
        ]),
        ("5. 超參數調優", [
            "調整 learning rate",
            "調整 LoRA rank 和 alpha",
            "調整 batch size",
            "監控過擬合",
        ]),
        ("6. 完整訓練", [
            "使用完整數據集",
            "使用最佳超參數",
            "訓練多個檢查點",
            "持續監控指標",
        ]),
        ("7. 評估和選擇", [
            "自動指標評估",
            "生成質量測試",
            "選擇最佳檢查點",
        ]),
        ("8. 模型優化", [
            "合併 LoRA 權重",
            "量化優化",
            "轉換為部署格式",
        ]),
        ("9. 部署", [
            "選擇推理框架",
            "配置服務",
            "性能測試",
            "上線和監控",
        ]),
        ("10. 維護", [
            "收集用戶反饋",
            "定期評估",
            "持續改進",
        ]),
    ]

    for phase, steps in workflow:
        console.print(f"[yellow]{phase}:[/yellow]")
        for step in steps:
            console.print(f"  - {step}")
        console.print()


def show_hyperparameter_tuning():
    """顯示超參數調優策略"""
    console.print("[cyan]超參數調優策略:[/cyan]\n")

    console.print("[yellow]1. 基礎參數範圍:[/yellow]\n")

    params = [
        ("learning_rate", "2e-5, 5e-5, 1e-4, 2e-4, 5e-4", "從小到大嘗試"),
        ("lora_r", "8, 16, 32, 64", "根據資源和效果選擇"),
        ("lora_alpha", "r, 2*r, 4*r", "通常為 rank 的 2 倍"),
        ("batch_size", "4, 8, 16, 32", "盡可能大但不 OOM"),
        ("num_epochs", "2, 3, 5", "觀察驗證損失"),
        ("warmup_steps", "50, 100, 200", "總步數的 5-10%"),
    ]

    table = Table(title="超參數建議範圍")
    table.add_column("參數", style="cyan")
    table.add_column("建議值", style="yellow")
    table.add_column("說明", style="dim")

    for param in params:
        table.add_row(*param)

    console.print(table)
    console.print()

    console.print("[yellow]2. 調優順序:[/yellow]")
    console.print("  a. 先固定其他參數，調整 learning rate（影響最大）")
    console.print("  b. 再調整 LoRA rank（影響效果和速度）")
    console.print("  c. 然後調整 batch size（影響穩定性）")
    console.print("  d. 最後微調其他參數\n")

    console.print("[yellow]3. 調優技巧:[/yellow]")
    console.print("  - 使用小數據集快速實驗（100-500 樣本）")
    console.print("  - 每次只改變一個參數")
    console.print("  - 使用 Weights & Biases 記錄所有實驗")
    console.print("  - 觀察訓練/驗證損失曲線")
    console.print("  - 定期檢查生成質量\n")


def show_common_pitfalls():
    """顯示常見陷阱"""
    console.print("[cyan]常見陷阱和解決方案:[/cyan]\n")

    pitfalls = [
        ("過擬合", [
            "症狀：訓練損失持續下降，驗證損失上升",
            "解決：減少 epochs、增加數據、使用 dropout",
        ]),
        ("欠擬合", [
            "症狀：訓練和驗證損失都很高",
            "解決：增加 rank、提高學習率、訓練更多 epochs",
        ]),
        ("不穩定訓練", [
            "症狀：損失劇烈波動",
            "解決：降低學習率、增加 warmup、使用梯度裁剪",
        ]),
        ("內存不足", [
            "症狀：CUDA OOM 錯誤",
            "解決：減小 batch size、使用 QLoRA、啟用梯度檢查點",
        ]),
        ("訓練太慢", [
            "症狀：預計訓練時間過長",
            "解決：增加批次、減小 rank、使用多 GPU、減少數據",
        ]),
        ("生成質量差", [
            "症狀：輸出不符合預期",
            "解決：檢查數據質量、增加數據量、調整提示詞模板",
        ]),
        ("格式不一致", [
            "症狀：輸出格式混亂",
            "解決：統一數據格式、使用明確的提示詞模板",
        ]),
    ]

    for pitfall, solutions in pitfalls:
        console.print(f"[yellow]問題：{pitfall}[/yellow]")
        for solution in solutions:
            console.print(f"  {solution}")
        console.print()


def show_data_quality_checklist():
    """顯示數據質量檢查清單"""
    console.print("[cyan]數據質量檢查清單:[/cyan]\n")

    checklist = [
        "□ 數據量充足（至少 500 條，建議 1000+ 條）",
        "□ 數據多樣性（覆蓋不同場景和任務）",
        "□ 數據準確性（輸出正確、事實可靠）",
        "□ 格式一致性（統一的格式和模板）",
        "□ 無重複數據",
        "□ 無格式錯誤（JSON 格式正確）",
        "□ 長度適當（不超過 sequence_len）",
        "□ 平衡性（不同類別數據均衡）",
        "□ 質量優於數量（寧少勿濫）",
        "□ 驗證集代表性（與實際應用相符）",
    ]

    for item in checklist:
        console.print(f"  {item}")
    console.print()


def show_production_config():
    """顯示生產級配置"""
    console.print("[cyan]生產級訓練配置示例:[/cyan]\n")

    console.print("[yellow]config.yml:[/yellow]")
    console.print("""
# 基礎模型
base_model: meta-llama/Llama-2-7b-hf
model_type: LlamaForCausalLM
tokenizer_type: LlamaTokenizer

# LoRA 配置（經過調優）
adapter: lora
lora_r: 16
lora_alpha: 32
lora_dropout: 0.05
lora_target_modules:
  - q_proj
  - v_proj
  - k_proj
  - o_proj

# 數據配置
datasets:
  - path: data/train_final.jsonl
    type: alpaca
val_set_size: 0.1
sequence_len: 2048

# 訓練參數（優化過的）
batch_size: 16
micro_batch_size: 2
gradient_accumulation_steps: 8
num_epochs: 3

# 優化器配置
optimizer: adamw_torch
learning_rate: 0.0002
lr_scheduler: cosine
warmup_steps: 100
weight_decay: 0.01

# 精度和優化
bf16: true
tf32: true
gradient_checkpointing: true
flash_attention: true

# 正則化
max_grad_norm: 1.0

# 評估和保存
logging_steps: 10
eval_steps: 50
save_steps: 100
save_total_limit: 3
output_dir: ./production_output

# 監控
wandb_project: production-llm
wandb_run_id: llama2-7b-production-v1

# Early Stopping
early_stopping_patience: 3
    """)


def show_monitoring_strategy():
    """顯示監控策略"""
    console.print("[cyan]監控和調試策略:[/cyan]\n")

    console.print("[yellow]1. 訓練監控:[/yellow]")
    console.print("  - 訓練/驗證 Loss 曲線")
    console.print("  - 學習率變化")
    console.print("  - 梯度範數")
    console.print("  - GPU 利用率和內存")
    console.print()

    console.print("[yellow]2. 關鍵指標:[/yellow]")
    console.print("  - Loss 下降趨勢")
    console.print("  - 訓練/驗證 Loss 差距（檢測過擬合）")
    console.print("  - 訓練速度（tokens/s）")
    console.print("  - 內存使用量")
    console.print()

    console.print("[yellow]3. 定期檢查:[/yellow]")
    console.print("  - 每 100 步檢查生成質量")
    console.print("  - 每個 epoch 結束評估驗證集")
    console.print("  - 保存最佳檢查點")
    console.print()

    console.print("[yellow]4. 日誌分析:[/yellow]")
    console.print("""
# 監控訓練日誌
tail -f training.log | grep "loss\\|step"

# 使用 TensorBoard
tensorboard --logdir ./output

# 使用 Weights & Biases
wandb login
# 訓練時自動上傳
    """)


def show_resource_planning():
    """顯示資源規劃"""
    console.print("[cyan]資源規劃建議:[/cyan]\n")

    scenarios = [
        ("個人實驗", "RTX 3090 24GB", "QLoRA + 小數據集", "快速迭代"),
        ("小團隊", "A100 40GB x2", "LoRA + 中等數據集", "平衡性能和成本"),
        ("生產環境", "A100 80GB x4-8", "LoRA/全量 + 大數據集", "最佳性能"),
        ("學術研究", "雲端 GPU（按需）", "靈活配置", "成本可控"),
    ]

    table = Table(title="資源規劃")
    table.add_column("場景", style="cyan")
    table.add_column("硬體配置", style="yellow")
    table.add_column("訓練策略", style="green")
    table.add_column("目標", style="dim")

    for scenario in scenarios:
        table.add_row(*scenario)

    console.print(table)
    console.print()


def show_tips_and_tricks():
    """顯示技巧和竅門"""
    console.print("[cyan]實用技巧和竅門:[/cyan]\n")

    tips = [
        "1. 從小開始：先用小數據集和小 rank 驗證流程",
        "2. 版本控制：對配置文件和數據使用 git",
        "3. 實驗記錄：使用 Weights & Biases 記錄所有實驗",
        "4. 檢查點策略：保存多個檢查點，選擇最佳",
        "5. 數據優先：投資時間在數據質量上回報最高",
        "6. 漸進式調優：每次只改變一個變量",
        "7. 對比基線：始終與基礎模型對比",
        "8. 真實測試：使用真實場景測試，不只是指標",
        "9. 文檔記錄：記錄所有決策和觀察",
        "10. 社區資源：參考成功案例和最佳實踐",
    ]

    for tip in tips:
        console.print(f"  {tip}")
    console.print()


def show_cost_optimization():
    """顯示成本優化"""
    console.print("[cyan]成本優化策略:[/cyan]\n")

    strategies = [
        "1. 選擇合適的方法：",
        "   - 優先考慮 QLoRA（最省資源）",
        "   - 避免不必要的全量微調",
        "",
        "2. 高效使用 GPU：",
        "   - 使用 Spot 實例（便宜 60-90%）",
        "   - 批量實驗，減少啟動次數",
        "   - 使用檢查點恢復訓練",
        "",
        "3. 數據優化：",
        "   - 策略性地選擇訓練樣本",
        "   - 主動學習選擇最有價值的數據",
        "   - 避免過度訓練",
        "",
        "4. 雲端選項：",
        "   - Google Colab Pro（便宜但有限制）",
        "   - Vast.ai, RunPod（按小時計費）",
        "   - Lambda Labs（專注 ML，價格合理）",
    ]

    for strategy in strategies:
        console.print(f"  {strategy}")
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]Axolotl 最佳實踐[/bold cyan]",
        border_style="cyan"
    ))

    # 1. 完整工作流程
    show_complete_workflow()

    # 2. 超參數調優
    show_hyperparameter_tuning()

    # 3. 常見陷阱
    show_common_pitfalls()

    # 4. 數據質量檢查
    show_data_quality_checklist()

    # 5. 生產配置
    show_production_config()

    # 6. 監控策略
    show_monitoring_strategy()

    # 7. 資源規劃
    show_resource_planning()

    # 8. 技巧和竅門
    show_tips_and_tricks()

    # 9. 成本優化
    show_cost_optimization()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ Axolotl 所有示例完成！[/bold green]")
    console.print("\n[cyan]關鍵要點:[/cyan]")
    console.print("  1. 數據質量 > 模型大小 > 超參數調優")
    console.print("  2. 從小開始，逐步擴展")
    console.print("  3. 持續監控和評估")
    console.print("  4. 記錄所有實驗")
    console.print("  5. 真實場景測試最重要")


if __name__ == "__main__":
    main()
