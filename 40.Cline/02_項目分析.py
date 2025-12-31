"""
Cline 項目分析示例

展示如何使用 Cline 分析代碼庫：
1. 分析項目結構
2. 識別技術棧
3. 找出潛在問題
4. 生成項目文檔
5. 代碼質量評估

這對於理解新項目或審查現有代碼非常有用。
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ProjectStructure:
    """項目結構數據類"""
    root_path: str
    total_files: int
    total_lines: int
    languages: Dict[str, int]
    directories: List[str]
    main_files: List[str]


@dataclass
class TechStack:
    """技術棧數據類"""
    languages: List[str]
    frameworks: List[str]
    databases: List[str]
    tools: List[str]
    package_managers: List[str]


@dataclass
class CodeIssue:
    """代碼問題數據類"""
    file: str
    line: int
    severity: str  # "high", "medium", "low"
    category: str  # "security", "performance", "style", etc.
    description: str
    suggestion: str


class ClineProjectAnalyzer:
    """Cline 項目分析器"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化分析器"""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("需要提供 ANTHROPIC_API_KEY")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"

    def _call_claude(self, prompt: str, system: str = None) -> str:
        """調用 Claude API"""
        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": messages
        }

        if system:
            kwargs["system"] = system

        response = self.client.messages.create(**kwargs)
        return response.content[0].text

    def analyze_structure(self, project_path: str) -> Dict[str, Any]:
        """
        分析項目結構

        Args:
            project_path: 項目路徑

        Returns:
            項目結構分析結果
        """
        print(f"\n🔍 分析項目結構: {project_path}")

        # 收集項目信息
        project_info = self._scan_project(project_path)

        # 使用 Claude 分析
        prompt = f"""
        請分析以下項目結構：

        {json.dumps(project_info, indent=2, ensure_ascii=False)}

        請提供：
        1. 項目類型（Web 應用、庫、工具等）
        2. 主要功能模塊
        3. 架構模式
        4. 組織結構評價
        5. 改進建議

        請用 JSON 格式返回分析結果。
        """

        system = "你是一個專業的代碼架構分析師，擅長分析項目結構並提供改進建議。"

        response = self._call_claude(prompt, system)

        return {
            "raw_info": project_info,
            "analysis": response
        }

    def _scan_project(self, project_path: str) -> Dict[str, Any]:
        """掃描項目獲取基本信息"""
        path = Path(project_path)

        if not path.exists():
            return {"error": "項目路徑不存在"}

        files = []
        directories = []
        languages = {}
        total_lines = 0

        # 忽略的目錄
        ignore_dirs = {
            'node_modules', '.git', '__pycache__', 'venv',
            'env', 'dist', 'build', '.idea', '.vscode'
        }

        # 遍歷項目
        for item in path.rglob('*'):
            # 跳過忽略的目錄
            if any(part in ignore_dirs for part in item.parts):
                continue

            if item.is_file():
                # 記錄文件
                relative_path = str(item.relative_to(path))
                files.append(relative_path)

                # 統計語言
                suffix = item.suffix.lower()
                if suffix:
                    languages[suffix] = languages.get(suffix, 0) + 1

                # 統計行數（僅文本文件）
                try:
                    if suffix in ['.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp', '.md']:
                        with open(item, 'r', encoding='utf-8') as f:
                            total_lines += len(f.readlines())
                except:
                    pass

            elif item.is_dir():
                relative_path = str(item.relative_to(path))
                if relative_path and not any(part in ignore_dirs for part in item.parts):
                    directories.append(relative_path)

        # 識別主要文件
        main_files = []
        important_files = [
            'README.md', 'package.json', 'requirements.txt',
            'Cargo.toml', 'go.mod', 'pom.xml', 'build.gradle',
            'Dockerfile', 'docker-compose.yml', '.env.example'
        ]

        for f in files:
            if any(imp in f for imp in important_files):
                main_files.append(f)

        return {
            "total_files": len(files),
            "total_lines": total_lines,
            "languages": languages,
            "directories": directories[:20],  # 限制數量
            "main_files": main_files,
            "sample_files": files[:30]  # 樣本文件
        }

    def identify_tech_stack(self, project_path: str) -> TechStack:
        """
        識別技術棧

        Args:
            project_path: 項目路徑

        Returns:
            技術棧信息
        """
        print(f"\n🔧 識別技術棧: {project_path}")

        path = Path(project_path)
        tech_indicators = {}

        # 檢查配置文件
        config_files = {
            'package.json': 'Node.js/JavaScript',
            'requirements.txt': 'Python',
            'Pipfile': 'Python',
            'Cargo.toml': 'Rust',
            'go.mod': 'Go',
            'pom.xml': 'Java/Maven',
            'build.gradle': 'Java/Gradle',
            'composer.json': 'PHP',
            'Gemfile': 'Ruby'
        }

        for config_file, tech in config_files.items():
            file_path = path / config_file
            if file_path.exists():
                tech_indicators[config_file] = {
                    'tech': tech,
                    'exists': True
                }

                # 讀取文件內容（部分）
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read(2000)  # 只讀取前 2000 字符
                        tech_indicators[config_file]['content'] = content
                except:
                    pass

        # 使用 Claude 分析
        prompt = f"""
        基於以下項目配置文件，請識別完整的技術棧：

        {json.dumps(tech_indicators, indent=2, ensure_ascii=False)}

        請識別：
        1. 編程語言
        2. 框架和庫
        3. 數據庫
        4. 開發工具
        5. 包管理器

        請用 JSON 格式返回，格式如下：
        {{
            "languages": ["Python", "JavaScript"],
            "frameworks": ["FastAPI", "React"],
            "databases": ["PostgreSQL", "Redis"],
            "tools": ["Docker", "Git"],
            "package_managers": ["pip", "npm"]
        }}
        """

        response = self._call_claude(prompt)

        try:
            # 嘗試解析 JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                tech_data = json.loads(json_match.group())
                return TechStack(**tech_data)
        except:
            pass

        # 如果解析失敗，返回默認值
        return TechStack(
            languages=["Unknown"],
            frameworks=[],
            databases=[],
            tools=[],
            package_managers=[]
        )

    def find_issues(self, project_path: str, file_pattern: str = "*.py") -> List[CodeIssue]:
        """
        查找潛在問題

        Args:
            project_path: 項目路徑
            file_pattern: 文件模式

        Returns:
            發現的問題列表
        """
        print(f"\n🐛 查找潛在問題: {project_path}")

        path = Path(project_path)
        issues = []

        # 獲取匹配的文件
        files = list(path.glob(f"**/{file_pattern}"))[:10]  # 限制文件數量

        for file_path in files:
            print(f"  檢查: {file_path.name}")

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(3000)  # 限制內容大小

                # 使用 Claude 分析
                prompt = f"""
                請分析以下代碼，找出潛在問題：

                文件: {file_path.name}
                ```
                {content}
                ```

                請識別：
                1. 安全問題
                2. 性能問題
                3. 代碼風格問題
                4. 潛在 Bug

                對每個問題，請提供：
                - 問題描述
                - 嚴重程度（high/medium/low）
                - 改進建議

                如果沒有問題，返回空列表。
                請用簡潔的方式列出問題。
                """

                response = self._call_claude(prompt)

                # 簡單解析響應（實際應用中需要更複雜的解析）
                if "沒有發現" not in response and "沒有明顯" not in response:
                    issues.append(CodeIssue(
                        file=str(file_path.relative_to(path)),
                        line=0,
                        severity="medium",
                        category="general",
                        description=response[:200],
                        suggestion="參見完整分析"
                    ))

            except Exception as e:
                print(f"  ⚠️  分析失敗: {e}")

        return issues

    def generate_documentation(self, project_path: str) -> str:
        """
        生成項目文檔

        Args:
            project_path: 項目路徑

        Returns:
            生成的文檔（Markdown 格式）
        """
        print(f"\n📝 生成項目文檔: {project_path}")

        # 收集項目信息
        structure_info = self._scan_project(project_path)

        # 讀取 README（如果存在）
        readme_content = ""
        readme_path = Path(project_path) / "README.md"
        if readme_path.exists():
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read(1000)
            except:
                pass

        prompt = f"""
        基於以下項目信息，生成專業的項目文檔（README.md）：

        項目結構:
        {json.dumps(structure_info, indent=2, ensure_ascii=False)}

        現有 README:
        {readme_content if readme_content else "無"}

        請生成包含以下部分的文檔：
        1. 項目簡介
        2. 功能特性
        3. 技術棧
        4. 項目結構
        5. 安裝說明
        6. 使用示例
        7. 開發指南
        8. 貢獻指南

        請使用 Markdown 格式。
        """

        documentation = self._call_claude(prompt)

        return documentation

    def evaluate_code_quality(self, project_path: str) -> Dict[str, Any]:
        """
        評估代碼質量

        Args:
            project_path: 項目路徑

        Returns:
            質量評估報告
        """
        print(f"\n📊 評估代碼質量: {project_path}")

        structure_info = self._scan_project(project_path)

        # 收集代碼樣本
        path = Path(project_path)
        code_samples = []

        for ext in ['.py', '.js', '.ts', '.java']:
            files = list(path.glob(f"**/*{ext}"))[:3]  # 每種語言取 3 個樣本
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read(1000)
                        code_samples.append({
                            'file': str(file_path.relative_to(path)),
                            'content': content
                        })
                except:
                    pass

        prompt = f"""
        請評估以下項目的代碼質量：

        項目統計:
        - 總文件數: {structure_info['total_files']}
        - 總行數: {structure_info['total_lines']}
        - 語言分布: {json.dumps(structure_info['languages'])}

        代碼樣本:
        {json.dumps(code_samples[:3], indent=2, ensure_ascii=False)}

        請從以下維度評分（1-10）：
        1. 代碼可讀性
        2. 代碼組織
        3. 註釋質量
        4. 命名規範
        5. 錯誤處理
        6. 測試覆蓋（如果有）
        7. 文檔完整性
        8. 整體質量

        並提供改進建議。

        請用 JSON 格式返回評分和建議。
        """

        response = self._call_claude(prompt)

        return {
            "project_stats": structure_info,
            "quality_report": response
        }


