"""
Rasa NLU 訓練 - 自然語言理解詳解

本文件涵蓋：
1. 意圖（Intent）識別
2. 實體（Entity）提取
3. 訓練數據格式和最佳實踐
4. NLU Pipeline 配置
5. 模型評估和優化
"""

import yaml
import json
from typing import List, Dict, Any


# ==================== 1. 意圖識別 ====================

def intent_classification_examples():
    """
    意圖分類示例 - 識別用戶想要做什麼
    """
    print("=" * 60)
    print("意圖識別（Intent Classification）")
    print("=" * 60)

    # 基本意圖定義
    basic_intents = """
version: "3.1"

nlu:
# 問候意圖
- intent: greet
  examples: |
    - 你好
    - 嗨
    - 早安
    - 午安
    - 晚安
    - Hello
    - Hi there
    - 您好啊

# 告別意圖
- intent: goodbye
  examples: |
    - 再見
    - 拜拜
    - 回見
    - bye
    - see you
    - 下次見

# 感謝意圖
- intent: thanks
  examples: |
    - 謝謝
    - 感謝
    - 多謝
    - 太感謝了
    - thanks
    - thank you
    - 謝謝你的幫助

# 查詢訂單狀態
- intent: check_order_status
  examples: |
    - 我的訂單在哪裡？
    - 查詢訂單狀態
    - 訂單進度如何？
    - 我想查看我的訂單
    - 能幫我查一下訂單嗎
    - where is my order
    - order status

# 產品查詢
- intent: product_inquiry
  examples: |
    - 你們有什麼產品？
    - 介紹一下你們的產品
    - 產品列表
    - 有哪些商品
    - 我想看看產品
    - show me products
    - what do you sell
"""

    print("\n基本意圖定義:")
    print(basic_intents)

    # 意圖分類最佳實踐
    print("\n" + "=" * 60)
    print("意圖分類最佳實踐")
    print("=" * 60)
    print("""
    1. 每個意圖至少 10-20 個訓練示例
    2. 涵蓋不同的表達方式
    3. 包含同義詞和變體
    4. 考慮口語化和正式表達
    5. 平衡各個意圖的數據量
    6. 避免意圖重疊
    7. 使用有意義的意圖名稱
    """)


def entity_extraction_examples():
    """
    實體提取示例 - 從用戶輸入中提取關鍵信息
    """
    print("\n" + "=" * 60)
    print("實體提取（Entity Extraction）")
    print("=" * 60)

    entity_examples = """
version: "3.1"

nlu:
# 預訂餐廳 - 帶有實體標註
- intent: book_restaurant
  examples: |
    - 我想訂 [明天](date) [晚上7點](time) [2個人](number) 的位子
    - 預定 [今天](date) [中午](time) [4人](number) 的座位
    - 幫我訂 [下週五](date) [晚上8點](time) 的桌子
    - book a table for [2](number) on [Friday](date) at [7pm](time)
    - [3個人](number) [今晚](date:tonight) [6點](time)

# 產品搜索 - 帶有產品名稱實體
- intent: search_product
  examples: |
    - 我想買 [iPhone](product)
    - 有 [筆記本電腦](product) 嗎？
    - 搜索 [藍牙耳機](product)
    - 找一下 [運動鞋](product)
    - show me [laptops](product)

# 地點查詢 - 帶有城市實體
- intent: check_weather
  examples: |
    - [台北](city) 的天氣如何？
    - [上海](city) 今天天氣
    - [Beijing](city) weather
    - 查詢 [高雄](city) 天氣
    - [新竹](city) 會下雨嗎？

# 帶有同義詞的實體
- synonym: "台北"
  examples: |
    - Taipei
    - 台北市
    - TPE

- synonym: "上海"
  examples: |
    - Shanghai
    - 上海市
    - 滬

# 正則表達式實體 - 郵政編碼
- regex: zipcode
  examples: |
    - \\d{3,5}

# 正則表達式實體 - 電話號碼
- regex: phone_number
  examples: |
    - \\d{2,4}-\\d{6,8}
    - \\d{10}

# 查找實體（Lookup Tables）- 產品列表
- lookup: product
  examples: |
    - iPhone 14
    - MacBook Pro
    - iPad Air
    - AirPods
    - Apple Watch
"""

    print("\n實體提取示例:")
    print(entity_examples)

    # 實體類型說明
    print("\n" + "=" * 60)
    print("實體類型")
    print("=" * 60)
    print("""
    1. 自定義實體（Custom Entities）
       - 在訓練數據中手動標註
       - 格式: [實體值](實體類型)

    2. 同義詞（Synonyms）
       - 將不同的表達映射到標準值
       - 減少訓練數據需求

    3. 正則表達式（Regex）
       - 用於結構化數據（郵編、電話等）
       - 不需要大量訓練數據

    4. 查找表（Lookup Tables）
       - 用於有限的值集合
       - 提高特定實體的識別率

    5. 預訓練實體（Pretrained）
       - Duckling: 日期、時間、數字等
       - SpaCy: 人名、地名、組織等
    """)


