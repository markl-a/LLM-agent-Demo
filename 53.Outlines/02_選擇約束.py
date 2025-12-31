"""
Outlines 選擇約束生成示例
========================

本示例展示如何使用 Outlines 進行多選擇約束生成。

主要內容:
1. 單選擇約束
2. 多類別分類
3. 情感分析
4. 意圖識別
5. 層級選擇

作者: Outlines 教學團隊
日期: 2025-01
"""

import outlines
from outlines import models, generate
import torch
from typing import List, Dict, Optional, Tuple, Any
from pydantic import BaseModel, Field
import logging
import json
import time
from datetime import datetime
from collections import Counter, defaultdict
import sys

# ==================== 設置日誌 ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== 選擇約束管理器 ====================

class ChoiceConstraintManager:
    """
    選擇約束管理器

    管理和執行各種選擇約束的生成任務,包括:
    - 單選題
    - 多類別分類
    - 情感分析
    - 意圖識別
    """

    def __init__(self, model_name: str = "mistralai/Mistral-7B-v0.1"):
        """
        初始化選擇約束管理器

        Args:
            model_name: 使用的模型名稱
        """
        self.model_name = model_name
        self.model = None
        self.load_model()

        logger.info(f"選擇約束管理器初始化完成,模型: {model_name}")

    def load_model(self):
        """
        載入語言模型
        """
        try:
            logger.info(f"開始載入模型: {self.model_name}")
            start_time = time.time()

            # 檢查設備
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"使用設備: {device}")

            # 載入模型
            self.model = models.transformers(
                self.model_name,
                device=device
            )

            load_time = time.time() - start_time
            logger.info(f"模型載入完成,耗時: {load_time:.2f} 秒")

        except Exception as e:
            logger.error(f"模型載入失敗: {str(e)}")
            raise

    def generate_choice(
        self,
        prompt: str,
        choices: List[str]
    ) -> str:
        """
        生成單一選擇

        Args:
            prompt: 輸入提示
            choices: 可選擇的選項列表

        Returns:
            選擇的結果
        """
        try:
            logger.info(f"生成選擇,選項數: {len(choices)}")

            # 創建選擇生成器
            generator = generate.choice(self.model, choices)

            # 生成結果
            result = generator(prompt)

            logger.info(f"選擇結果: {result}")
            return result

        except Exception as e:
            logger.error(f"選擇生成失敗: {str(e)}")
            raise

    def batch_generate_choices(
        self,
        prompts: List[str],
        choices: List[str]
    ) -> List[str]:
        """
        批量生成選擇

        Args:
            prompts: 提示列表
            choices: 選項列表

        Returns:
            選擇結果列表
        """
        results = []

        for prompt in prompts:
            result = self.generate_choice(prompt, choices)
            results.append(result)

        return results


# ==================== 情感分析器 ====================

class SentimentAnalyzer:
    """
    情感分析器

    使用選擇約束進行文本情感分析
    """

    # 情感類別定義
    SENTIMENTS = ["正面", "負面", "中性"]
    DETAILED_SENTIMENTS = [
        "非常正面", "正面", "略微正面",
        "中性",
        "略微負面", "負面", "非常負面"
    ]

    def __init__(self, manager: ChoiceConstraintManager):
        """
        初始化情感分析器

        Args:
            manager: 選擇約束管理器
        """
        self.manager = manager
        logger.info("情感分析器初始化完成")

    def analyze(
        self,
        text: str,
        detailed: bool = False
    ) -> str:
        """
        分析文本情感

        Args:
            text: 待分析文本
            detailed: 是否使用詳細分類

        Returns:
            情感類別
        """
        sentiments = self.DETAILED_SENTIMENTS if detailed else self.SENTIMENTS

        prompt = f"分析以下文本的情感: \"{text}\"\n情感:"

        result = self.manager.generate_choice(prompt, sentiments)

        logger.info(f"文本: {text[:50]}... -> 情感: {result}")
        return result

    def batch_analyze(
        self,
        texts: List[str],
        detailed: bool = False
    ) -> List[str]:
        """
        批量分析情感

        Args:
            texts: 文本列表
            detailed: 是否詳細分類

        Returns:
            情感列表
        """
        results = []

        for text in texts:
            sentiment = self.analyze(text, detailed)
            results.append(sentiment)

        return results

    def analyze_with_confidence(
        self,
        text: str
    ) -> Dict[str, Any]:
        """
        分析情感並提供置信度

        Args:
            text: 待分析文本

        Returns:
            包含情感和元數據的字典
        """
        start_time = time.time()
        sentiment = self.analyze(text, detailed=False)
        analysis_time = time.time() - start_time

        return {
            "text": text,
            "sentiment": sentiment,
            "analysis_time": analysis_time,
            "timestamp": datetime.now().isoformat()
        }


