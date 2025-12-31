# Outlines - 結構化 LLM 輸出生成框架

## 框架介紹

Outlines 是一個強大的 Python 函式庫,專門用於從大型語言模型(LLM)生成結構化文本輸出。它通過在生成過程中強制執行結構約束,保證 LLM 的輸出符合預定義的格式和模式。

### 核心特性

Outlines 提供了革命性的方法來控制 LLM 輸出:

- **結構化輸出保證**: 在生成過程中強制執行結構約束,而不是事後驗證
- **零幻覺**: 完全消除格式錯誤和無效輸出
- **高效生成**: 通過智能採樣和約束傳播優化生成速度
- **靈活約束**: 支持多種約束類型和自定義規則

## 主要功能

### 1. JSON Schema 強制

Outlines 可以強制 LLM 生成符合 JSON Schema 的輸出:

```python
import outlines

schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "email": {"type": "string", "format": "email"}
    },
    "required": ["name", "age"]
}

model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")
generator = outlines.generate.json(model, schema)
result = generator("生成一個用戶資料")
```

### 2. 正則表達式約束

使用正則表達式定義輸出格式:

```python
import outlines

# 強制電話號碼格式
phone_pattern = r"\d{3}-\d{3}-\d{4}"
model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")
generator = outlines.generate.regex(model, phone_pattern)
phone = generator("生成一個電話號碼")
```

### 3. 上下文無關語法 (CFG)

支持使用 CFG 定義複雜的結構化輸出:

```python
import outlines

# SQL 查詢語法
sql_grammar = """
    ?start: select_statement

    select_statement: "SELECT" column_list "FROM" table_name where_clause?
    column_list: column_name ("," column_name)*
    column_name: /[a-zA-Z_][a-zA-Z0-9_]*/
    table_name: /[a-zA-Z_][a-zA-Z0-9_]*/
    where_clause: "WHERE" condition
    condition: column_name "=" value
    value: /'[^']*'/ | /[0-9]+/
"""

model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")
generator = outlines.generate.cfg(model, sql_grammar)
query = generator("查詢所有用戶")
```

### 4. Pydantic 模型整合

無縫整合 Pydantic 進行類型安全的輸出:

```python
from pydantic import BaseModel
import outlines

class User(BaseModel):
    name: str
    age: int
    email: str
    is_active: bool = True

model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")
generator = outlines.generate.json(model, User)
user = generator("生成一個管理員用戶")
```

### 5. 多選擇約束

強制從預定義選項中選擇:

```python
import outlines

choices = ["肯定", "否定", "中性"]
model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")
generator = outlines.generate.choice(model, choices)
sentiment = generator("這個產品很棒!")
```

## 安裝指南

### 基本安裝

```bash
pip install outlines
```

### 完整安裝(包含所有依賴)

```bash
pip install "outlines[all]"
```

### 從源碼安裝

```bash
git clone https://github.com/outlines-dev/outlines.git
cd outlines
pip install -e .
```

### 系統要求

- Python 3.8+
- PyTorch 2.0+ (用於 Transformers 後端)
- CUDA 11.8+ (GPU 加速,可選)
- 8GB+ RAM (CPU 模式)
- 16GB+ VRAM (GPU 模式,推薦)

### 依賴項

```bash
# 核心依賴
pip install transformers>=4.40.0
pip install torch>=2.0.0
pip install pydantic>=2.0.0

# 可選依賴
pip install vllm  # vLLM 加速
pip install openai  # OpenAI API 支持
pip install jsonschema  # JSON Schema 驗證
```

## 快速開始

### 1. 基本設置

```python
import outlines

# 載入模型
model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")

# 創建生成器
generator = outlines.generate.text(model)

# 生成文本
result = generator("寫一個關於 AI 的故事")
print(result)
```

### 2. JSON 結構化輸出

```python
import outlines
from pydantic import BaseModel, Field

class BlogPost(BaseModel):
    title: str = Field(description="文章標題")
    content: str = Field(description="文章內容")
    tags: list[str] = Field(description="標籤列表")
    views: int = Field(default=0, description="瀏覽次數")

# 載入模型
model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")

# 創建 JSON 生成器
generator = outlines.generate.json(model, BlogPost)

# 生成結構化輸出
prompt = "生成一篇關於人工智能的博客文章"
blog_post = generator(prompt)

print(f"標題: {blog_post.title}")
print(f"內容: {blog_post.content}")
print(f"標籤: {blog_post.tags}")
```

