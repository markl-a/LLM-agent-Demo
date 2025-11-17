# 實戰教程 Part 2：LLM 整合實作

## 目錄

1. [LLM API 整合基礎](#llm-api-整合基礎)
2. [智能數據提取](#智能數據提取)
3. [自然語言指令處理](#自然語言指令處理)
4. [Prompt Engineering 最佳實踐](#prompt-engineering-最佳實踐)
5. [錯誤處理與重試機制](#錯誤處理與重試機制)
6. [實戰專案：智能發票處理](#實戰專案智能發票處理)

---

## LLM API 整合基礎

### 環境準備

```bash
# 安裝 LLM 相關套件
pip install openai anthropic langchain langchain-openai langchain-anthropic

# 安裝本地 LLM 支援
pip install ollama

# 其他依賴
pip install python-dotenv tiktoken
```

### 配置 API 金鑰

更新 **.env** 文件：

```env
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# 本地 LLM (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# LLM 設置
LLM_PROVIDER=openai  # openai, anthropic, ollama
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
```

### 建立統一的 LLM 介面

**scripts/llm/base.py**

```python
"""
LLM 基礎模組
提供統一的 LLM 介面
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv

load_dotenv()

class BaseLLM(ABC):
    """LLM 基礎類"""

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """生成回應"""
        pass

    @abstractmethod
    async def generate_with_schema(
        self,
        prompt: str,
        schema: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """使用 Schema 生成結構化輸出"""
        pass

    def count_tokens(self, text: str) -> int:
        """估算 Token 數量"""
        # 簡化版本：約 4 字元 = 1 token
        return len(text) // 4

class OpenAILLM(BaseLLM):
    """OpenAI LLM 實現"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.model = self.model or os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

    async def generate(self, prompt: str, **kwargs) -> str:
        """生成回應"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        )
        return response.choices[0].message.content

    async def generate_with_schema(
        self,
        prompt: str,
        schema: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """使用 Function Calling 實現結構化輸出"""
        import json

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            functions=[{
                "name": "extract_data",
                "description": "Extract structured data",
                "parameters": schema
            }],
            function_call={"name": "extract_data"},
            temperature=kwargs.get("temperature", self.temperature),
        )

        function_call = response.choices[0].message.function_call
        return json.loads(function_call.arguments)

class ClaudeLLM(BaseLLM):
    """Anthropic Claude LLM 實現"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from anthropic import AsyncAnthropic

        self.client = AsyncAnthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.model = self.model or os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")

    async def generate(self, prompt: str, **kwargs) -> str:
        """生成回應"""
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            temperature=kwargs.get("temperature", self.temperature),
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    async def generate_with_schema(
        self,
        prompt: str,
        schema: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """使用提示工程實現結構化輸出"""
        import json

        # 構建結構化提示
        schema_description = self._schema_to_description(schema)
        structured_prompt = f"""{prompt}

Please provide your response in the following JSON format:
{schema_description}

Return only valid JSON without any explanation.
"""

        response = await self.generate(structured_prompt, **kwargs)

        # 提取 JSON
        try:
            # 嘗試直接解析
            return json.loads(response)
        except json.JSONDecodeError:
            # 嘗試提取 JSON 區塊
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError("Failed to extract JSON from response")

    def _schema_to_description(self, schema: Dict[str, Any]) -> str:
        """將 Schema 轉換為描述"""
        import json
        return json.dumps(schema, indent=2)

class OllamaLLM(BaseLLM):
    """Ollama 本地 LLM 實現"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = self.model or os.getenv("OLLAMA_MODEL", "llama2")

    async def generate(self, prompt: str, **kwargs) -> str:
        """生成回應"""
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get("temperature", self.temperature),
                        "num_predict": kwargs.get("max_tokens", self.max_tokens),
                    }
                }
            ) as response:
                result = await response.json()
                return result["response"]

    async def generate_with_schema(
        self,
        prompt: str,
        schema: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """使用提示工程實現結構化輸出"""
        import json

        schema_str = json.dumps(schema, indent=2)
        structured_prompt = f"""{prompt}

Return your response as JSON matching this schema:
{schema_str}

JSON:
"""

        response = await self.generate(structured_prompt, **kwargs)

        # 提取並解析 JSON
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())

        # 如果沒找到，嘗試直接解析
        return json.loads(response)

class LLMFactory:
    """LLM 工廠"""

    _providers = {
        "openai": OpenAILLM,
        "claude": ClaudeLLM,
        "anthropic": ClaudeLLM,
        "ollama": OllamaLLM,
    }

    @classmethod
    def create(cls, provider: Optional[str] = None, **kwargs) -> BaseLLM:
        """創建 LLM 實例"""
        provider = provider or os.getenv("LLM_PROVIDER", "openai")

        llm_class = cls._providers.get(provider.lower())
        if not llm_class:
            raise ValueError(f"Unknown provider: {provider}")

        return llm_class(**kwargs)

# 便捷函數
def get_llm(provider: Optional[str] = None, **kwargs) -> BaseLLM:
    """獲取 LLM 實例"""
    return LLMFactory.create(provider, **kwargs)
```

### 使用範例

```python
import asyncio
from scripts.llm.base import get_llm

async def test_llm():
    # 使用 OpenAI
    llm = get_llm("openai")
    response = await llm.generate("What is RPA?")
    print(f"OpenAI: {response}\n")

    # 使用 Claude
    llm = get_llm("claude")
    response = await llm.generate("What is RPA?")
    print(f"Claude: {response}\n")

    # 結構化輸出
    schema = {
        "type": "object",
        "properties": {
            "definition": {"type": "string"},
            "benefits": {"type": "array", "items": {"type": "string"}},
            "use_cases": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["definition", "benefits", "use_cases"]
    }

    result = await llm.generate_with_schema(
        "Explain RPA in detail",
        schema
    )
    print(f"Structured: {result}")

if __name__ == "__main__":
    asyncio.run(test_llm())
```

---

## 智能數據提取

### 從非結構化文本提取資訊

**scripts/llm/data_extraction.py**

```python
"""
智能數據提取模組
使用 LLM 從非結構化數據中提取結構化資訊
"""
from typing import Dict, Any, List
from scripts.llm.base import get_llm
from utils.logger import setup_logger

logger = setup_logger("data_extraction")

class IntelligentExtractor:
    """智能提取器"""

    def __init__(self, provider: str = "openai"):
        self.llm = get_llm(provider)

    async def extract_invoice_data(self, text: str) -> Dict[str, Any]:
        """
        從發票文本提取資訊

        Args:
            text: 發票文本內容

        Returns:
            結構化的發票資訊
        """
        logger.info("開始提取發票資訊")

        schema = {
            "type": "object",
            "properties": {
                "invoice_number": {"type": "string", "description": "發票號碼"},
                "date": {"type": "string", "description": "發票日期 (YYYY-MM-DD)"},
                "vendor": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "address": {"type": "string"},
                        "tax_id": {"type": "string"}
                    }
                },
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "quantity": {"type": "number"},
                            "unit_price": {"type": "number"},
                            "total": {"type": "number"}
                        }
                    }
                },
                "subtotal": {"type": "number"},
                "tax": {"type": "number"},
                "total": {"type": "number"}
            },
            "required": ["invoice_number", "date", "vendor", "items", "total"]
        }

        prompt = f"""Extract structured information from this invoice:

{text}

Extract all relevant details including invoice number, date, vendor information, line items, and totals.
"""

        result = await self.llm.generate_with_schema(prompt, schema)
        logger.info(f"提取完成: {result.get('invoice_number')}")

        return result

    async def extract_email_intent(self, email_text: str) -> Dict[str, Any]:
        """
        分析郵件意圖

        Args:
            email_text: 郵件內容

        Returns:
            郵件分析結果
        """
        schema = {
            "type": "object",
            "properties": {
                "intent": {
                    "type": "string",
                    "enum": ["inquiry", "complaint", "request", "feedback", "other"]
                },
                "urgency": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"]
                },
                "summary": {"type": "string"},
                "key_points": {"type": "array", "items": {"type": "string"}},
                "requires_action": {"type": "boolean"},
                "suggested_response": {"type": "string"}
            },
            "required": ["intent", "urgency", "summary", "requires_action"]
        }

        prompt = f"""Analyze this email and extract key information:

{email_text}

Determine the intent, urgency, summarize the content, and suggest a response if needed.
"""

        return await self.llm.generate_with_schema(prompt, schema)

    async def extract_resume_data(self, resume_text: str) -> Dict[str, Any]:
        """
        從履歷提取資訊

        Args:
            resume_text: 履歷內容

        Returns:
            結構化的履歷資訊
        """
        schema = {
            "type": "object",
            "properties": {
                "personal_info": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                        "phone": {"type": "string"},
                        "location": {"type": "string"}
                    }
                },
                "education": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "degree": {"type": "string"},
                            "school": {"type": "string"},
                            "year": {"type": "string"}
                        }
                    }
                },
                "experience": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "company": {"type": "string"},
                            "duration": {"type": "string"},
                            "responsibilities": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    }
                },
                "skills": {"type": "array", "items": {"type": "string"}}
            }
        }

        prompt = f"""Extract structured information from this resume:

{resume_text}

Extract personal information, education history, work experience, and skills.
"""

        return await self.llm.generate_with_schema(prompt, schema)

# 使用範例
async def demo_extraction():
    """示範數據提取"""
    extractor = IntelligentExtractor()

    # 示例發票文本
    invoice_text = """
    INVOICE #INV-2024-001
    Date: January 15, 2024

    From:
    ABC Company Ltd.
    123 Business Street
    Tax ID: 12345678

    Items:
    1. Widget A - Qty: 10 x $50.00 = $500.00
    2. Widget B - Qty: 5 x $100.00 = $500.00

    Subtotal: $1,000.00
    Tax (10%): $100.00
    Total: $1,100.00
    """

    result = await extractor.extract_invoice_data(invoice_text)
    print("發票提取結果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    import asyncio
    import json
    asyncio.run(demo_extraction())
```

---

## 自然語言指令處理

### 將自然語言轉換為 RPA 操作

**scripts/llm/nl_commander.py**

```python
"""
自然語言指令處理器
將自然語言指令轉換為可執行的 RPA 操作
"""
from typing import List, Dict, Any
from scripts.llm.base import get_llm
from utils.logger import setup_logger

logger = setup_logger("nl_commander")

class NLCommander:
    """自然語言指令處理器"""

    def __init__(self, provider: str = "openai"):
        self.llm = get_llm(provider)

    async def parse_command(self, command: str) -> Dict[str, Any]:
        """
        解析自然語言指令

        Args:
            command: 自然語言指令

        Returns:
            結構化的操作指令
        """
        logger.info(f"解析指令: {command}")

        schema = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "web_navigate", "web_click", "web_fill", "web_extract",
                        "file_open", "file_save", "file_process",
                        "data_filter", "data_transform", "data_export",
                        "email_send", "email_read",
                        "wait", "repeat"
                    ]
                },
                "parameters": {
                    "type": "object",
                    "description": "操作所需的參數"
                },
                "description": {
                    "type": "string",
                    "description": "操作的簡短描述"
                }
            },
            "required": ["action", "parameters"]
        }

        prompt = f"""Convert this natural language command into a structured RPA action:

Command: "{command}"

Available actions:
- web_navigate: Navigate to a URL
- web_click: Click an element
- web_fill: Fill a form field
- web_extract: Extract data from page
- file_open: Open a file
- file_save: Save a file
- file_process: Process file data
- data_filter: Filter data
- data_transform: Transform data
- data_export: Export data
- email_send: Send email
- email_read: Read email
- wait: Wait for some time
- repeat: Repeat actions

Return the most appropriate action with necessary parameters.
"""

        result = await self.llm.generate_with_schema(prompt, schema)
        logger.info(f"解析結果: {result['action']}")

        return result

    async def generate_workflow(self, task_description: str) -> List[Dict[str, Any]]:
        """
        從任務描述生成完整工作流程

        Args:
            task_description: 任務描述

        Returns:
            工作流程步驟列表
        """
        logger.info(f"生成工作流程: {task_description}")

        schema = {
            "type": "object",
            "properties": {
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "step_number": {"type": "integer"},
                            "action": {"type": "string"},
                            "parameters": {"type": "object"},
                            "description": {"type": "string"}
                        }
                    }
                }
            },
            "required": ["steps"]
        }

        prompt = f"""Generate a detailed RPA workflow for this task:

Task: {task_description}

Break down the task into specific, executable steps. Each step should have:
- action type (web_navigate, web_click, web_fill, etc.)
- parameters needed
- clear description

Return a complete workflow.
"""

        result = await self.llm.generate_with_schema(prompt, schema)
        logger.info(f"生成 {len(result['steps'])} 個步驟")

        return result['steps']

    async def execute_nl_workflow(self, task: str):
        """
        執行自然語言描述的工作流程

        Args:
            task: 任務描述
        """
        # 1. 生成工作流程
        steps = await self.generate_workflow(task)

        # 2. 執行每個步驟
        for step in steps:
            logger.info(f"執行步驟 {step['step_number']}: {step['description']}")

            # 根據 action 類型執行相應操作
            action = step['action']
            params = step['parameters']

            try:
                await self._execute_action(action, params)
                logger.info(f"步驟 {step['step_number']} 完成")
            except Exception as e:
                logger.error(f"步驟 {step['step_number']} 失敗: {str(e)}")
                raise

    async def _execute_action(self, action: str, params: Dict[str, Any]):
        """執行單個操作"""
        # 這裡需要整合實際的 RPA 執行模組
        # 示例實現
        action_map = {
            "web_navigate": self._web_navigate,
            "web_click": self._web_click,
            "web_fill": self._web_fill,
            # ... 其他操作
        }

        handler = action_map.get(action)
        if handler:
            await handler(params)
        else:
            logger.warning(f"未實現的操作: {action}")

    async def _web_navigate(self, params: Dict[str, Any]):
        """網頁導航"""
        url = params.get("url")
        logger.info(f"導航到: {url}")
        # 實際實現使用 Playwright

    async def _web_click(self, params: Dict[str, Any]):
        """點擊元素"""
        selector = params.get("selector")
        logger.info(f"點擊: {selector}")
        # 實際實現

    async def _web_fill(self, params: Dict[str, Any]):
        """填寫表單"""
        selector = params.get("selector")
        value = params.get("value")
        logger.info(f"填寫 {selector}: {value}")
        # 實際實現

# 使用範例
async def demo_nl_commander():
    """示範自然語言指令處理"""
    commander = NLCommander()

    # 1. 解析單個指令
    print("=== 解析單個指令 ===")
    command = "Go to google.com and search for 'RPA automation'"
    action = await commander.parse_command(command)
    print(json.dumps(action, indent=2))

    # 2. 生成完整工作流程
    print("\n=== 生成工作流程 ===")
    task = """
    Open the company website, login with credentials,
    navigate to the reports section, download last month's sales report,
    and send it via email to manager@company.com
    """
    workflow = await commander.generate_workflow(task)

    for step in workflow:
        print(f"\nStep {step['step_number']}: {step['description']}")
        print(f"Action: {step['action']}")
        print(f"Parameters: {step['parameters']}")

if __name__ == "__main__":
    import asyncio
    import json
    asyncio.run(demo_nl_commander())
```

---

## Prompt Engineering 最佳實踐

### Prompt 模板管理

**scripts/llm/prompts.py**

```python
"""
Prompt 模板管理
"""
from typing import Dict, Any
from jinja2 import Template

class PromptTemplates:
    """Prompt 模板集合"""

    # 數據提取模板
    EXTRACT_INVOICE = Template("""
You are an expert at extracting structured data from invoices.

Extract the following information from the invoice text below:
- Invoice Number
- Date (format: YYYY-MM-DD)
- Vendor Information (name, address, tax ID)
- Line Items (description, quantity, unit price, total)
- Subtotal, Tax, and Total Amount

Invoice Text:
{{ invoice_text }}

Return the data in valid JSON format matching this schema:
{{ schema }}
""")

    # 數據驗證模板
    VALIDATE_DATA = Template("""
You are a data quality expert.

Validate the following extracted data and identify any issues:

Data:
{{ data }}

Check for:
1. Missing required fields
2. Invalid formats (dates, numbers, etc.)
3. Logical inconsistencies (e.g., total != subtotal + tax)
4. Suspicious values

Return validation results in JSON format:
{
  "is_valid": boolean,
  "issues": [
    {"field": "field_name", "issue": "description", "severity": "error|warning"}
  ],
  "suggestions": ["suggestion1", "suggestion2"]
}
""")

    # 自然語言轉 SQL
    NL_TO_SQL = Template("""
Convert this natural language query to SQL:

Database Schema:
{{ schema }}

Query: {{ query }}

Return only the SQL query without explanation.
""")

    # 錯誤分析
    ANALYZE_ERROR = Template("""
Analyze this error and suggest solutions:

Error Message:
{{ error_message }}

Context:
{{ context }}

Provide:
1. Root cause analysis
2. Potential solutions
3. Prevention strategies

Return as JSON.
""")

    @classmethod
    def render(cls, template_name: str, **kwargs) -> str:
        """渲染模板"""
        template = getattr(cls, template_name)
        return template.render(**kwargs)
```

### Few-Shot Learning

```python
async def extract_with_examples(text: str, llm):
    """使用示例學習提升準確度"""

    prompt = f"""Extract product information from the text.

Here are some examples:

Example 1:
Input: "Apple iPhone 14 Pro - $999 - 128GB Storage - Blue"
Output: {{"name": "iPhone 14 Pro", "brand": "Apple", "price": 999, "specs": {{"storage": "128GB", "color": "Blue"}}}}

Example 2:
Input: "Samsung Galaxy S23 Ultra, Price: $1199, Memory: 256GB, Color: Black"
Output: {{"name": "Galaxy S23 Ultra", "brand": "Samsung", "price": 1199, "specs": {{"storage": "256GB", "color": "Black"}}}}

Now extract from this text:
Input: "{text}"
Output:"""

    response = await llm.generate(prompt)
    return json.loads(response)
```

### Chain of Thought (CoT)

```python
async def complex_reasoning(problem: str, llm):
    """使用思維鏈提升推理能力"""

    prompt = f"""Solve this problem step by step.

Problem: {problem}

Let's think through this carefully:
1. First, identify the key information
2. Then, break down the problem into steps
3. Solve each step
4. Combine the results

Show your reasoning for each step, then provide the final answer in JSON format.
"""

    return await llm.generate(prompt)
```

---

## 錯誤處理與重試機制

### 智能重試

**scripts/llm/retry_handler.py**

```python
"""
LLM 調用重試處理器
"""
import asyncio
from typing import Callable, Any, Optional
from functools import wraps
from utils.logger import setup_logger

logger = setup_logger("retry_handler")

class RetryConfig:
    """重試配置"""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0

async def retry_with_backoff(
    func: Callable,
    *args,
    config: Optional[RetryConfig] = None,
    **kwargs
) -> Any:
    """
    帶指數退避的重試機制

    Args:
        func: 要執行的函數
        config: 重試配置
        *args, **kwargs: 函數參數

    Returns:
        函數執行結果
    """
    config = config or RetryConfig()

    for attempt in range(config.max_retries):
        try:
            return await func(*args, **kwargs)

        except Exception as e:
            if attempt == config.max_retries - 1:
                logger.error(f"最終重試失敗: {str(e)}")
                raise

            # 計算延遲時間（指數退避）
            delay = min(
                config.base_delay * (config.exponential_base ** attempt),
                config.max_delay
            )

            logger.warning(
                f"第 {attempt + 1} 次嘗試失敗: {str(e)}. "
                f"{delay:.1f}秒後重試..."
            )

            await asyncio.sleep(delay)

def with_retry(config: Optional[RetryConfig] = None):
    """重試裝飾器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_with_backoff(func, *args, config=config, **kwargs)
        return wrapper
    return decorator

# 使用範例
@with_retry(RetryConfig(max_retries=5))
async def call_llm_with_retry(llm, prompt: str) -> str:
    """帶重試的 LLM 調用"""
    return await llm.generate(prompt)
```

---

## 實戰專案：智能發票處理

### 完整實現

**scripts/projects/invoice_processor.py**

```python
"""
智能發票處理系統
整合 RPA + LLM 自動處理發票
"""
import asyncio
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from scripts.llm.base import get_llm
from scripts.llm.data_extraction import IntelligentExtractor
from utils.logger import setup_logger
from config.settings import INPUT_DIR, OUTPUT_DIR

logger = setup_logger("invoice_processor")

class InvoiceProcessor:
    """發票處理器"""

    def __init__(self):
        self.llm = get_llm()
        self.extractor = IntelligentExtractor()
        self.processed_data: List[Dict[str, Any]] = []

    async def process_invoice_files(self, input_dir: Path):
        """
        批次處理發票文件

        Args:
            input_dir: 輸入目錄
        """
        logger.info(f"開始處理發票文件: {input_dir}")

        # 獲取所有 PDF 文件
        invoice_files = list(input_dir.glob("*.pdf"))
        logger.info(f"找到 {len(invoice_files)} 個發票文件")

        # 並發處理
        tasks = [
            self.process_single_invoice(file)
            for file in invoice_files
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 統計結果
        successful = sum(1 for r in results if not isinstance(r, Exception))
        logger.info(f"處理完成: {successful}/{len(invoice_files)} 成功")

    async def process_single_invoice(self, file_path: Path) -> Dict[str, Any]:
        """
        處理單個發票

        Args:
            file_path: 發票文件路徑

        Returns:
            提取的數據
        """
        logger.info(f"處理發票: {file_path.name}")

        try:
            # 1. 提取文本
            text = self._extract_pdf_text(file_path)

            # 2. 使用 LLM 提取結構化數據
            data = await self.extractor.extract_invoice_data(text)

            # 3. 驗證數據
            is_valid, issues = await self._validate_data(data)

            if not is_valid:
                logger.warning(f"數據驗證失敗: {issues}")
                # 嘗試修正
                data = await self._fix_data(data, issues)

            # 4. 保存結果
            data['source_file'] = file_path.name
            data['is_valid'] = is_valid
            self.processed_data.append(data)

            logger.info(f"發票處理成功: {data.get('invoice_number')}")
            return data

        except Exception as e:
            logger.error(f"處理發票失敗 {file_path.name}: {str(e)}")
            raise

    def _extract_pdf_text(self, file_path: Path) -> str:
        """提取 PDF 文本"""
        import pdfplumber

        with pdfplumber.open(file_path) as pdf:
            text = "\n".join([page.extract_text() for page in pdf.pages])

        return text

    async def _validate_data(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """驗證數據"""
        from scripts.llm.prompts import PromptTemplates
        import json

        prompt = PromptTemplates.render(
            "VALIDATE_DATA",
            data=json.dumps(data, indent=2)
        )

        result = await self.llm.generate(prompt)
        validation = json.loads(result)

        return validation['is_valid'], validation.get('issues', [])

    async def _fix_data(self, data: Dict[str, Any], issues: List[Dict]) -> Dict[str, Any]:
        """嘗試修正數據"""
        logger.info("嘗試自動修正數據")

        prompt = f"""Fix these data issues:

Original Data:
{json.dumps(data, indent=2)}

Issues:
{json.dumps(issues, indent=2)}

Return the corrected data in JSON format.
"""

        result = await self.llm.generate(prompt)
        return json.loads(result)

    def export_to_excel(self, output_path: Path):
        """導出到 Excel"""
        if not self.processed_data:
            logger.warning("沒有數據可導出")
            return

        # 展平嵌套數據
        flat_data = []
        for invoice in self.processed_data:
            flat_invoice = {
                'invoice_number': invoice.get('invoice_number'),
                'date': invoice.get('date'),
                'vendor_name': invoice.get('vendor', {}).get('name'),
                'total': invoice.get('total'),
                'source_file': invoice.get('source_file'),
                'is_valid': invoice.get('is_valid')
            }
            flat_data.append(flat_invoice)

        df = pd.DataFrame(flat_data)
        df.to_excel(output_path, index=False)

        logger.info(f"數據已導出: {output_path}")

async def main():
    """主函數"""
    processor = InvoiceProcessor()

    # 處理發票
    await processor.process_invoice_files(INPUT_DIR / "invoices")

    # 導出結果
    processor.export_to_excel(OUTPUT_DIR / "invoices_processed.xlsx")

    print("\n發票處理完成！")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 總結與下一步

### 本章學習重點

✅ 整合多種 LLM API (OpenAI, Claude, Ollama)
✅ 智能數據提取技術
✅ 自然語言指令處理
✅ Prompt Engineering 最佳實踐
✅ 錯誤處理與重試機制
✅ 完整的實戰專案實現

### 下一步

繼續學習 [tutorial-part3-advanced.md](./tutorial-part3-advanced.md)，探索：
- 多 Agent 協作系統
- RAG 在 RPA 中的應用
- 工作流程自動生成
- 效能優化技巧

---

## 練習作業

1. **基礎**：修改 LLM 工廠支援你自己的 LLM 提供商
2. **中級**：實現一個智能郵件分類器
3. **進階**：創建一個可以理解中文自然語言指令的 RPA 系統

參考解答見 [examples/](./examples/) 目錄。