# ==================== 意圖識別器 ====================

class IntentClassifier:
    """
    意圖識別器

    識別用戶輸入的意圖
    """

    # 意圖類別
    INTENTS = [
        "查詢信息",
        "執行操作",
        "尋求幫助",
        "投訴抱怨",
        "閒聊",
        "其他"
    ]

    # 詳細意圖類別
    DETAILED_INTENTS = {
        "查詢信息": ["查詢訂單", "查詢產品", "查詢價格", "查詢庫存"],
        "執行操作": ["下訂單", "取消訂單", "修改訂單", "退貨"],
        "尋求幫助": ["使用說明", "技術支持", "售後服務"],
        "投訴抱怨": ["產品質量", "服務態度", "配送問題"]
    }

    def __init__(self, manager: ChoiceConstraintManager):
        """
        初始化意圖識別器

        Args:
            manager: 選擇約束管理器
        """
        self.manager = manager
        logger.info("意圖識別器初始化完成")

    def classify(self, text: str) -> str:
        """
        識別文本意圖

        Args:
            text: 用戶輸入文本

        Returns:
            意圖類別
        """
        prompt = f"識別以下文本的用戶意圖: \"{text}\"\n意圖:"

        result = self.manager.generate_choice(prompt, self.INTENTS)

        logger.info(f"文本: {text[:50]}... -> 意圖: {result}")
        return result

    def classify_hierarchical(self, text: str) -> Tuple[str, Optional[str]]:
        """
        層級意圖識別

        先識別主要意圖,再識別細分意圖

        Args:
            text: 用戶輸入文本

        Returns:
            (主要意圖, 細分意圖) 元組
        """
        # 第一層:主要意圖
        main_intent = self.classify(text)

        # 第二層:細分意圖
        sub_intent = None
        if main_intent in self.DETAILED_INTENTS:
            sub_choices = self.DETAILED_INTENTS[main_intent]
            prompt = f"進一步細分以下文本的意圖: \"{text}\"\n細分意圖:"
            sub_intent = self.manager.generate_choice(prompt, sub_choices)

        logger.info(f"層級意圖: {main_intent} -> {sub_intent}")
        return main_intent, sub_intent

    def classify_with_metadata(self, text: str) -> Dict[str, Any]:
        """
        識別意圖並返回完整元數據

        Args:
            text: 用戶輸入文本

        Returns:
            包含意圖和元數據的字典
        """
        start_time = time.time()

        # 層級分類
        main_intent, sub_intent = self.classify_hierarchical(text)

        classification_time = time.time() - start_time

        return {
            "text": text,
            "main_intent": main_intent,
            "sub_intent": sub_intent,
            "classification_time": classification_time,
            "timestamp": datetime.now().isoformat()
        }


# ==================== 文本分類器 ====================

