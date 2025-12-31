"""
PandasAI 緩存機制示例

這個示例展示了如何使用 PandasAI 的緩存功能：
1. 啟用/禁用緩存
2. 緩存配置
3. 緩存性能測試
4. 緩存清理
5. 自定義緩存策略

作者：PandasAI 示例
日期：2025-12-31
"""

import os
import time
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# 載入環境變量
load_dotenv()


def create_large_dataframe():
    """
    創建較大的數據集用於測試緩存性能

    Returns:
        pd.DataFrame: 大型數據集
    """
    np.random.seed(42)

    n_records = 10000

    data = {
        "訂單ID": [f"ORD{str(i).zfill(6)}" for i in range(1, n_records + 1)],
        "客戶ID": [f"C{str(np.random.randint(1, 1001)).zfill(4)}" for _ in range(n_records)],
        "產品ID": [f"P{str(np.random.randint(1, 101)).zfill(3)}" for _ in range(n_records)],
        "產品類別": np.random.choice(["電子產品", "服飾", "食品", "家居", "運動"], n_records),
        "銷售額": np.random.randint(100, 10000, n_records),
        "數量": np.random.randint(1, 20, n_records),
        "折扣": np.random.choice([0, 0.05, 0.1, 0.15, 0.2], n_records),
        "地區": np.random.choice(["北部", "中部", "南部", "東部"], n_records),
        "客戶評分": np.random.randint(1, 6, n_records)
    }

    df = pd.DataFrame(data)
    df["淨銷售額"] = df["銷售額"] * (1 - df["折扣"])

    return df


def cache_enabled_example(api_key):
    """
    啟用緩存示例

    Args:
        api_key: OpenAI API 密鑰
    """
    print("\n" + "="*60)
    print("啟用緩存示例")
    print("="*60)

    try:
        from pandasai import Agent

        df = create_large_dataframe()
        print(f"數據集大小: {df.shape}")

        # 啟用緩存
        agent = Agent(df, config={
            "llm": {
                "api_key": api_key,
                "model": "gpt-3.5-turbo"
            },
            "enable_cache": True,
            "verbose": False
        })

        # 測試查詢
        test_query = "總銷售額是多少？"

        # 第一次查詢（無緩存）
        print(f"\n第一次查詢: {test_query}")
        start_time = time.time()
        response1 = agent.chat(test_query)
        time1 = time.time() - start_time
        print(f"回答: {response1}")
        print(f"耗時: {time1:.2f} 秒")

        # 第二次相同查詢（使用緩存）
        print(f"\n第二次查詢（相同問題）: {test_query}")
        start_time = time.time()
        response2 = agent.chat(test_query)
        time2 = time.time() - start_time
        print(f"回答: {response2}")
        print(f"耗時: {time2:.2f} 秒")

        # 性能比較
        print(f"\n性能提升: {((time1 - time2) / time1 * 100):.1f}%")
        print(f"速度提升: {(time1 / time2):.1f}x")

    except Exception as e:
        print(f"錯誤: {str(e)}")


def cache_disabled_example(api_key):
    """
    禁用緩存示例

    Args:
        api_key: OpenAI API 密鑰
    """
    print("\n" + "="*60)
    print("禁用緩存示例")
    print("="*60)

    try:
        from pandasai import Agent

        df = create_large_dataframe()

        # 禁用緩存
        agent = Agent(df, config={
            "llm": {
                "api_key": api_key,
                "model": "gpt-3.5-turbo"
            },
            "enable_cache": False,
            "verbose": False
        })

        test_query = "平均訂單金額是多少？"

        # 第一次查詢
        print(f"\n第一次查詢: {test_query}")
        start_time = time.time()
        response1 = agent.chat(test_query)
        time1 = time.time() - start_time
        print(f"回答: {response1}")
        print(f"耗時: {time1:.2f} 秒")

        # 第二次相同查詢（沒有緩存）
        print(f"\n第二次查詢（相同問題）: {test_query}")
        start_time = time.time()
        response2 = agent.chat(test_query)
        time2 = time.time() - start_time
        print(f"回答: {response2}")
        print(f"耗時: {time2:.2f} 秒")

        print("\n注意: 禁用緩存時，每次查詢都會調用 API")

    except Exception as e:
        print(f"錯誤: {str(e)}")


