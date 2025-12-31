#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
vLLM OpenAI 兼容 API 示例
========================

本示例展示如何使用 vLLM 的 OpenAI 兼容 API，包括：
1. 啟動 OpenAI 兼容 API 服務器
2. 使用 OpenAI Python 客戶端調用
3. Chat Completions API
4. Completions API
5. 流式響應
6. 模型管理和配置

vLLM 提供完全兼容 OpenAI 的 API 接口，
可以無縫替換 OpenAI API，降低遷移成本。

適用場景：
- 從 OpenAI 遷移到自部署
- 構建兼容 OpenAI 的服務
- 集成現有 OpenAI 應用
- 本地 LLM 服務
"""

import sys
import subprocess
import time
import requests
from typing import List, Dict
from openai import OpenAI


def server_startup_guide():
    """
    服務器啟動指南

    展示如何啟動 vLLM OpenAI API 服務器
    """
    print("=" * 80)
    print("示例 1: 啟動 OpenAI 兼容 API 服務器")
    print("=" * 80)

    print("""
啟動命令：
----------

1. 基礎啟動：
   ```bash
   python -m vllm.entrypoints.openai.api_server \\
       --model facebook/opt-125m \\
       --port 8000
   ```

2. 完整配置：
   ```bash
   python -m vllm.entrypoints.openai.api_server \\
       --model meta-llama/Llama-2-7b-chat-hf \\
       --port 8000 \\
       --host 0.0.0.0 \\
       --tensor-parallel-size 1 \\
       --gpu-memory-utilization 0.9 \\
       --max-model-len 4096 \\
       --served-model-name llama-2-7b \\
       --chat-template ./chat_template.jinja \\
       --trust-remote-code
   ```

3. 使用環境變量：
   ```bash
   export VLLM_HOST=0.0.0.0
   export VLLM_PORT=8000
   python -m vllm.entrypoints.openai.api_server \\
       --model facebook/opt-125m
   ```

4. Docker 方式：
   ```bash
   docker run --runtime nvidia --gpus all \\
       -v ~/.cache/huggingface:/root/.cache/huggingface \\
       -p 8000:8000 \\
       --env "HUGGING_FACE_HUB_TOKEN=<token>" \\
       vllm/vllm-openai:latest \\
       --model meta-llama/Llama-2-7b-chat-hf
   ```

常用參數：
----------
--model              模型名稱或路徑
--port               服務端口（默認 8000）
--host               綁定地址（默認 localhost）
--tensor-parallel-size   張量並行 GPU 數
--dtype              數據類型（auto/float16/bfloat16）
--max-model-len      最大序列長度
--served-model-name  API 中顯示的模型名稱
--api-key            API 密鑰（可選）
--ssl-keyfile        SSL 密鑰文件
--ssl-certfile       SSL 證書文件

