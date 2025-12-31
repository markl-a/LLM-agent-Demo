#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Guidance 快速開始示例
====================================================

本模塊展示 Guidance 框架的基本使用方法，包括：
1. 模型初始化和配置
2. 基本文本生成
3. 變量捕獲和使用
4. 簡單的輸出控制
5. 錯誤處理和調試

Guidance 是微軟開發的 LLM 輸出控制庫，通過 token 級別的約束
來確保模型輸出符合預期格式，將結構化任務錯誤率降低 90%。

作者: Guidance 示例團隊
日期: 2025-01-01
"""

import os
import sys
from typing import Dict, List, Optional, Any
import json
import time
from datetime import datetime

# Guidance 核心導入
try:
    from guidance import models, gen, select, user, assistant, system
    import guidance
except ImportError:
    print("錯誤: 請先安裝 guidance 庫")
    print("運行: pip install guidance>=0.2.0")
    sys.exit(1)

# OpenAI API 支持
try:
    import openai
except ImportError:
    print("警告: OpenAI 庫未安裝，某些功能可能不可用")
    openai = None


class GuidanceQuickStart:
    """
    Guidance 快速開始類

    提供 Guidance 框架的基本功能演示，包括模型初始化、
    文本生成、變量管理等核心操作。

    Attributes:
        model_name: 使用的模型名稱
        api_key: OpenAI API 密鑰
        lm: 當前的語言模型實例
        examples_run: 已運行的示例計數
    """

    def __init__(self, model_name: str = "gpt-4", api_key: Optional[str] = None):
        """
        初始化 Guidance 快速開始實例

        Args:
            model_name: 要使用的模型名稱，默認為 gpt-4
            api_key: OpenAI API 密鑰，如果為 None 則從環境變量讀取
        """
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.lm = None
        self.examples_run = 0

        # 驗證 API 密鑰
        if not self.api_key:
            print("警告: 未找到 OPENAI_API_KEY 環境變量")
            print("請設置環境變量或在初始化時傳入 api_key 參數")

    def initialize_model(self) -> None:
        """
        初始化語言模型

        創建 Guidance 模型實例，這是使用 Guidance 的第一步。
        模型對象是可變的，可以通過 += 操作符累積內容。

        Raises:
            Exception: 如果模型初始化失敗
        """
        try:
            print(f"\n{'='*60}")
            print(f"正在初始化模型: {self.model_name}")
            print(f"{'='*60}")

            # 創建 OpenAI 模型實例
            # Guidance 支持多種後端: OpenAI, Transformers, vLLM 等
            self.lm = models.OpenAI(
                model=self.model_name,
                api_key=self.api_key,
                # 可選參數:
                # temperature=0.7,      # 控制隨機性
                # max_tokens=1000,      # 最大生成 token 數
                # top_p=0.9,           # 核採樣參數
            )

            print(f"✓ 模型初始化成功!")
            print(f"  - 模型: {self.model_name}")
            print(f"  - 後端: OpenAI API")

        except Exception as e:
            print(f"✗ 模型初始化失敗: {str(e)}")
            raise

    def example_basic_generation(self) -> None:
        """
        示例 1: 基本文本生成

        演示如何使用 Guidance 進行最基本的文本生成。
        Guidance 使用 += 操作符來累積文本和生成指令。
        """
        print(f"\n{'='*60}")
        print("示例 1: 基本文本生成")
        print(f"{'='*60}\n")

        # 重置模型狀態
        lm = self.lm

        # 添加靜態文本 (提示詞)
        # 使用 += 操作符將文本添加到模型對象中
        lm += "請列出三種流行的程式語言:\n"

        # 添加生成指令
        # gen() 函數會讓模型生成文本
        # name 參數用於捕獲生成的內容
        # max_tokens 限制生成的長度
        lm += "1. " + gen(name="lang1", max_tokens=10) + "\n"
        lm += "2. " + gen(name="lang2", max_tokens=10) + "\n"
        lm += "3. " + gen(name="lang3", max_tokens=10) + "\n"

        # 輸出結果
        print("生成的語言列表:")
        print(f"  1. {lm['lang1']}")
        print(f"  2. {lm['lang2']}")
        print(f"  3. {lm['lang3']}")

        # 輸出完整對話
        print("\n完整輸出:")
        print(lm)

        self.examples_run += 1

    def example_variable_capture(self) -> Dict[str, str]:
        """
        示例 2: 變量捕獲與使用

        演示如何捕獲模型生成的內容並在後續使用。
        Guidance 允許通過 name 參數捕獲生成的文本。

        Returns:
            包含捕獲變量的字典
        """
        print(f"\n{'='*60}")
        print("示例 2: 變量捕獲與使用")
        print(f"{'='*60}\n")

        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        # 第一步: 生成一個城市名稱並捕獲
        lm += "請說出一個著名的旅遊城市: "
        lm += gen(name="city", max_tokens=10, stop="\n")

        print(f"生成的城市: {lm['city']}")

        # 第二步: 使用捕獲的變量繼續生成
        # 可以通過 lm['變量名'] 訪問之前捕獲的內容
        lm += f"\n\n關於 {lm['city']} 的簡介:\n"
        lm += gen(name="description", max_tokens=100, stop="\n\n")

        print(f"\n城市簡介:\n{lm['description']}")

        # 第三步: 生成結構化信息
        lm += f"\n{lm['city']} 的最佳旅遊季節: "
        lm += gen(name="season", max_tokens=20, stop="\n")

        print(f"\n最佳旅遊季節: {lm['season']}")

        # 返回所有捕獲的變量
        results = {
            "city": lm["city"],
            "description": lm["description"],
            "season": lm["season"]
        }

        self.examples_run += 1
        return results

    def example_controlled_selection(self) -> str:
        """
        示例 3: 控制選擇

        演示如何使用 select() 函數強制模型從預定義選項中選擇。
        這是 Guidance 最強大的功能之一 - 零錯誤率的選擇。

        Returns:
            選擇的答案
        """
        print(f"\n{'='*60}")
        print("示例 3: 控制選擇")
        print(f"{'='*60}\n")

        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        # select() 函數強制模型從給定選項中選擇
        # 這保證了 100% 的準確率 - 模型不可能選擇其他答案
        lm += "Python 是一種編譯型語言嗎? "
        lm += select(["是", "否"], name="answer1")

        print(f"問題 1: Python 是編譯型語言嗎?")
        print(f"答案: {lm['answer1']}\n")

        # 可以使用英文選項
        lm += "\n\nIs JavaScript a statically-typed language? "
        lm += select(["yes", "no"], name="answer2")

        print(f"問題 2: JavaScript 是靜態類型語言嗎?")
        print(f"答案: {lm['answer2']}\n")

        # 多選項範例
        lm += "\n\n以下哪個是最好的機器學習框架? "
        lm += select([
            "TensorFlow",
            "PyTorch",
            "JAX",
            "MXNet",
            "Scikit-learn"
        ], name="framework")

        print(f"問題 3: 最好的機器學習框架?")
        print(f"答案: {lm['framework']}\n")

        self.examples_run += 1
        return lm["framework"]

    def example_stop_sequences(self) -> None:
        """
        示例 4: 停止序列控制

        演示如何使用 stop 參數控制生成何時停止。
        這對於提取特定格式的信息非常有用。
        """
        print(f"\n{'='*60}")
        print("示例 4: 停止序列控制")
        print(f"{'='*60}\n")

        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        # 使用 stop 參數在遇到特定字符時停止
        lm += "請提供一個電子郵件地址範例: "
        lm += gen(name="email", stop=["\n", " ", ","])

        print(f"提取的郵箱: {lm['email']}\n")

        # 提取句子
        lm += "\n\n請說一句關於 AI 的話: "
        lm += gen(name="sentence", stop=[".", "!", "?"])

        print(f"提取的句子: {lm['sentence']}\n")

        # 提取列表項
        lm += "\n\n列出三個常見的 HTTP 狀態碼:\n"
        for i in range(3):
            lm += f"{i+1}. "
            lm += gen(name=f"code_{i}", stop="\n")
            lm += "\n"

        print("HTTP 狀態碼:")
        for i in range(3):
            print(f"  {i+1}. {lm[f'code_{i}']}")

        self.examples_run += 1

    def example_temperature_control(self) -> None:
        """
        示例 5: 溫度參數控制

        演示如何控制生成的隨機性和創造性。
        溫度越高，輸出越有創造性但也越不可預測。
        """
        print(f"\n{'='*60}")
        print("示例 5: 溫度參數控制")
        print(f"{'='*60}\n")

        prompt = "用一句話描述人工智能: "

        # 低溫度 (更確定性)
        print("低溫度 (temperature=0.1) - 更確定性:")
        lm_low = models.OpenAI(
            self.model_name,
            api_key=self.api_key,
            temperature=0.1
        )
        lm_low += prompt
        lm_low += gen(name="desc", max_tokens=50)
        print(f"  {lm_low['desc']}\n")

        # 中溫度 (平衡)
        print("中溫度 (temperature=0.7) - 平衡:")
        lm_mid = models.OpenAI(
            self.model_name,
            api_key=self.api_key,
            temperature=0.7
        )
        lm_mid += prompt
        lm_mid += gen(name="desc", max_tokens=50)
        print(f"  {lm_mid['desc']}\n")

        # 高溫度 (更有創造性)
        print("高溫度 (temperature=1.5) - 更有創造性:")
        lm_high = models.OpenAI(
            self.model_name,
            api_key=self.api_key,
            temperature=1.5
        )
        lm_high += prompt
        lm_high += gen(name="desc", max_tokens=50)
        print(f"  {lm_high['desc']}\n")

        self.examples_run += 1

    def example_multi_step_generation(self) -> Dict[str, Any]:
        """
        示例 6: 多步驟生成

        演示如何構建複雜的多步驟生成流程，
        每一步的輸出可以影響後續步驟。

        Returns:
            包含所有步驟結果的字典
        """
        print(f"\n{'='*60}")
        print("示例 6: 多步驟生成")
        print(f"{'='*60}\n")

        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        # 步驟 1: 選擇一個主題
        lm += "從以下主題中選擇一個: "
        lm += select([
            "太空探索",
            "深海探險",
            "人工智能",
            "量子計算"
        ], name="topic")

        print(f"步驟 1 - 選擇的主題: {lm['topic']}")

        # 步驟 2: 確定難度級別
        lm += f"\n\n對於主題「{lm['topic']}」，選擇講解難度: "
        lm += select(["入門", "中級", "高級"], name="level")

        print(f"步驟 2 - 難度級別: {lm['level']}")

        # 步驟 3: 生成標題
        lm += f"\n\n為「{lm['topic']}」寫一個適合{lm['level']}讀者的文章標題: "
        lm += gen(name="title", max_tokens=30, stop="\n")

        print(f"步驟 3 - 文章標題: {lm['title']}")

        # 步驟 4: 生成摘要
        lm += f"\n\n為這篇文章寫一個簡短摘要:\n"
        lm += gen(name="summary", max_tokens=100, stop="\n\n")

        print(f"步驟 4 - 文章摘要:\n{lm['summary']}")

        # 步驟 5: 確定目標受眾
        lm += f"\n\n這篇文章最適合的讀者群: "
        lm += select([
            "學生",
            "研究人員",
            "工程師",
            "普通大眾"
        ], name="audience")

        print(f"步驟 5 - 目標受眾: {lm['audience']}")

        results = {
            "topic": lm["topic"],
            "level": lm["level"],
            "title": lm["title"],
            "summary": lm["summary"],
            "audience": lm["audience"],
            "timestamp": datetime.now().isoformat()
        }

        self.examples_run += 1
        return results

    def example_error_handling(self) -> None:
        """
        示例 7: 錯誤處理

        演示如何正確處理 Guidance 操作中可能出現的錯誤。
        """
        print(f"\n{'='*60}")
        print("示例 7: 錯誤處理")
        print(f"{'='*60}\n")

        # 錯誤 1: API 密鑰錯誤
        print("測試 1: API 密鑰錯誤處理")
        try:
            lm_bad = models.OpenAI(self.model_name, api_key="invalid_key")
            lm_bad += "Test"
            lm_bad += gen(max_tokens=10)
        except Exception as e:
            print(f"  ✓ 捕獲錯誤: {type(e).__name__}")
            print(f"  訊息: {str(e)[:100]}...\n")

        # 錯誤 2: 無效的 select 選項
        print("測試 2: 空選項列表")
        try:
            lm = models.OpenAI(self.model_name, api_key=self.api_key)
            lm += "Choose: "
            lm += select([], name="choice")  # 空列表會導致錯誤
        except Exception as e:
            print(f"  ✓ 捕獲錯誤: {type(e).__name__}")
            print(f"  訊息: {str(e)}\n")

        # 錯誤 3: 訪問不存在的變量
        print("測試 3: 訪問未定義的變量")
        try:
            lm = models.OpenAI(self.model_name, api_key=self.api_key)
            lm += "Hello"
            value = lm["nonexistent_var"]  # 訪問不存在的變量
        except Exception as e:
            print(f"  ✓ 捕獲錯誤: {type(e).__name__}")
            print(f"  訊息: {str(e)}\n")

        self.examples_run += 1

    def run_all_examples(self) -> None:
        """
        運行所有示例

        按順序執行所有示例，展示 Guidance 的基本功能。
        """
        print("\n" + "="*60)
        print("Guidance 快速開始 - 完整示例")
        print("="*60)

        start_time = time.time()

        # 初始化模型
        self.initialize_model()

        # 運行各個示例
        self.example_basic_generation()
        self.example_variable_capture()
        self.example_controlled_selection()
        self.example_stop_sequences()
        self.example_temperature_control()
        results = self.example_multi_step_generation()
        self.example_error_handling()

        # 統計信息
        elapsed_time = time.time() - start_time

        print(f"\n{'='*60}")
        print("執行摘要")
        print(f"{'='*60}")
        print(f"總共運行示例數: {self.examples_run}")
        print(f"總耗時: {elapsed_time:.2f} 秒")
        print(f"平均每個示例: {elapsed_time/self.examples_run:.2f} 秒")
        print(f"\n最後一個多步驟生成結果:")
        print(json.dumps(results, indent=2, ensure_ascii=False))


def main():
    """
    主函數

    創建 GuidanceQuickStart 實例並運行所有示例。
    """
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║         Guidance 框架 - 快速開始示例                       ║
    ║                                                            ║
    ║  Guidance 是微軟開發的 LLM 輸出控制庫                      ║
    ║  通過 token 級約束確保輸出符合預期格式                     ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    # 檢查環境變量
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        print("請運行: export OPENAI_API_KEY='your-api-key'")
        print("\n為了演示，程序將繼續運行，但實際 API 調用可能失敗。\n")

    # 創建實例並運行示例
    quickstart = GuidanceQuickStart(
        model_name="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    try:
        quickstart.run_all_examples()
        print("\n✓ 所有示例執行完成!")

    except KeyboardInterrupt:
        print("\n\n⚠️  用戶中斷執行")

    except Exception as e:
        print(f"\n✗ 執行出錯: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
