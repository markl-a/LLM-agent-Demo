"""
PEFT 多任務學習和適配器管理

這個文件介紹如何使用 PEFT 進行多任務學習，包括：
1. 一個基礎模型 + 多個適配器
2. 適配器的保存和加載
3. 動態切換適配器
4. 適配器合併
5. 多任務訓練策略

使用 PEFT，一個基礎模型可以通過不同的適配器服務多個任務。
"""

import os
import torch
from typing import Dict, List
import warnings

warnings.filterwarnings('ignore')


def explain_multi_task_peft():
    """
    解釋多任務 PEFT 的概念
    """
    print("=" * 70)
    print("多任務 PEFT 概念")
    print("=" * 70)

    print("""
多任務 PEFT 的核心思想：

1. 傳統多任務學習：
   • 為每個任務訓練一個完整模型
   • 存儲成本高（N 個任務 = N 個完整模型）
   • 部署復雜

2. PEFT 多任務方法：

   ┌──────────────────────────────────┐
   │      基礎模型 (共享)            │
   │      例如: LLaMA-7B             │
   └──────────┬───────────────────────┘
              │
      ┌───────┼───────┬───────┐
      │       │       │       │
   [翻譯]  [摘要]  [QA]  [代碼生成]
   適配器   適配器  適配器  適配器
   (3MB)   (3MB)  (3MB)  (3MB)

3. 優勢：
   • 基礎模型只需存儲一份
   • 每個適配器只有幾 MB
   • 動態切換，靈活高效
   • 易於擴展新任務

4. 存儲對比（以 7B 模型為例）：

   傳統方法:
   • 4 個任務 = 4 × 14GB = 56GB

   PEFT 方法:
   • 1 個基礎模型 (14GB) + 4 個適配器 (4 × 3MB = 12MB)
   • 總計: ~14GB
   • 節省: 75%

5. 應用場景：
   • 企業多業務線
   • 研究多個任務
   • SaaS 多租戶
   • 個性化服務
    """)


def train_multiple_adapters():
    """
    訓練多個適配器的示例
    """
    print("\n" + "=" * 70)
    print("訓練多個任務適配器")
    print("=" * 70)

    print("""
完整的多任務訓練流程：

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from peft import LoraConfig, get_peft_model, TaskType
from datasets import Dataset

# 1. 加載基礎模型（只需一次）
base_model_name = "gpt2"
base_model = AutoModelForCausalLM.from_pretrained(base_model_name)
tokenizer = AutoTokenizer.from_pretrained(base_model_name)
tokenizer.pad_token = tokenizer.eos_token

# 2. 定義任務和數據
tasks = {
    "translation": {
        "data": Dataset.from_dict({
            "text": ["Translate to French: Hello", "Translate to French: World", ...]
        }),
        "output_dir": "./adapters/translation"
    },
    "summarization": {
        "data": Dataset.from_dict({
            "text": ["Summarize: Long text here...", ...]
        }),
        "output_dir": "./adapters/summarization"
    },
    "qa": {
        "data": Dataset.from_dict({
            "text": ["Q: What is AI? A: ...", ...]
        }),
        "output_dir": "./adapters/qa"
    },
}

# 3. LoRA 配置（所有任務共用）
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["c_attn"],
    lora_dropout=0.1,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)

# 4. 為每個任務訓練適配器
for task_name, task_info in tasks.items():
    print(f"\\n訓練任務: {task_name}")

    # 重新加載基礎模型（確保乾淨狀態）
    model = AutoModelForCausalLM.from_pretrained(base_model_name)

    # 應用 LoRA
    peft_model = get_peft_model(model, lora_config)

    # 訓練配置
    training_args = TrainingArguments(
        output_dir=task_info["output_dir"],
        num_train_epochs=3,
        per_device_train_batch_size=4,
        learning_rate=3e-4,
    )

    # 訓練
    trainer = Trainer(
        model=peft_model,
        args=training_args,
        train_dataset=task_info["data"],
    )
    trainer.train()

    # 保存適配器
    peft_model.save_pretrained(task_info["output_dir"])
    print(f"適配器已保存到: {task_info['output_dir']}")

print("\\n所有任務適配器訓練完成！")
```
    """)


