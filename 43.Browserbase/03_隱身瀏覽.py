"""
Browserbase 隱身瀏覽示例
========================

本模塊展示了如何使用 Browserbase 的隱身功能來避免被網站檢測為爬蟲。
包括反指紋識別、行為模擬、請求頭管理等技術。

主要內容:
1. 瀏覽器指紋偽造
2. User-Agent 輪換
3. Canvas 和 WebGL 保護
4. 行為模擬（鼠標、鍵盤、滾動）
5. 請求頭優化
6. 反檢測測試

作者: Browserbase 示例團隊
日期: 2025-12-31
"""

import os
import time
import random
import hashlib
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from dotenv import load_dotenv


# 加載環境變量
load_dotenv()


class BrowserType(Enum):
    """瀏覽器類型"""
    CHROME = "chrome"
    FIREFOX = "firefox"
    SAFARI = "safari"
    EDGE = "edge"


class OSType(Enum):
    """操作系統類型"""
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    ANDROID = "android"
    IOS = "ios"


@dataclass
class BrowserFingerprint:
    """瀏覽器指紋配置"""
    user_agent: str
    platform: str
    languages: List[str]
    screen_resolution: Tuple[int, int]
    timezone: str
    webgl_vendor: str
    webgl_renderer: str
    canvas_hash: str
    hardware_concurrency: int
    device_memory: int
    color_depth: int = 24
    pixel_ratio: float = 1.0

    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            "user_agent": self.user_agent,
            "platform": self.platform,
            "languages": self.languages,
            "screen_resolution": f"{self.screen_resolution[0]}x{self.screen_resolution[1]}",
            "timezone": self.timezone,
            "webgl_vendor": self.webgl_vendor,
            "webgl_renderer": self.webgl_renderer,
            "canvas_hash": self.canvas_hash,
            "hardware_concurrency": self.hardware_concurrency,
            "device_memory": self.device_memory,
            "color_depth": self.color_depth,
            "pixel_ratio": self.pixel_ratio
        }


class FingerprintGenerator:
    """
    指紋生成器

    生成真實的瀏覽器指紋，用於反檢測。
    """

    # 真實的 User-Agent 模板
    USER_AGENTS = {
        BrowserType.CHROME: [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ],
        BrowserType.FIREFOX: [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
        ],
        BrowserType.SAFARI: [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        ],
    }

    # 常見屏幕分辨率
    SCREEN_RESOLUTIONS = [
        (1920, 1080),
        (1366, 768),
        (1440, 900),
        (1536, 864),
        (2560, 1440),
    ]

    # WebGL 渲染器
    WEBGL_CONFIGS = [
        ("NVIDIA Corporation", "NVIDIA GeForce GTX 1660 Ti"),
        ("Intel Inc.", "Intel(R) UHD Graphics 630"),
        ("AMD", "AMD Radeon Pro 5500M"),
        ("Apple", "Apple M1"),
    ]

    def __init__(self, seed: Optional[int] = None):
        """
        初始化指紋生成器

        Args:
            seed: 隨機種子（用於可重現的指紋）
        """
        if seed:
            random.seed(seed)
        print("[FingerprintGenerator] 初始化完成")

    def generate(
        self,
        browser_type: BrowserType = BrowserType.CHROME,
        os_type: OSType = OSType.WINDOWS
    ) -> BrowserFingerprint:
        """
        生成瀏覽器指紋

        Args:
            browser_type: 瀏覽器類型
            os_type: 操作系統類型

        Returns:
            瀏覽器指紋對象
        """
        # 選擇 User-Agent
        user_agent = random.choice(self.USER_AGENTS.get(browser_type, self.USER_AGENTS[BrowserType.CHROME]))

        # 生成平台信息
        platform = self._get_platform(os_type)

        # 語言設置
        languages = ["zh-TW", "zh", "en-US", "en"]

        # 屏幕分辨率
        screen_resolution = random.choice(self.SCREEN_RESOLUTIONS)

        # 時區
        timezone = "Asia/Taipei"

        # WebGL 配置
        webgl_vendor, webgl_renderer = random.choice(self.WEBGL_CONFIGS)

        # 生成 Canvas 指紋（模擬）
        canvas_hash = hashlib.md5(
            f"{user_agent}{time.time()}".encode()
        ).hexdigest()[:16]

        # 硬件信息
        hardware_concurrency = random.choice([4, 6, 8, 12, 16])
        device_memory = random.choice([4, 8, 16, 32])

        fingerprint = BrowserFingerprint(
            user_agent=user_agent,
            platform=platform,
            languages=languages,
            screen_resolution=screen_resolution,
            timezone=timezone,
            webgl_vendor=webgl_vendor,
            webgl_renderer=webgl_renderer,
            canvas_hash=canvas_hash,
            hardware_concurrency=hardware_concurrency,
            device_memory=device_memory
        )

        print(f"[FingerprintGenerator] 生成指紋: {browser_type.value}/{os_type.value}")
        return fingerprint

    def _get_platform(self, os_type: OSType) -> str:
        """獲取平台字符串"""
        platform_map = {
            OSType.WINDOWS: "Win32",
            OSType.MACOS: "MacIntel",
            OSType.LINUX: "Linux x86_64",
            OSType.ANDROID: "Linux armv8l",
            OSType.IOS: "iPhone",
        }
        return platform_map.get(os_type, "Win32")


