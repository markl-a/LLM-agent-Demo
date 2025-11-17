# 🏗️ 系統架構說明

本文檔深入解析銷售外展自動化系統的架構設計、工作流程和技術實現。

## 📋 目錄

- [架構概覽](#架構概覽)
- [LangGraph 工作流](#langgraph-工作流)
- [核心組件](#核心組件)
- [數據流程](#數據流程)
- [狀態管理](#狀態管理)
- [Agent 設計](#agent-設計)
- [錯誤處理機制](#錯誤處理機制)
- [性能優化](#性能優化)

---

## 架構概覽

### 系統層次結構

```
┌─────────────────────────────────────────────────────────────┐
│                      應用層 (Application)                     │
│                         main.py                              │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   編排層 (Orchestration)                      │
│                    LangGraph State Machine                   │
│    ┌──────────┬──────────┬──────────┬──────────┐            │
│    │  Init    │ Research │ Generate │  Send    │            │
│    │  Node    │   Node   │   Node   │  Node    │            │
│    └──────────┴──────────┴──────────┴──────────┘            │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agent 層 (Agents)                         │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │  Data    │   LLM    │  Email   │   CRM    │  Search  │  │
│  │  Agent   │  Agent   │  Agent   │  Agent   │  Agent   │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    整合層 (Integration)                       │
│  ┌────────┬─────────┬─────────┬──────────┬──────────┐      │
│  │LinkedIn│  Gemini │  Gmail  │ Airtable │  Serper  │      │
│  │  API   │ /OpenAI │   API   │ HubSpot  │   API    │      │
│  └────────┴─────────┴─────────┴──────────┴──────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 設計原則

1. **模組化設計**：每個組件職責單一，易於維護和擴展
2. **狀態驅動**：使用 LangGraph 的狀態機管理複雜流程
3. **鬆耦合**：Agent 之間通過狀態傳遞通信，不直接依賴
4. **可觀察性**：完整的日誌和監控機制
5. **容錯性**：多層次的錯誤處理和重試機制

---

## LangGraph 工作流

### 什麼是 LangGraph？

LangGraph 是 LangChain 生態系統中用於構建狀態化、多步驟 AI 應用的框架。它基於圖的概念，允許定義：

- **節點（Nodes）**：執行特定任務的函數
- **邊（Edges）**：定義節點之間的轉換
- **狀態（State）**：在節點間傳遞的數據

### 工作流圖

```
                    ┌─────────┐
                    │  Start  │
                    └────┬────┘
                         │
                         ▼
                  ┌──────────────┐
                  │  Load Leads  │ ─────┐
                  │  from CRM    │      │ (No leads)
                  └──────┬───────┘      │
                         │              ▼
                         │         ┌─────────┐
                   (Has leads)     │   End   │
                         │         └─────────┘
                         ▼
              ┌────────────────────┐
              │  For each lead:    │
              │  ┌──────────────┐  │
              │  │ 1. Research  │  │
              │  └──────┬───────┘  │
              │         ▼          │
              │  ┌──────────────┐  │
              │  │ 2. Generate  │  │
              │  └──────┬───────┘  │
              │         ▼          │
              │  ┌──────────────┐  │
              │  │ 3. Send      │  │
              │  └──────┬───────┘  │
              │         ▼          │
              │  ┌──────────────┐  │
              │  │ 4. Update    │  │
              │  └──────────────┘  │
              └────────┬───────────┘
                       │
                       ▼
                  ┌─────────┐
                  │   End   │
                  └─────────┘
```

### 狀態定義

```python
from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    """Agent 工作流的狀態"""

    # 當前處理的潛在客戶
    current_lead: Optional[dict]

    # 所有待處理的潛在客戶列表
    leads: List[dict]

    # 研究階段收集的信息
    research_data: Optional[dict]

    # 生成的郵件內容
    email_content: Optional[str]

    # 發送狀態
    send_status: Optional[str]

    # 錯誤信息
    errors: List[str]

    # 處理進度
    processed_count: int
    total_count: int
```

### 節點實現示例

```python
def research_node(state: AgentState) -> AgentState:
    """
    研究節點：收集潛在客戶信息

    1. 從 LinkedIn 獲取職業背景
    2. 搜索公司相關信息
    3. 分析行業趨勢
    """
    lead = state["current_lead"]

    # LinkedIn 數據抓取
    linkedin_data = fetch_linkedin_profile(lead["linkedin_url"])

    # 公司信息搜索
    company_info = search_company_info(lead["company"])

    # 整合研究數據
    state["research_data"] = {
        "linkedin": linkedin_data,
        "company": company_info,
        "industry": extract_industry_insights(company_info)
    }

    return state


def generate_node(state: AgentState) -> AgentState:
    """
    生成節點：創建個性化郵件

    使用 LLM 基於研究數據生成郵件
    """
    lead = state["current_lead"]
    research = state["research_data"]

    # 構建 prompt
    prompt = build_email_prompt(lead, research)

    # 調用 LLM 生成郵件
    email = llm_generate_email(prompt)

    state["email_content"] = email

    return state


def send_node(state: AgentState) -> AgentState:
    """
    發送節點：通過 Gmail 發送郵件
    """
    lead = state["current_lead"]
    email = state["email_content"]

    try:
        # 發送郵件
        send_gmail(
            to=lead["email"],
            subject=f"Re: {lead['company']}",
            body=email
        )

        state["send_status"] = "sent"

    except Exception as e:
        state["send_status"] = "failed"
        state["errors"].append(str(e))

    return state
```

---

## 核心組件

### 1. Data Agent（數據代理）

**職責**：
- 從 CRM 系統讀取潛在客戶列表
- 驗證數據完整性
- 過濾已處理的客戶

**實現**：

```python
class DataAgent:
    def __init__(self, crm_client):
        self.crm = crm_client

    def fetch_leads(self, filters=None):
        """獲取潛在客戶列表"""
        # 從 CRM 讀取
        leads = self.crm.get_records(filters)

        # 數據驗證
        valid_leads = [
            lead for lead in leads
            if self.validate_lead(lead)
        ]

        return valid_leads

    def validate_lead(self, lead):
        """驗證客戶數據"""
        required_fields = ["name", "email", "company"]

        return all(
            field in lead and lead[field]
            for field in required_fields
        )
```

### 2. LLM Agent（語言模型代理）

**職責**：
- 生成個性化郵件內容
- 提取和總結研究信息
- 調整語調和風格

**實現**：

```python
class LLMAgent:
    def __init__(self, model_name="gemini-pro"):
        self.llm = ChatGoogleGenerativeAI(model=model_name)

    def generate_email(self, lead_info, research_data):
        """生成個性化郵件"""

        prompt_template = """
        你是一位專業的銷售專家。根據以下信息，
        撰寫一封個性化的銷售郵件。

        潛在客戶信息：
        姓名：{name}
        公司：{company}
        職位：{position}

        研究數據：
        {research}

        要求：
        1. 語氣專業但親切
        2. 突出你對客戶業務的了解
        3. 清晰說明產品/服務的價值
        4. 包含明確的行動呼籲（CTA）
        5. 控制在 150-200 字

        郵件內容：
        """

        prompt = prompt_template.format(
            name=lead_info["name"],
            company=lead_info["company"],
            position=lead_info.get("position", ""),
            research=self.format_research(research_data)
        )

        response = self.llm.invoke(prompt)
        return response.content

    def format_research(self, data):
        """格式化研究數據"""
        # 提取關鍵信息
        return f"""
        公司背景：{data['company'].get('description', 'N/A')}
        行業趨勢：{data['industry'].get('trends', 'N/A')}
        近期動態：{data['company'].get('recent_news', 'N/A')}
        """
```

### 3. Email Agent（郵件代理）

**職責**：
- 通過 Gmail API 發送郵件
- 處理郵件格式和編碼
- 追蹤發送狀態

**實現**：

```python
class EmailAgent:
    def __init__(self, credentials_path):
        self.service = self.authenticate_gmail(credentials_path)

    def authenticate_gmail(self, creds_path):
        """Gmail API 認證"""
        # OAuth 2.0 認證流程
        # ...
        return build('gmail', 'v1', credentials=creds)

    def send_email(self, to, subject, body, cc=None, bcc=None):
        """發送郵件"""
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject

        if cc:
            message['cc'] = cc
        if bcc:
            message['bcc'] = bcc

        raw = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode()

        try:
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()

            return {
                'status': 'success',
                'message_id': sent_message['id']
            }

        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
```

### 4. CRM Agent（CRM 代理）

**職責**：
- 與 CRM 系統（Airtable/HubSpot）交互
- 更新客戶狀態
- 記錄互動歷史

**實現（Airtable 為例）**：

```python
class AirtableCRMAgent:
    def __init__(self, access_token, base_id, table_name):
        self.api = Api(access_token)
        self.table = self.api.table(base_id, table_name)

    def get_leads(self, status_filter="pending"):
        """獲取潛在客戶"""
        formula = f"{{status}} = '{status_filter}'"
        records = self.table.all(formula=formula)

        return [
            {
                'id': record['id'],
                **record['fields']
            }
            for record in records
        ]

    def update_status(self, record_id, status, notes=None):
        """更新客戶狀態"""
        fields = {'status': status}

        if notes:
            fields['notes'] = notes

        self.table.update(record_id, fields)

    def log_interaction(self, record_id, interaction_type, details):
        """記錄互動"""
        # 添加互動記錄到歷史欄位
        # ...
```

### 5. Search Agent（搜索代理）

**職責**：
- 使用 Serper API 搜索公司信息
- 抓取 LinkedIn 數據
- 收集行業洞察

**實現**：

```python
class SearchAgent:
    def __init__(self, serper_key, rapidapi_key):
        self.serper = SerperAPI(api_key=serper_key)
        self.rapid = RapidAPI(api_key=rapidapi_key)

    def search_company(self, company_name):
        """搜索公司信息"""
        query = f"{company_name} company news products"

        results = self.serper.search(query)

        return {
            'description': results.get('knowledge_graph', {}).get('description'),
            'recent_news': results.get('news', [])[:3],
            'website': results.get('knowledge_graph', {}).get('website')
        }

    def get_linkedin_profile(self, linkedin_url):
        """獲取 LinkedIn 檔案"""
        # 調用 RapidAPI LinkedIn scraper
        endpoint = "linkedin-profile-scraper"

        response = self.rapid.get(
            endpoint,
            params={'url': linkedin_url}
        )

        return {
            'headline': response.get('headline'),
            'summary': response.get('summary'),
            'experience': response.get('experience', [])[:2]
        }
```

---

## 數據流程

### 完整數據流

```
1. 初始化
   ├── 加載環境變數
   ├── 初始化 API 客戶端
   └── 創建 LangGraph 工作流

2. 獲取潛在客戶
   ├── Data Agent 從 CRM 讀取
   ├── 過濾狀態為 "pending" 的客戶
   └── 驗證數據完整性

3. 對每個客戶執行循環
   │
   ├── 3.1 研究階段
   │   ├── Search Agent 搜索公司信息
   │   ├── Search Agent 獲取 LinkedIn 數據
   │   └── 整合研究數據到 state
   │
   ├── 3.2 生成階段
   │   ├── 構建包含研究數據的 prompt
   │   ├── LLM Agent 生成個性化郵件
   │   └── 驗證郵件內容質量
   │
   ├── 3.3 發送階段
   │   ├── Email Agent 發送郵件
   │   ├── 處理發送錯誤
   │   └── 記錄發送結果
   │
   └── 3.4 更新階段
       ├── CRM Agent 更新客戶狀態為 "sent"
       ├── 添加互動記錄
       └── 記錄時間戳

4. 完成
   ├── 生成執行報告
   ├── 輸出統計信息
   └── 清理資源
```

---

## 狀態管理

### 狀態轉換圖

```
┌─────────┐
│ PENDING │ ←── 初始狀態
└────┬────┘
     │
     │ research_node()
     ▼
┌─────────────┐
│ RESEARCHING │
└────┬────────┘
     │
     │ generate_node()
     ▼
┌────────────┐
│ GENERATING │
└────┬───────┘
     │
     │ send_node()
     ▼
┌─────────┐
│ SENDING │
└────┬────┘
     │
     ├─── 成功 ──→ ┌──────┐
     │            │ SENT │
     │            └──────┘
     │
     └─── 失敗 ──→ ┌────────┐
                  │ FAILED │
                  └────────┘
```

### 狀態持久化

```python
class StatePersistence:
    """狀態持久化管理"""

    def __init__(self, storage_path="state.json"):
        self.path = storage_path

    def save_state(self, state):
        """保存狀態到磁盤"""
        with open(self.path, 'w') as f:
            json.dump(state, f, indent=2)

    def load_state(self):
        """從磁盤加載狀態"""
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                return json.load(f)
        return None

    def clear_state(self):
        """清除狀態"""
        if os.path.exists(self.path):
            os.remove(self.path)
```

---

## Agent 設計

### Agent 通信模式

我們使用 **基於狀態的通信**，而非直接調用：

```python
# ✓ 好的做法：通過狀態傳遞
def research_node(state):
    # 讀取狀態
    lead = state["current_lead"]

    # 執行研究
    research_data = do_research(lead)

    # 更新狀態
    state["research_data"] = research_data
    return state

def generate_node(state):
    # 從狀態讀取研究結果
    research = state["research_data"]

    # 生成郵件
    email = generate_email(research)

    state["email_content"] = email
    return state


# ✗ 壞的做法：直接耦合
def generate_node(state):
    # 直接調用其他 agent
    research = ResearchAgent().research(state["lead"])  # 緊耦合！
    ...
```

### Agent 可組合性

通過組合不同的 Agent，可以構建更複雜的工作流：

```python
# 基礎工作流
basic_workflow = (
    START
    >> research_node
    >> generate_node
    >> send_node
    >> END
)

# 增強工作流（添加質量檢查）
enhanced_workflow = (
    START
    >> research_node
    >> generate_node
    >> quality_check_node  # 新增節點
    >> send_node
    >> END
)

# A/B 測試工作流（條件分支）
ab_test_workflow = (
    START
    >> research_node
    >> generate_node
    >> ab_split_node  # 分支決策
    >> [send_version_a, send_version_b]  # 並行發送
    >> merge_results_node
    >> END
)
```

---

## 錯誤處理機制

### 多層次錯誤處理

```python
# 1. API 層級錯誤處理
class APIClient:
    def request(self, endpoint, retries=3):
        for attempt in range(retries):
            try:
                response = requests.get(endpoint)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == retries - 1:
                    raise
                time.sleep(2 ** attempt)  # 指數退避

# 2. Agent 層級錯誤處理
def research_node(state):
    try:
        research_data = fetch_research(state["lead"])
        state["research_data"] = research_data
    except Exception as e:
        state["errors"].append(f"Research failed: {str(e)}")
        state["research_data"] = {}  # 降級處理
    return state

# 3. 工作流層級錯誤處理
class WorkflowExecutor:
    def run(self, state):
        try:
            result = self.graph.invoke(state)
            return result
        except Exception as e:
            self.log_error(e)
            self.notify_admin(e)
            # 保存部分進度
            self.save_partial_state(state)
            raise
```

### 降級策略

當某些服務不可用時，系統能夠降級運行：

```python
def research_node_with_fallback(state):
    """帶降級策略的研究節點"""

    lead = state["current_lead"]
    research = {}

    # 嘗試 LinkedIn 數據
    try:
        research["linkedin"] = fetch_linkedin(lead["linkedin_url"])
    except:
        logger.warning("LinkedIn fetch failed, using basic info")
        research["linkedin"] = {"name": lead["name"]}

    # 嘗試公司搜索
    try:
        research["company"] = search_company(lead["company"])
    except:
        logger.warning("Company search failed, skipping")
        research["company"] = {}

    # 即使部分失敗，仍然繼續
    state["research_data"] = research
    return state
```

---

## 性能優化

### 1. 並行處理

對於大量客戶，使用批次並行處理：

```python
from concurrent.futures import ThreadPoolExecutor

def process_leads_parallel(leads, max_workers=5):
    """並行處理多個客戶"""

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(process_single_lead, lead)
            for lead in leads
        ]

        results = [f.result() for f in futures]

    return results
```

### 2. 緩存機制

避免重複的 API 調用：

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def search_company_cached(company_name):
    """緩存公司搜索結果"""
    return search_company(company_name)
```

### 3. 速率限制

遵守 API 速率限制：

```python
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=60, period=60)  # 60 次/分鐘
def api_call():
    """受速率限制的 API 調用"""
    return make_request()
```

### 4. 批量操作

批量更新 CRM 而非逐個更新：

```python
def update_crm_batch(records):
    """批量更新 CRM"""

    # 收集所有更新
    updates = [
        {
            'id': record['id'],
            'fields': {'status': 'sent'}
        }
        for record in records
    ]

    # 一次性提交（Airtable 支持批量更新）
    table.batch_update(updates)
```

---

## 監控和可觀察性

### 日誌結構

```python
import logging
from datetime import datetime

class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)

    def log_event(self, event_type, **kwargs):
        """結構化日誌"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            **kwargs
        }

        self.logger.info(json.dumps(log_entry))

# 使用示例
logger = StructuredLogger('sales-automation')

logger.log_event(
    'email_sent',
    lead_id='123',
    email='john@example.com',
    status='success'
)
```

### 指標收集

```python
class Metrics:
    def __init__(self):
        self.counters = defaultdict(int)
        self.timers = defaultdict(list)

    def increment(self, metric):
        """計數器增加"""
        self.counters[metric] += 1

    def record_time(self, metric, duration):
        """記錄執行時間"""
        self.timers[metric].append(duration)

    def report(self):
        """生成報告"""
        return {
            'counters': dict(self.counters),
            'timers': {
                k: {
                    'avg': sum(v) / len(v),
                    'min': min(v),
                    'max': max(v)
                }
                for k, v in self.timers.items()
            }
        }
```

---

## 擴展性

### 添加新的 Agent

要添加新的 Agent（例如，SMS 通知 Agent）：

```python
# 1. 定義 Agent
class SMSAgent:
    def send_sms(self, to, message):
        # 實現 SMS 發送
        ...

# 2. 創建節點
def sms_notification_node(state):
    sms_agent = SMSAgent()

    lead = state["current_lead"]
    sms_agent.send_sms(
        to=lead["phone"],
        message=f"郵件已發送至 {lead['email']}"
    )

    return state

# 3. 添加到工作流
workflow = (
    START
    >> research_node
    >> generate_node
    >> send_node
    >> sms_notification_node  # 新節點
    >> update_crm_node
    >> END
)
```

### 支持新的 CRM

實現統一的 CRM 接口：

```python
from abc import ABC, abstractmethod

class CRMInterface(ABC):
    @abstractmethod
    def get_leads(self, filters):
        pass

    @abstractmethod
    def update_record(self, record_id, fields):
        pass

# Salesforce 實現
class SalesforceCRM(CRMInterface):
    def get_leads(self, filters):
        # Salesforce API 調用
        ...

    def update_record(self, record_id, fields):
        # 更新記錄
        ...
```

---

## 總結

銷售外展自動化系統採用了現代化的架構設計：

✅ **模組化**：易於理解和維護
✅ **可擴展**：輕鬆添加新功能
✅ **容錯性**：多層次錯誤處理
✅ **可觀察**：完善的日誌和監控
✅ **高性能**：支持並行和批量處理

通過 LangGraph 的狀態機模型，系統能夠優雅地處理複雜的銷售流程，同時保持代碼的清晰性和可維護性。

---

**下一步**：
- 查看 [best-practices.md](./best-practices.md) 了解最佳實踐
- 查看 [examples/](../examples/) 查看實際代碼示例
