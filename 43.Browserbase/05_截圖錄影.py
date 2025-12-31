"""
Browserbase 截圖錄影示例
========================

本模塊展示了如何使用 Browserbase 進行截圖和視頻錄製。
包括全頁截圖、元素截圖、視頻錄製、截圖對比等功能。

主要內容:
1. 基礎截圖功能
2. 全頁面截圖
3. 元素截圖
4. 視頻錄製
5. 截圖對比
6. 自動化截圖工作流

作者: Browserbase 示例團隊
日期: 2025-12-31
"""

import os
import io
import time
import json
import base64
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum
from PIL import Image, ImageDraw, ImageFont, ImageChops
from dotenv import load_dotenv


# 加載環境變量
load_dotenv()


class ScreenshotFormat(Enum):
    """截圖格式"""
    PNG = "png"
    JPEG = "jpeg"
    WEBP = "webp"


class VideoFormat(Enum):
    """視頻格式"""
    MP4 = "mp4"
    WEBM = "webm"


@dataclass
class ScreenshotOptions:
    """截圖選項"""
    format: ScreenshotFormat = ScreenshotFormat.PNG
    quality: int = 90  # JPEG/WEBP 質量 (0-100)
    full_page: bool = False
    clip: Optional[Dict[str, int]] = None  # 裁剪區域 {x, y, width, height}
    omit_background: bool = False  # 透明背景
    scale: float = 1.0  # 縮放比例

    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            "type": self.format.value,
            "quality": self.quality,
            "fullPage": self.full_page,
            "clip": self.clip,
            "omitBackground": self.omit_background,
            "scale": self.scale
        }


@dataclass
class VideoOptions:
    """視頻錄製選項"""
    format: VideoFormat = VideoFormat.MP4
    fps: int = 30
    quality: int = 90
    width: int = 1920
    height: int = 1080

    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            "format": self.format.value,
            "fps": self.fps,
            "quality": self.quality,
            "width": self.width,
            "height": self.height
        }


