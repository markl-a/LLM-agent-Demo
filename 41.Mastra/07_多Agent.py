"""
Mastra 多 Agent 協作示例

本示例展示如何構建多 Agent 系統。

功能：
1. Agent 團隊創建
2. 協作模式（主從、對等、層級）
3. Agent 間通信
4. 任務分配和路由
5. 協作工作流
"""

import os
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()


class MastraMultiAgent:
    """Mastra 多 Agent 管理器"""

    def __init__(self, api_url: str = None):
        """初始化多 Agent 管理器"""
        self.api_url = api_url or os.getenv('MASTRA_API_URL', 'http://localhost:3000')
        self.api_key = os.getenv('MASTRA_API_KEY')

        self.headers = {
            'Content-Type': 'application/json',
        }
        if self.api_key:
            self.headers['Authorization'] = f'Bearer {self.api_key}'

    def create_team(self, team_config: Dict[str, Any]) -> Dict[str, Any]:
        """創建 Agent 團隊"""
        try:
            response = requests.post(
                f'{self.api_url}/api/teams',
                headers=self.headers,
                json=team_config,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def execute_team_task(self, team_name: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """執行團隊任務"""
        try:
            response = requests.post(
                f'{self.api_url}/api/teams/{team_name}/execute',
                headers=self.headers,
                json=task,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}


def example_1_supervisor_pattern():
    """示例 1：主從模式（Supervisor Pattern）"""
    print("=" * 60)
    print("示例 1：主從模式 - 客戶服務團隊")
    print("=" * 60)

    multi_agent = MastraMultiAgent()

    # 定義團隊成員
    team_config = {
        'name': 'customer-service-team',
        'description': '客戶服務團隊',
        'pattern': 'supervisor',
        'agents': [
            {
                'role': 'supervisor',
                'name': 'service-supervisor',
                'description': '客服主管，負責分配任務',
                'model': 'gpt-4',
                'instructions': '''你是客服主管。根據客戶查詢的性質，
                將任務分配給合適的專員：
                - 技術問題 -> technical-agent
                - 帳務問題 -> billing-agent
                - 一般諮詢 -> general-agent

                分析查詢並選擇最合適的 agent。'''
            },
            {
                'role': 'worker',
                'name': 'technical-agent',
                'description': '技術支持專員',
                'model': 'gpt-4',
                'instructions': '''你是技術支持專員，專門處理技術問題。
                提供詳細的技術解決方案和故障排除步驟。'''
            },
            {
                'role': 'worker',
                'name': 'billing-agent',
                'description': '帳務專員',
                'model': 'gpt-4',
                'instructions': '''你是帳務專員，處理付款、發票和訂閱問題。
                提供準確的帳務信息和解決方案。'''
            },
            {
                'role': 'worker',
                'name': 'general-agent',
                'description': '一般諮詢專員',
                'model': 'gpt-4',
                'instructions': '''你是一般諮詢專員，處理產品詢問和一般問題。
                提供友好且有幫助的回答。'''
            }
        ],
        'routing': {
            'strategy': 'llm-based',  # 使用 LLM 決定路由
            'fallback': 'general-agent'  # 默認代理
        }
    }

    result = multi_agent.create_team(team_config)
    print(f"\n團隊創建結果: {json.dumps(result, indent=2, ensure_ascii=False)}")

    # 執行任務
    test_queries = [
        "我的應用無法登入，一直顯示錯誤",
        "我想取消訂閱並申請退款",
        "你們的產品有哪些功能？"
    ]

    for query in test_queries:
        print(f"\n客戶查詢: {query}")
        task = {'query': query}
        result = multi_agent.execute_team_task('customer-service-team', task)
        print(f"處理 Agent: {result.get('handler', 'unknown')}")
        print(f"回答: {result.get('response', 'error')}")


def example_2_peer_collaboration():
    """示例 2：對等協作模式"""
    print("\n" + "=" * 60)
    print("示例 2：對等協作 - 內容創作團隊")
    print("=" * 60)

    multi_agent = MastraMultiAgent()

    team_config = {
        'name': 'content-creation-team',
        'description': '內容創作團隊',
        'pattern': 'peer-to-peer',
        'agents': [
            {
                'role': 'researcher',
                'name': 'content-researcher',
                'description': '內容研究員',
                'model': 'gpt-4',
                'instructions': '''你是內容研究員。
                任務：收集和整理主題相關的資料、數據和引用。
                輸出：結構化的研究報告。''',
                'tools': ['web_search', 'database_query']
            },
            {
                'role': 'writer',
                'name': 'content-writer',
                'description': '內容寫作者',
                'model': 'gpt-4',
                'instructions': '''你是內容寫作者。
                基於研究員提供的資料，撰寫高質量的文章。
                風格：清晰、吸引人、有見地。''',
                'tools': ['grammar_check', 'seo_analysis']
            },
            {
                'role': 'editor',
                'name': 'content-editor',
                'description': '內容編輯',
                'model': 'gpt-4',
                'instructions': '''你是內容編輯。
                審查文章的質量、準確性和一致性。
                提供改進建議並確保符合品牌標準。''',
                'tools': ['plagiarism_check', 'readability_score']
            }
        ],
        'workflow': {
            'type': 'sequential',
            'steps': [
                {
                    'agent': 'content-researcher',
                    'output': 'research_data'
                },
                {
                    'agent': 'content-writer',
                    'input': '{{research_data}}',
                    'output': 'draft_article'
                },
                {
                    'agent': 'content-editor',
                    'input': '{{draft_article}}',
                    'output': 'final_article'
                }
            ],
            'iterative': {
                'enabled': true,
                'maxIterations': 3,
                'condition': '{{content-editor.approval == false}}'
            }
        }
    }

    result = multi_agent.create_team(team_config)
    print(f"\n團隊創建結果: {json.dumps(result, indent=2, ensure_ascii=False)}")

    print("\n協作流程:")
    print("""
    1. 研究員階段:
       - 收集主題相關資料
       - 整理數據和引用
       - 輸出研究報告

    2. 寫作者階段:
       - 基於研究報告撰寫
       - 應用 SEO 最佳實踐
       - 輸出草稿文章

    3. 編輯階段:
       - 審查質量和準確性
       - 提供改進建議
       - 如果不合格，返回寫作者修改
       - 最多迭代 3 次

    4. 完成:
       - 輸出最終文章
    """)


def example_3_hierarchical_pattern():
    """示例 3：層級模式"""
    print("\n" + "=" * 60)
    print("示例 3：層級模式 - 企業決策系統")
    print("=" * 60)

    team_config = {
        'name': 'decision-making-team',
        'description': '企業決策團隊',
        'pattern': 'hierarchical',
        'hierarchy': {
            'ceo': {
                'agent': 'ceo-agent',
                'description': 'CEO - 最終決策者',
                'subordinates': ['cfo', 'cto', 'cmo']
            },
            'cfo': {
                'agent': 'cfo-agent',
                'description': 'CFO - 財務長',
                'subordinates': ['finance-analyst']
            },
            'cto': {
                'agent': 'cto-agent',
                'description': 'CTO - 技術長',
                'subordinates': ['tech-lead', 'security-expert']
            },
            'cmo': {
                'agent': 'cmo-agent',
                'description': 'CMO - 行銷長',
                'subordinates': ['marketing-analyst']
            }
        },
        'communication': {
            'upward': 'report',      # 向上報告
            'downward': 'delegate',  # 向下委派
            'peer': 'collaborate'    # 平級協作
        },
        'decisionProcess': {
            'type': 'bottom-up',
            'aggregation': 'consensus'
        }
    }

    print(f"\n層級結構: {json.dumps(team_config, indent=2, ensure_ascii=False)}")

    print("\n決策流程示例:")
    print("""
    問題: "是否應該投資新產品開發？"

    1. 信息收集階段（底層）:
       - Finance Analyst: 財務可行性分析
       - Tech Lead: 技術可行性評估
       - Marketing Analyst: 市場需求調研

    2. 部門評估（中層）:
       - CFO: 整合財務分析，評估投資回報
       - CTO: 評估技術風險和資源需求
       - CMO: 評估市場機會和競爭態勢

    3. 最終決策（高層）:
       - CEO: 綜合各部門意見
       - 權衡利弊
       - 做出最終決定
       - 制定執行計劃

    輸出:
    - 決策: 是/否
    - 理由: 詳細分析
    - 行動計劃: 具體步驟
    - 風險評估: 潛在問題
    """)


def example_4_debate_pattern():
    """示例 4：辯論模式"""
    print("\n" + "=" * 60)
    print("示例 4：辯論模式 - 多角度分析")
    print("=" * 60)

    team_config = {
        'name': 'debate-team',
        'description': '辯論分析團隊',
        'pattern': 'debate',
        'agents': [
            {
                'role': 'proponent',
                'name': 'advocate-agent',
                'description': '支持方',
                'instructions': '''你是支持方。
                為提議提供最強有力的論據和證據。
                積極論證優點和機會。'''
            },
            {
                'role': 'opponent',
                'name': 'critic-agent',
                'description': '反對方',
                'instructions': '''你是反對方。
                指出提議的缺陷、風險和挑戰。
                提供批判性分析。'''
            },
            {
                'role': 'moderator',
                'name': 'moderator-agent',
                'description': '主持人',
                'instructions': '''你是主持人。
                引導討論，確保雙方充分表達。
                最後總結雙方觀點。'''
            },
            {
                'role': 'judge',
                'name': 'judge-agent',
                'description': '評判者',
                'instructions': '''你是評判者。
                權衡雙方論據，做出客觀評估。
                提供平衡的最終建議。'''
            }
        ],
        'process': {
            'rounds': 3,
            'sequence': [
                'moderator -> proponent',
                'moderator -> opponent',
                'proponent <-> opponent',
                'moderator -> judge'
            ]
        }
    }

    print(f"\n辯論配置: {json.dumps(team_config, indent=2, ensure_ascii=False)}")

    print("\n辯論流程示例:")
    print("""
    議題: "公司是否應該遷移到雲端？"

    第一輪:
    支持方: "雲端可以降低成本、提高靈活性..."
    反對方: "存在安全風險、遷移成本高..."

    第二輪:
    支持方: "現代雲端有完善的安全措施..."
    反對方: "但我們的數據敏感，需要完全控制..."

    第三輪:
    支持方: "可以採用混合雲策略..."
    反對方: "混合雲增加了複雜性..."

    主持人總結:
    - 支持方主要論點: 成本、靈活性、擴展性
    - 反對方主要論點: 安全、控制、遷移風險

    評判者建議:
    "建議採用混合雲策略：
     - 非敏感工作負載遷移到公有雲
     - 敏感數據保留在私有雲
     - 制定詳細的遷移計劃
     - 投資安全和合規措施"
    """)


def example_5_swarm_pattern():
    """示例 5：群體智能模式"""
    print("\n" + "=" * 60)
    print("示例 5：群體智能 - 分散式問題解決")
    print("=" * 60)

    team_config = {
        'name': 'swarm-team',
        'description': '群體智能團隊',
        'pattern': 'swarm',
        'agents': [
            {
                'role': 'explorer',
                'name': f'explorer-{i}',
                'description': f'探索者 {i}',
                'instructions': '''你是探索者。
                探索解決方案空間，尋找新穎的方法。
                與其他 agents 分享發現。'''
            } for i in range(5)
        ],
        'swarmBehavior': {
            'communication': 'broadcast',  # 廣播通信
            'convergence': {
                'method': 'voting',
                'threshold': 0.7  # 70% 共識
            },
            'diversity': {
                'encourage': true,
                'temperature': 0.9  # 鼓勵多樣性
            }
        }
    }

    print(f"\n群體配置: {json.dumps(team_config, indent=2, ensure_ascii=False)}")

    print("\n群體智能示例:")
    print("""
    問題: "優化物流配送路線"

    初始化:
    - 5 個探索者 agents
    - 每個嘗試不同的優化策略

    迭代 1:
    Explorer-1: 使用遺傳算法 (成本: 1200)
    Explorer-2: 使用模擬退火 (成本: 1150)
    Explorer-3: 使用貪婪算法 (成本: 1300)
    Explorer-4: 使用動態規劃 (成本: 1100)
    Explorer-5: 使用蟻群算法 (成本: 1180)

    分享和學習:
    - 所有 agents 了解最佳方案（動態規劃）
    - 結合多種策略的優點

    迭代 2:
    Explorer-1: 混合遺傳+動態規劃 (成本: 1080)
    Explorer-2: 改進模擬退火 (成本: 1090)
    ...

    收斂:
    - 達到 70% 共識
    - 最佳方案: 成本 1050
    - 綜合了多種算法的優點
    """)


def example_6_agent_communication():
    """示例 6：Agent 間通信"""
    print("\n" + "=" * 60)
    print("示例 6：Agent 間通信協議")
    print("=" * 60)

    communication_patterns = {
        'direct': {
            'description': '直接通信',
            'example': {
                'from': 'agent-a',
                'to': 'agent-b',
                'type': 'request',
                'payload': {
                    'action': 'process_data',
                    'data': {'key': 'value'}
                }
            }
        },
        'broadcast': {
            'description': '廣播通信',
            'example': {
                'from': 'coordinator',
                'to': 'all',
                'type': 'announcement',
                'payload': {
                    'message': 'New task available',
                    'priority': 'high'
                }
            }
        },
        'publish-subscribe': {
            'description': '發布-訂閱',
            'example': {
                'publisher': 'data-agent',
                'topic': 'data-updates',
                'subscribers': ['agent-1', 'agent-2'],
                'payload': {
                    'event': 'data_changed',
                    'data': {}
                }
            }
        },
        'queue': {
            'description': '消息隊列',
            'example': {
                'queue': 'tasks',
                'producers': ['task-creator'],
                'consumers': ['worker-1', 'worker-2'],
                'message': {
                    'task_id': '123',
                    'type': 'processing',
                    'data': {}
                }
            }
        }
    }

    print(f"\n通信模式: {json.dumps(communication_patterns, indent=2, ensure_ascii=False)}")


def example_7_task_delegation():
    """示例 7：任務委派和路由"""
    print("\n" + "=" * 60)
    print("示例 7：智能任務委派")
    print("=" * 60)

    delegation_config = {
        'strategies': [
            {
                'name': 'skill-based',
                'description': '基於技能匹配',
                'logic': '''
                    function delegate(task, agents) {
                        // 計算每個 agent 與任務的技能匹配度
                        const scores = agents.map(agent => ({
                            agent,
                            score: calculateSkillMatch(task, agent.skills)
                        }));
                        // 選擇最高分的 agent
                        return scores.sort((a, b) => b.score - a.score)[0].agent;
                    }
                '''
            },
            {
                'name': 'load-balanced',
                'description': '負載均衡',
                'logic': '''
                    function delegate(task, agents) {
                        // 選擇當前負載最低的 agent
                        return agents.sort((a, b) =>
                            a.currentLoad - b.currentLoad
                        )[0];
                    }
                '''
            },
            {
                'name': 'priority-based',
                'description': '基於優先級',
                'logic': '''
                    function delegate(task, agents) {
                        if (task.priority === 'urgent') {
                            // 緊急任務分配給最有經驗的 agent
                            return agents.sort((a, b) =>
                                b.experience - a.experience
                            )[0];
                        }
                        // 普通任務使用輪詢
                        return agents[taskCount++ % agents.length];
                    }
                '''
            },
            {
                'name': 'llm-based',
                'description': '基於 LLM 決策',
                'logic': '''
                    async function delegate(task, agents) {
                        const prompt = `
                            Task: ${task.description}
                            Available Agents: ${JSON.stringify(agents)}

                            Which agent is best suited for this task?
                            Consider: skills, current load, past performance
                        `;
                        const decision = await llm.generate(prompt);
                        return findAgent(decision.agentName);
                    }
                '''
            }
        ]
    }

    print(f"\n委派策略: {json.dumps(delegation_config, indent=2, ensure_ascii=False)}")


def example_8_conflict_resolution():
    """示例 8：衝突解決機制"""
    print("\n" + "=" * 60)
    print("示例 8：Agent 衝突解決")
    print("=" * 60)

    print("""
    🔧 衝突解決機制

    1. 資源衝突
       情況: 多個 agents 競爭同一資源
       解決:
       - 優先級隊列
       - 資源鎖定
       - 時間片輪轉

    2. 決策衝突
       情況: Agents 提出不同的建議
       解決:
       - 投票機制（多數決）
       - 權重評分（基於可信度）
       - 上級仲裁（升級到 supervisor）
       - LLM 評判（中立評估）

    3. 通信衝突
       情況: 消息丟失或亂序
       解決:
       - 消息確認機制
       - 序列號和時間戳
       - 重試邏輯

    4. 狀態衝突
       情況: Agents 對系統狀態有不同認知
       解決:
       - 集中式狀態管理
       - 事件溯源
       - 最終一致性

    示例場景:
    問題: Agent A 和 B 對用戶需求有不同理解

    Agent A: "用戶想要快速交付"
    Agent B: "用戶想要高質量產品"

    解決步驟:
    1. 收集證據: 分析用戶原始查詢
    2. 評分:
       - Agent A 證據強度: 0.7
       - Agent B 證據強度: 0.8
    3. 綜合: "用戶主要重視質量，但也關注交付速度"
    4. 策略: 平衡質量和速度
    """)


def example_9_team_performance():
    """示例 9：團隊性能優化"""
    print("\n" + "=" * 60)
    print("示例 9：多 Agent 團隊性能優化")
    print("=" * 60)

    print("""
    🚀 團隊性能優化策略

    1. 並行化
       ✅ 識別可並行的任務
       ✅ 使用異步通信
       ✅ 避免阻塞等待

       示例:
       # 串行（慢）
       result1 = agent1.process()
       result2 = agent2.process()

       # 並行（快）
       [result1, result2] = await Promise.all([
           agent1.process(),
           agent2.process()
       ])

    2. 緩存和記憶共享
       ✅ 共享知識庫
       ✅ 緩存常見查詢結果
       ✅ 避免重複工作

    3. 負載均衡
       ✅ 動態調整 agent 數量
       ✅ 根據負載分配任務
       ✅ 實現故障轉移

    4. 通信優化
       ✅ 批量處理消息
       ✅ 使用高效的序列化
       ✅ 減少不必要的通信

    5. 監控和調優
       ✅ 追蹤每個 agent 的性能
       ✅ 識別瓶頸
       ✅ A/B 測試不同配置

    性能指標:
    - 任務完成時間
    - Agent 利用率
    - 通信開銷
    - 資源消耗
    - 質量評分
    """)


def example_10_best_practices():
    """示例 10：多 Agent 最佳實踐"""
    print("\n" + "=" * 60)
    print("示例 10：多 Agent 系統最佳實踐")
    print("=" * 60)

    print("""
    📚 多 Agent 系統最佳實踐

    1. 設計原則
       ✅ 單一職責: 每個 agent 專注一項任務
       ✅ 鬆耦合: Agents 之間低依賴
       ✅ 可替換: 易於更新和替換 agents
       ✅ 可擴展: 支持動態添加 agents

    2. 協作模式選擇
       - 簡單任務 → 單 Agent
       - 需要專業分工 → 主從模式
       - 創意任務 → 對等協作
       - 複雜決策 → 層級或辯論模式
       - 探索優化 → 群體智能

    3. 通信設計
       ✅ 明確的消息格式
       ✅ 錯誤處理和重試
       ✅ 超時機制
       ✅ 消息優先級

    4. 狀態管理
       ✅ 集中式狀態存儲
       ✅ 版本控制
       ✅ 事務支持
       ✅ 衝突解決

    5. 測試策略
       ✅ 單元測試（單個 agent）
       ✅ 集成測試（agent 交互）
       ✅ 端到端測試（完整流程）
       ✅ 壓力測試（負載和並發）

    6. 監控和調試
       ✅ 追蹤消息流
       ✅ 記錄決策過程
       ✅ 性能分析
       ✅ 錯誤告警

    7. 安全性
       ✅ Agent 身份驗證
       ✅ 權限控制
       ✅ 數據加密
       ✅ 審計日誌

    8. 可維護性
       ✅ 清晰的文檔
       ✅ 版本管理
       ✅ 配置外部化
       ✅ 模塊化設計

    決策樹:

    需要多 Agent 嗎？
    ├─ 任務複雜且可分解 → 是
    ├─ 需要多種專業知識 → 是
    ├─ 需要並行處理 → 是
    └─ 簡單單一任務 → 否（單 Agent 即可）

    選擇哪種模式？
    ├─ 明確的層級結構 → 主從或層級
    ├─ 平等協作 → 對等
    ├─ 需要多角度分析 → 辯論
    └─ 探索優化問題 → 群體智能
    """)


def main():
    """主函數"""
    print("\n🤝 Mastra 多 Agent 協作示例\n")

    try:
        example_1_supervisor_pattern()
        example_2_peer_collaboration()
        example_3_hierarchical_pattern()
        example_4_debate_pattern()
        example_5_swarm_pattern()
        example_6_agent_communication()
        example_7_task_delegation()
        example_8_conflict_resolution()
        example_9_team_performance()
        example_10_best_practices()

        print("\n" + "=" * 60)
        print("✅ 所有示例運行完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")


if __name__ == "__main__":
    main()
