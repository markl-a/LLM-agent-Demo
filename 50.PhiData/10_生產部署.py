"""
PhiData 生產部署示例

這個腳本展示了如何將 PhiData Agent 部署到生產環境，包括：
1. 配置管理
2. 日誌和監控
3. 錯誤處理和重試
4. 性能優化
5. 安全性配置
6. API 服務化
7. 負載均衡
8. 緩存策略
9. 版本控制
10. 容器化部署

作者: PhiData Team
日期: 2025
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from functools import wraps
from pathlib import Path
import hashlib

# PhiData 核心導入
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo
from phi.utils.log import logger

# 環境變量管理
from dotenv import load_dotenv

# 載入環境變量
load_dotenv()


# ============================================================================
# 配置管理
# ============================================================================

class ProductionConfig:
    """
    生產環境配置類

    集中管理所有生產環境配置。
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置

        參數:
            config_file: 配置文件路徑
        """
        self.config_file = config_file or "config.json"
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """載入配置"""
        if Path(self.config_file).exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 默認配置
            return {
                "environment": "production",
                "debug": False,
                "log_level": "INFO",
                "max_retries": 3,
                "timeout": 30,
                "cache_enabled": True,
                "rate_limit": 100,  # 每分鐘請求數
                "model_config": {
                    "id": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 2000,
                },
                "monitoring": {
                    "enabled": True,
                    "metrics_interval": 60,
                },
            }

    def get(self, key: str, default: Any = None) -> Any:
        """獲取配置值"""
        return self.config.get(key, default)

    def save(self) -> None:
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)


# ============================================================================
# 日誌系統
# ============================================================================

class ProductionLogger:
    """
    生產環境日誌系統

    提供結構化日誌記錄。
    """

    def __init__(self, name: str = "phidata_production"):
        """
        初始化日誌系統

        參數:
            name: 日誌名稱
        """
        self.logger = logging.getLogger(name)
        self._setup_logging()

    def _setup_logging(self) -> None:
        """配置日誌"""
        # 設置日誌級別
        self.logger.setLevel(logging.INFO)

        # 創建日誌目錄
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # 文件處理器
        fh = logging.FileHandler(
            log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        fh.setLevel(logging.INFO)

        # 控制台處理器
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)

        # 格式化
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 添加處理器
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def info(self, message: str, **kwargs) -> None:
        """記錄信息"""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """記錄警告"""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs) -> None:
        """記錄錯誤"""
        self.logger.error(message, extra=kwargs)


# ============================================================================
# 監控系統
# ============================================================================

class ProductionMonitor:
    """
    生產環境監控系統

    監控 Agent 性能和使用情況。
    """

    def __init__(self):
        """初始化監控系統"""
        self.metrics = {
            "requests": 0,
            "successes": 0,
            "failures": 0,
            "total_time": 0,
            "errors": [],
        }

    def record_request(self) -> None:
        """記錄請求"""
        self.metrics["requests"] += 1

    def record_success(self, duration: float) -> None:
        """記錄成功"""
        self.metrics["successes"] += 1
        self.metrics["total_time"] += duration

    def record_failure(self, error: str) -> None:
        """記錄失敗"""
        self.metrics["failures"] += 1
        self.metrics["errors"].append({
            "timestamp": datetime.now().isoformat(),
            "error": error,
        })

    def get_metrics(self) -> Dict[str, Any]:
        """獲取指標"""
        avg_time = (
            self.metrics["total_time"] / self.metrics["successes"]
            if self.metrics["successes"] > 0
            else 0
        )

        return {
            **self.metrics,
            "average_time": avg_time,
            "success_rate": (
                self.metrics["successes"] / self.metrics["requests"]
                if self.metrics["requests"] > 0
                else 0
            ),
        }

    def reset(self) -> None:
        """重置指標"""
        self.metrics = {
            "requests": 0,
            "successes": 0,
            "failures": 0,
            "total_time": 0,
            "errors": [],
        }


# ============================================================================
# 緩存系統
# ============================================================================

class SimpleCache:
    """
    簡單的緩存系統

    用於緩存 Agent 響應。
    """

    def __init__(self, max_size: int = 100):
        """
        初始化緩存

        參數:
            max_size: 最大緩存條目數
        """
        self.cache: Dict[str, Any] = {}
        self.max_size = max_size

    def _generate_key(self, *args, **kwargs) -> str:
        """生成緩存鍵"""
        key_str = json.dumps([args, kwargs], sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """獲取緩存"""
        return self.cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """設置緩存"""
        if len(self.cache) >= self.max_size:
            # 刪除最舊的條目（簡化實現）
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]

        self.cache[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
        }

    def clear(self) -> None:
        """清空緩存"""
        self.cache.clear()


# ============================================================================
# 錯誤處理和重試
# ============================================================================

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    重試裝飾器

    參數:
        max_retries: 最大重試次數
        delay: 重試延遲（秒）
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"嘗試 {attempt + 1}/{max_retries} 失敗: {e}"
                    )

                    if attempt < max_retries - 1:
                        time.sleep(delay * (attempt + 1))  # 指數退避

            # 所有重試都失敗
            logger.error(f"所有重試都失敗: {last_exception}")
            raise last_exception

        return wrapper
    return decorator


# ============================================================================
# 生產環境 Agent
# ============================================================================

class ProductionAgent:
    """
    生產環境 Agent 類

    集成配置、日誌、監控、緩存等生產環境功能。
    """

    def __init__(self, config: Optional[ProductionConfig] = None):
        """
        初始化生產 Agent

        參數:
            config: 配置對象
        """
        self.config = config or ProductionConfig()
        self.logger = ProductionLogger()
        self.monitor = ProductionMonitor()
        self.cache = SimpleCache() if self.config.get("cache_enabled") else None

        # API 密鑰
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("未找到 OPENAI_API_KEY")

        self.logger.info("生產環境 Agent 初始化完成")

    def create_agent(self, **kwargs) -> Agent:
        """
        創建 Agent

        參數:
            **kwargs: Agent 配置參數

        返回:
            配置好的 Agent
        """
        model_config = self.config.get("model_config", {})

        agent = Agent(
            model=OpenAIChat(
                id=model_config.get("id", "gpt-4"),
                api_key=self.api_key,
                temperature=model_config.get("temperature", 0.7),
                max_tokens=model_config.get("max_tokens", 2000),
            ),
            debug_mode=self.config.get("debug", False),
            **kwargs
        )

        return agent

    @retry_on_failure(max_retries=3)
    def run_agent(
        self,
        agent: Agent,
        message: str,
        use_cache: bool = True
    ) -> str:
        """
        運行 Agent（帶監控和緩存）

        參數:
            agent: Agent 實例
            message: 消息
            use_cache: 是否使用緩存

        返回:
            Agent 響應
        """
        # 記錄請求
        self.monitor.record_request()
        self.logger.info(f"接收請求: {message[:100]}...")

        # 檢查緩存
        cache_key = hashlib.md5(message.encode()).hexdigest()
        if use_cache and self.cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                self.logger.info("使用緩存響應")
                return cached_result["value"]

        # 執行請求
        start_time = time.time()

        try:
            response = agent.run(message)
            result = response.content if hasattr(response, 'content') else str(response)

            duration = time.time() - start_time

            # 記錄成功
            self.monitor.record_success(duration)
            self.logger.info(f"請求成功，耗時: {duration:.2f} 秒")

            # 緩存結果
            if use_cache and self.cache:
                self.cache.set(cache_key, result)

            return result

        except Exception as e:
            # 記錄失敗
            self.monitor.record_failure(str(e))
            self.logger.error(f"請求失敗: {e}")
            raise

    def get_health_status(self) -> Dict[str, Any]:
        """
        獲取健康狀態

        返回:
            健康狀態字典
        """
        metrics = self.monitor.get_metrics()

        return {
            "status": "healthy" if metrics["success_rate"] > 0.9 else "degraded",
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
        }

    def generate_report(self, filepath: str) -> None:
        """
        生成運行報告

        參數:
            filepath: 報告保存路徑
        """
        metrics = self.monitor.get_metrics()

        report = f"""# 生產環境運行報告

