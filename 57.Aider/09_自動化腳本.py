"""
Aider 自動化腳本
================

本範例展示如何使用 Aider 進行自動化開發任務，包括：
- 批處理模式
- 腳本化工作流程
- CI/CD 集成
- 自動化測試生成
- 代碼審查自動化

作者：AI Agent Demo
日期：2025-12-31
"""

import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json
import sys


class AutomationTask(Enum):
    """自動化任務類型"""
    CODE_GENERATION = "code_generation"
    TEST_GENERATION = "test_generation"
    REFACTORING = "refactoring"
    DOCUMENTATION = "documentation"
    CODE_REVIEW = "code_review"
    BUG_FIX = "bug_fix"


@dataclass
class TaskConfig:
    """
    任務配置

    定義自動化任務的參數。
    """
    task_type: AutomationTask
    files: List[Path]
    prompt: str
    model: str = "gpt-4-turbo"
    auto_commit: bool = False
    commit_message: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.task_type.value}: {self.prompt[:50]}..."


class AiderAutomation:
    """
    Aider 自動化類

    提供各種自動化開發任務的功能。
    """

    def __init__(self, project_root: Path):
        """
        初始化自動化工具

        Args:
            project_root: 專案根目錄
        """
        self.project_root = project_root
        self.tasks: List[TaskConfig] = []
        self.results: List[Dict] = []

    def run_batch_command(
        self,
        files: List[str],
        message: str,
        model: str = "gpt-4-turbo",
        auto_commit: bool = False
    ) -> bool:
        """
        執行批處理命令

        Args:
            files: 文件列表
            message: 要執行的命令/請求
            model: 使用的模型
            auto_commit: 是否自動提交

        Returns:
            是否成功
        """
        cmd = [
            "aider",
            "--model", model,
            "--message", message,
            "--yes"  # 自動確認
        ]

        if auto_commit:
            cmd.append("--auto-commits")

        cmd.extend(files)

        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )

            print(f"✓ 批處理命令執行成功")
            return True

        except subprocess.CalledProcessError as e:
            print(f"✗ 批處理命令執行失敗: {e.stderr}")
            return False

    @staticmethod
    def demonstrate_batch_mode():
        """
        演示批處理模式

        展示如何在非交互模式下使用 Aider。
        """
        print("\n" + "=" * 80)
        print("批處理模式")
        print("=" * 80)

        print("""
## 1. 基本批處理命令

### 單一任務執行

```bash
# 為文件添加類型註解
aider --message "為所有函數添加類型註解" --yes src/utils.py

# 生成測試
aider --message "為這個模組生成單元測試" --yes src/models.py tests/test_models.py

# 重構代碼
aider --message "重構這個類以遵循 SOLID 原則" --yes src/service.py
```

### 多文件操作

```bash
# 批量重命名
aider --message "將 UserModel 重命名為 User" --yes src/**/*.py

# 批量添加文檔
aider --message "為所有公共方法添加 docstring" --yes src/**/*.py
```

## 2. 自動提交模式

```bash
# 執行任務並自動提交
aider \\
  --message "實現用戶認證功能" \\
  --auto-commits \\
  --yes \\
  src/auth.py src/models.py

# 結果：
# ✓ 代碼已修改
# ✓ 自動提交: "aider: 實現用戶認證功能"
```

## 3. 管道模式

### 從文件讀取任務

```bash
# tasks.txt
# ========
# 為 User 類添加 email 驗證
# 實現密碼加密功能
# 添加單元測試

# 執行
cat tasks.txt | while read task; do
  aider --message "$task" --yes src/auth.py
done
```

### 從 JSON 讀取配置

```json
// automation_tasks.json
{
  "tasks": [
    {
      "files": ["src/models.py"],
      "message": "添加數據驗證",
      "model": "gpt-4-turbo"
    },
    {
      "files": ["tests/test_models.py"],
      "message": "生成測試",
      "model": "gpt-3.5-turbo"
    }
  ]
}
```

```bash
# 執行腳本
python run_automation.py automation_tasks.json
```

## 4. CI/CD 集成

### GitHub Actions

```yaml
# .github/workflows/aider-automation.yml
name: Aider Automation

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  aider-review:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Aider
        run: pip install aider-chat

      - name: Generate Tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          aider \\
            --message "為新增的代碼生成測試" \\
            --yes \\
            --auto-commits \\
            src/**/*.py

      - name: Run Tests
        run: pytest

      - name: Commit Changes
        run: |
          git config user.name "Aider Bot"
          git config user.email "bot@aider.chat"
          git push
```

### GitLab CI

```yaml
# .gitlab-ci.yml
aider-automation:
  stage: test
  image: python:3.10
  script:
    - pip install aider-chat
    - |
      aider \\
        --message "代碼審查和優化" \\
        --yes \\
        src/**/*.py
  only:
    - merge_requests
```

## 5. 定時任務

### Cron 作業

```bash
# 每天凌晨 2 點運行代碼優化
0 2 * * * cd /path/to/project && aider --message "優化代碼性能" --yes src/**/*.py
```

### 週期性重構

```bash
#!/bin/bash
# weekly_refactor.sh

cd /path/to/project

# 運行代碼分析
aider --message "分析代碼並提出重構建議" --yes --read src/**/*.py > refactor_plan.txt

# 執行重構
if [ -s refactor_plan.txt ]; then
  aider --message "根據分析結果執行重構" --yes --auto-commits src/**/*.py
fi
```

## 6. 並行處理

### 多個獨立任務

```bash
#!/bin/bash
# parallel_tasks.sh

# 並行執行多個獨立任務
(
  aider --message "優化 models.py" --yes src/models.py &
  aider --message "優化 views.py" --yes src/views.py &
  aider --message "優化 controllers.py" --yes src/controllers.py &
  wait
)

echo "所有任務完成"
```

## 7. 條件執行

### 基於測試結果

```bash
#!/bin/bash

# 運行測試
pytest

# 如果測試失敗，使用 Aider 修復
if [ $? -ne 0 ]; then
  echo "測試失敗，嘗試自動修復..."

  aider \\
    --message "修復導致測試失敗的問題" \\
    --yes \\
    --auto-commits \\
    src/**/*.py tests/**/*.py
fi
```

### 基於代碼審查

```bash
#!/bin/bash

# 運行 linter
pylint src/ > lint_results.txt

# 如果有問題，使用 Aider 修復
if grep -q "Your code has been rated at 10.00/10" lint_results.txt; then
  echo "代碼質量完美！"
else
  aider \\
    --message "修復 linter 指出的問題" \\
    --yes \\
    src/**/*.py
fi
```

## 8. 輸出處理

### 捕獲和記錄輸出

```bash
# 記錄所有輸出
aider --message "任務描述" --yes src/*.py 2>&1 | tee aider_log.txt

# 只記錄錯誤
aider --message "任務描述" --yes src/*.py 2> aider_errors.log

# JSON 格式輸出
aider --message "任務描述" --yes --json-output results.json src/*.py
```

## 9. 錯誤處理

### 重試機制

```bash
#!/bin/bash

MAX_RETRIES=3
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  aider --message "執行任務" --yes src/*.py

  if [ $? -eq 0 ]; then
    echo "成功"
    break
  else
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "失敗，重試 $RETRY_COUNT/$MAX_RETRIES"
    sleep 5
  fi
done
```

### 回滾機制

```bash
#!/bin/bash

# 保存當前狀態
git stash

# 執行 Aider
aider --message "嘗試性修改" --yes src/*.py

# 運行測試
pytest

# 如果測試失敗，回滾
if [ $? -ne 0 ]; then
  echo "測試失敗，回滾變更"
  git reset --hard HEAD
  git stash pop
fi
```
        """)

    @staticmethod
    def demonstrate_automation_scripts():
        """
        演示自動化腳本範例
        """
        print("\n" + "=" * 80)
        print("自動化腳本範例")
        print("=" * 80)

        print("""
## 1. 自動測試生成器

```python
#!/usr/bin/env python3
# auto_test_generator.py

import subprocess
from pathlib import Path
import sys


def generate_tests_for_module(module_path: Path) -> bool:
    \"\"\"為模組生成測試\"\"\"

    # 確定測試文件路徑
    test_path = Path("tests") / f"test_{module_path.name}"

    # 使用 Aider 生成測試
    cmd = [
        "aider",
        "--message", f"為 {module_path} 生成全面的單元測試",
        "--yes",
        "--auto-commits",
        "--model", "gpt-3.5-turbo",  # 使用便宜的模型
        str(module_path),
        str(test_path)
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"✓ 已為 {module_path} 生成測試")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ 生成測試失敗: {module_path}")
        return False


def main():
    # 查找所有沒有測試的 Python 文件
    src_files = Path("src").rglob("*.py")

    for src_file in src_files:
        test_file = Path("tests") / f"test_{src_file.name}"

        if not test_file.exists():
            print(f"\\n處理: {src_file}")
            generate_tests_for_module(src_file)


if __name__ == "__main__":
    main()
```

## 2. 代碼審查自動化

```python
#!/usr/bin/env python3
# auto_code_review.py

import subprocess
import sys
from pathlib import Path


def review_changed_files() -> None:
    \"\"\"審查 Git 變更的文件\"\"\"

    # 獲取變更的文件
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        capture_output=True,
        text=True
    )

    changed_files = [
        f for f in result.stdout.splitlines()
        if f.endswith(".py")
    ]

    if not changed_files:
        print("沒有 Python 文件變更")
        return

    print(f"審查 {len(changed_files)} 個文件...")

    # 使用 Aider 進行代碼審查
    review_prompt = \"\"\"
    請審查這些代碼變更，檢查：
    1. 代碼品質和風格
    2. 潛在的 bug
    3. 性能問題
    4. 安全隱患
    5. 最佳實踐

    如果發現問題，請修復它們。
    \"\"\"

    cmd = [
        "aider",
        "--message", review_prompt,
        "--yes",
        "--model", "gpt-4-turbo",
    ] + changed_files

    subprocess.run(cmd)


if __name__ == "__main__":
    review_changed_files()
```

## 3. 文檔生成器

```python
#!/usr/bin/env python3
# auto_documentation.py

import subprocess
from pathlib import Path


def generate_documentation(file_path: Path) -> None:
    \"\"\"為文件生成文檔\"\"\"

    doc_prompt = \"\"\"
    請為這個文件生成詳細的文檔：
    1. 為每個類添加 docstring
    2. 為每個公共方法添加 docstring
    3. 包括參數說明、返回值和示例
    4. 使用 Google 風格的 docstring
    \"\"\"

    cmd = [
        "aider",
        "--message", doc_prompt,
        "--yes",
        "--model", "gpt-3.5-turbo",
        str(file_path)
    ]

    subprocess.run(cmd)


def main():
    # 處理所有 Python 文件
    for py_file in Path("src").rglob("*.py"):
        print(f"\\n生成文檔: {py_file}")
        generate_documentation(py_file)


if __name__ == "__main__":
    main()
```

## 4. 依賴更新助手

```python
#!/usr/bin/env python3
# dependency_updater.py

import subprocess
import re


def update_dependencies() -> None:
    \"\"\"更新依賴並修復相容性問題\"\"\"

    # 更新依賴
    print("更新依賴...")
    subprocess.run(["pip", "install", "--upgrade", "-r", "requirements.txt"])

    # 運行測試
    result = subprocess.run(["pytest"], capture_output=True)

    if result.returncode != 0:
        print("測試失敗，使用 Aider 修復相容性問題...")

        fix_prompt = \"\"\"
        依賴更新後測試失敗。請：
        1. 檢查測試輸出
        2. 識別相容性問題
        3. 修復代碼以適配新版本的依賴
        4. 確保所有測試通過
        \"\"\"

        cmd = [
            "aider",
            "--message", fix_prompt,
            "--yes",
            "src/**/*.py",
            "tests/**/*.py"
        ]

        subprocess.run(cmd)


if __name__ == "__main__":
    update_dependencies()
```

## 5. 持續重構

```python
#!/usr/bin/env python3
# continuous_refactor.py

import subprocess
from pathlib import Path


def analyze_code_smells() -> list:
    \"\"\"分析代碼異味\"\"\"

    # 使用 pylint 或其他工具
    result = subprocess.run(
        ["pylint", "src/", "--output-format=json"],
        capture_output=True,
        text=True
    )

    # 解析結果，找出需要重構的文件
    # ... 解析邏輯 ...

    return ["src/large_class.py", "src/complex_method.py"]


def refactor_file(file_path: str) -> None:
    \"\"\"重構文件\"\"\"

    refactor_prompt = \"\"\"
    請重構這個文件：
    1. 拆分過長的方法
    2. 簡化複雜的邏輯
    3. 遵循 SOLID 原則
    4. 改善命名
    5. 移除重複代碼
    \"\"\"

    cmd = [
        "aider",
        "--message", refactor_prompt,
        "--yes",
        "--auto-commits",
        file_path
    ]

    subprocess.run(cmd)


def main():
    files_to_refactor = analyze_code_smells()

    for file_path in files_to_refactor:
        print(f"\\n重構: {file_path}")
        refactor_file(file_path)

        # 運行測試確保沒有破壞功能
        result = subprocess.run(["pytest"])

        if result.returncode != 0:
            print("測試失敗，回滾變更")
            subprocess.run(["git", "reset", "--hard", "HEAD~1"])


if __name__ == "__main__":
    main()
```

## 6. 多語言遷移

```bash
#!/bin/bash
# migrate_to_typescript.sh

# 將 JavaScript 文件遷移到 TypeScript

find src -name "*.js" | while read js_file; do
  ts_file="${js_file%.js}.ts"

  echo "遷移: $js_file -> $ts_file"

  aider \\
    --message "將這個 JavaScript 文件轉換為 TypeScript，添加適當的類型註解" \\
    --yes \\
    "$js_file"

  # 重命名文件
  mv "$js_file" "$ts_file"
done

echo "遷移完成！"
```

## 7. 性能優化

```python
#!/usr/bin/env python3
# performance_optimizer.py

import subprocess
import cProfile
import pstats


def profile_code():
    \"\"\"分析代碼性能\"\"\"
    # 運行性能分析
    # ... 分析邏輯 ...
    pass


def optimize_slow_functions(slow_functions: list):
    \"\"\"優化慢速函數\"\"\"

    for func_info in slow_functions:
        file_path, func_name = func_info

        optimize_prompt = f\"\"\"
        函數 {func_name} 在性能分析中被識別為瓶頸。
        請優化這個函數：
        1. 分析當前實現
        2. 識別性能問題
        3. 實現更高效的算法或數據結構
        4. 保持功能不變
        \"\"\"

        cmd = [
            "aider",
            "--message", optimize_prompt,
            "--yes",
            file_path
        ]

        subprocess.run(cmd)


if __name__ == "__main__":
    slow_functions = profile_code()
    optimize_slow_functions(slow_functions)
```

## 8. 自動化部署準備

```bash
#!/bin/bash
# prepare_deployment.sh

echo "準備部署..."

# 1. 代碼審查
aider --message "最後的代碼審查和優化" --yes --read src/**/*.py

# 2. 更新文檔
aider --message "更新 README 和 CHANGELOG" --yes README.md CHANGELOG.md

# 3. 生成發布說明
aider --message "基於最近的提交生成發布說明" --yes RELEASE_NOTES.md

# 4. 運行完整測試
pytest

# 5. 構建和打包
python setup.py sdist bdist_wheel

echo "部署準備完成！"
```
        """)

    def create_automation_config(self, output_path: Path) -> None:
        """
        創建自動化配置文件

        Args:
            output_path: 輸出路徑
        """
        config = {
            "automation": {
                "enabled": True,
                "tasks": [
                    {
                        "name": "daily_test_generation",
                        "type": "test_generation",
                        "schedule": "0 2 * * *",
                        "files": ["src/**/*.py"],
                        "model": "gpt-3.5-turbo"
                    },
                    {
                        "name": "weekly_refactoring",
                        "type": "refactoring",
                        "schedule": "0 2 * * 0",
                        "files": ["src/**/*.py"],
                        "model": "gpt-4-turbo"
                    },
                    {
                        "name": "documentation_update",
                        "type": "documentation",
                        "schedule": "0 2 * * 5",
                        "files": ["src/**/*.py"],
                        "model": "gpt-3.5-turbo"
                    }
                ],
                "ci_cd": {
                    "enabled": True,
                    "on_pull_request": {
                        "run_tests": True,
                        "code_review": True,
                        "generate_tests": True
                    }
                },
                "notifications": {
                    "email": "dev@example.com",
                    "slack_webhook": ""
                }
            }
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"✓ 自動化配置已保存到: {output_path}")


