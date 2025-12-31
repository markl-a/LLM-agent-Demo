"""
DeepEval CI/CD 整合示例
展示如何將 DeepEval 整合到持續集成流程
"""

def github_actions_example():
    """GitHub Actions 整合示例"""
    print("\n" + "=" * 60)
    print("GitHub Actions 整合")
    print("=" * 60)

    yaml_content = """
# .github/workflows/deepeval-tests.yml

name: DeepEval Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  llm-tests:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install deepeval openai pytest
        pip install -r requirements.txt

    - name: Run DeepEval tests
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        pytest tests/ -v --tb=short

    - name: Upload test results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: deepeval-results
        path: test-results/

    - name: Comment PR with results
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          // 添加評論到 PR
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: 'DeepEval 測試完成！查看詳細結果。'
          })
    """

    print(yaml_content)

    print("\n配置步驟:")
    print("1. 在 GitHub 倉庫中創建 .github/workflows/deepeval-tests.yml")
    print("2. 在倉庫設置中添加 OPENAI_API_KEY secret")
    print("3. 推送代碼觸發工作流")
    print("4. 查看 Actions 標籤頁中的測試結果")


def gitlab_ci_example():
    """GitLab CI 整合示例"""
    print("\n" + "=" * 60)
    print("GitLab CI 整合")
    print("=" * 60)

    yaml_content = """
# .gitlab-ci.yml

stages:
  - test
  - report

llm-tests:
  stage: test
  image: python:3.9
  variables:
    OPENAI_API_KEY: $OPENAI_API_KEY
  before_script:
    - pip install deepeval openai pytest
    - pip install -r requirements.txt
  script:
    - pytest tests/ -v --junitxml=report.xml
  artifacts:
    when: always
    reports:
      junit: report.xml
    paths:
      - report.xml
  only:
    - main
    - merge_requests

generate-report:
  stage: report
  dependencies:
    - llm-tests
  script:
    - echo "生成評估報告"
  only:
    - main
    """

    print(yaml_content)

    print("\n配置步驟:")
    print("1. 在倉庫根目錄創建 .gitlab-ci.yml")
    print("2. 在 GitLab 設置中添加 OPENAI_API_KEY 變量")
    print("3. 推送代碼觸發 pipeline")


def pytest_configuration():
    """pytest 配置示例"""
    print("\n" + "=" * 60)
    print("pytest 配置")
    print("=" * 60)

    print("\n1. pytest.ini 配置:")
    print("""
# pytest.ini

[pytest]
markers =
    llm: LLM 相關測試
    critical: 關鍵測試，必須通過
    slow: 慢速測試
    integration: 整合測試

testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

addopts =
    -v
    --tb=short
    --strict-markers
    -m "not slow"  # 默認跳過慢速測試

# DeepEval 特定配置
env =
    DEEPEVAL_TELEMETRY_OPT_OUT=YES
    """)

    print("\n2. conftest.py 配置:")
    print("""
# conftest.py

import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric

@pytest.fixture
def default_metrics():
    '''默認評估指標'''
    return [
        AnswerRelevancyMetric(threshold=0.7),
    ]

@pytest.fixture
def rag_system():
    '''RAG 系統 fixture'''
    # 初始化你的 RAG 系統
    pass

def pytest_configure(config):
    '''pytest 配置鉤子'''
    config.addinivalue_line(
        "markers", "llm: mark test as LLM test"
    )
    """)


def quality_gates():
    """質量門控示例"""
    print("\n" + "=" * 60)
    print("質量門控")
    print("=" * 60)

    print("\n質量門控可以確保代碼質量:")

    print("\n1. 設定通過標準:")
    standards = [
        {
            "指標": "答案相關性",
            "閾值": "≥ 0.7",
            "必須通過": True
        },
        {
            "指標": "忠實度",
            "閾值": "≥ 0.7",
            "必須通過": True
        },
        {
            "指標": "毒性",
            "閾值": "< 0.3",
            "必須通過": True
        },
        {
            "指標": "測試覆蓋率",
            "閾值": "≥ 80%",
            "必須通過": False
        }
    ]

    for standard in standards:
        required = "✓ 必須" if standard['必須通過'] else "○ 可選"
        print(f"  {required} {standard['指標']}: {standard['閾值']}")

    print("\n2. 實施門控:")
    print("""
# 在 CI 腳本中

# 運行測試
pytest tests/ -v

# 檢查結果
if [ $? -eq 0 ]; then
    echo "✓ 質量門控通過"
    exit 0
else
    echo "✗ 質量門控失敗"
    exit 1
fi
    """)


