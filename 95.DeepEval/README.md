# DeepEval - LLM 評估框架

## 簡介

DeepEval 是一個全面的 LLM（大型語言模型）評估框架，專為評估和測試 LLM 應用而設計。它提供了豐富的評估指標、單元測試集成和 CI/CD 支持，是構建可靠 AI 應用的重要工具。

## 核心特性

### 1. **豐富的評估指標**
- 答案相關性（Answer Relevancy）
- 忠實度（Faithfulness）
- 上下文相關性（Contextual Relevancy）
- 幻覺檢測（Hallucination）
- 毒性檢測（Toxicity）
- 偏見檢測（Bias）

### 2. **單元測試集成**
- 與 pytest 無縫整合
- 類似傳統軟件測試的體驗
- 自動化測試流程
- 清晰的斷言語法

### 3. **紅隊測試**
- 自動生成對抗性測試用例
- 測試模型魯棒性
- 發現潛在漏洞
- 提高系統安全性

### 4. **CI/CD 整合**
- 支持持續集成
- 自動化評估流程
- 性能回歸檢測
- 質量門控

## 安裝

```bash
pip install deepeval openai
```

## 主要組件

### 評估指標

1. **Answer Relevancy（答案相關性）**
   - 評估答案與問題的相關程度
   - 檢測離題回答

2. **Faithfulness（忠實度）**
   - 評估答案是否忠實於上下文
   - 檢測幻覺和虛假信息

3. **Contextual Relevancy（上下文相關性）**
   - 評估檢索上下文的相關性
   - 優化檢索質量

4. **Hallucination（幻覺檢測）**
   - 專門檢測 AI 幻覺
   - 識別虛構的信息

5. **Toxicity（毒性檢測）**
   - 檢測有害內容
   - 確保輸出安全

6. **Bias（偏見檢測）**
   - 識別性別、種族等偏見
   - 促進公平性

## 使用場景

### 1. **LLM 應用開發**
- 快速評估原型
- 對比不同模型
- 優化提示詞

### 2. **質量保證**
- 單元測試
- 集成測試
- 回歸測試

### 3. **安全性測試**
- 紅隊測試
- 對抗性評估
- 漏洞發現

### 4. **持續集成**
- 自動化評估
- 性能監控
- 質量門控

## 示例代碼結構

本目錄包含 10 個完整示例：

1. **01_快速開始.py** - DeepEval 基礎入門
2. **02_單元測試.py** - 使用 pytest 進行單元測試
3. **03_相關性測試.py** - 答案相關性評估
4. **04_幻覺檢測.py** - 檢測 AI 幻覺
5. **05_毒性測試.py** - 檢測有害內容
6. **06_偏見檢測.py** - 檢測模型偏見
7. **07_自定義指標.py** - 創建自定義評估指標
8. **08_紅隊測試.py** - 對抗性測試
9. **09_CI整合.py** - CI/CD 整合示例
10. **10_儀表板.py** - 評估結果可視化

## 快速開始

```python
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric

# 創建測試用例
test_case = LLMTestCase(
    input="什麼是機器學習？",
    actual_output="機器學習是人工智慧的一個分支...",
    retrieval_context=["機器學習讓計算機從數據中學習..."]
)

# 創建指標
metric = AnswerRelevancyMetric(threshold=0.7)

# 執行評估
metric.measure(test_case)
assert_test(test_case, [metric])
```

## 單元測試示例

```python
import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric

@pytest.mark.parametrize(
    "input,output",
    [
        ("什麼是 Python？", "Python 是一種編程語言"),
        ("如何學習 AI？", "可以從基礎數學開始學習"),
    ]
)
def test_answer_relevancy(input, output):
    test_case = LLMTestCase(input=input, actual_output=output)
    metric = AnswerRelevancyMetric(threshold=0.7)
    assert_test(test_case, [metric])
```

## 最佳實踐

### 1. **選擇合適的指標**
- 根據應用場景選擇
- 結合多個指標評估
- 設定合理的閾值

### 2. **編寫測試用例**
- 覆蓋典型場景
- 包含邊界情況
- 測試負面案例

### 3. **自動化測試**
- 整合到 CI/CD
- 定期運行測試
- 監控性能變化

### 4. **持續優化**
- 收集失敗案例
- 分析問題根源
- 迭代改進系統

## 與 Ragas 的區別

| 特性 | DeepEval | Ragas |
|-----|----------|-------|
| 主要用途 | LLM 應用測試 | RAG 系統評估 |
| 測試集成 | pytest 集成 | 獨立評估 |
| 紅隊測試 | ✓ 支持 | ✗ 不支持 |
| CI/CD | ✓ 原生支持 | 需要自行整合 |
| 毒性檢測 | ✓ 內置 | ✗ 無 |
| 偏見檢測 | ✓ 內置 | ✗ 無 |

## 進階功能

### 自定義指標
創建特定領域的評估指標

### 批量評估
高效處理大量測試數據

### 報告生成
生成詳細的評估報告

### 儀表板
可視化評估結果和趨勢

## 性能優化建議

1. **並行測試** - 使用 pytest-xdist 並行執行
2. **緩存結果** - 避免重複評估
3. **採樣測試** - 在開發階段使用採樣
4. **增量測試** - 只測試變更部分

## 常見問題

### Q: DeepEval 需要什麼依賴？
A: 主要需要 Python 3.7+、OpenAI API（或其他 LLM）。

### Q: 如何處理 API 成本？
A: 使用緩存、採樣測試、本地模型等方法降低成本。

### Q: 可以用於哪些 LLM？
A: 支持 OpenAI、Anthropic、本地模型等多種 LLM。

### Q: 如何在 CI 中使用？
A: 配置 GitHub Actions 或其他 CI 工具運行 pytest 測試。

## 相關資源

- 官方文檔: https://docs.confident-ai.com/
- GitHub: https://github.com/confident-ai/deepeval
- 社區論壇: https://discord.gg/deepeval

## 與傳統測試的對比

DeepEval 將 LLM 評估帶入了傳統軟件測試的範式：

```python
# 傳統測試
def test_addition():
    assert add(2, 3) == 5

# LLM 測試（使用 DeepEval）
def test_answer_quality():
    test_case = LLMTestCase(...)
    assert_test(test_case, [metric])
```

## 總結

DeepEval 是評估 LLM 應用的強大工具，特別適合：

- 需要單元測試的 LLM 應用
- 要求高質量和安全性的系統
- CI/CD 自動化流程
- 紅隊測試和安全評估

通過本目錄的示例，您可以快速掌握 DeepEval 的使用，構建更可靠的 AI 應用。