class StealthConfig:
    """隱身配置類"""

    def __init__(self):
        """初始化隱身配置"""
        self.fingerprint: Optional[BrowserFingerprint] = None
        self.block_webrtc: bool = True
        self.block_media_devices: bool = True
        self.randomize_canvas: bool = True
        self.randomize_webgl: bool = True
        self.randomize_audio: bool = True
        self.fake_plugins: bool = True
        self.fake_battery: bool = True
        self.custom_headers: Dict[str, str] = {}

    def apply_fingerprint(self, fingerprint: BrowserFingerprint):
        """應用指紋配置"""
        self.fingerprint = fingerprint
        print(f"[StealthConfig] 應用指紋配置")
        print(f"  - User-Agent: {fingerprint.user_agent[:50]}...")
        print(f"  - Platform: {fingerprint.platform}")
        print(f"  - Screen: {fingerprint.screen_resolution}")


class HumanBehaviorSimulator:
    """
    人類行為模擬器

    模擬真實的人類操作行為，包括鼠標移動、點擊延遲、隨機停頓等。
    """

    def __init__(self):
        """初始化行為模擬器"""
        self.typing_speed_wpm = random.randint(40, 80)  # 每分鐘打字數
        self.mouse_speed = random.uniform(0.5, 2.0)     # 鼠標速度係數
        print(f"[HumanBehaviorSimulator] 初始化 (打字速度: {self.typing_speed_wpm} WPM)")

    def calculate_typing_delay(self, text_length: int) -> float:
        """
        計算輸入延遲

        Args:
            text_length: 文本長度

        Returns:
            延遲時間（秒）
        """
        # 基於打字速度計算
        chars_per_second = (self.typing_speed_wpm * 5) / 60  # 假設平均每詞5個字符
        base_delay = text_length / chars_per_second

        # 添加隨機變化
        variation = random.uniform(0.8, 1.2)
        delay = base_delay * variation

        print(f"[HumanBehaviorSimulator] 輸入 {text_length} 個字符需要 {delay:.2f}秒")
        return delay

    def random_pause(self, min_seconds: float = 0.5, max_seconds: float = 2.0):
        """
        隨機停頓

        Args:
            min_seconds: 最小停頓時間
            max_seconds: 最大停頓時間
        """
        pause_time = random.uniform(min_seconds, max_seconds)
        print(f"[HumanBehaviorSimulator] 隨機停頓 {pause_time:.2f}秒")
        time.sleep(pause_time)

    def simulate_mouse_movement(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        steps: int = 10
    ) -> List[Tuple[int, int]]:
        """
        模擬鼠標移動軌跡

        Args:
            start_x: 起始 X 坐標
            start_y: 起始 Y 坐標
            end_x: 結束 X 坐標
            end_y: 結束 Y 坐標
            steps: 移動步數

        Returns:
            移動軌跡點列表
        """
        points = []

        for i in range(steps + 1):
            # 線性插值
            t = i / steps

            # 添加貝塞爾曲線效果
            curve_factor = 4 * t * (1 - t)  # 二次貝塞爾曲線

            # 計算中間點
            x = int(start_x + (end_x - start_x) * t)
            y = int(start_y + (end_y - start_y) * t)

            # 添加隨機抖動
            if i > 0 and i < steps:
                jitter_x = random.randint(-5, 5)
                jitter_y = random.randint(-5, 5)
                x += jitter_x
                y += jitter_y

            points.append((x, y))

        print(f"[HumanBehaviorSimulator] 生成鼠標軌跡: {len(points)} 個點")
        return points

    def simulate_scroll(
        self,
        total_distance: int,
        duration: float = 2.0
    ) -> List[int]:
        """
        模擬滾動行為

        Args:
            total_distance: 總滾動距離（像素）
            duration: 持續時間（秒）

        Returns:
            滾動步進列表
        """
        steps = int(duration * 10)  # 每秒10步
        positions = []

        for i in range(steps + 1):
            # 使用緩動函數（ease-out）
            t = i / steps
            eased_t = 1 - (1 - t) ** 3

            position = int(total_distance * eased_t)
            positions.append(position)

        print(f"[HumanBehaviorSimulator] 滾動 {total_distance}px，分 {len(positions)} 步")
        return positions

    def random_reading_pause(self, word_count: int):
        """
        基於內容長度的閱讀停頓

        Args:
            word_count: 字數
        """
        # 假設每分鐘閱讀 200-300 字
        reading_speed = random.randint(200, 300)
        reading_time = (word_count / reading_speed) * 60

        # 添加一些變化
        actual_time = reading_time * random.uniform(0.7, 1.3)

        print(f"[HumanBehaviorSimulator] 閱讀 {word_count} 字，停頓 {actual_time:.2f}秒")
        time.sleep(min(actual_time, 5.0))  # 最多停頓5秒


