.PHONY: help install install-dev test lint format clean docker-build docker-up docker-down docs serve-docs

# 默認目標
.DEFAULT_GOAL := help

# 顏色輸出
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Python 解釋器
PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest

# 專案信息
PROJECT_NAME := LLM-agent-Demo
VERSION := 2.0.0

help: ## 顯示幫助信息
	@echo "$(BLUE)$(PROJECT_NAME) - Makefile 幫助$(NC)"
	@echo ""
	@echo "$(GREEN)可用命令:$(NC)"
	@awk 'BEGIN {FS = ":.*##"; printf ""} \
		/^[a-zA-Z_-]+:.*?##/ { printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2 } \
		/^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ 安裝和設置

venv: ## 創建虛擬環境
	@echo "$(GREEN)創建虛擬環境...$(NC)"
	$(PYTHON) -m venv venv
	@echo "$(GREEN)✓ 虛擬環境已創建$(NC)"
	@echo "$(YELLOW)激活方式:$(NC)"
	@echo "  Linux/Mac: source venv/bin/activate"
	@echo "  Windows:   venv\\Scripts\\activate"

install: ## 安裝生產環境依賴
	@echo "$(GREEN)安裝依賴...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ 安裝完成$(NC)"

install-dev: install ## 安裝開發環境依賴（包括測試和 linting 工具）
	@echo "$(GREEN)安裝開發依賴...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install pre-commit
	pre-commit install
	@echo "$(GREEN)✓ 開發環境設置完成$(NC)"

install-poetry: ## 使用 Poetry 安裝依賴
	@echo "$(GREEN)使用 Poetry 安裝...$(NC)"
	poetry install
	@echo "$(GREEN)✓ Poetry 安裝完成$(NC)"

install-playwright: ## 安裝 Playwright 瀏覽器
	@echo "$(GREEN)安裝 Playwright 瀏覽器...$(NC)"
	playwright install
	@echo "$(GREEN)✓ Playwright 瀏覽器已安裝$(NC)"

install-all: install-dev install-playwright ## 安裝所有依賴（包括 Playwright）
	@echo "$(GREEN)✓ 所有依賴已安裝完成$(NC)"

setup-env: ## 設置環境變數文件
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)創建 .env 文件...$(NC)"; \
		cp .env.example .env; \
		echo "$(GREEN)✓ .env 文件已創建，請編輯並添加您的 API keys$(NC)"; \
	else \
		echo "$(YELLOW).env 文件已存在$(NC)"; \
	fi

update-deps: ## 更新所有依賴到最新版本
	@echo "$(GREEN)更新依賴...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -r requirements.txt
	@echo "$(GREEN)✓ 依賴已更新$(NC)"

##@ 測試

test: ## 運行所有測試
	@echo "$(GREEN)運行測試...$(NC)"
	$(PYTEST) tests/ -v

test-unit: ## 運行單元測試
	@echo "$(GREEN)運行單元測試...$(NC)"
	$(PYTEST) tests/unit/ -v -m unit

test-integration: ## 運行集成測試
	@echo "$(GREEN)運行集成測試...$(NC)"
	$(PYTEST) tests/integration/ -v -m integration

test-cov: ## 運行測試並生成覆蓋率報告
	@echo "$(GREEN)運行測試並生成覆蓋率報告...$(NC)"
	$(PYTEST) tests/ -v --cov=. --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ 覆蓋率報告已生成: htmlcov/index.html$(NC)"

test-quick: ## 快速測試（跳過慢速測試）
	@echo "$(GREEN)運行快速測試...$(NC)"
	$(PYTEST) tests/ -v -m "not slow"

test-watch: ## 監視模式運行測試（文件變化時自動重新運行）
	@echo "$(GREEN)啟動測試監視模式...$(NC)"
	@if command -v pytest-watch > /dev/null; then \
		pytest-watch tests/; \
	else \
		echo "$(YELLOW)pytest-watch 未安裝，嘗試安裝...$(NC)"; \
		$(PIP) install pytest-watch; \
		pytest-watch tests/; \
	fi

test-failed: ## 只重新運行上次失敗的測試
	@echo "$(GREEN)重新運行失敗的測試...$(NC)"
	$(PYTEST) tests/ -v --lf

