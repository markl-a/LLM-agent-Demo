#!/bin/bash
# LLM Agent Demo - Docker Entrypoint Script
# 容器啟動腳本，用於初始化環境和啟動服務

set -e

echo "======================================"
echo "LLM Agent Demo - Container Starting"
echo "======================================"

# ==================== 環境變數檢查 ====================
echo "Checking environment variables..."

# 檢查是否至少配置了一個 LLM API Key
if [ -z "$OPENAI_API_KEY" ] && [ -z "$GOOGLE_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$GROQ_API_KEY" ]; then
    echo "⚠️  WARNING: No LLM API keys configured!"
    echo "   Please set at least one of: OPENAI_API_KEY, GOOGLE_API_KEY, ANTHROPIC_API_KEY, GROQ_API_KEY"
    echo "   Some features may not work without API keys."
fi

# 檢查 Ollama 連接
if [ -n "$OLLAMA_HOST" ]; then
    echo "Checking Ollama connection at: $OLLAMA_HOST"
    max_retries=30
    retry_count=0
    until curl -sf "$OLLAMA_HOST/api/tags" > /dev/null 2>&1 || [ $retry_count -eq $max_retries ]; do
        echo "Waiting for Ollama to be ready... ($retry_count/$max_retries)"
        retry_count=$((retry_count + 1))
        sleep 2
    done

    if [ $retry_count -eq $max_retries ]; then
        echo "⚠️  WARNING: Could not connect to Ollama at $OLLAMA_HOST"
        echo "   Ollama features may not be available."
    else
        echo "✓ Ollama is ready"
    fi
fi

# 檢查 ChromaDB 連接
if [ -n "$CHROMADB_HOST" ]; then
    echo "Checking ChromaDB connection at: $CHROMADB_HOST:$CHROMADB_PORT"
    max_retries=30
    retry_count=0
    until curl -sf "http://$CHROMADB_HOST:$CHROMADB_PORT/api/v1/heartbeat" > /dev/null 2>&1 || [ $retry_count -eq $max_retries ]; do
        echo "Waiting for ChromaDB to be ready... ($retry_count/$max_retries)"
        retry_count=$((retry_count + 1))
        sleep 2
    done

    if [ $retry_count -eq $max_retries ]; then
        echo "⚠️  WARNING: Could not connect to ChromaDB at $CHROMADB_HOST:$CHROMADB_PORT"
        echo "   ChromaDB features may not be available."
    else
        echo "✓ ChromaDB is ready"
    fi
fi

# ==================== 目錄初始化 ====================
echo "Initializing directories..."

# 創建必要的目錄
mkdir -p /app/data
mkdir -p /app/outputs
mkdir -p /app/logs
mkdir -p /app/.cache

echo "✓ Directories initialized"

# ==================== 權限設置 ====================
echo "Setting up permissions..."

# 確保數據目錄可寫
if [ -w /app/data ] && [ -w /app/outputs ] && [ -w /app/logs ]; then
    echo "✓ Permissions OK"
else
    echo "⚠️  WARNING: Some directories may not be writable"
fi

# ==================== 環境信息 ====================
echo ""
echo "======================================"
echo "Environment Information:"
echo "======================================"
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"
echo "Environment: ${ENVIRONMENT:-production}"
echo "Log level: ${LOG_LEVEL:-INFO}"
echo "Default LLM Model: ${DEFAULT_LLM_MODEL:-gpt-4}"

if [ -n "$LANGCHAIN_TRACING_V2" ] && [ "$LANGCHAIN_TRACING_V2" = "true" ]; then
    echo "LangSmith Tracing: ENABLED"
    echo "LangSmith Project: ${LANGCHAIN_PROJECT:-llm-agent-demo}"
fi

# ==================== 顯示可用的 LLM 提供商 ====================
echo ""
echo "======================================"
echo "Available LLM Providers:"
echo "======================================"

[ -n "$OPENAI_API_KEY" ] && echo "✓ OpenAI" || echo "✗ OpenAI"
[ -n "$GOOGLE_API_KEY" ] && echo "✓ Google Gemini" || echo "✗ Google Gemini"
[ -n "$ANTHROPIC_API_KEY" ] && echo "✓ Anthropic Claude" || echo "✗ Anthropic Claude"
[ -n "$GROQ_API_KEY" ] && echo "✓ Groq" || echo "✗ Groq"
[ -n "$COHERE_API_KEY" ] && echo "✓ Cohere" || echo "✗ Cohere"

# ==================== 顯示可用的向量數據庫 ====================
echo ""
echo "======================================"
echo "Available Vector Databases:"
echo "======================================"

[ -n "$CHROMADB_HOST" ] && echo "✓ ChromaDB (http://$CHROMADB_HOST:$CHROMADB_PORT)" || echo "✗ ChromaDB"
[ -n "$PINECONE_API_KEY" ] && echo "✓ Pinecone" || echo "✗ Pinecone"
[ -n "$QDRANT_URL" ] && echo "✓ Qdrant" || echo "✗ Qdrant"
[ -n "$WEAVIATE_URL" ] && echo "✓ Weaviate" || echo "✗ Weaviate"

# ==================== Jupyter 配置 ====================
if [ "$1" = "jupyter" ] || [ "$1" = "jupyter-lab" ]; then
    echo ""
    echo "======================================"
    echo "Starting Jupyter Lab..."
    echo "======================================"
    echo "Access Jupyter Lab at: http://localhost:8888"
    echo "No token or password required (development mode)"
fi

# ==================== 啟動服務 ====================
echo ""
echo "======================================"
echo "Starting application..."
echo "======================================"

# 執行傳入的命令
exec "$@"