def cache_performance_test(api_key):
    """
    緩存性能測試

    Args:
        api_key: OpenAI API 密鑰
    """
    print("\n" + "="*60)
    print("緩存性能測試")
    print("="*60)

    try:
        from pandasai import Agent

        df = create_large_dataframe()

        # 創建啟用緩存的 Agent
        agent = Agent(df, config={
            "llm": {
                "api_key": api_key,
                "model": "gpt-3.5-turbo"
            },
            "enable_cache": True,
            "verbose": False
        })

        # 測試多個查詢
        queries = [
            "總銷售額是多少？",
            "哪個地區的銷售額最高？",
            "電子產品的平均價格是多少？",
            "客戶評分的平均值是多少？",
            "銷售數量最多的產品類別是什麼？"
        ]

        print("\n第一輪查詢（建立緩存）:")
        first_round_times = []

        for i, query in enumerate(queries, 1):
            start_time = time.time()
            response = agent.chat(query)
            elapsed = time.time() - start_time
            first_round_times.append(elapsed)
            print(f"{i}. {query} - {elapsed:.2f}秒")

        print("\n第二輪查詢（使用緩存）:")
        second_round_times = []

        for i, query in enumerate(queries, 1):
            start_time = time.time()
            response = agent.chat(query)
            elapsed = time.time() - start_time
            second_round_times.append(elapsed)
            print(f"{i}. {query} - {elapsed:.2f}秒")

        # 性能統計
        total_time_first = sum(first_round_times)
        total_time_second = sum(second_round_times)

        print("\n性能統計:")
        print(f"第一輪總耗時: {total_time_first:.2f} 秒")
        print(f"第二輪總耗時: {total_time_second:.2f} 秒")
        print(f"節省時間: {total_time_first - total_time_second:.2f} 秒")
        print(f"性能提升: {((total_time_first - total_time_second) / total_time_first * 100):.1f}%")

    except Exception as e:
        print(f"錯誤: {str(e)}")


def cache_configuration_example(api_key):
    """
    緩存配置示例

    Args:
        api_key: OpenAI API 密鑰
    """
    print("\n" + "="*60)
    print("緩存配置示例")
    print("="*60)

    try:
        from pandasai import Agent

        df = create_large_dataframe()

        # 自定義緩存路徑
        cache_path = "/tmp/pandasai_cache"
        os.makedirs(cache_path, exist_ok=True)

        print(f"\n緩存路徑: {cache_path}")

        agent = Agent(df, config={
            "llm": {
                "api_key": api_key,
                "model": "gpt-3.5-turbo"
            },
            "enable_cache": True,
            "cache_path": cache_path,
            "verbose": False
        })

        # 執行查詢
        queries = [
            "北部地區的總銷售額",
            "服飾類別的平均評分",
            "折扣最高的訂單"
        ]

        print("\n執行查詢並緩存結果:")
        for i, query in enumerate(queries, 1):
            print(f"\n查詢 {i}: {query}")
            response = agent.chat(query)
            print(f"回答: {response}")

        # 檢查緩存文件
        if os.path.exists(cache_path):
            cache_files = os.listdir(cache_path)
            print(f"\n緩存文件數量: {len(cache_files)}")
            if cache_files:
                print("緩存文件:")
                for file in cache_files[:5]:  # 只顯示前 5 個
                    print(f"  - {file}")

    except Exception as e:
        print(f"錯誤: {str(e)}")


def cache_invalidation_example(api_key):
    """
    緩存失效示例

    Args:
        api_key: OpenAI API 密鑰
    """
    print("\n" + "="*60)
    print("緩存失效示例")
    print("="*60)

    try:
        from pandasai import Agent

        # 創建初始數據集
        df = create_large_dataframe()

        agent = Agent(df, config={
            "llm": {
                "api_key": api_key,
                "model": "gpt-3.5-turbo"
            },
            "enable_cache": True,
            "verbose": False
        })

        query = "總銷售額是多少？"

        # 第一次查詢
        print(f"\n初始查詢: {query}")
        response1 = agent.chat(query)
        print(f"回答: {response1}")

        # 修改數據（這應該使緩存失效）
        print("\n修改數據集...")
        df_modified = df.copy()
        df_modified.loc[0, "銷售額"] = 999999

        # 使用新數據創建新 Agent
        agent_new = Agent(df_modified, config={
            "llm": {
                "api_key": api_key,
                "model": "gpt-3.5-turbo"
            },
            "enable_cache": True,
            "verbose": False
        })

        # 再次查詢（應該返回新結果）
        print(f"\n數據修改後查詢: {query}")
        response2 = agent_new.chat(query)
        print(f"回答: {response2}")

        print("\n注意: 數據變化會導致緩存失效")

    except Exception as e:
        print(f"錯誤: {str(e)}")


