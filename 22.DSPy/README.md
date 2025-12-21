# DSPy - Stanford LLM 編程框架

## 簡介

DSPy (Declarative Self-improving Python) 是由 Stanford NLP 開發的革命性 LLM 編程框架。與傳統的提示工程不同，DSPy 將語言模型視為可編程的組件，允許開發者編寫模塊化的 Python 代碼，並使用優化算法自動調整提示和權重。

**核心理念：編程，而非提示工程**

DSPy 的設計哲學類似於 PyTorch 在神經網絡領域的地位，它將 LLM 應用開發從手動調整提示詞轉變為系統化的編程範式。

## 主要特點

### 1. 聲明式編程
- **Signatures（簽名）**：使用簡潔的字符串聲明模型的輸入輸出規範
  - 例如：`"question -> answer"` 或 `"context, question -> reasoning, response"`
  - 讓框架自動生成和優化提示詞

### 2. 模塊化架構
- **內置模塊**：
  - `dspy.Predict`：基礎預測模塊
  - `dspy.ChainOfThought`：思維鏈推理
  - `dspy.ReAct`：推理-行動代理模式
  - `dspy.Refine`：迭代優化輸出
  - `dspy.BestOfN`：多次採樣選擇最佳結果

- **自定義模塊**：類似 PyTorch，繼承 `dspy.Module` 並實現 `forward()` 方法

### 3. 自動優化器
- **BootstrapFewShot**：使用教師模型生成少樣本示範
- **MIPROv2**：結合貝葉斯優化和數據感知的指令生成
- **GEPA**：基於反思的提示演化優化
- **SIMBA**：使用隨機小批次採樣識別困難樣本

### 4. 多模型支持
- 通過 LiteLLM 集成，支持 100+ 種語言模型提供商
- 包括 OpenAI、Anthropic、Cohere、本地模型等
- 統一的 `dspy.LM` 接口

### 5. 檢索增強生成（RAG）
- 內置 RAG 支持，可輕鬆整合檢索系統
- 支持向量數據庫如 Weaviate、Pinecone 等
- 多跳推理和複雜查詢鏈

## 三層架構

DSPy 採用清晰的三層架構設計：

1. **核心編程模型層**：面向用戶的抽象，用於定義任務和組合程序
2. **執行層**：運行時基礎設施，處理 LM 交互、提示格式化和響應解析
3. **優化層**：通過基於軌跡的學習算法自動改進程序

## 安裝方式

### 基本安裝

```bash
# 使用 pip 安裝穩定版本
pip install dspy-ai

# 或者
pip install dspy
```

### 從 GitHub 安裝最新版本

```bash
# 安裝最新的開發版本
pip install -U git+https://github.com/stanfordnlp/dspy.git@main
```

### 系統要求

- Python 3.10 或更高版本（支持到 Python 3.13）
- 最新穩定版本：v3.0.4（2025年11月發布）

## 快速開始

```python
import dspy

# 配置語言模型
lm = dspy.LM('openai/gpt-4o-mini', api_key='your-api-key')
dspy.configure(lm=lm)

# 定義簽名
class QuestionAnswer(dspy.Signature):
    """回答用戶問題"""
    question = dspy.InputField()
    answer = dspy.OutputField()

# 使用模塊
predictor = dspy.Predict(QuestionAnswer)
response = predictor(question="什麼是 DSPy？")
print(response.answer)
```

## 核心概念詳解

### Signatures（簽名）

簽名是 DSPy 的核心抽象，聲明式地定義模型應完成什麼任務：

```python
# 簡短字符串形式
"question -> answer"
"sentence -> sentiment: bool"
"question, choices: list[str] -> reasoning: str, selection: int"

# 類形式
class MySignature(dspy.Signature):
    """任務描述"""
    input_field = dspy.InputField(desc="輸入描述")
    output_field = dspy.OutputField(desc="輸出描述")
```

### Modules（模塊）

模塊封裝了特定的提示技術：

```python
# 基礎預測
predict = dspy.Predict("question -> answer")

# 思維鏈推理
cot = dspy.ChainOfThought("question -> answer")

# ReAct 代理
react = dspy.ReAct("question -> answer", tools=[...])
```

### Optimizers（優化器）

優化器自動改進程序性能：

