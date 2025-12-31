"""
Aider Git 整合功能
==================

本範例展示 Aider 與 Git 的深度整合，包括：
- 自動提交管理
- 智能提交訊息生成
- 分支操作
- 變更歷史追蹤
- 衝突解決

作者：AI Agent Demo
日期：2025-12-31
"""

import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re


class GitOperationType(Enum):
    """Git 操作類型"""
    COMMIT = "commit"
    BRANCH = "branch"
    MERGE = "merge"
    REBASE = "rebase"
    RESET = "reset"
    STASH = "stash"


@dataclass
class GitCommit:
    """
    Git 提交記錄

    表示一個 Git 提交，包含哈希值、訊息、作者等資訊。
    """
    hash: str
    message: str
    author: str
    date: datetime
    files_changed: List[str]

    def __str__(self) -> str:
        """返回提交的簡短描述"""
        return f"{self.hash[:7]} - {self.message} ({self.author})"


class AiderGitIntegration:
    """
    Aider Git 整合類

    提供與 Git 整合的各種功能，模擬 Aider 如何自動管理
    版本控制操作。
    """

    def __init__(self, repo_path: Path):
        """
        初始化 Git 整合

        Args:
            repo_path: Git 儲存庫路徑
        """
        self.repo_path = repo_path
        self.auto_commit = False
        self.commit_prefix = "aider:"

    def is_git_repo(self) -> bool:
        """
        檢查目錄是否為 Git 儲存庫

        Returns:
            是否為 Git 儲存庫
        """
        git_dir = self.repo_path / ".git"
        return git_dir.exists() and git_dir.is_dir()

    def init_repo(self) -> bool:
        """
        初始化 Git 儲存庫

        如果目錄不是 Git 儲存庫，則初始化一個新的。

        Returns:
            是否成功初始化
        """
        if self.is_git_repo():
            print("已經是 Git 儲存庫")
            return True

        try:
            result = subprocess.run(
                ["git", "init"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✓ Git 儲存庫初始化成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ 初始化失敗: {e.stderr}")
            return False

    def get_status(self) -> Dict[str, List[str]]:
        """
        獲取 Git 狀態

        Returns:
            包含修改、新增、刪除文件的字典
        """
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            status = {
                "modified": [],
                "added": [],
                "deleted": [],
                "untracked": []
            }

            for line in result.stdout.splitlines():
                if not line.strip():
                    continue

                code = line[:2]
                filename = line[3:]

                if code == " M" or code == "M ":
                    status["modified"].append(filename)
                elif code == "A " or code == "AM":
                    status["added"].append(filename)
                elif code == " D" or code == "D ":
                    status["deleted"].append(filename)
                elif code == "??":
                    status["untracked"].append(filename)

            return status

        except subprocess.CalledProcessError as e:
            print(f"獲取狀態失敗: {e.stderr}")
            return {"modified": [], "added": [], "deleted": [], "untracked": []}

    def print_status(self) -> None:
        """
        打印當前 Git 狀態

        以友好的格式顯示文件狀態。
        """
        print("\n" + "=" * 60)
        print("Git 狀態")
        print("=" * 60)

        status = self.get_status()

        if status["modified"]:
            print("\n修改的文件:")
            for file in status["modified"]:
                print(f"  M {file}")

        if status["added"]:
            print("\n新增的文件:")
            for file in status["added"]:
                print(f"  A {file}")

        if status["deleted"]:
            print("\n刪除的文件:")
            for file in status["deleted"]:
                print(f"  D {file}")

        if status["untracked"]:
            print("\n未追蹤的文件:")
            for file in status["untracked"]:
                print(f"  ? {file}")

        if not any(status.values()):
            print("\n工作區乾淨，沒有變更")

    def stage_files(self, files: Optional[List[str]] = None) -> bool:
        """
        將文件加入暫存區

        Args:
            files: 要加入的文件列表，None 表示全部

        Returns:
            是否成功
        """
        try:
            if files is None:
                # 加入所有變更
                subprocess.run(
                    ["git", "add", "-A"],
                    cwd=self.repo_path,
                    check=True
                )
                print("✓ 已加入所有變更到暫存區")
            else:
                # 加入指定文件
                subprocess.run(
                    ["git", "add"] + files,
                    cwd=self.repo_path,
                    check=True
                )
                print(f"✓ 已加入 {len(files)} 個文件到暫存區")

            return True

        except subprocess.CalledProcessError as e:
            print(f"✗ 加入暫存區失敗: {e}")
            return False

    def generate_commit_message(
        self,
        files: Optional[List[str]] = None,
        context: str = ""
    ) -> str:
        """
        自動生成提交訊息

        基於變更的文件和上下文生成有意義的提交訊息。
        這是 Aider 的核心功能之一。

        Args:
            files: 變更的文件列表
            context: 額外的上下文資訊

        Returns:
            生成的提交訊息
        """
        print("\n生成提交訊息...")

        if files is None:
            status = self.get_status()
            files = (
                status["modified"] +
                status["added"] +
                status["deleted"]
            )

        if not files:
            return "No changes to commit"

        # 分析文件類型和變更模式
        file_types = self._analyze_file_types(files)
        change_pattern = self._detect_change_pattern(files)

        # 生成訊息
        message_parts = []

        # 添加前綴
        if self.commit_prefix:
            message_parts.append(self.commit_prefix)

        # 添加變更類型
        message_parts.append(change_pattern)

        # 添加受影響的組件
        if file_types:
            components = ", ".join(file_types[:3])  # 最多列出 3 個
            message_parts.append(f"({components})")

        # 添加上下文
        if context:
            message_parts.append(f"- {context}")

        message = " ".join(message_parts)

        print(f"生成的訊息: {message}")
        return message

    def _analyze_file_types(self, files: List[str]) -> List[str]:
        """
        分析文件類型

        Args:
            files: 文件列表

        Returns:
            文件類型或組件名稱列表
        """
        types = set()

        for file in files:
            path = Path(file)

            # 根據目錄結構判斷組件
            if "test" in path.parts:
                types.add("tests")
            elif "src" in path.parts:
                types.add("core")
            elif "docs" in path.parts:
                types.add("docs")
            elif path.suffix == ".py":
                types.add("python")
            elif path.suffix in [".js", ".ts"]:
                types.add("javascript")
            elif path.suffix in [".md", ".rst"]:
                types.add("docs")

        return list(types)

    def _detect_change_pattern(self, files: List[str]) -> str:
        """
        檢測變更模式

        Args:
            files: 變更的文件列表

        Returns:
            變更類型描述
        """
        # 簡化的模式檢測
        if len(files) == 1:
            if files[0].startswith("test_"):
                return "Add tests"
            elif files[0] == "README.md":
                return "Update documentation"
            else:
                return "Update"
        elif len(files) > 5:
            return "Refactor"
        else:
            return "Update"

    def commit(
        self,
        message: Optional[str] = None,
        auto_message: bool = True
    ) -> bool:
        """
        創建提交

        Args:
            message: 提交訊息，如果為 None 則自動生成
            auto_message: 是否自動生成訊息

        Returns:
            是否成功
        """
        # 檢查是否有變更
        status = self.get_status()
        if not any([status["modified"], status["added"], status["deleted"]]):
            print("沒有變更需要提交")
            return False

        # 加入暫存區
        if not self.stage_files():
            return False

        # 生成或使用提供的訊息
        if message is None and auto_message:
            message = self.generate_commit_message()
        elif message is None:
            message = "Update files"

        try:
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            print(f"✓ 提交成功: {message}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"✗ 提交失敗: {e.stderr}")
            return False

    def get_recent_commits(self, count: int = 10) -> List[GitCommit]:
        """
        獲取最近的提交

        Args:
            count: 要獲取的提交數量

        Returns:
            提交列表
        """
        try:
            result = subprocess.run(
                [
                    "git", "log",
                    f"-{count}",
                    "--pretty=format:%H|%s|%an|%ad",
                    "--date=iso"
                ],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            commits = []

            for line in result.stdout.splitlines():
                if not line.strip():
                    continue

                parts = line.split("|")
                if len(parts) >= 4:
                    commit = GitCommit(
                        hash=parts[0],
                        message=parts[1],
                        author=parts[2],
                        date=datetime.fromisoformat(parts[3].strip()),
                        files_changed=self._get_commit_files(parts[0])
                    )
                    commits.append(commit)

            return commits

        except subprocess.CalledProcessError:
            return []

    def _get_commit_files(self, commit_hash: str) -> List[str]:
        """
        獲取提交中變更的文件

        Args:
            commit_hash: 提交哈希值

        Returns:
            文件列表
        """
        try:
            result = subprocess.run(
                ["git", "show", "--name-only", "--pretty=format:", commit_hash],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            files = [f for f in result.stdout.splitlines() if f.strip()]
            return files

        except subprocess.CalledProcessError:
            return []

    def show_commit_history(self, count: int = 10) -> None:
        """
        顯示提交歷史

        Args:
            count: 顯示的提交數量
        """
        print("\n" + "=" * 60)
        print(f"最近 {count} 次提交")
        print("=" * 60)

        commits = self.get_recent_commits(count)

        for i, commit in enumerate(commits, 1):
            print(f"\n{i}. {commit}")
            print(f"   日期: {commit.date.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   文件: {len(commit.files_changed)} 個")

            if commit.files_changed:
                for file in commit.files_changed[:3]:
                    print(f"     - {file}")
                if len(commit.files_changed) > 3:
                    print(f"     ... 還有 {len(commit.files_changed) - 3} 個")

    def create_branch(self, branch_name: str) -> bool:
        """
        創建新分支

        Args:
            branch_name: 分支名稱

        Returns:
            是否成功
        """
        try:
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=self.repo_path,
                capture_output=True,
                check=True
            )

            print(f"✓ 創建並切換到分支: {branch_name}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"✗ 創建分支失敗: {e.stderr}")
            return False

    def list_branches(self) -> List[str]:
        """
        列出所有分支

        Returns:
            分支名稱列表
        """
        try:
            result = subprocess.run(
                ["git", "branch", "-a"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            branches = []
            for line in result.stdout.splitlines():
                branch = line.strip().lstrip("* ")
                if branch:
                    branches.append(branch)

            return branches

        except subprocess.CalledProcessError:
            return []

    def switch_branch(self, branch_name: str) -> bool:
        """
        切換分支

        Args:
            branch_name: 要切換到的分支名稱

        Returns:
            是否成功
        """
        try:
            subprocess.run(
                ["git", "checkout", branch_name],
                cwd=self.repo_path,
                capture_output=True,
                check=True
            )

            print(f"✓ 已切換到分支: {branch_name}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"✗ 切換分支失敗: {e.stderr}")
            return False

    def get_diff(
        self,
        staged: bool = False,
        file_path: Optional[str] = None
    ) -> str:
        """
        獲取變更差異

        Args:
            staged: 是否只顯示暫存區的變更
            file_path: 特定文件路徑

        Returns:
            diff 內容
        """
        cmd = ["git", "diff"]

        if staged:
            cmd.append("--staged")

        if file_path:
            cmd.append(file_path)

        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            return result.stdout

        except subprocess.CalledProcessError as e:
            return f"獲取 diff 失敗: {e.stderr}"

    def show_diff(
        self,
        staged: bool = False,
        file_path: Optional[str] = None
    ) -> None:
        """
        顯示變更差異

        Args:
            staged: 是否只顯示暫存區的變更
            file_path: 特定文件路徑
        """
        print("\n" + "=" * 60)
        print("變更差異")
        print("=" * 60)

        diff = self.get_diff(staged, file_path)

        if diff:
            print(diff)
        else:
            print("沒有變更")

    def undo_last_commit(self, soft: bool = True) -> bool:
        """
        撤銷最後一次提交

        Args:
            soft: 是否保留變更（soft reset）

        Returns:
            是否成功
        """
        reset_type = "--soft" if soft else "--hard"

        try:
            subprocess.run(
                ["git", "reset", reset_type, "HEAD~1"],
                cwd=self.repo_path,
                check=True
            )

            action = "保留" if soft else "丟棄"
            print(f"✓ 已撤銷最後一次提交（{action}變更）")
            return True

        except subprocess.CalledProcessError as e:
            print(f"✗ 撤銷失敗: {e}")
            return False


class AiderGitWorkflow:
    """
    Aider Git 工作流程

    展示如何在實際開發中使用 Aider 的 Git 整合功能。
    """

    def __init__(self, repo_path: Path):
        """初始化工作流程"""
        self.git = AiderGitIntegration(repo_path)

    def feature_development_workflow(self) -> None:
        """
        功能開發工作流程

        展示如何使用 Aider 開發新功能的完整流程。
        """
        print("\n" + "=" * 60)
        print("功能開發工作流程")
        print("=" * 60)

        print("""
步驟 1: 創建功能分支
-------------------

$ aider
> /git checkout -b feature/user-authentication

步驟 2: 開始開發
---------------

> 請實現用戶認證功能，包括登入和註冊

# Aider 會修改相關文件

步驟 3: 自動提交
---------------

如果啟用了 auto-commits:

> /git auto-commits true

Aider 會在每次變更後自動創建提交，訊息由 AI 生成。

步驟 4: 手動提交
---------------

或者手動控制提交:

> /commit 實現用戶登入功能

步驟 5: 繼續開發
---------------

> 現在請添加密碼重設功能

> /commit 添加密碼重設功能

步驟 6: 查看歷史
---------------

> /git log

顯示提交歷史

步驟 7: 合併到主分支
-------------------

$ git checkout main
$ git merge feature/user-authentication
        """)

    def bugfix_workflow(self) -> None:
        """
        Bug 修復工作流程
        """
        print("\n" + "=" * 60)
        print("Bug 修復工作流程")
        print("=" * 60)

        print("""
步驟 1: 創建修復分支
-------------------

$ git checkout -b bugfix/login-error

步驟 2: 使用 Aider 修復
----------------------

$ aider src/auth.py tests/test_auth.py

> 用戶報告登入時出現 500 錯誤。
> 請檢查 auth.py 並修復問題，同時添加測試確保不會再次發生。

步驟 3: 查看變更
---------------

> /diff

檢查 Aider 的修改

步驟 4: 測試修復
---------------

> /test

運行測試確保修復有效

步驟 5: 提交
-----------

> /commit 修復: 處理登入時的空值錯誤

步驟 6: 如果需要調整
------------------

> /undo  # 撤銷變更
> 請用另一種方式修復...

步驟 7: 推送和合併
-----------------

$ git push origin bugfix/login-error
# 創建 Pull Request
        """)

    def refactoring_workflow(self) -> None:
        """
        重構工作流程
        """
        print("\n" + "=" * 60)
        print("重構工作流程")
        print("=" * 60)

        print("""
步驟 1: 確保有完整的測試覆蓋
---------------------------

$ python -m pytest --cov

步驟 2: 創建重構分支
-------------------

$ git checkout -b refactor/improve-structure

步驟 3: 使用 Aider 重構
----------------------

$ aider src/**/*.py

> 請重構這個專案以遵循 SOLID 原則:
> 1. 將大型類拆分為更小的類
> 2. 使用依賴注入
> 3. 改善命名

步驟 4: 逐步提交
---------------

Aider 會建議分步驟重構，每個步驟一個提交:

> /commit 重構: 拆分 UserService 類
> 重構: 引入依賴注入容器
> 重構: 改善變數和方法命名

步驟 5: 確保測試通過
-------------------

> /test

每次重構後確保測試仍然通過

步驟 6: 審查變更
---------------

> /git log --oneline

查看重構的提交歷史

步驟 7: 合併
-----------

$ git checkout main
$ git merge refactor/improve-structure
        """)


def demonstrate_git_features():
    """
    演示 Git 功能

    創建一個示例項目並展示各種 Git 操作。
    """
    print("\n" + "=" * 60)
    print("Aider Git 整合演示")
    print("=" * 60)

    # 創建示例目錄
    demo_path = Path("./aider_git_demo")
    demo_path.mkdir(exist_ok=True)

    # 初始化 Git
    git = AiderGitIntegration(demo_path)

    if not git.is_git_repo():
        git.init_repo()

    # 創建示例文件
    (demo_path / "example.py").write_text('''
def hello():
    print("Hello, World!")
''')

    # 演示狀態
    git.print_status()

    # 演示提交
    print("\n### 演示自動提交")
    commit_msg = git.generate_commit_message(["example.py"], "初始版本")
    git.commit(commit_msg)

    # 修改文件
    (demo_path / "example.py").write_text('''
def hello(name="World"):
    """問候函數"""
    print(f"Hello, {name}!")

def goodbye():
    """告別函數"""
    print("Goodbye!")
''')

    # 顯示差異
    git.show_diff()

    # 再次提交
    git.commit("添加 goodbye 函數和文檔")

    # 顯示歷史
    git.show_commit_history(5)

    # 演示分支
    print("\n### 演示分支操作")
    git.create_branch("feature/new-feature")

    branches = git.list_branches()
    print(f"現有分支: {', '.join(branches)}")


def main():
    """
    主函數

    運行 Git 整合演示。
    """
    # 演示基本功能
    demonstrate_git_features()

    # 展示工作流程
    demo_path = Path("./aider_git_demo")
    workflow = AiderGitWorkflow(demo_path)

    workflow.feature_development_workflow()
    workflow.bugfix_workflow()
    workflow.refactoring_workflow()


if __name__ == "__main__":
    main()
