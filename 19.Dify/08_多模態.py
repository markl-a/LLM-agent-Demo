"""
Dify 多模態處理範例
==================

本範例展示如何使用 Dify 處理多模態內容（圖片、音頻、視頻等）。

多模態功能：
1. 圖片理解和分析
2. 圖片生成
3. 語音識別
4. 語音合成
5. 文件處理

安裝依賴：
pip install requests pillow
"""

import os
import json
import requests
import base64
from typing import Dict, Any, Optional, List, BinaryIO
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# ============================================================
# 配置
# ============================================================

DIFY_API_KEY = os.getenv("DIFY_API_KEY", "app-xxxxxxxxxxxxxxxx")
DIFY_BASE_URL = os.getenv("DIFY_BASE_URL", "https://api.dify.ai/v1")


# ============================================================
# 文件類型枚舉
# ============================================================

class FileType(Enum):
    """支持的文件類型"""
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"


class ImageFormat(Enum):
    """圖片格式"""
    PNG = "png"
    JPEG = "jpeg"
    GIF = "gif"
    WEBP = "webp"


# ============================================================
# 多模態客戶端
# ============================================================

class DifyMultimodalClient:
    """
    Dify 多模態客戶端

    提供多模態內容處理功能
    """

    def __init__(self, api_key: str, base_url: str = "https://api.dify.ai/v1"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_key}"
        }

    def upload_file(
        self,
        file_path: str,
        user: str
    ) -> Dict[str, Any]:
        """
        上傳文件

        Args:
            file_path: 文件路徑
            user: 用戶標識

        Returns:
            上傳結果，包含文件 ID
        """
        url = f"{self.base_url}/files/upload"

        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'user': user}

            response = requests.post(
                url,
                headers=self.headers,
                files=files,
                data=data
            )
            response.raise_for_status()

        return response.json()

    def chat_with_image(
        self,
        query: str,
        user: str,
        image_file_id: Optional[str] = None,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        帶圖片的對話

        Args:
            query: 用戶查詢
            user: 用戶標識
            image_file_id: 已上傳的文件 ID
            image_url: 圖片 URL
            image_base64: Base64 編碼的圖片
            conversation_id: 對話 ID

        Returns:
            對話響應
        """
        url = f"{self.base_url}/chat-messages"

        files = []

        if image_file_id:
            files.append({
                "type": "image",
                "transfer_method": "local_file",
                "upload_file_id": image_file_id
            })
        elif image_url:
            files.append({
                "type": "image",
                "transfer_method": "remote_url",
                "url": image_url
            })

        payload = {
            "query": query,
            "user": user,
            "response_mode": "blocking",
            "files": files
        }

        if conversation_id:
            payload["conversation_id"] = conversation_id

        headers = {
            **self.headers,
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        return response.json()

    def text_to_audio(
        self,
        text: str,
        user: str,
        voice: str = "alloy"
    ) -> bytes:
        """
        文字轉語音

        Args:
            text: 要轉換的文字
            user: 用戶標識
            voice: 語音類型

        Returns:
            音頻數據
        """
        url = f"{self.base_url}/text-to-audio"

        payload = {
            "text": text,
            "user": user,
            "voice": voice
        }

        headers = {
            **self.headers,
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        return response.content

    def audio_to_text(
        self,
        audio_file_path: str,
        user: str
    ) -> Dict[str, Any]:
        """
        語音轉文字

        Args:
            audio_file_path: 音頻文件路徑
            user: 用戶標識

        Returns:
            轉換結果
        """
        url = f"{self.base_url}/audio-to-text"

        with open(audio_file_path, 'rb') as f:
            files = {'file': f}
            data = {'user': user}

            response = requests.post(
                url,
                headers=self.headers,
                files=files,
                data=data
            )
            response.raise_for_status()

        return response.json()


# ============================================================
# 圖片處理工具
# ============================================================

class ImageProcessor:
    """
    圖片處理工具

    提供圖片預處理和轉換功能
    """

    @staticmethod
    def load_image_as_base64(file_path: str) -> str:
        """
        將圖片載入為 Base64

        Args:
            file_path: 圖片路徑

        Returns:
            Base64 編碼的圖片
        """
        with open(file_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    @staticmethod
    def save_base64_image(
        base64_data: str,
        output_path: str
    ):
        """
        保存 Base64 圖片

        Args:
            base64_data: Base64 編碼的圖片
            output_path: 輸出路徑
        """
        image_data = base64.b64decode(base64_data)
        with open(output_path, 'wb') as f:
            f.write(image_data)

    @staticmethod
    def get_image_info(file_path: str) -> Dict[str, Any]:
        """
        獲取圖片信息

        Args:
            file_path: 圖片路徑

        Returns:
            圖片信息
        """
        try:
            from PIL import Image

            with Image.open(file_path) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode,
                    "size_bytes": os.path.getsize(file_path)
                }
        except ImportError:
            # 如果沒有 PIL，返回基本信息
            return {
                "size_bytes": os.path.getsize(file_path),
                "extension": Path(file_path).suffix
            }

    @staticmethod
    def resize_image(
        file_path: str,
        max_size: int = 1024,
        output_path: Optional[str] = None
    ) -> str:
        """
        調整圖片大小

        Args:
            file_path: 圖片路徑
            max_size: 最大尺寸
            output_path: 輸出路徑

        Returns:
            輸出文件路徑
        """
        try:
            from PIL import Image

            with Image.open(file_path) as img:
                # 計算新尺寸
                ratio = min(max_size / img.width, max_size / img.height)
                if ratio < 1:
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)

                output = output_path or file_path
                img.save(output)
                return output

        except ImportError:
            print("需要安裝 Pillow: pip install pillow")
            return file_path


# ============================================================
# 音頻處理工具
# ============================================================

class AudioProcessor:
    """
    音頻處理工具

    提供音頻預處理功能
    """

    @staticmethod
    def get_audio_info(file_path: str) -> Dict[str, Any]:
        """
        獲取音頻信息

        Args:
            file_path: 音頻路徑

        Returns:
            音頻信息
        """
        return {
            "size_bytes": os.path.getsize(file_path),
            "extension": Path(file_path).suffix
        }

    @staticmethod
    def save_audio(
        audio_data: bytes,
        output_path: str
    ):
        """
        保存音頻文件

        Args:
            audio_data: 音頻數據
            output_path: 輸出路徑
        """
        with open(output_path, 'wb') as f:
            f.write(audio_data)


# ============================================================
# 使用範例
# ============================================================

def example_upload_and_chat():
    """
    範例 1: 上傳圖片並對話

    展示如何上傳圖片並進行對話
    """
    print("=" * 50)
    print("範例 1: 上傳圖片並對話")
    print("=" * 50)

    client = DifyMultimodalClient(
        api_key=DIFY_API_KEY,
        base_url=DIFY_BASE_URL
    )

    # 模擬上傳圖片
    print("模擬上傳圖片...")

    try:
        # 假設有一個圖片文件
        # upload_result = client.upload_file(
        #     file_path="path/to/image.jpg",
        #     user="user-001"
        # )
        # file_id = upload_result.get('id')

        # 使用圖片 URL 進行對話
        result = client.chat_with_image(
            query="請描述這張圖片的內容",
            user="user-001",
            image_url="https://example.com/sample-image.jpg"
        )

        print(f"回答: {result.get('answer', '')}")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_image_analysis():
    """
    範例 2: 圖片分析

    展示如何分析圖片內容
    """
    print("\n" + "=" * 50)
    print("範例 2: 圖片分析")
    print("=" * 50)

    client = DifyMultimodalClient(
        api_key=DIFY_API_KEY,
        base_url=DIFY_BASE_URL
    )

    # 分析任務列表
    analysis_tasks = [
        "描述圖片中的主要物體",
        "識別圖片中的文字（如果有）",
        "分析圖片的整體風格和色調",
        "判斷圖片的拍攝場景"
    ]

    print("圖片分析任務:")
    for task in analysis_tasks:
        print(f"  - {task}")

    # 模擬分析
    print("\n模擬分析結果:")
    print("  主要物體: 建築物、樹木、天空")
    print("  文字: 無")
    print("  風格: 自然風光，暖色調")
    print("  場景: 戶外公園")


def example_text_to_speech():
    """
    範例 3: 文字轉語音

    展示如何將文字轉換為語音
    """
    print("\n" + "=" * 50)
    print("範例 3: 文字轉語音")
    print("=" * 50)

    client = DifyMultimodalClient(
        api_key=DIFY_API_KEY,
        base_url=DIFY_BASE_URL
    )

    text = "你好！歡迎使用 Dify 多模態功能。這是一段測試語音。"

    print(f"文字: {text}")

    try:
        # 轉換為語音
        # audio_data = client.text_to_audio(
        #     text=text,
        #     user="user-001",
        #     voice="alloy"
        # )

        # 保存音頻
        # AudioProcessor.save_audio(audio_data, "output.mp3")
        # print("音頻已保存到 output.mp3")

        print("（模擬）語音生成完成")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_speech_to_text():
    """
    範例 4: 語音轉文字

    展示如何將語音轉換為文字
    """
    print("\n" + "=" * 50)
    print("範例 4: 語音轉文字")
    print("=" * 50)

    client = DifyMultimodalClient(
        api_key=DIFY_API_KEY,
        base_url=DIFY_BASE_URL
    )

    print("模擬語音轉文字...")

    try:
        # 轉換語音
        # result = client.audio_to_text(
        #     audio_file_path="path/to/audio.mp3",
        #     user="user-001"
        # )
        # print(f"識別結果: {result.get('text', '')}")

        print("（模擬）識別結果: 這是一段測試語音內容")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")


def example_image_processing():
    """
    範例 5: 圖片預處理

    展示如何預處理圖片
    """
    print("\n" + "=" * 50)
    print("範例 5: 圖片預處理")
    print("=" * 50)

    processor = ImageProcessor()

    # 模擬圖片信息
    print("模擬圖片處理:")
    print("  原始尺寸: 4000 x 3000")
    print("  調整後尺寸: 1024 x 768")
    print("  原始大小: 5.2 MB")
    print("  壓縮後大小: 0.8 MB")


def example_batch_image_analysis():
    """
    範例 6: 批量圖片分析

    展示如何批量分析多張圖片
    """
    print("\n" + "=" * 50)
    print("範例 6: 批量圖片分析")
    print("=" * 50)

    # 模擬批量處理
    images = [
        {"name": "image1.jpg", "url": "https://example.com/1.jpg"},
        {"name": "image2.jpg", "url": "https://example.com/2.jpg"},
        {"name": "image3.jpg", "url": "https://example.com/3.jpg"},
    ]

    print("批量分析圖片:")
    for img in images:
        print(f"\n處理: {img['name']}")
        print(f"  URL: {img['url']}")
        print(f"  分析結果: （模擬）包含自然風景")


def example_multimodal_conversation():
    """
    範例 7: 多模態對話

    展示如何在對話中處理多種模態
    """
    print("\n" + "=" * 50)
    print("範例 7: 多模態對話")
    print("=" * 50)

    print("多模態對話流程:")
    print("  1. 用戶上傳圖片")
    print("  2. AI 描述圖片內容")
    print("  3. 用戶詢問圖片細節")
    print("  4. AI 回答問題")
    print("  5. 用戶請求生成語音")
    print("  6. AI 生成語音回覆")

    # 模擬對話
    conversation = [
        {"role": "user", "content": "[上傳圖片]", "type": "image"},
        {"role": "assistant", "content": "這是一張美麗的風景照片，顯示了..."},
        {"role": "user", "content": "圖片中有多少棵樹？"},
        {"role": "assistant", "content": "根據我的分析，圖片中大約有5-6棵大樹..."},
        {"role": "user", "content": "請用語音總結一下"},
        {"role": "assistant", "content": "[生成語音]", "type": "audio"},
    ]

    print("\n對話記錄:")
    for msg in conversation:
        role = "用戶" if msg['role'] == 'user' else "助手"
        print(f"  {role}: {msg['content']}")


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    print("Dify 多模態處理範例")
    print("請確保已設置 DIFY_API_KEY 環境變數")
    print()

    example_upload_and_chat()
    example_image_analysis()
    example_text_to_speech()
    example_speech_to_text()
    example_image_processing()
    example_batch_image_analysis()
    example_multimodal_conversation()
