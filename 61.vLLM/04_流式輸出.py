#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
vLLM 流式輸出示例
=================

本示例展示 vLLM 的流式生成功能，包括：
1. 基本流式生成
2. 多個提示詞的流式處理
3. 流式輸出的實時顯示
4. 異步流式處理
5. 流式 API 服務

流式輸出允許在生成過程中逐步返回結果，
提供更好的用戶體驗，特別適合聊天應用。

適用場景：
- 聊天機器人
- 實時文本生成
- 交互式應用
- 漸進式內容展示
"""

import sys
import time
import asyncio
from typing import AsyncIterator, List
from vllm import LLM, SamplingParams
from vllm.outputs import RequestOutput


def basic_streaming():
    """
    基礎流式生成

    展示最簡單的流式輸出用法
    """
    print("=" * 80)
    print("示例 1: 基礎流式生成")
    print("=" * 80)

    try:
        # 初始化模型
        print("\n正在加載模型...")
        llm = LLM(model="facebook/opt-125m", trust_remote_code=True)
        print("✓ 模型加載成功！\n")

        # 設置採樣參數
        sampling_params = SamplingParams(
            temperature=0.8,
            top_p=0.95,
            max_tokens=100,
        )

        # 提示詞
        prompt = "Once upon a time, in a land far away,"

        print(f"提示詞: {prompt}")
        print("\n流式生成中...")
        print("-" * 80)
        print(prompt, end="", flush=True)

        # 使用 stream=True 啟用流式生成
        # 注意：vLLM 的 Python API 不直接支持 streaming
        # 需要使用 AsyncLLMEngine 或 API server
        # 這裡我們模擬流式效果

        outputs = llm.generate([prompt], sampling_params)
        generated_text = outputs[0].outputs[0].text

        # 模擬流式輸出效果
        for char in generated_text:
            print(char, end="", flush=True)
            time.sleep(0.02)  # 模擬流式延遲

        print("\n" + "-" * 80)
        print("\n✓ 流式生成完成！")

    except Exception as e:
        print(f"\n✗ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


def streaming_with_progress():
    """
    帶進度顯示的流式生成

    展示如何在流式生成時顯示進度信息
    """
    print("\n" + "=" * 80)
    print("示例 2: 帶進度的流式生成")
    print("=" * 80)

    try:
        llm = LLM(model="facebook/opt-125m", trust_remote_code=True)

        sampling_params = SamplingParams(
            temperature=0.7,
            max_tokens=80,
        )

        prompt = "The future of artificial intelligence is"

        print(f"\n提示詞: {prompt}")
        print(f"最大生成長度: {sampling_params.max_tokens} tokens\n")

        print("生成進度:")
        print("-" * 80)

        # 生成文本
        outputs = llm.generate([prompt], sampling_params)
        generated_text = outputs[0].outputs[0].text
        generated_tokens = outputs[0].outputs[0].token_ids

        # 模擬流式輸出，顯示進度
        total_tokens = len(generated_tokens)
        print(prompt, end="", flush=True)

        for i, char in enumerate(generated_text):
            print(char, end="", flush=True)
            time.sleep(0.03)

            # 每 20 個字符顯示一次進度
            if (i + 1) % 20 == 0:
                progress = (i + 1) / len(generated_text) * 100
                print(f" [{progress:.0f}%]", end="", flush=True)

        print(f"\n{'-' * 80}")
        print(f"\n✓ 完成！生成了 {total_tokens} 個 tokens")

    except Exception as e:
        print(f"\n✗ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


def multi_prompt_streaming():
    """
    多提示詞流式生成

    同時處理多個提示詞的流式生成
    """
    print("\n" + "=" * 80)
    print("示例 3: 多提示詞流式生成")
    print("=" * 80)

    try:
        llm = LLM(model="facebook/opt-125m", trust_remote_code=True)

        prompts = [
            "The most important invention in history is",
            "In the next 10 years, technology will",
            "The key to happiness is",
        ]

        sampling_params = SamplingParams(
            temperature=0.8,
            max_tokens=50,
        )

        print(f"\n批量處理 {len(prompts)} 個提示詞...\n")

        # 生成所有輸出
        outputs = llm.generate(prompts, sampling_params)

        # 逐個顯示流式效果
        for i, output in enumerate(outputs):
            print("=" * 80)
            print(f"提示詞 {i+1}/{len(prompts)}")
            print("=" * 80)
            print(f"\n{output.prompt}", end="", flush=True)

            # 模擬流式顯示
            for char in output.outputs[0].text:
                print(char, end="", flush=True)
                time.sleep(0.02)

            print("\n")

        print("=" * 80)
        print("✓ 所有提示詞處理完成！")

    except Exception as e:
        print(f"\n✗ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


def streaming_with_stop_conditions():
    """
    帶停止條件的流式生成

    展示如何使用停止詞控制流式生成
    """
    print("\n" + "=" * 80)
    print("示例 4: 帶停止條件的流式生成")
    print("=" * 80)

    try:
        llm = LLM(model="facebook/opt-125m", trust_remote_code=True)

        # 使用停止詞
        sampling_params = SamplingParams(
            temperature=0.7,
            max_tokens=100,
            stop=["\n\n", ".", "!"],  # 遇到這些符號就停止
        )

        prompts = [
            "The capital of France is",
            "Python is a programming language that",
            "Machine learning is",
        ]

        print("\n使用停止條件: ['\\n\\n', '.', '!']")
        print("生成會在遇到這些符號時自動停止\n")

        outputs = llm.generate(prompts, sampling_params)

        for i, output in enumerate(outputs):
            print(f"\n{'-' * 80}")
            print(f"[{i+1}] 提示詞: {output.prompt}")
            print(f"{'-' * 80}")
            print("生成: ", end="", flush=True)

            # 模擬流式輸出
            for char in output.outputs[0].text:
                print(char, end="", flush=True)
                time.sleep(0.03)

            # 顯示停止原因
            finish_reason = "達到停止條件" if len(output.outputs[0].text) < 100 else "達到最大長度"
            print(f"\n[{finish_reason}]")

    except Exception as e:
        print(f"\n✗ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


def chat_style_streaming():
    """
    聊天風格流式生成

    模擬聊天機器人的流式響應
    """
    print("\n" + "=" * 80)
    print("示例 5: 聊天風格流式生成")
    print("=" * 80)

    try:
        llm = LLM(model="facebook/opt-125m", trust_remote_code=True)

        # 模擬多輪對話
        conversations = [
            {
                "user": "What is Python?",
                "context": "User: What is Python?\nAssistant:"
            },
            {
                "user": "How do I learn it?",
                "context": "User: How do I learn it?\nAssistant:"
            },
            {
                "user": "What are some good resources?",
                "context": "User: What are some good resources?\nAssistant:"
            },
        ]

        sampling_params = SamplingParams(
            temperature=0.7,
            max_tokens=60,
            stop=["User:", "\n\n"],
        )

        print("\n模擬聊天對話：")
        print("=" * 80)

        for i, conv in enumerate(conversations):
            print(f"\n{'🧑 User:':<15} {conv['user']}")
            print(f"{'🤖 Assistant:':<15}", end="", flush=True)

            # 生成回復
            outputs = llm.generate([conv['context']], sampling_params)
            response = outputs[0].outputs[0].text

            # 流式顯示回復
            for char in response:
                print(char, end="", flush=True)
                time.sleep(0.03)

            print()  # 換行

        print("\n" + "=" * 80)
        print("✓ 對話結束")

    except Exception as e:
        print(f"\n✗ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


async def async_streaming_example():
    """
    異步流式生成示例

    展示如何使用異步方式進行流式生成
    注意：這是一個概念性示例，實際的異步流式生成
    需要使用 AsyncLLMEngine
    """
    print("\n" + "=" * 80)
    print("示例 6: 異步流式生成（概念示例）")
    print("=" * 80)

    print("""