test-report: test-cov ## 生成詳細的測試報告
	@echo "$(GREEN)生成測試報告...$(NC)"
	@echo "$(BLUE)HTML 覆蓋率報告: htmlcov/index.html$(NC)"
	@echo "$(BLUE)XML 覆蓋率報告: coverage.xml$(NC)"
	@if command -v xdg-open > /dev/null; then \
		xdg-open htmlcov/index.html; \
	elif command -v open > /dev/null; then \
		open htmlcov/index.html; \
	else \
		echo "$(YELLOW)請手動打開 htmlcov/index.html 查看報告$(NC)"; \
	fi

benchmark: ## 運行性能基準測試
	@echo "$(GREEN)運行性能測試...$(NC)"
	@if command -v pytest-benchmark > /dev/null; then \
		$(PYTEST) tests/ -v -m benchmark --benchmark-only; \
	else \
		echo "$(YELLOW)pytest-benchmark 未安裝$(NC)"; \
		echo "$(YELLOW)運行: pip install pytest-benchmark$(NC)"; \
	fi

##@ 代碼質量

lint: ## 運行 Ruff linting 檢查
	@echo "$(GREEN)運行 Ruff linting 檢查...$(NC)"
	$(PYTHON) -m ruff check .
	@echo "$(GREEN)✓ Linting 完成$(NC)"

lint-fix: ## 自動修復 linting 問題
	@echo "$(GREEN)自動修復 linting 問題...$(NC)"
	$(PYTHON) -m ruff check --fix .
	@echo "$(GREEN)✓ 自動修復完成$(NC)"

format: ## 使用 Ruff 格式化代碼
	@echo "$(GREEN)格式化代碼...$(NC)"
	$(PYTHON) -m ruff format .
	@echo "$(GREEN)✓ 代碼格式化完成$(NC)"

format-check: ## 檢查代碼格式（不修改）
	@echo "$(GREEN)檢查代碼格式...$(NC)"
	$(PYTHON) -m ruff format --check .

type-check: ## 運行類型檢查
	@echo "$(GREEN)運行類型檢查...$(NC)"
	$(PYTHON) -m mypy .
	@echo "$(GREEN)✓ 類型檢查完成$(NC)"

security-check: ## 運行安全檢查
	@echo "$(GREEN)運行安全檢查...$(NC)"
	$(PYTHON) -m bandit -r . -f json -o bandit-report.json || true
	@echo "$(GREEN)✓ 安全檢查完成（報告: bandit-report.json）$(NC)"

check: lint test ## 運行 linting 和測試
	@echo "$(GREEN)✓ 代碼檢查和測試完成$(NC)"

check-all: format-check lint type-check security-check ## 運行所有檢查

##@ Docker

docker-build: ## 構建 Docker 鏡像
	@echo "$(GREEN)構建 Docker 鏡像...$(NC)"
	docker-compose build
	@echo "$(GREEN)✓ Docker 鏡像構建完成$(NC)"

docker-up: ## 啟動 Docker 容器
	@echo "$(GREEN)啟動 Docker 容器...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Docker 容器已啟動$(NC)"

docker-down: ## 停止 Docker 容器
	@echo "$(GREEN)停止 Docker 容器...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Docker 容器已停止$(NC)"

docker-logs: ## 查看 Docker 日誌
	docker-compose logs -f

docker-shell: ## 進入 Docker 容器 shell
	docker-compose exec app /bin/bash

##@ 文檔

docs: ## 構建文檔
	@echo "$(GREEN)構建文檔...$(NC)"
	@if [ -d "docs" ]; then \
		mkdocs build; \
		echo "$(GREEN)✓ 文檔構建完成: site/$(NC)"; \
	else \
		echo "$(YELLOW)docs 目錄不存在，跳過文檔構建$(NC)"; \
	fi

serve-docs: ## 本地預覽文檔
	@echo "$(GREEN)啟動文檔服務器...$(NC)"
	@if [ -d "docs" ]; then \
		mkdocs serve; \
	else \
		echo "$(RED)docs 目錄不存在$(NC)"; \
		exit 1; \
	fi

docs-deploy: docs ## 部署文檔到 GitHub Pages
	@echo "$(GREEN)部署文檔到 GitHub Pages...$(NC)"
	@if [ -d "docs" ]; then \
		mkdocs gh-deploy --force; \
		echo "$(GREEN)✓ 文檔已部署$(NC)"; \
	else \
		echo "$(RED)docs 目錄不存在$(NC)"; \
		exit 1; \
	fi