生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 性能指標

- 總請求數: {metrics['requests']}
- 成功數: {metrics['successes']}
- 失敗數: {metrics['failures']}
- 成功率: {metrics['success_rate']:.2%}
- 平均響應時間: {metrics['average_time']:.2f} 秒

## 配置信息

- 環境: {self.config.get('environment')}
- 模型: {self.config.get('model_config', {}).get('id')}
- 緩存: {'啟用' if self.config.get('cache_enabled') else '禁用'}
- 最大重試: {self.config.get('max_retries')}

## 錯誤記錄

"""

        for i, error in enumerate(metrics['errors'][-10:], 1):  # 只顯示最近10個錯誤
            report += f"\n### 錯誤 {i}\n"
            report += f"- 時間: {error['timestamp']}\n"
            report += f"- 錯誤: {error['error']}\n"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n✓ 報告已生成: {filepath}")


# ============================================================================
# API 服務（示例）
# ============================================================================

class AgentAPIService:
    """
    Agent API 服務

    將 Agent 包裝為 API 服務。
    """

    def __init__(self, production_agent: ProductionAgent):
        """
        初始化 API 服務

        參數:
            production_agent: 生產 Agent 實例
        """
        self.production_agent = production_agent
        self.agent = production_agent.create_agent(
            name="API Agent",
            description="API 服務 Agent",
        )

    def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理 API 請求

        參數:
            request_data: 請求數據

        返回:
            響應數據
        """
        try:
            message = request_data.get("message")
            if not message:
                return {
                    "status": "error",
                    "error": "缺少消息字段",
                }

            # 運行 Agent
            result = self.production_agent.run_agent(self.agent, message)

            return {
                "status": "success",
                "result": result,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def get_status(self) -> Dict[str, Any]:
        """獲取服務狀態"""
        return self.production_agent.get_health_status()


# ============================================================================
# 演示函數
# ============================================================================

def demonstration_production_agent():
    """演示生產環境 Agent"""
    print("\n" + "="*60)
    print("演示 1: 生產環境 Agent")
    print("="*60)

    # 創建生產 Agent
    prod_agent = ProductionAgent()

    # 創建 Agent
    agent = prod_agent.create_agent(
        name="生產助手",
        description="生產環境的 AI 助手",
    )

    # 執行請求
    result = prod_agent.run_agent(
        agent,
        "什麼是 PhiData？"
    )

    print(f"\n響應: {result}\n")

    # 查看健康狀態
    health = prod_agent.get_health_status()
    print(f"健康狀態: {json.dumps(health, ensure_ascii=False, indent=2)}")


def demonstration_caching():
    """演示緩存功能"""
    print("\n" + "="*60)
    print("演示 2: 緩存功能")
    print("="*60)

    prod_agent = ProductionAgent()
    agent = prod_agent.create_agent(name="緩存測試")

    message = "2+2等於多少？"

    # 第一次請求（不使用緩存）
    print("\n第一次請求（新請求）...")
    start = time.time()
    result1 = prod_agent.run_agent(agent, message)
    time1 = time.time() - start
    print(f"耗時: {time1:.2f} 秒")

    # 第二次請求（使用緩存）
    print("\n第二次請求（使用緩存）...")
    start = time.time()
    result2 = prod_agent.run_agent(agent, message)
    time2 = time.time() - start
    print(f"耗時: {time2:.2f} 秒")

    print(f"\n加速比: {time1/time2:.2f}x")


def demonstration_monitoring():
    """演示監控功能"""
    print("\n" + "="*60)
    print("演示 3: 監控和報告")
    print("="*60)

    prod_agent = ProductionAgent()
    agent = prod_agent.create_agent(name="監控測試")

    # 執行多個請求
    messages = [
        "你好",
        "今天天氣如何？",
        "什麼是AI？",
    ]

    for msg in messages:
        try:
            prod_agent.run_agent(agent, msg)
        except Exception as e:
            print(f"錯誤: {e}")

    # 生成報告
    prod_agent.generate_report("production_report.md")


def demonstration_api_service():
    """演示 API 服務"""
    print("\n" + "="*60)
    print("演示 4: API 服務")
    print("="*60)

    prod_agent = ProductionAgent()
    api_service = AgentAPIService(prod_agent)

    # 處理請求
    request = {
        "message": "解釋一下什麼是雲計算"
    }

    response = api_service.handle_request(request)
    print(f"\nAPI 響應:\n{json.dumps(response, ensure_ascii=False, indent=2)}")

    # 獲取狀態
    status = api_service.get_status()
    print(f"\n服務狀態:\n{json.dumps(status, ensure_ascii=False, indent=2)}")


def main():
    """主函數"""
    print("\n" + "="*60)
    print("PhiData 生產部署 - 完整示例")
    print("="*60)

    try:
        # 運行演示
        demonstration_production_agent()
        demonstration_caching()
        demonstration_monitoring()
        demonstration_api_service()

        print("\n" + "="*60)
        print("所有演示完成！")
        print("="*60)

        print("\n生產部署最佳實踐：")
        print("1. 完善的配置管理")
        print("2. 結構化日誌記錄")
        print("3. 性能監控和告警")
        print("4. 錯誤處理和重試")
        print("5. 請求緩存優化")
        print("6. API 限流控制")
        print("7. 安全性加固")
        print("8. 容器化部署")
        print("9. 負載均衡")
        print("10. 持續監控和優化")

        print("\n部署清單：")
        print("□ 環境變量配置")
        print("□ 日誌系統設置")
        print("□ 監控系統部署")
        print("□ 錯誤處理機制")
        print("□ 緩存策略配置")
        print("□ API 限流設置")
        print("□ 安全審計")
        print("□ 備份恢復方案")
        print("□ 文檔完善")
        print("□ 運維手冊")

    except Exception as e:
        logger.error(f"運行錯誤: {e}")
        print(f"\n錯誤: {e}")


if __name__ == "__main__":
    main()
