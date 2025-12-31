"""
PEFT 推理優化

這個文件介紹 PEFT 模型的推理優化技術，包括：
1. 合併適配器以加速推理
2. 批處理優化
3. 量化推理
4. 緩存機制
5. 多適配器批次推理

優化推理可以大幅提升服務性能和吞吐量。
"""

import torch
import time
import warnings

warnings.filterwarnings('ignore')


def explain_inference_optimization():
    """
    解釋推理優化的概念
    """
    print("=" * 70)
    print("PEFT 推理優化概述")
    print("=" * 70)

    print("""
PEFT 推理的性能考慮：

1. 推理流程對比：

   未優化的 PEFT 推理：
   ┌────────────────────────────────┐
   │ 輸入 → 基礎模型 (W·x)         │
   │      → LoRA 計算 (BA·x)       │
   │      → 相加 (W·x + BA·x)      │
   │ 輸出                           │
   └────────────────────────────────┘
   問題: 兩次矩陣乘法，額外計算開銷

   優化後的推理：
   ┌────────────────────────────────┐
   │ 預處理: W' = W + BA (一次性)  │
   │ 推理: 輸入 → W'·x → 輸出      │
   └────────────────────────────────┘
   優勢: 一次矩陣乘法，無額外開銷

2. 性能指標對比：

   ┌────────────────┬─────────┬─────────┬─────────┐
   │ 方法           │ 延遲    │ 吞吐量  │ 顯存    │
   ├────────────────┼─────────┼─────────┼─────────┤
   │ 未合併 PEFT    │ 基準    │ 基準    │ 基準    │
   │ 合併後         │ 0.7x    │ 1.4x    │ 0.95x   │
   │ 合併+量化      │ 0.4x    │ 3.0x    │ 0.4x    │
   │ 合併+批處理    │ 0.3x    │ 5.0x    │ 1.5x    │
   └────────────────┴─────────┴─────────┴─────────┘

3. 優化策略：

   Level 1: 基礎優化（必做）
   • 合併適配器
   • 使用 torch.inference_mode()

   Level 2: 進階優化
   • 使用混合精度 (FP16/BF16)
   • 批處理
   • KV 緩存

   Level 3: 極致優化
   • 模型量化 (INT8/INT4)
   • 算子融合
   • GPU 優化庫（FlashAttention）
    """)


def basic_optimization():
    """
    基礎優化技術
    """
    print("\n" + "=" * 70)
    print("基礎優化技術")
    print("=" * 70)

    print("""
1. 合併適配器（最重要）：

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM

# 加載模型
base_model = AutoModelForCausalLM.from_pretrained("gpt2")
peft_model = PeftModel.from_pretrained(base_model, "./lora_adapter")

# 合併適配器
model = peft_model.merge_and_unload()

# 現在推理更快
inputs = tokenizer("Test", return_tensors="pt")
with torch.inference_mode():  # 進一步優化
    outputs = model.generate(**inputs)
```

2. 使用正確的推理模式：

```python
# 方法 1: torch.inference_mode() (推薦)
with torch.inference_mode():
    outputs = model.generate(**inputs)

# 方法 2: torch.no_grad() (較舊)
with torch.no_grad():
    outputs = model.generate(**inputs)

# 性能對比:
# inference_mode: 禁用 autograd + 優化
# no_grad: 只禁用 autograd
```

3. 模型評估模式：

```python
# 設置為評估模式
model.eval()

# 這會：
# • 禁用 Dropout
# • 使用 BatchNorm 的統計量
# • 提升推理速度和一致性
```

4. 設備優化：

```python
# 確保模型在 GPU 上
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)

# 輸入也要在同一設備
inputs = {k: v.to(device) for k, v in inputs.items()}
```
    """)