# ==================== 2. NLU Pipeline 配置 ====================

def nlu_pipeline_configuration():
    """
    NLU Pipeline 配置詳解
    """
    print("\n" + "=" * 60)
    print("NLU Pipeline 配置")
    print("=" * 60)

    # 基礎 Pipeline（中文）
    basic_chinese_pipeline = {
        'language': 'zh',
        'pipeline': [
            # 1. 分詞器
            {'name': 'JiebaTokenizer'},

            # 2. 特徵提取
            {'name': 'CountVectorsFeaturizer'},
            {'name': 'CountVectorsFeaturizer',
             'analyzer': 'char_wb',
             'min_ngram': 1,
             'max_ngram': 4},

            # 3. 意圖分類器和實體提取器
            {'name': 'DIETClassifier',
             'epochs': 100},

            # 4. 實體同義詞映射
            {'name': 'EntitySynonymMapper'}
        ]
    }

    print("\n基礎 Pipeline（中文）:")
    print(yaml.dump(basic_chinese_pipeline, allow_unicode=True))

    # 進階 Pipeline（中文 + 預訓練模型）
    advanced_pipeline = {
        'language': 'zh',
        'pipeline': [
            # 分詞
            {'name': 'JiebaTokenizer'},

            # 字符級特徵
            {'name': 'CountVectorsFeaturizer',
             'analyzer': 'char_wb',
             'min_ngram': 1,
             'max_ngram': 4},

            # 詞級特徵
            {'name': 'CountVectorsFeaturizer'},

            # 正則表達式特徵
            {'name': 'RegexFeaturizer'},

            # 查找表特徵
            {'name': 'LexicalSyntacticFeaturizer'},

            # DIET 分類器（同時做意圖分類和實體提取）
            {'name': 'DIETClassifier',
             'epochs': 100,
             'entity_recognition': True,
             'constrain_similarities': True},

            # 實體同義詞
            {'name': 'EntitySynonymMapper'},

            # Response Selector（用於FAQ）
            {'name': 'ResponseSelector',
             'epochs': 100}
        ]
    }

    print("\n進階 Pipeline:")
    print(yaml.dump(advanced_pipeline, allow_unicode=True))

    # Pipeline 組件說明
    print("\n" + "=" * 60)
    print("Pipeline 組件說明")
    print("=" * 60)
    print("""
    【Tokenizers - 分詞器】
    - JiebaTokenizer: 中文分詞
    - WhitespaceTokenizer: 空格分詞（英文）
    - SpacyTokenizer: SpaCy 分詞

    【Featurizers - 特徵提取器】
    - CountVectorsFeaturizer: 詞袋模型
    - RegexFeaturizer: 正則表達式特徵
    - LexicalSyntacticFeaturizer: 詞法句法特徵
    - SpacyFeaturizer: SpaCy 詞向量

    【Classifiers - 分類器】
    - DIETClassifier: 雙重意圖實體轉換器（推薦）
    - SklearnIntentClassifier: 傳統 ML 分類器
    - FallbackClassifier: 回退分類器

    【Entity Extractors - 實體提取器】
    - DIETClassifier: 同時進行實體提取
    - CRFEntityExtractor: 條件隨機場
    - DucklingEntityExtractor: 日期、數字等
    - SpacyEntityExtractor: 預訓練實體

    【其他組件】
    - EntitySynonymMapper: 實體同義詞映射
    - ResponseSelector: 檢索式回覆選擇
    """)


# ==================== 3. 訓練數據最佳實踐 ====================

