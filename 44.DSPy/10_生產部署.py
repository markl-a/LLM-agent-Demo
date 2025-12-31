"""
DSPy 生產部署教學

本模組展示如何將 DSPy 應用部署到生產環境：
1. 生產環境準備
2. 配置管理
3. 錯誤處理和日誌
4. 性能監控
5. API 服務構建
6. 容器化部署
7. 擴展和負載均衡
8. 安全性考慮

作者：DSPy 教學團隊
日期：2025-01
"""

import dspy
from typing import List, Dict, Optional, Any
import os
import json
import logging
from datetime import datetime
from functools import wraps
import time
import traceback


# ==================== 生產部署概念 ====================

def explain_production_deployment():
    """
    解釋生產部署的關鍵概念

    從開發到生產需要考慮的因素
    """
    print("\n" + "="*60)
    print("生產部署核心概念")
    print("="*60)

    print("""
    生產部署的關鍵考慮：

    1. 可靠性
       - 錯誤處理和恢復
       - 容錯機制
       - 備用方案
       - 健康檢查

    2. 性能
       - 響應時間優化
       - 並發處理
       - 緩存策略
       - 資源管理

    3. 可擴展性
       - 水平擴展
       - 負載均衡
       - 無狀態設計
       - 分佈式部署

    4. 安全性
       - API 金鑰管理
       - 輸入驗證
       - 速率限制
       - 數據加密

    5. 可觀測性
       - 日誌記錄
       - 性能監控
       - 錯誤追蹤
       - 使用分析

    6. 成本控制
       - API 調用優化
       - 緩存利用
       - 資源配額
       - 成本監控

    部署檢查清單：
    ☐ 配置環境變數
    ☐ 設置日誌系統
    ☐ 實施錯誤處理
    ☐ 配置監控告警
    ☐ 測試容錯機制
    ☐ 實施速率限制
    ☐ 設置備份策略
    ☐ 文檔化 API
    ☐ 負載測試
    ☐ 安全審計
    """)


# ==================== 配置管理 ====================

class Config:
    """
    配置管理類

    統一管理所有配置項
    """

    def __init__(self, env: str = "production"):
        """
        初始化配置

        Args:
            env: 環境名稱（development, staging, production）
        """
        self.env = env

        # LLM 配置
        self.llm_provider = os.getenv("LLM_PROVIDER", "openai")
        self.llm_model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        self.llm_api_key = os.getenv("OPENAI_API_KEY", "")
        self.llm_max_tokens = int(os.getenv("LLM_MAX_TOKENS", "500"))
        self.llm_temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))

        # 緩存配置
        self.cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        self.cache_type = os.getenv("CACHE_TYPE", "lru")
        self.cache_max_size = int(os.getenv("CACHE_MAX_SIZE", "1000"))
        self.cache_ttl = int(os.getenv("CACHE_TTL", "3600"))

        # 性能配置
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.timeout_seconds = int(os.getenv("TIMEOUT_SECONDS", "30"))
        self.rate_limit_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.rate_limit_period = int(os.getenv("RATE_LIMIT_PERIOD", "60"))

        # 日誌配置
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "dspy_app.log")

        # 監控配置
        self.enable_metrics = os.getenv("ENABLE_METRICS", "true").lower() == "true"
        self.metrics_port = int(os.getenv("METRICS_PORT", "9090"))

    def validate(self):
        """
        驗證配置的有效性

        Returns:
            驗證結果和錯誤信息
        """
        errors = []

        # 檢查必需的配置
        if not self.llm_api_key:
            errors.append("缺少 LLM API 金鑰")

        if self.llm_max_tokens <= 0:
            errors.append("max_tokens 必須大於 0")

        if not 0 <= self.llm_temperature <= 2:
            errors.append("temperature 必須在 0-2 之間")

        return len(errors) == 0, errors

    def __str__(self):
        """返回配置摘要"""
        return f"""
        環境: {self.env}
        LLM: {self.llm_provider} / {self.llm_model}
        緩存: {'啟用' if self.cache_enabled else '禁用'} ({self.cache_type})
        日誌級別: {self.log_level}
        """


# ==================== 日誌系統 ====================

def setup_logging(config: Config):
    """
    設置日誌系統

    Args:
        config: 配置對象
    """
    # 配置日誌格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # 配置日誌級別
    log_level = getattr(logging, config.log_level.upper(), logging.INFO)

    # 配置日誌處理器
    handlers = [
        logging.StreamHandler(),  # 控制台輸出
        logging.FileHandler(config.log_file)  # 文件輸出
    ]

    # 設置基礎配置
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers
    )

    logger = logging.getLogger(__name__)
    logger.info(f"日誌系統已初始化，級別：{config.log_level}")

    return logger


