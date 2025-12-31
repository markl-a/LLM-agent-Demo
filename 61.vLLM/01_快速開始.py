#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
vLLM 快速開始示例
=================

本示例展示 vLLM 的基本使用方法，包括：
1. 初始化 LLM 模型
2. 配置採樣參數
3. 單個和多個提示詞的推理
4. 查看生成結果

適用場景：
- 首次使用 vLLM
- 快速驗證環境配置
- 理解基本工作流程
"""

import sys
from typing import List
from vllm import LLM, SamplingParams


def basic_generation():
    """
    基礎生成示例

    使用小型 OPT 模型進行快速測試，展示最簡單的使用方式
    """
    print("=" * 80)
    print("示例 1: 基礎文本生成")
    print("=" * 80)

    try:
        # 初始化模型（使用較小的模型進行快速測試）
        # facebook/opt-125m 是一個輕量級模型，適合快速測試
        print("\n正在加載模型 facebook/opt-125m...")
        llm = LLM(
            model="facebook/opt-125m",
            trust_remote_code=True,  # 信任遠程代碼
        )
        print("✓ 模型加載成功！")

        # 設置採樣參數
        sampling_params = SamplingParams(
            temperature=0.8,      # 溫度：控制隨機性，越高越隨機
            top_p=0.95,          # nucleus sampling：只考慮概率質量前 95% 的詞
            max_tokens=100,      # 最大生成 token 數
        )

        # 單個提示詞生成
        prompt = "Hello, my name is"
        print(f"\n提示詞: {prompt}")

        outputs = llm.generate([prompt], sampling_params)

        # 打印結果
        for output in outputs:
            generated_text = output.outputs[0].text
            print(f"生成結果: {generated_text}")
            print(f"生成 token 數: {len(output.outputs[0].token_ids)}")

    except Exception as e:
        print(f"✗ 錯誤: {str(e)}")
        sys.exit(1)


def multi_prompt_generation():
    """
    多提示詞批量生成

    展示 vLLM 的批處理能力，可以同時處理多個提示詞
    """
    print("\n" + "=" * 80)
    print("示例 2: 批量文本生成")
    print("=" * 80)

    try:
        # 初始化模型
        print("\n正在加載模型...")
        llm = LLM(model="facebook/opt-125m")

        # 採樣參數：使用較低的溫度獲得更確定性的輸出
        sampling_params = SamplingParams(
            temperature=0.3,
            top_p=0.9,
            max_tokens=50,
        )

        # 多個提示詞
        prompts = [
            "The future of AI is",
            "In the year 2050, technology will",
            "The most important skill for programmers is",
            "Machine learning helps us to",
        ]

        print(f"\n批量處理 {len(prompts)} 個提示詞...")

        # 批量生成（vLLM 會自動優化批處理）
        outputs = llm.generate(prompts, sampling_params)

        # 打印所有結果
        print("\n生成結果：")
        print("-" * 80)
        for i, output in enumerate(outputs):
            prompt = output.prompt
            generated_text = output.outputs[0].text
            print(f"\n[{i+1}] 提示詞: {prompt}")
            print(f"    生成: {generated_text}")

    except Exception as e:
        print(f"✗ 錯誤: {str(e)}")
        sys.exit(1)


def advanced_sampling_params():
    """
    高級採樣參數配置

    展示不同採樣參數對生成結果的影響
    """
    print("\n" + "=" * 80)
    print("示例 3: 高級採樣參數")
    print("=" * 80)

    try:
        llm = LLM(model="facebook/opt-125m")

        prompt = "Artificial intelligence is"

        # 測試不同的溫度設置
        temperatures = [0.1, 0.5, 1.0]

        print(f"\n提示詞: {prompt}")
        print("\n比較不同溫度參數的效果：")
        print("-" * 80)

        for temp in temperatures:
            sampling_params = SamplingParams(
                temperature=temp,
                max_tokens=30,
                top_p=0.95,
            )

            outputs = llm.generate([prompt], sampling_params)
            generated_text = outputs[0].outputs[0].text

            print(f"\n溫度 = {temp}:")
            print(f"  {generated_text}")

        # 測試 top_k 和 top_p
        print("\n" + "-" * 80)
        print("測試 top_k 和 top_p 參數：")

        configs = [
            {"top_k": 10, "top_p": 1.0, "name": "top_k=10"},
            {"top_k": -1, "top_p": 0.9, "name": "top_p=0.9"},
            {"top_k": 50, "top_p": 0.95, "name": "top_k=50, top_p=0.95"},
        ]

        for config in configs:
            sampling_params = SamplingParams(
                temperature=0.8,
                top_k=config["top_k"],
                top_p=config["top_p"],
                max_tokens=30,
            )

            outputs = llm.generate([prompt], sampling_params)
            generated_text = outputs[0].outputs[0].text

            print(f"\n{config['name']}:")
            print(f"  {generated_text}")

    except Exception as e:
        print(f"✗ 錯誤: {str(e)}")
        sys.exit(1)


def inspect_output_details():
    """
    檢查輸出詳細信息

    展示如何訪問生成結果的各種元數據
    """
    print("\n" + "=" * 80)
    print("示例 4: 檢查輸出詳細信息")
    print("=" * 80)

    try:
        llm = LLM(model="facebook/opt-125m")

        sampling_params = SamplingParams(
            temperature=0.8,
            max_tokens=50,
            n=2,  # 為每個提示詞生成 2 個不同的輸出
        )

        prompt = "The key to success is"

        print(f"\n提示詞: {prompt}")
        print(f"生成數量: {sampling_params.n}")

        outputs = llm.generate([prompt], sampling_params)

        # 檢查詳細信息
        for output in outputs:
            print(f"\n提示詞: {output.prompt}")
            print(f"輸出數量: {len(output.outputs)}")

            for i, completion in enumerate(output.outputs):
                print(f"\n--- 輸出 {i+1} ---")
                print(f"文本: {completion.text}")
                print(f"Token IDs 數量: {len(completion.token_ids)}")
                print(f"累積對數概率: {completion.cumulative_logprob:.4f}")

                # 如果有 finish_reason
                if hasattr(completion, 'finish_reason'):
                    print(f"結束原因: {completion.finish_reason}")

    except Exception as e:
        print(f"✗ 錯誤: {str(e)}")
        sys.exit(1)


def chat_style_generation():
    """
    聊天風格生成

    模擬對話場景的文本生成
    """
    print("\n" + "=" * 80)
    print("示例 5: 聊天風格生成")
    print("=" * 80)

    try:
        llm = LLM(model="facebook/opt-125m")

        sampling_params = SamplingParams(
            temperature=0.7,
            max_tokens=60,
            stop=["User:", "\n\n"],  # 遇到這些詞就停止生成
        )

        # 模擬對話提示詞
        conversation = """User: What is Python?
