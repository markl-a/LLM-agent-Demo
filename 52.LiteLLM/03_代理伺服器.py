"""
LiteLLM 代理伺服器範例

這個檔案展示如何設定和使用 LiteLLM 代理伺服器（Proxy Server）：
1. 基本的代理伺服器設定
2. 配置檔案管理
3. 虛擬金鑰（Virtual Keys）
4. 使用者認證和授權
5. 速率限制
6. 負載均衡配置
7. 日誌和監控
8. 健康檢查
9. 多租戶支援
10. 生產環境部署

代理伺服器模式特別適合企業級應用，提供集中管理和進階功能。
"""

import os
import yaml
import json
from typing import Dict, List, Any, Optional
import subprocess
import time
import requests
from pathlib import Path
import signal


# ============================================================================
# 第一部分：基本配置
# ============================================================================

def create_basic_config():
    """
    建立基本的代理伺服器配置檔案

    這是最簡單的配置，包含幾個常用的模型。
    """
    print("=" * 80)
    print("建立基本配置檔案")
    print("=" * 80)

    config = {
        "model_list": [
            {
                "model_name": "gpt-4",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "os.environ/OPENAI_API_KEY"
                }
            },
            {
                "model_name": "gpt-3.5",
                "litellm_params": {
                    "model": "gpt-3.5-turbo",
                    "api_key": "os.environ/OPENAI_API_KEY"
                }
            },
            {
                "model_name": "claude",
                "litellm_params": {
                    "model": "claude-3-5-sonnet-20241022",
                    "api_key": "os.environ/ANTHROPIC_API_KEY"
                }
            }
        ]
    }

    # 儲存配置檔案
    config_path = "litellm_config_basic.yaml"
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    print(f"✓ 配置檔案已建立：{config_path}")
    print("\n配置內容：")
    print(yaml.dump(config, default_flow_style=False, allow_unicode=True))

    return config_path


def create_advanced_config():
    """
    建立進階的代理伺服器配置檔案

    包含更多進階功能：
    - 多個供應商
    - 虛擬金鑰
    - 速率限制
    - 預算控制
    - 日誌設定
    """
    print("\n" + "=" * 80)
    print("建立進階配置檔案")
    print("=" * 80)

    config = {
        # 環境變數設定
        "environment_variables": {
            "OPENAI_API_KEY": "your-openai-key",
            "ANTHROPIC_API_KEY": "your-anthropic-key"
        },

        # 模型列表
        "model_list": [
            # OpenAI 模型
            {
                "model_name": "gpt-4",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "os.environ/OPENAI_API_KEY"
                },
                "model_info": {
                    "id": "gpt-4-001",
                    "mode": "chat",
                    "supports_function_calling": True
                }
            },
            {
                "model_name": "gpt-3.5",
                "litellm_params": {
                    "model": "gpt-3.5-turbo",
                    "api_key": "os.environ/OPENAI_API_KEY"
                }
            },

            # Anthropic Claude 模型
            {
                "model_name": "claude-sonnet",
                "litellm_params": {
                    "model": "claude-3-5-sonnet-20241022",
                    "api_key": "os.environ/ANTHROPIC_API_KEY"
                }
            },
            {
                "model_name": "claude-haiku",
                "litellm_params": {
                    "model": "claude-3-haiku-20240307",
                    "api_key": "os.environ/ANTHROPIC_API_KEY"
                }
            },

            # AWS Bedrock 模型
            {
                "model_name": "bedrock-claude",
                "litellm_params": {
                    "model": "bedrock/anthropic.claude-3-sonnet-20240229-v1:0",
                    "aws_region_name": "us-east-1"
                }
            }
        ],

        # LiteLLM 設定
        "litellm_settings": {
            # 成功回調
            "success_callback": ["langfuse"],
            # 失敗回調
            "failure_callback": ["sentry"],
            # 快取設定
            "cache": True,
            "cache_params": {
                "type": "redis",
                "host": "localhost",
                "port": 6379
            },
            # 預設的 request timeout
            "request_timeout": 600,
            # 重試次數
            "num_retries": 3,
            # 日誌等級
            "set_verbose": True
        },

        # 一般設定
        "general_settings": {
            # 主密鑰（用於管理端點）
            "master_key": "sk-1234",
            # 資料庫 URL（用於儲存虛擬金鑰等）
            "database_url": "postgresql://user:password@localhost:5432/litellm",
            # 啟用虛擬金鑰
            "store_model_in_db": True
        },

        # 路由器設定
        "router_settings": {
            # 路由策略
            "routing_strategy": "least-busy",
            # 允許的失敗次數
            "allowed_fails": 3,
            # 冷卻時間（秒）
            "cooldown_time": 30
        }
    }

    # 儲存配置檔案
    config_path = "litellm_config_advanced.yaml"
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    print(f"✓ 進階配置檔案已建立：{config_path}")
    print("\n主要功能：")
    print("  - 多供應商模型支援")
    print("  - Redis 快取")
    print("  - 日誌和監控整合")
    print("  - 路由策略配置")
    print("  - 資料庫整合")

    return config_path


