"""
Rasa 安裝入門 - 從零開始構建第一個對話機器人

本文件涵蓋：
1. Rasa 安裝和環境設置
2. 項目初始化和結構說明
3. 基本配置文件詳解
4. 創建第一個聊天機器人
5. 訓練和測試流程
"""

import subprocess
import os
from pathlib import Path
import yaml
import json


# ==================== 1. Rasa 安裝 ====================

def install_rasa():
    """
    安裝 Rasa 和相關依賴
    """
    print("=" * 50)
    print("Rasa 安裝步驟")
    print("=" * 50)

    # 步驟 1: 創建虛擬環境
    print("\n步驟 1: 創建虛擬環境")
    print("python -m venv rasa-env")
    print("source rasa-env/bin/activate  # Linux/Mac")
    print("rasa-env\\Scripts\\activate  # Windows")

    # 步驟 2: 升級 pip
    print("\n步驟 2: 升級 pip")
    print("pip install --upgrade pip")

    # 步驟 3: 安裝 Rasa
    print("\n步驟 3: 安裝 Rasa")
    print("pip install rasa")

    # 步驟 4: 安裝中文支持（Jieba）
    print("\n步驟 4: 安裝中文分詞")
    print("pip install jieba")

    # 步驟 5: 驗證安裝
    print("\n步驟 5: 驗證安裝")
    print("rasa --version")

    # 可選：安裝 Rasa X (用於可視化對話設計)
    print("\n可選：安裝 Rasa X")
    print("pip install rasa-x --extra-index-url https://pypi.rasa.com/simple")


# ==================== 2. 項目初始化 ====================

def initialize_project():
    """
    初始化 Rasa 項目
    """
    print("\n" + "=" * 50)
    print("初始化 Rasa 項目")
    print("=" * 50)

    # 創建新項目
    print("\n創建新項目:")
    print("rasa init --no-prompt")

    # 項目結構說明
    print("\n項目結構:")
    structure = """
    my-rasa-bot/
    ├── actions/              # 自定義動作代碼
    │   ├── __init__.py
    │   └── actions.py       # 自定義動作實現
    ├── data/                # 訓練數據
    │   ├── nlu.yml         # NLU 訓練數據（意圖和實體）
    │   ├── stories.yml     # 對話故事
    │   └── rules.yml       # 對話規則
    ├── models/              # 訓練好的模型
    ├── tests/               # 測試數據
    │   └── test_stories.yml
    ├── config.yml           # Pipeline 和 Policies 配置
    ├── domain.yml           # Domain 定義（意圖、實體、槽位、響應）
    ├── credentials.yml      # 通道憑證（Slack、Telegram 等）
    └── endpoints.yml        # 端點配置（Action Server、Tracker Store）
    """
    print(structure)


# ==================== 3. 配置文件詳解 ====================

def create_config_yml():
    """
    創建 config.yml - Pipeline 和 Policies 配置
    """
    config = {
        'language': 'zh',  # 語言設置
        'pipeline': [
            # 分詞器 - 中文使用 Jieba
            {'name': 'JiebaTokenizer'},

            # 特徵提取器
            {'name': 'CountVectorsFeaturizer'},
            {'name': 'CountVectorsFeaturizer',
             'analyzer': 'char_wb',
             'min_ngram': 1,
             'max_ngram': 4},

            # 意圖分類和實體提取 - DIET
            {'name': 'DIETClassifier',
             'epochs': 100,
             'constrain_similarities': True},

            # 實體同義詞映射
            {'name': 'EntitySynonymMapper'},

            # Response Selector（用於 FAQ）
            {'name': 'ResponseSelector',
             'epochs': 100}
        ],
        'policies': [
            # 記憶策略 - 記住訓練故事
            {'name': 'MemoizationPolicy'},

            # 規則策略 - 處理固定規則
            {'name': 'RulePolicy'},

            # 意外意圖策略
            {'name': 'UnexpecTEDIntentPolicy',
             'max_history': 5,
             'epochs': 100},

            # TED 策略 - 主要對話策略
            {'name': 'TEDPolicy',
             'max_history': 5,
             'epochs': 100,
             'constrain_similarities': True}
        ]
    }

    print("\n" + "=" * 50)
    print("config.yml 配置")
    print("=" * 50)
    print(yaml.dump(config, allow_unicode=True, default_flow_style=False))

    return config