api-docs: ## 生成 API 文檔
	@echo "$(GREEN)生成 API 文檔...$(NC)"
	@if command -v pdoc > /dev/null; then \
		pdoc --html --output-dir api-docs src/llm_agent_demo --force; \
		echo "$(GREEN)✓ API 文檔已生成: api-docs/$(NC)"; \
	else \
		echo "$(YELLOW)pdoc 未安裝，嘗試安裝...$(NC)"; \
		$(PIP) install pdoc3; \
		pdoc --html --output-dir api-docs src/llm_agent_demo --force; \
	fi

changelog: ## 查看變更日誌
	@if [ -f CHANGELOG.md ]; then \
		cat CHANGELOG.md | head -50; \
	else \
		echo "$(YELLOW)CHANGELOG.md 不存在$(NC)"; \
	fi

##@ 清理

clean: ## 清理生成的文件
	@echo "$(GREEN)清理生成的文件...$(NC)"
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '.coverage' -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf dist/
	rm -rf build/
	rm -rf site/
	rm -rf api-docs/
	rm -f bandit-report.json
	rm -f coverage.xml
	@echo "$(GREEN)✓ 清理完成$(NC)"

clean-cache: ## 清理 Python 緩存文件
	@echo "$(GREEN)清理 Python 緩存...$(NC)"
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ 緩存清理完成$(NC)"

clean-docs: ## 清理文檔生成文件
	@echo "$(GREEN)清理文檔文件...$(NC)"
	rm -rf site/
	rm -rf api-docs/
	@echo "$(GREEN)✓ 文檔清理完成$(NC)"

clean-test: ## 清理測試生成的文件
	@echo "$(GREEN)清理測試文件...$(NC)"
	find . -type f -name '.coverage' -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -f coverage.xml
	@echo "$(GREEN)✓ 測試文件清理完成$(NC)"

clean-all: clean ## 清理所有文件（包括向量數據庫）
	@echo "$(YELLOW)清理所有文件（包括向量數據庫）...$(NC)"
	find . -type d -name 'vectorstore' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name 'chroma_db' -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ 完全清理完成$(NC)"

clean-venv: ## 刪除虛擬環境
	@echo "$(YELLOW)刪除虛擬環境...$(NC)"
	@read -p "確定要刪除虛擬環境嗎？ [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf venv/; \
		echo "$(GREEN)✓ 虛擬環境已刪除$(NC)"; \
	else \
		echo "$(YELLOW)取消操作$(NC)"; \
	fi

reset: clean-all clean-venv ## 完全重置專案（刪除所有生成文件和虛擬環境）
	@echo "$(RED)專案已重置$(NC)"

##@ 開發工具

nb: ## 啟動 Jupyter Notebook
	@echo "$(GREEN)啟動 Jupyter Notebook...$(NC)"
	jupyter notebook

lab: ## 啟動 Jupyter Lab
	@echo "$(GREEN)啟動 Jupyter Lab...$(NC)"
	jupyter lab

streamlit-doc-qa: ## 啟動文檔問答系統 Web UI
	@echo "$(GREEN)啟動文檔問答系統...$(NC)"
	cd "11.實際應用案例/文檔問答系統" && streamlit run app.py

##@ Git 操作

git-status: ## 查看 Git 狀態
	@git status

git-diff: ## 查看 Git 差異
	@git diff

commit: ## 創建 Git commit（需要先 git add）
	@echo "$(YELLOW)請輸入 commit 信息:$(NC)"
	@read -p "> " msg; \
	git commit -m "$$msg"

push: ## 推送到遠端
	@echo "$(GREEN)推送到遠端...$(NC)"
	@BRANCH=$$(git rev-parse --abbrev-ref HEAD); \
	git push -u origin $$BRANCH

pull: ## 從遠端拉取
	@echo "$(GREEN)從遠端拉取...$(NC)"
	git pull

##@ 實用工具

check-deps: ## 檢查依賴是否有更新
	@echo "$(GREEN)檢查依賴更新...$(NC)"
	$(PIP) list --outdated

verify-env: ## 驗證環境配置
	@echo "$(GREEN)驗證環境配置...$(NC)"
	@if [ -f .env ]; then \
		echo "$(GREEN)✓ .env 文件存在$(NC)"; \
	else \
		echo "$(RED)✗ .env 文件不存在$(NC)"; \
		echo "$(YELLOW)  運行 'make setup-env' 創建$(NC)"; \
	fi
	@echo ""
	@echo "$(BLUE)檢查必需的 API Keys:$(NC)"
	@if [ -f .env ]; then \
		grep -q "OPENAI_API_KEY" .env && echo "$(GREEN)✓ OPENAI_API_KEY$(NC)" || echo "$(YELLOW)○ OPENAI_API_KEY 未設置$(NC)"; \
		grep -q "ANTHROPIC_API_KEY" .env && echo "$(GREEN)✓ ANTHROPIC_API_KEY$(NC)" || echo "$(YELLOW)○ ANTHROPIC_API_KEY 未設置$(NC)"; \
		grep -q "GOOGLE_API_KEY" .env && echo "$(GREEN)✓ GOOGLE_API_KEY$(NC)" || echo "$(YELLOW)○ GOOGLE_API_KEY 未設置$(NC)"; \
	fi

