"""
CrewAI 示例 02: 角色定義

這個示例展示如何設計豐富且具有個性的 Agent 角色。
我們將創建多個不同角色的 Agents，展示角色定義對 Agent 行為的影響。

學習重點:
- 如何撰寫有效的角色描述（role）
- 如何設定清晰的目標（goal）
- 如何創建吸引人的背景故事（backstory）
- 不同屬性如何影響 Agent 的行為
"""

import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process

load_dotenv()


def create_content_writer():
    """創建內容寫作專家 Agent"""
    return Agent(
        role="創意內容寫作專家",
        goal="創作引人入勝、信息豐富且 SEO 友好的內容",
        backstory="""你是一位獲獎無數的內容創作者，擁有 10 年的數字營銷經驗。
        你精通 SEO 優化，知道如何吸引讀者注意力。
        你的文字風格生動活潑，但又不失專業性。
        你總能找到完美的平衡點，讓內容既有深度又易於理解。

        你的作品曾登上多個頂級科技媒體的首頁，
        你最擅長將複雜的技術概念轉化為普通人能理解的語言。""",
        verbose=True,
        allow_delegation=False
    )


def create_seo_specialist():
    """創建 SEO 優化專家 Agent"""
    return Agent(
        role="SEO 優化專家",
        goal="確保內容在搜索引擎中獲得最佳排名",
        backstory="""你是 SEO 領域的資深專家，擁有超過 8 年的搜索引擎優化經驗。
        你深入理解 Google 的算法變化，總能預測搜索趨勢。

        你不僅關注關鍵詞密度，更注重用戶體驗和內容質量。
        你知道如何優化標題、元描述、標籤結構，
        以及如何建立有效的內部和外部鏈接策略。

        你曾幫助多家公司將網站流量提升 300% 以上。""",
        verbose=True,
        allow_delegation=False
    )


def create_editor():
    """創建編輯審校專家 Agent"""
    return Agent(
        role="資深編輯審校專家",
        goal="確保內容無誤、結構清晰、風格一致",
        backstory="""你是一位嚴謹的編輯，擁有新聞學碩士學位。
        你在頂級出版社工作了 12 年，審閱過上千篇文章。

        你對語法、標點、風格有近乎完美主義的要求。
        你能迅速發現邏輯漏洞、事實錯誤和不一致的地方。

        同時，你也是一位優秀的導師，
        總能用建設性的方式提出改進建議，而不是簡單地批評。

        你的座右銘是："好的內容需要打磨，優秀的內容需要雕琢。" """,
        verbose=True,
        allow_delegation=False
    )


def create_research_analyst():
    """創建數據分析研究員 Agent"""
    return Agent(
        role="數據分析研究員",
        goal="提供數據驅動的洞察和研究支持",
        backstory="""你是一位數據科學家，同時也是一位研究狂熱者。
        你擁有統計學博士學位，並在多家科技公司擔任數據分析師。

        你擅長從海量數據中提取有價值的洞察，
        你的研究報告總是基於紮實的數據和嚴謹的分析。

        你對新興技術充滿好奇，會主動追蹤最新的研究論文和行業報告。
        你能將複雜的統計分析結果轉化為清晰的商業建議。

        你相信："沒有數據支持的觀點只是意見，而不是事實。" """,
        verbose=True,
        allow_delegation=False
    )


def create_creative_strategist():
    """創建創意策略師 Agent"""
    return Agent(
        role="創意策略總監",
        goal="開發創新的內容策略和創意概念",
        backstory="""你是一位屢獲殊榮的創意總監，曾在全球頂尖廣告公司工作。
        你主導過多個病毒式傳播的營銷活動。

        你的思維方式獨特，總能從不同角度看問題。
        你擅長將品牌故事、用戶需求和市場趨勢完美結合。

        你的創意不只是好看，更是有效的。
        你深知如何觸動受眾的情感，如何在信息過載的時代脫穎而出。

        你的口頭禪是："偉大的創意不是憑空而來，而是深刻洞察的結晶。" """,
        verbose=True,
        allow_delegation=True  # 策略師可以委託具體執行任務
    )


