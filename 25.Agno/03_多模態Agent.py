"""
03_多模態Agent.py - Agno 多模態 Agent 完整指南

本範例展示 Agno 的多模態處理能力，包括：
- 圖像理解與分析（Image Understanding）
- 圖像描述與生成
- OCR 文字識別
- 音頻轉錄與分析
- 視頻內容理解
- 多模態融合應用

作者：LLM-agent-Demo Team
日期：2025-12
框架：Agno (原 Phidata)
"""

import os
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv

# Agno 核心導入
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools

# 載入環境變數
load_dotenv()


# ============================================================================
# 範例 1: 圖像理解 - 使用 GPT-4 Vision
# ============================================================================
def example_1_image_understanding():
    """
    使用 GPT-4 Vision 理解圖像內容

    支持的圖像格式：
    - JPEG, PNG, GIF, WebP
    - 本地文件或 URL
    """
    print("\n" + "="*80)
    print("範例 1: 圖像理解 - GPT-4 Vision")
    print("="*80)

    # 創建視覺 Agent
    vision_agent = Agent(
        name="vision_analyst",
        role="專業的圖像分析師",
        model=OpenAIChat(id="gpt-4-vision-preview"),

        instructions=[
            "仔細觀察圖像中的所有細節",
            "提供準確、詳細的圖像描述",
            "識別圖像中的對象、場景、文字",
            "分析圖像的構圖、色彩、風格"
        ],

        markdown=True
    )

    # 範例圖片 URL（可以替換為你自己的圖片）
    image_urls = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
    ]

    for i, image_url in enumerate(image_urls, 1):
        print(f"\n分析圖片 {i}: {image_url}")
        print("-" * 80)

        # 分析圖片
        response = vision_agent.run(
            f"請詳細描述這張圖片的內容：{image_url}"
        )

        print(f"\n分析結果:\n{response.content}\n")


# ============================================================================
# 範例 2: OCR 文字識別
# ============================================================================
def example_2_ocr_text_recognition():
    """
    使用 Vision 模型進行 OCR 文字識別

    應用場景：
    - 名片識別
    - 文檔掃描
    - 截圖文字提取
    - 手寫文字識別
    """
    print("\n" + "="*80)
    print("範例 2: OCR 文字識別")
    print("="*80)

    # 創建 OCR Agent
    ocr_agent = Agent(
        name="ocr_specialist",
        role="OCR 文字識別專家",
        model=OpenAIChat(id="gpt-4-vision-preview"),

        instructions=[
            "識別圖片中的所有文字",
            "保持原始文字的格式和結構",
            "如果有多種語言，分別標註",
            "對不清晰的文字進行標記"
        ],

        markdown=True
    )

    # 測試圖片（包含文字的圖片）
    print("\n任務: 識別圖片中的文字")
    print("-" * 80)

    # 示例：識別包含文字的圖片
    test_prompt = """
    請從以下圖片中提取所有文字：
    https://example.com/sample-text-image.jpg

    請按照原始格式輸出文字，並標註語言類型。
    """

    print("提示: 在實際使用中，請替換為包含文字的真實圖片 URL\n")

    # response = ocr_agent.run(test_prompt)
    # print(f"\n識別結果:\n{response.content}\n")


# ============================================================================
# 範例 3: 圖像對比分析
# ============================================================================
def example_3_image_comparison():
    """
    對比分析多張圖片

    應用場景：
    - 產品版本對比
    - 前後對比分析
    - 相似度檢測
    - 變化檢測
    """
    print("\n" + "="*80)
    print("範例 3: 圖像對比分析")
    print("="*80)

    # 創建圖像對比 Agent
    comparison_agent = Agent(
        name="image_comparator",
        role="圖像對比分析專家",
        model=OpenAIChat(id="gpt-4-vision-preview"),

        instructions=[
            "仔細對比多張圖片的差異",
            "列出主要的相同點和不同點",
            "使用結構化的方式呈現對比結果",
            "提供專業的分析見解"
        ],

        markdown=True
    )

    print("\n任務: 對比兩張圖片的差異")
    print("-" * 80)

    comparison_task = """
    請對比以下兩張圖片，列出它們的相同點和不同點：

    圖片 1: [第一張圖片的 URL]
    圖片 2: [第二張圖片的 URL]

    請從以下角度進行對比：
    1. 內容主題
    2. 色彩風格
    3. 構圖方式
    4. 細節差異
    """

    print(f"分析任務:\n{comparison_task}\n")
    print("提示: 在實際使用中，請替換為真實圖片 URL\n")


