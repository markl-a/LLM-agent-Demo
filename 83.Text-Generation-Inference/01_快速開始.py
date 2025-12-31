#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TGI 快速開始示例
================

本示例展示 Text Generation Inference 的基本使用，包括：
1. 啟動 TGI 服務
2. 使用 Python 客戶端
3. HTTP API 調用
4. 基本配置選項

適用場景：
- 首次使用 TGI
- 快速驗證環境
- 理解基本工作流程
"""

import sys


def start_server_instructions():
    """展示如何啟動 TGI 服務"""
    print("=" * 80)
    print("示例 1: 啟動 TGI 服務")
    print("=" * 80)

    print("\n📝 使用 Docker 啟動（推薦）：")
    print("-" * 80)

    docker_commands = '''
# 基本啟動（GPU）
docker run --rm --gpus all --shm-size 1g -p 8080:80 \\
    -v $PWD/data:/data \\
    ghcr.io/huggingface/text-generation-inference:latest \\
    --model-id meta-llama/Llama-2-7b-chat-hf

# CPU 模式
docker run --rm -p 8080:80 \\
    -v $PWD/data:/data \\
    ghcr.io/huggingface/text-generation-inference:latest \\
    --model-id facebook/opt-125m

# 使用 HuggingFace token（私有模型）
docker run --rm --gpus all -p 8080:80 \\
    -v $PWD/data:/data \\
    -e HUGGING_FACE_HUB_TOKEN=your_token_here \\
    ghcr.io/huggingface/text-generation-inference:latest \\
    --model-id meta-llama/Llama-2-7b-chat-hf
'''

    print(docker_commands)

    print("\n本地啟動：")
    print("-" * 80)
    print("text-generation-launcher --model-id meta-llama/Llama-2-7b-chat-hf --port 8080")


def python_client_basic():
    """使用 Python 客戶端的基本示例"""
    print("\n" + "=" * 80)
    print("示例 2: Python 客戶端基本使用")
    print("=" * 80)

    print("\n📝 安裝客戶端：")
    print("pip install text-generation\n")

    print("基本使用：")
    print("-" * 80)

    code_example = '''
from text_generation import Client

# 創建客戶端（連接到 TGI 服務）
client = Client("http://localhost:8080")

# 1. 簡單生成
response = client.generate(
    "What is machine learning?",
    max_new_tokens=100,
)
print(f"生成結果: {response.generated_text}")

# 2. 帶參數的生成
response = client.generate(
    "Explain quantum computing",
    max_new_tokens=200,
    temperature=0.7,
    top_p=0.95,
    do_sample=True,
)
print(response.generated_text)

# 3. 檢查詳細信息
print(f"生成的 token 數: {len(response.details.tokens)}")
print(f"生成時間: {response.details.generated_tokens} tokens")
'''

    print(code_example)

    # 實際測試
    print("\n嘗試連接到服務...")
    print("-" * 80)

    try:
        from text_generation import Client
        import requests

        # 檢查服務是否運行
        response = requests.get("http://localhost:8080/health", timeout=2)

        if response.status_code == 200:
            print("✓ 檢測到運行中的 TGI 服務！")

            client = Client("http://localhost:8080")

            # 簡單測試
            result = client.generate(
                "Hello, I am",
                max_new_tokens=20,
            )

            print(f"\n測試生成:")
            print(f"提示詞: Hello, I am")
            print(f"結果: {result.generated_text}")

        else:
            print("⚠️  服務未正常響應")

    except requests.exceptions.RequestException:
        print("ℹ️  未檢測到運行中的服務")
        print("   請先啟動 TGI 服務再運行此示例")
    except ImportError:
        print("⚠️  需要安裝: pip install text-generation")
    except Exception as e:
        print(f"ℹ️  {str(e)}")


def http_api_examples():
    """HTTP API 直接調用示例"""
    print("\n" + "=" * 80)
    print("示例 3: HTTP API 直接調用")
    print("=" * 80)

    print("\n📝 使用 curl：")
    print("-" * 80)

    curl_examples = '''
# 生成文本
curl http://localhost:8080/generate \\
    -X POST \\
    -H 'Content-Type: application/json' \\
    -d '{
        "inputs": "What is AI?",
        "parameters": {
            "max_new_tokens": 100,
            "temperature": 0.7
        }
    }'

# 檢查健康狀態
curl http://localhost:8080/health

# 獲取模型信息
curl http://localhost:8080/info
'''

    print(curl_examples)

    print("\nPython requests 庫：")
    print("-" * 80)

    requests_code = '''
import requests
import json

# 生成請求
response = requests.post(
    "http://localhost:8080/generate",
    json={
        "inputs": "Explain machine learning",
        "parameters": {
            "max_new_tokens": 150,
            "temperature": 0.7,
            "top_p": 0.95,
        }
    }
)

result = response.json()
print(result["generated_text"])

# 查看詳細信息
print(f"Token 詳情: {result.get('details', {})}")
'''

    print(requests_code)


def configuration_options():
    """配置選項說明"""
    print("\n" + "=" * 80)
    print("示例 4: 常用配置選項")
    print("=" * 80)

    print("\n📝 生成參數：")
    print("-" * 80)

    params = {
        "max_new_tokens": "生成的最大 token 數",
        "temperature": "溫度，控制隨機性 (0-2)",
        "top_p": "nucleus sampling 參數 (0-1)",
        "top_k": "top-k sampling 參數",
        "do_sample": "是否使用採樣 (True/False)",
        "repetition_penalty": "重複懲罰 (1.0-2.0)",
        "stop_sequences": "停止序列列表",
        "seed": "隨機種子，用於可重複生成",
    }

    for param, desc in params.items():
        print(f"{param:25} - {desc}")

    print("\n\n服務器啟動參數：")
    print("-" * 80)

    server_params = '''
--model-id              # 模型 ID
--num-shard            # 張量並行數（多 GPU）
--port                 # 服務端口
--max-concurrent-requests  # 最大並發請求數
--max-input-length     # 最大輸入長度
--max-total-tokens     # 最大總 token 數
--max-batch-prefill-tokens  # 批預填充最大 token 數
--quantize             # 量化方法 (gptq/awq/bitsandbytes)
--dtype                # 數據類型 (float16/bfloat16)
'''

    print(server_params)


def troubleshooting():
    """常見問題排查"""
    print("\n" + "=" * 80)
    print("示例 5: 常見問題排查")
    print("=" * 80)

    print("\n📝 問題診斷：")
    print("-" * 80)

    issues = [
        {
            "問題": "服務啟動失敗",
            "可能原因": [
                "GPU 內存不足",
                "模型下載失敗",
                "Docker 配置問題"
            ],
            "解決方案": [
                "使用更小的模型或量化版本",
                "檢查網絡連接和 HF token",
                "確保 Docker 有 GPU 訪問權限"
            ]
        },
        {
            "問題": "生成速度慢",
            "可能原因": [
                "批處理未優化",
                "GPU 未充分利用",
                "輸入/輸出過長"
            ],
            "解決方案": [
                "調整 max-batch-total-tokens",
                "使用張量並行",
                "限制 max-input-length"
            ]
        },
        {
            "問題": "內存溢出 (OOM)",
            "可能原因": [
                "模型太大",
                "並發請求過多",
                "批大小過大"
            ],
            "解決方案": [
                "使用量化模型",
                "減少 max-concurrent-requests",
                "調整批處理參數"
            ]
        },
    ]

    for issue in issues:
        print(f"\n❓ {issue['問題']}:")
        print("   可能原因:")
        for reason in issue['可能原因']:
            print(f"   - {reason}")
        print("   解決方案:")
        for solution in issue['解決方案']:
            print(f"   ✓ {solution}")


def main():
    """主函數：運行所有示例"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "TGI 快速開始示例" + " " * 22 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    try:
        # 示例 1: 啟動服務
        start_server_instructions()

        # 示例 2: Python 客戶端
        python_client_basic()

        # 示例 3: HTTP API
        http_api_examples()

        # 示例 4: 配置選項
        configuration_options()

        # 示例 5: 問題排查
        troubleshooting()

        print("\n" + "=" * 80)
        print("✓ 所有示例展示完成！")
        print("=" * 80)
        print("\n💡 下一步：")
        print("   1. 查看其他示例了解更多功能")
        print("   2. 閱讀 README.md 了解完整文檔")
        print("   3. 訪問 HuggingFace 文檔獲取更多資源")
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
