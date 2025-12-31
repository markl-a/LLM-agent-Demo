"""
Mastra 記憶管理示例

本示例展示如何管理 Agent 的記憶和上下文。

功能：
1. 短期記憶（會話內）
2. 長期記憶（跨會話）
3. 向量記憶（語義搜索）
4. 記憶檢索和更新
5. 記憶壓縮和清理
"""

import os
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta
import hashlib

load_dotenv()


class MastraMemoryManager:
    """Mastra 記憶管理器"""

    def __init__(self, api_url: str = None):
        """初始化記憶管理器"""
        self.api_url = api_url or os.getenv('MASTRA_API_URL', 'http://localhost:3000')
        self.api_key = os.getenv('MASTRA_API_KEY')

        self.headers = {
            'Content-Type': 'application/json',
        }
        if self.api_key:
            self.headers['Authorization'] = f'Bearer {self.api_key}'

    def create_memory(self, memory_config: Dict[str, Any]) -> Dict[str, Any]:
        """創建記憶存儲"""
        try:
            response = requests.post(
                f'{self.api_url}/api/memory',
                headers=self.headers,
                json=memory_config,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def save_memory(self, session_id: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """保存記憶"""
        try:
            response = requests.post(
                f'{self.api_url}/api/memory/{session_id}',
                headers=self.headers,
                json=content,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def get_memory(self, session_id: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """獲取記憶"""
        try:
            params = filters or {}
            response = requests.get(
                f'{self.api_url}/api/memory/{session_id}',
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def search_memory(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """語義搜索記憶"""
        try:
            response = requests.post(
                f'{self.api_url}/api/memory/search',
                headers=self.headers,
                json={'query': query, 'limit': limit},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}


def example_1_short_term_memory():
    """示例 1：短期記憶（會話記憶）"""
    print("=" * 60)
    print("示例 1：短期記憶 - 對話上下文")
    print("=" * 60)

    memory_manager = MastraMemoryManager()

    # 配置短期記憶
    config = {
        'type': 'short_term',
        'name': 'conversation-memory',
        'description': '對話上下文記憶',
        'config': {
            'maxMessages': 20,  # 最多保留 20 條消息
            'ttl': 3600,  # 1 小時後過期
            'storage': 'memory',  # 存儲在內存中
            'compression': {
                'enabled': true,
                'threshold': 10,  # 超過 10 條消息時壓縮
                'method': 'summary'  # 使用摘要壓縮
            }
        }
    }

    result = memory_manager.create_memory(config)
    print(f"\n記憶配置: {json.dumps(result, indent=2, ensure_ascii=False)}")

    # 模擬對話並保存記憶
    session_id = "session-12345"
    conversation = [
        {"role": "user", "content": "我叫張三"},
        {"role": "assistant", "content": "你好，張三！很高興認識你。"},
        {"role": "user", "content": "我住在台北"},
        {"role": "assistant", "content": "台北是個很棒的城市！"},
        {"role": "user", "content": "你還記得我的名字嗎？"},
    ]

    for msg in conversation:
        memory_manager.save_memory(session_id, {
            'type': 'message',
            'data': msg,
            'timestamp': datetime.now().isoformat()
        })
        print(f"\n{msg['role']}: {msg['content']}")

    # 獲取記憶
    print("\n獲取會話記憶:")
    memories = memory_manager.get_memory(session_id)
    print(json.dumps(memories, indent=2, ensure_ascii=False))


def example_2_long_term_memory():
    """示例 2：長期記憶（持久化）"""
    print("\n" + "=" * 60)
    print("示例 2：長期記憶 - 用戶偏好和事實")
    print("=" * 60)

    memory_manager = MastraMemoryManager()

    # 配置長期記憶
    config = {
        'type': 'long_term',
        'name': 'user-knowledge',
        'description': '用戶知識庫',
        'config': {
            'storage': 'database',  # 持久化到數據庫
            'ttl': None,  # 永不過期
            'categories': [
                'personal_info',
                'preferences',
                'history',
                'relationships'
            ],
            'indexing': {
                'enabled': true,
                'fields': ['category', 'userId', 'timestamp']
            }
        }
    }

    result = memory_manager.create_memory(config)
    print(f"\n記憶配置: {json.dumps(result, indent=2, ensure_ascii=False)}")

    # 保存長期記憶
    user_id = "user-001"
    long_term_facts = [
        {
            'category': 'personal_info',
            'key': 'name',
            'value': '張三',
            'confidence': 1.0
        },
        {
            'category': 'personal_info',
            'key': 'location',
            'value': '台北',
            'confidence': 1.0
        },
        {
            'category': 'preferences',
            'key': 'communication_style',
            'value': '簡潔明了',
            'confidence': 0.8
        },
        {
            'category': 'preferences',
            'key': 'language',
            'value': '繁體中文',
            'confidence': 1.0
        },
        {
            'category': 'history',
            'key': 'last_topic',
            'value': '產品詢問',
            'timestamp': datetime.now().isoformat()
        }
    ]

    for fact in long_term_facts:
        memory_manager.save_memory(user_id, {
            'type': 'fact',
            'data': fact
        })
        print(f"\n保存: {fact['category']} - {fact['key']}: {fact['value']}")


def example_3_vector_memory():
    """示例 3：向量記憶（語義搜索）"""
    print("\n" + "=" * 60)
    print("示例 3：向量記憶 - 語義搜索")
    print("=" * 60)

    memory_manager = MastraMemoryManager()

    # 配置向量記憶
    config = {
        'type': 'vector',
        'name': 'semantic-memory',
        'description': '語義記憶存儲',
        'config': {
            'vectorStore': {
                'provider': 'pinecone',
                'index': 'mastra-memory',
                'dimension': 1536,  # OpenAI embeddings
                'metric': 'cosine'
            },
            'embedding': {
                'provider': 'openai',
                'model': 'text-embedding-3-large'
            },
            'chunking': {
                'size': 500,
                'overlap': 50
            },
            'retrieval': {
                'topK': 5,
                'minScore': 0.7
            }
        }
    }

    result = memory_manager.create_memory(config)
    print(f"\n記憶配置: {json.dumps(result, indent=2, ensure_ascii=False)}")

    # 保存向量記憶
    documents = [
        {
            'content': '張三是一位軟體工程師，專長是 Python 和機器學習',
            'metadata': {
                'category': 'professional',
                'userId': 'user-001'
            }
        },
        {
            'content': '張三喜歡在週末爬山和閱讀技術書籍',
            'metadata': {
                'category': 'hobbies',
                'userId': 'user-001'
            }
        },
        {
            'content': '張三上個月參加了一個 AI 研討會，對 LLM 很感興趣',
            'metadata': {
                'category': 'events',
                'userId': 'user-001'
            }
        }
    ]

    for doc in documents:
        memory_manager.save_memory('vector-store', {
            'type': 'document',
            'data': doc
        })
        print(f"\n保存文檔: {doc['content'][:50]}...")

    # 語義搜索
    print("\n執行語義搜索:")
    queries = [
        "張三的職業是什麼？",
        "張三的興趣愛好",
        "張三最近的活動"
    ]

    for query in queries:
        print(f"\n查詢: {query}")
        results = memory_manager.search_memory(query, limit=3)
        if 'results' in results:
            for i, result in enumerate(results['results'], 1):
                print(f"  {i}. {result.get('content', '')} (相似度: {result.get('score', 0):.2f})")


def example_4_memory_retrieval():
    """示例 4：智能記憶檢索"""
    print("\n" + "=" * 60)
    print("示例 4：智能記憶檢索")
    print("=" * 60)

    # 記憶檢索策略配置
    retrieval_config = {
        'strategies': [
            {
                'name': 'recency',
                'description': '最近訪問的記憶',
                'weight': 0.3,
                'config': {
                    'timeWindow': '7d',  # 最近 7 天
                    'limit': 10
                }
            },
            {
                'name': 'frequency',
                'description': '經常訪問的記憶',
                'weight': 0.2,
                'config': {
                    'minAccessCount': 3,
                    'limit': 10
                }
            },
            {
                'name': 'relevance',
                'description': '語義相關的記憶',
                'weight': 0.5,
                'config': {
                    'minScore': 0.7,
                    'limit': 10
                }
            }
        ],
        'combination': 'weighted',  # 加權組合
        'deduplication': true,  # 去重
        'maxResults': 10
    }

    print(f"\n檢索策略: {json.dumps(retrieval_config, indent=2, ensure_ascii=False)}")

    # 模擬檢索
    print("\n檢索示例:")
    print("""
    查詢: "張三的技術背景"

    檢索過程:
    1. 最近記憶 (權重 0.3):
       - "張三上個月參加了 AI 研討會" (7 天前) → 分數 0.9
       - "張三在學習 LangChain" (3 天前) → 分數 1.0

    2. 頻繁記憶 (權重 0.2):
       - "張三是軟體工程師" (訪問 15 次) → 分數 1.0
       - "張三專長 Python" (訪問 10 次) → 分數 0.8

    3. 相關記憶 (權重 0.5):
       - "張三是軟體工程師，專長是 Python 和機器學習" → 分數 0.95
       - "張三參加了 AI 研討會" → 分數 0.85

    最終排序:
    1. "張三是軟體工程師，專長是 Python 和機器學習" (綜合分數: 0.935)
    2. "張三參加了 AI 研討會" (綜合分數: 0.880)
    3. "張三在學習 LangChain" (綜合分數: 0.820)
    """)


def example_5_memory_compression():
    """示例 5：記憶壓縮"""
    print("\n" + "=" * 60)
    print("示例 5：記憶壓縮和摘要")
    print("=" * 60)

    # 記憶壓縮配置
    compression_config = {
        'methods': [
            {
                'name': 'summarization',
                'description': '使用 LLM 生成摘要',
                'config': {
                    'model': 'gpt-4',
                    'maxLength': 200,
                    'preserveKeyFacts': true
                }
            },
            {
                'name': 'deduplication',
                'description': '去除重複信息',
                'config': {
                    'similarityThreshold': 0.95,
                    'keepMostRecent': true
                }
            },
            {
                'name': 'pruning',
                'description': '修剪低價值記憶',
                'config': {
                    'minImportance': 0.3,
                    'keepCount': 100
                }
            }
        ],
        'triggers': [
            {
                'type': 'size',
                'threshold': 1000,  # 超過 1000 條記憶
                'action': 'compress'
            },
            {
                'type': 'time',
                'interval': '24h',  # 每 24 小時
                'action': 'compress'
            }
        ]
    }

    print(f"\n壓縮配置: {json.dumps(compression_config, indent=2, ensure_ascii=False)}")

    # 模擬壓縮
    print("\n壓縮示例:")
    print("""
    原始對話（15 條消息）:
    1. 用戶: 你好
    2. 助手: 你好！有什麼可以幫助你的嗎？
    3. 用戶: 我想了解你們的產品
    4. 助手: 我們有多款產品...
    ... (省略)
    15. 助手: 如有其他問題，隨時聯繫我們！

    壓縮後的摘要:
    "用戶詢問產品信息，助手介紹了三款主要產品（A、B、C）的功能和價格。
     用戶對產品 B 特別感興趣，詢問了技術規格和售後服務。
     助手提供了詳細說明，用戶表示滿意並會考慮購買。"

    保留的關鍵事實:
    - 用戶對產品 B 感興趣
    - 已提供技術規格和售後服務信息
    - 用戶處於考慮階段

    壓縮率: 80% (15 條 → 3 條關鍵信息)
    """)


def example_6_memory_context_window():
    """示例 6：記憶上下文窗口管理"""
    print("\n" + "=" * 60)
    print("示例 6：上下文窗口管理")
    print("=" * 60)

    # 上下文窗口配置
    context_config = {
        'windowSize': {
            'tokens': 4000,  # 最多 4000 tokens
            'messages': 20   # 或 20 條消息
        },
        'strategy': 'sliding',  # 滑動窗口
        'preservation': {
            'systemMessage': true,  # 始終保留系統消息
            'firstMessage': true,   # 保留第一條消息
            'importantFacts': true  # 保留重要事實
        },
        'overflow': {
            'action': 'summarize',  # 超出時摘要
            'keepRecent': 10        # 保留最近 10 條
        }
    }

    print(f"\n上下文配置: {json.dumps(context_config, indent=2, ensure_ascii=False)}")

    print("\n上下文窗口管理示例:")
    print("""
    當前窗口: [系統消息] + [最近 20 條消息]

    添加新消息時:
    1. 檢查 token 數量
    2. 如果超出限制:
       - 保留系統消息
       - 保留第一條消息（建立上下文）
       - 摘要中間的消息
       - 保留最近 10 條消息
    3. 更新窗口

    示例:
    窗口容量: 4000 tokens
    當前使用: 3800 tokens
    新消息: 500 tokens
    需要釋放: 300 tokens

    操作:
    - 移除消息 3-8 (800 tokens)
    - 生成摘要 (100 tokens)
    - 釋放淨空間: 700 tokens
    - 新窗口: 3600 tokens ✓
    """)


def example_7_memory_personalization():
    """示例 7：個性化記憶"""
    print("\n" + "=" * 60)
    print("示例 7：個性化記憶和學習")
    print("=" * 60)

    # 個性化記憶配置
    personalization_config = {
        'userProfile': {
            'demographics': {
                'age': 'optional',
                'location': 'optional',
                'language': 'auto-detect'
            },
            'preferences': {
                'communicationStyle': 'learn',
                'topics': 'track',
                'responseLength': 'adapt'
            },
            'behavior': {
                'sessionTimes': 'track',
                'queryPatterns': 'analyze',
                'feedbackHistory': 'record'
            }
        },
        'learning': {
            'implicit': {
                'enabled': true,
                'signals': ['clicks', 'time_spent', 'scroll_depth']
            },
            'explicit': {
                'enabled': true,
                'feedbackMethods': ['thumbs', 'stars', 'comments']
            }
        },
        'adaptation': {
            'toneAdjustment': true,
            'contentRelevance': true,
            'responseSpeed': true
        }
    }

    print(f"\n個性化配置: {json.dumps(personalization_config, indent=2, ensure_ascii=False)}")

    # 學習示例
    print("\n個性化學習示例:")
    print("""
    用戶: user-001

    觀察到的模式:
    1. 通訊風格:
       - 偏好簡潔回答 (80% 的互動)
       - 喜歡要點列表 (65% 正面反饋)
       - 避免冗長解釋

    2. 主題偏好:
       - 技術主題 (70% 查詢)
       - Python 和 AI (高參與度)
       - 業務策略 (中等參與度)

    3. 互動模式:
       - 活躍時間: 工作日 9-11AM, 2-4PM
       - 平均會話長度: 5-8 輪對話
       - 偏好快速回答

    4. 反饋歷史:
       - 技術準確性: 高評分
       - 代碼示例: 非常有幫助
       - 理論解釋: 評分中等

    適應策略:
    ✅ 使用簡潔、要點式回答
    ✅ 提供 Python 代碼示例
    ✅ 優先技術準確性
    ✅ 減少理論性解釋
    ✅ 快速響應優先於完美
    """)


def example_8_memory_cleanup():
    """示例 8：記憶清理和維護"""
    print("\n" + "=" * 60)
    print("示例 8：記憶清理和維護")
    print("=" * 60)

    cleanup_config = {
        'policies': [
            {
                'name': 'expire_old_sessions',
                'description': '清理過期會話',
                'condition': 'age > 30d AND inactive',
                'action': 'delete'
            },
            {
                'name': 'archive_important',
                'description': '歸檔重要記憶',
                'condition': 'importance > 0.8 AND age > 90d',
                'action': 'archive'
            },
            {
                'name': 'compress_large_sessions',
                'description': '壓縮大型會話',
                'condition': 'messageCount > 100',
                'action': 'compress'
            },
            {
                'name': 'remove_duplicates',
                'description': '移除重複記憶',
                'condition': 'similarity > 0.95',
                'action': 'deduplicate'
            }
        ],
        'schedule': {
            'frequency': 'daily',
            'time': '02:00',  # 凌晨 2 點
            'timezone': 'Asia/Taipei'
        },
        'retention': {
            'shortTerm': '7d',
            'mediumTerm': '30d',
            'longTerm': '365d',
            'permanent': ['user_preferences', 'important_facts']
        }
    }

    print(f"\n清理配置: {json.dumps(cleanup_config, indent=2, ensure_ascii=False)}")


def example_9_memory_privacy():
    """示例 9：記憶隱私和安全"""
    print("\n" + "=" * 60)
    print("示例 9：記憶隱私和安全")
    print("=" * 60)

    print("""
    🔒 記憶隱私和安全最佳實踐

    1. 數據加密
       ✅ 傳輸加密 (TLS/SSL)
       ✅ 存儲加密 (AES-256)
       ✅ 密鑰管理 (KMS)

    2. 訪問控制
       ✅ 用戶隔離
       ✅ 權限檢查
       ✅ 審計日誌

    3. 隱私保護
       ✅ PII 檢測和脫敏
       ✅ 數據最小化
       ✅ 用戶同意管理

    4. 合規性
       ✅ GDPR 合規
       ✅ CCPA 合規
       ✅ 數據可攜性

    5. 用戶權利
       ✅ 查看數據
       ✅ 導出數據
       ✅ 刪除數據
       ✅ 更正數據

    隱私配置示例:
    {
        "privacy": {
            "piiDetection": {
                "enabled": true,
                "entities": ["email", "phone", "ssn", "credit_card"],
                "action": "mask"
            },
            "retention": {
                "autoDelete": true,
                "period": "90d",
                "exceptions": ["explicit_consent"]
            },
            "userRights": {
                "dataAccess": true,
                "dataExport": true,
                "dataDelete": true,
                "rightToCorrect": true
            },
            "compliance": {
                "gdpr": true,
                "ccpa": true,
                "auditLog": true
            }
        }
    }
    """)


def example_10_memory_best_practices():
    """示例 10：記憶管理最佳實踐"""
    print("\n" + "=" * 60)
    print("示例 10：記憶管理最佳實踐")
    print("=" * 60)

    print("""
    📚 記憶管理最佳實踐

    1. 分層記憶架構
       ✅ 短期: 當前會話（快速訪問）
       ✅ 中期: 近期歷史（平衡性能）
       ✅ 長期: 重要事實（持久化）
       ✅ 向量: 語義知識（智能檢索）

    2. 效能優化
       ✅ 索引關鍵字段
       ✅ 緩存熱數據
       ✅ 異步寫入
       ✅ 批量操作

    3. 數據質量
       ✅ 驗證輸入
       ✅ 去重
       ✅ 一致性檢查
       ✅ 定期清理

    4. 可擴展性
       ✅ 水平分片
       ✅ 讀寫分離
       ✅ CDN 加速
       ✅ 負載均衡

    5. 監控和告警
       ✅ 存儲使用率
       ✅ 查詢性能
       ✅ 錯誤率
       ✅ 數據增長趨勢

    6. 災難恢復
       ✅ 定期備份
       ✅ 多地域複製
       ✅ 快速恢復計劃
       ✅ 數據完整性驗證

    7. 用戶體驗
       ✅ 快速響應
       ✅ 相關建議
       ✅ 無縫上下文
       ✅ 個性化體驗
    """)


def main():
    """主函數"""
    print("\n💾 Mastra 記憶管理示例\n")

    try:
        example_1_short_term_memory()
        example_2_long_term_memory()
        example_3_vector_memory()
        example_4_memory_retrieval()
        example_5_memory_compression()
        example_6_memory_context_window()
        example_7_memory_personalization()
        example_8_memory_cleanup()
        example_9_memory_privacy()
        example_10_memory_best_practices()

        print("\n" + "=" * 60)
        print("✅ 所有示例運行完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")


if __name__ == "__main__":
    main()