count-lines: ## 統計代碼行數
	@echo "$(GREEN)統計代碼行數...$(NC)"
	@echo "Python 文件:"
	@find . -name '*.py' -not -path '*/\.*' -not -path '*/venv/*' | xargs wc -l | tail -1
	@echo ""
	@echo "Jupyter Notebook:"
	@find . -name '*.ipynb' -not -path '*/\.*' | wc -l
	@echo ""
	@echo "Markdown 文件:"
	@find . -name '*.md' -not -path '*/\.*' | wc -l

tree: ## 顯示專案目錄結構
	@echo "$(GREEN)專案目錄結構:$(NC)"
	@if command -v tree > /dev/null; then \
		tree -L 2 -I 'venv|__pycache__|*.egg-info|.git|.pytest_cache|.mypy_cache|.ruff_cache|htmlcov|node_modules' --dirsfirst; \
	else \
		echo "$(YELLOW)tree 命令未安裝，使用 ls 替代$(NC)"; \
		ls -R | grep ":$$" | sed -e 's/:$$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/' | head -50; \
	fi

list-examples: ## 列出所有可用的示例
	@echo "$(GREEN)可用的 LLM Agent 示例:$(NC)"
	@echo ""
	@echo "$(BLUE)1. LangChain Demos$(NC)"
	@ls -1 "1.LangchainDemos" 2>/dev/null | head -5 || echo "  (查看 1.LangchainDemos 目錄)"
	@echo ""
	@echo "$(BLUE)2. Multi-modal RAG$(NC)"
	@ls -1 "2.Multi_modal_RAG" 2>/dev/null | head -5 || echo "  (查看 2.Multi_modal_RAG 目錄)"
	@echo ""
	@echo "$(YELLOW)運行 'make help' 查看更多命令$(NC)"

show-config: ## 顯示當前配置
	@echo "$(BLUE)=== Python 環境 ===$(NC)"
	@echo "Python 版本: $$($(PYTHON) --version)"
	@echo "Python 路徑: $$(which $(PYTHON))"
	@echo "Pip 版本: $$($(PIP) --version | cut -d' ' -f2)"
	@echo ""
	@echo "$(BLUE)=== 已安裝的主要框架 ===$(NC)"
	@$(PIP) list | grep -E "(langchain|llama-index|autogen|crewai|metagpt)" || echo "尚未安裝框架"

version: ## 顯示版本信息
	@echo "$(BLUE)$(PROJECT_NAME) v$(VERSION)$(NC)"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Pip: $$($(PIP) --version | cut -d' ' -f2)"

info: ## 顯示專案信息
	@echo "$(BLUE)=== 專案信息 ===$(NC)"
	@echo "專案名稱: $(PROJECT_NAME)"
	@echo "版本: $(VERSION)"
	@echo "Python: $$($(PYTHON) --version)"
	@echo ""
	@echo "$(BLUE)=== 目錄統計 ===$(NC)"
	@echo "Python 文件: $$(find . -name '*.py' -not -path '*/\.*' -not -path '*/venv/*' | wc -l)"
	@echo "Jupyter Notebooks: $$(find . -name '*.ipynb' -not -path '*/\.*' | wc -l)"
	@echo "Markdown 文件: $$(find . -name '*.md' -not -path '*/\.*' | wc -l)"
	@echo ""
	@echo "$(BLUE)=== Git 信息 ===$(NC)"
	@echo "當前分支: $$(git rev-parse --abbrev-ref HEAD)"
	@echo "最後一次提交: $$(git log -1 --pretty=format:'%h - %s (%cr)')"

##@ 快速操作

