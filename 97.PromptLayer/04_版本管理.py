"""
PromptLayer 版本管理示例

本示例展示：
1. 模板版本控制
2. 版本對比
3. 版本回滾
4. 版本最佳實踐
"""

import os
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

console = Console()


def show_version_concept():
    """版本控制概念"""
    console.print("\n[cyan]版本控制概念[/cyan]\n")

    concept = """PromptLayer 自動為每個模板更新創建新版本

版本特性：
• 自動版本號：每次更新自動遞增
• 完整歷史：保留所有版本
• 獨立使用：可以使用任何歷史版本
• 不可變性：已創建的版本不能修改
• 元數據：記錄創建時間、創建者等

使用場景：
• A/B 測試不同版本
• 回滾到穩定版本
• 對比版本效果
• 追蹤提示演進"""

    console.print(Panel(concept, border_style="cyan"))
    console.print()


def create_versions():
    """創建版本"""
    console.print("[cyan]1. 創建和管理版本[/cyan]\n")

    code = """import promptlayer
import requests

# 初始版本（版本 1）
create_template(
    name="product_description",
    prompt=\"\"\"為以下產品撰寫描述：
產品名稱：{{product_name}}
特點：{{features}}\"\"\"
)

# 版本 2：添加目標受眾
update_template(
    name="product_description",
    prompt=\"\"\"為以下產品撰寫吸引 {{target_audience}} 的描述：
產品名稱：{{product_name}}
特點：{{features}}
重點突出：{{highlights}}\"\"\"
)

# 版本 3：優化結構
update_template(
    name="product_description",
    prompt=\"\"\"產品描述撰寫任務：

目標受眾：{{target_audience}}
產品名稱：{{product_name}}

產品特點：
{{features}}

請撰寫一段專業的產品描述（約100字），突出以下賣點：
{{highlights}}

語氣：{{tone}}\"\"\"
)

# 每次更新都會創建新版本
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def use_specific_version():
    """使用特定版本"""
    console.print("[cyan]2. 使用特定版本[/cyan]\n")

    code = """# 使用最新版本（默認）
response_latest = promptlayer.run(
    prompt_name="product_description",
    input_variables={
        "product_name": "智能手錶",
        "features": "健康監測、GPS、7天續航",
        "target_audience": "健身愛好者",
        "highlights": "精準心率監測",
        "tone": "專業、可信"
    }
)

# 使用版本 2
response_v2 = promptlayer.run(
    prompt_name="product_description",
    prompt_version=2,  # 明確指定版本
    input_variables={
        "product_name": "智能手錶",
        "features": "健康監測、GPS",
        "target_audience": "健身愛好者",
        "highlights": "精準心率監測"
    }
)