### 3. 正則表達式約束

```python
import outlines

# 定義電子郵件格式
email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

# 載入模型
model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")

# 創建正則生成器
generator = outlines.generate.regex(model, email_pattern)

# 生成符合格式的郵箱
email = generator("生成一個公司郵箱地址")
print(f"郵箱: {email}")
```

### 4. 多選擇分類

```python
import outlines

# 定義類別
categories = ["科技", "娛樂", "體育", "財經", "健康"]

# 載入模型
model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")

# 創建選擇生成器
generator = outlines.generate.choice(model, categories)

# 分類文本
text = "蘋果公司發布了新款 iPhone"
category = generator(f"將以下新聞分類: {text}")
print(f"類別: {category}")
```

### 5. 類型約束生成

```python
import outlines

# 載入模型
model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")

# 生成整數
int_generator = outlines.generate.format(model, int)
age = int_generator("一個成年人的年齡")
print(f"年齡: {age} (類型: {type(age)})")

# 生成浮點數
float_generator = outlines.generate.format(model, float)
price = float_generator("一台筆記本電腦的價格")
print(f"價格: {price} (類型: {type(price)})")

# 生成布爾值
bool_generator = outlines.generate.format(model, bool)
is_valid = bool_generator("這個郵箱地址有效嗎?")
print(f"有效: {is_valid} (類型: {type(is_valid)})")
```

## 使用場景

### 1. API 響應生成

自動生成符合 API 規範的 JSON 響應:

```python
from pydantic import BaseModel
import outlines

class APIResponse(BaseModel):
    status: str
    code: int
    message: str
    data: dict

model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")
generator = outlines.generate.json(model, APIResponse)
response = generator("生成成功的用戶創建響應")
```

### 2. 數據提取

從非結構化文本中提取結構化信息:

```python
from pydantic import BaseModel
import outlines

class PersonInfo(BaseModel):
    name: str
    age: int
    occupation: str
    location: str

text = "張三是一位35歲的軟件工程師,目前在北京工作"
model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")
generator = outlines.generate.json(model, PersonInfo)
info = generator(f"從以下文本提取信息: {text}")
```

### 3. 代碼生成

生成符合語法的代碼:

```python
import outlines

# Python 函數語法
python_grammar = """
    ?start: function_def

    function_def: "def" CNAME "(" params? ")" ":" suite
    params: CNAME ("," CNAME)*
    suite: simple_stmt | NEWLINE INDENT stmt+ DEDENT
    simple_stmt: "return" expr NEWLINE
    stmt: simple_stmt | compound_stmt
    compound_stmt: if_stmt | for_stmt
    if_stmt: "if" expr ":" suite
    for_stmt: "for" CNAME "in" expr ":" suite
    expr: CNAME | NUMBER | STRING

    %import common.CNAME
    %import common.NUMBER
    %import common.STRING
    %import common.NEWLINE
    %import common.INDENT
    %import common.DEDENT
"""

model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")
generator = outlines.generate.cfg(model, python_grammar)
code = generator("生成一個計算斐波那契數列的函數")
```

### 4. 表單驗證

確保用戶輸入符合特定格式:

```python
import outlines

# 驗證郵政編碼
zip_pattern = r"\d{5}(-\d{4})?"
model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")
generator = outlines.generate.regex(model, zip_pattern)
zip_code = generator("台北市的郵政編碼")
```

### 5. 聊天機器人

構建可靠的結構化對話系統:

```python
from pydantic import BaseModel
import outlines

class ChatResponse(BaseModel):
    intent: str
    sentiment: str
    response: str
    confidence: float
    requires_human: bool

model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")
generator = outlines.generate.json(model, ChatResponse)

user_message = "我的訂單還沒收到,很著急"
response = generator(f"用戶消息: {user_message}")
print(f"意圖: {response.intent}")
print(f"情緒: {response.sentiment}")
print(f"回覆: {response.response}")
```