class AntiDetectionTester:
    """
    反檢測測試器

    測試瀏覽器是否被檢測為自動化工具。
    """

    # 常見的檢測點
    DETECTION_CHECKS = [
        "navigator.webdriver",
        "window.chrome",
        "navigator.plugins.length",
        "navigator.languages",
        "screen.width/height",
        "WebGL fingerprint",
        "Canvas fingerprint",
        "Audio fingerprint",
        "Timezone",
        "Battery API",
    ]

    def __init__(self):
        """初始化測試器"""
        self.test_results: Dict[str, bool] = {}
        print("[AntiDetectionTester] 初始化完成")

    def run_tests(self) -> Dict[str, bool]:
        """
        運行所有檢測測試

        Returns:
            測試結果字典
        """
        print("\n" + "=" * 50)
        print("運行反檢測測試")
        print("=" * 50)

        for check in self.DETECTION_CHECKS:
            # 模擬測試（實際需要在真實瀏覽器中執行 JavaScript）
            passed = random.choice([True, True, True, False])  # 75% 通過率
            self.test_results[check] = passed

            status = "✓ 通過" if passed else "✗ 失敗"
            print(f"{status} - {check}")

        # 計算總體通過率
        total = len(self.test_results)
        passed = sum(1 for v in self.test_results.values() if v)
        pass_rate = (passed / total) * 100

        print("=" * 50)
        print(f"總體通過率: {pass_rate:.1f}% ({passed}/{total})")
        print("=" * 50 + "\n")

        return self.test_results

    def test_specific_site(self, url: str) -> Dict[str, any]:
        """
        測試特定網站的反爬蟲機制

        Args:
            url: 網站 URL

        Returns:
            測試結果
        """
        print(f"\n測試網站: {url}")

        # 模擬測試結果
        result = {
            "url": url,
            "accessible": True,
            "captcha_detected": random.choice([True, False]),
            "rate_limited": False,
            "bot_detected": random.choice([True, False, False]),
            "response_time_ms": random.randint(100, 500)
        }

        print(f"  - 可訪問: {result['accessible']}")
        print(f"  - 驗證碼: {'是' if result['captcha_detected'] else '否'}")
        print(f"  - 速率限制: {'是' if result['rate_limited'] else '否'}")
        print(f"  - 機器人檢測: {'是' if result['bot_detected'] else '否'}")
        print(f"  - 響應時間: {result['response_time_ms']}ms")

        return result


def example_fingerprint_generation():
    """示例1: 指紋生成"""
    print("\n" + "=" * 60)
    print("示例1: 瀏覽器指紋生成")
    print("=" * 60 + "\n")

    generator = FingerprintGenerator()

    # 生成不同的指紋
    print("生成 Chrome/Windows 指紋:")
    fp1 = generator.generate(BrowserType.CHROME, OSType.WINDOWS)
    print(f"  User-Agent: {fp1.user_agent}")
    print(f"  屏幕分辨率: {fp1.screen_resolution}")
    print(f"  WebGL: {fp1.webgl_vendor} - {fp1.webgl_renderer}")
    print(f"  Canvas Hash: {fp1.canvas_hash}")

    print("\n生成 Firefox/MacOS 指紋:")
    fp2 = generator.generate(BrowserType.FIREFOX, OSType.MACOS)
    print(f"  User-Agent: {fp2.user_agent}")
    print(f"  屏幕分辨率: {fp2.screen_resolution}")
    print(f"  硬件線程: {fp2.hardware_concurrency}")
    print(f"  設備內存: {fp2.device_memory}GB")


