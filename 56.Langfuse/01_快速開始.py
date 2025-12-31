"""
Langfuse 快速開始示例

這個示例展示了如何快速開始使用 Langfuse 進行 LLM 應用的可觀測性追蹤。
包含基本的客戶端初始化、追蹤創建和 OpenAI API 整合。

主要功能：
1. Langfuse 客戶端初始化和配置
2. 基本的追蹤（Trace）創建
3. Generation 記錄
4. OpenAI API 調用追蹤
5. 錯誤處理和調試
6. 同步和異步操作
7. 元數據管理
8. 用戶和會話追蹤

作者: Langfuse Team
日期: 2025-01-01
"""

import os
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from langfuse import Langfuse
from openai import OpenAI
import asyncio


# ============================================================================
# 第一部分：基本配置和初始化
# ============================================================================

def initialize_langfuse() -> Langfuse:
    """
    初始化 Langfuse 客戶端

    這個函數展示了如何正確配置和初始化 Langfuse 客戶端。
    支持從環境變量或直接傳參兩種方式。

    Returns:
        Langfuse: 配置好的 Langfuse 客戶端實例
    """
    # 方法 1: 從環境變量讀取配置（推薦用於生產環境）
    # export LANGFUSE_PUBLIC_KEY="pk-lf-..."
    # export LANGFUSE_SECRET_KEY="sk-lf-..."
    # export LANGFUSE_HOST="https://cloud.langfuse.com"

    # 方法 2: 直接傳入參數（適合開發和測試）
    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY", "pk-lf-demo-key"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY", "sk-lf-demo-secret"),
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        # 可選配置
        debug=True,  # 啟用調試模式，輸出詳細日誌
        enabled=True,  # 是否啟用追蹤（可用於開關功能）
        flush_at=15,  # 批量發送的閾值
        flush_interval=0.5,  # 自動刷新間隔（秒）
    )

    print("✅ Langfuse 客戶端初始化成功")
    print(f"   Host: {langfuse.base_url}")
    print(f"   Debug: {langfuse.debug}")

    return langfuse


def initialize_openai() -> OpenAI:
    """
    初始化 OpenAI 客戶端

    Returns:
        OpenAI: OpenAI 客戶端實例
    """
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY", "sk-demo-key")
    )

    print("✅ OpenAI 客戶端初始化成功")
    return client


# ============================================================================
# 第二部分：基本追蹤功能
# ============================================================================

def basic_trace_example(langfuse: Langfuse):
    """
    基本追蹤示例

    展示如何創建一個簡單的追蹤，記錄基本的操作信息。
    追蹤是 Langfuse 中最頂層的組織單位。

    Args:
        langfuse: Langfuse 客戶端實例
    """
    print("\n" + "="*60)
    print("基本追蹤示例")
    print("="*60)

    # 創建一個追蹤
    trace = langfuse.trace(
        name="simple-chat",  # 追蹤名稱
        user_id="user-123",  # 用戶 ID（可選）
        session_id="session-456",  # 會話 ID（可選）
        metadata={  # 元數據（可選）
            "environment": "development",
            "version": "1.0.0",
            "feature": "chat"
        },
        tags=["demo", "quickstart"],  # 標籤（可選）
        input={"message": "你好，Langfuse！"},  # 輸入數據
        timestamp=datetime.now()  # 時間戳（可選，默認為當前時間）
    )

    print(f"📊 創建追蹤: {trace.id}")
    print(f"   名稱: simple-chat")
    print(f"   用戶: user-123")
    print(f"   會話: session-456")

    # 模擬一些處理時間
    time.sleep(0.5)

    # 更新追蹤的輸出
    trace.update(
        output={"response": "你好！很高興認識你。"},
        metadata={"processing_time": 0.5}
    )

    print("✅ 追蹤更新完成")

    return trace


