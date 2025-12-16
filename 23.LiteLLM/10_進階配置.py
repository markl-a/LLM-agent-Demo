"""
LiteLLM 進階配置範例
===================

本範例展示 LiteLLM 的進階配置和使用技巧。

內容：
1. 環境變數配置
2. 自定義回調
3. 日誌配置
4. 模型別名
5. 請求參數優化

安裝依賴：
pip install litellm python-dotenv
"""

import litellm
from litellm import completion
from litellm.integrations.custom_logger import CustomLogger
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
import os
import json
import time
from datetime import datetime

# ============================================================
# 1. 環境變數配置
# ============================================================

ENV_CONFIG_EXAMPLE = '''
# .env 文件配置

# OpenAI
OPENAI_API_KEY=sk-xxx

# Anthropic
ANTHROPIC_API_KEY=sk-ant-xxx

# Azure OpenAI
AZURE_API_KEY=xxx
AZURE_API_BASE=https://your-resource.openai.azure.com/
AZURE_API_VERSION=2024-02-15-preview

# Google
GOOGLE_API_KEY=xxx

# AWS Bedrock
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_REGION_NAME=us-east-1

# LiteLLM 設置
LITELLM_LOG=DEBUG
LITELLM_TELEMETRY=False
'''

def setup_environment():
    """設置環境變數"""
    from dotenv import load_dotenv
    load_dotenv()

    # 驗證必要的 API 密鑰
    required_keys = ["OPENAI_API_KEY"]
    missing = [k for k in required_keys if not os.getenv(k)]

    if missing:
        print(f"警告: 缺少環境變數: {missing}")


# ============================================================
# 2. LiteLLM 全局配置
# ============================================================

def configure_litellm():
    """配置 LiteLLM 全局設置"""
    # 設置詳細日誌
    litellm.set_verbose = True

    # 禁用遙測
    litellm.telemetry = False

    # 設置超時
    litellm.request_timeout = 60

    # 設置重試
    litellm.num_retries = 3

    # 設置默認參數
    litellm.drop_params = True  # 自動刪除不支持的參數

    # 設置成功回調
    litellm.success_callback = ["langfuse"]  # 可選: langfuse, lunary, etc.

    # 設置失敗回調
    litellm.failure_callback = ["sentry"]


# ============================================================
# 3. 自定義回調
# ============================================================

class MyCustomLogger(CustomLogger):
    """自定義日誌記錄器"""

    def __init__(self):
        self.logs: List[Dict[str, Any]] = []

    def log_pre_api_call(self, model, messages, kwargs):
        """API 調用前"""
        print(f"\n[PRE-CALL] 模型: {model}")
        print(f"[PRE-CALL] 消息數: {len(messages)}")

    def log_post_api_call(self, kwargs, response_obj, start_time, end_time):
        """API 調用後"""
        elapsed = end_time - start_time
        print(f"[POST-CALL] 耗時: {elapsed:.2f}s")

        if hasattr(response_obj, 'usage'):
            print(f"[POST-CALL] Tokens: {response_obj.usage.total_tokens}")

    def log_stream_event(self, kwargs, response_obj, start_time, end_time):
        """流式事件"""
        pass

    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        """成功事件"""
        self.logs.append({
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "model": kwargs.get("model"),
            "elapsed": end_time - start_time
        })

    def log_failure_event(self, kwargs, response_obj, start_time, end_time):
        """失敗事件"""
        self.logs.append({
            "status": "failure",
            "timestamp": datetime.now().isoformat(),
            "model": kwargs.get("model"),
            "error": str(response_obj)
        })


def setup_custom_callbacks():
    """設置自定義回調"""
    custom_logger = MyCustomLogger()
    litellm.callbacks = [custom_logger]
    return custom_logger


# ============================================================
# 4. 模型別名配置
# ============================================================

MODEL_ALIASES = {
    # 簡化名稱
    "gpt4": "gpt-4",
    "gpt4-turbo": "gpt-4-turbo-preview",
    "gpt35": "gpt-3.5-turbo",

    # Claude 別名
    "claude-opus": "claude-3-opus-20240229",
    "claude-sonnet": "claude-3-sonnet-20240229",
    "claude-haiku": "claude-3-haiku-20240307",

    # 自定義組合
    "fast": "gpt-3.5-turbo",
    "smart": "gpt-4",
    "cheap": "claude-3-haiku-20240307",
}


class ModelAliasManager:
    """模型別名管理器"""

    def __init__(self, aliases: Dict[str, str] = None):
        self.aliases = aliases or MODEL_ALIASES.copy()

    def add_alias(self, alias: str, model: str):
        """添加別名"""
        self.aliases[alias] = model

    def resolve(self, model_or_alias: str) -> str:
        """解析模型名稱"""
        return self.aliases.get(model_or_alias, model_or_alias)

    def completion(self, model: str, messages: List[Dict], **kwargs):
        """帶別名解析的完成調用"""
        resolved_model = self.resolve(model)
        return completion(model=resolved_model, messages=messages, **kwargs)


# ============================================================
# 5. 請求配置優化
# ============================================================

@dataclass
class RequestConfig:
    """請求配置"""
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 60
    stream: bool = False