class ScreenshotManager:
    """
    截圖管理器

    提供豐富的截圖功能和管理。
    """

    def __init__(self, output_dir: str = "./screenshots"):
        """
        初始化截圖管理器

        Args:
            output_dir: 輸出目錄
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.screenshot_count = 0
        print(f"[ScreenshotManager] 初始化，輸出目錄: {self.output_dir}")

    def take_screenshot(
        self,
        page_title: str = "page",
        options: Optional[ScreenshotOptions] = None
    ) -> str:
        """
        截取屏幕截圖

        Args:
            page_title: 頁面標題（用於文件名）
            options: 截圖選項

        Returns:
            截圖文件路徑
        """
        if options is None:
            options = ScreenshotOptions()

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{page_title}_{timestamp}.{options.format.value}"
        filepath = self.output_dir / filename

        # 模擬截圖（實際應該調用瀏覽器 API）
        self._create_mock_screenshot(filepath, options)

        self.screenshot_count += 1
        print(f"[ScreenshotManager] 截圖已保存: {filepath}")

        return str(filepath)

    def take_element_screenshot(
        self,
        selector: str,
        page_title: str = "element",
        options: Optional[ScreenshotOptions] = None
    ) -> str:
        """
        截取元素截圖

        Args:
            selector: CSS 選擇器
            page_title: 頁面標題
            options: 截圖選項

        Returns:
            截圖文件路徑
        """
        if options is None:
            options = ScreenshotOptions()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{page_title}_element_{timestamp}.{options.format.value}"
        filepath = self.output_dir / filename

        print(f"[ScreenshotManager] 截取元素: {selector}")
        self._create_mock_screenshot(filepath, options, is_element=True)

        self.screenshot_count += 1
        print(f"[ScreenshotManager] 元素截圖已保存: {filepath}")

        return str(filepath)

    def take_full_page_screenshot(
        self,
        page_title: str = "fullpage",
        options: Optional[ScreenshotOptions] = None
    ) -> str:
        """
        截取全頁面截圖

        Args:
            page_title: 頁面標題
            options: 截圖選項

        Returns:
            截圖文件路徑
        """
        if options is None:
            options = ScreenshotOptions(full_page=True)
        else:
            options.full_page = True

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{page_title}_fullpage_{timestamp}.{options.format.value}"
        filepath = self.output_dir / filename

        print(f"[ScreenshotManager] 截取全頁面截圖...")
        self._create_mock_screenshot(filepath, options, is_full_page=True)

        self.screenshot_count += 1
        print(f"[ScreenshotManager] 全頁面截圖已保存: {filepath}")

        return str(filepath)

    def _create_mock_screenshot(
        self,
        filepath: Path,
        options: ScreenshotOptions,
        is_element: bool = False,
        is_full_page: bool = False
    ):
        """創建模擬截圖"""
        # 確定尺寸
        if is_element:
            width, height = 400, 300
        elif is_full_page:
            width, height = 1920, 3000
        else:
            width, height = 1920, 1080

        # 應用縮放
        if options.scale != 1.0:
            width = int(width * options.scale)
            height = int(height * options.scale)

        # 創建圖像
        if options.omit_background:
            img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        else:
            img = Image.new('RGB', (width, height), (240, 240, 240))

        # 添加一些示例內容
        draw = ImageDraw.Draw(img)

        # 繪製標題
        title_text = "Screenshot Mock"
        if is_element:
            title_text = "Element Screenshot"
        elif is_full_page:
            title_text = "Full Page Screenshot"

        draw.text((50, 50), title_text, fill=(0, 0, 0))

        # 繪製時間戳
        timestamp_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        draw.text((50, 100), timestamp_text, fill=(100, 100, 100))

        # 應用裁剪
        if options.clip:
            clip = options.clip
            img = img.crop((
                clip['x'],
                clip['y'],
                clip['x'] + clip['width'],
                clip['y'] + clip['height']
            ))

        # 保存
        if options.format == ScreenshotFormat.PNG:
            img.save(filepath, 'PNG')
        elif options.format == ScreenshotFormat.JPEG:
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            img.save(filepath, 'JPEG', quality=options.quality)
        elif options.format == ScreenshotFormat.WEBP:
            img.save(filepath, 'WEBP', quality=options.quality)

    def get_screenshot_metadata(self, filepath: str) -> Dict:
        """
        獲取截圖元數據

        Args:
            filepath: 截圖文件路徑

        Returns:
            元數據字典
        """
        path = Path(filepath)

        if not path.exists():
            return {}

        img = Image.open(path)
        file_size = path.stat().st_size

        return {
            "filename": path.name,
            "format": img.format,
            "size": f"{img.width}x{img.height}",
            "mode": img.mode,
            "file_size_kb": file_size / 1024,
            "created_at": datetime.fromtimestamp(path.stat().st_ctime).isoformat()
        }


class VideoRecorder:
    """
    視頻錄製器

    錄製瀏覽器操作過程。
    """

    def __init__(self, output_dir: str = "./recordings"):
        """
        初始化視頻錄製器

        Args:
            output_dir: 輸出目錄
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.is_recording = False
        self.current_recording = None
        print(f"[VideoRecorder] 初始化，輸出目錄: {self.output_dir}")

    def start_recording(
        self,
        session_name: str = "session",
        options: Optional[VideoOptions] = None
    ) -> str:
        """
        開始錄製

        Args:
            session_name: 會話名稱
            options: 視頻選項

        Returns:
            錄製 ID
        """
        if self.is_recording:
            print("[VideoRecorder] 警告: 已在錄製中")
            return self.current_recording

        if options is None:
            options = VideoOptions()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        recording_id = f"{session_name}_{timestamp}"
        self.current_recording = recording_id

        print(f"[VideoRecorder] 開始錄製: {recording_id}")
        print(f"  - 格式: {options.format.value}")
        print(f"  - FPS: {options.fps}")
        print(f"  - 解析度: {options.width}x{options.height}")

        self.is_recording = True
        self.recording_start_time = time.time()

        return recording_id

    def stop_recording(self) -> Optional[str]:
        """
        停止錄製

        Returns:
            視頻文件路徑
        """
        if not self.is_recording:
            print("[VideoRecorder] 警告: 沒有進行中的錄製")
            return None

        duration = time.time() - self.recording_start_time
        filename = f"{self.current_recording}.mp4"
        filepath = self.output_dir / filename

        # 模擬創建視頻文件
        self._create_mock_video(filepath, duration)

        print(f"[VideoRecorder] 停止錄製")
        print(f"  - 時長: {duration:.2f}秒")
        print(f"  - 文件: {filepath}")

        self.is_recording = False
        self.current_recording = None

        return str(filepath)

    def pause_recording(self):
        """暫停錄製"""
        if self.is_recording:
            print("[VideoRecorder] 暫停錄製")
            self.is_recording = False

    def resume_recording(self):
        """恢復錄製"""
        if not self.is_recording and self.current_recording:
            print("[VideoRecorder] 恢復錄製")
            self.is_recording = True

    def _create_mock_video(self, filepath: Path, duration: float):
        """創建模擬視頻文件"""
        # 創建一個簡單的文本文件模擬視頻
        with open(filepath, 'w') as f:
            f.write(f"Mock video file\n")
            f.write(f"Duration: {duration:.2f} seconds\n")
            f.write(f"Created at: {datetime.now()}\n")


