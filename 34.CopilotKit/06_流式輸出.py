"""
CopilotKit 流式輸出範例

這個範例展示如何實現流式（streaming）響應，提供流暢的用戶體驗：
1. 基礎流式輸出
2. 進度更新
3. 中斷處理
4. 實時數據流
5. 長任務處理
6. 前端實時更新

流式輸出的優勢：
- 即時反饋，提升用戶體驗
- 處理長時間運行的任務
- 實時進度更新
- 降低感知延遲
"""

import os
import asyncio
from typing import AsyncGenerator, Any, Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from copilotkit import CopilotKitSDK, Action
from copilotkit.integrations.fastapi import add_fastapi_endpoint
import uvicorn
import json


# ============================================================================
# 第一部分：流式生成器函數
# ============================================================================

async def stream_text_generator(text: str, delay: float = 0.05) -> AsyncGenerator[str, None]:
    """
    逐字流式輸出文本

    Args:
        text: 要流式輸出的文本
        delay: 每個字符之間的延遲（秒）
    """
    for char in text:
        yield char
        await asyncio.sleep(delay)


async def stream_progress_generator(
    total_steps: int,
    task_name: str = "處理中"
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    流式輸出任務進度

    Args:
        total_steps: 總步驟數
        task_name: 任務名稱
    """
    for step in range(1, total_steps + 1):
        progress = {
            "step": step,
            "total": total_steps,
            "percentage": int((step / total_steps) * 100),
            "task": task_name,
            "message": f"正在執行步驟 {step}/{total_steps}"
        }
        yield json.dumps(progress) + "\\n"
        await asyncio.sleep(0.5)  # 模擬處理時間

    # 完成消息
    yield json.dumps({
        "step": total_steps,
        "total": total_steps,
        "percentage": 100,
        "task": task_name,
        "message": "任務完成！",
        "completed": True
    }) + "\\n"


async def stream_data_processing(
    data_items: list,
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    流式處理數據並輸出結果

    Args:
        data_items: 要處理的數據項列表
    """
    results = []

    for i, item in enumerate(data_items):
        # 模擬處理
        await asyncio.sleep(0.3)

        # 處理結果
        result = {
            "index": i,
            "item": item,
            "processed": f"已處理: {item}",
            "timestamp": asyncio.get_event_loop().time()
        }
        results.append(result)

        # 流式輸出當前結果
        yield json.dumps({
            "type": "progress",
            "current": i + 1,
            "total": len(data_items),
            "result": result
        }) + "\\n"

    # 輸出最終摘要
    yield json.dumps({
        "type": "complete",
        "total_processed": len(results),
        "results": results
    }) + "\\n"


# ============================================================================
# 第二部分：FastAPI 應用設置
# ============================================================================

app = FastAPI(title="CopilotKit 流式輸出範例")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.environ.setdefault("OPENAI_API_KEY", "your-openai-api-key")


# ============================================================================
# 第三部分：流式 Actions
# ============================================================================

async def generate_story_stream(topic: str) -> Dict[str, Any]:
    """
    流式生成故事（模擬）

    Args:
        topic: 故事主題

    Returns:
        故事內容
    """
    story = f"""
    從前，在一個關於{topic}的世界裡，
    有一位勇敢的探險者開始了他的旅程。
    他遇到了許多挑戰，但從未放棄。
    最終，他發現了{topic}的真正意義。
    這是一個關於堅持和勇氣的故事。
    """

    # 模擬流式輸出
    chunks = []
    for sentence in story.strip().split('\\n'):
        await asyncio.sleep(0.5)
        chunks.append(sentence.strip())

    return {
        "success": True,
        "topic": topic,
        "story": "\\n".join(chunks),
        "chunks_count": len(chunks)
    }


async def process_large_dataset(item_count: int) -> Dict[str, Any]:
    """
    處理大數據集並實時更新進度

    Args:
        item_count: 數據項數量

    Returns:
        處理結果
    """
    results = []

    for i in range(item_count):
        await asyncio.sleep(0.1)
        results.append({
            "id": i,
            "processed": True,
            "value": i * 2
        })

        # 每處理 10 個項目輸出一次進度
        if (i + 1) % 10 == 0 or i == item_count - 1:
            progress = {
                "processed": i + 1,
                "total": item_count,
                "percentage": int(((i + 1) / item_count) * 100)
            }

    return {
        "success": True,
        "total_processed": len(results),
        "results": results[:10],  # 只返回前 10 個結果示例
        "message": f"成功處理 {len(results)} 個項目"
    }


async def analyze_with_progress(text: str) -> Dict[str, Any]:
    """
    帶進度的文本分析

    Args:
        text: 要分析的文本

    Returns:
        分析結果
    """
    steps = [
        "分詞處理",
        "詞性標註",
        "情感分析",
        "關鍵詞提取",
        "生成摘要"
    ]

    results = {}

    for i, step in enumerate(steps):
        await asyncio.sleep(0.5)
        results[step] = f"{step}完成"

    return {
        "success": True,
        "text_length": len(text),
        "steps_completed": len(steps),
        "results": results,
        "summary": f"分析了 {len(text)} 個字符，完成 {len(steps)} 個步驟"
    }


# ============================================================================
# 第四部分：註冊 Actions
# ============================================================================

sdk = CopilotKitSDK()

sdk.add_action(Action(
    name="generate_story",
    description="根據主題流式生成故事",
    parameters=[
        {
            "name": "topic",
            "type": "string",
            "description": "故事主題",
            "required": True
        }
    ],
    handler=generate_story_stream
))

sdk.add_action(Action(
    name="process_dataset",
    description="處理大數據集並實時顯示進度",
    parameters=[
        {
            "name": "item_count",
            "type": "number",
            "description": "要處理的數據項數量",
            "required": True
        }
    ],
    handler=process_large_dataset
))

sdk.add_action(Action(
    name="analyze_text",
    description="帶進度的文本分析",
    parameters=[
        {
            "name": "text",
            "type": "string",
            "description": "要分析的文本",
            "required": True
        }
    ],
    handler=analyze_with_progress
))

add_fastapi_endpoint(app, sdk, "/copilotkit")


# ============================================================================
# 第五部分：流式 REST 端點
# ============================================================================

@app.get("/stream/text")
async def stream_text(text: str = "這是一個流式輸出的示例"):
    """流式輸出文本"""
    return StreamingResponse(
        stream_text_generator(text),
        media_type="text/plain"
    )


@app.get("/stream/progress")
async def stream_progress(steps: int = 10, task: str = "數據處理"):
    """流式輸出進度"""
    return StreamingResponse(
        stream_progress_generator(steps, task),
        media_type="application/x-ndjson"
    )


@app.get("/")
async def root():
    return {
        "message": "CopilotKit 流式輸出範例",
        "endpoints": {
            "stream_text": "/stream/text?text=你的文本",
            "stream_progress": "/stream/progress?steps=10&task=任務名稱"
        }
    }


# ============================================================================
# 第六部分：React 前端範例
# ============================================================================

REACT_CODE = """
// ===== App.tsx - 流式輸出前端 =====
import React, { useState, useEffect } from 'react';
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";
import { useCopilotAction } from "@copilotkit/react-core";
import "@copilotkit/react-ui/styles.css";

// ========== 1. 基礎流式輸出組件 ==========

function StreamingTextDemo() {
  const [streamedText, setStreamedText] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);

  const startStreaming = async () => {
    setIsStreaming(true);
    setStreamedText("");

    try {
      const response = await fetch('http://localhost:8000/stream/text?text=歡迎使用CopilotKit流式輸出功能！');
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) return;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        setStreamedText(prev => prev + chunk);
      }
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
      <h3>流式文本輸出</h3>
      <button
        onClick={startStreaming}
        disabled={isStreaming}
        style={{
          padding: '10px 20px',
          marginBottom: '15px',
          background: isStreaming ? '#ccc' : '#4CAF50',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: isStreaming ? 'not-allowed' : 'pointer'
        }}
      >
        {isStreaming ? '輸出中...' : '開始流式輸出'}
      </button>
      <div style={{
        padding: '15px',
        background: '#f5f5f5',
        borderRadius: '4px',
        minHeight: '100px',
        fontFamily: 'monospace'
      }}>
        {streamedText || '點擊按鈕開始...'}
      </div>
    </div>
  );
}

// ========== 2. 進度條組件 ==========

interface ProgressData {
  step: number;
  total: number;
  percentage: number;
  task: string;
  message: string;
  completed?: boolean;
}

function StreamingProgressDemo() {
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  const startTask = async () => {
    setIsRunning(true);
    setProgress(null);

    try {
      const response = await fetch('http://localhost:8000/stream/progress?steps=20&task=數據分析');
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) return;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\\n').filter(line => line.trim());

        for (const line of lines) {
          try {
            const data = JSON.parse(line);
            setProgress(data);
          } catch (e) {
            console.error('解析錯誤:', e);
          }
        }
      }
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
      <h3>流式進度更新</h3>
      <button
        onClick={startTask}
        disabled={isRunning}
        style={{
          padding: '10px 20px',
          marginBottom: '15px',
          background: isRunning ? '#ccc' : '#2196F3',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: isRunning ? 'not-allowed' : 'pointer'
        }}
      >
        {isRunning ? '執行中...' : '開始任務'}
      </button>

      {progress && (
        <div>
          <div style={{ marginBottom: '10px' }}>
            <strong>{progress.task}</strong>: {progress.message}
          </div>
          <div style={{
            width: '100%',
            height: '30px',
            background: '#e0e0e0',
            borderRadius: '15px',
            overflow: 'hidden'
          }}>
            <div style={{
              width: `${progress.percentage}%`,
              height: '100%',
              background: progress.completed ? '#4CAF50' : '#2196F3',
              transition: 'width 0.3s ease',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontWeight: 'bold'
            }}>
              {progress.percentage}%
            </div>
          </div>
          <div style={{ marginTop: '10px', color: '#666' }}>
            步驟: {progress.step} / {progress.total}
          </div>
        </div>
      )}
    </div>
  );
}

// ========== 3. 與 CopilotKit Actions 整合 ==========

function CopilotStreamingExample() {
  const [results, setResults] = useState<any[]>([]);

  useCopilotAction({
    name: "stream_story",
    description: "流式生成故事",
    parameters: [
      {
        name: "topic",
        type: "string",
        description: "故事主題",
        required: true
      }
    ],
    handler: async ({ topic }) => {
      // CopilotKit 自動處理流式響應
      return `正在生成關於 ${topic} 的故事...`;
    }
  });

  return (
    <div style={{ padding: '20px' }}>
      <h3>AI 流式生成</h3>
      <div className="ai-hints" style={{
        padding: '15px',
        background: '#e3f2fd',
        borderRadius: '5px'
      }}>
        <h4>💡 試試對 AI 說：</h4>
        <ul>
          <li>"生成一個關於勇氣的故事"</li>
          <li>"處理 100 個數據項"</li>
          <li>"分析這段文本：CopilotKit 是一個強大的框架"</li>
        </ul>
      </div>
    </div>
  );
}

// ========== 4. 主應用 ==========

function MainApp() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>CopilotKit 流式輸出範例</h1>

      <div style={{ display: 'grid', gap: '20px', marginTop: '20px' }}>
        <StreamingTextDemo />
        <StreamingProgressDemo />
        <CopilotStreamingExample />
      </div>
    </div>
  );
}

function App() {
  return (
    <CopilotKit runtimeUrl="http://localhost:8000/copilotkit">
      <CopilotSidebar
        instructions="你是一個助手，專門處理流式輸出任務。"
        labels={{
          title: "流式助手",
          initial: "我可以幫你處理流式任務！",
        }}
        defaultOpen={true}
      >
        <MainApp />
      </CopilotSidebar>
    </CopilotKit>
  );
}

export default App;
"""


if __name__ == "__main__":
    print("\\n" + "="*70)
    print("CopilotKit 流式輸出範例")
    print("="*70)
    print("\\n特點：")
    print("  • 實時文本流式輸出")
    print("  • 進度實時更新")
    print("  • 大數據集處理")
    print("  • 前端實時渲染")
    print("\\n端點：")
    print("  • /stream/text - 流式文本")
    print("  • /stream/progress - 流式進度")
    print("="*70 + "\\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)


"""
流式輸出最佳實踐：

1. 何時使用流式輸出
   ✓ 長時間運行的任務（>2秒）
   ✓ 大量數據處理
   ✓ 需要即時反饋的場景
   ✓ AI 文本生成

2. 實現要點
   ✓ 使用 AsyncGenerator
   ✓ 設置正確的 Content-Type
   ✓ 處理流中斷
   ✓ 提供進度信息

3. 前端處理
   ✓ 使用 ReadableStream
   ✓ 實時更新 UI
   ✓ 顯示進度條
   ✓ 支持取消操作

4. 錯誤處理
   ✓ 捕獲流中的異常
   ✓ 提供錯誤恢復機制
   ✓ 超時處理
   ✓ 網絡中斷處理

5. 性能優化
   ✓ 合理的塊大小
   ✓ 背壓處理
   ✓ 內存管理
   ✓ 連接池管理

流式輸出 vs 普通響應：

| 特性 | 流式輸出 | 普通響應 |
|------|---------|----------|
| 首字節時間 | 快 | 慢 |
| 內存占用 | 低 | 高 |
| 用戶體驗 | 優秀 | 一般 |
| 實現複雜度 | 高 | 低 |
| 錯誤處理 | 複雜 | 簡單 |
| 適用場景 | 長任務 | 短任務 |

常見問題：

Q: 如何取消流式請求？
A: 使用 AbortController：
   const controller = new AbortController();
   fetch(url, { signal: controller.signal });
   // 取消：controller.abort();

Q: 流式輸出時如何處理錯誤？
A: 在流中發送錯誤對象：
   yield json.dumps({"error": "錯誤信息"})

Q: 如何優化大文件流式傳輸？
A: 使用適當的塊大小（通常 8KB-64KB）
   並實現背壓機制

下一步：
- 查看 07_自定義UI.py 學習 UI 定制
- 查看 09_部署指南.py 了解生產部署
- 查看 10_最佳實踐.py 學習最佳實踐
"""
