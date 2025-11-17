#!/usr/bin/env python3
"""
自定義 Agent 示例
=================

這個示例展示如何創建和整合自定義的 Agent 到 LangGraph 工作流中。

場景：添加一個「質量檢查 Agent」來驗證生成的郵件是否符合要求。

運行方式：
    python examples/custom_agent.py
"""

import os
import sys
from typing import TypedDict, Annotated
from dotenv import load_dotenv

# 加載環境變數
load_dotenv()


# ===== 狀態定義 =====

class AgentState(TypedDict):
    """Agent 工作流的狀態"""
    lead_name: str
    lead_email: str
    company: str
    email_content: str
    quality_score: float
    quality_issues: list[str]
    approved: bool
    retry_count: int


# ===== 自定義 Agent =====

class EmailQualityChecker:
    """
    郵件質量檢查 Agent

    檢查生成的郵件是否符合最佳實踐：
    - 長度適中（150-250 字）
    - 包含個性化元素
    - 沒有垃圾郵件指標
    - 有明確的 CTA
    """

    def __init__(self):
        self.min_length = 150
        self.max_length = 250
        self.spam_keywords = [
            '!!!', '100% FREE', 'CLICK HERE', 'LIMITED TIME',
            '立即購買', '限時優惠', '馬上行動'
        ]

    def check_length(self, email: str) -> tuple[bool, str]:
        """檢查郵件長度"""
        length = len(email)

        if length < self.min_length:
            return False, f"郵件太短（{length} 字，建議至少 {self.min_length} 字）"
        elif length > self.max_length:
            return False, f"郵件太長（{length} 字，建議不超過 {self.max_length} 字）"

        return True, ""

    def check_personalization(self, email: str, lead_name: str, company: str) -> tuple[bool, str]:
        """檢查個性化程度"""
        issues = []

        # 檢查是否包含收件人姓名
        if lead_name not in email:
            issues.append("缺少收件人姓名")

        # 檢查是否提及公司
        if company not in email:
            issues.append("未提及公司名稱")

        if issues:
            return False, "; ".join(issues)

        return True, ""

    def check_spam_indicators(self, email: str) -> tuple[bool, str]:
        """檢查垃圾郵件指標"""
        found_spam = []

        email_upper = email.upper()
        for keyword in self.spam_keywords:
            if keyword in email_upper:
                found_spam.append(keyword)

        if found_spam:
            return False, f"包含垃圾郵件關鍵詞: {', '.join(found_spam)}"

        # 檢查大寫字母比例
        uppercase_count = sum(1 for c in email if c.isupper())
        if uppercase_count / len(email) > 0.3:
            return False, "大寫字母比例過高"

        return True, ""

    def check_cta(self, email: str) -> tuple[bool, str]:
        """檢查是否有明確的行動呼籲"""
        cta_indicators = [
            '通話', '會議', '討論', '回覆', '聯繫',
            'call', 'meeting', 'discuss', 'reply', 'contact'
        ]

        has_cta = any(indicator in email.lower() for indicator in cta_indicators)

        if not has_cta:
            return False, "缺少明確的行動呼籲（CTA）"

        return True, ""

    def evaluate(self, email: str, lead_name: str, company: str) -> tuple[float, list[str]]:
        """
        評估郵件質量

        Returns:
            (quality_score, issues):質量分數（0-100）和問題列表
        """
        checks = [
            self.check_length(email),
            self.check_personalization(email, lead_name, company),
            self.check_spam_indicators(email),
            self.check_cta(email),
        ]

        # 計算分數
        passed = sum(1 for passed, _ in checks if passed)
        score = (passed / len(checks)) * 100

        # 收集問題
        issues = [issue for passed, issue in checks if not passed]

        return score, issues


class SentimentAnalyzer:
    """
    情感分析 Agent

    分析郵件的語氣是否合適
    """

    def analyze(self, email: str) -> str:
        """
        分析郵件語氣

        Returns:
            sentiment: 'positive', 'neutral', 'negative'
        """
        # 這裡應該使用實際的情感分析模型
        # 例如：transformers, TextBlob, 或 LLM

        # 簡單示例：基於關鍵詞
        positive_keywords = ['恭喜', '很高興', '期待', '感謝']
        negative_keywords = ['抱歉', '遺憾', '問題', '困難']

        email_lower = email.lower()

        pos_count = sum(1 for kw in positive_keywords if kw in email_lower)
        neg_count = sum(1 for kw in negative_keywords if kw in email_lower)

        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        else:
            return 'neutral'


# ===== 節點函數 =====

def generate_email_node(state: AgentState) -> AgentState:
    """生成郵件節點（模擬）"""
    print(f"\n📝 為 {state['lead_name']} 生成郵件...")

    # 模擬生成的郵件
    email = f"""
嗨 {state['lead_name']}，

我注意到 {state['company']} 最近在行業內的發展。

我們的解決方案可以幫助您提升效率。

如果有興趣，歡迎安排一個簡短的通話討論。

謝謝，
銷售團隊
    """.strip()

    state['email_content'] = email
    state['retry_count'] = state.get('retry_count', 0)

    print("✅ 郵件已生成")
    return state


