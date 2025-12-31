"""
Aider 語音編程功能
==================

本範例展示 Aider 的語音編程功能，包括：
- 語音輸入設置
- 語音命令
- 多語言支援
- 語音轉文字
- 文字轉語音回饋

作者：AI Agent Demo
日期：2025-12-31
"""

import os
from typing import Optional, List, Dict, Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import json


class VoiceLanguage(Enum):
    """支援的語音語言"""
    ENGLISH = "en-US"
    CHINESE_TW = "zh-TW"
    CHINESE_CN = "zh-CN"
    JAPANESE = "ja-JP"
    KOREAN = "ko-KR"
    SPANISH = "es-ES"
    FRENCH = "fr-FR"
    GERMAN = "de-DE"


class VoiceCommand(Enum):
    """語音命令類型"""
    CODE = "code"              # 編碼命令
    NAVIGATE = "navigate"      # 導航命令
    REFACTOR = "refactor"      # 重構命令
    TEST = "test"             # 測試命令
    GIT = "git"               # Git 命令
    SYSTEM = "system"         # 系統命令


@dataclass
class VoiceConfig:
    """
    語音配置

    管理語音輸入和輸出的各種設置。
    """
    language: VoiceLanguage = VoiceLanguage.ENGLISH
    enable_input: bool = True
    enable_output: bool = False
    voice_speed: float = 1.0  # 語音速度 0.5-2.0
    voice_pitch: float = 1.0  # 語音音調 0.5-2.0
    auto_punctuation: bool = True
    noise_suppression: bool = True

    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            "language": self.language.value,
            "enable_input": self.enable_input,
            "enable_output": self.enable_output,
            "voice_speed": self.voice_speed,
            "voice_pitch": self.voice_pitch,
            "auto_punctuation": self.auto_punctuation,
            "noise_suppression": self.noise_suppression
        }


