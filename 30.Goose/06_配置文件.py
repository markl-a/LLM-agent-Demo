#!/usr/bin/env python3
"""
Goose 配置文件詳解

展示 Goose 的配置選項和個性化設置:
1. 全局配置
2. 項目配置
3. 環境變量
4. 團隊配置
5. 配置最佳實踐

作者: AI Agent
日期: 2024
"""

import yaml
from pathlib import Path
from typing import Dict, Any


class GooseConfigDemo:
    """Goose 配置示例"""

    def __init__(self):
        """初始化"""
        self.config_dir = Path.home() / ".config" / "goose"

    def global_config_example(self):
        """
        全局配置示例
        ~/.config/goose/config.yaml
        """
        print("\n" + "="*70)
        print("全局配置")
        print("="*70)

        global_config = """# Goose 全局配置文件
# 位置: ~/.config/goose/config.yaml

# ============================================================================
# LLM 提供商設置
# ============================================================================
provider:
  # 提供商類型: openai, anthropic, google, azure, ollama
  type: openai

  # 模型名稱
  model: gpt-4-turbo-preview

  # API Key（建議使用環境變量）
  api_key: ${OPENAI_API_KEY}

  # API 基礎 URL（可選，用於代理或本地部署）
  base_url: null

  # 模型參數
  temperature: 0.7        # 創造性 (0.0-2.0)
  max_tokens: 4096        # 最大生成 tokens
  top_p: 1.0              # 核採樣
  frequency_penalty: 0.0  # 頻率懲罰
  presence_penalty: 0.0   # 出現懲罰

  # 請求超時（秒）
  timeout: 30

  # 重試設置
  max_retries: 3
  retry_delay: 1


# ============================================================================
# 工具配置
# ============================================================================
tools:
  # 啟用的工具模塊
  enabled:
    - file_operations     # 文件讀寫
    - shell_executor      # Shell 命令
    - git_operations      # Git 操作
    - web_search          # 網頁搜索
    - code_analyzer       # 代碼分析
    - database_tools      # 數據庫操作

  # 文件操作配置
  file_operations:
    # 允許的文件擴展名
    allowed_extensions:
      - .py
      - .js
      - .ts
      - .tsx
      - .java
      - .go
      - .rs
      - .cpp
      - .c
      - .h
      - .md
      - .txt
      - .json
      - .yaml
      - .toml
      - .xml
      - .html
      - .css
      - .scss

    # 禁止訪問的文件
    blocked_files:
      - "*.env"
      - "*.pem"
      - "*.key"
      - "credentials.*"
      - "secrets.*"

    # 最大文件大小（字節）
    max_file_size: 1048576  # 1MB

    # 自動備份
    auto_backup: true
    backup_dir: ~/.config/goose/backups

  # Shell 執行配置
  shell_executor:
    enabled: true

    # 執行超時（秒）
    timeout: 30

    # 允許的命令（白名單）
    allowed_commands:
      - git
      - npm
      - yarn
      - pip
      - python
      - python3
      - pytest
      - node
      - cargo
      - go
      - docker
      - docker-compose

    # 禁止的命令（黑名單）
    blocked_commands:
      - rm -rf /
      - dd
      - mkfs
      - format

    # 需要確認的危險命令
    requires_confirmation:
      - rm -rf
      - git push --force
      - docker system prune
      - npm publish

  # Git 操作配置
  git_operations:
    auto_add: false        # 自動 git add
    auto_commit: false     # 自動提交
    commit_prefix: "[AI]"  # 提交消息前綴
    branch_prefix: "ai/"   # 分支名稱前綴

  # Web 搜索配置
  web_search:
    enabled: true
    engine: google         # google, bing, duckduckgo
    max_results: 5
    timeout: 10


# ============================================================================
# 會話配置
# ============================================================================
session:
  # 自動保存
  auto_save: true

  # 保存間隔（秒）
  save_interval: 60

  # 最大歷史消息數
  max_history: 100

  # 會話存儲目錄
  storage_dir: ~/.config/goose/sessions

  # 自動清理舊會話（天）
  cleanup_after_days: 30


# ============================================================================
# 日誌配置
# ============================================================================
logging:
  # 日誌級別: DEBUG, INFO, WARNING, ERROR, CRITICAL
  level: INFO

  # 日誌文件
  file: ~/.config/goose/logs/goose.log

  # 日誌輪換
  rotation: daily        # daily, weekly, size
  max_size: 10485760    # 10MB (用於 size 輪換)

  # 保留天數
  retention: 7

  # 日誌格式
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

  # 詳細模式（包含調試信息）
  verbose: false


# ============================================================================
# UI 配置
# ============================================================================
ui:
  # 啟用顏色輸出
  color: true

  # 顏色方案: default, dark, light, custom
  color_scheme: default

  # 啟用 Emoji
  emoji: true

  # 流式輸出
  streaming: true

  # 顯示進度條
  progress_bar: true

  # 自動換行
  word_wrap: true

  # 終端寬度（0 表示自動檢測）
  terminal_width: 0


# ============================================================================
# 性能配置
# ============================================================================
performance:
  # 啟用緩存
  cache_enabled: true

  # 緩存 TTL（秒）
  cache_ttl: 3600

  # 緩存目錄
  cache_dir: ~/.cache/goose

  # 並發工具執行數
  parallel_tools: 3

  # 請求批處理
  batch_requests: true
  batch_size: 10


# ============================================================================
# 安全配置
# ============================================================================
security:
  # 啟用沙箱模式
  sandbox_mode: false

  # 允許的目錄
  allowed_directories:
    - ~/projects
    - ~/workspace

  # 禁止的目錄
  blocked_directories:
    - /
    - /etc
    - /sys
    - /proc
    - ~/.ssh

  # 需要確認的操作
  require_confirmation:
    - delete_files
    - execute_shell
    - modify_system_files


# ============================================================================
# 插件配置
# ============================================================================
plugins:
  # 啟用的插件
  enabled:
    - my_custom_plugin

  # 插件目錄
  plugin_dir: ~/.config/goose/plugins

  # 自動更新插件
  auto_update: false


# ============================================================================
# 網絡配置
# ============================================================================
network:
  # HTTP 代理
  proxy: null
  # proxy: http://proxy.example.com:8080

  # HTTPS 代理
  https_proxy: null

  # 不使用代理的主機
  no_proxy:
    - localhost
    - 127.0.0.1

  # 驗證 SSL 證書
  verify_ssl: true


# ============================================================================
# 實驗性功能
# ============================================================================
experimental:
  # 啟用多模態支持
  multimodal: false

  # 啟用語音輸入
  voice_input: false

  # 啟用 Agent 自主模式
  autonomous_mode: false

  # 啟用記憶系統
  memory_system: false
"""

        print("\n配置文件:")
        print("-"*70)
        print(global_config)

    def project_config_example(self):
        """
        項目配置示例
        .goose/config.yaml
        """
        print("\n" + "="*70)
        print("項目配置")
        print("="*70)

        project_config = """# 項目特定配置
# 位置: .goose/config.yaml（項目根目錄）

# ============================================================================
# 項目信息
# ============================================================================
project:
  name: my-awesome-app
  version: "1.0.0"
  language: python
  framework: fastapi
  description: "一個很棒的應用程序"

  # 項目結構
  structure:
    source_dir: src
    test_dir: tests
    docs_dir: docs
    config_dir: config


# ============================================================================
# 代碼風格
# ============================================================================
style:
  # 代碼風格指南
  guide: pep8          # pep8, google, airbnb

  # 縮進
  indentation: 4       # 空格數
  use_tabs: false

  # 行長度
  max_line_length: 88  # Black 默認

  # 引號風格
  quotes: double       # single, double

  # 導入排序
  import_sort: isort   # isort, manual

  # 文檔字符串風格
  docstring_style: google  # google, numpy, sphinx


# ============================================================================
# 測試配置
# ============================================================================
testing:
  # 測試框架
  framework: pytest    # pytest, unittest, nose

  # 測試目錄
  test_directory: tests

  # 最小覆蓋率
  coverage_threshold: 80

  # 測試命令
  test_command: pytest tests/ -v --cov=src

  # 自動運行測試
  auto_run: false


# ============================================================================
# 文檔配置
# ============================================================================
documentation:
  # 文檔風格
  style: google        # google, numpy, sphinx

  # 自動生成文檔
  auto_generate: true

  # 文檔工具
  tool: sphinx         # sphinx, mkdocs

  # 輸出目錄
  output_dir: docs/build


# ============================================================================
# Git 配置
# ============================================================================
git:
  # 自動提交
  auto_commit: false

  # 提交消息模板
  commit_message_template: |
    {type}: {subject}

    {body}

    {footer}

  # 提交類型
  commit_types:
    - feat      # 新功能
    - fix       # Bug 修復
    - docs      # 文檔
    - style     # 格式
    - refactor  # 重構
    - test      # 測試
    - chore     # 雜項

  # 分支命名
  branch_prefix: ai/
  branch_format: "{prefix}{type}/{description}"


# ============================================================================
# 依賴管理
# ============================================================================
dependencies:
  # 包管理器
  manager: pip         # pip, poetry, pipenv

  # 自動安裝缺失的包
  auto_install: false

  # 自動更新依賴文件
  auto_update_lockfile: true


# ============================================================================
# 構建配置
# ============================================================================
build:
  # 構建命令
  command: python setup.py build

  # 構建輸出目錄
  output_dir: dist

  # 清理舊構建
  clean_before_build: true


# ============================================================================
# 部署配置
# ============================================================================
deployment:
  # 部署環境
  environments:
    - name: development
      url: http://localhost:8000

    - name: staging
      url: https://staging.example.com

    - name: production
      url: https://example.com

  # 部署前檢查
  pre_deploy_checks:
    - run_tests
    - check_coverage
    - lint_code


# ============================================================================
# 自定義命令
# ============================================================================
custom_commands:
  # 快速命令別名
  aliases:
    test: pytest tests/ -v
    lint: ruff check src/
    format: black src/ tests/
    type-check: mypy src/

  # 工作流
  workflows:
    ci:
      - lint
      - type-check
      - test

    deploy:
      - test
      - build
      - deploy-staging
"""

        print("\n項目配置文件:")
        print("-"*70)
        print(project_config)

    def environment_variables(self):
        """環境變量配置"""
        print("\n" + "="*70)
        print("環境變量")
        print("="*70)

        env_vars = """# Goose 環境變量
# 可以在 ~/.bashrc, ~/.zshrc 或 .env 文件中設置

# ============================================================================
# API Keys
# ============================================================================
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic Claude
export ANTHROPIC_API_KEY="sk-ant-..."

# Google Gemini
export GOOGLE_API_KEY="..."

# Azure OpenAI
export AZURE_OPENAI_API_KEY="..."
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT="your-deployment"

# ============================================================================
# Goose 配置
# ============================================================================
# 配置目錄
export GOOSE_CONFIG_DIR="~/.config/goose"

# 日誌級別
export GOOSE_LOG_LEVEL="INFO"

# 啟用調試模式
export GOOSE_DEBUG="false"

# 默認模型
export GOOSE_MODEL="gpt-4-turbo-preview"

# ============================================================================
# 代理設置
# ============================================================================
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="http://proxy.example.com:8080"
export NO_PROXY="localhost,127.0.0.1"

# ============================================================================
# 其他 API Keys
# ============================================================================
# DeepL 翻譯
export DEEPL_API_KEY="..."

# OpenWeather
export OPENWEATHER_API_KEY="..."

# GitHub Token
export GITHUB_TOKEN="ghp_..."
"""

        print("\n環境變量設置:")
        print("-"*70)
        print(env_vars)

        # .env 文件示例
        dotenv_example = """# .env 文件示例
# 位置: .env（項目根目錄或 ~/.config/goose/.env）

# LLM API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# 應用配置
DEBUG=false
LOG_LEVEL=INFO

# 數據庫
DATABASE_URL=postgresql://user:pass@localhost/dbname

# 其他服務
REDIS_URL=redis://localhost:6379
SLACK_WEBHOOK=https://hooks.slack.com/services/...
"""

        print("\n.env 文件示例:")
        print("-"*70)
        print(dotenv_example)

    def team_config_example(self):
        """團隊配置示例"""
        print("\n" + "="*70)
        print("團隊配置")
        print("="*70)

        team_config = """# 團隊共享配置
# 位置: .goose/team.yaml
# 提交到版本控制，團隊成員共享

# ============================================================================
# 團隊信息
# ============================================================================
team:
  name: development-team
  members:
    - alice@example.com
    - bob@example.com

# ============================================================================
# 代碼規範
# ============================================================================
standards:
  # 編碼規範
  coding:
    style_guide: pep8
    linter: ruff
    formatter: black
    type_checker: mypy

  # 提交規範
  commits:
    conventional: true
    require_issue_number: true
    message_max_length: 72

  # 審查規範
  review:
    min_approvals: 2
    require_tests: true
    require_docs: true


# ============================================================================
# 工具配置
# ============================================================================
tools:
  # 共享的自定義工具
  custom:
    - name: deploy_staging
      description: "部署到測試環境"
      command: ./scripts/deploy.sh staging

    - name: run_e2e_tests
      description: "運行端到端測試"
      command: npm run test:e2e

  # 代碼質量工具
  quality:
    - tool: ruff
      config: pyproject.toml

    - tool: black
      config: pyproject.toml

    - tool: mypy
      config: mypy.ini


# ============================================================================
# CI/CD 配置
# ============================================================================
ci_cd:
  # CI 管道
  pipeline:
    - stage: lint
      command: ruff check src/

    - stage: type-check
      command: mypy src/

    - stage: test
      command: pytest tests/ --cov=src

    - stage: build
      command: python -m build

  # 部署策略
  deployment:
    strategy: blue-green
    auto_rollback: true


# ============================================================================
# 通知配置
# ============================================================================
notifications:
  # Slack
  slack:
    enabled: true
    webhook: ${SLACK_WEBHOOK_URL}
    channel: "#dev-notifications"

  # Email
  email:
    enabled: false
    recipients:
      - team@example.com


# ============================================================================
# 模板配置
# ============================================================================
templates:
  # PR 模板
  pull_request: |
    ## 變更內容
    <!-- 描述這個 PR 的變更 -->

    ## 測試
    <!-- 如何測試這些變更 -->

    ## 檢查清單
    - [ ] 測試通過
    - [ ] 代碼已審查
    - [ ] 文檔已更新

  # Issue 模板
  issue: |
    ## 問題描述
    <!-- 清楚地描述問題 -->

    ## 重現步驟
    1.
    2.
    3.

    ## 預期行為
    <!-- 應該發生什麼 -->

    ## 實際行為
    <!-- 實際發生了什麼 -->
"""

        print("\n團隊配置文件:")
        print("-"*70)
        print(team_config)

    def configuration_best_practices(self):
        """配置最佳實踐"""
        print("\n" + "="*70)
        print("配置最佳實踐")
        print("="*70)

        practices = """
1. 配置層級
   全局配置 < 項目配置 < 環境變量 < 命令行參數

2. 敏感信息
   ✓ 使用環境變量存儲 API Keys
   ✓ 使用 .env 文件（不提交到版本控制）
   ✗ 不要在配置文件中硬編碼密鑰

3. 團隊協作
   ✓ 提交團隊共享配置到版本控制
   ✓ 使用 .gitignore 忽略個人配置
   ✓ 提供配置示例文件

4. 文檔化
   ✓ 為每個配置選項添加註釋
   ✓ 提供配置示例
   ✓ 說明默認值

5. 驗證
   ✓ 在啟動時驗證配置
   ✓ 提供有用的錯誤消息
   ✓ 檢查必需的配置項

6. 版本控制
   提交:
   - .goose/config.yaml（項目配置）
   - .goose/team.yaml（團隊配置）

   忽略:
   - .env（環境變量）
   - .goose/local.yaml（個人配置）

7. 配置覆蓋順序
   1. 默認配置
   2. 全局配置（~/.config/goose/config.yaml）
   3. 項目配置（.goose/config.yaml）
   4. 環境變量
   5. 命令行參數

示例 .gitignore:
```
# Goose
.env
.goose/local.yaml
.goose/sessions/
```

示例配置文件結構:
```
項目/
├── .goose/
│   ├── config.yaml          # 項目配置（提交）
│   ├── team.yaml            # 團隊配置（提交）
│   ├── local.yaml           # 個人配置（忽略）
│   └── config.example.yaml  # 配置示例（提交）
├── .env                     # 環境變量（忽略）
└── .env.example             # 環境變量示例（提交）
```
"""

        print(practices)


def main():
    """主函數"""
    print("="*70)
    print("Goose 配置文件教程")
    print("="*70)

    demo = GooseConfigDemo()

    sections = [
        ("全局配置", demo.global_config_example),
        ("項目配置", demo.project_config_example),
        ("環境變量", demo.environment_variables),
        ("團隊配置", demo.team_config_example),
        ("最佳實踐", demo.configuration_best_practices),
    ]

    print("\n執行所有示例...\n")

    for name, func in sections:
        func()

    print("\n" + "="*70)
    print("教程完成！")
    print("="*70)

    print("\n關鍵要點:")
    print("1. 使用分層配置管理不同場景")
    print("2. 敏感信息使用環境變量")
    print("3. 團隊配置提交到版本控制")
    print("4. 個人配置保持在本地")
    print("5. 提供配置示例文件")

    print("\n下一步: 閱讀 07_多模型支持.py")


if __name__ == "__main__":
    main()
