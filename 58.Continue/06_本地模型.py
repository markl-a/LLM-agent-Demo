"""
Continue AI 編程助手 - 本地模型集成

這個文件展示了如何集成和使用本地 AI 模型。
支持 Ollama、llama.cpp、LocalAI 等本地模型運行方案。

主要內容:
1. Ollama 集成
2. llama.cpp 集成
3. LocalAI 集成
4. 模型下載和管理
5. 本地模型優化
6. 離線使用配置
7. GPU 加速設置

Author: Continue Team
Date: 2025
"""

import os
import subprocess
import json
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
import time


# =====================================================
# 第一部分: 本地模型框架定義
# =====================================================

class LocalModelFramework(Enum):
    """
    本地模型框架
    """
    OLLAMA = "ollama"
    LLAMA_CPP = "llama_cpp"
    LOCAL_AI = "localai"
    TRANSFORMERS = "transformers"
    VLLM = "vllm"


@dataclass
class LocalModelInfo:
    """
    本地模型信息
    """
    name: str  # 模型名稱
    size: str  # 模型大小
    parameters: str  # 參數數量
    quantization: str  # 量化方式
    modified_at: str  # 修改時間
    framework: LocalModelFramework  # 所屬框架


class ModelQuantization(Enum):
    """
    模型量化方式
    """
    FP16 = "fp16"  # 16位浮點
    INT8 = "int8"  # 8位整數
    INT4 = "int4"  # 4位整數
    GGUF_Q4_0 = "q4_0"  # GGUF Q4_0
    GGUF_Q4_1 = "q4_1"  # GGUF Q4_1
    GGUF_Q5_0 = "q5_0"  # GGUF Q5_0
    GGUF_Q5_1 = "q5_1"  # GGUF Q5_1
    GGUF_Q8_0 = "q8_0"  # GGUF Q8_0


# =====================================================
# 第二部分: Ollama 集成
# =====================================================

