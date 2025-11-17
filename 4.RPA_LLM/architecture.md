# RPA + LLM 系統架構設計指南

## 目錄

1. [架構概覽](#架構概覽)
2. [核心組件](#核心組件)
3. [架構模式](#架構模式)
4. [資料流設計](#資料流設計)
5. [可擴展性設計](#可擴展性設計)
6. [安全架構](#安全架構)
7. [監控與維護](#監控與維護)
8. [實際案例](#實際案例)

---

## 架構概覽

### 整體架構圖

```
┌─────────────────────────────────────────────────────────────────┐
│                         使用者介面層                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Web UI   │  │ CLI      │  │ API      │  │ Scheduler│       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         編排層 (Orchestration)                   │
│  ┌────────────────────────────────────────────────────┐         │
│  │  Task Manager                                      │         │
│  │  - 任務調度   - 狀態管理   - 錯誤處理              │         │
│  └────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         決策層 (LLM Layer)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ LLM      │  │ Prompt   │  │ RAG      │  │ Memory   │       │
│  │ Service  │  │ Manager  │  │ Engine   │  │ Store    │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         執行層 (Execution Layer)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Web      │  │ Desktop  │  │ Data     │  │ API      │       │
│  │ Automation│ │ Automation│ │ Processing│ │ Integration│      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         資料層 (Data Layer)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Database │  │ File     │  │ Cache    │  │ Vector   │       │
│  │          │  │ Storage  │  │ (Redis)  │  │ DB       │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    基礎設施層 (Infrastructure)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Logging  │  │ Monitoring│ │ Security │  │ Container│       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 核心組件

### 1. 使用者介面層

#### Web UI
**職責**：提供視覺化的工作流編輯與監控介面

**技術選擇**：
- React + TypeScript（前端框架）
- Material-UI 或 Ant Design（UI 組件庫）
- Redux 或 Zustand（狀態管理）

**核心功能**：
```typescript
// 工作流設計器範例
interface WorkflowNode {
  id: string;
  type: 'action' | 'decision' | 'llm' | 'condition';
  config: NodeConfig;
  connections: Connection[];
}

interface WorkflowDesigner {
  nodes: WorkflowNode[];
  edges: Edge[];
  addNode(node: WorkflowNode): void;
  removeNode(id: string): void;
  execute(): Promise<WorkflowResult>;
}
```

#### CLI
**職責**：命令列介面，適合腳本化與自動化部署

**範例**：
```bash
# 執行工作流
rpa-cli run --workflow invoice-processing

# 監控任務狀態
rpa-cli status --task-id 12345

# 部署新工作流
rpa-cli deploy --config workflow.yaml
```

#### API Gateway
**職責**：對外提供 RESTful API，支援第三方整合

**設計原則**：
```python
# FastAPI 範例
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class WorkflowRequest(BaseModel):
    workflow_id: str
    parameters: dict

@app.post("/api/v1/workflows/execute")
async def execute_workflow(request: WorkflowRequest):
    """執行指定的工作流程"""
    try:
        result = await orchestrator.run(
            workflow_id=request.workflow_id,
            params=request.parameters
        )
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### 2. 編排層 (Orchestration)

#### Task Manager
**職責**：任務調度、狀態管理、錯誤處理

**架構設計**：
```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
import asyncio

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRY = "retry"

@dataclass
class Task:
    id: str
    workflow_id: str
    status: TaskStatus
    retries: int = 0
    max_retries: int = 3

class TaskOrchestrator:
    def __init__(self):
        self.tasks: dict[str, Task] = {}
        self.queue: asyncio.Queue = asyncio.Queue()

    async def submit_task(self, task: Task):
        """提交新任務"""
        self.tasks[task.id] = task
        await self.queue.put(task)

    async def process_tasks(self, workers: int = 5):
        """並發處理任務"""
        workers_list = [
            asyncio.create_task(self._worker())
            for _ in range(workers)
        ]
        await asyncio.gather(*workers_list)

    async def _worker(self):
        """工作線程"""
        while True:
            task = await self.queue.get()
            try:
                await self._execute_task(task)
                task.status = TaskStatus.SUCCESS
            except Exception as e:
                await self._handle_error(task, e)
            finally:
                self.queue.task_done()

    async def _handle_error(self, task: Task, error: Exception):
        """錯誤處理與重試邏輯"""
        if task.retries < task.max_retries:
            task.retries += 1
            task.status = TaskStatus.RETRY
            await asyncio.sleep(2 ** task.retries)  # 指數退避
            await self.queue.put(task)
        else:
            task.status = TaskStatus.FAILED
            await self._notify_failure(task, error)
```

---

### 3. 決策層 (LLM Layer)

#### LLM Service
**職責**：提供統一的 LLM 呼叫介面，支援多種模型

**設計模式**：策略模式 + 工廠模式

```python
from abc import ABC, abstractmethod
from typing import Optional

class LLMProvider(ABC):
    """LLM 提供者抽象基類"""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """生成回應"""
        pass

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """生成嵌入向量"""
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str, **kwargs) -> str:
        # OpenAI API 呼叫實作
        import openai
        openai.api_key = self.api_key
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return response.choices[0].message.content

class ClaudeProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-3-sonnet"):
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str, **kwargs) -> str:
        # Anthropic Claude API 呼叫實作
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=self.api_key)
        response = await client.messages.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return response.content[0].text

class LocalLLMProvider(LLMProvider):
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    async def generate(self, prompt: str, **kwargs) -> str:
        # 本地 LLM 服務呼叫（如 Ollama）
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.endpoint}/api/generate",
                json={"prompt": prompt, **kwargs}
            ) as response:
                result = await response.json()
                return result["response"]

class LLMFactory:
    """LLM 工廠類"""

    _providers = {
        "openai": OpenAIProvider,
        "claude": ClaudeProvider,
        "local": LocalLLMProvider,
    }

    @classmethod
    def create(cls, provider_type: str, **kwargs) -> LLMProvider:
        provider_class = cls._providers.get(provider_type)
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider_type}")
        return provider_class(**kwargs)

# 使用範例
llm = LLMFactory.create("openai", api_key="sk-...", model="gpt-4")
response = await llm.generate("Extract invoice details from this text...")
```

#### Prompt Manager
**職責**：管理 Prompt 模板、版本控制、A/B 測試

```python
from jinja2 import Template
from typing import Dict

class PromptTemplate:
    def __init__(self, template: str, version: str = "v1"):
        self.template = Template(template)
        self.version = version

    def render(self, **kwargs) -> str:
        return self.template.render(**kwargs)

class PromptManager:
    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}

    def register(self, name: str, template: str, version: str = "v1"):
        """註冊新的 Prompt 模板"""
        self.templates[f"{name}:{version}"] = PromptTemplate(template, version)

    def get(self, name: str, version: str = "latest") -> PromptTemplate:
        """獲取 Prompt 模板"""
        key = f"{name}:{version}"
        if key not in self.templates:
            # 如果是 latest，找最新版本
            available = [k for k in self.templates.keys() if k.startswith(f"{name}:")]
            if available:
                key = sorted(available)[-1]
        return self.templates.get(key)

# 使用範例
pm = PromptManager()

# 註冊數據提取模板
pm.register(
    "extract_invoice",
    """
    Extract the following information from this invoice:
    - Invoice Number
    - Date
    - Total Amount
    - Vendor Name

    Invoice Text:
    {{ invoice_text }}

    Return the result in JSON format.
    """,
    version="v1"
)

# 使用模板
template = pm.get("extract_invoice")
prompt = template.render(invoice_text="Invoice #12345...")
```

#### RAG Engine
**職責**：檢索增強生成，整合知識庫

```python
from typing import List
import chromadb

class RAGEngine:
    def __init__(self, collection_name: str = "knowledge_base"):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def add_documents(self, documents: List[str], metadatas: List[dict] = None):
        """添加文檔到知識庫"""
        ids = [f"doc_{i}" for i in range(len(documents))]
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def search(self, query: str, top_k: int = 5) -> List[str]:
        """檢索相關文檔"""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        return results['documents'][0]

    async def augmented_generate(self, query: str, llm: LLMProvider) -> str:
        """RAG 增強生成"""
        # 1. 檢索相關文檔
        relevant_docs = self.search(query, top_k=3)

        # 2. 構建增強 Prompt
        context = "\n\n".join(relevant_docs)
        augmented_prompt = f"""
        Based on the following context, answer the question:

        Context:
        {context}

        Question: {query}

        Answer:
        """

        # 3. 生成回應
        response = await llm.generate(augmented_prompt)
        return response
```

---

### 4. 執行層 (Execution Layer)

#### Web Automation
**職責**：瀏覽器自動化

```python
from playwright.async_api import async_playwright, Page
from typing import Optional

class WebAutomation:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser = None
        self.page: Optional[Page] = None

    async def initialize(self):
        """初始化瀏覽器"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        self.page = await self.browser.new_page()

    async def navigate(self, url: str):
        """導航到指定 URL"""
        await self.page.goto(url)

    async def extract_with_llm(self, instruction: str, llm: LLMProvider) -> dict:
        """使用 LLM 提取頁面資訊"""
        # 1. 獲取頁面內容
        content = await self.page.content()

        # 2. 構建 Prompt
        prompt = f"""
        Extract information from this HTML based on the instruction:

        Instruction: {instruction}

        HTML:
        {content[:5000]}  # 限制長度

        Return JSON format.
        """

        # 3. 使用 LLM 提取
        result = await llm.generate(prompt)
        return json.loads(result)

    async def close(self):
        """關閉瀏覽器"""
        if self.browser:
            await self.browser.close()
```

#### Data Processing
**職責**：資料處理與轉換

```python
import pandas as pd
from typing import Any, Dict

class DataProcessor:
    @staticmethod
    async def process_csv(file_path: str, llm: LLMProvider) -> pd.DataFrame:
        """處理 CSV 文件"""
        df = pd.read_csv(file_path)

        # 使用 LLM 進行數據清洗與標準化
        # ...

        return df

    @staticmethod
    async def extract_from_pdf(file_path: str, llm: LLMProvider) -> Dict[str, Any]:
        """從 PDF 提取結構化數據"""
        import pdfplumber

        with pdfplumber.open(file_path) as pdf:
            text = "\n".join([page.extract_text() for page in pdf.pages])

        # 使用 LLM 提取關鍵資訊
        prompt = f"""
        Extract structured data from this document:

        {text[:3000]}

        Return as JSON.
        """

        result = await llm.generate(prompt)
        return json.loads(result)
```

---

## 架構模式

### 模式 1：事件驅動架構

**適用場景**：需要處理大量異步事件的系統

```python
from typing import Callable, List
import asyncio

class Event:
    def __init__(self, type: str, data: dict):
        self.type = type
        self.data = data

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable):
        """訂閱事件"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    async def publish(self, event: Event):
        """發布事件"""
        handlers = self.subscribers.get(event.type, [])
        await asyncio.gather(*[handler(event) for handler in handlers])

# 使用範例
event_bus = EventBus()

async def handle_task_completed(event: Event):
    print(f"Task {event.data['task_id']} completed")
    # 發送通知、更新資料庫等

event_bus.subscribe("task.completed", handle_task_completed)
await event_bus.publish(Event("task.completed", {"task_id": "123"}))
```

### 模式 2：責任鏈模式

**適用場景**：需要依序處理多個步驟的工作流

```python
from abc import ABC, abstractmethod

class Handler(ABC):
    def __init__(self):
        self.next_handler: Optional[Handler] = None

    def set_next(self, handler: 'Handler'):
        self.next_handler = handler
        return handler

    @abstractmethod
    async def handle(self, context: dict) -> dict:
        pass

    async def process(self, context: dict) -> dict:
        result = await self.handle(context)
        if self.next_handler:
            return await self.next_handler.process(result)
        return result

class ValidationHandler(Handler):
    async def handle(self, context: dict) -> dict:
        # 驗證輸入數據
        if not context.get("data"):
            raise ValueError("Missing data")
        return context

class LLMProcessingHandler(Handler):
    def __init__(self, llm: LLMProvider):
        super().__init__()
        self.llm = llm

    async def handle(self, context: dict) -> dict:
        # LLM 處理
        result = await self.llm.generate(context["data"])
        context["llm_result"] = result
        return context

class SaveResultHandler(Handler):
    async def handle(self, context: dict) -> dict:
        # 保存結果
        # await db.save(context["llm_result"])
        return context

# 構建處理鏈
validation = ValidationHandler()
llm_processing = LLMProcessingHandler(llm)
save_result = SaveResultHandler()

validation.set_next(llm_processing).set_next(save_result)

# 執行
result = await validation.process({"data": "..."})
```

---

## 資料流設計

### 資料流圖

```
輸入數據 → 驗證 → 預處理 → LLM 處理 → 後處理 → 輸出
   ↓         ↓        ↓          ↓          ↓        ↓
 日誌記錄   快取    向量化     Prompt     解析     儲存
```

### 資料管理策略

```python
import redis
import json
from typing import Optional

class DataManager:
    def __init__(self, redis_url: str = "redis://localhost"):
        self.redis = redis.from_url(redis_url)
        self.ttl = 3600  # 1 小時

    def cache_set(self, key: str, value: dict, ttl: Optional[int] = None):
        """設置快取"""
        self.redis.setex(
            key,
            ttl or self.ttl,
            json.dumps(value)
        )

    def cache_get(self, key: str) -> Optional[dict]:
        """獲取快取"""
        value = self.redis.get(key)
        return json.loads(value) if value else None

    async def get_or_compute(self, key: str, compute_fn: Callable) -> dict:
        """獲取快取或計算"""
        cached = self.cache_get(key)
        if cached:
            return cached

        result = await compute_fn()
        self.cache_set(key, result)
        return result
```

---

## 可擴展性設計

### 水平擴展

使用分佈式任務隊列（Celery + Redis）

```python
from celery import Celery

app = Celery('rpa_tasks', broker='redis://localhost:6379/0')

@app.task
async def process_document(doc_id: str):
    """處理文檔任務"""
    # 任務邏輯
    pass

# 提交任務
task = process_document.delay("doc_123")
```

### 垂直擴展

優化單機效能：
- 使用異步 I/O（asyncio）
- 批次處理請求
- 連接池管理

```python
import asyncio
from typing import List

class BatchProcessor:
    def __init__(self, batch_size: int = 10, max_wait: float = 1.0):
        self.batch_size = batch_size
        self.max_wait = max_wait
        self.queue: List = []

    async def add(self, item):
        """添加項目到批次"""
        self.queue.append(item)

        if len(self.queue) >= self.batch_size:
            await self.process_batch()

    async def process_batch(self):
        """批次處理"""
        if not self.queue:
            return

        batch = self.queue[:self.batch_size]
        self.queue = self.queue[self.batch_size:]

        # 批次調用 LLM
        await self.llm.batch_generate(batch)
```

---

## 安全架構

### 認證與授權

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """驗證 JWT Token"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
```

### 敏感資料保護

```python
from cryptography.fernet import Fernet

class SecretManager:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)

    def encrypt(self, data: str) -> str:
        """加密"""
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted: str) -> str:
        """解密"""
        return self.cipher.decrypt(encrypted.encode()).decode()
```

---

## 監控與維護

### 日誌系統

```python
import logging
import structlog

# 結構化日誌
logger = structlog.get_logger()

async def execute_task(task_id: str):
    logger.info("task_started", task_id=task_id)
    try:
        # 執行任務
        result = await perform_task()
        logger.info("task_completed", task_id=task_id, result=result)
    except Exception as e:
        logger.error("task_failed", task_id=task_id, error=str(e))
        raise
```

### 性能監控

```python
from prometheus_client import Counter, Histogram
import time

# 定義指標
task_counter = Counter('rpa_tasks_total', 'Total tasks processed')
task_duration = Histogram('rpa_task_duration_seconds', 'Task duration')

async def monitored_task():
    task_counter.inc()

    with task_duration.time():
        # 執行任務
        await perform_task()
```

---

## 實際案例

### 案例：智能發票處理系統

完整架構實現請參考 [use-cases.md](./use-cases.md#發票處理系統)

```python
# 簡化版本示例
class InvoiceProcessingWorkflow:
    def __init__(self, llm: LLMProvider, rag: RAGEngine):
        self.llm = llm
        self.rag = rag

    async def process(self, invoice_path: str) -> dict:
        # 1. 提取文本
        text = await self.extract_text(invoice_path)

        # 2. RAG 增強理解
        context = await self.rag.search(text)

        # 3. LLM 提取結構化數據
        structured_data = await self.llm.generate(
            f"Extract invoice data:\n{text}\nContext:\n{context}"
        )

        # 4. 驗證與保存
        validated = await self.validate(structured_data)
        await self.save(validated)

        return validated
```

---

## 總結

本架構設計指南提供了構建生產級 RPA + LLM 系統的完整藍圖。關鍵要點：

1. **分層架構**：清晰的職責劃分，易於維護和擴展
2. **模組化設計**：可插拔的組件，支援靈活配置
3. **可擴展性**：支援水平和垂直擴展
4. **安全性**：完善的認證、授權和數據保護
5. **可觀測性**：全面的日誌、監控和追蹤

接下來建議閱讀：
- [tutorial-part1-basic-rpa.md](./tutorial-part1-basic-rpa.md) - 開始實作
- [best-practices.md](./best-practices.md) - 學習最佳實踐
- [use-cases.md](./use-cases.md) - 查看實際應用案例
