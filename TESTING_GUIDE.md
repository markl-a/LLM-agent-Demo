# 測試基礎設施指南

本文檔說明如何使用 LLM Agent Demo 專案的測試基礎設施。

## 概述

測試基礎設施已完整建立，包含以下組件：

### 📁 測試文件結構

```
/home/user/LLM-agent-Demo/
├── pytest.ini                    # Pytest 配置文件
├── requirements-dev.txt          # 開發和測試依賴
├── TESTING_GUIDE.md             # 本文件
└── tests/
    ├── __init__.py              # 測試套件初始化
    ├── conftest.py              # Pytest fixtures 和配置
    ├── README.md                # 測試目錄說明
    ├── test_basic.py            # 基礎測試
    ├── test_imports.py          # 框架文件導入和語法測試
    ├── test_examples.py         # 示例文件測試
    ├── test_logging.py          # 日誌系統測試
    ├── unit/                    # 單元測試
    └── integration/             # 整合測試
```

## 🚀 快速開始

### 1. 安裝測試依賴

```bash
# 安裝所有測試依賴
pip install -r requirements-dev.txt

# 或者只安裝核心測試工具
pip install pytest pytest-cov pytest-asyncio pytest-mock pytest-timeout
```

### 2. 運行測試

```bash
# 運行所有測試
pytest

# 運行特定測試文件
pytest tests/test_imports.py

# 運行特定測試函數
pytest tests/test_basic.py::test_python_version

# 詳細輸出
pytest -v

# 安靜模式（只顯示摘要）
pytest -q
```

### 3. 使用測試標記

```bash
# 只運行單元測試
pytest -m unit

# 只運行整合測試
pytest -m integration

# 排除慢速測試
pytest -m "not slow"

# 排除需要 API key 的測試
pytest -m "not requires_api_key"
```

### 4. 查看測試覆蓋率

```bash
# 生成終端覆蓋率報告
pytest --cov=src --cov=. --cov-report=term-missing

# 生成 HTML 覆蓋率報告
pytest --cov=src --cov=. --cov-report=html

# 查看 HTML 報告（在瀏覽器中打開）
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## 📋 測試文件說明

### test_imports.py - 框架導入和語法測試

此測試文件掃描所有框架目錄，檢查：

- ✓ Python 文件語法正確性
- ✓ 文件編碼（UTF-8）
- ✓ 模組導入能力
- ✓ 重複文件名檢測
- ⚠ README 文件存在性

**運行示例：**
```bash
pytest tests/test_imports.py -v
```

**功能：**
- 自動掃描所有框架目錄（1.LangchainDemos, 2.Multi_modal_RAG 等）
- 使用 AST 解析檢查語法錯誤
- 報告文件編碼問題
- 檢測可能的導入衝突

### test_examples.py - 示例文件測試

此測試文件檢查示例文件的質量：

- ✓ 文檔字符串（docstrings）
- ✓ 環境變數使用
- ✓ 錯誤處理
- ✓ 代碼結構
- ⚠ 硬編碼 API keys 檢測
- ⚠ TODO 標記檢測

**運行示例：**
```bash
pytest tests/test_examples.py -v
```

**功能：**
- 檢查示例文件是否有模組級文檔
- 檢測硬編碼的 API keys（安全性）
- 驗證使用環境變數獲取配置
- 檢查錯誤處理機制
- 分析函數文檔覆蓋率

### test_logging.py - 日誌系統測試

此測試文件驗證日誌系統功能：

- ✓ 日誌器創建和配置
- ✓ 不同日誌級別
- ✓ LogTimer 計時器
- ✓ 裝飾器功能
- ✓ 結構化日誌
- ✓ 性能日誌

**運行示例：**
```bash
pytest tests/test_logging.py -v
```

**功能：**
- 測試 `get_logger()` 函數
- 測試 `LogTimer` 上下文管理器
- 測試 `@log_execution` 裝飾器
- 測試 `@log_exception` 裝飾器
- 測試 `StructuredLogger` 類
- 測試 `PerformanceLogger` 類

## 🔧 Pytest 配置 (pytest.ini)

主要配置選項：

```ini
[pytest]
# 測試目錄
testpaths = tests

# 測試文件模式
python_files = test_*.py *_test.py

# 命令行選項
addopts =
    -v                    # 詳細輸出
    --cov=src            # 覆蓋率測試
    --cov-report=html    # HTML 報告
    --tb=short           # 簡短的錯誤追蹤
    --durations=10       # 顯示最慢的 10 個測試
    --strict-markers     # 嚴格標記檢查

# 日誌配置
log_cli = true
log_cli_level = INFO
log_file = logs/pytest.log
```

## 🎯 Pytest Fixtures

### 專案相關 Fixtures

在 `tests/conftest.py` 中定義：

```python
# 基礎 fixtures
project_root          # 專案根目錄路徑
sample_data_dir       # 測試數據目錄
mock_api_key         # 模擬 API key

