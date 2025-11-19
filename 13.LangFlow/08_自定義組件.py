#!/usr/bin/env python3
"""
LangFlow - 自定義組件示例

展示如何創建自定義組件並在 LangFlow 中使用
"""

from typing import Optional
from langflow import CustomComponent
from langflow.field_typing import Data, Text


class SentimentAnalyzer(CustomComponent):
    """情感分析自定義組件"""

    display_name = "Sentiment Analyzer"
    description = "分析文本情感"
    documentation = "https://docs.langflow.org/custom-components"

    def build_config(self):
        return {
            "text": {
                "display_name": "Input Text",
                "info": "要分析的文本",
            },
            "language": {
                "display_name": "Language",
                "options": ["zh", "en", "ja"],
                "value": "zh",
            },
        }

    def build(self, text: Text, language: str = "zh") -> Data:
        """執行情感分析"""
        # 簡化示例 - 實際應該調用 NLP 模型
        result = {
            "text": text,
            "language": language,
            "sentiment": "positive",  # 模擬結果
            "score": 0.85,
        }

        self.status = f"Analyzed {len(text)} characters"
        return result


class DataFormatter(CustomComponent):
    """數據格式化組件"""

    display_name = "Data Formatter"
    description = "格式化輸出數據"

    def build_config(self):
        return {
            "data": {"display_name": "Input Data"},
            "format": {
                "display_name": "Format",
                "options": ["json", "csv", "markdown"],
                "value": "json",
            },
        }

    def build(self, data: Data, format: str = "json") -> Text:
        """格式化數據"""
        import json

        if format == "json":
            return json.dumps(data, ensure_ascii=False, indent=2)
        elif format == "csv":
            # 簡化的 CSV 轉換
            return str(data)
        elif format == "markdown":
            # 簡化的 Markdown 轉換
            return f"```json\n{json.dumps(data, ensure_ascii=False, indent=2)}\n```"

        return str(data)


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🔧 LangFlow - 自定義組件示例")
    print("=" * 60)

    print("""
📋 創建自定義組件步驟：

1. 繼承 CustomComponent 類
2. 定義 display_name 和 description
3. 實現 build_config() 方法
4. 實現 build() 方法

🔧 組件配置字段：
- display_name: 顯示名稱
- info: 說明文本
- options: 下拉選項
- value: 默認值

💡 使用自定義組件：
1. 將組件代碼放在 LangFlow 的 custom_components 目錄
2. 重啟 LangFlow
3. 在界面中找到自定義組件
4. 拖放使用

📝 示例組件：
- SentimentAnalyzer: 情感分析
- DataFormatter: 數據格式化
""")

    # 測試組件
    analyzer = SentimentAnalyzer()
    result = analyzer.build(text="這個產品很棒！", language="zh")
    print(f"\n✅ 情感分析結果: {result}")

    formatter = DataFormatter()
    formatted = formatter.build(data=result, format="json")
    print(f"\n✅ 格式化輸出:\n{formatted}")

    print("\n" + "=" * 60)
    print("✅ 自定義組件示例完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
