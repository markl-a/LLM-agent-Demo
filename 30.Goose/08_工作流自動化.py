#!/usr/bin/env python3
"""
Goose 工作流自動化示例

展示如何使用 Goose 自動化開發工作流:
1. CI/CD 集成
2. 自動化測試
3. 代碼質量檢查
4. 自動部署
5. 定時任務

作者: AI Agent
日期: 2024
"""

from typing import List, Dict
from pathlib import Path


class WorkflowAutomationDemo:
    """工作流自動化演示"""

    def __init__(self):
        """初始化"""
        pass

    def ci_cd_integration(self):
        """
        CI/CD 集成示例
        """
        print("\n" + "="*70)
        print("CI/CD 集成")
        print("="*70)

        # GitHub Actions 集成
        github_actions = """# .github/workflows/goose-ci.yml
name: Goose AI Code Review

on:
  pull_request:
    types: [opened, synchronize]
  push:
    branches: [main, develop]

jobs:
  ai-code-review:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Goose
        run: |
          pip install goose-ai

      - name: Run AI Code Review
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          goose "審查這個 PR 的變更，關注安全性和性能問題" > review.md

      - name: Post Review Comment
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const review = fs.readFileSync('review.md', 'utf8');

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '## 🤖 AI Code Review\\n\\n' + review
            });

  automated-tests:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install goose-ai pytest

      - name: Generate Tests with Goose
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          goose "為新增的代碼生成單元測試"

      - name: Run Tests
        run: |
          pytest tests/ -v --cov=src

      - name: Upload Coverage
        uses: codecov/codecov-action@v3
"""

        print("\n📝 GitHub Actions 配置:")
        print("-"*70)
        print(github_actions)

        # GitLab CI 集成
        gitlab_ci = """# .gitlab-ci.yml
image: python:3.11

stages:
  - review
  - test
  - deploy

ai-code-review:
  stage: review
  script:
    - pip install goose-ai
    - goose "審查代碼變更" > review.md
    - cat review.md
  artifacts:
    paths:
      - review.md
  only:
    - merge_requests

ai-test-generation:
  stage: test
  script:
    - pip install goose-ai pytest
    - goose "為缺少測試的代碼生成測試"
    - pytest tests/ -v --cov=src
  coverage: '/^TOTAL.+?(\\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

ai-deploy:
  stage: deploy
  script:
    - pip install goose-ai
    - goose "檢查部署前的檢查清單"
    - ./deploy.sh
  only:
    - main
"""

        print("\n📝 GitLab CI 配置:")
        print("-"*70)
        print(gitlab_ci)

    def pre_commit_hooks(self):
        """
        Pre-commit 鉤子集成
        """
        print("\n" + "="*70)
        print("Pre-commit 鉤子")
        print("="*70)

        pre_commit_config = """# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      # AI 代碼審查
      - id: goose-review
        name: Goose AI Review
        entry: bash -c 'goose "快速審查這次提交的代碼" || true'
        language: system
        pass_filenames: false
        stages: [commit]

      # 自動生成文檔
      - id: goose-docs
        name: Goose Auto Docs
        entry: bash -c 'goose "為修改的 Python 文件添加/更新 docstring"'
        language: system
        files: \\.py$
        stages: [commit]

      # 代碼質量檢查
      - id: goose-quality
        name: Goose Quality Check
        entry: bash -c 'goose "檢查代碼質量問題（PEP 8, 安全性）"'
        language: system
        files: \\.py$
        stages: [commit]

  # 標準的 pre-commit 鉤子
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.270
    hooks:
      - id: ruff
"""

        print("\n配置文件:")
        print("-"*70)
        print(pre_commit_config)

        # 安裝和使用
        setup = """
# 安裝 pre-commit
$ pip install pre-commit

# 安裝鉤子
$ pre-commit install

# 手動運行所有鉤子
$ pre-commit run --all-files

# 更新鉤子版本
$ pre-commit autoupdate

# 提交時自動運行
$ git commit -m "your message"
# 鉤子會自動運行，包括 Goose 審查
"""

        print("\n安裝和使用:")
        print("-"*70)
        print(setup)

    def automated_testing_workflow(self):
        """
        自動化測試工作流
        """
        print("\n" + "="*70)
        print("自動化測試工作流")
        print("="*70)

        test_workflow = """# scripts/auto-test.sh
#!/bin/bash

set -e

echo "🤖 Goose 自動化測試工作流"
echo "================================"

# 1. 分析代碼找出缺少測試的部分
echo "1️⃣ 分析測試覆蓋率..."
goose "分析項目的測試覆蓋率，找出缺少測試的函數和類" > coverage-analysis.md

# 2. 生成缺失的測試
echo "2️⃣ 生成缺失的測試..."
goose "為覆蓋率報告中未測試的代碼生成 pytest 測試"

# 3. 運行測試
echo "3️⃣ 運行測試套件..."
pytest tests/ -v --cov=src --cov-report=html --cov-report=term

# 4. 分析失敗的測試
if [ $? -ne 0 ]; then
    echo "❌ 測試失敗，使用 Goose 分析..."
    goose "分析失敗的測試，找出原因並提供修復建議" > test-failures.md
    exit 1
fi

# 5. 檢查覆蓋率閾值
echo "4️⃣ 檢查覆蓋率..."
coverage report --fail-under=80

# 6. 生成測試報告
echo "5️⃣ 生成測試報告..."
goose "基於測試結果生成詳細的測試報告" > test-report.md

echo "✅ 測試工作流完成！"
"""

        print("\n自動化測試腳本:")
        print("-"*70)
        print(test_workflow)

        # Python 測試工作流
        python_workflow = """# scripts/test_workflow.py
import subprocess
import sys
from pathlib import Path

def run_goose_command(prompt):
    \"\"\"運行 Goose 命令\"\"\"
    result = subprocess.run(
        ['goose', prompt],
        capture_output=True,
        text=True
    )
    return result.stdout

def run_tests():
    \"\"\"運行測試套件\"\"\"
    result = subprocess.run(
        ['pytest', 'tests/', '-v', '--cov=src'],
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stdout

def main():
    print("🤖 啟動自動化測試工作流...")

    # 1. 生成測試
    print("\\n1. 生成缺失的測試...")
    run_goose_command("分析並生成缺失的測試")

    # 2. 運行測試
    print("\\n2. 運行測試...")
    success, output = run_tests()

    if not success:
        print("\\n❌ 測試失敗，分析問題...")
        analysis = run_goose_command(
            f"分析以下測試失敗輸出並提供修復建議：\\n{output}"
        )
        print(analysis)
        sys.exit(1)

    # 3. 代碼質量檢查
    print("\\n3. 代碼質量檢查...")
    quality_report = run_goose_command("審查測試代碼質量")
    print(quality_report)

    print("\\n✅ 測試工作流完成！")

if __name__ == "__main__":
    main()
"""

        print("\nPython 測試工作流:")
        print("-"*70)
        print(python_workflow)

    def deployment_automation(self):
        """
        部署自動化
        """
        print("\n" + "="*70)
        print("部署自動化")
        print("="*70)

        deploy_script = """# scripts/deploy.sh
#!/bin/bash

set -e

ENVIRONMENT=${1:-staging}

echo "🚀 部署到 $ENVIRONMENT"
echo "================================"

# 1. 部署前檢查
echo "1️⃣ 部署前檢查..."
goose "執行部署前檢查清單：測試、構建、配置" > pre-deploy-check.md

if grep -q "❌" pre-deploy-check.md; then
    echo "❌ 部署前檢查失敗"
    cat pre-deploy-check.md
    exit 1
fi

# 2. 構建
echo "2️⃣ 構建應用..."
goose "生成 $ENVIRONMENT 環境的構建腳本並執行"

# 3. 數據庫遷移檢查
echo "3️⃣ 檢查數據庫遷移..."
goose "分析數據庫遷移文件，確保安全性" > migration-check.md

# 4. 部署
echo "4️⃣ 執行部署..."
case $ENVIRONMENT in
    staging)
        kubectl apply -f k8s/staging/
        ;;
    production)
        goose "生成 production 部署的安全確認清單" > deploy-confirm.md
        echo "請確認以下內容："
        cat deploy-confirm.md
        read -p "繼續部署？(yes/no) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kubectl apply -f k8s/production/
        fi
        ;;
esac

# 5. 部署後驗證
echo "5️⃣ 部署後驗證..."
goose "生成部署驗證測試腳本並執行"

# 6. 生成部署報告
echo "6️⃣ 生成部署報告..."
goose "生成部署報告，包括版本、時間、變更摘要" > deployment-report.md

echo "✅ 部署完成！"
"""

        print("\n部署腳本:")
        print("-"*70)
        print(deploy_script)

        # Docker 部署自動化
        docker_deploy = """# scripts/docker-deploy.py
from goose_automation import GooseAutomation

def deploy_docker():
    goose = GooseAutomation()

    # 1. 生成 Dockerfile
    goose.execute("為這個 Python FastAPI 應用生成優化的 Dockerfile")

    # 2. 生成 docker-compose.yml
    goose.execute("生成 docker-compose.yml，包括應用、數據庫、Redis")

    # 3. 安全檢查
    security = goose.execute("檢查 Dockerfile 的安全性問題")
    if "問題" in security:
        print("⚠️ 發現安全問題：", security)

    # 4. 構建鏡像
    goose.execute("生成 Docker 鏡像構建腳本並執行")

    # 5. 推送到倉庫
    goose.execute("將鏡像推送到 Docker Hub")

    # 6. 部署到 Kubernetes
    goose.execute("生成 Kubernetes 部署配置並應用")

if __name__ == "__main__":
    deploy_docker()
"""

        print("\nDocker 部署自動化:")
        print("-"*70)
        print(docker_deploy)

    def scheduled_tasks(self):
        """
        定時任務
        """
        print("\n" + "="*70)
        print("定時任務")
        print("="*70)

        cron_jobs = """# 定時任務配置

# 1. 每日代碼質量報告
# crontab: 0 9 * * * /path/to/daily-quality-report.sh

#!/bin/bash
# daily-quality-report.sh

echo "📊 生成每日代碼質量報告..."

goose "分析項目代碼質量，生成報告包括：
1. 代碼複雜度分析
2. 技術債務評估
3. 安全漏洞掃描
4. 性能瓶頸識別
5. 改進建議" > daily-report-$(date +%Y%m%d).md

# 發送到 Slack
curl -X POST $SLACK_WEBHOOK \\
    -H 'Content-Type: application/json' \\
    -d "{\"text\": \"每日代碼質量報告已生成\"}"

# 2. 每週依賴更新檢查
# crontab: 0 10 * * 1 /path/to/weekly-dependency-check.sh

#!/bin/bash
# weekly-dependency-check.sh

echo "🔄 檢查依賴更新..."

goose "檢查 requirements.txt 中的依賴包更新：
1. 列出有可用更新的包
2. 檢查更新的安全性
3. 評估更新的影響
4. 生成更新建議" > dependency-updates.md

# 創建 PR（如果有更新）
if [ -s dependency-updates.md ]; then
    git checkout -b auto/dependency-updates
    git add requirements.txt
    git commit -m "chore: 依賴包更新建議"
    git push origin auto/dependency-updates
    gh pr create --title "🤖 自動依賴更新" \\
        --body-file dependency-updates.md
fi

# 3. 每月技術債務審查
# crontab: 0 9 1 * * /path/to/monthly-tech-debt.sh

#!/bin/bash
# monthly-tech-debt.sh

echo "💳 技術債務審查..."

goose "進行全面的技術債務審查：
1. 識別過時的代碼和技術棧
2. 評估重構優先級
3. 估算修復成本
4. 制定改進路線圖" > tech-debt-$(date +%Y%m).md

# 4. 實時監控（每小時）
# crontab: 0 * * * * /path/to/hourly-monitor.sh

#!/bin/bash
# hourly-monitor.sh

# 檢查錯誤日誌
ERROR_COUNT=$(grep -c "ERROR" /var/log/app.log)

if [ $ERROR_COUNT -gt 10 ]; then
    echo "🚨 檢測到大量錯誤..."

    goose "分析錯誤日誌 /var/log/app.log：
    1. 識別主要錯誤類型
    2. 找出錯誤模式
    3. 提供修復建議
    4. 生成告警報告" > error-analysis.md

    # 發送告警
    curl -X POST $ALERT_WEBHOOK -d @error-analysis.md
fi
"""

        print("\n定時任務配置:")
        print("-"*70)
        print(cron_jobs)

        # Python 定時任務
        python_scheduler = """# scheduled_tasks.py
from apscheduler.schedulers.blocking import BlockingScheduler
from goose_automation import GooseAutomation
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

goose = GooseAutomation()

def daily_code_review():
    \"\"\"每日代碼審查\"\"\"
    logger.info("開始每日代碼審查...")

    report = goose.execute(
        "審查昨天的所有提交，生成代碼質量報告"
    )

    # 保存報告
    with open(f"reports/daily-{date.today()}.md", "w") as f:
        f.write(report)

def weekly_dependency_update():
    \"\"\"每週依賴更新\"\"\"
    logger.info("檢查依賴更新...")

    updates = goose.execute(
        "檢查並更新項目依賴，生成變更日誌"
    )

    if "更新可用" in updates:
        # 創建 PR
        create_dependency_pr(updates)

def monthly_tech_debt():
    \"\"\"每月技術債務審查\"\"\"
    logger.info("技術債務審查...")

    debt_report = goose.execute(
        "全面審查技術債務，制定改進計劃"
    )

    # 生成報告並發送
    send_report_to_team(debt_report)

# 設置調度器
scheduler = BlockingScheduler()

# 每天早上 9 點
scheduler.add_job(
    daily_code_review,
    'cron',
    hour=9,
    minute=0
)

# 每週一早上 10 點
scheduler.add_job(
    weekly_dependency_update,
    'cron',
    day_of_week='mon',
    hour=10,
    minute=0
)

# 每月 1 號早上 9 點
scheduler.add_job(
    monthly_tech_debt,
    'cron',
    day=1,
    hour=9,
    minute=0
)

if __name__ == "__main__":
    logger.info("啟動定時任務調度器...")
    scheduler.start()
"""

        print("\nPython 定時任務:")
        print("-"*70)
        print(python_scheduler)

    def makefile_automation(self):
        """
        Makefile 自動化
        """
        print("\n" + "="*70)
        print("Makefile 自動化")
        print("="*70)

        makefile = """# Makefile
.PHONY: help install test review deploy

help:
\t@echo "可用命令："
\t@echo "  make install   - 安裝依賴"
\t@echo "  make test      - 運行測試"
\t@echo "  make review    - AI 代碼審查"
\t@echo "  make deploy    - 部署應用"

install:
\t@echo "📦 安裝依賴..."
\tpip install -r requirements.txt
\tpip install goose-ai

test:
\t@echo "🧪 運行測試..."
\tgoose "生成缺失的測試"
\tpytest tests/ -v --cov=src

review:
\t@echo "🔍 AI 代碼審查..."
\tgoose "審查所有 Python 文件，檢查：\\n\\
\t1. 代碼質量\\n\\
\t2. 安全性問題\\n\\
\t3. 性能瓶頸\\n\\
\t4. 最佳實踐" > code-review.md
\t@cat code-review.md

lint:
\t@echo "✨ 代碼格式化..."
\tgoose "運行 black 和 ruff 格式化代碼"
\tblack src/ tests/
\truff check src/ --fix

docs:
\t@echo "📚 生成文檔..."
\tgoose "為所有模塊生成文檔"
\tsphinx-build docs/ docs/_build

deploy-staging:
\t@echo "🚀 部署到 Staging..."
\tgoose "執行部署前檢查"
\t./scripts/deploy.sh staging

deploy-prod:
\t@echo "🚀 部署到 Production..."
\t@echo "⚠️  確認部署到生產環境？(yes/no)"
\t@read confirm && [ "$$confirm" = "yes" ] || exit 1
\tgoose "生成生產部署檢查清單並執行"
\t./scripts/deploy.sh production

clean:
\t@echo "🧹 清理..."
\tfind . -type d -name __pycache__ -exec rm -rf {} +
\tfind . -type f -name "*.pyc" -delete
\trm -rf .pytest_cache .coverage htmlcov/

ai-refactor:
\t@echo "♻️  AI 重構..."
\tgoose "分析項目並建議重構機會"

ai-optimize:
\t@echo "⚡ AI 性能優化..."
\tgoose "分析性能瓶頸並優化"

security-scan:
\t@echo "🔒 安全掃描..."
\tgoose "執行安全掃描，檢查漏洞"
"""

        print("\nMakefile:")
        print("-"*70)
        print(makefile)


def main():
    """主函數"""
    print("="*70)
    print("Goose 工作流自動化教程")
    print("="*70)

    demo = WorkflowAutomationDemo()

    sections = [
        ("CI/CD 集成", demo.ci_cd_integration),
        ("Pre-commit 鉤子", demo.pre_commit_hooks),
        ("自動化測試", demo.automated_testing_workflow),
        ("部署自動化", demo.deployment_automation),
        ("定時任務", demo.scheduled_tasks),
        ("Makefile 自動化", demo.makefile_automation),
    ]

    print("\n執行所有示例...\n")

    for name, func in sections:
        func()

    print("\n" + "="*70)
    print("教程完成！")
    print("="*70)

    print("\n關鍵要點:")
    print("1. 將 Goose 集成到 CI/CD 管道")
    print("2. 使用 pre-commit 鉤子自動審查")
    print("3. 自動化測試生成和執行")
    print("4. 智能部署流程")
    print("5. 定時任務持續優化代碼")

    print("\n下一步: 閱讀 09_與IDE整合.py")


if __name__ == "__main__":
    main()