def generation_example(langfuse: Langfuse, openai_client: OpenAI):
    """
    Generation 追蹤示例

    Generation 用於記錄 LLM 的生成操作，包括輸入、輸出、
    模型信息、使用量和成本等。

    Args:
        langfuse: Langfuse 客戶端實例
        openai_client: OpenAI 客戶端實例
    """
    print("\n" + "="*60)
    print("Generation 追蹤示例")
    print("="*60)

    # 創建追蹤
    trace = langfuse.trace(
        name="chat-with-gpt",
        user_id="user-789",
        metadata={"type": "chat"}
    )

    # 準備聊天消息
    messages = [
        {"role": "system", "content": "你是一個友善的 AI 助手。"},
        {"role": "user", "content": "請用一句話介紹 Langfuse。"}
    ]

    # 創建 generation（在調用 LLM 之前）
    generation = trace.generation(
        name="openai-chat-completion",
        model="gpt-3.5-turbo",
        input=messages,
        metadata={
            "interface": "openai",
            "temperature": 0.7
        }
    )

    print(f"📝 創建 Generation: {generation.id}")

    try:
        # 調用 OpenAI API
        start_time = time.time()

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )

        end_time = time.time()
        latency = end_time - start_time

        # 提取響應內容
        assistant_message = response.choices[0].message.content

        print(f"💬 AI 回應: {assistant_message}")

        # 結束 generation 並記錄結果
        generation.end(
            output=assistant_message,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            level="DEFAULT",  # 日誌級別: DEBUG, DEFAULT, WARNING, ERROR
            status_message="成功完成",
            metadata={
                "latency_ms": latency * 1000,
                "finish_reason": response.choices[0].finish_reason
            }
        )

        print(f"✅ Generation 完成")
        print(f"   Token 使用: {response.usage.total_tokens}")
        print(f"   延遲: {latency*1000:.2f}ms")

    except Exception as e:
        # 記錄錯誤
        generation.end(
            level="ERROR",
            status_message=str(e),
            metadata={"error_type": type(e).__name__}
        )
        print(f"❌ 錯誤: {e}")

    return trace


# ============================================================================
# 第三部分：多步驟追蹤
# ============================================================================

def multi_step_trace_example(langfuse: Langfuse, openai_client: OpenAI):
    """
    多步驟追蹤示例

    展示如何在一個追蹤中記錄多個步驟，例如檢索增強生成（RAG）
    或多輪對話等場景。

    Args:
        langfuse: Langfuse 客戶端實例
        openai_client: OpenAI 客戶端實例
    """
    print("\n" + "="*60)
    print("多步驟追蹤示例")
    print("="*60)

    # 創建主追蹤
    trace = langfuse.trace(
        name="rag-pipeline",
        user_id="user-001",
        metadata={"pipeline": "retrieval-augmented-generation"}
    )

    print(f"🔄 開始 RAG 流程: {trace.id}")

    # 步驟 1: 查詢向量化
    step1 = trace.span(
        name="query-embedding",
        input={"query": "什麼是 Langfuse？"}
    )

    time.sleep(0.2)  # 模擬處理

    step1.end(
        output={"embedding": [0.1, 0.2, 0.3]},  # 簡化的向量
        metadata={"model": "text-embedding-ada-002"}
    )
    print("  ✓ 步驟 1: 查詢向量化完成")

    # 步驟 2: 檢索相關文檔
    step2 = trace.span(
        name="document-retrieval",
        input={"embedding": [0.1, 0.2, 0.3], "top_k": 3}
    )

    time.sleep(0.3)  # 模擬檢索

    retrieved_docs = [
        "Langfuse 是一個開源的 LLM 可觀測性平台。",
        "它提供追蹤、提示管理和評估功能。",
        "採用 MIT 許可證，可以自託管。"
    ]

    step2.end(
        output={"documents": retrieved_docs},
        metadata={"num_results": 3, "source": "vector_db"}
    )
    print("  ✓ 步驟 2: 文檔檢索完成")

    # 步驟 3: 生成回答
    context = "\n".join(retrieved_docs)
    messages = [
        {"role": "system", "content": f"基於以下信息回答問題：\n{context}"},
        {"role": "user", "content": "什麼是 Langfuse？"}
    ]

    step3 = trace.generation(
        name="answer-generation",
        model="gpt-3.5-turbo",
        input=messages
    )

    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.3
        )

        answer = response.choices[0].message.content

        step3.end(
            output=answer,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        )

        print("  ✓ 步驟 3: 答案生成完成")
        print(f"\n📝 最終答案: {answer}")

    except Exception as e:
        step3.end(level="ERROR", status_message=str(e))
        print(f"  ✗ 步驟 3 失敗: {e}")

    # 更新整體追蹤
    trace.update(
        output={"answer": answer if 'answer' in locals() else None},
        metadata={"total_steps": 3}
    )

    print(f"✅ RAG 流程完成")

    return trace


