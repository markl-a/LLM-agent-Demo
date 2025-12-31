"""
LangSmith 提示管理 - Prompt Hub

這個示例展示如何：
1. 使用 LangChain Hub 管理提示詞
2. 發布和共享提示詞
3. 版本控制提示詞
4. 拉取和使用共享提示詞
5. 提示詞最佳實踐

Prompt Hub 是集中管理提示詞的平台。
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


def setup_environment():
    """配置環境"""
    load_dotenv()
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    if not os.getenv("LANGCHAIN_PROJECT"):
        os.environ["LANGCHAIN_PROJECT"] = "prompt-hub-demo"
    console.print("[green]✓ 環境配置完成[/green]")


def pull_prompt_example():
    """示例 1：從 Hub 拉取提示詞"""
    console.print(Panel("[bold cyan]示例 1：從 Hub 拉取提示詞[/bold cyan]"))

    try:
        console.print("\n[cyan]從 LangChain Hub 拉取公開提示詞...[/cyan]\n")

        # 拉取一個熱門的提示詞
        # 注意：需要使用實際存在的提示詞
        # 這裡展示概念性代碼

        example_code = '''
from langchain import hub

# 拉取提示詞（使用完整路徑：username/prompt-name）
# 例如拉取一個 RAG 提示詞
prompt = hub.pull("rlm/rag-prompt")

# 查看提示詞內容
print(prompt.messages)
print(prompt.input_variables)

# 使用提示詞
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")
chain = prompt | llm

result = chain.invoke({
    "context": "LangSmith 是 LangChain 的可觀測性平台",
    "question": "什麼是 LangSmith？"
})

print(result.content)
        '''

        syntax = Syntax(example_code, "python", theme="monokai", line_numbers=True)
        console.print(syntax)

        console.print("\n[yellow]注意：拉取提示詞需要網絡連接到 LangChain Hub[/yellow]")

        # 實際演示（如果有可用的提示詞）
        console.print("\n[cyan]嘗試實際拉取...[/cyan]")

        try:
            # 嘗試拉取一個公開的提示詞
            prompt = hub.pull("rlm/rag-prompt")
            console.print("[green]✓ 成功拉取提示詞[/green]")
            console.print(f"輸入變量：{prompt.input_variables}")

        except Exception as e:
            console.print(f"[yellow]無法拉取提示詞（可能需要配置或提示詞不存在）：{e}[/yellow]")

    except Exception as e:
        console.print(f"[red]錯誤：{e}[/red]")


def push_prompt_example():
    """示例 2：推送提示詞到 Hub"""
    console.print(Panel("[bold cyan]示例 2：推送提示詞到 Hub[/bold cyan]"))

    example_code = '''
from langchain import hub
from langchain.prompts import ChatPromptTemplate

# 創建一個提示詞模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一個專業的技術文檔助手。"),
    ("human", "請解釋以下概念：{concept}")
])

# 推送到 Hub
# 格式：username/prompt-name
# username 是你的 LangChain Hub 用戶名
hub.push(
    "your-username/tech-doc-assistant",
    prompt,
    api_key=os.getenv("LANGCHAIN_API_KEY")
)

print("✓ 提示詞已推送到 Hub")

# 推送新版本（會自動創建新版本）
updated_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一個專業的技術文檔助手，請用簡潔的語言解釋。"),
    ("human", "請解釋以下概念：{concept}")
])

hub.push(
    "your-username/tech-doc-assistant",
    updated_prompt
)

print("✓ 已推送新版本")
    '''

    syntax = Syntax(example_code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)

    console.print("\n[yellow]注意：推送需要 LangChain Hub 帳號和 API Key[/yellow]")

    guide = """
[bold cyan]推送提示詞步驟：[/bold cyan]

1. [green]註冊 LangChain Hub[/green]
   - 訪問：https://smith.langchain.com/
   - 使用 LangSmith 帳號登入

2. [green]獲取 API Key[/green]
   - 在設置中生成 API Key
   - 設置環境變量：LANGCHAIN_API_KEY

3. [green]推送提示詞[/green]
   - 使用 hub.push() 方法
   - 命名格式：username/prompt-name
   - 自動版本控制

4. [green]管理提示詞[/green]
   - 在 Hub UI 中查看和編輯
   - 查看版本歷史
   - 設置公開/私有
    """

    console.print(Panel(guide, border_style="blue"))


def version_control_example():
    """示例 3：提示詞版本控制"""
    console.print(Panel("[bold cyan]示例 3：提示詞版本控制[/bold cyan]"))

    example_code = '''
from langchain import hub

# 拉取特定版本的提示詞
# 格式：username/prompt-name:commit-hash
prompt_v1 = hub.pull("username/my-prompt:abc123")

# 拉取最新版本（默認）
prompt_latest = hub.pull("username/my-prompt")

# 比較版本
print("版本 1:", prompt_v1.messages)
print("最新版本:", prompt_latest.messages)

# 查看提示詞歷史
# 需要在 LangChain Hub UI 中查看
# 或使用 SDK（如果支持）

# 使用特定版本運行評估
from langsmith import evaluate

def predict_v1(inputs):
    chain = prompt_v1 | llm
    return chain.invoke(inputs)

def predict_latest(inputs):
    chain = prompt_latest | llm
    return chain.invoke(inputs)

# 比較不同版本的性能
results_v1 = evaluate(predict_v1, data="test-dataset")
results_latest = evaluate(predict_latest, data="test-dataset")
    '''

    syntax = Syntax(example_code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)

    best_practices = """
