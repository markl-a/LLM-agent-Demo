#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Composio GitHub 整合範例
========================

本範例展示如何使用 Composio 整合 GitHub，包括：
1. GitHub 認證和連接
2. 倉庫管理（創建、列表、更新）
3. Issue 管理
4. Pull Request 操作
5. 代碼審查自動化
6. GitHub Actions 整合
7. 協作工作流程

GitHub 是最受歡迎的代碼託管平台，Composio 提供完整的 GitHub API 整合。

作者: Composio 團隊
日期: 2025-01-01
"""

import os
import sys
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 導入 Composio SDK
try:
    from composio import Composio, App, Action
    from composio.client.exceptions import ComposioException
except ImportError as e:
    print("錯誤：請先安裝 Composio SDK")
    print("執行: pip install composio-core")
    sys.exit(1)


class GitHubIntegration:
    """
    GitHub 整合類別

    提供完整的 GitHub 整合功能，包括：
    - 倉庫管理
    - Issue 追蹤
    - Pull Request 工作流程
    - 代碼審查
    - 自動化操作
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 GitHub 整合

        Args:
            api_key: Composio API 金鑰
        """
        print("=" * 70)
        print("初始化 GitHub 整合")
        print("=" * 70)

        self.api_key = api_key or os.getenv("COMPOSIO_API_KEY")

        try:
            # 初始化 Composio 客戶端
            self.client = Composio(api_key=self.api_key)
            self.entity = self.client.get_entity(id="default")
            print("✓ Composio 客戶端初始化成功")

            # 檢查 GitHub 連接
            self._check_github_connection()

        except Exception as e:
            print(f"✗ 初始化失敗: {e}")
            raise

    def _check_github_connection(self) -> bool:
        """
        檢查 GitHub 連接狀態

        Returns:
            是否已連接
        """
        try:
            connections = self.entity.get_connections(app_name="github")

            if connections:
                print("✓ GitHub 已連接")
                return True
            else:
                print("⚠ GitHub 尚未連接")
                print("\n要連接 GitHub，請執行:")
                print("  connection = entity.initiate_connection('github')")
                print("  然後訪問返回的 URL 進行授權")
                return False

        except Exception as e:
            print(f"✗ 檢查連接失敗: {e}")
            return False

    def connect_github(self, redirect_url: str = "http://localhost:8000/callback") -> Optional[str]:
        """
        連接 GitHub 帳號

        Args:
            redirect_url: OAuth 回調 URL

        Returns:
            授權 URL
        """
        print("\n" + "=" * 70)
        print("連接 GitHub 帳號")
        print("=" * 70)

        try:
            # 啟動 OAuth 流程
            connection_request = self.entity.initiate_connection(
                app_name="github",
                redirect_url=redirect_url
            )

            if hasattr(connection_request, 'redirectUrl'):
                auth_url = connection_request.redirectUrl
                print(f"\n請訪問以下 URL 進行授權:")
                print(f"{auth_url}")
                return auth_url
            else:
                print("✓ GitHub 連接已建立")
                return None

        except Exception as e:
            print(f"✗ 連接 GitHub 失敗: {e}")
            return None

    def list_repositories(self, org: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        列出 GitHub 倉庫

        Args:
            org: 組織名稱（可選）
            limit: 限制返回的倉庫數量

        Returns:
            倉庫列表
        """
        print("\n" + "=" * 70)
        print("列出 GitHub 倉庫")
        print("=" * 70)

        try:
            # 構建參數
            params = {"per_page": limit}
            if org:
                params["org"] = org
                action = "GITHUB_LIST_ORG_REPOS"
            else:
                action = "GITHUB_LIST_USER_REPOS"

            # 執行操作
            result = self.entity.execute(
                action=action,
                params=params
            )

            repositories = result.get('data', [])
            print(f"\n找到 {len(repositories)} 個倉庫:")
            print("-" * 70)

            for i, repo in enumerate(repositories, 1):
                name = repo.get('name', 'Unknown')
                full_name = repo.get('full_name', 'Unknown')
                description = repo.get('description', '無描述')
                stars = repo.get('stargazers_count', 0)
                language = repo.get('language', 'Unknown')

                print(f"{i}. {full_name}")
                print(f"   描述: {description}")
                print(f"   語言: {language} | Stars: {stars}")
                print()

            return repositories

        except Exception as e:
            print(f"✗ 列出倉庫失敗: {e}")
            return []

    def create_repository(self, name: str, description: str = "",
                         private: bool = False, auto_init: bool = True) -> Dict[str, Any]:
        """
        創建新的 GitHub 倉庫

        Args:
            name: 倉庫名稱
            description: 倉庫描述
            private: 是否為私有倉庫
            auto_init: 是否自動初始化（創建 README）

        Returns:
            創建的倉庫資訊
        """
        print("\n" + "=" * 70)
        print(f"創建 GitHub 倉庫: {name}")
        print("=" * 70)

        try:
            # 執行創建操作
            result = self.entity.execute(
                action="GITHUB_CREATE_REPO",
                params={
                    "name": name,
                    "description": description,
                    "private": private,
                    "auto_init": auto_init
                }
            )

            repo = result.get('data', {})
            print(f"\n✓ 倉庫創建成功!")
            print(f"  名稱: {repo.get('full_name')}")
            print(f"  URL: {repo.get('html_url')}")
            print(f"  克隆: {repo.get('clone_url')}")

            return repo

        except Exception as e:
            print(f"✗ 創建倉庫失敗: {e}")
            return {}

    def list_issues(self, owner: str, repo: str, state: str = "open",
                    limit: int = 10) -> List[Dict[str, Any]]:
        """
        列出倉庫的 Issues

        Args:
            owner: 倉庫擁有者
            repo: 倉庫名稱
            state: Issue 狀態 (open/closed/all)
            limit: 限制返回的數量

        Returns:
            Issue 列表
        """
        print("\n" + "=" * 70)
        print(f"列出 {owner}/{repo} 的 Issues")
        print("=" * 70)

        try:
            # 執行操作
            result = self.entity.execute(
                action="GITHUB_LIST_ISSUES",
                params={
                    "owner": owner,
                    "repo": repo,
                    "state": state,
                    "per_page": limit
                }
            )

            issues = result.get('data', [])
            print(f"\n找到 {len(issues)} 個 {state} Issues:")
            print("-" * 70)

            for i, issue in enumerate(issues, 1):
                number = issue.get('number')
                title = issue.get('title')
                user = issue.get('user', {}).get('login', 'Unknown')
                labels = [l.get('name') for l in issue.get('labels', [])]
                created = issue.get('created_at', '')

                print(f"{i}. #{number}: {title}")
                print(f"   作者: {user}")
                print(f"   標籤: {', '.join(labels) if labels else '無'}")
                print(f"   創建時間: {created}")
                print()

            return issues

        except Exception as e:
            print(f"✗ 列出 Issues 失敗: {e}")
            return []

    def create_issue(self, owner: str, repo: str, title: str,
                    body: str = "", labels: List[str] = None) -> Dict[str, Any]:
        """
        創建新的 Issue

        Args:
            owner: 倉庫擁有者
            repo: 倉庫名稱
            title: Issue 標題
            body: Issue 內容
            labels: 標籤列表

        Returns:
            創建的 Issue 資訊
        """
        print("\n" + "=" * 70)
        print(f"創建 Issue: {title}")
        print("=" * 70)

        try:
            # 構建參數
            params = {
                "owner": owner,
                "repo": repo,
                "title": title,
                "body": body
            }

            if labels:
                params["labels"] = labels

            # 執行操作
            result = self.entity.execute(
                action="GITHUB_CREATE_ISSUE",
                params=params
            )

            issue = result.get('data', {})
            print(f"\n✓ Issue 創建成功!")
            print(f"  編號: #{issue.get('number')}")
            print(f"  標題: {issue.get('title')}")
            print(f"  URL: {issue.get('html_url')}")

            return issue

        except Exception as e:
            print(f"✗ 創建 Issue 失敗: {e}")
            return {}

    def update_issue(self, owner: str, repo: str, issue_number: int,
                    title: Optional[str] = None, body: Optional[str] = None,
                    state: Optional[str] = None, labels: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        更新 Issue

        Args:
            owner: 倉庫擁有者
            repo: 倉庫名稱
            issue_number: Issue 編號
            title: 新標題
            body: 新內容
            state: 新狀態 (open/closed)
            labels: 新標籤列表

        Returns:
            更新後的 Issue 資訊
        """
        print("\n" + "=" * 70)
        print(f"更新 Issue #{issue_number}")
        print("=" * 70)

        try:
            # 構建參數
            params = {
                "owner": owner,
                "repo": repo,
                "issue_number": issue_number
            }

            if title:
                params["title"] = title
            if body:
                params["body"] = body
            if state:
                params["state"] = state
            if labels:
                params["labels"] = labels

            # 執行操作
            result = self.entity.execute(
                action="GITHUB_UPDATE_ISSUE",
                params=params
            )

            issue = result.get('data', {})
            print(f"\n✓ Issue 更新成功!")
            print(f"  標題: {issue.get('title')}")
            print(f"  狀態: {issue.get('state')}")

            return issue

        except Exception as e:
            print(f"✗ 更新 Issue 失敗: {e}")
            return {}

    def create_pull_request(self, owner: str, repo: str, title: str,
                           head: str, base: str = "main",
                           body: str = "") -> Dict[str, Any]:
        """
        創建 Pull Request

        Args:
            owner: 倉庫擁有者
            repo: 倉庫名稱
            title: PR 標題
            head: 源分支
            base: 目標分支
            body: PR 描述

        Returns:
            創建的 PR 資訊
        """
        print("\n" + "=" * 70)
        print(f"創建 Pull Request: {title}")
        print("=" * 70)

        try:
            # 執行操作
            result = self.entity.execute(
                action="GITHUB_CREATE_PULL_REQUEST",
                params={
                    "owner": owner,
                    "repo": repo,
                    "title": title,
                    "head": head,
                    "base": base,
                    "body": body
                }
            )

            pr = result.get('data', {})
            print(f"\n✓ Pull Request 創建成功!")
            print(f"  編號: #{pr.get('number')}")
            print(f"  標題: {pr.get('title')}")
            print(f"  URL: {pr.get('html_url')}")
            print(f"  分支: {head} → {base}")

            return pr

        except Exception as e:
            print(f"✗ 創建 Pull Request 失敗: {e}")
            return {}

    def list_pull_requests(self, owner: str, repo: str, state: str = "open",
                          limit: int = 10) -> List[Dict[str, Any]]:
        """
        列出 Pull Requests

        Args:
            owner: 倉庫擁有者
            repo: 倉庫名稱
            state: PR 狀態 (open/closed/all)
            limit: 限制返回的數量

        Returns:
            PR 列表
        """
        print("\n" + "=" * 70)
        print(f"列出 {owner}/{repo} 的 Pull Requests")
        print("=" * 70)

        try:
            # 執行操作
            result = self.entity.execute(
                action="GITHUB_LIST_PULL_REQUESTS",
                params={
                    "owner": owner,
                    "repo": repo,
                    "state": state,
                    "per_page": limit
                }
            )

            prs = result.get('data', [])
            print(f"\n找到 {len(prs)} 個 {state} Pull Requests:")
            print("-" * 70)

            for i, pr in enumerate(prs, 1):
                number = pr.get('number')
                title = pr.get('title')
                user = pr.get('user', {}).get('login', 'Unknown')
                head = pr.get('head', {}).get('ref', 'unknown')
                base = pr.get('base', {}).get('ref', 'unknown')

                print(f"{i}. #{number}: {title}")
                print(f"   作者: {user}")
                print(f"   分支: {head} → {base}")
                print()

            return prs

        except Exception as e:
            print(f"✗ 列出 Pull Requests 失敗: {e}")
            return []

    def add_comment(self, owner: str, repo: str, issue_number: int,
                   comment: str) -> Dict[str, Any]:
        """
        在 Issue 或 PR 添加評論

        Args:
            owner: 倉庫擁有者
            repo: 倉庫名稱
            issue_number: Issue/PR 編號
            comment: 評論內容

        Returns:
            評論資訊
        """
        print("\n" + "=" * 70)
        print(f"添加評論到 #{issue_number}")
        print("=" * 70)

        try:
            # 執行操作
            result = self.entity.execute(
                action="GITHUB_CREATE_ISSUE_COMMENT",
                params={
                    "owner": owner,
                    "repo": repo,
                    "issue_number": issue_number,
                    "body": comment
                }
            )

            comment_data = result.get('data', {})
            print(f"\n✓ 評論添加成功!")
            print(f"  ID: {comment_data.get('id')}")
            print(f"  內容: {comment[:50]}...")

            return comment_data

        except Exception as e:
            print(f"✗ 添加評論失敗: {e}")
            return {}


def demo_repository_management():
    """
    演示倉庫管理功能
    """
    print("\n" + "=" * 80)
    print("GitHub 倉庫管理演示")
    print("=" * 80)

    try:
        github = GitHubIntegration()

        # 1. 列出倉庫
        print("\n1. 列出用戶倉庫")
        repos = github.list_repositories(limit=5)

        # 2. 創建新倉庫（註解掉以避免實際創建）
        print("\n2. 創建新倉庫（示例）")
        print("   github.create_repository(")
        print("       name='my-new-repo',")
        print("       description='這是一個測試倉庫',")
        print("       private=False")
        print("   )")

    except Exception as e:
        print(f"\n演示過程中發生錯誤: {e}")


def demo_issue_management():
    """
    演示 Issue 管理功能
    """
    print("\n" + "=" * 80)
    print("GitHub Issue 管理演示")
    print("=" * 80)

    try:
        github = GitHubIntegration()

        # 示例倉庫資訊（請替換為實際的倉庫）
        OWNER = "your-username"
        REPO = "your-repo"

        print(f"\n使用倉庫: {OWNER}/{REPO}")
        print("（請替換為實際的倉庫資訊）")

        # 1. 列出 Issues
        print("\n1. 列出開放的 Issues（示例）")
        print(f"   github.list_issues('{OWNER}', '{REPO}', state='open')")

        # 2. 創建 Issue
        print("\n2. 創建新 Issue（示例）")
        print("   github.create_issue(")
        print(f"       owner='{OWNER}',")
        print(f"       repo='{REPO}',")
        print("       title='新功能請求',")
        print("       body='詳細描述...',")
        print("       labels=['enhancement', 'feature']")
        print("   )")

    except Exception as e:
        print(f"\n演示過程中發生錯誤: {e}")


def demo_pr_workflow():
    """
    演示 Pull Request 工作流程
    """
    print("\n" + "=" * 80)
    print("GitHub Pull Request 工作流程演示")
    print("=" * 80)

    workflow_steps = [
        ("1. 創建功能分支", "git checkout -b feature/new-feature"),
        ("2. 進行代碼更改", "編輯文件並提交更改"),
        ("3. 推送到遠端", "git push origin feature/new-feature"),
        ("4. 創建 PR", "使用 Composio API 創建 Pull Request"),
        ("5. 代碼審查", "團隊成員審查並添加評論"),
        ("6. 合併 PR", "審查通過後合併到主分支")
    ]

    print("\nPull Request 工作流程:")
    print("-" * 80)
    for step, description in workflow_steps:
        print(f"{step}")
        print(f"   {description}")
        print()


def main():
    """
    主函數
    """
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║              Composio GitHub 整合範例                            ║
    ║                                                                  ║
    ║              自動化您的 GitHub 工作流程                          ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)

    # 演示倉庫管理
    demo_repository_management()

    # 演示 Issue 管理
    demo_issue_management()

    # 演示 PR 工作流程
    demo_pr_workflow()

    print("\n" + "=" * 80)
    print("GitHub 整合最佳實踐:")
    print("  • 使用有意義的提交訊息")
    print("  • 定期同步分支")
    print("  • 進行代碼審查")
    print("  • 使用 Issue 追蹤任務")
    print("  • 自動化重複性任務")
    print("=" * 80)


if __name__ == "__main__":
    main()
