# AI 程式碼助手

基於 LangChain 構建的智能代碼輔助系統，提供代碼分析、生成、調試、審查等全方位支持。

## 功能特點

### 1. 代碼解釋 (Explain)
- 清晰解釋代碼的功能和邏輯
- 識別關鍵概念和設計模式
- 通俗易懂的語言，適合學習

### 2. 代碼生成 (Generate)
- 根據自然語言描述生成代碼
- 支持多種程式語言
- 自動包含註釋和文檔
- 可選生成單元測試

### 3. 代碼調試 (Debug)
- 診斷錯誤的根本原因
- 提供詳細的修復方案
- 預防類似問題的建議

### 4. 代碼審查 (Review)
- 全面的代碼質量評估
- 檢測潛在 Bug 和安全漏洞
- 性能和風格問題分析
- 具體的改進建議

### 5. 重構建議 (Refactor)
- 識別代碼異味
- 提供重構方案
- 應用設計模式
- 提高代碼質量

### 6. 文檔生成 (Document)
- 自動生成完整文檔
- 包含參數說明和使用範例
- Markdown 格式輸出

### 7. 性能優化 (Optimize)
- 分析性能瓶頸
- 優化算法和數據結構
- 提升代碼效率

## 支持的語言

- Python
- JavaScript / TypeScript
- Java
- C / C++
- Go
- Rust
- 以及更多...

## 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 配置環境

```bash
export OPENAI_API_KEY='your-openai-api-key'
```

### 3. 運行助手

```bash
python main.py
```

## 使用指南

### 互動式模式

運行程序後，您會看到功能選單：

```
============================================================
🤖 AI 程式碼助手
============================================================

可用功能：
1. 解釋代碼 (explain)
2. 生成代碼 (generate)
3. 調試代碼 (debug)
4. 代碼審查 (review)
5. 重構建議 (refactor)
6. 生成文檔 (document)
7. 性能優化 (optimize)
8. 設置當前代碼 (set-code)
9. 顯示當前代碼 (show-code)
0. 退出 (quit)
============================================================
```

### 使用範例

#### 範例 1：解釋代碼

```
請選擇功能: 1

請輸入要解釋的代碼 (輸入 END 結束):
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
END

🔍 正在分析代碼...

============================================================
📖 代碼解釋:
============================================================
這段代碼實現了斐波那契數列的計算。

主要功能：
計算斐波那契數列的第 n 項。斐波那契數列是一個經典的數學序列，
每一項都是前兩項的和（0, 1, 1, 2, 3, 5, 8, 13...）。

邏輯解釋：
1. 基礎情況：當 n 小於等於 1 時，直接返回 n
   - fibonacci(0) = 0
   - fibonacci(1) = 1

2. 遞迴情況：對於 n > 1，返回前兩項的和
   - fibonacci(n) = fibonacci(n-1) + fibonacci(n-2)

重要概念：
- 遞迴：函數調用自己來解決問題
- 基礎情況：遞迴的終止條件

注意事項：
這個實現雖然直觀，但效率較低。對於較大的 n，會產生大量
重複計算。建議使用動態規劃或記憶化來優化。
============================================================
```

#### 範例 2：生成代碼

```
請選擇功能: 2

請描述您需要的功能:
實現一個函數，檢查一個字符串是否是迴文

目標語言 (默認 python): python

是否包含測試? (y/n, 默認 n): y

⚙️ 正在生成代碼...

============================================================
✨ 生成的代碼:
============================================================
```python
def is_palindrome(s: str) -> bool:
    """
    檢查字符串是否為迴文

    迴文是指正讀和反讀都相同的字符串，如 "radar", "level"

    Args:
        s: 要檢查的字符串

    Returns:
        如果是迴文返回 True，否則返回 False
    """
    # 移除空格並轉換為小寫，使比較更準確
    cleaned = ''.join(s.split()).lower()

    # 比較字符串與其反轉
    return cleaned == cleaned[::-1]


# 單元測試
import unittest

class TestPalindrome(unittest.TestCase):
    def test_simple_palindrome(self):
        self.assertTrue(is_palindrome("radar"))
        self.assertTrue(is_palindrome("level"))

    def test_with_spaces(self):
        self.assertTrue(is_palindrome("A man a plan a canal Panama"))

    def test_not_palindrome(self):
        self.assertFalse(is_palindrome("hello"))
        self.assertFalse(is_palindrome("world"))

    def test_empty_string(self):
        self.assertTrue(is_palindrome(""))

    def test_single_character(self):
        self.assertTrue(is_palindrome("a"))

