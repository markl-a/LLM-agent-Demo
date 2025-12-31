#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Guidance 多模型支援示例
====================================================

本模塊展示 Guidance 如何支持多種 LLM 後端:
1. OpenAI API (GPT-4, GPT-3.5)
2. Transformers 本地模型
3. vLLM 高性能推理
4. llama.cpp 輕量級部署
5. Azure OpenAI Service
6. 自定義模型後端
7. 模型切換和比較
8. 性能優化

Guidance 的統一接口讓你可以輕鬆在不同模型之間切換，
而無需修改核心邏輯代碼。

作者: Guidance 示例團隊
日期: 2025-01-01
"""

import os
import sys
from typing import Dict, List, Any, Optional
import json
import time
from datetime import datetime

try:
    from guidance import models, gen, select
    import guidance
except ImportError:
    print("錯誤: 請先安裝 guidance 庫")
    sys.exit(1)


class MultiModelDemo:
    """
    多模型支援演示類

    展示如何使用 Guidance 與不同的模型後端交互。
    """

    def __init__(self):
        """初始化多模型演示器"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.azure_key = os.getenv("AZURE_OPENAI_KEY")
        self.model_instances: Dict[str, Any] = {}
        self.benchmark_results: List[Dict] = []

    def example_openai_models(self) -> None:
        """
        示例 1: OpenAI API 模型

        演示如何使用不同的 OpenAI 模型。
        """
        print(f"\n{'='*60}")
        print("示例 1: OpenAI API 模型")
        print(f"{'='*60}\n")

        if not self.api_key:
            print("⚠️  未設置 OPENAI_API_KEY，跳過此示例")
            return

        # GPT-4
        print("使用 GPT-4:")
        lm_gpt4 = models.OpenAI(
            model="gpt-4",
            api_key=self.api_key,
            temperature=0.7
        )

        lm_gpt4 += "用一句話解釋量子計算: "
        lm_gpt4 += gen(name="explanation", max_tokens=80)

        print(f"GPT-4 回答: {lm_gpt4['explanation']}\n")
        self.model_instances["gpt-4"] = lm_gpt4

        # GPT-3.5 Turbo
        print("使用 GPT-3.5 Turbo:")
        lm_gpt35 = models.OpenAI(
            model="gpt-3.5-turbo",
            api_key=self.api_key,
            temperature=0.7
        )

        lm_gpt35 += "用一句話解釋量子計算: "
        lm_gpt35 += gen(name="explanation", max_tokens=80)

        print(f"GPT-3.5 回答: {lm_gpt35['explanation']}\n")
        self.model_instances["gpt-3.5-turbo"] = lm_gpt35

        # 比較回答
        print("模型回答比較:")
        print(f"  GPT-4:       {lm_gpt4['explanation'][:100]}...")
        print(f"  GPT-3.5:     {lm_gpt35['explanation'][:100]}...\n")

    def example_model_parameters(self) -> None:
        """
        示例 2: 模型參數調整

        演示如何調整不同的模型參數。
        """
        print(f"\n{'='*60}")
        print("示例 2: 模型參數調整")
        print(f"{'='*60}\n")

        if not self.api_key:
            print("⚠️  未設置 API 密鑰，跳過此示例")
            return

        prompt = "生成一個創意故事標題: "

        # 不同溫度參數
        temperatures = [0.1, 0.5, 0.9, 1.2]

        print("測試不同溫度參數:")
        for temp in temperatures:
            lm = models.OpenAI(
                model="gpt-4",
                api_key=self.api_key,
                temperature=temp
            )

            lm += prompt
            lm += gen(name="title", max_tokens=30)

            print(f"  溫度 {temp}: {lm['title']}")

        print()

        # Top-p 採樣
        top_p_values = [0.5, 0.9, 0.95, 1.0]

        print("測試不同 top_p 值:")
        for top_p in top_p_values:
            lm = models.OpenAI(
                model="gpt-4",
                api_key=self.api_key,
                top_p=top_p,
                temperature=0.7
            )

            lm += prompt
            lm += gen(name="title", max_tokens=30)

            print(f"  top_p {top_p}: {lm['title']}")

        print()

        # Max tokens 限制
        max_tokens_values = [10, 30, 50, 100]

        print("測試不同 max_tokens:")
        for max_tokens in max_tokens_values:
            lm = models.OpenAI(
                model="gpt-4",
                api_key=self.api_key,
                max_tokens=max_tokens
            )

            lm += "寫一篇關於 AI 的文章: "
            lm += gen(name="content", max_tokens=max_tokens)

            print(f"  max_tokens {max_tokens}: {len(lm['content'])} 字符")

        print()

    def example_transformers_backend(self) -> None:
        """
        示例 3: Transformers 本地模型

        演示如何使用 Hugging Face Transformers 本地模型。
        """
        print(f"\n{'='*60}")
        print("示例 3: Transformers 本地模型")
        print(f"{'='*60}\n")

        try:
            import transformers
        except ImportError:
            print("⚠️  未安裝 transformers 庫，跳過此示例")
            print("安裝: pip install transformers torch")
            return

        print("使用本地 Transformers 模型:")
        print("(此示例展示概念，實際執行需要下載模型)\n")

        # 示例代碼 (實際使用需要根據具體模型調整)
        code_example = """
# 加載本地模型
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "gpt2"  # 或其他模型
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# 使用 Guidance
from guidance import models

lm = models.Transformers(
    model=model,
    tokenizer=tokenizer,
    device="cuda"  # 或 "cpu"
)

lm += "Once upon a time"
lm += gen(name="story", max_tokens=50)
print(lm["story"])
"""

        print("示例代碼:")
        print(code_example)

        print("\n支持的本地模型:")
        local_models = [
            "gpt2",
            "gpt2-medium",
            "gpt2-large",
            "EleutherAI/gpt-neo-2.7B",
            "facebook/opt-1.3b",
            "bigscience/bloom-7b1",
            "meta-llama/Llama-2-7b-hf"
        ]

        for i, model in enumerate(local_models, 1):
            print(f"  {i}. {model}")

        print()

    def example_vllm_backend(self) -> None:
        """
        示例 4: vLLM 高性能推理

        演示如何使用 vLLM 進行高效批量推理。
        """
        print(f"\n{'='*60}")
        print("示例 4: vLLM 高性能推理")
        print(f"{'='*60}\n")

        try:
            import vllm
        except ImportError:
            print("⚠️  未安裝 vllm 庫，跳過此示例")
            print("安裝: pip install vllm")
            return

        print("使用 vLLM 進行高性能推理:")
        print("(此示例展示概念，實際執行需要 GPU 支持)\n")

        code_example = """
from vllm import LLM, SamplingParams
from guidance import models

# 初始化 vLLM
vllm_model = LLM(
    model="meta-llama/Llama-2-7b-hf",
    tensor_parallel_size=1
)

# 使用 Guidance
lm = models.VLLM(vllm_model)

# 批量推理
prompts = [
    "Explain quantum computing",
    "What is machine learning",
    "Describe blockchain"
]

for prompt in prompts:
    lm += prompt + ": "
    lm += gen(name="answer", max_tokens=100)
    print(lm["answer"])
"""

        print("示例代碼:")
        print(code_example)

        print("\nvLLM 的優勢:")
        advantages = [
            "高吞吐量: PagedAttention 算法",
            "批量推理: 有效利用 GPU",
            "低延遲: 優化的 CUDA 內核",
            "動態批處理: 自動優化批次大小",
            "支持多種模型: LLaMA, GPT, OPT 等"
        ]

        for i, adv in enumerate(advantages, 1):
            print(f"  {i}. {adv}")

        print()

    def example_llama_cpp_backend(self) -> None:
        """
        示例 5: llama.cpp 輕量級部署

        演示如何使用 llama.cpp 進行輕量級模型部署。
        """
        print(f"\n{'='*60}")
        print("示例 5: llama.cpp 輕量級部署")
        print(f"{'='*60}\n")

        print("使用 llama.cpp 進行輕量級部署:")
        print("(適合 CPU 環境和資源受限場景)\n")

        code_example = """
from llama_cpp import Llama
from guidance import models

# 加載量化模型
llm = Llama(
    model_path="./models/llama-2-7b.gguf",
    n_ctx=2048,        # 上下文長度
    n_threads=8,       # CPU 線程數
    n_gpu_layers=0     # CPU 模式
)

# 使用 Guidance
lm = models.LlamaCpp(llm)

lm += "Question: What is AI?\\nAnswer: "
lm += gen(name="answer", max_tokens=100)
print(lm["answer"])
"""

        print("示例代碼:")
        print(code_example)

        print("\nllama.cpp 的特點:")
        features = [
            "純 C/C++ 實現，無需 Python",
            "支持 CPU 推理",
            "模型量化 (4-bit, 8-bit)",
            "低內存佔用",
            "跨平台支持 (Linux, Windows, macOS)",
            "支持 Metal (macOS), CUDA (NVIDIA), OpenCL"
        ]

        for i, feat in enumerate(features, 1):
            print(f"  {i}. {feat}")

        print()

    def example_azure_openai(self) -> None:
        """
        示例 6: Azure OpenAI Service

        演示如何使用 Azure OpenAI Service。
        """
        print(f"\n{'='*60}")
        print("示例 6: Azure OpenAI Service")
        print(f"{'='*60}\n")

        if not self.azure_key:
            print("⚠️  未設置 AZURE_OPENAI_KEY，跳過此示例")
            print("需要設置: AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT\n")

            print("示例配置:")
            config_example = """
# 環境變量
export AZURE_OPENAI_KEY="your-api-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT="gpt-4"

# 使用代碼
from guidance import models

lm = models.AzureOpenAI(
    deployment_name="gpt-4",
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2023-05-15"
)

lm += "Explain Azure: "
lm += gen(name="explanation", max_tokens=100)
print(lm["explanation"])
"""
            print(config_example)
            return

        # 如果有配置，實際使用
        print("使用 Azure OpenAI Service:")

        try:
            lm_azure = models.AzureOpenAI(
                deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4"),
                api_key=self.azure_key,
                api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_version="2023-05-15"
            )

            lm_azure += "What is Azure? "
            lm_azure += gen(name="answer", max_tokens=80)

            print(f"Azure OpenAI 回答: {lm_azure['answer']}\n")

        except Exception as e:
            print(f"✗ Azure OpenAI 初始化失敗: {str(e)}\n")

    def example_model_comparison(self) -> None:
        """
        示例 7: 模型比較

        演示如何比較不同模型的輸出。
        """
        print(f"\n{'='*60}")
        print("示例 7: 模型比較")
        print(f"{'='*60}\n")

        if not self.api_key:
            print("⚠️  未設置 API 密鑰，跳過此示例")
            return

        question = "什麼是深度學習?"

        models_to_compare = [
            {"name": "GPT-4", "model": "gpt-4"},
            {"name": "GPT-3.5", "model": "gpt-3.5-turbo"}
        ]

        print(f"問題: {question}\n")
        print("不同模型的回答:\n")

        results = []

        for model_info in models_to_compare:
            start_time = time.time()

            lm = models.OpenAI(
                model=model_info["model"],
                api_key=self.api_key,
                temperature=0.7
            )

            lm += f"{question} "
            lm += gen(name="answer", max_tokens=100)

            elapsed = time.time() - start_time

            result = {
                "model": model_info["name"],
                "answer": lm["answer"],
                "length": len(lm["answer"]),
                "time": elapsed
            }

            results.append(result)

            print(f"{model_info['name']}:")
            print(f"  回答: {lm['answer'][:100]}...")
            print(f"  長度: {len(lm['answer'])} 字符")
            print(f"  耗時: {elapsed:.2f} 秒\n")

        # 統計
        print("統計摘要:")
        print(f"  平均回答長度: {sum(r['length'] for r in results) / len(results):.0f} 字符")
        print(f"  平均耗時: {sum(r['time'] for r in results) / len(results):.2f} 秒\n")

    def example_custom_backend(self) -> None:
        """
        示例 8: 自定義模型後端

        演示如何實現自定義的模型後端。
        """
        print(f"\n{'='*60}")
        print("示例 8: 自定義模型後端")
        print(f"{'='*60}\n")

        print("實現自定義模型後端:\n")

        custom_backend_code = """
from guidance import models
from guidance.models import Model

class CustomModel(Model):
    '''自定義模型後端'''

    def __init__(self, model_name: str, **kwargs):
        super().__init__()
        self.model_name = model_name
        self.config = kwargs

    def _generate(self, prompt: str, max_tokens: int = 100) -> str:
        '''
        實現生成邏輯

        這裡可以調用任何自定義的 API 或本地模型
        '''
        # 示例: 調用自定義 API
        import requests

        response = requests.post(
            "https://your-custom-api.com/generate",
            json={
                "prompt": prompt,
                "max_tokens": max_tokens,
                "model": self.model_name
            }
        )

        return response.json()["text"]

    def __add__(self, value):
        # 實現 += 操作符
        if isinstance(value, str):
            self._current_text += value
        return self

# 使用自定義後端
lm = CustomModel(
    model_name="custom-gpt",
    api_key="your-key",
    temperature=0.7
)

lm += "Generate text: "
lm += gen(name="text", max_tokens=50)
print(lm["text"])
"""

        print(custom_backend_code)

        print("\n自定義後端的應用場景:")
        use_cases = [
            "私有部署的模型 API",
            "本地優化的推理引擎",
            "特定領域的微調模型",
            "多模型集成和路由",
            "自定義緩存和優化策略"
        ]

        for i, use_case in enumerate(use_cases, 1):
            print(f"  {i}. {use_case}")

        print()

    def example_performance_benchmark(self) -> None:
        """
        示例 9: 性能基準測試

        演示如何對不同模型後端進行性能測試。
        """
        print(f"\n{'='*60}")
        print("示例 9: 性能基準測試")
        print(f"{'='*60}\n")

        if not self.api_key:
            print("⚠️  未設置 API 密鑰，跳過此示例")
            return

        test_prompts = [
            "解釋機器學習",
            "什麼是區塊鏈",
            "描述量子計算",
            "介紹深度學習",
            "說明人工智能"
        ]

        models_to_test = ["gpt-3.5-turbo", "gpt-4"]

        print("開始性能基準測試...\n")

        for model_name in models_to_test:
            print(f"測試模型: {model_name}")

            total_time = 0
            total_tokens = 0

            for i, prompt in enumerate(test_prompts, 1):
                start = time.time()

                lm = models.OpenAI(
                    model=model_name,
                    api_key=self.api_key,
                    max_tokens=50
                )

                lm += prompt + ": "
                lm += gen(name="answer", max_tokens=50)

                elapsed = time.time() - start
                total_time += elapsed
                total_tokens += len(lm["answer"])

                print(f"  提示 {i}: {elapsed:.2f}s")

            avg_time = total_time / len(test_prompts)
            avg_tokens = total_tokens / len(test_prompts)

            print(f"\n{model_name} 統計:")
            print(f"  平均延遲: {avg_time:.2f}s")
            print(f"  平均生成: {avg_tokens:.0f} 字符")
            print(f"  總耗時: {total_time:.2f}s\n")

            self.benchmark_results.append({
                "model": model_name,
                "avg_latency": avg_time,
                "avg_tokens": avg_tokens,
                "total_time": total_time
            })

    def example_model_fallback(self) -> None:
        """
        示例 10: 模型回退策略

        演示如何實現模型回退和容錯機制。
        """
        print(f"\n{'='*60}")
        print("示例 10: 模型回退策略")
        print(f"{'='*60}\n")

        print("實現模型回退策略:\n")

        fallback_code = """
from guidance import models
import logging

class ModelWithFallback:
    '''帶回退機制的模型包裝器'''

    def __init__(self, primary_model, fallback_models):
        self.primary = primary_model
        self.fallbacks = fallback_models
        self.logger = logging.getLogger(__name__)

    def generate(self, prompt, max_tokens=100):
        # 嘗試主模型
        try:
            self.logger.info(f"使用主模型: {self.primary}")
            lm = models.OpenAI(model=self.primary)
            lm += prompt
            lm += gen(name="result", max_tokens=max_tokens)
            return lm["result"]

        except Exception as e:
            self.logger.warning(f"主模型失敗: {e}")

            # 嘗試回退模型
            for fallback in self.fallbacks:
                try:
                    self.logger.info(f"使用回退模型: {fallback}")
                    lm = models.OpenAI(model=fallback)
                    lm += prompt
                    lm += gen(name="result", max_tokens=max_tokens)
                    return lm["result"]

                except Exception as e:
                    self.logger.warning(f"回退模型 {fallback} 失敗: {e}")
                    continue

            raise Exception("所有模型都失敗了")

# 使用示例
model_chain = ModelWithFallback(
    primary_model="gpt-4",
    fallback_models=["gpt-3.5-turbo", "gpt-3.5-turbo-16k"]
)

result = model_chain.generate("什麼是 AI?")
print(result)
"""

        print(fallback_code)

        print("\n回退策略的優勢:")
        benefits = [
            "提高系統可靠性",
            "應對 API 限流和故障",
            "成本優化 (優先使用便宜模型)",
            "負載均衡",
            "保證服務連續性"
        ]

        for i, benefit in enumerate(benefits, 1):
            print(f"  {i}. {benefit}")

        print()

    def run_all_examples(self) -> None:
        """運行所有示例"""
        print(f"\n{'='*60}")
        print("Guidance 多模型支援 - 完整示例")
        print(f"{'='*60}")

        self.example_openai_models()
        self.example_model_parameters()
        self.example_transformers_backend()
        self.example_vllm_backend()
        self.example_llama_cpp_backend()
        self.example_azure_openai()
        self.example_model_comparison()
        self.example_custom_backend()
        self.example_performance_benchmark()
        self.example_model_fallback()

        print(f"\n{'='*60}")
        print("執行摘要")
        print(f"{'='*60}")
        print(f"✓ 所有多模型支援示例執行完成!")

        if self.benchmark_results:
            print(f"\n性能基準測試結果:")
            print(json.dumps(self.benchmark_results, indent=2, ensure_ascii=False))


def main():
    """主函數"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║         Guidance 框架 - 多模型支援示例                     ║
    ║                                                            ║
    ║  統一接口支持多種 LLM 後端                                 ║
    ║  包括 OpenAI, Transformers, vLLM, llama.cpp 等             ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    demo = MultiModelDemo()

    try:
        demo.run_all_examples()
    except KeyboardInterrupt:
        print("\n\n⚠️  用戶中斷執行")
    except Exception as e:
        print(f"\n✗ 執行出錯: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