def mixed_precision_inference():
    """
    混合精度推理
    """
    print("\n" + "=" * 70)
    print("混合精度推理")
    print("=" * 70)

    print("""
1. FP16 推理（Float16）：

```python
# 方法 1: 轉換模型
model = model.half()  # FP32 → FP16

# 方法 2: 使用 torch.cuda.amp
with torch.cuda.amp.autocast():
    outputs = model.generate(**inputs)
```

2. BF16 推理（BFloat16，推薦）：

```python
# 需要較新的 GPU (Ampere+)
model = model.to(torch.bfloat16)

# 或使用 autocast
with torch.cuda.amp.autocast(dtype=torch.bfloat16):
    outputs = model.generate(**inputs)
```

3. 性能對比：

┌──────────┬──────────┬──────────┬──────────┐
│ 精度     │ 速度     │ 顯存     │ 精度損失 │
├──────────┼──────────┼──────────┼──────────┤
│ FP32     │ 1.0x     │ 1.0x     │ 無       │
│ FP16     │ 2.0x     │ 0.5x     │ 極小     │
│ BF16     │ 2.0x     │ 0.5x     │ 更小     │
│ INT8     │ 3-4x     │ 0.25x    │ 小       │
└──────────┴──────────┴──────────┴──────────┘

4. 完整示例：

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")

# 轉換為 BF16
model = model.to(torch.bfloat16).cuda()
model.eval()

# 推理
inputs = tokenizer("Hello", return_tensors="pt").to("cuda")

with torch.inference_mode():
    outputs = model.generate(
        **inputs,
        max_new_tokens=50,
        do_sample=False,  # 貪婪解碼更快
    )

print(tokenizer.decode(outputs[0]))
```
    """)


def batching_optimization():
    """
    批處理優化
    """
    print("\n" + "=" * 70)
    print("批處理優化")
    print("=" * 70)

    print("""
1. 動態批處理：

```python
def generate_batch(model, tokenizer, prompts, batch_size=8):
    '''批量生成'''
    all_outputs = []

    for i in range(0, len(prompts), batch_size):
        batch_prompts = prompts[i:i + batch_size]

        # 批量編碼
        inputs = tokenizer(
            batch_prompts,
            padding=True,  # 填充到相同長度
            truncation=True,
            return_tensors="pt"
        ).to(model.device)

        # 批量生成
        with torch.inference_mode():
            outputs = model.generate(
                **inputs,
                max_new_tokens=50,
                pad_token_id=tokenizer.pad_token_id,
            )

        # 解碼
        decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        all_outputs.extend(decoded)

    return all_outputs

# 使用
prompts = ["Prompt 1", "Prompt 2", ..., "Prompt 100"]
results = generate_batch(model, tokenizer, prompts, batch_size=16)
```

2. 批次大小選擇：

```python
import torch

def find_optimal_batch_size(model, tokenizer, max_batch_size=32):
    '''找到最優批次大小'''
    for batch_size in [1, 2, 4, 8, 16, 32]:
        if batch_size > max_batch_size:
            break

        try:
            # 測試
            prompts = ["Test"] * batch_size
            inputs = tokenizer(prompts, padding=True, return_tensors="pt").to(model.device)

            with torch.inference_mode():
                _ = model.generate(**inputs, max_new_tokens=10)

            print(f"✓ Batch size {batch_size} works")
            optimal_batch_size = batch_size

        except RuntimeError as e:
            if "out of memory" in str(e):
                print(f"✗ Batch size {batch_size} OOM")
                break
            raise

        # 清理
        torch.cuda.empty_cache()

    return optimal_batch_size
```

3. 吞吐量測試：

```python
import time

def benchmark_throughput(model, tokenizer, batch_sizes=[1, 4, 8, 16]):
    '''測試不同批次大小的吞吐量'''
    num_samples = 100
    prompt = "Test prompt"

    for batch_size in batch_sizes:
        prompts = [prompt] * batch_size
        num_batches = num_samples // batch_size

        start = time.time()

        for _ in range(num_batches):
            inputs = tokenizer(prompts, padding=True, return_tensors="pt").to(model.device)
            with torch.inference_mode():
                _ = model.generate(**inputs, max_new_tokens=20)

        elapsed = time.time() - start
        throughput = num_samples / elapsed

        print(f"Batch size {batch_size}: {throughput:.2f} samples/sec")
```
    """)


