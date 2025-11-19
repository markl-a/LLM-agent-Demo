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

setup-env: ## 設置環境變數文件
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)創建 .env 文件...$(NC)"; \
		cp .env.example .env; \
		echo "$(GREEN)✓ .env 文件已創建，請編輯並添加您的 API keys$(NC)"; \
	else \
		echo "$(YELLOW).env 文件已存在$(NC)"; \
	fi

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

##@ 代碼質量

lint: ## 運行所有 linting 檢查
	@echo "$(GREEN)運行 linting 檢查...$(NC)"
	$(PYTHON) -m flake8 .
	$(PYTHON) -m ruff check .
	@echo "$(GREEN)✓ Linting 完成$(NC)"

lint-fix: ## 自動修復 linting 問題
	@echo "$(GREEN)自動修復 linting 問題...$(NC)"
	$(PYTHON) -m ruff check --fix .
	@echo "$(GREEN)✓ 自動修復完成$(NC)"

format: ## 格式化代碼
	@echo "$(GREEN)格式化代碼...$(NC)"
	$(PYTHON) -m black .
	$(PYTHON) -m isort .
	@echo "$(GREEN)✓ 代碼格式化完成$(NC)"

format-check: ## 檢查代碼格式（不修改）
	@echo "$(GREEN)檢查代碼格式...$(NC)"
	$(PYTHON) -m black --check .
	$(PYTHON) -m isort --check-only .

type-check: ## 運行類型檢查
	@echo "$(GREEN)運行類型檢查...$(NC)"
	$(PYTHON) -m mypy .
	@echo "$(GREEN)✓ 類型檢查完成$(NC)"

security-check: ## 運行安全檢查
	@echo "$(GREEN)運行安全檢查...$(NC)"
	$(PYTHON) -m bandit -r . -f json -o bandit-report.json || true
	@echo "$(GREEN)✓ 安全檢查完成（報告: bandit-report.json）$(NC)"

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
	rm -f bandit-report.json
	@echo "$(GREEN)✓ 清理完成$(NC)"

clean-all: clean ## 清理所有文件（包括向量數據庫）
	@echo "$(YELLOW)清理所有文件（包括向量數據庫）...$(NC)"
	find . -type d -name 'vectorstore' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name 'chroma_db' -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ 完全清理完成$(NC)"

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

quick-start: install-dev setup-env ## 快速開始（安裝依賴並設置環境）
	@echo "$(GREEN)=== 快速開始完成 ===$(NC)"
	@echo "接下來的步驟:"
	@echo "  1. 編輯 .env 文件並添加你的 API keys"
	@echo "  2. 運行 'make test' 確保一切正常"
	@echo "  3. 查看 README.md 了解更多信息"

dev: install-dev test lint ## 開發流程（安裝、測試、檢查）
	@echo "$(GREEN)✓ 開發環境準備完成$(NC)"

ci: format-check lint test ## CI 流程（格式檢查、linting、測試）
	@echo "$(GREEN)✓ CI 檢查通過$(NC)"

deploy-prep: clean test lint ## 部署前準備
	@echo "$(GREEN)✓ 部署前檢查完成$(NC)"
