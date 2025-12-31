# Instructor - 結構化 LLM 輸出框架

## 框架簡介

Instructor 是最受歡迎的 Python 結構化數據提取庫，專門用於從大型語言模型（LLM）中提取結構化數據。該框架擁有超過 300 萬月下載量和 11,000+ GitHub 星標，是業界標準的結構化輸出解決方案。

### 核心特點

- **Pydantic 整合**: 基於 Pydantic v2 構建，提供完整的類型安全和數據驗證
- **自動驗證**: 內建數據驗證機制，確保 LLM 輸出符合預期格式
- **重試機制**: 智能重試邏輯，自動處理驗證失敗和格式錯誤
- **流式輸出**: 支持流式結構化數據提取，實現實時響應
- **多模型支援**: 支持 OpenAI、Anthropic、Google、Cohere 等主流 LLM 提供商
- **零學習曲線**: 基於標準 Pydantic 模型，無需學習新的 API
- **生產就緒**: 經過大規模生產環境驗證，性能可靠

### 為什麼選擇 Instructor？

傳統的 LLM API 返回非結構化的文本，需要手動解析和驗證。Instructor 通過以下方式解決這個問題：

1. **類型安全**: 使用 Python 類型提示定義期望的輸出結構
2. **自動解析**: 自動將 LLM 響應解析為 Pydantic 模型
3. **驗證保證**: 確保所有字段符合定義的約束條件
4. **錯誤處理**: 智能重試機制處理格式錯誤和驗證失敗

## 安裝指南

### 基本安裝

```bash
pip install instructor
```

### 安裝特定 LLM 提供商支持

```bash
# OpenAI
pip install instructor openai

# Anthropic (Claude)
pip install instructor anthropic

# Google (Gemini)
pip install instructor google-generativeai

# 完整安裝（所有提供商）
pip install "instructor[all]"
```

### 從源碼安裝

```bash
git clone https://github.com/jxnl/instructor.git
cd instructor
pip install -e .
```

## 快速開始

### 基本示例

```python
import instructor
from openai import OpenAI
from pydantic import BaseModel

# 啟用 Instructor
client = instructor.from_openai(OpenAI())

# 定義輸出結構
class User(BaseModel):
    name: str
    age: int
    email: str

# 提取結構化數據
user = client.chat.completions.create(
    model="gpt-4",
    response_model=User,
    messages=[
        {"role": "user", "content": "Extract: John Doe, 30 years old, john@example.com"}
    ]
)

print(f"姓名: {user.name}")
print(f"年齡: {user.age}")
print(f"郵箱: {user.email}")
```

### 使用 Claude (Anthropic)

```python
import instructor
from anthropic import Anthropic
from pydantic import BaseModel

# 使用 Anthropic 模式
client = instructor.from_anthropic(Anthropic())

class Article(BaseModel):
    title: str
    summary: str
    keywords: list[str]

article = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    response_model=Article,
    messages=[
        {"role": "user", "content": "分析這篇文章..."}
    ]
)
```

### 帶驗證的模型

```python
from pydantic import BaseModel, Field, field_validator

class Product(BaseModel):
    name: str = Field(description="產品名稱")
    price: float = Field(gt=0, description="產品價格（必須大於0）")
    category: str = Field(description="產品類別")

    @field_validator('price')
    def validate_price(cls, v):
        if v > 1000000:
            raise ValueError('價格不能超過一百萬')
        return v

# 自動驗證和重試
product = client.chat.completions.create(
    model="gpt-4",
    response_model=Product,
    messages=[{"role": "user", "content": "提取產品信息..."}]
)
```

## 主要使用場景

### 1. 數據提取

從非結構化文本中提取結構化信息：

- 簡歷解析
- 發票處理
- 合同信息提取
- 新聞文章分析

### 2. API 響應格式化

確保 LLM 生成的 API 響應符合預定義格式：

- RESTful API 響應
- JSON Schema 驗證
- 數據庫記錄生成

### 3. 數據驗證和清洗

自動驗證和清洗 LLM 輸出：

- 數據類型驗證
- 範圍檢查
- 格式標準化
- 缺失值處理

### 4. 複雜結構化輸出

生成嵌套的複雜數據結構：

- 組織架構圖
- 知識圖譜
- 多層級分類
- 關係數據提取

