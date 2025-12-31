"""
PandasAI 安全設置示例

這個示例展示了如何配置 PandasAI 的安全設置：
1. 安全模式配置
2. 代碼執行限制
3. 數據隱私保護
4. API 密鑰管理
5. 審計和日誌

作者：PandasAI 示例
日期：2025-12-31
"""

import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import logging

# 載入環境變量
load_dotenv()


def create_sensitive_dataframe():
    """
    創建包含敏感信息的數據集

    Returns:
        pd.DataFrame: 包含客戶敏感數據
    """
    np.random.seed(42)

    data = {
        "客戶ID": [f"C{str(i).zfill(4)}" for i in range(1, 21)],
        "姓名": [f"客戶{i}" for i in range(1, 21)],
        "電話": [f"09{np.random.randint(10000000, 99999999)}" for _ in range(20)],
        "郵箱": [f"customer{i}@example.com" for i in range(1, 21)],
        "信用卡後四碼": [str(np.random.randint(1000, 9999)) for _ in range(20)],
        "購買金額": np.random.randint(1000, 100000, 20),
        "會員等級": np.random.choice(["銅牌", "銀牌", "金牌"], 20)
    }

    return pd.DataFrame(data)


def safe_mode_example(api_key):
    """
    安全模式示例

    Args:
        api_key: OpenAI API 密鑰
    """
    print("\n" + "="*60)
    print("安全模式示例")
    print("="*60)

    try:
        from pandasai import Agent

        df = create_sensitive_dataframe()

        # 啟用安全模式
        agent = Agent(df, config={
            "llm": {
                "api_key": api_key,
                "model": "gpt-3.5-turbo"
            },
            "enable_cache": False,
            "save_logs": True,
            "verbose": True,
            "enforce_privacy": True  # 啟用隱私保護
        })

        print("\n安全模式已啟用")
        print("配置:")
        print("  - 隱私保護: 啟用")
        print("  - 日誌記錄: 啟用")
        print("  - 詳細輸出: 啟用")

        # 嘗試安全查詢
        safe_queries = [
            "有多少個客戶？",
            "統計每個會員等級的客戶數量",
            "平均購買金額是多少？"
        ]

        print("\n執行安全查詢:")
        for i, query in enumerate(safe_queries, 1):
            try:
                print(f"\n查詢 {i}: {query}")
                response = agent.chat(query)
                print(f"回答: {response}")
            except Exception as e:
                print(f"錯誤: {str(e)}")

    except Exception as e:
        print(f"錯誤: {str(e)}")


def data_masking_example(api_key):
    """
    數據脫敏示例

    Args:
        api_key: OpenAI API 密鑰
    """
    print("\n" + "="*60)
    print("數據脫敏示例")
    print("="*60)

    try:
        from pandasai import Agent

        # 創建原始數據
        df_original = create_sensitive_dataframe()

        print("\n原始數據（包含敏感信息）:")
        print(df_original.head())

        # 數據脫敏
        df_masked = df_original.copy()

        # 脫敏電話號碼（只保留前3位和後2位）
        df_masked["電話"] = df_masked["電話"].apply(
            lambda x: f"{x[:3]}****{x[-2:]}" if isinstance(x, str) else x
        )

        # 脫敏郵箱（保留域名）
        df_masked["郵箱"] = df_masked["郵箱"].apply(
            lambda x: f"***@{x.split('@')[1]}" if '@' in str(x) else x
        )

        # 脫敏信用卡號（使用星號）
        df_masked["信用卡後四碼"] = "****"

        print("\n脫敏後的數據:")
        print(df_masked.head())

        # 使用脫敏數據創建 Agent
        agent = Agent(df_masked, config={
            "llm": {
                "api_key": api_key,
                "model": "gpt-3.5-turbo"
            },
            "verbose": False
        })

        print("\n使用脫敏數據進行查詢:")
        queries = [
            "金牌會員有多少人？",
            "最高購買金額是多少？"
        ]

        for i, query in enumerate(queries, 1):
            try:
                print(f"\n查詢 {i}: {query}")
                response = agent.chat(query)
                print(f"回答: {response}")
            except Exception as e:
                print(f"錯誤: {str(e)}")

    except Exception as e:
        print(f"錯誤: {str(e)}")


