"""
Rasa X 平台使用 - 對話管理和優化工具

本文件涵蓋：
1. Rasa X 安裝和配置
2. 對話數據標註
3. 模型訓練和比較
4. A/B 測試
5. 團隊協作
"""

import yaml


# ==================== 1. Rasa X 概述 ====================

def rasa_x_overview():
    """
    Rasa X 概述
    """
    print("=" * 60)
    print("Rasa X 概述")
    print("=" * 60)

    print("""
    【什麼是 Rasa X】
    Rasa X 是 Rasa 的企業級對話管理平台，提供：
    - 可視化對話設計
    - 對話數據標註
    - 模型訓練和比較
    - A/B 測試
    - 團隊協作
    - 對話分析

    【核心功能】
    1. Talk to Your Bot
       - 實時測試機器人
       - 查看對話流程
       - 即時修正錯誤

    2. Conversations
       - 查看所有用戶對話
       - 標註對話數據
       - 識別問題對話

    3. NLU Inbox
       - 審查 NLU 預測
       - 修正意圖和實體
       - 添加訓練數據

    4. Training
       - 訓練新模型
       - 比較模型性能
       - 版本管理

    5. Analytics
       - 對話統計
       - 用戶行為分析
       - 性能指標

    【版本差異】
    - Rasa X Community: 免費，本地部署
    - Rasa X Enterprise: 付費，企業級功能
    - Rasa Pro: 最新版本，包含 LLM 整合
    """)


# ==================== 2. 安裝和配置 ====================

def rasa_x_installation():
    """
    Rasa X 安裝
    """
    print("\n" + "=" * 60)
    print("Rasa X 安裝和配置")
    print("=" * 60)

    print("""
    【安裝方式 1：本地安裝】

    # 安裝 Rasa X
    pip install rasa-x --extra-index-url https://pypi.rasa.com/simple

    # 啟動 Rasa X
    rasa x

    # 默認訪問地址
    http://localhost:5002

    【安裝方式 2：Docker Compose】
    """)

    docker_compose = """
# docker-compose.yml for Rasa X
version: '3.8'

services:
  rasa-x:
    image: rasa/rasa-x:latest
    ports:
      - "5002:5002"
    volumes:
      - ./models:/app/models
      - ./data:/app/data
      - ./db:/app/db
    environment:
      - PASSWORD_SALT=your-secret-salt
      - RASA_X_USER_ANALYTICS=0
      - RASA_MODEL_SERVER=http://rasa:5005
      - RABBITMQ_HOST=rabbit
      - POSTGRESQL_SERVICE_HOST=postgres
    depends_on:
      - rasa
      - postgres
      - rabbit

  rasa:
    image: rasa/rasa:latest-full
    ports:
      - "5005:5005"
    volumes:
      - ./models:/app/models
    command: run --enable-api --cors "*"

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_USER=rasa
      - POSTGRES_PASSWORD=rasa
      - POSTGRES_DB=rasa
    volumes:
      - postgres-data:/var/lib/postgresql/data

  rabbit:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"

volumes:
  postgres-data:
"""

    print(docker_compose)

    print("""
    【啟動 Rasa X】
    docker-compose up -d

    【首次登錄】
    1. 訪問 http://localhost:5002
    2. 使用默認賬號登錄
       - 用戶名: me
       - 密碼: 查看終端輸出

    3. 修改密碼
    """)


# ==================== 3. 對話數據標註 ====================

def conversation_annotation():
    """
    對話數據標註
    """
    print("\n" + "=" * 60)
    print("對話數據標註")
    print("=" * 60)

    print("""
    【標註流程】
    1. 收集對話數據
       - 真實用戶對話
       - 測試對話
       - 導入歷史對話

    2. 審查對話
       在 Conversations 頁面：
       - 查看對話列表
       - 篩選問題對話
       - 標記重要對話

    3. 標註意圖
       在 NLU Inbox：
       - 審查意圖預測
       - 修正錯誤意圖
       - 添加新意圖

    4. 標註實體
       - 高亮實體
       - 修正實體類型
       - 添加新實體

    5. 改進對話流程
       - 查看對話樹
       - 識別問題路徑
       - 添加新 Stories

    【標註技巧】
    ✓ 優先處理低置信度預測
    ✓ 關注失敗對話
    ✓ 定期批量標註
    ✓ 保持標註一致性
    """)

    # 標註示例
    print("\n【標註示例】")
    annotation_example = """
    原始用戶輸入:
    "我的訂單 ORD123 什麼時候到？"

    NLU 預測:
    Intent: check_order_status (confidence: 0.75)
    Entities: []

    標註修正:
    Intent: check_order_status ✓
    Entities:
    - order_id: "ORD123" (new)

    添加到訓練數據:
    - intent: check_order_status
      examples: |
        - 我的訂單 [ORD123](order_id) 什麼時候到？
    """

    print(annotation_example)


# ==================== 4. 模型訓練和比較 ====================

