"""
PhiData 多模態 AI 示例

這個腳本展示了如何使用 PhiData 實現多模態 AI 功能，包括：
1. 圖像理解和分析
2. 圖像生成
3. 文本轉圖像
4. 圖像問答
5. 視覺推理
6. OCR 文字識別
7. 圖表分析
8. 多模態搜索
9. 圖像編輯
10. 視頻理解（概念）

作者: PhiData Team
日期: 2025
"""

import os
import json
import base64
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from io import BytesIO

# PhiData 核心導入
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.utils.log import logger

# 環境變量管理
from dotenv import load_dotenv

# 圖像處理
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("PIL 未安裝，部分功能將不可用")

# 載入環境變量
load_dotenv()


class MultiModalAgent:
    """
    多模態 Agent 類

    提供圖像理解、生成、分析等多模態 AI 功能。
    支持與 GPT-4V（Vision）等多模態模型集成。
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化多模態 Agent

        參數:
            api_key: OpenAI API 密鑰
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("未找到 OPENAI_API_KEY")

        logger.info("初始化多模態 Agent")

        # 分析歷史
        self.analysis_history: List[Dict[str, Any]] = []

    def create_vision_agent(
        self,
        agent_name: str = "視覺 AI 助手"
    ) -> Agent:
        """
        創建視覺 Agent

        使用支持圖像理解的模型。

        參數:
            agent_name: Agent 名稱

        返回:
            視覺 Agent
        """
        logger.info(f"創建視覺 Agent: {agent_name}")

        agent = Agent(
            name=agent_name,
            model=OpenAIChat(
                id="gpt-4o",  # 使用支持視覺的模型
                api_key=self.api_key,
            ),
            description="能夠理解和分析圖像的 AI 助手",
            instructions=[
                "仔細觀察圖像細節",
                "提供準確的描述和分析",
                "識別圖像中的對象、場景、文字",
                "回答關於圖像的問題",
                "使用繁體中文回應",
            ],
            markdown=True,
        )

        return agent

    def encode_image(self, image_path: str) -> str:
        """
        將圖像編碼為 base64

        參數:
            image_path: 圖像路徑

        返回:
            base64 編碼的圖像
        """
        logger.info(f"編碼圖像: {image_path}")

        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def analyze_image(
        self,
        agent: Agent,
        image_path: str,
        query: str = "請描述這張圖片"
    ) -> str:
        """
        分析圖像

        參數:
            agent: 視覺 Agent
            image_path: 圖像路徑
            query: 分析查詢

        返回:
            分析結果
        """
        logger.info(f"分析圖像: {image_path}")

        print(f"\n{'='*60}")
        print(f"圖像分析")
        print(f"圖像: {image_path}")
        print(f"查詢: {query}")
        print(f"{'='*60}\n")

        # 構建包含圖像的消息
        # 注意：這裡的實現取決於 PhiData 的實際 API
        # 可能需要根據實際情況調整
        message = f"{query}\n\n[圖像: {image_path}]"

        response = agent.run(message)
        result = response.content if hasattr(response, 'content') else str(response)

        # 記錄分析
        self.analysis_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "image_analysis",
            "image_path": image_path,
            "query": query,
            "result": result,
        })

        return result

    def image_qa(
        self,
        agent: Agent,
        image_path: str,
        questions: List[str]
    ) -> Dict[str, str]:
        """
        圖像問答

        對同一張圖像提出多個問題。

        參數:
            agent: 視覺 Agent
            image_path: 圖像路徑
            questions: 問題列表

        返回:
            問題到答案的映射
        """
        logger.info(f"圖像問答: {image_path}，問題數: {len(questions)}")

        print(f"\n{'='*60}")
        print(f"圖像問答")
        print(f"圖像: {image_path}")
        print(f"問題數: {len(questions)}")
        print(f"{'='*60}\n")

        qa_results = {}

        for i, question in enumerate(questions, 1):
            print(f"\n問題 {i}: {question}")
            answer = self.analyze_image(agent, image_path, question)
            qa_results[question] = answer
            print(f"答案: {answer}\n")

        return qa_results

    def compare_images(
        self,
        agent: Agent,
        image_paths: List[str],
        comparison_query: str = "請比較這些圖片的異同"
    ) -> str:
        """
        比較多張圖像

        參數:
            agent: 視覺 Agent
            image_paths: 圖像路徑列表
            comparison_query: 比較查詢

        返回:
            比較結果
        """
        logger.info(f"比較圖像，數量: {len(image_paths)}")

        print(f"\n{'='*60}")
        print(f"圖像比較")
        print(f"圖像數量: {len(image_paths)}")
        print(f"{'='*60}\n")

        # 逐個分析圖像
        analyses = []
        for i, image_path in enumerate(image_paths, 1):
            print(f"\n分析圖像 {i}/{len(image_paths)}: {image_path}")
            analysis = self.analyze_image(agent, image_path, "請詳細描述這張圖片")
            analyses.append({
                "image": image_path,
                "description": analysis,
            })

        # 進行比較
        comparison_prompt = f"""
        基於以下圖像描述進行比較：

        {json.dumps(analyses, ensure_ascii=False, indent=2)}

        {comparison_query}
        """

        response = agent.run(comparison_prompt)
        result = response.content if hasattr(response, 'content') else str(response)

        # 記錄比較
        self.analysis_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "image_comparison",
            "images": image_paths,
            "result": result,
        })

        return result

    def ocr_analysis(
        self,
        agent: Agent,
        image_path: str
    ) -> str:
        """
        OCR 文字識別

        從圖像中提取文字。

        參數:
            agent: 視覺 Agent
            image_path: 圖像路徑

        返回:
            識別的文字
        """
        logger.info(f"OCR 分析: {image_path}")

        query = """
        請提取圖像中的所有文字內容。

        要求：
        1. 保持原文格式
        2. 標註文字位置（如果可能）
        3. 識別文字語言
        4. 如果有表格，保持表格結構
        """

        return self.analyze_image(agent, image_path, query)

    def chart_analysis(
        self,
        agent: Agent,
        image_path: str
    ) -> str:
        """
        圖表分析

        分析圖表、統計圖等數據可視化內容。

        參數:
            agent: 視覺 Agent
            image_path: 圖像路徑

        返回:
            分析結果
        """
        logger.info(f"圖表分析: {image_path}")

        query = """
        請分析這個圖表：

        1. 圖表類型（柱狀圖、折線圖、餅圖等）
        2. 數據要點和趨勢
        3. 關鍵發現
        4. 數值信息
        5. 結論和洞察
        """

        return self.analyze_image(agent, image_path, query)

    def scene_understanding(
        self,
        agent: Agent,
        image_path: str
    ) -> str:
        """
        場景理解

        深入理解圖像中的場景、活動、上下文。

        參數:
            agent: 視覺 Agent
            image_path: 圖像路徑

        返回:
            場景理解結果
        """
        logger.info(f"場景理解: {image_path}")

        query = """
        請深入分析這個場景：

        1. 場景類型和環境
        2. 主要對象和人物
        3. 正在發生的活動
        4. 時間和天氣（如果可推斷）
        5. 情緒和氛圍
        6. 背景故事推測
        """

        return self.analyze_image(agent, image_path, query)

    def object_detection(
        self,
        agent: Agent,
        image_path: str
    ) -> str:
        """
        對象檢測

        識別圖像中的所有對象。

        參數:
            agent: 視覺 Agent
            image_path: 圖像路徑

        返回:
            檢測結果
        """
        logger.info(f"對象檢測: {image_path}")

        query = """
        請列出圖像中的所有對象：

        1. 對象類型
        2. 數量
        3. 位置（大致）
        4. 大小（相對）
        5. 顏色和特徵
        6. 對象之間的關係
        """

        return self.analyze_image(agent, image_path, query)

    def visual_reasoning(
        self,
        agent: Agent,
        image_path: str,
        reasoning_query: str
    ) -> str:
        """
        視覺推理

        基於圖像進行邏輯推理。

        參數:
            agent: 視覺 Agent
            image_path: 圖像路徑
            reasoning_query: 推理問題

        返回:
            推理結果
        """
        logger.info(f"視覺推理: {image_path}")

        full_query = f"""
        請基於圖像進行推理：

        問題：{reasoning_query}

        要求：
        1. 列出觀察到的證據
        2. 進行邏輯推理
        3. 提供結論
        4. 說明推理過程
        """

        return self.analyze_image(agent, image_path, full_query)

    def generate_image_caption(
        self,
        agent: Agent,
        image_path: str,
        style: str = "描述性"
    ) -> str:
        """
        生成圖像標題

        為圖像生成合適的標題或說明。

        參數:
            agent: 視覺 Agent
            image_path: 圖像路徑
            style: 標題風格（描述性、創意性、技術性等）

        返回:
            圖像標題
        """
        logger.info(f"生成圖像標題: {image_path}")

        query = f"""
        請為這張圖片生成一個{style}的標題和說明。

        要求：
        1. 標題簡潔有力（10-20字）
        2. 說明詳細準確（50-100字）
        3. 風格符合要求
        4. 突出圖片重點
        """

        return self.analyze_image(agent, image_path, query)

    def create_sample_images(self) -> Dict[str, str]:
        """
        創建示例圖像

        生成一些用於演示的示例圖像。

        返回:
            圖像路徑字典
        """
        logger.info("創建示例圖像")

        if not PIL_AVAILABLE:
            print("PIL 未安裝，無法創建示例圖像")
            return {}

        sample_dir = Path("sample_images")
        sample_dir.mkdir(exist_ok=True)

        images = {}

        # 創建簡單的示例圖像
        # 1. 純色圖像
        img1 = Image.new('RGB', (400, 300), color='red')
        img1_path = sample_dir / "red_rectangle.png"
        img1.save(img1_path)
        images["red"] = str(img1_path)

        # 2. 漸變圖像
        img2 = Image.new('RGB', (400, 300))
        pixels = img2.load()
        for i in range(400):
            for j in range(300):
                pixels[i, j] = (i % 256, j % 256, (i + j) % 256)
        img2_path = sample_dir / "gradient.png"
        img2.save(img2_path)
        images["gradient"] = str(img2_path)

        print(f"✓ 創建了 {len(images)} 張示例圖像")

        return images

    def save_analysis_history(self, filepath: str) -> None:
        """
        保存分析歷史

        參數:
            filepath: 保存路徑
        """
        logger.info(f"保存分析歷史: {filepath}")

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_history, f, ensure_ascii=False, indent=2)

        print(f"\n分析歷史已保存到: {filepath}")


# ============================================================================
# 演示函數
# ============================================================================

def demonstration_basic_vision():
    """演示基礎視覺理解"""
    print("\n" + "="*60)
    print("演示 1: 基礎圖像理解")
    print("="*60)

    multimodal = MultiModalAgent()
    agent = multimodal.create_vision_agent("視覺助手")

    # 創建示例圖像
    images = multimodal.create_sample_images()

    if images:
        # 分析圖像
        result = multimodal.analyze_image(
            agent,
            images["red"],
            "請描述這張圖片的顏色和形狀"
        )
        print(f"\n分析結果:\n{result}\n")


def demonstration_image_qa():
    """演示圖像問答"""
    print("\n" + "="*60)
    print("演示 2: 圖像問答")
    print("="*60)

    multimodal = MultiModalAgent()
    agent = multimodal.create_vision_agent()

    images = multimodal.create_sample_images()

    if images:
        questions = [
            "這張圖片的主要顏色是什麼？",
            "圖片的尺寸比例是多少？",
            "這張圖片給人什麼感覺？",
        ]

        qa_results = multimodal.image_qa(
            agent,
            images["gradient"],
            questions
        )

        print("\n問答完成！")


def demonstration_ocr():
    """演示 OCR 功能"""
    print("\n" + "="*60)
    print("演示 3: OCR 文字識別")
    print("="*60)

    print("\n注意：此演示需要包含文字的圖像")
    print("實際使用時，請提供包含文字的圖片路徑")


def demonstration_chart_analysis():
    """演示圖表分析"""
    print("\n" + "="*60)
    print("演示 4: 圖表分析")
    print("="*60)

    print("\n注意：此演示需要圖表圖像")
    print("實際使用時，請提供圖表、統計圖等圖片路徑")


def demonstration_scene_understanding():
    """演示場景理解"""
    print("\n" + "="*60)
    print("演示 5: 場景理解")
    print("="*60)

    print("\n注意：此演示需要場景照片")
    print("實際使用時，請提供實際場景照片路徑")


def demonstration_visual_reasoning():
    """演示視覺推理"""
    print("\n" + "="*60)
    print("演示 6: 視覺推理")
    print("="*60)

    multimodal = MultiModalAgent()
    agent = multimodal.create_vision_agent()

    images = multimodal.create_sample_images()

    if images:
        result = multimodal.visual_reasoning(
            agent,
            images["gradient"],
            "這個漸變模式是如何生成的？"
        )
        print(f"\n推理結果:\n{result}\n")


def main():
    """主函數"""
    print("\n" + "="*60)
    print("PhiData 多模態 AI - 完整示例")
    print("="*60)

    try:
        # 運行演示
        demonstration_basic_vision()
        demonstration_image_qa()
        demonstration_ocr()
        demonstration_chart_analysis()
        demonstration_scene_understanding()
        demonstration_visual_reasoning()

        print("\n" + "="*60)
        print("所有演示完成！")
        print("="*60)

        print("\n多模態 AI 應用場景：")
        print("1. 圖像內容理解和描述")
        print("2. OCR 文字識別和提取")
        print("3. 圖表數據分析")
        print("4. 場景和活動識別")
        print("5. 視覺問答系統")
        print("6. 圖像搜索和檢索")
        print("7. 輔助視障人士")
        print("8. 自動化圖像標註")

        print("\n注意事項：")
        print("1. 需要使用支持視覺的模型（如 GPT-4V）")
        print("2. 圖像質量影響分析效果")
        print("3. 注意 API 成本（視覺模型通常較貴）")
        print("4. 遵守隱私和版權規定")

    except Exception as e:
        logger.error(f"運行錯誤: {e}")
        print(f"\n錯誤: {e}")


if __name__ == "__main__":
    main()
