"""
Outlines 快速開始示例
===================

本示例展示如何快速開始使用 Outlines 框架進行結構化文本生成。

主要內容:
1. 環境設置和模型載入
2. 基本文本生成
3. 簡單的結構化輸出
4. 常見配置選項
5. 錯誤處理

作者: Outlines 教學團隊
日期: 2025-01
"""

import outlines
from outlines import models, generate
import torch
import json
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import logging
import time
import sys
from pathlib import Path

# ==================== 設置日誌 ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('outlines_quickstart.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


# ==================== 配置類 ====================

class OutlinesConfig:
    """
    Outlines 配置類

    用於管理 Outlines 的各種配置參數,包括:
    - 模型選擇和載入參數
    - 生成參數
    - 設備配置
    - 性能優化選項
    """

    def __init__(
        self,
        model_name: str = "mistralai/Mistral-7B-v0.1",
        device: str = "auto",
        max_tokens: int = 512,
        temperature: float = 0.7,
        use_cache: bool = True,
        load_in_8bit: bool = False,
        load_in_4bit: bool = False
    ):
        """
        初始化配置

        Args:
            model_name: 要使用的模型名稱
            device: 設備選擇 ('cuda', 'cpu', 'auto')
            max_tokens: 生成的最大 token 數量
            temperature: 生成溫度,控制隨機性
            use_cache: 是否使用緩存加速生成
            load_in_8bit: 是否使用 8-bit 量化
            load_in_4bit: 是否使用 4-bit 量化
        """
        self.model_name = model_name
        self.device = self._determine_device(device)
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.use_cache = use_cache
        self.load_in_8bit = load_in_8bit
        self.load_in_4bit = load_in_4bit

        logger.info(f"配置初始化完成: 模型={model_name}, 設備={self.device}")

    def _determine_device(self, device: str) -> str:
        """
        自動確定使用的設備

        Args:
            device: 設備偏好

        Returns:
            實際使用的設備
        """
        if device == "auto":
            if torch.cuda.is_available():
                logger.info("檢測到 CUDA,使用 GPU")
                return "cuda"
            else:
                logger.info("未檢測到 CUDA,使用 CPU")
                return "cpu"
        return device

    def get_model_kwargs(self) -> Dict[str, Any]:
        """
        獲取模型載入參數

        Returns:
            模型參數字典
        """
        kwargs = {
            "device": self.device,
        }

        if self.load_in_8bit:
            kwargs["load_in_8bit"] = True
            logger.info("啟用 8-bit 量化")

        if self.load_in_4bit:
            kwargs["load_in_4bit"] = True
            logger.info("啟用 4-bit 量化")

        return kwargs


# ==================== 模型管理器 ====================

class ModelManager:
    """
    模型管理器

    負責:
    - 載入和管理 Outlines 模型
    - 模型緩存
    - 資源清理
    """

    def __init__(self, config: OutlinesConfig):
        """
        初始化模型管理器

        Args:
            config: Outlines 配置對象
        """
        self.config = config
        self.model = None
        self.load_time = None

        logger.info("模型管理器初始化完成")

    def load_model(self) -> Any:
        """
        載入模型

        Returns:
            載入的模型對象

        Raises:
            RuntimeError: 當模型載入失敗時
        """
        try:
            logger.info(f"開始載入模型: {self.config.model_name}")
            start_time = time.time()

            # 載入 Transformers 模型
            self.model = models.transformers(
                self.config.model_name,
                device=self.config.device,
                model_kwargs=self.config.get_model_kwargs()
            )

            self.load_time = time.time() - start_time
            logger.info(f"模型載入完成,耗時: {self.load_time:.2f} 秒")

            return self.model

        except Exception as e:
            logger.error(f"模型載入失敗: {str(e)}")
            raise RuntimeError(f"無法載入模型: {str(e)}")

    def get_model(self) -> Any:
        """
        獲取模型(如果未載入則自動載入)

        Returns:
            模型對象
        """
        if self.model is None:
            self.load_model()
        return self.model

    def cleanup(self):
        """
        清理模型資源
        """
        if self.model is not None:
            del self.model
            self.model = None

            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            logger.info("模型資源已清理")


# ==================== 基本生成器 ====================