def example_analyze_structure():
    """示例 1: 分析項目結構"""
    print("=" * 60)
    print("示例 1: 分析項目結構")
    print("=" * 60)

    analyzer = ClineProjectAnalyzer()

    # 分析當前項目
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)

    result = analyzer.analyze_structure(parent_dir)

    print("\n項目信息:")
    print(json.dumps(result['raw_info'], indent=2, ensure_ascii=False))
    print("\nClaude 分析:")
    print(result['analysis'])


def example_identify_tech_stack():
    """示例 2: 識別技術棧"""
    print("\n" + "=" * 60)
    print("示例 2: 識別技術棧")
    print("=" * 60)

    analyzer = ClineProjectAnalyzer()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)

    tech_stack = analyzer.identify_tech_stack(parent_dir)

    print("\n技術棧:")
    print(f"  編程語言: {', '.join(tech_stack.languages)}")
    print(f"  框架: {', '.join(tech_stack.frameworks) if tech_stack.frameworks else '未檢測到'}")
    print(f"  數據庫: {', '.join(tech_stack.databases) if tech_stack.databases else '未檢測到'}")
    print(f"  工具: {', '.join(tech_stack.tools) if tech_stack.tools else '未檢測到'}")
    print(f"  包管理器: {', '.join(tech_stack.package_managers) if tech_stack.package_managers else '未檢測到'}")


def example_find_issues():
    """示例 3: 查找潛在問題"""
    print("\n" + "=" * 60)
    print("示例 3: 查找潛在問題")
    print("=" * 60)

    analyzer = ClineProjectAnalyzer()

    current_dir = os.path.dirname(os.path.abspath(__file__))

    issues = analyzer.find_issues(current_dir, "*.py")

    print(f"\n發現 {len(issues)} 個潛在問題:")
    for i, issue in enumerate(issues, 1):
        print(f"\n問題 {i}:")
        print(f"  文件: {issue.file}")
        print(f"  嚴重程度: {issue.severity}")
        print(f"  描述: {issue.description}")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Cline 項目分析示例")
    print("=" * 60)

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠️  警告: 未設置 ANTHROPIC_API_KEY")
        return

    try:
        # 運行示例（注釋以節省 API 調用）
        # example_analyze_structure()
        # example_identify_tech_stack()
        # example_find_issues()

        print("\n✅ 示例代碼已準備就緒")
        print("\n💡 提示:")
        print("1. 取消注釋 main() 中的函數來運行示例")
        print("2. 項目分析可幫助快速理解新代碼庫")
        print("3. 使用技術棧識別了解項目依賴")
        print("4. 問題檢測幫助提高代碼質量")

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