class OllamaManager:
    """
    Ollama 管理器

    管理 Ollama 本地模型的下載、運行和使用
    """

    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        初始化 Ollama 管理器

        Args:
            base_url: Ollama 服務地址
        """
        self.base_url = base_url
        self.api_url = f"{base_url}/api"

    def is_running(self) -> bool:
        """
        檢查 Ollama 服務是否運行

        Returns:
            是否運行
        """
        try:
            response = requests.get(f"{self.api_url}/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def start_service(self) -> bool:
        """
        啟動 Ollama 服務

        Returns:
            是否啟動成功
        """
        try:
            # 嘗試啟動 Ollama
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # 等待服務啟動
            for _ in range(10):
                time.sleep(1)
                if self.is_running():
                    print("Ollama 服務已啟動")
                    return True

            return False

        except FileNotFoundError:
            print("錯誤: 未找到 Ollama 命令,請先安裝 Ollama")
            print("安裝方法: https://ollama.ai/download")
            return False
        except Exception as e:
            print(f"啟動 Ollama 服務失敗: {e}")
            return False

    def list_models(self) -> List[LocalModelInfo]:
        """
        列出已下載的模型

        Returns:
            模型信息列表
        """
        try:
            response = requests.get(f"{self.api_url}/tags")
            response.raise_for_status()

            data = response.json()
            models = []

            for model in data.get("models", []):
                models.append(LocalModelInfo(
                    name=model["name"],
                    size=self._format_size(model.get("size", 0)),
                    parameters=model.get("details", {}).get("parameter_size", "unknown"),
                    quantization=model.get("details", {}).get("quantization_level", "unknown"),
                    modified_at=model.get("modified_at", ""),
                    framework=LocalModelFramework.OLLAMA
                ))

            return models

        except Exception as e:
            print(f"獲取模型列表失敗: {e}")
            return []

    def pull_model(self, model_name: str) -> bool:
        """
        下載模型

        Args:
            model_name: 模型名稱(如 llama2, codellama, mistral)

        Returns:
            是否下載成功
        """
        print(f"開始下載模型: {model_name}")
        print("這可能需要幾分鐘到幾小時,取決於模型大小和網絡速度...")

        try:
            response = requests.post(
                f"{self.api_url}/pull",
                json={"name": model_name},
                stream=True
            )
            response.raise_for_status()

            # 顯示下載進度
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    status = data.get("status", "")
                    if "total" in data and "completed" in data:
                        total = data["total"]
                        completed = data["completed"]
                        percentage = (completed / total) * 100
                        print(f"\r{status}: {percentage:.1f}%", end="")
                    else:
                        print(f"\r{status}", end="")

            print(f"\n模型 {model_name} 下載完成!")
            return True

        except Exception as e:
            print(f"\n下載模型失敗: {e}")
            return False

    def remove_model(self, model_name: str) -> bool:
        """
        刪除模型

        Args:
            model_name: 模型名稱

        Returns:
            是否刪除成功
        """
        try:
            response = requests.delete(
                f"{self.api_url}/delete",
                json={"name": model_name}
            )
            response.raise_for_status()
            print(f"模型 {model_name} 已刪除")
            return True

        except Exception as e:
            print(f"刪除模型失敗: {e}")
            return False

    def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Optional[str]:
        """
        使用模型生成文本

        Args:
            model: 模型名稱
            prompt: 提示詞
            temperature: 溫度
            max_tokens: 最大 token 數

        Returns:
            生成的文本
        """
        try:
            response = requests.post(
                f"{self.api_url}/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "options": {
                        "num_predict": max_tokens
                    },
                    "stream": False
                }
            )
            response.raise_for_status()

            data = response.json()
            return data.get("response")

        except Exception as e:
            print(f"生成失敗: {e}")
            return None

    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> Optional[str]:
        """
        聊天模式

        Args:
            model: 模型名稱
            messages: 消息列表
            temperature: 溫度

        Returns:
            回覆文本
        """
        try:
            response = requests.post(
                f"{self.api_url}/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "stream": False
                }
            )
            response.raise_for_status()

            data = response.json()
            return data.get("message", {}).get("content")

        except Exception as e:
            print(f"聊天失敗: {e}")
            return None

    def _format_size(self, bytes_size: int) -> str:
        """
        格式化大小

        Args:
            bytes_size: 字節大小

        Returns:
            格式化的字符串
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} PB"


# =====================================================
# 第三部分: llama.cpp 集成
# =====================================================