class ScreenshotComparator:
    """
    截圖對比器

    對比兩張截圖的差異。
    """

    def __init__(self):
        """初始化對比器"""
        print("[ScreenshotComparator] 初始化完成")

    def compare_screenshots(
        self,
        image1_path: str,
        image2_path: str,
        output_path: Optional[str] = None
    ) -> Dict:
        """
        對比兩張截圖

        Args:
            image1_path: 第一張截圖路徑
            image2_path: 第二張截圖路徑
            output_path: 差異圖輸出路徑（可選）

        Returns:
            對比結果字典
        """
        print(f"[ScreenshotComparator] 對比截圖:")
        print(f"  - 圖片1: {image1_path}")
        print(f"  - 圖片2: {image2_path}")

        try:
            img1 = Image.open(image1_path)
            img2 = Image.open(image2_path)

            # 檢查尺寸
            if img1.size != img2.size:
                print("  警告: 圖片尺寸不同，調整大小...")
                img2 = img2.resize(img1.size)

            # 轉換為相同模式
            if img1.mode != img2.mode:
                img2 = img2.convert(img1.mode)

            # 計算差異
            diff = ImageChops.difference(img1, img2)

            # 計算差異百分比
            diff_pixels = sum(sum(pixel) for pixel in diff.getdata())
            total_pixels = img1.size[0] * img1.size[1] * len(img1.getbands())
            diff_percentage = (diff_pixels / (total_pixels * 255)) * 100

            # 保存差異圖
            if output_path:
                # 增強差異顯示
                diff_enhanced = diff.point(lambda x: x * 10)
                diff_enhanced.save(output_path)
                print(f"  差異圖已保存: {output_path}")

            result = {
                "identical": diff_percentage < 0.01,
                "difference_percentage": diff_percentage,
                "image1_size": img1.size,
                "image2_size": img2.size,
                "diff_image": output_path
            }

            print(f"  差異百分比: {diff_percentage:.2f}%")

            return result

        except Exception as e:
            print(f"  錯誤: {str(e)}")
            return {"error": str(e)}

    def find_changed_regions(
        self,
        image1_path: str,
        image2_path: str,
        threshold: int = 30
    ) -> List[Dict]:
        """
        查找變化的區域

        Args:
            image1_path: 第一張截圖路徑
            image2_path: 第二張截圖路徑
            threshold: 差異閾值

        Returns:
            變化區域列表
        """
        print(f"[ScreenshotComparator] 查找變化區域 (閾值: {threshold})")

        # 模擬查找結果
        regions = [
            {"x": 100, "y": 200, "width": 300, "height": 150, "diff": 45.2},
            {"x": 500, "y": 600, "width": 200, "height": 100, "diff": 32.1},
        ]

        print(f"  找到 {len(regions)} 個變化區域")
        for i, region in enumerate(regions, 1):
            print(f"  區域{i}: ({region['x']}, {region['y']}) "
                  f"{region['width']}x{region['height']} "
                  f"差異: {region['diff']:.1f}%")

        return regions