if __name__ == '__main__':
    unittest.main()
\```

============================================================

是否保存為當前代碼? (y/n): y
✅ 已保存為當前代碼
```

#### 範例 3：代碼審查

```
請選擇功能: 4

📋 正在進行代碼審查...

============================================================
📊 代碼審查報告
============================================================

總體評分: 75/100

✅ 優點:
  - 代碼邏輯清晰易懂
  - 包含文檔字符串
  - 使用類型提示

⚠️ 缺點:
  - 遞迴深度可能導致堆棧溢出
  - 時間複雜度較高（O(2^n)）
  - 缺少輸入驗證

🐛 潛在 Bug:
  - 負數輸入會導致無限遞迴

⚡ 性能問題:
  - 存在大量重複計算
  - 建議使用動態規劃或記憶化

💡 建議:
  - 添加輸入驗證
  - 使用 @lru_cache 裝飾器優化性能
  - 考慮使用迭代方法替代遞迴
  - 添加單元測試
============================================================
```

#### 範例 4：性能優化

```
請選擇功能: 7

⚡ 正在分析性能優化機會...

============================================================
🚀 性能優化建議:
============================================================

性能瓶頸分析：

當前實現使用簡單遞迴，時間複雜度為 O(2^n)，空間複雜度為 O(n)。
對於 fibonacci(40) 需要計算約 2億次。

優化建議：

1. 使用記憶化 (Memoization)
   - 緩存已計算的結果
   - 時間複雜度降至 O(n)

2. 使用動態規劃
   - 自底向上計算
   - 避免遞迴開銷

3. 使用矩陣快速冪
   - 時間複雜度降至 O(log n)

優化後的代碼：

```python
from functools import lru_cache

# 方法1：記憶化
@lru_cache(maxsize=None)
def fibonacci_memo(n: int) -> int:
    """使用記憶化優化的斐波那契"""
    if n <= 1:
        return n
    return fibonacci_memo(n-1) + fibonacci_memo(n-2)

# 方法2：動態規劃
def fibonacci_dp(n: int) -> int:
    """使用動態規劃的斐波那契"""
    if n <= 1:
        return n

    # 只需保存前兩個值
    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr

    return curr