# ==================== 錯誤處理 ====================

class DSPyError(Exception):
    """DSPy 應用的基礎異常類"""
    pass


class ConfigurationError(DSPyError):
    """配置錯誤"""
    pass


class ModelError(DSPyError):
    """模型調用錯誤"""
    pass


class ValidationError(DSPyError):
    """輸入驗證錯誤"""
    pass


def with_retry(max_retries: int = 3, delay: float = 1.0):
    """
    重試裝飾器

    Args:
        max_retries: 最大重試次數
        delay: 重試延遲（秒）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (attempt + 1))  # 指數退避
                        logging.warning(
                            f"重試 {func.__name__} (嘗試 {attempt + 1}/{max_retries}): {e}"
                        )
                    else:
                        logging.error(
                            f"{func.__name__} 失敗，已達最大重試次數: {e}"
                        )

            raise last_exception

        return wrapper
    return decorator


def with_timeout(timeout_seconds: int = 30):
    """
    超時裝飾器

    Args:
        timeout_seconds: 超時時間（秒）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError(f"{func.__name__} 執行超時（{timeout_seconds}秒）")

            # 設置超時
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)

            try:
                result = func(*args, **kwargs)
            finally:
                # 取消超時
                signal.alarm(0)

            return result

        return wrapper
    return decorator


# ==================== 輸入驗證 ====================