啟動後訪問：
-----------
- API 文檔: http://localhost:8000/docs
- OpenAPI 規範: http://localhost:8000/openapi.json
- 健康檢查: http://localhost:8000/health
    """)


def check_server_health():
    """
    檢查服務器健康狀態

    驗證 API 服務器是否正常運行
    """
    print("\n" + "=" * 80)
    print("示例 2: 檢查服務器健康狀態")
    print("=" * 80)

    server_url = "http://localhost:8000"

    print(f"\n檢查服務器: {server_url}")

    try:
        # 健康檢查
        health_url = f"{server_url}/health"
        print(f"\n[1] 健康檢查: {health_url}")

        response = requests.get(health_url, timeout=5)

        if response.status_code == 200:
            print("✓ 服務器健康狀態良好")
        else:
            print(f"⚠ 服務器返回狀態碼: {response.status_code}")

        # 獲取模型列表
        models_url = f"{server_url}/v1/models"
        print(f"\n[2] 獲取模型列表: {models_url}")

        response = requests.get(models_url, timeout=5)

        if response.status_code == 200:
            models = response.json()
            print("✓ 可用模型:")
            for model in models.get('data', []):
                print(f"   - {model['id']}")
        else:
            print(f"⚠ 無法獲取模型列表")

    except requests.exceptions.ConnectionError:
        print("✗ 無法連接到服務器")
        print("\n請先啟動 vLLM API 服務器:")
        print("  python -m vllm.entrypoints.openai.api_server --model facebook/opt-125m")
    except Exception as e:
        print(f"✗ 錯誤: {str(e)}")


def chat_completions_example():
    """
    Chat Completions API 示例

    使用 OpenAI Chat Completions 格式
    """
    print("\n" + "=" * 80)
    print("示例 3: Chat Completions API")
    print("=" * 80)

    try:
        # 初始化 OpenAI 客戶端，指向本地 vLLM 服務器
        client = OpenAI(
            base_url="http://localhost:8000/v1",
            api_key="dummy"  # vLLM 默認不需要 API key
        )

        print("\n[1] 單輪對話")
        print("-" * 80)

        # 單輪對話
        response = client.chat.completions.create(
            model="facebook/opt-125m",  # 使用服務器加載的模型
            messages=[
                {"role": "user", "content": "Hello! How are you?"}
            ],
            temperature=0.7,
            max_tokens=50,
        )

        print(f"用戶: Hello! How are you?")
        print(f"助手: {response.choices[0].message.content}")

        # 多輪對話
        print("\n[2] 多輪對話")
        print("-" * 80)

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is Python?"},
        ]

        response = client.chat.completions.create(
            model="facebook/opt-125m",
            messages=messages,
            temperature=0.7,
            max_tokens=80,
        )

        print("系統: You are a helpful assistant.")
        print(f"用戶: What is Python?")
        print(f"助手: {response.choices[0].message.content}")

        # 添加助手回復到對話歷史
        messages.append({
            "role": "assistant",
            "content": response.choices[0].message.content
        })

        # 繼續對話
        messages.append({
            "role": "user",
            "content": "Can you give me an example?"
        })

        response = client.chat.completions.create(
            model="facebook/opt-125m",
            messages=messages,
            temperature=0.7,
            max_tokens=80,
        )

        print(f"用戶: Can you give me an example?")
        print(f"助手: {response.choices[0].message.content}")

        # 響應元數據
        print("\n[3] 響應元數據")
        print("-" * 80)
        print(f"模型: {response.model}")
        print(f"完成原因: {response.choices[0].finish_reason}")
        print(f"使用 tokens: {response.usage.total_tokens}")
        print(f"  - 提示詞: {response.usage.prompt_tokens}")
        print(f"  - 生成: {response.usage.completion_tokens}")

    except Exception as e:
        print(f"✗ 錯誤: {str(e)}")
        print("\n請確保 vLLM API 服務器正在運行")
        import traceback
        traceback.print_exc()


def completions_example():
    """
    Completions API 示例

    使用傳統的 Completions 格式
    """
    print("\n" + "=" * 80)
    print("示例 4: Completions API")
    print("=" * 80)

    try:
        client = OpenAI(
            base_url="http://localhost:8000/v1",
            api_key="dummy"
        )

        print("\n[1] 基礎文本補全")
        print("-" * 80)

        # 文本補全
        response = client.completions.create(
            model="facebook/opt-125m",
            prompt="The future of AI is",
            max_tokens=50,
            temperature=0.8,
        )

        print(f"提示詞: The future of AI is")
        print(f"補全: {response.choices[0].text}")

        # 多個提示詞
        print("\n[2] 批量文本補全")
        print("-" * 80)

        prompts = [
            "Python is a",
            "Machine learning helps",
            "The most important skill is",
        ]

        response = client.completions.create(
            model="facebook/opt-125m",
            prompt=prompts,
            max_tokens=30,
            temperature=0.7,
        )

        for i, choice in enumerate(response.choices):
            print(f"\n提示詞 {i+1}: {prompts[choice.index]}")
            print(f"補全: {choice.text}")

        # 生成多個候選
        print("\n[3] 生成多個候選結果")
        print("-" * 80)

        response = client.completions.create(
            model="facebook/opt-125m",
            prompt="Once upon a time",
            max_tokens=40,
            temperature=0.9,
            n=3,  # 生成 3 個候選
        )

        for i, choice in enumerate(response.choices):
            print(f"\n候選 {i+1}:")
            print(choice.text)

    except Exception as e:
        print(f"✗ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


def streaming_example():
    """
    流式響應示例

    展示如何使用流式 API
    """
    print("\n" + "=" * 80)
    print("示例 5: 流式響應")
    print("=" * 80)

    try:
        client = OpenAI(
            base_url="http://localhost:8000/v1",
            api_key="dummy"
        )

        print("\n[1] Chat Completions 流式響應")
        print("-" * 80)

        print("用戶: Tell me a short story about a robot.")
        print("助手: ", end="", flush=True)

        # 流式聊天
        stream = client.chat.completions.create(
            model="facebook/opt-125m",
            messages=[
                {"role": "user", "content": "Tell me a short story about a robot."}
            ],
            max_tokens=100,
            temperature=0.8,
            stream=True,  # 啟用流式
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="", flush=True)

        print("\n")

        print("\n[2] Completions 流式響應")
        print("-" * 80)

        print("提示詞: In the year 2050,")
        print("補全: ", end="", flush=True)

        # 流式補全
        stream = client.completions.create(
            model="facebook/opt-125m",
            prompt="In the year 2050,",
            max_tokens=80,
            temperature=0.8,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].text:
                print(chunk.choices[0].text, end="", flush=True)

        print("\n")

    except Exception as e:
        print(f"✗ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


def advanced_parameters():
    """
    高級參數配置

    展示各種 API 參數的使用
    """
    print("\n" + "=" * 80)
    print("示例 6: 高級參數配置")
    print("=" * 80)

    try:
        client = OpenAI(
            base_url="http://localhost:8000/v1",
            api_key="dummy"
        )

        print("\n[1] 使用停止詞")
        print("-" * 80)

        response = client.chat.completions.create(
            model="facebook/opt-125m",
            messages=[{"role": "user", "content": "List three colors:"}],
            max_tokens=50,
            stop=["\n", "4."],  # 遇到換行或 "4." 就停止
        )

        print("提示: List three colors:")
        print(f"回應: {response.choices[0].message.content}")
        print(f"停止原因: {response.choices[0].finish_reason}")

        print("\n[2] 頻率和存在懲罰")
        print("-" * 80)

        response = client.chat.completions.create(
            model="facebook/opt-125m",
            messages=[{"role": "user", "content": "Write a creative sentence."}],
            max_tokens=50,
            frequency_penalty=1.0,  # 懲罰重複詞
            presence_penalty=1.0,   # 鼓勵新話題
            temperature=0.9,
        )

        print("提示: Write a creative sentence.")
        print(f"回應: {response.choices[0].message.content}")

        print("\n[3] Top-P 和 Top-K")
        print("-" * 80)

        response = client.chat.completions.create(
            model="facebook/opt-125m",
            messages=[{"role": "user", "content": "Complete this: AI is"}],
            max_tokens=40,
            top_p=0.9,  # Nucleus sampling
            temperature=0.8,
        )

        print("提示: Complete this: AI is")
        print(f"回應: {response.choices[0].message.content}")

        print("\n[4] Logprobs（如果支持）")
        print("-" * 80)

        # 注意: vLLM 可能不支持所有 OpenAI 參數
        response = client.completions.create(
            model="facebook/opt-125m",
            prompt="Hello",
            max_tokens=10,
            logprobs=2,  # 返回前 2 個 token 的對數概率
        )

        print("提示: Hello")
        print(f"補全: {response.choices[0].text}")

    except Exception as e:
        print(f"✗ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


def migration_guide():
    """
    從 OpenAI 遷移指南

    展示如何從 OpenAI 遷移到 vLLM
    """
    print("\n" + "=" * 80)
    print("從 OpenAI 遷移到 vLLM 指南")
    print("=" * 80)

    print("""