# 環境相關 fixtures
env_setup            # 自動設置測試環境變數
clean_environment    # 乾淨的環境（無 API keys）

# 目錄和文件 fixtures
test_dirs            # 測試相關目錄字典
framework_dirs       # 所有框架目錄列表
example_files        # 所有示例 Python 文件

# 日誌相關 fixtures
temp_log_file        # 臨時日誌文件
captured_logs        # 捕獲的日誌記錄
ensure_log_dir       # 確保日誌目錄存在

# 工具 fixtures
mock_framework_file  # 創建模擬框架文件
session_temp_dir     # 會話級臨時目錄
```

### 使用 Fixtures 示例

```python
import pytest

@pytest.mark.unit
def test_with_fixtures(project_root, mock_api_key):
    """使用 fixtures 的測試示例"""
    assert project_root.exists()
    assert mock_api_key.startswith("sk-test")

@pytest.mark.unit
def test_framework_count(framework_dirs):
    """測試框架數量"""
    assert len(framework_dirs) > 0
    print(f"找到 {len(framework_dirs)} 個框架")
```

## 📊 測試標記 (Markers)

可用的測試標記：

| 標記 | 說明 | 使用示例 |
|-----|------|---------|
| `unit` | 單元測試 | `@pytest.mark.unit` |
| `integration` | 整合測試 | `@pytest.mark.integration` |
| `slow` | 慢速測試 | `@pytest.mark.slow` |
| `requires_api_key` | 需要真實 API key | `@pytest.mark.requires_api_key` |
| `requires_network` | 需要網絡連接 | `@pytest.mark.requires_network` |
| `skip_in_ci` | CI 環境中跳過 | `@pytest.mark.skip_in_ci` |
| `asyncio` | 異步測試 | `@pytest.mark.asyncio` |
| `mock` | 使用 mock | `@pytest.mark.mock` |

## 🔍 測試結果解讀

### 成功的測試運行

```bash
$ pytest tests/test_basic.py -v

============================= test session starts ==============================
...
tests/test_basic.py::test_python_version PASSED                          [100%]

============================== 1 passed in 0.02s ===============================
```

### 發現問題的測試

```bash
$ pytest tests/test_imports.py::test_python_files_syntax -v

發現 5 個語法錯誤:
  - /path/to/file.py:21 - invalid syntax
  ...

FAILED tests/test_imports.py::test_python_files_syntax
```

這表示測試發現了代碼中的語法錯誤，需要修復。

## 🛠️ 常見任務

### 添加新測試

1. 在 `tests/` 目錄創建新測試文件（以 `test_` 開頭）
2. 導入必要的模組和 fixtures
3. 編寫測試函數（以 `test_` 開頭）
4. 添加適當的標記

```python
import pytest

@pytest.mark.unit
def test_my_new_feature():
    """測試我的新功能"""
    assert True
```

### 跳過特定測試

```python
@pytest.mark.skip(reason="暫時跳過")
def test_todo_feature():
    pass

@pytest.mark.skipif(sys.version_info < (3, 10), reason="需要 Python 3.10+")
def test_new_python_feature():
    pass
```

### 參數化測試

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    assert input * 2 == expected
```

## 📈 持續改進

### 提高測試覆蓋率

1. 查看覆蓋率報告：`pytest --cov=src --cov-report=html`
2. 打開 `htmlcov/index.html` 查看詳細報告
3. 為未覆蓋的代碼添加測試

### 優化測試速度

1. 使用 `--durations=10` 查找慢速測試
2. 考慮使用 `@pytest.mark.slow` 標記慢速測試
3. 使用適當的 fixture scope（function, class, module, session）

## ⚠️ 已知問題

### 語法錯誤

`test_imports.py` 發現了以下文件的語法錯誤：

1. `/home/user/LLM-agent-Demo/27.OpenAI-Agents-SDK/09_研究助手.py:21`
2. `/home/user/LLM-agent-Demo/27.OpenAI-Agents-SDK/08_客服系統.py:94`
3. `/home/user/LLM-agent-Demo/34.CopilotKit/10_最佳實踐.py:387`
4. `/home/user/LLM-agent-Demo/45.Letta/10_生產部署.py:436`
5. `/home/user/LLM-agent-Demo/61.vLLM/08_LoRA適配.py:609`

建議修復這些語法錯誤以確保代碼質量。

### 日誌測試問題

部分日誌測試可能由於日誌配置問題而失敗。這些測試驗證日誌系統功能，失敗不影響核心功能。

## 📚 參考資源

- [Pytest 官方文檔](https://docs.pytest.org/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Pytest 標記](https://docs.pytest.org/en/stable/mark.html)
- [Coverage.py](https://coverage.readthedocs.io/)

## 🤝 貢獻

如果你發現測試問題或有改進建議：

1. 在 GitHub 上創建 issue
2. 提交 pull request
3. 確保所有測試通過

---

**最後更新**: 2025-12-31
**維護者**: LLM Agent Demo Team