異步流式生成說明：

vLLM 提供了 AsyncLLMEngine 用於異步流式生成，適合高並發場景。

基本用法：

```python
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.sampling_params import SamplingParams
from vllm.utils import random_uuid

# 初始化異步引擎
engine = AsyncLLMEngine.from_engine_args(engine_args)

# 添加請求
request_id = random_uuid()
await engine.add_request(request_id, prompt, sampling_params)

# 流式獲取結果
async for request_output in engine.generate():
    if request_output.request_id == request_id:
        if request_output.finished:
            print(request_output.outputs[0].text)
            break
        else:
            # 流式輸出中間結果
            print(request_output.outputs[0].text, end='', flush=True)
```

優勢：
1. 高並發處理能力
2. 真正的異步流式輸出
3. 更好的資源利用率
4. 適合 API 服務

推薦使用 vLLM 的 OpenAI 兼容 API 服務器，
它內建了異步流式支持。
    """)


def streaming_performance_comparison():
    """
    流式 vs 非流式性能對比

    比較流式和非流式模式的區別
    """
    print("\n" + "=" * 80)
    print("示例 7: 流式 vs 非流式對比")
    print("=" * 80)

    try:
        llm = LLM(model="facebook/opt-125m", trust_remote_code=True)

        prompt = "The history of computers begins with"
        sampling_params = SamplingParams(temperature=0.7, max_tokens=80)

        print("\n[1] 非流式模式（一次性返回）")
        print("-" * 80)

        start_time = time.time()
        outputs = llm.generate([prompt], sampling_params)
        generation_time = time.time() - start_time
        generated_text = outputs[0].outputs[0].text

        print(f"提示詞: {prompt}")
        print(f"\n等待 {generation_time:.2f} 秒後收到完整結果：")
        print(generated_text)

        print("\n[2] 流式模式（逐步返回）")
        print("-" * 80)

        print(f"提示詞: {prompt}")
        print("\n立即開始接收結果：")
        print(prompt, end="", flush=True)

        # 模擬流式輸出
        first_token_time = 0.1  # 模擬首 token 延遲
        time.sleep(first_token_time)

        for char in generated_text:
            print(char, end="", flush=True)
            time.sleep(0.02)

        print("\n\n" + "=" * 80)
        print("對比總結：")
        print("-" * 80)
        print(f"非流式模式:")
        print(f"  - 首次響應時間: {generation_time:.2f} 秒（完整生成）")
        print(f"  - 用戶體驗: 需要等待全部完成")
        print(f"\n流式模式:")
        print(f"  - 首次響應時間: {first_token_time:.2f} 秒（首 token）")
        print(f"  - 用戶體驗: 立即看到輸出，體驗更好")
        print(f"\n✓ 流式模式特別適合長文本生成和交互式應用")

    except Exception as e:
        print(f"\n✗ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


def streaming_best_practices():
    """
    流式生成最佳實踐

    分享流式生成的使用技巧
    """
    print("\n" + "=" * 80)
    print("流式生成最佳實踐")
    print("=" * 80)

    print("""
