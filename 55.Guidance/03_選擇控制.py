#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Guidance 選擇控制示例
====================================================

本模塊展示 Guidance 的選擇控制功能，這是框架最強大的特性之一:
1. select() 函數基礎用法
2. 單選和多選場景
3. 條件式選擇鏈
4. 選擇驗證和錯誤處理
5. 動態選項生成
6. 分類任務應用
7. 決策樹實現
8. 選擇結果分析

select() 函數通過 token 級約束保證模型只能從預定義選項中選擇，
實現 100% 的準確率，這在傳統提示工程中幾乎不可能達到。

作者: Guidance 示例團隊
日期: 2025-01-01
"""

import os
import sys
from typing import List, Dict, Any, Optional, Tuple
import json
from collections import Counter
from datetime import datetime

try:
    from guidance import models, gen, select, user, assistant, system
    import guidance
except ImportError:
    print("錯誤: 請先安裝 guidance 庫")
    sys.exit(1)


class SelectionController:
    """
    選擇控制演示類

    展示 Guidance select() 函數的各種應用場景和最佳實踐。

    Attributes:
        model_name: 模型名稱
        api_key: API 密鑰
        selection_history: 選擇歷史記錄
    """

    def __init__(self, model_name: str = "gpt-4", api_key: Optional[str] = None):
        """初始化選擇控制器"""
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.selection_history: List[Dict] = []

    def example_basic_selection(self) -> None:
        """
        示例 1: 基本選擇控制

        演示 select() 函數的基本用法，包括二元選擇和多選項。
        """
        print(f"\n{'='*60}")
        print("示例 1: 基本選擇控制")
        print(f"{'='*60}\n")

        # 二元選擇 (是/否)
        print("二元選擇示例:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "Python 是動態類型語言嗎? "
        lm += select(["是", "否"], name="answer1")

        print(f"Q: Python 是動態類型語言嗎?")
        print(f"A: {lm['answer1']}\n")

        # 多選項選擇
        print("多選項示例:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "以下哪個是 NoSQL 數據庫? "
        lm += select([
            "MySQL",
            "MongoDB",
            "PostgreSQL",
            "Oracle",
            "Redis"
        ], name="nosql_db")

        print(f"Q: 以下哪個是 NoSQL 數據庫?")
        print(f"A: {lm['nosql_db']}\n")

        # 英文選項
        print("英文選項示例:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "What is the time complexity of binary search? "
        lm += select([
            "O(1)",
            "O(log n)",
            "O(n)",
            "O(n log n)",
            "O(n^2)"
        ], name="complexity")

        print(f"Q: What is the time complexity of binary search?")
        print(f"A: {lm['complexity']}\n")

        # 記錄選擇歷史
        self.selection_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "basic",
            "selections": {
                "answer1": lm["answer1"] if "answer1" in dir(lm) else None,
                "nosql_db": lm["nosql_db"],
                "complexity": lm["complexity"]
            }
        })

    def example_classification_tasks(self) -> Dict[str, Any]:
        """
        示例 2: 分類任務

        演示如何使用 select() 實現各種分類任務。
        這是 Guidance 最常見的應用場景之一。

        Returns:
            分類結果字典
        """
        print(f"\n{'='*60}")
        print("示例 2: 分類任務")
        print(f"{'='*60}\n")

        # 情感分析
        print("情感分析:")
        texts = [
            "這個產品真是太棒了，我非常喜歡!",
            "質量很差，完全不值這個價錢。",
            "還行吧，沒什麼特別的。"
        ]

        sentiments = []
        for text in texts:
            lm = models.OpenAI(self.model_name, api_key=self.api_key)
            lm += f"文本: {text}\n"
            lm += "情感: "
            lm += select(["正面", "負面", "中性"], name="sentiment")

            sentiments.append(lm["sentiment"])
            print(f"  文本: {text}")
            print(f"  情感: {lm['sentiment']}\n")

        # 主題分類
        print("\n主題分類:")
        articles = [
            "科學家發現新的系外行星，可能適合生命存在",
            "股市今日大漲，科技股領漲",
            "新型 AI 模型在圖像識別領域創下紀錄"
        ]

        topics = []
        topic_options = ["科技", "財經", "體育", "娛樂", "科學"]

        for article in articles:
            lm = models.OpenAI(self.model_name, api_key=self.api_key)
            lm += f"文章: {article}\n"
            lm += "分類: "
            lm += select(topic_options, name="topic")

            topics.append(lm["topic"])
            print(f"  文章: {article}")
            print(f"  分類: {lm['topic']}\n")

        # 優先級分類
        print("\n優先級分類:")
        tasks = [
            "修復生產環境的嚴重 bug",
            "更新文檔",
            "客戶要求的緊急功能"
        ]

        priorities = []
        for task in tasks:
            lm = models.OpenAI(self.model_name, api_key=self.api_key)
            lm += f"任務: {task}\n"
            lm += "優先級: "
            lm += select(["緊急", "高", "中", "低"], name="priority")

            priorities.append(lm["priority"])
            print(f"  任務: {task}")
            print(f"  優先級: {lm['priority']}\n")

        # 語言檢測
        print("\n語言檢測:")
        multilingual_texts = [
            "Hello, how are you?",
            "你好，最近怎麼樣?",
            "Bonjour, comment allez-vous?"
        ]

        languages = []
        for text in multilingual_texts:
            lm = models.OpenAI(self.model_name, api_key=self.api_key)
            lm += f"文本: {text}\n"
            lm += "語言: "
            lm += select(["英文", "中文", "法文", "德文", "日文"], name="language")

            languages.append(lm["language"])
            print(f"  文本: {text}")
            print(f"  語言: {lm['language']}\n")

        results = {
            "sentiments": sentiments,
            "topics": topics,
            "priorities": priorities,
            "languages": languages,
            "timestamp": datetime.now().isoformat()
        }

        return results

    def example_conditional_selection_chain(self) -> None:
        """
        示例 3: 條件式選擇鏈

        演示如何基於前一個選擇結果來決定後續的選擇選項。
        這可以實現複雜的決策樹邏輯。
        """
        print(f"\n{'='*60}")
        print("示例 3: 條件式選擇鏈")
        print(f"{'='*60}\n")

        # 技術問題診斷
        print("技術問題診斷流程:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "步驟 1: 問題類型是? "
        lm += select(["硬件", "軟件", "網絡"], name="problem_type")

        print(f"問題類型: {lm['problem_type']}")

        # 根據問題類型選擇不同的後續選項
        if lm["problem_type"] == "硬件":
            lm += "\n步驟 2: 硬件類型? "
            lm += select(["CPU", "內存", "硬盤", "顯卡"], name="hardware_type")
            print(f"硬件類型: {lm['hardware_type']}")

            lm += "\n步驟 3: 問題嚴重程度? "
            lm += select(["輕微", "中等", "嚴重"], name="severity")
            print(f"嚴重程度: {lm['severity']}")

        elif lm["problem_type"] == "軟件":
            lm += "\n步驟 2: 軟件類型? "
            lm += select(["操作系統", "應用程序", "驅動程序"], name="software_type")
            print(f"軟件類型: {lm['software_type']}")

            lm += "\n步驟 3: 是否嘗試重啟? "
            lm += select(["是", "否"], name="restarted")
            print(f"是否重啟: {lm['restarted']}")

        else:  # 網絡
            lm += "\n步驟 2: 網絡類型? "
            lm += select(["有線", "無線", "VPN"], name="network_type")
            print(f"網絡類型: {lm['network_type']}")

            lm += "\n步驟 3: 其他設備是否正常? "
            lm += select(["是", "否", "不確定"], name="other_devices")
            print(f"其他設備: {lm['other_devices']}")

        print(f"\n診斷完成!")

        # 購物建議系統
        print("\n\n購物建議系統:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += "你想買什麼類型的產品? "
        lm += select(["電子產品", "服裝", "書籍", "食品"], name="category")

        print(f"類別: {lm['category']}")

        if lm["category"] == "電子產品":
            lm += "\n預算範圍? "
            lm += select(["$0-100", "$100-500", "$500-1000", "$1000+"], name="budget")
            print(f"預算: {lm['budget']}")

            lm += "\n用途? "
            lm += select(["工作", "娛樂", "學習"], name="purpose")
            print(f"用途: {lm['purpose']}")

        elif lm["category"] == "服裝":
            lm += "\n性別? "
            lm += select(["男", "女", "中性"], name="gender")
            print(f"性別: {lm['gender']}")

            lm += "\n季節? "
            lm += select(["春", "夏", "秋", "冬"], name="season")
            print(f"季節: {lm['season']}")

        print(f"\n建議生成中...")

    def example_multi_level_selection(self) -> None:
        """
        示例 4: 多層級選擇

        演示如何構建多層級的選擇結構。
        """
        print(f"\n{'='*60}")
        print("示例 4: 多層級選擇")
        print(f"{'='*60}\n")

        # 地理位置選擇
        print("地理位置選擇器:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        # 第一層: 大陸
        lm += "選擇大陸: "
        lm += select(["亞洲", "歐洲", "北美洲", "南美洲"], name="continent")
        print(f"大陸: {lm['continent']}")

        # 第二層: 國家
        country_options = {
            "亞洲": ["中國", "日本", "韓國", "印度"],
            "歐洲": ["英國", "法國", "德國", "意大利"],
            "北美洲": ["美國", "加拿大", "墨西哥"],
            "南美洲": ["巴西", "阿根廷", "智利"]
        }

        lm += "\n選擇國家: "
        lm += select(country_options[lm["continent"]], name="country")
        print(f"國家: {lm['country']}")

        # 第三層: 城市
        city_options = {
            "中國": ["北京", "上海", "深圳", "台北"],
            "日本": ["東京", "大阪", "京都"],
            "美國": ["紐約", "洛杉磯", "舊金山"],
            # ... 其他國家的城市
        }

        if lm["country"] in city_options:
            lm += "\n選擇城市: "
            lm += select(city_options[lm["country"]], name="city")
            print(f"城市: {lm['city']}")

        print(f"\n完整位置: {lm['continent']} > {lm['country']}", end="")
        if "city" in dir(lm):
            print(f" > {lm['city']}")
        else:
            print()

        # 技能樹選擇
        print("\n\n技能樹選擇:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        # 主技能
        lm += "選擇主技能方向: "
        lm += select(["前端開發", "後端開發", "數據科學", "DevOps"], name="main_skill")
        print(f"\n主技能: {lm['main_skill']}")

        # 子技能
        sub_skills = {
            "前端開發": ["React", "Vue", "Angular"],
            "後端開發": ["Python", "Java", "Go"],
            "數據科學": ["機器學習", "深度學習", "數據工程"],
            "DevOps": ["Docker", "Kubernetes", "CI/CD"]
        }

        lm += "\n選擇專精技能: "
        lm += select(sub_skills[lm["main_skill"]], name="sub_skill")
        print(f"專精: {lm['sub_skill']}")

        # 難度級別
        lm += "\n選擇學習級別: "
        lm += select(["初級", "中級", "高級", "專家"], name="level")
        print(f"級別: {lm['level']}")

        print(f"\n技能路徑: {lm['main_skill']} → {lm['sub_skill']} ({lm['level']})")

    def example_dynamic_options(self) -> None:
        """
        示例 5: 動態選項生成

        演示如何在運行時動態生成選擇選項。
        """
        print(f"\n{'='*60}")
        print("示例 5: 動態選項生成")
        print(f"{'='*60}\n")

        # 從數據庫/API 獲取選項 (模擬)
        def get_available_courses(category: str) -> List[str]:
            """模擬從數據庫獲取可用課程"""
            courses_db = {
                "程式設計": ["Python 基礎", "Java 進階", "C++ 高級"],
                "數據分析": ["Excel 入門", "SQL 實戰", "Tableau 可視化"],
                "設計": ["Photoshop 技巧", "UI/UX 設計", "平面設計"]
            }
            return courses_db.get(category, [])

        # 動態課程選擇
        print("動態課程選擇:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        # 先選擇類別
        categories = ["程式設計", "數據分析", "設計"]
        lm += "選擇課程類別: "
        lm += select(categories, name="category")
        print(f"類別: {lm['category']}")

        # 動態獲取該類別的課程
        available_courses = get_available_courses(lm["category"])
        lm += "\n選擇具體課程: "
        lm += select(available_courses, name="course")
        print(f"課程: {lm['course']}")

        # 基於用戶歷史的推薦 (模擬)
        def get_personalized_options(user_id: str) -> List[str]:
            """模擬個性化推薦"""
            return ["推薦 A", "推薦 B", "推薦 C", "瀏覽所有"]

        print("\n\n個性化推薦:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        user_id = "user_123"
        personalized_options = get_personalized_options(user_id)

        lm += "為您推薦的選項: "
        lm += select(personalized_options, name="recommendation")
        print(f"選擇: {lm['recommendation']}")

        # 基於時間的選項
        from datetime import datetime

        current_hour = datetime.now().hour

        if 6 <= current_hour < 12:
            meal_options = ["早餐 A", "早餐 B", "早餐 C"]
            meal_type = "早餐"
        elif 12 <= current_hour < 18:
            meal_options = ["午餐 A", "午餐 B", "午餐 C"]
            meal_type = "午餐"
        else:
            meal_options = ["晚餐 A", "晚餐 B", "晚餐 C"]
            meal_type = "晚餐"

        print(f"\n\n當前時間: {current_hour}:00")
        print(f"推薦{meal_type}選項:")

        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += f"選擇{meal_type}: "
        lm += select(meal_options, name="meal")
        print(f"選擇: {lm['meal']}")

    def example_validation_and_confidence(self) -> None:
        """
        示例 6: 驗證和置信度

        演示如何結合選擇和置信度評估。
        """
        print(f"\n{'='*60}")
        print("示例 6: 驗證和置信度")
        print(f"{'='*60}\n")

        # 答案 + 置信度
        questions = [
            "地球是平的嗎?",
            "量子計算機是否已經商用化?",
            "人工智能能否完全替代人類?"
        ]

        print("答案與置信度評估:")
        for question in questions:
            lm = models.OpenAI(self.model_name, api_key=self.api_key)

            lm += f"問題: {question}\n"
            lm += "答案: "
            lm += select(["是", "否", "不確定"], name="answer")

            lm += "\n置信度: "
            lm += select(["非常確定", "比較確定", "不太確定", "完全不確定"], name="confidence")

            print(f"\nQ: {question}")
            print(f"A: {lm['answer']}")
            print(f"置信度: {lm['confidence']}")

        # 分類 + 理由類型
        print("\n\n分類與理由:")
        text = "這個產品質量很好，但是價格太貴了。"

        lm = models.OpenAI(self.model_name, api_key=self.api_key)
        lm += f"評論: {text}\n"
        lm += "整體情感: "
        lm += select(["正面", "負面", "混合"], name="sentiment")

        lm += "\n主要考慮因素: "
        lm += select(["質量", "價格", "服務", "品牌"], name="factor")

        print(f"評論: {text}")
        print(f"情感: {lm['sentiment']}")
        print(f"主要因素: {lm['factor']}")

    def example_batch_classification(self) -> Dict[str, Any]:
        """
        示例 7: 批量分類

        演示如何高效地對多個項目進行分類。

        Returns:
            批量分類結果
        """
        print(f"\n{'='*60}")
        print("示例 7: 批量分類")
        print(f"{'='*60}\n")

        # 批量郵件分類
        emails = [
            {"subject": "會議通知: 明天下午3點", "sender": "boss@company.com"},
            {"subject": "恭喜中獎! 點擊領取", "sender": "unknown@spam.com"},
            {"subject": "項目進度報告", "sender": "colleague@company.com"},
            {"subject": "您的訂單已發貨", "sender": "noreply@shop.com"},
            {"subject": "緊急: 服務器故障", "sender": "ops@company.com"}
        ]

        print("郵件分類:")
        classifications = []

        for i, email in enumerate(emails):
            lm = models.OpenAI(self.model_name, api_key=self.api_key)

            lm += f"主題: {email['subject']}\n"
            lm += f"發件人: {email['sender']}\n"
            lm += "分類: "
            lm += select(["工作", "垃圾郵件", "通知", "個人"], name="category")

            lm += "\n優先級: "
            lm += select(["高", "中", "低"], name="priority")

            classifications.append({
                "email": email,
                "category": lm["category"],
                "priority": lm["priority"]
            })

            print(f"\n郵件 {i+1}:")
            print(f"  主題: {email['subject']}")
            print(f"  分類: {lm['category']}")
            print(f"  優先級: {lm['priority']}")

        # 統計分析
        categories = [c["category"] for c in classifications]
        priorities = [c["priority"] for c in classifications]

        print(f"\n\n分類統計:")
        print(f"  類別分布: {dict(Counter(categories))}")
        print(f"  優先級分布: {dict(Counter(priorities))}")

        return {
            "total": len(classifications),
            "classifications": classifications,
            "statistics": {
                "categories": dict(Counter(categories)),
                "priorities": dict(Counter(priorities))
            }
        }

    def example_decision_tree(self) -> None:
        """
        示例 8: 決策樹實現

        演示如何使用選擇控制實現完整的決策樹。
        """
        print(f"\n{'='*60}")
        print("示例 8: 決策樹 - 職業建議系統")
        print(f"{'='*60}\n")

        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        print("職業建議決策樹:\n")

        # 節點 1: 興趣領域
        lm += "你對什麼領域最感興趣? "
        lm += select(["技術", "商業", "創意"], name="interest")
        print(f"興趣領域: {lm['interest']}")

        if lm["interest"] == "技術":
            # 技術分支
            lm += "\n你更喜歡? "
            lm += select(["寫代碼", "分析數據", "設計系統"], name="tech_preference")
            print(f"技術偏好: {lm['tech_preference']}")

            if lm["tech_preference"] == "寫代碼":
                lm += "\n偏好的工作環境? "
                lm += select(["創業公司", "大公司", "自由職業"], name="env")
                recommendation = "軟件工程師"

            elif lm["tech_preference"] == "分析數據":
                lm += "\n數學能力? "
                lm += select(["強", "一般"], name="math")
                recommendation = "數據科學家" if lm["math"] == "強" else "數據分析師"

            else:  # 設計系統
                recommendation = "系統架構師"

        elif lm["interest"] == "商業":
            # 商業分支
            lm += "\n你更擅長? "
            lm += select(["人際交往", "數字分析", "戰略規劃"], name="business_skill")
            print(f"商業技能: {lm['business_skill']}")

            if lm["business_skill"] == "人際交往":
                recommendation = "銷售經理"
            elif lm["business_skill"] == "數字分析":
                recommendation = "財務分析師"
            else:
                recommendation = "戰略顧問"

        else:  # 創意
            # 創意分支
            lm += "\n你的創意類型? "
            lm += select(["視覺設計", "文字創作", "音樂藝術"], name="creative_type")
            print(f"創意類型: {lm['creative_type']}")

            recommendation = {
                "視覺設計": "UI/UX 設計師",
                "文字創作": "內容創作者",
                "音樂藝術": "多媒體藝術家"
            }[lm["creative_type"]]

        print(f"\n{'='*60}")
        print(f"建議職業: {recommendation}")
        print(f"{'='*60}")

    def run_all_examples(self) -> None:
        """運行所有示例"""
        print(f"\n{'='*60}")
        print("Guidance 選擇控制 - 完整示例")
        print(f"{'='*60}")

        self.example_basic_selection()
        classification_results = self.example_classification_tasks()
        self.example_conditional_selection_chain()
        self.example_multi_level_selection()
        self.example_dynamic_options()
        self.example_validation_and_confidence()
        batch_results = self.example_batch_classification()
        self.example_decision_tree()

        print(f"\n{'='*60}")
        print("執行摘要")
        print(f"{'='*60}")
        print(f"✓ 所有選擇控制示例執行完成!")
        print(f"\n批量分類統計:")
        print(json.dumps(batch_results["statistics"], indent=2, ensure_ascii=False))


def main():
    """主函數"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║         Guidance 框架 - 選擇控制示例                       ║
    ║                                                            ║
    ║  select() 函數保證 100% 準確率的選擇控制                   ║
    ║  適用於分類、決策樹、表單等各種場景                        ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        return

    controller = SelectionController(
        model_name="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    try:
        controller.run_all_examples()
    except KeyboardInterrupt:
        print("\n\n⚠️  用戶中斷執行")
    except Exception as e:
        print(f"\n✗ 執行出錯: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
