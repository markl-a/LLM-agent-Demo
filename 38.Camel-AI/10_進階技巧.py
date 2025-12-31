"""
CAMEL-AI 進階技巧

這個範例展示 CAMEL 的高級配置和優化技巧：
1. 自定義 Agent 配置
2. Memory 管理策略
3. 性能優化技巧
4. 錯誤處理和重試
5. 監控和日誌
6. 生產環境部署建議

掌握這些技巧可以構建更穩定、高效的 Agent 系統。
"""

import os
from dotenv import load_dotenv
from colorama import init, Fore, Style
from typing import List, Dict, Any
import time

init(autoreset=True)
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print(f"{Fore.RED}錯誤: 請設置 OPENAI_API_KEY{Style.RESET_ALL}")
    exit(1)


def example1_advanced_agent_configuration():
    """範例1: 高級 Agent 配置"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例1: 高級 Agent 配置")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage
        from camel.configs import ChatGPTConfig

        print(f"{Fore.YELLOW}配置不同場景的 Agent...{Style.RESET_ALL}\n")

        # 配置 1: 創意型 Agent
        creative_config = ChatGPTConfig(
            temperature=0.9,      # 高創造性
            top_p=0.95,
            presence_penalty=0.6,  # 鼓勵新想法
            frequency_penalty=0.6,
            max_tokens=1000
        )

        creative_msg = BaseMessage.make_assistant_message(
            role_name="創意作家",
            content="你是一位富有創造力的作家。"
        )

        creative_agent = ChatAgent(
            system_message=creative_msg,
            model_type="gpt-3.5-turbo",
            model_config=creative_config
        )

        # 配置 2: 精確型 Agent
        precise_config = ChatGPTConfig(
            temperature=0.1,      # 低溫度，更精確
            top_p=0.1,
            presence_penalty=0.0,
            frequency_penalty=0.0,
            max_tokens=500
        )

        precise_msg = BaseMessage.make_assistant_message(
            role_name="技術分析師",
            content="你是一位精確的技術分析師。"
        )

        precise_agent = ChatAgent(
            system_message=precise_msg,
            model_type="gpt-3.5-turbo",
            model_config=precise_config
        )

        # 配置 3: 平衡型 Agent
        balanced_config = ChatGPTConfig(
            temperature=0.7,
            top_p=0.9,
            presence_penalty=0.2,
            frequency_penalty=0.2,
            max_tokens=800
        )

        balanced_msg = BaseMessage.make_assistant_message(
            role_name="通用助手",
            content="你是一位平衡的助手。"
        )

        balanced_agent = ChatAgent(
            system_message=balanced_msg,
            model_type="gpt-3.5-turbo",
            model_config=balanced_config
        )

        # 測試不同配置
        prompt = "描述一下未來的 AI 系統"

        agents = [
            ("創意型", creative_agent, creative_config),
            ("精確型", precise_agent, precise_config),
            ("平衡型", balanced_agent, balanced_config)
        ]

        print(f"{Fore.CYAN}測試提示:{Style.RESET_ALL} {prompt}\n")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        for name, agent, config in agents:
            print(f"{Fore.GREEN}[{name} Agent]{Style.RESET_ALL}")
            print(f"配置: temp={config.temperature}, top_p={config.top_p}\n")

            msg = BaseMessage.make_user_message(
                role_name="用戶",
                content=prompt
            )

            response = agent.step(msg)
            print(f"{response.msg.content[:200]}...\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example2_memory_management():
    """範例2: Memory 管理策略"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例2: Memory 管理策略")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage

        print(f"{Fore.YELLOW}演示不同的 Memory 管理策略...{Style.RESET_ALL}\n")

        class MemoryManager:
            """記憶管理器"""

            def __init__(self, max_messages: int = 10):
                self.max_messages = max_messages
                self.messages = []

            def add_message(self, role: str, content: str):
                """添加消息"""
                self.messages.append({
                    "role": role,
                    "content": content,
                    "timestamp": time.time()
                })

                # 保持消息數量限制
                if len(self.messages) > self.max_messages:
                    self.messages = self.messages[-self.max_messages:]

            def get_context(self, strategy: str = "recent") -> str:
                """獲取上下文"""
                if strategy == "recent":
                    # 最近的消息
                    return self._get_recent_context()
                elif strategy == "summary":
                    # 摘要式上下文
                    return self._get_summary_context()
                elif strategy == "important":
                    # 重要消息
                    return self._get_important_context()

            def _get_recent_context(self, n: int = 5) -> str:
                """獲取最近 n 條消息"""
                recent = self.messages[-n:]
                return "\n".join([f"{m['role']}: {m['content']}" for m in recent])

            def _get_summary_context(self) -> str:
                """獲取摘要上下文"""
                if not self.messages:
                    return ""

                # 簡化：只保留關鍵信息
                summary = f"對話開始於: {self.messages[0]['content'][:50]}...\n"
                summary += f"最近討論: {self.messages[-1]['content'][:50]}..."
                return summary

            def _get_important_context(self) -> str:
                """獲取重要消息（示例：包含問號的）"""
                important = [m for m in self.messages if '？' in m['content'] or '?' in m['content']]
                return "\n".join([f"{m['role']}: {m['content']}" for m in important[-3:]])

        # 測試記憶管理
        memory = MemoryManager(max_messages=10)

        # 模擬對話
        conversations = [
            ("用戶", "你好，我想學習 Python"),
            ("助手", "很好！Python 是一門很棒的語言"),
            ("用戶", "從哪裡開始？"),
            ("助手", "建議從基礎語法開始"),
            ("用戶", "能推薦一些資源嗎？"),
            ("助手", "當然，有很多優秀的在線課程")
        ]

        print(f"{Fore.CYAN}添加對話到記憶...{Style.RESET_ALL}\n")

        for role, content in conversations:
            memory.add_message(role, content)
            print(f"  {role}: {content}")

        print(f"\n{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        # 測試不同策略
        strategies = ["recent", "summary", "important"]

        for strategy in strategies:
            print(f"{Fore.GREEN}策略: {strategy}{Style.RESET_ALL}\n")
            context = memory.get_context(strategy)
            print(f"{context}\n")
            print(f"{Fore.MAGENTA}{'-'*60}{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example3_performance_optimization():
    """範例3: 性能優化"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例3: 性能優化技巧")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        print(f"{Fore.YELLOW}演示性能優化技巧...{Style.RESET_ALL}\n")

        class PerformanceOptimizer:
            """性能優化器"""

            @staticmethod
            def batch_processing(items: List[str], batch_size: int = 5):
                """批次處理"""
                print(f"{Fore.CYAN}批次處理 ({len(items)} 項目, 批次大小 {batch_size}):{Style.RESET_ALL}\n")

                for i in range(0, len(items), batch_size):
                    batch = items[i:i+batch_size]
                    print(f"  處理批次 {i//batch_size + 1}: {len(batch)} 項目")
                    # 模擬處理
                    time.sleep(0.1)

                print()

            @staticmethod
            def caching_demo():
                """緩存示例"""
                print(f"{Fore.CYAN}緩存策略:{Style.RESET_ALL}\n")

                cache = {}

                def expensive_operation(key: str) -> str:
                    """模擬昂貴操作"""
                    if key in cache:
                        print(f"  ✓ 緩存命中: {key}")
                        return cache[key]

                    print(f"  ⚙ 執行計算: {key}")
                    time.sleep(0.1)  # 模擬延遲
                    result = f"結果_{key}"
                    cache[key] = result
                    return result

                # 測試
                keys = ["query1", "query2", "query1", "query3", "query2"]
                for key in keys:
                    expensive_operation(key)

                print()

            @staticmethod
            def token_optimization():
                """Token 優化"""
                print(f"{Fore.CYAN}Token 優化:{Style.RESET_ALL}\n")

                def estimate_tokens(text: str) -> int:
                    """估算 token 數（簡化）"""
                    return len(text.split())

                def optimize_prompt(prompt: str, max_tokens: int = 50) -> str:
                    """優化提示詞長度"""
                    tokens = estimate_tokens(prompt)

                    if tokens <= max_tokens:
                        return prompt

                    # 簡化：截斷
                    words = prompt.split()
                    return ' '.join(words[:max_tokens]) + "..."

                long_prompt = "這是一個非常長的提示詞 " * 20

                print(f"  原始: {estimate_tokens(long_prompt)} tokens")
                optimized = optimize_prompt(long_prompt, max_tokens=50)
                print(f"  優化後: {estimate_tokens(optimized)} tokens")
                print(f"  優化: {optimized[:100]}...\n")

        optimizer = PerformanceOptimizer()

        # 測試優化技巧
        print(f"{Fore.GREEN}1. 批次處理{Style.RESET_ALL}\n")
        items = [f"任務{i}" for i in range(15)]
        optimizer.batch_processing(items, batch_size=5)

        print(f"{Fore.GREEN}2. 緩存策略{Style.RESET_ALL}\n")
        optimizer.caching_demo()

        print(f"{Fore.GREEN}3. Token 優化{Style.RESET_ALL}\n")
        optimizer.token_optimization()

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example4_error_handling():
    """範例4: 錯誤處理和重試"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例4: 錯誤處理和重試機制")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        print(f"{Fore.YELLOW}演示錯誤處理策略...{Style.RESET_ALL}\n")

        class RobustAgent:
            """具有錯誤處理的 Agent 包裝器"""

            def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
                self.max_retries = max_retries
                self.retry_delay = retry_delay

            def execute_with_retry(self, operation, *args, **kwargs):
                """帶重試的執行"""
                last_error = None

                for attempt in range(1, self.max_retries + 1):
                    try:
                        print(f"  嘗試 {attempt}/{self.max_retries}...")
                        result = operation(*args, **kwargs)
                        print(f"  ✓ 成功！")
                        return result

                    except Exception as e:
                        last_error = e
                        print(f"  ✗ 失敗: {str(e)}")

                        if attempt < self.max_retries:
                            wait_time = self.retry_delay * attempt
                            print(f"  等待 {wait_time}秒 後重試...\n")
                            time.sleep(wait_time)
                        else:
                            print(f"  已達最大重試次數\n")

                raise last_error

            def validate_response(self, response: str, criteria: Dict[str, Any]) -> bool:
                """驗證回應"""
                # 檢查最小長度
                if 'min_length' in criteria:
                    if len(response) < criteria['min_length']:
                        return False

                # 檢查必需關鍵字
                if 'required_keywords' in criteria:
                    for keyword in criteria['required_keywords']:
                        if keyword.lower() not in response.lower():
                            return False

                return True

        # 測試錯誤處理
        agent = RobustAgent(max_retries=3, retry_delay=0.5)

        print(f"{Fore.GREEN}1. 重試機制測試{Style.RESET_ALL}\n")

        def unstable_operation(success_rate: float = 0.3):
            """不穩定的操作（模擬）"""
            import random
            if random.random() < success_rate:
                return "成功結果"
            raise Exception("隨機失敗")

        try:
            result = agent.execute_with_retry(unstable_operation, success_rate=0.5)
            print(f"最終結果: {result}\n")
        except Exception as e:
            print(f"操作失敗: {e}\n")

        print(f"{Fore.GREEN}2. 回應驗證測試{Style.RESET_ALL}\n")

        test_responses = [
            ("這是一個很短的回應", False),
            ("這是一個較長的回應，包含了足夠的內容來滿足最小長度要求", True),
        ]

        criteria = {
            'min_length': 20,
            'required_keywords': []
        }

        for response, expected in test_responses:
            is_valid = agent.validate_response(response, criteria)
            status = "✓ 通過" if is_valid == expected else "✗ 失敗"
            print(f"  {status}: '{response[:40]}...' (長度: {len(response)})")

        print()

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example5_monitoring_and_logging():
    """範例5: 監控和日誌"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例5: 監控和日誌系統")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        import logging
        from datetime import datetime

        print(f"{Fore.YELLOW}設置監控和日誌...{Style.RESET_ALL}\n")

        class AgentMonitor:
            """Agent 監控器"""

            def __init__(self):
                self.metrics = {
                    "requests": 0,
                    "successes": 0,
                    "failures": 0,
                    "total_tokens": 0,
                    "total_time": 0.0
                }
                self.setup_logging()

            def setup_logging(self):
                """設置日誌"""
                logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                self.logger = logging.getLogger("AgentMonitor")

            def log_request(self, agent_name: str, query: str):
                """記錄請求"""
                self.metrics["requests"] += 1
                self.logger.info(f"Agent: {agent_name}, Query: {query[:50]}...")

            def log_response(self, success: bool, tokens: int, elapsed_time: float):
                """記錄回應"""
                if success:
                    self.metrics["successes"] += 1
                else:
                    self.metrics["failures"] += 1

                self.metrics["total_tokens"] += tokens
                self.metrics["total_time"] += elapsed_time

                self.logger.info(
                    f"Success: {success}, Tokens: {tokens}, Time: {elapsed_time:.2f}s"
                )

            def get_metrics(self) -> Dict[str, Any]:
                """獲取指標"""
                success_rate = (
                    self.metrics["successes"] / self.metrics["requests"] * 100
                    if self.metrics["requests"] > 0 else 0
                )

                avg_time = (
                    self.metrics["total_time"] / self.metrics["requests"]
                    if self.metrics["requests"] > 0 else 0
                )

                return {
                    **self.metrics,
                    "success_rate": success_rate,
                    "avg_time": avg_time,
                    "avg_tokens": (
                        self.metrics["total_tokens"] / self.metrics["requests"]
                        if self.metrics["requests"] > 0 else 0
                    )
                }

        # 測試監控
        monitor = AgentMonitor()

        print(f"{Fore.CYAN}模擬 Agent 操作...{Style.RESET_ALL}\n")

        # 模擬一些操作
        operations = [
            ("Agent1", "查詢1", True, 150, 0.5),
            ("Agent1", "查詢2", True, 200, 0.7),
            ("Agent2", "查詢3", False, 0, 0.0),
            ("Agent2", "查詢4", True, 180, 0.6),
        ]

        for agent, query, success, tokens, elapsed in operations:
            monitor.log_request(agent, query)
            monitor.log_response(success, tokens, elapsed)

        # 顯示指標
        print(f"\n{Fore.GREEN}監控指標:{Style.RESET_ALL}\n")

        metrics = monitor.get_metrics()
        print(f"  總請求數: {metrics['requests']}")
        print(f"  成功: {metrics['successes']}")
        print(f"  失敗: {metrics['failures']}")
        print(f"  成功率: {metrics['success_rate']:.1f}%")
        print(f"  總 Tokens: {metrics['total_tokens']}")
        print(f"  平均 Tokens: {metrics['avg_tokens']:.1f}")
        print(f"  平均耗時: {metrics['avg_time']:.2f}秒\n")

    except Exception as e:
        print(f"{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")


def example6_production_deployment():
    """範例6: 生產環境部署建議"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"範例6: 生產環境部署建議")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    print(f"{Fore.YELLOW}生產環境部署檢查清單:{Style.RESET_ALL}\n")

    checklist = {
        "安全性": [
            "API 密鑰管理（使用環境變量或密鑰管理服務）",
            "輸入驗證和清理",
            "速率限制",
            "訪問控制"
        ],
        "可靠性": [
            "錯誤處理和重試機制",
            "超時設置",
            "熔斷器模式",
            "健康檢查端點"
        ],
        "性能": [
            "響應緩存",
            "批次處理",
            "異步處理",
            "連接池管理"
        ],
        "監控": [
            "日誌系統",
            "指標收集",
            "告警設置",
            "追蹤系統"
        ],
        "擴展性": [
            "水平擴展支持",
            "負載均衡",
            "狀態管理",
            "數據庫優化"
        ],
        "維護": [
            "版本控制",
            "回滾計劃",
            "文檔完善",
            "測試覆蓋"
        ]
    }

    for category, items in checklist.items():
        print(f"{Fore.GREEN}{category}:{Style.RESET_ALL}")
        for item in items:
            print(f"  ☐ {item}")
        print()

    print(f"{Fore.CYAN}配置示例:{Style.RESET_ALL}\n")

    config_example = """
# 生產環境配置示例

# API 配置
API_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 1.0

# 限流配置
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_PERIOD = 60  # 秒

# 緩存配置
CACHE_ENABLED = True
CACHE_TTL = 3600  # 秒

# 日誌配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "json"
LOG_DESTINATION = "file"

# 監控配置
METRICS_ENABLED = True
METRICS_PORT = 9090

# Agent 配置
DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_TEMPERATURE = 0.7
MAX_TOKENS = 2000
"""

    print(config_example)

    print(f"{Fore.CYAN}部署注意事項:{Style.RESET_ALL}\n")
    notes = [
        "定期更新依賴套件",
        "實施 A/B 測試",
        "準備災難恢復計劃",
        "建立性能基準",
        "監控成本和使用量",
        "定期審查安全設置"
    ]

    for i, note in enumerate(notes, 1):
        print(f"  {i}. {note}")

    print()


def main():
    """主函數"""
    print(f"\n{Fore.GREEN}{'='*60}")
    print(f"  CAMEL-AI 進階技巧範例")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    print(f"{Fore.YELLOW}關於進階技巧:{Style.RESET_ALL}")
    print("掌握這些技巧可以構建生產級 Agent 系統：")
    print("1. 高級配置 - 針對不同場景優化")
    print("2. Memory 管理 - 有效管理上下文")
    print("3. 性能優化 - 提高響應速度")
    print("4. 錯誤處理 - 提高系統穩定性")
    print("5. 監控日誌 - 追蹤系統狀態")
    print("6. 生產部署 - 準備上線\n")

    try:
        example1_advanced_agent_configuration()
        example2_memory_management()
        example3_performance_optimization()
        example4_error_handling()
        example5_monitoring_and_logging()
        example6_production_deployment()

        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"  所有範例執行完成！")
        print(f"{'='*60}{Style.RESET_ALL}\n")

        print(f"{Fore.CYAN}總結:{Style.RESET_ALL}")
        print("恭喜完成所有 CAMEL-AI 範例！")
        print("\n你已經學習了：")
        print("1. CAMEL 的基本概念和快速開始")
        print("2. 角色扮演和任務分解")
        print("3. 雙 Agent 和多 Agent 協作")
        print("4. 工具整合和知識檢索")
        print("5. 代碼生成和研究助手")
        print("6. 進階技巧和生產部署\n")

        print(f"{Fore.YELLOW}下一步建議:{Style.RESET_ALL}")
        print("1. 閱讀 CAMEL 官方文檔深入學習")
        print("2. 研究 CAMEL 論文了解理論基礎")
        print("3. 參與社群討論交流經驗")
        print("4. 構建自己的 Agent 應用")
        print("5. 貢獻代碼或分享案例\n")

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}程序被用戶中斷{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}執行過程中發生錯誤: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
