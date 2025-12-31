#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenLLM 推理服務示例
===================

本示例展示如何啟動和使用推理服務，包括：
1. 啟動 HTTP 服務
2. 使用 RESTful API
3. OpenAI 兼容 API
4. 服務配置和優化
5. 健康檢查和監控

適用場景：
- 部署生產環境服務
- API 集成
- 服務監控和維護
"""

import sys
import time
import json
import requests
from typing import Dict, Any, Optional, List


def start_server_cli():
    """
    使用 CLI 啟動服務

    展示各種服務啟動選項
    """
    print("=" * 80)
    print("示例 1: 使用 CLI 啟動服務")
    print("=" * 80)

    print("\n📝 基本啟動命令：")
    print("-" * 80)

    commands = [
        {
            "desc": "基本啟動",
            "cmd": "openllm start llama --model-id meta-llama/Llama-2-7b-chat-hf"
        },
        {
            "desc": "指定端口和主機",
            "cmd": "openllm start llama --model-id meta-llama/Llama-2-7b-chat-hf --host 0.0.0.0 --port 3000"
        },
        {
            "desc": "設置工作進程數",
            "cmd": "openllm start llama --model-id meta-llama/Llama-2-7b-chat-hf --workers 4"
        },
        {
            "desc": "啟用 CORS",
            "cmd": "openllm start llama --model-id meta-llama/Llama-2-7b-chat-hf --cors"
        },
        {
            "desc": "後台運行",
            "cmd": "openllm start llama --model-id meta-llama/Llama-2-7b-chat-hf --daemon"
        },
    ]

    for i, cmd in enumerate(commands, 1):
        print(f"\n{i}. {cmd['desc']}")
        print(f"   {cmd['cmd']}")

    print("\n\n💡 服務管理命令：")
    print("-" * 80)
    print("openllm list                    # 列出所有運行的服務")
    print("openllm stop <model_name>       # 停止指定服務")
    print("openllm stop-all                # 停止所有服務")


def start_server_python():
    """
    使用 Python API 啟動服務

    展示如何在 Python 代碼中啟動服務
    """
    print("\n" + "=" * 80)
    print("示例 2: 使用 Python API 啟動服務")
    print("=" * 80)

    code_example = '''
import openllm

# 方式 1: 使用 serve 方法
llm = openllm.LLM("llama", model_id="meta-llama/Llama-2-7b-chat-hf")

# 啟動服務（阻塞式）
llm.serve(
    host="0.0.0.0",
    port=3000,
    workers=1,
    cors=True,
    timeout=3600,
)

# 方式 2: 使用 BentoML Runner
import bentoml

llm = openllm.LLM("llama", model_id="meta-llama/Llama-2-7b-chat-hf")
runner = bentoml.Runner(llm, name="llm_runner")

# 創建服務
svc = bentoml.Service("llm-service", runners=[runner])

@svc.api(input=bentoml.io.JSON(), output=bentoml.io.JSON())
async def generate(input_data: dict) -> dict:
    prompt = input_data.get("prompt", "")
    result = await runner.generate.async_run(
        prompt,
        max_new_tokens=input_data.get("max_tokens", 100)
    )
    return {"text": result}

# 啟動服務
# bentoml serve service:svc --host 0.0.0.0 --port 3000
'''

    print(code_example)


def use_rest_api():
    """
    使用 REST API

    展示如何通過 HTTP API 與服務交互
    """
    print("\n" + "=" * 80)
    print("示例 3: 使用 REST API")
    print("=" * 80)

    print("\n📝 API 端點：")
    print("-" * 80)

    endpoints = [
        {
            "method": "GET",
            "path": "/health",
            "desc": "健康檢查",
        },
        {
            "method": "GET",
            "path": "/models",
            "desc": "列出可用模型",
        },
        {
            "method": "POST",
            "path": "/v1/generate",
            "desc": "生成文本",
        },
        {
            "method": "POST",
            "path": "/v1/generate_stream",
            "desc": "流式生成",
        },
    ]

    for endpoint in endpoints:
        print(f"\n{endpoint['method']:6} {endpoint['path']:30} - {endpoint['desc']}")

    print("\n\n使用示例：")
    print("-" * 80)

    # Python requests 示例
    python_example = '''
import requests
import json

# 1. 健康檢查
response = requests.get("http://localhost:3000/health")
print(response.json())
# 輸出: {"status": "ok"}

# 2. 生成文本
data = {
    "prompt": "What is machine learning?",
    "max_new_tokens": 100,
    "temperature": 0.7,
    "top_p": 0.95,
}

response = requests.post(
    "http://localhost:3000/v1/generate",
    json=data,
    headers={"Content-Type": "application/json"}
)

result = response.json()
print(result["text"])

# 3. 流式生成
response = requests.post(
    "http://localhost:3000/v1/generate_stream",
    json=data,
    stream=True
)

for line in response.iter_lines():
    if line:
        chunk = json.loads(line)
        print(chunk["text"], end="", flush=True)
'''

    print(python_example)

    # cURL 示例
    print("\ncURL 示例：")
    print("-" * 80)

    curl_examples = '''
# 健康檢查
curl http://localhost:3000/health

# 生成文本
curl -X POST http://localhost:3000/v1/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "prompt": "What is AI?",
    "max_new_tokens": 100
  }'

# 流式生成
curl -X POST http://localhost:3000/v1/generate_stream \\
  -H "Content-Type: application/json" \\
  -d '{
    "prompt": "Tell me a story",
    "max_new_tokens": 200
  }' \\
  --no-buffer
'''

    print(curl_examples)

    # 實際測試（如果服務正在運行）
    print("\n嘗試連接到本地服務...")
    print("-" * 80)

    try:
        response = requests.get("http://localhost:3000/health", timeout=2)
        if response.status_code == 200:
            print("✓ 服務正在運行！")
            print(f"響應: {response.json()}")

            # 測試生成
            print("\n測試文本生成...")
            gen_response = requests.post(
                "http://localhost:3000/v1/generate",
                json={
                    "prompt": "Hello, I am",
                    "max_new_tokens": 20,
                },
                timeout=30
            )

            if gen_response.status_code == 200:
                print(f"生成結果: {gen_response.json()}")
            else:
                print(f"生成失敗: {gen_response.status_code}")

    except requests.exceptions.RequestException:
        print("ℹ️  未檢測到運行中的服務")
        print("   請先啟動服務: openllm start llama --model-id meta-llama/Llama-2-7b-chat-hf")


def openai_compatible_api():
    """
    OpenAI 兼容 API

    展示如何使用 OpenAI 兼容的 API 接口
    """
    print("\n" + "=" * 80)
    print("示例 4: OpenAI 兼容 API")
    print("=" * 80)

    print("\n📝 OpenAI 兼容性說明：")
    print("-" * 80)
    print("OpenLLM 提供與 OpenAI API 兼容的接口，可以無縫切換。")

    print("\n\n啟動 OpenAI 兼容服務：")
    print("-" * 80)

    start_cmd = '''
# 啟動時啟用 OpenAI 兼容模式
openllm start llama \\
  --model-id meta-llama/Llama-2-7b-chat-hf \\
  --backend vllm \\
  --openai-compatible
'''

    print(start_cmd)

    print("\n使用 OpenAI Python 客戶端：")
    print("-" * 80)

    openai_example = '''
from openai import OpenAI

# 創建客戶端，指向 OpenLLM 服務
client = OpenAI(
    base_url="http://localhost:3000/v1",
    api_key="not-needed",  # OpenLLM 不需要 API key
)

# 1. Chat Completions
response = client.chat.completions.create(
    model="llama",  # 或使用完整的 model_id
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is machine learning?"}
    ],
    max_tokens=100,
    temperature=0.7,
)

print(response.choices[0].message.content)

# 2. 流式響應
stream = client.chat.completions.create(
    model="llama",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True,
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)

# 3. Completions (非聊天格式)
response = client.completions.create(
    model="llama",
    prompt="The future of AI is",
    max_tokens=50,
)

print(response.choices[0].text)
'''

    print(openai_example)

    print("\n\n兼容性說明：")
    print("-" * 80)
    print("✓ 支持 chat.completions")
    print("✓ 支持 completions")
    print("✓ 支持流式響應")
    print("✓ 支持大部分 OpenAI 參數")
    print("⚠️  某些高級功能可能不完全兼容")


def server_configuration():
    """
    服務配置

    展示各種服務配置選項
    """
    print("\n" + "=" * 80)
    print("示例 5: 服務配置")
    print("=" * 80)

    print("\n📝 配置文件示例 (config.yaml)：")
    print("-" * 80)

    yaml_config = '''
# OpenLLM 服務配置
model_name: llama
model_id: meta-llama/Llama-2-7b-chat-hf

# 後端配置
backend: vllm
backend_config:
  max_model_len: 4096
  gpu_memory_utilization: 0.9
  tensor_parallel_size: 1

# 服務器配置
server_config:
  host: 0.0.0.0
  port: 3000
  workers: 1
  timeout: 3600
  cors: true

# 生成參數默認值
generation_config:
  max_new_tokens: 256
  temperature: 0.7
  top_p: 0.95
  top_k: 50

# 日誌配置
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 性能配置
performance:
  max_batch_size: 32
  max_waiting_time: 10  # 毫秒
'''

    print(yaml_config)

    print("\n使用配置文件啟動：")
    print("-" * 80)
    print("openllm start --config config.yaml")

    print("\n\nPython 配置示例：")
    print("-" * 80)

    python_config = '''
import openllm

# 創建配置
config = openllm.LLMConfig(
    max_new_tokens=256,
    temperature=0.7,
    top_p=0.95,
    repetition_penalty=1.1,
)

# 使用配置加載模型
llm = openllm.LLM(
    "llama",
    model_id="meta-llama/Llama-2-7b-chat-hf",
    llm_config=config,
)

# 啟動服務
llm.serve(host="0.0.0.0", port=3000)
'''

    print(python_config)


def monitoring_and_health():
    """
    監控和健康檢查

    展示如何監控服務狀態
    """
    print("\n" + "=" * 80)
    print("示例 6: 監控和健康檢查")
    print("=" * 80)

    print("\n📝 監控端點：")
    print("-" * 80)

    endpoints = {
        "/health": "基本健康檢查",
        "/readyz": "就緒狀態檢查（Kubernetes）",
        "/livez": "存活狀態檢查（Kubernetes）",
        "/metrics": "Prometheus 指標",
    }

    for path, desc in endpoints.items():
        print(f"{path:20} - {desc}")

    print("\n\n健康檢查示例：")
    print("-" * 80)

    health_example = '''
import requests
import time

def check_health(url: str, timeout: int = 30):
    """檢查服務健康狀態"""
    start = time.time()

    while time.time() - start < timeout:
        try:
            response = requests.get(f"{url}/health", timeout=2)
            if response.status_code == 200:
                print(f"✓ 服務健康: {response.json()}")
                return True
        except:
            pass

        time.sleep(1)

    print("✗ 服務不健康")
    return False

# 使用
check_health("http://localhost:3000")
'''

    print(health_example)

    print("\n\nPrometheus 監控配置：")
    print("-" * 80)

    prometheus_config = '''
# prometheus.yml
scrape_configs:
  - job_name: 'openllm'
    static_configs:
      - targets: ['localhost:3000']
    metrics_path: '/metrics'
    scrape_interval: 10s
'''

    print(prometheus_config)

    print("\n常用指標：")
    print("-" * 80)
    metrics = [
        "request_total - 總請求數",
        "request_duration_seconds - 請求延遲",
        "model_inference_duration - 推理時間",
        "gpu_memory_usage - GPU 內存使用",
        "active_requests - 活躍請求數",
    ]

    for metric in metrics:
        print(f"  • {metric}")


def main():
    """
    主函數：運行所有示例
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "OpenLLM 推理服務示例" + " " * 20 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    try:
        # 示例 1: CLI 啟動
        start_server_cli()

        # 示例 2: Python 啟動
        start_server_python()

        # 示例 3: REST API
        use_rest_api()

        # 示例 4: OpenAI 兼容
        openai_compatible_api()

        # 示例 5: 服務配置
        server_configuration()

        # 示例 6: 監控
        monitoring_and_health()

        print("\n" + "=" * 80)
        print("✓ 所有示例展示完成！")
        print("=" * 80)
        print("\n💡 關鍵要點：")
        print("   1. OpenLLM 提供多種服務啟動方式")
        print("   2. 支持 OpenAI 兼容 API")
        print("   3. 完整的監控和健康檢查")
        print("   4. 靈活的配置選項")
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