# ============================================================================
# 第四部分：會話追蹤
# ============================================================================

def session_tracking_example(langfuse: Langfuse, openai_client: OpenAI):
    """
    會話追蹤示例

    展示如何追蹤多輪對話會話，將相關的追蹤組織在一起。

    Args:
        langfuse: Langfuse 客戶端實例
        openai_client: OpenAI 客戶端實例
    """
    print("\n" + "="*60)
    print("會話追蹤示例")
    print("="*60)

    # 會話配置
    session_id = f"session-{int(time.time())}"
    user_id = "user-chat-001"

    print(f"💬 開始新會話: {session_id}")
    print(f"👤 用戶: {user_id}")

    # 對話歷史
    conversation_history = []

    # 輪次 1
    print("\n--- 輪次 1 ---")
    user_message_1 = "你好！"
    conversation_history.append({"role": "user", "content": user_message_1})

    trace1 = langfuse.trace(
        name="chat-turn-1",
        user_id=user_id,
        session_id=session_id,
        input={"message": user_message_1},
        tags=["chat", "greeting"]
    )

    generation1 = trace1.generation(
        name="response-1",
        model="gpt-3.5-turbo",
        input=conversation_history
    )

    try:
        response1 = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation_history
        )

        assistant_message_1 = response1.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": assistant_message_1})

        generation1.end(
            output=assistant_message_1,
            usage={
                "prompt_tokens": response1.usage.prompt_tokens,
                "completion_tokens": response1.usage.completion_tokens,
                "total_tokens": response1.usage.total_tokens
            }
        )

        print(f"用戶: {user_message_1}")
        print(f"助手: {assistant_message_1}")

    except Exception as e:
        generation1.end(level="ERROR", status_message=str(e))

    # 輪次 2
    print("\n--- 輪次 2 ---")
    user_message_2 = "Langfuse 有什麼功能？"
    conversation_history.append({"role": "user", "content": user_message_2})

    trace2 = langfuse.trace(
        name="chat-turn-2",
        user_id=user_id,
        session_id=session_id,
        input={"message": user_message_2},
        tags=["chat", "question"]
    )

    generation2 = trace2.generation(
        name="response-2",
        model="gpt-3.5-turbo",
        input=conversation_history
    )

    try:
        response2 = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation_history
        )

        assistant_message_2 = response2.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": assistant_message_2})

        generation2.end(
            output=assistant_message_2,
            usage={
                "prompt_tokens": response2.usage.prompt_tokens,
                "completion_tokens": response2.usage.completion_tokens,
                "total_tokens": response2.usage.total_tokens
            }
        )

        print(f"用戶: {user_message_2}")
        print(f"助手: {assistant_message_2}")

    except Exception as e:
        generation2.end(level="ERROR", status_message=str(e))

    print(f"\n✅ 會話完成，共 {len(conversation_history)//2} 輪對話")

    return session_id


# ============================================================================
# 第五部分：異步操作
# ============================================================================

async def async_trace_example(langfuse: Langfuse):
    """
    異步追蹤示例

    展示如何在異步環境中使用 Langfuse 進行追蹤。

    Args:
        langfuse: Langfuse 客戶端實例
    """
    print("\n" + "="*60)
    print("異步追蹤示例")
    print("="*60)

    # 創建多個異步任務
    async def async_task(task_id: int, langfuse: Langfuse):
        trace = langfuse.trace(
            name=f"async-task-{task_id}",
            metadata={"task_id": task_id, "type": "async"}
        )

        print(f"  🚀 啟動任務 {task_id}")

        # 模擬異步操作
        await asyncio.sleep(0.5)

        trace.update(
            output={"result": f"Task {task_id} completed"},
            metadata={"status": "success"}
        )

        print(f"  ✅ 任務 {task_id} 完成")

        return task_id

    # 並發執行多個任務
    tasks = [async_task(i, langfuse) for i in range(1, 6)]
    results = await asyncio.gather(*tasks)

    print(f"\n✅ 所有異步任務完成: {results}")