def api_key_security_example():
    """
    API 密鑰安全管理示例
    """
    print("\n" + "="*60)
    print("API 密鑰安全管理示例")
    print("="*60)

    best_practices = """
API 密鑰安全最佳實踐：

1. 環境變量存儲：
   - 使用 .env 文件存儲 API 密鑰
   - 將 .env 添加到 .gitignore
   - 使用 python-dotenv 載入

示例 .env 文件：
```
OPENAI_API_KEY=sk-xxx...
ANTHROPIC_API_KEY=sk-ant-xxx...
```

2. 代碼中使用：
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("未找到 API 密鑰")
```

3. 生產環境：
   - 使用密鑰管理服務（AWS Secrets Manager、Azure Key Vault）
   - 設置 API 密鑰輪換策略
   - 限制 API 密鑰權限
   - 監控 API 使用情況

4. 避免的做法：
   ✗ 直接寫在代碼中
   ✗ 提交到版本控制系統
   ✗ 在日誌中打印
   ✗ 共享給未授權人員

5. 安全檢查清單：
   □ API 密鑰使用環境變量
   □ .env 文件已加入 .gitignore
   □ 定期輪換密鑰
   □ 設置使用限額
   □ 啟用使用監控
   □ 配置 IP 白名單（如果可能）
    """

    print(best_practices)


def logging_and_auditing_example(api_key):
    """
    日誌和審計示例

    Args:
        api_key: OpenAI API 密鑰
    """
    print("\n" + "="*60)
    print("日誌和審計示例")
    print("="*60)

    try:
        from pandasai import Agent

        # 配置日誌
        log_file = "/tmp/pandasai_audit.log"
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        df = create_sensitive_dataframe()

        # 創建 Agent 並啟用日誌
        agent = Agent(df, config={
            "llm": {
                "api_key": api_key,
                "model": "gpt-3.5-turbo"
            },
            "save_logs": True,
            "verbose": True
        })

        print(f"\n日誌文件: {log_file}")

        # 記錄查詢
        queries = [
            "客戶總數是多少？",
            "金牌會員的平均購買金額"
        ]

        for i, query in enumerate(queries, 1):
            try:
                logging.info(f"用戶查詢: {query}")
                print(f"\n查詢 {i}: {query}")
                response = agent.chat(query)
                logging.info(f"查詢結果: {response}")
                print(f"回答: {response}")
            except Exception as e:
                logging.error(f"查詢錯誤: {str(e)}")
                print(f"錯誤: {str(e)}")

        # 讀取並顯示日誌
        if os.path.exists(log_file):
            print(f"\n審計日誌內容:")
            with open(log_file, 'r') as f:
                logs = f.readlines()
                for log in logs[-10:]:  # 顯示最後 10 行
                    print(f"  {log.strip()}")

    except Exception as e:
        print(f"錯誤: {str(e)}")


def restricted_operations_example():
    """
    限制操作示例
    """
    print("\n" + "="*60)
    print("限制操作示例")
    print("="*60)

    restrictions = """
建議的安全限制：

1. 代碼執行限制：
   - 禁止執行危險的系統命令
   - 限制文件系統訪問
   - 禁止網絡請求
   - 限制導入模塊

2. 數據訪問限制：
   - 只允許查詢特定列
   - 限制返回行數
   - 過濾敏感字段
   - 實施行級安全

3. 配置示例：
```python
agent = Agent(df, config={{
    "llm": {{"api_key": api_key}},
    "enable_cache": False,        # 禁用緩存避免數據洩露
    "save_logs": True,             # 啟用審計日誌
    "save_charts": False,          # 禁止保存圖表
    "enforce_privacy": True,       # 啟用隱私保護
    "max_retries": 3,              # 限制重試次數
}})
```

4. 查詢驗證：
   - 檢查查詢意圖
   - 過濾惡意請求
   - 限制查詢複雜度
   - 設置超時限制

5. 輸出過濾：
   - 檢查輸出是否包含敏感信息
   - 自動脫敏個人信息
   - 限制數據導出
    """

    print(restrictions)