def quantization_inference():
    """
    量化推理
    """
    print("\n" + "=" * 70)
    print("量化推理")
    print("=" * 70)

    print("""
1. 8-bit 量化推理：

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

# 配置 8-bit 量化
quantization_config = BitsAndBytesConfig(load_in_8bit=True)

# 加載量化模型
model = AutoModelForCausalLM.from_pretrained(
    "gpt2",
    quantization_config=quantization_config,
    device_map="auto"
)

# 推理（自動使用量化）
with torch.inference_mode():
    outputs = model.generate(**inputs)
```

2. 4-bit 量化推理（更激進）：

```python
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16
)

model = AutoModelForCausalLM.from_pretrained(
    "model_name",
    quantization_config=quantization_config,
    device_map="auto"
)
```

3. 動態量化（PyTorch）：

```python
import torch.quantization

# 動態量化（推理時）
model_quantized = torch.quantization.quantize_dynamic(
    model,
    {torch.nn.Linear},  # 量化線性層
    dtype=torch.qint8
)
```

4. 性能對比：

顯存使用（7B 模型）：
• FP32: ~28 GB
• FP16: ~14 GB
• INT8: ~7 GB
• INT4: ~3.5 GB

速度：
• INT8: 1.5-2x 加速
• INT4: 2-3x 加速
```
    """)


def caching_strategies():
    """
    緩存策略
    """
    print("\n" + "=" * 70)
    print("緩存策略")
    print("=" * 70)

    print("""
1. KV 緩存（自動）：

```python
# transformers 自動啟用 KV 緩存
outputs = model.generate(
    **inputs,
    max_new_tokens=100,
    use_cache=True,  # 默認值，啟用 KV 緩存
)

# KV 緩存存儲過去的 key 和 value
# 避免重複計算，加速自回歸生成
```

2. 預填充緩存（Prefix Caching）：

```python
# 對於重複的前綴，可以預計算並緩存
class PrefixCache:
    def __init__(self, model):
        self.model = model
        self.cache = {}

    def get_cached_prefix(self, prefix):
        if prefix in self.cache:
            return self.cache[prefix]

        # 計算前綴的 KV 緩存
        inputs = tokenizer(prefix, return_tensors="pt")
        with torch.inference_mode():
            outputs = self.model(**inputs, use_cache=True)

        # 緩存
        self.cache[prefix] = outputs.past_key_values
        return outputs.past_key_values

    def generate_with_prefix(self, prefix, continuation):
        # 獲取緩存的前綴
        past_kv = self.get_cached_prefix(prefix)

        # 只處理新的 token
        continuation_ids = tokenizer(continuation, return_tensors="pt").input_ids

        outputs = self.model.generate(
            continuation_ids,
            past_key_values=past_kv,
            max_new_tokens=50
        )
        return outputs
```

3. 適配器緩存：

```python
class AdapterCache:
    '''緩存多個適配器'''
    def __init__(self, base_model):
        self.base_model = base_model
        self.adapters = {}

    def load_adapter(self, adapter_name, adapter_path):
        if adapter_name not in self.adapters:
            model = PeftModel.from_pretrained(
                self.base_model,
                adapter_path
            )
            self.adapters[adapter_name] = model.merge_and_unload()

        return self.adapters[adapter_name]

    def generate(self, adapter_name, inputs):
        model = self.adapters.get(adapter_name, self.base_model)
        return model.generate(**inputs)
```
    """)


