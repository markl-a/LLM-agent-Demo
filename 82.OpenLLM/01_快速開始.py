#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenLLM 快速開始示例
===================

本示例展示 OpenLLM 的基本使用方法，包括：
1. 使用 CLI 命令啟動模型服務
2. 使用 Python API 加載和運行模型
3. 使用客戶端連接到服務
4. 基本的文本生成

適用場景：
- 首次使用 OpenLLM
- 快速驗證環境配置
- 理解基本工作流程
"""

import sys
import subprocess
import time
from typing import Optional


def cli_quick_start():
    """
    CLI 快速開始示例

    展示如何使用命令行工具快速啟動 OpenLLM 服務
    """
    print("=" * 80)
    print("示例 1: CLI 快速開始")
    print("=" * 80)

    print("\n📝 CLI 命令示例：")
    print("-" * 80)

    # 基本啟動命令
    commands = [
        {
            "desc": "啟動 Llama 2 模型",
            "cmd": "openllm start llama --model-id meta-llama/Llama-2-7b-chat-hf"
        },
        {
            "desc": "啟動 Mistral 模型",
            "cmd": "openllm start mistral --model-id mistralai/Mistral-7B-Instruct-v0.1"
        },
        {
            "desc": "啟動 Falcon 模型",
            "cmd": "openllm start falcon --model-id tiiuae/falcon-7b-instruct"
        },
        {
            "desc": "使用量化模型",
            "cmd": "openllm start llama --model-id TheBloke/Llama-2-7B-Chat-GPTQ --quantize gptq"
        },
        {
            "desc": "指定 GPU 和端口",
            "cmd": "openllm start llama --model-id meta-llama/Llama-2-7b-chat-hf --device cuda:0 --port 3000"
        }
    ]

    for i, cmd_info in enumerate(commands, 1):
        print(f"\n{i}. {cmd_info['desc']}")
        print(f"   命令: {cmd_info['cmd']}")

    print("\n💡 提示：")
    print("   - 首次運行會自動下載模型")
    print("   - 模型會緩存在 ~/.cache/huggingface/")
    print("   - 服務啟動後可通過 http://localhost:3000 訪問")
    print()


def python_api_quick_start():
    """
    Python API 快速開始示例

    展示如何在 Python 代碼中直接使用 OpenLLM
    """
    print("\n" + "=" * 80)
    print("示例 2: Python API 快速開始")
    print("=" * 80)

    try:
        import openllm

        print("\n正在加載模型...")
        print("⚠️  首次運行需要下載模型，請耐心等待...")

        # 使用較小的模型進行快速測試
        # 如果沒有 GPU，建議使用更小的模型或量化版本
        llm = openllm.LLM(
            "opt",  # 使用 OPT 模型（較小，適合測試）
            model_id="facebook/opt-125m",  # 125M 參數的小模型
        )

        print("✓ 模型加載成功！")

        # 基本推理
        print("\n進行文本生成...")
        prompt = "Hello, my name is"

        print(f"提示詞: {prompt}")
        result = llm(prompt, max_new_tokens=50)

        print(f"\n生成結果:")
        print(f"{result}")

    except ImportError:
        print("✗ 錯誤: 未安裝 openllm")
        print("請運行: pip install openllm")
        sys.exit(1)
    except Exception as e:
        print(f"✗ 錯誤: {str(e)}")
        print("\n💡 提示: 如果遇到內存不足，請嘗試：")
        print("   1. 使用更小的模型")
        print("   2. 使用量化版本")
        print("   3. 確保有足夠的 GPU 內存")
        sys.exit(1)


def client_api_example():
    """
    客戶端 API 示例

    展示如何使用客戶端連接到 OpenLLM 服務
    """
    print("\n" + "=" * 80)
    print("示例 3: 客戶端 API 使用")
    print("=" * 80)

    print("\n📝 使用步驟：")
    print("-" * 80)
    print("1. 啟動服務（在另一個終端）：")
    print("   openllm start llama --model-id meta-llama/Llama-2-7b-chat-hf")
    print()
    print("2. 使用 Python 客戶端：")
    print()

    # 示例代碼
    example_code = '''
import openllm

# 創建客戶端
client = openllm.client.HTTPClient("http://localhost:3000")

# 發送查詢
response = client.query("What is machine learning?")
print(response)

# 流式生成
for chunk in client.query_stream("Tell me a story"):
    print(chunk, end="", flush=True)
'''

    print(example_code)

    # 嘗試連接到服務（如果正在運行）
    try:
        import openllm
        import requests

        print("\n嘗試連接到本地服務...")
        response = requests.get("http://localhost:3000/health", timeout=2)

        if response.status_code == 200:
            print("✓ 檢測到正在運行的服務！")

            client = openllm.client.HTTPClient("http://localhost:3000")
            result = client.query("Hello, how are you?")

            print("\n查詢結果:")
            print(result)
        else:
            print("⚠️  服務未響應")

    except requests.exceptions.RequestException:
        print("ℹ️  未檢測到運行中的服務")
        print("   請先啟動 OpenLLM 服務再運行客戶端代碼")
    except ImportError:
        print("⚠️  需要安裝 openllm 和 requests")
    except Exception as e:
        print(f"ℹ️  {str(e)}")


def interactive_chat_example():
    """
    交互式對話示例

    展示如何創建簡單的交互式聊天界面
    """
    print("\n" + "=" * 80)
    print("示例 4: 交互式對話")
    print("=" * 80)

    print("\n📝 交互式聊天代碼示例：")
    print("-" * 80)

    chat_code = '''
import openllm

# 加載聊天模型
llm = openllm.LLM(
    "llama",
    model_id="meta-llama/Llama-2-7b-chat-hf"
)

print("聊天已啟動！輸入 'quit' 退出")

while True:
    user_input = input("\\nYou: ")

    if user_input.lower() in ['quit', 'exit']:
        break

    # 構建對話提示詞
    prompt = f"[INST] {user_input} [/INST]"

    # 生成回覆
    response = llm(prompt, max_new_tokens=200)
    print(f"\\nAssistant: {response}")

print("\\n再見！")
'''

    print(chat_code)
    print()


def batch_inference_example():
    """
    批量推理示例

    展示如何批量處理多個請求
    """
    print("\n" + "=" * 80)
    print("示例 5: 批量推理")
    print("=" * 80)

    try:
        import openllm

        print("\n正在加載模型...")
        llm = openllm.LLM("opt", model_id="facebook/opt-125m")

        # 批量提示詞
        prompts = [
            "The future of AI is",
            "Machine learning helps us",
            "Python is a programming language that",
            "Deep learning models are",
        ]

        print(f"\n批量處理 {len(prompts)} 個提示詞...")

        # 批量生成
        results = []
        for i, prompt in enumerate(prompts):
            print(f"處理 {i+1}/{len(prompts)}: {prompt[:30]}...")
            result = llm(prompt, max_new_tokens=30)
            results.append(result)

        # 顯示結果
        print("\n生成結果：")
        print("-" * 80)
        for i, (prompt, result) in enumerate(zip(prompts, results), 1):
            print(f"\n[{i}] 提示詞: {prompt}")
            print(f"    生成: {result}")

    except Exception as e:
        print(f"✗ 錯誤: {str(e)}")
        print("這是一個演示，實際使用時需要適當的環境配置")


def environment_check():
    """
    環境檢查

    檢查必要的依賴和配置
    """
    print("\n" + "=" * 80)
    print("環境檢查")
    print("=" * 80)

    checks = []

    # 檢查 Python 版本
    import sys
    python_version = sys.version_info
    checks.append({
        "name": "Python 版本",
        "status": python_version >= (3, 8),
        "value": f"{python_version.major}.{python_version.minor}.{python_version.micro}"
    })

    # 檢查 OpenLLM
    try:
        import openllm
        checks.append({
            "name": "OpenLLM",
            "status": True,
            "value": openllm.__version__
        })
    except ImportError:
        checks.append({
            "name": "OpenLLM",
            "status": False,
            "value": "未安裝"
        })

    # 檢查 PyTorch
    try:
        import torch
        checks.append({
            "name": "PyTorch",
            "status": True,
            "value": torch.__version__
        })

        # 檢查 CUDA
        checks.append({
            "name": "CUDA 可用",
            "status": torch.cuda.is_available(),
            "value": "是" if torch.cuda.is_available() else "否"
        })

        if torch.cuda.is_available():
            checks.append({
                "name": "GPU 名稱",
                "status": True,
                "value": torch.cuda.get_device_name(0)
            })
    except ImportError:
        checks.append({
            "name": "PyTorch",
            "status": False,
            "value": "未安裝"
        })

    # 檢查 BentoML
    try:
        import bentoml
        checks.append({
            "name": "BentoML",
            "status": True,
            "value": bentoml.__version__
        })
    except ImportError:
        checks.append({
            "name": "BentoML",
            "status": False,
            "value": "未安裝"
        })

    # 顯示檢查結果
    print()
    for check in checks:
        status_icon = "✓" if check["status"] else "✗"
        print(f"{status_icon} {check['name']}: {check['value']}")

    print()


def main():
    """
    主函數：運行所有示例
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "OpenLLM 快速開始示例" + " " * 20 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    # 環境檢查
    environment_check()

    # 運行示例
    try:
        # CLI 示例
        cli_quick_start()

        # Python API 示例
        python_api_quick_start()

        # 客戶端示例
        client_api_example()

        # 交互式聊天示例
        interactive_chat_example()

        # 批量推理示例
        batch_inference_example()

        print("\n" + "=" * 80)
        print("✓ 所有示例展示完成！")
        print("=" * 80)
        print("\n💡 下一步：")
        print("   1. 查看其他示例文件了解更多功能")
        print("   2. 閱讀 README.md 了解完整文檔")
        print("   3. 訪問 https://github.com/bentoml/OpenLLM 獲取更多資源")
        print()

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