# ============================================================================
# 第二部分：啟動和管理代理伺服器
# ============================================================================

class ProxyServerManager:
    """代理伺服器管理類別"""

    def __init__(self, config_path: str, port: int = 4000):
        self.config_path = config_path
        self.port = port
        self.process = None
        self.base_url = f"http://localhost:{port}"

    def start(self):
        """啟動代理伺服器"""
        print("\n" + "=" * 80)
        print(f"啟動代理伺服器（埠號：{self.port}）")
        print("=" * 80)

        # 構建啟動命令
        cmd = [
            "litellm",
            "--config", self.config_path,
            "--port", str(self.port),
            "--detailed_debug"
        ]

        print(f"\n執行命令：{' '.join(cmd)}")

        try:
            # 啟動伺服器進程
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            print(f"✓ 代理伺服器已啟動（PID: {self.process.pid}）")
            print(f"✓ 服務地址：{self.base_url}")
            print("\n等待伺服器就緒...")
            time.sleep(5)

            # 檢查伺服器狀態
            if self.is_healthy():
                print("✓ 伺服器就緒！")
                return True
            else:
                print("✗ 伺服器啟動失敗")
                return False

        except Exception as e:
            print(f"✗ 啟動失敗：{e}")
            return False

    def stop(self):
        """停止代理伺服器"""
        if self.process:
            print(f"\n停止代理伺服器（PID: {self.process.pid}）...")
            self.process.terminate()
            self.process.wait()
            print("✓ 伺服器已停止")

    def is_healthy(self) -> bool:
        """檢查伺服器健康狀態"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_models(self) -> List[str]:
        """取得可用的模型列表"""
        try:
            response = requests.get(f"{self.base_url}/models")
            if response.status_code == 200:
                data = response.json()
                return [model['id'] for model in data.get('data', [])]
        except Exception as e:
            print(f"錯誤：{e}")
        return []


def proxy_server_example():
    """代理伺服器使用範例"""
    print("\n" + "=" * 80)
    print("代理伺服器使用範例")
    print("=" * 80)

    # 建立配置檔案
    config_path = create_basic_config()

    print("\n" + "=" * 80)
    print("啟動說明")
    print("=" * 80)
    print("\n在終端機執行以下命令來啟動代理伺服器：")
    print(f"\n  litellm --config {config_path} --port 4000")
    print("\n伺服器啟動後，您可以使用標準的 OpenAI SDK 來呼叫它：")

    # 用戶端範例程式碼
    client_code = """
import openai

# 設定代理伺服器
client = openai.OpenAI(
    api_key="sk-1234",  # 代理伺服器的 API 金鑰
    base_url="http://localhost:4000"
)

# 使用標準 OpenAI SDK
response = client.chat.completions.create(
    model="gpt-4",  # 使用配置檔中定義的模型名稱
    messages=[
        {"role": "user", "content": "你好！"}
    ]
)

