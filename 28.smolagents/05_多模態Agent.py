"""
多模態 Agent - 處理視覺和音頻
============================

smolagents 原生支持多模態！
不只是文本，還能處理圖像、音頻、視頻。

本範例展示：
1. 圖像理解和分析
2. 圖像生成和編輯
3. 語音識別（STT）
4. 文字轉語音（TTS）
5. 多模態組合任務
"""

from smolagents import CodeAgent, HfApiModel, tool
from typing import Optional
import base64
import io


# ============================================================================
# 範例 1: 圖像理解工具
# ============================================================================

@tool
def analyze_image(image_path: str, question: str) -> str:
    """
    分析圖像並回答問題（模擬）

    Args:
        image_path: 圖像文件路徑或 URL
        question: 關於圖像的問題

    Returns:
        分析結果
    """
    # 實際應用中會調用視覺模型 API
    # 這裡使用模擬響應
    mock_responses = {
        "這是什麼": "這是一張風景照片，包含山脈和湖泊",
        "有什麼顏色": "主要顏色有藍色（天空和湖泊）、綠色（樹木）和灰色（山脈）",
        "有多少人": "圖像中沒有人物",
    }

    # 根據問題返回模擬答案
    for key, value in mock_responses.items():
        if key in question:
            return value

    return f"圖像分析結果：{question}（這是模擬響應）"


def example_1_image_understanding():
    """圖像理解範例"""
    print("\n" + "="*70)
    print("範例 1: 圖像理解")
    print("="*70)

    print("\nsmolagents 可以處理圖像理解任務：")
    print("- 圖像描述")
    print("- 物體檢測")
    print("- 視覺問答（VQA）")
    print("- 場景理解\n")

    model = HfApiModel()
    agent = CodeAgent(tools=[analyze_image], model=model, max_steps=5)

    # 使用真實的圖像 URL 或本地路徑
    result = agent.run(
        "分析這張圖片並告訴我主要內容：landscape.jpg",
        # image="https://example.com/landscape.jpg"  # 實際使用時提供圖像
    )

    print(f"\n結果: {result}")

    print("\n實際使用示例：")
    print("```python")
    print("from smolagents.tools import ImageQuestionAnsweringTool")
    print("")
    print("agent = CodeAgent(")
    print("    tools=[ImageQuestionAnsweringTool()],")
    print("    model=model")
    print(")")
    print("")
    print("result = agent.run(")
    print("    '這張圖片中有什麼動物？',")
    print("    image='path/to/image.jpg'")
    print(")")
    print("```")


# ============================================================================
# 範例 2: 圖像生成工具
# ============================================================================

@tool
def generate_image(prompt: str, style: Optional[str] = None) -> str:
    """
    根據描述生成圖像（模擬）

    Args:
        prompt: 圖像描述
        style: 可選的風格（如 'realistic', 'cartoon', 'artistic'）

    Returns:
        生成的圖像路徑或 URL
    """
    print(f"\n🎨 生成圖像:")
    print(f"   描述: {prompt}")
    if style:
        print(f"   風格: {style}")

    # 實際應用中會調用 DALL-E、Stable Diffusion 等
    generated_path = f"generated_image_{hash(prompt) % 1000}.png"
    print(f"   已生成: {generated_path}")

    return generated_path


@tool
def edit_image(image_path: str, instruction: str) -> str:
    """
    編輯現有圖像（模擬）

    Args:
        image_path: 原始圖像路徑
        instruction: 編輯指令

    Returns:
        編輯後的圖像路徑
    """
    print(f"\n✏️ 編輯圖像:")
    print(f"   原始圖像: {image_path}")
    print(f"   編輯指令: {instruction}")

    edited_path = f"edited_{image_path}"
    print(f"   已保存: {edited_path}")

    return edited_path


def example_2_image_generation():
    """圖像生成和編輯"""
    print("\n" + "="*70)
    print("範例 2: 圖像生成和編輯")
    print("="*70)

    print("\nsmolagents 支持圖像生成：")
    print("- 文字轉圖像（Text-to-Image）")
    print("- 圖像編輯")
    print("- 風格遷移")
    print("- 圖像修復\n")

    model = HfApiModel()
    agent = CodeAgent(
        tools=[generate_image, edit_image],
        model=model,
        max_steps=8
    )

    result = agent.run(
        "生成一張夕陽下的海灘圖片，風格要逼真，"
        "然後在圖片中添加一艘帆船"
    )

    print(f"\n結果: {result}")

    print("\n實際使用示例：")
    print("```python")
    print("from smolagents.tools import TextToImageTool")
    print("")
    print("agent = CodeAgent(")
    print("    tools=[TextToImageTool()],")
    print("    model=model")
    print(")")
    print("")
    print("result = agent.run(")
    print("    '生成一張未來城市的圖片'")
    print(")")
    print("```")