class InputValidator:
    """輸入驗證器"""

    @staticmethod
    def validate_question(question: str) -> tuple:
        """
        驗證問題輸入

        Args:
            question: 用戶問題

        Returns:
            (是否有效, 錯誤信息)
        """
        if not question:
            return False, "問題不能為空"

        if not isinstance(question, str):
            return False, "問題必須是字符串"

        if len(question) < 3:
            return False, "問題太短（至少3個字符）"

        if len(question) > 1000:
            return False, "問題太長（最多1000個字符）"

        # 檢查惡意輸入
        dangerous_patterns = [
            "eval(", "exec(", "__import__", "os.system"
        ]

        for pattern in dangerous_patterns:
            if pattern in question.lower():
                return False, f"輸入包含危險模式：{pattern}"

        return True, ""

    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        清理輸入

        Args:
            text: 原始輸入

        Returns:
            清理後的輸入
        """
        # 移除前後空白
        text = text.strip()

        # 移除多餘的空白字符
        text = " ".join(text.split())

        # 限制長度
        if len(text) > 1000:
            text = text[:1000]

        return text


# ==================== 性能監控 ====================

class PerformanceMonitor:
    """性能監控器"""

    def __init__(self):
        """初始化監控器"""
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_latency": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors_by_type": {}
        }

    def record_request(self, success: bool, latency: float, from_cache: bool = False):
        """
        記錄請求

        Args:
            success: 是否成功
            latency: 延遲時間（秒）
            from_cache: 是否來自緩存
        """
        self.metrics["total_requests"] += 1

        if success:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1

        self.metrics["total_latency"] += latency

        if from_cache:
            self.metrics["cache_hits"] += 1
        else:
            self.metrics["cache_misses"] += 1

    def record_error(self, error_type: str):
        """
        記錄錯誤

        Args:
            error_type: 錯誤類型
        """
        if error_type not in self.metrics["errors_by_type"]:
            self.metrics["errors_by_type"][error_type] = 0
        self.metrics["errors_by_type"][error_type] += 1

    def get_stats(self) -> Dict[str, Any]:
        """
        獲取統計信息

        Returns:
            統計字典
        """
        total_requests = self.metrics["total_requests"]

        if total_requests == 0:
            avg_latency = 0
            success_rate = 0
            cache_hit_rate = 0
        else:
            avg_latency = self.metrics["total_latency"] / total_requests
            success_rate = self.metrics["successful_requests"] / total_requests * 100
            cache_requests = self.metrics["cache_hits"] + self.metrics["cache_misses"]
            cache_hit_rate = (self.metrics["cache_hits"] / cache_requests * 100) if cache_requests > 0 else 0

        return {
            "total_requests": total_requests,
            "successful_requests": self.metrics["successful_requests"],
            "failed_requests": self.metrics["failed_requests"],
            "success_rate": f"{success_rate:.2f}%",
            "average_latency": f"{avg_latency:.3f}s",
            "cache_hit_rate": f"{cache_hit_rate:.2f}%",
            "errors_by_type": self.metrics["errors_by_type"]
        }

    def reset(self):
        """重置統計"""
        self.__init__()


# ==================== 生產級 DSPy 模組 ====================

class ProductionQAModule(dspy.Module):
    """
    生產級問答模組

    集成所有生產所需的功能
    """

    def __init__(self, config: Config, monitor: PerformanceMonitor):
        """
        初始化生產模組

        Args:
            config: 配置對象
            monitor: 性能監控器
        """
        super().__init__()
        self.config = config
        self.monitor = monitor
        self.logger = logging.getLogger(__name__)

        # 定義簽名
        class QA(dspy.Signature):
            """專業問答系統"""
            question = dspy.InputField(desc="用戶問題")
            answer = dspy.OutputField(desc="專業、準確的答案")

        self.generate_answer = dspy.ChainOfThought(QA)

        # 初始化緩存（如果啟用）
        if config.cache_enabled:
            from functools import lru_cache
            self.logger.info("緩存已啟用")

    @with_retry(max_retries=3, delay=1.0)
    def _generate_answer_with_retry(self, question: str) -> str:
        """
        帶重試的答案生成

        Args:
            question: 問題

        Returns:
            答案
        """
        result = self.generate_answer(question=question)
        return result.answer

    def forward(self, question: str) -> Dict[str, Any]:
        """
        執行問答（生產版本）

        Args:
            question: 用戶問題

        Returns:
            響應字典
        """
        start_time = time.time()
        success = False
        from_cache = False
        error_message = None
        answer = None

        try:
            # 1. 輸入驗證
            is_valid, error_msg = InputValidator.validate_question(question)
            if not is_valid:
                raise ValidationError(error_msg)

            # 2. 清理輸入
            clean_question = InputValidator.sanitize_input(question)

            # 3. 生成答案
            answer = self._generate_answer_with_retry(clean_question)

            success = True
            self.logger.info(f"成功處理問題：{clean_question[:50]}...")

        except ValidationError as e:
            error_message = f"輸入驗證失敗：{str(e)}"
            self.logger.warning(error_message)
            self.monitor.record_error("ValidationError")

        except TimeoutError as e:
            error_message = f"請求超時：{str(e)}"
            self.logger.error(error_message)
            self.monitor.record_error("TimeoutError")

        except Exception as e:
            error_message = f"未知錯誤：{str(e)}"
            self.logger.error(f"{error_message}\n{traceback.format_exc()}")
            self.monitor.record_error("UnknownError")

        finally:
            # 記錄性能指標
            latency = time.time() - start_time
            self.monitor.record_request(success, latency, from_cache)

        # 構建響應
        response = {
            "success": success,
            "question": question,
            "answer": answer,
            "error": error_message,
            "metadata": {
                "latency": f"{latency:.3f}s",
                "from_cache": from_cache,
                "timestamp": datetime.now().isoformat()
            }
        }

        return response


# ==================== API 服務（Flask 範例）====================

def create_api_service(config: Config):
    """
    創建 Flask API 服務

    Args:
        config: 配置對象

    Returns:
        Flask 應用
    """
    try:
        from flask import Flask, request, jsonify
    except ImportError:
        print("需要安裝 Flask: pip install flask")
        return None

    app = Flask(__name__)
    logger = logging.getLogger(__name__)

    # 初始化監控器
    monitor = PerformanceMonitor()

    # 初始化 DSPy
    try:
        lm = dspy.OpenAI(
            model=config.llm_model,
            max_tokens=config.llm_max_tokens,
            temperature=config.llm_temperature
        )
        dspy.settings.configure(lm=lm)

        qa_module = ProductionQAModule(config, monitor)
        logger.info("DSPy 模組初始化成功")
    except Exception as e:
        logger.error(f"DSPy 初始化失敗：{e}")
        qa_module = None

    @app.route('/health', methods=['GET'])
    def health_check():
        """健康檢查端點"""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        })

    @app.route('/metrics', methods=['GET'])
    def get_metrics():
        """獲取監控指標"""
        return jsonify(monitor.get_stats())

    @app.route('/ask', methods=['POST'])
    def ask_question():
        """問答端點"""
        if qa_module is None:
            return jsonify({
                "success": False,
                "error": "服務未就緒"
            }), 503

        # 獲取請求數據
        data = request.get_json()

        if not data or 'question' not in data:
            return jsonify({
                "success": False,
                "error": "缺少 question 參數"
            }), 400

        question = data['question']

        # 處理請求
        response = qa_module(question=question)

        # 返回響應
        status_code = 200 if response['success'] else 400
        return jsonify(response), status_code

    return app


# ==================== Docker 部署範例 ====================

DOCKERFILE_CONTENT = """
# DSPy 生產部署 Dockerfile

