"""
Marvin 語音功能示例

本示例展示：
1. 文字轉語音（TTS）
2. 語音轉文字（STT）
3. 語音參數配置
4. 多語言支持
5. 音頻處理

注意：
- 需要安裝 marvin[audio]
- 需要音頻文件進行測試

運行方式：
    python 07_語音功能.py
"""

import os
import marvin
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel


# ==================== 文字轉語音 ====================

def example_text_to_speech():
    """示例 1: 文字轉語音（TTS）"""
    print("\n" + "="*60)
    print("示例 1: 文字轉語音（TTS）")
    print("="*60)

    try:
        print("文字轉語音功能示例:")
        print("使用 marvin.speak() 將文字轉換為語音\n")

        print("基本用法:")
        print("""
        # 簡單的文字轉語音
        marvin.speak("你好，世界！", output="hello.mp3")
        print("✅ 語音文件已生成: hello.mp3")

        # 英文轉語音
        marvin.speak(
            "Hello, how are you today?",
            output="greeting.mp3"
        )

        # 長文本轉語音
        text = \"\"\"
        人工智能正在改變世界。從智能助手到自動駕駛，
        AI 技術已經滲透到我們生活的方方面面。
        \"\"\"
        marvin.speak(text, output="long_text.mp3")
        """)

        print("\n功能特點:")
        print("  🔊 自然語音合成")
        print("  🌍 多語言支持")
        print("  📝 長文本處理")
        print("  🎵 高質量音頻")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 語音轉文字 ====================

def example_speech_to_text():
    """示例 2: 語音轉文字（STT）"""
    print("\n" + "="*60)
    print("示例 2: 語音轉文字（STT）")
    print("="*60)

    try:
        print("語音轉文字功能示例:")
        print("使用 marvin.transcribe() 將語音轉換為文字\n")

        print("基本用法:")
        print("""
        # 轉錄音頻文件
        text = marvin.transcribe("audio.mp3")
        print(f"轉錄結果: {text}")

        # 轉錄不同格式的音頻
        formats = ["audio.mp3", "audio.wav", "audio.m4a"]
        for audio_file in formats:
            text = marvin.transcribe(audio_file)
            print(f"{audio_file}: {text}")

        # 指定語言
        text = marvin.transcribe(
            "chinese_audio.mp3",
            language="zh"
        )
        """)

        print("\n支持的功能:")
        print("  🎤 高精度識別")
        print("  🌐 多語言支持")
        print("  📱 多種音頻格式")
        print("  ⚡ 快速處理")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 語音參數配置 ====================

def example_voice_configuration():
    """示例 3: 語音參數配置"""
    print("\n" + "="*60)
    print("示例 3: 語音參數配置")
    print("="*60)

    try:
        print("語音參數配置示例:")
        print("自定義語音合成的各種參數\n")

        print("示例代碼:")
        print("""
        # 配置語音參數
        marvin.speak(
            "這是一段測試文字",
            output="custom.mp3",
            voice="alloy",      # 語音類型
            speed=1.0,          # 語速（0.25 - 4.0）
            pitch=1.0           # 音調
        )

        # 不同語音類型
        voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        for voice in voices:
            marvin.speak(
                f"這是 {voice} 語音",
                output=f"voice_{voice}.mp3",
                voice=voice
            )

        # 調整語速
        speeds = [0.5, 1.0, 1.5, 2.0]
        for speed in speeds:
            marvin.speak(
                "語速測試",
                output=f"speed_{speed}.mp3",
                speed=speed
            )
        """)

        print("\n可配置參數:")
        print("  🗣️ 語音類型（6種）")
        print("  ⏩ 語速控制")
        print("  🎵 音調調整")
        print("  🔊 音量設置")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 多語言支持 ====================

def example_multilingual():
    """示例 4: 多語言支持"""
    print("\n" + "="*60)
    print("示例 4: 多語言支持")
    print("="*60)

    try:
        print("多語言語音處理示例:\n")

        print("文字轉語音（多語言）:")
        print("""
        # 中文
        marvin.speak("你好，很高興見到你", output="zh.mp3")

        # 英文
        marvin.speak("Hello, nice to meet you", output="en.mp3")

        # 日文
        marvin.speak("こんにちは、お会いできて嬉しいです", output="ja.mp3")

        # 西班牙文
        marvin.speak("Hola, encantado de conocerte", output="es.mp3")

        # 法文
        marvin.speak("Bonjour, ravi de vous rencontrer", output="fr.mp3")
        """)

        print("\n語音轉文字（多語言）:")
        print("""
        # 指定語言進行轉錄
        languages = {
            "zh": "chinese_audio.mp3",
            "en": "english_audio.mp3",
            "ja": "japanese_audio.mp3"
        }

        for lang, audio in languages.items():
            text = marvin.transcribe(audio, language=lang)
            print(f"{lang}: {text}")
        """)

        print("\n支持的語言:")
        print("  🇨🇳 中文")
        print("  🇺🇸 英文")
        print("  🇯🇵 日文")
        print("  🇪🇸 西班牙文")
        print("  🇫🇷 法文")
        print("  🇩🇪 德文")
        print("  ... 更多語言")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 音頻處理 ====================

