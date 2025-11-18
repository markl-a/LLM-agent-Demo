# 測試套件

此目錄包含 LLM Agent Demo 專案的所有測試。

## 目錄結構

```
tests/
├── __init__.py              # 測試套件初始化
├── conftest.py              # Pytest 配置和共享 fixtures
├── README.md                # 本文件
├── test_basic.py            # 基礎測試範例
├── unit/                    # 單元測試
│   └── test_utils.py
├── integration/             # 整合測試
│   └── test_langchain_integration.py
└── data/                    # 測試數據
    └── sample.txt
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

## 測試標記 (Markers)

- `@pytest.mark.unit` - 單元測試
- `@pytest.mark.integration` - 整合測試
- `@pytest.mark.slow` - 運行時間較長的測試
- `@pytest.mark.requires_api_key` - 需要真實 API Key 的測試

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