def cost_optimization():
    """成本優化策略"""
    print("\n" + "=" * 60)
    print("CI 中的成本優化")
    print("=" * 60)

    strategies = [
        {
            "策略": "測試分層",
            "方法": [
                "快速測試在每次提交時運行",
                "完整測試只在 PR 和主分支運行",
                "昂貴測試只在發布前運行",
                "使用 pytest 標記控制"
            ]
        },
        {
            "策略": "緩存結果",
            "方法": [
                "緩存評估結果避免重複",
                "只測試變更的部分",
                "使用 git diff 識別變更",
                "緩存依賴安裝"
            ]
        },
        {
            "策略": "並行執行",
            "方法": [
                "使用 pytest-xdist 並行測試",
                "分配到多個 runner",
                "優化測試順序",
                "先運行快速測試"
            ]
        },
        {
            "策略": "使用更便宜的模型",
            "方法": [
                "開發環境使用 gpt-3.5-turbo",
                "生產環境使用 gpt-4",
                "本地模型進行初步測試",
                "只在必要時調用 API"
            ]
        }
    ]

    for i, strategy in enumerate(strategies, 1):
        print(f"\n{i}. {strategy['策略']}")
        for method in strategy['方法']:
            print(f"   • {method}")


def monitoring_integration():
    """監控整合"""
    print("\n" + "=" * 60)
    print("監控整合")
    print("=" * 60)

    print("\n整合監控系統追蹤 LLM 性能:")

    print("\n1. 收集指標:")
    print("""
# 示例：發送指標到 Datadog

from datadog import statsd

def track_llm_metrics(test_results):
    for result in test_results:
        # 發送指標
        statsd.gauge(
            'llm.answer_relevancy',
            result.relevancy_score,
            tags=['env:ci', 'test:llm']
        )

        statsd.increment(
            'llm.tests.run',
            tags=['env:ci']
        )

        if result.passed:
            statsd.increment('llm.tests.passed')
        else:
            statsd.increment('llm.tests.failed')
    """)

    print("\n2. 設置告警:")
    alert_rules = [
        "答案相關性低於 0.6 時告警",
        "測試失敗率超過 20% 時告警",
        "評估延遲超過 5 秒時告警",
        "成本異常增長時告警"
    ]

    for rule in alert_rules:
        print(f"  • {rule}")


def best_practices():
    """CI 整合最佳實踐"""
    print("\n" + "=" * 60)
    print("CI 整合最佳實踐")
    print("=" * 60)

    practices = [
        {
            "實踐": "快速反饋",
            "說明": "優化測試速度，快速發現問題",
            "建議": [
                "先運行快速測試",
                "並行執行測試",
                "使用緩存加速"
            ]
        },
        {
            "實踐": "穩定性",
            "說明": "確保測試結果可靠",
            "建議": [
                "處理 API 限流",
                "重試失敗的測試",
                "處理網絡問題"
            ]
        },
        {
            "實踐": "安全性",
            "說明": "保護敏感信息",
            "建議": [
                "使用 secrets 管理 API key",
                "不在日誌中輸出密鑰",
                "限制訪問權限"
            ]
        },
        {
            "實踐": "可維護性",
            "說明": "保持配置簡潔清晰",
            "建議": [
                "模塊化配置",
                "文檔化流程",
                "定期審查和更新"
            ]
        }
    ]

    for i, practice in enumerate(practices, 1):
        print(f"\n{i}. {practice['實踐']}")
        print(f"   {practice['說明']}")
        print(f"   建議:")
        for suggestion in practice['建議']:
            print(f"   • {suggestion}")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("DeepEval CI/CD 整合教程")
    print("=" * 60)

    print("\n為什麼要整合到 CI/CD？")
    print("  • 自動化質量檢查")
    print("  • 防止性能退化")
    print("  • 持續監控系統表現")
    print("  • 提高開發效率")

    print("\n主要 CI 平台:")
    print("  • GitHub Actions")
    print("  • GitLab CI")
    print("  • Jenkins")
    print("  • CircleCI")

    input("\n按 Enter 查看配置示例...")

    github_actions_example()
    gitlab_ci_example()
    pytest_configuration()
    quality_gates()
    cost_optimization()
    monitoring_integration()
    best_practices()

    print("\n" + "=" * 60)
    print("CI 整合示例完成！")
    print("=" * 60)

    print("\n關鍵要點:")
    print("  • CI/CD 整合實現自動化質量保證")
    print("  • 需要平衡測試覆蓋和成本")
    print("  • 快速反饋循環很重要")
    print("  • 持續監控和優化")

    print("\n下一步:")
    print("  1. 選擇適合的 CI 平台")
    print("  2. 配置工作流")
    print("  3. 設定質量門控")
    print("  4. 優化成本和速度")
    print("  5. 整合監控系統")


if __name__ == "__main__":
    main()