def create_domain_yml():
    """
    創建 domain.yml - 定義機器人的"宇宙"
    """
    domain = {
        'version': '3.1',

        # 意圖定義
        'intents': [
            'greet',           # 問候
            'goodbye',         # 告別
            'affirm',          # 肯定
            'deny',            # 否定
            'mood_great',      # 心情好
            'mood_unhappy',    # 心情不好
            'bot_challenge'    # 詢問是否是機器人
        ],

        # 響應模板
        'responses': {
            'utter_greet': [
                {'text': '你好！我是你的助手，有什麼可以幫你的嗎？'},
                {'text': '嗨！很高興見到你！'}
            ],
            'utter_cheer_up': [
                {'text': '這裡有些東西能讓你開心：',
                 'image': 'https://i.imgur.com/nGF1K8f.jpg'}
            ],
            'utter_did_that_help': [
                {'text': '這樣有幫助嗎？'}
            ],
            'utter_happy': [
                {'text': '太好了！繼續保持！'}
            ],
            'utter_goodbye': [
                {'text': '再見！'},
                {'text': '拜拜！期待下次見面！'}
            ],
            'utter_iamabot': [
                {'text': '我是由 Rasa 構建的機器人。'}
            ]
        },

        # 會話配置
        'session_config': {
            'session_expiration_time': 60,  # 會話過期時間（分鐘）
            'carry_over_slots_to_new_session': True  # 保留槽位到新會話
        }
    }

    print("\n" + "=" * 50)
    print("domain.yml 配置")
    print("=" * 50)
    print(yaml.dump(domain, allow_unicode=True, default_flow_style=False))

    return domain


def create_nlu_data():
    """
    創建 NLU 訓練數據 (data/nlu.yml)
    """
    nlu_data = """
version: "3.1"

nlu:
- intent: greet
  examples: |
    - 你好
    - 嗨
    - 早安
    - 午安
    - 晚安
    - 嘿
    - 哈囉
    - 您好
    - Hi
    - Hello

- intent: goodbye
  examples: |
    - 再見
    - 拜拜
    - 下次見
    - 回頭見
    - 待會見
    - 88
    - bye
    - goodbye
    - see you

- intent: affirm
  examples: |
    - 是的
    - 對
    - 沒錯
    - 確認
    - 好的
    - 可以
    - yes
    - ok
    - 當然

- intent: deny
  examples: |
    - 不是
    - 不對
    - 否
    - 不要
    - 不可以
    - no
    - never
    - 不用了

- intent: mood_great
  examples: |
    - 我很好
    - 我很開心
    - 感覺很棒
    - 心情很好
    - 我很快樂
    - 超棒的
    - 非常好
    - 完美

- intent: mood_unhappy
  examples: |
    - 我很難過
    - 心情不好
    - 感覺糟糕
    - 我不開心
    - 很沮喪
    - 很失落
    - 不太好
    - 很糟

- intent: bot_challenge
  examples: |
    - 你是機器人嗎？
    - 你是真人嗎？
    - 我在跟誰說話？
    - 你是 AI 嗎？
    - 你是人類嗎？
    - are you a bot?
    - are you human?
"""

    print("\n" + "=" * 50)
    print("NLU 訓練數據 (data/nlu.yml)")
    print("=" * 50)
    print(nlu_data)

    return nlu_data


