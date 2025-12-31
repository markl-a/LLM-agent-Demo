# GitHub Actions CI/CD 配置說明

本目錄包含專案的 GitHub Actions CI/CD 配置、Issue 模板和其他 GitHub 相關設定。

## 📁 目錄結構

```
.github/
├── ISSUE_TEMPLATE/           # Issue 模板目錄
│   ├── bug_report.md        # Bug 回報模板
│   ├── feature_request.md   # 功能請求模板
│   └── config.yml           # Issue 模板配置
├── workflows/               # GitHub Actions 工作流
│   ├── ci.yml              # CI/CD 主工作流
│   ├── docs.yml            # 文檔構建和部署
│   └── publish.yml         # 發布工作流
├── PULL_REQUEST_TEMPLATE.md # PR 模板
├── dependabot.yml          # Dependabot 自動更新配置
└── markdown-link-check-config.json  # Markdown 鏈接檢查配置
```

## 🔄 CI/CD 工作流

### 1. CI Workflow (ci.yml)

主要的持續集成工作流，在每次 push 和 PR 時自動運行。

#### 觸發條件
- **Push**: main, develop, claude/* 分支
- **Pull Request**: main, develop 分支

#### 包含的 Jobs

##### a. Test Job
- **Python 版本矩陣**: 3.9, 3.10, 3.11, 3.12
- **步驟**:
  1. Checkout 代碼
  2. 設置 Python 環境
  3. 緩存 pip 套件
  4. 安裝依賴 (requirements.txt, requirements-dev.txt)
  5. 運行 pytest 測試（排除需要 API key 的測試）
  6. 上傳測試覆蓋率到 Codecov
  7. 保存測試結果

##### b. Lint Job
代碼質量檢查，包含：
- **Black**: 代碼格式化檢查
- **Flake8**: 代碼風格檢查
- **Ruff**: 快速 Python linter
- **isort**: import 排序檢查
- **mypy**: 類型檢查

##### c. Docker Job
- Docker 鏡像構建測試
- 使用 BuildKit 和 GitHub Actions 緩存

##### d. Security Job
安全掃描，包含：
- **Bandit**: Python 安全問題掃描
- **Safety**: 依賴漏洞檢查
- **pip-audit**: 依賴安全審計
- 結果上傳到 GitHub Security

##### e. CodeQL Job
- GitHub 官方代碼安全分析
- 使用 security-extended 和 security-and-quality 查詢

##### f. Trivy Job
- 漏洞掃描工具
- 掃描文件系統和依賴
- 結果上傳到 GitHub Security

##### g. Dependency Review Job
- PR 時進行依賴審查
- 阻止有安全問題的依賴
- 禁止使用 GPL-3.0 和 AGPL-3.0 授權

##### h. Build Test Job
- 測試 Python 套件構建
- 使用 twine 檢查套件完整性
- 驗證 manifest 文件

### 2. Documentation Workflow (docs.yml)

文檔構建和部署工作流。

#### 觸發條件
- **Push** 到 main 分支（docs/**, mkdocs.yml, **.md 文件變更時）
- **Pull Request** 到 main 分支
- **手動觸發** (workflow_dispatch)

#### 包含的 Jobs

##### a. Check Links Job
- 檢查 Markdown 文件中的鏈接
- 使用自定義配置文件

##### b. Validate Notebooks Job
- 驗證所有 Jupyter Notebook 文件結構
- 確保 JSON 格式正確

##### c. Build MkDocs Job
- 構建 MkDocs 靜態網站
- 使用 Material 主題
- 包含 git-revision-date 和 minify 插件

##### d. Deploy Pages Job
- 部署到 GitHub Pages
- 僅在 push 到 main 時執行

### 3. Publish Workflow (publish.yml)

發布套件到 PyPI（需手動或通過 tag 觸發）。

## 🐛 Issue 模板

### Bug Report (bug_report.md)
包含以下部分：
- Bug 描述
- 重現步驟
- 預期/實際行為
- 錯誤訊息/截圖
- 環境資訊
- 重現程式碼
- 已嘗試的解決方案

### Feature Request (feature_request.md)
包含以下部分：
- 功能描述
- 問題陳述
- 建議的解決方案
- 使用場景
- 範例程式碼
- 優先級評估
- 實作建議

### Issue 模板配置 (config.yml)
- 禁用空白 issue
- 提供文檔、討論區和 FAQ 的快捷連結

## 📝 Pull Request 模板

PR 模板包含：
- 改動描述
- 改動類型（Bug 修復、新功能等）
- 相關 Issue 連結
- 測試說明
- 完整的檢查清單

## 🤖 Dependabot 配置

自動依賴更新配置：

### Python 依賴 (pip)
- **更新頻率**: 每週一 09:00 (台北時間)
- **PR 限制**: 最多 10 個
- **標籤**: dependencies, python
- **分組策略**:
  - LLM 框架 (langchain, llama-index, crewai, openai 等)
  - 開發工具 (pytest, black, ruff, mypy 等)
  - 向量數據庫 (chromadb, faiss, pinecone 等)

### GitHub Actions
- **更新頻率**: 每週一
- **標籤**: dependencies, github-actions

### Docker
- **更新頻率**: 每月
- **標籤**: dependencies, docker

## 🚀 使用方式

### 本地測試

執行完整的 CI 檢查：
```bash
# 安裝依賴
pip install -r requirements-dev.txt

# 代碼格式化
black --check .

# Linting
ruff check .
flake8 .

# 類型檢查
mypy . --config-file pyproject.toml

# 運行測試
pytest -v --cov=. --cov-report=term-missing
```

### 使用 Makefile

專案包含 Makefile，可以快速運行常用命令：
```bash
# 安裝依賴
make install

# 運行測試
make test

# 代碼檢查
make lint

# 代碼格式化
make format

# 完整 CI 流程
make ci
```

## 📊 CI/CD 流程圖

```
Push/PR
  │
  ├─► Test (Python 3.9, 3.10, 3.11, 3.12)
  │     └─► Upload Coverage
  │
  ├─► Lint
  │     ├─► Black
  │     ├─► Flake8
  │     ├─► Ruff
  │     ├─► isort
  │     └─► mypy
  │
  ├─► Docker Build
  │
  ├─► Security Scan
  │     ├─► Bandit
  │     ├─► Safety
  │     └─► pip-audit
  │
  ├─► CodeQL Analysis
  │
  ├─► Trivy Scan
  │
  ├─► Dependency Review (PR only)
  │
  └─► Build Package Test
```

## 🔒 安全性

所有安全掃描結果會自動上傳到 GitHub Security 標籤頁，包括：
- Bandit (SARIF)
- CodeQL (內建)
- Trivy (SARIF)
- Dependency Review

## 📈 最佳實踐

1. **在提交前本地運行測試**: 使用 `make test` 或 `pytest`
2. **使用 pre-commit hooks**: 已配置在 `.pre-commit-config.yaml`
3. **保持測試覆蓋率**: 目標至少 50%
4. **遵循代碼風格**: 使用 Black 和 Ruff
5. **及時更新依賴**: 審查 Dependabot PR
6. **處理安全警告**: 定期檢查 Security 標籤頁

## 🔧 自定義配置

如需修改 CI/CD 配置：

1. **修改 Python 版本**: 編輯 `ci.yml` 的 `matrix.python-version`
2. **調整測試覆蓋率要求**: 編輯 `pyproject.toml` 的 `--cov-fail-under`
3. **更改 Dependabot 頻率**: 編輯 `dependabot.yml` 的 `schedule.interval`
4. **自定義 Issue 模板**: 編輯 `ISSUE_TEMPLATE/` 下的 Markdown 文件

## 📚 相關文檔

- [GitHub Actions 文檔](https://docs.github.com/en/actions)
- [Dependabot 文檔](https://docs.github.com/en/code-security/dependabot)
- [GitHub Security 文檔](https://docs.github.com/en/code-security)
- [專案主要文檔](../README.md)

## 🤝 貢獻

如果你想改進 CI/CD 配置，請：
1. 創建新的分支
2. 修改相關配置文件
3. 本地測試驗證
4. 提交 PR 並說明改進原因

---

最後更新: 2025-12-31
