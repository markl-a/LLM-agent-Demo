"""
PandasAI 自定義提示示例

這個示例展示了如何自定義 PandasAI 的提示詞（Prompt）：
1. 自定義系統提示
2. 添加上下文信息
3. 指定輸出格式
4. 行業特定提示
5. 提示模板

作者：PandasAI 示例
日期：2025-12-31
"""

import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# 載入環境變量
load_dotenv()


def create_sample_dataframe():
    """
    創建示例數據集

    Returns:
        pd.DataFrame: 電商數據
    """
    np.random.seed(42)

    data = {
        "訂單ID": [f"ORD{str(i).zfill(5)}" for i in range(1, 101)],
        "產品名稱": np.random.choice(
            ["筆記本電腦", "智能手機", "平板電腦", "智能手錶", "耳機"], 100
        ),
        "類別": np.random.choice(["電子產品", "配件"], 100),
        "銷售額": np.random.randint(1000, 50000, 100),
        "利潤": np.random.randint(100, 10000, 100),
        "客戶滿意度": np.random.randint(1, 6, 100),
        "地區": np.random.choice(["北部", "中部", "南部", "東部"], 100)
    }

    df = pd.DataFrame(data)
    df["利潤率"] = (df["利潤"] / df["銷售額"] * 100).round(2)

    return df