def production_optimization():
    """
    生產環境優化
    """
    print("\n" + "=" * 70)
    print("生產環境優化")
    print("=" * 70)

    print("""
1. 完整的優化推理配置：

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class OptimizedInference:
    def __init__(self, model_path, device="cuda"):
        # 加載模型
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.bfloat16,  # BF16
            device_map="auto",
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)

        # 設置評估模式
        self.model.eval()

        # 編譯模型（PyTorch 2.0+）
        if hasattr(torch, 'compile'):
            self.model = torch.compile(self.model)

    def generate(self, prompts, max_new_tokens=50, batch_size=8):
        '''優化的批量生成'''
        all_outputs = []

        for i in range(0, len(prompts), batch_size):
            batch = prompts[i:i + batch_size]

            # 編碼
            inputs = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                return_tensors="pt"
            ).to(self.model.device)

            # 生成
            with torch.inference_mode():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=False,
                    use_cache=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                )

            # 解碼
            decoded = self.tokenizer.batch_decode(
                outputs,
                skip_special_tokens=True
            )
            all_outputs.extend(decoded)

        return all_outputs

# 使用
inference = OptimizedInference("./merged_model")
results = inference.generate(["Prompt 1", "Prompt 2", ...])
```

2. 性能監控：

```python
import time
import psutil
import torch

class PerformanceMonitor:
    def __init__(self):
        self.reset()

    def reset(self):
        self.start_time = time.time()
        self.num_requests = 0
        self.total_tokens = 0

    def log_request(self, num_tokens):
        self.num_requests += 1
        self.total_tokens += num_tokens

    def get_stats(self):
        elapsed = time.time() - self.start_time
        return {
            "requests_per_sec": self.num_requests / elapsed,
            "tokens_per_sec": self.total_tokens / elapsed,
            "avg_tokens_per_request": self.total_tokens / self.num_requests,
            "gpu_memory_used": torch.cuda.memory_allocated() / 1e9,
            "cpu_percent": psutil.cpu_percent(),
        }
```
    """)


def main():
    """
    主函數：推理優化完整教程
    """
    print("=" * 70)
    print("PEFT 推理優化完整指南")
    print("=" * 70)

    # 1. 概述
    explain_inference_optimization()

    # 2. 基礎優化
    basic_optimization()

    # 3. 混合精度
    mixed_precision_inference()

    # 4. 批處理
    batching_optimization()

    # 5. 量化
    quantization_inference()

    # 6. 緩存
    caching_strategies()

    # 7. 生產優化
    production_optimization()

    # 8. 總結
    print("\n" + "=" * 70)
    print("總結")
    print("=" * 70)
    print("""
PEFT 推理優化關鍵要點：

1. 必做優化（Level 1）：
   ✓ 合併適配器 (merge_and_unload)
   ✓ 使用 torch.inference_mode()
   ✓ 設置 model.eval()
   → 速度提升: 30-50%

2. 進階優化（Level 2）：
   ✓ 混合精度（BF16/FP16）
   ✓ 批處理
   ✓ KV 緩存
   → 額外提升: 2-3x

3. 極致優化（Level 3）：
   ✓ 模型量化（INT8/INT4）
   ✓ torch.compile（PyTorch 2.0+）
   ✓ FlashAttention
   → 總提升: 5-10x

4. 優化優先級：
   1. 合併適配器（最重要，免費的性能）
   2. 批處理（吞吐量提升最大）
   3. 混合精度（顯存減半，速度翻倍）
   4. 量化（進一步壓縮）

5. 實際建議：
   • 開發: 快速迭代，不過度優化
   • 測試: 建立性能基準
   • 生產: 應用所有適用的優化
    """)

    print("\n下一步:")
    print("  • 查看 10_生產部署.py - 完整的生產部署指南")

    print("\n資源:")
    print("  • PyTorch 推理優化: https://pytorch.org/tutorials/recipes/recipes/tuning_guide.html")
    print("  • HuggingFace 優化: https://huggingface.co/docs/transformers/perf_infer_gpu_one")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用戶中斷")
    except Exception as e:
        print(f"\n程序執行出錯: {e}")
        import traceback
        traceback.print_exc()