class ScreenshotWorkflow:
    """
    截圖工作流

    自動化截圖任務的執行。
    """

    def __init__(self, screenshot_manager: ScreenshotManager):
        """
        初始化工作流

        Args:
            screenshot_manager: 截圖管理器
        """
        self.screenshot_manager = screenshot_manager
        self.workflow_steps: List[Dict] = []
        print("[ScreenshotWorkflow] 初始化完成")

    def add_step(
        self,
        name: str,
        action: str,
        delay: float = 0.0,
        screenshot: bool = True,
        **kwargs
    ):
        """
        添加工作流步驟

        Args:
            name: 步驟名稱
            action: 動作類型
            delay: 延遲時間（秒）
            screenshot: 是否截圖
            **kwargs: 其他參數
        """
        step = {
            "name": name,
            "action": action,
            "delay": delay,
            "screenshot": screenshot,
            **kwargs
        }
        self.workflow_steps.append(step)
        print(f"[ScreenshotWorkflow] 添加步驟: {name} ({action})")

    def execute(self) -> List[str]:
        """
        執行工作流

        Returns:
            截圖文件路徑列表
        """
        print("\n" + "=" * 50)
        print("[ScreenshotWorkflow] 開始執行工作流")
        print("=" * 50)

        screenshots = []

        for i, step in enumerate(self.workflow_steps, 1):
            print(f"\n步驟 {i}/{len(self.workflow_steps)}: {step['name']}")

            # 執行延遲
            if step['delay'] > 0:
                print(f"  等待 {step['delay']}秒...")
                time.sleep(step['delay'])

            # 執行動作
            self._execute_action(step)

            # 截圖
            if step['screenshot']:
                screenshot_path = self.screenshot_manager.take_screenshot(
                    page_title=step['name'].replace(' ', '_')
                )
                screenshots.append(screenshot_path)

        print("\n" + "=" * 50)
        print(f"[ScreenshotWorkflow] 工作流完成，共 {len(screenshots)} 張截圖")
        print("=" * 50 + "\n")

        return screenshots

    def _execute_action(self, step: Dict):
        """執行動作"""
        action = step['action']
        print(f"  執行動作: {action}")

        # 這裡應該實現真實的瀏覽器操作
        # 現在只是模擬
        if action == "navigate":
            print(f"    導航到: {step.get('url', 'unknown')}")
        elif action == "click":
            print(f"    點擊: {step.get('selector', 'unknown')}")
        elif action == "type":
            print(f"    輸入: {step.get('text', 'unknown')}")
        elif action == "scroll":
            print(f"    滾動: {step.get('distance', 0)}px")


def example_basic_screenshot():
    """示例1: 基礎截圖"""
    print("\n" + "=" * 60)
    print("示例1: 基礎截圖功能")
    print("=" * 60 + "\n")

    manager = ScreenshotManager(output_dir="./screenshots/example1")

    # 普通截圖
    print("1. 普通截圖:")
    path1 = manager.take_screenshot("homepage")

    # 高質量 JPEG
    print("\n2. 高質量 JPEG:")
    options = ScreenshotOptions(format=ScreenshotFormat.JPEG, quality=95)
    path2 = manager.take_screenshot("homepage_hq", options)

    # 縮放截圖
    print("\n3. 縮放截圖 (50%):")
    options = ScreenshotOptions(scale=0.5)
    path3 = manager.take_screenshot("homepage_small", options)

    print(f"\n總共截取了 {manager.screenshot_count} 張截圖")