def demonstrate_role_impact():
    """
    演示不同角色定義對 Agent 行為的影響

    我們將讓不同角色的 Agents 完成相同的任務，
    觀察他們的工作方式和輸出結果的差異。
    """

    print("=" * 80)
    print("CrewAI 角色定義示例 - 角色對行為的影響")
    print("=" * 80)
    print()

    # 創建不同角色的 Agents
    writer = create_content_writer()
    seo_expert = create_seo_specialist()
    editor = create_editor()
    researcher = create_research_analyst()
    strategist = create_creative_strategist()

    print("📋 創建了 5 個不同角色的 Agents:")
    print(f"1. {writer.role}")
    print(f"2. {seo_expert.role}")
    print(f"3. {editor.role}")
    print(f"4. {researcher.role}")
    print(f"5. {strategist.role}")
    print()

    # 為每個 Agent 創建特定的任務
    topic = "CrewAI - 新一代 AI Agent 協作框架"

    # 策略師的任務
    strategy_task = Task(
        description=f"""為主題 "{topic}" 開發一個全面的內容策略。

        你的策略應該包括:
        1. 目標受眾分析
        2. 核心信息點
        3. 內容角度和創意方向
        4. 預期效果和成功指標

        請確保策略既有創意又切實可行。""",

        expected_output="一份創意內容策略文檔，包含受眾分析、核心信息、創意方向和成功指標",
        agent=strategist
    )

    # 研究員的任務
    research_task = Task(
        description=f"""對 "{topic}" 進行深入的數據研究和分析。

        你需要:
        1. 收集相關數據和統計信息
        2. 分析市場趨勢和競爭態勢
        3. 識別關鍵洞察和機會點
        4. 提供數據支持的建議

        確保所有結論都有數據支撐。""",

        expected_output="一份數據驅動的研究報告，包含統計分析、趨勢洞察和建議",
        agent=researcher
    )

    # 創建 Crew 並執行
    crew = Crew(
        agents=[strategist, researcher],
        tasks=[strategy_task, research_task],
        process=Process.sequential,
        verbose=True
    )

    print("🚀 開始執行任務...")
    print("-" * 80)
    print()

    try:
        result = crew.kickoff()

        print()
        print("=" * 80)
        print("✅ 執行完成！")
        print("=" * 80)
        print()
        print("📊 最終結果:")
        print("-" * 80)
        print(result)
        print()

    except Exception as e:
        print(f"❌ 執行錯誤: {str(e)}")


def demonstrate_role_attributes():
    """展示不同的 Agent 屬性配置"""

    print("\n" + "=" * 80)
    print("Agent 屬性配置最佳實踐")
    print("=" * 80)
    print()

    print("📝 Role（角色）編寫建議:")
    print("-" * 80)
    print("✅ 要做:")
    print("  • 使用具體、專業的角色名稱")
    print("  • 明確角色的專業領域")
    print("  • 保持簡潔（5-10 個字）")
    print()
    print("❌ 避免:")
    print("  • 模糊的角色描述")
    print("  • 過於寬泛的角色定位")
    print("  • 冗長的角色名稱")
    print()

    print("🎯 Goal（目標）編寫建議:")
    print("-" * 80)
    print("✅ 要做:")
    print("  • 使用動詞開頭（創建、分析、優化等）")
    print("  • 明確具體的期望結果")
    print("  • 與角色專業領域對齊")
    print()
    print("❌ 避免:")
    print("  • 模糊的目標描述")
    print("  • 與角色不匹配的目標")
    print("  • 過於宏大或不切實際的目標")
    print()

    print("📖 Backstory（背景故事）編寫建議:")
    print("-" * 80)
    print("✅ 要做:")
    print("  • 提供豐富的專業背景")
    print("  • 描述工作風格和方法")
    print("  • 包含成就和經驗")
    print("  • 展示個性和價值觀")
    print("  • 使用生動的語言")
    print()
    print("❌ 避免:")
    print("  • 過於簡單的背景")
    print("  • 與角色不一致的描述")
    print("  • 純粹虛構無關的信息")
    print()


def main():
    """主函數"""

    # 演示角色定義的影響
    demonstrate_role_impact()

    # 展示屬性配置建議
    demonstrate_role_attributes()


if __name__ == "__main__":
    main()


"""
關鍵要點:
----------

1. Role（角色）的重要性:
   - 定義 Agent 的專業身份
   - 影響 Agent 的思考方式
   - 決定 Agent 的專業視角

2. Goal（目標）的作用:
   - 指導 Agent 的行動方向
   - 幫助 Agent 做出決策
   - 評估任務完成情況

3. Backstory（背景故事）的價值:
   - 豐富 Agent 的個性
   - 影響 Agent 的工作風格
   - 增強輸出的一致性和可信度

4. 屬性組合的藝術:
   - role + goal + backstory 應該協調一致
   - 共同塑造 Agent 的完整人格
   - 影響團隊協作的效果

最佳實踐:
----------
✅ 為每個 Agent 創建獨特的身份
✅ 確保角色與任務匹配
✅ 使用具體、生動的語言
✅ 保持專業性和一致性
✅ 考慮團隊協作的需求

下一步:
-------
- 03_任務設計.py: 學習如何設計複雜任務
- 04_團隊組建.py: 創建高效的多 Agent 團隊
"""