def model_training_comparison():
    """
    模型訓練和比較
    """
    print("\n" + "=" * 60)
    print("模型訓練和比較")
    print("=" * 60)

    print("""
    【訓練新模型】
    1. 在 Training 頁面點擊 "Train"
    2. 選擇訓練數據
    3. 等待訓練完成
    4. 查看訓練日誌

    【模型比較】
    Rasa X 自動記錄每個模型的性能：

    Model A (2024-12-15)
    - Intent Accuracy: 92%
    - Entity F1: 88%
    - Stories Success: 85%

    Model B (2024-12-16)
    - Intent Accuracy: 94% ↑
    - Entity F1: 90% ↑
    - Stories Success: 87% ↑

    【模型切換】
    1. 在 Models 頁面查看所有模型
    2. 選擇要激活的模型
    3. 點擊 "Promote to Production"
    4. 確認切換

    【版本管理】
    - 自動保存所有訓練的模型
    - 可以回滾到任何歷史版本
    - 標記重要版本
    - 添加版本註釋
    """)

    # 模型比較腳本
    comparison_script = """
# 使用 Rasa X API 比較模型
import requests

RASA_X_URL = "http://localhost:5002"
API_TOKEN = "your-api-token"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# 獲取所有模型
response = requests.get(
    f"{RASA_X_URL}/api/projects/default/models",
    headers=headers
)

models = response.json()

# 比較性能
for model in models:
    print(f"Model: {model['name']}")
    print(f"  Trained: {model['trained_at']}")
    print(f"  Performance: {model.get('performance', 'N/A')}")
    print()
"""

    print("\n【模型比較腳本】")
    print(comparison_script)


# ==================== 5. A/B 測試 ====================

def ab_testing():
    """
    A/B 測試
    """
    print("\n" + "=" * 60)
    print("A/B 測試")
    print("=" * 60)

    print("""
    【什麼是 A/B 測試】
    同時運行兩個版本的機器人，比較性能：
    - 版本 A: 當前生產模型
    - 版本 B: 新訓練的模型

    【設置 A/B 測試】
    1. 訓練新模型（版本 B）
    2. 在 Models 頁面選擇 "A/B Test"
    3. 設置流量分配（例如 80/20）
    4. 設置測試時長
    5. 啟動測試

    【監控指標】
    版本 A:
    - 用戶數: 800
    - 成功率: 85%
    - 平均輪次: 5.2
    - 用戶滿意度: 4.1/5

    版本 B:
    - 用戶數: 200
    - 成功率: 88% ↑
    - 平均輪次: 4.8 ↓
    - 用戶滿意度: 4.3/5 ↑

    【決策】
    如果版本 B 表現更好：
    - 逐步增加流量
    - 最終完全切換
    - 保留版本 A 作為備份

    如果版本 A 表現更好：
    - 停止測試
    - 分析版本 B 的問題
    - 改進後重新測試
    """)

    # A/B 測試配置
    ab_config = """
# endpoints.yml - A/B 測試配置
models:
  model_a:
    url: http://rasa-a:5005/model
    weight: 80  # 80% 流量
  model_b:
    url: http://rasa-b:5005/model
    weight: 20  # 20% 流量

# 追蹤測試結果
tracker_store:
  type: SQL
  dialect: postgresql
  host: postgres
  port: 5432
  db: rasa
  username: rasa
  password: rasa
  # 記錄使用的模型版本
  query_logs: true
"""

    print("\n【A/B 測試配置】")
    print(ab_config)


# ==================== 6. 團隊協作 ====================

def team_collaboration():
    """
    團隊協作
    """
    print("\n" + "=" * 60)
    print("團隊協作")
    print("=" * 60)

    print("""
    【角色管理】
    Rasa X 支持多種角色：

    1. Admin（管理員）
       - 完全訪問權限
       - 用戶管理
       - 系統配置

    2. Annotator（標註員）
       - 標註對話數據
       - 審查 NLU 預測
       - 添加訓練示例

    3. Tester（測試員）
       - 測試機器人
       - 查看對話
       - 報告問題

    4. Viewer（查看者）
       - 只讀訪問
       - 查看分析報告

    【協作流程】
    1. 數據收集
       Tester: 測試機器人，生成對話

    2. 數據標註
       Annotator: 審查和標註對話

    3. 模型訓練
       Admin: 訓練和部署新模型

    4. 性能分析
       All: 查看分析報告

    【權限設置】
    在 Settings > Users：
    - 添加新用戶
    - 分配角色
    - 設置權限
    - 管理團隊

    【協作技巧】
    ✓ 定期團隊會議討論改進
    ✓ 建立標註規範
    ✓ 使用標籤組織對話
    ✓ 記錄重要決策
    ✓ 分享最佳實踐
    """)


# ==================== 7. 分析和報告 ====================