[bold green]版本控制最佳實踐：[/bold green]

1. [cyan]語義化版本[/cyan]
   - 在描述中標註版本號
   - 重大改動：v1.0 → v2.0
   - 小改進：v1.0 → v1.1
   - 修復：v1.0.1 → v1.0.2

2. [cyan]變更日誌[/cyan]
   - 在描述中記錄變更
   - 說明改動原因
   - 記錄性能影響

3. [cyan]穩定版本[/cyan]
   - 為生產環境固定版本
   - 測試新版本後再升級
   - 保留回滾能力

4. [cyan]A/B 測試[/cyan]
   - 新版本先在測試環境驗證
   - 使用評估系統比較版本
   - 數據驅動決策
    """

    console.print(Panel(best_practices, border_style="green"))


def prompt_templates_examples():
    """示例 4：常用提示詞模板"""
    console.print(Panel("[bold cyan]示例 4：常用提示詞模板[/bold cyan]"))

    templates = {
        "問答助手": '''
from langchain.prompts import ChatPromptTemplate

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一個有幫助的助手。請基於給定的上下文回答問題。"),
    ("human", """上下文：{context}

問題：{question}

請提供簡潔準確的答案。""")
])
        ''',

        "代碼解釋": '''
code_explain_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一個資深程序員，擅長解釋代碼。"),
    ("human", """請解釋以下代碼：

```{language}
{code}
```

請說明：
1. 代碼的功能
2. 關鍵邏輯
3. 可能的改進點""")
])
        ''',

        "文本總結": '''
summary_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一個專業的內容總結專家。"),
    ("human", """請用{num_sentences}句話總結以下內容：

{text}

要求：
- 保留關鍵信息
- 語言簡潔
- 邏輯清晰""")
])
        ''',

        "翻譯助手": '''
translation_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一個專業的翻譯員，精通{source_lang}和{target_lang}。"),
    ("human", """請將以下{source_lang}翻譯成{target_lang}：

{text}

要求：
- 保持原意
- 語言自然
- 符合目標語言習慣""")
])
        ''',

        "創意寫作": '''
creative_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一個創意寫作專家。"),
    ("human", """主題：{topic}
風格：{style}
長度：{length}

請創作一個{genre}。""")
])
        '''
    }

    for name, code in templates.items():
        console.print(f"\n[bold green]{name}：[/bold green]")
        syntax = Syntax(code, "python", theme="monokai")
        console.print(syntax)
        console.print()


def few_shot_prompting():
    """示例 5：Few-shot 提示詞"""
    console.print(Panel("[bold cyan]示例 5：Few-shot Prompting[/bold cyan]"))

    example_code = '''
from langchain.prompts import FewShotChatMessagePromptTemplate, ChatPromptTemplate

# 定義示例
examples = [
    {
        "input": "快樂",
        "output": "悲傷"
    },
    {
        "input": "高",
        "output": "低"
    },
    {
        "input": "炎熱",
        "output": "寒冷"
    }
]

# 創建示例模板
example_prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}"),
    ("ai", "{output}")
])

# 創建 few-shot 提示詞
few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=examples
)

# 完整提示詞
final_prompt = ChatPromptTemplate.from_messages([
    ("system", "請給出相反的詞。"),
    few_shot_prompt,
    ("human", "{input}")
])

# 使用
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")
chain = final_prompt | llm

result = chain.invoke({"input": "光明"})
print(result.content)  # 應該輸出：黑暗
    '''

    syntax = Syntax(example_code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)

    console.print("\n[green]Few-shot 提示詞適用於：[/green]")
    console.print("- 需要特定格式的輸出")
    console.print("- 複雜的推理任務")
    console.print("- 風格模仿")
    console.print("- 提高準確性")


def prompt_optimization_tips():
    """提示詞優化技巧"""
    console.print(Panel("[bold cyan]提示詞優化技巧[/bold cyan]"))

    tips = """
[bold green]提示詞工程最佳實踐：[/bold green]

1. [cyan]清晰具體[/cyan]
   ✓ "用三句話總結"
   ✗ "簡短總結"

2. [cyan]提供上下文[/cyan]
   ✓ "作為Python專家，解釋列表推導式"
   ✗ "解釋列表推導式"