def basic_custom_prompt_example(api_key):
    """
    基本自定義提示示例

    Args:
        api_key: OpenAI API 密鑰
    """
    print("\n" + "="*60)
    print("基本自定義提示示例")
    print("="*60)

    try:
        from pandasai import Agent

        df = create_sample_dataframe()

        # 自定義系統提示
        custom_prompt = """
        你是一位專業的數據分析師，專精於電商數據分析。
        在回答問題時，請：
        1. 提供準確的數字和統計數據
        2. 使用專業的分析術語
        3. 給出可操作的業務建議
        4. 以繁體中文回答
        """

        agent = Agent(df, config={
            "llm": {
                "api_key": api_key,
                "model": "gpt-3.5-turbo"
            },
            "custom_prompts": {
                "system": custom_prompt
            },
            "verbose": False
        })

        print("\n使用自定義提示查詢：")

        queries = [
            "分析銷售數據的總體情況",
            "哪個地區的表現最好？",
            "提供提升利潤率的建議"
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


def context_aware_prompt_example(api_key):
    """
    上下文感知提示示例

    Args:
        api_key: OpenAI API 密鑰
    """
    print("\n" + "="*60)
    print("上下文感知提示示例")
    print("="*60)

    try:
        from pandasai import Agent

        df = create_sample_dataframe()

        # 添加業務上下文
        context_prompt = """
        數據背景：
        - 這是一家電商公司 2024 年第一季度的銷售數據
        - 公司目標是提升 20% 的銷售額
        - 重點關注客戶滿意度和利潤率
        - 北部地區是主要市場

        在分析時請考慮這些業務背景，並提供符合公司目標的建議。
        """

        agent = Agent(df, config={
            "llm": {
                "api_key": api_key,
                "model": "gpt-4"
            },
            "custom_prompts": {
                "context": context_prompt
            },
            "verbose": False
        })

        print("\n使用上下文感知提示查詢：")

        queries = [
            "分析當前銷售表現是否達到目標",
            "北部市場的優勢在哪裡？",
            "如何改善客戶滿意度？",
            "哪些產品值得重點推廣？"
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


def format_specific_prompt_example(api_key):
    """
    指定輸出格式提示示例

    Args:
        api_key: OpenAI API 密鑰
    """
    print("\n" + "="*60)
    print("指定輸出格式提示示例")
    print("="*60)

    try:
        from pandasai import Agent

        df = create_sample_dataframe()

        # 指定輸出格式
        format_prompt = """
        請以以下格式回答所有問題：

        【數據摘要】
        - 關鍵指標
        - 重要發現

        【詳細分析】
        - 具體數字和百分比
        - 趨勢說明

        【建議】
        - 具體的行動建議
        - 預期效果

        使用繁體中文，並以專業、簡潔的方式表達。
        """

        agent = Agent(df, config={
            "llm": {
                "api_key": api_key,
                "model": "gpt-4"
            },
            "custom_prompts": {
                "format": format_prompt
            },
            "verbose": False
        })

        print("\n使用格式化提示查詢：")

        queries = [
            "分析銷售額和利潤的關係",
            "評估各地區的表現",
            "客戶滿意度分析"
        ]

        for i, query in enumerate(queries, 1):
            try:
                print(f"\n查詢 {i}: {query}")
                response = agent.chat(query)
                print(f"回答:\n{response}")
            except Exception as e:
                print(f"錯誤: {str(e)}")

    except Exception as e:
        print(f"錯誤: {str(e)}")


def industry_specific_prompt_example(api_key):
    """
    行業特定提示示例

    Args:
        api_key: OpenAI API 密鑰
    """
    print("\n" + "="*60)
    print("行業特定提示示例")
    print("="*60)

    try:
        from pandasai import Agent

        df = create_sample_dataframe()

        # 電商行業特定提示
        industry_prompt = """
        你是電商行業的數據分析專家，熟悉以下指標和概念：
        - GMV（商品交易總額）
        - 轉換率、客單價、復購率
        - RFM 分析（最近購買、購買頻率、購買金額）
        - 長尾效應
        - 季節性趨勢

        在分析時：
        1. 使用電商行業術語
        2. 關注用戶生命週期價值（LTV）
        3. 考慮市場競爭因素
        4. 提供數據驅動的營銷建議
        """

        agent = Agent(df, config={
            "llm": {
                "api_key": api_key,
                "model": "gpt-4"
            },
            "custom_prompts": {
                "industry": industry_prompt
            },
            "verbose": False
        })

        print("\n使用行業特定提示查詢：")

        queries = [
            "從電商角度分析這份數據",
            "如何優化客單價？",
            "識別高價值客戶群體",
            "提供促銷活動建議"
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


def combined_prompts_example(api_key):
    """
    組合提示示例

    Args:
        api_key: OpenAI API 密鑰
    """
    print("\n" + "="*60)
    print("組合提示示例")
    print("="*60)

    try:
        from pandasai import Agent

        df = create_sample_dataframe()

        # 組合多種提示
        combined_config = {
            "llm": {
                "api_key": api_key,
                "model": "gpt-4"
            },
            "custom_prompts": {
                "system": """
                你是一位資深的商業智能分析師，專精於零售和電商數據分析。
                """,
                "context": """
                公司背景：台灣電商平台
                分析目標：提升銷售額和客戶滿意度
                關鍵時期：季度末績效評估
                """,
                "format": """
                回答格式：
                1. 核心發現（2-3 點）
                2. 數據支持（具體數字）
                3. 行動建議（可執行的步驟）
                """,
                "constraints": """
                限制條件：
                - 所有百分比保留兩位小數
                - 金額使用千分位逗號
                - 使用繁體中文
                - 避免過於技術化的術語
                """
            },
            "verbose": False
        }

        agent = Agent(df, config=combined_config)

        print("\n使用組合提示查詢：")

        queries = [
            "提供完整的季度銷售分析報告",
            "評估各產品的表現並給出建議",
            "分析客戶滿意度與銷售的關係"
        ]

        for i, query in enumerate(queries, 1):
            try:
                print(f"\n查詢 {i}: {query}")
                response = agent.chat(query)
                print(f"回答:\n{response}")
                print("\n" + "-"*60)
            except Exception as e:
                print(f"錯誤: {str(e)}")

    except Exception as e:
        print(f"錯誤: {str(e)}")


def prompt_templates():
    """
    顯示各種提示模板
    """
    print("\n" + "="*60)
    print("提示模板庫")
    print("="*60)

    templates = {
        "金融分析": """
        你是金融數據分析專家，熟悉：
        - 財務指標（ROI, ROE, EBITDA）
        - 風險評估
        - 投資組合分析
        - 市場趨勢

        提供專業的金融分析和投資建議。
        """,

        "市場營銷": """
        你是數字營銷分析師，專注於：
        - 客戶獲取成本（CAC）
        - 客戶生命週期價值（LTV）
        - 轉換漏斗分析
        - A/B 測試結果

        提供數據驅動的營銷策略建議。
        """,

        "供應鏈": """
        你是供應鏈優化專家，關注：
        - 庫存週轉率
        - 訂單履行時間
        - 供應商績效
        - 需求預測

        提供優化供應鏈效率的建議。
        """,

        "人力資源": """
        你是 HR 數據分析師，專精於：
        - 員工績效評估
        - 離職率分析
        - 薪酬競爭力
        - 培訓效果評估

        提供改善人力資源管理的洞察。
        """,

        "客戶服務": """
        你是客戶體驗分析專家，關注：
        - NPS（淨推薦值）
        - CSAT（客戶滿意度）
        - 平均處理時間
        - 首次解決率

        提供提升客戶滿意度的建議。
        """
    }

    for industry, prompt in templates.items():
        print(f"\n【{industry}】")
        print(prompt.strip())
        print("-" * 60)


def main():
    """
    主函數：演示自定義提示功能
    """
    print("PandasAI 自定義提示示例")
    print("="*60)

    # 檢查 API 密鑰
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("警告: 未找到 OPENAI_API_KEY 環境變量")
        print("請在 .env 文件中設置: OPENAI_API_KEY=your_api_key")
        print("\n顯示示例數據和提示模板...")

        # 顯示示例數據
        df = create_sample_dataframe()
        print("\n示例數據（前 10 行）:")
        print(df.head(10))

        # 顯示提示模板
        prompt_templates()

        return

    try:
        # 1. 基本自定義提示
        basic_custom_prompt_example(api_key)

        # 2. 上下文感知提示
        context_aware_prompt_example(api_key)

        # 3. 指定輸出格式
        format_specific_prompt_example(api_key)

        # 4. 行業特定提示
        industry_specific_prompt_example(api_key)

        # 5. 組合提示
        combined_prompts_example(api_key)

        # 6. 顯示提示模板
        prompt_templates()

        # 總結
        print("\n" + "="*60)
        print("自定義提示功能總結")
        print("="*60)
        print("✓ 系統提示：定義 AI 的角色和專業領域")
        print("✓ 上下文提示：添加業務背景信息")
        print("✓ 格式提示：指定輸出格式")
        print("✓ 行業提示：使用行業特定術語")
        print("✓ 組合提示：結合多種提示類型")

        print("\n最佳實踐：")
        print("- 明確定義 AI 的角色和專業領域")
        print("- 提供充分的業務上下文")
        print("- 指定清晰的輸出格式")
        print("- 使用行業特定術語提高專業性")
        print("- 迭代優化提示詞以獲得更好結果")
        print("- 保持提示簡潔但信息豐富")

    except ImportError:
        print("\n錯誤: 未安裝 pandasai 庫")
        print("請運行: pip install pandasai")
    except Exception as e:
        print(f"\n發生錯誤: {str(e)}")
        print(f"錯誤類型: {type(e).__name__}")

        # 提供故障排除建議
        print("\n故障排除建議:")
        print("1. 檢查自定義提示的格式是否正確")
        print("2. 確保提示不會太長（注意 token 限制）")
        print("3. 使用 GPT-4 以獲得更好的理解能力")
        print("4. 測試不同的提示組合")
        print("5. 監控 API 使用量和成本")


if __name__ == "__main__":
    main()