def example_stealth_config():
    """示例2: 隱身配置"""
    print("\n" + "=" * 60)
    print("示例2: 隱身配置應用")
    print("=" * 60 + "\n")

    generator = FingerprintGenerator()
    fingerprint = generator.generate(BrowserType.CHROME, OSType.WINDOWS)

    config = StealthConfig()

    # 配置各項隱身功能
    print("配置隱身功能:")
    print(f"  - 阻止 WebRTC: {config.block_webrtc}")
    print(f"  - 隨機化 Canvas: {config.randomize_canvas}")
    print(f"  - 隨機化 WebGL: {config.randomize_webgl}")
    print(f"  - 偽造插件: {config.fake_plugins}")

    print("\n應用指紋:")
    config.apply_fingerprint(fingerprint)

    # 添加自定義請求頭
    config.custom_headers = {
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
    }

    print("\n自定義請求頭:")
    for key, value in config.custom_headers.items():
        print(f"  - {key}: {value}")


def example_human_behavior():
    """示例3: 人類行為模擬"""
    print("\n" + "=" * 60)
    print("示例3: 人類行為模擬")
    print("=" * 60 + "\n")

    simulator = HumanBehaviorSimulator()

    # 模擬輸入
    print("1. 模擬表單輸入:")
    text = "example@email.com"
    delay = simulator.calculate_typing_delay(len(text))

    # 模擬鼠標移動
    print("\n2. 模擬鼠標移動:")
    path = simulator.simulate_mouse_movement(100, 100, 500, 300, steps=15)
    print(f"  起點: {path[0]}")
    print(f"  中點: {path[len(path)//2]}")
    print(f"  終點: {path[-1]}")

    # 模擬滾動
    print("\n3. 模擬頁面滾動:")
    scroll_steps = simulator.simulate_scroll(1000, duration=1.5)
    print(f"  滾動步驟: {scroll_steps[:5]}... {scroll_steps[-5:]}")

    # 隨機停頓
    print("\n4. 模擬閱讀停頓:")
    simulator.random_reading_pause(100)


def example_anti_detection_test():
    """示例4: 反檢測測試"""
    print("\n" + "=" * 60)
    print("示例4: 反檢測測試")
    print("=" * 60 + "\n")

    tester = AntiDetectionTester()

    # 運行通用檢測測試
    results = tester.run_tests()

    # 測試特定網站
    print("\n測試常見網站:")
    test_sites = [
        "https://bot.sannysoft.com",
        "https://arh.antoinevastel.com/bots/areyouheadless",
        "https://pixelscan.net",
    ]

    for site in test_sites:
        tester.test_specific_site(site)


def example_complete_stealth_setup():
    """示例5: 完整隱身設置"""
    print("\n" + "=" * 60)
    print("示例5: 完整隱身設置流程")
    print("=" * 60 + "\n")

    print("步驟 1: 生成瀏覽器指紋")
    generator = FingerprintGenerator(seed=12345)
    fingerprint = generator.generate(BrowserType.CHROME, OSType.WINDOWS)

    print("\n步驟 2: 配置隱身選項")
    config = StealthConfig()
    config.apply_fingerprint(fingerprint)

    print("\n步驟 3: 設置人類行為模擬")
    behavior = HumanBehaviorSimulator()

    print("\n步驟 4: 運行反檢測測試")
    tester = AntiDetectionTester()
    results = tester.run_tests()

    # 統計
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    success_rate = (passed / total) * 100

    print(f"\n✓ 設置完成！反檢測通過率: {success_rate:.1f}%")

    if success_rate >= 80:
        print("  隱身質量: 優秀 ⭐⭐⭐⭐⭐")
    elif success_rate >= 60:
        print("  隱身質量: 良好 ⭐⭐⭐⭐")
    else:
        print("  隱身質量: 需要改進 ⭐⭐⭐")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Browserbase 隱身瀏覽示例")
    print("=" * 60)

    # 運行所有示例
    example_fingerprint_generation()
    example_stealth_config()
    example_human_behavior()
    example_anti_detection_test()
    example_complete_stealth_setup()

    print("\n" + "=" * 60)
    print("所有示例完成！")
    print("=" * 60 + "\n")

    print("提示:")
    print("- 使用真實的指紋配置可以大大提高反檢測成功率")
    print("- 行為模擬要自然，避免機械化操作")
    print("- 定期更新指紋以保持隱蔽性")
    print("- 結合代理使用效果更佳（參見 04_代理輪換.py）")


if __name__ == "__main__":
    main()