def manage_adapters():
    """
    適配器管理示例
    """
    print("\n" + "=" * 70)
    print("適配器管理和切換")
    print("=" * 70)

    print("""
1. 加載特定任務的適配器：

```python
from transformers import AutoModelForCausalLM
from peft import PeftModel

# 加載基礎模型
base_model = AutoModelForCausalLM.from_pretrained("gpt2")

# 加載翻譯適配器
translation_model = PeftModel.from_pretrained(
    base_model,
    "./adapters/translation"
)

# 使用
inputs = tokenizer("Translate to French: Hello", return_tensors="pt")
outputs = translation_model.generate(**inputs)
```

2. 動態切換適配器（多適配器加載）：

```python
from peft import PeftModel

# 加載基礎模型
base_model = AutoModelForCausalLM.from_pretrained("gpt2")

# 加載第一個適配器
model = PeftModel.from_pretrained(base_model, "./adapters/translation")

# 加載額外的適配器
model.load_adapter("./adapters/summarization", adapter_name="summarization")
model.load_adapter("./adapters/qa", adapter_name="qa")

# 切換到不同適配器
model.set_adapter("summarization")  # 使用摘要適配器
outputs = model.generate(**inputs)

model.set_adapter("qa")  # 切換到 QA 適配器
outputs = model.generate(**inputs)
```

3. 列出所有適配器：

```python
# 查看已加載的適配器
print(model.peft_config.keys())
# 輸出: dict_keys(['default', 'summarization', 'qa'])
```

4. 卸載適配器：

```python
# 卸載特定適配器
model.delete_adapter("summarization")

# 禁用所有適配器（使用原始模型）
model.disable_adapter()

# 重新啟用
model.enable_adapter()
```
    """)


def adapter_fusion():
    """
    適配器融合技術
    """
    print("\n" + "=" * 70)
    print("適配器融合（Adapter Fusion）")
    print("=" * 70)

    print("""
適配器融合的概念：

1. 基本思想：
   • 組合多個任務的適配器
   • 學習如何混合它們的知識
   • 創建新的複合適配器

2. 方法一：加權平均
   ```python
   # 合併兩個適配器（平均權重）
   from peft import PeftModel

   # 這是概念性代碼，實際實現更復雜
   merged_weights = (adapter1_weights + adapter2_weights) / 2
   ```

3. 方法二：任務向量
   ```python
   # 計算任務向量
   task_vector = fine_tuned_weights - pretrained_weights

   # 縮放和添加
   new_weights = pretrained_weights + alpha * task_vector
   ```

4. PEFT 中的合併：
   ```python
   # 合併適配器到基礎模型
   model = model.merge_and_unload()

   # 現在模型包含適配器，可以當普通模型使用
   model.save_pretrained("./merged_model")
   ```

5. 多適配器組合：
   ```python
   # 加載多個適配器
   model.load_adapter("./task1", adapter_name="task1")
   model.load_adapter("./task2", adapter_name="task2")

   # 同時激活多個（實驗性功能）
   model.set_adapter(["task1", "task2"])
   ```
    """)


def multi_tenant_example():
    """
    多租戶場景示例
    """
    print("\n" + "=" * 70)
    print("多租戶 / 個性化場景")
    print("=" * 70)

    print("""
場景：SaaS 平台為每個客戶提供定制化模型

架構設計：

```python
class MultiTenantLLM:
    def __init__(self, base_model_path: str):
        # 加載共享的基礎模型
        self.base_model = AutoModelForCausalLM.from_pretrained(base_model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_path)

        # 適配器緩存
        self.adapters = {}

    def load_customer_adapter(self, customer_id: str, adapter_path: str):
        '''加載客戶專屬適配器'''
        if customer_id not in self.adapters:
            # 創建新的 PEFT 模型實例
            model = PeftModel.from_pretrained(
                self.base_model,
                adapter_path
            )
            self.adapters[customer_id] = model
        return self.adapters[customer_id]

    def generate_for_customer(self, customer_id: str, prompt: str):
        '''為特定客戶生成內容'''
        # 獲取客戶模型
        model = self.adapters.get(customer_id)
        if model is None:
            # 使用基礎模型
            model = self.base_model

        # 生成
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = model.generate(**inputs, max_new_tokens=50)
        return self.tokenizer.decode(outputs[0])

# 使用
llm_service = MultiTenantLLM("gpt2")

# 加載客戶適配器
llm_service.load_customer_adapter("customer_A", "./adapters/customer_A")
llm_service.load_customer_adapter("customer_B", "./adapters/customer_B")

# 為不同客戶生成
response_A = llm_service.generate_for_customer("customer_A", "產品描述：")
response_B = llm_service.generate_for_customer("customer_B", "產品描述：")
```

優勢：
✓ 一個基礎模型服務所有客戶
✓ 每個客戶有獨特的風格/知識
✓ 極低的存儲和計算成本
✓ 易於添加新客戶
    """)