print(response.choices[0].message.content)
"""

    print("\nPython 用戶端範例：")
    print("-" * 40)
    print(client_code)


# ============================================================================
# 第三部分：虛擬金鑰管理
# ============================================================================

def create_virtual_keys_config():
    """
    建立支援虛擬金鑰的配置

    虛擬金鑰允許您為不同的使用者或應用程式建立獨立的 API 金鑰，
    並為每個金鑰設定不同的權限、配額和預算。
    """
    print("\n" + "=" * 80)
    print("虛擬金鑰配置")
    print("=" * 80)

    config = {
        "model_list": [
            {
                "model_name": "gpt-4",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "os.environ/OPENAI_API_KEY"
                }
            }
        ],

        "general_settings": {
            # 主密鑰（用於管理 API）
            "master_key": "sk-master-1234",

            # 資料庫配置（用於儲存虛擬金鑰）
            "database_url": "postgresql://user:password@localhost:5432/litellm",

            # 啟用虛擬金鑰功能
            "store_model_in_db": True
        }
    }

    config_path = "litellm_config_virtual_keys.yaml"
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    print(f"✓ 虛擬金鑰配置已建立：{config_path}")

    return config_path


class VirtualKeyManager:
    """虛擬金鑰管理器"""

    def __init__(self, base_url: str, master_key: str):
        self.base_url = base_url
        self.master_key = master_key
        self.headers = {
            "Authorization": f"Bearer {master_key}",
            "Content-Type": "application/json"
        }

    def create_key(
        self,
        key_name: str,
        models: List[str],
        max_budget: Optional[float] = None,
        budget_duration: Optional[str] = None,
        max_parallel_requests: Optional[int] = None,
        tpm_limit: Optional[int] = None,
        rpm_limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        建立虛擬金鑰

        Args:
            key_name: 金鑰名稱
            models: 允許的模型列表
            max_budget: 最大預算（美元）
            budget_duration: 預算週期（例如："30d", "1mo"）
            max_parallel_requests: 最大並行請求數
            tpm_limit: Tokens Per Minute 限制
            rpm_limit: Requests Per Minute 限制
        """
        print(f"\n建立虛擬金鑰：{key_name}")
        print("-" * 40)

        payload = {
            "key_name": key_name,
            "models": models
        }

        if max_budget:
            payload["max_budget"] = max_budget
        if budget_duration:
            payload["budget_duration"] = budget_duration
        if max_parallel_requests:
            payload["max_parallel_requests"] = max_parallel_requests
        if tpm_limit:
            payload["tpm_limit"] = tpm_limit
        if rpm_limit:
            payload["rpm_limit"] = rpm_limit

        try:
            response = requests.post(
                f"{self.base_url}/key/generate",
                headers=self.headers,
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✓ 金鑰已建立")
                print(f"  金鑰：{data.get('key', 'N/A')}")
                print(f"  模型：{', '.join(models)}")
                if max_budget:
                    print(f"  預算：${max_budget}/{budget_duration}")
                return data
            else:
                print(f"✗ 建立失敗：{response.text}")
                return {}

        except Exception as e:
            print(f"✗ 錯誤：{e}")
            return {}

    def list_keys(self) -> List[Dict[str, Any]]:
        """列出所有虛擬金鑰"""
        print("\n列出所有虛擬金鑰")
        print("-" * 40)

        try:
            response = requests.get(
                f"{self.base_url}/key/info",
                headers=self.headers
            )

            if response.status_code == 200:
                keys = response.json().get('keys', [])
                for i, key in enumerate(keys, 1):
                    print(f"{i}. {key.get('key_name', 'Unknown')}")
                    print(f"   金鑰：{key.get('key', 'N/A')[:20]}...")
                    print(f"   模型：{', '.join(key.get('models', []))}")
                return keys
            else:
                print(f"✗ 取得失敗：{response.text}")
                return []

        except Exception as e:
            print(f"✗ 錯誤：{e}")
            return []

    def delete_key(self, key: str):
        """刪除虛擬金鑰"""
        print(f"\n刪除虛擬金鑰：{key[:20]}...")
        print("-" * 40)

        try:
            response = requests.post(
                f"{self.base_url}/key/delete",
                headers=self.headers,
                json={"keys": [key]}
            )

            if response.status_code == 200:
                print("✓ 金鑰已刪除")
            else:
                print(f"✗ 刪除失敗：{response.text}")

        except Exception as e:
            print(f"✗ 錯誤：{e}")


def virtual_keys_example():
    """虛擬金鑰使用範例"""
    print("\n" + "=" * 80)
    print("虛擬金鑰使用範例")
    print("=" * 80)

    base_url = "http://localhost:4000"
    master_key = "sk-master-1234"

    manager = VirtualKeyManager(base_url, master_key)

    # 範例 1：為開發團隊建立金鑰
    print("\n範例 1：開發團隊金鑰")
    manager.create_key(
        key_name="dev-team",
        models=["gpt-4", "gpt-3.5"],
        max_budget=100.0,
        budget_duration="30d",
        rpm_limit=100
    )

    # 範例 2：為測試環境建立金鑰
    print("\n範例 2：測試環境金鑰")
    manager.create_key(
        key_name="test-env",
        models=["gpt-3.5"],
        max_budget=10.0,
        budget_duration="30d",
        rpm_limit=20
    )

    # 範例 3：為生產環境建立金鑰
    print("\n範例 3：生產環境金鑰")
    manager.create_key(
        key_name="production",
        models=["gpt-4", "claude-sonnet"],
        max_budget=1000.0,
        budget_duration="30d",
        rpm_limit=500,
        max_parallel_requests=50
    )

    # 列出所有金鑰
    manager.list_keys()


# ============================================================================
# 第四部分：速率限制和配額管理
# ============================================================================

def create_rate_limit_config():
    """
    建立包含速率限制的配置

    速率限制可以防止濫用並控制成本。
    """
    print("\n" + "=" * 80)
    print("速率限制配置")
    print("=" * 80)

    config = {
        "model_list": [
            {
                "model_name": "gpt-4",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "os.environ/OPENAI_API_KEY",
                    "rpm": 500,  # Requests Per Minute
                    "tpm": 100000  # Tokens Per Minute
                },
                "model_info": {
                    "max_budget": 500.0,
                    "budget_duration": "30d"
                }
            },
            {
                "model_name": "gpt-3.5",
                "litellm_params": {
                    "model": "gpt-3.5-turbo",
                    "api_key": "os.environ/OPENAI_API_KEY",
                    "rpm": 1000,
                    "tpm": 200000
                },
                "model_info": {
                    "max_budget": 100.0,
                    "budget_duration": "30d"
                }
            }
        ],

        "litellm_settings": {
            # 全域速率限制
            "global_max_parallel_requests": 100,
            # 預設的 RPM 限制
            "default_rpm": 500
        }
    }

    config_path = "litellm_config_rate_limit.yaml"
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    print(f"✓ 速率限制配置已建立：{config_path}")
    print("\n配置說明：")
    print("  - gpt-4：500 RPM, 100K TPM, $500/月")
    print("  - gpt-3.5：1000 RPM, 200K TPM, $100/月")
    print("  - 全域：最多 100 個並行請求")

    return config_path


