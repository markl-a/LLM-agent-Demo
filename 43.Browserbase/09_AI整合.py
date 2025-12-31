"""
Browserbase AI 整合示例
=======================

本模塊展示了如何將 Browserbase 與 AI 模型（OpenAI、Claude 等）整合。
包括智能網頁分析、自動化決策、內容生成、對話式瀏覽等。

主要內容:
1. OpenAI GPT 整合
2. Claude 整合
3. 智能網頁分析
4. 自動化決策
5. 內容提取和總結
6. 對話式網頁助手

作者: Browserbase 示例團隊
日期: 2025-12-31
"""

import os
import json
import time
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from dotenv import load_dotenv


# 加載環境變量
load_dotenv()


class AIProvider(Enum):
    """AI 提供商"""
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"


class MessageRole(Enum):
    """消息角色"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    """對話消息"""
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            "role": self.role.value,
            "content": self.content
        }


@dataclass
class AIResponse:
    """AI 響應"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    timestamp: datetime = field(default_factory=datetime.now)


class AIClient:
    """
    AI 客戶端基類

    提供與 AI 模型交互的統一接口。
    """

    def __init__(self, provider: AIProvider, api_key: str, model: str):
        """
        初始化 AI 客戶端

        Args:
            provider: AI 提供商
            api_key: API 密鑰
            model: 模型名稱
        """
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.conversation_history: List[Message] = []

        print(f"[AIClient] 初始化: {provider.value} - {model}")

    def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> AIResponse:
        """
        發送聊天消息

        Args:
            message: 用戶消息
            system_prompt: 系統提示詞
            temperature: 溫度參數
            max_tokens: 最大 token 數

        Returns:
            AI 響應
        """
        # 構建消息列表
        messages = []

        if system_prompt:
            messages.append(Message(MessageRole.SYSTEM, system_prompt))

        # 添加歷史對話
        messages.extend(self.conversation_history)

        # 添加當前消息
        user_message = Message(MessageRole.USER, message)
        messages.append(user_message)

        print(f"\n[AIClient] 發送消息到 {self.provider.value}")
        print(f"  用戶: {message[:100]}...")

        # 模擬 AI 響應
        response = self._mock_ai_response(messages, temperature, max_tokens)

        # 保存到歷史
        self.conversation_history.append(user_message)
        self.conversation_history.append(
            Message(MessageRole.ASSISTANT, response.content)
        )

        print(f"  AI: {response.content[:100]}...")

        return response

    def _mock_ai_response(
        self,
        messages: List[Message],
        temperature: float,
        max_tokens: int
    ) -> AIResponse:
        """模擬 AI 響應"""
        # 實際應該調用真實的 AI API
        return AIResponse(
            content=f"這是一個模擬的 {self.provider.value} 響應。根據您的問題，我建議...",
            model=self.model,
            usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
            finish_reason="stop"
        )

    def clear_history(self):
        """清空對話歷史"""
        self.conversation_history.clear()
        print("[AIClient] 對話歷史已清空")


class OpenAIClient(AIClient):
    """OpenAI 客戶端"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4"
    ):
        """
        初始化 OpenAI 客戶端

        Args:
            api_key: API 密鑰
            model: 模型名稱
        """
        api_key = api_key or os.getenv("OPENAI_API_KEY", "mock_key")
        super().__init__(AIProvider.OPENAI, api_key, model)


class ClaudeClient(AIClient):
    """Claude 客戶端"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-sonnet-20240229"
    ):
        """
        初始化 Claude 客戶端

        Args:
            api_key: API 密鑰
            model: 模型名稱
        """
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "mock_key")
        super().__init__(AIProvider.CLAUDE, api_key, model)