1. 何時使用流式生成
   ✓ 聊天應用 - 提供即時反饋
   ✓ 長文本生成 - 改善用戶體驗
   ✓ 交互式應用 - 減少感知延遲
   ✗ 批量處理 - 非流式更高效
   ✗ 短文本生成 - 差異不明顯

2. 實現建議
   ✓ 使用 vLLM OpenAI API 服務器（內建流式支持）
   ✓ 使用 AsyncLLMEngine 進行異步流式生成
   ✓ 在前端使用 Server-Sent Events (SSE)
   ✓ 實現超時和錯誤處理

3. 用戶體驗優化
   ✓ 顯示打字機效果
   ✓ 提供停止生成按鈕
   ✓ 顯示生成進度指示器
   ✓ 處理網絡中斷

4. 性能考慮
   ✓ 流式不影響總體生成時間
   ✓ 首 token 延遲是關鍵指標
   ✓ 批量請求可能不適合流式
   ✓ 監控連接數和內存使用

5. API 服務器流式示例

   啟動服務器：
   ```bash
   python -m vllm.entrypoints.openai.api_server \\
       --model facebook/opt-125m \\
       --port 8000
   ```

   客戶端調用：
   ```python
   from openai import OpenAI

   client = OpenAI(
       base_url="http://localhost:8000/v1",
       api_key="dummy"
   )

   stream = client.chat.completions.create(
       model="facebook/opt-125m",
       messages=[{"role": "user", "content": "Hello!"}],
       stream=True  # 啟用流式
   )

   for chunk in stream:
       if chunk.choices[0].delta.content:
           print(chunk.choices[0].delta.content, end='', flush=True)
   ```

6. 錯誤處理
   ✓ 處理連接中斷
   ✓ 實現重試機制
   ✓ 超時保護
   ✓ 優雅降級到非流式

7. 監控指標
   ✓ 首 token 延遲 (TTFT - Time To First Token)
   ✓ 每 token 延遲 (TPOT - Time Per Output Token)
   ✓ 總生成時間
   ✓ 流式連接數
    """)


def main():
    """
    主函數：運行所有示例
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 25 + "vLLM 流式輸出示例" + " " * 25 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    try:
        # 示例 1: 基礎流式生成
        basic_streaming()

        # 示例 2: 帶進度的流式生成
        streaming_with_progress()

        # 示例 3: 多提示詞流式
        multi_prompt_streaming()

        # 示例 4: 停止條件
        streaming_with_stop_conditions()

        # 示例 5: 聊天風格
        chat_style_streaming()

        # 示例 6: 異步流式（概念）
        asyncio.run(async_streaming_example())

        # 示例 7: 性能對比
        streaming_performance_comparison()

        # 最佳實踐
        streaming_best_practices()

        print("\n" + "=" * 80)
        print("✓ 所有示例運行完成！")
        print("=" * 80)

        print("\n提示：")
        print("  - 本示例使用模擬流式效果演示概念")
        print("  - 生產環境推薦使用 vLLM OpenAI API 服務器")
        print("  - API 服務器提供真正的 SSE 流式支持")
        print("  - 參考 05_OpenAI兼容.py 了解 API 使用方法")

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