def training_data_best_practices():
    """
    訓練數據最佳實踐
    """
    print("\n" + "=" * 60)
    print("訓練數據最佳實踐")
    print("=" * 60)

    # 完整的訓練數據示例
    complete_training_data = """
version: "3.1"

nlu:
# ============ 客服機器人示例 ============

# 1. 問候（多樣性）
- intent: greet
  examples: |
    - 你好
    - 嗨
    - 早安
    - 午安
    - 您好
    - hi
    - hello
    - 安安
    - 哈囉

# 2. 訂單查詢（實體提取）
- intent: check_order
  examples: |
    - 我想查詢訂單 [ORD123456](order_id)
    - 訂單 [ORD789012](order_id) 在哪裡
    - 幫我查一下 [ORD345678](order_id)
    - 我的訂單編號是 [ORD901234](order_id)
    - check order [ORD567890](order_id)

# 3. 退款申請（多槽位）
- intent: request_refund
  examples: |
    - 我要退款訂單 [ORD123](order_id) 金額 [500元](amount)
    - 申請退款 [ORD456](order_id)
    - 想退貨 [ORD789](order_id)
    - refund order [ORD012](order_id)

# 4. 產品諮詢（組合實體）
- intent: product_question
  examples: |
    - [iPhone 14](product) 有 [藍色](color) 的嗎？
    - [MacBook](product) [16GB](spec) 版本多少錢？
    - [iPad](product) 支持 [5G](spec) 嗎？

# 5. 投訴（情感識別）
- intent: complaint
  examples: |
    - 你們的服務太差了
    - 我要投訴
    - 這是什麼爛產品
    - 非常不滿意
    - 我要找客服主管

# ============ 同義詞定義 ============
- synonym: "iPhone 14"
  examples: |
    - iPhone14
    - i14
    - 愛瘋14

- synonym: "退款"
  examples: |
    - 退錢
    - 退貨
    - refund
    - 取消訂單

# ============ 正則表達式 ============
- regex: order_id
  examples: |
    - ORD\\d{6}
    - ORDER-\\d{4,8}

- regex: amount
  examples: |
    - \\d+元
    - \\$\\d+
    - \\d+塊

# ============ 查找表 ============
- lookup: product
  examples: |
    - iPhone 14
    - iPhone 14 Pro
    - MacBook Air
    - MacBook Pro
    - iPad Air
    - AirPods Pro
"""

    print("\n完整訓練數據示例:")
    print(complete_training_data)

    # 數據質量檢查清單
    print("\n" + "=" * 60)
    print("數據質量檢查清單")
    print("=" * 60)
    print("""
    □ 每個意圖至少 10-20 個示例
    □ 涵蓋不同的表達方式
    □ 包含拼寫錯誤和口語化表達
    □ 實體標註一致
    □ 避免意圖重疊
    □ 平衡正負樣本
    □ 定期更新真實用戶數據
    □ 使用 rasa data validate 驗證
    """)


# ==================== 4. 模型評估 ====================

def model_evaluation():
    """
    模型評估和優化
    """
    print("\n" + "=" * 60)
    print("模型評估")
    print("=" * 60)

    print("\n1. NLU 評估命令:")
    print("   rasa test nlu --nlu data/nlu.yml")

    print("\n2. 交叉驗證:")
    print("   rasa test nlu --cross-validation --runs 3 --folds 5")

    print("\n3. 評估指標:")
    evaluation_metrics = """
    【意圖分類指標】
    - Accuracy（準確率）: 正確分類的比例
    - Precision（精確率）: 預測為正的樣本中實際為正的比例
    - Recall（召回率）: 實際為正的樣本中被正確預測的比例
    - F1-Score: 精確率和召回率的調和平均

    【實體提取指標】
    - Entity Recognition Precision
    - Entity Recognition Recall
    - Entity Recognition F1-Score

    【混淆矩陣】
    - 顯示哪些意圖容易混淆
    - 幫助識別需要改進的地方
    """
    print(evaluation_metrics)

    # 評估報告示例
    print("\n4. 評估報告示例:")
    print("""
    Intent Classification Report:

                    precision    recall  f1-score   support

           greet       0.95      0.90      0.92        20
         goodbye       0.88      0.92      0.90        15
          thanks       0.92      0.88      0.90        18
    check_order       0.85      0.88      0.86        16

        accuracy                           0.90        69
       macro avg       0.90      0.90      0.90        69
    weighted avg       0.90      0.90      0.90        69
    """)