# ============================================================================
# 範例 3: 語音識別工具
# ============================================================================

@tool
def speech_to_text(audio_path: str, language: str = "zh-TW") -> dict:
    """
    將語音轉換為文字（模擬）

    Args:
        audio_path: 音頻文件路徑
        language: 語言代碼

    Returns:
        轉錄結果
    """
    print(f"\n🎤 語音轉文字:")
    print(f"   音頻: {audio_path}")
    print(f"   語言: {language}")

    # 模擬轉錄結果
    mock_transcript = "這是一段測試音頻，展示語音識別功能。"

    return {
        "transcript": mock_transcript,
        "language": language,
        "confidence": 0.95,
        "duration": 5.2
    }


def example_3_speech_to_text():
    """語音識別"""
    print("\n" + "="*70)
    print("範例 3: 語音識別（STT）")
    print("="*70)

    print("\nsmolagents 支持語音處理：")
    print("- 語音轉文字")
    print("- 多語言支持")
    print("- 時間戳提取")
    print("- 說話人識別\n")

    model = HfApiModel()
    agent = CodeAgent(tools=[speech_to_text], model=model, max_steps=5)

    result = agent.run(
        "轉錄這個音頻文件：meeting_recording.mp3"
    )

    print(f"\n結果: {result}")

    print("\n實際使用示例：")
    print("```python")
    print("from smolagents.tools import SpeechToTextTool")
    print("")
    print("agent = CodeAgent(")
    print("    tools=[SpeechToTextTool()],")
    print("    model=model")
    print(")")
    print("")
    print("result = agent.run(")
    print("    '轉錄這段語音',")
    print("    audio='path/to/audio.mp3'")
    print(")")
    print("```")


# ============================================================================
# 範例 4: 文字轉語音工具
# ============================================================================

@tool
def text_to_speech(
    text: str,
    voice: str = "female",
    language: str = "zh-TW"
) -> str:
    """
    將文字轉換為語音（模擬）

    Args:
        text: 要轉換的文字
        voice: 語音類型（'male', 'female'）
        language: 語言代碼

    Returns:
        生成的音頻文件路徑
    """
    print(f"\n🔊 文字轉語音:")
    print(f"   文字: {text}")
    print(f"   語音: {voice}")
    print(f"   語言: {language}")

    audio_path = f"tts_output_{hash(text) % 1000}.mp3"
    print(f"   已生成: {audio_path}")

    return audio_path


def example_4_text_to_speech():
    """文字轉語音"""
    print("\n" + "="*70)
    print("範例 4: 文字轉語音（TTS）")
    print("="*70)

    print("\nsmolagents 支持語音合成：")
    print("- 多語言 TTS")
    print("- 語音選擇")
    print("- 語速控制")
    print("- 情感調節\n")

    model = HfApiModel()
    agent = CodeAgent(tools=[text_to_speech], model=model, max_steps=5)

    result = agent.run(
        "將這段文字轉換為女性語音：'歡迎使用 smolagents 多模態功能'"
    )

    print(f"\n結果: {result}")

    print("\n實際使用示例：")
    print("```python")
    print("from smolagents.tools import TextToSpeechTool")
    print("")
    print("agent = CodeAgent(")
    print("    tools=[TextToSpeechTool()],")
    print("    model=model")
    print(")")
    print("")
    print("result = agent.run(")
    print("    '朗讀這段文字：Hello World'")
    print(")")
    print("```")


# ============================================================================
# 範例 5: 多模態組合任務
# ============================================================================

def example_5_multimodal_pipeline():
    """組合多個模態的複雜任務"""
    print("\n" + "="*70)
    print("範例 5: 多模態組合任務")
    print("="*70)

    print("\nCode Agent 可以組合多個模態完成複雜任務：")
    print("1. 分析圖像")
    print("2. 生成描述")
    print("3. 轉換為語音")
    print("4. 生成相關圖像\n")

    model = HfApiModel()
    agent = CodeAgent(
        tools=[
            analyze_image,
            generate_image,
            text_to_speech,
            speech_to_text
        ],
        model=model,
        max_steps=15
    )

    result = agent.run(
        "分析這張圖片：photo.jpg，"
        "生成一段描述，"
        "將描述轉換為語音，"
        "然後根據描述生成一張新的藝術風格圖片"
    )

    print(f"\n結果: {result}")

    print("\n這展示了 smolagents 的強大之處：")
    print("  - 跨模態處理")
    print("  - 自動編排流程")
    print("  - 靈活組合工具")


# ============================================================================
# 範例 6: 視覺推理任務
# ============================================================================