### 5. 流式數據處理

實時處理和展示結構化數據：

- 實時數據儀表板
- 進度更新
- 增量數據提取

## 核心功能

### 自動重試機制

```python
from pydantic import BaseModel, field_validator

class ValidatedData(BaseModel):
    email: str

    @field_validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('必須包含 @ 符號')
        return v

# Instructor 會自動重試直到獲得有效的電子郵件
result = client.chat.completions.create(
    model="gpt-4",
    response_model=ValidatedData,
    max_retries=3,  # 最多重試 3 次
    messages=[{"role": "user", "content": "..."}]
)
```

### 流式輸出

```python
from instructor import Partial

# 使用 Partial 模型進行流式提取
for partial_user in client.chat.completions.create_partial(
    model="gpt-4",
    response_model=User,
    messages=[{"role": "user", "content": "..."}],
    stream=True
):
    print(partial_user)  # 實時獲取部分結果
```

### 批量處理

```python
from typing import List

class UserList(BaseModel):
    users: List[User]

# 批量提取多個用戶
users = client.chat.completions.create(
    model="gpt-4",
    response_model=UserList,
    messages=[{"role": "user", "content": "提取所有用戶信息..."}]
)
```

## 項目結構

```
47.Instructor/
├── README.md              # 項目文檔
├── requirements.txt       # 依賴包
├── 01_快速開始.py        # 基礎設置和提取
├── 02_模型定義.py        # Pydantic 模型定義
├── 03_驗證重試.py        # 驗證和重試機制
├── 04_流式提取.py        # 流式數據提取
├── 05_多模型支援.py      # 多 LLM 提供商
├── 06_複雜結構.py        # 複雜嵌套結構
├── 07_列表提取.py        # 列表和可迭代對象
├── 08_自定義驗證.py      # 自定義驗證器
├── 09_部分提取.py        # 部分提取和流式
└── 10_生產部署.py        # 生產最佳實踐
```

## 學習路徑

1. **入門** (01-02): 了解基本概念和模型定義
2. **進階** (03-05): 掌握驗證、流式輸出和多模型支持
3. **高級** (06-08): 處理複雜結構和自定義驗證
4. **生產** (09-10): 部分提取和生產部署

## 性能優勢

- **減少 API 調用**: 通過自動重試減少手動處理
- **提高準確性**: Pydantic 驗證確保數據質量
- **加快開發**: 零學習曲線，使用標準 Python 類型
- **降低成本**: 減少因格式錯誤導致的額外調用

## 最佳實踐

1. **明確的模型定義**: 使用描述性字段名和 Field 描述
2. **適當的驗證**: 添加必要的驗證器，但不要過度驗證
3. **錯誤處理**: 設置合理的 max_retries 值
4. **類型提示**: 充分利用 Python 類型系統
5. **文檔化**: 為模型和字段添加清晰的文檔字符串

## 社區資源

- **官方文檔**: https://python.useinstructor.com/
- **GitHub**: https://github.com/jxnl/instructor
- **Discord 社區**: https://discord.gg/bD9YE9JArw
- **教程**: https://python.useinstructor.com/tutorials/
- **示例庫**: https://github.com/jxnl/instructor/tree/main/examples

## 貢獻指南

歡迎貢獻！請查看：
- 提交 Issue: 報告 bug 或建議新功能
- Pull Request: 貢獻代碼或文檔改進
- 社區討論: 在 Discord 分享使用經驗

## 許可證

Instructor 採用 MIT 許可證開源。

## 更新日誌

### v1.13.0 (最新)
- 改進的流式支持
- 更好的錯誤消息
- 性能優化
- 新增 Google Gemini 支持

### v1.12.0
- Pydantic v2 完整支持
- 新的重試策略
- 改進的類型推斷

## 開始使用

選擇一個示例文件開始學習：

```bash
# 基礎示例
python 01_快速開始.py

# 高級功能
python 06_複雜結構.py

# 生產部署
python 10_生產部署.py
```

## 技術支持

如有問題，請：
1. 查閱官方文檔
2. 搜索 GitHub Issues
3. 加入 Discord 社區
4. 提交新的 Issue

---

**注意**: 使用前請確保設置相應的 API 密鑰（OPENAI_API_KEY、ANTHROPIC_API_KEY 等）。