def analytics_reporting():
    """
    分析和報告
    """
    print("\n" + "=" * 60)
    print("分析和報告")
    print("=" * 60)

    print("""
    【對話統計】
    - 總對話數
    - 活躍用戶數
    - 平均對話輪次
    - 對話完成率

    【意圖分析】
    - 意圖分布
    - 高頻意圖
    - 低置信度意圖
    - 未識別輸入

    【實體分析】
    - 實體提取準確率
    - 常見實體值
    - 提取失敗案例

    【性能指標】
    - NLU 準確率
    - 對話成功率
    - 響應時間
    - 錯誤率

    【用戶行為】
    - 用戶留存率
    - 使用時段分布
    - 常見問題路徑
    - 放棄率

    【導出報告】
    可以導出：
    - PDF 報告
    - Excel 數據
    - JSON 格式
    - CSV 文件
    """)

    # 使用 API 獲取分析數據
    analytics_script = """
# 獲取分析數據
import requests
import pandas as pd
from datetime import datetime, timedelta

RASA_X_URL = "http://localhost:5002"
API_TOKEN = "your-api-token"

headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}

# 獲取對話統計
def get_conversation_stats(days=7):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    params = {
        "start": start_date.isoformat(),
        "end": end_date.isoformat()
    }

    response = requests.get(
        f"{RASA_X_URL}/api/conversations/statistics",
        headers=headers,
        params=params
    )

    return response.json()

# 獲取意圖分布
def get_intent_distribution():
    response = requests.get(
        f"{RASA_X_URL}/api/analytics/intents",
        headers=headers
    )

    data = response.json()
    df = pd.DataFrame(data)
    return df.sort_values('count', ascending=False)

# 生成報告
stats = get_conversation_stats()
print(f"Total Conversations: {stats['total']}")
print(f"Unique Users: {stats['unique_users']}")
print(f"Avg Turns: {stats['avg_turns']}")

intent_dist = get_intent_distribution()
print("\\nTop 5 Intents:")
print(intent_dist.head())
"""

    print("\n【分析腳本示例】")
    print(analytics_script)


# ==================== 8. 最佳實踐 ====================

def best_practices():
    """
    Rasa X 最佳實踐
    """
    print("\n" + "=" * 60)
    print("Rasa X 最佳實踐")
    print("=" * 60)

    print("""
    【數據管理】
    1. 定期備份
       - 對話數據
       - 訓練數據
       - 模型文件

    2. 數據清理
       - 刪除測試對話
       - 去除重複數據
       - 歸檔舊數據

    3. 版本控制
       - 訓練數據版本化
       - 模型版本管理
       - 配置文件追蹤

    【模型管理】
    1. 訓練策略
       - 定期重新訓練（每週）
       - 增量添加數據
       - 驗證性能

    2. 部署策略
       - 使用 A/B 測試
       - 漸進式發布
       - 保留回滾能力

    3. 監控
       - 實時性能監控
       - 錯誤告警
       - 使用情況追蹤

    【團隊協作】
    1. 建立流程
       - 標註規範
       - 審核流程
       - 發布檢查清單

    2. 知識分享
       - 定期會議
       - 文檔維護
       - 最佳實踐庫

    3. 質量控制
       - 交叉驗證標註
       - 定期審查
       - 性能基準

    【持續改進】
    1. 分析用戶反饋
    2. 識別問題模式
    3. 優先處理高頻問題
    4. 測試改進效果
    5. 迭代優化

    【安全性】
    1. 用戶訪問控制
    2. 數據加密
    3. 定期安全審計
    4. 合規性檢查
    """)


# ==================== 主程序 ====================

def main():
    """
    主程序
    """
    print("\n" + "=" * 70)
    print("Rasa X 平台使用 - 完整指南")
    print("=" * 70)

    # 1. 概述
    rasa_x_overview()

    # 2. 安裝
    rasa_x_installation()

    # 3. 標註
    conversation_annotation()

    # 4. 訓練
    model_training_comparison()

    # 5. A/B 測試
    ab_testing()

    # 6. 協作
    team_collaboration()

    # 7. 分析
    analytics_reporting()

    # 8. 最佳實踐
    best_practices()

    # 總結
    print("\n" + "=" * 70)
    print("總結")
    print("=" * 70)
    print("""
    【Rasa X 核心價值】
    1. 可視化管理
       - 直觀的界面
       - 簡化操作流程
       - 降低技術門檻

    2. 數據驅動改進
       - 真實對話數據
       - 持續學習
       - 快速迭代

    3. 團隊協作
       - 多角色支持
       - 工作流程
       - 知識共享

    4. 質量保證
       - A/B 測試
       - 性能監控
       - 版本管理

    【適用場景】
    ✓ 需要持續優化的機器人
    ✓ 多人協作開發
    ✓ 企業級部署
    ✓ 數據驅動決策

    【學習路徑完成】
    恭喜！您已完成 Rasa 完整學習路徑：

    01. 安裝入門 ✓
    02. NLU 訓練 ✓
    03. 對話故事 ✓
    04. 自定義動作 ✓
    05. 表單處理 ✓
    06. LLM 整合 ✓
    07. 多語言支持 ✓
    08. 部署上線 ✓
    09. 客服機器人 ✓
    10. FAQ 機器人 ✓
    11. Rasa X ✓

    【下一步建議】
    1. 實踐項目：構建自己的對話機器人
    2. 深入研究：Rasa 源碼和算法
    3. 社區參與：Rasa 論壇和 GitHub
    4. 持續學習：關注 Rasa 更新

    祝您在對話式 AI 領域取得成功！🚀
    """)


if __name__ == "__main__":
    main()