def example_full_page_screenshot():
    """示例2: 全頁面截圖"""
    print("\n" + "=" * 60)
    print("示例2: 全頁面截圖")
    print("=" * 60 + "\n")

    manager = ScreenshotManager(output_dir="./screenshots/example2")

    # 全頁面截圖
    path = manager.take_full_page_screenshot("article_page")

    # 獲取元數據
    metadata = manager.get_screenshot_metadata(path)
    print("\n截圖元數據:")
    for key, value in metadata.items():
        print(f"  - {key}: {value}")


def example_element_screenshot():
    """示例3: 元素截圖"""
    print("\n" + "=" * 60)
    print("示例3: 元素截圖")
    print("=" * 60 + "\n")

    manager = ScreenshotManager(output_dir="./screenshots/example3")

    # 截取不同元素
    elements = [
        ("#header", "header"),
        (".content", "content"),
        ("#footer", "footer"),
    ]

    for selector, name in elements:
        manager.take_element_screenshot(selector, name)


def example_video_recording():
    """示例4: 視頻錄製"""
    print("\n" + "=" * 60)
    print("示例4: 視頻錄製")
    print("=" * 60 + "\n")

    recorder = VideoRecorder(output_dir="./recordings/example4")

    # 開始錄製
    recording_id = recorder.start_recording("test_session")

    # 模擬一些操作
    print("\n執行操作...")
    for i in range(3):
        print(f"  操作 {i + 1}")
        time.sleep(0.5)

    # 停止錄製
    video_path = recorder.stop_recording()
    print(f"\n視頻已保存: {video_path}")


def example_screenshot_comparison():
    """示例5: 截圖對比"""
    print("\n" + "=" * 60)
    print("示例5: 截圖對比")
    print("=" * 60 + "\n")

    manager = ScreenshotManager(output_dir="./screenshots/example5")
    comparator = ScreenshotComparator()

    # 創建兩張截圖
    print("創建測試截圖...")
    path1 = manager.take_screenshot("before")
    time.sleep(0.1)
    path2 = manager.take_screenshot("after")

    # 對比截圖
    print("\n對比截圖:")
    diff_path = "./screenshots/example5/diff.png"
    result = comparator.compare_screenshots(path1, path2, diff_path)

    print("\n對比結果:")
    for key, value in result.items():
        if key != "diff_image":
            print(f"  - {key}: {value}")


def example_automated_workflow():
    """示例6: 自動化工作流"""
    print("\n" + "=" * 60)
    print("示例6: 自動化截圖工作流")
    print("=" * 60 + "\n")

    manager = ScreenshotManager(output_dir="./screenshots/example6")
    workflow = ScreenshotWorkflow(manager)

    # 定義工作流
    workflow.add_step("打開首頁", "navigate", url="https://example.com", delay=1.0)
    workflow.add_step("點擊登錄", "click", selector="#login", delay=0.5)
    workflow.add_step("輸入用戶名", "type", selector="#username", text="user@example.com", delay=0.5)
    workflow.add_step("輸入密碼", "type", selector="#password", text="password", delay=0.5)
    workflow.add_step("提交表單", "click", selector="#submit", delay=1.0)
    workflow.add_step("查看儀表板", "navigate", url="https://example.com/dashboard", delay=1.0)

    # 執行工作流
    screenshots = workflow.execute()

    print(f"\n工作流生成了 {len(screenshots)} 張截圖:")
    for i, path in enumerate(screenshots, 1):
        print(f"  {i}. {path}")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Browserbase 截圖錄影示例")
    print("=" * 60)

    # 運行所有示例
    example_basic_screenshot()
    example_full_page_screenshot()
    example_element_screenshot()
    example_video_recording()
    example_screenshot_comparison()
    example_automated_workflow()

    print("\n" + "=" * 60)
    print("所有示例完成！")
    print("=" * 60 + "\n")

    print("提示:")
    print("- PNG 適合需要透明背景的場景")
    print("- JPEG 文件更小，適合存檔")
    print("- 使用全頁面截圖可以捕獲長頁面")
    print("- 視頻錄製適合記錄完整操作流程")
    print("- 截圖對比可用於視覺回歸測試")


if __name__ == "__main__":
    main()