class Transcription(BaseModel):
    """轉錄結果"""
    text: str
    language: str
    duration: Optional[float] = None
    confidence: Optional[float] = None


def example_audio_processing():
    """示例 5: 音頻處理"""
    print("\n" + "="*60)
    print("示例 5: 音頻處理")
    print("="*60)

    try:
        print("音頻處理和分析示例:\n")

        print("示例代碼:")
        print("""
        # 轉錄並獲取詳細信息
        result = marvin.transcribe(
            "audio.mp3",
            return_details=True
        )

        print(f"文字: {result.text}")
        print(f"語言: {result.language}")
        print(f"時長: {result.duration}秒")

        # 批量處理音頻文件
        audio_files = [
            "audio1.mp3",
            "audio2.mp3",
            "audio3.mp3"
        ]

        results = []
        for audio in audio_files:
            text = marvin.transcribe(audio)
            results.append({
                "file": audio,
                "text": text
            })

        # 保存結果
        for result in results:
            print(f"{result['file']}: {result['text']}")
        """)

        print("\n處理功能:")
        print("  📊 批量轉錄")
        print("  📝 詳細信息提取")
        print("  🔍 質量分析")
        print("  💾 結果保存")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 實際應用場景 ====================

def example_real_applications():
    """示例 6: 實際應用場景"""
    print("\n" + "="*60)
    print("示例 6: 實際應用場景")
    print("="*60)

    try:
        print("實際應用場景示例:\n")

        # 場景 1: 語音備忘錄轉文字
        print("場景 1: 語音備忘錄轉文字")
        print("""
        # 轉錄語音備忘錄
        memo_text = marvin.transcribe("voice_memo.mp3")

        # 提取關鍵信息
        from pydantic import BaseModel

        class Memo(BaseModel):
            date: str
            topic: str
            action_items: List[str]

        memo = marvin.extract(memo_text, target=Memo)
        print(f"日期: {memo.date}")
        print(f"主題: {memo.topic}")
        print(f"待辦: {', '.join(memo.action_items)}")
        """)

        # 場景 2: 會議記錄
        print("\n場景 2: 會議記錄")
        print("""
        # 轉錄會議錄音
        meeting_text = marvin.transcribe("meeting.mp3")

        # 生成會議紀要
        summary = marvin.fn(
            lambda text: "生成會議摘要",
            target=str
        )(meeting_text)

        print(f"會議摘要: {summary}")
        """)

        # 場景 3: 多語言字幕生成
        print("\n場景 3: 多語言字幕生成")
        print("""
        # 轉錄視頻音軌
        original_text = marvin.transcribe("video_audio.mp3")

        # 翻譯成其他語言
        @marvin.fn
        def translate(text: str, target_lang: str) -> str:
            return f"將文本翻譯成{target_lang}"

        chinese = translate(original_text, "中文")
        english = translate(original_text, "英文")

        # 生成語音
        marvin.speak(chinese, output="subtitle_zh.mp3")
        marvin.speak(english, output="subtitle_en.mp3")
        """)

        print("\n應用場景:")
        print("  📝 語音備忘錄")
        print("  🎤 會議記錄")
        print("  📺 字幕生成")
        print("  🎧 播客轉錄")
        print("  🌐 多語言翻譯")
        print("  🔊 有聲書製作")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║        Marvin 語音功能示例                ║
╚══════════════════════════════════════════╝

Marvin 語音功能:
✅ 文字轉語音（TTS）
✅ 語音轉文字（STT）
✅ 語音參數配置
✅ 多語言支持
✅ 批量處理

注意：
⚠️ 需要安裝: pip install marvin[audio]
⚠️ 需要音頻文件進行測試
⚠️ 語音功能會消耗 API 調用
    """)

    # 檢查環境
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 請設置 OPENAI_API_KEY 環境變量")
        return

    # 配置 Marvin
    marvin.settings.openai.api_key = os.getenv("OPENAI_API_KEY")

    # 運行示例（演示性質）
    example_text_to_speech()
    example_speech_to_text()
    example_voice_configuration()
    example_multilingual()
    example_audio_processing()
    example_real_applications()

    print("\n" + "="*60)
    print("✅ 所有示例演示完成！")
    print("="*60)
    print("\n💡 提示: 要運行實際的語音處理，請:")
    print("   1. 安裝 marvin[audio]")
    print("   2. 準備音頻文件")
    print("   3. 取消註釋相關代碼")


if __name__ == "__main__":
    main()