def best_practices():
    """
    多任務 PEFT 最佳實踐
    """
    print("\n" + "=" * 70)
    print("最佳實踐")
    print("=" * 70)

    practices = {
        "1. 適配器組織": [
            "使用清晰的目錄結構 (./adapters/task_name/)",
            "為每個適配器添加元數據文件（任務描述、訓練日期等）",
            "使用版本控制管理適配器",
        ],
        "2. 訓練策略": [
            "所有任務使用相同的 LoRA 配置（便於管理）",
            "每個任務獨立訓練（避免災難性遺忘）",
            "保存訓練日誌和配置",
        ],
        "3. 部署優化": [
            "預加載常用適配器",
            "使用適配器緩存機制",
            "考慮適配器的懶加載",
        ],
        "4. 性能監控": [
            "跟踪每個適配器的性能指標",
            "定期評估和更新",
            "A/B 測試新舊適配器",
        ],
        "5. 資源管理": [
            "限制同時加載的適配器數量",
            "實現適配器 LRU 緩存",
            "監控內存使用",
        ],
    }

    for title, items in practices.items():
        print(f"\n{title}:")
        for item in items:
            print(f"  • {item}")


def cost_analysis():
    """
    成本分析
    """
    print("\n" + "=" * 70)
    print("多任務 PEFT 成本分析")
    print("=" * 70)

    print("""
場景：10 個不同任務

傳統方法（每任務一個模型）：
├─ 存儲: 10 × 14GB = 140GB
├─ 顯存: 14GB per task
├─ 訓練成本: 10 × 全量微調
└─ 部署複雜度: 管理 10 個模型

PEFT 方法（一個基礎模型 + 10 個適配器）：
├─ 存儲: 14GB + 10 × 3MB = 14.03GB
├─ 顯存: 14GB (基礎) + 3MB (當前適配器)
├─ 訓練成本: 10 × PEFT 微調（快 3-5 倍）
└─ 部署複雜度: 一個模型 + 動態加載適配器

成本節省：
✓ 存儲: 節省 90%
✓ 訓練時間: 節省 60-80%
✓ 顯存: 節省 ~90%
✓ 維護成本: 大幅降低

投資回報率（ROI）：
• 初始投資: 訓練基礎模型 + PEFT 設置
• 每增加一個任務: 只需訓練一個小適配器
• 邊際成本趨近於零
    """)


def main():
    """
    主函數：多任務 PEFT 完整教程
    """
    print("=" * 70)
    print("多任務學習與適配器管理")
    print("=" * 70)

    # 1. 概念講解
    explain_multi_task_peft()

    # 2. 訓練多個適配器
    train_multiple_adapters()

    # 3. 適配器管理
    manage_adapters()

    # 4. 適配器融合
    adapter_fusion()

    # 5. 多租戶示例
    multi_tenant_example()

    # 6. 最佳實踐
    best_practices()

    # 7. 成本分析
    cost_analysis()

    # 8. 總結
    print("\n" + "=" * 70)
    print("總結")
    print("=" * 70)
    print("""
多任務 PEFT 的核心價值：

1. 經濟高效：
   • 一個基礎模型，無限適配器
   • 存儲成本降低 90%
   • 訓練成本大幅降低

2. 靈活擴展：
   • 輕鬆添加新任務
   • 動態切換適配器
   • 支持個性化定制

3. 易於管理：
   • 統一的基礎模型
   • 模塊化的適配器
   • 簡化部署流程

4. 實際應用：
   • 企業多業務線
   • SaaS 多租戶
   • 研究多任務
   • 個性化服務

5. 最佳實踐：
   • 良好的組織結構
   • 獨立訓練各任務
   • 實現緩存機制
   • 持續監控性能
    """)

    print("\n下一步:")
    print("  • 查看 08_模型合併.py - 學習適配器合併技術")
    print("  • 查看 09_推理優化.py - 優化多適配器推理")
    print("  • 查看 10_生產部署.py - 生產環境部署指南")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用戶中斷")
    except Exception as e:
        print(f"\n程序執行出錯: {e}")
        import traceback
        traceback.print_exc()