class LlamaCppManager:
    """
    llama.cpp 管理器

    管理 llama.cpp 模型的運行
    """

    def __init__(self, models_dir: str = "./models"):
        """
        初始化 llama.cpp 管理器

        Args:
            models_dir: 模型目錄
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.server_process: Optional[subprocess.Popen] = None
        self.server_url = "http://localhost:8080"

    def list_models(self) -> List[LocalModelInfo]:
        """
        列出本地 GGUF 模型

        Returns:
            模型信息列表
        """
        models = []

        for model_file in self.models_dir.glob("*.gguf"):
            size = model_file.stat().st_size
            models.append(LocalModelInfo(
                name=model_file.name,
                size=self._format_size(size),
                parameters=self._guess_parameters(model_file.name),
                quantization=self._extract_quantization(model_file.name),
                modified_at=str(model_file.stat().st_mtime),
                framework=LocalModelFramework.LLAMA_CPP
            ))

        return models

    def start_server(
        self,
        model_path: str,
        n_gpu_layers: int = 0,
        context_size: int = 2048,
        threads: int = 4
    ) -> bool:
        """
        啟動 llama.cpp 服務器

        Args:
            model_path: 模型路徑
            n_gpu_layers: GPU 層數(0=CPU only)
            context_size: 上下文大小
            threads: 線程數

        Returns:
            是否啟動成功
        """
        try:
            cmd = [
                "llama-server",  # 或 "./server" 如果是編譯的版本
                "-m", model_path,
                "-c", str(context_size),
                "-t", str(threads),
                "--host", "0.0.0.0",
                "--port", "8080"
            ]

            if n_gpu_layers > 0:
                cmd.extend(["-ngl", str(n_gpu_layers)])

            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # 等待服務器啟動
            time.sleep(3)

            if self.is_server_running():
                print(f"llama.cpp 服務器已啟動")
                print(f"模型: {model_path}")
                print(f"GPU 層數: {n_gpu_layers}")
                return True
            else:
                print("服務器啟動失敗")
                return False

        except FileNotFoundError:
            print("錯誤: 未找到 llama-server")
            print("請先編譯 llama.cpp 或下載預編譯版本")
            return False
        except Exception as e:
            print(f"啟動服務器失敗: {e}")
            return False

    def stop_server(self):
        """
        停止服務器
        """
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            print("llama.cpp 服務器已停止")

    def is_server_running(self) -> bool:
        """
        檢查服務器是否運行

        Returns:
            是否運行
        """
        try:
            response = requests.get(f"{self.server_url}/health", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def generate(self, prompt: str, max_tokens: int = 2000) -> Optional[str]:
        """
        生成文本

        Args:
            prompt: 提示詞
            max_tokens: 最大 token 數

        Returns:
            生成的文本
        """
        try:
            response = requests.post(
                f"{self.server_url}/completion",
                json={
                    "prompt": prompt,
                    "n_predict": max_tokens
                }
            )
            response.raise_for_status()

            data = response.json()
            return data.get("content")

        except Exception as e:
            print(f"生成失敗: {e}")
            return None

    def _format_size(self, bytes_size: int) -> str:
        """格式化大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} PB"

    def _guess_parameters(self, filename: str) -> str:
        """從文件名推測參數數量"""
        if "7b" in filename.lower():
            return "7B"
        elif "13b" in filename.lower():
            return "13B"
        elif "70b" in filename.lower():
            return "70B"
        return "unknown"

    def _extract_quantization(self, filename: str) -> str:
        """從文件名提取量化信息"""
        for q in ModelQuantization:
            if q.value in filename.lower():
                return q.value
        return "unknown"


# =====================================================
# 第四部分: LocalAI 集成
# =====================================================

class LocalAIManager:
    """
    LocalAI 管理器

    管理 LocalAI 服務和模型
    """

    def __init__(self, base_url: str = "http://localhost:8080"):
        """
        初始化 LocalAI 管理器

        Args:
            base_url: LocalAI 服務地址
        """
        self.base_url = base_url

    def is_running(self) -> bool:
        """
        檢查服務是否運行

        Returns:
            是否運行
        """
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def list_models(self) -> List[str]:
        """
        列出可用模型

        Returns:
            模型名稱列表
        """
        try:
            response = requests.get(f"{self.base_url}/v1/models")
            response.raise_for_status()

            data = response.json()
            return [model["id"] for model in data.get("data", [])]

        except Exception as e:
            print(f"獲取模型列表失敗: {e}")
            return []

    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> Optional[str]:
        """
        聊天

        Args:
            model: 模型名稱
            messages: 消息列表
            temperature: 溫度

        Returns:
            回覆
        """
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature
                }
            )
            response.raise_for_status()

            data = response.json()
            return data["choices"][0]["message"]["content"]

        except Exception as e:
            print(f"聊天失敗: {e}")
            return None


# =====================================================
# 第五部分: 本地模型推薦
# =====================================================

