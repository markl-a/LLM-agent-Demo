# Instructor & Outlines - 結構化輸出框架

## 📚 簡介

本資料夾包含兩個強大的 Python 框架的完整範例：**Instructor** 和 **Outlines**。這兩個框架都專注於從大型語言模型（LLM）中獲得結構化、可驗證的輸出。

### Instructor
Instructor 是最受歡迎的 Python 函式庫，用於從 LLM 中提取結構化資料。擁有超過 300 萬月下載量、11k+ GitHub stars，是開發者獲取可靠且經過驗證的 AI 輸出的首選方案。

**特點：**
- 🎯 **結構化輸出**：使用 Pydantic 模型定義精確的資料結構
- 🔄 **自動重試**：驗證失敗時內建重試邏輯
- ✅ **資料驗證**：利用 Pydantic 的強大驗證功能
- 🌊 **串流支援**：即時處理部分回應
- 🔌 **多提供商支援**：支援 OpenAI、Anthropic、Google、Ollama 等 15+ 提供商
- 🛡️ **型別安全**：完整的 IDE 支援和型別提示

### Outlines
Outlines 保證在生成過程中直接從任何 LLM 獲得結構化輸出。它使用有限狀態機（FSM）來強制執行輸出約束，確保輸出嚴格符合指定的模式或格式。

**特點：**
- 🎯 **保證結構**：確保輸出符合指定格式，無需解析錯誤
- 🔀 **提供商獨立**：相同程式碼可在 OpenAI、Ollama、vLLM 等平台運行
- 📐 **靈活約束**：支援 JSON Schema、正則表達式、上下文無關文法
- ⚡ **高性能**：Rust 實作提供 2x 編譯速度提升
- 🔧 **簡單整合**：易於與現有專案整合

## 🚀 安裝方式

### Instructor 安裝

```bash
# 基本安裝
pip install instructor

# 包含 OpenAI 支援
pip install instructor openai

# 包含 Anthropic Claude 支援
pip install instructor anthropic

# 包含所有依賴
pip install "instructor[all]"
```

**需求：**
- Python >= 3.9, < 4.0
- 最新版本：1.13.0（2025 年 11 月）

### Outlines 安裝

```bash
# 基本安裝
pip install outlines

# 使用 Rust 核心（更快）
pip install outlines-core

# 與 Transformers 一起使用
pip install outlines transformers torch

# 與 vLLM 一起使用
pip install outlines vllm
```

**需求：**
- Python >= 3.10
- 支援 CPython 3.10-3.13

## 📁 範例檔案說明

### Instructor 範例（01-04）

1. **01_Instructor基礎.py**
   - Instructor 的基本使用方法
   - 如何定義 Pydantic 模型
   - 從 LLM 提取結構化資料
   - 多提供商配置（OpenAI、Anthropic）

2. **02_Pydantic驗證.py**
   - Pydantic 欄位驗證
   - 自訂驗證器
   - 欄位約束（min/max、regex 等）
   - 驗證錯誤處理

3. **03_複雜結構.py**
   - 嵌套 Pydantic 模型
   - 列表和字典結構
   - 可選欄位和預設值
   - 複雜資料關係

4. **04_重試機制.py**
   - 自動重試配置
   - 驗證失敗處理
   - 自訂重試邏輯
   - 錯誤回饋機制

### Outlines 範例（05-07）

5. **05_Outlines基礎.py**
   - Outlines 基本概念
   - 文字生成約束
   - 多種後端支援
   - 基本生成範例

6. **06_JSON生成.py**
   - JSON Schema 定義
   - Pydantic 模型轉換
   - 保證有效 JSON 輸出
   - 複雜 JSON 結構

7. **07_正則約束.py**
   - 正則表達式模式
   - 格式驗證（Email、IP、電話等）
   - 自訂正則約束
   - 多模式組合

### 整合與進階範例（08-10）

8. **08_多模型支持.py**
   - 多 LLM 提供商配置
   - Instructor 與不同模型
   - Outlines 後端切換
   - 統一介面設計

9. **09_流式輸出.py**
   - Instructor 串流生成
   - 部分結果處理
   - 即時驗證
   - 串流錯誤處理

10. **10_進階技巧.py**
    - 效能優化
    - 快取策略
    - 錯誤處理最佳實踐
    - 生產環境建議

## 🔗 官方資源

### Instructor
- 📖 官方文檔：https://python.useinstructor.com/
- 🐙 GitHub：https://github.com/567-labs/instructor
- 📦 PyPI：https://pypi.org/project/instructor/
- 🎓 入門教學：https://python.useinstructor.com/learning/getting_started/structured_outputs/

### Outlines
- 📖 官方文檔：https://dottxt-ai.github.io/outlines/latest/
- 🐙 GitHub：https://github.com/dottxt-ai/outlines
- 📦 PyPI：https://pypi.org/project/outlines/
- 🦀 Rust 核心：https://github.com/dottxt-ai/outlines-core
- 🔗 LangChain 整合：https://python.langchain.com/docs/integrations/providers/outlines/

## 💡 使用建議

### 何時使用 Instructor
- 需要強大的型別安全和驗證
- 使用 Pydantic 進行資料建模
- 需要自動重試機制
- 快速、以 schema 為先的資料提取

### 何時使用 Outlines
- 需要保證輸出格式（如有效 JSON、XML）
- 使用正則表達式或文法約束
- 需要高效能的結構化生成
- 希望提供商獨立的解決方案

### 兩者結合
可以同時使用兩個框架：
- Outlines 用於生成階段的約束
- Instructor 用於後處理和驗證
- 根據具體需求選擇最適合的工具

## 🎯 快速開始

```python
# Instructor 範例
import instructor
from openai import OpenAI
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

client = instructor.from_openai(OpenAI())
user = client.chat.completions.create(
    model="gpt-4",
    response_model=User,
    messages=[{"role": "user", "content": "Extract: John is 30 years old"}]
)
print(user)  # User(name='John', age=30)
```

```python
# Outlines 範例
import outlines

model = outlines.models.openai("gpt-4")
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"}
    }
}

generator = outlines.generate.json(model, schema)
result = generator("Extract: John is 30 years old")
print(result)  # {"name": "John", "age": 30}
```

## 📝 注意事項

1. **API 金鑰**：所有範例都需要設定相應的 API 金鑰（OpenAI、Anthropic 等）
2. **環境變數**：建議使用 `.env` 檔案管理 API 金鑰
3. **成本控制**：注意 API 呼叫成本，特別是使用重試機制時
4. **版本兼容**：確保使用最新版本以獲得最佳功能和效能
5. **錯誤處理**：生產環境中務必實作完善的錯誤處理

## 🔄 更新日誌

- **2025-12-15**：創建初始範例集
- 包含 Instructor 1.13.0 和 Outlines 最新版本
- 所有範例已測試並包含詳細中文註解

## 📚 學習路徑

建議按以下順序學習：

1. **基礎入門**：01 → 05（了解兩個框架的基本用法）
2. **深入功能**：02 → 03 → 06 → 07（學習驗證和約束）
3. **實用技巧**：04 → 08 → 09（掌握重試、多模型、串流）
4. **進階應用**：10（優化和生產環境實踐）

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request 來改進這些範例！

## 📄 授權

本範例集採用 MIT 授權。

---

**最後更新：2025-12-15**