class IntelligentBrowser:
    """
    智能瀏覽器

    結合 AI 能力的智能瀏覽器代理。
    """

    def __init__(self, ai_client: AIClient):
        """
        初始化智能瀏覽器

        Args:
            ai_client: AI 客戶端
        """
        self.ai_client = ai_client
        self.current_url = None
        self.page_content = None
        print("[IntelligentBrowser] 初始化完成")

    def navigate_and_analyze(self, url: str) -> Dict:
        """
        導航並分析頁面

        Args:
            url: 目標 URL

        Returns:
            分析結果
        """
        print(f"\n[IntelligentBrowser] 導航到: {url}")

        # 模擬加載頁面
        self.current_url = url
        self.page_content = self._mock_page_content(url)

        print(f"  頁面加載完成 ({len(self.page_content)} 字符)")

        # 使用 AI 分析頁面
        analysis = self._analyze_page()

        return analysis

    def _mock_page_content(self, url: str) -> str:
        """模擬頁面內容"""
        return f"""
        <html>
        <head><title>示例頁面</title></head>
        <body>
            <h1>歡迎來到示例網站</h1>
            <p>這是一個關於 {url} 的示例頁面。</p>
            <article>
                <h2>主要內容</h2>
                <p>這裡有一些有趣的內容和信息...</p>
            </article>
        </body>
        </html>
        """

    def _analyze_page(self) -> Dict:
        """分析頁面"""
        print("  使用 AI 分析頁面...")

        prompt = f"""
        請分析以下網頁內容：

        URL: {self.current_url}
        內容: {self.page_content[:500]}...

        請提供：
        1. 頁面主題
        2. 主要內容摘要
        3. 關鍵信息點
        4. 建議的操作
        """

        response = self.ai_client.chat(
            message=prompt,
            system_prompt="你是一個專業的網頁分析助手。"
        )

        return {
            "url": self.current_url,
            "analysis": response.content,
            "timestamp": datetime.now().isoformat()
        }

    def extract_information(self, query: str) -> str:
        """
        從頁面提取特定信息

        Args:
            query: 查詢問題

        Returns:
            提取的信息
        """
        print(f"\n[IntelligentBrowser] 提取信息: {query}")

        if not self.page_content:
            return "請先導航到一個頁面"

        prompt = f"""
        基於以下網頁內容：
        {self.page_content[:1000]}

        請回答這個問題：{query}
        """

        response = self.ai_client.chat(
            message=prompt,
            system_prompt="你是一個信息提取專家，請準確簡潔地回答問題。"
        )

        return response.content

    def suggest_next_action(self) -> str:
        """
        建議下一步操作

        Returns:
            建議的操作
        """
        print("\n[IntelligentBrowser] 請求操作建議...")

        if not self.page_content:
            return "請先導航到一個頁面"

        prompt = f"""
        我目前在這個頁面：{self.current_url}

        頁面內容：
        {self.page_content[:500]}

        請建議我接下來應該做什麼？
        """

        response = self.ai_client.chat(
            message=prompt,
            system_prompt="你是一個網頁瀏覽助手，幫助用戶高效瀏覽網頁。"
        )

        return response.content


class ContentSummarizer:
    """
    內容摘要器

    使用 AI 對網頁內容進行摘要。
    """

    def __init__(self, ai_client: AIClient):
        """
        初始化摘要器

        Args:
            ai_client: AI 客戶端
        """
        self.ai_client = ai_client
        print("[ContentSummarizer] 初始化完成")

    def summarize(
        self,
        content: str,
        max_length: int = 200,
        style: str = "professional"
    ) -> str:
        """
        摘要內容

        Args:
            content: 原始內容
            max_length: 最大長度
            style: 摘要風格 (professional, casual, bullet_points)

        Returns:
            摘要文本
        """
        print(f"\n[ContentSummarizer] 摘要內容 ({len(content)} 字符)")
        print(f"  風格: {style}")
        print(f"  最大長度: {max_length}")

        style_prompts = {
            "professional": "請用專業、正式的語氣",
            "casual": "請用輕鬆、口語化的方式",
            "bullet_points": "請用要點列表的形式"
        }

        prompt = f"""
        請摘要以下內容，{style_prompts.get(style, '')}，
        控制在 {max_length} 字以內：

        {content}
        """

        response = self.ai_client.chat(
            message=prompt,
            system_prompt="你是一個專業的內容摘要專家。"
        )

        print(f"  生成摘要: {len(response.content)} 字符")
        return response.content

    def extract_key_points(self, content: str, num_points: int = 5) -> List[str]:
        """
        提取關鍵點

        Args:
            content: 原始內容
            num_points: 關鍵點數量

        Returns:
            關鍵點列表
        """
        print(f"\n[ContentSummarizer] 提取 {num_points} 個關鍵點")

        prompt = f"""
        請從以下內容中提取 {num_points} 個最重要的關鍵點：

        {content}

        請以 JSON 數組格式返回，例如：["要點1", "要點2", ...]
        """

        response = self.ai_client.chat(
            message=prompt,
            system_prompt="你是一個信息提取專家。"
        )

        # 嘗試解析 JSON
        try:
            # 簡化處理，實際應該更嚴格
            points = ["關鍵點1", "關鍵點2", "關鍵點3"]
            return points[:num_points]
        except:
            return response.content.split('\n')[:num_points]