3. [cyan]使用分隔符[/cyan]
   ✓ 用 ```, ---, ### 分隔不同部分
   ✗ 混在一起

4. [cyan]指定輸出格式[/cyan]
   ✓ "以JSON格式輸出"
   ✓ "用項目符號列出"
   ✗ 沒有格式說明

5. [cyan]提供示例[/cyan]
   ✓ 使用 few-shot learning
   ✗ 只有指令

6. [cyan]迭代改進[/cyan]
   ✓ 測試 → 分析 → 優化 → 重複
   ✗ 一次性完成

7. [cyan]考慮邊緣情況[/cyan]
   ✓ "如果沒有足夠信息，說'我不知道'"
   ✗ 不處理異常情況

8. [cyan]控制創意性[/cyan]
   ✓ 事實性任務：temperature=0.0-0.3
   ✓ 創意任務：temperature=0.7-1.0

[bold yellow]優化流程：[/bold yellow]

1. 基準版本 → 測試
2. 識別問題案例
3. 改進提示詞
4. A/B 測試
5. 採用最佳版本
6. 重複

[bold yellow]評估指標：[/bold yellow]

- 準確性：答案是否正確
- 一致性：相似輸入產生相似輸出
- 完整性：是否涵蓋所有要點
- 簡潔性：是否冗餘
- 格式：是否符合要求
- 成本：token 使用量
    """

    console.print(tips)


def prompt_hub_workflow():
    """Prompt Hub 工作流"""
    console.print(Panel("[bold cyan]Prompt Hub 工作流[/bold cyan]"))

    workflow = """
[bold green]推薦的 Prompt Hub 工作流：[/bold green]

[cyan]階段 1：本地開發[/cyan]
1. 在代碼中創建提示詞模板
2. 本地測試和迭代
3. 使用 LangSmith 追蹤和評估

[cyan]階段 2：推送到 Hub[/cyan]
1. 提示詞穩定後推送到 Hub
2. 添加清晰的描述和標籤
3. 設置適當的可見性（公開/私有）

[cyan]階段 3：版本管理[/cyan]
1. 每次重要更新推送新版本
2. 在描述中記錄變更
3. 保留舊版本用於對比

[cyan]階段 4：團隊協作[/cyan]
1. 團隊成員從 Hub 拉取提示詞
2. 共享最佳實踐
3. 避免重複工作

[cyan]階段 5：生產部署[/cyan]
1. 在代碼中引用 Hub 提示詞
2. 固定版本號（不使用 latest）
3. 監控性能

[bold yellow]代碼示例：[/bold yellow]

```python
# 開發環境：使用最新版本
from langchain import hub
prompt = hub.pull("team/qa-prompt")

# 生產環境：固定版本
prompt = hub.pull("team/qa-prompt:abc123def")

# 或使用環境變量控制
import os
version = os.getenv("PROMPT_VERSION", "latest")
if version == "latest":
    prompt = hub.pull("team/qa-prompt")
else:
    prompt = hub.pull(f"team/qa-prompt:{version}")
```

[bold yellow]團隊規範建議：[/bold yellow]

- 命名：team-name/use-case-description
- 標籤：language, domain, use-case
- 描述：目的、使用場景、版本歷史
- 評審：重要提示詞需要評審
- 測試：推送前必須測試
    """

    console.print(workflow)


def main():
    """主函數"""
    console.print(Panel.fit(
        "[bold green]LangSmith Prompt Hub[/bold green]",
        border_style="green"
    ))

    # 設置環境
    setup_environment()

    console.print("\n" + "="*60 + "\n")

    # 運行示例
    pull_prompt_example()
    console.print("\n" + "="*60 + "\n")

    push_prompt_example()
    console.print("\n" + "="*60 + "\n")

    version_control_example()
    console.print("\n" + "="*60 + "\n")

    prompt_templates_examples()
    console.print("\n" + "="*60 + "\n")

    few_shot_prompting()
    console.print("\n" + "="*60 + "\n")

    prompt_optimization_tips()
    console.print("\n" + "="*60 + "\n")

    prompt_hub_workflow()

    # 總結
    console.print(Panel("""
[bold green]Prompt Hub 總結[/bold green]

核心功能：
1. ✓ 集中管理提示詞
2. ✓ 版本控制
3. ✓ 團隊協作
4. ✓ 共享和復用
5. ✓ 與 LangChain 無縫集成

使用場景：
- 團隊協作開發
- 提示詞版本管理
- 最佳實踐共享
- A/B 測試不同版本
- 生產環境部署

最佳實踐：
✓ 使用描述性名稱
✓ 添加詳細描述
✓ 版本控制重要變更
✓ 測試後再推送
✓ 生產環境固定版本
✓ 定期審查和優化

下一步：
- 訪問 https://smith.langchain.com/ 探索 Hub
- 查看 06_AB測試.py 比較不同提示詞
- 查看 04_評估系統.py 評估提示詞性能
- 查看社區共享的優秀提示詞

提示：
- Prompt Hub 是 LangChain 生態的一部分
- 需要 LangSmith 帳號
- 支持公開和私有提示詞
- 自動版本控制
- 與評估系統集成
    """, title="總結", border_style="green"))


if __name__ == "__main__":
    main()