def cache_best_practices():
    """
    顯示緩存最佳實踐
    """
    print("\n" + "="*60)
    print("緩存最佳實踐")
    print("="*60)

    practices = """
1. 何時啟用緩存：
   ✓ 重複執行相同或相似的查詢
   ✓ 數據集變化不頻繁
   ✓ 開發和測試階段
   ✓ 交互式數據探索

2. 何時禁用緩存：
   ✓ 數據實時更新
   ✓ 每次查詢都不同
   ✓ 需要最新結果
   ✓ 生產環境（視情況而定）

3. 緩存管理：
   - 定期清理過期緩存
   - 監控緩存大小
   - 設置合理的緩存路徑
   - 考慮磁盤空間限制

4. 性能優化：
   - 預先執行常見查詢建立緩存
   - 使用緩存減少 API 調用成本
   - 平衡緩存命中率和數據新鮮度

5. 安全考慮：
   - 不要緩存敏感數據
   - 設置適當的緩存權限
   - 定期清理緩存目錄

6. 調試技巧：
   - 使用 verbose=True 查看緩存狀態
   - 比較有無緩存的性能差異
   - 監控緩存命中率
    """

    print(practices)


def main():
    """
    主函數：演示緩存機制
    """
    print("PandasAI 緩存機制示例")
    print("="*60)

    # 檢查 API 密鑰
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("警告: 未找到 OPENAI_API_KEY 環境變量")
        print("請在 .env 文件中設置: OPENAI_API_KEY=your_api_key")
        print("\n顯示緩存配置示例...")

        # 顯示示例配置
        config_example = """
# 緩存配置示例

from pandasai import Agent

# 啟用緩存
agent = Agent(df, config={{
    "enable_cache": True,
    "cache_path": "/path/to/cache",
    "llm": {{
        "api_key": "your_api_key",
        "model": "gpt-3.5-turbo"
    }}
}})

# 禁用緩存
agent = Agent(df, config={{
    "enable_cache": False,
    "llm": {{
        "api_key": "your_api_key",
        "model": "gpt-3.5-turbo"
    }}
}})
        """
        print(config_example)

        # 顯示最佳實踐
        cache_best_practices()

        return

    try:
        # 1. 啟用緩存示例
        cache_enabled_example(api_key)

        # 2. 禁用緩存示例
        cache_disabled_example(api_key)

        # 3. 緩存性能測試
        cache_performance_test(api_key)

        # 4. 緩存配置示例
        cache_configuration_example(api_key)

        # 5. 緩存失效示例
        cache_invalidation_example(api_key)

        # 6. 最佳實踐
        cache_best_practices()

        # 總結
        print("\n" + "="*60)
        print("緩存機制總結")
        print("="*60)
        print("✓ 緩存啟用：顯著提升重複查詢的性能")
        print("✓ 緩存配置：可自定義緩存路徑")
        print("✓ 性能提升：減少 API 調用和響應時間")
        print("✓ 成本節省：減少 LLM API 使用費用")
        print("✓ 智能失效：數據變化時自動更新")

        print("\n關鍵收穫：")
        print("- 緩存可以大幅提升性能（通常 10x 以上）")
        print("- 適合重複查詢和數據探索場景")
        print("- 需要平衡性能和數據新鮮度")
        print("- 注意管理緩存大小和清理")
        print("- 在開發階段默認啟用緩存")

    except ImportError:
        print("\n錯誤: 未安裝 pandasai 庫")
        print("請運行: pip install pandasai")
    except Exception as e:
        print(f"\n發生錯誤: {str(e)}")
        print(f"錯誤類型: {type(e).__name__}")

        # 提供故障排除建議
        print("\n故障排除建議:")
        print("1. 確保緩存路徑有寫入權限")
        print("2. 檢查磁盤空間是否充足")
        print("3. 驗證 API 密鑰正確")
        print("4. 如果緩存有問題，嘗試禁用緩存")
        print("5. 清理舊的緩存文件")


if __name__ == "__main__":
    main()
