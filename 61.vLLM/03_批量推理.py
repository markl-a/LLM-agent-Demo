#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
vLLM 批量推理示例
=================

本示例展示 vLLM 的批量推理能力，包括：
1. 靜態批處理
2. 動態批處理（連續批處理）
3. 大規模批量推理
4. 批量推理性能優化
5. 批量推理的實際應用場景

vLLM 的核心優勢之一就是高效的批處理能力，
可以同時處理大量請求並最大化 GPU 利用率。

適用場景：
- 數據集批量處理
- 離線推理任務
- 大規模文本生成
- API 服務後端
"""

import time
import sys
from typing import List, Dict
from vllm import LLM, SamplingParams


def simple_batch_inference():
    """
    簡單批量推理

    展示如何一次處理多個提示詞
    """
    print("=" * 80)
    print("示例 1: 簡單批量推理")
    print("=" * 80)

    try:
        # 初始化模型
        print("\n正在加載模型...")
        llm = LLM(model="facebook/opt-125m", trust_remote_code=True)
        print("✓ 模型加載成功！")

        # 準備批量提示詞
        prompts = [
            "The future of technology is",
            "Artificial intelligence will",
            "In the next decade, we will see",
            "The most important innovation is",
            "Machine learning helps us",
        ]

        # 設置採樣參數
        sampling_params = SamplingParams(
            temperature=0.8,
            top_p=0.95,
            max_tokens=50,
        )

        print(f"\n批量處理 {len(prompts)} 個提示詞...")
        start_time = time.time()

        # 批量生成
        outputs = llm.generate(prompts, sampling_params)

        end_time = time.time()
        elapsed_time = end_time - start_time

        # 打印結果
        print("\n生成結果：")
        print("-" * 80)
        for i, output in enumerate(outputs):
            prompt = output.prompt
            generated_text = output.outputs[0].text
            print(f"\n[{i+1}] 提示詞: {prompt}")
            print(f"    生成: {generated_text[:100]}...")

        # 性能統計
        total_tokens = sum(len(output.outputs[0].token_ids) for output in outputs)
        print("\n" + "=" * 80)
        print("性能統計：")
        print(f"  - 總耗時: {elapsed_time:.2f} 秒")
        print(f"  - 平均每個請求: {elapsed_time/len(prompts):.3f} 秒")
        print(f"  - 總生成 tokens: {total_tokens}")
        print(f"  - 吞吐量: {total_tokens/elapsed_time:.2f} tokens/秒")

    except Exception as e:
        print(f"✗ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


def large_scale_batch_inference():
    """
    大規模批量推理

    處理數百個請求，展示 vLLM 的高吞吐量能力
    """
    print("\n" + "=" * 80)
    print("示例 2: 大規模批量推理")
    print("=" * 80)

    try:
        print("\n正在加載模型...")
        llm = LLM(
            model="facebook/opt-125m",
            trust_remote_code=True,
            gpu_memory_utilization=0.9,  # 提高 GPU 利用率
        )

        # 生成大量提示詞
        num_requests = 100
        prompts = [
            f"Question {i}: What is the meaning of life?"
            for i in range(num_requests)
        ]

        sampling_params = SamplingParams(
            temperature=0.7,
            max_tokens=30,
        )

        print(f"\n批量處理 {num_requests} 個請求...")
        print("vLLM 會自動優化批處理以最大化吞吐量...")

        start_time = time.time()

        # 批量生成
        outputs = llm.generate(prompts, sampling_params)

        end_time = time.time()
        elapsed_time = end_time - start_time

        # 統計信息
        total_tokens = sum(len(output.outputs[0].token_ids) for output in outputs)
        throughput = total_tokens / elapsed_time

        print("\n" + "=" * 80)
        print("大規模批量推理統計：")
        print(f"  - 請求數量: {num_requests}")
        print(f"  - 總耗時: {elapsed_time:.2f} 秒")
        print(f"  - 平均延遲: {elapsed_time/num_requests:.3f} 秒/請求")
        print(f"  - 總生成 tokens: {total_tokens}")
        print(f"  - 吞吐量: {throughput:.2f} tokens/秒")
        print(f"  - QPS: {num_requests/elapsed_time:.2f} 請求/秒")

        # 顯示部分結果
        print("\n前 5 個生成結果示例：")
        print("-" * 80)
        for i in range(min(5, len(outputs))):
            print(f"[{i+1}] {outputs[i].outputs[0].text[:80]}...")

    except Exception as e:
        print(f"✗ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


def batch_with_different_lengths():
    """
    處理不同長度的輸入

    展示 vLLM 如何高效處理長度不一的批量請求
    """
    print("\n" + "=" * 80)
    print("示例 3: 不同長度的批量推理")
    print("=" * 80)

    try:
        llm = LLM(model="facebook/opt-125m", trust_remote_code=True)

        # 不同長度的提示詞
        prompts = [
            "AI",  # 短
            "The development of artificial intelligence",  # 中
            "In recent years, the rapid advancement of artificial intelligence and machine learning technologies has transformed",  # 長
            "Hello",  # 短
            "The impact of climate change on global ecosystems",  # 中
        ]

        # 為不同提示詞設置不同的最大生成長度
        sampling_params_list = [
            SamplingParams(temperature=0.8, max_tokens=20),   # 短輸入，短輸出
            SamplingParams(temperature=0.8, max_tokens=40),   # 中等
            SamplingParams(temperature=0.8, max_tokens=60),   # 長輸入，長輸出
            SamplingParams(temperature=0.8, max_tokens=20),
            SamplingParams(temperature=0.8, max_tokens=40),
        ]

        print(f"\n處理 {len(prompts)} 個不同長度的提示詞...")
        print("-" * 80)

        # 注意: vLLM 的 generate 方法只接受單一 SamplingParams
        # 如需不同參數，需要分別調用或使用統一參數
        sampling_params = SamplingParams(temperature=0.8, max_tokens=50)

        start_time = time.time()
        outputs = llm.generate(prompts, sampling_params)
        elapsed_time = time.time() - start_time

        # 打印結果
        for i, output in enumerate(outputs):
            prompt_len = len(output.prompt.split())
            generated_len = len(output.outputs[0].token_ids)
            print(f"\n[{i+1}] 輸入長度: {prompt_len} 詞")
            print(f"    提示: {output.prompt[:50]}...")
            print(f"    生成長度: {generated_len} tokens")
            print(f"    生成: {output.outputs[0].text[:80]}...")

        print("\n" + "=" * 80)
        print(f"總耗時: {elapsed_time:.2f} 秒")
        print("vLLM 的 PagedAttention 能高效處理不同長度的序列")

    except Exception as e:
        print(f"✗ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


def batch_inference_with_multiple_outputs():
    """
    每個輸入生成多個輸出

    展示如何為每個提示詞生成多個不同的候選結果
    """
    print("\n" + "=" * 80)
    print("示例 4: 批量推理 - 多輸出模式")
    print("=" * 80)

    try:
        llm = LLM(model="facebook/opt-125m", trust_remote_code=True)

        prompts = [
            "The best way to learn programming is",
            "In the future, robots will",
        ]

        # 設置 n=3，為每個提示詞生成 3 個不同的輸出
        sampling_params = SamplingParams(
            temperature=0.9,  # 較高溫度產生更多樣化的輸出
            max_tokens=40,
            n=3,  # 每個提示詞生成 3 個輸出
        )

        print(f"\n為 {len(prompts)} 個提示詞各生成 {sampling_params.n} 個輸出...")

        outputs = llm.generate(prompts, sampling_params)

        # 打印結果
        for i, output in enumerate(outputs):
            print(f"\n{'=' * 80}")
            print(f"提示詞 {i+1}: {output.prompt}")
            print(f"{'=' * 80}")

            for j, completion in enumerate(output.outputs):
                print(f"\n候選 {j+1}:")
                print(f"  {completion.text}")
                print(f"  [累積對數概率: {completion.cumulative_logprob:.4f}]")

    except Exception as e:
        print(f"✗ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


def batch_inference_application_examples():
    """
    批量推理實際應用場景

    展示批量推理在實際場景中的應用
    """
    print("\n" + "=" * 80)
    print("示例 5: 批量推理實際應用")
    print("=" * 80)

    try:
        llm = LLM(model="facebook/opt-125m", trust_remote_code=True)

        # 場景 1: 批量摘要生成
        print("\n[應用場景 1] 批量文本摘要")
        print("-" * 80)

        documents = [
            "Climate change is one of the biggest challenges. ",
            "Artificial intelligence is transforming industries. ",
            "Renewable energy sources are becoming more popular. ",
        ]

        summary_prompts = [
            f"Summarize this text: {doc}" for doc in documents
        ]

        sampling_params = SamplingParams(temperature=0.3, max_tokens=30)
        outputs = llm.generate(summary_prompts, sampling_params)

        for i, output in enumerate(outputs):
            print(f"\n文檔 {i+1}: {documents[i][:50]}...")
            print(f"摘要: {output.outputs[0].text[:80]}...")

        # 場景 2: 批量分類
        print("\n\n[應用場景 2] 批量文本分類")
        print("-" * 80)

        texts = [
            "This product is amazing! I love it.",
            "Terrible experience, would not recommend.",
            "It's okay, nothing special.",
        ]

        classification_prompts = [
            f"Classify the sentiment of this text as positive, negative, or neutral: '{text}' Sentiment:"
            for text in texts
        ]

        sampling_params = SamplingParams(temperature=0.1, max_tokens=5)
        outputs = llm.generate(classification_prompts, sampling_params)

        for i, output in enumerate(outputs):
            print(f"\n文本 {i+1}: {texts[i]}")
            print(f"情感: {output.outputs[0].text.strip()}")

        # 場景 3: 批量問答
        print("\n\n[應用場景 3] 批量問答")
        print("-" * 80)

        questions = [
            "What is Python?",
            "What is machine learning?",
            "What is cloud computing?",
        ]

        qa_prompts = [f"Q: {q}\nA:" for q in questions]

        sampling_params = SamplingParams(temperature=0.5, max_tokens=50)
        outputs = llm.generate(qa_prompts, sampling_params)

        for i, output in enumerate(outputs):
            print(f"\n問題 {i+1}: {questions[i]}")
            print(f"回答: {output.outputs[0].text[:100]}...")

    except Exception as e:
        print(f"✗ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


def compare_batch_vs_sequential():
    """
    批量推理 vs 順序推理性能對比

    展示批量推理的性能優勢
    """
    print("\n" + "=" * 80)
    print("示例 6: 批量 vs 順序推理性能對比")
    print("=" * 80)

    try:
        llm = LLM(model="facebook/opt-125m", trust_remote_code=True)

        prompts = [
            f"Write a short story about {topic}"
            for topic in ["space", "ocean", "forest", "desert", "city"]
        ]

        sampling_params = SamplingParams(temperature=0.8, max_tokens=40)

        # 批量推理
        print("\n[1] 批量推理模式...")
        batch_start = time.time()
        batch_outputs = llm.generate(prompts, sampling_params)
        batch_time = time.time() - batch_start

        # 順序推理（模擬）
        print("\n[2] 順序推理模式...")
        sequential_start = time.time()
        sequential_outputs = []
        for prompt in prompts:
            output = llm.generate([prompt], sampling_params)
            sequential_outputs.extend(output)
        sequential_time = time.time() - sequential_start

        # 性能對比
        print("\n" + "=" * 80)
        print("性能對比結果：")
        print("-" * 80)
        print(f"批量推理耗時:   {batch_time:.2f} 秒")
        print(f"順序推理耗時:   {sequential_time:.2f} 秒")
        print(f"速度提升:       {sequential_time/batch_time:.2f}x")
        print(f"批量吞吐量:     {len(prompts)/batch_time:.2f} 請求/秒")
        print(f"順序吞吐量:     {len(prompts)/sequential_time:.2f} 請求/秒")

        print("\n結論: 批量推理能顯著提高吞吐量，特別是處理大量請求時")

    except Exception as e:
        print(f"✗ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


def batch_inference_best_practices():
    """
    批量推理最佳實踐

    分享批量推理的優化技巧和注意事項
    """
    print("\n" + "=" * 80)
    print("批量推理最佳實踐")
    print("=" * 80)

    print("""