# ============================================================================
# 第五部分：負載均衡配置
# ============================================================================

def create_load_balancing_config():
    """
    建立負載均衡配置

    當有多個相同模型的 API 金鑰時，可以使用負載均衡來分散流量。
    """
    print("\n" + "=" * 80)
    print("負載均衡配置")
    print("=" * 80)

    config = {
        "model_list": [
            # GPT-4 的多個部署
            {
                "model_name": "gpt-4",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "os.environ/OPENAI_API_KEY_1"
                },
                "model_info": {
                    "id": "gpt-4-deployment-1"
                }
            },
            {
                "model_name": "gpt-4",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "os.environ/OPENAI_API_KEY_2"
                },
                "model_info": {
                    "id": "gpt-4-deployment-2"
                }
            },
            {
                "model_name": "gpt-4",
                "litellm_params": {
                    "model": "azure/gpt-4",
                    "api_base": "os.environ/AZURE_API_BASE",
                    "api_key": "os.environ/AZURE_API_KEY"
                },
                "model_info": {
                    "id": "gpt-4-azure"
                }
            }
        ],

        "router_settings": {
            # 路由策略選項：
            # - simple-shuffle：隨機選擇
            # - least-busy：選擇最不忙碌的
            # - usage-based-routing：基於使用量
            # - latency-based-routing：基於延遲
            "routing_strategy": "least-busy",

            # 允許的失敗次數（之後會暫時禁用該部署）
            "allowed_fails": 3,

            # 冷卻時間（秒）
            "cooldown_time": 60,

            # 重試設定
            "num_retries": 2,
            "retry_delay": 1
        }
    }

    config_path = "litellm_config_load_balancing.yaml"
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    print(f"✓ 負載均衡配置已建立：{config_path}")
    print("\n配置說明：")
    print("  - GPT-4 有 3 個部署（2 個 OpenAI，1 個 Azure）")
    print("  - 使用 least-busy 策略自動分配流量")
    print("  - 失敗 3 次後自動切換到其他部署")

    return config_path


# ============================================================================
# 第六部分：監控和日誌
# ============================================================================