class BasicGenerator:
    """
    基本文本生成器

    提供:
    - 無約束文本生成
    - 基本的生成參數控制
    - 性能監控
    """

    def __init__(self, model_manager: ModelManager):
        """
        初始化生成器

        Args:
            model_manager: 模型管理器對象
        """
        self.model_manager = model_manager
        self.model = model_manager.get_model()

        logger.info("基本生成器初始化完成")

    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        生成文本

        Args:
            prompt: 輸入提示
            max_tokens: 最大 token 數(可選)
            temperature: 生成溫度(可選)

        Returns:
            生成的文本
        """
        try:
            logger.info(f"開始生成,提示: {prompt[:50]}...")
            start_time = time.time()

            # 創建文本生成器
            generator = generate.text(self.model)

            # 生成文本
            result = generator(prompt)

            generation_time = time.time() - start_time
            logger.info(f"生成完成,耗時: {generation_time:.2f} 秒")

            return result

        except Exception as e:
            logger.error(f"生成失敗: {str(e)}")
            raise


# ==================== 結構化生成器 ====================

class Person(BaseModel):
    """
    人物信息模型

    用於演示結構化輸出生成
    """
    name: str = Field(description="姓名")
    age: int = Field(description="年齡", ge=0, le=120)
    occupation: str = Field(description="職業")
    email: str = Field(description="電子郵件")


class StructuredGenerator:
    """
    結構化生成器

    提供:
    - JSON Schema 約束生成
    - Pydantic 模型生成
    - 類型安全保證
    """

    def __init__(self, model_manager: ModelManager):
        """
        初始化結構化生成器

        Args:
            model_manager: 模型管理器對象
        """
        self.model_manager = model_manager
        self.model = model_manager.get_model()

        logger.info("結構化生成器初始化完成")

    def generate_json(
        self,
        prompt: str,
        schema: BaseModel
    ) -> BaseModel:
        """
        生成符合 Pydantic 模型的 JSON

        Args:
            prompt: 輸入提示
            schema: Pydantic 模型類

        Returns:
            模型實例
        """
        try:
            logger.info(f"開始 JSON 生成,模型: {schema.__name__}")
            start_time = time.time()

            # 創建 JSON 生成器
            generator = generate.json(self.model, schema)

            # 生成結構化輸出
            result = generator(prompt)

            generation_time = time.time() - start_time
            logger.info(f"JSON 生成完成,耗時: {generation_time:.2f} 秒")

            return result

        except Exception as e:
            logger.error(f"JSON 生成失敗: {str(e)}")
            raise


# ==================== 示例運行器 ====================

class ExampleRunner:
    """
    示例運行器

    統一管理和運行各種示例
    """

    def __init__(self, config: OutlinesConfig):
        """
        初始化示例運行器

        Args:
            config: Outlines 配置
        """
        self.config = config
        self.model_manager = ModelManager(config)

        logger.info("示例運行器初始化完成")

    def run_basic_generation(self):
        """
        運行基本文本生成示例
        """
        print("\n" + "="*60)
        print("示例 1: 基本文本生成")
        print("="*60)

        try:
            generator = BasicGenerator(self.model_manager)

            # 測試提示
            prompts = [
                "什麼是人工智能?",
                "寫一個關於春天的詩句",
                "解釋量子計算的基本概念"
            ]

            for i, prompt in enumerate(prompts, 1):
                print(f"\n提示 {i}: {prompt}")
                result = generator.generate(prompt)
                print(f"生成結果: {result}")
                print("-" * 60)

        except Exception as e:
            logger.error(f"基本生成示例失敗: {str(e)}")

    def run_structured_generation(self):
        """
        運行結構化生成示例
        """
        print("\n" + "="*60)
        print("示例 2: 結構化輸出生成")
        print("="*60)

        try:
            generator = StructuredGenerator(self.model_manager)

            # 測試提示
            prompts = [
                "生成一個軟件工程師的信息",
                "創建一個醫生的個人資料",
                "生成一個學生的數據"
            ]

            for i, prompt in enumerate(prompts, 1):
                print(f"\n提示 {i}: {prompt}")
                result = generator.generate_json(prompt, Person)

                print(f"姓名: {result.name}")
                print(f"年齡: {result.age}")
                print(f"職業: {result.occupation}")
                print(f"郵箱: {result.email}")
                print("-" * 60)

        except Exception as e:
            logger.error(f"結構化生成示例失敗: {str(e)}")

    def cleanup(self):
        """
        清理資源
        """
        self.model_manager.cleanup()
        logger.info("示例運行器資源已清理")


# ==================== 主程序 ====================

def print_system_info():
    """
    打印系統信息
    """
    print("\n" + "="*60)
    print("系統信息")
    print("="*60)
    print(f"Python 版本: {sys.version}")
    print(f"PyTorch 版本: {torch.__version__}")
    print(f"CUDA 可用: {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        print(f"CUDA 版本: {torch.version.cuda}")
        print(f"GPU 數量: {torch.cuda.device_count()}")
        print(f"當前 GPU: {torch.cuda.get_device_name()}")

    print("="*60)


def main():
    """
    主函數

    運行所有快速開始示例
    """
    try:
        # 打印系統信息
        print_system_info()

        # 創建配置
        print("\n創建 Outlines 配置...")
        config = OutlinesConfig(
            model_name="mistralai/Mistral-7B-v0.1",
            device="auto",
            max_tokens=256,
            temperature=0.7,
            load_in_8bit=False  # 如果內存不足,可以設置為 True
        )

        # 創建示例運行器
        print("初始化示例運行器...")
        runner = ExampleRunner(config)

        # 運行示例
        print("\n開始運行示例...")

        # 示例 1: 基本文本生成
        runner.run_basic_generation()

        # 示例 2: 結構化生成
        runner.run_structured_generation()

        # 清理資源
        print("\n清理資源...")
        runner.cleanup()

        print("\n" + "="*60)
        print("所有示例運行完成!")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\n用戶中斷執行")
        logger.info("用戶中斷執行")
    except Exception as e:
        print(f"\n錯誤: {str(e)}")
        logger.error(f"主程序錯誤: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