# ============================================================================
# 範例 4: 圖表和數據可視化分析
# ============================================================================
def example_4_chart_analysis():
    """
    分析圖表和數據可視化

    支持分析：
    - 折線圖、柱狀圖、餅圖
    - 數據趨勢分析
    - 統計圖表解讀
    - 商業報表分析
    """
    print("\n" + "="*80)
    print("範例 4: 圖表和數據可視化分析")
    print("="*80)

    # 創建數據分析 Agent
    chart_agent = Agent(
        name="chart_analyst",
        role="數據可視化分析專家",
        model=OpenAIChat(id="gpt-4-vision-preview"),

        instructions=[
            "仔細分析圖表中的數據",
            "識別關鍵趨勢和模式",
            "提取重要的數據點",
            "提供專業的解讀和見解",
            "指出可能的異常值或有趣發現"
        ],

        markdown=True
    )

    print("\n任務: 分析商業數據圖表")
    print("-" * 80)

    analysis_task = """
    請分析這張銷售趨勢圖表：
    [圖表 URL]

    請提供以下分析：
    1. 整體趨勢描述
    2. 關鍵數據點
    3. 異常值或特殊模式
    4. 商業洞察和建議
    """

    print(f"分析任務:\n{analysis_task}\n")
    print("提示: 在實際使用中，請替換為真實圖表 URL\n")


# ============================================================================
# 範例 5: 多模態融合 - 圖像 + 文本
# ============================================================================
def example_5_multimodal_fusion():
    """
    結合圖像和文本進行綜合分析

    應用場景：
    - 社交媒體內容分析
    - 產品評論分析
    - 內容審核
    - 廣告效果評估
    """
    print("\n" + "="*80)
    print("範例 5: 多模態融合 - 圖像 + 文本")
    print("="*80)

    # 創建多模態分析 Agent
    multimodal_agent = Agent(
        name="multimodal_analyst",
        role="多模態內容分析專家",
        model=OpenAIChat(id="gpt-4-vision-preview"),

        # 添加搜索工具以獲取額外信息
        tools=[DuckDuckGoTools()],

        instructions=[
            "綜合分析圖像和文本內容",
            "識別內容的一致性和關聯性",
            "評估內容的質量和真實性",
            "提供全面的分析報告",
            "必要時搜索相關背景信息"
        ],

        show_tool_calls=True,
        markdown=True
    )

    print("\n任務: 分析社交媒體帖子（圖像 + 文本）")
    print("-" * 80)

    # 模擬社交媒體內容
    post_content = """
    文字內容：
    "今天參加了 AI 技術峰會，學到了很多關於 Agno 框架的知識！
    它的性能真的比其他框架快很多。#AI #Agno #TechConference"

    圖片：[會議現場照片 URL]

    請分析：
    1. 圖文是否一致
    2. 內容的真實性和可信度
    3. 情感傾向
    4. 可能的目標受眾
    5. 內容優化建議
    """

    print(f"分析內容:\n{post_content}\n")


# ============================================================================
# 範例 6: 圖像生成提示詞創建
# ============================================================================
def example_6_image_prompt_generation():
    """
    基於圖像創建圖像生成提示詞

    應用場景：
    - 為 DALL-E / Midjourney 生成提示詞
    - 圖像風格轉換
    - 創意設計輔助
    """
    print("\n" + "="*80)
    print("範例 6: 圖像生成提示詞創建")
    print("="*80)

    # 創建提示詞生成 Agent
    prompt_agent = Agent(
        name="prompt_engineer",
        role="AI 圖像生成提示詞專家",
        model=OpenAIChat(id="gpt-4-vision-preview"),

        instructions=[
            "分析圖像的所有視覺元素",
            "創建詳細的圖像生成提示詞",
            "包含風格、構圖、色彩、氛圍等要素",
            "提供多個版本的提示詞",
            "適用於 DALL-E、Midjourney 等工具"
        ],

        markdown=True
    )

    print("\n任務: 為參考圖片生成 AI 繪圖提示詞")
    print("-" * 80)

    task = """
    請分析這張圖片並生成 3 個不同風格的 AI 繪圖提示詞：
    [參考圖片 URL]

    要求：
    1. 寫實風格版本
    2. 藝術風格版本
    3. 未來科技風格版本

    每個提示詞應包含：場景、主體、風格、色彩、光線、構圖等元素
    """

    print(f"任務描述:\n{task}\n")


# ============================================================================
# 範例 7: 視覺問答（VQA）
# ============================================================================
def example_7_visual_qa():
    """
    基於圖像的問答系統

    應用場景：
    - 產品諮詢
    - 教育輔助
    - 技術支持
    - 旅遊導覽
    """
    print("\n" + "="*80)
    print("範例 7: 視覺問答（VQA）")
    print("="*80)

    # 創建視覺問答 Agent
    vqa_agent = Agent(
        name="visual_qa_bot",
        role="視覺問答助手",
        model=OpenAIChat(id="gpt-4-vision-preview"),

        instructions=[
            "基於圖像內容回答用戶問題",
            "只回答圖像中可見的信息",
            "如果圖像中沒有相關信息，明確說明",
            "提供準確、具體的答案"
        ],

        markdown=True
    )

    print("\n場景: 產品圖片問答")
    print("-" * 80)

    # 模擬產品圖片問答
    product_image = "https://example.com/product.jpg"

    questions = [
        "這個產品是什麼顏色？",
        "圖片中有幾個產品？",
        "產品上有沒有文字或標誌？",
        "這個產品看起來是什麼材質？"
    ]

    print(f"產品圖片: {product_image}\n")

    for q in questions:
        print(f"問題: {q}")
        # response = vqa_agent.run(f"圖片：{product_image}\n問題：{q}")
        # print(f"回答: {response.content}\n")

    print("提示: 在實際使用中，Agent 會根據實際圖片內容回答\n")


