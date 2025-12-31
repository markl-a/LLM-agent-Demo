"""
PromptFlow 最佳實踐示例

本示例展示：
1. 項目結構組織
2. 代碼質量和測試
3. 性能優化技巧
4. 生產環境準備
"""

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.tree import Tree
from rich.table import Table

console = Console()


def show_project_structure():
    """推薦的項目結構"""
    console.print("\n[cyan]1. 推薦的項目結構[/cyan]\n")

    structure = """my_promptflow_project/
├── flows/                      # Flow 定義
│   ├── main_flow/
│   │   ├── flow.dag.yaml
│   │   ├── requirements.txt
│   │   ├── nodes/
│   │   │   ├── preprocess.py
│   │   │   ├── llm_call.py
│   │   │   └── postprocess.py
│   │   └── prompts/
│   │       └── main_prompt.jinja2
│   └── eval_flow/
│       ├── flow.dag.yaml
│       └── evaluate.py
│
├── connections/                # 連接配置
│   ├── azure_openai.yaml
│   └── custom_api.yaml
│
├── data/                       # 數據文件
│   ├── train/
│   │   └── train_data.jsonl
│   └── test/
│       └── test_data.jsonl
│
├── tests/                      # 測試文件
│   ├── test_flows.py
│   ├── test_nodes.py
│   └── fixtures/
│
├── scripts/                    # 腳本
│   ├── prepare_data.py
│   ├── run_evaluation.py
│   └── deploy.sh
│
├── docs/                       # 文檔
│   ├── architecture.md
│   └── deployment.md
│
├── .github/                    # CI/CD
│   └── workflows/
│       ├── test.yml
│       └── deploy.yml
│
├── .env.example                # 環境變量模板
├── .gitignore
├── README.md
└── requirements.txt            # 項目依賴"""

    console.print(Panel(structure, title="項目結構", border_style="cyan"))
    console.print()