```python
from dspy.teleprompt import BootstrapFewShot

# 定義評估指標
def validate_answer(example, prediction):
    return example.answer.lower() in prediction.answer.lower()

# 優化程序
optimizer = BootstrapFewShot(metric=validate_answer)
optimized_program = optimizer.compile(
    student=my_program,
    trainset=train_data
)
```

## 應用場景

1. **問答系統**：構建智能問答應用
2. **RAG 流程**：實現檢索增強生成
3. **代理系統**：開發 ReAct 風格的智能代理
4. **文本分類**：情感分析、主題分類等
5. **複雜推理**：多跳推理、數學問題求解
6. **代碼生成**：自動化編程任務

## 優勢對比

### DSPy vs 傳統提示工程

| 特性 | 傳統提示工程 | DSPy |
|------|-------------|------|
| 開發方式 | 手動調整提示詞 | 編寫 Python 程序 |
| 優化方法 | 人工試錯 | 自動優化算法 |
| 可維護性 | 脆弱，難以維護 | 模塊化，易於維護 |
| 可組合性 | 有限 | 高度可組合 |
| 性能優化 | 需要大量手動工作 | 自動化優化 |

### DSPy vs LangChain/LlamaIndex

- **DSPy**：專注於自動優化和編程範式
- **LangChain**：專注於鏈式組合和工具集成
- **LlamaIndex**：專注於數據索引和檢索

DSPy 可以與這些框架配合使用，各有側重。

## 研究與社區

- **研發團隊**：Stanford NLP（領導者：Omar Khattab, Chris Potts, Matei Zaharia）
- **開源貢獻者**：250+ 貢獻者
- **用戶規模**：數萬名開發者使用
- **起源時間**：2022年2月開始研究，2023年10月發布 DSPy

### 最新研究成果（2024-2025）

- **GEPA**：反思式提示演化（2025年7月）
- **多階段程序優化**：優化指令和示範（2024年6月）
- **微調與提示優化結合**：兩步法優化（2024年7月）

## 範例文件說明

本資料夾包含 10 個詳細的 Python 範例：

1. **01_快速開始.py** - DSPy 基礎使用，配置和簡單預測
2. **02_Signature定義.py** - 多種簽名定義方式和最佳實踐
3. **03_Module構建.py** - 創建自定義模塊
4. **04_優化器使用.py** - 使用各種優化器提升性能
5. **05_檢索增強.py** - 實現 RAG 系統
6. **06_ChainOfThought.py** - 思維鏈推理技術
7. **07_ReAct模式.py** - 構建 ReAct 代理
8. **08_評估系統.py** - 評估和測試程序
9. **09_多模型支持.py** - 配置和使用多個 LLM
10. **10_進階技巧.py** - 高級用法和最佳實踐

## 資源鏈接

- **官方網站**：[https://dspy.ai](https://dspy.ai)
- **GitHub 倉庫**：[https://github.com/stanfordnlp/dspy](https://github.com/stanfordnlp/dspy)
- **文檔**：[https://dspy.ai/learn](https://dspy.ai/learn)
- **DeepLearning.AI 課程**：[DSPy: Build and Optimize Agentic Apps](https://learn.deeplearning.ai/courses/dspy-build-optimize-agentic-apps)

## 學習建議

1. **從基礎開始**：先理解 Signatures 和基本的 Predict 模塊
2. **逐步進階**：學習 ChainOfThought、ReAct 等高級模塊
3. **實踐優化**：嘗試使用優化器改進程序性能
4. **構建項目**：將學到的技術應用到實際項目中
5. **參與社區**：加入 Discord 社區，與其他開發者交流

## 注意事項

- 需要設置相應的 API 密鑰（如 `OPENAI_API_KEY`）
- 某些功能需要訪問外部服務（如檢索系統）
- 優化過程可能需要較多的 API 調用，注意成本控制
- Assertions 功能已在 DSPy 2.6+ 版本中棄用，改用 `dspy.Refine` 和 `dspy.Suggest`

## 貢獻與反饋

DSPy 是一個活躍的開源項目，歡迎貢獻代碼、報告問題或分享使用經驗。

---

**最後更新**：2025年12月
**DSPy 版本**：3.0.4
**作者**：Stanford NLP & 開源社區