def security_checklist():
    """
    安全檢查清單
    """
    print("\n" + "="*60)
    print("安全檢查清單")
    print("="*60)

    checklist = """
生產環境部署前的安全檢查：

□ 數據安全
  □ 敏感數據已脫敏
  □ 實施數據訪問控制
  □ 啟用數據加密（傳輸和存儲）
  □ 定期備份數據

□ 認證授權
  □ API 密鑰安全存儲
  □ 實施用戶認證
  □ 配置角色權限
  □ 啟用多因素認證

□ 配置安全
  □ 禁用不必要的功能
  □ 設置資源限制
  □ 配置超時時間
  □ 啟用安全模式

□ 監控審計
  □ 啟用日誌記錄
  □ 配置告警機制
  □ 定期審查日誌
  □ 監控異常活動

□ 網絡安全
  □ 使用 HTTPS
  □ 配置防火牆
  □ 設置 IP 白名單
  □ 實施 DDoS 防護

□ 合規性
  □ 符合 GDPR/PDPA 要求
  □ 遵守數據保護法規
  □ 制定隱私政策
  □ 獲得用戶同意

□ 事件響應
  □ 制定安全事件響應計劃
  □ 定期安全演練
  □ 建立緊急聯繫機制
  □ 準備數據恢復方案
    """

    print(checklist)


def main():
    """
    主函數：演示安全設置
    """
    print("PandasAI 安全設置示例")
    print("="*60)

    # 檢查 API 密鑰
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("警告: 未找到 OPENAI_API_KEY 環境變量")
        print("請在 .env 文件中設置: OPENAI_API_KEY=your_api_key")
        print("\n顯示安全配置指南...")

        # 顯示安全指南
        api_key_security_example()
        restricted_operations_example()
        security_checklist()

        return

    try:
        # 1. 安全模式示例
        safe_mode_example(api_key)

        # 2. 數據脫敏示例
        data_masking_example(api_key)

        # 3. API 密鑰安全
        api_key_security_example()

        # 4. 日誌和審計
        logging_and_auditing_example(api_key)

        # 5. 限制操作
        restricted_operations_example()

        # 6. 安全檢查清單
        security_checklist()

        # 總結
        print("\n" + "="*60)
        print("安全設置總結")
        print("="*60)
        print("✓ 安全模式：限制危險操作")
        print("✓ 數據脫敏：保護敏感信息")
        print("✓ 密鑰管理：安全存儲 API 密鑰")
        print("✓ 日誌審計：記錄所有操作")
        print("✓ 訪問控制：限制數據訪問")

        print("\n關鍵安全原則：")
        print("1. 最小權限原則：只授予必要的權限")
        print("2. 深度防禦：多層安全措施")
        print("3. 數據隱私：保護用戶隱私")
        print("4. 持續監控：及時發現安全問題")
        print("5. 定期審查：更新安全策略")

        print("\n重要提醒：")
        print("⚠ 永不在代碼中硬編碼 API 密鑰")
        print("⚠ 敏感數據務必脫敏處理")
        print("⚠ 生產環境啟用完整的安全措施")
        print("⚠ 定期審查和更新安全配置")
        print("⚠ 遵守相關法規和合規要求")

    except ImportError:
        print("\n錯誤: 未安裝 pandasai 庫")
        print("請運行: pip install pandasai python-dotenv")
    except Exception as e:
        print(f"\n發生錯誤: {str(e)}")
        print(f"錯誤類型: {type(e).__name__}")

        # 提供故障排除建議
        print("\n故障排除建議:")
        print("1. 確保所有安全配置正確")
        print("2. 檢查日誌文件權限")
        print("3. 驗證數據脫敏邏輯")
        print("4. 測試安全限制是否生效")
        print("5. 審查錯誤日誌")


if __name__ == "__main__":
    main()