class TextClassifier:
    """
    通用文本分類器

    支持自定義類別的文本分類
    """

    def __init__(self, manager: ChoiceConstraintManager):
        """
        初始化文本分類器

        Args:
            manager: 選擇約束管理器
        """
        self.manager = manager
        logger.info("文本分類器初始化完成")

    def classify(
        self,
        text: str,
        categories: List[str],
        task_description: str = "分類文本"
    ) -> str:
        """
        分類文本

        Args:
            text: 待分類文本
            categories: 類別列表
            task_description: 任務描述

        Returns:
            分類結果
        """
        prompt = f"{task_description}: \"{text}\"\n類別:"

        result = self.manager.generate_choice(prompt, categories)

        logger.info(f"分類: {text[:50]}... -> {result}")
        return result

    def multi_label_classify(
        self,
        text: str,
        categories: List[str]
    ) -> List[str]:
        """
        多標籤分類

        對每個類別判斷是否適用

        Args:
            text: 待分類文本
            categories: 類別列表

        Returns:
            適用的類別列表
        """
        results = []

        for category in categories:
            prompt = f"文本 \"{text}\" 是否屬於類別 \"{category}\"?"
            is_applicable = self.manager.generate_choice(
                prompt,
                ["是", "否"]
            )

            if is_applicable == "是":
                results.append(category)

        logger.info(f"多標籤分類: {text[:50]}... -> {results}")
        return results


# ==================== 問答分類器 ====================

class QAClassifier:
    """
    問答分類器

    處理問答相關的分類任務
    """

    # 問題類型
    QUESTION_TYPES = [
        "是非題",
        "選擇題",
        "開放性問題",
        "數值問題",
        "定義問題",
        "比較問題"
    ]

    # 答案類型
    ANSWER_TYPES = [
        "事實性回答",
        "意見性回答",
        "解釋性回答",
        "步驟性回答"
    ]

    def __init__(self, manager: ChoiceConstraintManager):
        """
        初始化問答分類器

        Args:
            manager: 選擇約束管理器
        """
        self.manager = manager
        logger.info("問答分類器初始化完成")

    def classify_question_type(self, question: str) -> str:
        """
        分類問題類型

        Args:
            question: 問題文本

        Returns:
            問題類型
        """
        prompt = f"判斷以下問題的類型: \"{question}\"\n類型:"

        result = self.manager.generate_choice(prompt, self.QUESTION_TYPES)

        logger.info(f"問題類型: {result}")
        return result

    def classify_answer_type(self, answer: str) -> str:
        """
        分類答案類型

        Args:
            answer: 答案文本

        Returns:
            答案類型
        """
        prompt = f"判斷以下答案的類型: \"{answer}\"\n類型:"

        result = self.manager.generate_choice(prompt, self.ANSWER_TYPES)

        logger.info(f"答案類型: {result}")
        return result

    def verify_answer(self, question: str, answer: str) -> str:
        """
        驗證答案是否正確

        Args:
            question: 問題
            answer: 答案

        Returns:
            驗證結果
        """
        prompt = f"問題: \"{question}\"\n答案: \"{answer}\"\n這個答案是否正確?"

        result = self.manager.generate_choice(
            prompt,
            ["正確", "不正確", "部分正確", "無法判斷"]
        )

        logger.info(f"答案驗證: {result}")
        return result


# ==================== 統計分析器 ====================

class StatisticsAnalyzer:
    """
    統計分析器

    分析分類結果並提供統計信息
    """

    @staticmethod
    def analyze_distribution(
        results: List[str]
    ) -> Dict[str, Any]:
        """
        分析結果分佈

        Args:
            results: 分類結果列表

        Returns:
            統計信息字典
        """
        counter = Counter(results)
        total = len(results)

        distribution = {
            category: {
                "count": count,
                "percentage": (count / total) * 100
            }
            for category, count in counter.items()
        }

        return {
            "total": total,
            "unique_categories": len(counter),
            "distribution": distribution,
            "most_common": counter.most_common(3)
        }

    @staticmethod
    def print_statistics(stats: Dict[str, Any]):
        """
        打印統計信息

        Args:
            stats: 統計信息字典
        """
        print("\n" + "="*60)
        print("統計分析結果")
        print("="*60)
        print(f"總數: {stats['total']}")
        print(f"類別數: {stats['unique_categories']}")
        print("\n分佈:")

        for category, info in stats['distribution'].items():
            print(f"  {category}: {info['count']} ({info['percentage']:.2f}%)")

        print("\n最常見類別:")
        for category, count in stats['most_common']:
            print(f"  {category}: {count}")

        print("="*60)