Assistant: Python is a high-level programming language that is widely used for
User: What are its main features?
Assistant:"""

        print("對話上下文：")
        print("-" * 80)
        print(conversation)
        print("-" * 80)

        outputs = llm.generate([conversation], sampling_params)

        print("\n生成的回覆：")
        for output in outputs:
            generated_text = output.outputs[0].text
            print(generated_text)

    except Exception as e:
        print(f"✗ 錯誤: {str(e)}")
        sys.exit(1)


def main():
    """
    主函數：運行所有示例
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "vLLM 快速開始示例" + " " * 20 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    # 檢查系統信息
    try:
        import torch
        print(f"PyTorch 版本: {torch.__version__}")
        print(f"CUDA 可用: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA 版本: {torch.version.cuda}")
            print(f"GPU 數量: {torch.cuda.device_count()}")
            print(f"當前 GPU: {torch.cuda.get_device_name(0)}")
    except Exception as e:
        print(f"無法獲取系統信息: {e}")

    print("\n")

    # 運行所有示例
    try:
        # 示例 1: 基礎生成
        basic_generation()

        # 示例 2: 批量生成
        multi_prompt_generation()

        # 示例 3: 高級採樣參數
        advanced_sampling_params()

        # 示例 4: 檢查輸出詳情
        inspect_output_details()

        # 示例 5: 聊天風格
        chat_style_generation()

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
