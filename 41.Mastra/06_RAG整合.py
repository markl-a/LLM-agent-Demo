"""
Mastra RAG（檢索增強生成）整合示例

本示例展示如何在 Mastra 中實現 RAG 系統。

功能：
1. 文檔索引和向量化
2. 語義搜索和檢索
3. 上下文增強生成
4. 混合搜索策略
5. RAG 性能優化
"""

import os
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()


class MastraRAG:
    """Mastra RAG 系統客戶端"""

    def __init__(self, api_url: str = None):
        """初始化 RAG 客戶端"""
        self.api_url = api_url or os.getenv('MASTRA_API_URL', 'http://localhost:3000')
        self.api_key = os.getenv('MASTRA_API_KEY')

        self.headers = {
            'Content-Type': 'application/json',
        }
        if self.api_key:
            self.headers['Authorization'] = f'Bearer {self.api_key}'

    def create_rag(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """創建 RAG 配置"""
        try:
            response = requests.post(
                f'{self.api_url}/api/rag',
                headers=self.headers,
                json=config,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def index_documents(self, rag_name: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """索引文檔"""
        try:
            response = requests.post(
                f'{self.api_url}/api/rag/{rag_name}/index',
                headers=self.headers,
                json={'documents': documents},
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def query(self, rag_name: str, query: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """RAG 查詢"""
        try:
            payload = {'query': query}
            if options:
                payload.update(options)

            response = requests.post(
                f'{self.api_url}/api/rag/{rag_name}/query',
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}


def example_1_basic_rag():
    """示例 1：基礎 RAG 配置"""
    print("=" * 60)
    print("示例 1：基礎 RAG 系統")
    print("=" * 60)

    rag_client = MastraRAG()

    # 基礎 RAG 配置
    config = {
        'name': 'basic-rag',
        'description': '基礎知識庫 RAG',
        'embeddings': {
            'provider': 'openai',
            'model': 'text-embedding-3-large',
            'dimensions': 1536
        },
        'vectorStore': {
            'provider': 'pinecone',
            'index': 'knowledge-base',
            'namespace': 'basic'
        },
        'chunking': {
            'strategy': 'fixed',
            'size': 1000,
            'overlap': 200
        },
        'retrieval': {
            'topK': 5,
            'minScore': 0.7
        }
    }

    result = rag_client.create_rag(config)
    print(f"\nRAG 配置: {json.dumps(result, indent=2, ensure_ascii=False)}")

    # 索引文檔
    documents = [
        {
            'id': 'doc-1',
            'content': '''Mastra 是一個現代化的 TypeScript-first AI Agent 框架。
            它提供了強大的工作流引擎、豐富的工具整合和優雅的多 Agent 協作機制。
            Mastra 特別適合構建生產級的 AI 應用。''',
            'metadata': {
                'source': 'documentation',
                'category': 'intro',
                'date': '2025-01-01'
            }
        },
        {
            'id': 'doc-2',
            'content': '''Mastra 支持多種 LLM 提供商，包括 OpenAI、Anthropic 和 Cohere。
            您可以輕鬆切換不同的模型，並且框架會自動處理 API 調用和錯誤處理。''',
            'metadata': {
                'source': 'documentation',
                'category': 'features',
                'date': '2025-01-01'
            }
        },
        {
            'id': 'doc-3',
            'content': '''使用 Mastra 的工作流引擎，您可以定義複雜的多步驟流程。
            工作流支持順序執行、並行執行、條件分支和循環迭代。''',
            'metadata': {
                'source': 'documentation',
                'category': 'workflows',
                'date': '2025-01-01'
            }
        }
    ]

    index_result = rag_client.index_documents('basic-rag', documents)
    print(f"\n索引結果: {json.dumps(index_result, indent=2, ensure_ascii=False)}")

    # 查詢
    queries = [
        "Mastra 是什麼？",
        "Mastra 支持哪些 LLM？",
        "如何使用工作流？"
    ]

    for query in queries:
        print(f"\n查詢: {query}")
        result = rag_client.query('basic-rag', query)
        if 'answer' in result:
            print(f"回答: {result['answer']}")
            print(f"來源: {[doc['id'] for doc in result.get('sources', [])]}")


def example_2_advanced_chunking():
    """示例 2：進階文檔分塊策略"""
    print("\n" + "=" * 60)
    print("示例 2：進階文檔分塊策略")
    print("=" * 60)

    chunking_strategies = {
        'fixed': {
            'description': '固定大小分塊',
            'config': {
                'strategy': 'fixed',
                'size': 1000,
                'overlap': 200,
                'separator': '\n\n'
            },
            'pros': ['簡單', '可預測'],
            'cons': ['可能切斷語義單元']
        },
        'semantic': {
            'description': '語義分塊',
            'config': {
                'strategy': 'semantic',
                'model': 'gpt-4',
                'minSize': 500,
                'maxSize': 2000,
                'coherenceThreshold': 0.8
            },
            'pros': ['保持語義完整', '質量高'],
            'cons': ['計算成本高', '較慢']
        },
        'recursive': {
            'description': '遞歸分塊',
            'config': {
                'strategy': 'recursive',
                'separators': ['\n\n', '\n', '. ', ' '],
                'chunkSize': 1000,
                'overlap': 200
            },
            'pros': ['靈活', '保持結構'],
            'cons': ['複雜度中等']
        },
        'markdown': {
            'description': 'Markdown 結構分塊',
            'config': {
                'strategy': 'markdown',
                'splitBy': 'section',  # 按章節
                'maxSize': 2000,
                'preserveHeaders': true
            },
            'pros': ['保持文檔結構', '適合技術文檔'],
            'cons': ['僅適用於 Markdown']
        },
        'code': {
            'description': '代碼分塊',
            'config': {
                'strategy': 'code',
                'language': 'python',
                'splitBy': 'function',  # 按函數
                'includeContext': true
            },
            'pros': ['保持代碼完整性', '包含上下文'],
            'cons': ['需要語言特定解析器']
        }
    }

    print("\n分塊策略對比:")
    for name, strategy in chunking_strategies.items():
        print(f"\n{name}:")
        print(f"  描述: {strategy['description']}")
        print(f"  優點: {', '.join(strategy['pros'])}")
        print(f"  缺點: {', '.join(strategy['cons'])}")
        print(f"  配置: {json.dumps(strategy['config'], indent=4, ensure_ascii=False)}")


def example_3_hybrid_search():
    """示例 3：混合搜索策略"""
    print("\n" + "=" * 60)
    print("示例 3：混合搜索（語義 + 關鍵詞）")
    print("=" * 60)

    rag_client = MastraRAG()

    # 混合搜索配置
    config = {
        'name': 'hybrid-search-rag',
        'description': '混合搜索 RAG',
        'search': {
            'strategies': [
                {
                    'type': 'semantic',
                    'weight': 0.7,
                    'config': {
                        'embeddings': {
                            'provider': 'openai',
                            'model': 'text-embedding-3-large'
                        },
                        'topK': 10
                    }
                },
                {
                    'type': 'keyword',
                    'weight': 0.3,
                    'config': {
                        'algorithm': 'BM25',
                        'topK': 10
                    }
                }
            ],
            'fusion': {
                'method': 'reciprocal_rank_fusion',  # RRF
                'k': 60
            },
            'reranking': {
                'enabled': true,
                'model': 'cohere-rerank',
                'topK': 5
            }
        }
    }

    print(f"\n混合搜索配置: {json.dumps(config, indent=2, ensure_ascii=False)}")

    print("\n混合搜索工作流程:")
    print("""
    1. 並行搜索:
       - 語義搜索: 使用向量相似度
       - 關鍵詞搜索: 使用 BM25 算法

    2. 結果融合:
       - 使用 Reciprocal Rank Fusion (RRF)
       - 公式: RRF(d) = Σ 1/(k + rank(d))

    3. 重排序:
       - 使用 Cohere Rerank 模型
       - 根據查詢相關性重新排序

    4. 返回最終結果

    示例:
    查詢: "如何優化 RAG 性能"

    語義搜索結果:
    1. "RAG 性能優化技巧" (0.92)
    2. "提升檢索質量" (0.88)
    3. "向量索引優化" (0.85)

    關鍵詞搜索結果:
    1. "RAG 系統性能調優" (15.3)
    2. "優化檢索速度" (12.7)
    3. "性能基準測試" (11.2)

    RRF 融合後:
    1. "RAG 性能優化技巧"
    2. "RAG 系統性能調優"
    3. "提升檢索質量"

    重排序後:
    1. "RAG 系統性能調優"
    2. "RAG 性能優化技巧"
    3. "向量索引優化"
    """)


def example_4_metadata_filtering():
    """示例 4：元數據過濾"""
    print("\n" + "=" * 60)
    print("示例 4：元數據過濾和查詢優化")
    print("=" * 60)

    rag_client = MastraRAG()

    # 帶元數據過濾的查詢
    query_examples = [
        {
            'description': '按日期過濾',
            'query': '最新的產品更新',
            'filters': {
                'metadata.date': {
                    '$gte': '2025-01-01'
                },
                'metadata.category': 'product-updates'
            }
        },
        {
            'description': '按來源過濾',
            'query': '技術文檔',
            'filters': {
                'metadata.source': {
                    '$in': ['official-docs', 'api-reference']
                },
                'metadata.language': 'zh-TW'
            }
        },
        {
            'description': '組合過濾',
            'query': '高級功能',
            'filters': {
                '$and': [
                    {'metadata.level': 'advanced'},
                    {'metadata.verified': true},
                    {'metadata.date': {'$gte': '2024-01-01'}}
                ]
            }
        },
        {
            'description': '排除過濾',
            'query': '教程',
            'filters': {
                '$not': {
                    'metadata.deprecated': true
                }
            }
        }
    ]

    for example in query_examples:
        print(f"\n{example['description']}:")
        print(f"  查詢: {example['query']}")
        print(f"  過濾器: {json.dumps(example['filters'], indent=4, ensure_ascii=False)}")


def example_5_contextual_compression():
    """示例 5：上下文壓縮"""
    print("\n" + "=" * 60)
    print("示例 5：上下文壓縮和優化")
    print("=" * 60)

    compression_config = {
        'name': 'compressed-rag',
        'description': '帶上下文壓縮的 RAG',
        'retrieval': {
            'topK': 20,  # 先檢索更多文檔
            'compression': {
                'enabled': true,
                'method': 'llm',
                'config': {
                    'model': 'gpt-4',
                    'prompt': '''從以下文檔中提取與查詢最相關的信息。
                    保留關鍵事實、數據和引用。
                    移除冗餘和不相關的內容。

                    查詢: {{query}}
                    文檔: {{documents}}
                    ''',
                    'maxTokens': 2000
                }
            },
            'deduplication': {
                'enabled': true,
                'similarityThreshold': 0.95
            }
        }
    }

    print(f"\n壓縮配置: {json.dumps(compression_config, indent=2, ensure_ascii=False)}")

    print("\n上下文壓縮示例:")
    print("""
    原始檢索結果（3 個文檔，共 3000 tokens）:

    文檔 1 (1200 tokens):
    "Mastra 是一個 TypeScript-first AI Agent 框架...
     [大量背景信息]
     關鍵特性包括工作流引擎、工具整合..."

    文檔 2 (1000 tokens):
    "框架支持多種 LLM 提供商...
     [重複的介紹]
     性能優化建議: 使用緩存、批量處理..."

    文檔 3 (800 tokens):
    "安裝步驟: npm install @mastra/core...
     [詳細的安裝說明]
     配置文件示例..."

    壓縮後（800 tokens）:
    "Mastra TypeScript AI Agent 框架核心特性:
     1. 工作流引擎 - 支持複雜流程編排
     2. 工具整合 - 100+ 預建整合
     3. 多 LLM 支持 - OpenAI, Anthropic, Cohere

     性能優化:
     - 使用緩存減少 API 調用
     - 批量處理提升效率

     安裝: npm install @mastra/core"

    壓縮率: 73% (3000 → 800 tokens)
    相關性: 保留所有關鍵信息
    """)


def example_6_query_expansion():
    """示例 6：查詢擴展"""
    print("\n" + "=" * 60)
    print("示例 6：查詢擴展和改寫")
    print("=" * 60)

    expansion_config = {
        'queryExpansion': {
            'enabled': true,
            'strategies': [
                {
                    'type': 'synonyms',
                    'description': '同義詞擴展',
                    'example': {
                        'original': '快速',
                        'expanded': ['快速', '迅速', '高效', '敏捷']
                    }
                },
                {
                    'type': 'llm-rewrite',
                    'description': 'LLM 改寫查詢',
                    'config': {
                        'model': 'gpt-4',
                        'numVariations': 3
                    },
                    'example': {
                        'original': '如何提升性能',
                        'variations': [
                            '性能優化的最佳實踐',
                            '提高系統效率的方法',
                            '性能調優技巧'
                        ]
                    }
                },
                {
                    'type': 'multi-query',
                    'description': '生成多個子查詢',
                    'example': {
                        'original': 'RAG 系統優化',
                        'subQueries': [
                            '如何優化檢索質量',
                            '如何提升生成速度',
                            '如何減少幻覺'
                        ]
                    }
                },
                {
                    'type': 'hyde',
                    'description': '假設性文檔嵌入',
                    'example': {
                        'query': '什麼是 Mastra',
                        'hypothetical': 'Mastra 是一個現代化的 TypeScript-first AI Agent 框架...'
                    }
                }
            ]
        }
    }

    print(f"\n查詢擴展策略: {json.dumps(expansion_config, indent=2, ensure_ascii=False)}")


def example_7_multi_modal_rag():
    """示例 7：多模態 RAG"""
    print("\n" + "=" * 60)
    print("示例 7：多模態 RAG（文本 + 圖片）")
    print("=" * 60)

    multimodal_config = {
        'name': 'multimodal-rag',
        'description': '多模態知識庫',
        'modalities': {
            'text': {
                'embeddings': {
                    'provider': 'openai',
                    'model': 'text-embedding-3-large'
                }
            },
            'image': {
                'embeddings': {
                    'provider': 'openai',
                    'model': 'clip-vit-large'
                },
                'ocr': {
                    'enabled': true,
                    'provider': 'google-vision'
                }
            },
            'code': {
                'embeddings': {
                    'provider': 'openai',
                    'model': 'code-embedding'
                },
                'syntax': {
                    'highlighting': true,
                    'parsing': true
                }
            }
        },
        'fusion': {
            'crossModal': true,
            'weights': {
                'text': 0.5,
                'image': 0.3,
                'code': 0.2
            }
        }
    }

    print(f"\n多模態配置: {json.dumps(multimodal_config, indent=2, ensure_ascii=False)}")

    print("\n多模態檢索示例:")
    print("""
    查詢: "如何設計用戶界面"

    檢索結果:
    1. 文本文檔: "UI 設計原則和最佳實踐" (0.92)
    2. 圖片: architecture-diagram.png (0.88)
       - OCR 文本: "用戶界面架構圖"
       - 視覺特徵: 包含組件布局
    3. 代碼: Button.tsx (0.85)
       - 註釋: "可重用的按鈕組件"
       - 功能: UI 組件實現

    融合後的上下文:
    - 設計原則（文本）
    - 架構圖（圖片）
    - 代碼示例（代碼）

    生成的回答:
    結合理論、視覺和實現的完整答案
    """)


def example_8_rag_evaluation():
    """示例 8：RAG 評估指標"""
    print("\n" + "=" * 60)
    print("示例 8：RAG 系統評估")
    print("=" * 60)

    evaluation_metrics = {
        'retrieval': {
            'precision': {
                'description': '檢索精確度',
                'formula': '相關文檔數 / 檢索文檔總數',
                'target': '> 0.8'
            },
            'recall': {
                'description': '檢索召回率',
                'formula': '檢索到的相關文檔 / 所有相關文檔',
                'target': '> 0.9'
            },
            'mrr': {
                'description': '平均倒數排名',
                'formula': '1 / 第一個相關文檔的排名',
                'target': '> 0.85'
            },
            'ndcg': {
                'description': '歸一化折損累積增益',
                'formula': 'DCG / IDCG',
                'target': '> 0.9'
            }
        },
        'generation': {
            'faithfulness': {
                'description': '忠實度（無幻覺）',
                'method': 'LLM 評估生成內容是否基於檢索文檔',
                'target': '> 0.95'
            },
            'relevance': {
                'description': '答案相關性',
                'method': '評估答案是否回答了問題',
                'target': '> 0.9'
            },
            'coherence': {
                'description': '連貫性',
                'method': '評估答案的邏輯流暢度',
                'target': '> 0.85'
            }
        },
        'endToEnd': {
            'latency': {
                'description': '端到端延遲',
                'target': '< 2s (p95)'
            },
            'cost': {
                'description': '每次查詢成本',
                'components': ['embeddings', 'vector search', 'LLM generation'],
                'target': '< $0.01'
            },
            'userSatisfaction': {
                'description': '用戶滿意度',
                'method': '顯式反饋（讚/踩）',
                'target': '> 85% 正面'
            }
        }
    }

    print("\nRAG 評估指標:")
    for category, metrics in evaluation_metrics.items():
        print(f"\n{category.upper()}:")
        for name, details in metrics.items():
            print(f"  {name}:")
            for key, value in details.items():
                print(f"    {key}: {value}")


def example_9_rag_optimization():
    """示例 9：RAG 優化技巧"""
    print("\n" + "=" * 60)
    print("示例 9：RAG 性能優化")
    print("=" * 60)

    print("""
    🚀 RAG 性能優化最佳實踐

    1. 索引優化
       ✅ 使用高質量的 embeddings 模型
       ✅ 優化分塊大小和重疊
       ✅ 創建適當的索引（HNSW, IVF）
       ✅ 定期更新和維護索引

    2. 檢索優化
       ✅ 使用混合搜索（語義 + 關鍵詞）
       ✅ 實現查詢擴展和改寫
       ✅ 添加元數據過濾
       ✅ 使用重排序模型

    3. 上下文優化
       ✅ 壓縮檢索到的文檔
       ✅ 去除重複內容
       ✅ 保留最相關的片段
       ✅ 控制上下文長度

    4. 生成優化
       ✅ 優化提示詞模板
       ✅ 使用適當的溫度設置
       ✅ 實現流式輸出
       ✅ 緩存常見查詢

    5. 性能優化
       ✅ 批量處理嵌入
       ✅ 異步檢索
       ✅ 使用 CDN 加速
       ✅ 實現多級緩存

    6. 成本優化
       ✅ 緩存 embeddings
       ✅ 使用較小的模型（when appropriate）
       ✅ 批量 API 調用
       ✅ 智能 token 管理

    7. 質量優化
       ✅ 數據清洗和預處理
       ✅ 定期評估和調優
       ✅ A/B 測試不同配置
       ✅ 收集用戶反饋
    """)


def example_10_production_rag():
    """示例 10：生產級 RAG 配置"""
    print("\n" + "=" * 60)
    print("示例 10：生產級 RAG 系統")
    print("=" * 60)

    production_config = {
        'name': 'production-rag',
        'description': '生產級 RAG 系統',
        'embeddings': {
            'provider': 'openai',
            'model': 'text-embedding-3-large',
            'batchSize': 100,
            'cache': {
                'enabled': true,
                'ttl': '7d',
                'provider': 'redis'
            }
        },
        'vectorStore': {
            'provider': 'pinecone',
            'index': 'production-kb',
            'replicas': 3,
            'shards': 2,
            'pods': 'p1.x2'
        },
        'retrieval': {
            'hybrid': {
                'semantic': {
                    'weight': 0.7,
                    'topK': 20
                },
                'keyword': {
                    'weight': 0.3,
                    'algorithm': 'BM25'
                }
            },
            'reranking': {
                'enabled': true,
                'model': 'cohere-rerank-v3',
                'topK': 5
            },
            'compression': {
                'enabled': true,
                'maxTokens': 2000
            }
        },
        'generation': {
            'model': 'gpt-4-turbo',
            'temperature': 0.7,
            'streaming': true,
            'maxTokens': 1000
        },
        'monitoring': {
            'metrics': ['latency', 'cost', 'quality'],
            'logging': {
                'level': 'info',
                'destination': 'datadog'
            },
            'alerts': {
                'latencyP95': '> 3s',
                'errorRate': '> 1%',
                'costPerQuery': '> $0.02'
            }
        },
        'security': {
            'authentication': 'required',
            'rateLimit': {
                'requests': 100,
                'window': '1m'
            },
            'piiDetection': true
        },
        'scaling': {
            'autoScale': true,
            'minReplicas': 2,
            'maxReplicas': 10,
            'targetCPU': 70
        }
    }

    print(f"\n生產配置: {json.dumps(production_config, indent=2, ensure_ascii=False)}")


def main():
    """主函數"""
    print("\n📚 Mastra RAG 整合示例\n")

    try:
        example_1_basic_rag()
        example_2_advanced_chunking()
        example_3_hybrid_search()
        example_4_metadata_filtering()
        example_5_contextual_compression()
        example_6_query_expansion()
        example_7_multi_modal_rag()
        example_8_rag_evaluation()
        example_9_rag_optimization()
        example_10_production_rag()

        print("\n" + "=" * 60)
        print("✅ 所有示例運行完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")


if __name__ == "__main__":
    main()