def create_stories_data():
    """
    創建對話故事 (data/stories.yml)
    """
    stories_data = """
version: "3.1"

stories:

- story: happy path
  steps:
  - intent: greet
  - action: utter_greet
  - intent: mood_great
  - action: utter_happy

- story: sad path 1
  steps:
  - intent: greet
  - action: utter_greet
  - intent: mood_unhappy
  - action: utter_cheer_up
  - action: utter_did_that_help
  - intent: affirm
  - action: utter_happy

- story: sad path 2
  steps:
  - intent: greet
  - action: utter_greet
  - intent: mood_unhappy
  - action: utter_cheer_up
  - action: utter_did_that_help
  - intent: deny
  - action: utter_goodbye
"""

    print("\n" + "=" * 50)
    print("對話故事 (data/stories.yml)")
    print("=" * 50)
    print(stories_data)

    return stories_data


def create_rules_data():
    """
    創建對話規則 (data/rules.yml)
    """
    rules_data = """
version: "3.1"

rules:

- rule: Say goodbye anytime the user says goodbye
  steps:
  - intent: goodbye
  - action: utter_goodbye

- rule: Say 'I am a bot' anytime the user challenges
  steps:
  - intent: bot_challenge
  - action: utter_iamabot
"""

    print("\n" + "=" * 50)
    print("對話規則 (data/rules.yml)")
    print("=" * 50)
    print(rules_data)

    return rules_data


# ==================== 4. 訓練和測試 ====================

def train_model():
    """
    訓練 Rasa 模型
    """
    print("\n" + "=" * 50)
    print("訓練模型")
    print("=" * 50)

    print("\n1. 訓練完整模型（NLU + Core）:")
    print("   rasa train")
    print("   - 訓練時間取決於數據量和 epochs 設置")
    print("   - 模型會保存在 models/ 目錄")

    print("\n2. 僅訓練 NLU:")
    print("   rasa train nlu")

    print("\n3. 僅訓練 Core:")
    print("   rasa train core")

    print("\n4. 強制重新訓練:")
    print("   rasa train --force")

    # 訓練過程示例
    print("\n訓練過程輸出示例:")
    print("""
    Training NLU model...
    Epochs: 100%|████████████████████| 100/100
    NLU model saved to models/nlu-20231215-123456.tar.gz

    Training Core model...
    Processed story blocks: 100%|████| 3/3
    Epochs: 100%|████████████████████| 100/100
    Core model saved to models/core-20231215-123456.tar.gz

    Model trained! Save to models/20231215-123456.tar.gz
    """)


def test_model():
    """
    測試 Rasa 模型
    """
    print("\n" + "=" * 50)
    print("測試模型")
    print("=" * 50)

    print("\n1. 命令行交互測試:")
    print("   rasa shell")
    print("   - 啟動交互式聊天界面")
    print("   - 輸入訊息測試機器人回應")

    print("\n2. 僅測試 NLU:")
    print("   rasa shell nlu")
    print("   - 查看意圖和實體識別結果")

    print("\n3. 調試模式:")
    print("   rasa shell --debug")
    print("   - 顯示詳細的對話流程信息")

    print("\n4. 交互示例:")
    print("""
    Your input ->  你好
    Hi! I'm a bot. How can I help?

    Your input ->  我很開心
    Great! Keep up the positive vibes!

    Your input ->  再見
    Bye!
    """)


def evaluate_model():
    """
    評估模型性能
    """
    print("\n" + "=" * 50)
    print("評估模型")
    print("=" * 50)

    print("\n1. NLU 評估:")
    print("   rasa test nlu --nlu data/nlu.yml")

    print("\n2. 交叉驗證:")
    print("   rasa test nlu --cross-validation")

    print("\n3. Core 評估:")
    print("   rasa test core --stories data/test_stories.yml")

    print("\n4. 評估報告:")
    print("   - 混淆矩陣 (Confusion Matrix)")
    print("   - 意圖分類報告 (Intent Classification Report)")
    print("   - 實體提取報告 (Entity Extraction Report)")
    print("   - F1 分數、精確率、召回率")


