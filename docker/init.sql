-- LLM Agent Demo - PostgreSQL 初始化腳本
-- 創建必要的數據庫表和索引

-- 創建擴展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 會話表（用於存儲聊天會話）
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- 消息表（用於存儲聊天消息）
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Agent 執行記錄表
CREATE TABLE IF NOT EXISTS agent_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name VARCHAR(255) NOT NULL,
    task TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    result JSONB,
    error TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms INTEGER,
    metadata JSONB
);

-- 文檔存儲表（用於 RAG）
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255),
    content TEXT NOT NULL,
    source VARCHAR(255),
    doc_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- 向量嵌入記錄表（記錄哪些文檔已經被嵌入到向量數據庫）
CREATE TABLE IF NOT EXISTS vector_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    vector_db VARCHAR(50) NOT NULL,
    collection_name VARCHAR(255) NOT NULL,
    embedding_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    UNIQUE(document_id, vector_db, collection_name)
);

-- API 調用日誌表（用於追蹤和成本管理）
CREATE TABLE IF NOT EXISTS api_call_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    endpoint VARCHAR(255),
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    cost_usd DECIMAL(10, 6),
    latency_ms INTEGER,
    status VARCHAR(50),
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- 創建索引以提高查詢性能
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_created_at ON chat_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_agent_executions_status ON agent_executions(status);
CREATE INDEX IF NOT EXISTS idx_agent_executions_agent_name ON agent_executions(agent_name);
CREATE INDEX IF NOT EXISTS idx_agent_executions_started_at ON agent_executions(started_at);
CREATE INDEX IF NOT EXISTS idx_documents_doc_type ON documents(doc_type);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);
CREATE INDEX IF NOT EXISTS idx_vector_embeddings_document_id ON vector_embeddings(document_id);
CREATE INDEX IF NOT EXISTS idx_api_call_logs_provider ON api_call_logs(provider);
CREATE INDEX IF NOT EXISTS idx_api_call_logs_created_at ON api_call_logs(created_at);

-- 創建更新時間戳的函數
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 為需要的表創建觸發器
CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 創建視圖：最近的聊天會話
CREATE OR REPLACE VIEW recent_chat_sessions AS
SELECT
    s.id,
    s.session_name,
    s.created_at,
    s.updated_at,
    COUNT(m.id) as message_count,
    MAX(m.created_at) as last_message_at
FROM chat_sessions s
LEFT JOIN chat_messages m ON s.id = m.session_id
GROUP BY s.id, s.session_name, s.created_at, s.updated_at
ORDER BY s.updated_at DESC;

-- 創建視圖：API 使用統計
CREATE OR REPLACE VIEW api_usage_stats AS
SELECT
    provider,
    model,
    COUNT(*) as call_count,
    SUM(prompt_tokens) as total_prompt_tokens,
    SUM(completion_tokens) as total_completion_tokens,
    SUM(total_tokens) as total_tokens,
    SUM(cost_usd) as total_cost_usd,
    AVG(latency_ms) as avg_latency_ms,
    DATE_TRUNC('day', created_at) as date
FROM api_call_logs
GROUP BY provider, model, DATE_TRUNC('day', created_at)
ORDER BY date DESC;

-- 創建視圖：Agent 執行統計
CREATE OR REPLACE VIEW agent_execution_stats AS
SELECT
    agent_name,
    status,
    COUNT(*) as execution_count,
    AVG(duration_ms) as avg_duration_ms,
    MIN(duration_ms) as min_duration_ms,
    MAX(duration_ms) as max_duration_ms,
    DATE_TRUNC('day', started_at) as date
FROM agent_executions
WHERE duration_ms IS NOT NULL
GROUP BY agent_name, status, DATE_TRUNC('day', started_at)
ORDER BY date DESC;

-- 插入示例數據（可選）
-- INSERT INTO chat_sessions (session_name, metadata)
-- VALUES ('Example Session', '{"tags": ["demo", "example"]}');

-- 顯示創建的表
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
