# 測試套件

此目錄包含 LLM Agent Demo 專案的所有測試。

## 目錄結構

```
tests/
├── __init__.py              # 測試套件初始化
├── conftest.py              # Pytest 配置和共享 fixtures
├── README.md                # 本文件
├── test_basic.py            # 基礎測試範例
├── test_imports.py          # 測試所有框架文件的導入和語法
├── test_examples.py         # 測試示例文件的語法和結構
├── test_logging.py          # 測試日誌系統功能
├── unit/                    # 單元測試
│   ├── __init__.py
│   ├── test_async_utils.py
│   ├── test_cli.py
│   ├── test_config.py
│   ├── test_cost_tracker.py
│   ├── test_events.py
│   ├── test_logger.py
│   ├── test_rate_limiter.py
│   ├── test_retry.py
│   ├── test_serialization.py
│   ├── test_utils.py
│   └── test_validators.py
├── integration/             # 整合測試
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_config_logger_validators.py
│   ├── test_cost_tracker_retry.py
│   ├── test_full_config_loading.py
│   └── test_import.py
└── data/                    # 測試數據（如需要）
```

## 運行測試

### 運行所有測試

```bash
pytest
```

### 運行特定測試文件

```bash
pytest tests/test_basic.py
```

### 運行帶標記的測試

```bash
# 只運行單元測試
pytest -m unit

# 只運行整合測試
pytest -m integration

# 排除慢速測試
pytest -m "not slow"

# 只運行不需要 API Key 的測試
pytest -m "not requires_api_key"
```

### 生成覆蓋率報告

```bash
# 生成 HTML 覆蓋率報告
pytest --cov=. --cov-report=html

# 生成終端覆蓋率報告
pytest --cov=. --cov-report=term-missing
```

## 測試文件說明

### 核心測試文件

- **test_basic.py** - 專案基礎結構和配置測試
- **test_imports.py** - 掃描所有框架目錄，檢查 Python 文件語法和導入
- **test_examples.py** - 驗證示例文件的語法、結構和最佳實踐
- **test_logging.py** - 測試日誌系統的各項功能（日誌器、裝飾器、工具類等）

### 單元測試 (unit/)

單元測試專注於測試個別組件和函數的正確性。

### 整合測試 (integration/)

整合測試驗證多個組件協同工作的情況。

## 測試標記 (Markers)

- `@pytest.mark.unit` - 單元測試
- `@pytest.mark.integration` - 整合測試
- `@pytest.mark.slow` - 運行時間較長的測試
- `@pytest.mark.requires_api_key` - 需要真實 API Key 的測試
- `@pytest.mark.requires_network` - 需要網絡連接的測試
- `@pytest.mark.skip_in_ci` - 在 CI 環境中跳過的測試
- `@pytest.mark.asyncio` - 異步測試
- `@pytest.mark.mock` - 使用 mock 的測試

## 編寫測試的最佳實踐

1. **使用描述性的測試名稱**
   ```python
   def test_langchain_simple_rag_returns_valid_response():
       pass
   ```

2. **使用 fixtures 共享設置**
   ```python
   def test_with_mock_api(mock_api_key):
       assert mock_api_key.startswith("sk-test")
   ```

3. **適當使用標記**
   ```python
   @pytest.mark.unit
   def test_utility_function():
       pass

   @pytest.mark.integration
   @pytest.mark.slow
   @pytest.mark.requires_api_key
   def test_full_rag_pipeline():
       pass
   ```

4. **測試應該是獨立的**
   - 不依賴其他測試的執行順序
   - 清理創建的資源

5. **使用參數化測試處理多個案例**
   ```python
   @pytest.mark.parametrize("input,expected", [
       ("hello", "HELLO"),
       ("world", "WORLD"),
   ])
   def test_uppercase(input, expected):
       assert input.upper() == expected
   ```

## CI/CD 整合

測試會在 GitHub Actions 中自動運行。詳見 `.github/workflows/ci.yml`。