# ==================== 示例運行器 ====================

def run_sentiment_analysis_example():
    """
    運行情感分析示例
    """
    print("\n" + "="*60)
    print("示例 1: 情感分析")
    print("="*60)

    # 初始化
    manager = ChoiceConstraintManager()
    analyzer = SentimentAnalyzer(manager)

    # 測試文本
    texts = [
        "這個產品非常好用,我很滿意!",
        "質量太差了,完全不值這個價錢",
        "還可以,沒有什麼特別的",
        "超級喜歡,已經推薦給朋友了",
        "有點失望,和描述不符"
    ]

    # 分析情感
    print("\n基本情感分析:")
    for text in texts:
        sentiment = analyzer.analyze(text)
        print(f"  文本: {text}")
        print(f"  情感: {sentiment}\n")

    # 詳細情感分析
    print("\n詳細情感分析:")
    for text in texts[:2]:
        sentiment = analyzer.analyze(text, detailed=True)
        print(f"  文本: {text}")
        print(f"  情感: {sentiment}\n")

    # 批量分析
    print("\n批量分析:")
    sentiments = analyzer.batch_analyze(texts)
    stats = StatisticsAnalyzer.analyze_distribution(sentiments)
    StatisticsAnalyzer.print_statistics(stats)


def run_intent_classification_example():
    """
    運行意圖識別示例
    """
    print("\n" + "="*60)
    print("示例 2: 意圖識別")
    print("="*60)

    # 初始化
    manager = ChoiceConstraintManager()
    classifier = IntentClassifier(manager)

    # 測試文本
    texts = [
        "我的訂單什麼時候能到?",
        "幫我取消昨天的訂單",
        "這個功能怎麼使用?",
        "你們的服務態度太差了!",
        "今天天氣不錯啊",
        "這個產品有折扣嗎?"
    ]

    # 基本意圖識別
    print("\n基本意圖識別:")
    for text in texts:
        intent = classifier.classify(text)
        print(f"  文本: {text}")
        print(f"  意圖: {intent}\n")

    # 層級意圖識別
    print("\n層級意圖識別:")
    for text in texts[:4]:
        main_intent, sub_intent = classifier.classify_hierarchical(text)
        print(f"  文本: {text}")
        print(f"  主意圖: {main_intent}")
        print(f"  子意圖: {sub_intent}\n")


def run_text_classification_example():
    """
    運行文本分類示例
    """
    print("\n" + "="*60)
    print("示例 3: 文本分類")
    print("="*60)

    # 初始化
    manager = ChoiceConstraintManager()
    classifier = TextClassifier(manager)

    # 新聞分類
    news_categories = ["科技", "體育", "財經", "娛樂", "健康"]
    news_texts = [
        "蘋果公司發布新款 iPhone",
        "NBA 總決賽今晚開打",
        "股市今日大漲 3%",
        "新電影票房破億",
        "研究發現每天運動有益健康"
    ]

    print("\n新聞分類:")
    for text in news_texts:
        category = classifier.classify(text, news_categories, "分類新聞")
        print(f"  文本: {text}")
        print(f"  類別: {category}\n")

    # 多標籤分類
    print("\n多標籤分類:")
    tags = ["技術", "商業", "創新", "移動設備"]
    text = "蘋果公司推出革命性的新款 iPhone,採用最新技術"

    labels = classifier.multi_label_classify(text, tags)
    print(f"  文本: {text}")
    print(f"  標籤: {', '.join(labels)}\n")


def main():
    """
    主函數
    """
    try:
        print("\n開始運行選擇約束示例...")

        # 運行各個示例
        run_sentiment_analysis_example()
        run_intent_classification_example()
        run_text_classification_example()

        print("\n" + "="*60)
        print("所有示例運行完成!")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\n用戶中斷執行")
    except Exception as e:
        print(f"\n錯誤: {str(e)}")
        logger.error(f"主程序錯誤: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