def create_monitoring_config():
    """
    建立包含監控和日誌的配置

    整合各種監控和分析工具。
    """
    print("\n" + "=" * 80)
    print("監控和日誌配置")
    print("=" * 80)

    config = {
        "model_list": [
            {
                "model_name": "gpt-4",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "os.environ/OPENAI_API_KEY"
                }
            }
        ],

        "litellm_settings": {
            # 成功回調（記錄成功的請求）
            "success_callback": [
                "langfuse",  # LLM 分析平台
                "prometheus",  # 指標收集
                "s3"  # 儲存到 S3
            ],

            # 失敗回調（記錄失敗的請求）
            "failure_callback": [
                "sentry",  # 錯誤追蹤
                "slack"  # Slack 通知
            ],

            # 日誌設定
            "set_verbose": True,
            "json_logs": True,

            # Prometheus 設定
            "prometheus": {
                "port": 9090
            },

            # Langfuse 設定
            "langfuse": {
                "public_key": "os.environ/LANGFUSE_PUBLIC_KEY",
                "secret_key": "os.environ/LANGFUSE_SECRET_KEY",
                "host": "https://cloud.langfuse.com"
            }
        }
    }

    config_path = "litellm_config_monitoring.yaml"
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    print(f"✓ 監控配置已建立：{config_path}")
    print("\n整合的工具：")
    print("  - Langfuse：LLM 追蹤和分析")
    print("  - Prometheus：指標收集")
    print("  - Sentry：錯誤追蹤")
    print("  - Slack：即時通知")
    print("  - S3：日誌歸檔")

    return config_path


# ============================================================================
# 第七部分：健康檢查和管理端點
# ============================================================================

class ProxyHealthChecker:
    """代理伺服器健康檢查器"""

    def __init__(self, base_url: str):
        self.base_url = base_url

    def check_health(self) -> Dict[str, Any]:
        """檢查伺服器健康狀態"""
        print("\n檢查伺服器健康狀態")
        print("-" * 40)

        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✓ 伺服器狀態：健康")
                return response.json()
            else:
                print(f"✗ 伺服器狀態：不健康（{response.status_code}）")
                return {}
        except Exception as e:
            print(f"✗ 無法連接到伺服器：{e}")
            return {}

    def get_metrics(self) -> Dict[str, Any]:
        """取得伺服器指標"""
        print("\n取得伺服器指標")
        print("-" * 40)

        try:
            response = requests.get(f"{self.base_url}/metrics")
            if response.status_code == 200:
                metrics = response.json()
                print("✓ 指標：")
                print(json.dumps(metrics, indent=2))
                return metrics
            else:
                print(f"✗ 無法取得指標")
                return {}
        except Exception as e:
            print(f"✗ 錯誤：{e}")
            return {}

    def get_models(self) -> List[str]:
        """取得可用的模型列表"""
        print("\n取得可用模型")
        print("-" * 40)

        try:
            response = requests.get(f"{self.base_url}/models")
            if response.status_code == 200:
                data = response.json()
                models = [model['id'] for model in data.get('data', [])]
                print(f"✓ 可用模型（共 {len(models)} 個）：")
                for model in models:
                    print(f"  - {model}")
                return models
            else:
                print(f"✗ 無法取得模型列表")
                return []
        except Exception as e:
            print(f"✗ 錯誤：{e}")
            return []


def health_check_example():
    """健康檢查範例"""
    print("\n" + "=" * 80)
    print("健康檢查範例")
    print("=" * 80)

    base_url = "http://localhost:4000"
    checker = ProxyHealthChecker(base_url)

    # 檢查健康狀態
    checker.check_health()

    # 取得指標
    checker.get_metrics()

    # 取得模型列表
    checker.get_models()


# ============================================================================
# 主程式
# ============================================================================

def main():
    """主程式"""
    print("\n")
    print("=" * 80)
    print("LiteLLM 代理伺服器完整教學")
    print("=" * 80)
    print()

    # 建立各種配置檔案
    print("建立配置檔案範例...")
    print()

    create_basic_config()
    create_advanced_config()
    create_virtual_keys_config()
    create_rate_limit_config()
    create_load_balancing_config()
    create_monitoring_config()

    # 使用範例（需要實際啟動伺服器才能執行）
    # proxy_server_example()
    # virtual_keys_example()
    # health_check_example()

    print("\n" + "=" * 80)
    print("教學完成！")
    print("=" * 80)
    print("\n重點回顧：")
    print("1. 代理伺服器提供集中管理和企業級功能")
    print("2. 虛擬金鑰允許細粒度的存取控制")
    print("3. 速率限制和配額管理防止濫用")
    print("4. 負載均衡提高可用性和效能")
    print("5. 監控和日誌幫助追蹤和優化")
    print()


if __name__ == "__main__":
    main()