def optimization_tips():
    """
    優化技巧
    """
    print("\n" + "=" * 60)
    print("NLU 優化技巧")
    print("=" * 60)

    tips = """
    【數據優化】
    1. 增加訓練數據量
       - 每個意圖 20-50 個示例
       - 收集真實用戶數據

    2. 平衡數據分布
       - 各意圖數據量相近
       - 避免數據傾斜

    3. 提高數據質量
       - 標註一致性
       - 涵蓋邊緣情況
       - 包含錯誤拼寫

    【Pipeline 優化】
    1. 選擇合適的組件
       - 中文使用 JiebaTokenizer
       - 英文使用 WhitespaceTokenizer

    2. 調整超參數
       - epochs: 訓練輪次
       - learning_rate: 學習率
       - batch_size: 批次大小

    3. 使用預訓練模型
       - SpaCy 語言模型
       - BERT/RoBERTa

    【意圖設計優化】
    1. 避免意圖過細或過粗
    2. 清晰的意圖邊界
    3. 使用 out_of_scope 意圖處理無關輸入

    【實體優化】
    1. 使用同義詞減少變體
    2. 結合正則表達式和查找表
    3. 考慮使用 Duckling 處理日期時間
    """
    print(tips)


# ==================== 5. 實戰示例 ====================

def practical_example():
    """
    實戰示例：電商客服 NLU
    """
    print("\n" + "=" * 60)
    print("實戰示例：電商客服 NLU")
    print("=" * 60)

    ecommerce_nlu = """
version: "3.1"

nlu:
# 查詢類
- intent: check_order_status
  examples: |
    - 我的訂單 [ORD123456](order_id) 到哪了
    - 查詢訂單 [ORD789012](order_id)
    - [ORD345678](order_id) 什麼時候到

- intent: track_shipment
  examples: |
    - 追蹤物流
    - 快遞到哪了
    - 什麼時候能收到

- intent: check_price
  examples: |
    - [iPhone 14](product) 多少錢
    - [筆記本](product) 價格
    - [藍牙耳機](product) 賣多少

# 操作類
- intent: cancel_order
  examples: |
    - 取消訂單 [ORD123](order_id)
    - 我不要 [ORD456](order_id) 了
    - 退訂 [ORD789](order_id)

- intent: modify_address
  examples: |
    - 修改收貨地址
    - 改地址到 [台北市](city) [信義區](district)
    - 換個收貨地址

- intent: request_invoice
  examples: |
    - 我要發票
    - 開發票給我
    - 需要統一編號 [12345678](tax_id)

# 問題類
- intent: product_inquiry
  examples: |
    - [iPhone](product) 有 [黑色](color) 的嗎
    - [iPad](product) 支持 [5G](feature) 嗎
    - [MacBook](product) [16GB](spec) 版本有貨嗎

- intent: return_policy
  examples: |
    - 退貨政策
    - 可以退貨嗎
    - 退款需要多久

- intent: payment_methods
  examples: |
    - 支持什麼付款方式
    - 可以用信用卡嗎
    - 能貨到付款嗎

# 實體定義
- synonym: "iPhone 14"
  examples: |
    - iPhone14
    - i14

- regex: order_id
  examples: |
    - ORD\\d{6}

- lookup: product
  examples: |
    - iPhone 14
    - MacBook Pro
    - iPad Air
"""

    print("\n電商客服 NLU 配置:")
    print(ecommerce_nlu)


# ==================== 主程序 ====================

def main():
    """
    主程序
    """
    print("\n" + "=" * 70)
    print("Rasa NLU 訓練 - 完整指南")
    print("=" * 70)

    # 1. 意圖和實體
    intent_classification_examples()
    entity_extraction_examples()

    # 2. Pipeline 配置
    nlu_pipeline_configuration()

    # 3. 訓練數據
    training_data_best_practices()

    # 4. 評估和優化
    model_evaluation()
    optimization_tips()

    # 5. 實戰示例
    practical_example()

    # 總結
    print("\n" + "=" * 70)
    print("總結")
    print("=" * 70)
    print("""
    NLU 是 Rasa 的核心組件，負責理解用戶輸入：

    【關鍵要點】
    1. 意圖識別：理解用戶想做什麼
    2. 實體提取：提取關鍵信息
    3. 訓練數據：質量比數量更重要
    4. Pipeline 配置：根據語言和需求選擇
    5. 持續優化：基於真實數據改進

    【下一步】
    - 學習 03_對話故事.py - 設計對話流程
    - 學習 04_自定義動作.py - 實現業務邏輯
    """)


if __name__ == "__main__":
    main()