def show_code_quality():
    """代碼質量實踐"""
    console.print("[cyan]2. 代碼質量實踐[/cyan]\n")

    console.print("[yellow]良好的節點函數示例:[/yellow]\n")

    good_code = """from promptflow import tool
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


@tool
def process_documents(
    documents: List[Dict[str, str]],
    max_length: int = 500,
    min_score: float = 0.7
) -> List[Dict[str, any]]:
    \"\"\"
    處理和過濾文檔列表

    Args:
        documents: 文檔列表，每個文檔包含 'text' 和 'score' 字段
        max_length: 文檔最大長度
        min_score: 最小分數閾值

    Returns:
        過濾和處理後的文檔列表

    Raises:
        ValueError: 如果輸入參數無效
    \"\"\"
    # 驗證輸入
    if not documents:
        logger.warning("收到空文檔列表")
        return []

    if min_score < 0 or min_score > 1:
        raise ValueError(f"min_score 必須在 0-1 之間，收到: {min_score}")

    processed = []

    for i, doc in enumerate(documents):
        try:
            # 檢查必需字段
            if 'text' not in doc or 'score' not in doc:
                logger.warning(f"文檔 {i} 缺少必需字段，跳過")
                continue

            # 過濾條件
            if doc['score'] < min_score:
                continue

            # 處理文本
            text = doc['text'].strip()
            if len(text) > max_length:
                text = text[:max_length] + "..."

            processed.append({
                'text': text,
                'score': doc['score'],
                'original_length': len(doc['text']),
                'processed': True
            })

        except Exception as e:
            logger.error(f"處理文檔 {i} 時出錯: {e}")
            continue

    logger.info(f"處理了 {len(documents)} 個文檔，保留 {len(processed)} 個")
    return processed
"""

    syntax = Syntax(good_code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_testing_practices():
    """測試實踐"""
    console.print("[cyan]3. 測試實踐[/cyan]\n")

    test_code = """# tests/test_nodes.py
import pytest
from flows.main_flow.nodes.preprocess import process_documents


class TestProcessDocuments:
    \"\"\"測試文檔處理函數\"\"\"

    def test_basic_processing(self):
        \"\"\"測試基本處理功能\"\"\"
        documents = [
            {'text': 'Hello World', 'score': 0.9},
            {'text': 'Test Document', 'score': 0.8}
        ]

        result = process_documents(documents)

        assert len(result) == 2
        assert all('processed' in doc for doc in result)

    def test_score_filtering(self):
        \"\"\"測試分數過濾\"\"\"
        documents = [
            {'text': 'High Score', 'score': 0.9},
            {'text': 'Low Score', 'score': 0.3}
        ]

        result = process_documents(documents, min_score=0.5)

        assert len(result) == 1
        assert result[0]['text'] == 'High Score'

    def test_length_truncation(self):
        \"\"\"測試長度截斷\"\"\"
        long_text = 'A' * 1000
        documents = [{'text': long_text, 'score': 0.9}]

        result = process_documents(documents, max_length=100)

        assert len(result[0]['text']) <= 103  # 100 + "..."

    def test_empty_input(self):
        \"\"\"測試空輸入\"\"\"
        result = process_documents([])
        assert result == []

    def test_invalid_score(self):
        \"\"\"測試無效分數\"\"\"
        documents = [{'text': 'Test', 'score': 0.9}]

        with pytest.raises(ValueError):
            process_documents(documents, min_score=1.5)

    def test_missing_fields(self):
        \"\"\"測試缺少字段\"\"\"
        documents = [
            {'text': 'Complete', 'score': 0.9},
            {'text': 'Missing Score'},  # 缺少 score
            {'score': 0.8}  # 缺少 text
        ]

        result = process_documents(documents)
        assert len(result) == 1


# tests/test_flows.py
import pytest
from promptflow.client import PFClient


class TestMainFlow:
    \"\"\"測試主 Flow\"\"\"

    @pytest.fixture
    def pf_client(self):
        return PFClient()

    def test_flow_execution(self, pf_client):
        \"\"\"測試 Flow 執行\"\"\"
        flow_path = "./flows/main_flow"

        # 測試單個輸入
        result = pf_client.test(
            flow=flow_path,
            inputs={"question": "測試問題"}
        )

        assert result is not None
        assert 'answer' in result

    def test_flow_with_batch(self, pf_client):
        \"\"\"測試批量運行\"\"\"
        flow_path = "./flows/main_flow"
        data_path = "./data/test/test_data.jsonl"

        run = pf_client.run(
            flow=flow_path,
            data=data_path
        )

        # 等待完成
        pf_client.stream(run)

        # 檢查結果
        metrics = pf_client.get_metrics(run.name)
        assert metrics is not None
"""

    syntax = Syntax(test_code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_performance_optimization():
    """性能優化技巧"""
    console.print("[cyan]4. 性能優化技巧[/cyan]\n")

    optimization_tips = [
        ("緩存 LLM 調用", "避免重複調用相同的問題"),
        ("批量處理", "合併多個請求減少網絡開銷"),
        ("並行執行", "利用多核並行處理獨立任務"),
        ("延遲加載", "只在需要時加載大型資源"),
        ("連接池", "重用數據庫和 API 連接"),
        ("異步處理", "使用異步 I/O 提高吞吐量"),
    ]

    table = Table(title="性能優化技巧")
    table.add_column("技巧", style="cyan")
    table.add_column("說明", style="yellow")

    for tip, desc in optimization_tips:
        table.add_row(tip, desc)

    console.print(table)
    console.print()

    console.print("[yellow]緩存示例:[/yellow]\n")

    cache_code = """from promptflow import tool
from functools import lru_cache
import hashlib
import json


class LLMCache:
    \"\"\"簡單的 LLM 調用緩存\"\"\"

    def __init__(self):
        self._cache = {}

    def get_cache_key(self, prompt: str, **kwargs) -> str:
        \"\"\"生成緩存鍵\"\"\"
        cache_data = {"prompt": prompt, **kwargs}
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()

    def get(self, key: str):
        return self._cache.get(key)

    def set(self, key: str, value: any):
        self._cache[key] = value


# 全局緩存實例
_llm_cache = LLMCache()


@tool
def cached_llm_call(prompt: str, temperature: float = 0.7) -> str:
    \"\"\"帶緩存的 LLM 調用\"\"\"

    # 生成緩存鍵
    cache_key = _llm_cache.get_cache_key(prompt, temperature=temperature)

    # 檢查緩存
    cached_result = _llm_cache.get(cache_key)
    if cached_result is not None:
        logger.info(f"緩存命中: {cache_key}")
        return cached_result

    # 調用 LLM
    result = call_llm(prompt, temperature)

    # 保存到緩存
    _llm_cache.set(cache_key, result)

    return result
"""

    syntax = Syntax(cache_code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_error_handling():
    """錯誤處理"""
    console.print("[cyan]5. 錯誤處理和重試[/cyan]\n")

    error_handling_code = """from promptflow import tool
import time
import logging
from typing import Optional, Callable

logger = logging.getLogger(__name__)


def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0
):
    \"\"\"指數退避重試裝飾器\"\"\"

    def wrapper(*args, **kwargs):
        delay = initial_delay

        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)

            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"重試 {max_retries} 次後仍失敗: {e}")
                    raise

                logger.warning(
                    f"嘗試 {attempt + 1}/{max_retries} 失敗: {e}，"
                    f"{delay}秒後重試"
                )
                time.sleep(delay)
                delay *= backoff_factor

    return wrapper


@tool
def robust_api_call(endpoint: str, data: dict) -> Optional[dict]:
    \"\"\"健壯的 API 調用\"\"\"

    @retry_with_backoff(max_retries=3)
    def _call_api():
        try:
            response = requests.post(endpoint, json=data, timeout=30)
            response.raise_for_status()
            return response.json()

        except requests.Timeout:
            logger.error("API 調用超時")
            raise

        except requests.HTTPError as e:
            if e.response.status_code == 429:
                logger.warning("速率限制，需要重試")
                raise
            elif e.response.status_code >= 500:
                logger.warning("服務器錯誤，需要重試")
                raise
            else:
                logger.error(f"HTTP 錯誤: {e}")
                return None

        except Exception as e:
            logger.error(f"未知錯誤: {e}")
            raise

    try:
        return _call_api()
    except Exception as e:
        # 最終失敗，返回錯誤響應
        return {
            "error": True,
            "message": str(e),
            "endpoint": endpoint
        }
"""

    syntax = Syntax(error_handling_code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_monitoring_logging():
    """監控和日誌"""
    console.print("[cyan]6. 監控和日誌[/cyan]\n")

    logging_code = """import logging
import json
from datetime import datetime
from typing import Any


class StructuredLogger:
    \"\"\"結構化日誌記錄器\"\"\"

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log_event(
        self,
        event_type: str,
        level: str = "INFO",
        **kwargs
    ):
        \"\"\"記錄結構化事件\"\"\"

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "level": level,
            **kwargs
        }

        log_message = json.dumps(log_entry, ensure_ascii=False)

        if level == "ERROR":
            self.logger.error(log_message)
        elif level == "WARNING":
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)


# 使用示例
@tool
def monitored_function(input_data: str) -> dict:
    \"\"\"帶監控的函數\"\"\"
    logger = StructuredLogger(__name__)

    # 記錄開始
    logger.log_event(
        "function_start",
        function="monitored_function",
        input_length=len(input_data)
    )

    start_time = datetime.now()

    try:
        # 處理邏輯
        result = process(input_data)

        # 記錄成功
        duration = (datetime.now() - start_time).total_seconds()
        logger.log_event(
            "function_success",
            function="monitored_function",
            duration=duration,
            result_size=len(str(result))
        )

        return result

    except Exception as e:
        # 記錄錯誤
        duration = (datetime.now() - start_time).total_seconds()
        logger.log_event(
            "function_error",
            level="ERROR",
            function="monitored_function",
            duration=duration,
            error=str(e),
            error_type=type(e).__name__
        )
        raise
"""

    syntax = Syntax(logging_code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_ci_cd():
    """CI/CD 配置"""
    console.print("[cyan]7. CI/CD 配置[/cyan]\n")

    github_actions = """# .github/workflows/test-and-deploy.yml
name: Test and Deploy

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: |
          pytest tests/ --cov=flows --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  evaluate:
    needs: test
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install PromptFlow
        run: pip install promptflow promptflow-tools

      - name: Run evaluation
        run: |
          pf run create \\
            --flow ./flows/main_flow \\
            --data ./data/test/test_data.jsonl

  deploy:
    needs: [test, evaluate]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Deploy to Azure
        run: |
          pf flow build --source ./flows/main_flow --output ./build
          # Azure 部署命令
"""

    syntax = Syntax(github_actions, "yaml", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_production_checklist():
    """生產環境檢查清單"""
    console.print("[cyan]8. 生產環境檢查清單[/cyan]\n")

    checklist = """✅ 安全性
  □ 所有密鑰使用 Key Vault 或環境變量
  □ 啟用 HTTPS
  □ 實施 API 身份驗證
  □ 啟用速率限制
  □ 定期安全審計

✅ 可靠性
  □ 實施重試邏輯
  □ 配置健康檢查
  □ 設置超時時間
  □ 錯誤處理覆蓋所有路徑
  □ 實施熔斷器模式

✅ 性能
  □ 進行負載測試
  □ 配置緩存策略
  □ 啟用自動擴展
  □ 優化數據庫查詢
  □ 監控響應時間

✅ 監控
  □ 配置日誌記錄
  □ 設置性能監控
  □ 配置告警規則
  □ 追蹤關鍵指標
  □ 錯誤追蹤系統

✅ 測試
  □ 單元測試覆蓋率 > 80%
  □ 集成測試
  □ 端到端測試
  □ 性能測試
  □ 安全測試

✅ 文檔
  □ API 文檔完整
  □ 部署文檔
  □ 運維手冊
  □ 故障排查指南
  □ 架構文檔

✅ DevOps
  □ CI/CD 流程
  □ 自動化測試
  □ 自動化部署
  □ 回滾策略
  □ 災難恢復計劃"""

    console.print(Panel(checklist, title="生產環境檢查清單", border_style="cyan"))
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]PromptFlow 最佳實踐示例[/bold cyan]\n"
        "[dim]生產級 PromptFlow 應用開發指南[/dim]",
        border_style="cyan"
    ))

    # 1. 項目結構
    show_project_structure()

    # 2. 代碼質量
    show_code_quality()

    # 3. 測試
    show_testing_practices()

    # 4. 性能優化
    show_performance_optimization()

    # 5. 錯誤處理
    show_error_handling()

    # 6. 監控日誌
    show_monitoring_logging()

    # 7. CI/CD
    show_ci_cd()

    # 8. 生產檢查清單
    show_production_checklist()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 最佳實踐示例完成！[/bold green]\n")
    console.print("[cyan]恭喜！您已完成 PromptFlow 所有示例學習！[/cyan]\n")
    console.print("[yellow]建議下一步:[/yellow]")
    console.print("  1. 構建自己的 PromptFlow 應用")
    console.print("  2. 探索 PromptFlow 官方文檔")
    console.print("  3. 參與社區討論和貢獻")


if __name__ == "__main__":
    main()