1. 批量大小選擇
   ✓ 根據 GPU 內存選擇合適的批量大小
   ✓ 監控 GPU 利用率，保持在 80-95% 最佳
   ✓ 過大的批量可能導致 OOM，過小則利用率低

2. 動態批處理
   ✓ vLLM 自動進行動態批處理（Continuous Batching）
   ✓ 不同長度的請求可以高效混合處理
   ✓ 無需手動管理批次

3. 內存優化
   ✓ 設置 max_model_len 限制最大序列長度
   ✓ 使用 gpu_memory_utilization 控制內存使用
   ✓ 考慮使用量化模型減少內存佔用

4. 性能調優
   ✓ 使用較大的 max_num_batched_tokens 提高吞吐量
   ✓ 設置 max_num_seqs 控制並發請求數
   ✓ 啟用 tensor parallelism 使用多 GPU

5. 實際應用建議
   ✓ 離線批處理: 優先考慮吞吐量
   ✓ 在線服務: 需平衡延遲和吞吐量
   ✓ 使用連接池管理長期運行的模型實例

6. 錯誤處理
   ✓ 處理單個請求失敗不影響整批
   ✓ 實現超時機制避免長時間等待
   ✓ 記錄失敗請求以便重試
    """)

    # 示例：配置優化的批量推理
    print("\n推薦配置示例：")
    print("-" * 80)
    print("""