class LocalModelRecommender:
    """
    本地模型推薦器

    根據硬件配置推薦合適的模型
    """

    # 模型推薦表
    RECOMMENDATIONS = {
        "low_end": {  # 低配置 (8GB RAM, 無GPU)
            "models": ["llama2:7b-q4_0", "mistral:7b-q4_0", "phi:2.7b"],
            "description": "適合低配置設備的小型量化模型"
        },
        "mid_range": {  # 中配置 (16GB RAM, 入門GPU)
            "models": ["llama2:13b-q4_0", "codellama:13b", "mistral:7b"],
            "description": "適合中等配置的模型"
        },
        "high_end": {  # 高配置 (32GB+ RAM, 高性能GPU)
            "models": ["llama2:70b", "codellama:34b", "mixtral:8x7b"],
            "description": "適合高配置設備的大型模型"
        }
    }

    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """
        獲取系統信息

        Returns:
            系統信息字典
        """
        import psutil

        info = {
            "total_ram_gb": psutil.virtual_memory().total / (1024**3),
            "available_ram_gb": psutil.virtual_memory().available / (1024**3),
            "cpu_count": psutil.cpu_count(),
            "has_gpu": False
        }

        # 檢測 GPU
        try:
            import torch
            info["has_gpu"] = torch.cuda.is_available()
            if info["has_gpu"]:
                info["gpu_name"] = torch.cuda.get_device_name(0)
                info["gpu_memory_gb"] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        except ImportError:
            pass

        return info

    @classmethod
    def recommend_models(cls) -> Dict[str, Any]:
        """
        推薦模型

        Returns:
            推薦信息
        """
        sys_info = cls.get_system_info()
        total_ram = sys_info["total_ram_gb"]

        # 根據 RAM 判斷配置等級
        if total_ram < 12:
            tier = "low_end"
        elif total_ram < 24:
            tier = "mid_range"
        else:
            tier = "high_end"

        recommendation = cls.RECOMMENDATIONS[tier].copy()
        recommendation["system_info"] = sys_info
        recommendation["tier"] = tier

        return recommendation


# =====================================================
# 第六部分: 使用示例
# =====================================================

def ollama_example():
    """
    Ollama 使用示例
    """
    print("=" * 60)
    print("示例 1: Ollama 使用")
    print("=" * 60)

    manager = OllamaManager()

    # 檢查服務
    if not manager.is_running():
        print("Ollama 服務未運行,嘗試啟動...")
        # manager.start_service()

    # 列出模型
    print("\n已安裝的模型:")
    models = manager.list_models()
    for model in models:
        print(f"  - {model.name} ({model.size}, {model.parameters})")

    # 下載模型(示例,實際使用時取消註釋)
    # manager.pull_model("llama2:7b")

    # 使用模型生成
    if models:
        print(f"\n使用模型 {models[0].name} 生成文本:")
        response = manager.generate(
            model=models[0].name,
            prompt="用 Python 寫一個快速排序算法",
            temperature=0.7,
            max_tokens=500
        )
        if response:
            print(response)


def model_recommendation_example():
    """
    模型推薦示例
    """
    print("\n" + "=" * 60)
    print("示例 2: 模型推薦")
    print("=" * 60)

    recommender = LocalModelRecommender()

    # 獲取系統信息
    sys_info = recommender.get_system_info()
    print("\n系統信息:")
    print(f"  總 RAM: {sys_info['total_ram_gb']:.1f} GB")
    print(f"  可用 RAM: {sys_info['available_ram_gb']:.1f} GB")
    print(f"  CPU 核心數: {sys_info['cpu_count']}")
    print(f"  GPU: {'是' if sys_info['has_gpu'] else '否'}")

    # 獲取推薦
    recommendation = recommender.recommend_models()
    print(f"\n配置等級: {recommendation['tier']}")
    print(f"說明: {recommendation['description']}")
    print("\n推薦模型:")
    for model in recommendation['models']:
        print(f"  - {model}")


def llama_cpp_example():
    """
    llama.cpp 使用示例
    """
    print("\n" + "=" * 60)
    print("示例 3: llama.cpp 使用")
    print("=" * 60)

    manager = LlamaCppManager()

    # 列出模型
    print("\nGGUF 模型:")
    models = manager.list_models()
    for model in models:
        print(f"  - {model.name} ({model.size})")

    # 啟動服務器(示例)
    # if models:
    #     model_path = str(manager.models_dir / models[0].name)
    #     manager.start_server(model_path, n_gpu_layers=0)


def main():
    """
    主函數
    """
    print("Continue - 本地模型集成\n")

    try:
        ollama_example()
        model_recommendation_example()
        llama_cpp_example()
    except Exception as e:
        print(f"示例運行出錯: {e}")

    print("\n" + "=" * 60)
    print("示例運行完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