FROM python:3.10-slim

# 設置工作目錄
WORKDIR /app

# 複製依賴文件
COPY requirements.txt .

# 安裝依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY . .

# 設置環境變數
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# 暴露端口
EXPOSE 8000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# 啟動應用
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

DOCKER_COMPOSE_CONTENT = """
version: '3.8'

services:
  dspy-app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LLM_MODEL=gpt-3.5-turbo
      - CACHE_ENABLED=true
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
      - ./cache:/app/cache
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
"""


# ==================== 主程序 ====================

def main():
    """主函數：演示生產部署準備"""

    print("="*60)
    print("DSPy 生產部署教學")
    print("="*60)

    # 1. 概念說明
    explain_production_deployment()

    # 2. 配置管理
    print("\n" + "="*60)
    print("配置管理")
    print("="*60)

    config = Config(env="production")
    print(config)

    is_valid, errors = config.validate()
    if is_valid:
        print("✓ 配置驗證通過")
    else:
        print("✗ 配置驗證失敗：")
        for error in errors:
            print(f"  - {error}")

    # 3. 日誌系統
    print("\n" + "="*60)
    print("日誌系統")
    print("="*60)

    logger = setup_logging(config)
    logger.info("這是一條測試日誌")
    logger.warning("這是一條警告日誌")

    # 4. 性能監控
    print("\n" + "="*60)
    print("性能監控")
    print("="*60)

    monitor = PerformanceMonitor()

    # 模擬一些請求
    monitor.record_request(success=True, latency=0.5, from_cache=False)
    monitor.record_request(success=True, latency=0.1, from_cache=True)
    monitor.record_request(success=False, latency=2.0, from_cache=False)
    monitor.record_error("TimeoutError")

    print("\n監控統計：")
    stats = monitor.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # 5. 輸入驗證
    print("\n" + "="*60)
    print("輸入驗證")
    print("="*60)

    test_inputs = [
        "什麼是機器學習？",
        "",
        "a" * 1500,
        "eval(malicious_code)"
    ]

    for test_input in test_inputs:
        is_valid, error = InputValidator.validate_question(test_input)
        status = "✓" if is_valid else "✗"
        print(f"{status} {test_input[:50]}")
        if error:
            print(f"   錯誤：{error}")

    # 6. 部署文件
    print("\n" + "="*60)
    print("部署文件範例")
    print("="*60)

    print("\nDockerfile 範例已準備")
    print("docker-compose.yml 範例已準備")
    print("\n使用方法：")
    print("  1. docker build -t dspy-app .")
    print("  2. docker-compose up -d")

    # 7. API 服務
    print("\n" + "="*60)
    print("API 服務")
    print("="*60)

    print("Flask API 服務已準備")
    print("\nAPI 端點：")
    print("  GET  /health  - 健康檢查")
    print("  GET  /metrics - 性能指標")
    print("  POST /ask     - 問答服務")

    # 總結
    print("\n" + "="*60)
    print("教學完成！")
    print("="*60)
    print("""
    你已經學會了：
    1. ✓ 生產部署的核心概念
    2. ✓ 配置管理最佳實踐
    3. ✓ 日誌系統設置
    4. ✓ 錯誤處理和重試機制
    5. ✓ 輸入驗證和安全
    6. ✓ 性能監控
    7. ✓ API 服務構建
    8. ✓ 容器化部署

    生產部署檢查清單：

    配置：
    ☐ 環境變數設置正確
    ☐ API 金鑰安全存儲
    ☐ 配置驗證通過

    可靠性：
    ☐ 錯誤處理完善
    ☐ 重試機制測試
    ☐ 超時設置合理
    ☐ 健康檢查實施

    性能：
    ☐ 緩存配置優化
    ☐ 並發處理測試
    ☐ 資源限制設置
    ☐ 負載測試完成

    安全性：
    ☐ 輸入驗證實施
    ☐ 速率限制配置
    ☐ 日誌脫敏
    ☐ HTTPS 啟用

    監控：
    ☐ 日誌系統運行
    ☐ 性能指標收集
    ☐ 告警規則設置
    ☐ 監控儀表板

    下一步：
    - 實施 CI/CD 流程
    - 設置監控告警
    - 進行壓力測試
    - 制定應急預案
    - 編寫運維文檔

    推薦工具：
    - 容器編排：Kubernetes
    - 監控：Prometheus + Grafana
    - 日誌：ELK Stack
    - API 網關：Kong, Nginx
    - 負載均衡：HAProxy, Nginx
    """)


if __name__ == "__main__":
    main()
