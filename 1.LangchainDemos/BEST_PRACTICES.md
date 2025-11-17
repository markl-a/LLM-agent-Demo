# LangChain 最佳實踐指南

## 目錄
- [Prompt Engineering](#prompt-engineering)
- [RAG 系統優化](#rag-系統優化)
- [Agent 設計模式](#agent-設計模式)
- [效能優化](#效能優化)
- [錯誤處理](#錯誤處理)
- [安全性考量](#安全性考量)
- [監控與除錯](#監控與除錯)
- [成本控制](#成本控制)

---

## Prompt Engineering

### 1. 結構化 Prompt 設計

```python
# ✅ 好的做法：清晰的結構和角色定義
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一個專業的資料分析師。

工作原則：
1. 基於事實和數據進行分析
2. 提供可執行的建議
3. 承認不確定性

輸出格式：
- 使用 Markdown
- 關鍵點使用項目符號
- 包含數據來源
"""),
    ("user", "{input}")
])

# ❌ 避免：模糊的指示
bad_prompt = "分析這些數據並給我一些建議"
```

### 2. Few-Shot Learning

```python
# ✅ 提供範例以改善輸出品質
prompt = ChatPromptTemplate.from_messages([
    ("system", "將問題分類為技術、銷售或客服。"),
    ("user", "我的產品無法啟動"),
    ("assistant", "分類：技術"),
    ("user", "我想了解定價方案"),
    ("assistant", "分類：銷售"),
    ("user", "{input}")
])
```

### 3. Chain of Thought (CoT)

```python
# ✅ 引導模型逐步思考
prompt = """問題：{question}

請按照以下步驟解決：
1. 理解問題
2. 列出相關資訊
3. 推理過程
4. 得出結論

讓我們一步一步來："""
```

---

## RAG 系統優化

### 1. 文檔分割策略

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# ✅ 根據內容類型選擇適當的參數
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # 適中的區塊大小
    chunk_overlap=200,      # 20% 重疊以保持上下文
    length_function=len,
    separators=[
        "\n\n",    # 段落分隔優先
        "\n",      # 行分隔
        "。",      # 中文句子
        ". ",      # 英文句子
        " ",       # 空格
        ""         # 字元
    ]
)

# ❌ 避免：過小或過大的區塊
bad_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,   # 太小，失去上下文
    chunk_overlap=0    # 無重疊，可能遺漏資訊
)
```

### 2. 檢索優化

```python
# ✅ 多查詢檢索
from langchain.retrievers import MultiQueryRetriever

retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(),
    llm=llm
)

# ✅ 上下文壓縮
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

compressor = LLMChainExtractor.from_llm(llm)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vectorstore.as_retriever()
)

# ✅ 混合搜尋（語義 + 關鍵詞）
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

bm25_retriever = BM25Retriever.from_documents(documents)
ensemble_retriever = EnsembleRetriever(
    retrievers=[vectorstore.as_retriever(), bm25_retriever],
    weights=[0.7, 0.3]  # 70% 語義，30% 關鍵詞
)
```

### 3. Embedding 模型選擇

```python
# ✅ 根據需求選擇模型
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

# 選擇 1：商業模型（高品質）
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

# 選擇 2：開源模型（成本優化）
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    model_kwargs={'device': 'cuda'}  # 使用 GPU
)

# 選擇 3：中文優化
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-large-zh-v1.5"
)
```

---

## Agent 設計模式

### 1. ReAct Pattern

```python
# ✅ 清晰的思考-行動-觀察循環
agent_prompt = """回答以下問題，你可以使用這些工具：
{tools}

使用以下格式：

問題：輸入問題
思考：我需要做什麼
行動：要使用的工具
行動輸入：工具的輸入
觀察：工具返回的結果
... (重複思考/行動/觀察 N 次)
思考：我現在知道最終答案了
最終答案：對原始問題的答案

問題：{input}
{agent_scratchpad}"""
```

### 2. 工具定義最佳實踐

```python
from langchain.tools import tool

# ✅ 清晰的名稱、描述和參數
@tool
def search_database(query: str, limit: int = 5) -> str:
    """在產品資料庫中搜尋相關資訊。

    Args:
        query: 搜尋關鍵詞
        limit: 返回結果數量，預設為 5

    Returns:
        格式化的搜尋結果

    Examples:
        search_database("筆記型電腦", limit=3)
    """
    # 實現...
    pass

# ❌ 避免：模糊的描述
@tool
def search(q: str) -> str:
    """搜尋"""  # 太簡略
    pass
```

### 3. 狀態管理

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

# ✅ 明確的狀態定義
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    current_step: str
    iteration_count: int
    max_iterations: int

# ✅ 添加循環控制
def should_continue(state: AgentState) -> bool:
    if state["iteration_count"] >= state["max_iterations"]:
        return False
    # 其他條件...
    return True
```

---

## 效能優化

### 1. 批次處理

```python
# ✅ 批次處理多個請求
from langchain.chains import LLMChain

# 單個處理（慢）
results = [chain.invoke({"input": q}) for q in questions]

# 批次處理（快）
results = chain.batch([{"input": q} for q in questions])
```

### 2. 快取機制

```python
from langchain.cache import SQLiteCache
from langchain.globals import set_llm_cache

# ✅ 啟用快取
set_llm_cache(SQLiteCache(database_path=".langchain.db"))

# ✅ 快取向量搜尋結果
from langchain_community.vectorstores import Chroma

db = Chroma(
    persist_directory="./chroma_db",  # 持久化
    embedding_function=embeddings
)
```

### 3. 異步處理

```python
import asyncio

# ✅ 使用異步提高並發
async def process_documents(docs):
    tasks = [chain.ainvoke({"input": doc}) for doc in docs]
    results = await asyncio.gather(*tasks)
    return results

# 執行
results = asyncio.run(process_documents(documents))
```

---

## 錯誤處理

### 1. 重試機制

```python
from tenacity import retry, stop_after_attempt, wait_exponential

# ✅ 自動重試
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def call_llm(prompt):
    return llm.invoke(prompt)
```

### 2. 降級策略

```python
# ✅ 提供備用方案
def get_answer(question):
    try:
        # 嘗試使用 RAG
        return rag_chain.invoke({"question": question})
    except Exception as e:
        logger.error(f"RAG 失敗: {e}")
        try:
            # 降級到直接 LLM
            return llm.invoke(question)
        except Exception as e:
            logger.error(f"LLM 失敗: {e}")
            # 返回預設回應
            return "抱歉，系統暫時無法處理您的請求。"
```

### 3. 輸入驗證

```python
# ✅ 驗證和清理輸入
def validate_input(user_input: str) -> str:
    # 長度限制
    if len(user_input) > 1000:
        raise ValueError("輸入過長")

    # 過濾敏感詞
    forbidden_words = ["DROP", "DELETE", "EXEC"]
    if any(word in user_input.upper() for word in forbidden_words):
        raise ValueError("包含禁止的關鍵詞")

    # 清理特殊字元
    return user_input.strip()
```

---

## 安全性考量

### 1. API Key 管理

```python
# ✅ 使用環境變數
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# ❌ 避免：硬編碼
api_key = "sk-xxxxx"  # 危險！
```

### 2. Prompt Injection 防護

```python
# ✅ 分離系統指令和用戶輸入
prompt = ChatPromptTemplate.from_messages([
    ("system", system_instructions),  # 系統控制
    ("user", "{user_input}")           # 用戶輸入隔離
])

# ✅ 輸入過濾
def sanitize_input(text: str) -> str:
    # 移除潛在的注入指令
    dangerous_patterns = [
        r"ignore previous instructions",
        r"new instructions:",
        r"system:",
    ]
    # 實現過濾邏輯...
    return cleaned_text
```

### 3. 輸出驗證

```python
# ✅ 驗證模型輸出
def validate_output(output: str) -> bool:
    # 檢查是否包含敏感資訊
    if contains_pii(output):
        return False

    # 檢查格式是否正確
    if not is_valid_format(output):
        return False

    return True
```

---

## 監控與除錯

### 1. LangSmith 追蹤

```python
import os

# ✅ 啟用追蹤
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-key"
os.environ["LANGCHAIN_PROJECT"] = "my-project"

# ✅ 添加元數據
from langsmith import traceable

@traceable(
    run_type="chain",
    metadata={"version": "1.0", "environment": "production"}
)
def my_chain(input_text):
    return chain.invoke({"input": input_text})
```

### 2. 日誌記錄

```python
import logging

# ✅ 配置詳細日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 使用
logger.info(f"處理查詢: {query}")
logger.error(f"錯誤: {error}")
```

### 3. Token 使用追蹤

```python
from langchain.callbacks import get_openai_callback

# ✅ 追蹤成本
with get_openai_callback() as cb:
    result = chain.invoke({"input": query})
    print(f"Tokens: {cb.total_tokens}")
    print(f"Cost: ${cb.total_cost}")
```

---

## 成本控制

### 1. 模型選擇策略

```python
# ✅ 根據任務選擇適當的模型
def get_llm_for_task(task_complexity: str):
    if task_complexity == "simple":
        return ChatOpenAI(model="gpt-3.5-turbo")
    elif task_complexity == "medium":
        return ChatOpenAI(model="gpt-4o-mini")
    else:
        return ChatOpenAI(model="gpt-4")
```

### 2. Token 優化

```python
# ✅ 限制輸出長度
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    max_tokens=500  # 限制回應長度
)

# ✅ 壓縮上下文
from langchain.chains.summarize import load_summarize_chain

# 如果上下文太長，先摘要
if len(context) > 2000:
    summarize_chain = load_summarize_chain(llm, chain_type="stuff")
    context = summarize_chain.run(context)
```

### 3. 使用配額管理

```python
# ✅ 實施 Rate Limiting
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=50, period=60)  # 每分鐘最多 50 次
def call_api(query):
    return llm.invoke(query)
```

---

## 測試最佳實踐

### 1. 單元測試

```python
import pytest

def test_chain_output():
    # ✅ 測試鏈的輸出
    result = chain.invoke({"input": "test"})
    assert result is not None
    assert len(result) > 0

def test_prompt_template():
    # ✅ 測試提示模板
    prompt = template.format(input="test")
    assert "test" in prompt
```

### 2. 評估指標

```python
# ✅ 使用評估工具
from langchain.evaluation import load_evaluator

evaluator = load_evaluator("qa")
result = evaluator.evaluate_strings(
    prediction="模型回答",
    reference="正確答案",
    input="問題"
)
```

---

## 總結

### 關鍵原則

1. **明確性**: 清晰的 Prompt 和文檔
2. **魯棒性**: 完善的錯誤處理
3. **效能**: 合理的快取和批次處理
4. **安全性**: 保護敏感資訊
5. **可觀測性**: 完整的日誌和追蹤
6. **成本意識**: 優化 Token 使用

### 持續改進

- 定期審查和優化 Prompts
- 監控效能指標
- 收集用戶反饋
- 更新最佳實踐

---

**參考資源**

- [LangChain 官方文檔](https://python.langchain.com/)
- [LangSmith 最佳實踐](https://docs.smith.langchain.com/)
- [OpenAI 最佳實踐](https://platform.openai.com/docs/guides/production-best-practices)