class AiderVoiceProgramming:
    """
    Aider 語音編程類

    提供語音編程的各種功能和示例。
    """

    def __init__(self, config: Optional[VoiceConfig] = None):
        """
        初始化語音編程

        Args:
            config: 語音配置，如果為 None 則使用默認配置
        """
        self.config = config or VoiceConfig()
        self.command_history: List[str] = []

    @staticmethod
    def setup_voice_mode():
        """
        設置語音模式

        展示如何啟用和配置 Aider 的語音功能。
        """
        print("\n" + "=" * 60)
        print("設置 Aider 語音模式")
        print("=" * 60)

        print("""
## 1. 安裝語音依賴

首先需要安裝語音功能的額外依賴：

```bash
# 安裝完整的語音功能
pip install aider-chat[voice]

# 或單獨安裝依賴
pip install SpeechRecognition
pip install pyttsx3
pip install pyaudio
```

## 2. 啟動語音模式

### 基本啟動

```bash
# 使用英語語音
aider --voice-language en-US

# 使用繁體中文語音
aider --voice-language zh-TW

# 使用簡體中文語音
aider --voice-language zh-CN
```

### 進階配置

```bash
# 同時啟用語音輸入和輸出
aider --voice-language zh-TW --voice-output

# 調整語音速度（0.5-2.0）
aider --voice-language zh-TW --voice-speed 1.2

# 配置降噪
aider --voice-language zh-TW --noise-suppression
```

## 3. 語音配置文件

創建 `.aider.voice.yml` 配置文件：

```yaml
# 語音配置
voice:
  # 語言設置
  language: zh-TW

  # 啟用語音輸入
  input: true

  # 啟用語音輸出（可選）
  output: false

  # 語音速度 (0.5-2.0)
  speed: 1.0

  # 語音音調 (0.5-2.0)
  pitch: 1.0

  # 自動標點符號
  auto_punctuation: true

  # 降噪
  noise_suppression: true

  # 喚醒詞（可選）
  wake_word: "嘿 Aider"
```

## 4. 測試語音輸入

啟動後測試語音是否正常工作：

```bash
$ aider --voice-language zh-TW

🎤 語音模式已啟用 (zh-TW)
🎤 開始說話...

> [語音輸入] 請在主文件中添加一個函數

# Aider 會將語音轉換為文字並執行
```

## 5. 常見問題排除

### 麥克風無法使用

```bash
# 檢查麥克風權限
# macOS: 系統偏好設定 > 安全性與隱私 > 麥克風
# Linux: 檢查 ALSA 或 PulseAudio 設置
# Windows: 設定 > 隱私 > 麥克風

# 測試麥克風
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
```

### 語音識別不準確

```bash
# 使用降噪
aider --voice-language zh-TW --noise-suppression

# 在安靜環境中使用
# 使用高品質麥克風
# 清晰地說話
```

### 切換語音引擎

```bash
# 使用 Google 語音識別（需要網路）
aider --voice-language zh-TW --voice-engine google

# 使用離線語音識別
aider --voice-language zh-TW --voice-engine sphinx
```
        """)

    @staticmethod
    def demonstrate_voice_commands():
        """
        展示常用語音命令

        各種編程任務的語音命令示例。
        """
        print("\n" + "=" * 60)
        print("常用語音命令")
        print("=" * 60)

        print("""
## 1. 基本編程命令

### 創建函數

**語音**：
> 請在 utils.py 中創建一個計算兩個數字之和的函數

**Aider 執行**：
```python
# utils.py
def add_numbers(a: int, b: int) -> int:
    \"\"\"
    計算兩個數字之和

    Args:
        a: 第一個數字
        b: 第二個數字

    Returns:
        兩數之和
    \"\"\"
    return a + b
```

### 修改函數

**語音**：
> 請修改 add_numbers 函數，添加參數驗證

**Aider 執行**：
```python
def add_numbers(a: int, b: int) -> int:
    \"\"\"計算兩個數字之和\"\"\"
    if not isinstance(a, (int, float)):
        raise TypeError("a 必須是數字")
    if not isinstance(b, (int, float)):
        raise TypeError("b 必須是數字")

    return a + b
```

### 添加註釋

**語音**：
> 請為這個函數添加詳細的註釋

## 2. 類操作命令

### 創建類

**語音**：
> 在 models.py 中創建一個 User 類，包含 username 和 email 屬性

**Aider 執行**：
```python
# models.py
class User:
    \"\"\"用戶類\"\"\"

    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email

    def __str__(self) -> str:
        return f"User({self.username}, {self.email})"
```

### 添加方法

**語音**：
> 給 User 類添加一個驗證郵箱格式的方法

## 3. 重構命令

### 提取方法

**語音**：
> 請將這段代碼提取為一個獨立的方法

### 重命名

**語音**：
> 把 process_data 函數重命名為 transform_data

### 拆分類

**語音**：
> 這個類太大了，請拆分為多個小類

## 4. 測試命令

### 生成測試

**語音**：
> 為 add_numbers 函數生成單元測試

### 運行測試

**語音**：
> 運行測試

**對應命令**：
```bash
/test
```

## 5. Git 命令

### 查看狀態

**語音**：
> 顯示 Git 狀態

**對應命令**：
```bash
/git status
```

### 提交變更

**語音**：
> 提交這些變更，訊息是：添加用戶驗證功能

**對應命令**：
```bash
/commit 添加用戶驗證功能
```

### 查看差異

**語音**：
> 顯示變更的差異

**對應命令**：
```bash
/diff
```

## 6. 導航命令

### 添加文件

**語音**：
> 添加 models.py 到會話中

**對應命令**：
```bash
/add models.py
```

### 移除文件

**語音**：
> 從會話中移除 models.py

**對應命令**：
```bash
/drop models.py
```

### 列出文件

**語音**：
> 列出當前會話中的所有文件

**對應命令**：
```bash
/ls
```

## 7. 複雜任務命令

### API 開發

**語音**：
> 創建一個 RESTful API 端點，用於獲取用戶列表。
> 包含路由、控制器和數據庫查詢。

### 錯誤修復

**語音**：
> 這裡有一個錯誤，當輸入為空時程式會崩潰。
> 請添加適當的錯誤處理。

### 性能優化

**語音**：
> 這個函數執行很慢，請優化它的性能。
> 可以考慮使用緩存或更高效的算法。
        """)

    @staticmethod
    def demonstrate_multilingual():
        """
        展示多語言支援

        不同語言的語音命令示例。
        """
        print("\n" + "=" * 60)
        print("多語言語音編程")
        print("=" * 60)

        print("""
## 繁體中文 (zh-TW)

```bash
$ aider --voice-language zh-TW

🎤 > 請在主文件中添加一個函數
🎤 > 重構這個類以遵循單一職責原則
🎤 > 為這個函數生成測試
🎤 > 提交變更
```

## 簡體中文 (zh-CN)

```bash
$ aider --voice-language zh-CN

🎤 > 请在主文件中添加一个函数
🎤 > 重构这个类以遵循单一职责原则
🎤 > 为这个函数生成测试
🎤 > 提交更改
```

## 英語 (en-US)

```bash
$ aider --voice-language en-US

🎤 > Add a function to the main file
🎤 > Refactor this class to follow single responsibility principle
🎤 > Generate tests for this function
🎤 > Commit the changes
```

## 日語 (ja-JP)

```bash
$ aider --voice-language ja-JP

🎤 > メインファイルに関数を追加してください
🎤 > このクラスを単一責任の原則に従ってリファクタリングしてください
🎤 > この関数のテストを生成してください
```

## 韓語 (ko-KR)

```bash
$ aider --voice-language ko-KR

🎤 > 메인 파일에 함수를 추가해주세요
🎤 > 이 클래스를 단일 책임 원칙에 따라 리팩토링해주세요
🎤 > 이 함수에 대한 테스트를 생성해주세요
```

## 語言切換

在會話中切換語言：

```bash
> /voice-language zh-TW  # 切換到繁體中文
> /voice-language en-US  # 切換到英語
```
        """)

    @staticmethod
    def demonstrate_voice_workflow():
        """
        展示完整的語音編程工作流程

        從開始到結束的語音編程示例。
        """
        print("\n" + "=" * 60)
        print("語音編程工作流程示例")
        print("=" * 60)

        print("""
## 場景：使用語音開發一個用戶註冊功能

### 步驟 1: 啟動語音模式

```bash
$ aider --voice-language zh-TW src/
🎤 語音模式已啟用
```

### 步驟 2: 創建模型

**語音輸入**：
> 在 models.py 中創建一個 User 類，
> 包含 id、username、email 和 password 欄位

**Aider 回應**：
```
✓ 已在 models.py 中創建 User 類
```

### 步驟 3: 創建驗證器

**語音輸入**：
> 創建一個 validator.py 文件，
> 實現用戶名和郵箱的驗證函數

**Aider 回應**：
```
✓ 已創建 validator.py
✓ 實現了 validate_username 和 validate_email 函數
```

### 步驟 4: 創建註冊邏輯

**語音輸入**：
> 在 auth.py 中創建 register_user 函數，
> 使用 validator 驗證輸入，
> 然後創建 User 對象並保存到資料庫

**Aider 回應**：
```
✓ 已創建 auth.py
✓ 實現了 register_user 函數
✓ 集成了驗證器
```

### 步驟 5: 生成測試

**語音輸入**：
> 為 register_user 函數生成全面的測試

**Aider 回應**：
```
✓ 已創建 tests/test_auth.py
✓ 包含 15 個測試案例
```

### 步驟 6: 運行測試

**語音輸入**：
> 運行測試

**Aider 執行**：
```bash
$ pytest tests/test_auth.py
✓ 15 passed in 0.5s
```

### 步驟 7: 查看變更

**語音輸入**：
> 顯示所有變更

**Aider 執行**：
```bash
/diff
```

### 步驟 8: 提交

**語音輸入**：
> 提交這些變更，訊息是：實現用戶註冊功能

**Aider 執行**：
```bash
git add .
git commit -m "aider: 實現用戶註冊功能"
✓ 已提交
```

## 整個流程用時

- 語音輸入：約 3-5 分鐘
- AI 生成代碼：約 2-3 分鐘
- 總計：約 5-8 分鐘

對比手動編寫：通常需要 30-60 分鐘
        """)

    @staticmethod
    def demonstrate_voice_tips():
        """
        語音編程技巧和最佳實踐
        """
        print("\n" + "=" * 60)
        print("語音編程技巧")
        print("=" * 60)

        print("""
## 1. 清晰表達

### ✓ 好的語音命令

- "在 models.py 中創建一個 User 類"
- "為 calculate_total 函數添加錯誤處理"
- "重構這個方法，將其拆分為三個小方法"

### ✗ 不好的語音命令

- "改一下那個"（不具體）
- "加個東西"（太模糊）
- "嗯...那個...就是..."（太多停頓）

## 2. 分步驟執行

複雜任務分解為多個小步驟：

**步驟 1**：
> 創建基本的 User 類

**步驟 2**：
> 添加驗證方法

**步驟 3**：
> 添加資料庫操作方法

## 3. 使用技術術語

準確使用編程術語：

- "方法" (method) 而不是 "功能"
- "類" (class) 而不是 "物件"
- "參數" (parameter) 而不是 "輸入"
- "返回值" (return value) 而不是 "輸出"

## 4. 指定文件和位置

明確指出要修改的文件和位置：

> 在 src/models.py 的 User 類中添加 validate_email 方法

而不是：

> 添加一個驗證方法

## 5. 環境設置

### 安靜環境

- 選擇安靜的工作環境
- 使用降噪麥克風
- 關閉背景音樂

### 麥克風位置

- 距離嘴巴 10-15 cm
- 避免對著麥克風呼吸
- 保持一致的距離

### 說話方式

- 正常語速（不要太快或太慢）
- 清晰發音
- 適當的停頓

## 6. 語音快捷方式

設置常用命令的快捷語音：

```yaml
# .aider.voice.yml
shortcuts:
  "運行測試": "/test"
  "顯示差異": "/diff"
  "提交變更": "/commit"
  "撤銷": "/undo"
```

## 7. 錯誤修正

如果 Aider 誤解了命令：

**方法 1: 重新表達**
> 不對，我的意思是...

**方法 2: 使用撤銷**
> 撤銷上一個操作

**方法 3: 切換到文字輸入**
按 Ctrl+T 切換到文字模式

## 8. 混合模式

結合語音和鍵盤：

- 語音：大段的指令和描述
- 鍵盤：精確的命令和符號

```bash
# 語音輸入複雜需求
🎤 > 創建一個處理用戶認證的類...

# 鍵盤輸入精確命令
⌨️  > /commit
```

## 9. 上下文管理

在語音命令中提供足夠的上下文：

> 在我們剛剛創建的 User 類中，
> 添加一個 is_active 屬性，默認值為 True

## 10. 定期休息

語音編程可能比打字更累：

- 每 30 分鐘休息 5 分鐘
- 喝水潤喉
- 避免長時間連續使用
        """)

    def generate_voice_config(self, output_path: Path) -> None:
        """
        生成語音配置文件

        Args:
            output_path: 輸出路徑
        """
        config_content = f"""# Aider 語音配置文件
# Voice Configuration for Aider

voice:
  # 語言設置 / Language Setting
  # 支援: en-US, zh-TW, zh-CN, ja-JP, ko-KR, es-ES, fr-FR, de-DE
  language: {self.config.language.value}

  # 啟用語音輸入 / Enable Voice Input
  input: {str(self.config.enable_input).lower()}

  # 啟用語音輸出 / Enable Voice Output
  output: {str(self.config.enable_output).lower()}

  # 語音速度 / Voice Speed (0.5 - 2.0)
  speed: {self.config.voice_speed}

  # 語音音調 / Voice Pitch (0.5 - 2.0)
  pitch: {self.config.voice_pitch}

  # 自動標點符號 / Auto Punctuation
  auto_punctuation: {str(self.config.auto_punctuation).lower()}

  # 降噪 / Noise Suppression
  noise_suppression: {str(self.config.noise_suppression).lower()}

  # 語音快捷方式 / Voice Shortcuts
  shortcuts:
    "運行測試": "/test"
    "顯示差異": "/diff"
    "查看狀態": "/git status"
    "提交變更": "/commit"
    "撤銷": "/undo"
    "列出文件": "/ls"
    "幫助": "/help"

  # 喚醒詞（可選）/ Wake Word (Optional)
  # wake_word: "嘿 Aider"
"""

        output_path.write_text(config_content, encoding='utf-8')
        print(f"✓ 語音配置已保存到: {output_path}")


def main():
    """
    主函數

    運行語音編程演示。
    """
    print("=" * 60)
    print("Aider 語音編程功能")
    print("=" * 60)

    voice = AiderVoiceProgramming()

    # 演示各種功能
    voice.setup_voice_mode()
    voice.demonstrate_voice_commands()
    voice.demonstrate_multilingual()
    voice.demonstrate_voice_workflow()
    voice.demonstrate_voice_tips()

    # 生成配置文件
    config_path = Path(".aider.voice.yml")
    voice.generate_voice_config(config_path)

    print("\n" + "=" * 60)
    print("語音編程總結")
    print("=" * 60)

    print("""
語音編程的優勢：
✓ 解放雙手
✓ 更自然的交互方式
✓ 適合快速原型開發
✓ 減少重複性勞動
✓ 提高開發效率

適用場景：
✓ 創建新功能
✓ 代碼重構
✓ 生成測試
✓ 文檔編寫
✓ 代碼審查

注意事項：
! 需要安靜的環境
! 需要清晰的表達
! 可能需要適應期
! 複雜邏輯建議使用鍵盤
    """)


if __name__ == "__main__":
    main()