# ==================== 5. 啟動服務 ====================

def run_rasa_server():
    """
    啟動 Rasa 服務器
    """
    print("\n" + "=" * 50)
    print("啟動 Rasa 服務器")
    print("=" * 50)

    print("\n1. 啟動 Rasa 服務器:")
    print("   rasa run")
    print("   - 默認端口: 5005")
    print("   - API endpoint: http://localhost:5005/webhooks/rest/webhook")

    print("\n2. 啟用 API:")
    print("   rasa run --enable-api")

    print("\n3. 啟用 CORS:")
    print("   rasa run --cors '*'")

    print("\n4. 指定端口:")
    print("   rasa run --port 8080")

    print("\n5. API 調用示例:")
    api_example = {
        "sender": "user123",
        "message": "你好"
    }
    print(f"   curl -X POST http://localhost:5005/webhooks/rest/webhook \\")
    print(f"        -H 'Content-Type: application/json' \\")
    print(f"        -d '{json.dumps(api_example, ensure_ascii=False)}'")


def run_action_server():
    """
    啟動 Action Server（用於自定義動作）
    """
    print("\n" + "=" * 50)
    print("啟動 Action Server")
    print("=" * 50)

    print("\n啟動命令:")
    print("   rasa run actions")
    print("   - 默認端口: 5055")

    print("\n注意事項:")
    print("   - Action Server 需要單獨啟動")
    print("   - 用於執行自定義動作（Custom Actions）")
    print("   - 在 endpoints.yml 中配置連接")


# ==================== 主程序 ====================

def main():
    """
    主程序 - 演示 Rasa 安裝和入門流程
    """
    print("\n" + "=" * 60)
    print("Rasa 安裝入門 - 完整指南")
    print("=" * 60)

    # 1. 安裝說明
    install_rasa()

    # 2. 項目初始化
    initialize_project()

    # 3. 配置文件
    create_config_yml()
    create_domain_yml()
    create_nlu_data()
    create_stories_data()
    create_rules_data()

    # 4. 訓練和測試
    train_model()
    test_model()
    evaluate_model()

    # 5. 啟動服務
    run_rasa_server()
    run_action_server()

    # 快速開始檢查清單
    print("\n" + "=" * 60)
    print("快速開始檢查清單")
    print("=" * 60)
    checklist = """
    □ 1. 安裝 Python 3.7-3.10
    □ 2. 創建虛擬環境
    □ 3. 安裝 Rasa: pip install rasa
    □ 4. 安裝 Jieba: pip install jieba
    □ 5. 初始化項目: rasa init
    □ 6. 查看項目結構
    □ 7. 修改配置文件（config.yml, domain.yml）
    □ 8. 準備訓練數據（nlu.yml, stories.yml, rules.yml）
    □ 9. 訓練模型: rasa train
    □ 10. 測試機器人: rasa shell
    □ 11. 評估性能: rasa test
    □ 12. 啟動服務器: rasa run
    """
    print(checklist)

    print("\n" + "=" * 60)
    print("常見問題")
    print("=" * 60)
    print("""
    Q1: 訓練時間太長怎麼辦？
    A1: 減少 epochs 數量，從 100 降到 50 或更少

    Q2: 中文支持不好怎麼辦？
    A2: 確保安裝了 jieba，在 config.yml 中使用 JiebaTokenizer

    Q3: 如何更新模型？
    A3: 修改訓練數據後，重新運行 rasa train

    Q4: 如何查看詳細日誌？
    A4: 使用 --debug 標誌，如 rasa shell --debug

    Q5: 如何部署到生產環境？
    A5: 參考 08_部署上線.py 文件
    """)

    print("\n下一步: 學習 02_NLU訓練.py - 深入理解自然語言理解")


if __name__ == "__main__":
    main()