class WebAutomationAgent:
    """
    網頁自動化代理

    使用 AI 進行智能網頁自動化。
    """

    def __init__(self, ai_client: AIClient):
        """
        初始化自動化代理

        Args:
            ai_client: AI 客戶端
        """
        self.ai_client = ai_client
        self.action_history = []
        print("[WebAutomationAgent] 初始化完成")

    def decide_action(
        self,
        goal: str,
        current_state: Dict
    ) -> Dict:
        """
        決定下一步操作

        Args:
            goal: 目標描述
            current_state: 當前狀態

        Returns:
            決策結果
        """
        print(f"\n[WebAutomationAgent] 決策下一步操作")
        print(f"  目標: {goal}")

        prompt = f"""
        目標：{goal}

        當前狀態：
        - URL: {current_state.get('url', 'unknown')}
        - 頁面標題: {current_state.get('title', 'unknown')}
        - 可用操作: {current_state.get('available_actions', [])}

        歷史操作：
        {json.dumps(self.action_history[-5:], ensure_ascii=False, indent=2)}

        請決定下一步應該執行什麼操作，以 JSON 格式返回：
        {{
            "action": "操作類型 (navigate/click/type/wait)",
            "target": "目標元素或URL",
            "value": "輸入值（如果需要）",
            "reason": "原因說明"
        }}
        """

        response = self.ai_client.chat(
            message=prompt,
            system_prompt="你是一個網頁自動化專家，善於規劃和執行任務。"
        )

        # 模擬解析 JSON
        decision = {
            "action": "click",
            "target": "#submit-button",
            "value": None,
            "reason": "根據目標，需要點擊提交按鈕"
        }

        print(f"  決策: {decision['action']} - {decision['reason']}")

        # 記錄到歷史
        self.action_history.append({
            "timestamp": datetime.now().isoformat(),
            "decision": decision
        })

        return decision

    def execute_workflow(
        self,
        goal: str,
        max_steps: int = 10
    ) -> List[Dict]:
        """
        執行完整工作流

        Args:
            goal: 工作流目標
            max_steps: 最大步驟數

        Returns:
            執行歷史
        """
        print(f"\n[WebAutomationAgent] 執行工作流")
        print(f"  目標: {goal}")
        print(f"  最大步驟: {max_steps}")
        print("=" * 60)

        workflow_history = []

        for step in range(1, max_steps + 1):
            print(f"\n步驟 {step}:")

            # 模擬當前狀態
            current_state = {
                "url": "https://example.com",
                "title": "示例頁面",
                "available_actions": ["navigate", "click", "type"]
            }

            # 決策
            decision = self.decide_action(goal, current_state)

            # 執行（模擬）
            print(f"  執行: {decision['action']} {decision.get('target', '')}")
            time.sleep(0.5)

            workflow_history.append({
                "step": step,
                "decision": decision,
                "success": True
            })

            # 檢查是否完成
            if self._check_goal_completed(goal, workflow_history):
                print("\n✓ 目標已完成！")
                break

        print("\n" + "=" * 60)
        print(f"工作流完成，共 {len(workflow_history)} 步")
        print("=" * 60 + "\n")

        return workflow_history

    def _check_goal_completed(
        self,
        goal: str,
        history: List[Dict]
    ) -> bool:
        """檢查目標是否完成"""
        # 簡化處理：執行3步後認為完成
        return len(history) >= 3


class ConversationalBrowser:
    """
    對話式瀏覽器

    通過對話方式控制瀏覽器。
    """

    def __init__(self, ai_client: AIClient):
        """
        初始化對話式瀏覽器

        Args:
            ai_client: AI 客戶端
        """
        self.ai_client = ai_client
        self.browser_state = {
            "url": None,
            "title": None,
            "content": None
        }
        print("[ConversationalBrowser] 初始化完成")

    def process_command(self, user_input: str) -> str:
        """
        處理用戶命令

        Args:
            user_input: 用戶輸入

        Returns:
            響應文本
        """
        print(f"\n[ConversationalBrowser] 處理命令: {user_input}")

        # 構建上下文
        context = f"""
        當前瀏覽器狀態：
        - URL: {self.browser_state.get('url', '未訪問任何頁面')}
        - 標題: {self.browser_state.get('title', 'N/A')}

        用戶命令：{user_input}

        請執行用戶的命令，並用自然語言回復結果。
        如果需要導航、點擊或其他操作，請說明你將執行什麼。
        """

        response = self.ai_client.chat(
            message=context,
            system_prompt="""
            你是一個對話式瀏覽器助手。
            你可以：
            1. 導航到網頁
            2. 點擊元素
            3. 填寫表單
            4. 提取信息
            5. 回答關於頁面的問題

            請友好、準確地回應用戶。
            """
        )

        print(f"  響應: {response.content[:100]}...")
        return response.content

    def chat(self, message: str) -> str:
        """
        對話（別名）

        Args:
            message: 用戶消息

        Returns:
            AI 響應
        """
        return self.process_command(message)