### 6. 數據驗證

確保生成的數據符合業務規則:

```python
from pydantic import BaseModel, Field, validator
import outlines

class Product(BaseModel):
    name: str
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)
    category: str

    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('價格必須大於 0')
        return v

model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")
generator = outlines.generate.json(model, Product)
product = generator("生成一個電子產品")
```

### 7. SQL 查詢生成

生成安全的 SQL 查詢:

```python
import outlines

sql_grammar = """
    ?start: select_stmt

    select_stmt: "SELECT" columns "FROM" table where_clause?
    columns: "*" | column_list
    column_list: CNAME ("," CNAME)*
    table: CNAME
    where_clause: "WHERE" condition
    condition: CNAME "=" value
    value: STRING | NUMBER

    %import common.CNAME
    %import common.STRING
    %import common.NUMBER
"""

model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")
generator = outlines.generate.cfg(model, sql_grammar)
query = generator("查詢所有活躍用戶")
```

### 8. 批量數據生成

高效生成大量結構化數據:

```python
from pydantic import BaseModel
import outlines

class TestUser(BaseModel):
    username: str
    email: str
    age: int
    is_premium: bool

model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")
generator = outlines.generate.json(model, TestUser)

# 批量生成
users = []
for i in range(100):
    user = generator(f"生成測試用戶 #{i+1}")
    users.append(user)
```

### 9. 配置文件生成

生成符合格式的配置文件:

```python
from pydantic import BaseModel
import outlines

class DatabaseConfig(BaseModel):
    host: str
    port: int
    database: str
    username: str
    password: str
    max_connections: int = 10

model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")
generator = outlines.generate.json(model, DatabaseConfig)
config = generator("生成 PostgreSQL 數據庫配置")
```

### 10. 實時推理服務

部署為生產環境的 API 服務:

```python
from fastapi import FastAPI
from pydantic import BaseModel
import outlines

app = FastAPI()

class PredictionRequest(BaseModel):
    text: str

class PredictionResponse(BaseModel):
    category: str
    confidence: float
    explanation: str

# 載入模型(只載入一次)
model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")
generator = outlines.generate.json(model, PredictionResponse)

@app.post("/predict")
async def predict(request: PredictionRequest):
    response = generator(f"分類文本: {request.text}")
    return response
```

## 優勢特點

### 1. 零格式錯誤
- 生成過程中強制執行約束
- 完全消除解析錯誤
- 無需事後驗證和重試

### 2. 高性能
- 智能約束傳播算法
- 優化的採樣策略
- 支持 GPU 加速

### 3. 易於使用
- 簡潔的 API 設計
- 與現有工具無縫整合
- 豐富的文檔和示例

### 4. 靈活擴展
- 支持自定義約束
- 多種後端支持(Transformers, vLLM, OpenAI)
- 可插拔架構

## 性能優化

### 1. 使用 vLLM 加速

```python
import outlines

# 使用 vLLM 後端
model = outlines.models.vllm("mistralai/Mistral-7B-v0.1")
generator = outlines.generate.json(model, schema)
```

### 2. 批量處理

```python
# 批量生成可以提高吞吐量
prompts = ["提示1", "提示2", "提示3"]
results = generator(prompts)
```

### 3. 模型量化

```python
# 使用量化模型減少內存佔用
model = outlines.models.transformers(
    "mistralai/Mistral-7B-v0.1",
    device="cuda",
    model_kwargs={"load_in_8bit": True}
)
```

## 社區資源

- **官方網站**: https://outlines-dev.github.io/outlines/
- **GitHub**: https://github.com/outlines-dev/outlines
- **文檔**: https://outlines-dev.github.io/outlines/reference/
- **Discord**: https://discord.gg/R9DSu34mGd
- **Twitter**: @OutlinesAI

## 授權協議

Outlines 使用 Apache 2.0 授權協議開源。

## 貢獻指南

歡迎貢獻代碼、報告問題或提出建議!請訪問 GitHub 倉庫了解更多信息。

---

**注意**: Outlines 是一個快速發展的項目,API 可能會有變化。請參考官方文檔獲取最新信息。
