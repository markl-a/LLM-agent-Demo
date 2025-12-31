# 貢獻指南

感謝你對 LLM Agent Demo 專案的興趣！我們歡迎各種形式的貢獻。

## 目錄

- [行為準則](#行為準則)
- [如何貢獻](#如何貢獻)
- [開發環境設置](#開發環境設置)
- [代碼風格指南](#代碼風格指南)
- [提交 Pull Request](#提交-pull-request)
- [報告 Bug](#報告-bug)
- [建議新功能](#建議新功能)

## 行為準則

本專案採用 [Contributor Covenant](https://www.contributor-covenant.org/) 行為準則。參與本專案即表示你同意遵守其條款。

## 如何貢獻

你可以通過以下方式為專案做出貢獻：

- 📝 改進文檔
- 🐛 報告和修復 Bug
- ✨ 提出新功能建議
- 💡 添加新的教程或範例
- 🔍 改進代碼品質
- 🧪 增加測試覆蓋率
- 🌐 翻譯文檔到其他語言

## 開發環境設置

### 1. Fork 並克隆倉庫

```bash
# Fork 專案到你的 GitHub 帳號
# 然後克隆到本地
git clone https://github.com/YOUR_USERNAME/LLM-agent-Demo.git
cd LLM-agent-Demo
```

### 2. 創建虛擬環境

```bash
# 使用 venv
python -m venv venv

# 啟動虛擬環境
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. 安裝依賴

```bash
# 安裝專案依賴
pip install -r requirements.txt

# 安裝開發工具
pip install pre-commit black flake8 mypy pytest pytest-cov ruff isort
```

### 4. 設置 Pre-commit Hooks

Pre-commit hooks 會在每次 commit 前自動運行代碼檢查和格式化。

```bash
# 安裝 pre-commit hooks
pre-commit install

# (可選) 對所有文件運行一次
pre-commit run --all-files

# 手動運行特定 hook
pre-commit run black --all-files
pre-commit run flake8 --all-files
```

**Pre-commit 配置說明**（`.pre-commit-config.yaml`）：

```yaml
repos:
  # 代碼格式化
  - repo: https://github.com/psf/black
    hooks:
      - id: black
        args: ['--line-length=100']

  # 導入排序
  - repo: https://github.com/pycqa/isort
    hooks:
      - id: isort
        args: ['--profile=black']

  # 代碼檢查
  - repo: https://github.com/pycqa/flake8
    hooks:
      - id: flake8
        args: ['--max-line-length=100', '--extend-ignore=E203,W503']

  # Markdown 檢查
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

**跳過 Pre-commit**（不推薦）：

```bash
# 緊急情況下可以跳過
git commit --no-verify -m "message"
```

### 5. 配置環境變數

```bash
# 複製範例環境文件
cp .env.example .env

# 編輯 .env 添加你的 API Keys
nano .env  # 或使用你喜歡的編輯器
```

## 代碼風格指南

### Python 代碼

我們使用以下工具來保持代碼品質：

- **Black**: 代碼格式化（行長度：100）
- **isort**: 導入排序
- **Flake8**: 代碼檢查
- **Ruff**: 快速 linting
- **mypy**: 類型檢查

### 代碼風格要求

#### 基本規範

1. **行長度**: 最大 100 字符（由 Black 自動處理）
2. **縮進**: 使用 4 個空格
3. **引號**: 優先使用雙引號
4. **命名規範**:
   - 變量/函數: `snake_case`
   - 類: `PascalCase`
   - 常量: `UPPER_SNAKE_CASE`
   - 私有成員: `_leading_underscore`

#### 代碼示例

```python
# ✅ 好的範例
def calculate_embedding(
    text: str,
    model: str = "text-embedding-ada-002",
    temperature: float = 0.0
) -> list[float]:
    """
    計算文本的嵌入向量。

    Args:
        text: 要處理的文本
        model: 使用的嵌入模型名稱
        temperature: 模型溫度參數

    Returns:
        嵌入向量列表

    Raises:
        ValueError: 當文本為空時
        APIError: 當 API 調用失敗時

    Example:
        >>> embedding = calculate_embedding("Hello world")
        >>> len(embedding)
        1536
    """
    if not text:
        raise ValueError("文本不能為空")

    try:
        # 調用 API 獲取嵌入
        response = openai.Embedding.create(
            input=text,
            model=model
        )
        return response["data"][0]["embedding"]
    except Exception as e:
        raise APIError(f"API 調用失敗: {e}")


# ❌ 不好的範例
def calc_emb(t,m="text-embedding-ada-002"):
    if not t:raise ValueError("文本不能為空")
    return []
```

#### 類型提示

強烈建議使用類型提示：

```python
from typing import Optional, Union, List, Dict

def process_documents(
    docs: List[str],
    config: Optional[Dict[str, any]] = None
) -> Union[List[str], None]:
    """處理文檔列表"""
    if config is None:
        config = {}
    # ...
```

#### 錯誤處理

```python
# ✅ 明確的錯誤處理
try:
    result = llm.invoke(prompt)
except RateLimitError:
    logger.warning("達到速率限制，等待重試...")
    time.sleep(60)
    result = llm.invoke(prompt)
except Exception as e:
    logger.error(f"LLM 調用失敗: {e}")
    raise

# ❌ 過於寬泛的異常捕獲
try:
    result = llm.invoke(prompt)
except:  # 不要這樣做
    pass
```

### 文檔字串（Docstring）

使用 Google 風格的 docstring：

```python
def function_with_docstring(param1: str, param2: int) -> bool:
    """
    函數的簡短描述。

    更詳細的描述（如果需要的話）。

    Args:
        param1: 第一個參數的描述
        param2: 第二個參數的描述

    Returns:
        返回值的描述

    Raises:
        ValueError: 何時會拋出此異常

    Example:
        >>> function_with_docstring("test", 42)
        True
    """
    pass
```

### Markdown 文檔

- 行寬限制在 100 字符（中文除外）
- 使用一致的標題層級
- 代碼塊要指定語言
- 列表項使用 `-` 而不是 `*`

### Jupyter Notebook

- 保持 cells 簡潔，一個 cell 做一件事
- 添加 Markdown cells 解釋代碼
- 提交前清除輸出（pre-commit 會自動處理）
- 確保 notebook 可以從頭到尾運行

## 提交 Pull Request

### 1. 創建新分支

```bash
# 從 main 創建新分支
git checkout -b feature/your-feature-name

# 或者修復 bug
git checkout -b fix/bug-description
```

### 2. 進行更改

- 保持提交小而專注
- 編寫清晰的提交消息
- 遵循代碼風格指南

### 3. 運行測試

#### 基本測試命令

```bash
# 運行所有測試
pytest

# 運行特定測試
pytest tests/test_basic.py

# 運行特定測試函數
pytest tests/test_basic.py::test_function_name

# 顯示詳細輸出
pytest -v

# 顯示 print 輸出
pytest -s
```

#### 代碼覆蓋率

```bash
# 檢查代碼覆蓋率
pytest --cov=. --cov-report=html

# 生成覆蓋率報告
pytest --cov=src --cov-report=term-missing

# 要求最低覆蓋率
pytest --cov=src --cov-fail-under=80
```

#### 測試要求

**必須測試的內容**：

1. **核心功能**
   - 主要函數的正常流程
   - 邊界條件
   - 錯誤處理

2. **集成測試**
   - API 調用（使用 mock）
   - 數據庫操作
   - 文件 I/O

3. **示例代碼**
   - 確保所有示例可運行
   - 驗證輸出格式
   - 檢查錯誤處理

**測試示例**：

```python
import pytest
from unittest.mock import Mock, patch

def test_calculate_embedding():
    """測試嵌入計算"""
    # Arrange
    text = "Hello world"
    expected_length = 1536

    # Act
    with patch('openai.Embedding.create') as mock_create:
        mock_create.return_value = {
            "data": [{"embedding": [0.1] * expected_length}]
        }
        result = calculate_embedding(text)

    # Assert
    assert len(result) == expected_length
    mock_create.assert_called_once()


def test_calculate_embedding_empty_text():
    """測試空文本錯誤處理"""
    with pytest.raises(ValueError, match="文本不能為空"):
        calculate_embedding("")


@pytest.fixture
def sample_documents():
    """測試數據 fixture"""
    return [
        "Document 1",
        "Document 2",
        "Document 3"
    ]


def test_process_documents(sample_documents):
    """測試文檔處理"""
    result = process_documents(sample_documents)
    assert len(result) == 3
```

**測試覆蓋率目標**：

- 核心功能: 90%+
- 工具函數: 80%+
- 示例代碼: 基本可運行性測試

**持續集成**：

所有 Pull Request 必須通過 CI 測試：
- 所有測試通過
- 代碼覆蓋率達標
- Lint 檢查通過
- 類型檢查通過

### 4. 檢查代碼品質

```bash
# 格式化代碼
black .
isort .

# 檢查代碼
flake8 .
ruff check .
mypy .

# 或者讓 pre-commit 自動運行
pre-commit run --all-files
```

### 5. 提交更改

```bash
git add .
git commit -m "描述你的更改"

# 推送到你的 fork
git push origin feature/your-feature-name
```

### 6. 創建 Pull Request

1. 前往 GitHub 上的原始倉庫
2. 點擊 "New Pull Request"
3. 選擇你的分支
4. 填寫 PR 模板
5. 提交 PR

### Pull Request 檢查清單

- [ ] 代碼遵循專案的風格指南
- [ ] 已添加/更新測試
- [ ] 所有測試通過
- [ ] 已更新相關文檔
- [ ] 提交消息清晰明確
- [ ] 已運行 pre-commit hooks
- [ ] PR 描述清楚說明了更改內容

## 報告 Bug

### 在提交 Bug 報告前

1. 檢查是否已有相似的 issue
2. 確認你使用的是最新版本
3. 收集相關信息（錯誤消息、堆棧跟踪等）

### Bug 報告應包含

- **描述**: 清楚簡潔的 bug 描述
- **重現步驟**: 詳細的重現步驟
- **預期行為**: 你期望發生什麼
- **實際行為**: 實際發生了什麼
- **環境信息**:
  - Python 版本
  - 操作系統
  - 相關依賴版本
- **截圖/日誌**: 如果適用

### Bug 報告模板

```markdown
**描述 Bug**
[清楚簡潔的描述]

**重現步驟**
1. 執行 '...'
2. 運行 '...'
3. 看到錯誤

**預期行為**
[描述你期望的結果]

**實際行為**
[描述實際發生的情況]

**環境**
- Python 版本: [例如 3.11]
- OS: [例如 Ubuntu 22.04]
- 相關庫版本: [例如 langchain==1.0.0]

**額外信息**
[任何其他相關信息]
```

## 建議新功能

我們歡迎新功能建議！請創建一個 issue 並包含：

- **功能描述**: 清楚描述建議的功能
- **動機**: 為什麼這個功能有用
- **可能的實現**: 你認為如何實現（可選）
- **替代方案**: 你考慮過的其他方案（可選）

## 添加新教程

如果你想添加新的教程或範例：

1. 確保主題尚未被覆蓋
2. 在相應的目錄下創建文件
3. 添加清晰的說明和註解
4. 包含可運行的範例代碼
5. 更新主 README.md（如果需要）

### 教程結構建議

```
your-tutorial/
├── README.md           # 概述和使用說明
├── 0.introduction.ipynb  # 介紹
├── 1.basic_example.ipynb # 基礎範例
├── 2.advanced_example.ipynb # 進階範例
└── data/              # 範例數據（如需要）
```

## 代碼審查流程

1. **自動檢查**: CI/CD 會自動運行測試和代碼檢查
2. **人工審查**: 維護者會審查你的代碼
3. **反饋**: 可能會要求進行修改
4. **合併**: 通過審查後會被合併

## 許可證

通過貢獻，你同意你的貢獻將在 [MIT License](LICENSE) 下授權。

## 需要幫助？

如果你有任何問題，可以：

- 創建一個 [Discussion](https://github.com/yourusername/LLM-agent-Demo/discussions)
- 在 [Issues](https://github.com/yourusername/LLM-agent-Demo/issues) 中提問
- 查看現有的文檔和範例

## 致謝

感謝所有為本專案做出貢獻的人！你的努力讓這個專案變得更好。

---

再次感謝你的貢獻！🎉