# 使用版本 1
response_v1 = promptlayer.run(
    prompt_name="product_description",
    prompt_version=1,
    input_variables={
        "product_name": "智能手錶",
        "features": "健康監測、GPS、7天續航"
    }
)
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def compare_versions():
    """對比版本"""
    console.print("[cyan]3. 版本對比分析[/cyan]\n")

    code = """def compare_template_versions(template_name, version1, version2):
    \"\"\"對比兩個版本的性能\"\"\"
    import requests
    import pandas as pd

    # 獲取兩個版本的使用數據
    url = "https://api.promptlayer.com/rest/search-requests"

    # 版本 1 數據
    params_v1 = {
        "api_key": os.getenv("PROMPTLAYER_API_KEY"),
        "template_name": template_name,
        "template_version": version1
    }
    requests_v1 = requests.post(url, json=params_v1).json()

    # 版本 2 數據
    params_v2 = {
        "api_key": os.getenv("PROMPTLAYER_API_KEY"),
        "template_name": template_name,
        "template_version": version2
    }
    requests_v2 = requests.post(url, json=params_v2).json()

    # 統計對比
    def calculate_stats(requests_data):
        if not requests_data:
            return None

        return {
            'count': len(requests_data),
            'avg_latency': sum(r['latency'] for r in requests_data) / len(requests_data),
            'avg_tokens': sum(r['total_tokens'] for r in requests_data) / len(requests_data),
            'avg_score': sum(r.get('score', 0) for r in requests_data if r.get('score')) /
                        len([r for r in requests_data if r.get('score')]) if any(r.get('score') for r in requests_data) else 0
        }

    stats_v1 = calculate_stats(requests_v1)
    stats_v2 = calculate_stats(requests_v2)

    # 顯示對比
    print(f"=== 版本對比: {template_name} ===\\n")
    print(f"{'指標':<15} {'版本 ' + str(version1):<15} {'版本 ' + str(version2):<15} {'差異':<10}")
    print("-" * 60)

    if stats_v1 and stats_v2:
        print(f"{'使用次數':<15} {stats_v1['count']:<15} {stats_v2['count']:<15} {stats_v2['count'] - stats_v1['count']:<10}")
        print(f"{'平均延遲':<15} {stats_v1['avg_latency']:<15.2f} {stats_v2['avg_latency']:<15.2f} {stats_v2['avg_latency'] - stats_v1['avg_latency']:<10.2f}")
        print(f"{'平均 Token':<15} {stats_v1['avg_tokens']:<15.1f} {stats_v2['avg_tokens']:<15.1f} {stats_v2['avg_tokens'] - stats_v1['avg_tokens']:<10.1f}")
        print(f"{'平均評分':<15} {stats_v1['avg_score']:<15.1f} {stats_v2['avg_score']:<15.1f} {stats_v2['avg_score'] - stats_v1['avg_score']:<10.1f}")

    return stats_v1, stats_v2

# 執行對比
compare_template_versions("product_description", 2, 3)
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def version_rollback():
    """版本回滾"""
    console.print("[cyan]4. 版本回滾策略[/cyan]\n")

    code = """def rollback_to_version(template_name, target_version):
    \"\"\"回滾到指定版本\"\"\"

    # 方式 1：在代碼中指定使用舊版本
    # 這不會創建新版本，只是使用舊版本
    response = promptlayer.run(
        prompt_name=template_name,
        prompt_version=target_version,  # 使用舊版本
        input_variables={...}
    )

    # 方式 2：將舊版本的內容作為新版本發布
    # 這會創建一個新版本（內容與舊版本相同）
    def create_rollback_version(template_name, source_version):
        # 獲取源版本的內容
        url = f"https://api.promptlayer.com/rest/get-template"
        params = {
            "api_key": os.getenv("PROMPTLAYER_API_KEY"),
            "template_name": template_name,
            "version": source_version
        }
        template_data = requests.get(url, params=params).json()

        # 創建新版本（內容相同）
        update_template(
            name=template_name,
            prompt_template=template_data['prompt_template'],
            variables=template_data['variables'],
            metadata={
                "rollback_from_version": source_version,
                "reason": "回滾到穩定版本"
            }
        )

        print(f"已回滾 {template_name} 到版本 {source_version} 的內容")

    # 執行回滾
    create_rollback_version("product_description", 2)
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def version_metadata():
    """版本元數據"""
    console.print("[cyan]5. 版本元數據管理[/cyan]\n")

    code = """def add_version_metadata(template_name, version, metadata):
    \"\"\"為版本添加元數據（通過 API）\"\"\"

    # 創建版本時添加元數據
    result = update_template(
        name=template_name,
        prompt_template=new_prompt,
        variables=variables,
        metadata={
            "author": "張三",
            "change_type": "optimization",
            "tested": True,
            "approved_by": "李四",
            "notes": "優化了輸出格式，提高了可讀性",
            "jira_ticket": "PROJ-123"
        }
    )

    return result


def get_version_history(template_name):
    \"\"\"獲取完整的版本歷史\"\"\"
    url = "https://api.promptlayer.com/rest/get-template-versions"
    params = {
        "api_key": os.getenv("PROMPTLAYER_API_KEY"),
        "template_name": template_name
    }

    versions = requests.get(url, params=params).json()

    print(f"=== {template_name} 版本歷史 ===\\n")
    for v in versions:
        print(f"版本 {v['version']}:")
        print(f"  創建時間: {v['created_at']}")
        print(f"  創建者: {v.get('metadata', {}).get('author', '未知')}")
        print(f"  變更類型: {v.get('metadata', {}).get('change_type', '未指定')}")
        print(f"  說明: {v.get('metadata', {}).get('notes', '無')}")
        print()

# 使用示例
get_version_history("product_description")
"""

    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def show_best_practices():
    """版本管理最佳實踐"""
    console.print("[cyan]版本管理最佳實踐[/cyan]\n")

    practices = """1. 版本策略
   - 重大更改創建新版本
   - 小修改可以覆蓋當前版本（開發階段）
   - 生產版本不要頻繁更新
   - 保留關鍵版本的說明

2. 測試流程
   - 新版本先在測試環境驗證
   - 進行 A/B 測試對比
   - 收集足夠的數據再推廣
   - 有問題及時回滾

3. 文檔化
   - 記錄每個版本的變更
   - 說明變更原因
   - 標注重要版本
   - 保留決策過程

4. 回滾準備
   - 了解當前生產版本
   - 準備回滾腳本
   - 測試回滾流程
   - 監控回滾後效果

5. 版本清理
   - 定期審查舊版本
   - 歸檔不再使用的版本
   - 保留關鍵里程碑版本
   - 清理測試版本

6. 團隊協作
   - 版本更新通知團隊
   - 重大更改需要審批
   - 共享版本文檔
   - 定期版本回顧"""

    console.print(Panel(practices, border_style="cyan"))
    console.print()


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold cyan]PromptLayer 版本管理示例[/bold cyan]\n"
        "[dim]學習如何管理模板版本[/dim]",
        border_style="cyan"
    ))

    # 1. 版本概念
    show_version_concept()

    # 2. 創建版本
    create_versions()

    # 3. 使用特定版本
    use_specific_version()

    # 4. 版本對比
    compare_versions()

    # 5. 版本回滾
    version_rollback()

    # 6. 版本元數據
    version_metadata()

    # 7. 最佳實踐
    show_best_practices()

    # 完成
    console.print("="*60)
    console.print("[bold green]✓ 版本管理示例完成！[/bold green]\n")
    console.print("[cyan]下一步:[/cyan]")
    console.print("  1. 查看 05_AB測試.py - 進行 A/B 測試")
    console.print("  2. 查看 06_評分系統.py - 評估版本質量")
    console.print("  3. 實踐: 為模板創建和管理版本")


if __name__ == "__main__":
    main()
