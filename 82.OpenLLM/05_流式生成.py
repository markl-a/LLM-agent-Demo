#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenLLM 流式生成示例
==================

本示例展示流式文本生成，包括：
1. Python API 流式生成
2. HTTP SSE 流式響應
3. OpenAI 兼容流式 API
4. WebSocket 流式傳輸
5. 流式生成優化

適用場景：
- 實時對話應用
- 改善用戶體驗
- 長文本生成
"""

import sys
import time
import json
from typing import Iterator, Optional


def python_streaming():
    """
    Python API 流式生成

    展示如何在 Python 中使用流式生成
    """
    print("=" * 80)
    print("示例 1: Python API 流式生成")
    print("=" * 80)

    print("\n📝 基本流式生成：")
    print("-" * 80)

    basic_example = '''
import openllm

# 加載模型
llm = openllm.LLM("opt", model_id="facebook/opt-125m")

# 流式生成
prompt = "Once upon a time, in a galaxy far away"

print("生成中: ", end="", flush=True)

for token in llm.generate_iter(
    prompt,
    max_new_tokens=100,
    temperature=0.7,
):
    print(token, end="", flush=True)

print()  # 換行
'''

    print(basic_example)

    print("\n實際演示：")
    print("-" * 80)

    try:
        import openllm

        llm = openllm.LLM("opt", model_id="facebook/opt-125m")

        prompt = "The future of technology is"
        print(f"提示詞: {prompt}")
        print("生成: ", end="", flush=True)

        for token in llm.generate_iter(prompt, max_new_tokens=50):
            print(token, end="", flush=True)
            time.sleep(0.02)  # 模擬實時效果

        print("\n✓ 生成完成")

    except Exception as e:
        print(f"ℹ️  演示跳過: {str(e)}")


def http_sse_streaming():
    """
    HTTP SSE 流式響應

    展示如何通過 HTTP Server-Sent Events 實現流式傳輸
    """
    print("\n" + "=" * 80)
    print("示例 2: HTTP SSE 流式響應")
    print("=" * 80)

    print("\n📝 服務端實現（FastAPI）：")
    print("-" * 80)

    server_code = '''
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import openllm
import json

app = FastAPI()
llm = openllm.LLM("llama", model_id="meta-llama/Llama-2-7b-chat-hf")

@app.post("/v1/generate_stream")
async def generate_stream(request: dict):
    """流式生成端點"""
    prompt = request.get("prompt", "")
    max_tokens = request.get("max_tokens", 100)

    async def generate():
        for token in llm.generate_iter(
            prompt,
            max_new_tokens=max_tokens,
            temperature=request.get("temperature", 0.7),
        ):
            # SSE 格式
            chunk = {
                "text": token,
                "finish_reason": None,
            }
            yield f"data: {json.dumps(chunk)}\\n\\n"

        # 發送結束信號
        final = {"text": "", "finish_reason": "stop"}
        yield f"data: {json.dumps(final)}\\n\\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )
'''

    print(server_code)

    print("\n客戶端使用（Python requests）：")
    print("-" * 80)

    client_code = '''
import requests
import json

url = "http://localhost:3000/v1/generate_stream"
data = {
    "prompt": "Tell me a story about AI",
    "max_tokens": 200,
    "temperature": 0.7,
}

# 流式請求
response = requests.post(url, json=data, stream=True)

print("生成: ", end="", flush=True)

for line in response.iter_lines():
    if line:
        # 解析 SSE 格式
        if line.startswith(b"data: "):
            data = json.loads(line[6:])
            text = data.get("text", "")
            if text:
                print(text, end="", flush=True)

            if data.get("finish_reason"):
                break

print("\\n✓ 完成")
'''

    print(client_code)

    print("\n客戶端使用（JavaScript fetch）：")
    print("-" * 80)

    js_code = '''
// JavaScript SSE 客戶端
async function streamGenerate(prompt) {
    const response = await fetch('http://localhost:3000/v1/generate_stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            prompt: prompt,
            max_tokens: 200,
        }),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\\n');

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = JSON.parse(line.slice(6));
                if (data.text) {
                    document.getElementById('output').textContent += data.text;
                }
            }
        }
    }
}
'''

    print(js_code)


def openai_compatible_streaming():
    """
    OpenAI 兼容流式 API

    展示如何使用 OpenAI 客戶端進行流式生成
    """
    print("\n" + "=" * 80)
    print("示例 3: OpenAI 兼容流式 API")
    print("=" * 80)

    print("\n📝 使用 OpenAI Python 客戶端：")
    print("-" * 80)

    openai_code = '''
from openai import OpenAI

# 連接到 OpenLLM 服務
client = OpenAI(
    base_url="http://localhost:3000/v1",
    api_key="not-needed",
)

# Chat Completions 流式
print("Assistant: ", end="", flush=True)

stream = client.chat.completions.create(
    model="llama",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me about machine learning"},
    ],
    stream=True,  # 啟用流式
    max_tokens=200,
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)

print()

# Completions 流式
stream = client.completions.create(
    model="llama",
    prompt="The benefits of AI are",
    stream=True,
    max_tokens=100,
)

for chunk in stream:
    if chunk.choices[0].text:
        print(chunk.choices[0].text, end="", flush=True)
'''

    print(openai_code)

    print("\n實際測試：")
    print("-" * 80)

    try:
        import requests

        # 檢查服務是否運行
        response = requests.get("http://localhost:3000/health", timeout=2)

        if response.status_code == 200:
            print("✓ 檢測到運行中的服務")

            # 嘗試流式請求
            from openai import OpenAI

            client = OpenAI(
                base_url="http://localhost:3000/v1",
                api_key="not-needed",
            )

            print("\n測試流式生成: ", end="", flush=True)

            stream = client.completions.create(
                model="llama",
                prompt="Hello, I am",
                stream=True,
                max_tokens=20,
            )

            for chunk in stream:
                if chunk.choices[0].text:
                    print(chunk.choices[0].text, end="", flush=True)

            print("\n✓ 流式生成成功")

    except Exception as e:
        print(f"ℹ️  服務未運行或測試跳過: {type(e).__name__}")


def websocket_streaming():
    """
    WebSocket 流式傳輸

    展示如何使用 WebSocket 實現雙向流式通信
    """
    print("\n" + "=" * 80)
    print("示例 4: WebSocket 流式傳輸")
    print("=" * 80)

    print("\n📝 服務端實現（FastAPI + WebSocket）：")
    print("-" * 80)

    server_code = '''
from fastapi import FastAPI, WebSocket
import openllm
import json

app = FastAPI()
llm = openllm.LLM("llama", model_id="meta-llama/Llama-2-7b-chat-hf")

@app.websocket("/ws/generate")
async def websocket_generate(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            # 接收客戶端消息
            data = await websocket.receive_json()
            prompt = data.get("prompt", "")

            # 發送開始信號
            await websocket.send_json({
                "type": "start",
                "message": "生成開始"
            })

            # 流式生成並發送
            for token in llm.generate_iter(
                prompt,
                max_new_tokens=data.get("max_tokens", 100),
            ):
                await websocket.send_json({
                    "type": "token",
                    "text": token,
                })

            # 發送完成信號
            await websocket.send_json({
                "type": "done",
                "message": "生成完成"
            })

    except Exception as e:
        await websocket.close()
'''

    print(server_code)

    print("\n客戶端實現（Python）：")
    print("-" * 80)

    client_code = '''
import asyncio
import websockets
import json

async def stream_chat():
    uri = "ws://localhost:3000/ws/generate"

    async with websockets.connect(uri) as websocket:
        # 發送請求
        await websocket.send(json.dumps({
            "prompt": "Tell me about quantum computing",
            "max_tokens": 200,
        }))

        # 接收流式響應
        print("Assistant: ", end="", flush=True)

        while True:
            message = await websocket.recv()
            data = json.loads(message)

            if data["type"] == "token":
                print(data["text"], end="", flush=True)
            elif data["type"] == "done":
                print()
                break

# 運行
asyncio.run(stream_chat())
'''

    print(client_code)

    print("\n客戶端實現（JavaScript）：")
    print("-" * 80)

    js_code = '''
// JavaScript WebSocket 客戶端
const ws = new WebSocket('ws://localhost:3000/ws/generate');

ws.onopen = () => {
    // 發送請求
    ws.send(JSON.stringify({
        prompt: 'Explain artificial intelligence',
        max_tokens: 200,
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    switch (data.type) {
        case 'start':
            console.log('生成開始');
            break;
        case 'token':
            document.getElementById('output').textContent += data.text;
            break;
        case 'done':
            console.log('生成完成');
            ws.close();
            break;
    }
};
'''

    print(js_code)


def streaming_optimization():
    """
    流式生成優化

    展示如何優化流式生成的性能和體驗
    """
    print("\n" + "=" * 80)
    print("示例 5: 流式生成優化")
    print("=" * 80)

    print("\n📝 優化技巧：")
    print("-" * 80)

    print("\n1. 緩衝優化：")
    buffering_code = '''
# 使用令牌緩衝提高傳輸效率
def buffered_streaming(llm, prompt, buffer_size=5):
    """緩衝多個 token 後再發送"""
    buffer = []

    for token in llm.generate_iter(prompt, max_new_tokens=200):
        buffer.append(token)

        if len(buffer) >= buffer_size:
            yield ''.join(buffer)
            buffer = []

    # 發送剩餘的 token
    if buffer:
        yield ''.join(buffer)

# 使用
for chunk in buffered_streaming(llm, "Your prompt"):
    print(chunk, end="", flush=True)
'''

    print(buffering_code)

    print("\n2. 超時處理：")
    timeout_code = '''
import asyncio

async def streaming_with_timeout(llm, prompt, timeout=30):
    """帶超時的流式生成"""
    try:
        async with asyncio.timeout(timeout):
            for token in llm.generate_iter(prompt):
                yield token
    except asyncio.TimeoutError:
        yield "\\n[生成超時]"
'''

    print(timeout_code)

    print("\n3. 錯誤處理：")
    error_handling_code = '''
def safe_streaming(llm, prompt):
    """帶錯誤處理的流式生成"""
    try:
        for token in llm.generate_iter(
            prompt,
            max_new_tokens=200,
        ):
            yield {
                "status": "generating",
                "text": token,
                "error": None,
            }

        # 成功完成
        yield {
            "status": "completed",
            "text": "",
            "error": None,
        }

    except Exception as e:
        # 錯誤處理
        yield {
            "status": "error",
            "text": "",
            "error": str(e),
        }
'''

    print(error_handling_code)

    print("\n4. 進度追蹤：")
    progress_code = '''
def streaming_with_progress(llm, prompt, max_tokens=200):
    """帶進度顯示的流式生成"""
    generated_tokens = 0

    for token in llm.generate_iter(
        prompt,
        max_new_tokens=max_tokens,
    ):
        generated_tokens += 1
        progress = (generated_tokens / max_tokens) * 100

        yield {
            "text": token,
            "tokens_generated": generated_tokens,
            "max_tokens": max_tokens,
            "progress": f"{progress:.1f}%",
        }
'''

    print(progress_code)

    print("\n\n💡 最佳實踐：")
    print("-" * 80)

    best_practices = [
        "使用適當的緩衝大小（通常 3-10 個 token）",
        "設置合理的超時時間",
        "實現完善的錯誤處理機制",
        "監控生成速度和延遲",
        "對長文本考慮分段生成",
        "使用 WebSocket 實現雙向通信",
        "客戶端實現重連機制",
    ]

    for i, practice in enumerate(best_practices, 1):
        print(f"{i}. {practice}")


def main():
    """
    主函數：運行所有示例
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "OpenLLM 流式生成示例" + " " * 20 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    try:
        # 示例 1: Python 流式生成
        python_streaming()

        # 示例 2: HTTP SSE
        http_sse_streaming()

        # 示例 3: OpenAI 兼容
        openai_compatible_streaming()

        # 示例 4: WebSocket
        websocket_streaming()

        # 示例 5: 優化
        streaming_optimization()

        print("\n" + "=" * 80)
        print("✓ 所有示例展示完成！")
        print("=" * 80)
        print("\n💡 關鍵要點：")
        print("   1. 流式生成改善用戶體驗")
        print("   2. 支持多種傳輸協議（SSE、WebSocket）")
        print("   3. OpenAI 兼容 API 簡化集成")
        print("   4. 需要適當的錯誤處理和優化")
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