# 方法3：矩陣快速冪（最優）
def fibonacci_matrix(n: int) -> int:
    """使用矩陣快速冪的斐波那契 - O(log n)"""
    def matrix_multiply(a, b):
        return [
            [a[0][0]*b[0][0] + a[0][1]*b[1][0],
             a[0][0]*b[0][1] + a[0][1]*b[1][1]],
            [a[1][0]*b[0][0] + a[1][1]*b[1][0],
             a[1][0]*b[0][1] + a[1][1]*b[1][1]]
        ]

    def matrix_power(mat, n):
        if n == 1:
            return mat
        if n % 2 == 0:
            half = matrix_power(mat, n // 2)
            return matrix_multiply(half, half)
        return matrix_multiply(mat, matrix_power(mat, n - 1))

    if n <= 1:
        return n

    result = matrix_power([[1, 1], [1, 0]], n)
    return result[0][1]
\```

性能提升預估：

| 方法 | 時間複雜度 | fibonacci(40) 耗時 |
|------|-----------|------------------|
| 原始遞迴 | O(2^n) | ~30秒 |
| 記憶化 | O(n) | <0.001秒 |
| 動態規劃 | O(n) | <0.001秒 |
| 矩陣快速冪 | O(log n) | <0.0001秒 |

建議：
- 對於一般使用，推薦記憶化方法（最簡單）
- 對於大量計算，推薦動態規劃（無遞迴開銷）
- 對於極大的 n，推薦矩陣快速冪（最快）
============================================================
```

## API 使用

### 基本使用

```python
from main import CodeAssistant

# 初始化助手
assistant = CodeAssistant(model="gpt-4o", temperature=0.3)

# 解釋代碼
code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
"""

explanation = assistant.explain_code(code)
print(explanation)

# 生成代碼
description = "實現快速排序算法"
code = assistant.generate_code(description, language="python")
print(code)

# 調試代碼
buggy_code = """
def divide(a, b):
    return a / b
"""
debug_result = assistant.debug_code(buggy_code)
print(debug_result)

# 代碼審查
review = assistant.review_code(code)
print(f"評分: {review.overall_score}")
print(f"優點: {review.strengths}")
print(f"建議: {review.recommendations}")
```

### 批量處理

```python
# 批量審查多個文件
import os
from pathlib import Path

assistant = CodeAssistant()

def review_directory(path: str):
    """審查目錄中的所有 Python 文件"""
    results = {}

    for file_path in Path(path).rglob("*.py"):
        with open(file_path, 'r') as f:
            code = f.read()

        review = assistant.review_code(code)
        results[str(file_path)] = review

    return results

# 使用
results = review_directory("./src")
for file, review in results.items():
    print(f"{file}: {review.overall_score}/100")
```

## 進階配置

### 自定義模型

```python
# 使用不同的模型
assistant = CodeAssistant(
    model="gpt-4",  # 更準確但較慢
    temperature=0.1  # 更確定性的輸出
)

# 或使用更快的模型
assistant = CodeAssistant(
    model="gpt-4o-mini",  # 更快但可能不太準確
    temperature=0.5
)
```

### 流式輸出

```python
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# 啟用流式輸出
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.3,
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)

assistant = CodeAssistant()
assistant.llm = llm
```

## 最佳實踐

### 1. 代碼解釋
- 提供完整的上下文
- 包含相關的導入語句
- 說明代碼的使用場景

### 2. 代碼生成
- 詳細描述需求
- 指定約束條件
- 說明預期的輸入輸出

### 3. 代碼調試
- 提供完整的錯誤信息
- 包含相關的上下文代碼
- 說明預期行為

### 4. 代碼審查
- 提供完整的函數或類
- 包含使用的依賴
- 說明代碼的用途

## 整合到 IDE

### VS Code 整合

創建 VS Code 任務：

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "AI Code Review",
      "type": "shell",
      "command": "python",
      "args": [
        "path/to/main.py",
        "review",
        "${file}"
      ],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    }
  ]
}
```

### Vim 整合

在 `.vimrc` 添加：

```vim
function! AICodeReview()
  let code = join(getline(1, '$'), "\n")
  let cmd = 'python path/to/main.py review'
  execute '!' . cmd
endfunction

command! AIReview call AICodeReview()
```

## 常見問題

### Q1: 如何提高生成代碼的質量？

1. 提供更詳細的需求描述
2. 指定具體的約束條件
3. 說明預期的邊界情況
4. 使用更高級的模型（gpt-4）

### Q2: 審查結果如何解讀？

- 評分 90+: 優秀，可以直接使用
- 評分 70-89: 良好，需要小幅改進
- 評分 50-69: 一般，需要重要改進
- 評分 <50: 需要重新設計

### Q3: 如何處理大型代碼文件？

使用代碼分割：

```python
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=1000,
    chunk_overlap=100
)

chunks = splitter.split_text(large_code)

# 分別審查每個塊
for chunk in chunks:
    review = assistant.review_code(chunk)
```

## 性能考慮

### API 成本估算

| 操作 | 平均 Token | 成本 (GPT-4) | 成本 (GPT-4o) |
|------|-----------|-------------|--------------|
| 解釋代碼 | 1500 | ~$0.03 | ~$0.015 |
| 生成代碼 | 2000 | ~$0.04 | ~$0.02 |
| 代碼審查 | 2500 | ~$0.05 | ~$0.025 |
| 重構建議 | 3000 | ~$0.06 | ~$0.03 |

### 優化建議

1. 使用緩存避免重複請求
2. 批量處理多個文件
3. 使用較小的模型處理簡單任務
4. 實現請求限流

## 擴展功能

### 1. 添加更多語言支持

```python
# 在 detect_language 方法中添加
if "package main" in code and "func" in code:
    return "go"
```

### 2. 集成靜態分析工具

```python
import pylint
import mypy

def enhanced_review(code):
    # AI 審查
    ai_review = assistant.review_code(code)

    # 靜態分析
    pylint_result = run_pylint(code)
    mypy_result = run_mypy(code)

    # 合併結果
    return combine_results(ai_review, pylint_result, mypy_result)
```

### 3. 添加代碼搜索

```python
def search_similar_code(code, codebase_path):
    """在代碼庫中搜索相似代碼"""
    # 使用向量相似度搜索
    ...
```

## 授權

MIT License

## 貢獻

歡迎提交 Issue 和 Pull Request！