遷移步驟：
---------

1. 最小改動遷移（推薦）

   原始代碼（使用 OpenAI）:
   ```python
   from openai import OpenAI

   client = OpenAI(api_key="sk-...")

   response = client.chat.completions.create(
       model="gpt-3.5-turbo",
       messages=[{"role": "user", "content": "Hello!"}]
   )
   ```

   遷移後（使用 vLLM）:
   ```python
   from openai import OpenAI

   client = OpenAI(
       base_url="http://localhost:8000/v1",  # 只需改這裡
       api_key="dummy"  # vLLM 不需要真實 key
   )

   response = client.chat.completions.create(
       model="meta-llama/Llama-2-7b-chat-hf",  # 改為本地模型
       messages=[{"role": "user", "content": "Hello!"}]
   )
   ```

2. 使用環境變量

   ```python
   import os
   from openai import OpenAI

   # 設置環境變量
   os.environ["OPENAI_API_KEY"] = "dummy"
   os.environ["OPENAI_BASE_URL"] = "http://localhost:8000/v1"

   # 代碼無需改動
   client = OpenAI()
   response = client.chat.completions.create(...)
   ```

3. 兼容性注意事項

   完全兼容:
   ✓ chat.completions.create
   ✓ completions.create
   ✓ 流式響應 (stream=True)
   ✓ 大部分採樣參數

   部分兼容:
   ⚠ logprobs（可能不支持）
   ⚠ logit_bias（可能不支持）
   ⚠ 某些特殊參數

   不支持:
   ✗ embeddings（需要單獨的服務）
   ✗ fine-tuning API
   ✗ assistants API
   ✗ images, audio 等其他 API