def example_intelligent_browsing():
    """示例1: 智能瀏覽"""
    print("\n" + "=" * 60)
    print("示例1: 智能網頁瀏覽")
    print("=" * 60 + "\n")

    # 使用 OpenAI
    ai_client = OpenAIClient(model="gpt-4")
    browser = IntelligentBrowser(ai_client)

    # 導航並分析
    analysis = browser.navigate_and_analyze("https://example.com/news/article-1")

    print("\n分析結果:")
    print(analysis["analysis"])

    # 提取信息
    info = browser.extract_information("這篇文章的主要觀點是什麼？")
    print(f"\n提取的信息: {info}")

    # 獲取建議
    suggestion = browser.suggest_next_action()
    print(f"\n操作建議: {suggestion}")


def example_content_summarization():
    """示例2: 內容摘要"""
    print("\n" + "=" * 60)
    print("示例2: 內容摘要")
    print("=" * 60 + "\n")

    ai_client = ClaudeClient()
    summarizer = ContentSummarizer(ai_client)

    # 模擬長文本
    long_content = """
    人工智能（AI）正在改變我們的世界。從自動駕駛汽車到智能助手，
    AI 技術已經滲透到我們生活的方方面面。機器學習和深度學習的進步
    使得計算機能夠處理複雜的任務，並從數據中學習。然而，AI 的發展
    也帶來了倫理和隱私方面的挑戰。我們需要確保 AI 技術的發展是
    負責任和可持續的。
    """ * 3

    # 生成摘要
    summary = summarizer.summarize(long_content, max_length=100, style="professional")
    print(f"摘要:\n{summary}")

    # 提取關鍵點
    print("\n關鍵點:")
    key_points = summarizer.extract_key_points(long_content, num_points=3)
    for i, point in enumerate(key_points, 1):
        print(f"  {i}. {point}")


def example_automation_agent():
    """示例3: 自動化代理"""
    print("\n" + "=" * 60)
    print("示例3: 智能自動化代理")
    print("=" * 60 + "\n")

    ai_client = OpenAIClient()
    agent = WebAutomationAgent(ai_client)

    # 執行工作流
    goal = "在電商網站上搜索並購買一本書"
    workflow = agent.execute_workflow(goal, max_steps=5)

    # 顯示執行歷史
    print("\n執行歷史:")
    for item in workflow:
        print(f"  步驟 {item['step']}: {item['decision']['action']} - {item['decision']['reason']}")


def example_conversational_browser():
    """示例4: 對話式瀏覽"""
    print("\n" + "=" * 60)
    print("示例4: 對話式瀏覽器")
    print("=" * 60 + "\n")

    ai_client = ClaudeClient()
    conv_browser = ConversationalBrowser(ai_client)

    # 模擬對話
    commands = [
        "請訪問 example.com",
        "這個頁面講的是什麼？",
        "幫我找到登錄按鈕並點擊",
    ]

    for cmd in commands:
        print(f"\n用戶: {cmd}")
        response = conv_browser.chat(cmd)
        print(f"助手: {response}")
        print("-" * 40)


def example_multi_model_comparison():
    """示例5: 多模型對比"""
    print("\n" + "=" * 60)
    print("示例5: 多模型對比")
    print("=" * 60 + "\n")

    # 創建不同的客戶端
    openai_client = OpenAIClient(model="gpt-4")
    claude_client = ClaudeClient(model="claude-3-sonnet-20240229")

    question = "請總結這個網頁的主要內容"

    print("同一問題，不同模型的回答:\n")

    # OpenAI
    print("OpenAI GPT-4:")
    openai_response = openai_client.chat(question)
    print(f"  {openai_response.content}\n")

    # Claude
    print("Claude 3 Sonnet:")
    claude_response = claude_client.chat(question)
    print(f"  {claude_response.content}\n")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Browserbase AI 整合示例")
    print("=" * 60)

    # 運行所有示例
    example_intelligent_browsing()
    example_content_summarization()
    example_automation_agent()
    example_conversational_browser()
    example_multi_model_comparison()

    print("\n" + "=" * 60)
    print("所有示例完成！")
    print("=" * 60 + "\n")

    print("應用場景:")
    print("- 智能網頁分析和摘要")
    print("- 自動化測試和質量保證")
    print("- 內容提取和知識管理")
    print("- 客戶服務自動化")
    print("- 研究和數據收集")


if __name__ == "__main__":
    main()
