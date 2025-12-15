# LLM Agent Demo - API 使用指南

本文檔介紹優化後的 `llm_agent_demo` 包的公開 API 和使用方法。

## 目錄

- [快速開始](#快速開始)
- [配置管理](#配置管理)
- [日誌系統](#日誌系統)
- [成本追蹤](#成本追蹤)
- [重試機制](#重試機制)
- [驗證器](#驗證器)
- [LangChain 工具](#langchain-工具)
- [模組結構](#模組結構)

---

## 快速開始

### 安裝

```bash
pip install -e .
```

### 基本使用

```python
# 從主模組直接導入所有常用工具
from llm_agent_demo import (
    get_settings,
    get_logger,
    CostTracker,
    validate_api_key,
    create_chat_model,
)

# 獲取配置
settings = get_settings()

# 創建日誌記錄器
logger = get_logger(__name__)
logger.info("應用程式啟動")

# 驗證 API 金鑰
try:
    api_key = validate_api_key(settings.openai_api_key, "OpenAI")
    logger.info("API 金鑰驗證成功")
except ValidationError as e:
    logger.error(f"API 金鑰無效: {e}")
```

---

## 配置管理

### 使用配置單例

```python
from llm_agent_demo import get_settings, Settings

# 獲取配置實例（單例模式）
settings = get_settings()

# 訪問配置項
print(f"OpenAI 模型: {settings.openai_model}")
print(f"日誌級別: {settings.log_level}")
print(f"環境: {settings.app_env}")

# 檢查環境
if settings.is_production():
    print("運行在生產環境")
else:
    print("運行在開發環境")
```

### 獲取特定 LLM 配置

```python
from llm_agent_demo import (
    get_openai_config,
    get_anthropic_config,
    get_google_config,
    get_groq_config,
)

# 獲取 OpenAI 配置
openai_config = get_openai_config()
print(f"API 金鑰: {openai_config['api_key'][:10]}...")
print(f"模型: {openai_config['model']}")

# 獲取 Anthropic 配置
anthropic_config = get_anthropic_config()

# 獲取 Google 配置
google_config = get_google_config()
```

### 重新載入配置

```python
from llm_agent_demo import reload_settings

# 更新環境變數後重新載入配置
import os
os.environ['OPENAI_MODEL'] = 'gpt-4o'
settings = reload_settings()
```

---

## 日誌系統

### 基本日誌

```python
from llm_agent_demo import get_logger, setup_logging

# 設置日誌系統
setup_logging(
    level="INFO",
    log_file="app.log",
    colorize=True,  # 彩色輸出
    json_format=False,  # 使用文本格式
)

# 獲取日誌記錄器
logger = get_logger(__name__)

# 記錄日誌
logger.debug("調試信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("錯誤信息")
logger.critical("嚴重錯誤")
```

### 預定義的日誌記錄器

```python
from llm_agent_demo.utils import (
    get_app_logger,
    get_langchain_logger,
    get_autogen_logger,
)

# 獲取應用程式日誌記錄器
app_logger = get_app_logger()
app_logger.info("應用程式啟動")

# 獲取 LangChain 專用日誌記錄器
langchain_logger = get_langchain_logger()
langchain_logger.info("LangChain 鏈執行完成")
```

### JSON 格式日誌

```python
from llm_agent_demo import setup_logging

# 設置 JSON 格式日誌（適合生產環境）
setup_logging(
    level="INFO",
    log_file="app.json",
    json_format=True,
)
```

---

## 成本追蹤

### 基本使用

```python
from llm_agent_demo import CostTracker, TokenCounter

# 創建成本追蹤器
tracker = CostTracker(save_path="usage_history.json")

# 記錄一次 API 使用
usage = tracker.track_usage(
    prompt_tokens=150,
    completion_tokens=300,
    model="gpt-4o-mini",
    provider="openai",
)

# 獲取總成本
total_cost = tracker.get_total_cost()
print(f"總成本: ${total_cost:.6f}")

# 獲取使用摘要
summary = tracker.get_summary()
print(f"總請求次數: {summary['total_requests']}")
print(f"總 Token 數: {summary['total_tokens']['total_tokens']:,}")

# 打印詳細摘要
tracker.print_summary()
```

### Token 估算

```python
from llm_agent_demo import TokenCounter

# 估算文本的 token 數量
text = "你好，這是一段測試文本。Hello, this is a test."
tokens = TokenCounter.estimate_tokens(text)
print(f"估算 Token 數: {tokens}")
```

---

## 重試機制

### 使用裝飾器

```python
from llm_agent_demo import (
    retry_with_exponential_backoff,
    retry_on_rate_limit,
    retry_on_network_error,
)

# 基本重試
@retry_with_exponential_backoff(max_retries=3, initial_delay=1.0)
def call_api():
    # API 調用代碼
    response = client.chat.completions.create(...)
    return response

# 處理速率限制
@retry_on_rate_limit(max_retries=5)
def call_with_rate_limit():
    # 可能遇到速率限制的 API 調用
    return client.chat.completions.create(...)

# 處理網絡錯誤
@retry_on_network_error(max_retries=3)
def call_with_network_retry():
    # 可能遇到網絡問題的 API 調用
    return requests.get("https://api.example.com/data")
```

### 使用上下文管理器

```python
from llm_agent_demo import RetryContext

retry_ctx = RetryContext(max_retries=3, initial_delay=1.0)

for attempt in retry_ctx:
    try:
        result = call_api()
        retry_ctx.mark_success()
        break
    except Exception as e:
        retry_ctx.handle_exception(e)

if retry_ctx.succeeded:
    print(f"成功！結果: {result}")
else:
    print(f"失敗！錯誤: {retry_ctx.last_exception}")
```

---

## 驗證器

### API 金鑰驗證

```python
from llm_agent_demo import (
    validate_api_key,
    validate_openai_api_key,
    validate_anthropic_api_key,
    ValidationError,
)

# 通用 API 金鑰驗證
try:
    api_key = validate_api_key("sk-...", provider="OpenAI")
    print("API 金鑰有效")
except ValidationError as e:
    print(f"驗證失敗: {e}")

# OpenAI 特定驗證
try:
    openai_key = validate_openai_api_key("sk-proj-...")
except ValidationError as e:
    print(f"OpenAI API 金鑰無效: {e}")

# Anthropic 特定驗證
try:
    anthropic_key = validate_anthropic_api_key("sk-ant-...")
except ValidationError as e:
    print(f"Anthropic API 金鑰無效: {e}")
```

### 模型參數驗證

```python
from llm_agent_demo import (
    validate_model_name,
    validate_temperature,
    validate_max_tokens,
    ValidationError,
)

# 驗證模型名稱
valid_models = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
try:
    model = validate_model_name("gpt-4o", valid_models=valid_models)
except ValidationError as e:
    print(f"模型名稱無效: {e}")

# 驗證溫度參數
try:
    temp = validate_temperature(0.7)
except ValidationError as e:
    print(f"溫度參數無效: {e}")

# 驗證最大 token 數
try:
    max_tokens = validate_max_tokens(4000)
except ValidationError as e:
    print(f"最大 token 數無效: {e}")
```

### 用戶輸入驗證和清理

```python
from llm_agent_demo import (
    validate_user_query,
    sanitize_user_input,
    ValidationError,
)

# 驗證用戶查詢
try:
    query = validate_user_query(
        user_input,
        min_length=1,
        max_length=2000,
        check_suspicious=True,
    )
    print(f"查詢有效: {query}")
except ValidationError as e:
    print(f"查詢無效: {e}")

# 清理用戶輸入（防止注入攻擊）
clean_text = sanitize_user_input(
    user_input,
    max_length=10000,
    allow_newlines=True,
    strip_html=True,
)
```

---

## LangChain 工具

### 創建聊天模型

```python
from llm_agent_demo import create_chat_model

# 創建 OpenAI 模型
llm = create_chat_model(
    provider="openai",
    model="gpt-4o-mini",
    temperature=0.7,
)

# 創建 Anthropic 模型
llm = create_chat_model(
    provider="anthropic",
    model="claude-3-5-sonnet-20241022",
    temperature=0.7,
)

# 創建 Google 模型
llm = create_chat_model(
    provider="google",
    model="gemini-2.0-flash-exp",
    temperature=0.7,
)

# 使用模型
response = llm.invoke("你好！請介紹一下自己。")
print(response.content)
```

### 創建嵌入模型

```python
from llm_agent_demo import create_embeddings

# 創建 OpenAI 嵌入模型
embeddings = create_embeddings(
    provider="openai",
    model="text-embedding-3-small",
)

# 創建 HuggingFace 嵌入模型
embeddings = create_embeddings(
    provider="huggingface",
    model="sentence-transformers/all-MiniLM-L6-v2",
)

# 生成嵌入向量
vectors = embeddings.embed_documents(["文檔1", "文檔2"])
query_vector = embeddings.embed_query("查詢文本")
```

### 創建向量存儲

```python
from llm_agent_demo import create_embeddings, create_vector_store

# 創建嵌入模型
embeddings = create_embeddings()

# 創建 Chroma 向量存儲
vectorstore = create_vector_store(
    store_type="chroma",
    embeddings=embeddings,
    persist_directory="./chroma_db",
    collection_name="my_docs",
)

# 添加文檔
vectorstore.add_texts(
    texts=["文檔1內容", "文檔2內容"],
    metadatas=[{"source": "doc1"}, {"source": "doc2"}],
)

# 相似度搜索
results = vectorstore.similarity_search("查詢", k=3)
```

### RAG 配置

```python
from llm_agent_demo import RAGConfig

# 創建 RAG 配置
rag_config = RAGConfig(
    chunk_size=1000,
    chunk_overlap=200,
    top_k=5,
    score_threshold=0.7,
    embedding_model="text-embedding-3-small",
)

# 轉換為字典
config_dict = rag_config.to_dict()
print(config_dict)
```

### 系統提示詞模板

```python
from llm_agent_demo import SYSTEM_PROMPTS

# 使用預定義的系統提示詞
assistant_prompt = SYSTEM_PROMPTS["assistant"]
coder_prompt = SYSTEM_PROMPTS["coder"]
analyst_prompt = SYSTEM_PROMPTS["analyst"]
translator_prompt = SYSTEM_PROMPTS["translator"]

# RAG 問答提示詞（需要格式化）
qa_prompt = SYSTEM_PROMPTS["qa_rag"]
formatted_prompt = qa_prompt.format(
    context="這裡是上下文信息...",
    question="用戶的問題是什麼？",
)
```

---

## 模組結構

### 主模組導出 (llm_agent_demo)

```python
from llm_agent_demo import (
    # 版本信息
    __version__,
    __author__,
    __license__,

    # 配置管理
    Settings,
    get_settings,
    reload_settings,
    get_openai_config,
    get_anthropic_config,
    get_google_config,
    get_groq_config,

    # 日誌管理
    get_logger,
    setup_logging,
    get_app_logger,

    # 成本追蹤
    CostTracker,
    TokenCounter,
    TokenUsage,

    # 重試機制
    retry_with_exponential_backoff,
    retry_on_rate_limit,
    retry_on_network_error,
    RetryContext,

    # 驗證器
    validate_api_key,
    validate_openai_api_key,
    validate_anthropic_api_key,
    validate_model_name,
    validate_temperature,
    validate_max_tokens,
    validate_user_query,
    sanitize_user_input,
    ValidationError,

    # LangChain 工具
    create_chat_model,
    create_embeddings,
    create_vector_store,
    RAGConfig,
    SYSTEM_PROMPTS,
)
```

### Utils 模組導出 (llm_agent_demo.utils)

```python
from llm_agent_demo.utils import (
    # 完整的工具集，包含所有輔助函數
    # 44 個導出項目
)
```

### 框架模組

```python
# 這些模組目前為空，但有完整的文檔說明
from llm_agent_demo import autogen
from llm_agent_demo import crewai
from llm_agent_demo import langchain
from llm_agent_demo import llamaindex
from llm_agent_demo import metagpt
```

---

## 完整示例

### 完整的 LangChain RAG 應用

```python
from llm_agent_demo import (
    get_settings,
    get_logger,
    setup_logging,
    CostTracker,
    create_chat_model,
    create_embeddings,
    create_vector_store,
    RAGConfig,
    SYSTEM_PROMPTS,
)

# 1. 設置日誌
setup_logging(level="INFO", colorize=True)
logger = get_logger(__name__)

# 2. 獲取配置
settings = get_settings()
logger.info(f"使用模型: {settings.openai_model}")

# 3. 創建成本追蹤器
tracker = CostTracker(save_path="usage.json")

# 4. 創建 RAG 配置
rag_config = RAGConfig(
    chunk_size=1000,
    chunk_overlap=200,
    top_k=5,
)

# 5. 創建嵌入模型和向量存儲
embeddings = create_embeddings(provider="openai")
vectorstore = create_vector_store(
    store_type="chroma",
    embeddings=embeddings,
    persist_directory="./chroma_db",
)

# 6. 添加文檔
documents = ["文檔1內容...", "文檔2內容..."]
vectorstore.add_texts(documents)
logger.info(f"添加了 {len(documents)} 個文檔")

# 7. 創建 LLM
llm = create_chat_model(provider="openai", model="gpt-4o-mini")

# 8. 執行查詢
query = "這些文檔的主要內容是什麼？"
docs = vectorstore.similarity_search(query, k=rag_config.top_k)

# 9. 構建提示詞
context = "\n\n".join([doc.page_content for doc in docs])
prompt = SYSTEM_PROMPTS["qa_rag"].format(context=context, question=query)

# 10. 調用 LLM
response = llm.invoke(prompt)
logger.info(f"LLM 回答: {response.content}")

# 11. 追蹤成本（假設從 response 中獲取 token 使用量）
# tracker.track_usage(...)

# 12. 打印成本摘要
tracker.print_summary()
```

---

## 最佳實踐

### 1. 使用配置單例

```python
# ✓ 推薦
from llm_agent_demo import get_settings
settings = get_settings()

# ✗ 不推薦
from llm_agent_demo import Settings
settings = Settings()  # 會創建新實例
```

### 2. 錯誤處理

```python
from llm_agent_demo import validate_api_key, ValidationError

try:
    api_key = validate_api_key(user_input, "OpenAI")
except ValidationError as e:
    logger.error(f"驗證失敗: {e}")
    # 處理錯誤
```

### 3. 成本追蹤

```python
# 始終使用成本追蹤器來監控 API 使用
tracker = CostTracker(save_path="usage.json")
# ... API 調用 ...
tracker.print_summary()
```

### 4. 日誌級別

```python
# 開發環境：DEBUG
setup_logging(level="DEBUG", colorize=True)

# 生產環境：INFO + JSON
setup_logging(level="INFO", json_format=True, log_file="app.json")
```

---

## 更新日誌

### v2.0.0 (優化版本)

**主要改進：**

1. ✅ **優化主模組導出**：從 7 個增加到 34 個常用工具
2. ✅ **完善 utils 模組**：導出 44 個實用函數
3. ✅ **添加 LangChain 工具**：直接從主模組訪問
4. ✅ **改進文檔**：為所有框架模組添加詳細說明
5. ✅ **無循環依賴**：所有模組通過導入測試
6. ✅ **清晰的 API 結構**：分類組織，易於使用

**優化細節：**

- 配置管理：7 個函數
- 日誌系統：3 個主要函數 + 多個專用記錄器
- 成本追蹤：3 個類 + 價格表
- 重試機制：4 個工具（裝飾器 + 上下文管理器）
- 驗證器：9 個主要驗證函數 + 安全工具
- LangChain：5 個便捷函數 + 配置類

---

## 問題反饋

如有問題或建議，請聯繫：markl-a

**項目版本：** v2.0.0
**最後更新：** 2025-01-15