4. 模型映射

   OpenAI 模型 → vLLM 替代方案:
   - gpt-3.5-turbo → Llama-2-7b-chat / Mistral-7B
   - gpt-4 → Llama-2-70b-chat / Mixtral-8x7B
   - text-davinci-003 → Llama-2-13b / Falcon-40B

5. 性能優化建議

   ✓ 使用批量請求提高吞吐量
   ✓ 啟用流式響應改善用戶體驗
   ✓ 根據負載調整 tensor_parallel_size
   ✓ 監控 GPU 內存使用率
   ✓ 使用量化模型降低成本

6. 部署建議

   開發環境:
   - 單 GPU
   - 小模型（7B）
   - 簡單啟動命令

   生產環境:
   - 多 GPU（tensor parallelism）
   - 大模型 + 量化
   - Docker + Kubernetes
   - 負載均衡
   - 監控和日誌
    """)


def best_practices():
    """
    OpenAI API 最佳實踐

    分享使用建議和技巧
    """
    print("\n" + "=" * 80)
    print("OpenAI API 最佳實踐")
    print("=" * 80)

    print("""
1. 連接管理
   ✓ 重用 OpenAI 客戶端實例
   ✓ 使用連接池
   ✓ 設置合理的超時時間
   ✓ 實現重試邏輯

2. 錯誤處理
   ```python
   from openai import OpenAI, OpenAIError

   client = OpenAI(base_url="http://localhost:8000/v1")

   try:
       response = client.chat.completions.create(...)
   except OpenAIError as e:
       print(f"API 錯誤: {e}")
   except Exception as e:
       print(f"其他錯誤: {e}")
   ```

3. 批量處理
   ✓ 使用批量 API 提高效率
   ✓ 合理設置批量大小
   ✓ 實現並發控制

   ```python
   import asyncio
   from openai import AsyncOpenAI

   async def process_batch(prompts):
       client = AsyncOpenAI(base_url="http://localhost:8000/v1")
       tasks = [
           client.chat.completions.create(
               model="model",
               messages=[{"role": "user", "content": p}]
           )
           for p in prompts
       ]
       return await asyncio.gather(*tasks)
   ```

4. 流式響應
   ✓ 用於長文本生成
   ✓ 改善用戶體驗
   ✓ 實現取消機制

   ```python
   stream = client.chat.completions.create(
       model="model",
       messages=messages,
       stream=True
   )

   try:
       for chunk in stream:
           if should_cancel:
               break
           process_chunk(chunk)
   finally:
       stream.close()
   ```

5. 監控和日誌
   ✓ 記錄請求/響應
   ✓ 監控延遲
   ✓ 跟踪 token 使用
   ✓ 錯誤率統計

6. 安全性
   ✓ 使用 HTTPS
   ✓ 設置 API 密鑰驗證
   ✓ 實現速率限制
   ✓ 輸入驗證和清理

7. 成本優化
   ✓ 限制 max_tokens
   ✓ 使用較小模型（如果足夠）
   ✓ 實現緩存機制
   ✓ 批量處理請求
    """)


def main():
    """
    主函數：運行所有示例
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 22 + "vLLM OpenAI 兼容 API 示例" + " " * 22 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    # 示例 1: 服務器啟動指南
    server_startup_guide()

    # 示例 2: 健康檢查
    check_server_health()

    # 以下示例需要服務器運行
    print("\n" + "=" * 80)
    print("注意：以下示例需要 vLLM API 服務器正在運行")
    print("=" * 80)

    user_input = input("\nvLLM API 服務器是否正在運行? (y/n): ").strip().lower()

    if user_input == 'y':
        try:
            # 示例 3: Chat Completions
            chat_completions_example()

            # 示例 4: Completions
            completions_example()

            # 示例 5: 流式響應
            streaming_example()

            # 示例 6: 高級參數
            advanced_parameters()

        except Exception as e:
            print(f"\n✗ 運行出錯: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print("\n跳過需要服務器的示例")

    # 示例 7: 遷移指南
    migration_guide()

    # 最佳實踐
    best_practices()

    print("\n" + "=" * 80)
    print("✓ 所有示例展示完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
