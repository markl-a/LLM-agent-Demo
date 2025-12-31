"""
Mastra Agent 創建示例

本示例展示如何創建和配置不同類型的 Agents。

功能：
1. 創建基礎 Agent
2. 配置 Agent 參數
3. 添加系統指令
4. 設置模型選項
5. Agent 管理操作
"""

import os
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()


class MastraAgentBuilder:
    """Mastra Agent 構建器"""

    def __init__(self, api_url: str = None):
        """初始化構建器"""
        self.api_url = api_url or os.getenv('MASTRA_API_URL', 'http://localhost:3000')
        self.api_key = os.getenv('MASTRA_API_KEY')

        self.headers = {
            'Content-Type': 'application/json',
        }
        if self.api_key:
            self.headers['Authorization'] = f'Bearer {self.api_key}'

    def create_agent(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """創建 Agent"""
        try:
            response = requests.post(
                f'{self.api_url}/api/agents',
                headers=self.headers,
                json=config,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def update_agent(self, agent_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """更新 Agent 配置"""
        try:
            response = requests.put(
                f'{self.api_url}/api/agents/{agent_name}',
                headers=self.headers,
                json=config,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def delete_agent(self, agent_name: str) -> Dict[str, Any]:
        """刪除 Agent"""
        try:
            response = requests.delete(
                f'{self.api_url}/api/agents/{agent_name}',
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}


def example_1_basic_agent():
    """示例 1：創建基礎 Agent"""
    print("=" * 60)
    print("示例 1：創建基礎 Agent")
    print("=" * 60)

    builder = MastraAgentBuilder()

    # 最簡單的 Agent 配置
    config = {
        'name': 'basic-agent',
        'description': '基礎助手',
        'model': {
            'provider': 'openai',
            'name': 'gpt-4',
        },
        'instructions': '你是一個有幫助的助手。',
    }

    result = builder.create_agent(config)
    print(f"\n創建結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def example_2_customer_service_agent():
    """示例 2：客戶服務 Agent"""
    print("\n" + "=" * 60)
    print("示例 2：客戶服務 Agent")
    print("=" * 60)

    builder = MastraAgentBuilder()

    config = {
        'name': 'customer-service-agent',
        'description': '專業的客戶服務助手',
        'model': {
            'provider': 'openai',
            'name': 'gpt-4',
            'temperature': 0.7,
            'max_tokens': 1000,
        },
        'instructions': '''你是一個專業的客戶服務代表。

        核心職責：
        1. 友好且專業地回應客戶查詢
        2. 快速識別客戶需求
        3. 提供準確的產品信息
        4. 處理投訴時保持同理心
        5. 在必要時升級問題

        回應準則：
        - 始終保持禮貌和尊重
        - 使用清晰簡潔的語言
        - 提供具體的解決方案
        - 確認客戶理解
        - 結束前詢問是否還有其他問題

        語氣：專業、友好、有耐心
        ''',
        'tools': [],
        'metadata': {
            'department': 'customer-service',
            'priority': 'high',
            'version': '1.0',
        }
    }

    result = builder.create_agent(config)
    print(f"\n創建結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def example_3_technical_support_agent():
    """示例 3：技術支持 Agent"""
    print("\n" + "=" * 60)
    print("示例 3：技術支持 Agent")
    print("=" * 60)

    builder = MastraAgentBuilder()

    config = {
        'name': 'tech-support-agent',
        'description': '技術支持專家',
        'model': {
            'provider': 'openai',
            'name': 'gpt-4',
            'temperature': 0.3,  # 較低溫度以確保準確性
        },
        'instructions': '''你是一個專業的技術支持工程師。

        專業領域：
        - 軟體安裝和配置
        - 故障排除和診斷
        - 系統優化建議
        - 安全最佳實踐

        工作流程：
        1. 收集問題詳細信息
        2. 詢問相關的系統配置
        3. 提供逐步解決方案
        4. 驗證問題是否解決
        5. 提供預防措施

        回應風格：
        - 技術準確
        - 步驟明確
        - 提供原因解釋
        - 包含截圖或代碼示例
        ''',
        'tools': ['search_knowledge_base', 'create_ticket', 'escalate_issue'],
    }

    result = builder.create_agent(config)
    print(f"\n創建結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def example_4_sales_agent():
    """示例 4：銷售 Agent"""
    print("\n" + "=" * 60)
    print("示例 4：銷售 Agent")
    print("=" * 60)

    builder = MastraAgentBuilder()

    config = {
        'name': 'sales-agent',
        'description': '智能銷售助手',
        'model': {
            'provider': 'openai',
            'name': 'gpt-4',
            'temperature': 0.8,  # 較高溫度以保持創意
        },
        'instructions': '''你是一個專業的銷售顧問。

        銷售策略：
        1. 建立信任和關係
        2. 了解客戶需求（SPIN 提問法）
        3. 展示產品價值
        4. 處理異議
        5. 推動成交

        SPIN 提問法：
        - Situation（情況）：了解客戶現狀
        - Problem（問題）：發現痛點
        - Implication（影響）：放大問題影響
        - Need-payoff（價值）：展示解決方案價值

        銷售準則：
        - 傾聽多於說話
        - 提供個性化建議
        - 不強迫推銷
        - 專注於解決方案而非功能
        - 建立長期關係
        ''',
        'tools': ['get_product_info', 'check_inventory', 'calculate_discount', 'create_quote'],
        'metadata': {
            'team': 'sales',
            'quota_target': '100k',
        }
    }

    result = builder.create_agent(config)
    print(f"\n創建結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def example_5_content_writer_agent():
    """示例 5：內容寫作 Agent"""
    print("\n" + "=" * 60)
    print("示例 5：內容寫作 Agent")
    print("=" * 60)

    builder = MastraAgentBuilder()

    config = {
        'name': 'content-writer-agent',
        'description': '專業內容創作者',
        'model': {
            'provider': 'openai',
            'name': 'gpt-4',
            'temperature': 0.9,  # 高溫度以激發創意
            'max_tokens': 2000,
        },
        'instructions': '''你是一個專業的內容創作者和文案撰寫人。

        寫作能力：
        1. 博客文章
        2. 社交媒體內容
        3. 產品描述
        4. 新聞稿
        5. SEO 優化內容

        寫作原則：
        - 吸引人的標題
        - 清晰的結構（引言、主體、結論）
        - 使用生動的語言
        - 包含具體例子
        - 優化關鍵詞（SEO）

        語氣選項：
        - 正式/非正式
        - 專業/輕鬆
        - 教育/娛樂
        - 說服/告知

        請根據要求調整語氣和風格。
        ''',
        'tools': ['check_grammar', 'seo_analysis', 'plagiarism_check'],
    }

    result = builder.create_agent(config)
    print(f"\n創建結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def example_6_data_analyst_agent():
    """示例 6：數據分析 Agent"""
    print("\n" + "=" * 60)
    print("示例 6：數據分析 Agent")
    print("=" * 60)

    builder = MastraAgentBuilder()

    config = {
        'name': 'data-analyst-agent',
        'description': '數據分析專家',
        'model': {
            'provider': 'openai',
            'name': 'gpt-4',
            'temperature': 0.2,  # 低溫度確保精確性
        },
        'instructions': '''你是一個專業的數據分析師。

        分析能力：
        1. 描述性統計分析
        2. 趨勢識別
        3. 相關性分析
        4. 預測性見解
        5. 數據可視化建議

        分析流程：
        1. 理解業務問題
        2. 檢查數據質量
        3. 執行適當的分析
        4. 解釋結果
        5. 提供可行建議

        輸出格式：
        - 執行摘要
        - 關鍵發現
        - 數據可視化
        - 統計顯著性
        - 建議行動

        使用清晰的語言解釋技術概念。
        ''',
        'tools': ['query_database', 'generate_chart', 'calculate_stats'],
    }

    result = builder.create_agent(config)
    print(f"\n創建結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def example_7_multilingual_agent():
    """示例 7：多語言支持 Agent"""
    print("\n" + "=" * 60)
    print("示例 7：多語言支持 Agent")
    print("=" * 60)

    builder = MastraAgentBuilder()

    config = {
        'name': 'multilingual-agent',
        'description': '多語言客服助手',
        'model': {
            'provider': 'openai',
            'name': 'gpt-4',
            'temperature': 0.7,
        },
        'instructions': '''你是一個多語言客戶服務助手。

        支持語言：
        - 繁體中文
        - 簡體中文
        - English
        - 日本語
        - 한국어

        能力：
        1. 自動檢測用戶語言
        2. 使用相同語言回應
        3. 翻譯支持
        4. 文化敏感度

        回應準則：
        - 使用用戶的語言
        - 保持專業術語準確
        - 尊重文化差異
        - 在必要時提供翻譯

        對於不確定的翻譯，請詢問用戶偏好。
        ''',
        'tools': ['translate', 'detect_language'],
        'metadata': {
            'supported_languages': ['zh-TW', 'zh-CN', 'en', 'ja', 'ko'],
        }
    }

    result = builder.create_agent(config)
    print(f"\n創建結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def example_8_update_agent():
    """示例 8：更新 Agent 配置"""
    print("\n" + "=" * 60)
    print("示例 8：更新 Agent 配置")
    print("=" * 60)

    builder = MastraAgentBuilder()

    # 更新 Agent 的指令和溫度
    update_config = {
        'model': {
            'temperature': 0.5,  # 調整溫度
        },
        'instructions': '''你是一個更新後的助手。

        新增功能：
        - 更詳細的回應
        - 提供代碼示例
        - 包含最佳實踐建議
        ''',
    }

    result = builder.update_agent('basic-agent', update_config)
    print(f"\n更新結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def example_9_agent_with_constraints():
    """示例 9：帶約束的 Agent"""
    print("\n" + "=" * 60)
    print("示例 9：帶約束的 Agent")
    print("=" * 60)

    builder = MastraAgentBuilder()

    config = {
        'name': 'constrained-agent',
        'description': '帶有使用約束的助手',
        'model': {
            'provider': 'openai',
            'name': 'gpt-4',
            'temperature': 0.7,
            'max_tokens': 500,  # 限制回應長度
        },
        'instructions': '''你是一個簡潔的助手。

        約束條件：
        - 每個回應不超過 3 段
        - 使用要點格式
        - 避免冗長解釋
        - 直接回答問題

        禁止：
        - 提供法律或醫療建議
        - 生成有害內容
        - 分享個人信息
        - 執行金融交易
        ''',
        'metadata': {
            'max_response_length': 500,
            'rate_limit': '100/hour',
            'content_filter': 'strict',
        }
    }

    result = builder.create_agent(config)
    print(f"\n創建結果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def example_10_agent_management():
    """示例 10：Agent 管理操作"""
    print("\n" + "=" * 60)
    print("示例 10：Agent 管理操作")
    print("=" * 60)

    builder = MastraAgentBuilder()

    print("\n1. 列出所有 Agents:")
    try:
        response = requests.get(
            f'{builder.api_url}/api/agents',
            headers=builder.headers,
            timeout=10
        )
        agents = response.json()
        print(json.dumps(agents, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"錯誤: {e}")

    print("\n2. 刪除測試 Agent:")
    result = builder.delete_agent('basic-agent')
    print(json.dumps(result, indent=2, ensure_ascii=False))

    print("\n3. Agent 創建最佳實踐:")
    print("""
    ✅ 最佳實踐：

    1. 命名規範：
       - 使用小寫和連字符
       - 描述性名稱
       - 避免特殊字符

    2. 指令設計：
       - 清晰明確
       - 包含角色定義
       - 列出具體任務
       - 設置邊界

    3. 溫度設置：
       - 0.0-0.3: 事實性任務（技術支持、數據分析）
       - 0.4-0.7: 平衡任務（客服、教育）
       - 0.8-1.0: 創意任務（寫作、頭腦風暴）

    4. Token 限制：
       - 短回應：256-512
       - 中等回應：512-1024
       - 長回應：1024-2048

    5. 測試和迭代：
       - 多次測試不同場景
       - 收集用戶反饋
       - 持續優化指令
    """)


def main():
    """主函數"""
    print("\n🤖 Mastra Agent 創建示例\n")

    try:
        # 運行所有示例
        example_1_basic_agent()
        example_2_customer_service_agent()
        example_3_technical_support_agent()
        example_4_sales_agent()
        example_5_content_writer_agent()
        example_6_data_analyst_agent()
        example_7_multilingual_agent()
        example_8_update_agent()
        example_9_agent_with_constraints()
        example_10_agent_management()

        print("\n" + "=" * 60)
        print("✅ 所有示例運行完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")


if __name__ == "__main__":
    main()
