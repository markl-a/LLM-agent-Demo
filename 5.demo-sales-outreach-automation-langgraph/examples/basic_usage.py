#!/usr/bin/env python3
"""
基礎使用示例
============

這個示例展示如何使用銷售外展自動化系統的基本功能：
1. 初始化系統組件
2. 從 CRM 讀取潛在客戶
3. 生成個性化郵件
4. 發送郵件並更新狀態

運行前請確保：
- 已配置 .env 文件
- 已設置 credentials.json
- CRM 中有 status='pending' 的客戶

運行方式：
    python examples/basic_usage.py
"""

import os
import sys
from dotenv import load_dotenv

# 添加專案根目錄到路徑（如果需要導入專案模組）
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'sales-outreach-automation-langgraph'))

# 加載環境變數
load_dotenv()


class SimpleSalesAutomation:
    """簡化的銷售自動化系統示例"""

    def __init__(self):
        """初始化系統組件"""
        print("🚀 初始化銷售自動化系統...")

        # 檢查必要的環境變數
        self.check_environment()

        # 初始化各個組件
        self.init_llm()
        self.init_crm()
        self.init_email_service()

        print("✅ 系統初始化完成\n")

    def check_environment(self):
        """檢查環境變數配置"""
        required_vars = [
            'GEMINI_API_KEY',  # 或 OPENAI_API_KEY
        ]

        optional_vars = [
            'AIRTABLE_ACCESS_TOKEN',
            'SERPER_API_KEY',
            'RAPIDAPI_KEY',
        ]

        print("檢查環境變數配置...")

        # 檢查必需變數
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            print(f"❌ 缺少必要的環境變數: {', '.join(missing_vars)}")
            print("請在 .env 文件中配置這些變數")
            sys.exit(1)

        # 檢查可選變數
        for var in optional_vars:
            if os.getenv(var):
                print(f"  ✓ {var}: 已配置")
            else:
                print(f"  ⚠ {var}: 未配置（某些功能可能不可用）")

    def init_llm(self):
        """初始化 LLM"""
        print("\n初始化 LLM...")

        # 這裡應該導入和初始化實際的 LLM 客戶端
        # 例如：
        # from langchain_google_genai import ChatGoogleGenerativeAI
        # self.llm = ChatGoogleGenerativeAI(model="gemini-pro")

        # 示例中使用模擬
        print("  ✓ LLM 初始化成功（使用 Gemini）")

    def init_crm(self):
        """初始化 CRM 連接"""
        print("初始化 CRM 連接...")

        # 這裡應該導入和初始化實際的 CRM 客戶端
        # 例如（Airtable）：
        # from pyairtable import Api
        # self.crm = Api(os.getenv('AIRTABLE_ACCESS_TOKEN'))

        # 示例中使用模擬
        print("  ✓ CRM 連接成功")

    def init_email_service(self):
        """初始化郵件服務"""
        print("初始化郵件服務...")

        # 這裡應該初始化 Gmail API
        # from google.oauth2.credentials import Credentials
        # from googleapiclient.discovery import build

        # 示例中使用模擬
        print("  ✓ 郵件服務初始化成功")

    def get_pending_leads(self):
        """
        從 CRM 獲取待處理的潛在客戶

        Returns:
            list: 潛在客戶列表
        """
        print("📋 從 CRM 獲取待處理客戶...")

        # 實際實現應該從 CRM 讀取
        # 例如（Airtable）：
        # table = self.crm.table(base_id, table_name)
        # records = table.all(formula="status='pending'")

        # 示例數據
        mock_leads = [
            {
                'id': '1',
                'name': 'John Doe',
                'email': 'john@example.com',
                'company': 'TechCorp',
                'position': 'CTO',
                'linkedin_url': 'https://linkedin.com/in/johndoe',
            },
            {
                'id': '2',
                'name': 'Jane Smith',
                'email': 'jane@startup.io',
                'company': 'Startup Inc',
                'position': 'CEO',
                'linkedin_url': 'https://linkedin.com/in/janesmith',
            },
        ]

        print(f"  ✓ 找到 {len(mock_leads)} 個待處理客戶\n")
        return mock_leads

    def research_lead(self, lead):
        """
        研究潛在客戶

        Args:
            lead: 客戶信息字典

        Returns:
            dict: 研究數據
        """
        print(f"🔍 研究客戶: {lead['name']} ({lead['company']})...")

        # 實際實現應該：
        # 1. 使用 LinkedIn API 獲取檔案
        # 2. 使用 Serper 搜索公司信息
        # 3. 分析行業趨勢

        # 示例數據
        research_data = {
            'company_description': f"{lead['company']} 是一家科技公司",
            'recent_news': f"{lead['company']} 最近發布了新產品",
            'linkedin_summary': f"{lead['name']} 在 {lead['company']} 擔任 {lead['position']}",
        }

        print(f"  ✓ 研究完成\n")
        return research_data

    def generate_email(self, lead, research_data):
        """
        生成個性化郵件

        Args:
            lead: 客戶信息
            research_data: 研究數據

        Returns:
            str: 郵件內容
        """
        print(f"✍️  為 {lead['name']} 生成個性化郵件...")

        # 實際實現應該使用 LLM
        # prompt = build_email_prompt(lead, research_data)
        # email = self.llm.invoke(prompt)

        # 示例郵件
        email_content = f"""
嗨 {lead['name']}，

我注意到 {lead['company']} 最近的發展非常令人印象深刻。
特別是您在 {lead['position']} 這個職位上的工作。

我想和您分享一個可能對 {lead['company']} 有幫助的解決方案。
我們的產品已經幫助類似的公司提升了 40% 的效率。

如果方便的話，我們可以安排一個 15 分鐘的通話，
討論如何幫助 {lead['company']} 達成目標。

期待您的回覆。

最好的祝福，
銷售團隊
        """.strip()

        print(f"  ✓ 郵件生成完成\n")
        print("=" * 50)
        print(email_content)
        print("=" * 50 + "\n")

        return email_content

    def send_email(self, lead, email_content):
        """
        發送郵件

        Args:
            lead: 客戶信息
            email_content: 郵件內容

        Returns:
            bool: 是否成功
        """
        print(f"📧 發送郵件給 {lead['email']}...")

        try:
            # 實際實現應該使用 Gmail API
            # message = create_message(to=lead['email'], subject="...", body=email_content)
            # service.users().messages().send(userId='me', body=message).execute()

            # 示例中模擬成功
            print(f"  ✓ 郵件發送成功\n")
            return True

        except Exception as e:
            print(f"  ✗ 郵件發送失敗: {e}\n")
            return False

    def update_crm_status(self, lead_id, status, notes=None):
        """
        更新 CRM 中的客戶狀態

        Args:
            lead_id: 客戶 ID
            status: 新狀態（sent, failed 等）
            notes: 備註信息
        """
        print(f"💾 更新 CRM 狀態為: {status}...")

        # 實際實現應該更新 CRM
        # table.update(lead_id, {'status': status, 'notes': notes})

        print(f"  ✓ CRM 更新完成\n")

    def process_lead(self, lead):
        """
        處理單個潛在客戶

        Args:
            lead: 客戶信息

        Returns:
            bool: 是否成功
        """
        print("=" * 70)
        print(f"處理客戶 {lead['name']}")
        print("=" * 70 + "\n")

        try:
            # 1. 研究客戶
            research_data = self.research_lead(lead)

            # 2. 生成郵件
            email_content = self.generate_email(lead, research_data)

            # 3. 發送郵件
            success = self.send_email(lead, email_content)

            # 4. 更新 CRM
            if success:
                self.update_crm_status(
                    lead['id'],
                    status='sent',
                    notes=f"郵件已於 {os.popen('date').read().strip()} 發送"
                )
            else:
                self.update_crm_status(
                    lead['id'],
                    status='failed',
                    notes="郵件發送失敗"
                )

            return success

        except Exception as e:
            print(f"❌ 處理失敗: {e}\n")
            self.update_crm_status(
                lead['id'],
                status='failed',
                notes=f"錯誤: {str(e)}"
            )
            return False

    def run(self):
        """運行主流程"""
        print("\n" + "=" * 70)
        print("開始銷售外展自動化流程")
        print("=" * 70 + "\n")

        # 1. 獲取待處理客戶
        leads = self.get_pending_leads()

        if not leads:
            print("沒有待處理的客戶")
            return

        # 2. 處理每個客戶
        results = {
            'success': 0,
            'failed': 0,
        }

        for lead in leads:
            success = self.process_lead(lead)
            if success:
                results['success'] += 1
            else:
                results['failed'] += 1

        # 3. 顯示總結
        print("\n" + "=" * 70)
        print("處理完成")
        print("=" * 70)
        print(f"總計: {len(leads)} 個客戶")
        print(f"成功: {results['success']}")
        print(f"失敗: {results['failed']}")
        print(f"成功率: {results['success']/len(leads)*100:.1f}%")
        print("=" * 70 + "\n")


def main():
    """主函數"""

    # 創建自動化系統實例
    automation = SimpleSalesAutomation()

    # 運行流程
    automation.run()


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