class ConfiguredClient:
    """配置化客戶端"""

    def __init__(self, default_config: RequestConfig = None):
        self.default_config = default_config or RequestConfig()

    def completion(
        self,
        model: str,
        messages: List[Dict],
        config: RequestConfig = None,
        **kwargs
    ):
        """帶配置的完成調用"""
        cfg = config or self.default_config

        return completion(
            model=model,
            messages=messages,
            temperature=kwargs.get("temperature", cfg.temperature),
            max_tokens=kwargs.get("max_tokens", cfg.max_tokens),
            top_p=kwargs.get("top_p", cfg.top_p),
            frequency_penalty=kwargs.get("frequency_penalty", cfg.frequency_penalty),
            presence_penalty=kwargs.get("presence_penalty", cfg.presence_penalty),
            timeout=kwargs.get("timeout", cfg.timeout),
            stream=kwargs.get("stream", cfg.stream),
            **{k: v for k, v in kwargs.items() if k not in [
                "temperature", "max_tokens", "top_p",
                "frequency_penalty", "presence_penalty", "timeout", "stream"
            ]}
        )


# ============================================================
# 6. 預設配置
# ============================================================

PRESETS = {
    "creative": RequestConfig(
        temperature=0.9,
        max_tokens=2000,
        top_p=0.95,
        frequency_penalty=0.5,
        presence_penalty=0.5
    ),
    "precise": RequestConfig(
        temperature=0.1,
        max_tokens=1000,
        top_p=0.1,
        frequency_penalty=0.0,
        presence_penalty=0.0
    ),
    "balanced": RequestConfig(
        temperature=0.5,
        max_tokens=1500,
        top_p=0.9,
        frequency_penalty=0.2,
        presence_penalty=0.2
    ),
    "code": RequestConfig(
        temperature=0.2,
        max_tokens=2000,
        top_p=0.1,
        frequency_penalty=0.0,
        presence_penalty=0.0
    ),
}


# ============================================================
# 7. 高級日誌配置
# ============================================================

class AdvancedLogger:
    """高級日誌記錄器"""

    def __init__(self, log_file: str = None, log_level: str = "INFO"):
        self.log_file = log_file
        self.log_level = log_level
        self.logs = []

    def log(self, level: str, message: str, data: Dict = None):
        """記錄日誌"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "data": data or {}
        }

        self.logs.append(entry)

        # 打印到控制台
        if self._should_log(level):
            print(f"[{level}] {message}")

        # 寫入文件
        if self.log_file:
            self._write_to_file(entry)

    def _should_log(self, level: str) -> bool:
        """檢查是否應記錄"""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        return levels.index(level) >= levels.index(self.log_level)

    def _write_to_file(self, entry: Dict):
        """寫入文件"""
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")


# ============================================================
# 8. 配置文件管理
# ============================================================

CONFIG_FILE_EXAMPLE = '''
{
    "default_model": "gpt-3.5-turbo",
    "fallback_models": ["claude-3-haiku", "gpt-4"],
    "request_config": {
        "temperature": 0.7,
        "max_tokens": 1000,
        "timeout": 60
    },
    "rate_limits": {
        "requests_per_minute": 60,
        "tokens_per_minute": 90000
    },
    "logging": {
        "level": "INFO",
        "file": "llm.log"
    }
}
'''


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_path: str = None):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加載配置"""
        if self.config_path and os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {}

    def save_config(self):
        """保存配置"""
        if self.config_path:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """獲取配置值"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def set(self, key: str, value: Any):
        """設置配置值"""
        keys = key.split(".")
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value


# ============================================================
# 使用範例
# ============================================================

def example_env_config():
    """範例 1: 環境變數配置"""
    print("=" * 50)
    print("範例 1: 環境變數配置")
    print("=" * 50)
    print(ENV_CONFIG_EXAMPLE)


def example_global_config():
    """範例 2: 全局配置"""
    print("\n" + "=" * 50)
    print("範例 2: LiteLLM 全局配置")
    print("=" * 50)

    print("""
# 常用全局配置
litellm.set_verbose = True      # 詳細日誌
litellm.telemetry = False       # 禁用遙測
litellm.request_timeout = 60    # 請求超時
litellm.num_retries = 3         # 重試次數
litellm.drop_params = True      # 自動刪除不支持的參數
""")


def example_custom_callbacks():
    """範例 3: 自定義回調"""
    print("\n" + "=" * 50)
    print("範例 3: 自定義回調")
    print("=" * 50)

    print("""
class MyLogger(CustomLogger):
    def log_pre_api_call(self, model, messages, kwargs):
        print(f"調用模型: {model}")

    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        print(f"成功! 耗時: {end_time - start_time:.2f}s")

litellm.callbacks = [MyLogger()]
""")


def example_model_aliases():
    """範例 4: 模型別名"""
    print("\n" + "=" * 50)
    print("範例 4: 模型別名")
    print("=" * 50)

    manager = ModelAliasManager()

    print("預設別名:")
    for alias, model in list(MODEL_ALIASES.items())[:5]:
        print(f"  {alias} -> {model}")

    # 添加自定義別名
    manager.add_alias("my-model", "gpt-4-turbo-preview")
    print(f"\n解析 'smart': {manager.resolve('smart')}")


def example_request_config():
    """範例 5: 請求配置"""
    print("\n" + "=" * 50)
    print("範例 5: 請求配置預設")
    print("=" * 50)

    for name, config in PRESETS.items():
        print(f"\n{name}:")
        print(f"  temperature: {config.temperature}")
        print(f"  max_tokens: {config.max_tokens}")
        print(f"  top_p: {config.top_p}")


def example_config_file():
    """範例 6: 配置文件"""
    print("\n" + "=" * 50)
    print("範例 6: 配置文件格式")
    print("=" * 50)
    print(CONFIG_FILE_EXAMPLE)


if __name__ == "__main__":
    print("LiteLLM 進階配置範例\n")
    example_env_config()
    example_global_config()
    example_custom_callbacks()
    example_model_aliases()
    example_request_config()
    example_config_file()