@tool
def compare_images(image1: str, image2: str) -> dict:
    """
    比較兩張圖片（模擬）

    Args:
        image1: 第一張圖片路徑
        image2: 第二張圖片路徑

    Returns:
        比較結果
    """
    print(f"\n🔍 比較圖片:")
    print(f"   圖片 1: {image1}")
    print(f"   圖片 2: {image2}")

    return {
        "similarity": 0.85,
        "differences": ["顏色略有不同", "背景有些許差異"],
        "same_objects": ["主體物件相同"],
    }


@tool
def detect_objects(image_path: str) -> list:
    """
    檢測圖片中的物體（模擬）

    Args:
        image_path: 圖片路徑

    Returns:
        檢測到的物體列表
    """
    # 模擬物體檢測結果
    objects = [
        {"label": "person", "confidence": 0.95, "bbox": [100, 100, 200, 300]},
        {"label": "car", "confidence": 0.89, "bbox": [300, 150, 450, 250]},
        {"label": "tree", "confidence": 0.92, "bbox": [50, 50, 150, 200]},
    ]

    print(f"\n🎯 檢測到 {len(objects)} 個物體:")
    for obj in objects:
        print(f"   - {obj['label']} (信心度: {obj['confidence']:.2f})")

    return objects


def example_6_visual_reasoning():
    """視覺推理任務"""
    print("\n" + "="*70)
    print("範例 6: 視覺推理")
    print("="*70)

    print("\nsmolagents 支持複雜的視覺推理：")
    print("- 物體檢測和識別")
    print("- 圖像比較")
    print("- 場景理解")
    print("- 視覺關係推理\n")

    model = HfApiModel()
    agent = CodeAgent(
        tools=[compare_images, detect_objects, analyze_image],
        model=model,
        max_steps=10
    )

    result = agent.run(
        "檢測 photo1.jpg 中的所有物體，"
        "然後與 photo2.jpg 比較，"
        "找出兩張圖片的主要差異"
    )

    print(f"\n結果: {result}")


# ============================================================================
# 範例 7: 多模態工具集成
# ============================================================================

def example_7_builtin_multimodal_tools():
    """使用內建的多模態工具"""
    print("\n" + "="*70)
    print("範例 7: 內建多模態工具")
    print("="*70)

    print("\nsmolagents 提供了豐富的內建多模態工具：\n")

    tools_info = [
        {
            "工具": "ImageQuestionAnsweringTool",
            "功能": "回答關於圖像的問題",
            "用途": "視覺問答、圖像理解"
        },
        {
            "工具": "TextToImageTool",
            "功能": "根據文字生成圖像",
            "用途": "創意設計、內容生成"
        },
        {
            "工具": "ImageTransformationTool",
            "功能": "變換和編輯圖像",
            "用途": "圖像處理、風格遷移"
        },
        {
            "工具": "SpeechToTextTool",
            "功能": "語音轉文字",
            "用途": "會議轉錄、字幕生成"
        },
        {
            "工具": "TextToSpeechTool",
            "功能": "文字轉語音",
            "用途": "有聲讀物、語音助手"
        },
        {
            "工具": "DocumentQuestionAnsweringTool",
            "功能": "文檔問答",
            "用途": "文檔分析、信息提取"
        },
    ]

    for info in tools_info:
        print(f"{info['工具']}")
        print(f"  功能: {info['功能']}")
        print(f"  用途: {info['用途']}\n")

    print("使用示例：")
    print("```python")
    print("from smolagents.tools import (")
    print("    ImageQuestionAnsweringTool,")
    print("    TextToImageTool,")
    print("    SpeechToTextTool")
    print(")")
    print("")
    print("agent = CodeAgent(")
    print("    tools=[")
    print("        ImageQuestionAnsweringTool(),")
    print("        TextToImageTool(),")
    print("        SpeechToTextTool()")
    print("    ],")
    print("    model=HfApiModel()")
    print(")")
    print("```")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*70)
    print("多模態 Agent - 處理視覺和音頻")
    print("="*70)

    examples = [
        ("範例 1: 圖像理解", example_1_image_understanding),
        ("範例 2: 圖像生成和編輯", example_2_image_generation),
        ("範例 3: 語音識別", example_3_speech_to_text),
        ("範例 4: 文字轉語音", example_4_text_to_speech),
        ("範例 5: 多模態組合", example_5_multimodal_pipeline),
        ("範例 6: 視覺推理", example_6_visual_reasoning),
        ("範例 7: 內建工具", example_7_builtin_multimodal_tools),
    ]

    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n{name} 執行失敗: {e}")

    print("\n" + "="*70)
    print("多模態 Agent 完成！")
    print("="*70)

    print("\n關鍵要點：")
    print("  - smolagents 原生支持多模態")
    print("  - 可以處理圖像、音頻、視頻")
    print("  - 豐富的內建工具")
    print("  - 跨模態組合任務")
    print("  - Code Agent 自動編排流程")

    print("\n下一步: 查看 06_沙盒執行.py 學習安全執行環境")


if __name__ == "__main__":
    main()