def main():
    """
    主函數

    運行自動化演示。
    """
    print("=" * 80)
    print("Aider 自動化腳本")
    print("=" * 80)

    automation = AiderAutomation(Path.cwd())

    # 演示批處理模式
    automation.demonstrate_batch_mode()

    # 演示自動化腳本
    automation.demonstrate_automation_scripts()

    # 創建配置文件
    config_path = Path(".aider.automation.json")
    automation.create_automation_config(config_path)

    print("\n" + "=" * 80)
    print("自動化最佳實踐")
    print("=" * 80)

    print("""
1. 從小處開始
   - 先自動化簡單任務
   - 逐步擴展到複雜任務

2. 充分測試
   - 在生產環境前先在測試環境運行
   - 始終有回滾機制

3. 監控和日誌
   - 記錄所有自動化任務的執行
   - 設置錯誤通知

4. 成本控制
   - 使用便宜的模型處理簡單任務
   - 監控 API 使用量

5. 安全考慮
   - 保護 API 金鑰
   - 審查自動生成的代碼
   - 不要自動合併到主分支

6. 人工審查
   - 重要變更需要人工確認
   - 定期審查自動化結果

7. 文檔化
   - 記錄所有自動化流程
   - 維護配置文件

8. 持續改進
   - 收集反饋
   - 優化自動化腳本
    """)


if __name__ == "__main__":
    main()