def quality_check_node(state: AgentState) -> AgentState:
    """質量檢查節點（自定義 Agent）"""
    print("\n🔍 執行質量檢查...")

    checker = EmailQualityChecker()
    analyzer = SentimentAnalyzer()

    # 1. 質量評估
    score, issues = checker.evaluate(
        state['email_content'],
        state['lead_name'],
        state['company']
    )

    state['quality_score'] = score
    state['quality_issues'] = issues

    # 2. 情感分析
    sentiment = analyzer.analyze(state['email_content'])

    print(f"  質量分數: {score:.1f}/100")
    print(f"  語氣: {sentiment}")

    if issues:
        print("  發現問題:")
        for issue in issues:
            print(f"    - {issue}")

    # 3. 決定是否通過
    # 分數 >= 75 且語氣不是負面
    approved = score >= 75 and sentiment != 'negative'
    state['approved'] = approved

    if approved:
        print("✅ 質量檢查通過")
    else:
        print("❌ 質量檢查未通過")

    return state


def regenerate_email_node(state: AgentState) -> AgentState:
    """重新生成郵件節點"""
    print("\n🔄 根據反饋重新生成郵件...")

    state['retry_count'] += 1

    # 這裡應該根據 quality_issues 調整 prompt 重新生成
    # 例如：
    # prompt = build_improved_prompt(state['quality_issues'])
    # email = llm.invoke(prompt)

    # 示例：改進的郵件
    improved_email = f"""
嗨 {state['lead_name']}，

恭喜 {state['company']} 最近發布的新產品！我特別關注到你們在創新方面的努力。

作為 {state['company']} 的領導者，您可能對我們的解決方案感興趣。
我們已經幫助類似規模的公司提升了 40% 的效率。

我們可以安排一個 15 分鐘的通話，討論如何幫助 {state['company']} 達成目標嗎？

期待您的回覆。

最好的祝福，
Mark Chen
    """.strip()

    state['email_content'] = improved_email

    print("✅ 郵件已重新生成")
    return state


def send_email_node(state: AgentState) -> AgentState:
    """發送郵件節點"""
    print(f"\n📧 發送郵件給 {state['lead_email']}...")
    print("\n" + "=" * 60)
    print(state['email_content'])
    print("=" * 60 + "\n")
    print("✅ 郵件已發送")
    return state


# ===== 條件路由 =====

def should_regenerate(state: AgentState) -> str:
    """決定是否需要重新生成郵件"""

    # 如果通過質量檢查，直接發送
    if state['approved']:
        return "send"

    # 如果重試次數過多，仍然發送（或者選擇跳過）
    if state['retry_count'] >= 2:
        print("⚠️  已達到最大重試次數，強制發送")
        return "send"

    # 否則重新生成
    return "regenerate"


# ===== 主流程 =====

def create_workflow():
    """
    創建包含自定義 Agent 的工作流

    工作流程：
    生成郵件 → 質量檢查 → [通過] → 發送
                         ↓ [未通過]
                      重新生成 → 質量檢查 → ...
    """
    # 這裡應該使用 LangGraph 構建實際的圖
    # 示例中用函數調用模擬

    def workflow(lead_name: str, lead_email: str, company: str):
        """執行工作流"""

        print("=" * 70)
        print(f"處理客戶: {lead_name} ({company})")
        print("=" * 70)

        # 初始化狀態
        state: AgentState = {
            'lead_name': lead_name,
            'lead_email': lead_email,
            'company': company,
            'email_content': '',
            'quality_score': 0.0,
            'quality_issues': [],
            'approved': False,
            'retry_count': 0,
        }

        # 第一次生成
        state = generate_email_node(state)
        state = quality_check_node(state)

        # 循環直到通過或達到最大重試次數
        while not state['approved'] and state['retry_count'] < 2:
            state = regenerate_email_node(state)
            state = quality_check_node(state)

        # 發送郵件
        state = send_email_node(state)

        return state

    return workflow


def main():
    """主函數"""

    print("\n" + "=" * 70)
    print("自定義 Agent 示例 - 郵件質量檢查工作流")
    print("=" * 70 + "\n")

    # 創建工作流
    workflow = create_workflow()

    # 測試數據
    test_leads = [
        {
            'name': 'Alice Wang',
            'email': 'alice@techcorp.com',
            'company': 'TechCorp',
        },
        {
            'name': 'Bob Lee',
            'email': 'bob@startup.io',
            'company': 'Startup Inc',
        },
    ]

    # 處理每個客戶
    for lead in test_leads:
        workflow(
            lead_name=lead['name'],
            lead_email=lead['email'],
            company=lead['company']
        )
        print("\n")

    print("=" * 70)
    print("所有客戶處理完成")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  程式被用戶中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