# ============================================================================
# 範例 8: 圖像內容審核
# ============================================================================
def example_8_content_moderation():
    """
    圖像內容安全審核

    審核維度：
    - 暴力內容
    - 不當內容
    - 敏感信息
    - 版權問題
    """
    print("\n" + "="*80)
    print("範例 8: 圖像內容審核")
    print("="*80)

    # 創建內容審核 Agent
    moderation_agent = Agent(
        name="content_moderator",
        role="內容安全審核專員",
        model=OpenAIChat(id="gpt-4-vision-preview"),

        instructions=[
            "審核圖像內容的安全性和合規性",
            "檢測不當、暴力、敏感內容",
            "評估內容的適用年齡層",
            "提供詳細的審核報告",
            "給出內容改進建議"
        ],

        markdown=True
    )

    print("\n任務: 審核用戶上傳的圖片")
    print("-" * 80)

    moderation_task = """
    請審核以下圖片：
    [用戶上傳的圖片 URL]

    審核維度：
    1. 內容安全性（暴力、不當等）
    2. 適用年齡層
    3. 是否包含敏感信息（個人信息、隱私等）
    4. 內容質量
    5. 建議動作（通過/拒絕/需要人工審核）
    """

    print(f"審核任務:\n{moderation_task}\n")


# ============================================================================
# 主函數：運行所有範例
# ============================================================================
def main():
    """運行所有多模態範例"""

    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║            Agno 多模態 Agent 完整示範                          ║
    ║                                                                ║
    ║  展示圖像、音頻、視頻的處理能力和應用場景                      ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

    # 檢查環境變數
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 錯誤: 請設置 OPENAI_API_KEY 環境變數")
        return

    print("\n⚠️  注意: 多模態功能需要 GPT-4 Vision 模型支持")
    print("請確保你的 API Key 有權限訪問 gpt-4-vision-preview\n")

    try:
        # 運行各個範例
        example_1_image_understanding()
        example_2_ocr_text_recognition()
        example_3_image_comparison()
        example_4_chart_analysis()
        example_5_multimodal_fusion()
        example_6_image_prompt_generation()
        example_7_visual_qa()
        example_8_content_moderation()

        print("\n" + "="*80)
        print("✅ 所有範例展示完成！")
        print("="*80)

        print("\n📚 下一步學習：")
        print("- 04_Agentic_RAG.py - 學習智能 RAG 系統")
        print("- 05_團隊協作.py - 構建多 Agent 團隊")
        print("- 06_記憶和知識.py - 實現持久化記憶")

    except Exception as e:
        print(f"\n❌ 執行過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


# ============================================================================
# 學習要點總結
# ============================================================================
"""
📚 Agno 多模態學習要點：

1. **Vision 模型選擇**
   - GPT-4 Vision: 最強大的視覺理解
   - Claude 3: 優秀的圖像分析
   - Gemini Pro Vision: Google 的多模態模型

2. **圖像輸入方式**
   - URL: 直接提供圖片網址
   - Base64: 編碼後的圖片數據
   - 本地文件: 轉換為 Base64

3. **圖像理解能力**
   - 場景識別和描述
   - 對象檢測
   - OCR 文字識別
   - 圖表數據提取
   - 情感和風格分析

4. **多模態應用場景**
   - 內容審核與安全
   - 產品分析與 QA
   - 教育輔助
   - 醫療影像分析（需專業認證）
   - 藝術創作輔助

5. **最佳實踐**
   ```python
   vision_agent = Agent(
       model=OpenAIChat(id="gpt-4-vision-preview"),
       instructions=[
           "仔細觀察圖像細節",
           "提供準確的描述",
           "指出不確定的部分"
       ]
   )
   ```

6. **性能優化**
   - 圖片大小控制（建議 < 4MB）
   - 使用適當的分辨率
   - 批量處理時注意 token 限制
   - 緩存常用圖片分析結果

7. **錯誤處理**
   - 檢查圖片格式和大小
   - 處理無效 URL
   - 超時重試機制
   - 降級策略

8. **隱私與安全**
   - 避免上傳敏感圖片到公共服務
   - 實施內容過濾
   - 遵守數據隱私法規
   - 用戶授權與同意

💡 使用建議：
- 為不同任務提供明確的指導
- 結合其他工具（搜索、計算）增強能力
- 實施多層審核機制
- 監控 API 使用成本

🔗 相關資源：
- GPT-4 Vision 文檔: https://platform.openai.com/docs/guides/vision
- Agno 多模態指南: https://docs.agno.com/multimodal
- 最佳實踐: https://docs.agno.com/vision/best-practices

⚡ 多模態優勢：
- 突破純文本限制
- 更豐富的交互方式
- 解決實際視覺問題
- 提升用戶體驗
"""