# ============================================================================
# 第六部分：錯誤處理和調試
# ============================================================================

def error_handling_example(langfuse: Langfuse):
    """
    錯誤處理示例

    展示如何正確處理和記錄錯誤。

    Args:
        langfuse: Langfuse 客戶端實例
    """
    print("\n" + "="*60)
    print("錯誤處理示例")
    print("="*60)

    trace = langfuse.trace(
        name="error-handling-demo",
        metadata={"purpose": "demonstration"}
    )

    generation = trace.generation(
        name="problematic-operation",
        model="gpt-3.5-turbo",
        input={"query": "測試錯誤處理"}
    )

    try:
        # 模擬一個錯誤
        raise ValueError("這是一個模擬的錯誤")

    except Exception as e:
        # 記錄詳細的錯誤信息
        generation.end(
            level="ERROR",
            status_message=str(e),
            metadata={
                "error_type": type(e).__name__,
                "error_message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

        print(f"❌ 捕獲錯誤: {e}")
        print(f"   錯誤類型: {type(e).__name__}")
        print(f"   已記錄到 Langfuse")

    return trace


# ============================================================================
# 第七部分：數據刷新和清理
# ============================================================================

def flush_and_cleanup_example(langfuse: Langfuse):
    """
    數據刷新和清理示例

    展示如何確保所有數據都被發送到 Langfuse 服務器。

    Args:
        langfuse: Langfuse 客戶端實例
    """
    print("\n" + "="*60)
    print("數據刷新和清理示例")
    print("="*60)

    # 創建一些追蹤
    for i in range(5):
        trace = langfuse.trace(
            name=f"batch-trace-{i}",
            input={"index": i}
        )
        trace.update(output={"processed": True})

    print("📤 創建了 5 個追蹤")

    # 手動刷新，確保數據發送
    print("🔄 刷新數據到 Langfuse...")
    langfuse.flush()

    print("✅ 數據刷新完成")

    # 注意：在應用退出前應該調用 flush()
    # 或者使用 shutdown() 來確保所有數據都已發送


# ============================================================================
# 主程序
# ============================================================================

def main():
    """
    主函數：運行所有示例
    """
    print("\n" + "="*70)
    print("Langfuse 快速開始示例")
    print("="*70)

    # 初始化客戶端
    langfuse = initialize_langfuse()
    openai_client = initialize_openai()

    # 運行示例
    try:
        # 1. 基本追蹤
        basic_trace_example(langfuse)

        # 2. Generation 追蹤
        generation_example(langfuse, openai_client)

        # 3. 多步驟追蹤
        multi_step_trace_example(langfuse, openai_client)

        # 4. 會話追蹤
        session_tracking_example(langfuse, openai_client)

        # 5. 異步操作
        asyncio.run(async_trace_example(langfuse))

        # 6. 錯誤處理
        error_handling_example(langfuse)

        # 7. 數據刷新
        flush_and_cleanup_example(langfuse)

        print("\n" + "="*70)
        print("✅ 所有示例運行完成！")
        print("="*70)
        print("\n📊 查看追蹤數據:")
        print(f"   訪問: {langfuse.base_url}")
        print("\n💡 提示:")
        print("   - 在生產環境中使用環境變量配置密鑰")
        print("   - 記得在應用退出前調用 langfuse.flush()")
        print("   - 使用有意義的追蹤名稱和元數據")
        print("   - 為不同的操作類型設置適當的標籤")

    except Exception as e:
        print(f"\n❌ 運行示例時出錯: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 確保所有數據都被發送
        print("\n🔄 最終數據刷新...")
        langfuse.flush()
        print("✅ 完成")


if __name__ == "__main__":
    main()