quick-start: venv setup-env ## 快速開始（創建虛擬環境並設置環境）
	@echo "$(GREEN)=== 快速開始完成 ===$(NC)"
	@echo ""
	@echo "$(BLUE)接下來的步驟:$(NC)"
	@echo "  1. 激活虛擬環境:"
	@echo "     $(YELLOW)source venv/bin/activate$(NC)  (Linux/Mac)"
	@echo "     $(YELLOW)venv\\Scripts\\activate$(NC)      (Windows)"
	@echo ""
	@echo "  2. 安裝依賴:"
	@echo "     $(YELLOW)make install-all$(NC)"
	@echo ""
	@echo "  3. 編輯 .env 文件並添加你的 API keys"
	@echo ""
	@echo "  4. 運行測試確保一切正常:"
	@echo "     $(YELLOW)make test$(NC)"
	@echo ""
	@echo "  5. 查看 README.md 了解更多信息"

full-setup: venv install-all setup-env ## 完整設置（虛擬環境、依賴、環境配置）
	@echo "$(GREEN)=== 完整設置完成 ===$(NC)"
	@echo "$(YELLOW)請編輯 .env 文件並添加你的 API keys$(NC)"
	@echo "$(YELLOW)然後運行 'make verify-env' 驗證配置$(NC)"

dev: install-dev test lint ## 開發流程（安裝、測試、檢查）
	@echo "$(GREEN)✓ 開發環境準備完成$(NC)"

dev-check: format lint type-check ## 開發檢查（格式化、linting、類型檢查）
	@echo "$(GREEN)✓ 開發檢查完成$(NC)"

ci: format-check lint test ## CI 流程（格式檢查、linting、測試）
	@echo "$(GREEN)✓ CI 檢查通過$(NC)"

ci-full: format-check lint type-check security-check test-cov ## 完整 CI 流程
	@echo "$(GREEN)✓ 完整 CI 檢查通過$(NC)"

deploy-prep: clean test lint ## 部署前準備
	@echo "$(GREEN)✓ 部署前檢查完成$(NC)"

rebuild: clean-all install-all ## 重新構建（清理並重新安裝）
	@echo "$(GREEN)✓ 重新構建完成$(NC)"

daily: pull install format test ## 每日開發流程（拉取、安裝、格式化、測試）
	@echo "$(GREEN)✓ 每日開發流程完成$(NC)"

# ==================== Docker 相關命令 ====================
.PHONY: docker-build docker-up docker-down docker-restart docker-logs docker-shell docker-clean docker-dev

docker-build:  ## 構建 Docker 鏡像
	@echo "Building Docker images..."
	docker-compose build

docker-up:  ## 啟動 Docker 服務（生產模式）
	@echo "Starting Docker services (production)..."
	docker-compose up -d

docker-dev:  ## 啟動 Docker 服務（開發模式）
	@echo "Starting Docker services (development)..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

docker-down:  ## 停止 Docker 服務
	@echo "Stopping Docker services..."
	docker-compose down

docker-restart:  ## 重啟 Docker 服務
	@echo "Restarting Docker services..."
	docker-compose restart

docker-logs:  ## 查看 Docker 日誌
	docker-compose logs -f

docker-shell:  ## 進入應用容器
	docker-compose exec app bash

docker-clean:  ## 清理 Docker 資源（保留數據卷）
	@echo "Cleaning Docker resources..."
	docker-compose down --rmi local
	docker system prune -f

docker-clean-all:  ## 清理所有 Docker 資源（包括數據卷）
	@echo "⚠️  WARNING: This will delete all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v --rmi all; \
		docker system prune -af; \
	fi

docker-status:  ## 查看 Docker 服務狀態
	docker-compose ps

docker-pull:  ## 拉取最新的基礎鏡像
	docker-compose pull

docker-health:  ## 運行健康檢查
	docker-compose exec app python /healthcheck.py

docker-ollama-pull:  ## 拉取 Ollama 模型
	@read -p "Enter model name (e.g., llama2): " model; \
	docker-compose exec ollama ollama pull $$model

docker-ollama-list:  ## 列出 Ollama 模型
	docker-compose exec ollama ollama list

docker-backup:  ## 備份 Docker 數據卷
	@echo "Backing up Docker volumes..."
	@mkdir -p backups
	docker run --rm -v llm-agent-demo_chroma-data:/data -v $$(pwd)/backups:/backup ubuntu tar czf /backup/chromadb-$$(date +%Y%m%d-%H%M%S).tar.gz /data
	docker run --rm -v llm-agent-demo_ollama-data:/data -v $$(pwd)/backups:/backup ubuntu tar czf /backup/ollama-$$(date +%Y%m%d-%H%M%S).tar.gz /data
	@echo "✓ Backups saved to ./backups/"