# 高吞吐量配置（離線批處理）
llm = LLM(
    model="meta-llama/Llama-2-7b-hf",
    tensor_parallel_size=1,
    gpu_memory_utilization=0.95,
    max_num_batched_tokens=8192,
    max_num_seqs=256,
)

# 低延遲配置（在線服務）
llm = LLM(
    model="meta-llama/Llama-2-7b-hf",
    tensor_parallel_size=2,
    gpu_memory_utilization=0.85,
    max_num_batched_tokens=4096,
    max_num_seqs=128,
)
    """)


def main():
    """
    主函數：運行所有示例
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 25 + "vLLM 批量推理示例" + " " * 25 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    try:
        # 示例 1: 簡單批量推理
        simple_batch_inference()

        # 示例 2: 大規模批量推理
        large_scale_batch_inference()

        # 示例 3: 不同長度批量推理
        batch_with_different_lengths()

        # 示例 4: 多輸出批量推理
        batch_inference_with_multiple_outputs()

        # 示例 5: 實際應用場景
        batch_inference_application_examples()

        # 示例 6: 性能對比
        compare_batch_vs_sequential()

        # 最佳實踐
        batch_inference_best_practices()

        print("\n" + "=" * 80)
        print("✓ 所有示例運行完成！")
        print("=" * 80)

    except KeyboardInterrupt:
        print("\n\n程序被用戶中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ 運行出錯: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
